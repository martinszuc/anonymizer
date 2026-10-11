"""Training a name model, with stand-ins: examples, configs, storing and registering.

Nothing here loads gliner or PyTorch: the model, its loader and the trainer
are stand-ins, and every name and number is invented.
"""

import copy
import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.detect.gliner import gliner_tokens
from anonymizer.core.resources import load_catalog, trained_catalog_path
from anonymizer.core.types import Entity, EntityType

from experiments.__main__ import main
from experiments.datasets import DATASETS, load_corpus, make_page
from experiments.examples import (
    MAX_SPAN_TOKENS,
    Conversion,
    Example,
    corpus_examples,
    corpus_labels,
    cut,
    page_examples,
    sample,
    token_spans,
    training_labels,
)
from experiments.train import (
    TrainConfig,
    load_train_config,
    parse_train_config,
    register,
    seed_for,
    train,
)
from tests.experiments.conftest import CNEC_LINES, UNER_TEXT, ScoredStandIn
from tests.resources.test_catalog import trained_entry

CONFIGS = Path(__file__).parents[2] / "experiments" / "configs"
TAUGHT = training_labels()
ALL_LABELS = ("person", "street address", "organization")


def _gold(text: str, *values: tuple[EntityType, str]) -> list[Entity]:
    """Gold spans over a page's text, each value looked up after the previous one."""
    spans: list[Entity] = []
    position = 0
    for kind, value in values:
        start = text.index(value, position)
        end = start + len(value)
        spans.append(Entity(type=kind, page_index=0, start=start, end=end, text=text[start:end]))
        position = start + len(value)
    return spans


def _examples(text: str, *values: tuple[EntityType, str], max_tokens: int = 150):
    conversion = Conversion()
    page = make_page(0, text)
    examples = list(
        page_examples(page, _gold(text, *values), TAUGHT, ALL_LABELS, max_tokens, conversion)
    )
    return examples, conversion


def _spanned(example: Example) -> list[tuple[str, str]]:
    return [
        (label, " ".join(example.tokens[first : last + 1])) for first, last, label in example.spans
    ]


class TestLabels:
    def test_the_detectors_prompts_in_its_order(self):
        assert TAUGHT == {
            EntityType.PERSON: "person",
            EntityType.ADDRESS: "street address",
            EntityType.ORGANIZATION: "organization",
        }

    def test_a_distractor_naming_no_type_cannot_be_taught(self):
        with pytest.raises(ValueError, match="names no entity type"):
            training_labels(distractors=("job title",))

    def test_a_corpus_is_prompted_only_with_what_it_marks_throughout(self):
        assert corpus_labels(DATASETS["cnec-2.0"], TAUGHT) == ALL_LABELS
        assert corpus_labels(DATASETS["uner-sk-snk"], TAUGHT) == ("person", "organization")
        assert corpus_labels(DATASETS["openpii-1m-cs"], TAUGHT) == ("person", "street address")


class TestSpans:
    def test_whole_names_in_running_text_without_their_punctuation(self):
        text = "Smlouvu podepsal Ing. Jan Novák, Lipová 12, Brno."
        (example,), _ = _examples(
            text,
            (EntityType.PERSON, "Jan Novák"),
            (EntityType.ADDRESS, "Lipová 12, Brno"),
        )
        assert _spanned(example) == [
            ("person", "Jan Novák"),
            ("street address", "Lipová 12 , Brno"),
        ]
        assert example.labels == ALL_LABELS

    def test_a_span_ending_inside_a_token_takes_the_whole_token(self):
        text = "Volal Svobodovi-Novákovi včera."
        (example,), _ = _examples(text, (EntityType.PERSON, "Svobodovi-Nov"))
        assert _spanned(example) == [("person", "Svobodovi-Novákovi")]

    def test_diacritics_survive_as_nfc(self):
        (example,), _ = _examples("Pozdravuj Ján Kováč.", (EntityType.PERSON, "Ján Kováč"))
        assert _spanned(example) == [("person", "Ján Kováč")]
        assert all(unicodedata.is_normalized("NFC", token) for token in example.tokens)

    def test_types_not_prompted_are_left_out(self):
        text = "Jan Novák, jan@example.cz"
        spans = token_spans(
            [(0, 3), (4, 9), (9, 10), (11, 25)],
            _gold(text, (EntityType.PERSON, "Jan Novák"), (EntityType.EMAIL, "jan@example.cz")),
            TAUGHT,
            ("person",),
        )
        assert spans == [(0, 1, "person")]

    def test_an_example_with_a_span_too_wide_to_learn_is_left_out(self):
        address = " ".join(f"část{number}" for number in range(MAX_SPAN_TOKENS + 1))
        examples, conversion = _examples(f"Bydlí {address}.", (EntityType.ADDRESS, address))
        assert examples == []
        assert conversion.too_wide == {"street address": 1}

    def test_the_gliner_format(self):
        example = Example(("Jan", "Novák"), ((0, 1, "person"),), ("person",))
        assert example.to_gliner() == {
            "tokenized_text": ["Jan", "Novák"],
            "ner": [[0, 1, "person"]],
            "ner_labels": ["person"],
        }


