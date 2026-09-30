"""Word and geometry extraction from a PDF's text layer.

PyMuPDF reports word boxes in the page's **unrotated** coordinate system while
`page.rect` reflects the rotation, so boxes on a rotated page are mapped through
`page.rotation_matrix` before they enter the data contract (see `normalize`).

Pages whose text layer yields no words are marked `has_text_layer=False`. They
need OCR; this module does not attempt it. Strings outside the text layer are
listed by `surfaces`.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pymupdf
from anonymizer.core.ingest.normalize import normalize_text, unrotated_rect_to_bbox
from anonymizer.core.ingest.surfaces import extract_surfaces
from anonymizer.core.types import Document, Page, Word

# Reading order is reconstructed from PyMuPDF's block, line and word numbering.
_WORD_SEPARATOR = " "
_LINE_SEPARATOR = "\n"
_BLOCK_SEPARATOR = "\n\n"

# Field positions in PyMuPDF's "words" tuples.
_BLOCK_INDEX = 5
_LINE_INDEX = 6
_WORD_INDEX = 7


def extract_page(pdf_page: pymupdf.Page, index: int) -> Page:
    """Extract one page's words, boxes and reading-order text.

    Args:
        pdf_page: Page to read.
        index: Zero-based page number to record on the result.

    Returns:
        A page whose `text` is the reading-order reconstruction and whose words
        carry offsets into that text.
    """
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
        bbox = unrotated_rect_to_bbox(pymupdf.Rect(x0, y0, x1, y1), pdf_page)
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
        The document, as `document_from_bytes` describes it.

    Raises:
        FileNotFoundError: If `path` does not exist.
        pymupdf.FileDataError: If the file is not a readable PDF.
    """
    return document_from_bytes(read_pdf(path), language=language)


def document_from_bytes(data: bytes, *, language: str | None = None) -> Document:
    """Read a PDF held in memory into a `Document`.

    A caller that needs the file again (to render or redact it) keeps these
    bytes rather than reading the path twice: the file could change in
    between, and boxes computed for one version would land on another.

    Args:
        data: The PDF file's bytes.
        language: BCP 47 tag the detectors will be configured for, recorded on
            the document.

    Returns:
        A document with one page per PDF page, every string found outside the
        text layer as a surface, and the fingerprint of `data`. Neither a path
        nor a file name is recorded: both can be personal data.

    Raises:
        pymupdf.FileDataError: If the bytes are not a readable PDF.
    """
    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        pages = [extract_page(pdf.load_page(index), index) for index in range(pdf.page_count)]
        surfaces = extract_surfaces(pdf)
    return Document(
        pages=pages,
        surfaces=surfaces,
        fingerprint=fingerprint(data),
        language=language,
    )


def read_pdf(path: Path | str) -> bytes:
    """Read a PDF file's bytes.

    Args:
        path: Path to the PDF file.

    Returns:
        The file's content.

    Raises:
        FileNotFoundError: If `path` does not exist. The message names the file
            only, not the folders above it.
    """
    source = Path(path)
    if not source.is_file():
        msg = f"no such file: {source.name}"
        raise FileNotFoundError(msg)
    return source.read_bytes()


def read_verified(path: Path | str, document: Document) -> bytes:
    """Read the PDF a document was loaded from, refusing any other file.

    Boxes computed for one file land on unrelated content in another, even one
    with the same number of pages, and nothing would report it. The check runs
    on the bytes returned, so the file cannot change between check and use.

    Args:
        path: Path to the PDF file.
        document: Document loaded from it.

    Returns:
        The file's content.

    Raises:
        FileNotFoundError: If `path` does not exist.
        ValueError: If the document carries no fingerprint or one of a
            different file.
    """
    if document.fingerprint is None:
        msg = "document carries no fingerprint; load it from the file with load_document"
        raise ValueError(msg)
    data = read_pdf(path)
    if fingerprint(data) != document.fingerprint:
        msg = "document was loaded from a different file than the one given"
        raise ValueError(msg)
    return data


def fingerprint(data: bytes) -> str:
    """Return the SHA-256 of a file's bytes, as lowercase hex.

    Args:
        data: The file's content.

    Returns:
        The hex digest.
    """
    return hashlib.sha256(data).hexdigest()


def pages_needing_ocr(document: Document) -> list[int]:
    """Return the indices of pages that yielded no text layer.

    Args:
        document: Document to inspect.

    Returns:
        Page indices, in document order, that require OCR.
    """
    return [page.index for page in document.pages if not page.has_text_layer]
