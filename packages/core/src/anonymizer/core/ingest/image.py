"""Photos and scanned images, read as a PDF with one picture per page.

A JPEG, PNG or TIFF file is wrapped into a PDF whose pages each hold one
picture and nothing else, and from there takes the path of a scanned PDF:
OCR, redaction, the leak check. Every client reads a file through
`as_pdf`, which tells the type by content, not by the file name.

The page is built from decoded pixels only. A photo's EXIF and XMP hold a
GPS position, the device, an owner's name and timestamps; PNG text chunks
and TIFF tags hold authors and comments. Copying the encoded picture into
the PDF, as PyMuPDF's own conversion does, keeps all of them (see
`docs/findings.md`), so nothing of the file but its pixels reaches the page,
and so nothing of it reaches the redacted copy.

The EXIF orientation is applied first: a phone stores a photo as the sensor
saw it and only records how to turn it, and OCR reads nothing on a sideways
page. PyMuPDF ignores the tag in PNG and TIFF, Pillow applies it in all
three. A TIFF becomes one page per frame; a JPEG or PNG one page, since
their further frames are animation or a camera's previews, not pages.

The page size follows from the picture's resolution, so that
`points = pixels * 72 / dpi` holds for the stored pixels. A resolution the
file records is used when it is plausible for a document; cameras and
screenshots record 72 or 96 whatever they show, and a file without one is
taken as `ASSUMED_DPI`. The same bytes always give the same PDF, byte for
byte, so the copy redaction reads again is the one detection read.
"""

from __future__ import annotations

import io
import logging
from collections.abc import Iterator

import pymupdf
from PIL import Image, ImageOps, ImageSequence

log = logging.getLogger(__name__)

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
"""File name endings of the image formats read, for file dialogs; reading goes by content."""

SOURCE_SUFFIXES = (".pdf", *IMAGE_SUFFIXES)
"""File name endings of every format read."""

ASSUMED_DPI = 300.0
"""Resolution of a picture that records none, or none plausible for a document."""

# Scanners record their resolution truthfully; values outside this range are
# a camera's or a program's placeholder (72, 96) or a damaged header.
_PLAUSIBLE_DPI = (100.0, 1200.0)
_POINTS_PER_INCH = 72
_ORIENTATION_TAG = 0x0112
# EXIF orientations that turn the picture by a quarter, swapping its axes.
_QUARTER_TURNS = {5, 6, 7, 8}

_SIGNATURES = {
    b"\xff\xd8\xff": "JPEG",
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"II*\x00": "TIFF",
    b"MM\x00*": "TIFF",
    b"II+\x00": "TIFF",  # BigTIFF
    b"MM\x00+": "TIFF",
}
# PDF readers accept the header anywhere in the first kilobyte.
_PDF_HEADER = b"%PDF-"
_PDF_HEADER_WINDOW = 1024


class UnsupportedFileError(ValueError):
    """The file is neither a PDF nor an image format that is read, or it is damaged."""


def image_format(data: bytes) -> str | None:
    """Tell which image format a file holds from its first bytes.

    Args:
        data: The file's content.

    Returns:
        `"JPEG"`, `"PNG"` or `"TIFF"`, or `None` for anything else.
    """
    return next(
        (name for signature, name in _SIGNATURES.items() if data.startswith(signature)), None
    )


def as_pdf(data: bytes) -> bytes:
    """Return a file as the PDF it is read as.

    Args:
        data: The content of a PDF, JPEG, PNG or TIFF file.

    Returns:
        A PDF as it is, an image wrapped as `image_to_pdf` describes.

    Raises:
        UnsupportedFileError: If the file is of another type, or an image
            that cannot be decoded.
    """
    if image_format(data) is not None:
        return image_to_pdf(data)
    if _PDF_HEADER not in data[:_PDF_HEADER_WINDOW]:
        msg = (
            "unsupported file type: documents must be PDF, JPEG, PNG or TIFF "
            "(an iPhone's HEIC photos can be exported as JPEG)"
        )
        raise UnsupportedFileError(msg)
    return data


