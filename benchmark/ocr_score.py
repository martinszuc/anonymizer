"""Scoring OCR on scanned variants against the born-digital ground truth.

- **Character error rate.** Edit distance between what OCR read and the
  original's page text, over the original's length; whitespace runs count as
  one space, since line breaks are layout, not reading errors.
- **Diacritic error rate.** Of the original's letters carrying a diacritic
  (č, ř, ů, ...), the share not read exactly, from the same alignment. Czech
  names and addresses depend on these letters, and a detector matching a
  name or a label fails on a misread one.
- **Word boxes.** A ground-truth word is *boxed* when one OCR box overlaps
  it by intersection over union of at least one half. *Ink under boxes* is
  the share of the words' printed pixels inside OCR boxes, and a word is
  *partly outside* when some of its ink lies outside every box: redacted
  from OCR boxes, such a word would leave that ink in the picture. Ink, not
  the font's box, is the measure: OCR boxes hug the ink, while the original's
  word boxes span the font's full height.
- **Locating items.** A planted item is placed in the OCR text by where it is
  printed: the OCR words whose box centre lies in one of its ground-truth
  word boxes. Where they hold the item's exact words, those are its span (so
  a label read glued to a value stays outside it); otherwise the span runs
  from the first such word to the last, less punctuation at its edges the
  item does not have, so an item read split or misread (`jan.
  novak@example. com,`) is still located and an entity must cover all of it
  to find it. An item OCR read nothing of is missed.
- **Residue.** After redaction the ink inside each planted item's ground-truth
  word boxes is counted in the output picture and compared with the scan. An
  item is *readable* when a word keeps at least half of its ink, *partly
  readable* when one keeps more than a trace. Counting pixels needs no reader,
  so the measure is the same whichever engine is scored.
"""

from __future__ import annotations

import unicodedata
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from anonymizer.core.types import BBox, Page
from rapidfuzz.distance import Levenshtein

from benchmark.scans import TruthPage, covers, ink_inside, ink_under_boxes
from benchmark.score import Location, words_pattern
from benchmark.spec import GoldItem

WordLocations = list[tuple[int, list[int]] | None]
"""Per item, its ground-truth page and the indices of its words there, or None."""

BOXED_IOU = 0.5
# Below this share of its ink under OCR boxes, a word's ink is partly outside them.
FULLY_COVERED = 0.99
READABLE_SHARE = 0.5
TRACE_SHARE = 0.05


def text_errors(truth: Sequence[TruthPage], read: Sequence[Page]) -> dict[str, int]:
    """Count character and diacritic errors over a document's pages.

    Returns:
        `characters` and `character_errors`, `diacritics` and
        `diacritic_errors`, summed over pages, so rates pool by length.
    """
    counts: Counter[str] = Counter()
    for expected, page in zip(truth, read, strict=True):
        original, reading = _spaced(expected.text), _spaced(page.text)
        counts["characters"] += len(original)
        counts["character_errors"] += Levenshtein.distance(original, reading)
        marked = [index for index, character in enumerate(original) if _has_diacritic(character)]
        correct = _exactly_read(original, reading)
        counts["diacritics"] += len(marked)
        counts["diacritic_errors"] += sum(1 for index in marked if index not in correct)
    return dict(counts)


def box_scores(scan: Path, truth: Sequence[TruthPage], read: Sequence[Page]) -> dict[str, int]:
    """Score OCR's word boxes against the ground truth over a document.

    Returns:
        `words`, `boxed` (matched by one box), `ink` and `ink_covered` (the
        words' ink pixels, and those inside OCR boxes), and `partly_outside`
        (words with ink outside every box).
    """
    counts: Counter[str] = Counter()
    for page_index, (expected, page) in enumerate(zip(truth, read, strict=True)):
        boxes = [word.bbox for word in page.words]
        for word in expected.words:
            counts["words"] += 1
            counts["boxed"] += any(_iou(word.bbox, box) >= BOXED_IOU for box in boxes)
            ink, covered = ink_under_boxes(scan, page_index, word.corners, boxes)
            counts["ink"] += ink
            counts["ink_covered"] += covered
            counts["partly_outside"] += covered < ink * FULLY_COVERED
    return dict(counts)


def item_residue(
    scan: Path,
    redacted: Path,
    truth: Sequence[TruthPage],
    items: Sequence[GoldItem],
    located: WordLocations | None = None,
) -> list[float]:
    """Return, per planted page item, the largest share of a word's ink left after redaction.

    An item not found in the ground truth (it should always be) counts as
    fully readable, so a fault in the harness cannot pass as a safe document.
    `located` gives each item's words; by default they are found by its text.
    """
    locations = located if located is not None else _locate(truth, items)
    shares: list[float] = []
    for location in locations:
        if location is None:
            shares.append(1.0)
            continue
        page_index, word_indices = location
        page = truth[page_index]
        left = 0.0
        for index in word_indices:
            corners = page.words[index].corners
            before = ink_inside(scan, page_index, corners)
            if before:
                left = max(left, ink_inside(redacted, page_index, corners) / before)
        shares.append(left)
    return shares


