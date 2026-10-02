# Changelog

## 0.3.0 (2026-10-02)

## What's Changed
* feat: review window with page view and per-item decisions by @martinszuc in https://github.com/martinszuc/anonymizer/pull/23
* docs: add a handbook for the review window by @martinszuc in https://github.com/martinszuc/anonymizer/pull/25
* feat: detect whole postal addresses anchored on the postcode by @martinszuc in https://github.com/martinszuc/anonymizer/pull/27
* feat: detect dates of birth after a birth label by @martinszuc in https://github.com/martinszuc/anonymizer/pull/26
* feat: export the redacted PDF from the review window by @martinszuc in https://github.com/martinszuc/anonymizer/pull/28
* feat: draw regions over photos, signatures and stamps in the review window by @martinszuc in https://github.com/martinszuc/anonymizer/pull/29
* fix: close two leaks and narrow the review window's API after a code review by @martinszuc in https://github.com/martinszuc/anonymizer/pull/31
* fix: stop offering a keep decision on findings in hidden data by @martinszuc in https://github.com/martinszuc/anonymizer/pull/30
* feat: a home screen with detection options, progress while opening, and drag and drop by @martinszuc in https://github.com/martinszuc/anonymizer/pull/32
* test: add a generator for a mixed typed, scanned and handwritten sample PDF by @martinszuc in https://github.com/martinszuc/anonymizer/pull/33
* ci: photograph the review window on every platform and name workflows clearly by @martinszuc in https://github.com/martinszuc/anonymizer/pull/34
* feat: read scanned pages through an OCR engine interface by @martinszuc in https://github.com/martinszuc/anonymizer/pull/35
* feat: redact pages OCR read and re-read them in the leak check by @martinszuc in https://github.com/martinszuc/anonymizer/pull/38
* feat: a scanned benchmark scoring OCR across degradation levels by @martinszuc in https://github.com/martinszuc/anonymizer/pull/39
* test: run the mixed sample through the CLI in CI, and document it by @martinszuc in https://github.com/martinszuc/anonymizer/pull/40
* feat: OnnxTR, the first OCR engine, in the CLI and the scanned benchmark by @martinszuc in https://github.com/martinszuc/anonymizer/pull/41
* feat: read scanned pages with OCR in the review window by @martinszuc in https://github.com/martinszuc/anonymizer/pull/42
* feat: download models from the review window by @martinszuc in https://github.com/martinszuc/anonymizer/pull/43
* feat: add logging with --debug, --log-level and --log-file by @martinszuc in https://github.com/martinszuc/anonymizer/pull/44
* docs: record the issues found while testing the review window by hand by @martinszuc in https://github.com/martinszuc/anonymizer/pull/45


**Full Changelog**: https://github.com/martinszuc/anonymizer/compare/v0.2.0...v0.3.0

## 0.2.0 (2026-09-29)

## What's Changed
* fix: stop the leak check matching short numbers inside PDF syntax by @martinszuc in https://github.com/martinszuc/anonymizer/pull/20
* feat: synthetic benchmark with pictures and charts across versions by @martinszuc in https://github.com/martinszuc/anonymizer/pull/22


**Full Changelog**: https://github.com/martinszuc/anonymizer/compare/v0.1.0...v0.2.0

## 0.1.0 (2026-09-29)

## What's Changed
* Chore/repo foundation by @martinszuc in https://github.com/martinszuc/anonymizer/pull/1
* feat: add core data contract for documents, words and entities by @martinszuc in https://github.com/martinszuc/anonymizer/pull/2
* Feat/rule detectors by @martinszuc in https://github.com/martinszuc/anonymizer/pull/3
* feat: extract words and geometry from born-digital PDFs by @martinszuc in https://github.com/martinszuc/anonymizer/pull/4
* feat: list and scan PII surfaces outside the page text by @martinszuc in https://github.com/martinszuc/anonymizer/pull/5
* feat: detect web addresses without a list of sites by @martinszuc in https://github.com/martinszuc/anonymizer/pull/6
* feat: redact PDFs and check the output for leaks by @martinszuc in https://github.com/martinszuc/anonymizer/pull/7
* docs: make Czech and Slovak the primary NER target by @martinszuc in https://github.com/martinszuc/anonymizer/pull/8
* fix: remove hidden content and verify redaction on saved files by @martinszuc in https://github.com/martinszuc/anonymizer/pull/9
* feat: review data format v6 (regions, fingerprint, session files) by @martinszuc in https://github.com/martinszuc/anonymizer/pull/10
* feat: add the anonymize command line (detect, redact, check) by @martinszuc in https://github.com/martinszuc/anonymizer/pull/11
* feat/resource list by @martinszuc in https://github.com/martinszuc/anonymizer/pull/12
* chore: coverage floors, one ruff pin, no committed documents by @martinszuc in https://github.com/martinszuc/anonymizer/pull/13
* feat: GLiNER name and address detection (--ner) by @martinszuc in https://github.com/martinszuc/anonymizer/pull/14
* ci: automated releases with release-please by @martinszuc in https://github.com/martinszuc/anonymizer/pull/15
* chore: add poe tasks shared by developers and CI by @martinszuc in https://github.com/martinszuc/anonymizer/pull/17
* feat: add the inspect command by @martinszuc in https://github.com/martinszuc/anonymizer/pull/16
* ci: start releases at 0.1.0 with one changelog line per pull request by @martinszuc in https://github.com/martinszuc/anonymizer/pull/19

## New Contributors
* @martinszuc made their first contribution in https://github.com/martinszuc/anonymizer/pull/1

**Full Changelog**: https://github.com/martinszuc/anonymizer/commits/v0.1.0
