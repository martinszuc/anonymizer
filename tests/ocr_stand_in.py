"""An OCR engine for tests: it returns known words instead of reading the picture.

The words usually come from the born-digital original of a scan, loaded from
its text layer (`write_pdf` and `write_scanned_pdf` with the same pages), so
they are exactly what a perfect engine would read. They are handed back in
the pixels of the picture the engine receives, which tests the conversion to
points as a real engine's output would.
"""

from typing import NamedTuple

from anonymizer.core.ingest import OcrWord, PageImage
from anonymizer.core.types import BBox, Document, Page


class ScriptedWord(NamedTuple):
    """A word to report, with its box in page points."""

    text: str
    bbox: BBox
    block: int = 0
    line: int = 0


class ScriptedEngine:
    """Returns one scripted list of words per call, in call order, and keeps the pictures."""

    def __init__(self, pages: list[list[ScriptedWord]]) -> None:
        self.pages = pages
        self.images: list[PageImage] = []

    @classmethod
    def reading(cls, document: Document) -> "ScriptedEngine":
        """An engine that reads each page of a document as its text layer has it."""
        return cls([layout_of(page) for page in document.pages])

    def read(self, image: PageImage) -> list[OcrWord]:
        words = self.pages[len(self.images)]
        self.images.append(image)
        scale = image.dpi / 72
        return [
            OcrWord(
                text=word.text,
                box=(
                    word.bbox.x0 * scale,
                    word.bbox.y0 * scale,
                    word.bbox.x1 * scale,
                    word.bbox.y1 * scale,
                ),
                confidence=0.9,
                block=word.block,
                line=word.line,
            )
            for word in words
        ]


def layout_of(page: Page) -> list[ScriptedWord]:
    """Return a page's words numbered by block and line, from the whitespace between them."""
    scripted: list[ScriptedWord] = []
    block = line = 0
    for previous, word in zip([None, *page.words], page.words, strict=False):
        gap = page.text[previous.end : word.start] if previous is not None else ""
        if "\n\n" in gap:
            block += 1
        if "\n" in gap:
            line += 1
        scripted.append(ScriptedWord(word.text, word.bbox, block, line))
    return scripted
