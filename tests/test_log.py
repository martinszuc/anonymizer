"""Tests for the logging module: levels, format, and what an exception record leaves out."""

import io
import logging
from pathlib import Path

import pytest
from anonymizer.core.log import (
    LEVEL_VARIABLE,
    MAX_TEXT,
    configure_logging,
    counts,
    fields,
    resolve_level,
    short_fingerprint,
    step,
)

log = logging.getLogger("anonymizer.core.test_subject")

# Built in two parts, so that the source line a traceback shows does not contain it.
SECRET = "CANARY-" + "secret-text"


def configured(level: int) -> io.StringIO:
    stream = io.StringIO()
    configure_logging(level, stream=stream)
    return stream


class TestResolveLevel:
    def test_defaults_to_warning(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv(LEVEL_VARIABLE, raising=False)
        assert resolve_level() == logging.WARNING

    def test_debug_flag_means_debug(self):
        assert resolve_level(debug=True) == logging.DEBUG

    def test_a_named_level_wins_over_the_flag(self):
        assert resolve_level("error", debug=True) == logging.ERROR

    def test_environment_sets_the_level_when_nothing_else_does(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv(LEVEL_VARIABLE, " Info ")
        assert resolve_level() == logging.INFO

    def test_the_flag_wins_over_the_environment(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv(LEVEL_VARIABLE, "error")
        assert resolve_level(debug=True) == logging.DEBUG

    def test_unknown_level_is_refused(self):
        with pytest.raises(ValueError, match="unknown log level 'loud'"):
            resolve_level("loud")


class TestConfigure:
    def test_keeps_records_at_or_above_the_level(self):
        stream = configured(logging.INFO)
        log.debug("hidden")
        log.info("shown")
        log.warning("also shown")
        assert "hidden" not in stream.getvalue()
        assert "shown" in stream.getvalue()
        assert "also shown" in stream.getvalue()

    def test_a_line_has_time_level_short_logger_and_message(self):
        stream = configured(logging.INFO)
        log.info("opened")
        assert stream.getvalue().rstrip().endswith("INFO    [core.test_subject] opened")

    def test_thread_name_appears_only_in_a_debug_log(self):
        info = configured(logging.INFO)
        log.info("x")
        debug = configured(logging.DEBUG)
        log.info("y")
        assert "MainThread" not in info.getvalue()
        assert "MainThread" in debug.getvalue()

    def test_debug_says_that_the_log_holds_document_text(self):
        stream = configured(logging.DEBUG)
        assert "contains text from the documents" in stream.getvalue()
        assert "WARNING" in stream.getvalue()

    def test_other_levels_do_not_say_it(self):
        assert configured(logging.INFO).getvalue() == ""

    def test_configuring_again_replaces_the_handlers(self):
        first = configured(logging.INFO)
        second = configured(logging.INFO)
        log.info("once")
        assert first.getvalue() == ""
        assert second.getvalue().count("once") == 1

    def test_no_file_is_written_unless_one_is_named(self, tmp_path: Path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        configured(logging.DEBUG)
        log.debug("something")
        assert list(tmp_path.iterdir()) == []

    def test_a_named_file_receives_the_records_as_utf8(self, tmp_path: Path):
        target = tmp_path / "run.log"
        configure_logging(logging.INFO, file=target, stream=io.StringIO())
        log.info("Novák žije v Brně")
        assert "Novák žije v Brně" in target.read_text(encoding="utf-8")

    def test_records_do_not_reach_the_root_logger(self, caplog: pytest.LogCaptureFixture):
        configured(logging.INFO)
        log.info("private to the project")
        assert "private to the project" not in caplog.text

    def test_library_loggers_are_left_alone(self):
        configured(logging.DEBUG)
        assert logging.getLogger("transformers").level == logging.NOTSET


class TestExceptions:
    def test_the_type_and_frames_are_written_but_not_the_message(self):
        stream = configured(logging.ERROR)
        try:
            raise ValueError(SECRET)
        except ValueError:
            log.exception("operation failed")
        written = stream.getvalue()
        assert "operation failed" in written
        assert "ValueError" in written
        assert "test_the_type_and_frames_are_written_but_not_the_message" in written
        assert SECRET not in written

    def test_a_file_gets_the_same_treatment(self, tmp_path: Path):
        target = tmp_path / "run.log"
        configure_logging(logging.ERROR, file=target, stream=io.StringIO())
        try:
            raise KeyError(SECRET)
        except KeyError:
            log.exception("operation failed")
        assert SECRET not in target.read_text(encoding="utf-8")


class TestFields:
    def test_plain_values_are_bare(self):
        assert fields(pages=3, language="cs", took="0.31s") == " pages=3 language=cs took=0.31s"

    def test_accented_letters_are_plain(self):
        assert fields(text="Novák") == " text=Novák"

    def test_text_with_spaces_or_quotes_is_quoted(self):
        assert fields(text='Jan "Honza" Novák') == ' text="Jan \\"Honza\\" Novák"'

    def test_a_line_break_cannot_start_a_new_record(self):
        rendered = fields(text="first\nsecond\tthird")
        assert "\n" not in rendered
        assert "\\n" in rendered

    def test_long_text_is_cut(self):
        rendered = fields(text="x" * 500)
        assert rendered == ' text="' + "x" * MAX_TEXT + '…"'

    def test_nothing_gives_nothing(self):
        assert fields() == ""

    def test_none_and_empty_text_are_distinguishable(self):
        assert fields(a=None, b="") == ' a=None b=""'


class TestStep:
    def test_writes_start_and_done_with_the_results_and_time(self):
        stream = configured(logging.DEBUG)
        with step(log, "detect", pages=2) as outcome:
            outcome["found"] = 5
        lines = stream.getvalue().splitlines()
        assert lines[-2].endswith("detect: start pages=2")
        assert "detect: done pages=2 found=5 elapsed=" in lines[-1]

    def test_done_can_be_an_info_record(self):
        stream = configured(logging.INFO)
        with step(log, "load", done_level=logging.INFO):
            pass
        assert "load: done" in stream.getvalue()
        assert "load: start" not in stream.getvalue()

    def test_a_failure_is_recorded_with_its_type_and_propagates(self):
        stream = configured(logging.DEBUG)
        with pytest.raises(ValueError, match="boom"), step(log, "detect"):
            msg = "boom"
            raise ValueError(msg)
        assert "detect: failed elapsed=" in stream.getvalue()
        assert "error=ValueError" in stream.getvalue()
        assert "boom" not in stream.getvalue()
        assert "detect: done" not in stream.getvalue()


def test_fingerprints_are_cut_to_a_prefix():
    assert short_fingerprint("0123456789abcdef") == "01234567"


@pytest.mark.parametrize("value", [None, "", 12])
def test_a_missing_or_damaged_fingerprint_is_a_dash(value: object):
    assert short_fingerprint(value) == "-"


def test_counts_lists_the_most_frequent_first():
    assert counts({"email": 1, "phone": 3, "address": 1}) == "phone:3,address:1,email:1"
    assert counts({}) == "-"
