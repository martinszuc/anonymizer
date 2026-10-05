"""Images read as PDFs: type by content, orientation, resolution, metadata, fingerprint."""

import hashlib
import io
from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import (
    ASSUMED_DPI,
    UnsupportedFileError,
    as_pdf,
    document_from_bytes,
    extract_surfaces,
    image_format,
    image_to_pdf,
    load_document,
    pages_needing_ocr,
    read_verified,
)
from anonymizer.core.types import Document
from PIL import Image

from tests.image_builders import PLANTED, encode, every_byte, upright_scan
from tests.ocr_stand_in import ScriptedEngine
from tests.pdf_builders import SCAN_DPI, write_pdf

FORMATS = ["JPEG", "PNG", "TIFF"]
LINES = ["Kontakt: jan.novak@example.com", "Telefon: +420 603 123 456"]


def marked(width: int = 300, height: int = 200) -> Image.Image:
    """A white picture with a black square in its upright top-left corner."""
    picture = Image.new("RGB", (width, height), "white")
    picture.paste((0, 0, 0), (0, 0, 40, 40))
    return picture


def rendered(pdf_bytes: bytes, index: int = 0) -> Image.Image:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        page = pdf[index]
        # The page's own pixels: its size in points at the picture's resolution.
        dpi = round(page.get_image_info()[0]["width"] * 72 / page.rect.width)
        picture = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB, alpha=False)
    return Image.frombytes("RGB", (picture.width, picture.height), picture.samples)


def red(picture: Image.Image, x: int, y: int) -> int:
    pixel = picture.getpixel((x, y))
    assert isinstance(pixel, tuple)
    return int(pixel[0])


def page_sizes(pdf_bytes: bytes) -> list[tuple[float, float]]:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        return [(page.rect.width, page.rect.height) for page in pdf]


class TestFileType:
    @pytest.mark.parametrize("image_format_name", FORMATS)
    def test_images_are_told_apart_by_content(self, image_format_name: str):
        assert image_format(encode(marked(), image_format_name)) == image_format_name

    def test_a_pdf_is_returned_as_it_is(self, tmp_path: Path):
        data = write_pdf(tmp_path / "cv.pdf", [LINES]).read_bytes()
        assert image_format(data) is None
        assert as_pdf(data) is data

    def test_the_file_name_does_not_decide(self, tmp_path: Path):
        disguised = tmp_path / "scan.pdf"
        disguised.write_bytes(encode(marked(), "PNG"))
        assert len(load_document(disguised).pages) == 1
        pdf_named_as_photo = write_pdf(tmp_path / "photo.jpg", [LINES])
        assert load_document(pdf_named_as_photo).pages[0].has_text_layer

    @pytest.mark.parametrize(
        "data",
        [
            b"GIF89a" + bytes(32),
            b"\x00\x00\x00\x18ftypheic" + bytes(32),
            b"RIFF\x00\x00\x00\x00WEBPVP8 ",
            b"not a document at all",
        ],
        ids=["gif", "heic", "webp", "text"],
    )
    def test_other_types_are_refused_by_name(self, data: bytes):
        with pytest.raises(UnsupportedFileError, match="PDF, JPEG, PNG or TIFF"):
            as_pdf(data)

    def test_a_damaged_image_is_refused(self):
        truncated = encode(marked(), "JPEG")[:200]
        with pytest.raises(UnsupportedFileError, match="cannot be read"):
            as_pdf(truncated)

    def test_wrapping_needs_an_image(self, tmp_path: Path):
        with pytest.raises(UnsupportedFileError, match="not a JPEG, PNG or TIFF"):
            image_to_pdf(write_pdf(tmp_path / "cv.pdf", [LINES]).read_bytes())

    def test_a_pdf_header_after_leading_bytes_is_still_a_pdf(self, tmp_path: Path):
        data = b"\r\n" + write_pdf(tmp_path / "cv.pdf", [LINES]).read_bytes()
        assert as_pdf(data) is data


