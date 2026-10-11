"""NameTag 3's network in plain PyTorch, read from its Keras checkpoint.

`checkpoint.weights.h5` holds Keras 3 weights. The encoder is a
`transformers` model whose `state_dict` Keras stored by parameter name; the
heads are three small layers stored as Keras variables:

- flat (`decoding = "classification"`): one dense layer over the first
  subword of each token, plus a mask that keeps the labels of one tagset
  when the model was trained on several (`conll`, `uner`, `onto`);
- nested (`decoding = "seq2seq"`): a label embedding, an LSTM cell and a
  dense layer. Starting from a begin label, each step reads the previous
  label and the current token's encoding and writes the next label; an
  end-of-token label moves on to the next token (hard attention).

Keras stores a dense kernel as (inputs, outputs) and an LSTM's kernels as
(inputs, 4 * units) with gates in the order input, forget, cell, output,
the same order as PyTorch's `LSTMCell`, so each is transposed and nothing
is reordered. Padding follows NameTag: id 0 under a zero attention mask.

Imported only when a NameTag model is loaded: it needs PyTorch, `h5py` and
`transformers` (the `ner` dependency group).
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Self

import h5py  # pyright: ignore[reportMissingImports]
import torch  # pyright: ignore[reportMissingImports]
import transformers  # pyright: ignore[reportMissingImports]
from anonymizer.core.detect.gliner import without_known_warnings
from anonymizer.core.detect.nametag_model import BOS, EOW, MAX_LABELS_PER_TOKEN, LabelIds, Window

ENCODER_VARIABLES = "layers/plm_layer/_plm/vars"
FLAT_HEAD = "layers/dense"
NESTED_HEAD = "layers/decoder_training"


class Nametag3Network:
    """The encoder and head of a NameTag 3 model, in inference mode on the CPU."""

    def __init__(self, encoder: torch.nn.Module, head: FlatHead | NestedHead) -> None:
        """Assemble a network from its parts (see `load`)."""
        self.encoder = encoder.eval()
        self.head = head.eval()

    @classmethod
    def load(
        cls,
        checkpoint: Path,
        encoder_dir: Path,
        *,
        nested: bool,
        latent_dim: int,
        mask: Sequence[float],
    ) -> Self:
        """Read a NameTag 3 checkpoint into an encoder built from local files.

        Args:
            checkpoint: The model's `checkpoint.weights.h5`.
            encoder_dir: Directory with the encoder's `config.json`.
            nested: Whether the model decodes nested labels (seq2seq).
            latent_dim: The decoder's units, as the options state them.
            mask: Per label, 0 to allow it and -1e9 to rule it out (flat only).

        Returns:
            The network.

        Raises:
            RuntimeError: If the checkpoint does not fit the encoder's config.
            ValueError: If the decoder's size differs from `latent_dim`.
        """
        with without_known_warnings():
            config = transformers.AutoConfig.from_pretrained(
                str(encoder_dir), local_files_only=True
            )
            encoder = transformers.AutoModel.from_config(config)
        with h5py.File(checkpoint, "r") as weights:
            group: Any = weights[ENCODER_VARIABLES]
            encoder.load_state_dict(
                {name: torch.from_numpy(group[name][()]) for name in group}, strict=True
            )
            if nested:
                head: FlatHead | NestedHead = NestedHead.from_keras(weights[NESTED_HEAD])
                if head.cell.hidden_size != latent_dim:
                    msg = f"decoder has {head.cell.hidden_size} units, options say {latent_dim}"
                    raise ValueError(msg)
            else:
                head = FlatHead.from_keras(weights[FLAT_HEAD], torch.tensor(list(mask)))
        return cls(encoder, head)

    def label_ids(self, windows: Sequence[Window]) -> list[LabelIds]:
        """Return, per window and token, the label ids written and their probabilities."""
        longest = max(len(window.input_ids) for window in windows)
        most_tokens = max(len(window.first_subwords) for window in windows)
        input_ids = torch.zeros((len(windows), longest), dtype=torch.long)
        attention = torch.zeros((len(windows), longest), dtype=torch.long)
        first_subwords = torch.zeros((len(windows), most_tokens), dtype=torch.long)
        for row, window in enumerate(windows):
            input_ids[row, : len(window.input_ids)] = torch.tensor(window.input_ids)
            attention[row, : len(window.input_ids)] = 1
            first_subwords[row, : len(window.first_subwords)] = torch.tensor(window.first_subwords)
        token_counts = [len(window.first_subwords) for window in windows]
        with torch.inference_mode():
            hidden = self.encoder(input_ids=input_ids, attention_mask=attention).last_hidden_state
            gathered = torch.take_along_dim(hidden, first_subwords.unsqueeze(-1), dim=1)
            return self.head.label_ids(gathered, token_counts)


class FlatHead(torch.nn.Module):
    """A dense layer over each token, masked to one tagset, argmax per token."""

    def __init__(self, kernel: torch.Tensor, bias: torch.Tensor, mask: torch.Tensor) -> None:
        """Build the layer from Keras's kernel (inputs, outputs), bias and a label mask."""
        super().__init__()
        self.dense = torch.nn.Linear(kernel.shape[0], kernel.shape[1])
        self.dense.weight.data = kernel.T.contiguous()
        self.dense.bias.data = bias
        self.register_buffer("mask", mask)

    @classmethod
    def from_keras(cls, group: Any, mask: torch.Tensor) -> Self:
        """Read the layer from the checkpoint's `layers/dense` group."""
        return cls(_variable(group, "vars/0"), _variable(group, "vars/1"), mask)

    def label_ids(self, gathered: torch.Tensor, token_counts: Sequence[int]) -> list[LabelIds]:
        """Return each token's one label id and its probability."""
        logits = self.dense(gathered) + self.mask
        probabilities, label_ids = torch.softmax(logits, dim=-1).max(dim=-1)
        return [
            [
                [(int(label_ids[row, token]), float(probabilities[row, token]))]
                for token in range(count)
            ]
            for row, count in enumerate(token_counts)
        ]


