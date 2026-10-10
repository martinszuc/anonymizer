"""Systems under evaluation, built the way the tools build them, with cached model output.

A system is a named set of options (`SystemConfig`). Its detector is built
by `core.pipeline.build_detector` and run by `core.pipeline.run_detection`,
so the harness measures what the command line and the review window ship;
the options only switch what those functions already offer.

The name model is the slow part, so its raw output is cached per window
text (`CachedSpanModel`). The model is asked once at `CACHE_FLOOR` and the
spans are filtered up to each system's threshold. That is the same as asking
at the higher threshold: flat decoding is greedy, highest score first, so a
span under the threshold never displaced one above it. Everything after the
model (windows, word widening, the name filter, the rules, merging,
propagation, titles) runs for real on every run.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from anonymizer.core.detect import GlinerDetector, name_model
from anonymizer.core.detect.base import Detector
from anonymizer.core.detect.gliner import (
    DEFAULT_DISTRACTORS,
    DEFAULT_LABELS,
    DEFAULT_THRESHOLD,
    SpanModel,
    load_gliner_model,
)
from anonymizer.core.detect.models import NAME_MODEL_ALIASES
from anonymizer.core.language import AUTO
from anonymizer.core.pipeline import build_detector, resolve_language, run_detection
from anonymizer.core.resources import Catalog, load_catalog
from anonymizer.core.types import Document, EntityType

CACHE_FLOOR = 0.1
"""Threshold the model is asked at for the cache; systems may filter upwards only."""

SPAN_MODEL_ENGINE = "gliner"
"""The engine whose models the harness runs: its spans are cached and filtered by score."""

LANGUAGES = ("dataset", "auto", "none")


@dataclass(frozen=True)
class SystemConfig:
    """Options of one system; the defaults are what the tools ship.

    Attributes:
        name: Name in configs and results.
        model: `none` for the rules alone, else the catalog id of a GLiNER
            name model run beside them (`gliner` is the default one).
        threshold: The name model's minimum score.
        labels: Prompt label → entity type.
        distractors: Labels asked for whose spans are dropped.
        names_only: Cut the model's person and address spans back to the value.
        propagate: Mark further occurrences of what was found.
        language: `dataset` (the corpus's language), `auto` (recognised from
            the text, as the review window does) or `none` (every rule).
    """

    name: str
    model: str = "none"
    threshold: float = DEFAULT_THRESHOLD
    labels: Mapping[str, EntityType] = field(default_factory=lambda: dict(DEFAULT_LABELS))
    distractors: tuple[str, ...] = DEFAULT_DISTRACTORS
    names_only: bool = True
    propagate: bool = True
    language: str = "dataset"

    @property
    def model_id(self) -> str | None:
        """The catalog id of the system's name model; `None` for the rules alone."""
        return None if self.model == "none" else NAME_MODEL_ALIASES.get(self.model, self.model)

    def describe(self) -> dict[str, Any]:
        """Return the options as plain data, for the results file."""
        described: dict[str, Any] = {
            "model": self.model,
            "propagate": self.propagate,
            "language": self.language,
        }
        if self.model != "none":
            described |= {
                "threshold": self.threshold,
                "labels": {label: str(kind) for label, kind in self.labels.items()},
                "distractors": list(self.distractors),
                "names_only": self.names_only,
            }
        return described


_SYSTEM_KEYS = frozenset(
    {"model", "threshold", "labels", "distractors", "names_only", "propagate", "language"}
)


