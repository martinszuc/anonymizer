"""Corpus loaders on synthetic text in each corpus's own format."""

import json
from pathlib import Path

import pytest
from anonymizer.core.types import Entity, EntityType

from experiments.datasets import (
    DATASETS,
    OPENPII_LANGUAGES,
    REDACT_FILES,
    SENTENCES_PER_PAGE,
    WIKIGOLDSK_FILES,
    Role,
    TextForm,
    load_corpus,
    make_page,
    openpii_half,
    outermost,
    parse_cnec_line,
    parse_conll,
    parse_iob2,
    parse_openpii,
    parse_redact,
    parse_slavicner,
    read_redact,
)
from tests.experiments.conftest import (
    CNEC_LINES,
    OPENPII_FORM,
    OPENPII_FORM_LABELS,
    SLAVICNER_MENTIONS,
    SLAVICNER_TEXT,
    UNER_TEXT,
    WIKIGOLDSK_TEXT,
    openpii_record,
    redact_records,
    slavicner_annotations,
    store_slavicner,
)


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
        assert ("organization", "Nadace Karla Dvořáka") in _spans(sentence)
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
        assert _spans(documents[1][0]) == [("organization", "Tatra")]
        assert documents[1][0].unmapped == ()

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


class TestWikiGoldSk:
    def test_two_columns_with_persons_organisations_and_a_hash_token(self):
        first, second = parse_conll(WIKIGOLDSK_TEXT)
        assert first.text == "Peter Horák pracoval v Slovnafte ."
        assert _spans(first) == [("person", "Peter Horák"), ("organization", "Slovnafte")]
        assert first.unmapped == ()
        # `#` is a token, not a comment; an inside tag after `O` starts a person.
        assert second.text == "# Košice oslavujú Deň mesta s Evou ."
        assert _spans(second) == [("person", "Evou")]
        assert second.unmapped == ("LOC", "MISC")

    def test_tabs_and_a_missing_final_blank_line_are_read(self):
        (sentence,) = parse_conll("Ján\tB-PER\nspí\tO")
        assert _spans(sentence) == [("person", "Ján")]

    def test_a_line_without_a_tag_is_refused(self):
        with pytest.raises(ValueError, match="line 2 holds no tag"):
            parse_conll("Ján B-PER\nspí\n")

    def test_splits_and_roles(self, tmp_path: Path):
        folder = tmp_path / "data/wikigoldsk"
        folder.mkdir(parents=True)
        for name in WIKIGOLDSK_FILES.values():
            (folder / name).write_text((WIKIGOLDSK_TEXT + "\n") * 7, encoding="utf-8")
        train = load_corpus("wikigoldsk", "train", tmp_path)
        assert (train.role, train.language, train.sentences) == (Role.TRAIN, "sk", 14)
        # No article boundaries: page-like chunks, each a document of its own.
        assert len(train.documents) == 2
        assert train.gold_counts() == {"organization": 7, "person": 14}
        assert train.types == {EntityType.PERSON}
        assert load_corpus("wikigoldsk", "dev", tmp_path).role is Role.DEV
        assert load_corpus("wikigoldsk", "test", tmp_path).role is Role.TEST


