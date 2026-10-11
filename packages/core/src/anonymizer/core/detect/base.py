"""Detector interface shared by rule-based and model-based detection.

A detector maps a `Page` to the entities it found on it. Rule detectors are
built from *finders*: functions that scan a string and yield `Match` objects
with page-local offsets. Model backends implement the same `Detector` protocol
in `detect/` modules of their own.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol, Self, runtime_checkable

from anonymizer.core.log import fields
from anonymizer.core.types import DetectionSource, Entity, EntityType, Page

log = logging.getLogger(__name__)

# Applied when one span lies inside another: the type listed first wins.
# Structured identifiers beat free-form ones, because a valid checksum is
# stronger evidence than a digit pattern (a birth number also looks like
# `account/bank code`). URLs come first as the exception: a URL is a single
# token, so whatever overlaps it lies inside it, and keeping only the inner
# match would leave the rest of the URL (a profile path, say) unredacted.
OVERLAP_PRIORITY: tuple[EntityType, ...] = (
    EntityType.URL,
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

    @classmethod
    def from_regex(
        cls, found: re.Match[str], entity_type: EntityType, group: int | str = 0
    ) -> Self:
        """Build a match from one group of a regular expression match.

        Args:
            found: The regular expression match.
            entity_type: Category of personal data.
            group: The group that holds the value; the whole match by default.

        Returns:
            The match, with the group's offsets and text.
        """
        return cls(entity_type, found.start(group), found.end(group), found[group])


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


def merge_entities(
    entities: Iterable[Entity],
    priority: Sequence[EntityType] = OVERLAP_PRIORITY,
) -> list[Entity]:
    """Drop entities lying entirely inside a stronger or longer one.

    A partial overlap keeps both entities, and so does a weaker span that
    contains a stronger one: dropping a span that reaches beyond the winner
    would leave its remainder unredacted (an address containing a valid
    account number, a model span crossing a rule match). Spans are compared
    only within the same page text or surface; regions are always kept.

    Args:
        entities: Candidate text entities and regions, in any order.
        priority: Entity types from strongest to weakest.

    Returns:
        Surviving entities: regions first, then spans in reading order.
    """
    ranks = {entity_type: rank for rank, entity_type in enumerate(priority)}
    weakest = len(ranks)
    candidates = list(entities)
    regions = [entity for entity in candidates if entity.is_region]
    spans = [entity for entity in candidates if not entity.is_region]
    ordered = sorted(
        spans,
        key=lambda entity: (
            ranks.get(entity.type, weakest),
            -(entity.span[1] - entity.span[0]),
            -(entity.score if entity.score is not None else 1.0),
            entity.span[0],
        ),
    )
    kept: list[Entity] = []
    for entity in ordered:
        start, end = entity.span
        container = next(
            (
                other
                for other in kept
                if other.page_index == entity.page_index
                and other.surface_id == entity.surface_id
                and other.span[0] <= start
                and end <= other.span[1]
            ),
            None,
        )
        if container is None:
            kept.append(entity)
        elif log.isEnabledFor(logging.DEBUG):
            log.debug("merge: dropped %s, inside %s", describe(entity), describe(container))
    kept.sort(key=lambda entity: (entity.page_index or 0, entity.surface_id or "", entity.span))
    return regions + kept


def describe(entity: Entity) -> str:
    """Render an entity for a DEBUG record: what was found, where, and by what.

    This includes the document's text, so it belongs in DEBUG records only.

    Args:
        entity: Entity to describe.

    Returns:
        ``key=value`` pairs: type, page, span, source, score and text.
    """
    shown: dict[str, object] = {"type": entity.type, "page": entity.page_index}
    if not entity.is_region:
        shown["span"] = f"[{entity.span[0]},{entity.span[1]})"
    shown["source"] = entity.source
    if entity.score is not None:
        shown["score"] = f"{entity.score:.2f}"
    shown["text"] = entity.text
    return fields(**shown).lstrip()


class CombinedDetector:
    """Runs several detectors on a page and merges their entities.

    Attributes:
        detectors: Detectors applied to every page, in order.
    """

    def __init__(self, detectors: Sequence[Detector], name: str | None = None) -> None:
        """Initialize the detector.

        Args:
            detectors: Detectors applied to every page.
            name: Identifier; the members' names joined with `+` by default.

        Raises:
            ValueError: If no detector is given.
        """
        if not detectors:
            msg = "at least one detector is needed"
            raise ValueError(msg)
        self.detectors = tuple(detectors)
        self._name = name or "+".join(detector.name for detector in self.detectors)

    @property
    def name(self) -> str:
        """Identifier used in logs and evaluation reports."""
        return self._name

    def detect(self, page: Page) -> list[Entity]:
        """Return the merged entities of every detector.

        Args:
            page: Page to scan; offsets refer to `page.text`.

        Returns:
            Entities in reading order; see `merge_entities`.
        """
        found = [(detector.name, detector.detect(page)) for detector in self.detectors]
        merged = merge_entities(entity for _name, entities in found for entity in entities)
        if log.isEnabledFor(logging.DEBUG):
            per_detector = ", ".join(f"{name}={len(entities)}" for name, entities in found)
            log.debug(
                "%s: page %d: %s, %d after merge", self.name, page.index, per_detector, len(merged)
            )
        return merged


class AgreementDetector:
    """Runs several detectors on a page and keeps what they agree on.

    An entity survives when every other detector found an entity of the same
    type overlapping it. Where two agree, both their spans are kept and
    merged (`merge_entities`), so the wider reading still covers the whole
    name. A precision-first combination for evaluation: it misses whatever
    one detector alone found.

    Attributes:
        detectors: Detectors applied to every page, in order.
    """

    def __init__(self, detectors: Sequence[Detector], name: str | None = None) -> None:
        """Initialize the detector.

        Args:
            detectors: Detectors applied to every page; at least two.
            name: Identifier; the members' names joined with `&` by default.

        Raises:
            ValueError: If fewer than two detectors are given.
        """
        if len(detectors) < 2:
            msg = "agreement needs at least two detectors"
            raise ValueError(msg)
        self.detectors = tuple(detectors)
        self._name = name or "&".join(detector.name for detector in self.detectors)

    @property
    def name(self) -> str:
        """Identifier used in logs and evaluation reports."""
        return self._name

    def detect(self, page: Page) -> list[Entity]:
        """Return the entities every detector found, merged.

        Args:
            page: Page to scan; offsets refer to `page.text`.

        Returns:
            Entities in reading order; see `merge_entities`.
        """
        found = [detector.detect(page) for detector in self.detectors]
        agreed = [
            entity
            for index, entities in enumerate(found)
            for entity in entities
            if all(
                any(_same_reading(entity, other) for other in others)
                for other_index, others in enumerate(found)
                if other_index != index
            )
        ]
        merged = merge_entities(agreed)
        log.debug(
            "%s: page %d: %d found, %d agreed",
            self.name,
            page.index,
            sum(len(entities) for entities in found),
            len(merged),
        )
        return merged


def _same_reading(entity: Entity, other: Entity) -> bool:
    """Whether two text entities have one type and overlap on the same text."""
    if entity.is_region or other.is_region or entity.type != other.type:
        return False
    if (entity.page_index, entity.surface_id) != (other.page_index, other.surface_id):
        return False
    start, end = entity.span
    other_start, other_end = other.span
    return start < other_end and other_start < end


class RuleDetector:
    """Runs a set of finders over a page and merges their matches.

    Attributes:
        finders: Finder functions applied to the page text.
        ocr_finders: Finders applied in addition to pages read by OCR, whose
            text carries the reader's misreadings.
    """

    def __init__(
        self,
        finders: Sequence[Finder],
        name: str = "rules",
        ocr_finders: Sequence[Finder] = (),
    ) -> None:
        """Initialize the detector.

        Args:
            finders: Finder functions applied to the page text.
            name: Identifier used in logs and evaluation reports.
            ocr_finders: Finders applied in addition to pages with
                `Page.raster_dpi` set.
        """
        self.finders = tuple(finders)
        self.ocr_finders = tuple(ocr_finders)
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
            Entities in reading order, with geometry resolved from page words;
            see `merge_entities` for overlapping matches.
        """
        finders = self.finders
        if page.raster_dpi is not None:
            finders += self.ocr_finders
        entities = []
        for finder in finders:
            for match in finder(page.text):
                entity = Entity(
                    type=match.type,
                    page_index=page.index,
                    start=match.start,
                    end=match.end,
                    text=match.text,
                    bboxes=page.bboxes_for_span(match.start, match.end),
                    source=DetectionSource.RULE,
                )
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("%s matched %s", _finder_name(finder), describe(entity))
                entities.append(entity)
        merged = merge_entities(entities)
        log.debug(
            "%s: page %d: %d matches, %d after merge",
            self.name,
            page.index,
            len(entities),
            len(merged),
        )
        return merged


def _finder_name(finder: Finder) -> str:
    """Name a finder for a record: its function name, which is what to look for in the code."""
    return getattr(finder, "__name__", None) or type(finder).__name__
