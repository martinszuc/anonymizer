"""The benchmark documents: markup, generation and round trip through ingest."""

from pathlib import Path

import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.types import EntityType

from benchmark.render import render
from benchmark.score import compact
from benchmark.spec import load_document_spec, load_documents


def _spec(tmp_path: Path, body: str):
    path = tmp_path / "doc.toml"
    path.write_text(body, encoding="utf-8")
    return load_document_spec(path)


def test_markup_becomes_text_and_gold_items(tmp_path):
    spec = _spec(
        tmp_path,
        'language = "cs"\nkind = "letter"\n'
        'lines = ["Píše [[person:Jan Novák]], tel. [[phone:777 123 456]]."]\n'
        'metadata = { Author = "[[person:Jan Novák]]" }\n',
    )
    assert spec.lines == ("Píše Jan Novák, tel. 777 123 456.",)
    assert spec.metadata == {"Author": "Jan Novák"}
    assert [(item.type, item.text, item.carrier) for item in spec.gold] == [
        (EntityType.PERSON, "Jan Novák", "page"),
        (EntityType.PHONE, "777 123 456", "page"),
        (EntityType.PERSON, "Jan Novák", "metadata"),
    ]


@pytest.mark.parametrize(
    ("line", "message"),
    [("[[nickname:Honza]]", "unknown entity type"), ("[[person:Jan Novák]", "unbalanced")],
)
def test_bad_markup_is_refused(tmp_path, line, message):
    with pytest.raises(ValueError, match=message):
        _spec(tmp_path, f'language = "cs"\nkind = "x"\nlines = ["{line}"]\n')


def test_missing_field_is_refused(tmp_path):
    with pytest.raises(ValueError, match="malformed"):
        _spec(tmp_path, 'language = "cs"\nlines = ["a"]\n')


def test_filler_expands_to_the_requested_word_count(tmp_path):
    spec = _spec(tmp_path, 'language = "cs"\nkind = "x"\nlines = ["{{filler:500}}"]\n')
    assert len(spec.lines[0].split()) == 500


def test_shipped_documents_load_and_plant_items():
    specs = load_documents()
    assert len(specs) >= 6
    # A document without planted items measures false alarms, so it lists decoys.
    assert all(spec.gold or spec.decoys for spec in specs)
    assert sum(bool(spec.gold) for spec in specs) >= 6
    assert {spec.language for spec in specs} >= {"cs", "sk", "en"}


def test_long_document_puts_a_name_beyond_the_model_limit():
    spec = next(spec for spec in load_documents() if spec.name == "cs-long-report")
    text = " ".join(spec.lines)
    last_name = [item for item in spec.gold if item.type is EntityType.PERSON][-1]
    assert len(text[: text.index(last_name.text)].split()) > 384


@pytest.mark.parametrize("spec", load_documents(), ids=lambda spec: spec.name)
def test_every_planted_item_survives_generation(tmp_path, spec):
    document = load_document(render(spec, tmp_path / f"{spec.name}.pdf"), language=spec.language)
    page_text = compact("".join(page.text for page in document.pages))
    surfaces: dict[str, list[str]] = {}
    for surface in document.surfaces:
        surfaces.setdefault(str(surface.kind), []).append(compact(surface.value))
    for item in spec.gold:
        if item.carrier == "page":
            assert compact(item.text) in page_text, item
        else:
            assert any(compact(item.text) in value for value in surfaces[item.carrier]), item
