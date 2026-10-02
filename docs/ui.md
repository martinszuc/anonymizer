# Review window: handbook

Everything needed to work on the review window (`anonymize-ui`) without
reading its history: what exists, how it connects to the core and the CLI,
the rules it must keep, how to add a feature end to end, and what comes next.
Keep this file current: update it in the same pull request as the change.

Visual design (tokens, components, box states) lives in
[`packages/ui/frontend/DESIGN.md`](../packages/ui/frontend/DESIGN.md);
package usage in [`packages/ui/README.md`](../packages/ui/README.md).

## Status (after adding missed words, 2026-10-02)

Works, for PDFs with a text layer and for scanned pages read by OCR:

- **Home screen** (no document open): a drop area with *Open PDF…*, the
  detection options that apply to the next PDF (language: Auto, the default,
  recognised from the text after reading, falling back to every rule when
  unclear; All; or one with its own rules; the name model on or off; marking
  repeats), the model's
  state (ready, not installed, files missing with the fetch command), and
  *Continue a saved review…*. The options live for the session; the model
  is on by default when it is ready.
- Open a PDF from the dialog, by **dropping it on the window** (on the home
  screen or over an open document), or `anonymize-ui file.pdf --lang cs
  [--ner]`. An **Opening screen** shows what is running now above a progress
  bar, page by page for OCR and detection ("3 of 12 pages"), and a sweeping
  bar while a model loads (the names model's first load takes about ten
  seconds; models stay loaded for the session), with the steps below.
- **Close the document** (the back chevron in the toolbar) returns home,
  asking first if decisions are unsaved.
- Reopen a saved review: pick the session file, then the original PDF (a
  session stores a fingerprint, not a path).
- Every page rendered, proposed redactions drawn over it. **Review mode**
  (default) keeps the covered text readable; **preview mode** (eye button,
  Cmd/Ctrl+Y) draws the output's opaque black boxes.
- Click a box or a row switch to toggle redact / keep; hover shows a popover.
  The locate toggle in the toolbar (L) makes a click on a box only select it and
  find its row in the list, so the row's switch is the one way to decide.
- Sidebar: counts, findings grouped by type, a dot on items not yet reviewed,
  arrow keys and Space. Identical findings of a type (case and spacing ignored)
  are one row with a count and one switch for all of them (`set_reviews`);
  opened (chevron or →), each occurrence has its own switch, and a group decided
  both ways shows a mixed switch whose click redacts everything. Clicking a group
  row steps through its occurrences on the page.
- **Search, sort and filter** above the list (`review.findingSections`, one
  pure function the list, the keyboard and *Keep* share). Search matches the
  found text ignoring case and diacritics ("novak" finds "Novák"). Sort: Type
  (sections by type, reading order; the default), least or most certain first,
  most repeated first, page order, A–Z; any order but Type is one list unless
  *Sections by type* is ticked, and its rows name their type. A group of repeats
  is one row in every order, scored by its text's best evidence (the highest
  model score among identical findings; a rule's or the reviewer's finding has
  no score and sorts last). Filter: decision (undecided, redacted, kept), found
  by (rules, model, repeats, added: words and regions the reviewer added), model score below 40–70 %. While anything is
  filtered, boxes outside the filter are dimmed on the page (review mode only),
  the count reads "N of M", and *Keep N* keeps the undecided findings shown,
  with Undo on the toast; decisions already made are left alone. With nothing
  filtered, a hint offers *Show them* for findings scored below 50 %. The order
  lasts the session; the filter is cleared when another document opens.
- A finding in hidden data (a link, metadata) is locked,
  *Always removed*: export clears it with the hidden item, so there is nothing
  to decide. The *Hidden* tab lists every hidden item with what it is, what
  export does with it and the findings it contains; selecting one outlines it
  on its page. A file with attachments gets a warning: their contents are
  never opened or checked.
- **Export** (Cmd/Ctrl+E, the primary toolbar action): save dialog (default
  `<name>-redacted.pdf`), written through core's `export_redacted`, so the
  file exists only if the leak check passed. A sheet asks for consent first
  when pages have no text layer; a result sheet shows the counts and "Leak
  check: Passed", or "Nothing was written" with the leaks.
