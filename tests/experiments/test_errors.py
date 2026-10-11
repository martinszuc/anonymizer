"""Error analysis: categories on hand-made text, counts, and whole runs on synthetic corpora.

Every name is invented.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.detect.roles import role_words_for
from anonymizer.core.types import Document, Entity, EntityType

from experiments.__main__ import main
from experiments.config import parse_config
from experiments.datasets import GoldDocument, make_page
from experiments.errors import (
    ALARM_CATEGORIES,
    ALL,
    MISS_CATEGORIES,
    AlarmCounts,
    ErrorTally,
    MissCounts,
    Span,
    alarm_categories,
    analyse,
    check_examples_folder,
    gold_spans,
    is_synthetic,
    markdown,
    shape,
)
from experiments.metrics import Resampler, resamples
from experiments.run import run
from tests.experiments.conftest import ScoredStandIn
from tests.experiments.test_run import CONFIG, FOUND

PERSON, ADDRESS, ORGANIZATION = EntityType.PERSON, EntityType.ADDRESS, EntityType.ORGANIZATION


def _shape_of(text: str, value: str, occurrence: int = 0) -> set[str]:
    start = -1
    for _ in range(occurrence + 1):
        start = text.index(value, start + 1)
    return shape(text, start, start + len(value))


class TestShape:
    @pytest.mark.parametrize(
        ("value", "category"),
        [("Novák", "words=1"), ("Jan Novák", "words=2"), ("Jan Maria Nováková", "words=3+")],
    )
    def test_words(self, value: str, category: str):
        categories = _shape_of(f"Volal {value} včera.", value)
        assert category in categories
        assert len(categories & {"words=1", "words=2", "words=3+"}) == 1

    def test_a_double_surname_is_one_word_and_has_a_hyphen(self):
        categories = _shape_of("Volala Nováková-Svobodová.", "Nováková-Svobodová")
        assert {"words=1", "hyphen_apostrophe"} <= categories

    @pytest.mark.parametrize(
        ("text", "value"),
        [
            ("Volal pan Novák včera.", "Novák"),
            ("Pozdravujte pane Nováku.", "Nováku"),
            ("Přišla paní Nováková.", "Nováková"),
            ("Prišiel pán Kováč.", "Kováč"),
            ("Smlouvu podepsal Ing. Jan Novák.", "Jan Novák"),
            ("Smlouvu podepsal Ing. Jan Novák.", "Ing. Jan Novák"),
            ("Letter from Mr. Smith.", "Smith"),
            ("Posudek: doc. MUDr. Eva Malá.", "Eva Malá"),
        ],
    )
    def test_title_or_honorific(self, text: str, value: str):
        assert "title" in _shape_of(text, value)

    def test_no_title_before_an_ordinary_word(self):
        assert "title" not in _shape_of("Volal panu Novákovi a Jan Novák.", "Jan Novák")

    @pytest.mark.parametrize(
        ("text", "value"),
        [
            ("Novák přišel.", "Novák"),
            ("Byl tam. Novák přišel.", "Novák"),
            ("Kdo? Novák!", "Novák"),
            ("„Novák přišel,“ řekla.", "Novák"),
            ("První věta\nNovák přišel.", "Novák"),
            ("Konec. (Novák přišel.)", "Novák"),
            ("- Novák přišel.", "Novák"),
        ],
    )
    def test_sentence_start(self, text: str, value: str):
        assert "sentence_start" in _shape_of(text, value)

    @pytest.mark.parametrize(
        ("text", "value"),
        [
            ("Přišel Novák.", "Novák"),
            ("Podepsal Ing. Novák.", "Novák"),
            ("Podepsal J. Novák.", "Novák"),
            ("Přišel pan Novák.", "Novák"),
            ("Jméno: Jan Novák", "Jan Novák"),
        ],
    )
    def test_not_a_sentence_start(self, text: str, value: str):
        assert "sentence_start" not in _shape_of(text, value)

    @pytest.mark.parametrize(
        ("text", "value"),
        [
            ("Jméno: Ing. Jan Novák", "Jan Novák"),
            ("Kontaktní osoba: Eva Malá, tel. 1", "Eva Malá"),
            ("Pozn.\nZákonný zástupce dítěte: Petr Malý", "Petr Malý"),
        ],
    )
    def test_after_label(self, text: str, value: str):
        assert "after_label" in _shape_of(text, value)

    @pytest.mark.parametrize(
        ("text", "value"),
        [
            ("Volal Jan Novák.", "Jan Novák"),
            ("V dlouhé větě o mnoha slovech: Jan Novák", "Jan Novák"),
            ("12: Jan Novák", "Jan Novák"),
            ("Jan Novák: přišel", "Jan Novák"),
        ],
    )
    def test_not_after_label(self, text: str, value: str):
        assert "after_label" not in _shape_of(text, value)

    def test_all_caps_needs_two_letters(self):
        assert "all_caps" in _shape_of("Kupující: JAN NOVÁK", "JAN NOVÁK")
        assert "all_caps" not in _shape_of("Volal Jan Novák.", "Jan Novák")
        assert "all_caps" not in _shape_of("Volal J. Novák.", "J.")

    def test_apostrophes(self):
        assert "hyphen_apostrophe" in _shape_of("Met O'Brien.", "O'Brien")
        typographic = "O" + chr(0x2019) + "Brien"
        assert "hyphen_apostrophe" in _shape_of(f"Met {typographic}.", typographic)
        assert "hyphen_apostrophe" not in _shape_of("Met Jan Novák.", "Jan Novák")

    def test_diacritics(self):
        assert "diacritics" in _shape_of("Volal Jan Novák.", "Jan Novák")
        assert "diacritics" in _shape_of("Prišla Ľubica.", "Ľubica")
        assert "diacritics" not in _shape_of("Volal Jan Novak.", "Jan Novak")

    @pytest.mark.parametrize(
        ("text", "value"), [("Volal J. Novák.", "J. Novák"), ("A Jan N.", "Jan N.")]
    )
    def test_initial(self, text: str, value: str):
        assert "initial" in _shape_of(text, value)

    def test_no_initial_in_a_full_name(self):
        assert "initial" not in _shape_of("Volal Jan Novák.", "Jan Novák")


def _span(text: str, value: str, kind: EntityType = PERSON) -> Span:
    start = text.index(value)
    return Span(kind, 0, start, start + len(value))


class TestAlarmCategories:
    ROLE_WORDS = role_words_for("cs")

    def test_a_capitalised_role_noun(self):
        text = "Kupující zaplatí cenu."
        categories = alarm_categories(text, _span(text, "Kupující"), [], self.ROLE_WORDS)
        assert {"words=1", "capitalised_word", "role_noun", "sentence_start"} <= categories

    def test_a_role_noun_before_a_name(self):
        text = "Smlouvu podepsal Kupující Novák."
        categories = alarm_categories(text, _span(text, "Kupující Novák"), [], self.ROLE_WORDS)
        assert "role_noun" in categories
        assert "capitalised_word" not in categories

    def test_capitals_are_not_a_capitalised_word(self):
        text = "Vyplňte ADRESA a jméno."
        categories = alarm_categories(text, _span(text, "ADRESA"), [], self.ROLE_WORDS)
        assert "all_caps" in categories
        assert "capitalised_word" not in categories

    def test_overlapping_gold_of_another_type(self):
        text = "Dopis od Nadace Karla Dvořáka v Lipové 12."
        gold = [
            _span(text, "Nadace Karla Dvořáka", ORGANIZATION),
            _span(text, "Karla Dvořáka", PERSON),
            _span(text, "Lipové 12", ADDRESS),
        ]
        person = alarm_categories(text, _span(text, "Nadace Karla"), gold, self.ROLE_WORDS)
        assert "organization" in person
        assert "other_type" not in person  # the person gold is of its own type
        address = alarm_categories(text, _span(text, "Karla", ADDRESS), gold, self.ROLE_WORDS)
        assert {"organization", "other_type"} <= address


TEXT = (
    "Smlouvu podepsal Jan Novák.\n"
    "Kupující Karel Dvořák bydlí v Lipové 12.\n"
    "Svobodovi volala Nadace Petra Malého."
)


def _entity(kind: EntityType, value: str, text: str = TEXT) -> Entity:
    start = text.index(value)
    return Entity(kind, 0, start, start + len(value), value)


def _document() -> GoldDocument:
    gold = [
        _entity(PERSON, "Jan Novák"),
        _entity(PERSON, "Karel Dvořák"),
        _entity(PERSON, "Svobodovi"),
        _entity(PERSON, "Petra Malého"),
        _entity(ADDRESS, "Lipové 12"),
        _entity(ORGANIZATION, "Nadace Petra Malého"),
    ]
    document = Document(pages=[make_page(0, TEXT)], language="cs")
    return GoldDocument(name="hand/0", document=document, gold=gold)


def _tally() -> dict[str, Any]:
    gold = _document()
    found = [
        _entity(PERSON, "Jan Novák"),  # found whole
        _entity(PERSON, "Karel"),  # Karel Dvořák found in part
        _entity(PERSON, "Kupující"),  # a false alarm
        _entity(ADDRESS, "Lipové 12"),  # found whole
        _entity(ADDRESS, "Petra Malého"),  # a person tagged as an address
        _entity(PERSON, "Jan Novák"),  # the same span twice counts once
    ]
    tally = ErrorTally([PERSON, ADDRESS], role_words_for("cs"))
    tally.add(found, gold, gold_spans(gold, [PERSON, ADDRESS]))
    return tally.results(Resampler(1, resamples(1, 10, seed=1)))


class TestTally:
    def test_misses_by_outcome_and_category(self):
        person = _tally()["misses"]["person"]
        assert person[ALL]["counts"] == MissCounts(4, 2, 1, 1).to_dict()
        assert person["words=1"]["counts"] == MissCounts(1, 1, 0, 0).to_dict()
        assert person["words=2"]["counts"] == MissCounts(3, 1, 1, 1).to_dict()
        assert person["sentence_start"]["counts"] == MissCounts(1, 1, 0, 0).to_dict()
        assert person["diacritics"]["counts"]["gold"] == 3
        assert person["title"]["counts"]["gold"] == 0
        assert person[ALL]["not_found_rate"]["value"] == 0.5
        assert person[ALL]["partly_rate"]["value"] == 0.25
        assert person["words=1"]["share_not_found"] == 0.5
        assert person["words=2"]["share_partly"] == 1.0
        assert person["title"]["not_found_rate"]["value"] is None
        assert set(person) == set(MISS_CATEGORIES)

    def test_addresses_found_whole(self):
        address = _tally()["misses"]["address"]
        assert address[ALL]["counts"] == MissCounts(1, 0, 0, 0).to_dict()
        assert address[ALL]["share_not_found"] is None

    def test_false_alarms_by_category(self):
        alarms = _tally()["false_alarms"]
        person = alarms["person"]
        assert person[ALL]["counts"] == AlarmCounts(3, 1).to_dict()
        assert person["role_noun"]["counts"] == AlarmCounts(1, 1).to_dict()
        assert person["capitalised_word"]["counts"] == AlarmCounts(2, 1).to_dict()
        assert person["capitalised_word"]["alarm_rate"]["value"] == 0.5
        assert person["role_noun"]["share"] == 1.0
        address = alarms["address"]
        assert address[ALL]["counts"] == AlarmCounts(2, 1).to_dict()
        assert address["organization"]["counts"] == AlarmCounts(1, 1).to_dict()
        assert address["other_type"]["counts"] == AlarmCounts(1, 1).to_dict()
        assert set(person) == set(ALARM_CATEGORIES)

    def test_examples_only_when_asked(self):
        gold = _document()
        examples: dict[str, Any] = {}
        tally = ErrorTally([PERSON], role_words_for("cs"), examples)
        tally.add([_entity(PERSON, "Kupující")], gold, gold_spans(gold, [PERSON]))
        assert examples["misses"]["person"]["sentence_start"] == [
            {
                "text": "Svobodovi",
                "context": TEXT[TEXT.index("Svobodovi") - 40 : TEXT.index("Svobodovi") + 49],
                "outcome": "not_found",
            }
        ]
        assert examples["false_alarms"]["person"]["role_noun"][0]["text"] == "Kupující"


# --- Whole runs on the synthetic corpora --------------------------------------------

NAMES = ("Novák", "Svobodovi", "Dvořák", "Kováč", "Máriu", "Bratislavy", "Kounicova", "Tatra")


def _analyse(resource_root: Path, tmp_path: Path, **options: Any) -> tuple[dict, dict]:
    return analyse(
        parse_config(CONFIG),
        resource_root=resource_root,
        cache_dir=tmp_path / "cache",
        load_model=lambda _: ScoredStandIn(FOUND),
        **options,
    )


def test_totals_agree_with_the_run(resource_root: Path, tmp_path: Path):
    scores = run(
        parse_config(CONFIG),
        resource_root=resource_root,
        cache_dir=tmp_path / "cache",
        load_model=lambda _: ScoredStandIn(FOUND),
    )
    loads: list[str] = []

    def load(model_id: str) -> ScoredStandIn:
        loads.append(model_id)
        return ScoredStandIn({})

    errors, examples = analyse(
        parse_config(CONFIG),
        resource_root=resource_root,
        cache_dir=tmp_path / "cache",
        load_model=load,
    )
    assert examples == {}
    assert not loads  # every window is answered from the cache `run` filled
    for key, corpus in errors["corpora"].items():
        assert corpus["analysed_types"], key
        for name, system in corpus["systems"].items():
            if "cache" in system:
                assert system["cache"]["misses"] == 0
            partial = scores["corpora"][key]["systems"][name]["scores"]["partial"]
            for kind in corpus["analysed_types"]:
                counts = partial[kind]["counts"]
                missed = system["misses"][kind][ALL]["counts"]
                assert missed["gold"] == counts["gold"]
                assert missed["not_found"] == counts["gold"] - counts["gold_matched"]
                alarms = system["false_alarms"][kind][ALL]["counts"]
                assert alarms["predicted"] == counts["predicted"]
                assert alarms["alarms"] == counts["predicted"] - counts["predicted_matched"]
    cnec = errors["corpora"]["cnec-2.0/dtest"]
    # Karla Dvořáka is missed; Jan Novák and Svobodovi are found.
    assert cnec["systems"]["rules+gliner"]["misses"]["person"][ALL]["counts"]["not_found"] == 1
    assert cnec["gold"]["person"][ALL] == 3
    uner = errors["corpora"]["uner-sk-snk/dev+tokens"]["systems"]["rules+gliner"]
    assert uner["false_alarms"]["person"][ALL]["counts"]["alarms"] == 1  # Bratislavy


def test_no_corpus_text_in_the_results(resource_root: Path, tmp_path: Path):
    errors, examples = _analyse(resource_root, tmp_path, keep_examples=True)
    written = json.dumps(errors, ensure_ascii=False) + markdown(errors)
    assert not [name for name in NAMES if name in written]
    # Examples are kept apart, and only for the corpora naming no real person.
    assert set(examples) == {"redact/sample", "openpii-1m-cs/dev"}
    assert "Novák" in json.dumps(examples, ensure_ascii=False)


def test_synthetic_corpora():
    assert is_synthetic("redact")
    assert is_synthetic("openpii-1m-sk")
    assert is_synthetic("name-forms-cs")
    assert not is_synthetic("cnec-2.0")
    assert not is_synthetic("uner-sk-snk")


def test_tables(resource_root: Path, tmp_path: Path):
    errors, _ = _analyse(resource_root, tmp_path)
    text = markdown(errors)
    assert errors["name"] == "synthetic-errors"
    assert "## cnec-2.0/dtest · cs · dev" in text
    assert "### person · not found" in text
    assert "### person · found only in part" in text
    assert "### address · false alarms" in text
    assert "| category | gold | rules | rules+gliner |" in text
    assert "| all | 3 | 3 · 100 % · 1.000 [1.00, 1.00] | 1 · 100 % · 0.333 [" in text


def test_the_command_line(resource_root: Path, tmp_path: Path):
    config = tmp_path / "rules.toml"
    config.write_text(
        'name = "rules-only"\nseed = 3\nresamples = 20\n'
        '[[datasets]]\nid = "redact"\nsplit = "sample"\n[systems.rules]\n',
        encoding="utf-8",
    )
    out = tmp_path / "results"
    root = ["--resource-root", str(resource_root)]
    examples = tmp_path / "examples"
    arguments = ["errors", "--config", str(config), "--out", str(out), *root]
    assert main([*arguments, "--examples", str(out / "examples")]) == 2
    assert not out.exists()
    assert main([*arguments, "--examples", str(examples)]) == 0
    stored = json.loads((out / "rules-only-errors.json").read_text(encoding="utf-8"))
    assert stored["corpora"]["redact/sample"]["analysed_types"] == ["person", "address"]
    assert "### person · not found" in (out / "rules-only-errors.md").read_text(encoding="utf-8")
    kept = json.loads((examples / "rules-only-errors-examples.json").read_text(encoding="utf-8"))
    assert set(kept) == {"redact/sample"}


class TestExamplesFolder:
    def test_never_in_the_results(self, tmp_path: Path):
        with pytest.raises(ValueError, match="results directory"):
            check_examples_folder(tmp_path / "results" / "examples", tmp_path / "results")

    def test_only_where_git_ignores_it(self, tmp_path: Path):
        subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
        (tmp_path / ".gitignore").write_text("outputs/\n", encoding="utf-8")
        with pytest.raises(ValueError, match="ignored by git"):
            check_examples_folder(tmp_path / "examples", tmp_path / "results")
        check_examples_folder(tmp_path / "outputs" / "examples", tmp_path / "results")
