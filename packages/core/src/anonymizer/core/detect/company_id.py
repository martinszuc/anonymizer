"""Czech and Slovak company identifier (IČO) detection.

An IČO is eight digits whose last digit is a weighted mod-11 check digit. That
check alone accepts roughly one in eleven eight-digit numbers, which on an
invoice full of order and variable-symbol numbers is far too weak, so a match
additionally requires a nearby `IČO` / `IČ` label.

A sole trader's IČO identifies a natural person, which is why this is treated as
personal data rather than public company metadata.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from anonymizer.core.detect.base import Match
from anonymizer.core.types import EntityType

# The label carries the evidence; diacritics are optional because OCR drops them.
_PATTERN = re.compile(r"(I[CČ]O?)\s*[:.]?\s*(\d{8})(?!\d)", re.IGNORECASE)

_WEIGHT_COUNT = 7
_CHECKSUM_MODULUS = 11


def is_valid_company_id(value: str) -> bool:
    """Check an IČO's length and weighted mod-11 check digit.

    Args:
        value: Candidate string; whitespace is ignored.

    Returns:
        `True` if the value is a structurally valid IČO.
    """
    digits = re.sub(r"\s", "", value)
    if not digits.isdigit() or len(digits) != _WEIGHT_COUNT + 1:
        return False
    weighted = sum(
        int(digit) * (_WEIGHT_COUNT + 1 - position)
        for position, digit in enumerate(digits[:_WEIGHT_COUNT])
    )
    remainder = weighted % _CHECKSUM_MODULUS
    if remainder == 0:
        expected = 1
    elif remainder == 1:
        expected = 0
    else:
        expected = _CHECKSUM_MODULUS - remainder
    return int(digits[_WEIGHT_COUNT]) == expected


def find_company_ids(text: str) -> Iterator[Match]:
    """Yield the labelled IČO values in a text.

    Only the digits are reported, not the label, so redaction leaves the field
    name readable.

    Args:
        text: Text to scan.

    Yields:
        One match per valid IČO, in order of appearance.
    """
    for found in _PATTERN.finditer(text):
        digits = found.group(2)
        if is_valid_company_id(digits):
            yield Match(
                type=EntityType.COMPANY_ID,
                start=found.start(2),
                end=found.end(2),
                text=digits,
            )
