"""PDF text-layer extraction, non-text surfaces and OCR engine adapters."""

from anonymizer.core.ingest.normalize import normalize_text
from anonymizer.core.ingest.pdf import (
    extract_page,
    file_fingerprint,
    load_document,
    pages_needing_ocr,
)
from anonymizer.core.ingest.surfaces import extract_surfaces

__all__ = [
    "extract_page",
    "extract_surfaces",
    "file_fingerprint",
    "load_document",
    "normalize_text",
    "pages_needing_ocr",
]