class TestCut:
    @staticmethod
    def _tokens(text: str) -> list[tuple[int, int]]:
        return gliner_tokens(text)

    def test_ranges_cover_every_token_once_within_the_limit(self):
        text = " ".join(f"slovo{number}" for number in range(25))
        ranges = list(cut(text, self._tokens(text), [], 10))
        assert ranges == [(0, 10), (10, 20), (20, 25)]

    def test_a_cut_never_falls_inside_a_span(self):
        text = " ".join(f"slovo{number}" for number in range(25))
        ranges = list(cut(text, self._tokens(text), [(8, 11, "person")], 10))
        assert ranges[0] == (0, 8)
        assert not {end for _, end in ranges} & {9, 10, 11}

    def test_a_line_break_in_the_second_half_is_preferred(self):
        text = "a b c d e f g\nh i j k l"
        assert next(cut(text, self._tokens(text), [], 10)) == (0, 7)

    def test_long_pages_give_several_examples_with_their_spans(self):
        text = "\n".join(f"Věta {number} zmiňuje Jana Nováka." for number in range(40))
        values = [(EntityType.PERSON, "Jana Nováka")] * 40
        examples, _ = _examples(text, *values, max_tokens=30)
        assert len(examples) > 1
        assert all(len(example.tokens) <= 30 for example in examples)
        assert sum(len(example.spans) for example in examples) == 40
        assert all(
            _spanned(example) == [("person", "Jana Nováka")] * len(example.spans)
            for example in examples
        )


def test_sampling_is_seeded_and_takes_all_when_asked_for_more():
    examples = [Example((str(number),), (), ()) for number in range(50)]
    assert sample(examples, 10, 7) == sample(examples, 10, 7)
    assert sample(examples, 10, 7) != sample(examples, 10, 8)
    assert sample(examples, 80, 7) == examples
    assert seed_for(1, "cnec-2.0/train") == seed_for(1, "cnec-2.0/train")
    assert seed_for(1, "cnec-2.0/train") != seed_for(1, "uner-sk-snk/train")


@pytest.fixture
def training_root(resource_root: Path) -> Path:
    """The synthetic corpora with train splits, and the base model's config."""
    plain = resource_root / "data/cnec-2.0/Czech_Named_Entity_Corpus_2.0/cnec2.0/data/plain"
    (plain / "named_ent_train.txt").write_text("\n".join(CNEC_LINES) + "\n", encoding="utf-8")
    (resource_root / "data/uner-sk-snk/sk_snk-ud-train.iob2").write_text(
        UNER_TEXT, encoding="utf-8"
    )
    base = resource_root / "models/gliner-multi-v2.1"
    base.mkdir(parents=True)
    (base / "gliner_config.json").write_text('{"max_len": 384}', encoding="utf-8")
    return resource_root


def test_a_corpus_becomes_examples_with_its_labels(training_root: Path):
    conversion = Conversion()
    corpus = load_corpus("cnec-2.0", "train", training_root)
    examples = corpus_examples(corpus, DATASETS["cnec-2.0"], conversion)
    assert conversion.examples == {"cnec-2.0/train": len(examples)}
    spanned = [pair for example in examples for pair in _spanned(example)]
    assert ("person", "Jan Novák") in spanned
    assert ("organization", "Nadace Karla Dvořáka") in spanned
    assert ("street address", "Kounicova 12") in spanned
    assert all(example.labels == ALL_LABELS for example in examples)


