"""The name-model registry: models chosen by catalog id, loaded by their engine."""

import dataclasses
import importlib.util
import sys
from pathlib import Path

import pytest
from anonymizer.core.detect import (
    DEFAULT_NAME_MODEL,
    CombinedDetector,
    GlinerDetector,
    load_name_model,
    missing_name_model_files,
    name_model,
    name_model_installed,
    name_model_threshold,
    name_models,
    system_model,
    union_members,
)
from anonymizer.core.detect import gliner as gliner_module
from anonymizer.core.detect.gliner import (
    DEFAULT_DISTRACTORS,
    DEFAULT_LABELS,
    DEFAULT_THRESHOLD,
    encoder_resource,
)
from anonymizer.core.pipeline import build_detector
from anonymizer.core.resources import Catalog, Resource, ResourceFile, load_catalog

from tests.detect.test_gliner import StandInModel, _page
from tests.resources.test_catalog import store_trained, trained_entry, union_entry


def _resource(
    resource_id: str,
    uses: tuple[str, ...],
    engine: str | None = None,
    requires: tuple[str, ...] = (),
) -> Resource:
    return Resource(
        id=resource_id,
        name=resource_id.replace("-", " "),
        kind="model",
        uses=uses,
        source=f"https://example.org/{resource_id}",
        version="1",
        licence="Apache-2.0",
        languages=("cs",),
        files=(
            ResourceFile(
                path="weights.bin",
                url=f"https://example.org/{resource_id}/weights.bin",
                size=1,
                sha256="0" * 64,
            ),
        ),
        engine=engine,
        requires=requires,
    )


TOKENIZER = _resource("encoder-tokenizer", ("tokenizer",), "transformers")
CATALOG = Catalog(
    {
        "encoder-tokenizer": TOKENIZER,
        "gliner-multi-v2.1": _resource("gliner-multi-v2.1", ("ner",), "gliner", (TOKENIZER.id,)),
        # A fine-tuned GLiNER: the same engine, other weights.
        "gliner-cs-tuned": _resource("gliner-cs-tuned", ("ner",), "gliner", (TOKENIZER.id,)),
        # A model of an engine with no loader is not offered.
        "token-classifier": _resource("token-classifier", ("ner",), "transformers"),
        "ocr-reader": _resource("ocr-reader", ("ocr-recognition",), "onnxtr"),
    }
)


class TestChoosing:
    def test_the_shipped_catalog_offers_the_zero_shot_model_first(self):
        assert name_models()[0].id == DEFAULT_NAME_MODEL
        assert DEFAULT_NAME_MODEL == "gliner-multi-v2.1"

    def test_every_ner_model_of_a_known_engine_is_offered_in_catalog_order(self):
        assert [model.id for model in name_models(CATALOG)] == [
            "gliner-multi-v2.1",
            "gliner-cs-tuned",
        ]

    def test_the_earlier_name_gliner_is_the_default_model(self):
        assert name_model("gliner").id == DEFAULT_NAME_MODEL
        assert name_model("gliner-cs-tuned", CATALOG).id == "gliner-cs-tuned"

    @pytest.mark.parametrize("model_id", ["token-classifier", "ocr-reader", "nonexistent"])
    def test_anything_else_is_refused_with_the_choices(self, model_id: str):
        with pytest.raises(ValueError, match=r"choose from \['gliner-cs-tuned', 'gliner-multi"):
            name_model(model_id, CATALOG)


