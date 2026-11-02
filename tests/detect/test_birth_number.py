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
    "900141/1232",  # Czech insurance number (EČP): day +40
    "905171/1230",  # EČP for a woman, 31st day; remainder 10 recorded as 0
]

INVALID = [
    "900101/0008",  # check digit off by one
    "901301/0007",  # month 13
    "900132/0007",  # day 32
    "902901/0007",  # month 29 is not a valid offset month
    "900140/1233",  # day field 40: the EČP offset on day 0
    "900172/1234",  # day field 72: the EČP offset on day 32
    "900141/1233",  # EČP with the check digit off by one
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


def test_finds_an_insurance_number_in_running_text():
    text = "Pojištěnec bez r. č., EČP 905171/1230, státní příslušnost SK."
    assert [match.text for match in find_birth_numbers(text)] == ["905171/1230"]


def test_finds_several_numbers():
    text = "matka 905101/1233, otec 900101/0007"
    assert [match.text for match in find_birth_numbers(text)] == ["905101/1233", "900101/0007"]


# 900101000 mod 11 is 7, so 900101/0007 is valid and any other last digit is a
# wrong check digit on a real date; 900141/1232 is the valid EČP of the same day.
@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("Rodné číslo: 900101/0008, trvalý pobyt Brno.", "900101/0008"),
        ("rodného čísla 900101/0008 a adresy", "900101/0008"),
        ("rodne cislo 900101 / 0008", "900101 / 0008"),
        ("Pan Novák, r. č. 900101/0008, bydliště Brno.", "900101/0008"),
        ("R.Č.: 9001010008", "9001010008"),
        ("rod. č. 900101/0009", "900101/0009"),
        ("RČ 900101/0008", "900101/0008"),
        ("rč.900101/0008", "900101/0008"),
        ("EČP 900141/1233", "900141/1233"),
    ],
)
def test_finds_a_labelled_number_with_a_wrong_check_digit(text, value):
    found = list(find_birth_numbers(text))
    assert len(found) == 1
    assert text[found[0].start : found[0].end] == value


@pytest.mark.parametrize(
    "text",
    [
        "faktura 900101/0008 ze dne 1. 1. 2026",  # no label
        "rodné číslo uvedeno níže, faktura 900101/0008",  # label not right before
        "Marc 900101/0008",  # the label letters end another word
        "r. č. 901301/0008",  # month 13
        "r. č. 900132/0008",  # day 32
        "r. č. 900101008",  # nine digits but a post-1954 year
    ],
)
def test_a_label_does_not_rescue_other_candidates(text):
    assert list(find_birth_numbers(text)) == []


def test_a_label_does_not_change_validity():
    assert not is_valid_birth_number("900101/0008")
