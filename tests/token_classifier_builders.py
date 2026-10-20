"""Stand-ins for a token classifier, and a tiny real one built offline.

The stand-ins need nothing optional. `tiny_token_classifier` builds a random
XLM-RoBERTa token classifier and a word-piece tokenizer from a few invented
sentences in a folder, so the `transformers` path runs without downloading
anything; it needs PyTorch, `transformers` and `tokenizers`.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from anonymizer.core.detect.token_classifier import OUTSIDE, Window, bio_labels

TYPES = ("person", "street address", "organization")
LABELS = bio_labels(TYPES)
PIECE = 4


class StandInTokenizer:
    """Cuts each word into pieces of four characters, numbering pieces as it meets them."""

    cls_token_id, pad_token_id, sep_token_id, unk_token_id = 0, 1, 2, 3

    def __init__(self, model_max_length: int = 512) -> None:
        self.model_max_length = model_max_length
        self.ids: dict[str, int] = {}
        self.pieces: dict[int, str] = {}

    def __call__(self, words: list[str], *, add_special_tokens: bool) -> dict[str, Any]:
        assert not add_special_tokens
        return {"input_ids": [self._encode(word) for word in words]}

    def _encode(self, word: str) -> list[int]:
        encoded = []
        for start in range(0, len(word), PIECE):
            piece = word[start : start + PIECE]
            if piece not in self.ids:
                self.ids[piece] = len(self.ids) + 10
                self.pieces[self.ids[piece]] = piece
            encoded.append(self.ids[piece])
        return encoded


class StandInNetwork:
    """Labels a word by its first piece: `tags` maps a piece to a label, else `O`.

    The chosen label gets `confidence`, the others share the rest equally.
    """

    def __init__(
        self,
        tokenizer: StandInTokenizer,
        tags: dict[str, str],
        confidence: float = 0.9,
        labels: Sequence[str] = LABELS,
    ) -> None:
        self.tokenizer = tokenizer
        self.tags = tags
        self.confidence = confidence
        self.labels = list(labels)
        self.windows: list[Window] = []
        self.devices: list[str] = []

    def to(self, device: str) -> "StandInNetwork":
        self.devices.append(device)
        return self

    def probabilities(self, windows: Sequence[Window]) -> list[list[list[float]]]:
        self.windows += windows
        rest = (1 - self.confidence) / (len(self.labels) - 1)
        answers = []
        for window in windows:
            per_word = []
            for position in window.first_subwords:
                piece = self.tokenizer.pieces[window.input_ids[position]]
                label = self.tags.get(piece, OUTSIDE)
                per_word.append(
                    [self.confidence if name == label else rest for name in self.labels]
                )
            answers.append(per_word)
        return answers


SENTENCES = (
    "Smlouvu podepsal Jan Novák , bytem Lipová 12 , Brno .",
    "Pozdravuj Ján Kováč a Petru Svobodovou z Nadace Karla Dvořáka .",
    "Volal Svobodovi - Novákovi včera ; 777 123 456 .",
)


def tiny_token_classifier(folder: Path, *, max_length: int = 32) -> tuple[Path, Path]:
    """Write a random tiny XLM-R token classifier and its tokenizer into a folder.

    Returns:
        The model folder and the tokenizer folder.
    """
    import torch  # pyright: ignore[reportMissingImports]
    import transformers  # pyright: ignore[reportMissingImports]
    from tokenizers import (  # pyright: ignore[reportMissingImports]
        Tokenizer,
        models,
        pre_tokenizers,
        trainers,
    )

    tokenizer_dir, model_dir = folder / "tokenizer", folder / "model"
    specials = ["<s>", "<pad>", "</s>", "<unk>"]
    word_pieces = Tokenizer(models.WordPiece(unk_token="<unk>"))  # pyright: ignore[reportCallIssue]
    word_pieces.pre_tokenizer = pre_tokenizers.Whitespace()  # pyright: ignore[reportAttributeAccessIssue]
    word_pieces.train_from_iterator(
        SENTENCES, trainers.WordPieceTrainer(vocab_size=120, special_tokens=specials)
    )
    tokenizer = transformers.PreTrainedTokenizerFast(
        tokenizer_object=word_pieces,
        bos_token="<s>",
        cls_token="<s>",
        pad_token="<pad>",
        sep_token="</s>",
        eos_token="</s>",
        unk_token="<unk>",
        model_max_length=max_length,
    )
    tokenizer.save_pretrained(str(tokenizer_dir))
    config = transformers.XLMRobertaConfig(
        vocab_size=len(tokenizer),
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=32,
        # RoBERTa counts positions from the padding id + 1.
        max_position_embeddings=max_length + 2,
        pad_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.cls_token_id,
        eos_token_id=tokenizer.sep_token_id,
        num_labels=len(LABELS),  # pyright: ignore[reportCallIssue]
        id2label=dict(enumerate(LABELS)),
        label2id={label: index for index, label in enumerate(LABELS)},
    )
    torch.manual_seed(0)
    transformers.AutoModelForTokenClassification.from_config(config).save_pretrained(str(model_dir))
    return model_dir, tokenizer_dir
