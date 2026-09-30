"""Postal address detection anchored on the postcode.

An address has no checksum, but its postal line has a shape a rule can rely
on: a Czech or Slovak postcode (PSČ, `602 00`) followed by a town, or a US
state code and ZIP code (`IL 62704`). The postcode plays the part of a label:
it is the evidence, and the street and house number written before it are
taken along, so the address is found whole.

This completes the name model, which marks the street and number but stops
before the postcode and town, leaving them readable. Combined with it, the
model's shorter span lies inside the rule's and is dropped
(`merge_entities`).
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from anonymizer.core.detect.base import Match
from anonymizer.core.types import EntityType

_UPPER = "A-ZÁČĎÉĚÍĹĽŇÓÔŔŘŠŤÚŮÝŽ"
_WORD = r"[^\W\d_][\w.'-]*"
_CAPITALISED = rf"[{_UPPER}][\w.'-]*"

# Lowercase words that start a street name: "náměstí Míru 5", "tř. Kpt. Jaroše 7".
_STREET_PREFIXES = r"(?:náměstí|nám\.|námestie|třída|tř\.|trieda|ulice|ul\.|nábřeží|nábr\.)"

# 684/12, 12a, 1879/48b: a house number, optionally with an orientation number.
_HOUSE_NUMBER = r"\d{1,5}[a-zA-Z]?(?:/\d{1,5}[a-zA-Z]?)?"

_CZECH_SLOVAK_STREET = (
    rf"(?:{_STREET_PREFIXES}\s+)?{_CAPITALISED}(?:[ \t]+{_WORD}){{0,3}}?[ \t]+{_HOUSE_NUMBER}"
)

# "Brno", "České Budějovice", "Praha 1", "Frýdek-Místek", "Nové Město na Moravě".
_TOWN = (
    rf"{_CAPITALISED}(?:[ \t]+{_CAPITALISED})*"
    rf"(?:[ \t]+(?:na|nad|pod|u|v|ve|při|pri)[ \t]+{_CAPITALISED}(?:[ \t]+{_CAPITALISED})*)?"
    r"(?:[ \t]+\d{1,2}(?!\d))?"
)

# A wrapped line may split the address after the comma or after the postcode,
# never inside the town: a town continuing onto the next line would swallow
# that line's first word.
_LINE_WRAP = r"(?:[ \t]+|[ \t]*\n[ \t]*)"

_CZECH_SLOVAK_ADDRESS = re.compile(
    rf"(?:(?<!\w)(?:{_CZECH_SLOVAK_STREET})[ \t]*(?:,{_LINE_WRAP}?|\n[ \t]*))?"
    rf"(?<!\d)\d{{3}}[ \t]?\d{{2}}(?!\d){_LINE_WRAP}{_TOWN}"
)

_US_STATES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]

_US_ADDRESS = re.compile(
    rf"(?:(?<!\w)\d{{1,6}}(?:[ \t]+{_CAPITALISED}){{1,5}}[ \t]*,[ \t]*)?"
    rf"(?:{_CAPITALISED}(?:[ \t]+{_CAPITALISED}){{0,2}}[ \t]*,[ \t]*)?"
    rf"(?:{'|'.join(_US_STATES)})[ \t]+\d{{5}}(?:-\d{{4}})?(?!\d)"
)


def _matches(pattern: re.Pattern[str], text: str) -> Iterator[Match]:
    for found in pattern.finditer(text):
        yield Match(type=EntityType.ADDRESS, start=found.start(), end=found.end(), text=found[0])


def find_czech_slovak_addresses(text: str) -> Iterator[Match]:
    """Yield Czech and Slovak addresses: a postcode and town, with the street before them.

    Args:
        text: Text to scan.

    Yields:
        One match per postal line, including a street and house number written
        directly before it (after a comma or a line break).
    """
    yield from _matches(_CZECH_SLOVAK_ADDRESS, text)


def find_us_addresses(text: str) -> Iterator[Match]:
    """Yield US addresses: a state code and ZIP code, with the street and city before them.

    Args:
        text: Text to scan.

    Yields:
        One match per address.
    """
    yield from _matches(_US_ADDRESS, text)