def item_locations(
    truth: Sequence[TruthPage],
    read: Sequence[Page],
    items: Sequence[GoldItem],
    located: WordLocations | None = None,
) -> dict[int, Location | None]:
    """Locate each planted page item in the OCR text by its ground-truth boxes.

    Args:
        truth: The ground truth, one page per scanned page.
        read: The pages as OCR read them.
        items: The planted page items.
        located: Each item's ground-truth words; by default found by its text.

    Returns:
        Per item index, its page and span in that page's text, or None when
        no OCR word lies on it.
    """
    locations: dict[int, Location | None] = {}
    words = located if located is not None else _locate(truth, items)
    for index, location in enumerate(words):
        if location is None:
            locations[index] = None
            continue
        page_index, word_indices = location
        page = read[page_index]
        boxes = [truth[page_index].words[word].corners for word in word_indices]
        on_item = [
            word
            for word in page.words
            if any(covers(corners, *_centre(word.bbox)) for corners in boxes)
        ]
        if not on_item:
            locations[index] = None
            continue
        start, end = min(word.start for word in on_item), max(word.end for word in on_item)
        exact = [
            (match.start(), match.end())
            for match in words_pattern(items[index].text, whole_words=True).finditer(page.text)
            if match.start() < end and start < match.end()
        ]
        if exact:
            start, end = max(exact, key=lambda span: min(span[1], end) - max(span[0], start))
        else:
            start, end = _trimmed(page.text, start, end, items[index].text)
        locations[index] = (page_index, start, end)
    return locations


def residue_counts(shares: Sequence[float]) -> dict[str, int]:
    """Count readable and partly readable items from their ink shares."""
    return {
        "readable_after": sum(share >= READABLE_SHARE for share in shares),
        "partly_after": sum(TRACE_SHARE < share < READABLE_SHARE for share in shares),
    }


def _spaced(text: str) -> str:
    return " ".join(text.split())


def _has_diacritic(character: str) -> bool:
    decomposed = unicodedata.normalize("NFD", character)
    return len(decomposed) > 1 and any(unicodedata.combining(mark) for mark in decomposed[1:])


def _exactly_read(original: str, reading: str) -> set[int]:
    """Return the offsets of the original that the alignment matches unchanged."""
    correct: set[int] = set()
    for opcode in Levenshtein.opcodes(original, reading):
        if opcode.tag == "equal":
            correct.update(range(opcode.src_start, opcode.src_end))
    return correct


def _locate(
    truth: Sequence[TruthPage], items: Sequence[GoldItem]
) -> list[tuple[int, list[int]] | None]:
    """Find each item's words; the k-th item with a text gets its k-th occurrence."""
    seen: Counter[str] = Counter()
    found: list[tuple[int, list[int]] | None] = []
    for item in items:
        pattern = words_pattern(item.text, whole_words=True)
        occurrences = [
            (page_index, match.start(), match.end())
            for page_index, page in enumerate(truth)
            for match in pattern.finditer(page.text)
        ]
        nth = seen[item.text]
        seen[item.text] += 1
        if nth >= len(occurrences):
            found.append(None)
            continue
        page_index, start, end = occurrences[nth]
        page = truth[page_index]
        indices = [
            index
            for index, (word, word_start) in enumerate(zip(page.words, page.starts, strict=True))
            if word_start < end and start < word_start + len(word.text)
        ]
        found.append((page_index, indices))
    return found


def _trimmed(text: str, start: int, end: int, item: str) -> tuple[int, int]:
    """Drop punctuation OCR read into the edge words (`com,`) that the item does not have."""
    while end - start > 1 and not text[start].isalnum() and text[start] != item[0]:
        start += 1
    while end - start > 1 and not text[end - 1].isalnum() and text[end - 1] != item[-1]:
        end -= 1
    return start, end


def _centre(box: BBox) -> tuple[float, float]:
    return (box.x0 + box.x1) / 2, (box.y0 + box.y1) / 2


def _area(box: BBox) -> float:
    return max(box.width * box.height, 1e-9)


def _intersection(first: BBox, second: BBox) -> float:
    width = min(first.x1, second.x1) - max(first.x0, second.x0)
    height = min(first.y1, second.y1) - max(first.y0, second.y0)
    return max(width, 0.0) * max(height, 0.0)


def _iou(first: BBox, second: BBox) -> float:
    shared = _intersection(first, second)
    return shared / (_area(first) + _area(second) - shared)
