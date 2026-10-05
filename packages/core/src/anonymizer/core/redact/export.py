"""Writing a redacted copy that exists only if it passed the leak check.

The copy is written under a temporary name next to the destination, checked,
and renamed only when no leak was found, so a file that failed the check never
appears under the name the user asked for. The check can be left out (the
review window's setting, or a reviewer saving a copy the check refused after
seeing its findings); the copy is then written as redaction made it. The CLI
and the review window both export through here.
"""

from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

from anonymizer.core.ingest import OcrEngine
from anonymizer.core.log import counts, short_fingerprint, step
from anonymizer.core.redact.leakage import Leak, find_leaks
from anonymizer.core.redact.pdf import redact_pdf
from anonymizer.core.types import Document, StepProgress

log = logging.getLogger(__name__)


def export_redacted(
    source: Path | str,
    document: Document,
    destination: Path | str,
    *,
    ocr: OcrEngine | None = None,
    check: bool = True,
    progress: StepProgress | None = None,
) -> list[Leak]:
    """Redact a PDF into `destination`, keeping the result only if it has no leaks.

    An existing file at `destination` is replaced when the check passes (or
    is left out) and left untouched when it fails.

    Args:
        source: PDF the document was loaded from.
        document: The loaded document with its reviewed entities.
        destination: Path of the redacted copy.
        ocr: The engine that read the document's scanned pages; the leak
            check re-reads them with it.
        check: Run the leak check; without it the copy is always written.
        progress: Told each step as it starts: those of `redact_pdf`, then
            each layer of `find_leaks`.

    Returns:
        The leaks found. Empty means the copy was written; otherwise nothing
        was.

    Raises:
        ValueError: If `destination` is `source`, `redact_pdf` refuses the
            document (see there), or the check runs, OCR read pages and no
            engine is given.
    """
    source, destination = Path(source), Path(destination)
    if destination.resolve() == source.resolve():
        msg = "the redacted copy must not overwrite its source"
        raise ValueError(msg)
    partial = destination.with_name(f".{destination.name}.partial")
    with step(
        log, "export", done_level=logging.INFO, document=short_fingerprint(document.fingerprint)
    ) as outcome:
        try:
            redact_pdf(source, document, partial, progress=progress)
            leaks = find_leaks(partial, document, ocr=ocr, progress=progress) if check else []
        except BaseException:
            partial.unlink(missing_ok=True)
            raise
        if leaks:
            partial.unlink()
            log.error(
                "export refused: leak check found %d leak(s), nothing written; by layer: %s",
                len(leaks),
                counts(Counter(leak.layer.value for leak in leaks)),
            )
            outcome["written"] = False
            return leaks
        partial.replace(destination)
        outcome["written"] = True
        outcome["leak_check"] = "passed" if check else "off"
    return []
