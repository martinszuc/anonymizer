"""Tests for listing the strings a PDF carries outside its page text."""

from pathlib import Path

import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.types import BBox, Document, Surface, SurfaceKind

from tests.pdf_builders import (
    BOOKMARK_URI,
    CONTACT_EMAIL,
    INDIRECT_KEYWORDS,
    LAUNCH_PATH,
    METADATA_DATE,
    ROTATED_WORD,
    STRUCTURE_ACTUAL_TEXT,
    STRUCTURE_ALT,
    write_pdf,
    write_surfaces_pdf,
)


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


class TestStructureTree:
    def test_alternate_and_replacement_text_are_listed(self, document: Document):
        structure = values(of_kind(document, SurfaceKind.STRUCTURE))
        assert structure == {STRUCTURE_ALT, STRUCTURE_ACTUAL_TEXT}

    def test_structure_surfaces_name_the_element_and_key(self, document: Document):
        refs = {surface.ref.split("/")[1] for surface in of_kind(document, SurfaceKind.STRUCTURE)}
        assert refs == {"Alt", "ActualText"}

    def test_untagged_pdf_has_no_structure_surfaces(self, tmp_path: Path):
        plain = load_document(write_pdf(tmp_path / "plain.pdf", [["text"]]))
        assert of_kind(plain, SurfaceKind.STRUCTURE) == []


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
