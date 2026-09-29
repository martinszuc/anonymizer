"""The `anonymize-ui` command: a native window around `ReviewApi`.

The window shows the built frontend from `static/`, served by pywebview on
127.0.0.1 only. During frontend development `--dev-server` points it at Vite
instead, so edits reload without a rebuild.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import webview
from anonymizer.ui.api import ReviewApi, ReviewError

STATIC_INDEX = Path(__file__).parent / "static" / "index.html"

_PDF_TYPES = ("PDF documents (*.pdf)",)
_SESSION_TYPES = ("Review sessions (*.json)",)

_NOT_BUILT = """<!doctype html><meta charset="utf-8">
<body style="font: 15px system-ui; padding: 32px">
<h2>The review window has not been built</h2>
<p>Run <code>npm ci &amp;&amp; npm run build</code> in <code>packages/ui/frontend</code>,
or start it with <code>--dev-server</code>.</p></body>"""


class WindowApi(ReviewApi):
    """`ReviewApi` plus the native file dialogs, which need the window."""

    def __init__(self) -> None:
        super().__init__()
        # Private, so pywebview does not expose the window object to the page.
        self._window: webview.Window | None = None

    def attach(self, window: webview.Window) -> None:
        """Give the API the window its dialogs open over."""
        self._window = window

    def current_document(self) -> dict[str, Any] | None:
        """Describe the open document, or return None when nothing is open."""
        try:
            return self.document()
        except ReviewError:
            return None

    def choose_pdf(self, language: str | None = None) -> dict[str, Any] | None:
        """Ask for a PDF and open it; None if the reviewer cancelled."""
        path = self._ask(webview.FileDialog.OPEN, _PDF_TYPES)
        if path is None:
            return None
        return self._titled(self.open_pdf(path, language))

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
        return self._titled(self.open_session(pdf, session))

    def save_session_as(self) -> bool:
        """Ask where to save the review and write it; False if cancelled."""
        name = Path(self.document()["name"]).stem
        path = self._ask(webview.FileDialog.SAVE, _SESSION_TYPES, f"{name}-review.json")
        if path is None:
            return False
        self.save_session(path)
        return True

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
    api = WindowApi()
    title = "Anonymizer"
    if args.input is not None:
        try:
            title = f"{api.open_pdf(str(args.input), args.lang)['name']} — {title}"
        except ReviewError as error:
            print(f"anonymize-ui: error: {error}", file=sys.stderr)
            return 1
    url, html = _content(args.dev_server)
    window = webview.create_window(
        title, url=url, html=html, js_api=api, width=1280, height=860, min_size=(900, 600)
    )
    if window is None:  # pragma: no cover - only in pywebview's multi-process mode
        return 1
    api.attach(window)
    webview.start(debug=args.debug, private_mode=True)
    return 0


def _content(dev_server: str | None) -> tuple[str | None, str | None]:
    """Where the window's page comes from, as (url, html): Vite, the build, or a notice."""
    if dev_server is not None:
        return dev_server, None
    if STATIC_INDEX.is_file():
        return str(STATIC_INDEX), None
    return None, _NOT_BUILT
