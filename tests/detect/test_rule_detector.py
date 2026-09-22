"""Tests for the rule detector and overlap resolution."""

from anonymizer.core.detect import structured_detector
from anonymizer.core.detect.base import Match, resolve_overlaps
from anonymizer.core.types import BBox, DetectionSource, EntityType, Page, Word

TEXT = (
    "Jan Novák, r. č. 900101/0007\n"
    "účet 19-2000145399/0800, IBAN CZ65 0800 0000 1920 0014 5399\n"
    "tel. +420 777 123 456, e-mail jan.novak@example.com"
)


def test_overlap_resolution_prefers_stronger_type():
    weaker = Match(EntityType.PHONE, 0, 9, "123456789")
    stronger = Match(EntityType.BIRTH_NUMBER, 0, 10, "9001010007")
    assert resolve_overlaps([weaker, stronger]) == [stronger]


def test_overlap_resolution_prefers_longer_span_within_a_type():
    short = Match(EntityType.PERSON, 0, 3, "Jan")
    long = Match(EntityType.PERSON, 0, 9, "Jan Novák")
    assert resolve_overlaps([short, long]) == [long]


def test_overlap_resolution_keeps_disjoint_matches_in_order():
    first = Match(EntityType.EMAIL, 20, 30, "a@b.example")
    second = Match(EntityType.PHONE, 0, 9, "777123456")
    assert resolve_overlaps([first, second]) == [second, first]


def test_email_wins_over_digits_it_contains():
    text = "user123456789@example.com"
    types = [entity.type for entity in structured_detector().detect(Page(0, 595, 842, text=text))]
    assert types == [EntityType.EMAIL]


def test_detects_every_structured_entity_on_a_page():
    detector = structured_detector()
    entities = detector.detect(Page(index=0, width=595, height=842, text=TEXT))
    found = {entity.type: entity.text for entity in entities}
    assert found == {
        EntityType.BIRTH_NUMBER: "900101/0007",
        EntityType.BANK_ACCOUNT: "19-2000145399/0800",
        EntityType.IBAN: "CZ65 0800 0000 1920 0014 5399",
        EntityType.PHONE: "+420 777 123 456",
        EntityType.EMAIL: "jan.novak@example.com",
    }


def test_entities_are_ordered_and_attributed_to_the_page():
    entities = structured_detector().detect(Page(index=3, width=595, height=842, text=TEXT))
    assert [entity.start for entity in entities] == sorted(entity.start for entity in entities)
    assert {entity.page_index for entity in entities} == {3}
    assert {entity.source for entity in entities} == {DetectionSource.RULE}


def test_detector_attaches_geometry_from_page_words():
    text = "900101/0007"
    page = Page(
        index=0,
        width=595,
        height=842,
        text=text,
        words=[Word(text, BBox(10, 10, 90, 22), 0, len(text))],
    )
    entities = structured_detector().detect(page)
    assert entities[0].bboxes == [BBox(10, 10, 90, 22)]


def test_detector_has_a_name():
    assert structured_detector().name == "structured-rules"
