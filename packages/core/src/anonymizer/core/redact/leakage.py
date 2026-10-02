"""Checking a redacted PDF for personal data that survived.

Eight layers, because each misses something the others catch:

1. **Page text.** The output is extracted the way ingest extracts the input,
   and no redacted entity's text may remain on any page beyond the copies
   review kept there: the same text can be redacted in one place and kept in
   another, so occurrences are counted against the rejected entities.
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
   text are the first layers' job. A text that starts or ends with a digit
   must not continue into another digit or a decimal number there: a ZIP code
   `20001` also occurs inside the layout operand `9.200012`, which is syntax,
   not a leak. A text review kept on some page is not searched for: this
   layer cannot tell the kept copy from a redacted one, and a copy of a text
   the output shows anyway reveals nothing more.
7. **File bytes.** An incremental save appends new object revisions and leaves
   the old ones in the file, where the object table no longer points but any
   text editor still shows them. The raw bytes are searched as well, with the
   same literal-string limit and digit rule as layer 6.
8. **OCR.** A page OCR read keeps its content in pixels, which no layer above
   reads. Its text layer must be empty, and the engine that read it re-reads
   the redacted page at the same resolution: no redacted text may be found
   beyond the copies review kept, and no word may lie mostly (half its box or
   more) inside a redacted box or region: on a skewed scan an axis-aligned
   box clips the corners of neighbouring words, which are not leaks. This
   shows only that *this engine* can no longer read the
   value. It cannot prove the pixels are gone (that is verified by the test
   suite); it does not report a fragment beside a box that no longer spells
   the detected text, such as the end of an address a narrow box missed; and
   a value the engine misread when reading the original was neither
   detected nor can be found now, while a better reader or a person might
   still read it.

Whitespace is ignored when comparing text: a span that crossed a line break
may be extracted with different spacing.
"""

from __future__ import annotations

import logging
import re
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, NamedTuple

import pymupdf
from anonymizer.core.ingest import OcrEngine, extract_page, extract_surfaces, read_page
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.log import fields, step
from anonymizer.core.redact.canvas import off_page_words
from anonymizer.core.types import BBox, Document, Entity

log = logging.getLogger(__name__)

# A word or drawing merely touching a region's edge is not inside it.
_EDGE_TOLERANCE = 1.0
# A word re-read by OCR is under a redacted box when this share of it is.
_MOSTLY = 0.5
_BLACK = (0.0, 0.0, 0.0)


class _Target(NamedTuple):
    """An entity's text the output must no longer contain, and how it is stored literally."""

    entity_id: str
    text: str
    literal: re.Pattern[str]


class LeakLayer(StrEnum):
    """Where in the redacted file a leak was found."""

    PAGE_TEXT = "page_text"
    REGION = "region"
    OFF_PAGE_TEXT = "off_page_text"
    SURFACE = "surface"
    THUMBNAIL = "thumbnail"
    OBJECT = "object"
    FILE_BYTES = "file_bytes"
    OCR = "ocr"


