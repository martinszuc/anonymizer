"""Tests for the shared data contract."""

import json

import pytest
from anonymizer.core.types import (
    SCHEMA_VERSION,
    BBox,
    DetectionSource,
    Document,
    Entity,
    EntityType,
    Page,
    ReviewState,
    Word,
)

# "Jan Novák" spans a line break to cover multi-box entities and diacritics.
PAGE_TEXT = "Jméno: Jan\nNovák, r. č. 900101/0009"
NAME_START = PAGE_TEXT.index("Jan")
NAME_END = PAGE_TEXT.index("Novák") + len("Novák")
BIRTH_NUMBER_START = PAGE_TEXT.index("900101/0009")
BIRTH_NUMBER_END = len(PAGE_TEXT)


def sample_page() -> Page:
    words = [
        Word("Jméno:", BBox(10, 10, 60, 22), 0, 6),
        Word("Jan", BBox(64, 10, 84, 22), NAME_START, NAME_START + 3),
        Word("Novák,", BBox(10, 26, 58, 38), PAGE_TEXT.index("Novák"), PAGE_TEXT.index(",") + 1),
        Word("r.", BBox(62, 26, 70, 38), PAGE_TEXT.index("r."), PAGE_TEXT.index("r.") + 2),
        Word("č.", BBox(74, 26, 82, 38), PAGE_TEXT.index("č."), PAGE_TEXT.index("č.") + 2),
        Word("900101/0009", BBox(86, 26, 170, 38), BIRTH_NUMBER_START, BIRTH_NUMBER_END),
    ]
    return Page(index=0, width=595.0, height=842.0, text=PAGE_TEXT, words=words)


def sample_document() -> Document:
    entities = [
        Entity(
            type=EntityType.PERSON,
            page_index=0,
            start=NAME_START,
            end=NAME_END,
            text="Jan\nNovák",
            source=DetectionSource.MODEL,
            score=0.91,
        ),
        Entity(
            type=EntityType.BIRTH_NUMBER,
            page_index=0,
            start=BIRTH_NUMBER_START,
            end=BIRTH_NUMBER_END,
            text="900101/0009",
            review=ReviewState.CONFIRMED,
        ),
    ]
    return Document(pages=[sample_page()], entities=entities, source_name="form.pdf", language="cs")


class TestBBox:
    def test_dimensions(self):
        box = BBox(10, 20, 40, 60)
        assert (box.width, box.height) == (30, 40)

    def test_rejects_inverted_box(self):
        with pytest.raises(ValueError, match="inverted bbox"):
            BBox(40, 0, 10, 10)

    def test_union_and_enclosing_agree(self):
        left = BBox(0, 0, 10, 10)
        right = BBox(20, 5, 30, 25)
        assert left.union(right) == BBox(0, 0, 30, 25)
        assert BBox.enclosing([left, right]) == left.union(right)

    def test_enclosing_rejects_empty_input(self):
        with pytest.raises(ValueError, match="at least one box"):
            BBox.enclosing([])

    def test_list_round_trip(self):
        box = BBox(1.5, 2.5, 3.5, 4.5)
        assert BBox.from_list(box.to_list()) == box

    def test_from_list_rejects_wrong_length(self):
        with pytest.raises(ValueError, match="expected 4 coordinates"):
            BBox.from_list([1.0, 2.0, 3.0])


class TestSpans:
    def test_word_rejects_empty_span(self):
        with pytest.raises(ValueError, match="invalid word span"):
            Word("x", BBox(0, 0, 1, 1), 5, 5)

    def test_entity_rejects_negative_page_index(self):
        with pytest.raises(ValueError, match="negative page index"):
            Entity(type=EntityType.EMAIL, page_index=-1, start=0, end=3, text="a@b")

    def test_entity_rejects_out_of_range_score(self):
        with pytest.raises(ValueError, match="score out of range"):
            Entity(type=EntityType.EMAIL, page_index=0, start=0, end=3, text="a@b", score=1.5)

    def test_words_in_span_covers_line_break(self):
        page = sample_page()
        matched = [word.text for word in page.words_in_span(NAME_START, NAME_END)]
        assert matched == ["Jan", "Novák,"]

    def test_words_in_span_excludes_adjacent_words(self):
        page = sample_page()
        matched = [word.text for word in page.words_in_span(0, 6)]
        assert matched == ["Jméno:"]


class TestDocument:
    def test_resolve_bboxes_yields_one_box_per_word(self):
        document = sample_document()
        document.resolve_bboxes()
        name = document.entities_on_page(0)[0]
        assert len(name.bboxes) == 2
        assert BBox.enclosing(name.bboxes) == BBox(10, 10, 84, 38)

    def test_resolve_bboxes_keeps_existing_geometry(self):
        document = sample_document()
        manual = BBox(0, 0, 1, 1)
        document.entities[0].bboxes = [manual]
        document.resolve_bboxes()
        assert document.entities[0].bboxes == [manual]

    def test_entities_on_page_is_sorted_by_offset(self):
        document = sample_document()
        starts = [entity.start for entity in document.entities_on_page(0)]
        assert starts == sorted(starts)

    def test_page_lookup_rejects_unknown_index(self):
        with pytest.raises(KeyError, match="no page with index 7"):
            sample_document().page(7)

    def test_is_redactable_follows_review_state(self):
        document = sample_document()
        name = document.entities[0]
        assert name.is_redactable
        name.review = ReviewState.REJECTED
        assert not name.is_redactable

    def test_json_round_trip_preserves_everything(self):
        document = sample_document()
        document.resolve_bboxes()
        restored = Document.from_json(document.to_json())
        assert restored.to_dict() == document.to_dict()

    def test_json_preserves_diacritics_literally(self):
        text = sample_document().to_json()
        assert "Novák" in text

    def test_json_carries_schema_version(self):
        payload = json.loads(sample_document().to_json())
        assert payload["schema_version"] == SCHEMA_VERSION

    def test_from_dict_rejects_foreign_schema_version(self):
        payload = sample_document().to_dict()
        payload["schema_version"] = SCHEMA_VERSION + 1
        with pytest.raises(ValueError, match="unsupported schema version"):
            Document.from_dict(payload)

    def test_entity_ids_are_unique_and_stable_across_round_trip(self):
        document = sample_document()
        ids = [entity.entity_id for entity in document.entities]
        assert len(set(ids)) == len(ids)
        restored = Document.from_json(document.to_json())
        assert [entity.entity_id for entity in restored.entities] == ids
