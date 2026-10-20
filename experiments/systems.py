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
span under the threshold never displaced one above it. A system whose
threshold lies below `CACHE_FLOOR` reads a second cache, asked at
`LOW_CACHE_FLOOR` and kept in files of its own (`cache_path`), so the usual
cache stays as it was and other runs can read it meanwhile. A system that
sets no threshold runs each model at its own (`name_model_threshold`: the
catalog entry's, else GLiNER's default), so the floor is chosen per model
from that effective threshold. GLiNER may run on a GPU (`model_loader`); its
output there is cached apart from the CPU's, for the reason `cache_path`
gives. A token classifier trained here answers GLiNER's call
(`core.detect.token_classifier`) and is cached, filtered and run on a device
exactly as GLiNER is: its threshold filters decoded spans only, so the same
floor argument holds. NameTag 3
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
    name_model_threshold,
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
from anonymizer.core.detect.models import NAME_MODEL_ALIASES
from anonymizer.core.detect.nametag import (
    NAMETAG_ENGINE,
    Label,
    SentenceSplitter,
    Tagger,
    UDPipeSplitter,
    load_nametag_tagger,
    model_directory,
)
from anonymizer.core.detect.token_classifier import (
    TOKEN_CLASSIFIER_ENGINE,
    load_token_classifier_model,
)
from anonymizer.core.language import AUTO
from anonymizer.core.pipeline import build_detector, resolve_language, run_detection
from anonymizer.core.resources import Catalog, load_catalog
from anonymizer.core.types import Document, EntityType

CACHE_FLOOR = 0.1
"""Threshold GLiNER is asked at for the cache; systems may filter upwards only."""

LOW_CACHE_FLOOR = 0.02
"""Floor of the second cache, read by systems whose threshold lies below `CACHE_FLOOR`.

Low enough for the threshold matching a recall weight of 10: `t / (w(1 - t) + t)`
is 0.041 at the default 0.3 (`experiments/README.md`, *Training*).
"""

SPAN_MODEL_ENGINES = ("gliner", TOKEN_CLASSIFIER_ENGINE)
"""Engines answering GLiNER's call, whose spans are cached and filtered by score."""

ENGINES = (*SPAN_MODEL_ENGINES, NAMETAG_ENGINE)
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
        threshold: The minimum score for every span model (GLiNER, token
            classifier) of the system; `None` runs each at its own
            (`model_thresholds`).
        labels: GLiNER's prompt label → entity type; a token classifier's
            types are named the same.
        distractors: GLiNER labels asked for whose spans are dropped.
        names_only: Cut the models' person and address spans back to the value.
        propagate: Mark further occurrences of what was found.
        language: `dataset` (the corpus's language), `auto` (recognised from
            the text, as the review window does) or `none` (every rule).
        engines: The engine of each model, as the catalog names them when
            the system was parsed; empty when built directly, which reports
            GLiNER's options.
        model_thresholds: Each span model's own threshold by catalog id
            (`name_model_threshold`), filled when the system is parsed
            without a threshold; a model missing here runs at GLiNER's
            `DEFAULT_THRESHOLD`.
    """

    name: str
    model: str | tuple[str, ...] = "none"
    combine: str = "union"
    threshold: float | None = None
    labels: Mapping[str, EntityType] = field(default_factory=lambda: dict(DEFAULT_LABELS))
    distractors: tuple[str, ...] = DEFAULT_DISTRACTORS
    names_only: bool = True
    propagate: bool = True
    language: str = "dataset"
    engines: tuple[str, ...] = ()
    model_thresholds: Mapping[str, float] = field(default_factory=dict)

    @property
    def model_names(self) -> tuple[str, ...]:
        """The models as the config names them; empty for the rules alone."""
        if isinstance(self.model, tuple):
            return self.model
        return () if self.model == "none" else (self.model,)

    @property
    def model_ids(self) -> tuple[str, ...]:
        """The catalog ids of the system's name models; empty for the rules alone."""
        return tuple(NAME_MODEL_ALIASES.get(model, model) for model in self.model_names)

    @property
    def span_model_ids(self) -> tuple[str, ...]:
        """The catalog ids of the system's span models; every model when built directly."""
        if not self.engines:
            return self.model_ids
        return tuple(
            model_id
            for model_id, engine in zip(self.model_ids, self.engines, strict=True)
            if engine in SPAN_MODEL_ENGINES
        )

    def threshold_of(self, model_id: str) -> float:
        """Return the threshold a span model of the system runs at."""
        if self.threshold is not None:
            return self.threshold
        return self.model_thresholds.get(model_id, DEFAULT_THRESHOLD)

    def cache_floor_of(self, model_id: str) -> float:
        """Return the floor of the cache a model of the system reads (`cache_floor`)."""
        if model_id not in self.span_model_ids:
            return CACHE_FLOOR
        return cache_floor(self.threshold_of(model_id))

    def describe(self) -> dict[str, Any]:
        """Return the options as plain data, for the results file."""
        described: dict[str, Any] = {
            "model": list(self.model) if isinstance(self.model, tuple) else self.model,
            "propagate": self.propagate,
            "language": self.language,
        }
        if len(self.model_names) > 1:
            described["combine"] = self.combine
        if self.span_model_ids:
            thresholds = {model_id: self.threshold_of(model_id) for model_id in self.span_model_ids}
            described |= _per_model("threshold", thresholds) | {
                "labels": {label: str(kind) for label, kind in self.labels.items()},
                "distractors": list(self.distractors),
            }
            floors = {model_id: self.cache_floor_of(model_id) for model_id in thresholds}
            if set(floors.values()) != {CACHE_FLOOR}:
                described |= _per_model("cache_floor", floors)
        if self.model_names:
            described["names_only"] = self.names_only
        return described


