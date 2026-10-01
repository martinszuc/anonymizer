# anonymizer

Local-only tool that detects and redacts personal data in scanned and electronic documents.

Pipeline: ingest (PDF text layer or OCR) → entity detection (rules + NER) → human review → redaction.
Part of a diploma thesis at FEKT VUT Brno.

**No document content leaves the machine.** No code path may call a remote service for OCR or
inference; models load from a local cache and the test suite fails on any outbound connection.

## Layout

| Path | Contents |
| --- | --- |
| `packages/core/` | Library: `ingest/`, `detect/`, `redact/`, shared data contract |
| `packages/cli/` | `anonymize` command-line client |
| `packages/ui/` | `anonymize-ui` review window: Python side and React frontend |
| `benchmark/` | Synthetic benchmark documents, scorer, pictures and charts |
| `experiments/` | Evaluation scripts; no data committed (planned, not created yet) |
| `scripts/` | Model and dataset download helpers |

## Development

Requires [uv](https://docs.astral.sh/uv/). Python 3.12 is pinned via `.python-version`.

```sh
uv sync                    # create the environment
uv run poe check           # everything CI checks: lint, format, types, tests with coverage
uv run poe fix             # fix lint findings and format
uv run poe test            # tests only (network blocked)
uv run poe                 # list every task
uv run pre-commit install  # run the hooks on every commit
```

Tasks are defined in `[tool.poe.tasks]` in `pyproject.toml`, and CI runs the same ones.
`poe check` must pass before committing. Coverage must stay at 93 % or more overall and
95 % or more for `redact/`. The pre-commit hooks reject documents and images outside
`tests/fixtures/`.

## Usage

```sh
uv run anonymize detect cv.pdf -o review.json --lang cs --show
uv run anonymize redact cv.pdf -o cv-redacted.pdf --session review.json
uv run anonymize inspect cv.pdf -o cv.html --lang cs   # pages with the found items drawn on
```

See [`packages/cli/README.md`](packages/cli/README.md) for reviewing without a UI.

The review window needs its frontend built once (Node 22). It opens on a home
screen: drop a PDF or open one, with the language and the name model chosen
there (`--resource-root` says where `models/` is, as for the CLI):

```sh
npm --prefix packages/ui/frontend ci
npm --prefix packages/ui/frontend run build
uv run anonymize-ui cv.pdf --lang cs
```

See [`packages/ui/README.md`](packages/ui/README.md) for frontend development.

## Models and datasets

Every model and dataset is listed, pinned and checksummed in
[`catalog.toml`](packages/core/src/anonymizer/core/resources/catalog.toml).
Nothing downloads on its own; fetch one entry by id:

```sh
uv run python scripts/download.py list
uv run python scripts/download.py fetch gliner-multi-v2.1
uv run python scripts/download.py verify
```

Files land in `models/<id>/` or `data/<id>/` (both git-ignored). A file whose
size or checksum differs from the catalog is deleted and the run fails. Where the
source publishes only an MD5 or a git blob SHA-1, `fetch --pin` verifies that
digest and prints the SHA-256 to record in the catalog.

## Benchmark

Six synthetic documents (Czech, Slovak, English) with every personal item
marked, scored for rules only and rules + GLiNER:

```sh
uv sync --group ner --group benchmark
uv run python -m benchmark run --out benchmark-results
```

It writes a results table, per-document pictures (original, detections,
redacted, and a side-by-side collage) and, with `history`, charts across runs.
Each release runs it and attaches everything, so the charts show how results
change from version to version. See [`benchmark/README.md`](benchmark/README.md).

## Releases

Automated with [release-please](https://github.com/googleapis/release-please).
Every merge to `main` updates an open `chore: release X.Y.Z` pull request with
the next version (from the Conventional Commit messages) and the changelog (one
line per merged pull request). Merging that pull request tags the release and publishes it on
GitHub with the wheels and source archives. See [`CHANGELOG.md`](CHANGELOG.md).

## Status

Working for PDFs with a text layer: text and hidden-data extraction, rule-based
detection (Czech and Slovak identifiers, IBAN, cards, email, phone, URL, labelled
dates of birth, postal addresses), names with the GLiNER model (optional,
`--ner`), review through
session files or the review window (a home screen with the detection options
and the name model, open or drop a PDF, toggle each item, draw regions, save the
session, export), blackbox redaction and a leak check on the output.
Scanned pages: ingest reads pages without a text layer through an OCR engine
interface, but no engine is included yet, so the CLI refuses such pages and the
review window warns about them. Searchable scans (a picture under an invisible
text layer) are redacted through that layer; see `docs/findings.md`.
Not yet: measured NER quality, an OCR engine, adding a missed word in the review
window.

## License

[AGPL-3.0-or-later](LICENSE) — PyMuPDF, the intended PDF backend, is AGPL-licensed.
