"""Checking a redacted PDF for personal data that survived.

Eight layers, because each misses something the others catch:

1. **Page text.** The output is extracted the way ingest extracts the input,
   and no redacted entity's text may remain on any page beyond the copies
   review kept there: the same text can be redacted in one place and kept in
   another, so occurrences are counted against the rejected entities. An
   occurrence starts where a word starts and may run on into a longer word,
   so an inflected form of a detected name ("Nováka" for "Novák") counts,
   while "25" inside "1925" does not. A single character identifies no one
   and is not searched for.
2. **Regions.** A region has no text to search for, so nothing may remain
   inside its box: no word and no drawing apart from the black fill itself.
   Image pixels under a box are not re-read here; their removal is verified by
   the test suite instead.
3. **Off-page text.** Any word drawn outside a page's visible area is a leak:
   redaction removes that area whole, and ingest never extracted it.
4. **Surfaces.** The surface scan is re-run; redaction clears every surface, so
   any surface left is a leak, whether or not an entity was found in it.
   No file may remain embedded either: an attachment's contents are never
   scanned, so a file specification that still embeds a file, or an
   embedded-file stream with any content, is a leak even when it has no label
   to list.
5. **Thumbnails.** A page thumbnail is a picture of the page before redaction.
6. **Objects.** Every object and decompressed stream in the file is searched
   for each entity's text. This catches carriers the surface scan does not list
   (JavaScript, named destinations, an overlooked dictionary). It only sees
   strings stored literally; hex or UTF-16 encoded strings and font-encoded page
   text are the first layers' job. A text that starts or ends with a digit
   must not continue into another digit or a decimal number there: a ZIP code
   `20001` also occurs inside the layout operand `9.200012`, which is syntax,
   not a leak. Image and font streams are not searched, and neither is a
   text shorter than four characters: pixels, glyph outlines and compressed
   data contain any short byte sequence by chance. A text review kept on
   some page is not searched for: this layer cannot tell the kept copy from a
   redacted one, and a copy of a text the output shows anyway reveals nothing
   more.
7. **File bytes.** An incremental save appends new object revisions and leaves
   the old ones in the file, where the object table no longer points but any
   text editor still shows them. The raw bytes are searched as well, with the
   same literal-string limit, digit rule and shortest text as layer 6.
8. **OCR.** A page OCR read keeps its content in pixels, which no layer above
   reads. Its text layer must be empty, and the engine that read it re-reads
   the redacted page at the same resolution: no redacted text may be found
   beyond the copies review kept (counted as in layer 1), and no word may lie
   mostly (half its box or more) inside a redacted box or region: on a skewed
   scan an axis-aligned
   box clips the corners of neighbouring words, which are not leaks. This
   shows only that *this engine* can no longer read the
   value. It cannot prove the pixels are gone (that is verified by the test
   suite); it does not report a fragment beside a box that no longer spells
   the detected text, such as the end of an address a narrow box missed; and
   a value the engine misread when reading the original was neither
   detected nor can be found now, while a better reader or a person might
   still read it.

Whitespace is ignored when comparing text: a span that crossed a line break
may be extracted with different spacing. Entities sharing a text (a name and
its repeats) are searched for once, so each place it is left is one leak.
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
from anonymizer.core.ingest.objects import dictionaries_with_key, embedded_file_streams
from anonymizer.core.log import fields, step
from anonymizer.core.redact.canvas import off_page_words
from anonymizer.core.types import BBox, Document, Entity, Page, StepProgress

log = logging.getLogger(__name__)

# A word or drawing merely touching a region's edge is not inside it.
_EDGE_TOLERANCE = 1.0
# A word re-read by OCR is under a redacted box when this share of it is.
_MOSTLY = 0.5
_BLACK = (0.0, 0.0, 0.0)
# Shortest texts, without whitespace, searched for in a page's words and in the file's data.
_SHORTEST_WORDS = 2
_SHORTEST_LITERAL = 4
# Streams of pixels and glyph outlines, where any short byte sequence turns up by chance.
_BINARY_SUBTYPES = frozenset({"/Image", "/Type1C", "/CIDFontType0C", "/OpenType"})
_FONT_PROGRAM_KEYS = ("Length1", "Length2", "Length3")


class _Target(NamedTuple):
    """An entity's text the output must no longer contain, as read on a page and as stored."""

    entity_id: str
    text: str
    word: re.Pattern[str]
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
_LAYER_NAMES = {
    LeakLayer.PAGE_TEXT: "page text",
    LeakLayer.REGION: "region",
    LeakLayer.OFF_PAGE_TEXT: "off-page text",
    LeakLayer.SURFACE: "hidden items",
    LeakLayer.THUMBNAIL: "thumbnail",
    LeakLayer.OBJECT: "object",
    LeakLayer.FILE_BYTES: "file bytes",
    LeakLayer.OCR: "OCR re-read",
}


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
    redacted: Path | str,
    document: Document,
    *,
    ocr: OcrEngine | None = None,
    progress: StepProgress | None = None,
) -> list[Leak]:
    """Return every trace of redacted personal data in an output file.

    Args:
        redacted: Path of the redacted PDF.
        document: The document the redaction was made from; entities review
            rejected are not looked for.
        ocr: The engine that read the document's scanned pages, to re-read
            them; required when OCR read any page.
        progress: Told each layer as it starts, by its `LeakLayer` value; the
            OCR layer then counts the pages it re-reads.

    Returns:
        Leaks in layer order; an empty list means the file passed.

    Raises:
        ValueError: If OCR read a page of the document and no engine is given.
    """
    scanned = [page for page in document.pages if page.raster_dpi is not None]
    if scanned and ocr is None:
        msg = "OCR read pages of this document; pass its engine to re-read them"
        raise ValueError(msg)
    report = progress or (lambda _step, _done, _total: None)
    redactable = [entity for entity in document.entities if entity.is_redactable]
    targets = _targets(redactable)
    regions = [entity for entity in redactable if entity.is_region]
    kept = _kept_texts(document)
    all_kept = [text for texts in kept.values() for text in texts]
    in_words = [target for target in targets if _length(target.text) >= _SHORTEST_WORDS]
    literal = [
        target
        for target in targets
        if _length(target.text) >= _SHORTEST_LITERAL and _copies(target.word, all_kept) == 0
    ]
    checks: list[tuple[LeakLayer, int, Callable[[], list[Leak]]]] = [
        (LeakLayer.PAGE_TEXT, 0, lambda: _page_text_leaks(pdf, in_words, kept)),
        (LeakLayer.REGION, 0, lambda: _region_leaks(pdf, regions)),
        (LeakLayer.OFF_PAGE_TEXT, 0, lambda: _off_page_leaks(pdf)),
        (LeakLayer.SURFACE, 0, lambda: _surface_leaks(pdf)),
        (LeakLayer.THUMBNAIL, 0, lambda: _thumbnail_leaks(pdf)),
        (LeakLayer.OBJECT, 0, lambda: _object_leaks(pdf, literal)),
        (LeakLayer.FILE_BYTES, 0, lambda: _file_byte_leaks(Path(redacted), literal)),
    ]
    if ocr is not None:
        checks.append(
            (
                LeakLayer.OCR,
                len(scanned),
                lambda: _ocr_leaks(pdf, document, in_words, kept, ocr, report),
            )
        )
    with (
        step(log, "leak check", targets=len(targets), regions=len(regions)) as outcome,
        pymupdf.open(redacted) as pdf,
    ):
        leaks: list[Leak] = []
        for layer, pages, check in checks:
            report(layer.value, 0, pages)
            leaks.extend(_layer(layer, check))
        outcome["leaks"] = len(leaks)
    return leaks


