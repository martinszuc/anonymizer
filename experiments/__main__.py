"""Command line: `uv run python -m experiments run --config experiments/configs/rq1-dev.toml`.

`train --config experiments/configs/train-<name>.toml` fine-tunes a name
model, lists it under the resource root and scores it on development data
(`experiments.train`; needs `uv sync --group train`).

`leaks scan.pdf --engines onnxtr --system rules+gliner --out leaks/` counts
why the leak check fails on one document (`experiments.leaks`).

`funsd --work outputs/funsd --engines onnxtr,kraken` reads FUNSD's real
scanned forms with each engine and writes counts to `results/funsd-test.*`
(`experiments.funsd`); the work directory receives the scans and stays out of git.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from anonymizer.core.detect import load_name_model, system_model
from anonymizer.core.ingest import load_ocr_engine
from anonymizer.core.pipeline import build_detector
from anonymizer.core.resources import load_catalog, resolve_resource_root

from experiments import phenomena
from experiments.config import load_config
from experiments.datasets import DATASETS, load_corpus
from experiments.funsd import SPLITS, run_funsd, write_results
from experiments.leaks import breakdown, breakdown_markdown, write_breakdown
from experiments.report import latex, markdown
from experiments.run import run
from experiments.train import load_train_config, train, write_training

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
    train_parser = commands.add_parser(
        "train", help="fine-tune a name model and score it on development data"
    )
    train_parser.add_argument(
        "--config", type=Path, required=True, help="training configuration (TOML)"
    )
    train_parser.add_argument(
        "--out", type=Path, default=RESULTS, help=f"results directory (default: {RESULTS})"
    )
    train_parser.add_argument(
        "--cache-dir",
        type=Path,
        help="name model cache (default: <resource root>/.cache/experiments)",
    )
    tables = commands.add_parser("tables", help="rewrite the tables of a stored results file")
    tables.add_argument("results", type=Path, help="<name>.json")
    datasets = commands.add_parser("datasets", help="count documents and gold spans per split")
    leaks = commands.add_parser("leaks", help="count why the leak check fails on one PDF")
    leaks.add_argument("pdf", type=Path, help="document to load, detect, redact and check")
    leaks.add_argument("--out", type=Path, required=True, help="directory for leaks.json and .md")
    leaks.add_argument("--engines", default="onnxtr", help="comma-separated OCR engines")
    leaks.add_argument(
        "--system",
        default="rules+gliner",
        help="rules, or rules+<name model> (default: rules+gliner)",
    )
    leaks.add_argument("--language", default="cs", help="detection language")
    funsd = commands.add_parser("funsd", help="score OCR engines on FUNSD's scanned forms")
    funsd.add_argument(
        "--work", type=Path, required=True, help="directory for scans and redacted copies"
    )
    funsd.add_argument("--engines", required=True, help="comma-separated OCR engines")
    funsd.add_argument(
        "--system",
        default="rules+gliner",
        help="rules, or rules+<name model> (default: rules+gliner)",
    )
    funsd.add_argument("--split", default="test", choices=sorted(SPLITS), help="default: test")
    funsd.add_argument("--limit", type=int, help="score only the first forms")
    funsd.add_argument(
        "--out", type=Path, default=RESULTS, help=f"results directory (default: {RESULTS})"
    )
    for command in (run_parser, train_parser, datasets, leaks, funsd):
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
    if args.command == "leaks":
        return _leaks(args, root)
    if args.command == "funsd":
        return _funsd(args, root)
    if args.command == "train":
        return _train(args, root)
    config = load_config(args.config, load_catalog(root=root))
    cache_dir = args.cache_dir or root / ".cache" / "experiments"
    results = run(config, resource_root=root, cache_dir=cache_dir, progress=print)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"{config.name}.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_tables(results, args.out)
    print(f"wrote {path} and its .md and .tex")
    return 0


def _train(args: argparse.Namespace, root: Path) -> int:
    config = load_train_config(args.config, load_catalog(root=root))
    cache_dir = args.cache_dir or root / ".cache" / "experiments"
    results = train(config, resource_root=root, cache_dir=cache_dir, progress=print)
    path = write_training(results, args.out)
    print(f"stored {config.model} under {root / 'models'}; wrote {path}")
    return 0


def _write_tables(results: dict[str, Any], folder: Path) -> None:
    name = str(results["name"])
    # Recall by name form follows the standard tables, for the corpora that tag their spans.
    forms_md, forms_tex = phenomena.markdown(results), phenomena.latex(results)
    (folder / f"{name}.md").write_text(
        markdown(results) + (f"\n{forms_md}" if forms_md else ""), encoding="utf-8"
    )
    (folder / f"{name}.tex").write_text(
        latex(results) + (f"\n{forms_tex}" if forms_tex else ""), encoding="utf-8"
    )


def _leaks(args: argparse.Namespace, root: Path) -> int:
    model_id = system_model(args.system, load_catalog(root=root))
    model = load_name_model(model_id, root) if model_id is not None else None
    engines = {name: load_ocr_engine(name, root) for name in args.engines.split(",")}
    detector = build_detector(args.language, model=model)
    results = breakdown(args.pdf, engines, detector, args.language)
    write_breakdown(results, args.out)
    print(breakdown_markdown(results))
    return 0


def _funsd(args: argparse.Namespace, root: Path) -> int:
    results = run_funsd(
        args.work,
        engines=tuple(args.engines.split(",")),
        system=args.system,
        split=args.split,
        resource_root=root,
        limit=args.limit,
    )
    path = write_results(results, args.out)
    print(path.with_suffix(".md").read_text(encoding="utf-8"))
    return 0


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
