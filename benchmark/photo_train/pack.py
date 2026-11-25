"""Rendering photo training documents: one PDF each, their gold items, and the print pack."""

from __future__ import annotations

import json
from pathlib import Path

from benchmark.photo_train.generate import DOCUMENTS, generate, write
from benchmark.print_pack import gold_entry, page_count, write_pack
from benchmark.render import render
from benchmark.spec import load_document_spec, load_documents

PACK = "rq8-train-print.pdf"
MANIFEST = "manifest-train.md"
FILL_IN = "fill-in-train.pdf"
TITLE = "Print order of the training set (photograph in this order, every condition)"


def render_split(out: Path, *, split: str, count: int = 0, seed: str | None = None) -> Path:
    """Render a split into `out`; return the path of `gold.json`.

    Writes `pdf/<name>.pdf` and `gold.json` (per document: language, kind,
    pages and every gold item with its type, text and carrier). The print
    split is read from the committed files in `DOCUMENTS` and also gets `PACK`,
    every page in print order, `MANIFEST`, the print order, and `FILL_IN`,
    what to write by hand; the synthetic split is generated and its files
    written to `out/documents/` first.

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
    if split == "print":
        if count or seed is not None:
            msg = "the print split is fixed: it takes no count or seed"
            raise ValueError(msg)
        specs = load_documents(DOCUMENTS)
        return write_pack(
            specs,
            out,
            pack=PACK,
            manifest_name=MANIFEST,
            fill_in=FILL_IN,
            title=TITLE,
            set_name="training set",
        )
    out.mkdir(parents=True, exist_ok=True)
    paths = write(generate(split, count=count, seed=seed), out / "documents")
    specs = [load_document_spec(path) for path in paths]
    pdfs = [render(spec, out / "pdf" / f"{spec.name}.pdf") for spec in specs]
    gold = [gold_entry(spec, page_count(pdf)) for spec, pdf in zip(specs, pdfs, strict=True)]
    gold_path = out / "gold.json"
    gold_path.write_text(json.dumps(gold, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return gold_path
