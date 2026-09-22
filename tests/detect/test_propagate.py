"""Tests for redacting every occurrence of already marked text."""

from pathlib import Path

from anonymizer.core.detect import propagate_occurrences
from anonymizer.core.ingest import load_document
from anonymizer.core.types import (
    BBox,
    DetectionSource,
    Document,
    Entity,
    EntityType,
    Page,
    ReviewState,
    Surface,
    SurfaceKind,
)

from tests.pdf_builders import write_pdf


def marked(page: Page, text: str, entity_type: EntityType = EntityType.PERSON) -> Entity:
    start = page.text.index(text)
    return Entity(
        type=entity_type,
        page_index=page.index,
        start=start,
        end=start + len(text),
        text=text,
        source=DetectionSource.MANUAL,
    )


def texts(entities: list[Entity]) -> list[tuple[int | None, str | None]]:
    return [(entity.page_index, entity.text) for entity in entities]


def test_every_other_occurrence_becomes_a_propagated_entity(tmp_path: Path):
    pdf = write_pdf(tmp_path / "cv.pdf", [["Jan Novak", "ref: Jan Novak"], ["by Jan Novak"]])
    document = load_document(pdf)
    document.entities = [marked(document.pages[0], "Jan Novak")]
    found = propagate_occurrences(document)
    assert texts(found) == [(0, "Jan Novak"), (1, "Jan Novak")]
    assert {entity.source for entity in found} == {DetectionSource.PROPAGATED}
    assert {entity.review for entity in found} == {ReviewState.PENDING}
    assert all(entity.bboxes for entity in found)


def test_whole_words_only():
    page = Page(0, 595, 842, text="Jan wrote in January to Janek. Jan")
    document = Document(pages=[page], entities=[marked(page, "Jan")])
    assert texts(propagate_occurrences(document)) == [(0, "Jan")]


def test_occurrence_broken_across_lines_is_found():
    page = Page(0, 595, 842, text="Jan Novak signed.\nThanks, Jan\nNovak")
    document = Document(pages=[page], entities=[marked(page, "Jan Novak")])
    assert texts(propagate_occurrences(document)) == [(0, "Jan\nNovak")]


def test_inflected_forms_are_not_found():
    page = Page(0, 595, 842, text="Novák podepsal. Poděkování Novákovi.")
    document = Document(pages=[page], entities=[marked(page, "Novák")])
    assert propagate_occurrences(document) == []


def test_existing_entities_are_not_duplicated():
    page = Page(0, 595, 842, text="Jan Novak and Jan Novak")
    first = marked(page, "Jan Novak")
    second = Entity(type=EntityType.PERSON, page_index=0, start=14, end=23, text="Jan Novak")
    document = Document(pages=[page], entities=[first, second])
    assert propagate_occurrences(document) == []


def test_longer_text_claims_its_occurrence_first():
    page = Page(0, 595, 842, text="Jan Novak. Jan Novak. Jan.")
    full_name = marked(page, "Jan Novak")
    first_name = Entity(type=EntityType.PERSON, page_index=0, start=22, end=25, text="Jan")
    document = Document(pages=[page], entities=[first_name, full_name])
    # The second "Jan Novak" is taken whole, not as "Jan" plus a leftover "Novak".
    assert texts(propagate_occurrences(document)) == [(0, "Jan Novak")]


def test_rejected_text_is_not_propagated():
    page = Page(0, 595, 842, text="Jan Novak, Jan Novak")
    entity = marked(page, "Jan Novak")
    entity.review = ReviewState.REJECTED
    document = Document(pages=[page], entities=[entity])
    assert propagate_occurrences(document) == []


def test_text_found_on_a_surface_is_found_where_it_is_printed():
    url = "https://github.com/jnovak"
    page = Page(0, 595, 842, text=f"Code: {url}")
    link = Surface(SurfaceKind.LINK, url, "7/uri", 0, BBox(10, 10, 100, 20))
    on_link = Entity(
        type=EntityType.URL,
        page_index=0,
        start=0,
        end=len(url),
        text=url,
        surface_id=link.surface_id,
    )
    document = Document(pages=[page], surfaces=[link], entities=[on_link])
    found = propagate_occurrences(document)
    assert [(entity.type, entity.text, entity.in_page_text) for entity in found] == [
        (EntityType.URL, url, True)
    ]


def test_regions_are_ignored():
    page = Page(0, 595, 842, text="nothing to find")
    region = Entity(type=EntityType.REGION, page_index=0, bboxes=[BBox(0, 0, 10, 10)])
    document = Document(pages=[page], entities=[region])
    assert propagate_occurrences(document) == []
