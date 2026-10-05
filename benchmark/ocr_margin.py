"""How far each engine's word boxes must grow to cover their words' ink.

Ingest grows every OCR box on each side by a share of its height, the
engine's `box_margin` (see `anonymizer.core.ingest.ocr`). This measures the
share instead of guessing it. Each engine reads every scan once; its words
are then replayed through `read_page` with each candidate margin, so the
boxes are grown exactly as ingest grows them, and scored:

- **partly outside** — ground-truth words with ink outside every grown box
  (as in `ocr_score.box_scores`): what a redaction from those boxes would
  leave in the picture. The margin should bring this near zero.
- **reaching another line** — grown boxes that overlap a box, before
  growth, of a word on another of the engine's lines: a redaction from them
  would black out part of the neighbouring line. Engines whose boxes span the
  line's full height reach the next line sooner.

Command line: `uv run python -m benchmark ocr-margin --out margins/ --engines onnxtr,kraken`.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pymupdf
from anonymizer.core.ingest import DEFAULT_OCR_DPI, OcrEngine, OcrWord, PageImage, read_page
from anonymizer.core.ingest.ocr import render_page
from anonymizer.core.types import Page

from benchmark.degrade import Level
from benchmark.ocr_run import ENGINES
from benchmark.ocr_score import box_scores
from benchmark.render import render
from benchmark.scans import scan_document
from benchmark.spec import DocumentSpec, load_documents

MARGINS = (0.0, 0.05, 0.1, 0.15, 0.2, 0.3)
"""Shares of a box's height tried on each side."""


@dataclass
class _Replay:
    """Hands `read_page` words an engine read earlier, with the margin under test."""

    name: str
    box_margin: float
    words: list[OcrWord] = field(default_factory=list)

    def read(self, image: PageImage) -> list[OcrWord]:
        del image
        return self.words


def run_margins(
    output: Path,
    *,
    engines: tuple[str, ...],
    levels: tuple[Level, ...],
    margins: tuple[float, ...] = MARGINS,
    resource_root: Path = Path(),
    specs: list[DocumentSpec] | None = None,
) -> dict[str, Any]:
    """Score every engine's boxes, grown by every margin, on every document.

    Args:
        output: Directory for the scans and `ocr-margins.json`.
        engines: Names from `benchmark.ocr_run.ENGINES`.
        levels: Degradation levels to scan at.
        margins: Shares of a box's height to grow it by on each side.
        resource_root: Storage root holding `models/`.
        specs: Documents; every file in `benchmark/documents` by default.

    Returns:
        Per engine and level, per margin: `words`, `partly_outside`, `boxes`
        and `reaching_another_line`, summed over documents.
    """
    factories = {engine: ENGINES[engine](resource_root) for engine in engines}
    specs = specs if specs is not None else load_documents()
    results: dict[str, Any] = {"margins": list(margins), "runs": {}}
    for engine in engines:
        runs = results["runs"].setdefault(engine, {})
        for level in levels:
            totals: dict[float, Counter[str]] = {margin: Counter() for margin in margins}
            for spec in specs:
                original = output / "pdf" / f"{spec.name}.pdf"
                if not original.exists():
                    render(spec, original)
                scan = output / "scans" / f"{spec.name}.{level.name}.pdf"
                truth = scan_document(original, level, scan)
                read = _read_once(scan, factories[engine](truth))
                for margin in margins:
                    pages = _replayed(scan, read, engine, margin)
                    scores = box_scores(scan, truth, pages)
                    totals[margin]["words"] += scores["words"]
                    totals[margin]["partly_outside"] += scores["partly_outside"]
                    totals[margin].update(_reach(read, margin))
            runs[level.name] = {str(margin): dict(totals[margin]) for margin in margins}
    output.mkdir(parents=True, exist_ok=True)
    (output / "ocr-margins.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def _read_once(scan: Path, engine: OcrEngine) -> list[list[OcrWord]]:
    with pymupdf.open(scan) as pdf:
        return [
            engine.read(render_page(pdf.load_page(index), DEFAULT_OCR_DPI))
            for index in range(pdf.page_count)
        ]


def _replayed(scan: Path, read: list[list[OcrWord]], engine: str, margin: float) -> list[Page]:
    with pymupdf.open(scan) as pdf:
        return [
            read_page(
                pdf.load_page(index), index, _Replay(engine, margin, read[index]), DEFAULT_OCR_DPI
            )
            for index in range(pdf.page_count)
        ]


def _reach(read: Sequence[Sequence[OcrWord]], margin: float) -> Counter[str]:
    """Count boxes, and grown boxes overlapping an ungrown box on another line of their page."""
    counts: Counter[str] = Counter()
    for words in read:
        for word in words:
            counts["boxes"] += 1
            grown = _grown(word.box, margin)
            counts["reaching_another_line"] += any(
                _overlap(grown, other.box)
                for other in words
                if (other.block, other.line) != (word.block, word.line)
            )
    return counts


def _grown(box: tuple[float, float, float, float], margin: float) -> tuple[float, ...]:
    x0, y0, x1, y1 = box
    grow = margin * (y1 - y0)
    return (x0 - grow, y0 - grow, x1 + grow, y1 + grow)


def _overlap(first: Sequence[float], second: Sequence[float]) -> bool:
    return min(first[2], second[2]) > max(first[0], second[0]) and min(first[3], second[3]) > max(
        first[1], second[1]
    )


def margins_markdown(results: dict[str, Any]) -> str:
    """Render a margin run as Markdown, one table per engine and level."""
    lines = ["# OCR box margins", ""]
    for engine, runs in results["runs"].items():
        for level, by_margin in runs.items():
            lines += [
                f"## {engine}, {level}",
                "",
                "| margin | partly outside | reaching another line |",
                "|---|---|---|",
            ]
            for margin, counts in by_margin.items():
                lines.append(
                    f"| {float(margin):.0%} | {counts['partly_outside']}/{counts['words']} "
                    f"| {counts['reaching_another_line']}/{counts['boxes']} |"
                )
            lines.append("")
    return "\n".join(lines)
