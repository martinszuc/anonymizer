"""Payment card number detection.

Card numbers are validated with the Luhn checksum (ISO/IEC 7812, mod 10) and an
issuer prefix table. Luhn alone accepts one in ten random digit strings of the
right length, so the prefix check is what makes this usable on documents full of
invoice and order numbers.

The check is language-independent: a card number looks the same in every locale.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from anonymizer.core.detect.base import Match
from anonymizer.core.types import EntityType

# Groups of digits separated by a single space or dash, 13-19 digits in total.
_PATTERN = re.compile(r"(?<![\d-])(\d(?:[ -]?\d){12,18})(?![\d-])")

# Issuer prefixes and permitted lengths, narrow enough to exclude arbitrary
# numbers that happen to satisfy Luhn.
_ISSUERS: tuple[tuple[tuple[str, ...], frozenset[int]], ...] = (
    (("4",), frozenset({13, 16, 19})),  # Visa
    (tuple(str(prefix) for prefix in range(51, 56)), frozenset({16})),  # Mastercard
    (tuple(str(prefix) for prefix in range(2221, 2721)), frozenset({16})),  # Mastercard 2-series
    (("34", "37"), frozenset({15})),  # American Express
    (("6011", "65"), frozenset({16, 19})),  # Discover
    (tuple(str(prefix) for prefix in range(644, 650)), frozenset({16, 19})),  # Discover
    (("36", "38", "39"), frozenset({14, 16, 19})),  # Diners Club
    (tuple(str(prefix) for prefix in range(300, 306)), frozenset({14, 16, 19})),  # Diners Club
    (tuple(str(prefix) for prefix in range(3528, 3590)), frozenset({16, 17, 18, 19})),  # JCB
    (("62",), frozenset({16, 17, 18, 19})),  # UnionPay
)


def _digits(value: str) -> str:
    """Strip grouping separators from a card number candidate."""
    return re.sub(r"[ -]", "", value)


def _matches_issuer(digits: str) -> bool:
    """Whether the number's prefix and length match a known issuer range."""
    return any(
        len(digits) in lengths and digits.startswith(prefixes) for prefixes, lengths in _ISSUERS
    )


def passes_luhn(digits: str) -> bool:
    """Check the Luhn (mod 10) checksum.

    Args:
        digits: Digits only, no separators.

    Returns:
        `True` if the check digit is consistent with the rest of the number.
    """
    if not digits.isdigit():
        return False
    total = 0
    for position, digit in enumerate(reversed(digits)):
        value = int(digit)
        if position % 2:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def is_valid_card_number(value: str) -> bool:
    """Check a payment card number's issuer prefix, length and Luhn checksum.

    Args:
        value: Candidate string; spaces and dashes are ignored.

    Returns:
        `True` if the value is a plausible payment card number.
    """
    digits = _digits(value)
    return _matches_issuer(digits) and passes_luhn(digits)


def _longest_valid_window(candidate: str) -> tuple[int, int] | None:
    """Offsets of the longest group-aligned stretch of a candidate that is a card number.

    The pattern matches greedily, so a candidate can absorb digits that belong
    to the text around the card, such as an expiry date or a security code
    after it, or a number before it. Groups are dropped from either end
    instead of rejecting the whole candidate.
    """
    groups = [(group.start(), group.end()) for group in re.finditer(r"\d+", candidate)]
    for width in range(len(groups), 0, -1):
        for first in range(len(groups) - width + 1):
            start, end = groups[first][0], groups[first + width - 1][1]
            if is_valid_card_number(candidate[start:end]):
                return start, end
    return None


def find_card_numbers(text: str) -> Iterator[Match]:
    """Yield the payment card numbers in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per valid card number, in order of appearance.
    """
    for found in _PATTERN.finditer(text):
        window = _longest_valid_window(found[1])
        if window is None:
            continue
        offset = found.start(1)
        yield Match(
            EntityType.CREDIT_CARD,
            offset + window[0],
            offset + window[1],
            found[1][window[0] : window[1]],
        )
