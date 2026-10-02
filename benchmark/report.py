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
    lines += ["", "## Per carrier", ""]
    lines += _breakdown(results, "by_carrier", "carrier")
    lines += ["", "## Per document kind", ""]
    kinds = sorted({kind for system in systems for kind in results["totals"][system]["by_kind"]})
    lines += _table(
        [
            "kind",
            "documents",
            *(f"{system}: found / safe / false alarms" for system in systems),
        ],
        [
            [
                kind,
                str(results["totals"][systems[0]]["by_kind"][kind]["documents"]),
                *(
                    f"{_ratio(counts['found'], counts['gold'])} / "
                    f"{_ratio(counts['safe_documents'], counts['documents'])} / "
                    f"{counts['false_positives']}"
                    for counts in (results["totals"][system]["by_kind"][kind] for system in systems)
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
    lines += ["", "## Not found", ""]
    lines += _table(
        ["system", "document", "type", "carrier", "item", "outcome", "left readable"],
        [
            [
                system,
                name,
                item["type"],
                item["carrier"],
                item["text"],
                item["outcome"],
                "yes" if item["readable_after"] or item["fragments_after"] else "no",
            ]
            for system in systems
            for name, document in results["documents"].items()
            for item in document["systems"][system]["items"]
            if item["outcome"] != "found"
        ],
    )
    lines += ["", "## False alarms", ""]
    lines += _table(
        ["system", "document", "detected text"],
        [
            [system, name, text]
            for system in systems
            for name, document in results["documents"].items()
            for text in document["systems"][system]["false_positives"]
        ],
    )
    return "\n".join(lines) + "\n"


def _breakdown(results: dict[str, Any], key: str, label: str) -> list[str]:
    """Tabulate, per group of a breakdown, items found and items left in their carrier.

    Left means readable there whole or as a fragment, as for a safe document.
    """
    systems: list[str] = results["systems"]
    groups = sorted({group for system in systems for group in results["totals"][system][key]})
    return _table(
        [label, *(f"{system}: found / left there" for system in systems)],
        [
            [
                group,
                *(
                    f"{_ratio(counts['found'], counts['gold'])} / {counts['left_in_carrier']}"
                    if (counts := results["totals"][system][key].get(group))
                    else "-"
                    for system in systems
                ),
            ]
            for group in groups
        ],
    )


def _ratio(part: int, whole: int) -> str:
    return f"{part}/{whole}"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    return [
        "| " + " | ".join(header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
        *("| " + " | ".join(row) + " |" for row in rows),
    ]
