"""Matching, scores and bootstrap intervals, checked against hand counts."""

import pytest
from anonymizer.core.types import BBox, Entity, EntityType

from experiments.metrics import (
    ANY_TYPE,
    COVERAGE_METRICS,
    PARTIAL,
    STRICT,
    Counts,
    Coverage,
    document_counts,
    document_coverage,
    interval,
    match,
    paired_difference,
    percentiles,
    resampled_totals,
    resamples,
)

PERSON, ADDRESS = EntityType.PERSON, EntityType.ADDRESS


def entity(kind: EntityType, start: int, end: int, page: int = 0) -> Entity:
    return Entity(kind, page, start, end, "x" * (end - start))


class TestMatch:
    def test_strict_needs_the_exact_span(self):
        counts = match({(0, 0, 9), (0, 20, 25)}, {(0, 0, 9), (0, 20, 26)}, STRICT)
        assert counts == Counts(predicted=2, predicted_matched=1, gold=2, gold_matched=1)

    def test_partial_counts_each_side_on_its_own(self):
        # One long prediction covers two gold names; a second prediction hits nothing.
        counts = match({(0, 0, 30), (0, 40, 45)}, {(0, 0, 9), (0, 10, 20), (0, 50, 55)}, PARTIAL)
        assert counts == Counts(predicted=2, predicted_matched=1, gold=3, gold_matched=2)

    def test_touching_spans_do_not_overlap_and_pages_are_apart(self):
        assert match({(0, 0, 5)}, {(0, 5, 9)}, PARTIAL).gold_matched == 0
        assert match({(1, 0, 5)}, {(0, 0, 5)}, PARTIAL).gold_matched == 0

    def test_unknown_mode(self):
        with pytest.raises(ValueError, match="unknown match mode"):
            match(set(), set(), "fuzzy")


class TestCounts:
    def test_scores(self):
        counts = Counts(predicted=10, predicted_matched=8, gold=16, gold_matched=8)
        assert counts.precision == pytest.approx(0.8)
        assert counts.recall == pytest.approx(0.5)
        assert counts.metric("f1") == pytest.approx(2 * 0.8 * 0.5 / 1.3)
        assert counts.metric("f2") == pytest.approx(5 * 0.8 * 0.5 / (4 * 0.8 + 0.5))

    def test_precision_undefined_without_predictions(self):
        counts = Counts(predicted=0, predicted_matched=0, gold=4, gold_matched=0)
        assert counts.precision is None
        assert counts.metric("f2") == 0.0

    def test_nothing_to_find(self):
        assert Counts().recall is None
        assert Counts().metric("f1") is None

    def test_unknown_metric(self):
        with pytest.raises(ValueError, match="unknown metric"):
            Counts().metric("accuracy")


def test_document_counts_by_type_and_any_type():
    gold = [entity(PERSON, 0, 9), entity(ADDRESS, 20, 32)]
    predicted = [
        entity(PERSON, 0, 9),
        # An address found as a person: wrong type, but flagged all the same.
        entity(PERSON, 20, 32),
        # A type the corpus does not annotate is not scored.
        entity(EntityType.IBAN, 40, 60),
    ]
    counts = document_counts(predicted, gold, {PERSON, ADDRESS})
    assert counts[STRICT, "person"] == Counts(2, 1, 1, 1)
    assert counts[STRICT, "address"] == Counts(0, 0, 1, 0)
    assert counts[STRICT, ANY_TYPE] == Counts(2, 2, 2, 2)


def test_document_counts_skip_regions_and_unscored_gold():
    region = Entity(EntityType.REGION, 0, bboxes=[BBox(0, 0, 10, 10)])
    counts = document_counts([region], [entity(PERSON, 0, 3), entity(ADDRESS, 4, 8)], {PERSON})
    assert counts[PARTIAL, "person"] == Counts(0, 0, 1, 0)
    assert (PARTIAL, ANY_TYPE) not in counts


