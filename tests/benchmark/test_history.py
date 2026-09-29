"""Charts across runs."""

from pathlib import Path

import pytest
from anonymizer.core.types import EntityType

from benchmark.run import run
from benchmark.spec import DocumentSpec, GoldItem


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
