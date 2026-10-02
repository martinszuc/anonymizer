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

### 2026-09-29 · GLiNER (`--ner`) on the samples

`gliner-multi-v2.1`, labels "person" and "street address", threshold 0.3,
rules for the document language alongside.

- **Real CS CV:** 1 page; 12 entities (person 4, address 2, phone 2,
  email 2, URL 2), 10 hidden items removed, leak check passed. The author
  checked the output visually: the name is removed everywhere and nothing
  personal remains visible. Names were the gap left by the rules alone
  (see *Redaction of the real samples*).
- **Synthetic EN CV:** the name, the street address and the ZIP code were
  found. False positives at this threshold: a job title and the metadata
  producer string, both tagged as persons.
- **The leak check refused the synthetic CV although redaction was
  correct.** The object and raw-byte layers search each entity's text as a
  plain substring. The ZIP code `20001` occurs inside the content-stream
  operand `9.200012`, which is layout, present in the original too. A model
  can tag a bare short number, which no rule produced before. The check
  fails safe (nothing is written) but blocks correct output. **Fixed:** in
  those two layers a text starting or ending with a digit must not continue
  into another digit or a decimal number; stored as text (`(20001)`,
  `(20001 12)`, `ZIP:20001`) it is still found.
- GLiNER reads at most 384 of its word tokens and drops the rest with only
  a warning. Without windowing, names on the lower half of a full page would
  never be seen, and no score would show it.

### 2026-09-29 · First benchmark run (`benchmark/`, version 0.1.0)

Six synthetic documents (CS CV, contract, invoice, long minutes; SK letter;
EN CV), 51 planted items, 10 of them in links, metadata or a bookmark.

| | rules | rules + GLiNER |
|---|---|---|
| items found whole | 19/51 | 42/51 |
| names found | 0/23 | 22/23 |
| distinct false alarms | 1 | 3 |
| documents with nothing readable left | 0/6 | 2/6 |
| leak check passed | 6/6 | 6/6 |

- **Addresses are cut in half:** GLiNER's "street address" covers the street
  and number but not the postcode and town (0/6 whole, 6/6 partial), which
  stay readable. Address fragments remain in all four unsafe documents and
  are the only residue in two of them (EN CV, SK letter).
- **Dates of birth are never found** (0/2): no rule and no prompt label
  covers them.
- **One inflected name missed:** the genitive "Petra Svobody"; the
  nominative, dative and instrumental forms were found.
- False alarms: "Kupující" (buyer), "Smluvní strany" (contracting parties)
  as persons; the buyer company's IČO by the rules (by design: an IČO with a
  label is always flagged).
- The name after word 420 of the long document was found: the windowing works.
- The leak check passed everywhere, including documents that were not safe:
  it verifies that what was *detected* is gone, not that nothing personal
  remains. The benchmark's residue check is the one that measures safety.

### 2026-09-30 · Benchmark after the date-of-birth and address rules

Same six documents and 51 items; version 0.2.0 plus the review window and the two rules.

| | rules | rules + GLiNER |
|---|---|---|
| items found whole | 19 → 27/51 | 42 → 50/51 |
| dates of birth | 0 → 2/2 | 0 → 2/2 |
| addresses whole | 0 → 6/6 | 0 → 6/6 (was 6/6 partial) |
| distinct false alarms | 1 → 1 | 3 → 3 |
| documents with nothing readable left | 0/6 | 2 → 5/6 |

- **Dates of birth need a label, and have one.** Both planted dates follow
  `nar.` or `Datum narození`; the invoice's issue and due dates were left
  alone.
- **The postcode anchors the address.** GLiNER's street-only span now lies
  inside the rule's whole address and is dropped when the results merge.
- **A wrapped line split an address** after the postcode (`586 01` /
  `Jihlava`): the page text keeps the line break, so the rule allows one
  there and after the comma, but not inside the town, where it would take
  the next line's first word.
- **The one remaining miss** is the genitive `Petra Svobody` (NER, see the
  first run); it leaves the contract the only unsafe document.

### 2026-09-30 · Searchable scans (synthetic)

