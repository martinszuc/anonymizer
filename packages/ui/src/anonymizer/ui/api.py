"""What the review window asks of the core: open a PDF, show its pages, record decisions.

The window's JavaScript reaches these methods through `WindowApi` (`app.py`),
and pywebview passes arguments and results as JSON, so every result here is
plain data. Nothing in this module imports pywebview: the window is a thin
shell around `ReviewApi`, which is tested on its own. Methods here take file
paths, so the page never calls them directly; `WindowApi` passes on the paths
the reviewer chose in a dialog.

The PDF is read into memory once; the document is loaded from those bytes and
pages are rendered from them. Reading the path again instead would draw a file
that changed on disk under boxes computed for the old one. Export reads the
path again, and the core refuses it if the file no longer matches the
fingerprint.
"""

from __future__ import annotations

import base64
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pymupdf
from anonymizer.core.detect import (
    Detector,
    gliner_installed,
    load_gliner_detector,
    missing_gliner_files,
)
from anonymizer.core.ingest import document_from_bytes, pages_needing_ocr, read_pdf
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import Leak, export_redacted
from anonymizer.core.session import apply_session, save_session
from anonymizer.core.types import (
    BBox,
    DetectionSource,
    Document,
    Entity,
    Page,
    ReviewState,
    Surface,
)
from anonymizer.ui import __version__

MIN_DPI = 36
MAX_DPI = 400
"""Render resolution bounds. 400 dpi puts an A4 page at about 4,700 by 6,600 pixels."""


LANGUAGES = {"cs": "Czech", "sk": "Slovak", "en": "English"}
"""Languages with their own rules (`detect.finders_for`); without one, every rule runs."""

Progress = Callable[[str], None]
"""Told each step of opening a PDF: `reading`, `loading_model`, `detecting`."""


class ReviewError(Exception):
    """A request the window cannot carry out; its message is shown to the reviewer."""


@dataclass
class _OpenDocument:
    """The document under review, its file, and the exact bytes it was loaded from."""

    source: Path
    document: Document
    pdf_bytes: bytes


