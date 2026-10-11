"""The recall-weighted loss on hand-made tensors; no model is loaded.

Skipped without PyTorch (CI installs no training group); the comparison
with gliner's own cross-entropy also needs gliner.
"""

import math
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

torch = pytest.importorskip("torch")

from experiments.examples import Example  # noqa: E402
from experiments.loss import LossWeights, weighted_loss, weighted_trainer  # noqa: E402

CE = LossWeights()
LABELS = ("person", "street address", "organization")


def _logit(probability: float) -> float:
    return math.log(probability / (1 - probability))


def _pairs(*pairs: tuple[float, float]) -> tuple[Any, Any, Any, Any]:
    """One text, one label: a span per (probability, target), every span and label valid."""
    logits = torch.tensor([[[_logit(p)] for p, _ in pairs]])
    labels = torch.tensor([[[target] for _, target in pairs]])
    return logits, labels, torch.ones(1, 1), torch.ones(1, len(pairs), dtype=torch.bool)


def test_weight_one_is_binary_cross_entropy():
    # A found name (p 0.9), a missed one (p 0.2), a rejected non-name (p 0.1).
    loss = weighted_loss(*_pairs((0.9, 1.0), (0.2, 1.0), (0.1, 0.0)), CE)
    expected = -math.log(0.9) - math.log(0.2) - math.log(1 - 0.1)
    assert float(loss) == pytest.approx(expected, rel=1e-6)


def test_the_weight_raises_the_cost_of_a_missed_name_only():
    missed = _pairs((0.2, 1.0))
    rejected = _pairs((0.1, 0.0))
    false_alarm = _pairs((0.8, 0.0))
    weighted = LossWeights(positive_weight=3.0)
    assert float(weighted_loss(*missed, weighted)) == pytest.approx(
        3 * float(weighted_loss(*missed, CE))
    )
    assert float(weighted_loss(*rejected, weighted)) == float(weighted_loss(*rejected, CE))
    assert float(weighted_loss(*false_alarm, weighted)) == float(weighted_loss(*false_alarm, CE))
    # Equally confident errors: the miss now costs three times the false alarm.
    assert float(weighted_loss(*_pairs((0.2, 1.0)), weighted)) == pytest.approx(
        3 * float(weighted_loss(*_pairs((0.8, 0.0)), weighted))
    )


def test_the_focus_fades_easy_negatives_and_never_a_positive():
    focused = LossWeights(negative_focus=2.0)
    easy = _pairs((0.1, 0.0))
    assert float(weighted_loss(*easy, focused)) == pytest.approx(
        0.1**2 * float(weighted_loss(*easy, CE))
    )
    for probability in (0.2, 0.6, 0.99):
        positive = _pairs((probability, 1.0))
        assert float(weighted_loss(*positive, focused)) == float(weighted_loss(*positive, CE))


def test_masked_spans_and_padded_labels_count_nothing():
    # Two texts, two labels; the second text's last span lies past its end and
    # its second label is padding.
    logits = torch.randn(2, 3, 2, requires_grad=True)
    labels = torch.tensor(
        [[[1.0, 0.0], [0.0, 0.0], [0.0, 1.0]], [[0.0, 0.0], [1.0, 0.0], [0.0, 0.0]]]
    )
    prompts_mask = torch.tensor([[1, 1], [1, 0]])
    span_mask = torch.tensor([[True, True, True], [True, True, False]])
    weights = LossWeights(positive_weight=5.0, negative_focus=1.0)
    loss = weighted_loss(logits, labels, prompts_mask, span_mask, weights)
    loss.backward()
    assert logits.grad is not None
    assert torch.all(logits.grad[1, 2] == 0)
    assert torch.all(logits.grad[1, :, 1] == 0)
    assert torch.all(logits.grad[0] != 0)
    changed = logits.detach().clone()
    changed[1, 2] += 7.0
    changed[1, :, 1] -= 7.0
    assert float(weighted_loss(changed, labels, prompts_mask, span_mask, weights)) == float(
        loss.detach()
    )


