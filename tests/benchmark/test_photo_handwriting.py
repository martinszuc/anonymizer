"""Handwritten items of the phone-photo benchmark, scored apart (`experiments/photo-rules.md`).

The filled-in form is rendered with each handwritten text printed after its
label and photographed in code; the scorer renders its own truth from the
document file, which holds no handwriting.
"""

import dataclasses
from pathlib import Path

import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.pipeline import build_detector
from anonymizer.core.types import Document, Entity, EntityType, Page

from benchmark import photo_run
from benchmark.photo_files import PhotoSetError, expected_names, read_manifest
from benchmark.photo_run import photos_markdown, score_photos
from benchmark.photo_test import DOCUMENTS
from benchmark.photo_train.generate import DOCUMENTS as TRAIN_DOCUMENTS
from benchmark.render import render
from benchmark.spec import DocumentSpec, GoldItem, Handwritten, load_documents
from tests.benchmark.test_photo_run import FACTORIES, NameFinder
from tests.photo_builders import PhotoReader, SimulatedPhoto, simulated_photo

FORM = """language = "cs"
kind = "form"
lines = [
    "Přihláška do kroužku keramiky.",
    "Kontakt pro dotazy: [[email:krouzek@example.com]].",
]

[[blocks]]
type = "handwritten"
after = 2
label = "Zákonný zástupce:"
text = "[[person:Jiří Čermák]]"

[[blocks]]
type = "handwritten"
after = 2
label = "Datum:"
text = "3. 11. 2026"
"""
MANIFEST = """| # | document | pages |
|---|---|---|
| 1 | tst-form | 1 |
"""
CONDITIONS = ("flat", "angle")


def _fill_in(spec: DocumentSpec, out: Path) -> Path:
    """Render the document with each handwritten text printed after its label, in reading order."""
    blocks = tuple(
        dataclasses.replace(block, label=f"{block.label} {block.text}")
        if isinstance(block, Handwritten)
        else block
        for block in spec.blocks
    )
    return render(dataclasses.replace(spec, blocks=blocks), out)


@pytest.fixture(scope="module")
def filled_set(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, list[SimulatedPhoto]]:
    root = tmp_path_factory.mktemp("handwriting")
    documents = root / "documents"
    documents.mkdir()
    (documents / "tst-form.toml").write_text(FORM, encoding="utf-8")
    (root / "manifest.md").write_text(MANIFEST, encoding="utf-8")
    (spec,) = load_documents(documents)
    filled = _fill_in(spec, root / "filled.pdf")
    manifest = read_manifest(root / "manifest.md")
    photos: list[SimulatedPhoto] = []
    for index, condition in enumerate(CONDITIONS):
        folder = root / "photos" / condition
        folder.mkdir(parents=True)
        (name,) = expected_names(manifest, condition)
        photo = simulated_photo(
            filled,
            0,
            seed=index,
            captured=f"2026:11:25 11:00:{index:02d}",
            trim=index,
            # The angle photo does not show the handwritten name; the date reads as "3.11.2026".
            misread={"Jiří": "", "Čermák": "", "3.": "3.11.2026", "11.": "", "2026": ""}
            if condition == "angle"
            else None,
        )
        (folder / name).write_bytes(photo.jpeg)
        photos.append(photo)
    return root, photos


def _score(root: Path, photos: list[SimulatedPhoto], engines: tuple[str, ...], out: str) -> dict:
    reader = PhotoReader(photos)
    return score_photos(
        root / "photos",
        root / "manifest.md",
        root / out,
        documents=root / "documents",
        conditions=CONDITIONS,
        engines=engines,
        systems=tuple(FACTORIES),
        engine_loader=lambda name, resource_root: reader,
        detectors=FACTORIES,
        resample_count=20,
    )


@pytest.fixture(scope="module")
def results(filled_set: tuple[Path, list[SimulatedPhoto]]) -> dict:
    root, photos = filled_set
    return _score(root, photos, ("onnxtr", "kraken"), "out")


