"""Minimal PDF builders shared by the ingest tests.

Fixtures are written here rather than committed: a PDF in the repository would
be an opaque binary, and a realistic labelled corpus is a separate project.
Only Latin-1 characters are inserted, because the base-14 Helvetica font cannot
encode `č` or `ř`; NFC handling is covered by a unit test instead.
"""

from pathlib import Path

import pymupdf
import pytest

LINES = ["Jmeno: Jan Novák", "r. c. 900101/0007", "ucet 19-2000145399/0800"]


def write_pdf(path: Path, pages: list[list[str]], rotation: int = 0) -> Path:
    """Write a PDF with one text block per line of each page."""
    document = pymupdf.open()
    for lines in pages:
        page = document.new_page()
        for offset, line in enumerate(lines):
            page.insert_text((72, 100 + offset * 30), line, fontname="helv", fontsize=11)
        if rotation:
            page.set_rotation(rotation)
    document.save(path)
    document.close()
    return path


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
