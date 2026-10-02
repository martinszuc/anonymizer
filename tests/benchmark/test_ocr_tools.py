"""The OCR measurement commands: box margins on the benchmark, and the counts-only probe."""

import json
from pathlib import Path

import pytest
from anonymizer.core.ingest import OcrEngine, load_document

from benchmark import ocr_probe
from benchmark.degrade import level_named
from benchmark.ocr_margin import margins_markdown, run_margins
from benchmark.ocr_probe import probe, probe_markdown, write_probe
from tests.benchmark.test_ocr_benchmark import SPEC
from tests.ocr_stand_in import InkReadingEngine
from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_scanned_pdf


def test_margins_are_scored_on_boxes_grown_as_ingest_grows_them(tmp_path: Path):
    results = run_margins(
        tmp_path,
        engines=("oracle",),
        levels=(level_named("clean"),),
        margins=(0.0, 3.0),
        specs=[SPEC],
    )
    by_margin = results["runs"]["oracle"]["clean"]
    # The oracle's boxes are the words' own: no ink outside them, and zero is
    # recorded, not dropped.
    assert by_margin["0.0"]["partly_outside"] == 0
    assert by_margin["3.0"]["partly_outside"] == 0
    # The two lines' boxes do not touch until grown by three times their height.
    assert by_margin["0.0"]["reaching_another_line"] == 0
    assert 0 < by_margin["3.0"]["reaching_another_line"] < by_margin["3.0"]["boxes"]
    assert json.loads((tmp_path / "ocr-margins.json").read_text(encoding="utf-8")) == results
    report = margins_markdown(results)
    assert "## oracle, clean" in report
    assert f"| 0% | 0/{by_margin['0.0']['words']} | 0/" in report


PHONE = "+420 603 123 456"
LINES = [f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "Poznamka: nic osobniho"]


@pytest.fixture
def scan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A scan, with the engine loader replaced by the stand-in reading its original."""
    original = load_document(write_pdf(tmp_path / "original.pdf", [LINES]))

    def load(name: str, root: Path) -> OcrEngine:
        del name, root
        return InkReadingEngine.reading(original)

    monkeypatch.setattr(ocr_probe, "load_ocr_engine", load)
    return write_scanned_pdf(tmp_path / "secret-name.pdf", [LINES])


def test_probe_counts_what_was_read_and_found(scan: Path):
    results = probe(scan, engines=("stand-in",), truth=["\n".join(LINES)])
    run = results["engines"]["stand-in"]
    (page,) = run["pages"]
    assert page["page"] == 1
    assert page["words"] == sum(len(line.split()) for line in LINES)
    assert page["lines"] == len(LINES)
    assert page["character_errors"] == 0
    assert page["characters"] == len(" ".join(LINES))
    assert page["entities"] == {"email": 1, "phone": 1}
    assert run["entities"] == {"email": 1, "phone": 1}
    assert run["leak_check_passed"] is True
    assert "| 1 | 10 | 3 | 0.90 | 0.0% |" in probe_markdown(results)


def test_probe_output_holds_no_text_and_no_file_name(scan: Path, tmp_path: Path):
    write_probe(probe(scan, engines=("stand-in",)), tmp_path / "probe")
    for written in (tmp_path / "probe").iterdir():
        content = written.read_text(encoding="utf-8")
        assert CONTACT_EMAIL not in content
        assert "603" not in content
        assert "Poznamka" not in content
        assert "secret-name" not in content
