"""Charts of how the results change across runs, for presentations.

Reads any number of `results.json` files (one per release, typically) and
draws PNG charts:

    found-over-versions.png   share of planted items found, per system
    safe-over-versions.png    documents with nothing readable left, per system
    found-by-type.png         share found per item type, latest run

Colours are the first two slots of a validated categorical palette (checked
for colour-vision deficiency and contrast); each series is also labelled
directly, so identity never rests on colour alone. Requires the `benchmark`
dependency group (matplotlib).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
SERIES_COLOURS = {"rules": "#2a78d6", "rules+gliner": "#eb6834"}
SERIES_LABELS = {"rules": "Rules only", "rules+gliner": "Rules + GLiNER"}


def load_runs(paths: list[Path]) -> list[dict[str, Any]]:
    """Load results files, oldest version first."""
    runs = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    return sorted(runs, key=lambda run: (_version_key(run["tool_version"]), run["created"]))


def draw(paths: list[Path], output: Path) -> list[Path]:
    """Draw every chart from the given results files.

    Returns:
        The PNG files written.
    """
    import matplotlib as mpl  # pyright: ignore[reportMissingImports]

    mpl.use("Agg")
    runs = load_runs(paths)
    output.mkdir(parents=True, exist_ok=True)
    return [
        _over_versions(
            runs,
            lambda total: total["counts"]["found"] / total["counts"]["gold"],
            "Planted personal items found",
            output / "found-over-versions.png",
            percent=True,
        ),
        _over_versions(
            runs,
            lambda total: total["safe_documents"],
            "Documents with nothing readable left",
            output / "safe-over-versions.png",
            percent=False,
        ),
        _by_type(runs[-1], output / "found-by-type.png"),
    ]


def _over_versions(
    runs: list[dict[str, Any]],
    measure: Any,
    title: str,
    destination: Path,
    *,
    percent: bool,
) -> Path:
    import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]

    labels = _run_labels(runs)
    figure, axes = _figure(title)
    systems = [system for system in SERIES_COLOURS if any(system in run["totals"] for run in runs)]
    for system in systems:
        points = [
            (index, measure(run["totals"][system]))
            for index, run in enumerate(runs)
            if system in run["totals"]
        ]
        xs = [x for x, _ in points]
        ys = [y * 100 if percent else y for _, y in points]
        colour = SERIES_COLOURS[system]
        axes.plot(
            xs,
            ys,
            color=colour,
            linewidth=2,
            marker="o",
            markersize=8,
            markeredgecolor=SURFACE,
            markeredgewidth=2,
            label=SERIES_LABELS[system],
        )
        last = f"{ys[-1]:.0f} %" if percent else f"{ys[-1]:.0f}"
        axes.annotate(
            f"{SERIES_LABELS[system]}  {last}",
            (xs[-1], ys[-1]),
            xytext=(10, 0),
            textcoords="offset points",
            va="center",
            color=TEXT,
            fontsize=11,
        )
    axes.set_xticks(range(len(runs)), labels)
    axes.set_xlim(-0.5, len(runs) - 0.5 + 1.2)
    if percent:
        axes.set_ylim(0, 105)
        axes.set_ylabel("% of planted items", color=TEXT_SECONDARY)
    else:
        documents = max(
            run["totals"][system]["documents"]
            for run in runs
            for system in systems
            if system in run["totals"]
        )
        axes.set_ylim(0, documents + 0.5)
        axes.set_ylabel(f"documents (of {documents})", color=TEXT_SECONDARY)
    axes.set_xlabel("version", color=TEXT_SECONDARY)
    axes.grid(axis="x", visible=False)
    axes.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncols=2, labelcolor=TEXT)
    figure.savefig(destination, dpi=200, facecolor=SURFACE)
    plt.close(figure)
    return destination


def _by_type(run: dict[str, Any], destination: Path) -> Path:
    import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]

    systems = [system for system in SERIES_COLOURS if system in run["totals"]]
    kinds = sorted({kind for system in systems for kind in run["totals"][system]["by_type"]})
    figure, axes = _figure(
        f"Found per type, version {run['tool_version']}", height=0.55 * len(kinds) + 1.6
    )
    bar = 0.36
    for offset, system in enumerate(systems):
        by_type = run["totals"][system]["by_type"]
        ys = [
            index + (offset - (len(systems) - 1) / 2) * (bar + 0.04) for index in range(len(kinds))
        ]
        shares = [
            100 * by_type[kind]["found"] / by_type[kind]["gold"] if kind in by_type else 0.0
            for kind in kinds
        ]
        axes.barh(
            ys,
            shares,
            height=bar,
            color=SERIES_COLOURS[system],
            edgecolor=SURFACE,
            linewidth=2,
            label=SERIES_LABELS[system],
        )
        # Label only the bars short of 100 %: those are the story, and a
        # zero-length bar is otherwise indistinguishable from a missing one.
        for y, share, kind in zip(ys, shares, kinds, strict=True):
            counts = by_type.get(kind)
            if counts is None or share >= 100:
                continue
            note = f"{counts['found']}/{counts['gold']}"
            if counts["partial"]:
                note += f", {counts['partial']} partial"
            axes.annotate(
                note,
                (share, y),
                xytext=(6, 0),
                textcoords="offset points",
                va="center",
                fontsize=10,
                color=TEXT_SECONDARY,
            )
    axes.set_yticks(range(len(kinds)), [kind.replace("_", " ") for kind in kinds])
    axes.invert_yaxis()
    axes.set_xlim(0, 100)
    axes.set_xlabel("% of planted items found", color=TEXT_SECONDARY)
    axes.grid(axis="y", visible=False)
    axes.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncols=2, labelcolor=TEXT)
    figure.savefig(destination, dpi=200, facecolor=SURFACE)
    plt.close(figure)
    return destination


def _figure(title: str, height: float = 4.2) -> tuple[Any, Any]:
    import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]

    figure, axes = plt.subplots(figsize=(9, height), layout="constrained")
    figure.patch.set_facecolor(SURFACE)
    axes.set_facecolor(SURFACE)
    axes.set_title(title, loc="left", color=TEXT, fontsize=14, pad=30)
    for side in ("top", "right"):
        axes.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axes.spines[side].set_color(GRID)
    axes.tick_params(colors=TEXT_SECONDARY)
    axes.grid(color=GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    return figure, axes


def _run_labels(runs: list[dict[str, Any]]) -> list[str]:
    versions = [run["tool_version"] for run in runs]
    # Two runs of one version (a manual run between releases) get the commit.
    return [
        f"{version}\n{(run.get('git_commit') or '')[:7]}"
        if versions.count(version) > 1
        else version
        for version, run in zip(versions, runs, strict=True)
    ]


def _version_key(version: str) -> tuple[int, ...]:
    parts = []
    for part in version.split("."):
        digits = "".join(character for character in part if character.isdigit())
        parts.append(int(digits or 0))
    return tuple(parts)
