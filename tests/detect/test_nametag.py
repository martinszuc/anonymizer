"""Tests for the NameTag 3 detector and its model code, with stand-ins.

The real models run only in the `model`-marked tests at the end, skipped
unless the models are stored (under `ANONYMIZER_RESOURCE_ROOT` or the
repository) and the `ner` dependencies are installed. The network code needs
PyTorch and is tested on a tiny random encoder when PyTorch is present.
`experiments/nametag_reference.py` compares the whole tagger with upstream
NameTag 3.
"""

import os
import pickle
import re
import sys
import types
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.detect import load_name_model
from anonymizer.core.detect.nametag import (
    Label,
    NametagDetector,
    TaggedEntity,
    Token,
    address_runs,
    load_nametag_detector,
    model_directory,
    tagged_entities,
)
from anonymizer.core.detect.nametag_model import (
    BATCH_SIZE,
    LabelIds,
    Nametag3Tagger,
    Window,
    max_length,
    read_mappings,
    tagset_mask,
)
from anonymizer.core.resources import load_catalog
from anonymizer.core.types import BBox, DetectionSource, EntityType, Page, Word


def _page(text: str) -> Page:
    words = [
        Word(match.group(), BBox(10.0 * i, 0.0, 10.0 * i + 8, 10.0), match.start(), match.end())
        for i, match in enumerate(re.finditer(r"\S+", text))
    ]
    return Page(index=0, width=595, height=842, text=text, words=words)


def _labels(*tokens: str, probability: float = 0.9) -> list[list[Label]]:
    """`"B-P B-pf"` per token → its labels; `""` for outside."""
    return [[(label, probability) for label in token.split()] for token in tokens]


class StandInSplitter:
    """One sentence per line; words and punctuation apart, like UDPipe."""

    def sentences(self, text: str) -> list[list[Token]]:
        sentences: list[list[Token]] = []
        position = 0
        for line in text.split("\n"):
            tokens = [
                Token(match.group(), position + match.start(), position + match.end())
                for match in re.finditer(r"\w+|[^\w\s]", line)
            ]
            if tokens:
                sentences.append(tokens)
            position += len(line) + 1
        return sentences


class StandInTagger:
    """Labels fixed token sequences: `{("Jan", "Novák"): ["B-P B-pf", "I-P B-ps"]}`."""

    def __init__(self, found: dict[tuple[str, ...], list[str]], probability: float = 0.9) -> None:
        self.found = found
        self.probability = probability
        self.calls: list[list[list[str]]] = []

    def tag(self, sentences: Sequence[Sequence[str]]) -> list[list[list[Label]]]:
        self.calls.append([list(sentence) for sentence in sentences])
        tagged: list[list[list[Label]]] = []
        for sentence in sentences:
            labels: list[list[Label]] = [[] for _ in sentence]
            for needle, needle_labels in self.found.items():
                for first in range(len(sentence) - len(needle) + 1):
                    if tuple(sentence[first : first + len(needle)]) == needle:
                        for offset, token_labels in enumerate(needle_labels):
                            labels[first + offset] = [
                                (label, self.probability) for label in token_labels.split()
                            ]
            tagged.append(labels)
        return tagged


def _detector(found: dict[tuple[str, ...], list[str]], probability: float = 0.9) -> NametagDetector:
    return NametagDetector(StandInTagger(found, probability), StandInSplitter(), name="nametag")


def _found(detector: NametagDetector, text: str) -> set[tuple[str, str | None]]:
    return {(str(entity.type), entity.text) for entity in detector.detect(_page(text))}


