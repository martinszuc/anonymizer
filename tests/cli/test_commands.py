"""Tests for the `anonymize` command line, run through `main`."""

import json
from pathlib import Path

import pytest
from anonymizer.cli import commands
from anonymizer.cli.main import main
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import Leak, LeakLayer

from tests.pdf_builders import CONTACT_EMAIL, write_pdf

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

    def test_show_lists_every_item(self, pdf: Path, capsys: pytest.CaptureFixture):
        session = pdf.with_name("review.json")
        main(["detect", str(pdf), "-o", str(session), "--show"])
        out = capsys.readouterr().out
        assert CONTACT_EMAIL in out
        assert PHONE in out


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
        assert "different PDF" in capsys.readouterr().err
        assert not output.exists()

    def test_pages_without_text_stop_the_run_unless_allowed(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        pdf = write_pdf(tmp_path / "mixed.pdf", [LINES, []])
        output = tmp_path / "out.pdf"
        assert main(["redact", str(pdf), "-o", str(output)]) == 1
        assert "page 2 has no text layer" in capsys.readouterr().err
        assert not output.exists()
        assert main(["redact", str(pdf), "-o", str(output), "--allow-pages-without-text"]) == 0
        assert "page 2 has no text layer and is NOT redacted" in capsys.readouterr().err

    def test_failed_leak_check_writes_nothing(
        self, pdf: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ):
        leak = Leak(LeakLayer.PAGE_TEXT, "page 0", CONTACT_EMAIL, "e1")
        monkeypatch.setattr(commands, "find_leaks", lambda *_: [leak])
        output = pdf.with_name("out.pdf")
        assert main(["redact", str(pdf), "-o", str(output)]) == 3
        assert "leak check FAILED: 1 leak" in capsys.readouterr().err
        assert list(pdf.parent.glob("*out.pdf*")) == []

    def test_temporary_copy_is_removed_when_redaction_fails(
        self, pdf: Path, monkeypatch: pytest.MonkeyPatch
    ):
        def broken_check(*_: object) -> list[Leak]:
            raise RuntimeError("check crashed")

        monkeypatch.setattr(commands, "find_leaks", broken_check)
        with pytest.raises(RuntimeError, match="check crashed"):
            main(["redact", str(pdf), "-o", str(pdf.with_name("out.pdf"))])
        assert list(pdf.parent.glob("*out.pdf*")) == []


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
