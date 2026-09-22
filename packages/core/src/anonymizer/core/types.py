"""Shared data contract exchanged by ingest, detection, review and redaction.

Object graph: `Document -> Page -> Word` with `Entity` objects attached to the
document and referring back to a page by index.

Coordinate system:
    All boxes are in PDF user-space points (1/72 inch), relative to the page,
    with the origin at the **top-left** corner and `y` growing downward. This
    matches PyMuPDF's `page.rect` so extracted boxes need no conversion. A page
    rasterized for OCR reports the scale it was rendered at in `Page.raster_dpi`;
    pixel coordinates must be converted to points before they enter a `BBox`
    (`points = pixels * 72 / dpi`).

Text offsets:
    `Word.start`/`Word.end` and `Entity.start`/`Entity.end` are character offsets
    into `Page.text`, which is the page's reading-order reconstruction. Offsets
    are page-local: an entity never spans two pages, but it may span several
    words and lines, which is why it carries a list of boxes.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Self
from uuid import uuid4

SCHEMA_VERSION = 1
"""Version of the serialized review format. Bump on any incompatible change."""


class EntityType(StrEnum):
    """Category of detected personal data."""

    PERSON = "person"
    BIRTH_NUMBER = "birth_number"
    BANK_ACCOUNT = "bank_account"
    IBAN = "iban"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    DATE = "date"
    ID_NUMBER = "id_number"
    ORGANIZATION = "organization"
    OTHER = "other"


class DetectionSource(StrEnum):
    """Which component produced an entity."""

    RULE = "rule"
    MODEL = "model"
    MANUAL = "manual"


class ReviewState(StrEnum):
    """Outcome of human review for a single entity."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class BBox:
    """Axis-aligned rectangle in page points, origin top-left.

    Attributes:
        x0: Left edge.
        y0: Top edge.
        x1: Right edge.
        y1: Bottom edge.
    """

    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        """Reject inverted rectangles.

        Raises:
            ValueError: If either edge pair is inverted.
        """
        if self.x1 < self.x0 or self.y1 < self.y0:
            msg = f"inverted bbox: {self!r}"
            raise ValueError(msg)

    @property
    def width(self) -> float:
        """Horizontal extent in points."""
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """Vertical extent in points."""
        return self.y1 - self.y0

    def union(self, other: BBox) -> BBox:
        """Return the smallest box containing both boxes.

        Args:
            other: Box to merge with.

        Returns:
            The enclosing box.
        """
        return BBox(
            min(self.x0, other.x0),
            min(self.y0, other.y0),
            max(self.x1, other.x1),
            max(self.y1, other.y1),
        )

    @classmethod
    def enclosing(cls, boxes: Iterable[BBox]) -> BBox:
        """Return the smallest box containing every given box.

        Args:
            boxes: Boxes to merge; must not be empty.

        Returns:
            The enclosing box.

        Raises:
            ValueError: If `boxes` is empty.
        """
        merged: BBox | None = None
        for box in boxes:
            merged = box if merged is None else merged.union(box)
        if merged is None:
            msg = "enclosing() requires at least one box"
            raise ValueError(msg)
        return merged

    def to_list(self) -> list[float]:
        """Return the box as `[x0, y0, x1, y1]` for compact serialization."""
        return [self.x0, self.y0, self.x1, self.y1]

    @classmethod
    def from_list(cls, values: list[float]) -> Self:
        """Rebuild a box from `[x0, y0, x1, y1]`.

        Args:
            values: Four edge coordinates.

        Returns:
            The box.

        Raises:
            ValueError: If `values` does not hold exactly four numbers.
        """
        if len(values) != 4:
            msg = f"expected 4 coordinates, got {len(values)}"
            raise ValueError(msg)
        x0, y0, x1, y1 = values
        return cls(x0, y0, x1, y1)


