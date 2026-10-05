"""The settings file: preferences kept between runs, one JSON object.

It holds preferences only (the models folder, whether export checks for
leaks), never anything about a document: a file name can itself be personal
data. Its path is never logged, as a path can name its user.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import platformdirs

log = logging.getLogger(__name__)

APP_NAME = "anonymizer"


def settings_file() -> Path:
    """Return the per-user file the settings are kept in."""
    return Path(platformdirs.user_config_dir(APP_NAME, appauthor=False)) / "settings.json"


def read_settings() -> dict[str, object]:
    """Return every stored setting; empty when there are none.

    An unreadable or malformed file counts as no settings, so every
    preference falls back to its default.
    """
    try:
        settings = json.loads(settings_file().read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError):
        log.warning("the settings file cannot be read; using the defaults")
        return {}
    return settings if isinstance(settings, dict) else {}


def write_setting(key: str, value: object) -> None:
    """Store one setting, keeping the others.

    The file is written under another name first and then renamed, so a
    crash leaves either the old settings or the new ones.

    Args:
        key: The setting's name.
        value: Its value; must be JSON serializable.

    Raises:
        OSError: If the file cannot be written.
    """
    path = settings_file()
    settings = read_settings()
    settings[key] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(path.name + ".part")
    staging.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    staging.replace(path)
