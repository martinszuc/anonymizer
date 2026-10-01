"""The OCR engines a client can choose by name.

Each entry loads one engine from the catalog's models under a storage root.
The command line, the review window and the benchmark offer this list, so an
engine added here reaches all of them.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from anonymizer.core.ingest.ocr import OcrEngine
from anonymizer.core.ingest.onnxtr import (
    DETECTION_RESOURCE,
    RECOGNITION_RESOURCE,
    load_onnxtr_engine,
)

OCR_ENGINES: dict[str, Callable[[Path], OcrEngine]] = {"onnxtr": load_onnxtr_engine}
"""Engine loaders by name."""

OCR_ENGINE_RESOURCES: dict[str, tuple[str, ...]] = {
    "onnxtr": (DETECTION_RESOURCE, RECOGNITION_RESOURCE),
}
"""The catalog ids each engine loads, for recording versions and download hints."""


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
    return OCR_ENGINES[name](root)
