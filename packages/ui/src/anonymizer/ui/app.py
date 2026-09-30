"""The `anonymize-ui` command: a native window around `ReviewApi`.

The window shows the built frontend from `static/`, served by pywebview on
127.0.0.1 only. During frontend development `--dev-server` points it at Vite
instead, so edits reload without a rebuild.

Python tells the page about things it did not ask for (a step of opening a
PDF, a file dropped on the window) with DOM events on `window`, named
`anonymizer:<what>`; see `frontend/src/bridge.ts`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import webview
from anonymizer.ui.api import LANGUAGES, ReviewApi, ReviewError
from webview.dom import DOMEventHandler

STATIC_INDEX = Path(__file__).parent / "static" / "index.html"

_PDF_TYPES = ("PDF documents (*.pdf)",)
_SESSION_TYPES = ("Review sessions (*.json)",)

_NOT_BUILT = """<!doctype html><meta charset="utf-8">
<body style="font: 15px system-ui; padding: 32px">
<h2>The review window has not been built</h2>
<p>Run <code>npm ci &amp;&amp; npm run build</code> in <code>packages/ui/frontend</code>,
or start it with <code>--dev-server</code>.</p></body>"""


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
        # A PDF dropped on the window: its path stays here, and the page only
        # learns its name, so no path ever comes from the page.
        self._dropped: Path | None = None

    def _attach(self, window: webview.Window) -> None:
        """Give the API the window its dialogs open over; private so the page cannot."""
        self._window = window

    def status(self) -> dict[str, Any]:
        """Describe the installation for the home screen; see `ReviewApi.status`."""
        return self._review.status()

    def current_document(self) -> dict[str, Any] | None:
        """Describe the open document, or return None when nothing is open."""
        try:
            return self._review.document()
        except ReviewError:
            return None

    def choose_pdf(self, options: Any = None) -> dict[str, Any] | None:
        """Ask for a PDF and open it; None if the reviewer cancelled.

        `options` is `{language, propagate, use_model}`, all optional; see
        `ReviewApi.open_pdf`.
        """
        path = self._ask(webview.FileDialog.OPEN, _PDF_TYPES)
        if path is None:
            return None
        return self._open(path, options)

    def open_dropped(self, options: Any = None) -> dict[str, Any] | None:
        """Open the PDF last dropped on the window; None if there is none.

        `options` as for `choose_pdf`.
        """
        dropped, self._dropped = self._dropped, None
        if dropped is None:
            return None
        return self._open(str(dropped), options)

    def close_document(self) -> None:
        """Close the open document and return the window to its home screen."""
        self._review.close()
        self._dropped = None
        self._attached().title = "Anonymizer"

    def choose_session(self) -> dict[str, Any] | None:
        """Ask for a session file, then for the PDF it reviewed; None if cancelled.

        The session stores a fingerprint rather than a path, since a path can
        itself be personal data, so the reviewer points at the original.
        """
        session = self._ask(webview.FileDialog.OPEN, _SESSION_TYPES)
        if session is None:
            return None
        pdf = self._ask(webview.FileDialog.OPEN, _PDF_TYPES)
        if pdf is None:
            return None
        return self._titled(self._review.open_session(pdf, session))

    def save_session_as(self) -> bool:
        """Ask where to save the review and write it; False if cancelled."""
        default = f"{Path(self._review.name).stem}-review.json"
        path = self._ask(webview.FileDialog.SAVE, _SESSION_TYPES, default)
        if path is None:
            return False
        self._review.save_session(path)
        return True

    def export_as(self, allow_pages_without_text: bool = False) -> dict[str, Any] | None:
        """Ask where to write the redacted copy and export it; None if cancelled.

        See `ReviewApi.export` for the result and for pages without a text layer.
        """
        default = f"{Path(self._review.name).stem}-redacted.pdf"
        path = self._ask(webview.FileDialog.SAVE, _PDF_TYPES, default)
        if path is None:
            return None
        return self._review.export(path, allow_pages_without_text)

    def page_image(self, index: int, dpi: int = 144) -> str:
        """Render a page of the open PDF; see `ReviewApi.page_image`."""
        return self._review.page_image(index, dpi)

    def set_review(self, entity_id: str, state: str) -> dict[str, Any]:
        """Record the reviewer's decision on one entity; see `ReviewApi.set_review`."""
        return self._review.set_review(entity_id, state)

    def add_region(
        self, page_index: int, x0: float, y0: float, x1: float, y1: float
    ) -> dict[str, Any]:
        """Add a region the reviewer drew; see `ReviewApi.add_region`."""
        return self._review.add_region(page_index, x0, y0, x1, y1)

    def remove_entity(self, entity_id: str) -> None:
        """Remove an item the reviewer added; see `ReviewApi.remove_entity`."""
        self._review.remove_entity(entity_id)

    def _open(self, path: str, options: Any) -> dict[str, Any]:
        language, propagate, use_model = _open_options(options)
        payload = self._review.open_pdf(path, language, propagate, use_model, self._progress)
        return self._titled(payload)

    def _progress(self, step: str) -> None:
        """Tell the page which step of opening a PDF has started."""
        self._notify("progress", step)

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
        """Keep the first dropped PDF and tell the page its name, never its path."""
        files = event.get("dataTransfer", {}).get("files", [])
        paths = [Path(file["pywebviewFullPath"]) for file in files if file.get("pywebviewFullPath")]
        pdf = next((path for path in paths if path.suffix.lower() == ".pdf"), None)
        if pdf is None:
            names = [path.name for path in paths]
            self._notify("drop-refused", names[0] if names else "")
            return
        self._dropped = pdf
        self._notify("dropped", pdf.name)

    def _ask(
        self, dialog: webview.FileDialog, file_types: tuple[str, ...], save_name: str = ""
    ) -> str | None:
        """Show a file dialog and return the chosen path."""
        chosen = self._attached().create_file_dialog(
            dialog, save_filename=save_name, file_types=file_types
        )
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