- **Add a missed word or phrase**: in review mode, drag across words on the
  page (as text is selected in any PDF viewer; the cursor is a text cursor
  over words) or double-click one word. A drag may start on a box, so a
  detected first name can be extended over a missed surname; a click without
  a drag still toggles the box. A popover asks what it is (name, address,
  email, phone, ID number, other; keys 1–6, guessed from the text: `@` →
  email, digits → ID number or, with a leading `+`, phone, letters and digits
  → address, else name); Return adds, Escape cancels. The selection is
  widened to whole words in the core and trimmed of edge punctuation
  (`Novák,` → `Novák`; the box still covers the comma), added `manual` and
  `confirmed`, and its other occurrences are proposed as repeats (exact text,
  whole words; not inflected forms) when the document was opened marking
  repeats. A toast offers Undo; Cmd/Ctrl+Z removes the last item added
  (word or region); × on its row or Delete removes it with the repeats only
  it explained. Text already marked for redaction is refused; overlapping a
  finding partly, or text inside a kept one, is allowed (the union of boxes is
  removed). Works on OCR'd pages with OCR's words. A footer under the list
  says how.
- **Draw a region** over a photo, signature or stamp: the region tool (R) or
  holding Alt, then drag. The region is hatched in review mode, black in
  preview; a click selects it, Delete (or × in its sidebar row) removes it,
  Cmd/Ctrl+Z removes the last one drawn since the document opened. Regions are
  numbered in drawing order on the page and in the sidebar ("Region 2"), and
  renumbered when one is removed. A region is saved in the session and removed
  with everything under it on export (text, the drawings it touches, image
  pixels); overlapping regions are fine.
- **Models** (*Manage models…* on the home screen): a sheet listing what
  each feature needs (names and addresses: GLiNER and its tokenizer; scanned
  pages: OnnxTR's two models) with size, licence, languages, source and
  whether the files are stored, and a *Download* per feature. Files come from
  the catalog's official URLs, stream with a progress bar and are kept only
  if their checksums match (`resources.fetch_with_requirements`); both features
  can download at once, since they share no model. When one finishes, its
  feature's switch turns on. The sheet shows the folder models are stored in;
  *Change…* picks another in a folder dialog, kept in a settings file for later
  runs (`resources.location`, which the CLI and the benchmark follow too); files
  already there are not moved, models loaded from the old folder are dropped, and
  a feature whose models the new folder lacks turns off. A missing
  Python package is shown with its `uv sync --group …` command: the window
  never installs packages, as nothing but a model download may use the network.
- **Scanned pages**: the home screen's *Scanned pages* switch (on when the
  OCR engine is ready, with the same three states as the model) reads pages
  without a usable text layer with OnnxTR on open. Such a page shows a quiet
  "read by OCR" note; its boxes are OCR's, grown by a margin. Export passes
  the engine to the leak check, which re-reads the redacted page, and asks
  for consent only for scans OCR did not read (they keep the warning). A
  saved review of scans reopens with the engine it names (`ocr_engine` in
  the session), loading it first.
- Zoom (fit width by default, Cmd/Ctrl +/−/0), save the review, toasts for
  errors, light and dark mode, reduced motion respected.

Verified: macOS (real window driven from Python, see *Verifying the real
window*). Linux and Windows: the *Window tour* workflow opens the window and
photographs it on every run (see *Window tour*); its first runs are the first
time the window opens there.

Not yet: resizing a box, changing options on an open
document, remembered preferences, choosing an OCR engine (one is offered).
See *Backlog*.

## Architecture

```
anonymizer.core  (ingest, detect, session, redact)
      │  Python calls
anonymizer/ui/api.py     ReviewApi: plain JSON in and out, no pywebview import,
      │                  takes file paths, never reached by the page directly
anonymizer/ui/app.py     WindowApi: the only object the page sees; wraps a
      │                  private ReviewApi, asks for paths in native dialogs;
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
| `frontend/src/selection.ts` | Pure word-selection rules (hit test, nearest word, range, line highlight, type guess). Unit-tested in `selection.test.ts`. |
| `frontend/src/pageWords.ts` | Page word cache per document, for selecting missed text. |
| `frontend/src/demo.ts` | Synthetic stand-in for Python, development only (excluded from builds). |
| `frontend/src/styles/tokens.css`, `app.css` | Tokens and component styles; see `DESIGN.md`. |
| `tests/ui/test_api.py`, `tests/ui/test_app.py` | Python side, with pywebview stood in. |
| `frontend/src/review.test.ts` | vitest for `review.ts`. |

### The payload contract

`ReviewApi.document()` returns, and `types.ts` mirrors:

```
DocumentInfo { name, language, language_recognised, pages: PageInfo[], entities: EntityInfo[], surfaces: SurfaceInfo[] }
                # language: what detection ran with, null = every rule; language_recognised: from the text, not chosen
