"""Clearing every string a PDF carries outside its page text.

The counterpart of `ingest.surfaces`: whatever that module lists, this module
removes, **whether or not an entity was detected in it**. No rule recognises a
free-text metadata title, and an attachment's contents are never scanned at all,
so clearing cannot wait for detection. This follows the sanitizing step of
established redaction tools rather than judging each carrier.

Links that stay within the document carry no string and are kept; every other
annotation is removed, since its text, author and appearance can all carry
personal data.

Page thumbnails, small preview images some producers embed for a viewer's
sidebar, are removed too: they are a picture of the unredacted page.

The structure tree of a tagged PDF is removed whole, which costs the output its
accessibility tags. Pruning it instead is not enough: its replacement text can
repeat redacted words, and its references to removed annotations keep those
annotations, link targets included, alive through garbage collection.
"""

from __future__ import annotations

from typing import cast

import pymupdf

_TRAILER = -1


def clear_surfaces(pdf: pymupdf.Document) -> None:
    """Remove every non-text surface from an open PDF, in place.

    Args:
        pdf: Document to clear; the caller saves it.
    """
    _clear_metadata(pdf)
    _clear_xmp(pdf)
    _clear_bookmarks(pdf)
    _clear_embedded_files(pdf)
    _clear_structure_tree(pdf)
    for page in pdf:
        _clear_links(page)
        _clear_annotations(page)
        _clear_form_fields(page)
        _clear_thumbnail(pdf, page)


def _clear_metadata(pdf: pymupdf.Document) -> None:
    """Drop the information dictionary, custom keys included.

    `set_metadata({})` only empties the standard keys; unlinking the dictionary
    from the trailer lets garbage collection remove it whole.
    """
    pdf.xref_set_key(_TRAILER, "Info", "null")


def _clear_xmp(pdf: pymupdf.Document) -> None:
    """Delete the document's XMP stream."""
    pdf.del_xml_metadata()


def _clear_bookmarks(pdf: pymupdf.Document) -> None:
    """Remove the outline with every title and target in it."""
    pdf.set_toc([])


def _clear_embedded_files(pdf: pymupdf.Document) -> None:
    """Remove every file attached to the document as a whole."""
    for name in pdf.embfile_names():
        pdf.embfile_del(name)


def _clear_structure_tree(pdf: pymupdf.Document) -> None:
    """Remove the structure tree and the claim that the document is tagged."""
    catalog = pdf.pdf_catalog()
    pdf.xref_set_key(catalog, "StructTreeRoot", "null")
    pdf.xref_set_key(catalog, "MarkInfo", "null")


def _clear_links(page: pymupdf.Page) -> None:
    """Remove links that point outside the document."""
    for link in page.get_links():
        if link.get("uri") or link.get("file"):
            page.delete_link(link)


def _clear_annotations(page: pymupdf.Page) -> None:
    """Remove every annotation, attachment annotations included."""
    for annot in list(page.annots()):
        page.delete_annot(annot)


def _clear_thumbnail(pdf: pymupdf.Document, page: pymupdf.Page) -> None:
    """Remove the page's thumbnail image."""
    pdf.xref_set_key(page.xref, "Thumb", "null")


def _clear_form_fields(page: pymupdf.Page) -> None:
    """Remove every form field; its value is also drawn in its appearance."""
    for annot in list(page.widgets()):
        # PyMuPDF annotates widgets() as yielding Annot; it yields Widget.
        page.delete_widget(cast("pymupdf.Widget", annot))
