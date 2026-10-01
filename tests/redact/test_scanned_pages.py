"""Redaction of pages OCR read, verified on the saved file.

The stand-in engine reports the words of each scan's born-digital original
(`tests.ocr_stand_in`), so the boxes are where a perfect engine would put
them. Ink is counted in the image data stored in the output
(`tests.pixels`), for every way the fixtures store a scan's picture.
"""

from pathlib import Path
from typing import Any

import pymupdf
import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import export_redacted, redact_pdf
from anonymizer.core.types import BBox, Document, EntityType, ReviewState

from tests.ocr_stand_in import InkReadingEngine, ScriptedEngine
from tests.pdf_builders import (
    CONTACT_EMAIL,
    SCAN_PICTURES,
    scan_of,
    write_lines,
    write_pdf,
    write_scanned_pdf,
)
from tests.pixels import ink

PHONE = "+420 603 123 456"
LINES = [f"Kontakt: {CONTACT_EMAIL}", f"Telefon: {PHONE}", "Poznamka: nic osobniho"]
# Where the last line's ink lies, in unrotated page points; nothing there is redacted.
UNTOUCHED_AREA = pymupdf.Rect(70, 150, 200, 166)
STAMP = "Naskenovano 30. 9. 2026"

VARIANTS: dict[str, dict[str, Any]] = {kind: {"picture": kind} for kind in SCAN_PICTURES} | {
    "rotated": {"rotation": 90}
}


def read_by_ocr(scan: Path, tmp_path: Path, rotation: int = 0) -> Document:
    """Load a scan of `LINES` through the stand-in engine and detect."""
    original = load_document(write_pdf(tmp_path / "original.pdf", [LINES], rotation=rotation))
    document = load_document(scan, language="cs", ocr=ScriptedEngine.reading(original))
    run_detection(document, build_detector("cs"))
    return document


def redacted_areas(document: Document, page: pymupdf.Page) -> list[pymupdf.Rect]:
    return [
        bbox_to_unrotated_rect(box, page) for entity in document.entities for box in entity.bboxes
    ]


@pytest.fixture(params=list(VARIANTS), ids=list(VARIANTS))
def scan(request: pytest.FixtureRequest, tmp_path: Path) -> tuple[Path, Document]:
    options = VARIANTS[request.param]
    path = write_scanned_pdf(tmp_path / "scan.pdf", [LINES], **options)
    return path, read_by_ocr(path, tmp_path, rotation=options.get("rotation", 0))


class TestFixture:
    """The starting state the redaction tests rely on."""

    def test_detection_found_the_values(self, scan: tuple[Path, Document]):
        _, document = scan
        assert sorted(entity.text or "" for entity in document.entities) == [PHONE, CONTACT_EMAIL]

    def test_ink_lies_under_every_box_and_in_the_untouched_line(self, scan: tuple[Path, Document]):
        path, document = scan
        with pymupdf.open(path) as pdf:
            page = pdf[0]
            assert all(ink(page, area) for area in redacted_areas(document, page))
            assert ink(page, UNTOUCHED_AREA) > 0

    @pytest.mark.parametrize(
        ("picture", "key", "value"),
        [
            ("jpeg", "Filter", "/DCTDecode"),
            ("cmyk_jpeg", "Filter", "/DCTDecode"),
            ("ccitt", "Filter", "/CCITTFaxDecode"),
            ("stencil", "ImageMask", "true"),
        ],
    )
    def test_picture_is_stored_as_named(self, tmp_path: Path, picture: str, key: str, value: str):
        path = write_scanned_pdf(tmp_path / "scan.pdf", [LINES], picture=picture)
        with pymupdf.open(path) as pdf:
            stored = [pdf.xref_get_key(image[0], key)[1] for image in pdf[0].get_images(full=True)]
        assert value in stored

    def test_strips_split_the_first_line(self, tmp_path: Path):
        path = write_scanned_pdf(tmp_path / "scan.pdf", [LINES], picture="strips")
        document = read_by_ocr(path, tmp_path)
        email = next(entity for entity in document.entities if entity.type is EntityType.EMAIL)
        with pymupdf.open(path) as pdf:
            top, bottom = (pymupdf.Rect(info["bbox"]) for info in pdf[0].get_image_info())
        assert top.y1 == pytest.approx(bottom.y0)
        assert email.bboxes[0].y0 < top.y1 < email.bboxes[0].y1


