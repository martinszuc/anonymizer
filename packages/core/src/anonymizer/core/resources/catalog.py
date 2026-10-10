"""The resource catalog: every model and dataset, pinned and checksummed.

The catalog is data (`catalog.toml` next to this module), so the download
script, the evaluation and the app's model setup page read one list. Loading
validates it strictly: a malformed entry would otherwise surface only when
someone tries to download it, or worse, download something unverified.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path, PurePosixPath
from typing import Any, Literal

CATALOG_SCHEMA = 1

ResourceKind = Literal["model", "dataset"]

KIND_DIRECTORIES: dict[str, str] = {"model": "models", "dataset": "data"}
"""Top-level directory each kind is stored under, relative to the storage root."""

USES = frozenset(
    {"ner", "tokenizer", "ocr-detection", "ocr-recognition", "ocr-layout", "benchmark", "training"}
)
DIGEST_ALGORITHMS = frozenset({"md5", "git-sha1"})
UNPACK_FORMATS = frozenset({"zip"})

_HEX_LENGTHS = {"sha256": 64, "md5": 32, "git-sha1": 40}
_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
_LANGUAGE_PATTERN = re.compile(r"^([a-z]{2}|mul)$")


@dataclass(frozen=True)
class ResourceFile:
    """One file of a resource.

    Attributes:
        path: Location inside the resource directory, POSIX separators.
        url: Where the file is fetched from, pinned to the resource version.
        size: Size in bytes.
        sha256: Expected SHA-256, or None while only a source digest is known.
        source_digest: `(algorithm, hex)` as published by the source, for files
            whose SHA-256 the source does not publish.
        unpack: Archive format to extract after verification, if any.
    """

    path: str
    url: str
    size: int
    sha256: str | None = None
    source_digest: tuple[str, str] | None = None
    unpack: str | None = None


@dataclass(frozen=True)
class Resource:
    """A model or dataset entry.

    Attributes:
        id: Stable name; also the directory the files are stored in.
        name: Human-readable name.
        kind: `model` or `dataset`.
        uses: What the resource serves (`ner`, `ocr-recognition`, `benchmark`, ...).
        source: Official page the files come from.
        version: The source's immutable pin (commit hash or repository handle).
        licence: SPDX identifier, or a `LicenseRef-` for custom terms.
        languages: ISO 639-1 codes; `mul` for multilingual.
        files: The files to fetch.
        engine: Package that consumes a model, if any.
        requires: Ids of resources needed for this one to work.
        real_personal_data: The content names real people: local evaluation
            only, never a test fixture.
        notes: Free-text remarks.
    """

    id: str
    name: str
    kind: ResourceKind
    uses: tuple[str, ...]
    source: str
    version: str
    licence: str
    languages: tuple[str, ...]
    files: tuple[ResourceFile, ...]
    engine: str | None = None
    requires: tuple[str, ...] = ()
    real_personal_data: bool = False
    notes: str = ""

    @property
    def size(self) -> int:
        """Total size of the files in bytes."""
        return sum(item.size for item in self.files)

    def directory(self, root: Path) -> Path:
        """Return where this resource is stored under a storage root."""
        return root / KIND_DIRECTORIES[self.kind] / self.id


@dataclass(frozen=True)
class Catalog:
    """All resources, by id, in catalog order."""

    resources: dict[str, Resource] = field(default_factory=dict)

    def __getitem__(self, resource_id: str) -> Resource:
        """Return a resource by id.

        Raises:
            KeyError: If no resource has this id.
        """
        try:
            return self.resources[resource_id]
        except KeyError:
            msg = f"unknown resource {resource_id!r}"
            raise KeyError(msg) from None

    def with_requirements(self, resource_id: str) -> list[Resource]:
        """Return a resource preceded by everything it requires, each once.

        Raises:
            KeyError: If the id is unknown.
            ValueError: If the requirements form a cycle.
        """
        ordered: list[Resource] = []
        visiting: list[str] = []

        def visit(current_id: str) -> None:
            resource = self[current_id]
            if resource in ordered:
                return
            if current_id in visiting:
                msg = f"requirement cycle: {' -> '.join([*visiting, current_id])}"
                raise ValueError(msg)
            visiting.append(current_id)
            for required in resource.requires:
                visit(required)
            visiting.pop()
            ordered.append(resource)

        visit(resource_id)
        return ordered


def load_catalog(path: Path | None = None) -> Catalog:
    """Read and validate the resource catalog.

    Args:
        path: Catalog file; the one shipped with the package when omitted.

    Returns:
        The validated catalog.

    Raises:
        ValueError: If the catalog is malformed.
    """
    if path is None:
        text = resources.files(__package__).joinpath("catalog.toml").read_text(encoding="utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    return parse_catalog(tomllib.loads(text))


def parse_catalog(raw: dict[str, Any]) -> Catalog:
    """Build a catalog from parsed TOML, validating every entry.

    Raises:
        ValueError: If the catalog is malformed.
    """
    if raw.get("schema") != CATALOG_SCHEMA:
        msg = f"unsupported catalog schema {raw.get('schema')!r}, expected {CATALOG_SCHEMA}"
        raise ValueError(msg)
    catalog: dict[str, Resource] = {}
    for entry in raw.get("resource", []):
        resource = _parse_resource(entry)
        if resource.id in catalog:
            msg = f"duplicate resource id {resource.id!r}"
            raise ValueError(msg)
        catalog[resource.id] = resource
    for resource in catalog.values():
        for required in resource.requires:
            if required not in catalog:
                msg = f"{resource.id}: requires unknown resource {required!r}"
                raise ValueError(msg)
    parsed = Catalog(catalog)
    for resource_id in catalog:
        parsed.with_requirements(resource_id)
    return parsed


def _parse_resource(entry: dict[str, Any]) -> Resource:
    resource_id = entry.get("id", "")
    if not isinstance(resource_id, str) or not _ID_PATTERN.match(resource_id):
        msg = f"invalid resource id {resource_id!r}"
        raise ValueError(msg)

    def fail(reason: str) -> ValueError:
        return ValueError(f"{resource_id}: {reason}")

    kind = entry.get("kind")
    if kind not in KIND_DIRECTORIES:
        raise fail(f"kind must be one of {sorted(KIND_DIRECTORIES)}, not {kind!r}")
    uses = tuple(entry.get("uses", ()))
    if not uses or not set(uses) <= USES:
        raise fail(f"uses must be a non-empty subset of {sorted(USES)}")
    languages = tuple(entry.get("languages", ()))
    if not languages or not all(_LANGUAGE_PATTERN.match(code) for code in languages):
        raise fail("languages must be ISO 639-1 codes or 'mul'")
    for key in ("name", "source", "version", "licence"):
        if not entry.get(key):
            raise fail(f"missing {key}")
    if not str(entry["source"]).startswith("https://"):
        raise fail("source must be an HTTPS URL")
    raw_files = entry.get("files", [])
    if not raw_files:
        raise fail("no files")
    files = tuple(_parse_file(raw_file, fail) for raw_file in raw_files)
    paths = [item.path for item in files]
    if len(set(paths)) != len(paths):
        raise fail("duplicate file path")

    return Resource(
        id=resource_id,
        name=entry["name"],
        kind=kind,
        uses=uses,
        source=entry["source"],
        version=entry["version"],
        licence=entry["licence"],
        languages=languages,
        files=files,
        engine=entry.get("engine"),
        requires=tuple(entry.get("requires", ())),
        real_personal_data=bool(entry.get("real_personal_data", False)),
        notes=entry.get("notes", "").strip(),
    )


def _parse_file(entry: dict[str, Any], fail: Callable[[str], ValueError]) -> ResourceFile:
    path = entry.get("path", "")
    parts = PurePosixPath(path).parts
    # A path escaping the resource directory would let a catalog entry
    # overwrite arbitrary files under the storage root.
    if not path or PurePosixPath(path).is_absolute() or ".." in parts or "\\" in path:
        raise fail(f"file path {path!r} must be relative and stay inside the resource")
    url = entry.get("url", "")
    if not url.startswith("https://"):
        raise fail(f"{path}: url must be HTTPS")
    size = entry.get("size")
    if not isinstance(size, int) or size <= 0:
        raise fail(f"{path}: size must be a positive number of bytes")

    sha256 = entry.get("sha256")
    if sha256 is not None and not _is_hex(sha256, "sha256"):
        raise fail(f"{path}: sha256 must be 64 lowercase hex digits")
    source_digest = None
    if "source_digest" in entry:
        algorithm, _, value = str(entry["source_digest"]).partition(":")
        if algorithm not in DIGEST_ALGORITHMS or not _is_hex(value, algorithm):
            raise fail(f"{path}: source_digest must be md5:<hex> or git-sha1:<hex>")
        source_digest = (algorithm, value)
    if sha256 is None and source_digest is None:
        raise fail(f"{path}: needs sha256 or source_digest")

    unpack = entry.get("unpack")
    if unpack is not None and unpack not in UNPACK_FORMATS:
        raise fail(f"{path}: unpack must be one of {sorted(UNPACK_FORMATS)}")
    return ResourceFile(
        path=path,
        url=url,
        size=size,
        sha256=sha256,
        source_digest=source_digest,
        unpack=unpack,
    )


def _is_hex(value: str, algorithm: str) -> bool:
    return bool(re.fullmatch(f"[0-9a-f]{{{_HEX_LENGTHS[algorithm]}}}", value))
