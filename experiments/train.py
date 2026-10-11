"""Fine-tuning GLiNER for Czech and Slovak names and addresses, from a config, seeded.

`python -m experiments train --config experiments/configs/train-<name>.toml`
reads the train splits of the configured corpora (`examples.py` turns them
into GLiNER examples), trains the base model on this machine's GPU (`mps`)
or CPU, stores the weights under `<resource root>/models/<model>/` and lists
them in that root's `models/trained.json` (`resources.catalog`), so the
model runs as `rules+<model>` everywhere a name model can. It then scores
`rules+<model>` on the configured development splits through
`experiments.run`, which caches the model's output for later runs, and
writes `results/<name>.json` and `.md`: commit, machine, versions of the
base model and the data, the config, the counts of the examples, the loss
during training, the time it took and the scores.

```toml
name = "train-smoke"          # names the results files
description = "..."
model = "gliner-cs-sk-smoke"  # catalog id of the trained model
base = "gliner-multi-v2.1"    # a GLiNER name model of the catalog
seed = 20261010
device = "mps"                # "mps" (the Apple GPU) or "cpu"

[training]
steps = 40
batch_size = 8
learning_rate = 1e-5          # the encoder
head_learning_rate = 5e-5     # GLiNER's span and prompt layers
weight_decay = 0.01
warmup_ratio = 0.1
loss = "focal"                # "ce", or "focal" with focal_alpha and focal_gamma
focal_alpha = 0.75            # weight of the positive spans; above 0.5 favours recall
focal_gamma = 2.0

[[corpora]]                   # train splits only
id = "openpii-1m-cs"
split = "train"
examples = 200                # drawn at random (seeded); every example when omitted

[evaluate]                    # development splits only
limit = 40                    # optional: the first documents of each split
datasets = [{ id = "cnec-2.0", split = "dtest" }]
```

GLiNER scores every (span, label) pair on its own with a sigmoid, so its
`ce` is binary cross-entropy per pair. `focal` is gliner's focal loss: alpha
weights the positive pairs against the negative ones, gamma lowers the
weight of pairs already classified well. Weights trained on CNEC or UNER
hold real public names: they stay under the resource root, never committed
or published, and their catalog entry says so (`real_personal_data`).
"""

from __future__ import annotations

import datetime
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import tempfile
import time
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import anonymizer.core
from anonymizer.core.detect import name_model
from anonymizer.core.detect.gliner import SpanModel, load_gliner_model
from anonymizer.core.resources import Catalog, load_catalog, trained_catalog_path
from anonymizer.core.resources.catalog import CATALOG_SCHEMA, is_resource_id, parse_catalog

from experiments.config import DatasetRef, parse_config
from experiments.datasets import DATASETS, Role, load_corpus
from experiments.examples import MAX_TOKENS, Conversion, Example, corpus_examples, sample
from experiments.report import markdown
from experiments.run import Progress, git_state, machine, run

TRAINING_SCHEMA = 1
DEVICES = ("mps", "cpu")
LOSSES = ("ce", "focal")
WEIGHTS = "model.safetensors"
CONFIG = "gliner_config.json"

_KEYS = frozenset(
    {"name", "description", "model", "base", "seed", "device", "training", "corpora", "evaluate"}
)
_TRAINING_KEYS = frozenset(
    {
        "steps",
        "batch_size",
        "learning_rate",
        "head_learning_rate",
        "weight_decay",
        "warmup_ratio",
        "loss",
        "focal_alpha",
        "focal_gamma",
        "max_tokens",
        "logging_steps",
    }
)


@dataclass(frozen=True)
class Hyperparameters:
    """How the model is trained (the `[training]` table)."""

    steps: int
    batch_size: int = 8
    learning_rate: float = 1e-5
    head_learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    loss: str = "ce"
    focal_alpha: float = -1.0
    focal_gamma: float = 0.0
    max_tokens: int = MAX_TOKENS
    logging_steps: int = 10


@dataclass(frozen=True)
class CorpusRef:
    """A train split and how many of its examples to draw (`None`: all)."""

    id: str
    split: str
    examples: int | None = None


