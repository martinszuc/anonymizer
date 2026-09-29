"""Tests for blackbox redaction and the leakage check on its output."""

import shutil
from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.detect import detect_document, structured_detector
from anonymizer.core.ingest import extract_surfaces, load_document
from anonymizer.core.redact import LeakLayer, find_leaks, redact_pdf
from anonymizer.core.types import DetectionSource, Document, Entity, EntityType, ReviewState

from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_surfaces_pdf

PHONE = "+420 603 123 456"
LINES = ["Jan Novak", f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "KEEP this line"]


def detected(path: Path) -> Document:
    document = load_document(path)
    document.entities = detect_document(structured_detector(), document)
    return document


def output_text(path: Path) -> str:
    return "\n".join(page.text for page in load_document(path).pages)


def layers(leaks: list) -> set[LeakLayer]:
    return {leak.layer for leak in leaks}


@pytest.fixture(params=[0, 90], ids=["upright", "rotated"])
def contact_pdf(request: pytest.FixtureRequest, tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "contact.pdf", [LINES], rotation=request.param)


class TestPageText:
    def test_detected_entities_are_removed_and_the_rest_kept(self, contact_pdf: Path):
        document = detected(contact_pdf)
        output = contact_pdf.with_name("out.pdf")
        redact_pdf(contact_pdf, document, output)
        text = output_text(output)
        assert CONTACT_EMAIL not in text
        assert "603" not in text
        assert "KEEP" in text and "Novak" in text
        assert find_leaks(output, document) == []

    def test_redacted_area_is_filled_black(self, contact_pdf: Path):
        document = detected(contact_pdf)
        output = contact_pdf.with_name("out.pdf")
        redact_pdf(contact_pdf, document, output)
        with pymupdf.open(output) as pdf:
            fills = [drawing.get("fill") for drawing in pdf.load_page(0).get_drawings()]
        assert (0.0, 0.0, 0.0) in fills

    def test_one_box_per_line_hides_how_the_value_was_grouped(self, contact_pdf: Path):
        document = detected(contact_pdf)
        phone = next(entity for entity in document.entities if entity.type is EntityType.PHONE)
        assert len(phone.bboxes) == 4
        document.entities = [phone]
        output = contact_pdf.with_name("out.pdf")
        redact_pdf(contact_pdf, document, output)
        with pymupdf.open(output) as pdf:
            black = [d for d in pdf.load_page(0).get_drawings() if d.get("fill") == (0.0, 0.0, 0.0)]
        assert len(black) == 1

    def test_entity_crossing_a_line_break_gets_one_box_per_line(self, tmp_path: Path):
        source = write_pdf(tmp_path / "two-lines.pdf", [["name Jan", "Novak here"]])
        document = load_document(source)
        text = document.pages[0].text
        start, end = text.index("Jan"), text.index("Novak") + len("Novak")
        document.entities = [
            Entity(type=EntityType.PERSON, page_index=0, start=start, end=end, text=text[start:end])
        ]
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        with pymupdf.open(output) as pdf:
            black = [d for d in pdf.load_page(0).get_drawings() if d.get("fill") == (0.0, 0.0, 0.0)]
        assert len(black) == 2
        assert "name" in output_text(output) and "here" in output_text(output)

    def test_rejected_entity_is_kept(self, contact_pdf: Path):
        document = detected(contact_pdf)
        email = next(entity for entity in document.entities if entity.type is EntityType.EMAIL)
        email.review = ReviewState.REJECTED
        output = contact_pdf.with_name("out.pdf")
        redact_pdf(contact_pdf, document, output)
        assert CONTACT_EMAIL in output_text(output)
        assert find_leaks(output, document) == []

    def test_entity_added_in_review_is_redacted(self, contact_pdf: Path):
        document = detected(contact_pdf)
        page = document.pages[0]
        start = page.text.index("Jan Novak")
        document.entities.append(
            Entity(
                type=EntityType.PERSON,
                page_index=0,
                start=start,
                end=start + len("Jan Novak"),
                text="Jan Novak",
                source=DetectionSource.MANUAL,
                review=ReviewState.CONFIRMED,
            )
        )
        output = contact_pdf.with_name("out.pdf")
        redact_pdf(contact_pdf, document, output)
        assert "Novak" not in output_text(output)
        assert find_leaks(output, document) == []


