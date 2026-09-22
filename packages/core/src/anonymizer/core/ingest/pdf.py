"""Word and geometry extraction from a PDF's text layer.

PyMuPDF reports word boxes in the page's **unrotated** coordinate system while
`page.rect` reflects the rotation, so boxes on a rotated page are mapped through
`page.rotation_matrix` before they enter the data contract. Everything that
leaves this module is therefore in the convention `types` documents: PDF points,
per page, origin top-left.

Pages whose text layer yields no words are marked `has_text_layer=False`. They
need OCR; this module does not attempt it.
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

import pymupdf
from anonymizer.core.types import BBox, Document, Page, Word

# Reading order is reconstructed from PyMuPDF's block, line and word numbering.
_WORD_SEPARATOR = " "
_LINE_SEPARATOR = "\n"
_BLOCK_SEPARATOR = "\n\n"

# Field positions in PyMuPDF's "words" tuples.
_BLOCK_INDEX = 5
_LINE_INDEX = 6
_WORD_INDEX = 7


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


def _word_bbox(raw: tuple[float, float, float, float], matrix: pymupdf.Matrix | None) -> BBox:
    """Convert a PyMuPDF word rectangle into a `BBox`, applying page rotation."""
    rect = pymupdf.Rect(*raw)
    if matrix is not None:
        rect = rect * matrix
    rect.normalize()
    return BBox(rect.x0, rect.y0, rect.x1, rect.y1)


def extract_page(pdf_page: pymupdf.Page, index: int) -> Page:
    """Extract one page's words, boxes and reading-order text.

    Args:
        pdf_page: Page to read.
        index: Zero-based page number to record on the result.

    Returns:
        A page whose `text` is the reading-order reconstruction and whose words
        carry offsets into that text.
    """
    matrix = pdf_page.rotation_matrix if pdf_page.rotation else None
    raw_words = sorted(
        pdf_page.get_text("words"),
        key=lambda word: (word[_BLOCK_INDEX], word[_LINE_INDEX], word[_WORD_INDEX]),
    )

    parts: list[str] = []
    words: list[Word] = []
    cursor = 0
    previous_block: int | None = None
    previous_line: int | None = None

    for raw in raw_words:
        x0, y0, x1, y1, raw_text, block_no, line_no, _word_no = raw
        text = normalize_text(str(raw_text))
        if not text:
            continue
        separator = _separator_before(int(block_no), int(line_no), previous_block, previous_line)
        if separator:
            parts.append(separator)
            cursor += len(separator)
        start = cursor
        parts.append(text)
        cursor += len(text)
        bbox = _word_bbox((float(x0), float(y0), float(x1), float(y1)), matrix)
        words.append(Word(text=text, bbox=bbox, start=start, end=cursor))
        previous_block = int(block_no)
        previous_line = int(line_no)

    return Page(
        index=index,
        width=pdf_page.rect.width,
        height=pdf_page.rect.height,
        text="".join(parts),
        words=words,
        has_text_layer=bool(words),
    )


def _separator_before(
    block_no: int,
    line_no: int,
    previous_block: int | None,
    previous_line: int | None,
) -> str:
    """Whitespace to insert before a word, given the previous word's position."""
    if previous_block is None:
        return ""
    if block_no != previous_block:
        return _BLOCK_SEPARATOR
    if line_no != previous_line:
        return _LINE_SEPARATOR
    return _WORD_SEPARATOR


def load_document(path: Path | str, *, language: str | None = None) -> Document:
    """Read a PDF into a `Document`.

    Args:
        path: Path to the PDF file.
        language: BCP 47 tag the detectors will be configured for, recorded on
            the document.

    Returns:
        A document with one page per PDF page. Only the file's name is recorded,
        never its path, which can itself be personal data.

    Raises:
        FileNotFoundError: If `path` does not exist.
        pymupdf.FileDataError: If the file is not a readable PDF.
    """
    source = Path(path)
    if not source.is_file():
        msg = f"no such file: {source.name}"
        raise FileNotFoundError(msg)
    with pymupdf.open(source) as pdf:
        pages = [extract_page(pdf.load_page(index), index) for index in range(pdf.page_count)]
    return Document(pages=pages, source_name=source.name, language=language)


def pages_needing_ocr(document: Document) -> list[int]:
    """Return the indices of pages that yielded no text layer.

    Args:
        document: Document to inspect.

    Returns:
        Page indices, in document order, that require OCR.
    """
    return [page.index for page in document.pages if not page.has_text_layer]
