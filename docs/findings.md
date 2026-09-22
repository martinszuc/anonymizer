# Findings

Empirical notes from running the pipeline against real files. Each entry is
evidence for the thesis rather than only a work item: the analysis chapter can
cite these instead of asserting them. Corresponding work items live in `PLAN.md`.

Sample documents are never committed. They sit in `data/samples/` (git-ignored);
files named `*-real-*` contain genuine personal data and are used for manual runs
only — never as fixtures or training data. Nothing identifying is quoted here.

### 2026-09-22 · `resume-en-borndigital.pdf` — synthetic EN CV

- Ingest worked first try on a real-world PDF: 1 page, 225 words, correct reading
  order across blocks, bullet glyphs preserved.
- Rules found the email only. The US phone `(123) 456-7890` was missed — the
  pattern was CZ/SK-only. **Fixed:** locale-scoped finders, NANP added.
- Strict NANP validation would *still* have missed it: the fake area code starts
  with `1`, which the numbering plan forbids. Hence the rule that formatted
  numbers are accepted on layout and only bare digit runs must satisfy structure.
- Street address missed. No checksum for addresses exists in any locale → NER or
  gazetteer territory, not the rule layer.

### 2026-09-22 · `resume-real-en-borndigital.pdf` — real EN CV (react-pdf)

- **Link annotations carry identity the text layer does not.** Visible words:
  "Github, LinkedIn". Annotation URIs: `mailto:…`, `github.com/<handle>`,
  `linkedin.com/in/<name>`. Detection over `Page.text` cannot see them and
  redacting page content leaves them clickable in the "anonymized" output.
- Metadata title carried the job description.
- **Every information dictionary value is a separate string object** (react-pdf).
  A reader that takes only inline strings sees no metadata at all, so the first
  surface scan missed the title on exactly the file that motivated it.
- After the surface scan: the `mailto:` target is detected. The two profile links
  and all four metadata values produce no entity — no rule describes a profile
  URL or a free-text title.

### 2026-09-22 · `resume-real-cs-borndigital.pdf` — real CS CV (Skia / headless Chrome)

- **Same leak, different producer** → this is how PDFs work, not one library's
  quirk: `tel:+…`, `mailto:…`, site links, plus a metadata title containing the
  the submitter's account ID.
- Metadata values are inline strings here, unlike react-pdf. `ModDate` equals
  `CreationDate`: a scan that de-duplicates equal values drops one of two carriers.
- After the surface scan: `tel:` and `mailto:` targets are detected. Two site
  links and all five metadata values, including the title with the account ID,
  produce no entity.
- **Tagged PDF.** The file carries a structure tree for accessibility, with one
  `Alt` description. The first redaction removed the `tel:` and `mailto:` links
  from the page, yet both link annotations, targets included, survived in the
  output: the structure tree still referenced them, so garbage collection kept
  them. Only the object-level leak check noticed; the surface scan saw nothing.
  Redaction now removes the structure tree, and ingest lists its text.
- The Slovak phone matched only because `+` was present. A bare `421918446150`
  (the form OCR produces when it drops the plus) was missed, and `421 918 446 150`
  matched only its first nine digits — a partial match that would have left the
  rest unredacted. The Slovak domestic form with a trunk zero (`0918 446 150`) was
  missed as well. Fixed.
- **The file name was `<name>-<id>-Zivotopisy.cz.pdf`** — full name plus
  account ID. The contract stores `source_name` in every exported review JSON, so
  the file name is itself a PII surface. Open decision below.
- The person's name mixed `ü` with `č`, which is not standard Czech orthography.
  A good stress case for OCR and NER: do not assume a fixed Czech character set,
  and do not treat an unexpected letter as evidence against a name.

### 2026-09-22 · Surface coverage of the samples

Of the eight surface kinds ingest lists, the real samples exercise three: link
annotations, the information dictionary and (CS CV only) the structure tree.
None carries XMP, form fields, bookmarks, annotations or attachments. Those five
kinds are covered only by synthetic fixtures, so a real document of each kind is
still worth finding.

Detection over surfaces catches what the finders already know (`mailto:`,
`tel:`); it misses profile URLs and free-text metadata entirely. Clearing a
surface therefore cannot depend on an entity having been found in it.

With the site-independent URL rule every link on both real CVs yields an entity,
and no page-text URL is flagged by mistake. Metadata is the one surface kind no
rule reaches: the title carrying a job description or an account ID is free text.

### 2026-09-22 · Redaction of the real samples

