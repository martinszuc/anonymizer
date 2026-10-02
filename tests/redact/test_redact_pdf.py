"""Tests for blackbox redaction and the leakage check on its output."""

import shutil
from collections.abc import Callable
from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.detect import detect_document, structured_detector
from anonymizer.core.ingest import extract_surfaces, load_document
from anonymizer.core.redact import Leak, LeakKind, LeakLayer, find_leaks, redact_pdf
from anonymizer.core.types import DetectionSource, Document, Entity, EntityType, ReviewState

from tests.pdf_builders import (
    ASSOCIATED_CARRIERS,
    ASSOCIATED_CONTENT,
    CONTACT_EMAIL,
    LAUNCH_CONTENT,
    LOOSE_CONTENT,
    TREE_ATTACHMENT_CONTENT,
    TREE_ATTACHMENTS,
    add_stream,
    write_associated_file_pdf,
    write_attachment_tree_pdf,
    write_attachments_pdf,
    write_other_file_carriers_pdf,
    write_pdf,
    write_surfaces_pdf,
)

PHONE = "+420 603 123 456"
LINES = ["Jan Novak", f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "KEEP this line"]
TREE_LABELS = [label for key, labels in TREE_ATTACHMENTS.items() for label in (key, *labels)]


def detected(path: Path) -> Document:
    document = load_document(path)
    document.entities = detect_document(structured_detector(), document)
    return document


def output_text(path: Path) -> str:
    return "\n".join(page.text for page in load_document(path).pages)


def layers(leaks: list) -> set[LeakLayer]:
    return {leak.layer for leak in leaks}


def streams(pdf: pymupdf.Document) -> list[bytes]:
    xrefs = range(1, pdf.xref_length())
    return [pdf.xref_stream(xref) or b"" for xref in xrefs if pdf.xref_is_stream(xref)]


def objects(pdf: pymupdf.Document) -> str:
    return "".join(pdf.xref_object(xref) for xref in range(1, pdf.xref_length()))


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

    def test_text_kept_in_one_place_and_redacted_in_another_passes(self, tmp_path: Path):
        source = write_pdf(tmp_path / "twice.pdf", [[f"to {CONTACT_EMAIL}", f"cc {CONTACT_EMAIL}"]])
        document = detected(source)
        assert len(document.entities) == 2
        document.entities[1].review = ReviewState.REJECTED
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        assert output_text(output).count(CONTACT_EMAIL) == 1
        assert find_leaks(output, document) == []

    def test_copies_beyond_those_kept_are_leaks(self, tmp_path: Path):
        lines = [f"to {CONTACT_EMAIL}", f"cc {CONTACT_EMAIL}", f"bcc {CONTACT_EMAIL}"]
        source = write_pdf(tmp_path / "thrice.pdf", [lines])
        document = detected(source)
        document.entities[2].review = ReviewState.REJECTED
        # The unredacted original still shows the two copies review did not keep:
        # one text, so one leak on its page.
        leaks = find_leaks(source, document)
        assert [(leak.layer, leak.where, leak.text) for leak in leaks] == [
            (LeakLayer.PAGE_TEXT, "page 0", CONTACT_EMAIL)
        ]
        assert leaks[0].entity_id == document.entities[0].entity_id

    def test_a_copy_kept_on_one_page_does_not_excuse_another_page(self, tmp_path: Path):
        source = write_pdf(tmp_path / "pages.pdf", [[CONTACT_EMAIL], [CONTACT_EMAIL]])
        document = detected(source)
        kept, redacted = document.entities
        kept.review = ReviewState.REJECTED
        leaks = find_leaks(source, document)
        assert [(leak.where, leak.entity_id) for leak in leaks] == [("page 1", redacted.entity_id)]

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

    def test_attachments_named_with_diacritics_are_removed(self, tmp_path: Path):
        # PyMuPDF reports these names garbled; no name may keep an attachment.
        source = write_attachments_pdf(tmp_path / "attachments.pdf")
        output = tmp_path / "out.pdf"
        redact_pdf(source, load_document(source), output)
        with pymupdf.open(output) as pdf:
            assert pdf.embfile_count() == 0
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