@dataclass(frozen=True)
class TrainConfig:
    """A parsed training configuration.

    Attributes:
        name: Names the results files.
        description: Free text, copied into the results.
        model: Catalog id the trained model is stored under.
        base: Catalog id of the GLiNER model trained from.
        seed: Seeds the draw of examples, their order and the training.
        device: `mps` or `cpu`.
        training: Hyperparameters.
        corpora: Train splits.
        evaluate: Development splits to score the trained model on.
        limit: Documents per development split, all when `None`.
        raw: The file's contents, for the results.
    """

    name: str
    description: str
    model: str
    base: str
    seed: int
    device: str
    training: Hyperparameters
    corpora: tuple[CorpusRef, ...]
    evaluate: tuple[DatasetRef, ...]
    limit: int | None
    raw: dict[str, Any]


def load_train_config(path: Path, catalog: Catalog | None = None) -> TrainConfig:
    """Read and validate a training configuration file (see `parse_train_config`)."""
    with path.open("rb") as handle:
        return parse_train_config(tomllib.load(handle), catalog)


def parse_train_config(raw: dict[str, Any], catalog: Catalog | None = None) -> TrainConfig:
    """Validate a parsed training configuration.

    Args:
        raw: The TOML contents.
        catalog: The catalog naming the base model; the shipped one when omitted.

    Returns:
        The configuration.

    Raises:
        ValueError: On an unknown key; a corpus split that is not a train
            split, or an evaluated split that is not a development split; a
            model id the shipped catalog uses; a base that is not a GLiNER
            name model; or a hyperparameter out of range.
    """
    catalog = catalog or load_catalog()
    _known(raw, _KEYS, "the config")
    model = str(raw["model"])
    if not is_resource_id(model):
        msg = f"model {model!r} is no valid catalog id (lowercase letters, digits, '.', '-')"
        raise ValueError(msg)
    if model in load_catalog().resources:
        msg = f"model {model!r} is a shipped catalog entry; name the trained model otherwise"
        raise ValueError(msg)
    base = name_model(str(raw.get("base", "gliner-multi-v2.1")), catalog)
    if base.engine != "gliner":
        msg = f"base {base.id!r} runs on {base.engine}; only a GLiNER model can be trained here"
        raise ValueError(msg)
    device = str(raw.get("device", "mps"))
    if device not in DEVICES:
        msg = f"device must be one of {DEVICES}"
        raise ValueError(msg)
    corpora = tuple(_corpus(entry) for entry in raw.get("corpora", []))
    if not corpora:
        msg = "no corpora to train on"
        raise ValueError(msg)
    evaluate = dict(raw.get("evaluate", {}))
    _known(evaluate, frozenset({"datasets", "limit"}), "[evaluate]")
    # The run config's own checks (known dataset, split, no test split) apply.
    references = (
        parse_config(
            {"name": "evaluate", "datasets": evaluate["datasets"], "systems": {"rules": {}}}
        ).datasets
        if evaluate.get("datasets")
        else ()
    )
    for reference in references:
        if DATASETS[reference.id].splits[reference.split] is not Role.DEV:
            msg = f"{reference.id}/{reference.split} is not a development split"
            raise ValueError(msg)
    limit = evaluate.get("limit")
    return TrainConfig(
        name=str(raw["name"]),
        description=str(raw.get("description", "")),
        model=model,
        base=base.id,
        seed=int(raw.get("seed", 0)),
        device=device,
        training=_hyperparameters(dict(raw.get("training", {}))),
        corpora=corpora,
        evaluate=references,
        limit=None if limit is None else _positive(limit, "limit"),
        raw=raw,
    )


def _known(table: dict[str, Any], keys: frozenset[str], where: str) -> None:
    unknown = set(table) - keys
    if unknown:
        msg = f"unknown keys in {where}: {sorted(unknown)}"
        raise ValueError(msg)


