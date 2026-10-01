"""Session files: a saved review.

A session holds the reviewer's decisions, not the document: every entity with
its review state, the snippet it covers, and the fingerprint of the original
PDF. Pages and surfaces are read again from the original when the session is
opened, so the file carries only the marked snippets rather than a second copy
of the whole text.

Opening a session verifies that it belongs to the given PDF and that every
entity still covers the same text at the same place. A mismatch means the file
or its extraction changed, and a review applied to different text cannot be
trusted, so the session is refused instead. Pages OCR read must therefore be
read again by the same engine at the same resolution; the session records the
engine, and a document read otherwise is refused with a message naming it.
A review made without OCR is refused too when the document is now read with
OCR: its scanned pages would count as read although nothing on them was ever
detected, and export would no longer warn about them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from anonymizer.core.ingest import DEFAULT_OCR_DPI, OcrEngine, load_document
from anonymizer.core.types import SCHEMA_VERSION, Document, Entity

SESSION_FORMAT = "anonymizer-session"
"""Marker identifying a session file among other JSON files."""


def session_to_dict(document: Document) -> dict[str, Any]:
    """Return the session content for a reviewed document.

    Args:
        document: Document loaded from a PDF, with its reviewed entities.

    Returns:
        A JSON-compatible mapping without page text, words or surfaces.

    Raises:
        ValueError: If the document carries no fingerprint.
    """
    if document.fingerprint is None:
        msg = "document carries no fingerprint; load it from the file with load_document"
        raise ValueError(msg)
    return {
        "format": SESSION_FORMAT,
        "schema_version": SCHEMA_VERSION,
        "fingerprint": document.fingerprint,
        "language": document.language,
        "ocr_engine": document.ocr_engine,
        "entities": [entity.to_dict() for entity in document.entities],
    }


def save_session(document: Document, path: Path | str) -> None:
    """Write a reviewed document's session file.

    Args:
        document: Document loaded from a PDF, with its reviewed entities.
        path: Where to write the session.

    Raises:
        ValueError: If the document carries no fingerprint.
    """
    content = json.dumps(session_to_dict(document), ensure_ascii=False, indent=2)
    Path(path).write_text(content, encoding="utf-8")


def load_session(
    session_path: Path | str,
    pdf_path: Path | str,
    *,
    ocr: OcrEngine | None = None,
    ocr_dpi: int = DEFAULT_OCR_DPI,
) -> Document:
    """Reopen a saved review against its original PDF.

    Args:
        session_path: Session file written by `save_session`.
        pdf_path: The original PDF the review was made on.
        ocr: The engine that read the pages needing OCR when the review was made.
        ocr_dpi: The resolution it read them at.

    Returns:
        The document read again from the PDF, with the session's entities.

    Raises:
        ValueError: If the file is not a session of this schema version, it
            belongs to a different PDF, an entity refers to a missing page or
            surface, or an entity no longer covers the text it recorded.
    """
    return apply_session(load_document(pdf_path, ocr=ocr, ocr_dpi=ocr_dpi), session_path)


def apply_session(document: Document, session_path: Path | str) -> Document:
    """Give a document freshly read from its PDF the decisions of a saved review.

    Args:
        document: The original PDF, loaded without entities (see
            `load_document` or `document_from_bytes`).
        session_path: Session file written by `save_session`.

    Returns:
        The same document, with the session's language and entities.

    Raises:
        ValueError: As `load_session`.
    """
    data = json.loads(Path(session_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("format") != SESSION_FORMAT:
        msg = "not a session file"
        raise ValueError(msg)
    version = data.get("schema_version")
    if version != SCHEMA_VERSION:
        msg = f"unsupported session version {version}, expected {SCHEMA_VERSION}"
        raise ValueError(msg)
    if document.fingerprint != data.get("fingerprint"):
        msg = "session belongs to a different PDF"
        raise ValueError(msg)
    _check_ocr_engine(data.get("ocr_engine"), document.ocr_engine)
    document.language = data.get("language")
    document.entities = [Entity.from_dict(entity) for entity in data.get("entities", [])]
    document.check_references()
    _check_covered_text(document)
    return document


def session_ocr_engine(session_path: Path | str) -> str | None:
    """Return the OCR engine a saved review was made with, to read its PDF again.

    Args:
        session_path: Session file written by `save_session`.

    Returns:
        The engine's name, or `None` if the review was made without OCR.

    Raises:
        ValueError: If the file is not a session.
    """
    data = json.loads(Path(session_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("format") != SESSION_FORMAT:
        msg = "not a session file"
        raise ValueError(msg)
    engine = data.get("ocr_engine")
    return str(engine) if engine is not None else None


def _check_ocr_engine(recorded: str | None, used: str | None) -> None:
    """Refuse a document whose scanned pages were read otherwise than in the review."""
    if recorded == used:
        return
    if used is None:
        msg = f"the review was made with OCR engine {recorded!r}; read the PDF with it"
    elif recorded is None:
        msg = (
            "the review was made without OCR, so nothing on the scanned pages was "
            "detected; detect again with OCR instead of reopening it"
        )
    else:
        msg = f"the review was made with OCR engine {recorded!r}, not {used!r}"
    raise ValueError(msg)


def _check_covered_text(document: Document) -> None:
    """Refuse entities whose offsets no longer cover the text they recorded."""
    stale = [
        entity.entity_id for entity in document.entities if not _still_covers(document, entity)
    ]
    if stale:
        msg = (
            f"{len(stale)} entities no longer cover the text they recorded "
            f"(first: {stale[0]}); the PDF or its extraction changed"
        )
        raise ValueError(msg)


def _still_covers(document: Document, entity: Entity) -> bool:
    """Whether an entity's offsets still select exactly its recorded text."""
    if entity.is_region:
        return True
    start, end = entity.span
    if entity.surface_id is not None:
        source_text = document.surface(entity.surface_id).value
    elif entity.page_index is not None:
        source_text = document.page(entity.page_index).text
    else:
        return False
    return source_text[start:end] == entity.text
