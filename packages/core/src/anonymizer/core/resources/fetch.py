"""Downloading and verifying catalog resources.

This is the only code in the project that opens a network connection, and it
runs only when a user asks for one resource by id. Every file is streamed to a
temporary name, hashed on the way, and renamed into place only when its size
and checksums match the catalog; a mismatch deletes the temporary file.

A file for which the source publishes no SHA-256 is fetched only with
`pin=True`: it is then verified against the source's own digest (MD5 or git
blob SHA-1), and its SHA-256 is returned so it can be recorded in the catalog.
"""

from __future__ import annotations

import hashlib
import shutil
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from anonymizer.core.resources.catalog import Resource, ResourceFile

CHUNK_SIZE = 1 << 20
TIMEOUT_SECONDS = 60

Progress = Callable[[ResourceFile, int], None]
"""Called with a file and the bytes received so far."""


Opener = Callable[[str], Any]
"""Opens a URL and returns a context manager yielding a readable response."""


class ChecksumError(ValueError):
    """A downloaded or stored file does not match the catalog."""


class PinRequiredError(ValueError):
    """A file has no SHA-256 in the catalog and pinning was not requested."""


@dataclass(frozen=True)
class FetchResult:
    """Outcome of fetching one resource.

    Attributes:
        downloaded: Paths of the files downloaded in this run.
        present: Paths already on disk and verified, not downloaded again.
        pinned: SHA-256 computed for files that had only a source digest,
            by path; to be written into the catalog.
    """

    downloaded: tuple[str, ...]
    present: tuple[str, ...]
    pinned: dict[str, str]


def fetch_resource(
    resource: Resource,
    root: Path,
    *,
    pin: bool = False,
    opener: Opener | None = None,
    progress: Progress | None = None,
) -> FetchResult:
    """Download a resource's missing files and verify every file.

    Requirements are not followed; fetch each resource from
    `Catalog.with_requirements` in order.

    Args:
        resource: The catalog entry.
        root: Storage root; files go to `models/<id>/` or `data/<id>/` under it.
        pin: Allow files that have only a source digest, and report their SHA-256.
        opener: Opens a URL; `urllib.request.urlopen` with a timeout by default.
        progress: Receives progress while a file downloads.

    Returns:
        What was downloaded, what was already present, and new SHA-256 pins.

    Raises:
        PinRequiredError: If a file has no SHA-256 and `pin` is false. Nothing is
            downloaded in that case.
        ChecksumError: If a file differs from the catalog. The file is removed.
        OSError: If a download or a write fails.
    """
    unpinned = [item.path for item in resource.files if item.sha256 is None]
    if unpinned and not pin:
        msg = (
            f"{resource.id}: no SHA-256 recorded for {', '.join(unpinned)}; "
            "fetch with pinning to verify against the source's digest and record one"
        )
        raise PinRequiredError(msg)

    open_url = opener or _open_url
    directory = resource.directory(root)
    downloaded: list[str] = []
    present: list[str] = []
    pinned: dict[str, str] = {}
    for item in resource.files:
        target = directory / item.path
        if target.exists():
            sha256 = verify_file(item, target)
            present.append(item.path)
        else:
            sha256 = _download(item, target, open_url, progress)
            downloaded.append(item.path)
        if item.sha256 is None:
            pinned[item.path] = sha256
        if item.unpack == "zip" and not _unpacked_directory(target).exists():
            _extract_zip(target, _unpacked_directory(target))
    return FetchResult(tuple(downloaded), tuple(present), pinned)


def verify_resource(resource: Resource, root: Path) -> dict[str, str]:
    """Check a stored resource against the catalog.

    Args:
        resource: The catalog entry.
        root: Storage root the resource was fetched into.

    Returns:
        Problems by file path; empty when every file is present and matches.
    """
    problems: dict[str, str] = {}
    for item in resource.files:
        target = resource.directory(root) / item.path
        if not target.exists():
            problems[item.path] = "missing"
            continue
        try:
            verify_file(item, target)
        except ChecksumError as error:
            problems[item.path] = str(error)
    return problems


def resource_status(resource: Resource, root: Path) -> str:
    """Return `absent`, `partial` or `present` from file existence alone (no hashing)."""
    directory = resource.directory(root)
    found = sum((directory / item.path).exists() for item in resource.files)
    if found == 0:
        return "absent"
    return "present" if found == len(resource.files) else "partial"


def verify_file(item: ResourceFile, path: Path) -> str:
    """Hash a stored file and compare it with the catalog.

    Returns:
        The file's SHA-256.

    Raises:
        ChecksumError: If the size or a checksum differs.
    """
    hasher = _Hasher(item)
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.check(item.path)


def _download(
    item: ResourceFile,
    target: Path,
    open_url: Opener,
    progress: Progress | None,
) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")
    hasher = _Hasher(item)
    try:
        with open_url(item.url) as response, partial.open("wb") as output:
            while chunk := response.read(CHUNK_SIZE):
                hasher.update(chunk)
                # Stop early instead of filling the disk with an unexpected payload.
                if hasher.received > item.size:
                    break
                output.write(chunk)
                if progress is not None:
                    progress(item, hasher.received)
        sha256 = hasher.check(item.path)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    partial.replace(target)
    return sha256


def _open_url(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "anonymizer-resource-fetch"})
    return urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)


class _Hasher:
    """Computes every digest a catalog file is checked against, in one pass."""

    def __init__(self, item: ResourceFile) -> None:
        self.item = item
        self.received = 0
        self.sha256 = hashlib.sha256()
        self.source = None
        if item.source_digest is not None:
            algorithm = item.source_digest[0]
            if algorithm == "md5":
                self.source = hashlib.md5(usedforsecurity=False)
            else:
                # A git blob id hashes a header with the size before the content.
                self.source = hashlib.sha1(usedforsecurity=False)
                self.source.update(f"blob {item.size}\0".encode())

    def update(self, chunk: bytes) -> None:
        self.received += len(chunk)
        self.sha256.update(chunk)
        if self.source is not None:
            self.source.update(chunk)

    def check(self, label: str) -> str:
        """Return the SHA-256, or raise if the size or any digest differs."""
        if self.received != self.item.size:
            msg = f"{label}: expected {self.item.size} bytes, got {self.received}"
            raise ChecksumError(msg)
        sha256 = self.sha256.hexdigest()
        if self.item.sha256 is not None and sha256 != self.item.sha256:
            msg = f"{label}: SHA-256 {sha256} does not match the catalog"
            raise ChecksumError(msg)
        if self.source is not None and self.item.source_digest is not None:
            algorithm, expected = self.item.source_digest
            if self.source.hexdigest() != expected:
                msg = f"{label}: {algorithm} {self.source.hexdigest()} does not match the source"
                raise ChecksumError(msg)
        return sha256


def _unpacked_directory(archive: Path) -> Path:
    return archive.with_name(archive.stem)


def _extract_zip(archive: Path, destination: Path) -> None:
    staging = destination.with_name(destination.name + ".part")
    shutil.rmtree(staging, ignore_errors=True)
    try:
        with zipfile.ZipFile(archive) as bundle:
            root = staging.resolve()
            for member in bundle.namelist():
                # A verified archive is trusted content, but a member named
                # "../x" must still not write outside the destination.
                if not (root / member).resolve().is_relative_to(root):
                    msg = f"{archive.name}: member {member!r} escapes the destination"
                    raise ChecksumError(msg)
            bundle.extractall(staging)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    staging.replace(destination)
