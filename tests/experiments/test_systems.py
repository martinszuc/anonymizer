"""Systems built through the pipeline, and the name models' caches."""

import json
from pathlib import Path

import pytest
from anonymizer.core.detect import (
    AgreementDetector,
    CombinedDetector,
    GlinerDetector,
    NamesOnly,
    NametagDetector,
    RuleDetector,
)
from anonymizer.core.detect import models as models_module
from anonymizer.core.resources import Catalog
from anonymizer.core.types import Document, EntityType

from experiments.datasets import make_page
from experiments.systems import (
    CACHE_FLOOR,
    CachedSpanModel,
    CachedTagger,
    NameModel,
    PredictionCache,
    SystemConfig,
    build_system_detector,
    cache_path,
    detect,
    gliner_loader,
    model_versions,
    parse_system,
)
from tests.experiments.conftest import ScoredStandIn, StandInSplitter, StandInTagger

TEXT = "Smlouvu podepsal pan Jan Novák v Brně."
GLINER = "gliner-multi-v2.1"
NAMETAG = "nametag3-czech-cnec2.0-240830"


def _model(tmp_path: Path, stand_in: ScoredStandIn) -> CachedSpanModel:
    return CachedSpanModel(lambda: stand_in, PredictionCache(tmp_path / "cache.json"))


def _tagger(tmp_path: Path, stand_in: StandInTagger) -> CachedTagger:
    return CachedTagger(
        lambda: stand_in, StandInSplitter, PredictionCache(tmp_path / "nametag.json")
    )


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

    def test_two_models_and_how_they_combine(self):
        system = parse_system("both", {"model": ["gliner", NAMETAG], "combine": "agreement"})
        assert system.model_ids == (GLINER, NAMETAG)
        assert system.describe() == {
            "model": ["gliner", NAMETAG],
            "combine": "agreement",
            "propagate": True,
            "language": "dataset",
            "threshold": 0.3,
            "labels": {"person": "person", "street address": "address"},
            "distractors": ["organization"],
            "names_only": True,
        }

    def test_nametag_alone_describes_no_gliner_options(self):
        assert parse_system("nametag", {"model": NAMETAG}).describe() == {
            "model": NAMETAG,
            "propagate": True,
            "language": "dataset",
            "names_only": True,
        }

    @pytest.mark.parametrize(
        ("table", "message"),
        [
            ({"model": ["gliner", "gliner-multi-v2.1"]}, "two different models"),
            ({"model": [NAMETAG]}, "two different models"),
            ({"model": ["gliner", NAMETAG], "combine": "intersection"}, "combine must be"),
        ],
    )
    def test_invalid_combinations(self, table: dict, message: str):
        with pytest.raises(ValueError, match=message):
            parse_system("bad", table)


class TestBuild:
    def test_rules_alone(self):
        assert isinstance(build_system_detector(SystemConfig("rules"), "cs", {}), RuleDetector)

    def test_model_needed(self, tmp_path: Path):
        with pytest.raises(ValueError, match=r"needs the name model gliner-multi-v2\.1"):
            build_system_detector(SystemConfig("x", model="gliner"), "cs", {})

    def test_name_filter_switch(self, tmp_path: Path):
        models = {GLINER: _model(tmp_path, ScoredStandIn({}))}
        shipped = build_system_detector(SystemConfig("x", model="gliner"), "cs", models)
        unfiltered = build_system_detector(
            SystemConfig("x", model="gliner", names_only=False), "cs", models
        )
        assert isinstance(shipped, CombinedDetector)
        assert isinstance(unfiltered, CombinedDetector)
        assert isinstance(shipped.detectors[1], NamesOnly)
        assert isinstance(unfiltered.detectors[1], GlinerDetector)

    @pytest.mark.parametrize(
        ("combine", "kind"), [("union", CombinedDetector), ("agreement", AgreementDetector)]
    )
    def test_two_models(self, tmp_path: Path, combine: str, kind: type):
        models: dict[str, NameModel] = {
            GLINER: _model(tmp_path, ScoredStandIn({})),
            NAMETAG: _tagger(tmp_path, StandInTagger({})),
        }
        system = SystemConfig("x", model=("gliner", NAMETAG), combine=combine)
        detector = build_system_detector(system, "cs", models)
        assert isinstance(detector, CombinedDetector)
        filtered = detector.detectors[1]
        assert isinstance(filtered, NamesOnly)
        combined = filtered.detector
        assert isinstance(combined, CombinedDetector | AgreementDetector)
        assert type(combined) is kind
        members = combined.detectors
        assert isinstance(members[0], GlinerDetector)
        assert isinstance(members[1], NametagDetector)


def _detected(
    system: SystemConfig, models: dict[str, NameModel], language: str = "cs", text: str = TEXT
) -> set:
    document = Document(pages=[make_page(0, text)])
    detect(system, document, language, models)
    return {(str(entity.type), entity.text) for entity in document.entities}


def test_the_options_reach_the_pipeline(tmp_path: Path):
    stand_in = ScoredStandIn({"pan Jan Novák": ("person", 0.8), "Brně": ("street address", 0.35)})
    models: dict[str, NameModel] = {GLINER: _model(tmp_path, stand_in)}
    # The name filter trims the lowercase word; the 0.35 address passes 0.3 only.
    assert _detected(SystemConfig("x", model="gliner"), models) == {
        ("person", "Jan Novák"),
        ("address", "Brně"),
    }
    assert _detected(SystemConfig("x", model="gliner", threshold=0.4), models) == {
        ("person", "Jan Novák")
    }
    assert _detected(SystemConfig("x", model="gliner", names_only=False), models) == {
        ("person", "pan Jan Novák"),
        ("address", "Brně"),
    }
    # The model was asked once, at the floor; the rest came from the cache.
    assert stand_in.calls == 1
    assert stand_in.thresholds == [CACHE_FLOOR]


