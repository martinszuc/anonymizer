"""Conversion between raw PyMuPDF values and the conventions `types` documents.

Text is NFC-normalized; rectangles end up in rotated page space, origin top-left,
which is what `page.rect` describes and what a reviewer sees. Writing back into a
PDF needs the inverse, `bbox_to_unrotated_rect`.
"""

from __future__ import annotations

import unicodedata

import pymupdf
from anonymizer.core.types import BBox


def normalize_text(text: str) -> str:
    """Normalize text to NFC.

    Decomposed sequences (`n` + combining caron) and precomposed characters (`ň`)
    compare unequal and have different lengths, which would make offsets and
    redaction targets depend on how the producer wrote the file.

    Args:
        text: Text in any Unicode normalization form.

    Returns:
        The NFC-normalized text.
    """
    return unicodedata.normalize("NFC", text)


def rect_to_bbox(rect: pymupdf.Rect) -> BBox:
    """Convert a rectangle that is already in rotated page space into a `BBox`.

    Args:
        rect: Rectangle in page points, possibly with swapped corners.

    Returns:
        The box with its corners ordered.
    """
    ordered = pymupdf.Rect(rect)
    ordered.normalize()
    return BBox(ordered.x0, ordered.y0, ordered.x1, ordered.y1)


def unrotated_rect_to_bbox(rect: pymupdf.Rect, page: pymupdf.Page) -> BBox:
    """Convert a rectangle in the page's unrotated space into a `BBox`.

    PyMuPDF reports word, annotation and widget rectangles unrotated while
    `page.rect` reflects the rotation; link rectangles alone come back rotated.
    The rotation matrix is the identity on an unrotated page.

    Args:
        rect: Rectangle in the unrotated coordinate system of `page`.
        page: Page the rectangle belongs to.

    Returns:
        The box in rotated page space.
    """
    return rect_to_bbox(pymupdf.Rect(rect) * page.rotation_matrix)


def bbox_to_unrotated_rect(bbox: BBox, page: pymupdf.Page) -> pymupdf.Rect:
    """Convert a `BBox` into the page's unrotated space, as PyMuPDF annotations expect.

    A redaction annotation given rotated coordinates on a rotated page lands in
    the wrong place and removes nothing, without an error.

    Args:
        bbox: Box in rotated page space.
        page: Page the box belongs to.

    Returns:
        The rectangle in the unrotated coordinate system of `page`.
    """
    rect = pymupdf.Rect(bbox.x0, bbox.y0, bbox.x1, bbox.y1) * page.derotation_matrix
    rect.normalize()
    return rect