def test_weight_one_equals_the_cross_entropy_gliner_computes():
    pytest.importorskip("gliner")
    from gliner.modeling.base import (  # pyright: ignore[reportMissingImports]
        BaseModel,
        UniEncoderSpanModel,
    )

    generator = torch.Generator().manual_seed(7)
    # Logits as the forward pass returns them: (texts, tokens, widths, labels).
    logits = torch.randn(3, 5, 4, 3, generator=generator) * 4
    labels = (torch.rand(3, 20, 3, generator=generator) < 0.1).float()
    prompts_mask = torch.tensor([[1, 1, 1], [1, 1, 0], [1, 0, 0]])
    span_mask = torch.rand(3, 20, generator=generator) < 0.8
    stand_in = SimpleNamespace()
    stand_in._loss = lambda *args, **kwargs: BaseModel._loss(stand_in, *args, **kwargs)  # pyright: ignore[reportArgumentType]
    reference = UniEncoderSpanModel.loss(
        stand_in,  # pyright: ignore[reportArgumentType]
        logits,
        labels,
        prompts_mask,
        span_mask,
        alpha=-1.0,
        gamma=0.0,
        reduction="sum",
        masking="none",
    )
    ours = weighted_loss(logits, labels, prompts_mask, span_mask, CE)
    assert float(ours) == pytest.approx(float(reference), rel=1e-6)


class StandInTrainer:
    """gliner's Trainer as the weighted one uses it: its own loss and the model's outputs."""

    def compute_loss(
        self,
        model: Any,
        inputs: dict[str, Any],
        return_outputs: bool = False,
        num_items_in_batch: Any = None,
    ) -> Any:
        assert return_outputs
        return torch.tensor(99.0), model(**inputs)


def test_the_trainer_replaces_the_loss_with_the_weighted_one():
    logits, labels, prompts_mask, span_mask = _pairs((0.2, 1.0), (0.1, 0.0))

    def model(**inputs: Any) -> SimpleNamespace:
        assert torch.equal(inputs["labels"], labels)
        return SimpleNamespace(logits=logits, prompts_embedding_mask=prompts_mask)

    weights = LossWeights(positive_weight=4.0)
    trainer = weighted_trainer(weights, base=StandInTrainer)()
    inputs = {"labels": labels, "span_mask": span_mask}
    expected = float(weighted_loss(logits, labels, prompts_mask, span_mask, weights))
    assert float(trainer.compute_loss(model, inputs)) == pytest.approx(expected)
    loss, outputs = trainer.compute_loss(model, inputs, return_outputs=True)
    assert float(loss) == pytest.approx(expected)
    assert outputs.logits is logits


@pytest.mark.model
def test_weight_one_is_the_loss_gliner_computes_on_the_real_model():
    pytest.importorskip("gliner")
    from anonymizer.core.detect.gliner import load_gliner_model

    try:
        model: Any = load_gliner_model(Path(__file__).resolve().parents[2])
    except FileNotFoundError:
        pytest.skip("GLiNER not fetched")
    # Synthetic examples in the training format: every name is invented.
    examples = [
        Example(("Smlouvu", "podepsal", "Jan", "Novák", "."), ((2, 3, "person"),), LABELS),
        Example(
            ("Bydlí", "v", "Lipové", "12", ",", "Brno", "."), ((2, 5, "street address"),), LABELS
        ),
        Example(("Firma", "Tatra", "stojí", "."), ((1, 1, "organization"),), LABELS),
    ]
    collator = model.data_collator_class(
        model.config, data_processor=model.data_processor, prepare_labels=True
    )
    batch = collator([example.to_gliner() for example in examples])
    inputs = {key: value for key, value in batch.items() if isinstance(value, torch.Tensor)}
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs, alpha=-1.0, gamma=0.0, reduction="sum", masking="none")
        ours = weighted_loss(
            outputs.logits,
            inputs["labels"],
            outputs.prompts_embedding_mask,
            inputs["span_mask"],
            CE,
        )
    assert float(ours) == pytest.approx(float(outputs.loss), rel=1e-6)
