"""Word and geometry extraction from a PDF's text layer.

An image file is read as the PDF `image.as_pdf` wraps it into: pictures
only, so every page of it needs OCR. Its fingerprint is that of the image
file, and the same bytes always give the same PDF, so a session or a
redaction refuses a different image as they refuse a different PDF.

PyMuPDF reports word boxes in the page's **unrotated** coordinate system while
`page.rect` reflects the rotation, so boxes on a rotated page are mapped through
`page.rotation_matrix` before they enter the data contract (see `normalize`).

Pages whose text layer yields no words are marked `has_text_layer=False`, and
so are pages mostly covered by pictures with only a few visible words over
them: a scan with a page number or a scanner's stamp, whose content is in the
picture. Invisible text over a picture is a producer's OCR layer (a
searchable scan) and is used as the text layer.

Such pages need OCR: given an engine, they are read through it (see `ocr`);
without one they keep only what the text layer had. The thresholds are a
heuristic, not yet checked on real scans. Strings outside the text layer are
listed by `surfaces`.
"""

from __future__ import annotations

import hashlib
import logging
from collections import Counter
from pathlib import Path
from typing import Any

import pymupdf
from anonymizer.core.ingest.image import as_pdf, image_format
from anonymizer.core.ingest.layout import PlacedWord, assemble
from anonymizer.core.ingest.normalize import unrotated_rect_to_bbox
from anonymizer.core.ingest.ocr import DEFAULT_OCR_DPI, OcrEngine, read_page
from anonymizer.core.ingest.surfaces import extract_surfaces
from anonymizer.core.log import counts, short_fingerprint, step
from anonymizer.core.types import Document, Page, PageProgress

log = logging.getLogger(__name__)

# Field positions in PyMuPDF's "words" tuples.
_BLOCK_INDEX = 5
_LINE_INDEX = 6
_WORD_INDEX = 7

# A page at least this much covered by pictures, with fewer words than this
# over them, is a scan: a stamp or a page number is not its content.
_SCAN_PICTURE_SHARE = 0.5
_STAMP_WORDS = 20
# PyMuPDF's trace type for invisible text (render mode 3), as OCR layers use.
_INVISIBLE_TEXT = 3


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
    text, words = assemble(
        PlacedWord(
            text=str(raw_text),
            bbox=unrotated_rect_to_bbox(pymupdf.Rect(x0, y0, x1, y1), pdf_page),
            block=int(block_no),
            line=int(line_no),
        )
        for x0, y0, x1, y1, raw_text, block_no, line_no, _word_no in raw_words
    )
    return Page(
        index=index,
        width=pdf_page.rect.width,
        height=pdf_page.rect.height,
        text=text,
        words=words,
        has_text_layer=bool(words) and not _is_stamped_scan(pdf_page, raw_words),
    )


def _is_stamped_scan(pdf_page: pymupdf.Page, raw_words: list[Any]) -> bool:
    """Whether pictures cover most of the page with only a few visible words over them.

    Pictures and words are compared in the page's unrotated space, where
    PyMuPDF reports both.
    """
    page_area = pdf_page.rect.width * pdf_page.rect.height
    unrotated = pdf_page.rect * pdf_page.derotation_matrix
    pictures = [pymupdf.Rect(info["bbox"]) & unrotated for info in pdf_page.get_image_info()]
    pictures = [picture for picture in pictures if not picture.is_empty]
    if sum(picture.get_area() for picture in pictures) < _SCAN_PICTURE_SHARE * page_area:
        return False
    if any(span["type"] == _INVISIBLE_TEXT for span in pdf_page.get_texttrace()):
        return False
    centres = (pymupdf.Point((raw[0] + raw[2]) / 2, (raw[1] + raw[3]) / 2) for raw in raw_words)
    over_pictures = sum(1 for centre in centres if any(centre in picture for picture in pictures))
    return over_pictures < _STAMP_WORDS


def load_document(
    path: Path | str,
    *,
    language: str | None = None,
    ocr: OcrEngine | None = None,
    ocr_dpi: int = DEFAULT_OCR_DPI,
) -> Document:
    """Read a PDF or an image into a `Document`.

    Args:
        path: Path to the PDF, JPEG, PNG or TIFF file.
        language: BCP 47 tag the detectors will be configured for, recorded on
            the document.
        ocr: Engine that reads the pages needing OCR; without one they stay
            empty.
        ocr_dpi: Resolution those pages are rendered at for the engine.

    Returns:
        The document, as `document_from_bytes` describes it.

    Raises:
        FileNotFoundError: If `path` does not exist.
        UnsupportedFileError: If the file is of another type or a damaged image.
        pymupdf.FileDataError: If the file is not a readable PDF.
    """
    return document_from_bytes(read_source(path), language=language, ocr=ocr, ocr_dpi=ocr_dpi)


