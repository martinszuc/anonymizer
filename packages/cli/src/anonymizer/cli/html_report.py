"""HTML view of a document and what detection found in it, for `anonymize inspect`.

The report is one self-contained file. Each page is rendered as an image with
the entity boxes drawn over it in an SVG whose view box is the page size in
PDF points, the system the boxes are stored in, so no coordinate conversion
happens here. The entities and hidden items of each page are listed under it.

Its Content-Security-Policy allows nothing but the embedded images and styles,
so opening the report cannot load or send anything. Type filters are CSS
(`:has()`), not scripts.
"""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path

import pymupdf
from anonymizer.cli import report
from anonymizer.core.types import BBox, Document, Entity, EntityType, Surface

_CONTENT_SECURITY_POLICY = "default-src 'none'; img-src data:; style-src 'unsafe-inline'"
_SURFACE_PREVIEW_LENGTH = 300

# Distinguishable from one another and from black text on a white page.
TYPE_COLORS: dict[EntityType, str] = {
    EntityType.PERSON: "#d62728",
    EntityType.BIRTH_NUMBER: "#9467bd",
    EntityType.BANK_ACCOUNT: "#8c564b",
    EntityType.IBAN: "#e377c2",
    EntityType.CREDIT_CARD: "#bcbd22",
    EntityType.COMPANY_ID: "#17becf",
    EntityType.EMAIL: "#1f77b4",
    EntityType.PHONE: "#2ca02c",
    EntityType.URL: "#ff7f0e",
    EntityType.ADDRESS: "#a6761d",
    EntityType.DATE: "#66a61e",
    EntityType.ID_NUMBER: "#542788",
    EntityType.ORGANIZATION: "#e6550d",
    EntityType.REGION: "#111827",
    EntityType.OTHER: "#6b7280",
}

_STYLE = """
:root { color-scheme: light; font: 14px/1.45 system-ui, sans-serif; color: #1f2937; }
body { margin: 0 auto; padding: 24px 16px 64px; max-width: 960px; background: #f3f4f6; }
h1 { font-size: 20px; margin: 0 0 4px; overflow-wrap: anywhere; }
h2 { font-size: 16px; margin: 32px 0 8px; }
.muted { color: #6b7280; font-weight: normal; }
.warning { background: #fef3c7; border-left: 4px solid #d97706; padding: 8px 12px; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 14px; margin: 16px 0; padding: 10px 12px;
  background: #fff; border-radius: 6px; position: sticky; top: 0; z-index: 1;
  box-shadow: 0 1px 3px rgb(0 0 0 / 0.12); }
.legend label { display: inline-flex; align-items: center; gap: 5px; cursor: pointer; }
.swatch { display: inline-block; width: 12px; height: 12px; border-radius: 2px; }
.canvas { position: relative; background: #fff; box-shadow: 0 1px 4px rgb(0 0 0 / 0.2); }
.canvas img { display: block; width: 100%; height: auto; }
.canvas svg { position: absolute; inset: 0; width: 100%; height: 100%; }
rect.entity { fill-opacity: 0.22; stroke-width: 1; vector-effect: non-scaling-stroke; }
rect.entity:hover { fill-opacity: 0.45; stroke-width: 2; }
rect.review-rejected { fill-opacity: 0.04; stroke-dasharray: 4 3; }
rect.review-confirmed { stroke-width: 2; }
rect.hidden-item { fill: none; stroke: #6b7280; stroke-dasharray: 2 2;
  vector-effect: non-scaling-stroke; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; background: #fff;
  font-size: 13px; }
th, td { text-align: left; padding: 4px 8px; border-bottom: 1px solid #e5e7eb;
  vertical-align: top; overflow-wrap: anywhere; }
th { font-weight: 600; color: #4b5563; }
tr.review-rejected td { color: #9ca3af; text-decoration: line-through; }
"""


def render_report(source: Path, document: Document, *, dpi: int) -> str:
    """Build the HTML report for a document.

    Args:
        source: The PDF the document was loaded from; its pages are rendered.
        document: The document with its entities and surfaces.
        dpi: Resolution of the page images.

    Returns:
        A complete HTML page with every image embedded.
    """
    with pymupdf.open(source) as pdf:
        pages = [
            _page_section(document, index, _page_png(pdf[index], dpi))
            for index in range(len(document.pages))
        ]
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en"><head><meta charset="utf-8">',
            f'<meta http-equiv="Content-Security-Policy" content="{_CONTENT_SECURITY_POLICY}">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>Inspect {escape(source.name)}</title>",
            f"<style>{_STYLE}{_filter_rules(document)}</style>",
            "</head><body>",
            f"<h1>{escape(source.name)}</h1>",
            f'<p class="muted">{escape(report.document_summary(document))}. '
            "Contains the document's content: treat this file like the original.</p>",
            _legend(document),
            *pages,
            _document_level_section(document),
            "</body></html>",
        ]
    )


def _page_png(pdf_page: pymupdf.Page, dpi: int) -> str:
    """Render a page as a base64 PNG; the image covers exactly `page.rect`."""
    pixmap = pdf_page.get_pixmap(dpi=dpi)
    return base64.b64encode(pixmap.tobytes("png")).decode("ascii")


def _type_class(entity_type: EntityType) -> str:
    return f"t-{entity_type.value}"


def _filter_rules(document: Document) -> str:
    """CSS that hides a type while its legend checkbox is cleared."""
    rules = [
        f"body:has(#show-{entity_type.value}:not(:checked)) .{_type_class(entity_type)} "
        "{ display: none; }"
        for entity_type in _types_present(document)
    ]
    rules.append("body:has(#show-hidden:not(:checked)) .hidden-item { display: none; }")
    rules.extend(
        f".{_type_class(entity_type)} {{ fill: {color}; stroke: {color}; }}"
        for entity_type, color in TYPE_COLORS.items()
    )
    return "\n".join(rules)


