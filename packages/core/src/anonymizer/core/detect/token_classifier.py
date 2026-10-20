"""Name and address detection with a token classifier: one BIO label per word.

A token classifier is an encoder (XLM-RoBERTa large for the models trained
here, `experiments/train.py`) with a linear layer writing one label per
subword: `O`, or `B-` or `I-` and a type. Its types are named after GLiNER's
prompt labels (`person`, `street address`, `organization`), so it answers
GLiNER's `inference` call and runs inside `GlinerDetector`: the page's
windows, the widening to whole words, the distractor, the threshold and the
experiments' cache are shared, and the two model families differ only in
the model.

- **Words are GLiNER's tokens** (`gliner_tokens`: a word, or one punctuation
  mark), the units the training examples are written in
  (`experiments/examples.py`). Each word is cut into subwords on its own
  (`word_subwords`, used by training too) and labelled at its first subword.
- **An input holds at most the encoder's length** (512 subwords for XLM-R,
  its two special tokens included). The detector's windows of 150 GLiNER
  tokens almost always fit; a longer text is read in parts that overlap by
  `OVERLAP_SUBWORDS`, cut between words, and each word takes its label from
  the part where it has the most context on both sides. A single word longer
  than a whole input keeps its first subwords only: its label is read at the
  first one.
- **Decoding is greedy per word** (the most probable label). `I-` after `O`
  or after another type starts a span instead of being dropped, since a
  dropped start would leave the name readable.
- **A span's score is the mean, over its words, of the probability of its
  type** (`B-` plus `I-`). The threshold filters whole spans and never
  changes how they are decoded, so asking at a low threshold and filtering
  upwards gives the same spans as asking at the higher one, which the
  experiments' cache relies on. Spans scoring at most the threshold are
  dropped, as GLiNER drops them.

PyTorch and `transformers` are optional (the `ner` group) and imported only
when a model is loaded. The classifier itself needs a tokenizer and an
object with a `probabilities` method, which keeps it testable without them.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Self

from anonymizer.core.detect.gliner import (
    DEFAULT_DISTRACTORS,
    DEFAULT_LABELS,
    GlinerDetector,
    encoder_resource,
    force_offline,
    gliner_tokens,
    require_stored,
    without_known_warnings,
)
from anonymizer.core.detect.nametag_model import max_length
from anonymizer.core.log import step
from anonymizer.core.resources import Catalog, load_catalog
from anonymizer.core.types import EntityType

log = logging.getLogger(__name__)

TOKEN_CLASSIFIER_ENGINE = "token-classifier"
"""The catalog's `engine` of a token classifier trained here."""

DEFAULT_THRESHOLD = 0.5
"""Minimum span score. The most probable label of a word may have less than
0.5, so the default keeps the spans the model is sure of; recall is tuned
downwards on development data, as GLiNER's threshold is."""

OUTSIDE = "O"
"""The label of a word outside every span; id 0 in the models trained here."""

OVERLAP_SUBWORDS = 64
"""Subwords shared by consecutive parts of a text longer than one input."""

BATCH_SIZE = 8
"""Inputs per forward pass."""


@dataclass(frozen=True, slots=True)
class Window:
    """One encoder input.

    Attributes:
        input_ids: Subword ids, special tokens included.
        first_subwords: Position in `input_ids` of each word's first subword.
        first_word: Index of the input's first word in the text.
    """

    input_ids: list[int]
    first_subwords: list[int]
    first_word: int


class Network(Protocol):
    """The part of a token classification model the classifier uses."""

    def probabilities(self, windows: Sequence[Window]) -> list[list[list[float]]]:
        """Return, per window and word, the probability of each label id."""
        ...

    def to(self, device: str) -> Any:
        """Move the model to a torch device."""
        ...


def bio_labels(types: Sequence[str]) -> list[str]:
    """Return the labels of a classifier for its types, in id order: `O`, then `B-` and `I-`.

    Args:
        types: The types, in order (GLiNER's prompt labels).
    """
    return [OUTSIDE, *(f"{prefix}-{kind}" for kind in types for prefix in ("B", "I"))]


