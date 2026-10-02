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
```

A test split is refused unless the stage is `final`: thresholds and labels are
tuned on development data, and the test data is read once, for the final
table.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from anonymizer.core.types import EntityType

from experiments.datasets import DATASETS, Role, TextForm
from experiments.systems import SystemConfig, parse_system

STAGES = ("dev", "final")
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


def load_config(path: Path) -> RunConfig:
    """Read and validate a run configuration file.

    Raises:
        ValueError: If the file is invalid (see `parse_config`).
    """
    with path.open("rb") as handle:
        return parse_config(tomllib.load(handle))


def parse_config(raw: dict[str, Any]) -> RunConfig:
    """Validate a parsed run configuration.

    Args:
        raw: The TOML contents.

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
    systems = tuple(parse_system(name, table) for name, table in raw.get("systems", {}).items())
    if not systems:
        msg = "no systems"
        raise ValueError(msg)
    names = {system.name for system in systems}
    compare = tuple((str(pair[0]), str(pair[1])) for pair in raw.get("compare", []))
    for pair in compare:
        if not set(pair) <= names:
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
        systems=systems,
        types=None if types is None else frozenset(EntityType(kind) for kind in types),
        compare=compare,
        raw=raw,
    )


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
