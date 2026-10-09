"""Tests for the `anonymize` command line, run through `main`."""

import json
from pathlib import Path

import pytest
from anonymizer.cli import commands
from anonymizer.cli.main import main
from anonymizer.core.detect import GlinerDetector
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import Leak, LeakLayer

from tests.detect.test_gliner import StandInModel
from tests.pdf_builders import CONTACT_EMAIL, ENGLISH_LETTER, write_pdf

PHONE = "+420 603 123 456"
LINES = ["Jan Novak", f"e-mail {CONTACT_EMAIL}", f"tel. {PHONE}", "KEEP this line"]


def text_of(path: Path) -> str:
    return "\n".join(page.text for page in load_document(path).pages)


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "cv.pdf", [LINES])


class TestDetect:
    def test_writes_a_session_and_summarizes(self, pdf: Path, capsys: pytest.CaptureFixture):
        session = pdf.with_name("review.json")
        assert main(["detect", str(pdf), "-o", str(session), "--lang", "cs"]) == 0
        entities = json.loads(session.read_text(encoding="utf-8"))["entities"]
        assert {entity["type"] for entity in entities} == {"email", "phone"}
        out = capsys.readouterr().out
        assert "1 page, 2 entities" in out
        assert "wrote review" in out

    def test_auto_records_the_recognised_language(self, tmp_path: Path):
        letter = write_pdf(tmp_path / "letter.pdf", [ENGLISH_LETTER])
        session = tmp_path / "review.json"
        assert main(["detect", str(letter), "-o", str(session), "--lang", "auto"]) == 0
        saved = json.loads(session.read_text(encoding="utf-8"))
        assert saved["language"] == "en"
        assert saved["entities"] == []  # 777 123 456 is a phone number only in Czech

    def test_show_lists_every_item(self, pdf: Path, capsys: pytest.CaptureFixture):
        session = pdf.with_name("review.json")
        main(["detect", str(pdf), "-o", str(session), "--show"])
        out = capsys.readouterr().out
        assert CONTACT_EMAIL in out
        assert PHONE in out


