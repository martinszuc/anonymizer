"""Logging for every client: levels, format, and the rules for what a log may hold.

The core only ever calls `logging.getLogger(__name__)`; it never configures
handlers, so a program embedding it decides where records go. The command line
and the review window call `configure_logging` once at startup.

Levels mean the same everywhere:

- ``DEBUG``: every step started and finished with counts and timing, and every
  detection: which word, found by which rule or model.
- ``INFO``: milestones a user wants to see (a document opened, a model loaded,
  a copy written, a download started).
- ``WARNING``: something degraded but work went on (a scan OCR did not read).
- ``ERROR``: an operation failed.

What a log may hold is a privacy rule, not a style choice. INFO and above carry
counts, entity types, page numbers, durations and the first characters of a
document's fingerprint, never document text, file names or paths. DEBUG also
carries the words detection found, because following a detection back to the
rule that made it needs them; `configure_logging` says so when DEBUG is on, and
a debug log must not be shared. Exception messages are never written at any
level (`SafeFormatter`): pymupdf and `ValueError` messages can quote content.
Nothing is written to a file unless the caller names one.
"""

from __future__ import annotations

import logging
import os
import re
import time
import traceback
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType
from typing import TextIO

ROOT_LOGGER = "anonymizer"
"""Parent of every logger in the project; handlers are attached here."""

LEVEL_VARIABLE = "ANONYMIZER_LOG_LEVEL"
"""Environment variable naming the level when no argument does."""

LEVEL_NAMES: tuple[str, ...] = ("debug", "info", "warning", "error")
"""The level names a command line offers, from most to least verbose."""

DEFAULT_LEVEL = logging.WARNING

MAX_TEXT = 120
"""Longest document text written to a DEBUG record; the rest is cut."""

_FINGERPRINT_CHARS = 8
_PLAIN = re.compile(r"[\w.:/+@\[\](),-]+")
_HANDLER_MARK = "_anonymizer_handler"

logging.getLogger(ROOT_LOGGER).addHandler(logging.NullHandler())

_ExcInfo = tuple[type[BaseException], BaseException, TracebackType | None]


