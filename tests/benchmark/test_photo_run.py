"""The phone-photo benchmark end to end on simulated photos (`benchmark.photo_run`).

Photos are made in code from invented documents (`tests.photo_builders`) and
read by a stand-in engine, so no model is needed. A stand-in name model finds
the one invented name, so person scores have something to count.
"""

import json
import re
from pathlib import Path

import pytest
from anonymizer.core.pipeline import build_detector
from anonymizer.core.types import Entity, EntityType, Page

from benchmark import photo_run
from benchmark.__main__ import main
from benchmark.photo_files import expected_names, read_manifest
from benchmark.photo_run import photos_markdown, score_photos
from benchmark.render import render
from benchmark.spec import load_documents
from tests.photo_builders import PhotoReader, SimulatedPhoto, simulated_photo

PERSON = "Jiří Čermák"
LETTER = f"""language = "cs"
kind = "letter"
lines = [
    "Vážený pane,",
    "smlouvu podepsal [[person:{PERSON}]], e-mail [[email:jiri.cermak@example.com]].",
    "Telefon pro dotazy: [[phone:+420 777 123 456]].",
]
"""
NOTICE = """language = "cs"
kind = "notice"
lines = ["Oznámení o uzavírce. {{filler:60}}", "{{filler:900}}", "Konec oznámení."]
"""
MANIFEST = """| # | document | pages |
|---|---|---|
| 1 | tst-letter | 1 |
| 2 | tst-notice | 2 |
"""
CONDITIONS = ("flat", "angle")
NAME_PATTERN = re.compile(r"Ji[rř][ií]\s+[CČ]erm[aá]k")


class NameFinder:
    """Finds the one invented name, with or without its diacritics."""

    name = "stand-in names"

    def detect(self, page: Page) -> list[Entity]:
        return [
            Entity(
                EntityType.PERSON,
                page.index,
                match.start(),
                match.end(),
                match.group(),
                bboxes=page.bboxes_for_span(match.start(), match.end()),
            )
            for match in NAME_PATTERN.finditer(page.text)
        ]


FACTORIES = {
    "rules": build_detector,
    "rules+names": lambda language: build_detector(language, model=NameFinder()),
}


@pytest.fixture(scope="module")
def photo_set(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, list[SimulatedPhoto]]:
    """A set of simulated photos, renamed, beside its manifest and documents."""
    root = tmp_path_factory.mktemp("photo-set")
    documents = root / "documents"
    documents.mkdir()
    (documents / "tst-letter.toml").write_text(LETTER, encoding="utf-8")
    (documents / "tst-notice.toml").write_text(NOTICE, encoding="utf-8")
    (root / "manifest.md").write_text(MANIFEST, encoding="utf-8")
    pdfs = {
        spec.name: render(spec, root / "pdf" / f"{spec.name}.pdf")
        for spec in load_documents(documents)
    }
    manifest = read_manifest(root / "manifest.md")
    photos: list[SimulatedPhoto] = []
    for condition_index, condition in enumerate(CONDITIONS):
        folder = root / "photos" / condition
        folder.mkdir(parents=True)
        pages = [(entry.document, page) for entry in manifest for page in range(entry.pages)]
        for page_number, (name, (document, page)) in enumerate(
            zip(expected_names(manifest, condition), pages, strict=True)
        ):
            index = condition_index * len(pages) + page_number
            photo = simulated_photo(
                pdfs[document],
                page,
                seed=index,
                captured=f"2026:11:25 10:00:{index:02d}",
                trim=index,
                # The angle photo of the letter loses its diacritics and its phone number.
                misread={
                    "Jiří": "Jiri",
                    "Čermák,": "Cermak,",
                    "+420": "",
                    "777": "",
                    "123": "",
                    "456.": "",
                }
                if condition == "angle" and document == "tst-letter"
                else None,
                orientation=6 if index == 1 else 1,
            )
            (folder / name).write_bytes(photo.jpeg)
            photos.append(photo)
    return root, photos


@pytest.fixture(scope="module")
def results(photo_set: tuple[Path, list[SimulatedPhoto]]) -> dict:
    root, photos = photo_set
    reader = PhotoReader(photos)
    return score_photos(
        root / "photos",
        root / "manifest.md",
        root / "out",
        documents=root / "documents",
        conditions=(*CONDITIONS, "dim"),
        engines=("onnxtr",),
        systems=tuple(FACTORIES),
        compare=(("rules", "rules+names"),),
        primary=("rules", "rules+names"),
        engine_loader=lambda name, root: reader,
        detectors=FACTORIES,
        resample_count=200,
    )


def test_the_digital_row_reads_every_item_and_finds_the_name(results: dict):
    totals = results["digital"]["totals"]
    assert totals["rules+names"]["items"] == {
        "gold": 3,
        "found": 3,
        "partial": 0,
        "missed": 0,
        "not_read": 0,
        "not_read_present": 0,
    }
    assert totals["rules+names"]["person_recall"]["value"] == 1.0
    assert totals["rules+names"]["safe_documents"] == 2
    assert totals["rules"]["person_residual"]["value"] == 1.0


