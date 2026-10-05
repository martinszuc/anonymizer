"""Redaction of a photo of a document, end to end, verified on the saved file.

The photo is a phone's (`tests.image_builders.phone_photo`): stored sideways
with an EXIF orientation, recording 72 DPI, with an owner, a device, a time
and a GPS position in its EXIF and XMP. The leak check cannot see those, so
the output's bytes are searched for them directly. The engine is the
ink-reading stand-in (`tests.ocr_stand_in`), which also re-reads the
redacted page as the leak check does.
"""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import as_pdf, load_document
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import export_redacted, find_leaks, redact_pdf
from anonymizer.core.session import load_session, save_session
from anonymizer.core.types import Document

from tests.image_builders import PLANTED, every_byte, phone_photo
from tests.ocr_stand_in import InkReadingEngine
from tests.pdf_builders import CONTACT_EMAIL, write_pdf
from tests.pixels import ink

PHONE = "+420 603 123 456"
LINES = [f"Kontakt: {CONTACT_EMAIL}", f"Telefon: {PHONE}", "Poznamka: nic osobniho"]
# Where the last line's ink lies, in page points; nothing there is redacted.
UNTOUCHED_AREA = pymupdf.Rect(70, 150, 200, 166)


@pytest.fixture
def engine(tmp_path: Path) -> InkReadingEngine:
    return InkReadingEngine.reading(load_document(write_pdf(tmp_path / "original.pdf", [LINES])))


@pytest.fixture(params=["JPEG", "PNG", "TIFF"])
def photo(request: pytest.FixtureRequest, tmp_path: Path) -> Path:
    path = tmp_path / f"photo.{request.param.lower()}"
    path.write_bytes(phone_photo(LINES, image_format=request.param))
    return path


def detected(photo: Path, engine: InkReadingEngine) -> Document:
    document = load_document(photo, language="cs", ocr=engine)
    run_detection(document, build_detector("cs"))
    return document


def test_fixture_holds_the_planted_values_and_the_values_to_redact(
    photo: Path, engine: InkReadingEngine
):
    data = photo.read_bytes()
    assert all(value.encode() in data for value in PLANTED)
    document = detected(photo, engine)
    assert sorted(entity.text or "" for entity in document.entities) == [PHONE, CONTACT_EMAIL]


def test_redacted_copy_passes_and_holds_no_metadata_and_no_redacted_text(
    photo: Path, engine: InkReadingEngine, tmp_path: Path
):
    document = detected(photo, engine)
    destination = tmp_path / "photo-redacted.pdf"
    assert export_redacted(photo, document, destination, ocr=engine) == []
    output = every_byte(destination.read_bytes())
    for value in (*PLANTED, CONTACT_EMAIL, PHONE):
        assert value.encode() not in output, value
    assert b"Exif" not in output
    assert b"xmpmeta" not in output


def test_ink_under_every_box_is_removed_and_the_rest_kept(
    photo: Path, engine: InkReadingEngine, tmp_path: Path
):
    document = detected(photo, engine)
    destination = tmp_path / "out.pdf"
    export_redacted(photo, document, destination, ocr=engine)
    wrapped = as_pdf(photo.read_bytes())
    with pymupdf.open(stream=wrapped) as before, pymupdf.open(destination) as after:
        page = after[0]
        boxes = [bbox_to_unrotated_rect(box, page) for e in document.entities for box in e.bboxes]
        assert all(ink(before[0], box) > 0 for box in boxes)
        # The black fill is drawn over the picture; the picture itself holds no ink there.
        assert all(ink(page, box) == 0 for box in boxes)
        assert ink(page, UNTOUCHED_AREA) == ink(before[0], UNTOUCHED_AREA) > 0


def test_unredacted_value_is_reported_by_the_leak_check(
    photo: Path, engine: InkReadingEngine, tmp_path: Path
):
    # Control: a copy redacted without the phone number fails the check of the full review.
    document = detected(photo, engine)
    partial = detected(photo, engine)
    partial.entities = [entity for entity in partial.entities if entity.text != PHONE]
    destination = tmp_path / "out.pdf"
    redact_pdf(photo, partial, destination)
    leaks = find_leaks(destination, document, ocr=engine)
    assert PHONE in {leak.text for leak in leaks}


def test_a_saved_review_reopens_on_the_same_photo_only(
    photo: Path, engine: InkReadingEngine, tmp_path: Path
):
    document = detected(photo, engine)
    session = tmp_path / "review.json"
    save_session(document, session)
    reopened = load_session(session, photo, ocr=engine)
    assert [entity.text for entity in reopened.entities] == [
        entity.text for entity in document.entities
    ]
    other = tmp_path / f"other{photo.suffix}"
    other.write_bytes(phone_photo([*LINES, "jiny dokument"], image_format=_format_of(photo)))
    with pytest.raises(ValueError, match="different file"):
        load_session(session, other, ocr=engine)
    with pytest.raises(ValueError, match="different file"):
        export_redacted(other, document, tmp_path / "out.pdf", ocr=engine)


def _format_of(photo: Path) -> str:
    return {".jpeg": "JPEG", ".png": "PNG", ".tiff": "TIFF"}[photo.suffix]