FeatureModels { feature, title, installed, install_command, missing_bytes,
                models: { id, name, uses, licence, languages, source, version, size,
                          state: present | partial | absent }[] }   # requirements first
PageInfo     { index, width, height, has_text_layer, raster_dpi }  # points; raster_dpi null unless OCR read it
EntityInfo   { id, type, source, score, review, page_index, surface_id,
               text, is_region, boxes: [x0, y0, x1, y1][] }        # points, top-left origin
WordInfo     { start, end, text, box: [x0, y0, x1, y1] }          # offsets into the page text
SurfaceInfo  { id, kind, value, page_index, box | null }
```

`ReviewApi.export()` returns `ExportResult { written, name, redacted, regions,
kept, not_reviewed, hidden_removed, pages_without_text: number[] (1-based scans OCR did not read),
leaks: { layer, where, page: number | null (1-based), text }[] }`; nothing was
written unless `written`.

Methods the page calls (all return promises in JS):

| Method | Returns | Notes |
|---|---|---|
| `status()` | `AppStatus` | version, languages with their own rules, `models_folder`, the states of the model and of OCR (`ocr: {engine, state, missing}`); loads neither |
| `choose_models_folder()` | `AppStatus \| null` | folder dialog; stores models there from now on (settings file); null = cancelled; rejects while a download runs |
| `models()` | `FeatureModels[]` | each feature's models and whether they are stored; nothing is hashed |
| `download_models(feature)` | `FeatureModels[]` | `names` or `ocr`; the page names a feature, never a URL or catalog id; progress as `anonymizer:download`; rejects while one of its models is already downloading or when a checksum fails |
| `current_document()` | `DocumentInfo \| null` | on start: a PDF given on the command line |
| `choose_pdf(options)` | `DocumentInfo \| null` | options `{language, propagate, use_model, use_ocr}`, checked in Python (`language`: a code, `"auto"` or null); null = cancelled |
| `open_dropped(options)` | `DocumentInfo \| null` | opens the PDF Python kept from the last drop; null if none |
| `close_document()` | `None` | forgets the document, window title back to "Anonymizer" |
| `add_region(page_index, x0, y0, x1, y1)` | `EntityInfo` | points, corners in any order; clipped to the page; `manual`, `confirmed` |
| `remove_entity(entity_id)` | `string[]` | only `manual` items; a detected item is rejected instead. Returns the ids removed: the item's, then its repeats (`propagated`, not confirmed) when no other finding marks the same text (`pipeline.remove_finding`) |
| `page_words(index)` | `WordInfo[]` | a page's words in reading order (OCR's on a page OCR read); fetched once per page when it nears the viewport |
| `add_finding(page_index, start, end, type)` | `EntityInfo[]` | a selection by word offsets, widened to whole words (`pipeline.add_finding`); the finding first, then its repeats; refuses a non-integer, a region type, text already marked for redaction |
| `export_as(allow_pages_without_text)` | `ExportResult \| null` | save dialog; null = cancelled; raises (rejects) when scans OCR did not read remain and consent is false |
| `choose_session()` | `DocumentInfo \| null` | asks for session, then PDF; reads it with the OCR engine the session names |
| `save_session_as()` | `bool` | false = cancelled |
| `page_image(index, dpi)` | `data:` PNG URL | dpi clamped to 36..400 in Python |
| `set_review(entity_id, state)` | `EntityInfo` | `pending` / `confirmed` / `rejected` |
| `set_reviews(entity_ids, state)` | `EntityInfo[]` | one decision for several entities (a group of repeats); nothing changes unless every id and the state are valid |

A change to a payload or method touches four places: `api.py` (and its test),
`types.ts`, `bridge.ts`, `demo.ts`. Payloads use the core's snake_case names.

Python tells the page about what it did not ask for with DOM events on
`window` (`WindowApi._notify`), each with plain-data `detail`:

| Event | Detail | When |
|---|---|---|
| `anonymizer:progress` | `{step, done, total}`: step `loading_ocr` / `reading` / `ocr` / `loading_model` / `detecting`; pages done and in all, both 0 for a step without pages | a step of opening a PDF (or a saved review) starts, and after each page OCR reads or detection scans |
| `anonymizer:download` | `{feature, received, total}` (bytes) | a download progresses, at most once per whole percent |
| `anonymizer:dropped` | the file's name | a PDF was dropped; the page calls `open_dropped` |
| `anonymizer:drop-refused` | the file's name | something other than a PDF was dropped |

**Drag and drop keeps the no-path rule.** Only pywebview's own drop handler
(bound in `WindowApi._watch_drops` whenever the page loads) sees a dropped
file's full path. Python keeps it privately and tells the page only the name;
the page then calls `open_dropped`, which takes options, never a path. The
page's own drag listeners only draw the highlight.

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
  The one file the window keeps between runs is the settings file, holding
  the models folder the reviewer chose and nothing about any document.
- **Logs hold no file names, paths or exception messages**, and document text
  only at DEBUG (`docs/logging.md`). A new `ReviewApi` method logs counts and
  ids; a new `WindowApi` method gets `@_logged`.
- **The PDF bytes are read once**; the document is loaded from them and
  pages render from them, never from the path again.
- **The page reaches only `WindowApi`'s public methods**, which equal the
  `ReviewBridge` interface in `bridge.ts` (`tests/ui/test_app.py` checks
  this). pywebview exposes every public attribute, inherited ones included,
  and the page runs with `'unsafe-eval'`; a method taking a file path from the
  page would let any injected script read or write files. Paths come from
  dialogs the reviewer answered.
- **`api.py` never imports pywebview.** Anything needing the window goes in
  `WindowApi` (`app.py`); pure logic goes in `ReviewApi` or the core.
- **Coordinates are PDF points, top-left origin**, as in the core. The page
  overlay is an SVG whose view box is the page size in points, so nothing in
  the frontend converts coordinates. Rotated pages already come rotated from
  ingest and from PyMuPDF's renderer.
- **Review semantics** (decided in `PLAN.md`): undecided (`pending`) items are
  redacted at export; hidden data is always removed, so it has no decision;
  toggling a pending item means *keep* (`rejected`), toggling back is an
  explicit *redact* (`confirmed`). In code: `review.isRemoved(entity)` says
  what export does, `review.isDecidable(entity)` whether there is a choice
  (not for hidden-data findings, not for regions, which are removed instead).
  Never offer a control that export ignores.
- **Logic belongs in the core, not the window.** If the CLI could use it
  (export, adding an entity, re-detection), write it in `core` with tests,
  then call it from `ReviewApi`. The window stays a thin client.
- **Styles use tokens** from `tokens.css` for colours, shadows, materials,
  type, spacing, radii, motion and any size two components share; add a
  token to `DESIGN.md` and `tokens.css` first. Only one component's own
  geometry (a switch track, a dot) is a literal in its rule. Motion respects
  `prefers-reduced-motion` (`MotionConfig reducedMotion="user"` in `App`).
- **Demo data is synthetic** and development-only (`import.meta.env.DEV`).

## Adding a feature end to end

1. **Core first**, if the behaviour is not window-specific: function in
   `packages/core`, Google-style docstring, tests in `tests/`.
2. **`ReviewApi` method** in `api.py`: plain-data result, core errors wrapped
   with `_as_review_error()`. Test it in `tests/ui/test_api.py` with PDFs from
   `tests/pdf_builders.py`.
3. **Expose it in `WindowApi`** (`app.py`): a forwarding method, or one that
   first asks for a path in a dialog. Positional parameters only (pywebview
   passes arguments positionally), and never a path parameter. Test it with
   `StandInWindow` in `tests/ui/test_app.py`.
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

One command installs the frontend, starts Vite and opens the real window with
hot reload (`--debug` on); closing the window stops Vite. Options after the task
name go to `anonymize-ui`; `--built` builds the page once and opens that instead.

```sh
uv run poe dev
uv run poe dev some.pdf --lang cs --ner
uv run poe dev --built
```

The same steps by hand:

```sh
cd packages/ui/frontend && npm ci
npm run dev                  # http://127.0.0.1:5173 with the demo document
uv run anonymize-ui --dev-server http://127.0.0.1:5173 --debug   # real window, hot reload
npm run build && uv run anonymize-ui some.pdf --lang cs          # real window, built page
uv run anonymize-ui some.pdf --log-level info --log-file run.log # milestones, kept in a file
```

`--debug` is the web inspector (right-click → Inspect Element, or F12 where the
platform has it; it does not open on its own) and debug logging together: every step of
opening, detecting and exporting, and every word found with its rule or model,
on stderr. The log holds document text; INFO and above never do, and no file
exists unless `--log-file` names one. Every page call is logged by `_logged` in
`app.py` (a refusal is a warning, anything else an error; never the message).
How to log from a new method: [`docs/logging.md`](logging.md).

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
from anonymizer.ui.api import ReviewApi
from anonymizer.ui.app import STATIC_INDEX, WindowApi

review = ReviewApi()
review.open_pdf(sys.argv[1], "cs")
api = WindowApi(review)
window = webview.create_window("check", url=str(STATIC_INDEX), js_api=api)
api._attach(window)


def probe():
    time.sleep(3)
    print(window.evaluate_js("document.querySelectorAll('.redaction').length"))
    window.evaluate_js(
        "document.querySelector('.redaction')"
        ".dispatchEvent(new MouseEvent('click', {bubbles: true}))"
    )
    time.sleep(1)
    print([e["review"] for e in review.document()["entities"]])
    window.destroy()


webview.start(probe, private_mode=True)
```

