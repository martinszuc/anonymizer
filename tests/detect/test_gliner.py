"""Tests for the GLiNER detector, with a stand-in for the model.

The model itself is exercised only by the `model`-marked test at the end,
which is skipped unless the weights and the `gliner` package are present.
"""

import logging
import os
import re
import sys
import warnings
from pathlib import Path
from typing import Any

import pytest
from anonymizer.core.detect import CombinedDetector, detector_for, merge_entities
from anonymizer.core.detect.gliner import (
    MODEL_MAX_TOKENS,
    OVERLAP_TOKENS,
    WINDOW_TOKENS,
    GlinerDetector,
    load_gliner,
    load_gliner_detector,
    widen_to_words,
    without_known_warnings,
)
from anonymizer.core.types import BBox, DetectionSource, Entity, EntityType, Page, Word

# gliner 0.2.x's WhitespaceTokenSplitter, the splitter the pinned model's
# config selects; written out so the tests do not need the optional package.
GLINER_TOKEN = re.compile(r"\w+(?:[-_]\w+)*|\S")


def _gliner_tokens(text: str) -> list[re.Match[str]]:
    return list(GLINER_TOKEN.finditer(text))


class StandInModel:
    """Finds fixed strings in each text it receives, like GLiNER would.

    Spans are returned with offsets into the window text, exactly as the real
    model reports them. `cut` shortens a span to imitate GLiNER stopping
    inside a word. Like GLiNER, it reads only the first 384 of its tokens
    and warns when it drops the rest.
    """

    def __init__(self, found: dict[str, str], score: float = 0.9, cut: int = 0) -> None:
        self.found = found
        self.score = score
        self.cut = cut
        self.calls: list[list[str]] = []
        self.labels: list[str] = []

    def inference(
        self, texts: list[str], labels: list[str], *, threshold: float, flat_ner: bool
    ) -> list[list[dict[str, Any]]]:
        self.calls.append(texts)
        self.labels = labels
        results = []
        for text in texts:
            tokens = _gliner_tokens(text)
            if len(tokens) > MODEL_MAX_TOKENS:
                warnings.warn(
                    f"Sentence of length {len(tokens)} has been truncated to {MODEL_MAX_TOKENS}",
                    stacklevel=2,
                )
            read = text[: tokens[:MODEL_MAX_TOKENS][-1].end()] if tokens else ""
            spans = []
            for needle, label in self.found.items():
                for match in re.finditer(re.escape(needle), read):
                    spans.append(
                        {
                            "start": match.start(),
                            "end": match.end() - self.cut,
                            "text": needle,
                            "label": label,
                            "score": self.score,
                        }
                    )
            results.append(spans)
        return results


def _page(text: str) -> Page:
    words = [
        Word(match.group(), BBox(10.0 * i, 0.0, 10.0 * i + 8, 10.0), match.start(), match.end())
        for i, match in enumerate(re.finditer(r"\S+", text))
    ]
    return Page(index=0, width=595, height=842, text=text, words=words)


def _texts(entities: list[Entity]) -> list[str | None]:
    return [entity.text for entity in entities]


TEXT = "Smlouvu podepsal Jan Novák, bytem Kounicova 12, Brno."


def test_finds_labelled_spans_with_model_source_and_boxes():
    model = StandInModel({"Jan Novák": "person", "Kounicova 12": "street address"})
    entities = GlinerDetector(model).detect(_page(TEXT))
    assert _texts(entities) == ["Jan Novák", "Kounicova 12"]
    assert [entity.type for entity in entities] == [EntityType.PERSON, EntityType.ADDRESS]
    assert all(entity.source is DetectionSource.MODEL for entity in entities)
    assert entities[0].score == pytest.approx(0.9)
    assert len(entities[0].bboxes) == 2


def test_label_match_ignores_case():
    model = StandInModel({"Jan Novák": "Person"})
    assert _texts(GlinerDetector(model).detect(_page(TEXT))) == ["Jan Novák"]


def test_unrequested_labels_are_ignored():
    model = StandInModel({"Brno": "city"})
    assert GlinerDetector(model).detect(_page(TEXT)) == []


