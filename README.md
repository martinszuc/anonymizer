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
| `experiments/` | Evaluation scripts; no data committed |
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
```

See [`packages/cli/README.md`](packages/cli/README.md) for reviewing without a UI.

## Status

Working for PDFs with a text layer: text and hidden-data extraction, rule-based
detection (Czech and Slovak identifiers, IBAN, cards, email, phone, URL), review
through session files, blackbox redaction and a leak check on the output.
Not yet: names (NER), scanned documents (OCR), the review UI.

## License

[AGPL-3.0-or-later](LICENSE) — PyMuPDF, the intended PDF backend, is AGPL-licensed.
