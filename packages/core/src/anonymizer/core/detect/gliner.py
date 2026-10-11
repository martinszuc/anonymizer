"""Name and address detection with GLiNER, a zero-shot span model.

GLiNER is prompted with plain-text labels ("person") and returns character
spans with a score. Four properties of the model shape this module:

- It reads at most 384 of its own tokens and drops the rest with only a
  warning, so a name on the lower half of a page would never be seen. Pages
  are therefore scanned in overlapping windows, counted in those tokens:
  punctuation is a token of its own, and OCR text of handwriting holds so
  much of it that 120 words came to 409 tokens.
- Its spans can stop inside a word ("s.r.o" for "s.r.o."). Spans are widened
  to whole words, since a cut word leaks the remainder in the text layer.
- On a badly read scan it tags lone letters, such as a preposition starting
  a sentence, as an address or a person. A span with fewer than two letters
  or digits identifies no one, and propagation would mark the letter
  wherever it stands alone, so it is dropped.
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
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from anonymizer.core.detect.base import describe, merge_entities
from anonymizer.core.log import fields, step
from anonymizer.core.resources import Catalog, load_catalog, missing_resources
from anonymizer.core.types import DetectionSource, Entity, EntityType, Page

log = logging.getLogger(__name__)

GLINER_RESOURCE = "gliner-multi-v2.1"
"""Catalog id of the zero-shot model; its requirements hold the encoder tokenizer."""

DEFAULT_LABELS: Mapping[str, EntityType] = {
    "person": EntityType.PERSON,
    "street address": EntityType.ADDRESS,
}
"""Prompt label → entity type. A company name is not personal data, and a sole
trader's name is caught by the person label."""

DEFAULT_DISTRACTORS: tuple[str, ...] = ("organization",)
"""Labels the model is asked for whose spans are dropped. Given only "person",
the model has nowhere else to put a company or an institution; offered
"organization" as well, it tags more names and fewer non-names as persons
(CNEC 2.0 development set, threshold 0.3: precision 0.85 → 0.86, recall
0.80 → 0.82). Labels for job titles, roles and places were measured too and
lowered precision; role nouns are handled by `roles.NamesOnly` instead."""

DEFAULT_THRESHOLD = 0.3
"""Below GLiNER's own default (0.5) because detection is recall-first; a false
positive costs a click in review. To be tuned on development data only."""

MODEL_MAX_TOKENS = 384
"""GLiNER's `max_len` in the pinned model's config; tokens past it are dropped.
The encoder sets no limit of its own: its tokenizer has no maximum length and
it uses relative positions only."""

WINDOW_TOKENS = 150
"""GLiNER tokens per window. About 120 words of ordinary prose, which averages
1.24 tokens per word on the benchmark documents; the model limit is the
ceiling, not the target."""

OVERLAP_TOKENS = 40
"""GLiNER tokens shared by consecutive windows, so a name cut by one window's
edge is seen whole by the next."""

_OFFLINE_VARIABLES = ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")

_MIN_CHARACTERS = 2
# Czech and Slovak also quote with single low-9 and single turned commas,
# written as escapes because they look like a comma and backticks.
_EDGE_PUNCTUATION = ",;:!?()[]{}\"'„“”\u201a\u2018\u2019«»"

