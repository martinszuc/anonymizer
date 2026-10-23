# Changelog

## 0.7.0 (2026-10-23)

<!-- Release notes generated using configuration in .github/release.yml at main -->

## What's Changed
### Software
* feat(benchmark): comparable history across document sets, backfill and PR diff by @martinszuc in https://github.com/martinszuc/anonymizer/pull/110
* feat: per-model decision threshold in the catalog by @martinszuc in https://github.com/martinszuc/anonymizer/pull/115
* ci: list experiments under their own section of the release notes by @martinszuc in https://github.com/martinszuc/anonymizer/pull/120
* feat: XLM-R large token classifier as a second name-model family by @martinszuc in https://github.com/martinszuc/anonymizer/pull/122
* feat(experiments): WikiGoldSK and SlavicNER Czech as training corpora, with an overlap guard by @martinszuc in https://github.com/martinszuc/anonymizer/pull/127
* docs: the overlap guard may read test text to keep it out of training by @martinszuc in https://github.com/martinszuc/anonymizer/pull/131
### Experiments
* feat(experiments): train on an NVIDIA GPU with --device cuda by @martinszuc in https://github.com/martinszuc/anonymizer/pull/106
* feat(experiments): Czech-only and Slovak-only training configs for RQ7 by @martinszuc in https://github.com/martinszuc/anonymizer/pull/108
* feat(experiments): --tag names a config retrained on another machine by @martinszuc in https://github.com/martinszuc/anonymizer/pull/109
* feat(scripts): MetaCentrum training and scoring jobs by @martinszuc in https://github.com/martinszuc/anonymizer/pull/111
* fix(scripts): MetaCentrum jobs keep their scores, files stay private, uv is checked by @martinszuc in https://github.com/martinszuc/anonymizer/pull/114
* feat(experiments): MetaCentrum training results and their run configs by @martinszuc in https://github.com/martinszuc/anonymizer/pull/113
* docs(findings): the same training on an L40S, and training on one language by @martinszuc in https://github.com/martinszuc/anonymizer/pull/116
* feat(experiments): score run configs with GLiNER on a GPU by @martinszuc in https://github.com/martinszuc/anonymizer/pull/117
* chore(experiments): rq6-gpu-dev and rq7-dev results, with findings by @martinszuc in https://github.com/martinszuc/anonymizer/pull/118
* feat(experiments): oversample a training corpus, and the recipe sweep (stage A) by @martinszuc in https://github.com/martinszuc/anonymizer/pull/119
* chore(experiments): recipe sweep stage A results, with findings by @martinszuc in https://github.com/martinszuc/anonymizer/pull/121
* feat(experiments): run config for the two model families against NameTag 3 by @martinszuc in https://github.com/martinszuc/anonymizer/pull/123
* chore(experiments): XLM-R and recipe stage B training results by @martinszuc in https://github.com/martinszuc/anonymizer/pull/124
* feat(experiments): XLM-R token classifier with the real corpora repeated 3x by @martinszuc in https://github.com/martinszuc/anonymizer/pull/125
* feat(experiments): GLiNER focal loss with the real corpora repeated 3x by @martinszuc in https://github.com/martinszuc/anonymizer/pull/126
* chore(experiments): rq6-xlmr-dev and the newer training results, with findings by @martinszuc in https://github.com/martinszuc/anonymizer/pull/129
* feat(experiments): focal loss with the added corpora, the candidates against NameTag 3 by @martinszuc in https://github.com/martinszuc/anonymizer/pull/128
* feat(experiments): verdict by the fixed rule, and the candidates' error analysis by @martinszuc in https://github.com/martinszuc/anonymizer/pull/130
* fix(scripts): MetaCentrum jobs ask for fewer CPUs and less memory by @martinszuc in https://github.com/martinszuc/anonymizer/pull/132
* feat(experiments): the final RQ6 test configs, read once by @martinszuc in https://github.com/martinszuc/anonymizer/pull/134
* chore(experiments): candidates against NameTag 3, error analysis, and the model the rule picks by @martinszuc in https://github.com/martinszuc/anonymizer/pull/133
* feat(experiments): the final RQ6 test configs, read once by @martinszuc in https://github.com/martinszuc/anonymizer/pull/135


