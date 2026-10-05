"""Synthetic photos and scanned images, with metadata planted where cameras put it.

A photo is a scan of lines (`scan_of`) stored the way a phone stores it: as
the sensor saw it, turned away from upright, with an EXIF orientation that
says how to turn it back. Every planted value is invented; tests assert it is
in the image and gone from every PDF made from it.
"""

import io

import pymupdf
from PIL import Image, PngImagePlugin

from tests.pdf_builders import SCAN_DPI, scan_of

OWNER = "Jana Planted-Owner"
DEVICE = "Planted Phone X1"
CAPTURED = "2026:09:30 12:34:56"
# Where the photo was taken, as XMP writes it; the binary GPS block holds the same.
GPS_POSITION = "49,11.5000N"
XMP_PACKET = (
    b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF '
    b'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
    b'<rdf:Description xmlns:exif="http://ns.adobe.com/exif/1.0/" '
    b'exif:GPSLatitude="' + GPS_POSITION.encode() + b'"/></rdf:RDF></x:xmpmeta>'
)
PLANTED = (OWNER, DEVICE, CAPTURED, GPS_POSITION)

_ORIENTATION = 0x0112
_ARTIST = 0x013B
_MODEL = 0x0110
_DATE_TIME = 0x0132
_GPS_IFD = 0x8825
_GPS_LATITUDE_REF = 1
_GPS_LATITUDE = 2
_XMP_TAG = 700
# How to store an upright picture so that its EXIF orientation turns it back.
_STORED_AS = {
    1: None,
    3: Image.Transpose.ROTATE_180,
    6: Image.Transpose.ROTATE_90,
    8: Image.Transpose.ROTATE_270,
}


def upright_scan(lines: list[str], dpi: int = SCAN_DPI) -> Image.Image:
    """The lines as `write_lines` places them on an A4 page, as an RGB picture."""
    scan = scan_of(lines, dpi=dpi)
    return Image.frombytes("L", (scan.width, scan.height), scan.samples).convert("RGB")


def photo_exif(orientation: int = 1) -> Image.Exif:
    """EXIF as a phone writes it: orientation, owner, device, time and position."""
    exif = Image.Exif()
    exif[_ORIENTATION] = orientation
    exif[_ARTIST] = OWNER
    exif[_MODEL] = DEVICE
    exif[_DATE_TIME] = CAPTURED
    gps = exif.get_ifd(_GPS_IFD)
    gps[_GPS_LATITUDE_REF] = "N"
    gps[_GPS_LATITUDE] = (49.0, 11.0, 30.0)
    return exif


def encode(
    upright: Image.Image,
    image_format: str,
    *,
    orientation: int = 1,
    dpi: tuple[float, float] | None = None,
) -> bytes:
    """Store a picture as JPEG, PNG or TIFF, turned for `orientation`, with `PLANTED` in it."""
    turn = _STORED_AS[orientation]
    stored = upright.transpose(turn) if turn is not None else upright
    exif = photo_exif(orientation)
    if image_format == "TIFF":
        # A TIFF keeps XMP as a tag of its own, beside the EXIF ones.
        exif[_XMP_TAG] = XMP_PACKET
    options: dict = {"exif": exif.tobytes()}
    if dpi is not None:
        options["dpi"] = dpi
    if image_format == "JPEG":
        options |= {"quality": 95, "xmp": XMP_PACKET}
    if image_format == "PNG":
        text = PngImagePlugin.PngInfo()
        text.add_text("Author", OWNER)
        text.add_itxt("XML:com.adobe.xmp", XMP_PACKET.decode())
        options["pnginfo"] = text
    encoded = io.BytesIO()
    stored.save(encoded, image_format, **options)
    return encoded.getvalue()


def phone_photo(lines: list[str], *, image_format: str = "JPEG", orientation: int = 6) -> bytes:
    """A phone's photo of an A4 page of lines: turned by EXIF, recording 72 DPI, GPS tagged.

    The page is drawn at 300 DPI, the resolution a picture without a
    plausible one is taken at, so it wraps to an A4 page again.
    """
    return encode(upright_scan(lines, dpi=300), image_format, orientation=orientation, dpi=(72, 72))


def every_byte(pdf_bytes: bytes) -> bytes:
    """A PDF's raw bytes followed by every object and every stream decompressed."""
    parts = [pdf_bytes]
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        for xref in range(1, pdf.xref_length()):
            parts.append(pdf.xref_object(xref).encode("latin-1", errors="replace"))
            if pdf.xref_is_stream(xref):
                parts.append(pdf.xref_stream(xref) or b"")
    return b"\n".join(parts)
