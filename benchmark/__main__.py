"""Command line: `uv run python -m benchmark run --out results/` (or another command).

The commands: `run`, `ocr`, `ocr-margin`, `ocr-probe`, `history`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from anonymizer.core.resources import resolve_resource_root

from benchmark.degrade import LEVELS, level_named
from benchmark.ocr_margin import MARGINS, margins_markdown, run_margins
from benchmark.ocr_probe import probe, probe_markdown, write_probe
from benchmark.ocr_run import ENGINES, ocr_markdown, run_ocr
from benchmark.report import markdown
from benchmark.run import SYSTEMS, run


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark command line; return the exit code."""
    parser = argparse.ArgumentParser(prog="benchmark", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", help="score every system on every document")
    run_parser.add_argument("--out", type=Path, required=True, help="directory for results")
    run_parser.add_argument(
        "--systems",
        default=",".join(SYSTEMS),
        help=f"comma-separated systems (default: {','.join(SYSTEMS)})",
    )
    run_parser.add_argument(
        "--resource-root",
        type=Path,
        help="directory holding models/ (default: as for the CLI's --resource-root)",
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
    ocr_parser.add_argument(
        "--system", default="rules", choices=SYSTEMS, help="detector system (default: rules)"
    )
    ocr_parser.add_argument(
        "--resource-root",
        type=Path,
        help="directory holding models/ (default: as for the CLI's --resource-root)",
    )
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
    margin_parser.add_argument(
        "--resource-root",
        type=Path,
        help="directory holding models/ (default: as for the CLI's --resource-root)",
    )
    probe_parser = commands.add_parser(
        "ocr-probe", help="read one PDF with OCR engines and report counts only"
    )
    probe_parser.add_argument("pdf", type=Path, help="the PDF to read")
    probe_parser.add_argument("--out", type=Path, required=True, help="directory for results")
    probe_parser.add_argument("--engines", required=True, help="comma-separated OCR engines")
    probe_parser.add_argument("--lang", default="cs", help="detection language (default: cs)")
    probe_parser.add_argument(
        "--system", default="rules", choices=SYSTEMS, help="detector system (default: rules)"
    )
    probe_parser.add_argument(
        "--truth", type=Path, help="JSON list of each page's expected text, null to skip a page"
    )
    probe_parser.add_argument(
        "--resource-root",
        type=Path,
        help="directory holding models/ (default: as for the CLI's --resource-root)",
    )
    history_parser = commands.add_parser("history", help="draw charts from several runs")
    history_parser.add_argument("results", type=Path, nargs="+", help="results.json files")
    history_parser.add_argument("--out", type=Path, required=True, help="directory for charts")
    args = parser.parse_args(argv)
    if args.command != "history":
        args.resource_root = resolve_resource_root(args.resource_root)

    if args.command == "history":
        from benchmark.history import draw

        for chart in draw(args.results, args.out):
            print(f"wrote {chart}")
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


def _names(listed: str) -> tuple[str, ...]:
    return tuple(name.strip() for name in listed.split(",") if name.strip())


if __name__ == "__main__":
    sys.exit(main())
