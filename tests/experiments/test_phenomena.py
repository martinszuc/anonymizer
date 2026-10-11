"""Recall per tag of the gold spans, and its tables, on hand-made text and on the name-forms set."""

import json
from pathlib import Path

from anonymizer.core.types import DetectionSource, Entity, EntityType, ReviewState

from experiments import phenomena
from experiments.__main__ import main
from experiments.datasets import DatasetSpec, Role, Sentence, SourceSpan, build_corpus
from experiments.metrics import resamples
from experiments.name_forms import NAMES
from experiments.phenomena import PhenomenonTally

FULL = (("form", "full"), ("case", "nom"), ("form-case", "full/nom"))
TITLED = (("form", "title-surname"), ("case", "nom"), ("form-case", "title-surname/nom"))
TEXT = "Volal pan Novák a Jana Nováková."


def _corpus():
    spec = DatasetSpec(
        id="tagged",
        language="cs",
        types=frozenset({EntityType.PERSON}),
        splits={"dev": Role.DEV},
        read=lambda *_: [],
        generated="0",
    )
    novak, jana = TEXT.index("Novák"), TEXT.index("Jana Nováková")
    groups = [
        [
            Sentence(
                TEXT,
                (
                    SourceSpan(EntityType.PERSON, novak, novak + 5, TITLED),
                    SourceSpan(EntityType.PERSON, jana, jana + 13, FULL),
                ),
            )
        ],
        [Sentence("Kupující platí včas.")],
    ]
    return build_corpus(spec, "dev", "0", groups)


def _person(text: str, value: str) -> Entity:
    start = text.index(value)
    return Entity(
        type=EntityType.PERSON,
        page_index=0,
        start=start,
        end=start + len(value),
        text=value,
        source=DetectionSource.MODEL,
        review=ReviewState.PENDING,
    )


def test_recall_per_tag_and_false_alarms_in_texts_naming_nobody():
    corpus = _corpus()
    assert corpus.tagged
    tally = PhenomenonTally(corpus)
    types = frozenset({EntityType.PERSON})
    named, nobody = corpus.documents
    tally.add([_person(TEXT, "Jana")], named, types)
    tally.add([_person("Kupující platí včas.", "Kupující")], nobody, types)
    results = tally.results(resamples(2, 20, seed=1))

    partial, strict = results["recall"]["partial"], results["recall"]["strict"]
    assert partial["form"]["full"] == {
        "gold": 1,
        "found": 1,
        "recall": partial["form"]["full"]["recall"],
    }
    assert partial["form"]["full"]["recall"]["value"] == 1.0
    assert partial["form"]["title-surname"]["found"] == 0
    assert partial["case"]["nom"]["gold"] == 2
    assert partial["case"]["nom"]["found"] == 1
    assert strict["form"]["full"]["found"] == 0  # "Jana" alone leaves the surname
    assert results["control"] == {"texts": 1, "flagged": 1, "predictions": 1}


def test_tables_come_from_the_results_alone():
    corpus = _corpus()
    tally = PhenomenonTally(corpus)
    for gold in corpus.documents:
        tally.add([], gold, frozenset({EntityType.PERSON}))
    results = {
        "name": "tagged",
        "corpora": {
            "tagged/dev": {"systems": {"rules": {"phenomena": tally.results([[0, 1]])}}},
            "untagged/dev": {"systems": {"rules": {}}},
        },
    }
    text = phenomena.markdown(results)
    assert "## tagged/dev · recall by name form" in text
    assert "| form | full | 1 | 0 · 0.000 [0.00, 0.00] |" in text
    assert "| form / case | title-surname/nom | 1 |" in text
    assert "untagged" not in text
    assert "Texts naming nobody: 1. False alarms in them: rules in 0 (0 spans)." in text
    tex = phenomena.latex(results)
    assert "\\label{tab:tagged-tagged-dev-forms-partial}" in tex
    assert "0~$\\cdot$~0.000 \\ci{0.00}{0.00}" in tex
    assert phenomena.markdown({"name": "plain", "corpora": {}}) == ""


def test_a_run_on_the_name_forms_set_writes_the_tables(tmp_path: Path):
    config = tmp_path / "forms.toml"
    config.write_text(
        'name = "forms"\nseed = 3\nresamples = 20\n'
        '[[datasets]]\nid = "name-forms-sk"\nsplit = "dev"\n[systems.rules]\n',
        encoding="utf-8",
    )
    out = tmp_path / "results"
    root = ["--resource-root", str(tmp_path / "empty")]
    assert main(["run", "--config", str(config), "--out", str(out), *root]) == 0
    stored = json.loads((out / "forms.json").read_text(encoding="utf-8"))
    corpus = stored["corpora"]["name-forms-sk/dev"]
    assert stored["datasets"] == {"name-forms-sk": "1"}
    rules = corpus["systems"]["rules"]["phenomena"]
    assert rules["recall"]["partial"]["form"]["full"]["gold"] > 0
    assert rules["control"]["texts"] == 4
    written = (out / "forms.md").read_text(encoding="utf-8")
    assert "## name-forms-sk/dev · recall by name form" in written
    tex = (out / "forms.tex").read_text(encoding="utf-8")
    assert "forms-name-forms-sk-dev-forms-strict" in tex
    lists = NAMES["sk"]["dev"]
    names = {name.word for name in (*lists.male_first, *lists.female_first, *lists.surnames)}
    everything = json.dumps(stored, ensure_ascii=False) + written + tex
    assert not [name for name in names if name in everything]
