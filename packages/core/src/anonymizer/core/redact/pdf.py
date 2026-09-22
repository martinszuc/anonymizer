"""Blackbox redaction of a born-digital PDF.

Page-text entities are removed with PyMuPDF redaction annotations, which delete
the characters under each box instead of drawing over them. Every non-text
surface is then cleared (see `redact.surfaces`), and the file is written in
full: an incremental save would keep every earlier revision of each object.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pymupdf
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.redact.surfaces import clear_surfaces
from anonymizer.core.types import BBox, Document

_BLACK = (0.0, 0.0, 0.0)


def redact_pdf(source: Path | str, document: Document, destination: Path | str) -> None:
    """Write a redacted copy of a PDF.

    Every page-text entity review did not reject is blacked out and its text
    removed from the file. Every non-text surface is cleared regardless of
    detection. The source file is not modified.

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
    boxes_by_page = _page_text_boxes(document)
    with pymupdf.open(source) as pdf:
        if pdf.page_count != len(document.pages):
            msg = f"document has {len(document.pages)} pages, the file {pdf.page_count}"
            raise ValueError(msg)
        for index in range(pdf.page_count):
            _black_out(pdf.load_page(index), boxes_by_page.get(index, []))
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
        entity_boxes = entity.bboxes or page.bboxes_for_span(entity.start, entity.end)
        if not entity_boxes:
            msg = f"entity {entity.entity_id} has no geometry to redact"
            raise ValueError(msg)
        boxes[entity.page_index].append(entity_boxes)
    return boxes


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
