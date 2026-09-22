"""Detector interface shared by rule-based and model-based detection.

A detector maps a `Page` to the entities it found on it. Rule detectors are
built from *finders*: functions that scan a string and yield `Match` objects
with page-local offsets. Model backends implement the same `Detector` protocol
in `detect/` modules of their own.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from anonymizer.core.types import DetectionSource, Entity, EntityType, Page

# Applied when two matches overlap: the type listed first wins. Structured
# identifiers beat free-form ones, because a valid checksum is stronger evidence
# than a digit pattern (a birth number also looks like `account/bank code`).
OVERLAP_PRIORITY: tuple[EntityType, ...] = (
    EntityType.BIRTH_NUMBER,
    EntityType.IBAN,
    EntityType.CREDIT_CARD,
    EntityType.BANK_ACCOUNT,
    EntityType.COMPANY_ID,
    EntityType.EMAIL,
    EntityType.PHONE,
    EntityType.ID_NUMBER,
    EntityType.PERSON,
    EntityType.ADDRESS,
    EntityType.DATE,
    EntityType.ORGANIZATION,
    EntityType.OTHER,
)


@dataclass(frozen=True, slots=True)
class Match:
    """A span found in a page's text.

    Attributes:
        type: Category of personal data.
        start: First offset of the span in the scanned text.
        end: Offset one past the span.
        text: The matched substring.
    """

    type: EntityType
    start: int
    end: int
    text: str

    def __post_init__(self) -> None:
        """Reject empty or negative spans.

        Raises:
            ValueError: If the span is not a positive range at a valid offset.
        """
        if self.start < 0 or self.end <= self.start:
            msg = f"invalid match span [{self.start}, {self.end})"
            raise ValueError(msg)

    @property
    def length(self) -> int:
        """Number of characters covered."""
        return self.end - self.start

    def overlaps(self, other: Match) -> bool:
        """Whether the two spans share at least one character.

        Args:
            other: Span to compare with.

        Returns:
            `True` if the spans intersect.
        """
        return self.start < other.end and other.start < self.end


Finder = Callable[[str], Iterable[Match]]
"""Scans a string and yields matches with offsets into that same string."""


@runtime_checkable
class Detector(Protocol):
    """Produces entities for a single page."""

    @property
    def name(self) -> str:
        """Identifier used in logs and evaluation reports."""
        ...

    def detect(self, page: Page) -> list[Entity]:
        """Return the entities found on a page.

        Args:
            page: Page to scan; offsets refer to `page.text`.

        Returns:
            Entities in reading order.
        """
        ...


def resolve_overlaps(
    matches: Iterable[Match],
    priority: Sequence[EntityType] = OVERLAP_PRIORITY,
) -> list[Match]:
    """Drop matches that overlap a stronger one.

    Matches are considered by type priority first, then by length, then by
    position, and a match is kept only if it does not overlap a match already
    kept. Equal-priority overlaps therefore resolve in favour of the longer span.

    Args:
        matches: Candidate matches, in any order.
        priority: Entity types from strongest to weakest.

    Returns:
        Surviving matches sorted by start offset.
    """
    ranks = {entity_type: rank for rank, entity_type in enumerate(priority)}
    weakest = len(ranks)
    ordered = sorted(
        matches,
        key=lambda match: (ranks.get(match.type, weakest), -match.length, match.start),
    )
    kept: list[Match] = []
    for match in ordered:
        if not any(match.overlaps(other) for other in kept):
            kept.append(match)
    return sorted(kept, key=lambda match: match.start)


class RuleDetector:
    """Runs a set of finders over a page and resolves their overlaps.

    Attributes:
        finders: Finder functions applied to the page text.
    """

    def __init__(self, finders: Sequence[Finder], name: str = "rules") -> None:
        """Initialize the detector.

        Args:
            finders: Finder functions applied to the page text.
            name: Identifier used in logs and evaluation reports.
        """
        self.finders = tuple(finders)
        self._name = name

    @property
    def name(self) -> str:
        """Identifier used in logs and evaluation reports."""
        return self._name

    def detect(self, page: Page) -> list[Entity]:
        """Scan a page and return the entities its finders agree on.

        Args:
            page: Page to scan; offsets refer to `page.text`.

        Returns:
            Entities in reading order, with geometry resolved from page words.
        """
        candidates = [match for finder in self.finders for match in finder(page.text)]
        return [
            Entity(
                type=match.type,
                page_index=page.index,
                start=match.start,
                end=match.end,
                text=match.text,
                bboxes=page.bboxes_for_span(match.start, match.end),
                source=DetectionSource.RULE,
            )
            for match in resolve_overlaps(candidates)
        ]
