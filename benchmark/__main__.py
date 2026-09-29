"""Command line: `uv run python -m benchmark run --out results/`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
    history_parser = commands.add_parser("history", help="draw charts from several runs")
    history_parser.add_argument("results", type=Path, nargs="+", help="results.json files")
    history_parser.add_argument("--out", type=Path, required=True, help="directory for charts")
    args = parser.parse_args(argv)

    if args.command == "history":
        from benchmark.history import draw

        for chart in draw(args.results, args.out):
            print(f"wrote {chart}")
        return 0
    results = run(
        args.out,
        systems=tuple(system.strip() for system in args.systems.split(",") if system.strip()),
        resource_root=args.resource_root,
    )
    report = markdown(results)
    (args.out / "results.md").write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