class TestTaggedEntities:
    def test_nested_person_with_first_name_and_surname(self):
        labels = _labels("", "B-P B-pf", "I-P B-ps", "")
        assert tagged_entities(labels) == [
            TaggedEntity("P", 1, 2, 0.9),
            TaggedEntity("pf", 1, 1, 0.9),
            TaggedEntity("ps", 2, 2, 0.9),
        ]

    def test_b_label_starts_a_new_entity_of_the_same_type(self):
        assert [(e.label, e.first, e.last) for e in tagged_entities(_labels("B-ps", "B-ps"))] == [
            ("ps", 0, 0),
            ("ps", 1, 1),
        ]

    def test_another_type_at_a_depth_closes_the_deeper_entities(self):
        labels = _labels("B-P B-pf", "B-A B-gs", "I-A")
        assert {(e.label, e.first, e.last) for e in tagged_entities(labels)} == {
            ("P", 0, 0),
            ("pf", 0, 0),
            ("A", 1, 2),
            ("gs", 1, 1),
        }

    def test_an_i_label_after_outside_opens_an_entity(self):
        # IOB, as in CoNLL-2003: an entity may begin with I-.
        assert [
            (e.label, e.first, e.last) for e in tagged_entities(_labels("", "I-PER", "I-PER"))
        ] == [("PER", 1, 2)]

    def test_score_is_the_lowest_probability(self):
        labels = [[("B-P", 0.9)], [("I-P", 0.6)], [("I-P", 0.8)]]
        assert tagged_entities(labels) == [TaggedEntity("P", 0, 2, 0.6)]

    def test_entity_open_at_the_end_is_closed(self):
        assert tagged_entities(_labels("", "B-PER")) == [TaggedEntity("PER", 1, 1, 0.9)]

    def test_no_labels(self):
        assert tagged_entities(_labels("", "")) == []
        assert tagged_entities([]) == []


def _tokens(*forms: str) -> list[Token]:
    tokens, position = [], 0
    for form in forms:
        tokens.append(Token(form, position, position + len(form)))
        position += len(form) + 1
    return tokens


class TestAddressRuns:
    SENTENCE = _tokens("bytem", "Dlouhá", "12", ",", "110", "00", "Praha", "1", "a", "Brno")

    def test_parts_separated_by_punctuation_form_one_address(self):
        tagged = [
            TaggedEntity("gs", 1, 1, 0.9),
            TaggedEntity("ah", 2, 2, 0.8),
            TaggedEntity("az", 4, 5, 0.95),
            TaggedEntity("gq", 6, 7, 0.7),
            TaggedEntity("gu", 6, 6, 0.99),
        ]
        assert address_runs(self.SENTENCE, tagged) == [TaggedEntity("A", 1, 7, 0.7)]

    def test_a_word_between_parts_ends_the_run(self):
        tagged = [TaggedEntity("gs", 1, 2, 0.9), TaggedEntity("gu", 9, 9, 0.9)]
        # "Brno" after "a" is a town alone: dropped.
        assert address_runs(self.SENTENCE, tagged) == [TaggedEntity("A", 1, 2, 0.9)]

    def test_a_town_alone_is_a_place(self):
        assert address_runs(self.SENTENCE, [TaggedEntity("gu", 6, 6, 0.9)]) == []

    def test_a_container_and_its_parts_are_one_address(self):
        tagged = [
            TaggedEntity("A", 1, 7, 0.8),
            TaggedEntity("gs", 1, 1, 0.9),
            TaggedEntity("gu", 6, 6, 0.9),
        ]
        assert address_runs(self.SENTENCE, tagged) == [TaggedEntity("A", 1, 7, 0.8)]

    def test_other_types_are_ignored(self):
        assert address_runs(self.SENTENCE, [TaggedEntity("P", 1, 2, 0.9)]) == []