def image_to_pdf(data: bytes) -> bytes:
    """Wrap an image into a PDF holding only its pixels, one page per frame.

    Args:
        data: A JPEG, PNG or TIFF file.

    Returns:
        A PDF whose pages each hold one picture, upright, sized by its
        resolution; nothing else of the file is carried over.

    Raises:
        UnsupportedFileError: If the file is not one of these formats, or it
            cannot be decoded.
    """
    kind = image_format(data)
    if kind is None:
        msg = "not a JPEG, PNG or TIFF image"
        raise UnsupportedFileError(msg)
    pdf = pymupdf.open()
    try:
        # Only the format the signature names is tried, never another decoder.
        with Image.open(io.BytesIO(data), formats=[kind]) as image:
            for frame in _pages(image):
                _add_page(pdf, frame)
            log.debug("image wrapped: format=%s pages=%d", kind, pdf.page_count)
    except (OSError, SyntaxError, Image.DecompressionBombError) as error:
        # Pillow reports a damaged or truncated file as OSError or SyntaxError.
        msg = "the image cannot be read: it is damaged or uses an encoding that is not supported"
        raise UnsupportedFileError(msg) from error
    # Without a new /ID the same pixels always give the same bytes.
    wrapped = pdf.tobytes(garbage=3, deflate=True, no_new_id=True)
    pdf.close()
    return wrapped


def _pages(image: Image.Image) -> Iterator[Image.Image]:
    """The frames that are pages: every frame of a TIFF, the first of anything else."""
    if image.format != "TIFF":
        yield image
        return
    yield from ImageSequence.Iterator(image)


def _add_page(pdf: pymupdf.Document, frame: Image.Image) -> None:
    """Append a page holding the frame's pixels, upright and sized by its resolution."""
    # The resolution is recorded along the stored picture's axes.
    x_dpi, y_dpi = _resolution(frame)
    if frame.getexif().get(_ORIENTATION_TAG) in _QUARTER_TURNS:
        x_dpi, y_dpi = y_dpi, x_dpi
    # Pillow turns a TIFF upright as it loads it and drops the tag, so it is
    # loaded first: turning it before would turn it twice.
    frame.load()
    pixels = _plain_pixels(ImageOps.exif_transpose(frame))
    page = pdf.new_page(
        width=pixels.width * _POINTS_PER_INCH / x_dpi,
        height=pixels.height * _POINTS_PER_INCH / y_dpi,
    )
    colorspace = pymupdf.csGRAY if pixels.mode == "L" else pymupdf.csRGB
    picture = pymupdf.Pixmap(colorspace, pixels.width, pixels.height, pixels.tobytes(), False)
    # A fax's resolution differs between the axes: the picture is stretched to the page.
    page.insert_image(page.rect, pixmap=picture, keep_proportion=False)


def _resolution(frame: Image.Image) -> tuple[float, float]:
    """The frame's resolution per axis, or `ASSUMED_DPI` if it records none plausible."""
    recorded = frame.info.get("dpi")
    low, high = _PLAUSIBLE_DPI
    if recorded and all(low <= value <= high for value in recorded):
        x_dpi, y_dpi = recorded
        return float(x_dpi), float(y_dpi)
    return ASSUMED_DPI, ASSUMED_DPI


def _plain_pixels(image: Image.Image) -> Image.Image:
    """Convert to 8-bit grey or RGB, transparency flattened onto white paper."""
    if image.mode in ("1", "L"):
        return image.convert("L")
    if image.mode.startswith("I;16"):
        # Converting 16-bit grey to 8-bit clips instead of scaling: all would be white.
        return image.convert("I").point(lambda level: level / 256).convert("L")
    if image.has_transparency_data:
        paper = Image.new("RGBA", image.size, "white")
        return Image.alpha_composite(paper, image.convert("RGBA")).convert("RGB")
    return image.convert("RGB")
