"""Tests for the window shell, with pywebview replaced by stand-ins."""

import inspect
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import webview
from anonymizer.core.ingest import load_document
from anonymizer.core.log import configure_logging
from anonymizer.core.redact import Leak, LeakLayer
from anonymizer.core.redact import export as export_module
from anonymizer.ui import api as api_module
from anonymizer.ui import app
from anonymizer.ui.api import ReviewApi, ReviewError
from anonymizer.ui.app import WindowApi, main

from tests.image_builders import encode, upright_scan
from tests.ocr_stand_in import InkReadingEngine
from tests.pdf_builders import CONTACT_EMAIL, write_pdf, write_scanned_pdf
from tests.ui.test_api import LINES, NameModel

BRIDGE = Path(__file__).parents[2] / "packages/ui/frontend/src/bridge.ts"


class StandInEvent:
    """Collects handlers added with `+=`, as a pywebview window event does."""

    def __init__(self) -> None:
        self.handlers: list[Any] = []

    def __iadd__(self, handler: Any) -> "StandInEvent":
        self.handlers.append(handler)
        return self


class StandInElement:
    """Records DOM event handlers bound with `on`."""

    def __init__(self) -> None:
        self.bound: dict[str, Any] = {}

    def on(self, event: str, handler: Any) -> None:
        self.bound[event] = handler


@dataclass
class StandInWindow:
    """Answers file dialogs from a queue and records what was asked and told."""

    answers: list[Any] = field(default_factory=list)
    asked: list[dict[str, Any]] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    title: str = ""
    events: SimpleNamespace = field(default_factory=lambda: SimpleNamespace(loaded=StandInEvent()))
    dom: SimpleNamespace = field(default_factory=lambda: SimpleNamespace(document=StandInElement()))

    def create_file_dialog(self, dialog: int, **options: Any) -> Any:
        self.asked.append({"dialog": dialog, **options})
        return self.answers.pop(0)

    def evaluate_js(self, script: str) -> None:
        self.scripts.append(script)

    def events_told(self) -> list[tuple[str, Any]]:
        """The `anonymizer:` events dispatched on the page, as (name, detail)."""
        told = []
        for script in self.scripts:
            found = re.search(r'CustomEvent\("anonymizer:([\w-]+)", \{detail: (.*)\}\)\)$', script)
            if found:
                told.append((found[1], json.loads(found[2])))
        return told


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

    def test_debug_enables_the_inspector_without_opening_it(
        self, stand_in: StandInWebview, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setitem(webview.settings, "OPEN_DEVTOOLS_IN_DEBUG", True)
        main(["--debug"])
        assert stand_in.started == {"debug": True, "private_mode": True}
        assert webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] is False

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
        payload = attached(window).choose_pdf({"language": "cs"})
        assert payload is not None
        assert payload["name"] == "cv.pdf"
        assert window.title == "cv.pdf — Anonymizer"
        assert window.asked[0]["dialog"] == webview.FileDialog.OPEN

    def test_choose_pdf_offers_images_and_export_writes_a_pdf(self, tmp_path: Path):
        photo = tmp_path / "photo.png"
        photo.write_bytes(encode(upright_scan(LINES), "PNG"))
        window = StandInWindow(answers=[(str(photo),), None])
        api = attached(window)
        payload = api.choose_pdf({"language": "cs"})
        assert payload is not None
        assert payload["name"] == "photo.png"
        offered = window.asked[0]["file_types"]
        assert offered[0] == "Documents (*.pdf;*.jpg;*.jpeg;*.png;*.tif;*.tiff)"
        assert "Images (*.jpg;*.jpeg;*.png;*.tif;*.tiff)" in offered
        api.export_as()
        assert window.asked[1]["save_filename"] == "photo-redacted.pdf"
        assert window.asked[1]["file_types"] == ("PDF documents (*.pdf)",)

    def test_cancelled_dialogs_change_nothing(self, pdf: Path):
        api = attached(StandInWindow(answers=[None, None]))
        assert api.choose_pdf() is None
        assert api.choose_session() is None
        assert api.current_document() is None

    def test_save_then_reopen_a_session(self, pdf: Path):
        session = pdf.with_name("review.json")
        window = StandInWindow(answers=[(str(pdf),), str(session)])
        api = attached(window)
        api.choose_pdf({"language": "cs"})
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

    def test_words_and_added_text_are_forwarded(self, pdf: Path):
        api = attached(StandInWindow(answers=[(str(pdf),)]))
        api.choose_pdf({"language": "cs"})
        jan, novak = api.page_words(0)[:2]
        finding, *_ = api.add_finding(0, jan["start"], novak["end"], "person")
        assert finding["text"] == "Jan Novak"
        assert api.remove_entity(finding["id"]) == [finding["id"]]

    def test_dialogs_need_the_window(self):
        with pytest.raises(ReviewError, match="window is not ready"):
            WindowApi(ReviewApi()).choose_pdf()