class TestAssociatedFiles:
    """A file referred to from `/AF` or another carrier must not survive garbage collection."""

    # ASCII prefixes of the file's name and description; the rest is stored escaped.
    LABELS = ("faktura-Vesel", "Faktura pro pan")

    @staticmethod
    def carried(path: Path, content: bytes | None = None) -> tuple[bool, list[bool]]:
        """Whether some stream holds `content`, and whether the objects hold each label."""
        with pymupdf.open(path) as pdf:
            in_streams = content is not None and any(content in data for data in streams(pdf))
            source = objects(pdf)
        return in_streams, [label in source for label in TestAssociatedFiles.LABELS]

    @pytest.mark.parametrize(
        ("carrier", "listed"),
        [
            (None, True),
            ("catalog", True),
            *((carrier, False) for carrier in ASSOCIATED_CARRIERS),
        ],
        ids=["control", "invoice", *ASSOCIATED_CARRIERS],
    )
    def test_file_and_labels_are_removed(self, tmp_path: Path, carrier: str | None, listed: bool):
        source = write_associated_file_pdf(tmp_path / "associated.pdf", carrier, listed=listed)
        assert self.carried(source, ASSOCIATED_CONTENT) == (True, [True, True])
        document = load_document(source)
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        assert self.carried(output, ASSOCIATED_CONTENT) == (False, [False, False])
        with pymupdf.open(output) as pdf:
            assert extract_surfaces(pdf) == []
        assert find_leaks(output, document) == []

    @pytest.mark.parametrize("carrier", ASSOCIATED_CARRIERS)
    def test_labels_of_an_external_file_are_removed(self, tmp_path: Path, carrier: str):
        source = write_associated_file_pdf(tmp_path / "external.pdf", carrier, embedded=False)
        assert self.carried(source) == (False, [True, True])
        document = load_document(source)
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        assert self.carried(output) == (False, [False, False])
        assert find_leaks(output, document) == []

    def test_files_outside_any_listed_carrier_are_removed(self, tmp_path: Path):
        source = write_other_file_carriers_pdf(tmp_path / "carriers.pdf")
        assert all(self.carried(source, content)[0] for content in (LAUNCH_CONTENT, LOOSE_CONTENT))
        assert self.carried(source)[1][0]
        document = load_document(source)
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        assert not any(
            self.carried(output, content)[0] for content in (LAUNCH_CONTENT, LOOSE_CONTENT)
        )
        assert not self.carried(output)[1][0]
        assert find_leaks(output, document) == []


class TestAttachmentTree:
    """Attachments are removed whether their name tree is one node or split over `Kids`."""

    @pytest.fixture(params=[False, True], ids=["one-node", "split"])
    def attachments_pdf(self, request: pytest.FixtureRequest, tmp_path: Path) -> Path:
        return write_attachment_tree_pdf(tmp_path / "attachments.pdf", split=request.param)

    def test_content_and_labels_are_removed(self, attachments_pdf: Path):
        with pymupdf.open(attachments_pdf) as pdf:
            assert sum(TREE_ATTACHMENT_CONTENT in stream for stream in streams(pdf)) == 2
            assert all(label in objects(pdf) for label in TREE_LABELS)
        output = attachments_pdf.with_name("out.pdf")
        redact_pdf(attachments_pdf, load_document(attachments_pdf), output)
        with pymupdf.open(output) as pdf:
            assert not any(TREE_ATTACHMENT_CONTENT in stream for stream in streams(pdf))
            assert not any(label in objects(pdf) for label in TREE_LABELS)
            assert extract_surfaces(pdf) == []

    def test_the_surface_layer_reports_attachments_left_in_the_file(self, attachments_pdf: Path):
        leaks = find_leaks(attachments_pdf, load_document(attachments_pdf))
        assert layers(leaks) == {LeakLayer.SURFACE}


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

    def test_a_leak_names_the_page_it_lies_on(self, tmp_path: Path):
        source = write_surfaces_pdf(tmp_path / "surfaces.pdf")
        document = detected(source)
        leaks = find_leaks(source, document)
        on_page = [leak for leak in leaks if leak.layer == "page_text"]
        off_page = [leak for leak in leaks if leak.layer in {"surface", "object", "file_bytes"}]
        assert on_page
        assert off_page
        assert {leak.page_index for leak in on_page} == {0}
        assert {leak.page_index for leak in off_page} == {None}

    def test_a_leak_says_what_it_means(self, tmp_path: Path):
        source = write_surfaces_pdf(tmp_path / "surfaces.pdf")
        kinds = {(leak.layer, leak.kind) for leak in find_leaks(source, detected(source))}
        assert (LeakLayer.PAGE_TEXT, LeakKind.TEXT) in kinds
        assert (LeakLayer.OBJECT, LeakKind.TEXT) in kinds
        assert (LeakLayer.SURFACE, LeakKind.LEFTOVER) in kinds

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


