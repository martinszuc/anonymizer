"""Tests for email address and telephone number detection."""

import pytest
from anonymizer.core.detect.contact import (
    find_czech_phone_numbers,
    find_emails,
    find_nanp_phone_numbers,
)


@pytest.mark.parametrize(
    "value",
    [
        "jan.novak@example.com",
        "j.novak+faktury@sub.example.co.uk",
        "novak_99@example-firma.cz",
    ],
)
def test_finds_valid_addresses(value):
    assert [match.text for match in find_emails(value)] == [value]


@pytest.mark.parametrize("value", ["jan.novak@example", "@example.com", "jan.novak(at)example.com"])
def test_ignores_non_addresses(value):
    assert list(find_emails(value)) == []


def test_finds_address_in_running_text():
    text = "Kontakt: jan.novak@example.com, tel. níže."
    assert [match.text for match in find_emails(text)] == ["jan.novak@example.com"]


@pytest.mark.parametrize(
    "variant",
    [
        "777123456",
        "777 123 456",
        "+420 777 123 456",
        "+420777123456",
        "00420 777 123 456",
        "+421 911 123 456",
    ],
)
def test_finds_phone_variants(variant):
    assert [match.text for match in find_czech_phone_numbers(variant)] == [variant]


@pytest.mark.parametrize(
    "value",
    [
        "77712345",  # eight digits
        "7771234567",  # ten digits
        "900101/0007",  # birth number, not a phone number
    ],
)
def test_ignores_non_phone_digit_runs(value):
    assert list(find_czech_phone_numbers(value)) == []


def test_ignores_digits_inside_account_number():
    assert list(find_czech_phone_numbers("2000145399/0800")) == []


@pytest.mark.parametrize(
    "variant",
    [
        "(123) 456-7890",
        "123-456-7890",
        "123.456.7890",
        "+1 202 555 0147",
        "1-800-555-0199",
        "2025550147",
    ],
)
def test_finds_nanp_variants(variant):
    assert [match.text for match in find_nanp_phone_numbers(variant)] == [variant]


@pytest.mark.parametrize(
    "value",
    [
        "9001010007",  # birth number: exchange starts with 1
        "2000145399",  # account base: exchange starts with 0
        "123456789",  # nine digits
        "20255501470",  # eleven digits
    ],
)
def test_ignores_bare_digit_runs_that_break_nanp_structure(value):
    assert list(find_nanp_phone_numbers(value)) == []


def test_finds_nanp_number_in_running_text():
    text = "Casey Smith, Washington, D.C. 20001, (123) 456-7890"
    assert [match.text for match in find_nanp_phone_numbers(text)] == ["(123) 456-7890"]
