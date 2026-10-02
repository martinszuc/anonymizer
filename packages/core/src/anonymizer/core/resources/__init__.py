"""Models and datasets: the pinned catalog and its verified download."""

from anonymizer.core.resources.catalog import (
    Catalog,
    Resource,
    ResourceFile,
    load_catalog,
)
from anonymizer.core.resources.fetch import (
    ChecksumError,
    FetchResult,
    Opener,
    PinRequiredError,
    Progress,
    fetch_resource,
    fetch_with_requirements,
    resource_status,
    verify_resource,
)
from anonymizer.core.resources.location import (
    choose_resource_root,
    chosen_resource_root,
    resolve_resource_root,
    settings_file,
    user_resource_root,
)

__all__ = [
    "Catalog",
    "ChecksumError",
    "FetchResult",
    "Opener",
    "PinRequiredError",
    "Progress",
    "Resource",
    "ResourceFile",
    "choose_resource_root",
    "chosen_resource_root",
    "fetch_resource",
    "fetch_with_requirements",
    "load_catalog",
    "resolve_resource_root",
    "resource_status",
    "settings_file",
    "user_resource_root",
    "verify_resource",
]
