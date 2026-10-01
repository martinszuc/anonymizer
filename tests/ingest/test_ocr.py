"""Tests for reading scanned pages through an OCR engine.

The engine is a stand-in that reports the words of the scan's born-digital
original (`tests.ocr_stand_in`), so every expected box and text is known
independently of the code under test.
"""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import (
    DEFAULT_OCR_DPI,
    OCR_BOX_MARGIN,
    OcrWord,
    PageImage,
    load_document,
    pages_needing_ocr,
)
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import redact_pdf
from anonymizer.core.session import load_session, save_session
from anonymizer.core.types import BBox, Document, EntityType

from tests.ocr_stand_in import ScriptedEngine, ScriptedWord
from tests.pdf_builders import INK_LEVEL, write_pdf, write_scanned_pdf
from tests.pixels import ink

PHONE = "+420 603 123 456"
LINES = ["Jmeno: Jan Novak", f"Telefon: {PHONE}", "Poznamka: nic osobniho"]


def original(tmp_path: Path, rotation: int = 0) -> Document:
    return load_document(write_pdf(tmp_path / "original.pdf", [LINES], rotation=rotation))


def boxes(document: Document) -> list[list[float]]:
    return [word.bbox.to_list() for word in document.pages[0].words]


def grown(document: Document) -> list[list[float]]:
    """The document's word boxes grown as OCR boxes are: a share of the height on each side."""
    page = document.pages[0]
    result = []
    for word in page.words:
        box = word.bbox
        margin = OCR_BOX_MARGIN * box.height
        result.append(
            [
                max(box.x0 - margin, 0),
                max(box.y0 - margin, 0),
                min(box.x1 + margin, page.width),
                min(box.y1 + margin, page.height),
            ]
        )
    return result


@pytest.fixture
def scan(tmp_path: Path) -> Path:
    return write_scanned_pdf(tmp_path / "scan.pdf", [LINES])


@pytest.fixture
def blank_scan(tmp_path: Path) -> Path:
    return write_scanned_pdf(tmp_path / "blank.pdf", [[]])


def read_with(path: Path, words: list[ScriptedWord]) -> Document:
    return load_document(path, ocr=ScriptedEngine([words]))


class TestWithoutEngine:
    def test_scan_has_no_words_and_needs_ocr(self, scan: Path):
        document = load_document(scan)
        page = document.pages[0]
        assert page.words == []
        assert not page.has_text_layer
        assert page.raster_dpi is None
        assert pages_needing_ocr(document) == [0]


class TestScannedPage:
    def test_text_and_words_equal_the_original(self, scan: Path, tmp_path: Path):
        expected = original(tmp_path)
        document = load_document(scan, ocr=ScriptedEngine.reading(expected))
        page = document.pages[0]
        assert page.text == expected.pages[0].text
        assert [word.text for word in page.words] == [word.text for word in expected.pages[0].words]
        assert all(page.text[word.start : word.end] == word.text for word in page.words)

    def test_page_is_marked_as_read_by_ocr(self, scan: Path, tmp_path: Path):
        document = load_document(scan, ocr=ScriptedEngine.reading(original(tmp_path)))
        page = document.pages[0]
        assert not page.has_text_layer
        assert page.raster_dpi == DEFAULT_OCR_DPI
        assert pages_needing_ocr(document) == []

    @pytest.mark.parametrize("dpi", [150, 300])
    def test_boxes_convert_from_pixels_at_the_chosen_resolution(
        self, scan: Path, tmp_path: Path, dpi: int
    ):
        expected = original(tmp_path)
        document = load_document(scan, ocr=ScriptedEngine.reading(expected), ocr_dpi=dpi)
        assert document.pages[0].raster_dpi == dpi
        assert boxes(document) == [pytest.approx(box) for box in grown(expected)]

    def test_engine_receives_the_page_rendered_at_the_resolution(self, scan: Path, tmp_path: Path):
        expected = original(tmp_path)
        engine = ScriptedEngine.reading(expected)
        load_document(scan, ocr=engine, ocr_dpi=150)
        (image,) = engine.images
        # A4 is 595 x 842 points; 1754.2 pixels are rounded up to whole ones.
        assert (image.width, image.height, image.dpi) == (1240, 1755, 150)
        assert len(image.samples) == image.width * image.height * 3
        # The first word's ink is in the picture where its box says.
        box = expected.pages[0].words[0].bbox
        scale = 150 / 72
        pixels = [
            image.samples[(y * image.width + x) * 3]
            for x in range(int(box.x0 * scale), int(box.x1 * scale))
            for y in range(int(box.y0 * scale), int(box.y1 * scale))
        ]
        assert min(pixels) < INK_LEVEL

    def test_detection_finds_values_on_the_scan(self, scan: Path, tmp_path: Path):
        document = load_document(
            scan, language="cs", ocr=ScriptedEngine.reading(original(tmp_path))
        )
        run_detection(document, build_detector("cs"))
        phones = [entity for entity in document.entities if entity.type is EntityType.PHONE]
        assert [entity.text for entity in phones] == [PHONE]
        assert len(phones[0].bboxes) == 4


