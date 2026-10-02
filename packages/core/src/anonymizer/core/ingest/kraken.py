"""OCR with kraken: baseline segmentation and PP-OCRv6 line recognition.

kraken reads a page in two steps. Its layout model (BLLA) finds each text
line as a baseline with a bounding polygon, whatever the hand or script, and
a recognizer reads each line whole. The recognizer is PP-OCRv6 medium,
trained on handwritten and printed lines in 44 languages, Czech and Slovak
among them; OnnxTR reads print well but no handwriting at all.

A line recognizer returns no word boxes, only the position of each character
along the baseline (its CTC cuts). kraken's own ALTO and hOCR output takes
the section of the line's bounding polygon from a word's first to its last
character, which spans the line's height but not the word's width: a cut
marks where the recognizer emitted a character, not where its ink ends, so
such a box clips about half of the first and the last letter. On the clean
scanned benchmark 1,910 of 1,928 words had ink outside these boxes, and
growing them by a share of their height reached the next line long before
it covered the letters (`python -m benchmark ocr-margin`). Each word is
therefore widened sideways to the middle of the spaces before and after it,
and the first and last word of a line to the ends of the line's polygon,
which the segmenter fits to the ink. The boxes of a line then tile it
without gaps, so a redaction covers the spaces beside a value as well. A
line whose characters carry no positions becomes one word over the whole
line, which redacts more than needed rather than leaving part of a value.

The model returns text in Unicode NFD (the form it was trained on). Lines
are split into words before normalization, since the cuts count NFD code
points; `layout.assemble` then normalizes each word to NFC.

Both models load from the catalog's local files, never from kraken's model
repository (which only its `kraken get` command reaches). Inference is
pinned to the CPU, as OnnxTR is: Lightning would otherwise pick a GPU or
Apple's MPS where present, and the results should not depend on the machine.
Lines are cut out of the page in the calling process rather than in a pool
of worker processes, which would start one Python per worker in the review
window.

The optional dependency is the `ocr-kraken` extra (`uv sync --group
ocr-kraken`); it is imported inside the loader, as GLiNER is. kraken needs
coremltools, which has wheels for macOS and Linux x86-64 only.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from anonymizer.core.ingest.ocr import OcrWord, PageImage
from anonymizer.core.resources import load_catalog, resource_status

SEGMENTATION_RESOURCE = "kraken-blla"
RECOGNITION_RESOURCE = "kraken-ppocr-v6-medium"
_SEGMENTATION_FILE = "blla.mlmodel"
_RECOGNITION_FILE = "medium.safetensors"
_WORD = re.compile(r"\S+")

BOX_MARGIN = 0.05
"""Share of a word box's height added on each side of it, once widened.

Measured on the clean scanned benchmark: 83 of 1,928 words kept ink outside
the widened boxes, 9 with this margin, none with 10 %; boxes reaching a word
on another line rose from 18 to 76 with it, and to 290 at 10 %.
"""


class KrakenEngine:
    """Reads a page with kraken's segmenter and recognizer (see `load_kraken_engine`)."""

    name = "kraken"
    box_margin = BOX_MARGIN

    def __init__(
        self,
        segmenter: Any,
        recognizer: Any,
        segmentation_config: Any,
        recognition_config: Any,
    ) -> None:
        self.segmenter = segmenter
        self.recognizer = recognizer
        self.segmentation_config = segmentation_config
        self.recognition_config = recognition_config

    def read(self, image: PageImage) -> list[OcrWord]:
        """Return the words kraken reads, a block per run of lines in one region.

        Args:
            image: The rendered page.

        Returns:
            Words with boxes in pixels of `image`, lines in kraken's reading order.
        """
        from PIL import Image  # pyright: ignore[reportMissingImports]

        picture = Image.frombytes("RGB", (image.width, image.height), image.samples)
        segmentation = self.segmenter.predict(picture, self.segmentation_config)
        if not segmentation.lines:
            return []
        records = self.recognizer.predict(picture, segmentation, self.recognition_config)
        return words_of_lines(records)


def words_of_lines(records: Iterable[Any]) -> list[OcrWord]:
    """Split kraken's line records into words, numbering blocks and lines.

    A block is a run of consecutive lines kraken placed in the same regions,
    so blocks and lines both grow in reading order and sorting by them keeps it.

    Args:
        records: kraken `ocr_record`s in reading order.

    Returns:
        The words of every line that read as anything.
    """
    words: list[OcrWord] = []
    block = -1
    previous_regions: object = object()
    for line, record in enumerate(records):
        regions = tuple(getattr(record, "regions", None) or ())
        if regions != previous_regions:
            block += 1
            previous_regions = regions
        words.extend(_line_words(record, block, line))
    return words


