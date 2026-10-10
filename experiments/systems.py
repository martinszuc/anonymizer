"""Systems under evaluation, built the way the tools build them, with cached model output.

A system is a named set of options (`SystemConfig`). Its detector is built
by `core.pipeline.build_detector` and run by `core.pipeline.run_detection`,
so the harness measures what the command line and the review window ship;
the options only switch what those functions already offer. A system may
run two name models beside the rules: their union (`CombinedDetector`, as
the rules and a model are combined) or only what both found
(`AgreementDetector`).

The name models are the slow part, so their raw output is cached per model
input. GLiNER (`CachedSpanModel`) is asked once at `CACHE_FLOOR` and the
spans are filtered up to each system's threshold. That is the same as asking
at the higher threshold: flat decoding is greedy, highest score first, so a
span under the threshold never displaced one above it. NameTag 3
(`CachedTagger`) has no threshold; its labels are cached per page of
sentences. Everything after the model (windows, sentences, word widening,
the name filter, the rules, merging, propagation, titles) runs for real on
every run.
"""

from __future__ import annotations

import functools
import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from anonymizer.core.detect import (
    AgreementDetector,
    CombinedDetector,
    GlinerDetector,
    NametagDetector,
    name_model,
)
from anonymizer.core.detect.base import Detector
from anonymizer.core.detect.gliner import (
    DEFAULT_DISTRACTORS,
    DEFAULT_LABELS,
    DEFAULT_THRESHOLD,
    SpanModel,
    encoder_resource,
    load_gliner_model,
)
from anonymizer.core.detect.nametag import (
    NAMETAG_ENGINE,
    Label,
    SentenceSplitter,
    Tagger,
    UDPipeSplitter,
    load_nametag_tagger,
    model_directory,
)
from anonymizer.core.language import AUTO
from anonymizer.core.pipeline import build_detector, resolve_language, run_detection
from anonymizer.core.resources import load_catalog
from anonymizer.core.types import Document, EntityType

CACHE_FLOOR = 0.1
"""Threshold GLiNER is asked at for the cache; systems may filter upwards only."""

SPAN_MODEL_ENGINE = "gliner"
"""The engine whose spans are cached and filtered by score."""

ENGINES = (SPAN_MODEL_ENGINE, NAMETAG_ENGINE)
"""Engines whose output the harness can cache."""

LANGUAGES = ("dataset", "auto", "none")
COMBINATIONS = ("union", "agreement")


@dataclass(frozen=True)
class SystemConfig:
    """Options of one system; the defaults are what the tools ship.

    Attributes:
        name: Name in configs and results.
        model: `none` for the rules alone, else the catalog id of a name
            model run beside them (`gliner` is the default one), or several
            ids.
        combine: How several models are combined: `union` (everything
            either found) or `agreement` (what all of them found).
        threshold: GLiNER's minimum score.
        labels: GLiNER's prompt label → entity type.
        distractors: GLiNER labels asked for whose spans are dropped.
        names_only: Cut the models' person and address spans back to the value.
        propagate: Mark further occurrences of what was found.
        language: `dataset` (the corpus's language), `auto` (recognised from
            the text, as the review window does) or `none` (every rule).
    """

    name: str
    model: str | tuple[str, ...] = "none"
    combine: str = "union"
    threshold: float = DEFAULT_THRESHOLD
    labels: Mapping[str, EntityType] = field(default_factory=lambda: dict(DEFAULT_LABELS))
    distractors: tuple[str, ...] = DEFAULT_DISTRACTORS
    names_only: bool = True
    propagate: bool = True
    language: str = "dataset"

    @property
    def model_names(self) -> tuple[str, ...]:
        """The models as the config names them; empty for the rules alone."""
        if isinstance(self.model, tuple):
            return self.model
        return () if self.model == "none" else (self.model,)

    @property
    def model_ids(self) -> tuple[str, ...]:
        """The catalog ids of the system's name models; empty for the rules alone."""
        return tuple(name_model(model).id for model in self.model_names)

    def describe(self) -> dict[str, Any]:
        """Return the options as plain data, for the results file."""
        described: dict[str, Any] = {
            "model": list(self.model) if isinstance(self.model, tuple) else self.model,
            "propagate": self.propagate,
            "language": self.language,
        }
        if len(self.model_names) > 1:
            described["combine"] = self.combine
        if any(name_model(model).engine == SPAN_MODEL_ENGINE for model in self.model_names):
            described |= {
                "threshold": self.threshold,
                "labels": {label: str(kind) for label, kind in self.labels.items()},
                "distractors": list(self.distractors),
            }
        if self.model_names:
            described["names_only"] = self.names_only
        return described


