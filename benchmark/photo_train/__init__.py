"""Invented Czech and Slovak documents for fine-tuning on phone photos (RQ3 post hoc).

The 22 Czech and Slovak benchmark documents (`benchmark/documents/cs-*`,
`sk-*`), laid out as printed in `benchmark/photo_test/` and photographed, are
the photo test set. Fine-tuning on
photos needs photos of other documents: this package writes them. Two splits,
from the same templates:

- `print`: 16 single-page documents per language, every template twice,
  committed in `documents/` so the printed pages stay fixed. Martin prints and
  photographs them like the test set, in separate sessions.
- `synthetic`: any number of further documents with another seed, which a
  later step renders and degrades in code.

Documents are written in the benchmark's own format (`benchmark.spec`), with
gold items marked inline, and rendered by `benchmark.render`. They live
outside `benchmark/documents/`, so `python -m benchmark run` never reads them
and the benchmark's numbers do not move. Only page text is written: a photo
carries no metadata or bookmarks.

Disjoint from the test data (`tests/benchmark/test_photo_train.py`):

- no word 5-gram of a template line (slots read as one placeholder) is shared
  with a benchmark document, the held-out set (`experiments.heldout`) or any
  other string of `experiments/`, `scripts/` and the rest of `benchmark/`;
- no name word is shared with the benchmark's people, the held-out set or the
  name-forms set;
- birth numbers, account numbers, IBANs and IČOs are computed by `values.py`,
  and the tests check them with the core validators.

Command: `python -m benchmark photo-train --out DIR [--split synthetic --count N]`.
"""

from benchmark.photo_train.generate import DOCUMENTS, LANGUAGES, SPLITS, generate, write
from benchmark.photo_train.pack import render_split

__all__ = ["DOCUMENTS", "LANGUAGES", "SPLITS", "generate", "render_split", "write"]