def word_subwords(tokenizer: Any, words: Sequence[str]) -> list[list[int]]:
    """Return the subword ids of each word, each word cut on its own.

    Training and detection both cut words this way, so a word is the same
    subwords in both. A word the tokenizer drops entirely is read as unknown.

    Args:
        tokenizer: A `transformers` tokenizer, or a stand-in.
        words: The words.

    Returns:
        One non-empty list of ids per word.
    """
    if not words:
        return []
    encoded = tokenizer(list(words), add_special_tokens=False)["input_ids"]
    return [list(ids) or [tokenizer.unk_token_id] for ids in encoded]


def word_windows(
    subwords: Sequence[Sequence[int]], body: int, overlap: int = OVERLAP_SUBWORDS
) -> list[tuple[int, int]]:
    """Return `(first, end)` word ranges whose subwords fit in `body`, overlapping by `overlap`.

    Every word lies in at least one range. A word longer than `body` is a
    range of its own (its subwords are cut when the input is built).

    Args:
        subwords: Each word's subword ids.
        body: Subwords per input, special tokens excluded.
        overlap: Subwords the next range repeats at least, where it can.
    """
    ranges: list[tuple[int, int]] = []
    first = 0
    while first < len(subwords):
        end, length = first, 0
        while end < len(subwords) and length + len(subwords[end]) <= body:
            length += len(subwords[end])
            end += 1
        end = max(end, first + 1)
        ranges.append((first, end))
        if end == len(subwords):
            break
        following, repeated = end, 0
        while following - 1 > first and repeated + len(subwords[following - 1]) <= overlap:
            following -= 1
            repeated += len(subwords[following])
        first = following
    return ranges


def decode(
    probabilities: Sequence[Sequence[float]], labels: Sequence[str]
) -> list[tuple[int, int, str, float]]:
    """Decode words' label probabilities into spans, greedily (see the module docstring).

    Args:
        probabilities: Per word, the probability of each label id.
        labels: The label of each id.

    Returns:
        `(first, last, type, score)`: word indices, the last one included,
        and the mean probability of the type over the span's words.
    """
    spans: list[tuple[int, int, str, float]] = []
    current: tuple[int, str, list[float]] | None = None

    def close(last: int) -> None:
        if current is not None:
            first, kind, scores = current
            spans.append((first, last, kind, sum(scores) / len(scores)))

    for index, distribution in enumerate(probabilities):
        best = max(range(len(distribution)), key=distribution.__getitem__)
        prefix, _, kind = labels[best].partition("-")
        if labels[best] == OUTSIDE:
            close(index - 1)
            current = None
            continue
        type_probability = sum(
            probability
            for label, probability in zip(labels, distribution, strict=True)
            if label in {f"B-{kind}", f"I-{kind}"}
        )
        if prefix == "I" and current is not None and current[1] == kind:
            current[2].append(type_probability)
            continue
        close(index - 1)
        current = (index, kind, [type_probability])
    close(len(probabilities) - 1)
    return spans


