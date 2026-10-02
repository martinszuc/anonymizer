"""The benchmark documents: markup, generation and round trip through ingest."""

from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.types import EntityType

from benchmark.render import FIXED_DATE, render
from benchmark.score import compact
from benchmark.spec import load_document_spec, load_documents, spec_summary


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


HIDDEN = (
    'language = "cs"\nkind = "form"\nlines = ["Přihláška"]\n'
    'fields = [{ label = "Jméno:", value = "[[person:Zdeněk Kratochvíl]]" }]\n'
    'annotations = [{ author = "[[person:Řehoř Šťastný]]", text = "Ověřit" }]\n'
    'attachments = [{ filename = "[[person:kratochvil]]-doklad.pdf", '
    'description = "Doklad: [[person:Zdeněk Kratochvíl]]" }]\n'
    'xmp = { creator = "[[person:Řehoř Šťastný]]", title = "Přihláška <A & B>" }\n'
)


def test_hidden_carriers_become_gold_items(tmp_path):
    spec = _spec(tmp_path, HIDDEN)
    assert spec.fields == (("Jméno:", "Zdeněk Kratochvíl"),)
    assert spec.annotations == (("Řehoř Šťastný", "Ověřit"),)
    assert spec.attachments == (("kratochvil-doklad.pdf", "Doklad: Zdeněk Kratochvíl"),)
    assert spec.xmp == {"creator": "Řehoř Šťastný", "title": "Přihláška <A & B>"}
    # A field's value is drawn on the page and stored in the field.
    assert [(item.text, item.carrier) for item in spec.gold] == [
        ("Zdeněk Kratochvíl", "page"),
        ("Zdeněk Kratochvíl", "form_field"),
        ("Řehoř Šťastný", "annotation"),
        ("kratochvil", "embedded_file"),
        ("Zdeněk Kratochvíl", "embedded_file"),
        ("Řehoř Šťastný", "xmp"),
    ]
    assert spec_summary(spec)["words"] == 4


def test_hidden_carriers_are_written_where_ingest_reads_them(tmp_path):
    spec = _spec(tmp_path, HIDDEN)
    path = render(spec, tmp_path / "form.pdf")
    surfaces = {
        (str(surface.kind), surface.ref.split("/")[-1]): surface.value
        for surface in load_document(path, language="cs").surfaces
    }
    assert surfaces["form_field", "value"] == "Zdeněk Kratochvíl"
    assert surfaces["annotation", "title"] == "Řehoř Šťastný"
    assert surfaces["annotation", "content"] == "Ověřit"
    assert surfaces["embedded_file", "filename"] == "kratochvil-doklad.pdf"
    assert surfaces["embedded_file", "description"] == "Doklad: Zdeněk Kratochvíl"
    xmp = next(value for (kind, _), value in surfaces.items() if kind == "xmp")
    assert "<rdf:li>Řehoř Šťastný</rdf:li>" in xmp
    assert "Přihláška &lt;A &amp; B&gt;" in xmp
    # The value is drawn into the field's appearance, so the page shows it too.
    assert "Zdeněk Kratochvíl" in load_document(path, language="cs").pages[0].text


def test_generated_attachments_carry_a_fixed_date(tmp_path):
    with pymupdf.open(render(_spec(tmp_path, HIDDEN), tmp_path / "form.pdf")) as pdf:
        assert pdf.embfile_info(0)["creationDate"] == FIXED_DATE


def test_unknown_xmp_property_is_refused(tmp_path):
    spec = _spec(tmp_path, 'language = "cs"\nkind = "x"\nlines = ["a"]\nxmp = { Author = "b" }\n')
    with pytest.raises(ValueError, match="unsupported XMP"):
        render(spec, tmp_path / "x.pdf")


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
    # A document without planted items measures false alarms, so it lists decoys.
    assert all(spec.gold or spec.decoys for spec in specs)
    assert sum(bool(spec.gold) for spec in specs) >= 15
    # Every language has documents with and without personal data.
    for language in ("cs", "sk", "en"):
        assert any(spec.gold for spec in specs if spec.language == language), language
        assert any(not spec.gold for spec in specs if spec.language == language), language
    carriers = {item.carrier for spec in specs for item in spec.gold}
    assert carriers >= {"page", "link", "metadata", "bookmark", "form_field", "annotation"}
    assert carriers >= {"embedded_file", "xmp"}


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
