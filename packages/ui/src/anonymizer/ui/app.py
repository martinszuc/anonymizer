"""The `anonymize-ui` command: a native window around `ReviewApi`.

The window shows the built frontend from `static/`, served by pywebview on
127.0.0.1 only. During frontend development `--dev-server` points it at Vite
instead, so edits reload without a rebuild.

Python tells the page about things it did not ask for (a step of opening a
document, a file dropped on the window) with DOM events on `window`, named
`anonymizer:<what>`; see `frontend/src/bridge.ts`.
"""

from __future__ import annotations

import argparse
import functools
import json
import logging
import platform
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import webview
from anonymizer.core.detect import DEFAULT_NAME_MODEL, name_models
from anonymizer.core.ingest import IMAGE_SUFFIXES, OCR_ENGINES, SOURCE_SUFFIXES
from anonymizer.core.language import AUTO
from anonymizer.core.log import LEVEL_NAMES, configure_logging, resolve_level, step
from anonymizer.core.resources import resolve_resource_root
from anonymizer.ui import __version__
from anonymizer.ui.api import DEFAULT_OCR_ENGINE, LANGUAGES, ReviewApi, ReviewError
from webview.dom import DOMEventHandler

log = logging.getLogger(__name__)

STATIC_INDEX = Path(__file__).parent / "static" / "index.html"

_PDF_TYPES = ("PDF documents (*.pdf)",)
# The redacted copy is always a PDF; a document to review may also be an image.
_SOURCE_TYPES = (
    f"Documents ({';'.join(f'*{suffix}' for suffix in SOURCE_SUFFIXES)})",
    *_PDF_TYPES,
    f"Images ({';'.join(f'*{suffix}' for suffix in IMAGE_SUFFIXES)})",
)
_SESSION_TYPES = ("Review sessions (*.json)",)

_NOT_BUILT = """<!doctype html><meta charset="utf-8">
<body style="font: 15px system-ui; padding: 32px">
<h2>The review window has not been built</h2>
<p>Run <code>npm ci &amp;&amp; npm run build</code> in <code>packages/ui/frontend</code>,
or start it with <code>--dev-server</code>.</p></body>"""


def _logged[**P, R](call: Callable[P, R]) -> Callable[P, R]:
    """Log a page call: its start and end at DEBUG, and why it failed.

    A request the window refused (`ReviewError`) is a warning; anything else
    is an error. The exception's message is never written (see `core.log`);
    only its type and the frames it passed through. Arguments are not
    logged: they are paths and ids the call's own module reports.
    """

    @functools.wraps(call)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        name = call.__name__
        try:
            with step(log, f"page call {name}"):
                return call(*args, **kwargs)
        except ReviewError:
            log.warning("page call %s was refused", name, exc_info=True)
            raise
        except Exception:
            log.exception("page call %s failed", name)
            raise

    return wrapper


