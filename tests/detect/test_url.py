"""Tests for web address detection."""

import pytest
from anonymizer.core.detect import detector_for
from anonymizer.core.detect.url import find_ocr_urls, find_urls
from anonymizer.core.types import EntityType, Page


def urls(text: str) -> list[str]:
    return [match.text for match in find_urls(text)]


@pytest.mark.parametrize(
    "value",
    [
        "https://www.linkedin.com/in/jan-novak-123",
        "http://example.com",
        "HTTPS://EXAMPLE.COM/A",
        "ftp://files.example.com/cv.pdf",
        "www.example.cz",
        "https://example.com/search?q=a&b=c#top",
        "https://example.com/wiki/A_(b)",
        "https://www.příklad.cz/cesta",
    ],
)
def test_finds_urls_with_a_scheme_or_www(value):
    assert urls(value) == [value]


@pytest.mark.parametrize(
    "value",
    ["github.com/jnovak", "linkedin.com/in/jan-novak/", "cz.linkedin.com/in/jan-novak"],
)
def test_finds_a_host_followed_by_a_path_without_a_site_list(value):
    assert urls(value) == [value]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Profil: https://github.com/jnovak.", "https://github.com/jnovak"),
        ("(viz www.example.cz)", "www.example.cz"),
        ("see github.com/jnovak, or call", "github.com/jnovak"),
        ("[https://example.com/a]", "https://example.com/a"),
        ("Is it https://example.com/?", "https://example.com/"),
    ],
)
def test_sentence_punctuation_is_not_part_of_the_url(text, expected):
    assert urls(text) == [expected]


def test_offsets_point_at_the_url_in_the_text():
    text = "Web: www.example.cz, tel."
    (match,) = find_urls(text)
    assert text[match.start : match.end] == "www.example.cz"


@pytest.mark.parametrize(
    "value",
    [
        "and/or",
        "km/h",
        "1.5/2",
        "example.com",  # a bare domain is indistinguishable from "Node.js"
        "jan.novak@example.com",
        "mailto:jan.novak@example.com",
        "tel:+420603123456",
        "https://",
        "www.",
    ],
)
def test_ignores_non_urls(value):
    assert urls(value) == []


def test_url_wins_over_an_email_inside_it():
    text = "https://example.com/?mail=jan.novak@example.com"
    entities = detector_for(None).detect(Page(0, 595, 842, text=text))
    assert [(entity.type, entity.text) for entity in entities] == [(EntityType.URL, text)]


def ocr_urls(text: str) -> list[str]:
    return [match.text for match in find_ocr_urls(text)]


@pytest.mark.parametrize(
    "variant",
    [
        "https://www. linkedin. com/in/jordan-ellis-demo",
        "https://github. com/tereza-prochazkova-demo",
        "www. example. cz",
        "github. com/jnovak",
        "cz. linkedin. com/in/jan-novak",
        "ftp://files. example. com/cv. pdf",
        "https://www.linkedin.com/in/jan-novak-123",  # no split at all
    ],
)
def test_ocr_finder_joins_a_url_split_after_a_period(variant):
    assert ocr_urls(variant) == [variant]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Profil: https://www. linkedin. com/in/jordan-ellis-demo.",
            "https://www. linkedin. com/in/jordan-ellis-demo",
        ),
        ("(viz github. com/jnovak), tel.", "github. com/jnovak"),
        # The next sentence starts with a capital letter and is not taken in.
        ("Web: https://example.com/a. Další řádek", "https://example.com/a"),
    ],
)
def test_ocr_finder_matches_the_whole_url_in_running_text(text, expected):
    assert ocr_urls(text) == [expected]


@pytest.mark.parametrize(
    "value",
    [
        "Node. js",  # a bare domain stays out, split or not
        "www. Example. cz",  # a capital after the space
        "https://example.com/a  b",
        "tereza. prochazkova@example. com",
        "www.",
    ],
)
def test_ocr_finder_rejects_other_gaps(value):
    assert value not in ocr_urls(value)


def test_strict_finder_stops_at_the_space():
    assert urls("https://www. linkedin. com/in/jan") == ["https://www"]
