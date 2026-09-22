"""Tests for PDF text-layer extraction."""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.detect import structured_detector
from anonymizer.core.ingest import load_document, normalize_text, pages_needing_ocr
from anonymizer.core.types import EntityType


class TestNormalization:
    def test_composes_decomposed_characters(self):
        assert normalize_text("Novák") == "Novák"

    def test_leaves_composed_characters_unchanged(self):
        assert normalize_text("Novák") == "Novák"

    def test_normalization_makes_lengths_comparable(self):
        assert len(normalize_text("Novák")) == len("Novák")


class TestLoadDocument:
    def test_reads_one_page_with_words(self, single_page_pdf: Path):
        document = load_document(single_page_pdf)
        page = document.pages[0]
        assert len(document.pages) == 1
        assert page.has_text_layer
        assert page.words
        assert "Jan Novák" in page.text

    def test_records_only_the_file_name(self, single_page_pdf: Path):
        document = load_document(single_page_pdf)
        assert document.source_name == "single.pdf"
        assert str(single_page_pdf.parent) not in str(document.to_dict())

    def test_records_language_when_given(self, single_page_pdf: Path):
        assert load_document(single_page_pdf, language="cs").language == "cs"

    def test_page_geometry_matches_the_pdf(self, single_page_pdf: Path):
        page = load_document(single_page_pdf).pages[0]
        assert (round(page.width), round(page.height)) == (595, 842)

    def test_word_offsets_match_the_page_text(self, single_page_pdf: Path):
        page = load_document(single_page_pdf).pages[0]
        for word in page.words:
            assert page.text[word.start : word.end] == word.text

    def test_words_stay_inside_the_page_rectangle(self, single_page_pdf: Path):
        page = load_document(single_page_pdf).pages[0]
        for word in page.words:
            assert word.bbox.x0 >= 0 and word.bbox.x1 <= page.width
            assert word.bbox.y0 >= 0 and word.bbox.y1 <= page.height

    def test_lines_are_separated_in_reading_order(self, single_page_pdf: Path):
        text = load_document(single_page_pdf).pages[0].text
        assert text.index("Jmeno") < text.index("900101") < text.index("2000145399")

    def test_multi_page_documents_keep_page_indices(self, two_page_pdf: Path):
        document = load_document(two_page_pdf)
        assert [page.index for page in document.pages] == [0, 1]
        assert "Strana" in document.pages[1].text

    def test_rotated_page_boxes_are_mapped_into_the_rotated_rectangle(self, rotated_pdf: Path):
        page = load_document(rotated_pdf).pages[0]
        assert (round(page.width), round(page.height)) == (842, 595)
        for word in page.words:
            assert word.bbox.x1 <= page.width
            assert word.bbox.y1 <= page.height

    def test_page_without_text_layer_is_flagged_for_ocr(self, empty_pdf: Path):
        document = load_document(empty_pdf)
        assert not document.pages[0].has_text_layer
        assert pages_needing_ocr(document) == [0]

    def test_page_with_text_layer_needs_no_ocr(self, single_page_pdf: Path):
        assert pages_needing_ocr(load_document(single_page_pdf)) == []

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_document(tmp_path / "absent.pdf")

    def test_non_pdf_file_raises(self, tmp_path: Path):
        broken = tmp_path / "broken.pdf"
        broken.write_text("not a pdf", encoding="utf-8")
        with pytest.raises(pymupdf.FileDataError):
            load_document(broken)


class TestIngestFeedsDetection:
    def test_detectors_find_entities_in_an_extracted_page(self, single_page_pdf: Path):
        page = load_document(single_page_pdf).pages[0]
        entities = structured_detector().detect(page)
        found = {entity.type: entity.text for entity in entities}
        assert found == {
            EntityType.BIRTH_NUMBER: "900101/0007",
            EntityType.BANK_ACCOUNT: "19-2000145399/0800",
        }

    def test_detected_entities_carry_geometry_from_the_pdf(self, single_page_pdf: Path):
        page = load_document(single_page_pdf).pages[0]
        entities = structured_detector().detect(page)
        for entity in entities:
            assert entity.bboxes
            assert all(box.width > 0 and box.height > 0 for box in entity.bboxes)
