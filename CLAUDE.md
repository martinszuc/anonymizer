# CLAUDE.md

Context for AI coding sessions in this repository. Read before making changes.

## Project

Local-only tool that detects and redacts personal data in scanned and electronic documents.
Pipeline: ingest (PDF text layer or OCR) → entity detection (rules + NER) → human review → redaction.
Part of a diploma thesis at FEKT VUT Brno. Roadmap and open decisions: `PLAN.md`
(untracked, local). Empirical findings from running the pipeline on real documents:
`docs/findings.md` — read it before assuming how PDFs behave.

The thesis core is a Czech/Slovak name-detection model trained in this repository and
compared with existing models on reserved test data (RQ6 in the untracked `RESEARCH.md`).
The current pipeline (rules + GLiNER zero-shot) is its baseline. OCR uses existing
engines and is not itself a research topic.

## Hard constraints

- **Offline only.** No code path may send document content or call a remote service for OCR or inference. Models load from local cache (`HF_HUB_OFFLINE=1`). Tests run with network access blocked. The only network access ever allowed is a model download the user starts explicitly, from the model's official source, verified against a stored checksum.
- **No real personal data.** Test fixtures, examples and training data are synthetic or from public benchmarks. Never commit datasets, model weights or generated documents.
- **True redaction.** Redacted content must be removed from the output file, not covered. Every redaction path needs a leakage test (re-extract the output, assert target strings are absent).
- **Logs are not a side channel.** INFO and above hold no document text, file names or
  paths; DEBUG may hold detected words, never names or paths; exception messages are never
  written; no log file exists unless `--log-file` names one. Rules for adding a record:
  `docs/logging.md`.
- **Unicode.** UTF-8 everywhere; normalize text to NFC at ingest. Czech/Slovak diacritics must survive round-trips.

## Architecture

```
packages/core/   library, no UI or CLI dependencies
  types.py       shared data contract (the data format every component exchanges)
  log.py         logging setup, safe formatter, `step` (see docs/logging.md)
  session.py     slim session files: a saved review
  pipeline.py    detection as every client runs it: build the detector, run it,
                 propagate occurrences
  ingest/        pdf.py (text layer), surfaces.py (non-text surfaces),
                 normalize.py (NFC, rotation), OCR engine adapters
  detect/        base.py (protocol, Match, RuleDetector, merge_entities),
                 document.py (pages + surfaces), propagate.py (other occurrences),
                 rule modules, NER backends
  resources/     catalog.toml (every model and dataset, pinned and
                 checksummed), catalog.py, fetch.py (verified download)
  redact/        pdf.py (blackbox), surfaces.py (clearing), canvas.py (content
                 outside the visible area), leakage.py (layered leak check,
                 layers listed in its docstring)
packages/cli/    thin command-line client
packages/ui/     review window: api.py (ReviewApi, plain data), app.py
                 (pywebview window), frontend/ (React, Vite, DESIGN.md)
benchmark/       synthetic documents as data, generator, scorer, pictures, charts
experiments/     evaluation harness: corpus loaders, systems via pipeline.py, cached
                 model output, scores with bootstrap CIs, results tables
scripts/         model and dataset download, synthetic mixed-format sample generator
data/            local corpora, git-ignored, never committed
```

What works and what does not yet: `README.md` → *Status* (and `docs/ui.md` →
*Status* for the review window). Keep counts and module details in the module
docstrings, not here; they go stale in two places.

- **Before changing the review window, read `docs/ui.md`**: its status, the
  payload contract, the rules it keeps, a recipe for adding a feature end to end,
  how it connects to core and CLI, and the backlog. Update it in the same PR.
- The review window's Python side is `ReviewApi` in `ui/api.py`: plain JSON in and
  out, no pywebview import, tested like any module. The page never calls it
  directly: `WindowApi` in `app.py` is the only object pywebview exposes, its
  public methods equal `ReviewBridge` in `bridge.ts`, and none takes a file path.
  The frontend lives in `packages/ui/frontend/` (React + TypeScript + Vite,
  `npm run check` / `npm test` / `npm run build`); its tokens and
  components are in `frontend/DESIGN.md`; colours, shadows and shared sizes are
  tokens, and only one component's own geometry is written as a literal.
  Pages are rendered by PyMuPDF and boxes drawn in an SVG whose view box is the
  page in points, so nothing converts coordinates in the browser. Keep
  `'unsafe-eval'` in the CSP: pywebview returns API results through `eval()`.

- Clients (CLI, review window, benchmark, experiments) never chain core steps themselves: they
  call `core/pipeline.py` (`build_detector`, `run_detection`) and export through
  `redact.export_redacted`, which leaves a copy only if the leak check passed. A
  step or option added there reaches all of them, and the benchmark measures
  what ships.