A searchable scan is a page-sized picture under an invisible OCR text layer
(render mode 3) written by whoever made the scan searchable. Probed with
generated scans (`tests/redact/test_searchable_scans.py`); ink counted in
the image data stored in the saved output, not in a rendering.

- **Ingest reads the invisible layer** as ordinary text, so detection and
  redaction run as on a born-digital page. `get_texttrace()` reports the
  spans as type 3, which tells them apart from visible text.
- **With the layer over the ink, redaction removes the ink** under every box
  and nothing else, for a Flate and a JPEG picture (redaction re-encodes the
  JPEG as Flate), a picture inside a form XObject and a `/Rotate 90` page.
  The invisible text under the boxes is gone and the leak check passes.
- **A layer narrower than the printed words leaks, and nothing notices.**
  With word boxes shorter than the ink, the end of the value stays readable
  in the picture, while the text layer is gone and the leak check passes:
  no layer of it reads image pixels. The redaction box is only as good as
  the producer's OCR geometry. How well real producers align is unknown; no
  real searchable scan has been checked.
- **A scan carrying a few digital words looked born-digital.** A page with
  any text-layer word counted as having a text layer, so a scanner's stamp or
  a page number sent the whole picture past OCR, unread. Ingest now treats a
  page at least half covered by pictures with fewer than 20 visible words
  over them as needing OCR (a heuristic, unchecked on real scans).
- Picture encodings are covered for pages OCR read (next entry); JBIG2 and
  JPEG 2000 are not probed (no pip-installable JBIG2 encoder).

### 2026-09-30 · Redaction of pages OCR read (synthetic)

Boxes from a stand-in engine reporting the born-digital original's words;
ink counted in the stored image data (`tests/redact/test_scanned_pages.py`).

- **Pixels under every box are overwritten in every encoding tried:** Flate,
  JPEG, CMYK JPEG, black-and-white CCITT G4, a 1-bit stencil mask of the
  text over a background photo (mixed raster content, as compressed
  searchable scans store a page), a picture split in two strips across a
  line of text, and a rotated page. The rest of each picture is unchanged.
- MuPDF re-encodes a redacted picture: JPEG and CCITT pictures come back as
  Flate, a redacted stencil mask as CCITT.
- **Text on a page OCR read was never checked**, since detection read the
  pixels: a stamp, text drawn under the picture (hidden by it, still
  extractable) or in white. Redaction removes the whole text layer of such a
  page, painting no fill.
- **Fixture traps:** PyMuPDF re-encodes what `insert_image` receives (a G4
  TIFF or a palette PNG arrives as Flate), so CCITT and stencil pictures are
  written by hand; writing the stream drops its `/Filter`, which then
  decoded compressed bytes as pixels and made the whole box look inked; and
  Pillow splits a G4 TIFF into several strips unless told otherwise. Each
  was caught by checking the fixture before redacting.

### 2026-10-01 · Scanned benchmark with a perfect reader (synthetic)

`python -m benchmark ocr --engines oracle`, six documents, 16 levels; the
oracle reads the ground truth, so every error is the pipeline's, not OCR's.
Rules only.

- **The first OCR leak layer refused correct redaction on skewed scans:**
  2 of 6 documents failed at 1° of skew, 5 at 3° and all 6 at 5°. An
  axis-aligned box around a tilted value clips the corners of the words on
  the lines around it, and the layer counted any overlap as a word under a
  box. Fixed: a word counts when half its box or more is inside. Real scans
  are often skewed by a degree or more, so export would have been refused.
- **Skew costs over-redaction:** the same boxes black out parts of
  neighbouring labels; at 5° one item detection had missed became partly
  covered by a neighbour's box.
- With perfect reading, the rules find the same 23 of 41 on-page items at
  every level, and every found item leaves no ink. The other 18 (names,
  mostly) are detection misses, not OCR losses; GLiNER was not run here.
- The oracle's first version decided "still printed" by a fixed ink
  threshold and missed 7 % of words at blur radius 3, where ink turns light
  grey; it now compares each word with its first reading.

### 2026-10-01 · OnnxTR on the scanned benchmark (synthetic)

