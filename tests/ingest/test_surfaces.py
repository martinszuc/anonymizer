"""Tests for listing the strings a PDF carries outside its page text."""

from pathlib import Path
from typing import Any

import pymupdf
import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.types import BBox, Document, Surface, SurfaceKind

CONTACT_EMAIL = "jan.novak@example.com"
LAUNCH_PATH = "C:/Users/jnovak/cv.docx"
BOOKMARK_URI = "https://example.com/jnovak"
INDIRECT_KEYWORDS = "Nová účetní"
METADATA_DATE = "D:20260101120000"
ROTATED_WORD = "HERE"
# PyMuPDF creates its widget type constants at runtime.
TEXT_FIELD = pymupdf.PDF_WIDGET_TYPE_TEXT  # pyright: ignore[reportAttributeAccessIssue]
# Encloses ROTATED_WORD as inserted at (500, 800), in unrotated coordinates.
ROTATED_TARGET = pymupdf.Rect(495, 785, 545, 806)
XMP_PACKET = (
    '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
    '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
    '<rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/">'
    f"<dc:creator>{CONTACT_EMAIL}</dc:creator>"
    "</rdf:Description></rdf:RDF></x:xmpmeta>"
)


def add_text_field(page: pymupdf.Page, rect: pymupdf.Rect, name: str, value: str) -> None:
    # PyMuPDF initializes every Widget field to None, which pyright takes as its type.
    widget: Any = pymupdf.Widget()
    widget.field_name = name
    widget.field_type = TEXT_FIELD
    widget.rect = rect
    widget.field_value = value
    page.add_widget(widget)


def write_surfaces_pdf(path: Path) -> Path:
    """Write a PDF carrying one of every surface kind; page 2 is rotated."""
    document = pymupdf.open()
    # Creating a page detaches Page objects fetched earlier, so fetch after.
    document.new_page()
    document.new_page()
    first, second = document[0], document[1]

    first.insert_link(
        {
            "kind": pymupdf.LINK_URI,
            "from": pymupdf.Rect(72, 150, 200, 165),
            "uri": "mailto:jan.novak%40example.com",
        }
    )
    first.insert_link(
        {"kind": pymupdf.LINK_LAUNCH, "from": pymupdf.Rect(72, 170, 200, 185), "file": LAUNCH_PATH}
    )
    internal = {"kind": pymupdf.LINK_GOTO, "from": pymupdf.Rect(72, 190, 200, 205), "page": 1}
    first.insert_link(internal)
    note = first.add_text_annot((300, 300), "Call +420 603 123 456")
    note.set_info(title="Petra Svobodova")
    note.update()
    first.add_file_annot((400, 400), b"attached", "notes.txt", desc=f"notes for {CONTACT_EMAIL}")
    add_text_field(first, pymupdf.Rect(72, 500, 250, 520), "email", CONTACT_EMAIL)

    second.insert_text((500, 800), ROTATED_WORD, fontname="helv", fontsize=11)
    phone = {"kind": pymupdf.LINK_URI, "from": ROTATED_TARGET, "uri": "tel:+420603123456"}
    second.insert_link(phone)
    square = second.add_rect_annot(ROTATED_TARGET)
    square.set_info(content="rotated note")
    square.update()
    add_text_field(second, ROTATED_TARGET, "rotated", "rotated value")
    second.set_rotation(90)

    # Decomposed "á" checks that surface values are NFC-normalized like page text.
    document.set_metadata(
        {
            "title": "CV Jan Nova\u0301k",
            "subject": "   ",
            "creationDate": METADATA_DATE,
            "modDate": METADATA_DATE,
        }
    )
    info_xref = int(document.xref_get_key(-1, "Info")[1].split()[0])
    document.xref_set_key(info_xref, "Company", pymupdf.get_pdf_str("Novak Consulting"))
    # react-pdf stores every value as a separate string object.
    keywords_xref = document.get_new_xref()
    document.update_object(keywords_xref, pymupdf.get_pdf_str(INDIRECT_KEYWORDS))
    document.xref_set_key(info_xref, "Keywords", f"{keywords_xref} 0 R")
    document.set_xml_metadata(XMP_PACKET)
    profile = {"kind": pymupdf.LINK_URI, "uri": BOOKMARK_URI}
    document.set_toc([[1, "Jan Novak", 1, profile], [1, "Contact", 2]])
    document.embfile_add("cv.docx", b"attached", filename="cv.docx", desc="original CV")

    document.save(path)
    document.close()
    return path


@pytest.fixture
def document(tmp_path: Path) -> Document:
    return load_document(write_surfaces_pdf(tmp_path / "surfaces.pdf"))


def of_kind(document: Document, kind: SurfaceKind, page_index: int | None = None) -> list[Surface]:
    return [s for s in document.surfaces if s.kind is kind and s.page_index == page_index]


