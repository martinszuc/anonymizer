"""What the review window asks of the core: open a document, show its pages, record decisions.

The window's JavaScript reaches these methods through `WindowApi` (`app.py`),
and pywebview passes arguments and results as JSON, so every result here is
plain data. Nothing in this module imports pywebview: the window is a thin
shell around `ReviewApi`, which is tested on its own. Methods here take file
paths, so the page never calls them directly; `WindowApi` passes on the paths
the reviewer chose in a dialog.

The file (a PDF or an image) is read into memory once; the document is
loaded from those bytes and pages are rendered from the PDF they are read as.
Reading the path again instead would draw a file that changed on disk under
boxes computed for the old one. Export reads the path again, and the core
refuses it if the file no longer matches the fingerprint.
"""

from __future__ import annotations

import base64
import logging
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pymupdf
from anonymizer.core.detect import (
    DEFAULT_NAME_MODEL,
    Detector,
    load_name_model,
    missing_name_model_files,
    name_model,
    name_model_installed,
    name_models,
)
from anonymizer.core.detect.base import describe
from anonymizer.core.detect.models import name_model_engine
from anonymizer.core.ingest import (
    OCR_ENGINE_RESOURCES,
    OCR_ENGINES,
    OcrEngine,
    as_pdf,
    document_from_bytes,
    load_ocr_engine,
    missing_ocr_files,
    ocr_engine_installed,
    pages_needing_ocr,
    read_source,
)
from anonymizer.core.language import AUTO
from anonymizer.core.log import fields
from anonymizer.core.pipeline import (
    add_finding,
    build_detector,
    remove_finding,
    resolve_language,
    run_detection,
)
from anonymizer.core.redact import Leak, export_redacted
from anonymizer.core.resources import (
    Catalog,
    ChecksumError,
    Opener,
    PinRequiredError,
    Resource,
    ResourceFile,
    choose_resource_root,
    fetch_with_requirements,
    load_catalog,
    resolve_resource_root,
    resource_status,
)
from anonymizer.core.session import apply_session, save_session, session_ocr_engine
from anonymizer.core.settings import read_settings, write_setting
from anonymizer.core.types import (
    BBox,
    DetectionSource,
    Document,
    Entity,
    EntityType,
    Page,
    ReviewState,
    StepProgress,
    Surface,
)
from anonymizer.ui import __version__

log = logging.getLogger(__name__)

MIN_DPI = 36
MAX_DPI = 400
"""Render resolution bounds. 400 dpi puts an A4 page at about 4,700 by 6,600 pixels."""


LANGUAGES = {"cs": "Czech", "sk": "Slovak", "en": "English"}
"""Languages with their own rules (`detect.finders_for`); without one, every rule runs.
`language.AUTO` may be asked for as well: the language is recognised from the text."""

DEFAULT_OCR_ENGINE = "onnxtr"
"""The engine the home screen starts with: the faster one, and the one offered first."""


@dataclass(frozen=True)
class _OcrChoice:
    """How the window names an OCR engine and what it tells the reviewer it is for."""

    title: str
    description: str


OCR_CHOICES = {
    "onnxtr": _OcrChoice("OnnxTR", "Fast. Reads printed text, not handwriting."),
    # docs/findings.md, kraken on the scanned benchmark: about half OnnxTR's
    # character error rate on print, and about four times slower on the CPU.
    "kraken": _OcrChoice(
        "kraken",
        "Also reads handwriting and misreads print less, but takes about four times as long.",
    ),
}
"""Every engine of `ingest.OCR_ENGINES`, as the window offers it."""

NAME_MODEL_DESCRIPTIONS = {
    "gliner-multi-v2.1": "Zero-shot and multilingual. Finds names and addresses the rules cannot.",
}
"""What the window tells the reviewer a name model is for, by catalog id; a model
missing here is described by `NAME_MODEL_DESCRIPTION`."""

NAME_MODEL_DESCRIPTION = "Finds names and addresses the rules cannot."

Progress = Callable[[str, int, int], None]
"""Told each step of opening a PDF as it starts and, page by page, as it goes: the
step (`loading_ocr`, `reading`, `ocr`, `loading_model`, `detecting`), then the pages
done and the pages in all (both 0 for a step without pages)."""


Downloaded = Callable[[str, int, int], None]
"""Told a download's progress: the feature, bytes received so far, bytes in all."""