class TestEmbeddedFileLeakCheck:
    """Each case plants, in a clean output, a file only one part of the surface layer sees."""

    @staticmethod
    def leaks_with(
        tmp_path: Path, key: str, plant: Callable[[pymupdf.Document], str]
    ) -> list[Leak]:
        """Redact a plain PDF, store what `plant` returns under a catalog key, then check it."""
        source = write_pdf(tmp_path / "contact.pdf", [LINES])
        document = load_document(source)
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        with pymupdf.open(output) as pdf:
            pdf.xref_set_key(pdf.pdf_catalog(), key, plant(pdf))
            pdf.save(tmp_path / "tampered.pdf")
        return find_leaks(tmp_path / "tampered.pdf", document)

    def test_labels_of_an_associated_file_are_reported(self, tmp_path: Path):
        # An external file: a label, nothing embedded.
        label = pymupdf.get_pdf_str("cv-Vesela.pdf")
        leaks = self.leaks_with(tmp_path, "AF", lambda _: f"[<< /Type /Filespec /UF {label} >>]")
        assert [leak.text for leak in leaks] == ["cv-Vesela.pdf"]
        assert leaks[0].where.endswith("/af0/ufilename")

    def test_an_unlabelled_file_specification_embedding_a_file_is_reported(self, tmp_path: Path):
        def plant(pdf: pymupdf.Document) -> str:
            return f"<< /EF << /F {add_stream(pdf, '<< >>', LAUNCH_CONTENT)} 0 R >> >>"

        leaks = self.leaks_with(tmp_path, "Extra", plant)
        assert [(leak.layer, leak.text) for leak in leaks] == [
            (LeakLayer.SURFACE, "file specification embedding a file")
        ]

    @pytest.mark.parametrize(
        ("content", "reported"),
        [(LOOSE_CONTENT, ["embedded file"]), (b"", [])],
        ids=["full", "empty"],
    )
    def test_an_embedded_file_stream_is_reported_unless_empty(
        self, tmp_path: Path, content: bytes, reported: list[str]
    ):
        def plant(pdf: pymupdf.Document) -> str:
            return f"{add_stream(pdf, '<< /Type /EmbeddedFile >>', content)} 0 R"

        assert [leak.text for leak in self.leaks_with(tmp_path, "Extra", plant)] == reported


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


def marked(source: Path, text: str, *, nth: int = 0) -> Document:
    """Load a PDF with one finding: the nth occurrence of a text on its first page."""
    document = load_document(source)
    page = document.pages[0]
    start = -1
    for _ in range(nth + 1):
        start = page.text.index(text, start + 1)
    end = start + len(text)
    document.entities = [
        Entity(
            type=EntityType.PERSON,
            page_index=0,
            start=start,
            end=end,
            text=text,
            bboxes=page.bboxes_for_span(start, end),
        )
    ]
    return document


