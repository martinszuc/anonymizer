"""The photo training documents: fixed print split, valid values, disjoint from the test data."""

import ast
import json
import re
import tomllib
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.detect.bank_account import is_valid_account_number
from anonymizer.core.detect.birth_number import is_valid_birth_number
from anonymizer.core.detect.company_id import is_valid_company_id
from anonymizer.core.detect.iban import is_valid_iban
from anonymizer.core.types import EntityType

from benchmark.__main__ import main
from benchmark.photo_train import DOCUMENTS, generate, render_split, write
from benchmark.photo_train.generate import PRINT_PER_LANGUAGE
from benchmark.photo_train.templates import KINDS, TEMPLATES, Template
from benchmark.photo_train.values import NAMES, NamePool
from benchmark.render import render
from benchmark.spec import (
    Boxes,
    DocumentSpec,
    Handwritten,
    Signature,
    Stamp,
    Table,
    document_set,
    load_document_spec,
    load_documents,
    visible_text,
)
from experiments import heldout, name_forms
from experiments.declension import feminine_surname

REPOSITORY = Path(__file__).parents[2]
OWN = REPOSITORY / "benchmark" / "photo_train"
SYNTHETIC_COUNT = 40


def _specs(documents, directory: Path) -> list[DocumentSpec]:
    return [load_document_spec(path) for path in write(documents, directory)]


@pytest.fixture(scope="module")
def print_specs() -> list[DocumentSpec]:
    return load_documents(DOCUMENTS)


@pytest.fixture(scope="module")
def synthetic_specs(tmp_path_factory) -> list[DocumentSpec]:
    directory = tmp_path_factory.mktemp("synthetic")
    return _specs(generate("synthetic", count=SYNTHETIC_COUNT), directory)


# --- The splits ------------------------------------------------------------------


def test_the_committed_print_split_is_what_the_generator_writes():
    documents = generate("print")
    committed = {path.name: path.read_text(encoding="utf-8") for path in DOCUMENTS.glob("*.toml")}
    assert committed == {f"{document.name}.toml": document.source for document in documents}


def test_the_print_split_covers_every_kind_in_both_languages(print_specs):
    by_language = Counter(spec.language for spec in print_specs)
    assert by_language == {"cs": PRINT_PER_LANGUAGE, "sk": PRINT_PER_LANGUAGE}
    for language in ("cs", "sk"):
        kinds = {spec.kind for spec in print_specs if spec.language == language}
        assert kinds == set(KINDS)
        assert len(TEMPLATES[language]) * 2 == PRINT_PER_LANGUAGE


def test_the_print_split_has_the_layouts_of_the_photo_test_documents(print_specs, synthetic_specs):
    kinds = {type(block) for spec in print_specs for block in spec.blocks}
    assert kinds == {Table, Boxes, Handwritten, Signature, Stamp}
    assert sum(spec.letterhead is not None for spec in print_specs) >= 4
    assert sum(bool(spec.footer) for spec in print_specs) >= 20
    handwritten = {
        item.type for spec in print_specs for item in spec.gold if item.carrier != "page"
    }
    assert handwritten >= {EntityType.PERSON, EntityType.PHONE, EntityType.BIRTH_NUMBER}
    assert not any(spec.laid_out for spec in synthetic_specs)


def test_every_print_document_fits_one_page(print_specs, tmp_path):
    for spec in print_specs:
        with pymupdf.open(render(spec, tmp_path / f"{spec.name}.pdf")) as pdf:
            assert pdf.page_count == 1, spec.name


def test_the_synthetic_split_is_seeded_and_grows_by_appending():
    shorter = generate("synthetic", count=3)
    longer = generate("synthetic", count=5)
    assert shorter == generate("synthetic", count=3)
    assert set(shorter) < set(longer)
    other = generate("synthetic", count=3, seed="another")
    assert {document.source for document in other}.isdisjoint(
        document.source for document in shorter
    )
    printed = {document.source for document in generate("print")}
    assert printed.isdisjoint(document.source for document in longer)


@pytest.mark.parametrize(
    ("split", "count", "seed"),
    [("print", 3, None), ("print", 0, "x"), ("synthetic", 0, None), ("scan", 1, None)],
)
def test_bad_arguments_are_refused(split: str, count: int, seed: str | None):
    with pytest.raises(ValueError, match="split"):
        generate(split, count=count, seed=seed)


def test_the_benchmark_never_reads_them():
    names = {spec.name for spec in load_documents()}
    assert len(names) == document_set()["documents"] == 26
    assert not names & {path.stem for path in DOCUMENTS.glob("*.toml")}


# --- The values ------------------------------------------------------------------

_TITLES = re.compile(r"\b(pan|paní|pane|panu|panem|pán|pani|pána|pánovi|pánom)\b", re.IGNORECASE)
_DEGREE = re.compile(r"\b(MUDr|JUDr|Mgr|Ing|Bc|PaedDr)\.")
_ITEM = re.compile(r"\[\[([a-z_]+):([^\[\]]+)\]\]")


