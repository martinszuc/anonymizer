"""Web address detection.

A profile URL (`linkedin.com/in/<name>`, `github.com/<handle>`) identifies a
person, but any site can host a profile and a list of profile sites goes stale.
Every URL is therefore reported, and review rejects the harmless ones.

Three shapes are recognised: an address with a scheme, one starting with `www.`,
and a host followed by a path, the form CVs print profiles in. A bare domain
without a path (`jannovak.cz`) is not: it is indistinguishable from technology
names such as `Node.js` or `ASP.NET`. `mailto:` and `tel:` targets are left to
the email and phone finders.
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
    for found in _URL_PATTERN.finditer(text):
        url = _trim(found.group(0))
        if not _URL_PATTERN.fullmatch(url):
            continue
        yield Match(
            type=EntityType.URL,
            start=found.start(),
            end=found.start() + len(url),
            text=url,
        )