def test_distractor_spans_are_asked_for_and_dropped():
    model = StandInModel({"Kounicova 12": "street address", "Jan Novák": "organization"})
    detector = GlinerDetector(model)
    assert _texts(detector.detect(_page(TEXT))) == ["Kounicova 12"]
    assert model.labels == ["person", "street address", "organization"]


def test_a_label_cannot_be_a_distractor():
    with pytest.raises(ValueError, match="distractor"):
        GlinerDetector(StandInModel({}), distractors=("Person",))


def test_empty_page_does_not_call_the_model():
    model = StandInModel({})
    assert GlinerDetector(model).detect(_page("  \n ")) == []
    assert model.calls == []


def test_span_cut_inside_a_word_is_widened():
    model = StandInModel({"Novák": "person"}, cut=2)
    entities = GlinerDetector(model).detect(_page(TEXT))
    assert _texts(entities) == ["Novák"]


@pytest.mark.parametrize("lone", ["V", "5", "J."], ids=["preposition", "digit", "initial-with-dot"])
def test_a_span_of_one_character_is_dropped(lone: str):
    # On a badly read scan the model tags lone letters, which propagation
    # then marks wherever the letter stands alone.
    model = StandInModel({lone: "street address", "Li": "person"})
    page = _page(f"{lone} Brně bydlí pan Li.")
    assert _texts(GlinerDetector(model).detect(page)) == ["Li"]


def test_one_character_inside_a_word_is_widened_and_kept():
    model = StandInModel({"N": "person"})
    assert _texts(GlinerDetector(model).detect(_page("volal N.Novák"))) == ["N.Novák"]


@pytest.mark.parametrize("threshold", [-0.1, 1.5])
def test_invalid_threshold_is_refused(threshold):
    with pytest.raises(ValueError, match="threshold"):
        GlinerDetector(StandInModel({}), threshold=threshold)


def test_no_labels_is_refused():
    with pytest.raises(ValueError, match="label"):
        GlinerDetector(StandInModel({}), labels={})


# --- windows ------------------------------------------------------------


def _filler(count: int, start: int = 0) -> str:
    return " ".join(f"slovo{i}" for i in range(start, start + count))


def test_name_beyond_the_model_limit_is_found():
    # GLiNER alone would stop after 384 tokens and never see this name.
    text = f"{_filler(500)} Petra Nováková {_filler(10, 500)}"
    model = StandInModel({"Petra Nováková": "person"})
    entities = GlinerDetector(model).detect(_page(text))
    assert _texts(entities) == ["Petra Nováková"]
    assert text[entities[0].span[0] : entities[0].span[1]] == "Petra Nováková"


def test_every_window_stays_within_the_token_budget():
    model = StandInModel({})
    GlinerDetector(model).detect(_page(_filler(1000)))
    windows = model.calls[0]
    assert len(windows) > 1
    assert all(len(_gliner_tokens(window)) <= WINDOW_TOKENS for window in windows)


def _punctuated_filler(count: int) -> str:
    # Handwriting read by OCR: every word carries punctuation, which GLiNER
    # counts as tokens of its own (4 per word here).
    return " ".join(f"slovo{i}.,;" for i in range(count))


def test_punctuation_heavy_windows_stay_within_the_model_limit():
    model = StandInModel({})
    GlinerDetector(model).detect(_page(_punctuated_filler(400)))
    assert max(len(_gliner_tokens(window)) for window in model.calls[0]) <= MODEL_MAX_TOKENS


def test_name_in_the_last_words_of_a_punctuation_heavy_page_is_found():
    text = f"{_punctuated_filler(400)} Petra Nováková."
    model = StandInModel({"Petra Nováková": "person"})
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # a truncated window fails the test
        entities = GlinerDetector(model).detect(_page(text))
    assert _texts(entities) == ["Petra Nováková"]


def test_a_word_longer_than_a_window_is_still_split():
    # One "word" without spaces, e.g. a dotted line, is many GLiNER tokens.
    text = f"Podpis: {'.' * 1000} Jan Novák"
    model = StandInModel({"Jan Novák": "person"})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        entities = GlinerDetector(model).detect(_page(text))
    assert _texts(entities) == ["Jan Novák"]


def test_windows_cover_every_word():
    text = _filler(777)
    model = StandInModel({})
    GlinerDetector(model).detect(_page(text))
    seen = {word for window in model.calls[0] for word in window.split()}
    assert seen == set(text.split())


