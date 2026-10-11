"""Replicates of a trained model (`seeds` in a run config): expansion, spread, tables."""

import statistics
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.resources import load_catalog

from experiments.config import parse_config
from experiments.report import markdown
from experiments.run import run
from experiments.seeds import UNDEFINED, format_spread, spread
from tests.experiments.conftest import ScoredStandIn
from tests.resources.test_catalog import store_trained, trained_entry

MODELS = ("gliner-ce", "gliner-ce-s1", "gliner-ce-s2", "gliner-wt", "gliner-wt-s1", "gliner-wt-s2")

FOUND: dict[str, dict[str, tuple[str, float]]] = {
    "gliner-multi-v2.1": {"Jan Novák": ("person", 0.9)},
    "gliner-ce": {"Jan Novák": ("person", 0.9)},
    "gliner-ce-s1": {"Jan Novák": ("person", 0.9), "Svobodovi": ("person", 0.6)},
    "gliner-ce-s2": {"Jan Novák": ("person", 0.9)},
    "gliner-wt": {"Jan Novák": ("person", 0.9), "Svobodovi": ("person", 0.5)},
    "gliner-wt-s1": {"Jan Novák": ("person", 0.9), "Svobodovi": ("person", 0.5)},
    "gliner-wt-s2": {"Jan Novák": ("person", 0.9), "Svobodovi": ("person", 0.2)},
}

CONFIG: dict[str, Any] = {
    "name": "seeded",
    "seed": 1,
    "resamples": 20,
    "types": ["person"],
    "compare": [
        ["rules+gliner", "rules+gliner-ce"],
        ["rules+gliner-ce", "rules+gliner-wt"],
        ["rules+gliner", "rules"],
    ],
    "datasets": [{"id": "cnec-2.0", "split": "dtest"}],
    "systems": {
        "rules": {},
        "rules+gliner": {"model": "gliner"},
        "rules+gliner-ce": {"model": "gliner-ce", "seeds": [1, 2]},
        "rules+gliner-wt": {"model": "gliner-wt", "threshold": 0.4, "seeds": [1, 2]},
    },
}


@pytest.fixture
def seeded_root(resource_root: Path) -> Path:
    store_trained(resource_root, *(trained_entry(id=model) for model in MODELS))
    return resource_root


def test_seeds_add_a_system_per_replicate_with_the_same_options(seeded_root: Path):
    config = parse_config(CONFIG, load_catalog(root=seeded_root))
    systems = {system.name: system for system in config.systems}
    assert list(systems) == [
        "rules",
        "rules+gliner",
        "rules+gliner-ce",
        "rules+gliner-ce-s1",
        "rules+gliner-ce-s2",
        "rules+gliner-wt",
        "rules+gliner-wt-s1",
        "rules+gliner-wt-s2",
    ]
    assert systems["rules+gliner-wt-s2"].model == "gliner-wt-s2"
    assert systems["rules+gliner-wt-s2"].threshold == 0.4
    assert config.replicates["rules+gliner-ce"].members() == {
        "base": "rules+gliner-ce",
        "s1": "rules+gliner-ce-s1",
        "s2": "rules+gliner-ce-s2",
    }


@pytest.mark.parametrize(
    ("system", "message"),
    [
        ({"seeds": [1]}, "exactly one name model"),
        ({"model": "gliner-ce", "seeds": []}, "seeds must be"),
        ({"model": "gliner-ce", "seeds": [1, 1]}, "seeds must be"),
        ({"model": "gliner-ce", "seeds": [-1]}, "seeds must be"),
        ({"model": "gliner-ce", "seeds": ["1"]}, "seeds must be"),
        ({"model": "gliner-ce", "seeds": [3]}, "unknown name model 'gliner-ce-s3'"),
    ],
)
def test_invalid_seeds_are_refused(seeded_root: Path, system: dict[str, Any], message: str):
    config = {**CONFIG, "compare": [], "systems": {"tuned": system}}
    with pytest.raises(ValueError, match=message):
        parse_config(config, load_catalog(root=seeded_root))


