"""PDF text-layer extraction and OCR engine adapters."""

from anonymizer.core.ingest.normalize import normalize_text
from anonymizer.core.ingest.pdf import extract_page, load_document, pages_needing_ocr

__all__ = [
    "extract_page",
    "load_document",
    "normalize_text",
    "pages_needing_ocr",
]