class TokenClassifier:
    """A token classification model answering GLiNER's `inference` call.

    Attributes:
        tokenizer: The encoder's tokenizer.
        network: The encoder and its classification layer.
        labels: The label of each id (`bio_labels`).
        types: The types the model labels, in id order.
        max_length: Subwords per input, special tokens included.
    """

    def __init__(
        self, tokenizer: Any, network: Network, labels: Sequence[str], max_length: int
    ) -> None:
        """Assemble a classifier from loaded parts (see `load_token_classifier`).

        Args:
            tokenizer: A `transformers` tokenizer, or a stand-in.
            network: The model, or a stand-in.
            labels: The label of each id: `O`, then `B-<type>` and `I-<type>`.
            max_length: Subwords per input, special tokens included.

        Raises:
            ValueError: If a label is neither `O` nor `B-`/`I-` and a type,
                or an input could not hold a subword.
        """
        if OUTSIDE not in labels or any(
            label != OUTSIDE and label.partition("-")[0] not in {"B", "I"} for label in labels
        ):
            msg = f"labels must be {OUTSIDE!r} and B-/I- types, not {list(labels)}"
            raise ValueError(msg)
        if max_length < 3:
            msg = f"an input of {max_length} subwords holds no word"
            raise ValueError(msg)
        self.tokenizer = tokenizer
        self.network = network
        self.labels = list(labels)
        self.types = list(
            dict.fromkeys(label.partition("-")[2] for label in labels if label != OUTSIDE)
        )
        self.max_length = max_length

    def to(self, device: str) -> Self:
        """Move the model to a torch device (`cpu`, `cuda`, `mps`); return the classifier."""
        self.network.to(device)
        return self

    def inference(
        self,
        texts: list[str],
        labels: list[str],
        *,
        threshold: float,
        flat_ner: bool,
    ) -> list[list[dict[str, Any]]]:
        """Return, per text, the spans of the asked types scoring above the threshold.

        Args:
            texts: The texts (the detector's windows).
            labels: The types asked for; a type the model does not know finds nothing.
            threshold: Spans scoring at most this are dropped.
            flat_ner: Accepted for GLiNER's signature; BIO spans never overlap.

        Returns:
            Per text, dicts with `start`, `end` (character offsets into the
            text), `label` and `score`.
        """
        del flat_ner
        asked = {label.lower() for label in labels}
        words = [gliner_tokens(text) for text in texts]
        windows = [self.windows(text, spans) for text, spans in zip(texts, words, strict=True)]
        flat = [window for text_windows in windows for window in text_windows]
        probabilities: list[list[list[float]]] = []
        for first in range(0, len(flat), BATCH_SIZE):
            probabilities += self.network.probabilities(flat[first : first + BATCH_SIZE])
        answers: list[list[dict[str, Any]]] = []
        for text_words, text_windows in zip(words, windows, strict=True):
            per_window = probabilities[: len(text_windows)]
            probabilities = probabilities[len(text_windows) :]
            per_word = _most_context(len(text_words), text_windows, per_window)
            answers.append(
                [
                    {
                        "start": text_words[first][0],
                        "end": text_words[last][1],
                        "label": kind,
                        "score": score,
                    }
                    for first, last, kind, score in decode(per_word, self.labels)
                    if kind.lower() in asked and score > threshold
                ]
            )
        return answers

    def windows(self, text: str, words: Sequence[tuple[int, int]]) -> list[Window]:
        """Encode a text's words into inputs (see the module docstring).

        Args:
            text: The text.
            words: Its words as character spans (`gliner_tokens`).

        Returns:
            The inputs, in order; none for a text without words.
        """
        subwords = word_subwords(self.tokenizer, [text[start:end] for start, end in words])
        body = self.max_length - 2
        cls, sep = self.tokenizer.cls_token_id, self.tokenizer.sep_token_id
        windows: list[Window] = []
        for first, end in word_windows(subwords, body):
            input_ids, first_subwords = [cls], []
            for word in subwords[first:end]:
                first_subwords.append(len(input_ids))
                input_ids.extend(word[:body])
            windows.append(Window([*input_ids, sep], first_subwords, first))
        return windows


def _most_context(
    count: int, windows: Sequence[Window], probabilities: Sequence[Sequence[Sequence[float]]]
) -> list[Sequence[float]]:
    """Pick each word's label probabilities from the window where it has most context."""
    chosen: list[Sequence[float]] = [()] * count
    context = [-1] * count
    for window, window_probabilities in zip(windows, probabilities, strict=True):
        size = len(window.first_subwords)
        for offset, distribution in enumerate(window_probabilities):
            room = min(offset, size - 1 - offset)
            word = window.first_word + offset
            if room > context[word]:
                chosen[word], context[word] = distribution, room
    return chosen


