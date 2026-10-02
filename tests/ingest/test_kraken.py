"""Tests for the kraken engine adapter.

The unmarked tests hand the adapter stand-in line records shaped like
kraken's (`prediction`, `cuts`, `confidences`, `boundary`, `regions`, and a
slice returning the polygon section of a run of characters); the real models
run only under `@pytest.mark.model`.
"""

import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pymupdf
import pytest
from anonymizer.core.ingest import PageImage, load_document
from anonymizer.core.ingest.kraken import (
    KrakenEngine,
    load_kraken_engine,
    missing_kraken_files,
    words_of_lines,
)
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import export_redacted
from anonymizer.core.resources import load_catalog

from tests.pdf_builders import write_scanned_pdf

Point = tuple[float, float]


@dataclass
class _Record:
    """A line whose characters each span `width` pixels from `left`, between `top` and `bottom`."""

    prediction: str
    top: float = 10
    bottom: float = 30
    left: float = 100
    width: float = 10
    regions: list[str] | None = None
    positioned: bool = True

    @property
    def cuts(self) -> list[tuple[Point, ...]]:
        if not self.positioned:
            return []
        return [self._section(index, index + 1) for index in range(len(self.prediction))]

    @property
    def confidences(self) -> list[float]:
        return [0.5 + 0.1 * (index % 4) for index in range(len(self.prediction))]

    @property
    def boundary(self) -> tuple[Point, ...]:
        return self._section(0, len(self.prediction))

    def __getitem__(self, key: slice) -> tuple[str, tuple[Point, ...], float]:
        confidences = self.confidences[key]
        return (
            self.prediction[key],
            self._section(key.start, key.stop),
            sum(confidences) / len(confidences),
        )

    def _section(self, start: int, stop: int) -> tuple[Point, ...]:
        x0 = self.left + start * self.width
        x1 = self.left + stop * self.width
        return ((x0, self.top), (x1, self.top + 1), (x1, self.bottom), (x0, self.bottom - 1))


@dataclass
class _Segmentation:
    lines: list[Any]


@dataclass
class _Segmenter:
    lines: list[Any]
    seen: list[Any] = field(default_factory=list)

    def predict(self, picture: Any, config: Any) -> _Segmentation:
        self.seen.append((picture, config))
        return _Segmentation(self.lines)


@dataclass
class _Recognizer:
    records: list[_Record]
    seen: list[Any] = field(default_factory=list)

    def predict(self, picture: Any, segmentation: Any, config: Any) -> list[_Record]:
        self.seen.append((picture, segmentation, config))
        return self.records


def engine_reading(records: list[_Record], lines: int | None = None) -> KrakenEngine:
    segmenter = _Segmenter(["line"] * (len(records) if lines is None else lines))
    return KrakenEngine(segmenter, _Recognizer(records), "segmentation", "recognition")


IMAGE = PageImage(width=200, height=100, dpi=72, samples=bytes(200 * 100 * 3))


class TestWords:
    def test_a_line_splits_at_whitespace_into_boxes_tiling_it(self):
        words = words_of_lines([_Record("Jan  Novák 602")])
        assert [(word.text, word.block, word.line) for word in words] == [
            ("Jan", 0, 0),
            ("Novák", 0, 0),
            ("602", 0, 0),
        ]
        # Characters span 10 pixels from x 100: "Jan" 100-130, "Novák" 150-200,
        # "602" 210-240. Each box reaches the middle of the spaces beside it,
        # the outer ones the ends of the line, over the line's full height.
        assert [word.box for word in words] == [
            pytest.approx((100, 10, 140, 30)),
            pytest.approx((140, 10, 205, 30)),
            pytest.approx((205, 10, 240, 30)),
        ]
        assert words[1].confidence == pytest.approx((0.6 + 0.7 + 0.8 + 0.5 + 0.6) / 5)

    def test_a_box_is_never_narrowed_to_a_shorter_line_outline(self):
        class _ShortOutline(_Record):
            @property
            def boundary(self) -> tuple[Point, ...]:
                return self._section(1, len(self.prediction) - 1)

        (word,) = words_of_lines([_ShortOutline("Brno")])
        assert word.box == pytest.approx((100, 10, 140, 30))

    def test_lines_are_numbered_and_blocks_follow_their_regions(self):
        records = [
            _Record("Jméno", regions=["r1"]),
            _Record("Jan", regions=["r1"]),
            _Record("Adresa", regions=["r2"]),
            _Record("Brno"),
            _Record("602", regions=None),
        ]
        words = words_of_lines(records)
        assert [(word.text, word.block, word.line) for word in words] == [
            ("Jméno", 0, 0),
            ("Jan", 0, 1),
            ("Adresa", 1, 2),
            ("Brno", 2, 3),
            ("602", 2, 4),
        ]

    def test_a_line_read_as_whitespace_gives_no_words(self):
        assert words_of_lines([_Record("   "), _Record("")]) == []

    def test_a_line_without_character_positions_is_one_word_over_the_line(self):
        (word,) = words_of_lines([_Record("Jan  Novák", positioned=False)])
        assert word.text == "Jan Novák"
        assert word.box == pytest.approx((100, 10, 200, 30))
        assert 0 < word.confidence < 1


