"""Scoring phone photos of the printed benchmark documents (`experiments/photo-rules.md`).

Every photo (`photo_files.named_photos`) is read through the tool's own image
ingest (`load_document`: EXIF rotation applied, pixels only) with an OCR
engine, once per engine; each system then detects on what was read
(`pipeline.run_detection`) and writes its redacted copy through
`redact.export_redacted`, whose leak check re-reads it with the same engine.
A **digital** row scores every system on the born-digital text of the same
documents, the reference each condition's drop is measured against.

Ground truth is the generator's page text (`render` of the document's file,
read back), with the planted page items located in it as the benchmark
locates them (`score.page_locations`). In what OCR read they are located by
character alignment (`align.locate`); an item not read is missed and leaves
its document unsafe. Scores per engine, condition and system:

- CER and diacritics error (`ocr_score.text_errors`), and *not read*;
- items found, partial, missed (`score.score_detection`) and false alarms
  (`score.false_positives`), on the located spans;
- person recall and F2 (partial match) and person residual share
  (`experiments.metrics`), not-read persons counted as gold that nothing
  covers (they sit on a page of their own that no detection touches);
- documents safe (every printed item read and found whole) and leak check passed.

Handwritten items are scored apart. Their ground truth is the page text with
each handwritten text inserted after its label (`_handwriting`); in the
printed rows a detection overlapping a located handwritten text and no printed
item is left out, neither credited nor a false alarm. The handwritten row,
read with kraken only, counts per condition and system the handwritten items
not read, found, partial and missed, the CER of the handwritten texts' located
spans, and the documents safe overall (printed and handwritten items found
whole). Without a kraken run the row is not available.

Intervals: paired bootstrap over documents (a document's photos pool), with
the seed and resample count the rules fix. `compare` pairs systems as
baseline and candidate; `set_outcome` of `experiments.verdict` labels each
condition win, loss or tie. `primary` adds the rule's one sentence (OnnxTR).
An engine that fails to load or to read is reported and left out.

Only counts, ids and invented document text reach the results; nothing is
logged about the photos.
"""

from __future__ import annotations

import dataclasses
import datetime
import hashlib
import json
import re
import tempfile
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import anonymizer.core
from anonymizer.core.ingest import OcrEngine, load_document, load_ocr_engine
from anonymizer.core.pipeline import run_detection
from anonymizer.core.redact import export_redacted
from anonymizer.core.types import Document, Entity, EntityType
from rapidfuzz.distance import Levenshtein

from benchmark.align import Span, locate, spaced
from benchmark.ocr_run import ocr_model_versions
from benchmark.ocr_score import text_errors
from benchmark.photo_files import (
    CONDITIONS,
    ManifestEntry,
    PhotoSetError,
    named_photos,
    read_manifest,
)
from benchmark.photo_test import DOCUMENTS
from benchmark.render import render
from benchmark.run import (
    DetectorFactory,
    _model_thresholds,
    _model_versions,
    detector_factories,
    git_commit,
    machine,
)
from benchmark.scans import TruthPage
from benchmark.score import (
    Location,
    false_positives,
    page_locations,
    score_detection,
    words_pattern,
)
from benchmark.spec import DocumentSpec, GoldItem, Handwritten, document_set, load_documents
from experiments.metrics import (
    PARTIAL,
    Counts,
    Coverage,
    Resampler,
    Tally,
    document_counts,
    document_coverage,
    interval,
    paired_difference,
    resamples,
    total,
)
from experiments.verdict import set_outcome

PHOTOS_SCHEMA = 2
SEED = 20261010
RESAMPLES = 1000
DIGITAL = "digital"
PRIMARY_ENGINE = "onnxtr"
HANDWRITING_ENGINE = "kraken"
PERSON = EntityType.PERSON

EngineLoader = Callable[[str, Path], OcrEngine]


@dataclasses.dataclass(frozen=True, slots=True)
class TextTally(Tally):
    """Character and diacritic errors of OCR, additive over documents."""

    characters: int = 0
    character_errors: int = 0
    diacritics: int = 0
    diacritic_errors: int = 0

    def metric(self, name: str) -> float | None:
        """Return `cer` or `diacritics` by name; `None` when undefined."""
        if name == "cer":
            return self.character_errors / self.characters if self.characters else None
        if name == "diacritics":
            return self.diacritic_errors / self.diacritics if self.diacritics else None
        msg = f"unknown metric {name!r}"
        raise ValueError(msg)


