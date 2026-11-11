"""What a redaction method leaves behind: three methods on the same planted items.

Detection is taken out of the comparison. The targets are the planted items
themselves (an oracle), so a difference between the methods is a difference in
how they *remove*, never in what they found. Each method gets the same
located items and writes its own copy of each document:

- **overlay**: a black rectangle drawn over every item's words on the page,
  the text left underneath. What a pencil tool does.
- **apply_redactions**: PyMuPDF's redaction annotations over the same boxes,
  applied; the text under them is removed from the page. Nothing else is
  cleared. What a careful use of the library alone does.
- **tool**: `export_redacted`, the entry point of the CLI and the review
  window: redaction, surface clearing, off-page removal and the leak check.
  When the check refuses a copy, the copy is written without it and counted,
  so the refusal does not hide what the redaction itself left.

Every copy is saved, then **read again from the file** by ingest (page text and
surfaces, as `score.left_in_carrier` reads them) and, for content outside the
visible area, by `redact.canvas.off_page_words`. The count never uses a
method's own claim of what it removed. A planted item is *extractable* when its
own carrier still holds it, whole or as a word unique to it.

The benchmark documents plant nothing in a tagged PDF's structure tree or
outside a page's visible area, so this command adds one item to each of the two
(`CANARIES`) before anything is redacted. They are counted like the others and
reported as injected.
"""

from __future__ import annotations

import datetime
import json
import re
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import anonymizer.core
import pymupdf
from anonymizer.core.ingest import load_document
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.redact import export_redacted, find_leaks
from anonymizer.core.redact.canvas import off_page_words
from anonymizer.core.types import Document, Entity, EntityType, ReviewState

from benchmark.leaks_report import latex, markdown
from benchmark.render import render
from benchmark.run import git_commit, machine
from benchmark.score import compact, left_in_carrier, page_locations, words_pattern
from benchmark.spec import DOCUMENTS, DocumentSpec, GoldItem, document_set, load_documents

RESULTS_SCHEMA = 1
METHODS = ("overlay", "apply_redactions", "tool")
CANARIES = (
    GoldItem(EntityType.PERSON, "Bohumil Zahradnik", "structure"),
    GoldItem(EntityType.PERSON, "Radomir Pekarek", "off_page"),
)
"""One invented name per injected carrier; ASCII, because the font that draws it is not Unicode."""

_BLACK = (0.0, 0.0, 0.0)
_OFF_PAGE_ORIGIN = (100.0, 1500.0)
_WORD = re.compile(r"\w{3,}")


