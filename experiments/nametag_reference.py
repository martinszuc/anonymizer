r"""Checks that `core.detect.nametag_model` tags as upstream NameTag 3 does.

The project runs NameTag 3's released models without Keras. This script shows
the reimplementation is faithful: both tag the same synthetic sentences (the
benchmark's documents, cut by the model's own UDPipe tokenizer) and the labels
are compared token by token, and as entities after NameTag's postprocessing.

    # 1. sentences and a model directory upstream can load offline
    uv run python -m experiments.nametag_reference export \\
        --model nametag3-czech-cnec2.0-240830 --out outputs/nametag-reference/cs
    # 2. upstream, in its own environment (requirements.txt of github.com/ufal/nametag3)
    HF_HUB_OFFLINE=1 /path/to/venv/bin/python nametag3.py \\
        --load_checkpoint=outputs/nametag-reference/cs/model \\
        --test_data=outputs/nametag-reference/cs/sentences.conll \\
        --logdir=outputs/nametag-reference/cs/logs > outputs/nametag-reference/cs/upstream.conll
    # 3. the comparison: counts only
    uv run python -m experiments.nametag_reference compare \\
        --model nametag3-czech-cnec2.0-240830 --out outputs/nametag-reference/cs

`export` writes one `-DOCSTART-` block per benchmark document, so a model
trained on documents packs the same sentences together on both sides. The
model directory links the released files and the encoder's tokenizer and
config, which the released archives lack, so upstream loads it without the
network. The output directory holds synthetic text only; it stays out of git.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from anonymizer.core.detect.gliner import encoder_resource
from anonymizer.core.detect.nametag import (
    Label,
    UDPipeSplitter,
    load_nametag_tagger,
    model_directory,
    tagged_entities,
)
from anonymizer.core.resources import load_catalog, resolve_resource_root

from benchmark.spec import load_documents, visible_text

DOCSTART = "-DOCSTART-"

Document = list[list[str]]
"""Sentences of token forms."""


def export(model_id: str, out: Path, resource_root: Path) -> dict[str, int]:
    """Write the sentences and an offline-loadable model directory for upstream.

    Returns:
        Documents, sentences and tokens written.
    """
    catalog = load_catalog()
    source = model_directory(resource_root, model_id, catalog)
    encoder = catalog[encoder_resource(catalog, model_id)].directory(resource_root)
    model = out / "model"
    model.mkdir(parents=True, exist_ok=True)
    for directory in (source, encoder):
        for path in directory.iterdir():
            link = model / path.name
            if path.is_file() and not link.exists():
                link.symlink_to(path.resolve())
    splitter = UDPipeSplitter(source / "udpipe.tokenizer")
    documents = [
        [
            [token.form for token in sentence]
            for sentence in splitter.sentences("\n".join(visible_text(spec)))
        ]
        for spec in load_documents()
    ]
    lines: list[str] = []
    for document in documents:
        lines += [f"{DOCSTART}\tO", ""]
        for sentence in document:
            lines += [f"{form}\tO" for form in sentence]
            lines.append("")
    (out / "sentences.conll").write_text("\n".join(lines), encoding="utf-8")
    return {
        "documents": len(documents),
        "sentences": sum(len(document) for document in documents),
        "tokens": sum(len(sentence) for document in documents for sentence in document),
    }


def read_conll(path: Path) -> list[list[list[tuple[str, str]]]]:
    """Return documents of sentences of `(form, labels)` from a vertical file."""
    documents: list[list[list[tuple[str, str]]]] = []
    sentence: list[tuple[str, str]] = []
    for line in [*path.read_text(encoding="utf-8").splitlines(), ""]:
        if not line:
            if sentence:
                if not documents:
                    documents.append([])
                documents[-1].append(sentence)
            sentence = []
            continue
        form, labels = line.split("\t")
        if form == DOCSTART:
            documents.append([])
            continue
        sentence.append((form, labels))
    return documents


def upstream_labels(labels: str) -> list[Label]:
    """Read upstream's `B-P|B-pf` as our tagger names labels: stopped at `O`, no scores."""
    named: list[Label] = []
    for label in labels.split("|"):
        if label == "O":
            break
        named.append((label, 1.0))
    return named


def compare(model_id: str, out: Path, resource_root: Path) -> dict[str, int]:
    """Tag the exported sentences with the project's tagger and count differences from upstream.

    Returns:
        Token and entity counts: compared, equal, and found by one side only.

    Raises:
        ValueError: If the two files do not hold the same tokens.
    """
    catalog = load_catalog()
    tagger = load_nametag_tagger(
        model_directory(resource_root, model_id, catalog),
        catalog[encoder_resource(catalog, model_id)].directory(resource_root),
    )
    exported = read_conll(out / "sentences.conll")
    upstream = read_conll(out / "upstream.conll")
    if [[[form for form, _ in s] for s in d] for d in exported] != [
        [[form for form, _ in s] for s in d] for d in upstream
    ]:
        msg = "upstream output does not hold the exported tokens"
        raise ValueError(msg)
    counts: dict[str, int] = dict.fromkeys(
        ("tokens", "tokens_equal", "entities_both", "entities_ours_only", "entities_upstream_only"),
        0,
    )
    for document in upstream:
        ours = tagger.tag([[form for form, _ in sentence] for sentence in document])
        for sentence, our_labels in zip(document, ours, strict=True):
            theirs = [upstream_labels(labels) for _, labels in sentence]
            counts["tokens"] += len(sentence)
            counts["tokens_equal"] += sum(
                _names(mine) == _names(other)
                for mine, other in zip(our_labels, theirs, strict=True)
            )
            mine_entities = _entities(our_labels)
            their_entities = _entities(theirs)
            counts["entities_both"] += len(mine_entities & their_entities)
            counts["entities_ours_only"] += len(mine_entities - their_entities)
            counts["entities_upstream_only"] += len(their_entities - mine_entities)
    return counts


def _names(labels: Sequence[Label]) -> list[str]:
    return [label for label, _ in labels]


def _entities(labels: Sequence[Sequence[Label]]) -> set[tuple[str, int, int]]:
    return {(entity.label, entity.first, entity.last) for entity in tagged_entities(labels)}


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(prog="experiments.nametag_reference", description=__doc__)
    parser.add_argument("command", choices=("export", "compare"))
    parser.add_argument("--model", required=True, help="catalog id of a NameTag 3 model")
    parser.add_argument("--out", type=Path, required=True, help="work directory, outside git")
    parser.add_argument("--resource-root", type=Path, help="directory holding models/")
    args = parser.parse_args(argv)
    root = resolve_resource_root(args.resource_root)
    action = export if args.command == "export" else compare
    print(json.dumps(action(args.model, args.out, root), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