@dataclasses.dataclass
class _Scored:
    """One document's scores under one system, summed over its photos."""

    gold: int = 0
    found: int = 0
    partial: int = 0
    missed: int = 0
    not_read: int = 0
    not_read_present: int = 0
    counts: Counts = dataclasses.field(default_factory=Counts)
    coverage: Coverage = dataclasses.field(default_factory=Coverage)
    false_positives: set[str] = dataclasses.field(default_factory=set)
    leak_check_passed: bool = True

    @property
    def safe(self) -> bool:
        return self.found == self.gold

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": {
                "gold": self.gold,
                "found": self.found,
                "partial": self.partial,
                "missed": self.missed,
                "not_read": self.not_read,
                "not_read_present": self.not_read_present,
            },
            "person": self.counts.to_dict(),
            "coverage": self.coverage.to_dict(),
            "false_positives": sorted(self.false_positives),
            "safe": self.safe,
            "leak_check_passed": self.leak_check_passed,
        }


@dataclasses.dataclass
class _HandScored:
    """One document's handwritten items under one system, summed over its photos."""

    gold: int = 0
    not_read: int = 0
    found: int = 0
    partial: int = 0
    missed: int = 0

    def __add__(self, other: _HandScored) -> _HandScored:
        return _HandScored(*(getattr(self, key) + getattr(other, key) for key in _HAND_KEYS))

    def to_dict(self) -> dict[str, int]:
        return {key: getattr(self, key) for key in _HAND_KEYS}


_HAND_KEYS = ("gold", "not_read", "found", "partial", "missed")


@dataclasses.dataclass(frozen=True)
class _Handwriting:
    """A page's text with its handwritten texts inserted after their labels.

    Attributes:
        text: The page text with the handwriting in it.
        fields: Each handwritten text's span in `text`.
        items: Index into `_Truth.handwritten` and span in `text` of each
            handwritten item on the page.
    """

    text: str
    fields: tuple[Span, ...] = ()
    items: tuple[tuple[int, Span], ...] = ()


@dataclasses.dataclass(frozen=True)
class _Truth:
    """A document's ground truth: its born-digital PDF, page texts and page items."""

    spec: DocumentSpec
    pdf: Path
    pages: list[str]
    sizes: list[tuple[float, float]]
    items: tuple[GoldItem, ...]
    locations: list[Location | None]
    handwritten: tuple[GoldItem, ...] = ()
    handwriting: tuple[_Handwriting, ...] = ()


