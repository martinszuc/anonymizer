"""Rule-based and model-based entity detectors."""

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
from anonymizer.core.detect.contact import find_emails, find_phone_numbers
from anonymizer.core.detect.iban import find_ibans, is_valid_iban, normalize_iban

STRUCTURED_FINDERS: tuple[Finder, ...] = (
    find_birth_numbers,
    find_ibans,
    find_account_numbers,
    find_emails,
    find_phone_numbers,
)
"""Every rule-based finder, ordered from most to least specific."""


def structured_detector() -> RuleDetector:
    """Build a detector running all rule-based finders.

    Returns:
        A detector for structured identifiers and contact details.
    """
    return RuleDetector(STRUCTURED_FINDERS, name="structured-rules")


__all__ = [
    "OVERLAP_PRIORITY",
    "STRUCTURED_FINDERS",
    "Detector",
    "Finder",
    "Match",
    "RuleDetector",
    "find_account_numbers",
    "find_birth_numbers",
    "find_emails",
    "find_ibans",
    "find_phone_numbers",
    "is_valid_account_number",
    "is_valid_birth_number",
    "is_valid_iban",
    "normalize_iban",
    "resolve_overlaps",
    "structured_detector",
]
