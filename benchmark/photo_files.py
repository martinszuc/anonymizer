"""The phone photos on disk: the print manifest, capture times and renaming by them.

Photos arrive from the phone under the camera's own names (`IMG_4821.JPG`),
one folder per condition, taken in the print order of a manifest
(`outputs/rq8-photos/print/manifest.md`: a Markdown table of `#`, document
and pages). The capture time in EXIF (`DateTimeOriginal`, refined by
`SubSecTimeOriginal` when present) gives their order, which is matched to the
manifest's pages to name each photo `<document>[.p<page>].<condition>.jpg`;
`.p<page>` appears only for a document of several pages.

A folder is renamed only when its whole plan holds: exactly one JPEG per page
of the manifest, every one with a capture time, no two with the same. Any
other file (a HEIC, a Live Photo's video) is refused; hidden files (`.DS_Store`)
are ignored. Nothing is ever deleted, and a folder already named this way is
left as it is. Renaming goes through temporary names, so a photo can take a
name another one holds now.
"""

from __future__ import annotations

import datetime
import itertools
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from anonymizer.core.ingest import image_format
from PIL import Image

CONDITIONS = ("flat", "dim", "angle")
"""The capture conditions of `outputs/rq8-photos/PROTOCOL.md`, one folder each."""

PHOTO_SUFFIXES = (".jpg", ".jpeg")
_HEIC_SUFFIXES = (".heic", ".heif")
_EXIF_IFD = 0x8769
_DATE_TIME_ORIGINAL = 0x9003
_SUBSEC_TIME_ORIGINAL = 0x9291
_EXIF_TIME = "%Y:%m:%d %H:%M:%S"
_MANIFEST_ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|\s]+)\s*\|\s*(\d+)\s*\|\s*$")


class PhotoSetError(ValueError):
    """The photos or the manifest do not hold together; nothing was renamed or scored."""


@dataclass(frozen=True)
class ManifestEntry:
    """One printed document: its name and how many pages were photographed."""

    document: str
    pages: int


@dataclass(frozen=True)
class Rename:
    """One photo's planned name.

    Attributes:
        source: The photo as it is named now.
        target: The name it gets.
        captured: Its capture time as EXIF records it, sub-seconds appended.
    """

    source: Path
    target: Path
    captured: str


