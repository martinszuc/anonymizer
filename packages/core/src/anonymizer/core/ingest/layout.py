"""Reading-order page text built from positioned words.

The text layer and OCR both deliver words numbered by block and line; this
module joins them into `Page.text` and records each word's offsets into it, so
detection sees the same layout whichever reader produced the words.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

from anonymizer.core.ingest.normalize import normalize_text
from anonymizer.core.types import BBox, Word

_WORD_SEPARATOR = " "
_LINE_SEPARATOR = "\n"
_BLOCK_SEPARATOR = "\n\n"


class PlacedWord(NamedTuple):
    """A word as a reader found it: its text, its box and where it sits in the layout."""

    text: str
    bbox: BBox
    block: int
    line: int


def assemble(words: Iterable[PlacedWord]) -> tuple[str, list[Word]]:
    """Join words given in reading order into page text.

    Words are NFC-normalized first, and a word left empty is skipped, so
    offsets always refer to normalized text.

    Args:
        words: Words in reading order.

    Returns:
        The page text and its words, each with offsets into that text.
    """
    parts: list[str] = []
    placed: list[Word] = []
    cursor = 0
    previous: PlacedWord | None = None
    for word in words:
        text = normalize_text(word.text)
        if not text:
            continue
        separator = _separator_between(previous, word)
        parts.append(separator)
        start = cursor + len(separator)
        parts.append(text)
        cursor = start + len(text)
        placed.append(Word(text=text, bbox=word.bbox, start=start, end=cursor))
        previous = word
    return "".join(parts), placed


def _separator_between(previous: PlacedWord | None, word: PlacedWord) -> str:
    """Whitespace to insert before a word, given the previous word's position."""
    if previous is None:
        return ""
    if word.block != previous.block:
        return _BLOCK_SEPARATOR
    if word.line != previous.line:
        return _LINE_SEPARATOR
    return _WORD_SEPARATOR
