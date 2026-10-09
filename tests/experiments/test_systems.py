"""Systems built through the pipeline, and the name model's cache."""

import json
from pathlib import Path

import pytest
from anonymizer.core.detect import CombinedDetector, GlinerDetector, NamesOnly, RuleDetector
from anonymizer.core.detect import models as models_module
from anonymizer.core.resources import Catalog
from anonymizer.core.types import Document, EntityType

from experiments.datasets import make_page
from experiments.systems import (
    CACHE_FLOOR,
    CachedSpanModel,
    PredictionCache,
    SystemConfig,
    build_system_detector,
    cache_path,
    detect,
    gliner_loader,
    model_versions,
    parse_system,
)
from tests.experiments.conftest import ScoredStandIn

TEXT = "Smlouvu podepsal pan Jan Novák v Brně."


def _model(tmp_path: Path, stand_in: ScoredStandIn) -> CachedSpanModel:
    return CachedSpanModel(lambda: stand_in, PredictionCache(tmp_path / "cache.json"))


class TestParseSystem:
    def test_defaults_are_the_shipped_settings(self):
        system = parse_system("shipped", {"model": "gliner"})
        assert system.threshold == 0.3
        assert system.distractors == ("organization",)
        assert system.names_only and system.propagate
        assert system.labels == {"person": EntityType.PERSON, "street address": EntityType.ADDRESS}

    def test_options(self):
        system = parse_system(
            "ablation",
            {
                "model": "gliner",
                "threshold": 0.5,
                "labels": {"person": "person"},
                "distractors": [],
                "names_only": False,
                "propagate": False,
                "language": "auto",
            },
        )
        assert system.describe() == {
            "model": "gliner",
            "propagate": False,
            "language": "auto",
            "threshold": 0.5,
            "labels": {"person": "person"},
            "distractors": [],
            "names_only": False,
        }

    def test_rules_describe_no_model_options(self):
        assert parse_system("rules", {}).describe() == {
            "model": "none",
            "propagate": True,
            "language": "dataset",
        }

    @pytest.mark.parametrize(
        ("table", "message"),
        [
            ({"modle": "gliner"}, "unknown options"),
            ({"model": "spacy"}, "unknown name model 'spacy'"),
            ({"language": "cs"}, "language must be"),
            ({"threshold": 0.05}, "threshold must"),
        ],
    )
    def test_invalid(self, table: dict, message: str):
        with pytest.raises(ValueError, match=message):
            parse_system("bad", table)


class TestBuild:
    def test_rules_alone(self):
        assert isinstance(build_system_detector(SystemConfig("rules"), "cs", None), RuleDetector)

    def test_model_needed(self, tmp_path: Path):
        with pytest.raises(ValueError, match="needs the name model"):
            build_system_detector(SystemConfig("x", model="gliner"), "cs", None)

    def test_name_filter_switch(self, tmp_path: Path):
        model = _model(tmp_path, ScoredStandIn({}))
        shipped = build_system_detector(SystemConfig("x", model="gliner"), "cs", model)
        unfiltered = build_system_detector(
            SystemConfig("x", model="gliner", names_only=False), "cs", model
        )
        assert isinstance(shipped, CombinedDetector)
        assert isinstance(unfiltered, CombinedDetector)
        assert isinstance(shipped.detectors[1], NamesOnly)
        assert isinstance(unfiltered.detectors[1], GlinerDetector)


def _detected(system: SystemConfig, model: CachedSpanModel | None, language: str = "cs") -> set:
    document = Document(pages=[make_page(0, TEXT)])
    detect(system, document, language, model)
    return {(str(entity.type), entity.text) for entity in document.entities}


def test_the_options_reach_the_pipeline(tmp_path: Path):
    stand_in = ScoredStandIn({"pan Jan Novák": ("person", 0.8), "Brně": ("street address", 0.35)})
    model = _model(tmp_path, stand_in)
    # The name filter trims the lowercase word; the 0.35 address passes 0.3 only.
    assert _detected(SystemConfig("x", model="gliner"), model) == {
        ("person", "Jan Novák"),
        ("address", "Brně"),
    }
    assert _detected(SystemConfig("x", model="gliner", threshold=0.4), model) == {
        ("person", "Jan Novák")
    }
    assert _detected(SystemConfig("x", model="gliner", names_only=False), model) == {
        ("person", "pan Jan Novák"),
        ("address", "Brně"),
    }
    # The model was asked once, at the floor; the rest came from the cache.
    assert stand_in.calls == 1
    assert stand_in.thresholds == [CACHE_FLOOR]


