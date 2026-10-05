"""PDF text-layer extraction, images wrapped as PDFs, non-text surfaces and OCR engine adapters."""

from anonymizer.core.ingest.engines import (
    OCR_ENGINE_RESOURCES,
    OCR_ENGINES,
    load_ocr_engine,
    missing_ocr_files,
    ocr_engine_installed,
)
from anonymizer.core.ingest.image import (
    ASSUMED_DPI,
    IMAGE_SUFFIXES,
    SOURCE_SUFFIXES,
    UnsupportedFileError,
    as_pdf,
    image_format,
    image_to_pdf,
)
from anonymizer.core.ingest.normalize import normalize_text
from anonymizer.core.ingest.ocr import (
    DEFAULT_OCR_DPI,
    OCR_BOX_MARGIN,
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
    read_source,
    read_verified,
)
from anonymizer.core.ingest.surfaces import extract_surfaces

__all__ = [
    "ASSUMED_DPI",
    "DEFAULT_OCR_DPI",
    "IMAGE_SUFFIXES",
    "OCR_BOX_MARGIN",
    "OCR_ENGINES",
    "OCR_ENGINE_RESOURCES",
    "SOURCE_SUFFIXES",
    "OcrEngine",
    "OcrWord",
    "PageImage",
    "UnsupportedFileError",
    "as_pdf",
    "document_from_bytes",
    "extract_page",
    "extract_surfaces",
    "fingerprint",
    "image_format",
    "image_to_pdf",
    "load_document",
    "load_ocr_engine",
    "missing_ocr_files",
    "normalize_text",
    "ocr_engine_installed",
    "pages_needing_ocr",
    "read_page",
    "read_source",
    "read_verified",
    "render_page",
]