class TestWhatIsSearched:
    """Each case pairs a text the check must still find with one it must not."""

    @pytest.mark.parametrize(
        ("lines", "text", "nth", "reported"),
        [
            (["Novak", "dopis od Novaka"], "Novak", 0, True),
            (["Novak", "Kunovak"], "Novak", 0, False),
            (["25 let", "rok 25"], "25", 0, True),
            (["25 let", "rok 1925"], "25", 0, False),
            (["25 let", "cena 25.50"], "25", 0, False),
            (["A", "bod A"], "A", 0, False),
        ],
        ids=["inflected", "inside-a-word", "number", "inside-a-year", "decimal", "one-letter"],
    )
    def test_page_text_counts_a_copy_where_a_word_starts(
        self, tmp_path: Path, lines: list[str], text: str, nth: int, reported: bool
    ):
        source = write_pdf(tmp_path / "page.pdf", [lines])
        document = marked(source, text, nth=nth)
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        page_leaks = [leak for leak in find_leaks(output, document) if leak.layer == "page_text"]
        assert bool(page_leaks) is reported

    @pytest.mark.parametrize(("planted", "reported"), [("(Novak)", True), ("(Jan)", False)])
    def test_a_text_shorter_than_four_characters_is_not_searched_in_the_file(
        self, tmp_path: Path, planted: str, reported: bool
    ):
        text = planted.strip("()")
        source = write_pdf(tmp_path / "name.pdf", [[f"{text} here", "KEEP"]])
        document = marked(source, text)
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        with pymupdf.open(output) as pdf:
            pdf.xref_set_key(pdf.pdf_catalog(), "Note", planted)
            pdf.save(tmp_path / "planted.pdf")
        assert planted.encode() in (tmp_path / "planted.pdf").read_bytes()
        leaks = find_leaks(tmp_path / "planted.pdf", document)
        assert bool(layers(leaks) & {LeakLayer.OBJECT, LeakLayer.FILE_BYTES}) is reported

    @pytest.mark.parametrize(
        ("dictionary", "reported"),
        [
            ("<< >>", True),
            ("<< /Type /XObject /Subtype /Image /Width 1 /Height 1 >>", False),
            ("<< /Length1 5 >>", False),
        ],
        ids=["plain", "image", "font-program"],
    )
    def test_image_and_font_streams_are_not_searched(
        self, tmp_path: Path, dictionary: str, reported: bool
    ):
        source = write_pdf(tmp_path / "name.pdf", [["Novak here", "KEEP"]])
        document = marked(source, "Novak")
        output = tmp_path / "out.pdf"
        redact_pdf(source, document, output)
        with pymupdf.open(output) as pdf:
            xref = add_stream(pdf, dictionary, b"xx Novak xx")
            pdf.xref_set_key(pdf.pdf_catalog(), "Extra", f"{xref} 0 R")
            pdf.save(tmp_path / "planted.pdf", deflate=True)
        with pymupdf.open(tmp_path / "planted.pdf") as pdf:
            assert any(b"Novak" in stream for stream in streams(pdf))
        leaks = find_leaks(tmp_path / "planted.pdf", document)
        assert (LeakLayer.OBJECT in layers(leaks)) is reported

    def test_the_file_byte_layer_does_not_name_the_file(self, tmp_path: Path):
        source = write_surfaces_pdf(tmp_path / "Novak-letter.pdf")
        leaks = find_leaks(source, detected(source))
        assert {leak.where for leak in leaks if leak.layer == "file_bytes"} == {"the file's bytes"}


def test_progress_names_each_layer_as_it_starts(tmp_path: Path):
    source = write_pdf(tmp_path / "contact.pdf", [LINES])
    document = detected(source)
    output = tmp_path / "out.pdf"
    redact_pdf(source, document, output)
    told: list[tuple[str, int, int]] = []
    find_leaks(output, document, progress=lambda *step: told.append(step))
    assert told == [(layer.value, 0, 0) for layer in LeakLayer if layer is not LeakLayer.OCR]
