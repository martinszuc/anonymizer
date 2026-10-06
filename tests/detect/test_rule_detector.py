"""Tests for the rule detector and how it merges overlapping matches."""

from anonymizer.core.detect import detector_for
from anonymizer.core.detect.base import Finder, Match, RuleDetector
from anonymizer.core.types import BBox, DetectionSource, EntityType, Page, Word

TEXT = (
    "Jan Novák, r. č. 900101/0007\n"
    "účet 19-2000145399/0800, IBAN CZ65 0800 0000 1920 0014 5399\n"
    "tel. +420 777 123 456, e-mail jan.novak@example.com"
)


def _fixed(*matches: Match) -> Finder:
    """A finder that reports the given matches whatever the text."""
    return lambda _text: matches


def _detect(*finders: Finder, text: str = "x" * 40) -> list[tuple[EntityType, int, int]]:
    page = Page(index=0, width=595, height=842, text=text)
    return [(entity.type, *entity.span) for entity in RuleDetector(finders).detect(page)]


def test_a_match_inside_a_stronger_one_is_dropped():
    weaker = Match(EntityType.PHONE, 0, 9, "x" * 9)
    stronger = Match(EntityType.BIRTH_NUMBER, 0, 10, "x" * 10)
    assert _detect(_fixed(weaker), _fixed(stronger)) == [(EntityType.BIRTH_NUMBER, 0, 10)]


def test_a_match_inside_a_longer_one_of_its_type_is_dropped():
    short = Match(EntityType.PHONE, 0, 3, "x" * 3)
    long = Match(EntityType.PHONE, 0, 9, "x" * 9)
    assert _detect(_fixed(short, long)) == [(EntityType.PHONE, 0, 9)]


def test_partial_overlaps_keep_both_matches():
    # Dropping the weaker one would leave its part beyond the stronger one readable.
    stronger = Match(EntityType.BANK_ACCOUNT, 5, 15, "x" * 10)
    weaker = Match(EntityType.ADDRESS, 10, 30, "x" * 20)
    assert _detect(_fixed(stronger), _fixed(weaker)) == [
        (EntityType.BANK_ACCOUNT, 5, 15),
        (EntityType.ADDRESS, 10, 30),
    ]


def test_an_address_containing_a_valid_account_number_is_kept_whole():
    # 19/1234 passes the account checksum and sits inside the house number.
    text = "Bydliště: Hlavní 19/1234, 602 00 Brno"
    found = {
        entity.type: entity.text
        for entity in detector_for("cs").detect(Page(0, 595, 842, text=text))
    }
    assert found == {
        EntityType.ADDRESS: "Hlavní 19/1234, 602 00 Brno",
        EntityType.BANK_ACCOUNT: "19/1234",
    }


def test_disjoint_matches_are_kept_in_order():
    first = Match(EntityType.EMAIL, 20, 30, "x" * 10)
    second = Match(EntityType.PHONE, 0, 9, "x" * 9)
    assert _detect(_fixed(first, second)) == [
        (EntityType.PHONE, 0, 9),
        (EntityType.EMAIL, 20, 30),
    ]


def test_email_wins_over_digits_it_contains():
    text = "user123456789@example.com"
    types = [entity.type for entity in detector_for(None).detect(Page(0, 595, 842, text=text))]
    assert types == [EntityType.EMAIL]


def test_detects_every_structured_entity_on_a_page():
    detector = detector_for(None)
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
    entities = detector_for(None).detect(Page(index=3, width=595, height=842, text=TEXT))
    assert [entity.span for entity in entities] == sorted(entity.span for entity in entities)
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
    entities = detector_for(None).detect(page)
    assert entities[0].bboxes == [BBox(10, 10, 90, 22)]


SPLIT_TEXT = "e-mail tereza. prochazkova@example. com, tel. +420 777 123 456, www. example. cz"


def _found(page: Page) -> dict[EntityType, str | None]:
    return {entity.type: entity.text for entity in detector_for(None).detect(page)}


def test_addresses_split_by_ocr_are_matched_whole_on_a_page_read_by_ocr():
    page = Page(0, 595, 842, text=SPLIT_TEXT, has_text_layer=False, raster_dpi=300)
    assert _found(page) == {
        EntityType.EMAIL: "tereza. prochazkova@example. com",
        EntityType.PHONE: "+420 777 123 456",
        EntityType.URL: "www. example. cz",
    }


def test_a_text_layer_is_not_joined_across_spaces():
    # The space is real in a text layer; only the strict rules run there.
    assert _found(Page(0, 595, 842, text=SPLIT_TEXT)) == {EntityType.PHONE: "+420 777 123 456"}


def test_a_split_address_is_one_entity_covering_every_word():
    text = "tereza. prochazkova@example. com"
    pieces = [("tereza.", 10), ("prochazkova@example.", 60), ("com", 180)]
    words = []
    for piece, left in pieces:
        start = text.index(piece)
        box = BBox(left, 10, left + 5 * len(piece), 22)
        words.append(Word(piece, box, start, start + len(piece)))
    page = Page(0, 595, 842, text=text, words=words, has_text_layer=False, raster_dpi=300)
    (entity,) = detector_for(None).detect(page)
    assert entity.span == (0, len(text))
    assert entity.bboxes == [word.bbox for word in words]
