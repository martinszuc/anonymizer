"""Strings a PDF carries outside its page text.

Every non-blank string becomes one `Surface`. `Surface.ref` locates it so that
redaction of the same file can find the object again:

=============  ==============================================================
Kind           `ref`
=============  ==============================================================
METADATA       key of the document information dictionary, e.g. `Title`
XMP            object number of the document's XMP stream
LINK           `<object number>/uri` or `<object number>/file`
ANNOTATION     `<object number>/content`, `/title` (the author) or `/subject`
FORM_FIELD     `<object number>/value` of the widget
BOOKMARK       `<position in the outline>/title`, `/uri` or `/file`
EMBEDDED_FILE  `<position in the attachment tree>/<field>` for the document,
               `<object number>/<field>` for an attachment annotation on a page,
               `<object number>/af<n>/<field>` for the n-th associated file
               (`/AF`) of any dictionary in that object
STRUCTURE      `<object number>/Alt`, `/ActualText`, `/T` or `/E` of a
               structure element
=============  ==============================================================

Attachment *contents* are never read, only their names and descriptions. An
attached file can hold anything, so redaction has to drop attachments whatever
this module or a detector finds in their labels.

The labels are read from the file specifications themselves, found by walking
the document's attachment name tree: PyMuPDF's `embfile_info` and
`Annot.file_info` return a name with diacritics as UTF-8 bytes taken for
Latin-1, and `embfile_count` reads only the tree's root node, so it reports no
attachment in a tree a producer split over child nodes (`Kids`).

Associated files (`/AF`, PDF 2.0 and PDF/A-3; Factur-X and ZUGFeRD invoices
keep their XML there) are listed from every carrier, not only the catalog and
pages, and have no page index: they are not drawn. A file specification the
attachment tree or an attachment annotation already lists is not repeated.
File specifications in other carriers (launch actions, multimedia annotations)
are not listed; redaction empties every specification that embeds a file.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import cast
from urllib.parse import unquote

import pymupdf
from anonymizer.core.ingest.normalize import normalize_text, rect_to_bbox, unrotated_rect_to_bbox
from anonymizer.core.ingest.objects import dictionaries_with_key
from anonymizer.core.types import BBox, Surface, SurfaceKind
from pymupdf import mupdf

# Information dictionary values that MuPDF decodes as text: inline strings and
# references, since producers such as react-pdf store every value as a separate
# string object.
_STRING_TYPES = frozenset({"string", "xref"})
# Other value types that can still carry text, taken as PDF source.
_STRUCTURED_TYPES = frozenset({"name", "array", "dict"})

_TRAILER = -1

# Keys of a structure element that hold text for assistive technology: an
# alternate description, replacement text, a title and an expansion.
_STRUCTURE_TEXT_KEYS = ("Alt", "ActualText", "T", "E")

# PDF annotation subtype of an attached file. PyMuPDF's numeric constant for it
# is created at runtime and invisible to the type checker.
_FILE_ATTACHMENT_SUBTYPE = "FileAttachment"

# Root of the name tree that lists the files attached to the document.
_EMBEDDED_FILES_PATH = "Root/Names/EmbeddedFiles"


def extract_surfaces(pdf: pymupdf.Document) -> list[Surface]:
    """List every string the document carries outside its page text.

    Args:
        pdf: Open PDF to read.

    Returns:
        Document-level surfaces first, then each page's surfaces in page order.
    """
    surfaces = [
        *_metadata_surfaces(pdf),
        *_xmp_surfaces(pdf),
        *_bookmark_surfaces(pdf),
        *_embedded_file_surfaces(pdf),
        *_associated_file_surfaces(pdf),
        *_structure_surfaces(pdf),
    ]
    for page in pdf:
        surfaces.extend(_page_surfaces(page))
    return surfaces


def _page_surfaces(page: pymupdf.Page) -> Iterator[Surface]:
    """Yield the surfaces placed on one page."""
    yield from _link_surfaces(page)
    yield from _annotation_surfaces(page)
    yield from _form_field_surfaces(page)


def _text_surfaces(
    kind: SurfaceKind,
    values_by_ref: Mapping[str, object],
    page_index: int | None = None,
    bbox: BBox | None = None,
) -> Iterator[Surface]:
    """Yield one surface per non-blank string value.

    Equal values in different fields stay separate surfaces: each field is a
    carrier redaction has to clear.
    """
    for ref, raw in values_by_ref.items():
        if not isinstance(raw, str):
            continue
        value = normalize_text(raw)
        if value.strip():
            yield Surface(kind, value, ref, page_index, bbox)


def _decode_target(target: str | None) -> str | None:
    """Undo percent-encoding in a link target.

    `mailto:jan%40example.com` hides the address from an email finder. PyMuPDF
    also percent-encodes file paths it reports, e.g. `C%3A/Users/...`.
    """
    return unquote(target) if target else target


def _metadata_surfaces(pdf: pymupdf.Document) -> Iterator[Surface]:
    """Yield the values of the document information dictionary.

    Read raw rather than through `pdf.metadata`, which reports only the standard
    keys and invents a `format` entry: producers add keys such as `Company`.
    """
    kind, info = pdf.xref_get_key(_TRAILER, "Info")
    if kind != "xref":
        return
    info_xref = int(info.split()[0])
    values = {key: _info_value(pdf, info_xref, key) for key in pdf.xref_get_keys(info_xref)}
    yield from _text_surfaces(SurfaceKind.METADATA, values)


def _info_value(pdf: pymupdf.Document, info_xref: int, key: str) -> str | None:
    """Return an information dictionary value as text, or `None` if it has none."""
    value_type, source = pdf.xref_get_key(info_xref, key)
    if value_type in _STRING_TYPES:
        # Resolves references and decodes PDFDocEncoding and UTF-16 strings.
        return mupdf.fz_lookup_metadata2(pdf.this, f"info:{key}")
    if value_type in _STRUCTURED_TYPES:
        return source
    return None


def _xmp_surfaces(pdf: pymupdf.Document) -> Iterator[Surface]:
    """Yield the document's XMP packet as a single surface.

    XMP schemas are open-ended, so the raw XML is scanned instead of a fixed
    list of properties.
    """
    xmp_xref = pdf.xref_xml_metadata()
    if not xmp_xref:
        return
    packet = pdf.xref_stream(xmp_xref)
    if packet:
        text = packet.decode("utf-8", errors="replace")
        yield from _text_surfaces(SurfaceKind.XMP, {str(xmp_xref): text})


def _bookmark_surfaces(pdf: pymupdf.Document) -> Iterator[Surface]:
    """Yield outline titles and any external targets they point to.

    A bookmark is not drawn on the page it points to, so it has no page index.
    """
    for position, (_level, title, _page, destination) in enumerate(pdf.get_toc(simple=False)):
        yield from _text_surfaces(
            SurfaceKind.BOOKMARK,
            {
                f"{position}/title": title,
                f"{position}/uri": _decode_target(destination.get("uri")),
                f"{position}/file": _decode_target(destination.get("file")),
            },
        )


def _embedded_file_surfaces(pdf: pymupdf.Document) -> Iterator[Surface]:
    """Yield the labels of files attached to the document as a whole."""
    for position, (key, file_spec) in enumerate(_name_tree_entries(_attachment_tree(pdf))):
        yield from _text_surfaces(
            SurfaceKind.EMBEDDED_FILE,
            {
                f"{position}/name": _pdf_text(key),
                f"{position}/filename": _file_spec_text(file_spec, "F"),
                f"{position}/ufilename": _file_spec_text(file_spec, "UF"),
                f"{position}/description": _file_spec_text(file_spec, "Desc"),
            },
        )


def _attachment_tree(pdf: pymupdf.Document) -> mupdf.PdfObj:
    trailer = mupdf.pdf_trailer(mupdf.pdf_document_from_fz_document(pdf.this))
    return mupdf.pdf_dict_getp(trailer, _EMBEDDED_FILES_PATH)


def _name_tree_entries(root: mupdf.PdfObj) -> Iterator[tuple[mupdf.PdfObj, mupdf.PdfObj]]:
    """Yield a name tree's key and value pairs in tree order.

    A node lists pairs in `Names` and child nodes in `Kids` (PDF 32000-1,
    7.9.6). A node reached a second time is skipped, so a malformed tree that
    refers back to itself cannot loop; the walk keeps its own stack, so a deep
    tree cannot exhaust Python's recursion limit.
    """
    visited: set[int] = set()
    pending = [root]
    while pending:
        node = pending.pop()
        if mupdf.pdf_is_indirect(node):
            number = mupdf.pdf_to_num(node)
            if number in visited:
                continue
            visited.add(number)
        names = mupdf.pdf_dict_gets(node, "Names")
        for index in range(0, mupdf.pdf_array_len(names) - 1, 2):
            yield mupdf.pdf_array_get(names, index), mupdf.pdf_array_get(names, index + 1)
        kids = mupdf.pdf_dict_gets(node, "Kids")
        pending.extend(
            mupdf.pdf_array_get(kids, index) for index in reversed(range(mupdf.pdf_array_len(kids)))
        )


def _associated_file_surfaces(pdf: pymupdf.Document) -> Iterator[Surface]:
    """Yield the labels of file specifications listed in any `/AF` array."""
    listed = _listed_file_specs(pdf)
    for xref, file_specs in _associated_files(pdf).items():
        for position, file_spec in enumerate(file_specs):
            if mupdf.pdf_is_indirect(file_spec) and mupdf.pdf_to_num(file_spec) in listed:
                continue
            ref = f"{xref}/af{position}"
            yield from _text_surfaces(
                SurfaceKind.EMBEDDED_FILE,
                {
                    f"{ref}/filename": _file_spec_text(file_spec, "F"),
                    f"{ref}/ufilename": _file_spec_text(file_spec, "UF"),
                    f"{ref}/description": _file_spec_text(file_spec, "Desc"),
                },
            )


def _associated_files(pdf: pymupdf.Document) -> dict[int, list[mupdf.PdfObj]]:
    """Return each object's associated files, across all `/AF` arrays it holds.

    One object can hold several arrays (property lists in its resources), so
    files are numbered per object rather than per array.
    """
    by_object: dict[int, list[mupdf.PdfObj]] = {}
    for xref, dictionary in dictionaries_with_key(pdf, "AF"):
        file_specs = mupdf.pdf_dict_gets(dictionary, "AF")
        by_object.setdefault(xref, []).extend(
            mupdf.pdf_array_get(file_specs, index)
            for index in range(mupdf.pdf_array_len(file_specs))
        )
    return by_object


def _listed_file_specs(pdf: pymupdf.Document) -> set[int]:
    """Return the object numbers of file specifications listed as attachments already."""
    listed = {
        mupdf.pdf_to_num(file_spec)
        for _key, file_spec in _name_tree_entries(_attachment_tree(pdf))
        if mupdf.pdf_is_indirect(file_spec)
    }
    for page in pdf:
        for annot_xref, *_ in page.annot_xrefs():
            if pdf.xref_get_key(annot_xref, "Subtype") != ("name", f"/{_FILE_ATTACHMENT_SUBTYPE}"):
                continue
            kind, value = pdf.xref_get_key(annot_xref, "FS")
            if kind == "xref":
                listed.add(int(value.split()[0]))
    return listed


def _file_spec_text(file_spec: mupdf.PdfObj, key: str) -> str | None:
    """Return a file specification's string entry as text, or `None` if it has none."""
    return _pdf_text(mupdf.pdf_dict_gets(file_spec, key))


