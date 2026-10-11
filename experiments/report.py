"""Markdown and LaTeX tables from a results file.

Both are generated from the results dictionary alone, so a table in the
thesis can be regenerated from a stored `<name>.json` without rerunning.
Values are shown as `0.846 [0.80, 0.88]`: the score on all documents and its
95 % bootstrap interval. A results file written before leak coverage was
scored has no coverage tables; everything else is rendered as before.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from experiments.metrics import ANY_TYPE, COVERAGE_METRICS, MATCHES, PARTIAL, STRICT

UNDEFINED = "\N{EN DASH}"
"""Shown for a score that is undefined, e.g. precision without predictions."""

_MATCH_TITLES = {PARTIAL: "Partial match", STRICT: "Strict match"}
_HEADINGS = ("type", "system", "P", "R", "F1", "F2", "found / gold")
_METRIC_COLUMNS = ("precision", "recall", "f1", "f2")
_COVERAGE_TITLE = "Leak coverage"
_COVERAGE_NOTE = (
    "Characters other than whitespace. Residual: share of gold characters no prediction "
    "covers, whatever its type (lower is better). Hidden whole: gold spans with every "
    "character covered. Over: characters predicted outside every gold span, per 1,000 "
    "characters of text."
)
_COVERAGE_HEADINGS = ("type", "system", "residual", "hidden whole", "over / 1k", "hidden / gold")
_COVERAGE_DIGITS = {"residual": 3, "hidden_whole": 3, "over_redaction": 1}


def markdown(results: dict[str, Any]) -> str:
    """Render a results dictionary as Markdown tables."""
    lines = [f"# {results['name']}", ""]
    if results.get("description"):
        lines += [results["description"].strip(), ""]
    lines += [_provenance(results), ""]
    for key, corpus in results["corpora"].items():
        lines += [
            f"## {key} · {corpus['language']} · {corpus['role']}",
            "",
            _corpus_summary(corpus),
            "",
        ]
        for mode in (PARTIAL, STRICT):
            lines += [f"### {_MATCH_TITLES[mode]}", ""]
            lines += _table(_HEADINGS, list(_score_rows(corpus, mode)))
            lines.append("")
        if _has_coverage(corpus):
            lines += [f"### {_COVERAGE_TITLE}", "", _COVERAGE_NOTE, ""]
            lines += _table(_COVERAGE_HEADINGS, list(_coverage_rows(corpus)))
            lines.append("")
        for comparison in corpus["comparisons"]:
            lines += [
                f"### {comparison['baseline']} → {comparison['candidate']} (paired)",
                "",
                "Candidate minus baseline; p is two-sided, from the same resamples.",
                "",
            ]
            lines += _table(
                ("type", "match", "ΔP", "ΔR", "ΔF1", "ΔF2", "p (F2)"),
                list(_difference_rows(comparison)),
            )
            lines.append("")
            if "coverage" in comparison:
                lines += ["Leak coverage, candidate minus baseline:", ""]
                lines += _table(
                    ("type", "Δresidual", "Δhidden whole", "Δover / 1k", "p (residual)"),
                    list(_coverage_difference_rows(comparison["coverage"])),
                )
                lines.append("")
    return "\n".join(lines)


def _provenance(results: dict[str, Any]) -> str:
    git = results["git"]
    commit = (git.get("commit") or "unknown")[:10]
    state = " (uncommitted changes)" if git.get("dirty") else ""
    models = ", ".join(f"{name} @ {version[:10]}" for name, version in results["models"].items())
    return (
        f"Stage: {results['stage']} · commit {commit}{state} · {results['created']} · "
        f"seed {results['seed']}, {results['resamples']} resamples · "
        f"models: {models or 'none'} · tool {results['tool_version']}"
    )


def _corpus_summary(corpus: dict[str, Any]) -> str:
    gold = ", ".join(f"{kind} {count}" for kind, count in corpus["gold"].items())
    return (
        f"{corpus['documents']} documents, {corpus['pages']} pages, "
        f"{corpus['sentences']} sentences or records. Gold spans: {gold}."
    )


def _ordered_types(scores: dict[str, Any]) -> list[str]:
    kinds = sorted(kind for kind in scores if kind != ANY_TYPE)
    return [*kinds, ANY_TYPE] if ANY_TYPE in scores else kinds


def _score_rows(corpus: dict[str, Any], mode: str) -> Iterator[list[str]]:
    systems = corpus["systems"]
    first = next(iter(systems.values()))
    for kind in _ordered_types(first["scores"][mode]):
        for name, system in systems.items():
            score = system["scores"][mode][kind]
            counts = score["counts"]
            yield [
                kind,
                name,
                *(format_interval(score[metric]) for metric in _METRIC_COLUMNS),
                f"{counts['gold_matched']} / {counts['gold']}",
            ]


def _has_coverage(corpus: dict[str, Any]) -> bool:
    return all("coverage" in system for system in corpus["systems"].values())


def _coverage_rows(corpus: dict[str, Any]) -> Iterator[list[str]]:
    systems = corpus["systems"]
    first = next(iter(systems.values()))
    for kind in _ordered_types(first["coverage"]):
        for name, system in systems.items():
            coverage = system["coverage"][kind]
            counts = coverage["counts"]
            yield [
                kind,
                name,
                *(
                    format_interval(coverage[metric], _COVERAGE_DIGITS[metric])
                    for metric in COVERAGE_METRICS
                ),
                f"{counts['hidden_items']} / {counts['gold_items']}",
            ]


def _coverage_difference_rows(differences: dict[str, Any]) -> Iterator[list[str]]:
    for kind in _ordered_types(differences):
        metrics = differences[kind]
        yield [
            kind,
            *(
                format_difference(metrics[metric], _COVERAGE_DIGITS[metric])
                for metric in COVERAGE_METRICS
            ),
            _number(metrics["residual"]["p_value"], digits=3),
        ]


def _difference_rows(comparison: dict[str, Any]) -> Iterator[list[str]]:
    for mode in MATCHES:
        differences = comparison["differences"][mode]
        for kind in _ordered_types(differences):
            metrics = differences[kind]
            yield [
                kind,
                mode,
                *(format_difference(metrics[metric]) for metric in _METRIC_COLUMNS),
                _number(metrics["f2"]["p_value"], digits=3),
            ]


def format_interval(interval: dict[str, float | None], digits: int = 3) -> str:
    """Return `0.846 [0.80, 0.88]`, or `UNDEFINED` for an undefined score.

    The bounds get one digit less than the value, but at least one.
    """
    if interval["value"] is None:
        return UNDEFINED
    if interval["low"] is None or interval["high"] is None:
        return _number(interval["value"], digits)
    bound = max(1, digits - 1)
    return (
        f"{interval['value']:.{digits}f} "
        f"[{interval['low']:.{bound}f}, {interval['high']:.{bound}f}]"
    )


def format_difference(difference: dict[str, float | None], digits: int = 3) -> str:
    """Return `+0.012 [-0.01, 0.03]`, or `UNDEFINED` when undefined; digits as for intervals."""
    if difference["delta"] is None:
        return UNDEFINED
    if difference["low"] is None or difference["high"] is None:
        return f"{difference['delta']:+.{digits}f}"
    bound = max(1, digits - 1)
    return (
        f"{difference['delta']:+.{digits}f} "
        f"[{difference['low']:+.{bound}f}, {difference['high']:+.{bound}f}]"
    )


def _number(value: float | None, digits: int = 3) -> str:
    return UNDEFINED if value is None else f"{value:.{digits}f}"


def _table(header: tuple[str, ...], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines


# --- LaTeX ------------------------------------------------------------------


def latex(results: dict[str, Any]) -> str:
    r"""Render a results dictionary as LaTeX tables (booktabs).

    Each table defines nothing; `\ci` is provided once at the top, so the
    file can be `\input` as it is.
    """
    commit = (results["git"].get("commit") or "unknown")[:10]
    lines = [
        f"% {results['name']}: generated by `python -m experiments`, commit {commit}.",
        "% Requires \\usepackage{booktabs}.",
        "\\providecommand{\\ci}[2]{{\\scriptsize [#1, #2]}}",
        "",
    ]
    for key, corpus in results["corpora"].items():
        for mode in (PARTIAL, STRICT):
            lines += _latex_table(results["name"], key, corpus, mode)
        if _has_coverage(corpus):
            lines += _latex_coverage_table(results["name"], key, corpus)
    return "\n".join(lines)


def _latex_table(name: str, key: str, corpus: dict[str, Any], mode: str) -> list[str]:
    label = _escape(f"{name}-{key}-{mode}".replace("/", "-"))
    caption = (
        f"{_escape(key)} ({corpus['language']}, {corpus['role']}), "
        f"{_MATCH_TITLES[mode].lower()}; 95\\,\\% bootstrap intervals over "
        f"{corpus['documents']} documents."
    )
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\begin{tabular}{llrrrrr}",
        "\\toprule",
        "Type & System & P & R & F1 & F2 & Found / gold \\\\",
        "\\midrule",
    ]
    for row in _score_rows(corpus, mode):
        kind, system, *scores, found = row
        cells = [_escape(kind), _escape(system), *(_latex_value(cell) for cell in scores)]
        lines.append(" & ".join([*cells, found.replace(" / ", "/")]) + " \\\\")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        f"\\caption{{{caption}}}",
        f"\\label{{tab:{label}}}",
        "\\end{table}",
        "",
    ]
    return lines


def _latex_coverage_table(name: str, key: str, corpus: dict[str, Any]) -> list[str]:
    label = _escape(f"{name}-{key}-coverage".replace("/", "-"))
    caption = (
        f"{_escape(key)} ({corpus['language']}, {corpus['role']}), leak coverage: residual "
        "share of gold characters (whitespace not counted) no prediction of any type covers, "
        "gold spans hidden whole, and characters predicted outside every gold span per 1,000 "
        f"characters of text; 95\\,\\% bootstrap intervals over {corpus['documents']} documents."
    )
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        "\\begin{tabular}{llrrrr}",
        "\\toprule",
        "Type & System & Residual & Hidden whole & Over / 1k & Hidden / gold \\\\",
        "\\midrule",
    ]
    for row in _coverage_rows(corpus):
        kind, system, *scores, hidden = row
        cells = [_escape(kind), _escape(system), *(_latex_value(cell) for cell in scores)]
        lines.append(" & ".join([*cells, hidden.replace(" / ", "/")]) + " \\\\")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        f"\\caption{{{caption}}}",
        f"\\label{{tab:{label}}}",
        "\\end{table}",
        "",
    ]
    return lines


def _latex_value(cell: str) -> str:
    if "[" not in cell:
        return "--" if cell == UNDEFINED else cell
    value, interval = cell.split(" [", 1)
    low, high = interval.rstrip("]").split(", ")
    return f"{value} \\ci{{{low}}}{{{high}}}"


def _escape(text: str) -> str:
    replacements = (
        ("\\", "\\textbackslash{}"),
        ("_", "\\_"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("#", "\\#"),
    )
    for char, escaped in replacements:
        text = text.replace(char, escaped)
    return text
