"""Move the models a job trained in its scratch into the storage's resource root.

    python scripts/metacentrum/keep_trained.py <scratch root> <storage root>

A job trains with its scratch as the resource root, so the scratch's
`models/trained.json` lists only what that job trained. Each model is copied
next to its final place first and then swapped in and listed in the storage's
`trained.json` under a lock, since jobs running side by side finish at any time.
The lock is a file created exclusively, which works on the storages' NFS.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from anonymizer.core.resources import trained_catalog_path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from experiments.train import register  # noqa: E402

LOCK = ".trained.lock"
# Holding the lock takes a rename and a rewrite of trained.json, so waiting longer
# than this means a job was killed while holding it.
LOCK_TIMEOUT = 600.0


def keep_trained(scratch: Path, store: Path) -> list[str]:
    """Copy every model listed in the scratch root into the storage root and list it there.

    Returns:
        The ids of the models kept.
    """
    listed = json.loads(trained_catalog_path(scratch).read_text(encoding="utf-8"))
    models = store / "models"
    models.mkdir(parents=True, exist_ok=True)
    kept: list[str] = []
    holder = _holder()
    for entry in listed["resource"]:
        target = models / entry["id"]
        # Named after the job, so a resubmitted job storing the same model id
        # cannot copy into this one's staging folder.
        staging = target.with_name(f"{target.name}.{holder}.part")
        earlier = target.with_name(f"{target.name}.{holder}.old")
        shutil.rmtree(staging, ignore_errors=True)
        shutil.copytree(scratch / "models" / entry["id"], staging)
        with _locked(models / LOCK, holder):
            # Moved aside rather than deleted in place: on NFS a file another
            # process still reads survives its deletion as .nfs*, and the folder
            # holding it could not be replaced.
            if target.exists():
                target.rename(earlier)
            staging.rename(target)
            register(store, entry)
        shutil.rmtree(earlier, ignore_errors=True)
        kept.append(entry["id"])
    return kept


def _holder() -> str:
    """Name this process: its PBS job when it runs as one, else its process id."""
    return os.environ.get("PBS_JOBID") or f"pid{os.getpid()}"


@contextmanager
def _locked(path: Path, holder: str, timeout: float = LOCK_TIMEOUT) -> Iterator[None]:
    """Hold a lock file naming its holder; wait while another job holds it."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                held_by = path.read_text(encoding="utf-8").strip() or "an unknown job"
                msg = (
                    f"{path} is still held by {held_by}; delete it if that job "
                    "is no longer running (qstat)"
                )
                raise TimeoutError(msg) from None
            time.sleep(1)
    try:
        os.write(descriptor, holder.encode())
        yield
    finally:
        os.close(descriptor)
        path.unlink()


def main(argv: list[str]) -> int:
    """Run the command line; return the exit code."""
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    store = Path(argv[1])
    for model_id in keep_trained(Path(argv[0]), store):
        print(f"stored {model_id} under {store / 'models'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