Use a synthetic PDF (build one with `tests/pdf_builders.py`), never a real
document.

Native file dialogs cannot be scripted. To drive a feature behind one (open,
save, export), subclass `WindowApi` in the script and override `_ask` to
return a fixed path; everything else (the click in WebKit, the bridge, the
core, the sheet) still runs for real.

### Window tour (CI)

`scripts/ui_tour.py` opens the real window on a synthetic letter and performs
the basic tasks: home screen, choose a language, open a PDF, keep one finding, the *Hidden* tab,
preview, export. Each step is asserted and followed by a screenshot of the
*whole screen* (WebP), so the window appears with the desktop's own bars. It
ends by re-reading the exported PDF and failing if a planted value survived.
The page is driven with `evaluate_js` (no synthetic mouse), and file dialogs
are answered by a `WindowApi` subclass.

The `Window tour` workflow (`.github/workflows/window-tour.yml`) runs it on
Ubuntu 24.04, Debian 12 and Fedora 42 (containers started by
`scripts/tour-linux.sh`: Xvfb, xfwm4, xfce4-panel, Qt WebEngine from PyPI, so
Linux is checked with the Qt backend, not GTK), and on the macOS and Windows
runners. Artifacts: `window-tour-<platform>` per platform and `window-tour-all`
with every platform side by side; a failure adds `NN-failure.webp`.