def test_a_flat_photo_read_exactly_scores_as_the_digital_text(results: dict):
    flat = results["runs"]["onnxtr"]["flat"]
    assert flat["text"]["character_error_rate"] == 0.0
    assert flat["totals"]["rules+names"]["items"]["found"] == 3
    assert flat["totals"]["rules+names"]["leak_check_passed"] == 2
    assert flat["totals"]["rules+names"]["safe_documents"] == 2


def test_lost_diacritics_and_an_unread_item_are_scored_by_the_rules(results: dict):
    angle = results["runs"]["onnxtr"]["angle"]
    assert angle["text"]["character_error_rate"] > 0
    assert angle["text"]["diacritic_error_rate"] > 0
    names = angle["totals"]["rules+names"]
    # The name read without diacritics is still located and found; the phone was not read.
    assert names["items"]["not_read"] == 1
    assert names["items"]["found"] == 2
    assert names["person_recall"]["value"] == 1.0
    assert names["safe_documents"] == 1
    letter = angle["documents"]["tst-letter"]
    assert letter["photos"] == ["tst-letter.angle.jpg"]
    assert letter["systems"]["rules+names"]["safe"] is False


def test_a_document_of_two_photos_pools_them(results: dict):
    notice = results["runs"]["onnxtr"]["flat"]["documents"]["tst-notice"]
    assert notice["photos"] == ["tst-notice.p1.flat.jpg", "tst-notice.p2.flat.jpg"]
    assert notice["systems"]["rules"]["items"]["gold"] == 0
    assert notice["systems"]["rules"]["safe"] is True


def test_a_condition_without_photos_is_skipped_and_reported(results: dict):
    assert set(results["runs"]["onnxtr"]) == set(CONDITIONS)
    assert "dim" in results["skipped_conditions"]
    assert results["conditions"] == list(CONDITIONS)


def test_comparisons_and_the_primary_sentence_follow_the_rule(results: dict):
    (comparison,) = results["runs"]["onnxtr"]["flat"]["comparisons"]
    assert comparison["f2"]["delta"] > 0
    assert comparison["outcome"] in {"win", "tie", "n/a"}
    primary = results["primary"]
    assert primary["outcomes"]["dim"] == "not scored"
    assert primary["sentence"].startswith("rules+names is not better on phone photos")


def test_every_photo_is_fingerprinted_and_nothing_names_a_path(
    results: dict, photo_set: tuple[Path, list[SimulatedPhoto]]
):
    root, _ = photo_set
    assert len(results["photos"]["flat"]) == 3
    assert all(len(digest) == 64 for digest in results["photos"]["flat"].values())
    written = (root / "out" / "photos.json").read_text(encoding="utf-8")
    assert str(root) not in written
    assert json.loads(written)["schema"] == photo_run.PHOTOS_SCHEMA
    assert "## Comparisons" in (root / "out" / "photos.md").read_text(encoding="utf-8")
    assert "_text_tallies" not in written


def test_a_failing_engine_is_reported_and_left_out(photo_set: tuple[Path, list[SimulatedPhoto]]):
    root, _ = photo_set

    def broken(name: str, resource_root: Path):
        raise RuntimeError(name)

    results = score_photos(
        root / "photos",
        root / "manifest.md",
        root / "broken",
        documents=root / "documents",
        conditions=("flat",),
        engines=("kraken",),
        engine_loader=broken,
        detectors={"rules": build_detector},
        resample_count=10,
    )
    assert results["failed_engines"] == {"kraken": "RuntimeError"}
    assert results["runs"] == {}
    assert "Engine kraken failed" in photos_markdown(results)


def test_a_compared_system_must_be_run(photo_set: tuple[Path, list[SimulatedPhoto]]):
    root, _ = photo_set
    with pytest.raises(ValueError, match="not run"):
        score_photos(
            root / "photos",
            root / "manifest.md",
            root / "unused",
            systems=("rules",),
            compare=(("rules", "rules+other"),),
        )


def test_the_command_refuses_a_set_with_no_scorable_condition(
    photo_set: tuple[Path, list[SimulatedPhoto]], capsys: pytest.CaptureFixture[str]
):
    root, _ = photo_set
    code = main(
        [
            "photos",
            "score",
            "--photos",
            str(root / "photos"),
            "--manifest",
            str(root / "manifest.md"),
            "--documents",
            str(root / "documents"),
            "--conditions",
            "dim",
            "--out",
            str(root / "refused"),
        ]
    )
    assert code == 1
    assert "no condition can be scored" in capsys.readouterr().err


def test_the_command_refuses_a_malformed_comparison(photo_set: tuple[Path, list[SimulatedPhoto]]):
    root, _ = photo_set
    with pytest.raises(SystemExit):
        main(["photos", "score", "--out", str(root / "x"), "--compare", "rules"])
