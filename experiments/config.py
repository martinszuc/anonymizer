"""Run configurations: which systems on which splits, read from TOML.

```toml
name = "rq1-dev"            # names the results files
stage = "dev"               # "dev", or "final" to allow test splits
seed = 20261002             # bootstrap resamples
resamples = 1000
types = ["person"]          # optional: score only these types
compare = [["rules", "rules+gliner"]]   # paired bootstrap, baseline first

[[datasets]]
id = "cnec-2.0"
split = "dtest"             # always explicit, never defaulted
# text = "tokens"           # optional, see datasets.TextForm

[systems.rules]
model = "none"

[systems."rules+gliner"]
model = "gliner"            # every other option as shipped

[systems."rules+gliner-cs-sk-ce"]
model = "gliner-cs-sk-ce"
seeds = [1, 2]              # also runs gliner-cs-sk-ce-s1 and -s2 (see below)
```

`seeds` names the replicates of a trained model, the same config trained
again with `python -m experiments train --seed N`, stored as `<model>-sN`.
The system runs once per model, as `<system>` and `<system>-sN`, each with
its own scores, and the results add the mean and spread across them
(`seeds.py`); a comparison of two such systems is also made seed by seed.

A test split is refused unless the stage is `final`: thresholds and labels are
tuned on development data, and the test data is read once, for the final
table.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from anonymizer.core.resources import Catalog
from anonymizer.core.types import EntityType

from experiments.datasets import DATASETS, Role, TextForm
from experiments.systems import SystemConfig, parse_system

STAGES = ("dev", "final")
BASE_REPLICATE = "base"
"""Names the replicate trained with the training config's own seed."""
_KEYS = frozenset(
    {"name", "description", "stage", "seed", "resamples", "types", "compare", "datasets", "systems"}
)


@dataclass(frozen=True)
class DatasetRef:
    """One split of a dataset to run on, and how its text is built (`TextForm`)."""

    id: str
    split: str
    text: TextForm = TextForm.WRITTEN


@dataclass(frozen=True)
class RunConfig:
    """A parsed run configuration.

    Attributes:
        name: Names the results files.
        description: Free text, copied into the results.
        stage: `dev` or `final`.
        seed: Seed of the bootstrap resamples.
        resamples: Number of bootstrap resamples.
        datasets: Splits to run on.
        systems: Systems to run, in table order.
        types: Types to score, or `None` for every type a corpus annotates.
        compare: Pairs of system names (baseline, candidate).
        raw: The file's contents, for the results.
        replicates: The systems run once per seed, by system name.
    """

    name: str
    description: str
    stage: str
    seed: int
    resamples: int
    datasets: tuple[DatasetRef, ...]
    systems: tuple[SystemConfig, ...]
    types: frozenset[EntityType] | None
    compare: tuple[tuple[str, str], ...]
    raw: dict[str, Any]
    replicates: dict[str, Replicates] = field(default_factory=dict)


@dataclass(frozen=True)
class Replicates:
    """A system run with a trained model and with its replicates (`seeds`)."""

    system: str
    seeds: tuple[int, ...]

    def members(self) -> dict[str, str]:
        """Return the system of each replicate: `base`, then `s<N>` per seed."""
        return {
            BASE_REPLICATE: self.system,
            **{f"s{seed}": replicate_id(self.system, seed) for seed in self.seeds},
        }


def replicate_id(name: str, seed: int) -> str:
    """Name a replicate: a model, a training run or a system trained with another seed."""
    return f"{name}-s{seed}"


def load_config(path: Path, catalog: Catalog | None = None) -> RunConfig:
    """Read and validate a run configuration file.

    Args:
        path: The TOML file.
        catalog: The catalog naming the models; the shipped one when omitted,
            `load_catalog(root=...)` to allow the root's trained models.

    Raises:
        ValueError: If the file is invalid (see `parse_config`).
    """
    with path.open("rb") as handle:
        return parse_config(tomllib.load(handle), catalog)


