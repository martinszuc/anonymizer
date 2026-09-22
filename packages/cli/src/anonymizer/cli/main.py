"""Entry point for the `anonymize` command.

Typical use without a review UI:

    anonymize detect cv.pdf -o review.json --show     # find, save for review
    (edit review.json: set "review" to "rejected" to keep an item, add regions)
    anonymize redact cv.pdf -o cv-redacted.pdf --session review.json

or in one step, redacting everything the rules find:

    anonymize redact cv.pdf -o cv-redacted.pdf --lang cs

Exit codes: 0 success, 1 error, 2 invalid arguments, 3 leak check failed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pymupdf
from anonymizer.cli.commands import (
    EXIT_ERROR,
    CommandError,
    Output,
    run_check,
    run_detect,
    run_redact,
)
from anonymizer.core import __version__


def build_parser() -> argparse.ArgumentParser:
    """Define the command line."""
    parser = argparse.ArgumentParser(
        prog="anonymize",
        description="Detect and redact personal data in PDF documents, offline.",
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    detect = commands.add_parser("detect", help="find personal data and save it for review")
    detect.add_argument("input", type=Path, help="PDF to scan")
    detect.add_argument("-o", "--output", type=Path, required=True, help="session file to write")
    _add_detection_options(detect)
    detect.add_argument("--show", action="store_true", help="list every item found")
    detect.add_argument("--force", action="store_true", help="replace an existing session file")

    redact = commands.add_parser("redact", help="write a redacted copy of a PDF")
    redact.add_argument("input", type=Path, help="PDF to redact")
    redact.add_argument("-o", "--output", type=Path, required=True, help="redacted PDF to write")
    redact.add_argument(
        "--session",
        type=Path,
        help="apply a reviewed session file instead of detecting again",
    )
    _add_detection_options(redact)
    redact.add_argument(
        "--allow-pages-without-text",
        action="store_true",
        help="redact even if some pages have no text layer (they are left unredacted)",
    )
    redact.add_argument("--force", action="store_true", help="replace an existing output file")

    check = commands.add_parser("check", help="run the leak check on a redacted PDF")
    check.add_argument("redacted", type=Path, help="redacted PDF to check")
    check.add_argument("--source", type=Path, required=True, help="the original PDF")
    check.add_argument("--session", type=Path, required=True, help="the review it came from")
    return parser


def _add_detection_options(parser: argparse.ArgumentParser) -> None:
    """Options shared by every command that runs detection."""
    parser.add_argument(
        "--lang",
        help="document language, e.g. cs, sk or en; every rule runs when omitted",
    )
    parser.add_argument(
        "--no-propagate",
        dest="propagate",
        action="store_false",
        help="do not mark further occurrences of found text",
    )


def main(argv: list[str] | None = None) -> int:
    """Run the command-line client.

    Args:
        argv: Argument list to parse. Defaults to `sys.argv[1:]`.

    Returns:
        Process exit code.
    """
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exit_request:
        # argparse exits for --help, --version and invalid arguments.
        return exit_request.code if isinstance(exit_request.code, int) else EXIT_ERROR
    output = Output(out=sys.stdout, err=sys.stderr)
    try:
        return _dispatch(args, output)
    except (CommandError, ValueError, FileNotFoundError, pymupdf.FileDataError) as error:
        print(f"anonymize: error: {error}", file=output.err)
        return EXIT_ERROR


def _dispatch(args: argparse.Namespace, output: Output) -> int:
    """Run the command the arguments name."""
    if args.command == "detect":
        return run_detect(
            args.input,
            args.output,
            language=args.lang,
            propagate=args.propagate,
            show=args.show,
            force=args.force,
            output=output,
        )
    if args.command == "redact":
        return run_redact(
            args.input,
            args.output,
            session=args.session,
            language=args.lang,
            propagate=args.propagate,
            allow_pages_without_text=args.allow_pages_without_text,
            force=args.force,
            output=output,
        )
    return run_check(args.redacted, args.source, args.session, output=output)


if __name__ == "__main__":
    raise SystemExit(main())
