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

**Leak coverage** (`Coverage`, `document_coverage`) asks what stays readable
once every prediction is redacted, which a partial match cannot tell: "Jan"
found in "Jan Novák" is a partial hit, but "Novák" stays. Characters are
counted, not spans, and only characters that are not whitespace, so a line
break inside a name or two adjacent predictions with a space between them
change nothing. Per type, on each page:

- a gold character is **covered** when any prediction in page text covers
  it, whatever its type and whether or not the corpus scores that type: a
  name tagged as an address, or inside a span of a type the corpus does not
  score, is redacted all the same;
- **residual share**: uncovered gold characters / gold characters, over the
  union of the type's gold spans (what stays readable);
- **hidden whole**: gold spans with every character covered / gold spans
  (the same distinct spans the match counts use). The union of predictions
  counts, so "Jan" and "Novák" found apart hide "Jan Novák" whole; the
  benchmark's "found whole" asks for one entity covering the item instead;
- **over-redaction**: characters of the type's predictions outside every
  scored gold span, per 1,000 characters of page text. Like precision, it
  counts only predictions of scored types: whether a date the corpus does
  not annotate is personal is unknown.

`ANY_TYPE` takes the gold spans and predictions of every scored type
together. All counts are additive over documents, so the same bootstrap
serves both kinds of score.
"""

from __future__ import annotations

import bisect
import functools
import itertools
import math
import operator
import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, fields, replace
from typing import Self

from anonymizer.core.types import Entity, EntityType

STRICT = "strict"
PARTIAL = "partial"
MATCHES = (STRICT, PARTIAL)
ANY_TYPE = "any"
METRICS = ("precision", "recall", "f1", "f2")
COVERAGE_METRICS = ("residual", "hidden_whole", "over_redaction")
OVER_REDACTION_PER = 1000
"""Over-redaction is given per this many characters of page text."""

Span = tuple[int, int, int]
"""Page index, start, end."""


@dataclass(frozen=True, slots=True)
class Tally:
    """Integer counts of one document, additive over documents, and the scores they give."""

    def __add__(self, other: Self) -> Self:
        """Sum two tallies field by field."""
        return self.with_columns(
            [getattr(self, name) + getattr(other, name) for name in self.columns()]
        )

    @classmethod
    def columns(cls) -> tuple[str, ...]:
        """Return the names of the counts, in field order."""
        return tuple(field.name for field in fields(cls))

    def with_columns(self, values: Sequence[int]) -> Self:
        """Return a tally of the same kind holding these counts, in field order."""
        return replace(self, **dict(zip(self.columns(), values, strict=True)))

    def to_dict(self) -> dict[str, int]:
        """Return the counts as plain data."""
        return {name: getattr(self, name) for name in self.columns()}

    def metric(self, name: str) -> float | None:
        """Return a score by name; `None` when it is undefined."""
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Counts(Tally):
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
class Coverage(Tally):
    """Character and item counts of what redaction would leave, additive over documents.

    Characters are those that are not whitespace (see the module docstring).

    Attributes:
        gold_characters: Characters inside the type's gold spans.
        residual_characters: Of those, characters no prediction covers.
        gold_items: Distinct gold spans of the type.
        hidden_items: Gold spans with every character covered.
        over_characters: Characters of the type's predictions outside every
            scored gold span.
        text_characters: Characters of page text.
    """

    gold_characters: int = 0
    residual_characters: int = 0
    gold_items: int = 0
    hidden_items: int = 0
    over_characters: int = 0
    text_characters: int = 0

    def metric(self, name: str) -> float | None:
        """Return one of `COVERAGE_METRICS` by name; `None` when it is undefined."""
        if name == "residual":
            return _share(self.residual_characters, self.gold_characters)
        if name == "hidden_whole":
            return _share(self.hidden_items, self.gold_items)
        if name == "over_redaction":
            share = _share(self.over_characters, self.text_characters)
            return None if share is None else OVER_REDACTION_PER * share
        msg = f"unknown metric {name!r}"
        raise ValueError(msg)


def _share(part: int, whole: int) -> float | None:
    return part / whole if whole else None


Ranges = list[tuple[int, int]]
"""Disjoint, sorted half-open character ranges of one page."""


def document_coverage(
    predicted: Sequence[Entity],
    gold: Sequence[Entity],
    types: Iterable[EntityType],
    pages: Sequence[str],
) -> dict[str, Coverage]:
    """Count what one document would keep readable, per type, plus `ANY_TYPE` for several types.

    Args:
        predicted: What a system found; every prediction in page text covers,
            whatever its type.
        gold: The expected spans.
        types: Types the corpus annotates; only their gold spans are counted,
            and only their predictions count as over-redaction.
        pages: The text of each page, by page index; offsets are page-local.

    Returns:
        Coverage keyed by the type's string value.
    """
    types = sorted(set(types), key=str)
    redacted = _spans(entity for entity in predicted if entity.in_page_text)
    scored_predictions = scoreable(predicted, types)
    scored_gold = scoreable(gold, types)
    groups = {
        str(kind): (
            _spans(entity for entity in scored_predictions if entity.type is kind),
            _spans(entity for entity in scored_gold if entity.type is kind),
        )
        for kind in types
    }
    if len(types) > 1:
        groups[ANY_TYPE] = (_spans(scored_predictions), _spans(scored_gold))
    all_gold = _spans(scored_gold)
    coverage = {kind: Coverage() for kind in groups}
    for page_index, text in enumerate(pages):
        visible = _visible_prefix(text)
        covered = _page_ranges(redacted, page_index, len(text))
        gold_anywhere = _page_ranges(all_gold, page_index, len(text))
        for kind, (kind_predicted, kind_gold) in groups.items():
            coverage[kind] += _page_coverage(
                visible,
                covered,
                gold_anywhere,
                _page_ranges(kind_predicted, page_index, len(text)),
                sorted({_clamp(span, len(text)) for span in kind_gold if span[0] == page_index}),
            )
    return coverage


def _page_coverage(
    visible: Sequence[int],
    covered: Ranges,
    gold_anywhere: Ranges,
    kind_predicted: Ranges,
    kind_gold: Sequence[tuple[int, int]],
) -> Coverage:
    gold_ranges = _union(kind_gold)
    gold_characters = _count(visible, gold_ranges)
    # A span with no visible character hides nothing and leaks nothing: it counts as hidden.
    hidden = sum(
        1
        for item in kind_gold
        if _count(visible, [item]) == _count(visible, _intersect([item], covered))
    )
    return Coverage(
        gold_characters=gold_characters,
        residual_characters=gold_characters - _count(visible, _intersect(gold_ranges, covered)),
        gold_items=len(kind_gold),
        hidden_items=hidden,
        over_characters=_count(visible, kind_predicted)
        - _count(visible, _intersect(kind_predicted, gold_anywhere)),
        text_characters=visible[-1],
    )


def _visible_prefix(text: str) -> list[int]:
    """Characters that are not whitespace before each offset (`len(text) + 1` entries)."""
    return [0, *itertools.accumulate(0 if char.isspace() else 1 for char in text)]


def _clamp(span: Span, length: int) -> tuple[int, int]:
    _, start, end = span
    return min(start, length), min(end, length)


def _page_ranges(spans: Iterable[Span], page_index: int, length: int) -> Ranges:
    return _union(_clamp(span, length) for span in spans if span[0] == page_index)


def _union(ranges: Iterable[tuple[int, int]]) -> Ranges:
    """Merge overlapping and adjacent ranges."""
    merged: Ranges = []
    for start, end in sorted(ranges):
        if start >= end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _intersect(first: Ranges, second: Ranges) -> Ranges:
    """Intersect two lists of disjoint sorted ranges."""
    result: Ranges = []
    starts = [start for start, _ in second]
    for start, end in first:
        index = max(0, bisect.bisect_right(starts, start) - 1)
        for other_start, other_end in second[index:]:
            if other_start >= end:
                break
            low, high = max(start, other_start), min(end, other_end)
            if low < high:
                result.append((low, high))
    return result


def _count(visible: Sequence[int], ranges: Iterable[tuple[int, int]]) -> int:
    return sum(visible[end] - visible[start] for start, end in ranges)


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


def total[T: Tally](counts: Sequence[T]) -> T:
    """Sum per-document tallies (at least one) over documents."""
    return functools.reduce(operator.add, counts)


def resampled_totals[T: Tally](counts: Sequence[T], draws: Sequence[Sequence[int]]) -> list[T]:
    """Return the summed per-document tallies (at least one) of each resample of documents."""
    first = counts[0]
    columns = [[getattr(item, name) for item in counts] for name in first.columns()]
    return [
        first.with_columns([sum(column[index] for index in indices) for column in columns])
        for indices in draws
    ]


def interval[T: Tally](counts: Sequence[T], resampled: Sequence[T], metric: str) -> Interval:
    """Return a metric over all documents with its bootstrap interval.

    Args:
        counts: Per-document counts (`Counts` or `Coverage`).
        resampled: The same counts summed per resample (`resampled_totals`).
        metric: One of `METRICS` for `Counts`, of `COVERAGE_METRICS` for `Coverage`.

    Returns:
        The value and its interval; resamples where the metric is undefined
        are left out.
    """
    values = [value for draw in resampled if (value := draw.metric(metric)) is not None]
    low, high = percentiles(values)
    return Interval(total(counts).metric(metric), low, high)


def paired_difference[T: Tally](
    baseline: tuple[Sequence[T], Sequence[T]],
    candidate: tuple[Sequence[T], Sequence[T]],
    metric: str,
) -> Difference:
    """Compare two systems on the same resamples.

    Args:
        baseline: Per-document counts and their resampled totals.
        candidate: The same for the other system, drawn with the same indices.
        metric: A metric of the counts' kind, as for `interval`.

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
