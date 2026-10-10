"""Training examples for GLiNER from the corpora, in the model's own tokens.

GLiNER trains on examples of `tokenized_text` (its tokens, as
`detect.gliner.gliner_tokens` splits a text) and `ner` spans `[first, last,
label]` over token indices, the last one included. A corpus is read through
`datasets.load_corpus`, so training sees the same text, NFC normalisation and
gold spans as the evaluation, and each page is cut into examples:

- **Labels are the prompts of `GlinerDetector`**: `person`, `street address`
  and the `organization` distractor, in that order. An example is prompted
  only with the labels its corpus marks throughout (`ner_labels`), because a
  label asked for and never marked teaches the model that nothing in the
  corpus is one: UNER marks no addresses, OpenPII no organisations.
- **At most `MAX_TOKENS` tokens per example**, the length of the detector's
  windows, well under the model's 384. A cut never falls inside a gold span,
  and falls after a line break where the second half of the window has one.
- **Spans cover whole tokens.** A gold span starting or ending inside a token
  takes the whole token, as the detector widens its spans to whole words.
- **A span wider than the model's `max_width` (12 tokens)** cannot be
  predicted, and its parts would be taught as non-entities, so an example
  holding one is left out and counted (`Conversion.too_wide`).
"""

from __future__ import annotations

import random
from bisect import bisect_left, bisect_right
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from anonymizer.core.detect.gliner import DEFAULT_DISTRACTORS, DEFAULT_LABELS, gliner_tokens
from anonymizer.core.types import Entity, EntityType, Page

from experiments.datasets import Corpus, DatasetSpec

MAX_TOKENS = 150
"""Tokens per example: the detector's window (`gliner.WINDOW_TOKENS`)."""

MAX_SPAN_TOKENS = 12
"""The base model's `max_width`: the widest span it scores."""


def training_labels(
    labels: Mapping[str, EntityType] = DEFAULT_LABELS,
    distractors: Sequence[str] = DEFAULT_DISTRACTORS,
) -> dict[EntityType, str]:
    """Return the prompt label of each type taught, in the detector's prompt order.

    A distractor's label is the name of the type it stands for
    (`organization`), so the corpora's spans of that type teach it.

    Raises:
        ValueError: If a distractor names no entity type.
    """
    by_type = {kind: label for label, kind in labels.items()}
    for label in distractors:
        try:
            by_type[EntityType(label)] = label
        except ValueError as error:
            msg = f"distractor {label!r} names no entity type to train it on"
            raise ValueError(msg) from error
    return by_type


@dataclass(frozen=True, slots=True)
class Example:
    """One training example.

    Attributes:
        tokens: The text's GLiNER tokens.
        spans: `(first, last, label)`, token indices, the last one included.
        labels: The labels the example is prompted with.
    """

    tokens: tuple[str, ...]
    spans: tuple[tuple[int, int, str], ...]
    labels: tuple[str, ...]

    def to_gliner(self) -> dict[str, Any]:
        """Return the example in the format gliner's data collator reads."""
        return {
            "tokenized_text": list(self.tokens),
            "ner": [list(span) for span in self.spans],
            "ner_labels": list(self.labels),
        }


@dataclass
class Conversion:
    """What converting corpora produced, and what was drawn from it, as counts.

    Attributes:
        examples: Examples converted, per corpus key.
        too_wide: Spans wider than `MAX_SPAN_TOKENS`, per label; the examples
            holding them are left out.
        drawn: Examples drawn for training, per corpus key.
        spans: Spans in the drawn examples, per label.
        tokens: Tokens in the drawn examples.
        empty: Drawn examples holding no span.
    """

    examples: Counter[str] = field(default_factory=Counter)
    too_wide: Counter[str] = field(default_factory=Counter)
    drawn: Counter[str] = field(default_factory=Counter)
    spans: Counter[str] = field(default_factory=Counter)
    tokens: int = 0
    empty: int = 0

    def add_drawn(self, key: str, examples: Sequence[Example]) -> None:
        """Count the examples drawn from one corpus."""
        self.drawn[key] += len(examples)
        for example in examples:
            self.spans.update(label for *_, label in example.spans)
            self.tokens += len(example.tokens)
            self.empty += not example.spans

    def to_dict(self) -> dict[str, Any]:
        """Return the counts as plain data, for the results file."""
        return {
            "converted": dict(sorted(self.examples.items())),
            "too_wide": dict(sorted(self.too_wide.items())),
            "drawn": dict(sorted(self.drawn.items())),
            "spans": dict(sorted(self.spans.items())),
            "tokens": self.tokens,
            "empty": self.empty,
        }


def corpus_labels(spec: DatasetSpec, taught: Mapping[EntityType, str]) -> tuple[str, ...]:
    """Return the labels a corpus's examples are prompted with: those it marks throughout."""
    marked = spec.types | spec.unscored
    return tuple(label for kind, label in taught.items() if kind in marked)


