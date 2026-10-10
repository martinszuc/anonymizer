"""The loaders on the downloaded corpora: counts only, never text.

Skipped unless the corpora are stored under the repository's `data/`, or
under the storage root named by `ANONYMIZER_RESOURCE_ROOT` (a worktree
points it at the main checkout).
"""

import os
from collections import Counter
from pathlib import Path

import pytest
from anonymizer.core.resources import load_catalog

from experiments.datasets import TextForm, load_corpus
from experiments.funsd import read_forms

REPOSITORY = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ.get("ANONYMIZER_RESOURCE_ROOT", REPOSITORY))


def _load(dataset: str, split: str, form: TextForm = TextForm.WRITTEN):
    try:
        return load_corpus(dataset, split, ROOT, form)
    except FileNotFoundError:
        pytest.skip(f"{dataset} not stored under {ROOT}")


@pytest.mark.dataset
def test_cnec_dev_split():
    corpus = _load("cnec-2.0", "dtest")
    assert corpus.sentences == 900
    # The person spans of the 2026-10-02 measurement: outermost P plus standalone parts.
    assert corpus.gold_counts()["person"] == 524
    assert corpus.skipped == 0


@pytest.mark.dataset
def test_uner_dev_split_both_ways():
    written = _load("uner-sk-snk", "dev")
    tokens = _load("uner-sk-snk", "dev", TextForm.TOKENS)
    assert written.gold_counts() == tokens.gold_counts() == {"person": 276}
    assert written.sentences == tokens.sentences == 1060
    assert len(written.documents) == 36


@pytest.mark.dataset
def test_redact_czech_records():
    corpus = _load("redact", "sample")
    assert len(corpus.documents) == 40
    assert corpus.gold_counts()["person"] > 0
    assert corpus.skipped == 4


@pytest.mark.dataset
def test_every_gold_span_cuts_its_text():
    for dataset, split in (("cnec-2.0", "etest"), ("uner-sk-snk", "test")):
        corpus = _load(dataset, split)
        for gold in corpus.documents:
            for entity in gold.gold:
                page = gold.document.page(entity.page_index or 0)
                assert page.text[entity.start : entity.end] == entity.text


@pytest.mark.dataset
@pytest.mark.parametrize(
    ("language", "dev", "test"),
    [("cs", 4672, 4550), ("sk", 4451, 4552)],
)
def test_openpii_validation_halves(language: str, dev: int, test: int):
    halves = [_load(f"openpii-1m-{language}", split) for split in ("dev", "test")]
    assert [len(corpus.documents) for corpus in halves] == [dev, test]
    assert all(corpus.skipped == 0 for corpus in halves)
    assert all(
        set(corpus.gold_counts()) == {"address", "email", "person", "phone"} for corpus in halves
    )


@pytest.mark.dataset
def test_funsd_test_forms_and_derived_items():
    try:
        forms = read_forms(load_catalog()["funsd"].directory(ROOT), "test")
    except FileNotFoundError:
        pytest.skip(f"funsd not stored under {ROOT}")
    kinds = Counter(str(kind) for form in forms for kind, _ in form.items)
    assert len(forms) == 50
    assert sum(len(form.words) for form in forms) == 8707
    assert kinds == {"person": 103, "phone": 69, "address": 10}
