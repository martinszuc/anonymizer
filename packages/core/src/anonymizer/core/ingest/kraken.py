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
therefore widened sideways towards the middle of the spaces before and after
it, and the first and last word of a line towards the ends of the line's
polygon, which the segmenter fits to the ink; by at most `MAX_WIDENING` of
its height, which covers half a letter. Unbounded, a word beside a redaction
box spread over the box when the leak check re-read the page, since the box
reads as no word, and the check rightly reported a word under a box. A line
whose characters carry no positions becomes one word over the whole line,
which redacts more than needed rather than leaving part of a value.

Redaction boxes confuse the re-read of a redacted page in two more ways.
The segmenter stretches a line's polygon over a black bar above or below
it, so a word's box reached into the bar, and the recognizer reads a bar as
a stray letter. A box crossed by a band of solid ink rows at least
`MIN_BAR` of its height tall is therefore cut to the stretch of rows beside
the band that holds the most ink, and a word whose box is solid throughout
is dropped. Letters never fill a row of their box and an underline or a
table rule is thinner than a bar, so a first reading of a page is
unchanged, as the benchmark confirms. A word read across a bar as one
(`IČO ███ Brno` read as one word) still covers it.

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

import dataclasses
import re
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from anonymizer.core.ingest.ocr import OcrWord, PageImage
from anonymizer.core.resources import load_catalog, missing_resources

SEGMENTATION_RESOURCE = "kraken-blla"
RECOGNITION_RESOURCE = "kraken-ppocr-v6-medium"
_SEGMENTATION_FILE = "blla.mlmodel"
_RECOGNITION_FILE = "medium.safetensors"
_WORD = re.compile(r"\S+")

Box = tuple[float, float, float, float]

MAX_WIDENING = 0.5
"""Most a word box is widened sideways on each side, as a share of its height."""

SOLID_INK = 0.95
"""Share of dark pixels above which a row of a word's box is solid ink."""

MIN_BAR = 0.25
"""Least height of a band of solid rows, as a share of the box's, that is a bar."""

# A pixel darker than this grey level is ink, as in the scanned benchmark.
_DARK = 100

BOX_MARGIN = 0.05
"""Share of a word box's height added on each side of it, once widened (see findings)."""


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
        import numpy as np  # pyright: ignore[reportMissingImports]
        from PIL import Image  # pyright: ignore[reportMissingImports]

        picture = Image.frombytes("RGB", (image.width, image.height), image.samples)
        segmentation = self.segmenter.predict(picture, self.segmentation_config)
        if not segmentation.lines:
            return []
        records = self.recognizer.predict(picture, segmentation, self.recognition_config)
        pixels = np.frombuffer(image.samples, dtype=np.uint8).reshape(image.height, image.width, 3)
        ink = pixels.min(axis=2) < _DARK
        words: list[OcrWord] = []
        for word in words_of_lines(records):
            box = _beside_bars(word.box, ink)
            if box is not None:
                words.append(dataclasses.replace(word, box=box))
        return words


def _beside_bars(box: Box, ink: Any) -> Box | None:
    """Cut a box crossed by a black bar to the rows beside it holding most ink.

    Args:
        box: Word box in pixels.
        ink: Boolean picture, true where a pixel is ink.

    Returns:
        The box, cut if a bar crosses it; `None` if it lies inside a bar.
    """
    x0, y0, x1, y1 = box
    left, right = max(int(x0), 0), max(int(x1 + 0.5), 0)
    top, bottom = max(int(y0), 0), max(int(y1 + 0.5), 0)
    window = ink[top:bottom, left:right]
    if window.size == 0:
        return box
    row_ink = window.sum(axis=1)
    solid = row_ink >= SOLID_INK * window.shape[1]
    bars = [(start, end) for start, end in _runs(solid) if end - start >= MIN_BAR * len(solid)]
    if not bars:
        return box
    in_bar = [False] * len(solid)
    for start, end in bars:
        in_bar[start:end] = [True] * (end - start)
    beside = [(start, end) for start, end in _runs([not row for row in in_bar])]
    if not beside:
        return None
    start, end = max(beside, key=lambda run: int(row_ink[run[0] : run[1]].sum()))
    return (x0, max(y0, top + start), x1, min(y1, top + end))


def _runs(flags: Sequence[bool]) -> list[tuple[int, int]]:
    """Return the `(start, end)` of every run of true values."""
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, flag in enumerate([*flags, False]):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            runs.append((start, index))
            start = None
    return runs


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


def _widened(boxes: list[Box], record: Any) -> list[Box]:
    """Widen a line's word boxes, left to right, towards the middle of the spaces between them.

    The first word reaches towards the left end of the line's polygon and the
    last towards its right end, each side by at most `MAX_WIDENING` of the
    box's height. A box is never narrowed.
    """
    line_left, _top, line_right, _bottom = _enclose(record.boundary)
    widened: list[Box] = []
    for index, (x0, y0, x1, y1) in enumerate(boxes):
        reach = MAX_WIDENING * (y1 - y0)
        left = line_left if index == 0 else (boxes[index - 1][2] + x0) / 2
        right = line_right if index == len(boxes) - 1 else (x1 + boxes[index + 1][0]) / 2
        widened.append((min(max(left, x0 - reach), x0), y0, max(min(right, x1 + reach), x1), y1))
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
    return missing_resources(load_catalog(), RECOGNITION_RESOURCE, root)


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
