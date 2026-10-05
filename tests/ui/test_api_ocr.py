"""The review API on scanned pages, with the ink-reading stand-in in place of the engine."""

from pathlib import Path

import pytest
from anonymizer.core.ingest import OcrEngine, load_document
from anonymizer.ui import api
from anonymizer.ui.api import ReviewApi, ReviewError

from tests.ocr_stand_in import InkReadingEngine
from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_scanned_pdf

PHONE = "+420 603 123 456"
LINES = [f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "Poznamka: nic osobniho"]


@pytest.fixture
def scan(tmp_path: Path) -> Path:
    return write_scanned_pdf(tmp_path / "scan.pdf", [LINES])


@pytest.fixture
def loads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Put the stand-in, named as the engine asked for, in place of the loader; record each load."""
    original = load_document(write_pdf(tmp_path / "original.pdf", [LINES]))
    loaded: list[str] = []

    def load(name: str, root: Path) -> OcrEngine:
        loaded.append(name)
        engine = InkReadingEngine.reading(original)
        engine.name = name
        return engine

    monkeypatch.setattr(api, "load_ocr_engine", load)
    return loaded


def test_scanned_page_is_read_detected_and_marked(scan: Path, loads: list[str]):
    steps: list[tuple[str, int, int]] = []
    payload = ReviewApi().open_pdf(
        str(scan), "cs", progress=lambda *step: steps.append(step), ocr_engine="onnxtr"
    )
    (page,) = payload["pages"]
    assert page["raster_dpi"] == 300
    assert page["has_text_layer"] is False
    assert {entity["type"] for entity in payload["entities"]} == {"email", "phone"}
    assert steps == [
        ("loading_ocr", 0, 0),
        ("reading", 0, 0),
        ("ocr", 0, 1),
        ("ocr", 1, 1),
        ("detecting", 0, 1),
        ("detecting", 1, 1),
    ]
    assert loads == ["onnxtr"]


def test_engine_is_loaded_once_per_session(scan: Path, loads: list[str]):
    reviewer = ReviewApi()
    reviewer.open_pdf(str(scan), "cs", ocr_engine="onnxtr")
    steps: list[str] = []
    reviewer.open_pdf(
        str(scan), "cs", progress=lambda step, *_: steps.append(step), ocr_engine="onnxtr"
    )
    assert loads == ["onnxtr"]
    assert "loading_ocr" not in steps


def test_export_re_reads_with_the_engine_and_needs_no_consent(
    scan: Path, loads: list[str], tmp_path: Path
):
    reviewer = ReviewApi()
    reviewer.open_pdf(str(scan), "cs", ocr_engine="onnxtr")
    result = reviewer.export(str(tmp_path / "out.pdf"))
    assert result["written"] is True
    assert result["pages_without_text"] == []


def test_the_chosen_engine_reads_and_re_reads_on_export(
    scan: Path, loads: list[str], tmp_path: Path
):
    reviewer = ReviewApi()
    payload = reviewer.open_pdf(str(scan), "cs", ocr_engine="kraken")
    assert {entity["type"] for entity in payload["entities"]} == {"email", "phone"}
    assert reviewer._open is not None
    assert reviewer._open.document.ocr_engine == "kraken"
    assert reviewer.export(str(tmp_path / "out.pdf"))["written"] is True
    assert loads == ["kraken"]


def test_each_engine_is_loaded_once_and_kept(scan: Path, loads: list[str]):
    reviewer = ReviewApi()
    for engine in ("onnxtr", "kraken", "onnxtr", "kraken"):
        reviewer.open_pdf(str(scan), "cs", ocr_engine=engine)
    assert loads == ["onnxtr", "kraken"]


def test_an_unknown_engine_is_refused_before_anything_loads(scan: Path, loads: list[str]):
    reviewer = ReviewApi()
    with pytest.raises(ReviewError, match="unknown OCR engine 'tesseract'"):
        reviewer.open_pdf(str(scan), "cs", ocr_engine="tesseract")
    assert loads == []
    with pytest.raises(ReviewError, match="no document is open"):
        reviewer.document()


def test_without_ocr_the_scan_still_needs_consent(scan: Path, tmp_path: Path):
    reviewer = ReviewApi()
    payload = reviewer.open_pdf(str(scan), "cs")
    assert payload["pages"][0]["raster_dpi"] is None
    with pytest.raises(ReviewError, match="is a scan OCR has not read"):
        reviewer.export(str(tmp_path / "out.pdf"))


def test_unavailable_engine_is_reported(scan: Path, tmp_path: Path):
    with pytest.raises(ReviewError, match="OCR engine is not available"):
        ReviewApi(tmp_path / "no-models").open_pdf(str(scan), "cs", ocr_engine="onnxtr")


def test_saved_review_reopens_with_the_engine_it_names(
    scan: Path, loads: list[str], tmp_path: Path
):
    reviewer = ReviewApi()
    reviewer.open_pdf(str(scan), "cs", ocr_engine="onnxtr")
    reviewer.save_session(str(tmp_path / "review.json"))
    later = ReviewApi()
    steps: list[tuple[str, int, int]] = []
    payload = later.open_session(
        str(scan), str(tmp_path / "review.json"), lambda *step: steps.append(step)
    )
    assert payload["pages"][0]["raster_dpi"] == 300
    assert loads == ["onnxtr", "onnxtr"]
    assert steps == [("loading_ocr", 0, 0), ("reading", 0, 0), ("ocr", 0, 1), ("ocr", 1, 1)]
    assert later.export(str(tmp_path / "out.pdf"))["written"] is True


def test_saved_review_read_by_kraken_reopens_with_kraken(
    scan: Path, loads: list[str], tmp_path: Path
):
    reviewer = ReviewApi()
    reviewer.open_pdf(str(scan), "cs", ocr_engine="kraken")
    reviewer.save_session(str(tmp_path / "review.json"))
    later = ReviewApi()
    later.open_session(str(scan), str(tmp_path / "review.json"))
    assert loads == ["kraken", "kraken"]
    assert later._open is not None
    assert later._open.document.ocr_engine == "kraken"
    assert later.export(str(tmp_path / "out.pdf"))["written"] is True


def test_review_without_ocr_reopens_without_loading_an_engine(scan: Path, tmp_path: Path):
    reviewer = ReviewApi()
    reviewer.open_pdf(str(scan), "cs")
    reviewer.save_session(str(tmp_path / "review.json"))
    payload = ReviewApi().open_session(str(scan), str(tmp_path / "review.json"))
    assert payload["pages"][0]["raster_dpi"] is None


def test_export_refuses_when_the_engine_that_read_it_is_gone(
    scan: Path, loads: list[str], tmp_path: Path
):
    reviewer = ReviewApi()
    reviewer.open_pdf(str(scan), "cs", ocr_engine="onnxtr")
    reviewer._ocr.clear()
    with pytest.raises(ReviewError, match="not loaded"):
        reviewer.export(str(tmp_path / "out.pdf"))


def test_a_word_ocr_read_can_be_added_and_is_redacted(scan: Path, loads: list[str], tmp_path: Path):
    reviewer = ReviewApi()
    reviewer.open_pdf(str(scan), "cs", ocr_engine="onnxtr")
    # "osobniho" is no personal data; it stands for a word detection missed.
    (word,) = [word for word in reviewer.page_words(0) if word["text"] == "osobniho"]
    (added,) = reviewer.add_finding(0, word["start"], word["end"], "other")
    assert added["boxes"] == [word["box"]]
    result = reviewer.export(str(tmp_path / "out.pdf"))
    # The leak check re-read the page with the engine and found the word gone.
    assert result["written"] is True
    assert result["redacted"] == 3
