"""The command line's logging options: where records go and what is written."""

from pathlib import Path

import pytest
from anonymizer.cli.main import main

from tests.pdf_builders import CONTACT_EMAIL, write_pdf


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "cv.pdf", [[f"e-mail {CONTACT_EMAIL}", "KEEP this line"]])


def detect(pdf: Path, *options: str) -> int:
    return main(
        ["detect", str(pdf), "-o", str(pdf.with_name("review.json")), "--lang", "cs", *options]
    )


def files_in(folder: Path) -> set[str]:
    return {path.name for path in folder.iterdir()}


class TestLogOptions:
    def test_nothing_is_logged_by_default(self, pdf: Path, capsys: pytest.CaptureFixture):
        assert detect(pdf) == 0
        assert capsys.readouterr().err == ""

    def test_debug_logs_every_step_and_detection_to_stderr(
        self, pdf: Path, capsys: pytest.CaptureFixture
    ):
        assert detect(pdf, "--debug") == 0
        captured = capsys.readouterr()
        assert "find_emails matched type=email" in captured.err
        assert "detection: done" in captured.err
        assert "DEBUG" not in captured.out

    def test_debug_alone_writes_no_file(self, pdf: Path, tmp_path: Path):
        before = files_in(tmp_path)
        assert detect(pdf, "--debug") == 0
        assert files_in(tmp_path) == before | {"review.json"}

    def test_log_file_receives_the_log_and_is_the_only_new_file(self, pdf: Path, tmp_path: Path):
        target = tmp_path / "run.log"
        assert detect(pdf, "--log-level", "info", "--log-file", str(target)) == 0
        assert "detection: done" in target.read_text(encoding="utf-8")
        assert files_in(tmp_path) == {"cv.pdf", "review.json", "run.log"}

    def test_info_level_has_milestones_without_document_text(
        self, pdf: Path, capsys: pytest.CaptureFixture
    ):
        assert detect(pdf, "--log-level", "info") == 0
        err = capsys.readouterr().err
        assert "read document: done" in err
        assert CONTACT_EMAIL not in err
        assert "matched" not in err

    def test_level_comes_from_the_environment(
        self, pdf: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("ANONYMIZER_LOG_LEVEL", "info")
        assert detect(pdf) == 0
        assert "read document: done" in capsys.readouterr().err

    def test_an_unknown_level_is_an_invalid_argument(self, pdf: Path):
        assert detect(pdf, "--log-level", "loud") == 2

    def test_a_bad_environment_level_is_reported_without_a_traceback(
        self, pdf: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("ANONYMIZER_LOG_LEVEL", "loud")
        assert detect(pdf) == 1
        assert "unknown log level" in capsys.readouterr().err