def read_manifest(path: Path) -> list[ManifestEntry]:
    """Read a print manifest: rows `| # | document | pages |`, numbered from 1 in order.

    Raises:
        PhotoSetError: If it lists no document, numbers rows out of order,
            lists a document twice or one with no pages.
    """
    entries: list[ManifestEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = _MANIFEST_ROW.match(line.strip())
        if row is None:
            continue
        number, document, pages = int(row.group(1)), row.group(2), int(row.group(3))
        if number != len(entries) + 1:
            msg = f"manifest row {number} is out of order (expected {len(entries) + 1})"
            raise PhotoSetError(msg)
        if pages < 1:
            msg = f"manifest lists {document} with no pages"
            raise PhotoSetError(msg)
        if any(entry.document == document for entry in entries):
            msg = f"manifest lists {document} twice"
            raise PhotoSetError(msg)
        entries.append(ManifestEntry(document, pages))
    if not entries:
        msg = "manifest lists no document (expected rows | # | document | pages |)"
        raise PhotoSetError(msg)
    return entries


def photo_name(document: str, page: int, pages: int, condition: str) -> str:
    """Name the photo of one page: `<document>[.p<page>].<condition>.jpg`, pages from 1."""
    part = f".p{page}" if pages > 1 else ""
    return f"{document}{part}.{condition}.jpg"


def expected_names(manifest: list[ManifestEntry], condition: str) -> list[str]:
    """Every photo's name in one condition, in print order."""
    return [
        photo_name(entry.document, page, entry.pages, condition)
        for entry in manifest
        for page in range(1, entry.pages + 1)
    ]


def photo_files(folder: Path) -> list[Path]:
    """Return a folder's photos, refusing what is not a JPEG.

    Raises:
        PhotoSetError: If the folder is missing, or holds a HEIC or any file
            that is not hidden and not a JPEG by name and content.
    """
    if not folder.is_dir():
        msg = f"{folder.name}: no such folder"
        raise PhotoSetError(msg)
    photos: list[Path] = []
    problems: list[str] = []
    for path in sorted(folder.iterdir()):
        if path.name.startswith(".") or path.is_dir():
            continue
        suffix = path.suffix.lower()
        if suffix in _HEIC_SUFFIXES:
            problems.append(
                f"{path.name}: HEIC is not read; set the camera to Most Compatible "
                "(Settings, Camera, Formats) or export the photo as JPEG"
            )
        elif suffix not in PHOTO_SUFFIXES:
            problems.append(f"{path.name}: not a JPEG photo; move it out of the folder")
        elif image_format(path.read_bytes()[:16]) != "JPEG":
            problems.append(f"{path.name}: named .jpg but does not hold a JPEG")
        else:
            photos.append(path)
    if problems:
        raise PhotoSetError("\n".join(f"{folder.name}/{problem}" for problem in problems))
    return photos


def capture_time(path: Path) -> tuple[datetime.datetime, str]:
    """Return a photo's capture time and its text, from EXIF DateTimeOriginal and SubSec.

    Raises:
        PhotoSetError: If the photo records no readable capture time.
    """
    with Image.open(path) as image:
        exif = image.getexif().get_ifd(_EXIF_IFD)
    recorded = exif.get(_DATE_TIME_ORIGINAL)
    if not isinstance(recorded, str):
        msg = f"{path.name}: no capture time (EXIF DateTimeOriginal)"
        raise PhotoSetError(msg)
    try:
        captured = datetime.datetime.strptime(recorded.strip("\x00 "), _EXIF_TIME)
    except ValueError:
        msg = f"{path.name}: unreadable capture time {recorded!r}"
        raise PhotoSetError(msg) from None
    subsec = str(exif.get(_SUBSEC_TIME_ORIGINAL, "")).strip("\x00 ")
    text = recorded.strip("\x00 ")
    if subsec.isdigit():
        captured += datetime.timedelta(seconds=int(subsec) / 10 ** len(subsec))
        text = f"{text}.{subsec}"
    return captured, text


def plan_renames(folder: Path, manifest: list[ManifestEntry], condition: str) -> list[Rename]:
    """Plan one condition's names by capture order; validate before anything moves.

    Args:
        folder: The condition's folder of photos.
        manifest: The print order.
        condition: The condition, which ends every name.

    Returns:
        One rename per photo in print order; a photo already named right maps
        to itself.

    Raises:
        PhotoSetError: If the folder does not hold exactly one JPEG per page,
            a photo lacks a capture time, two share one, or photos already
            carry the manifest's names in an order their capture times contradict.
    """
    photos = photo_files(folder)
    names = expected_names(manifest, condition)
    if len(photos) != len(names):
        msg = (
            f"{folder.name}: {len(photos)} photos, but the manifest has {len(names)} pages; "
            "nothing renamed"
        )
        raise PhotoSetError(msg)
    problems: list[str] = []
    times: list[tuple[datetime.datetime, str, Path]] = []
    for photo in photos:
        try:
            captured, text = capture_time(photo)
        except PhotoSetError as error:
            problems.append(f"{folder.name}/{error}")
            continue
        times.append((captured, text, photo))
    times.sort(key=lambda entry: (entry[0], entry[2].name))
    for (first, _, first_path), (second, _, second_path) in itertools.pairwise(times):
        if first == second:
            problems.append(
                f"{folder.name}: {first_path.name} and {second_path.name} share a capture time"
            )
    if problems:
        raise PhotoSetError("\n".join(problems))
    plan = [
        Rename(photo, folder / name, text)
        for (_, text, photo), name in zip(times, names, strict=True)
    ]
    misplaced = [
        rename.source.name
        for rename in plan
        if rename.source.name in names and rename.source != rename.target
    ]
    if misplaced:
        msg = (
            f"{folder.name}: {', '.join(misplaced)} already carry manifest names that their "
            "capture order contradicts; nothing renamed"
        )
        raise PhotoSetError(msg)
    return plan


def plan_set(
    root: Path, manifest: list[ManifestEntry], conditions: tuple[str, ...] = CONDITIONS
) -> dict[str, list[Rename]]:
    """Plan every condition's names, reporting every folder's problems at once.

    Raises:
        PhotoSetError: If any condition's plan fails (see `plan_renames`).
    """
    plans: dict[str, list[Rename]] = {}
    problems: list[str] = []
    for condition in conditions:
        try:
            plans[condition] = plan_renames(root / condition, manifest, condition)
        except PhotoSetError as error:
            problems.append(str(error))
    if problems:
        raise PhotoSetError("\n".join(problems))
    return plans


def apply_renames(plan: list[Rename]) -> int:
    """Rename photos as planned, through temporary names; return how many moved.

    Raises:
        PhotoSetError: If a target name is held by a file outside the plan.
    """
    moving = [rename for rename in plan if rename.source != rename.target]
    sources = {rename.source for rename in moving}
    for rename in moving:
        if rename.target.exists() and rename.target not in sources:
            msg = f"{rename.target.name} exists and is not one of the photos renamed"
            raise PhotoSetError(msg)
    # A temporary name is listed like any photo, so an interrupted run is
    # planned again from capture times on the next one.
    staged: list[tuple[Path, Path]] = []
    for rename in moving:
        temporary = rename.source.with_name(f"renaming-{uuid.uuid4().hex}.jpg")
        rename.source.rename(temporary)
        staged.append((temporary, rename.target))
    for temporary, target in staged:
        temporary.rename(target)
    return len(moving)


def named_photos(folder: Path, manifest: list[ManifestEntry], condition: str) -> list[Path]:
    """Return one condition's photos in print order, once they are named by the manifest.

    Raises:
        PhotoSetError: If the folder does not hold exactly the manifest's names
            (a photo missing or extra, or the folder not renamed yet).
    """
    present = {photo.name: photo for photo in photo_files(folder)}
    names = expected_names(manifest, condition)
    missing = [name for name in names if name not in present]
    extra = sorted(set(present) - set(names))
    if missing or extra:
        msg = (
            f"{folder.name}: {len(missing)} expected photos missing, {len(extra)} other photos "
            f"(run `benchmark photos rename` first if they keep the camera's names)"
        )
        raise PhotoSetError(msg)
    return [present[name] for name in names]
