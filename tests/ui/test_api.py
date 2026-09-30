"""Tests for the review API the window calls."""

import base64
from pathlib import Path

import pymupdf
import pytest
from anonymizer.core import pipeline
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import Leak, LeakLayer
from anonymizer.core.types import Document
from anonymizer.ui import api
from anonymizer.ui.api import MAX_DPI, ReviewApi, ReviewError

from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_surfaces_pdf

PHONE = "+420 603 123 456"
LINES = ["Jan Novak", f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "KEEP this line"]


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "cv.pdf", [LINES])


@pytest.fixture
def review(pdf: Path) -> ReviewApi:
    reviewer = ReviewApi()
    reviewer.open_pdf(str(pdf), "cs")
    return reviewer


def entity_of_type(payload: dict, entity_type: str) -> dict:
    (entity,) = [entity for entity in payload["entities"] if entity["type"] == entity_type]
    return entity


def png_size(data_url: str) -> tuple[int, int]:
    prefix = "data:image/png;base64,"
    assert data_url.startswith(prefix)
    pixmap = pymupdf.Pixmap(base64.b64decode(data_url.removeprefix(prefix)))
    return pixmap.width, pixmap.height


class TestOpenPdf:
    def test_describes_pages_and_proposed_entities(self, pdf: Path):
        payload = ReviewApi().open_pdf(str(pdf), "cs")
        assert payload["name"] == "cv.pdf"
        assert payload["language"] == "cs"
        (page,) = payload["pages"]
        assert page["index"] == 0
        assert page["has_text_layer"] is True
        assert (page["width"], page["height"]) == pytest.approx((595, 842), abs=1)
        assert {entity["type"] for entity in payload["entities"]} == {"email", "phone"}
        email = entity_of_type(payload, "email")
        assert email["text"] == CONTACT_EMAIL
        assert email["review"] == "pending"
        assert email["source"] == "rule"
        assert email["page_index"] == 0
        assert email["is_region"] is False
        ((x0, y0, x1, y1),) = email["boxes"]
        assert 0 <= x0 < x1 <= page["width"]
        assert 0 <= y0 < y1 <= page["height"]

    def test_lists_hidden_items_with_their_place(self, tmp_path: Path):
        payload = ReviewApi().open_pdf(str(write_surfaces_pdf(tmp_path / "hidden.pdf")))
        kinds = {surface["kind"] for surface in payload["surfaces"]}
        assert {"metadata", "link", "annotation", "form_field", "bookmark"} <= kinds
        link = next(surface for surface in payload["surfaces"] if surface["kind"] == "link")
        assert link["page_index"] == 0
        assert len(link["box"]) == 4
        metadata = next(s for s in payload["surfaces"] if s["kind"] == "metadata")
        assert metadata["page_index"] is None
        assert metadata["box"] is None

    def test_marks_further_occurrences_unless_told_not_to(
        self, pdf: Path, monkeypatch: pytest.MonkeyPatch
    ):
        calls: list[Document] = []
        monkeypatch.setattr(pipeline, "propagate_occurrences", lambda doc: calls.append(doc) or [])
        ReviewApi().open_pdf(str(pdf), "cs")
        ReviewApi().open_pdf(str(pdf), "cs", False)
        assert len(calls) == 1

    def test_missing_file(self, tmp_path: Path):
        with pytest.raises(ReviewError, match=r"no such file: absent\.pdf"):
            ReviewApi().open_pdf(str(tmp_path / "absent.pdf"))

    def test_not_a_pdf(self, tmp_path: Path):
        text_file = tmp_path / "notes.pdf"
        text_file.write_text("not a PDF", encoding="utf-8")
        with pytest.raises(ReviewError):
            ReviewApi().open_pdf(str(text_file))

    def test_reads_the_file_once(self, pdf: Path, monkeypatch: pytest.MonkeyPatch):
        # Loading and rendering use the same bytes, so a change on disk
        # between them cannot put boxes over another file's content.
        reads: list[str] = []
        read_pdf = api.read_pdf

        def counting_read(path: str) -> bytes:
            reads.append(path)
            return read_pdf(path)

        monkeypatch.setattr(api, "read_pdf", counting_read)
        ReviewApi().open_pdf(str(pdf))
        assert reads == [str(pdf)]