# gliner's WhitespaceTokenSplitter, the splitter the pinned model's config
# selects (by leaving `words_splitter_type` at its default).
_GLINER_TOKEN = re.compile(r"\w+(?:[-_]\w+)*|\S")


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
        distractors: Labels asked for whose spans are dropped.
        threshold: Minimum score for a span to be reported.
    """

    def __init__(
        self,
        model: SpanModel,
        labels: Mapping[str, EntityType] = DEFAULT_LABELS,
        threshold: float = DEFAULT_THRESHOLD,
        name: str = GLINER_RESOURCE,
        distractors: Sequence[str] = DEFAULT_DISTRACTORS,
    ) -> None:
        """Initialize the detector.

        Args:
            model: A loaded GLiNER model (see `load_gliner`) or a stand-in.
            labels: Prompt label → entity type.
            threshold: Minimum score for a span to be reported.
            name: Identifier used in logs and evaluation reports.
            distractors: Labels asked for whose spans are dropped (see
                `DEFAULT_DISTRACTORS`).

        Raises:
            ValueError: If no label is given, a distractor is also a label, or
                the threshold is outside `[0, 1]`.
        """
        if not labels:
            msg = "at least one label is needed"
            raise ValueError(msg)
        if {label.lower() for label in labels} & {label.lower() for label in distractors}:
            msg = "a label cannot also be a distractor"
            raise ValueError(msg)
        if not 0.0 <= threshold <= 1.0:
            msg = f"threshold out of range: {threshold}"
            raise ValueError(msg)
        self.model = model
        self.labels = dict(labels)
        self.distractors = tuple(distractors)
        self.threshold = threshold
        self._name = name
        self._types_by_label = {label.lower(): kind for label, kind in self.labels.items()}
        self._distractors = {label.lower() for label in self.distractors}

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
        log.debug("%s: page %d: %d windows", self.name, page.index, len(windows))
        predictions = self.model.inference(
            [page.text[window.start : window.end] for window in windows],
            [*self.labels, *self.distractors],
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
        label = str(span["label"]).lower()
        if label in self._distractors:
            return None
        kind = self._types_by_label.get(label)
        if kind is None:
            log.debug("%s: ignored span with unknown label %s", self.name, span["label"])
            return None
        raw_start, raw_end = window.start + span["start"], window.start + span["end"]
        widened = widen_to_words(page.text, raw_start, raw_end)
        if widened is None:
            log.debug(
                "%s: dropped span, only punctuation left after widening:%s",
                self.name,
                fields(raw=page.text[raw_start:raw_end]),
            )
            return None
        start, end = widened
        if sum(character.isalnum() for character in page.text[start:end]) < _MIN_CHARACTERS:
            log.debug("%s: dropped span of one character", self.name)
            return None
        entity = Entity(
            type=kind,
            page_index=page.index,
            start=start,
            end=end,
            text=page.text[start:end],
            bboxes=page.bboxes_for_span(start, end),
            source=DetectionSource.MODEL,
            score=min(1.0, max(0.0, float(span["score"]))),
        )
        if log.isEnabledFor(logging.DEBUG):
            log.debug(
                "%s predicted %s label=%s%s",
                self.name,
                describe(entity),
                span["label"],
                fields(model_span=page.text[raw_start:raw_end])
                if (raw_start, raw_end) != (start, end)
                else "",
            )
        return entity


def widen_to_words(text: str, start: int, end: int) -> tuple[int, int] | None:
    """Extend a span to whole whitespace-separated words, minus edge punctuation.

    A span ending inside a word would leave the rest of the word in the text
    layer. Quotes, brackets and separators at the edges are dropped again,
    and so is a final full stop, unless the word holds another one: "Novák."
    ends a sentence, "s.r.o." is an abbreviation. A full stop after a closing
    bracket or quote always ends the sentence, so it goes before the edges
    are stripped once more: "(J. Novák)." gives "J. Novák".

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
    start, end = _strip_edges(text, start, end)
    if end - start > 1 and text[end - 1] == "." and text[end - 2] in _EDGE_PUNCTUATION:
        start, end = _strip_edges(text, start, end - 1)
    last_word = text[start:end].split()[-1] if end > start else ""
    if last_word.endswith(".") and last_word.count(".") == 1 and len(last_word) > 1:
        end -= 1
    return (start, end) if end > start else None


def _strip_edges(text: str, start: int, end: int) -> tuple[int, int]:
    """Narrow a span past whitespace and edge punctuation on both sides."""
    while start < end and (text[start].isspace() or text[start] in _EDGE_PUNCTUATION):
        start += 1
    while end > start and (text[end - 1].isspace() or text[end - 1] in _EDGE_PUNCTUATION):
        end -= 1
    return start, end


