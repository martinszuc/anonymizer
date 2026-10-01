"""The mixed synthetic sample (`scripts/make_mixed_sample.py`) through the command line.

One file holds a typed page with hidden items, two scans without a text layer
and a typed page beside a scanned stamp, so these tests cover how the text
layer, the non-text surfaces and the refusal to redact unread pages combine.
"""

import importlib.util
from pathlib import Path

import pymupdf
import pytest
from anonymizer.cli.main import main
from anonymizer.core.ingest import load_document

SCRIPT = Path(__file__).parents[1] / "scripts" / "make_mixed_sample.py"
# Values the sample plants in its typed pages, in text and in hidden items.
TYPED_VALUES = [
    "tereza.prochazkova@example.com",
    "+420 777 123 456",
    "910314/0013",
    "CZ65 0800 0000 1920 0014 5399",
    "Kounicova 684/12",
    "608 111 222",
    "https://github.com/tereza-demo",
    "ondrej.dvorak@example.com",
]


def build_sample(destination: Path) -> Path:
    spec = importlib.util.spec_from_file_location("make_mixed_sample", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.write_sample(destination)
    return destination


def metadata_of(path: Path) -> dict[str, str]:
    raw = pymupdf.open(path).metadata or {}
    return {key: str(value or "") for key, value in raw.items()}


def everything_stored(path: Path) -> str:
    """Page text plus the hidden carriers, the way the leak check's layers see a file."""
    document = pymupdf.open(path)
    parts: list[str] = [str(page.get_text()) for page in document]
    parts.extend(metadata_of(path).values())
    parts += [str(item[1]) for item in document.get_toc()]
    parts += [str(link.get("uri") or "") for page in document for link in page.get_links()]
    parts += [
        str(getattr(widget, "field_value", "")) for page in document for widget in page.widgets()
    ]
    parts += [
        document.embfile_get(name).decode("utf-8", "replace") for name in document.embfile_names()
    ]
    return "\n".join(parts)


@pytest.fixture(scope="module")
def sample(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return build_sample(tmp_path_factory.mktemp("sample") / "mixed.pdf")


class TestSample:
    def test_has_the_four_kinds_of_page(self, sample: Path):
        document = pymupdf.open(sample)
        words = [len(page.get_text("words")) for page in document]
        assert words[0] > 0
        assert words[1] == words[2] == 0
        assert 0 < words[3] < 20
        assert all(document[index].get_images() for index in (1, 2, 3))

    def test_plants_values_only_the_typed_pages_expose(self, sample: Path):
        stored = everything_stored(sample)
        assert all(value in stored for value in TYPED_VALUES)


class TestRedaction:
    def test_unread_pages_stop_the_run(
        self, sample: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        output = tmp_path / "out.pdf"
        assert main(["redact", str(sample), "-o", str(output), "--lang", "cs"]) == 1
        assert "page 2, 3 has no text layer" in capsys.readouterr().err
        assert not output.exists()

    def test_allowed_run_removes_every_typed_and_hidden_value(
        self, sample: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        output = tmp_path / "out.pdf"
        arguments = ["redact", str(sample), "-o", str(output), "--lang", "cs"]
        assert main([*arguments, "--allow-pages-without-text"]) == 0
        assert "page 2, 3 has no text layer and is NOT redacted" in capsys.readouterr().err

        stored = everything_stored(output)
        for value in TYPED_VALUES:
            assert value not in stored
        # Names have no rule (NER finds them), but metadata is cleared regardless.
        assert not any(metadata_of(output).get(key) for key in ("title", "author"))

    def test_scans_are_left_as_they_were(self, sample: Path, tmp_path: Path):
        output = tmp_path / "out.pdf"
        arguments = ["redact", str(sample), "-o", str(output), "--lang", "cs"]
        main([*arguments, "--allow-pages-without-text"])
        before, after = pymupdf.open(sample), pymupdf.open(output)
        for index in (1, 2):
            assert len(after[index].get_images()) == len(before[index].get_images())
        assert load_document(output).pages[1].text == ""
