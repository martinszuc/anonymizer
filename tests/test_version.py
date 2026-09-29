"""The release version is written in three places; they must agree."""

from pathlib import Path

import anonymizer.cli
import anonymizer.core

REPOSITORY = Path(__file__).resolve().parents[1]


def test_packages_and_release_manifest_share_one_version():
    released = (REPOSITORY / "version.txt").read_text(encoding="utf-8").strip()
    assert anonymizer.core.__version__ == released
    assert anonymizer.cli.__version__ == released
