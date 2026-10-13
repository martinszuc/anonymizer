"""The held-out synthetic set: reproducible, valid values, disjoint from every other template."""

import ast
import hashlib
import json
import random
import re
import tomllib
import unicodedata
from collections import Counter
from datetime import date
from itertools import pairwise
from pathlib import Path

import pytest
from anonymizer.core.detect.bank_account import is_valid_account_number
from anonymizer.core.detect.birth_number import is_valid_birth_number
from anonymizer.core.detect.iban import is_valid_iban
from anonymizer.core.detect.roles import role_words_for
from anonymizer.core.types import EntityType

from benchmark.spec import load_documents
from experiments import heldout, name_forms
from experiments.config import parse_config
from experiments.datasets import DATASETS, Role, dataset_version, load_corpus
from experiments.declension import Name, Paradigm, feminine_surname
from experiments.heldout import (
    CONTROLS,
    HELDOUT_VERSION,
    INSTANCES,
    NAMES,
    TEMPLATES,
    GoldSpan,
    Person,
    Template,
    generate,
    render,
)
from experiments.train import parse_train_config

LANGUAGES = ("cs", "sk")
PAIRS = [(language, split) for language in LANGUAGES for split in ("dev", "test")]
REPOSITORY = Path(__file__).parents[2]

GENERATED = {
    "1": {
        ("cs", "dev"): "04168ae0efc49ad67e8e8310639f5de3d4d8becf253f9bbe61679ff0e4fd7622",
        ("cs", "test"): "eefd5f03c0dd2ce6eb3a5c6eb2e9640313d92657ddf25efaef7aa38a9e79a04d",
        ("sk", "dev"): "b27930ffb57c4469f725a8026ccccf5a9c1fd318435a4bb39bbf5623a0eb0b02",
        ("sk", "test"): "276e4d40cd8160036c46b93a21ddd81f0eaf572bdbf06d422a53177136f06d8e",
    }
}
"""SHA-256 of each generated split, per version: changing the documents must bump the version."""


def _digest(language: str, split: str) -> str:
    documents = [
        [
            document.template,
            document.text,
            [
                [str(span.type), span.start, span.end, list(map(list, span.tags))]
                for span in document.spans
            ],
        ]
        for document in generate(language, split)
    ]
    return hashlib.sha256(json.dumps(documents, ensure_ascii=False).encode()).hexdigest()


@pytest.mark.parametrize(("language", "split"), PAIRS)
def test_the_documents_are_the_version_they_claim(language: str, split: str):
    assert _digest(language, split) == GENERATED[HELDOUT_VERSION][language, split]


def test_generation_is_reproducible():
    assert generate("sk", "test") == generate("sk", "test")


@pytest.mark.parametrize(("language", "split"), PAIRS)
def test_every_gold_span_is_a_whole_value(language: str, split: str):
    documents = generate(language, split)
    templates = TEMPLATES[language][split]
    assert len(documents) == INSTANCES[split] * len(templates) + len(CONTROLS[language][split])
    for document in documents:
        text = document.text
        assert unicodedata.normalize("NFC", text) == text
        ordered = sorted(document.spans, key=lambda span: span.start)
        for first, second in pairwise(ordered):
            assert first.end <= second.start, document.template
        for span in document.spans:
            value = text[span.start : span.end]
            before, after = text[span.start - 1 : span.start], text[span.end : span.end + 1]
            assert value == value.strip() and value
            assert not before.isalnum() and not after.isalnum(), value
            _check_value(span, value)


def _check_value(span: GoldSpan, value: str) -> None:
    if span.type is EntityType.PERSON:
        tags = dict(span.tags)
        assert value[:1].isupper(), value
        assert not re.search(r"\b(pan|paní|pane|pán|pani|pána|MUDr|Mgr|Ing)\b", value), value
        words = 2 if tags["form"] in {"full", "initial", "surname-first"} else 1
        assert len(value.split()) == words, value
        assert tags.keys() >= {"form", "form-case", "class", "gender", "context", "kind"}
    elif span.type is EntityType.ADDRESS:
        assert re.fullmatch(r"[^\W\d][\w ]* \d+(/\d+)?[,\n] ?\d{3} \d{2} \w[\w ]*", value), value
    elif span.type is EntityType.EMAIL:
        assert re.fullmatch(r"[a-z.]+@example\.(com|org|net)", value), value
    elif span.type is EntityType.PHONE:
        assert re.fullmatch(r"(\+42[01] |0)?[679]\d\d \d{3} \d{3}", value), value
    elif span.type is EntityType.DATE:
        day, month, year = map(int, value.split(". "))
        assert date(year, month, day)
    else:
        assert not span.tags