CONFIG: dict[str, Any] = {
    "name": "train-test",
    "model": "gliner-cs-test",
    "seed": 5,
    "device": "cpu",
    "training": {"steps": 2, "batch_size": 2, "loss": "focal", "focal_alpha": 0.75},
    "corpora": [
        {"id": "cnec-2.0", "split": "train"},
        {"id": "uner-sk-snk", "split": "train", "examples": 1},
        {"id": "openpii-1m-cs", "split": "train", "examples": 2},
    ],
    "evaluate": {"datasets": [{"id": "cnec-2.0", "split": "dtest"}]},
}


def _changed(path: str, value: object) -> dict[str, Any]:
    """CONFIG with one key replaced; `path` is dotted, a list index a number."""
    raw = copy.deepcopy(CONFIG)
    *parents, last = path.split(".")
    table: Any = raw
    for key in parents:
        table = table[int(key)] if key.isdigit() else table[key]
    table[int(last) if last.isdigit() else last] = value
    return raw


class TestConfig:
    def test_a_valid_config(self):
        config = parse_train_config(CONFIG)
        assert isinstance(config, TrainConfig)
        assert config.base == "gliner-multi-v2.1"
        assert config.training.focal_alpha == 0.75
        assert config.training.focal_gamma == 0.0
        assert [corpus.examples for corpus in config.corpora] == [None, 1, 2]
        assert [reference.split for reference in config.evaluate] == ["dtest"]

    @pytest.mark.parametrize(
        ("path", "value", "message"),
        [
            ("corpora.0.split", "etest", "not a train split"),
            ("corpora.0.split", "dtest", "not a train split"),
            ("corpora.2.split", "test", "not a train split"),
            ("corpora.0.id", "conll", "unknown dataset"),
            ("corpora.1.examples", 0, "examples must be"),
            ("evaluate.datasets", [{"id": "cnec-2.0", "split": "etest"}], "is test data"),
            ("evaluate.datasets", [{"id": "cnec-2.0", "split": "train"}], "not a development"),
            ("evaluate.limit", -1, "limit must be"),
            ("model", "gliner-multi-v2.1", "shipped catalog entry"),
            ("model", "Gliner Tuned", "no valid catalog id"),
            ("base", "onnxtr-fast-base", "unknown name model"),
            ("device", "cuda", "device must be"),
            ("training.loss", "dice", "loss must be"),
            ("training.focal_alpha", 1.5, "0 < focal_alpha < 1"),
            ("training.steps", 0, "steps must be"),
            ("training.max_tokens", 400, "longer texts than detection reads"),
            ("training.momentum", 0.9, "unknown keys"),
            ("epochs", 3, "unknown keys"),
        ],
    )
    def test_invalid_configs_are_refused(self, path: str, value: object, message: str):
        with pytest.raises(ValueError, match=message):
            parse_train_config(_changed(path, value))

    def test_cross_entropy_takes_no_focal_parameters(self):
        raw = _changed("training.loss", "ce")
        with pytest.raises(ValueError, match="focal loss only"):
            parse_train_config(raw)
        del raw["training"]["focal_alpha"]
        assert parse_train_config(raw).training.focal_alpha == -1.0

    def test_the_shipped_configs_are_valid(self):
        configs = sorted(CONFIGS.glob("train-*.toml"))
        assert configs
        for path in configs:
            assert load_train_config(path).name == path.stem


def test_registering_adds_or_replaces_one_entry(tmp_path: Path):
    register(tmp_path, trained_entry())
    register(tmp_path, trained_entry(id="gliner-sk-tuned"))
    register(tmp_path, trained_entry(name="retrained"))
    listed = json.loads(trained_catalog_path(tmp_path).read_text(encoding="utf-8"))
    assert [entry["id"] for entry in listed["resource"]] == ["gliner-sk-tuned", "gliner-cs-tuned"]
    assert load_catalog(root=tmp_path)["gliner-cs-tuned"].name == "retrained"
    with pytest.raises(ValueError, match="duplicate resource id"):
        register(tmp_path, trained_entry(id="gliner-multi-v2.1"))


WEIGHTS = b"stand-in weights after training"