class WindowApi:
    """The calls the page may make: the review, with paths chosen in native dialogs.

    pywebview hands every public method and attribute of this object to the
    page's JavaScript, inherited ones included. The `ReviewApi` it wraps takes
    file paths and would write a session anywhere it is told, so it stays
    private: here a path only ever comes from a dialog the reviewer answered.
    The public methods are exactly the `ReviewBridge` in `frontend/src/bridge.ts`.
    """

    def __init__(self, review: ReviewApi) -> None:
        self._review = review
        self._window: webview.Window | None = None
        # A document dropped on the window: its path stays here, and the page only
        # learns its name, so no path ever comes from the page.
        self._dropped: Path | None = None
        # The last whole percent told to the page per feature, so a download of
        # a gigabyte sends a hundred events rather than a thousand.
        self._told_percent: dict[str, int] = {}
        # Where the last export the leak check refused was going, and whether it
        # allowed unread scans: saving it anyway reuses them, so that call takes no path.
        self._refused_export: tuple[str, bool] | None = None
        # The copy last written, which the page may ask to be shown in the file manager.
        self._written: Path | None = None

    def _attach(self, window: webview.Window) -> None:
        """Give the API the window its dialogs open over; private so the page cannot."""
        self._window = window

    @_logged
    def status(self) -> dict[str, Any]:
        """Describe the installation for the home screen; see `ReviewApi.status`."""
        return self._review.status()

    @_logged
    def set_leak_check(self, enabled: bool) -> dict[str, Any]:
        """Turn the leak check on or off for later exports; see `ReviewApi.set_leak_check`."""
        return self._review.set_leak_check(enabled)

    @_logged
    def set_open_options(self, options: Any) -> dict[str, Any]:
        """Keep the home screen's options for later runs; see `ReviewApi.set_open_options`."""
        return self._review.set_open_options(options)

    @_logged
    def set_unsaved_changes(self, unsaved: bool) -> None:
        """Ask before the window closes while the review has changes not saved.

        pywebview asks with its own dialog, worded by `CLOSE_QUESTION`.
        """
        self._attached().confirm_close = unsaved is True

    @_logged
    def models(self) -> list[dict[str, Any]]:
        """Describe each feature's models and whether they are stored; see `ReviewApi.models`."""
        return self._review.models()

    @_logged
    def download_models(self, feature: str) -> list[dict[str, Any]]:
        """Download a feature's models, telling the page how far it is.

        The page names a feature; which files, from where and into which
        folder is decided here and in the catalog (`ReviewApi.download_models`).
        """
        self._told_percent[feature] = -1
        return self._review.download_models(feature, self._download_progress)

    @_logged
    def choose_models_folder(self) -> dict[str, Any] | None:
        """Ask for a folder to store models in from now on; None if the reviewer cancelled.

        Returns the installation as `status()` describes it, for the new folder.
        """
        path = self._ask(webview.FileDialog.FOLDER, ())
        if path is None:
            return None
        return self._review.choose_models_folder(path)

    @_logged
    def current_document(self) -> dict[str, Any] | None:
        """Describe the open document, or return None when nothing is open."""
        try:
            return self._review.document()
        except ReviewError:
            return None

    @_logged
    def choose_pdf(self, options: Any = None) -> dict[str, Any] | None:
        """Ask for a PDF or an image and open it; None if the reviewer cancelled.

        `options` is `{language, propagate, use_model, name_model, use_ocr,
        ocr_engine}`, all optional; see `ReviewApi.open_pdf`.
        """
        path = self._ask(webview.FileDialog.OPEN, _SOURCE_TYPES)
        if path is None:
            return None
        return self._open(path, options)

    @_logged
    def open_dropped(self, options: Any = None) -> dict[str, Any] | None:
        """Open the document last dropped on the window; None if there is none.

        `options` as for `choose_pdf`.
        """
        dropped, self._dropped = self._dropped, None
        if dropped is None:
            return None
        return self._open(str(dropped), options)

    @_logged
    def close_document(self) -> None:
        """Close the open document and return the window to its home screen."""
        self._review.close()
        self._dropped = None
        self._refused_export = None
        self._written = None
        self._attached().title = "Anonymizer"

    @_logged
    def choose_session(self) -> dict[str, Any] | None:
        """Ask for a session file, then for the document it reviewed; None if cancelled.

        The session stores a fingerprint rather than a path, since a path can
        itself be personal data, so the reviewer points at the original.
        """
        session = self._ask(webview.FileDialog.OPEN, _SESSION_TYPES)
        if session is None:
            return None
        source = self._ask(webview.FileDialog.OPEN, _SOURCE_TYPES)
        if source is None:
            return None
        self._refused_export = None
        return self._titled(self._review.open_session(source, session, self._progress))

    @_logged
    def save_session_as(self) -> bool:
        """Ask where to save the review and write it; False if cancelled."""
        default = f"{Path(self._review.name).stem}-review.json"
        path = self._ask(webview.FileDialog.SAVE, _SESSION_TYPES, default)
        if path is None:
            return False
        self._review.save_session(path)
        return True

    @_logged
    def export_as(self, allow_pages_without_text: bool = False) -> dict[str, Any] | None:
        """Ask where to write the redacted copy and export it; None if cancelled.

        Each step is told to the page as `anonymizer:export`. See
        `ReviewApi.export` for the result and for pages without a text layer.
        """
        self._refused_export = None
        default = f"{Path(self._review.name).stem}-redacted.pdf"
        path = self._ask(webview.FileDialog.SAVE, _PDF_TYPES, default)
        if path is None:
            return None
        result = self._review.export(path, allow_pages_without_text, self._export_progress)
        if result["written"]:
            self._written = Path(path)
        else:
            self._refused_export = (path, bool(allow_pages_without_text))
        return result

    @_logged
    def export_unchecked(self) -> dict[str, Any]:
        """Write the copy the leak check refused, where it was going, without checking again.

        The reviewer has seen the leaks and decided to keep the copy. Redaction
        makes the same file again; nothing else is left out.
        """
        if self._refused_export is None:
            msg = "there is no refused export to save"
            raise ReviewError(msg)
        (path, allow_pages_without_text), self._refused_export = self._refused_export, None
        result = self._review.export(
            path, allow_pages_without_text, self._export_progress, check=False
        )
        self._written = Path(path)
        return result

    @_logged
    def show_export(self) -> None:
        """Show the copy just exported in the system's file manager.

        The path is the one the reviewer chose in the save dialog; the page names none.
        """
        if self._written is None or not self._written.is_file():
            msg = "there is no exported copy to show"
            raise ReviewError(msg)
        _reveal(self._written)

    @_logged
    def page_image(self, index: int, dpi: int = 144) -> str:
        """Render a page of the open document; see `ReviewApi.page_image`."""
        return self._review.page_image(index, dpi)

    @_logged
    def set_review(self, entity_id: str, state: str) -> dict[str, Any]:
        """Record the reviewer's decision on one entity; see `ReviewApi.set_review`."""
        return self._review.set_review(entity_id, state)

    @_logged
    def set_reviews(self, entity_ids: Any, state: str) -> list[dict[str, Any]]:
        """Record one decision on several entities; see `ReviewApi.set_reviews`."""
        return self._review.set_reviews(entity_ids, state)

    @_logged
    def add_region(
        self, page_index: int, x0: float, y0: float, x1: float, y1: float
    ) -> dict[str, Any]:
        """Add a region the reviewer drew; see `ReviewApi.add_region`."""
        return self._review.add_region(page_index, x0, y0, x1, y1)

    @_logged
    def page_words(self, index: int) -> list[dict[str, Any]]:
        """List a page's words with their offsets and boxes; see `ReviewApi.page_words`."""
        return self._review.page_words(index)

    @_logged
    def add_finding(
        self, page_index: int, start: int, end: int, entity_type: str
    ) -> list[dict[str, Any]]:
        """Add text the reviewer selected, with its repeats; see `ReviewApi.add_finding`."""
        return self._review.add_finding(page_index, start, end, entity_type)

    @_logged
    def remove_entity(self, entity_id: str) -> list[str]:
        """Remove an item the reviewer added; see `ReviewApi.remove_entity`."""
        return self._review.remove_entity(entity_id)

    def _open(self, path: str, options: Any) -> dict[str, Any]:
        self._refused_export = None
        language, propagate, name_model, ocr_engine = _open_options(options)
        payload = self._review.open_pdf(
            path, language, propagate, name_model, self._progress, ocr_engine
        )
        return self._titled(payload)

    def _progress(self, step: str, done: int, total: int) -> None:
        """Tell the page which step of opening a document is running, and on which page."""
        self._notify("progress", {"step": step, "done": done, "total": total})

    def _export_progress(self, step: str, done: int, total: int) -> None:
        """Tell the page which step of an export is running, and on which page."""
        self._notify("export", {"step": step, "done": done, "total": total})

    def _download_progress(self, feature: str, received: int, total: int) -> None:
        """Tell the page how far a download is, once per whole percent."""
        percent = 100 if total == 0 else min(100, received * 100 // total)
        if percent == self._told_percent.get(feature):
            return
        self._told_percent[feature] = percent
        self._notify("download", {"feature": feature, "received": received, "total": total})

    def _notify(self, what: str, detail: object) -> None:
        """Dispatch `anonymizer:<what>` on the page's window, with plain-data detail."""
        event = json.dumps(f"anonymizer:{what}")
        self._attached().evaluate_js(
            f"window.dispatchEvent(new CustomEvent({event}, {{detail: {json.dumps(detail)}}}))"
        )

    def _watch_drops(self) -> None:
        """Receive files dropped on the page; bound again whenever the page loads.

        Only pywebview's own drop handler sees a dropped file's full path, so
        the drop is handled here rather than in the page.
        """
        document = self._attached().dom.document
        document.on("dragover", DOMEventHandler(_ignore, prevent_default=True))
        document.on("drop", DOMEventHandler(self._on_drop, prevent_default=True))

    def _on_drop(self, event: dict[str, Any]) -> None:
        """Keep the first dropped PDF or image and tell the page its name, never its path.

        The name's ending only picks the file; opening it reads its type from
        the content, and refuses a file that is neither.
        """
        files = event.get("dataTransfer", {}).get("files", [])
        paths = [Path(file["pywebviewFullPath"]) for file in files if file.get("pywebviewFullPath")]
        source = next((path for path in paths if path.suffix.lower() in SOURCE_SUFFIXES), None)
        if source is None:
            log.warning(
                "drop refused: none of the %d dropped file(s) is a PDF or an image", len(paths)
            )
            names = [path.name for path in paths]
            self._notify("drop-refused", names[0] if names else "")
            return
        log.debug("document dropped on the window (%d file(s) in the drop)", len(paths))
        self._dropped = source
        self._notify("dropped", source.name)

    def _ask(
        self, dialog: webview.FileDialog, file_types: tuple[str, ...], save_name: str = ""
    ) -> str | None:
        """Show a file dialog and return the chosen path."""
        chosen = self._attached().create_file_dialog(
            dialog, save_filename=save_name, file_types=file_types
        )
        log.debug("%s dialog: %s", dialog.name, "answered" if chosen else "cancelled")
        if not chosen:
            return None
        # The save dialog returns a plain string on some platforms.
        return chosen if isinstance(chosen, str) else chosen[0]

    def _titled(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._attached().title = f"{payload['name']} — Anonymizer"
        return payload

    def _attached(self) -> webview.Window:
        if self._window is None:
            msg = "the window is not ready"
            raise ReviewError(msg)
        return self._window


def _reveal(path: Path) -> None:
    """Open the file manager at a file, selected where the platform allows it."""
    if sys.platform == "darwin":
        command = ["open", "-R", str(path)]
    elif sys.platform == "win32":
        command = ["explorer", f"/select,{path}"]
    else:
        command = ["xdg-open", str(path.parent)]
    # A list, no shell: the path cannot be read as a command.
    subprocess.Popen(command)


CLOSE_QUESTION = {
    "global.quitConfirmation": "Your decisions on this document are not saved. Close anyway?",
    "global.quit": "Close",
    "global.cancel": "Cancel",
}
"""pywebview's question before closing a window with unsaved changes, in the window's words."""


def _ignore(_event: dict[str, Any]) -> None:
    """A drag over the page needs a handler only so the drop is allowed."""


def _open_options(options: Any) -> tuple[str | None, bool, str | None, str | None]:
    """Read the options for opening a PDF from the page, which is not trusted.

    `{language, propagate, use_model, name_model, use_ocr, ocr_engine}`; the
    name model is returned only when the model is asked for, the engine only
    when OCR is. `ReviewApi.open_pdf` checks the name model against the catalog.
    """
    if options is None:
        options = {}
    if not isinstance(options, dict):
        msg = "open options must be an object"
        raise ReviewError(msg)
    language = options.get("language")
    if language is not None and language != AUTO and language not in LANGUAGES:
        msg = f"unknown language {language!r}"
        raise ReviewError(msg)
    ocr_engine = options.get("ocr_engine", DEFAULT_OCR_ENGINE)
    if not isinstance(ocr_engine, str) or ocr_engine not in OCR_ENGINES:
        msg = f"unknown OCR engine {ocr_engine!r}"
        raise ReviewError(msg)
    name_model = options.get("name_model", DEFAULT_NAME_MODEL)
    if not isinstance(name_model, str):
        msg = f"unknown name model {name_model!r}"
        raise ReviewError(msg)
    return (
        language,
        bool(options.get("propagate", True)),
        name_model if options.get("use_model", False) else None,
        ocr_engine if options.get("use_ocr", False) else None,
    )


def build_parser() -> argparse.ArgumentParser:
    """Define the command line."""
    parser = argparse.ArgumentParser(
        prog="anonymize-ui", description="Review proposed redactions in a window, offline."
    )
    parser.add_argument("input", nargs="?", type=Path, help="PDF or image to open")
    parser.add_argument(
        "--lang",
        help=(
            "document language, e.g. cs, sk or en, or auto to recognise it from the text; "
            "every rule runs when omitted"
        ),
    )
    parser.add_argument(
        "--ner",
        action="store_true",
        help=f"also run the name model {DEFAULT_NAME_MODEL} on the document given here "
        "(install with uv sync --group ner)",
    )
    parser.add_argument(
        "--name-model",
        choices=[model.id for model in name_models()],
        metavar="MODEL",
        help="run this catalog name model instead; implies --ner (choices: %(choices)s)",
    )
    parser.add_argument(
        "--ocr",
        nargs="?",
        const=DEFAULT_OCR_ENGINE,
        choices=sorted(OCR_ENGINES),
        metavar="ENGINE",
        help=f"read scanned pages and images given here with OCR: {', '.join(sorted(OCR_ENGINES))} "
        f"(default {DEFAULT_OCR_ENGINE}; install with uv sync --group ocr-<engine>)",
    )
    parser.add_argument(
        "--resource-root",
        type=Path,
        help="directory holding models/ (default: the folder chosen in the review window, "
        "else ./models if it exists, else a per-user folder)",
    )
    parser.add_argument(
        "--dev-server",
        metavar="URL",
        help="load the frontend from a local Vite server (e.g. http://localhost:5173)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="log every step and every detection (the log holds document text) and allow "
        "the web inspector",
    )
    parser.add_argument(
        "--log-level",
        choices=LEVEL_NAMES,
        help="how much to log to stderr (default: warning; the ANONYMIZER_LOG_LEVEL variable "
        "also sets it, and --debug means debug)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        metavar="PATH",
        help="also append the log to this file; nothing is written to a file without it",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Open the review window.

    Args:
        argv: Argument list to parse. Defaults to `sys.argv[1:]`.

    Returns:
        The exit code: 0 once the window closes, 1 if the given file cannot be opened.
    """
    args = build_parser().parse_args(argv)
    configure_logging(resolve_level(args.log_level, debug=args.debug), file=args.log_file)
    log.info(
        "anonymize-ui %s starting: python %s on %s",
        __version__,
        platform.python_version(),
        platform.system(),
    )
    review = ReviewApi(resolve_resource_root(args.resource_root))
    title = "Anonymizer"
    if args.input is not None:
        try:
            name_model = args.name_model or (DEFAULT_NAME_MODEL if args.ner else None)
            opened = review.open_pdf(
                str(args.input), args.lang, True, name_model, ocr_engine=args.ocr
            )
            title = f"{opened['name']} — {title}"
        except ReviewError as error:
            print(f"anonymize-ui: error: {error}", file=sys.stderr)
            return 1
    api = WindowApi(review)
    url, html = _content(args.dev_server)
    window = webview.create_window(
        title, url=url, html=html, js_api=api, width=1280, height=860, min_size=(900, 600)
    )
    if window is None:  # pragma: no cover - only in pywebview's multi-process mode
        return 1
    api._attach(window)
    window.events.loaded += api._watch_drops
    log.debug("window created, starting the event loop")
    # --debug enables the inspector (context menu, F12 where the platform has it);
    # pywebview would also open it on every start.
    webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
    webview.start(debug=args.debug, private_mode=True, localization=CLOSE_QUESTION)
    log.info("window closed")
    return 0


def _content(dev_server: str | None) -> tuple[str | None, str | None]:
    """Where the window's page comes from, as (url, html): Vite, the build, or a notice."""
    if dev_server is not None:
        return dev_server, None
    if STATIC_INDEX.is_file():
        return str(STATIC_INDEX), None
    return None, _NOT_BUILT