@pytest.mark.parametrize(("language", "split"), PAIRS)
def test_checksum_values_pass_the_core_validators(language: str, split: str):
    """The generator computes check digits itself; the pipeline's validators must agree."""
    counts: Counter[EntityType] = Counter()
    for document in generate(language, split):
        for span in document.spans:
            value = document.text[span.start : span.end]
            if span.type is EntityType.BIRTH_NUMBER:
                assert is_valid_birth_number(value), value
            elif span.type is EntityType.BANK_ACCOUNT:
                number, _, _ = value.partition("/")
                prefix, _, base = number.rpartition("-")
                assert is_valid_account_number(base, prefix or None), value
            elif span.type is EntityType.IBAN:
                assert value.startswith({"cs": "CZ", "sk": "SK"}[language])
                assert is_valid_iban(value), value
            counts[span.type] += 1
    if split == "test":
        assert counts[EntityType.BIRTH_NUMBER] and counts[EntityType.DATE]
        assert counts[EntityType.BANK_ACCOUNT] or counts[EntityType.IBAN]


def test_a_birth_number_encodes_the_date_of_birth_and_gender():
    person = _person(female=True)
    digits = person.birth_number.replace("/", "")
    assert int(digits) % 11 == 0
    assert digits[:6] == "855314"  # 14 March 1985, month + 50 for a woman


@pytest.mark.parametrize(("language", "split"), PAIRS)
def test_documents_naming_nobody_have_no_gold(language: str, split: str):
    controls = generate(language, split)[-len(CONTROLS[language][split]) :]
    assert controls
    assert all(not document.spans for document in controls)
    roles = role_words_for(language)
    for document in controls:  # capitalised role nouns inside a sentence, as contracts write them
        inner = re.findall(r"(?<=\w )[^\W\d_]+", document.text)
        assert any(word[0].isupper() and word.lower() in roles for word in inner), document.template


# Minimum counts per test split: the forms models miss on dev must be there in numbers.
MINIMUM = {
    "cs": {
        "later-surname/nom": 150,
        "lone-surname/nom": 8,
        "nickname": 40,
        "surname-possessive": 8,
        "first-name-possessive": 24,
        "title-surname": 40,
        "initial": 40,
        "surname-first": 16,
        "role-noun": 250,
        "degree": 40,
        "label": 200,
    },
    "sk": {
        "later-surname/nom": 100,
        "lone-surname/nom": 8,
        "nickname": 40,
        "surname-possessive": 8,
        "first-name-possessive": 16,
        "title-surname": 8,
        "initial": 24,
        "surname-first": 16,
        "role-noun": 150,
        "degree": 16,
        "label": 150,
    },
}


@pytest.mark.parametrize("language", LANGUAGES)
def test_the_test_half_covers_the_forms_models_miss(language: str):
    counts: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    for document in generate(language, "test"):
        for span in document.spans:
            for facet, value in span.tags:
                if facet in {"form", "form-case", "context"}:
                    counts[value] += 1
    for template in TEMPLATES[language]["test"]:
        kinds[template.kind] += 1
    for name, minimum in MINIMUM[language].items():
        assert counts[name] >= minimum, (name, counts[name])
    assert set(kinds) == set(heldout.KINDS)
    assert min(kinds.values()) >= 3
    genders = Counter(
        dict(span.tags)["gender"]
        for document in generate(language, "test")
        for span in document.spans
        if span.tags
    )
    assert min(genders.values()) > 0.35 * sum(genders.values())