def parse_system(
    name: str, table: Mapping[str, Any], catalog: Catalog | None = None
) -> SystemConfig:
    """Read a system from its config table, rejecting unknown options.

    Args:
        name: The table's name.
        table: Its options.
        catalog: The catalog naming the models; the shipped one when omitted.

    Returns:
        The system.

    Raises:
        ValueError: If an option is unknown or out of range.
    """
    unknown = set(table) - _SYSTEM_KEYS
    if unknown:
        msg = f"system {name!r}: unknown options {sorted(unknown)}"
        raise ValueError(msg)
    model = str(table.get("model", "none"))
    if model != "none":
        _check_model(name, model, catalog or load_catalog())
    language = str(table.get("language", "dataset"))
    if language not in LANGUAGES:
        msg = f"system {name!r}: language must be one of {LANGUAGES}"
        raise ValueError(msg)
    threshold = float(table.get("threshold", DEFAULT_THRESHOLD))
    if not CACHE_FLOOR <= threshold <= 1.0:
        msg = f"system {name!r}: threshold must lie in [{CACHE_FLOOR}, 1]"
        raise ValueError(msg)
    labels = {
        str(label): EntityType(kind)
        for label, kind in dict(table.get("labels", DEFAULT_LABELS)).items()
    }
    return SystemConfig(
        name=name,
        model=model,
        threshold=threshold,
        labels=labels,
        distractors=tuple(str(label) for label in table.get("distractors", DEFAULT_DISTRACTORS)),
        names_only=bool(table.get("names_only", True)),
        propagate=bool(table.get("propagate", True)),
        language=language,
    )


def _check_model(system: str, model: str, catalog: Catalog) -> None:
    """Refuse a model that is not a catalog GLiNER model, whose output the harness can cache."""
    try:
        engine = name_model(model, catalog).engine
    except ValueError as error:
        msg = f"system {system!r}: {error}, or none"
        raise ValueError(msg) from error
    if engine != SPAN_MODEL_ENGINE:
        msg = f"system {system!r}: model {model!r} runs on {engine}, not {SPAN_MODEL_ENGINE}"
        raise ValueError(msg)


class PredictionCache:
    """Model spans per window, stored as JSON keyed by a hash of the input.

    The file holds offsets, labels and scores, never text: a key is the
    SHA-256 of the model input (labels, decoding mode, floor and the window
    text), so changed text or a changed prompt simply misses.
    """

    def __init__(self, path: Path) -> None:
        """Open a cache file, reading it if it exists.

        Args:
            path: The JSON file.
        """
        self.path = path
        self._entries: dict[str, list[dict[str, Any]]] = (
            json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        )
        self._dirty = False

    def __contains__(self, key: str) -> bool:
        """Whether spans are stored for a key."""
        return key in self._entries

    def __getitem__(self, key: str) -> list[dict[str, Any]]:
        """Return the spans stored for a key."""
        return self._entries[key]

    def __setitem__(self, key: str, spans: list[dict[str, Any]]) -> None:
        """Store spans for a key."""
        self._entries[key] = spans
        self._dirty = True

    def __len__(self) -> int:
        """Return the number of windows stored."""
        return len(self._entries)

    def save(self) -> None:
        """Write the file if anything was added, atomically."""
        if not self._dirty:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        staging = self.path.with_name(self.path.name + ".part")
        staging.write_text(json.dumps(self._entries, sort_keys=True), encoding="utf-8")
        staging.replace(self.path)
        self._dirty = False


