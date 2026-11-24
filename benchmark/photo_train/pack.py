"""Rendering photo training documents: one PDF each, their gold items, and the print pack."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pymupdf

from benchmark.photo_train.generate import DOCUMENTS, generate, write
from benchmark.render import render
from benchmark.spec import DocumentSpec, load_document_spec, load_documents

PACK = "rq8-train-print.pdf"
MANIFEST = "manifest-train.md"


def render_split(out: Path, *, split: str, count: int = 0, seed: str | None = None) -> Path:
    """Render a split into `out`; return the path of `gold.json`.

    Writes `pdf/<name>.pdf` and `gold.json` (per document: language, kind,
    pages and every gold item with its type and text). The print split is read
    from the committed files in `DOCUMENTS` and also gets `PACK`, every page in
    print order, and `MANIFEST`, the print order; the synthetic split is
    generated and its files written to `out/documents/` first.

    Args:
        out: Output directory.
        split: `print` or `synthetic`.
        count: Synthetic documents per language.
        seed: Seed of the synthetic split.

    Returns:
        The path of `gold.json`.

    Raises:
        ValueError: For an unknown split, a count or seed given to the print
            split, or a synthetic count below one.
    """
    out.mkdir(parents=True, exist_ok=True)
    if split == "print":
        if count or seed is not None:
            msg = "the print split is fixed: it takes no count or seed"
            raise ValueError(msg)
        specs = load_documents(DOCUMENTS)
    else:
        paths = write(generate(split, count=count, seed=seed), out / "documents")
        specs = [load_document_spec(path) for path in paths]
    pdfs = [render(spec, out / "pdf" / f"{spec.name}.pdf") for spec in specs]
    pages = [_page_count(pdf) for pdf in pdfs]
    gold = [_gold(spec, count) for spec, count in zip(specs, pages, strict=True)]
    gold_path = out / "gold.json"
    gold_path.write_text(json.dumps(gold, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if split == "print":
        _concatenate(pdfs, out / PACK)
        (out / MANIFEST).write_text(manifest(specs, pages), encoding="utf-8")
    return gold_path


def manifest(specs: list[DocumentSpec], pages: list[int]) -> str:
    """Return the print order as a Markdown table, with the total number of pages."""
    rows = [
        f"| {number} | {spec.name} | {count} |"
        for number, (spec, count) in enumerate(zip(specs, pages, strict=True), start=1)
    ]
    return "\n".join(
        [
            "# Print order of the training set (photograph in this order, every condition)",
            "",
            "| # | document | pages |",
            "|---|---|---|",
            *rows,
            "",
            f"Total: {len(specs)} documents, {sum(pages)} pages.",
            "",
        ]
    )


def _gold(spec: DocumentSpec, pages: int) -> dict[str, Any]:
    return {
        "name": spec.name,
        "language": spec.language,
        "kind": spec.kind,
        "pages": pages,
        "gold": [{"type": str(item.type), "text": item.text} for item in spec.gold],
        "decoys": list(spec.decoys),
    }


def _page_count(path: Path) -> int:
    with pymupdf.open(path) as pdf:
        return pdf.page_count


def _concatenate(pdfs: list[Path], destination: Path) -> None:
    pack = pymupdf.open()
    for path in pdfs:
        with pymupdf.open(path) as pdf:
            pack.insert_pdf(pdf)
    pack.set_metadata({"producer": "", "creator": ""})
    pack.save(destination, garbage=4, deflate=True)
    pack.close()