class TestSurfaces:
    @pytest.fixture
    def surfaces_pdf(self, tmp_path: Path) -> Path:
        return write_surfaces_pdf(tmp_path / "surfaces.pdf")

    def test_every_surface_is_cleared_without_waiting_for_detection(self, surfaces_pdf: Path):
        document = load_document(surfaces_pdf)
        output = surfaces_pdf.with_name("out.pdf")
        redact_pdf(surfaces_pdf, document, output)
        with pymupdf.open(output) as pdf:
            assert extract_surfaces(pdf) == []

    def test_cleared_output_passes_the_leak_check(self, surfaces_pdf: Path):
        document = detected(surfaces_pdf)
        assert any(not entity.in_page_text for entity in document.entities)
        output = surfaces_pdf.with_name("out.pdf")
        redact_pdf(surfaces_pdf, document, output)
        assert find_leaks(output, document) == []

    def test_structure_tree_references_do_not_keep_removed_links_alive(self, surfaces_pdf: Path):
        output = surfaces_pdf.with_name("out.pdf")
        redact_pdf(surfaces_pdf, load_document(surfaces_pdf), output)
        with pymupdf.open(output) as pdf:
            objects = "".join(pdf.xref_object(xref) for xref in range(1, pdf.xref_length()))
            assert pdf.xref_get_key(pdf.pdf_catalog(), "StructTreeRoot")[0] == "null"
        assert "mailto:" not in objects

    def test_links_within_the_document_are_kept(self, surfaces_pdf: Path):
        output = surfaces_pdf.with_name("out.pdf")
        redact_pdf(surfaces_pdf, load_document(surfaces_pdf), output)
        with pymupdf.open(output) as pdf:
            kinds = [link["kind"] for link in pdf.load_page(0).get_links()]
        assert kinds == [pymupdf.LINK_GOTO]

    def test_source_file_is_left_untouched(self, surfaces_pdf: Path):
        before = surfaces_pdf.read_bytes()
        redact_pdf(surfaces_pdf, load_document(surfaces_pdf), surfaces_pdf.with_name("out.pdf"))
        assert surfaces_pdf.read_bytes() == before


class TestLeakCheck:
    def test_unredacted_file_leaks_in_every_layer(self, tmp_path: Path):
        source = write_surfaces_pdf(tmp_path / "surfaces.pdf")
        document = detected(source)
        assert layers(find_leaks(source, document)) >= {LeakLayer.SURFACE, LeakLayer.OBJECT}

    def test_page_text_layer_reports_text_left_on_a_page(self, tmp_path: Path):
        source = write_pdf(tmp_path / "contact.pdf", [LINES])
        document = detected(source)
        page_leaks = [leak for leak in find_leaks(source, document) if leak.layer == "page_text"]
        assert {leak.text for leak in page_leaks} == {CONTACT_EMAIL, PHONE}

    def test_object_layer_catches_a_carrier_the_surface_scan_does_not_list(self, tmp_path: Path):
        source = write_pdf(tmp_path / "contact.pdf", [LINES])
        document = detected(source)
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        with pymupdf.open(output) as pdf:
            pdf.xref_set_key(pdf.pdf_catalog(), "Note", pymupdf.get_pdf_str(CONTACT_EMAIL))
            pdf.save(tmp_path / "tampered.pdf")
        leaks = find_leaks(tmp_path / "tampered.pdf", document)
        assert LeakLayer.OBJECT in layers(leaks)
        assert LeakLayer.SURFACE not in layers(leaks)

    def test_file_byte_layer_catches_a_revision_an_incremental_save_left(self, tmp_path: Path):
        source = write_pdf(tmp_path / "contact.pdf", [LINES])
        document = detected(source)
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        revised = tmp_path / "revised.pdf"
        with pymupdf.open(output) as pdf:
            pdf.xref_set_key(pdf.pdf_catalog(), "Note", pymupdf.get_pdf_str(CONTACT_EMAIL))
            pdf.save(revised)
        # The update removes the key, but the earlier catalog revision stays in the file.
        with pymupdf.open(revised) as pdf:
            pdf.xref_set_key(pdf.pdf_catalog(), "Note", "null")
            pdf.saveIncr()
        leaks = find_leaks(revised, document)
        assert layers(leaks) == {LeakLayer.FILE_BYTES}


