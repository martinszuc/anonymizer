"""Tests for saving and reopening a review as a session file."""

import json
from pathlib import Path

import pytest
from anonymizer.core.detect import detect_document, structured_detector
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import find_leaks, redact_pdf
from anonymizer.core.session import load_session, save_session
from anonymizer.core.types import (
    SCHEMA_VERSION,
    BBox,
    DetectionSource,
    Document,
    Entity,
    EntityType,
    ReviewState,
)

from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_surfaces_pdf

LINES = ["Jan Novak", f"e-mail {CONTACT_EMAIL}", "tel. +420 603 123 456", "KEEP this line"]
PHOTO = BBox(300, 80, 400, 180)


def reviewed(path: Path) -> Document:
    """Detect, reject the phone number, and draw one region."""
    document = load_document(path, language="cs")
    document.entities = detect_document(structured_detector(), document)
    for entity in document.entities:
        if entity.type is EntityType.PHONE:
            entity.review = ReviewState.REJECTED
    document.entities.append(
        Entity(
            type=EntityType.REGION,
            page_index=0,
            bboxes=[PHOTO],
            source=DetectionSource.MANUAL,
            review=ReviewState.CONFIRMED,
        )
    )
    return document


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "contact.pdf", [LINES])


@pytest.fixture
def saved(pdf: Path) -> tuple[Document, Path]:
    document = reviewed(pdf)
    path = pdf.with_suffix(".session.json")
    save_session(document, path)
    return document, path


@pytest.fixture
def session(saved: tuple[Document, Path]) -> Path:
    return saved[1]


class TestRoundTrip:
    def test_reopened_session_has_the_same_decisions(self, pdf: Path, saved: tuple[Document, Path]):
        document, session = saved
        reopened = load_session(session, pdf)
        assert [entity.to_dict() for entity in reopened.entities] == [
            entity.to_dict() for entity in document.entities
        ]

    def test_pages_and_language_come_back(self, pdf: Path, session: Path):
        reopened = load_session(session, pdf)
        assert reopened.language == "cs"
        assert "KEEP this line" in reopened.pages[0].text

    def test_entities_on_surfaces_survive_reloading(self, tmp_path: Path):
        pdf = write_surfaces_pdf(tmp_path / "surfaces.pdf")
        document = load_document(pdf)
        document.entities = detect_document(structured_detector(), document)
        assert any(not entity.in_page_text for entity in document.entities)
        save_session(document, tmp_path / "surfaces.session.json")
        reopened = load_session(tmp_path / "surfaces.session.json", pdf)
        assert len(reopened.entities) == len(document.entities)


class TestSlimFile:
    def test_session_holds_decisions_not_the_document(self, session: Path):
        content = json.loads(session.read_text(encoding="utf-8"))
        assert set(content) == {"format", "schema_version", "fingerprint", "language", "entities"}
        assert "KEEP this line" not in session.read_text(encoding="utf-8")

    def test_session_holds_neither_path_nor_file_name(self, pdf: Path, session: Path):
        text = session.read_text(encoding="utf-8")
        assert pdf.name not in text
        assert str(pdf.parent) not in text


class TestRefusals:
    def test_session_for_another_pdf_is_refused(self, tmp_path: Path, session: Path):
        other = write_pdf(tmp_path / "other.pdf", [["something", "else"]])
        with pytest.raises(ValueError, match="different PDF"):
            load_session(session, other)

    def test_non_session_json_is_refused(self, tmp_path: Path, pdf: Path):
        path = tmp_path / "other.json"
        path.write_text('{"pages": []}', encoding="utf-8")
        with pytest.raises(ValueError, match="not a session file"):
            load_session(path, pdf)

    def test_foreign_schema_version_is_refused(self, pdf: Path, session: Path):
        content = json.loads(session.read_text(encoding="utf-8"))
        content["schema_version"] = SCHEMA_VERSION + 1
        session.write_text(json.dumps(content), encoding="utf-8")
        with pytest.raises(ValueError, match="unsupported session version"):
            load_session(session, pdf)

    def test_entity_that_no_longer_covers_its_text_is_refused(self, pdf: Path, session: Path):
        content = json.loads(session.read_text(encoding="utf-8"))
        email = next(entity for entity in content["entities"] if entity["type"] == "email")
        email["start"] += 1
        session.write_text(json.dumps(content), encoding="utf-8")
        with pytest.raises(ValueError, match="no longer cover the text"):
            load_session(session, pdf)

    def test_entity_on_a_missing_page_is_refused(self, pdf: Path, session: Path):
        content = json.loads(session.read_text(encoding="utf-8"))
        content["entities"][-1]["page_index"] = 5
        session.write_text(json.dumps(content), encoding="utf-8")
        with pytest.raises(ValueError, match="missing page 5"):
            load_session(session, pdf)

    def test_document_without_a_fingerprint_cannot_be_saved(self, tmp_path: Path):
        with pytest.raises(ValueError, match="no fingerprint"):
            save_session(Document(), tmp_path / "empty.session.json")


def test_redaction_from_a_reopened_session_passes_the_leak_check(pdf: Path, session: Path):
    document = load_session(session, pdf)
    output = pdf.with_name("out.pdf")
    redact_pdf(pdf, document, output)
    text = load_document(output).pages[0].text
    assert CONTACT_EMAIL not in text
    assert "603" in text
    assert find_leaks(output, document) == []
