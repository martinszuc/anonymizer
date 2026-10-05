"""Scoring detections and redacted output against the planted items.

The generator wraps paragraphs, so an item may be split over lines; every
comparison tolerates whitespace.

- **Detection.** A page item is located in the ingested page text by its
  words (a scan's caller can locate it by its ground-truth boxes instead, as
  `ocr_score.item_locations` does); it is *found* when one entity's span
  covers it, *partial* when entities only overlap it, *missed* otherwise. On
  a surface (no page position) an item is found when an entity's text
  contains it, partial when an entity's text lies inside it.
- **False positives.** Page entities overlapping no planted item.
- **Residue.** After redaction the output is read again, pages and surfaces.
  An item is *readable* when its whole text is still there; a *fragment* is a
  word of it (three characters or more) that is readable although it occurs
  nowhere else in the original. A document is *safe* with neither. The same
  test on the item's own carrier alone gives leaks by carrier.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any, Literal

from anonymizer.core.types import Document, Entity

from benchmark.spec import DocumentSpec, GoldItem

Outcome = Literal["found", "partial", "missed"]

_WORD = re.compile(r"\w{3,}")

Location = tuple[int, int, int]
"""Page index, start and end of a planted item in the ingested page text."""

Locations = Mapping[int, Location | None]
"""Where each planted page item lies, by its index in `DocumentSpec.gold`; None if nowhere."""


def compact(text: str) -> str:
    """Remove all whitespace."""
    return "".join(text.split())


@dataclass(frozen=True)
class ItemResult:
    """What happened to one planted item."""

    type: str
    text: str
    carrier: str
    outcome: Outcome
    type_correct: bool
    readable_after: bool
    fragments_after: tuple[str, ...]
    left_in_carrier: bool


@dataclass(frozen=True)
class DocumentResult:
    """Scores for one document under one detector system."""

    items: tuple[ItemResult, ...]
    false_positives: tuple[str, ...]
    decoys_removed: tuple[str, ...]
    leak_check_passed: bool
    seconds: float

    @property
    def safe(self) -> bool:
        """No planted item readable, whole or in fragments."""
        return not any(item.readable_after or item.fragments_after for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping."""
        return {
            "items": [asdict(item) for item in self.items],
            "false_positives": list(self.false_positives),
            "decoys_removed": list(self.decoys_removed),
            "leak_check_passed": self.leak_check_passed,
            "seconds": round(self.seconds, 3),
            "safe": self.safe,
            "counts": outcome_counts(self.items),
        }


def score_detection(
    spec: DocumentSpec, document: Document, locations: Locations | None = None
) -> list[tuple[Outcome, bool]]:
    """Return, per planted item, its outcome and whether the type matched.

    `locations` places the page items; by default each is found by its words.
    """
    if locations is None:
        locations = _page_locations(spec, document)
    results: list[tuple[Outcome, bool]] = []
    for index, item in enumerate(spec.gold):
        entities = _on_carrier(document.entities, item.carrier)
        if item.carrier == "page":
            results.append(_match_position(item, locations.get(index), entities))
        else:
            results.append(_match_text(item, entities))
    return results


def false_positives(
    spec: DocumentSpec, document: Document, locations: Locations | None = None
) -> list[str]:
    """Return the distinct texts of page entities overlapping no planted item.

    Distinct, because one wrong text repeated through a document is one mistake
    for the detector, and repeated filler would otherwise dominate the count.
    `locations` places the page items, as in `score_detection`.
    """
    if locations is None:
        locations = _page_locations(spec, document)
    planted = [location for location in locations.values() if location]
    wrong = (
        " ".join(entity.text.split())
        for entity in _on_carrier(document.entities, "page")
        if entity.text is not None and not any(_overlaps(entity, location) for location in planted)
    )
    return sorted(set(wrong))


def residue(
    spec: DocumentSpec, original: Document, redacted: Document
) -> list[tuple[bool, list[str]]]:
    """Return, per planted item, whether it is readable after redaction and its fragments."""
    unplanted = _unplanted_words(spec, original)
    after = _all_text(redacted)
    return [_left_in(item, after, unplanted) for item in spec.gold]


def left_in_carrier(spec: DocumentSpec, original: Document, redacted: Document) -> list[bool]:
    """Return, per planted item, whether its own carrier still holds it, whole or in part.

    `residue` reads the whole output, so a surname left on the page counts
    against a bookmark carrying the same name as well; this tells the
    carriers apart, for leaks by carrier.
    """
    unplanted = _unplanted_words(spec, original)
    results: list[bool] = []
    for item in spec.gold:
        readable, fragments = _left_in(item, _carrier_text(redacted, item.carrier), unplanted)
        results.append(readable or bool(fragments))
    return results


