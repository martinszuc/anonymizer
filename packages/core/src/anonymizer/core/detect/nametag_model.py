"""A released NameTag 3 model, from tokens to labels, as NameTag's own code reads it.

A model is a directory: `options.json` (its training options),
`mappings.pickle` (the label list) and `checkpoint.weights.h5` (Keras 3
weights, read by `nametag_network.py` without Keras). This module prepares
the network's input and names its output, reproducing NameTag's dataset code:

- Each token is NFC-normalised and cut to 200 characters; unless the model
  keeps the original casing, a word in capitals is title-cased ("NOVÁK"
  becomes "Novák"), NameTag's "poor man's truecasing".
- Tokens are cut into subwords one by one. A sentence becomes
  `[CLS] subwords [SEP]`, cut between tokens where it would reach the
  encoder's length (512 subwords for the released models).
- A model trained on sentences reads each such input alone; one trained on
  documents (`split_document`) reads consecutive ones packed into one input
  while they fit.
- The network writes label ids per token (nested models several, outermost
  first); the bookkeeping labels are dropped, a label list stops at `O`, and
  a multitagset model's labels lose their tagset suffix (`B-PER-conll`).

The label list is a pickled object of NameTag's own class. It is read by an
unpickler that accepts that one class, as a plain attribute holder, and
refuses anything else, so loading it cannot run code.
"""

from __future__ import annotations

import json
import pickle
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Self

from anonymizer.core.detect.gliner import without_known_warnings
from anonymizer.core.detect.nametag import Label

BOS = 4
EOW = 3
CONTROL_LABELS = frozenset({"<mask>", "<pad>", "<unk>", "<eow>", "<bos>"})
"""Labels the decoder uses for bookkeeping; NameTag's ids 0 to 4."""