def _targets(redactable: list[Entity]) -> list[_Target]:
    """Return the texts to search for, each once however many entities share it."""
    targets: dict[str, _Target] = {}
    for entity in redactable:
        if entity.text is None or not _compact(entity.text):
            continue
        targets.setdefault(
            _compact(entity.text),
            _Target(
                entity.entity_id,
                entity.text,
                _word_pattern(entity.text),
                _literal_pattern(entity.text),
            ),
        )
    return list(targets.values())


def _layer(layer: LeakLayer, check: Callable[[], list[Leak]]) -> list[Leak]:
    """Run one layer of the check and log what it found, in one record."""
    name = _LAYER_NAMES[layer]
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


def _length(text: str) -> int:
    """Count a text's characters, whitespace left out."""
    return len(_compact(text))


def _kept_texts(document: Document) -> dict[int, list[str]]:
    """Return the page texts review rejected, by page."""
    kept: dict[int, list[str]] = defaultdict(list)
    for entity in document.entities:
        if not entity.is_redactable and entity.in_page_text and entity.page_index is not None:
            kept[entity.page_index].append(entity.text or "")
    return kept


def _copies(pattern: re.Pattern[str], texts: list[str]) -> int:
    """Count a text's occurrences in other texts."""
    return sum(len(pattern.findall(text)) for text in texts)


