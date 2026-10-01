"""Redaction of searchable scans: a page-sized picture under an invisible OCR text layer.

Ingest reads such a page through its text layer, so detection finds the
invisible words and redaction boxes land where the layer puts them. What a
reader sees is the picture, so every test counts ink in the image data stored
in the saved output (`tests.pixels`).
"""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.ingest.normalize import bbox_to_unrotated_rect
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.redact import find_leaks, redact_pdf
from anonymizer.core.types import BBox, Document, EntityType

from tests.pdf_builders import CONTACT_EMAIL, write_searchable_scan
from tests.pixels import ink

PHONE = "+420 603 123 456"
UNTOUCHED = "Poznamka: nic osobniho"
LINES = [f"Kontakt: {CONTACT_EMAIL}", f"Telefon: {PHONE}", UNTOUCHED]
# Where the untouched line's ink lies, in unrotated page points.
UNTOUCHED_AREA = pymupdf.Rect(70, 150, 200, 166)
# PyMuPDF reports invisible text (render mode 3) as trace type 3.
INVISIBLE = 3

VARIANTS = {
    "flate": {},
    "jpeg": {"jpeg": True},
    "form_xobject": {"in_form_xobject": True},
    "rotated": {"rotation": 90},
}


def detected(path: Path) -> Document:
    document = load_document(path, language="cs")
    run_detection(document, build_detector("cs"))
    return document


def entity_boxes(document: Document) -> list[BBox]:
    return [box for entity in document.entities for box in entity.bboxes]


@pytest.fixture(params=list(VARIANTS), ids=list(VARIANTS))
def scan(request: pytest.FixtureRequest, tmp_path: Path) -> Path:
    return write_searchable_scan(tmp_path / "scan.pdf", LINES, **VARIANTS[request.param])


class TestFixture:
    """The starting state the redaction tests rely on."""

    def test_text_layer_is_invisible_and_read_by_ingest(self, scan: Path):
        with pymupdf.open(scan) as pdf:
            kinds = {span["type"] for span in pdf[0].get_texttrace()}
        page = load_document(scan).pages[0]
        assert kinds == {INVISIBLE}
        assert page.has_text_layer
        assert CONTACT_EMAIL in page.text

    def test_picture_covers_the_page(self, scan: Path):
        with pymupdf.open(scan) as pdf:
            page = pdf[0]
            (placement,) = page.get_image_info()
            mediabox = page.mediabox
            expected = (mediabox.x0, mediabox.y0, mediabox.x1, mediabox.y1)
            assert tuple(placement["bbox"]) == pytest.approx(expected, abs=0.1)

    def test_every_detected_box_has_ink_under_it(self, scan: Path):
        document = detected(scan)
        assert {entity.type for entity in document.entities} == {
            EntityType.EMAIL,
            EntityType.PHONE,
        }
        with pymupdf.open(scan) as pdf:
            page = pdf[0]
            assert all(
                ink(page, bbox_to_unrotated_rect(box, page)) for box in entity_boxes(document)
            )


class TestAlignedLayer:
    def test_ink_under_every_box_is_removed(self, scan: Path, tmp_path: Path):
        document = detected(scan)
        output = tmp_path / "out.pdf"
        redact_pdf(scan, document, output)
        with pymupdf.open(output) as pdf:
            page = pdf[0]
            left = [ink(page, bbox_to_unrotated_rect(box, page)) for box in entity_boxes(document)]
        assert left == [0] * len(left)

    def test_ink_elsewhere_is_kept(self, scan: Path, tmp_path: Path):
        output = tmp_path / "out.pdf"
        redact_pdf(scan, detected(scan), output)
        with pymupdf.open(scan) as before, pymupdf.open(output) as after:
            assert ink(before[0], UNTOUCHED_AREA) > 0
            assert ink(after[0], UNTOUCHED_AREA) == ink(before[0], UNTOUCHED_AREA)

    def test_hidden_text_is_removed_and_the_rest_kept(self, scan: Path, tmp_path: Path):
        document = detected(scan)
        output = tmp_path / "out.pdf"
        redact_pdf(scan, document, output)
        text = load_document(output).pages[0].text
        assert CONTACT_EMAIL not in text
        assert PHONE not in text
        assert UNTOUCHED in text
        assert find_leaks(output, document) == []


class TestNarrowLayer:
    """A layer whose word boxes are narrower than the printed words: a known gap."""

    # The email's ink as the 11-point scan printed it, wider than the 9-point layer.
    PRINTED = pymupdf.Rect(113, 86, 242, 106)

    @pytest.fixture
    def redacted(self, tmp_path: Path) -> tuple[Path, Path, Document]:
        scan = write_searchable_scan(tmp_path / "narrow.pdf", LINES, layer_font_size=9)
        document = detected(scan)
        output = tmp_path / "out.pdf"
        redact_pdf(scan, document, output)
        return scan, output, document

    def test_layer_is_narrower_than_the_ink_and_the_leak_check_passes(
        self, redacted: tuple[Path, Path, Document]
    ):
        scan, output, document = redacted
        email = next(entity for entity in document.entities if entity.type is EntityType.EMAIL)
        with pymupdf.open(scan) as pdf:
            assert ink(pdf[0], self.PRINTED) > 0
        assert email.bboxes[0].x1 < self.PRINTED.x1
        assert find_leaks(output, document) == []

    @pytest.mark.xfail(
        strict=True,
        reason="the producer's OCR geometry is trusted; the ink beyond a narrow layer "
        "stays readable until our own OCR re-reads searchable scans",
    )
    def test_ink_beyond_the_layer_is_removed(self, redacted: tuple[Path, Path, Document]):
        _, output, _ = redacted
        with pymupdf.open(output) as pdf:
            assert ink(pdf[0], self.PRINTED) == 0