def document_from_bytes(
    data: bytes,
    *,
    language: str | None = None,
    ocr: OcrEngine | None = None,
    ocr_dpi: int = DEFAULT_OCR_DPI,
    ocr_progress: PageProgress | None = None,
) -> Document:
    """Read a PDF or an image held in memory into a `Document`.

    A caller that needs the file again (to render or redact it) keeps these
    bytes rather than reading the path twice: the file could change in
    between, and boxes computed for one version would land on another.

    Args:
        data: The file's bytes: a PDF, or a JPEG, PNG or TIFF image, told
            apart by content.
        language: BCP 47 tag the detectors will be configured for, recorded on
            the document.
        ocr: Engine that reads the pages needing OCR; without one they stay
            empty. A session saved for the document can only be reopened with
            the same engine and resolution, since its offsets refer to what
            OCR read.
        ocr_dpi: Resolution those pages are rendered at for the engine.
        ocr_progress: Told how many of the pages needing OCR it has read; the
            text layer is read too fast to be worth telling.

    Returns:
        A document with one page per PDF page (per image frame), every
        string found outside the text layer as a surface, and the
        fingerprint of `data`. Neither a path nor a file name is recorded:
        both can be personal data.

    Raises:
        UnsupportedFileError: If the bytes are of another type or a damaged
            image.
        pymupdf.FileDataError: If the bytes are not a readable PDF.
    """
    digest = fingerprint(data)
    with step(
        log,
        "read document",
        done_level=logging.INFO,
        document=short_fingerprint(digest),
        size=len(data),
        format=(image_format(data) or "PDF").lower(),
        ocr=ocr.name if ocr is not None else None,
    ) as outcome:
        with pymupdf.open(stream=as_pdf(data), filetype="pdf") as pdf:
            pages = [extract_page(pdf.load_page(index), index) for index in range(pdf.page_count)]
            for page in pages:
                log.debug(
                    "page %d: text layer=%s words=%d",
                    page.index,
                    page.has_text_layer,
                    len(page.words),
                )
            if ocr is not None:
                pages = _read_scans(pdf, pages, ocr, ocr_dpi, ocr_progress)
            surfaces = extract_surfaces(pdf)
        read_by_ocr = sum(page.raster_dpi is not None for page in pages)
        unread = len(pages_needing_ocr(Document(pages=pages)))
        outcome.update(
            pages=len(pages),
            read_by_ocr=read_by_ocr,
            hidden_items=len(surfaces),
            hidden_kinds=counts(Counter(surface.kind for surface in surfaces)),
        )
        if unread:
            log.info(
                "%d page(s) have no text layer and were not read by OCR; nothing on them "
                "is detected or redacted",
                unread,
            )
    return Document(
        pages=pages,
        surfaces=surfaces,
        fingerprint=digest,
        language=language,
        ocr_engine=ocr.name if ocr is not None and read_by_ocr else None,
    )


def _read_scans(
    pdf: pymupdf.Document,
    pages: list[Page],
    ocr: OcrEngine,
    dpi: int,
    progress: PageProgress | None,
) -> list[Page]:
    """Replace each page without a text layer by what OCR reads on it."""
    scans = [page.index for page in pages if not page.has_text_layer]
    if scans and progress is not None:
        progress(0, len(scans))
    read = list(pages)
    for done, index in enumerate(scans, start=1):
        read[index] = read_page(pdf.load_page(index), index, ocr, dpi)
        if progress is not None:
            progress(done, len(scans))
    return read


def read_source(path: Path | str) -> bytes:
    """Read the bytes of a file to review: a PDF or an image.

    Args:
        path: Path to the file.

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
    """Read the file a document was loaded from as a PDF, refusing any other file.

    Boxes computed for one file land on unrelated content in another, even one
    with the same number of pages, and nothing would report it. The check runs
    on the bytes the PDF is made from, so the file cannot change between
    check and use.

    Args:
        path: Path to the PDF or image file.
        document: Document loaded from it.

    Returns:
        A PDF's content, or the PDF an image is wrapped into (`as_pdf`),
        identical to the one the document was read from.

    Raises:
        FileNotFoundError: If `path` does not exist.
        ValueError: If the document carries no fingerprint or one of a
            different file.
    """
    if document.fingerprint is None:
        msg = "document carries no fingerprint; load it from the file with load_document"
        raise ValueError(msg)
    data = read_source(path)
    if fingerprint(data) != document.fingerprint:
        msg = "document was loaded from a different file than the one given"
        raise ValueError(msg)
    return as_pdf(data)


def fingerprint(data: bytes) -> str:
    """Return the SHA-256 of a file's bytes, as lowercase hex.

    Args:
        data: The file's content.

    Returns:
        The hex digest.
    """
    return hashlib.sha256(data).hexdigest()


def pages_needing_ocr(document: Document) -> list[int]:
    """Return the indices of pages without a usable text layer that OCR has not read.

    Nothing on such a page is detected, so it would reach a redacted copy
    unchanged while the leak check still passes.

    Args:
        document: Document to inspect.

    Returns:
        Page indices, in document order, that still require OCR.
    """
    return [
        page.index for page in document.pages if not page.has_text_layer and page.raster_dpi is None
    ]
