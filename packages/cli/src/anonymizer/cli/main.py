"""Entry point for the `anonymize` command.

Typical use without a review UI:

    anonymize detect cv.pdf -o review.json --show     # find, save for review
    (edit review.json: set "review" to "rejected" to keep an item, add regions)
    anonymize redact cv.pdf -o cv-redacted.pdf --session review.json

or in one step, redacting everything the rules find:

    anonymize redact cv.pdf -o cv-redacted.pdf --lang cs

To see what was found drawn on the pages:

    anonymize inspect cv.pdf -o cv.html [--session review.json]

A photo or a scanned image (JPEG, PNG, TIFF) is accepted wherever a PDF is,
read with OCR, and redacted into a PDF:

    anonymize redact photo.jpg -o photo-redacted.pdf --ocr onnxtr

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
    run_inspect,
    run_redact,
)
from anonymizer.core import __version__
from anonymizer.core.ingest import OCR_ENGINES, load_ocr_engine
from anonymizer.core.log import LEVEL_NAMES, configure_logging, resolve_level
from anonymizer.core.resources import resolve_resource_root


def build_parser() -> argparse.ArgumentParser:
    """Define the command line."""
    parser = argparse.ArgumentParser(
        prog="anonymize",
        description="Detect and redact personal data in PDF documents and images, offline.",
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    logging_options = _logging_options()

    detect = commands.add_parser(
        "detect", parents=[logging_options], help="find personal data and save it for review"
    )
    detect.add_argument("input", type=Path, help="PDF or image (JPEG, PNG, TIFF) to scan")
    detect.add_argument("-o", "--output", type=Path, required=True, help="session file to write")
    _add_detection_options(detect)
    detect.add_argument("--show", action="store_true", help="list every item found")
    detect.add_argument("--force", action="store_true", help="replace an existing session file")

    redact = commands.add_parser(
        "redact", parents=[logging_options], help="write a redacted copy of a PDF or an image"
    )
    redact.add_argument("input", type=Path, help="PDF or image (JPEG, PNG, TIFF) to redact")
    redact.add_argument(
        "-o", "--output", type=Path, required=True, help="redacted PDF to write (also for an image)"
    )
    redact.add_argument(
        "--session",
        type=Path,
        help="apply a reviewed session file instead of detecting again",
    )
    _add_detection_options(redact)
    redact.add_argument(
        "--allow-pages-without-text",
        action="store_true",
        help="redact even if some scanned pages were not read by OCR (they are left unredacted)",
    )
    redact.add_argument("--force", action="store_true", help="replace an existing output file")

    check = commands.add_parser(
        "check", parents=[logging_options], help="run the leak check on a redacted PDF"
    )
    check.add_argument("redacted", type=Path, help="redacted PDF to check")
    check.add_argument("--source", type=Path, required=True, help="the original PDF or image")
    check.add_argument("--session", type=Path, required=True, help="the review it came from")
    _add_ocr_options(check)

    inspect = commands.add_parser(
        "inspect",
        parents=[logging_options],
        help="write an HTML view of the pages with what was found drawn on them",
    )
    inspect.add_argument("input", type=Path, help="PDF or image (JPEG, PNG, TIFF) to show")
    inspect.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="HTML file to write; it contains the document's content",
    )
    inspect.add_argument(
        "--session",
        type=Path,
        help="show a reviewed session file instead of detecting again",
    )
    _add_detection_options(inspect)
    inspect.add_argument(
        "--dpi", type=int, default=110, help="resolution of the page images (default 110)"
    )
    inspect.add_argument("--force", action="store_true", help="replace an existing output file")
    return parser


def _logging_options() -> argparse.ArgumentParser:
    """Options every command takes; logs go to stderr, the command's own output to stdout."""
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument(
        "--debug",
        action="store_true",
        help="log every step and every detection (the log holds document text)",
    )
    options.add_argument(
        "--log-level",
        choices=LEVEL_NAMES,
        help="how much to log to stderr (default: warning; the ANONYMIZER_LOG_LEVEL variable "
        "also sets it, and --debug means debug)",
    )
    options.add_argument(
        "--log-file",
        type=Path,
        metavar="PATH",
        help="also append the log to this file; nothing is written to a file without it",
    )
    return options


def _add_detection_options(parser: argparse.ArgumentParser) -> None:
    """Options shared by every command that runs detection."""
    parser.add_argument(
        "--lang",
        help=(
            "document language, e.g. cs, sk or en, or auto to recognise it from the text; "
            "every rule runs when omitted"
        ),
    )
    parser.add_argument(
        "--no-propagate",
        dest="propagate",
        action="store_false",
        help="do not mark further occurrences of found text",
    )
    parser.add_argument(
        "--ner",
        action="store_true",
        help="also detect names and addresses with the GLiNER model (install with "
        "uv sync --group ner, fetch with scripts/download.py)",
    )
    _add_ocr_options(parser)


def _add_ocr_options(parser: argparse.ArgumentParser) -> None:
    """Options for reading scanned pages, and where the models are stored."""
    parser.add_argument(
        "--ocr",
        choices=sorted(OCR_ENGINES),
        help="read scanned pages and images with this OCR engine (install with uv sync "
        "--group ocr-<engine>, fetch its models with scripts/download.py); an image needs it",
    )
    parser.add_argument(
        "--resource-root",
        type=Path,
        help="directory holding models/ (default: the folder chosen in the review window, "
        "else ./models if it exists, else a per-user folder)",
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
        args.resource_root = resolve_resource_root(args.resource_root)
    except SystemExit as exit_request:
        # argparse exits for --help, --version and invalid arguments.
        return exit_request.code if isinstance(exit_request.code, int) else EXIT_ERROR
    output = Output(out=sys.stdout, err=sys.stderr)
    try:
        configure_logging(resolve_level(args.log_level, debug=args.debug), file=args.log_file)
        return _dispatch(args, output)
    except (
        CommandError,
        ValueError,
        FileNotFoundError,
        ImportError,
        pymupdf.FileDataError,
    ) as error:
        print(f"anonymize: error: {error}", file=output.err)
        return EXIT_ERROR


def _dispatch(args: argparse.Namespace, output: Output) -> int:
    """Run the command the arguments name."""
    ocr = load_ocr_engine(args.ocr, args.resource_root) if args.ocr else None
    ner_root = args.resource_root if getattr(args, "ner", False) else None
    if args.command == "detect":
        return run_detect(
            args.input,
            args.output,
            language=args.lang,
            propagate=args.propagate,
            ner_root=ner_root,
            show=args.show,
            force=args.force,
            output=output,
            ocr=ocr,
        )
    if args.command == "redact":
        return run_redact(
            args.input,
            args.output,
            session=args.session,
            language=args.lang,
            propagate=args.propagate,
            ner_root=ner_root,
            allow_pages_without_text=args.allow_pages_without_text,
            force=args.force,
            output=output,
            ocr=ocr,
        )
    if args.command == "inspect":
        return run_inspect(
            args.input,
            args.output,
            session=args.session,
            language=args.lang,
            propagate=args.propagate,
            ner_root=ner_root,
            dpi=args.dpi,
            force=args.force,
            output=output,
            ocr=ocr,
        )
    return run_check(args.redacted, args.source, args.session, output=output, ocr=ocr)


if __name__ == "__main__":
    raise SystemExit(main())