def _per_model(key: str, values: Mapping[str, float]) -> dict[str, Any]:
    """Describe one value per model as `key` when they agree, else by model as `<key>s`."""
    if len(set(values.values())) == 1:
        return {key: next(iter(values.values()))}
    return {f"{key}s": dict(values)}


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
    raw_model = table.get("model", "none")
    model: str | tuple[str, ...] = (
        tuple(str(item) for item in raw_model) if isinstance(raw_model, list) else str(raw_model)
    )
    models = model if isinstance(model, tuple) else ((model,) if model != "none" else ())
    catalog = catalog or load_catalog()
    engines = tuple(_check_model(name, item, catalog) for item in models)
    if isinstance(model, tuple) and len({name_model(item, catalog).id for item in models}) < 2:
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
    threshold = None if "threshold" not in table else float(table["threshold"])
    if threshold is not None and not LOW_CACHE_FLOOR <= threshold <= 1.0:
        msg = f"system {name!r}: threshold must lie in [{LOW_CACHE_FLOOR}, 1]"
        raise ValueError(msg)
    model_thresholds = (
        _model_thresholds(name, models, engines, catalog) if threshold is None else {}
    )
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
        engines=engines,
        model_thresholds=model_thresholds,
    )


def _model_thresholds(
    system: str, models: Sequence[str], engines: Sequence[str], catalog: Catalog
) -> dict[str, float]:
    """Return each span model's own threshold; refuse one no cache reaches."""
    thresholds: dict[str, float] = {}
    for model, engine in zip(models, engines, strict=True):
        if engine not in SPAN_MODEL_ENGINES:
            continue
        model_id = name_model(model, catalog).id
        threshold = name_model_threshold(model_id, catalog) or DEFAULT_THRESHOLD
        if threshold < LOW_CACHE_FLOOR:
            msg = (
                f"system {system!r}: model {model!r} runs at threshold {threshold}, below the "
                f"lowest cache floor {LOW_CACHE_FLOOR}; give the system a threshold"
            )
            raise ValueError(msg)
        thresholds[model_id] = threshold
    return thresholds


def cache_floor(threshold: float) -> float:
    """Return the floor of the GLiNER cache a threshold is read from.

    Raises:
        ValueError: If the threshold lies below the lowest floor.
    """
    if threshold < LOW_CACHE_FLOOR:
        msg = f"threshold {threshold} is below the lowest cache floor {LOW_CACHE_FLOOR}"
        raise ValueError(msg)
    return CACHE_FLOOR if threshold >= CACHE_FLOOR else LOW_CACHE_FLOOR


def _check_model(system: str, model: str, catalog: Catalog) -> str:
    """Return a model's engine; refuse one whose output the harness cannot cache."""
    try:
        engine = name_model(model, catalog).engine
    except ValueError as error:
        msg = f"system {system!r}: {error}, or none"
        raise ValueError(msg) from error
    if engine not in ENGINES:
        msg = (
            f"system {system!r}: model {model!r} runs on {engine}, not one of {', '.join(ENGINES)}"
        )
        raise ValueError(msg)
    return engine


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
    cache_dir: Path,
    model_id: str,
    dataset: str,
    dataset_version: str,
    split: str,
    catalog: Catalog | None = None,
    floor: float = CACHE_FLOOR,
    device: str = "cpu",
) -> Path:
    """Return the cache file for a name model on one split of a dataset.

    The model's version is part of the path: a trained model's is the hash of
    its weights, so a model trained again under the same id starts a new cache.
    A GLiNER cache asked at another floor than `CACHE_FLOOR` has a file of its
    own (`<split>@floor<floor>.json`): a run filling it never writes the file
    other runs read.

    So does a GLiNER model run on a GPU (`<split>@cuda.json`, `@mps`). A GPU
    adds up in another order than the CPU, so scores differ in the last
    digits, and a span scored next to a threshold or the floor can fall on
    either side of it; greedy decoding can then keep another of two
    overlapping spans. Sharing one file would make a run's scores depend on
    which device filled it first, and `machine.device` in the results would
    not say where the predictions came from. The CPU keeps the plain name, so
    caches written before devices were chosen stay valid. NameTag 3 always
    runs on the CPU and has no device in its path.
    """
    model = (catalog or load_catalog())[model_id]
    name = split if floor == CACHE_FLOOR else f"{split}@floor{floor:g}"
    if device != "cpu":
        name += f"@{device}"
    return (
        cache_dir
        / f"{model.id}@{_safe(model.version)}"
        / f"{dataset}@{_safe(dataset_version)}"
        / f"{name}.json"
    )


