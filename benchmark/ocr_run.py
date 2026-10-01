"""The scanned benchmark: OCR engines across degradation levels (RQ2).

For every document, level and engine, a run writes under its output directory:

    ocr-results.json                         every score, versions and machine
    ocr-results.md                           the same as tables
    pdf/<doc>.pdf                            the born-digital original
    scans/<doc>.<level>.pdf                  its degraded, picture-only scan
    scans/<doc>.<level>.<engine>.pdf         the redacted scan

Only items on the page are scored: a scan carries no links or metadata. The
`oracle` engine reads the ground truth and bounds what OCR can give the rest
of the pipeline. `onnxtr` is the first real engine (models from the catalog,
`uv sync --group ocr-onnxtr`).
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

import anonymizer.core
from anonymizer.core.ingest import (
    OCR_ENGINE_RESOURCES,
    OCR_ENGINES,
    OcrEngine,
    load_document,
    load_ocr_engine,
)
from anonymizer.core.pipeline import run_detection
from anonymizer.core.redact import find_leaks, redact_pdf
from anonymizer.core.resources import load_catalog

from benchmark.degrade import LEVELS, Level
from benchmark.ocr_score import box_scores, item_residue, residue_counts, text_errors
from benchmark.render import render
from benchmark.run import DetectorFactory, detector_factories, git_commit, machine
from benchmark.scans import OracleEngine, TruthPage, scan_document
from benchmark.score import score_detection
from benchmark.spec import DocumentSpec, load_documents

OCR_RESULTS_SCHEMA = 1

EngineFactory = Callable[[list[TruthPage]], OcrEngine]
"""Gives the engine for one scan, from its ground truth if the engine needs it."""


def _oracle(resource_root: Path) -> EngineFactory:
    del resource_root
    return OracleEngine


def _loaded(name: str) -> Callable[[Path], EngineFactory]:
    def load(resource_root: Path) -> EngineFactory:
        engine = load_ocr_engine(name, resource_root)
        return lambda _truth: engine

    return load


ENGINES: dict[str, Callable[[Path], EngineFactory]] = {"oracle": _oracle} | {
    name: _loaded(name) for name in OCR_ENGINES
}
"""Engines by name; each is loaded once per run, from the models under a storage root."""


def run_ocr(
    output: Path,
    *,
    engines: tuple[str, ...] = ("oracle",),
    levels: tuple[Level, ...] = LEVELS,
    system: str = "rules",
    resource_root: Path = Path(),
    specs: list[DocumentSpec] | None = None,
) -> dict[str, Any]:
    """Score every engine on every document at every degradation level.

    Args:
        output: Directory for results and PDFs.
        engines: Names from `ENGINES`.
        levels: Degradation levels to scan at.
        system: Detector system, as in the born-digital benchmark (`SYSTEMS`).
        resource_root: Storage root holding `models/`, for GLiNER and OCR engines.
        specs: Documents; every file in `benchmark/documents` by default.

    Returns:
        The results, as written to `ocr-results.json`.

    Raises:
        ValueError: If an engine name is unknown.
    """
    unknown = set(engines) - set(ENGINES)
    if unknown:
        msg = f"unknown engines {sorted(unknown)}; choose from {list(ENGINES)}"
        raise ValueError(msg)
    factories = {engine: ENGINES[engine](resource_root) for engine in engines}
    specs = specs if specs is not None else load_documents()
    detector_for = detector_factories((system,), resource_root)[system]
    runs: dict[str, dict[str, Any]] = {engine: {} for engine in engines}
    for level in levels:
        for engine in engines:
            documents = {
                spec.name: _run_one(spec, level, engine, factories[engine], detector_for, output)
                for spec in specs
            }
            runs[engine][level.name] = {"documents": documents, "totals": _totals(documents)}
    results = {
        "schema": OCR_RESULTS_SCHEMA,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git_commit": git_commit(),
        "machine": machine(),
        "engines": list(engines),
        "models": _model_versions(engines),
        "system": system,
        "levels": [dataclasses.asdict(level) | {"name": level.name} for level in levels],
        "runs": runs,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "ocr-results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return results


def _run_one(
    spec: DocumentSpec,
    level: Level,
    engine_name: str,
    engine_for: EngineFactory,
    detector_for: DetectorFactory,
    output: Path,
) -> dict[str, Any]:
    original = output / "pdf" / f"{spec.name}.pdf"
    if not original.exists():
        render(spec, original)
    scan = output / "scans" / f"{spec.name}.{level.name}.pdf"
    truth = scan_document(original, level, scan)
    engine = engine_for(truth)

    started = time.perf_counter()
    document = load_document(scan, language=spec.language, ocr=engine)
    seconds = time.perf_counter() - started
    run_detection(document, detector_for(spec.language))
    on_page = dataclasses.replace(
        spec, gold=tuple(item for item in spec.gold if item.carrier == "page")
    )
    detection = score_detection(on_page, document)

    redacted = output / "scans" / f"{spec.name}.{level.name}.{engine_name}.pdf"
    redact_pdf(scan, document, redacted)
    leak_check_passed = not find_leaks(redacted, document, ocr=engine)
    shares = item_residue(scan, redacted, truth, on_page.gold)
    residue = residue_counts(shares)
    found = Counter(outcome for outcome, _ in detection)
    return {
        "pages": len(truth),
        "seconds": round(seconds, 3),
        "text": text_errors(truth, document.pages),
        "boxes": box_scores(truth, document.pages),
        "items": {
            "gold": len(on_page.gold),
            "found": found["found"],
            "partial": found["partial"],
            "missed": found["missed"],
        }
        | residue,
        "safe": residue["readable_after"] + residue["partly_after"] == 0,
        "leak_check_passed": leak_check_passed,
    }


def _model_versions(engines: tuple[str, ...]) -> dict[str, str]:
    catalog = load_catalog()
    return {
        resource_id: catalog[resource_id].version
        for engine in engines
        for resource_id in OCR_ENGINE_RESOURCES.get(engine, ())
    }


def _totals(documents: dict[str, Any]) -> dict[str, Any]:
    results = list(documents.values())
    text: Counter[str] = Counter()
    items: Counter[str] = Counter()
    boxes: Counter[str] = Counter()
    for result in results:
        text.update(result["text"])
        items.update(result["items"])
        boxes.update(result["boxes"])
    pages = sum(result["pages"] for result in results)
    return {
        "character_error_rate": _rate(text["character_errors"], text["characters"]),
        "diacritic_error_rate": _rate(text["diacritic_errors"], text["diacritics"]),
        "boxed": _rate(boxes["boxed"], boxes["words"]),
        "coverage": _rate(boxes["coverage"], boxes["words"]),
        "items": dict(items),
        "safe_documents": sum(result["safe"] for result in results),
        "leak_check_passed": sum(result["leak_check_passed"] for result in results),
        "documents": len(results),
        "seconds_per_page": _rate(sum(result["seconds"] for result in results), pages),
    }


def _rate(part: float, whole: float) -> float | None:
    return round(part / whole, 4) if whole else None


def ocr_markdown(results: dict[str, Any]) -> str:
    """Render a scanned-benchmark run as Markdown, one table per engine."""
    machine = results["machine"]
    lines = [
        f"# Scanned benchmark: anonymizer {results['tool_version']}",
        "",
        f"Run {results['created']} on {machine['system']} {machine['machine']}, "
        f"Python {machine['python']}"
        + (f", commit `{results['git_commit'][:7]}`" if results.get("git_commit") else "")
        + f". Detection: `{results['system']}`.",
    ]
    header = [
        "level",
        "CER",
        "diacritics",
        "boxed",
        "coverage",
        "found",
        "readable after",
        "partly after",
        "safe",
        "leak check passed",
        "s/page",
    ]
    for engine in results["engines"]:
        lines += ["", f"## {engine}", "", _row(header), _row(["---"] * len(header))]
        for level, run in results["runs"][engine].items():
            total = run["totals"]
            items = total["items"]
            lines.append(
                _row(
                    [
                        level,
                        _percent(total["character_error_rate"]),
                        _percent(total["diacritic_error_rate"]),
                        _percent(total["boxed"]),
                        _percent(total["coverage"]),
                        f"{items['found']}/{items['gold']}",
                        str(items["readable_after"]),
                        str(items["partly_after"]),
                        f"{total['safe_documents']}/{total['documents']}",
                        f"{total['leak_check_passed']}/{total['documents']}",
                        f"{total['seconds_per_page']:.2f}",
                    ]
                )
            )
    return "\n".join(lines) + "\n"


def _row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _percent(rate: float | None) -> str:
    return "n/a" if rate is None else f"{rate:.1%}"
