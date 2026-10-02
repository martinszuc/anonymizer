"""Where models are stored: one rule for the CLI, the review window and the benchmark.

A storage root holds `models/<id>/` (and `data/<id>/` for datasets). It is,
in this order:

1. a root given explicitly (`--resource-root`);
2. the folder the reviewer chose in the review window, kept in the settings file;
3. the working directory, when it already has `models/`: a checkout of this
   repository, where `scripts/download.py` stores them;
4. a folder in the user's data directory (`~/Library/Application Support/anonymizer`
   on macOS, `%LOCALAPPDATA%/anonymizer` on Windows, `~/.local/share/anonymizer`
   on Linux).

The settings file holds the chosen folder and nothing else: no document, no
file name. Neither path is ever logged, as a path can name its user.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import platformdirs

log = logging.getLogger(__name__)

APP_NAME = "anonymizer"
_MODELS_ROOT_KEY = "models_root"


def user_resource_root() -> Path:
    """Return the per-user storage root used when nothing else names one."""
    return Path(platformdirs.user_data_dir(APP_NAME, appauthor=False))


def settings_file() -> Path:
    """Return the file the chosen storage root is kept in."""
    return Path(platformdirs.user_config_dir(APP_NAME, appauthor=False)) / "settings.json"


def chosen_resource_root() -> Path | None:
    """Return the storage root chosen in the review window, if one was.

    An unreadable or malformed settings file counts as no choice: models are
    then looked for where they would be without it.
    """
    path = settings_file()
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        log.warning("the settings file cannot be read; using the default models folder")
        return None
    chosen = settings.get(_MODELS_ROOT_KEY) if isinstance(settings, dict) else None
    return Path(chosen) if isinstance(chosen, str) and chosen else None


def choose_resource_root(root: Path) -> None:
    """Keep a storage root for every later run that names none explicitly.

    Args:
        root: The folder to hold `models/`; made absolute before it is kept.

    Raises:
        OSError: If the settings file cannot be written.
    """
    path = settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(path.name + ".part")
    staging.write_text(
        json.dumps({_MODELS_ROOT_KEY: str(root.resolve())}, indent=2) + "\n", encoding="utf-8"
    )
    staging.replace(path)
    log.info("models folder chosen")


def resolve_resource_root(explicit: Path | None = None, *, cwd: Path | None = None) -> Path:
    """Return the storage root to read and write models in (see the module docstring).

    Args:
        explicit: A root the user named for this run, such as `--resource-root`.
        cwd: The working directory; the process's own when omitted.

    Returns:
        The storage root; it need not exist yet.
    """
    if explicit is not None:
        return explicit
    chosen = chosen_resource_root()
    if chosen is not None:
        return chosen
    working = cwd or Path.cwd()
    if (working / "models").is_dir():
        return working
    return user_resource_root()