@dataclass(frozen=True)
class MethodResult:
    """What one method left in one document.

    Attributes:
        items: Per planted item: type, text, carrier and whether it is still
            extractable from the saved output.
        leak_layers: Leaks the tool's own leak check reports on the output,
            by layer (a cross-check of the check, not part of the count).
        refused: For `tool`: the leak check refused the copy.
    """

    items: tuple[dict[str, Any], ...]
    leak_layers: dict[str, int]
    refused: bool = False

    @property
    def extractable(self) -> int:
        """Planted items still extractable."""
        return sum(item["left"] for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping."""
        return {
            "items": list(self.items),
            "extractable": self.extractable,
            "leak_layers": self.leak_layers,
            "refused": self.refused,
        }


def run_leaks(
    output: Path,
    *,
    documents: Path = DOCUMENTS,
    names: tuple[str, ...] = (),
    specs: list[DocumentSpec] | None = None,
) -> dict[str, Any]:
    """Compare the three methods on every document and write the results.

    Args:
        output: Directory for `leaks.json`, `leaks.md`, `leaks.tex` and `pdf/`.
        documents: Directory of document files, read when `specs` is not given.
        names: Document names to run; every document when empty.
        specs: Documents to run instead of the files.

    Returns:
        The results, as written to `leaks.json`.

    Raises:
        ValueError: If a name matches no document.
    """
    if specs is None:
        specs = load_documents(documents)
        identity = document_set(documents)
    else:
        identity = {"fingerprint": None, "documents": len(specs)}
    if names:
        unknown = set(names) - {spec.name for spec in specs}
        if unknown:
            msg = f"no such document: {', '.join(sorted(unknown))}"
            raise ValueError(msg)
        specs = [spec for spec in specs if spec.name in names]
        identity = {"fingerprint": None, "documents": len(specs)}
    (output / "pdf").mkdir(parents=True, exist_ok=True)
    scores = {spec.name: compare_document(spec, output / "pdf") for spec in specs}
    results = {
        "schema": RESULTS_SCHEMA,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git_commit": git_commit(),
        "machine": machine(),
        "document_set": identity,
        "methods": list(METHODS),
        "injected": [item.text for item in CANARIES],
        "documents": scores,
        "totals": totals(scores),
    }
    (output / "leaks.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "leaks.md").write_text(markdown(results), encoding="utf-8")
    (output / "leaks.tex").write_text(latex(results), encoding="utf-8")
    return results


def compare_document(spec: DocumentSpec, folder: Path) -> dict[str, Any]:
    """Render one document, add the injected items, and compare the methods on it.

    Args:
        spec: The document; its planted items are the oracle targets.
        folder: Directory for the original and the three copies.

    Returns:
        As `compare_pdf`.
    """
    source = folder / f"{spec.name}.pdf"
    render(spec, source)
    plant_canaries(source)
    return compare_pdf(replace(spec, gold=(*spec.gold, *CANARIES)), source, folder)


def compare_pdf(spec: DocumentSpec, source: Path, folder: Path) -> dict[str, Any]:
    """Redact a PDF by each method and count what is still extractable.

    Args:
        spec: The document with every planted item, the injected ones included.
        source: The PDF holding them.
        folder: Directory for the three copies, named after `spec`.

    Returns:
        `unlocated` (planted items the oracle could not place, which no method
        can then remove) and, per method, a `MethodResult` as a mapping.
    """
    original = load_document(source, language=spec.language)
    unlocated = apply_oracle(spec, original)
    overlay_path = folder / f"{spec.name}.overlay.pdf"
    plain_path = folder / f"{spec.name}.apply_redactions.pdf"
    overlay(source, original, overlay_path)
    apply_redactions(source, original, plain_path)
    tool_path, refused = tool(source, original, folder / f"{spec.name}.tool.pdf")
    paths = {"overlay": overlay_path, "apply_redactions": plain_path, "tool": tool_path}
    results = {
        method: count_extractable(spec, original, path, refused=method == "tool" and refused)
        for method, path in paths.items()
    }
    return {
        "summary": {"name": spec.name, "kind": spec.kind, "items": len(spec.gold)},
        "unlocated": unlocated,
        "methods": {method: result.to_dict() for method, result in results.items()},
    }


def plant_canaries(path: Path) -> None:
    """Add the injected items to a PDF: a name in its structure tree, a name off the page.

    Args:
        path: The PDF; rewritten in place.
    """
    structure, off_page = CANARIES
    partial = path.with_name(f".{path.name}.partial")
    with pymupdf.open(path) as pdf:
        page = pdf[0]
        page.insert_text(_OFF_PAGE_ORIGIN, off_page.text, fontname="helv", fontsize=12)
        root = pdf.get_new_xref()
        pdf.update_object(root, "<< /Type /StructTreeRoot >>")
        figure = pdf.get_new_xref()
        pdf.update_object(
            figure,
            f"<< /Type /StructElem /S /Figure /P {root} 0 R /Pg {page.xref} 0 R"
            f" /Alt {pymupdf.get_pdf_str(structure.text)} >>",
        )
        pdf.xref_set_key(root, "K", f"[{figure} 0 R]")
        catalog = pdf.pdf_catalog()
        pdf.xref_set_key(catalog, "StructTreeRoot", f"{root} 0 R")
        pdf.xref_set_key(catalog, "MarkInfo", "<< /Marked true >>")
        pdf.save(partial, garbage=4, deflate=True)
    partial.replace(path)


def apply_oracle(spec: DocumentSpec, document: Document) -> int:
    """Give a document one entity per planted item, placed where the item lies.

    Page items are placed by their words, hidden ones on the first surface of
    their kind that holds them. The off-page item has no entity: no extractor
    reads it, which is what the comparison is about.

    Args:
        spec: The document with its planted items.
        document: The loaded document; its entities are replaced.

    Returns:
        The number of planted items that could not be placed.
    """
    locations = page_locations(spec, document)
    entities: list[Entity] = []
    unlocated = 0
    for index, item in enumerate(spec.gold):
        entity = (
            _page_entity(item, locations.get(index), document)
            if item.carrier == "page"
            else _surface_entity(item, document)
        )
        if entity is not None:
            entities.append(entity)
        elif item.carrier != "off_page":
            unlocated += 1
    document.entities = entities
    return unlocated


def _page_entity(
    item: GoldItem, location: tuple[int, int, int] | None, document: Document
) -> Entity | None:
    if location is None:
        return None
    page_index, start, end = location
    page = document.page(page_index)
    return Entity(
        type=item.type,
        page_index=page_index,
        start=start,
        end=end,
        text=page.text[start:end],
        bboxes=page.bboxes_for_span(start, end),
        review=ReviewState.CONFIRMED,
    )


def _surface_entity(item: GoldItem, document: Document) -> Entity | None:
    pattern = words_pattern(item.text)
    for surface in document.surfaces:
        match = pattern.search(surface.value)
        if surface.kind.value == item.carrier and match:
            return Entity(
                type=item.type,
                page_index=surface.page_index,
                start=match.start(),
                end=match.end(),
                text=match.group(),
                surface_id=surface.surface_id,
                review=ReviewState.CONFIRMED,
            )
    return None


def overlay(source: Path, document: Document, destination: Path) -> None:
    """Draw a black rectangle over every page entity and save; the text stays underneath."""
    _edit_pages(source, document, destination, redact=False)


def apply_redactions(source: Path, document: Document, destination: Path) -> None:
    """Apply a redaction annotation over every page entity and save; nothing else is cleared."""
    _edit_pages(source, document, destination, redact=True)


def _edit_pages(source: Path, document: Document, destination: Path, *, redact: bool) -> None:
    with pymupdf.open(source) as pdf:
        for index in range(pdf.page_count):
            page = pdf[index]
            rects = [
                bbox_to_unrotated_rect(box, page)
                for entity in document.entities
                if entity.in_page_text and entity.page_index == index
                for box in entity.bboxes
            ]
            for rect in rects:
                if redact:
                    page.add_redact_annot(rect, fill=_BLACK)
                else:
                    page.draw_rect(rect, color=None, fill=_BLACK)
            if redact and rects:
                page.apply_redactions()
        pdf.save(destination, garbage=4, deflate=True)


def tool(source: Path, document: Document, destination: Path) -> tuple[Path, bool]:
    """Export through the tool's entry point; return the copy to count and whether it was refused.

    A refused copy is not written by `export_redacted`, so it is written again
    without the check: the count is of what redaction left, not of whether the
    check let the file out.
    """
    if not export_redacted(source, document, destination):
        return destination, False
    unchecked = destination.with_name(f"{destination.stem}.unchecked.pdf")
    export_redacted(source, document, unchecked, check=False)
    return unchecked, True


def count_extractable(
    spec: DocumentSpec, original: Document, path: Path, *, refused: bool = False
) -> MethodResult:
    """Read a saved copy again and decide, per planted item, whether it is still there.

    Args:
        spec: The document with its planted items (the injected ones included).
        original: The document as loaded from the unredacted file.
        path: The saved copy; read from disk, not from the process that wrote it.
        refused: Whether the tool's leak check refused this copy.

    Returns:
        The items with their outcome, and the leak check's layers on the copy.
    """
    redacted = load_document(path, language=spec.language)
    left = left_in_carrier(spec, original, redacted)
    off_page = _off_page_text(path)
    items = tuple(
        {
            "type": str(item.type),
            "text": item.text,
            "carrier": item.carrier,
            "left": _readable(item.text, off_page) if item.carrier == "off_page" else bool(found),
        }
        for item, found in zip(spec.gold, left, strict=True)
    )
    layers = Counter(leak.layer.value for leak in find_leaks(path, original))
    return MethodResult(items, dict(sorted(layers.items())), refused)


def _off_page_text(path: Path) -> str:
    """Return the words drawn outside the visible area of any page of a saved file."""
    with pymupdf.open(path) as pdf:
        return " ".join(word for page in pdf for word in off_page_words(page))


def _readable(text: str, found: str) -> bool:
    """Whether a text, or a word of three letters or more of it, is in `found`."""
    if compact(text) in compact(found):
        return True
    present = {word.lower() for word in _WORD.findall(found)}
    return any(word.lower() in present for word in _WORD.findall(text))


def totals(documents: dict[str, Any]) -> dict[str, Any]:
    """Add up planted and extractable items per method and carrier.

    Args:
        documents: `compare_document` results by document name.

    Returns:
        Per carrier the number of planted items, per method the number still
        extractable by carrier, in all, in documents, refusals and leaks by layer.
    """
    items: Counter[str] = Counter()
    summary: dict[str, Any] = {
        "documents": len(documents),
        "unlocated": sum(document["unlocated"] for document in documents.values()),
        "methods": {},
    }
    for method in METHODS:
        by_carrier: Counter[str] = Counter()
        layers: Counter[str] = Counter()
        results = [document["methods"][method] for document in documents.values()]
        for result in results:
            by_carrier.update(item["carrier"] for item in result["items"] if item["left"])
            layers.update(result["leak_layers"])
        summary["methods"][method] = {
            "extractable_by_carrier": dict(by_carrier),
            "extractable": sum(by_carrier.values()),
            "clean_documents": sum(result["extractable"] == 0 for result in results),
            "refused": sum(result["refused"] for result in results),
            "documents_flagged": sum(bool(result["leak_layers"]) for result in results),
            "leak_layers": dict(sorted(layers.items())),
        }
    for document in documents.values():
        items.update(item["carrier"] for item in document["methods"][METHODS[0]]["items"])
    summary["items_by_carrier"] = dict(items)
    summary["items"] = sum(items.values())
    return summary