class TestBootstrap:
    def test_resamples_are_seeded(self):
        assert resamples(5, 3, seed=1) == resamples(5, 3, seed=1)
        assert resamples(5, 3, seed=1) != resamples(5, 3, seed=2)
        assert all(len(draw) == 5 for draw in resamples(5, 3, seed=1))

    def test_interval_surrounds_the_value(self):
        per_document = [Counts(2, 2, 2, 2), Counts(2, 1, 2, 1), Counts(2, 0, 2, 0)] * 4
        draws = resamples(len(per_document), 500, seed=7)
        result = interval(per_document, resampled_totals(per_document, draws), "recall")
        assert result.value == pytest.approx(0.5)
        assert result.low is not None and result.high is not None
        assert result.low < 0.5 < result.high

    def test_identical_documents_give_no_spread(self):
        per_document = [Counts(2, 1, 2, 1)] * 6
        draws = resamples(6, 100, seed=7)
        result = interval(per_document, resampled_totals(per_document, draws), "precision")
        assert (result.value, result.low, result.high) == (0.5, 0.5, 0.5)

    def test_paired_difference_of_a_clear_improvement(self):
        before = [Counts(2, 1, 2, 1)] * 10
        after = [Counts(2, 2, 2, 2)] * 10
        draws = resamples(10, 200, seed=3)
        difference = paired_difference(
            (before, resampled_totals(before, draws)),
            (after, resampled_totals(after, draws)),
            "recall",
        )
        assert difference.delta == pytest.approx(0.5)
        assert difference.p_value == 0.0
        assert difference.to_dict()["low"] == 0.5

    def test_paired_difference_of_the_same_system(self):
        counts = [Counts(2, 1, 2, 1), Counts(2, 2, 2, 2)]
        draws = resamples(2, 50, seed=3)
        paired = (counts, resampled_totals(counts, draws))
        assert paired_difference(paired, paired, "f2").p_value == 1.0

    def test_paired_difference_undefined_without_predictions(self):
        none = [Counts(0, 0, 2, 0)] * 3
        draws = resamples(3, 20, seed=3)
        paired = (none, resampled_totals(none, draws))
        difference = paired_difference(paired, paired, "precision")
        assert difference.delta is None
        assert difference.p_value is None

    def test_percentiles(self):
        assert percentiles([]) == (None, None)
        values = [float(number) for number in range(1, 1001)]
        assert percentiles(values) == (25.0, 975.0)


