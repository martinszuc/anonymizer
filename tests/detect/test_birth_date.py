"""Tests for date of birth detection."""

import pytest
from anonymizer.core.detect import finders_for
from anonymizer.core.detect.birth_date import (
    find_czech_slovak_birth_dates,
    find_english_birth_dates,
)
from anonymizer.core.types import EntityType


def found_texts(finder, text: str) -> list[str]:
    return [match.text for match in finder(text)]


@pytest.mark.parametrize(
    "text",
    [
        "nar. 12. 6. 1988",
        "nar. 12.6.1988",
        "nar. 12.06.1988",
        "nar.12. 6. 1988",
        "nar. 12 . 6 . 1988",
        "nar. 12/06/1988",
        "nar. 12-06-1988",
        "nar. 1988-06-12",
        "narozen 12. 6. 1988",
        "narozena dne 12. 6. 1988",
        "narozený: 12. 6. 1988",
        "Datum narození: 12. 6. 1988",
        "Datum narozeni: 12. 6. 1988",
        "datum\nnarození:\n12. 6. 1988",
        "dat. nar. 12. 6. 1988",
        "narodená 12. 6. 1988",
        "narodený dňa 12. 6. 1988",
        "Dátum narodenia: 12. 6. 1988",
        "Datum narodenia: 12. 6. 1988",
    ],
)
def test_czech_and_slovak_labels_and_numeric_forms(text):
    (match,) = find_czech_slovak_birth_dates(text)
    assert match.type is EntityType.DATE
    assert text[match.start : match.end] == match.text
    assert "1988" in match.text


@pytest.mark.parametrize(
    ("text", "date"),
    [
        ("nar. 12. června 1988", "12. června 1988"),
        ("nar. 12. cervna 1988", "12. cervna 1988"),
        ("narozena 1. ledna 2001", "1. ledna 2001"),
        ("nar. 30. září 1975", "30. září 1975"),
        ("narodený 12. júna 1988", "12. júna 1988"),
        ("narodena 3. decembra 1969", "3. decembra 1969"),
    ],
)
def test_czech_and_slovak_month_names(text, date):
    assert found_texts(find_czech_slovak_birth_dates, text) == [date]


@pytest.mark.parametrize(
    ("text", "date"),
    [
        ("Date of birth: 12 June 1988", "12 June 1988"),
        ("Date of Birth: 12/06/1988", "12/06/1988"),
        ("DOB: 1988-06-12", "1988-06-12"),
        ("D.O.B. 12 Jun 1988", "12 Jun 1988"),
        ("Born on June 12, 1988", "June 12, 1988"),
        ("born 12th of June 1988", "12th of June 1988"),
        ("Birth date: Sept. 3 1969", "Sept. 3 1969"),
        ("Birthdate: 3 Sep 1969", "3 Sep 1969"),
    ],
)
def test_english_labels_and_forms(text, date):
    assert found_texts(find_english_birth_dates, text) == [date]


def test_reports_only_the_date_so_the_label_stays_readable():
    text = "Prodávající: Ondřej Dvořák, nar. 12. 6. 1988, bytem Jihlava"
    (match,) = find_czech_slovak_birth_dates(text)
    assert text[match.start : match.end] == "12. 6. 1988"


def test_two_digit_year():
    assert found_texts(find_czech_slovak_birth_dates, "nar. 12. 6. 88") == ["12. 6. 88"]


@pytest.mark.parametrize(
    "text",
    [
        "Datum vystavení: 1. 9. 2026",  # an invoice date, not a birth date
        "Splatnost 14. 9. 2026",
        "12. 6. 1988",  # no label at all
        "narozeniny 12. 6. 1988",  # "birthday party", not the label
        "nar. 31. 2. 1990",  # no 31 February
        "nar. 12. 13. 1990",  # no month 13
        "nar. 0. 6. 1990",
        "nar. 12. 6. 1850",  # implausible birth year
        "nar. 12. června",  # no year
        "nar. 12. smarch 1988",  # not a month
        "nar. 29. 2. 1990",  # 1990 is not a leap year
        "nar. 12. 6. 19888",
    ],
)
def test_rejects(text):
    assert found_texts(find_czech_slovak_birth_dates, text) == []


def test_leap_day():
    assert found_texts(find_czech_slovak_birth_dates, "nar. 29. 2. 1992") == ["29. 2. 1992"]


def test_only_the_labelled_date_in_a_line_with_several():
    text = "Smlouva ze dne 1. 9. 2026 mezi Janem Novákem, nar. 3. 3. 1970, a ..."
    assert found_texts(find_czech_slovak_birth_dates, text) == ["3. 3. 1970"]


def test_english_labels_do_not_fire_in_the_czech_finder():
    assert found_texts(find_czech_slovak_birth_dates, "Date of birth: 12 June 1988") == []


@pytest.mark.parametrize(
    ("language", "finder"),
    [
        ("cs", find_czech_slovak_birth_dates),
        ("sk", find_czech_slovak_birth_dates),
        ("en", find_english_birth_dates),
    ],
)
def test_registered_for_its_languages(language, finder):
    assert finder in finders_for(language)


def test_every_rule_runs_without_a_language():
    finders = finders_for(None)
    assert find_czech_slovak_birth_dates in finders
    assert find_english_birth_dates in finders


def test_en_dash_between_label_and_date():
    assert found_texts(find_czech_slovak_birth_dates, "nar. \u2013 12. 6. 1988") == ["12. 6. 1988"]