class TestDetector:
    def test_a_person_is_its_outermost_container(self):
        detector = _detector({("Jan", "Novák"): ["B-P B-pf", "I-P B-ps"]})
        entities = detector.detect(_page("Smlouvu podepsal Jan Novák."))
        assert [(entity.type, entity.text) for entity in entities] == [
            (EntityType.PERSON, "Jan Novák")
        ]
        assert entities[0].source is DetectionSource.MODEL
        assert entities[0].score == pytest.approx(0.9)
        assert len(entities[0].bboxes) == 2

    def test_a_name_part_alone_is_a_person(self):
        detector = _detector({("Svobodovi",): ["B-ps"], ("Pražané",): ["B-pc"]})
        assert _found(detector, "Volal Svobodovi, přišli Pražané.") == {("person", "Svobodovi")}

    @pytest.mark.parametrize("label", ["PER", "PERSON"])
    def test_flat_person_labels(self, label: str):
        detector = _detector(
            {("Ján", "Kováč"): [f"B-{label}", f"I-{label}"], ("Tatra",): ["B-ORG"]}
        )
        assert _found(detector, "Ján Kováč pracuje v Tatra.") == {("person", "Ján Kováč")}

    def test_address_parts_become_one_address_and_a_town_alone_is_dropped(self):
        detector = _detector(
            {
                ("Dlouhá", "12"): ["B-gs", "B-ah"],
                ("110", "00"): ["B-az", "I-az"],
                ("Praha",): ["B-gu"],
                ("Brně",): ["B-gu"],
            }
        )
        found = _found(detector, "Bydlí Dlouhá 12, 110 00 Praha, narodil se v Brně.")
        assert found == {("address", "Dlouhá 12, 110 00 Praha")}

    def test_a_span_is_widened_to_whole_words_without_edge_punctuation(self):
        # The splitter cuts "J." from "Novák"; the span covers both words.
        detector = _detector({("J", ".", "Novák"): ["B-P", "I-P", "I-P"]})
        assert _found(detector, "Podepsal (J. Novák) dnes.") == {("person", "J. Novák")}

    def test_one_character_is_dropped(self):
        detector = _detector({("J",): ["B-pf"]})
        assert _found(detector, "Podepsal J sám.") == set()

    def test_sentences_keep_their_offsets(self):
        tagger = StandInTagger({("Eva", "Malá"): ["B-P", "I-P"]})
        detector = NametagDetector(tagger, StandInSplitter(), name="nametag")
        text = "První věta bez jména.\nDruhá věta: Eva Malá."
        (entity,) = detector.detect(_page(text))
        assert (entity.start, entity.end) == (text.index("Eva"), text.index("Eva") + 8)
        assert tagger.calls == [
            [
                ["První", "věta", "bez", "jména", "."],
                ["Druhá", "věta", ":", "Eva", "Malá", "."],
            ]
        ]

    def test_an_empty_page_asks_nothing(self):
        tagger = StandInTagger({})
        detector = NametagDetector(tagger, StandInSplitter(), name="nametag")
        assert detector.detect(_page("  \n ")) == []
        assert tagger.calls == []

    def test_name(self):
        assert _detector({}).name == "nametag"


class StandInEncoding:
    def __init__(self, input_ids: list[list[int]], word_ids: list[list[int | None]]) -> None:
        self._input_ids = input_ids
        self._word_ids = word_ids

    def __getitem__(self, key: str) -> list[list[int]]:
        assert key == "input_ids"
        return self._input_ids

    def word_ids(self, index: int) -> list[int | None]:
        return self._word_ids[index]


class StandInTokenizer:
    """Cuts each word into pieces of three characters; a zero-width space into nothing."""

    cls_token_id, sep_token_id, unk_token_id = 0, 2, 3

    def __init__(self, model_max_length: int = 512) -> None:
        self.model_max_length = model_max_length
        self.vocabulary: dict[str, int] = {}
        self.seen: list[list[str]] = []

    def __call__(self, forms: list[list[str]], **options: Any) -> StandInEncoding:
        assert options == {
            "add_special_tokens": False,
            "is_split_into_words": True,
            "verbose": False,
        }
        self.seen += forms
        input_ids: list[list[int]] = []
        word_ids: list[list[int | None]] = []
        for sentence in forms:
            input_ids.append([])
            word_ids.append([])
            for index, form in enumerate(sentence):
                for start in range(0, len(form.replace("​", "")), 3):
                    piece = form[start : start + 3]
                    input_ids[-1].append(
                        self.vocabulary.setdefault(piece, 10 + len(self.vocabulary))
                    )
                    word_ids[-1].append(index)
        return StandInEncoding(input_ids, word_ids)