class TestFiles:
    def test_missing_files_are_listed_in_download_order(self, tmp_path: Path):
        assert missing_name_model_files(DEFAULT_NAME_MODEL, tmp_path) == [
            "mdeberta-v3-base-tokenizer",
            "gliner-multi-v2.1",
        ]

    def test_no_files_are_missing_once_every_file_is_stored(self, tmp_path: Path):
        for resource in load_catalog().with_requirements(DEFAULT_NAME_MODEL):
            for item in resource.files:
                stored = resource.directory(tmp_path) / item.path
                stored.parent.mkdir(parents=True, exist_ok=True)
                stored.write_bytes(b"")
        assert missing_name_model_files("gliner", tmp_path) == []

    def test_installed_is_checked_without_importing(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setitem(sys.modules, "gliner", None)
        assert name_model_installed(DEFAULT_NAME_MODEL) is False
        monkeypatch.delitem(sys.modules, "gliner")
        monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
        assert name_model_installed(DEFAULT_NAME_MODEL) is True


class TestLoading:
    @pytest.fixture
    def loaded_from(self, monkeypatch: pytest.MonkeyPatch) -> list[tuple[Path, Path]]:
        """Stand in for gliner, recording the model and encoder folders it is given."""
        folders: list[tuple[Path, Path]] = []

        def load(model_dir: Path, encoder_dir: Path) -> StandInModel:
            folders.append((model_dir, encoder_dir))
            return StandInModel({})

        monkeypatch.setattr(gliner_module, "load_gliner", load)
        monkeypatch.setattr(gliner_module, "missing_resources", lambda *_: [])
        return folders

    def test_the_default_model_keeps_the_shipped_settings(
        self, loaded_from: list[tuple[Path, Path]]
    ):
        root = Path("/models-root")
        detector = load_name_model("gliner", root)
        assert isinstance(detector, GlinerDetector)
        assert detector.name == DEFAULT_NAME_MODEL
        assert detector.labels == dict(DEFAULT_LABELS)
        assert detector.distractors == DEFAULT_DISTRACTORS
        assert detector.threshold == DEFAULT_THRESHOLD
        assert loaded_from == [
            (
                root / "models" / "gliner-multi-v2.1",
                root / "models" / "mdeberta-v3-base-tokenizer",
            )
        ]

    def test_another_entry_of_the_engine_loads_its_own_weights(
        self, loaded_from: list[tuple[Path, Path]]
    ):
        root = Path("/models-root")
        detector = load_name_model("gliner-cs-tuned", root, CATALOG)
        assert detector.name == "gliner-cs-tuned"
        assert loaded_from == [
            (root / "models" / "gliner-cs-tuned", root / "models" / "encoder-tokenizer")
        ]

    def test_a_model_trained_under_the_root_loads_from_there(
        self, tmp_path: Path, loaded_from: list[tuple[Path, Path]]
    ):
        store_trained(tmp_path, trained_entry())
        detector = load_name_model("gliner-cs-tuned", tmp_path)
        assert detector.name == "gliner-cs-tuned"
        assert loaded_from == [
            (
                tmp_path / "models" / "gliner-cs-tuned",
                tmp_path / "models" / "mdeberta-v3-base-tokenizer",
            )
        ]

    def test_a_missing_trained_model_points_to_its_training_record(self, tmp_path: Path):
        store_trained(tmp_path, trained_entry())
        with pytest.raises(FileNotFoundError, match=r"trained on this machine.*train-cs\.json"):
            load_name_model("gliner-cs-tuned", tmp_path)

    def test_missing_files_name_the_fetch_command_of_that_model(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match=r"download\.py fetch gliner-cs-tuned"):
            load_name_model("gliner-cs-tuned", tmp_path, CATALOG)

    def test_a_model_runs_at_its_entrys_threshold_unless_the_caller_gives_one(
        self, loaded_from: list[tuple[Path, Path]]
    ):
        root = Path("/models-root")
        tuned = dataclasses.replace(CATALOG["gliner-cs-tuned"], threshold=0.041)
        catalog = Catalog({**CATALOG.resources, tuned.id: tuned})
        detector = load_name_model("gliner-cs-tuned", root, catalog)
        assert isinstance(detector, GlinerDetector)
        assert detector.threshold == 0.041
        chosen = load_name_model("gliner-cs-tuned", root, catalog, threshold=0.5)
        assert isinstance(chosen, GlinerDetector)
        assert chosen.threshold == 0.5
        # Another model of the same catalog keeps the engine's default.
        default = load_name_model("gliner", root, catalog)
        assert isinstance(default, GlinerDetector)
        assert default.threshold == DEFAULT_THRESHOLD

    def test_a_trained_entrys_threshold_reaches_the_loaded_model(
        self, tmp_path: Path, loaded_from: list[tuple[Path, Path]]
    ):
        store_trained(tmp_path, trained_entry(threshold=0.041))
        detector = load_name_model("gliner-cs-tuned", tmp_path)
        assert isinstance(detector, GlinerDetector)
        assert detector.threshold == 0.041

    def test_the_encoder_is_the_one_tokenizer_a_model_requires(self):
        assert encoder_resource(load_catalog(), DEFAULT_NAME_MODEL) == "mdeberta-v3-base-tokenizer"
        no_tokenizer = Catalog(
            {"gliner-bare": _resource("gliner-bare", ("ner",), "gliner")},
        )
        with pytest.raises(ValueError, match="exactly one tokenizer, found 0"):
            encoder_resource(no_tokenizer, "gliner-bare")


class TestSystems:
    @pytest.mark.parametrize(
        ("system", "model_id"),
        [
            ("rules", None),
            ("rules+gliner", DEFAULT_NAME_MODEL),
            ("rules+gliner-multi-v2.1", DEFAULT_NAME_MODEL),
        ],
    )
    def test_a_system_names_its_model(self, system: str, model_id: str | None):
        assert system_model(system) == model_id

    def test_a_trained_model_is_known_to_its_roots_catalog_only(self, tmp_path: Path):
        store_trained(tmp_path, trained_entry())
        assert system_model("rules+gliner-cs-tuned", load_catalog(root=tmp_path)) == (
            "gliner-cs-tuned"
        )
        with pytest.raises(ValueError, match="unknown name model"):
            system_model("rules+gliner-cs-tuned")

    @pytest.mark.parametrize("system", ["gliner", "model+gliner", "rules+"])
    def test_other_names_are_refused(self, system: str):
        with pytest.raises(ValueError, match=r"choose|unknown"):
            system_model(system)


class TestThreshold:
    NAMETAG = "nametag3-czech-cnec2.0-240830"

    def test_the_caller_wins_then_the_entry_then_the_engine(self):
        tuned = dataclasses.replace(CATALOG["gliner-cs-tuned"], threshold=0.041)
        catalog = Catalog({**CATALOG.resources, tuned.id: tuned})
        assert name_model_threshold("gliner-cs-tuned", catalog, 0.2) == 0.2
        assert name_model_threshold("gliner-cs-tuned", catalog) == 0.041
        assert name_model_threshold("gliner", catalog) == DEFAULT_THRESHOLD

    def test_an_engine_without_a_threshold_has_none(self):
        assert name_model_threshold(self.NAMETAG) is None

    def test_a_threshold_for_an_engine_without_one_is_refused(self):
        with pytest.raises(ValueError, match="which has no threshold"):
            name_model_threshold(self.NAMETAG, threshold=0.3)
        shipped = load_catalog()
        nametag = dataclasses.replace(shipped[self.NAMETAG], threshold=0.3)
        catalog = Catalog({**shipped.resources, nametag.id: nametag})
        with pytest.raises(ValueError, match="which has no threshold"):
            name_model_threshold(self.NAMETAG, catalog)
        with pytest.raises(ValueError, match="which has no threshold"):
            load_name_model(self.NAMETAG, Path("/models-root"), catalog)


class TestUnion:
    @pytest.fixture
    def root(self, tmp_path: Path) -> Path:
        store_trained(tmp_path, trained_entry(threshold=0.041), union_entry())
        return tmp_path

    @pytest.fixture
    def stand_ins(self, monkeypatch: pytest.MonkeyPatch) -> dict[str, StandInModel]:
        """Each member finds its own names, chosen by the folder it is loaded from."""
        models = {
            "gliner-cs-tuned": StandInModel({"Jan Novák": "person", "Novák": "person"}),
            "gliner-multi-v2.1": StandInModel({"Novák": "person", "Petra Svobodová": "person"}),
        }
        monkeypatch.setattr(
            gliner_module, "load_gliner", lambda model_dir, _: models[model_dir.name]
        )
        monkeypatch.setattr(gliner_module, "missing_resources", lambda *_: [])
        return models

    def test_a_union_is_offered_and_loads_each_member_at_its_own_threshold(
        self, root: Path, stand_ins: dict[str, StandInModel]
    ):
        catalog = load_catalog(root=root)
        assert "cs-union" in [resource.id for resource in name_models(catalog)]
        assert union_members("cs-union", catalog) == ("gliner-cs-tuned", "gliner-multi-v2.1")
        detector = load_name_model("cs-union", root)
        assert isinstance(detector, CombinedDetector)
        assert detector.name == "cs-union"
        members = detector.detectors
        assert all(isinstance(member, GlinerDetector) for member in members)
        assert [member.threshold for member in members if isinstance(member, GlinerDetector)] == [
            0.041,
            DEFAULT_THRESHOLD,
        ]

    def test_the_union_reports_what_either_member_finds_merged(
        self, root: Path, stand_ins: dict[str, StandInModel]
    ):
        text = "Smlouvu podepsal Jan Novák a Petra Svobodová."
        detector = build_detector("cs", model=load_name_model("cs-union", root))
        found = sorted(str(entity.text) for entity in detector.detect(_page(text)))
        # "Novák" from both lies inside "Jan Novák" and is merged away.
        assert found == ["Jan Novák", "Petra Svobodová"]

    def test_a_union_has_no_threshold_of_its_own(self, root: Path):
        catalog = load_catalog(root=root)
        assert name_model_threshold("cs-union", catalog) is None
        with pytest.raises(ValueError, match="which has no threshold"):
            name_model_threshold("cs-union", catalog, 0.3)

    def test_missing_files_are_the_members(self, root: Path):
        assert missing_name_model_files("cs-union", root) == [
            "mdeberta-v3-base-tokenizer",
            "gliner-cs-tuned",
            "gliner-multi-v2.1",
        ]

    def test_installed_when_every_member_is(self, root: Path, monkeypatch: pytest.MonkeyPatch):
        catalog = load_catalog(root=root)
        monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
        assert name_model_installed("cs-union", catalog) is False
        monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
        assert name_model_installed("cs-union", catalog) is True

    def test_only_a_union_has_members(self, root: Path):
        with pytest.raises(ValueError, match="is not a union"):
            union_members("gliner-cs-tuned", load_catalog(root=root))

    def test_a_union_of_unions_is_refused(self, tmp_path: Path):
        nested = union_entry(id="outer", requires=["cs-union", "gliner-multi-v2.1"])
        store_trained(tmp_path, trained_entry(), union_entry(), nested)
        with pytest.raises(ValueError, match="a union among its members"):
            union_members("outer", load_catalog(root=tmp_path))
