"""Tests for cutting model person spans back to the name."""

import pytest
from anonymizer.core.detect import (
    CombinedDetector,
    GlinerDetector,
    NamesOnly,
    cut_to_name,
    role_words_for,
)
from anonymizer.core.detect.roles import CZECH_ROLE_WORDS, SLOVAK_ROLE_WORDS
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.types import Document, EntityType

from tests.detect.test_gliner import StandInModel, _page


def _cut(text: str, language: str | None = "cs") -> str | None:
    span = cut_to_name(text, 0, len(text), role_words_for(language))
    return None if span is None else text[span[0] : span[1]]


@pytest.mark.parametrize(
    ("span", "expected"),
    [
        ("Jan Novák", "Jan Novák"),
        ("Janu Novákovi", "Janu Novákovi"),
        ("JAN NOVÁK", "JAN NOVÁK"),
        ("pan Jan Novák", "Jan Novák"),
        ("Jan Novák, který", "Jan Novák"),
        ("(Jan Novák)", "Jan Novák"),
        ("doc. Ing. Jan Novák", "doc. Ing. Jan Novák"),
        ("Jan z Lobkovic", "Jan z Lobkovic"),
        ("Ludwig van Beethoven", "Ludwig van Beethoven"),
        # A role word beside a name stays: cutting it is not worth the risk.
        ("Prodávající Jan Novák", "Prodávající Jan Novák"),
        # Surnames that are also role nouns are not on the lists.
        ("Starosta města", "Starosta"),
        ("Žák", "Žák"),
    ],
)
def test_names_are_kept_and_lowercase_edges_trimmed(span: str, expected: str):
    assert _cut(span) == expected


@pytest.mark.parametrize(
    "span",
    [
        "Kupující",
        "Kupujícímu",
        "Prodávajícího",
        "Spotřebiteli",
        "Žadatele",
        "Zákonný zástupce nezletilého žáka",
        "Vedoucí odboru sociálních věcí a školství",
        "Referent odboru",
        "Smluvní strany",
        "Matrikářka",
        "žák",
        "zletilý student",
        "a",
        "( )",
    ],
)
def test_czech_roles_and_lowercase_spans_are_dropped(span: str):
    assert _cut(span) is None


@pytest.mark.parametrize(
    "span", ["Kupujúci", "Predávajúcemu", "Spotrebiteľ", "Žiadateľovi", "Zákonný zástupca"]
)
def test_slovak_roles_are_dropped(span: str):
    assert _cut(span, "sk") is None


def test_role_words_follow_the_language():
    assert _cut("Kupující", "en") == "Kupující"
    assert _cut("Kupující", None) is None
    assert _cut("Kupujúci", "cs-CZ") == "Kupujúci"
    assert role_words_for("de") == CZECH_ROLE_WORDS | SLOVAK_ROLE_WORDS


def test_offsets_refer_to_the_whole_text():
    text = "Smlouvu podepsal pan Jan Novák dnes."
    start = text.index("pan")
    assert cut_to_name(text, start, start + len("pan Jan Novák"), CZECH_ROLE_WORDS) == (
        text.index("Jan"),
        text.index(" dnes"),
    )


TEXT = "Kupující převezme zboží. Kupní cenu zaplatí pan Jan Novák, Kounicova 12."


def test_wrapper_trims_drops_and_passes_other_types():
    model = StandInModel(
        {"Kupující": "person", "pan Jan Novák": "person", "Kounicova 12": "street address"}
    )
    detector = NamesOnly(GlinerDetector(model), "cs")
    entities = detector.detect(_page(TEXT))
    assert [(entity.type, entity.text) for entity in entities] == [
        (EntityType.PERSON, "Jan Novák"),
        (EntityType.ADDRESS, "Kounicova 12"),
    ]
    name = entities[0]
    assert TEXT[slice(*name.span)] == "Jan Novák"
    assert len(name.bboxes) == 2  # "pan" no longer has a box
    assert detector.name == "gliner-multi-v2.1"


def test_pipeline_filters_the_model_and_its_repeats():
    page = _page("Kupující Jan Novák. Kupující zaplatí. Ing. Jan Novák podepsal.")
    model = GlinerDetector(
        StandInModel({"Kupující Jan Novák": "person", "Kupující": "person", "Jan Novák": "person"})
    )
    detector = build_detector("cs", model=model)
    assert isinstance(detector, CombinedDetector)
    document = Document(pages=[page], language="cs")
    run_detection(document, detector)
    # The name keeps its role word, the lone role words are gone, and the
    # name's repeat is found and widened over its title.
    assert sorted(entity.text or "" for entity in document.entities) == [
        "Ing. Jan Novák",
        "Kupující Jan Novák",
    ]
