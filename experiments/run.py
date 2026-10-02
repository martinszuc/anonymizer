"""Running every system on every configured split and writing the results.

A run writes `<name>.json` (every score, with the commit, machine, model and
dataset versions, seed), `<name>.md` and `<name>.tex` into its output
directory. Nothing in them comes from corpus text: documents are named by
position, and only counts and scores are kept, so CNEC and UNER, which name
real people, cannot leak through a results file.
"""

from __future__ import annotations

import datetime
import platform
import subprocess
import time
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import anonymizer.core
from anonymizer.core.detect.gliner import SpanModel
from anonymizer.core.resources import load_catalog
from anonymizer.core.types import EntityType

from experiments.config import RunConfig
from experiments.datasets import Corpus, load_corpus
from experiments.metrics import (
    MATCHES,
    METRICS,
    Counts,
    document_counts,
    interval,
    paired_difference,
    resampled_totals,
    resamples,
    total,
)
from experiments.systems import (
    CACHE_FLOOR,
    CachedSpanModel,
    PredictionCache,
    SystemConfig,
    cache_path,
    detect,
    gliner_loader,
    model_versions,
)

RESULTS_SCHEMA = 1

Progress = Callable[[str], None]


def run(
    config: RunConfig,
    *,
    resource_root: Path,
    cache_dir: Path,
    load_model: Callable[[], SpanModel] | None = None,
    progress: Progress = lambda _: None,
) -> dict[str, Any]:
    """Run the configured systems on the configured splits and score them.

    Args:
        config: The run configuration.
        resource_root: Storage root holding `data/` and `models/`.
        cache_dir: Where the name model's output is cached.
        load_model: Returns the name model; the catalog's GLiNER by default.
        progress: Told what is running (no corpus text).

    Returns:
        The results, as `write_results` stores them.
    """
    load_model = _once(load_model or gliner_loader(resource_root))
    corpora: dict[str, Any] = {}
    for reference in config.datasets:
        corpus = load_corpus(reference.id, reference.split, resource_root, reference.text)
        progress(f"{corpus.key}: {len(corpus.documents)} documents")
        corpora[corpus.key] = _run_corpus(config, corpus, cache_dir, load_model, progress)
    return {
        "schema": RESULTS_SCHEMA,
        "name": config.name,
        "description": config.description,
        "stage": config.stage,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git": git_state(),
        "machine": machine(),
        "seed": config.seed,
        "resamples": config.resamples,
        "cache_floor": CACHE_FLOOR,
        "models": model_versions(config.systems),
        "datasets": {
            reference.id: load_catalog()[reference.id].version for reference in config.datasets
        },
        "systems": {system.name: system.describe() for system in config.systems},
        "config": config.raw,
        "corpora": corpora,
    }


def _once(load_model: Callable[[], SpanModel]) -> Callable[[], SpanModel]:
    """Load the model on first use only, however many corpora ask for it."""
    loaded: list[SpanModel] = []

    def load() -> SpanModel:
        if not loaded:
            loaded.append(load_model())
        return loaded[0]

    return load