The script refuses to run outside CI without `--allow-desktop`, because it
photographs everything on the screen. To try it locally, use a virtual
display (the script in a Linux container), not your desktop.

## Connections to the rest of the project

| Core / CLI piece | How the window uses it, or will |
|---|---|
| `ingest.read_pdf`, `document_from_bytes` | `open_pdf`: the file is read once; the document is loaded from those bytes and pages render from them |
| `pipeline.build_detector(language, model=...)`, `run_detection` | detection on open, with the options from the home screen |
| `detect.load_gliner_detector(root)` | the name model, loaded on first use from `--resource-root` and kept for the session |
| `detect.gliner_installed`, `missing_gliner_files` | the model's state on the home screen, without loading it |
| `session.save_session` / `apply_session` | save and reopen; same files as `anonymize detect` / `redact --session` |
| `Document.adjust_span(entity_id, start, end)` | **not wired**: resizing a box to other words |
| `Document.add_region`, `Document.remove_entity` | drawing and removing a region |
| `pipeline.add_finding` (`Document.add_span`, `propagate_occurrences(document, marked)`), `pipeline.remove_finding` | adding a missed word with its repeats, and removing it with the repeats only it explained |
| `redact.export_redacted` | export: temporary file, `redact_pdf`, `find_leaks`, rename only when clean; the CLI's `redact` uses the same function |
| `ingest.load_ocr_engine`, `ocr_engine_installed`, `missing_ocr_files` | OCR on open, loaded once per session; its state on the home screen without loading it |
| `ingest.pages_needing_ocr`, `Page.raster_dpi` | the page warning and export consent for scans OCR did not read; the "read by OCR" note |
| `session.session_ocr_engine` | reopening a review of scans with the engine that read them |
| `resources.load_catalog`, `fetch_with_requirements`, `resource_status` | the Models sheet: listing, verified download, stored state |
| CLI `inspect` (HTML report) | independent; same box geometry, useful to compare against |