`python -m benchmark ocr --engines oracle,onnxtr`, six documents, 16 levels,
rules only; OnnxTR with FAST base and PARSeq multilingual v1 on the CPU.

| level | CER | diacritics | items found | partly readable after | s/page |
|---|---|---|---|---|---|
| clean | 1.1 % | 0.0 % | 22/41 | 0 | 1.5 |
| resolution 100 DPI | 1.4 % | 0.9 % | 16/41 | 0 | 1.4 |
| noise σ 50 | 1.1 % | 0.0 % | 20/41 | 0 | 1.4 |
| skew 1° | 5.0 % | 3.1 % | 21/41 | 0 | 1.3 |
| skew 5° | 0.5 % | 0.0 % | 22/41 | 0 | 1.3 |

(The oracle finds 23/41 at every level; the leak check passed in all 96 runs.)

- **Czech letters are read reliably** by the multilingual recognizer; docTR's
  own recognizers lack háček letters altogether. One dash (—) was dropped
  in a probe.
- **Read as straight, a skewed page fell apart:** at 3° the character error
  rate was 41 %, at 5° 56 %, with detection down to 11/41. A tilted line was
  split into pieces in the wrong order and tilted words misread. Read in
  rotated mode it stays under 1 % at 3° and 5°; 1° is an unexplained outlier
  at 5 %.
- **OCR boxes hug the ink and clip letter edges.** On clean scans 322 of 750
  words had ink outside their boxes, and at most levels one or two items
  detection had found stayed partly readable after redaction, while the leak
  check passed. Growing every OCR box by 15 % of its height brought this to
  4 of 750 words and no partly readable item at any level.
- **OnnxTR downloads models it is not handed:** building its rotated-mode
  predictor fetched two orientation classifiers (6 MB each) into
  `~/.cache/onnxtr` during an experiment. The loader now disables them and
  makes any download raise.
- **onnxruntime's default providers on macOS** start with CoreML, which fails
  to build the recognizer, and include Azure's remote provider; the engine
  runs on the CPU provider only.
- Missed items are detection misses (mostly names: rules only), not OCR
  losses: the oracle finds just one more. That one is an email on the clean
  CS CV: OnnxTR read its `@example` as `(mexampie`, so no rule matched and
  the address stayed readable while the leak check passed. A misread
  separator hides a structured value from the rules entirely.

### 2026-10-02 · False alarms from the name model

Three benchmark documents with no personal data at all (Czech terms and
conditions, Czech official instructions, Slovak complaints policy) next to
the six earlier ones; GLiNER at threshold 0.3. Development sets: CNEC 2.0
dtest (cs, 524 person spans) and UNER Slovak-SNK dev (276), scored with
partial match; only counts and scores were printed, never corpus text.

| | false alarms | per 1,000 words | items found | leak check |
|---|---|---|---|---|
| before | 33 | 17.2 | 50/51 | 8/9 |
| + "organization" label | 31 | 16.1 | 50/51 | 7/9 |
| + name filter (shipped) | 4 | 2.1 | 50/51 | 9/9 |

| person spans | CNEC P | CNEC R | UNER-SK P | UNER-SK R |
|---|---|---|---|---|
| before | 0.846 | 0.796 | 0.722 | 0.634 |
| + "organization" label | 0.862 | 0.821 | 0.738 | 0.667 |
| + name filter (shipped) | 0.916 | 0.821 | 0.789 | 0.667 |

- **Role nouns were the false alarms.** 30 of 33 lay in the documents
  without personal data, nearly all capitalised role nouns in every case:
  "Kupující", "Kupujícímu", "Žadatele", "Vedoucí odboru …", "Zákonný
  zástupce žáka". The six earlier documents, dense with planted items,
  showed 3 and hid the problem.
- **More labels did not move them.** Offered "job title", "role" or
  "location" as well, the model kept the role nouns as persons and lost
  precision on the corpora. "Organization" alone raised precision and
  recall on both corpora, and is kept.
- **A higher threshold costs recall first.** On CNEC, 0.3 → 0.5 raised
  precision 0.85 → 0.89 and dropped recall 0.80 → 0.67; on the benchmark it
  removed 4 of 33 false alarms. The role nouns score high.
