"""Finding dictionaries and streams anywhere in a PDF's object graph.

File specifications are not confined to one place. Besides the attachment list
and attachment annotations, PDF 2.0 and PDF/A-3 let any page, annotation,
XObject, structure element, marked-content property list or document part refer
to *associated files* through an `/AF` array, and actions and multimedia
annotations carry file specifications of their own. A key is therefore looked
for in every object, including dictionaries nested directly inside another one,
such as a property list inside a page's resources.
"""

from __future__ import annotations

from collections.abc import Iterator

import pymupdf
from pymupdf import mupdf

_EMBEDDED_FILE_TYPE = "/EmbeddedFile"


def dictionaries_with_key(pdf: pymupdf.Document, key: str) -> list[tuple[int, mupdf.PdfObj]]:
    """Return every dictionary holding a key, with the number of the object it lies in.

    Args:
        pdf: Open PDF to search.
        key: Dictionary key without the leading slash, e.g. `AF`.

    Returns:
        `(object number, dictionary)` pairs in object order; a dictionary nested
        directly in an object reports that object's number.
    """
    document = mupdf.pdf_document_from_fz_document(pdf.this)
    found: list[tuple[int, mupdf.PdfObj]] = []
    for xref in range(1, pdf.xref_length()):
        # Reading the source first spares walking objects that cannot hold the key.
        if f"/{key}" not in pdf.xref_object(xref, compressed=True):
            continue
        found.extend(
            (xref, dictionary)
            for dictionary in _holding(mupdf.pdf_load_object(document, xref), key)
        )
    return found


def _holding(value: mupdf.PdfObj, key: str) -> Iterator[mupdf.PdfObj]:
    """Yield the dictionaries holding a key within a value, not following references.

    A referenced object is visited under its own number, so following
    references here would only visit it twice, or loop.
    """
    if mupdf.pdf_is_indirect(value):
        return
    if mupdf.pdf_is_dict(value):
        if not mupdf.pdf_is_null(mupdf.pdf_dict_gets(value, key)):
            yield value
        for index in range(mupdf.pdf_dict_len(value)):
            yield from _holding(mupdf.pdf_dict_get_val(value, index), key)
    elif mupdf.pdf_is_array(value):
        for index in range(mupdf.pdf_array_len(value)):
            yield from _holding(mupdf.pdf_array_get(value, index), key)


def embedded_file_streams(pdf: pymupdf.Document) -> list[int]:
    """Return the object numbers of every stream typed as an embedded file.

    Args:
        pdf: Open PDF to search.

    Returns:
        Object numbers in ascending order.
    """
    return [
        xref
        for xref in range(1, pdf.xref_length())
        if pdf.xref_is_stream(xref)
        and pdf.xref_get_key(xref, "Type") == ("name", _EMBEDDED_FILE_TYPE)
    ]
