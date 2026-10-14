"""A run compared with the latest release, per item type."""

import json
from pathlib import Path
from typing import Any

import pytest

from benchmark.__main__ import main
from benchmark.diff import diff_markdown

NAMES = ["cs-cv", "cs-invoice"]


def counts(gold: int, found: int, readable: int = 0, left: int | None = 0) -> dict[str, int]:
    result = {"gold": gold, "found": found, "readable_after": readable}
    if left is not None:
        result["left_in_carrier"] = left
    return result


def results(
    version: str,
    by_type: dict[str, dict[str, int]],
    *,
    fingerprint: str | None = "current",
    names: list[str] = NAMES,
    safe: int = 1,
    false_positives: int = 3,
) -> dict[str, Any]:
    total = {
        key: sum(entry.get(key, 0) for entry in by_type.values())
        for key in ("gold", "found", "readable_after", "left_in_carrier")
    }
    run: dict[str, Any] = {
        "tool_version": version,
        "git_commit": "0123456789abcdef",
        "systems": ["rules"],
        "documents": {name: {} for name in names},
        "totals": {
            "rules": {
                "counts": total,
                "by_type": by_type,
                "safe_documents": safe,
                "false_positives": false_positives,
            }
        },
    }
    if fingerprint is not None:
        run["document_set"] = {"fingerprint": fingerprint, "documents": len(names)}
    return run


def test_unchanged_scores_read_as_no_change():
    by_type = {"email": counts(4, 4), "person": counts(6, 3, readable=3, left=3)}
    report = diff_markdown(results("0.6.0", by_type), results("0.6.0", by_type))
    assert "## Benchmark against 0.6.0" in report
    assert "Same document set by fingerprint: 2 documents, 10 planted items." in report
    assert "No type changed." in report
    assert "| person | 3/6 | 3 | 3 |" in report
    assert "| **all** | 7/10 | 3 | 3 |" in report
    assert "→" not in report


def test_a_change_is_shown_before_and_after():
    before = results("0.6.0", {"email": counts(4, 4), "person": counts(6, 3, readable=3, left=3)})
    after = results(
        "0.7.0",
        {"email": counts(4, 4), "person": counts(6, 5, readable=1, left=1)},
        safe=2,
    )
    report = diff_markdown(before, after)
    assert "1 of 2 types changed." in report
    assert "| person | **3/6 → 5/6** | **3 → 1** | **3 → 1** |" in report
    assert "| email | 4/4 | 0 | 0 |" in report
    assert "Safe documents: **1 → 2**; false alarms: 3." in report


def test_a_type_new_to_one_side_and_a_count_the_baseline_lacks():
    # Releases before v0.4.0 did not count items left in their carrier.
    before = results("0.3.0", {"email": counts(6, 5, left=None)}, fingerprint=None)
    after = results("0.7.0", {"email": counts(4, 4), "iban": counts(2, 2)})
    report = diff_markdown(before, after)
    assert "Same document set by document names: 2 documents, 6 planted items." in report
    assert "| email | **5/6 → 4/4** | 0 | **- → 0** |" in report
    assert "| iban | **- → 2/2** | **- → 0** | **- → 0** |" in report


def test_different_document_sets_are_flagged():
    before = results("0.3.0", {"email": counts(4, 4)}, fingerprint=None, names=["cs-cv"])
    after = results("0.7.0", {"email": counts(9, 9)})
    report = diff_markdown(before, after)
    assert (
        "**Different document sets** (1 documents, 4 items against 2 documents, 9 items)" in report
    )


def test_no_system_in_common():
    before = results("0.6.0", {"email": counts(4, 4)})
    after = results("0.7.0", {"email": counts(4, 4)})
    after["systems"] = ["rules+gliner"]
    assert diff_markdown(before, after).endswith("No system in common.\n")


def test_the_diff_command_prints_markdown(tmp_path: Path, capsys: pytest.CaptureFixture):
    by_type = {"email": counts(4, 4)}
    for name in ("baseline", "current"):
        (tmp_path / f"{name}.json").write_text(json.dumps(results("0.6.0", by_type)))
    assert main(["diff", str(tmp_path / "baseline.json"), str(tmp_path / "current.json")]) == 0
    assert "No type changed." in capsys.readouterr().out
