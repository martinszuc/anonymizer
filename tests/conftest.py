"""Fixtures shared by every test."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from anonymizer.core.log import reset_logging
from anonymizer.core.resources import location


@pytest.fixture(autouse=True)
def _undo_logging_setup() -> Iterator[None]:
    """Undo `configure_logging`, which the commands call, so no test inherits its handlers."""
    yield
    reset_logging()


@pytest.fixture(autouse=True)
def user_folders(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the per-user settings and models folders at a temporary directory.

    No test may read the developer's chosen models folder or write a settings
    file into their home directory.
    """
    home = tmp_path_factory.mktemp("user")
    monkeypatch.setattr(location, "settings_file", lambda: home / "config" / "settings.json")
    monkeypatch.setattr(location, "user_resource_root", lambda: home / "data")
    return home
