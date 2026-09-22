"""PDF fixtures shared by the ingest tests."""

from pathlib import Path

import pytest

from tests.pdf_builders import write_pdf

LINES = ["Jmeno: Jan Novák", "r. c. 900101/0007", "ucet 19-2000145399/0800"]


@pytest.fixture
def single_page_pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "single.pdf", [LINES])


@pytest.fixture
def two_page_pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "two.pdf", [LINES, ["Strana dve"]])


@pytest.fixture
def rotated_pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "rotated.pdf", [LINES], rotation=90)


@pytest.fixture
def empty_pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "empty.pdf", [[]])
