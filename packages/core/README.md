# anonymizer-core

Offline detection and redaction of personal data in documents.

The library behind the CLI and the review window: ingest (PDF text layer,
non-text surfaces), detection (rules, optional GLiNER), review sessions and
redaction with a leak check. No UI or CLI dependencies. Clients call
`anonymizer.core.pipeline` (`build_detector`, `run_detection`) and export through
`anonymizer.core.redact.export_redacted`. The data contract is `core/types.py`.
Architecture, constraints and conventions: the root `CLAUDE.md`; usage: the root
`README.md`.
