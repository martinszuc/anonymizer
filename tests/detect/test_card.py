"""Tests for payment card number detection."""

import pytest
from anonymizer.core.detect.card import find_card_numbers, is_valid_card_number, passes_luhn

VALID = [
    "4111111111111111",  # Visa
    "4012888888881881",  # Visa
    "5555555555554444",  # Mastercard
    "378282246310005",  # American Express
    "6011111111111117",  # Discover
]


@pytest.mark.parametrize("value", VALID)
def test_accepts_valid_cards(value):
    assert is_valid_card_number(value)


@pytest.mark.parametrize(
    "value",
    [
        "4111111111111112",  # Luhn fails
        "1234567890123456",  # unknown issuer and Luhn fails
        "9111111111111110",  # Luhn passes, but no issuer range starts with 9
        "41111111111111",  # valid prefix, wrong length
        "411111111111",  # too short to be a card
    ],
)
def test_rejects_invalid_cards(value):
    assert not is_valid_card_number(value)


@pytest.mark.parametrize(
    "variant",
    ["4111111111111111", "4111 1111 1111 1111", "4111-1111-1111-1111"],
)
def test_accepts_grouping_variants(variant):
    assert [match.text for match in find_card_numbers(variant)] == [variant]


def test_luhn_is_checked_independently_of_the_issuer_table():
    # Luhn alone accepts one in ten digit strings, so the issuer table does the
    # real filtering: this number is Luhn-valid but belongs to no issuer range.
    assert passes_luhn("9111111111111110")
    assert not is_valid_card_number("9111111111111110")


def test_finds_card_in_running_text():
    text = "Platba kartou 4111 1111 1111 1111 dne 1. 10."
    assert [match.text for match in find_card_numbers(text)] == ["4111 1111 1111 1111"]


def test_ignores_an_invoice_number_that_happens_to_be_digits():
    assert list(find_card_numbers("faktura 20260012345678")) == []
