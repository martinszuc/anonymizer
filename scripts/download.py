"""Download models and datasets from the resource catalog.

Nothing is fetched without naming a resource and confirming the prompt:

    uv run python scripts/download.py list
    uv run python scripts/download.py show gliner-multi-v2.1
    uv run python scripts/download.py fetch gliner-multi-v2.1
    uv run python scripts/download.py verify

`fetch` also fetches what the resource requires, shows the licence and size of
each first, and refuses any file whose checksum differs from the catalog.
Files are stored under `models/<id>/` and `data/<id>/` below `--root`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from anonymizer.core.resources import (
    ChecksumError,
    PinRequiredError,
    Resource,
    ResourceFile,
    fetch_resource,
    load_catalog,
    resource_status,
    verify_resource,
)

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(description="Download pinned models and datasets.")
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="storage root holding models/ and data/ (default: the repository)",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list every resource and whether it is stored")
    show = commands.add_parser("show", help="describe one resource")
    show.add_argument("id")
    fetch = commands.add_parser("fetch", help="download one resource and its requirements")
    fetch.add_argument("id")
    fetch.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    fetch.add_argument(
        "--pin",
        action="store_true",
        help="accept files the catalog knows only by the source's digest; print their SHA-256",
    )
    verify = commands.add_parser("verify", help="re-hash stored files against the catalog")
    verify.add_argument("id", nargs="?")
    args = parser.parse_args(argv)

    catalog = load_catalog()
    try:
        if args.command == "list":
            return _list(list(catalog.resources.values()), args.root)
        if args.command == "show":
            _describe(catalog[args.id])
            return 0
        if args.command == "fetch":
            return _fetch(catalog.with_requirements(args.id), args.root, args.yes, args.pin)
        targets = [catalog[args.id]] if args.id else list(catalog.resources.values())
        return _verify(targets, args.root)
    except KeyError as error:
        print(f"error: {error.args[0]}", file=sys.stderr)
        return 2


def _list(resources: list[Resource], root: Path) -> int:
    rows = [
        (
            resource.id,
            resource.kind,
            _human_size(resource.size),
            resource.licence,
            ",".join(resource.languages),
            resource_status(resource, root),
        )
        for resource in resources
    ]
    header = ("id", "kind", "size", "licence", "languages", "stored")
    widths = [max(len(row[column]) for row in [header, *rows]) for column in range(len(header))]
    for row in [header, *rows]:
        print("  ".join(cell.ljust(width) for cell, width in zip(row, widths, strict=True)))
    return 0


def _describe(resource: Resource) -> None:
    print(f"{resource.id}: {resource.name}")
    print(f"  kind       {resource.kind} ({', '.join(resource.uses)})")
    print(f"  source     {resource.source}")
    print(f"  version    {resource.version}")
    print(f"  licence    {resource.licence}")
    print(f"  languages  {', '.join(resource.languages)}")
    print(f"  size       {_human_size(resource.size)}")
    if resource.requires:
        print(f"  requires   {', '.join(resource.requires)}")
    if resource.real_personal_data:
        print("  contains   names of real people: local evaluation only, never a fixture")
    for item in resource.files:
        check = f"sha256 {item.sha256}" if item.sha256 else _source_digest(item)
        print(f"  file       {item.path} ({_human_size(item.size)}, {check})")
    if resource.notes:
        print(f"  notes      {resource.notes}")


def _fetch(resources: list[Resource], root: Path, assume_yes: bool, pin: bool) -> int:
    for resource in resources:
        _describe(resource)
        print(f"  target     {resource.directory(root)}")
    unpinned = [
        resource.id for resource in resources if any(item.sha256 is None for item in resource.files)
    ]
    if unpinned and not pin:
        print(
            f"error: {', '.join(unpinned)} has files without a recorded SHA-256; "
            "rerun with --pin to verify them against the source's digest",
            file=sys.stderr,
        )
        return 1
    total = sum(resource.size for resource in resources)
    if not assume_yes and input(f"Download up to {_human_size(total)}? [y/N] ").lower() != "y":
        print("Nothing downloaded.")
        return 1
    for resource in resources:
        try:
            result = fetch_resource(resource, root, pin=pin, progress=_print_progress)
        except (PinRequiredError, ChecksumError, OSError) as error:
            print(f"\nerror: {error}", file=sys.stderr)
            return 1
        print(
            f"\n{resource.id}: {len(result.downloaded)} downloaded, "
            f"{len(result.present)} already present, all verified"
        )
        for path, sha256 in result.pinned.items():
            print(f'  record in catalog.toml for {path}: sha256 = "{sha256}"')
    return 0


def _verify(resources: list[Resource], root: Path) -> int:
    failed = False
    for resource in resources:
        if resource_status(resource, root) == "absent":
            continue
        problems = verify_resource(resource, root)
        print(f"{resource.id}: {'ok' if not problems else 'FAILED'}")
        for path, problem in problems.items():
            print(f"  {path}: {problem}")
        failed = failed or bool(problems)
    return 1 if failed else 0


def _print_progress(item: ResourceFile, received: int) -> None:
    percent = received * 100 // item.size
    print(f"\r  {item.path}: {percent:3d}% of {_human_size(item.size)}", end="", flush=True)


def _source_digest(item: ResourceFile) -> str:
    assert item.source_digest is not None
    algorithm, value = item.source_digest
    return f"{algorithm} {value} (source digest; SHA-256 not yet recorded)"


def _human_size(size: int) -> str:
    scaled = float(size)
    for unit in ("B", "KB", "MB"):
        if scaled < 1000:
            return f"{scaled:.0f} {unit}"
        scaled /= 1000
    return f"{scaled:.2f} GB"


if __name__ == "__main__":
    sys.exit(main())
