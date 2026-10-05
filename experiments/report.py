"""Markdown and LaTeX tables from a results file.

Both are generated from the results dictionary alone, so a table in the
thesis can be regenerated from a stored `<name>.json` without rerunning.
Values are shown as `0.846 [0.80, 0.88]`: the score on all documents and its
95 % bootstrap interval.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from experiments.metrics import ANY_TYPE, MATCHES, PARTIAL, STRICT

UNDEFINED = "\N{EN DASH}"
"""Shown for a score that is undefined, e.g. precision without predictions."""

_MATCH_TITLES = {PARTIAL: "Partial match", STRICT: "Strict match"}
_HEADINGS = ("type", "system", "P", "R", "F1", "F2", "found / gold")
_METRIC_COLUMNS = ("precision", "recall", "f1", "f2")


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


def format_interval(interval: dict[str, float | None]) -> str:
    """Return `0.846 [0.80, 0.88]`, or `UNDEFINED` for an undefined score."""
    if interval["value"] is None:
        return UNDEFINED
    if interval["low"] is None or interval["high"] is None:
        return _number(interval["value"])
    return f"{interval['value']:.3f} [{interval['low']:.2f}, {interval['high']:.2f}]"


def format_difference(difference: dict[str, float | None]) -> str:
    """Return `+0.012 [-0.01, 0.03]`, or `UNDEFINED` when undefined."""
    if difference["delta"] is None:
        return UNDEFINED
    if difference["low"] is None or difference["high"] is None:
        return f"{difference['delta']:+.3f}"
    return f"{difference['delta']:+.3f} [{difference['low']:+.2f}, {difference['high']:+.2f}]"


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
