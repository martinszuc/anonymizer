"""Tests for Czech and Slovak birth number detection."""

import pytest
from anonymizer.core.detect.birth_number import find_birth_numbers, is_valid_birth_number

VALID = [
    "900101/0007",  # male, 1990
    "905101/1233",  # female (month +50)
    "902101/0075",  # exhausted daily series (month +20)
    "541231/0002",  # first year with a check digit
    "531231/1235",  # two-digit year 53 resolves to 2053 for ten digits
    "531231123",  # nine-digit form, issued before 1954
]

INVALID = [
    "900101/0008",  # check digit off by one
    "901301/0007",  # month 13
    "900132/0007",  # day 32
    "902901/0007",  # month 29 is not a valid offset month
    "900101123",  # nine digits but a post-1954 year
    "90010/0007",  # too few digits
    "900101/00007",  # too many digits
    "abc101/0007",
]


@pytest.mark.parametrize("value", VALID)
def test_accepts_valid_numbers(value):
    assert is_valid_birth_number(value)


@pytest.mark.parametrize("value", INVALID)
def test_rejects_invalid_numbers(value):
    assert not is_valid_birth_number(value)


@pytest.mark.parametrize(
    "variant",
    ["900101/0007", "9001010007", "900101 / 0007", "900101/ 0007", "900101 0007"],
)
def test_accepts_separator_variants(variant):
    assert is_valid_birth_number(variant)


def test_finds_number_in_running_text():
    text = "Pan Novák, r. č. 900101/0007, bydliště Brno."
    found = list(find_birth_numbers(text))
    assert len(found) == 1
    assert found[0].text == "900101/0007"
    assert text[found[0].start : found[0].end] == "900101/0007"


def test_skips_invalid_candidates_in_text():
    assert list(find_birth_numbers("faktura 900101/0008 ze dne 1. 1. 2026")) == []


def test_finds_several_numbers():
    text = "matka 905101/1233, otec 900101/0007"
    assert [match.text for match in find_birth_numbers(text)] == ["905101/1233", "900101/0007"]