class TestExportDialog:
    def test_exports_where_the_reviewer_chose(self, pdf: Path):
        destination = pdf.with_name("chosen.pdf")
        window = StandInWindow(answers=[(str(pdf),), str(destination)])
        api = attached(window)
        api.choose_pdf({"language": "cs"})
        result = api.export_as()
        assert result is not None
        assert result["written"] is True
        assert destination.exists()
        assert window.asked[1]["dialog"] == webview.FileDialog.SAVE
        assert window.asked[1]["save_filename"] == "cv-redacted.pdf"

    def test_cancelled_export_writes_nothing(self, pdf: Path):
        api = attached(StandInWindow(answers=[(str(pdf),), None]))
        api.choose_pdf({"language": "cs"})
        assert api.export_as() is None
        assert sorted(path.name for path in pdf.parent.iterdir()) == ["cv.pdf"]

    def test_tells_the_page_each_step(self, pdf: Path):
        window = StandInWindow(answers=[(str(pdf),), str(pdf.with_name("chosen.pdf"))])
        api = attached(window)
        api.choose_pdf({"language": "cs"})
        api.export_as()
        told = [detail for name, detail in window.events_told() if name == "export"]
        assert told[0] == {"step": "redacting", "done": 0, "total": 1}
        assert told[-1] == {"step": "file_bytes", "done": 0, "total": 0}

    def test_a_refused_copy_is_saved_where_it_was_going_without_a_second_check(
        self, pdf: Path, monkeypatch: pytest.MonkeyPatch
    ):
        leak = Leak(LeakLayer.PAGE_TEXT, "page 0", CONTACT_EMAIL, "e1", page_index=0)
        monkeypatch.setattr(export_module, "find_leaks", lambda *_, **__: [leak])
        destination = pdf.with_name("chosen.pdf")
        api = attached(StandInWindow(answers=[(str(pdf),), str(destination)]))
        api.choose_pdf({"language": "cs"})
        refused = api.export_as()
        assert refused is not None
        assert (refused["written"], refused["leak_check"]) == (False, "failed")
        assert not destination.exists()
        saved = api.export_unchecked()
        assert (saved["written"], saved["leak_check"]) == (True, "off")
        assert destination.exists()
        with pytest.raises(ReviewError, match="no refused export"):
            api.export_unchecked()

    def test_nothing_refused_cannot_be_saved(self, pdf: Path):
        destination = pdf.with_name("chosen.pdf")
        api = attached(StandInWindow(answers=[(str(pdf),), str(destination)]))
        api.choose_pdf({"language": "cs"})
        assert api.export_as() is not None
        with pytest.raises(ReviewError, match="no refused export"):
            api.export_unchecked()

    def test_closing_forgets_a_refused_export(self, pdf: Path, monkeypatch: pytest.MonkeyPatch):
        leak = Leak(LeakLayer.PAGE_TEXT, "page 0", CONTACT_EMAIL, "e1", page_index=0)
        monkeypatch.setattr(export_module, "find_leaks", lambda *_, **__: [leak])
        api = attached(StandInWindow(answers=[(str(pdf),), str(pdf.with_name("chosen.pdf"))]))
        api.choose_pdf({"language": "cs"})
        api.export_as()
        api.close_document()
        with pytest.raises(ReviewError, match="no refused export"):
            api.export_unchecked()

    def test_the_leak_check_setting_is_forwarded(self):
        api = WindowApi(ReviewApi())
        assert api.set_leak_check(False)["settings"] == {"leak_check": False}

    def test_passes_consent_for_pages_without_text(self, tmp_path: Path):
        mixed = write_pdf(tmp_path / "mixed.pdf", [LINES, []])
        destination = tmp_path / "out.pdf"
        api = attached(StandInWindow(answers=[(str(mixed),), str(destination)]))
        api.choose_pdf({"language": "cs"})
        result = api.export_as(True)
        assert result is not None
        assert result["pages_without_text"] == [2]


