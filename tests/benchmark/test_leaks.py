"""The leak comparison: three redaction methods, counted on the files they save."""

import json
from pathlib import Path

import pymupdf
import pytest
from anonymizer.core.ingest import load_document
from anonymizer.core.redact import export_redacted
from anonymizer.core.redact.leakage import Leak, LeakLayer
from anonymizer.core.types import EntityType

from benchmark.__main__ import main
from benchmark.leaks import (
    CANARIES,
    apply_oracle,
    compare_pdf,
    count_extractable,
    plant_canaries,
    run_leaks,
    tool,
)
from benchmark.spec import DocumentSpec, GoldItem
from tests.pdf_builders import write_pdf

NAME = "Jan Novak"
EMAIL = "jan.novak@example.com"
STRUCTURE, OFF_PAGE = CANARIES
SPEC = DocumentSpec(
    name="tiny",
    language="en",
    kind="letter",
    lines=(f"Contact {NAME} at {EMAIL}.", "Thank you for your order."),
    metadata={"Title": f"Letter to {NAME}"},
    gold=(
        GoldItem(EntityType.PERSON, NAME, "page"),
        GoldItem(EntityType.EMAIL, EMAIL, "page"),
        GoldItem(EntityType.PERSON, NAME, "metadata"),
    ),
)
PLANTED = DocumentSpec(
    name=SPEC.name,
    language=SPEC.language,
    kind=SPEC.kind,
    lines=SPEC.lines,
    gold=(*SPEC.gold, *CANARIES),
)


def _tiny_pdf(directory: Path) -> Path:
    """Write the document by `pdf_builders`, set its title, add the injected items."""
    plain = write_pdf(directory / "plain.pdf", [list(SPEC.lines)])
    with pymupdf.open(plain) as pdf:
        pdf.set_metadata({"title": SPEC.metadata["Title"]})
        pdf.save(directory / "tiny.pdf")
    plant_canaries(directory / "tiny.pdf")
    return directory / "tiny.pdf"


def _left(result: dict, method: str) -> dict[tuple[str, str], bool]:
    return {
        (item["carrier"], item["text"]): item["left"] for item in result["methods"][method]["items"]
    }


@pytest.fixture
def comparison(tmp_path: Path) -> dict:
    return compare_pdf(PLANTED, _tiny_pdf(tmp_path), tmp_path)


def test_a_rectangle_over_the_words_removes_nothing(comparison):
    left = _left(comparison, "overlay")
    assert all(left.values())
    assert len(left) == 5


def test_apply_redactions_clears_the_page_and_nothing_else(comparison):
    left = _left(comparison, "apply_redactions")
    assert not left["page", NAME]
    assert not left["page", EMAIL]
    assert left["metadata", NAME]
    assert left["structure", STRUCTURE.text]
    assert left["off_page", OFF_PAGE.text]


def test_the_tool_leaves_none_of_the_five(comparison):
    assert not any(_left(comparison, "tool").values())
    assert comparison["methods"]["tool"]["refused"] is False
    assert comparison["unlocated"] == 0


def test_the_leak_check_flags_the_naive_copies_and_passes_the_tools(comparison):
    layers = {
        method: comparison["methods"][method]["leak_layers"] for method in comparison["methods"]
    }
    assert layers["tool"] == {}
    assert layers["overlay"]["page_text"] >= 2
    assert "page_text" not in layers["apply_redactions"]
    assert {"surface", "off_page_text"} <= set(layers["apply_redactions"])


def test_the_count_reads_the_saved_file_and_not_the_tools_claim(tmp_path):
    source = _tiny_pdf(tmp_path)
    original = load_document(source, language="en")
    apply_oracle(PLANTED, original)
    exported, refused = tool(source, original, tmp_path / "tiny.tool.pdf")
    assert not refused
    assert not any(item["left"] for item in count_extractable(PLANTED, original, exported).items)

    # The export passed its own check. Put a name back afterwards, in a place the
    # export had cleared and one it had cleaned: the count must see both.
    with pymupdf.open(exported) as pdf:
        pdf.set_metadata({"title": f"Letter to {NAME}"})
        pdf[0].insert_text((10, 2000), OFF_PAGE.text, fontname="helv", fontsize=9)
        pdf.save(tmp_path / "tampered.pdf")
    recount = count_extractable(PLANTED, original, tmp_path / "tampered.pdf")
    left = {(item["carrier"], item["text"]) for item in recount.items if item["left"]}
    assert left == {("metadata", NAME), ("off_page", OFF_PAGE.text)}


def test_a_refused_copy_is_counted_from_an_unchecked_copy(tmp_path, monkeypatch):
    source = _tiny_pdf(tmp_path)
    original = load_document(source, language="en")
    apply_oracle(PLANTED, original)
    calls: list[bool] = []

    def refuse_once(source, document, destination, *, check=True):
        calls.append(check)
        if check:
            return [Leak(LeakLayer.PAGE_TEXT, "page 0", NAME)]
        return export_redacted(source, document, destination, check=False)

    monkeypatch.setattr("benchmark.leaks.export_redacted", refuse_once)
    path, refused = tool(source, original, tmp_path / "tiny.tool.pdf")
    assert refused
    assert calls == [True, False]
    assert path.exists()
    assert not (tmp_path / "tiny.tool.pdf").exists()


def test_an_item_the_oracle_cannot_place_stays_and_is_reported(tmp_path):
    missing = DocumentSpec(
        name="tiny",
        language="en",
        kind="letter",
        lines=SPEC.lines,
        gold=(*PLANTED.gold, GoldItem(EntityType.PERSON, "Eva Absent", "page")),
    )
    result = compare_pdf(missing, _tiny_pdf(tmp_path), tmp_path)
    assert result["unlocated"] == 1
    assert not _left(result, "tool")["page", NAME]


def test_a_run_writes_the_tables(tmp_path):
    results = run_leaks(tmp_path, specs=[SPEC])
    totals = results["totals"]
    assert totals["items"] == 5
    assert totals["items_by_carrier"] == {
        "page": 2,
        "metadata": 1,
        "structure": 1,
        "off_page": 1,
    }
    assert totals["methods"]["overlay"]["extractable"] == 5
    assert totals["methods"]["apply_redactions"]["extractable_by_carrier"] == {
        "metadata": 1,
        "structure": 1,
        "off_page": 1,
    }
    assert totals["methods"]["tool"]["clean_documents"] == 1
    assert json.loads((tmp_path / "leaks.json").read_text(encoding="utf-8"))["totals"] == totals

    report = (tmp_path / "leaks.md").read_text(encoding="utf-8")
    assert "| page | 2 | 2/2 | 0/2 | 0/2 |" in report
    assert "| all | 5 | 5/5 | 3/5 | 0/5 |" in report
    table = (tmp_path / "leaks.tex").read_text(encoding="utf-8")
    assert "\\toprule" in table
    assert "off\\_page & 1 & 1 & 1 & 0" in table
    assert "all & 5 & 5 & 3 & 0" in table
    assert (tmp_path / "pdf" / "tiny.tool.pdf").exists()


def test_the_command_runs_chosen_documents(tmp_path, capsys):
    assert main(["leaks", "--out", str(tmp_path), "--documents", "cs-email"]) == 0
    assert "## Items still extractable, per carrier" in capsys.readouterr().out
    assert json.loads((tmp_path / "leaks.json").read_text(encoding="utf-8"))[
        "documents"
    ].keys() == {"cs-email"}


def test_an_unknown_document_is_refused(tmp_path):
    with pytest.raises(ValueError, match="no such document: nope"):
        run_leaks(tmp_path, names=("nope",))