class StandInNetwork:
    """Labels each token by its first subword: `{subword id: [(label id, probability)]}`."""

    def __init__(self, labels_by_subword: dict[int, list[tuple[int, float]]] | None = None) -> None:
        self.labels_by_subword = labels_by_subword or {}
        self.batches: list[list[Window]] = []

    def label_ids(self, windows: Sequence[Window]) -> list[LabelIds]:
        self.batches.append(list(windows))
        return [
            [
                self.labels_by_subword.get(window.input_ids[position], [])
                for position in window.first_subwords
            ]
            for window in windows
        ]


LABELS = ["<mask>", "<pad>", "<unk>", "<eow>", "<bos>", "O", "B-P", "I-P", "B-pf"]
SENTENCE_OPTIONS = {"context_type": "sentence", "keep_original_casing": False}
DOCUMENT_OPTIONS = {"context_type": "split_document", "keep_original_casing": False}


class TestTagger:
    def test_sentences_are_inputs_of_their_own(self):
        tokenizer = StandInTokenizer()
        tagger = Nametag3Tagger(SENTENCE_OPTIONS, LABELS, tokenizer, StandInNetwork())
        windows = tagger.windows([["Jan", "Novákovi"], ["Eva"]])
        novakovi = [
            tokenizer.vocabulary["Nov"],
            tokenizer.vocabulary["áko"],
            tokenizer.vocabulary["vi"],
        ]
        assert windows == [
            Window([0, tokenizer.vocabulary["Jan"], *novakovi, 2], [1, 2]),
            Window([0, tokenizer.vocabulary["Eva"], 2], [1]),
        ]

    def test_a_document_model_packs_sentences_while_they_fit(self):
        tokenizer = StandInTokenizer(model_max_length=8)
        tagger = Nametag3Tagger(DOCUMENT_OPTIONS, LABELS, tokenizer, StandInNetwork())
        windows = tagger.windows([["Jan"], ["Eva"], ["Petr", "Malý"]])
        # The third sentence (4 subwords) would bring the first input to 8.
        assert [window.first_subwords for window in windows] == [[1, 2], [1, 3]]
        assert [len(window.input_ids) for window in windows] == [4, 6]
        assert all(window.input_ids[0] == 0 and window.input_ids[-1] == 2 for window in windows)

    def test_a_long_sentence_is_cut_between_tokens(self):
        tokenizer = StandInTokenizer(model_max_length=6)
        tagger = Nametag3Tagger(SENTENCE_OPTIONS, LABELS, tokenizer, StandInNetwork())
        windows = tagger.windows([["aaa", "bbb", "cccddd", "eee"]])
        assert all(len(window.input_ids) < 6 for window in windows)
        assert sum(len(window.first_subwords) for window in windows) == 4

    def test_a_token_without_subwords_is_unknown(self):
        tagger = Nametag3Tagger(SENTENCE_OPTIONS, LABELS, StandInTokenizer(), StandInNetwork())
        (window,) = tagger.windows([["​"]])
        assert window.input_ids == [0, 3, 2]

    def test_capitals_are_title_cased_and_text_normalised(self):
        tokenizer = StandInTokenizer()
        tagger = Nametag3Tagger(SENTENCE_OPTIONS, LABELS, tokenizer, StandInNetwork())
        tagger.windows([["NOVÁK", "ČR", "Novák", "é"]])
        assert tokenizer.seen == [["Novák", "Čr", "Novák", "é"]]
        original = StandInTokenizer()
        kept = Nametag3Tagger(
            {**SENTENCE_OPTIONS, "keep_original_casing": True}, LABELS, original, StandInNetwork()
        )
        kept.windows([["NOVÁK"]])
        assert original.seen == [["NOVÁK"]]

    def test_labels_are_named_per_sentence(self):
        tokenizer = StandInTokenizer()
        tokenizer.vocabulary = {"Jan": 20, "Nov": 21}
        network = StandInNetwork(
            {
                # bookkeeping skipped, a list stops at O
                20: [(6, 0.9), (3, 0.5), (8, 0.8)],
                21: [(7, 0.7), (5, 0.6), (8, 0.9)],
            }
        )
        tagger = Nametag3Tagger(SENTENCE_OPTIONS, LABELS, tokenizer, network)
        assert tagger.tag([["Jan", "Novák"], ["a"]]) == [
            [[("B-P", 0.9), ("B-pf", 0.8)], [("I-P", 0.7)]],
            [[]],
        ]
        assert tagger.tag([]) == []

    def test_a_multitagset_model_drops_the_suffix(self):
        tokenizer = StandInTokenizer()
        tokenizer.vocabulary = {"Ján": 20}
        labels = ["<mask>", "O", "B-PER-conll", "B-PER-uner"]
        tagger = Nametag3Tagger(
            DOCUMENT_OPTIONS, labels, tokenizer, StandInNetwork({20: [(2, 0.9)]}), tagset="conll"
        )
        assert tagger.tag([["Ján"]]) == [[[("B-PER", 0.9)]]]

    def test_windows_are_sent_in_batches(self):
        network = StandInNetwork()
        tagger = Nametag3Tagger(SENTENCE_OPTIONS, LABELS, StandInTokenizer(), network)
        tagged = tagger.tag([["slovo"]] * (BATCH_SIZE + 1))
        assert [len(batch) for batch in network.batches] == [BATCH_SIZE, 1]
        assert len(tagged) == BATCH_SIZE + 1