class ReviewApi:
    """The calls available to the review window.

    One document is open at a time. Every method that needs it raises
    `ReviewError` when none is.
    """

    def __init__(self, resource_root: Path | None = None) -> None:
        """Initialize the API.

        Args:
            resource_root: Directory holding `models/`, as for the CLI's
                `--resource-root`; the working directory when omitted.
        """
        self._open: _OpenDocument | None = None
        self._resource_root = resource_root or Path()
        # Loaded on first use and kept: loading takes seconds, detecting does not.
        self._model: Detector | None = None

    def status(self) -> dict[str, Any]:
        """Describe what this installation can do, for the home screen.

        Checking the name model never loads it, so the home screen appears at
        once.

        Returns:
            The version, the languages with their own rules, and the name
            model's state: `ready`, `not_installed` (the optional `ner`
            dependencies are missing) or `files_missing` (with the catalog ids
            to fetch).
        """
        missing = missing_gliner_files(self._resource_root)
        if not gliner_installed():
            state = "not_installed"
        elif missing:
            state = "files_missing"
        else:
            state = "ready"
        return {
            "version": __version__,
            "languages": [{"code": code, "name": name} for code, name in LANGUAGES.items()],
            "model": {"state": state, "missing": missing},
        }

    def open_pdf(
        self,
        path: str,
        language: str | None = None,
        propagate: bool = True,
        use_model: bool = False,
        progress: Progress | None = None,
    ) -> dict[str, Any]:
        """Open a PDF and propose redactions for it.

        Args:
            path: The PDF to review.
            language: BCP 47 tag selecting the rules; every rule runs when omitted.
            propagate: Also mark further occurrences of the text found.
            use_model: Also run the name model (see `status`).
            progress: Told each step as it starts.

        Returns:
            The document as `document()` describes it.

        Raises:
            ReviewError: If the file is missing or unreadable, or the model was
                asked for but cannot be loaded.
        """
        report = progress or (lambda _step: None)
        report("reading")
        with _as_review_error():
            pdf_bytes = read_pdf(path)
            document = document_from_bytes(pdf_bytes, language=language)
        model = self._loaded_model(report) if use_model else None
        report("detecting")
        run_detection(document, build_detector(language, model=model), propagate=propagate)
        self._open = _OpenDocument(Path(path), document, pdf_bytes)
        return self.document()

    def _loaded_model(self, report: Progress) -> Detector:
        """Return the name model, loading it the first time."""
        if self._model is None:
            report("loading_model")
            try:
                self._model = load_gliner_detector(self._resource_root)
            except (ImportError, FileNotFoundError) as error:
                msg = f"the name model is not available: {error}"
                raise ReviewError(msg) from error
        return self._model

    def open_session(self, pdf_path: str, session_path: str) -> dict[str, Any]:
        """Reopen a saved review of a PDF.

        Args:
            pdf_path: The original PDF.
            session_path: The session file saved from a review of it.

        Returns:
            The document as `document()` describes it.

        Raises:
            ReviewError: If the session belongs to another file or no longer
                matches it, or either file cannot be read.
        """
        with _as_review_error():
            pdf_bytes = read_pdf(pdf_path)
            document = apply_session(document_from_bytes(pdf_bytes), session_path)
        self._open = _OpenDocument(Path(pdf_path), document, pdf_bytes)
        return self.document()

    @property
    def name(self) -> str:
        """File name of the open PDF, for the window title and default file names.

        Raises:
            ReviewError: If no document is open.
        """
        return self._current().source.name

    def close(self) -> None:
        """Forget the open document, so its content no longer stays in memory."""
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
        with pymupdf.open(stream=current.pdf_bytes, filetype="pdf") as pdf:
            png = pdf[index].get_pixmap(dpi=resolution).tobytes("png")
        return "data:image/png;base64," + base64.b64encode(png).decode("ascii")

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
        return _entity_payload(entity)

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
        return _entity_payload(region)

    def remove_entity(self, entity_id: str) -> None:
        """Remove an item the reviewer added, such as a region drawn by mistake.

        Args:
            entity_id: The item to remove.

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
        current.document.remove_entity(entity_id)

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

    def export(self, path: str, allow_pages_without_text: bool = False) -> dict[str, Any]:
        """Write the redacted copy, keeping it only if the leak check passes.

        Undecided items are redacted, rejected ones kept, and every hidden
        item removed (`export_redacted`).

        Args:
            path: Where to write the copy; the window's save dialog has
                already confirmed replacing an existing file.
            allow_pages_without_text: Export even though some pages have no
                text layer. Nothing on such a page is detected, so it reaches
                the output unredacted while the leak check still passes.

        Returns:
            What the export did: whether the copy was written, the counts of
            redacted, kept and not reviewed items and of hidden items removed,
            the pages left unredacted, and the leaks that stopped it.

        Raises:
            ReviewError: If pages have no text layer and that was not allowed,
                the path is the original, or the original changed on disk.
        """
        current = self._current()
        unreadable = [index + 1 for index in pages_needing_ocr(current.document)]
        if unreadable and not allow_pages_without_text:
            listed = ", ".join(str(page) for page in unreadable)
            msg = f"page {listed} has no text layer; nothing on it would be redacted"
            raise ReviewError(msg)
        with _as_review_error():
            leaks = export_redacted(current.source, current.document, path)
        return _export_payload(Path(path).name, current.document, leaks, unreadable)

    def _current(self) -> _OpenDocument:
        if self._open is None:
            msg = "no document is open"
            raise ReviewError(msg)
        return self._open


@contextmanager
def _as_review_error() -> Iterator[None]:
    """Turn the errors the core reports for bad input into `ReviewError`."""
    try:
        yield
    except (ValueError, KeyError, OSError, pymupdf.FileDataError) as error:
        # str() of a KeyError quotes its message.
        message = error.args[0] if isinstance(error, KeyError) and error.args else str(error)
        raise ReviewError(message) from error


def _page_payload(page: Page) -> dict[str, Any]:
    return {
        "index": page.index,
        "width": page.width,
        "height": page.height,
        "has_text_layer": page.has_text_layer,
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
    name: str, document: Document, leaks: list[Leak], unreadable: list[int]
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
        "leaks": [
            {"layer": leak.layer.value, "where": leak.where, "text": leak.text} for leak in leaks
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
