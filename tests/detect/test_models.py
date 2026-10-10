"""The name-model registry: models chosen by catalog id, loaded by their engine."""

import importlib.util
import sys
from pathlib import Path

import pytest
from anonymizer.core.detect import (
    DEFAULT_NAME_MODEL,
    GlinerDetector,
    load_name_model,
    missing_name_model_files,
    name_model,
    name_model_installed,
    name_models,
    system_model,
)
from anonymizer.core.detect import gliner as gliner_module
from anonymizer.core.detect.gliner import (
    DEFAULT_DISTRACTORS,
    DEFAULT_LABELS,
    DEFAULT_THRESHOLD,
    encoder_resource,
)
from anonymizer.core.resources import Catalog, Resource, ResourceFile, load_catalog

from tests.detect.test_gliner import StandInModel
from tests.resources.test_catalog import store_trained, trained_entry


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
