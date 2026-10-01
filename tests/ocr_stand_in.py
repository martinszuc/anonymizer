"""An OCR engine for tests: it returns known words instead of reading the picture.

The words usually come from the born-digital original of a scan, loaded from
its text layer (`write_pdf` and `write_scanned_pdf` with the same pages), so
they are exactly what a perfect engine would read. They are handed back in
the pixels of the picture the engine receives, which tests the conversion to
points as a real engine's output would.

`ScriptedEngine` reports its words whatever the picture shows; `InkReadingEngine`
reports a word only where the picture still holds ink that looks like text,
so it can re-read a redacted page as the leak check does.
"""

from typing import NamedTuple, Self

from anonymizer.core.ingest import OcrWord, PageImage
from anonymizer.core.types import BBox, Document, Page


class ScriptedWord(NamedTuple):
    """A word to report, with its box in page points."""

    text: str
    bbox: BBox
    block: int = 0
    line: int = 0


class ScriptedEngine:
    """Returns one scripted list of words per call, and keeps the pictures.

    The lists are used in call order and then from the start again, so the
    leak check re-reads the pages ingest read in the same turn.
    """

    name = "stand-in"

    def __init__(self, pages: list[list[ScriptedWord]]) -> None:
        self.pages = pages
        self.images: list[PageImage] = []

    @classmethod
    def reading(cls, document: Document) -> Self:
        """An engine that reads each page of a document as its text layer has it."""
        return cls([layout_of(page) for page in document.pages])

    def read(self, image: PageImage) -> list[OcrWord]:
        words = [
            word
            for word in self.pages[len(self.images) % len(self.pages)]
            if self.sees(word, image)
        ]
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

    def sees(self, word: ScriptedWord, image: PageImage) -> bool:
        """Whether the word is still in the picture; a scripted engine always sees it."""
        del word, image
        return True


# Dark pixels are ink; a word's box holding fewer is blank, holding more is a
# solid fill, such as a redaction box. Text covers a fraction in between.
_DARK = 100
_TEXT_COVERAGE = (0.02, 0.8)


class InkReadingEngine(ScriptedEngine):
    """Reports a scripted word only where its box in the picture holds text-like ink."""

    def sees(self, word: ScriptedWord, image: PageImage) -> bool:
        scale = image.dpi / 72
        columns = range(int(word.bbox.x0 * scale), min(int(word.bbox.x1 * scale), image.width))
        rows = range(int(word.bbox.y0 * scale), min(int(word.bbox.y1 * scale), image.height))
        # The red channel of an RGB pixel stands in for its grey level.
        levels = [image.samples[(y * image.width + x) * 3] for y in rows for x in columns]
        coverage = sum(1 for level in levels if level < _DARK) / max(len(levels), 1)
        low, high = _TEXT_COVERAGE
        return low < coverage < high


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
