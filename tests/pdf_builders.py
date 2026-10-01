"""Minimal PDFs written by the tests themselves.

Fixtures are generated rather than committed: a PDF in the repository would be
an opaque binary, and a realistic labelled corpus is a separate project. Page
text is Latin-1 only, because the base-14 Helvetica font cannot encode `č` or
`ř`; strings outside the page text (metadata) have no such limit.
"""

import io
import zlib
from pathlib import Path
from typing import Any

import pymupdf
from PIL import Image, TiffImagePlugin


def write_pdf(path: Path, pages: list[list[str]], rotation: int = 0) -> Path:
    """Write a PDF with one text block per line of each page."""
    document = pymupdf.open()
    for lines in pages:
        page = document.new_page()
        write_lines(page, lines)
        if rotation:
            page.set_rotation(rotation)
    document.save(path)
    document.close()
    return path


def write_lines(
    page: pymupdf.Page, lines: list[str], *, font_size: float = 11, **options: Any
) -> None:
    """Write one line of text every 30 points, from the top left of the page."""
    for offset, line in enumerate(lines):
        page.insert_text(
            (72, 100 + offset * 30), line, fontname="helv", fontsize=font_size, **options
        )


SCAN_DPI = 150
# Pixels darker than this are ink; the scans are black text on white.
INK_LEVEL = 100


def scan_of(lines: list[str], dpi: int = SCAN_DPI) -> pymupdf.Pixmap:
    """Render lines as `write_lines` places them into a greyscale A4 picture: a scan."""
    document = pymupdf.open()
    page = document.new_page()
    write_lines(page, lines)
    picture = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    document.close()
    return picture


def write_searchable_scan(
    path: Path,
    lines: list[str],
    *,
    jpeg: bool = False,
    in_form_xobject: bool = False,
    rotation: int = 0,
    layer_font_size: float = 11,
) -> Path:
    """Write a scan with an OCR text layer: a page-sized picture under invisible text.

    The invisible text (render mode 3) lies where `write_lines` puts it, over
    the ink when `layer_font_size` is the scan's own 11 points. A smaller
    size gives narrower word boxes than the printed words, as a producer's
    OCR layer with poor geometry would.
    """
    document = pymupdf.open()
    page = document.new_page()
    picture = scan_of(lines)
    if in_form_xobject:
        holder = pymupdf.open()
        holder.new_page().insert_image(page.rect, pixmap=picture)
        page.show_pdf_page(page.rect, holder, 0)
    elif jpeg:
        page.insert_image(page.rect, stream=picture.tobytes("jpeg"))
    else:
        page.insert_image(page.rect, pixmap=picture)
    write_lines(page, lines, font_size=layer_font_size, render_mode=3)
    if rotation:
        page.set_rotation(rotation)
    document.save(path)
    document.close()
    return path


CONTACT_EMAIL = "jan.novak@example.com"
LAUNCH_PATH = "C:/Users/jnovak/cv.docx"
BOOKMARK_URI = "https://example.com/jnovak"
INDIRECT_KEYWORDS = "Nová účetní"
METADATA_DATE = "D:20260101120000"
ROTATED_WORD = "HERE"
STRUCTURE_ALT = "Photo of Jan Novak"
STRUCTURE_ACTUAL_TEXT = f"write to {CONTACT_EMAIL}"
# PyMuPDF creates its widget type constants at runtime.
TEXT_FIELD = pymupdf.PDF_WIDGET_TYPE_TEXT  # pyright: ignore[reportAttributeAccessIssue]
# Encloses ROTATED_WORD as inserted at (500, 800), in unrotated coordinates.
ROTATED_TARGET = pymupdf.Rect(495, 785, 545, 806)
XMP_PACKET = (
    '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
    '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
    '<rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/">'
    f"<dc:creator>{CONTACT_EMAIL}</dc:creator>"
    "</rdf:Description></rdf:RDF></x:xmpmeta>"
)


def add_text_field(page: pymupdf.Page, rect: pymupdf.Rect, name: str, value: str) -> None:
    # PyMuPDF initializes every Widget field to None, which pyright takes as its type.
    widget: Any = pymupdf.Widget()
    widget.field_name = name
    widget.field_type = TEXT_FIELD
    widget.rect = rect
    widget.field_value = value
    page.add_widget(widget)


