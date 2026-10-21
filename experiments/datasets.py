"""Evaluation corpora as documents of the shared data contract, with gold spans.

A loader turns one split of a corpus into `GoldDocument`s: a `Document` whose
pages hold the text, as ingest would hand it to detection, and the gold spans
as `Entity` objects of our `EntityType`s. Only the types a corpus annotates
are scored on it (`Corpus.types`): CNEC marks no birth numbers, so a birth
number found in it is neither right nor wrong. Organisations are kept in the
gold of the corpora that mark them but never scored (`DatasetSpec.unscored`):
they are what training teaches the name model's `organization` distractor.

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
    organization (not scored)  `ic`, `if`, `io`, `i_`: cultural, educational
             and scientific institutions, companies, government bodies, and
             institutions of no finer type. Not `ia` (conferences, contests).

UNER Slovak-SNK (IOB2; the sentence's own text is used where its tokens
align with it, so punctuation sits where the writer put it)
    person   `PER`. `LOC` is not personal data on its own.
    organization (not scored)  `ORG`.

WikiGoldSK (Slovak Wikipedia; `token tag` per line, IOB2, no document
boundaries, so tokens joined by spaces and cut into page-like chunks as CNEC)
    person   `PER`. Not `LOC` or `MISC`.
    organization (not scored)  `ORG`.
    Splits: the source's `train`, `dev` and `test`; `test` is reserved.

SlavicNER (BSNLP news, one language per dataset: `slavicner-cs`; every
mention with character offsets into the raw document; each non-empty line of
a document, a paragraph, is one "sentence", and pages follow documents)
    person   `PER`. Not `LOC`, `EVT` (events), `PRO` (products).
    organization (not scored)  `ORG`.
    Splits: the source's cross-topic split (`SPLIT_cross-topic_*.txt`, every
    topic in both parts): its `train` part is `train`, its `test` part,
    which the paper calls the tuning part, is `dev`. No test split.

The train splits of WikiGoldSK and SlavicNER may repeat text of another
corpus's dev or test split (Slovak Wikipedia is read by several corpora), so
a training config reading them must drop such text (`DatasetSpec.check_overlap`,
`overlap.py`).

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

OpenPII 1M (ai4privacy; synthetic records in 23 languages, one dataset per
language: `openpii-1m-cs`, `-sk`, `-en`)
    person   GIVENNAME and SURNAME, a run of them joined when only spaces lie
             between (no line break, no "a"/"and"): one name, as in CNEC.
             Not TITLE (CNEC leaves titles out too).
    address  STREET, BUILDINGNUM, ZIPCODE and CITY, a run of them joined when
             at most `OPENPII_ADDRESS_GAP` characters and no line break lie
             between (", ", " č. ", ", PSČ "). A run without a street or a
             postcode (a city alone, "born in Brno") is not an address.
    email    EMAIL.
    Not mapped: the identifiers (SOCIALNUM, IDCARDNUM, PASSPORTNUM,
    DRIVERLICENSENUM, TAXNUM, CREDITCARDNUMBER), because they are invented
    without their checksums: 184 of 1,522 Czech SOCIALNUMs in validation
    pass the rodné číslo rule (2026-10-10), so recall on them would measure
    the generator, and identifiers are the rules' job. TELEPHONENUM, for
    the same reason: the numbers follow no numbering plan (`+42008.128.8025`,
    `(48)-1071 6019`; 604 of 1,915 Czech dev numbers even start with the
    country code), and the phone rule found 8.7 % of them. DATE (ours is a
    date of birth only), AGE, SEX, GENDER, TITLE.
    Splits: `train` is the source's train split. The source has no test
    split, so its validation split is cut in two by a hash of the record's
    uid: `dev` for tuning, `test` reserved (`openpii_half`).

Name forms (`name-forms-cs`, `name-forms-sk`; generated by `name_forms.py`,
no files and no catalog entry: the version is the generator's)
    person   every name slot of a template. Each span carries tags (form,
             case, declension class, gender) that `phenomena.py` breaks
             recall down by. Splits: `dev` (dev) and `test` (test), with
             different names and templates.

Held-out synthetic set (`heldout-cs`, `heldout-sk`; generated by `heldout.py`
like the name-forms set, the final test's own synthetic set)
    person, address, email, phone, birth_number, date (of birth),
             bank_account, iban: every value slot of a template. Person spans
             carry tags as above, plus context and document kind. Splits:
             `dev` (dev) and `test` (test), with different names and
             templates; no train split, so training never reads it.

Spans of one type nested in another of the same type are reduced to the
outermost (REDACT marks a full name and its first name), so a detector is not
asked to find a name twice.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import unicodedata
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

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

from experiments import heldout
from experiments.name_forms import NAME_FORMS_VERSION, Tag, generate

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
        tags: What kind of span it is, for corpora that break recall down
            (`name_forms.Tag`); empty otherwise.
    """

    type: EntityType
    start: int
    end: int
    tags: tuple[Tag, ...] = ()


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
        tags: The tags of tagged gold spans, by page, start and end.
    """

    name: str
    document: Document
    gold: list[Entity]
    tags: dict[tuple[int, int, int], tuple[Tag, ...]] = field(default_factory=dict)


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
        excluded: Sentences left out because the loader was told to
            (`load_corpus(exclude=...)`), not counted in `sentences`.
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
    excluded: int = 0

    @property
    def key(self) -> str:
        """`<dataset>/<split>`, the corpus's name in results, `+tokens` when so built."""
        suffix = "" if self.text_form is TextForm.WRITTEN else f"+{self.text_form}"
        return f"{self.dataset}/{self.split}{suffix}"

    @property
    def tagged(self) -> bool:
        """Whether gold spans carry tags to break recall down by."""
        return any(gold.tags for gold in self.documents)

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
        types: Types the corpus annotates, and which are scored.
        splits: Split name → role.
        read: Reads a split from the dataset directory, in a text form.
        resource: Catalog id when it differs from `id` (one language of a
            multilingual resource).
        unscored: Types the corpus marks throughout but which are not
            personal data, so are kept in the gold for training only.
        generated: For a dataset generated in code rather than read from
            files, its generator's version; it has no catalog entry.
        check_overlap: Its train split may repeat text of a dev or test
            split, so a training config reading it must drop such text
            (`drop_overlap` in `train.py`).
    """

    id: str
    language: str
    types: frozenset[EntityType]
    splits: dict[str, Role]
    read: Callable[[Path, str, TextForm], list[list[Sentence]]]
    resource: str | None = None
    unscored: frozenset[EntityType] = frozenset()
    generated: str | None = None
    check_overlap: bool = False

    @property
    def catalog_id(self) -> str:
        """The catalog entry holding the files."""
        return self.resource or self.id


# --- CNEC 2.0 ---------------------------------------------------------------

_CNEC_TAG = re.compile(r"<([A-Za-z_?]+) ?")
_CNEC_PERSON_PARTS = frozenset({"pf", "ps", "pm", "p_"})
_CNEC_CONTAINERS = _CNEC_PERSON_PARTS | {"P", "A"}
_CNEC_TYPES = {"at": EntityType.PHONE, "me": EntityType.EMAIL, "mi": EntityType.URL}
_CNEC_ORGANIZATIONS = frozenset({"ic", "if", "io", "i_"})


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
    text, starts = _joined(tokens)
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
    return Sentence(text, tuple(spans), tuple(unmapped))


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
    if entity.type in _CNEC_ORGANIZATIONS:
        return EntityType.ORGANIZATION
    return _CNEC_TYPES.get(entity.type)


def read_cnec(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:  # noqa: ARG001
    """Read a CNEC split; each page-like chunk of sentences is a document of its own.

    CNEC's sentences come from unrelated sources, so there is no document to
    keep together.
    """
    path = directory / "Czech_Named_Entity_Corpus_2.0" / "cnec2.0" / "data" / "plain"
    text = (path / f"named_ent_{split}.txt").read_text(encoding="utf-8")
    sentences = [parse_cnec_line(line) for line in text.splitlines() if line.strip()]
    return list(_chunks(sentences, SENTENCES_PER_PAGE))


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
        return list(_chunks(sentences, SENTENCES_PER_PAGE))
    return [document for document in documents if document]


_IOB2_TYPES = {"PER": EntityType.PERSON, "ORG": EntityType.ORGANIZATION}


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
        kind = _IOB2_TYPES.get(label)
        if kind is not None:
            spans.append(SourceSpan(kind, starts[first], starts[last] + len(tokens[last])))
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
    return _joined(tokens)


def _joined(tokens: list[str]) -> tuple[str, list[int]]:
    """Join tokens by single spaces; return the text and each token's offset in it."""
    starts: list[int] = []
    offset = 0
    for token in tokens:
        starts.append(offset)
        offset += len(token) + 1
    return " ".join(tokens), starts