_SYSTEM_KEYS = frozenset(
    {
        "model",
        "combine",
        "threshold",
        "labels",
        "distractors",
        "names_only",
        "propagate",
        "language",
    }
)


def parse_system(name: str, table: Mapping[str, Any]) -> SystemConfig:
    """Read a system from its config table, rejecting unknown options.

    Args:
        name: The table's name.
        table: Its options.

    Returns:
        The system.

    Raises:
        ValueError: If an option is unknown or out of range.
    """
    unknown = set(table) - _SYSTEM_KEYS
    if unknown:
        msg = f"system {name!r}: unknown options {sorted(unknown)}"
        raise ValueError(msg)
    raw_model = table.get("model", "none")
    model: str | tuple[str, ...] = (
        tuple(str(item) for item in raw_model) if isinstance(raw_model, list) else str(raw_model)
    )
    models = model if isinstance(model, tuple) else ((model,) if model != "none" else ())
    for item in models:
        _check_model(name, item)
    if isinstance(model, tuple) and len({name_model(item).id for item in models}) < 2:
        msg = f"system {name!r}: a list of models needs two different models"
        raise ValueError(msg)
    combine = str(table.get("combine", "union"))
    if combine not in COMBINATIONS:
        msg = f"system {name!r}: combine must be one of {COMBINATIONS}"
        raise ValueError(msg)
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
        combine=combine,
        threshold=threshold,
        labels=labels,
        distractors=tuple(str(label) for label in table.get("distractors", DEFAULT_DISTRACTORS)),
        names_only=bool(table.get("names_only", True)),
        propagate=bool(table.get("propagate", True)),
        language=language,
    )


def _check_model(system: str, model: str) -> None:
    """Refuse a model that is not a catalog name model whose output the harness can cache."""
    try:
        engine = name_model(model).engine
    except ValueError as error:
        msg = f"system {system!r}: {error}, or none"
        raise ValueError(msg) from error
    if engine not in ENGINES:
        msg = f"system {system!r}: model {model!r} runs on {engine}, not {' or '.join(ENGINES)}"
        raise ValueError(msg)


