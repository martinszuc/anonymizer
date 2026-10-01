"""The `detect`, `redact`, `check` and `inspect` commands.

Each command returns an exit code and prints to the given streams; argument
parsing and error reporting live in `main`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from anonymizer.cli import html_report, report
from anonymizer.core.detect import load_gliner_detector
from anonymizer.core.ingest import OcrEngine, load_document, pages_needing_ocr
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import export_redacted, find_leaks
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


def detected(
    source: Path,
    language: str | None,
    *,
    propagate: bool,
    ner_root: Path | None = None,
    ocr: OcrEngine | None = None,
) -> Document:
    """Load a PDF and run the detectors over its pages and surfaces.

    The rules for the language always run; with `ner_root`, so does the name
    model stored under that directory. With `ocr`, scanned pages are read
    through that engine first.
    """
    model = load_gliner_detector(ner_root) if ner_root is not None else None
    document = load_document(source, language=language, ocr=ocr)
    run_detection(document, build_detector(language, model=model), propagate=propagate)
    return document


def run_detect(
    source: Path,
    session: Path,
    *,
    language: str | None,
    propagate: bool,
    ner_root: Path | None,
    show: bool,
    force: bool,
    output: Output,
    ocr: OcrEngine | None = None,
) -> int:
    """Detect personal data and save it as a session file for review."""
    _refuse_existing(session, force=force)
    document = detected(source, language, propagate=propagate, ner_root=ner_root, ocr=ocr)
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
    ner_root: Path | None,
    allow_pages_without_text: bool,
    force: bool,
    output: Output,
    ocr: OcrEngine | None = None,
) -> int:
    """Redact a PDF, and write it only if the leak check passes (`export_redacted`)."""
    if destination.resolve() == source.resolve():
        msg = "the output must not overwrite the input"
        raise CommandError(msg)
    _refuse_existing(destination, force=force)
    document = _reviewed_or_detected(
        source, session, language, propagate=propagate, ner_root=ner_root, ocr=ocr
    )
    _refuse_unreadable_pages(document, allow=allow_pages_without_text, output=output)

    leaks = export_redacted(source, document, destination, ocr=ocr)
    if leaks:
        print(report.leak_report(leaks), file=output.err)
        print(f"nothing written to {destination}", file=output.err)
        return EXIT_LEAKS
    print(f"{source.name}: {report.document_summary(document)}", file=output.out)
    print(report.redaction_summary(document), file=output.out)
    print("leak check passed", file=output.out)
    print(f"wrote {destination}", file=output.out)
    return EXIT_OK


def run_check(
    redacted: Path,
    source: Path,
    session: Path,
    *,
    output: Output,
    ocr: OcrEngine | None = None,
) -> int:
    """Run the leak check on a redacted file against the review it came from.

    A review of scanned pages needs the engine that read them: it reopens the
    review, and the check re-reads the redacted pages with it.
    """
    document = load_session(session, source, ocr=ocr)
    leaks = find_leaks(redacted, document, ocr=ocr)
    if leaks:
        print(report.leak_report(leaks), file=output.err)
        return EXIT_LEAKS
    print("leak check passed", file=output.out)
    return EXIT_OK


def run_inspect(
    source: Path,
    destination: Path,
    *,
    session: Path | None,
    language: str | None,
    propagate: bool,
    ner_root: Path | None,
    dpi: int,
    force: bool,
    output: Output,
    ocr: OcrEngine | None = None,
) -> int:
    """Write an HTML view of the pages with what detection or a review marked."""
    _refuse_existing(destination, force=force)
    document = _reviewed_or_detected(
        source, session, language, propagate=propagate, ner_root=ner_root, ocr=ocr
    )
    destination.write_text(html_report.render_report(source, document, dpi=dpi), encoding="utf-8")
    print(f"{source.name}: {report.document_summary(document)}", file=output.out)
    print(f"wrote {destination} (contains the document's content)", file=output.out)
    return EXIT_OK


def _reviewed_or_detected(
    source: Path,
    session: Path | None,
    language: str | None,
    *,
    propagate: bool,
    ner_root: Path | None,
    ocr: OcrEngine | None,
) -> Document:
    """Load a reviewed session for the source, or detect afresh without one."""
    if session is not None:
        return load_session(session, source, ocr=ocr)
    return detected(source, language, propagate=propagate, ner_root=ner_root, ocr=ocr)


def _refuse_existing(path: Path, *, force: bool) -> None:
    """Refuse to replace an existing file unless asked to."""
    if path.exists() and not force:
        msg = f"{path} already exists; use --force to replace it"
        raise CommandError(msg)


def _refuse_unreadable_pages(document: Document, *, allow: bool, output: Output) -> None:
    """Stop at scanned pages OCR has not read, which cannot be checked.

    Nothing on such a page is detected, so it would reach the output
    unredacted while the leak check still passes.
    """
    pages = [index + 1 for index in pages_needing_ocr(document)]
    if not pages:
        return
    listed = ", ".join(str(page) for page in pages)
    if not allow:
        msg = (
            f"page {listed} is a scan OCR has not read (no text layer, or only a few "
            "words over a picture), so its content would not be redacted. Read it with "
            "--ocr onnxtr, or use --allow-pages-without-text to redact the rest anyway"
        )
        raise CommandError(msg)
    print(f"warning: page {listed} is a scan OCR has not read and is NOT redacted", file=output.err)
