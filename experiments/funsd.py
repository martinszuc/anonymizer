"""FUNSD: real scanned forms read by each OCR engine, then detected, redacted and checked.

FUNSD (catalog `funsd`) holds 199 noisy scanned English forms (149 train, 50
test) with every word's text and box. It measures what the synthetic scanned
benchmark cannot: real scans, with typewriter, fax noise and handwritten
entries. It names real people, so results hold counts only, documents are
named by position, and the wrapped scans and redacted copies go to a work
directory that must stay out of git (`outputs/`).

Each form is scored as a document of the scanned benchmark
(`benchmark.ocr_run.score_scan`): character error rate, word boxes, items
found, ink left on them after redaction, false alarms (counted, never
written), and the leak check.

Ground truth:

- **Words.** FUNSD's words; those without text are dropped. Boxes are in
  the image's pixels and converted to points of the page `ingest.as_pdf`
  wraps the image into (the images record no resolution, so 300 DPI is
  assumed there; the pixels reach the engine unchanged either way).
- **Reading order.** On a form neither FUNSD's order nor an engine's matches
  the other, so the character error rate compares both in one geometric
  order (`reading_order`): words sorted by the centre of their box from the
  top, a word joining the line above while its centre lies above the bottom
  of that line's first word, each line left to right.
- **Personal items.** FUNSD labels no personal data. An answer linked to a
  question naming a person, phone or address field (`FIELD_TYPES`) is an item
  of that type, located by its words rather than its text; questions about
  products, companies or other things (`NOT_PERSONAL`) are left out, as are
  dates (our date type is a date of birth only; FUNSD's are mostly document
  dates). The labels are derived, not annotated: a "To:" can name a
  department, a phone a switchboard.
"""

from __future__ import annotations

import datetime
import json
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anonymizer.core
import pymupdf
from anonymizer.core.ingest import as_pdf, load_ocr_engine
from anonymizer.core.resources import load_catalog
from anonymizer.core.types import BBox, EntityType, Page
from PIL import Image

from benchmark.ocr_run import ocr_markdown, ocr_model_versions, scan_totals, score_scan
from benchmark.ocr_score import WordLocations
from benchmark.run import detector_factories, git_commit, machine
from benchmark.scans import TruthPage, TruthWord
from benchmark.spec import DocumentSpec, GoldItem

FUNSD_ID = "funsd"
FUNSD_RESULTS_SCHEMA = 1
SPLITS = {"train": "training_data", "test": "testing_data"}

FIELD_TYPES: tuple[tuple[EntityType, re.Pattern[str]], ...] = (
    (EntityType.PHONE, re.compile(r"phone|\btel\b|\btelephone|\bfax\b")),
    (EntityType.ADDRESS, re.compile(r"address|\bstreet\b|\bcity\b|\bzip\b")),
    (
        EntityType.PERSON,
        re.compile(
            r"\bname\b|\bsignature\b|\bsigned\b|^(to|from|cc|c\.c\.|attn|attention)\b"
            r"|\bcontact\b|\bauthor\b|\brecipient\b|\b(submitted|prepared|approved|requested) by\b"
        ),
    ),
)
"""Question text (lower case) → the type of its answers; the first pattern that matches wins."""

NOT_PERSONAL = re.compile(
    r"brand|product|company|firm|\bfile\b|program|project|account|\btest\b|chemical|trade"
    r"|\bcode\b|organi[sz]ation|agency|department|\bdept\b|division|vendor|supplier"
    r"|client|customer|store|chain|plant|facility"
)
"""Questions whose answers name a thing, not a person, even if a pattern above matches."""


@dataclass(frozen=True, slots=True)
class FunsdWord:
    """A word of a form, its box in image pixels."""

    text: str
    box: tuple[float, float, float, float]


@dataclass(frozen=True, slots=True)
class FunsdForm:
    """One annotated form.

    Attributes:
        image: The scanned page (PNG).
        words: Every word with text, in FUNSD's order.
        items: Derived personal items: type and the indices of their words.
    """

    image: Path
    words: tuple[FunsdWord, ...]
    items: tuple[tuple[EntityType, tuple[int, ...]], ...]


