"""Detection as every client runs it, written once.

The command line, the review window and the benchmark all settle the language
(recognising it from the text when asked to), build a detector for it, run it
over a loaded document and mark further occurrences; text a reviewer adds is
marked again the same way.
Keeping those steps here means a client cannot drift from the others: an option
one of them forgets is a bug in one place, and the benchmark measures exactly
what the tools ship. Writing the redacted copy is `redact.export_redacted`.
"""

from __future__ import annotations

import logging
from collections import Counter

from anonymizer.core.detect import (
    CombinedDetector,
    Detector,
    NamesOnly,
    detect_document,
    detector_for,
    extend_with_titles,
    propagate_occurrences,
)
from anonymizer.core.language import AUTO, detect_language
from anonymizer.core.log import counts, short_fingerprint, step
from anonymizer.core.types import (
    DetectionSource,
    Document,
    Entity,
    EntityType,
    PageProgress,
    ReviewState,
)

log = logging.getLogger(__name__)


def resolve_language(document: Document, requested: str | None) -> str | None:
    """Return the language to detect with, recognising it from the text for `AUTO`.

    The answer is stored as the document's language, so a saved review keeps
    what detection used.

    Args:
        document: The loaded document, scanned pages already read.
        requested: A BCP 47 tag, `None` for every rule, or `language.AUTO`.

    Returns:
        A BCP 47 tag, or `None` when every rule is to run.
    """
    if requested != AUTO:
        document.language = requested
        return requested
    language = detect_language(document)
    log.info("language recognised: %s", language or "none, every rule runs")
    document.language = language
    return language


def build_detector(
    language: str | None, *, model: Detector | None = None, names_only: bool = True
) -> Detector:
    """Return the rules for a language, combined with a model detector if one is given.

    The model's person spans are cut back to the name and its address spans
    lose the labels of address fields (`detect.NamesOnly`), with the role
    words of the same language.

    Args:
        language: BCP 47 tag selecting the rules and role words; every list
            applies for `None`.
        model: A loaded model detector (see `detect.load_gliner_detector`).
        names_only: Cut the model's person and address spans back to the
            value. Every client keeps the default; the evaluation turns it
            off to measure what the filter is worth.

    Returns:
        The detector to run over a document.
    """
    rules = detector_for(language)
    if model is None:
        detector = rules
    else:
        filtered = NamesOnly(model, language) if names_only else model
        detector = CombinedDetector([rules, filtered])
    log.debug("detector built: %s (%d rules)", detector.name, len(rules.finders))
    return detector


def run_detection(
    document: Document,
    detector: Detector,
    *,
    propagate: bool = True,
    progress: PageProgress | None = None,
) -> None:
    """Replace a document's entities with what a detector finds in its pages and surfaces.

    Person spans are widened over the academic titles beside them last, so a
    repeat found without its title gets the one written next to it.

    Args:
        document: Document to scan, in place.
        detector: Detector to run (see `build_detector`).
        propagate: Also mark every further occurrence of the texts found.
        progress: Told how many pages are scanned (see `PageProgress`).
    """
    with step(
        log,
        "detection",
        done_level=logging.INFO,
        document=short_fingerprint(document.fingerprint),
        detector=detector.name,
        propagate=propagate,
        pages=len(document.pages),
        hidden_items=len(document.surfaces),
    ) as outcome:
        document.entities = detect_document(detector, document, progress)
        outcome["found"] = len(document.entities)
        if propagate:
            propagated = propagate_occurrences(document)
            document.entities += propagated
            outcome["propagated"] = len(propagated)
        outcome["titles"] = extend_with_titles(document)
        outcome["types"] = counts(Counter(entity.type for entity in document.entities))


def add_finding(
    document: Document,
    page_index: int,
    start: int,
    end: int,
    entity_type: EntityType,
    *,
    propagate: bool = True,
) -> list[Entity]:
    """Add text a reviewer marked because detection missed it, with its other occurrences.

    The span is widened to whole words (`Document.add_span`). Further
    occurrences are found as detection finds them (`propagate_occurrences`):
    exact text, whole words, any spacing; inflected forms are not found.

    Args:
        document: The document under review, in place.
        page_index: Page the text is on.
        start: First offset of the selection in the page text.
        end: Offset one past the selection.
        entity_type: What the text is; not a region.
        propagate: Also mark the text's further occurrences, as detection did.

    Returns:
        The added entity first, then its further occurrences (pending, marked
        propagated), all already in the document.

    Raises:
        KeyError: If no page carries that index.
        ValueError: As `Document.add_span`.
    """
    finding = document.add_span(page_index, start, end, entity_type)
    repeats = propagate_occurrences(document, [finding]) if propagate else []
    document.entities += repeats
    log.debug(
        "finding added: entity=%s page=%d repeats=%d", finding.entity_id, page_index, len(repeats)
    )
    return [finding, *repeats]


def remove_finding(document: Document, entity_id: str) -> list[Entity]:
    """Take out what a reviewer added, with the repeats nothing else explains any more.

    A repeat (`DetectionSource.PROPAGATED`) of the removed text goes too,
    unless the reviewer confirmed it or another finding still marks the same
    text: it was proposed only because the text was marked.

    Args:
        document: The document under review, in place.
        entity_id: The entity to remove.

    Returns:
        The removed entity first, then the repeats removed with it.

    Raises:
        KeyError: If no entity carries that id.
    """
    removed = document.remove_entity(entity_id)
    text = _spaced(removed.text)
    if text is None or any(
        _spaced(entity.text) == text
        for entity in document.entities
        if entity.is_redactable and entity.source is not DetectionSource.PROPAGATED
    ):
        return [removed]
    orphans = [
        entity
        for entity in document.entities
        if entity.source is DetectionSource.PROPAGATED
        and entity.review is not ReviewState.CONFIRMED
        and _spaced(entity.text) == text
    ]
    for orphan in orphans:
        document.remove_entity(orphan.entity_id)
    log.debug("finding removed: entity=%s repeats=%d", entity_id, len(orphans))
    return [removed, *orphans]


def _spaced(text: str | None) -> str | None:
    """A text with its spacing made uniform, as repeats are matched with any spacing."""
    return None if text is None else " ".join(text.split())
