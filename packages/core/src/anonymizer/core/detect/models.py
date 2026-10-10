"""The name models a client can choose by catalog id.

A name model is a catalog entry used for `ner` whose `engine` has a loader
here. A fine-tuned model of a known engine is therefore only a catalog entry:
the command line, the review window, the benchmark and the experiments offer
every such entry. A model trained on this machine is an entry of its storage
root's `models/trained.json`, so a client that knows the root reads its
catalog with `load_catalog(root=...)`; the functions taking a root do so
when given no catalog. A new kind of model (a token classifier, say) adds one
loader to `NAME_MODEL_ENGINES` and the package that runs it.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from anonymizer.core.detect.base import Detector
from anonymizer.core.detect.gliner import GLINER_RESOURCE, load_gliner_detector
from anonymizer.core.resources import Catalog, Resource, load_catalog, missing_resources

DEFAULT_NAME_MODEL = GLINER_RESOURCE
"""The model `--ner` and the window use unless another is chosen."""

NAME_MODEL_ALIASES = {"gliner": DEFAULT_NAME_MODEL}
"""Earlier names of a model, still accepted, so configs and results naming
the system `rules+gliner` stay valid."""


@dataclass(frozen=True)
class NameModelEngine:
    """How models of one engine are loaded.

    Attributes:
        load: Builds the detector from a storage root, a catalog id and the catalog.
        package: The importable package the engine needs, checked without importing it.
        group: The optional dependency group that installs it (`uv sync --group <group>`).
    """

    load: Callable[[Path, str, Catalog], Detector]
    package: str
    group: str


NAME_MODEL_ENGINES: dict[str, NameModelEngine] = {
    "gliner": NameModelEngine(
        lambda root, model_id, catalog: load_gliner_detector(root, model_id, catalog=catalog),
        package="gliner",
        group="ner",
    ),
}
"""Loaders by the catalog's `engine` field."""


def name_models(catalog: Catalog | None = None) -> list[Resource]:
    """Return the catalog's name models, in catalog order.

    Args:
        catalog: The resource catalog; the one shipped with the core when omitted.

    Returns:
        Every model used for `ner` whose engine has a loader.
    """
    catalog = catalog or load_catalog()
    return [
        resource
        for resource in catalog.resources.values()
        if "ner" in resource.uses and resource.engine in NAME_MODEL_ENGINES
    ]


def name_model(model_id: str, catalog: Catalog | None = None) -> Resource:
    """Return a name model's catalog entry, accepting an earlier name (`gliner`).

    Args:
        model_id: A catalog id from `name_models`, or a key of `NAME_MODEL_ALIASES`.
        catalog: The resource catalog; the one shipped with the core when omitted.

    Returns:
        The catalog entry.

    Raises:
        ValueError: If no name model has that id.
    """
    models = {resource.id: resource for resource in name_models(catalog)}
    resolved = NAME_MODEL_ALIASES.get(model_id, model_id)
    if resolved not in models:
        msg = f"unknown name model {model_id!r}; choose from {sorted(models)}"
        raise ValueError(msg)
    return models[resolved]


def name_model_engine(model_id: str, catalog: Catalog | None = None) -> NameModelEngine:
    """Return the engine that runs a name model.

    Raises:
        ValueError: If no name model has that id.
    """
    # name_models keeps only entries whose engine has a loader.
    return NAME_MODEL_ENGINES[name_model(model_id, catalog).engine or ""]


def name_model_installed(model_id: str, catalog: Catalog | None = None) -> bool:
    """Whether a name model's optional dependencies are installed, checked without importing them.

    Importing them would load PyTorch, which takes seconds: too slow for a status check.

    Args:
        model_id: A name model's catalog id.
        catalog: The resource catalog; the one shipped with the core when omitted.

    Returns:
        `True` if the engine's package can be imported.

    Raises:
        ValueError: If no name model has that id.
    """
    package = name_model_engine(model_id, catalog).package
    try:
        return importlib.util.find_spec(package) is not None
    except (ImportError, ValueError):
        # find_spec raises for a module that is present but broken or blocked.
        return False


def missing_name_model_files(
    model_id: str, root: Path, catalog: Catalog | None = None
) -> list[str]:
    """Return the catalog ids of a name model's resources not stored under a root.

    Args:
        model_id: A name model's catalog id.
        root: Storage root holding `models/` (see `scripts/download.py`).
        catalog: The resource catalog; the shipped one and the root's
            trained models when omitted.

    Returns:
        Ids in download order; empty when the model can be loaded.

    Raises:
        ValueError: If no name model has that id.
    """
    catalog = catalog or load_catalog(root=root)
    return missing_resources(catalog, name_model(model_id, catalog).id, root)


def load_name_model(model_id: str, root: Path, catalog: Catalog | None = None) -> Detector:
    """Load a name model by catalog id.

    Args:
        model_id: A name model's catalog id, or an earlier name (`gliner`).
        root: Storage root holding `models/` (see `scripts/download.py`).
        catalog: The resource catalog; the shipped one and the root's
            trained models when omitted.

    Returns:
        The ready detector, named after the model; give it to
        `pipeline.build_detector`.

    Raises:
        ValueError: If no name model has that id.
        FileNotFoundError: If its files are not stored.
        ImportError: If its optional dependencies are not installed.
    """
    catalog = catalog or load_catalog(root=root)
    resource = name_model(model_id, catalog)
    return name_model_engine(resource.id, catalog).load(root, resource.id, catalog)


def system_model(system: str, catalog: Catalog | None = None) -> str | None:
    """Return the catalog id of the name model an evaluated system runs; `None` for `rules`.

    The benchmark and the experiments name a system `rules` or
    `rules+<model>`, the model by catalog id or by an earlier name, so
    `rules+gliner` and `rules+gliner-multi-v2.1` run the same model.

    Args:
        system: The system's name.
        catalog: The resource catalog; the one shipped with the core when
            omitted, which lists no trained model.

    Returns:
        The model's catalog id, or `None` for the rules alone.

    Raises:
        ValueError: If the name is neither `rules` nor `rules+<name model>`.
    """
    if system == "rules":
        return None
    prefix, plus, model_id = system.partition("+")
    if prefix != "rules" or not plus:
        msg = f"unknown system {system!r}; choose rules or rules+<name model>"
        raise ValueError(msg)
    return name_model(model_id, catalog).id
