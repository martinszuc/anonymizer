"""Czech and Slovak birth number (rodné číslo) detection.

Format: `YYMMDD/XXX` (issued before 1954, no check digit) or `YYMMDD/XXXX`
(1954 onwards, last digit is a mod-11 check digit). The separator is optional.

The month field encodes more than the month: `+50` marks a female holder, and
`+20` (with `+70` for female) marks a number from an exhausted daily series,
used since 2004. Valid month fields are therefore 1-12, 21-32, 51-62 and 71-82.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from datetime import date

from anonymizer.core.detect.base import Match
from anonymizer.core.types import EntityType

# Optional whitespace is tolerated around the separator because OCR inserts it.
_PATTERN = re.compile(r"(?<![\d/])(\d{6})\s*/?\s*(\d{3,4})(?![\d/])")

_FEMALE_MONTH_OFFSET = 50
_EXTENDED_MONTH_OFFSET = 20
_CHECKSUM_MODULUS = 11
# Numbers issued from 1954 onwards carry a check digit; earlier ones have 9 digits.
_FIRST_CHECKSUM_YEAR = 1954


def _normalized_month(month_field: int) -> int:
    """Strip the female and exhausted-series offsets from a month field."""
    month = month_field
    if month > _FEMALE_MONTH_OFFSET:
        month -= _FEMALE_MONTH_OFFSET
    if month > _EXTENDED_MONTH_OFFSET:
        month -= _EXTENDED_MONTH_OFFSET
    return month


def _birth_date(digits: str) -> date | None:
    """Return the encoded birth date, or `None` if the fields are not a real date."""
    year_field = int(digits[0:2])
    month = _normalized_month(int(digits[2:4]))
    day = int(digits[4:6])
    # Two digits cannot distinguish centuries on their own: a 10-digit number
    # belongs to 1954-2053, a 9-digit one to 1900-1953.
    year = 1900 + year_field
    if len(digits) == 10 and year < _FIRST_CHECKSUM_YEAR:
        year += 100
    try:
        return date(year, month, day)
    except ValueError:
        return None


def is_valid_birth_number(value: str) -> bool:
    """Check a birth number's format, encoded date and check digit.

    Args:
        value: Candidate string; separators and surrounding whitespace are ignored.

    Returns:
        `True` if the value is a structurally valid Czech or Slovak birth number.
    """
    digits = re.sub(r"[\s/]", "", value)
    if not digits.isdigit() or len(digits) not in {9, 10}:
        return False
    birth_date = _birth_date(digits)
    if birth_date is None:
        return False
    if len(digits) == 9:
        # The nine-digit form was only issued before the check digit was introduced.
        return birth_date.year < _FIRST_CHECKSUM_YEAR
    remainder = int(digits[:9]) % _CHECKSUM_MODULUS
    check_digit = int(digits[9])
    # Until 1985 a remainder of 10 was recorded as a check digit of 0.
    expected = 0 if remainder == 10 else remainder
    return check_digit == expected


def find_birth_numbers(text: str) -> Iterator[Match]:
    """Yield the valid birth numbers in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per valid birth number, in order of appearance.
    """
    for found in _PATTERN.finditer(text):
        value = found.group(0)
        if is_valid_birth_number(value):
            yield Match(
                type=EntityType.BIRTH_NUMBER,
                start=found.start(),
                end=found.end(),
                text=value,
            )
