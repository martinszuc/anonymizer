"""Tests for the window shell, with pywebview replaced by stand-ins."""

import inspect
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
import webview
from anonymizer.ui import app
from anonymizer.ui.api import ReviewApi, ReviewError
from anonymizer.ui.app import WindowApi, main

from tests.pdf_builders import write_pdf
from tests.ui.test_api import LINES

BRIDGE = Path(__file__).parents[2] / "packages/ui/frontend/src/bridge.ts"


@dataclass
class StandInWindow:
    """Answers file dialogs from a queue and records what was asked."""

    answers: list[Any] = field(default_factory=list)
    asked: list[dict[str, Any]] = field(default_factory=list)
    title: str = ""

    def create_file_dialog(self, dialog: int, **options: Any) -> Any:
        self.asked.append({"dialog": dialog, **options})
        return self.answers.pop(0)


@dataclass
class StandInWebview:
    """Records the window pywebview would have created and started."""

    created: dict[str, Any] = field(default_factory=dict)
    started: dict[str, Any] | None = None
    window: StandInWindow = field(default_factory=StandInWindow)

    def create_window(self, title: str, **options: Any) -> StandInWindow:
        self.created = {"title": title, **options}
        return self.window

    def start(self, **options: Any) -> None:
        self.started = options


@pytest.fixture
def stand_in(monkeypatch: pytest.MonkeyPatch) -> StandInWebview:
    fake = StandInWebview()
    monkeypatch.setattr(webview, "create_window", fake.create_window)
    monkeypatch.setattr(webview, "start", fake.start)
    return fake


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "cv.pdf", [LINES])


def attached(window: StandInWindow) -> WindowApi:
    api = WindowApi(ReviewApi())
    api._attach(window)  # type: ignore[arg-type]
    return api


def bridge_methods() -> set[str]:
    """Method names of the `ReviewBridge` interface the frontend calls."""
    source = BRIDGE.read_text(encoding="utf-8")
    interface = source[source.index("interface ReviewBridge") :]
    body = interface[: interface.index("}")]
    return set(re.findall(r"^\s+(\w+)\(", body, re.MULTILINE))


class TestExposedCalls:
    def test_the_page_can_call_exactly_the_bridge_methods(self):
        # pywebview exposes every public attribute, so this set is the page's reach.
        exposed = {name for name in dir(WindowApi(ReviewApi())) if not name.startswith("_")}
        assert exposed == bridge_methods()

    def test_no_exposed_call_takes_a_file_path(self):
        for name in bridge_methods():
            parameters = inspect.signature(getattr(WindowApi, name)).parameters
            assert not {"path", "pdf_path", "session_path"} & set(parameters), name


class TestMain:
    def test_opens_an_empty_window(self, stand_in: StandInWebview):
        assert main([]) == 0
        assert stand_in.created["title"] == "Anonymizer"
        assert isinstance(stand_in.created["js_api"], WindowApi)
        assert stand_in.created["js_api"].current_document() is None
        assert stand_in.started == {"debug": False, "private_mode": True}

    def test_opens_the_given_pdf(self, stand_in: StandInWebview, pdf: Path):
        assert main([str(pdf), "--lang", "cs"]) == 0
        assert stand_in.created["title"] == "cv.pdf — Anonymizer"
        document = stand_in.created["js_api"].current_document()
        assert document["language"] == "cs"

    def test_reports_a_pdf_it_cannot_open(
        self, stand_in: StandInWebview, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        assert main([str(tmp_path / "absent.pdf")]) == 1
        assert "no such file: absent.pdf" in capsys.readouterr().err
        assert stand_in.started is None

    def test_loads_the_dev_server(self, stand_in: StandInWebview):
        main(["--dev-server", "http://localhost:5173", "--debug"])
        assert stand_in.created["url"] == "http://localhost:5173"
        assert stand_in.started == {"debug": True, "private_mode": True}

    def test_loads_the_built_frontend(
        self, stand_in: StandInWebview, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        index = tmp_path / "index.html"
        index.write_text("<!doctype html>", encoding="utf-8")
        monkeypatch.setattr(app, "STATIC_INDEX", index)
        main([])
        assert stand_in.created["url"] == str(index)

    def test_explains_a_missing_build(
        self, stand_in: StandInWebview, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        monkeypatch.setattr(app, "STATIC_INDEX", tmp_path / "absent.html")
        main([])
        assert "has not been built" in stand_in.created["html"]
        assert stand_in.created["url"] is None


class TestDialogs:
    def test_choose_pdf_opens_it_and_titles_the_window(self, pdf: Path):
        window = StandInWindow(answers=[(str(pdf),)])
        payload = attached(window).choose_pdf("cs")
        assert payload is not None
        assert payload["name"] == "cv.pdf"
        assert window.title == "cv.pdf — Anonymizer"
        assert window.asked[0]["dialog"] == webview.FileDialog.OPEN

    def test_cancelled_dialogs_change_nothing(self, pdf: Path):
        api = attached(StandInWindow(answers=[None, None]))
        assert api.choose_pdf() is None
        assert api.choose_session() is None
        assert api.current_document() is None

    def test_save_then_reopen_a_session(self, pdf: Path):
        session = pdf.with_name("review.json")
        window = StandInWindow(answers=[(str(pdf),), str(session)])
        api = attached(window)
        api.choose_pdf("cs")
        assert api.save_session_as() is True
        assert window.asked[1]["dialog"] == webview.FileDialog.SAVE
        assert window.asked[1]["save_filename"] == "cv-review.json"

        reopening = attached(StandInWindow(answers=[(str(session),), (str(pdf),)]))
        reopened = reopening.choose_session()
        assert reopened is not None
        assert reopened["name"] == "cv.pdf"

    def test_session_needs_its_pdf(self, pdf: Path):
        api = attached(StandInWindow(answers=[(str(pdf.with_name("review.json")),), None]))
        assert api.choose_session() is None

    def test_cancelled_save_writes_nothing(self, pdf: Path):
        api = attached(StandInWindow(answers=[(str(pdf),), ()]))
        api.choose_pdf()
        assert api.save_session_as() is False
        assert not list(pdf.parent.glob("*.json"))

    def test_dialogs_need_the_window(self):
        with pytest.raises(ReviewError, match="window is not ready"):
            WindowApi(ReviewApi()).choose_pdf()


class TestExportDialog:
    def test_exports_where_the_reviewer_chose(self, pdf: Path):
        destination = pdf.with_name("chosen.pdf")
        window = StandInWindow(answers=[(str(pdf),), str(destination)])
        api = attached(window)
        api.choose_pdf("cs")
        result = api.export_as()
        assert result is not None
        assert result["written"] is True
        assert destination.exists()
        assert window.asked[1]["dialog"] == webview.FileDialog.SAVE
        assert window.asked[1]["save_filename"] == "cv-redacted.pdf"

    def test_cancelled_export_writes_nothing(self, pdf: Path):
        api = attached(StandInWindow(answers=[(str(pdf),), None]))
        api.choose_pdf("cs")
        assert api.export_as() is None
        assert sorted(path.name for path in pdf.parent.iterdir()) == ["cv.pdf"]

    def test_passes_consent_for_pages_without_text(self, tmp_path: Path):
        mixed = write_pdf(tmp_path / "mixed.pdf", [LINES, []])
        destination = tmp_path / "out.pdf"
        api = attached(StandInWindow(answers=[(str(mixed),), str(destination)]))
        api.choose_pdf("cs")
        result = api.export_as(True)
        assert result is not None
        assert result["pages_without_text"] == [2]
