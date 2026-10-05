"""The scanned benchmark: degradations, ground truth, OCR scores and an oracle run."""

import json
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pymupdf
import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.types import BBox, Document, Entity, EntityType, Page, Word
from PIL import Image, ImageChops, ImageDraw

from benchmark.degrade import LEVELS, Level, level_named
from benchmark.ocr_run import ocr_markdown, run_ocr
from benchmark.ocr_score import (
    box_scores,
    item_locations,
    item_residue,
    residue_counts,
    text_errors,
)
from benchmark.render import render
from benchmark.scans import TruthPage, TruthWord, covers, scan_document
from benchmark.score import Outcome, false_positives, score_detection
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
    @pytest.fixture
    def scanned(self, tmp_path: Path) -> tuple[Path, TruthPage]:
        original = render(SPEC, tmp_path / "tiny.pdf")
        (truth,) = scan_document(original, level_named("clean"), tmp_path / "scan.pdf")
        return tmp_path / "scan.pdf", truth

    def _read(self, truth: TruthPage, shrink: float = 0.0) -> Page:
        """OCR output with the ground-truth words, each box cut from the right by a share."""
        words = []
        for word, start in zip(truth.words, truth.starts, strict=True):
            box = word.bbox
            cut = BBox(box.x0, box.y0, box.x1 - shrink * box.width, box.y1)
            words.append(Word(word.text, cut, start, start + len(word.text)))
        return Page(0, 595, 842, truth.text, words, has_text_layer=False, raster_dpi=300)

    def test_boxes_as_large_as_the_words_cover_all_ink(self, scanned: tuple[Path, TruthPage]):
        scan, truth = scanned
        scores = box_scores(scan, [truth], [self._read(truth)])
        assert scores["words"] == scores["boxed"] == len(truth.words)
        assert scores["ink_covered"] == scores["ink"] > 0
        assert scores["partly_outside"] == 0

    def test_narrow_boxes_leave_ink_outside(self, scanned: tuple[Path, TruthPage]):
        scan, truth = scanned
        scores = box_scores(scan, [truth], [self._read(truth, shrink=0.4)])
        assert scores["boxed"] == len(truth.words)
        assert scores["ink_covered"] < scores["ink"]
        assert scores["partly_outside"] == len(truth.words)

    def test_no_boxes_cover_nothing(self, scanned: tuple[Path, TruthPage]):
        scan, truth = scanned
        empty = Page(0, 595, 842, "", [], has_text_layer=False, raster_dpi=300)
        scores = box_scores(scan, [truth], [empty])
        assert (scores["boxed"], scores["ink_covered"]) == (0, 0)


LINE = f"Pište na {EMAIL}, tel. {PHONE}."
ON_PAGE = DocumentSpec(
    name="tiny",
    language="cs",
    kind="letter",
    lines=(LINE,),
    gold=(GoldItem(EntityType.EMAIL, EMAIL, "page"), GoldItem(EntityType.PHONE, PHONE, "page")),
)


def _printed(fragment: str) -> BBox:
    """Where a fragment of `LINE` is printed: one line, every character 5 points wide."""
    offset = LINE.index(fragment)
    return BBox(50 + 5 * offset, 100, 50 + 5 * (offset + len(fragment)), 112)


def _ocr(text: str, printed: Sequence[str] | None = None) -> Page:
    """A page OCR read as `text`, each word at the fragment of `LINE` it was read from."""
    fragments = printed or text.split()
    page = _page(text, [_printed(fragment) for fragment in fragments])
    return Page(0, 595, 842, text, page.words, has_text_layer=False, raster_dpi=300)


def _over(page: Page, text: str, kind: EntityType) -> Entity:
    start = page.text.index(text)
    return Entity(type=kind, page_index=0, start=start, end=start + len(text), text=text)


def _located(page: Page, index: int, truth: TruthPage) -> str | None:
    """The OCR text an item was located at, None if nowhere."""
    location = item_locations([truth], [page], ON_PAGE.gold)[index]
    return None if location is None else page.text[location[1] : location[2]]


