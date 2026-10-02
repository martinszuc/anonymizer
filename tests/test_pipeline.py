"""Tests for detection as every client runs it."""

from pathlib import Path

import pytest
from anonymizer.core.detect import (
    CombinedDetector,
    GlinerDetector,
    NamesOnly,
    RuleDetector,
    role_words_for,
)
from anonymizer.core.ingest import load_document
from anonymizer.core.pipeline import build_detector, run_detection
from anonymizer.core.types import DetectionSource, Document, Entity, EntityType, Page

from tests.detect.test_gliner import StandInModel
from tests.pdf_builders import CONTACT_EMAIL, write_pdf


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    return write_pdf(tmp_path / "cv.pdf", [[f"mail {CONTACT_EMAIL}", f"again {CONTACT_EMAIL}"]])


def detected(pdf: Path) -> Document:
    document = load_document(pdf, language="en")
    run_detection(document, build_detector("en"))
    return document


class TestBuildDetector:
    def test_rules_alone_without_a_model(self):
        assert isinstance(build_detector("cs"), RuleDetector)

    def test_rules_and_model_together(self):
        model = GlinerDetector(StandInModel({}))
        detector = build_detector("cs", model=model)
        assert isinstance(detector, CombinedDetector)
        wrapped = detector.detectors[1]
        assert isinstance(wrapped, NamesOnly)
        assert wrapped.detector is model
        assert wrapped.role_words == role_words_for("cs")

    def test_model_unfiltered_when_names_only_is_off(self):
        model = GlinerDetector(StandInModel({}))
        detector = build_detector("cs", model=model, names_only=False)
        assert isinstance(detector, CombinedDetector)
        assert detector.detectors[1] is model


class FirstOccurrence:
    """Finds only the first occurrence of a name, as a detector often does."""

    name = "first-occurrence"

    def detect(self, page: Page) -> list[Entity]:
        start = page.text.find("Jan Novak")
        if start < 0:
            return []
        end = start + len("Jan Novak")
        return [Entity(EntityType.PERSON, page.index, start, end, page.text[start:end])]


class TestRunDetection:
    def test_tells_its_progress_per_page(self, tmp_path: Path):
        document = load_document(write_pdf(tmp_path / "three.pdf", [["a"], ["b"], ["c"]]))
        told: list[tuple[int, int]] = []
        run_detection(document, build_detector("cs"), progress=lambda *step: told.append(step))
        assert told == [(0, 3), (1, 3), (2, 3), (3, 3)]

    @pytest.fixture
    def named(self, tmp_path: Path) -> Document:
        return load_document(
            write_pdf(tmp_path / "name.pdf", [["Jan Novak wrote", "to Jan Novak"]])
        )

    def test_marks_further_occurrences(self, named: Document):
        run_detection(named, FirstOccurrence())
        assert [entity.source for entity in named.entities] == [
            DetectionSource.RULE,
            DetectionSource.PROPAGATED,
        ]

    def test_propagation_can_be_turned_off(self, named: Document):
        run_detection(named, FirstOccurrence(), propagate=False)
        assert len(named.entities) == 1

    def test_replaces_earlier_entities(self, pdf: Path):
        document = detected(pdf)
        run_detection(document, build_detector("en"))
        assert len(document.entities) == 2