- **The name filter** (`detect.NamesOnly`) trims lowercase words from the
  edges of a model's person span and drops a span whose capitalised words
  are all role nouns of the document's language. On the corpora it dropped
  29 (CNEC) and 16 (UNER-SK) person spans, **none of them a gold name**, and
  trimmed 21 and 14 to the name, which raised strict-match precision too.
  The role lists were written with the benchmark documents in view; the
  corpora were not used to write them and are the independent check.
- **A role noun failed the leak check.** With "Žadatel" detected and the
  inflected "Žadatelem" not, the redacted page still contained the detected
  text inside the longer word, and the page-text layer refused the copy. For
  a surname (Novák found, Nováka missed) that refusal is correct: the
  inflected form still names the person. Fewer false alarms made all 9
  documents pass.
- Left: two street names without a number tagged as addresses, "Starosta"
  (a surname as well as a mayor, left off the role lists on purpose) and a
  labelled company IČO (rules, by design).

### 2026-10-02 · Benchmark grown to 26 documents

Seventeen new synthetic documents (`benchmark/documents`): employment and
rental contracts, a form filled in on screen, a power of attorney, an
official decision, e-mail printouts, owners' minutes, an invoice, a CV and
a hospital report, in Czech, Slovak and English, plus four documents
without personal data written without looking at the name filter's role
lists. 224 planted items (was 51), 45 of them outside the page text in
seven carriers: links, metadata, a bookmark, and now form fields, notes,
attachments and XMP. Commit `bde70da`, GLiNER at threshold 0.3.

| | rules | rules + GLiNER |
|---|---|---|
| items found whole | 27/51 → 86/224 | 50/51 → 199/224 |
| names found | 0/23 → 0/128 | 22/23 → 110/128 |
| distinct false alarms | 1 → 14 | 4 → 44 |
| per 1,000 words | 0.5 → 3.0 | 2.1 → 9.4 |
| documents with nothing readable left | 3/9 → 8/26 | 8/9 → 17/26 |
| leak check passed | 9/9 → 26/26 | 9/9 → 25/26 |

The nine earlier documents score as before (50/51, 4 false alarms); their
word count grew from 1,921 to 1,928 because link anchors are now counted.

- **A name written as one word is mostly missed:** 5 of 16 on the page,
  against 80 of 81 names of two or more words. Missed: a surname after
  "pan"/"paní" or in a later sentence (Sýkora, Bartoš, Musil, Vránu,
  Zemanem, Hruškové, Hudák), a vocative ("pane Navrátile"), a nickname
  ("Báro") and English first names ("Megan", "Sam"). Occurrence propagation
  does not help: it repeats the detected text, and the surname alone is not
  that text. These are most of what leaves 9 documents unsafe.
