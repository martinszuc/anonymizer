# anonymizer-cli

Command-line client for `anonymizer-core`. Runs fully offline.

```sh
anonymize detect cv.pdf -o review.json --lang cs --show   # find, save for review
anonymize redact cv.pdf -o cv-redacted.pdf --session review.json
anonymize redact cv.pdf -o cv-redacted.pdf --lang cs      # one step, no review
anonymize check cv-redacted.pdf --source cv.pdf --session review.json
anonymize inspect cv.pdf -o cv.html [--session review.json]  # see what was found
anonymize redact photo.jpg -o photo-redacted.pdf --ocr onnxtr  # a photo or scanned image
```

**Images.** Every command that takes a PDF also takes a JPEG, PNG or TIFF image (told
apart by content, not by the file name; HEIC is refused, so export iPhone photos as
JPEG). The image is turned upright by its EXIF orientation and wrapped into a PDF
holding only its pixels, one page per TIFF frame; its EXIF, GPS position, XMP and
text chunks never reach the output. The page size follows the resolution the image
records when it is between 100 and 1200 DPI, else 300 DPI is assumed (cameras record
72). An image has no text layer, so it needs `--ocr`: without it `detect` and
`inspect` refuse it as having nothing to review, and `redact` as a scan OCR has not
read. The redacted copy is always a PDF.

**Language.** `--lang` picks the rules (`cs`, `sk`, `en`); without it every
rule runs. `--lang auto` recognises the language from the text (py3langid, offline)
and falls back to every rule when the text is in another language or too short to
judge; the session records what was used.

To try the commands without a real document, generate the synthetic sample
(`uv run python scripts/make_mixed_sample.py`, see the root README, *Try it on a
sample*). Keep `review.json` with its PDF or image: a session only applies to the
file it was made from, and `check` rejects a session from a different file.

**Names and addresses.** The rules find identifiers; names need the GLiNER model.
Install its dependencies (PyTorch; kept optional) and fetch the model once, then
add `--ner`:

```sh
uv sync --group ner
uv run python scripts/download.py fetch gliner-multi-v2.1
anonymize redact cv.pdf -o cv-redacted.pdf --lang cs --ner
```

The model is read from `models/` under `--resource-root` (default: the folder chosen in the review window (*Manage models… → Change…*), else
`./models` if the working directory has one (a checkout of this repository),
else a per-user folder (`~/Library/Application Support/anonymizer` on macOS,
`%LOCALAPPDATA%/anonymizer` on Windows, `~/.local/share/anonymizer` on Linux)) and never contacts the network.

**Seeing what was found.** `inspect` writes one HTML file: every page as an image
with the detected boxes drawn over it, coloured by type (hover for details, rejected
items dashed, hidden items dotted), and the entities and hidden items listed per page.
Checkboxes hide a type. The file embeds everything and its security policy blocks all
loading, so opening it sends nothing anywhere, but it contains the document's content:
keep it out of the repository and delete it like the original.

**Reviewing without a UI.** `review.json` lists every item found. Set an item's
`"review"` to `"rejected"` to keep it in the output. To redact something without
text (a photo, a signature), add an entity
`{"type": "region", "page_index": 0, "bboxes": [[x0, y0, x1, y1]], "source": "manual"}`
with the box in PDF points, origin top-left. The session holds the marked snippets
and a fingerprint of the file, not the whole text, and only applies to that file.

**Safety.**

- A redacted copy is written only if the leak check passes; otherwise nothing is
  written and the leaks are listed.
- Scanned pages (no text layer, or only a few words over a picture) are read with
  `--ocr onnxtr` (`uv sync --group ocr-onnxtr`, then
  `uv run python scripts/download.py fetch onnxtr-parseq-multilingual-v1`) or, for
  handwriting, `--ocr kraken` (`uv sync --group ocr-kraken`, macOS and Linux x86-64
  only, then `uv run python scripts/download.py fetch kraken-ppocr-v6-medium`). Their
  pixels under each box are overwritten, their text layer removed, and the leak
  check re-reads them with the same engine. A review of scanned pages reopens, and
  `check` runs, only with the same `--ocr`. Without it, scanned pages stop the run;
  `--allow-pages-without-text` redacts the rest and leaves them as they are.
- Existing files are replaced only with `--force`; the output is never the input.
- Every link, metadata field, attachment, bookmark, annotation and form field is
  removed, as is anything outside the visible page area.

Exit codes: `0` success, `1` error, `2` invalid arguments, `3` leak found.
