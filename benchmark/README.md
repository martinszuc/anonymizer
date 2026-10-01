# Benchmark

Scores the pipeline on synthetic documents and produces material for
reports and presentations. Everything here is invented and safe to publish.

```sh
uv sync --group ner --group benchmark        # GLiNER and matplotlib
uv run python -m benchmark run --out benchmark-results
uv run python -m benchmark run --out benchmark-results --systems rules   # no model
uv run python -m benchmark history run-a/results.json run-b/results.json --out charts
```

## Scanned variants (OCR)

```sh
uv run python -m benchmark ocr --out ocr-results                    # every level, the oracle
uv run python -m benchmark ocr --out ocr-results --levels clean,blur-2,skew-3
uv run python -m benchmark ocr --out ocr-results --engines oracle,onnxtr   # uv sync --group ocr-onnxtr
```

Each document is rendered to a greyscale picture, degraded one factor at a
time (resolution, blur, noise, JPEG quality, skew; noise is seeded), and
written as a picture-only PDF. The original's text layer is the ground
truth, its boxes moved with the ink under skew. Only items on the page are
scored: a scan carries no links or metadata. Scores, per engine and level:

- **CER** — character error rate against the original's text; **diacritics**
  — the share of letters with a diacritic not read exactly.
- **boxed** — ground-truth words matched by an OCR box (IoU ≥ 0.5);
  **ink under boxes** — the share of the words' printed pixels inside OCR
  boxes; **partly outside** — words with ink outside every box, which a
  redaction drawn from OCR boxes would leave partly in the picture.
- **found** — as below, on the OCR text.
- **readable / partly after** — ink left in each item's ground-truth boxes in
  the redacted picture: half a word or more, or more than a trace. Counted in
  pixels, so it does not depend on the engine being scored.

The `oracle` engine reads the ground truth (and, when the leak check re-reads
a redacted page, only the words still printed), so it bounds what OCR can
give the rest of the pipeline. `onnxtr` is the first real engine; the release
workflow runs both on one level per factor. Output:
`ocr-results.json`, `ocr-results.md`, `pdf/`, and `scans/<doc>.<level>[.<engine>].pdf`.

## Output

| Path | What |
|---|---|
| `results.json` | every score, with tool and model versions, commit and machine |
| `results.md` | the same as tables |
| `pdf/<doc>.pdf`, `pdf/<doc>.<system>.pdf` | generated original, redacted output |
| `images/<doc>.original.png` | the page (text area) |
| `images/<doc>.<system>.detected.png` | detections, one colour per type |
| `images/<doc>.<system>.redacted.png` | the redacted page |
| `images/<doc>.<system>.collage.png` | the three side by side |
| `charts/*.png` | (`history`) found and safe documents per version, found per type |

Each release attaches `benchmark-results.json`, the charts and a zip of all
pictures; `history` over the downloaded `benchmark-results.json` files of
several releases draws the change across versions:

```sh
for tag in $(gh release list --json tagName --jq '.[].tagName'); do
  gh release download "$tag" -p benchmark-results.json -D "history/$tag"
done
uv run python -m benchmark history history/*/benchmark-results.json --out charts
```

## Scores

- **found / partial / missed** — whether one detected span covers the planted
  item, only part of it, or none of it.
- **false alarms** — distinct detected texts overlapping no planted item.
- **decoys removed** — listed strings that look personal but are not, and
  were redacted anyway.
- **safe** — after redaction, no planted item is readable, whole or as a word
  unique to it. The leak check only verifies that *detected* items are gone;
  this is the measure of what was never detected.

## Adding a document

Write `documents/<language>-<kind>.toml`:

```toml
language = "cs"
kind = "letter"
lines = ["Píše [[person:Jan Novák]], tel. [[phone:+420 777 123 456]]."]
links = [{ anchor = "E-mail", target = "mailto:[[email:jan.novak@example.com]]" }]
metadata = { Title = "Dopis – [[person:Jan Novák]]" }
bookmarks = ["Dopis"]
decoys = ["Stavby Morava a.s."]
```

`[[type:text]]` plants an item (types as in `EntityType`); `{{filler:N}}`
adds N words of neutral text. Use invented names, `example.com/.org/.net`
addresses, and checksum-bearing values computed independently of the
validators under test.