## Backlog

In suggested order. Each item names where it plugs in.

1. **Done.** ~~Add a missed word or phrase.~~ Still open: inflected repeats
   ("Novák" added, "Nováka" not proposed; needs a morphological analyser), and
   the open document's *mark repeats* option is not stored in a session, so a
   reopened review always proposes repeats of added text.
2. **Resize a box** to fewer or more words → `Document.adjust_span`.
3. **Change options on an open document:** re-run detection with another
   language or with the model, carrying decisions over by span. Opening
   options already live on the home screen.
4. **Remembered preferences:** the home screen's options kept between runs
   in a small settings file (no personal data), and an **opt-in** list of
   recent files, off by default: a file name can be personal data.
5. **Unsaved changes on close:** pywebview `confirm_close` or a closing
   event tied to the `dirty` flag; today only opening another document asks.
6. **Undo / redo** of decisions (Cmd/Ctrl+Z), kept in the frontend as a
   stack of `set_review` calls.
7. **Models sheet, next steps:** cancel a running download; verify stored
   files on request (`verify_resource`, hashing takes seconds per GB); choose
   between OCR engines once a second one is in the catalog.
8. **OCR quality in review:** show OCR's confidence per word and flag
    low-confidence words (an `@` read as `(m` hides an email from the rules),
    and offer a second engine once RapidOCR or EasyOCR is in the catalog.
9. **Label mode preview** once labels exist (M5): preview draws `[NAME]`
    instead of black boxes.
10. **Accessibility pass:** boxes are not keyboard-reachable (the list is the
    keyboard path); run a WCAG review of both themes.
11. **Packaging (M9):** PyInstaller bundle per OS; test Windows (WebView2)
    and Linux (GTK or Qt backend) by hand.
12. **Large documents:** virtualize the page list and the sidebar beyond a
    few hundred pages or entities.

## Open issues from manual testing (2026-10-02)

Found by hand in the review window on real documents and on a set of unrelated
Czech documents (kept outside the repository). Items marked **Done** are fixed and
stay listed so the numbering holds; the rest are open. Items marked **Explain** need an explanation for the maintainer before any
change; **Decide** items need a product decision first. Related older items are in
*Backlog* (undo/redo, models sheet, packaging, OCR quality).

**Evidence.** A local log, `debug-log.log` in the repository root, records a run on
documents with names and Czech text: the repeated occurrences and the ordinary Czech
words marked as personal data (items 11 and 12). It is git-ignored (`*.log`) and may
hold text from real documents. A session that works on those items reads it from disk
to find which detector produced each hit, and reports counts, detector sources and
entity types, never the words, names or sentences themselves. It is not copied into
the repository, a test, a fixture or a commit message.

### Loading a document

1. **Done.** ~~Remove the once-per-session hint strings~~ shown while a PDF loads.
2. **Done.** ~~Progress bar for detection.~~ OCR and detection run page by page and
   report "N of M pages" (`PageProgress` in the core); loading a model is one call and
   shows an indeterminate bar.
3. **Done.** ~~Status line above the progress bar.~~

### Models and storage

4. **Done.** ~~Download several models at once.~~ Features that share no model download
   side by side; a second download of the same models is refused.
5. **Done.** ~~Choose where models are stored.~~ *Manage models… → Change…*; the
   choice is kept in a settings file. Without one, models live in `./models` when the
   working directory has it, else in a per-user folder; the CLI and the benchmark
   resolve the same way (`resources.resolve_resource_root`).

### Formats

