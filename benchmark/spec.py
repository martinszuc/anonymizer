"""Benchmark documents written as data, with personal items marked inline.

A document file (`documents/*.toml`) holds the visible lines and the strings
written outside them: link targets, metadata, bookmarks, form fields,
annotations, attachments and XMP properties. Every personal item is written
where it occurs as `[[type:text]]`, so its text, type and carrier come from the
markup and are never typed twice. `{{filler:N}}` expands to N words of neutral text, for
documents that must be long (the model reads at most 384 tokens at once).

Layout is optional and used by the phone-photo documents only: a letterhead
and footer, and blocks placed after a number of lines (a table, labelled
boxes, a blank line filled in by hand, a stamp, a signature). A document
without them renders as it always has. Gold items are collected in reading
order (letterhead, lines and blocks as placed, footer), which is the order the
scorer locates them in. Text written by hand is not on the printed page: its
items have the carrier `handwritten`.
"""

from __future__ import annotations

import hashlib
import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import cycle, islice
from pathlib import Path
from typing import Any

from anonymizer.core.types import EntityType

DOCUMENTS = Path(__file__).parent / "documents"

_ITEM = re.compile(r"\[\[([a-z_]+):([^\[\]]+)\]\]")
_FILLER = re.compile(r"\{\{filler:(\d+)\}\}")

_Plain = Callable[[str, str], str]

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
class Letterhead:
    """The organisation printed at the top of the first page.

    Attributes:
        organisation: Its name.
        address: Lines of its address block.
        logo: Letters drawn in the logo box.
    """

    organisation: str
    address: tuple[str, ...]
    logo: str


@dataclass(frozen=True)
class Table:
    """A ruled table; every cell is one string, wrapped inside its column.

    Attributes:
        after: Lines printed before it.
        columns: Header cells.
        rows: Body cells, as many per row as there are columns.
        widths: Share of the text width per column (equal when empty).
    """

    after: int
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    widths: tuple[float, ...] = ()


@dataclass(frozen=True)
class Boxes:
    """Form fields printed as boxes: a small label above each value.

    Attributes:
        after: Lines printed before them.
        fields: (label, value) pairs, filled row by row.
        per_row: Boxes in a row.
    """

    after: int
    fields: tuple[tuple[str, str], ...]
    per_row: int = 2


@dataclass(frozen=True)
class Handwritten:
    """A printed label and a blank line; `text` is written there by hand.

    Attributes:
        after: Lines printed before it.
        label: Printed before the blank line.
        text: What is written on the line (never printed).
    """

    after: int
    label: str
    text: str


@dataclass(frozen=True)
class Stamp:
    """A round stamp drawn as a picture over the text above its place.

    Attributes:
        after: Lines printed before it.
        lines: Text inside the ring.
    """

    after: int
    lines: tuple[str, ...]


@dataclass(frozen=True)
class Signature:
    """A signature line with a scribble drawn in vector strokes.

    Attributes:
        after: Lines printed before it.
        label: Printed before the line.
        seed: Seeds the shape of the scribble.
    """

    after: int
    label: str
    seed: str


Block = Table | Boxes | Handwritten | Stamp | Signature


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
        letterhead: Organisation at the top of the first page.
        footer: Text at the foot of every page.
        blocks: Layout blocks, in the order they are placed.
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
    letterhead: Letterhead | None = None
    footer: str = ""
    blocks: tuple[Block, ...] = ()

    @property
    def laid_out(self) -> bool:
        """Whether any layout field is set."""
        return self.letterhead is not None or bool(self.footer or self.blocks)


def load_documents(directory: Path = DOCUMENTS) -> list[DocumentSpec]:
    """Load every document file in a directory, sorted by name."""
    return [load_document_spec(path) for path in sorted(directory.glob("*.toml"))]


