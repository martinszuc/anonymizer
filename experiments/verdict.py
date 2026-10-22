"""The verdict of the headline claim, decided by rule from a results file.

The rule was fixed by the author before any test data was read (JOURNAL.md,
2026-10-11, decisions 2B and 3), so the wording of the outcome cannot follow
the numbers:

- a set is a **win** when the candidate is better than the opponent on both
  person F2 (partial match) and residual share, each paired bootstrap 95 %
  interval excluding 0 (F2 above, residual share below);
- a **loss** when it is significantly worse on either;
- a **tie** otherwise.

Across the sets one fixed sentence applies (`sentence`). On development data
the same rule only shows where a candidate stands; the claim is made once, on
the test sets of a `stage = "final"` run.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

Outcome = Literal["win", "loss", "tie"]
OPPONENT_NAME = "NameTag 3 multilingual"


@dataclass(frozen=True)
class SetVerdict:
    """One set's outcome and the two differences it rests on (candidate minus opponent)."""

    corpus: str
    f2: Mapping[str, float]
    residual: Mapping[str, float]
    outcome: Outcome


def set_outcome(f2: Mapping[str, float], residual: Mapping[str, float]) -> Outcome:
    """Apply the rule to one set's paired differences (each with `low` and `high`)."""
    if f2["high"] < 0 or residual["low"] > 0:
        return "loss"
    if f2["low"] > 0 and residual["high"] < 0:
        return "win"
    return "tie"


def verdicts(results: Mapping[str, Any], opponent: str, candidate: str) -> list[SetVerdict]:
    """Return the outcome on every corpus of a run that compares the two systems.

    Raises:
        ValueError: If the run holds no comparison of the opponent with the candidate.
    """
    found: list[SetVerdict] = []
    for corpus, scored in results["corpora"].items():
        for comparison in scored.get("comparisons", []):
            if (comparison["baseline"], comparison["candidate"]) != (opponent, candidate):
                continue
            f2 = comparison["differences"]["partial"]["person"]["f2"]
            residual = comparison["coverage"]["person"]["residual"]
            found.append(SetVerdict(corpus, f2, residual, set_outcome(f2, residual)))
    if not found:
        msg = f"no comparison of {opponent!r} with {candidate!r} in {results['name']!r}"
        raise ValueError(msg)
    return found


def sentence(outcomes: Sequence[SetVerdict]) -> str:
    """Return the sentence fixed in advance for this combination of outcomes."""
    wins = [v.corpus for v in outcomes if v.outcome == "win"]
    losses = [v.corpus for v in outcomes if v.outcome == "loss"]
    if losses:
        better = ", ".join(wins) or "none"
        return f"does not beat {OPPONENT_NAME}; better on {better}, worse on {', '.join(losses)}"
    if len(wins) == len(outcomes):
        return f"beats {OPPONENT_NAME} on the reserved test data"
    if wins:
        return f"at least as good as {OPPONENT_NAME}; better on {', '.join(wins)}"
    return f"no measurable difference from {OPPONENT_NAME}"


def markdown(results: Mapping[str, Any], outcomes: Sequence[SetVerdict], candidate: str) -> str:
    """Render the verdict as a table and the sentence, naming the run's stage."""
    lines = [
        f"Verdict of {candidate} against the opponent, {results['name']} "
        f"(stage {results['stage']})",
        "",
        "| set | ΔF2 (person, partial) | Δresidual share | outcome |",
        "|---|---|---|---|",
    ]
    for verdict in outcomes:
        lines.append(
            f"| {verdict.corpus} | {_interval(verdict.f2)} | {_interval(verdict.residual)} "
            f"| {verdict.outcome} |"
        )
    lines += ["", f"Fixed sentence: {sentence(outcomes)}."]
    if results["stage"] != "final":
        lines.append("Development data: this places the candidate; it is not the claim.")
    return "\n".join(lines) + "\n"


def _interval(difference: Mapping[str, float]) -> str:
    return f"{difference['delta']:+.3f} [{difference['low']:+.3f}, {difference['high']:+.3f}]"
