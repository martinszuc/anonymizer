# anonymizer-core

Offline detection and redaction of personal data in documents.

The library behind the CLI and the review window: ingest (PDF text layer,
non-text surfaces, OCR), detection (rules, optional name models), review sessions and
redaction with a leak check. No UI or CLI dependencies. Clients call
`anonymizer.core.pipeline` (`build_detector`, `run_detection`) and export through
`anonymizer.core.redact.export_redacted`. The data contract is `core/types.py`.
Layout, usage and status: the root `README.md`.
