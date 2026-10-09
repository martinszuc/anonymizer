"""Benchmark systems: the rules alone, or with a name model chosen by catalog id."""

from pathlib import Path

import pytest
from anonymizer.core.detect import CombinedDetector, GlinerDetector, RuleDetector

from benchmark import run as run_module
from benchmark.__main__ import main
from benchmark.run import detector_factories
from tests.detect.test_gliner import StandInModel


def test_each_model_is_loaded_once_whatever_its_systems_call_it(monkeypatch: pytest.MonkeyPatch):
    loads: list[tuple[str, Path]] = []

    def load(model_id: str, root: Path) -> GlinerDetector:
        loads.append((model_id, root))
        return GlinerDetector(StandInModel({}), name=model_id)

    monkeypatch.setattr(run_module, "load_name_model", load)
    factories = detector_factories(
        ("rules", "rules+gliner", "rules+gliner-multi-v2.1"), Path("/models-root")
    )
    assert loads == [("gliner-multi-v2.1", Path("/models-root"))]
    assert list(factories) == ["rules", "rules+gliner", "rules+gliner-multi-v2.1"]
    assert isinstance(factories["rules"]("cs"), RuleDetector)
    combined = factories["rules+gliner"]("cs")
    assert isinstance(combined, CombinedDetector)
    assert combined.name == factories["rules+gliner-multi-v2.1"]("cs").name


def test_model_versions_cover_every_system_model():
    assert run_module._model_versions(("rules",)) == {}
    assert set(run_module._model_versions(("rules", "rules+gliner"))) == {
        "gliner-multi-v2.1",
        "mdeberta-v3-base-tokenizer",
    }


@pytest.mark.parametrize("system", ["gliner", "rules+spacy"])
def test_an_unknown_system_is_refused(system: str, capsys: pytest.CaptureFixture, tmp_path: Path):
    with pytest.raises(ValueError, match="unknown"):
        detector_factories((system,), Path())
    with pytest.raises(SystemExit):
        main(["ocr", "--out", str(tmp_path), "--system", system])
    assert "unknown" in capsys.readouterr().err