- **The role lists do not carry over to new documents.** The three
  documents they were written with produce 3 false alarms in 1,178 words;
  the four written without looking at them produce 28 in 992. Role nouns
  missing from the lists ("Poplatník", "Zákazníka", "Uchazeče",
  "Pověřenec", "Trenér", "Údržbář", "Prednosta", "Vlastník") and English
  roles, for which no list exists ("Employee", "Line Manager", "Head of
  People"), are tagged as persons; so are "Priemyselnej ulici" and the
  emergency numbers "na čísle 155" as addresses.
- **The English handbook failed the leak check** for the reason recorded
  above for "Žadatel": "Employee" was detected, "Employees" was not, and
  the page-text layer found the detected text inside the longer word.
- **A law citation is a valid account number.** "zákona č. 262/2006 Sb.",
  the Labour Code that every Czech employment contract cites, passes the
  account checksum (262 weighted is 22) and was redacted as a bank
  account. A citation number/year is a valid account roughly one time in
  eleven.
- **Every rule false alarm is by design:** a labelled company IČO, company
  seats and an authority's address, shared mailboxes (`recepce@`, `hr@`),
  a bank's PO box. Recall-first rules cannot tell them from personal ones.
- **A label separated from its value hides it.** Text extraction returns
  form field values after every printed label, so "Datum narození:" is not
  followed by the date and the rule misses it (the field is cleared
  anyway). "my date of birth is March 12, 1990" is missed because of the
  "is" between label and date.
- **No rule covers** an identity card number, a Slovak DIČ, a car
  registration plate or a British mobile number (`+44 7700 …`), and GLiNER
  found none of them. The identity card number was redacted all the same,
  by chance: its nine digits also read as a birth number from before 1954,
  which has no check digit. A US address with "Apt 4B" was found in part.
- **Hidden carriers are cleared whatever detection finds.** With rules only,
  no item in a form field, note, attachment, XMP packet, link, bookmark or
  metadata entry was left in its carrier; every residue is page text. A
  form whose answers are all fields is safe without detection, since
  deleting a field removes its drawn value too.
- **Detection on hidden carriers is uneven:** names in the XMP packet
  (1/4) and an attachment file name written without diacritics
  ("op-hruskova-sken.pdf") are not found; review would not show them as
  findings although redaction removes them.
- **Two generator quirks seen in passing:** PyMuPDF reads an attachment's
  file name containing "í" as "Ã­" (`embfile_info`), so ingest shows a
  garbled name; and in field appearances MuPDF draws punctuation that text
  extraction then omits when the value has letters outside Latin-1 ("Ing.
  Markéta" reads as "Ing Markéta"). Benchmark field values avoid both.
- **Scanned, perfect reader, 3° skew:** the leak check refused 2 of 26
  correct redactions. A short word on a neighbouring line ("dne", "se",
  "is") lay half under a tilted box: the half-box threshold recorded
  under *Scanned benchmark with a perfect reader* is not enough for
  two- and three-letter words.

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
| Raster image | pixels inside the box overwritten in the image data; rest intact (also JPEG, CMYK, CCITT G4, stencil masks, strips) |
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
- **PyMuPDF garbles attachment names with diacritics** (1.28.2). `embfile_names`,
  `embfile_info` (`name`, `filename`, `ufilename`) and `Annot.file_info`
  (`filename`) take MuPDF's correctly decoded UTF-8 and map each byte to a
  character, so a `/UF` stored as UTF-16BE comes back as `KratochvÃ­l` for
  `Kratochvíl`; descriptions (`/Desc`) are not affected. Ingest reads the file
  specification through MuPDF's `pdf_to_text_string` instead. Repairing the
  string (`encode("latin-1").decode("utf-8")`) would break silently once PyMuPDF
  fixes the bug. Deleting by the garbled name still works, since the lookup
  garbles the same way.
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
  **Correction 2026-09-29:** the limit is the *non-embedded* standard 14 font
  with its single-byte encoding, not the typeface. MuPDF bundles Nimbus Sans
  and Nimbus Roman (URW's Helvetica and Times clones) with full Latin
  Extended coverage; written through `TextWriter` with `Font("helv")` they are
  embedded as CID fonts, and Czech and Slovak text round-trips exactly and
  renders correctly (checked visually). The benchmark generator uses this; no
  font download is needed.
- **Checksum strength varies enormously.** Mod-11 on a rodné číslo rejects ~10 of
  11 wrong strings; Luhn alone accepts 1 in 10; IČO mod-11 accepts 1 in 11, which
  on an invoice full of variable symbols is worthless without a label. US SSNs have
  no checksum at all. Detector precision is therefore not uniform across entity
  types, and the evaluation must report per-type, not aggregate.

### 2026-09-30 · Mixed synthetic sample (`scripts/make_mixed_sample.py`)

Four pages, all values invented: typed form with hidden items, scanned form,
handwriting-font scan, typed text beside a scanned stamp.

- Page 1 and the typed text on page 4: 8 entities (birth number, IBAN, email,
  2 phones, address, date, link URL) and 14 hidden items; the export passes the
  leak check and clears links, metadata, bookmarks, the attachment and the form field.
- Pages 2 and 3 have no text layer; `redact` stops unless
  `--allow-pages-without-text` is given, and then warns that they are not redacted.
- First attempt used a rodné číslo that failed its own mod-11 check, and the
  detector rightly skipped it: a fixture value is computed, not guessed.
- Handwriting here is a font, so it says nothing about recognition quality.

---