class SafeFormatter(logging.Formatter):
    """One readable line per record, with exceptions shown without their messages.

    A traceback keeps its frames and the exception's type, so the failing code
    is visible; the message is dropped because it may quote document content.
    """

    def __init__(self, *, with_thread: bool) -> None:
        """Initialize the formatter.

        Args:
            with_thread: Add the thread's name, which separates the window's
                worker threads and downloads in a debug log.
        """
        thread = " %(threadName)s" if with_thread else ""
        super().__init__(
            f"%(asctime)s.%(msecs)03d %(levelname)-7s{thread} [%(short_name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        """Format a record, naming its logger without the shared prefix."""
        record.short_name = record.name.removeprefix(f"{ROOT_LOGGER}.")
        return super().format(record)

    def formatException(self, ei: _ExcInfo | tuple[None, None, None]) -> str:  # noqa: N802
        """Render the frames and the exception type, never its message."""
        kind, _message, trace = ei
        if kind is None:
            return ""
        frames = "".join(traceback.format_tb(trace)).rstrip()
        return f"Traceback (most recent call last):\n{frames}\n{kind.__name__}: (message withheld)"


def resolve_level(name: str | None = None, *, debug: bool = False) -> int:
    """Pick the logging level from a flag, the environment and the default.

    Args:
        name: The level a command-line option named, if any.
        debug: Whether the `--debug` flag was given; it means ``debug`` unless
            a level was named.

    Returns:
        A `logging` level: `name` if given, else ``debug`` for the flag, else
        `ANONYMIZER_LOG_LEVEL`, else warnings and errors only.

    Raises:
        ValueError: If a name is not one of `LEVEL_NAMES`.
    """
    chosen = (name or ("debug" if debug else os.environ.get(LEVEL_VARIABLE, ""))).strip().lower()
    if not chosen:
        return DEFAULT_LEVEL
    if chosen not in LEVEL_NAMES:
        msg = f"unknown log level {chosen!r}; use one of {', '.join(LEVEL_NAMES)}"
        raise ValueError(msg)
    return logging.getLevelNamesMapping()[chosen.upper()]


def configure_logging(
    level: int = DEFAULT_LEVEL,
    *,
    file: Path | None = None,
    stream: TextIO | None = None,
) -> None:
    """Send the project's log records to stderr and, if asked, to a file.

    Calling it again replaces the handlers of the previous call. Only the
    project's own loggers are touched, so libraries keep their usual defaults.

    Args:
        level: The least severe record to keep.
        file: Also append to this file (UTF-8). No file is created otherwise.
        stream: Where the console records go; stderr by default.
    """
    reset_logging()
    logger = logging.getLogger(ROOT_LOGGER)
    handlers: list[logging.Handler] = [logging.StreamHandler(stream)]
    if file is not None:
        handlers.append(logging.FileHandler(file, encoding="utf-8"))
    formatter = SafeFormatter(with_thread=level <= logging.DEBUG)
    for handler in handlers:
        setattr(handler, _HANDLER_MARK, True)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    logging.captureWarnings(True)
    if level <= logging.DEBUG:
        logger.warning(
            "debug logging is on: this log contains text from the documents being processed"
        )


def reset_logging() -> None:
    """Remove the handlers `configure_logging` added and close its file, if any.

    Leaves the project's loggers as the core ships them: silent, so a program
    embedding the library sees nothing unless it configures logging itself.
    """
    logger = logging.getLogger(ROOT_LOGGER)
    for handler in [handler for handler in logger.handlers if hasattr(handler, _HANDLER_MARK)]:
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(logging.NOTSET)
    logger.propagate = True


def fields(**values: object) -> str:
    """Render `key=value` pairs for a record, quoting text that is not a plain token.

    Args:
        **values: The pairs, in order. Text is cut at `MAX_TEXT` characters
            and quoted when it holds spaces, quotes or line breaks, so one
            record stays one line.

    Returns:
        The pairs separated by spaces, with a leading space; empty if none.
    """
    if not values:
        return ""
    return "".join(f" {key}={_render(value)}" for key, value in values.items())


def _render(value: object) -> str:
    text = str(value)
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT] + "…"
    if _PLAIN.fullmatch(text):
        return text
    # Line breaks and control characters are escaped, so text cannot start a new record.
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + "".join(c if c.isprintable() else _escape(c) for c in escaped) + '"'


def _escape(character: str) -> str:
    return character.encode("unicode_escape").decode("ascii")


@contextmanager
def step(
    logger: logging.Logger,
    name: str,
    *,
    done_level: int = logging.DEBUG,
    **context: object,
) -> Iterator[dict[str, object]]:
    """Log a step's start and its end with the time it took.

    The start and a failure are DEBUG records. The end is one at `done_level`,
    carrying the context and whatever the block put in the yielded dict, so a
    result known only at the end (a count) is reported with the step.

    Args:
        logger: The module's logger.
        name: What the step does, e.g. ``detect``.
        done_level: Level of the record written when the step ends.
        **context: Fields known when the step starts.

    Yields:
        A dict the block fills with results to report when the step ends.
    """
    outcome: dict[str, object] = {}
    started = time.perf_counter()
    logger.debug("%s: start%s", name, fields(**context))
    try:
        yield outcome
    except BaseException as error:
        logger.debug(
            "%s: failed%s",
            name,
            fields(**context, elapsed=_seconds(started), error=type(error).__name__),
        )
        raise
    logger.log(
        done_level,
        "%s: done%s",
        name,
        fields(**context, **outcome, elapsed=_seconds(started)),
    )


def _seconds(started: float) -> str:
    return f"{time.perf_counter() - started:.2f}s"


def short_fingerprint(fingerprint: object) -> str:
    """Return the first characters of a document's fingerprint, enough to tell documents apart.

    Args:
        fingerprint: The SHA-256 hex digest; anything else (a damaged session
            file may hold any JSON) gives ``-``.

    Returns:
        A short prefix, or ``-`` when there is none.
    """
    return fingerprint[:_FINGERPRINT_CHARS] if isinstance(fingerprint, str) and fingerprint else "-"


def counts(items: Mapping[str, int]) -> str:
    """Render counts as ``a:2,b:1``, most frequent first, for a record's field."""
    ordered = sorted(items.items(), key=lambda pair: (-pair[1], pair[0]))
    return ",".join(f"{key}:{count}" for key, count in ordered) or "-"
