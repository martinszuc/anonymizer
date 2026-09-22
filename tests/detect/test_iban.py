"""Tests for IBAN detection."""

import pytest
from anonymizer.core.detect.iban import find_ibans, is_valid_iban, normalize_iban

VALID = [
    "CZ6508000000192000145399",
    "SK3112000000198742637541",
    "DE89370400440532013000",
]

INVALID = [
    "CZ6508000000192000145390",  # mod-97 fails
    "CZ650800000019200014539",  # wrong length for CZ
    "DE8937040044053201300",  # wrong length for DE
    "CZ65",
    "6508000000192000145399",  # no country code
]


@pytest.mark.parametrize("value", VALID)
def test_accepts_valid_ibans(value):
    assert is_valid_iban(value)


@pytest.mark.parametrize("value", INVALID)
def test_rejects_invalid_ibans(value):
    assert not is_valid_iban(value)


@pytest.mark.parametrize(
    "variant",
    [
        "CZ6508000000192000145399",
        "CZ65 0800 0000 1920 0014 5399",
        "cz65 0800 0000 1920 0014 5399",
        "CZ65 0800000019 2000145399",
    ],
)
def test_accepts_spacing_and_case_variants(variant):
    assert is_valid_iban(variant)
    assert [match.text for match in find_ibans(variant)] == [variant]


def test_normalize_strips_spacing_and_upper_cases():
    assert normalize_iban("cz65 0800 0000 1920 0014 5399") == "CZ6508000000192000145399"


def test_rejects_czech_iban_whose_domestic_account_is_invalid():
    # Valid mod-97 payload, but the embedded base fails its mod-11 checksum.
    assert not is_valid_iban("CZ1708000000192000145390")


def test_finds_iban_in_running_text():
    text = "IBAN: CZ65 0800 0000 1920 0014 5399 (SWIFT GIBACZPX)"
    found = list(find_ibans(text))
    assert len(found) == 1
    assert found[0].text == "CZ65 0800 0000 1920 0014 5399"
