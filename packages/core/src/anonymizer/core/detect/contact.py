"""Email address and telephone number detection.

Neither pattern implements its full specification. An RFC 5322 address parser
accepts constructs that never occur in documents, and phone numbers are written
too freely to be parsed strictly; the patterns aim for the shapes that appear in
real paperwork and accept OCR spacing. `find_ocr_emails` additionally accepts
the space an OCR reader puts after a period inside an address; it runs on
pages read by OCR only.

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

# PP-OCR recognizers put a space after every period, inside an address too
# (`tereza. prochazkova@example. com`). A space is accepted only after a period
# and before a lowercase letter or digit, so a following capitalised sentence is
# not taken in; a text layer's space is real, so this runs on OCR pages only.
# The lookbehind refuses to start inside any word, diacritics included.
_OCR_SPLIT = r"(?<=\.) (?=[a-z0-9])"
_OCR_EMAIL_PATTERN = re.compile(
    r"(?<![\w.%+\-])"
    rf"[A-Za-z0-9._%+\-]+(?:{_OCR_SPLIT}[A-Za-z0-9._%+\-]+)*"
    r"@"
    rf"[A-Za-z0-9\-]+(?:\.(?:{_OCR_SPLIT})?[A-Za-z0-9\-]+)*"
    rf"\.(?:{_OCR_SPLIT})?[A-Za-z]{{2,}}"
    r"(?![A-Za-z0-9\-])"
)

# Nine digits, conventionally in groups of three. The country code 420 / 421 may
# be written with `+`, with `00`, or bare (OCR drops the plus); a Slovak domestic
# number starts with a trunk `0` instead (`0918 446 150`). The prefixes are part
# of the pattern so a longer number is never matched only in part.
_PHONE_PATTERN = re.compile(
    r"(?<![\d+])"
    r"(?:(?:(?:\+|00)\s?)?42[01]\s?|0)?"
    r"\d{3}\s?\d{3}\s?\d{3}"
    r"(?!\d)"
)


def find_emails(text: str) -> Iterator[Match]:
    """Yield the email addresses in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per address, in order of appearance.
    """
    for found in _EMAIL_PATTERN.finditer(text):
        yield Match.from_regex(found, EntityType.EMAIL)


def find_ocr_emails(text: str) -> Iterator[Match]:
    """Yield the email addresses in OCR output, joined across a space after a period.

    Args:
        text: Text read by OCR.

    Yields:
        One match per address, in order of appearance, spaces included.
    """
    for found in _OCR_EMAIL_PATTERN.finditer(text):
        yield Match.from_regex(found, EntityType.EMAIL)


def find_czech_phone_numbers(text: str) -> Iterator[Match]:
    """Yield the Czech and Slovak telephone numbers in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per number, in order of appearance.
    """
    for found in _PHONE_PATTERN.finditer(text):
        yield Match.from_regex(found, EntityType.PHONE)


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
        yield Match.from_regex(found, EntityType.PHONE)
