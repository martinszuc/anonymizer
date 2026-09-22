"""Redacting every occurrence of text that is already marked.

Detection may find a name once and miss it elsewhere, and a reviewer may add
a missed name by hand. Every other place the same text appears in the page text
becomes an entity of its own, marked as propagated so that evaluation can tell
it apart from what a detector found. Whether this runs is the caller's setting.

Matching is exact and whole-word, with any whitespace between the words, so a
name broken across lines is found and `Jan` does not match `January`. It does
not find inflected forms (`Novák`, `Nováka`, `Novákovi`); that needs a
morphological analyser or a model.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from anonymizer.core.types import DetectionSource, Document, Entity, EntityType, Page


def propagate_occurrences(document: Document) -> list[Entity]:
    """Return entities for further occurrences of marked text in the page text.

    The texts come from every entity review has not rejected, on a page or on
    a surface, so an address found in a link target is also found where it is
    printed. Occurrences overlapping an existing page-text entity are skipped,
    and longer texts claim their occurrences first.

    Args:
        document: Document whose entities mark the texts to look for.

    Returns:
        New pending entities, in page and offset order. The caller adds them to
        the document.
    """
    types_by_text: dict[str, EntityType] = {}
    for entity in document.entities:
        if entity.is_redactable and entity.text and entity.text not in types_by_text:
            types_by_text[entity.text] = entity.type
    texts = sorted(types_by_text, key=len, reverse=True)

    propagated: list[Entity] = []
    for page in document.pages:
        taken = [entity.span for entity in document.entities_on_page(page.index)]
        for text in texts:
            for start, end in _occurrences(text, page.text):
                if any(start < other_end and other_start < end for other_start, other_end in taken):
                    continue
                taken.append((start, end))
                propagated.append(_occurrence(page, start, end, types_by_text[text]))
    return sorted(propagated, key=lambda entity: (entity.page_index, entity.span))


def _occurrences(text: str, page_text: str) -> Iterator[tuple[int, int]]:
    """Yield the spans where `text` occurs as whole words, spacing ignored."""
    words = text.split()
    if not words:
        return
    pattern = r"(?<!\w)" + r"\s+".join(re.escape(word) for word in words) + r"(?!\w)"
    for found in re.finditer(pattern, page_text):
        yield found.start(), found.end()


def _occurrence(page: Page, start: int, end: int, entity_type: EntityType) -> Entity:
    """Build a propagated entity for one occurrence."""
    return Entity(
        type=entity_type,
        page_index=page.index,
        start=start,
        end=end,
        text=page.text[start:end],
        bboxes=page.bboxes_for_span(start, end),
        source=DetectionSource.PROPAGATED,
    )
