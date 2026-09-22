# anonymizer-cli

Command-line client for `anonymizer-core`. Runs fully offline.

```sh
anonymize detect cv.pdf -o review.json --lang cs --show   # find, save for review
anonymize redact cv.pdf -o cv-redacted.pdf --session review.json
anonymize redact cv.pdf -o cv-redacted.pdf --lang cs      # one step, no review
anonymize check cv-redacted.pdf --source cv.pdf --session review.json
```

**Reviewing without a UI.** `review.json` lists every item found. Set an item's
`"review"` to `"rejected"` to keep it in the output. To redact something without
text (a photo, a signature), add an entity
`{"type": "region", "page_index": 0, "bboxes": [[x0, y0, x1, y1]], "source": "manual"}`
with the box in PDF points, origin top-left. The session holds the marked snippets
and a fingerprint of the PDF, not the whole text, and only applies to that PDF.

**Safety.**

- A redacted copy is written only if the leak check passes; otherwise nothing is
  written and the leaks are listed.
- Pages without a text layer (usually scans) stop the run, since they cannot be
  read yet; `--allow-pages-without-text` redacts the rest and leaves them as they are.
- Existing files are replaced only with `--force`; the output is never the input.
- Every link, metadata field, attachment, bookmark, annotation and form field is
  removed, as is anything outside the visible page area.

Exit codes: `0` success, `1` error, `2` invalid arguments, `3` leak found.
