"""Measuring earlier releases on the current benchmark documents.

The results attached to each release were measured on that release's own
documents, so the history charts cannot tell a code change from a document
change across them. Backfilling runs each tag's own code (pipeline and
harness) on the current files:

1. `git worktree add --detach` the tag into a temporary directory;
2. replace its `benchmark/documents` with the current ones;
3. `uv run --locked --all-packages python -m benchmark run` there, writing
   `<out>/<tag>/results.json`;
4. record the current set's fingerprint in that file (older code does not)
   and remove the worktree.

An older harness reads only the carriers it knew, so it may score fewer
planted items than the current one; the history charts keep such runs apart.
The release assets on GitHub are left as they are.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from benchmark.run import git_commit
from benchmark.spec import DOCUMENTS, document_set

REPOSITORY = Path(__file__).resolve().parent.parent

Runner = Callable[..., subprocess.CompletedProcess[Any]]


def backfill(
    tags: tuple[str, ...],
    output: Path,
    *,
    systems: tuple[str, ...] = ("rules",),
    resource_root: Path,
    repository: Path = REPOSITORY,
    documents: Path = DOCUMENTS,
    runner: Runner = subprocess.run,
) -> list[Path]:
    """Run each tag's benchmark on the current documents.

    Args:
        tags: Git tags to measure, each a release with a `benchmark` package.
        output: Directory; each tag's run goes to `<output>/<tag>/`.
        systems: Systems to run (`rules` needs no model).
        resource_root: Storage root holding `models/`, passed to every tag.
        repository: The git checkout the tags belong to.
        documents: The document files to measure on.
        runner: Runs a command; replaced in tests.

    Returns:
        The `results.json` files written, one per tag.

    Raises:
        subprocess.CalledProcessError: If git or a tag's benchmark fails.
    """
    identity = document_set(documents)
    written = []
    with tempfile.TemporaryDirectory(prefix="benchmark-backfill-") as scratch:
        for tag in tags:
            checkout = Path(scratch) / tag
            destination = (output / tag).resolve()
            runner(
                ["git", "worktree", "add", "--detach", str(checkout), tag],
                cwd=repository,
                check=True,
            )
            try:
                _replace_documents(checkout / "benchmark" / "documents", documents)
                runner(
                    _benchmark_command(destination, systems, resource_root),
                    cwd=checkout,
                    env=_environment(),
                    check=True,
                )
            finally:
                runner(
                    ["git", "worktree", "remove", "--force", str(checkout)],
                    cwd=repository,
                    check=True,
                )
            written.append(stamp(destination / "results.json", identity))
    return written


def stamp(path: Path, identity: dict[str, Any]) -> Path:
    """Record the document set and the documents' commit in a results file."""
    results = json.loads(path.read_text(encoding="utf-8"))
    results["document_set"] = identity
    results["backfill"] = {"documents_commit": git_commit()}
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _replace_documents(target: Path, documents: Path) -> None:
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(documents, target)


def _benchmark_command(
    destination: Path, systems: tuple[str, ...], resource_root: Path
) -> list[str]:
    # Every tag since v0.2.0 takes these options.
    model = ["--group", "ner"] if any(system != "rules" for system in systems) else []
    return [
        "uv",
        "run",
        "--locked",
        "--all-packages",
        *model,
        "python",
        "-m",
        "benchmark",
        "run",
        "--out",
        str(destination),
        "--systems",
        ",".join(systems),
        "--resource-root",
        str(resource_root.resolve()),
    ]


def _environment() -> dict[str, str]:
    """Run offline, in the tag's own environment rather than this one."""
    environment = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    return {**environment, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