def parse_config(raw: dict[str, Any], catalog: Catalog | None = None) -> RunConfig:
    """Validate a parsed run configuration.

    Args:
        raw: The TOML contents.
        catalog: The catalog naming the models; the shipped one when omitted.

    Returns:
        The configuration.

    Raises:
        ValueError: On an unknown key, dataset, split, system or type, a test
            split outside the final stage, or a comparison naming an unknown
            system.
    """
    unknown = set(raw) - _KEYS
    if unknown:
        msg = f"unknown keys {sorted(unknown)}"
        raise ValueError(msg)
    stage = str(raw.get("stage", "dev"))
    if stage not in STAGES:
        msg = f"stage must be one of {STAGES}"
        raise ValueError(msg)
    datasets = tuple(_dataset(entry, stage) for entry in raw.get("datasets", []))
    if not datasets:
        msg = "no datasets"
        raise ValueError(msg)
    replicates: dict[str, Replicates] = {}
    systems: list[SystemConfig] = []
    for name, table in raw.get("systems", {}).items():
        options = {key: value for key, value in table.items() if key != "seeds"}
        system = parse_system(name, options, catalog)
        systems.append(system)
        if "seeds" not in table:
            continue
        group = _replicates(name, table["seeds"], system)
        replicates[name] = group
        model = system.model_names[0]
        systems += [
            parse_system(
                replicate_id(name, seed), {**options, "model": replicate_id(model, seed)}, catalog
            )
            for seed in group.seeds
        ]
    if not systems:
        msg = "no systems"
        raise ValueError(msg)
    names = [system.name for system in systems]
    if len(set(names)) < len(names):
        msg = "a replicate's system name is also configured as a system of its own"
        raise ValueError(msg)
    compare = tuple((str(pair[0]), str(pair[1])) for pair in raw.get("compare", []))
    for pair in compare:
        if not set(pair) <= set(names):
            msg = f"comparison {list(pair)} names a system that is not configured"
            raise ValueError(msg)
    types = raw.get("types")
    resamples = int(raw.get("resamples", 1000))
    if resamples < 1:
        msg = "resamples must be positive"
        raise ValueError(msg)
    return RunConfig(
        name=str(raw["name"]),
        description=str(raw.get("description", "")),
        stage=stage,
        seed=int(raw.get("seed", 0)),
        resamples=resamples,
        datasets=datasets,
        systems=tuple(systems),
        types=None if types is None else frozenset(EntityType(kind) for kind in types),
        compare=compare,
        raw=raw,
        replicates=replicates,
    )


def _replicates(name: str, seeds: object, system: SystemConfig) -> Replicates:
    if (
        not isinstance(seeds, list)
        or not seeds
        or not all(isinstance(seed, int) and not isinstance(seed, bool) for seed in seeds)
        or min(seeds) < 0
        or len(set(seeds)) < len(seeds)
    ):
        msg = f"system {name!r}: seeds must be a list of different whole numbers, none negative"
        raise ValueError(msg)
    if len(system.model_names) != 1:
        msg = f"system {name!r}: seeds need exactly one name model, a trained one"
        raise ValueError(msg)
    return Replicates(name, tuple(seeds))


def _dataset(entry: dict[str, Any], stage: str) -> DatasetRef:
    if not {"id", "split"} <= set(entry) <= {"id", "split", "text"}:
        msg = f"a dataset entry needs 'id' and 'split' (and may set 'text'), got {sorted(entry)}"
        raise ValueError(msg)
    reference = DatasetRef(
        str(entry["id"]), str(entry["split"]), TextForm(entry.get("text", TextForm.WRITTEN))
    )
    spec = DATASETS.get(reference.id)
    if spec is None:
        msg = f"unknown dataset {reference.id!r}; choose from {sorted(DATASETS)}"
        raise ValueError(msg)
    role = spec.splits.get(reference.split)
    if role is None:
        msg = f"{reference.id} has no split {reference.split!r}; choose from {sorted(spec.splits)}"
        raise ValueError(msg)
    if role is Role.TEST and stage != "final":
        msg = f'{reference.id}/{reference.split} is test data; set stage = "final" to report it'
        raise ValueError(msg)
    return reference
