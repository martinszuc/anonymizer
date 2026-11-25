"""Command line: `uv run python -m benchmark run --out results/` (or another command).

The commands: `run`, `leaks`, `ocr`, `ocr-margin`, `ocr-probe`, `photos`, `history`,
`diff`, `backfill`, `photo-train`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from anonymizer.core.detect import system_model
from anonymizer.core.resources import load_catalog, resolve_resource_root

from benchmark.backfill import backfill
from benchmark.degrade import LEVELS, level_named
from benchmark.diff import diff_markdown
from benchmark.leaks import run_leaks
from benchmark.ocr_margin import MARGINS, margins_markdown, run_margins
from benchmark.ocr_probe import probe, probe_markdown, write_probe
from benchmark.ocr_run import ENGINES, ocr_markdown, run_ocr
from benchmark.photo_files import (
    CONDITIONS,
    PhotoSetError,
    apply_renames,
    plan_set,
    read_manifest,
)
from benchmark.photo_run import photos_markdown, score_photos
from benchmark.photo_train import SPLITS, render_split
from benchmark.report import markdown
from benchmark.run import SYSTEMS, run
from benchmark.spec import DOCUMENTS


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark command line; return the exit code."""
    parser = argparse.ArgumentParser(prog="benchmark", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", help="score every system on every document")
    run_parser.add_argument("--out", type=Path, required=True, help="directory for results")
    run_parser.add_argument(
        "--systems",
        default=",".join(SYSTEMS),
        help=f"comma-separated systems, rules or rules+<name model> (default: {','.join(SYSTEMS)})",
    )
    _add_resource_root(run_parser)
    leaks_parser = commands.add_parser(
        "leaks", help="compare redaction methods by what they leave extractable"
    )
    leaks_parser.add_argument("--out", type=Path, required=True, help="directory for results")
    leaks_parser.add_argument(
        "--documents", default="", help="comma-separated document names (default: all)"
    )
    ocr_parser = commands.add_parser("ocr", help="score OCR engines on degraded scans")
    ocr_parser.add_argument("--out", type=Path, required=True, help="directory for results")
    ocr_parser.add_argument(
        "--engines", default="oracle", help=f"comma-separated, from {','.join(ENGINES)}"
    )
    ocr_parser.add_argument(
        "--levels",
        default=",".join(level.name for level in LEVELS),
        help="comma-separated degradation levels (default: all)",
    )
    ocr_parser.add_argument("--system", default="rules", help="detector system (default: rules)")
    _add_resource_root(ocr_parser)
    margin_parser = commands.add_parser(
        "ocr-margin", help="measure how far OCR boxes must grow to cover their words"
    )
    margin_parser.add_argument("--out", type=Path, required=True, help="directory for results")
    margin_parser.add_argument(
        "--engines", required=True, help=f"comma-separated, from {','.join(ENGINES)}"
    )
    margin_parser.add_argument(
        "--levels", default="clean", help="comma-separated degradation levels (default: clean)"
    )
    margin_parser.add_argument(
        "--margins",
        default=",".join(str(margin) for margin in MARGINS),
        help="comma-separated shares of a box's height (default: %(default)s)",
    )
    _add_resource_root(margin_parser)
    probe_parser = commands.add_parser(
        "ocr-probe", help="read one PDF with OCR engines and report counts only"
    )
    probe_parser.add_argument("pdf", type=Path, help="the PDF to read")
    probe_parser.add_argument("--out", type=Path, required=True, help="directory for results")
    probe_parser.add_argument("--engines", required=True, help="comma-separated OCR engines")
    probe_parser.add_argument("--lang", default="cs", help="detection language (default: cs)")
    probe_parser.add_argument("--system", default="rules", help="detector system (default: rules)")
    probe_parser.add_argument(
        "--truth", type=Path, help="JSON list of each page's expected text, null to skip a page"
    )
    _add_resource_root(probe_parser)
    _add_photos(commands)
    history_parser = commands.add_parser("history", help="draw charts from several runs")
    history_parser.add_argument("results", type=Path, nargs="+", help="results.json files")
    history_parser.add_argument("--out", type=Path, required=True, help="directory for charts")
    diff_parser = commands.add_parser(
        "diff", help="compare a run with a baseline per item type, as Markdown"
    )
    diff_parser.add_argument("baseline", type=Path, help="results.json to compare against")
    diff_parser.add_argument("current", type=Path, help="results.json of this run")
    backfill_parser = commands.add_parser(
        "backfill", help="run earlier tags' code on the current documents"
    )
    backfill_parser.add_argument("tags", nargs="+", help="git tags, e.g. v0.4.0 v0.5.0")
    backfill_parser.add_argument("--out", type=Path, required=True, help="writes <out>/<tag>/")
    backfill_parser.add_argument(
        "--systems", default="rules", help="comma-separated systems (default: rules)"
    )
    _add_resource_root(backfill_parser)
    photo_parser = commands.add_parser(
        "photo-train", help="render the invented documents for the phone-photo fine-tune"
    )
    photo_parser.add_argument("--out", type=Path, required=True, help="directory for the PDFs")
    photo_parser.add_argument(
        "--split", choices=SPLITS, default="print", help="print (fixed) or synthetic"
    )
    photo_parser.add_argument(
        "--count", type=int, default=0, help="synthetic documents per language"
    )
    photo_parser.add_argument("--seed", help="seed of the synthetic split")
    args = parser.parse_args(argv)
    if args.command == "photos":
        return _photos(parser, args)
    if args.command not in ("history", "diff", "leaks", "photo-train"):
        args.resource_root = resolve_resource_root(args.resource_root)
        _check_system(parser, args)

    if args.command == "history":
        from benchmark.history import draw

        for chart in draw(args.results, args.out):
            print(f"wrote {chart}")
        return 0
    if args.command == "diff":
        print(diff_markdown(_read_json(args.baseline), _read_json(args.current)), end="")
        return 0
    if args.command == "photo-train":
        try:
            gold = render_split(args.out, split=args.split, count=args.count, seed=args.seed)
        except ValueError as error:
            parser.error(str(error))
        print(f"wrote {gold}")
        return 0
    if args.command == "leaks":
        run_leaks(args.out, names=_names(args.documents))
        print((args.out / "leaks.md").read_text(encoding="utf-8"), end="")
        return 0
    if args.command == "backfill":
        for path in backfill(
            tuple(args.tags),
            args.out,
            systems=_names(args.systems),
            resource_root=args.resource_root,
        ):
            print(f"wrote {path}")
        return 0
    if args.command == "ocr":
        ocr_results = run_ocr(
            args.out,
            engines=_names(args.engines),
            levels=tuple(level_named(name) for name in _names(args.levels)),
            system=args.system,
            resource_root=args.resource_root,
        )
        ocr_report = ocr_markdown(ocr_results)
        (args.out / "ocr-results.md").write_text(ocr_report, encoding="utf-8")
        print(ocr_report)
        return 0
    if args.command == "ocr-probe":
        truth = json.loads(args.truth.read_text(encoding="utf-8")) if args.truth else None
        probe_results = probe(
            args.pdf,
            engines=_names(args.engines),
            language=args.lang,
            system=args.system,
            truth=truth,
            resource_root=args.resource_root,
        )
        write_probe(probe_results, args.out)
        print(probe_markdown(probe_results))
        return 0
    if args.command == "ocr-margin":
        margin_results = run_margins(
            args.out,
            engines=_names(args.engines),
            levels=tuple(level_named(name) for name in _names(args.levels)),
            margins=tuple(float(margin) for margin in _names(args.margins)),
            resource_root=args.resource_root,
        )
        margin_report = margins_markdown(margin_results)
        (args.out / "ocr-margins.md").write_text(margin_report, encoding="utf-8")
        print(margin_report)
        return 0
    results = run(
        args.out,
        systems=_names(args.systems),
        resource_root=args.resource_root,
    )
    report = markdown(results)
    (args.out / "results.md").write_text(report, encoding="utf-8")
    print(report)
    return 0


def _add_photos(commands: Any) -> None:
    photos_parser = commands.add_parser(
        "photos", help="phone photos of printed documents (experiments/photo-rules.md)"
    )
    actions = photos_parser.add_subparsers(dest="action", required=True)
    rename_parser = actions.add_parser(
        "rename", help="name each photo by capture time and the manifest's print order"
    )
    _add_photo_set(rename_parser)
    rename_parser.add_argument(
        "--dry-run", action="store_true", help="print the planned names, rename nothing"
    )
    score_parser = actions.add_parser(
        "score", help="read, detect, redact and score every photo, and the born-digital text"
    )
    _add_photo_set(score_parser)
    score_parser.add_argument("--out", type=Path, required=True, help="directory for results")
    score_parser.add_argument(
        "--run", help="name the results photos-<run>.json and .md (default: photos.json)"
    )
    score_parser.add_argument(
        "--set", default="test", help="which photo set: test or train (default: %(default)s)"
    )
    score_parser.add_argument(
        "--documents",
        type=Path,
        default=DOCUMENTS,
        help="directory of the documents' files (default: the benchmark's)",
    )
    score_parser.add_argument(
        "--engines", default="onnxtr", help="comma-separated OCR engines (default: %(default)s)"
    )
    score_parser.add_argument(
        "--systems", default="rules", help="comma-separated systems, as for run"
    )
    score_parser.add_argument(
        "--compare",
        default="",
        help="comma-separated baseline:candidate pairs of systems to compare",
    )
    score_parser.add_argument(
        "--primary", help="baseline:candidate, the comparison the rules give one sentence"
    )
    score_parser.add_argument(
        "--redacted", type=Path, help="keep the redacted copies here (default: discarded)"
    )
    _add_resource_root(score_parser)


def _add_photo_set(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--photos",
        type=Path,
        default=Path("outputs/rq8-photos/photos"),
        help="folder holding one folder per condition (default: %(default)s)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("outputs/rq8-photos/print/manifest.md"),
        help="print order, a table | # | document | pages | (default: %(default)s)",
    )
    parser.add_argument(
        "--conditions",
        default=",".join(CONDITIONS),
        help="comma-separated condition folders (default: %(default)s)",
    )


def _photos(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    """Run `photos rename` or `photos score`; a refused photo set prints why and exits with 1."""
    if args.action == "score":
        return _score_photos(parser, args)
    try:
        manifest = read_manifest(args.manifest)
        plans = plan_set(args.photos, manifest, _names(args.conditions))
    except (PhotoSetError, OSError) as error:
        print(f"refused, nothing renamed:\n{error}", file=sys.stderr)
        return 1
    for condition, plan in plans.items():
        for rename in plan:
            mark = "=" if rename.source == rename.target else "->"
            names = f"{rename.source.name} {mark} {rename.target.name}"
            print(f"{condition}: {names}  ({rename.captured})")
    if args.dry_run:
        print("dry run: nothing renamed")
        return 0
    moved = sum(apply_renames(plan) for plan in plans.values())
    print(f"renamed {moved} photos")
    return 0


def _score_photos(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    resource_root = resolve_resource_root(args.resource_root)
    systems = _names(args.systems)
    catalog = load_catalog(root=resource_root)
    try:
        for system in systems:
            system_model(system, catalog)
    except ValueError as error:
        parser.error(str(error))
    try:
        results = score_photos(
            args.photos,
            args.manifest,
            args.out,
            documents=args.documents,
            conditions=_names(args.conditions),
            engines=_names(args.engines),
            systems=systems,
            compare=tuple(_pair(parser, pair) for pair in _names(args.compare)),
            primary=_pair(parser, args.primary) if args.primary else None,
            resource_root=resource_root,
            set_name=args.set,
            run_name=args.run,
            redacted=args.redacted,
        )
    except (ValueError, OSError) as error:
        print(f"refused, nothing scored:\n{error}", file=sys.stderr)
        return 1
    print(photos_markdown(results), end="")
    return 0


def _pair(parser: argparse.ArgumentParser, listed: str) -> tuple[str, str]:
    baseline, colon, candidate = listed.partition(":")
    if not colon or not baseline or not candidate:
        parser.error(f"expected baseline:candidate, got {listed!r}")
    return baseline, candidate


def _check_system(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Refuse an unknown `--system`; the models trained under the resource root count too."""
    if not hasattr(args, "system"):
        return
    try:
        system_model(args.system, load_catalog(root=args.resource_root))
    except ValueError as error:
        parser.error(str(error))


def _add_resource_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--resource-root",
        type=Path,
        help="directory holding models/ (default: as for the CLI's --resource-root)",
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _names(listed: str) -> tuple[str, ...]:
    return tuple(name.strip() for name in listed.split(",") if name.strip())


if __name__ == "__main__":
    sys.exit(main())
