"""The token classifier: windows, BIO decoding, offsets, loading, with stand-ins.

The tests at the end build a tiny random XLM-RoBERTa model offline and run
the `transformers` path; they are skipped without PyTorch. Every name is
invented.
"""

import itertools
import os
import random
import re
import unicodedata
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.detect import GlinerDetector, load_name_model, name_model_threshold
from anonymizer.core.detect import token_classifier as token_module
from anonymizer.core.detect.gliner import gliner_tokens
from anonymizer.core.detect.token_classifier import (
    DEFAULT_THRESHOLD,
    TOKEN_CLASSIFIER_ENGINE,
    TokenClassifier,
    bio_labels,
    decode,
    load_token_classifier,
    word_subwords,
    word_windows,
)
from anonymizer.core.resources import Catalog, load_catalog
from anonymizer.core.types import BBox, EntityType, Page, Word

from tests.resources.test_catalog import store_trained, trained_entry
from tests.token_classifier_builders import (
    LABELS,
    TYPES,
    StandInNetwork,
    StandInTokenizer,
    tiny_token_classifier,
)

ASKED = ["person", "street address", "organization"]
TAGS = {
    "Jan": "B-person",
    "Nová": "I-person",
    "Lipo": "B-street address",
    "12": "I-street address",
}


def _classifier(
    tags: dict[str, str], *, max_length: int = 512, confidence: float = 0.9
) -> tuple[TokenClassifier, StandInNetwork]:
    tokenizer = StandInTokenizer(max_length)
    network = StandInNetwork(tokenizer, tags, confidence)
    return TokenClassifier(tokenizer, network, LABELS, max_length), network