def read_forms(directory: Path, split: str) -> list[FunsdForm]:
    """Read a FUNSD split from the dataset directory, in file name order.

    Args:
        directory: `data/funsd`.
        split: `train` or `test`.

    Returns:
        The forms with their words and derived items.

    Raises:
        ValueError: If the split is unknown.
        FileNotFoundError: If the dataset is not stored there.
    """
    if split not in SPLITS:
        msg = f"FUNSD has no split {split!r}; choose from {sorted(SPLITS)}"
        raise ValueError(msg)
    folder = directory / "dataset" / "dataset" / SPLITS[split]
    annotations = sorted((folder / "annotations").glob("*.json"))
    if not annotations:
        msg = f"no FUNSD annotations under {folder}"
        raise FileNotFoundError(msg)
    return [
        parse_form(
            json.loads(path.read_text(encoding="utf-8")),
            folder / "images" / f"{path.stem}.png",
        )
        for path in annotations
    ]


def parse_form(annotation: dict[str, Any], image: Path) -> FunsdForm:
    """Turn one FUNSD annotation into words and derived personal items."""
    entities = {entity["id"]: entity for entity in annotation["form"]}
    words: list[FunsdWord] = []
    word_indices: dict[int, list[int]] = {}
    for entity in annotation["form"]:
        indices = word_indices.setdefault(entity["id"], [])
        for word in entity["words"]:
            if word["text"].strip():
                indices.append(len(words))
                words.append(FunsdWord(word["text"].strip(), tuple(word["box"])))
    items: list[tuple[EntityType, tuple[int, ...]]] = []
    for entity in annotation["form"]:
        if entity["label"] != "answer" or not word_indices[entity["id"]]:
            continue
        questions = [
            entities[other]["text"]
            for pair in entity["linking"]
            for other in pair
            if other != entity["id"] and entities.get(other, {}).get("label") == "question"
        ]
        kind = field_type(questions)
        if kind is not None:
            items.append((kind, tuple(word_indices[entity["id"]])))
    return FunsdForm(image=image, words=tuple(words), items=tuple(items))


def field_type(questions: Sequence[str]) -> EntityType | None:
    """Return the type of an answer from the questions linked to it, or None."""
    for question in questions:
        text = question.lower().strip().rstrip(":").strip()
        if NOT_PERSONAL.search(text):
            continue
        for kind, pattern in FIELD_TYPES:
            if pattern.search(text):
                return kind
    return None


def reading_order(boxes: Sequence[BBox]) -> list[list[int]]:
    """Group boxes into lines from the top, each line left to right.

    Returns:
        The lines, as indices into `boxes`.
    """
    by_centre = sorted(range(len(boxes)), key=lambda index: _centre_y(boxes[index]))
    lines: list[list[int]] = []
    for index in by_centre:
        if lines and _centre_y(boxes[index]) <= boxes[lines[-1][0]].y1:
            lines[-1].append(index)
        else:
            lines.append([index])
    return [sorted(line, key=lambda index: boxes[index].x0) for line in lines]


def in_reading_order(page: Page) -> Page:
    """Return a page whose text is its words in `reading_order` (for scoring text only)."""
    lines = reading_order([word.bbox for word in page.words])
    text = "\n".join(" ".join(page.words[index].text for index in line) for line in lines)
    return Page(index=page.index, width=page.width, height=page.height, text=text, words=[])


def truth_page(form: FunsdForm, scale: float, width: float, height: float) -> TruthPage:
    """Build a form's ground truth in points, its text in `reading_order`.

    Args:
        form: The form.
        scale: Points per image pixel on the wrapped page.
        width: Page width in points.
        height: Page height in points.

    Returns:
        The truth page; `words[i]` is `form.words[i]`, so item indices hold.
    """
    boxes = [BBox(*(value * scale for value in word.box)) for word in form.words]
    starts = [0] * len(boxes)
    lines: list[str] = []
    line_numbers = [0] * len(boxes)
    offset = 0
    for number, line in enumerate(reading_order(boxes)):
        parts: list[str] = []
        for index in line:
            starts[index] = offset + sum(len(part) + 1 for part in parts)
            line_numbers[index] = number
            parts.append(form.words[index].text)
        lines.append(" ".join(parts))
        offset += len(lines[-1]) + 1
    words = tuple(
        TruthWord(
            word.text,
            ((box.x0, box.y0), (box.x1, box.y0), (box.x1, box.y1), (box.x0, box.y1)),
            0,
            line_numbers[index],
        )
        for index, (word, box) in enumerate(zip(form.words, boxes, strict=True))
    )
    return TruthPage(
        text="\n".join(lines), words=words, starts=tuple(starts), width=width, height=height
    )