LEAK_CHECK_SETTING = "leak_check"
"""Whether export checks the copy for leaks; on unless the reviewer turned it off."""

OPEN_OPTIONS_SETTING = "open_options"
"""The home screen's detection options as the reviewer last left them; nothing about a document."""

_OPEN_OPTION_TYPES: dict[str, tuple[type, ...]] = {
    "language": (str, type(None)),
    "propagate": (bool,),
    "use_model": (bool,),
    "name_model": (str,),
    "use_ocr": (bool,),
    "ocr_engine": (str,),
}


@dataclass(frozen=True)
class _Feature:
    """Something the window can do once its models are stored and its package installed."""

    title: str
    description: str
    resource_id: str
    group: str
    installed: Callable[[], bool]


def _ocr_feature(engine: str) -> _Feature:
    choice = OCR_CHOICES[engine]
    return _Feature(
        f"Scanned pages: {choice.title}",
        choice.description,
        OCR_ENGINE_RESOURCES[engine][-1],
        f"ocr-{engine}",
        lambda: ocr_engine_installed(engine),
    )


def _name_model_feature(model: Resource, catalog: Catalog) -> _Feature:
    return _Feature(
        f"Names and addresses: {model.name}",
        NAME_MODEL_DESCRIPTIONS.get(model.id, NAME_MODEL_DESCRIPTION),
        model.id,
        name_model_engine(model.id, catalog).group,
        lambda: name_model_installed(model.id, catalog),
    )


def features(catalog: Catalog) -> dict[str, _Feature]:
    """The features whose models the window can download, by the name the page uses.

    One per name model of the catalog (`names-<catalog id>`), then one per OCR
    engine (`ocr-<engine>`, as its dependency group is named).
    """
    return {
        **{
            f"names-{model.id}": _name_model_feature(model, catalog)
            for model in name_models(catalog)
        },
        **{f"ocr-{engine}": _ocr_feature(engine) for engine in OCR_ENGINES},
    }


class ReviewError(Exception):
    """A request the window cannot carry out; its message is shown to the reviewer."""


@dataclass
class _OpenDocument:
    """The document under review, its file, and the PDF it was read as, from one read."""

    source: Path
    document: Document
    pdf_bytes: bytes
    language_recognised: bool = False
    # Whether text the reviewer adds is marked again where it repeats, as
    # detection's was; a reopened review has no record of it and marks them.
    propagate: bool = True