def _positive(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        msg = f"{name} must be a positive whole number"
        raise ValueError(msg)
    return value


def _corpus(entry: dict[str, Any]) -> CorpusRef:
    _known(entry, frozenset({"id", "split", "examples"}), "a corpus entry")
    corpus_id, split = str(entry["id"]), str(entry["split"])
    spec = DATASETS.get(corpus_id)
    if spec is None:
        msg = f"unknown dataset {corpus_id!r}; choose from {sorted(DATASETS)}"
        raise ValueError(msg)
    if spec.splits.get(split) is not Role.TRAIN:
        msg = f"{corpus_id}/{split} is not a train split; training reads train splits only"
        raise ValueError(msg)
    examples = entry.get("examples")
    return CorpusRef(
        corpus_id, split, None if examples is None else _positive(examples, "examples")
    )


def _hyperparameters(table: dict[str, Any]) -> Hyperparameters:
    _known(table, _TRAINING_KEYS, "[training]")
    loss = str(table.get("loss", "ce"))
    if loss not in LOSSES:
        msg = f"loss must be one of {LOSSES}"
        raise ValueError(msg)
    focal = {"focal_alpha", "focal_gamma"} & set(table)
    if loss == "ce" and focal:
        msg = f"{sorted(focal)} apply to the focal loss only"
        raise ValueError(msg)
    alpha = float(table.get("focal_alpha", -1.0))
    gamma = float(table.get("focal_gamma", 0.0))
    if loss == "focal" and not (0.0 < alpha < 1.0 and gamma >= 0.0):
        msg = "the focal loss needs 0 < focal_alpha < 1 and focal_gamma >= 0"
        raise ValueError(msg)
    rates = {
        key: float(table.get(key, default))
        for key, default in (
            ("learning_rate", 1e-5),
            ("head_learning_rate", 5e-5),
        )
    }
    if not all(0.0 < rate < 1.0 for rate in rates.values()):
        msg = "learning rates must lie in (0, 1)"
        raise ValueError(msg)
    warmup_ratio = float(table.get("warmup_ratio", 0.1))
    if not 0.0 <= warmup_ratio <= 1.0:
        msg = "warmup_ratio must lie in [0, 1]"
        raise ValueError(msg)
    weight_decay = float(table.get("weight_decay", 0.01))
    if weight_decay < 0.0:
        msg = "weight_decay must not be negative"
        raise ValueError(msg)
    max_tokens = _positive(table.get("max_tokens", MAX_TOKENS), "max_tokens")
    if max_tokens > MAX_TOKENS:
        msg = f"max_tokens above {MAX_TOKENS} would train on longer texts than detection reads"
        raise ValueError(msg)
    return Hyperparameters(
        steps=_positive(table.get("steps"), "steps"),
        batch_size=_positive(table.get("batch_size", 8), "batch_size"),
        learning_rate=rates["learning_rate"],
        head_learning_rate=rates["head_learning_rate"],
        weight_decay=weight_decay,
        warmup_ratio=warmup_ratio,
        loss=loss,
        focal_alpha=alpha,
        focal_gamma=gamma,
        max_tokens=max_tokens,
        logging_steps=_positive(table.get("logging_steps", 10), "logging_steps"),
    )


def training_examples(
    config: TrainConfig, resource_root: Path, conversion: Conversion
) -> tuple[list[Example], dict[str, str]]:
    """Read the configured train splits and draw their examples.

    Returns:
        The examples, and the version of every dataset read, by catalog id.
    """
    catalog = load_catalog()
    examples: list[Example] = []
    versions: dict[str, str] = {}
    for reference in config.corpora:
        spec = DATASETS[reference.id]
        corpus = load_corpus(reference.id, reference.split, resource_root)
        converted = corpus_examples(corpus, spec, conversion, max_tokens=config.training.max_tokens)
        drawn = sample(converted, reference.examples, seed_for(config.seed, corpus.key))
        conversion.add_drawn(corpus.key, drawn)
        examples += drawn
        versions[spec.catalog_id] = catalog[spec.catalog_id].version
    return examples, versions


def seed_for(seed: int, purpose: str) -> int:
    """Derive a seed for one purpose, stable across runs and Python versions."""
    digest = hashlib.sha256(f"{seed}/{purpose}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


Fit = Callable[[Any, list[dict[str, Any]], TrainConfig, Path], dict[str, Any]]
"""Trains a loaded model in place on GLiNER examples; returns the trainer's log."""

Load = Callable[[Path, str, Catalog], Any]
"""Loads a catalog GLiNER model by id from a storage root, ready on the device."""


def train(
    config: TrainConfig,
    *,
    resource_root: Path,
    cache_dir: Path,
    progress: Progress = lambda _: None,
    fit: Fit | None = None,
    load: Load | None = None,
) -> dict[str, Any]:
    """Train, store and register a model, then score it on development data.

    The scores come from the stored model, loaded again through the root's
    catalog, so they also show that `rules+<model>` runs.

    Args:
        config: The training configuration.
        resource_root: Storage root holding `data/` and `models/`; the model
            is stored and listed there.
        cache_dir: Where the name models' output is cached.
        progress: Told what is running (no corpus text).
        fit: Trains the model; gliner's Trainer (seeded by it) by default.
        load: Loads the base and the trained model; from the catalog's files
            onto the configured device by default.

    Returns:
        The results, as the command line stores them in `<name>.json`.
    """
    load = load or _loader(config.device)
    conversion = Conversion()
    examples, data_versions = training_examples(config, resource_root, conversion)
    progress(f"{len(examples)} examples drawn from {len(config.corpora)} train splits")
    catalog = load_catalog(root=resource_root)
    model = load(resource_root, config.base, catalog)
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="gliner-training-") as work:
        log = (fit or fit_gliner)(model, [ex.to_gliner() for ex in examples], config, Path(work))
    seconds = time.perf_counter() - started
    progress(f"trained {config.training.steps} steps in {seconds:.0f} s")
    entry = store_model(model, config, resource_root, catalog, data_versions)
    del model
    catalog = load_catalog(root=resource_root)
    evaluation = (
        _evaluate(
            config,
            load(resource_root, config.model, catalog),
            resource_root,
            cache_dir,
            catalog,
            progress,
        )
        if config.evaluate
        else None
    )
    return {
        "schema": TRAINING_SCHEMA,
        "name": config.name,
        "description": config.description,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git": git_state(),
        "machine": {**machine(), "chip": _chip(), "device": config.device, **_packages()},
        "seed": config.seed,
        "config": config.raw,
        "base": {"id": config.base, "version": catalog[config.base].version},
        "datasets": data_versions,
        "examples": {"count": len(examples), **conversion.to_dict()},
        "training": {
            "steps": config.training.steps,
            "seconds": round(seconds, 1),
            "seconds_per_step": round(seconds / config.training.steps, 3),
            "log": log,
        },
        "model": entry,
        "evaluation": evaluation,
    }


def _loader(device: str) -> Load:
    def load(root: Path, model_id: str, catalog: Catalog) -> Any:
        model: Any = load_gliner_model(root, model_id, catalog=catalog)
        # The trainer switches to training mode itself; detection needs eval mode.
        return model.to(device).eval()

    return load


def fit_gliner(
    model: Any, examples: list[dict[str, Any]], config: TrainConfig, work: Path
) -> dict[str, Any]:
    """Train a GLiNER model in place with gliner's Trainer.

    Args:
        model: The loaded GLiNER model.
        examples: Examples in gliner's format (`Example.to_gliner`).
        config: The configuration.
        work: Scratch directory for the trainer; nothing is kept from it.

    Returns:
        The losses logged during training and the trainer's summary.
    """
    hyper = config.training
    arguments = model.create_training_args(
        output_dir=str(work),
        learning_rate=hyper.learning_rate,
        others_lr=hyper.head_learning_rate,
        weight_decay=hyper.weight_decay,
        others_weight_decay=hyper.weight_decay,
        focal_loss_alpha=hyper.focal_alpha,
        focal_loss_gamma=hyper.focal_gamma,
        # transformers calls the ratio deprecated, but gliner applies only the
        # ratio: warmup_steps passed through its arguments left no warm-up
        # in the learning rate log (transformers 5.12, gliner 0.2.29).
        warmup_ratio=hyper.warmup_ratio,
        per_device_train_batch_size=hyper.batch_size,
        max_steps=hyper.steps,
        logging_steps=hyper.logging_steps,
        use_cpu=config.device == "cpu",
        # Workers would be separate processes, each with its own copy of the tokenizer.
        dataloader_num_workers=0,
        # Pinned memory is a CUDA feature; on MPS it only warns.
        dataloader_pin_memory=False,
        save_strategy="no",
        seed=config.seed,
        data_seed=config.seed,
    )
    trainer = model.train_model(train_dataset=examples, eval_dataset=None, training_args=arguments)
    history = trainer.state.log_history
    return {
        "loss": [
            {"step": entry["step"], "loss": round(float(entry["loss"]), 4)}
            for entry in history
            if "loss" in entry
        ],
        "summary": {
            key: value
            for entry in history
            for key, value in entry.items()
            if key in {"train_runtime", "train_samples_per_second", "train_steps_per_second"}
        },
    }


def store_model(
    model: Any,
    config: TrainConfig,
    resource_root: Path,
    catalog: Catalog,
    data_versions: dict[str, str],
) -> dict[str, Any]:
    """Store the trained weights under the root and list them in its `trained.json`.

    Training changes the weights only, so the base model's `gliner_config.json`
    is stored beside them and the model loads exactly as its base does, with
    the base's tokenizer from the catalog. The config gliner writes itself
    would not do: it pins the indices of the special tokens gliner adds to
    the tokenizer, which the catalog's tokenizer does not hold yet, and
    names the local encoder folder the model was loaded with.

    Returns:
        The model's catalog entry.
    """
    base = catalog[config.base]
    target = base.directory(resource_root).with_name(config.model)
    staging = target.with_name(f".{config.model}.staging")
    shutil.rmtree(staging, ignore_errors=True)
    model.save_pretrained(staging / "saved", safe_serialization=True)
    (staging / "saved" / WEIGHTS).replace(staging / WEIGHTS)
    shutil.rmtree(staging / "saved")
    shutil.copyfile(base.directory(resource_root) / CONFIG, staging / CONFIG)
    shutil.rmtree(target, ignore_errors=True)
    staging.replace(target)
    corpora = [
        catalog[resource_id]
        for resource_id in dict.fromkeys(
            DATASETS[reference.id].catalog_id for reference in config.corpora
        )
    ]
    entry = {
        "id": config.model,
        "name": f"GLiNER fine-tuned on this machine ({config.name})",
        "kind": "model",
        "uses": ["ner"],
        "engine": base.engine,
        "trained": True,
        "source": f"experiments/results/{config.name}.json",
        "version": _sha256(target / WEIGHTS),
        "licence": "LicenseRef-Trained-Locally",
        "languages": sorted({DATASETS[reference.id].language for reference in config.corpora}),
        "requires": list(base.requires),
        "real_personal_data": any(corpus.real_personal_data for corpus in corpora),
        "notes": (
            f"Trained from {base.id} ({base.licence}) on "
            + ", ".join(
                f"{corpus.id}@{data_versions[corpus.id]} ({corpus.licence})" for corpus in corpora
            )
            + ". Local use only: never committed or published."
        ),
        "files": [
            {"path": name, "size": (target / name).stat().st_size, "sha256": _sha256(target / name)}
            for name in (CONFIG, WEIGHTS)
        ],
    }
    register(resource_root, entry)
    return entry


def register(resource_root: Path, entry: dict[str, Any]) -> None:
    """Add or replace a trained model's entry in the root's `trained.json`.

    Raises:
        ValueError: If the list would not load (see `resources.load_catalog`).
    """
    path = trained_catalog_path(resource_root)
    listed = (
        json.loads(path.read_text(encoding="utf-8"))
        if path.exists()
        else {"schema": CATALOG_SCHEMA, "resource": []}
    )
    listed["resource"] = [
        other for other in listed["resource"] if other.get("id") != entry["id"]
    ] + [entry]
    parse_catalog(listed, base=load_catalog())
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(path.name + ".part")
    staging.write_text(json.dumps(listed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    staging.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def _evaluate(
    config: TrainConfig,
    model: Any,
    resource_root: Path,
    cache_dir: Path,
    catalog: Catalog,
    progress: Progress,
) -> dict[str, Any]:
    """Score `rules+<model>` on the development splits with the stored model."""
    system = f"rules+{config.model}"
    run_config = parse_config(
        {
            "name": f"{config.name}-dev",
            "description": f"{system} after training ({config.name}).",
            "seed": config.seed,
            "datasets": [
                {"id": reference.id, "split": reference.split, "text": str(reference.text)}
                for reference in config.evaluate
            ],
            "systems": {system: {"model": config.model}},
        },
        catalog,
    )
    return run(
        run_config,
        resource_root=resource_root,
        cache_dir=cache_dir,
        load_model=lambda _: cast("SpanModel", model),
        progress=progress,
        limit=config.limit,
    )


def _chip() -> str:
    """The processor's name; on a Mac, the chip (`platform` reports only `arm`)."""
    if platform.system() == "Darwin":
        try:
            return subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return platform.processor()


def _packages() -> dict[str, str]:
    """Versions of the packages training runs on."""
    versions: dict[str, str] = {}
    for package in ("torch", "transformers", "accelerate", "gliner"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "absent"
    return versions


def write_training(results: dict[str, Any], folder: Path) -> Path:
    """Write `<name>.json`, and `<name>.md` with the development scores, into a folder."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{results['name']}.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if results["evaluation"] is not None:
        (folder / f"{results['name']}.md").write_text(
            markdown(results["evaluation"]), encoding="utf-8"
        )
    return path
