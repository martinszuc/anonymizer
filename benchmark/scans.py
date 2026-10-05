"""Scanned variants of the benchmark documents, with ground truth from the original.

A born-digital benchmark PDF is rendered to a greyscale picture per page,
degraded (`degrade.Level`) and written as a picture-only PDF: no text layer,
links or metadata survive, as on paper. The original's text layer knows every
word and its box, so it is the ground truth of what OCR should read; under
skew each box is moved with the ink and kept as the four corners of a
rotated rectangle.
"""

from __future__ import annotations

import functools
import io
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pymupdf
from anonymizer.core.ingest import OCR_BOX_MARGIN, OcrWord, PageImage, load_document
from anonymizer.core.types import BBox, Word
from PIL import Image

from benchmark.degrade import Level

Corners = tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]
"""A word's box on the scanned page, in points: top left, top right, bottom right, bottom left."""

# Grey levels below this are ink; the scans are black text on white.
INK_LEVEL = 128


@dataclass(frozen=True)
class TruthWord:
    """A word of the original and where it lies on the scanned page.

    Attributes:
        text: The word.
        corners: Its box moved with the ink, in points.
        block: Block number in the original's reading order.
        line: Line number in the original's reading order.
    """

    text: str
    corners: Corners
    block: int
    line: int

    @property
    def bbox(self) -> BBox:
        """The axis-aligned box enclosing the corners."""
        xs = [x for x, _ in self.corners]
        ys = [y for _, y in self.corners]
        return BBox(min(xs), min(ys), max(xs), max(ys))


@dataclass(frozen=True)
class TruthPage:
    """What a perfect reader would read on one scanned page.

    Attributes:
        text: The original's page text.
        words: Its words, offsets as in `text`.
        starts: Each word's offset into `text`.
        width: Page width in points.
        height: Page height in points.
    """

    text: str
    words: tuple[TruthWord, ...]
    starts: tuple[int, ...]
    width: float
    height: float


def scan_document(born_digital: Path, level: Level, destination: Path) -> list[TruthPage]:
    """Write a degraded, picture-only copy of a PDF and return its ground truth.

    Args:
        born_digital: The generated benchmark PDF.
        level: The degradation to apply.
        destination: Where to write the scanned copy.

    Returns:
        One ground-truth page per page.
    """
    original = load_document(born_digital)
    truth: list[TruthPage] = []
    with pymupdf.open(born_digital) as source:
        scanned = pymupdf.open()
        for page in original.pages:
            pdf_page = source.load_page(page.index)
            rendered = pdf_page.get_pixmap(dpi=level.dpi, colorspace=pymupdf.csGRAY)
            picture = Image.frombytes("L", (rendered.width, rendered.height), rendered.samples)
            encoded = io.BytesIO()
            level.apply(picture).save(encoded, format="PNG")
            target = scanned.new_page(width=page.width, height=page.height)
            target.insert_image(target.rect, stream=encoded.getvalue(), keep_proportion=False)
            truth.append(_truth_page(page.text, page.words, level, page.width, page.height))
        destination.parent.mkdir(parents=True, exist_ok=True)
        scanned.save(destination, garbage=4, deflate=True)
        scanned.close()
    return truth


def _truth_page(
    text: str, words: list[Word], level: Level, width: float, height: float
) -> TruthPage:
    placed: list[TruthWord] = []
    block = line = 0
    previous_end: int | None = None
    for word in words:
        gap = text[previous_end : word.start] if previous_end is not None else ""
        block += int("\n\n" in gap)
        line += int("\n" in gap)
        box = word.bbox
        corners: Corners = (
            level.moved(box.x0, box.y0, width, height),
            level.moved(box.x1, box.y0, width, height),
            level.moved(box.x1, box.y1, width, height),
            level.moved(box.x0, box.y1, width, height),
        )
        placed.append(TruthWord(word.text, corners, block, line))
        previous_end = word.end
    return TruthPage(
        text=text,
        words=tuple(placed),
        starts=tuple(word.start for word in words),
        width=width,
        height=height,
    )


class OracleEngine:
    """A perfect reader: reports each page's ground-truth words, pages in call order.

    It bounds what OCR can give the rest of the pipeline: detection and
    redaction errors under the oracle are not OCR errors. The first reading
    of a page reports every word and keeps how each word's box looked. A
    later reading (the leak check's re-read of the redacted page) reports a
    word only while most of its box still looks the same, so a word blanked
    or blacked out is no longer read, however faint the scan. Pages are used
    in turn and then from the start again.
    """

    name = "oracle"
    box_margin = OCR_BOX_MARGIN

    def __init__(self, truth: list[TruthPage]) -> None:
        self.truth = truth
        self.calls = 0
        self.first_seen: dict[int, list[np.ndarray]] = {}

    def read(self, image: PageImage) -> list[OcrWord]:
        """Return the next page's ground-truth words still printed, in pixels of `image`."""
        index = self.calls % len(self.truth)
        self.calls += 1
        scale = image.dpi / 72
        levels = np.frombuffer(image.samples, dtype=np.uint8).reshape(image.height, image.width, 3)
        boxes = [
            (word.bbox.x0 * scale, word.bbox.y0 * scale, word.bbox.x1 * scale, word.bbox.y1 * scale)
            for word in self.truth[index].words
        ]
        crops = [_crop(levels, box) for box in boxes]
        before = self.first_seen.setdefault(index, crops)
        return [
            OcrWord(word.text, box, 1.0, block=word.block, line=word.line)
            for word, box, crop, original in zip(
                self.truth[index].words, boxes, crops, before, strict=True
            )
            if _unchanged(original, crop)
        ]


