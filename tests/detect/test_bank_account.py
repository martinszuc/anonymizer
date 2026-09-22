"""Tests for Czech and Slovak bank account number detection."""

import pytest
from anonymizer.core.detect.bank_account import find_account_numbers, is_valid_account_number


@pytest.mark.parametrize(
    ("base", "prefix"),
    [
        ("2000145399", None),
        ("2000145399", "19"),
        ("8742637541", None),
        ("19", None),  # shortest permitted base
    ],
)
def test_accepts_valid_numbers(base, prefix):
    assert is_valid_account_number(base, prefix)


@pytest.mark.parametrize(
    ("base", "prefix"),
    [
        ("2000145390", None),  # base checksum fails
        ("2000145399", "1"),  # prefix checksum fails
        ("123456789", None),
        ("0", None),  # an all-zero account is not an account
        ("2", None),  # too short
        ("20001453990", None),  # too long
        ("20001a5399", None),
    ],
)
def test_rejects_invalid_numbers(base, prefix):
    assert not is_valid_account_number(base, prefix)


@pytest.mark.parametrize(
    "variant",
    [
        "2000145399/0800",
        "19-2000145399/0800",
        "19 - 2000145399 / 0800",
        "2000145399 /0800",
    ],
)
def test_accepts_separator_variants(variant):
    assert [match.text for match in find_account_numbers(variant)] == [variant]


def test_finds_number_in_running_text():
    text = "Platbu zašlete na účet 19-2000145399/0800 do 15. 10."
    found = list(find_account_numbers(text))
    assert len(found) == 1
    assert found[0].text == "19-2000145399/0800"


def test_skips_number_with_broken_checksum():
    assert list(find_account_numbers("účet 2000145390/0800")) == []
