"""Tests for email address and telephone number detection."""

import pytest
from anonymizer.core.detect.contact import (
    find_czech_phone_numbers,
    find_emails,
    find_nanp_phone_numbers,
    find_ocr_emails,
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
        "tereza. prochazkova@example. com",  # as kraken read it
        "tereza. prochazkova@example.com",
        "tereza.prochazkova@example. com",
        "f. navratil@example. org",
        "j. a. novak@mail. example. co. uk",
        "novak_99@example-firma. cz",
        "jan.novak@example.com",  # no split at all
    ],
)
def test_ocr_finder_joins_an_address_split_after_a_period(variant):
    assert [match.text for match in find_ocr_emails(variant)] == [variant]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("E-mail: tereza. prochazkova@example. com, tel. 777", "tereza. prochazkova@example. com"),
        ("pište na f. navratil@example. org.", "f. navratil@example. org"),
        ("(jan. novak@example. cz)", "jan. novak@example. cz"),
        # The next sentence starts with a capital letter and is not taken in.
        ("Adresa: jan@example.cz. Telefon níže.", "jan@example.cz"),
        # A word before the split is taken whole or not at all.
        ("Napište nám. jan@example.cz", "jan@example.cz"),
    ],
)
def test_ocr_finder_matches_the_whole_address_in_running_text(text, expected):
    assert [match.text for match in find_ocr_emails(text)] == [expected]


@pytest.mark.parametrize(
    "value",
    [
        "tereza.prochazkova @example.com",  # a space not after a period
        "tereza.  prochazkova@example.com",  # two spaces
        "tereza.\nprochazkova@example.com",  # a line break
        "jan. @example.com",
        "jan@. example.com",
        "jan@example. Com",  # a capital after the space
        "jan@example",
        "ondrej. dvorakGexample. com",  # "@" misread: nothing to anchor on
    ],
)
def test_ocr_finder_rejects_other_gaps(value):
    assert [match.text for match in find_ocr_emails(value)] != [value]


def test_ocr_finder_ignores_a_line_break_after_a_period():
    text = "tereza.\nprochazkova@example.com"
    assert [match.text for match in find_ocr_emails(text)] == ["prochazkova@example.com"]


def test_strict_finder_does_not_join_across_a_space():
    text = "tereza. prochazkova@example. com"
    assert list(find_emails(text)) == []


@pytest.mark.parametrize(
    "variant",
    [
        "777123456",
        "777 123 456",
        "+420 777 123 456",
        "+420777123456",
        "00420 777 123 456",
        "+421 911 123 456",
        "421918446150",  # country code without "+", as OCR produces
        "421 918 446 150",
        "420777123456",
        "0918 446 150",  # Slovak domestic form with trunk zero
        "0918446150",
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
        "1421918446150",  # thirteen digits
        "4219184461500",
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


def test_country_code_without_plus_is_matched_whole_in_running_text():
    text = "tel. 421 918 446 150, e-mail"
    assert [match.text for match in find_czech_phone_numbers(text)] == ["421 918 446 150"]
