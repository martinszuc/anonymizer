"""Rule-based and model-based entity detectors.

Which rules apply depends on the configured language: a rodné číslo is a Czech
and Slovak concept, a NANP telephone number a North American one. Finders that
validate something locale-independent (email syntax, IBAN mod-97, the Luhn
checksum, URLs) always run.
"""

from anonymizer.core.detect.address import find_czech_slovak_addresses, find_us_addresses
from anonymizer.core.detect.bank_account import find_account_numbers, is_valid_account_number
from anonymizer.core.detect.base import (
    OVERLAP_PRIORITY,
    AgreementDetector,
    CombinedDetector,
    Detector,
    Finder,
    Match,
    RuleDetector,
    merge_entities,
)
from anonymizer.core.detect.birth_date import (
    find_czech_slovak_birth_dates,
    find_english_birth_dates,
)
from anonymizer.core.detect.birth_number import find_birth_numbers, is_valid_birth_number
from anonymizer.core.detect.card import find_card_numbers, is_valid_card_number, passes_luhn
from anonymizer.core.detect.company_id import find_company_ids, is_valid_company_id
from anonymizer.core.detect.contact import (
    find_czech_phone_numbers,
    find_emails,
    find_nanp_phone_numbers,
    find_ocr_emails,
)
from anonymizer.core.detect.document import detect_document, detect_surface
from anonymizer.core.detect.gliner import GlinerDetector, load_gliner_detector
from anonymizer.core.detect.iban import find_ibans, is_valid_iban, normalize_iban
from anonymizer.core.detect.models import (
    DEFAULT_NAME_MODEL,
    NAME_MODEL_ENGINES,
    load_name_model,
    missing_name_model_files,
    name_model,
    name_model_installed,
    name_models,
    system_model,
)
from anonymizer.core.detect.propagate import propagate_occurrences
from anonymizer.core.detect.roles import NamesOnly, cut_to_address, cut_to_name, role_words_for
from anonymizer.core.detect.titles import extend_with_titles
from anonymizer.core.detect.url import find_ocr_urls, find_urls

LANGUAGE_INDEPENDENT_FINDERS: tuple[Finder, ...] = (
    find_emails,
    find_ibans,
    find_card_numbers,
    find_urls,
)
"""Finders whose evidence does not depend on the document's language."""

OCR_FINDERS: tuple[Finder, ...] = (find_ocr_emails, find_ocr_urls)
"""Finders run in addition on pages read by OCR, in every language.

They accept the space OCR puts after a period inside an address, which in a
text layer would be a real space; the strict finders still run beside them and
`merge_entities` keeps the longer match.
"""

_CZECH_SLOVAK_FINDERS: tuple[Finder, ...] = (
    find_birth_numbers,
    find_czech_slovak_birth_dates,
    find_account_numbers,
    find_company_ids,
    find_czech_phone_numbers,
    find_czech_slovak_addresses,
)

_FINDERS_BY_LANGUAGE: dict[str, tuple[Finder, ...]] = {
    "cs": _CZECH_SLOVAK_FINDERS,
    "sk": _CZECH_SLOVAK_FINDERS,
    "en": (find_nanp_phone_numbers, find_english_birth_dates, find_us_addresses),
}

RULE_LANGUAGES: tuple[str, ...] = tuple(_FINDERS_BY_LANGUAGE)
"""Languages with rules of their own; any other runs every rule."""

STRUCTURED_FINDERS: tuple[Finder, ...] = (
    *LANGUAGE_INDEPENDENT_FINDERS,
    *_CZECH_SLOVAK_FINDERS,
    find_nanp_phone_numbers,
    find_english_birth_dates,
    find_us_addresses,
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
    return RuleDetector(finders_for(language), name=f"rules:{tag}", ocr_finders=OCR_FINDERS)


__all__ = [
    "DEFAULT_NAME_MODEL",
    "LANGUAGE_INDEPENDENT_FINDERS",
    "NAME_MODEL_ENGINES",
    "OCR_FINDERS",
    "OVERLAP_PRIORITY",
    "RULE_LANGUAGES",
    "STRUCTURED_FINDERS",
    "AgreementDetector",
    "CombinedDetector",
    "Detector",
    "Finder",
    "GlinerDetector",
    "Match",
    "NamesOnly",
    "RuleDetector",
    "cut_to_address",
    "cut_to_name",
    "detect_document",
    "detect_surface",
    "detector_for",
    "extend_with_titles",
    "find_account_numbers",
    "find_birth_numbers",
    "find_card_numbers",
    "find_company_ids",
    "find_czech_phone_numbers",
    "find_czech_slovak_addresses",
    "find_czech_slovak_birth_dates",
    "find_emails",
    "find_english_birth_dates",
    "find_ibans",
    "find_nanp_phone_numbers",
    "find_ocr_emails",
    "find_ocr_urls",
    "find_urls",
    "find_us_addresses",
    "finders_for",
    "is_valid_account_number",
    "is_valid_birth_number",
    "is_valid_card_number",
    "is_valid_company_id",
    "is_valid_iban",
    "load_gliner_detector",
    "load_name_model",
    "merge_entities",
    "missing_name_model_files",
    "name_model",
    "name_model_installed",
    "name_models",
    "normalize_iban",
    "passes_luhn",
    "propagate_occurrences",
    "role_words_for",
    "system_model",
]