6. **Support document types beyond PDF** (images, Office and text formats). **Decided
   (2026-10-02): PDF only for now**; other formats are left for a later semester. When
   taken up: images are the cheapest (wrapped in a PDF, they take the OCR path and its
   leak check), Office files the most expensive (a converter or a native reader with its
   own hidden-data cover: comments, tracked changes, metadata).

### Review window behaviour

7. **Done.** ~~The detail popup does not update live.~~ It reads the entity by id on every
   render.
8. **Done.** ~~Clicking a box both selects and toggles it.~~ Decided: a click still
   toggles by default; the toolbar's locate toggle (L) makes it only select and find
   the item.
9. **Done** for regions and added words: Cmd/Ctrl+Z removes the last item added since
   the document opened. Undo of decisions stays in *Backlog*.
10. **Done.** ~~Number the drawn regions.~~ Numbered in drawing order on the page and in
    the list; removing one closes the gap.

### Too many harmless detections

11. **Many ordinary Czech words are marked as personal data** in unrelated documents, and
    the same word is repeated many times in the list. If a word is rejected and occurs 30
    times, rejecting it 30 times is not acceptable. Needed: identical occurrences grouped
    in the left panel (one row with a count, decided together, expandable), or a switch
    between grouped and individual view. Find out first which detector produces the
    false positives (rules, names model, or OCR text) and in which documents.
    **Done** for the list: grouped by default, decided together, expandable. What the
    local log shows (one 2-page document, `language` All): 31 findings, about 21 from the
    names model scoring mostly 0.34–0.54 against a 0.3 threshold, 8 from rules, 2
    repeats. **Measured and reduced (2026-10-02):** the benchmark now has documents
    without personal data; nearly all false alarms there were capitalised role nouns
    ("Kupující", "Žadatel"), which no threshold removes without losing names. The name
    model is now also asked for organizations, and its person spans pass
    `detect.NamesOnly`: false alarms 33 → 4 with every name still found
    (`docs/findings.md` → *False alarms from the name model*). Still open: a run on the
    unrelated documents to confirm it there.
12. **Names, titles and degrees.** **Explain:** which model finds Czech names (GLiNER via
    `--ner`, see the catalog) and what label set it is asked for. Academic titles and
    degrees (Ing., Mgr., doc., Ph.D., prof.) are often left unredacted; list the options
    (a label for titles, a rule next to a detected name, a prompt change) and what each
    costs in false positives. The OCR models also need more work: OCR errors turn up in
    the false positives above.
    **Done** for titles (option b): `detect.extend_with_titles` widens every person span
    over the titles before it and the degrees after it, as the last detection step. OCR
    quality stays open.

### Export

13. **Export refuses a copy because text is still readable, without saying where.**
    **Explain:** how the leak check decides this, which layers it has, and why a
    hand-drawn region on a text page can leave readable text behind. Then the window must
    name what was found (page, the text, which layer) and what to do about it, instead of
    a general failure. Today's behaviour on the leak result is in `ReviewApi` and the
    export sheet.
    **Partly done:** overlapping or nested regions no longer fail the region layer (each
    region's fill was reported as a drawing left inside the other), and the sheet numbers
    pages from 1 (`page` in the leak payload). Advice per layer is still open. Another
    cause found on the benchmark: a detected word whose inflected form was not detected
    ("Žadatel" found, "Žadatelem" not) is still in the page text, so the page-text layer
    refuses. Right for a surname; for a role noun, rejecting the finding clears it.

## Known gotchas

- pywebview exposes every public method and attribute of the `js_api`
  object to the page, inherited ones and those of nested objects included;
  keep everything else in underscore attributes (`_review`, `_window`).
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
- Pointer handlers keep their drag in a ref, not state: events can arrive
  before React re-renders, and a handler reading state sees the previous
  event's value. `setPointerCapture` is wrapped in try/catch; WebKit refuses it
  for synthetic pointers, which is how a probe script drives a drag.
- A word selection that ends over a box would also fire that box's click and
  toggle it; `PageView` swallows the one click after a drag (`onClickCapture`).
  The selection starts only after the pointer moves 4 px, so a click stays a click.
- `demo.ts` returns copies (`structuredClone`), as pywebview's JSON round trip
  does; returning its own objects let a mutation there change React state and
  duplicated a drawn region.
