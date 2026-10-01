"""The scanned benchmark: degradations, ground truth, OCR scores and an oracle run."""

import json
from pathlib import Path

import numpy as np
import pymupdf
import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.types import BBox, EntityType, Page, Word
from PIL import Image, ImageChops, ImageDraw

from benchmark.degrade import LEVELS, Level, level_named
from benchmark.ocr_run import ocr_markdown, run_ocr
from benchmark.ocr_score import box_scores, item_residue, residue_counts, text_errors
from benchmark.render import render
from benchmark.scans import TruthPage, TruthWord, scan_document
from benchmark.spec import DocumentSpec, GoldItem

EMAIL = "jana.dvorakova@example.com"
PHONE = "+420 777 123 456"
SPEC = DocumentSpec(
    name="tiny",
    language="cs",
    kind="letter",
    lines=(f"Pište na {EMAIL}, tel. {PHONE}.", "Děkujeme za spolupráci."),
    gold=(
        GoldItem(EntityType.EMAIL, EMAIL, "page"),
        GoldItem(EntityType.PHONE, PHONE, "page"),
        GoldItem(EntityType.EMAIL, EMAIL, "metadata"),
    ),
)


def _truth(text: str, boxes: list[BBox]) -> TruthPage:
    words = []
    starts = []
    cursor = 0
    for word, box in zip(text.split(), boxes, strict=True):
        start = text.index(word, cursor)
        corners = ((box.x0, box.y0), (box.x1, box.y0), (box.x1, box.y1), (box.x0, box.y1))
        words.append(TruthWord(word, corners, 0, 0))
        starts.append(start)
        cursor = start + len(word)
    return TruthPage(text, tuple(words), tuple(starts), 595, 842)


def _page(text: str, boxes: list[BBox] | None = None) -> Page:
    words = []
    cursor = 0
    for word, box in zip(text.split(), boxes or [], strict=False):
        start = text.index(word, cursor)
        words.append(Word(word, box, start, start + len(word)))
        cursor = start + len(word)
    return Page(index=0, width=595, height=842, text=text, words=words, has_text_layer=False)


class TestLevels:
    def test_names_are_unique_and_found_again(self):
        names = [level.name for level in LEVELS]
        assert len(names) == len(set(names))
        assert all(level_named(name).name == name for name in names)

    def test_unknown_name_is_refused(self):
        with pytest.raises(ValueError, match="unknown level"):
            level_named("blur-99")

    def test_resolution_sets_the_scan_dpi_and_nothing_else_does(self):
        assert level_named("resolution-100").dpi == 100
        assert {level.dpi for level in LEVELS if level.factor != "resolution"} == {300}

    def test_noise_is_the_same_on_every_run(self):
        scan = Image.new("L", (64, 64), 200)
        noisy = level_named("noise-25")
        assert noisy.apply(scan).tobytes() == noisy.apply(scan).tobytes()
        assert noisy.apply(scan).tobytes() != scan.tobytes()

    @pytest.mark.parametrize("name", ["blur-2", "jpeg-10", "skew-3"])
    def test_each_factor_changes_the_picture(self, name: str):
        scan = Image.new("L", (64, 64), 255)
        ImageDraw.Draw(scan).rectangle((20, 20, 40, 28), fill=0)
        assert ImageChops.difference(level_named(name).apply(scan), scan).getbbox() is not None

    def test_clean_leaves_the_picture_alone(self):
        scan = Image.new("L", (8, 8), 128)
        assert level_named("clean").apply(scan) is scan

    @pytest.mark.parametrize("angle", [3, -5])
    def test_skew_moves_a_point_where_the_ink_goes(self, angle: float):
        width, height, x, y = 400, 300, 320.0, 60.0
        scan = Image.new("L", (width, height), 255)
        ImageDraw.Draw(scan).ellipse((x - 3, y - 3, x + 3, y + 3), fill=0)
        rotated = Level("skew", angle).apply(scan)
        rows, columns = np.nonzero(np.asarray(rotated) < 128)
        centre = (float(columns.mean()), float(rows.mean()))
        expected = Level("skew", angle).moved(x, y, width, height)
        assert centre == pytest.approx(expected, abs=1.0)
        assert Level("blur", 1).moved(x, y, width, height) == (x, y)


class TestTextErrors:
    def test_counts_characters_and_diacritics_independently(self):
        # Three letters lose their diacritic: Ř, ř and á; 11 characters in all.
        counts = text_errors(
            [_truth("Řehoř Novák", [BBox(0, 0, 1, 1)] * 2)], [_page("Rehor Novak")]
        )
        assert counts == {
            "characters": 11,
            "character_errors": 3,
            "diacritics": 3,
            "diacritic_errors": 3,
        }

    def test_line_breaks_are_not_errors(self):
        counts = text_errors([_truth("Jan\n\nNovák", [BBox(0, 0, 1, 1)] * 2)], [_page("Jan Novák")])
        assert counts["character_errors"] == 0
        assert counts["diacritic_errors"] == 0

    def test_a_misread_letter_next_to_a_diacritic_leaves_it_correct(self):
        counts = text_errors([_truth("Dvořák", [BBox(0, 0, 1, 1)])], [_page("Dvořak")])
        assert (counts["character_errors"], counts["diacritics"], counts["diacritic_errors"]) == (
            1,
            2,
            1,
        )


