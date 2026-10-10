"""A whole run on synthetic corpora: configs, results, tables and the command line."""

import json
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.resources import load_catalog

from experiments.__main__ import main
from experiments.config import load_config, parse_config
from experiments.report import UNDEFINED, format_difference, format_interval, latex, markdown
from experiments.run import run
from tests.experiments.conftest import ScoredStandIn, StandInSplitter, StandInTagger

CONFIG: dict[str, Any] = {
    "name": "synthetic",
    "description": "Synthetic corpora.",
    "stage": "dev",
    "seed": 1,
    "resamples": 50,
    "compare": [["rules", "rules+gliner"]],
    "datasets": [
        {"id": "cnec-2.0", "split": "dtest"},
        {"id": "uner-sk-snk", "split": "dev", "text": "tokens"},
        {"id": "redact", "split": "sample"},
        {"id": "openpii-1m-cs", "split": "dev"},
    ],
    "systems": {"rules": {}, "rules+gliner": {"model": "gliner"}},
}

FOUND = {
    "Jan Novák": ("person", 0.9),
    "Svobodovi": ("person", 0.6),
    "Ján Kováč": ("person", 0.8),
    "Bratislavy": ("person", 0.4),
}


def _run(resource_root: Path, tmp_path: Path, stand_in: ScoredStandIn) -> dict[str, Any]:
    loads: list[int] = []

    def load(model_id: str) -> ScoredStandIn:
        assert model_id == "gliner-multi-v2.1"
        loads.append(1)
        return stand_in

    results = run(
        parse_config(CONFIG),
        resource_root=resource_root,
        cache_dir=tmp_path / "cache",
        load_model=load,
    )
    results["_loads"] = len(loads)
    return results


def test_scores_and_provenance(resource_root: Path, tmp_path: Path):
    results = _run(resource_root, tmp_path, ScoredStandIn(FOUND))
    assert results["stage"] == "dev"
    assert results["seed"] == 1
    assert set(results["models"]) == {"gliner-multi-v2.1", "mdeberta-v3-base-tokenizer"}
    assert set(results["datasets"]) == {"cnec-2.0", "uner-sk-snk", "redact", "openpii-1m-cs"}
    assert results["datasets"]["openpii-1m-cs"] == load_catalog()["openpii-1m"].version
    assert set(results["git"]) == {"commit", "dirty"}

    cnec = results["corpora"]["cnec-2.0/dtest"]
    assert cnec["gold"] == {"address": 1, "email": 1, "person": 3, "phone": 1}
    person = cnec["systems"]["rules+gliner"]["scores"]["partial"]["person"]
    assert person["counts"] == {
        "predicted": 2,
        "predicted_matched": 2,
        "gold": 3,
        "gold_matched": 2,
    }
    assert person["recall"]["value"] == pytest.approx(2 / 3, abs=1e-4)
    email = cnec["systems"]["rules"]["scores"]["strict"]["email"]
    assert email["recall"]["value"] == 1.0
    assert cnec["systems"]["rules"]["scores"]["strict"]["person"]["precision"]["value"] is None

    uner = results["corpora"]["uner-sk-snk/dev+tokens"]
    assert uner["text"] == "tokens"
    scores = uner["systems"]["rules+gliner"]["scores"]["partial"]
    assert set(scores) == {"person"}  # one scored type: no "any" row
    assert scores["person"]["counts"]["predicted"] == 2  # Bratislavy is a false alarm

    comparison = cnec["comparisons"][0]
    assert (comparison["baseline"], comparison["candidate"]) == ("rules", "rules+gliner")
    assert comparison["differences"]["partial"]["person"]["recall"]["delta"] == pytest.approx(
        2 / 3, abs=1e-4
    )


def test_no_corpus_text_in_the_results(resource_root: Path, tmp_path: Path):
    results = _run(resource_root, tmp_path, ScoredStandIn(FOUND))
    written = json.dumps(results, ensure_ascii=False) + markdown(results) + latex(results)
    for text in ("Novák", "Svobodovi", "Kováč", "Máriu", "example.cz", "777 123 456"):
        assert text not in written


def test_rerun_answers_from_the_cache(resource_root: Path, tmp_path: Path):
    first = _run(resource_root, tmp_path, ScoredStandIn(FOUND))
    assert first["_loads"] == 1
    second = _run(resource_root, tmp_path, ScoredStandIn({}))
    assert second["_loads"] == 0
    for key, corpus in second["corpora"].items():
        cache = corpus["systems"]["rules+gliner"]["cache"]
        assert cache["misses"] == 0, key
        assert (
            corpus["systems"]["rules+gliner"]["scores"]
            == first["corpora"][key]["systems"]["rules+gliner"]["scores"]
        )


def test_tables(resource_root: Path, tmp_path: Path):
    results = _run(resource_root, tmp_path, ScoredStandIn(FOUND))
    text = markdown(results)
    assert "## cnec-2.0/dtest · cs · dev" in text
    assert "### rules → rules+gliner (paired)" in text
    assert "| person | rules+gliner | 1.000 [1.00, 1.00] | 0.667 [" in text
    tex = latex(results)
    assert "\\begin{tabular}" in tex
    assert "rules+gliner" in tex
    assert "\\label{tab:synthetic-cnec-2.0-dtest-partial}" in tex
    assert "uner-sk-snk/dev+tokens" in tex


def test_value_formats():
    assert format_interval({"value": None, "low": None, "high": None}) == UNDEFINED
    assert format_interval({"value": 0.5, "low": None, "high": None}) == "0.500"
    assert format_difference({"delta": 0.1, "low": None, "high": None, "p_value": None}) == "+0.100"
    assert (
        format_difference({"delta": None, "low": None, "high": None, "p_value": None}) == UNDEFINED
    )