def test_language_options(tmp_path: Path):
    document = Document(pages=[make_page(0, TEXT)])
    detect(SystemConfig("x", language="none"), document, "cs", None)
    assert document.language is None
    detect(SystemConfig("x", language="auto"), document, "sk", None)
    assert document.language in {"cs", None}
    detect(SystemConfig("x"), document, "sk", None)
    assert document.language == "sk"


class TestCache:
    def test_reused_across_instances_and_text_free(self, tmp_path: Path):
        stand_in = ScoredStandIn({"Jan Novák": ("person", 0.9)})
        first = _model(tmp_path, stand_in)
        first.inference([TEXT], ["person"], threshold=0.3, flat_ner=True)
        first.cache.save()
        assert (first.hits, first.misses) == (0, 1)
        stored = (tmp_path / "cache.json").read_text(encoding="utf-8")
        assert "Novák" not in stored
        assert json.loads(stored)  # one entry, offsets and scores only

        second = _model(tmp_path, ScoredStandIn({}))
        answer = second.inference([TEXT], ["person"], threshold=0.3, flat_ner=True)
        assert (second.hits, second.misses) == (1, 0)
        assert [(span["start"], span["end"]) for span in answer[0]] == [
            (TEXT.index("Jan"), TEXT.index(" v Brně"))
        ]

    def test_a_different_prompt_misses(self, tmp_path: Path):
        stand_in = ScoredStandIn({"Jan Novák": ("person", 0.9)})
        model = _model(tmp_path, stand_in)
        model.inference([TEXT], ["person"], threshold=0.3, flat_ner=True)
        model.inference([TEXT], ["person", "organization"], threshold=0.3, flat_ner=True)
        assert stand_in.calls == 2

    def test_below_the_floor_is_refused(self, tmp_path: Path):
        model = _model(tmp_path, ScoredStandIn({}))
        with pytest.raises(ValueError, match="below the cache floor"):
            model.inference([TEXT], ["person"], threshold=0.05, flat_ner=True)

    def test_unchanged_cache_is_not_rewritten(self, tmp_path: Path):
        cache = PredictionCache(tmp_path / "nested" / "cache.json")
        cache.save()
        assert not cache.path.exists()
        cache["key"] = []
        cache.save()
        assert cache.path.exists()
        assert len(PredictionCache(cache.path)) == 1

    def test_path_names_model_dataset_and_split(self, tmp_path: Path):
        path = cache_path(tmp_path, "gliner-multi-v2.1", "cnec-2.0", "hdl:11858/00-097C", "dtest")
        assert path.parent.name == "cnec-2.0@hdl_11858_00-097C"
        assert path.parent.parent.name.startswith("gliner-multi-v2.1@")
        assert path.name == "dtest.json"


def test_loader_reports_missing_model(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="model files missing"):
        gliner_loader(tmp_path)("gliner-multi-v2.1")


def test_model_versions():
    assert model_versions([SystemConfig("rules")]) == {}
    versions = model_versions([SystemConfig("x", model="gliner")])
    assert set(versions) == {"gliner-multi-v2.1", "mdeberta-v3-base-tokenizer"}


class TestModels:
    def test_the_earlier_name_and_the_catalog_id_are_one_model(self):
        assert SystemConfig("x", model="gliner").model_id == "gliner-multi-v2.1"
        assert SystemConfig("x", model="gliner-multi-v2.1").model_id == "gliner-multi-v2.1"
        assert SystemConfig("x").model_id is None
        # Results keep the name the config used.
        assert parse_system("x", {"model": "gliner"}).describe()["model"] == "gliner"

    def test_another_catalog_gliner_model_is_a_system_model(
        self, monkeypatch: pytest.MonkeyPatch, tuned_catalog: Catalog
    ):
        system = parse_system("tuned", {"model": "gliner-cs-tuned"})
        assert system.model_id == "gliner-cs-tuned"
        assert set(model_versions([system])) == {"gliner-cs-tuned", "mdeberta-v3-base-tokenizer"}
        detector = build_system_detector(system, "cs", ScoredStandIn({}))
        assert isinstance(detector, CombinedDetector)
        assert "gliner-cs-tuned" in detector.name

    def test_a_model_of_another_engine_is_refused(
        self, monkeypatch: pytest.MonkeyPatch, tuned_catalog: Catalog
    ):
        # A second engine the core can run, whose output the harness cannot cache yet.
        monkeypatch.setitem(
            models_module.NAME_MODEL_ENGINES,
            "transformers",
            models_module.NameModelEngine(lambda *_: RuleDetector([]), "transformers", "ner"),
        )
        with pytest.raises(ValueError, match="runs on transformers, not gliner"):
            parse_system("x", {"model": "token-classifier"})