class ReviewApi:
    """The calls available to the review window.

    One document is open at a time. Every method that needs it raises
    `ReviewError` when none is.
    """

    def __init__(
        self,
        resource_root: Path | None = None,
        *,
        catalog: Catalog | None = None,
        opener: Opener | None = None,
    ) -> None:
        """Initialize the API.

        Args:
            resource_root: Directory holding `models/`, as for the CLI's
                `--resource-root`; `resources.resolve_resource_root` picks it
                when omitted.
            catalog: The resource catalog; the one shipped with the core when
                omitted.
            opener: Opens a download URL; the default opens the network.
        """
        self._open: _OpenDocument | None = None
        self._resource_root = (
            resource_root if resource_root is not None else resolve_resource_root()
        )
        self._catalog = catalog or load_catalog()
        self._features = features(self._catalog)
        self._opener = opener
        # Catalog ids being downloaded: two downloads of one model would write
        # the same files, while features sharing no model download side by side.
        self._downloads_lock = threading.Lock()
        self._downloading: set[str] = set()
        # Loaded on first use and kept: loading takes seconds, detecting does not.
        self._models: dict[str, Detector] = {}
        self._ocr: dict[str, OcrEngine] = {}
        settings = read_settings()
        self._leak_check = settings.get(LEAK_CHECK_SETTING) is not False
        self._open_options: dict[str, Any] | None = None
        # Never set, or written by another version: the home screen starts from its defaults.
        with suppress(ReviewError):
            self._open_options = open_options(settings.get(OPEN_OPTIONS_SETTING))

    def status(self) -> dict[str, Any]:
        """Describe what this installation can do, for the home screen.

        Checking the name model never loads it, so the home screen appears at
        once.

        Returns:
            The version, the languages with their own rules, the folder models
            are stored in, the state of every name model and every OCR engine
            (`ready`, `not_installed`: the optional dependencies are missing,
            or `files_missing`, with the catalog ids to fetch), the name model
            and the OCR engine offered first, and the settings (`leak_check`,
            and `open_options` as last kept, or None).
        """
        return {
            "version": __version__,
            "languages": [{"code": code, "name": name} for code, name in LANGUAGES.items()],
            "models_folder": str(self._resource_root / "models"),
            "names": {
                "default": DEFAULT_NAME_MODEL,
                "models": [self._name_model_status(model) for model in name_models(self._catalog)],
            },
            "ocr": {
                "default": DEFAULT_OCR_ENGINE,
                "engines": [self._ocr_engine_status(engine) for engine in OCR_ENGINES],
            },
            "settings": {"leak_check": self._leak_check, "open_options": self._open_options},
        }

    def _name_model_status(self, model: Resource) -> dict[str, Any]:
        missing = missing_name_model_files(model.id, self._resource_root, self._catalog)
        key = f"names-{model.id}"
        feature = self._features[key]
        return {
            "name": model.id,
            "title": model.name,
            "description": feature.description,
            "feature": key,
            "state": _state(feature.installed(), missing),
            "missing": missing,
            "install_command": f"uv sync --group {feature.group}",
        }

    def _ocr_engine_status(self, engine: str) -> dict[str, Any]:
        missing = missing_ocr_files(engine, self._resource_root)
        feature = self._features[f"ocr-{engine}"]
        return {
            "name": engine,
            "title": OCR_CHOICES[engine].title,
            "description": feature.description,
            "feature": f"ocr-{engine}",
            "state": _state(ocr_engine_installed(engine), missing),
            "missing": missing,
            "install_command": f"uv sync --group {feature.group}",
        }

    def set_leak_check(self, enabled: bool) -> dict[str, Any]:
        """Turn the leak check of every later export on or off, in this run and later ones.

        Args:
            enabled: Whether export checks the copy before writing it.

        Returns:
            The installation as `status()` describes it.

        Raises:
            ReviewError: If `enabled` is not a boolean or the choice cannot be saved.
        """
        if not isinstance(enabled, bool):
            msg = "the leak check is turned on or off with true or false"
            raise ReviewError(msg)
        with _as_review_error():
            write_setting(LEAK_CHECK_SETTING, enabled)
        self._leak_check = enabled
        log.info("leak check turned %s", "on" if enabled else "off")
        return self.status()

    def set_open_options(self, options: object) -> dict[str, Any]:
        """Keep the home screen's detection options for this run and later ones.

        A name model or an OCR engine kept here may be missing later; the home
        screen then offers a ready one instead.

        Args:
            options: `{language, propagate, use_model, name_model, use_ocr, ocr_engine}`.

        Returns:
            The installation as `status()` describes it.

        Raises:
            ReviewError: If an option is missing, unknown or of the wrong kind, or the
                choice cannot be saved.
        """
        checked = open_options(options)
        with _as_review_error():
            write_setting(OPEN_OPTIONS_SETTING, checked)
        self._open_options = checked
        log.debug("open options kept")
        return self.status()

    def models(self) -> list[dict[str, Any]]:
        """Describe the models each feature needs and whether they are stored.

        Returns:
            Per feature: its key, title and one-line description, whether its
            package is installed and the command that installs it, the bytes
            still to download, and each model (requirements first) with what
            it is, its licence, languages, source, version, size and state
            (`present`, `partial` or `absent`, from the files on disk).
        """
        return [self._feature_payload(key, feature) for key, feature in self._features.items()]

    def download_models(
        self, feature: str, progress: Downloaded | None = None
    ) -> list[dict[str, Any]]:
        """Download the models a feature needs from their official sources, each verified.

        Only the catalog's files for a known feature can be fetched: the page
        names a feature, never a URL or a catalog id. Features that share no
        model download at the same time.

        Args:
            feature: A key of `features()`.
            progress: Told the bytes received and the bytes in all, as they arrive.

        Returns:
            The models of every feature, as `models()` describes them.

        Raises:
            ReviewError: If the feature is unknown, one of its models is
                already downloading, or a download fails or does not match
                its checksum (the file is then removed).
        """
        if feature not in self._features:
            msg = f"unknown feature {feature!r}"
            raise ReviewError(msg)
        log.info("download requested: feature=%s", feature)
        resources = self._catalog.with_requirements(self._features[feature].resource_id)
        ids = {resource.id for resource in resources}
        with self._downloads_lock:
            if ids & self._downloading:
                log.warning("download refused: one of its models is already downloading")
                msg = "this download is already running"
                raise ReviewError(msg)
            self._downloading |= ids
        try:
            self._download(feature, progress or _no_progress)
        finally:
            with self._downloads_lock:
                self._downloading -= ids
        return self.models()

    def choose_models_folder(self, path: str) -> dict[str, Any]:
        """Store models under another folder, in this run and every later one.

        Models already stored elsewhere are not moved, and models loaded from
        the old folder are dropped, so the next document opens with the
        models of the new one.

        Args:
            path: The folder to hold `models/`, chosen in a dialog.

        Returns:
            The installation as `status()` describes it, for the new folder.

        Raises:
            ReviewError: If a download is running, or the choice cannot be saved.
        """
        with self._downloads_lock:
            if self._downloading:
                msg = "wait for the download to finish before changing the folder"
                raise ReviewError(msg)
            root = Path(path).resolve()
            with _as_review_error():
                choose_resource_root(root)
            self._resource_root = root
            self._models.clear()
            self._ocr.clear()
        return self.status()

    def _download(self, feature: str, progress: Downloaded) -> None:
        resource_id = self._features[feature].resource_id
        # Stored files are verified, not downloaded, so only missing ones count.
        total = sum(
            item.size
            for resource in self._catalog.with_requirements(resource_id)
            for item in resource.files
            if not (resource.directory(self._resource_root) / item.path).exists()
        )
        received_by_file: dict[str, int] = {}

        def report(item: ResourceFile, received: int) -> None:
            received_by_file[item.url] = received
            progress(feature, sum(received_by_file.values()), total)

        try:
            fetch_with_requirements(
                self._catalog,
                resource_id,
                self._resource_root,
                opener=self._opener,
                progress=report,
            )
        except (PinRequiredError, ChecksumError, OSError) as error:
            msg = f"the download failed: {error}"
            raise ReviewError(msg) from error
        progress(feature, total, total)

    def _feature_payload(self, key: str, feature: _Feature) -> dict[str, Any]:
        resources = self._catalog.with_requirements(feature.resource_id)
        states = {
            resource.id: resource_status(resource, self._resource_root) for resource in resources
        }
        return {
            "feature": key,
            "title": feature.title,
            "description": feature.description,
            "installed": feature.installed(),
            "install_command": f"uv sync --group {feature.group}",
            "missing_bytes": sum(
                resource.size for resource in resources if states[resource.id] != "present"
            ),
            "models": [
                {
                    "id": resource.id,
                    "name": resource.name,
                    "uses": list(resource.uses),
                    "licence": resource.licence,
                    "languages": list(resource.languages),
                    "source": resource.source,
                    "version": resource.version,
                    "size": resource.size,
                    "state": states[resource.id],
                }
                for resource in resources
            ],
        }

    def open_pdf(
        self,
        path: str,
        language: str | None = None,
        propagate: bool = True,
        name_model: str | None = None,
        progress: Progress | None = None,
        ocr_engine: str | None = None,
    ) -> dict[str, Any]:
        """Open a PDF or an image and propose redactions for it.

        An image has no text layer: without OCR nothing on it is detected,
        and its pages are reported as scans OCR has not read.

        Args:
            path: The PDF, JPEG, PNG or TIFF file to review.
            language: BCP 47 tag selecting the rules, or `language.AUTO` to
                recognise it from the text; every rule runs when omitted.
            propagate: Also mark further occurrences of the text found.
            name_model: Also run this name model, a catalog id (see `status`);
                none when omitted.
            progress: Told each step as it starts.
            ocr_engine: Read scanned pages with this engine, a key of
                `ingest.OCR_ENGINES` (see `status`); none when omitted.

        Returns:
            The document as `document()` describes it.

        Raises:
            ReviewError: If the file is missing or unreadable, the name model
                or the OCR engine is unknown, or either was asked for but
                cannot be loaded.
        """
        log.debug(
            "open pdf:%s",
            fields(language=language, propagate=propagate, model=name_model, ocr=ocr_engine),
        )
        if ocr_engine is not None and ocr_engine not in OCR_ENGINES:
            msg = f"unknown OCR engine {ocr_engine!r}"
            raise ReviewError(msg)
        if name_model is not None:
            with _as_review_error():
                name_model = _name_model_id(name_model, self._catalog)
        report = progress or _no_progress
        ocr = self._loaded_ocr(ocr_engine, report) if ocr_engine is not None else None
        document, pdf_bytes = _read(path, ocr, report, language=language)
        model = self._loaded_model(name_model, report) if name_model is not None else None
        resolved = resolve_language(document, language)
        run_detection(
            document,
            build_detector(resolved, model=model),
            propagate=propagate,
            progress=lambda done, total: report("detecting", done, total),
        )
        self._open = _OpenDocument(
            Path(path),
            document,
            pdf_bytes,
            language_recognised=language == AUTO,
            propagate=propagate,
        )
        return self.document()

    def _loaded_model(self, model_id: str, report: Progress) -> Detector:
        """Return a name model, loading it the first time."""
        if model_id in self._models:
            log.debug("name model %s already loaded", model_id)
        else:
            report("loading_model", 0, 0)
            try:
                self._models[model_id] = load_name_model(
                    model_id, self._resource_root, self._catalog
                )
            except (ImportError, FileNotFoundError) as error:
                log.warning("the name model is not available", exc_info=True)
                msg = f"the name model is not available: {error}"
                raise ReviewError(msg) from error
        return self._models[model_id]

    def _loaded_ocr(self, name: str, report: Progress) -> OcrEngine:
        """Return an OCR engine, loading it the first time."""
        if name in self._ocr:
            log.debug("OCR engine %s already loaded", name)
        else:
            report("loading_ocr", 0, 0)
            try:
                self._ocr[name] = load_ocr_engine(name, self._resource_root)
            except (ImportError, FileNotFoundError, ValueError) as error:
                log.warning("the OCR engine is not available", exc_info=True)
                msg = f"the OCR engine is not available: {error}"
                raise ReviewError(msg) from error
        return self._ocr[name]

    def open_session(
        self, pdf_path: str, session_path: str, progress: Progress | None = None
    ) -> dict[str, Any]:
        """Reopen a saved review of a PDF or an image.

        A review of scanned pages records the OCR engine that read them; the
        file is read with that engine again, since the review's offsets refer
        to what it read.

        Args:
            pdf_path: The original PDF or image.
            session_path: The session file saved from a review of it.
            progress: Told each step as it starts.

        Returns:
            The document as `document()` describes it.

        Raises:
            ReviewError: If the session belongs to another file or no longer
                matches it, either file cannot be read, or the review's OCR
                engine cannot be loaded.
        """
        report = progress or _no_progress
        with _as_review_error():
            engine = session_ocr_engine(session_path)
        ocr = self._loaded_ocr(engine, report) if engine is not None else None
        scanned, pdf_bytes = _read(pdf_path, ocr, report)
        with _as_review_error():
            document = apply_session(scanned, session_path)
        self._open = _OpenDocument(Path(pdf_path), document, pdf_bytes)
        return self.document()

    @property
    def name(self) -> str:
        """File name of the open document, for the window title and default file names.

        Raises:
            ReviewError: If no document is open.
        """
        return self._current().source.name

    def close(self) -> None:
        """Forget the open document, so its content no longer stays in memory."""
        if self._open is not None:
            log.info("document closed")
        self._open = None

    def document(self) -> dict[str, Any]:
        """Describe the open document: its pages, the proposed entities, the hidden items.

        Returns:
            A JSON-compatible mapping. Boxes are `[x0, y0, x1, y1]` in PDF
            points, origin top-left, the same system the page sizes use.
        """
        current = self._current()
        document = current.document
        return {
            "name": current.source.name,
            "language": document.language,
            "language_recognised": current.language_recognised,
            "pages": [_page_payload(page) for page in document.pages],
            "entities": [_entity_payload(entity) for entity in document.entities],
            "surfaces": [_surface_payload(surface) for surface in document.surfaces],
        }

    def page_image(self, index: int, dpi: int = 144) -> str:
        """Render a page of the original PDF.

        Args:
            index: Zero-based page number.
            dpi: Resolution, clamped to `MIN_DPI`..`MAX_DPI`.

        Returns:
            A `data:` URL of a PNG covering exactly the page's area.

        Raises:
            ReviewError: If the page does not exist.
        """
        current = self._current()
        with _as_review_error():
            current.document.page(index)
        resolution = min(max(dpi, MIN_DPI), MAX_DPI)
        log.debug("render page %d at %d dpi", index, resolution)
        with pymupdf.open(stream=current.pdf_bytes, filetype="pdf") as pdf:
            png = pdf[index].get_pixmap(dpi=resolution).tobytes("png")
        return "data:image/png;base64," + base64.b64encode(png).decode("ascii")

    def page_words(self, index: int) -> list[dict[str, Any]]:
        """List a page's words, so the reviewer can select text detection missed.

        Args:
            index: Zero-based page number.

        Returns:
            The words in reading order, each with its offsets in the page text,
            its text and its box (`[x0, y0, x1, y1]` in points). A page OCR
            read lists the words OCR found.

        Raises:
            ReviewError: If the page does not exist.
        """
        current = self._current()
        with _as_review_error():
            page = current.document.page(index)
        log.debug("words of page %d: %d", index, len(page.words))
        return [
            {"start": word.start, "end": word.end, "text": word.text, "box": word.bbox.to_list()}
            for word in page.words
        ]

    def add_finding(
        self, page_index: int, start: int, end: int, entity_type: str
    ) -> list[dict[str, Any]]:
        """Add text the reviewer selected because detection missed it.

        The selection is widened to whole words, and its other occurrences are
        proposed too when the document was opened marking repeats
        (`pipeline.add_finding`).

        Args:
            page_index: Page the text is on.
            start: First offset of the selection in the page text (a word's
                `start` from `page_words`).
            end: Offset one past the selection (a word's `end`).
            entity_type: What the text is, e.g. `person` or `email`.

        Returns:
            The added finding, then its other occurrences, as `document()`
            lists entities.

        Raises:
            ReviewError: If an argument is not a whole number, the type or the
                page is unknown, the selection covers no word, or the text is
                already marked for redaction.
        """
        current = self._current()
        if not all(_is_whole(value) for value in (page_index, start, end)):
            msg = "the page and the offsets must be whole numbers"
            raise ReviewError(msg)
        with _as_review_error():
            kind = EntityType(entity_type)
            added = add_finding(
                current.document, page_index, start, end, kind, propagate=current.propagate
            )
        log.debug("review: added %s with %d repeats", describe(added[0]), len(added) - 1)
        return [_entity_payload(entity) for entity in added]

    def set_review(self, entity_id: str, state: str) -> dict[str, Any]:
        """Record the reviewer's decision on one entity.

        Args:
            entity_id: The entity decided on.
            state: `confirmed` (redact), `rejected` (keep) or `pending`.

        Returns:
            The entity as `document()` lists it.

        Raises:
            ReviewError: If the entity or the state is unknown.
        """
        current = self._current()
        with _as_review_error():
            entity = current.document.entity(entity_id)
            entity.review = ReviewState(state)
        log.debug("review: %s decided %s", state, describe(entity))
        return _entity_payload(entity)

    def set_reviews(self, entity_ids: list[str], state: str) -> list[dict[str, Any]]:
        """Record one decision on several entities at once, such as every repeat of a word.

        Nothing changes unless every entity and the state are valid.

        Args:
            entity_ids: The entities decided on.
            state: `confirmed` (redact), `rejected` (keep) or `pending`.

        Returns:
            The entities as `document()` lists them, in the order given.

        Raises:
            ReviewError: If `entity_ids` is not a list of ids, or an entity or
                the state is unknown.
        """
        current = self._current()
        if not isinstance(entity_ids, list) or not all(isinstance(i, str) for i in entity_ids):
            msg = "entity ids must be a list of strings"
            raise ReviewError(msg)
        with _as_review_error():
            review = ReviewState(state)
            entities = [current.document.entity(entity_id) for entity_id in entity_ids]
        for entity in entities:
            entity.review = review
        log.debug("review: %s decided on %d entities at once", state, len(entities))
        return [_entity_payload(entity) for entity in entities]

    def add_region(
        self, page_index: int, x0: float, y0: float, x1: float, y1: float
    ) -> dict[str, Any]:
        """Add a region the reviewer drew, in page points; the corners may come in any order.

        Args:
            page_index: Page it was drawn on.
            x0: One corner's horizontal position.
            y0: One corner's vertical position.
            x1: The opposite corner's horizontal position.
            y1: The opposite corner's vertical position.

        Returns:
            The region as `document()` lists entities, clipped to the page.

        Raises:
            ReviewError: If the page does not exist or the box lies outside it.
        """
        current = self._current()
        box = BBox(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        with _as_review_error():
            region = current.document.add_region(page_index, box)
        log.debug("region added: entity=%s page=%d", region.entity_id, page_index)
        return _entity_payload(region)

    def remove_entity(self, entity_id: str) -> list[str]:
        """Remove an item the reviewer added, such as a region drawn by mistake.

        Repeats proposed only because the reviewer added the text go with it
        (`pipeline.remove_finding`).

        Args:
            entity_id: The item to remove.

        Returns:
            The ids removed: the item's first, then those of its repeats.

        Raises:
            ReviewError: If it is unknown, or was detected rather than added:
                a detected item is kept by rejecting it, so the decision is saved.
        """
        current = self._current()
        with _as_review_error():
            entity = current.document.entity(entity_id)
        if entity.source is not DetectionSource.MANUAL:
            msg = "only items you added can be removed; keep a detected item instead"
            raise ReviewError(msg)
        removed = remove_finding(current.document, entity_id)
        log.debug("item removed: entity=%s repeats=%d", entity_id, len(removed) - 1)
        return [item.entity_id for item in removed]

    def save_session(self, path: str) -> None:
        """Write the review to a session file, replacing one that exists.

        Args:
            path: Where to write it; the window's save dialog has already
                confirmed replacing an existing file.

        Raises:
            ReviewError: If the file cannot be written.
        """
        current = self._current()
        with _as_review_error():
            save_session(current.document, path)

    def export(
        self,
        path: str,
        allow_pages_without_text: bool = False,
        progress: StepProgress | None = None,
        check: bool | None = None,
    ) -> dict[str, Any]:
        """Write the redacted copy, keeping it only if the leak check passes.

        Undecided items are redacted, rejected ones kept, and every hidden
        item removed (`export_redacted`).

        Args:
            path: Where to write the copy; the window's save dialog has
                already confirmed replacing an existing file.
            allow_pages_without_text: Export even though some scanned pages
                were not read by OCR. Nothing on such a page is detected, so
                it reaches the output unredacted while the leak check still
                passes.
            progress: Told each step of the export as it starts (see
                `export_redacted`).
            check: Run the leak check; the setting (`set_leak_check`) decides
                when omitted. False writes the copy whatever it holds, as
                when the reviewer saves a copy the check refused.

        Returns:
            What the export did: whether the copy was written, the counts of
            redacted, kept and not reviewed items and of hidden items removed,
            the pages left unredacted, the leak check's outcome (`passed`,
            `failed` or `off`) and the leaks that stopped it.

        Raises:
            ReviewError: If pages have no text layer and that was not allowed,
                the path is the original, or the original changed on disk.
        """
        current = self._current()
        checked = self._leak_check if check is None else check
        unreadable = [index + 1 for index in pages_needing_ocr(current.document)]
        log.info(
            "export requested: unread_scan_pages=%d leak_check=%s",
            len(unreadable),
            "on" if checked else "off",
        )
        if unreadable and allow_pages_without_text:
            log.warning(
                "exporting with %d scanned page(s) OCR has not read; they stay unredacted",
                len(unreadable),
            )
        if unreadable and not allow_pages_without_text:
            listed = ", ".join(str(page) for page in unreadable)
            msg = f"page {listed} is a scan OCR has not read; nothing on it would be redacted"
            raise ReviewError(msg)
        ocr = self._engine_that_read(current.document) if checked else None
        with _as_review_error():
            leaks = export_redacted(
                current.source, current.document, path, ocr=ocr, check=checked, progress=progress
            )
        return _export_payload(
            Path(path).name, current.document, leaks, unreadable, checked=checked
        )

    def _engine_that_read(self, document: Document) -> OcrEngine | None:
        """Return the loaded engine that read the document, for the leak check to re-read with."""
        if document.ocr_engine is None:
            return None
        for engine in self._ocr.values():
            if engine.name == document.ocr_engine:
                return engine
        msg = f"the OCR engine {document.ocr_engine!r} that read this document is not loaded"
        raise ReviewError(msg)

    def _current(self) -> _OpenDocument:
        if self._open is None:
            msg = "no document is open"
            raise ReviewError(msg)
        return self._open


def _no_progress(_step: str, _done: int, _total: int) -> None:
    pass


def open_options(options: object) -> dict[str, Any]:
    """Check the home screen's detection options, as the page or the settings file gives them.

    Args:
        options: `{language, propagate, use_model, name_model, use_ocr, ocr_engine}`;
            `language` is a code of `LANGUAGES`, `language.AUTO` or None.

    Returns:
        The same options, as a new mapping.

    Raises:
        ReviewError: If an option is missing, unknown or of the wrong kind.
    """
    if not isinstance(options, dict) or set(options) != set(_OPEN_OPTION_TYPES):
        msg = f"open options need exactly {sorted(_OPEN_OPTION_TYPES)}"
        raise ReviewError(msg)
    for key, kinds in _OPEN_OPTION_TYPES.items():
        if not isinstance(options[key], kinds):
            msg = f"open option {key} has the wrong kind"
            raise ReviewError(msg)
    language = options["language"]
    if language is not None and language != AUTO and language not in LANGUAGES:
        msg = f"unknown language {language!r}"
        raise ReviewError(msg)
    return dict(options)


def _name_model_id(model_id: str, catalog: Catalog) -> str:
    """The catalog id of a name model the page named, which may be an earlier name."""
    return name_model(model_id, catalog).id


def _read(
    path: str, ocr: OcrEngine | None, report: Progress, *, language: str | None = None
) -> tuple[Document, bytes]:
    """Read a file once into a document and the PDF it is read as."""
    report("reading", 0, 0)
    with _as_review_error():
        source_bytes = read_source(path)
        document = document_from_bytes(
            source_bytes,
            language=language,
            ocr=ocr,
            ocr_progress=lambda done, total: report("ocr", done, total),
        )
        return document, as_pdf(source_bytes)


@contextmanager
def _as_review_error() -> Iterator[None]:
    """Turn the errors the core reports for bad input into `ReviewError`."""
    try:
        yield
    except (ValueError, KeyError, OSError, pymupdf.FileDataError) as error:
        # str() of a KeyError quotes its message.
        message = error.args[0] if isinstance(error, KeyError) and error.args else str(error)
        raise ReviewError(message) from error


def _is_whole(value: object) -> bool:
    """Whether a value from the page is an integer (JSON has no separate type for it)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _state(installed: bool, missing: list[str]) -> str:
    """Whether an optional model can be used: `ready`, `not_installed` or `files_missing`."""
    if not installed:
        return "not_installed"
    return "files_missing" if missing else "ready"


def _page_payload(page: Page) -> dict[str, Any]:
    return {
        "index": page.index,
        "width": page.width,
        "height": page.height,
        "has_text_layer": page.has_text_layer,
        "raster_dpi": page.raster_dpi,
    }


def _entity_payload(entity: Entity) -> dict[str, Any]:
    return {
        "id": entity.entity_id,
        "type": entity.type.value,
        "source": entity.source.value,
        "score": entity.score,
        "review": entity.review.value,
        "page_index": entity.page_index,
        "surface_id": entity.surface_id,
        "text": entity.text,
        "is_region": entity.is_region,
        "boxes": [box.to_list() for box in entity.bboxes],
    }


def _export_payload(
    name: str, document: Document, leaks: list[Leak], unreadable: list[int], *, checked: bool
) -> dict[str, Any]:
    # A finding in hidden data goes with it, whatever its review says: export
    # clears every hidden item.
    applied = [
        entity
        for entity in document.entities
        if entity.is_redactable or entity.surface_id is not None
    ]
    return {
        "written": not leaks,
        "name": name,
        "redacted": sum(not entity.is_region for entity in applied),
        "regions": sum(entity.is_region for entity in applied),
        "kept": len(document.entities) - len(applied),
        "not_reviewed": sum(entity.review is ReviewState.PENDING for entity in applied),
        "hidden_removed": len(document.surfaces),
        "pages_without_text": unreadable,
        "leak_check": "off" if not checked else "failed" if leaks else "passed",
        "leaks": [
            {
                "layer": leak.layer.value,
                "where": leak.where,
                # 1-based, as the window numbers pages; the core counts from 0.
                "page": None if leak.page_index is None else leak.page_index + 1,
                "text": leak.text,
                "entity_id": leak.entity_id,
                "kind": leak.kind.value,
            }
            for leak in leaks
        ],
    }


def _surface_payload(surface: Surface) -> dict[str, Any]:
    return {
        "id": surface.surface_id,
        "kind": surface.kind.value,
        "value": surface.value,
        "page_index": surface.page_index,
        "box": None if surface.bbox is None else surface.bbox.to_list(),
    }
