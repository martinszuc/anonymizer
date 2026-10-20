"""Training a token classifier (BIO labels per word) from the examples GLiNER trains on.

The second model family of RQ6: an encoder with a linear layer writing one
label per word (`core.detect.token_classifier`), trained here from a catalog
encoder whose `uses` holds `training` (XLM-RoBERTa large, the encoder of
NameTag 3 multilingual). `train.py` picks this path when the config's `base`
is such an encoder; everything around the model is shared with GLiNER:

- **The same examples.** `examples.py` cuts the same train splits into the
  same examples of at most 150 GLiNER tokens, drawn with the same seed, so
  both families see the same data. Each GLiNER token is a word here: it is
  cut into subwords on its own (`word_subwords`, as detection cuts it) and
  labelled at its first subword (`B-<type>` on a span's first word, `I-` on
  the rest, `O` elsewhere); its other subwords, and the special tokens,
  carry no label (-100). An example longer than the encoder's 512 subwords
  is cut after its last whole word that fits, and counted (`truncated`).
- **The same types.** The labels are GLiNER's prompts (`person`, `street
  address`, and the `organization` distractor), so the trained model runs
  in `GlinerDetector` as GLiNER does and is scored on the same types.
- **What a corpus does not mark is not taught as `O`.** GLiNER asks an
  example only for the labels its corpus marks throughout; a token
  classifier labels every word, so an unmarked organisation in OpenPII
  would be taught as `O` while CNEC teaches it as an organisation. The loss
  therefore accepts, for a word labelled `O`, the labels of the types its
  corpus does not mark (`unmarked`): its term is `-log` of the summed
  probability of `O` and those labels. Where a corpus marks every type, as
  CNEC does, that is plain cross-entropy.
- **The loss** is that cross-entropy averaged over the labelled words
  (`ce`), or, with `loss = "weighted"`, the words inside a span weighted by
  `positive_weight`, so a missed name word costs that many equally confident
  false alarms: the recall-weighted idea of `loss.py` for one label per word.

The classification layer starts random, drawn from the config's seed before
the encoder is loaded; the trainer is seeded by it too. The trained model is
stored as `config.json` (its `id2label` names the labels) and
`model.safetensors`; its tokenizer is the encoder's, a catalog requirement.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from anonymizer.core.detect.nametag_model import max_length
from anonymizer.core.detect.token_classifier import (
    OUTSIDE,
    bio_labels,
    load_token_classifier_model,
    word_subwords,
)
from anonymizer.core.resources import Catalog

from experiments.examples import Example, training_labels

if TYPE_CHECKING:
    from experiments.train import TrainConfig

TYPES = tuple(training_labels().values())
"""The types taught, in id order: GLiNER's prompt labels."""

LABELS = tuple(bio_labels(TYPES))
"""The label of each id: `O`, then `B-` and `I-` per type."""

IGNORED = -100
"""The label of a subword the loss skips."""

PRECISIONS = ("fp32", "bf16", "fp16")
"""Floating-point formats training may run in; the halves on CUDA only."""


@dataclass
class Trainee:
    """A token classification model being trained, with its tokenizer.

    Attributes:
        model: An `AutoModelForTokenClassification` model.
        tokenizer: The encoder's tokenizer.
    """

    model: Any
    tokenizer: Any

    def save_pretrained(self, directory: Path, *, safe_serialization: bool) -> None:
        """Write `config.json` and `model.safetensors` into a directory."""
        del safe_serialization  # transformers 5 writes safetensors only
        self.model.save_pretrained(str(directory))


@dataclass(frozen=True)
class Features:
    """One example as the model reads it.

    Attributes:
        input_ids: Subword ids, special tokens included.
        labels: Label id at each word's first subword, `IGNORED` elsewhere.
        unmarked: Per label id, whether a word labelled `O` may also be it:
            the labels of the types the example's corpus does not mark.
        truncated: Words were cut off to fit the encoder.
    """

    input_ids: list[int]
    labels: list[int]
    unmarked: list[bool]
    truncated: bool