def write_surfaces_pdf(path: Path) -> Path:
    """Write a PDF carrying one of every surface kind; page 2 is rotated."""
    document = pymupdf.open()
    # Creating a page detaches Page objects fetched earlier, so fetch after.
    document.new_page()
    document.new_page()
    first, second = document[0], document[1]

    first.insert_link(
        {
            "kind": pymupdf.LINK_URI,
            "from": pymupdf.Rect(72, 150, 200, 165),
            "uri": "mailto:jan.novak%40example.com",
        }
    )
    mailto_xref = first.annot_xrefs()[-1][0]
    first.insert_link(
        {"kind": pymupdf.LINK_LAUNCH, "from": pymupdf.Rect(72, 170, 200, 185), "file": LAUNCH_PATH}
    )
    internal = {"kind": pymupdf.LINK_GOTO, "from": pymupdf.Rect(72, 190, 200, 205), "page": 1}
    first.insert_link(internal)
    note = first.add_text_annot((300, 300), "Call +420 603 123 456")
    note.set_info(title="Petra Svobodova")
    note.update()
    first.add_file_annot((400, 400), b"attached", "notes.txt", desc=f"notes for {CONTACT_EMAIL}")
    add_text_field(first, pymupdf.Rect(72, 500, 250, 520), "email", CONTACT_EMAIL)

    second.insert_text((500, 800), ROTATED_WORD, fontname="helv", fontsize=11)
    phone = {"kind": pymupdf.LINK_URI, "from": ROTATED_TARGET, "uri": "tel:+420603123456"}
    second.insert_link(phone)
    square = second.add_rect_annot(ROTATED_TARGET)
    square.set_info(content="rotated note")
    square.update()
    add_text_field(second, ROTATED_TARGET, "rotated", "rotated value")
    second.set_rotation(90)

    # Decomposed "á" checks that surface values are NFC-normalized like page text.
    document.set_metadata(
        {
            "title": "CV Jan Nova\u0301k",
            "subject": "   ",
            "creationDate": METADATA_DATE,
            "modDate": METADATA_DATE,
        }
    )
    info_xref = int(document.xref_get_key(-1, "Info")[1].split()[0])
    document.xref_set_key(info_xref, "Company", pymupdf.get_pdf_str("Novak Consulting"))
    # react-pdf stores every value as a separate string object.
    keywords_xref = document.get_new_xref()
    document.update_object(keywords_xref, pymupdf.get_pdf_str(INDIRECT_KEYWORDS))
    document.xref_set_key(info_xref, "Keywords", f"{keywords_xref} 0 R")
    document.set_xml_metadata(XMP_PACKET)
    profile = {"kind": pymupdf.LINK_URI, "uri": BOOKMARK_URI}
    document.set_toc([[1, "Jan Novak", 1, profile], [1, "Contact", 2]])
    document.embfile_add("cv.docx", b"attached", filename="cv.docx", desc="original CV")
    add_structure_tree(document, first.xref, mailto_xref)

    document.save(path)
    document.close()
    return path


def add_structure_tree(document: pymupdf.Document, page_xref: int, link_xref: int) -> None:
    """Tag the document: a figure with alternate text and a link element.

    The link element refers to the link annotation, as tagged PDFs from Word or
    Chrome do; that reference keeps the annotation alive after it is removed
    from its page.
    """
    root = document.get_new_xref()
    document.update_object(root, "<< /Type /StructTreeRoot >>")
    figure = document.get_new_xref()
    document.update_object(
        figure,
        f"<< /Type /StructElem /S /Figure /P {root} 0 R /Pg {page_xref} 0 R"
        f" /Alt {pymupdf.get_pdf_str(STRUCTURE_ALT)} >>",
    )
    link = document.get_new_xref()
    document.update_object(
        link,
        f"<< /Type /StructElem /S /Link /P {root} 0 R"
        f" /ActualText {pymupdf.get_pdf_str(STRUCTURE_ACTUAL_TEXT)}"
        f" /K << /Type /OBJR /Obj {link_xref} 0 R /Pg {page_xref} 0 R >> >>",
    )
    document.xref_set_key(root, "K", f"[{figure} 0 R {link} 0 R]")
    catalog = document.pdf_catalog()
    document.xref_set_key(catalog, "StructTreeRoot", f"{root} 0 R")
    document.xref_set_key(catalog, "MarkInfo", "<< /Marked true >>")


def write_scanned_pdf(
    path: Path,
    pages: list[list[str]],
    rotation: int = 0,
    stamp: str | None = None,
    picture: str = "flate",
) -> Path:
    """Write the pages `write_pdf` would, but each as a picture only: a scan without text.

    `write_pdf` with the same pages and rotation gives the born-digital
    original, whose words are the ground truth of what OCR should read. A
    `stamp` is written as visible text at the foot of every page, as a
    scanner's page stamp would be. `picture` picks how the scan is stored
    (see `SCAN_PICTURES`).
    """
    document = pymupdf.open()
    for lines in pages:
        page = document.new_page()
        SCAN_PICTURES[picture](document, page, scan_of(lines))
        if stamp:
            page.insert_text((72, 820), stamp, fontname="helv", fontsize=8)
        if rotation:
            page.set_rotation(rotation)
    document.save(path)
    document.close()
    return path


def _flate(document: pymupdf.Document, page: pymupdf.Page, scan: pymupdf.Pixmap) -> None:
    del document
    page.insert_image(page.rect, pixmap=scan)


