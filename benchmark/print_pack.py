"""Print packs of the phone-photo documents: PDFs, gold items, print order, fill-in sheet.

A pack is every page in print order in one PDF, a manifest (the print order
as a Markdown table, read back by `photo_files.read_manifest`), `gold.json`
and, when any document has lines to be filled in by hand, a fill-in sheet:
per document and line, the exact text to write there. That text is the
ground truth of those items; the sheet is never photographed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pymupdf

from benchmark.render import render
from benchmark.spec import DocumentSpec, Handwritten, Table

FILL_IN_NOTE = (
    "Write each text exactly as given (letters, diacritics, spaces and punctuation), in pen, "
    "on the ruled line after its printed label. Fill in every page before photographing it. "
    "This sheet is the ground truth of the handwritten items and is never photographed."
)


def write_pack(
    specs: list[DocumentSpec],
    out: Path,
    *,
    pack: str,
    manifest_name: str,
    fill_in: str,
    title: str,
    set_name: str,
) -> Path:
    """Render every document and write the pack, manifest, gold and fill-in sheet into `out`.

    Args:
        specs: Documents in print order.
        out: Output directory; PDFs of single documents go to `out/pdf/`.
        pack: File name of the pack.
        manifest_name: File name of the manifest.
        fill_in: File name of the fill-in sheet (written only when needed).
        title: Heading of the manifest.
        set_name: Which set the pack is, in the fill-in sheet's heading.

    Returns:
        The path of `gold.json`.
    """
    out.mkdir(parents=True, exist_ok=True)
    pdfs = [render(spec, out / "pdf" / f"{spec.name}.pdf") for spec in specs]
    pages = [page_count(pdf) for pdf in pdfs]
    gold = [gold_entry(spec, count) for spec, count in zip(specs, pages, strict=True)]
    gold_path = out / "gold.json"
    gold_path.write_text(json.dumps(gold, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    concatenate(pdfs, out / pack)
    (out / manifest_name).write_text(manifest(specs, pages, title), encoding="utf-8")
    sheet = fill_in_sheet(specs, set_name)
    if sheet is not None:
        render(sheet, out / fill_in)
    return gold_path


def manifest(specs: list[DocumentSpec], pages: list[int], title: str) -> str:
    """Return the print order as a Markdown table, with the total number of pages."""
    rows = [
        f"| {number} | {spec.name} | {count} |"
        for number, (spec, count) in enumerate(zip(specs, pages, strict=True), start=1)
    ]
    handwritten = sum(isinstance(block, Handwritten) for spec in specs for block in spec.blocks)
    lines = [
        f"# {title}",
        "",
        "| # | document | pages |",
        "|---|---|---|",
        *rows,
        "",
        f"Total: {len(specs)} documents, {sum(pages)} pages.",
        "",
    ]
    if handwritten:
        lines += [f"Lines to fill in by hand: {handwritten} (see the fill-in sheet).", ""]
    return "\n".join(lines)


def fill_in_sheet(specs: list[DocumentSpec], set_name: str) -> DocumentSpec | None:
    """Return the fill-in sheet as a document, or None when nothing is written by hand.

    Documents are numbered as in the manifest.
    """
    lines = [f"Fill-in sheet of the {set_name}", FILL_IN_NOTE]
    blocks: list[Table] = []
    for number, spec in enumerate(specs, start=1):
        rows = tuple(
            (block.label, block.text) for block in spec.blocks if isinstance(block, Handwritten)
        )
        if not rows:
            continue
        lines.append(f"{number}. {spec.name}")
        blocks.append(Table(len(lines), ("Printed label", "Write exactly"), rows, (2.0, 3.0)))
    if not blocks:
        return None
    return DocumentSpec(
        name="fill-in", language="en", kind="sheet", lines=tuple(lines), blocks=tuple(blocks)
    )


def gold_entry(spec: DocumentSpec, pages: int) -> dict[str, Any]:
    """Return a document's gold items and decoys as written to `gold.json`."""
    return {
        "name": spec.name,
        "language": spec.language,
        "kind": spec.kind,
        "pages": pages,
        "gold": [
            {"type": str(item.type), "text": item.text, "carrier": item.carrier}
            for item in spec.gold
        ],
        "decoys": list(spec.decoys),
    }


def page_count(path: Path) -> int:
    """Return the number of pages of a PDF."""
    with pymupdf.open(path) as pdf:
        return pdf.page_count


def concatenate(pdfs: list[Path], destination: Path) -> None:
    """Write every page of the PDFs, in order, into one PDF."""
    pack = pymupdf.open()
    for path in pdfs:
        with pymupdf.open(path) as pdf:
            pack.insert_pdf(pdf)
    pack.set_metadata({"producer": "", "creator": ""})
    pack.save(destination, garbage=4, deflate=True)
    pack.close()
