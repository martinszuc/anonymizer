"""The recall-weighted loss: a missed personal-data span costs more than a false alarm.

**How gliner 0.2.29 computes its training loss** (read from the installed
package; the line of reasoning the weighted loss builds on):

- *Pairs.* `UniEncoderSpanModel.forward` scores every candidate span (each
  start token, widths 1 to `max_width` = 12) against every prompted label:
  logits of shape (batch, tokens x 12, labels). The target of a pair is 1
  when the span carries that label, else 0, and each pair is a separate
  binary decision through a sigmoid (`processor.create_labels`).
- *Per-pair loss.* `BaseModel._loss` calls `focal_loss_with_logits` with the
  trainer's `focal_loss_alpha` and `focal_loss_gamma`; alpha -1 and gamma 0
  (`loss = "ce"` here) leave binary cross-entropy, `-y log p - (1 - y)
  log(1 - p)`, with each probability clamped at 1e-6 before the logarithm.
  Focal multiplies a pair by `(1 - p_t)^gamma` (p_t: the probability of the
  right answer) and weights positives by alpha, negatives by 1 - alpha.
- *Masking.* A pair is multiplied by `prompts_embedding_mask` (labels padded
  to the longest label list in the batch count nothing) and by `span_mask`
  (spans reaching past the text's last token, and the padding of shorter
  texts, count nothing). Targets equal to -100 would be ignored too; the
  span collator never produces any.
- *Negative sampling* exists (`negatives`, `masking`) but is off as
  `create_training_args` sets it: masking `none`, negatives 1.0. Negative
  *types* are sampled from the batch only for examples without
  `ner_labels`; every example here has them (`examples.py`), so each is
  asked exactly its corpus's labels. Label smoothing is 0.
- *Reduction* is a sum over every unmasked pair (`loss_reduction = "sum"`),
  not a mean: a batch's loss grows with its tokens and labels.

**The weighted loss** changes only the per-pair term and keeps the rest:

    loss = -w * y * log p  -  (1 - y) * p^gamma * log(1 - p)

`w` (`positive_weight`) multiplies the term of the positive pairs, the
spans that are personal data: missing one costs `w` times as much as an
equally confident false alarm. `gamma` (`negative_focus`) fades out the
negative pairs the model already rejects (small p), so the many easy
non-entity spans do not drown the few positives; the positives are never
faded, unlike in focal loss, whose `(1 - p_t)^gamma` also weakens a
positive the model finds only just above its threshold. With `w = 1` and
`gamma = 0` the loss is gliner's cross-entropy, value for value (the same
clamping, masks and sum). It is computed from the logits the unchanged
forward pass returns (`weighted_trainer`), so gliner's span enumeration,
masks and label handling are reused, not reimplemented.

In a model that fitted the training data perfectly, weighting the positives
by `w` moves a pair's predicted odds by the factor `w`, as a lower threshold
would; training with it also changes what the encoder learns, which a
threshold cannot. That is why the comparison includes cross-entropy at a
lower threshold (`experiments/README.md`, *Training*).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch  # pyright: ignore[reportMissingImports]

PROBABILITY_FLOOR = 1e-6
"""Probabilities are clamped here before the logarithm, as gliner does."""

IGNORED = -100
"""A target gliner's loss ignores."""


@dataclass(frozen=True)
class LossWeights:
    """The weighted loss's two parameters.

    Attributes:
        positive_weight: Weight of the positive pairs' term; 1 is cross-entropy.
        negative_focus: Exponent of `p` on the negative pairs' term; 0 keeps
            every negative at full weight.
    """

    positive_weight: float = 1.0
    negative_focus: float = 0.0


def weighted_loss(
    logits: Any,
    labels: Any,
    prompts_mask: Any,
    span_mask: Any,
    weights: LossWeights,
) -> Any:
    """Sum the weighted binary cross-entropy over every valid (span, label) pair.

    Args:
        logits: Scores, (batch, spans, labels) or (batch, tokens, widths, labels).
        labels: Targets 0 or 1 (or `IGNORED`), shaped as `logits`.
        prompts_mask: (batch, labels): which labels are real, not padding.
        span_mask: (batch, spans) or (batch, tokens, widths): which spans lie
            inside their text.
        weights: The loss's parameters.

    Returns:
        The loss, a scalar tensor.
    """
    batch, classes = logits.shape[0], logits.shape[-1]
    logits = logits.reshape(batch, -1, classes)
    labels = labels.reshape(batch, -1, classes)
    valid = (labels != IGNORED).float()
    targets = labels.clamp(min=0.0)
    probability = torch.sigmoid(logits)
    positive = -targets * torch.log(probability.clamp(min=PROBABILITY_FLOOR))
    negative = -(1.0 - targets) * torch.log((1.0 - probability).clamp(min=PROBABILITY_FLOOR))
    if weights.negative_focus > 0:
        negative = negative * probability.pow(weights.negative_focus)
    pairs = (weights.positive_weight * positive + negative) * valid
    pairs = pairs * prompts_mask.reshape(batch, 1, classes).float()
    pairs = pairs * span_mask.reshape(batch, -1, 1).float()
    return pairs.sum()


def weighted_trainer(weights: LossWeights, base: type | None = None) -> type:
    """Return a Trainer class whose loss is `weighted_loss`.

    The model's forward pass runs as gliner's Trainer runs it (and computes
    gliner's own loss, which is dropped: a sum over the pairs, cheap beside
    the encoder); the loss is then recomputed from its logits.

    Args:
        weights: The loss's parameters.
        base: The Trainer to extend; gliner's when omitted. Imported only
            here: transformers' Trainer is slow to import and only training
            needs it.
    """
    if base is None:
        from gliner.training import Trainer  # pyright: ignore[reportMissingImports]

        base = Trainer

    class WeightedLossTrainer(base):  # pyright: ignore[reportGeneralTypeIssues]
        def compute_loss(
            self,
            model: Any,
            inputs: dict[str, Any],
            return_outputs: bool = False,
            num_items_in_batch: Any = None,
        ) -> Any:
            _, outputs = super().compute_loss(
                model, inputs, return_outputs=True, num_items_in_batch=num_items_in_batch
            )
            loss = weighted_loss(
                outputs.logits,
                inputs["labels"],
                outputs.prompts_embedding_mask,
                inputs["span_mask"],
                weights,
            )
            return (loss, outputs) if return_outputs else loss

    return WeightedLossTrainer