_ONTONOTES_TYPES = (
    *("PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "DATE", "TIME"),
    *("PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL", "EVENT", "WORK_OF_ART"),
    *("LAW", "LANGUAGE"),
)

TAGSETS: dict[str, tuple[str, ...]] = {
    "conll": ("B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "B-MISC", "I-MISC", "O"),
    "uner": ("B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "O"),
    "onto": ("O", *(f"{prefix}-{kind}" for kind in _ONTONOTES_TYPES for prefix in ("B", "I"))),
}
"""NameTag's built-in tagsets; a multitagset model shipped without its own config uses these."""

PREFIX_SPACE_ENCODERS = frozenset(
    {"roberta-base", "roberta-large", "ufal/robeczech-base", "allenai/biomed_roberta_base"}
)
"""Encoders NameTag tokenizes with a space before each word."""

MAX_CHARACTERS_PER_WORD = 200
MAX_LABELS_PER_TOKEN = 5
UNDECLARED_LENGTH = 10**6
ROBERTA_LENGTH = 512
BATCH_SIZE = 8
RULED_OUT = -1e9

LabelIds = list[list[tuple[int, float]]]
"""Per token, the label ids the network wrote and their probabilities."""


@dataclass(frozen=True, slots=True)
class Window:
    """One encoder input: subword ids and the position of each token's first subword."""

    input_ids: list[int]
    first_subwords: list[int]


class Network(Protocol):
    """The part of NameTag's network the tagger uses."""

    def label_ids(self, windows: Sequence[Window]) -> list[LabelIds]:
        """Return, per window and token, the label ids written and their probabilities."""
        ...


class Nametag3Tagger:
    """A NameTag 3 model, ready to tag sentences of tokens.

    Attributes:
        labels: The label of each id.
        tokenizer: The encoder's subword tokenizer (a `transformers` fast tokenizer).
        network: The encoder and head.
        tagset: The tagset a multitagset model answers in; `None` otherwise.
        max_length: Subwords per encoder input, special tokens included.
    """

    def __init__(
        self,
        options: dict[str, Any],
        labels: Sequence[str],
        tokenizer: Any,
        network: Network,
        tagset: str | None = None,
    ) -> None:
        """Assemble a tagger from loaded parts (see `load`).

        Args:
            options: The model's `options.json`.
            labels: The label of each id.
            tokenizer: The encoder's subword tokenizer, or a stand-in.
            network: The encoder and head, or a stand-in.
            tagset: For a multitagset model, the tagset it answers in.
        """
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.network = network
        self.tagset = tagset
        self.max_length = max_length(tokenizer)
        self._truecase = not options.get("keep_original_casing", False)
        self._by_sentence = options["context_type"] == "sentence"

    @classmethod
    def load(cls, model_dir: Path, encoder_dir: Path, tagset: str | None = None) -> Self:
        """Load a released model from local files.

        Args:
            model_dir: Directory with `options.json`, `mappings.pickle` and the checkpoint.
            encoder_dir: Directory with the encoder's config and tokenizer.
            tagset: For a multitagset model, the tagset to answer in; its
                default (`conll`) when omitted.

        Returns:
            The tagger, in inference mode on the CPU.

        Raises:
            ValueError: If the options name an unknown decoding or tagset.
            ImportError: If the optional `ner` dependencies are not installed.
        """
        options = json.loads((model_dir / "options.json").read_text(encoding="utf-8"))
        decoding = options["decoding"]
        if decoding not in {"classification", "seq2seq"}:
            msg = f"unknown NameTag decoding {decoding!r}"
            raise ValueError(msg)
        nested = decoding == "seq2seq"
        mappings = read_mappings(model_dir / "mappings.pickle")
        labels = list(mappings["_id2label_sublabel" if nested else "_id2label"])
        tagset = (tagset or options["default_tagset"]) if options.get("tagsets") else None
        if tagset is not None and tagset not in TAGSETS:
            msg = f"unknown NameTag tagset {tagset!r}"
            raise ValueError(msg)
        import transformers  # pyright: ignore[reportMissingImports]
        from anonymizer.core.detect.nametag_network import Nametag3Network

        prefix_space = options["hf_plm"] in PREFIX_SPACE_ENCODERS
        with without_known_warnings():
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                str(encoder_dir),
                local_files_only=True,
                **({"add_prefix_space": True} if prefix_space else {}),
            )
        network = Nametag3Network.load(
            model_dir / options["checkpoint_filename"],
            encoder_dir,
            nested=nested,
            latent_dim=int(options.get("latent_dim", 0)),
            mask=tagset_mask(labels, tagset),
        )
        return cls(options, labels, tokenizer, network, tagset)

    def tag(self, sentences: Sequence[Sequence[str]]) -> list[list[list[Label]]]:
        """Return, per sentence and token, its labels outermost first; `[]` for outside.

        Args:
            sentences: One page's sentences of tokens, in order.

        Returns:
            Per sentence and token, `(label, probability)` pairs.
        """
        if not sentences:
            return []
        windows = self.windows(sentences)
        per_token: list[list[Label]] = []
        for first in range(0, len(windows), BATCH_SIZE):
            for window_labels in self.network.label_ids(windows[first : first + BATCH_SIZE]):
                per_token += [self._named(token_labels) for token_labels in window_labels]
        tagged: list[list[list[Label]]] = []
        for sentence in sentences:
            tagged.append(per_token[: len(sentence)])
            per_token = per_token[len(sentence) :]
        return tagged

    def windows(self, sentences: Sequence[Sequence[str]]) -> list[Window]:
        """Encode sentences into encoder inputs, as NameTag's dataset does.

        Args:
            sentences: Sentences of tokens, in order.

        Returns:
            The inputs; every token's first subword lies in exactly one, in order.
        """
        forms = [[self._prepared(form) for form in sentence] for sentence in sentences]
        encoded = self.tokenizer(
            forms, add_special_tokens=False, is_split_into_words=True, verbose=False
        )
        cls, sep = self.tokenizer.cls_token_id, self.tokenizer.sep_token_id
        pieces: list[Window] = []
        for index, sentence in enumerate(forms):
            subwords: list[list[int]] = [[] for _ in sentence]
            for token_id, word in zip(
                encoded["input_ids"][index], encoded.word_ids(index), strict=True
            ):
                if word is not None:
                    subwords[word].append(token_id)
            window = Window([cls], [])
            for word_subwords in subwords:
                # A token the tokenizer drops entirely is read as unknown.
                pieces_of_word = word_subwords or [self.tokenizer.unk_token_id]
                if len(window.input_ids) + len(pieces_of_word) + 1 >= self.max_length:
                    window.input_ids.append(sep)
                    pieces.append(window)
                    window = Window([cls], [])
                window.first_subwords.append(len(window.input_ids))
                window.input_ids.extend(pieces_of_word)
            window.input_ids.append(sep)
            pieces.append(window)
        return pieces if self._by_sentence else self._packed(pieces)

    def _packed(self, pieces: list[Window]) -> list[Window]:
        """Join consecutive sentence inputs while they fit in one (`split_document`)."""
        cls, sep = self.tokenizer.cls_token_id, self.tokenizer.sep_token_id
        windows: list[Window] = []
        for piece in pieces:
            if (
                not windows
                or len(windows[-1].input_ids) + len(piece.input_ids) - 1 >= self.max_length
            ):
                if windows:
                    windows[-1].input_ids.append(sep)
                windows.append(Window([cls], []))
            window = windows[-1]
            offset = len(window.input_ids) - 1
            window.first_subwords.extend(position + offset for position in piece.first_subwords)
            window.input_ids.extend(piece.input_ids[1:-1])
        windows[-1].input_ids.append(sep)
        return windows

    def _prepared(self, form: str) -> str:
        form = unicodedata.normalize("NFC", form[:MAX_CHARACTERS_PER_WORD])
        return form.lower().title() if self._truecase and form.isupper() else form

    def _named(self, token_labels: Sequence[tuple[int, float]]) -> list[Label]:
        """Name a token's label ids, dropping bookkeeping labels and stopping at `O`."""
        named: list[Label] = []
        for label_id, probability in token_labels:
            label = self.labels[label_id]
            if label in CONTROL_LABELS:
                continue
            if label == "O":
                break
            if self.tagset is not None:
                label = label.rsplit("-", 1)[0]
            named.append((label, probability))
        return named


class _Mappings:
    """Stands in for NameTag's dataset class: the pickle holds only its attributes."""


class _MappingsUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str) -> type:
        if (module, name) == ("nametag3_dataset", "NameTag3Dataset"):
            return _Mappings
        msg = f"unexpected object in NameTag mappings: {module}.{name}"
        raise pickle.UnpicklingError(msg)


def read_mappings(path: Path) -> dict[str, Any]:
    """Return the attributes of NameTag's pickled label mappings.

    Raises:
        pickle.UnpicklingError: If the file holds anything but NameTag's mappings.
    """
    with path.open("rb") as stream:
        mappings = _MappingsUnpickler(stream).load()
    if not isinstance(mappings, _Mappings):
        msg = f"{path.name} does not hold NameTag mappings"
        raise pickle.UnpicklingError(msg)
    return vars(mappings)


def tagset_mask(labels: Sequence[str], tagset: str | None) -> list[float]:
    """Return 0 for the labels of a tagset and -1e9 for every other, as NameTag masks them.

    Without a tagset every label is allowed. A multitagset model names its
    labels with the tagset appended (`B-PER-conll`); `O` is shared.
    """
    if tagset is None:
        return [0.0] * len(labels)
    allowed = {label if label == "O" else f"{label}-{tagset}" for label in TAGSETS[tagset]}
    return [0.0 if label in allowed else RULED_OUT for label in labels]


def max_length(tokenizer: Any) -> int:
    """Return the subwords per input NameTag uses: the tokenizer's, or 512 where it declares none.

    NameTag falls back to 512 for RoBERTa and BERT tokenizers, the only
    encoders of the released models.
    """
    declared = tokenizer.model_max_length
    return declared if declared is not None and declared <= UNDECLARED_LENGTH else ROBERTA_LENGTH