def _name_words(lists: name_forms.NameLists) -> set[str]:
    names = (
        *lists.male_first,
        *lists.female_first,
        *lists.surnames,
        *lists.nicknames.values(),
        *lists.foreign_male_first,
        *lists.foreign_female_first,
        *lists.foreign_surnames,
    )
    return {name.word for name in names} | {feminine_surname(name).word for name in lists.surnames}


@pytest.mark.parametrize("language", LANGUAGES)
def test_dev_and_test_share_no_name_and_no_template(language: str):
    assert not _name_words(NAMES[language]["dev"]) & _name_words(NAMES[language]["test"])
    halves = {
        split: [*TEMPLATES[language][split], *CONTROLS[language][split]]
        for split in ("dev", "test")
    }
    dev_grams = set().union(*(_template_grams(template) for template in halves["dev"]))
    for template in halves["test"]:
        assert not _template_grams(template) & dev_grams, template.name


def test_names_are_new_to_the_benchmark_and_the_name_forms_set():
    benchmark = {
        word
        for spec in load_documents()
        for item in spec.gold
        if item.type is EntityType.PERSON
        for word in item.text.split()
    }
    name_forms_words = set().union(
        *(_name_words(lists) for splits in name_forms.NAMES.values() for lists in splits.values())
    )
    for splits in NAMES.values():
        for lists in splits.values():
            words = _name_words(lists)
            assert not words & benchmark
            assert not words & name_forms_words


# --- Disjoint templates ----------------------------------------------------------

GRAM = 5
"""Words in a shared phrase that counts as a reused template."""

SCANNED = ("experiments", "benchmark", "scripts")
"""Directories whose Python string constants and TOML strings hold every other template.

A generator of training data added outside them must add its directory here.
"""

_ALTERNATIVE = re.compile(r"\{[A-Z]\?([^|{}]*)\|[^{}]*\}")
_SLOT = re.compile(r"\{[^{}]*\}|\[\[[a-z_]+:[^\[\]]*\]\]")
_TOKEN = re.compile(r"\w+|□")


def _grams(line: str) -> set[tuple[str, ...]]:
    """Word 5-grams of a line: gender alternatives as their masculine text, slots as □."""
    line = _SLOT.sub(" □ ", _ALTERNATIVE.sub(r"\1", line))
    words = _TOKEN.findall(line.lower())
    return {tuple(words[index : index + GRAM]) for index in range(len(words) - GRAM + 1)}


def _template_grams(template: Template) -> set[tuple[str, ...]]:
    return set().union(*(_grams(line) for line in template.lines))


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def _other_texts() -> list[str]:
    """Every string written in the scanned directories, except this set's own module."""
    own = Path(heldout.__file__).resolve()
    texts: list[str] = []
    for directory in SCANNED:
        for path in sorted((REPOSITORY / directory).rglob("*.py")):
            if path.resolve() == own:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            texts += [
                node.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
            ]
        for path in sorted((REPOSITORY / directory).rglob("*.toml")):
            texts += _strings(tomllib.loads(path.read_text(encoding="utf-8")))
    return texts


def test_the_scan_sees_the_other_templates():
    texts = _other_texts()
    assert any("{P.full.nom}" in text for text in texts)  # name_forms.py
    assert any("[[person:" in text for text in texts)  # benchmark documents


@pytest.mark.parametrize("language", LANGUAGES)
def test_no_template_shares_a_phrase_with_any_other_template(language: str):
    other = set().union(*(_grams(line) for text in _other_texts() for line in text.split("\n")))
    for split in ("dev", "test"):
        for template in (*TEMPLATES[language][split], *CONTROLS[language][split]):
            shared = _template_grams(template) & other
            assert not shared, (template.name, sorted(shared)[:3])


def test_a_shared_phrase_is_seen_through_slots_and_alternatives():
    held_out = "Smlouvu podepsal{A?|a} {A.full.nom} dne 3. května."
    reused = "Smlouvu podepsal{P?|a} {P.full.nom} dne 3. května."
    benchmark = "Smlouvu podepsal [[person:Jan Novák]] dne 3. května."
    assert _grams(held_out) == _grams(reused) == _grams(benchmark)
    assert not _grams("Smlouvu podepsal dne") & _grams(held_out)


