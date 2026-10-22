"""The verdict rule fixed before the test (`experiments.verdict`), on hand-made comparisons."""

import json
from pathlib import Path
from typing import Any

import pytest

from experiments.__main__ import main
from experiments.verdict import SetVerdict, sentence, set_outcome, verdicts


def _diff(low: float, high: float) -> dict[str, float]:
    return {"delta": (low + high) / 2, "low": low, "high": high, "p_value": 0.5}


@pytest.mark.parametrize(
    ("f2", "residual", "outcome"),
    [
        ((0.01, 0.05), (-0.05, -0.01), "win"),
        # Better on F2 alone, or on residual share alone, is no win.
        ((0.01, 0.05), (-0.05, 0.01), "tie"),
        ((-0.01, 0.05), (-0.05, -0.01), "tie"),
        ((-0.02, 0.03), (-0.02, 0.03), "tie"),
        # Significantly worse on either is a loss, even when better on the other.
        ((-0.05, -0.01), (-0.05, -0.01), "loss"),
        ((0.01, 0.05), (0.01, 0.05), "loss"),
        # An interval touching zero excludes nothing.
        ((0.0, 0.05), (-0.05, -0.01), "tie"),
    ],
)
def test_one_set(f2: tuple[float, float], residual: tuple[float, float], outcome: str):
    assert set_outcome(_diff(*f2), _diff(*residual)) == outcome


def _verdict(corpus: str, outcome: str) -> SetVerdict:
    return SetVerdict(corpus, _diff(0, 0), _diff(0, 0), outcome)  # pyright: ignore[reportArgumentType]


def test_the_sentence_fixed_for_each_combination():
    wins = [_verdict(c, "win") for c in ("a", "b", "c")]
    assert sentence(wins) == "beats NameTag 3 multilingual on the reserved test data"
    some = [_verdict("a", "win"), _verdict("b", "tie"), _verdict("c", "win")]
    assert sentence(some) == "at least as good as NameTag 3 multilingual; better on a, c"
    ties = [_verdict(c, "tie") for c in ("a", "b")]
    assert sentence(ties) == "no measurable difference from NameTag 3 multilingual"
    mixed = [_verdict("a", "win"), _verdict("b", "loss"), _verdict("c", "tie")]
    assert sentence(mixed) == ("does not beat NameTag 3 multilingual; better on a, worse on b")
    assert sentence([_verdict("a", "loss")]).endswith("better on none, worse on a")


def _results(stage: str = "final") -> dict[str, Any]:
    def comparison(baseline: str, f2: tuple[float, float], residual: tuple[float, float]):
        return {
            "baseline": baseline,
            "candidate": "rules+own",
            "differences": {"partial": {"person": {"f2": _diff(*f2)}}},
            "coverage": {"person": {"residual": _diff(*residual)}},
        }

    return {
        "name": "rq6-test",
        "stage": stage,
        "corpora": {
            "cnec-2.0/etest": {
                "comparisons": [
                    comparison("rules+nametag-multi", (0.01, 0.05), (-0.05, -0.01)),
                    comparison("rules+nametag-cs", (-0.05, -0.01), (0.01, 0.05)),
                ]
            },
            "uner-sk-snk/test": {
                "comparisons": [comparison("rules+nametag-multi", (-0.01, 0.03), (-0.03, 0.01))]
            },
        },
    }


def test_only_the_named_opponents_comparisons_count():
    outcomes = verdicts(_results(), "rules+nametag-multi", "rules+own")
    assert [(v.corpus, v.outcome) for v in outcomes] == [
        ("cnec-2.0/etest", "win"),
        ("uner-sk-snk/test", "tie"),
    ]
    with pytest.raises(ValueError, match="no comparison"):
        verdicts(_results(), "rules+nametag-multi", "rules+other")


def test_the_command_prints_the_table_and_the_sentence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    path = tmp_path / "rq6-test.json"
    path.write_text(json.dumps(_results()), encoding="utf-8")
    assert main(["verdict", str(path), "--candidate", "rules+own"]) == 0
    out = capsys.readouterr().out
    assert "| cnec-2.0/etest | +0.030 [+0.010, +0.050] | -0.030 [-0.050, -0.010] | win |" in out
    assert (
        "Fixed sentence: at least as good as NameTag 3 multilingual; better on cnec-2.0/etest."
        in out
    )
    assert "Development data" not in out

    path.write_text(json.dumps(_results(stage="dev")), encoding="utf-8")
    assert main(["verdict", str(path), "--candidate", "rules+own"]) == 0
    assert "Development data" in capsys.readouterr().out
    assert main(["verdict", str(path), "--candidate", "rules+other"]) == 2
