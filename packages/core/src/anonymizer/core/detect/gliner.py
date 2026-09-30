"""Name and address detection with GLiNER, a zero-shot span model.

GLiNER is prompted with plain-text labels ("person") and returns character
spans with a score. Three properties of the model shape this module:

- It reads at most 384 words and drops the rest with only a warning, so a
  name on the lower half of a page would never be seen. Pages are therefore
  scanned in overlapping windows.
- Its spans can stop inside a word ("s.r.o" for "s.r.o."). Spans are widened
  to whole words, since a cut word leaks the remainder in the text layer.
- Its configuration names the encoder by Hub id, and the `gliner` package
  resolves that id when loading. `load_gliner` points it at the local copy
  from the resource catalog, so loading never touches the network.

`gliner` (and PyTorch with it) is an optional dependency: install the `ner`
extra. The detector itself only needs an object with an `inference` method,
which keeps it testable without the model.
"""

from __future__ import annotations

import logging
import os
import re
import warnings
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from anonymizer.core.detect.base import merge_entities
from anonymizer.core.resources import load_catalog, resource_status
from anonymizer.core.types import DetectionSource, Entity, EntityType, Page

GLINER_RESOURCE = "gliner-multi-v2.1"
"""Catalog id of the model; its requirements hold the encoder tokenizer."""

ENCODER_RESOURCE = "mdeberta-v3-base-tokenizer"

DEFAULT_LABELS: Mapping[str, EntityType] = {
    "person": EntityType.PERSON,
    "street address": EntityType.ADDRESS,
}
"""Prompt label → entity type. Organizations are left out: a company name is
not personal data, and a sole trader's name is caught by the person label."""

DEFAULT_THRESHOLD = 0.3
"""Below GLiNER's own default (0.5) because detection is recall-first; a false
positive costs a click in review. To be tuned on development data only."""

WINDOW_WORDS = 120
"""Words per window. GLiNER's limit is 384 of its own tokens, which split off
punctuation, and the encoder's is 512 subword tokens; Czech averages about two
subwords per word, so 120 whitespace-separated words stay well inside both."""

OVERLAP_WORDS = 30
"""Words shared by consecutive windows, so a name cut by one window's edge is
seen whole by the next."""

# Czech and Slovak also quote with single low-9 and single turned commas,
# written as escapes because they look like a comma and backticks.
_OFFLINE_VARIABLES = ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")

_EDGE_PUNCTUATION = ",;:!?()[]{}\"'„“”\u201a\u2018\u2019«»"
_WORD = re.compile(r"\S+")


class SpanModel(Protocol):
    """The part of a GLiNER model the detector uses."""

    def inference(
        self,
        texts: list[str],
        labels: list[str],
        *,
        threshold: float,
        flat_ner: bool,
    ) -> list[list[dict[str, Any]]]:
        """Return, per text, dicts with `start`, `end`, `label` and `score`."""
        ...


@dataclass(frozen=True, slots=True)
class _Window:
    start: int
    end: int


