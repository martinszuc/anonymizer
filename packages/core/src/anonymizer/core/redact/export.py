"""Writing a redacted copy that exists only if it passed the leak check.

The copy is written under a temporary name next to the destination, checked,
and renamed only when no leak was found, so a file that failed the check never
appears under the name the user asked for. The CLI and the review window both
export through here.
"""

from __future__ import annotations

from pathlib import Path

from anonymizer.core.ingest import OcrEngine
from anonymizer.core.redact.leakage import Leak, find_leaks
from anonymizer.core.redact.pdf import redact_pdf
from anonymizer.core.types import Document


def export_redacted(
    source: Path | str,
    document: Document,
    destination: Path | str,
    *,
    ocr: OcrEngine | None = None,
) -> list[Leak]:
    """Redact a PDF into `destination`, keeping the result only if it has no leaks.

    An existing file at `destination` is replaced when the check passes and
    left untouched when it fails.

    Args:
        source: PDF the document was loaded from.
        document: The loaded document with its reviewed entities.
        destination: Path of the redacted copy.
        ocr: The engine that read the document's scanned pages; the leak
            check re-reads them with it.

    Returns:
        The leaks found. Empty means the copy was written; otherwise nothing
        was.

    Raises:
        ValueError: If `destination` is `source`, `redact_pdf` refuses the
            document (see there), or OCR read pages and no engine is given.
    """
    source, destination = Path(source), Path(destination)
    if destination.resolve() == source.resolve():
        msg = "the redacted copy must not overwrite its source"
        raise ValueError(msg)
    partial = destination.with_name(f".{destination.name}.partial")
    try:
        redact_pdf(source, document, partial)
        leaks = find_leaks(partial, document, ocr=ocr)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    if leaks:
        partial.unlink()
        return leaks
    partial.replace(destination)
    return []
