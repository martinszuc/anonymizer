"""Scoring rules and a rules-only run end to end."""

import json

from anonymizer.core.types import Document, Entity, EntityType, Page, Surface, SurfaceKind

from benchmark.report import markdown
from benchmark.run import run
from benchmark.score import (
    decoys_removed,
    false_positives,
    left_in_carrier,
    residue,
    score_detection,
)
from benchmark.spec import DocumentSpec, GoldItem

TEXT = "Smlouvu podepsal Jan Novák, bytem Lidická 12, 602 00 Brno. Kupující souhlasí."
SPEC = DocumentSpec(
    name="tiny",
    language="cs",
    kind="contract",
    lines=(TEXT,),
    gold=(
        GoldItem(EntityType.PERSON, "Jan Novák", "page"),
        GoldItem(EntityType.ADDRESS, "Lidická 12, 602 00 Brno", "page"),
        GoldItem(EntityType.PERSON, "Jan Novák", "metadata"),
    ),
    decoys=("Kupující",),
)


def _entity(text: str, kind: EntityType, surface_id: str | None = None) -> Entity:
    start = TEXT.index(text) if surface_id is None else 0
    return Entity(
        type=kind,
        page_index=0,
        start=start,
        end=start + len(text),
        text=text,
        surface_id=surface_id,
    )


def _document(text: str, entities: list[Entity] | None = None) -> Document:
    return Document(
        pages=[Page(index=0, width=595, height=842, text=text)], entities=entities or []
    )


def test_detection_outcomes():
    entities = [
        _entity("Jan Novák", EntityType.ORGANIZATION),
        _entity("Lidická 12", EntityType.ADDRESS),
    ]
    assert score_detection(SPEC, _document(TEXT, entities)) == [
        ("found", False),
        ("partial", True),
        ("missed", False),
    ]


def test_a_shared_word_elsewhere_is_not_a_partial_find():
    text = "Kontakt: jan.novak@example.com, Jan Novák"
    spec = DocumentSpec(
        name="x",
        language="cs",
        kind="x",
        lines=(text,),
        gold=(GoldItem(EntityType.PERSON, "Jan Novák", "page"),),
    )
    start = text.index("jan.novak")
    email = Entity(
        type=EntityType.EMAIL,
        page_index=0,
        start=start,
        end=start + len("jan.novak@example.com"),
        text="jan.novak@example.com",
    )
    assert score_detection(spec, _document(text, [email])) == [("missed", False)]


def test_a_surname_planted_alone_is_its_own_occurrence():
    text = "Technik Roman Bartoš přijede ve čtvrtek. Minule ji dělal pan Bartoš."
    spec = DocumentSpec(
        name="x",
        language="cs",
        kind="x",
        lines=(text,),
        gold=(
            GoldItem(EntityType.PERSON, "Roman Bartoš", "page"),
            GoldItem(EntityType.PERSON, "Bartoš", "page"),
        ),
    )
    full_name = Entity(type=EntityType.PERSON, page_index=0, start=8, end=20, text="Roman Bartoš")
    assert score_detection(spec, _document(text, [full_name])) == [
        ("found", True),
        ("missed", False),
    ]


def test_surface_items_match_only_entities_on_that_carrier():
    entities = [_entity("Jan Novák", EntityType.PERSON, surface_id="metadata:doc:Author")]
    scores = score_detection(SPEC, _document(TEXT, entities))
    assert scores[2] == ("found", True)
    assert scores[0] == ("missed", False)


def test_false_positives_are_distinct_and_ignore_planted_items():
    entities = [
        _entity("Kupující", EntityType.PERSON),
        _entity("Kupující", EntityType.PERSON),
        _entity("Novák", EntityType.PERSON),
    ]
    assert false_positives(SPEC, _document(TEXT, entities)) == ["Kupující"]


def test_residue_reports_whole_items_and_unique_fragments():
    original = _document(TEXT)
    # The street was redacted, postcode and town were not; "Brno" also
    # appears outside the item in this version, so it is no evidence.
    redacted = _document("Smlouvu podepsal ███, bytem ███, 602 00 Brno. Kupující souhlasí. Brno")
    readable = residue(SPEC, _document(TEXT + " Brno"), redacted)
    assert readable[0] == (False, [])
    assert readable[1] == (False, ["602"])
    assert residue(SPEC, original, original)[0] == (True, [])


def test_leaks_are_counted_against_their_own_carrier():
    original = _document(TEXT)
    original.surfaces.append(Surface(SurfaceKind.METADATA, "Jan Novák", "Author"))
    # The name stays on the page; the metadata holding it was cleared.
    redacted = _document("Smlouvu podepsal Jan Novák, bytem ███. Kupující souhlasí.")
    assert residue(SPEC, original, redacted)[2] == (True, [])
    assert left_in_carrier(SPEC, original, redacted) == [True, False, False]


def test_removed_decoys_are_reported():
    assert decoys_removed(SPEC, _document("Smlouvu podepsal")) == ["Kupující"]


def test_rules_only_run_writes_results_and_pictures(tmp_path):
    spec = DocumentSpec(
        name="contact",
        language="cs",
        kind="letter",
        lines=("Kontakt: jan.novak@example.com, tel. +420 777 123 456, Jan Novák",),
        gold=(
            GoldItem(EntityType.EMAIL, "jan.novak@example.com", "page"),
            GoldItem(EntityType.PHONE, "+420 777 123 456", "page"),
            GoldItem(EntityType.PERSON, "Jan Novák", "page"),
        ),
    )
    results = run(tmp_path, systems=("rules",), specs=[spec])
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert saved == json.loads(json.dumps(results))
    scores = results["documents"]["contact"]["systems"]["rules"]
    assert [item["outcome"] for item in scores["items"]] == ["found", "found", "missed"]
    assert scores["leak_check_passed"]
    assert not scores["safe"]  # the name is still readable
    assert results["totals"]["rules"]["counts"]["found"] == 2
    assert results["totals"]["rules"]["words"] == 9
    assert results["totals"]["rules"]["false_alarms_per_1000_words"] == 0.0
    for picture in ("original", "rules.detected", "rules.redacted", "rules.collage"):
        assert (tmp_path / "images" / f"contact.{picture}.png").stat().st_size > 0
    assert results["totals"]["rules"]["by_carrier"]["page"]["found"] == 2
    assert results["totals"]["rules"]["by_kind"]["letter"]["documents"] == 1
    report = markdown(results)
    assert "| rules | 2/3 |" in report
    # The name is readable, and "jan" of the email address with it.
    assert "| page | 2/3 / 2 |" in report
    assert "| letter | 1 | 2/3 / 0/1 / 0 |" in report
    assert "| rules | contact | person | page | Jan Novák | missed | yes |" in report
