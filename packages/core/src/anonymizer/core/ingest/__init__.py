"""PDF text-layer extraction, non-text surfaces and OCR engine adapters."""

from anonymizer.core.ingest.normalize import normalize_text
from anonymizer.core.ingest.ocr import (
    DEFAULT_OCR_DPI,
    OcrEngine,
    OcrWord,
    PageImage,
    read_page,
    render_page,
)
from anonymizer.core.ingest.pdf import (
    document_from_bytes,
    extract_page,
    fingerprint,
    load_document,
    pages_needing_ocr,
    read_pdf,
    read_verified,
)
from anonymizer.core.ingest.surfaces import extract_surfaces

__all__ = [
    "DEFAULT_OCR_DPI",
    "OcrEngine",
    "OcrWord",
    "PageImage",
    "document_from_bytes",
    "extract_page",
    "extract_surfaces",
    "fingerprint",
    "load_document",
    "normalize_text",
    "pages_needing_ocr",
    "read_page",
    "read_pdf",
    "read_verified",
    "render_page",
]
