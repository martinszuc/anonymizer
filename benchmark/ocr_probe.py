"""OCR engines on one PDF, reported as counts only: safe to run on a real scan.

The scanned benchmark needs ground truth, which a real scan or a
handwritten page does not have. This reads one PDF with each engine and
reports, per page OCR read: words, lines, mean word confidence and seconds,
then the entities detection found by type, and whether the redacted copy
passes the leak check. Nothing read from the document is printed or written:
no text, no values, no file name, so the output can be shared even when the
input holds personal data.

With `--truth`, a JSON list of each page's expected text (`null` for a page
not to score), the character error rate is reported too, as the benchmark
computes it; `scripts/make_mixed_sample.py --truth` writes one for its sample.

Command line: `uv run python -m benchmark ocr-probe scan.pdf --out probe/ --engines onnxtr,kraken`.
"""

from __future__ import annotations

import json
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

from anonymizer.core.ingest import OcrEngine, OcrWord, PageImage, load_document, load_ocr_engine
from anonymizer.core.pipeline import run_detection
from anonymizer.core.redact import find_leaks, redact_pdf
from rapidfuzz.distance import Levenshtein

from benchmark.run import detector_factories


class _Recording:
    """Passes pictures to an engine and keeps what it read, page by page."""

    def __init__(self, engine: OcrEngine) -> None:
        self.engine = engine
        self.name = engine.name
        self.box_margin = engine.box_margin
        self.pages: list[list[OcrWord]] = []
        self.seconds: list[float] = []

    def read(self, image: PageImage) -> list[OcrWord]:
        started = time.perf_counter()
        words = self.engine.read(image)
        self.seconds.append(time.perf_counter() - started)
        self.pages.append(words)
        return words


def probe(
    pdf: Path,
    *,
    engines: tuple[str, ...],
    language: str = "cs",
    system: str = "rules",
    truth: list[str | None] | None = None,
    resource_root: Path = Path(),
) -> dict[str, Any]:
    """Read a PDF with each engine and count what was read and found.

    Args:
        pdf: The document; it is read, never copied into the output.
        engines: Names from `anonymizer.core.ingest.OCR_ENGINES`.
        language: Detection language.
        system: Detector system, as in the benchmark (`benchmark.run.SYSTEMS`).
        truth: Expected text per page, `None` for a page not to score.
        resource_root: Storage root holding `models/`.

    Returns:
        Per engine: `pages` (per page OCR read: `page`, `words`, `lines`,
        `mean_confidence`, `seconds`, `entities` by type and, with truth,
        `characters` and `character_errors`), `entities` by type over the
        document, and `leak_check_passed`.
    """
    detector = detector_factories((system,), resource_root)[system](language)
    results: dict[str, Any] = {"language": language, "system": system, "engines": {}}
    for name in engines:
        engine = _Recording(load_ocr_engine(name, resource_root))
        document = load_document(pdf, language=language, ocr=engine)
        run_detection(document, detector)
        pages = []
        read_pages = [page for page in document.pages if page.raster_dpi is not None]
        for page, words, seconds in zip(read_pages, engine.pages, engine.seconds, strict=True):
            confidences = [word.confidence for word in words]
            entry: dict[str, Any] = {
                "page": page.index + 1,
                "words": len(page.words),
                "lines": len({(word.block, word.line) for word in words}),
                "mean_confidence": (
                    round(sum(confidences) / len(confidences), 3) if confidences else None
                ),
                "seconds": round(seconds, 2),
                "entities": dict(
                    Counter(
                        entity.type.value
                        for entity in document.entities
                        if entity.page_index == page.index and entity.surface_id is None
                    )
                ),
            }
            expected = truth[page.index] if truth and page.index < len(truth) else None
            if expected is not None:
                original, reading = " ".join(expected.split()), " ".join(page.text.split())
                entry["characters"] = len(original)
                entry["character_errors"] = Levenshtein.distance(original, reading)
            pages.append(entry)
        with tempfile.TemporaryDirectory() as scratch:
            redacted = Path(scratch) / "redacted.pdf"
            redact_pdf(pdf, document, redacted)
            leaks = find_leaks(redacted, document, ocr=engine)
        results["engines"][name] = {
            "pages": pages,
            "entities": dict(Counter(entity.type.value for entity in document.entities)),
            "leak_check_passed": not leaks,
        }
    return results


def probe_markdown(results: dict[str, Any]) -> str:
    """Render a probe as Markdown: one table per engine, counts only."""
    lines = [f"# OCR probe ({results['language']}, detection `{results['system']}`)"]
    for name, run in results["engines"].items():
        lines += [
            "",
            f"## {name}",
            "",
            "| page | words | lines | mean confidence | CER | s | entities |",
            "|---|---|---|---|---|---|---|",
        ]
        for page in run["pages"]:
            cer = (
                f"{page['character_errors'] / page['characters']:.1%}"
                if page.get("characters")
                else "n/a"
            )
            confidence = page["mean_confidence"]
            entities = ", ".join(
                f"{kind} {count}" for kind, count in sorted(page["entities"].items())
            )
            lines.append(
                f"| {page['page']} | {page['words']} | {page['lines']} "
                f"| {'n/a' if confidence is None else f'{confidence:.2f}'} | {cer} "
                f"| {page['seconds']:.1f} | {entities or '-'} |"
            )
        lines += ["", f"Leak check passed: {'yes' if run['leak_check_passed'] else '**no**'}."]
    return "\n".join(lines) + "\n"


def write_probe(results: dict[str, Any], output: Path) -> None:
    """Write `ocr-probe.json` and `ocr-probe.md` into a directory."""
    output.mkdir(parents=True, exist_ok=True)
    (output / "ocr-probe.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (output / "ocr-probe.md").write_text(probe_markdown(results), encoding="utf-8")