def _pdf_text(value: mupdf.PdfObj) -> str | None:
    """Decode a PDF string (PDFDocEncoding or UTF-16, possibly indirect), or `None`."""
    return mupdf.pdf_to_text_string(value) if mupdf.pdf_is_string(value) else None


def _structure_surfaces(pdf: pymupdf.Document) -> Iterator[Surface]:
    """Yield the text a tagged PDF keeps in its structure tree.

    This text is written for screen readers and never drawn. `ActualText` can
    hold the very words redaction removes from the page, and `Alt` often names
    the person in a photo. A structure element is recognised by its structure
    type `S` and its parent `P`, since its `Type` entry is optional.
    """
    if pdf.xref_get_key(pdf.pdf_catalog(), "StructTreeRoot")[0] == "null":
        return
    for xref in range(1, pdf.xref_length()):
        if not _is_structure_element(pdf, xref):
            continue
        values = {f"{xref}/{key}": _inline_string(pdf, xref, key) for key in _STRUCTURE_TEXT_KEYS}
        yield from _text_surfaces(SurfaceKind.STRUCTURE, values)


def _is_structure_element(pdf: pymupdf.Document, xref: int) -> bool:
    """Whether an object is a structure element."""
    return pdf.xref_get_key(xref, "S")[0] == "name" and pdf.xref_get_key(xref, "P")[0] == "xref"


