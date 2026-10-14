"""Charts of how the results change across runs, for presentations.

Reads any number of `results.json` files (one per release, typically) and
draws PNG charts:

    found-over-versions.png   share of planted items found, per system
    safe-over-versions.png    documents with nothing readable left, per system
    found-by-type.png         share found per item type, latest run

A score moves when the code changes or when the documents do, so a line joins
only runs on one document set: the same files (`document_set` in the results)
read as the same number of planted items (an older harness skips carriers it
does not know). The set of the newest run is drawn solid, earlier sets dashed
and labelled with their size. Results from before the fingerprint was recorded
are told apart by their document names. `benchmark backfill` measures earlier
releases on the current files, which gives one line over the versions that
read them whole.

Colours are the first two slots of a validated categorical palette (checked
for colour-vision deficiency and contrast); each series is also labelled
directly, so identity never rests on colour alone. Requires the `benchmark`
dependency group (matplotlib).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
SERIES_COLOURS = {"rules": "#2a78d6", "rules+gliner": "#eb6834"}
TITLE_PAD = 30
SERIES_LABELS = {"rules": "Rules only", "rules+gliner": "Rules + GLiNER"}


@dataclass
class DocumentSet:
    """Runs made on one set of benchmark documents.

    Attributes:
        fingerprint: The set's fingerprint, `None` while only runs from before
            it was recorded belong to the set.
        names: The documents' names.
        items: The planted items the runs read from them.
        runs: Indexes into the runs, oldest first.
    """

    fingerprint: str | None
    names: frozenset[str]
    items: int
    runs: list[int] = field(default_factory=list)

    @property
    def label(self) -> str:
        """Describe the set by its size."""
        return f"{len(self.names)} documents, {self.items} items"

    def admits(self, run: dict[str, Any]) -> bool:
        """Whether a run was made on this set.

        Two fingerprints decide which files were read, and without one the
        document names do; the planted items must match either way.
        """
        if planted_items(run) != self.items:
            return False
        fingerprint = run_fingerprint(run)
        if fingerprint is not None and self.fingerprint is not None:
            return fingerprint == self.fingerprint
        return frozenset(run["documents"]) == self.names


def run_fingerprint(run: dict[str, Any]) -> str | None:
    """Return a run's document set fingerprint, or `None` for older results."""
    return (run.get("document_set") or {}).get("fingerprint")


def planted_items(run: dict[str, Any]) -> int:
    """Return how many planted items a run scored (the same for every system)."""
    return next(iter(run["totals"].values()))["counts"]["gold"]


def document_sets(runs: list[dict[str, Any]]) -> list[DocumentSet]:
    """Group runs by the document set they were made on, in order of first run.

    A run fitting several sets (one without a fingerprint, after a set's files
    changed but not their names) joins the one used most recently.
    """
    sets: list[DocumentSet] = []
    for index, run in enumerate(runs):
        fitting = [candidate for candidate in sets if candidate.admits(run)]
        if fitting:
            chosen = max(fitting, key=lambda candidate: candidate.runs[-1])
        else:
            chosen = DocumentSet(
                run_fingerprint(run), frozenset(run["documents"]), planted_items(run)
            )
            sets.append(chosen)
        chosen.fingerprint = chosen.fingerprint or run_fingerprint(run)
        chosen.runs.append(index)
    return sets


def code_states(runs: list[dict[str, Any]]) -> list[tuple[str, str | None]]:
    """Return the distinct (version, commit) pairs of the runs, in run order.

    A release measured twice, once on its own documents and once on the
    current set (a backfill), is one place on the version axis.
    """
    return list(dict.fromkeys(_code_state(run) for run in runs))


def _code_state(run: dict[str, Any]) -> tuple[str, str | None]:
    return run["tool_version"], run.get("git_commit")


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

    states = code_states(runs)
    sets = document_sets(runs)
    current = next(document_set for document_set in sets if len(runs) - 1 in document_set.runs)
    figure, axes = _figure(title)
    systems = [system for system in SERIES_COLOURS if any(system in run["totals"] for run in runs)]
    for system in systems:
        for document_set in sets:
            # One point per place on the axis; the newer run of a release
            # measured twice on one set wins.
            points = {
                states.index(_code_state(runs[index])): measure(runs[index]["totals"][system])
                for index in document_set.runs
                if system in runs[index]["totals"]
            }
            if not points:
                continue
            xs = sorted(points)
            ys = [points[x] * 100 if percent else points[x] for x in xs]
            label = SERIES_LABELS[system]
            if len(sets) > 1:
                label += f", {document_set.label}"
            solid = document_set is current
            colour = SERIES_COLOURS[system]
            axes.plot(
                xs,
                ys,
                color=colour,
                linewidth=2,
                linestyle="-" if solid else "--",
                alpha=1 if solid else 0.6,
                marker="o",
                markersize=8,
                markerfacecolor=colour if solid else SURFACE,
                markeredgecolor=SURFACE if solid else colour,
                markeredgewidth=2,
                label=label,
            )
            if not solid:
                continue
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
    axes.set_xticks(range(len(states)), _state_labels(states))
    axes.set_xlim(-0.5, len(states) - 0.5 + 1.2)
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
        axes.set_ylabel(
            "documents" if len(sets) > 1 else f"documents (of {documents})",
            color=TEXT_SECONDARY,
        )
    axes.set_xlabel("version", color=TEXT_SECONDARY)
    axes.grid(axis="x", visible=False)
    legend = axes.legend(
        frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncols=2, labelcolor=TEXT
    )
    # Each legend row beyond the first pushes the title up by one line.
    rows = -(-len(legend.get_texts()) // 2)
    axes.set_title(title, loc="left", color=TEXT, fontsize=14, pad=TITLE_PAD + 22 * (rows - 1))
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
    axes.set_title(title, loc="left", color=TEXT, fontsize=14, pad=TITLE_PAD)
    for side in ("top", "right"):
        axes.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axes.spines[side].set_color(GRID)
    axes.tick_params(colors=TEXT_SECONDARY)
    axes.grid(color=GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    return figure, axes


def _state_labels(states: list[tuple[str, str | None]]) -> list[str]:
    versions = [version for version, _ in states]
    # Two commits of one version (a manual run between releases) get the commit.
    return [
        f"{version}\n{(commit or '')[:7]}" if versions.count(version) > 1 else version
        for version, commit in states
    ]


def _version_key(version: str) -> tuple[int, ...]:
    parts = []
    for part in version.split("."):
        digits = "".join(character for character in part if character.isdigit())
        parts.append(int(digits or 0))
    return tuple(parts)