class TestOrientation:
    @pytest.mark.parametrize("image_format_name", FORMATS)
    @pytest.mark.parametrize("orientation", [1, 3, 6, 8])
    def test_the_page_is_upright(self, image_format_name: str, orientation: int):
        data = encode(marked(), image_format_name, orientation=orientation, dpi=(200, 200))
        picture = rendered(as_pdf(data))
        assert picture.size == (300, 200)
        assert red(picture, 20, 20) < 60
        assert red(picture, 280, 180) > 200

    def test_the_stored_picture_is_turned_before_the_control(self):
        # Fixture's starting state: without the tag the picture is sideways.
        stored = Image.open(io.BytesIO(encode(marked(), "PNG", orientation=6)))
        assert stored.size == (200, 300)


class TestResolution:
    @pytest.mark.parametrize("image_format_name", FORMATS)
    def test_a_recorded_resolution_sizes_the_page(self, image_format_name: str):
        data = encode(marked(), image_format_name, dpi=(200, 200))
        (width, height), *_ = page_sizes(as_pdf(data))
        assert (width, height) == pytest.approx((300 * 72 / 200, 200 * 72 / 200), abs=0.01)

    @pytest.mark.parametrize("recorded", [None, (72, 72), (96, 96), (5000, 5000)])
    def test_a_missing_or_implausible_resolution_is_assumed(
        self, recorded: tuple[float, float] | None
    ):
        data = encode(marked(), "PNG", dpi=recorded)
        assert page_sizes(as_pdf(data)) == [
            pytest.approx((300 * 72 / ASSUMED_DPI, 200 * 72 / ASSUMED_DPI))
        ]

    def test_a_fax_resolution_differs_between_the_axes(self):
        data = encode(marked(), "TIFF", dpi=(204, 196))
        assert page_sizes(as_pdf(data)) == [pytest.approx((300 * 72 / 204, 200 * 72 / 196))]

    def test_axes_swap_with_a_quarter_turn(self):
        # Stored 200 wide at 204 DPI and 300 high at 196 DPI; upright, 300 wide at 196.
        for image_format_name in FORMATS:
            data = encode(marked(), image_format_name, orientation=6, dpi=(204, 196))
            sizes = page_sizes(as_pdf(data))
            assert sizes == [pytest.approx((300 * 72 / 196, 200 * 72 / 204), abs=0.01)]

    def test_a_scan_wraps_to_its_page(self):
        data = encode(upright_scan(LINES), "PNG", dpi=(SCAN_DPI, SCAN_DPI))
        assert page_sizes(as_pdf(data)) == [pytest.approx((595, 842), abs=0.5)]


class TestPixels:
    def test_transparency_is_white_paper(self):
        transparent = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
        transparent.paste((0, 0, 0, 255), (0, 0, 10, 10))
        picture = rendered(as_pdf(encode(transparent, "PNG")))
        assert picture.getpixel((5, 5)) == (0, 0, 0)
        assert picture.getpixel((40, 40)) == (255, 255, 255)

    def test_sixteen_bit_grey_is_scaled_not_clipped(self):
        grey = Image.new("I;16", (20, 20), 0x8000)
        level = red(rendered(as_pdf(encode(grey, "PNG"))), 10, 10)
        assert level == pytest.approx(128, abs=2)

    @pytest.mark.parametrize("mode", ["1", "L", "P", "CMYK"])
    def test_other_modes_keep_their_ink(self, mode: str):
        picture = marked().convert(mode)
        image_format_name = "JPEG" if mode == "CMYK" else "TIFF"
        page = rendered(as_pdf(encode(picture, image_format_name)))
        assert red(page, 20, 20) < 60
        assert red(page, 280, 180) > 200

    def test_a_tiff_has_one_page_per_frame(self):
        first, second = marked(300, 200), marked(100, 400)
        encoded = io.BytesIO()
        first.save(encoded, "TIFF", save_all=True, append_images=[second], dpi=(200, 200))
        sizes = page_sizes(as_pdf(encoded.getvalue()))
        assert sizes == [pytest.approx((108, 72)), pytest.approx((36, 144))]

    def test_a_jpeg_has_one_page(self):
        assert len(page_sizes(as_pdf(encode(marked(), "JPEG")))) == 1


