"""Entity-level scores with document-level bootstrap confidence intervals.

Matching, per type and page:

- **strict**: a predicted span counts if a gold span of the same type has
  exactly its offsets.
- **partial**: a predicted span counts if it overlaps any gold span of the
  same type, and a gold span counts as found if any prediction of its type
  overlaps it. Precision and recall are counted on their own sides, so one
  long prediction covering two names finds both.

`ANY_TYPE` scores the same spans with types ignored: whether personal data
was flagged at all, which is what redaction needs (a street detected as a
person is still removed). Only the types a corpus annotates take part.

F-beta: F1, and F2, which weighs recall four times as much as precision, as
is usual in de-identification, where a miss leaks and a false alarm costs a
click. Precision is undefined (`None`) without predictions.

Confidence intervals resample whole documents with replacement (spans of
one document are not independent: a repeated name is found or missed
everywhere) and take the 2.5th and 97.5th percentiles. Two systems are
compared on the same resamples (paired bootstrap).
"""

from __future__ import annotations

import math
import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from anonymizer.core.types import Entity, EntityType

STRICT = "strict"
PARTIAL = "partial"
MATCHES = (STRICT, PARTIAL)
ANY_TYPE = "any"
METRICS = ("precision", "recall", "f1", "f2")

Span = tuple[int, int, int]
"""Page index, start, end."""


@dataclass(frozen=True, slots=True)
class Counts:
    """Match counts, additive over documents.

    Attributes:
        predicted: Predicted spans.
        predicted_matched: Predicted spans that match a gold span.
        gold: Gold spans.
        gold_matched: Gold spans matched by a prediction.
    """

    predicted: int = 0
    predicted_matched: int = 0
    gold: int = 0
    gold_matched: int = 0

    def __add__(self, other: Counts) -> Counts:
        """Sum two counts."""
        return Counts(
            self.predicted + other.predicted,
            self.predicted_matched + other.predicted_matched,
            self.gold + other.gold,
            self.gold_matched + other.gold_matched,
        )

    @property
    def precision(self) -> float | None:
        """Share of predictions that match; `None` without predictions."""
        return self.predicted_matched / self.predicted if self.predicted else None

    @property
    def recall(self) -> float | None:
        """Share of gold spans found; `None` without gold spans."""
        return self.gold_matched / self.gold if self.gold else None

    def f_beta(self, beta: float) -> float | None:
        """F-beta score; `None` when recall is undefined."""
        recall = self.recall
        if recall is None:
            return None
        precision = self.precision or 0.0
        weight = beta * beta
        denominator = weight * precision + recall
        return (1 + weight) * precision * recall / denominator if denominator else 0.0

    def metric(self, name: str) -> float | None:
        """Return one of `METRICS` by name."""
        if name == "precision":
            return self.precision
        if name == "recall":
            return self.recall
        if name == "f1":
            return self.f_beta(1.0)
        if name == "f2":
            return self.f_beta(2.0)
        msg = f"unknown metric {name!r}"
        raise ValueError(msg)


def _spans(entities: Iterable[Entity]) -> set[Span]:
    spans: set[Span] = set()
    for entity in entities:
        if entity.page_index is None:
            continue
        start, end = entity.span
        spans.add((entity.page_index, start, end))
    return spans


def match(predicted: set[Span], gold: set[Span], mode: str) -> Counts:
    """Count matches between predicted and gold spans of one type.

    Args:
        predicted: Predicted spans.
        gold: Gold spans.
        mode: `strict` or `partial`.

    Returns:
        The counts.
    """
    if mode == STRICT:
        both = len(predicted & gold)
        return Counts(len(predicted), both, len(gold), both)
    if mode != PARTIAL:
        msg = f"unknown match mode {mode!r}"
        raise ValueError(msg)
    predicted_matched = sum(1 for span in predicted if _overlaps_any(span, gold))
    gold_matched = sum(1 for span in gold if _overlaps_any(span, predicted))
    return Counts(len(predicted), predicted_matched, len(gold), gold_matched)


def _overlaps_any(span: Span, others: set[Span]) -> bool:
    page, start, end = span
    return any(
        page == other_page and start < other_end and other_start < end
        for other_page, other_start, other_end in others
    )


def scoreable(entities: Iterable[Entity], types: Iterable[EntityType]) -> list[Entity]:
    """Keep the entities in page text whose type a corpus annotates."""
    wanted = set(types)
    return [entity for entity in entities if entity.in_page_text and entity.type in wanted]


