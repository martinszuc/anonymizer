"""The photo set on disk: manifest, capture times, renaming by them (`benchmark.photo_files`)."""

from pathlib import Path

import pytest
from PIL import Image

from benchmark.__main__ import main
from benchmark.photo_files import (
    ManifestEntry,
    PhotoSetError,
    apply_renames,
    capture_time,
    expected_names,
    named_photos,
    photo_files,
    photo_name,
    plan_renames,
    plan_set,
    read_manifest,
)
from tests.photo_builders import jpeg_with_capture_time

MANIFEST = """# Print order

| # | document | pages |
|---|---|---|
| 1 | cs-letter | 1 |
| 2 | cs-terms | 2 |
| 3 | sk-cv | 1 |
"""
ENTRIES = [ManifestEntry("cs-letter", 1), ManifestEntry("cs-terms", 2), ManifestEntry("sk-cv", 1)]
NAMES = ["cs-letter.flat.jpg", "cs-terms.p1.flat.jpg", "cs-terms.p2.flat.jpg", "sk-cv.flat.jpg"]
# Capture times in print order; the camera's names are deliberately not in that order.
SHOTS = [
    ("IMG_0104.JPG", "2026:11:25 10:00:01", None),
    ("IMG_0102.jpeg", "2026:11:25 10:00:05", "120"),
    ("IMG_0103.jpg", "2026:11:25 10:00:05", "450"),
    ("IMG_0101.JPG", "2026:11:25 10:01:00", None),
]


def _write(path: Path, captured: str | None, subsec: str | None = None, shade: int = 200) -> None:
    picture = Image.new("RGB", (40, 30), (shade, shade, shade))
    path.write_bytes(jpeg_with_capture_time(picture, captured, subsec=subsec))


@pytest.fixture
def folder(tmp_path: Path) -> Path:
    flat = tmp_path / "flat"
    flat.mkdir()
    for shade, (name, captured, subsec) in enumerate(SHOTS):
        _write(flat / name, captured, subsec, shade=50 + 40 * shade)
    return flat


def _contents(folder: Path) -> dict[str, bytes]:
    return {path.name: path.read_bytes() for path in folder.iterdir()}


class TestManifest:
    def test_rows_are_read_in_print_order(self, tmp_path: Path):
        path = tmp_path / "manifest.md"
        path.write_text(MANIFEST, encoding="utf-8")
        assert read_manifest(path) == ENTRIES

    @pytest.mark.parametrize(
        ("rows", "message"),
        [
            ("| 1 | a | 1 |\n| 3 | b | 1 |", "out of order"),
            ("| 1 | a | 1 |\n| 2 | a | 1 |", "twice"),
            ("| 1 | a | 0 |", "no pages"),
            ("no table here", "no document"),
        ],
    )
    def test_a_malformed_manifest_is_refused(self, tmp_path: Path, rows: str, message: str):
        path = tmp_path / "manifest.md"
        path.write_text(rows, encoding="utf-8")
        with pytest.raises(PhotoSetError, match=message):
            read_manifest(path)

    def test_names_number_pages_only_for_documents_of_several(self):
        assert photo_name("cs-cv", 1, 1, "dim") == "cs-cv.dim.jpg"
        assert photo_name("cs-terms", 2, 2, "dim") == "cs-terms.p2.dim.jpg"
        assert expected_names(ENTRIES, "flat") == NAMES


class TestCaptureTime:
    def test_sub_seconds_order_photos_taken_in_the_same_second(self, folder: Path):
        early, early_text = capture_time(folder / "IMG_0102.jpeg")
        late, _ = capture_time(folder / "IMG_0103.jpg")
        assert early < late
        assert early_text == "2026:11:25 10:00:05.120"

    def test_a_photo_without_one_is_refused(self, tmp_path: Path):
        _write(tmp_path / "IMG_1.jpg", None)
        with pytest.raises(PhotoSetError, match="no capture time"):
            capture_time(tmp_path / "IMG_1.jpg")

    def test_an_unreadable_one_is_refused(self, tmp_path: Path):
        _write(tmp_path / "IMG_1.jpg", "yesterday")
        with pytest.raises(PhotoSetError, match="unreadable"):
            capture_time(tmp_path / "IMG_1.jpg")


class TestPhotoFiles:
    def test_jpegs_are_taken_whatever_the_case_of_their_ending(self, folder: Path):
        assert len(photo_files(folder)) == 4

    def test_hidden_files_are_ignored(self, folder: Path):
        (folder / ".DS_Store").write_bytes(b"\0\0")
        assert len(photo_files(folder)) == 4

    def test_heic_is_refused_with_how_to_avoid_it(self, folder: Path):
        (folder / "IMG_0105.HEIC").write_bytes(b"\0\0\0\x18ftypheic")
        with pytest.raises(PhotoSetError, match=r"HEIC is not read.*Most Compatible"):
            photo_files(folder)

    def test_another_file_is_refused(self, folder: Path):
        (folder / "IMG_0105.MOV").write_bytes(b"\0")
        with pytest.raises(PhotoSetError, match="not a JPEG photo"):
            photo_files(folder)

    def test_a_jpeg_name_on_other_content_is_refused(self, folder: Path):
        (folder / "IMG_0105.jpg").write_bytes(b"\0\0\0\x18ftypheic")
        with pytest.raises(PhotoSetError, match="does not hold a JPEG"):
            photo_files(folder)

    def test_a_missing_folder_is_refused(self, tmp_path: Path):
        with pytest.raises(PhotoSetError, match="no such folder"):
            photo_files(tmp_path / "dim")


