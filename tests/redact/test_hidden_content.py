"""Redaction of content a reader does not see, verified on the saved file.

Every test runs `redact_pdf` and then inspects the output file itself: what a
viewer shows is not evidence that the data is gone.
"""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.detect import detect_document, structured_detector
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import LeakLayer, find_leaks, redact_pdf
from anonymizer.core.types import Document

from tests.pdf_builders import CONTACT_EMAIL

IMAGE_AREA = pymupdf.Rect(100, 100, 200, 200)
# Baseline of the email line: its word box covers image rows ~38-53.
EMAIL_ORIGIN = (100, 150)


def detected(path: Path) -> Document:
    document = load_document(path)
    document.entities = detect_document(structured_detector(), document)
    return document


def redacted(path: Path) -> tuple[Path, Document]:
    document = detected(path)
    output = path.with_name(f"{path.stem}-out.pdf")
    redact_pdf(path, document, output)
    return output, document


def layers(path: Path, document: Document) -> set[LeakLayer]:
    return {leak.layer for leak in find_leaks(path, document)}


def image_pixels(page: pymupdf.Page) -> tuple[pymupdf.Pixmap, pymupdf.Pixmap | None]:
    """Return a page's first image and its transparency mask, as stored in the file."""
    xref, mask_xref = page.get_images(full=True)[0][:2]
    document = page.parent
    assert document is not None
    image = pymupdf.Pixmap(document.extract_image(xref)["image"])
    mask = pymupdf.Pixmap(document.extract_image(mask_xref)["image"]) if mask_xref else None
    return image, mask


def solid_image(color: tuple[int, int, int]) -> pymupdf.Pixmap:
    image = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 100, 100), False)
    image.set_rect(image.irect, color)
    return image


def stroke_with_transparency() -> pymupdf.Pixmap:
    """A blue horizontal stroke (rows 40-59) on a fully transparent background."""
    samples = bytearray()
    for row in range(100):
        pixel = bytes((0, 0, 255, 255)) if 40 <= row < 60 else bytes((0, 0, 0, 0))
        samples += pixel * 100
    return pymupdf.Pixmap(pymupdf.csRGB, 100, 100, bytes(samples), True)


class TestPageThumbnail:
    @pytest.fixture
    def source(self, tmp_path: Path) -> Path:
        document = pymupdf.open()
        page = document.new_page()
        page.insert_text((72, 100), f"mail {CONTACT_EMAIL}", fontname="helv", fontsize=11)
        thumbnail = document.get_new_xref()
        document.update_object(
            thumbnail,
            "<< /Type /XObject /Subtype /Image /Width 1 /Height 1"
            " /ColorSpace /DeviceRGB /BitsPerComponent 8 >>",
        )
        document.update_stream(thumbnail, b"\xff\x00\x00")
        document.xref_set_key(page.xref, "Thumb", f"{thumbnail} 0 R")
        document.save(tmp_path / "thumb.pdf")
        return tmp_path / "thumb.pdf"

    def test_leak_check_reports_a_thumbnail(self, source: Path):
        assert LeakLayer.THUMBNAIL in layers(source, detected(source))

    def test_thumbnail_is_removed(self, source: Path):
        output, document = redacted(source)
        with pymupdf.open(output) as pdf:
            assert pdf.xref_get_key(pdf.load_page(0).xref, "Thumb")[0] == "null"
        assert find_leaks(output, document) == []


