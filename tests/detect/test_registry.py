"""Tests for language-scoped finder selection."""

import pytest
from anonymizer.core.detect import (
    LANGUAGE_INDEPENDENT_FINDERS,
    STRUCTURED_FINDERS,
    detector_for,
    find_birth_numbers,
    find_czech_phone_numbers,
    find_nanp_phone_numbers,
    finders_for,
)
from anonymizer.core.types import EntityType, Page

CZECH_TEXT = "Jan Novák, r. č. 900101/0007, tel. 777 123 456"
ENGLISH_TEXT = "Casey Smith, (123) 456-7890, casey_smith@email.com"


def page(text: str) -> Page:
    return Page(index=0, width=595, height=842, text=text)


class TestFinderSelection:
    @pytest.mark.parametrize("language", ["cs", "sk", "cs-CZ", "SK", " sk "])
    def test_czech_and_slovak_get_the_domestic_finders(self, language):
        finders = finders_for(language)
        assert find_birth_numbers in finders
        assert find_czech_phone_numbers in finders
        assert find_nanp_phone_numbers not in finders

    @pytest.mark.parametrize("language", ["en", "en-US"])
    def test_english_gets_the_nanp_finder_only(self, language):
        finders = finders_for(language)
        assert find_nanp_phone_numbers in finders
        assert find_birth_numbers not in finders

    @pytest.mark.parametrize("language", ["cs", "en", None, "de"])
    def test_language_independent_finders_always_apply(self, language):
        finders = finders_for(language)
        assert all(finder in finders for finder in LANGUAGE_INDEPENDENT_FINDERS)

    @pytest.mark.parametrize("language", [None, "de", "fr-CA"])
    def test_unset_or_unknown_language_runs_everything(self, language):
        assert finders_for(language) == STRUCTURED_FINDERS


class TestDetectorFor:
    def test_czech_detector_finds_the_birth_number(self):
        found = {entity.type for entity in detector_for("cs").detect(page(CZECH_TEXT))}
        assert EntityType.BIRTH_NUMBER in found

    def test_english_detector_ignores_czech_identifiers(self):
        found = {entity.type for entity in detector_for("en").detect(page(CZECH_TEXT))}
        assert EntityType.BIRTH_NUMBER not in found

    def test_english_detector_finds_the_us_number_and_email(self):
        found = {entity.type for entity in detector_for("en").detect(page(ENGLISH_TEXT))}
        assert found == {EntityType.PHONE, EntityType.EMAIL}

    def test_czech_detector_misses_the_us_number(self):
        found = {entity.type for entity in detector_for("cs").detect(page(ENGLISH_TEXT))}
        assert found == {EntityType.EMAIL}

    def test_detector_name_records_the_language(self):
        assert detector_for("cs-CZ").name == "rules:cs"
        assert detector_for(None).name == "rules:all"
