"""Checksum-bearing values planted in the benchmark documents are valid.

Each check is written here from the published rule, not taken from the
detectors: a detector that rejects a planted value must show up as a miss,
and a guessed value that fails its own checksum would hide that miss.
"""

import re

import pytest
from anonymizer.core.types import EntityType

from benchmark.spec import GoldItem, load_documents

# Rodné číslo: ten digits from 1954 on, the whole number divisible by 11
# (or remainder 10 with a final 0, issued until 1985).
BIRTH_NUMBER = re.compile(r"(\d{2})(\d{2})(\d{2})/?(\d{4})")
# Bank account weights for the prefix and the base, right-aligned (ČNB decree 169/2011).
PREFIX_WEIGHTS = (10, 5, 8, 4, 2, 1)
BASE_WEIGHTS = (6, 3, 7, 9, 10, 5, 8, 4, 2, 1)
IBAN_LENGTHS = {"CZ": 24, "SK": 24, "DE": 22}


def birth_number_is_valid(value: str) -> bool:
    match = BIRTH_NUMBER.fullmatch(value.replace(" ", ""))
    if not match:
        return False
    month = int(match.group(2))
    # +50 for a woman, +20 for an extended daily series (since 2004).
    month_valid = any(1 <= month - offset <= 12 for offset in (0, 20, 50, 70))
    digits = "".join(match.groups())
    remainder = int(digits[:9]) % 11
    check = int(digits[9])
    return month_valid and (remainder == check or (remainder == 10 and check == 0))


def weighted_mod11(digits: str, weights: tuple[int, ...]) -> bool:
    padded = digits.rjust(len(weights), "0")
    return sum(int(d) * w for d, w in zip(padded, weights, strict=True)) % 11 == 0


def bank_account_is_valid(value: str) -> bool:
    number, _, bank_code = value.replace(" ", "").partition("/")
    prefix, _, base = number.rpartition("-")
    return (
        len(bank_code) == 4
        and len(prefix) <= 6
        and 2 <= len(base) <= 10
        and weighted_mod11(prefix, PREFIX_WEIGHTS)
        and weighted_mod11(base, BASE_WEIGHTS)
    )


def iban_is_valid(value: str) -> bool:
    compact = value.replace(" ", "")
    if len(compact) != IBAN_LENGTHS.get(compact[:2], -1):
        return False
    rearranged = compact[4:] + compact[:4]
    return int("".join(str(int(char, 36)) for char in rearranged)) % 97 == 1


def company_id_is_valid(value: str) -> bool:
    if not re.fullmatch(r"\d{8}", value):
        return False
    remainder = sum(int(d) * w for d, w in zip(value, range(8, 1, -1), strict=False)) % 11
    return int(value[7]) == (11 - remainder) % 10


def luhn_is_valid(value: str) -> bool:
    digits = [int(d) for d in value if d.isdigit()]
    total = sum(
        d if i % 2 == 0 else (d * 2 - 9 if d > 4 else d * 2) for i, d in enumerate(digits[::-1])
    )
    return len(digits) >= 12 and total % 10 == 0


CHECKS = {
    EntityType.BIRTH_NUMBER: birth_number_is_valid,
    EntityType.BANK_ACCOUNT: bank_account_is_valid,
    EntityType.IBAN: iban_is_valid,
    EntityType.COMPANY_ID: company_id_is_valid,
    EntityType.CREDIT_CARD: luhn_is_valid,
}

PLANTED = [
    pytest.param(item, id=f"{spec.name}:{item.type}:{item.text}")
    for spec in load_documents()
    for item in spec.gold
    if item.type in CHECKS
]


@pytest.mark.parametrize("item", PLANTED)
def test_planted_value_passes_its_checksum(item: GoldItem):
    assert CHECKS[item.type](item.text)


@pytest.mark.parametrize(
    ("check", "valid", "invalid"),
    [
        (birth_number_is_valid, "880612/1005", "880612/1006"),
        (bank_account_is_valid, "19-2000145399/0800", "19-2000145390/0800"),
        (iban_is_valid, "CZ65 0800 0000 1920 0014 5399", "CZ65 0800 0000 1920 0014 5390"),
        (company_id_is_valid, "73120456", "73120457"),
        (luhn_is_valid, "4111 1111 1111 1111", "4111 1111 1111 1112"),
    ],
)
def test_checks_tell_valid_from_invalid(check, valid, invalid):
    assert check(valid)
    assert not check(invalid)