class TestSlavicNer:
    def test_each_line_is_a_sentence_with_its_mentions(self):
        annotations = slavicner_annotations(SLAVICNER_TEXT, SLAVICNER_MENTIONS)
        sentences = parse_slavicner(SLAVICNER_TEXT, annotations)
        assert [_spans(sentence) for sentence in sentences] == [
            [("person", "Janu Novákovi")],
            [("person", "Jan Novák"), ("organization", "Alfa Group")],
            [("organization", "Komise")],
        ]
        assert sum((sentence.unmapped for sentence in sentences), ()) == ("LOC", "LOC")

    def test_offsets_follow_nfc_normalisation(self):
        text = "Pane Nováku, Petr Novák volal."
        annotations = slavicner_annotations(text, [("Nováku", "PER"), ("Petr Novák", "PER")])
        (sentence,) = parse_slavicner(text, annotations)
        assert sentence.text == "Pane Nováku, Petr Novák volal."
        assert _spans(sentence) == [("person", "Nováku"), ("person", "Petr Novák")]

    def test_mentions_off_their_text_are_skipped(self):
        text = "Jan\nNovák a Eva Malá."
        rows = "0\t3\tJan\tx\tPER\tp-1\n12\t16\tEva Malá\tx\tPER\tp-2\n0\t0\t\tx\tPER\tp-3\n"
        sentences = parse_slavicner(text, rows)
        assert [_spans(sentence) for sentence in sentences] == [[("person", "Jan")], []]
        assert sentences[0].unmapped == ("(span not in text)", "(span not in text)")

    def test_an_annotation_line_needs_six_columns(self):
        with pytest.raises(ValueError, match="holds 3 columns"):
            parse_slavicner("Jan Novák", "0\t3\tJan\n")

    def test_the_cross_topic_split_of_one_language(self, tmp_path: Path):
        annotations = slavicner_annotations(SLAVICNER_TEXT, SLAVICNER_MENTIONS)
        documents = {
            "raw/brexit/cs/brexit_cs.txt_file_1.txt": (SLAVICNER_TEXT, annotations),
            "raw/brexit/cs/brexit_cs.txt_file_2.txt": (
                "Eva Malá mlčela.",
                "0\t8\tEva Malá\tx\tPER\tp\n",
            ),
            "raw/brexit/pl/brexit_pl.txt_file_1.txt": (
                "Jan Kowalski.",
                "0\t12\tJan Kowalski\tx\tPER\tp\n",
            ),
        }
        store_slavicner(
            tmp_path,
            documents,
            {
                "train": ["raw/brexit/pl/brexit_pl.txt_file_1.txt", *list(documents)[:1]],
                "test": [list(documents)[1]],
            },
        )
        train = load_corpus("slavicner-cs", "train", tmp_path)
        assert (train.role, train.language, len(train.documents), train.sentences) == (
            Role.TRAIN,
            "cs",
            1,
            3,
        )
        assert train.gold_counts() == {"organization": 2, "person": 2}
        assert train.unmapped == {"LOC": 2}
        # The source's test part is the tuning part: development data.
        dev = load_corpus("slavicner-cs", "dev", tmp_path)
        assert (dev.role, dev.gold_counts()) == (Role.DEV, {"person": 1})
        assert set(DATASETS["slavicner-cs"].splits) == {"train", "dev"}

    def test_a_split_listing_another_kind_of_path_is_refused(self, tmp_path: Path):
        store_slavicner(tmp_path, {}, {"train": ["ner/brexit/cs/file.tsv"]})
        with pytest.raises(ValueError, match="not of the form"):
            load_corpus("slavicner-cs", "train", tmp_path)


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

    def test_the_test_split_is_the_full_release_without_the_sample(self, tmp_path: Path):
        sample = redact_records()
        held_out = {"axes": {"language": "CS"}, "text": "Paní Eva Malá", "entities": []}
        (tmp_path / REDACT_FILES["sample"]).write_text(json.dumps(sample), encoding="utf-8")
        (tmp_path / REDACT_FILES["test"]).write_text(
            json.dumps([*sample, held_out]), encoding="utf-8"
        )
        texts = {
            split: [document[0].text for document in read_redact(tmp_path, split, TextForm.TOKENS)]
            for split in ("sample", "test")
        }
        assert texts == {"sample": [sample[0]["text"]], "test": ["Paní Eva Malá"]}

    def test_a_sample_record_missing_from_the_full_release_is_refused(self, tmp_path: Path):
        sample = redact_records()
        # The same record with one extra space would stay in the test split unnoticed.
        changed = {**sample[0], "text": sample[0]["text"] + " "}
        (tmp_path / REDACT_FILES["sample"]).write_text(json.dumps(sample), encoding="utf-8")
        (tmp_path / REDACT_FILES["test"]).write_text(json.dumps([changed]), encoding="utf-8")
        with pytest.raises(ValueError, match="1 of 1 Czech sample records"):
            read_redact(tmp_path, "test", TextForm.TOKENS)

    def test_only_czech_sample_records_must_be_in_the_full_release(self, tmp_path: Path):
        sample = redact_records()
        english = {"axes": {"language": "EN"}, "text": "Not in the full file", "entities": []}
        (tmp_path / REDACT_FILES["sample"]).write_text(
            json.dumps([*sample, english]), encoding="utf-8"
        )
        (tmp_path / REDACT_FILES["test"]).write_text(json.dumps(sample), encoding="utf-8")
        assert read_redact(tmp_path, "test", TextForm.TOKENS) == []

    def test_an_unknown_split_is_refused(self, tmp_path: Path):
        with pytest.raises(ValueError, match="'dev'"):
            read_redact(tmp_path, "dev", TextForm.TOKENS)

    def test_its_test_split_is_test_data(self):
        assert DATASETS["redact"].splits == {"sample": Role.DEV, "test": Role.TEST}


def _openpii(text: str, labelled: list[tuple[str, str]]):
    (document,) = parse_openpii([openpii_record(text, labelled, uid=1)], "cs")
    return document[0]


