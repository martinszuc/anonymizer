"""Benchmark documents written as data, with personal items marked inline.

A document file (`documents/*.toml`) holds the visible lines and the strings
written outside them: link targets, metadata, bookmarks, form fields,
annotations, attachments and XMP properties. Every personal item is written where it occurs as
`[[type:text]]`, so its text, type and carrier come from the markup and are
never typed twice. `{{filler:N}}` expands to N words of neutral text, for
documents that must be long (the model reads at most 384 tokens at once).
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from itertools import cycle, islice
from pathlib import Path
from typing import Any

from anonymizer.core.types import EntityType

DOCUMENTS = Path(__file__).parent / "documents"

_ITEM = re.compile(r"\[\[([a-z_]+):([^\[\]]+)\]\]")
_FILLER = re.compile(r"\{\{filler:(\d+)\}\}")

# Neutral text for {{filler:N}}: no names, numbers or places.
_FILLER_TEXT = (
    "Tento odstavec popisuje obecné podmínky spolupráce a nemá žádný vztah k "
    "jednotlivým osobám. Smluvní strany se dohodly na postupu, který bude "
    "průběžně vyhodnocován a upravován podle potřeby. Dokument slouží jako "
    "podklad pro další jednání a neobsahuje údaje o konkrétních lidech."
)


@dataclass(frozen=True)
class GoldItem:
    """A personal item planted in a document.

    Attributes:
        type: What the item is.
        text: The item as written.
        carrier: `page`, or the surface kind holding it (`link`, `metadata`, ...).
    """

    type: EntityType
    text: str
    carrier: str


@dataclass(frozen=True)
class DocumentSpec:
    """One benchmark document.

    Attributes:
        name: File stem; also names the generated PDF.
        language: BCP 47 tag the pipeline is run with.
        kind: Document type (cv, invoice, letter, ...).
        lines: Visible text, one entry per paragraph, markup removed.
        links: Link targets with their visible anchor text.
        metadata: Information dictionary entries.
        bookmarks: Outline titles.
        fields: Text form fields as (label printed before the field, value).
        annotations: Sticky notes as (author, note text).
        attachments: Files attached to the document as (file name, description).
        xmp: Dublin Core properties written to the XMP packet.
        gold: Every planted item.
        decoys: Strings that look personal but are not (must stay readable).
    """

    name: str
    language: str
    kind: str
    lines: tuple[str, ...]
    links: tuple[tuple[str, str], ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    bookmarks: tuple[str, ...] = ()
    fields: tuple[tuple[str, str], ...] = ()
    annotations: tuple[tuple[str, str], ...] = ()
    attachments: tuple[tuple[str, str], ...] = ()
    xmp: dict[str, str] = field(default_factory=dict)
    gold: tuple[GoldItem, ...] = ()
    decoys: tuple[str, ...] = ()


def load_documents(directory: Path = DOCUMENTS) -> list[DocumentSpec]:
    """Load every document file in a directory, sorted by name."""
    return [load_document_spec(path) for path in sorted(directory.glob("*.toml"))]


def load_document_spec(path: Path) -> DocumentSpec:
    """Load one document file.

    Raises:
        ValueError: If the file is malformed or names an unknown entity type.
    """
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    gold: list[GoldItem] = []

    def plain(text: str, carrier: str) -> str:
        return _strip_markup(_expand_filler(text), carrier, gold)

    try:
        lines = tuple(plain(line, "page") for line in raw["lines"])
        links = tuple(
            (plain(link["anchor"], "page"), plain(link["target"], "link"))
            for link in raw.get("links", [])
        )
        metadata = {key: plain(value, "metadata") for key, value in raw.get("metadata", {}).items()}
        bookmarks = tuple(plain(title, "bookmark") for title in raw.get("bookmarks", []))
        # A field's value is drawn on the page as well as stored in the field:
        # two carriers, two items.
        fields = tuple(
            (plain(entry["label"], "page"), _field_value(entry["value"], gold))
            for entry in raw.get("fields", [])
        )
        annotations = tuple(
            (plain(note["author"], "annotation"), plain(note["text"], "annotation"))
            for note in raw.get("annotations", [])
        )
        attachments = tuple(
            (
                plain(entry["filename"], "embedded_file"),
                plain(entry["description"], "embedded_file"),
            )
            for entry in raw.get("attachments", [])
        )
        xmp = {key: plain(value, "xmp") for key, value in raw.get("xmp", {}).items()}
        return DocumentSpec(
            name=path.stem,
            language=raw["language"],
            kind=raw["kind"],
            lines=lines,
            links=links,
            metadata=metadata,
            bookmarks=bookmarks,
            fields=fields,
            annotations=annotations,
            attachments=attachments,
            xmp=xmp,
            gold=tuple(gold),
            decoys=tuple(raw.get("decoys", [])),
        )
    except (KeyError, TypeError) as error:
        msg = f"{path.name}: malformed document ({error})"
        raise ValueError(msg) from error


def _field_value(text: str, gold: list[GoldItem]) -> str:
    value = _strip_markup(text, "page", gold)
    _strip_markup(text, "form_field", gold)
    return value


def _strip_markup(text: str, carrier: str, gold: list[GoldItem]) -> str:
    def replace(match: re.Match[str]) -> str:
        kind, value = match.group(1), match.group(2)
        try:
            entity_type = EntityType(kind)
        except ValueError:
            msg = f"unknown entity type {kind!r} in {match.group(0)!r}"
            raise ValueError(msg) from None
        gold.append(GoldItem(entity_type, value, carrier))
        return value

    stripped = _ITEM.sub(replace, text)
    if "[[" in stripped or "]]" in stripped:
        msg = f"unbalanced item markup in {text!r}"
        raise ValueError(msg)
    return stripped


def _expand_filler(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return " ".join(islice(cycle(_FILLER_TEXT.split()), int(match.group(1))))

    return _FILLER.sub(replace, text)


def visible_text(spec: DocumentSpec) -> list[str]:
    """Return every string drawn on the pages, in the order it is written."""
    return [
        *spec.lines,
        *(anchor for anchor, _ in spec.links),
        *(text for pair in spec.fields for text in pair),
    ]


def spec_summary(spec: DocumentSpec) -> dict[str, Any]:
    """Return counts describing a document, for reports."""
    return {
        "name": spec.name,
        "language": spec.language,
        "kind": spec.kind,
        "words": sum(len(line.split()) for line in visible_text(spec)),
        "gold_items": len(spec.gold),
        "hidden_items": sum(item.carrier != "page" for item in spec.gold),
    }
