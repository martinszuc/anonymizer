"""Recognising a document's language from its text, so its own rules run.

Rules are locale-scoped (`detect.finders_for`); without a language every rule
runs, which costs precision: North American phone numbers and US addresses
looked for in a Czech contract. A client may ask for `AUTO` instead of a
language, and the language is recognised from the page text once ingest (and
OCR) has read it.

Recognition uses py3langid (BSD-3-Clause), a naive Bayes model over byte
n-grams that ships inside the package: nothing is downloaded and nothing leaves
the machine. Only a language with its own rules is answered. A text in another
language, one too short to judge (a form with a name and a number), or a guess
below `MIN_CONFIDENCE` answers `None`, and every rule runs, as when no language
was given: a missed identifier leaks, a false alarm costs a click.

Czech and Slovak are close and short texts are confused, but they share their
rules, so the mistake costs nothing there.
"""

from __future__ import annotations

import logging
from functools import cache
from typing import TYPE_CHECKING

from anonymizer.core.detect import RULE_LANGUAGES

if TYPE_CHECKING:
    from anonymizer.core.types import Document
    from py3langid.langid import LanguageIdentifier

log = logging.getLogger(__name__)

AUTO = "auto"
"""Asked for instead of a language: recognise it from the text."""

MIN_LETTERS = 100
"""Fewer letters than this are not judged; a form's few values say little."""

MIN_CONFIDENCE = 0.9
"""Smallest probability, among every language the model knows, to accept a guess."""

SAMPLE_CHARS = 20_000
"""Characters of page text read; enough to judge, and quick on a long document."""


def recognise_language(text: str) -> str | None:
    """Return the language of a text, if it has its own rules and the guess is clear.

    Args:
        text: Text to judge.

    Returns:
        A code from `detect.RULE_LANGUAGES`, or `None`.
    """
    sample = text[:SAMPLE_CHARS]
    if sum(character.isalpha() for character in sample) < MIN_LETTERS:
        return None
    language, probability = _identifier().classify(sample)
    if language not in RULE_LANGUAGES or probability < MIN_CONFIDENCE:
        log.debug("language not accepted: %s at %.2f", language, probability)
        return None
    return str(language)


def detect_language(document: Document) -> str | None:
    """Return the language of a document's page text (see `recognise_language`).

    Args:
        document: A loaded document; scanned pages count once OCR has read them.

    Returns:
        A code from `detect.RULE_LANGUAGES`, or `None`.
    """
    return recognise_language("\n".join(page.text for page in document.pages))


@cache
def _identifier() -> LanguageIdentifier:
    from py3langid.langid import MODEL_FILE, LanguageIdentifier

    return LanguageIdentifier.from_model_file(MODEL_FILE, norm_probs=True)