def test_a_replicate_may_not_take_the_name_of_another_system(seeded_root: Path):
    config = {
        **CONFIG,
        "compare": [],
        "systems": {"tuned": {"model": "gliner-ce", "seeds": [1]}, "tuned-s1": {}},
    }
    with pytest.raises(ValueError, match="also configured"):
        parse_config(config, load_catalog(root=seeded_root))


def test_a_run_sums_the_replicates_up(seeded_root: Path, tmp_path: Path):
    results = run(
        parse_config(CONFIG, load_catalog(root=seeded_root)),
        resource_root=seeded_root,
        cache_dir=tmp_path,
        load_model=lambda model_id: ScoredStandIn(FOUND[model_id]),
    )
    assert results["replicates"]["rules+gliner-wt"]["s2"] == "rules+gliner-wt-s2"
    corpus = results["corpora"]["cnec-2.0/dtest"]
    systems = corpus["systems"]

    def recall(system: str) -> float:
        return systems[system]["scores"]["partial"]["person"]["recall"]["value"]

    seeds = corpus["seeds"]
    ce = seeds["systems"]["rules+gliner-ce"]["scores"]["partial"]["person"]["recall"]
    values = [recall(f"rules+gliner-ce{suffix}") for suffix in ("", "-s1", "-s2")]
    assert values[0] != values[1]  # the replicates differ, or the test proves nothing
    assert ce["mean"] == pytest.approx(statistics.fmean(values))
    assert ce["sd"] == pytest.approx(statistics.stdev(values))
    assert (ce["low"], ce["high"], ce["n"]) == (min(values), max(values), 3)

    by_pair = {(item["baseline"], item["candidate"]): item for item in seeds["comparisons"]}
    # Replicates of two seeded systems pair by seed; s2's span lies under 0.4.
    paired = by_pair["rules+gliner-ce", "rules+gliner-wt"]
    assert paired["pairs"]["s2"] == ["rules+gliner-ce-s2", "rules+gliner-wt-s2"]
    deltas = paired["differences"]["partial"]["person"]["recall"]
    assert deltas["values"]["base"] == pytest.approx(
        recall("rules+gliner-wt") - recall("rules+gliner-ce")
    )
    assert deltas["values"]["s2"] == pytest.approx(0.0)
    assert (deltas["above_zero"], deltas["n"]) == (1, 3)
    # A system without replicates stands beside each replicate.
    zero_shot = by_pair["rules+gliner", "rules+gliner-ce"]
    assert {pair[0] for pair in zero_shot["pairs"].values()} == {"rules+gliner"}
    # Neither side seeded: the paired bootstrap alone.
    assert ("rules+gliner", "rules") not in by_pair

    text = markdown(results)
    assert "### Across seeds" in text
    assert "| person | partial | rules+gliner-ce | 3 |" in text
    assert "| person | partial | rules+gliner-ce → rules+gliner-wt | 3 |" in text


def test_a_run_without_seeds_has_no_seed_tables(resource_root: Path, tmp_path: Path):
    config = {**CONFIG, "compare": [], "systems": {"rules": {}}}
    results = run(parse_config(config), resource_root=resource_root, cache_dir=tmp_path)
    assert "replicates" not in results
    assert "seeds" not in results["corpora"]["cnec-2.0/dtest"]
    assert "Across seeds" not in markdown(results)


def test_spread_of_defined_values():
    summary = spread({"base": 0.8, "s1": 0.9, "s2": None})
    assert summary["mean"] == pytest.approx(0.85)
    assert summary["sd"] == pytest.approx(statistics.stdev([0.8, 0.9]))
    assert (summary["low"], summary["high"], summary["n"]) == (0.8, 0.9, 2)
    assert format_spread(summary) == "0.850 ± 0.071"
    single = spread({"base": -0.02})
    assert single["sd"] is None
    assert single["above_zero"] == 0
    assert format_spread(single, signed=True) == "-0.020"
    assert format_spread(spread({"base": None})) == UNDEFINED
