"""Results as Markdown tables."""

from __future__ import annotations

from typing import Any


def markdown(results: dict[str, Any]) -> str:
    """Render a run's results as Markdown."""
    systems: list[str] = results["systems"]
    lines = [
        f"# Benchmark: anonymizer {results['tool_version']}",
        "",
        f"Run {results['created']} on {results['machine']['system']} "
        f"{results['machine']['machine']}, Python {results['machine']['python']}"
        + (f", commit `{results['git_commit'][:7]}`" if results.get("git_commit") else "")
        + ".",
    ]
    if results["models"]:
        models = ", ".join(
            f"`{name}@{version[:12]}`" for name, version in results["models"].items()
        )
        lines.append(f"Models: {models}.")
    lines += ["", "## Summary", ""]
    lines += _table(
        [
            "system",
            "found",
            "partial",
            "missed",
            "false alarms",
            "per 1,000 words",
            "decoys removed",
            "safe documents",
            "leak check passed",
            "seconds",
        ],
        [
            [
                system,
                _ratio(total["counts"]["found"], total["counts"]["gold"]),
                str(total["counts"]["partial"]),
                str(total["counts"]["missed"]),
                str(total["false_positives"]),
                f"{total['false_alarms_per_1000_words']:.1f}",
                str(total["decoys_removed"]),
                _ratio(total["safe_documents"], total["documents"]),
                _ratio(total["leak_check_passed"], total["documents"]),
                f"{total['seconds']:.1f}",
            ]
            for system, total in ((system, results["totals"][system]) for system in systems)
        ],
    )
    lines += ["", "## Found per type", ""]
    kinds = sorted({kind for system in systems for kind in results["totals"][system]["by_type"]})
    lines += _table(
        ["type", *systems],
        [
            [
                kind,
                *(
                    _ratio(counts["found"], counts["gold"])
                    if (counts := results["totals"][system]["by_type"].get(kind))
                    else "-"
                    for system in systems
                ),
            ]
            for kind in kinds
        ],
    )
    lines += ["", "## Per document", ""]
    lines += _table(
        [
            "document",
            "language",
            "kind",
            *(f"{system}: found / safe / false alarms" for system in systems),
        ],
        [
            [
                name,
                document["summary"]["language"],
                document["summary"]["kind"],
                *(
                    f"{_ratio(scores['counts']['found'], scores['counts']['gold'])} / "
                    f"{'yes' if scores['safe'] else '**no**'} / "
                    f"{len(scores['false_positives'])}"
                    for scores in (document["systems"][system] for system in systems)
                ),
            ]
            for name, document in results["documents"].items()
        ],
    )
    return "\n".join(lines) + "\n"


def _ratio(part: int, whole: int) -> str:
    return f"{part}/{whole}"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    return [
        "| " + " | ".join(header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
        *("| " + " | ".join(row) + " |" for row in rows),
    ]
