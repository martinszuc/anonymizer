"""The leak check breakdown: counts why a check failed, never the text."""

import json
import re
from pathlib import Path

from anonymizer.core.ingest import load_document
from anonymizer.core.types import DetectionSource, Entity, EntityType, Page

from experiments.leaks import breakdown, breakdown_markdown, write_breakdown
from tests.ocr_stand_in import InkReadingEngine, layout_of
from tests.pdf_builders import write_pdf, write_scanned_pdf

LINES = ["pan Novak", "s Novakem", "Nowak dal"]


class NameDetector:
    """Finds one name as a whole word, as a model would."""

    name = "stand-in"

    def detect(self, page: Page) -> list[Entity]:
        return [
            Entity(
                type=EntityType.PERSON,
                page_index=page.index,
                start=found.start(),
                end=found.end(),
                text=found.group(),
                bboxes=page.bboxes_for_span(*found.span()),
                source=DetectionSource.MODEL,
            )
            for found in re.finditer(r"\bNovak\b", page.text)
        ]


def test_counts_where_the_ocr_layer_found_a_redacted_text(tmp_path: Path):
    scan = write_scanned_pdf(tmp_path / "Novak-scan.pdf", [LINES])
    layout = layout_of(load_document(write_pdf(tmp_path / "original.pdf", [LINES])).pages[0])
    # The leak check and the breakdown each re-read "Nowak" as the name.
    renamed = [word._replace(text=word.text.replace("Nowak", "Novak")) for word in layout]
    engine = InkReadingEngine([layout, renamed, renamed])
    results = breakdown(scan, {"stand-in": engine}, NameDetector(), "cs")

    run = results["engines"]["stand-in"]
    assert run["entities"] == {"model/person/4+": 1}
    assert run["leaks"] == {"ocr": 1}
    (group,) = run["groups"]
    assert group["length"] == 5
    assert group["occurrences"] == {"longer_word": 1, "whole_word_read_differently": 1}

    write_breakdown(results, tmp_path / "out")
    written = "".join(path.read_text() for path in (tmp_path / "out").iterdir())
    for text in ("Novak", "Nowak", "pan", "scan"):
        assert text not in written + json.dumps(results) + breakdown_markdown(results)
