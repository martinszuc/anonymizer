"""Rule-based and model-based entity detectors.

Which rules apply depends on the configured language: a rodné číslo is a Czech
and Slovak concept, a NANP telephone number a North American one. Finders that
validate something locale-independent (email syntax, IBAN mod-97, the Luhn
checksum, URLs) always run.
"""

from anonymizer.core.detect.bank_account import find_account_numbers, is_valid_account_number
from anonymizer.core.detect.base import (
    OVERLAP_PRIORITY,
    Detector,
    Finder,
    Match,
    RuleDetector,
    resolve_overlaps,
)
from anonymizer.core.detect.birth_number import find_birth_numbers, is_valid_birth_number
from anonymizer.core.detect.card import find_card_numbers, is_valid_card_number, passes_luhn
from anonymizer.core.detect.company_id import find_company_ids, is_valid_company_id
from anonymizer.core.detect.contact import (
    find_czech_phone_numbers,
    find_emails,
    find_nanp_phone_numbers,
)
from anonymizer.core.detect.document import detect_document, detect_surface
from anonymizer.core.detect.iban import find_ibans, is_valid_iban, normalize_iban
from anonymizer.core.detect.propagate import propagate_occurrences
from anonymizer.core.detect.url import find_urls

LANGUAGE_INDEPENDENT_FINDERS: tuple[Finder, ...] = (
    find_emails,
    find_ibans,
    find_card_numbers,
    find_urls,
)
"""Finders whose evidence does not depend on the document's language."""

_CZECH_SLOVAK_FINDERS: tuple[Finder, ...] = (
    find_birth_numbers,
    find_account_numbers,
    find_company_ids,
    find_czech_phone_numbers,
)

_FINDERS_BY_LANGUAGE: dict[str, tuple[Finder, ...]] = {
    "cs": _CZECH_SLOVAK_FINDERS,
    "sk": _CZECH_SLOVAK_FINDERS,
    "en": (find_nanp_phone_numbers,),
}

STRUCTURED_FINDERS: tuple[Finder, ...] = (
    *LANGUAGE_INDEPENDENT_FINDERS,
    *_CZECH_SLOVAK_FINDERS,
    find_nanp_phone_numbers,
)
"""Every rule-based finder, regardless of language."""


def _primary_subtag(language: str) -> str:
    """Reduce a BCP 47 tag to its primary language subtag."""
    return language.strip().lower().split("-")[0]


def finders_for(language: str | None) -> tuple[Finder, ...]:
    """Return the finders that apply to a language.

    An unknown or unset language yields every finder: detection is recall-first,
    and running a locale's rules on the wrong locale costs precision, which
    review can repair, rather than recall, which it cannot.

    Args:
        language: BCP 47 tag such as `"cs"` or `"en-US"`, or `None`.

    Returns:
        The applicable finders, language-independent ones first.
    """
    if language is None:
        return STRUCTURED_FINDERS
    specific = _FINDERS_BY_LANGUAGE.get(_primary_subtag(language))
    if specific is None:
        return STRUCTURED_FINDERS
    return (*LANGUAGE_INDEPENDENT_FINDERS, *specific)


def detector_for(language: str | None) -> RuleDetector:
    """Build a rule detector for a language.

    Args:
        language: BCP 47 tag such as `"cs"` or `"en-US"`, or `None` for every rule.

    Returns:
        A detector over the applicable finders.
    """
    tag = _primary_subtag(language) if language else "all"
    return RuleDetector(finders_for(language), name=f"rules:{tag}")


def structured_detector() -> RuleDetector:
    """Build a detector running every rule-based finder.

    Returns:
        A detector for structured identifiers and contact details in any locale.
    """
    return RuleDetector(STRUCTURED_FINDERS, name="structured-rules")


__all__ = [
    "LANGUAGE_INDEPENDENT_FINDERS",
    "OVERLAP_PRIORITY",
    "STRUCTURED_FINDERS",
    "Detector",
    "Finder",
    "Match",
    "RuleDetector",
    "detect_document",
    "detect_surface",
    "detector_for",
    "find_account_numbers",
    "find_birth_numbers",
    "find_card_numbers",
    "find_company_ids",
    "find_czech_phone_numbers",
    "find_emails",
    "find_ibans",
    "find_nanp_phone_numbers",
    "find_urls",
    "finders_for",
    "is_valid_account_number",
    "is_valid_birth_number",
    "is_valid_card_number",
    "is_valid_company_id",
    "is_valid_iban",
    "normalize_iban",
    "passes_luhn",
    "propagate_occurrences",
    "resolve_overlaps",
    "structured_detector",
]