class TestMetadata:
    @pytest.mark.parametrize("image_format_name", FORMATS)
    def test_planted_values_are_in_the_image(self, image_format_name: str):
        data = encode(marked(), image_format_name, orientation=6)
        for value in PLANTED:
            assert value.encode() in data, value

    @pytest.mark.parametrize("image_format_name", FORMATS)
    def test_nothing_but_pixels_reaches_the_pdf(self, image_format_name: str):
        wrapped = every_byte(as_pdf(encode(marked(), image_format_name, orientation=6)))
        for value in PLANTED:
            assert value.encode() not in wrapped, value
        assert b"Exif" not in wrapped
        assert b"xmpmeta" not in wrapped

    def test_the_pdf_carries_no_metadata_of_its_own(self):
        with pymupdf.open(stream=as_pdf(encode(marked(), "JPEG")), filetype="pdf") as pdf:
            metadata = pdf.metadata or {}
            assert not any(metadata.get(key) for key in ("author", "creator", "producer"))
            assert pdf.get_xml_metadata() == ""
            assert not extract_surfaces(pdf)


class TestDocument:
    def test_the_fingerprint_is_of_the_image_file(self):
        data = encode(marked(), "JPEG")
        document = document_from_bytes(data)
        assert document.fingerprint == hashlib.sha256(data).hexdigest()

    def test_the_same_bytes_give_the_same_pdf(self):
        data = encode(upright_scan(LINES), "JPEG", orientation=6)
        assert as_pdf(data) == as_pdf(data)

    def test_an_image_page_needs_ocr(self):
        document = document_from_bytes(encode(marked(), "PNG"))
        assert not document.pages[0].has_text_layer
        assert pages_needing_ocr(document) == [0]

    def test_ocr_reads_the_image_page(self, tmp_path: Path):
        original = load_document(write_pdf(tmp_path / "original.pdf", [LINES]))
        data = encode(upright_scan(LINES), "JPEG", orientation=6, dpi=(SCAN_DPI, SCAN_DPI))
        engine = ScriptedEngine.reading(original)
        document = document_from_bytes(data, ocr=engine)
        (page,) = document.pages
        assert page.raster_dpi == 300
        assert page.text == original.pages[0].text
        assert document.ocr_engine == engine.name
        # The engine received the upright page, rendered at the OCR resolution.
        (image,) = engine.images
        assert (image.width, image.height) == pytest.approx((2480, 3508), abs=2)

    def test_read_verified_gives_the_pdf_the_document_was_read_from(self, tmp_path: Path):
        photo = tmp_path / "photo.jpg"
        photo.write_bytes(encode(marked(), "JPEG", orientation=6))
        document = load_document(photo)
        assert read_verified(photo, document) == as_pdf(photo.read_bytes())

    def test_read_verified_refuses_another_image(self, tmp_path: Path):
        photo = tmp_path / "photo.png"
        photo.write_bytes(encode(marked(), "PNG"))
        document: Document = load_document(photo)
        other = marked()
        other.putpixel((299, 199), (254, 255, 255))
        photo.write_bytes(encode(other, "PNG"))
        with pytest.raises(ValueError, match="different file"):
            read_verified(photo, document)


class TestWhyPillow:
    """PyMuPDF's own image handling, which `image.py` does not rely on (`docs/findings.md`)."""

    def test_pymupdf_conversion_copies_the_metadata_into_the_pdf(self):
        data = encode(marked(), "JPEG", orientation=6)
        with pymupdf.open(stream=data) as image:
            converted = image.convert_to_pdf()
        with pymupdf.open() as pdf:
            page = pdf.new_page()
            page.insert_image(page.rect, stream=data)
            inserted = pdf.tobytes(garbage=3, deflate=True)
        for saved in (converted, inserted):
            assert all(value.encode() in every_byte(saved) for value in PLANTED)
        assert not any(value.encode() in every_byte(as_pdf(data)) for value in PLANTED)

    @pytest.mark.parametrize("image_format_name", ["PNG", "TIFF"])
    def test_pymupdf_ignores_the_orientation_of_png_and_tiff(self, image_format_name: str):
        sizes = {}
        for orientation in (1, 6):
            data = encode(marked(), image_format_name, orientation=orientation, dpi=(72, 72))
            with pymupdf.open(stream=data) as image:
                sizes[orientation] = (image[0].rect.width, image[0].rect.height)
        # Control: upright it is 300 x 200; stored for orientation 6 it is 200 x 300 and stays so.
        assert sizes == {1: (300, 200), 6: (200, 300)}
