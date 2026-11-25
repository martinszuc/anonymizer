"""Layout fields of a document: absent, nothing changes; present, the ground truth stays exact."""

import hashlib
import json
from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import load_document

from benchmark.render import render
from benchmark.score import page_locations
from benchmark.spec import (
    Boxes,
    Handwritten,
    Signature,
    Stamp,
    Table,
    load_document_spec,
    load_documents,
    visible_text,
)

DIGESTS = Path(__file__).parent / "render_digests.json"

LAID_OUT = """
language = "cs"
kind = "invoice"
footer = "Č. j. VK-2026/0418 · Vodárenská 7, 602 00 Brno"
lines = [
  "Faktura č. 2026001234",
  "Odběratel: [[person:Jan Novák]], [[address:Lidická 1879/48, 602 00 Brno]]",
  "Celkem k úhradě: 18 000 Kč",
]

[letterhead]
organisation = "Vodárny Kraví hora s.r.o."
address = ["Vodárenská 7", "602 00 Brno"]
logo = "VK"

[[blocks]]
type = "table"
after = 2
columns = ["Položka", "Cena"]
widths = [3, 1]
rows = [
  [
    "Měření tlaku v přípojce domu, kterou objednal [[person:Jan Novák]] pro dům v ulici Lidická",
    "900 Kč",
  ],
  ["Doprava", "[[phone:603 555 120]]"],
]

[[blocks]]
type = "boxes"
after = 2
per_row = 2
fields = [
  ["Jméno", "[[person:Petr Malý]]"],
  ["Adresa", "[[address:Polní 3, 586 01 Jihlava]]"],
  ["Telefon", "[[phone:777 123 456]]"],
]

[[blocks]]
type = "handwritten"
after = 3
label = "Převzal:"
text = "[[person:Karel Dvořák]], Brno"

[[blocks]]
type = "signature"
after = 3
label = "Podpis:"
seed = "test"

[[blocks]]
type = "stamp"
after = 3
lines = ["Vodárny Kraví hora", "Brno"]
"""


def _digest(path: Path) -> str:
    """Hash every PDF object; the file identifier PyMuPDF draws at random is not one."""
    digest = hashlib.sha256()
    with pymupdf.open(path) as pdf:
        for xref in range(1, pdf.xref_length()):
            digest.update(pdf.xref_object(xref, compressed=True).encode())
            if pdf.xref_is_stream(xref):
                digest.update(pdf.xref_stream(xref) or b"")
    return digest.hexdigest()


@pytest.fixture
def laid_out(tmp_path: Path):
    path = tmp_path / "doc.toml"
    path.write_text(LAID_OUT, encoding="utf-8")
    spec = load_document_spec(path)
    pdf = render(spec, tmp_path / "doc.pdf")
    return spec, pdf


def test_documents_without_layout_render_as_before(tmp_path: Path):
    # Recorded before layout fields existed. A deliberate edit of a benchmark
    # document changes its digest; record the new one with that edit.
    expected = json.loads(DIGESTS.read_text(encoding="utf-8"))
    rendered = {
        spec.name: _digest(render(spec, tmp_path / f"{spec.name}.pdf")) for spec in load_documents()
    }
    assert rendered == expected
    assert not any(spec.laid_out for spec in load_documents())


def test_blocks_are_read_in_reading_order(laid_out):
    spec, _ = laid_out
    assert [type(block) for block in spec.blocks] == [Table, Boxes, Handwritten, Signature, Stamp]
    assert [(item.text, item.carrier) for item in spec.gold] == [
        ("Jan Novák", "page"),
        ("Lidická 1879/48, 602 00 Brno", "page"),
        ("Jan Novák", "page"),
        ("603 555 120", "page"),
        ("Petr Malý", "page"),
        ("Polní 3, 586 01 Jihlava", "page"),
        ("777 123 456", "page"),
        ("Karel Dvořák", "handwritten"),
    ]
    assert spec.blocks[2] == Handwritten(3, "Převzal:", "Karel Dvořák, Brno")
    assert "Převzal:" in visible_text(spec)
    assert "Karel Dvořák, Brno" not in visible_text(spec)


def test_every_printed_item_is_located_whole(laid_out):
    spec, pdf = laid_out
    document = load_document(pdf, language="cs")
    assert len(document.pages) == 1
    located = page_locations(spec, document)
    text = document.pages[0].text
    for index, item in enumerate(spec.gold):
        if item.carrier == "handwritten":
            assert index not in located
            continue
        page, start, end = located[index] or (None, 0, 0)
        assert page == 0, item
        assert " ".join(text[start:end].split()) == item.text
    for printed in ("Vodárny Kraví hora s.r.o.", "Č. j. VK-2026/0418", "Položka", "Převzal:"):
        assert printed in text


def test_stamp_and_signature_add_no_text(laid_out):
    _, pdf = laid_out
    text = load_document(pdf, language="cs").pages[0].text
    assert "Karel Dvořák" not in text
    assert text.count("Vodárny Kraví hora") == 1  # the letterhead, not the stamp
    with pymupdf.open(pdf) as rendered:
        page = rendered[0]
        assert len(page.get_image_info()) == 1
        curves = [item for path in page.get_drawings() for item in path["items"] if item[0] == "c"]
        assert len(curves) >= 6


def test_a_signature_is_the_same_for_the_same_seed(laid_out, tmp_path: Path):
    spec, pdf = laid_out
    again = render(spec, tmp_path / "again.pdf")
    assert _digest(pdf) == _digest(again)


@pytest.mark.parametrize(
    ("block", "message"),
    [
        ('type = "table"\nafter = 1\ncolumns = ["A", "B"]\nrows = [["x"]]', "do not match"),
        ('type = "table"\nafter = 1\ncolumns = ["A"]\nrows = [["x"]]\nwidths = [1, 2]', "match"),
        ('type = "frame"\nafter = 1', "unknown block type"),
        ('type = "stamp"\nafter = 5\nlines = ["A"]', "past the end"),
    ],
)
def test_bad_blocks_are_refused(tmp_path: Path, block: str, message: str):
    path = tmp_path / "doc.toml"
    path.write_text(f'language = "cs"\nkind = "form"\nlines = ["A"]\n[[blocks]]\n{block}\n')
    with pytest.raises(ValueError, match=message):
        load_document_spec(path)
