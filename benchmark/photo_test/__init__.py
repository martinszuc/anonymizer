"""The phone-photo test documents: the 22 Czech and Slovak benchmark documents as printed.

Each file in `documents/` is the benchmark document of the same name
(`benchmark/documents/`) laid out like real paperwork: a letterhead, a footer
with a reference id, tables, form fields in boxes, a stamp, signatures and
lines filled in by hand. The planted items are those on the benchmark
document's page, no more and no fewer (`tests/benchmark/test_photo_test.py`);
some sit in a table or a box, and some are written by hand (carrier
`handwritten`, listed on the fill-in sheet). Strings outside the page
(metadata, links, form fields) are left out: a photo shows the page only.

The benchmark itself never reads these files, so its numbers do not move.
Organisation names in letterheads and stamps are the invented ones the
benchmark documents already use; letterhead addresses and IČOs are invented.

Command: `python -m benchmark photo-test --out DIR` writes `rq8-print.pdf`,
`manifest.md`, `fill-in.pdf`, `gold.json` and one PDF per document.
"""

from __future__ import annotations

from pathlib import Path

from benchmark.print_pack import write_pack
from benchmark.spec import load_documents

DOCUMENTS = Path(__file__).parent / "documents"
PACK = "rq8-print.pdf"
MANIFEST = "manifest.md"
FILL_IN = "fill-in.pdf"
TITLE = "Print order (photograph in this order, every condition)"


def render_print(out: Path) -> Path:
    """Write the test set's print pack, manifest, fill-in sheet and gold into `out`.

    Returns:
        The path of `gold.json`.
    """
    return write_pack(
        load_documents(DOCUMENTS),
        out,
        pack=PACK,
        manifest_name=MANIFEST,
        fill_in=FILL_IN,
        title=TITLE,
        set_name="test set",
    )