class StandInGliner:
    """What training uses of a GLiNER model: saving its weights."""

    def save_pretrained(self, directory: Path, *, safe_serialization: bool) -> None:
        assert safe_serialization
        directory.mkdir(parents=True)
        (directory / "model.safetensors").write_bytes(WEIGHTS)
        # gliner also writes its own config and the tokenizer; neither is kept.
        (directory / "gliner_config.json").write_text('{"class_token_index": 9}')
        (directory / "tokenizer_config.json").write_text("{}")


class Recorder:
    def __init__(self) -> None:
        self.fitted: list[list[dict[str, Any]]] = []
        self.loaded: list[str] = []

    def fit(self, model: Any, examples: list[dict[str, Any]], config: TrainConfig, work: Path):
        assert isinstance(model, StandInGliner)
        assert work.is_dir()
        self.fitted.append(examples)
        return {"loss": [{"step": 1, "loss": 2.5}], "summary": {"train_runtime": 0.1}}

    def load(self, root: Path, model_id: str, catalog: Any) -> Any:
        self.loaded.append(model_id)
        if model_id == "gliner-multi-v2.1":
            return StandInGliner()
        # The stored model, loaded through the root's catalog.
        assert catalog[model_id].trained
        return ScoredStandIn({"Jan Novák": ("person", 0.9)})


def test_training_stores_registers_and_scores_the_model(training_root: Path, tmp_path: Path):
    recorder = Recorder()
    results = train(
        parse_train_config(CONFIG),
        resource_root=training_root,
        cache_dir=tmp_path / "cache",
        fit=recorder.fit,
        load=recorder.load,
    )
    assert recorder.loaded == ["gliner-multi-v2.1", "gliner-cs-test"]
    (examples,) = recorder.fitted
    assert results["examples"]["drawn"] == {
        "cnec-2.0/train": results["examples"]["converted"]["cnec-2.0/train"],
        "openpii-1m-cs/train": 2,
        "uner-sk-snk/train": 1,
    }
    assert len(examples) == results["examples"]["count"]
    assert {tuple(example["ner_labels"]) for example in examples} >= {ALL_LABELS}

    stored = training_root / "models/gliner-cs-test"
    assert sorted(path.name for path in stored.iterdir()) == [
        "gliner_config.json",
        "model.safetensors",
    ]
    # The base model's config, not the one gliner wrote.
    assert (stored / "gliner_config.json").read_text() == '{"max_len": 384}'
    entry = load_catalog(root=training_root)["gliner-cs-test"]
    weights_sha256 = hashlib.sha256(WEIGHTS).hexdigest()
    assert entry.version == weights_sha256
    assert {item.path: item.sha256 for item in entry.files}["model.safetensors"] == weights_sha256
    assert entry.real_personal_data  # trained on CNEC and UNER
    assert entry.languages == ("cs", "sk")
    assert entry.source == "experiments/results/train-test.json"

    assert results["model"]["id"] == "gliner-cs-test"
    assert results["datasets"] == {
        "cnec-2.0": load_catalog()["cnec-2.0"].version,
        "uner-sk-snk": load_catalog()["uner-sk-snk"].version,
        "openpii-1m": load_catalog()["openpii-1m"].version,
    }
    cnec = results["evaluation"]["corpora"]["cnec-2.0/dtest"]
    person = cnec["systems"]["rules+gliner-cs-test"]["scores"]["partial"]["person"]
    assert person["counts"]["predicted_matched"] >= 1
    # Counts and scores only: no corpus text in the results.
    assert "Novák" not in json.dumps(results, ensure_ascii=False)


def test_the_command_writes_the_results(
    training_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    from experiments import train as train_module

    recorder = Recorder()
    monkeypatch.setattr(train_module, "fit_gliner", recorder.fit)
    monkeypatch.setattr(train_module, "_loader", lambda device: recorder.load)
    config = tmp_path / "train-test.toml"
    config.write_text(
        'name = "train-test"\nmodel = "gliner-cs-test"\ndevice = "cpu"\n'
        "[training]\nsteps = 1\n"
        '[[corpora]]\nid = "openpii-1m-cs"\nsplit = "train"\n',
        encoding="utf-8",
    )
    out = tmp_path / "results"
    args = ["train", "--config", str(config), "--out", str(out)]
    assert main([*args, "--resource-root", str(training_root)]) == 0
    results = json.loads((out / "train-test.json").read_text(encoding="utf-8"))
    assert results["evaluation"] is None
    assert not (out / "train-test.md").exists()
    assert results["training"]["steps"] == 1