Both real CVs redact with no leak in any of the four leak-check layers (page
text, surface scan, objects, raw bytes). Names remain: nothing detects them yet.

### Toolchain findings: redaction

- **Redaction annotations take unrotated coordinates.** Giving them the rotated
  box on a rotated page removes nothing and raises no error: a silent leak.
- **An incremental save keeps old revisions.** After an incremental update the
  old value is gone from every object the file's table points to, but still in
  the raw bytes. Unlinking the information dictionary and saving incrementally
  does not even take effect: the trailer keeps pointing to it.
- Deleting a form field also removes its value from the page text, since the
  value was only drawn in the field's appearance.
- One box per word leaves gaps that show how a value was grouped (a phone number
  as four blocks); an entity's boxes on one line are merged before redacting.

### Toolchain findings: what a redaction box really removes

Verified on saved files, one probe per kind of content under a box:

| Under the box | Result |
|---|---|
| Text, also inside a form XObject | removed |
| Raster image | pixels inside the box overwritten in the image data; rest intact |
| Image shared by two pages | redacted copy made for the redacted page; the other page untouched |
| Image with transparency | mask made uniform inside the box (no shape left); unchanged outside |
| Vector drawing fully under the box | **kept** with PyMuPDF's normal setting; removed with the strict setting (`graphics=2`), which also deletes any line merely touching the box |
| Page thumbnail (`/Thumb`) | **kept**: a small picture of the unredacted page |

- **Content outside the visible area is invisible to PyMuPDF's extraction**, even
  unclipped: text outside the crop box or beyond the media box is simply not
  returned, yet it is in the file. Enlarging the media box exposes it.
- PyMuPDF reports the crop box measured from the top of the media box, while the
  PDF stores it from the bottom; converting between the two is needed before any
  geometry changes.
- A test image built without real transparency made the first transparency probe
  meaningless. Probes check the fixture's starting state first.
- None of the real samples has content outside the visible area or a thumbnail;
  those fixes are exercised by synthetic files only.

- `Page.apply_redactions()` removes a link only if a redaction box overlaps its
  rectangle; links elsewhere on the page survive. A URL entity whose box is the
  link's own rectangle therefore removes the link through the ordinary redaction
  path.
- `Document.scrub()` removes all links, metadata, XMP, attachments, JavaScript
  and form values, but has no option for bookmarks or annotation text. Re-running
  the surface scan on the output is what shows a gap like this.
- Links inserted in memory are not returned by `get_links()` until the document is
  saved and reopened. A test that skips the round trip reports "no links" and
  proves nothing.

### Toolchain findings

- **PyMuPDF geometry:** word boxes come back in the *unrotated* coordinate system
  while `page.rect` reflects rotation. Without mapping through
  `page.rotation_matrix`, every box on a rotated page is silently misplaced.
  Verified empirically, handled in ingest.
- **PyMuPDF rectangle conventions differ by object.** Words, annotation and
  widget rectangles come back unrotated; link rectangles (`get_links()`) come back
  already rotated. One conversion for all of them misplaces either the links or
  everything else on a rotated page.
- **PyMuPDF's `doc.metadata` is not the information dictionary.** It resolves
  references, but reports only the standard keys and adds a `format` entry that is
  not in the file. Custom keys (`Company`) need the raw dictionary, and values
  stored as references need MuPDF's metadata lookup to decode.
- **Form field values leak twice.** The value is also drawn into the widget's
  appearance stream, so it shows up in `Page.text` as well as in the field.
- PyMuPDF percent-encodes launch-link file paths (`C%3A/...`), and a `mailto:`
  target may be percent-encoded by its producer. Targets are decoded before
  detection.
- `Document.new_page()` detaches `Page` objects fetched before it; fixture
  builders must create pages first and fetch them afterwards.
- **Base-14 fonts cannot encode Czech.** Helvetica has no `č`, `ř`, `ž`, so PDF
  test fixtures are limited to Latin-1 text and NFC handling is covered by a
  separate unit test. The MG generator must embed a font with full Czech coverage
  (DejaVu, Noto) — otherwise a "Czech" corpus silently isn't one.
- **Checksum strength varies enormously.** Mod-11 on a rodné číslo rejects ~10 of
  11 wrong strings; Luhn alone accepts 1 in 10; IČO mod-11 accepts 1 in 11, which
  on an invoice full of variable symbols is worthless without a label. US SSNs have
  no checksum at all. Detector precision is therefore not uniform across entity
  types, and the evaluation must report per-type, not aggregate.

---
