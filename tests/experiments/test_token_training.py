"""Training a token classifier: configs, features, the loss, storing, and a tiny real run.

The loss and the real run need PyTorch and `transformers` and are skipped
without them (CI installs no training group); the real run trains a tiny
random XLM-RoBERTa built offline on the synthetic corpora. Every name and
number is invented.
"""

import copy
import json
import math
import os
import shutil
import tomllib
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.detect import GlinerDetector, load_name_model
from anonymizer.core.resources import load_catalog
from anonymizer.core.types import EntityType

from experiments import run as run_module
from experiments.examples import Example
from experiments.token_training import (
    IGNORED,
    LABELS,
    features,
    word_tags,
)
from experiments.train import TrainConfig, parse_train_config, train, with_device
from tests.detect.test_token_classifier import _page
from tests.experiments.conftest import ScoredStandIn
from tests.token_classifier_builders import StandInTokenizer, tiny_token_classifier

CONFIG: dict[str, Any] = {
    "name": "train-xlmr-test",
    "model": "xlmr-cs-test",
    "base": "xlm-roberta-large",
    "seed": 5,
    "device": "cpu",
    "training": {
        "steps": 4,
        "batch_size": 2,
        "learning_rate": 1e-3,
        "loss": "ce",
        "logging_steps": 1,
    },
    "corpora": [
        {"id": "cnec-2.0", "split": "train"},
        {"id": "uner-sk-snk", "split": "train", "examples": 2},
        {"id": "openpii-1m-cs", "split": "train", "examples": 2},
    ],
    "evaluate": {"limit": 2, "datasets": [{"id": "cnec-2.0", "split": "dtest"}]},
}

EXAMPLE = Example(
    tokens=("Smlouvu", "podepsal", "Jan", "Novák", ",", "Lipová", "12"),
    spans=((2, 3, "person"), (5, 6, "street address")),
    labels=("person", "street address"),
)


def _training(**change: Any) -> dict[str, Any]:
    raw = copy.deepcopy(CONFIG)
    raw["training"] |= change
    return raw


