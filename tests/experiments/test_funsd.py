"""FUNSD scoring on a synthetic form in FUNSD's format; every name and number is invented."""

import io
import json
from pathlib import Path
from typing import Any

import pymupdf
import pytest
from anonymizer.core.ingest import document_from_bytes
from anonymizer.core.types import BBox, EntityType, Page, Word
from PIL import Image

from experiments import funsd as funsd_module
from experiments.__main__ import main
from experiments.funsd import (
    field_type,
    in_reading_order,
    parse_form,
    read_forms,
    reading_order,
    run_funsd,
    truth_page,
    write_results,
)
from tests.ocr_stand_in import InkReadingEngine, ScriptedWord
from tests.pdf_builders import write_lines

LINES = ["Name: Jan Novák", "Fax No.: (212) 555-0147", "Brand Name: Tatra", "Date: 1.2.2026"]
# The line's first words are the question, the rest its answer.
QUESTION_WORDS = (1, 2, 2, 1)
SCAN_DPI = 150
# The images record no resolution, so `as_pdf` lays them out at 300 DPI.
WRAPPED_POINTS_PER_PIXEL = 72 / 300


def _entity(identifier: int, label: str, words: list[tuple[str, list[float]]]) -> dict[str, Any]:
    return {
        "id": identifier,
        "label": label,
        "text": " ".join(text for text, _ in words),
        "box": words[0][1],
        "words": [{"text": text, "box": box} for text, box in words],
        "linking": [],
    }


def _form(folder: Path, stem: str = "0001") -> list[tuple[str, BBox]]:
    """Write a scanned form and its annotation; return its words with boxes in pixels."""
    document = pymupdf.open()
    page = document.new_page()
    write_lines(page, LINES)
    picture = page.get_pixmap(dpi=SCAN_DPI, colorspace=pymupdf.csGRAY)
    read = document_from_bytes(document.tobytes()).pages[0]
    document.close()
    scale = SCAN_DPI / 72
    pixels = [
        (
            word.text,
            BBox(
                word.bbox.x0 * scale,
                word.bbox.y0 * scale,
                word.bbox.x1 * scale,
                word.bbox.y1 * scale,
            ),
        )
        for word in read.words
    ]
    tops = sorted({round(word.bbox.y0) for word in read.words})
    line_of = [tops.index(round(word.bbox.y0)) for word in read.words]
    entities: list[dict[str, Any]] = []
    for line, question_words in enumerate(QUESTION_WORDS):
        on_line = [
            (text, [box.x0, box.y0, box.x1, box.y1])
            for (text, box), word_line in zip(pixels, line_of, strict=True)
            if word_line == line
        ]
        question = _entity(2 * line, "question", on_line[:question_words])
        answer = _entity(2 * line + 1, "answer", on_line[question_words:])
        question["linking"] = answer["linking"] = [[question["id"], answer["id"]]]
        entities += [question, answer]
    entities.append(_entity(99, "other", [(" ", [0, 0, 1, 1])]))
    (folder / "annotations").mkdir(parents=True, exist_ok=True)
    (folder / "images").mkdir(parents=True, exist_ok=True)
    (folder / "annotations" / f"{stem}.json").write_text(
        json.dumps({"form": entities}, ensure_ascii=False), encoding="utf-8"
    )
    encoded = io.BytesIO()
    Image.frombytes("L", (picture.width, picture.height), picture.samples).save(
        encoded, format="PNG"
    )
    (folder / "images" / f"{stem}.png").write_bytes(encoded.getvalue())
    return pixels


@pytest.fixture
def funsd_root(tmp_path: Path) -> tuple[Path, list[tuple[str, BBox]]]:
    root = tmp_path / "resources"
    words = _form(root / "data/funsd/dataset/dataset/testing_data")
    return root, words


def _engine(words: list[tuple[str, BBox]]) -> InkReadingEngine:
    """An engine reading the form's words where ink is left, as the wrapped page places them."""
    scale = WRAPPED_POINTS_PER_PIXEL
    return InkReadingEngine(
        [
            [
                ScriptedWord(
                    text, BBox(box.x0 * scale, box.y0 * scale, box.x1 * scale, box.y1 * scale)
                )
                for text, box in words
            ]
        ]
    )


