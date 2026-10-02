"""Evaluation corpora as documents of the shared data contract, with gold spans.

A loader turns one split of a corpus into `GoldDocument`s: a `Document` whose
pages hold the text, as ingest would hand it to detection, and the gold spans
as `Entity` objects of our `EntityType`s. Only the types a corpus annotates
are scored on it (`Corpus.types`): CNEC marks no birth numbers, so a birth
number found in it is neither right nor wrong.

Sentence corpora are cut into page-like texts of `SENTENCES_PER_PAGE`
sentences, one sentence per line, because detection runs on pages and the
name model reads a page in windows. Words get made-up boxes in reading order;
nothing here is ever rendered, but the pipeline resolves geometry.

Type mappings (source → ours); everything else is counted in
`Corpus.unmapped` and not scored:

CNEC 2.0 (plain format, nested `<type ...>` markup, tokens split by spaces)
    person   `P` containers with no `P` above them, and `pf`, `ps`, `pm`,
             `p_` outside any `P` (a first name alone, a surname alone).
             Not `pc` (inhabitants: "Pražané"), `pp` (religious and
             mythological persons), `pd` (a title on its own).
    address  `A` containers with no `A` above them.
    phone    `at` (telephone and fax numbers).
    email    `me`.
    url      `mi`.

UNER Slovak-SNK (IOB2; the sentence's own text is used where its tokens
align with it, so punctuation sits where the writer put it)
    person   `PER`. `LOC` and `ORG` are not personal data on their own.

REDACT (synthetic records; Czech records only, as the corpus has no Slovak)
    person        Full_Name, First_Given_Name, Last_Family_Name
    email         Work_Email_Address, Personal_Email_Address
    phone         Telephone_Numbers_Personal, Telephone_Numbers_Work
    address       Address_Personal, Address_Work
    date          Date_of_Birth (our date type is only ever a date of birth)
    birth_number  National_Identification_Number: in Czech records the
                  national number is the rodné číslo; a few are 8 to 9 digit
                  card numbers no rule knows, which counts against recall.
    id_number     Passport_Number, Driving_License_Number
    Not mapped: Credit_Card_Numbers (in the Czech records only the last four
    digits, which identify nothing alone), Account_Statements (statement text,
    not account numbers), customer, employee and tax references, IP
    addresses, social media handles, places, organisations, dates other than
    of birth, and the special categories (health, religion, ...), which have
    no type of ours.

Spans of one type nested in another of the same type are reduced to the
outermost (REDACT marks a full name and its first name), so a detector is not
asked to find a name twice.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from anonymizer.core.resources import load_catalog
from anonymizer.core.types import (
    BBox,
    DetectionSource,
    Document,
    Entity,
    EntityType,
    Page,
    ReviewState,
    Word,
)

SENTENCES_PER_PAGE = 12
"""Sentences per page-like text: about a page of prose (~250 words)."""


class TextForm(StrEnum):
    """How a sentence corpus becomes page text.

    `written`: each sentence as its writer punctuated it, where the corpus
    keeps that (UNER's `# text`), and pages grouped by source document.
    `tokens`: tokens joined by spaces and every `SENTENCES_PER_PAGE`
    sentences a document of their own, regardless of source documents: how
    the 2026-10-02 sweep built its texts. CNEC and REDACT read the same
    either way (CNEC keeps only tokens, REDACT whole records).
    """

    WRITTEN = "written"
    TOKENS = "tokens"


class Role(StrEnum):
    """What a split may be used for (tuning happens on dev only)."""

    TRAIN = "train"
    DEV = "dev"
    TEST = "test"


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """A gold span in a sentence, already mapped to our type.

    Attributes:
        type: Our entity type.
        start: First offset in the sentence text.
        end: Offset one past the span.
    """

    type: EntityType
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class Sentence:
    """A sentence's text with its gold spans and the source types left unmapped."""

    text: str
    spans: tuple[SourceSpan, ...] = ()
    unmapped: tuple[str, ...] = ()


@dataclass(slots=True)
class GoldDocument:
    """A document to run detection on, with the spans it should find.

    Attributes:
        name: Position in the corpus (`<dataset>/<split>/<number>`), never text.
        document: Pages with text; `entities` is what a system last found.
        gold: The expected spans, page-local, in our types.
    """

    name: str
    document: Document
    gold: list[Entity]


@dataclass(slots=True)
class Corpus:
    """One split of a dataset, ready to score.

    Attributes:
        dataset: Catalog id.
        version: The catalog's pinned version of the dataset.
        split: Split name as the source calls it.
        role: What the split may be used for.
        language: BCP 47 tag of the text.
        text_form: How the page text was built.
        types: Types the corpus annotates; only these are scored.
        documents: The documents with their gold spans.
        sentences: Sentences (or records) read.
        unmapped: Source types read but not scored, with counts.
        skipped: Gold spans dropped because they did not match the text.
    """

    dataset: str
    version: str
    split: str
    role: Role
    language: str
    text_form: TextForm
    types: frozenset[EntityType]
    documents: list[GoldDocument]
    sentences: int = 0
    unmapped: Counter[str] = field(default_factory=Counter)
    skipped: int = 0

    @property
    def key(self) -> str:
        """`<dataset>/<split>`, the corpus's name in results, `+tokens` when so built."""
        suffix = "" if self.text_form is TextForm.WRITTEN else f"+{self.text_form}"
        return f"{self.dataset}/{self.split}{suffix}"

    def gold_counts(self) -> dict[str, int]:
        """Return the number of gold spans per type."""
        counts = Counter(str(entity.type) for doc in self.documents for entity in doc.gold)
        return dict(sorted(counts.items()))


@dataclass(frozen=True, slots=True)
class DatasetSpec:
    """How to read one dataset.

    Attributes:
        id: Catalog id.
        language: Language of the text.
        types: Types the corpus annotates.
        splits: Split name → role.
        read: Reads a split from the dataset directory, in a text form.
    """

    id: str
    language: str
    types: frozenset[EntityType]
    splits: dict[str, Role]
    read: Callable[[Path, str, TextForm], list[list[Sentence]]]


# --- CNEC 2.0 ---------------------------------------------------------------

_CNEC_TAG = re.compile(r"<([A-Za-z_?]+) ?")
_CNEC_PERSON_PARTS = frozenset({"pf", "ps", "pm", "p_"})
_CNEC_CONTAINERS = _CNEC_PERSON_PARTS | {"P", "A"}
_CNEC_TYPES = {"at": EntityType.PHONE, "me": EntityType.EMAIL, "mi": EntityType.URL}


@dataclass(frozen=True, slots=True)
class _Tagged:
    type: str
    first: int
    last: int
    ancestors: tuple[str, ...]


def parse_cnec_line(line: str) -> Sentence:
    """Parse one sentence of CNEC's plain format.

    Every `<` opens an entity (`<type ` or `<type<`) and every `>` closes the
    innermost one; the corpus has no literal brackets (`&lt;` stands for one).

    Args:
        line: One line of `named_ent_*.txt`.

    Returns:
        The sentence, its tokens joined by single spaces, with mapped spans.

    Raises:
        ValueError: If the brackets do not balance.
    """
    tokens: list[str] = []
    tagged: list[_Tagged] = []
    open_tags: list[tuple[str, int]] = []
    position = 0
    while position < len(line):
        char = line[position]
        if char == "<":
            found = _CNEC_TAG.match(line, position)
            if found is None:
                msg = f"unreadable tag at offset {position}"
                raise ValueError(msg)
            open_tags.append((found.group(1), len(tokens)))
            position = found.end()
        elif char == ">":
            if not open_tags:
                msg = f"unbalanced '>' at offset {position}"
                raise ValueError(msg)
            kind, first = open_tags.pop()
            ancestors = tuple(name for name, _ in open_tags)
            tagged.append(_Tagged(kind, first, len(tokens), ancestors))
            position += 1
        elif char.isspace():
            position += 1
        else:
            end = position
            while end < len(line) and not line[end].isspace() and line[end] not in "<>":
                end += 1
            tokens.append(html.unescape(line[position:end]))
            position = end
    if open_tags:
        msg = "unclosed entity"
        raise ValueError(msg)
    return _cnec_sentence(tokens, tagged)


def _cnec_sentence(tokens: list[str], tagged: list[_Tagged]) -> Sentence:
    starts: list[int] = []
    offset = 0
    for token in tokens:
        starts.append(offset)
        offset += len(token) + 1
    spans: list[SourceSpan] = []
    unmapped: list[str] = []
    for entity in tagged:
        if entity.first == entity.last:
            continue
        kind = _cnec_type(entity)
        if kind is None:
            # Name parts inside a name, and addresses inside an address, are
            # covered by the outer span rather than left out.
            if not _cnec_covered(entity):
                unmapped.append(entity.type)
            continue
        start = starts[entity.first]
        end = starts[entity.last - 1] + len(tokens[entity.last - 1])
        spans.append(SourceSpan(kind, start, end))
    return Sentence(" ".join(tokens), tuple(spans), tuple(unmapped))


def _cnec_covered(entity: _Tagged) -> bool:
    """Whether a span lies in (or is) a name or an address that is scored as a whole."""
    return entity.type in _CNEC_CONTAINERS or bool(_CNEC_CONTAINERS & set(entity.ancestors))


def _cnec_type(entity: _Tagged) -> EntityType | None:
    if entity.type == "P":
        return None if "P" in entity.ancestors else EntityType.PERSON
    if entity.type in _CNEC_PERSON_PARTS:
        inside_name = any(name == "P" or name in _CNEC_PERSON_PARTS for name in entity.ancestors)
        return None if inside_name else EntityType.PERSON
    if entity.type == "A":
        return None if "A" in entity.ancestors else EntityType.ADDRESS
    return _CNEC_TYPES.get(entity.type)


def read_cnec(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:  # noqa: ARG001
    """Read a CNEC split; each page-like chunk of sentences is a document of its own.

    CNEC's sentences come from unrelated sources, so there is no document to
    keep together.
    """
    path = directory / "Czech_Named_Entity_Corpus_2.0" / "cnec2.0" / "data" / "plain"
    text = (path / f"named_ent_{split}.txt").read_text(encoding="utf-8")
    sentences = [parse_cnec_line(line) for line in text.splitlines() if line.strip()]
    return [[*chunk] for chunk in _chunks(sentences, SENTENCES_PER_PAGE)]


# --- UNER -------------------------------------------------------------------


def parse_iob2(text: str, form: TextForm = TextForm.WRITTEN) -> list[list[Sentence]]:
    """Parse a Universal NER IOB2 file into documents of sentences.

    Columns: token id, token, tag. `# newdoc` starts a document, `# text =`
    gives the sentence as written; the tokens are placed in it where they
    align, and joined by spaces where they do not.

    Args:
        text: Contents of a `.iob2` file.
        form: `tokens` ignores `# text` and the document boundaries.

    Returns:
        Documents, each a list of sentences with `PER` spans as persons.
    """
    written = form is TextForm.WRITTEN
    documents: list[list[Sentence]] = [[]]
    sentence_text: str | None = None
    rows: list[tuple[str, str]] = []

    def finish() -> None:
        nonlocal sentence_text, rows
        if rows:
            documents[-1].append(_iob2_sentence(rows, sentence_text))
        sentence_text, rows = None, []

    for line in text.splitlines():
        if not line.strip():
            finish()
        elif line.startswith("#"):
            if line.startswith("# newdoc") and documents[-1]:
                finish()
                documents.append([])
            elif line.startswith("# text = ") and written:
                sentence_text = line[len("# text = ") :]
        else:
            columns = line.split("\t")
            rows.append((columns[1], columns[2]))
    finish()
    if not written:
        sentences = [sentence for document in documents for sentence in document]
        return [*_chunks(sentences, SENTENCES_PER_PAGE)]
    return [document for document in documents if document]


def _iob2_sentence(rows: list[tuple[str, str]], written: str | None) -> Sentence:
    tokens = [token for token, _ in rows]
    text, starts = _place_tokens(tokens, written)
    spans: list[SourceSpan] = []
    unmapped: list[str] = []
    current: tuple[str, int, int] | None = None  # label, first token, last token

    def close() -> None:
        if current is None:
            return
        label, first, last = current
        if label == "PER":
            spans.append(
                SourceSpan(EntityType.PERSON, starts[first], starts[last] + len(tokens[last]))
            )
        else:
            unmapped.append(label)

    for index, (_, tag) in enumerate(rows):
        prefix, _, label = tag.partition("-")
        if prefix == "I" and current is not None and current[0] == label:
            current = (label, current[1], index)
            continue
        close()
        current = (label, index, index) if prefix in {"B", "I"} else None
    close()
    return Sentence(text, tuple(spans), tuple(unmapped))


def _place_tokens(tokens: list[str], written: str | None) -> tuple[str, list[int]]:
    """Return the sentence text and each token's offset in it."""
    if written is not None:
        starts: list[int] = []
        position = 0
        for token in tokens:
            found = written.find(token, position)
            if found < 0 or written[position:found].strip():
                break
            starts.append(found)
            position = found + len(token)
        else:
            return written, starts
    starts = []
    offset = 0
    for token in tokens:
        starts.append(offset)
        offset += len(token) + 1
    return " ".join(tokens), starts


def read_uner(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:
    """Read a UNER Slovak-SNK split (see `TextForm` for the two ways)."""
    return parse_iob2((directory / f"sk_snk-ud-{split}.iob2").read_text(encoding="utf-8"), form)


# --- REDACT -----------------------------------------------------------------

REDACT_TYPES: dict[str, EntityType] = {
    "Full_Name": EntityType.PERSON,
    "First_Given_Name": EntityType.PERSON,
    "Last_Family_Name": EntityType.PERSON,
    "Work_Email_Address": EntityType.EMAIL,
    "Personal_Email_Address": EntityType.EMAIL,
    "Telephone_Numbers_Personal": EntityType.PHONE,
    "Telephone_Numbers_Work": EntityType.PHONE,
    "Address_Personal": EntityType.ADDRESS,
    "Address_Work": EntityType.ADDRESS,
    "Date_of_Birth": EntityType.DATE,
    "National_Identification_Number": EntityType.BIRTH_NUMBER,
    "Passport_Number": EntityType.ID_NUMBER,
    "Driving_License_Number": EntityType.ID_NUMBER,
}
"""REDACT type → ours (see the module docstring for what is left out and why)."""

REDACT_FILE = "pii_benchmark_sample1000.json"
_REDACT_LANGUAGE = "CS"
_SKIPPED = "(span not in text)"


def parse_redact(records: list[dict[str, object]], language: str) -> list[list[Sentence]]:
    """Turn REDACT records of one language into one-record documents.

    The record text is normalised to NFC with the gold offsets moved along;
    a span whose offsets do not cut out its own string is dropped and counted
    under `(span not in text)`.

    Args:
        records: The parsed JSON list.
        language: REDACT's language code, e.g. `CS`.

    Returns:
        One document per record, holding the record as a single "sentence".
    """
    documents: list[list[Sentence]] = []
    for record in records:
        axes = record.get("axes")
        if not isinstance(axes, dict) or axes.get("language") != language:
            continue
        raw = str(record["text"])
        spans: list[SourceSpan] = []
        unmapped: list[str] = []
        entities = record.get("entities")
        for entity in entities if isinstance(entities, list) else []:
            start, end = entity.get("start"), entity.get("end")
            if (
                not isinstance(start, int)
                or not isinstance(end, int)
                or end <= start
                or raw[start:end] != entity["entity_string"]
            ):
                unmapped.append(_SKIPPED)
                continue
            kind = REDACT_TYPES.get(str(entity["entity_type"]))
            if kind is None:
                unmapped.append(str(entity["entity_type"]))
                continue
            spans.append(SourceSpan(kind, _nfc_offset(raw, start), _nfc_offset(raw, end)))
        text = unicodedata.normalize("NFC", raw)
        documents.append([Sentence(text, tuple(spans), tuple(unmapped))])
    return documents


def _nfc_offset(text: str, offset: int) -> int:
    """Return where an offset into `text` lands once the text is NFC-normalised."""
    return len(unicodedata.normalize("NFC", text[:offset]))


def read_redact(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:  # noqa: ARG001
    """Read the Czech records of the REDACT sample."""
    if split != "sample":
        msg = f"REDACT has only the 'sample' split here, not {split!r}"
        raise ValueError(msg)
    records = json.loads((directory / REDACT_FILE).read_text(encoding="utf-8"))
    return parse_redact(records, _REDACT_LANGUAGE)


# --- Registry and assembly --------------------------------------------------

DATASETS: dict[str, DatasetSpec] = {
    "cnec-2.0": DatasetSpec(
        id="cnec-2.0",
        language="cs",
        types=frozenset(
            {
                EntityType.PERSON,
                EntityType.ADDRESS,
                EntityType.PHONE,
                EntityType.EMAIL,
                EntityType.URL,
            }
        ),
        splits={"train": Role.TRAIN, "dtest": Role.DEV, "etest": Role.TEST},
        read=read_cnec,
    ),
    "uner-sk-snk": DatasetSpec(
        id="uner-sk-snk",
        language="sk",
        types=frozenset({EntityType.PERSON}),
        splits={"train": Role.TRAIN, "dev": Role.DEV, "test": Role.TEST},
        read=read_uner,
    ),
    "redact": DatasetSpec(
        id="redact",
        language="cs",
        types=frozenset(REDACT_TYPES.values()),
        # The 1,000-record sample is all there is locally; anything measured
        # on it is development data, and the full file will hold the test.
        splits={"sample": Role.DEV},
        read=read_redact,
    ),
}


def load_corpus(
    dataset: str, split: str, resource_root: Path, form: TextForm = TextForm.WRITTEN
) -> Corpus:
    """Load one split of a catalogued dataset from the storage root.

    Args:
        dataset: Catalog id (see `DATASETS`).
        split: Split name as the source calls it.
        resource_root: Storage root holding `data/<id>/`.
        form: How sentences become page text.

    Returns:
        The corpus with its documents and gold spans.

    Raises:
        ValueError: If the dataset or split is unknown.
        FileNotFoundError: If the dataset is not stored under the root.
    """
    spec = DATASETS.get(dataset)
    if spec is None:
        msg = f"unknown dataset {dataset!r}; choose from {sorted(DATASETS)}"
        raise ValueError(msg)
    role = spec.splits.get(split)
    if role is None:
        msg = f"{dataset} has no split {split!r}; choose from {sorted(spec.splits)}"
        raise ValueError(msg)
    resource = load_catalog()[dataset]
    groups = spec.read(resource.directory(resource_root), split, form)
    return build_corpus(spec, split, resource.version, groups, form)


def build_corpus(
    spec: DatasetSpec,
    split: str,
    version: str,
    groups: list[list[Sentence]],
    form: TextForm = TextForm.WRITTEN,
) -> Corpus:
    """Assemble documents and gold spans from sentences grouped into documents.

    Args:
        spec: The dataset.
        split: Split name.
        version: Pinned dataset version.
        groups: Sentences per source document.
        form: How the sentences were turned into text, for the record.

    Returns:
        The corpus; a long document gets several pages.
    """
    corpus = Corpus(
        dataset=spec.id,
        version=version,
        split=split,
        role=spec.splits[split],
        language=spec.language,
        text_form=form,
        types=spec.types,
        documents=[],
    )
    for number, sentences in enumerate(groups):
        corpus.sentences += len(sentences)
        for sentence in sentences:
            corpus.unmapped.update(sentence.unmapped)
        name = f"{spec.id}/{split}/{number:04d}"
        corpus.documents.append(_gold_document(name, sentences, spec.language))
    corpus.skipped = corpus.unmapped.pop(_SKIPPED, 0)
    return corpus


def _gold_document(name: str, sentences: list[Sentence], language: str) -> GoldDocument:
    pages: list[Page] = []
    gold: list[Entity] = []
    for index, chunk in enumerate(_chunks(sentences, SENTENCES_PER_PAGE)):
        text = "\n".join(sentence.text for sentence in chunk)
        page = make_page(index, text)
        offset = 0
        page_gold: list[Entity] = []
        for sentence in chunk:
            for span in sentence.spans:
                start, end = offset + span.start, offset + span.end
                page_gold.append(
                    Entity(
                        type=span.type,
                        page_index=index,
                        start=start,
                        end=end,
                        text=text[start:end],
                        source=DetectionSource.MANUAL,
                        review=ReviewState.CONFIRMED,
                    )
                )
            offset += len(sentence.text) + 1
        pages.append(page)
        gold += outermost(page_gold)
    document = Document(pages=pages, language=language)
    return GoldDocument(name=name, document=document, gold=gold)


def outermost(spans: Iterable[Entity]) -> list[Entity]:
    """Drop spans lying inside another span of the same type on the same page.

    Exact duplicates are kept once.
    """
    ordered = sorted(spans, key=lambda entity: (entity.page_index, entity.span[0], -entity.span[1]))
    kept: list[Entity] = []
    for entity in ordered:
        start, end = entity.span
        inside = any(
            other.type is entity.type
            and other.page_index == entity.page_index
            and other.span[0] <= start
            and end <= other.span[1]
            for other in kept
        )
        if not inside:
            kept.append(entity)
    return kept


_LINE_HEIGHT = 14.0
_CHAR_WIDTH = 5.0
_WORD = re.compile(r"\S+")


def make_page(index: int, text: str) -> Page:
    """Build a page for text that was never laid out, with made-up word boxes.

    Each line of the text is a line on the page and each character five
    points wide, so boxes keep reading order and never overlap.

    Args:
        index: Page number.
        text: The page text.

    Returns:
        A page with one word per whitespace-separated token.
    """
    words: list[Word] = []
    line_start = 0
    widest = 0.0
    for line_number, line in enumerate(text.split("\n")):
        top = line_number * _LINE_HEIGHT
        for found in _WORD.finditer(line):
            box = BBox(
                found.start() * _CHAR_WIDTH,
                top,
                found.end() * _CHAR_WIDTH,
                top + _LINE_HEIGHT - 2,
            )
            words.append(
                Word(found.group(), box, line_start + found.start(), line_start + found.end())
            )
            widest = max(widest, box.x1)
        line_start += len(line) + 1
    lines = text.count("\n") + 1
    return Page(
        index=index,
        width=max(widest, 595.0),
        height=max(lines * _LINE_HEIGHT, 842.0),
        text=text,
        words=words,
    )


def _chunks(items: list[Sentence], size: int) -> Iterator[list[Sentence]]:
    for first in range(0, len(items), size):
        yield items[first : first + size]