class TestConfig:
    def test_an_encoder_base_trains_a_token_classifier(self):
        config = parse_train_config(CONFIG)
        assert (config.base, config.engine) == ("xlm-roberta-large", "token-classifier")
        assert config.training.precision == "fp32"
        assert parse_train_config(_training(precision="bf16")).training.precision == "bf16"

    def test_a_gliner_base_still_trains_gliner(self):
        config = parse_train_config({**CONFIG, "base": "gliner"})
        assert (config.base, config.engine) == ("gliner-multi-v2.1", "gliner")

    @pytest.mark.parametrize(
        ("change", "message"),
        [
            ({"loss": "focal", "focal_alpha": 0.75}, "token classifier's loss must be"),
            ({"head_learning_rate": 1e-4}, "apply to GLiNER only"),
            ({"loss": "weighted", "negative_focus": 1.0}, "apply to GLiNER only"),
            ({"precision": "fp8"}, "precision must be one of"),
        ],
    )
    def test_what_a_token_classifier_does_not_train_with_is_refused(
        self, change: dict[str, Any], message: str
    ):
        with pytest.raises(ValueError, match=message):
            parse_train_config(_training(**change))

    def test_the_xlmr_config_trains_on_the_data_of_the_gliner_one(self):
        configs = Path(__file__).parents[2] / "experiments" / "configs"
        gliner, xlmr = (
            tomllib.loads((configs / f"{name}.toml").read_text(encoding="utf-8"))
            for name in ("train-cs-sk-ce", "train-cs-sk-xlmr-ce")
        )
        for key in ("corpora", "evaluate", "seed"):
            assert xlmr[key] == gliner[key]
        assert parse_train_config(xlmr).engine == "token-classifier"

    def test_the_weighted_loss_takes_its_weight(self):
        training = parse_train_config(_training(loss="weighted", positive_weight=3)).training
        assert (training.loss, training.positive_weight) == ("weighted", 3.0)

    def test_half_precision_off_cuda_is_refused_before_any_data_is_read(
        self, training_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        from experiments import train as train_module

        def no_data(*_: object) -> None:
            raise AssertionError("data read for a precision the device cannot run")

        monkeypatch.setattr(train_module, "training_examples", no_data)
        config = parse_train_config(_training(precision="bf16"))
        with pytest.raises(ValueError, match="bf16 needs device cuda"):
            train(config, resource_root=training_root, cache_dir=tmp_path)


class TestFeatures:
    def test_bio_tags_per_word(self):
        assert word_tags(EXAMPLE) == [
            "O",
            "O",
            "B-person",
            "I-person",
            "O",
            "B-street address",
            "I-street address",
        ]

    def test_each_word_is_labelled_at_its_first_subword_only(self):
        tokenizer = StandInTokenizer()
        encoded = features(EXAMPLE, tokenizer, 512)
        ids = {label: index for index, label in enumerate(LABELS)}
        # Pieces of four characters: Smlouvu 2, podepsal 2, Jan 1, Novák 2, "," 1, Lipová 2, 12 1.
        assert encoded.labels == [
            IGNORED,
            ids["O"],
            IGNORED,
            ids["O"],
            IGNORED,
            ids["B-person"],
            ids["I-person"],
            IGNORED,
            ids["O"],
            ids["B-street address"],
            IGNORED,
            ids["I-street address"],
            IGNORED,
        ]
        assert encoded.input_ids[0] == tokenizer.cls_token_id
        assert encoded.input_ids[-1] == tokenizer.sep_token_id
        assert len(encoded.input_ids) == len(encoded.labels)
        assert not encoded.truncated

    def test_labels_of_types_the_corpus_does_not_mark_are_accepted_for_outside(self):
        encoded = features(EXAMPLE, StandInTokenizer(), 512)
        accepted = [label for label, open_ in zip(LABELS, encoded.unmarked, strict=True) if open_]
        assert accepted == ["B-organization", "I-organization"]
        everything = Example(
            EXAMPLE.tokens, EXAMPLE.spans, ("person", "street address", "organization")
        )
        assert not any(features(everything, StandInTokenizer(), 512).unmarked)

    def test_an_example_too_long_is_cut_after_its_last_whole_word(self):
        encoded = features(EXAMPLE, StandInTokenizer(), 8)
        # [CLS] Smlouvu(2) podepsal(2) Jan(1) [SEP] = 7; Novák (2 pieces) would make 9.
        assert len(encoded.input_ids) == 7
        assert encoded.truncated
        assert len(encoded.labels) == 7


class TestLoss:
    @pytest.fixture
    def torch(self) -> Any:
        return pytest.importorskip("torch")

    def _logits(self, torch: Any, rows: list[list[float]]) -> Any:
        return torch.tensor([rows], dtype=torch.float32)

    def test_with_every_type_marked_it_is_cross_entropy(self, torch: Any):
        from experiments.token_training import token_loss

        generator = torch.Generator().manual_seed(3)
        logits = torch.randn(2, 5, len(LABELS), generator=generator)
        labels = torch.tensor([[IGNORED, 0, 1, 2, IGNORED], [IGNORED, 0, 0, 5, 6]])
        unmarked = torch.zeros(2, len(LABELS), dtype=torch.bool)
        expected = torch.nn.functional.cross_entropy(
            logits.reshape(-1, len(LABELS)), labels.reshape(-1), ignore_index=IGNORED
        )
        assert token_loss(logits, labels, unmarked).item() == pytest.approx(expected.item())

    def test_an_outside_word_also_accepts_the_unmarked_labels(self, torch: Any):
        from experiments.token_training import token_loss

        logits = torch.zeros(1, 1, len(LABELS))
        labels = torch.tensor([[0]])
        unmarked = torch.tensor([[label.endswith("organization") for label in LABELS]])
        # Uniform over 7 labels: O alone has 1/7, O or an organisation 3/7.
        assert token_loss(logits, labels, unmarked).item() == pytest.approx(-math.log(3 / 7))
        none = torch.zeros(1, len(LABELS), dtype=torch.bool)
        assert token_loss(logits, labels, none).item() == pytest.approx(-math.log(1 / 7))

    def test_the_weight_multiplies_the_words_inside_a_span(self, torch: Any):
        from experiments.token_training import token_loss

        logits = torch.zeros(1, 2, len(LABELS))
        labels = torch.tensor([[0, 1]])
        unmarked = torch.zeros(1, len(LABELS), dtype=torch.bool)
        each = -math.log(1 / 7)
        assert token_loss(logits, labels, unmarked, 3.0).item() == pytest.approx(
            (each + 3 * each) / 2
        )


WEIGHTS = b"stand-in token classifier weights"


class StandInTrainee:
    def save_pretrained(self, directory: Path, *, safe_serialization: bool) -> None:
        directory.mkdir(parents=True)
        (directory / "model.safetensors").write_bytes(WEIGHTS)
        (directory / "config.json").write_text('{"id2label": {"0": "O"}}')
        (directory / "training_args.bin").write_bytes(b"not kept")


def test_training_stores_and_registers_a_token_classifier(training_root: Path, tmp_path: Path):
    fitted: list[list[Example]] = []

    def fit(model: Any, examples: list[Example], config: TrainConfig, work: Path):
        assert isinstance(model, StandInTrainee)
        fitted.append(examples)
        return {"loss": [], "summary": {}, "truncated": 0}

    def load(root: Path, model_id: str, catalog: Any) -> Any:
        if model_id == "xlm-roberta-large":
            return StandInTrainee()
        assert catalog[model_id].engine == "token-classifier"
        return ScoredStandIn({"Jan Novák": ("person", 0.9)})

    results = train(
        parse_train_config(CONFIG),
        resource_root=training_root,
        cache_dir=tmp_path / "cache",
        fit=fit,
        load=load,
    )
    stored = training_root / "models/xlmr-cs-test"
    assert sorted(path.name for path in stored.iterdir()) == ["config.json", "model.safetensors"]
    entry = load_catalog(root=training_root)["xlmr-cs-test"]
    assert entry.engine == "token-classifier"
    assert entry.requires == ("xlm-roberta-large-tokenizer",)
    assert entry.name.startswith("Token classifier trained on this machine from xlm-roberta-large")
    assert results["base"]["id"] == "xlm-roberta-large"
    person = results["evaluation"]["corpora"]["cnec-2.0/dtest"]["systems"]["rules+xlmr-cs-test"][
        "scores"
    ]["partial"]["person"]
    assert person["counts"]["predicted_matched"] >= 1
    assert len(fitted[0]) == results["examples"]["count"]


@pytest.fixture
def tiny_root(training_root: Path, tmp_path: Path) -> Path:
    """The training root with a tiny random encoder stored as the catalog's XLM-R large."""
    pytest.importorskip("torch")
    pytest.importorskip("transformers")
    model_dir, tokenizer_dir = tiny_token_classifier(tmp_path / "tiny", max_length=64)
    models = training_root / "models"
    shutil.copytree(model_dir, models / "xlm-roberta-large")
    shutil.copytree(tokenizer_dir, models / "xlm-roberta-large-tokenizer")
    # The catalog lists the real tokenizer's files; the tiny one needs only tokenizer.json.
    shutil.copyfile(model_dir / "config.json", models / "xlm-roberta-large-tokenizer/config.json")
    (models / "xlm-roberta-large-tokenizer/sentencepiece.bpe.model").write_bytes(b"")
    return training_root


def test_a_tiny_token_classifier_trains_scores_and_loads_by_catalog_id(
    tiny_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    results = train(
        parse_train_config(CONFIG), resource_root=tiny_root, cache_dir=tmp_path / "cache"
    )
    log = results["training"]["log"]
    assert log["loss"]
    assert log["truncated"] >= 0
    assert results["model"]["engine"] == "token-classifier"
    stored = tiny_root / "models/xlmr-cs-test"
    labels = json.loads((stored / "config.json").read_text(encoding="utf-8"))["id2label"]
    assert list(labels.values()) == list(LABELS)
    assert "rules+xlmr-cs-test" in results["evaluation"]["corpora"]["cnec-2.0/dtest"]["systems"]
    # Counts and scores only: no corpus text in the results.
    assert "Novák" not in json.dumps(results, ensure_ascii=False)

    detector = load_name_model("xlmr-cs-test", tiny_root)
    assert isinstance(detector, GlinerDetector)
    entities = detector.detect(_page("Smlouvu podepsal Jan Novák, bytem Lipová 12, Brno."))
    assert all(entity.type in {EntityType.PERSON, EntityType.ADDRESS} for entity in entities)

    # The same seed draws the same classification layer and trains it the same way.
    monkeypatch.setattr(run_module, "device_available", lambda device: True)
    again = train(
        with_device(parse_train_config({**CONFIG, "model": "xlmr-cs-again"}), "cpu"),
        resource_root=tiny_root,
        cache_dir=tmp_path / "cache-again",
    )
    assert again["model"]["version"] == results["model"]["version"]


ROOT = Path(os.environ.get("ANONYMIZER_RESOURCE_ROOT", Path(__file__).resolve().parents[2]))


@pytest.mark.model
def test_the_real_encoder_loads_with_a_seeded_layer_for_the_labels():
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from experiments.token_training import collate, load_base, token_loss

    catalog = load_catalog()
    try:
        trainee = load_base(ROOT, "xlm-roberta-large", catalog, seed=1)
    except FileNotFoundError:
        pytest.skip("XLM-R large not fetched")
    assert trainee.model.config.num_labels == len(LABELS)
    assert [trainee.model.config.id2label[i] for i in range(len(LABELS))] == list(LABELS)
    batch = collate([features(EXAMPLE, trainee.tokenizer, 512)], trainee.tokenizer.pad_token_id)
    labels, unmarked = batch.pop("labels"), batch.pop("unmarked")
    with torch.inference_mode():
        logits = trainee.model(**batch).logits
    assert math.isfinite(token_loss(logits, labels, unmarked).item())
