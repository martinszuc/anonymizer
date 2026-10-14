"""Charts across runs, and which runs a line may join."""

from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.types import EntityType

from benchmark.history import code_states, document_sets
from benchmark.run import run
from benchmark.spec import DocumentSpec, GoldItem

SIX = [f"doc-{index}" for index in range(6)]
TWENTY_SIX = [f"doc-{index}" for index in range(26)]


def results(
    version: str,
    names: list[str],
    *,
    items: int = 100,
    fingerprint: str | None = None,
    commit: str | None = None,
    found: int = 50,
) -> dict[str, Any]:
    """Return the parts of a results file the history reads."""
    run: dict[str, Any] = {
        "tool_version": version,
        "created": f"2026-01-01T00:00:00+00:00 {version}",
        "git_commit": commit or f"commit-{version}",
        "documents": {name: {} for name in names},
        "totals": {
            "rules": {
                "counts": {"gold": items, "found": found},
                "safe_documents": 1,
                "documents": len(names),
                "by_type": {"email": {"gold": items, "found": found, "partial": 0}},
            }
        },
    }
    if fingerprint is not None:
        run["document_set"] = {"fingerprint": fingerprint, "documents": len(names)}
    return run


def test_a_new_document_set_starts_a_new_series():
    # The releases as published: 6 documents to v0.3.0, 26 from v0.4.0, and
    # a fingerprint recorded from v0.7.0 on.
    runs = [
        results("0.2.0", SIX, items=40),
        results("0.3.0", SIX, items=40),
        results("0.4.0", TWENTY_SIX),
        results("0.7.0", TWENTY_SIX, fingerprint="current"),
    ]
    sets = document_sets(runs)
    assert [document_set.runs for document_set in sets] == [[0, 1], [2, 3]]
    assert sets[1].fingerprint == "current"
    assert sets[0].label == "6 documents, 40 items"


def test_fingerprints_part_sets_with_the_same_names():
    runs = [
        results("0.7.0", TWENTY_SIX, fingerprint="before-edit"),
        results("0.8.0", TWENTY_SIX, fingerprint="after-edit"),
    ]
    assert [document_set.runs for document_set in document_sets(runs)] == [[0], [1]]


def test_an_older_harness_reading_fewer_items_is_kept_apart():
    # v0.2.0's harness skips the carriers it did not know.
    runs = [
        results("0.2.0", TWENTY_SIX, items=195, fingerprint="current"),
        results("0.4.0", TWENTY_SIX, items=224, fingerprint="current"),
    ]
    assert [document_set.runs for document_set in document_sets(runs)] == [[0], [1]]


def test_a_run_without_fingerprint_joins_the_latest_matching_set():
    runs = [
        results("0.7.0", TWENTY_SIX, fingerprint="before-edit"),
        results("0.8.0", TWENTY_SIX, fingerprint="after-edit"),
        results("0.8.1", TWENTY_SIX),
    ]
    assert [document_set.runs for document_set in document_sets(runs)] == [[0], [1, 2]]


def test_a_release_and_its_backfill_share_a_place_on_the_axis():
    runs = [
        results("0.2.0", SIX, items=40),
        results("0.2.0", TWENTY_SIX, fingerprint="current"),
        results("0.3.0", TWENTY_SIX, fingerprint="current"),
        results("0.3.0", TWENTY_SIX, fingerprint="current", commit="manual-run"),
    ]
    assert code_states(runs) == [
        ("0.2.0", "commit-0.2.0"),
        ("0.3.0", "commit-0.3.0"),
        ("0.3.0", "manual-run"),
    ]


def test_history_charts_of_mixed_document_sets(tmp_path: Path):
    pytest.importorskip("matplotlib")
    import json

    from benchmark.history import draw

    runs = [
        results("0.2.0", SIX, items=40, found=30),
        results("0.4.0", TWENTY_SIX, found=60),
        results("0.2.0", TWENTY_SIX, fingerprint="current", found=55),
        results("0.4.0", TWENTY_SIX, fingerprint="current", found=60),
    ]
    paths = []
    for index, content in enumerate(runs):
        path = tmp_path / f"{index}.json"
        path.write_text(json.dumps(content), encoding="utf-8")
        paths.append(path)
    charts = draw(paths, tmp_path / "charts")
    assert all(chart.stat().st_size > 0 for chart in charts)


def test_history_charts(tmp_path: Path):
    pytest.importorskip("matplotlib")
    from benchmark.history import draw

    spec = DocumentSpec(
        name="mail",
        language="cs",
        kind="letter",
        lines=("jan.novak@example.com",),
        gold=(GoldItem(EntityType.EMAIL, "jan.novak@example.com", "page"),),
    )
    run(tmp_path / "run", systems=("rules",), specs=[spec])
    charts = draw([tmp_path / "run" / "results.json"], tmp_path / "charts")
    assert all(chart.stat().st_size > 0 for chart in charts)
