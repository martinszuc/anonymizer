"""Scores of one run against another, per item type, as Markdown.

Pull requests are compared with the latest release this way: a regression
check that reports and never fails. Per type it lists found, readable after
redaction (whole) and left in the carrier (whole or as a fragment); a change
reads `before → after`. Runs on different document sets are compared anyway,
with a warning, since their scores differ for that reason alone.
"""

from __future__ import annotations

from typing import Any

from benchmark.history import document_sets, planted_items, run_fingerprint

COLUMNS = ("found", "readable_after", "left_in_carrier")


def diff_markdown(baseline: dict[str, Any], current: dict[str, Any]) -> str:
    """Compare two runs' results per item type, for every system both ran.

    Args:
        baseline: The results to compare against (the latest release).
        current: The results of this run.

    Returns:
        Markdown: a heading, a line on the document sets, a table per system.
    """
    lines = [
        f"## Benchmark against {baseline['tool_version']}",
        "",
        f"Baseline {_describe(baseline)}; this run {_describe(current)}.",
        "",
        _set_note(baseline, current),
    ]
    systems = [system for system in current["systems"] if system in baseline["totals"]]
    if not systems:
        return "\n".join([*lines, "", "No system in common."]) + "\n"
    for system in systems:
        before = baseline["totals"][system]
        after = current["totals"][system]
        kinds = sorted({*before["by_type"], *after["by_type"]})
        rows = [
            _row(kind, before["by_type"].get(kind), after["by_type"].get(kind)) for kind in kinds
        ]
        changed = sum(row_changed for _, row_changed in rows)
        rows.append(_row("**all**", before["counts"], after["counts"]))
        lines += [
            "",
            f"### {system}",
            "",
            f"{changed} of {len(kinds)} types changed." if changed else "No type changed.",
            "",
            "| type | found | readable after | left in carrier |",
            "|---|---|---|---|",
            *(f"| {' | '.join(cells)} |" for cells, _ in rows),
            "",
            f"Safe documents: {_change(before['safe_documents'], after['safe_documents'])}; "
            f"false alarms: {_change(before['false_positives'], after['false_positives'])}.",
        ]
    return "\n".join(lines) + "\n"


def _row(
    kind: str, before: dict[str, int] | None, after: dict[str, int] | None
) -> tuple[list[str], bool]:
    """Return a table row's cells and whether any of them changed.

    A count the baseline did not record yet (an older release) shows as `-`.
    """
    cells = [kind]
    changed = False
    for column in COLUMNS:
        old, new = _shown(column, before), _shown(column, after)
        changed |= old != new
        cells.append(new if old == new else f"**{old} → {new}**")
    return cells, changed


def _shown(column: str, counts: dict[str, int] | None) -> str:
    if counts is None or column not in counts:
        return "-"
    return f"{counts[column]}/{counts['gold']}" if column == "found" else str(counts[column])


def _change(old: int, new: int) -> str:
    return str(new) if old == new else f"**{old} → {new}**"


def _describe(results: dict[str, Any]) -> str:
    commit = (results.get("git_commit") or "")[:7]
    return f"{results['tool_version']}" + (f" (`{commit}`)" if commit else "")


def _set_note(baseline: dict[str, Any], current: dict[str, Any]) -> str:
    sets = document_sets([baseline, current])
    if len(sets) > 1:
        return (
            f"**Different document sets** ({sets[0].label} against {sets[1].label}): "
            "the scores differ for that reason too."
        )
    by_fingerprint = run_fingerprint(baseline) and run_fingerprint(current)
    how = "fingerprint" if by_fingerprint else "document names"
    return (
        f"Same document set by {how}: {len(sets[0].names)} documents, "
        f"{planted_items(current)} planted items."
    )