def run_funsd(
    work: Path,
    *,
    engines: tuple[str, ...],
    system: str = "rules+gliner",
    split: str = "test",
    resource_root: Path = Path(),
    limit: int | None = None,
) -> dict[str, Any]:
    """Read, detect, redact and check every form of a split with every engine.

    Args:
        work: Directory for the wrapped scans and redacted copies (keep out of git).
        engines: OCR engine names (`ingest.OCR_ENGINES`).
        system: Detector system, `rules` or `rules+<name model>`.
        split: `test` or `train`.
        resource_root: Storage root holding `data/funsd` and `models/`.
        limit: Score only the first forms, for a quick look.

    Returns:
        The results: counts and rates only.
    """
    resource = load_catalog()[FUNSD_ID]
    forms = read_forms(resource.directory(resource_root), split)[:limit]
    detector = detector_factories((system,), resource_root)[system]("en")
    loaded = {name: load_ocr_engine(name, resource_root) for name in engines}
    scans = work / "scans"
    scans.mkdir(parents=True, exist_ok=True)
    runs: dict[str, dict[str, Any]] = {engine: {} for engine in engines}
    items: Counter[str] = Counter()
    documents: dict[str, dict[str, Any]] = {engine: {} for engine in engines}
    for number, form in enumerate(forms):
        name = f"{FUNSD_ID}/{split}/{number:04d}"
        scan = scans / f"{number:04d}.pdf"
        scan.write_bytes(as_pdf(form.image.read_bytes()))
        truth = [_truth(form, scan)]
        spec = DocumentSpec(
            name=name,
            language="en",
            kind="form",
            lines=(),
            gold=tuple(
                GoldItem(kind, _item_text(form, words), "page") for kind, words in form.items
            ),
        )
        located: WordLocations = [(0, list(words)) for _, words in form.items]
        items.update(str(kind) for kind, _ in form.items)
        for engine in engines:
            documents[engine][name] = score_scan(
                scan,
                truth,
                spec,
                loaded[engine],
                detector,
                scans / f"{number:04d}.{engine}.pdf",
                located=located,
                record_texts=False,
                reading_order=in_reading_order,
            )
    for engine in engines:
        runs[engine][split] = {
            "documents": documents[engine],
            "totals": scan_totals(documents[engine]),
        }
    return {
        "schema": FUNSD_RESULTS_SCHEMA,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git_commit": git_commit(),
        "machine": machine(),
        "dataset": {"id": FUNSD_ID, "version": resource.version, "split": split},
        "forms": len(forms),
        "items": dict(sorted(items.items())),
        "engines": list(engines),
        "models": ocr_model_versions(engines),
        "system": system,
        "runs": runs,
    }


def write_results(results: dict[str, Any], folder: Path) -> Path:
    """Write `funsd-<split>.json` and its Markdown table; return the JSON path."""
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"{FUNSD_ID}-{results['dataset']['split']}"
    path = folder / f"{stem}.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    table = ocr_markdown(results, title="FUNSD scans")
    counted = ", ".join(f"{kind} {count}" for kind, count in results["items"].items())
    (folder / f"{stem}.md").write_text(
        table + f"\n{results['forms']} forms; derived items: {counted}.\n", encoding="utf-8"
    )
    return path


def _truth(form: FunsdForm, scan: Path) -> TruthPage:
    with pymupdf.open(scan) as document:
        rect = document[0].rect
    with Image.open(form.image) as picture:
        pixels = picture.width
    return truth_page(form, rect.width / pixels, rect.width, rect.height)


def _item_text(form: FunsdForm, words: Sequence[int]) -> str:
    return " ".join(form.words[index].text for index in words)


def _centre_y(box: BBox) -> float:
    return (box.y0 + box.y1) / 2
