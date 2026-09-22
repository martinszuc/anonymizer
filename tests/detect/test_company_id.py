"""Tests for Czech and Slovak company identifier (IČO) detection."""

import pytest
from anonymizer.core.detect.company_id import find_company_ids, is_valid_company_id


@pytest.mark.parametrize("value", ["25912810", "00000191", "45237310", "12345679"])
def test_accepts_valid_identifiers(value):
    assert is_valid_company_id(value)


@pytest.mark.parametrize(
    "value",
    ["25912811", "12345678", "2591281", "259128100", "2591281a"],
)
def test_rejects_invalid_identifiers(value):
    assert not is_valid_company_id(value)


@pytest.mark.parametrize(
    "variant",
    ["IČO: 25912810", "IČO 25912810", "IC: 25912810", "ico:25912810", "IČ 25912810"],
)
def test_accepts_label_variants(variant):
    assert [match.text for match in find_company_ids(variant)] == ["25912810"]


def test_reports_only_the_digits_so_the_label_stays_readable():
    text = "Dodavatel, IČO: 25912810, Brno"
    found = list(find_company_ids(text))
    assert found[0].text == "25912810"
    assert text[found[0].start : found[0].end] == "25912810"


def test_requires_a_label():
    # A bare eight-digit number passing mod 11 is far too weak on its own.
    assert list(find_company_ids("variabilní symbol 25912810")) == []


def test_skips_labelled_but_invalid_identifier():
    assert list(find_company_ids("IČO: 25912811")) == []
