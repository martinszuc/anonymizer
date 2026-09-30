"""Tests for postcode-anchored address detection."""

import pytest
from anonymizer.core.detect import finders_for
from anonymizer.core.detect.address import find_czech_slovak_addresses, find_us_addresses
from anonymizer.core.types import EntityType


def found_texts(finder, text: str) -> list[str]:
    return [match.text for match in finder(text)]


@pytest.mark.parametrize(
    ("text", "address"),
    [
        ("Adresa: Kounicova 684/12, 602 00 Brno", "Kounicova 684/12, 602 00 Brno"),
        ("bytem Masarykova 112, 586 01 Jihlava", "Masarykova 112, 586 01 Jihlava"),
        ("Nádražní 7, 370 01 České Budějovice", "Nádražní 7, 370 01 České Budějovice"),
        ("Hlavná 45, 040 01 Košice", "Hlavná 45, 040 01 Košice"),
        ("Dlouhá 12, 110 00 Praha 1", "Dlouhá 12, 110 00 Praha 1"),
        ("Lidická 1879/48b, 602 00 Brno", "Lidická 1879/48b, 602 00 Brno"),
        ("nám. Míru 5, 120 00 Praha 2", "nám. Míru 5, 120 00 Praha 2"),
        ("náměstí Svobody 12, 602 00 Brno", "náměstí Svobody 12, 602 00 Brno"),
        ("Na Příkopě 3, 110 00 Praha 1", "Na Příkopě 3, 110 00 Praha 1"),
        ("tř. Kpt. Jaroše 7, 602 00 Brno", "tř. Kpt. Jaroše 7, 602 00 Brno"),
        ("Hlavní 1, 592 31 Nové Město na Moravě", "Hlavní 1, 592 31 Nové Město na Moravě"),
        ("Palackého 5, 738 01 Frýdek-Místek", "Palackého 5, 738 01 Frýdek-Místek"),
        ("Kounicova 684/12\n602 00 Brno", "Kounicova 684/12\n602 00 Brno"),
        ("Kounicova 684/12,602 00 Brno", "Kounicova 684/12,602 00 Brno"),
        ("Masarykova 112, 586 01\nJihlava", "Masarykova 112, 586 01\nJihlava"),
        ("Masarykova 112,\n586 01 Jihlava", "Masarykova 112,\n586 01 Jihlava"),
        ("sídlo: 60200 Brno", "60200 Brno"),
        ("PSČ 602 00 Brno", "602 00 Brno"),
    ],
)
def test_czech_and_slovak_addresses(text, address):
    (match,) = find_czech_slovak_addresses(text)
    assert match.type is EntityType.ADDRESS
    assert match.text == address
    assert text[match.start : match.end] == address


def test_the_postal_line_alone_when_no_street_precedes_it():
    assert found_texts(find_czech_slovak_addresses, "Doručte do: 602 00 Brno") == ["602 00 Brno"]


def test_a_preceding_lowercase_word_is_not_taken_as_the_street():
    text = "bytem Masarykova 112, 586 01 Jihlava"
    assert found_texts(find_czech_slovak_addresses, text) == ["Masarykova 112, 586 01 Jihlava"]


def test_a_paragraph_break_after_the_postcode_ends_it():
    assert found_texts(find_czech_slovak_addresses, "PSČ 602 00\n\nBrno") == []


def test_a_line_break_after_the_town_ends_it():
    text = "Hlavná 45, 040 01 Košice\nVážený pán"
    assert found_texts(find_czech_slovak_addresses, text) == ["Hlavná 45, 040 01 Košice"]


@pytest.mark.parametrize(
    "text",
    [
        "tel. +420 603 123 456",
        "IBAN CZ65 0800 0000 1920 0014 5399",
        "Celkem 18 000 Kč",
        "Faktura č. 2026001234",
        "r. č. 880612/1005",
        "IČO 45862176",
        "602 00 brno",  # a town is capitalised
        "6020 0 Brno",
        "1602 00 Brno",
        "602 001 Brno",
        "nar. 12. 6. 1988",
    ],
)
def test_rejects_czech_and_slovak_look_alikes(text):
    assert found_texts(find_czech_slovak_addresses, text) == []


@pytest.mark.parametrize(
    ("text", "address"),
    [
        (
            "742 Evergreen Terrace, Springfield, IL 62704",
            "742 Evergreen Terrace, Springfield, IL 62704",
        ),
        ("1600 Pennsylvania Avenue NW, Washington, DC 20500", None),
        ("Springfield, IL 62704-1234", "Springfield, IL 62704-1234"),
        ("Mail to: Austin, TX 78701", "Austin, TX 78701"),
    ],
)
def test_us_addresses(text, address):
    expected = address or text
    assert found_texts(find_us_addresses, text) == [expected]


@pytest.mark.parametrize(
    "text",
    [
        "Order XX 12345",  # not a state
        "IL 1234",
        "IL 123456",
        "call 555-123-4567",
    ],
)
def test_rejects_us_look_alikes(text):
    assert found_texts(find_us_addresses, text) == []


@pytest.mark.parametrize(
    ("language", "finder"),
    [
        ("cs", find_czech_slovak_addresses),
        ("sk", find_czech_slovak_addresses),
        ("en", find_us_addresses),
    ],
)
def test_registered_for_its_languages(language, finder):
    assert finder in finders_for(language)
