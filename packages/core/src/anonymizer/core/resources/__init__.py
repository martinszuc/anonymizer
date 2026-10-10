"""Models and datasets: the pinned catalog and its verified download."""

from anonymizer.core.resources.catalog import (
    Catalog,
    Resource,
    ResourceFile,
    load_catalog,
    trained_catalog_path,
)
from anonymizer.core.resources.fetch import (
    ChecksumError,
    FetchResult,
    NotDownloadableError,
    Opener,
    PinRequiredError,
    Progress,
    fetch_resource,
    fetch_with_requirements,
    missing_resources,
    resource_status,
    verify_resource,
)
from anonymizer.core.resources.location import (
    choose_resource_root,
    chosen_resource_root,
    resolve_resource_root,
    user_resource_root,
)
from anonymizer.core.settings import settings_file

__all__ = [
    "Catalog",
    "ChecksumError",
    "FetchResult",
    "NotDownloadableError",
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
    "missing_resources",
    "resolve_resource_root",
    "resource_status",
    "settings_file",
    "trained_catalog_path",
    "user_resource_root",
    "verify_resource",
]
