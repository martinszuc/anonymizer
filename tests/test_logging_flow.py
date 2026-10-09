"""What a run logs: which rule or model found which word, and what a log must never hold."""

import io
import logging
from pathlib import Path

import pytest
from anonymizer.core.detect import GlinerDetector
from anonymizer.core.ingest import load_document
from anonymizer.core.log import configure_logging
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import Leak, LeakLayer, export_redacted
from anonymizer.core.redact.leakage import _layer
from anonymizer.core.session import save_session
from anonymizer.ui.api import ReviewApi

from tests.detect.test_gliner import StandInModel
from tests.pdf_builders import CONTACT_EMAIL, write_pdf
from tests.ui.test_api import NameModel

PHONE = "+420 603 123 456"
NAME = "Jan Novak"
LINES = [
    NAME,
    f"e-mail {CONTACT_EMAIL}",
    f"tel. {PHONE}",
    f"again {CONTACT_EMAIL}",
    "KEEP this line",
]
# A file name can be personal data too, so it must never appear in any record.
FILE_STEM = "CANARYFILENAME"


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / f"{FILE_STEM}.pdf", [LINES])


def run_with_log(level: int, pdf: Path, tmp_path: Path) -> str:
    """Open, review, save and export a PDF through the window's API and return the log."""
    stream = io.StringIO()
    configure_logging(level, stream=stream)
    model = GlinerDetector(StandInModel({NAME: "person"}))
    api = ReviewApi()
    api._models["gliner-multi-v2.1"] = model
    opened = api.open_pdf(str(pdf), "cs", True, "gliner-multi-v2.1")
    first = opened["entities"][0]["id"]
    api.set_review(first, "rejected")
    api.add_region(0, 10, 10, 50, 50)
    api.save_session(str(tmp_path / "review.json"))
    api.export(str(tmp_path / "out.pdf"))
    api.close()
    return stream.getvalue()


class TestDebugLogFollowsEachDetection:
    @pytest.fixture
    def log(self, pdf: Path, tmp_path: Path) -> str:
        return run_with_log(logging.DEBUG, pdf, tmp_path)

    def test_a_rule_match_names_the_function_the_word_and_where(self, log: str):
        line = next(line for line in log.splitlines() if "find_emails matched" in line)
        assert "type=email" in line
        assert "page=0" in line
        assert "source=rule" in line
        assert f"text={CONTACT_EMAIL}" in line

    def test_a_model_prediction_names_the_model_label_and_score(self, log: str):
        line = next(line for line in log.splitlines() if "gliner-multi-v2.1 predicted" in line)
        assert "type=person" in line
        assert "label=person" in line
        assert "score=0.90" in line
        assert f'text="{NAME}"' in line

    def test_a_propagated_occurrence_says_so(self, tmp_path: Path):
        # The stand-in model marks only the first name, so the second is propagated.
        stream = io.StringIO()
        configure_logging(logging.DEBUG, stream=stream)
        document = load_document(write_pdf(tmp_path / "twice.pdf", [[NAME, f"signed {NAME}"]]))
        run_detection(document, build_detector("cs", model=NameModel()))
        line = next(line for line in stream.getvalue().splitlines() if "propagated further" in line)
        assert "source=propagated" in line
        assert f'text="{NAME}"' in line

    def test_the_detectors_counts_per_page_are_listed(self, log: str):
        assert "rules:cs+gliner-multi-v2.1: page 0:" in log
        assert "rules:cs=" in log

    def test_every_step_has_a_start_and_an_end(self, log: str):
        for name in ("read document", "detection", "redact", "leak check", "export"):
            assert f"{name}: start" in log
            assert f"{name}: done" in log

    def test_the_leak_check_reports_each_layer(self, log: str):
        assert "leak check layer page text: 0 leak(s)" in log
        assert "leak check layer file bytes: 0 leak(s)" in log

    def test_the_reviewers_decision_names_the_word(self, log: str):
        assert "review: rejected decided" in log

    def test_the_log_says_it_holds_document_text(self, log: str):
        assert "contains text from the documents" in log


