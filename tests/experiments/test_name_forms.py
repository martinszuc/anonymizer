"""The name-forms set: reproducible, split cleanly, and loadable as a corpus without files."""

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pytest
from anonymizer.core.types import EntityType

from experiments.config import parse_config
from experiments.datasets import DATASETS, Role, dataset_version, load_corpus
from experiments.declension import Name, Paradigm
from experiments.name_forms import (
    CONTROLS,
    INSTANCES,
    NAME_FORMS_VERSION,
    NAMES,
    TEMPLATES,
    Person,
    generate,
    render,
)

LANGUAGES = ("cs", "sk")
PAIRS = [(language, split) for language in LANGUAGES for split in ("dev", "test")]

GENERATED = {
    "1": {
        ("cs", "dev"): "80107f42b4f58853d3bca5e7415228e5e4ca5f8f281f15b8b450e7f059ba304d",
        ("cs", "test"): "658d10ab87b3acaa95e04c7ca672570908da8ace1e9ed4bbe839900ba9ec5cce",
        ("sk", "dev"): "5865fccae0dd31f431d6cf7c627f32f9a575aa48196806cc6f0112804d99acee",
        ("sk", "test"): "14854bc8328640721e33af3f1308e0fff7af2e3263bea5c08cb9cbc2a0307f53",
    }
}
"""SHA-256 of each generated split, per version: changing the texts must bump the version."""


def _digest(language: str, split: str) -> str:
    texts = [
        [text.text, [[name.start, name.end, list(map(list, name.tags))] for name in text.names]]
        for text in generate(language, split)
    ]
    return hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode()).hexdigest()


@pytest.mark.parametrize(("language", "split"), PAIRS)
def test_the_texts_are_the_version_they_claim(language: str, split: str):
    assert _digest(language, split) == GENERATED[NAME_FORMS_VERSION][language, split]


@pytest.mark.parametrize(("language", "split"), PAIRS)
def test_every_gold_span_is_a_whole_name(language: str, split: str):
    texts = generate(language, split)
    assert len(texts) == INSTANCES * len(TEMPLATES[language][split]) + len(
        CONTROLS[language][split]
    )
    for text in texts:
        assert unicodedata.normalize("NFC", text.text) == text.text
        for name in text.names:
            value = text.text[name.start : name.end]
            before = text.text[name.start - 1 : name.start]
            after = text.text[name.end : name.end + 1]
            assert value[:1].isupper(), value
            assert not before.isalpha() and not after.isalpha(), value
            assert not re.search(r"\b(pan|paní|pane|pán|pani|s|se|so)\b", value), value
            tags = dict(name.tags)
            assert tags.keys() >= {"form", "form-case", "class", "gender"}
            words = 2 if tags["form"] in {"full", "foreign-full"} else 1
            assert len(value.split()) == words, value


@pytest.mark.parametrize(("language", "split"), PAIRS)
def test_control_texts_name_nobody(language: str, split: str):
    controls = [text for text in generate(language, split) if not text.names]
    assert len(controls) == len(CONTROLS[language][split]) >= 4


@pytest.mark.parametrize("language", LANGUAGES)
def test_dev_and_test_share_no_name_and_no_template(language: str):
    dev, test = NAMES[language]["dev"], NAMES[language]["test"]

    def words(lists) -> set[str]:
        names = (
            *lists.male_first,
            *lists.female_first,
            *lists.surnames,
            *lists.nicknames.values(),
            *lists.foreign_male_first,
            *lists.foreign_female_first,
            *lists.foreign_surnames,
        )
        return {name.word for name in names}

    assert not words(dev) & words(test)
    assert not set(TEMPLATES[language]["dev"]) & set(TEMPLATES[language]["test"])
    assert not set(CONTROLS[language]["dev"]) & set(CONTROLS[language]["test"])


def test_generation_is_reproducible():
    assert generate("cs", "dev") == generate("cs", "dev")


@pytest.mark.parametrize(("language", "split"), PAIRS)
def test_every_case_of_full_names_and_titled_surnames_is_covered(language: str, split: str):
    cells = Counter(
        dict(name.tags)["form-case"] for text in generate(language, split) for name in text.names
    )
    cases = ("nom", "gen", "dat", "acc", "voc", "loc", "ins")
    for form in ("full", "title-surname"):
        for case in cases:
            if language == "sk" and case == "voc":
                assert cells[f"{form}/voc"] == 0
            else:
                assert cells[f"{form}/{case}"] >= INSTANCES, f"{form}/{case}"
    expected_forms = {"later-surname", "first-name", "nickname", "surname-possessive"}
    if language == "cs":
        expected_forms |= {"foreign-full", "foreign-first"}
    forms = {cell.split("/")[0] for cell in cells}
    assert forms >= expected_forms


def test_render_marks_names_and_vocalises_prepositions():
    woman = Person(
        female=True,
        first=Name("Zuzana", Paradigm.A_FEM),
        surname=Name("Svobodová", Paradigm.OVA),
        nickname=None,
        foreign=False,
    )
    text = render(
        "Smlouvu {P?podepsal|podepsala} {P.full.nom}. Jednáme {s~P.titled.ins} a {s~P.first.ins}.",
        {"P": woman},
        "cs",
    )
    assert (
        text.text == "Smlouvu podepsala Zuzana Svobodová. Jednáme s paní Svobodovou a se Zuzanou."
    )
    spans = [
        (text.text[name.start : name.end], dict(name.tags)["form-case"]) for name in text.names
    ]
    assert spans == [
        ("Zuzana Svobodová", "full/nom"),
        ("Svobodovou", "title-surname/ins"),
        ("Zuzanou", "first-name/ins"),
    ]


@pytest.mark.parametrize("language", LANGUAGES)
def test_a_generated_dataset_loads_without_files(language: str, tmp_path: Path):
    dataset = f"name-forms-{language}"
    corpus = load_corpus(dataset, "dev", tmp_path)
    assert corpus.version == NAME_FORMS_VERSION == dataset_version(dataset)
    assert corpus.types == frozenset({EntityType.PERSON})
    assert corpus.tagged
    assert DATASETS[dataset].splits == {"dev": Role.DEV, "test": Role.TEST}
    tagged = [gold for gold in corpus.documents if gold.gold]
    for gold in tagged:
        page = gold.document.pages[0]
        for entity in gold.gold:
            start, end = entity.span
            assert entity.text == page.text[start:end]
            assert gold.tags[0, start, end]
    limited = load_corpus(dataset, "dev", tmp_path, limit=5)
    assert len(limited.documents) == 5


def test_the_test_half_needs_the_final_stage():
    config = {
        "name": "forms",
        "datasets": [{"id": "name-forms-cs", "split": "test"}],
        "systems": {"rules": {}},
    }
    with pytest.raises(ValueError, match="test data"):
        parse_config(config)
    assert parse_config({**config, "stage": "final"}).stage == "final"
