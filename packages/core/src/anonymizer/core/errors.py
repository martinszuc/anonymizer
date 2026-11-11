"""Which exception messages may be shown to a person.

Messages of third-party exceptions (pymupdf, parsers, the operating system)
can quote document content or a file's name or path, and a file name can itself
be personal data. This code base's own errors are different: their text is
written here and names no document content, no file name and no path. They
derive from `Controlled`; every other exception is shown by its class name only.

Raise a controlled error only with a message built from fixed text, counts,
ids, page numbers and values the person typed or chose themselves, never from
text read out of a document, a file name or a path.
"""

from __future__ import annotations


class Controlled:
    """Marks an exception whose message this code base wrote and may be shown."""


class ControlledValueError(Controlled, ValueError):
    """A `ValueError` with a message that is safe to show."""


class ControlledKeyError(Controlled, KeyError):
    """A `KeyError` with a message that is safe to show (`error_text` unquotes it)."""


class ControlledFileNotFoundError(Controlled, FileNotFoundError):
    """A `FileNotFoundError` with a message that names no file and no folder."""


class MissingDependencyError(Controlled, ImportError):
    """An optional dependency is not installed; the message says how to install it."""


def error_text(error: BaseException, failure: str) -> str:
    """Return what may be shown of an exception.

    Args:
        error: The exception caught.
        failure: A fixed sentence saying what went wrong, shown with the
            exception's class name when its message may not be shown.

    Returns:
        The message of a controlled error; otherwise `failure` followed by the
        exception's class name in parentheses, never its message or arguments.
    """
    if isinstance(error, Controlled):
        # str() of a KeyError quotes its message.
        if isinstance(error, KeyError) and error.args:
            return str(error.args[0])
        return str(error)
    return f"{failure} ({type(error).__name__})"
