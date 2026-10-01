"""Tests for recognising a scan that carries a few words of text layer.

A scanner or a viewer may write a page number or a stamp onto a scanned page.
The page then has a text layer, but its content is in the picture, and
treating the page as born-digital would leave everything in the picture
unread and unredacted.
"""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import load_document, pages_needing_ocr

from tests.ocr_stand_in import ScriptedEngine
from tests.pdf_builders import scan_of, write_lines, write_pdf, write_scanned_pdf

LINES = ["Jmeno: Jan Novak", "Telefon: +420 603 123 456"]
STAMP = "Naskenovano 30. 9. 2026, strana 1"


def picture_with_words(path: Path, picture: pymupdf.Rect, word_count: int) -> Path:
    """Write a page with a picture over `picture` and that many visible words over the page."""
    document = pymupdf.open()
    page = document.new_page()
    page.insert_image(picture, pixmap=scan_of([]), keep_proportion=False)
    words = [f"slovo{number}" for number in range(word_count)]
    write_lines(page, [" ".join(words[start : start + 5]) for start in range(0, word_count, 5)])
    document.save(path)
    document.close()
    return path


class TestStampedScan:
    @pytest.mark.parametrize("rotation", [0, 90])
    def test_scan_with_a_stamp_needs_ocr(self, tmp_path: Path, rotation: int):
        scan = write_scanned_pdf(tmp_path / "scan.pdf", [LINES], rotation=rotation, stamp=STAMP)
        document = load_document(scan)
        assert not document.pages[0].has_text_layer
        assert pages_needing_ocr(document) == [0]

    def test_stamp_words_are_kept_until_ocr_reads_the_page(self, tmp_path: Path):
        scan = write_scanned_pdf(tmp_path / "scan.pdf", [LINES], stamp=STAMP)
        assert load_document(scan).pages[0].text == STAMP

    def test_engine_reads_the_whole_page(self, tmp_path: Path):
        scan = write_scanned_pdf(tmp_path / "scan.pdf", [LINES], stamp=STAMP)
        original = load_document(write_pdf(tmp_path / "original.pdf", [LINES]))
        engine = ScriptedEngine.reading(original)
        page = load_document(scan, ocr=engine).pages[0]
        assert len(engine.images) == 1
        assert page.text == original.pages[0].text
        assert page.raster_dpi is not None


class TestPagesKeepingTheirTextLayer:
    FULL_PAGE = pymupdf.Rect(0, 0, 595, 842)

    def test_background_picture_under_enough_words(self, tmp_path: Path):
        page = picture_with_words(tmp_path / "background.pdf", self.FULL_PAGE, 20)
        assert load_document(page).pages[0].has_text_layer

    def test_one_word_fewer_counts_as_a_stamp(self, tmp_path: Path):
        page = picture_with_words(tmp_path / "background.pdf", self.FULL_PAGE, 19)
        assert not load_document(page).pages[0].has_text_layer

    def test_picture_covering_less_than_half_the_page(self, tmp_path: Path):
        photo = pymupdf.Rect(0, 0, 595, 400)
        assert (
            load_document(picture_with_words(tmp_path / "photo.pdf", photo, 1))
            .pages[0]
            .has_text_layer
        )

    def test_searchable_scan_with_a_short_invisible_layer(self, tmp_path: Path):
        document = pymupdf.open()
        page = document.new_page()
        page.insert_image(page.rect, pixmap=scan_of(LINES))
        write_lines(page, LINES, render_mode=3)
        document.save(tmp_path / "searchable.pdf")
        document.close()
        assert load_document(tmp_path / "searchable.pdf").pages[0].has_text_layer


def test_words_beside_the_picture_do_not_count(tmp_path: Path):
    # The picture covers the lower 60 % of the page; the words sit above it.
    page = picture_with_words(tmp_path / "beside.pdf", pymupdf.Rect(0, 330, 595, 842), 30)
    assert not load_document(page).pages[0].has_text_layer
