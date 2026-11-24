"""Invented people and the values written about them, with this module's own check digits.

Names are combined arbitrarily from short lists that share no word with the
benchmark's people, the name-forms set or the held-out set
(`tests/benchmark/test_photo_train.py` checks it). Each name carries its
declension pattern for `experiments.declension`. Streets name no person, and
companies, IČOs and reference numbers are decoys: they look like identifiers
but are not personal data.

Birth numbers, account numbers, IBANs and IČOs get their check digits from
the arithmetic written here, never from the validators the pipeline uses, so
the tests can check one against the other.
"""

from __future__ import annotations

import random
import unicodedata
from dataclasses import dataclass
from datetime import date

from experiments.declension import Name, Paradigm, feminine_surname

H, S, E = Paradigm.HARD, Paradigm.SOFT, Paradigm.MOBILE_E
AM, ADJ = Paradigm.A_MASC, Paradigm.ADJ_MASC
AF, IE, IA = Paradigm.A_FEM, Paradigm.IE_FEM, Paradigm.IA_FEM


@dataclass(frozen=True, slots=True)
class NamePool:
    """The names one language draws from; surnames in the masculine form."""

    male_first: tuple[Name, ...]
    female_first: tuple[Name, ...]
    surnames: tuple[Name, ...]


def _names(*entries: tuple[str, Paradigm]) -> tuple[Name, ...]:
    return tuple(Name(word, paradigm) for word, paradigm in entries)


NAMES: dict[str, NamePool] = {
    "cs": NamePool(
        male_first=_names(
            ("Vít", H),
            ("Rostislav", H),
            ("Bořivoj", S),
            ("Svatopluk", H),
            ("Hynek", E),
            ("Otakar", H),
            ("Leoš", S),
            ("Přemysl", H),
            ("Drahomír", H),
            ("Kryštof", H),
            ("Vilém", H),
            ("Arnošt", H),
        ),
        female_first=_names(
            ("Hedvika", AF),
            ("Bohdana", AF),
            ("Libuše", IE),
            ("Radmila", AF),
            ("Vendula", AF),
            ("Drahomíra", AF),
            ("Ilona", AF),
            ("Milena", AF),
            ("Lýdie", IE),
            ("Žaneta", AF),
        ),
        surnames=_names(
            ("Vondráček", E),
            ("Kalina", AM),
            ("Šebesta", AM),
            ("Toman", H),
            ("Kovařík", H),
            ("Pešek", E),
            ("Bureš", S),
            ("Skála", AM),
            ("Strnad", H),
            ("Linhart", H),
            ("Šafránek", E),
            ("Vybíral", H),
            ("Pokorný", ADJ),
            ("Hronek", E),
            ("Jedlička", AM),
        ),
    ),
    "sk": NamePool(
        male_first=_names(
            ("Jozef", H),
            ("Štefan", H),
            ("Tibor", H),
            ("Ondrej", S),
            ("Imrich", H),
            ("Vojtech", H),
            ("Róbert", H),
            ("Norbert", H),
            ("Ivan", H),
            ("Július", H),
        ),
        female_first=_names(
            ("Marta", AF),
            ("Beáta", AF),
            ("Božena", AF),
            ("Klaudia", IA),
            ("Margita", AF),
            ("Agáta", AF),
            ("Lívia", IA),
            ("Sabína", AF),
            ("Henrieta", AF),
            ("Terézia", IA),
        ),
        surnames=_names(
            ("Mikuš", S),
            ("Baran", H),
            ("Hudec", E),
            ("Ferenc", H),
            ("Sloboda", AM),
            ("Kmeť", H),
            ("Juhás", H),
            ("Chovanec", E),
            ("Pavlovič", H),
            ("Kováčik", H),
            ("Ševčík", H),
            ("Petráš", H),
            ("Kušnír", H),
            ("Hlinka", AM),
            ("Hrušovský", ADJ),
        ),
    ),
}
"""Names per language; women take `feminine_surname` of a surname."""

STREETS = {
    "cs": (
        "Topolová",
        "Habrová",
        "U Mlýna",
        "Na Kopci",
        "Lesní",
        "Severní",
        "Úzká",
        "Cihlářská",
        "Ke Hřišti",
        "Třešňová",
        "Rybářská",
        "Za Humny",
    ),
    "sk": (
        "Kvetná",
        "Orgovánová",
        "Za Humnami",
        "Pri Potoku",
        "Gaštanová",
        "Vinohradnícka",
        "Rybárska",
        "Pod Hájom",
        "Okružná",
        "Severná",
        "Brezová",
        "Na Vŕšku",
    ),
}
"""Street names that name no person."""

