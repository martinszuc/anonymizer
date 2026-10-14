"""Earlier tags measured on the current documents, with git and uv stood in."""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from benchmark.backfill import backfill
from benchmark.spec import document_set


class FakeRunner:
    """Plays git and uv: makes a tag's checkout and writes its results."""

    def __init__(self, *, fail_benchmark: bool = False):
        self.commands: list[list[str]] = []
        self.documents_seen: list[set[str]] = []
        self.fail_benchmark = fail_benchmark

    def __call__(self, command: list[str], **options: Any) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        if command[:3] == ["git", "worktree", "add"]:
            stale = Path(command[4]) / "benchmark" / "documents"
            stale.mkdir(parents=True)
            (stale / "old.toml").write_text("lines = []\n", encoding="utf-8")
        elif command[0] == "uv":
            if self.fail_benchmark:
                raise subprocess.CalledProcessError(1, command)
            assert options["env"]["HF_HUB_OFFLINE"] == "1"
            assert "VIRTUAL_ENV" not in options["env"]
            checkout = Path(options["cwd"])
            self.documents_seen.append(
                {path.name for path in (checkout / "benchmark" / "documents").iterdir()}
            )
            output = Path(command[command.index("--out") + 1])
            output.mkdir(parents=True)
            (output / "results.json").write_text(
                json.dumps({"tool_version": "0.4.0", "totals": {}}), encoding="utf-8"
            )
        return subprocess.CompletedProcess(command, 0)


@pytest.fixture
def documents(tmp_path: Path) -> Path:
    folder = tmp_path / "documents"
    folder.mkdir()
    (folder / "cs-cv.toml").write_text('lines = ["Jan Novák"]\n', encoding="utf-8")
    return folder


def test_each_tag_runs_on_the_current_documents(tmp_path: Path, documents: Path):
    runner = FakeRunner()
    written = backfill(
        ("v0.4.0", "v0.5.0"),
        tmp_path / "out",
        resource_root=tmp_path,
        repository=tmp_path,
        documents=documents,
        runner=runner,
    )
    assert written == [
        (tmp_path / "out" / tag / "results.json").resolve() for tag in ("v0.4.0", "v0.5.0")
    ]
    assert runner.documents_seen == [{"cs-cv.toml"}, {"cs-cv.toml"}]
    results = json.loads(written[0].read_text(encoding="utf-8"))
    assert results["document_set"] == document_set(documents)
    assert "documents_commit" in results["backfill"]
    benchmark = next(command for command in runner.commands if command[0] == "uv")
    assert benchmark[benchmark.index("--systems") + 1] == "rules"
    assert "ner" not in benchmark
    removed = [
        command for command in runner.commands if command[:3] == ["git", "worktree", "remove"]
    ]
    assert len(removed) == 2


def test_a_model_system_brings_the_model_dependencies(tmp_path: Path, documents: Path):
    runner = FakeRunner()
    backfill(
        ("v0.5.0",),
        tmp_path / "out",
        systems=("rules", "rules+gliner"),
        resource_root=tmp_path,
        repository=tmp_path,
        documents=documents,
        runner=runner,
    )
    benchmark = next(command for command in runner.commands if command[0] == "uv")
    assert benchmark[benchmark.index("--group") + 1] == "ner"
    assert benchmark[benchmark.index("--systems") + 1] == "rules,rules+gliner"


def test_a_failed_run_still_removes_the_worktree(tmp_path: Path, documents: Path):
    runner = FakeRunner(fail_benchmark=True)
    with pytest.raises(subprocess.CalledProcessError):
        backfill(
            ("v0.2.0",),
            tmp_path / "out",
            resource_root=tmp_path,
            repository=tmp_path,
            documents=documents,
            runner=runner,
        )
    assert runner.commands[-1][:3] == ["git", "worktree", "remove"]
