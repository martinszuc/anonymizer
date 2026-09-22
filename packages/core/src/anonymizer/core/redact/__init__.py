"""Redaction of reviewed entities and the leakage check on its output.

Blackbox is the only strategy so far; label and pseudonym modes will sit beside
it behind a shared interface once a second one exists.
"""

from anonymizer.core.redact.leakage import Leak, LeakLayer, find_leaks
from anonymizer.core.redact.pdf import redact_pdf
from anonymizer.core.redact.surfaces import clear_surfaces

__all__ = [
    "Leak",
    "LeakLayer",
    "clear_surfaces",
    "find_leaks",
    "redact_pdf",
]