def test_every_gold_item_is_a_whole_valid_value(print_specs, synthetic_specs):
    counts: Counter[EntityType] = Counter()
    for spec in [*print_specs, *synthetic_specs]:
        assert spec.gold
        for item in spec.gold:
            assert item.carrier in ("page", "handwritten")
            assert item.text == item.text.strip() and item.text
            _check_value(item.type, item.text, spec.language)
            counts[item.type] += 1
        for decoy in spec.decoys:
            assert any(decoy in line for line in visible_text(spec)), decoy
            if re.fullmatch(r"\d{8}", decoy):
                assert is_valid_company_id(decoy), decoy
    assert set(counts) == {
        EntityType.PERSON,
        EntityType.ADDRESS,
        EntityType.EMAIL,
        EntityType.PHONE,
        EntityType.BIRTH_NUMBER,
        EntityType.DATE,
        EntityType.BANK_ACCOUNT,
        EntityType.IBAN,
    }


def _check_value(entity_type: EntityType, value: str, language: str) -> None:
    if entity_type is EntityType.PERSON:
        assert value[:1].isupper(), value
        assert not _TITLES.search(value) and not _DEGREE.search(value), value
        assert 1 <= len(value.split()) <= 2, value
    elif entity_type is EntityType.BIRTH_NUMBER:
        assert is_valid_birth_number(value), value
    elif entity_type is EntityType.BANK_ACCOUNT:
        number, _, _ = value.partition("/")
        prefix, _, base = number.rpartition("-")
        assert is_valid_account_number(base, prefix or None), value
    elif entity_type is EntityType.IBAN:
        assert value.startswith({"cs": "CZ", "sk": "SK"}[language]), value
        assert is_valid_iban(value), value
    elif entity_type is EntityType.EMAIL:
        assert re.fullmatch(r"[a-z.]+@example\.(com|org|net)", value), value
    elif entity_type is EntityType.PHONE:
        assert re.fullmatch(r"(\+42[01] |0)?[679]\d\d \d{3} \d{3}", value), value
    elif entity_type is EntityType.DATE:
        day, month, year = map(int, value.split(". "))
        assert date(year, month, day) < date(2020, 1, 1)
    else:
        assert entity_type is EntityType.ADDRESS, entity_type
        assert re.fullmatch(r"[^\W\d][\w ]* \d+(/\d+)?, \d{3} \d{2} \w[\w ]*", value), value


def test_items_stand_apart_from_the_words_around_them():
    for document in [*generate("print"), *generate("synthetic", count=SYNTHETIC_COUNT)]:
        source = document.source
        assert unicodedata.normalize("NFC", source) == source
        assert "{" not in source and "}" not in source, document.name
        for found in _ITEM.finditer(source):
            before = source[found.start() - 1 : found.start()]
            after = source[found.end() : found.end() + 1]
            assert not before.isalnum() and not after.isalnum(), found.group(0)


def test_birth_numbers_encode_the_gender_of_a_full_name(print_specs):
    """A woman's month is raised by 50; her birth number follows her full name, dates between."""
    matched = 0
    for spec in print_specs:
        person = ""
        for item in spec.gold:
            if item.type is EntityType.PERSON:
                person = "" if "." in item.text else item.text
            elif item.type is EntityType.BIRTH_NUMBER:
                if person.endswith("á"):
                    assert int(item.text[2:4]) > 50, (spec.name, person, item.text)
                    matched += 1
                person = ""
            elif item.type is not EntityType.DATE:
                person = ""
    assert matched


# --- Disjoint from the test data ---------------------------------------------------


def _pool_words(pool: NamePool) -> set[str]:
    names = (*pool.male_first, *pool.female_first, *pool.surnames)
    return {name.word for name in names} | {feminine_surname(name).word for name in pool.surnames}


def _lists_words(lists: name_forms.NameLists) -> set[str]:
    names = (
        *lists.male_first,
        *lists.female_first,
        *lists.surnames,
        *lists.nicknames.values(),
        *lists.foreign_male_first,
        *lists.foreign_female_first,
        *lists.foreign_surnames,
    )
    return {name.word for name in names} | {feminine_surname(name).word for name in lists.surnames}


def test_names_are_new_to_the_benchmark_and_both_generated_sets(print_specs, synthetic_specs):
    benchmark = {
        word
        for spec in load_documents()
        for item in spec.gold
        if item.type is EntityType.PERSON
        for word in item.text.split()
    }
    other = (
        benchmark
        | set().union(
            *(_lists_words(lists) for splits in heldout.NAMES.values() for lists in splits.values())
        )
        | set().union(
            *(
                _lists_words(lists)
                for splits in name_forms.NAMES.values()
                for lists in splits.values()
            )
        )
    )
    written = {
        word
        for spec in [*print_specs, *synthetic_specs]
        for item in spec.gold
        if item.type is EntityType.PERSON
        for word in item.text.split()
        if not re.fullmatch(r"\w\.", word)  # an initial
    }
    for pool in NAMES.values():
        assert not _pool_words(pool) & other
    assert not written & other, sorted(written & other)