class GlinerDetector:
    """Detects entities with a GLiNER model, window by window.

    Attributes:
        labels: Prompt label → entity type.
        threshold: Minimum score for a span to be reported.
    """

    def __init__(
        self,
        model: SpanModel,
        labels: Mapping[str, EntityType] = DEFAULT_LABELS,
        threshold: float = DEFAULT_THRESHOLD,
        name: str = GLINER_RESOURCE,
    ) -> None:
        """Initialize the detector.

        Args:
            model: A loaded GLiNER model (see `load_gliner`) or a stand-in.
            labels: Prompt label → entity type.
            threshold: Minimum score for a span to be reported.
            name: Identifier used in logs and evaluation reports.

        Raises:
            ValueError: If no label is given or the threshold is outside `[0, 1]`.
        """
        if not labels:
            msg = "at least one label is needed"
            raise ValueError(msg)
        if not 0.0 <= threshold <= 1.0:
            msg = f"threshold out of range: {threshold}"
            raise ValueError(msg)
        self.model = model
        self.labels = dict(labels)
        self.threshold = threshold
        self._name = name
        self._types_by_label = {label.lower(): kind for label, kind in self.labels.items()}

    @property
    def name(self) -> str:
        """Identifier used in logs and evaluation reports."""
        return self._name

    def detect(self, page: Page) -> list[Entity]:
        """Return the entities the model finds on a page.

        Args:
            page: Page to scan; offsets refer to `page.text`.

        Returns:
            Entities in reading order, with geometry resolved from page words.
        """
        windows = list(_windows(page.text))
        if not windows:
            return []
        predictions = self.model.inference(
            [page.text[window.start : window.end] for window in windows],
            list(self.labels),
            threshold=self.threshold,
            flat_ner=True,
        )
        entities = [
            entity
            for window, spans in zip(windows, predictions, strict=True)
            for span in spans
            if (entity := self._entity(page, window, span)) is not None
        ]
        return merge_entities(entities)

    def _entity(self, page: Page, window: _Window, span: Mapping[str, Any]) -> Entity | None:
        kind = self._types_by_label.get(str(span["label"]).lower())
        if kind is None:
            return None
        widened = widen_to_words(
            page.text, window.start + span["start"], window.start + span["end"]
        )
        if widened is None:
            return None
        start, end = widened
        return Entity(
            type=kind,
            page_index=page.index,
            start=start,
            end=end,
            text=page.text[start:end],
            bboxes=page.bboxes_for_span(start, end),
            source=DetectionSource.MODEL,
            score=min(1.0, max(0.0, float(span["score"]))),
        )


def widen_to_words(text: str, start: int, end: int) -> tuple[int, int] | None:
    """Extend a span to whole whitespace-separated words, minus edge punctuation.

    A span ending inside a word would leave the rest of the word in the text
    layer. Quotes, brackets and separators at the edges are dropped again,
    and so is a final full stop, unless the word holds another one: "Novák."
    ends a sentence, "s.r.o." is an abbreviation.

    Args:
        text: The text the span refers to.
        start: First offset of the span.
        end: Offset one past the span.

    Returns:
        The widened span, or `None` if nothing but whitespace and punctuation
        is left.
    """
    while start > 0 and not text[start - 1].isspace():
        start -= 1
    while end < len(text) and not text[end].isspace():
        end += 1
    while start < end and (text[start].isspace() or text[start] in _EDGE_PUNCTUATION):
        start += 1
    while end > start and (text[end - 1].isspace() or text[end - 1] in _EDGE_PUNCTUATION):
        end -= 1
    last_word = text[start:end].split()[-1] if end > start else ""
    if last_word.endswith(".") and last_word.count(".") == 1 and len(last_word) > 1:
        end -= 1
    return (start, end) if end > start else None


def _windows(text: str) -> Iterator[_Window]:
    words = [match.span() for match in _WORD.finditer(text)]
    step = WINDOW_WORDS - OVERLAP_WORDS
    for first in range(0, len(words), step):
        chunk = words[first : first + WINDOW_WORDS]
        yield _Window(chunk[0][0], chunk[-1][1])
        if first + WINDOW_WORDS >= len(words):
            return


def load_gliner_detector(
    root: Path,
    *,
    labels: Mapping[str, EntityType] = DEFAULT_LABELS,
    threshold: float = DEFAULT_THRESHOLD,
) -> GlinerDetector:
    """Build the GLiNER detector from the catalog's files under a storage root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).
        labels: Prompt label → entity type.
        threshold: Minimum score for a span to be reported.

    Returns:
        A ready detector.

    Raises:
        FileNotFoundError: If the model or its encoder files are not stored.
        ImportError: If the `gliner` package is not installed.
    """
    catalog = load_catalog()
    missing = [
        resource.id
        for resource in catalog.with_requirements(GLINER_RESOURCE)
        if resource_status(resource, root) != "present"
    ]
    if missing:
        msg = (
            f"model files missing under {root}: {', '.join(missing)}; "
            f"fetch them with: uv run python scripts/download.py fetch {GLINER_RESOURCE}"
        )
        raise FileNotFoundError(msg)
    model = load_gliner(
        catalog[GLINER_RESOURCE].directory(root),
        catalog[ENCODER_RESOURCE].directory(root),
    )
    return GlinerDetector(model, labels=labels, threshold=threshold)


