"""Mean and spread of a trained model's scores across the seeds it was trained with.

The bootstrap intervals of a run resample documents: they say how much a
score depends on which documents were drawn, not on how training happened
to go. A system whose model was trained with several seeds (`seeds` in the
run config, `train --seed N`) runs once per replicate; this module sums the
replicates' scores up per corpus, match mode, type and metric as the mean,
the sample standard deviation, the lowest and the highest value.

A comparison naming such a system is also made seed by seed: replicate
`sN` of the candidate against replicate `sN` of the baseline (trained on the
same examples in the same order), or against the baseline itself when it
has no replicates (GLiNER zero-shot). The difference's mean and spread, and
on how many seeds the candidate was better, say whether a change of the
loss is larger than the change between two seeds of one loss.
"""

from __future__ import annotations

import statistics
from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any

from experiments.config import Replicates
from experiments.metrics import ANY_TYPE, MATCHES, METRICS

UNDEFINED = "\N{EN DASH}"
"""Shown for a score that is undefined on every replicate."""

_METRIC_COLUMNS = ("precision", "recall", "f1", "f2")

Values = Callable[[str, str, str], Mapping[str, float | None]]
"""A score per replicate, for one match mode, type and metric."""


def summarize(
    corpus: Mapping[str, Any],
    replicates: Mapping[str, Replicates],
    compare: Sequence[tuple[str, str]],
) -> dict[str, Any]:
    """Sum up the replicates of each seeded system on one corpus.

    Args:
        corpus: One corpus of a run's results, with every system's scores.
        replicates: The seeded systems, by name.
        compare: The run's comparisons; those naming a seeded system are
            also made seed by seed.

    Returns:
        `systems`: per seeded system, its replicates and, per mode, type and
        metric, the spread of their values; `comparisons`: per comparison
        naming a seeded system, the pairs and the spread of their differences.
    """
    scores = {name: system["scores"] for name, system in corpus["systems"].items()}

    def values_of(members: Mapping[str, str]) -> Values:
        return lambda mode, kind, metric: {
            key: scores[system][mode][kind][metric]["value"] for key, system in members.items()
        }

    def differences_of(pairs: Mapping[str, tuple[str, str]]) -> Values:
        return lambda mode, kind, metric: {
            key: _difference(
                scores[before][mode][kind][metric]["value"],
                scores[after][mode][kind][metric]["value"],
            )
            for key, (before, after) in pairs.items()
        }

    summary: dict[str, Any] = {"systems": {}, "comparisons": []}
    for name, group in replicates.items():
        members = group.members()
        summary["systems"][name] = {
            "replicates": members,
            "scores": _spreads(scores[name], values_of(members)),
        }
    for baseline, candidate in compare:
        pairs = _pairs(baseline, candidate, replicates)
        if pairs is None:
            continue
        summary["comparisons"].append(
            {
                "baseline": baseline,
                "candidate": candidate,
                "pairs": {key: list(pair) for key, pair in pairs.items()},
                "differences": _spreads(scores[baseline], differences_of(pairs)),
            }
        )
    return summary


def _pairs(
    baseline: str, candidate: str, replicates: Mapping[str, Replicates]
) -> dict[str, tuple[str, str]] | None:
    """Pair replicates by seed; a system without replicates stands beside each one."""
    before, after = replicates.get(baseline), replicates.get(candidate)
    if before is not None and after is not None:
        theirs = before.members()
        return {
            key: (theirs[key], system) for key, system in after.members().items() if key in theirs
        }
    if after is not None:
        return {key: (baseline, system) for key, system in after.members().items()}
    if before is not None:
        return {key: (system, candidate) for key, system in before.members().items()}
    return None


def _difference(before: float | None, after: float | None) -> float | None:
    return None if before is None or after is None else after - before


def _spreads(template: Mapping[str, Mapping[str, Any]], values: Values) -> dict[str, Any]:
    """The spread of `values` for every mode, type and metric that `template` scores."""
    return {
        mode: {
            kind: {metric: spread(values(mode, kind, metric)) for metric in METRICS}
            for kind in template[mode]
        }
        for mode in MATCHES
    }


def spread(values: Mapping[str, float | None]) -> dict[str, Any]:
    """Return the mean, sample standard deviation, range and count of the defined values.

    The standard deviation needs two values. `above_zero` counts the values
    above 0: for differences, the seeds on which the candidate was better.
    The values are kept by replicate, so a table can be checked against the
    systems' own rows.
    """
    defined = [number for number in values.values() if number is not None]
    return {
        "mean": statistics.fmean(defined) if defined else None,
        "sd": statistics.stdev(defined) if len(defined) > 1 else None,
        "low": min(defined, default=None),
        "high": max(defined, default=None),
        "n": len(defined),
        "above_zero": sum(number > 0 for number in defined),
        "values": dict(values),
    }


def markdown_lines(corpus: Mapping[str, Any]) -> list[str]:
    """Render a corpus's seed summary as Markdown tables; nothing without one."""
    summary = corpus.get("seeds")
    if not summary:
        return []
    lines = [
        "### Across seeds",
        "",
        "Mean ± sample standard deviation over n replicates, each scored on all documents.",
        "",
    ]
    lines += _table(
        ("type", "match", "system", "n", "P", "R", "F1", "F2"),
        list(_system_rows(summary["systems"])),
    )
    lines.append("")
    if summary["comparisons"]:
        lines += [
            "### Seed by seed (paired)",
            "",
            "Candidate minus baseline per seed: mean ± sd; on how many seeds F2 rose.",
            "",
        ]
        lines += _table(
            ("type", "match", "baseline → candidate", "n", "ΔP", "ΔR", "ΔF1", "ΔF2", "F2 rose"),
            list(_comparison_rows(summary["comparisons"])),
        )
        lines.append("")
    return lines


def _system_rows(systems: Mapping[str, Any]) -> Iterator[list[str]]:
    for name, system in systems.items():
        for mode in MATCHES:
            for kind in _ordered(system["scores"][mode]):
                metrics = system["scores"][mode][kind]
                yield [
                    kind,
                    mode,
                    name,
                    str(metrics["f2"]["n"]),
                    *(format_spread(metrics[metric]) for metric in _METRIC_COLUMNS),
                ]


def _comparison_rows(comparisons: Sequence[Mapping[str, Any]]) -> Iterator[list[str]]:
    for comparison in comparisons:
        for mode in MATCHES:
            for kind in _ordered(comparison["differences"][mode]):
                metrics = comparison["differences"][mode][kind]
                f2 = metrics["f2"]
                yield [
                    kind,
                    mode,
                    f"{comparison['baseline']} → {comparison['candidate']}",
                    str(f2["n"]),
                    *(format_spread(metrics[metric], signed=True) for metric in _METRIC_COLUMNS),
                    f"{f2['above_zero']} / {f2['n']}",
                ]


def format_spread(summary: Mapping[str, Any], *, signed: bool = False) -> str:
    """Return `0.846 ± 0.012`, the mean alone for one value, or `UNDEFINED`."""
    if summary["mean"] is None:
        return UNDEFINED
    mean = f"{summary['mean']:+.3f}" if signed else f"{summary['mean']:.3f}"
    return mean if summary["sd"] is None else f"{mean} ± {summary['sd']:.3f}"


def _ordered(scores: Mapping[str, Any]) -> list[str]:
    kinds = sorted(kind for kind in scores if kind != ANY_TYPE)
    return [*kinds, ANY_TYPE] if ANY_TYPE in scores else kinds


def _table(header: tuple[str, ...], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return lines + ["| " + " | ".join(row) + " |" for row in rows]
