"""Page writers: plain paragraphs, and the layout of the phone-photo documents.

`PageWriter` writes wrapped paragraphs top to bottom; every benchmark document
without layout fields is written by it alone. `LayoutWriter` adds a letterhead
and a footer and places the blocks of `spec.Block` between the paragraphs.
Text goes to the text layer in reading order (letterhead, paragraphs and
blocks top to bottom, footer), the order gold items are collected in. A
stamp is a picture and a signature is vector strokes, so neither adds text; a
line to be filled in by hand is a printed label and a ruled line.
"""

from __future__ import annotations

import random

import pymupdf

from benchmark.spec import (
    Block,
    Boxes,
    DocumentSpec,
    Handwritten,
    Letterhead,
    Signature,
    Stamp,
    Table,
)

PAGE = pymupdf.paper_rect("a4")
MARGIN = 56.0
FONT_SIZE = 11
LEADING = 15.0
PARAGRAPH_GAP = 6.0

BRAND = (0.12, 0.27, 0.45)
LOGO_FILL = (0.93, 0.95, 0.98)
RULE = (0.35, 0.35, 0.35)
HEADER_FILL = (0.9, 0.9, 0.9)
PEN = (0.08, 0.12, 0.42)
STAMP_INK = (0.2, 0.28, 0.72)

LOGO_SIZE = 46.0
LETTERHEAD_HEIGHT = 64.0
FOOTER_SIZE = 8
FOOTER_HEIGHT = 20.0
CELL_SIZE = 10
CELL_LEADING = 12.5
CELL_PAD = 4.0
BOX_LABEL_SIZE = 7
BOX_GAP = 6.0
HANDWRITING_HEIGHT = 30.0
SIGNATURE_WIDTH = 170.0
SIGNATURE_HEIGHT = 40.0
STAMP_RADIUS = 48.0
STAMP_DPI = 300
STAMP_SIZE = 7
STAMP_ANGLE = -14.0
STAMP_OFFSET = 215.0