class TestRead:
    def test_models_receive_the_page_as_a_picture_with_their_configs(self):
        engine = engine_reading([_Record("Brno")])
        (word,) = engine.read(IMAGE)
        assert word.text == "Brno"
        ((picture, segmentation_config),) = engine.segmenter.seen
        assert picture.size == (200, 100)
        assert picture.mode == "RGB"
        assert segmentation_config == "segmentation"
        ((_picture, segmentation, recognition_config),) = engine.recognizer.seen
        assert segmentation.lines == ["line"]
        assert recognition_config == "recognition"

    def test_a_page_without_lines_is_not_recognized(self):
        engine = engine_reading([_Record("never")], lines=0)
        assert engine.read(IMAGE) == []
        assert engine.recognizer.seen == []

    def test_decomposed_letters_reach_the_page_text_composed(self, tmp_path: Path):
        """The model writes NFD; its cuts count the combining marks as characters."""
        decomposed = unicodedata.normalize("NFD", "Jiří Dvořák")
        assert len(decomposed) > len("Jiří Dvořák")
        scan = write_scanned_pdf(tmp_path / "blank.pdf", [[]])
        page = load_document(scan, ocr=engine_reading([_Record(decomposed)])).pages[0]
        assert page.text == "Jiří Dvořák"
        assert [word.text for word in page.words] == ["Jiří", "Dvořák"]
        first, second = (word.bbox for word in page.words)
        # In NFD "Jiří" is 6 characters (x 100-160 pixels) and "Dvořák" starts
        # at the 8th (x 170): the boxes divide in the space between them, which
        # cuts counted in composed letters would misplace.
        points = 72 / 300
        assert 160 * points < first.x1 < 170 * points
        assert 160 * points < second.x0 < 170 * points


class TestLoading:
    def test_missing_models_are_named_in_download_order(self, tmp_path: Path):
        assert missing_kraken_files(tmp_path) == ["kraken-blla", "kraken-ppocr-v6-medium"]
        with pytest.raises(FileNotFoundError, match=r"scripts/download\.py fetch"):
            load_kraken_engine(tmp_path)

    def test_missing_package_is_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        for resource in load_catalog().with_requirements("kraken-ppocr-v6-medium"):
            for item in resource.files:
                stored = resource.directory(tmp_path) / item.path
                stored.parent.mkdir(parents=True, exist_ok=True)
                stored.write_bytes(b"")
        monkeypatch.setitem(sys.modules, "kraken", None)
        with pytest.raises(ImportError, match="uv sync --group ocr-kraken"):
            load_kraken_engine(tmp_path)


REPOSITORY = Path(__file__).resolve().parents[2]
BIRTH_NUMBER = "900101/0007"


def _real_engine() -> KrakenEngine:
    pytest.importorskip("kraken")
    try:
        return load_kraken_engine(REPOSITORY)
    except FileNotFoundError:
        pytest.skip("kraken models not fetched")


def _printed_scan(path: Path, lines: list[str]) -> Path:
    """A picture-only page of Czech text; the test PDF font cannot encode Czech."""
    document = pymupdf.open()
    page = document.new_page()
    writer = pymupdf.TextWriter(page.rect)
    for number, line in enumerate(lines):
        writer.append((72, 100 + 30 * number), line, font=pymupdf.Font("helv"), fontsize=14)
    writer.write_text(page)
    picture = page.get_pixmap(dpi=200, colorspace=pymupdf.csGRAY)
    scan = pymupdf.open()
    target = scan.new_page()
    target.insert_image(target.rect, pixmap=picture)
    scan.save(path)
    return path


@pytest.mark.model
def test_real_engine_reads_czech_offline(tmp_path: Path):
    """Network access is blocked for the whole suite, so this also proves offline loading."""
    engine = _real_engine()
    scan = _printed_scan(tmp_path / "scan.pdf", ["Jiří Dvořák, Šumavská 12, Brno"])
    read = load_document(scan, ocr=engine).pages[0]
    assert "Dvořák" in read.text
    assert "Šumavská" in read.text
    assert read.text == unicodedata.normalize("NFC", read.text)
    assert all(word.bbox.y0 < 110 for word in read.words)


@pytest.mark.model
def test_real_engine_redacts_a_scan_and_its_leak_check_passes(tmp_path: Path):
    engine = _real_engine()
    scan = _printed_scan(tmp_path / "scan.pdf", [f"Rodné číslo: {BIRTH_NUMBER}", "Brno"])
    document = load_document(scan, language="cs", ocr=engine)
    run_detection(document, build_detector("cs"))
    assert [entity.text for entity in document.entities] == [BIRTH_NUMBER]
    output = tmp_path / "out.pdf"
    assert export_redacted(scan, document, output, ocr=engine) == []
    reread = load_document(output, ocr=engine).pages[0]
    assert "0007" not in reread.text
    assert "Brno" in reread.text
