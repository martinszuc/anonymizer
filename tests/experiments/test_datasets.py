"""Corpus loaders on synthetic text in each corpus's own format."""

from pathlib import Path

import pytest
from anonymizer.core.types import Entity, EntityType

from experiments.datasets import (
    SENTENCES_PER_PAGE,
    Role,
    TextForm,
    load_corpus,
    make_page,
    outermost,
    parse_cnec_line,
    parse_iob2,
    parse_redact,
)
from tests.experiments.conftest import CNEC_LINES, UNER_TEXT, redact_records


def _spans(sentence) -> list[tuple[str, str]]:
    return [(str(span.type), sentence.text[span.start : span.end]) for span in sentence.spans]


class TestCnec:
    def test_a_name_container_is_one_person(self):
        sentence = parse_cnec_line(CNEC_LINES[0])
        assert sentence.text == "Včera přijel Jan Novák do Brna ."
        assert _spans(sentence) == [("person", "Jan Novák")]
        assert sentence.unmapped == ("gu",)

    def test_a_surname_alone_is_a_person_and_a_phone_is_mapped(self):
        sentence = parse_cnec_line(CNEC_LINES[1])
        assert _spans(sentence) == [("person", "Svobodovi"), ("phone", "777 123 456")]

    def test_inhabitants_are_not_persons_but_a_name_inside_an_institution_is(self):
        sentence = parse_cnec_line(CNEC_LINES[2])
        assert ("person", "Karla Dvořáka") in _spans(sentence)
        assert ("address", "Kounicova 12") in _spans(sentence)
        assert "Pražané" not in [text for _, text in _spans(sentence)]
        assert "pc" in sentence.unmapped
        # Name and address parts are covered by their containers, not left out.
        assert not {"pf", "ps", "gs", "ah"} & set(sentence.unmapped)

    def test_entities_are_unescaped(self):
        sentence = parse_cnec_line(CNEC_LINES[3])
        assert sentence.text == "Napište na info@example.cz & přijďte ."
        assert _spans(sentence) == [("email", "info@example.cz")]

    def test_closing_bracket_after_a_space(self):
        sentence = parse_cnec_line("Dne <T<td 12 . > <tm května>> přijel <ps Novák> .")
        assert _spans(sentence) == [("person", "Novák")]

    @pytest.mark.parametrize("line", ["<ps Novák", "Novák>", "a <"])
    def test_unbalanced_markup_is_refused(self, line: str):
        with pytest.raises(ValueError, match=r"unbalanced|unclosed|unreadable"):
            parse_cnec_line(line)


class TestIob2:
    def test_written_text_keeps_the_writers_punctuation(self):
        documents = parse_iob2(UNER_TEXT)
        assert len(documents) == 2
        first = documents[0][0]
        assert first.text == "Ján Kováč prišiel do Bratislavy."
        assert _spans(first) == [("person", "Ján Kováč")]
        assert first.unmapped == ("LOC",)
        assert documents[1][0].unmapped == ("ORG",)

    def test_tokens_form_joins_tokens_and_ignores_documents(self):
        documents = parse_iob2(UNER_TEXT, TextForm.TOKENS)
        assert len(documents) == 1
        assert [sentence.text for sentence in documents[0]] == [
            "Ján Kováč prišiel do Bratislavy .",
            "Pozdravuj Máriu .",
            "Firma Tatra stojí .",
        ]
        assert _spans(documents[0][1]) == [("person", "Máriu")]

    def test_tokens_that_do_not_align_fall_back_to_spaces(self):
        text = "# text = Something else\n1\tJán\tB-PER\t-\t-\n2\tKováč\tI-PER\t-\t-\n"
        sentence = parse_iob2(text)[0][0]
        assert sentence.text == "Ján Kováč"
        assert _spans(sentence) == [("person", "Ján Kováč")]

    def test_an_inside_tag_without_a_beginning_starts_a_span(self):
        text = "1\tVidel\tO\t-\t-\n2\tJána\tI-PER\t-\t-\n3\tB\tB-PER\t-\t-\n"
        assert _spans(parse_iob2(text)[0][0]) == [("person", "Jána"), ("person", "B")]


