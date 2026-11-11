"""Tests for which exception messages may be shown."""

import pytest
from anonymizer.core.errors import (
    ControlledFileNotFoundError,
    ControlledKeyError,
    ControlledValueError,
    MissingDependencyError,
    error_text,
)

# Built in two parts, so that no source line a failure shows contains it whole.
CANARY = "CANARY-" + "private-text"


@pytest.mark.parametrize(
    "error",
    [
        ValueError(CANARY),
        KeyError(CANARY),
        OSError(2, CANARY, f"/home/{CANARY}/cv.pdf"),
        FileNotFoundError(f"no such file: {CANARY}.pdf"),
        ImportError(CANARY),
        RuntimeError(CANARY, CANARY),
    ],
)
def test_a_foreign_exception_shows_its_class_and_nothing_else(error: Exception):
    shown = error_text(error, "it failed")
    assert shown == f"it failed ({type(error).__name__})"
    assert CANARY not in shown


def test_a_subclass_of_a_builtin_error_is_not_trusted():
    class ForeignError(ValueError):
        pass

    assert CANARY not in error_text(ForeignError(CANARY), "it failed")


@pytest.mark.parametrize(
    ("error", "text"),
    [
        (ControlledValueError("not a session file"), "not a session file"),
        (ControlledKeyError("no page with index 5"), "no page with index 5"),
        (ControlledFileNotFoundError("no such file"), "no such file"),
        (MissingDependencyError("install the ner group"), "install the ner group"),
    ],
)
def test_a_controlled_error_keeps_its_message(error: Exception, text: str):
    assert error_text(error, "it failed") == text
