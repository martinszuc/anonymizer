"""Running the pipeline over every benchmark document and recording the results.

A run writes, under its output directory:

    results.json            every score, with tool/model versions and machine
    results.md              the same as tables
    pdf/<doc>.pdf           the generated originals
    pdf/<doc>.<system>.pdf  the redacted outputs
    images/<doc>.*.png      original, detections, redacted, collage per system

Everything in it is synthetic and safe to publish.
"""

from __future__ import annotations

import datetime
import json
import platform
import subprocess
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import anonymizer.core
from anonymizer.core.detect import Detector, load_gliner_detector
from anonymizer.core.detect.gliner import GLINER_RESOURCE
from anonymizer.core.ingest import load_document
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import find_leaks, redact_pdf
from anonymizer.core.resources import load_catalog
from anonymizer.core.types import Entity

from benchmark import images
from benchmark.render import render
from benchmark.score import (
    DocumentResult,
    ItemResult,
    decoys_removed,
    false_positives,
    outcome_counts,
    residue,
    score_detection,
)
from benchmark.spec import DocumentSpec, load_documents, spec_summary

RESULTS_SCHEMA = 1
SYSTEMS = ("rules", "rules+gliner")

DetectorFactory = Callable[[str], Detector]


def run(
    output: Path,
    *,
    systems: tuple[str, ...] = SYSTEMS,
    resource_root: Path = Path(),
    specs: list[DocumentSpec] | None = None,
) -> dict[str, Any]:
    """Run every system over every document and write the results.

    Args:
        output: Directory for results, PDFs and images.
        systems: Detector systems to run (`rules`, `rules+gliner`).
        resource_root: Storage root holding `models/`, for GLiNER.
        specs: Documents to run; every file in `benchmark/documents` by default.

    Returns:
        The results, as written to `results.json`.
    """
    specs = specs if specs is not None else load_documents()
    factories = detector_factories(systems, resource_root)
    (output / "pdf").mkdir(parents=True, exist_ok=True)
    (output / "images").mkdir(parents=True, exist_ok=True)

    documents: dict[str, Any] = {}
    for spec in specs:
        documents[spec.name] = {
            "summary": spec_summary(spec),
            "systems": {
                system: _run_one(spec, system, factory, output).to_dict()
                for system, factory in factories.items()
            },
        }
    results = {
        "schema": RESULTS_SCHEMA,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git_commit": git_commit(),
        "models": _model_versions(systems),
        "machine": machine(),
        "systems": list(factories),
        "documents": documents,
        "totals": _totals(documents, list(factories)),
    }
    (output / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return results


def _run_one(
    spec: DocumentSpec, system: str, factory: DetectorFactory, output: Path
) -> DocumentResult:
    source = output / "pdf" / f"{spec.name}.pdf"
    if not source.exists():
        render(spec, source)
    redacted_path = output / "pdf" / f"{spec.name}.{system}.pdf"

    started = time.perf_counter()
    document = load_document(source, language=spec.language)
    run_detection(document, factory(spec.language))
    redact_pdf(source, document, redacted_path)
    seconds = time.perf_counter() - started

    leak_check_passed = not find_leaks(redacted_path, document)
    redacted = load_document(redacted_path, language=spec.language)
    detection = score_detection(spec, document)
    after = residue(spec, document, redacted)
    items = tuple(
        ItemResult(
            type=str(item.type),
            carrier=item.carrier,
            outcome=outcome,
            type_correct=type_correct,
            readable_after=readable,
            fragments_after=tuple(fragments),
        )
        for item, (outcome, type_correct), (readable, fragments) in zip(
            spec.gold, detection, after, strict=True
        )
    )
    _draw(spec, system, document.entities, source, redacted_path, output)
    return DocumentResult(
        items=items,
        false_positives=tuple(false_positives(spec, document)),
        decoys_removed=tuple(decoys_removed(spec, redacted)),
        leak_check_passed=leak_check_passed,
        seconds=seconds,
    )


def _draw(
    spec: DocumentSpec,
    system: str,
    entities: list[Entity],
    source: Path,
    redacted: Path,
    output: Path,
) -> None:
    folder = output / "images"
    clip = images.content_clip(source)
    original = images.page_image(source, clip, folder / f"{spec.name}.original.png")
    detected = images.detection_image(
        source, entities, clip, folder / f"{spec.name}.{system}.detected.png"
    )
    cleaned = images.page_image(redacted, clip, folder / f"{spec.name}.{system}.redacted.png")
    images.collage(
        [("Original", original), (f"Detected ({system})", detected), ("Redacted", cleaned)],
        folder / f"{spec.name}.{system}.collage.png",
    )


def detector_factories(systems: tuple[str, ...], resource_root: Path) -> dict[str, DetectorFactory]:
    """Return a detector factory per system name, loading GLiNER once if needed.

    Raises:
        ValueError: If a system name is unknown.
    """
    unknown = set(systems) - set(SYSTEMS)
    if unknown:
        msg = f"unknown systems {sorted(unknown)}; choose from {list(SYSTEMS)}"
        raise ValueError(msg)
    factories: dict[str, DetectorFactory] = {}
    if "rules" in systems:
        factories["rules"] = build_detector
    if "rules+gliner" in systems:
        # Load once; the model takes seconds to read.
        model = load_gliner_detector(resource_root)
        factories["rules+gliner"] = lambda language: build_detector(language, model=model)
    return factories


def _totals(documents: dict[str, Any], systems: list[str]) -> dict[str, Any]:
    totals: dict[str, Any] = {}
    for system in systems:
        results = [document["systems"][system] for document in documents.values()]
        items = [ItemResult(**item) for result in results for item in result["items"]]
        by_type: dict[str, dict[str, int]] = {}
        for kind in sorted({item.type for item in items}):
            by_type[kind] = outcome_counts([item for item in items if item.type == kind])
        totals[system] = {
            "counts": outcome_counts(items),
            "by_type": by_type,
            "false_positives": sum(len(result["false_positives"]) for result in results),
            "decoys_removed": sum(len(result["decoys_removed"]) for result in results),
            "safe_documents": sum(result["safe"] for result in results),
            "leak_check_passed": sum(result["leak_check_passed"] for result in results),
            "documents": len(results),
            "seconds": round(sum(result["seconds"] for result in results), 3),
        }
    return totals


def _model_versions(systems: tuple[str, ...]) -> dict[str, str]:
    if "rules+gliner" not in systems:
        return {}
    catalog = load_catalog()
    return {
        resource.id: resource.version for resource in catalog.with_requirements(GLINER_RESOURCE)
    }


def machine() -> dict[str, str]:
    """Describe the machine a run is made on."""
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": platform.python_version(),
    }


def git_commit() -> str | None:
    """Return the commit the benchmark runs from, or `None` outside a checkout."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip()