class TestRedact:
    def test_czech_records_mapped_and_unmappable_types_counted(self):
        documents = parse_redact(redact_records(), "CS")
        assert len(documents) == 1
        record = documents[0][0]
        assert ("person", "Jan Novák") in _spans(record)
        assert ("email", "jan.novak@example.cz") in _spans(record)
        assert "Credit_Card_Numbers" in record.unmapped
        assert record.unmapped.count("(span not in text)") == 1

    def test_offsets_follow_nfc_normalisation(self):
        decomposed = "Pan Novák a Jan"
        records = [
            {
                "axes": {"language": "CS"},
                "text": decomposed,
                "entities": [
                    {
                        "entity_type": "First_Given_Name",
                        "entity_string": "Jan",
                        "start": decomposed.index("Jan"),
                        "end": len(decomposed),
                    }
                ],
            }
        ]
        record = parse_redact(records, "CS")[0][0]
        assert record.text == "Pan Novák a Jan"
        assert _spans(record) == [("person", "Jan")]


class TestLoadCorpus:
    def test_cnec_split_with_gold_and_roles(self, resource_root: Path):
        corpus = load_corpus("cnec-2.0", "dtest", resource_root)
        assert corpus.role is Role.DEV
        assert corpus.language == "cs"
        assert corpus.sentences == len(CNEC_LINES)
        assert corpus.gold_counts() == {"address": 1, "email": 1, "person": 3, "phone": 1}
        for gold in corpus.documents:
            for entity in gold.gold:
                page = gold.document.page(entity.page_index or 0)
                assert page.text[entity.start : entity.end] == entity.text

    def test_redact_keeps_the_outermost_name_only(self, resource_root: Path):
        corpus = load_corpus("redact", "sample", resource_root)
        persons = [e.text for d in corpus.documents for e in d.gold if e.type is EntityType.PERSON]
        assert persons == ["Jan Novák"]
        assert corpus.skipped == 1
        assert corpus.unmapped["Credit_Card_Numbers"] == 1

    def test_uner_documents_and_key(self, resource_root: Path):
        written = load_corpus("uner-sk-snk", "dev", resource_root)
        assert len(written.documents) == 2
        assert written.key == "uner-sk-snk/dev"
        tokens = load_corpus("uner-sk-snk", "dev", resource_root, TextForm.TOKENS)
        assert len(tokens.documents) == 1
        assert tokens.key == "uner-sk-snk/dev+tokens"

    def test_unknown_dataset_and_split(self, resource_root: Path):
        with pytest.raises(ValueError, match="unknown dataset"):
            load_corpus("conll", "dev", resource_root)
        with pytest.raises(ValueError, match="no split"):
            load_corpus("cnec-2.0", "dev", resource_root)

    def test_missing_files(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_corpus("cnec-2.0", "dtest", tmp_path)


def test_long_documents_get_several_pages(resource_root: Path):
    sentence = "# text = Ján spí.\n1\tJán\tB-PER\t-\t-\n2\tspí\tO\t-\t-\n3\t.\tO\t-\t-\n\n"
    folder = resource_root / "data/uner-sk-snk"
    (folder / "sk_snk-ud-dev.iob2").write_text(
        sentence * (SENTENCES_PER_PAGE + 1), encoding="utf-8"
    )
    corpus = load_corpus("uner-sk-snk", "dev", resource_root)
    document = corpus.documents[0]
    assert len(document.document.pages) == 2
    assert [entity.page_index for entity in document.gold][-1] == 1
    assert all(
        document.document.page(e.page_index or 0).text[e.start : e.end] == "Ján"
        for e in document.gold
    )


def test_page_words_follow_the_text():
    page = make_page(0, "Jan  Novák\nBrno")
    assert [(word.text, page.text[word.start : word.end]) for word in page.words] == [
        ("Jan", "Jan"),
        ("Novák", "Novák"),
        ("Brno", "Brno"),
    ]
    assert page.words[2].bbox.y0 > page.words[0].bbox.y0


def test_outermost_keeps_one_of_each_nesting():
    whole = Entity(EntityType.PERSON, 0, 0, 9, "Jan Novák")
    part = Entity(EntityType.PERSON, 0, 0, 3, "Jan")
    duplicate = Entity(EntityType.PERSON, 0, 0, 9, "Jan Novák")
    other_type = Entity(EntityType.ADDRESS, 0, 4, 9, "Novák")
    kept = outermost([part, whole, duplicate, other_type])
    assert [(e.type, e.text) for e in kept] == [
        (EntityType.PERSON, "Jan Novák"),
        (EntityType.ADDRESS, "Novák"),
    ]
