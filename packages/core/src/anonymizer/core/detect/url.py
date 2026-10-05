"""Web address detection.

A profile URL (`linkedin.com/in/<name>`, `github.com/<handle>`) identifies a
person, but any site can host a profile and a list of profile sites goes stale.
Every URL is therefore reported, and review rejects the harmless ones.

Three shapes are recognised: an address with a scheme, one starting with `www.`,
and a host followed by a path, the form CVs print profiles in. A bare domain
without a path (`jannovak.cz`) is not: it is indistinguishable from technology
names such as `Node.js` or `ASP.NET`. `mailto:` and `tel:` targets are left to
the email and phone finders. `find_ocr_urls` additionally accepts the space an
OCR reader puts after a period inside an address; it runs on pages read by OCR
only.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from anonymizer.core.detect.base import Match
from anonymizer.core.types import EntityType

# A URL is one token without whitespace or quotes. The lookbehind keeps a match
# from starting inside a word, an email address or another URL's path.
_URL_PATTERN = re.compile(
    r"(?<![\w@.\-/])"
    r"(?:"
    r"(?:https?|ftp)://[^\s<>\"'`]+"
    r"|www\.[^\s<>\"'`]+"
    r"|(?:[a-z0-9\-]+\.)+[a-z]{2,}/[^\s<>\"'`]*"
    r")",
    re.IGNORECASE,
)

# The space PP-OCR puts after a period (`https://www. linkedin. com/in/...`), as
# in `contact._OCR_SPLIT`; the lookahead is case-sensitive inside an IGNORECASE pattern.
_OCR_SPLIT = r"(?<=\.) (?-i:(?=[a-z0-9]))"
_OCR_TOKEN = r"[^\s<>\"'`]+"
_OCR_URL_PATTERN = re.compile(
    r"(?<![\w@.\-/])"
    r"(?:"
    rf"(?:https?|ftp)://{_OCR_TOKEN}(?:{_OCR_SPLIT}{_OCR_TOKEN})*"
    rf"|www\.(?:{_OCR_SPLIT})?{_OCR_TOKEN}(?:{_OCR_SPLIT}{_OCR_TOKEN})*"
    rf"|(?:[a-z0-9\-]+\.(?:{_OCR_SPLIT})?)+[a-z]{{2,}}/[^\s<>\"'`]*(?:{_OCR_SPLIT}{_OCR_TOKEN})*"
    r")",
    re.IGNORECASE,
)

# Punctuation that ends the sentence around a URL more often than the URL itself.
_TRAILING_PUNCTUATION = ".,;:!?"
_CLOSING_BRACKETS = {")": "(", "]": "[", "}": "{"}


def _trim(url: str) -> str:
    """Drop trailing punctuation and closing brackets the URL did not open."""
    while url:
        last = url[-1]
        opener = _CLOSING_BRACKETS.get(last)
        unbalanced = opener is not None and url.count(last) > url.count(opener)
        if last not in _TRAILING_PUNCTUATION and not unbalanced:
            break
        url = url[:-1]
    return url


def find_urls(text: str) -> Iterator[Match]:
    """Yield the web addresses in a text.

    Args:
        text: Text to scan.

    Yields:
        One match per address, in order of appearance, without the punctuation
        of the surrounding sentence.
    """
    yield from _trimmed_matches(_URL_PATTERN, text)


def find_ocr_urls(text: str) -> Iterator[Match]:
    """Yield the web addresses in OCR output, joined across a space after a period.

    Args:
        text: Text read by OCR.

    Yields:
        One match per address, in order of appearance, spaces included and
        without the punctuation of the surrounding sentence.
    """
    yield from _trimmed_matches(_OCR_URL_PATTERN, text)


def _trimmed_matches(pattern: re.Pattern[str], text: str) -> Iterator[Match]:
    """Yield a pattern's matches without the punctuation of the surrounding sentence."""
    for found in pattern.finditer(text):
        url = _trim(found.group(0))
        if not pattern.fullmatch(url):
            continue
        yield Match(
            type=EntityType.URL,
            start=found.start(),
            end=found.start() + len(url),
            text=url,
        )
