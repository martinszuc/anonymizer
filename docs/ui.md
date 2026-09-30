# Review window: handbook

Everything needed to work on the review window (`anonymize-ui`) without
reading its history: what exists, how it connects to the core and the CLI,
the rules it must keep, how to add a feature end to end, and what comes next.
Keep this file current: update it in the same pull request as the change.

Visual design (tokens, components, box states) lives in
[`packages/ui/frontend/DESIGN.md`](../packages/ui/frontend/DESIGN.md);
package usage in [`packages/ui/README.md`](../packages/ui/README.md).

## Status (after export, 2026-09-30)

Works, for PDFs with a text layer:

- Open a PDF (native dialog, or `anonymize-ui file.pdf --lang cs`); detection
  runs with the rules for the language and occurrence propagation.
- Reopen a saved review: pick the session file, then the original PDF (a
  session stores a fingerprint, not a path).
- Every page rendered, proposed redactions drawn over it. **Review mode**
  (default) keeps the covered text readable; **preview mode** (eye button,
  Cmd/Ctrl+Y) draws the output's opaque black boxes.
- Click a box or a row switch to toggle redact / keep; hover shows a popover.
- Sidebar: counts, findings grouped by type, a dot on items not yet reviewed,
  arrow keys and Space; a *Hidden* tab lists every hidden item (informational:
  all are removed on export) and outlines their areas on the page.
- **Export** (Cmd/Ctrl+E, the primary toolbar action): save dialog (default
  `<name>-redacted.pdf`), written through core's `export_redacted`, so the
  file exists only if the leak check passed. A sheet asks for consent first
  when pages have no text layer; a result sheet shows the counts and "Leak
  check: Passed", or "Nothing was written" with the leaks.
- Zoom (fit width by default, Cmd/Ctrl +/−/0), save the review, toasts for
  errors, light and dark mode, reduced motion respected.

Verified: macOS (real window driven from Python, see *Verifying the real
window*). Linux and Windows: CI only (install, import, tests), never opened.

Not yet: adding or drawing items, settings, scanned pages. See
*Backlog*.

## Architecture

```
anonymizer.core  (ingest, detect, session, redact)
      │  Python calls
anonymizer/ui/api.py     ReviewApi: plain JSON in and out, no pywebview import
anonymizer/ui/app.py     WindowApi(ReviewApi): native dialogs, window title,
      │                  `anonymize-ui` command, starts pywebview
      │  pywebview js_api bridge: window.pywebview.api.<method>(...) → Promise
frontend/src/bridge.ts   ReviewBridge interface, connect(), errorMessage()
frontend/src/App.tsx     state, shortcuts, optimistic updates
frontend/src/components  Toolbar, Sidebar, PageView, EmptyState, Toasts, controls
```

| File | Owns |
|---|---|
| `packages/ui/src/anonymizer/ui/api.py` | The open document, its PDF bytes, every call the page makes. Converts core input errors to `ReviewError`, whose message the page shows. |
| `packages/ui/src/anonymizer/ui/app.py` | Window creation, file dialogs, what the window loads (build, `--dev-server`, or a "not built" notice). |
| `frontend/src/types.ts` | TypeScript mirror of the payloads `api.py` returns. |
| `frontend/src/bridge.ts` | The method list the page may call; waits for `pywebviewready`; falls back to `demo.ts` in a plain browser under `npm run dev`. |
| `frontend/src/review.ts` | Pure review rules (toggle, grouping, summary, render resolution, zoom). Unit-tested. |
| `frontend/src/pageImages.ts` | Page image cache per document and resolution. |
| `frontend/src/demo.ts` | Synthetic stand-in for Python, development only (excluded from builds). |
| `frontend/src/styles/tokens.css`, `app.css` | Tokens and component styles; see `DESIGN.md`. |
| `tests/ui/test_api.py`, `tests/ui/test_app.py` | Python side, with pywebview stood in. |
| `frontend/src/review.test.ts` | vitest for `review.ts`. |

### The payload contract

`ReviewApi.document()` returns, and `types.ts` mirrors:

```
DocumentInfo { name, language, pages: PageInfo[], entities: EntityInfo[], surfaces: SurfaceInfo[] }
PageInfo     { index, width, height, has_text_layer }              # points
EntityInfo   { id, type, source, score, review, page_index, surface_id,
               text, is_region, boxes: [x0, y0, x1, y1][] }        # points, top-left origin
SurfaceInfo  { id, kind, value, page_index, box | null }
```

`ReviewApi.export()` returns `ExportResult { written, name, redacted, regions,
kept, not_reviewed, hidden_removed, pages_without_text: number[] (1-based),
leaks: { layer, where, text }[] }`; nothing was written unless `written`.

Methods the page calls (all return promises in JS):

