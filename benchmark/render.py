"""Turning a benchmark document into a born-digital PDF.

Text is written with MuPDF's bundled Nimbus Sans, embedded as a CID font, so
Czech and Slovak letters survive: the non-embedded standard 14 fonts are
limited to Western European characters. Output is deterministic apart from
the file identifier PyMuPDF generates.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf

from benchmark.spec import DocumentSpec

PAGE = pymupdf.paper_rect("a4")
MARGIN = 56.0
FONT_SIZE = 11
LEADING = 15.0
PARAGRAPH_GAP = 6.0
FIXED_DATE = "D:20260101000000Z"

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
    writer.finish()

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