def test_the_handwritten_name_is_scored_in_the_kraken_row(results: dict):
    flat = results["handwritten"]["conditions"]["flat"]
    assert results["handwritten"]["available"] is True
    assert flat["character_error_rate"] == 0.0
    assert flat["totals"]["rules+names"] == {
        "gold": 1,
        "not_read": 0,
        "found": 1,
        "partial": 0,
        "missed": 0,
        "safe_overall": 1,
        "documents": 1,
    }
    assert flat["totals"]["rules"]["missed"] == 1
    assert flat["totals"]["rules"]["safe_overall"] == 0


def test_handwriting_not_on_the_photo_is_not_read_and_counted_in_its_cer(results: dict):
    angle = results["handwritten"]["conditions"]["angle"]
    names = angle["totals"]["rules+names"]
    assert names["not_read"] == 1
    assert names["missed"] == 1
    assert names["safe_overall"] == 0
    # The name's 11 characters are all lost; the date loses its two spaces.
    assert angle["characters"] == len("Jiří Čermák") + len("3. 11. 2026")
    assert angle["character_error_rate"] == pytest.approx(13 / 22, abs=1e-4)


def test_a_detection_on_handwriting_is_no_false_alarm_in_the_printed_rows(results: dict):
    for engine in ("onnxtr", "kraken"):
        flat = results["runs"][engine]["flat"]["totals"]["rules+names"]
        assert flat["false_alarms"] == 0
        # Printed items only: the e-mail, found.
        assert flat["items"]["gold"] == 1
        assert flat["items"]["found"] == 1
        assert flat["safe_documents"] == 1
        # The handwritten name is not a person the printed rows know of.
        assert flat["person_recall"]["value"] is None


def test_only_kraken_has_a_handwritten_row(results: dict):
    assert results["handwritten"]["engine"] == "kraken"
    assert all("handwritten" not in row for row in results["runs"]["onnxtr"].values())
    assert all("handwritten" not in row for row in results["runs"]["kraken"].values())
    assert results["schema"] == photo_run.PHOTOS_SCHEMA
    markdown = photos_markdown(results)
    assert "## Handwritten items (kraken, counts only)" in markdown
    assert "| flat | rules+names | 0.0% | 0 | 1/1 | 0 | 0 | 1/1 |" in markdown


def test_without_kraken_the_handwritten_row_is_not_available(
    filled_set: tuple[Path, list[SimulatedPhoto]],
):
    root, photos = filled_set
    results = _score(root, photos, ("onnxtr",), "onnxtr-only")
    assert results["handwritten"] == {
        "engine": "kraken",
        "available": False,
        "reason": "not run",
        "conditions": {},
    }
    assert "Not available (kraken not run)." in photos_markdown(results)
    # The printed rows still leave the handwritten name out of their false alarms.
    assert results["runs"]["onnxtr"]["flat"]["totals"]["rules+names"]["false_alarms"] == 0


def test_a_failing_kraken_leaves_the_row_not_available(
    filled_set: tuple[Path, list[SimulatedPhoto]],
):
    root, _ = filled_set

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
    assert results["handwritten"]["reason"] == "failed"


def _document(text: str, *spans: tuple[int, int]) -> Document:
    entities = [Entity(EntityType.PERSON, 0, start, end, text[start:end]) for start, end in spans]
    return Document(pages=[Page(index=0, width=595, height=842, text=text)], entities=entities)