| Method | Returns | Notes |
|---|---|---|
| `current_document()` | `DocumentInfo \| null` | on start: a PDF given on the command line |
| `choose_pdf(language)` | `DocumentInfo \| null` | null = cancelled |
| `export_as(allow_pages_without_text)` | `ExportResult \| null` | save dialog; null = cancelled; raises (rejects) when pages lack text and consent is false |
| `choose_session()` | `DocumentInfo \| null` | asks for session, then PDF |
| `save_session_as()` | `bool` | false = cancelled |
| `page_image(index, dpi)` | `data:` PNG URL | dpi clamped to 36..400 in Python |
| `set_review(entity_id, state)` | `EntityInfo` | `pending` / `confirmed` / `rejected` |

A change to a payload or method touches four places: `api.py` (and its test),
`types.ts`, `bridge.ts`, `demo.ts`. Payloads use the core's snake_case names.

## Rules to keep

- **Offline.** No remote fonts, scripts, images or requests. The built page's
  CSP (`frontend/vite.config.ts`) allows its own files, `data:` images, no
  connections. Keep `'unsafe-eval'` in `script-src`: pywebview returns every
  API result to the page through `eval()`; without it every call silently
  never resolves. pywebview serves the build on 127.0.0.1 only.
- **No document content on disk.** Page images stay in memory (Python sends
  `data:` URLs); the window runs with `private_mode=True`; a session file is
  written only on the reviewer's Save. Do not add "recent files" or caches
  that persist paths or content: a file name can itself be personal data.
- **The PDF bytes are read once** and checked against the fingerprint; pages
  render from those bytes, never from the path again.
- **`api.py` never imports pywebview.** Anything needing the window goes in
  `WindowApi` (`app.py`); pure logic goes in `ReviewApi` or the core.
- **Coordinates are PDF points, top-left origin**, as in the core. The page
  overlay is an SVG whose view box is the page size in points, so nothing in
  the frontend converts coordinates. Rotated pages already come rotated from
  ingest and from PyMuPDF's renderer.
- **Review semantics** (decided in `PLAN.md`): undecided (`pending`) items are
  redacted at export; hidden data is always removed, so it has no decision;
  toggling a pending item means *keep* (`rejected`), toggling back is an
  explicit *redact* (`confirmed`).
- **Logic belongs in the core, not the window.** If the CLI could use it
  (export, adding an entity, re-detection), write it in `core` with tests,
  then call it from `ReviewApi`. The window stays a thin client.
- **Styles use tokens** from `tokens.css`, never literal colours or sizes;
  add a token to `DESIGN.md` and `tokens.css` first. Motion respects
  `prefers-reduced-motion` (`MotionConfig reducedMotion="user"` in `App`).
- **Demo data is synthetic** and development-only (`import.meta.env.DEV`).

## Adding a feature end to end

1. **Core first**, if the behaviour is not window-specific: function in
   `packages/core`, Google-style docstring, tests in `tests/`.
2. **`ReviewApi` method** in `api.py`: positional parameters only (pywebview
   passes arguments positionally), plain-data result, core errors wrapped
   with `_as_review_error()`. Test it in `tests/ui/test_api.py` with PDFs from
   `tests/pdf_builders.py`.
3. **Needs a dialog or the window?** Add it to `WindowApi` in `app.py`; test
   it with `StandInWindow` in `tests/ui/test_app.py`.
4. **Frontend contract:** extend `types.ts`, the `ReviewBridge` interface in
   `bridge.ts`, and the stand-in in `demo.ts` so `npm run dev` keeps working.
5. **Pure rules** into `review.ts` (or a new module) with vitest tests;
   components stay presentational.
6. **UI** in `components/`, styled with tokens; new component or state →
   document it in `DESIGN.md`.
7. **Check:** `uv run poe check`; in `packages/ui/frontend`: `npm run check`,
   `npm test`, `npm run build`; look at it in `npm run dev`, then once in the
   real window.
8. **Docs:** update *Status* and *Backlog* here.

## Development

```sh
cd packages/ui/frontend && npm ci
npm run dev                  # http://127.0.0.1:5173 with the demo document
uv run anonymize-ui --dev-server http://127.0.0.1:5173 --debug   # real window, hot reload
npm run build && uv run anonymize-ui some.pdf --lang cs          # real window, built page
```

An AI session can preview the page in its browser pane with `npm run dev`
(the demo document appears after Open PDF…). The demo never goes through
pywebview, so bridge problems (the CSP `eval` issue, argument passing) only
show in the real window.

### Verifying the real window

A native window from a bare Python process cannot be screenshotted by screen
tools, but it can be driven from Python. A throwaway script (keep it in the
scratchpad, not the repository):

