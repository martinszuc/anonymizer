"""Matching, scores and bootstrap intervals, checked against hand counts."""

import pytest
from anonymizer.core.types import BBox, Entity, EntityType

from experiments.metrics import (
    ANY_TYPE,
    PARTIAL,
    STRICT,
    Counts,
    document_counts,
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