**Full Changelog**: https://github.com/martinszuc/anonymizer/compare/v0.6.0...v0.7.0

## 0.6.0 (2026-10-14)

## What's Changed
* docs: OpenPII baseline, FUNSD scans and the rq1-dev re-run by @martinszuc in https://github.com/martinszuc/anonymizer/pull/86
* feat(experiments): train a Czech/Slovak name model (fine-tuned GLiNER) by @martinszuc in https://github.com/martinszuc/anonymizer/pull/87
* fix(detect): drop a full stop after a closing bracket before stripping edges by @martinszuc in https://github.com/martinszuc/anonymizer/pull/89
* feat: add NameTag 3 as a name model and compare it with GLiNER by @martinszuc in https://github.com/martinszuc/anonymizer/pull/90
* docs: record NameTag 3 against GLiNER on development data by @martinszuc in https://github.com/martinszuc/anonymizer/pull/91
* chore(experiments): train the first full runs in batches of 16 by @martinszuc in https://github.com/martinszuc/anonymizer/pull/92
* feat(experiments): score leak coverage beside the match scores by @martinszuc in https://github.com/martinszuc/anonymizer/pull/93
* feat(experiments): recall-weighted training loss and seed replicates by @martinszuc in https://github.com/martinszuc/anonymizer/pull/94
* feat(experiments): recall-weighted training loss and seed replicates by @martinszuc in https://github.com/martinszuc/anonymizer/pull/96
* feat(experiments): Czech and Slovak name-forms challenge set with recall per form by @martinszuc in https://github.com/martinszuc/anonymizer/pull/95
* docs(experiments): first trained models against NameTag 3, name forms by @martinszuc in https://github.com/martinszuc/anonymizer/pull/97
* feat(experiments): weight sweep configs, and --device for training without the Apple GPU by @martinszuc in https://github.com/martinszuc/anonymizer/pull/98
* feat(experiments): error analysis of misses and false alarms by category by @martinszuc in https://github.com/martinszuc/anonymizer/pull/99
* feat(experiments): full REDACT Czech records as the test split by @martinszuc in https://github.com/martinszuc/anonymizer/pull/100
* docs(experiments): losses over three seeds, the weight sweep, name forms of the trained models by @martinszuc in https://github.com/martinszuc/anonymizer/pull/101
* docs: make the documentation match the code by @martinszuc in https://github.com/martinszuc/anonymizer/pull/102
* feat(experiments): held-out synthetic test set for the final RQ6 test by @martinszuc in https://github.com/martinszuc/anonymizer/pull/103
* feat(experiments): threshold control for weights 5 and 10, error analysis by document by @martinszuc in https://github.com/martinszuc/anonymizer/pull/104
* feat(experiments): guards for test data and brute-force checks of the metrics by @martinszuc in https://github.com/martinszuc/anonymizer/pull/105


**Full Changelog**: https://github.com/martinszuc/anonymizer/compare/v0.5.0...v0.6.0

## 0.5.0 (2026-10-10)

## What's Changed
* docs: record the thesis direction: a model of our own by @martinszuc in https://github.com/martinszuc/anonymizer/pull/75
* fix: match emails and URLs that OCR split after a period by @martinszuc in https://github.com/martinszuc/anonymizer/pull/77
* feat: read handwriting with a kraken OCR engine by @martinszuc in https://github.com/martinszuc/anonymizer/pull/78
* feat: score scanned detection by where items are printed, and count false alarms by @martinszuc in https://github.com/martinszuc/anonymizer/pull/79
* feat: choose the OCR engine in the review window by @martinszuc in https://github.com/martinszuc/anonymizer/pull/80
* feat: open JPEG, PNG and TIFF images wherever a PDF is accepted by @martinszuc in https://github.com/martinszuc/anonymizer/pull/81
* refactor: review cleanup across core, clients, benchmark and frontend by @martinszuc in https://github.com/martinszuc/anonymizer/pull/82
* feat: choose the name model by catalog id by @martinszuc in https://github.com/martinszuc/anonymizer/pull/83
* feat(ui): redesign the review window for long reviews by @martinszuc in https://github.com/martinszuc/anonymizer/pull/84
* feat: FUNSD and OpenPII 1M as evaluation corpora by @martinszuc in https://github.com/martinszuc/anonymizer/pull/85