class TestCoverage:
    """Leak coverage, counted by hand on short texts. Whitespace is never counted."""

    TEXT = "Jan Novák ahoj"  # 12 characters that are not whitespace; the name has 8

    def coverage(
        self,
        predicted: list[Entity],
        gold: list[Entity],
        pages: list[str] | None = None,
        types: set[EntityType] | None = None,
    ) -> dict[str, Coverage]:
        pages = [self.TEXT] if pages is None else pages
        return document_coverage(predicted, gold, types or {PERSON}, pages)

    def test_a_first_name_alone_leaves_the_surname_readable(self):
        # A partial match counts this as found; "Novák" stays readable.
        person = self.coverage([entity(PERSON, 0, 3)], [entity(PERSON, 0, 9)])["person"]
        assert person == Coverage(
            gold_characters=8,
            residual_characters=5,
            gold_items=1,
            hidden_items=0,
            over_characters=0,
            text_characters=12,
        )
        assert person.metric("residual") == pytest.approx(5 / 8)
        assert person.metric("hidden_whole") == 0.0
        assert person.metric("over_redaction") == 0.0

    def test_a_name_found_as_an_address_is_hidden(self):
        coverage = self.coverage(
            [entity(ADDRESS, 0, 9)], [entity(PERSON, 0, 9)], types={PERSON, ADDRESS}
        )
        assert coverage["person"].residual_characters == 0
        assert coverage["person"].hidden_items == 1
        # Inside a gold span of another scored type: not over-redaction.
        assert coverage["address"].over_characters == 0
        assert coverage["address"].metric("residual") is None  # no address gold
        assert coverage[ANY_TYPE].metric("hidden_whole") == 1.0

    def test_an_unscored_type_covers_but_is_not_over_redaction(self):
        predicted = [entity(EntityType.IBAN, 0, 9), entity(EntityType.IBAN, 10, 14)]
        person = self.coverage(predicted, [entity(PERSON, 0, 9)])["person"]
        assert (person.hidden_items, person.over_characters) == (1, 0)

    def test_adjacent_predictions_hide_the_name_whole(self):
        # "Jan" and "Novák" apart: the space between them is not counted.
        predicted = [entity(PERSON, 0, 3), entity(PERSON, 4, 9)]
        person = self.coverage(predicted, [entity(PERSON, 0, 9)])["person"]
        assert (person.residual_characters, person.hidden_items) == (0, 1)

    def test_overlapping_predictions_count_each_character_once(self):
        predicted = [entity(PERSON, 0, 6), entity(PERSON, 2, 14)]
        person = self.coverage(predicted, [entity(PERSON, 0, 9)])["person"]
        # "ahoj" is predicted once, by the longer span: 4 characters outside the gold.
        assert person.over_characters == 4
        assert person.metric("over_redaction") == pytest.approx(1000 * 4 / 12)
        assert person.hidden_items == 1

    def test_a_wider_prediction_hides_the_gold_and_over_redacts(self):
        person = self.coverage([entity(PERSON, 0, 9)], [entity(PERSON, 4, 9)])["person"]
        assert person == Coverage(
            gold_characters=5,
            residual_characters=0,
            gold_items=1,
            hidden_items=1,
            over_characters=3,  # "Jan"
            text_characters=12,
        )

    def test_a_name_across_a_line_break(self):
        text = "Jan\n  Novák"
        gold = [entity(PERSON, 0, 11)]
        person = self.coverage([entity(PERSON, 0, 3)], gold, [text])["person"]
        assert (person.gold_characters, person.residual_characters) == (8, 5)
        both = [entity(PERSON, 0, 3), entity(PERSON, 6, 11)]
        person = self.coverage(both, gold, [text])["person"]
        assert (person.residual_characters, person.hidden_items) == (0, 1)
        # A prediction of whitespace alone removes nothing readable.
        spaces = self.coverage([entity(PERSON, 3, 6)], [], [text])["person"]
        assert spaces.over_characters == 0

    def test_offsets_are_page_local(self):
        pages = ["Jan Novák", "Jan Novák"]
        gold = [entity(PERSON, 0, 9, page=1)]
        person = self.coverage([entity(PERSON, 0, 9, page=0)], gold, pages)["person"]
        assert person == Coverage(
            gold_characters=8,
            residual_characters=8,
            gold_items=1,
            hidden_items=0,
            over_characters=8,
            text_characters=16,
        )
        found = self.coverage([entity(PERSON, 0, 9, page=1)], gold, pages)["person"]
        assert (found.hidden_items, found.over_characters) == (1, 0)

    def test_gold_items_are_the_distinct_spans_the_match_counts_use(self):
        gold = [entity(PERSON, 0, 9), entity(PERSON, 0, 9), entity(PERSON, 4, 9)]
        person = self.coverage([entity(PERSON, 4, 9)], gold)["person"]
        # Overlapping gold characters are counted once; each distinct span is an item.
        assert (person.gold_characters, person.residual_characters) == (8, 3)
        assert (person.gold_items, person.hidden_items) == (2, 1)
        assert person.gold_items == document_counts([], gold, {PERSON})[PARTIAL, "person"].gold

    @pytest.mark.parametrize("pages", [[], [""], ["   \n"]])
    def test_empty_documents(self, pages: list[str]):
        person = self.coverage([], [], pages)["person"]
        assert person == Coverage()
        for metric in COVERAGE_METRICS:
            assert person.metric(metric) is None

    def test_regions_are_skipped_and_one_type_gives_no_any_row(self):
        region = Entity(EntityType.REGION, 0, bboxes=[BBox(0, 0, 10, 10)])
        coverage = self.coverage([region], [entity(PERSON, 0, 9)])
        assert set(coverage) == {"person"}
        assert coverage["person"].residual_characters == 8

    def test_unknown_metric(self):
        with pytest.raises(ValueError, match="unknown metric"):
            Coverage().metric("f2")

    def test_sum_and_bootstrap(self):
        hidden = Coverage(10, 0, 2, 2, 5, 100)
        leaky = Coverage(10, 10, 2, 0, 0, 100)
        assert hidden + leaky == Coverage(20, 10, 4, 2, 5, 200)
        per_document = [hidden, leaky] * 5
        draws = resamples(len(per_document), 300, seed=5)
        result = interval(per_document, resampled_totals(per_document, draws), "residual")
        assert result.value == pytest.approx(0.5)
        assert result.low is not None and result.high is not None
        assert result.low < 0.5 < result.high
        better = [hidden] * 10
        difference = paired_difference(
            (per_document, resampled_totals(per_document, draws)),
            (better, resampled_totals(better, draws)),
            "residual",
        )
        assert difference.delta == pytest.approx(-0.5)
        assert difference.p_value == 0.0
