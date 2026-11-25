"""Phone-photo test documents: the Czech and Slovak benchmark documents, laid out as printed."""

import json
from collections import Counter

import pymupdf
import pytest
from anonymizer.core.ingest import load_document

from benchmark.__main__ import main
from benchmark.photo_files import read_manifest
from benchmark.photo_test import DOCUMENTS, render_print
from benchmark.render import render
from benchmark.score import page_locations
from benchmark.spec import Boxes, Handwritten, Signature, Stamp, Table, load_documents


@pytest.fixture(scope="module")
def specs():
    return load_documents(DOCUMENTS)


@pytest.fixture(scope="module")
def benchmark_specs():
    return {spec.name: spec for spec in load_documents() if spec.language in ("cs", "sk")}


def test_they_are_the_benchmarks_czech_and_slovak_documents(specs, benchmark_specs):
    assert [spec.name for spec in specs] == sorted(benchmark_specs)
    for spec in specs:
        original = benchmark_specs[spec.name]
        assert (spec.language, spec.kind, spec.decoys) == (
            original.language,
            original.kind,
            original.decoys,
        )


def test_they_plant_the_items_of_the_benchmark_page(specs, benchmark_specs):
    for spec in specs:
        assert {item.carrier for item in spec.gold} <= {"page", "handwritten"}, spec.name
        planted = {(item.type, item.text) for item in spec.gold}
        on_page = {
            (item.type, item.text)
            for item in benchmark_specs[spec.name].gold
            if item.carrier == "page"
        }
        assert planted == on_page, spec.name


def test_every_kind_of_layout_is_used(specs):
    kinds = Counter(type(block) for spec in specs for block in spec.blocks)
    assert set(kinds) == {Table, Boxes, Handwritten, Signature, Stamp}
    assert sum(spec.letterhead is not None for spec in specs) >= 5
    assert sum(bool(spec.footer) for spec in specs) >= 15
    handwritten = [item for spec in specs for item in spec.gold if item.carrier == "handwritten"]
    assert {item.type.value for item in handwritten} >= {"person", "phone"}


def test_pages_match_the_benchmark_and_printed_items_are_located_whole(
    specs, benchmark_specs, tmp_path
):
    for spec in specs:
        pdf = render(spec, tmp_path / f"{spec.name}.pdf")
        original = render(benchmark_specs[spec.name], tmp_path / f"{spec.name}.original.pdf")
        document = load_document(pdf, language=spec.language)
        with pymupdf.open(original) as reference:
            assert len(document.pages) == reference.page_count, spec.name
        located = page_locations(spec, document)
        for index, item in enumerate(spec.gold):
            if item.carrier != "page":
                continue
            page, start, end = located[index] or (-1, 0, 0)
            assert page >= 0, (spec.name, item.text)
            assert " ".join(document.pages[page].text[start:end].split()) == item.text


def test_the_print_pack_lists_what_to_write_by_hand(tmp_path, capsys):
    assert main(["photo-test", "--out", str(tmp_path)]) == 0
    assert "gold.json" in capsys.readouterr().out
    gold = json.loads((tmp_path / "gold.json").read_text(encoding="utf-8"))
    entries = read_manifest(tmp_path / "manifest.md")
    assert [entry.document for entry in entries] == [entry["name"] for entry in gold]
    assert sum(entry.pages for entry in entries) == 23
    with pymupdf.open(tmp_path / "rq8-print.pdf") as pack:
        assert pack.page_count == 23
    with pymupdf.open(tmp_path / "fill-in.pdf") as sheet:
        listed = " ".join(" ".join(page.get_text().split()) for page in sheet)
    for spec in load_documents(DOCUMENTS):
        for block in spec.blocks:
            if isinstance(block, Handwritten):
                assert block.text in listed
    assert render_print(tmp_path / "again").name == "gold.json"