def test_a_dropped_overlap_is_logged_with_what_it_lay_inside(tmp_path: Path):
    stream = io.StringIO()
    configure_logging(logging.DEBUG, stream=stream)
    page = ["see https://example.org/u/jan.novak@example.com now"]
    document = load_document(write_pdf(tmp_path / "overlap.pdf", [page]))
    run_detection(document, build_detector("cs"))
    dropped = [line for line in stream.getvalue().splitlines() if "merge: dropped" in line]
    assert any("type=email" in line and "inside type=url" in line for line in dropped)


def test_a_rule_built_by_a_factory_is_logged_under_its_own_name(tmp_path: Path):
    stream = io.StringIO()
    configure_logging(logging.DEBUG, stream=stream)
    document = load_document(write_pdf(tmp_path / "born.pdf", [["narozen 12. 3. 1985"]]))
    run_detection(document, build_detector("cs"))
    assert "find_czech_slovak_birth_dates matched type=date" in stream.getvalue()


@pytest.mark.parametrize("layer", [LeakLayer.FILE_BYTES, LeakLayer.SURFACE])
def test_a_leak_found_by_name_or_locator_is_logged_without_where(layer: LeakLayer):
    # A file's name and a link's target are what these layers locate a leak by.
    stream = io.StringIO()
    configure_logging(logging.DEBUG, stream=stream)
    _layer(layer, lambda: [Leak(layer, f"{FILE_STEM}.pdf", "leaked text")])
    assert "leaked text" in stream.getvalue()
    assert FILE_STEM not in stream.getvalue()


class TestNothingPrivateBelowDebug:
    def test_an_info_log_holds_no_document_text_and_no_file_name(self, pdf: Path, tmp_path: Path):
        log = run_with_log(logging.INFO, pdf, tmp_path)
        assert "export: done" in log
        assert CONTACT_EMAIL not in log
        assert NAME not in log
        assert PHONE not in log
        assert FILE_STEM not in log

    def test_a_debug_log_never_holds_a_file_name_or_path(self, pdf: Path, tmp_path: Path):
        log = run_with_log(logging.DEBUG, pdf, tmp_path)
        assert FILE_STEM not in log
        assert str(tmp_path) not in log

    def test_the_document_is_identified_by_a_fingerprint_prefix_only(
        self, pdf: Path, tmp_path: Path
    ):
        log = run_with_log(logging.INFO, pdf, tmp_path)
        full = load_document(pdf).fingerprint
        assert full is not None
        assert f"document={full[:8]}" in log
        assert full not in log

    def test_a_failure_logs_the_exception_type_and_not_its_message(self, pdf: Path, tmp_path: Path):
        stream = io.StringIO()
        configure_logging(logging.DEBUG, stream=stream)
        document = load_document(pdf)
        run_detection(document, build_detector("cs"))
        other = write_pdf(tmp_path / "other.pdf", [["Something else"]])
        with pytest.raises(ValueError, match="different file"):
            export_redacted(other, document, tmp_path / "out.pdf")
        assert "export: failed" in stream.getvalue()
        assert "error=ValueError" in stream.getvalue()
        assert "different file" not in stream.getvalue()


class TestWarningsAndMilestones:
    def test_a_download_is_always_on_record(self):
        # The one network access the project makes; see test_fetch for the download itself.
        from anonymizer.core.resources import fetch

        assert fetch.log.name == "anonymizer.core.resources.fetch"

    def test_a_session_for_another_pdf_is_a_warning_naming_both_fingerprints(
        self, pdf: Path, tmp_path: Path
    ):
        from anonymizer.core.session import apply_session

        stream = io.StringIO()
        configure_logging(logging.WARNING, stream=stream)
        document = load_document(pdf)
        run_detection(document, build_detector("cs"))
        session = tmp_path / "review.json"
        save_session(document, session)
        other = load_document(write_pdf(tmp_path / "other.pdf", [["Something else"]]))
        with pytest.raises(ValueError, match="different file"):
            apply_session(other, session)
        assert "WARNING" in stream.getvalue()
        assert "session refused" in stream.getvalue()
        assert (other.fingerprint or "")[:8] in stream.getvalue()
