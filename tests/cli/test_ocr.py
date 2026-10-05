"""The command line on scanned pages: `--ocr` through detect, redact, check and inspect.

The engine is the ink-reading stand-in (`tests.ocr_stand_in`), put in place
of the real loader; it reads the scan's born-digital original and, when the
leak check re-reads a redacted page, only what is still printed.
"""

from pathlib import Path

import pytest
from anonymizer.cli import main as main_module
from anonymizer.cli.main import main
from anonymizer.core.ingest import OcrEngine, load_document
from anonymizer.core.resources import choose_resource_root
from anonymizer.core.session import save_session

from tests.ocr_stand_in import InkReadingEngine
from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_scanned_pdf

PHONE = "+420 603 123 456"
LINES = [f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "Poznamka: nic osobniho"]


@pytest.fixture
def scan(tmp_path: Path) -> Path:
    return write_scanned_pdf(tmp_path / "scan.pdf", [LINES])


@pytest.fixture
def roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, Path]]:
    """Replace the engine loader with the stand-in and record what was asked for."""
    original = load_document(write_pdf(tmp_path / "original.pdf", [LINES]))
    asked: list[tuple[str, Path]] = []

    def load(name: str, root: Path) -> OcrEngine:
        asked.append((name, root))
        return InkReadingEngine.reading(original)

    monkeypatch.setattr(main_module, "load_ocr_engine", load)
    return asked


def test_scan_is_refused_without_ocr(scan: Path, capsys: pytest.CaptureFixture):
    assert main(["redact", str(scan), "-o", str(scan.with_name("out.pdf"))]) == 1
    assert "--ocr onnxtr" in capsys.readouterr().err


def test_redact_reads_the_scan_and_passes_the_leak_check(
    scan: Path, roots: list[tuple[str, Path]], capsys: pytest.CaptureFixture
):
    output = scan.with_name("out.pdf")
    args = ["redact", str(scan), "-o", str(output), "--lang", "cs", "--ocr", "onnxtr"]
    assert main([*args, "--resource-root", str(scan.parent)]) == 0
    assert roots == [("onnxtr", scan.parent)]
    assert "leak check passed" in capsys.readouterr().out
    assert output.exists()


def test_review_of_a_scan_reopens_and_checks_with_the_engine(
    scan: Path, roots: list[tuple[str, Path]], capsys: pytest.CaptureFixture
):
    session, output = scan.with_name("review.json"), scan.with_name("out.pdf")
    assert main(["detect", str(scan), "-o", str(session), "--lang", "cs", "--ocr", "onnxtr"]) == 0
    redact = ["redact", str(scan), "-o", str(output), "--session", str(session)]
    assert main([*redact, "--ocr", "onnxtr"]) == 0
    check = ["check", str(output), "--source", str(scan), "--session", str(session)]
    assert main([*check, "--ocr", "onnxtr"]) == 0
    assert capsys.readouterr().out.count("leak check passed") == 2
    assert len(roots) == 3


def test_check_of_a_scan_without_the_engine_is_an_error(
    scan: Path, roots: list[tuple[str, Path]], capsys: pytest.CaptureFixture
):
    session, output = scan.with_name("review.json"), scan.with_name("out.pdf")
    main(["detect", str(scan), "-o", str(session), "--ocr", "onnxtr"])
    main(["redact", str(scan), "-o", str(output), "--session", str(session), "--ocr", "onnxtr"])
    capsys.readouterr()
    assert main(["check", str(output), "--source", str(scan), "--session", str(session)]) == 1
    assert "made with OCR engine 'stand-in'" in capsys.readouterr().err


def test_inspect_says_the_page_was_read_by_ocr(scan: Path, roots: list[tuple[str, Path]]):
    report = scan.with_name("scan.html")
    assert main(["inspect", str(scan), "-o", str(report), "--ocr", "onnxtr"]) == 0
    assert "read by OCR at 300 DPI" in report.read_text(encoding="utf-8")


def test_missing_models_are_reported_with_the_download_command(
    scan: Path, tmp_path: Path, capsys: pytest.CaptureFixture
):
    args = ["detect", str(scan), "-o", str(tmp_path / "review.json"), "--ocr", "onnxtr"]
    assert main([*args, "--resource-root", str(tmp_path / "no-models")]) == 1
    assert "download.py fetch onnxtr-parseq-multilingual-v1" in capsys.readouterr().err


def test_unknown_engine_is_an_invalid_argument(scan: Path):
    assert main(["detect", str(scan), "-o", "review.json", "--ocr", "tesseract"]) == 2


def test_review_made_without_ocr_is_refused_when_reading_with_ocr(
    scan: Path, roots: list[tuple[str, Path]], capsys: pytest.CaptureFixture
):
    """Read now, the scans would pass as redacted although nothing on them was detected."""
    session, output = scan.with_name("review.json"), scan.with_name("out.pdf")
    # Saved by the core: `detect` refuses a document it can read nothing of.
    save_session(load_document(scan), session)
    redact = ["redact", str(scan), "-o", str(output), "--session", str(session), "--ocr", "onnxtr"]
    assert main(redact) == 1
    assert "made without OCR" in capsys.readouterr().err
    assert not output.exists()


def test_models_are_read_from_the_folder_chosen_in_the_window(
    scan: Path, roots: list[tuple[str, Path]], tmp_path: Path
):
    choose_resource_root(tmp_path / "chosen")
    assert main(["inspect", str(scan), "--ocr", "onnxtr", "--out", str(tmp_path / "r.html")]) == 0
    assert roots == [("onnxtr", (tmp_path / "chosen").resolve())]
