"""Human-readable summaries printed by the command-line client."""

from __future__ import annotations

from collections import Counter

from anonymizer.core.redact import Leak
from anonymizer.core.types import Document, Entity

_PREVIEW_LENGTH = 60


def _counts(entities: list[Entity]) -> str:
    """Summarize entities as `email 2, phone 1`, most frequent first."""
    by_type = Counter(entity.type.value for entity in entities)
    return ", ".join(f"{name} {count}" for name, count in by_type.most_common())


def document_summary(document: Document) -> str:
    """One line describing what was found in a document."""
    pages = len(document.pages)
    entities = len(document.entities)
    line = f"{pages} page{'s' * (pages != 1)}, {entities} entit{'ies' if entities != 1 else 'y'}"
    if document.entities:
        line += f" ({_counts(document.entities)})"
    return f"{line}, {len(document.surfaces)} hidden items"


def entity_table(document: Document) -> str:
    """List every entity: page, type, source, review state and what it covers."""
    rows = ["page  type          source      review     covers"]
    for entity in document.entities:
        page = "-" if entity.page_index is None else str(entity.page_index + 1)
        rows.append(
            f"{page:<5} {entity.type.value:<13} {entity.source.value:<11} "
            f"{entity.review.value:<10} {_covers(document, entity)}"
        )
    return "\n".join(rows)


def _covers(document: Document, entity: Entity) -> str:
    """Describe an entity's content in one line."""
    if entity.is_region:
        (box,) = entity.bboxes
        return f"region [{box.x0:.0f}, {box.y0:.0f}, {box.x1:.0f}, {box.y1:.0f}]"
    text = " ".join((entity.text or "").split())
    if len(text) > _PREVIEW_LENGTH:
        text = text[: _PREVIEW_LENGTH - 1] + "…"
    if entity.surface_id is not None:
        return f"{text}  (in {document.surface(entity.surface_id).kind.value})"
    return text


def redaction_summary(document: Document) -> str:
    """One line describing what a redaction removed."""
    applied = [entity for entity in document.entities if entity.is_redactable]
    kept = len(document.entities) - len(applied)
    regions = sum(entity.is_region for entity in applied)
    line = f"redacted {len(applied) - regions} entities and {regions} regions"
    if kept:
        line += f", kept {kept} rejected"
    return f"{line}; removed {len(document.surfaces)} hidden items"


def leak_report(leaks: list[Leak]) -> str:
    """List the leaks the check found, one per line."""
    lines = [f"leak check FAILED: {len(leaks)} leak{'s' * (len(leaks) != 1)}"]
    lines.extend(f"  {leak.layer.value:<14} {leak.where}: {leak.text}" for leak in leaks)
    return "\n".join(lines)