# --- Registration ----------------------------------------------------------------


@pytest.mark.parametrize("language", LANGUAGES)
def test_registered_as_test_data_without_a_train_split(language: str, tmp_path: Path):
    dataset = f"heldout-{language}"
    spec = DATASETS[dataset]
    assert spec.splits == {"dev": Role.DEV, "test": Role.TEST}
    assert spec.generated == HELDOUT_VERSION == dataset_version(dataset)
    corpus = load_corpus(dataset, "dev", tmp_path)
    assert corpus.tagged
    assert corpus.types == heldout.TYPES
    for gold in corpus.documents:
        page = gold.document.pages[0]
        for entity in gold.gold:
            start, end = entity.span
            assert entity.text == page.text[start:end]
            assert (entity.type is EntityType.PERSON) == ((0, start, end) in gold.tags)


def test_the_test_half_needs_the_final_stage():
    config = {
        "name": "heldout",
        "datasets": [{"id": "heldout-sk", "split": "test"}],
        "systems": {"rules": {}},
    }
    with pytest.raises(ValueError, match="test data"):
        parse_config(config)
    assert parse_config({**config, "stage": "final"}).stage == "final"


@pytest.mark.parametrize("split", ["dev", "test", "train"])
def test_training_never_reads_the_set(split: str):
    config = {
        "name": "train-heldout",
        "model": "gliner-heldout-test",
        "corpora": [{"id": "heldout-cs", "split": split}],
    }
    with pytest.raises(ValueError, match="not a train split"):
        parse_train_config(config)


# --- Rendering -------------------------------------------------------------------


def _person(*, female: bool) -> Person:
    first = Name("Jarmila", Paradigm.A_FEM) if female else Name("Libor", Paradigm.HARD)
    family = Name("Polák", Paradigm.HARD)
    return Person(
        female=female,
        first=first,
        surname=feminine_surname(family) if female else family,
        family_surname=family,
        nickname=Name("Jarka", Paradigm.A_FEM) if female else None,
        street="Lipová 12",
        town="390 01 Tábor",
        born=date(1985, 3, 14),
        birth_number=heldout.birth_number(date(1985, 3, 14), female=female, draw=random.Random(0)),
        phone="602 111 222",
        email="j.polakova@example.com",
        account="19-123457/0800",
        iban="CZ00",
    )


def test_render_marks_values_forms_and_contexts():
    template = Template(
        "render-check",
        "letter",
        (
            "Nájemkyně: {A.full.nom}, bytem {A.addrblock}",
            "{A.surname.nom} a {B.surname.nom} se dohodli. Svědek {B.initial.nom} souhlasí.",
            "MUDr. {B.full.ins}, {A.rev}, {M.sposs.f} sestra",
        ),
    )
    people = {"A": _person(female=True), "B": _person(female=False), "M": _person(female=False)}
    document = render(template, people, "cs")
    found = [
        (
            document.text[span.start : span.end],
            dict(span.tags).get("form-case"),
            tuple(value for facet, value in span.tags if facet == "context"),
        )
        for span in document.spans
    ]
    assert found == [
        ("Jarmila Poláková", "full/nom", ("role-noun", "label")),
        ("Lipová 12\n390 01 Tábor", None, ()),
        ("Poláková", "later-surname/nom", ("plain",)),
        ("Polák", "lone-surname/nom", ("plain",)),
        ("L. Polák", "initial/nom", ("role-noun",)),
        ("Liborem Polákem", "full/ins", ("degree",)),
        ("Poláková Jarmila", "surname-first/nom", ("plain",)),
        ("Polákova", "surname-possessive", ("plain",)),
    ]
    assert all(("kind", "letter") in span.tags for span in document.spans if span.tags)


def test_a_womans_surname_has_no_possessive():
    template = Template("bad", "letter", ("{W.sposs.f} dům",))
    with pytest.raises(ValueError, match="no possessive"):
        heldout._cast(template, NAMES["cs"]["dev"], random.Random(0), 0, "cs")
