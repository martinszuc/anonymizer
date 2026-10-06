"""OCR with OnnxTR: docTR's detector and a multilingual recognizer on onnxruntime.

OnnxTR finds word boxes (FAST) and reads each word (PARSeq). Its default
recognizer uses a French vocabulary without háček letters, so the catalog
pins the maintainer's multilingual model, whose 195-character vocabulary
holds every Czech and Slovak letter.

Both models load from the catalog's local files. OnnxTR downloads any model
it is not handed (its orientation classifiers, for instance, when it reads
skewed pages), so the loader turns those classifiers off and replaces its
download function with one that refuses: a model missing from the catalog
is an error, never a fetch. Inference is pinned to onnxruntime's CPU
provider: the default list on macOS starts with CoreML, which fails to
build the recognizer, and includes Azure's, which runs models on remote
endpoints; the CPU gives the same results on every machine.

Pages are read without assuming straight text: OnnxTR then measures each
word as a rotated box and straightens it before reading. Read as straight,
a scan skewed by 3 degrees lost half its text to misread and misordered
words in the scanned benchmark; read this way it stayed under one per cent.
A rotated word comes back as four corners, and its box is the axis-aligned
rectangle around them, which encloses the tilted word.

The optional dependency is the `ocr-onnxtr` extra (`uv sync --group
ocr-onnxtr`); it is imported inside the loader, as GLiNER is.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from anonymizer.core.ingest.ocr import OCR_BOX_MARGIN, OcrWord, PageImage
from anonymizer.core.resources import load_catalog, missing_resources

DETECTION_RESOURCE = "onnxtr-fast-base"
RECOGNITION_RESOURCE = "onnxtr-parseq-multilingual-v1"
_MODEL_FILE = "model.onnx"
_CONFIG_FILE = "config.json"
_CHANNELS = 3
_CPU_PROVIDER = "CPUExecutionProvider"
# OnnxTR imports huggingface_hub; this keeps it from reaching the network.
_OFFLINE_VARIABLES = ("HF_HUB_OFFLINE",)


class OnnxtrEngine:
    """Reads a page with an OnnxTR predictor (see `load_onnxtr_engine`)."""

    name = "onnxtr"
    box_margin = OCR_BOX_MARGIN

    def __init__(self, predictor: Any) -> None:
        self.predictor = predictor

    def read(self, image: PageImage) -> list[OcrWord]:
        """Return the words OnnxTR reads, numbered by its blocks and lines.

        Args:
            image: The rendered page.

        Returns:
            Words with boxes in pixels of `image`, in OnnxTR's reading order.
        """
        import numpy as np  # pyright: ignore[reportMissingImports]

        pixels = np.frombuffer(image.samples, dtype=np.uint8)
        page = self.predictor([pixels.reshape(image.height, image.width, _CHANNELS)]).pages[0]
        words: list[OcrWord] = []
        line_number = 0
        for block_number, block in enumerate(page.blocks):
            for line in block.lines:
                words.extend(
                    OcrWord(
                        text=word.value,
                        box=_pixels(word.geometry, image),
                        confidence=float(word.confidence),
                        block=block_number,
                        line=line_number,
                    )
                    for word in line.words
                )
                line_number += 1
        return words


def _pixels(geometry: Any, image: PageImage) -> tuple[float, float, float, float]:
    """Enclose OnnxTR's relative corner points, two or four, in a box in pixels."""
    xs = [float(x) for x, _ in geometry]
    ys = [float(y) for _, y in geometry]
    return (
        min(xs) * image.width,
        min(ys) * image.height,
        max(xs) * image.width,
        max(ys) * image.height,
    )


def missing_onnxtr_files(root: Path) -> list[str]:
    """Return the catalog ids of the OnnxTR models not stored under a root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).

    Returns:
        Ids in download order; empty when the engine can be loaded.
    """
    return missing_resources(load_catalog(), RECOGNITION_RESOURCE, root)


def load_onnxtr_engine(root: Path) -> OnnxtrEngine:
    """Build the OnnxTR engine from the catalog's files under a storage root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).

    Returns:
        A ready engine.

    Raises:
        FileNotFoundError: If a model is not stored.
        ImportError: If the `onnxtr` package is not installed.
    """
    missing = missing_onnxtr_files(root)
    if missing:
        msg = (
            f"OCR model files missing under {root}: {', '.join(missing)}; fetch them with: "
            f"uv run python scripts/download.py fetch {RECOGNITION_RESOURCE}"
        )
        raise FileNotFoundError(msg)
    catalog = load_catalog()
    detection = catalog[DETECTION_RESOURCE].directory(root)
    recognition = catalog[RECOGNITION_RESOURCE].directory(root)
    for variable in _OFFLINE_VARIABLES:
        os.environ[variable] = "1"
    try:
        from onnxtr.models import engine as onnxtr_engine  # pyright: ignore[reportMissingImports]
        from onnxtr.models import (  # pyright: ignore[reportMissingImports]
            fast_base,
            ocr_predictor,
            parseq,
        )
    except ImportError as error:
        msg = "OCR needs the optional 'ocr-onnxtr' dependencies: uv sync --group ocr-onnxtr"
        raise ImportError(msg) from error
    vocab = json.loads((recognition / _CONFIG_FILE).read_text(encoding="utf-8"))["vocab"]
    onnxtr_engine.download_from_url = _refuse_download  # pyright: ignore[reportPrivateImportUsage]
    cpu = onnxtr_engine.EngineConfig(providers=[_CPU_PROVIDER])
    predictor = ocr_predictor(
        det_arch=fast_base(str(detection / _MODEL_FILE), engine_cfg=cpu),
        reco_arch=parseq(str(recognition / _MODEL_FILE), engine_cfg=cpu, vocab=vocab),
        assume_straight_pages=False,
        detect_orientation=False,
        straighten_pages=False,
        detect_language=False,
        disable_page_orientation=True,
        disable_crop_orientation=True,
    )
    return OnnxtrEngine(predictor)


def _refuse_download(url: str, *args: Any, **kwargs: Any) -> str:
    """Stand in for OnnxTR's downloader, which must never run."""
    del args, kwargs
    msg = f"OnnxTR tried to download {url}; every model must come from the resource catalog"
    raise RuntimeError(msg)
