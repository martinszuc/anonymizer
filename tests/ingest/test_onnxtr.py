"""Tests for the OnnxTR engine adapter.

The unmarked tests give the adapter a stand-in predictor shaped like
OnnxTR's result (page, blocks, lines, words with relative geometry); the
real models run only under `@pytest.mark.model`.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pymupdf
import pytest
from anonymizer.core.ingest import PageImage, load_document
from anonymizer.core.ingest.onnxtr import (
    OnnxtrEngine,
    load_onnxtr_engine,
    missing_onnxtr_files,
)
from anonymizer.core.resources import load_catalog


@dataclass
class _Word:
    value: str
    confidence: float
    geometry: tuple[tuple[float, float], tuple[float, float]]


@dataclass
class _Line:
    words: list[_Word]


@dataclass
class _Block:
    lines: list[_Line]


@dataclass
class _Page:
    blocks: list[_Block]


@dataclass
class _Result:
    pages: list[_Page]


@dataclass
class _Predictor:
    """Returns one fixed page and keeps the arrays it was given."""

    page: _Page
    seen: list[Any] = field(default_factory=list)

    def __call__(self, pages: list[Any]) -> _Result:
        self.seen.extend(pages)
        return _Result([self.page])


IMAGE = PageImage(width=200, height=100, dpi=72, samples=bytes(200 * 100 * 3))


class TestRead:
    def test_relative_boxes_become_pixels_with_blocks_and_lines_numbered(self):
        page = _Page(
            [
                _Block(
                    [
                        _Line(
                            [
                                _Word("Jan", 0.9, ((0.1, 0.1), (0.2, 0.2))),
                                _Word("Novák", 0.8, ((0.25, 0.1), (0.4, 0.2))),
                            ]
                        )
                    ]
                ),
                _Block(
                    [
                        _Line([_Word("Brno", 0.7, ((0.1, 0.5), (0.3, 0.6)))]),
                        _Line([_Word("602", 0.6, ((0.1, 0.7), (0.2, 0.8)))]),
                    ]
                ),
            ]
        )
        words = OnnxtrEngine(_Predictor(page)).read(IMAGE)
        assert [(word.text, word.block, word.line) for word in words] == [
            ("Jan", 0, 0),
            ("Novák", 0, 0),
            ("Brno", 1, 1),
            ("602", 1, 2),
        ]
        assert words[1].box == pytest.approx((50, 10, 80, 20))
        assert words[1].confidence == pytest.approx(0.8)

    def test_a_rotated_word_is_enclosed_by_the_box_around_its_corners(self):
        corners = ((0.30, 0.42), (0.50, 0.40), (0.51, 0.50), (0.31, 0.52))
        page = _Page([_Block([_Line([_Word("Šumavská", 0.9, corners)])])])  # type: ignore[arg-type]
        (word,) = OnnxtrEngine(_Predictor(page)).read(IMAGE)
        assert word.box == pytest.approx((60, 40, 102, 52))

    def test_predictor_receives_the_page_as_height_width_channels(self):
        predictor = _Predictor(_Page([]))
        assert OnnxtrEngine(predictor).read(IMAGE) == []
        (array,) = predictor.seen
        assert array.shape == (100, 200, 3)
        assert array.dtype == np.uint8


class TestLoading:
    def test_missing_models_are_named_in_download_order(self, tmp_path: Path):
        assert missing_onnxtr_files(tmp_path) == [
            "onnxtr-fast-base",
            "onnxtr-parseq-multilingual-v1",
        ]
        with pytest.raises(FileNotFoundError, match=r"scripts/download\.py fetch"):
            load_onnxtr_engine(tmp_path)

    def test_missing_package_is_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        for resource in load_catalog().with_requirements("onnxtr-parseq-multilingual-v1"):
            for item in resource.files:
                stored = resource.directory(tmp_path) / item.path
                stored.parent.mkdir(parents=True, exist_ok=True)
                stored.write_bytes(b"")
        monkeypatch.setitem(sys.modules, "onnxtr.models", None)
        with pytest.raises(ImportError, match="uv sync --group ocr-onnxtr"):
            load_onnxtr_engine(tmp_path)


REPOSITORY = Path(__file__).resolve().parents[2]


@pytest.mark.model
def test_real_engine_reads_czech_offline(tmp_path: Path):
    """Network access is blocked for the whole suite, so this also proves offline loading."""
    pytest.importorskip("onnxtr")
    try:
        engine = load_onnxtr_engine(REPOSITORY)
    except FileNotFoundError:
        pytest.skip("OnnxTR models not fetched")
    # The test PDF font cannot encode Czech; the scan is drawn with an embedded font.
    document = pymupdf.open()
    page = document.new_page()
    writer = pymupdf.TextWriter(page.rect)
    writer.append(
        (72, 100), "Jiří Dvořák, Šumavská 12, Brno", font=pymupdf.Font("helv"), fontsize=14
    )
    writer.write_text(page)
    picture = page.get_pixmap(dpi=200, colorspace=pymupdf.csGRAY)
    scan = pymupdf.open()
    target = scan.new_page()
    target.insert_image(target.rect, pixmap=picture)
    scan.save(tmp_path / "scan.pdf")
    read = load_document(tmp_path / "scan.pdf", ocr=engine).pages[0]
    assert "Jiří Dvořák" in read.text
    assert "Šumavská" in read.text
    assert all(word.bbox.y0 < 110 for word in read.words)


@pytest.mark.model
def test_onnxtr_cannot_download_once_the_engine_is_loaded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """OnnxTR fetches any model it is not handed; the loader must have disabled that."""
    onnxtr_models = pytest.importorskip("onnxtr.models")
    monkeypatch.setenv("ONNXTR_CACHE_DIR", str(tmp_path / "cache"))
    try:
        load_onnxtr_engine(REPOSITORY)
    except FileNotFoundError:
        pytest.skip("OnnxTR models not fetched")
    with pytest.raises(RuntimeError, match="tried to download"):
        onnxtr_models.fast_tiny()
    assert not (tmp_path / "cache").exists()