class TestPixels:
    def test_ink_under_every_box_is_removed(self, scan: tuple[Path, Document], tmp_path: Path):
        path, document = scan
        output = tmp_path / "out.pdf"
        redact_pdf(path, document, output)
        with pymupdf.open(output) as pdf:
            page = pdf[0]
            left = [ink(page, area) for area in redacted_areas(document, page)]
        assert left == [0] * len(left)

    def test_ink_elsewhere_is_kept(self, scan: tuple[Path, Document], tmp_path: Path):
        path, document = scan
        output = tmp_path / "out.pdf"
        redact_pdf(path, document, output)
        with pymupdf.open(path) as before, pymupdf.open(output) as after:
            assert ink(after[0], UNTOUCHED_AREA) == ink(before[0], UNTOUCHED_AREA)


class TestTextLayer:
    @pytest.fixture
    def scan_with_text(self, tmp_path: Path) -> Path:
        """A scan whose text layer holds a stamp, text under the picture and white text."""
        document = pymupdf.open()
        page = document.new_page()
        page.insert_text((72, 400), "hidden under the picture", fontname="helv")
        SCAN_PICTURES["flate"](document, page, scan_of(LINES))
        page.insert_text((72, 820), STAMP, fontname="helv", fontsize=8)
        page.insert_text((72, 500), "white text", fontname="helv", color=(1, 1, 1))
        document.save(tmp_path / "scan.pdf")
        document.close()
        return tmp_path / "scan.pdf"

    def test_fixture_has_three_kinds_of_text_and_needs_ocr(self, scan_with_text: Path):
        page = load_document(scan_with_text).pages[0]
        assert not page.has_text_layer
        for text in ("hidden under the picture", STAMP, "white text"):
            assert text in page.text

    def test_page_read_by_ocr_loses_its_whole_text_layer(
        self, scan_with_text: Path, tmp_path: Path
    ):
        output = tmp_path / "out.pdf"
        redact_pdf(scan_with_text, read_by_ocr(scan_with_text, tmp_path), output)
        with pymupdf.open(scan_with_text) as before, pymupdf.open(output) as after:
            assert after[0].get_text("words") == []
            assert ink(after[0], UNTOUCHED_AREA) == ink(before[0], UNTOUCHED_AREA)

    def test_page_not_read_by_ocr_keeps_its_text(self, scan_with_text: Path, tmp_path: Path):
        document = load_document(scan_with_text)
        output = tmp_path / "out.pdf"
        redact_pdf(scan_with_text, document, output)
        with pymupdf.open(output) as pdf:
            assert STAMP in pdf[0].get_text()

    def test_born_digital_page_beside_it_keeps_its_text(self, tmp_path: Path):
        mixed = pymupdf.open()
        write_lines(mixed.new_page(), ["Strana jedna"])
        with pymupdf.open(
            write_scanned_pdf(tmp_path / "scan.pdf", [LINES], stamp=STAMP)
        ) as scanned:
            mixed.insert_pdf(scanned)
        mixed.save(tmp_path / "mixed.pdf")
        mixed.close()
        original = load_document(write_pdf(tmp_path / "original.pdf", [["Strana jedna"], LINES]))
        engine = ScriptedEngine([ScriptedEngine.reading(original).pages[1]])
        document = load_document(tmp_path / "mixed.pdf", ocr=engine)
        output = tmp_path / "out.pdf"
        redact_pdf(tmp_path / "mixed.pdf", document, output)
        with pymupdf.open(output) as pdf:
            assert pdf[1].get_text("words") == []
        assert load_document(output).pages[0].text == "Strana jedna"


def test_export_with_mixed_decisions_on_a_scanned_page(tmp_path: Path):
    """A kept phone, a redacted email and a drawn region, through the leak-checked export.

    The leak check re-reads the page, so the engine must react to the pixels.
    """
    path = write_scanned_pdf(tmp_path / "scan.pdf", [LINES])
    engine = InkReadingEngine.reading(load_document(write_pdf(tmp_path / "original.pdf", [LINES])))
    document = load_document(path, language="cs", ocr=engine)
    run_detection(document, build_detector("cs"))
    phone = next(entity for entity in document.entities if entity.type is EntityType.PHONE)
    phone.review = ReviewState.REJECTED
    region = document.add_region(0, BBox(*UNTOUCHED_AREA))
    output = tmp_path / "out.pdf"
    assert export_redacted(path, document, output, ocr=engine) == []
    with pymupdf.open(path) as before, pymupdf.open(output) as after:
        page = after[0]
        email = next(entity for entity in document.entities if entity.type is EntityType.EMAIL)
        assert ink(page, bbox_to_unrotated_rect(email.bboxes[0], page)) == 0
        assert ink(page, bbox_to_unrotated_rect(region.bboxes[0], page)) == 0
        kept = [bbox_to_unrotated_rect(box, page) for box in phone.bboxes]
        assert [ink(page, area) for area in kept] == [ink(before[0], area) for area in kept]
        assert page.get_text("words") == []