def load_gliner(model_dir: Path, encoder_dir: Path) -> SpanModel:
    """Load a GLiNER model from local files only.

    Args:
        model_dir: Directory with `gliner_config.json` and the weights.
        encoder_dir: Directory with the encoder's config and tokenizer.

    Returns:
        The loaded model.

    Raises:
        ImportError: If the `gliner` package is not installed.
    """
    # Belt and braces: local_files_only covers the model, the variables cover
    # anything transformers resolves on its own. Set outright rather than as
    # defaults, so an environment saying otherwise cannot reopen the network.
    # huggingface_hub reads them when first imported, which happens below.
    for variable in _OFFLINE_VARIABLES:
        os.environ[variable] = "1"
    with without_known_warnings():
        try:
            from gliner import GLiNER  # pyright: ignore[reportMissingImports]
        except ImportError as error:
            msg = "name detection needs the optional 'ner' dependencies: uv sync --group ner"
            raise ImportError(msg) from error
        with _local_encoder(encoder_dir):
            model = GLiNER.from_pretrained(str(model_dir), local_files_only=True)
    # gliner types the result as a union of every architecture it can load;
    # this model's config selects a uni-encoder span model, which fits.
    return cast("SpanModel", model)


@contextmanager
def _local_encoder(encoder_dir: Path) -> Iterator[None]:
    """Make gliner read the encoder from `encoder_dir` instead of its Hub id.

    gliner (0.2.x) offers no argument for this: the id comes from
    `gliner_config.json` and feeds `AutoConfig` and `AutoTokenizer`. Its config
    loader accepts overrides, so it is wrapped for the duration of the load.
    """
    from gliner.model import BaseGLiNER  # pyright: ignore[reportMissingImports]

    original = BaseGLiNER.__dict__["_load_config"]
    load_config = original.__func__

    def with_local_encoder(cls: type, config_file: Path, **overrides: Any) -> object:
        return load_config(cls, config_file, **{**overrides, "model_name": str(encoder_dir)})

    BaseGLiNER._load_config = classmethod(with_local_encoder)  # pyright: ignore[reportAttributeAccessIssue]
    try:
        yield
    finally:
        BaseGLiNER._load_config = original


@contextmanager
def without_known_warnings() -> Iterator[None]:
    """Hide two library messages that do not apply to this model.

    - PyTorch deprecates `torch.jit.script`, which transformers' DeBERTa
      module uses when it is imported. Nothing to act on in this project.
    - transformers warns of an "incorrect regex pattern" whenever a local
      tokenizer's config lacks a `transformers_version` field, which
      mDeBERTa's does. The check targets Mistral tokenizers; on this path it
      only logs and leaves the tokenizer unchanged.

    Only these two messages are filtered, and only while the block runs.
    """
    tokenizer_logger = logging.getLogger("transformers.tokenization_utils_tokenizers")
    regex_filter = _DropMessage("incorrect regex pattern")
    tokenizer_logger.addFilter(regex_filter)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"`torch\.jit\.script` is deprecated",
                category=FutureWarning,
            )
            yield
    finally:
        tokenizer_logger.removeFilter(regex_filter)


class _DropMessage(logging.Filter):
    def __init__(self, fragment: str) -> None:
        super().__init__()
        self.fragment = fragment

    def filter(self, record: logging.LogRecord) -> bool:
        return self.fragment not in record.getMessage()
