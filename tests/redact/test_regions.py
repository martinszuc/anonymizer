"""Redaction of regions a reviewer draws, verified on the saved file."""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.detect import detect_document, structured_detector
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import LeakLayer, find_leaks, redact_pdf
from anonymizer.core.types import BBox, DetectionSource, Document, Entity, EntityType, ReviewState

from tests.pdf_builders import CONTACT_EMAIL

SIGNATURE_BLUE = (0.0, 0.0, 1.0)
BORDER_GREEN = (0.0, 0.5, 0.0)
BACKGROUND_GREY = (0.9, 0.9, 0.9)

TEXT_REGION = BBox(70, 90, 220, 120)
PHOTO_REGION = BBox(290, 70, 350, 190)
SIGNATURE_REGION = BBox(70, 240, 210, 360)
BORDER_REGION = BBox(250, 480, 350, 520)
PHOTO_AREA = pymupdf.Rect(300, 80, 400, 180)


def write_region_pdf(path: Path, rotation: int = 0) -> Path:
    """Text, a photo, a vector signature, a line crossing a region's edge, and an
    email on a grey background (for text redaction, not regions)."""
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((80, 110), "SECRET TEXT", fontname="helv", fontsize=12)
    photo = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 100, 100), False)
    photo.set_rect(photo.irect, (255, 0, 0))
    page.insert_image(PHOTO_AREA, pixmap=photo)
    signature = page.new_shape()
    signature.draw_bezier((80, 300), (120, 250), (160, 350), (200, 300))
    signature.finish(color=SIGNATURE_BLUE, width=2)
    signature.commit()
    border = page.new_shape()
    border.draw_line((50, 500), (550, 500))
    border.finish(color=BORDER_GREEN, width=1)
    border.commit()
    background = page.new_shape()
    background.draw_rect(pymupdf.Rect(50, 590, 550, 625))
    background.finish(fill=BACKGROUND_GREY, color=None)
    background.commit()
    page.insert_text((60, 612), f"mail {CONTACT_EMAIL}", fontname="helv", fontsize=12)
    if rotation:
        page.set_rotation(rotation)
    document.save(path)
    return path


def region(box: BBox, review: ReviewState = ReviewState.CONFIRMED) -> Entity:
    return Entity(
        type=EntityType.REGION,
        page_index=0,
        bboxes=[box],
        source=DetectionSource.MANUAL,
        review=review,
    )


def redacted(source: Path, document: Document) -> Path:
    output = source.with_name(f"{source.stem}-out.pdf")
    redact_pdf(source, document, output)
    return output


def same_color(actual: tuple[float, ...] | None, expected: tuple[float, float, float]) -> bool:
    # The file stores colours as 32-bit floats: 0.9 comes back as 0.8999999761581421.
    if actual is None:
        return False
    return all(abs(a - e) < 1e-3 for a, e in zip(actual, expected, strict=True))


def stroked(path: Path, color: tuple[float, float, float]) -> list[pymupdf.Rect]:
    with pymupdf.open(path) as pdf:
        drawings = pdf.load_page(0).get_drawings()
    return [d["rect"] for d in drawings if same_color(d.get("color"), color)]


def filled(path: Path, color: tuple[float, float, float]) -> list[pymupdf.Rect]:
    with pymupdf.open(path) as pdf:
        drawings = pdf.load_page(0).get_drawings()
    return [d["rect"] for d in drawings if same_color(d.get("fill"), color)]


@pytest.fixture
def source(tmp_path: Path) -> Path:
    return write_region_pdf(tmp_path / "regions.pdf")


class TestWhatARegionRemoves:
    def test_text_under_a_region_is_removed(self, source: Path):
        document = load_document(source)
        document.entities = [region(TEXT_REGION)]
        output = redacted(source, document)
        assert "SECRET" not in load_document(output).pages[0].text
        assert find_leaks(output, document) == []

    def test_photo_pixels_under_a_region_are_overwritten(self, source: Path):
        document = load_document(source)
        document.entities = [region(PHOTO_REGION)]
        output = redacted(source, document)
        with pymupdf.open(output) as pdf:
            xref = pdf.load_page(0).get_images()[0][0]
            photo = pymupdf.Pixmap(pdf.extract_image(xref)["image"])
        assert photo.pixel(20, 50) != (255, 0, 0)
        assert photo.pixel(90, 50) == (255, 0, 0)

    def test_vector_signature_fully_under_a_region_is_removed(self, source: Path):
        assert stroked(source, SIGNATURE_BLUE)
        document = load_document(source)
        document.entities = [region(SIGNATURE_REGION)]
        output = redacted(source, document)
        assert stroked(output, SIGNATURE_BLUE) == []
        assert find_leaks(output, document) == []

    def test_line_touching_a_region_is_removed_whole(self, source: Path):
        document = load_document(source)
        document.entities = [region(BORDER_REGION)]
        output = redacted(source, document)
        # The known cost of strict removal: the line vanishes outside the box too.
        assert stroked(output, BORDER_GREEN) == []

    def test_region_on_a_rotated_page_removes_the_word_under_it(self, tmp_path: Path):
        source = write_region_pdf(tmp_path / "rotated.pdf", rotation=90)
        document = load_document(source)
        secret = next(word for word in document.pages[0].words if word.text == "SECRET")
        box = secret.bbox
        document.entities = [region(BBox(box.x0 - 2, box.y0 - 2, box.x1 + 2, box.y1 + 2))]
        output = redacted(source, document)
        words = [word.text for word in load_document(output).pages[0].words]
        assert "SECRET" not in words
        assert "TEXT" in words
        assert find_leaks(output, document) == []


class TestTextBoxesKeepWhatIsBehindThem:
    def test_background_behind_a_redacted_word_survives(self, source: Path):
        document = load_document(source)
        document.entities = detect_document(structured_detector(), document)
        assert [entity.type for entity in document.entities] == [EntityType.EMAIL]
        output = redacted(source, document)
        assert CONTACT_EMAIL not in load_document(output).pages[0].text
        assert filled(output, BACKGROUND_GREY)


class TestRegionLeakCheck:
    def test_unredacted_region_reports_the_word_and_the_drawing(self, source: Path):
        document = load_document(source)
        document.entities = [region(TEXT_REGION), region(SIGNATURE_REGION)]
        leaks = [leak for leak in find_leaks(source, document) if leak.layer is LeakLayer.REGION]
        assert {leak.text for leak in leaks} == {"word 'SECRET'", "word 'TEXT'", "drawing"}

    def test_rejected_region_is_kept_and_not_reported(self, source: Path):
        document = load_document(source)
        document.entities = [region(TEXT_REGION, review=ReviewState.REJECTED)]
        output = redacted(source, document)
        assert "SECRET" in load_document(output).pages[0].text
        assert find_leaks(output, document) == []