# A pixel changed by more grey levels than this no longer shows what it did.
_CHANGED_LEVELS = 64


def _crop(levels: np.ndarray, box: tuple[float, float, float, float]) -> np.ndarray:
    x0, y0, x1, y1 = (int(value) for value in box)
    return levels[max(y0, 0) : y1, max(x0, 0) : x1, 0].astype(np.int16)


def _unchanged(original: np.ndarray, crop: np.ndarray) -> bool:
    """Whether most of a word's box shows what it showed at the first reading."""
    if original.shape != crop.shape or crop.size == 0:
        return False
    changed = np.count_nonzero(np.abs(crop - original) > _CHANGED_LEVELS)
    return bool(changed < crop.size / 2)


def ink_under_boxes(
    pdf_path: Path, page_index: int, corners: Corners, boxes: list[BBox]
) -> tuple[int, int]:
    """Count a word's ink pixels, and those lying inside any of the given boxes (points).

    Returns:
        The word's ink pixels and how many of them the boxes cover.
    """
    levels, scale = _grey_picture(pdf_path, page_index, pdf_path.stat().st_mtime_ns)
    window = _window(np.array(corners) * scale, levels.shape)
    if window is None:
        return 0, 0
    left, top, right, bottom, inked = window
    inked &= levels[top:bottom, left:right] < INK_LEVEL
    covered = np.zeros(inked.shape, dtype=bool)
    for box in boxes:
        x0, y0 = max(int(box.x0 * scale) - left, 0), max(int(box.y0 * scale) - top, 0)
        x1, y1 = int(np.ceil(box.x1 * scale)) - left, int(np.ceil(box.y1 * scale)) - top
        if x1 > 0 and y1 > 0:
            covered[y0:y1, x0:x1] = True
    return int(np.count_nonzero(inked)), int(np.count_nonzero(inked & covered))


def _window(
    polygon: np.ndarray, shape: tuple[int, ...]
) -> tuple[int, int, int, int, np.ndarray] | None:
    """Return the pixel rectangle around a polygon and which of its pixels lie inside it."""
    height, width = shape
    left, top = np.floor(polygon.min(axis=0)).astype(int).clip(0)
    right, bottom = np.ceil(polygon.max(axis=0)).astype(int)
    right, bottom = min(right, width), min(bottom, height)
    if right <= left or bottom <= top:
        return None
    ys, xs = np.mgrid[top:bottom, left:right] + 0.5
    return left, top, right, bottom, _inside(polygon, xs, ys)


def ink_inside(pdf_path: Path, page_index: int, corners: Corners) -> int:
    """Count ink pixels of a scanned page's picture inside a (possibly rotated) box.

    The picture is the page's only image, placed over the whole page, as
    `scan_document` writes it; redaction overwrites its pixels in place.
    """
    levels, scale = _grey_picture(pdf_path, page_index, pdf_path.stat().st_mtime_ns)
    window = _window(np.array(corners) * scale, levels.shape)
    if window is None:
        return 0
    left, top, right, bottom, inside = window
    return int(np.count_nonzero(inside & (levels[top:bottom, left:right] < INK_LEVEL)))


@functools.lru_cache(maxsize=4)
def _grey_picture(pdf_path: Path, page_index: int, modified: int) -> tuple[np.ndarray, float]:
    """Decode a page's picture to grey levels, with its pixels per point.

    Cached, since every word of a page is measured in the same picture; the
    modification time is part of the key, so a rewritten file is read again.
    """
    del modified
    with pymupdf.open(pdf_path) as pdf:
        page = pdf.load_page(page_index)
        picture = pymupdf.Pixmap(pdf, page.get_images(full=True)[0][0])
        # Redaction may store a greyscale picture back as RGB.
        if picture.n != 1:
            picture = pymupdf.Pixmap(pymupdf.csGRAY, picture)
        scale = picture.width / page.rect.width
    levels = np.frombuffer(picture.samples, dtype=np.uint8).reshape(picture.height, picture.width)
    return levels, scale


def covers(corners: Corners, x: float, y: float) -> bool:
    """Whether a point (points) lies inside a word's box on the scanned page."""
    return bool(_inside(np.array(corners), np.array([x]), np.array([y]))[0])


def _inside(polygon: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    """Whether points lie inside a convex polygon whose corners run clockwise on screen."""
    inside = np.ones(xs.shape, dtype=bool)
    for (x0, y0), (x1, y1) in zip(polygon, np.roll(polygon, -1, axis=0), strict=True):
        inside &= (x1 - x0) * (ys - y0) - (y1 - y0) * (xs - x0) >= 0
    return inside
