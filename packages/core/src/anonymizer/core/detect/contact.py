"""Email address and telephone number detection.

Neither pattern implements its full specification. An RFC 5322 address parser
accepts constructs that never occur in documents, and phone numbers are written
too freely to be parsed strictly; the patterns aim for the shapes that appear in
real paperwork and accept OCR spacing.

Telephone numbers carry no checksum anywhere, so they are recognised by locale:
`find_czech_phone_numbers` for CZ/SK, `find_nanp_phone_numbers` for the North
American plan. Which ones run is decided by the configured language.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from anonymizer.core.detect.base import Match
from anonymizer.core.types import EntityType

_EMAIL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9._%+\-])"
    r"[A-Za-z0-9._%+\-]+"
    r"@"
    r"[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*"
    r"\.[A-Za-z]{2,}"
    r"(?![A-Za-z0-9\-])"
)

# Czech and Slovak subscriber numbers are nine digits, conventionally written in
# groups of three. The country code 420 / 421 may be written with `+`, with `00`,
# or bare, as OCR produces when it drops the plus. Slovak numbers written for
# domestic use start with a trunk `0` instead (`0918 446 150`). Without these
# prefixes a 12-digit number matched only its first nine digits, leaving the rest
# unredacted.
_PHONE_PATTERN = re.compile(
    r"(?<![\d+])"
    r"(?:(?:(?:\+|00)\s?)?42[01]\s?|0)?"
    r"\d{3}\s?\d{3}\s?\d{3}"
    r"(?!\d)"
)

_MIN_PHONE_DIGITS = 9


def find_emails(text: str) -> Iterator[Match]:
    """Yield the email addresses in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per address, in order of appearance.
    """
    for found in _EMAIL_PATTERN.finditer(text):
        yield Match(
            type=EntityType.EMAIL,
            start=found.start(),
            end=found.end(),
            text=found.group(0),
        )


def find_czech_phone_numbers(text: str) -> Iterator[Match]:
    """Yield the Czech and Slovak telephone numbers in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per number, in order of appearance.
    """
    for found in _PHONE_PATTERN.finditer(text):
        value = found.group(0)
        digits = re.sub(r"\D", "", value)
        if len(digits) < _MIN_PHONE_DIGITS:
            continue
        yield Match(
            type=EntityType.PHONE,
            start=found.start(),
            end=found.end(),
            text=value,
        )


# North American numbers are 3-3-4 with an optional country code. Separators and
# parentheses are all optional, which is why validation depends on them below.
_NANP_PATTERN = re.compile(
    r"(?<![\d+])"
    r"(?:\+?1[ .\-]?)?"
    r"(?:\(\d{3}\)|\d{3})"
    r"[ .\-]?\d{3}[ .\-]?\d{4}"
    r"(?!\d)"
)

_NANP_DIGITS = 10
_NANP_SEPARATORS = " .-()"


def _is_plausible_nanp(digits: str) -> bool:
    """Whether the ten digits satisfy the North American numbering plan's rules."""
    area, exchange = digits[:3], digits[3:6]
    # Area and exchange codes never start with 0 or 1, and N11 codes are services.
    return area[0] in "23456789" and exchange[0] in "23456789" and area[1:] != "11"


def find_nanp_phone_numbers(text: str) -> Iterator[Match]:
    """Yield the North American telephone numbers in a text.

    A number written with separators or parentheses is accepted on its layout
    alone, because the formatting is already strong evidence and a missed number
    leaks. A bare run of ten digits must additionally satisfy the numbering
    plan's structural rules, which is what keeps invoice and account numbers out.

    Args:
        text: Text to scan.

    Yields:
        One match per number, in order of appearance.
    """
    for found in _NANP_PATTERN.finditer(text):
        value = found.group(0)
        digits = re.sub(r"\D", "", value)
        if len(digits) == _NANP_DIGITS + 1 and digits.startswith("1"):
            digits = digits[1:]
        if len(digits) != _NANP_DIGITS:
            continue
        formatted = any(char in _NANP_SEPARATORS for char in value)
        if not formatted and not _is_plausible_nanp(digits):
            continue
        yield Match(
            type=EntityType.PHONE,
            start=found.start(),
            end=found.end(),
            text=value,
        )
