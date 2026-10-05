"""Tests for writing a redacted copy only when it passes the leak check."""

from pathlib import Path

import pytest
from anonymizer.core.detect import detect_document, detector_for
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import Leak, LeakLayer, export_redacted
from anonymizer.core.redact import export as export_module
from anonymizer.core.types import BBox, Document

from tests.pdf_builders import CONTACT_EMAIL, write_pdf

PHONE = "+420 603 123 456"
LINES = [f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "KEEP this line"]


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "cv.pdf", [LINES])


@pytest.fixture
def document(pdf: Path) -> Document:
    loaded = load_document(pdf, language="cs")
    loaded.entities = detect_document(detector_for("cs"), loaded)
    return loaded


def page_text(path: Path) -> str:
    return "\n".join(page.text for page in load_document(path).pages)


def test_writes_a_clean_copy_without_the_redacted_text(pdf: Path, document: Document):
    destination = pdf.with_name("cv-redacted.pdf")
    assert export_redacted(pdf, document, destination) == []
    text = page_text(destination)
    assert CONTACT_EMAIL not in text
    assert "603 123 456" not in text
    assert "KEEP this line" in text
    assert sorted(path.name for path in pdf.parent.iterdir()) == ["cv-redacted.pdf", "cv.pdf"]


def test_replaces_an_existing_destination_when_the_check_passes(pdf: Path, document: Document):
    destination = pdf.with_name("cv-redacted.pdf")
    destination.write_bytes(b"old export")
    assert export_redacted(pdf, document, destination) == []
    assert destination.read_bytes().startswith(b"%PDF")


def test_a_failed_check_writes_nothing_and_keeps_an_existing_file(
    pdf: Path, document: Document, monkeypatch: pytest.MonkeyPatch
):
    leak = Leak(LeakLayer.PAGE_TEXT, "page 1", CONTACT_EMAIL, "e1")
    monkeypatch.setattr(export_module, "find_leaks", lambda *_, **__: [leak])
    destination = pdf.with_name("cv-redacted.pdf")
    destination.write_bytes(b"old export")
    assert export_redacted(pdf, document, destination) == [leak]
    assert destination.read_bytes() == b"old export"
    assert not list(pdf.parent.glob("*.partial"))


def test_the_temporary_copy_is_removed_when_the_check_crashes(
    pdf: Path, document: Document, monkeypatch: pytest.MonkeyPatch
):
    def broken_check(*_: object, **__: object) -> list[Leak]:
        raise RuntimeError("check crashed")

    monkeypatch.setattr(export_module, "find_leaks", broken_check)
    destination = pdf.with_name("cv-redacted.pdf")
    with pytest.raises(RuntimeError, match="check crashed"):
        export_redacted(pdf, document, destination)
    assert sorted(path.name for path in pdf.parent.iterdir()) == ["cv.pdf"]


def test_without_the_check_the_copy_is_written_as_redaction_made_it(
    pdf: Path, document: Document, monkeypatch: pytest.MonkeyPatch
):
    def no_check(*_: object, **__: object) -> list[Leak]:
        raise AssertionError("the check was run")

    monkeypatch.setattr(export_module, "find_leaks", no_check)
    destination = pdf.with_name("cv-redacted.pdf")
    destination.write_bytes(b"old export")
    assert export_redacted(pdf, document, destination, check=False) == []
    assert CONTACT_EMAIL not in page_text(destination)
    assert sorted(path.name for path in pdf.parent.iterdir()) == ["cv-redacted.pdf", "cv.pdf"]


def test_progress_tells_redaction_then_each_layer(pdf: Path, document: Document):
    told: list[tuple[str, int, int]] = []
    export_redacted(
        pdf, document, pdf.with_name("cv-redacted.pdf"), progress=lambda *step: told.append(step)
    )
    layers = [layer.value for layer in LeakLayer if layer is not LeakLayer.OCR]
    assert told == [
        ("redacting", 0, 1),
        ("redacting", 1, 1),
        ("clearing", 0, 0),
        ("saving", 0, 0),
        *((layer, 0, 0) for layer in layers),
    ]


def test_without_the_check_progress_ends_with_saving(pdf: Path, document: Document):
    told: list[str] = []
    export_redacted(
        pdf,
        document,
        pdf.with_name("cv-redacted.pdf"),
        check=False,
        progress=lambda step, _done, _total: told.append(step),
    )
    assert told[-1] == "saving"


def test_refuses_to_overwrite_the_source(pdf: Path, document: Document):
    original = pdf.read_bytes()
    with pytest.raises(ValueError, match="must not overwrite its source"):
        export_redacted(pdf, document, pdf)
    assert pdf.read_bytes() == original


def test_refuses_a_document_of_another_file(pdf: Path, document: Document, tmp_path: Path):
    other = write_pdf(tmp_path / "other.pdf", [["another document"]])
    with pytest.raises(ValueError):
        export_redacted(other, document, tmp_path / "out.pdf")
    assert not (tmp_path / "out.pdf").exists()
    assert not list(tmp_path.glob("*.partial"))


def test_a_drawn_region_removes_what_lies_under_it(pdf: Path, document: Document):
    keep_line = next(word for word in document.page(0).words if word.text == "KEEP")
    # A reviewer draws over the whole "KEEP this line" row, reaching past the page edge.
    top, bottom = keep_line.bbox.y0 - 2, keep_line.bbox.y1 + 2
    document.add_region(0, BBox(-10, top, document.page(0).width + 10, bottom))
    destination = pdf.with_name("cv-redacted.pdf")
    assert export_redacted(pdf, document, destination) == []
    text = page_text(destination)
    assert "KEEP this line" not in text
    assert "e-mail" in text  # outside the region, and not an entity