def _run_corpus(
    config: RunConfig,
    corpus: Corpus,
    cache_dir: Path,
    load_model: Callable[[], SpanModel],
    progress: Progress,
) -> dict[str, Any]:
    types = corpus.types if config.types is None else corpus.types & config.types
    model: CachedSpanModel | None = None
    if any(system.model != "none" for system in config.systems):
        cache = PredictionCache(cache_path(cache_dir, corpus.dataset, corpus.version, corpus.split))
        model = CachedSpanModel(load_model, cache)
    draws = resamples(len(corpus.documents), config.resamples, config.seed)

    per_system: dict[str, dict[tuple[str, str], list[Counts]]] = {}
    systems: dict[str, Any] = {}
    for system in config.systems:
        started = time.perf_counter()
        hits, misses = (model.hits, model.misses) if model else (0, 0)
        counts, details = _run_system(system, corpus, types, model)
        if model is not None:
            model.cache.save()
        per_system[system.name] = counts
        details["seconds"] = round(time.perf_counter() - started, 2)
        if model is not None and system.model != "none":
            details["cache"] = {"hits": model.hits - hits, "misses": model.misses - misses}
        details["scores"] = _scores(counts, draws)
        systems[system.name] = details
        progress(f"{corpus.key}: {system.name} done in {details['seconds']} s")

    return {
        "dataset": corpus.dataset,
        "version": corpus.version,
        "split": corpus.split,
        "role": str(corpus.role),
        "language": corpus.language,
        "text": str(corpus.text_form),
        "documents": len(corpus.documents),
        "pages": sum(len(gold.document.pages) for gold in corpus.documents),
        "sentences": corpus.sentences,
        "scored_types": sorted(str(kind) for kind in types),
        "gold": {
            kind: count
            for kind, count in corpus.gold_counts().items()
            if kind in {str(item) for item in types}
        },
        "unmapped": dict(corpus.unmapped.most_common()),
        "skipped": corpus.skipped,
        "systems": systems,
        "comparisons": [
            _compare(baseline, candidate, per_system, draws)
            for baseline, candidate in config.compare
        ],
    }


def _run_system(
    system: SystemConfig,
    corpus: Corpus,
    types: frozenset[EntityType],
    model: CachedSpanModel | None,
) -> tuple[dict[tuple[str, str], list[Counts]], dict[str, Any]]:
    counts: dict[tuple[str, str], list[Counts]] = {}
    unscored: Counter[str] = Counter()
    languages: Counter[str] = Counter()
    for gold in corpus.documents:
        detect(system, gold.document, corpus.language, model)
        found = gold.document.entities
        for key, value in document_counts(found, gold.gold, types).items():
            counts.setdefault(key, []).append(value)
        unscored.update(str(entity.type) for entity in found if entity.type not in types)
        languages[gold.document.language or "none"] += 1
        gold.document.entities = []
    details: dict[str, Any] = {
        "languages": dict(languages.most_common()),
        "unscored_predictions": dict(unscored.most_common()),
    }
    return counts, details


def _scores(
    counts: dict[tuple[str, str], list[Counts]], draws: Sequence[Sequence[int]]
) -> dict[str, dict[str, Any]]:
    scores: dict[str, dict[str, Any]] = {mode: {} for mode in MATCHES}
    for (mode, kind), per_document in counts.items():
        resampled = resampled_totals(per_document, draws)
        summed = total(per_document)
        scores[mode][kind] = {
            "counts": {
                "predicted": summed.predicted,
                "predicted_matched": summed.predicted_matched,
                "gold": summed.gold,
                "gold_matched": summed.gold_matched,
            },
            **{metric: interval(per_document, resampled, metric).to_dict() for metric in METRICS},
        }
    return scores


def _compare(
    baseline: str,
    candidate: str,
    per_system: dict[str, dict[tuple[str, str], list[Counts]]],
    draws: Sequence[Sequence[int]],
) -> dict[str, Any]:
    differences: dict[str, dict[str, Any]] = {mode: {} for mode in MATCHES}
    for key, before in per_system[baseline].items():
        after = per_system[candidate][key]
        paired_before = (before, resampled_totals(before, draws))
        paired_after = (after, resampled_totals(after, draws))
        mode, kind = key
        differences[mode][kind] = {
            metric: paired_difference(paired_before, paired_after, metric).to_dict()
            for metric in METRICS
        }
    return {"baseline": baseline, "candidate": candidate, "differences": differences}


def machine() -> dict[str, str]:
    """Describe the machine a run is made on."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": platform.python_version(),
    }


def git_state() -> dict[str, Any]:
    """Return the commit the run is made from and whether the tree had changes."""
    here = Path(__file__).parent
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=here
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            check=True,
            cwd=here,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}
    return {"commit": commit, "dirty": bool(status.strip())}