TOWNS = {
    "cs": (
        ("547 01", "Náchod"),
        ("568 02", "Svitavy"),
        ("789 01", "Zábřeh"),
        ("438 01", "Žatec"),
        ("290 01", "Poděbrady"),
        ("664 34", "Kuřim"),
        ("460 01", "Liberec"),
        ("301 00", "Plzeň"),
        ("695 01", "Hodonín"),
        ("682 01", "Vyškov"),
        ("269 01", "Rakovník"),
        ("513 01", "Semily"),
    ),
    "sk": (
        ("026 01", "Dolný Kubín"),
        ("902 01", "Pezinok"),
        ("921 01", "Piešťany"),
        ("066 01", "Humenné"),
        ("984 01", "Lučenec"),
        ("048 01", "Rožňava"),
        ("909 01", "Skalica"),
        ("085 01", "Bardejov"),
        ("945 01", "Komárno"),
        ("955 01", "Topoľčany"),
        ("977 01", "Brezno"),
        ("052 01", "Spišská Nová Ves"),
    ),
}
"""Postcode and town; a town alone is not personal data, the whole address is."""

COMPANIES = {
    "cs": (
        "Strojírny Litavka a.s.",
        "Okna Polabí s.r.o.",
        "Teplo Vysočina a.s.",
        "Stavby Haná s.r.o.",
        "Tiskárna Orlice s.r.o.",
        "Lesní školka Brdy s.r.o.",
        "Účetnictví Plus s.r.o.",
        "Autoservis Sever s.r.o.",
        "Topenářství Jizera s.r.o.",
        "Zahrady Podyjí s.r.o.",
    ),
    "sk": (
        "Drevostav Orava s. r. o.",
        "Agro Hron, a. s.",
        "Teplo Tatry s. r. o.",
        "Strojárne Považie a. s.",
        "Účtovníctvo Dunaj s. r. o.",
        "Pekáreň Kysuce s. r. o.",
        "Okná Záhorie s. r. o.",
        "Kúrenie Gemer s. r. o.",
        "Stavby Ponitrie s. r. o.",
        "Záhrady Hont s. r. o.",
    ),
}
"""Company names: decoys, organisations rather than people."""

BANK_CODES = {
    "cs": ("0100", "0300", "0600", "0800", "2010", "2700", "3030", "5500", "6100"),
    "sk": ("0200", "0900", "1100", "5600", "6500", "7500", "8330"),
}
_COUNTRY = {"cs": "CZ", "sk": "SK"}
_DOMAINS = ("example.com", "example.org", "example.net")
_CURRENCY = {"cs": "Kč", "sk": "EUR"}

BIRTH_YEARS = {"child": (2010, 2019), "adult": (1956, 2003), "elder": (1954, 1962)}
"""Birth numbers before 1954 have nine digits and no check digit; none is generated."""

# Weights of the account number check (ČNB decree 169/2011), right-aligned: the
# last digit always has weight 1. Slovak numbers use the same rule.
ACCOUNT_WEIGHTS = (6, 3, 7, 9, 10, 5, 8, 4, 2, 1)
# IČO: the first seven digits weighted 8 down to 2.
COMPANY_ID_WEIGHTS = (8, 7, 6, 5, 4, 3, 2)


@dataclass(frozen=True, slots=True)
class Person:
    """An invented person with every value a template may ask for."""

    female: bool
    first: Name
    surname: Name
    family_surname: Name
    address: str
    born: date
    birth_number: str
    phone: str
    email: str
    account: str
    iban: str


def draw_person(
    female: bool,
    first: Name,
    family_surname: Name,
    *,
    years: tuple[int, int],
    draw: random.Random,
    language: str,
) -> Person:
    """Draw every value of a person, always in the same order."""
    surname = feminine_surname(family_surname) if female else family_surname
    number = str(draw.randint(1, 1800))
    if draw.random() < 0.3:
        number += f"/{draw.randint(1, 40)}"
    postcode, town = draw.choice(TOWNS[language])
    born = date(draw.randint(*years), draw.randint(1, 12), draw.randint(1, 28))
    prefix = account_part(draw, draw.choice((2, 6))) if draw.random() < 0.3 else ""
    base = account_part(draw, draw.choice((6, 8, 10)))
    bank_code = draw.choice(BANK_CODES[language])
    return Person(
        female=female,
        first=first,
        surname=surname,
        family_surname=family_surname,
        address=f"{draw.choice(STREETS[language])} {number}, {postcode} {town}",
        born=born,
        birth_number=birth_number(born, female=female, draw=draw),
        phone=phone(draw, language),
        email=email(first, surname, draw),
        account=f"{prefix + '-' if prefix else ''}{base}/{bank_code}",
        iban=iban(_COUNTRY[language], bank_code, prefix, base),
    )