@dataclass(frozen=True, slots=True)
class Word:
    """A token with its position on the page and in the page text.

    Attributes:
        text: Word as it appears in `Page.text`.
        bbox: Position on the page.
        start: Offset of the word's first character in `Page.text`.
        end: Offset one past the word's last character in `Page.text`.
    """

    text: str
    bbox: BBox
    start: int
    end: int

    def __post_init__(self) -> None:
        """Reject empty or negative spans.

        Raises:
            ValueError: If the span is not a positive range at a valid offset.
        """
        if self.start < 0 or self.end <= self.start:
            msg = f"invalid word span [{self.start}, {self.end})"
            raise ValueError(msg)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping."""
        return {
            "text": self.text,
            "bbox": self.bbox.to_list(),
            "start": self.start,
            "end": self.end,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a word from `to_dict` output.

        Args:
            data: Serialized word.

        Returns:
            The word.
        """
        return cls(
            text=data["text"],
            bbox=BBox.from_list(data["bbox"]),
            start=data["start"],
            end=data["end"],
        )


@dataclass(slots=True)
class Page:
    """One page: its geometry, reading-order text and positioned words.

    Attributes:
        index: Zero-based page number within the document.
        width: Page width in points.
        height: Page height in points.
        text: Reading-order reconstruction that offsets refer to.
        words: Words in reading order.
        has_text_layer: Whether the source page carried an extractable text
            layer. `False` means `text` came from OCR.
        raster_dpi: Resolution the page was rendered at before OCR, or `None`
            for a born-digital page.
    """

    index: int
    width: float
    height: float
    text: str = ""
    words: list[Word] = field(default_factory=list)
    has_text_layer: bool = True
    raster_dpi: float | None = None

    def words_in_span(self, start: int, end: int) -> Iterator[Word]:
        """Yield the words overlapping a character span.

        Args:
            start: First offset of the span.
            end: Offset one past the span.

        Yields:
            Words whose own span intersects `[start, end)`, in reading order.
        """
        for word in self.words:
            if word.start < end and start < word.end:
                yield word

    def bboxes_for_span(self, start: int, end: int) -> list[BBox]:
        """Return the boxes of the words overlapping a character span.

        One box per overlapping word, so a span crossing a line break yields
        several boxes rather than one box covering the gap between lines.

        Args:
            start: First offset of the span.
            end: Offset one past the span.

        Returns:
            Boxes in reading order; empty if nothing overlaps.
        """
        return [word.bbox for word in self.words_in_span(start, end)]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping."""
        return {
            "index": self.index,
            "width": self.width,
            "height": self.height,
            "text": self.text,
            "words": [word.to_dict() for word in self.words],
            "has_text_layer": self.has_text_layer,
            "raster_dpi": self.raster_dpi,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a page from `to_dict` output.

        Args:
            data: Serialized page.

        Returns:
            The page.
        """
        return cls(
            index=data["index"],
            width=data["width"],
            height=data["height"],
            text=data.get("text", ""),
            words=[Word.from_dict(word) for word in data.get("words", [])],
            has_text_layer=data.get("has_text_layer", True),
            raster_dpi=data.get("raster_dpi"),
        )


