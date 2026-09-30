"""Reading the picture a scanned page is made of, as stored in a PDF.

Tests count ink in the image data itself rather than in a rendering, where a
redaction's black fill would look like ink.
"""

import pymupdf

from tests.pdf_builders import INK_LEVEL


def stored_image(page: pymupdf.Page) -> pymupdf.Pixmap:
    """Return the page's first picture as stored in the file, decoded."""
    document = page.parent
    assert document is not None
    return pymupdf.Pixmap(document, page.get_images(full=True)[0][0])


def ink(page: pymupdf.Page, area: pymupdf.Rect) -> int:
    """Count ink pixels of the page's picture inside an area given in unrotated points.

    The picture must cover the whole unrotated page, as the scan builders
    place it, so points scale to pixels by the ratio of the two widths.
    """
    image = stored_image(page)
    scale = image.width / page.mediabox.width
    channels = min(image.n, 3)
    columns = range(int(area.x0 * scale), int(area.x1 * scale))
    rows = range(int(area.y0 * scale), int(area.y1 * scale))
    return sum(1 for x in columns for y in rows if min(image.pixel(x, y)[:channels]) < INK_LEVEL)
