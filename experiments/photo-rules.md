# Phone photos (RQ3, `rq8`): scoring rules

Written and committed on 2026-11-24, before any photo was taken or scored. Nothing in
this file may change after the first scoring run of the test photos; a change before
that is a new commit with its reason in `JOURNAL.md`.

Everything about photos is **post hoc** relative to the final test of 2026-10-29: it is
reported apart from that table and never changes its verdict.

## Photo sets

- **Test set:** the 22 Czech and Slovak benchmark documents, 23 pages (`cs-terms` has
  two), printed from `outputs/rq8-photos/print/rq8-print.pdf` in the order of
  `print/manifest.md`, each page photographed once under each of three conditions:
  `flat`, `dim`, `angle` (`outputs/rq8-photos/PROTOCOL.md`). Exactly **69 photos** in
  `outputs/rq8-photos/photos/<condition>/`, 23 per condition. A condition with a
  missing or extra photo is not scored. Six of the 22 documents plant nothing
  (`cs-gym-rules`, `cs-notice`, `cs-privacy-notice`, `cs-terms`, `sk-terms`,
  `sk-waste-notice`); they count for false alarms.
- **Training set:** invented documents of `benchmark/photo_train/` (split `print`),
  printed from `print/rq8-train-print.pdf` (`print/manifest-train.md`) and photographed
  under the same three conditions into `outputs/rq8-photos/photos-train/<condition>/`.
  Training photos are never scored as test data, and no test photo is used in training,
  tuning or choosing a checkpoint. The two sets are photographed in separate sessions and
  never stored together.
- Ground truth of a photo is the generator's text of its page (the born-digital text
  layer) with the planted items marked inline; it is never read off the photo.

## Systems

Thresholds are each model's catalog threshold or its engine default
(`name_model_threshold`); nothing is tuned on photos.

| System | Model(s) |
|---|---|
| `rules` | none |
| `rules+gliner` | `gliner-multi-v2.1`, zero-shot |
| `rules+nametag-multi` | `nametag3-multilingual-260521` |
| `rules+xlmr\|focal-more` | final model: union of `xlmr-cs-sk-ce-more` @ 0.5 and `gliner-cs-sk-focal-more` @ 0.3 (catalog `xlmr-focal-more`) |
| `rules+xlmr-cs-sk-ce-more` | the union's first member alone |
| `rules+gliner-cs-sk-focal-more` | the union's second member alone |
| `rules+xlmr\|photo` | post hoc: the union with the photo fine-tune of `gliner-cs-sk-focal-more` in place of it, @ 0.3 |
| `rules+gliner-photo` | post hoc: the photo fine-tune alone |

The photo model is fine-tuned from `gliner-cs-sk-focal-more` on invented documents
degraded in code and on the training photos (`experiments/configs/`, named as post hoc).
Its configuration and checkpoint are fixed before the test photos are scored with it;
any choice between its variants is made on training-set documents held out from its
training, never on test photos.

## OCR

- **OnnxTR** (`onnxtr-fast-base` + `onnxtr-parseq-multilingual-v1`), as in the scanned
  benchmark. **kraken** (`kraken-blla` + `kraken-ppocr-v6-medium`) as a second engine if
  it runs on the photos; if it fails, the failure is reported and OnnxTR alone is scored.
- Photos enter through the tool's own image ingest (`core/ingest/image.py`) with its
  rotation handling and nothing else: no cropping, dewarping or contrast step that the
  tool does not ship. The measure is the tool as a user would run it on a phone photo.
- A **digital** reference row scores every system on the born-digital text of the same
  documents (no OCR), so each condition's drop is measured against it.

## Locating the ground truth in OCR text

Perspective and the page edge break the box mapping `benchmark/scans.py` uses for flat
scans, so items are placed by text alignment:

- The page's ground-truth text and the OCR text are aligned character by character
  (Levenshtein edit operations, both with whitespace runs as one space, NFC).
- An item's located span runs from the OCR character aligned to its first read character
  to the one aligned to its last read character. An item none of whose characters is
  aligned to an OCR character (all deleted) is **not read**.
- An item not read is missed for every system and leaves its document unsafe: it is
  printed on the photo and stays in the redacted copy.

## Scores, per engine and condition (and the digital row)

- **CER** and **diacritics error**, as `benchmark/ocr_score.py` `text_errors`: edit
  distance over the ground truth's length; share of letters with a diacritic not read
  exactly. Per engine and condition, independent of the system.
- **Not read**: items not located at all.
- **Items found / partial / missed** (all types): found when one detected span covers the
  whole located span, as in the benchmark.
- **Person recall and F2, partial match**, and **person residual share**, by
  `experiments/metrics.py` (`partial` mode; residual = gold person characters no
  detection covers / gold person characters), on the located person spans, with
  not-read persons counted as missed (their characters as residual).
- **Documents left safe**: every planted item read and found whole.
- **Leak check after redaction**: whether `redact.export_redacted` accepts the copy, per
  document. It proves only that detected items are gone; it is reported as is, never as
  evidence of anonymization.
- **False alarms**: distinct detected texts overlapping no planted item.

## Intervals and the rule of "better"

- Paired bootstrap over **documents** (22; the two pages of `cs-terms` are one document),
  1000 resamples, seed 20261010, 95 % percentile intervals, as `experiments/metrics.py`.
  Each condition is a separate set, as the corpora were in the final test.
- **Primary post hoc comparison:** `rules+xlmr|photo` (candidate) against
  `rules+xlmr|focal-more` (baseline), per condition, OnnxTR. The rule of the final test
  (`experiments/verdict.py`): a condition is a **win** when the candidate's person F2
  (partial) is higher and its person residual share lower, each paired 95 % interval
  excluding 0; a **loss** when it is significantly worse on either; a **tie** otherwise.
- The photo model is called **better on phone photos** only if it wins on all three
  conditions. Otherwise the per-condition outcomes are reported as they are, in that
  wording. Its result on the digital row is reported in the same sentence (a loss there
  is a cost of the fine-tune).
- Reported as data, by the same rule, no verdict: the final union against
  `rules+nametag-multi` per condition; each member against the union; kraken against
  OnnxTR on CER.

## Runs

- The test photos are scored once per system set: once with the six existing systems
  (allowed as soon as all 69 photos are in), once more when the photo model exists. Each
  run writes `experiments/results/photos-<run>.json` and `.md` with commit, machine, tool
  and model versions and the photo files' SHA-256.
- A re-run after a bug fix keeps the earlier results file, and `JOURNAL.md` records why.
- No score on photos is computed before this file is committed.
