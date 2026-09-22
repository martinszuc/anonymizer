"""Tests for running a detector over a document's pages and surfaces."""

from anonymizer.core.detect import detect_document, detect_surface, structured_detector
from anonymizer.core.types import BBox, Document, EntityType, Page, Surface, SurfaceKind

LINK_BOX = BBox(72, 150, 200, 165)
EMAIL = "jan.novak@example.com"


def link_surface(value: str) -> Surface:
    return Surface(SurfaceKind.LINK, value, "7/uri", page_index=2, bbox=LINK_BOX)


def test_surface_offsets_refer_to_the_surface_value():
    surface = link_surface(f"mailto:{EMAIL}?subject=CV")
    (entity,) = detect_surface(structured_detector(), surface)
    assert entity.type is EntityType.EMAIL
    assert surface.value[entity.start : entity.end] == EMAIL


def test_surface_entity_carries_the_surface_identity_page_and_box():
    surface = link_surface("tel:+420603123456")
    (entity,) = detect_surface(structured_detector(), surface)
    assert entity.type is EntityType.PHONE
    assert entity.surface_id == surface.surface_id
    assert entity.page_index == 2
    assert entity.bboxes == [LINK_BOX]


def test_document_level_surface_yields_entities_without_page_or_box():
    surface = Surface(SurfaceKind.METADATA, "r. c. 900101/0007", "Subject")
    (entity,) = detect_surface(structured_detector(), surface)
    assert entity.type is EntityType.BIRTH_NUMBER
    assert entity.page_index is None
    assert entity.bboxes == []


def test_surface_without_personal_data_yields_nothing():
    surface = Surface(SurfaceKind.METADATA, "Curriculum vitae", "Title")
    assert detect_surface(structured_detector(), surface) == []


def test_link_target_is_reported_as_a_url():
    surface = link_surface("https://www.linkedin.com/in/jan-novak")
    (entity,) = detect_surface(structured_detector(), surface)
    assert entity.type is EntityType.URL
    assert entity.text == surface.value
    assert entity.bboxes == [LINK_BOX]


def test_every_match_on_one_surface_is_reported():
    surface = Surface(SurfaceKind.XMP, f"<dc:creator>{EMAIL}</dc:creator> +420 603 123 456", "9")
    entities = detect_surface(structured_detector(), surface)
    assert {entity.type for entity in entities} == {EntityType.EMAIL, EntityType.PHONE}


def test_detect_document_covers_pages_and_surfaces():
    page = Page(index=0, width=595, height=842, text=f"e-mail {EMAIL}")
    surface = Surface(SurfaceKind.METADATA, f"CV {EMAIL}", "Title")
    document = Document(pages=[page], surfaces=[surface])
    document.entities = detect_document(structured_detector(), document)
    assert [entity.in_page_text for entity in document.entities] == [True, False]
    document.check_references()


def test_detecting_a_surface_leaves_the_document_pages_untouched():
    document = Document(surfaces=[link_surface(f"mailto:{EMAIL}")])
    detect_document(structured_detector(), document)
    assert document.pages == []
