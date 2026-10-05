"""The command line on a photo of a document: detect, redact, check and inspect.

The photo is a phone's (`tests.image_builders.phone_photo`), with metadata
planted in it. The engine is the ink-reading stand-in, put in place of the
real loader as in `test_ocr`.
"""

from pathlib import Path

import pytest
from anonymizer.cli import main as main_module
from anonymizer.cli.main import build_parser, main
from anonymizer.core.ingest import OcrEngine, load_document

from tests.image_builders import PLANTED, every_byte, phone_photo
from tests.ocr_stand_in import InkReadingEngine
from tests.pdf_builders import CONTACT_EMAIL, write_pdf

PHONE = "+420 603 123 456"
LINES = [f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "Poznamka: nic osobniho"]
OCR = ["--ocr", "onnxtr", "--lang", "cs"]


@pytest.fixture
def photo(tmp_path: Path) -> Path:
    path = tmp_path / "photo.jpg"
    path.write_bytes(phone_photo(LINES))
    return path


@pytest.fixture(autouse=True)
def stand_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = load_document(write_pdf(tmp_path / "original.pdf", [LINES]))

    def load(name: str, root: Path) -> OcrEngine:
        del name, root
        return InkReadingEngine.reading(original)

    monkeypatch.setattr(main_module, "load_ocr_engine", load)


@pytest.mark.parametrize("command", ["detect", "redact", "inspect"])
def test_without_ocr_an_image_is_refused(command: str, photo: Path, capsys: pytest.CaptureFixture):
    output = photo.with_name("out")
    assert main([command, str(photo), "-o", str(output)]) == 1
    error = capsys.readouterr().err
    assert "page 1 is a scan OCR has not read" in error
    assert "--ocr onnxtr" in error
    assert not output.exists()


def test_redact_writes_a_checked_pdf_without_the_photo_metadata(
    photo: Path, capsys: pytest.CaptureFixture
):
    output = photo.with_name("photo-redacted.pdf")
    assert main(["redact", str(photo), "-o", str(output), *OCR]) == 0
    assert "leak check passed" in capsys.readouterr().out
    written = every_byte(output.read_bytes())
    assert written.startswith(b"%PDF-")
    for value in (*PLANTED, CONTACT_EMAIL, PHONE):
        assert value.encode() not in written, value


def test_a_review_of_the_photo_redacts_and_checks(photo: Path, capsys: pytest.CaptureFixture):
    session, output = photo.with_name("review.json"), photo.with_name("out.pdf")
    assert main(["detect", str(photo), "-o", str(session), *OCR]) == 0
    assert "1 page, 2 entities" in capsys.readouterr().out
    redact = ["redact", str(photo), "-o", str(output), "--session", str(session), *OCR]
    assert main(redact) == 0
    check = ["check", str(output), "--source", str(photo), "--session", str(session)]
    assert main([*check, "--ocr", "onnxtr"]) == 0
    assert "leak check passed" in capsys.readouterr().out


def test_inspect_shows_the_photo_upright_and_read_by_ocr(photo: Path):
    report = photo.with_name("report.html")
    assert main(["inspect", str(photo), "-o", str(report), *OCR]) == 0
    html = report.read_text(encoding="utf-8")
    assert "read by OCR at 300 DPI" in html
    # A4 portrait: the photo was stored sideways and turned by its EXIF orientation.
    assert 'viewBox="0 0 595' in html


def test_a_review_refuses_another_photo(photo: Path, tmp_path: Path, capsys: pytest.CaptureFixture):
    session = photo.with_name("review.json")
    assert main(["detect", str(photo), "-o", str(session), *OCR]) == 0
    other = tmp_path / "other.jpg"
    other.write_bytes(phone_photo([*LINES, "jiny dokument"]))
    output = tmp_path / "out.pdf"
    assert main(["redact", str(other), "-o", str(output), "--session", str(session), *OCR]) == 1
    assert "different file" in capsys.readouterr().err


def test_an_unsupported_file_is_reported_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture
):
    photo = tmp_path / "photo.heic"
    photo.write_bytes(b"\x00\x00\x00\x18ftypheic" + bytes(32))
    assert main(["detect", str(photo), "-o", str(tmp_path / "review.json")]) == 1
    error = capsys.readouterr().err
    assert "unsupported file type" in error
    assert "Traceback" not in error


def test_help_names_images():
    help_text = build_parser().format_help()
    assert "PDF documents and images" in help_text
