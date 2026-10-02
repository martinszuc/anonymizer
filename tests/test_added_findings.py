"""Tests for text a reviewer adds because detection missed it: repeats, removal,
the saved review and the redacted copy, in one small PDF."""

from pathlib import Path

import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.pipeline import add_finding, build_detector, remove_finding, run_detection
from anonymizer.core.redact import LeakLayer, export_redacted
from anonymizer.core.session import load_session, save_session
from anonymizer.core.types import DetectionSource, Document, EntityType, ReviewState

from tests.pdf_builders import CONTACT_EMAIL, write_pdf

# Names no rule finds, an identifier beside one, and a surname repeated alone.
PAGES = [
    [
        "Contact Petra Svobodova today",
        f"e-mail {CONTACT_EMAIL}",
        "Svobodova signed, Svobodova paid",
    ],
    ["by Petra Svobodova"],
]


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "letter.pdf", PAGES)


@pytest.fixture
def document(pdf: Path) -> Document:
    loaded = load_document(pdf, language="cs")
    run_detection(loaded, build_detector("cs"))
    return loaded


def add(document: Document, text: str, *, page: int = 0, nth: int = 0, propagate: bool = True):
    """Add the `nth` occurrence of a text on a page, as the window does from its words."""
    page_text = document.pages[page].text
    start = -1
    for _ in range(nth + 1):
        start = page_text.index(text, start + 1)
    return add_finding(
        document, page, start, start + len(text), EntityType.PERSON, propagate=propagate
    )


def page_text(path: Path) -> str:
    return "\n".join(page.text for page in load_document(path).pages)


def test_the_fixture_starts_with_the_names_unfound(document: Document):
    assert [entity.type for entity in document.entities] == [EntityType.EMAIL]


class TestAddFinding:
    def test_the_finding_comes_first_then_its_repeats(self, document: Document):
        added = add(document, "Petra Svobodova")
        assert [(entity.page_index, entity.text, entity.source) for entity in added] == [
            (0, "Petra Svobodova", DetectionSource.MANUAL),
            (1, "Petra Svobodova", DetectionSource.PROPAGATED),
        ]
        assert added[1].review is ReviewState.PENDING
        assert all(entity in document.entities for entity in added)

    def test_repeats_skip_text_already_marked(self, document: Document):
        add(document, "Petra Svobodova")
        added = add(document, "Svobodova", page=0, nth=1)
        # The surname inside the marked full names is already covered.
        assert [entity.text for entity in added] == ["Svobodova", "Svobodova"]
        assert {entity.page_index for entity in added} == {0}

    def test_repeats_can_be_left_out(self, document: Document):
        assert len(add(document, "Petra Svobodova", propagate=False)) == 1


class TestRemoveFinding:
    def test_repeats_go_with_the_added_text(self, document: Document):
        finding, repeat = add(document, "Petra Svobodova")
        removed = remove_finding(document, finding.entity_id)
        assert removed == [finding, repeat]
        assert [entity.type for entity in document.entities] == [EntityType.EMAIL]

    def test_a_confirmed_repeat_stays(self, document: Document):
        finding, repeat = add(document, "Petra Svobodova")
        repeat.review = ReviewState.CONFIRMED
        assert remove_finding(document, finding.entity_id) == [finding]
        assert repeat in document.entities

    def test_repeats_stay_while_another_finding_marks_the_text(self, document: Document):
        finding, repeat = add(document, "Petra Svobodova")
        start = document.pages[1].text.index("Petra")
        # Detected there too, by a model say, before the reviewer added it.
        document.remove_entity(repeat.entity_id)
        second = document.add_span(1, start, start + len("Petra Svobodova"), EntityType.PERSON)
        second.source = DetectionSource.MODEL
        _, again = add(document, "Svobodova", page=0, nth=1)
        assert remove_finding(document, finding.entity_id) == [finding]
        assert second in document.entities
        assert again in document.entities

    def test_a_region_goes_alone(self, document: Document):
        add(document, "Petra Svobodova")
        region = document.add_region(0, document.entities[0].bboxes[0])
        assert remove_finding(document, region.entity_id) == [region]


class TestExport:
    def test_added_text_and_its_repeats_leave_the_copy(
        self, pdf: Path, document: Document, tmp_path: Path
    ):
        add(document, "Petra Svobodova")
        add(document, "Svobodova", page=0, nth=1)
        destination = tmp_path / "out.pdf"
        assert export_redacted(pdf, document, destination) == []
        text = page_text(destination)
        assert "Svobodova" not in text
        assert "Petra" not in text
        assert CONTACT_EMAIL not in text
        assert "Contact" in text
        assert "today" in text

    def test_a_kept_repeat_stays_and_the_check_still_passes(
        self, pdf: Path, document: Document, tmp_path: Path
    ):
        add(document, "Petra Svobodova")
        _, repeat = add(document, "Svobodova", page=0, nth=1)
        repeat.review = ReviewState.REJECTED
        destination = tmp_path / "out.pdf"
        assert export_redacted(pdf, document, destination) == []
        assert page_text(destination).count("Svobodova") == 1

    def test_the_leak_check_reads_added_text_like_any_finding(
        self, pdf: Path, document: Document, tmp_path: Path
    ):
        # Without its repeat, the name stays on page 2: the copy must be refused.
        add(document, "Petra Svobodova", propagate=False)
        destination = tmp_path / "out.pdf"
        leaks = export_redacted(pdf, document, destination)
        # The object layer sees the literal string on page 2 as well.
        assert (LeakLayer.PAGE_TEXT, 1, "Petra Svobodova") in [
            (leak.layer, leak.page_index, leak.text) for leak in leaks
        ]
        assert not destination.exists()


def test_added_text_survives_a_saved_review(pdf: Path, document: Document, tmp_path: Path):
    add(document, "Petra Svobodova")
    session = tmp_path / "letter.session.json"
    save_session(document, session)
    reopened = load_session(session, pdf)
    assert [entity.to_dict() for entity in reopened.entities] == [
        entity.to_dict() for entity in document.entities
    ]