def word_tags(example: Example) -> list[str]:
    """Return the BIO label of each of an example's words."""
    tags = [OUTSIDE] * len(example.tokens)
    for first, last, label in example.spans:
        tags[first] = f"B-{label}"
        for index in range(first + 1, last + 1):
            tags[index] = f"I-{label}"
    return tags


def features(example: Example, tokenizer: Any, length: int) -> Features:
    """Encode an example (see the module docstring).

    Args:
        example: The example, in GLiNER tokens.
        tokenizer: The encoder's tokenizer.
        length: Subwords per input, special tokens included.

    Returns:
        The model's input, labels and the labels an `O` word may also be.
    """
    ids = {label: index for index, label in enumerate(LABELS)}
    input_ids, labels = [tokenizer.cls_token_id], [IGNORED]
    truncated = False
    for subwords, tag in zip(
        word_subwords(tokenizer, example.tokens), word_tags(example), strict=True
    ):
        if len(input_ids) + len(subwords) + 1 > length:
            truncated = True
            break
        input_ids += subwords
        labels += [ids[tag]] + [IGNORED] * (len(subwords) - 1)
    unmarked = [
        label != OUTSIDE and label.partition("-")[2] not in example.labels for label in LABELS
    ]
    return Features([*input_ids, tokenizer.sep_token_id], [*labels, IGNORED], unmarked, truncated)


def collate(batch: Sequence[Features], pad_id: int) -> dict[str, Any]:
    """Pad a batch of examples into tensors."""
    import torch  # pyright: ignore[reportMissingImports]

    longest = max(len(item.input_ids) for item in batch)
    input_ids = torch.full((len(batch), longest), pad_id, dtype=torch.long)
    attention = torch.zeros((len(batch), longest), dtype=torch.long)
    labels = torch.full((len(batch), longest), IGNORED, dtype=torch.long)
    for row, item in enumerate(batch):
        size = len(item.input_ids)
        input_ids[row, :size] = torch.tensor(item.input_ids)
        attention[row, :size] = 1
        labels[row, :size] = torch.tensor(item.labels)
    return {
        "input_ids": input_ids,
        "attention_mask": attention,
        "labels": labels,
        "unmarked": torch.tensor([item.unmarked for item in batch], dtype=torch.bool),
    }


def token_loss(logits: Any, labels: Any, unmarked: Any, positive_weight: float = 1.0) -> Any:
    """Average the cross-entropy over labelled words; an `O` word also accepts its unmarked labels.

    Args:
        logits: (batch, subwords, labels).
        labels: (batch, subwords): label ids, `IGNORED` where none.
        unmarked: (batch, labels): the labels an `O` word of each example may also be.
        positive_weight: Weight of the words inside a span; 1 is cross-entropy.

    Returns:
        The loss, a scalar tensor.
    """
    import torch  # pyright: ignore[reportMissingImports]

    log_probabilities = logits.float().log_softmax(dim=-1)
    labelled = labels != IGNORED
    targets = labels.clamp(min=0)
    gold = log_probabilities.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    accepted = unmarked.unsqueeze(1).expand_as(log_probabilities).clone()
    accepted[..., LABELS.index(OUTSIDE)] = True
    outside = torch.logsumexp(log_probabilities.masked_fill(~accepted, -math.inf), dim=-1)
    is_outside = targets == LABELS.index(OUTSIDE)
    terms = -torch.where(is_outside, outside, gold)
    weights = torch.where(is_outside, 1.0, positive_weight)
    return (terms * weights * labelled).sum() / labelled.sum().clamp(min=1)


def token_trainer(positive_weight: float) -> type:
    """Return a transformers Trainer class whose loss is `token_loss`.

    Imported only here: transformers' Trainer is slow to import and only
    training needs it.
    """
    from transformers import Trainer  # pyright: ignore[reportMissingImports]

    class TokenClassifierTrainer(Trainer):
        def compute_loss(
            self,
            model: Any,
            inputs: dict[str, Any],
            return_outputs: bool = False,
            num_items_in_batch: Any = None,
        ) -> Any:
            del num_items_in_batch  # the loss is a mean over its own batch's words
            labels, unmarked = inputs.pop("labels"), inputs.pop("unmarked")
            outputs = model(**inputs)
            loss = token_loss(outputs.logits, labels, unmarked, positive_weight)
            return (loss, outputs) if return_outputs else loss

    return TokenClassifierTrainer


