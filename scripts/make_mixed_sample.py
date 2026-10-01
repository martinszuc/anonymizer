"""Generate a four-page PDF that mixes every kind of input the pipeline meets.

    uv run python scripts/make_mixed_sample.py [-o data/samples/mixed-synthetic.pdf]

Every value is invented. The output is git-ignored; only this script is committed.

| Page | Content | Text layer |
|---|---|---|
| 1 | typed form, link, form field, bookmark, metadata, attachment | yes |
| 2 | the same kind of form, scanned: skewed, speckled, JPEG | no |
| 3 | values in a handwriting font, scanned | no |
| 4 | typed text beside a scanned stamp and signature | partly |

Pages 2 and 3 cannot be read until OCR exists; that is what they are for.
A handwriting font only imitates handwriting: it tests the plumbing, not recognition quality.
Without the macOS font the page uses an italic serif, which is not handwriting at all.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import pymupdf

PAGE = pymupdf.paper_rect("a4")
MARGIN = 56.0
SCAN_DPI = 200
SKEW_DEGREES = 1.2
HANDWRITING_FONTS = [Path("/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf")]
# MuPDF's bundled italic serif, used when no handwriting font is installed.
FALLBACK_FONT = "tiit"
SEED = 20260930

FORM_LINES = [
    "Žádost o vydání potvrzení",
    "Jméno: Tereza Procházková",
    "Datum narození: 14. 3. 1991",
    "Rodné číslo: 910314/0013",
    "Adresa: Kounicova 684/12, 602 00 Brno",
    "E-mail: tereza.prochazkova@example.com",
    "Telefon: +420 777 123 456",
    "IBAN: CZ65 0800 0000 1920 0014 5399",
]
HANDWRITTEN_LINES = [
    "Jméno: Ondřej Dvořák",
    "Telefon: 603 987 654",
    "E-mail: ondrej.dvorak@example.com",
    "Adresa: Masarykova 25, 602 00 Brno",
]


def main() -> None:
    """Parse arguments and write the sample."""
    parser = argparse.ArgumentParser(description="Generate the mixed synthetic sample PDF.")
    parser.add_argument("-o", "--out", type=Path, default=Path("data/samples/mixed-synthetic.pdf"))
    args = parser.parse_args()
    write_sample(args.out)
    print(f"wrote {args.out}")


def write_sample(destination: Path) -> None:
    """Write the four-page sample to `destination`."""
    rng = random.Random(SEED)
    pdf = pymupdf.open()
    _typed_page(pdf)
    _scanned_page(pdf, FORM_LINES, pymupdf.Font("helv"), rng)
    _scanned_page(pdf, HANDWRITTEN_LINES, _handwriting_font(), rng, size=22, leading=44)
    _stamp_page(pdf, rng)
    pdf.set_metadata(
        {
            "title": "Žádost, Tereza Procházková",
            "author": "Tereza Procházková",
            "creationDate": "D:20260101000000Z",
            "modDate": "D:20260101000000Z",
        }
    )
    pdf.set_toc([[1, "Žádost", 1], [1, "Sken", 2], [1, "Ručně psané", 3], [1, "Razítko", 4]])
    pdf.embfile_add("poznamka.txt", b"Kontakt: ondrej.dvorak@example.com", desc="note")
    destination.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(destination, garbage=4, deflate=True)
    pdf.close()


def _handwriting_font() -> pymupdf.Font:
    """Return the first installed handwriting font, else an italic that only stands in for one."""
    for path in HANDWRITING_FONTS:
        if path.exists():
            return pymupdf.Font(fontfile=str(path))
    return pymupdf.Font(FALLBACK_FONT)


def _typed_page(pdf: pymupdf.Document) -> None:
    page = pdf.new_page(width=PAGE.width, height=PAGE.height)
    writer = pymupdf.TextWriter(page.rect)
    font = pymupdf.Font("helv")
    y = MARGIN
    for line in FORM_LINES:
        writer.append((MARGIN, y), line, font=font, fontsize=12)
        y += 20
    writer.write_text(page)
    anchor = pymupdf.Rect(MARGIN, y + 6, MARGIN + 160, y + 22)
    page.insert_textbox(anchor, "Portfolio", fontsize=12, fontname="helv")
    page.insert_link(
        {"kind": pymupdf.LINK_URI, "from": anchor, "uri": "https://github.com/tereza-demo"}
    )
    field = pymupdf.Widget()
    field.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT  # pyright: ignore[reportAttributeAccessIssue]
    field.field_name = "kontakt"  # pyright: ignore[reportAttributeAccessIssue]
    field.field_value = "Kateřina Veselá"  # pyright: ignore[reportAttributeAccessIssue]
    field.rect = pymupdf.Rect(MARGIN, y + 40, MARGIN + 220, y + 60)  # pyright: ignore[reportAttributeAccessIssue]
    page.add_widget(field)


def _scanned_page(
    pdf: pymupdf.Document,
    lines: list[str],
    font: pymupdf.Font,
    rng: random.Random,
    size: int = 12,
    leading: int = 20,
) -> None:
    """Add a page holding only a degraded picture of `lines`."""
    source = pymupdf.open()
    sheet = source.new_page(width=PAGE.width, height=PAGE.height)
    writer = pymupdf.TextWriter(sheet.rect)
    y = MARGIN
    for line in lines:
        writer.append((MARGIN, y), line, font=font, fontsize=size)
        y += leading
    pivot = pymupdf.Point(PAGE.width / 2, PAGE.height / 2)
    writer.write_text(sheet, morph=(pivot, pymupdf.Matrix(SKEW_DEGREES)))
    _add_to_pdf(pdf, _speckled(sheet, rng))


def _stamp_page(pdf: pymupdf.Document, rng: random.Random) -> None:
    """Typed text plus a scanned stamp region with no text layer of its own."""
    stamp_sheet = pymupdf.open().new_page(width=200, height=90)
    stamp_sheet.draw_rect(pymupdf.Rect(4, 4, 196, 86), color=(0.1, 0.2, 0.7), width=2)
    stamp_sheet.insert_textbox(
        pymupdf.Rect(12, 18, 188, 76),
        "Magistrát města Brna\nPodepsáno: J. Novotný",
        fontsize=11,
        fontname="helv",
        color=(0.1, 0.2, 0.7),
        align=pymupdf.TEXT_ALIGN_CENTER,
    )
    pix = _speckled(stamp_sheet, rng, dpi=SCAN_DPI)
    page = pdf.new_page(width=PAGE.width, height=PAGE.height)
    page.insert_textbox(
        pymupdf.Rect(MARGIN, MARGIN, PAGE.width - MARGIN, 140),
        "Potvrzení převzal: Martin Kučera, tel. 608 111 222.",
        fontsize=12,
        fontname="helv",
    )
    page.insert_image(pymupdf.Rect(MARGIN, 180, MARGIN + 200, 270), stream=pix.tobytes("jpeg"))


def _speckled(sheet: pymupdf.Page, rng: random.Random, dpi: int = SCAN_DPI) -> pymupdf.Pixmap:
    """Rasterize a page to grey and add scanner-like speckle."""
    pix = sheet.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    samples = bytearray(pix.samples)
    for _ in range(len(samples) // 400):
        samples[rng.randrange(len(samples))] = rng.randrange(150, 230)
    return pymupdf.Pixmap(pymupdf.csGRAY, pix.width, pix.height, bytes(samples), False)


def _add_to_pdf(pdf: pymupdf.Document, pix: pymupdf.Pixmap) -> None:
    page = pdf.new_page(width=PAGE.width, height=PAGE.height)
    page.insert_image(page.rect, stream=pix.tobytes("jpeg"))


if __name__ == "__main__":
    main()
