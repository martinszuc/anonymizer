"""Command line: `uv run python -m benchmark run --out results/` (or `ocr`, `history`)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from benchmark.degrade import LEVELS, level_named
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
        "--resource-root", type=Path, default=Path(), help="directory holding models/"
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
        "--resource-root", type=Path, default=Path(), help="directory holding models/"
    )
    history_parser = commands.add_parser("history", help="draw charts from several runs")
    history_parser.add_argument("results", type=Path, nargs="+", help="results.json files")
    history_parser.add_argument("--out", type=Path, required=True, help="directory for charts")
    args = parser.parse_args(argv)

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