def test_name_in_the_overlap_is_reported_once():
    step = WINDOW_TOKENS - OVERLAP_TOKENS
    text = f"{_filler(step + 5)} Jan Novák {_filler(200, 1000)}"
    model = StandInModel({"Jan Novák": "person"})
    entities = GlinerDetector(model).detect(_page(text))
    assert _texts(entities) == ["Jan Novák"]


def test_name_cut_by_a_window_edge_keeps_the_whole_name():
    # The first window ends after "Jan"; the stand-in reports "Jan" there and
    # the full name in the next window. Only the full name survives.
    text = f"{_filler(WINDOW_TOKENS - 1)} Jan Novák {_filler(50, 1000)}"
    model = StandInModel({"Jan Novák": "person", "Jan": "person"})
    entities = GlinerDetector(model).detect(_page(text))
    assert _texts(entities) == ["Jan Novák"]


# --- widening -----------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "needle", "expected"),
    [
        ("firma Stavby s.r.o. sídlí", "Stavby s.r.o", "Stavby s.r.o."),
        ("volal Novák.", "Novák", "Novák"),
        ("volal Novákovi, pak", "Nováko", "Novákovi"),
        ("„Jan Novák“ řekl", "Jan Novák", "Jan Novák"),
        ("(Jan) a", "Jan", "Jan"),
        ("Ing. Marie Dvořáková podepsala", "Marie Dvořáková", "Marie Dvořáková"),
        ("jméno:Novák", "Novák", "jméno:Novák"),
        ("Podepsal (J. Novák).", "J. Novák", "J. Novák"),
        ("Podepsal J. Novák.", "Novák.", "Novák"),
        ("Dodavatel: Stavby s.r.o.", "Stavby s.r.o", "Stavby s.r.o."),
        ("Dodavatel (Stavby s.r.o.).", "Stavby s.r.o.", "Stavby s.r.o."),
        ("Podepsal „Novák“.", "Novák", "Novák"),
        ("Podepsal (Novák.).", "Novák", "Novák"),
    ],
    ids=[
        "abbreviation-dot",
        "sentence-dot",
        "cut-word",
        "czech-quotes",
        "brackets",
        "title",
        "glued-word",
        "bracket-then-full-stop",
        "full-stop-ending-text",
        "abbreviation-ending-text",
        "abbreviation-in-brackets",
        "czech-quotes-then-full-stop",
        "full-stops-around-bracket",
    ],
)
def test_widen_to_words(text, needle, expected):
    start = text.index(needle)
    widened = widen_to_words(text, start, start + len(needle))
    assert widened is not None
    assert text[widened[0] : widened[1]] == expected


def test_widen_punctuation_only_span_is_dropped():
    assert widen_to_words("a , b", 2, 3) is None


# --- merging with rules -------------------------------------------------


def _entity(kind: EntityType, start: int, end: int, text: str, **extra: Any) -> Entity:
    return Entity(type=kind, page_index=0, start=start, end=end, text=text[start:end], **extra)


def test_merge_drops_span_inside_a_stronger_one():
    text = "jan.novak@example.com"
    email = _entity(EntityType.EMAIL, 0, len(text), text)
    person = _entity(EntityType.PERSON, 0, 8, text, source=DetectionSource.MODEL)
    assert merge_entities([person, email]) == [email]


def test_merge_keeps_partial_overlaps():
    # Dropping the address would leave "Brno 602 00" unredacted.
    text = "Kounicova 12, Brno 602 00"
    address = _entity(EntityType.ADDRESS, 0, len(text), text)
    phone = _entity(EntityType.PHONE, 14, 25, text)
    assert set(map(id, merge_entities([address, phone]))) == {id(address), id(phone)}


def test_merge_keeps_same_offsets_on_different_carriers():
    text = "Jan Novák"
    on_page = _entity(EntityType.PERSON, 0, 9, text)
    on_surface = _entity(EntityType.PERSON, 0, 9, text, surface_id="metadata:0:Author")
    assert len(merge_entities([on_page, on_surface])) == 2


def test_merge_keeps_regions():
    region = Entity(type=EntityType.REGION, page_index=0, bboxes=[BBox(0, 0, 10, 10)])
    assert merge_entities([region]) == [region]