**Full Changelog**: https://github.com/martinszuc/anonymizer/compare/v0.4.0...v0.5.0

## 0.4.0 (2026-10-05)

## What's Changed
* fix: review window issues from manual testing by @martinszuc in https://github.com/martinszuc/anonymizer/pull/46
* test: compare library loggers with their state before configuring by @martinszuc in https://github.com/martinszuc/anonymizer/pull/48
* feat: widen detected names over academic titles by @martinszuc in https://github.com/martinszuc/anonymizer/pull/49
* feat: group identical findings in the review list by @martinszuc in https://github.com/martinszuc/anonymizer/pull/53
* feat: opening progress, locate-only clicks and a models folder by @martinszuc in https://github.com/martinszuc/anonymizer/pull/54
* feat: fewer false alarms from the name model by @martinszuc in https://github.com/martinszuc/anonymizer/pull/55
* feat: keep the names model's uncertain findings in one click by @martinszuc in https://github.com/martinszuc/anonymizer/pull/56
* feat: recognise the document language from its text by @martinszuc in https://github.com/martinszuc/anonymizer/pull/57
* feat: search, sort and filter the findings list by @martinszuc in https://github.com/martinszuc/anonymizer/pull/58
* feat: add a missed word or phrase in the review window by @martinszuc in https://github.com/martinszuc/anonymizer/pull/59
* feat: grow the benchmark to 26 documents with hidden leaks in seven carriers by @martinszuc in https://github.com/martinszuc/anonymizer/pull/60
* fix: read attachment names with diacritics correctly by @martinszuc in https://github.com/martinszuc/anonymizer/pull/62
* feat: evaluation harness in experiments/ with first RQ1 results by @martinszuc in https://github.com/martinszuc/anonymizer/pull/61
* feat: add a dev task that starts Vite and the review window by @martinszuc in https://github.com/martinszuc/anonymizer/pull/63
* fix: remove attachments listed in a split name tree by @martinszuc in https://github.com/martinszuc/anonymizer/pull/64
* fix: remove files referred to as associated files (/AF) by @martinszuc in https://github.com/martinszuc/anonymizer/pull/65
* docs: mention the dev task in the READMEs and CLAUDE.md by @martinszuc in https://github.com/martinszuc/anonymizer/pull/66
* fix: keep the web inspector from opening by itself under --debug by @martinszuc in https://github.com/martinszuc/anonymizer/pull/67
* fix: cut explanatory copy from the models sheet and reword the home footer by @martinszuc in https://github.com/martinszuc/anonymizer/pull/68
* fix: keep the selected box's outline visible in redacted preview by @martinszuc in https://github.com/martinszuc/anonymizer/pull/69
* feat: show export progress, make the leak check a warning, add Settings by @martinszuc in https://github.com/martinszuc/anonymizer/pull/73
* fix: drop form headers the name model tags as persons and addresses by @martinszuc in https://github.com/martinszuc/anonymizer/pull/72
* fix: size GLiNER windows in the model's own tokens by @martinszuc in https://github.com/martinszuc/anonymizer/pull/70
* fix: stop the leak check matching short texts by chance by @martinszuc in https://github.com/martinszuc/anonymizer/pull/71
* fix(ui): close the hover popover when the pointer leaves a box by @martinszuc in https://github.com/martinszuc/anonymizer/pull/74


**Full Changelog**: https://github.com/martinszuc/anonymizer/compare/v0.3.0...v0.4.0

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
