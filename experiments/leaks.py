"""Why the leak check fails on a document, in counts only: safe to run on a real scan.

`python -m experiments leaks scan.pdf --engines onnxtr --system rules+gliner`
loads the document with each OCR engine, detects, redacts and runs the leak
check, then sorts what it reported. Nothing read from the document is
printed or written: no text, no file name. A text is named by a salted hash
that changes on every run, so equal texts can be grouped without being
recognisable.

Reports are grouped by layer, page and text, since every entity with the
same text (a model's span and its propagated copies) reports the same
occurrence again. Each group gives the text's length and shape, the entities
behind it by type and source, and, on the OCR layer, where each occurrence
the re-read found lies (`OCR_CLASSES`). A word under a box gets the share of
its box that is now black fill and the share of its ink left untouched.

This explains failures; it does not decide them. Whether an occurrence read
differently at ingest is the name or a misreading takes a person.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import tempfile
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any

import pymupdf
from anonymizer.core.detect import Detector
from anonymizer.core.ingest import OcrEngine, load_document, read_page
from anonymizer.core.pipeline import run_detection
from anonymizer.core.redact import Leak, LeakLayer, find_leaks, redact_pdf
from anonymizer.core.types import BBox, Document, Entity, Page

OCR_CLASSES = {
    "longer_word": "begins a longer word (an inflected form, or another word by chance)",
    "inside_word": "inside a word, not at its start",
    "across_words": "spans the gap between words of the re-read",
    "whole_word_read_differently": "a word of its own where ingest read another word",
    "whole_word_read_the_same": "a word of its own where ingest read it too",
}
"""Where an occurrence of a reported text lies in the re-read page."""

# Pixels darker than this are ink; redaction fills pure black.
_INK_LEVEL = 128
_BLACK = (0, 0, 0)
# An original word lies where the re-read found a text when it covers this much of it.
_SAME_PLACE = 0.3


def breakdown(
    pdf: Path, engines: Mapping[str, OcrEngine], detector: Detector, language: str | None
) -> dict[str, Any]:
    """Detect, redact and check a PDF with each engine, and count why the check failed.

    Args:
        pdf: The document; it is read, never copied into the result.
        engines: OCR engines by the name to report them under.
        detector: The detector to run (see `core.pipeline.build_detector`).
        language: Detection language.

    Returns:
        Per engine: `entities` by source, type and length, `leaks` by layer,
        and `groups`, one per layer, page and text (see the module docstring).
    """
    salt = secrets.token_bytes(16)
    results: dict[str, Any] = {"language": language, "engines": {}}
    for name, engine in engines.items():
        document = load_document(pdf, language=language, ocr=engine)
        run_detection(document, detector)
        with tempfile.TemporaryDirectory() as scratch:
            redacted = Path(scratch) / "redacted.pdf"
            redact_pdf(pdf, document, redacted)
            leaks = find_leaks(redacted, document, ocr=engine)
            with pymupdf.open(pdf) as original, pymupdf.open(redacted) as output:
                groups = _groups(leaks, document, engine, original, output, salt)
        results["engines"][name] = {
            "entities": dict(Counter(_entity_key(entity) for entity in document.entities)),
            "leaks": dict(Counter(leak.layer.value for leak in leaks)),
            "groups": groups,
        }
    return results


def _entity_key(entity: Entity) -> str:
    length = len(_compact(entity.text or ""))
    bucket = "region" if entity.is_region else str(length) if length < 4 else "4+"
    return f"{entity.source.value}/{entity.type.value}/{bucket}"


def _groups(
    leaks: list[Leak],
    document: Document,
    engine: OcrEngine,
    original: pymupdf.Document,
    output: pymupdf.Document,
    salt: bytes,
) -> list[dict[str, Any]]:
    entities = {entity.entity_id: entity for entity in document.entities}
    grouped: dict[tuple[str, int | None, str], list[Leak]] = defaultdict(list)
    for leak in leaks:
        under_box = "under a box" in leak.where
        entity = entities.get(leak.entity_id or "")
        text = leak.text if under_box or entity is None else entity.text or ""
        kind = f"{leak.layer.value} under a box" if under_box else leak.layer.value
        grouped[(kind, leak.page_index, text)].append(leak)
    rereads: dict[int, Page] = {}

    def reread(index: int) -> Page:
        if index not in rereads:
            dpi = int(document.page(index).raster_dpi or 0)
            rereads[index] = read_page(output.load_page(index), index, engine, dpi)
        return rereads[index]

    rows = []
    for (kind, page_index, text), members in grouped.items():
        tied = [entities[leak.entity_id] for leak in members if leak.entity_id in entities]
        row: dict[str, Any] = {
            "layer": kind,
            "page": page_index,
            "text_id": hashlib.sha256(salt + text.encode()).hexdigest()[:8],
            "reports": len(members),
            "entities": dict(Counter(f"{e.source.value}/{e.type.value}" for e in tied)),
        }
        if kind == LeakLayer.OCR.value and tied and page_index is not None:
            row |= _shape(text)
            row["occurrences"] = dict(
                Counter(_ocr_occurrences(text, document.page(page_index), reread(page_index)))
            )
        elif kind.endswith("under a box") and page_index is not None:
            row["word_length"] = len(text) - len("word ''")
            row["boxes"] = _under_box(text, document, page_index, reread, original, output)
        elif tied:
            row |= _shape(text)
        rows.append(row)
    return rows


def _shape(text: str) -> dict[str, Any]:
    compact = _compact(text)
    if compact.isdigit():
        shape = "digits"
    elif compact.isalpha():
        shape = "letters"
    else:
        shape = "mixed"
    return {"length": len(compact), "shape": shape}


def _ocr_occurrences(text: str, ingested: Page, reread: Page) -> Iterable[str]:
    """Classify each place the re-read holds a text (see `OCR_CLASSES`)."""
    compact = _compact(text)
    pattern = re.compile(r"\s*".join(re.escape(character) for character in compact))
    for found in pattern.finditer(reread.text):
        start, end = found.span()
        if re.search(r"\s", found.group()) and len(text.split()) == 1:
            yield "across_words"
        elif start > 0 and reread.text[start - 1].isalnum():
            yield "inside_word"
        elif end < len(reread.text) and reread.text[end].isalnum():
            yield "longer_word"
        elif _read_there(ingested, reread.bboxes_for_span(start, end), compact):
            yield "whole_word_read_the_same"
        else:
            yield "whole_word_read_differently"


def _read_there(ingested: Page, boxes: list[BBox], compact: str) -> bool:
    """Whether ingest read the text in the words where the re-read found it."""
    there = [
        word
        for box in boxes
        for word in ingested.words
        if _shared(word.bbox, box) > _SAME_PLACE * _rect(box).get_area()
    ]
    return compact in _compact(" ".join(word.text for word in there))


def _under_box(
    text: str,
    document: Document,
    page_index: int,
    reread: Callable[[int], Page],
    original: pymupdf.Document,
    output: pymupdf.Document,
) -> list[dict[str, float]]:
    """Return, per re-read word reported under a box, its black fill and untouched ink shares."""
    dpi = int(document.page(page_index).raster_dpi or 72)
    before = original.load_page(page_index).get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB)
    after = output.load_page(page_index).get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB)
    shares = []
    for word in reread(page_index).words:
        if f"word {word.text!r}" != text:
            continue
        fill = ink = untouched = area = 0
        scale = dpi / 72
        box = word.bbox
        for y in range(int(box.y0 * scale), min(before.height, int(box.y1 * scale) + 1)):
            for x in range(int(box.x0 * scale), min(before.width, int(box.x1 * scale) + 1)):
                old, new = before.pixel(x, y), after.pixel(x, y)
                area += 1
                fill += new == _BLACK and old != _BLACK
                if sum(old) < 3 * _INK_LEVEL:
                    ink += 1
                    untouched += old == new
        shares.append(
            {
                "black_fill": round(fill / max(area, 1), 2),
                "ink_untouched": round(untouched / max(ink, 1), 2),
            }
        )
    return shares


def _compact(text: str) -> str:
    return "".join(text.split())


def _rect(box: BBox) -> pymupdf.Rect:
    return pymupdf.Rect(*box.to_list())


def _shared(first: BBox, second: BBox) -> float:
    shared = _rect(first) & _rect(second)
    return 0.0 if shared.is_empty else shared.get_area()


def breakdown_markdown(results: dict[str, Any]) -> str:
    """Render a breakdown as Markdown, counts only."""
    lines = [f"# Leak check breakdown ({results['language']})"]
    for name, run in results["engines"].items():
        lines += ["", f"## {name}", "", f"Leaks by layer: {_counts(run['leaks']) or 'none'}."]
        lines += [f"Entities by source/type/length: {_counts(run['entities'])}.", ""]
        lines += ["| layer | page | text | reports | length | shape | entities | detail |"]
        lines += ["|---|---|---|---|---|---|---|---|"]
        for group in run["groups"]:
            detail = group.get("occurrences") or group.get("boxes") or ""
            lines.append(
                f"| {group['layer']} | {group['page']} | {group['text_id']} "
                f"| {group['reports']} | {group.get('length', group.get('word_length', ''))} "
                f"| {group.get('shape', '')} | {_counts(group['entities'])} | {detail} |"
            )
    return "\n".join(lines) + "\n"


def _counts(counts: Mapping[str, int]) -> str:
    return ", ".join(f"{key} {value}" for key, value in sorted(counts.items()))


def write_breakdown(results: dict[str, Any], output: Path) -> None:
    """Write `leaks.json` and `leaks.md` into a directory."""
    output.mkdir(parents=True, exist_ok=True)
    (output / "leaks.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (output / "leaks.md").write_text(breakdown_markdown(results), encoding="utf-8")
