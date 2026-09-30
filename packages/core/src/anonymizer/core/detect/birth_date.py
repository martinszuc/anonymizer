"""Date of birth detection.

A date has no checksum, and most dates in a document (issue dates, deadlines,
periods of employment) are not personal. A date therefore counts only right
after a birth label such as `nar.`, `datum narození` or `date of birth`: the
label is the evidence, as for IČO. Only the date is reported, so the label
stays readable after redaction.

Dates are written as numbers (`12. 6. 1988`, `12/06/1988`, `1988-06-12`) or
with a month name in Czech, Slovak or English (`12. června 1988`,
`12. júna 1988`, `12 June 1988`, `June 12, 1988`). Month names are matched
without diacritics, because OCR drops them, and every month table applies to
every language: the labels are what is locale-specific.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator
from datetime import date

from anonymizer.core.detect.base import Finder, Match
from anonymizer.core.types import EntityType

_MONTHS: dict[str, int] = {
    # Czech, nominative and genitive (a date uses the genitive: "12. června").
    **dict.fromkeys(["leden", "ledna"], 1),
    **dict.fromkeys(["unor", "unora"], 2),
    **dict.fromkeys(["brezen", "brezna"], 3),
    **dict.fromkeys(["duben", "dubna"], 4),
    **dict.fromkeys(["kveten", "kvetna"], 5),
    **dict.fromkeys(["cerven", "cervna"], 6),
    **dict.fromkeys(["cervenec", "cervence"], 7),
    **dict.fromkeys(["srpen", "srpna"], 8),
    "zari": 9,
    **dict.fromkeys(["rijen", "rijna"], 10),
    **dict.fromkeys(["listopad", "listopadu"], 11),
    **dict.fromkeys(["prosinec", "prosince"], 12),
    # Slovak, nominative and genitive.
    **dict.fromkeys(["januar", "januara"], 1),
    **dict.fromkeys(["februar", "februara"], 2),
    **dict.fromkeys(["marec", "marca"], 3),
    **dict.fromkeys(["april", "aprila"], 4),
    **dict.fromkeys(["maj", "maja"], 5),
    **dict.fromkeys(["jun", "juna"], 6),
    **dict.fromkeys(["jul", "jula"], 7),
    **dict.fromkeys(["august", "augusta"], 8),
    **dict.fromkeys(["september", "septembra"], 9),
    **dict.fromkeys(["oktober", "oktobra"], 10),
    **dict.fromkeys(["november", "novembra"], 11),
    **dict.fromkeys(["december", "decembra"], 12),
    # English, full and abbreviated.
    **dict.fromkeys(["january", "jan"], 1),
    **dict.fromkeys(["february", "feb"], 2),
    **dict.fromkeys(["march", "mar"], 3),
    "apr": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "aug": 8,
    **dict.fromkeys(["sep", "sept"], 9),
    **dict.fromkeys(["october", "oct"], 10),
    "nov": 11,
    "dec": 12,
}

_MONTH_WORD = r"[^\W\d_]{3,}"
_ORDINAL = r"(?:st|nd|rd|th)?"

# One alternative per way of writing a date; group names say which part is which.
_SEPARATOR = r"\s*[./-]\s*"
_DATE = (
    r"(?:"
    # 12. 6. 1988, 12/06/1988, 12-06-88
    rf"(?P<n_day>\d{{1,2}}){_SEPARATOR}(?P<n_month>\d{{1,2}}){_SEPARATOR}"
    r"(?P<n_year>\d{4}|\d{2})"
    # 1988-06-12
    r"|(?P<i_year>\d{4})-(?P<i_month>\d{1,2})-(?P<i_day>\d{1,2})"
    # 12. června 1988, 12 June 1988, 12th of June 1988
    rf"|(?P<w_day>\d{{1,2}})(?:\.|{_ORDINAL})\s*(?:of\s+)?"
    rf"(?P<w_month>{_MONTH_WORD})\.?\s+(?P<w_year>\d{{4}})"
    # June 12, 1988
    rf"|(?P<m_month>{_MONTH_WORD})\.?\s+(?P<m_day>\d{{1,2}}){_ORDINAL},?\s+(?P<m_year>\d{{4}})"
    r")(?!\d)"
)

# Between the label and the date: punctuation, and "dne" / "dňa" / "on" ("born on").
# \u2013 is an en dash, as in "nar. \u2013 12. 6. 1988".
_CONNECTOR = r"\s*[:.,\u2013-]?\s*(?:(?:dne|dňa|dna|on)\s+)?"

_CZECH_SLOVAK_LABELS = (
    r"nar\.",
    r"narozen[aáýy]?",
    r"naroden[aáýy]?",
    r"datum\s+narozen[ií]",
    r"d[aá]tum\s+narodenia",
    r"dat\.\s*nar\.",
)

_ENGLISH_LABELS = (
    r"date\s+of\s+birth",
    r"birth\s*date",
    r"d\.?o\.?b\.?",
    r"born",
)

# Two-digit years cannot be checked for 29 February; a leap year accepts them.
_LEAP_YEAR = 2000
_EARLIEST_YEAR = 1900
_LATEST_YEAR = 2099


def _fold(word: str) -> str:
    """Lowercase and strip diacritics: `června` → `cervna`."""
    decomposed = unicodedata.normalize("NFD", word.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _is_calendar_date(day: str, month: int | None, year: str) -> bool:
    """Whether the parts form a real date in a plausible birth year."""
    if month is None:
        return False
    full_year = int(year)
    if len(year) == 4 and not _EARLIEST_YEAR <= full_year <= _LATEST_YEAR:
        return False
    try:
        date(full_year if len(year) == 4 else _LEAP_YEAR, month, int(day))
    except ValueError:
        return False
    return True


def _is_valid(found: re.Match[str]) -> bool:
    """Check whichever date alternative matched."""
    if found.group("n_day"):
        return _is_calendar_date(found["n_day"], int(found["n_month"]), found["n_year"])
    if found.group("i_year"):
        return _is_calendar_date(found["i_day"], int(found["i_month"]), found["i_year"])
    if found.group("w_day"):
        month = _MONTHS.get(_fold(found["w_month"]))
        return _is_calendar_date(found["w_day"], month, found["w_year"])
    month = _MONTHS.get(_fold(found["m_month"]))
    return _is_calendar_date(found["m_day"], month, found["m_year"])


def _labelled_date_finder(labels: tuple[str, ...]) -> Finder:
    """Build a finder for dates that directly follow one of the labels."""
    # A label ending in a letter must end a word ("narozen", not "narozeniny");
    # one ending in a full stop may touch the date ("nar.12. 6. 1988").
    bounded = [label if label.endswith(r"\.") else rf"{label}(?!\w)" for label in labels]
    pattern = re.compile(
        rf"(?<!\w)(?:{'|'.join(bounded)}){_CONNECTOR}(?P<date>{_DATE})",
        re.IGNORECASE,
    )

    def find(text: str) -> Iterator[Match]:
        for found in pattern.finditer(text):
            if _is_valid(found):
                yield Match.from_regex(found, EntityType.DATE, group="date")

    return find


find_czech_slovak_birth_dates = _labelled_date_finder(_CZECH_SLOVAK_LABELS)
"""Yield dates of birth after a Czech or Slovak label (`nar.`, `datum narození`, ...)."""

find_english_birth_dates = _labelled_date_finder(_ENGLISH_LABELS)
"""Yield dates of birth after an English label (`date of birth`, `DOB`, `born`)."""
