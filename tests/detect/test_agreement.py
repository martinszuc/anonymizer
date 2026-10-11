"""Tests for `AgreementDetector`: what several detectors agree on."""

import re

import pytest
from anonymizer.core.detect import AgreementDetector, CombinedDetector
from anonymizer.core.detect.base import RuleDetector
from anonymizer.core.types import BBox, DetectionSource, Entity, EntityType, Page, Word


def _page(text: str) -> Page:
    words = [
        Word(match.group(), BBox(10.0 * i, 0.0, 10.0 * i + 8, 10.0), match.start(), match.end())
        for i, match in enumerate(re.finditer(r"\S+", text))
    ]
    return Page(index=0, width=595, height=842, text=text, words=words)


class TestAgreement:
    PAGE = _page("Podepsal Jan Novák a Eva Malá.")

    class Fixed:
        def __init__(self, name: str, spans: dict[str, EntityType]) -> None:
            self.name = name
            self.spans = spans

        def detect(self, page: Page) -> list[Entity]:
            return [
                Entity(
                    type=kind,
                    page_index=page.index,
                    start=page.text.index(text),
                    end=page.text.index(text) + len(text),
                    text=text,
                    bboxes=page.bboxes_for_span(
                        page.text.index(text), page.text.index(text) + len(text)
                    ),
                    source=DetectionSource.MODEL,
                    score=0.9,
                )
                for text, kind in self.spans.items()
            ]

    def test_keeps_overlapping_readings_of_one_type(self):
        first = self.Fixed("a", {"Jan Novák": EntityType.PERSON, "Eva": EntityType.PERSON})
        second = self.Fixed("b", {"Novák": EntityType.PERSON, "Eva Malá": EntityType.ADDRESS})
        agreed = AgreementDetector([first, second])
        assert agreed.name == "a&b"
        # "Novák" lies inside "Jan Novák" and is merged away; "Eva" has no
        # person reading in the second detector.
        assert [entity.text for entity in agreed.detect(self.PAGE)] == ["Jan Novák"]

    def test_needs_two_detectors(self):
        with pytest.raises(ValueError, match="at least two"):
            AgreementDetector([RuleDetector([])])

    def test_a_union_keeps_everything(self):
        first = self.Fixed("a", {"Jan Novák": EntityType.PERSON})
        second = self.Fixed("b", {"Eva Malá": EntityType.PERSON})
        found = CombinedDetector([first, second]).detect(self.PAGE)
        assert [entity.text for entity in found] == ["Jan Novák", "Eva Malá"]
