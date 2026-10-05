"""Tests for the settings file shared by the review window and the CLI."""

from anonymizer.core import settings


def test_without_a_file_there_are_no_settings():
    assert settings.read_settings() == {}


def test_a_setting_is_stored_beside_the_others():
    settings.write_setting("models_root", "/models")
    settings.write_setting("leak_check", False)
    assert settings.read_settings() == {"models_root": "/models", "leak_check": False}


def test_writing_a_setting_again_replaces_it():
    settings.write_setting("leak_check", False)
    settings.write_setting("leak_check", True)
    assert settings.read_settings() == {"leak_check": True}
    assert not settings.settings_file().with_name("settings.json.part").exists()


def test_a_broken_file_counts_as_no_settings_and_is_replaced_on_write():
    path = settings.settings_file()
    path.parent.mkdir(parents=True)
    for content in ["{not json", "[]", "3"]:
        path.write_text(content, encoding="utf-8")
        assert settings.read_settings() == {}
    settings.write_setting("leak_check", False)
    assert settings.read_settings() == {"leak_check": False}