class NestedHead(torch.nn.Module):
    """NameTag's seq2seq decoder with hard attention on the current token, greedy."""

    def __init__(
        self,
        embedding: torch.Tensor,
        kernels: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
        output_kernel: torch.Tensor,
        output_bias: torch.Tensor,
    ) -> None:
        """Build the decoder from Keras's variables.

        Args:
            embedding: Label embeddings (labels, units).
            kernels: The LSTM's kernel, recurrent kernel and bias.
            output_kernel: The output layer's kernel (units, labels).
            output_bias: Its bias.
        """
        super().__init__()
        kernel, recurrent_kernel, bias = kernels
        units = recurrent_kernel.shape[0]
        self.embedding = torch.nn.Embedding.from_pretrained(embedding)
        self.cell = torch.nn.LSTMCell(kernel.shape[0], units)
        self.cell.weight_ih.data = kernel.T.contiguous()
        self.cell.weight_hh.data = recurrent_kernel.T.contiguous()
        self.cell.bias_ih.data = bias
        self.cell.bias_hh.data = torch.zeros_like(bias)
        self.output = torch.nn.Linear(units, output_kernel.shape[1])
        self.output.weight.data = output_kernel.T.contiguous()
        self.output.bias.data = output_bias

    @classmethod
    def from_keras(cls, group: Any) -> Self:
        """Read the decoder from the checkpoint's `layers/decoder_training` group."""
        return cls(
            _variable(group, "_embeddings/vars/0"),
            (
                _variable(group, "_decoder_lstm/cell/vars/0"),
                _variable(group, "_decoder_lstm/cell/vars/1"),
                _variable(group, "_decoder_lstm/cell/vars/2"),
            ),
            _variable(group, "_decoder_output_layer/vars/0"),
            _variable(group, "_decoder_output_layer/vars/1"),
        )

    def label_ids(self, gathered: torch.Tensor, token_counts: Sequence[int]) -> list[LabelIds]:
        """Write each token's labels, up to an end-of-token label per token.

        As upstream, decoding stops when every row has passed its last token
        or after `MAX_LABELS_PER_TOKEN` steps per token of the longest row; a
        token cut off there keeps the labels written so far, and the tokens
        after it get none.
        """
        rows = gathered.shape[0]
        batch = torch.arange(rows)
        counts = torch.tensor(token_counts)
        previous = torch.full((rows,), BOS, dtype=torch.long)
        state = (
            torch.zeros((rows, self.cell.hidden_size)),
            torch.zeros((rows, self.cell.hidden_size)),
        )
        current = torch.zeros(rows, dtype=torch.long)
        written: list[LabelIds] = [[[] for _ in range(count)] for count in token_counts]
        steps = 0
        while steps < MAX_LABELS_PER_TOKEN * gathered.shape[1] and not bool(
            torch.all(current == counts)
        ):
            attended = torch.where(current < counts, current, current - 1)
            inputs = torch.cat([self.embedding(previous), gathered[batch, attended]], dim=-1)
            state = self.cell(inputs, state)
            probabilities, predicted = torch.softmax(self.output(state[0]), dim=-1).max(dim=-1)
            for row in range(rows):
                token = int(current[row])
                label_id = int(predicted[row])
                if token < token_counts[row] and label_id != EOW:
                    written[row][token].append((label_id, float(probabilities[row])))
            current = current + ((predicted == EOW) & (current < counts)).long()
            previous = predicted
            steps += 1
        return written


def _variable(group: Any, path: str) -> torch.Tensor:
    return torch.from_numpy(group[path][()])
