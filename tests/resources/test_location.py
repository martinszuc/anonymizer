"""Tests for choosing where models are stored."""

from pathlib import Path

import pytest
from anonymizer.core.resources import location
from anonymizer.core.resources.location import (
    choose_resource_root,
    chosen_resource_root,
    resolve_resource_root,
)


def test_without_anything_models_go_to_the_user_folder(tmp_path: Path, user_folders: Path):
    assert resolve_resource_root(cwd=tmp_path) == user_folders / "data"


def test_a_checkout_with_models_uses_its_own(tmp_path: Path):
    (tmp_path / "models").mkdir()
    assert resolve_resource_root(cwd=tmp_path) == tmp_path


def test_a_chosen_folder_wins_over_the_working_directory(tmp_path: Path):
    (tmp_path / "models").mkdir()
    chosen = tmp_path / "elsewhere"
    choose_resource_root(chosen)
    assert chosen_resource_root() == chosen.resolve()
    assert resolve_resource_root(cwd=tmp_path) == chosen.resolve()


def test_an_explicit_root_wins_over_everything(tmp_path: Path):
    choose_resource_root(tmp_path / "elsewhere")
    assert resolve_resource_root(tmp_path / "given", cwd=tmp_path) == tmp_path / "given"


def test_choosing_again_replaces_the_choice_and_keeps_nothing_else(tmp_path: Path):
    choose_resource_root(tmp_path / "first")
    choose_resource_root(tmp_path / "second")
    assert chosen_resource_root() == (tmp_path / "second").resolve()
    assert location.settings_file().read_text(encoding="utf-8").count("models_root") == 1
    assert not location.settings_file().with_name("settings.json.part").exists()


def test_a_relative_folder_is_kept_absolute(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    choose_resource_root(Path("relative"))
    assert chosen_resource_root() == tmp_path.resolve() / "relative"


def test_a_broken_settings_file_counts_as_no_choice(tmp_path: Path, user_folders: Path):
    settings = location.settings_file()
    settings.parent.mkdir(parents=True)
    for content in ["{not json", "[]", '{"models_root": 3}', '{"models_root": ""}']:
        settings.write_text(content, encoding="utf-8")
        assert chosen_resource_root() is None
        assert resolve_resource_root(cwd=tmp_path) == user_folders / "data"


def test_the_real_folders_are_per_user_and_named_for_the_app(monkeypatch: pytest.MonkeyPatch):
    # The autouse fixture replaced them; look at the functions it saved.
    monkeypatch.undo()
    assert location.settings_file().name == "settings.json"
    assert location.APP_NAME in location.settings_file().parts
    assert location.APP_NAME in location.user_resource_root().parts