def _jpeg(document: pymupdf.Document, page: pymupdf.Page, scan: pymupdf.Pixmap) -> None:
    del document
    page.insert_image(page.rect, stream=scan.tobytes("jpeg"))


def _cmyk_jpeg(document: pymupdf.Document, page: pymupdf.Page, scan: pymupdf.Pixmap) -> None:
    del document
    encoded = io.BytesIO()
    _pillow(scan).convert("CMYK").save(encoded, format="JPEG")
    page.insert_image(page.rect, stream=encoded.getvalue())


def _ccitt(document: pymupdf.Document, page: pymupdf.Page, scan: pymupdf.Pixmap) -> None:
    """Store the scan as a black-and-white CCITT G4 picture, as office scanners do."""
    encoded = io.BytesIO()
    # One strip for the whole picture: that strip is the raw G4 data a PDF image holds.
    _black_and_white(scan).save(encoded, format="TIFF", compression="group4", strip_size=1 << 30)
    tiff = Image.open(io.BytesIO(encoded.getvalue()))
    assert isinstance(tiff, TiffImagePlugin.TiffImageFile)
    (offset,), (length,) = tiff.tag_v2[273], tiff.tag_v2[279]
    strip = encoded.getvalue()[offset : offset + length]
    _write_raw_picture(
        document,
        page,
        f"<< /Type /XObject /Subtype /Image /Width {scan.width} /Height {scan.height}"
        " /ColorSpace /DeviceGray /BitsPerComponent 1 >>",
        strip,
        "/CCITTFaxDecode",
        f"<< /K -1 /Columns {scan.width} /Rows {scan.height} /BlackIs1 true >>",
    )


def _stencil(document: pymupdf.Document, page: pymupdf.Page, scan: pymupdf.Pixmap) -> None:
    """Store the ink as a 1-bit stencil mask over a plain background photo.

    Compressed searchable scans (mixed raster content) separate the page this
    way: the background as a JPEG, the text as a mask painted in black.
    """
    background = io.BytesIO()
    Image.new("RGB", (scan.width, scan.height), (235, 230, 220)).save(background, format="JPEG")
    page.insert_image(page.rect, stream=background.getvalue())
    _write_raw_picture(
        document,
        page,
        f"<< /Type /XObject /Subtype /Image /Width {scan.width} /Height {scan.height}"
        " /ImageMask true /BitsPerComponent 1 >>",
        zlib.compress(_black_and_white(scan).tobytes()),
        "/FlateDecode",
    )


# Row 198 of a 150 DPI scan lies at 95 points, inside the first line's words.
_STRIP_ROW = 198


def _strips(document: pymupdf.Document, page: pymupdf.Page, scan: pymupdf.Pixmap) -> None:
    """Store the scan as two pictures, split across a line of text, as some scanners do."""
    del document
    whole = _pillow(scan)
    split = _STRIP_ROW * 72 / SCAN_DPI
    for band, crop in (
        (pymupdf.Rect(0, 0, page.rect.width, split), (0, 0, scan.width, _STRIP_ROW)),
        (
            pymupdf.Rect(0, split, page.rect.width, page.rect.height),
            (0, _STRIP_ROW, scan.width, scan.height),
        ),
    ):
        encoded = io.BytesIO()
        whole.crop(crop).save(encoded, format="PNG")
        page.insert_image(band, stream=encoded.getvalue(), keep_proportion=False)


SCAN_PICTURES = {
    "flate": _flate,
    "jpeg": _jpeg,
    "cmyk_jpeg": _cmyk_jpeg,
    "ccitt": _ccitt,
    "stencil": _stencil,
    "strips": _strips,
}
"""How a scan's picture can be stored, by name."""


def _pillow(scan: pymupdf.Pixmap) -> Image.Image:
    return Image.frombytes("L", (scan.width, scan.height), scan.samples)


def _black_and_white(scan: pymupdf.Pixmap) -> Image.Image:
    """Threshold the scan to 1 bit per pixel, white as 1."""
    return _pillow(scan).point([0] * 129 + [255] * 127).convert("1")


def _write_raw_picture(
    document: pymupdf.Document,
    page: pymupdf.Page,
    dictionary: str,
    data: bytes,
    image_filter: str,
    decode_parms: str | None = None,
) -> None:
    """Place a page-sized picture whose stream is written exactly as given.

    PyMuPDF re-encodes what `insert_image` receives, so a placeholder is
    inserted and its object replaced. Writing the stream drops the filter,
    which is set again afterwards.
    """
    placeholder = pymupdf.Pixmap(pymupdf.csGRAY, pymupdf.IRect(0, 0, 1, 1), False)
    xref = page.insert_image(page.rect, pixmap=placeholder)
    document.update_object(xref, dictionary)
    document.update_stream(xref, data, compress=False)
    document.xref_set_key(xref, "Filter", image_filter)
    if decode_parms:
        document.xref_set_key(xref, "DecodeParms", decode_parms)