def read_uner(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:
    """Read a UNER Slovak-SNK split (see `TextForm` for the two ways)."""
    return parse_iob2((directory / f"sk_snk-ud-{split}.iob2").read_text(encoding="utf-8"), form)


# --- WikiGoldSK -------------------------------------------------------------

WIKIGOLDSK_FILES = {"train": "train.txt", "dev": "dev.txt", "test": "test.txt"}


def parse_conll(text: str) -> list[Sentence]:
    """Parse a two-column IOB2 file: `token tag` per line, a blank line after each sentence.

    Every non-blank line is a token, even one starting with `#`: the format
    has no comments.

    Args:
        text: Contents of the file.

    Returns:
        The sentences, tokens joined by single spaces, `PER` spans as persons.

    Raises:
        ValueError: If a line holds no tag.
    """
    sentences: list[Sentence] = []
    rows: list[tuple[str, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            if rows:
                sentences.append(_iob2_sentence(rows, None))
            rows = []
            continue
        columns = line.rsplit(maxsplit=1)
        if len(columns) != 2:
            msg = f"line {number} holds no tag"
            raise ValueError(msg)
        rows.append((columns[0], columns[1]))
    if rows:
        sentences.append(_iob2_sentence(rows, None))
    return sentences


def read_wikigoldsk(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:  # noqa: ARG001
    """Read a WikiGoldSK split; each page-like chunk of sentences is a document of its own.

    The files keep no article boundaries, so none can be kept together.
    """
    text = (directory / WIKIGOLDSK_FILES[split]).read_text(encoding="utf-8")
    return list(_chunks(parse_conll(text), SENTENCES_PER_PAGE))


# --- SlavicNER --------------------------------------------------------------

SLAVICNER_ID = "slavicner"
SLAVICNER_SPLITS = {"train": "SPLIT_cross-topic_train.txt", "dev": "SPLIT_cross-topic_test.txt"}
"""Our split → the source's cross-topic split file (its `test` part is the tuning part)."""

_SLAVICNER_TYPES = {"PER": EntityType.PERSON, "ORG": EntityType.ORGANIZATION}


def parse_slavicner(text: str, annotations: str) -> list[Sentence]:
    """Turn one SlavicNER document and its mentions into one sentence per non-empty line.

    The text is normalised to NFC with the offsets moved along. A mention
    whose offsets do not cut out its own string is dropped and counted under
    `(span not in text)`; one that does never crosses a line, as a line of
    the `.tsv` holds no line break.

    Args:
        text: The raw document (`raw/<topic>/<language>/<file>.txt`).
        annotations: Its mentions (`ner/.../<file>.tsv`): start, end (one
            past the mention), mention, lemma, category, cross-lingual id,
            separated by tabs.

    Returns:
        The document's lines (paragraphs) with mapped spans.

    Raises:
        ValueError: If an annotation line does not hold six columns.
    """
    unmapped: list[str] = []
    mentions: list[tuple[EntityType, int, int]] = []
    for number, line in enumerate(annotations.splitlines(), start=1):
        if not line.strip():
            continue
        columns = line.split("\t")
        if len(columns) != 6:
            msg = f"annotation line {number} holds {len(columns)} columns, not 6"
            raise ValueError(msg)
        start, end, mention, category = int(columns[0]), int(columns[1]), columns[2], columns[4]
        if end <= start or text[start:end] != mention:
            unmapped.append(_SKIPPED)
            continue
        kind = _SLAVICNER_TYPES.get(category)
        if kind is None:
            unmapped.append(category)
            continue
        mentions.append((kind, _nfc_offset(text, start), _nfc_offset(text, end)))
    normalised = unicodedata.normalize("NFC", text)
    sentences: list[Sentence] = []
    line_start = 0
    for line in normalised.split("\n"):
        line_end = line_start + len(line)
        if line.strip():
            spans = tuple(
                SourceSpan(kind, start - line_start, end - line_start)
                for kind, start, end in mentions
                if line_start <= start and end <= line_end
            )
            sentences.append(Sentence(line, spans))
        line_start = line_end + 1
    if sentences and unmapped:
        first = sentences[0]
        sentences[0] = Sentence(first.text, first.spans, tuple(unmapped))
    return sentences


def slavicner_reader(language: str) -> Callable[[Path, str, TextForm], list[list[Sentence]]]:
    """Return the reader of one language's documents of a cross-topic split, one document each."""

    def read(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:  # noqa: ARG001
        version = load_catalog()[SLAVICNER_ID].version
        root = directory / "SlavicNER" / f"SlavicNER-{version}"
        listed = (root / SLAVICNER_SPLITS[split]).read_text(encoding="utf-8").split()
        documents: list[list[Sentence]] = []
        for raw in listed:
            parts = raw.split("/")
            if len(parts) != 4 or parts[0] != "raw":
                msg = f"{SLAVICNER_SPLITS[split]} lists a path not of the form raw/<topic>/<lang>/"
                raise ValueError(msg)
            if parts[2] != language:
                continue
            annotations = root / "ner" / Path(*parts[1:]).with_suffix(".tsv")
            documents.append(
                parse_slavicner(
                    (root / raw).read_text(encoding="utf-8"),
                    annotations.read_text(encoding="utf-8"),
                )
            )
        return documents

    return read


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

REDACT_FILES = {"sample": "pii_benchmark_sample1000.json", "test": "pii_benchmark_full.json"}
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
        if _redact_language(record) != language:
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
    """Read the Czech records of a REDACT split.

    `sample` is the published sample (40 Czech records), development data.
    `test` is every other Czech record of the full release: the full file
    repeats the sample's records word for word, so they are left out by text
    (pinned release: 496 Czech records, 456 left for test).

    Raises:
        ValueError: For an unknown split, or if a Czech sample record is not
            in the full release word for word: it could stay in the test split
            under a slightly different text.
    """
    if split not in REDACT_FILES:
        msg = f"REDACT has the splits {sorted(REDACT_FILES)}, not {split!r}"
        raise ValueError(msg)
    records = _redact_records(directory / REDACT_FILES[split])
    if split == "test":
        sample = _redact_records(directory / REDACT_FILES["sample"])
        development = {record["text"] for record in sample}
        _check_sample_in_release(sample, records)
        records = [record for record in records if record["text"] not in development]
    return parse_redact(records, _REDACT_LANGUAGE)


def _check_sample_in_release(
    sample: list[dict[str, object]], release: list[dict[str, object]]
) -> None:
    """Refuse a full release that lacks a Czech sample record word for word (counts only)."""
    czech = {record["text"] for record in sample if _redact_language(record) == _REDACT_LANGUAGE}
    missing = czech - {record["text"] for record in release}
    if missing:
        msg = (
            f"{len(missing)} of {len(czech)} Czech sample records are not in the full REDACT "
            "release word for word; the test split would keep development data"
        )
        raise ValueError(msg)


def _redact_language(record: dict[str, object]) -> object:
    axes = record.get("axes")
    return axes.get("language") if isinstance(axes, dict) else None


def _redact_records(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


# --- OpenPII 1M -------------------------------------------------------------

OPENPII_ID = "openpii-1m"
OPENPII_LANGUAGES = ("cs", "sk", "en")
"""Languages registered as datasets; any of the source's 23 can be added here."""

OPENPII_ADDRESS_GAP = 8
"""Most characters between two address parts of one address (", PSČ " is six)."""

_OPENPII_PERSON = frozenset({"GIVENNAME", "SURNAME"})
_OPENPII_ADDRESS = frozenset({"STREET", "BUILDINGNUM", "ZIPCODE", "CITY"})
_OPENPII_ADDRESS_ANCHORS = frozenset({"STREET", "ZIPCODE"})
_OPENPII_TYPES = {"EMAIL": EntityType.EMAIL}
_OPENPII_FILES = {"train": "train.jsonl", "dev": "validation.jsonl", "test": "validation.jsonl"}
_HORIZONTAL_SPACE = re.compile(r"[^\S\n]*")


def openpii_half(uid: int) -> str:
    """Return `dev` or `test`: which half of the source's validation split a record is in.

    A hash of the uid rather than its parity or position, so the halves do not
    follow however the source numbered or ordered its records.
    """
    digest = hashlib.sha256(f"{OPENPII_ID}:{uid}".encode()).digest()
    return "dev" if digest[0] % 2 == 0 else "test"


def parse_openpii(records: Iterable[dict[str, Any]], language: str) -> list[list[Sentence]]:
    """Turn OpenPII records of one language into one-record documents.

    Args:
        records: Parsed JSON lines.
        language: The source's language code, e.g. `cs`.

    Returns:
        One document per record, holding the record as a single "sentence";
        spans whose offsets do not cut out their value are counted as skipped.
    """
    documents: list[list[Sentence]] = []
    for record in records:
        if record.get("language") != language:
            continue
        raw = str(record["source_text"])
        labelled: list[tuple[str, int, int]] = []
        unmapped: list[str] = []
        for span in record.get("privacy_mask") or []:
            start, end = span.get("start"), span.get("end")
            if (
                not isinstance(start, int)
                or not isinstance(end, int)
                or end <= start
                or raw[start:end] != span.get("value")
            ):
                unmapped.append(_SKIPPED)
            else:
                labelled.append((str(span["label"]), start, end))
        spans: list[SourceSpan] = []
        for run in _openpii_runs(raw, sorted(labelled, key=lambda item: item[1])):
            labels = {label for label, _, _ in run}
            kind = _openpii_type(labels)
            if kind is None:
                unmapped += [label for label, _, _ in run]
                continue
            start, end = run[0][1], run[-1][2]
            spans.append(SourceSpan(kind, _nfc_offset(raw, start), _nfc_offset(raw, end)))
        text = unicodedata.normalize("NFC", raw)
        documents.append([Sentence(text, tuple(spans), tuple(unmapped))])
    return documents


def _openpii_runs(
    text: str, labelled: list[tuple[str, int, int]]
) -> Iterator[list[tuple[str, int, int]]]:
    """Group adjacent name parts and adjacent address parts; every other span stands alone."""
    run: list[tuple[str, int, int]] = []
    for item in labelled:
        if run and _joins(text, run[-1], item):
            run.append(item)
            continue
        if run:
            yield run
        run = [item]
    if run:
        yield run


def _joins(text: str, previous: tuple[str, int, int], current: tuple[str, int, int]) -> bool:
    gap = text[previous[2] : current[1]]
    if previous[0] in _OPENPII_PERSON and current[0] in _OPENPII_PERSON:
        return _HORIZONTAL_SPACE.fullmatch(gap) is not None
    if previous[0] in _OPENPII_ADDRESS and current[0] in _OPENPII_ADDRESS:
        return len(gap) <= OPENPII_ADDRESS_GAP and "\n" not in gap
    return False


def _openpii_type(labels: set[str]) -> EntityType | None:
    if labels <= _OPENPII_PERSON:
        return EntityType.PERSON
    if labels <= _OPENPII_ADDRESS:
        return EntityType.ADDRESS if labels & _OPENPII_ADDRESS_ANCHORS else None
    (label,) = labels
    return _OPENPII_TYPES.get(label)


def openpii_reader(language: str) -> Callable[[Path, str, TextForm], list[list[Sentence]]]:
    """Return the reader of one language's records (see `parse_openpii`)."""

    def read(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:  # noqa: ARG001
        return parse_openpii(
            _openpii_records(directory / _OPENPII_FILES[split], language, split), language
        )

    return read


def _openpii_records(path: Path, language: str, split: str) -> Iterator[dict[str, Any]]:
    """Yield the records of one language, and of one half for `dev` and `test`."""
    # Checking the raw line first skips parsing the other 22 languages' records.
    marker = f'"language": "{language}"'
    with path.open(encoding="utf-8") as lines:
        for line in lines:
            if marker not in line:
                continue
            record = json.loads(line)
            if split == "train" or openpii_half(int(record["uid"])) == split:
                yield record


# --- Name forms -------------------------------------------------------------


def name_forms_reader(language: str) -> Callable[[Path, str, TextForm], list[list[Sentence]]]:
    """Return the generator of one language's name-forms texts, one text per document."""

    def read(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:  # noqa: ARG001
        return [
            [
                Sentence(
                    text.text,
                    tuple(
                        SourceSpan(EntityType.PERSON, name.start, name.end, name.tags)
                        for name in text.names
                    ),
                )
            ]
            for text in generate(language, split)
        ]

    return read


# --- Held-out synthetic set -------------------------------------------------


def heldout_reader(language: str) -> Callable[[Path, str, TextForm], list[list[Sentence]]]:
    """Return the generator of one language's held-out documents, one document each."""

    def read(directory: Path, split: str, form: TextForm) -> list[list[Sentence]]:  # noqa: ARG001
        return [
            [
                Sentence(
                    document.text,
                    tuple(
                        SourceSpan(span.type, span.start, span.end, span.tags)
                        for span in document.spans
                    ),
                )
            ]
            for document in heldout.generate(language, split)
        ]

    return read


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
        unscored=frozenset({EntityType.ORGANIZATION}),
    ),
    "uner-sk-snk": DatasetSpec(
        id="uner-sk-snk",
        language="sk",
        types=frozenset({EntityType.PERSON}),
        splits={"train": Role.TRAIN, "dev": Role.DEV, "test": Role.TEST},
        read=read_uner,
        unscored=frozenset({EntityType.ORGANIZATION}),
    ),
    "wikigoldsk": DatasetSpec(
        id="wikigoldsk",
        language="sk",
        types=frozenset({EntityType.PERSON}),
        splits={"train": Role.TRAIN, "dev": Role.DEV, "test": Role.TEST},
        read=read_wikigoldsk,
        unscored=frozenset({EntityType.ORGANIZATION}),
        check_overlap=True,
    ),
    "slavicner-cs": DatasetSpec(
        id="slavicner-cs",
        language="cs",
        types=frozenset({EntityType.PERSON}),
        splits={"train": Role.TRAIN, "dev": Role.DEV},
        read=slavicner_reader("cs"),
        resource=SLAVICNER_ID,
        unscored=frozenset({EntityType.ORGANIZATION}),
        check_overlap=True,
    ),
    "redact": DatasetSpec(
        id="redact",
        language="cs",
        types=frozenset(REDACT_TYPES.values()),
        splits={"sample": Role.DEV, "test": Role.TEST},
        read=read_redact,
    ),
    **{
        f"{OPENPII_ID}-{language}": DatasetSpec(
            id=f"{OPENPII_ID}-{language}",
            language=language,
            types=frozenset({EntityType.PERSON, EntityType.ADDRESS, EntityType.EMAIL}),
            splits={"train": Role.TRAIN, "dev": Role.DEV, "test": Role.TEST},
            read=openpii_reader(language),
            resource=OPENPII_ID,
        )
        for language in OPENPII_LANGUAGES
    },
    **{
        f"name-forms-{language}": DatasetSpec(
            id=f"name-forms-{language}",
            language=language,
            types=frozenset({EntityType.PERSON}),
            splits={"dev": Role.DEV, "test": Role.TEST},
            read=name_forms_reader(language),
            generated=NAME_FORMS_VERSION,
        )
        for language in ("cs", "sk")
    },
    **{
        f"heldout-{language}": DatasetSpec(
            id=f"heldout-{language}",
            language=language,
            types=heldout.TYPES,
            splits={"dev": Role.DEV, "test": Role.TEST},
            read=heldout_reader(language),
            generated=heldout.HELDOUT_VERSION,
        )
        for language in ("cs", "sk")
    },
}


def dataset_version(dataset: str) -> str:
    """Return a dataset's version: the catalog's, or its generator's for a generated one."""
    spec = DATASETS[dataset]
    if spec.generated is not None:
        return spec.generated
    return load_catalog()[spec.catalog_id].version


def read_sentences(
    dataset: str, split: str, resource_root: Path, form: TextForm = TextForm.WRITTEN
) -> list[list[Sentence]]:
    """Read one split of a dataset as sentences grouped by document, before any page is built.

    Raises:
        ValueError: If the dataset or split is unknown.
        FileNotFoundError: If the dataset is not stored under the root.
    """
    spec = DATASETS.get(dataset)
    if spec is None:
        msg = f"unknown dataset {dataset!r}; choose from {sorted(DATASETS)}"
        raise ValueError(msg)
    if split not in spec.splits:
        msg = f"{dataset} has no split {split!r}; choose from {sorted(spec.splits)}"
        raise ValueError(msg)
    if spec.generated is not None:
        return spec.read(resource_root, split, form)
    return spec.read(load_catalog()[spec.catalog_id].directory(resource_root), split, form)


def load_corpus(
    dataset: str,
    split: str,
    resource_root: Path,
    form: TextForm = TextForm.WRITTEN,
    limit: int | None = None,
    exclude: Callable[[Sentence], bool] | None = None,
) -> Corpus:
    """Load one split of a catalogued dataset from the storage root.

    Args:
        dataset: Catalog id (see `DATASETS`).
        split: Split name as the source calls it.
        resource_root: Storage root holding `data/<id>/`.
        form: How sentences become page text.
        limit: Keep only the first documents, for a quick look; every count
            of the corpus describes those.
        exclude: Tells which sentences to leave out (counted in
            `Corpus.excluded`, over the whole split); a document left with
            none is left out.

    Returns:
        The corpus with its documents and gold spans.

    Raises:
        ValueError: If the dataset or split is unknown.
        FileNotFoundError: If the dataset is not stored under the root.
    """
    groups = read_sentences(dataset, split, resource_root, form)
    spec = DATASETS[dataset]
    excluded = 0
    if exclude is not None:
        kept: list[list[Sentence]] = []
        for sentences in groups:
            remaining = [sentence for sentence in sentences if not exclude(sentence)]
            excluded += len(sentences) - len(remaining)
            if remaining:
                kept.append(remaining)
        groups = kept
    version = spec.generated or load_catalog()[spec.catalog_id].version
    corpus = build_corpus(spec, split, version, groups[:limit], form)
    corpus.excluded = excluded
    return corpus


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
    tags: dict[tuple[int, int, int], tuple[Tag, ...]] = {}
    for index, chunk in enumerate(_chunks(sentences, SENTENCES_PER_PAGE)):
        text = "\n".join(sentence.text for sentence in chunk)
        page = make_page(index, text)
        offset = 0
        page_gold: list[Entity] = []
        for sentence in chunk:
            for span in sentence.spans:
                start, end = offset + span.start, offset + span.end
                if span.tags:
                    tags[index, start, end] = span.tags
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
    return GoldDocument(name=name, document=document, gold=gold, tags=tags)


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