def _ignore(_event: dict[str, Any]) -> None:
    """A drag over the page needs a handler only so the drop is allowed."""


def _open_options(options: Any) -> tuple[str | None, bool, bool]:
    """Read `{language, propagate, use_model}` from the page, which is not trusted."""
    if options is None:
        options = {}
    if not isinstance(options, dict):
        msg = "open options must be an object"
        raise ReviewError(msg)
    language = options.get("language")
    if language is not None and language not in LANGUAGES:
        msg = f"unknown language {language!r}"
        raise ReviewError(msg)
    return language, bool(options.get("propagate", True)), bool(options.get("use_model", False))


def build_parser() -> argparse.ArgumentParser:
    """Define the command line."""
    parser = argparse.ArgumentParser(
        prog="anonymize-ui", description="Review proposed redactions in a window, offline."
    )
    parser.add_argument("input", nargs="?", type=Path, help="PDF to open")
    parser.add_argument(
        "--lang", help="document language, e.g. cs, sk or en; every rule runs when omitted"
    )
    parser.add_argument(
        "--ner",
        action="store_true",
        help="also run the name model on the PDF given here (install with uv sync --group ner)",
    )
    parser.add_argument(
        "--resource-root",
        type=Path,
        default=Path(),
        help="directory holding models/ (default: the current directory)",
    )
    parser.add_argument(
        "--dev-server",
        metavar="URL",
        help="load the frontend from a local Vite server (e.g. http://localhost:5173)",
    )
    parser.add_argument("--debug", action="store_true", help="allow the web inspector")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Open the review window.

    Args:
        argv: Argument list to parse. Defaults to `sys.argv[1:]`.

    Returns:
        The exit code: 0 once the window closes, 1 if the given PDF cannot be opened.
    """
    args = build_parser().parse_args(argv)
    review = ReviewApi(args.resource_root)
    title = "Anonymizer"
    if args.input is not None:
        try:
            opened = review.open_pdf(str(args.input), args.lang, True, args.ner)
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
    webview.start(debug=args.debug, private_mode=True)
    return 0


def _content(dev_server: str | None) -> tuple[str | None, str | None]:
    """Where the window's page comes from, as (url, html): Vite, the build, or a notice."""
    if dev_server is not None:
        return dev_server, None
    if STATIC_INDEX.is_file():
        return str(STATIC_INDEX), None
    return None, _NOT_BUILT
