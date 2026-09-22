"""The `detect`, `redact` and `check` commands.

Each command returns an exit code and prints to the given streams; argument
parsing and error reporting live in `main`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from anonymizer.cli import report
from anonymizer.core.detect import detect_document, detector_for, propagate_occurrences
from anonymizer.core.ingest import load_document, pages_needing_ocr
from anonymizer.core.redact import find_leaks, redact_pdf
from anonymizer.core.session import load_session, save_session
from anonymizer.core.types import Document

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_LEAKS = 3


class CommandError(Exception):
    """A problem with the user's input, reported without a traceback."""


@dataclass(frozen=True)
class Output:
    """Where a command writes its messages."""

    out: TextIO
    err: TextIO


def detected(source: Path, language: str | None, *, propagate: bool) -> Document:
    """Load a PDF and run the rules for its language over pages and surfaces."""
    document = load_document(source, language=language)
    document.entities = detect_document(detector_for(language), document)
    if propagate:
        document.entities += propagate_occurrences(document)
    return document


def run_detect(
    source: Path,
    session: Path,
    *,
    language: str | None,
    propagate: bool,
    show: bool,
    force: bool,
    output: Output,
) -> int:
    """Detect personal data and save it as a session file for review."""
    _refuse_existing(session, force=force)
    document = detected(source, language, propagate=propagate)
    save_session(document, session)
    print(f"{source.name}: {report.document_summary(document)}", file=output.out)
    if show:
        print(report.entity_table(document), file=output.out)
    print(f"wrote review {session}", file=output.out)
    return EXIT_OK


def run_redact(
    source: Path,
    destination: Path,
    *,
    session: Path | None,
    language: str | None,
    propagate: bool,
    allow_pages_without_text: bool,
    force: bool,
    output: Output,
) -> int:
    """Redact a PDF, and write it only if the leak check passes.

    The copy is written under a temporary name next to the destination and
    renamed only after the check, so a file that failed it never appears
    under the name the user asked for.
    """
    if destination.resolve() == source.resolve():
        msg = "the output must not overwrite the input"
        raise CommandError(msg)
    _refuse_existing(destination, force=force)
    if session is not None:
        document = load_session(session, source)
    else:
        document = detected(source, language, propagate=propagate)
    _refuse_unreadable_pages(document, allow=allow_pages_without_text, output=output)

    partial = destination.with_name(f".{destination.name}.partial")
    try:
        redact_pdf(source, document, partial)
        leaks = find_leaks(partial, document)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    if leaks:
        partial.unlink()
        print(report.leak_report(leaks), file=output.err)
        print(f"nothing written to {destination}", file=output.err)
        return EXIT_LEAKS
    partial.replace(destination)
    print(f"{source.name}: {report.document_summary(document)}", file=output.out)
    print(report.redaction_summary(document), file=output.out)
    print("leak check passed", file=output.out)
    print(f"wrote {destination}", file=output.out)
    return EXIT_OK


def run_check(redacted: Path, source: Path, session: Path, *, output: Output) -> int:
    """Run the leak check on a redacted file against the review it came from."""
    document = load_session(session, source)
    leaks = find_leaks(redacted, document)
    if leaks:
        print(report.leak_report(leaks), file=output.err)
        return EXIT_LEAKS
    print("leak check passed", file=output.out)
    return EXIT_OK


def _refuse_existing(path: Path, *, force: bool) -> None:
    """Refuse to replace an existing file unless asked to."""
    if path.exists() and not force:
        msg = f"{path} already exists; use --force to replace it"
        raise CommandError(msg)


def _refuse_unreadable_pages(document: Document, *, allow: bool, output: Output) -> None:
    """Stop at pages without a text layer, which cannot be checked yet.

    Such a page is usually a scan. Without OCR nothing on it is detected, so it
    would reach the output unredacted while the leak check still passes.
    """
    pages = [index + 1 for index in pages_needing_ocr(document)]
    if not pages:
        return
    listed = ", ".join(str(page) for page in pages)
    if not allow:
        msg = (
            f"page {listed} has no text layer (a scan?); OCR is not supported yet, so "
            "its content would not be redacted. Use --allow-pages-without-text to "
            "redact the rest anyway"
        )
        raise CommandError(msg)
    print(f"warning: page {listed} has no text layer and is NOT redacted", file=output.err)