def test_combined_detector_runs_rules_and_model():
    text = "Jan Novák, tel. +420 777 123 456"
    model = StandInModel({"Jan Novák": "person", "+420 777": "person"})
    combined = CombinedDetector([detector_for(None), GlinerDetector(model)])
    entities = combined.detect(_page(text))
    assert [entity.type for entity in entities] == [EntityType.PERSON, EntityType.PHONE]
    assert combined.name == "rules:all+gliner-multi-v2.1"


def test_combined_detector_needs_a_member():
    with pytest.raises(ValueError, match="detector"):
        CombinedDetector([])


# --- loading ------------------------------------------------------------


def test_known_warnings_are_hidden_only_inside_the_block(caplog):
    tokenizer_logger = logging.getLogger("transformers.tokenization_utils_tokenizers")
    regex_message = "The tokenizer you are loading with an incorrect regex pattern: ..."
    jit_message = "`torch.jit.script` is deprecated. Please switch to `torch.compile`."
    # GLiNER's notice that it dropped words is a recall gap and must stay visible.
    truncation_message = "Sentence of length 409 has been truncated to 384"
    with caplog.at_level(logging.WARNING), warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with without_known_warnings():
            tokenizer_logger.warning(regex_message)
            warnings.warn(jit_message, FutureWarning, stacklevel=1)
            tokenizer_logger.warning("an unrelated tokenizer problem")
            warnings.warn("an unrelated deprecation", FutureWarning, stacklevel=1)
            warnings.warn(truncation_message, UserWarning, stacklevel=1)
        tokenizer_logger.warning(regex_message)
    assert [record.getMessage() for record in caplog.records] == [
        "an unrelated tokenizer problem",
        regex_message,
    ]
    assert [str(warning.message) for warning in caught] == [
        "an unrelated deprecation",
        truncation_message,
    ]


def test_loading_forces_offline_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    monkeypatch.delenv("TRANSFORMERS_OFFLINE", raising=False)
    monkeypatch.setitem(sys.modules, "gliner", None)  # stop before any model code runs
    with pytest.raises(ImportError, match="optional 'ner' dependencies"):
        load_gliner(tmp_path, tmp_path)
    assert os.environ["HF_HUB_OFFLINE"] == "1"
    assert os.environ["TRANSFORMERS_OFFLINE"] == "1"


def test_missing_model_files_name_the_fetch_command(tmp_path):
    with pytest.raises(FileNotFoundError, match=re.escape("download.py fetch gliner-multi-v2.1")):
        load_gliner_detector(tmp_path)


REPOSITORY = Path(__file__).resolve().parents[2]


@pytest.mark.model
def test_real_model_finds_czech_names_offline():
    pytest.importorskip("gliner")
    try:
        detector = load_gliner_detector(REPOSITORY)
    except FileNotFoundError:
        pytest.skip("GLiNER not fetched")
    # Synthetic sentence; inflected forms on purpose.
    page = _page("Včera volal Petře Novákové a poslal Janu Svobodovi smlouvu.")
    found = {entity.text for entity in detector.detect(page) if entity.type is EntityType.PERSON}
    assert {"Petře Novákové", "Janu Svobodovi"} <= found


@pytest.mark.model
def test_real_model_reads_the_end_of_a_punctuation_heavy_page():
    pytest.importorskip("gliner")
    try:
        detector = load_gliner_detector(REPOSITORY)
    except FileNotFoundError:
        pytest.skip("GLiNER not fetched")
    from gliner.data_processing.tokenizer import (  # pyright: ignore[reportMissingImports]
        WhitespaceTokenSplitter,
    )

    # The splitter written out above must be the one gliner uses.
    sample = "Ing. J.Novák-Svobodová, (tel.: 777/123) e_mail; s.r.o.…"
    assert [token for token, _, _ in WhitespaceTokenSplitter()(sample)] == GLINER_TOKEN.findall(
        sample
    )
    # Synthetic, shaped like OCR of handwriting; the name comes last.
    page = _page(f"{_punctuated_filler(400)} Smlouvu podepsal Petr Svoboda.")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        found = {entity.text for entity in detector.detect(page)}
    assert not [warning for warning in caught if "truncated" in str(warning.message)]
    assert "Petr Svoboda" in found
