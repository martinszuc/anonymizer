"""Reading a page without a usable text layer through an OCR engine.

The page is rendered to a picture at a chosen resolution and an `OcrEngine`
returns the words it reads with boxes in that picture's pixels. Rendering
follows the page's rotation, so the picture is what a reviewer sees and a box
converts to rotated page space by scale alone (`points = pixels * 72 / dpi`),
with no rotation mapping as the text layer needs. The page records the
resolution in `Page.raster_dpi`.

Engines fit a word's box to the core of its ink and clip the edges of its
letters; redacted from such a box, a word leaves slivers of ink beside it,
which the leak check cannot see. Every box is therefore grown on each side
by `OCR_BOX_MARGIN` of its height. In the scanned benchmark (OnnxTR, clean
scans) 322 of 750 words had ink outside their boxes; with this margin 4 did.
A larger margin starts to cover the neighbouring lines at usual spacing.

An engine runs locally and never downloads anything: an adapter for a
library that fetches its own weights is given local model paths from the
resource catalog instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pymupdf
from anonymizer.core.ingest.layout import PlacedWord, assemble
from anonymizer.core.types import BBox, Page

DEFAULT_OCR_DPI = 300
"""Resolution pages are rendered at for OCR; 300 DPI is the usual scanning resolution."""

OCR_BOX_MARGIN = 0.15
"""Share of a word box's height added on each side of it."""

_POINTS_PER_INCH = 72


@dataclass(frozen=True, slots=True)
class PageImage:
    """A rendered page, as an engine receives it.

    Attributes:
        width: Width in pixels.
        height: Height in pixels.
        dpi: Resolution the page was rendered at.
        samples: RGB pixels, three bytes each, row by row from the top left.
    """

    width: int
    height: int
    dpi: int
    samples: bytes


@dataclass(frozen=True, slots=True)
class OcrWord:
    """One word an engine read.

    Attributes:
        text: The word. It may contain spaces when the engine could not split
            a line into words; its box then covers all of them, which redacts
            more than needed rather than leaving part of a value.
        box: `(x0, y0, x1, y1)` in pixels of the picture, origin top left.
        confidence: The engine's confidence in `[0, 1]`.
        block: Number of the text block (paragraph) the word belongs to.
        line: Number of the line within the page the word belongs to.
    """

    text: str
    box: tuple[float, float, float, float]
    confidence: float
    block: int
    line: int


class OcrEngine(Protocol):
    """Reads the words in a picture of a page."""

    def read(self, image: PageImage) -> list[OcrWord]:
        """Return the words in the picture.

        Args:
            image: The rendered page.

        Returns:
            Words in reading order within each line; lines may come in any
            order, since they are sorted by their block and line numbers.
        """
        ...


def render_page(pdf_page: pymupdf.Page, dpi: int) -> PageImage:
    """Render a page, rotation applied, into the picture an engine reads.

    Args:
        pdf_page: Page to render.
        dpi: Resolution in pixels per inch.

    Returns:
        The page as RGB pixels without transparency.
    """
    picture = pdf_page.get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB, alpha=False)
    return PageImage(
        width=picture.width, height=picture.height, dpi=dpi, samples=bytes(picture.samples)
    )


def read_page(pdf_page: pymupdf.Page, index: int, engine: OcrEngine, dpi: int) -> Page:
    """Read a page's words with an OCR engine instead of its text layer.

    Args:
        pdf_page: Page to read.
        index: Zero-based page number to record on the result.
        engine: Engine that reads the rendered page.
        dpi: Resolution to render the page at.

    Returns:
        A page whose words and text come from OCR, with `has_text_layer`
        false and `raster_dpi` set.
    """
    image = render_page(pdf_page, dpi)
    page = Page(
        index=index,
        width=pdf_page.rect.width,
        height=pdf_page.rect.height,
        has_text_layer=False,
        raster_dpi=dpi,
    )
    read = sorted(engine.read(image), key=lambda word: (word.block, word.line))
    page.text, page.words = assemble(
        PlacedWord(
            text=word.text.strip(),
            bbox=_to_points(word.box, image, page),
            block=word.block,
            line=word.line,
        )
        for word in read
    )
    return page


def _to_points(box: tuple[float, float, float, float], image: PageImage, page: Page) -> BBox:
    """Convert a pixel box to page points, grown by the margin and clipped to the page.

    The picture is rounded up to whole pixels, so it can reach a fraction of
    a point past the page; clipping happens in points for that reason.
    """
    scale = _POINTS_PER_INCH / image.dpi
    x0, y0, x1, y1 = (value * scale for value in box)
    left, right = sorted((x0, x1))
    top, bottom = sorted((y0, y1))
    margin = OCR_BOX_MARGIN * (bottom - top)
    return BBox(
        _clip(left - margin, page.width),
        _clip(top - margin, page.height),
        _clip(right + margin, page.width),
        _clip(bottom + margin, page.height),
    )


def _clip(value: float, limit: float) -> float:
    return min(max(value, 0.0), limit)
