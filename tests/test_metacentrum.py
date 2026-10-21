"""MetaCentrum scripts: keeping a trained model (`keep_trained.py`), what a job copies."""

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest
from anonymizer.core.resources import trained_catalog_path

from experiments.datasets import DATASETS
from experiments.train import load_train_config
from tests.resources.test_catalog import store_trained, trained_entry

SCRIPT = Path(__file__).parents[1] / "scripts" / "metacentrum" / "keep_trained.py"


@pytest.fixture(scope="module")
def keeper() -> ModuleType:
    spec = importlib.util.spec_from_file_location("keep_trained", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _model(root: Path, model_id: str, weights: bytes) -> None:
    folder = root / "models" / model_id
    folder.mkdir(parents=True)
    (folder / "model.safetensors").write_bytes(weights)


def _listed(root: Path) -> list[str]:
    listed = json.loads(trained_catalog_path(root).read_text(encoding="utf-8"))
    return [entry["id"] for entry in listed["resource"]]


def test_the_model_replaces_an_earlier_one_and_joins_the_list(keeper: ModuleType, tmp_path: Path):
    scratch, store = tmp_path / "scratch", tmp_path / "store"
    store_trained(scratch, trained_entry())
    _model(scratch, "gliner-cs-tuned", b"hello\n")
    store_trained(store, trained_entry(id="gliner-sk-tuned"), trained_entry(name="earlier run"))
    _model(store, "gliner-cs-tuned", b"earlier weights")

    assert keeper.keep_trained(scratch, store) == ["gliner-cs-tuned"]

    kept = store / "models" / "gliner-cs-tuned"
    assert (kept / "model.safetensors").read_bytes() == b"hello\n"
    assert sorted(_listed(store)) == ["gliner-cs-tuned", "gliner-sk-tuned"]
    listed = json.loads(trained_catalog_path(store).read_text(encoding="utf-8"))
    names = {entry["id"]: entry["name"] for entry in listed["resource"]}
    assert names["gliner-cs-tuned"] == trained_entry()["name"]
    assert sorted(path.name for path in (store / "models").iterdir()) == [
        "gliner-cs-tuned",
        "trained.json",
    ]


def test_a_store_without_models_gets_its_list(keeper: ModuleType, tmp_path: Path):
    scratch, store = tmp_path / "scratch", tmp_path / "store"
    store_trained(scratch, trained_entry())
    _model(scratch, "gliner-cs-tuned", b"hello\n")

    keeper.keep_trained(scratch, store)

    assert _listed(store) == ["gliner-cs-tuned"]


def test_a_held_lock_is_waited_for_and_then_reported(keeper: ModuleType, tmp_path: Path):
    lock = tmp_path / keeper.LOCK
    lock.write_text("1234.pbs-m1", encoding="utf-8")
    with (
        pytest.raises(TimeoutError, match=r"held by 1234\.pbs-m1"),
        keeper._locked(lock, "5678.pbs-m1", timeout=0),
    ):
        pass
    assert lock.exists()


def test_the_lock_names_its_holder_and_is_gone_afterwards(keeper: ModuleType, tmp_path: Path):
    lock = tmp_path / keeper.LOCK
    with keeper._locked(lock, "5678.pbs-m1"):
        assert lock.read_text(encoding="utf-8") == "5678.pbs-m1"
    assert not lock.exists()


def test_staging_folders_are_named_after_the_job(
    keeper: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("PBS_JOBID", "5678.pbs-m1")
    scratch, store = tmp_path / "scratch", tmp_path / "store"
    store_trained(scratch, trained_entry())
    _model(scratch, "gliner-cs-tuned", b"hello\n")
    # A copy another job left half done must not be touched.
    _model(store, "gliner-cs-tuned.1234.pbs-m1.part", b"half")

    keeper.keep_trained(scratch, store)

    left = sorted(path.name for path in (store / "models").iterdir())
    assert left == ["gliner-cs-tuned", "gliner-cs-tuned.1234.pbs-m1.part", "trained.json"]


def test_the_command_line_needs_both_roots(keeper: ModuleType):
    assert keeper.main(["only-one"]) == 2


SCRIPTS = SCRIPT.parent
REPOSITORY = SCRIPTS.parents[1]


@pytest.fixture(scope="module")
def bases() -> ModuleType:
    spec = importlib.util.spec_from_file_location("base_models", SCRIPTS / "base_models.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_job_copies_the_configs_base_and_its_tokenizer(
    bases: ModuleType, capsys: pytest.CaptureFixture[str]
):
    configs = REPOSITORY / "experiments" / "configs"
    assert bases.base_models(configs / "train-smoke.toml") == [
        "mdeberta-v3-base-tokenizer",
        "gliner-multi-v2.1",
    ]
    assert bases.main([str(configs / "train-xlmr-smoke.toml")]) == 0
    assert capsys.readouterr().out.split() == ["xlm-roberta-large-tokenizer", "xlm-roberta-large"]
    assert bases.main([]) == 2


def test_push_data_copies_every_base_a_shipped_config_names(bases: ModuleType):
    script = (SCRIPTS / "push-data.sh").read_text(encoding="utf-8")
    pushed = set(script.split("MODELS=(", 1)[1].split(")", 1)[0].split())
    configs = (REPOSITORY / "experiments" / "configs").rglob("train-*.toml")
    needed = {model for path in configs for model in bases.base_models(path)}
    assert needed <= pushed


def test_push_data_copies_every_corpus_a_shipped_config_reads():
    script = (SCRIPTS / "push-data.sh").read_text(encoding="utf-8")
    pushed = set(script.split("DATASETS=(", 1)[1].split(")", 1)[0].split())
    needed: set[str] = set()
    for path in (REPOSITORY / "experiments" / "configs").rglob("train-*.toml"):
        config = load_train_config(path)
        for dataset in [corpus.id for corpus in config.corpora] + [
            reference.id for reference in config.evaluate
        ]:
            spec = DATASETS[dataset]
            if spec.generated is None:
                needed.add(spec.catalog_id)
    assert {"wikigoldsk", "slavicner"} <= needed
    assert needed <= pushed
