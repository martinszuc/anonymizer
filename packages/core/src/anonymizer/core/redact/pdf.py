"""Blackbox redaction of a born-digital PDF.

Page-text entities and drawn regions are removed with PyMuPDF redaction
annotations, which delete what lies under each box instead of drawing over it.
A region also removes every vector drawing it touches: with PyMuPDF's normal
setting a drawing fully under the box, such as a signature, stays in the file.
Text boxes keep the normal setting, because the strict one would delete
backgrounds and table lines behind the words. Everything drawn
outside a page's visible area is removed next (see `redact.canvas`), then every
non-text surface is cleared (see `redact.surfaces`). The file is written in
full: an incremental save would keep every earlier revision of each object.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pymupdf
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.redact.canvas import remove_off_page_content
from anonymizer.core.redact.surfaces import clear_surfaces
from anonymizer.core.types import BBox, Document
from pymupdf import mupdf

_BLACK = (0.0, 0.0, 0.0)
_REMOVE_TOUCHED_DRAWINGS = mupdf.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED


def redact_pdf(source: Path | str, document: Document, destination: Path | str) -> None:
    """Write a redacted copy of a PDF.

    Every page-text entity and region review did not reject is blacked out
    and what lies under it removed from the file. Content outside each page's visible area and every
    non-text surface are removed regardless of detection. The source file is
    not modified.

    Args:
        source: PDF the document was loaded from.
        document: The loaded document with its reviewed entities.
        destination: Path of the redacted copy; must differ from `source`.

    Raises:
        ValueError: If `destination` is `source`, the document's page count does
            not match the file, or a redactable entity has no geometry.
    """
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        msg = "the redacted copy must not overwrite its source"
        raise ValueError(msg)
    text_boxes = _page_text_boxes(document)
    region_boxes = _region_boxes(document)
    with pymupdf.open(source) as pdf:
        if pdf.page_count != len(document.pages):
            msg = f"document has {len(document.pages)} pages, the file {pdf.page_count}"
            raise ValueError(msg)
        for index in range(pdf.page_count):
            page = pdf.load_page(index)
            _black_out(page, text_boxes.get(index, []))
            _black_out_regions(page, region_boxes.get(index, []))
            remove_off_page_content(page)
        clear_surfaces(pdf)
        pdf.save(destination, garbage=4, deflate=True)


def _page_text_boxes(document: Document) -> dict[int, list[list[BBox]]]:
    """Collect each redactable entity's boxes, grouped by page.

    Surface entities are skipped: their carriers are cleared as a whole, and
    a link's box covers visible words that are not themselves personal data.
    """
    boxes: dict[int, list[list[BBox]]] = defaultdict(list)
    for entity in document.entities:
        if not entity.is_redactable or not entity.in_page_text or entity.page_index is None:
            continue
        page = document.page(entity.page_index)
        entity_boxes = entity.bboxes or page.bboxes_for_span(*entity.span)
        if not entity_boxes:
            msg = f"entity {entity.entity_id} has no geometry to redact"
            raise ValueError(msg)
        boxes[entity.page_index].append(entity_boxes)
    return boxes


def _region_boxes(document: Document) -> dict[int, list[BBox]]:
    """Collect each redactable region's box, grouped by page."""
    boxes: dict[int, list[BBox]] = defaultdict(list)
    for entity in document.entities:
        if entity.is_region and entity.is_redactable and entity.page_index is not None:
            boxes[entity.page_index].extend(entity.bboxes)
    return boxes


def _black_out_regions(page: pymupdf.Page, boxes: list[BBox]) -> None:
    """Remove everything under each region and every drawing it touches."""
    if not boxes:
        return
    for box in boxes:
        page.add_redact_annot(bbox_to_unrotated_rect(box, page), fill=_BLACK)
    page.apply_redactions(graphics=_REMOVE_TOUCHED_DRAWINGS)


def _black_out(page: pymupdf.Page, boxes_per_entity: list[list[BBox]]) -> None:
    """Remove the content under each entity's boxes and fill them black."""
    if not boxes_per_entity:
        return
    for boxes in boxes_per_entity:
        rects = [bbox_to_unrotated_rect(box, page) for box in boxes]
        for rect in _merge_lines(rects):
            page.add_redact_annot(rect, fill=_BLACK)
    page.apply_redactions()


def _merge_lines(rects: list[pymupdf.Rect]) -> list[pymupdf.Rect]:
    """Merge one entity's word rectangles that share a line.

    Separate boxes with gaps show how a value was grouped, e.g. that a phone
    number was written as four blocks of digits. Rectangles are compared in the
    page's unrotated space, where text lines run horizontally; boxes on
    different lines stay apart so the space between the lines is kept.
    """
    merged: list[pymupdf.Rect] = []
    for rect in rects:
        if merged and _same_line(merged[-1], rect):
            merged[-1] = merged[-1] | rect
        else:
            merged.append(rect)
    return merged


def _same_line(first: pymupdf.Rect, second: pymupdf.Rect) -> bool:
    """Whether two rectangles overlap vertically by at least half the lower one."""
    overlap = min(first.y1, second.y1) - max(first.y0, second.y0)
    return overlap >= min(first.height, second.height) / 2
