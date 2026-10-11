"""Recall per kind of gold span, for corpora whose spans carry tags (the name-forms set).

Each tagged gold span counts under every tag it has (`name_forms.Tag`: form,
case, form and case, declension class, gender), matched as `metrics.match`
matches any span: strict or partial, against predictions of its type. Only
recall is defined per tag: a prediction has no tag, so precision stays in the
standard tables. Intervals resample whole texts, on the same draws as every
other score of the corpus.

Texts with no gold span name nobody; the predictions in them are false
alarms and are counted on their own.

The tables are appended to `<name>.md` and `<name>.tex` after the standard
ones (`markdown`, `latex`), from the results file alone.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Any

from anonymizer.core.types import Entity, EntityType

from experiments.datasets import Corpus, GoldDocument
from experiments.declension import Case
from experiments.metrics import (
    MATCHES,
    PARTIAL,
    STRICT,
    Counts,
    Span,
    interval,
    match,
    resampled_totals,
    scoreable,
    total,
)
from experiments.name_forms import FORMS, Tag

FACETS = ("form", "form-case", "case", "class", "gender")
"""Facets in table order."""

_FACET_TITLES = {
    "form": "form",
    "form-case": "form / case",
    "case": "case",
    "class": "declension class",
    "gender": "gender",
}
_MATCH_TITLES = {PARTIAL: "partial match", STRICT: "strict match"}
_CASES = tuple(str(case) for case in Case)


class PhenomenonTally:
    """Collects per-document counts per tag while a system runs over a corpus."""

    def __init__(self, corpus: Corpus) -> None:
        """Prepare a tally for every tag the corpus's gold spans carry."""
        self.tags: list[Tag] = sorted(
            {tag for gold in corpus.documents for tags in gold.tags.values() for tag in tags}
        )
        self.counts: dict[tuple[str, Tag], list[Counts]] = {
            (mode, tag): [] for mode in MATCHES for tag in self.tags
        }
        self.control_texts = 0
        self.control_flagged = 0
        self.control_predictions = 0

    def add(
        self, found: Sequence[Entity], gold: GoldDocument, types: frozenset[EntityType]
    ) -> None:
        """Count one document; every tag gets an entry, so resample indices stay aligned."""
        predicted = scoreable(found, types)
        expected = scoreable(gold.gold, types)
        if not expected:
            self.control_texts += 1
            self.control_flagged += bool(predicted)
            self.control_predictions += len(predicted)
        by_tag: dict[Tag, list[Entity]] = {}
        for entity in expected:
            if entity.page_index is None:
                continue
            start, end = entity.span
            for tag in gold.tags.get((entity.page_index, start, end), ()):
                by_tag.setdefault(tag, []).append(entity)
        for mode in MATCHES:
            for tag in self.tags:
                self.counts[mode, tag].append(_recall_counts(predicted, by_tag.get(tag, []), mode))

    def results(self, draws: Sequence[Sequence[int]]) -> dict[str, Any]:
        """Return recall per match mode, facet and value, and the false alarms on control texts."""
        recall: dict[str, dict[str, dict[str, Any]]] = {mode: {} for mode in MATCHES}
        for (mode, (facet, value)), per_document in self.counts.items():
            summed = total(per_document)
            recall[mode].setdefault(facet, {})[value] = {
                "gold": summed.gold,
                "found": summed.gold_matched,
                "recall": interval(
                    per_document, resampled_totals(per_document, draws), "recall"
                ).to_dict(),
            }
        return {
            "recall": recall,
            "control": {
                "texts": self.control_texts,
                "flagged": self.control_flagged,
                "predictions": self.control_predictions,
            },
        }


def _recall_counts(predicted: list[Entity], gold: list[Entity], mode: str) -> Counts:
    """Gold spans and those found; predictions are matched per type, as in `metrics`."""
    found = 0
    for kind in {entity.type for entity in gold}:
        counts = match(
            _spans(entity for entity in predicted if entity.type is kind),
            _spans(entity for entity in gold if entity.type is kind),
            mode,
        )
        found += counts.gold_matched
    return Counts(gold=len(gold), gold_matched=found)


def _spans(entities: Iterator[Entity]) -> set[Span]:
    return {
        (entity.page_index, *entity.span) for entity in entities if entity.page_index is not None
    }


# --- Tables -------------------------------------------------------------------


