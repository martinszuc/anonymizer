"""Czech and Slovak bank account number detection.

Format: `[prefix-]base/bank code`, where the prefix has up to 6 digits, the base
up to 10 and the bank code exactly 4. Prefix and base each carry their own
weighted mod-11 checksum (ČNB decree 169/2011, the same algorithm in Slovakia).

The bank code is only checked for shape. Validating it against the ČNB register
would raise precision but cost recall whenever the register is out of date, and
recall matters more here: a missed account number leaks.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from anonymizer.core.detect.base import Match
from anonymizer.core.types import EntityType

_PATTERN = re.compile(
    r"(?<![\d-])"
    r"(?:(\d{1,6})\s*-\s*)?"  # optional prefix
    r"(\d{2,10})"  # base
    r"\s*/\s*"
    r"(\d{4})"  # bank code
    r"(?!\d)"
)

_PREFIX_WEIGHTS = (10, 5, 8, 4, 2, 1)
_BASE_WEIGHTS = (6, 3, 7, 9, 10, 5, 8, 4, 2, 1)
_CHECKSUM_MODULUS = 11


def _weighted_sum_is_valid(digits: str, weights: tuple[int, ...]) -> bool:
    """Whether the right-aligned digits satisfy the weighted mod-11 rule."""
    padded = digits.rjust(len(weights), "0")
    total = sum(int(digit) * weight for digit, weight in zip(padded, weights, strict=True))
    return total % _CHECKSUM_MODULUS == 0


def is_valid_account_number(base: str, prefix: str | None = None) -> bool:
    """Check the weighted mod-11 checksums of an account number.

    Args:
        base: Base part, 2 to 10 digits.
        prefix: Optional prefix part, 1 to 6 digits.

    Returns:
        `True` if every present part satisfies its checksum.
    """
    if not base.isdigit() or not 2 <= len(base) <= len(_BASE_WEIGHTS):
        return False
    if int(base) == 0:
        return False
    if not _weighted_sum_is_valid(base, _BASE_WEIGHTS):
        return False
    if prefix is None:
        return True
    if not prefix.isdigit() or not 1 <= len(prefix) <= len(_PREFIX_WEIGHTS):
        return False
    return _weighted_sum_is_valid(prefix, _PREFIX_WEIGHTS)


def find_account_numbers(text: str) -> Iterator[Match]:
    """Yield the valid Czech and Slovak account numbers in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per valid account number, in order of appearance.
    """
    for found in _PATTERN.finditer(text):
        prefix, base, _bank_code = found.groups()
        if is_valid_account_number(base, prefix):
            yield Match(
                type=EntityType.BANK_ACCOUNT,
                start=found.start(),
                end=found.end(),
                text=found.group(0),
            )