def wrap(text: str, font: pymupdf.Font, size: int, width: float) -> list[str]:
    """Break text into lines no wider than `width`, at spaces only."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if current and font.text_length(candidate, fontsize=size) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


class PageWriter:
    """Writes wrapped paragraphs top to bottom, adding pages as needed."""

    bottom = PAGE.height - MARGIN

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
        for line in wrap(text, self.font, FONT_SIZE, self.width):
            page, writer = self._reserve(LEADING)
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

    def _reserve(self, height: float) -> tuple[pymupdf.Page, pymupdf.TextWriter]:
        """Return the page and writer with `height` free below `y`, starting a page if needed."""
        if self.page is None or self.writer is None or self.y + height > self.bottom:
            self.finish()
            self.page = self.pdf.new_page(width=PAGE.width, height=PAGE.height)
            self.writer = pymupdf.TextWriter(self.page.rect)
            self.y = self._top(self.page)
        return self.page, self.writer

    def _top(self, page: pymupdf.Page) -> float:
        del page
        return MARGIN

    def _width_of(self, text: str) -> float:
        return self.font.text_length(text, fontsize=FONT_SIZE)


class LayoutWriter(PageWriter):
    """A page writer for a document with layout fields."""

    bottom = PAGE.height - MARGIN - FOOTER_HEIGHT

    def __init__(self, pdf: pymupdf.Document, font: pymupdf.Font, spec: DocumentSpec) -> None:
        super().__init__(pdf, font)
        self.spec = spec
        self.bold = pymupdf.Font("hebo")
        self.stamps: list[tuple[pymupdf.Rect, Stamp]] = []

    def body(self) -> None:
        """Write the paragraphs with the blocks placed between them."""
        blocks = list(self.spec.blocks)
        for position in range(len(self.spec.lines) + 1):
            while blocks and blocks[0].after == position:
                self._block(blocks.pop(0))
            if position < len(self.spec.lines):
                self.paragraph(self.spec.lines[position])

    def finish(self) -> None:
        """Flush the page's text, then its footer and stamps, which lie over the text."""
        if self.page is None or self.writer is None:
            return
        super().finish()
        if self.spec.footer:
            self._footer(self.page)
        for rect, stamp in self.stamps:
            self.page.insert_image(rect, pixmap=_stamp_picture(stamp, self.bold))
        self.stamps = []

    def _top(self, page: pymupdf.Page) -> float:
        letterhead = self.spec.letterhead
        if letterhead is None or page.number != 0:
            return MARGIN
        self._letterhead(page, letterhead)
        return MARGIN + LETTERHEAD_HEIGHT

    def _letterhead(self, page: pymupdf.Page, letterhead: Letterhead) -> None:
        top = MARGIN - 16
        logo = pymupdf.Rect(MARGIN, top, MARGIN + LOGO_SIZE, top + LOGO_SIZE)
        page.draw_rect(logo, color=BRAND, fill=LOGO_FILL, width=1.4)
        roof = [
            pymupdf.Point(logo.x0 + 9, logo.y0 + 20),
            pymupdf.Point(logo.x0 + LOGO_SIZE / 2, logo.y0 + 7),
            pymupdf.Point(logo.x1 - 9, logo.y0 + 20),
        ]
        page.draw_polyline(roof, color=BRAND, width=2.2)
        text = pymupdf.TextWriter(page.rect, color=BRAND)
        logo_size = 13
        logo_width = self.bold.text_length(letterhead.logo, fontsize=logo_size)
        text.append(
            pymupdf.Point(logo.x0 + (LOGO_SIZE - logo_width) / 2, logo.y1 - 9),
            letterhead.logo,
            font=self.bold,
            fontsize=logo_size,
        )
        left = logo.x1 + 12
        text.append(
            pymupdf.Point(left, top + 15), letterhead.organisation, font=self.bold, fontsize=15
        )
        for number, line in enumerate(letterhead.address):
            baseline = pymupdf.Point(left, top + 28 + 10 * number)
            text.append(baseline, line, font=self.font, fontsize=9)
        text.write_text(page)
        rule = top + LOGO_SIZE + 6
        page.draw_line((MARGIN, rule), (PAGE.width - MARGIN, rule), color=BRAND, width=1.0)

    def _footer(self, page: pymupdf.Page) -> None:
        rule = PAGE.height - MARGIN - 8
        page.draw_line((MARGIN, rule), (PAGE.width - MARGIN, rule), color=RULE, width=0.5)
        text = pymupdf.TextWriter(page.rect, color=RULE)
        for number, line in enumerate(wrap(self.spec.footer, self.font, FOOTER_SIZE, self.width)):
            baseline = pymupdf.Point(MARGIN, rule + 10 + 10 * number)
            text.append(baseline, line, font=self.font, fontsize=FOOTER_SIZE)
        text.write_text(page)

    def _block(self, block: Block) -> None:
        if isinstance(block, Table):
            self._table(block)
        elif isinstance(block, Boxes):
            self._boxes(block)
        elif isinstance(block, Handwritten):
            self._handwritten(block)
        elif isinstance(block, Signature):
            self._signature(block)
        else:
            self._stamp(block)

    def _table(self, table: Table) -> None:
        shares = table.widths or tuple(1.0 for _ in table.columns)
        widths = [self.width * share / sum(shares) for share in shares]
        self._row(table.columns, widths, header=True)
        for row in table.rows:
            self._row(row, widths, header=False)
        self.y += PARAGRAPH_GAP

    def _row(self, cells: tuple[str, ...], widths: list[float], *, header: bool) -> None:
        font = self.bold if header else self.font
        wrapped = [
            wrap(cell, font, CELL_SIZE, width - 2 * CELL_PAD)
            for cell, width in zip(cells, widths, strict=True)
        ]
        height = max(len(lines) for lines in wrapped) * CELL_LEADING + 2 * CELL_PAD
        page, writer = self._reserve(height)
        left = MARGIN
        for lines, width in zip(wrapped, widths, strict=True):
            cell = pymupdf.Rect(left, self.y, left + width, self.y + height)
            page.draw_rect(cell, color=RULE, fill=HEADER_FILL if header else None, width=0.6)
            for number, line in enumerate(lines):
                baseline = self.y + CELL_PAD + CELL_SIZE + number * CELL_LEADING
                writer.append(
                    pymupdf.Point(left + CELL_PAD, baseline), line, font=font, fontsize=CELL_SIZE
                )
            left += width
        self.y += height

    def _boxes(self, boxes: Boxes) -> None:
        width = (self.width - (boxes.per_row - 1) * BOX_GAP) / boxes.per_row
        for start in range(0, len(boxes.fields), boxes.per_row):
            row = boxes.fields[start : start + boxes.per_row]
            values = [wrap(value, self.font, FONT_SIZE, width - 2 * CELL_PAD) for _, value in row]
            lines = max(len(value) for value in values)
            height = lines * LEADING + BOX_LABEL_SIZE + 3 * CELL_PAD
            page, writer = self._reserve(height + BOX_GAP)
            for column, ((label, _), value) in enumerate(zip(row, values, strict=True)):
                left = MARGIN + column * (width + BOX_GAP)
                box = pymupdf.Rect(left, self.y, left + width, self.y + height)
                page.draw_rect(box, color=RULE, width=0.7)
                writer.append(
                    pymupdf.Point(left + CELL_PAD, self.y + CELL_PAD + BOX_LABEL_SIZE),
                    label,
                    font=self.font,
                    fontsize=BOX_LABEL_SIZE,
                )
                for number, line in enumerate(value):
                    baseline = self.y + 2 * CELL_PAD + BOX_LABEL_SIZE + FONT_SIZE + number * LEADING
                    writer.append(
                        pymupdf.Point(left + CELL_PAD, baseline),
                        line,
                        font=self.font,
                        fontsize=FONT_SIZE,
                    )
            self.y += height + BOX_GAP
        self.y += PARAGRAPH_GAP

    def _handwritten(self, field: Handwritten) -> None:
        page, writer = self._reserve(HANDWRITING_HEIGHT)
        baseline = self.y + HANDWRITING_HEIGHT - 8
        writer.append(
            pymupdf.Point(MARGIN, baseline), field.label, font=self.font, fontsize=FONT_SIZE
        )
        start = MARGIN + self._width_of(field.label) + 6
        end = PAGE.width - MARGIN
        page.draw_line((start, baseline + 2), (end, baseline + 2), color=RULE, width=0.6)
        self.y += HANDWRITING_HEIGHT + PARAGRAPH_GAP

    def _signature(self, signature: Signature) -> None:
        page, writer = self._reserve(SIGNATURE_HEIGHT)
        baseline = self.y + SIGNATURE_HEIGHT - 8
        writer.append(
            pymupdf.Point(MARGIN, baseline), signature.label, font=self.font, fontsize=FONT_SIZE
        )
        start = MARGIN + self._width_of(signature.label) + 8
        line = baseline + 2
        page.draw_line((start, line), (start + SIGNATURE_WIDTH, line), color=RULE, width=0.6)
        _scribble(page, signature.seed, pymupdf.Point(start + 10, line - 6))
        self.y += SIGNATURE_HEIGHT + PARAGRAPH_GAP

    def _stamp(self, stamp: Stamp) -> None:
        self._reserve(0)
        # Pressed over what was written last (usually the signature line), as by hand.
        centre = pymupdf.Point(MARGIN + STAMP_OFFSET, self.y - STAMP_RADIUS / 2 - PARAGRAPH_GAP)
        rect = pymupdf.Rect(
            centre.x - STAMP_RADIUS,
            centre.y - STAMP_RADIUS,
            centre.x + STAMP_RADIUS,
            centre.y + STAMP_RADIUS,
        )
        self.stamps.append((rect, stamp))