class TestPageImage:
    def test_covers_the_page_at_the_requested_resolution(self, review: ReviewApi):
        page = review.document()["pages"][0]
        width, height = png_size(review.page_image(0, 72))
        assert (width, height) == pytest.approx((page["width"], page["height"]), abs=1)

    def test_rotated_page_matches_the_reported_size(self, tmp_path: Path):
        reviewer = ReviewApi()
        payload = reviewer.open_pdf(str(write_pdf(tmp_path / "turned.pdf", [LINES], rotation=90)))
        page = payload["pages"][0]
        assert page["width"] > page["height"]
        width, height = png_size(reviewer.page_image(0, 72))
        assert (width, height) == pytest.approx((page["width"], page["height"]), abs=1)

    def test_resolution_is_clamped(self, review: ReviewApi):
        page = review.document()["pages"][0]
        width, _ = png_size(review.page_image(0, 10_000))
        assert width == pytest.approx(page["width"] * MAX_DPI / 72, abs=1)

    def test_draws_the_bytes_that_were_loaded(self, review: ReviewApi, pdf: Path):
        before = review.page_image(0, 36)
        write_pdf(pdf, [["someone else's file"]])
        assert review.page_image(0, 36) == before

    def test_unknown_page(self, review: ReviewApi):
        with pytest.raises(ReviewError, match="no page with index 5"):
            review.page_image(5)


class TestSetReview:
    def test_records_the_decision(self, review: ReviewApi):
        email = entity_of_type(review.document(), "email")
        changed = review.set_review(email["id"], "rejected")
        assert changed["review"] == "rejected"
        assert entity_of_type(review.document(), "email")["review"] == "rejected"

    def test_unknown_state(self, review: ReviewApi):
        email = entity_of_type(review.document(), "email")
        with pytest.raises(ReviewError, match="'maybe' is not a valid ReviewState"):
            review.set_review(email["id"], "maybe")

    def test_unknown_entity_message_is_not_quoted(self, review: ReviewApi):
        with pytest.raises(ReviewError) as raised:
            review.set_review("missing", "confirmed")
        assert str(raised.value) == "no entity with id missing"


class TestSessions:
    def test_a_saved_review_reopens_with_its_decisions(self, review: ReviewApi, pdf: Path):
        email = entity_of_type(review.document(), "email")
        review.set_review(email["id"], "rejected")
        session = pdf.with_name("review.json")
        review.save_session(str(session))

        reopened = ReviewApi().open_session(str(pdf), str(session))
        assert reopened["name"] == "cv.pdf"
        assert entity_of_type(reopened, "email")["review"] == "rejected"
        assert entity_of_type(reopened, "phone")["review"] == "pending"

    def test_refuses_a_session_of_another_file(self, review: ReviewApi, tmp_path: Path):
        session = tmp_path / "review.json"
        review.save_session(str(session))
        other = write_pdf(tmp_path / "other.pdf", [["a different document"]])
        with pytest.raises(ReviewError, match="different PDF"):
            ReviewApi().open_session(str(other), str(session))

    def test_unwritable_destination(self, review: ReviewApi, tmp_path: Path):
        with pytest.raises(ReviewError):
            review.save_session(str(tmp_path / "missing-dir" / "review.json"))


def test_closing_forgets_the_document(review: ReviewApi):
    review.close()
    with pytest.raises(ReviewError, match="no document is open"):
        review.page_image(0)


def output_text(path: Path) -> str:
    return "\n".join(page.text for page in load_document(path).pages)