def _inline_string(pdf: pymupdf.Document, xref: int, key: str) -> str | None:
    """Return a dictionary's string value, or `None` if the key holds none.

    Structure elements store their text inline in practice; a value stored as a
    separate object is left to the leakage check's object scan.
    """
    value_type, value = pdf.xref_get_key(xref, key)
    return value if value_type == "string" else None


def _link_surfaces(page: pymupdf.Page) -> Iterator[Surface]:
    """Yield the external targets of a page's links.

    Links within the document carry no string and are skipped. Unlike other
    annotations, PyMuPDF reports link rectangles already in rotated page space.
    """
    for link in page.get_links():
        yield from _text_surfaces(
            SurfaceKind.LINK,
            {
                f"{link['xref']}/uri": _decode_target(link.get("uri")),
                f"{link['xref']}/file": _decode_target(link.get("file")),
            },
            page.number,
            rect_to_bbox(link["from"]),
        )


def _annotation_surfaces(page: pymupdf.Page) -> Iterator[Surface]:
    """Yield the text of a page's annotations and the labels of attached files.

    `title` is the annotation's author, usually a person's name.
    """
    for annot in page.annots():
        bbox = unrotated_rect_to_bbox(annot.rect, page)
        info = annot.info
        yield from _text_surfaces(
            SurfaceKind.ANNOTATION,
            {
                f"{annot.xref}/content": info.get("content"),
                f"{annot.xref}/title": info.get("title"),
                f"{annot.xref}/subject": info.get("subject"),
            },
            page.number,
            bbox,
        )
        if annot.type[1] == _FILE_ATTACHMENT_SUBTYPE:
            file_spec = mupdf.pdf_dict_gets(mupdf.pdf_annot_obj(annot.this), "FS")
            # The Unicode name when present, as `Annot.file_info` reports it.
            filename = _file_spec_text(file_spec, "UF") or _file_spec_text(file_spec, "F")
            yield from _text_surfaces(
                SurfaceKind.EMBEDDED_FILE,
                {
                    f"{annot.xref}/filename": filename,
                    f"{annot.xref}/description": _file_spec_text(file_spec, "Desc"),
                },
                page.number,
                bbox,
            )


def _form_field_surfaces(page: pymupdf.Page) -> Iterator[Surface]:
    """Yield the values of a page's form fields.

    A multi-select list reports its value as a list of strings.
    """
    for annot in page.widgets():
        # PyMuPDF annotates widgets() as yielding Annot; it yields Widget.
        widget = cast("pymupdf.Widget", annot)
        value: object = widget.field_value
        if isinstance(value, list | tuple):
            value = "\n".join(str(item) for item in value)
        bbox = unrotated_rect_to_bbox(widget.rect, page) if widget.rect is not None else None
        yield from _text_surfaces(
            SurfaceKind.FORM_FIELD,
            {f"{widget.xref}/value": value},
            page.number,
            bbox,
        )