def _types_present(document: Document) -> list[EntityType]:
    return sorted({entity.type for entity in document.entities}, key=list(EntityType).index)


def _legend(document: Document) -> str:
    """Checkboxes that show or hide each entity type and the hidden items."""
    items = []
    for entity_type in _types_present(document):
        count = sum(entity.type is entity_type for entity in document.entities)
        items.append(
            f'<label><input type="checkbox" id="show-{entity_type.value}" checked>'
            f'<span class="swatch" style="background:{TYPE_COLORS[entity_type]}"></span>'
            f"{entity_type.value} ({count})</label>"
        )
    items.append(
        '<label><input type="checkbox" id="show-hidden" checked>'
        f"hidden-item boxes ({sum(s.bbox is not None for s in document.surfaces)})</label>"
    )
    items.append('<span class="muted">dashed box: rejected in review</span>')
    return f'<div class="legend">{"".join(items)}</div>'


def _page_section(document: Document, index: int, png: str) -> str:
    """One page: the image with its overlay, then its entities and hidden items."""
    page = document.page(index)
    entities = _entities_placed_on(document, index)
    surfaces = [surface for surface in document.surfaces if surface.page_index == index]
    shapes = [
        _rect(surface.bbox, "hidden-item", f"{surface.kind.value}: {surface.value}")
        for surface in surfaces
        if surface.bbox is not None
    ]
    shapes.extend(
        _rect(box, _entity_classes(entity), _entity_tooltip(document, entity))
        for entity in entities
        for box in entity.bboxes
    )
    parts = [
        f'<section id="page-{index + 1}">',
        f'<h2>Page {index + 1} <span class="muted">'
        f"{page.width:.0f} &times; {page.height:.0f} pt</span></h2>",
    ]
    if not page.has_text_layer:
        parts.append(
            '<p class="warning">No text layer (a scan?): nothing on this page is detected '
            "until OCR exists.</p>"
        )
    parts += [
        '<div class="canvas">',
        f'<img src="data:image/png;base64,{png}" alt="Page {index + 1}">',
        f'<svg viewBox="0 0 {page.width:.2f} {page.height:.2f}" preserveAspectRatio="none">',
        *shapes,
        "</svg></div>",
        _entity_table(document, entities),
        _surface_table(surfaces),
        "</section>",
    ]
    return "\n".join(parts)


def _entities_placed_on(document: Document, index: int) -> list[Entity]:
    """Everything with a place on the page: text spans, drawn regions, page surfaces.

    `Document.entities_on_page` returns only spans of the page text; regions and
    entities in a link or annotation on the page have boxes here too.
    """
    in_surfaces = [
        entity
        for entity in document.entities
        if entity.surface_id is not None and entity.page_index == index
    ]
    return document.entities_on_page(index) + document.regions_on_page(index) + in_surfaces


def _document_level_section(document: Document) -> str:
    """Entities and hidden items that belong to no page, such as metadata."""
    entities = [entity for entity in document.entities if entity.page_index is None]
    surfaces = [surface for surface in document.surfaces if surface.page_index is None]
    if not entities and not surfaces:
        return ""
    return "\n".join(
        [
            '<section id="document">',
            "<h2>Document level</h2>",
            _entity_table(document, entities),
            _surface_table(surfaces),
            "</section>",
        ]
    )


def _rect(box: BBox, classes: str, tooltip: str) -> str:
    return (
        f'<rect class="{classes}" x="{box.x0:.2f}" y="{box.y0:.2f}" '
        f'width="{box.width:.2f}" height="{box.height:.2f}"><title>{escape(tooltip)}</title></rect>'
    )


def _entity_classes(entity: Entity) -> str:
    return f"entity {_type_class(entity.type)} review-{entity.review.value}"


def _entity_tooltip(document: Document, entity: Entity) -> str:
    """Hover text for an entity box: what it is, who found it, what it covers."""
    return (
        f"{entity.type.value} · {entity.source.value}{_score(entity)} · "
        f"{entity.review.value}\n{report.covers(document, entity)}"
    )


def _score(entity: Entity) -> str:
    return "" if entity.score is None else f" {entity.score:.2f}"


def _entity_table(document: Document, entities: list[Entity]) -> str:
    if not entities:
        return ""
    rows = [
        f'<tr class="{_type_class(entity.type)} review-{entity.review.value}">'
        f'<td><span class="swatch" style="background:{TYPE_COLORS[entity.type]}"></span> '
        f"{entity.type.value}</td><td>{entity.source.value}{_score(entity)}</td>"
        f"<td>{entity.review.value}</td>"
        f"<td>{escape(report.covers(document, entity))}</td></tr>"
        for entity in entities
    ]
    return (
        "<table><tr><th>type</th><th>source</th><th>review</th><th>covers</th></tr>"
        f"{''.join(rows)}</table>"
    )


def _surface_table(surfaces: list[Surface]) -> str:
    """Hidden items, all of which redaction removes whether or not anything was found."""
    if not surfaces:
        return ""
    rows = [
        f"<tr><td>{surface.kind.value}</td><td>{escape(_preview(surface.value))}</td></tr>"
        for surface in surfaces
    ]
    return (
        "<table><tr><th>hidden item</th><th>value (removed on redaction)</th></tr>"
        f"{''.join(rows)}</table>"
    )


def _preview(value: str) -> str:
    """Shorten a long value such as an XMP packet, which can run to kilobytes."""
    if len(value) <= _SURFACE_PREVIEW_LENGTH:
        return value
    return value[: _SURFACE_PREVIEW_LENGTH - 1] + "…"