def _safe(version: str) -> str:
    """Make a version usable in a file name (CNEC's is a handle with slashes)."""
    return re.sub(r"[^A-Za-z0-9.-]+", "_", version)[:64]


def span_model_loader(
    resource_root: Path, catalog: Catalog | None = None, device: str = "cpu"
) -> Callable[[str], SpanModel]:
    """Return a function loading a catalog span model (GLiNER, token classifier), by id.

    Args:
        resource_root: Storage root holding `models/`.
        catalog: The catalog naming the models; the shipped one when omitted.
        device: Where the model runs (`run.DEVICES`). Both load onto the CPU
            and move each batch to the model's device.

    Raises:
        FileNotFoundError: When called, if the model is not stored under the root.
    """
    catalog = catalog or load_catalog()

    def load(model_id: str) -> SpanModel:
        model: Any = (
            load_token_classifier_model(resource_root, model_id, catalog=catalog)
            if name_model(model_id, catalog).engine == TOKEN_CLASSIFIER_ENGINE
            else load_gliner_model(resource_root, model_id, catalog=catalog)
        )
        return model.to(device)

    return load


def model_loader(
    resource_root: Path, catalog: Catalog | None = None, device: str = "cpu"
) -> Callable[[str], SpanModel | Tagger]:
    """Return a function loading a catalog name model of either engine, by id.

    `device` is where a span model runs; NameTag 3 runs on the CPU.

    Raises:
        FileNotFoundError: When called, if the model is not stored under the root.
    """
    catalog = catalog or load_catalog()
    load_span_model = span_model_loader(resource_root, catalog, device)

    def load(model_id: str) -> SpanModel | Tagger:
        if name_model(model_id, catalog).engine in SPAN_MODEL_ENGINES:
            return load_span_model(model_id)
        return load_nametag_tagger(
            model_directory(resource_root, model_id, catalog),
            catalog[encoder_resource(catalog, model_id)].directory(resource_root),
        )

    return load


def splitter_loader(
    resource_root: Path, catalog: Catalog | None = None
) -> Callable[[str], SentenceSplitter]:
    """Return a function loading a NameTag model's sentence splitter, by id."""
    catalog = catalog or load_catalog()

    def load(model_id: str) -> SentenceSplitter:
        directory = model_directory(resource_root, model_id, catalog)
        return UDPipeSplitter(directory / "udpipe.tokenizer")

    return load


def cached_model(
    model_id: str,
    cache: PredictionCache,
    load_model: Callable[[str], Any],
    load_splitter: Callable[[str], SentenceSplitter],
    catalog: Catalog | None = None,
    floor: float = CACHE_FLOOR,
) -> NameModel:
    """Wrap a name model, loaded on first need, in the cache of its engine.

    `floor` is the threshold a span model is asked at; NameTag has none.
    """
    if name_model(model_id, catalog).engine in SPAN_MODEL_ENGINES:
        return CachedSpanModel(functools.partial(load_model, model_id), cache, floor)
    return CachedTagger(
        functools.partial(load_model, model_id), functools.partial(load_splitter, model_id), cache
    )


def model_versions(
    systems: Sequence[SystemConfig], catalog: Catalog | None = None
) -> dict[str, str]:
    """Return the catalog version of every model the systems use."""
    catalog = catalog or load_catalog()
    return {
        resource.id: resource.version
        for system in systems
        for model_id in system.model_ids
        for resource in catalog.with_requirements(model_id)
    }


def system_models(
    system: SystemConfig, models: Mapping[tuple[str, float], NameModel]
) -> dict[str, NameModel]:
    """Return the cached name models a system uses, by catalog id, each at its cache floor.

    Args:
        system: The system.
        models: Cached models by catalog id and cache floor (`run.corpus_models`).

    Returns:
        The models `detect` needs for the system.
    """
    return {
        model_id: models[model_id, system.cache_floor_of(model_id)] for model_id in system.model_ids
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


def _model_detector(system: SystemConfig, model_id: str, model: NameModel) -> Detector:
    if isinstance(model, CachedTagger):
        return NametagDetector(model, model.splitter, name=model_id)
    return GlinerDetector(
        model,
        labels=system.labels,
        threshold=system.threshold_of(model_id),
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