class TestParse:
    def test_answers_to_person_and_phone_questions_are_items(
        self, funsd_root: tuple[Path, list[tuple[str, BBox]]]
    ):
        root, _ = funsd_root
        (form,) = read_forms(root / "data/funsd", "test")
        items = [
            (kind, " ".join(form.words[index].text for index in words))
            for kind, words in form.items
        ]
        # A brand name is a thing, and a date is not a date of birth.
        assert items == [
            (EntityType.PERSON, "Jan Novák"),
            (EntityType.PHONE, "(212) 555-0147"),
        ]
        assert all(word.text.strip() for word in form.words)

    @pytest.mark.parametrize(
        ("question", "kind"),
        [
            ("NAME:", EntityType.PERSON),
            ("To:", EntityType.PERSON),
            ("Submitted by", EntityType.PERSON),
            ("Telephone No.", EntityType.PHONE),
            ("FAX:", EntityType.PHONE),
            ("Mailing address", EntityType.ADDRESS),
            ("Product name", None),
            ("Company:", None),
            ("Date", None),
            ("Total", None),
        ],
    )
    def test_field_types(self, question: str, kind: EntityType | None):
        assert field_type([question]) is kind

    def test_an_answer_without_words_is_no_item(self):
        question = _entity(1, "question", [("Name:", [0, 0, 10, 10])])
        answer = _entity(2, "answer", [(" ", [20, 0, 30, 10])])
        question["linking"] = answer["linking"] = [[1, 2]]
        assert parse_form({"form": [question, answer]}, Path("x.png")).items == ()

    def test_unknown_split_and_missing_files(self, tmp_path: Path):
        with pytest.raises(ValueError, match="no split"):
            read_forms(tmp_path, "dev")
        with pytest.raises(FileNotFoundError):
            read_forms(tmp_path, "test")


class TestReadingOrder:
    BOXES = (
        BBox(300, 12, 340, 22),  # right column, first line, a little lower
        BBox(10, 10, 50, 20),
        BBox(10, 40, 50, 50),
    )

    def test_lines_from_the_top_each_left_to_right(self):
        assert reading_order(self.BOXES) == [[1, 0], [2]]

    def test_a_read_page_is_rewritten_in_that_order(self):
        texts = ["right", "left", "below"]
        page = Page(
            index=0,
            width=400,
            height=100,
            text="right left below",
            words=[
                Word(text, box, start, start + len(text))
                for text, box, start in zip(texts, self.BOXES, (0, 6, 11), strict=True)
            ],
        )
        assert in_reading_order(page).text == "left right\nbelow"

    def test_truth_offsets_point_at_their_words(
        self, funsd_root: tuple[Path, list[tuple[str, BBox]]]
    ):
        root, pixels = funsd_root
        (form,) = read_forms(root / "data/funsd", "test")
        truth = truth_page(form, 0.5, 300, 400)
        assert truth.text.splitlines()[0] == "Name: Jan Novák"
        for word, start in zip(truth.words, truth.starts, strict=True):
            assert truth.text[start : start + len(word.text)] == word.text
        first = pixels[0][1]
        assert truth.words[0].bbox == BBox(first.x0 / 2, first.y0 / 2, first.x1 / 2, first.y1 / 2)


def test_run_scores_the_form_and_writes_counts_only(
    funsd_root: tuple[Path, list[tuple[str, BBox]]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    root, words = funsd_root
    monkeypatch.setattr(funsd_module, "load_ocr_engine", lambda name, _root: _engine(words))
    results = run_funsd(
        tmp_path / "work", engines=("stand-in",), system="rules", resource_root=root
    )
    assert results["forms"] == 1
    assert results["items"] == {"person": 1, "phone": 1}
    document = results["runs"]["stand-in"]["test"]["documents"]["funsd/test/0000"]
    assert document["text"]["character_errors"] == 0
    # The rules find the phone, not the name; the name stays readable after redaction.
    assert document["items"] == {
        "gold": 2,
        "found": 1,
        "partial": 0,
        "missed": 1,
        "readable_after": 1,
        "partly_after": 0,
    }
    assert document["leak_check_passed"]
    assert "false_positives" not in document

    path = write_results(results, tmp_path / "results")
    written = path.read_text(encoding="utf-8") + path.with_suffix(".md").read_text(encoding="utf-8")
    for text in ("Novák", "555-0147", "Tatra"):
        assert text not in written
    assert "derived items: person 1, phone 1" in written


def test_command_line(
    funsd_root: tuple[Path, list[tuple[str, BBox]]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    root, words = funsd_root
    monkeypatch.setattr(funsd_module, "load_ocr_engine", lambda name, _root: _engine(words))
    arguments = ["funsd", "--work", str(tmp_path / "work"), "--engines", "stand-in"]
    arguments += ["--system", "rules", "--limit", "1", "--out", str(tmp_path / "results")]
    assert main([*arguments, "--resource-root", str(root)]) == 0
    assert "# FUNSD scans" in capsys.readouterr().out
    assert (tmp_path / "results" / "funsd-test.json").exists()
