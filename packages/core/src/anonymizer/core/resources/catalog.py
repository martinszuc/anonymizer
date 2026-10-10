"""The resource catalog: every model and dataset, pinned and checksummed.

The catalog is data (`catalog.toml` next to this module), so the download
script, the evaluation and the app's model setup page read one list. Loading
validates it strictly: a malformed entry would otherwise surface only when
someone tries to download it, or worse, download something unverified.

A model trained on this machine (`python -m experiments train`) has no
official source to download it from. It is listed in its storage root's own
catalog, `models/trained.json`, which the training writes: the same fields,
except that `trained` is set, `source` names the training record instead of
a URL, and its files carry no URL, only a size and a SHA-256. Such an entry
can be loaded and verified, never fetched; `load_catalog(root=...)` adds it
to the shipped entries, which it may not replace.
"""

from __future__ import annotations

import json
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

TRAINED_CATALOG = "trained.json"
"""A storage root's catalog of models trained on this machine, in its `models/` folder."""

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
        url: Where the file is fetched from, pinned to the resource version;
            `None` for a model trained on this machine.
        size: Size in bytes.
        sha256: Expected SHA-256, or None while only a source digest is known.
        source_digest: `(algorithm, hex)` as published by the source, for files
            whose SHA-256 the source does not publish.
        unpack: Archive format to extract after verification, if any.
    """

    path: str
    url: str | None
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
        source: Official page the files come from; for a trained model, the
            record of its training run.
        version: The source's immutable pin (commit hash or repository handle);
            for a trained model, the SHA-256 of its weights.
        licence: SPDX identifier, or a `LicenseRef-` for custom terms.
        languages: ISO 639-1 codes; `mul` for multilingual.
        files: The files to fetch.
        engine: Package that consumes a model, if any.
        requires: Ids of resources needed for this one to work.
        real_personal_data: The content names real people: local evaluation
            only, never a test fixture.
        notes: Free-text remarks.
        trained: Trained on this machine: listed in a storage root's
            `trained.json`, never downloaded.
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
    trained: bool = False

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


def load_catalog(path: Path | None = None, *, root: Path | None = None) -> Catalog:
    """Read and validate the resource catalog.

    Args:
        path: Catalog file; the one shipped with the package when omitted.
        root: A storage root whose trained models (`models/trained.json`) are
            added, if it lists any.

    Returns:
        The validated catalog.

    Raises:
        ValueError: If the catalog or the root's list of trained models is
            malformed, or a trained model reuses a catalog id.
    """
    if path is None:
        text = resources.files(__package__).joinpath("catalog.toml").read_text(encoding="utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    catalog = parse_catalog(tomllib.loads(text))
    if root is None or not trained_catalog_path(root).exists():
        return catalog
    trained = json.loads(trained_catalog_path(root).read_text(encoding="utf-8"))
    return parse_catalog(trained, base=catalog)


def trained_catalog_path(root: Path) -> Path:
    """Return where a storage root lists the models trained on this machine."""
    return root / KIND_DIRECTORIES["model"] / TRAINED_CATALOG


def parse_catalog(raw: dict[str, Any], *, base: Catalog | None = None) -> Catalog:
    """Build a catalog from parsed TOML, validating every entry.

    Args:
        raw: The parsed catalog.
        base: A catalog the entries are added to; they are then trained
            models (see the module docstring) and may require its entries.

    Raises:
        ValueError: If the catalog is malformed.
    """
    if raw.get("schema") != CATALOG_SCHEMA:
        msg = f"unsupported catalog schema {raw.get('schema')!r}, expected {CATALOG_SCHEMA}"
        raise ValueError(msg)
    catalog: dict[str, Resource] = dict(base.resources) if base is not None else {}
    for entry in raw.get("resource", []):
        resource = _parse_resource(entry, trained=base is not None)
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


def _parse_resource(entry: dict[str, Any], *, trained: bool) -> Resource:
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
    if entry.get("trained", False) is not trained:
        raise fail(
            "every entry of trained.json sets trained = true"
            if trained
            else "only a storage root's trained.json lists trained models"
        )
    if trained and kind != "model":
        raise fail("only a model can be trained")
    if not trained and not str(entry["source"]).startswith("https://"):
        raise fail("source must be an HTTPS URL")
    raw_files = entry.get("files", [])
    if not raw_files:
        raise fail("no files")
    files = tuple(_parse_file(raw_file, fail, trained=trained) for raw_file in raw_files)
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
        trained=trained,
    )


def _parse_file(
    entry: dict[str, Any], fail: Callable[[str], ValueError], *, trained: bool
) -> ResourceFile:
    path = entry.get("path", "")
    parts = PurePosixPath(path).parts
    # A path escaping the resource directory would let a catalog entry
    # overwrite arbitrary files under the storage root.
    if not path or PurePosixPath(path).is_absolute() or ".." in parts or "\\" in path:
        raise fail(f"file path {path!r} must be relative and stay inside the resource")
    url = entry.get("url")
    if trained and url is not None:
        raise fail(f"{path}: a trained model's file has no url")
    if not trained and not str(url).startswith("https://"):
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
    if trained and sha256 is None:
        raise fail(f"{path}: a trained model's file needs its sha256")

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