def document_set(directory: Path = DOCUMENTS) -> dict[str, Any]:
    """Identify the set of document files in a directory.

    Runs are comparable only on the same set, and a set can change without
    changing its size. The fingerprint is a SHA-256 over every file's name and
    contents, in name order; line endings are normalised, so a Windows checkout
    gives the same value.

    Returns:
        `fingerprint` (hex digest) and `documents` (the number of files).
    """
    paths = sorted(directory.glob("*.toml"))
    digest = hashlib.sha256()
    for path in paths:
        content = path.read_bytes().replace(b"\r\n", b"\n")
        digest.update(f"{path.name}\0{len(content)}\0".encode())
        digest.update(content)
    return {"fingerprint": digest.hexdigest(), "documents": len(paths)}


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
        letterhead = _letterhead(raw.get("letterhead"), plain)
        raw_lines = raw["lines"]
        raw_blocks = raw.get("blocks", [])
        lines_list: list[str] = []
        blocks_list: list[Block] = []
        # Lines and blocks are read in the order they are placed, so the gold
        # items stay in reading order.
        pending = sorted(range(len(raw_blocks)), key=lambda index: raw_blocks[index]["after"])
        for position in range(len(raw_lines) + 1):
            while pending and raw_blocks[pending[0]]["after"] == position:
                blocks_list.append(_block(raw_blocks[pending.pop(0)], plain))
            if position < len(raw_lines):
                lines_list.append(plain(raw_lines[position], "page"))
        if pending:
            msg = f"a block is placed after line {raw_blocks[pending[0]]['after']}, past the end"
            raise ValueError(msg)
        lines = tuple(lines_list)
        footer = plain(raw.get("footer", ""), "page")
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
            letterhead=letterhead,
            footer=footer,
            blocks=tuple(blocks_list),
        )
    except (KeyError, TypeError) as error:
        msg = f"{path.name}: malformed document ({error})"
        raise ValueError(msg) from error


def _letterhead(raw: dict[str, Any] | None, plain: _Plain) -> Letterhead | None:
    if raw is None:
        return None
    return Letterhead(
        organisation=plain(raw["organisation"], "page"),
        address=tuple(plain(line, "page") for line in raw["address"]),
        logo=raw["logo"],
    )


def _block(raw: dict[str, Any], plain: _Plain) -> Block:
    """Read one layout block; its gold items are collected in reading order.

    Raises:
        ValueError: For an unknown block type or a table row of the wrong length.
    """
    after = raw["after"]
    kind = raw["type"]
    if kind == "table":
        columns = tuple(plain(cell, "page") for cell in raw["columns"])
        rows = tuple(tuple(plain(cell, "page") for cell in row) for row in raw["rows"])
        widths = tuple(float(width) for width in raw.get("widths", []))
        if any(len(row) != len(columns) for row in rows) or (
            widths and len(widths) != len(columns)
        ):
            msg = "a table row or its widths do not match its columns"
            raise ValueError(msg)
        return Table(after, columns, rows, widths)
    if kind == "boxes":
        fields = tuple(
            (plain(label, "page"), plain(value, "page")) for label, value in raw["fields"]
        )
        return Boxes(after, fields, raw.get("per_row", 2))
    if kind == "handwritten":
        return Handwritten(after, plain(raw["label"], "page"), plain(raw["text"], "handwritten"))
    if kind == "stamp":
        # A stamp is a picture: its text is not on the text layer.
        return Stamp(after, tuple(raw["lines"]))
    if kind == "signature":
        return Signature(after, plain(raw["label"], "page"), raw["seed"])
    msg = f"unknown block type {kind!r}"
    raise ValueError(msg)


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
    """Return every string drawn on the pages, in the order it is written.

    Text written by hand is left out: it is not printed.
    """
    head = [spec.letterhead.organisation, *spec.letterhead.address] if spec.letterhead else []
    placed: list[str] = []
    blocks = list(spec.blocks)
    for position in range(len(spec.lines) + 1):
        while blocks and blocks[0].after == position:
            placed += _block_text(blocks.pop(0))
        if position < len(spec.lines):
            placed.append(spec.lines[position])
    return [
        *head,
        *placed,
        *([spec.footer] if spec.footer else []),
        *(anchor for anchor, _ in spec.links),
        *(text for pair in spec.fields for text in pair),
    ]


def _block_text(block: Block) -> list[str]:
    if isinstance(block, Table):
        return [*block.columns, *(cell for row in block.rows for cell in row)]
    if isinstance(block, Boxes):
        return [text for pair in block.fields for text in pair]
    if isinstance(block, Handwritten | Signature):
        return [block.label]
    return []


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