def corpus_examples(
    corpus: Corpus,
    spec: DatasetSpec,
    conversion: Conversion,
    *,
    taught: Mapping[EntityType, str] | None = None,
    max_tokens: int = MAX_TOKENS,
) -> list[Example]:
    """Cut a corpus's pages into training examples.

    Args:
        corpus: The corpus, read with `datasets.load_corpus`.
        spec: Its dataset, for the types it marks.
        conversion: Receives the counts.
        taught: Type → label; `training_labels()` when omitted.
        max_tokens: Tokens per example at most.

    Returns:
        The examples in corpus order.
    """
    taught = taught if taught is not None else training_labels()
    labels = corpus_labels(spec, taught)
    examples: list[Example] = []
    for gold in corpus.documents:
        for page in gold.document.pages:
            on_page = [entity for entity in gold.gold if entity.page_index == page.index]
            for example in page_examples(page, on_page, taught, labels, max_tokens, conversion):
                conversion.examples[corpus.key] += 1
                examples.append(example)
    return examples


def page_examples(
    page: Page,
    gold: Iterable[Entity],
    taught: Mapping[EntityType, str],
    labels: Sequence[str],
    max_tokens: int,
    conversion: Conversion,
) -> Iterator[Example]:
    """Yield the examples of one page; spans of types not prompted are left out.

    Args:
        page: The page.
        gold: Its gold spans.
        taught: Type → label.
        labels: The labels the examples are prompted with.
        max_tokens: Tokens per example at most.
        conversion: Receives the count of spans too wide to learn.
    """
    tokens = gliner_tokens(page.text)
    spans = token_spans(tokens, gold, taught, labels)
    for first, end in cut(page.text, tokens, spans, max_tokens):
        inside = [
            (start - first, last - first, label)
            for start, last, label in spans
            if first <= start and last < end
        ]
        too_wide = [label for start, last, label in inside if last - start + 1 > MAX_SPAN_TOKENS]
        if too_wide:
            conversion.too_wide.update(too_wide)
            continue
        yield Example(
            tokens=tuple(page.text[start:stop] for start, stop in tokens[first:end]),
            spans=tuple(inside),
            labels=tuple(labels),
        )


def token_spans(
    tokens: Sequence[tuple[int, int]],
    gold: Iterable[Entity],
    taught: Mapping[EntityType, str],
    labels: Sequence[str],
) -> list[tuple[int, int, str]]:
    """Return gold spans as `(first, last, label)` over a text's GLiNER tokens.

    A span takes every token it touches; one touching no token (whitespace
    only) is dropped. Types without a prompted label are left out.

    Args:
        tokens: The text's tokens as character spans (`gliner_tokens`).
        gold: Gold spans with character offsets into the same text.
        taught: Type → label.
        labels: The labels prompted.
    """
    starts = [start for start, _ in tokens]
    ends = [end for _, end in tokens]
    spans: set[tuple[int, int, str]] = set()
    for entity in gold:
        label = taught.get(entity.type)
        if label is None or label not in labels:
            continue
        start, end = entity.span
        # The first token ending after the span starts, the last starting before it ends.
        first, last = bisect_right(ends, start), bisect_left(starts, end) - 1
        if first <= last:
            spans.add((first, last, label))
    return sorted(spans)


def cut(
    text: str,
    tokens: Sequence[tuple[int, int]],
    spans: Sequence[tuple[int, int, str]],
    max_tokens: int,
) -> Iterator[tuple[int, int]]:
    """Yield `(first, end)` token ranges of at most `max_tokens`, never inside a span.

    A cut between token `b - 1` and token `b` is allowed when no span holds
    both. The latest allowed cut after a line break in the second half of
    the range is taken; else the latest allowed cut; a span longer than the
    whole range (never under `MAX_SPAN_TOKENS`) is cut through.
    """
    blocked = {boundary for start, last, _ in spans for boundary in range(start + 1, last + 1)}
    first = 0
    while first < len(tokens):
        end = min(first + max_tokens, len(tokens))
        if end < len(tokens):
            allowed = [b for b in range(end, first, -1) if b not in blocked]
            at_line_break = [
                b
                for b in allowed
                if b > first + max_tokens // 2 and "\n" in text[tokens[b - 1][1] : tokens[b][0]]
            ]
            if at_line_break:
                end = at_line_break[0]
            elif allowed:
                end = allowed[0]
        yield first, end
        first = end


def sample(examples: list[Example], count: int | None, seed: int) -> list[Example]:
    """Return `count` examples drawn without replacement, seeded; all of them when `None`."""
    if count is None or count >= len(examples):
        return list(examples)
    return random.Random(seed).sample(examples, count)