_UNLOGGED_LOCATIONS = frozenset({LeakLayer.SURFACE, LeakLayer.FILE_BYTES})


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
        page_index: Zero-based page the leak lies on, or `None` when it lies
            in no page (a surface, an object, the file's bytes).
    """

    layer: LeakLayer
    where: str
    text: str
    entity_id: str | None = None
    page_index: int | None = None


def find_leaks(
    redacted: Path | str, document: Document, *, ocr: OcrEngine | None = None
) -> list[Leak]:
    """Return every trace of redacted personal data in an output file.

    Args:
        redacted: Path of the redacted PDF.
        document: The document the redaction was made from; entities review
            rejected are not looked for.
        ocr: The engine that read the document's scanned pages, to re-read
            them; required when OCR read any page.

    Returns:
        Leaks in layer order; an empty list means the file passed.

    Raises:
        ValueError: If OCR read a page of the document and no engine is given.
    """
    scanned = [page for page in document.pages if page.raster_dpi is not None]
    if scanned and ocr is None:
        msg = "OCR read pages of this document; pass its engine to re-read them"
        raise ValueError(msg)
    redactable = [entity for entity in document.entities if entity.is_redactable]
    targets = [
        _Target(entity.entity_id, entity.text, _literal_pattern(entity.text))
        for entity in redactable
        if entity.text is not None
    ]
    regions = [entity for entity in redactable if entity.is_region]
    kept = _kept_texts(document)
    all_kept = [text for texts in kept.values() for text in texts]
    never_kept = [target for target in targets if _copies(target.text, all_kept) == 0]
    with (
        step(log, "leak check", targets=len(targets), regions=len(regions)) as outcome,
        pymupdf.open(redacted) as pdf,
    ):
        leaks = [
            *_layer("page text", lambda: _page_text_leaks(pdf, targets, kept)),
            *_layer("region", lambda: _region_leaks(pdf, regions)),
            *_layer("off-page text", lambda: _off_page_leaks(pdf)),
            *_layer("hidden items", lambda: _surface_leaks(pdf)),
            *_layer("thumbnail", lambda: _thumbnail_leaks(pdf)),
            *_layer("object", lambda: _object_leaks(pdf, never_kept)),
        ]
        file_bytes = _layer("file bytes", lambda: _file_byte_leaks(Path(redacted), never_kept))
        reread = (
            _layer("OCR re-read", lambda: _ocr_leaks(pdf, document, targets, kept, ocr))
            if ocr is not None
            else []
        )
        outcome["leaks"] = len(leaks) + len(file_bytes) + len(reread)
    return leaks + file_bytes + reread


def _layer(name: str, check: Callable[[], list[Leak]]) -> list[Leak]:
    """Run one layer of the check and log what it found, in one record."""
    started = time.perf_counter()
    leaks = check()
    log.debug(
        "leak check layer %s: %d leak(s) in %.2fs", name, len(leaks), time.perf_counter() - started
    )
    for leak in leaks:
        # A leak is as sensitive as the text it quotes, so it is a DEBUG record.
        # Where a leak lies is left out when it is a file name or a surface's
        # locator (a link target, an attachment's name): a log holds no names.
        where = "-" if leak.layer in _UNLOGGED_LOCATIONS else leak.where
        log.debug("leak in %s:%s", name, fields(where=where, entity=leak.entity_id, text=leak.text))
    return leaks


def _compact(text: str) -> str:
    """Remove all whitespace, so line breaks and spacing do not hide a match."""
    return "".join(text.split())


def _kept_texts(document: Document) -> dict[int, list[str]]:
    """Return the page texts review rejected, compacted, by page."""
    kept: dict[int, list[str]] = defaultdict(list)
    for entity in document.entities:
        if not entity.is_redactable and entity.in_page_text and entity.page_index is not None:
            kept[entity.page_index].append(_compact(entity.text or ""))
    return kept


def _copies(text: str, compacted: list[str]) -> int:
    """Count the occurrences of a text in already compacted texts."""
    needle = _compact(text)
    return sum(haystack.count(needle) for haystack in compacted)


def _page_text_leaks(
    pdf: pymupdf.Document, targets: list[_Target], kept: dict[int, list[str]]
) -> list[Leak]:
    """Find entity text in any page's extracted text, beyond the copies review kept."""
    leaks: list[Leak] = []
    for index in range(pdf.page_count):
        page_text = _compact(extract_page(pdf.load_page(index), index).text)
        leaks.extend(
            Leak(LeakLayer.PAGE_TEXT, f"page {index}", target.text, target.entity_id, index)
            for target in targets
            if _copies(target.text, [page_text]) > _copies(target.text, kept.get(index, []))
        )
    return leaks


def _region_leaks(pdf: pymupdf.Document, regions: list[Entity]) -> list[Leak]:
    """Report words and drawings left inside a region's box."""
    boxes: dict[int, list[BBox]] = defaultdict(list)
    for region in regions:
        if region.page_index is not None:
            boxes[region.page_index].extend(region.bboxes)
    leaks: list[Leak] = []
    for region in regions:
        if region.page_index is None:
            continue
        page = pdf.load_page(region.page_index)
        (box,) = region.bboxes
        where = f"page {region.page_index} region"
        words = extract_page(page, region.page_index).words
        leaks.extend(
            Leak(
                LeakLayer.REGION, where, f"word {word.text!r}", region.entity_id, region.page_index
            )
            for word in words
            if _overlaps_inside(word.bbox, box)
        )
        inside = _shrunk(bbox_to_unrotated_rect(box, page))
        # Overlapping regions each paint their own fill, which reaches into the other.
        fills = [bbox_to_unrotated_rect(other, page) for other in boxes[region.page_index]]
        leaks.extend(
            Leak(LeakLayer.REGION, where, "drawing", region.entity_id, region.page_index)
            for drawing in page.get_drawings()
            if drawing["rect"].intersects(inside) and not _is_region_fill(drawing, fills)
        )
    return leaks


def _shrunk(rect: pymupdf.Rect) -> pymupdf.Rect:
    """Return the rectangle without a thin margin along its edges."""
    t = _EDGE_TOLERANCE
    return pymupdf.Rect(rect.x0 + t, rect.y0 + t, rect.x1 - t, rect.y1 - t)


def _grown(rect: pymupdf.Rect) -> pymupdf.Rect:
    """Return the rectangle with a thin margin added along its edges."""
    t = _EDGE_TOLERANCE
    return pymupdf.Rect(rect.x0 - t, rect.y0 - t, rect.x1 + t, rect.y1 + t)


def _overlaps_inside(word_box: BBox, region_box: BBox) -> bool:
    """Whether a word box reaches past the region's edge margin into it."""
    word = pymupdf.Rect(*word_box.to_list())
    return word.intersects(_shrunk(pymupdf.Rect(*region_box.to_list())))


def _is_region_fill(drawing: dict[str, Any], fills: list[pymupdf.Rect]) -> bool:
    """Whether a drawing is the black fill redaction painted over one of the page's regions."""
    if drawing.get("fill") != _BLACK:
        return False
    rect = drawing["rect"]
    return any(rect.contains(_shrunk(fill)) and _grown(fill).contains(rect) for fill in fills)


def _off_page_leaks(pdf: pymupdf.Document) -> list[Leak]:
    """Report every word drawn outside a page's visible area."""
    return [
        Leak(LeakLayer.OFF_PAGE_TEXT, f"page {index}", word, page_index=index)
        for index in range(pdf.page_count)
        for word in off_page_words(pdf.load_page(index))
    ]


def _thumbnail_leaks(pdf: pymupdf.Document) -> list[Leak]:
    """Report every page that still carries a thumbnail."""
    return [
        Leak(LeakLayer.THUMBNAIL, f"page {index}", "page thumbnail", page_index=index)
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
        content = _object_text(pdf, xref)
        leaks.extend(
            Leak(LeakLayer.OBJECT, f"object {xref}", target.text, target.entity_id)
            for target in targets
            if target.literal.search(content)
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
    content = _latin1(path.read_bytes())
    return [
        Leak(LeakLayer.FILE_BYTES, path.name, target.text, target.entity_id)
        for target in targets
        if target.literal.search(content)
    ]


def _ocr_leaks(
    pdf: pymupdf.Document,
    document: Document,
    targets: list[_Target],
    kept: dict[int, list[str]],
    engine: OcrEngine,
) -> list[Leak]:
    """Find text left on pages OCR read: in the text layer, or in the pixels when re-read."""
    boxes = _redacted_boxes(document)
    leaks: list[Leak] = []
    for page in document.pages:
        if page.raster_dpi is None:
            continue
        pdf_page = pdf.load_page(page.index)
        where = f"page {page.index}"
        leaks.extend(
            Leak(LeakLayer.OCR, where, f"text layer word {word.text!r}", page_index=page.index)
            for word in extract_page(pdf_page, page.index).words
        )
        reread = read_page(pdf_page, page.index, engine, int(page.raster_dpi))
        reread_text = _compact(reread.text)
        leaks.extend(
            Leak(LeakLayer.OCR, where, target.text, target.entity_id, page.index)
            for target in targets
            if _copies(target.text, [reread_text]) > _copies(target.text, kept.get(page.index, []))
        )
        leaks.extend(
            Leak(
                LeakLayer.OCR, f"{where} under a box", f"word {word.text!r}", entity_id, page.index
            )
            for entity_id, box in boxes.get(page.index, [])
            for word in reread.words
            if _mostly_inside(word.bbox, box)
        )
    return leaks


def _mostly_inside(word_box: BBox, box: BBox) -> bool:
    """Whether at least half of a word's box lies inside another box."""
    word = pymupdf.Rect(*word_box.to_list())
    shared = word & pymupdf.Rect(*box.to_list())
    return not shared.is_empty and shared.get_area() >= _MOSTLY * word.get_area()


def _redacted_boxes(document: Document) -> dict[int, list[tuple[str, BBox]]]:
    """Return every box redaction blacked out, with its entity, by page."""
    boxes: dict[int, list[tuple[str, BBox]]] = defaultdict(list)
    for entity in document.entities:
        if entity.page_index is None or not entity.is_redactable:
            continue
        if entity.is_region or entity.in_page_text:
            boxes[entity.page_index].extend((entity.entity_id, box) for box in entity.bboxes)
    return boxes


def _literal_pattern(text: str) -> re.Pattern[str]:
    """Match a text stored literally, with any whitespace between its characters.

    A text starting or ending with a digit must not continue into another
    digit or a decimal number: PDF syntax is full of numbers, and `20001`
    inside `9.200012` is a glyph offset, not a ZIP code. Whitespace still
    counts as a boundary, so `(20001 12)` matches.
    """
    compact = _compact(text)
    body = r"\s*".join(re.escape(character) for character in compact)
    before = r"(?<!\d)(?<!\d\.)" if compact[:1].isdigit() else ""
    after = r"(?!\d)(?!\.\d)" if compact[-1:].isdigit() else ""
    return re.compile(before + body + after)


def _latin1(data: bytes) -> str:
    """Decode bytes one character per byte, so any ASCII text is preserved."""
    return data.decode("latin-1")
