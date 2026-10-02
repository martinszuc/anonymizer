"""Turning a benchmark document into a born-digital PDF.

Text is written with MuPDF's bundled Nimbus Sans, embedded as a CID font, so
Czech and Slovak letters survive: the non-embedded standard 14 fonts are
limited to Western European characters. Output is deterministic apart from
the file identifier PyMuPDF generates.

Strings outside the page text are written as producers write them: a text
field with its value drawn into the widget's appearance, a sticky note whose
author is the annotation's title, a document-level attachment with a file
name and description, and an XMP packet of Dublin Core properties.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import pymupdf

from benchmark.spec import DocumentSpec

PAGE = pymupdf.paper_rect("a4")
MARGIN = 56.0
FONT_SIZE = 11
LEADING = 15.0
PARAGRAPH_GAP = 6.0
FIXED_DATE = "D:20260101000000Z"
# PyMuPDF creates its widget type constants at runtime.
TEXT_FIELD: int = pymupdf.PDF_WIDGET_TYPE_TEXT  # pyright: ignore[reportAttributeAccessIssue]
FIELD_GAP = 8.0
NOTE_SIZE = 20.0
ATTACHMENT_CONTENT = b"Synthetic attachment of a benchmark document.\n"

_METADATA_KEYS = {
    "Title": "title",
    "Author": "author",
    "Subject": "subject",
    "Keywords": "keywords",
    "Creator": "creator",
    "Producer": "producer",
}


def render(spec: DocumentSpec, destination: Path) -> Path:
    """Write a document as a PDF.

    Raises:
        ValueError: If the metadata uses a key PyMuPDF cannot write.
    """
    font = pymupdf.Font("helv")
    pdf = pymupdf.open()
    writer = _PageWriter(pdf, font)
    for line in spec.lines:
        writer.paragraph(line)
    for anchor, target in spec.links:
        page, rect = writer.paragraph(anchor)
        page.insert_link({"kind": pymupdf.LINK_URI, "from": rect, "uri": target})
    fields = [(writer.paragraph(label), value) for label, value in spec.fields]
    writer.finish()
    for number, ((page, rect), value) in enumerate(fields):
        _add_text_field(page, rect, f"field{number}", value)
    for number, (author, text) in enumerate(spec.annotations):
        _add_note(pdf[0], number, author, text)
    for number, (filename, description) in enumerate(spec.attachments):
        pdf.embfile_add(
            f"attachment{number}", ATTACHMENT_CONTENT, filename=filename, desc=description
        )
    _fix_attachment_dates(pdf)
    if spec.xmp:
        pdf.set_xml_metadata(_xmp_packet(spec.name, spec.xmp))

    unknown = set(spec.metadata) - set(_METADATA_KEYS)
    if unknown:
        msg = f"{spec.name}: unsupported metadata keys {sorted(unknown)}"
        raise ValueError(msg)
    metadata = {"creationDate": FIXED_DATE, "modDate": FIXED_DATE, "producer": "", "creator": ""}
    metadata |= {_METADATA_KEYS[key]: value for key, value in spec.metadata.items()}
    pdf.set_metadata(metadata)
    if spec.bookmarks:
        pdf.set_toc([[1, title, 1] for title in spec.bookmarks])

    destination.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(destination, garbage=4, deflate=True)
    pdf.close()
    return destination


# Dublin Core elements and the XMP container each is written in: an ordered
# list of people, an unordered set of keywords, or alternatives by language.
_DUBLIN_CORE = {
    "creator": "Seq",
    "contributor": "Seq",
    "subject": "Bag",
    "title": "Alt",
    "description": "Alt",
    "rights": "Alt",
}


def _add_text_field(page: pymupdf.Page, label: pymupdf.Rect, name: str, value: str) -> None:
    """Add a filled text field after its label, up to the right margin."""
    # PyMuPDF's stubs declare a new widget's attributes as None.
    widget: Any = pymupdf.Widget()
    widget.field_name = name
    widget.field_type = TEXT_FIELD
    widget.field_value = value
    widget.text_font = "Helv"
    widget.text_fontsize = FONT_SIZE
    left = label.x1 + FIELD_GAP
    widget.rect = pymupdf.Rect(left, label.y0, PAGE.width - MARGIN, label.y1)
    page.add_widget(widget)


def _add_note(page: pymupdf.Page, number: int, author: str, text: str) -> None:
    """Add a sticky note in the right margin, one below the other."""
    top = MARGIN + number * (NOTE_SIZE + FIELD_GAP)
    note = page.add_text_annot(pymupdf.Point(PAGE.width - MARGIN / 2 - NOTE_SIZE / 2, top), text)
    note.set_info(title=author)
    note.update()


def _fix_attachment_dates(pdf: pymupdf.Document) -> None:
    """Replace the current time PyMuPDF stamps on attached files."""
    for xref in range(1, pdf.xref_length()):
        if pdf.xref_get_key(xref, "Type") == ("name", "/EmbeddedFile"):
            for key in ("CreationDate", "ModDate"):
                pdf.xref_set_key(xref, f"Params/{key}", f"({FIXED_DATE})")


def _xmp_packet(name: str, properties: dict[str, str]) -> str:
    """Write Dublin Core properties as an XMP packet, each a one-item container.

    Raises:
        ValueError: If a property is not a Dublin Core element written here.
    """
    unknown = set(properties) - set(_DUBLIN_CORE)
    if unknown:
        msg = f"{name}: unsupported XMP properties {sorted(unknown)}"
        raise ValueError(msg)
    elements = "".join(
        f"<dc:{key}><rdf:{_DUBLIN_CORE[key]}>"
        + ('<rdf:li xml:lang="x-default">' if _DUBLIN_CORE[key] == "Alt" else "<rdf:li>")
        + f"{escape(value)}</rdf:li></rdf:{_DUBLIN_CORE[key]}></dc:{key}>"
        for key, value in properties.items()
    )
    return (
        '<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        f'<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">{elements}'
        "</rdf:Description></rdf:RDF></x:xmpmeta>"
        '<?xpacket end="w"?>'
    )


class _PageWriter:
    """Writes wrapped paragraphs top to bottom, adding pages as needed."""

    def __init__(self, pdf: pymupdf.Document, font: pymupdf.Font) -> None:
        self.pdf = pdf
        self.font = font
        self.width = PAGE.width - 2 * MARGIN
        self.page: pymupdf.Page | None = None
        self.writer: pymupdf.TextWriter | None = None
        self.y = 0.0

    def paragraph(self, text: str) -> tuple[pymupdf.Page, pymupdf.Rect]:
        """Write one paragraph; return its page and the box of its first line."""
        first: tuple[pymupdf.Page, pymupdf.Rect] | None = None
        for line in self._wrap(text):
            page, writer = self._line_slot()
            baseline = pymupdf.Point(MARGIN, self.y + FONT_SIZE)
            writer.append(baseline, line, font=self.font, fontsize=FONT_SIZE)
            box = pymupdf.Rect(
                MARGIN,
                self.y,
                MARGIN + self._width_of(line),
                self.y + LEADING,
            )
            first = first or (page, box)
            self.y += LEADING
        self.y += PARAGRAPH_GAP
        if first is None:
            msg = "empty paragraph"
            raise ValueError(msg)
        return first

    def finish(self) -> None:
        """Flush the text of the last page."""
        if self.page is not None and self.writer is not None:
            self.writer.write_text(self.page)

    def _line_slot(self) -> tuple[pymupdf.Page, pymupdf.TextWriter]:
        if self.page is None or self.writer is None or self.y + LEADING > PAGE.height - MARGIN:
            self.finish()
            self.page = self.pdf.new_page(width=PAGE.width, height=PAGE.height)
            self.writer = pymupdf.TextWriter(self.page.rect)
            self.y = MARGIN
        return self.page, self.writer

    def _width_of(self, text: str) -> float:
        return self.font.text_length(text, fontsize=FONT_SIZE)

    def _wrap(self, text: str) -> list[str]:
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = f"{current} {word}" if current else word
            if current and self._width_of(candidate) > self.width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines
