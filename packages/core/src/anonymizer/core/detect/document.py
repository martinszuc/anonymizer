"""Running a detector over a whole document: its pages and its surfaces.

A `Detector` scans pages. To reuse every detector unchanged, including model
backends, a surface is wrapped in a transient `Page` whose text is the surface
value. The page only lives for the call and never enters the document; the
entities it yields are re-attached to the surface.
"""

from __future__ import annotations

from dataclasses import replace

from anonymizer.core.detect.base import Detector
from anonymizer.core.types import Document, Entity, Page, Surface


def detect_surface(detector: Detector, surface: Surface) -> list[Entity]:
    """Return the entities a detector finds in one surface.

    Args:
        detector: Detector to run.
        surface: Surface to scan.

    Returns:
        Entities whose offsets refer to `surface.value`, carrying the surface's
        id, page index and, if it is drawn on a page, its box.
    """
    transient = Page(index=surface.page_index or 0, width=0.0, height=0.0, text=surface.value)
    bboxes = [surface.bbox] if surface.bbox is not None else []
    return [
        replace(
            entity,
            page_index=surface.page_index,
            surface_id=surface.surface_id,
            bboxes=list(bboxes),
        )
        for entity in detector.detect(transient)
    ]


def detect_document(detector: Detector, document: Document) -> list[Entity]:
    """Return the entities a detector finds anywhere in a document.

    Args:
        detector: Detector to run.
        document: Document whose pages and surfaces are scanned.

    Returns:
        Page-text entities in page order, followed by surface entities in
        surface order.
    """
    on_pages = [entity for page in document.pages for entity in detector.detect(page)]
    on_surfaces = [
        entity for surface in document.surfaces for entity in detect_surface(detector, surface)
    ]
    return on_pages + on_surfaces