def _page_text_leaks(
    pdf: pymupdf.Document, targets: list[_Target], kept: dict[int, list[str]]
) -> list[Leak]:
    """Find entity text in any page's extracted text, beyond the copies review kept."""
    leaks: list[Leak] = []
    for index in range(pdf.page_count):
        page_text = extract_page(pdf.load_page(index), index).text
        leaks.extend(
            Leak(LeakLayer.PAGE_TEXT, f"page {index}", target.text, target.entity_id, index)
            for target in targets
            if _copies(target.word, [page_text]) > _copies(target.word, kept.get(index, []))
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
    """Report every surface still present and every file still embedded."""
    return [
        *(
            Leak(LeakLayer.SURFACE, f"{surface.kind} {surface.ref}", surface.value)
            for surface in extract_surfaces(pdf)
        ),
        *(
            Leak(LeakLayer.SURFACE, f"object {xref}", "file specification embedding a file")
            for xref, _file_spec in dictionaries_with_key(pdf, "EF")
        ),
        *(
            Leak(LeakLayer.SURFACE, f"object {xref}", "embedded file")
            for xref in embedded_file_streams(pdf)
            if pdf.xref_stream(xref)
        ),
    ]


def _object_leaks(pdf: pymupdf.Document, targets: list[_Target]) -> list[Leak]:
    """Find entity text stored literally in any object or stream."""
    leaks: list[Leak] = []
    if not targets:
        return leaks
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
    if not pdf.xref_is_stream(xref) or _is_binary_stream(pdf, xref):
        return source
    return source + _latin1(pdf.xref_stream(xref) or b"")


def _is_binary_stream(pdf: pymupdf.Document, xref: int) -> bool:
    """Whether a stream holds an image's pixels or a font program."""
    _kind, subtype = pdf.xref_get_key(xref, "Subtype")
    if subtype in _BINARY_SUBTYPES:
        return True
    return any(pdf.xref_get_key(xref, key)[0] != "null" for key in _FONT_PROGRAM_KEYS)


def _file_byte_leaks(path: Path, targets: list[_Target]) -> list[Leak]:
    """Find entity text anywhere in the raw file, earlier revisions included."""
    if not targets:
        return []
    content = _latin1(path.read_bytes())
    # Not the file's name: the copy is checked under a temporary one.
    return [
        Leak(LeakLayer.FILE_BYTES, "the file's bytes", target.text, target.entity_id)
        for target in targets
        if target.literal.search(content)
    ]


def _ocr_leaks(
    pdf: pymupdf.Document,
    document: Document,
    targets: list[_Target],
    kept: dict[int, list[str]],
    engine: OcrEngine,
    progress: StepProgress,
) -> list[Leak]:
    """Find text left on pages OCR read: in the text layer, or in the pixels when re-read."""
    boxes = _redacted_boxes(document)
    scanned = [page for page in document.pages if page.raster_dpi is not None]
    leaks: list[Leak] = []
    for done, page in enumerate(scanned, start=1):
        leaks.extend(_scanned_page_leaks(pdf, page, targets, kept, engine, boxes))
        progress(LeakLayer.OCR.value, done, len(scanned))
    return leaks


def _scanned_page_leaks(
    pdf: pymupdf.Document,
    page: Page,
    targets: list[_Target],
    kept: dict[int, list[str]],
    engine: OcrEngine,
    boxes: dict[int, list[tuple[str, BBox]]],
) -> list[Leak]:
    """Find text left on one page OCR read."""
    pdf_page = pdf.load_page(page.index)
    where = f"page {page.index}"
    leaks = [
        Leak(LeakLayer.OCR, where, f"text layer word {word.text!r}", page_index=page.index)
        for word in extract_page(pdf_page, page.index).words
    ]
    reread = read_page(pdf_page, page.index, engine, int(page.raster_dpi or 0))
    leaks.extend(
        Leak(LeakLayer.OCR, where, target.text, target.entity_id, page.index)
        for target in targets
        if _copies(target.word, [reread.text]) > _copies(target.word, kept.get(page.index, []))
    )
    for word in reread.words:
        # A word under several overlapping boxes is one leak.
        under = next(
            (
                entity_id
                for entity_id, box in boxes.get(page.index, [])
                if _mostly_inside(word.bbox, box)
            ),
            None,
        )
        if under is not None:
            leaks.append(
                Leak(
                    LeakLayer.OCR, f"{where} under a box", f"word {word.text!r}", under, page.index
                )
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


def _word_pattern(text: str) -> re.Pattern[str]:
    """Match a text in extracted text where a word starts, with any whitespace inside it.

    The match may run on into a longer word, as Czech inflects by its endings,
    but a text ending in a digit must not continue into another number.
    """
    compact = _compact(text)
    body = r"\s*".join(re.escape(character) for character in compact)
    before = r"(?<!\w)" if re.match(r"\w", compact) else ""
    after = r"(?!\d)(?!\.\d)" if compact[-1:].isdigit() else ""
    return re.compile(before + body + after)


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