def test_only_a_detection_on_handwriting_alone_is_left_out_of_false_alarms():
    text = "Podpis: Jiří Čermák\nPavel Dvořák a Eva Malá"
    printed = (0, text.index("Eva"), len(text))
    handwriting = [(0, text.index("Jiří"), text.index("\n"))]
    on_handwriting = (text.index("Jiří"), text.index("\n"))
    elsewhere = (text.index("Pavel"), text.index(" a "))
    # A detection reaching from the handwriting into a printed item still counts for it.
    across = (text.index("Čermák"), len(text))
    item = GoldItem(EntityType.PERSON, "Eva Malá", "page")

    scored = photo_run._score(  # pyright: ignore[reportPrivateUsage]
        _document(text, on_handwriting, elsewhere), (item,), [printed], handwriting
    )
    assert scored.false_positives == {"Pavel Dvořák"}
    assert scored.missed == 1

    scored = photo_run._score(  # pyright: ignore[reportPrivateUsage]
        _document(text, across), (item,), [printed], handwriting
    )
    assert scored.found == 1
    assert scored.false_positives == set()

    scored = photo_run._score(  # pyright: ignore[reportPrivateUsage]
        _document(text, on_handwriting), (item,), [printed]
    )
    assert scored.false_positives == {"Jiří Čermák"}


@pytest.mark.parametrize("documents", [DOCUMENTS, TRAIN_DOCUMENTS], ids=["test", "train"])
def test_every_handwritten_label_of_a_photo_set_is_found_and_filled(
    documents: Path, tmp_path: Path
):
    specs = [
        spec
        for spec in load_documents(documents)
        if any(isinstance(block, Handwritten) for block in spec.blocks)
    ]
    assert specs
    for spec in specs:
        pages = [page.text for page in load_document(render(spec, tmp_path / "x.pdf")).pages]
        items = tuple(item for item in spec.gold if item.carrier == "handwritten")
        hands = photo_run._handwriting(spec, pages, items)  # pyright: ignore[reportPrivateUsage]
        blocks = [block for block in spec.blocks if isinstance(block, Handwritten)]
        fields = [hand.text[start:end] for hand in hands for start, end in hand.fields]
        assert fields == [block.text for block in blocks]
        for block in blocks:
            assert any(f"{block.label} {block.text}" in hand.text for hand in hands)
        placed = [(index, hand.text[a:b]) for hand in hands for index, (a, b) in hand.items]
        assert placed == [(index, item.text) for index, item in enumerate(items)]


def test_a_label_not_printed_as_a_line_is_refused():
    spec = DocumentSpec(
        name="tst",
        language="cs",
        kind="form",
        lines=(),
        blocks=(Handwritten(0, "Podpis:", "Jiří Čermák"),),
        gold=(GoldItem(EntityType.PERSON, "Jiří Čermák", "handwritten"),),
    )
    items = spec.gold
    with pytest.raises(PhotoSetError, match="label"):
        photo_run._handwriting(spec, ["Podpis: vlastní rukou"], items)  # pyright: ignore[reportPrivateUsage]
    hands = photo_run._handwriting(spec, ["Text\nPodpis:\nKonec"], items)  # pyright: ignore[reportPrivateUsage]
    assert hands[0].text == "Text\nPodpis: Jiří Čermák\nKonec"
    assert hands[0].items == ((0, (13, 24)),)


def test_a_handwritten_item_outside_every_handwritten_text_is_refused():
    spec = DocumentSpec(
        name="tst",
        language="cs",
        kind="form",
        lines=(),
        blocks=(Handwritten(0, "Datum:", "3. 11. 2026"),),
    )
    items = (GoldItem(EntityType.PERSON, "Jiří Čermák", "handwritten"),)
    with pytest.raises(PhotoSetError, match="no handwritten text"):
        photo_run._handwriting(spec, ["Datum:"], items)  # pyright: ignore[reportPrivateUsage]


def test_a_name_finder_reads_the_filled_form(filled_set: tuple[Path, list[SimulatedPhoto]]):
    root, _ = filled_set
    page = load_document(root / "filled.pdf").pages[0]
    assert "Zákonný zástupce: Jiří Čermák" in " ".join(page.text.split())
    assert [entity.text for entity in NameFinder().detect(page)] == ["Jiří Čermák"]
