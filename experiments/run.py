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
from anonymizer.core.detect.nametag import SentenceSplitter
from anonymizer.core.resources import Catalog, load_catalog
from anonymizer.core.types import EntityType

from experiments.config import RunConfig
from experiments.datasets import DATASETS, Corpus, load_corpus
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
    NameModel,
    PredictionCache,
    SystemConfig,
    cache_path,
    cached_model,
    detect,
    model_loader,
    model_versions,
    splitter_loader,
)

RESULTS_SCHEMA = 1

Progress = Callable[[str], None]


def run(
    config: RunConfig,
    *,
    resource_root: Path,
    cache_dir: Path,
    load_model: Callable[[str], Any] | None = None,
    load_splitter: Callable[[str], SentenceSplitter] | None = None,
    progress: Progress = lambda _: None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Run the configured systems on the configured splits and score them.

    Args:
        config: The run configuration.
        resource_root: Storage root holding `data/` and `models/`; the models
            trained under it can be run as well.
        cache_dir: Where the name models' output is cached.
        load_model: Returns a name model by catalog id; from the catalog's
            files under `resource_root` by default.
        load_splitter: Returns a NameTag model's sentence splitter by catalog
            id; from the same files by default.
        progress: Told what is running (no corpus text).
        limit: Score only the first documents of each split, for a quick
            look; recorded in the results.

    Returns:
        The results, as the command line stores them in `<name>.json`.
    """
    catalog = load_catalog(root=resource_root)
    load_model = _once(load_model or model_loader(resource_root, catalog))
    load_splitter = _once(load_splitter or splitter_loader(resource_root, catalog))
    corpora: dict[str, Any] = {}
    for reference in config.datasets:
        corpus = load_corpus(reference.id, reference.split, resource_root, reference.text, limit)
        progress(f"{corpus.key}: {len(corpus.documents)} documents")
        corpora[corpus.key] = _run_corpus(
            config, corpus, cache_dir, load_model, load_splitter, catalog, progress
        )
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
        "models": model_versions(config.systems, catalog),
        "datasets": {
            reference.id: load_catalog()[DATASETS[reference.id].catalog_id].version
            for reference in config.datasets
        },
        "systems": {system.name: system.describe() for system in config.systems},
        "config": config.raw,
        **({"limit": limit} if limit is not None else {}),
        "corpora": corpora,
    }


def _once[Loaded](load_model: Callable[[str], Loaded]) -> Callable[[str], Loaded]:
    """Load each model on first use only, however many corpora ask for it."""
    loaded: dict[str, Loaded] = {}

    def load(model_id: str) -> Loaded:
        if model_id not in loaded:
            loaded[model_id] = load_model(model_id)
        return loaded[model_id]

    return load


def _run_corpus(
    config: RunConfig,
    corpus: Corpus,
    cache_dir: Path,
    load_model: Callable[[str], Any],
    load_splitter: Callable[[str], SentenceSplitter],
    catalog: Catalog,
    progress: Progress,
) -> dict[str, Any]:
    types = corpus.types if config.types is None else corpus.types & config.types
    models: dict[str, NameModel] = {
        model_id: cached_model(
            model_id,
            PredictionCache(
                cache_path(
                    cache_dir, model_id, corpus.dataset, corpus.version, corpus.split, catalog
                )
            ),
            load_model,
            load_splitter,
            catalog,
        )
        for model_id in dict.fromkeys(
            model_id for system in config.systems for model_id in system.model_ids
        )
    }
    draws = resamples(len(corpus.documents), config.resamples, config.seed)

    per_system: dict[str, dict[tuple[str, str], list[Counts]]] = {}
    systems: dict[str, Any] = {}
    for system in config.systems:
        started = time.perf_counter()
        used = {model_id: models[model_id] for model_id in system.model_ids}
        before = {model_id: (model.hits, model.misses) for model_id, model in used.items()}
        counts, details = _run_system(system, corpus, types, used)
        per_system[system.name] = counts
        details["seconds"] = round(time.perf_counter() - started, 2)
        for model in used.values():
            model.cache.save()
        if used:
            details["cache"] = {
                "hits": sum(model.hits - before[model_id][0] for model_id, model in used.items()),
                "misses": sum(
                    model.misses - before[model_id][1] for model_id, model in used.items()
                ),
            }
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
    models: dict[str, NameModel],
) -> tuple[dict[tuple[str, str], list[Counts]], dict[str, Any]]:
    counts: dict[tuple[str, str], list[Counts]] = {}
    unscored: Counter[str] = Counter()
    languages: Counter[str] = Counter()
    for gold in corpus.documents:
        detect(system, gold.document, corpus.language, models)
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