```python
import sys, time, webview
from anonymizer.ui.app import STATIC_INDEX, WindowApi

api = WindowApi()
api.open_pdf(sys.argv[1], "cs")
window = webview.create_window("check", url=str(STATIC_INDEX), js_api=api)
api.attach(window)


def probe():
    time.sleep(3)
    print(window.evaluate_js("document.querySelectorAll('.redaction').length"))
    window.evaluate_js(
        "document.querySelector('.redaction')"
        ".dispatchEvent(new MouseEvent('click', {bubbles: true}))"
    )
    time.sleep(1)
    print([e["review"] for e in api.document()["entities"]])
    window.destroy()


webview.start(probe, private_mode=True)
```

Use a synthetic PDF (build one with `tests/pdf_builders.py`), never a real
document.

Native file dialogs cannot be scripted. To drive a feature behind one (open,
save, export), subclass `WindowApi` in the script and override `_ask` to
return a fixed path; everything else (the click in WebKit, the bridge, the
core, the sheet) still runs for real.

## Connections to the rest of the project

| Core / CLI piece | How the window uses it, or will |
|---|---|
| `ingest.load_document`, `file_fingerprint` | `open_pdf`; fingerprint checked against the bytes kept for rendering |
| `detect.detector_for(language)`, `detect_document` | detection on open (rules only today) |
| `detect.load_gliner_detector(root)`, `CombinedDetector` | **not wired**: NER in the window (see backlog, settings) |
| `detect.propagate_occurrences` | on open, always on today |
| `session.save_session` / `load_session` | save and reopen; same files as `anonymize detect` / `redact --session` |
| `Document.adjust_span(entity_id, start, end)` | **not wired**: resizing a box to other words |
| `Entity(type=REGION, bboxes=[box], source=MANUAL)` | **not wired**: drawing a region |
| `redact.export_redacted` | export: temporary file, `redact_pdf`, `find_leaks`, rename only when clean; the CLI's `redact` uses the same function |
| `ingest.pages_needing_ocr`, `Page.raster_dpi` | page warning today; scanned-page review after the OCR path |
| `resources.load_catalog`, `fetch_resource`, `resource_status` | **not wired**: the model setup page (M9) |
| CLI `inspect` (HTML report) | independent; same box geometry, useful to compare against |

## Backlog

In suggested order. Each item names where it plugs in.

1. **Add a missed word or phrase.** Needs the page's words in the payload
   (new `page_words(index)` → text, offsets, boxes) and a core helper that
   creates a `MANUAL` entity from a span (`Page.bboxes_for_span` gives the
   boxes). UI: drag across words in review mode, a popover with a type
   picker, then propagation of the new text (`propagate_occurrences`).
2. **Draw a region** (photo, signature, stamp): drag a rectangle with a
   modifier or a toolbar tool → `REGION` entity with one box in points
   (divide screen pixels by the zoom scale). Redaction and the region leak
   check already support it.
3. **Resize a box** to fewer or more words → `Document.adjust_span`.
4. **Settings sheet:** language (re-run detection, warning that decisions
   reset or are carried over by span), propagation on/off, NER on/off
   (available only when the `ner` group is installed and the model is
   present: `resource_status`), entity types shown.
5. **Unsaved changes on close:** pywebview `confirm_close` or a closing
   event tied to the `dirty` flag; today only opening another document asks.
6. **Undo / redo** of decisions (Cmd/Ctrl+Z), kept in the frontend as a
   stack of `set_review` calls.
7. **Drag and drop a PDF** onto the window.
8. **Model setup page (M9):** catalog entries with task, languages, size,
   licence; download only on an explicit click, from the official source,
   verified by SHA-256 (`fetch_resource`), progress shown.
9. **Scanned pages** once the OCR path exists: OCR words arrive with
    `raster_dpi`, boxes are already in points; the warning goes away;
    region drawing matters more.
10. **Label mode preview** once labels exist (M5): preview draws `[NAME]`
    instead of black boxes.
11. **Accessibility pass:** boxes are not keyboard-reachable (the list is the
    keyboard path); run a WCAG review of both themes.
12. **Packaging (M9):** PyInstaller bundle per OS; test Windows (WebView2)
    and Linux (GTK or Qt backend) by hand.
13. **Large documents:** virtualize the page list and the sidebar beyond a
    few hundred pages or entities.

## Known gotchas

- pywebview exposes public attributes of the `js_api` object to the page;
  keep state in underscore attributes (`_open`, `_window`).
- pywebview calls methods with positional arguments; keyword-only
  parameters cannot be called from the page.
- A Python exception reaches the page as a rejected promise whose `message`
  is the exception text; `bridge.errorMessage()` extracts it.
- React StrictMode runs effects twice in development; `connect()` tolerates it.
- The built frontend (`anonymizer/ui/static/`) is git-ignored and bundled
  into the wheel through hatch `artifacts`; the release job builds it first.
  Python tests never need it.
- `anonymizer/ui/__init__.py` carries the release version; release-please
  bumps it with the others. Never edit it by hand except to match
  `version.txt` when a rebase crosses a release.
- On a rebase, `uv.lock` conflicts are resolved by taking the other side and
  running `uv lock`.
