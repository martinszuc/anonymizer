"""Tests for the text export: every redacted value replaced by a fixed label."""

from pathlib import Path

import pytest
from anonymizer.core.detect import detect_document, detector_for
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import (
    LeakLayer,
    export_redacted_text,
    find_text_leaks,
    redact_text,
)
from anonymizer.core.types import BBox, Document, EntityType, ReviewState

from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_surfaces_pdf

LINES = [
    "Kupujici Jan Novak, r. c. 900101/0007",
    "Novakova a Jan Novak podepsali",
    "Petra Svobodova, Brno",
    "KEEP this line",
]


def add_person(document: Document, text: str, occurrence: int = 0) -> str:
    """Mark the nth occurrence of a text on page 0 as a person; return its id."""
    page_text = document.pages[0].text
    start = -1
    for _ in range(occurrence + 1):
        start = page_text.index(text, start + 1)
    return document.add_span(0, start, start + len(text), EntityType.PERSON).entity_id


def review(document: Document, entity_id: str, state: ReviewState) -> None:
    document.entity(entity_id).review = state


@pytest.fixture
def document(tmp_path: Path) -> Document:
    loaded = load_document(write_pdf(tmp_path / "contract.pdf", [LINES]), language="cs")
    loaded.entities = detect_document(detector_for("cs"), loaded)
    add_person(loaded, "Jan Novak")
    # A span ending inside a word: the rest of the word goes with it.
    add_person(loaded, "Novak", occurrence=1)
    review(loaded, add_person(loaded, "Jan Novak", occurrence=1), ReviewState.REJECTED)
    add_person(loaded, "Petra Svobodova")  # undecided: redacted
    brno = next(word for word in loaded.pages[0].words if word.text == "Brno").bbox
    loaded.add_region(0, BBox(brno.x0 - 1, brno.y0 - 1, brno.x1 + 1, brno.y1 + 1))
    return loaded


def test_values_become_labels_and_kept_text_stays(document: Document):
    # The fixture's starting state: every value is in the page text.
    assert all(line.split()[0] in document.pages[0].text for line in LINES)
    lines = [line for line in redact_text(document).splitlines() if line]
    assert lines == [
        # "Novak," is one word: the comma goes with it, as in the PDF.
        "Kupujici [PERSON] r. c. [BIRTH_NUMBER]",
        "[PERSON] a Jan Novak podepsali",
        "[PERSON] [REDACTED]",
        "KEEP this line",
    ]


def test_the_written_file_passes_its_check_and_holds_no_redacted_value(
    document: Document, tmp_path: Path
):
    destination = tmp_path / "contract.txt"
    assert export_redacted_text(document, destination) == []
    written = destination.read_text(encoding="utf-8")
    for value in ("900101/0007", "Novakova", "Svobodova", "Brno"):
        assert value not in written
    assert written.count("Jan Novak") == 1  # the copy review kept
    assert sorted(path.name for path in tmp_path.iterdir()) == ["contract.pdf", "contract.txt"]


def test_an_occurrence_left_unmarked_is_a_leak_and_nothing_is_written(tmp_path: Path):
    document = load_document(write_pdf(tmp_path / "a.pdf", [["Jan Novak", "Jan Novak"]]))
    entity_id = add_person(document, "Jan Novak")
    destination = tmp_path / "a.txt"
    destination.write_text("old export", encoding="utf-8")
    leaks = export_redacted_text(document, destination)
    assert [(leak.layer, leak.entity_id, leak.page_index) for leak in leaks] == [
        (LeakLayer.PAGE_TEXT, entity_id, 0)
    ]
    assert destination.read_text(encoding="utf-8") == "old export"
    assert not list(tmp_path.glob(".*.partial"))


def test_without_the_check_the_text_is_written_as_made(tmp_path: Path):
    document = load_document(write_pdf(tmp_path / "a.pdf", [["Jan Novak", "Jan Novak"]]))
    add_person(document, "Jan Novak")
    destination = tmp_path / "a.txt"
    assert export_redacted_text(document, destination, check=False) == []
    written = destination.read_text(encoding="utf-8").split()
    assert written == ["[PERSON]", "Jan", "Novak"]


def test_hidden_items_never_reach_the_text(tmp_path: Path):
    document = load_document(write_surfaces_pdf(tmp_path / "cv.pdf"))
    hidden = " ".join(surface.value for surface in document.surfaces)
    # The fixture's starting state: metadata only in surfaces; a form field's
    # value both in its surface and in the page text, as the field draws it.
    assert "Novak Consulting" in hidden
    assert CONTACT_EMAIL in hidden
    assert CONTACT_EMAIL in document.pages[0].text
    assert "rotated value" in document.pages[1].text
    pages = redact_text(document).split("\f")
    assert "Novak" not in "".join(pages)
    assert pages[0].split() == ["[REDACTED]"]
    # The rotated field lies over the word HERE too, which goes with it.
    assert set(pages[1].split()) == {"[REDACTED]"}


def test_pages_are_separated_by_a_form_feed(tmp_path: Path):
    document = load_document(write_pdf(tmp_path / "a.pdf", [["first page"], ["second page"]]))
    document.pages[0].text += "\fstray"
    pages = redact_text(document).split("\f")
    assert [page.split()[0] for page in pages] == ["first", "second"]
    assert find_text_leaks(pages, document) == []
    with pytest.raises(ValueError, match="has 1 pages, the document 2"):
        find_text_leaks(["one"], document)


def test_overlapping_values_merge_into_the_first_label(tmp_path: Path):
    document = load_document(write_pdf(tmp_path / "a.pdf", [["Jan Novak Brno 12 KEEP"]]))
    text = document.pages[0].text
    document.add_span(0, text.index("Jan"), text.index(" Brno"), EntityType.PERSON)
    document.add_span(0, text.index("Novak"), text.index(" KEEP"), EntityType.ADDRESS)
    assert redact_text(document).split() == ["[PERSON]", "KEEP"]
