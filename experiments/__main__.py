"""Command line: `uv run python -m experiments run --config experiments/configs/rq1-dev.toml`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from anonymizer.core.resources import resolve_resource_root

from experiments.config import load_config
from experiments.datasets import DATASETS, load_corpus
from experiments.report import latex, markdown
from experiments.run import run

RESULTS = Path(__file__).parent / "results"


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(prog="experiments", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", help="score the configured systems")
    run_parser.add_argument("--config", type=Path, required=True, help="run configuration (TOML)")
    run_parser.add_argument(
        "--out", type=Path, default=RESULTS, help=f"results directory (default: {RESULTS})"
    )
    run_parser.add_argument(
        "--cache-dir",
        type=Path,
        help="name model cache (default: <resource root>/.cache/experiments)",
    )
    tables = commands.add_parser("tables", help="rewrite the tables of a stored results file")
    tables.add_argument("results", type=Path, help="<name>.json")
    datasets = commands.add_parser("datasets", help="count documents and gold spans per split")
    for command in (run_parser, datasets):
        command.add_argument(
            "--resource-root",
            type=Path,
            help="directory holding data/ and models/ (default: as for the CLI)",
        )
    args = parser.parse_args(argv)

    if args.command == "tables":
        results = json.loads(args.results.read_text(encoding="utf-8"))
        _write_tables(results, args.results.parent)
        return 0
    root = resolve_resource_root(args.resource_root)
    if args.command == "datasets":
        return _count(root)
    config = load_config(args.config)
    cache_dir = args.cache_dir or root / ".cache" / "experiments"
    results = run(config, resource_root=root, cache_dir=cache_dir, progress=print)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"{config.name}.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_tables(results, args.out)
    print(f"wrote {path} and its .md and .tex")
    return 0


def _write_tables(results: dict[str, Any], folder: Path) -> None:
    name = str(results["name"])
    (folder / f"{name}.md").write_text(markdown(results), encoding="utf-8")
    (folder / f"{name}.tex").write_text(latex(results), encoding="utf-8")


def _count(root: Path) -> int:
    """Print documents and gold spans per split; counts only, never text."""
    for dataset, spec in DATASETS.items():
        for split, role in spec.splits.items():
            try:
                corpus = load_corpus(dataset, split, root)
            except FileNotFoundError:
                print(f"{dataset}/{split}: not stored under {root}")
                continue
            gold = ", ".join(f"{kind} {count}" for kind, count in corpus.gold_counts().items())
            print(
                f"{corpus.key} ({role}, {corpus.language}): {len(corpus.documents)} documents, "
                f"{corpus.sentences} sentences or records; gold {gold}; "
                f"skipped {corpus.skipped}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
