"""Checking a redacted PDF for personal data that survived.

Seven layers, because each misses something the others catch:

1. **Page text.** The output is extracted the way ingest extracts the input,
   and no redacted entity's text may remain on any page.
2. **Regions.** A region has no text to search for, so nothing may remain
   inside its box: no word and no drawing apart from the black fill itself.
   Image pixels under a box are not re-read here; their removal is verified by
   the test suite instead.
3. **Off-page text.** Any word drawn outside a page's visible area is a leak:
   redaction removes that area whole, and ingest never extracted it.
4. **Surfaces.** The surface scan is re-run; redaction clears every surface, so
   any surface left is a leak, whether or not an entity was found in it.
5. **Thumbnails.** A page thumbnail is a picture of the page before redaction.
6. **Objects.** Every object and decompressed stream in the file is searched
   for each entity's text. This catches carriers the surface scan does not list
   (JavaScript, named destinations, an overlooked dictionary). It only sees
   strings stored literally; hex or UTF-16 encoded strings and font-encoded page
   text are the first layers' job.
7. **File bytes.** An incremental save appends new object revisions and leaves
   the old ones in the file, where the object table no longer points but any
   text editor still shows them. The raw bytes are searched as well, with the
   same literal-string limit as layer 6.

Whitespace is ignored when comparing text: a span that crossed a line break
may be extracted with different spacing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, NamedTuple

import pymupdf
from anonymizer.core.ingest import extract_page, extract_surfaces
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.redact.canvas import off_page_words
from anonymizer.core.types import BBox, Document, Entity

# A word or drawing merely touching a region's edge is not inside it.
_EDGE_TOLERANCE = 1.0
_BLACK = (0.0, 0.0, 0.0)


class _Target(NamedTuple):
    """An entity's text the output must no longer contain."""

    entity_id: str
    text: str


class LeakLayer(StrEnum):
    """Where in the redacted file a leak was found."""

    PAGE_TEXT = "page_text"
    REGION = "region"
    OFF_PAGE_TEXT = "off_page_text"
    SURFACE = "surface"
    THUMBNAIL = "thumbnail"
    OBJECT = "object"
    FILE_BYTES = "file_bytes"


@dataclass(frozen=True, slots=True)
class Leak:
    """Personal data found in a redacted file.

    Attributes:
        layer: Which check found it.
        where: Location within the layer: a page number, a surface kind and
            reference, or an object number.
        text: The leaked string; for an uncleared surface its value, for a
            region or a thumbnail a description of what was found.
        entity_id: Entity whose content leaked, or `None` when the leak is not
            tied to an entity (an uncleared surface, off-page text, a thumbnail).
    """

    layer: LeakLayer
    where: str
    text: str
    entity_id: str | None = None


def find_leaks(redacted: Path | str, document: Document) -> list[Leak]:
    """Return every trace of redacted personal data in an output file.

    Args:
        redacted: Path of the redacted PDF.
        document: The document the redaction was made from; entities review
            rejected are not looked for.

    Returns:
        Leaks in layer order; an empty list means the file passed.
    """
    redactable = [entity for entity in document.entities if entity.is_redactable]
    targets = [
        _Target(entity.entity_id, entity.text) for entity in redactable if entity.text is not None
    ]
    regions = [entity for entity in redactable if entity.is_region]
    with pymupdf.open(redacted) as pdf:
        leaks = [
            *_page_text_leaks(pdf, targets),
            *_region_leaks(pdf, regions),
            *_off_page_leaks(pdf),
            *_surface_leaks(pdf),
            *_thumbnail_leaks(pdf),
            *_object_leaks(pdf, targets),
        ]
    return leaks + _file_byte_leaks(Path(redacted), targets)


def _compact(text: str) -> str:
    """Remove all whitespace, so line breaks and spacing do not hide a match."""
    return "".join(text.split())


def _page_text_leaks(pdf: pymupdf.Document, targets: list[_Target]) -> list[Leak]:
    """Find entity text in any page's extracted text."""
    leaks: list[Leak] = []
    for index in range(pdf.page_count):
        page_text = _compact(extract_page(pdf.load_page(index), index).text)
        leaks.extend(
            Leak(LeakLayer.PAGE_TEXT, f"page {index}", target.text, target.entity_id)
            for target in targets
            if _compact(target.text) in page_text
        )
    return leaks