def score_photos(
    photos: Path,
    manifest_path: Path,
    output: Path,
    *,
    documents: Path = DOCUMENTS,
    conditions: tuple[str, ...] = CONDITIONS,
    engines: tuple[str, ...] = (PRIMARY_ENGINE,),
    systems: tuple[str, ...] = ("rules",),
    compare: tuple[tuple[str, str], ...] = (),
    primary: tuple[str, str] | None = None,
    resource_root: Path = Path(),
    engine_loader: EngineLoader = load_ocr_engine,
    detectors: Mapping[str, DetectorFactory] | None = None,
    set_name: str = "test",
    run_name: str | None = None,
    redacted: Path | None = None,
    resample_count: int = RESAMPLES,
) -> dict[str, Any]:
    """Score every system on every photo of a set, and on the born-digital text.

    Args:
        photos: Folder of condition folders, photos named by `photos rename`.
        manifest_path: The print order the photos were taken in.
        output: Directory for `photos[-<run>].json` and `.md`.
        documents: Directory of the documents' files (`*.toml`).
        conditions: Condition folders to score; one whose photos do not
            match the manifest is skipped and reported.
        engines: OCR engines by name (`ingest.OCR_ENGINES`).
        systems: Detector systems, named as for `benchmark run`.
        compare: Pairs of systems (baseline, candidate) to compare.
        primary: The pair whose outcome gets the rule's sentence.
        resource_root: Storage root holding `models/`.
        engine_loader: Loads an engine by name; tests give a stand-in.
        detectors: Detector factories by system, instead of loading `systems`.
        set_name: Which photo set this is (`test`, `train`), recorded.
        run_name: Suffix of the result files.
        redacted: Keep the redacted copies here; by default they are discarded.
        resample_count: Bootstrap resamples.

    Returns:
        The results, as written to the JSON file.

    Raises:
        PhotoSetError: If the manifest names a document without a file, a
            document has another page count than the manifest says, or no
            condition can be scored.
        ValueError: If a compared system is not run.
    """
    for pair in (*compare, *([primary] if primary else [])):
        unknown = set(pair) - set(systems)
        if unknown:
            msg = f"compared systems not run: {sorted(unknown)}"
            raise ValueError(msg)
    manifest = read_manifest(manifest_path)
    factories = dict(detectors) if detectors else detector_factories(systems, resource_root)
    sets, skipped = _photo_sets(photos, manifest, conditions)
    if not sets:
        msg = "no condition can be scored:\n" + "\n".join(skipped.values())
        raise PhotoSetError(msg)
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch)
        truths = _truths(manifest, documents, work / "pdf")
        keep = redacted or work / "redacted"
        keep.mkdir(parents=True, exist_ok=True)
        rows: dict[str, dict[str, Any]] = {}
        rows[DIGITAL] = _row(
            {name: _digital(truth, factories, keep) for name, truth in truths.items()},
            None,
            compare,
            resample_count,
        )
        runs: dict[str, dict[str, Any]] = {}
        failed: dict[str, str] = {}
        for engine_name in engines:
            try:
                engine = engine_loader(engine_name, resource_root)
                runs[engine_name] = {
                    condition: _condition(
                        engine_name, engine, truths, paths, factories, keep, compare, resample_count
                    )
                    for condition, paths in sets.items()
                }
            # The rules report an engine that fails on photos and score the others.
            except Exception as error:
                failed[engine_name] = type(error).__name__
    handwritten = _handwritten_rows(runs, failed)
    results: dict[str, Any] = {
        "schema": PHOTOS_SCHEMA,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git_commit": git_commit(),
        "machine": machine(),
        "set": set_name,
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "document_set": document_set(documents),
        "documents": [entry.document for entry in manifest],
        "engines": [engine for engine in engines if engine in runs],
        "failed_engines": failed,
        "models": ocr_model_versions(engines)
        | ({} if detectors else _model_versions(systems, resource_root)),
        "thresholds": {} if detectors else _model_thresholds(systems, resource_root),
        "systems": list(systems),
        "seed": SEED,
        "resamples": resample_count,
        "conditions": list(sets),
        "skipped_conditions": skipped,
        "photos": {
            condition: {path.name: _sha256(path) for path in paths}
            for condition, paths in sets.items()
        },
        "digital": rows[DIGITAL],
        "runs": runs,
        "handwritten": handwritten,
        "engine_comparisons": _engine_comparisons(runs, resample_count),
        "primary": _primary(primary, rows[DIGITAL], runs.get(PRIMARY_ENGINE)),
    }
    output.mkdir(parents=True, exist_ok=True)
    stem = f"photos-{run_name}" if run_name else "photos"
    (output / f"{stem}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / f"{stem}.md").write_text(photos_markdown(results), encoding="utf-8")
    return results


def _photo_sets(
    root: Path, manifest: list[ManifestEntry], conditions: tuple[str, ...]
) -> tuple[dict[str, list[Path]], dict[str, str]]:
    sets: dict[str, list[Path]] = {}
    skipped: dict[str, str] = {}
    for condition in conditions:
        try:
            sets[condition] = named_photos(root / condition, manifest, condition)
        except PhotoSetError as error:
            skipped[condition] = str(error)
    return sets, skipped


def _truths(manifest: list[ManifestEntry], documents: Path, pdf_folder: Path) -> dict[str, _Truth]:
    specs = {spec.name: spec for spec in load_documents(documents)}
    missing = [entry.document for entry in manifest if entry.document not in specs]
    if missing:
        msg = f"no document file for {', '.join(missing)} in {documents}"
        raise PhotoSetError(msg)
    truths: dict[str, _Truth] = {}
    for entry in manifest:
        spec = specs[entry.document]
        pdf = render(spec, pdf_folder / f"{spec.name}.pdf")
        document = load_document(pdf, language=spec.language)
        if len(document.pages) != entry.pages:
            msg = (
                f"{spec.name} renders to {len(document.pages)} pages, "
                f"the manifest says {entry.pages}"
            )
            raise PhotoSetError(msg)
        on_page = dataclasses.replace(
            spec, gold=tuple(item for item in spec.gold if item.carrier == "page")
        )
        located = page_locations(on_page, document)
        pages = [page.text for page in document.pages]
        handwritten = tuple(item for item in spec.gold if item.carrier == "handwritten")
        truths[spec.name] = _Truth(
            spec=on_page,
            pdf=pdf,
            pages=pages,
            sizes=[(page.width, page.height) for page in document.pages],
            items=on_page.gold,
            locations=[located.get(index) for index in range(len(on_page.gold))],
            handwritten=handwritten,
            handwriting=_handwriting(spec, pages, handwritten),
        )
    return truths


def _handwriting(
    spec: DocumentSpec, pages: list[str], items: tuple[GoldItem, ...]
) -> tuple[_Handwriting, ...]:
    """Insert each handwritten text after its label, one space between, and place its items.

    Raises:
        PhotoSetError: If a label is not a line of the pages after the
            previous one, or a handwritten item is in no handwritten text.
    """
    texts = list(pages)
    fields: list[list[Span]] = [[] for _ in pages]
    placed: list[list[tuple[int, Span]]] = [[] for _ in pages]
    cursor = (0, 0)
    item_index = 0
    for block in spec.blocks:
        if not isinstance(block, Handwritten):
            continue
        page_index, label_end = _label_end(texts, block.label, cursor, spec.name)
        page = texts[page_index]
        start = label_end + 1
        texts[page_index] = f"{page[:label_end]} {block.text}{page[label_end:]}"
        fields[page_index].append((start, start + len(block.text)))
        # Items are collected in reading order, so a line's items come next and in order.
        offset = 0
        while item_index < len(items):
            text = items[item_index].text
            found = block.text.find(text, offset)
            if found < 0:
                break
            placed[page_index].append((item_index, (start + found, start + found + len(text))))
            offset = found + len(text)
            item_index += 1
        cursor = (page_index, start + len(block.text))
    if item_index < len(items):
        msg = f"{spec.name}: a handwritten item is in no handwritten text"
        raise PhotoSetError(msg)
    return tuple(
        _Handwriting(text, tuple(spans), tuple(on_page))
        for text, spans, on_page in zip(texts, fields, placed, strict=True)
    )


def _label_end(texts: list[str], label: str, cursor: tuple[int, int], name: str) -> tuple[int, int]:
    """Return the page and end offset of `label` printed as a line of its own, after `cursor`."""
    line = re.compile(rf"^{re.escape(label)}[ \t]*$", re.MULTILINE)
    for page_index in range(cursor[0], len(texts)):
        match = line.search(texts[page_index], cursor[1] if page_index == cursor[0] else 0)
        if match:
            return page_index, match.start() + len(label)
    msg = f"{name}: the label {label!r} of a handwritten line is not on its pages"
    raise PhotoSetError(msg)


def _digital(truth: _Truth, factories: Mapping[str, DetectorFactory], keep: Path) -> dict[str, Any]:
    document = load_document(truth.pdf, language=truth.spec.language)
    scored: dict[str, _Scored] = {}
    for system, factory in factories.items():
        run_detection(document, factory(truth.spec.language))
        result = _score(document, truth.items, truth.locations)
        destination = keep / f"{truth.spec.name}.{_safe(system)}.pdf"
        result.leak_check_passed = not export_redacted(truth.pdf, document, destination)
        scored[system] = result
    return {"photos": [], "systems": scored}


def _condition(
    engine_name: str,
    engine: OcrEngine,
    truths: dict[str, _Truth],
    paths: list[Path],
    factories: Mapping[str, DetectorFactory],
    keep: Path,
    compare: tuple[tuple[str, str], ...],
    resample_count: int,
) -> dict[str, Any]:
    # Photos come in print order, which is the order of the truths.
    remaining = iter(paths)
    by_document = {name: [next(remaining) for _ in truth.pages] for name, truth in truths.items()}
    documents: dict[str, dict[str, Any]] = {}
    reads_handwriting = engine_name == HANDWRITING_ENGINE
    hands: dict[str, dict[str, Any]] = {}
    for name, truth in truths.items():
        scored = {system: _Scored() for system in factories}
        hand_scored = {system: _HandScored() for system in factories}
        hand_text = TextTally()
        text = TextTally()
        for page_index, photo in enumerate(by_document[name]):
            document = load_document(photo, language=truth.spec.language, ocr=engine)
            page_text = document.pages[0].text
            width, height = truth.sizes[page_index]
            errors = text_errors(
                [TruthPage(truth.pages[page_index], (), (), width, height)], document.pages
            )
            text += TextTally(**{key: errors.get(key, 0) for key in TextTally.columns()})
            indices = [
                index
                for index, location in enumerate(truth.locations)
                if (location is not None and location[0] == page_index)
                # An item the truth does not hold is charged to the first photo.
                or (location is None and page_index == 0)
            ]
            spans = [truth.locations[index] for index in indices]
            located = locate(
                truth.pages[page_index], [span[1:] for span in spans if span], page_text
            )
            positions = iter(located)
            items = [truth.items[index] for index in indices]
            placed: list[Location | None] = []
            for span in spans:
                found = next(positions) if span else None
                placed.append(None if found is None else (0, *found))
            hand = truth.handwriting[page_index]
            field_spans, item_spans = _locate_handwriting(hand, page_text)
            written = [(0, *span) for span in field_spans if span]
            if reads_handwriting:
                hand_text += _handwriting_errors(hand, field_spans, page_text)
            hand_items = tuple(truth.handwritten[index] for index, _ in hand.items)
            for system, factory in factories.items():
                run_detection(document, factory(truth.spec.language))
                result = _score(document, tuple(items), placed, written)
                destination = keep / f"{photo.stem}.{engine_name}.{_safe(system)}.pdf"
                passed = not export_redacted(photo, document, destination, ocr=engine)
                result.leak_check_passed = passed
                scored[system] = _merge(scored[system], result)
                if reads_handwriting:
                    hand_scored[system] += _score_handwriting(document, hand_items, item_spans)
        documents[name] = {
            "photos": [photo.name for photo in by_document[name]],
            "text": text,
            "systems": scored,
        }
        hands[name] = {"text": hand_text, "systems": hand_scored, "printed": scored}
    row = _row(documents, "text", compare, resample_count)
    if reads_handwriting:
        row["handwritten"] = _hand_row(hands)
    return row


def _locate_handwriting(
    hand: _Handwriting, page_text: str
) -> tuple[list[Span | None], list[Span | None]]:
    """Locate a page's handwritten texts and items in what OCR read of it."""
    if not hand.fields:
        return [], []
    located = locate(hand.text, [*hand.fields, *(span for _, span in hand.items)], page_text)
    return located[: len(hand.fields)], located[len(hand.fields) :]


def _handwriting_errors(
    hand: _Handwriting, located: list[Span | None], page_text: str
) -> TextTally:
    """Edit distance of each handwritten text to its located span; a text not read is all errors."""
    characters = errors = 0
    for (start, end), span in zip(hand.fields, located, strict=True):
        truth = spaced(hand.text[start:end]).text
        read = spaced(page_text[span[0] : span[1]]).text if span else ""
        characters += len(truth)
        errors += Levenshtein.distance(truth, read)
    return TextTally(characters=characters, character_errors=errors)


def _score_handwriting(
    document: Document, items: tuple[GoldItem, ...], located: list[Span | None]
) -> _HandScored:
    """Score handwritten items at their located spans, as page items are scored."""
    as_printed = tuple(dataclasses.replace(item, carrier="page") for item in items)
    spec = DocumentSpec(name="", language="", kind="", lines=(), gold=as_printed)
    placed = {index: None if span is None else (0, *span) for index, span in enumerate(located)}
    outcomes = [outcome for outcome, _ in score_detection(spec, document, placed)]
    return _HandScored(
        gold=len(items),
        not_read=sum(span is None for span in located),
        found=outcomes.count("found"),
        partial=outcomes.count("partial"),
        missed=outcomes.count("missed"),
    )


def _hand_row(hands: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Pool one condition's handwritten items: counts per system, CER, documents safe overall."""
    systems = list(next(iter(hands.values()))["systems"])
    pooled = total([hand["text"] for hand in hands.values()])

    def safe_overall(hand: dict[str, Any], system: str) -> bool:
        written: _HandScored = hand["systems"][system]
        return hand["printed"][system].safe and written.found == written.gold

    return {
        "character_error_rate": _rounded(pooled.metric("cer")),
        "characters": pooled.characters,
        "documents": {
            name: {
                system: hand["systems"][system].to_dict()
                | {"safe_overall": safe_overall(hand, system)}
                for system in systems
            }
            for name, hand in hands.items()
        },
        "totals": {
            system: _HandScored(
                *(
                    sum(getattr(hand["systems"][system], key) for hand in hands.values())
                    for key in _HAND_KEYS
                )
            ).to_dict()
            | {
                "safe_overall": sum(safe_overall(hand, system) for hand in hands.values()),
                "documents": len(hands),
            }
            for system in systems
        },
    }


def _handwritten_rows(runs: dict[str, dict[str, Any]], failed: dict[str, str]) -> dict[str, Any]:
    """Move kraken's handwritten rows out of its runs; without them the row is not available."""
    rows = {
        condition: row.pop("handwritten")
        for condition, row in runs.get(HANDWRITING_ENGINE, {}).items()
    }
    if rows:
        return {"engine": HANDWRITING_ENGINE, "available": True, "conditions": rows}
    reason = "failed" if HANDWRITING_ENGINE in failed else "not run"
    return {"engine": HANDWRITING_ENGINE, "available": False, "reason": reason, "conditions": {}}


def _score(
    document: Document,
    items: Sequence[GoldItem],
    locations: Sequence[Location | None],
    handwriting: Sequence[Location] = (),
) -> _Scored:
    """Score one read document against items placed in its pages (`None`: not read).

    A detection overlapping `handwriting` and no placed item is left out: the
    handwritten row scores it.
    """
    planted = [location for location in locations if location]
    document = dataclasses.replace(
        document,
        entities=[
            entity
            for entity in document.entities
            if not _touches(entity, handwriting) or _touches(entity, planted)
        ],
    )
    spec = DocumentSpec(name="", language="", kind="", lines=(), gold=tuple(items))
    placed = dict(enumerate(locations))
    outcomes = score_detection(spec, document, placed)
    texts = [page.text for page in document.pages]
    gold: list[Entity] = []
    unread: list[str] = []
    for item, location in zip(items, locations, strict=True):
        if item.type is not PERSON:
            continue
        if location is None:
            unread.append(item.text)
            continue
        page_index, start, end = location
        gold.append(Entity(PERSON, page_index, start, end, texts[page_index][start:end]))
    # Persons not read sit on a page of their own that no detection reaches.
    extra_page = " ".join(unread)
    cursor = 0
    for text in unread:
        gold.append(Entity(PERSON, len(texts), cursor, cursor + len(text), text))
        cursor += len(text) + 1
    pages = [*texts, extra_page]
    whole = "\n".join(texts)
    not_read = [item for item, location in zip(items, locations, strict=True) if not location]
    return _Scored(
        gold=len(items),
        found=sum(outcome == "found" for outcome, _ in outcomes),
        partial=sum(outcome == "partial" for outcome, _ in outcomes),
        missed=sum(outcome == "missed" for outcome, _ in outcomes),
        not_read=len(not_read),
        not_read_present=sum(bool(words_pattern(item.text).search(whole)) for item in not_read),
        counts=document_counts(document.entities, gold, [PERSON])[PARTIAL, str(PERSON)],
        coverage=document_coverage(document.entities, gold, [PERSON], pages)[str(PERSON)],
        false_positives=set(false_positives(spec, document, placed)),
    )


def _touches(entity: Entity, locations: Sequence[Location]) -> bool:
    start, end = entity.span
    return any(
        entity.page_index == page_index and start < stop and begin < end
        for page_index, begin, stop in locations
    )


def _merge(first: _Scored, second: _Scored) -> _Scored:
    return _Scored(
        gold=first.gold + second.gold,
        found=first.found + second.found,
        partial=first.partial + second.partial,
        missed=first.missed + second.missed,
        not_read=first.not_read + second.not_read,
        not_read_present=first.not_read_present + second.not_read_present,
        counts=first.counts + second.counts,
        coverage=first.coverage + second.coverage,
        false_positives=first.false_positives | second.false_positives,
        leak_check_passed=first.leak_check_passed and second.leak_check_passed,
    )


def _row(
    documents: dict[str, dict[str, Any]],
    text_key: str | None,
    compare: tuple[tuple[str, str], ...],
    resample_count: int,
) -> dict[str, Any]:
    """Pool one row's documents: totals, intervals and comparisons per system."""
    names = list(documents)
    draws = resamples(len(names), resample_count, SEED)
    resampler = Resampler(len(names), draws)
    systems = list(documents[names[0]]["systems"])
    bootstrapped: dict[str, tuple[Any, Any]] = {}
    totals: dict[str, Any] = {}
    for system in systems:
        scores: list[_Scored] = [documents[name]["systems"][system] for name in names]
        counts = [score.counts for score in scores]
        coverage = [score.coverage for score in scores]
        bootstrapped[system] = (
            (counts, resampler.totals(counts)),
            (coverage, resampler.totals(coverage)),
        )
        totals[system] = {
            "items": {
                key: sum(getattr(score, key) for score in scores)
                for key in ("gold", "found", "partial", "missed", "not_read", "not_read_present")
            },
            "person_recall": interval(counts, bootstrapped[system][0][1], "recall").to_dict(),
            "person_f2": interval(counts, bootstrapped[system][0][1], "f2").to_dict(),
            "person_residual": interval(coverage, bootstrapped[system][1][1], "residual").to_dict(),
            "false_alarms": sum(len(score.false_positives) for score in scores),
            "safe_documents": sum(score.safe for score in scores),
            "leak_check_passed": sum(score.leak_check_passed for score in scores),
            "documents": len(scores),
        }
    row: dict[str, Any] = {
        "documents": {
            name: {
                "photos": documents[name]["photos"],
                "systems": {
                    system: score.to_dict() for system, score in documents[name]["systems"].items()
                },
            }
            | ({"text": documents[name][text_key].to_dict()} if text_key else {})
            for name in names
        },
        "totals": totals,
        "comparisons": [
            _comparison(baseline, candidate, bootstrapped) for baseline, candidate in compare
        ],
    }
    if text_key:
        tallies: list[TextTally] = [documents[name][text_key] for name in names]
        pooled = total(tallies)
        row["text"] = pooled.to_dict() | {
            "character_error_rate": _rounded(pooled.metric("cer")),
            "diacritic_error_rate": _rounded(pooled.metric("diacritics")),
        }
        row["_text_tallies"] = (tallies, resampler.totals(tallies))
    return row


def _comparison(
    baseline: str, candidate: str, bootstrapped: Mapping[str, tuple[Any, Any]]
) -> dict[str, Any]:
    f2 = paired_difference(bootstrapped[baseline][0], bootstrapped[candidate][0], "f2").to_dict()
    residual = paired_difference(
        bootstrapped[baseline][1], bootstrapped[candidate][1], "residual"
    ).to_dict()
    bounds = (f2["low"], f2["high"], residual["low"], residual["high"])
    outcome = "n/a" if None in bounds else set_outcome(f2, residual)  # pyright: ignore[reportArgumentType]
    return {
        "baseline": baseline,
        "candidate": candidate,
        "f2": f2,
        "residual": residual,
        "outcome": outcome,
    }


def _engine_comparisons(
    runs: dict[str, dict[str, Any]], resample_count: int
) -> list[dict[str, Any]]:
    """CER of every further engine against the first, per condition; drops the raw tallies."""
    del resample_count
    names = list(runs)
    found: list[dict[str, Any]] = []
    for candidate in names[1:]:
        for condition, row in runs[candidate].items():
            difference = paired_difference(
                runs[names[0]][condition]["_text_tallies"], row["_text_tallies"], "cer"
            )
            found.append(
                {
                    "baseline": names[0],
                    "candidate": candidate,
                    "condition": condition,
                    "cer": difference.to_dict(),
                }
            )
    for engine_runs in runs.values():
        for row in engine_runs.values():
            row.pop("_text_tallies", None)
    return found


def _primary(
    pair: tuple[str, str] | None,
    digital: dict[str, Any],
    onnxtr: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """The primary comparison's outcome per condition and its fixed sentence."""
    if pair is None:
        return None
    baseline, candidate = pair
    if onnxtr is None:
        return {"baseline": baseline, "candidate": candidate, "sentence": None}

    def outcome(row: dict[str, Any]) -> str:
        return next(
            comparison["outcome"]
            for comparison in row["comparisons"]
            if (comparison["baseline"], comparison["candidate"]) == pair
        )

    outcomes = {
        condition: outcome(onnxtr[condition]) if condition in onnxtr else "not scored"
        for condition in CONDITIONS
    }
    on_digital = outcome(digital)
    listed = ", ".join(f"{condition} {result}" for condition, result in outcomes.items())
    if all(result == "win" for result in outcomes.values()):
        sentence = f"{candidate} is better on phone photos than {baseline}"
    else:
        sentence = f"{candidate} is not better on phone photos than {baseline}"
    sentence += f" ({listed}; digital {on_digital})"
    return {
        "baseline": baseline,
        "candidate": candidate,
        "engine": PRIMARY_ENGINE,
        "outcomes": outcomes,
        "digital": on_digital,
        "sentence": sentence,
    }


def photos_markdown(results: dict[str, Any]) -> str:
    """Render a photo run as Markdown tables."""
    machine_info = results["machine"]
    commit = results.get("git_commit")
    lines = [
        f"# Phone photos ({results['set']} set): anonymizer {results['tool_version']}",
        "",
        f"Run {results['created']} on {machine_info['system']} {machine_info['machine']}, "
        f"Python {machine_info['python']}" + (f", commit `{commit[:7]}`" if commit else "") + ". "
        f"Scored as `experiments/photo-rules.md` fixes it; {len(results['documents'])} documents, "
        f"bootstrap {results['resamples']} resamples, seed {results['seed']}.",
    ]
    for condition, reason in results["skipped_conditions"].items():
        lines.append(f"\nNot scored: {condition} ({reason.splitlines()[0]}).")
    for engine, failure in results["failed_engines"].items():
        lines.append(f"\nEngine {engine} failed ({failure}); not scored.")
    header = [
        "row",
        "system",
        "CER",
        "diacritics",
        "not read",
        "found",
        "partial",
        "missed",
        "person recall",
        "person F2",
        "person residual",
        "safe (printed)",
        "leak check passed",
        "false alarms",
    ]
    lines += ["", "## Scores", "", _cells(header), _cells(["---"] * len(header))]
    rows = [(DIGITAL, None, results["digital"])] + [
        (f"{engine} {condition}", engine, row)
        for engine, conditions in results["runs"].items()
        for condition, row in conditions.items()
    ]
    for label, _, row in rows:
        text = row.get("text")
        for system, scores in row["totals"].items():
            items = scores["items"]
            lines.append(
                _cells(
                    [
                        label,
                        system,
                        _percent(text["character_error_rate"]) if text else "—",
                        _percent(text["diacritic_error_rate"]) if text else "—",
                        str(items["not_read"]),
                        f"{items['found']}/{items['gold']}",
                        str(items["partial"]),
                        str(items["missed"]),
                        _interval(scores["person_recall"]),
                        _interval(scores["person_f2"]),
                        _interval(scores["person_residual"]),
                        f"{scores['safe_documents']}/{scores['documents']}",
                        f"{scores['leak_check_passed']}/{scores['documents']}",
                        str(scores["false_alarms"]),
                    ]
                )
            )
    lines += _handwritten_markdown(results["handwritten"])
    comparisons = [
        (label, comparison) for label, _, row in rows for comparison in row["comparisons"]
    ]
    if comparisons:
        lines += [
            "",
            "## Comparisons (candidate minus baseline, paired 95 % interval)",
            "",
            "| row | baseline | candidate | ΔF2 (person, partial) | Δresidual share | outcome |",
            "|---|---|---|---|---|---|",
        ]
        for label, comparison in comparisons:
            lines.append(
                _cells(
                    [
                        label,
                        comparison["baseline"],
                        comparison["candidate"],
                        _delta(comparison["f2"]),
                        _delta(comparison["residual"]),
                        comparison["outcome"],
                    ]
                )
            )
    if results["engine_comparisons"]:
        lines += ["", "## OCR engines (ΔCER)", "", "| condition | baseline | candidate | ΔCER |"]
        lines.append("|---|---|---|---|")
        for comparison in results["engine_comparisons"]:
            lines.append(
                _cells(
                    [
                        comparison["condition"],
                        comparison["baseline"],
                        comparison["candidate"],
                        _delta(comparison["cer"]),
                    ]
                )
            )
    primary = results.get("primary")
    if primary and primary.get("sentence"):
        lines += ["", "## Primary comparison", "", f"{primary['sentence']}."]
    photo_count = sum(len(photos) for photos in results["photos"].values())
    lines += ["", f"{photo_count} photos, SHA-256 of each in the JSON file."]
    return "\n".join(lines) + "\n"


def _handwritten_markdown(handwritten: dict[str, Any]) -> list[str]:
    lines = ["", f"## Handwritten items ({handwritten['engine']}, counts only)", ""]
    if not handwritten["available"]:
        return [*lines, f"Not available ({handwritten['engine']} {handwritten['reason']})."]
    header = [
        "condition",
        "system",
        "CER",
        "not read",
        "found",
        "partial",
        "missed",
        "safe overall",
    ]
    lines += [_cells(header), _cells(["---"] * len(header))]
    for condition, row in handwritten["conditions"].items():
        for system, counts in row["totals"].items():
            lines.append(
                _cells(
                    [
                        condition,
                        system,
                        _percent(row["character_error_rate"]),
                        str(counts["not_read"]),
                        f"{counts['found']}/{counts['gold']}",
                        str(counts["partial"]),
                        str(counts["missed"]),
                        f"{counts['safe_overall']}/{counts['documents']}",
                    ]
                )
            )
    return lines


def _cells(cells: list[str]) -> str:
    return "| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |"


def _percent(rate: float | None) -> str:
    return "n/a" if rate is None else f"{rate:.1%}"


def _interval(value: Mapping[str, float | None]) -> str:
    if value["value"] is None:
        return "n/a"
    low, high = value["low"], value["high"]
    bounds = "" if low is None or high is None else f" [{low:.3f}, {high:.3f}]"
    return f"{value['value']:.3f}{bounds}"


def _delta(value: Mapping[str, float | None]) -> str:
    if value["delta"] is None or value["low"] is None or value["high"] is None:
        return "n/a"
    return f"{value['delta']:+.3f} [{value['low']:+.3f}, {value['high']:+.3f}]"


def _rounded(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


def _safe(system: str) -> str:
    return system.replace("|", "_").replace("/", "_")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