class TestRotatedScan:
    @pytest.fixture
    def rotated(self, tmp_path: Path) -> tuple[Path, Document]:
        scan = write_scanned_pdf(tmp_path / "scan.pdf", [LINES], rotation=90)
        return scan, original(tmp_path, rotation=90)

    def test_engine_receives_the_page_as_a_reader_sees_it(self, rotated: tuple[Path, Document]):
        scan, expected = rotated
        engine = ScriptedEngine.reading(expected)
        load_document(scan, ocr=engine)
        (image,) = engine.images
        assert image.width > image.height

    def test_boxes_are_in_rotated_page_space(self, rotated: tuple[Path, Document]):
        scan, expected = rotated
        document = load_document(scan, ocr=ScriptedEngine.reading(expected))
        assert boxes(document) == [pytest.approx(box) for box in grown(expected)]

    def test_redaction_boxes_land_on_the_ink(self, rotated: tuple[Path, Document], tmp_path: Path):
        scan, expected = rotated
        document = load_document(scan, language="cs", ocr=ScriptedEngine.reading(expected))
        run_detection(document, build_detector("cs"))
        output = tmp_path / "out.pdf"
        redact_pdf(scan, document, output)
        phone_boxes = [
            box
            for entity in document.entities
            if entity.type is EntityType.PHONE
            for box in entity.bboxes
        ]
        with pymupdf.open(scan) as before, pymupdf.open(output) as after:
            areas = [bbox_to_unrotated_rect(box, before[0]) for box in phone_boxes]
            assert all(ink(before[0], area) for area in areas)
            assert [ink(after[0], area) for area in areas] == [0] * len(areas)


def test_only_pages_without_a_text_layer_are_read(tmp_path: Path):
    mixed = pymupdf.open(write_pdf(tmp_path / "text.pdf", [["Strana jedna"]]))
    with pymupdf.open(write_scanned_pdf(tmp_path / "scan.pdf", [LINES])) as scanned:
        mixed.insert_pdf(scanned)
    mixed.save(tmp_path / "mixed.pdf")
    mixed.close()
    engine = ScriptedEngine.reading(original(tmp_path))
    document = load_document(tmp_path / "mixed.pdf", ocr=engine)
    first, second = document.pages
    assert len(engine.images) == 1
    assert (first.has_text_layer, first.raster_dpi, first.text) == (True, None, "Strana jedna")
    assert "Telefon" in second.text


class TestEngineOutput:
    BOX = BBox(72, 90, 150, 104)

    def test_text_is_normalized_and_czech_letters_survive(self, blank_scan: Path):
        page = read_with(
            blank_scan,
            [ScriptedWord("Novák", self.BOX), ScriptedWord("Řehoř Ůžasný", self.BOX)],
        ).pages[0]
        assert page.text == "Novák Řehoř Ůžasný"
        assert all(page.text[word.start : word.end] == word.text for word in page.words)

    def test_lines_are_ordered_by_block_and_line_and_words_kept_in_line_order(
        self, blank_scan: Path
    ):
        page = read_with(
            blank_scan,
            [
                ScriptedWord("third", self.BOX, block=1, line=2),
                ScriptedWord("first", self.BOX, block=0, line=0),
                ScriptedWord("second", self.BOX, block=0, line=1),
                ScriptedWord("again", self.BOX, block=0, line=1),
            ],
        ).pages[0]
        assert page.text == "first\nsecond again\n\nthird"

    def test_surrounding_whitespace_is_dropped_and_blank_words_skipped(self, blank_scan: Path):
        page = read_with(
            blank_scan,
            [
                ScriptedWord(" Jan ", self.BOX),
                ScriptedWord("  ", self.BOX),
                ScriptedWord("Novak", self.BOX),
            ],
        ).pages[0]
        assert page.text == "Jan Novak"
        assert len(page.words) == 2

    def test_boxes_are_grown_by_a_share_of_their_height_on_each_side(self, blank_scan: Path):
        page = read_with(blank_scan, [ScriptedWord("Novák", BBox(100, 200, 160, 210))]).pages[0]
        margin = OCR_BOX_MARGIN * 10
        assert page.words[0].bbox.to_list() == pytest.approx(
            [100 - margin, 200 - margin, 160 + margin, 210 + margin]
        )

    def test_boxes_are_clipped_to_the_page_and_their_corners_ordered(self, blank_scan: Path):
        class SwappedCorners:
            """Reports one word with its corners swapped, reaching past the bottom right."""

            def read(self, image: PageImage) -> list[OcrWord]:
                right, bottom = image.width, image.height
                box = (right + 50, bottom + 9, right - 100, bottom - 30)
                return [OcrWord("edge", box, 0.9, block=0, line=0)]

        page = load_document(blank_scan, ocr=SwappedCorners(), ocr_dpi=300).pages[0]
        # The picture is 2480 x 3509 pixels at 300 DPI (3508.3 rounded up); the box
        # is 39 pixels tall before clipping.
        margin = OCR_BOX_MARGIN * 39 * 72 / 300
        assert page.words[0].bbox.to_list() == pytest.approx(
            [2380 * 72 / 300 - margin, 3479 * 72 / 300 - margin, 595, 842], abs=0.01
        )


class TestSession:
    def test_review_reopens_with_the_same_engine(self, scan: Path, tmp_path: Path):
        expected = original(tmp_path)
        document = load_document(scan, language="cs", ocr=ScriptedEngine.reading(expected))
        run_detection(document, build_detector("cs"))
        save_session(document, tmp_path / "review.json")
        reopened = load_session(
            tmp_path / "review.json", scan, ocr=ScriptedEngine.reading(expected)
        )
        assert [entity.text for entity in reopened.entities] == [
            entity.text for entity in document.entities
        ]

    def test_review_is_refused_without_the_engine(self, scan: Path, tmp_path: Path):
        document = load_document(
            scan, language="cs", ocr=ScriptedEngine.reading(original(tmp_path))
        )
        run_detection(document, build_detector("cs"))
        save_session(document, tmp_path / "review.json")
        with pytest.raises(ValueError, match="no longer cover"):
            load_session(tmp_path / "review.json", scan)