def values(surfaces: list[Surface]) -> set[str]:
    return {surface.value for surface in surfaces}


def overlaps(first: BBox, second: BBox) -> bool:
    horizontal = first.x0 < second.x1 and second.x0 < first.x1
    vertical = first.y0 < second.y1 and second.y0 < first.y1
    return horizontal and vertical


class TestDocumentLevelSurfaces:
    def test_metadata_values_are_nfc_normalized(self, document: Document):
        title = next(s for s in of_kind(document, SurfaceKind.METADATA) if s.ref == "Title")
        assert title.value == "CV Jan Novák"
        assert title.bbox is None

    def test_non_standard_metadata_keys_are_included(self, document: Document):
        refs = {surface.ref for surface in of_kind(document, SurfaceKind.METADATA)}
        assert "Company" in refs

    def test_metadata_stored_as_separate_string_objects_is_resolved(self, document: Document):
        keywords = next(s for s in of_kind(document, SurfaceKind.METADATA) if s.ref == "Keywords")
        assert keywords.value == INDIRECT_KEYWORDS

    def test_equal_values_under_different_keys_are_separate_surfaces(self, document: Document):
        dates = [s.ref for s in of_kind(document, SurfaceKind.METADATA) if s.value == METADATA_DATE]
        assert sorted(dates) == ["CreationDate", "ModDate"]

    def test_blank_metadata_values_are_skipped(self, document: Document):
        refs = {surface.ref for surface in of_kind(document, SurfaceKind.METADATA)}
        assert "Subject" not in refs

    def test_xmp_packet_is_one_surface(self, document: Document):
        (xmp,) = of_kind(document, SurfaceKind.XMP)
        assert CONTACT_EMAIL in xmp.value

    def test_bookmark_titles_and_targets_have_no_page(self, document: Document):
        bookmarks = of_kind(document, SurfaceKind.BOOKMARK)
        assert values(bookmarks) == {"Jan Novak", BOOKMARK_URI, "Contact"}

    def test_every_attachment_label_is_a_surface(self, document: Document):
        refs = {surface.ref for surface in of_kind(document, SurfaceKind.EMBEDDED_FILE)}
        assert refs == {"0/name", "0/filename", "0/ufilename", "0/description"}


class TestPageSurfaces:
    def test_link_targets_are_percent_decoded(self, document: Document):
        links = of_kind(document, SurfaceKind.LINK, page_index=0)
        assert values(links) == {f"mailto:{CONTACT_EMAIL}", LAUNCH_PATH}

    def test_link_boxes_match_the_clickable_area(self, document: Document):
        links = of_kind(document, SurfaceKind.LINK, page_index=0)
        mailto = next(link for link in links if link.value.startswith("mailto:"))
        assert mailto.bbox == BBox(72, 150, 200, 165)

    def test_annotation_text_and_author_are_listed(self, document: Document):
        annotations = values(of_kind(document, SurfaceKind.ANNOTATION, page_index=0))
        assert {"Call +420 603 123 456", "Petra Svobodova"} <= annotations

    def test_attachment_annotation_labels_are_embedded_files_on_the_page(self, document: Document):
        attachments = values(of_kind(document, SurfaceKind.EMBEDDED_FILE, page_index=0))
        assert attachments == {"notes.txt", f"notes for {CONTACT_EMAIL}"}

    def test_form_field_values_are_listed(self, document: Document):
        (field,) = of_kind(document, SurfaceKind.FORM_FIELD, page_index=0)
        assert field.value == CONTACT_EMAIL
        assert field.bbox == BBox(72, 500, 250, 520)

    def test_every_page_surface_has_a_box(self, document: Document):
        placed = [surface for surface in document.surfaces if surface.page_index is not None]
        assert placed
        assert all(surface.bbox is not None for surface in placed)


class TestRotatedPage:
    @pytest.mark.parametrize(
        "kind", [SurfaceKind.LINK, SurfaceKind.ANNOTATION, SurfaceKind.FORM_FIELD]
    )
    def test_surface_box_lies_over_the_word_it_was_placed_on(
        self, document: Document, kind: SurfaceKind
    ):
        page = document.pages[1]
        word = next(word for word in page.words if word.text == ROTATED_WORD)
        (surface,) = of_kind(document, kind, page_index=1)
        assert surface.bbox is not None
        assert surface.bbox.x1 <= page.width and surface.bbox.y1 <= page.height
        assert overlaps(surface.bbox, word.bbox)


class TestLoadDocument:
    def test_plain_pdf_has_no_surfaces(self, single_page_pdf: Path):
        assert load_document(single_page_pdf).surfaces == []

    def test_surfaces_survive_a_json_round_trip(self, document: Document):
        assert Document.from_json(document.to_json()).surfaces == document.surfaces