class TestExport:
    def test_writes_the_decisions_and_reports_them(self, review: ReviewApi, pdf: Path):
        phone = entity_of_type(review.document(), "phone")
        review.set_review(phone["id"], "rejected")
        destination = pdf.with_name("cv-redacted.pdf")

        result = review.export(str(destination))

        assert result == {
            "written": True,
            "name": "cv-redacted.pdf",
            "redacted": 1,
            "regions": 0,
            "kept": 1,
            "not_reviewed": 1,
            "hidden_removed": 0,
            "pages_without_text": [],
            "leaks": [],
        }
        text = output_text(destination)
        assert CONTACT_EMAIL not in text
        assert PHONE in text  # kept in review

    def test_a_leak_writes_nothing_and_is_reported(
        self, review: ReviewApi, pdf: Path, monkeypatch: pytest.MonkeyPatch
    ):
        leak = Leak(LeakLayer.PAGE_TEXT, "page 1", CONTACT_EMAIL, "e1")
        monkeypatch.setattr(api, "export_redacted", lambda *_: [leak])
        result = review.export(str(pdf.with_name("cv-redacted.pdf")))
        assert result["written"] is False
        assert result["leaks"] == [{"layer": "page_text", "where": "page 1", "text": CONTACT_EMAIL}]

    def test_pages_without_text_need_consent(self, tmp_path: Path):
        reviewer = ReviewApi()
        reviewer.open_pdf(str(write_pdf(tmp_path / "mixed.pdf", [LINES, []])), "cs")
        destination = tmp_path / "out.pdf"
        with pytest.raises(ReviewError, match="page 2 has no text layer"):
            reviewer.export(str(destination))
        assert not destination.exists()
        result = reviewer.export(str(destination), True)
        assert result["written"] is True
        assert result["pages_without_text"] == [2]

    def test_refuses_to_overwrite_the_original(self, review: ReviewApi, pdf: Path):
        with pytest.raises(ReviewError, match="must not overwrite its source"):
            review.export(str(pdf))

    def test_refuses_an_original_that_changed_on_disk(self, review: ReviewApi, pdf: Path):
        write_pdf(pdf, [["someone else's file"]])
        with pytest.raises(ReviewError):
            review.export(str(pdf.with_name("cv-redacted.pdf")))
        assert not pdf.with_name("cv-redacted.pdf").exists()

    def test_needs_an_open_document(self, tmp_path: Path):
        with pytest.raises(ReviewError, match="no document is open"):
            ReviewApi().export(str(tmp_path / "out.pdf"))


class TestRegions:
    def test_adds_a_region_with_corners_in_any_order(self, review: ReviewApi):
        region = review.add_region(0, 300, 200, 100, 120)
        assert region["type"] == "region"
        assert region["is_region"] is True
        assert region["source"] == "manual"
        assert region["review"] == "confirmed"
        assert region["text"] is None
        assert region["boxes"] == [[100, 120, 300, 200]]
        assert region in review.document()["entities"]

    def test_clips_to_the_page(self, review: ReviewApi):
        page = review.document()["pages"][0]
        region = review.add_region(0, -50, -50, 100, 100)
        assert region["boxes"] == [[0, 0, 100, 100]]
        assert page["width"] > 100

    def test_refuses_a_box_outside_the_page(self, review: ReviewApi):
        with pytest.raises(ReviewError, match="exactly one box with an area"):
            review.add_region(0, -100, 10, -50, 60)

    def test_refuses_an_unknown_page(self, review: ReviewApi):
        with pytest.raises(ReviewError, match="no page with index 4"):
            review.add_region(4, 10, 10, 50, 50)

    def test_removes_a_drawn_region(self, review: ReviewApi):
        region = review.add_region(0, 100, 120, 300, 200)
        review.remove_entity(region["id"])
        assert region["id"] not in [entity["id"] for entity in review.document()["entities"]]

    def test_a_detected_item_is_kept_not_removed(self, review: ReviewApi):
        email = entity_of_type(review.document(), "email")
        with pytest.raises(ReviewError, match="only items you added can be removed"):
            review.remove_entity(email["id"])
        assert entity_of_type(review.document(), "email") == email

    def test_removing_an_unknown_item(self, review: ReviewApi):
        with pytest.raises(ReviewError, match="no entity with id nope"):
            review.remove_entity("nope")

    def test_a_region_is_saved_and_exported(self, review: ReviewApi, pdf: Path):
        keep = next(word for word in load_document(pdf).page(0).words if word.text == "KEEP")
        region = review.add_region(0, 0, keep.bbox.y0 - 2, 595, keep.bbox.y1 + 2)
        session = pdf.with_name("review.json")
        review.save_session(str(session))
        reopened = ReviewApi()
        reopened.open_session(str(pdf), str(session))
        assert region in reopened.document()["entities"]

        destination = pdf.with_name("cv-redacted.pdf")
        result = reopened.export(str(destination))
        assert result["written"] is True
        assert result["regions"] == 1
        assert "KEEP this line" not in output_text(destination)


def test_a_finding_in_hidden_data_counts_as_removed_even_if_rejected(tmp_path: Path):
    reviewer = ReviewApi()
    payload = reviewer.open_pdf(str(write_surfaces_pdf(tmp_path / "hidden.pdf")), "cs")
    hidden = [entity for entity in payload["entities"] if entity["surface_id"] is not None]
    assert hidden
    for entity in hidden:
        reviewer.set_review(entity["id"], "rejected")
    result = reviewer.export(str(tmp_path / "out.pdf"), True)
    assert result["written"] is True
    assert result["kept"] == 0
    assert result["redacted"] == len(payload["entities"])