def _found(text: str, answer: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [(span["label"], text[span["start"] : span["end"]]) for span in answer]


def _page(text: str) -> Page:
    words = [
        Word(match.group(), BBox(10.0 * i, 0.0, 10.0 * i + 8, 10.0), match.start(), match.end())
        for i, match in enumerate(re.finditer(r"\S+", text))
    ]
    return Page(index=0, width=595, height=842, text=text, words=words)


def _distribution(label: str, probability: float) -> list[float]:
    rest = (1 - probability) / (len(LABELS) - 1)
    return [probability if name == label else rest for name in LABELS]


class TestLabels:
    def test_outside_first_then_begin_and_inside_per_type(self):
        assert bio_labels(TYPES) == [
            "O",
            "B-person",
            "I-person",
            "B-street address",
            "I-street address",
            "B-organization",
            "I-organization",
        ]

    @pytest.mark.parametrize("labels", [["B-person", "I-person"], ["O", "PER"], ["O", "X-person"]])
    def test_labels_that_are_not_bio_are_refused(self, labels: list[str]):
        with pytest.raises(ValueError, match="B-/I- types"):
            TokenClassifier(StandInTokenizer(), StandInNetwork(StandInTokenizer(), {}), labels, 8)

    def test_an_input_too_short_for_a_word_is_refused(self):
        with pytest.raises(ValueError, match="holds no word"):
            TokenClassifier(StandInTokenizer(), StandInNetwork(StandInTokenizer(), {}), LABELS, 2)

    def test_the_types_in_label_order(self):
        classifier, _ = _classifier({})
        assert classifier.types == list(TYPES)


class TestDecode:
    def test_begin_and_inside_make_one_span_scored_by_its_type(self):
        words = [
            _distribution("O", 0.9),
            _distribution("B-person", 0.6),
            _distribution("I-person", 0.8),
            _distribution("O", 0.9),
        ]
        # A word's type probability is B- plus I-: 0.6 + rest, 0.8 + rest.
        rest_06, rest_08 = 0.4 / 6, 0.2 / 6
        ((first, last, kind, score),) = decode(words, LABELS)
        assert (first, last, kind) == (1, 2, "person")
        assert score == pytest.approx(((0.6 + rest_06) + (0.8 + rest_08)) / 2)

    def test_inside_after_outside_starts_a_span(self):
        words = [_distribution("O", 0.9), _distribution("I-person", 0.9)]
        assert [span[:3] for span in decode(words, LABELS)] == [(1, 1, "person")]

    def test_a_change_of_type_or_a_new_begin_ends_the_span(self):
        words = [
            _distribution("B-person", 0.9),
            _distribution("I-street address", 0.9),
            _distribution("B-street address", 0.9),
            _distribution("I-street address", 0.9),
        ]
        assert [span[:3] for span in decode(words, LABELS)] == [
            (0, 0, "person"),
            (1, 1, "street address"),
            (2, 3, "street address"),
        ]

    def test_a_span_reaching_the_last_word_is_kept(self):
        words = [_distribution("B-organization", 0.9), _distribution("I-organization", 0.9)]
        assert [span[:3] for span in decode(words, LABELS)] == [(0, 1, "organization")]

    def test_nothing_from_outside_only_or_no_words(self):
        assert decode([_distribution("O", 0.9)] * 3, LABELS) == []
        assert decode([], LABELS) == []


class TestInference:
    TEXT = "Smlouvu podepsal Jan Novák, bytem Lipová 12, Brno."

    def test_whole_spans_in_running_text_without_their_punctuation(self):
        classifier, _ = _classifier(TAGS)
        (answer,) = classifier.inference([self.TEXT], ASKED, threshold=0.5, flat_ner=True)
        assert _found(self.TEXT, answer) == [
            ("person", "Jan Novák"),
            ("street address", "Lipová 12"),
        ]
        assert all(span["score"] == pytest.approx(0.9 + 0.1 / 6) for span in answer)

    def test_only_the_types_asked_for_are_returned(self):
        classifier, _ = _classifier(TAGS)
        (answer,) = classifier.inference([self.TEXT], ["Person"], threshold=0.5, flat_ner=True)
        assert _found(self.TEXT, answer) == [("person", "Jan Novák")]

    def test_spans_scoring_at_most_the_threshold_are_dropped(self):
        classifier, _ = _classifier(TAGS, confidence=0.5)
        score = 0.5 + 0.5 / 6
        assert classifier.inference([self.TEXT], ASKED, threshold=score, flat_ner=True) == [[]]
        (answer,) = classifier.inference([self.TEXT], ASKED, threshold=0.5, flat_ner=True)
        assert len(answer) == 2

    def test_filtering_a_low_threshold_upwards_equals_asking_higher(self):
        classifier, _ = _classifier(TAGS, confidence=0.7)
        low = classifier.inference([self.TEXT], ASKED, threshold=0.1, flat_ner=True)
        for threshold in (0.3, 0.7, 0.75, 0.9):
            high = classifier.inference([self.TEXT], ASKED, threshold=threshold, flat_ner=True)
            assert high == [[span for span in low[0] if span["score"] > threshold]]

    def test_diacritics_and_nfc_offsets(self):
        text = unicodedata.normalize("NFC", "Pozdravuj Jána Kováče z Lipové.")
        classifier, _ = _classifier({"Jána": "B-person", "Ková": "I-person"})
        (answer,) = classifier.inference([text], ASKED, threshold=0.5, flat_ner=True)
        assert _found(text, answer) == [("person", "Jána Kováče")]

    def test_texts_without_words_and_batches_of_many_texts(self):
        classifier, network = _classifier(TAGS)
        texts = ["", "   ", *[f"{'Ano ' * index}Jan Novák" for index in range(20)]]
        answers = classifier.inference(texts, ASKED, threshold=0.5, flat_ner=True)
        assert answers[:2] == [[], []]
        assert all(
            _found(text, answer) == [("person", "Jan Novák")]
            for text, answer in zip(texts[2:], answers[2:], strict=True)
        )
        assert len(network.windows) == 20

    def test_a_text_longer_than_one_input_is_read_in_overlapping_parts(self):
        filler = " ".join(f"slovo{index}" for index in range(60))
        text = f"{filler} Jan Novák podepsal. {filler} Jan Novák znovu."
        classifier, network = _classifier(TAGS, max_length=40)
        (answer,) = classifier.inference([text], ASKED, threshold=0.5, flat_ner=True)
        assert _found(text, answer) == [("person", "Jan Novák")] * 2
        assert len(network.windows) > 2
        assert all(len(window.input_ids) <= 40 for window in network.windows)

    def test_each_word_takes_the_part_where_it_has_most_context(self):
        # The network labels a word only where it lies in the middle of its part.
        words = [f"w{index:02d}" for index in range(30)]
        text = " ".join(words)

        class Central(StandInNetwork):
            def probabilities(self, windows):
                answers = []
                for window in windows:
                    size = len(window.first_subwords)
                    answers.append(
                        [
                            _distribution(
                                "B-person" if size // 4 <= offset < size - size // 4 else "O",
                                0.9,
                            )
                            for offset in range(size)
                        ]
                    )
                return answers

        tokenizer = StandInTokenizer(12)
        classifier = TokenClassifier(tokenizer, Central(tokenizer, {}), LABELS, 12)
        (answer,) = classifier.inference([text], ASKED, threshold=0.5, flat_ner=True)
        found = {text[span["start"] : span["end"]] for span in answer}
        # Every word but the outer edges of the text sits mid-part in some part.
        assert set(words[3:-3]) <= found

    def test_a_word_longer_than_an_input_keeps_its_first_subwords(self):
        text = "Jan " + "x" * 200 + " Novák"
        classifier, network = _classifier(TAGS, max_length=10)
        classifier.inference([text], ASKED, threshold=0.5, flat_ner=True)
        assert all(len(window.input_ids) <= 10 for window in network.windows)
        assert len(network.windows) == 3

    def test_moving_to_a_device_moves_the_network(self):
        classifier, network = _classifier({})
        assert classifier.to("mps") is classifier
        assert network.devices == ["mps"]


class TestWindows:
    def test_ranges_cover_every_word_and_fit(self):
        draw = random.Random("windows")
        for _ in range(500):
            subwords = [[1] * draw.randint(1, 6) for _ in range(draw.randint(1, 80))]
            body = draw.randint(6, 30)
            overlap = draw.randint(0, body)
            ranges = word_windows(subwords, body, overlap)
            assert ranges[0][0] == 0
            assert ranges[-1][1] == len(subwords)
            for (first, end), (following, _) in itertools.pairwise(ranges):
                assert first < following <= end
            for first, end in ranges:
                assert sum(len(word) for word in subwords[first:end]) <= body

    def test_a_word_longer_than_the_body_is_a_range_of_its_own(self):
        assert word_windows([[1], [1] * 9, [1]], 4, 0) == [(0, 1), (1, 2), (2, 3)]

    def test_a_dropped_word_reads_as_unknown(self):
        class Dropping(StandInTokenizer):
            def __call__(self, words, *, add_special_tokens):
                return {"input_ids": [[] if word == "​" else [5] for word in words]}

        assert word_subwords(Dropping(), ["a", "​"]) == [[5], [3]]
        assert word_subwords(Dropping(), []) == []


class TestDetector:
    def test_the_detector_widens_and_types_the_spans(self):
        classifier, _ = _classifier(TAGS)
        page = _page(TestInference.TEXT)
        entities = GlinerDetector(classifier, threshold=DEFAULT_THRESHOLD).detect(page)
        assert [(entity.type, entity.text) for entity in entities] == [
            (EntityType.PERSON, "Jan Novák"),
            (EntityType.ADDRESS, "Lipová 12"),
        ]

    def test_organisations_are_the_distractor(self):
        classifier, _ = _classifier({"Nada": "B-organization", "Karl": "I-organization"})
        page = _page("Dar od Nadace Karla Dvořáka.")
        assert GlinerDetector(classifier).detect(page) == []


def _token_entry(**change: Any) -> dict[str, Any]:
    return trained_entry(
        id="xlmr-cs-tuned",
        engine=TOKEN_CLASSIFIER_ENGINE,
        requires=["xlm-roberta-large-tokenizer"],
        **change,
    )


class TestLoading:
    @pytest.fixture
    def loaded_from(self, monkeypatch: pytest.MonkeyPatch) -> list[tuple[Path, Path]]:
        folders: list[tuple[Path, Path]] = []

        def load(model_dir: Path, tokenizer_dir: Path) -> TokenClassifier:
            folders.append((model_dir, tokenizer_dir))
            return _classifier(TAGS)[0]

        monkeypatch.setattr(token_module, "load_token_classifier", load)
        monkeypatch.setattr(token_module, "require_stored", lambda *_: None)
        return folders

    def test_a_trained_classifier_loads_by_catalog_id_at_its_engines_threshold(
        self, tmp_path: Path, loaded_from: list[tuple[Path, Path]]
    ):
        store_trained(tmp_path, _token_entry())
        detector = load_name_model("xlmr-cs-tuned", tmp_path)
        assert isinstance(detector, GlinerDetector)
        assert detector.name == "xlmr-cs-tuned"
        assert detector.threshold == DEFAULT_THRESHOLD
        assert loaded_from == [
            (tmp_path / "models/xlmr-cs-tuned", tmp_path / "models/xlm-roberta-large-tokenizer")
        ]
        entities = detector.detect(_page(TestInference.TEXT))
        assert [entity.text for entity in entities] == ["Jan Novák", "Lipová 12"]

    def test_the_entrys_threshold_and_the_callers_win(
        self, tmp_path: Path, loaded_from: list[tuple[Path, Path]]
    ):
        store_trained(tmp_path, _token_entry(threshold=0.2))
        catalog = load_catalog(root=tmp_path)
        assert name_model_threshold("xlmr-cs-tuned", catalog) == 0.2
        detector = load_name_model("xlmr-cs-tuned", tmp_path, threshold=0.7)
        assert isinstance(detector, GlinerDetector)
        assert detector.threshold == 0.7

    def test_missing_files_point_to_the_training_record(self, tmp_path: Path):
        store_trained(tmp_path, _token_entry())
        with pytest.raises(FileNotFoundError, match=r"trained on this machine"):
            load_name_model("xlmr-cs-tuned", tmp_path)

    def test_without_transformers_the_ner_group_is_named(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        import sys

        monkeypatch.setitem(sys.modules, "transformers", None)
        with pytest.raises(ImportError, match="optional 'ner' dependencies"):
            load_token_classifier(tmp_path, tmp_path)

    def test_the_shipped_encoder_is_for_training_not_a_name_model(self):
        catalog: Catalog = load_catalog()
        encoder = catalog["xlm-roberta-large"]
        assert encoder.uses == ("training",)
        assert encoder.requires == ("xlm-roberta-large-tokenizer",)
        assert encoder.version == catalog["xlm-roberta-large-tokenizer"].version
        with pytest.raises(ValueError, match="unknown name model"):
            load_name_model("xlm-roberta-large", Path("/models-root"))


class TestTinyModel:
    """The `transformers` path on a tiny random model built offline."""

    @pytest.fixture
    def folders(self, tmp_path: Path) -> tuple[Path, Path]:
        pytest.importorskip("torch")
        pytest.importorskip("transformers")
        return tiny_token_classifier(tmp_path, max_length=24)

    def test_loads_offline_and_answers_well_formed_spans(self, folders: tuple[Path, Path]):
        classifier = load_token_classifier(*folders)
        assert classifier.labels == LABELS
        assert classifier.max_length == 24
        filler = " ".join(["Brno"] * 40)
        text = f"Smlouvu podepsal Jan Novák , bytem Lipová 12 . {filler} Pozdravuj Ján Kováč ."
        (answer,) = classifier.inference([text], ASKED, threshold=0.0, flat_ner=True)
        starts = {start for start, _ in gliner_tokens(text)}
        ends = {end for _, end in gliner_tokens(text)}
        for span in answer:
            assert span["start"] in starts
            assert span["end"] in ends
            assert span["label"] in TYPES
            assert 0.0 < span["score"] <= 1.0

    def test_moves_to_the_cpu(self, folders: tuple[Path, Path]):
        classifier = load_token_classifier(*folders)
        assert classifier.to("cpu") is classifier


ROOT = Path(os.environ.get("ANONYMIZER_RESOURCE_ROOT", Path(__file__).resolve().parents[2]))


@pytest.mark.model
def test_the_real_tokenizer_cuts_words_as_split_words_and_a_window_fits():
    transformers = pytest.importorskip("transformers")
    directory = load_catalog()["xlm-roberta-large-tokenizer"].directory(ROOT)
    if not (directory / "tokenizer.json").exists():
        pytest.skip("XLM-R tokenizer not fetched")
    tokenizer = transformers.AutoTokenizer.from_pretrained(str(directory), local_files_only=True)
    # Synthetic, punctuation-heavy on purpose.
    text = "Smlouvu podepsal Ing. Ján Kováč-Nováková, bytem Lipová 12, 602 00 Brno; tel.: 777/123."
    words = [text[start:end] for start, end in gliner_tokens(text)]
    split = tokenizer(words, is_split_into_words=True, add_special_tokens=False)
    grouped: list[list[int]] = [[] for _ in words]
    for token_id, word in zip(split["input_ids"], split.word_ids(), strict=True):
        grouped[word].append(token_id)
    assert word_subwords(tokenizer, words) == grouped
    # A detector window of 150 such words fits one input of 512 subwords.
    per_word = sum(map(len, grouped)) / len(words)
    assert 150 * per_word + 2 <= tokenizer.model_max_length == 512
