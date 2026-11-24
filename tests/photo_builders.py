"""Simulated phone photos for tests, stored as a phone stores them, and a reader for them.

A page is rendered from an invented benchmark document, turned into a photo
in code (`benchmark.photo_sim`) and written as a JPEG with an EXIF capture
time. `PhotoReader` stands in for OCR: it knows each photo's words, with
boxes moved by the photo's warp, and tells the photos apart by size.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import pymupdf
from anonymizer.core.ingest import ASSUMED_DPI, OcrWord, PageImage, load_document
from anonymizer.core.types import BBox
from PIL import Image

from benchmark.photo_sim import photo_warp, simulate_photo
from tests.ocr_stand_in import InkReadingEngine, ScriptedWord, layout_of

_EXIF_IFD = 0x8769
_ORIENTATION = 0x0112
_DATE_TIME_ORIGINAL = 0x9003
_SUBSEC_TIME_ORIGINAL = 0x9291
# Turning an upright picture so its EXIF orientation turns it back.
_STORED_AS = {1: None, 6: Image.Transpose.ROTATE_90}


def jpeg_with_capture_time(
    picture: Image.Image,
    captured: str | None,
    *,
    subsec: str | None = None,
    orientation: int = 1,
) -> bytes:
    """Encode an upright picture as a phone's JPEG: stored as the sensor saw it, EXIF time."""
    turn = _STORED_AS[orientation]
    stored = picture.transpose(turn) if turn is not None else picture
    exif = Image.Exif()
    exif[_ORIENTATION] = orientation
    details = exif.get_ifd(_EXIF_IFD)
    if captured is not None:
        details[_DATE_TIME_ORIGINAL] = captured
    if subsec is not None:
        details[_SUBSEC_TIME_ORIGINAL] = subsec
    encoded = io.BytesIO()
    stored.convert("RGB").save(encoded, format="JPEG", quality=92, exif=exif.tobytes())
    return encoded.getvalue()


@dataclass(frozen=True)
class SimulatedPhoto:
    """A simulated photo of one page and what a perfect reader would read on it.

    Attributes:
        jpeg: The photo as a phone writes it.
        size: Its upright size in pixels.
        words: The page's words with boxes on the photo, in the photo's points.
    """

    jpeg: bytes
    size: tuple[int, int]
    words: list[ScriptedWord]


def simulated_photo(
    pdf: Path,
    page_index: int,
    *,
    seed: int,
    captured: str,
    dpi: int = 100,
    trim: int = 0,
    orientation: int = 1,
    misread: dict[str, str] | None = None,
) -> SimulatedPhoto:
    """Photograph one page of a born-digital PDF in code.

    Args:
        pdf: The rendered document.
        page_index: The page to photograph.
        seed: Seeds the simulated photo.
        captured: EXIF capture time, `YYYY:MM:DD HH:MM:SS`.
        dpi: Resolution the page is rendered at.
        trim: Pixels cut off the right and bottom edge, which are blank
            paper, to give every photo of a test its own size.
        orientation: EXIF orientation the photo is stored with.
        misread: Words the reader reads otherwise, by their printed text.

    Returns:
        The photo and its words.
    """
    with pymupdf.open(pdf) as document:
        page = document.load_page(page_index)
        rendered = page.get_pixmap(dpi=dpi)
        picture = Image.frombytes("RGB", (rendered.width, rendered.height), rendered.samples)
        picture = picture.crop((0, 0, picture.width - trim, picture.height - trim))
    text_page = load_document(pdf).pages[page_index]
    warp = photo_warp(picture.size, seed)
    photo = simulate_photo(picture, seed)
    to_pixels = dpi / 72
    to_points = 72 / ASSUMED_DPI
    words: list[ScriptedWord] = []
    for word in layout_of(text_page):
        corners = [
            warp.forward(x * to_pixels, y * to_pixels)
            for x, y in (
                (word.bbox.x0, word.bbox.y0),
                (word.bbox.x1, word.bbox.y0),
                (word.bbox.x1, word.bbox.y1),
                (word.bbox.x0, word.bbox.y1),
            )
        ]
        xs, ys = [x for x, _ in corners], [y for _, y in corners]
        box = BBox(
            min(xs) * to_points, min(ys) * to_points, max(xs) * to_points, max(ys) * to_points
        )
        text = (misread or {}).get(word.text, word.text)
        words.append(ScriptedWord(text, box, word.block, word.line))
    jpeg = jpeg_with_capture_time(photo, captured, orientation=orientation)
    return SimulatedPhoto(jpeg, photo.size, words)


class PhotoReader(InkReadingEngine):
    """Reads simulated photos: a photo's words where its picture still shows them.

    The photo is told by its size, so every photo given must have its own.
    """

    name = "stand-in photo reader"

    def __init__(self, photos: list[SimulatedPhoto]) -> None:
        super().__init__([])
        self.by_size = {photo.size: photo.words for photo in photos}

    def read(self, image: PageImage) -> list[OcrWord]:
        """Read the photo whose size is nearest the picture's."""
        size = min(
            self.by_size,
            key=lambda known: abs(known[0] - image.width) + abs(known[1] - image.height),
        )
        self.pages = [self.by_size[size]]
        return super().read(image)