class TestPreconditions:
    def test_refuses_to_overwrite_the_source(self, tmp_path: Path):
        source = write_pdf(tmp_path / "contact.pdf", [LINES])
        with pytest.raises(ValueError, match="must not overwrite"):
            redact_pdf(source, load_document(source), source)

    def test_rejects_a_document_from_another_file_with_the_same_page_count(self, tmp_path: Path):
        source = write_pdf(tmp_path / "contact.pdf", [LINES])
        other = write_pdf(tmp_path / "other.pdf", [["different", "content"]])
        with pytest.raises(ValueError, match="different file"):
            redact_pdf(other, load_document(source), tmp_path / "out.pdf")

    def test_rejects_a_document_without_a_fingerprint(self, tmp_path: Path):
        source = write_pdf(tmp_path / "contact.pdf", [LINES])
        document = load_document(source)
        document.fingerprint = None
        with pytest.raises(ValueError, match="no fingerprint"):
            redact_pdf(source, document, tmp_path / "out.pdf")

    def test_redactable_entity_without_geometry_fails_loudly(self, tmp_path: Path):
        source = write_pdf(tmp_path / "blank.pdf", [[]])
        document = load_document(source)
        document.entities.append(
            Entity(type=EntityType.EMAIL, page_index=0, start=0, end=5, text="a@b.c")
        )
        with pytest.raises(ValueError, match="no geometry"):
            redact_pdf(source, document, tmp_path / "out.pdf")


def test_copying_the_source_does_not_count_as_redaction(tmp_path: Path):
    source = write_pdf(tmp_path / "contact.pdf", [LINES])
    document = detected(source)
    copy = tmp_path / "copy.pdf"
    shutil.copy(source, copy)
    assert find_leaks(copy, document)


class TestNumbersInPdfSyntax:
    """A short number also occurs inside the numbers PDF syntax is made of."""

    ZIP = "20001"

    def _redacted(self, tmp_path: Path, extra_keys: dict[str, str]) -> tuple[Path, Document]:
        source = write_pdf(tmp_path / "zip.pdf", [[f"PSC {self.ZIP}", "KEEP"]])
        document = load_document(source)
        page = document.pages[0]
        start = page.text.index(self.ZIP)
        end = start + len(self.ZIP)
        zip_code = Entity(
            type=EntityType.ADDRESS,
            page_index=0,
            start=start,
            end=end,
            text=self.ZIP,
            bboxes=page.bboxes_for_span(start, end),
            source=DetectionSource.MODEL,
        )
        document.entities = [zip_code]
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        with pymupdf.open(output) as pdf:
            xref = pdf.load_page(0).xref
            for key, value in extra_keys.items():
                pdf.xref_set_key(xref, key, value)
            pdf.save(tmp_path / "planted.pdf")
        planted = tmp_path / "planted.pdf"
        # Guard the fixture: the planted value must really be in the file.
        raw = planted.read_bytes()
        assert all(value.encode() in raw for value in extra_keys.values())
        return planted, document

    @pytest.mark.parametrize("operand", ["9.200012", "120001", "1.20001", "20001.5"])
    def test_number_inside_a_longer_number_is_not_a_leak(self, tmp_path: Path, operand: str):
        planted, document = self._redacted(tmp_path, {"Pad": operand})
        assert find_leaks(planted, document) == []

    @pytest.mark.parametrize(
        "literal",
        ["(20001)", "(PSC 20001.)", "(20001 12)", "(ZIP:20001)", "(2 0 0 0 1)", "(20001-12)"],
        ids=["alone", "sentence-end", "space-then-digits", "after-colon", "spaced", "hyphen"],
    )
    def test_the_number_stored_as_text_is_a_leak(self, tmp_path: Path, literal: str):
        planted, document = self._redacted(tmp_path, {"Note": literal})
        assert layers(find_leaks(planted, document)) == {LeakLayer.OBJECT, LeakLayer.FILE_BYTES}

    def test_letters_keep_matching_inside_words(self, tmp_path: Path):
        source = write_pdf(tmp_path / "name.pdf", [["Jan Novak", "KEEP"]])
        document = load_document(source)
        page = document.pages[0]
        start = page.text.index("Novak")
        name = Entity(
            type=EntityType.PERSON,
            page_index=0,
            start=start,
            end=start + 5,
            text="Novak",
            bboxes=page.bboxes_for_span(start, start + 5),
        )
        document.entities = [name]
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        with pymupdf.open(output) as pdf:
            pdf.xref_set_key(pdf.load_page(0).xref, "Note", "(xNovakx)")
            pdf.save(tmp_path / "planted.pdf")
        leaks = find_leaks(tmp_path / "planted.pdf", document)
        assert layers(leaks) == {LeakLayer.OBJECT, LeakLayer.FILE_BYTES}
