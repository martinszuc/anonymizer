"""Reading the pictures a scanned page is made of, as stored in a PDF.

Tests count ink in the image data itself rather than in a rendering, where a
redaction's black fill would look like ink.
"""

import pymupdf

from tests.pdf_builders import INK_LEVEL

# Full coverage paints black: grey level 255 - coverage.
_INVERTED = bytes(range(255, -1, -1))


def ink(page: pymupdf.Page, area: pymupdf.Rect) -> int:
    """Count ink pixels of every picture on the page inside an area in unrotated points.

    Each picture is read over the part of the area it covers, scaled by its
    own placement, so a scan stored in strips is counted whole.
    """
    return sum(
        _ink_in_picture(page, placement["xref"], pymupdf.Rect(placement["bbox"]), area)
        for placement in page.get_image_info(xrefs=True)
    )


def _ink_in_picture(page: pymupdf.Page, xref: int, placed: pymupdf.Rect, area: pymupdf.Rect) -> int:
    overlap = placed & area
    if overlap.is_empty:
        return 0
    levels = _grey_levels(page, xref)
    scale_x, scale_y = levels.width / placed.width, levels.height / placed.height
    columns = range(
        int((overlap.x0 - placed.x0) * scale_x), int((overlap.x1 - placed.x0) * scale_x)
    )
    rows = range(int((overlap.y0 - placed.y0) * scale_y), int((overlap.y1 - placed.y0) * scale_y))
    return sum(1 for x in columns for y in rows if levels.pixel(x, y)[0] < INK_LEVEL)


def _grey_levels(page: pymupdf.Page, xref: int) -> pymupdf.Pixmap:
    """Decode a picture into grey levels as it looks over white paper.

    A stencil mask decodes to coverage alone, painted in black.
    """
    document = page.parent
    assert document is not None
    picture = pymupdf.Pixmap(document, xref)
    if picture.colorspace is None:
        paper = bytes(picture.samples).translate(_INVERTED)
        return pymupdf.Pixmap(pymupdf.csGRAY, picture.width, picture.height, paper, False)
    assert not picture.alpha, "pictures with transparency are not read here"
    return picture if picture.colorspace.n == 1 else pymupdf.Pixmap(pymupdf.csGRAY, picture)