class TestCombinations:
    TEXT = "Smlouvu podepsal Jan Novák.\nSvědkem byla Eva Malá z Brna."

    def _models(self, tmp_path: Path) -> dict[str, NameModel]:
        gliner = ScoredStandIn({"Jan Novák": ("person", 0.9), "Eva": ("person", 0.8)})
        nametag = StandInTagger({("Jan", "Novák"): ("P", 0.99), ("Eva", "Malá"): ("P", 0.98)})
        return {GLINER: _model(tmp_path, gliner), NAMETAG: _tagger(tmp_path, nametag)}

    def test_each_model_alone(self, tmp_path: Path):
        models = self._models(tmp_path)
        assert _detected(SystemConfig("x", model="gliner"), models, text=self.TEXT) == {
            ("person", "Jan Novák"),
            ("person", "Eva"),
        }
        assert _detected(SystemConfig("x", model=NAMETAG), models, text=self.TEXT) == {
            ("person", "Jan Novák"),
            ("person", "Eva Malá"),
        }

    def test_union_keeps_what_either_found(self, tmp_path: Path):
        system = SystemConfig("x", model=("gliner", NAMETAG))
        assert _detected(system, self._models(tmp_path), text=self.TEXT) == {
            ("person", "Jan Novák"),
            ("person", "Eva Malá"),
        }

    def test_agreement_keeps_the_wider_of_two_overlapping_readings(self, tmp_path: Path):
        system = SystemConfig("x", model=("gliner", NAMETAG), combine="agreement")
        # Both found Jan Novák; "Eva" and "Eva Malá" overlap, so the whole name stays.
        assert _detected(system, self._models(tmp_path), text=self.TEXT) == {
            ("person", "Jan Novák"),
            ("person", "Eva Malá"),
        }

    def test_agreement_drops_what_one_model_alone_found(self, tmp_path: Path):
        gliner = ScoredStandIn({"Jan Novák": ("person", 0.9)})
        nametag = StandInTagger({("Eva", "Malá"): ("P", 0.98)})
        models: dict[str, NameModel] = {
            GLINER: _model(tmp_path, gliner),
            NAMETAG: _tagger(tmp_path, nametag),
        }
        system = SystemConfig("x", model=("gliner", NAMETAG), combine="agreement")
        assert _detected(system, models, text=self.TEXT) == set()


def test_language_options(tmp_path: Path):
    document = Document(pages=[make_page(0, TEXT)])
    detect(SystemConfig("x", language="none"), document, "cs", {})
    assert document.language is None
    detect(SystemConfig("x", language="auto"), document, "sk", {})
    assert document.language in {"cs", None}
    detect(SystemConfig("x"), document, "sk", {})
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

    def test_tagger_answers_from_the_cache_without_text(self, tmp_path: Path):
        stand_in = StandInTagger({("Jan", "Novák"): ("P", 0.9)})
        sentences = [["Podepsal", "Jan", "Novák", "."]]
        first = _tagger(tmp_path, stand_in)
        labels = first.tag(sentences)
        first.cache.save()
        assert (first.hits, first.misses) == (0, 1)
        assert "Novák" not in (tmp_path / "nametag.json").read_text(encoding="utf-8")

        second = _tagger(tmp_path, StandInTagger({}))
        assert second.tag(sentences) == labels
        assert labels[0][1] == [("B-P", 0.9)]
        assert (second.hits, second.misses) == (1, 0)
        assert stand_in.calls == 1
        # Other tokens miss.
        second.tag([["Podepsal", "Jan", "Novák", "!"]])
        assert second.misses == 1

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
    both = model_versions([SystemConfig("x", model=("gliner", NAMETAG))])
    assert set(both) == {
        "gliner-multi-v2.1",
        "mdeberta-v3-base-tokenizer",
        NAMETAG,
        "robeczech-base-v1.1-tokenizer",
    }


class TestModels:
    def test_the_earlier_name_and_the_catalog_id_are_one_model(self):
        assert SystemConfig("x", model="gliner").model_ids == ("gliner-multi-v2.1",)
        assert SystemConfig("x", model="gliner-multi-v2.1").model_ids == ("gliner-multi-v2.1",)
        assert SystemConfig("x").model_ids == ()
        # Results keep the name the config used.
        assert parse_system("x", {"model": "gliner"}).describe()["model"] == "gliner"

    def test_another_catalog_gliner_model_is_a_system_model(
        self, monkeypatch: pytest.MonkeyPatch, tuned_catalog: Catalog, tmp_path: Path
    ):
        system = parse_system("tuned", {"model": "gliner-cs-tuned"})
        assert system.model_ids == ("gliner-cs-tuned",)
        assert set(model_versions([system])) == {"gliner-cs-tuned", "mdeberta-v3-base-tokenizer"}
        models: dict[str, NameModel] = {"gliner-cs-tuned": _model(tmp_path, ScoredStandIn({}))}
        detector = build_system_detector(system, "cs", models)
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
        with pytest.raises(ValueError, match="runs on transformers, not gliner or nametag3"):
            parse_system("x", {"model": "token-classifier"})