def drop_event(*paths: str) -> dict[str, Any]:
    """A drop event as pywebview's handler receives it, with full paths filled in."""
    files = [{"name": Path(path).name, "pywebviewFullPath": path} for path in paths]
    return {"type": "drop", "dataTransfer": {"files": files}}


class TestHomeScreenCalls:
    def test_status_is_forwarded(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(api_module, "name_model_installed", lambda model_id, catalog: False)
        (model,) = WindowApi(ReviewApi()).status()["names"]["models"]
        assert model["state"] == "not_installed"

    def test_opening_reports_each_step_to_the_page(self, pdf: Path):
        window = StandInWindow(answers=[(str(pdf),)])
        attached(window).choose_pdf({"language": "cs", "propagate": False})
        assert window.events_told() == [
            ("progress", {"step": "reading", "done": 0, "total": 0}),
            ("progress", {"step": "detecting", "done": 0, "total": 1}),
            ("progress", {"step": "detecting", "done": 1, "total": 1}),
        ]

    def test_options_select_the_name_model(self, pdf: Path, monkeypatch: pytest.MonkeyPatch):
        chosen: list[str] = []

        def load(model_id: str, root: Path, catalog: object) -> NameModel:
            chosen.append(model_id)
            return NameModel()

        monkeypatch.setattr(api_module, "load_name_model", load)
        window = StandInWindow(answers=[(str(pdf),)])
        payload = attached(window).choose_pdf({"language": "cs", "use_model": True})
        assert chosen == ["gliner-multi-v2.1"]
        assert payload is not None
        assert "person" in {entity["type"] for entity in payload["entities"]}
        assert (
            "progress",
            {"step": "loading_model", "done": 0, "total": 0},
        ) in window.events_told()

    @pytest.mark.parametrize(
        ("options", "message"),
        [
            ("cs", "must be an object"),
            ({"language": "xx"}, "unknown language 'xx'"),
            ({"use_ocr": True, "ocr_engine": "tesseract"}, "unknown OCR engine 'tesseract'"),
            ({"use_ocr": True, "ocr_engine": ["onnxtr"]}, "unknown OCR engine"),
            ({"use_model": True, "name_model": "other"}, "unknown name model 'other'"),
            ({"use_model": True, "name_model": 3}, "unknown name model 3"),
        ],
    )
    def test_options_from_the_page_are_checked(self, pdf: Path, options: Any, message: str):
        api = attached(StandInWindow(answers=[(str(pdf),)]))
        with pytest.raises(ReviewError, match=message):
            api.choose_pdf(options)

    def test_auto_is_accepted_as_a_language(self, pdf: Path):
        payload = attached(StandInWindow(answers=[(str(pdf),)])).choose_pdf({"language": "auto"})
        assert payload is not None
        assert payload["language_recognised"] is True

    def test_close_returns_to_home(self, pdf: Path):
        window = StandInWindow(answers=[(str(pdf),)])
        api = attached(window)
        api.choose_pdf({"language": "cs"})
        api.close_document()
        assert api.current_document() is None
        assert window.title == "Anonymizer"


class TestDrop:
    def test_drop_handlers_are_bound_when_the_page_loads(self, stand_in: StandInWebview):
        main([])
        api = stand_in.created["js_api"]
        (bind,) = stand_in.window.events.loaded.handlers
        bind()
        bound = stand_in.window.dom.document.bound
        assert set(bound) == {"dragover", "drop"}
        assert bound["drop"].callback == api._on_drop
        assert bound["drop"].prevent_default is True

    def test_a_dropped_pdf_is_named_to_the_page_and_opened_on_request(self, pdf: Path):
        window = StandInWindow()
        api = attached(window)
        api._on_drop(drop_event("/tmp/notes.txt", str(pdf)))
        assert window.events_told() == [("dropped", "cv.pdf")]
        assert not any(str(pdf) in script for script in window.scripts)  # the path stays here

        payload = api.open_dropped({"language": "cs"})
        assert payload is not None
        assert payload["name"] == "cv.pdf"
        assert window.title == "cv.pdf — Anonymizer"
        assert api.open_dropped() is None  # used once

    def test_a_dropped_image_is_opened(self, tmp_path: Path):
        photo = tmp_path / "photo.JPG"
        photo.write_bytes(encode(upright_scan(LINES), "JPEG"))
        window = StandInWindow()
        api = attached(window)
        api._on_drop(drop_event(str(photo)))
        assert window.events_told() == [("dropped", "photo.JPG")]
        payload = api.open_dropped()
        assert payload is not None
        assert payload["pages"][0]["has_text_layer"] is False

    def test_a_drop_without_a_pdf_or_an_image_is_refused(self):
        window = StandInWindow()
        api = attached(window)
        api._on_drop(drop_event("/tmp/letter.docx", "/tmp/photo.heic"))
        assert window.events_told() == [("drop-refused", "letter.docx")]
        assert api.open_dropped() is None

    def test_a_drop_without_paths_is_refused(self):
        window = StandInWindow()
        attached(window)._on_drop({"type": "drop", "dataTransfer": {"files": [{"name": "x.pdf"}]}})
        assert window.events_told() == [("drop-refused", "")]

    def test_closing_forgets_a_pending_drop(self, pdf: Path):
        window = StandInWindow(answers=[(str(pdf),)])
        api = attached(window)
        api.choose_pdf({"language": "cs"})
        api._on_drop(drop_event(str(pdf)))
        api.close_document()
        assert api.open_dropped() is None


class TestMainOptions:
    def test_the_name_model_for_the_given_pdf(
        self, stand_in: StandInWebview, pdf: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        loads: list[tuple[str, Path]] = []

        def load(model_id: str, root: Path, catalog: object) -> NameModel:
            loads.append((model_id, root))
            return NameModel()

        monkeypatch.setattr(api_module, "load_name_model", load)
        assert main([str(pdf), "--lang", "cs", "--ner", "--resource-root", str(tmp_path)]) == 0
        document = stand_in.created["js_api"].current_document()
        assert "person" in {entity["type"] for entity in document["entities"]}
        assert loads == [("gliner-multi-v2.1", tmp_path)]


class TestOcr:
    @pytest.fixture
    def scan(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        """A scan of `LINES`, with the ink-reading stand-in in place of each engine."""
        original = load_document(write_pdf(tmp_path / "original.pdf", [LINES]))

        def load(name: str, root: Path) -> InkReadingEngine:
            engine = InkReadingEngine.reading(original)
            engine.name = name
            return engine

        monkeypatch.setattr(api_module, "load_ocr_engine", load)
        return write_scanned_pdf(tmp_path / "scan.pdf", [LINES])

    def test_the_page_asks_for_ocr_and_is_told_it_loads(self, scan: Path):
        window = StandInWindow(answers=[(str(scan),)])
        payload = attached(window).choose_pdf({"language": "cs", "use_ocr": True})
        assert payload is not None
        assert payload["pages"][0]["raster_dpi"] == 300
        assert [
            detail["step"] for event, detail in window.events_told() if event == "progress"
        ] == [
            "loading_ocr",
            "reading",
            "ocr",
            "ocr",
            "detecting",
            "detecting",
        ]

    def test_a_saved_review_of_a_scan_reopens_with_its_engine(self, scan: Path, tmp_path: Path):
        session = tmp_path / "review.json"
        window = StandInWindow(answers=[(str(scan),), str(session), (str(session),), (str(scan),)])
        api = attached(window)
        api.choose_pdf({"language": "cs", "use_ocr": True, "ocr_engine": "kraken"})
        assert api.save_session_as() is True
        payload = api.choose_session()
        assert payload is not None
        assert payload["pages"][0]["raster_dpi"] == 300
        assert api._review._open is not None
        assert api._review._open.document.ocr_engine == "kraken"

    def test_the_engine_is_left_out_unless_ocr_is_asked_for(self, scan: Path):
        window = StandInWindow(answers=[(str(scan),)])
        payload = attached(window).choose_pdf({"language": "cs", "ocr_engine": "kraken"})
        assert payload is not None
        assert payload["pages"][0]["raster_dpi"] is None

    def test_command_line_reads_the_given_scan(
        self, stand_in: StandInWebview, scan: Path, tmp_path: Path
    ):
        assert main([str(scan), "--lang", "cs", "--ocr", "--resource-root", str(tmp_path)]) == 0
        document = stand_in.created["js_api"].current_document()
        assert document["pages"][0]["raster_dpi"] == 300
        assert stand_in.created["js_api"]._review._open.document.ocr_engine == "onnxtr"

    def test_command_line_chooses_the_engine(
        self, stand_in: StandInWebview, scan: Path, tmp_path: Path
    ):
        arguments = [str(scan), "--ocr", "kraken", "--resource-root", str(tmp_path)]
        assert main(arguments) == 0
        assert stand_in.created["js_api"]._review._open.document.ocr_engine == "kraken"


class TestLogging:
    def test_debug_turns_on_debug_logging_and_the_inspector(
        self, stand_in: StandInWebview, pdf: Path, capsys: pytest.CaptureFixture
    ):
        assert main([str(pdf), "--lang", "cs", "--debug"]) == 0
        assert stand_in.started == {"debug": True, "private_mode": True}
        err = capsys.readouterr().err
        assert "detection: start" in err
        assert "find_emails matched" in err

    def test_debug_writes_no_file(
        self, stand_in: StandInWebview, pdf: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        before = {path.name for path in tmp_path.iterdir()}
        main([str(pdf), "--debug"])
        assert {path.name for path in tmp_path.iterdir()} == before

    def test_log_file_is_written_only_when_named(
        self, stand_in: StandInWebview, pdf: Path, tmp_path: Path
    ):
        target = tmp_path / "window.log"
        main([str(pdf), "--log-level", "info", "--log-file", str(target)])
        written = target.read_text(encoding="utf-8")
        assert "anonymize-ui" in written
        assert "window closed" in written
        assert "cv.pdf" not in written

    def test_the_default_is_quiet(
        self, stand_in: StandInWebview, pdf: Path, capsys: pytest.CaptureFixture
    ):
        main([str(pdf)])
        assert capsys.readouterr().err == ""

    def test_a_refused_call_is_a_warning_with_no_message(self, capsys: pytest.CaptureFixture):
        configure_logging(logging.WARNING)
        api = attached(StandInWindow())
        with pytest.raises(ReviewError):
            api.set_review("any", "confirmed")
        err = capsys.readouterr().err
        assert "page call set_review was refused" in err
        assert "WARNING" in err
        assert "no document is open" not in err

    def test_an_unexpected_failure_is_an_error(self, capsys: pytest.CaptureFixture):
        configure_logging(logging.WARNING)
        api = attached(StandInWindow())
        api._review.page_image = None  # type: ignore[method-assign,assignment]
        with pytest.raises(TypeError):
            api.page_image(0)
        err = capsys.readouterr().err
        assert "ERROR" in err
        assert "page call page_image failed" in err
