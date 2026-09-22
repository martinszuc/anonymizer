"""Content drawn outside a page's visible area.

A PDF shows only what lies inside the page's crop box, but its content stream
may place text and images anywhere: outside the crop box, or beyond the media box
altogether. PyMuPDF extracts nothing from there, so detection never sees it,
yet any other tool reads it from the file. The whole area outside the visible
part is therefore removed, whatever it holds.

To reach that content, the page is temporarily enlarged to a large canvas with
rotation switched off; afterwards the page's own box and rotation entries are
written back exactly as they were, inherited values included.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import pymupdf

# Page dictionary entries the enlargement touches, restored verbatim afterwards.
_PAGE_GEOMETRY_KEYS = ("MediaBox", "CropBox", "BleedBox", "TrimBox", "ArtBox", "Rotate")

# Large enough for any content a real producer places off the page.
_CANVAS = pymupdf.Rect(-20000, -20000, 20000, 20000)


@contextmanager
def full_canvas(page: pymupdf.Page) -> Iterator[pymupdf.Rect]:
    """Temporarily expose everything drawn on a page.

    Inside the block the page is unrotated and as large as `_CANVAS`, so
    extraction and redaction reach content outside the visible area.

    Args:
        page: Page to expose.

    Yields:
        The originally visible area, in the enlarged page's coordinates.

    Raises:
        ValueError: If the page no longer belongs to an open document.
    """
    pdf = page.parent
    if pdf is None:
        msg = "page is detached from its document; load it again"
        raise ValueError(msg)
    saved = {key: pdf.xref_get_key(page.xref, key) for key in _PAGE_GEOMETRY_KEYS}
    visible = _visible_area_in_pdf_space(page)
    page.set_rotation(0)
    page.set_mediabox(_CANVAS)
    try:
        # Page coordinates run from the canvas's top-left corner, y downward.
        yield pymupdf.Rect(
            visible.x0 - _CANVAS.x0,
            _CANVAS.y1 - visible.y1,
            visible.x1 - _CANVAS.x0,
            _CANVAS.y1 - visible.y0,
        )
    finally:
        for key, (value_type, value) in saved.items():
            pdf.xref_set_key(page.xref, key, "null" if value_type == "null" else value)


def _visible_area_in_pdf_space(page: pymupdf.Page) -> pymupdf.Rect:
    """Return the crop box in PDF coordinates (origin bottom-left, y upward).

    PyMuPDF reports the crop box measured from the top of the media box; the
    media box itself is reported in PDF coordinates.
    """
    media, crop = page.mediabox, page.cropbox
    return pymupdf.Rect(crop.x0, media.y1 - crop.y1, crop.x1, media.y1 - crop.y0)


def _surrounding_bands(visible: pymupdf.Rect, canvas: pymupdf.Rect) -> list[pymupdf.Rect]:
    """Four rectangles that together cover the canvas outside `visible`."""
    return [
        pymupdf.Rect(canvas.x0, canvas.y0, canvas.x1, visible.y0),
        pymupdf.Rect(canvas.x0, visible.y1, canvas.x1, canvas.y1),
        pymupdf.Rect(canvas.x0, visible.y0, visible.x0, visible.y1),
        pymupdf.Rect(visible.x1, visible.y0, canvas.x1, visible.y1),
    ]


def remove_off_page_content(page: pymupdf.Page) -> None:
    """Remove text, image pixels and drawings lying outside the visible area.

    Drawings that reach into the visible area are kept whole, so a background
    that bleeds past the crop box for printing does not disappear.

    Args:
        page: Page to clean, in place.
    """
    with full_canvas(page) as visible:
        for band in _surrounding_bands(visible, page.rect):
            if not band.is_empty:
                page.add_redact_annot(band)
        page.apply_redactions()


def off_page_words(page: pymupdf.Page) -> list[str]:
    """Return the words drawn outside a page's visible area.

    Args:
        page: Page to inspect. Its geometry is restored afterwards, but the
            document should not be saved from within a leak check.

    Returns:
        The words whose box lies outside the visible area, in extraction order.
    """
    with full_canvas(page) as visible:
        return [
            str(word[4])
            for word in page.get_text("words")
            if not pymupdf.Rect(word[:4]).intersects(visible)
        ]
