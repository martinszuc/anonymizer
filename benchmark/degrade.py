"""Controlled degradations of a scanned page: the variables of the OCR experiment.

Each level changes one factor of a clean 300 DPI greyscale scan (resolution,
blur, noise, JPEG quality or skew), so a result can be attributed to that
factor. Noise is drawn from a seeded generator, so a level gives the same
picture on every machine. Skew is the only factor that moves ink; `Level`
reports where a point of the clean scan lands, so ground truth follows it.
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageFilter

CLEAN_DPI = 300
_SEED = 20260930
_WHITE = 255


@dataclass(frozen=True)
class Level:
    """One degradation level.

    Attributes:
        factor: What is degraded (`clean`, `resolution`, `blur`, `noise`,
            `jpeg`, `skew`).
        value: The setting: DPI, blur radius in pixels at 300 DPI, noise
            standard deviation in grey levels, JPEG quality, or skew angle
            in degrees (counter-clockwise).
    """

    factor: str
    value: float

    @property
    def name(self) -> str:
        """A file-name-safe label, such as `blur-2` or `clean`."""
        if self.factor == "clean":
            return "clean"
        return f"{self.factor}-{self.value:g}"

    @property
    def dpi(self) -> int:
        """Resolution the page is scanned at."""
        return int(self.value) if self.factor == "resolution" else CLEAN_DPI

    def apply(self, scan: Image.Image) -> Image.Image:
        """Degrade a greyscale scan made at `dpi`."""
        if self.factor == "blur":
            return scan.filter(ImageFilter.GaussianBlur(self.value))
        if self.factor == "noise":
            rng = np.random.default_rng(_SEED)
            levels = np.asarray(scan, dtype=np.float64)
            noisy = levels + rng.normal(0.0, self.value, levels.shape)
            return Image.fromarray(np.clip(noisy, 0, _WHITE).astype(np.uint8), mode="L")
        if self.factor == "jpeg":
            encoded = io.BytesIO()
            scan.save(encoded, format="JPEG", quality=int(self.value))
            return Image.open(io.BytesIO(encoded.getvalue())).convert("L")
        if self.factor == "skew":
            return scan.rotate(self.value, resample=Image.Resampling.BICUBIC, fillcolor=_WHITE)
        return scan

    def moved(self, x: float, y: float, width: float, height: float) -> tuple[float, float]:
        """Where a point of the clean page lands, in the same units as the page size.

        Pillow rotates counter-clockwise about the centre as the picture is
        seen, which in coordinates with y growing downward is the matrix
        below.
        """
        if self.factor != "skew":
            return x, y
        angle = math.radians(self.value)
        cx, cy = width / 2, height / 2
        dx, dy = x - cx, y - cy
        return (
            cx + dx * math.cos(angle) + dy * math.sin(angle),
            cy - dx * math.sin(angle) + dy * math.cos(angle),
        )


LEVELS: tuple[Level, ...] = (
    Level("clean", 0),
    Level("resolution", 200),
    Level("resolution", 150),
    Level("resolution", 100),
    Level("blur", 1),
    Level("blur", 2),
    Level("blur", 3),
    Level("noise", 10),
    Level("noise", 25),
    Level("noise", 50),
    Level("jpeg", 50),
    Level("jpeg", 20),
    Level("jpeg", 10),
    Level("skew", 1),
    Level("skew", 3),
    Level("skew", 5),
)
"""Every level, the clean scan first; each changes one factor."""


def level_named(name: str) -> Level:
    """Return the level with a given name.

    Raises:
        ValueError: If no level has that name.
    """
    for level in LEVELS:
        if level.name == name:
            return level
    msg = f"unknown level {name!r}; choose from {[level.name for level in LEVELS]}"
    raise ValueError(msg)
