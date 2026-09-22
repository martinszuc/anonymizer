"""IBAN detection.

An IBAN is validated by moving its first four characters to the end, mapping
letters to numbers (`A` = 10 … `Z` = 35) and checking that the result is
congruent to 1 modulo 97 (ISO 13616 / ISO 7064 MOD-97-10).

Czech and Slovak IBANs additionally embed a domestic account number, whose own
weighted mod-11 checksums are verified through `bank_account`.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from anonymizer.core.detect.bank_account import is_valid_account_number
from anonymizer.core.detect.base import Match
from anonymizer.core.types import EntityType

# Grouping in fours is conventional but not guaranteed, so any single-space layout
# is accepted. Only spaces separate groups: a line break ends the candidate.
_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z]{2}\d{2}(?:[ ]?[A-Za-z0-9]){11,30})(?![A-Za-z0-9])"
)

_MOD_97_REMAINDER = 1
_MIN_LENGTH = 15
_MAX_LENGTH = 34
_ALPHABET_OFFSET = ord("A") - 10

# Fixed lengths for the countries this tool targets; others are only length-bounded.
_KNOWN_LENGTHS = {"CZ": 24, "SK": 24, "AT": 20, "DE": 22, "PL": 28, "HU": 28}

_CZSK_BANK_CODE_DIGITS = 4
_CZSK_PREFIX_DIGITS = 6


def _to_numeric(iban: str) -> str:
    """Rearrange an IBAN and map its letters to digits for the mod-97 check."""
    rotated = iban[4:] + iban[:4]
    return "".join(
        str(ord(char) - _ALPHABET_OFFSET) if char.isalpha() else char for char in rotated
    )


def _domestic_part_is_valid(iban: str) -> bool:
    """Whether a CZ/SK IBAN's embedded account number passes its mod-11 checksums."""
    bban = iban[4:]
    prefix = bban[_CZSK_BANK_CODE_DIGITS : _CZSK_BANK_CODE_DIGITS + _CZSK_PREFIX_DIGITS]
    base = bban[_CZSK_BANK_CODE_DIGITS + _CZSK_PREFIX_DIGITS :]
    # Leading zeros are padding, not part of the account number.
    prefix = prefix.lstrip("0")
    base = base.lstrip("0")
    return is_valid_account_number(base, prefix or None)


def normalize_iban(value: str) -> str:
    """Strip separators and upper-case an IBAN candidate.

    Args:
        value: Candidate string.

    Returns:
        The value without whitespace, in upper case.
    """
    return re.sub(r"\s", "", value).upper()


def is_valid_iban(value: str) -> bool:
    """Check an IBAN's length, mod-97 checksum and, for CZ/SK, its account number.

    Args:
        value: Candidate string; whitespace and case are ignored.

    Returns:
        `True` if the value is a valid IBAN.
    """
    iban = normalize_iban(value)
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]+", iban):
        return False
    if not _MIN_LENGTH <= len(iban) <= _MAX_LENGTH:
        return False
    country = iban[:2]
    expected_length = _KNOWN_LENGTHS.get(country)
    if expected_length is not None and len(iban) != expected_length:
        return False
    if int(_to_numeric(iban)) % 97 != _MOD_97_REMAINDER:
        return False
    if country in {"CZ", "SK"}:
        return _domestic_part_is_valid(iban)
    return True


def _longest_valid_prefix(candidate: str) -> int | None:
    """Length of the longest space-aligned prefix of a candidate that is a valid IBAN.

    The pattern matches greedily, so a candidate can absorb the word that follows
    the IBAN. Trailing groups are dropped one at a time instead of rejecting the
    whole candidate.
    """
    groups = candidate.split(" ")
    for count in range(len(groups), 0, -1):
        prefix = " ".join(groups[:count])
        if is_valid_iban(prefix):
            return len(prefix)
    return None


def find_ibans(text: str) -> Iterator[Match]:
    """Yield the valid IBANs in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per valid IBAN, in order of appearance.
    """
    for found in _PATTERN.finditer(text):
        candidate = found.group(1)
        length = _longest_valid_prefix(candidate)
        if length is None:
            continue
        start = found.start(1)
        yield Match(
            type=EntityType.IBAN,
            start=start,
            end=start + length,
            text=candidate[:length],
        )