def document_counts(
    predicted: Sequence[Entity],
    gold: Sequence[Entity],
    types: Iterable[EntityType],
) -> dict[tuple[str, str], Counts]:
    """Count one document's matches per (match mode, type), plus `ANY_TYPE` for several types.

    Args:
        predicted: What a system found.
        gold: The expected spans.
        types: Types the corpus annotates; other predictions are ignored.

    Returns:
        Counts keyed by `(mode, type)`, with the type as its string value.
    """
    types = sorted(set(types), key=str)
    predicted = scoreable(predicted, types)
    gold = scoreable(gold, types)
    counts: dict[tuple[str, str], Counts] = {}
    for mode in MATCHES:
        for kind in types:
            counts[mode, str(kind)] = match(
                _spans(entity for entity in predicted if entity.type is kind),
                _spans(entity for entity in gold if entity.type is kind),
                mode,
            )
        if len(types) > 1:
            counts[mode, ANY_TYPE] = match(_spans(predicted), _spans(gold), mode)
    return counts


@dataclass(frozen=True, slots=True)
class Interval:
    """A point estimate with its 95 % bootstrap interval."""

    value: float | None
    low: float | None
    high: float | None

    def to_dict(self) -> dict[str, float | None]:
        """Return the interval as plain data, rounded to four places."""
        return {key: _round(getattr(self, key)) for key in ("value", "low", "high")}


@dataclass(frozen=True, slots=True)
class Difference:
    """A paired difference between two systems (candidate minus baseline).

    Attributes:
        delta: The difference on the full data.
        low: 2.5th percentile of the resampled differences.
        high: 97.5th percentile.
        p_value: Two-sided: twice the smaller share of resamples on either
            side of zero, capped at 1.
    """

    delta: float | None
    low: float | None
    high: float | None
    p_value: float | None

    def to_dict(self) -> dict[str, float | None]:
        """Return the difference as plain data, rounded to four places."""
        return {key: _round(getattr(self, key)) for key in ("delta", "low", "high", "p_value")}


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


def resamples(documents: int, count: int, seed: int) -> list[list[int]]:
    """Return `count` lists of document indices drawn with replacement.

    The same lists serve every system of a corpus, which pairs the comparison.
    """
    generator = random.Random(seed)
    population = range(documents)
    return [generator.choices(population, k=documents) for _ in range(count)]


def total(counts: Sequence[Counts]) -> Counts:
    """Sum counts over documents."""
    result = Counts()
    for item in counts:
        result += item
    return result


def resampled_totals(counts: Sequence[Counts], draws: Sequence[Sequence[int]]) -> list[Counts]:
    """Return the summed counts of each resample of documents."""
    columns = [
        [item.predicted for item in counts],
        [item.predicted_matched for item in counts],
        [item.gold for item in counts],
        [item.gold_matched for item in counts],
    ]
    return [
        Counts(*(sum(column[index] for index in indices) for column in columns))
        for indices in draws
    ]


def interval(counts: Sequence[Counts], resampled: Sequence[Counts], metric: str) -> Interval:
    """Return a metric over all documents with its bootstrap interval.

    Args:
        counts: Per-document counts.
        resampled: The same counts summed per resample (`resampled_totals`).
        metric: One of `METRICS`.

    Returns:
        The value and its interval; resamples where the metric is undefined
        are left out.
    """
    values = [value for draw in resampled if (value := draw.metric(metric)) is not None]
    low, high = percentiles(values)
    return Interval(total(counts).metric(metric), low, high)


def paired_difference(
    baseline: tuple[Sequence[Counts], Sequence[Counts]],
    candidate: tuple[Sequence[Counts], Sequence[Counts]],
    metric: str,
) -> Difference:
    """Compare two systems on the same resamples.

    Args:
        baseline: Per-document counts and their resampled totals.
        candidate: The same for the other system, drawn with the same indices.
        metric: One of `METRICS`.

    Returns:
        Candidate minus baseline, with interval and p-value.
    """
    deltas: list[float] = []
    for before_draw, after_draw in zip(baseline[1], candidate[1], strict=True):
        before, after = before_draw.metric(metric), after_draw.metric(metric)
        if before is not None and after is not None:
            deltas.append(after - before)
    before, after = total(baseline[0]).metric(metric), total(candidate[0]).metric(metric)
    delta = None if before is None or after is None else after - before
    low, high = percentiles(deltas)
    if not deltas:
        return Difference(delta, low, high, None)
    at_or_below = sum(1 for value in deltas if value <= 0) / len(deltas)
    at_or_above = sum(1 for value in deltas if value >= 0) / len(deltas)
    return Difference(delta, low, high, min(1.0, 2 * min(at_or_below, at_or_above)))


def percentiles(values: Sequence[float]) -> tuple[float | None, float | None]:
    """Return the 2.5th and 97.5th percentiles (nearest rank), or `None`s if empty."""
    if not values:
        return None, None
    ordered = sorted(values)
    count = len(ordered)
    low = ordered[max(0, math.ceil(0.025 * count) - 1)]
    high = ordered[min(count - 1, math.ceil(0.975 * count) - 1)]
    return low, high
