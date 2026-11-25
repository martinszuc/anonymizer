"""Invented documents photographed in code and read by OCR, as training text (RQ3 post hoc).

The photo fine-tune (`experiments/photo-rules.md`) learns from text as OCR
reads it off a phone photo. Before the training photos exist, this module
makes such text from the `synthetic` split of `benchmark.photo_train`, with
a seed of its own (`SEED`), never from the `print` split:

1. each document is rendered (`photo_train.render_split`) and located as the
   photo benchmark locates its ground truth (`score.page_locations`);
2. each page is drawn at `RENDER_DPI` and turned into a photo by
   `photo_sim.simulate_photo`, with one of three seeded profiles that echo
   the photo conditions (`PROFILES`: flat, dim, angle; strength, blur, JPEG
   quality and brightness drawn from each profile's range);
3. the photo enters through the tool's own image ingest with OnnxTR, and the
   gold items are placed in what it read by `align.locate`; an item none of
   whose characters was read is dropped and counted.

Each page becomes one JSONL record, `{"document", "text", "spans": [{"type",
"start", "end"}]}`, in `<language>-<split>.jsonl`; `split_of` sends about
`DEV_SHARE` % of the documents to `dev` and the rest to `train`, by a hash
of the document's name. `build.json` records the counts, the OCR time and
each page's degradation, never text. `experiments.datasets` reads the files
as `photo-noisy-cs` and `photo-noisy-sk`.

Command: `python -m benchmark photo-noisy [--out DIR] --count N`.
"""

from __future__ import annotations

import hashlib
import json
import random
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pymupdf
from anonymizer.core.ingest import OcrEngine, load_document
from PIL import Image, ImageEnhance

from benchmark.align import locate
from benchmark.photo_sim import simulate_photo
from benchmark.photo_train import render_split
from benchmark.score import page_locations
from benchmark.spec import GoldItem, load_documents
from experiments.datasets import PHOTO_NOISY_VERSION

SEED = f"photo-noisy/v{PHOTO_NOISY_VERSION}"
"""Seed of the generated documents and of every page's degradation."""

DEV_SHARE = 15
"""Percent of the documents held out as `dev`."""

RENDER_DPI = 200
"""Resolution each page is drawn at before it is degraded."""


@dataclass(frozen=True, slots=True)
class Profile:
    """Ranges a page's degradation is drawn from, each `(low, high)`."""

    strength: tuple[float, float]
    blur: tuple[float, float]
    jpeg_quality: tuple[int, int]
    brightness: tuple[float, float]


PROFILES: dict[str, Profile] = {
    "flat": Profile(
        strength=(0.1, 0.4), blur=(0.0, 0.6), jpeg_quality=(75, 92), brightness=(0.95, 1.0)
    ),
    "dim": Profile(
        strength=(0.3, 0.7), blur=(0.3, 1.2), jpeg_quality=(55, 85), brightness=(0.55, 0.8)
    ),
    "angle": Profile(
        strength=(0.7, 1.0), blur=(0.2, 1.0), jpeg_quality=(60, 88), brightness=(0.85, 1.0)
    ),
}
"""One profile per photo condition of the rules: flat, dim, angle."""


@dataclass(frozen=True, slots=True)
class Degradation:
    """What happened to one page: the profile and the values drawn from it."""

    profile: str
    seed: int
    strength: float
    blur: float
    jpeg_quality: int
    brightness: float


def split_of(name: str) -> str:
    """Return `dev` or `train` for a document, by a hash of its name."""
    digest = int.from_bytes(hashlib.sha256(f"{SEED}/{name}".encode()).digest()[:8], "big")
    return "dev" if digest % 100 < DEV_SHARE else "train"


def degradation(name: str, page_index: int) -> Degradation:
    """Draw one page's degradation, the same on every call."""
    draw = random.Random(f"{SEED}/{name}/{page_index}")
    profile_name = draw.choice(sorted(PROFILES))
    profile = PROFILES[profile_name]
    return Degradation(
        profile=profile_name,
        seed=draw.randrange(2**32),
        strength=round(draw.uniform(*profile.strength), 3),
        blur=round(draw.uniform(*profile.blur), 2),
        jpeg_quality=draw.randint(*profile.jpeg_quality),
        brightness=round(draw.uniform(*profile.brightness), 3),
    )


def degrade(page: Image.Image, applied: Degradation) -> Image.Image:
    """Turn a page picture into a simulated photo of it (dimmed first for a dim profile)."""
    dimmed = ImageEnhance.Brightness(page.convert("RGB")).enhance(applied.brightness)
    return simulate_photo(
        dimmed,
        applied.seed,
        strength=applied.strength,
        blur=applied.blur,
        jpeg_quality=applied.jpeg_quality,
    )