- Overlapping detections, within the rules and between detectors
  (`CombinedDetector`), go through `merge_entities`: a span entirely inside a
  stronger or longer one is dropped; a partial overlap, or a weaker span
  containing a stronger one, keeps both (dropping one would leave its remainder
  unredacted). Strength is entity-type priority first (checksum-backed
  identifiers beat free-form patterns; URLs beat everything, since anything
  overlapping a URL lies inside it), then span length. Add a type to
  `OVERLAP_PRIORITY` rather than special-casing a caller.
- GLiNER reads at most 384 of its own tokens (punctuation counts as one) and
  drops the rest with only a warning; `GlinerDetector` scans a page in
  overlapping windows counted in those tokens and widens spans to whole words. Its
  dependencies are the optional `ner` extra (`uv sync --group ner`); tests use a
  stand-in model, and the real one only runs under `@pytest.mark.model`.
- A model's person and address spans pass `detect.NamesOnly` (`roles.py`,
  applied by `build_detector`): lowercase edge words trimmed, spans of role
  nouns only ("Kupující", "Adult") dropped; address-field labels ("Post Code",
  "Telephone Number") trimmed from address spans, which are dropped when
  nothing else is left. Role nouns that are also surnames (Starosta, Žák,
  Child) stay off its lists; measure any change on the benchmark's documents
  without personal data and on the development corpora (`docs/findings.md`).