def test_tagset_mask():
    labels = ["<mask>", "O", "B-PER-conll", "B-PER-uner", "I-MISC-conll"]
    assert tagset_mask(labels, None) == [0.0] * 5
    assert tagset_mask(labels, "conll") == [-1e9, 0.0, 0.0, -1e9, 0.0]


class Declared:
    def __init__(self, model_max_length: int | None) -> None:
        self.model_max_length = model_max_length


@pytest.mark.parametrize(("declared", "expected"), [(256, 256), (10**30, 512), (None, 512)])
def test_max_length(declared: int | None, expected: int):
    assert max_length(Declared(declared)) == expected


class TestMappings:
    def test_reads_nametags_pickle_as_plain_attributes(self, tmp_path: Path):
        module = types.ModuleType("nametag3_dataset")

        class NameTag3Dataset:
            pass

        NameTag3Dataset.__module__ = "nametag3_dataset"
        NameTag3Dataset.__qualname__ = "NameTag3Dataset"
        module.NameTag3Dataset = NameTag3Dataset  # pyright: ignore[reportAttributeAccessIssue]
        sys.modules["nametag3_dataset"] = module
        try:
            mappings = NameTag3Dataset()
            mappings._id2label = ["<mask>", "O", "B-P"]  # pyright: ignore[reportAttributeAccessIssue]
            path = tmp_path / "mappings.pickle"
            path.write_bytes(pickle.dumps(mappings, protocol=3))
        finally:
            del sys.modules["nametag3_dataset"]
        assert read_mappings(path) == {"_id2label": ["<mask>", "O", "B-P"]}

    def test_refuses_anything_else(self, tmp_path: Path):
        path = tmp_path / "mappings.pickle"
        path.write_bytes(pickle.dumps(os.getcwd))
        with pytest.raises(pickle.UnpicklingError, match="unexpected object"):
            read_mappings(path)

    def test_refuses_plain_data(self, tmp_path: Path):
        path = tmp_path / "mappings.pickle"
        path.write_bytes(pickle.dumps({"_id2label": []}))
        with pytest.raises(pickle.UnpicklingError, match="does not hold"):
            read_mappings(path)


class TestLoading:
    MODEL = "nametag3-czech-cnec2.0-240830"

    def test_missing_files_name_the_fetch_command(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match=re.escape(f"download.py fetch {self.MODEL}")):
            load_nametag_detector(tmp_path, self.MODEL)

    def test_the_model_directory_is_the_one_with_options(self, tmp_path: Path):
        catalog = load_catalog()
        directory = catalog[self.MODEL].directory(tmp_path)
        with pytest.raises(FileNotFoundError, match="found 0"):
            model_directory(tmp_path, self.MODEL, catalog)
        unpacked = directory / "archive" / "model"
        unpacked.mkdir(parents=True)
        (unpacked / "options.json").write_text("{}", encoding="utf-8")
        assert model_directory(tmp_path, self.MODEL, catalog) == unpacked