@dataclass(slots=True)
class Entity:
    """A span of personal data detected on one page.

    Attributes:
        type: Category of personal data.
        page_index: Page the span belongs to.
        start: First offset of the span in `Page.text`.
        end: Offset one past the span in `Page.text`.
        text: The matched text, kept for review and leakage checks.
        bboxes: One box per covered word; empty until geometry is resolved.
        source: Component that produced the entity.
        score: Detector confidence in `[0, 1]`, or `None` for rule matches.
        review: Human review outcome.
        replacement: Substitute string for label or pseudonym redaction.
        entity_id: Stable identifier so the UI and review files can reference
            an entity across edits.
    """

    type: EntityType
    page_index: int
    start: int
    end: int
    text: str
    bboxes: list[BBox] = field(default_factory=list)
    source: DetectionSource = DetectionSource.RULE
    score: float | None = None
    review: ReviewState = ReviewState.PENDING
    replacement: str | None = None
    entity_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        """Reject impossible spans, page indices and scores.

        Raises:
            ValueError: If the span is empty, the page index is negative or the
                score lies outside `[0, 1]`.
        """
        if self.start < 0 or self.end <= self.start:
            msg = f"invalid entity span [{self.start}, {self.end})"
            raise ValueError(msg)
        if self.page_index < 0:
            msg = f"negative page index: {self.page_index}"
            raise ValueError(msg)
        if self.score is not None and not 0.0 <= self.score <= 1.0:
            msg = f"score out of range: {self.score}"
            raise ValueError(msg)

    @property
    def is_redactable(self) -> bool:
        """Whether review left this entity to be applied to the output."""
        return self.review is not ReviewState.REJECTED

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping."""
        return {
            "entity_id": self.entity_id,
            "type": self.type.value,
            "page_index": self.page_index,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "bboxes": [box.to_list() for box in self.bboxes],
            "source": self.source.value,
            "score": self.score,
            "review": self.review.value,
            "replacement": self.replacement,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild an entity from `to_dict` output.

        Args:
            data: Serialized entity.

        Returns:
            The entity.
        """
        return cls(
            type=EntityType(data["type"]),
            page_index=data["page_index"],
            start=data["start"],
            end=data["end"],
            text=data["text"],
            bboxes=[BBox.from_list(box) for box in data.get("bboxes", [])],
            source=DetectionSource(data.get("source", DetectionSource.RULE)),
            score=data.get("score"),
            review=ReviewState(data.get("review", ReviewState.PENDING)),
            replacement=data.get("replacement"),
            entity_id=data.get("entity_id") or uuid4().hex,
        )


@dataclass(slots=True)
class Document:
    """A whole document with its pages and detected entities.

    Attributes:
        pages: Pages in document order.
        entities: Detected entities, each pointing at a page by index.
        source_name: Name of the input file, without a path, for display and
            logging. Never a full path, which may itself be personal data.
        language: BCP 47 tag the detectors are configured for, e.g. `"en"`.
        schema_version: Version of the serialized format.
    """

    pages: list[Page] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    source_name: str | None = None
    language: str | None = None
    schema_version: int = SCHEMA_VERSION

    def page(self, index: int) -> Page:
        """Return the page with the given index.

        Args:
            index: Zero-based page number.

        Returns:
            The page.

        Raises:
            KeyError: If no page carries that index.
        """
        for page in self.pages:
            if page.index == index:
                return page
        msg = f"no page with index {index}"
        raise KeyError(msg)

    def entities_on_page(self, index: int) -> list[Entity]:
        """Return the entities detected on one page, in reading order.

        Args:
            index: Zero-based page number.

        Returns:
            Entities sorted by their start offset.
        """
        found = [entity for entity in self.entities if entity.page_index == index]
        return sorted(found, key=lambda entity: entity.start)

    def resolve_bboxes(self) -> None:
        """Fill in `Entity.bboxes` from page words for entities lacking them."""
        for entity in self.entities:
            if entity.bboxes:
                continue
            entity.bboxes = self.page(entity.page_index).bboxes_for_span(entity.start, entity.end)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping."""
        return {
            "schema_version": self.schema_version,
            "source_name": self.source_name,
            "language": self.language,
            "pages": [page.to_dict() for page in self.pages],
            "entities": [entity.to_dict() for entity in self.entities],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a document from `to_dict` output.

        Args:
            data: Serialized document.

        Returns:
            The document.

        Raises:
            ValueError: If the payload was written by an incompatible version.
        """
        version = data.get("schema_version", SCHEMA_VERSION)
        if version != SCHEMA_VERSION:
            msg = f"unsupported schema version {version}, expected {SCHEMA_VERSION}"
            raise ValueError(msg)
        return cls(
            pages=[Page.from_dict(page) for page in data.get("pages", [])],
            entities=[Entity.from_dict(entity) for entity in data.get("entities", [])],
            source_name=data.get("source_name"),
            language=data.get("language"),
            schema_version=version,
        )

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize the document to JSON.

        Args:
            indent: Indentation passed to `json.dumps`; `None` for compact output.

        Returns:
            JSON text with non-ASCII characters preserved.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, text: str) -> Self:
        """Parse a document from JSON produced by `to_json`.

        Args:
            text: JSON text.

        Returns:
            The document.
        """
        return cls.from_dict(json.loads(text))
