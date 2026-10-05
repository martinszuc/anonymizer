"""The OCR engines a client can choose by name.

Each entry loads one engine from the catalog's models under a storage root.
The command line, the review window and the benchmark offer this list, so an
engine added here reaches all of them.
"""

from __future__ import annotations

import importlib.util
import logging
from collections.abc import Callable
from pathlib import Path

from anonymizer.core.ingest import kraken, onnxtr
from anonymizer.core.ingest.ocr import OcrEngine
from anonymizer.core.log import step
from anonymizer.core.resources import load_catalog, missing_resources

log = logging.getLogger(__name__)

OCR_ENGINES: dict[str, Callable[[Path], OcrEngine]] = {
    "onnxtr": onnxtr.load_onnxtr_engine,
    "kraken": kraken.load_kraken_engine,
}
"""Engine loaders by name."""

OCR_ENGINE_RESOURCES: dict[str, tuple[str, ...]] = {
    "onnxtr": (onnxtr.DETECTION_RESOURCE, onnxtr.RECOGNITION_RESOURCE),
    "kraken": (kraken.SEGMENTATION_RESOURCE, kraken.RECOGNITION_RESOURCE),
}
"""The catalog ids each engine loads, in download order, for versions and download hints."""

_PACKAGES = {"onnxtr": "onnxtr", "kraken": "kraken"}


def ocr_engine_installed(name: str) -> bool:
    """Whether an engine's optional dependencies are installed, checked without importing them.

    Args:
        name: A key of `OCR_ENGINES`.

    Returns:
        `True` if the engine's package can be imported.
    """
    try:
        return importlib.util.find_spec(_PACKAGES[name]) is not None
    except (ImportError, ValueError):
        # find_spec raises for a module that is present but broken or blocked.
        return False


def missing_ocr_files(name: str, root: Path) -> list[str]:
    """Return the catalog ids of an engine's models not stored under a root.

    Args:
        name: A key of `OCR_ENGINES`.
        root: Storage root holding `models/` (see `scripts/download.py`).

    Returns:
        Ids in download order; empty when the engine can be loaded.
    """
    return missing_resources(load_catalog(), OCR_ENGINE_RESOURCES[name][-1], root)


def load_ocr_engine(name: str, root: Path) -> OcrEngine:
    """Load an OCR engine by name.

    Args:
        name: A key of `OCR_ENGINES`.
        root: Storage root holding `models/` (see `scripts/download.py`).

    Returns:
        The ready engine.

    Raises:
        ValueError: If no engine has that name.
        FileNotFoundError: If its models are not stored.
        ImportError: If its optional dependencies are not installed.
    """
    if name not in OCR_ENGINES:
        msg = f"unknown OCR engine {name!r}; choose from {sorted(OCR_ENGINES)}"
        raise ValueError(msg)
    with step(log, "load OCR engine", done_level=logging.INFO, engine=name):
        return OCR_ENGINES[name](root)