def load_base(root: Path, model_id: str, catalog: Catalog, seed: int) -> Trainee:
    """Load a catalog encoder with a new classification layer for `LABELS`, on the CPU.

    The layer is drawn from `seed`, set just before.
    """
    import transformers  # pyright: ignore[reportMissingImports]
    from anonymizer.core.detect.gliner import (
        encoder_resource,
        force_offline,
        require_stored,
        without_known_warnings,
    )

    force_offline()
    require_stored(catalog, model_id, root)
    tokenizer_dir = catalog[encoder_resource(catalog, model_id)].directory(root)
    with without_known_warnings():
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            str(tokenizer_dir), local_files_only=True
        )
        transformers.set_seed(seed)
        model = transformers.AutoModelForTokenClassification.from_pretrained(
            str(catalog[model_id].directory(root)),
            local_files_only=True,
            num_labels=len(LABELS),
            id2label=dict(enumerate(LABELS)),
            label2id={label: index for index, label in enumerate(LABELS)},
        )
    return Trainee(model, tokenizer)


def loader(device: str, seed: int, base: str) -> Any:
    """Return `train.Load` for this family: the base as a `Trainee`, a trained model to score."""

    def load(root: Path, model_id: str, catalog: Catalog) -> Any:
        if model_id == base:
            trainee = load_base(root, model_id, catalog, seed)
            trainee.model.to(device)
            return trainee
        return load_token_classifier_model(root, model_id, catalog=catalog).to(device)

    return load


def fit_token_classifier(
    trainee: Trainee, examples: list[Example], config: TrainConfig, work: Path
) -> dict[str, Any]:
    """Train a token classifier in place with transformers' Trainer.

    Args:
        trainee: The model and its tokenizer (`load_base`).
        examples: The drawn examples.
        config: The configuration.
        work: Scratch directory for the trainer; nothing is kept from it.

    Returns:
        The losses logged during training, the trainer's summary and the
        count of examples cut to fit the encoder.
    """
    from transformers import TrainingArguments  # pyright: ignore[reportMissingImports]

    hyper = config.training
    length = max_length(trainee.tokenizer)
    encoded = [features(example, trainee.tokenizer, length) for example in examples]
    arguments = TrainingArguments(
        output_dir=str(work),
        learning_rate=hyper.learning_rate,
        weight_decay=hyper.weight_decay,
        # Whole steps: a float of 1 would mean one step, not the whole run.
        warmup_steps=math.ceil(hyper.steps * hyper.warmup_ratio),
        per_device_train_batch_size=hyper.batch_size,
        max_steps=hyper.steps,
        logging_steps=hyper.logging_steps,
        use_cpu=config.device == "cpu",
        bf16=hyper.precision == "bf16",
        fp16=hyper.precision == "fp16",
        dataloader_num_workers=0,
        dataloader_pin_memory=config.device == "cuda",
        # The examples are not a datasets.Dataset; `unmarked` must reach the loss.
        remove_unused_columns=False,
        save_strategy="no",
        report_to="none",
        seed=config.seed,
        data_seed=config.seed,
    )
    pad_id = trainee.tokenizer.pad_token_id
    trainer = token_trainer(hyper.positive_weight)(
        model=trainee.model,
        args=arguments,
        train_dataset=encoded,
        data_collator=lambda batch: collate(batch, pad_id),
    )
    trainer.train()
    trainee.model.eval()
    history = trainer.state.log_history
    return {
        "loss": [
            {"step": entry["step"], "loss": round(float(entry["loss"]), 4)}
            for entry in history
            if "loss" in entry
        ],
        "summary": {
            key: value
            for entry in history
            for key, value in entry.items()
            if key in {"train_runtime", "train_samples_per_second", "train_steps_per_second"}
        },
        "truncated": sum(item.truncated for item in encoded),
    }