class TransformersNetwork:
    """A `transformers` token classification model, behind `Network`."""

    def __init__(self, model: Any, pad_id: int) -> None:
        """Wrap a loaded model.

        Args:
            model: An `AutoModelForTokenClassification` model, in eval mode.
            pad_id: The tokenizer's padding id.
        """
        self.model = model
        self.pad_id = pad_id

    def to(self, device: str) -> Self:
        """Move the model to a torch device; return the network."""
        self.model.to(device)
        return self

    def probabilities(self, windows: Sequence[Window]) -> list[list[list[float]]]:
        """Run the model on a batch of inputs, padded to the longest."""
        import torch  # pyright: ignore[reportMissingImports]

        longest = max(len(window.input_ids) for window in windows)
        input_ids = torch.full((len(windows), longest), self.pad_id, dtype=torch.long)
        attention = torch.zeros((len(windows), longest), dtype=torch.long)
        for row, window in enumerate(windows):
            input_ids[row, : len(window.input_ids)] = torch.tensor(window.input_ids)
            attention[row, : len(window.input_ids)] = 1
        device = next(self.model.parameters()).device
        with torch.inference_mode():
            logits = self.model(
                input_ids=input_ids.to(device), attention_mask=attention.to(device)
            ).logits
        distributions = logits.float().softmax(dim=-1).cpu()
        return [
            distributions[row, window.first_subwords].tolist() for row, window in enumerate(windows)
        ]


def load_token_classifier(model_dir: Path, tokenizer_dir: Path) -> TokenClassifier:
    """Load a token classifier from local files only, on the CPU.

    Args:
        model_dir: Directory with `config.json` (its `id2label` names the
            labels) and `model.safetensors`.
        tokenizer_dir: Directory with the encoder's tokenizer.

    Returns:
        The classifier, in inference mode.

    Raises:
        ImportError: If the optional `ner` dependencies are not installed.
        ValueError: If the model's labels are not BIO labels.
    """
    force_offline()
    with without_known_warnings():
        try:
            import transformers  # pyright: ignore[reportMissingImports]
        except ImportError as error:
            msg = "name detection needs the optional 'ner' dependencies: uv sync --group ner"
            raise ImportError(msg) from error
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            str(tokenizer_dir), local_files_only=True
        )
        model = transformers.AutoModelForTokenClassification.from_pretrained(
            str(model_dir), local_files_only=True
        ).eval()
    labels = [model.config.id2label[index] for index in range(model.config.num_labels)]
    network = TransformersNetwork(model, tokenizer.pad_token_id)
    return TokenClassifier(tokenizer, network, labels, max_length(tokenizer))


def load_token_classifier_model(
    root: Path, model_id: str, *, catalog: Catalog | None = None
) -> TokenClassifier:
    """Load a catalog token classifier and its tokenizer from a storage root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).
        model_id: Catalog id of the model.
        catalog: The resource catalog; the shipped one and the root's
            trained models when omitted.

    Returns:
        The classifier, on the CPU.

    Raises:
        FileNotFoundError: If the model or its tokenizer is not stored.
        ImportError: If the optional `ner` dependencies are not installed.
    """
    catalog = catalog or load_catalog(root=root)
    require_stored(catalog, model_id, root)
    with step(log, "load name model", done_level=logging.INFO, model=model_id):
        return load_token_classifier(
            catalog[model_id].directory(root),
            catalog[encoder_resource(catalog, model_id)].directory(root),
        )


def load_token_classifier_detector(
    root: Path,
    model_id: str,
    *,
    catalog: Catalog | None = None,
    labels: Mapping[str, EntityType] = DEFAULT_LABELS,
    threshold: float = DEFAULT_THRESHOLD,
) -> GlinerDetector:
    """Build a detector from a catalog token classifier stored under a storage root.

    Args:
        root: Storage root holding `models/`.
        model_id: Catalog id of the model.
        catalog: The resource catalog; the shipped one and the root's
            trained models when omitted.
        labels: Type name → entity type, as GLiNER's prompts.
        threshold: Minimum span score.

    Returns:
        A ready detector, named after the model.

    Raises:
        FileNotFoundError: If the model or its tokenizer is not stored.
        ImportError: If the optional `ner` dependencies are not installed.
    """
    model = load_token_classifier_model(root, model_id, catalog=catalog)
    return GlinerDetector(
        model, labels=labels, threshold=threshold, name=model_id, distractors=DEFAULT_DISTRACTORS
    )
