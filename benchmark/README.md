# Benchmark

Scores the pipeline on synthetic documents and produces material for
reports and presentations. Everything here is invented and safe to publish.

```sh
uv sync --group ner --group benchmark        # GLiNER and matplotlib
uv run python -m benchmark run --out benchmark-results
uv run python -m benchmark run --out benchmark-results --systems rules   # no model
uv run python -m benchmark run --out benchmark-results --systems rules,rules+<catalog id>
uv run python -m benchmark history run-a/results.json run-b/results.json --out charts
uv run python -m benchmark diff baseline/results.json run/results.json   # per type, Markdown
uv run python -m benchmark backfill v0.4.0 v0.5.0 --out backfill        # earlier code, current documents
```

A system is `rules` or `rules+<model>`, the model a catalog name model
(`uses = ["ner"]`) by id; `rules+gliner` is the default model under its earlier
name, so it and `rules+gliner-multi-v2.1` give the same scores. Each model is
loaded once however many systems name it. The history charts draw `rules` and
`rules+gliner` only.

## Scanned variants (OCR)

```sh
uv run python -m benchmark ocr --out ocr-results                    # every level, the oracle
uv run python -m benchmark ocr --out ocr-results --levels clean,blur-2,skew-3
uv run python -m benchmark ocr --out ocr-results --engines oracle,onnxtr   # uv sync --group ocr-onnxtr
uv run python -m benchmark ocr --out ocr-results --engines oracle,kraken   # uv sync --group ocr-kraken
uv run python -m benchmark ocr-margin --out margins --engines onnxtr,kraken --levels clean,skew-3
uv run python -m benchmark ocr-probe scan.pdf --out probe --engines onnxtr,kraken [--truth t.json]
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
- **found** — as below, on the OCR text. An item is located there by where
  it is printed: the OCR words whose box centre lies in its ground-truth
  boxes. Read split or misread (`jan. novak@example. com`), it is still
  located, and found only when one detected span covers all of it.
- **false alarms** — as below: distinct detected texts on the OCR text
  overlapping no planted item.
- **readable / partly after** — ink left in each item's ground-truth boxes in
  the redacted picture: half a word or more, or more than a trace. Counted in
  pixels, so it does not depend on the engine being scored.

The `oracle` engine reads the ground truth (and, when the leak check re-reads
a redacted page, only the words still printed), so it bounds what OCR can
give the rest of the pipeline. `onnxtr` and `kraken` are the real engines; the
release workflow runs the oracle and `onnxtr` on one level per factor. Output:
`ocr-results.json`, `ocr-results.md`, `pdf/`, and `scans/<doc>.<level>[.<engine>].pdf`.

`ocr-margin` measures how far an engine's word boxes must grow (its
`box_margin`, a share of the box height on each side) to cover their words'
ink: each engine reads every scan once, and its words are replayed through
ingest with each candidate margin. It reports words with ink outside every
box and boxes reaching a word on another line (`ocr-margins.json`, `.md`).

`ocr-probe` reads one PDF that has no ground truth, such as a real or
handwritten scan, and reports counts only: per page words, lines, mean
confidence, seconds and entities by type, and whether the leak check passed.
No text and no file name reach its output (`ocr-probe.json`, `.md`), so it can
run on a document holding personal data. With `--truth`, a JSON list of each
page's text (`scripts/make_mixed_sample.py --truth` writes one for the mixed
sample), it adds the character error rate.

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

`results.json` records the document set it was measured on (`document_set`:
a SHA-256 over the names and contents of `documents/*.toml`, and their
number). Files from before it was recorded (schema 1) have none.

## Over versions

The documents were written with the rules in view, so the benchmark is a
development and regression set, not held-out evidence (that is
`experiments/`). Across versions, a score moves when the code changes or when
the documents do: releases v0.2.0 and v0.3.0 were measured on 6 documents,
v0.4.0 and later on 26.

Each release attaches `benchmark-results.json`, the charts and a zip of all
pictures; `history` over the downloaded `benchmark-results.json` files of
several releases draws the change across versions:

```sh
for tag in $(gh release list --json tagName --jq '.[].tagName'); do
  gh release download "$tag" -p benchmark-results.json -D "history/$tag"
done
uv run python -m benchmark history history/*/benchmark-results.json --out charts
```

A line joins only runs on one document set: the same files, read as the same
number of planted items. Without a fingerprint, the document names stand in
for the files. The newest run's set is drawn solid, earlier sets dashed and
labelled with their size, so the jump from 6 to 26 documents is a new line
and not a step in one.

`backfill` gives one line over the versions: for each tag it checks out that
tag's code in a temporary git worktree, replaces its `benchmark/documents`
with the current ones, runs its own `benchmark run` (rules only unless
`--systems` says otherwise) and records the current set's fingerprint in
`<out>/<tag>/results.json`. Each tag syncs its own environment from its
`uv.lock`. Draw the backfilled runs with the release assets or alone:

```sh
uv run python -m benchmark backfill $(git tag -l 'v*' | grep -v v0.1.0) --out backfill
uv run python -m benchmark history history/*/benchmark-results.json backfill/*/results.json --out charts
```

A release and its backfill share a place on the version axis. A tag's own
harness reads only the carriers it knew (v0.2.0 and v0.3.0 skip form fields,
annotations, attachments and XMP), so its run scores fewer planted items and
starts a line of its own. v0.1.0 has no benchmark. The release assets are not
changed.

Pull requests get the same comparison as a regression check: the Checks
workflow runs `benchmark run --systems rules`, downloads the latest release's
`benchmark-results.json` and writes `benchmark diff` to the job summary: per
item type, found, readable after redaction, and left in the carrier, with a
change shown `before → after`, plus safe documents and false alarms. It notes
when the two runs are on different document sets, and never fails the job.

## Scores

- **found / partial / missed** — whether one detected span covers the planted
  item, only part of it, or none of it.
- **false alarms** — distinct detected texts overlapping no planted item;
  **per 1,000 words** — the same over every document's words, so documents
  of different lengths compare.
- **decoys removed** — listed strings that look personal but are not, and
  were redacted anyway.
- **per carrier** — found, and left there: still readable, whole or as a
  fragment, in the place the item was planted (the page or a surface kind).
  A surname left on the page is not counted against the bookmark that
  carries it too. **Per document
  kind** — the same scores over documents of one kind (cv, contract, ...).
- **not found / false alarms** — the report lists every item not found whole
  and every false alarm, by document, for error analysis.
- **safe** — after redaction, no planted item is readable, whole or as a word
  unique to it. The leak check only verifies that *detected* items are gone;
  this is the measure of what was never detected.

## Documents

Twenty-six documents: CVs, contracts (purchase, employment, flat rental),
invoices, letters, e-mail printouts, minutes, a filled-in form, a power of
attorney, an official decision and a hospital report, in Czech, Slovak and
English. Names appear in several grammatical cases, alone after "pan" or
"paní", with degrees, as first names or nicknames; addresses with and
without a postcode, split over form fields; decoys sit beside them: company
names, seats and IČOs, shared mailboxes, law citations, reference numbers
and dates that are not dates of birth.

Seven documents plant nothing: terms and conditions, a complaints policy, a
privacy notice, an employee handbook, sports-hall rules and two notices from
an office (`cs-terms`, `cs-notice`, `cs-gym-rules`, `cs-privacy-notice`,
`sk-terms`, `sk-waste-notice`, `en-handbook`). They are full of capitalised
role nouns ("Kupující", "Žadatel", "Poplatník", "Line Manager"), company and
authority names. Every finding in them is a false alarm, which is what
ordinary documents produce most of; the documents with planted items are
too dense with personal data to show it. A document without items lists
decoys instead. The later ones were written without looking at the name
filter's role lists, so that they test the filter rather than mirror it.

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

Strings outside the page text, each a carrier redaction has to clear:

```toml
fields = [{ label = "Jméno:", value = "[[person:Jan Novák]]" }]        # text form field
annotations = [{ author = "[[person:Eva Malá]]", text = "Ověřit." }]   # sticky note
attachments = [{ filename = "novak-doklad.pdf", description = "Doklad" }]
xmp = { creator = "[[person:Jan Novák]]", title = "Dopis" }           # Dublin Core
```

A field's value is drawn on the page as well as stored in the field, so it
plants two items: one on the page, one in the field. MuPDF draws a value
with Czech letters a little low, so the top of it is clipped in pictures;
the text is unaffected. The annotation's author
is its title, usually a person's name. Attachment contents are fixed neutral
text: ingest never reads them, and redaction drops attachments whole.

`[[type:text]]` plants an item (types as in `EntityType`); `{{filler:N}}`
adds N words of neutral text. Use invented names, `example.com/.org/.net`
addresses, and checksum-bearing values computed independently of the
validators under test.
