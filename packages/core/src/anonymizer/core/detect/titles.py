"""Academic titles and degrees written next to a detected name.

A title narrows down who a person is ("doc. Ing. Jan Novák, Ph.D." among the
Jan Nováks), but the name model is asked for persons and usually stops at the
name. Rather than asking the model for titles, which would also tag the same
abbreviations where no name follows, every person span is widened over the
titles directly before it and the degrees directly after it. Only spans already
found grow, so this adds no new false positives; a title next to a missed name
stays, as the name does.

The lists cover Czech and Slovak titles and the common English and
international ones (Dr., Ph.D., MBA). They are matched case-insensitively,
since "Doc." and "Prof." open a sentence, and a title must stand as a whole
word: "Ing." is not found inside "Lng.".
"""

from __future__ import annotations

import logging
import re

from anonymizer.core.detect.base import describe
from anonymizer.core.types import Document, Entity, EntityType

log = logging.getLogger(__name__)

TITLES_BEFORE = (
    "Bc.",
    "BcA.",
    "Ing.",
    "Ing. arch.",
    "Mgr.",
    "MgA.",
    "MUDr.",
    "MDDr.",
    "MVDr.",
    "JUDr.",
    "PhDr.",
    "RNDr.",
    "PharmDr.",
    "PaedDr.",
    "ThDr.",
    "ThLic.",
    "ICDr.",
    "RSDr.",
    "Dr.",
    "doc.",
    "prof.",
)
"""Titles written before a name."""

DEGREES_AFTER = (
    "Ph.D.",
    "PhD.",
    "Ph.D",
    "PhD",
    "Th.D.",
    "ArtD.",
    "CSc.",
    "DrSc.",
    "DiS.",
    "MBA",
    "MPA",
    "LL.M.",
    "DBA",
)
"""Degrees written after a name, usually after a comma."""


def _alternatives(titles: tuple[str, ...]) -> str:
    # Longest first, so "Ing. arch." wins over "Ing." and "Ph.D." over "Ph.D".
    ordered = sorted(titles, key=len, reverse=True)
    return "|".join(r"\s+".join(re.escape(part) for part in title.split()) for title in ordered)


# Titles end where the name starts; degrees start where it ends.
_BEFORE = re.compile(rf"(?:(?<!\w)(?:{_alternatives(TITLES_BEFORE)})\s*)+$", re.IGNORECASE)
_AFTER = re.compile(rf"(?:\s*,?\s*(?:{_alternatives(DEGREES_AFTER)})(?!\w))+", re.IGNORECASE)
# Far enough back for "prof. Ing. arch. MUDr. " and the like.
_LOOK_BACK = 80


def extend_with_titles(document: Document) -> int:
    """Widen every person span in the page text over the titles and degrees beside it.

    A span never grows into another page-text entity.

    Args:
        document: Document whose person entities are widened, in place.

    Returns:
        The number of entities widened.
    """
    widened = 0
    for page in document.pages:
        on_page = document.entities_on_page(page.index)
        for entity in on_page:
            if entity.type is not EntityType.PERSON:
                continue
            start, end = entity.span
            before = _BEFORE.search(page.text, max(start - _LOOK_BACK, 0), start)
            after = _AFTER.match(page.text, end)
            new_start = before.start() if before else start
            new_end = after.end() if after else end
            if (new_start, new_end) == (start, end) or _collides(
                new_start, new_end, entity, on_page
            ):
                continue
            document.adjust_span(entity.entity_id, new_start, new_end)
            widened += 1
            if log.isEnabledFor(logging.DEBUG):
                log.debug("widened over a title: %s", describe(entity))
    return widened


def _collides(start: int, end: int, entity: Entity, on_page: list[Entity]) -> bool:
    """Whether a widened span would reach into another entity on the page."""
    for other in on_page:
        if other is entity:
            continue
        other_start, other_end = other.span
        if start < other_end and other_start < end:
            return True
    return False
