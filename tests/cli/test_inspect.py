"""Tests for `anonymize inspect` and the HTML report it writes."""

import base64
import json
import re
from pathlib import Path

import pymupdf
import pytest
from anonymizer.cli import commands
from anonymizer.cli.html_report import TYPE_COLORS, render_report
from anonymizer.cli.main import main
from anonymizer.core.detect import GlinerDetector
from anonymizer.core.types import EntityType

from tests.detect.test_gliner import StandInModel
from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_surfaces_pdf

PHONE = "+420 603 123 456"


def inspect(source: Path, *extra: str) -> str:
    report = source.with_name("report.html")
    assert main(["inspect", str(source), "-o", str(report), "--force", *extra]) == 0
    return report.read_text(encoding="utf-8")


def rects(html: str, css_class: str) -> list[str]:
    """Every rect with the class, including its tooltip."""
    return re.findall(rf'<rect class="[^"]*\b{css_class}\b[^"]*".*?</rect>', html, re.DOTALL)


def rect_geometry(rect: str) -> tuple[float, float, float, float]:
    values = []
    for name in ("x", "y", "width", "height"):
        match = re.search(rf' {name}="([\d.]+)"', rect)
        assert match is not None
        values.append(float(match.group(1)))
    x, y, width, height = values
    return x, y, width, height


def png_size(html: str) -> tuple[int, int]:
    """Width and height of the first page image, read from the PNG header."""
    match = re.search(r'src="data:image/png;base64,([^"]+)"', html)
    assert match is not None
    png = base64.b64decode(match.group(1))
    return int.from_bytes(png[16:20]), int.from_bytes(png[20:24])


def view_box(html: str) -> tuple[float, float]:
    match = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', html)
    assert match is not None
    return float(match.group(1)), float(match.group(2))


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "cv.pdf", [[f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}"], ["end"]])


class TestReport:
    def test_draws_one_box_per_covered_word(self, pdf: Path):
        html = inspect(pdf, "--lang", "cs")
        assert html.count("<img ") == 2
        assert len(rects(html, "t-email")) == 1
        # The phone number spans four words, so four boxes.
        assert len(rects(html, "t-phone")) == len(PHONE.split())
        assert CONTACT_EMAIL in html

    def test_loads_nothing_from_outside_the_file(self, pdf: Path):
        html = inspect(pdf)
        assert "Content-Security-Policy" in html
        assert "default-src 'none'" in html
        assert "<script" not in html
        assert "<link" not in html
        assert all(src.startswith("data:") for src in re.findall(r'src="([^"]*)"', html))

    def test_overlay_matches_the_image_on_a_rotated_page(self, tmp_path: Path):
        rotated = write_pdf(tmp_path / "rotated.pdf", [[f"mail {CONTACT_EMAIL}"]], rotation=90)
        html = inspect(rotated)
        width, height = view_box(html)
        pixels_wide, pixels_high = png_size(html)
        # Landscape after rotation, and the image has the page's proportions.
        assert width > height
        assert pixels_wide / pixels_high == pytest.approx(width / height, rel=0.01)

    def test_boxes_lie_within_the_page(self, tmp_path: Path):
        rotated = write_pdf(tmp_path / "rotated.pdf", [[f"mail {CONTACT_EMAIL}"]], rotation=90)
        html = inspect(rotated)
        width, height = view_box(html)
        boxes = [rect_geometry(rect) for rect in rects(html, "entity")]
        assert boxes
        for x, y, box_width, box_height in boxes:
            assert x >= 0 and x + box_width <= width
            assert y >= 0 and y + box_height <= height

    def test_draws_entities_in_hidden_items_on_the_page(self, tmp_path: Path):
        html = inspect(write_surfaces_pdf(tmp_path / "surfaces.pdf"))
        page_one = html.split('<section id="page-2">')[0]
        # The link annotation's mailto: target has a box, although it is not page text.
        assert any("(in link)" in rect for rect in rects(page_one, "t-email"))
        assert rects(page_one, "hidden-item")

    def test_lists_document_level_items(self, tmp_path: Path):
        html = inspect(write_surfaces_pdf(tmp_path / "surfaces.pdf"))
        document_level = html.split('<section id="document">')[1]
        assert "xmp" in document_level
        assert "metadata" in document_level

    def test_escapes_document_content(self, tmp_path: Path):
        path = tmp_path / "titled.pdf"
        document = pymupdf.open()
        document.new_page()
        document.set_metadata({"title": "<img src=x onerror=alert(1)>"})
        document.save(path)
        document.close()
        html = inspect(path)
        assert "<img src=x" not in html
        assert "&lt;img src=x onerror=alert(1)&gt;" in html

    def test_warns_about_a_page_without_text(self, tmp_path: Path):
        html = inspect(write_pdf(tmp_path / "blank.pdf", [["page one"], []]))
        assert "A scan OCR has not read" in html

    def test_refuses_a_file_other_than_the_one_detected(self, pdf: Path, tmp_path: Path):
        document = commands.detected(pdf, "cs", propagate=False)
        other = write_pdf(tmp_path / "other.pdf", [["someone else's file"]])
        with pytest.raises(ValueError, match="different file"):
            render_report(other, document, dpi=36)

    def test_every_entity_type_has_a_color(self):
        assert set(TYPE_COLORS) == set(EntityType)


class TestReviewedSession:
    def test_shows_review_state_and_drawn_regions(self, pdf: Path):
        session = pdf.with_name("review.json")
        main(["detect", str(pdf), "-o", str(session)])
        content = json.loads(session.read_text(encoding="utf-8"))
        for entity in content["entities"]:
            if entity["type"] == "email":
                entity["review"] = "rejected"
        content["entities"].append(
            {
                "type": "region",
                "page_index": 1,
                "bboxes": [[100, 100, 200, 150]],
                "source": "manual",
            }
        )
        session.write_text(json.dumps(content), encoding="utf-8")

        html = inspect(pdf, "--session", str(session))
        (email,) = rects(html, "t-email")
        assert "review-rejected" in email
        page_two = html.split('<section id="page-2">')[1]
        (region,) = rects(page_two, "t-region")
        assert 'x="100.00" y="100.00" width="100.00" height="50.00"' in region


class TestCommand:
    def test_ner_draws_names_from_the_model(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        detector = GlinerDetector(StandInModel({"Jan Novak": "person"}))
        monkeypatch.setattr(commands, "load_name_model", lambda model_id, root: detector)
        source = write_pdf(tmp_path / "cv.pdf", [["Jan Novak"]])
        html = inspect(source, "--ner", "--resource-root", str(tmp_path))
        assert len(rects(html, "t-person")) == len(["Jan", "Novak"])

    def test_refuses_to_replace_a_file_without_force(
        self, pdf: Path, capsys: pytest.CaptureFixture
    ):
        report = pdf.with_name("report.html")
        report.write_text("keep", encoding="utf-8")
        assert main(["inspect", str(pdf), "-o", str(report)]) == 1
        assert report.read_text(encoding="utf-8") == "keep"
        assert "already exists" in capsys.readouterr().err

    def test_says_the_report_holds_document_content(self, pdf: Path, capsys: pytest.CaptureFixture):
        inspect(pdf)
        assert "contains the document's content" in capsys.readouterr().out