class TestNer:
    def test_missing_model_is_reported_before_anything_is_written(
        self, pdf: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        session = pdf.with_name("review.json")
        empty_root = tmp_path / "no-models"
        args = ["detect", str(pdf), "-o", str(session), "--ner", "--resource-root", str(empty_root)]
        assert main(args) == 1
        assert "download.py fetch gliner-multi-v2.1" in capsys.readouterr().err
        assert not session.exists()

    def test_names_from_the_model_are_redacted(
        self, pdf: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ):
        detector = GlinerDetector(StandInModel({"Jan Novak": "person"}))
        loads: list[tuple[str, Path]] = []

        def load(model_id: str, root: Path) -> GlinerDetector:
            loads.append((model_id, root))
            return detector

        monkeypatch.setattr(commands, "load_name_model", load)
        output = pdf.with_name("out.pdf")
        args = ["redact", str(pdf), "-o", str(output), "--lang", "cs", "--ner"]
        assert main([*args, "--resource-root", str(pdf.parent)]) == 0
        assert loads == [("gliner-multi-v2.1", pdf.parent)]
        assert "Jan Novak" not in text_of(output)
        assert "KEEP this line" in text_of(output)

    def test_name_model_chooses_the_model_and_implies_ner(
        self, pdf: Path, monkeypatch: pytest.MonkeyPatch
    ):
        loads: list[str] = []

        def load(model_id: str, root: Path) -> GlinerDetector:
            loads.append(model_id)
            return GlinerDetector(StandInModel({"Jan Novak": "person"}), name=model_id)

        monkeypatch.setattr(commands, "load_name_model", load)
        session = pdf.with_name("review.json")
        args = ["detect", str(pdf), "-o", str(session), "--name-model", "gliner-multi-v2.1"]
        assert main(args) == 0
        assert loads == ["gliner-multi-v2.1"]
        content = json.loads(session.read_text(encoding="utf-8"))
        assert "person" in {entity["type"] for entity in content["entities"]}

    def test_an_unknown_name_model_is_an_invalid_argument(
        self, pdf: Path, capsys: pytest.CaptureFixture
    ):
        args = ["detect", str(pdf), "-o", str(pdf.with_name("r.json")), "--name-model", "x"]
        assert main(args) == 2
        assert "invalid choice: 'x'" in capsys.readouterr().err

    def test_a_reviewed_session_does_not_load_the_model(
        self, pdf: Path, monkeypatch: pytest.MonkeyPatch
    ):
        session = pdf.with_name("review.json")
        assert main(["detect", str(pdf), "-o", str(session)]) == 0

        def fail(model_id: str, root: Path) -> GlinerDetector:
            raise AssertionError

        monkeypatch.setattr(commands, "load_name_model", fail)
        output = pdf.with_name("out.pdf")
        args = ["redact", str(pdf), "-o", str(output), "--session", str(session), "--ner"]
        assert main(args) == 0


class TestRedact:
    def test_one_step_redaction_writes_a_checked_copy(
        self, pdf: Path, capsys: pytest.CaptureFixture
    ):
        output = pdf.with_name("out.pdf")
        assert main(["redact", str(pdf), "-o", str(output), "--lang", "cs"]) == 0
        assert CONTACT_EMAIL not in text_of(output)
        assert "KEEP this line" in text_of(output)
        assert "leak check passed" in capsys.readouterr().out

    def test_reviewed_session_decides_what_is_kept(self, pdf: Path):
        session = pdf.with_name("review.json")
        main(["detect", str(pdf), "-o", str(session)])
        content = json.loads(session.read_text(encoding="utf-8"))
        for entity in content["entities"]:
            if entity["type"] == "email":
                entity["review"] = "rejected"
        session.write_text(json.dumps(content), encoding="utf-8")

        output = pdf.with_name("out.pdf")
        assert main(["redact", str(pdf), "-o", str(output), "--session", str(session)]) == 0
        text = text_of(output)
        assert CONTACT_EMAIL in text
        assert "603" not in text

    def test_region_added_by_hand_is_redacted(self, pdf: Path):
        session = pdf.with_name("review.json")
        main(["detect", str(pdf), "-o", str(session)])
        content = json.loads(session.read_text(encoding="utf-8"))
        name = next(w for w in load_document(pdf).pages[0].words if w.text == "Novak").bbox
        content["entities"].append(
            {
                "type": "region",
                "page_index": 0,
                "bboxes": [[name.x0 - 1, name.y0 - 1, name.x1 + 1, name.y1 + 1]],
                "source": "manual",
            }
        )
        session.write_text(json.dumps(content), encoding="utf-8")
        output = pdf.with_name("out.pdf")
        assert main(["redact", str(pdf), "-o", str(output), "--session", str(session)]) == 0
        assert "Novak" not in text_of(output)

    def test_existing_output_needs_force(self, pdf: Path, capsys: pytest.CaptureFixture):
        output = pdf.with_name("out.pdf")
        output.write_bytes(b"old")
        assert main(["redact", str(pdf), "-o", str(output)]) == 1
        assert "already exists" in capsys.readouterr().err
        assert output.read_bytes() == b"old"
        assert main(["redact", str(pdf), "-o", str(output), "--force"]) == 0

    def test_output_may_not_be_the_input(self, pdf: Path, capsys: pytest.CaptureFixture):
        before = pdf.read_bytes()
        assert main(["redact", str(pdf), "-o", str(pdf), "--force"]) == 1
        assert "must not overwrite the input" in capsys.readouterr().err
        assert pdf.read_bytes() == before

    def test_session_for_another_pdf_is_refused(
        self, pdf: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        session = pdf.with_name("review.json")
        main(["detect", str(pdf), "-o", str(session)])
        other = write_pdf(tmp_path / "other.pdf", [["other", "text"]])
        output = tmp_path / "out.pdf"
        assert main(["redact", str(other), "-o", str(output), "--session", str(session)]) == 1
        assert "different file" in capsys.readouterr().err
        assert not output.exists()

    def test_pages_without_text_stop_the_run_unless_allowed(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        pdf = write_pdf(tmp_path / "mixed.pdf", [LINES, []])
        output = tmp_path / "out.pdf"
        assert main(["redact", str(pdf), "-o", str(output)]) == 1
        err = capsys.readouterr().err
        assert "page 2 is a scan OCR has not read" in err
        assert "--ocr onnxtr" in err
        assert not output.exists()
        assert main(["redact", str(pdf), "-o", str(output), "--allow-pages-without-text"]) == 0
        assert "page 2 is a scan OCR has not read and is NOT redacted" in capsys.readouterr().err

    def test_failed_leak_check_reports_and_exits_with_three(
        self, pdf: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ):
        # Writing nothing on a leak is export_redacted's job, tested in core.
        leak = Leak(LeakLayer.PAGE_TEXT, "page 0", CONTACT_EMAIL, "e1")
        monkeypatch.setattr(commands, "export_redacted", lambda *_, **__: [leak])
        output = pdf.with_name("out.pdf")
        assert main(["redact", str(pdf), "-o", str(output)]) == 3
        err = capsys.readouterr().err
        assert "leak check FAILED: 1 leak" in err
        assert f"nothing written to {output}" in err


class TestCheck:
    def test_clean_output_passes_and_the_original_fails(
        self, pdf: Path, capsys: pytest.CaptureFixture
    ):
        session = pdf.with_name("review.json")
        output = pdf.with_name("out.pdf")
        main(["detect", str(pdf), "-o", str(session)])
        main(["redact", str(pdf), "-o", str(output), "--session", str(session)])
        capsys.readouterr()
        assert main(["check", str(output), "--source", str(pdf), "--session", str(session)]) == 0
        assert main(["check", str(pdf), "--source", str(pdf), "--session", str(session)]) == 3
        assert "leak check FAILED" in capsys.readouterr().err


class TestErrors:
    def test_missing_input_is_reported_without_a_traceback(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        missing = tmp_path / "absent.pdf"
        assert main(["redact", str(missing), "-o", str(tmp_path / "out.pdf")]) == 1
        assert "no such file" in capsys.readouterr().err

    def test_invalid_arguments_exit_with_two(self):
        assert main(["redact"]) == 2