def cache_key(text: str, labels: Sequence[str], *, flat_ner: bool, floor: float) -> str:
    """Return the cache key for one model input."""
    payload = json.dumps([list(labels), flat_ner, floor, text], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CachedSpanModel:
    """A `SpanModel` answering from a cache, and asking the real model only for misses.

    Attributes:
        hits: Windows answered from the cache.
        misses: Windows the model was asked about.
    """

    def __init__(
        self,
        load_model: Callable[[], SpanModel],
        cache: PredictionCache,
        floor: float = CACHE_FLOOR,
    ) -> None:
        """Wrap a model loader and a cache.

        Args:
            load_model: Returns the real model; called on the first miss only.
            cache: Where spans are kept.
            floor: Threshold the model is asked at.
        """
        self._load_model = load_model
        self.cache = cache
        self.floor = floor
        self.hits = 0
        self.misses = 0

    def inference(
        self,
        texts: list[str],
        labels: list[str],
        *,
        threshold: float,
        flat_ner: bool,
    ) -> list[list[dict[str, Any]]]:
        """Return the spans above a threshold for each text, as GLiNER does.

        Raises:
            ValueError: If the threshold is below the cache floor.
        """
        if threshold < self.floor:
            msg = f"threshold {threshold} is below the cache floor {self.floor}"
            raise ValueError(msg)
        keys = [cache_key(text, labels, flat_ner=flat_ner, floor=self.floor) for text in texts]
        missing = [index for index, key in enumerate(keys) if key not in self.cache]
        self.hits += len(keys) - len(missing)
        self.misses += len(missing)
        if missing:
            answers = self._load_model().inference(
                [texts[index] for index in missing],
                labels,
                threshold=self.floor,
                flat_ner=flat_ner,
            )
            for index, spans in zip(missing, answers, strict=True):
                self.cache[keys[index]] = [_stored(span) for span in spans]
        # GLiNER keeps a span whose score is strictly above the threshold.
        return [[span for span in self.cache[key] if span["score"] > threshold] for key in keys]


def _stored(span: Mapping[str, Any]) -> dict[str, Any]:
    """Keep what the detector reads from a span; GLiNER also returns its text."""
    return {
        "start": int(span["start"]),
        "end": int(span["end"]),
        "label": str(span["label"]),
        "score": float(span["score"]),
    }


def cache_path(
    cache_dir: Path,
    model_id: str,
    dataset: str,
    dataset_version: str,
    split: str,
    catalog: Catalog | None = None,
) -> Path:
    """Return the cache file for a name model on one split of a dataset.

    The model's version is part of the path: a trained model's is the hash of
    its weights, so a model trained again under the same id starts a new cache.
    """
    model = (catalog or load_catalog())[model_id]
    return (
        cache_dir
        / f"{model.id}@{_safe(model.version)}"
        / f"{dataset}@{_safe(dataset_version)}"
        / f"{split}.json"
    )


def _safe(version: str) -> str:
    """Make a version usable in a file name (CNEC's is a handle with slashes)."""
    return re.sub(r"[^A-Za-z0-9.-]+", "_", version)[:64]


def gliner_loader(resource_root: Path) -> Callable[[str], SpanModel]:
    """Return a function loading a catalog GLiNER model, by id, from the storage root.

    Raises:
        FileNotFoundError: When called, if the model is not stored under the root.
    """
    return lambda model_id: load_gliner_model(resource_root, model_id)


def model_versions(
    systems: Sequence[SystemConfig], catalog: Catalog | None = None
) -> dict[str, str]:
    """Return the catalog version of every model the systems use."""
    catalog = catalog or load_catalog()
    return {
        resource.id: resource.version
        for system in systems
        if system.model_id is not None
        for resource in catalog.with_requirements(system.model_id)
    }


def build_system_detector(
    system: SystemConfig, language: str | None, model: SpanModel | None
) -> Detector:
    """Build a system's detector for a language through `core.pipeline`.

    Args:
        system: The options.
        language: The language detection runs in.
        model: The (cached) name model, needed unless the system has none.

    Returns:
        The detector.

    Raises:
        ValueError: If the system needs a model and none is given.
    """
    if system.model_id is None:
        return build_detector(language)
    if model is None:
        msg = f"system {system.name!r} needs the name model"
        raise ValueError(msg)
    gliner = GlinerDetector(
        model,
        labels=system.labels,
        threshold=system.threshold,
        name=system.model_id,
        distractors=system.distractors,
    )
    return build_detector(language, model=gliner, names_only=system.names_only)


def detect(
    system: SystemConfig, document: Document, language: str, model: SpanModel | None
) -> None:
    """Run a system over a document in place, as the tools do.

    Args:
        system: The options.
        document: The document; its entities are replaced.
        language: The corpus's language, used when the system says `dataset`.
        model: The (cached) name model, if the system uses one.
    """
    requested = {"dataset": language, "auto": AUTO, "none": None}[system.language]
    resolved = resolve_language(document, requested)
    detector = build_system_detector(system, resolved, model)
    run_detection(document, detector, propagate=system.propagate)