def _line_words(record: Any, block: int, line: int) -> list[OcrWord]:
    prediction: str = record.prediction
    if not prediction.strip():
        return []
    if not record.cuts:
        return [_whole_line(record, block, line)]
    matches = list(_WORD.finditer(prediction))
    sections = [record[match.start() : match.end()] for match in matches]
    boxes = _widened([_enclose(polygon) for _text, polygon, _confidence in sections], record)
    return [
        OcrWord(
            text=match.group(),
            box=box,
            confidence=float(confidence),
            block=block,
            line=line,
        )
        for match, box, (_text, _polygon, confidence) in zip(matches, boxes, sections, strict=True)
    ]


Box = tuple[float, float, float, float]


def _widened(boxes: list[Box], record: Any) -> list[Box]:
    """Widen a line's word boxes, left to right, to the middle of the spaces between them.

    The first word reaches the left end of the line's polygon and the last
    its right end. A box is never narrowed.
    """
    line_left, _top, line_right, _bottom = _enclose(record.boundary)
    widened: list[Box] = []
    for index, (x0, y0, x1, y1) in enumerate(boxes):
        left = line_left if index == 0 else (boxes[index - 1][2] + x0) / 2
        right = line_right if index == len(boxes) - 1 else (x1 + boxes[index + 1][0]) / 2
        widened.append((min(left, x0), y0, max(right, x1), y1))
    return widened


def _whole_line(record: Any, block: int, line: int) -> OcrWord:
    """One word over the whole line, for a record whose characters have no positions."""
    confidences = list(record.confidences)
    return OcrWord(
        text=" ".join(record.prediction.split()),
        box=_enclose(record.boundary),
        confidence=sum(confidences) / len(confidences) if confidences else 0.0,
        block=block,
        line=line,
    )


def _enclose(polygon: Sequence[Sequence[float]]) -> Box:
    """The axis-aligned box around a polygon's points, in pixels."""
    xs = [float(point[0]) for point in polygon]
    ys = [float(point[1]) for point in polygon]
    return (min(xs), min(ys), max(xs), max(ys))


def missing_kraken_files(root: Path) -> list[str]:
    """Return the catalog ids of the kraken models not stored under a root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).

    Returns:
        Ids in download order; empty when the engine can be loaded.
    """
    catalog = load_catalog()
    return [
        resource.id
        for resource in catalog.with_requirements(RECOGNITION_RESOURCE)
        if resource_status(resource, root) != "present"
    ]


def load_kraken_engine(root: Path) -> KrakenEngine:
    """Build the kraken engine from the catalog's files under a storage root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).

    Returns:
        A ready engine.

    Raises:
        FileNotFoundError: If a model is not stored.
        ImportError: If the `kraken` package is not installed.
    """
    missing = missing_kraken_files(root)
    if missing:
        msg = (
            f"OCR model files missing under {root}: {', '.join(missing)}; fetch them with: "
            f"uv run python scripts/download.py fetch {RECOGNITION_RESOURCE}"
        )
        raise FileNotFoundError(msg)
    catalog = load_catalog()
    segmentation_model = catalog[SEGMENTATION_RESOURCE].directory(root) / _SEGMENTATION_FILE
    recognition_model = catalog[RECOGNITION_RESOURCE].directory(root) / _RECOGNITION_FILE
    try:
        from kraken.configs import (  # pyright: ignore[reportMissingImports]
            RecognitionInferenceConfig,
            SegmentationInferenceConfig,
        )
        from kraken.tasks import (  # pyright: ignore[reportMissingImports]
            RecognitionTaskModel,
            SegmentationTaskModel,
        )
    except ImportError as error:
        msg = "OCR needs the optional 'ocr-kraken' dependencies: uv sync --group ocr-kraken"
        raise ImportError(msg) from error
    cpu = {"accelerator": "cpu", "device": 1}
    return KrakenEngine(
        segmenter=SegmentationTaskModel.load_model(segmentation_model),
        recognizer=RecognitionTaskModel.load_model(recognition_model),
        segmentation_config=SegmentationInferenceConfig(**cpu),
        recognition_config=RecognitionInferenceConfig(num_line_workers=0, **cpu),
    )
