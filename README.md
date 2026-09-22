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
uv run pytest              # tests (network blocked)
uv run ruff check --fix .  # lint
uv run ruff format .       # format
uv run pyright             # type check
```

All four must pass before committing. Optionally `uv run pre-commit install`.

## Status

Early scaffolding: no pipeline stage is implemented yet.

## License

[AGPL-3.0-or-later](LICENSE) — PyMuPDF, the intended PDF backend, is AGPL-licensed.
