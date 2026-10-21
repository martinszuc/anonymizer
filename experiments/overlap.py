"""Training text that also occurs in development or test data, found so it can be dropped.

Corpora drawn from the same sources share sentences: WikiGoldSK and UNER
Slovak-SNK both read Slovak Wikipedia, and nothing says where UNER's other
genres come from. A model trained on a sentence it is later scored on is
scored on what it memorised, so a training config that reads such a corpus
(`DatasetSpec.check_overlap`) sets `drop_overlap`, and every train sentence
whose text occurs in a dev or test split of any dataset of `DATASETS` is left
out before examples are cut, and counted.

Texts are compared by `text_key`: NFC, every whitespace character removed,
so a sentence matches whether its corpus joined tokens by spaces (CNEC,
WikiGoldSK) or kept the writer's spacing (UNER), then hashed. The unit is a
corpus's sentence: a sentence, a SlavicNER paragraph, a whole REDACT or
OpenPII record. A sentence repeated inside a longer unit of another corpus is
not found.

This is the one place training opens a test split: its texts are read and
hashed, never its gold spans, and nothing is scored on it.
"""

from __future__ import annotations

import hashlib
import unicodedata
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from experiments.datasets import DATASETS, DatasetSpec, Role, Sentence, TextForm, read_sentences


def text_key(text: str) -> bytes | None:
    """Return the key two texts share when they differ in whitespace only; `None` for no text."""
    compact = "".join(unicodedata.normalize("NFC", text).split())
    return hashlib.sha256(compact.encode("utf-8")).digest() if compact else None


@dataclass
class HeldTexts:
    """The texts of every dev and test split, by key.

    Attributes:
        sources: Text key → the splits (`<dataset>/<split>`) holding it.
        sentences: Sentences (or records) read, per split.
    """

    sources: dict[bytes, tuple[str, ...]] = field(default_factory=dict)
    sentences: dict[str, int] = field(default_factory=dict)

    def splits_of(self, text: str) -> tuple[str, ...]:
        """Return the dev and test splits holding a text; empty when none does."""
        key = text_key(text)
        return () if key is None else self.sources.get(key, ())


def held_texts(
    resource_root: Path,
    datasets: Mapping[str, DatasetSpec] = DATASETS,
    read: Callable[[str, str, Path, TextForm], list[list[Sentence]]] = read_sentences,
) -> HeldTexts:
    """Read the text of every dev and test split of the datasets.

    Args:
        resource_root: Storage root holding `data/`.
        datasets: The datasets whose dev and test splits are held out.
        read: Reads a split as sentences (`datasets.read_sentences`).

    Returns:
        The texts' keys and the splits holding each.

    Raises:
        FileNotFoundError: If a dataset is not stored under the root: the
            check would otherwise pass without having looked.
    """
    held = HeldTexts()
    found: dict[bytes, list[str]] = {}
    for dataset, spec in datasets.items():
        for split, role in spec.splits.items():
            if role is Role.TRAIN:
                continue
            name = f"{dataset}/{split}"
            groups = read(dataset, split, resource_root, TextForm.WRITTEN)
            held.sentences[name] = sum(len(sentences) for sentences in groups)
            for sentences in groups:
                for sentence in sentences:
                    key = text_key(sentence.text)
                    if key is not None and name not in found.setdefault(key, []):
                        found[key].append(name)
    held.sources = {key: tuple(names) for key, names in found.items()}
    return held


@dataclass
class OverlapFilter:
    """Tells `load_corpus` to leave out held-out text, and counts where each match came from.

    Attributes:
        held: The dev and test texts.
        sources: Matches per dev or test split; a sentence held by two
            splits counts in both.
    """

    held: HeldTexts
    sources: Counter[str] = field(default_factory=Counter)

    def __call__(self, sentence: Sentence) -> bool:
        """Return whether the sentence is held out (and count it)."""
        splits = self.held.splits_of(sentence.text)
        self.sources.update(splits)
        return bool(splits)
