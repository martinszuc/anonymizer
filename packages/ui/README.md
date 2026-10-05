# anonymizer-ui

Review window for `anonymizer-core`. Runs fully offline.

The window shows the original PDF page by page with the proposed redactions drawn
over it. The reviewer keeps or redacts each one and saves the decisions as a session
file, the same format `anonymize detect` writes and `anonymize redact --session` reads.

```sh
anonymize-ui [cv.pdf] [--lang cs] [--ner] [--ocr [onnxtr|kraken]]
```

Scanned pages are read with OCR when the home screen's *Scanned pages* switch is
on, by the engine chosen under it: OnnxTR (the default, print only) or kraken
(also handwriting, about four times slower). `--ocr` reads a PDF given on the
command line, with OnnxTR unless an engine is named. The packages come from
`uv sync --group ner --group ocr-onnxtr --group ocr-kraken` (kraken installs on
macOS and Linux x86-64 only); the models are downloaded from the window
(*Manage models…*, each file checked against the catalog's checksum) or with
`uv run python scripts/download.py fetch <id>`. Models go to `models/` under
`--resource-root`, by default the folder chosen in the review window (*Manage models… → Change…*), else
`./models` if the working directory has one (a checkout of this repository),
else a per-user folder (`~/Library/Application Support/anonymizer` on macOS,
`%LOCALAPPDATA%/anonymizer` on Windows, `~/.local/share/anonymizer` on Linux). The Models sheet shows the folder and
changes it; the choice is kept for later runs, and files already downloaded are
not moved.

Working on the window: start with [`docs/ui.md`](../../docs/ui.md) (status, contract,
rules, how to add a feature, backlog).

## Layout

- `src/anonymizer/ui/api.py`: `ReviewApi`, everything the window asks of the core,
  as plain JSON data. No pywebview import; tested on its own.
- `src/anonymizer/ui/app.py`: the window (pywebview); `WindowApi`, the only
  calls the page can make, with paths chosen in native file dialogs; the
  `anonymize-ui` command.
- `frontend/`: React + TypeScript, built by Vite into `src/anonymizer/ui/static/`
  (git-ignored, bundled into the wheel). `frontend/DESIGN.md` holds the design
  tokens and components.

## Frontend development

```sh
cd packages/ui/frontend
npm ci
npm run dev        # http://127.0.0.1:5173, a synthetic demo document in a plain browser
npm run check      # type check
npm test           # unit tests (vitest)
npm run build      # into ../src/anonymizer/ui/static
```

To work on the frontend inside the real window with hot reload, run `uv run poe dev`
from the repository root: it installs the frontend dependencies when stale, starts
Vite, opens the window against it with `--debug`, and stops Vite when the window
closes. Options go to `anonymize-ui` (`uv run poe dev some.pdf --lang cs`); `--built`
builds the page once and opens that. By hand: keep `npm run dev` running and start
`anonymize-ui --dev-server http://127.0.0.1:5173 --debug`.
`--debug` also turns on debug logging to stderr, which holds document text;
`--log-level` and `--log-file` are described in [`docs/logging.md`](../../docs/logging.md).

The built page carries a Content-Security-Policy (see `vite.config.ts`): its own
files only, page images as `data:` URLs, no connections. `'unsafe-eval'` stays
allowed because pywebview returns every API result to the page through `eval()`;
without it every call silently never resolves.
