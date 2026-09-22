"""Shared data contract exchanged by ingest, detection, review and redaction.

Object graph: `Document -> Page -> Word` for the page content and
`Document -> Surface` for strings carried outside it, with `Entity` objects
attached to the document and referring back to a page or a surface.

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
    words and lines, which is why it carries a list of boxes. A region entity,
    drawn by a reviewer over something without text, has no offsets and one box.

Surfaces:
    Link targets, metadata, form field values, bookmarks, annotations,
    attachments and a tagged PDF's structure tree hold strings that never appear
    in `Page.text`, so redacting the
    page content leaves them intact. Ingest lists each such string as a
    `Surface`. An entity found in one sets `Entity.surface_id`, and its offsets
    then refer to `Surface.value` instead of `Page.text`.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Self
from uuid import uuid4

SCHEMA_VERSION = 6
"""Version of the serialized review format. Bump on any incompatible change."""


class EntityType(StrEnum):
    """Category of detected personal data."""

    PERSON = "person"
    BIRTH_NUMBER = "birth_number"
    BANK_ACCOUNT = "bank_account"
    IBAN = "iban"
    CREDIT_CARD = "credit_card"
    COMPANY_ID = "company_id"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    ADDRESS = "address"
    DATE = "date"
    ID_NUMBER = "id_number"
    ORGANIZATION = "organization"
    REGION = "region"
    OTHER = "other"


class SurfaceKind(StrEnum):
    """Carrier of a string that lies outside the page text."""

    METADATA = "metadata"
    XMP = "xmp"
    LINK = "link"
    ANNOTATION = "annotation"
    FORM_FIELD = "form_field"
    BOOKMARK = "bookmark"
    EMBEDDED_FILE = "embedded_file"
    STRUCTURE = "structure"


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


@dataclass(frozen=True, slots=True)
class Surface:
    """A string the document carries outside its page text.

    Redaction and the leakage check walk every surface, not only those in which
    an entity was detected: a surface is a place where personal data can hide
    whether or not a detector recognises it.

    Attributes:
        kind: Carrier the string comes from.
        value: The string, NFC-normalized. Offsets of entities on this surface
            refer to it.
        ref: Locator of the carrier within the source file. Its format belongs
            to the ingest module that produced the surface; redaction of the
            same file uses it to find the object again.
        page_index: Page the carrier sits on, or `None` for a document-level
            carrier such as metadata.
        bbox: The carrier's own rectangle on the page, e.g. a link's clickable
            area, or `None` if it has none. Not derived from words.
    """

    kind: SurfaceKind
    value: str
    ref: str
    page_index: int | None = None
    bbox: BBox | None = None

    def __post_init__(self) -> None:
        """Reject empty values, negative page indices and unplaced boxes.

        Raises:
            ValueError: If the value is empty, the page index is negative or a
                box is given without a page.
        """
        if not self.value:
            msg = f"empty surface value: {self.kind} {self.ref}"
            raise ValueError(msg)
        if self.page_index is not None and self.page_index < 0:
            msg = f"negative page index: {self.page_index}"
            raise ValueError(msg)
        if self.bbox is not None and self.page_index is None:
            msg = f"surface has a bbox but no page: {self.kind} {self.ref}"
            raise ValueError(msg)

    @property
    def surface_id(self) -> str:
        """Identifier entities use to refer to the surface.

        Derived from what the surface is, not generated, so loading the same
        file twice yields the same ids and a saved review still points at the
        right carrier. The page is part of it because a reference is unique
        only within its page or the document level.
        """
        page = "doc" if self.page_index is None else str(self.page_index)
        return f"{self.kind.value}:{page}:{self.ref}"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping."""
        return {
            "surface_id": self.surface_id,
            "kind": self.kind.value,
            "value": self.value,
            "ref": self.ref,
            "page_index": self.page_index,
            "bbox": self.bbox.to_list() if self.bbox is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a surface from `to_dict` output.

        Args:
            data: Serialized surface.

        Returns:
            The surface.
        """
        bbox = data.get("bbox")
        return cls(
            kind=SurfaceKind(data["kind"]),
            value=data["value"],
            ref=data["ref"],
            page_index=data.get("page_index"),
            bbox=BBox.from_list(bbox) if bbox is not None else None,
        )


@dataclass(slots=True)
class Entity:
    """Personal data to redact: a span of text, or a region drawn on a page.

    A text entity covers a span of `Page.text`, or of `Surface.value` when
    `surface_id` is set. A region entity (type `REGION`) is a rectangle a
    reviewer drew over something that has no text, such as a photo, a signature
    or a stamp: it has no span and exactly one box.

    Attributes:
        type: Category of personal data.
        page_index: Page the entity belongs to. `None` only for an entity on a
            document-level surface.
        start: First offset of the span in `Page.text`, or in `Surface.value`
            when `surface_id` is set; `None` for a region.
        end: Offset one past the span, in the same text as `start`; `None` for
            a region.
        text: The covered text, kept for review and leakage checks; `None` for
            a region.
        surface_id: Surface the span lies in, or `None` for page text.
        bboxes: One box per covered word, the surface's own box, or a region's
            single box; empty until geometry is resolved.
        source: Component that produced the entity.
        score: Detector confidence in `[0, 1]`, or `None` for rule matches.
        review: Human review outcome.
        replacement: Substitute string for label or pseudonym redaction.
        entity_id: Stable identifier so the UI and review files can reference
            an entity across edits.
    """

    type: EntityType
    page_index: int | None
    start: int | None = None
    end: int | None = None
    text: str | None = None
    surface_id: str | None = None
    bboxes: list[BBox] = field(default_factory=list)
    source: DetectionSource = DetectionSource.RULE
    score: float | None = None
    review: ReviewState = ReviewState.PENDING
    replacement: str | None = None
    entity_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        """Reject impossible spans, regions, page indices and scores.

        Raises:
            ValueError: If a text entity lacks a valid span or a page index
                where it needs one, a region carries a span or not exactly one
                box, the page index is negative, or the score lies outside
                `[0, 1]`.
        """
        if self.is_region:
            self._check_region()
        else:
            self._check_span()
        if self.page_index is not None and self.page_index < 0:
            msg = f"negative page index: {self.page_index}"
            raise ValueError(msg)
        if self.score is not None and not 0.0 <= self.score <= 1.0:
            msg = f"score out of range: {self.score}"
            raise ValueError(msg)

    def _check_span(self) -> None:
        """Validate a text entity's span and page."""
        if self.start is None or self.end is None or self.text is None:
            msg = f"a {self.type} entity needs a text span"
            raise ValueError(msg)
        if self.start < 0 or self.end <= self.start:
            msg = f"invalid entity span [{self.start}, {self.end})"
            raise ValueError(msg)
        if self.page_index is None and self.surface_id is None:
            msg = "an entity in page text needs a page index"
            raise ValueError(msg)

    def _check_region(self) -> None:
        """Validate a region: a page, one box with an area, and nothing else."""
        if self.start is not None or self.end is not None or self.text is not None:
            msg = "a region has no text span"
            raise ValueError(msg)
        if self.surface_id is not None:
            msg = "a region cannot lie on a surface"
            raise ValueError(msg)
        if self.page_index is None:
            msg = "a region needs a page index"
            raise ValueError(msg)
        if len(self.bboxes) != 1 or self.bboxes[0].width <= 0 or self.bboxes[0].height <= 0:
            msg = "a region needs exactly one box with an area"
            raise ValueError(msg)

    @property
    def is_region(self) -> bool:
        """Whether the entity is a drawn region rather than a span of text."""
        return self.type is EntityType.REGION

    @property
    def in_page_text(self) -> bool:
        """Whether the entity is a span of `Page.text`."""
        return self.surface_id is None and not self.is_region

    @property
    def span(self) -> tuple[int, int]:
        """The span's start and end offsets.

        Raises:
            ValueError: If the entity is a region, which has no span.
        """
        if self.start is None or self.end is None:
            msg = f"entity {self.entity_id} is a region and has no span"
            raise ValueError(msg)
        return self.start, self.end

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
            "surface_id": self.surface_id,
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
            start=data.get("start"),
            end=data.get("end"),
            text=data.get("text"),
            surface_id=data.get("surface_id"),
            bboxes=[BBox.from_list(box) for box in data.get("bboxes", [])],
            source=DetectionSource(data.get("source", DetectionSource.RULE)),
            score=data.get("score"),
            review=ReviewState(data.get("review", ReviewState.PENDING)),
            replacement=data.get("replacement"),
            entity_id=data.get("entity_id") or uuid4().hex,
        )