def markdown(results: dict[str, Any]) -> str:
    """Render the recall tables of every tagged corpus; empty when there is none."""
    lines: list[str] = []
    for key, corpus in results["corpora"].items():
        systems = _tagged_systems(corpus)
        if not systems:
            continue
        lines += [f"## {key} · recall by name form", ""]
        for mode in (PARTIAL, STRICT):
            lines += [
                f"### {_MATCH_TITLES[mode].capitalize()}",
                "",
                "Names found · recall [95 % bootstrap interval over texts].",
                "",
            ]
            header = ["facet", "kind", "gold", *systems]
            lines += ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
            for facet, value, gold, cells in _rows(corpus, systems, mode):
                lines.append(f"| {facet} | {value} | {gold} | " + " | ".join(cells) + " |")
            lines.append("")
        lines += [_control_line(corpus, systems), ""]
    return "\n".join(lines)


def latex(results: dict[str, Any]) -> str:
    r"""Render the recall tables as LaTeX (booktabs; `\ci` as in `report.latex`)."""
    lines: list[str] = []
    for key, corpus in results["corpora"].items():
        systems = _tagged_systems(corpus)
        if not systems:
            continue
        for mode in (PARTIAL, STRICT):
            label = _escape(f"{results['name']}-{key}-forms-{mode}".replace("/", "-"))
            lines += [
                "\\begin{table}[htbp]",
                "\\centering",
                "\\small",
                "\\begin{tabular}{llr" + "r" * len(systems) + "}",
                "\\toprule",
                " & ".join(["Facet", "Kind", "Gold", *(_escape(name) for name in systems)])
                + " \\\\",
                "\\midrule",
            ]
            for facet, value, gold, cells in _rows(corpus, systems, mode, latex=True):
                lines.append(
                    " & ".join([_escape(facet), _escape(value), str(gold), *cells]) + " \\\\"
                )
            lines += [
                "\\bottomrule",
                "\\end{tabular}",
                f"\\caption{{{_escape(key)}: names found and recall by form, "
                f"{_MATCH_TITLES[mode]}; 95\\,\\% bootstrap intervals over texts.}}",
                f"\\label{{tab:{label}}}",
                "\\end{table}",
                "",
            ]
    return "\n".join(lines)


def _tagged_systems(corpus: dict[str, Any]) -> list[str]:
    return [name for name, system in corpus["systems"].items() if "phenomena" in system]


def _rows(
    corpus: dict[str, Any], systems: list[str], mode: str, *, latex: bool = False
) -> Iterator[tuple[str, str, int, list[str]]]:
    first = corpus["systems"][systems[0]]["phenomena"]["recall"][mode]
    for facet in FACETS:
        for value in sorted(first.get(facet, {}), key=lambda item: _order(facet, item)):
            cells = []
            for name in systems:
                score = corpus["systems"][name]["phenomena"]["recall"][mode][facet][value]
                cells.append(_cell(score, latex=latex))
            yield _FACET_TITLES[facet], value, first[facet][value]["gold"], cells


def _order(facet: str, value: str) -> tuple[int, int, str]:
    """Forms in `FORMS` order, cases in grammar order, anything else by name."""
    form, _, case = value.partition("/")
    if facet == "case":
        return (0, _CASES.index(value) if value in _CASES else len(_CASES), value)
    if facet in {"form", "form-case"}:
        form_rank = FORMS.index(form) if form in FORMS else len(FORMS)
        return (form_rank, _CASES.index(case) if case in _CASES else -1, value)
    return (0, 0, value)


def _cell(score: dict[str, Any], *, latex: bool) -> str:
    recall = score["recall"]
    if recall["value"] is None:
        return "--" if latex else "\N{EN DASH}"
    if recall["low"] is None or recall["high"] is None:
        value = f"{recall['value']:.3f}"
    elif latex:
        value = f"{recall['value']:.3f} \\ci{{{recall['low']:.2f}}}{{{recall['high']:.2f}}}"
    else:
        value = f"{recall['value']:.3f} [{recall['low']:.2f}, {recall['high']:.2f}]"
    separator = "~$\\cdot$~" if latex else " · "
    return f"{score['found']}{separator}{value}"


def _control_line(corpus: dict[str, Any], systems: list[str]) -> str:
    texts = corpus["systems"][systems[0]]["phenomena"]["control"]["texts"]
    parts = []
    for name in systems:
        control = corpus["systems"][name]["phenomena"]["control"]
        parts.append(f"{name} in {control['flagged']} ({control['predictions']} spans)")
    return f"Texts naming nobody: {texts}. False alarms in them: " + ", ".join(parts) + "."


def _escape(text: str) -> str:
    for char, escaped in (("\\", "\\textbackslash{}"), ("_", "\\_"), ("&", "\\&"), ("%", "\\%")):
        text = text.replace(char, escaped)
    return text