def page_record(
    document: str,
    truth_text: str,
    items: Sequence[tuple[GoldItem, tuple[int, int]]],
    ocr_text: str,
) -> tuple[dict[str, Any], int]:
    """Place a page's items in what OCR read of it.

    Args:
        document: The record's name.
        truth_text: The page's born-digital text.
        items: Each item with its span in `truth_text`.
        ocr_text: What OCR read of the page's photo.

    Returns:
        The record (OCR text, spans of the items read) and the number of
        items not read.
    """
    located = locate(truth_text, [span for _, span in items], ocr_text)
    spans = [
        {"type": str(item.type), "start": found[0], "end": found[1]}
        for (item, _), found in zip(items, located, strict=True)
        if found is not None
    ]
    return {"document": document, "text": ocr_text, "spans": spans}, len(items) - len(spans)


def build(
    out: Path,
    *,
    count: int,
    engine: OcrEngine,
    progress: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    """Generate, degrade and read `count` documents per language; write the JSONL files.

    Args:
        out: Output directory; the rendered documents go to `out/source/`.
        count: Synthetic documents per language.
        engine: The OCR engine photos are read with.
        progress: Called with documents done and documents in all.

    Returns:
        The build's counts, as written to `build.json`.

    Raises:
        ValueError: If `count` is below one.
    """
    source = out / "source"
    render_split(source, split="synthetic", count=count, seed=SEED)
    specs = load_documents(source / "documents")
    records: dict[tuple[str, str], list[dict[str, Any]]] = {}
    counts: Counter[str] = Counter()
    pages: list[dict[str, Any]] = []
    ocr_seconds = 0.0
    with tempfile.TemporaryDirectory() as scratch:
        for done, spec in enumerate(specs, start=1):
            split = split_of(spec.name)
            pdf = source / "pdf" / f"{spec.name}.pdf"
            truth = load_document(pdf, language=spec.language)
            located = page_locations(spec, truth)
            counts["items"] += len(spec.gold)
            counts["items_not_in_truth"] += sum(1 for place in located.values() if place is None)
            with pymupdf.open(pdf) as rendered:
                for page_index in range(rendered.page_count):
                    pixmap = rendered[page_index].get_pixmap(dpi=RENDER_DPI)
                    picture = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
                    applied = degradation(spec.name, page_index)
                    photo_path = Path(scratch) / f"{spec.name}-{page_index}.png"
                    degrade(picture, applied).save(photo_path, dpi=(RENDER_DPI, RENDER_DPI))
                    started = time.perf_counter()
                    read = load_document(photo_path, language=spec.language, ocr=engine)
                    ocr_seconds += time.perf_counter() - started
                    photo_path.unlink()
                    items = [
                        (spec.gold[index], (place[1], place[2]))
                        for index, place in sorted(located.items())
                        if place is not None and place[0] == page_index
                    ]
                    record, not_read = page_record(
                        f"{spec.name}/{page_index + 1}",
                        truth.pages[page_index].text,
                        items,
                        read.pages[0].text,
                    )
                    records.setdefault((spec.language, split), []).append(record)
                    counts["pages"] += 1
                    counts["items_read"] += len(record["spans"])
                    counts["items_not_read"] += not_read
                    pages.append(
                        {
                            "document": spec.name,
                            "page": page_index + 1,
                            "split": split,
                            "items": len(items),
                            "not_read": not_read,
                            **asdict(applied),
                        }
                    )
            if progress is not None:
                progress(done, len(specs))
    for (language, split), written in sorted(records.items()):
        lines = (json.dumps(record, ensure_ascii=False) for record in written)
        (out / f"{language}-{split}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    stats: dict[str, Any] = {
        "version": PHOTO_NOISY_VERSION,
        "seed": SEED,
        "count_per_language": count,
        "render_dpi": RENDER_DPI,
        "dev_share_percent": DEV_SHARE,
        "engine": engine.name,
        "documents": len(specs),
        **dict(sorted(counts.items())),
        "ocr_seconds": round(ocr_seconds, 1),
        "examples": {
            f"{language}-{split}": len(written)
            for (language, split), written in sorted(records.items())
        },
        "documents_per_split": dict(sorted(Counter(split_of(spec.name) for spec in specs).items())),
        "pages_by_profile": dict(sorted(Counter(page["profile"] for page in pages).items())),
        "page_degradations": pages,
    }
    (out / "build.json").write_text(json.dumps(stats, indent=1) + "\n", encoding="utf-8")
    return stats