class TestConfig:
    def test_test_split_needs_the_final_stage(self):
        config = {**CONFIG, "datasets": [{"id": "cnec-2.0", "split": "etest"}]}
        with pytest.raises(ValueError, match="test data"):
            parse_config(config)
        assert parse_config({**config, "stage": "final"}).stage == "final"

    @pytest.mark.parametrize(
        ("change", "message"),
        [
            ({"colour": "red"}, "unknown keys"),
            ({"stage": "pilot"}, "stage must be"),
            ({"datasets": []}, "no datasets"),
            ({"systems": {}}, "no systems"),
            ({"compare": [["rules", "nametag"]]}, "not configured"),
            ({"resamples": 0}, "resamples must be"),
            ({"datasets": [{"id": "cnec-2.0"}]}, "needs 'id' and 'split'"),
            ({"datasets": [{"id": "conll", "split": "dev"}]}, "unknown dataset"),
            ({"datasets": [{"id": "cnec-2.0", "split": "dev"}]}, "no split"),
        ],
    )
    def test_invalid(self, change: dict, message: str):
        with pytest.raises(ValueError, match=message):
            parse_config({**CONFIG, **change})

    def test_types_restrict_scoring(self, resource_root: Path, tmp_path: Path):
        config = parse_config(
            {**CONFIG, "types": ["person"], "systems": {"rules": {}}, "compare": []}
        )
        results = run(config, resource_root=resource_root, cache_dir=tmp_path)
        assert results["corpora"]["cnec-2.0/dtest"]["scored_types"] == ["person"]

    def test_shipped_configs_parse(self):
        folder = Path(__file__).resolve().parents[2] / "experiments" / "configs"
        configs = sorted(folder.glob("*.toml"))
        assert configs
        for path in configs:
            assert load_config(path).name == path.stem


def test_command_line(resource_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    config = tmp_path / "rules.toml"
    config.write_text(
        'name = "rules-only"\nseed = 3\nresamples = 20\n'
        '[[datasets]]\nid = "cnec-2.0"\nsplit = "dtest"\n[systems.rules]\n',
        encoding="utf-8",
    )
    out = tmp_path / "results"
    root = ["--resource-root", str(resource_root)]
    assert main(["run", "--config", str(config), "--out", str(out), *root]) == 0
    stored = json.loads((out / "rules-only.json").read_text(encoding="utf-8"))
    assert stored["name"] == "rules-only"
    (out / "rules-only.md").unlink()
    assert main(["tables", str(out / "rules-only.json")]) == 0
    assert (out / "rules-only.md").exists()
    assert (out / "rules-only.tex").exists()

    assert main(["datasets", *root]) == 0
    printed = capsys.readouterr().out
    assert "cnec-2.0/dtest (dev, cs): 1 documents" in printed
    assert "cnec-2.0/train: not stored" in printed
    assert "Novák" not in printed


def test_the_earlier_name_and_the_catalog_id_run_one_model(resource_root: Path, tmp_path: Path):
    loads: list[str] = []

    def load(model_id: str) -> ScoredStandIn:
        loads.append(model_id)
        return ScoredStandIn(FOUND)

    config = {
        **CONFIG,
        "compare": [],
        "systems": {
            "rules+gliner": {"model": "gliner"},
            "rules+gliner-multi-v2.1": {"model": "gliner-multi-v2.1"},
        },
    }
    results = run(
        parse_config(config), resource_root=resource_root, cache_dir=tmp_path, load_model=load
    )
    assert loads == ["gliner-multi-v2.1"]
    for corpus in results["corpora"].values():
        systems = corpus["systems"]
        assert systems["rules+gliner"]["scores"] == systems["rules+gliner-multi-v2.1"]["scores"]
        assert systems["rules+gliner-multi-v2.1"]["cache"]["misses"] == 0


def test_nametag_and_a_union_run_and_rerun_from_the_cache(resource_root: Path, tmp_path: Path):
    nametag = "nametag3-czech-cnec2.0-240830"
    config = {
        **CONFIG,
        "datasets": [{"id": "cnec-2.0", "split": "dtest"}],
        "compare": [["rules+gliner", "rules+gliner|nametag"]],
        "systems": {
            "rules+gliner": {"model": "gliner"},
            "rules+nametag": {"model": nametag},
            "rules+gliner|nametag": {"model": ["gliner", nametag]},
        },
    }
    loads: list[str] = []

    def load(model_id: str) -> Any:
        loads.append(model_id)
        if model_id == nametag:
            return StandInTagger({("Karla", "Dvořáka"): ("P", 0.95)})
        return ScoredStandIn(FOUND)

    def results() -> dict[str, Any]:
        return run(
            parse_config(config),
            resource_root=resource_root,
            cache_dir=tmp_path / "cache",
            load_model=load,
            load_splitter=lambda _: StandInSplitter(),
        )

    first = results()
    assert sorted(loads) == ["gliner-multi-v2.1", nametag]
    assert set(first["models"]) >= {nametag, "robeczech-base-v1.1-tokenizer"}
    systems = first["corpora"]["cnec-2.0/dtest"]["systems"]
    person = {
        name: system["scores"]["partial"]["person"]["counts"]["gold_matched"]
        for name, system in systems.items()
    }
    assert person == {"rules+gliner": 2, "rules+nametag": 1, "rules+gliner|nametag": 3}
    assert systems["rules+nametag"]["cache"] == {"hits": 0, "misses": 1}

    loads.clear()
    second = results()
    assert loads == []
    for system in second["corpora"]["cnec-2.0/dtest"]["systems"].values():
        assert system["cache"]["misses"] == 0
