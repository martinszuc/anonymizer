"""Finding training text that dev or test data also holds, on synthetic corpora."""

from pathlib import Path

import pytest

from experiments.datasets import DATASETS, Sentence, TextForm, load_corpus
from experiments.overlap import HeldTexts, OverlapFilter, held_texts, text_key
from tests.experiments.conftest import CNEC_LINES


def test_texts_differing_in_whitespace_or_normal_form_share_a_key():
    written = "Ján Kováč prišiel do Bratislavy."
    assert text_key(written) == text_key("Ján  Kováč prišiel do Bratislavy .")
    assert text_key(written) == text_key("Ján Kováč\nprišiel do\tBratislavy.")
    assert text_key(written) != text_key("Ján Kováč prišiel do Košíc.")
    assert text_key(" \n\t") is None
    assert text_key("") is None


def _read(groups: dict[tuple[str, str], list[list[Sentence]]], read: list[tuple[str, str]]):
    def reader(dataset: str, split: str, root: Path, form: TextForm) -> list[list[Sentence]]:
        assert form is TextForm.WRITTEN
        read.append((dataset, split))
        return groups[dataset, split]

    return reader


def test_every_dev_and_test_split_is_read_and_no_train_split():
    shared, other = Sentence("Eva Malá spí."), Sentence("Petr bdí.")
    groups = {
        ("cnec-2.0", "dtest"): [[shared], [other]],
        ("cnec-2.0", "etest"): [[Sentence("Eva  Malá spí .")]],
        ("uner-sk-snk", "dev"): [[Sentence(" ")]],
        ("uner-sk-snk", "test"): [],
    }
    read: list[tuple[str, str]] = []
    datasets = {key: DATASETS[key] for key in ("cnec-2.0", "uner-sk-snk")}
    held = held_texts(Path("unused"), datasets, _read(groups, read))
    assert sorted(read) == sorted(groups)
    assert held.sentences == {
        "cnec-2.0/dtest": 2,
        "cnec-2.0/etest": 1,
        "uner-sk-snk/dev": 1,
        "uner-sk-snk/test": 0,
    }
    assert held.splits_of("Eva Malá spí.") == ("cnec-2.0/dtest", "cnec-2.0/etest")
    assert held.splits_of("Petr bdí.") == ("cnec-2.0/dtest",)
    assert held.splits_of("Jan spí.") == ()
    assert held.splits_of(" ") == ()


def test_a_dataset_not_stored_fails_the_check_instead_of_passing_it(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        held_texts(tmp_path, {"cnec-2.0": DATASETS["cnec-2.0"]})


def test_held_out_sentences_are_left_out_of_a_split_and_counted(resource_root: Path):
    plain = resource_root / "data/cnec-2.0/Czech_Named_Entity_Corpus_2.0/cnec2.0/data/plain"
    (plain / "named_ent_train.txt").write_text("\n".join(CNEC_LINES) + "\n", encoding="utf-8")
    held = held_texts(resource_root, {"cnec-2.0": DATASETS["cnec-2.0"]})
    # etest holds the first CNEC line only; dev and test text of the same corpus is found too.
    etest_only = HeldTexts(
        {key: splits for key, splits in held.sources.items() if len(splits) == 2}
    )
    matches = OverlapFilter(etest_only)
    corpus = load_corpus("cnec-2.0", "train", resource_root, exclude=matches)
    assert (corpus.excluded, corpus.sentences) == (1, len(CNEC_LINES) - 1)
    assert matches.sources == {"cnec-2.0/dtest": 1, "cnec-2.0/etest": 1}
    assert all(
        "Jan Novák" not in page.text for doc in corpus.documents for page in doc.document.pages
    )

    # A document left with no sentence is left out.
    everything = load_corpus("cnec-2.0", "train", resource_root, exclude=OverlapFilter(held))
    assert (everything.excluded, everything.sentences, everything.documents) == (4, 0, [])
    assert load_corpus("cnec-2.0", "train", resource_root).excluded == 0


def test_the_command_counts_per_train_split_without_text(
    training_root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    import experiments.__main__ as command

    monkeypatch.setattr(
        command, "held_texts", lambda root: held_texts(root, {"cnec-2.0": DATASETS["cnec-2.0"]})
    )
    assert command.main(["overlap", "cnec-2.0", "--resource-root", str(training_root)]) == 0
    printed = capsys.readouterr().out
    assert "held out cnec-2.0/etest: 1 sentences or records" in printed
    assert (
        "cnec-2.0/train: 4 of 4 sentences or records repeat dev or test text "
        "(cnec-2.0/dtest 4, cnec-2.0/etest 1)"
    ) in printed
    assert "uner-sk-snk/train" not in printed
    assert "Novák" not in printed
    assert command.main(["overlap", "conll", "--resource-root", str(training_root)]) == 2
