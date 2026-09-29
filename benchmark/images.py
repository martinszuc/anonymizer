"""Pictures for presentations: original, detections, redacted, and a collage.

All three views of a page share one clip (the text area plus a margin), so
they line up side by side. Everything is drawn with PyMuPDF; no image library
is needed.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf
from anonymizer.core.types import Entity, EntityType

DPI = 110
CLIP_MARGIN = 18.0
GAP = 24
HEADER = 52

# Colour per type for the detection view (RGB, 0-1).
TYPE_COLOURS: dict[EntityType, tuple[float, float, float]] = {
    EntityType.PERSON: (0.85, 0.20, 0.20),
    EntityType.ADDRESS: (0.95, 0.55, 0.10),
    EntityType.EMAIL: (0.15, 0.45, 0.85),
    EntityType.PHONE: (0.10, 0.60, 0.55),
    EntityType.URL: (0.45, 0.30, 0.80),
    EntityType.BIRTH_NUMBER: (0.75, 0.10, 0.55),
    EntityType.BANK_ACCOUNT: (0.30, 0.55, 0.15),
    EntityType.IBAN: (0.30, 0.55, 0.15),
    EntityType.COMPANY_ID: (0.55, 0.45, 0.20),
}
_OTHER_COLOUR = (0.40, 0.40, 0.40)


def content_clip(pdf_path: Path, page_index: int = 0) -> pymupdf.Rect:
    """Return the page's text area plus a margin."""
    with pymupdf.open(pdf_path) as pdf:
        page = pdf.load_page(page_index)
        area = pymupdf.Rect()
        for block in page.get_text("blocks"):
            area |= pymupdf.Rect(block[:4])
        if area.is_empty:
            return page.rect
        grown = pymupdf.Rect(
            area.x0 - CLIP_MARGIN,
            area.y0 - CLIP_MARGIN,
            area.x1 + CLIP_MARGIN,
            area.y1 + CLIP_MARGIN,
        )
        return grown & page.rect


def page_image(pdf_path: Path, clip: pymupdf.Rect, destination: Path, page_index: int = 0) -> Path:
    """Render a page region to PNG."""
    with pymupdf.open(pdf_path) as pdf:
        pdf.load_page(page_index).get_pixmap(dpi=DPI, clip=clip).save(destination)
    return destination


def detection_image(
    pdf_path: Path,
    entities: list[Entity],
    clip: pymupdf.Rect,
    destination: Path,
    page_index: int = 0,
) -> Path:
    """Render a page with a translucent box per detected word, coloured by type."""
    with pymupdf.open(pdf_path) as pdf:
        page = pdf.load_page(page_index)
        for entity in entities:
            if entity.page_index != page_index or entity.surface_id is not None:
                continue
            colour = TYPE_COLOURS.get(entity.type, _OTHER_COLOUR)
            for box in entity.bboxes:
                rect = pymupdf.Rect(box.x0 - 1, box.y0 - 1, box.x1 + 1, box.y1 + 1)
                page.draw_rect(rect, color=colour, fill=colour, fill_opacity=0.25, width=1.2)
        page.get_pixmap(dpi=DPI, clip=clip).save(destination)
    return destination


def collage(panels: list[tuple[str, Path]], destination: Path) -> Path:
    """Place PNG panels side by side, each under a caption."""
    sizes = []
    for _, path in panels:
        pixmap = pymupdf.Pixmap(str(path))
        sizes.append((pixmap.width, pixmap.height))
    width = sum(size[0] for size in sizes) + GAP * (len(panels) + 1)
    height = max(size[1] for size in sizes) + HEADER + GAP
    canvas = pymupdf.open()
    page = canvas.new_page(width=width, height=height)
    page.draw_rect(page.rect, color=None, fill=(1, 1, 1))
    x = GAP
    for (caption, path), (panel_width, panel_height) in zip(panels, sizes, strict=True):
        page.insert_text((x, HEADER - 16), caption, fontsize=24, fontname="helv")
        box = pymupdf.Rect(x, HEADER, x + panel_width, HEADER + panel_height)
        page.insert_image(box, filename=str(path))
        page.draw_rect(box, color=(0.8, 0.8, 0.8), width=0.8)
        x += panel_width + GAP
    page.get_pixmap(dpi=72).save(destination)
    canvas.close()
    return destination
