# anonymizer

[![Checks](https://github.com/martinszuc/anonymizer/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/martinszuc/anonymizer/actions/workflows/ci.yml)
[![Window tour](https://github.com/martinszuc/anonymizer/actions/workflows/window-tour.yml/badge.svg?branch=main)](https://github.com/martinszuc/anonymizer/actions/workflows/window-tour.yml)

Local-only tool that detects and redacts personal data in scanned and electronic documents.

Pipeline: ingest (PDF text layer or OCR) → entity detection (rules + NER) → human review → redaction.
Part of a diploma thesis at FEKT VUT Brno.

**No document content leaves the machine.** No code path may call a remote service for OCR or
inference; models load from a local cache and the test suite fails on any outbound connection.

## Status

- **PDFs with a text layer:** text and hidden-data extraction; rule-based
  detection (Czech and Slovak identifiers, IBAN, cards, email, phone, URL,
  labelled dates of birth, postal addresses) scoped to the document's
  language, which can be recognised from the text (`--lang auto`, the
  window's default); blackbox redaction and a leak check on the output.
- **Names and addresses:** an optional name model, GLiNER (`--ner`) or another
  catalog name model such as NameTag 3 (`--name-model`); person spans are
  widened over the academic titles beside them.
- **Review:** through session files, or in the review window: a home screen
  with the detection options, models downloaded from the window and checked
  against their checksums, open or drop a PDF or an image, toggle each item,
  add a missed word by selecting it, draw regions, save the session, export.
- **Scanned pages:** read through an OCR engine interface; redaction
  overwrites the pixels under each box and removes the page's text layer, and
  the leak check re-reads the redacted page with the same engine. Two engines,
  both optional and offered by the CLI (`--ocr onnxtr|kraken`) and the review
  window (*Scanned pages*, then the engine): OnnxTR with a multilingual
  recognizer for print, the window's default, and kraken with the PP-OCRv6
  line recognizer, which also reads handwriting. Searchable scans (a picture
  under an invisible text layer) are redacted through that layer; see
  `docs/findings.md`.
- **Images** (JPEG, PNG, TIFF) are read as scanned pages: wrapped into a PDF
  from their pixels only, upright by their EXIF orientation, and redacted into
  a PDF. Photos are read as they are taken: no perspective correction or
  dewarping.
- **Measurement:** detection quality is measured on development data only so
  far (`experiments/results/`, the benchmark for each release). A
  Czech/Slovak name model is trained in this repository (`python -m
  experiments train`, fine-tuned GLiNER): three losses, and three weights of
  the recall-weighted loss, each trained with three seeds and scored on
  development data (`experiments/results/rq6-*`). The comparison with
  existing models on reserved test data has not been run.
- **Not yet:** Office and text formats, HEIC images, a per-OS bundle of the
  review window (see *Installing and releases*).

## Quick start

Requires [uv](https://docs.astral.sh/uv/). No real document is needed: the
generator writes a four-page synthetic PDF (every value invented) into the
git-ignored `data/samples/`:

```sh
uv sync
uv run python scripts/make_mixed_sample.py        # data/samples/mixed-synthetic.pdf
uv run anonymize inspect data/samples/mixed-synthetic.pdf -o inspect.html --lang cs
uv run anonymize redact data/samples/mixed-synthetic.pdf -o redacted.pdf --lang cs --allow-pages-without-text
```

| Page | Content | Without `--ocr` |
| --- | --- | --- |
| 1 | typed form, link, form field, bookmarks, metadata, attachment | detected and redacted, hidden items cleared |
| 2 | scanned form (skewed, speckled, no text layer) | not read |
| 3 | handwriting-font values, scanned | not read |
| 4 | typed text beside a scanned stamp | typed text redacted; the stamp needs a drawn region |

Without `--allow-pages-without-text` the redaction stops at pages 2 and 3 on purpose:
their content could not be redacted, so the tool refuses rather than hand back a
copy that looks safe; with `--ocr` (see *Usage*) they are read and redacted. The
handwriting font is a macOS system font; elsewhere page 3 falls back to an
italic serif, which is not handwriting at all. A font only imitates handwriting
and tests the plumbing, not recognition quality. A real handwritten scan
belongs in `data/samples/` and is never committed or used as a fixture.
`tests/test_mixed_sample.py` builds the same sample and runs these steps in CI,
so the refusal and the clearing of hidden items cannot regress unnoticed.

## Usage

```sh
uv run anonymize detect cv.pdf -o review.json --lang cs --show
uv run anonymize redact cv.pdf -o cv-redacted.pdf --session review.json
uv run anonymize inspect cv.pdf -o cv.html --lang cs   # pages with the found items drawn on
uv run anonymize redact photo.jpg -o photo-redacted.pdf --ocr onnxtr --lang cs
```

A photo or a scanned image (JPEG, PNG or TIFF; not HEIC, so export iPhone
photos as JPEG) is accepted wherever a PDF is. It is turned upright by its EXIF
orientation, wrapped into a PDF holding only its pixels (no EXIF, GPS or other
metadata reaches the output), read with OCR, which an image always needs, and
redacted into a PDF. A multi-page TIFF gives one page per frame.

See [`packages/cli/README.md`](packages/cli/README.md) for every command
(including `check`), the OCR engines and reviewing without a UI.

The review window needs its frontend built once (Node 22). It opens on a home
screen: drop a PDF or an image or open one, with the language and the name model chosen
there (`--resource-root` says where `models/` is, as for the CLI; see *Models and
datasets* for the default):

```sh
npm --prefix packages/ui/frontend ci
npm --prefix packages/ui/frontend run build
uv run anonymize-ui cv.pdf --lang cs
```

See [`packages/ui/README.md`](packages/ui/README.md) for frontend development.

Both commands take `--debug` (every step and detection to stderr, with the word
found and the rule or model that found it), `--log-level` and `--log-file`;
nothing is written to a file unless `--log-file` names one. A debug log holds
document text. See [`docs/logging.md`](docs/logging.md).

## What it produces

For a PDF: a redacted copy in which the detected text is removed from the file,
not covered, and every link, metadata field, attachment, bookmark, annotation and
form field is cleared. The CLI writes a copy only if the leak check passes; the
review window shows what the check found and lets the reviewer save the copy
anyway, or turn the check off in its settings. A
`review.json` session file records what was found and each decision; it holds
snippets of personal data, so treat it like the original. The leak check proves
the *detected* items are gone; what detection missed is what the benchmark
measures, so a human review before sharing the copy stays part of the workflow.

## Models and datasets

Every model and dataset is listed, pinned and checksummed in
[`catalog.toml`](packages/core/src/anonymizer/core/resources/catalog.toml).
Nothing downloads on its own; fetch one entry by id:

```sh
uv run python scripts/download.py list
uv run python scripts/download.py fetch gliner-multi-v2.1
uv run python scripts/download.py verify
```

Name models are chosen by catalog id: `--ner` runs the default
(`gliner-multi-v2.1`), `--name-model <id>` another catalog entry used for `ner`,
and the review window lists every such entry. Besides GLiNER (zero-shot,
Apache-2.0) the catalog holds NameTag 3 Czech and multilingual (ÚFAL, supervised,
CC BY-NC-SA 4.0: non-commercial use only), run without Keras on the same `ner`
dependency group. A model trained in this repository
(`python -m experiments train`, see [`experiments/README.md`](experiments/README.md))
has no download source: training lists it in its storage root's
`models/trained.json` with the SHA-256 of each file, and it is chosen the same way
whenever that root is the resource root. A name model's entry may set `threshold`,
its minimum span score chosen on development data; every client then runs the
model at it instead of GLiNER's default 0.3.

Files land in `models/<id>/` or `data/<id>/` of the repository (both git-ignored;
`--root` names another place). The CLI, the review window and the benchmark read
models from `models/` under `--resource-root`, by default the folder chosen in the review window (*Manage Models… → Change…*), else
`./models` if the working directory has one (a checkout of this repository),
else a per-user folder (`~/Library/Application Support/anonymizer` on macOS,
`%LOCALAPPDATA%/anonymizer` on Windows, `~/.local/share/anonymizer` on Linux). A file whose
size or checksum differs from the catalog is deleted and the run fails. Where the
source publishes only an MD5 or a git blob SHA-1, `fetch --pin` verifies that
digest and prints the SHA-256 to record in the catalog.

## Benchmark

Synthetic documents (Czech, Slovak, English) with every personal item
marked, plus documents with none that count false alarms, scored for rules
only and rules + GLiNER (`rules+<model>` runs any catalog name model):

```sh
uv sync --group ner --group benchmark
uv run python -m benchmark run --out benchmark-results
```

It writes a results table, per-document pictures (original, detections,
redacted, and a side-by-side collage) and, with `history`, charts across runs.
Each release runs it and attaches everything, so the charts show how results
change from version to version. See [`benchmark/README.md`](benchmark/README.md).

## Experiments

Detection quality on public corpora (CNEC 2.0, UNER Slovak, REDACT, OpenPII)
and generated name-form sets, from one command per config, with bootstrap
intervals; OCR on FUNSD's scanned forms; the training of the own name model. Results tables are
committed in `experiments/results/`; corpora and weights are not. See
[`experiments/README.md`](experiments/README.md).

## Layout

| Path | Contents |
| --- | --- |
| `packages/core/` | Library: `ingest/`, `detect/`, `redact/`, `resources/`, shared data contract |
| `packages/cli/` | `anonymize` command-line client |
| `packages/ui/` | `anonymize-ui` review window: Python side and React frontend |
| `benchmark/` | Synthetic benchmark documents, scorer, pictures and charts |
| `experiments/` | Evaluation harness and name-model training: corpus loaders, cached runs, scores with bootstrap intervals, results tables; no data committed |
| `scripts/` | Model and dataset download (`download.py`), mixed-format sample generator (`make_mixed_sample.py`), review window for development (`dev.py`), the CI window tour (`ui_tour.py`, `tour-linux.sh`, `answer-macos-prompts.sh`) |
| `docs/` | [`findings.md`](docs/findings.md) (what running the pipeline on real files showed), [`ui.md`](docs/ui.md) (review window handbook), [`logging.md`](docs/logging.md) |
| `tests/` | pytest suite; synthetic PDFs are built by `tests/pdf_builders.py` |

## Development

Requires [uv](https://docs.astral.sh/uv/). Python 3.12 is pinned via `.python-version`;
CI runs 3.12 and 3.13 on Linux, macOS and Windows.

```sh
uv sync                    # create the environment
uv run poe check           # everything CI checks: lint, format, types, tests with coverage
uv run poe fix             # fix lint findings and format
uv run poe test            # tests only (network blocked)
uv run poe dev             # review window with frontend hot reload (--built: build and open)
uv run poe                 # list every task
uv run pre-commit install  # run the hooks on every commit
```

Tasks are defined in `[tool.poe.tasks]` in `pyproject.toml`, and CI runs the same ones.
`poe check` must pass before committing. Coverage must stay at 93 % or more overall and
95 % or more for `redact/`. The pre-commit hooks reject documents and images outside
`tests/fixtures/`. Tests that need a downloaded model or corpus are marked `model` or
`dataset` and skipped when it is absent, so the default suite needs neither.

Contributions follow [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `docs:`, …), signed off and signed (`git commit -s -S`), on a feature branch;
pull request titles follow the same form, since the changelog is built from them.
`CLAUDE.md` holds the project's rules and architecture notes in full.

## Installing and releases

Today it is a developer install: `uv sync`, and Node 22 to build the review
window (see *Usage*). A per-OS bundle of the review window (PyInstaller) is
planned and not built yet. Models are never bundled; the user fetches each
explicitly, checked against the catalog checksum (*Models and datasets*).
Because PyMuPDF is AGPL, any distributed bundle is AGPL-3.0-or-later.

Releases are automated with [release-please](https://github.com/googleapis/release-please).
Every merge to `main` updates an open `chore: release X.Y.Z` pull request with
the next version (from the Conventional Commit messages) and the changelog (one
line per merged pull request). Merging that pull request tags the release and publishes it on
GitHub with the wheels and source archives. See [`CHANGELOG.md`](CHANGELOG.md).

## License

[AGPL-3.0-or-later](LICENSE): PyMuPDF, the PDF backend, is AGPL-licensed.
