"""Filling the templates: invented people in, benchmark document files out."""

from __future__ import annotations

import json
import random
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from benchmark.photo_train.templates import TEMPLATES, Template
from benchmark.photo_train.values import (
    BIRTH_YEARS,
    COMPANIES,
    NAMES,
    TOWNS,
    Person,
    amount,
    company_id,
    draw_person,
    issue_date,
    reference,
)
from experiments.declension import (
    Agreement,
    Case,
    Name,
    decline,
    has_possessive,
    possessive,
    title,
)

LANGUAGES = ("cs", "sk")
SPLITS = ("print", "synthetic")

PRINT_PER_LANGUAGE = 16
"""Documents of the print split per language: every template twice."""

SEEDS = {"print": "photo-train/print", "synthetic": "photo-train/synthetic"}
"""Default seed of each split; the synthetic split takes another with `seed`."""

DOCUMENTS = Path(__file__).parent / "documents"
"""The print split as generated, committed so the printed pages stay fixed."""

_PLACEHOLDER = re.compile(
    r"\{(?:(?P<preposition>[skv])~)?(?P<person>[A-EMNVW])"
    r"(?:\.(?P<slot>[a-z]+)(?:\.(?P<form>[a-z_]+))?"
    r"|\?(?P<male>[^|}]*)\|(?P<female>[^}]*))\}"
    r"|\{doc\.(?P<doc>[a-z0-9]+)\}"
)
_NAME_SLOTS = frozenset({"full", "titled", "surname", "first", "initial", "rev", "sposs"})
_VALUE_SLOTS = {
    "addr": "address",
    "rc": "birth_number",
    "born": "date",
    "phone": "phone",
    "email": "email",
    "account": "bank_account",
    "iban": "iban",
}
_DECOY_SLOTS = frozenset({"company", "company2", "ico", "ref"})
# Vocalised prepositions: the longer form before the letters that need it.
_VOCALISED = {
    "cs": {"s": ("se", "szšž"), "k": ("ke", "kg"), "v": ("ve", "fv")},
    "sk": {"s": ("so", "szšž"), "k": ("ku", "kg"), "v": ("vo", "fv")},
}


@dataclass(frozen=True, slots=True)
class GeneratedDocument:
    """One generated document.

    Attributes:
        name: File stem, unique within a split.
        language: `cs` or `sk`.
        kind: The template's kind.
        template: The template's name.
        source: The document file in the benchmark's TOML format.
    """

    name: str
    language: str
    kind: str
    template: str
    source: str


