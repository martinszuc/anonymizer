# CLAUDE.md

Context for AI coding sessions in this repository. Read before making changes.

## Project

Local-only tool that detects and redacts personal data in scanned and electronic documents.
Pipeline: ingest (PDF text layer or OCR) → entity detection (rules + NER) → human review → redaction.
Part of a diploma thesis at FEKT VUT Brno. Roadmap and open decisions: `PLAN.md`.

## Hard constraints

- **Offline only.** No code path may send document content or call a remote service for OCR or inference. Models load from local cache (`HF_HUB_OFFLINE=1`). Tests run with network access blocked.
- **No real personal data.** Test fixtures, examples and training data are synthetic or from public benchmarks. Never commit datasets, model weights or generated documents.
- **True redaction.** Redacted content must be removed from the output file, not covered. Every redaction path needs a leakage test (re-extract the output, assert target strings are absent).
- **Unicode.** UTF-8 everywhere; normalize text to NFC at ingest. Czech/Slovak diacritics must survive round-trips.

## Architecture

```
packages/core/   library, no UI or CLI dependencies
  types.py       shared data contract
  ingest/        PDF text layer (PyMuPDF), OCR engine adapters
  detect/        base.py (protocol, Match, RuleDetector, overlap resolution),
                 birth_number.py, bank_account.py, iban.py, contact.py, NER backends
  redact/        redaction strategies
packages/cli/    thin command-line client
ui/              review UI (framework not decided)
experiments/     evaluation scripts
scripts/         model and dataset download
data/            local corpora, git-ignored, never committed
```

Implemented so far: the data contract, the rule-based detectors, and
born-digital PDF ingest. The OCR adapter, redaction, CLI and UI are empty.

- All components exchange data through `core/types.py`: `Document → Page → Word(bbox) → Entity`. Change the contract deliberately; it is consumed by CLI, UI and serialized review files.
- OCR engines, detectors and redaction strategies sit behind interfaces. Add implementations, do not special-case callers.
- Structured identifiers (rodné číslo, bank accounts, IBAN) are detected by format + checksum rules, not by ML.
- Coordinates are **PDF points, per page, origin top-left, y downward** (PyMuPDF's convention, so extraction needs no conversion). A rasterized page records `Page.raster_dpi`; pixels convert with `points = pixels * 72 / dpi` before entering a `BBox`.
- Text offsets are **page-local into `Page.text`**. An entity carries its character span *and* one bbox per covered word, so a span crossing a line break yields several boxes instead of one covering the gap.
- Overlapping detections are resolved by `resolve_overlaps`: entity-type priority first (checksum-backed identifiers beat free-form patterns), then longest span. Add a type to `OVERLAP_PRIORITY` rather than special-casing a caller.
- Detection is **recall-first**: a missed entity leaks, a false positive is removed during review. Prefer a rule that over-matches to one that depends on a register that can go stale (this is why bank codes are not validated against the ČNB list).
- English is the first target language; Czech/Slovak follow. Keep language a configuration value, never hardcoded.

## Stack

Python ≥ 3.12 (CI: 3.12, 3.13 on macOS, Linux, Windows) · uv workspace · ruff · pyright (standard) · pytest.

```sh
uv sync                    # install
uv run pytest              # tests
uv run ruff check --fix .  # lint
uv run ruff format .       # format
uv run pyright             # type check
```

All four must pass before committing.

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
- Fixtures are generated or hand-written synthetic data in `tests/fixtures/`. Checksum-bearing test values (rodná čísla, account numbers, IBANs) are computed independently, never by asking the validator under test whether it likes its own output.
- Tests needing a downloaded model are marked `@pytest.mark.model` and skipped when the model is absent.
- Tests needing a downloaded corpus are marked `@pytest.mark.dataset` and skipped when the corpus is absent. The unmarked suite must pass with no network and no `data/` directory, because that is all CI has.
- Datasets are never test fixtures, and a dataset containing real personal data is never used in tests at all. Measurement lives in `experiments/`, not in `pytest`.

## Dependencies and data

- Adding a dependency is fine; justify it in the commit message and prefer well-maintained packages with permissive licenses. Flag AGPL or non-commercial licenses.
- Ask before downloading models or datasets.

## Git

- Work on feature branches (`feat/iban-detector`); never commit to `main`. The maintainer reviews and merges.
- Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`, `ci:`.
- Commit with `git commit -s -S`.
- One logical change per commit.

## Out of scope for AI sessions

Thesis text (analysis, literature review, conclusions) is written by the author outside this repository. Repository docs describe the software only.
