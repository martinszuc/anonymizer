"""The document's text with every redacted value replaced by a fixed label.

The output is each page's text (`Page.text`, in reading order), pages
separated by a form feed, with every page-text entity review did not reject
replaced by its type in brackets (`[PERSON]`). Every word under a
redactable region, and every word a form field draws on the page, becomes
`[REDACTED]`: a field's value appears in the page text, and redaction
removes every form field whatever detection found in it. A label is the same whatever it
replaces, so neither the value's width nor its length survives, which a
blacked-out PDF keeps (the gap a removed word leaves is as wide as the word).
Nothing but page text is written: metadata, links, form fields, attachments
and the other surfaces never appear in it, whatever detection found there.

A replacement covers whole words, as PDF redaction removes the words under
its boxes: a span ending inside a word takes the rest of that word with it,
since the remainder of a cut value can still identify. A word touching a
region or a form field at all is replaced: neither has text to check
against, so the text export errs towards removing a neighbour. Overlapping replacements merge
into one, which keeps the label of the one starting first.
"""

from __future__ import annotations

from anonymizer.core.types import BBox, Document, Entity, Page, SurfaceKind

PAGE_SEPARATOR = "\f"
"""Between two pages, as `pdftotext` writes them."""

REGION_LABEL = "[REDACTED]"
"""What a word under a drawn region or inside a form field becomes."""


def entity_label(entity: Entity) -> str:
    """Return the label a redacted value is replaced by, such as `[PERSON]`."""
    return f"[{entity.type.value.upper()}]"


def redact_text(document: Document) -> str:
    """Return the document's page text with every redacted value replaced by its label.

    Args:
        document: The loaded document with its reviewed entities.

    Returns:
        The pages' texts joined by `PAGE_SEPARATOR`; a form feed inside a
        page's own text becomes a line break, so the pages can be told apart.
    """
    return PAGE_SEPARATOR.join(
        _redacted_page(page, document).replace(PAGE_SEPARATOR, "\n") for page in document.pages
    )


def _redacted_page(page: Page, document: Document) -> str:
    """Return one page's text with its replacements made."""
    replacements = _replacements(page, document)
    parts: list[str] = []
    position = 0
    for start, end, label in replacements:
        parts.extend((page.text[position:start], label))
        position = end
    parts.append(page.text[position:])
    return "".join(parts)


def _replacements(page: Page, document: Document) -> list[tuple[int, int, str]]:
    """Return the page's spans to replace, widened to whole words and merged, in order."""
    spans: list[tuple[int, int, str]] = []
    regions = [
        surface.bbox
        for surface in document.surfaces
        if surface.kind is SurfaceKind.FORM_FIELD
        and surface.page_index == page.index
        and surface.bbox is not None
    ]
    for entity in document.entities:
        if entity.page_index != page.index or not entity.is_redactable:
            continue
        if entity.is_region:
            regions.extend(entity.bboxes)
        elif entity.in_page_text:
            spans.append((*_whole_words(page, *entity.span), entity_label(entity)))
    spans.extend(
        (word.start, word.end, REGION_LABEL)
        for word in page.words
        if any(_touches(word.bbox, region) for region in regions)
    )
    merged: list[tuple[int, int, str]] = []
    for start, end, label in sorted(spans, key=lambda span: (span[0], -span[1])):
        if merged and start < merged[-1][1]:
            first_start, first_end, first_label = merged[-1]
            merged[-1] = (first_start, max(first_end, end), first_label)
        else:
            merged.append((start, end, label))
    return merged


def _whole_words(page: Page, start: int, end: int) -> tuple[int, int]:
    """Widen a span to the words it overlaps."""
    words = list(page.words_in_span(start, end))
    if not words:
        return start, end
    return min(start, *(word.start for word in words)), max(end, *(word.end for word in words))


def _touches(word: BBox, region: BBox) -> bool:
    """Whether a word's box and a region share any area."""
    return (
        word.x0 < region.x1 and region.x0 < word.x1 and word.y0 < region.y1 and region.y0 < word.y1
    )