class TestRename:
    def test_photos_are_named_by_capture_order(self, folder: Path):
        before = _contents(folder)
        plan = plan_renames(folder, ENTRIES, "flat")
        assert [(rename.source.name, rename.target.name) for rename in plan] == [
            ("IMG_0104.JPG", NAMES[0]),
            ("IMG_0102.jpeg", NAMES[1]),
            ("IMG_0103.jpg", NAMES[2]),
            ("IMG_0101.JPG", NAMES[3]),
        ]
        assert apply_renames(plan) == 4
        after = _contents(folder)
        assert sorted(after) == sorted(NAMES)
        # Every photo kept its bytes under its new name: nothing lost or swapped.
        assert after[NAMES[0]] == before["IMG_0104.JPG"]
        assert after[NAMES[3]] == before["IMG_0101.JPG"]
        assert named_photos(folder, ENTRIES, "flat") == [folder / name for name in NAMES]

    def test_renaming_again_changes_nothing(self, folder: Path):
        apply_renames(plan_renames(folder, ENTRIES, "flat"))
        before = _contents(folder)
        plan = plan_renames(folder, ENTRIES, "flat")
        assert all(rename.source == rename.target for rename in plan)
        assert apply_renames(plan) == 0
        assert _contents(folder) == before

    def test_manifest_names_out_of_capture_order_are_refused(self, folder: Path):
        # The first photo taken already carries the last name: renamed by hand, or wrongly.
        (folder / "IMG_0104.JPG").rename(folder / "sk-cv.flat.jpg")
        with pytest.raises(PhotoSetError, match="contradicts"):
            plan_renames(folder, ENTRIES, "flat")

    def test_a_temporary_name_left_by_an_interrupted_run_is_planned_again(self, folder: Path):
        (folder / "IMG_0101.JPG").rename(folder / "renaming-0123.jpg")
        plan = plan_renames(folder, ENTRIES, "flat")
        assert plan[-1].source.name == "renaming-0123.jpg"
        assert plan[-1].target.name == NAMES[-1]

    def test_a_missing_photo_stops_everything(self, folder: Path):
        (folder / "IMG_0101.JPG").unlink()
        before = _contents(folder)
        with pytest.raises(PhotoSetError, match="3 photos, but the manifest has 4 pages"):
            plan_renames(folder, ENTRIES, "flat")
        assert _contents(folder) == before

    def test_an_extra_photo_stops_everything(self, folder: Path):
        _write(folder / "IMG_0109.JPG", "2026:11:25 10:05:00")
        with pytest.raises(PhotoSetError, match="5 photos"):
            plan_renames(folder, ENTRIES, "flat")

    def test_a_photo_without_a_capture_time_stops_everything(self, folder: Path):
        _write(folder / "IMG_0101.JPG", None)
        with pytest.raises(PhotoSetError, match=r"IMG_0101\.JPG: no capture time"):
            plan_renames(folder, ENTRIES, "flat")

    def test_two_photos_with_one_capture_time_stop_everything(self, folder: Path):
        _write(folder / "IMG_0101.JPG", "2026:11:25 10:00:01")
        with pytest.raises(PhotoSetError, match="share a capture time"):
            plan_renames(folder, ENTRIES, "flat")

    def test_one_bad_folder_stops_every_folder_and_all_are_reported(
        self, folder: Path, tmp_path: Path
    ):
        dim = tmp_path / "dim"
        dim.mkdir()
        _write(dim / "IMG_0200.JPG", "2026:11:25 20:00:00")
        with pytest.raises(PhotoSetError) as refused:
            plan_set(tmp_path, ENTRIES, ("flat", "dim", "angle"))
        message = str(refused.value)
        assert "dim: 1 photos" in message
        assert "angle: no such folder" in message
        assert sorted(path.name for path in folder.iterdir()) == sorted(
            name for name, _, _ in SHOTS
        )

    def test_a_target_held_by_a_file_outside_the_plan_is_refused(self, folder: Path):
        plan = plan_renames(folder, ENTRIES, "flat")
        (folder / NAMES[0]).write_bytes(b"not part of the plan")
        before = _contents(folder)
        with pytest.raises(PhotoSetError, match="exists"):
            apply_renames(plan)
        assert _contents(folder) == before

    def test_scoring_refuses_a_folder_not_renamed_yet(self, folder: Path):
        with pytest.raises(PhotoSetError, match="rename"):
            named_photos(folder, ENTRIES, "flat")


class TestCommand:
    def _run(self, folder: Path, *extra: str) -> int:
        manifest = folder.parent / "manifest.md"
        manifest.write_text(MANIFEST, encoding="utf-8")
        return main(
            [
                "photos",
                "rename",
                "--photos",
                str(folder.parent),
                "--manifest",
                str(manifest),
                "--conditions",
                "flat",
                *extra,
            ]
        )

    def test_a_dry_run_prints_the_plan_and_renames_nothing(
        self, folder: Path, capsys: pytest.CaptureFixture[str]
    ):
        before = _contents(folder)
        assert self._run(folder, "--dry-run") == 0
        printed = capsys.readouterr().out
        assert f"flat: IMG_0104.JPG -> {NAMES[0]}" in printed
        assert "nothing renamed" in printed
        assert _contents(folder) == before

    def test_the_command_renames_and_then_finds_nothing_to_do(
        self, folder: Path, capsys: pytest.CaptureFixture[str]
    ):
        assert self._run(folder) == 0
        assert sorted(path.name for path in folder.iterdir()) == sorted(NAMES)
        assert self._run(folder) == 0
        assert "renamed 0 photos" in capsys.readouterr().out

    def test_a_refused_set_exits_with_one_and_says_why(
        self, folder: Path, capsys: pytest.CaptureFixture[str]
    ):
        (folder / "IMG_0101.JPG").unlink()
        assert self._run(folder) == 1
        assert "nothing renamed" in capsys.readouterr().err
