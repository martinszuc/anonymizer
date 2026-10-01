"""The leak check's OCR layer: re-reading the pixels of pages OCR read.

The engine is `InkReadingEngine`: it reports the scan's words only where the
picture still holds text-like ink, so a blanked or blacked-out word is no
longer read, as a real engine would no longer read it. Each test plants a
leak the other layers cannot see: pixels or a word on a page whose text
detection never read from the text layer.
"""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import load_document, render_page
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import LeakLayer, export_redacted, find_leaks, redact_pdf
from anonymizer.core.types import BBox, Document, EntityType, ReviewState

from tests.ocr_stand_in import InkReadingEngine
from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_scanned_pdf

PHONE = "+420 603 123 456"
LINES = [f"Kontakt: {CONTACT_EMAIL}", f"Telefon: {PHONE}", "Poznamka: nic osobniho"]
# The last line, which detection leaves alone; a region drawn over it has no text.
LAST_LINE = BBox(70, 150, 200, 166)


@pytest.fixture
def scan(tmp_path: Path) -> Path:
    return write_scanned_pdf(tmp_path / "scan.pdf", [LINES])


@pytest.fixture
def engine(tmp_path: Path) -> InkReadingEngine:
    return InkReadingEngine.reading(load_document(write_pdf(tmp_path / "original.pdf", [LINES])))


def detected(scan: Path, engine: InkReadingEngine) -> Document:
    document = load_document(scan, language="cs", ocr=engine)
    run_detection(document, build_detector("cs"))
    return document


class TestStandIn:
    """The engine the tests rely on reads ink, and only ink that looks like text."""

    def test_reads_the_whole_scan(self, scan: Path, engine: InkReadingEngine, tmp_path: Path):
        original = load_document(write_pdf(tmp_path / "again.pdf", [LINES])).pages[0]
        assert load_document(scan, ocr=engine).pages[0].text == original.text

    @pytest.mark.parametrize("fill", [(1, 1, 1), (0, 0, 0)], ids=["blank", "black"])
    def test_reads_nothing_under_a_filled_box(
        self, scan: Path, engine: InkReadingEngine, fill: tuple[int, int, int]
    ):
        with pymupdf.open(scan) as pdf:
            page = pdf[0]
            page.draw_rect(page.rect, color=fill, fill=fill)
            assert engine.read(render_page(page, 150)) == []


class TestPassing:
    def test_correct_redaction_passes_and_is_written(
        self, scan: Path, engine: InkReadingEngine, tmp_path: Path
    ):
        output = tmp_path / "out.pdf"
        assert export_redacted(scan, detected(scan, engine), output, ocr=engine) == []
        assert output.exists()

    def test_kept_value_is_not_reported(self, scan: Path, engine: InkReadingEngine, tmp_path: Path):
        document = detected(scan, engine)
        for entity in document.entities:
            if entity.type is EntityType.PHONE:
                entity.review = ReviewState.REJECTED
        output = tmp_path / "out.pdf"
        redact_pdf(scan, document, output)
        assert find_leaks(output, document, ocr=engine) == []