@dataclass(slots=True)
class Document:
    """A whole document with its pages, surfaces and detected entities.

    Attributes:
        pages: Pages in document order.
        surfaces: Strings carried outside the page text.
        entities: Detected entities, each pointing at a page by index and, when
            found outside the page text, at a surface by id.
        fingerprint: SHA-256 of the source file, so a document, and a review
            saved from it, can only be applied to the file it was made from.
            The file's name is not kept: names such as
            `<first>-<last>-<id>.pdf` are personal data themselves.
        language: BCP 47 tag the detectors are configured for, e.g. `"en"`.
        schema_version: Version of the serialized format.
    """

    pages: list[Page] = field(default_factory=list)
    surfaces: list[Surface] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    fingerprint: str | None = None
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

    def surface(self, surface_id: str) -> Surface:
        """Return the surface with the given id.

        Args:
            surface_id: Identifier of the surface.

        Returns:
            The surface.

        Raises:
            KeyError: If no surface carries that id.
        """
        for surface in self.surfaces:
            if surface.surface_id == surface_id:
                return surface
        msg = f"no surface with id {surface_id}"
        raise KeyError(msg)

    def entities_on_page(self, index: int) -> list[Entity]:
        """Return the entities in one page's text, in reading order.

        Entities on surfaces are excluded even when the surface sits on the
        page, because their offsets refer to the surface value; see
        `entities_in_surface`.

        Args:
            index: Zero-based page number.

        Returns:
            Entities sorted by their start offset in `Page.text`.
        """
        found = [
            entity for entity in self.entities if entity.in_page_text and entity.page_index == index
        ]
        return sorted(found, key=lambda entity: entity.span)

    def regions_on_page(self, index: int) -> list[Entity]:
        """Return the regions drawn on one page.

        Args:
            index: Zero-based page number.

        Returns:
            Region entities in the order they were added.
        """
        return [
            entity for entity in self.entities if entity.is_region and entity.page_index == index
        ]

    def entities_in_surface(self, surface_id: str) -> list[Entity]:
        """Return the entities found on one surface, in offset order.

        Args:
            surface_id: Identifier of the surface.

        Returns:
            Entities sorted by their start offset in `Surface.value`.
        """
        found = [entity for entity in self.entities if entity.surface_id == surface_id]
        return sorted(found, key=lambda entity: entity.span)

    def resolve_bboxes(self) -> None:
        """Fill in `Entity.bboxes` for entities lacking them.

        Page-text entities get one box per covered word. Surface entities get
        the surface's own box, or none for a surface that is not drawn. Regions
        always carry their box already.
        """
        for entity in self.entities:
            if entity.bboxes or entity.is_region:
                continue
            if entity.surface_id is not None:
                bbox = self.surface(entity.surface_id).bbox
                entity.bboxes = [bbox] if bbox is not None else []
            elif entity.page_index is not None:
                page = self.page(entity.page_index)
                entity.bboxes = page.bboxes_for_span(*entity.span)

    def check_references(self) -> None:
        """Verify that every surface entity points at a surface it matches.

        Raises:
            ValueError: If an entity names an unknown surface or a page other
                than its surface's.
        """
        surfaces = {surface.surface_id: surface for surface in self.surfaces}
        for entity in self.entities:
            if entity.surface_id is None:
                continue
            surface = surfaces.get(entity.surface_id)
            if surface is None:
                msg = f"entity {entity.entity_id} refers to unknown surface {entity.surface_id}"
                raise ValueError(msg)
            if entity.page_index != surface.page_index:
                msg = (
                    f"entity {entity.entity_id} is on page {entity.page_index}, "
                    f"its surface on page {surface.page_index}"
                )
                raise ValueError(msg)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping."""
        return {
            "schema_version": self.schema_version,
            "fingerprint": self.fingerprint,
            "language": self.language,
            "pages": [page.to_dict() for page in self.pages],
            "surfaces": [surface.to_dict() for surface in self.surfaces],
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
            ValueError: If the payload was written by an incompatible version or
                an entity refers to a surface inconsistently.
        """
        version = data.get("schema_version", SCHEMA_VERSION)
        if version != SCHEMA_VERSION:
            msg = f"unsupported schema version {version}, expected {SCHEMA_VERSION}"
            raise ValueError(msg)
        document = cls(
            pages=[Page.from_dict(page) for page in data.get("pages", [])],
            surfaces=[Surface.from_dict(surface) for surface in data.get("surfaces", [])],
            entities=[Entity.from_dict(entity) for entity in data.get("entities", [])],
            fingerprint=data.get("fingerprint"),
            language=data.get("language"),
            schema_version=version,
        )
        document.check_references()
        return document

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