class TestNetwork:
    """The network on a tiny random encoder, against the same layers computed by hand."""

    HIDDEN, UNITS, LABELS = 8, 4, 7

    @pytest.fixture
    def torch(self) -> Any:
        pytest.importorskip("h5py")
        pytest.importorskip("transformers")
        return pytest.importorskip("torch")

    def _checkpoint(self, tmp_path: Path, torch: Any, *, nested: bool) -> tuple[Path, Path, Any]:
        import h5py  # pyright: ignore[reportMissingImports]
        import transformers  # pyright: ignore[reportMissingImports]

        encoder_dir = tmp_path / "encoder"
        encoder_dir.mkdir()
        config = transformers.RobertaConfig(
            vocab_size=30,
            hidden_size=self.HIDDEN,
            num_hidden_layers=1,
            num_attention_heads=2,
            intermediate_size=16,
            max_position_embeddings=40,
        )
        config.save_pretrained(encoder_dir)
        torch.manual_seed(0)
        encoder = transformers.AutoModel.from_config(config).eval()
        generator = torch.Generator().manual_seed(1)

        def random(*shape: int) -> Any:
            return torch.randn(*shape, generator=generator)

        heads: dict[str, Any] = (
            {
                "layers/decoder_training/_embeddings/vars/0": random(self.LABELS, self.UNITS),
                "layers/decoder_training/_decoder_lstm/cell/vars/0": random(
                    self.UNITS + self.HIDDEN, 4 * self.UNITS
                ),
                "layers/decoder_training/_decoder_lstm/cell/vars/1": random(
                    self.UNITS, 4 * self.UNITS
                ),
                "layers/decoder_training/_decoder_lstm/cell/vars/2": random(4 * self.UNITS),
                "layers/decoder_training/_decoder_output_layer/vars/0": random(
                    self.UNITS, self.LABELS
                ),
                "layers/decoder_training/_decoder_output_layer/vars/1": random(self.LABELS),
            }
            if nested
            else {
                "layers/dense/vars/0": random(self.HIDDEN, self.LABELS),
                "layers/dense/vars/1": random(self.LABELS),
            }
        )
        checkpoint = tmp_path / "checkpoint.weights.h5"
        with h5py.File(checkpoint, "w") as weights:
            for name, value in encoder.state_dict().items():
                weights[f"layers/plm_layer/_plm/vars/{name}"] = value.numpy()
            for path, value in heads.items():
                weights[path] = value.numpy()
        return checkpoint, encoder_dir, (encoder, heads)

    WINDOWS = (Window([0, 5, 6, 7, 2], [1, 3]), Window([0, 8, 2], [1]))

    def _gathered(self, torch: Any, encoder: Any) -> list[Any]:
        rows = []
        for window in self.WINDOWS:
            with torch.no_grad():
                hidden = encoder(input_ids=torch.tensor([window.input_ids])).last_hidden_state[0]
            rows.append(hidden[window.first_subwords])
        return rows

    def test_flat_head_is_a_masked_dense_layer(self, tmp_path: Path, torch: Any):
        from anonymizer.core.detect.nametag_network import Nametag3Network

        checkpoint, encoder_dir, (encoder, heads) = self._checkpoint(tmp_path, torch, nested=False)
        mask = [0.0] * (self.LABELS - 1) + [-1e9]
        network = Nametag3Network.load(
            checkpoint, encoder_dir, nested=False, latent_dim=0, mask=mask
        )
        answer = network.label_ids(self.WINDOWS)
        for gathered, window_answer in zip(self._gathered(torch, encoder), answer, strict=True):
            logits = gathered @ heads["layers/dense/vars/0"] + heads["layers/dense/vars/1"]
            logits = logits + torch.tensor(mask)
            probabilities, label_ids = torch.softmax(logits, dim=-1).max(dim=-1)
            assert [token[0][0] for token in window_answer] == label_ids.tolist()
            assert [token[0][1] for token in window_answer] == pytest.approx(
                probabilities.tolist(), abs=1e-5
            )

    def test_nested_head_is_keras_lstm_decoding(self, tmp_path: Path, torch: Any):
        from anonymizer.core.detect.nametag_model import BOS, EOW, MAX_LABELS_PER_TOKEN
        from anonymizer.core.detect.nametag_network import Nametag3Network

        checkpoint, encoder_dir, (encoder, heads) = self._checkpoint(tmp_path, torch, nested=True)
        network = Nametag3Network.load(
            checkpoint, encoder_dir, nested=True, latent_dim=self.UNITS, mask=[]
        )
        answer = network.label_ids(self.WINDOWS)
        prefix = "layers/decoder_training/"
        embedding = heads[prefix + "_embeddings/vars/0"]
        kernel, recurrent, bias = (
            heads[prefix + f"_decoder_lstm/cell/vars/{index}"] for index in range(3)
        )
        output_kernel = heads[prefix + "_decoder_output_layer/vars/0"]
        output_bias = heads[prefix + "_decoder_output_layer/vars/1"]
        longest = max(len(window.first_subwords) for window in self.WINDOWS)
        for gathered, window_answer in zip(self._gathered(torch, encoder), answer, strict=True):
            # Keras's LSTM cell, gates in the order input, forget, cell, output.
            hidden = cell = torch.zeros(self.UNITS)
            previous, token, expected = BOS, 0, [[] for _ in range(len(gathered))]
            for _ in range(MAX_LABELS_PER_TOKEN * longest):
                if token == len(gathered):
                    break
                inputs = torch.cat([embedding[previous], gathered[token]])
                z = inputs @ kernel + hidden @ recurrent + bias
                i, f, c, o = z.split(self.UNITS)
                cell = torch.sigmoid(f) * cell + torch.sigmoid(i) * torch.tanh(c)
                hidden = torch.sigmoid(o) * torch.tanh(cell)
                probabilities = torch.softmax(hidden @ output_kernel + output_bias, dim=-1)
                previous = int(probabilities.argmax())
                if previous == EOW:
                    token += 1
                else:
                    expected[token].append(previous)
            assert [[label for label, _ in labels] for labels in window_answer] == expected

    def test_a_decoder_of_another_size_is_refused(self, tmp_path: Path, torch: Any):
        from anonymizer.core.detect.nametag_network import Nametag3Network

        checkpoint, encoder_dir, _ = self._checkpoint(tmp_path, torch, nested=True)
        with pytest.raises(ValueError, match="units"):
            Nametag3Network.load(checkpoint, encoder_dir, nested=True, latent_dim=256, mask=[])