class TestOpenpii:
    def test_a_form_mapped_to_our_types(self):
        record = _openpii(OPENPII_FORM, OPENPII_FORM_LABELS)
        assert _spans(record) == [
            ("person", "Jan Novák"),
            ("address", "Lipová č. 12, 602 00 Brno"),
            ("email", "jan.novak@example.cz"),
        ]
        # The title, the invented identifier and phone, and a city on its own are not scored.
        assert sorted(record.unmapped) == ["CITY", "SOCIALNUM", "TELEPHONENUM", "TITLE"]

    @pytest.mark.parametrize("gap", [" ", "\u00a0", "\u202f", ""])
    def test_name_parts_join_across_spaces(self, gap: str):
        text = f"Eva{gap}Malá"
        record = _openpii(text, [("GIVENNAME", "Eva"), ("SURNAME", "Malá")])
        assert _spans(record) == [("person", text)]

    @pytest.mark.parametrize("gap", [" a ", "\n", ", "])
    def test_names_stay_apart_across_words_lines_and_commas(self, gap: str):
        record = _openpii(f"Petr{gap}Svoboda", [("GIVENNAME", "Petr"), ("SURNAME", "Svoboda")])
        assert _spans(record) == [("person", "Petr"), ("person", "Svoboda")]

    def test_address_parts_apart_by_a_long_gap_or_a_line_are_two_addresses(self):
        text = "Lipová 12 a o kus dál 602 00\nBrno"
        record = _openpii(
            text,
            [("STREET", "Lipová"), ("BUILDINGNUM", "12"), ("ZIPCODE", "602 00"), ("CITY", "Brno")],
        )
        assert _spans(record) == [("address", "Lipová 12"), ("address", "602 00")]
        assert record.unmapped == ("CITY",)

    def test_a_name_next_to_an_address_stays_a_name(self):
        record = _openpii("Jan Novák Lipová 3", [("SURNAME", "Novák"), ("STREET", "Lipová")])
        assert _spans(record) == [("person", "Novák"), ("address", "Lipová")]

    def test_spans_that_miss_their_value_are_skipped(self):
        record = openpii_record("Jan Novák", [("GIVENNAME", "Jan")], uid=1)
        record["privacy_mask"].append({"label": "SURNAME", "start": 4, "end": 9, "value": "Malý"})
        record["privacy_mask"].append({"label": "SURNAME", "start": None, "end": 9, "value": "x"})
        (document,) = parse_openpii([record], "cs")
        assert _spans(document[0]) == [("person", "Jan")]
        assert document[0].unmapped.count("(span not in text)") == 2

    def test_offsets_follow_nfc_normalisation(self):
        decomposed = "Pan Nova\u0301k a Jan"
        record = _openpii(decomposed, [("SURNAME", "Nova\u0301k"), ("GIVENNAME", "Jan")])
        assert record.text == "Pan Novák a Jan"
        assert _spans(record) == [("person", "Novák"), ("person", "Jan")]

    def test_other_languages_are_left_out(self):
        records = [openpii_record("Ján Kováč", [("GIVENNAME", "Ján")], uid=1, language="sk")]
        assert parse_openpii(records, "cs") == []

    def test_halves_are_stable_and_both_used(self):
        halves = [openpii_half(uid) for uid in range(200)]
        assert halves == [openpii_half(uid) for uid in range(200)]
        assert 60 < halves.count("dev") < 140
        assert set(halves) == {"dev", "test"}

    def test_every_language_is_a_dataset_of_the_one_catalog_entry(self):
        for language in OPENPII_LANGUAGES:
            spec = DATASETS[f"openpii-1m-{language}"]
            assert spec.catalog_id == "openpii-1m"
            assert spec.language == language


class TestLoadCorpus:
    def test_cnec_split_with_gold_and_roles(self, resource_root: Path):
        corpus = load_corpus("cnec-2.0", "dtest", resource_root)
        assert corpus.role is Role.DEV
        assert corpus.language == "cs"
        assert corpus.sentences == len(CNEC_LINES)
        assert corpus.gold_counts() == {
            "address": 1,
            "email": 1,
            "organization": 1,
            "person": 3,
            "phone": 1,
        }
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

    def test_openpii_dev_and_test_split_the_validation_records(self, resource_root: Path):
        dev = load_corpus("openpii-1m-cs", "dev", resource_root)
        test = load_corpus("openpii-1m-cs", "test", resource_root)
        assert (dev.role, test.role) == (Role.DEV, Role.TEST)
        assert len(dev.documents) + len(test.documents) == 6
        assert dev.key == "openpii-1m-cs/dev"
        assert dev.version == test.version != ""
        train = load_corpus("openpii-1m-cs", "train", resource_root)
        assert train.role is Role.TRAIN
        assert len(train.documents) == 6
        assert train.gold_counts() == {"address": 6, "email": 6, "person": 6}
        slovak = load_corpus("openpii-1m-sk", "train", resource_root)
        assert (slovak.language, slovak.gold_counts()) == ("sk", {"person": 1})

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


def test_a_limit_keeps_the_first_documents_and_counts_only_those(resource_root: Path):
    whole = load_corpus("openpii-1m-cs", "dev", resource_root)
    first = load_corpus("openpii-1m-cs", "dev", resource_root, limit=2)
    assert [doc.name for doc in first.documents] == [doc.name for doc in whole.documents[:2]]
    assert first.sentences == 2
    assert sum(first.gold_counts().values()) < sum(whole.gold_counts().values())
