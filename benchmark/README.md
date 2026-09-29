# Benchmark

Scores the pipeline on synthetic documents and produces material for
reports and presentations. Everything here is invented and safe to publish.

```sh
uv sync --group ner --group benchmark        # GLiNER and matplotlib
uv run python -m benchmark run --out benchmark-results
uv run python -m benchmark run --out benchmark-results --systems rules   # no model
uv run python -m benchmark history run-a/results.json run-b/results.json --out charts
```

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