def _scribble(page: pymupdf.Page, seed: str, start: pymupdf.Point) -> None:
    """Draw a signature: loops of cubic curves along the line, then a stroke back under them."""
    draw = random.Random(seed)
    shape = page.new_shape()
    capital = pymupdf.Point(start.x + draw.uniform(8, 14), start.y + 2)
    shape.draw_bezier(
        start,
        pymupdf.Point(start.x - 4, start.y - draw.uniform(26, 34)),
        pymupdf.Point(start.x + 22, start.y - draw.uniform(22, 30)),
        capital,
    )
    point = capital
    for _ in range(draw.randint(5, 8)):
        step = draw.uniform(9, 22)
        end = pymupdf.Point(point.x + step, start.y + draw.uniform(-6, 4))
        # A control point behind the start of a stroke makes the pen loop back.
        shape.draw_bezier(
            point,
            pymupdf.Point(point.x + step * draw.uniform(-0.5, 0.6), start.y - draw.uniform(4, 22)),
            pymupdf.Point(point.x + step * draw.uniform(0.4, 1.4), start.y + draw.uniform(0, 10)),
            end,
        )
        point = end
    shape.draw_bezier(
        point,
        pymupdf.Point(point.x + 12, start.y + 10),
        pymupdf.Point(start.x - 6, start.y + 12),
        pymupdf.Point(start.x + draw.uniform(0, 15), start.y + 7),
    )
    shape.finish(color=PEN, width=1.1, closePath=False, lineCap=1, lineJoin=1)
    shape.commit()


def _stamp_picture(stamp: Stamp, font: pymupdf.Font) -> pymupdf.Pixmap:
    """Draw a round stamp on a page of its own and return it as a transparent picture."""
    size = 2 * STAMP_RADIUS
    sheet = pymupdf.open()
    page = sheet.new_page(width=size, height=size)
    centre = pymupdf.Point(STAMP_RADIUS, STAMP_RADIUS)
    shape = page.new_shape()
    shape.draw_circle(centre, STAMP_RADIUS - 2)
    shape.finish(color=STAMP_INK, width=2.2, stroke_opacity=0.85)
    shape.draw_circle(centre, STAMP_RADIUS - 7)
    shape.finish(color=STAMP_INK, width=0.8, stroke_opacity=0.85)
    shape.commit()
    room = 1.75 * (STAMP_RADIUS - 9)
    if max(font.text_length(line, fontsize=STAMP_SIZE) for line in stamp.lines) > room:
        msg = f"a stamp line is too wide: {stamp.lines}"
        raise ValueError(msg)
    leading = STAMP_SIZE * 1.25
    text = pymupdf.TextWriter(page.rect, color=STAMP_INK)
    top = STAMP_RADIUS - leading * (len(stamp.lines) - 1) / 2 + STAMP_SIZE / 3
    for number, line in enumerate(stamp.lines):
        width = font.text_length(line, fontsize=STAMP_SIZE)
        text.append(
            pymupdf.Point(STAMP_RADIUS - width / 2, top + number * leading),
            line,
            font=font,
            fontsize=STAMP_SIZE,
        )
    text.write_text(page, morph=(centre, pymupdf.Matrix(STAMP_ANGLE)))
    picture = page.get_pixmap(dpi=STAMP_DPI, alpha=True)
    sheet.close()
    return picture
