# Redaction leaks: anonymizer 0.7.0

Run 2026-11-11T02:02:47+00:00 on Darwin arm64, Python 3.12.14, commit `6b89b0b`. 26 documents, 276 planted items.

Targets are the planted items (an oracle), so only the redaction method differs. Each copy is saved and read again; an item counts when its own carrier still holds it, whole or as a word unique to it. Two items (Bohumil Zahradnik, Radomir Pekarek) are added to every document, for the carriers the benchmark does not plant.

## Items still extractable, per carrier

| carrier | planted | black rectangle | apply_redactions | this tool |
|---|---|---|---|---|
| page | 179 | 179/179 | 8/179 | 0/179 |
| link | 7 | 7/7 | 7/7 | 0/7 |
| metadata | 15 | 15/15 | 15/15 | 0/15 |
| xmp | 4 | 4/4 | 4/4 | 0/4 |
| form_field | 8 | 8/8 | 8/8 | 0/8 |
| annotation | 5 | 5/5 | 5/5 | 0/5 |
| bookmark | 2 | 2/2 | 2/2 | 0/2 |
| embedded_file | 4 | 4/4 | 4/4 | 0/4 |
| structure | 26 | 26/26 | 26/26 | 0/26 |
| off_page | 26 | 26/26 | 26/26 | 0/26 |
| all | 276 | 276/276 | 105/276 | 0/276 |

## Documents and the leak check

|  | black rectangle | apply_redactions | this tool |
|---|---|---|---|
| documents with nothing extractable | 0/26 | 0/26 | 26/26 |
| documents the leak check flags | 26/26 | 26/26 | 0/26 |
| copies the leak check refused | 0/26 | 0/26 | 0/26 |

## Leaks the leak check reports on each copy, by layer

| layer | black rectangle | apply_redactions | this tool |
|---|---|---|---|
| file_bytes | 43 | 43 | 0 |
| object | 49 | 49 | 0 |
| off_page_text | 52 | 52 | 0 |
| page_text | 160 | 8 | 0 |
| surface | 141 | 141 | 0 |

## Per document, items still extractable

| document | planted | black rectangle | apply_redactions | this tool |
|---|---|---|---|---|
| cs-contract | 14 | 14 | 2 | 0 |
| cs-cv | 16 | 16 | 8 | 0 |
| cs-decision | 15 | 15 | 3 | 0 |
| cs-email | 17 | 17 | 4 | 0 |
| cs-employment-contract | 20 | 20 | 6 | 0 |
| cs-gym-rules | 2 | 2 | 2 | 0 |
| cs-invoice | 8 | 8 | 2 | 0 |
| cs-long-report | 5 | 5 | 2 | 0 |
| cs-notice | 2 | 2 | 2 | 0 |
| cs-owners-minutes | 18 | 18 | 2 | 0 |
| cs-power-of-attorney | 13 | 13 | 4 | 0 |
| cs-privacy-notice | 2 | 2 | 2 | 0 |
| cs-rental-contract | 22 | 22 | 5 | 0 |
| cs-school-form | 20 | 20 | 20 | 0 |
| cs-terms | 2 | 2 | 2 | 0 |
| en-cv | 9 | 9 | 4 | 0 |
| en-email | 11 | 11 | 4 | 0 |
| en-handbook | 2 | 2 | 2 | 0 |
| en-letter | 13 | 13 | 4 | 0 |
| sk-cv | 14 | 14 | 6 | 0 |
| sk-email | 11 | 11 | 3 | 0 |
| sk-invoice | 11 | 11 | 3 | 0 |
| sk-letter | 11 | 11 | 4 | 0 |
| sk-medical-report | 14 | 14 | 5 | 0 |
| sk-terms | 2 | 2 | 2 | 0 |
| sk-waste-notice | 2 | 2 | 2 | 0 |