class TestLeaks:
    def test_unredacted_pixels_are_found_by_this_layer_alone(
        self, scan: Path, engine: InkReadingEngine
    ):
        document = detected(scan, engine)
        leaks = find_leaks(scan, document, ocr=engine)
        assert {leak.layer for leak in leaks} == {LeakLayer.OCR}
        assert {leak.text for leak in leaks} >= {CONTACT_EMAIL, PHONE}

    def test_word_left_under_a_region_is_found(self, scan: Path, engine: InkReadingEngine):
        document = detected(scan, engine)
        for entity in document.entities:
            entity.review = ReviewState.REJECTED
        region = document.add_region(0, LAST_LINE)
        leaks = find_leaks(scan, document, ocr=engine)
        assert [(leak.where, leak.entity_id) for leak in leaks] == [
            ("page 0 under a box", region.entity_id)
        ] * len(leaks)
        assert {leak.text for leak in leaks} == {
            "word 'Poznamka:'",
            "word 'nic'",
            "word 'osobniho'",
        }

    def test_word_merely_clipped_by_a_box_is_not_a_leak(self, scan: Path, engine: InkReadingEngine):
        # On a skewed scan an axis-aligned box clips a neighbouring line's corner:
        # here a region over only the top fifth of the last line's words.
        document = detected(scan, engine)
        for entity in document.entities:
            entity.review = ReviewState.REJECTED
        document.add_region(0, BBox(LAST_LINE.x0, LAST_LINE.y0 - 2, LAST_LINE.x1, LAST_LINE.y0 + 2))
        assert find_leaks(scan, document, ocr=engine) == []

    def test_word_written_into_the_text_layer_is_found(
        self, scan: Path, engine: InkReadingEngine, tmp_path: Path
    ):
        document = detected(scan, engine)
        output = tmp_path / "out.pdf"
        redact_pdf(scan, document, output)
        with pymupdf.open(output) as pdf:
            pdf[0].insert_text((72, 820), "stamp", fontname="helv", fontsize=8)
            pdf.save(tmp_path / "stamped.pdf")
        leaks = find_leaks(tmp_path / "stamped.pdf", document, ocr=engine)
        assert [(leak.layer, leak.text) for leak in leaks] == [
            (LeakLayer.OCR, "text layer word 'stamp'")
        ]


class TestWithoutEngine:
    def test_leak_check_refuses(self, scan: Path, engine: InkReadingEngine, tmp_path: Path):
        document = detected(scan, engine)
        output = tmp_path / "out.pdf"
        redact_pdf(scan, document, output)
        with pytest.raises(ValueError, match="pass its engine"):
            find_leaks(output, document)

    def test_export_refuses_and_writes_nothing(
        self, scan: Path, engine: InkReadingEngine, tmp_path: Path
    ):
        with pytest.raises(ValueError, match="pass its engine"):
            export_redacted(scan, detected(scan, engine), tmp_path / "out.pdf")
        assert list(tmp_path.glob("out.pdf*")) == []
        assert list(tmp_path.glob(".out.pdf*")) == []


def test_born_digital_document_needs_no_engine(tmp_path: Path):
    path = write_pdf(tmp_path / "text.pdf", [LINES])
    document = load_document(path, language="cs")
    run_detection(document, build_detector("cs"))
    output = tmp_path / "out.pdf"
    assert export_redacted(path, document, output) == []


def test_mixed_document_with_a_link_passes(tmp_path: Path):
    """A born-digital page with a mailto link beside a scanned page, through the export."""
    mixed = pymupdf.open()
    mixed.new_page()
    first = mixed[0]
    first.insert_text((72, 100), f"Napiste na {CONTACT_EMAIL}", fontname="helv", fontsize=11)
    first.insert_link(
        {
            "kind": pymupdf.LINK_URI,
            "from": pymupdf.Rect(72, 88, 300, 104),
            "uri": f"mailto:{CONTACT_EMAIL}",
        }
    )
    with pymupdf.open(write_scanned_pdf(tmp_path / "scan.pdf", [LINES])) as scanned:
        mixed.insert_pdf(scanned)
    mixed.save(tmp_path / "mixed.pdf")
    mixed.close()
    original = load_document(write_pdf(tmp_path / "original.pdf", [LINES]))
    engine = InkReadingEngine.reading(original)
    document = load_document(tmp_path / "mixed.pdf", language="cs", ocr=engine)
    run_detection(document, build_detector("cs"))
    assert any(entity.surface_id for entity in document.entities)
    assert [page.raster_dpi is not None for page in document.pages] == [False, True]
    assert export_redacted(tmp_path / "mixed.pdf", document, tmp_path / "out.pdf", ocr=engine) == []