def _unplanted_words(spec: DocumentSpec, original: Document) -> set[str]:
    """Words occurring outside every planted item: no evidence of a leak."""
    unplanted = _all_text(original)
    for item in sorted(spec.gold, key=lambda item: -len(item.text)):
        # The generator may have wrapped the item over two lines.
        pattern = r"\s+".join(re.escape(word) for word in item.text.split())
        unplanted = re.sub(pattern, " ", unplanted)
    return {word.lower() for word in _WORD.findall(unplanted)}


def _left_in(item: GoldItem, after: str, unplanted: set[str]) -> tuple[bool, list[str]]:
    if compact(item.text) in compact(after):
        return True, []
    after_words = {word.lower() for word in _WORD.findall(after)}
    fragments = [
        word
        for word in _WORD.findall(item.text)
        if word.lower() in after_words and word.lower() not in unplanted
    ]
    return False, fragments


def decoys_removed(spec: DocumentSpec, redacted: Document) -> list[str]:
    """Return decoys (not personal) that redaction removed: over-redaction."""
    after = compact(_all_text(redacted))
    return [decoy for decoy in spec.decoys if compact(decoy) not in after]


def outcome_counts(items: tuple[ItemResult, ...] | list[ItemResult]) -> dict[str, int]:
    """Count items by outcome, plus readable ones."""
    counts = Counter(item.outcome for item in items)
    return {
        "gold": len(items),
        "found": counts["found"],
        "partial": counts["partial"],
        "missed": counts["missed"],
        "readable_after": sum(item.readable_after for item in items),
        "with_fragments": sum(bool(item.fragments_after) for item in items),
        "left_in_carrier": sum(item.left_in_carrier for item in items),
    }


def _page_locations(spec: DocumentSpec, document: Document) -> dict[int, Location | None]:
    """Locate each planted page item in the ingested page text.

    Items are planted in reading order, so each takes the first occurrence of
    its text after the previous item. "Bartoš" planted alone after "Roman
    Bartoš" is the later, standalone occurrence, not the surname inside the
    full name. An item found only before that point (the text extracted in an
    unexpected order) takes its first occurrence no other item holds.
    """
    cursor = (0, 0)
    taken: list[Location] = []
    locations: dict[int, Location | None] = {}
    for index, item in enumerate(spec.gold):
        if item.carrier != "page":
            continue
        # Whole words only, any whitespace between them: the generator wraps lines.
        pattern = re.compile(
            r"(?<!\w)" + r"\s+".join(re.escape(word) for word in item.text.split()) + r"(?!\w)"
        )
        free = [
            (page.index, match.start(), match.end())
            for page in document.pages
            for match in pattern.finditer(page.text)
            if not any(
                _overlapping((page.index, match.start(), match.end()), held) for held in taken
            )
        ]
        ahead = [location for location in free if location[:2] >= cursor]
        location = ahead[0] if ahead else (free[0] if free else None)
        locations[index] = location
        if location is not None:
            taken.append(location)
            if ahead:
                cursor = (location[0], location[2])
    return locations


def _overlapping(first: Location, second: Location) -> bool:
    return first[0] == second[0] and first[1] < second[2] and second[1] < first[2]


def _overlaps(entity: Entity, location: Location) -> bool:
    page_index, start, end = location
    entity_start, entity_end = entity.span
    return entity.page_index == page_index and entity_start < end and start < entity_end


def _match_position(
    item: GoldItem, location: Location | None, entities: list[Entity]
) -> tuple[Outcome, bool]:
    if location is None:
        return "missed", False
    _, start, end = location
    touching = [entity for entity in entities if _overlaps(entity, location)]
    covering = [entity for entity in touching if entity.span[0] <= start and end <= entity.span[1]]
    if covering:
        return "found", any(entity.type == item.type for entity in covering)
    if touching:
        return "partial", any(entity.type == item.type for entity in touching)
    return "missed", False


def _match_text(item: GoldItem, entities: list[Entity]) -> tuple[Outcome, bool]:
    """Match on a surface, where there is no page position: by containment."""
    target = compact(item.text)
    covering = [entity for entity in entities if entity.text and target in compact(entity.text)]
    if covering:
        return "found", any(entity.type == item.type for entity in covering)
    inside = [entity for entity in entities if entity.text and compact(entity.text) in target]
    if inside:
        return "partial", any(entity.type == item.type for entity in inside)
    return "missed", False


def _on_carrier(entities: list[Entity], carrier: str) -> list[Entity]:
    if carrier == "page":
        return [entity for entity in entities if entity.surface_id is None and not entity.is_region]
    return [
        entity
        for entity in entities
        if entity.surface_id is not None and entity.surface_id.startswith(f"{carrier}:")
    ]


def _carrier_text(document: Document, carrier: str) -> str:
    if carrier == "page":
        return "\n".join(page.text for page in document.pages)
    return "\n".join(surface.value for surface in document.surfaces if surface.kind == carrier)


def _all_text(document: Document) -> str:
    pages = "\n".join(page.text for page in document.pages)
    surfaces = "\n".join(surface.value for surface in document.surfaces)
    return f"{pages}\n{surfaces}"