def generate(split: str, *, count: int = 0, seed: str | None = None) -> list[GeneratedDocument]:
    """Return the documents of a split, the same on every call with the same arguments.

    Args:
        split: `print` (`PRINT_PER_LANGUAGE` documents per language; `count`
            and `seed` must be left out) or `synthetic` (`count` per language).
        count: Synthetic documents per language.
        seed: Seed of the synthetic split (default `SEEDS["synthetic"]`).

    Returns:
        Czech documents, then Slovak, each cycling through its templates.

    Raises:
        ValueError: For an unknown split, a count or seed given to the print
            split, or a synthetic count below one.
    """
    if split not in SPLITS:
        msg = f"unknown split {split!r}; use one of {', '.join(SPLITS)}"
        raise ValueError(msg)
    if split == "print":
        if count or seed is not None:
            msg = "the print split is fixed: it takes no count or seed"
            raise ValueError(msg)
        count = PRINT_PER_LANGUAGE
    elif count < 1:
        msg = "the synthetic split needs a count of at least one"
        raise ValueError(msg)
    seed = seed if seed is not None else SEEDS[split]
    width = 2 if split == "print" else 5
    letter = split[0]
    documents: list[GeneratedDocument] = []
    for language in LANGUAGES:
        templates = TEMPLATES[language]
        for index in range(count):
            number = index % len(templates)
            template = templates[number]
            # Seeded per document, so a longer synthetic split extends a shorter one.
            draw = random.Random(f"{seed}/{language}/{index}")
            people = cast(template, language, draw, instance=index // len(templates) + number)
            name = f"{language}-{letter}{index + 1:0{width}d}-{template.name}"
            source = document_source(template, people, language, draw, name=name, seed=seed)
            documents.append(
                GeneratedDocument(name, language, template.kind, template.name, source)
            )
    return documents


def write(documents: list[GeneratedDocument], directory: Path) -> list[Path]:
    """Write each document as `<name>.toml`; return the paths in order."""
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for document in documents:
        path = directory / f"{document.name}.toml"
        path.write_text(document.source, encoding="utf-8", newline="\n")
        paths.append(path)
    return paths


def cast(
    template: Template, language: str, draw: random.Random, *, instance: int
) -> dict[str, Person]:
    """Choose the people of one document: different first names, surnames shared by families.

    Raises:
        ValueError: If a woman's surname is asked for a possessive.
    """
    needs: dict[str, set[str]] = {}
    for found in _PLACEHOLDER.finditer("\n".join(template.lines)):
        if found["person"]:
            needs.setdefault(found["person"], set()).add(found["slot"] or "")
    family_of = {letter: group for group in template.families for letter in group}
    pool = NAMES[language]
    surnames: dict[str, Name] = {}
    people: dict[str, Person] = {}
    for letter in sorted(needs):
        female = _female(letter, instance)
        if female and "sposs" in needs[letter]:
            msg = f"{template.name}: a woman's surname has no possessive ({letter})"
            raise ValueError(msg)
        group = family_of.get(letter, letter)
        if group not in surnames:
            wants_possessive = any("sposs" in needs.get(member, ()) for member in group)
            surnames[group] = draw.choice(
                [
                    name
                    for name in pool.surnames
                    if name not in surnames.values()
                    and (not wants_possessive or has_possessive(name, language))
                ]
            )
        taken = {person.first for person in people.values()}
        first = draw.choice(
            [
                name
                for name in (pool.female_first if female else pool.male_first)
                if name not in taken
            ]
        )
        people[letter] = draw_person(
            female,
            first,
            surnames[group],
            years=_birth_years(template, letter),
            draw=draw,
            language=language,
        )
    return people


def _female(letter: str, instance: int) -> bool:
    """M, N are men and V, W women; A to E alternate, neighbours of opposite gender."""
    if letter in "MN":
        return False
    if letter in "VW":
        return True
    return (instance + "ABCDE".index(letter)) % 2 == 1


def _birth_years(template: Template, letter: str) -> tuple[int, int]:
    if letter in template.children:
        return BIRTH_YEARS["child"]
    if letter in template.elders:
        return BIRTH_YEARS["elder"]
    return BIRTH_YEARS["adult"]


def document_source(
    template: Template,
    people: dict[str, Person],
    language: str,
    draw: random.Random,
    *,
    name: str,
    seed: str,
) -> str:
    """Return a filled template as a benchmark document file, gold items marked inline.

    Raises:
        ValueError: For an unknown slot, a form the slot does not take, or
            text not in NFC.
    """
    companies = draw.sample(COMPANIES[language], 2)
    values = {
        "company": companies[0],
        "company2": companies[1],
        "ico": company_id(draw),
        "ref": reference(draw),
        "issued": issue_date(draw),
        "place": draw.choice(TOWNS[language])[1],
        "amount": amount(draw, language),
    }
    used: set[str] = set()
    lines = [_fill(line, people, values, language, used) for line in template.lines]
    for line in lines:
        if unicodedata.normalize("NFC", line) != line:
            msg = f"{template.name}: a template, name or value is not in NFC"
            raise ValueError(msg)
    decoys = [*template.decoys, *(values[slot] for slot in sorted(used & _DECOY_SLOTS))]
    return "\n".join(
        [
            f"# Photo training document {name}: template {language}/{template.name},",
            f"# seed {seed!r}. Generated by benchmark.photo_train; every value is invented.",
            f"language = {_string(language)}",
            f"kind = {_string(template.kind)}",
            "lines = [",
            *(f"  {_string(line)}," for line in lines),
            "]",
            f"decoys = [{', '.join(_string(decoy) for decoy in decoys)}]",
            "",
        ]
    )


def _string(text: str) -> str:
    """Return a TOML basic string; JSON's escapes are valid TOML."""
    return json.dumps(text, ensure_ascii=False)


def _fill(
    line: str, people: dict[str, Person], values: dict[str, str], language: str, used: set[str]
) -> str:
    def replace(found: re.Match[str]) -> str:
        if found["doc"]:
            used.add(found["doc"])
            return values[found["doc"]]
        person = people[found["person"]]
        if found["slot"] is None:
            return found["female"] if person.female else found["male"]
        lead, value, kind = _slot(person, found["slot"], found["form"], language)
        if found["preposition"]:
            lead = _preposition(found["preposition"], lead + value, language) + " " + lead
        return f"{lead}[[{kind}:{value}]]"

    return _PLACEHOLDER.sub(replace, line)


def _preposition(written: str, following: str, language: str) -> str:
    vocalised, before = _VOCALISED[language][written]
    return vocalised if following[:1].lower() in before else written


def _slot(person: Person, slot: str, form: str | None, language: str) -> tuple[str, str, str]:
    """Return the text before the value, the value and its entity type."""
    if slot in _VALUE_SLOTS:
        if form is not None:
            msg = f"{slot} takes no form"
            raise ValueError(msg)
        return "", _value(person, slot), _VALUE_SLOTS[slot]
    if slot not in _NAME_SLOTS:
        msg = f"unknown slot {slot!r}"
        raise ValueError(msg)
    if slot == "rev":
        if form is not None:
            msg = "rev takes no form"
            raise ValueError(msg)
        return "", f"{person.surname.word} {person.first.word}", "person"
    if form is None:
        msg = f"{slot} needs a form"
        raise ValueError(msg)
    if slot == "sposs":
        return "", possessive(person.family_surname, Agreement(form), language), "person"
    case = Case(form)
    surname = decline(person.surname, case, language)
    if slot == "full":
        first = decline(person.first, case, language, before_surname=True)
        return "", f"{first} {surname}", "person"
    if slot == "titled":
        return title(person.female, case, language) + " ", surname, "person"
    if slot == "surname":
        return "", surname, "person"
    if slot == "initial":
        return "", f"{person.first.word[0]}. {surname}", "person"
    return "", decline(person.first, case, language), "person"


def _value(person: Person, slot: str) -> str:
    born = person.born
    values = {
        "addr": person.address,
        "rc": person.birth_number,
        "born": f"{born.day}. {born.month}. {born.year}",
        "phone": person.phone,
        "email": person.email,
        "account": person.account,
        "iban": person.iban,
    }
    return values[slot]
