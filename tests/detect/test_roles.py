"""Tests for cutting model person and address spans back to the value."""

import pytest
from anonymizer.core.detect import (
    CombinedDetector,
    GlinerDetector,
    NamesOnly,
    cut_to_address,
    cut_to_name,
    role_words_for,
)
from anonymizer.core.detect.roles import (
    CZECH_ROLE_WORDS,
    ENGLISH_ROLE_WORDS,
    SLOVAK_ROLE_WORDS,
)
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


@pytest.mark.parametrize(
    "span", ["Adult", "Adult at Risk", "Student", "Gender", "PERSON", "Next of Kin", "Parent/Carer"]
)
def test_english_roles_and_field_names_are_dropped(span: str):
    assert _cut(span, "en") is None


@pytest.mark.parametrize(
    ("span", "expected"),
    [
        ("Jane Doe", "Jane Doe"),
        ("Student Jane Doe", "Student Jane Doe"),
        # Surnames that are also role nouns are not on the list.
        ("Child", "Child"),
        ("Judge", "Judge"),
    ],
)
def test_english_names_are_kept(span: str, expected: str):
    assert _cut(span, "en") == expected


def test_role_words_follow_the_language():
    assert _cut("Kupující", "en") == "Kupující"
    assert _cut("Kupující", None) is None
    assert _cut("Kupujúci", "cs-CZ") == "Kupujúci"
    assert _cut("Adult", "cs") == "Adult"
    assert role_words_for("de") == CZECH_ROLE_WORDS | SLOVAK_ROLE_WORDS | ENGLISH_ROLE_WORDS


def test_offsets_refer_to_the_whole_text():
    text = "Smlouvu podepsal pan Jan Novák dnes."
    start = text.index("pan")
    assert cut_to_name(text, start, start + len("pan Jan Novák"), CZECH_ROLE_WORDS) == (
        text.index("Jan"),
        text.index(" dnes"),
    )


def _address(text: str) -> str | None:
    span = cut_to_address(text, 0, len(text))
    return None if span is None else text[span[0] : span[1]]


@pytest.mark.parametrize(
    "span",
    [
        "Address",
        "Home Address",
        "Contact Address:",
        "Post Code",
        "Postcode",
        "Telephone Number",
        "Tel. No.",
        "E-mail Address",
        "Adresa trvalého bydliště",
        "Místo trvalého pobytu",
        "PSČ",
        "Telefonní číslo",
        "Kontaktná adresa",
    ],
)
def test_address_labels_alone_are_dropped(span: str):
    assert _address(span) is None


@pytest.mark.parametrize(
    ("span", "expected"),
    [
        ("Post Code AB1 2CD", "AB1 2CD"),
        ("Post Code: AB1 2CD", "AB1 2CD"),
        ("Contact Address 12 Mill Lane", "12 Mill Lane"),
        ("12 Mill Lane Post Code", "12 Mill Lane"),
        ("Home Address: 12 Mill Lane, Post Code AB1 2CD", "12 Mill Lane, Post Code AB1 2CD"),
        ("Adresa: Kounicova 12, 602 00 Brno", "Kounicova 12, 602 00 Brno"),
        ("PSČ 602 00 Brno", "602 00 Brno"),
        # A qualifying word without the word it qualifies may be a place.
        ("Home Farm, Mill Lane 4", "Home Farm, Mill Lane 4"),
        ("Post Office Lane 3", "Post Office Lane 3"),
        ("12 Mill Lane Home", "12 Mill Lane Home"),
        ("Address Home Farm", "Home Farm"),
        ("náměstí Míru 5", "náměstí Míru 5"),
        ("Kounicova 12", "Kounicova 12"),
    ],
)
def test_address_labels_are_trimmed_from_the_edges(span: str, expected: str):
    assert _address(span) == expected


def test_address_offsets_refer_to_the_whole_text():
    text = "Form. Post Code AB1 2CD Telephone"
    start = text.index("Post")
    assert cut_to_address(text, start, len(text)) == (text.index("AB1"), text.index(" Telephone"))


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


FORM = "Adult Post Code Telephone Number\nJane Doe AB1 2CD 0123 456789"


def test_wrapper_drops_form_headers_and_keeps_the_values():
    model = StandInModel(
        {
            "Adult": "person",
            "Post Code": "street address",
            "Telephone Number": "street address",
            "Jane Doe": "person",
            "AB1 2CD": "street address",
        }
    )
    detector = NamesOnly(GlinerDetector(model), "en")
    entities = detector.detect(_page(FORM))
    assert [(entity.type, entity.text) for entity in entities] == [
        (EntityType.PERSON, "Jane Doe"),
        (EntityType.ADDRESS, "AB1 2CD"),
    ]


def test_wrapper_trims_an_address_label_and_its_box():
    text = "Post Code AB1 2CD"
    detector = NamesOnly(GlinerDetector(StandInModel({text: "street address"})), "en")
    (entity,) = detector.detect(_page(text))
    assert entity.text == "AB1 2CD"
    assert text[slice(*entity.span)] == "AB1 2CD"
    assert len(entity.bboxes) == 2


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