class TestBoxScores:
    TRUTH = BBox(100, 100, 160, 112)

    @pytest.mark.parametrize(
        ("read", "boxed", "coverage"),
        [
            (BBox(100, 100, 160, 112), 1, 1.0),
            (BBox(100, 100, 130, 112), 1, 0.5),
            (BBox(100, 100, 120, 112), 0, 1 / 3),
        ],
        ids=["exact", "half", "third"],
    )
    def test_boxed_and_coverage(self, read: BBox, boxed: int, coverage: float):
        scores = box_scores([_truth("Novák", [self.TRUTH])], [_page("Novák", [read])])
        assert scores["words"] == 1
        assert scores["boxed"] == boxed
        assert scores["coverage"] == pytest.approx(coverage)

    def test_a_word_read_as_two_boxes_is_covered_whole(self):
        halves = [BBox(100, 100, 130, 112), BBox(130, 100, 160, 112)]
        scores = box_scores([_truth("Novák", [self.TRUTH])], [_page("No vák", halves)])
        assert scores["coverage"] == pytest.approx(1.0)


class TestScan:
    @pytest.fixture
    def original(self, tmp_path: Path) -> Path:
        return render(SPEC, tmp_path / "tiny.pdf")

    def test_scan_is_a_picture_without_text_and_truth_is_the_original(
        self, original: Path, tmp_path: Path
    ):
        truth = scan_document(original, level_named("clean"), tmp_path / "scan.pdf")
        page = load_document(tmp_path / "scan.pdf").pages[0]
        born_digital = load_document(original).pages[0]
        assert page.words == []
        assert truth[0].text == born_digital.text
        assert [word.text for word in truth[0].words] == [word.text for word in born_digital.words]
        with pymupdf.open(tmp_path / "scan.pdf") as pdf:
            assert len(pdf[0].get_images()) == 1
            assert pdf[0].get_links() == []

    def test_skew_moves_the_truth_with_the_ink(self, original: Path, tmp_path: Path):
        clean = scan_document(original, level_named("clean"), tmp_path / "clean.pdf")
        skewed = scan_document(original, level_named("skew-5"), tmp_path / "skew.pdf")
        first_clean, first_skewed = clean[0].words[0], skewed[0].words[0]
        assert first_clean.corners[0][1] == first_clean.corners[1][1]
        # Counter-clockwise: the right corner of a word rises above its left one.
        assert first_skewed.corners[1][1] < first_skewed.corners[0][1]

    def test_unredacted_scan_leaves_every_item_readable(self, original: Path, tmp_path: Path):
        truth = scan_document(original, level_named("clean"), tmp_path / "scan.pdf")
        items = [item for item in SPEC.gold if item.carrier == "page"]
        shares = item_residue(tmp_path / "scan.pdf", tmp_path / "scan.pdf", truth, items)
        assert shares == [1.0, 1.0]
        assert residue_counts(shares) == {"readable_after": 2, "partly_after": 0}

    def test_item_missing_from_the_truth_counts_as_readable(self, original: Path, tmp_path: Path):
        truth = scan_document(original, level_named("clean"), tmp_path / "scan.pdf")
        absent = [GoldItem(EntityType.PERSON, "Nikdo Nikde", "page")]
        assert item_residue(tmp_path / "scan.pdf", tmp_path / "scan.pdf", truth, absent) == [1.0]


def test_oracle_run_end_to_end(tmp_path: Path):
    levels = (level_named("clean"), level_named("skew-3"))
    results = run_ocr(tmp_path, levels=levels, specs=[SPEC])
    written = json.loads((tmp_path / "ocr-results.json").read_text(encoding="utf-8"))
    assert written["runs"]["oracle"].keys() == {"clean", "skew-3"}
    for level in ("clean", "skew-3"):
        total = results["runs"]["oracle"][level]["totals"]
        assert total["character_error_rate"] == 0
        assert total["boxed"] == 1
        # The metadata copy is not on a scan; both page items are found and removed.
        assert total["items"] == {
            "gold": 2,
            "found": 2,
            "partial": 0,
            "missed": 0,
            "readable_after": 0,
            "partly_after": 0,
        }
        assert (total["safe_documents"], total["leak_check_passed"]) == (1, 1)
    report = ocr_markdown(results)
    assert "## oracle" in report
    assert "| skew-3 | 0.0% |" in report


def test_unknown_engine_is_refused(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown engines"):
        run_ocr(tmp_path, engines=("tesseract",), specs=[SPEC])
