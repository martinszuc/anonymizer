"""Phone photos simulated in code: a page picture warped, lit unevenly and shadowed.

Tests of the phone-photo benchmark need photos without a camera, and a noisy
training set needs many; both take a rendered page and turn it into what a
handheld phone would see:

- **perspective**: the page's corners move to a quadrilateral inside the
  frame, the rest of which shows the table under the page (`photo_warp`);
- **lighting**: brightness falls off linearly in one direction, as from a
  window or a lamp at the side;
- **shadow**: one soft-edged region is darker, as under a hand or the phone;
- optionally **blur** (Gaussian, radius in pixels) and **JPEG** compression.

Everything is drawn from one seed, so the same page and seed give the same
photo. `photo_warp` returns the geometry `simulate_photo` applies, so a test
can tell where each word of the page lands. Ink stays darker than the darkest
paper: at `strength` 1 the paper keeps at least 45 % of its brightness.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

Point = tuple[float, float]
Quad = tuple[Point, Point, Point, Point]
"""Corners in pixels: top left, top right, bottom right, bottom left."""

TABLE = (118, 104, 92)
"""The colour of the table around the page."""

# At strength 1: the page's corners move by up to this share of its size,
# inside a border of `_INSET`; the light falls to `1 - _LIGHT_DROP` across the
# page, a shadow keeps `1 - _SHADOW_DEPTH`.
_INSET = 0.05
_CORNER_JITTER = 0.07
_LIGHT_DROP = 0.3
_SHADOW_DEPTH = 0.35
_SHADOW_SOFTNESS = 0.03


@dataclass(frozen=True)
class Warp:
    """Where a page picture's corners land in the photo, and the mapping between them.

    Attributes:
        size: The photo's width and height in pixels (the page picture's size).
        corners: The page's corners in the photo.
    """

    size: tuple[int, int]
    corners: Quad

    def forward(self, x: float, y: float) -> Point:
        """Map a pixel of the page picture to the photo."""
        return _apply(_homography(_frame(self.size), self.corners), x, y)

    def backward(self, x: float, y: float) -> Point:
        """Map a pixel of the photo to the page picture."""
        return _apply(_homography(self.corners, _frame(self.size)), x, y)

    def coefficients(self) -> tuple[float, ...]:
        """The eight coefficients Pillow's perspective transform takes (photo to page)."""
        matrix = _homography(self.corners, _frame(self.size))
        return tuple(float(value) for value in matrix.flatten()[:8])


def photo_warp(size: tuple[int, int], seed: int, *, strength: float = 1.0) -> Warp:
    """Draw the perspective of a simulated photo of a page picture.

    Args:
        size: The page picture's width and height in pixels; the photo has the same.
        seed: Seeds every random choice.
        strength: Scales how far the corners move; 0 keeps the page square in its border.

    Returns:
        The geometry `simulate_photo` applies with the same arguments.
    """
    generator = np.random.default_rng(seed)
    width, height = size
    inset_x, inset_y = _INSET * width, _INSET * height
    jitter_x, jitter_y = _CORNER_JITTER * strength * width, _CORNER_JITTER * strength * height
    square = (
        (inset_x, inset_y),
        (width - inset_x, inset_y),
        (width - inset_x, height - inset_y),
        (inset_x, height - inset_y),
    )
    moved = [
        (
            float(np.clip(x + generator.uniform(-jitter_x, jitter_x), 0, width - 1)),
            float(np.clip(y + generator.uniform(-jitter_y, jitter_y), 0, height - 1)),
        )
        for x, y in square
    ]
    return Warp(size, (moved[0], moved[1], moved[2], moved[3]))


def simulate_photo(
    page: Image.Image,
    seed: int,
    *,
    strength: float = 1.0,
    blur: float = 0.0,
    jpeg_quality: int | None = None,
) -> Image.Image:
    """Turn a page picture into a simulated phone photo of it.

    Args:
        page: The rendered page, any mode; read as RGB.
        seed: Seeds the perspective, the light's direction and the shadow.
        strength: Scales perspective, light fall-off and shadow depth (0 to 1).
        blur: Gaussian blur radius in pixels, applied last before compression.
        jpeg_quality: Compress as JPEG at this quality and decode again; none by default.

    Returns:
        An RGB picture of the page's size.

    Raises:
        ValueError: If `strength` lies outside [0, 1].
    """
    if not 0.0 <= strength <= 1.0:
        msg = f"strength must lie in [0, 1], not {strength}"
        raise ValueError(msg)
    warp = photo_warp(page.size, seed, strength=strength)
    # The geometry uses the first draws of the seed; light and shadow the next ones.
    generator = np.random.default_rng([seed, 1])
    photo = page.convert("RGB").transform(
        page.size,
        Image.Transform.PERSPECTIVE,
        warp.coefficients(),
        resample=Image.Resampling.BICUBIC,
        fillcolor=TABLE,
    )
    light = _light(page.size, generator, strength) * _shadow(page.size, generator, strength)
    levels = np.asarray(photo, dtype=np.float32) * light[..., None]
    photo = Image.fromarray(levels.clip(0, 255).astype(np.uint8), "RGB")
    if blur > 0:
        photo = photo.filter(ImageFilter.GaussianBlur(blur))
    if jpeg_quality is not None:
        encoded = io.BytesIO()
        photo.save(encoded, format="JPEG", quality=jpeg_quality)
        photo = Image.open(io.BytesIO(encoded.getvalue())).convert("RGB")
    return photo


def _light(size: tuple[int, int], generator: np.random.Generator, strength: float) -> np.ndarray:
    """Brightness falling off linearly across the frame in a random direction."""
    width, height = size
    angle = generator.uniform(0, 2 * np.pi)
    ys, xs = np.mgrid[0:height, 0:width].astype(np.float32)
    along = xs / max(width, 1) * np.cos(angle) + ys / max(height, 1) * np.sin(angle)
    along = (along - along.min()) / max(float(np.ptp(along)), 1e-9)
    return 1.0 - _LIGHT_DROP * strength * along


def _shadow(size: tuple[int, int], generator: np.random.Generator, strength: float) -> np.ndarray:
    """A soft-edged ellipse of shade at a random place, up to a third of the frame across."""
    width, height = size
    centre_x, centre_y = generator.uniform(0, width), generator.uniform(0, height)
    radius_x = generator.uniform(0.1, 0.35) * width
    radius_y = generator.uniform(0.1, 0.35) * height
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse(
        (centre_x - radius_x, centre_y - radius_y, centre_x + radius_x, centre_y + radius_y),
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(_SHADOW_SOFTNESS * min(size)))
    shade = np.asarray(mask, dtype=np.float32) / 255
    return 1.0 - _SHADOW_DEPTH * strength * shade


def _frame(size: tuple[int, int]) -> Quad:
    width, height = size
    return ((0.0, 0.0), (float(width), 0.0), (float(width), float(height)), (0.0, float(height)))


def _homography(source: Quad, target: Quad) -> np.ndarray:
    """The 3x3 projective map taking four source points to four target points."""
    rows: list[list[float]] = []
    values: list[float] = []
    for (x, y), (u, v) in zip(source, target, strict=True):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        values += [u, v]
    solved = np.linalg.solve(np.array(rows), np.array(values))
    return np.append(solved, 1.0).reshape(3, 3)


def _apply(matrix: np.ndarray, x: float, y: float) -> Point:
    u, v, w = matrix @ np.array([x, y, 1.0])
    return float(u / w), float(v / w)
