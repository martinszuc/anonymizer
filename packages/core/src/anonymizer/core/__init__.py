"""Core library: document ingest, entity detection and redaction.

The package is UI- and CLI-agnostic. All components exchange data through the
contract defined in `anonymizer.core.types`.
"""

from anonymizer.core.types import (
    SCHEMA_VERSION,
    BBox,
    DetectionSource,
    Document,
    Entity,
    EntityType,
    Page,
    ReviewState,
    Surface,
    SurfaceKind,
    Word,
)

__version__ = "0.5.0"  # x-release-please-version

__all__ = [
    "SCHEMA_VERSION",
    "BBox",
    "DetectionSource",
    "Document",
    "Entity",
    "EntityType",
    "Page",
    "ReviewState",
    "Surface",
    "SurfaceKind",
    "Word",
    "__version__",
]
