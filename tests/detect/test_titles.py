"""Tests for widening person spans over the academic titles beside them."""

from pathlib import Path

import pytest
from anonymizer.core.detect import extend_with_titles
from anonymizer.core.ingest import load_document
from anonymizer.core.pipeline import run_detection
from anonymizer.core.redact import export_redacted
from anonymizer.core.types import Document, Entity, EntityType, Page

from tests.pdf_builders import write_pdf

NAME = "Jan Novák"
# The test PDFs use a base font without Czech letters.
PDF_NAME = "Jan Novak"


def person(page: Page, text: str = NAME, entity_type: EntityType = EntityType.PERSON) -> Entity:
    start = page.text.index(text)
    return Entity(entity_type, page.index, start, start + len(text), text)


def widened(text: str, entity_type: EntityType = EntityType.PERSON) -> str | None:
    page = Page(0, 595, 842, text=text)
    document = Document(pages=[page], entities=[person(page, entity_type=entity_type)])
    extend_with_titles(document)
    return document.entities[0].text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (f"podepsal Ing. {NAME} dne", f"Ing. {NAME}"),
        (f"doc. Ing. {NAME}, Ph.D. dne", f"doc. Ing. {NAME}, Ph.D."),
        (f"prof. MUDr. {NAME}, DrSc.", f"prof. MUDr. {NAME}, DrSc."),
        (f"Ing. arch. {NAME}", f"Ing. arch. {NAME}"),
        (f"Doc. RNDr. {NAME}, CSc., Ph.D.", f"Doc. RNDr. {NAME}, CSc., Ph.D."),
        (f"Bc. {NAME}, DiS.", f"Bc. {NAME}, DiS."),
        (f"{NAME} PhD", f"{NAME} PhD"),
        (f"{NAME}, MBA a další", f"{NAME}, MBA"),
        (f"Mgr.{NAME}", f"Mgr.{NAME}"),
        (f"Ing.\n{NAME},\nPh.D.", f"Ing.\n{NAME},\nPh.D."),
        (f"Ing.  {NAME} ,  Ph.D.", f"Ing.  {NAME} ,  Ph.D."),
        (f"Dr. {NAME}", f"Dr. {NAME}"),
    ],
)
def test_titles_and_degrees_beside_a_name_join_it(text: str, expected: str):
    assert widened(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        f"pan {NAME} dne",
        f"Lng. {NAME}",  # OCR misread, not a title
        f"Xing. {NAME}",  # a title only as a whole word
        f"Ing. a {NAME}",  # something between the title and the name
        f"{NAME}, MBAx",
        f"{NAME} Ph.Dr",
        f"{NAME}. Ing. Petr",  # a title after the name belongs to the next one
    ],
)
def test_nothing_else_joins_a_name(text: str):
    assert widened(text) == NAME


def test_only_persons_are_widened():
    assert widened(f"Ing. {NAME}", EntityType.ORGANIZATION) == NAME


def test_a_name_never_grows_into_another_entity():
    page = Page(0, 595, 842, text=f"Ing. {NAME}, Ph.D.")
    title = Entity(EntityType.OTHER, 0, 0, 4, "Ing.")
    document = Document(pages=[page], entities=[title, person(page)])
    assert extend_with_titles(document) == 0
    assert document.entities[1].text == NAME


def test_widened_boxes_cover_the_title(tmp_path: Path):
    document = load_document(write_pdf(tmp_path / "cv.pdf", [[f"Ing. {PDF_NAME}, Ph.D."]]))
    document.entities = [person(document.pages[0], PDF_NAME)]
    before = len(document.entities[0].bboxes)
    extend_with_titles(document)
    assert document.entities[0].text == f"Ing. {PDF_NAME}, Ph.D."
    assert len(document.entities[0].bboxes) > before


class FirstName:
    """Finds the name once and without its title, as the model often does."""

    name = "first-name"

    def detect(self, page: Page) -> list[Entity]:
        return [person(page, PDF_NAME)] if PDF_NAME in page.text else []


def test_a_repeat_gets_its_own_title_and_none_survives_redaction(tmp_path: Path):
    source = write_pdf(
        tmp_path / "letter.pdf", [[f"Ing. {PDF_NAME} wrote", f"Reply to doc. {PDF_NAME}, Ph.D."]]
    )
    document = load_document(source)
    run_detection(document, FirstName())
    assert [entity.text for entity in document.entities] == [
        f"Ing. {PDF_NAME}",
        f"doc. {PDF_NAME}, Ph.D.",
    ]
    output = tmp_path / "out.pdf"
    assert export_redacted(source, document, output) == []
    text = load_document(output).pages[0].text
    assert "Ing." not in text
    assert "doc." not in text
    assert "Ph.D." not in text
    assert "wrote" in text