ROOT = Path(os.environ.get("ANONYMIZER_RESOURCE_ROOT", Path(__file__).resolve().parents[2]))


def _real(model_id: str) -> NametagDetector:
    pytest.importorskip("torch")
    pytest.importorskip("ufal.udpipe")
    try:
        detector = load_name_model(model_id, ROOT)
    except FileNotFoundError:
        pytest.skip(f"{model_id} not fetched")
    assert isinstance(detector, NametagDetector)
    return detector


@pytest.mark.model
def test_real_czech_model_finds_a_name_and_a_whole_address():
    detector = _real("nametag3-czech-cnec2.0-240830")
    # Synthetic; a name in capitals and an inflected one.
    found = _found(
        detector,
        "Kupující Ing. Jan Nováček, bytem Dlouhá 12, 110 00 Praha 1, uzavírá smlouvu "
        "s paní Marií ŠŤASTNOU, narozenou v Brně.",
    )
    assert found == {
        ("person", "Jan Nováček"),
        ("person", "Marií ŠŤASTNOU"),
        ("address", "Dlouhá 12, 110 00 Praha 1"),
    }


@pytest.mark.model
def test_real_multilingual_model_finds_slovak_names():
    detector = _real("nametag3-multilingual-260521")
    found = _found(detector, "Včera prišiel Ján Kováč do Bratislavy a pozdravil Máriu.")
    assert found == {("person", "Ján Kováč"), ("person", "Máriu")}