def birth_number(born: date, *, female: bool, draw: random.Random) -> str:
    """Return a birth number (rodné číslo) for a date of birth.

    YYMMDDSSSC, the month plus 50 for a woman, the whole number divisible by
    11: the check digit is the first nine digits modulo 11. A serial leaving
    10 is drawn again.
    """
    month = born.month + (50 if female else 0)
    while True:
        first_nine = f"{born.year % 100:02d}{month:02d}{born.day:02d}{draw.randrange(1000):03d}"
        check = int(first_nine) % 11
        if check < 10:
            return f"{first_nine[:6]}/{first_nine[6:]}{check}"


def account_part(draw: random.Random, length: int) -> str:
    """Return an account prefix or base whose weighted digit sum is divisible by 11."""
    weights = ACCOUNT_WEIGHTS[-length:]
    while True:
        digits = [draw.randint(1, 9), *(draw.randrange(10) for _ in range(length - 2))]
        weighted = sum(digit * weight for digit, weight in zip(digits, weights, strict=False))
        last = -weighted % 11  # the last weight is 1, so this digit closes the sum
        if last < 10:
            return "".join(map(str, digits)) + str(last)


def iban(country: str, bank_code: str, prefix: str, base: str) -> str:
    """Return the IBAN of a Czech or Slovak account, in groups of four.

    The check digits make the number, with country and check moved to the end
    and letters read as 10 to 35, leave 1 modulo 97 (ISO 13616).
    """
    bban = bank_code + prefix.zfill(6) + base.zfill(10)
    letters = "".join(str(ord(letter) - ord("A") + 10) for letter in country)
    check = 98 - int(bban + letters + "00") % 97
    compact = f"{country}{check:02d}{bban}"
    return " ".join(compact[start : start + 4] for start in range(0, len(compact), 4))


def company_id(draw: random.Random) -> str:
    """Return an IČO: seven digits and a weighted mod-11 check digit."""
    digits = [draw.randint(1, 9), *(draw.randrange(10) for _ in range(6))]
    remainder = sum(d * w for d, w in zip(digits, COMPANY_ID_WEIGHTS, strict=True)) % 11
    check = {0: 1, 1: 0}.get(remainder, 11 - remainder)
    return "".join(map(str, digits)) + str(check)


def phone(draw: random.Random, language: str) -> str:
    """Return a mobile number: Czech 6xx/7xx, Slovak 9xx, with or without the country code."""
    lead = draw.choice("67") if language == "cs" else "9"
    digits = lead + "".join(str(draw.randrange(10)) for _ in range(8))
    groups = f"{digits[:3]} {digits[3:6]} {digits[6:]}"
    if draw.random() < 0.5:
        return f"+{420 if language == 'cs' else 421} {groups}"
    return groups if language == "cs" else f"0{groups}"


def email(first: Name, surname: Name, draw: random.Random) -> str:
    """Return an e-mail address made of the name, at a reserved example domain."""
    given, family = ascii_word(first.word), ascii_word(surname.word)
    local = draw.choice(
        (f"{given}.{family}", f"{given[0]}{family}", f"{family}.{given[0]}", f"{family}{given}")
    )
    return f"{local}@{draw.choice(_DOMAINS)}"


def ascii_word(word: str) -> str:
    """Return a word lowercased without diacritics, as e-mail addresses write it."""
    decomposed = unicodedata.normalize("NFKD", word)
    return "".join(char for char in decomposed if char.isascii()).lower()


def amount(draw: random.Random, language: str) -> str:
    """Return a sum of money as Czech and Slovak documents write it ("12 480 Kč")."""
    value = draw.randrange(1500, 90000, 10)
    thousands, rest = divmod(value, 1000)
    written = f"{thousands} {rest:03d}" if thousands else str(rest)
    return f"{written} {_CURRENCY[language]}"


def issue_date(draw: random.Random) -> str:
    """Return a date of 2026 written d. m. yyyy: a document date, never a date of birth."""
    day = date(2026, draw.randint(1, 12), draw.randint(1, 28))
    return f"{day.day}. {day.month}. {day.year}"


def reference(draw: random.Random) -> str:
    """Return a file or invoice number: a decoy, not personal data."""
    return f"{draw.randint(10000, 99999)}/2026"
