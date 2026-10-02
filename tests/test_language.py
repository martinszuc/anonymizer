"""Tests for recognising a document's language from its text."""

import pytest
from anonymizer.core.language import AUTO, detect_language, recognise_language
from anonymizer.core.pipeline import resolve_language
from anonymizer.core.types import Document, Page

CZECH = (
    "Kupující převezme zboží v provozovně prodávajícího a zaplatí kupní cenu převodem "
    "na účet do sedmi dnů. Reklamaci lze uplatnit písemně nebo osobně v prodejně."
)
SLOVAK = (
    "Kupujúci prevezme tovar v prevádzke predávajúceho a zaplatí kúpnu cenu prevodom "
    "na účet do siedmich dní. Reklamáciu je možné uplatniť písomne alebo osobne v predajni."
)
ENGLISH = (
    "The buyer collects the goods at the seller's shop and pays the price by bank "
    "transfer within seven days. Complaints may be made in writing or in person."
)
GERMAN = (
    "Der Käufer holt die Ware im Geschäft des Verkäufers ab und bezahlt den Preis "
    "innerhalb von sieben Tagen per Überweisung. Reklamationen sind schriftlich möglich."
)


def _document(*texts: str) -> Document:
    return Document(
        pages=[Page(index=i, width=595, height=842, text=text) for i, text in enumerate(texts)]
    )


@pytest.mark.parametrize(("text", "language"), [(CZECH, "cs"), (SLOVAK, "sk"), (ENGLISH, "en")])
def test_languages_with_their_own_rules_are_recognised(text: str, language: str):
    assert recognise_language(text) == language


@pytest.mark.parametrize(
    "text",
    [
        GERMAN,  # no rules of its own: every rule runs
        "Jan Novák, +420 777 123 456",  # too short to judge
        "1234 5678 / 9012 " * 40,  # no letters
        "",
    ],
)
def test_other_languages_and_short_texts_are_not_answered(text: str):
    assert recognise_language(text) is None


def test_a_document_is_judged_by_all_its_pages():
    assert detect_language(_document(CZECH[:60], CZECH[60:])) == "cs"


class TestResolveLanguage:
    def test_auto_recognises_and_records_the_language(self):
        document = _document(SLOVAK)
        assert resolve_language(document, AUTO) == "sk"
        assert document.language == "sk"

    def test_auto_without_an_answer_runs_every_rule(self):
        document = _document(GERMAN)
        assert resolve_language(document, AUTO) is None
        assert document.language is None

    @pytest.mark.parametrize("requested", ["cs", None])
    def test_a_chosen_language_is_kept(self, requested: str | None):
        document = _document(ENGLISH)
        assert resolve_language(document, requested) == requested
        assert document.language == requested