class PredictionCache:
    """Model output per input, stored as JSON keyed by a hash of the input.

    The file holds offsets, labels and scores, never text: a key is the
    SHA-256 of the model input (for GLiNER the labels, decoding mode, floor
    and window text; for NameTag the page's tokens), so changed text or a
    changed prompt simply misses.
    """

    def __init__(self, path: Path) -> None:
        """Open a cache file, reading it if it exists.

        Args:
            path: The JSON file.
        """
        self.path = path
        self._entries: dict[str, Any] = (
            json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        )
        self._dirty = False

    def __contains__(self, key: str) -> bool:
        """Whether output is stored for a key."""
        return key in self._entries

    def __getitem__(self, key: str) -> Any:
        """Return the output stored for a key."""
        return self._entries[key]

    def __setitem__(self, key: str, output: Any) -> None:
        """Store output for a key."""
        self._entries[key] = output
        self._dirty = True

    def __len__(self) -> int:
        """Return the number of inputs stored."""
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
    """Return the cache key for one GLiNER input."""
    payload = json.dumps([list(labels), flat_ner, floor, text], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def tagger_key(sentences: Sequence[Sequence[str]]) -> str:
    """Return the cache key for one NameTag input: a page's sentences of tokens."""
    payload = json.dumps([list(sentence) for sentence in sentences], ensure_ascii=False)
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


class CachedTagger:
    """A NameTag `Tagger` answering from a cache, with the model's sentence splitter.

    Attributes:
        hits: Pages answered from the cache.
        misses: Pages the model was asked about.
    """

    def __init__(
        self,
        load_tagger: Callable[[], Tagger],
        load_splitter: Callable[[], SentenceSplitter],
        cache: PredictionCache,
    ) -> None:
        """Wrap a model loader, a splitter loader and a cache.

        Args:
            load_tagger: Returns the real model; called on the first miss only.
            load_splitter: Returns the model's sentence splitter.
            cache: Where labels are kept.
        """
        self._load_tagger = load_tagger
        self._load_splitter = load_splitter
        self.cache = cache
        self.hits = 0
        self.misses = 0

    @functools.cached_property
    def splitter(self) -> SentenceSplitter:
        """The model's sentence splitter, loaded on first use."""
        return self._load_splitter()

    def tag(self, sentences: Sequence[Sequence[str]]) -> list[list[list[Label]]]:
        """Return the labels of a page's tokens, from the cache where stored."""
        key = tagger_key(sentences)
        if key in self.cache:
            self.hits += 1
        else:
            self.misses += 1
            self.cache[key] = self._load_tagger().tag(sentences)
        return [
            [[(label, probability) for label, probability in token] for token in sentence]
            for sentence in self.cache[key]
        ]


NameModel = CachedSpanModel | CachedTagger
"""A name model as a system runs it: cached, by engine."""


def _stored(span: Mapping[str, Any]) -> dict[str, Any]:
    """Keep what the detector reads from a span; GLiNER also returns its text."""
    return {
        "start": int(span["start"]),
        "end": int(span["end"]),
        "label": str(span["label"]),
        "score": float(span["score"]),
    }


def cache_path(
    cache_dir: Path, model_id: str, dataset: str, dataset_version: str, split: str
) -> Path:
    """Return the cache file for a name model on one split of a dataset."""
    model = load_catalog()[model_id]
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


def model_loader(resource_root: Path) -> Callable[[str], SpanModel | Tagger]:
    """Return a function loading a catalog name model of either engine, by id.

    Raises:
        FileNotFoundError: When called, if the model is not stored under the root.
    """
    load_gliner = gliner_loader(resource_root)

    def load(model_id: str) -> SpanModel | Tagger:
        if name_model(model_id).engine == SPAN_MODEL_ENGINE:
            return load_gliner(model_id)
        catalog = load_catalog()
        return load_nametag_tagger(
            model_directory(resource_root, model_id, catalog),
            catalog[encoder_resource(catalog, model_id)].directory(resource_root),
        )

    return load


def splitter_loader(resource_root: Path) -> Callable[[str], SentenceSplitter]:
    """Return a function loading a NameTag model's sentence splitter, by id."""

    def load(model_id: str) -> SentenceSplitter:
        directory = model_directory(resource_root, model_id, load_catalog())
        return UDPipeSplitter(directory / "udpipe.tokenizer")

    return load


def cached_model(
    model_id: str,
    cache: PredictionCache,
    load_model: Callable[[str], Any],
    load_splitter: Callable[[str], SentenceSplitter],
) -> NameModel:
    """Wrap a name model, loaded on first need, in the cache of its engine."""
    if name_model(model_id).engine == SPAN_MODEL_ENGINE:
        return CachedSpanModel(functools.partial(load_model, model_id), cache)
    return CachedTagger(
        functools.partial(load_model, model_id), functools.partial(load_splitter, model_id), cache
    )


def model_versions(systems: Sequence[SystemConfig]) -> dict[str, str]:
    """Return the catalog version of every model the systems use."""
    catalog = load_catalog()
    return {
        resource.id: resource.version
        for system in systems
        for model_id in system.model_ids
        for resource in catalog.with_requirements(model_id)
    }


def build_system_detector(
    system: SystemConfig, language: str | None, models: Mapping[str, NameModel]
) -> Detector:
    """Build a system's detector for a language through `core.pipeline`.

    Args:
        system: The options.
        language: The language detection runs in.
        models: The (cached) name models by catalog id; those the system uses
            are needed.

    Returns:
        The detector.

    Raises:
        ValueError: If the system needs a model that is not given.
    """
    if not system.model_ids:
        return build_detector(language)
    missing = [model_id for model_id in system.model_ids if model_id not in models]
    if missing:
        msg = f"system {system.name!r} needs the name model {', '.join(missing)}"
        raise ValueError(msg)
    detectors = [
        _model_detector(system, model_id, models[model_id]) for model_id in system.model_ids
    ]
    if len(detectors) == 1:
        model: Detector = detectors[0]
    elif system.combine == "agreement":
        model = AgreementDetector(detectors)
    else:
        model = CombinedDetector(detectors)
    return build_detector(language, model=model, names_only=system.names_only)


def _model_detector(system: SystemConfig, model_id: str, model: Any) -> Detector:
    if name_model(model_id).engine == NAMETAG_ENGINE:
        return NametagDetector(model, model.splitter, name=model_id)
    return GlinerDetector(
        model,
        labels=system.labels,
        threshold=system.threshold,
        name=model_id,
        distractors=system.distractors,
    )


def detect(
    system: SystemConfig, document: Document, language: str, models: Mapping[str, NameModel]
) -> None:
    """Run a system over a document in place, as the tools do.

    Args:
        system: The options.
        document: The document; its entities are replaced.
        language: The corpus's language, used when the system says `dataset`.
        models: The (cached) name models by catalog id.
    """
    requested = {"dataset": language, "auto": AUTO, "none": None}[system.language]
    resolved = resolve_language(document, requested)
    detector = build_system_detector(system, resolved, models)
    run_detection(document, detector, propagate=system.propagate)
