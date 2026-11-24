"""Locating ground-truth spans in OCR text by aligning the two texts character by character.

A phone photo's perspective and page edge break the box mapping a flat scan
allows (`ocr_score.item_locations`), so a planted item is placed in what OCR
read by text alone, as `experiments/photo-rules.md` fixes it:

- Both texts are NFC-normalized and every whitespace run counts as one space,
  edges stripped, as for the character error rate (`ocr_score.text_errors`).
- Levenshtein edit operations (rapidfuzz) align them. A ground-truth character
  kept or substituted is aligned to one OCR character; a deleted one to none;
  an inserted OCR character (junk at the page edge, table lines) belongs to no
  ground-truth character.
- A span's located span runs from the OCR character aligned to its first
  aligned character to the one aligned to its last, so junk OCR read inside
  the item belongs to it and junk around it does not. Only characters that are
  not whitespace count: a line break is layout, and an item whose only aligned
  character would be a space has nothing of it read.
- A span none of whose characters is aligned is **not read** (`None`).

Offsets in and out are those of the texts as given, before normalization, so
a located span indexes the OCR page text directly. NFC is applied per
character cluster (a base character and the combining marks after it), which
keeps every output character's place in the input; it equals NFC of the whole
text for the Latin scripts the documents use.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

from rapidfuzz.distance import Levenshtein

Span = tuple[int, int]
"""Start and end offset (one past the last character) in a text."""


@dataclass(frozen=True)
class SpacedText:
    """A text NFC-normalized with whitespace runs as one space, and where each character came from.

    Attributes:
        text: The normalized text.
        starts: Per character of `text`, the offset in the original where it begins.
        ends: Per character of `text`, the offset in the original one past where it ends.
    """

    text: str
    starts: tuple[int, ...]
    ends: tuple[int, ...]


def spaced(text: str) -> SpacedText:
    """Normalize a text as alignment compares it, keeping each character's original offsets."""
    characters: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    pending_space: tuple[int, int] | None = None
    for start, end in _clusters(text):
        cluster = text[start:end]
        if cluster.isspace():
            run_start = pending_space[0] if pending_space else start
            pending_space = (run_start, end)
            continue
        if pending_space is not None and characters:
            characters.append(" ")
            starts.append(pending_space[0])
            ends.append(pending_space[1])
        pending_space = None
        for character in unicodedata.normalize("NFC", cluster):
            characters.append(character)
            starts.append(start)
            ends.append(end)
    return SpacedText("".join(characters), tuple(starts), tuple(ends))


def _clusters(text: str) -> list[Span]:
    """Split a text into a base character and the combining marks following it."""
    clusters: list[Span] = []
    for index, character in enumerate(text):
        if clusters and unicodedata.combining(character) and not text[index - 1].isspace():
            clusters[-1] = (clusters[-1][0], index + 1)
        else:
            clusters.append((index, index + 1))
    return clusters


def aligned_characters(source: str, target: str) -> list[int | None]:
    """Return, per character of `source`, the index of the `target` character aligned to it.

    Kept and substituted characters are aligned; deleted ones get `None`.
    """
    mapping: list[int | None] = [None] * len(source)
    source_index = target_index = 0
    for operation in Levenshtein.editops(source, target):
        # Characters between two edit operations are equal and aligned in turn.
        while source_index < operation.src_pos and target_index < operation.dest_pos:
            mapping[source_index] = target_index
            source_index += 1
            target_index += 1
        if operation.tag == "replace":
            mapping[source_index] = target_index
            source_index += 1
            target_index += 1
        elif operation.tag == "delete":
            source_index += 1
        else:
            target_index += 1
    while source_index < len(source) and target_index < len(target):
        mapping[source_index] = target_index
        source_index += 1
        target_index += 1
    return mapping


def locate(truth_text: str, spans: Sequence[Span], ocr_text: str) -> list[Span | None]:
    """Locate spans of a page's ground-truth text in what OCR read of the page.

    Args:
        truth_text: The page's ground-truth text (the born-digital text layer).
        spans: Spans of `truth_text` to locate, such as planted items.
        ocr_text: The page text OCR produced.

    Returns:
        Per span, in order, its located span in `ocr_text`, or `None` when no
        character of it is aligned to an OCR character (not read).
    """
    truth, read = spaced(truth_text), spaced(ocr_text)
    mapping = aligned_characters(truth.text, read.text)
    located: list[Span | None] = []
    for start, end in spans:
        aligned = [
            target
            for index, target in enumerate(mapping)
            if target is not None
            and start <= truth.starts[index]
            and truth.ends[index] <= end
            and not truth.text[index].isspace()
        ]
        # A letter substituted by a space reads as nothing at the span's edge.
        while aligned and read.text[aligned[0]].isspace():
            aligned.pop(0)
        while aligned and read.text[aligned[-1]].isspace():
            aligned.pop()
        if not aligned:
            located.append(None)
            continue
        located.append((read.starts[aligned[0]], read.ends[aligned[-1]]))
    return located