- Every model and dataset is an entry in `core/resources/catalog.toml`: official
  source, immutable version, licence, languages, and per file a URL, size and
  SHA-256. Add an entry there rather than downloading from code; a library that
  fetches its own weights (GLiNER's encoder tokenizer, OCR engines) must be given
  local paths instead.

- All components exchange data through `core/types.py`: `Document → Page → Word(bbox)` and `Document → Surface`, with `Entity` pointing at a page and optionally a surface. Change the contract deliberately; it is consumed by CLI, UI and serialized review files.
- OCR engines, detectors and redaction strategies sit behind interfaces. Add implementations, do not special-case callers.
- Structured identifiers (rodné číslo, bank accounts, IBAN, payment cards, IČO) are detected by format + checksum rules, not by ML.
- URLs are reported without a list of sites: a list of profile sites goes stale, so every URL is an entity and review rejects the harmless ones.
- Rules are **locale-scoped**: `detect.finders_for(language)` picks the set, locale-independent finders (email, IBAN, Luhn) always run, and an unknown language falls back to every rule. Register a new rule there rather than calling it directly. `auto` recognises the language from the page text (`core/language.py`, py3langid, offline) through `pipeline.resolve_language`, answering only languages with their own rules and otherwise none (every rule).
- A checksum is the strongest evidence available, but most non-Czech identifiers have none (US SSNs and phone numbers do not). Where a checksum is weak or absent, require a label from the document (as IČO does) instead of lowering the bar on digits alone.
- Coordinates are **PDF points, per page, origin top-left, y downward** (PyMuPDF's convention, so extraction needs no conversion). A rasterized page records `Page.raster_dpi`; pixels convert with `points = pixels * 72 / dpi` before entering a `BBox`.
- **The text layer is not the only place personal data hides.** Link annotations, document metadata and XMP, form field values, bookmarks, embedded files and a tagged PDF's structure tree all carry identifying data that never appears in `Page.text`, and clearing the visible words leaves them intact. Ingest lists them as `Document.surfaces`; an entity on one sets `surface_id` and its offsets refer to `Surface.value`. Redaction must clear surfaces whether or not an entity was found in them.
- Text offsets are **page-local into `Page.text`**. An entity carries its character span *and* one bbox per covered word, so a span crossing a line break yields several boxes instead of one covering the gap. A **region** entity (a box a reviewer drew over a photo, signature or stamp) has no span and exactly one box; use `Entity.span`, which refuses a region, rather than reading `start`/`end` directly.
- A document is tied to its source by **fingerprint** (SHA-256), never by file name, which can itself be personal data. Redaction and session loading refuse a different file. Read a source file once (`document_from_bytes`, `read_verified`) and work from those bytes, so it cannot change between check and use. Surface ids are derived from kind, page and reference, so they are stable across loads.
- Detection is **recall-first**: a missed entity leaks, a false positive is removed during review. Prefer a rule that over-matches to one that depends on a register that can go stale (this is why bank codes are not validated against the ČNB list).
- Czech and Slovak are the primary target for name detection (NER); English is covered by the rules and serves as a secondary check. Keep language a configuration value, never hardcoded.

## Stack

Python ≥ 3.12 (CI: 3.12, 3.13 on macOS, Linux, Windows) · uv workspace · ruff · pyright (standard) · pytest.

```sh
uv sync                    # install
uv run poe check           # lint, format check, pyright, pytest with coverage floors
uv run poe fix             # ruff check --fix, ruff format
uv run poe test            # pytest only
uv run poe dev             # review window with Vite hot reload (installs the frontend, --built builds it)
```

`poe check` must pass before committing; it runs every step and fails at the end, so one
run lists all problems. Tasks live in `[tool.poe.tasks]` and CI calls the same tasks, so
thresholds (93 % overall coverage, 95 % for `redact/`) are defined once in `pyproject.toml`.
Ruff runs from `uv.lock` everywhere; pre-commit does not pin its own ruff version.

## Code style

- English only: identifiers, comments, docstrings, commit messages, docs.
- Names describe purpose (`bank_code`, `find_birth_numbers`), not type or position (`data`, `tmp`, `process2`).
- Type hints on all function signatures.
- Comments explain *why* or non-obvious logic (checksum rules, coordinate transforms). No comments restating the code.
- Docstrings: Google style with `Args`/`Returns`/`Raises` on the public API of `core`; a one-line docstring on internal functions only when the name is not enough.
- Small functions, early returns, no dead code or commented-out blocks.
- Documentation is concise and technical. No filler, no marketing tone.

## Testing

- Every detector gets valid **and** invalid cases, including separator and whitespace variants.
- Fixtures are synthetic: PDFs are generated by the tests (`tests/pdf_builders.py`); a hand-written fixture goes in `tests/fixtures/`, the only place the pre-commit hook accepts documents. Checksum-bearing test values (rodná čísla, account numbers, IBANs) are computed independently, never by asking the validator under test whether it likes its own output.
- Tests needing a downloaded model are marked `@pytest.mark.model` and skipped when the model is absent.
- Tests needing a downloaded corpus are marked `@pytest.mark.dataset` and skipped when the corpus is absent. The unmarked suite must pass with no network and no `data/` directory, because that is all CI has.
- The benchmark (`benchmark/`, `python -m benchmark run`) scores the pipeline on synthetic documents whose personal items are marked inline (`[[person:Jan Novák]]`). Add documents there, not PDFs; every value is invented, and checksum-bearing ones are computed independently. Its GitHub workflow is the one place CI fetches a model: started by hand or by a release, from the official source, checked against the catalog checksum.
- Datasets are never test fixtures, and a dataset containing real personal data is never used in tests at all. Measurement belongs in `experiments/` (`python -m experiments run --config …`), not in `pytest`.
- Training belongs in `experiments/` as well: one command from a config, base models and corpora from the catalog, seeded, with the machine recorded. It reads train splits, tunes on dev, and never opens a test split; the final table reads test data once (`stage = "final"`). Synthetic training data must not reuse the templates of a held-out synthetic test set. Trained weights go to `models/` and are never committed: trained on CNEC or UNER, they carry real public names.

## Lessons from earlier mistakes

Each of these cost a bug or a wrong claim once.

- **Bugs sit where correct parts meet**: surfaces and page text, the leak check and
  review decisions, rules and the model, CLI options and each command. When
  adding a detector, re-read the code that combines detectors; when adding a
  review decision, check what the leak check makes of it. Test the combinations
  in one small PDF (repeated text with mixed decisions, an address next to an
  identifier), not only each part alone.
- **No step may drop a span that reaches beyond what it keeps**; a partial match
  is a leak, not a near miss. Detector tests assert the whole value is matched in
  running text, not that something matched.
- **A passing leak check is not evidence of anonymization.** It proves the
  *detected* items are gone; what detection missed is measured by the benchmark.
- **PDF behaviour is real only after save and reload.** Every probe needs a control
  case, and the fixture's starting state is checked before reading what changed.
- **A test for one layer of a layered check** plants a leak only that layer can see.
- **Synthetic fixtures do not reproduce producer quirks** (react-pdf stores metadata
  as separate objects). Run new ingest code on a real sample and compare with an
  independent reading; a scan prints structure (kinds, keys, lengths), never
  values, and nothing is claimed about a real document without one.
- **After adding an optional dependency**, verify in an environment synced like CI
  (`uv sync --locked --all-packages`, then `uv run poe check`).
- **Numbers in docs come from the results file**, checked before they are written.

## Dependencies and data

- Adding a dependency is fine; justify it in the commit message and prefer well-maintained packages with permissive licenses. Flag AGPL or non-commercial licenses.
- Ask before downloading models or datasets.

## Git

- Work on feature branches (`feat/iban-detector`); never commit to `main`. The maintainer reviews and merges.
- Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`, `ci:`.
- Commit with `git commit -s -S`.
- One logical change per commit.
- Releases are automated by release-please (`.github/workflows/release.yml`): it
  derives the next version from the Conventional Commits on `main`, writes the
  changelog from the merged pull requests (one line per PR title, so PR titles
  must be Conventional too), and keeps a `chore: release X.Y.Z` PR open. Merging it tags the release and attaches the built packages. Never edit
  versions by hand; `version.txt` and the three `__version__` lines (marked
  `x-release-please-version`) are bumped together. Pre-1.0, `feat` bumps the
  minor version and `fix` the patch.

## Out of scope for AI sessions

Thesis text (analysis, literature review, conclusions) is written by the author outside this repository. Repository docs describe the software only.