def _windows(text: str) -> Iterator[_Window]:
    """Split text into windows of at most `WINDOW_TOKENS` GLiNER tokens.

    A window starts and ends on a token boundary, which may fall between a
    word and its punctuation, or inside a run of dots with no space; the
    overlap gives the next window the whole word, and spans are widened to
    whole words anyway.
    """
    tokens = gliner_tokens(text)
    step = WINDOW_TOKENS - OVERLAP_TOKENS
    for first in range(0, len(tokens), step):
        chunk = tokens[first : first + WINDOW_TOKENS]
        yield _Window(chunk[0][0], chunk[-1][1])
        if first + WINDOW_TOKENS >= len(tokens):
            return


def gliner_tokens(text: str) -> list[tuple[int, int]]:
    """Return the model's own tokens of a text as character spans.

    These are the tokens `MODEL_MAX_TOKENS` and `WINDOW_TOKENS` count, and the
    units a GLiNER training example is written in.
    """
    return [match.span() for match in _GLINER_TOKEN.finditer(text)]


def load_gliner_detector(
    root: Path,
    model_id: str = GLINER_RESOURCE,
    *,
    catalog: Catalog | None = None,
    labels: Mapping[str, EntityType] = DEFAULT_LABELS,
    threshold: float = DEFAULT_THRESHOLD,
) -> GlinerDetector:
    """Build a GLiNER detector from a catalog model stored under a storage root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).
        model_id: Catalog id of a GLiNER model; a fine-tuned one differs only
            in its weights.
        catalog: The resource catalog; the shipped one and the root's
            trained models when omitted.
        labels: Prompt label → entity type.
        threshold: Minimum score for a span to be reported.

    Returns:
        A ready detector, named after the model.

    Raises:
        FileNotFoundError: If the model or its encoder files are not stored.
        ImportError: If the `gliner` package is not installed.
    """
    model = load_gliner_model(root, model_id, catalog=catalog)
    return GlinerDetector(model, labels=labels, threshold=threshold, name=model_id)


def load_gliner_model(
    root: Path, model_id: str = GLINER_RESOURCE, *, catalog: Catalog | None = None
) -> SpanModel:
    """Load a catalog GLiNER model and its encoder from a storage root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).
        model_id: Catalog id of a GLiNER model.
        catalog: The resource catalog; the shipped one and the root's
            trained models when omitted.

    Returns:
        The loaded model.

    Raises:
        FileNotFoundError: If the model or its encoder files are not stored.
        ImportError: If the `gliner` package is not installed.
    """
    catalog = catalog or load_catalog(root=root)
    missing = missing_resources(catalog, model_id, root)
    if missing:
        remedy = (
            f"it was trained on this machine, as {catalog[model_id].source} records"
            if catalog[model_id].trained and model_id in missing
            else f"fetch them with: uv run python scripts/download.py fetch {model_id}"
        )
        msg = f"model files missing under {root}: {', '.join(missing)}; {remedy}"
        raise FileNotFoundError(msg)
    with step(log, "load name model", done_level=logging.INFO, model=model_id):
        return load_gliner(
            catalog[model_id].directory(root),
            catalog[encoder_resource(catalog, model_id)].directory(root),
        )


def encoder_resource(catalog: Catalog, model_id: str) -> str:
    """Return the catalog id of the encoder tokenizer a model requires (GLiNER, NameTag 3).

    Args:
        catalog: The resource catalog.
        model_id: Catalog id of the model.

    Returns:
        The id of its one requirement used as a tokenizer.

    Raises:
        ValueError: If the model does not require exactly one tokenizer.
    """
    encoders = [
        required for required in catalog[model_id].requires if "tokenizer" in catalog[required].uses
    ]
    if len(encoders) != 1:
        msg = f"{model_id}: the model requires exactly one tokenizer, found {len(encoders)}"
        raise ValueError(msg)
    return encoders[0]


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
