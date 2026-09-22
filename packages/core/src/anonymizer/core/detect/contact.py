"""Email address and telephone number detection.

Neither pattern implements its full specification. An RFC 5322 address parser
accepts constructs that never occur in documents, and phone numbers are written
too freely to be parsed strictly; both patterns aim for the shapes that appear
in Czech and Slovak paperwork and accept OCR spacing.
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
# groups of three, with an optional +420 / +421 or 00420 / 00421 country prefix.
_PHONE_PATTERN = re.compile(
    r"(?<![\d+])"
    r"(?:(?:\+|00)\s?42[01]\s?)?"
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


def find_phone_numbers(text: str) -> Iterator[Match]:
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
