# anonymizer-ui

Review window for `anonymizer-core`. Runs fully offline.

The window shows the original PDF page by page with the proposed redactions drawn
over it. The reviewer keeps or redacts each one and saves the decisions as a session
file, the same format `anonymize detect` writes and `anonymize redact --session` reads.

```sh
anonymize-ui [cv.pdf] [--lang cs] [--ner] [--ocr]
```

Scanned pages are read with OCR when the home screen's *Scanned pages* switch is
on (`--ocr` for a PDF given on the command line): install `uv sync --group
ocr-onnxtr` and fetch the models with
`uv run python scripts/download.py fetch onnxtr-parseq-multilingual-v1`.

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

To work on the frontend inside the real window with hot reload, keep `npm run dev`
running and start `anonymize-ui --dev-server http://127.0.0.1:5173 --debug`.

The built page carries a Content-Security-Policy (see `vite.config.ts`): its own
files only, page images as `data:` URLs, no connections. `'unsafe-eval'` stays
allowed because pywebview returns every API result to the page through `eval()`;
without it every call silently never resolves.
