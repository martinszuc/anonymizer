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
from anonymizer.core.detect import name_model
from anonymizer.core.detect.nametag import SentenceSplitter
from anonymizer.core.resources import Catalog, load_catalog
from anonymizer.core.types import EntityType

from experiments.config import RunConfig
from experiments.datasets import Corpus, dataset_version, load_corpus
from experiments.metrics import (
    COVERAGE_METRICS,
    MATCHES,
    METRICS,
    Counts,
    Coverage,
    document_counts,
    document_coverage,
    interval,
    paired_difference,
    resampled_totals,
    resamples,
    total,
)
from experiments.phenomena import PhenomenonTally
from experiments.seeds import summarize
from experiments.systems import (
    CACHE_FLOOR,
    SPAN_MODEL_ENGINE,
    NameModel,
    PredictionCache,
    SystemConfig,
    cache_path,
    cached_model,
    detect,
    model_loader,
    model_versions,
    splitter_loader,
    system_models,
)

RESULTS_SCHEMA = 1

DEVICES = ("mps", "cuda", "cpu")
"""Where torch runs a model: the Apple GPU, an NVIDIA GPU or the CPU."""

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
    device: str = "cpu",
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
        device: Where GLiNER predicts (`DEVICES`); its output is cached per
            device (`systems.cache_path`) and the results record it.

    Returns:
        The results, as the command line stores them in `<name>.json`.

    Raises:
        ValueError: If the device is unknown.
        RuntimeError: If torch cannot reach it; before any data is read.
    """
    check_device(device)
    catalog = load_catalog(root=resource_root)
    load_model = once(load_model or model_loader(resource_root, catalog, device))
    load_splitter = once(load_splitter or splitter_loader(resource_root, catalog))
    corpora: dict[str, Any] = {}
    for reference in config.datasets:
        corpus = load_corpus(reference.id, reference.split, resource_root, reference.text, limit)
        progress(f"{corpus.key}: {len(corpus.documents)} documents")
        models = corpus_models(
            config, corpus, cache_dir, load_model, load_splitter, catalog, device
        )
        corpora[corpus.key] = _run_corpus(config, corpus, models, progress)
        if config.replicates:
            corpora[corpus.key]["seeds"] = summarize(
                corpora[corpus.key], config.replicates, config.compare
            )
    return {
        "schema": RESULTS_SCHEMA,
        "name": config.name,
        "description": config.description,
        "stage": config.stage,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git": git_state(),
        "machine": machine_on(device),
        "seed": config.seed,
        "resamples": config.resamples,
        "cache_floor": CACHE_FLOOR,
        "models": model_versions(config.systems, catalog),
        "datasets": {reference.id: dataset_version(reference.id) for reference in config.datasets},
        "systems": {system.name: system.describe() for system in config.systems},
        **(
            {"replicates": {name: group.members() for name, group in config.replicates.items()}}
            if config.replicates
            else {}
        ),
        "config": config.raw,
        **({"limit": limit} if limit is not None else {}),
        "corpora": corpora,
    }


def once[Loaded](load_model: Callable[[str], Loaded]) -> Callable[[str], Loaded]:
    """Load each model on first use only, however many corpora ask for it."""
    loaded: dict[str, Loaded] = {}

    def load(model_id: str) -> Loaded:
        if model_id not in loaded:
            loaded[model_id] = load_model(model_id)
        return loaded[model_id]

    return load


def scored_types(config: RunConfig, corpus: Corpus) -> frozenset[EntityType]:
    """Return the types scored on a corpus: those it annotates, narrowed by the config."""
    return corpus.types if config.types is None else corpus.types & config.types


def corpus_models(
    config: RunConfig,
    corpus: Corpus,
    cache_dir: Path,
    load_model: Callable[[str], Any],
    load_splitter: Callable[[str], SentenceSplitter],
    catalog: Catalog,
    device: str = "cpu",
) -> dict[tuple[str, float], NameModel]:
    """Return every name model the systems use, wrapped in its cache for this corpus.

    The cache file is chosen by model and dataset version, split and, for
    GLiNER, cache floor and the device it runs on (`systems.cache_path`;
    `load_model` must load it there), and its entries by the model
    input, so every command reading the same corpus the same way answers
    from one cache. Models are keyed by catalog id and the cache floor each
    system reads them at (`SystemConfig.cache_floor_of`, from the threshold
    the model runs at in that system, its catalog entry's when the system
    sets none); NameTag has no floor, so every floor gets its one cached
    tagger.
    """
    models: dict[tuple[str, float], NameModel] = {}
    opened: dict[tuple[str, float], NameModel] = {}
    for system in config.systems:
        for model_id in system.model_ids:
            gliner = name_model(model_id, catalog).engine == SPAN_MODEL_ENGINE
            floor = system.cache_floor_of(model_id) if gliner else CACHE_FLOOR
            if (model_id, floor) not in opened:
                path = cache_path(
                    cache_dir,
                    model_id,
                    corpus.dataset,
                    corpus.version,
                    corpus.split,
                    catalog,
                    floor,
                    device if gliner else "cpu",
                )
                opened[model_id, floor] = cached_model(
                    model_id, PredictionCache(path), load_model, load_splitter, catalog, floor
                )
            models[model_id, system.cache_floor_of(model_id)] = opened[model_id, floor]
    return models


def _run_corpus(
    config: RunConfig,
    corpus: Corpus,
    models: dict[tuple[str, float], NameModel],
    progress: Progress,
) -> dict[str, Any]:
    types = scored_types(config, corpus)
    draws = resamples(len(corpus.documents), config.resamples, config.seed)

    per_system: dict[str, dict[tuple[str, str], list[Counts]]] = {}
    coverage_per_system: dict[str, dict[str, list[Coverage]]] = {}
    systems: dict[str, Any] = {}
    for system in config.systems:
        started = time.perf_counter()
        used = system_models(system, models)
        before = {model_id: (model.hits, model.misses) for model_id, model in used.items()}
        counts, coverage, details = _run_system(system, corpus, types, used, draws)
        per_system[system.name] = counts
        coverage_per_system[system.name] = coverage
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
        details["coverage"] = _coverage_scores(coverage, draws)
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
            {
                **_compare(baseline, candidate, per_system, draws),
                "coverage": _compare_coverage(baseline, candidate, coverage_per_system, draws),
            }
            for baseline, candidate in config.compare
        ],
    }


def _run_system(
    system: SystemConfig,
    corpus: Corpus,
    types: frozenset[EntityType],
    models: dict[str, NameModel],
    draws: Sequence[Sequence[int]],
) -> tuple[dict[tuple[str, str], list[Counts]], dict[str, list[Coverage]], dict[str, Any]]:
    counts: dict[tuple[str, str], list[Counts]] = {}
    coverage: dict[str, list[Coverage]] = {}
    tally = PhenomenonTally(corpus) if corpus.tagged else None
    unscored: Counter[str] = Counter()
    languages: Counter[str] = Counter()
    for gold in corpus.documents:
        detect(system, gold.document, corpus.language, models)
        found = gold.document.entities
        for key, value in document_counts(found, gold.gold, types).items():
            counts.setdefault(key, []).append(value)
        pages = [page.text for page in gold.document.pages]
        for kind, value in document_coverage(found, gold.gold, types, pages).items():
            coverage.setdefault(kind, []).append(value)
        if tally is not None:
            tally.add(found, gold, types)
        unscored.update(str(entity.type) for entity in found if entity.type not in types)
        languages[gold.document.language or "none"] += 1
        gold.document.entities = []
    details: dict[str, Any] = {
        "languages": dict(languages.most_common()),
        "unscored_predictions": dict(unscored.most_common()),
    }
    if tally is not None:
        details["phenomena"] = tally.results(draws)
    return counts, coverage, details


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


def _coverage_scores(
    coverage: dict[str, list[Coverage]], draws: Sequence[Sequence[int]]
) -> dict[str, dict[str, Any]]:
    scores: dict[str, dict[str, Any]] = {}
    for kind, per_document in coverage.items():
        resampled = resampled_totals(per_document, draws)
        scores[kind] = {
            "counts": total(per_document).to_dict(),
            **{
                metric: interval(per_document, resampled, metric).to_dict()
                for metric in COVERAGE_METRICS
            },
        }
    return scores


def _compare_coverage(
    baseline: str,
    candidate: str,
    per_system: dict[str, dict[str, list[Coverage]]],
    draws: Sequence[Sequence[int]],
) -> dict[str, Any]:
    differences: dict[str, Any] = {}
    for kind, before in per_system[baseline].items():
        after = per_system[candidate][kind]
        paired_before = (before, resampled_totals(before, draws))
        paired_after = (after, resampled_totals(after, draws))
        differences[kind] = {
            metric: paired_difference(paired_before, paired_after, metric).to_dict()
            for metric in COVERAGE_METRICS
        }
    return differences


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


def machine_on(device: str) -> dict[str, str]:
    """Describe the machine and the device GLiNER ran on; on CUDA also the card."""
    return {**machine(), "device": device, **gpu(device)}


def check_device(device: str) -> None:
    """Refuse a device torch cannot reach; called before minutes of loading data.

    Raises:
        ValueError: If the device is not one of `DEVICES`.
        RuntimeError: If torch cannot reach it on this machine.
    """
    if device not in DEVICES:
        msg = f"device must be one of {DEVICES}"
        raise ValueError(msg)
    if not device_available(device):
        msg = f"device {device!r} is not available on this machine"
        raise RuntimeError(msg)


def device_available(device: str) -> bool:
    """Whether torch can reach the device; the CPU needs no torch to say so."""
    if device == "cpu":
        return True
    import torch  # pyright: ignore[reportMissingImports]

    if device == "cuda":
        return torch.cuda.is_available()
    return torch.backends.mps.is_available()


def gpu(device: str) -> dict[str, str]:
    """The NVIDIA card used and the CUDA version torch was built for; empty off CUDA.

    Runs compared in one table belong on one kind of card, so the results name it.
    """
    if device != "cuda":
        return {}
    import torch  # pyright: ignore[reportMissingImports]

    return {"gpu": torch.cuda.get_device_name(0), "cuda": str(torch.version.cuda)}


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
