"""Detection as every client runs it, written once.

The command line, the review window and the benchmark all build a detector
for a language, run it over a loaded document and mark further occurrences.
Keeping those steps here means a client cannot drift from the others: an option
one of them forgets is a bug in one place, and the benchmark measures exactly
what the tools ship. Writing the redacted copy is `redact.export_redacted`.
"""

from __future__ import annotations

from anonymizer.core.detect import (
    CombinedDetector,
    Detector,
    detect_document,
    detector_for,
    propagate_occurrences,
)
from anonymizer.core.types import Document


def build_detector(language: str | None, *, model: Detector | None = None) -> Detector:
    """Return the rules for a language, combined with a model detector if one is given.

    Args:
        language: BCP 47 tag selecting the rules; every rule runs for `None`.
        model: A loaded model detector (see `detect.load_gliner_detector`).

    Returns:
        The detector to run over a document.
    """
    rules = detector_for(language)
    return rules if model is None else CombinedDetector([rules, model])


def run_detection(document: Document, detector: Detector, *, propagate: bool = True) -> None:
    """Replace a document's entities with what a detector finds in its pages and surfaces.

    Args:
        document: Document to scan, in place.
        detector: Detector to run (see `build_detector`).
        propagate: Also mark every further occurrence of the texts found.
    """
    document.entities = detect_document(detector, document)
    if propagate:
        document.entities += propagate_occurrences(document)
