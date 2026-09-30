"""Drive the real review window through its basic tasks and photograph the screen.

Run by the "Window tour" workflow on every platform we support, and by hand:

    uv run python scripts/ui_tour.py OUT_DIR

Each step of the tour (open a PDF, keep a finding, look at hidden data, preview,
export) is performed in the real window, asserted, and followed by a screenshot
of the *whole screen*, so the file shows the window together with the desktop's
own bars (menu bar, panel, taskbar). Screenshots are numbered WebP files in
OUT_DIR, next to `tour.json`, which lists what each one shows.

The page is driven through `window.evaluate_js`, not with synthetic mouse
input, so the tour checks the real bridge, the core and the rendering, but not
pointer handling. Native file dialogs cannot be scripted; `TourApi` answers
them with fixed paths. The document is generated here and every value in it is
invented.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any

import pymupdf
import webview
from anonymizer.ui.api import ReviewApi
from anonymizer.ui.app import STATIC_INDEX, WindowApi
from PIL import ImageGrab

EMAIL = "jana.modra@example.com"
# Invented values whose checksums were computed independently of the detectors.
BIRTH_NUMBER = "710319/0006"
IBAN = "CZ65 0800 0000 1920 0014 5399"
PHONE = "+420 603 123 456"
HIDDEN_AUTHOR = "Jana Modra"
KEPT_TYPE = "birth_number"  # the finding the tour switches to keep, then back
PLANTED = (EMAIL, BIRTH_NUMBER, IBAN)

SETTLE_SECONDS = 0.7  # let the page finish animating before the screen is read
WAIT_SECONDS = 20.0
WEBP_QUALITY = 85


def build_letter(path: Path) -> None:
    """Write a one-page synthetic letter with visible and hidden personal data."""
    document = pymupdf.open()
    page = document.new_page()
    lines = [
        ("Application for a student grant", 16),
        ("", 11),
        (f"Applicant: {HIDDEN_AUTHOR}", 11),
        (f"Birth number: {BIRTH_NUMBER}", 11),
        (f"E-mail: {EMAIL}", 11),
        (f"Phone: {PHONE}", 11),
        (f"Pay the grant to IBAN {IBAN}", 11),
        ("", 11),
        ("I confirm that the information above is complete and correct.", 11),
        (f"Contact: {EMAIL}", 11),
    ]
    y = 90
    for text, size in lines:
        page.insert_text((72, y), text, fontname="helv", fontsize=size)
        y += size + 14
    page.insert_link(
        {
            "kind": pymupdf.LINK_URI,
            "from": pymupdf.Rect(72, 250, 260, 266),
            "uri": f"mailto:{EMAIL}",
        }
    )
    document.set_metadata({"title": "Grant application", "author": HIDDEN_AUTHOR})
    document.save(path)
    document.close()


class TourApi(WindowApi):
    """The window's API with its file dialogs answered by the tour."""

    def __init__(self, review: ReviewApi, source: Path, output: Path) -> None:
        super().__init__(review)
        self._source = source
        self._output = output

    def _ask(
        self,
        dialog: webview.FileDialog,
        file_types: tuple[str, ...],  # noqa: ARG002
        save_name: str = "",  # noqa: ARG002
    ) -> str | None:
        return str(self._output if dialog == webview.FileDialog.SAVE else self._source)