class TestContentOutsideTheVisibleArea:
    @pytest.fixture
    def source(self, tmp_path: Path) -> Path:
        """Four pages, each with visible text and text a reader never sees.

        0: crop box shows the top half; 1: media box does not start at 0,0;
        2: cropped and rotated; 3: no crop box, text beyond the media box.
        """
        document = pymupdf.open()
        for _ in range(4):
            document.new_page()
        for index in range(4):
            page = document[index]
            page.insert_text((100, 100), f"VISIBLE{index}", fontname="helv", fontsize=12)
            page.insert_text((100, 700), f"HIDDEN{index}", fontname="helv", fontsize=12)
            page.insert_text((100, 1500), f"BEYOND{index}", fontname="helv", fontsize=12)
        document.xref_set_key(document[0].xref, "CropBox", "[0 442 595 842]")
        document.xref_set_key(document[1].xref, "MediaBox", "[100 200 695 1042]")
        document.xref_set_key(document[1].xref, "CropBox", "[100 642 695 1042]")
        document.xref_set_key(document[2].xref, "CropBox", "[0 442 595 842]")
        document.xref_set_key(document[2].xref, "Rotate", "90")
        document.save(tmp_path / "off-page.pdf")
        return tmp_path / "off-page.pdf"

    def test_ingest_sees_only_the_visible_text(self, source: Path):
        words = [[word.text for word in page.words] for page in load_document(source).pages]
        assert words == [["VISIBLE0"], ["VISIBLE1"], ["VISIBLE2"], ["VISIBLE3", "HIDDEN3"]]

    def test_leak_check_reports_text_a_reader_never_sees(self, source: Path):
        hidden = {leak.text for leak in find_leaks(source, detected(source))}
        assert hidden >= {"HIDDEN0", "HIDDEN1", "HIDDEN2", "BEYOND0", "BEYOND3"}

    def test_hidden_text_is_removed_and_visible_text_kept(self, source: Path):
        output, document = redacted(source)
        assert find_leaks(output, document) == []
        words = [[word.text for word in page.words] for page in load_document(output).pages]
        assert words == [["VISIBLE0"], ["VISIBLE1"], ["VISIBLE2"], ["VISIBLE3", "HIDDEN3"]]

    def test_page_geometry_is_restored_verbatim(self, source: Path):
        keys = ("MediaBox", "CropBox", "Rotate")
        with pymupdf.open(source) as pdf:
            before = [[pdf.xref_get_key(page.xref, key) for key in keys] for page in pdf]
        output, _ = redacted(source)
        with pymupdf.open(output) as pdf:
            after = [[pdf.xref_get_key(page.xref, key) for key in keys] for page in pdf]
        assert after == before


class TestImagesUnderARedactionBox:
    def test_shared_image_is_redacted_only_where_the_box_is(self, tmp_path: Path):
        document = pymupdf.open()
        document.new_page()
        document.new_page()
        first, second = document[0], document[1]
        image_xref = first.insert_image(IMAGE_AREA, pixmap=solid_image((255, 0, 0)))
        second.insert_image(IMAGE_AREA, xref=image_xref)
        first.insert_text(EMAIL_ORIGIN, CONTACT_EMAIL, fontname="helv", fontsize=12)
        document.save(tmp_path / "shared.pdf")

        output, document_model = redacted(tmp_path / "shared.pdf")
        assert find_leaks(output, document_model) == []
        with pymupdf.open(output) as pdf:
            redacted_image, _ = image_pixels(pdf.load_page(0))
            untouched_image, _ = image_pixels(pdf.load_page(1))
        assert redacted_image.pixel(10, 45) != (255, 0, 0)
        assert redacted_image.pixel(10, 90) == (255, 0, 0)
        assert untouched_image.pixel(10, 45) == (255, 0, 0)

    def test_transparency_mask_keeps_no_shape_under_the_box(self, tmp_path: Path):
        document = pymupdf.open()
        page = document.new_page()
        page.insert_image(IMAGE_AREA, pixmap=stroke_with_transparency())
        page.insert_text(EMAIL_ORIGIN, CONTACT_EMAIL, fontname="helv", fontsize=12)
        document.save(tmp_path / "transparent.pdf")

        output, _ = redacted(tmp_path / "transparent.pdf")
        with pymupdf.open(output) as pdf:
            image, mask = image_pixels(pdf.load_page(0))
        assert mask is not None
        # Under the box: colour blanked, mask uniform, so the stroke's shape is gone.
        assert image.pixel(10, 45) != (0, 0, 255)
        assert {mask.pixel(10, row)[0] for row in (39, 41, 45, 52)} == {mask.pixel(10, 39)[0]}
        # Outside the box the transparency survives unchanged.
        assert mask.pixel(10, 20)[0] == 0
        assert mask.pixel(10, 80)[0] == 0


def test_text_inside_a_form_xobject_is_removed(tmp_path: Path):
    wrapped = pymupdf.open()
    wrapped_page = wrapped.new_page()
    wrapped_page.insert_text((100, 100), f"mail {CONTACT_EMAIL}", fontname="helv", fontsize=12)
    document = pymupdf.open()
    page = document.new_page()
    page.show_pdf_page(page.rect, wrapped, 0)
    document.save(tmp_path / "wrapped.pdf")
    with pymupdf.open(tmp_path / "wrapped.pdf") as pdf:
        assert pdf.load_page(0).get_xobjects()

    output, document_model = redacted(tmp_path / "wrapped.pdf")
    assert CONTACT_EMAIL not in load_document(output).pages[0].text
    assert find_leaks(output, document_model) == []