def _region_leaks(pdf: pymupdf.Document, regions: list[Entity]) -> list[Leak]:
    """Report words and drawings left inside a region's box."""
    leaks: list[Leak] = []
    for region in regions:
        if region.page_index is None:
            continue
        page = pdf.load_page(region.page_index)
        (box,) = region.bboxes
        where = f"page {region.page_index} region"
        words = extract_page(page, region.page_index).words
        leaks.extend(
            Leak(LeakLayer.REGION, where, f"word {word.text!r}", region.entity_id)
            for word in words
            if _overlaps_inside(word.bbox, box)
        )
        inside = _shrunk(bbox_to_unrotated_rect(box, page))
        leaks.extend(
            Leak(LeakLayer.REGION, where, "drawing", region.entity_id)
            for drawing in page.get_drawings()
            if drawing["rect"].intersects(inside) and not _is_region_fill(drawing, inside)
        )
    return leaks


def _shrunk(rect: pymupdf.Rect) -> pymupdf.Rect:
    """Return the rectangle without a thin margin along its edges."""
    t = _EDGE_TOLERANCE
    return pymupdf.Rect(rect.x0 + t, rect.y0 + t, rect.x1 - t, rect.y1 - t)


def _overlaps_inside(word_box: BBox, region_box: BBox) -> bool:
    """Whether a word box reaches past the region's edge margin into it."""
    word = pymupdf.Rect(*word_box.to_list())
    return word.intersects(_shrunk(pymupdf.Rect(*region_box.to_list())))


def _is_region_fill(drawing: dict[str, Any], inside: pymupdf.Rect) -> bool:
    """Whether a drawing is the black fill redaction painted over the region."""
    return drawing.get("fill") == _BLACK and drawing["rect"].contains(inside)


def _off_page_leaks(pdf: pymupdf.Document) -> list[Leak]:
    """Report every word drawn outside a page's visible area."""
    return [
        Leak(LeakLayer.OFF_PAGE_TEXT, f"page {index}", word)
        for index in range(pdf.page_count)
        for word in off_page_words(pdf.load_page(index))
    ]


def _thumbnail_leaks(pdf: pymupdf.Document) -> list[Leak]:
    """Report every page that still carries a thumbnail."""
    return [
        Leak(LeakLayer.THUMBNAIL, f"page {index}", "page thumbnail")
        for index in range(pdf.page_count)
        if pdf.xref_get_key(pdf.load_page(index).xref, "Thumb")[0] != "null"
    ]


def _surface_leaks(pdf: pymupdf.Document) -> list[Leak]:
    """Report every surface still present."""
    return [
        Leak(LeakLayer.SURFACE, f"{surface.kind} {surface.ref}", surface.value)
        for surface in extract_surfaces(pdf)
    ]


def _object_leaks(pdf: pymupdf.Document, targets: list[_Target]) -> list[Leak]:
    """Find entity text stored literally in any object or stream."""
    leaks: list[Leak] = []
    for xref in range(1, pdf.xref_length()):
        content = _compact(_object_text(pdf, xref))
        leaks.extend(
            Leak(LeakLayer.OBJECT, f"object {xref}", target.text, target.entity_id)
            for target in targets
            if _compact(target.text) in content
        )
    return leaks


def _object_text(pdf: pymupdf.Document, xref: int) -> str:
    """Return an object's source and, for a stream, its decompressed data."""
    source = pdf.xref_object(xref)
    if not pdf.xref_is_stream(xref):
        return source
    return source + _latin1(pdf.xref_stream(xref) or b"")


def _file_byte_leaks(path: Path, targets: list[_Target]) -> list[Leak]:
    """Find entity text anywhere in the raw file, earlier revisions included."""
    content = _compact(_latin1(path.read_bytes()))
    return [
        Leak(LeakLayer.FILE_BYTES, path.name, target.text, target.entity_id)
        for target in targets
        if _compact(target.text) in content
    ]


def _latin1(data: bytes) -> str:
    """Decode bytes one character per byte, so any ASCII text is preserved."""
    return data.decode("latin-1")