class Tour:
    """The window under test, the screenshots taken so far and the steps."""

    def __init__(self, window: webview.Window, out_dir: Path, output_pdf: Path) -> None:
        self.window = window
        self.out_dir = out_dir
        self.output_pdf = output_pdf
        self.shots: list[dict[str, str]] = []

    def js(self, expression: str) -> Any:
        """Evaluate JavaScript in the page."""
        return self.window.evaluate_js(expression)

    def wait_for(self, expression: str, what: str) -> None:
        """Poll until a JavaScript expression is truthy; fail naming `what` on timeout."""
        deadline = time.monotonic() + WAIT_SECONDS
        while time.monotonic() < deadline:
            if self.js(f"Boolean({expression})"):
                return
            time.sleep(0.2)
        msg = f"timed out waiting for {what}"
        raise AssertionError(msg)

    def click_button(self, label: str) -> None:
        """Click the enabled button whose text or aria-label is `label`."""
        clicked = self.js(
            f"""(() => {{
              const wanted = {json.dumps(label)};
              const button = [...document.querySelectorAll('button')].find(
                (b) => {{
                  if (b.disabled) return false;
                  const text = b.textContent.trim();
                  // a tab's text also carries its count, e.g. "Hidden2"
                  return b.getAttribute('aria-label') === wanted || text === wanted ||
                    (b.getAttribute('role') === 'tab' && text.startsWith(wanted));
                }}
              );
              if (!button) return false;
              button.click();
              return true;
            }})()"""
        )
        assert clicked, f"no enabled button named {label!r}"

    def click_box(self, entity_type: str) -> None:
        """Click the first proposed redaction of a type, as the reviewer would."""
        self.js(
            f"""document.querySelector('.redaction[data-type="{entity_type}"]')
              .dispatchEvent(new MouseEvent('click', {{bubbles: true}}))"""
        )

    def shot(self, name: str, shows: str) -> None:
        """Photograph the whole screen, system bars included, as a WebP file."""
        time.sleep(SETTLE_SECONDS)
        image = ImageGrab.grab(all_screens=True).convert("RGB")
        file = f"{len(self.shots) + 1:02d}-{name}.webp"
        image.save(self.out_dir / file, "WEBP", quality=WEBP_QUALITY, method=6)
        self.shots.append({"file": file, "shows": shows, "size": f"{image.width}x{image.height}"})
        print(f"  {file}  {image.width}x{image.height}  {shows}")

    def run(self) -> None:
        """Perform every step, asserting as it goes."""
        self.window.maximize()
        self.wait_for("document.querySelector('.empty')", "the start screen")
        self.shot("start", "Start screen before anything is open")

        self.click_button("Open PDF…")
        self.wait_for("document.querySelectorAll('.redaction').length >= 3", "proposed redactions")
        self.wait_for("document.querySelector('.page img, .page canvas')", "the rendered page")
        boxes = self.js("document.querySelectorAll('.redaction').length")
        self.shot("review", f"Review mode, {boxes} proposed redactions over the page")

        self.click_box(KEPT_TYPE)
        self.wait_for(
            "document.querySelector('.redaction[data-state=\"rejected\"]')", "a kept finding"
        )
        self.shot("keep", "One finding switched to keep")

        self.click_box(KEPT_TYPE)
        self.click_button("Hidden")
        self.wait_for("document.querySelector('.group[aria-label]')", "the hidden-data list")
        self.shot("hidden", "Hidden tab: link and metadata that export clears")

        self.click_button("Findings")
        self.click_button("Preview the redacted output")
        self.wait_for("document.querySelector('.toggle[aria-pressed=\"true\"]')", "preview mode")
        self.shot("preview", "Preview: the opaque black boxes the output will contain")
        self.click_button("Preview the redacted output")

        self.click_button("Export…")
        self.wait_for("document.querySelector('.sheet-passed')", "the leak-check result")
        self.shot("export", "Export finished, leak check passed")
        self.click_button("Done")

        assert_no_leaks(self.output_pdf)
        (self.out_dir / "tour.json").write_text(json.dumps(self.shots, indent=2) + "\n")


def assert_no_leaks(path: Path) -> None:
    """Re-read the exported file and fail if a planted value survived."""
    with pymupdf.open(path) as document:
        text = "".join(str(page.get_text()) for page in document)
        metadata = json.dumps(document.metadata)
    survivors = [value for value in PLANTED if value in text or value in metadata]
    survivors += [HIDDEN_AUTHOR] if HIDDEN_AUTHOR in metadata else []
    assert not survivors, f"exported file still contains {survivors}"


def main(argv: list[str] | None = None) -> int:
    """Run the tour and return the exit code."""
    parser = argparse.ArgumentParser(
        description="Drive the review window and photograph the screen."
    )
    parser.add_argument("out_dir", type=Path, help="where the screenshots go")
    parser.add_argument(
        "--allow-desktop",
        action="store_true",
        help="photograph this computer's real screen (otherwise only a CI runner's)",
    )
    args = parser.parse_args(argv)
    if not (args.allow_desktop or os.environ.get("CI")):
        print(
            "ui_tour: this photographs the whole screen, which on your own computer means "
            "your desktop and every window on it.\nRun it on a CI runner or a virtual display, "
            "or pass --allow-desktop after closing anything private.",
            file=sys.stderr,
        )
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if not STATIC_INDEX.is_file():
        print("ui_tour: build the frontend first (npm ci && npm run build)", file=sys.stderr)
        return 2

    failure: list[str] = []
    with tempfile.TemporaryDirectory() as scratch:
        source = Path(scratch) / "grant-application.pdf"
        output = Path(scratch) / "grant-application-redacted.pdf"
        build_letter(source)
        api = TourApi(ReviewApi(), source, output)
        window = webview.create_window(
            "Anonymizer", url=str(STATIC_INDEX), js_api=api, width=1280, height=860, maximized=True
        )
        assert window is not None  # only None in pywebview's multi-process mode
        api._attach(window)
        tour = Tour(window, args.out_dir, output)

        def steps() -> None:
            try:
                tour.run()
            except Exception:
                failure.append(traceback.format_exc())
                try:
                    tour.shot("failure", "The screen when the tour failed")
                except Exception:
                    traceback.print_exc()
            finally:
                window.destroy()

        webview.start(steps, private_mode=True)
    if failure:
        print(failure[0], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
