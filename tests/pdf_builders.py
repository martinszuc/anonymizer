"""Minimal PDFs written by the tests themselves.

Fixtures are generated rather than committed: a PDF in the repository would be
an opaque binary, and a realistic labelled corpus is a separate project. Page
text is Latin-1 only, because the base-14 Helvetica font cannot encode `č` or
`ř`; strings outside the page text (metadata) have no such limit.
"""

from pathlib import Path
from typing import Any

import pymupdf


def write_pdf(path: Path, pages: list[list[str]], rotation: int = 0) -> Path:
    """Write a PDF with one text block per line of each page."""
    document = pymupdf.open()
    for lines in pages:
        page = document.new_page()
        for offset, line in enumerate(lines):
            page.insert_text((72, 100 + offset * 30), line, fontname="helv", fontsize=11)
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