GRAM = 5
_ALTERNATIVE = re.compile(r"\{[A-Z]\?([^|{}]*)\|[^{}]*\}")
_SLOT = re.compile(r"\{[^{}]*\}|\[\[[a-z_]+:[^\[\]]*\]\]")
_TOKEN = re.compile(r"\w+|□")


def _grams(line: str) -> set[tuple[str, ...]]:
    """Word 5-grams as `test_heldout` counts them: alternatives masculine, slots as □."""
    line = _SLOT.sub(" □ ", _ALTERNATIVE.sub(r"\1", line))
    words = _TOKEN.findall(line.lower())
    return {tuple(words[index : index + GRAM]) for index in range(len(words) - GRAM + 1)}


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def _other_texts() -> list[str]:
    """Benchmark documents, held-out templates and other strings of the generator directories."""
    texts = [
        line
        for language in heldout.TEMPLATES
        for split in heldout.SPLITS
        for template in (*heldout.TEMPLATES[language][split], *heldout.CONTROLS[language][split])
        for line in template.lines
    ]
    for directory in ("benchmark", "experiments", "scripts"):
        for path in sorted((REPOSITORY / directory).rglob("*.py")):
            if path.is_relative_to(OWN):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            texts += [
                node.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
            ]
        for path in sorted((REPOSITORY / directory).rglob("*.toml")):
            if not path.is_relative_to(OWN):
                texts += _strings(tomllib.loads(path.read_text(encoding="utf-8")))
    return texts


def test_the_scan_sees_the_benchmark_and_the_held_out_set():
    texts = _other_texts()
    assert any("[[person:" in text for text in texts)
    assert any("{A.full.nom}" in text for text in texts)
    assert not any("[[person:" in text and "Photo training" in text for text in texts)


def _layout_texts(template: Template) -> list[str]:
    layout = template.layout
    texts = [layout.letterhead, layout.footer]
    for block in layout.blocks:
        if isinstance(block, Table):
            texts += [*block.columns, *(cell for row in block.rows for cell in row)]
        elif isinstance(block, Boxes):
            texts += [text for pair in block.fields for text in pair]
        elif isinstance(block, Handwritten):
            texts += [block.label, block.text]
        elif isinstance(block, Signature):
            texts.append(block.label)
        elif isinstance(block, Stamp):
            texts += list(block.lines)
    return texts


@pytest.mark.parametrize("language", ["cs", "sk"])
def test_no_template_shares_a_phrase_with_the_test_data(language: str):
    other = set().union(*(_grams(line) for text in _other_texts() for line in text.split("\n")))
    for template in TEMPLATES[language]:
        for line in [*template.lines, *_layout_texts(template)]:
            shared = _grams(line) & other
            assert not shared, (template.name, sorted(shared)[:3])


def test_slots_read_as_placeholders():
    assert _grams("Montáž vykonal {M.full.nom} spolu {s~N.full.ins} {doc.place}") == {
        ("montáž", "vykonal", "□", "spolu", "□"),
        ("vykonal", "□", "spolu", "□", "□"),
    }


# --- Rendering -------------------------------------------------------------------


def test_render_split_writes_pdfs_gold_and_for_print_the_pack(tmp_path):
    gold_path = render_split(tmp_path / "print", split="print")
    gold = json.loads(gold_path.read_text(encoding="utf-8"))
    assert len(gold) == 2 * PRINT_PER_LANGUAGE
    assert all(entry["pages"] == 1 and entry["gold"] for entry in gold)
    with pymupdf.open(tmp_path / "print" / "rq8-train-print.pdf") as pack:
        assert pack.page_count == sum(entry["pages"] for entry in gold)
    manifest = (tmp_path / "print" / "manifest-train.md").read_text(encoding="utf-8")
    assert f"| 1 | {gold[0]['name']} | 1 |" in manifest
    assert f"{len(gold)} pages" in manifest
    with pytest.raises(ValueError, match="fixed"):
        render_split(tmp_path / "again", split="print", count=2)


def test_the_command_renders_a_synthetic_split(tmp_path, capsys):
    assert (
        main(["photo-train", "--out", str(tmp_path), "--split", "synthetic", "--count", "1"]) == 0
    )
    assert "gold.json" in capsys.readouterr().out
    assert sorted(path.name for path in (tmp_path / "pdf").iterdir()) == [
        "cs-s00001-loan.pdf",
        "sk-s00001-loan.pdf",
    ]
    assert not (tmp_path / "rq8-train-print.pdf").exists()
    with pytest.raises(SystemExit):
        main(["photo-train", "--out", str(tmp_path), "--count", "2"])
