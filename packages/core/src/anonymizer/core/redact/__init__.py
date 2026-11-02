"""Redaction of reviewed entities and the leakage check on its output.

A PDF is blacked out (`redact_pdf`); its text can also be exported with each
value replaced by a label (`redact_text`), which keeps nothing of the value's
width. Pseudonyms are not implemented.
"""

from anonymizer.core.redact.export import export_redacted, export_redacted_text
from anonymizer.core.redact.leakage import (
    Leak,
    LeakKind,
    LeakLayer,
    find_leaks,
    find_text_leaks,
)
from anonymizer.core.redact.pdf import redact_pdf
from anonymizer.core.redact.surfaces import clear_surfaces
from anonymizer.core.redact.text import redact_text

__all__ = [
    "Leak",
    "LeakKind",
    "LeakLayer",
    "clear_surfaces",
    "export_redacted",
    "export_redacted_text",
    "find_leaks",
    "find_text_leaks",
    "redact_pdf",
    "redact_text",
]