class TestItemLocations:
    TRUTH = _truth(LINE, [_printed(word) for word in LINE.split()])
    SPLIT = "Pište na jana. dvorakova@example. com, tel. +420 777 123 456."

    def _scores(self, page: Page, entities: list[Entity]) -> list[tuple[Outcome, bool]]:
        locations = item_locations([self.TRUTH], [page], ON_PAGE.gold)
        return score_detection(ON_PAGE, Document(pages=[page], entities=entities), locations)

    def test_an_address_read_split_at_its_periods_is_located_whole(self):
        assert _located(_ocr(self.SPLIT), 0, self.TRUTH) == "jana. dvorakova@example. com"

    def test_an_entity_covering_the_split_address_finds_it(self):
        page = _ocr(self.SPLIT)
        email = _over(page, "jana. dvorakova@example. com", EntityType.EMAIL)
        document = Document(pages=[page], entities=[email])
        assert self._scores(page, [email])[0] == ("found", True)
        # Control: located by its exact words, the split address is missed.
        assert score_detection(ON_PAGE, document)[0] == ("missed", False)

    def test_an_entity_on_part_of_the_split_address_is_partial(self):
        page = _ocr(self.SPLIT)
        part = _over(page, "dvorakova@example. com", EntityType.EMAIL)
        assert self._scores(page, [part])[0] == ("partial", True)

    def test_a_misread_item_is_located_by_where_it_is_printed(self):
        text = "Pište na jana.dvorakova@exarnple.com, tel. +420 777 123 456."
        page = _ocr(text, LINE.split())
        misread = _over(page, "jana.dvorakova@exarnple.com", EntityType.EMAIL)
        assert self._scores(page, [misread])[0] == ("found", True)

    def test_a_label_read_glued_to_a_value_stays_outside_it(self):
        text = "Pište na jana.dvorakova@example.com, tel.+420 777 123 456."
        page = _ocr(text, [*LINE.split()[:3], "tel. +420", "777", "123", "456."])
        assert _located(page, 1, self.TRUTH) == PHONE
        assert self._scores(page, [_over(page, PHONE, EntityType.PHONE)])[1] == ("found", True)

    def test_an_item_ocr_read_nothing_of_is_missed(self):
        page = _ocr("Pište na tel. +420 777 123 456.")
        assert _located(page, 0, self.TRUTH) is None
        assert self._scores(page, [])[0] == ("missed", False)

    def test_words_of_the_next_line_are_not_taken_in(self):
        page = _ocr(self.SPLIT)
        # A grown box of the next line reaches into the item's line; its centre does not.
        below = Word("Novák", BBox(100, 106, 140, 125), len(page.text) + 1, len(page.text) + 6)
        page = Page(0, 595, 842, f"{page.text}\nNovák", [*page.words, below], False, raster_dpi=300)
        assert _located(page, 0, self.TRUTH) == "jana. dvorakova@example. com"

    def test_false_alarms_leave_out_an_item_read_split(self):
        page = _ocr(self.SPLIT)
        entities = [
            _over(page, "jana. dvorakova@example. com", EntityType.EMAIL),
            _over(page, "Pište", EntityType.PERSON),
        ]
        document = Document(pages=[page], entities=entities)
        locations = item_locations([self.TRUTH], [page], ON_PAGE.gold)
        assert false_positives(ON_PAGE, document, locations) == ["Pište"]
        # Control: by exact words, the split address counts as a false alarm too.
        assert len(false_positives(ON_PAGE, document)) == 2

    def test_a_skewed_box_covers_its_middle_but_not_the_corners_of_its_frame(self):
        # A 40 x 10 box turned by 30 degrees about its top left corner.
        corners = ((0.0, 0.0), (34.64, 20.0), (29.64, 28.66), (-5.0, 8.66))
        assert covers(corners, 14.8, 14.3)
        assert not covers(corners, 30.0, 2.0)
        assert not covers(corners, -4.0, 27.0)


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
        assert total["ink_under_boxes"] == 1
        assert total["words_partly_outside"] == 0
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
        assert total["false_positives"] == 0
    report = ocr_markdown(results)
    assert "## oracle" in report
    assert "| found | false alarms |" in report
    assert "| skew-3 | 0.0% |" in report


def test_unknown_engine_is_refused(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown engines"):
        run_ocr(tmp_path, engines=("tesseract",), specs=[SPEC])
