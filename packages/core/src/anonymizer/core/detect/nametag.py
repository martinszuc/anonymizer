"""Name and address detection with NameTag 3, ÚFAL's supervised NER.

NameTag 3 (Straková et al., 2019) fine-tunes a pretrained encoder and puts one
of two heads on the first subword of every token: a softmax over flat BIO
labels, or a small LSTM decoder that writes each token's labels one after
another, outermost entity first, which is how it tags CNEC's nested entities.
Upstream it is a set of Keras scripts, not a package; this module runs the
released models without Keras (`nametag_model.py` reads the checkpoint), and
reproduces what NameTag's own server does with raw text (the model's input
and output in `nametag_model.py`):

- Text is split into sentences and tokens by the UDPipe tokenizer shipped
  with each model, so the model sees tokens as it saw them in training
  (punctuation apart, "Ing" and "." as two tokens).
- Each token is NFC-normalised, cut to 200 characters and, unless the model
  was trained otherwise, a word in capitals is title-cased ("NOVÁK" becomes
  "Novák") before subword tokenization.
- A model trained on sentences reads one sentence at a time; one trained on
  documents reads a page in windows of whole sentences up to the encoder's
  512 subwords. A sentence longer than that is cut between words.
- Labels become entities the way the server's postprocessing reads them: a
  label continues the entity at the same nesting depth on the previous token
  unless it begins with `B-` or names another type.

Entity types, CNEC 2.0 (Czech model) and CoNLL / UNER / OntoNotes
(multilingual model):

    person   `P` containers (a whole name), and `pf`, `ps`, `pm`, `p_`
             (first name, surname, middle name, other part); `PER`, `PERSON`.
             A part inside a container is dropped by `merge_entities`. Not
             `pc` (inhabitants), `pp` (mythological persons), `pd` (a title
             alone), as in the evaluation's reading of CNEC.
    address  A run of address parts: `A` containers, `gs` (street), `ah`
             (house number), `az` (postcode), `gu` (town), `gq` (part of
             town), joined while only punctuation lies between them. The
             Czech model often tags the parts without the container around
             them ("Dlouhá 12, 110 00 Praha 1" as street, number, postcode
             and town), and a part left out of the span stays in the text. A
             run with no container, street, number or postcode is a place
             ("born in Brno"), not an address, and is dropped.

Telephone numbers (`at`) and e-mail addresses (`me`) are left to the rules,
which check their format. Spans are widened to whole words and a span with
fewer than two letters or digits is dropped, as for GLiNER.

The model gives no score of its own; an entity's score is the lowest
probability the model assigned to one of its labels.

The detector takes a sentence splitter and a tagger, so it is testable with
stand-ins; the real ones need the optional `ner` dependencies.
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from anonymizer.core.detect.base import describe, merge_entities
from anonymizer.core.detect.gliner import encoder_resource, widen_to_words
from anonymizer.core.log import step
from anonymizer.core.resources import Catalog, load_catalog, missing_resources
from anonymizer.core.types import DetectionSource, Entity, EntityType, Page

log = logging.getLogger(__name__)

NAMETAG_ENGINE = "nametag3"
"""The catalog's `engine` for NameTag 3 models."""

PERSON_LABELS = frozenset({"P", "pf", "ps", "pm", "p_", "PER", "PERSON"})
"""Model entity types reported as persons."""

ADDRESS_LABELS = frozenset({"A", "gs", "ah", "az", "gu", "gq"})
"""Model entity types joined into address runs."""

ADDRESS_ANCHORS = frozenset({"A", "gs", "ah", "az"})
"""Types of which an address run needs one; a town alone is a place."""

_MIN_CHARACTERS = 2

Label = tuple[str, float]
"""A BIO label (`B-P`, `I-ps`) and the probability the model gave it."""


@dataclass(frozen=True, slots=True)
class Token:
    """A token of the page text as the model's tokenizer cut it.

    Attributes:
        form: The token as written.
        start: First offset in the page text.
        end: Offset one past the token.
    """

    form: str
    start: int
    end: int


class SentenceSplitter(Protocol):
    """Cuts text into sentences of tokens with offsets."""

    def sentences(self, text: str) -> list[list[Token]]:
        """Return the sentences of a text, each a list of tokens in order."""
        ...


class Tagger(Protocol):
    """The part of a NameTag 3 model the detector uses."""

    def tag(self, sentences: Sequence[Sequence[str]]) -> list[list[list[Label]]]:
        """Return, per sentence and token, its labels outermost first; `[]` for outside.

        The sentences are one page, in order; a model trained on documents
        reads them together.
        """
        ...


@dataclass(frozen=True, slots=True)
class TaggedEntity:
    """An entity in token positions, as decoded from the labels.

    Attributes:
        label: The model's entity type (`P`, `ps`, `PER`).
        first: Index of the first token.
        last: Index of the last token.
        score: The lowest probability among its labels.
    """

    label: str
    first: int
    last: int
    score: float


def tagged_entities(labels: Sequence[Sequence[Label]]) -> list[TaggedEntity]:
    """Read nested entities from one sentence's labels, as NameTag's postprocessing does.

    The label at depth `j` of a token continues the entity at depth `j` of the
    previous token if it is an `I-` label of the same type; otherwise it
    closes that entity and every one nested in it, and opens a new one. A
    token with fewer labels closes the deeper entities.

    Args:
        labels: Per token, its labels outermost first; `[]` for outside.

    Returns:
        The entities, each once, ordered by first token and then outermost first.
    """
    found: dict[tuple[int, int, str], TaggedEntity] = {}
    opened: list[tuple[str, int, float]] = []

    def close(depth: int, last: int) -> None:
        for label, first, score in opened[depth:]:
            found.setdefault((first, last, label), TaggedEntity(label, first, last, score))
        del opened[depth:]

    for index, token_labels in enumerate(labels):
        for depth, (label, probability) in enumerate(token_labels):
            kind = label[2:]
            if depth < len(opened):
                open_kind, first, score = opened[depth]
                if label.startswith("B-") or open_kind != kind:
                    close(depth, index - 1)
                    opened.append((kind, index, probability))
                else:
                    opened[depth] = (open_kind, first, min(score, probability))
            else:
                opened.append((kind, index, probability))
        close(len(token_labels), index - 1)
    close(0, len(labels) - 1)
    return sorted(found.values(), key=lambda entity: (entity.first, -entity.last))


class NametagDetector:
    """Detects persons and addresses with a NameTag 3 model, sentence by sentence.

    Attributes:
        tagger: The model, or a stand-in.
        splitter: Cuts page text into sentences of tokens.
    """

    def __init__(self, tagger: Tagger, splitter: SentenceSplitter, name: str) -> None:
        """Initialize the detector.

        Args:
            tagger: A loaded model (see `load_nametag_detector`) or a stand-in.
            splitter: The model's sentence splitter, or a stand-in.
            name: Identifier used in logs and evaluation reports.
        """
        self.tagger = tagger
        self.splitter = splitter
        self._name = name

    @property
    def name(self) -> str:
        """Identifier used in logs and evaluation reports."""
        return self._name

    def detect(self, page: Page) -> list[Entity]:
        """Return the entities the model finds on a page.

        Args:
            page: Page to scan; offsets refer to `page.text`.

        Returns:
            Entities in reading order, with geometry resolved from page words.
        """
        sentences = [sentence for sentence in self.splitter.sentences(page.text) if sentence]
        if not sentences:
            return []
        log.debug("%s: page %d: %d sentences", self.name, page.index, len(sentences))
        labels = self.tagger.tag([[token.form for token in sentence] for sentence in sentences])
        entities: list[Entity] = []
        for sentence, sentence_labels in zip(sentences, labels, strict=True):
            tagged = tagged_entities(sentence_labels)
            found = [
                (EntityType.PERSON, entity) for entity in tagged if entity.label in PERSON_LABELS
            ]
            found += [(EntityType.ADDRESS, run) for run in address_runs(sentence, tagged)]
            entities += [
                entity
                for kind, span in found
                if (entity := self._entity(page, sentence, kind, span)) is not None
            ]
        return merge_entities(entities)

    def _entity(
        self, page: Page, sentence: Sequence[Token], kind: EntityType, tagged: TaggedEntity
    ) -> Entity | None:
        widened = widen_to_words(page.text, sentence[tagged.first].start, sentence[tagged.last].end)
        if widened is None:
            return None
        start, end = widened
        if sum(character.isalnum() for character in page.text[start:end]) < _MIN_CHARACTERS:
            log.debug("%s: dropped span of one character", self.name)
            return None
        entity = Entity(
            type=kind,
            page_index=page.index,
            start=start,
            end=end,
            text=page.text[start:end],
            bboxes=page.bboxes_for_span(start, end),
            source=DetectionSource.MODEL,
            score=min(1.0, max(0.0, tagged.score)),
        )
        if log.isEnabledFor(logging.DEBUG):
            log.debug("%s predicted %s label=%s", self.name, describe(entity), tagged.label)
        return entity


def address_runs(sentence: Sequence[Token], tagged: Sequence[TaggedEntity]) -> list[TaggedEntity]:
    """Join a sentence's address parts into addresses.

    Parts overlapping or separated by punctuation only (", ") form one run; a
    run without a container, street, house number or postcode is dropped.

    Args:
        sentence: The sentence's tokens.
        tagged: Its entities, as `tagged_entities` returns them.

    Returns:
        One entity per run, labelled `A`, scored by its weakest part.
    """
    parts = sorted(
        (entity for entity in tagged if entity.label in ADDRESS_LABELS),
        key=lambda entity: (entity.first, entity.last),
    )
    runs: list[list[TaggedEntity]] = []
    for part in parts:
        if runs and _joined(sentence, max(entity.last for entity in runs[-1]), part.first):
            runs[-1].append(part)
        else:
            runs.append([part])
    return [
        TaggedEntity(
            "A",
            run[0].first,
            max(entity.last for entity in run),
            min(entity.score for entity in run),
        )
        for run in runs
        if any(entity.label in ADDRESS_ANCHORS for entity in run)
    ]


def _joined(sentence: Sequence[Token], last: int, first: int) -> bool:
    """Whether a part starting at token `first` continues a run ending at token `last`."""
    between = sentence[last + 1 : first]
    return not any(character.isalnum() for token in between for character in token.form)


class UDPipeSplitter:
    """Sentences and tokens from the UDPipe tokenizer shipped with a NameTag 3 model.

    Multiword tokens (Czech "aby" in some contexts) stay one token, as the
    NameTag server feeds them.
    """

    def __init__(self, path: Path) -> None:
        """Load the tokenizer.

        Args:
            path: The model's `udpipe.tokenizer`.

        Raises:
            ImportError: If `ufal.udpipe` is not installed.
            OSError: If the tokenizer cannot be loaded.
        """
        try:
            # The module is generated by SWIG and carries no type information.
            self._udpipe: Any = importlib.import_module("ufal.udpipe")
        except ImportError as error:
            msg = "NameTag 3 needs the optional 'ner' dependencies: uv sync --group ner"
            raise ImportError(msg) from error
        self._model = self._udpipe.Model.load(str(path))
        if self._model is None:
            msg = f"cannot load the UDPipe tokenizer {path.name}"
            raise OSError(msg)

    def sentences(self, text: str) -> list[list[Token]]:
        """Return the sentences of a text, each a list of tokens with their offsets."""
        # "ranges" records each token's character offsets; the tokens are the
        # same as with the default options the NameTag server uses.
        tokenizer = self._model.newTokenizer("ranges")
        tokenizer.setText(text)
        error = self._udpipe.ProcessingError()
        sentence = self._udpipe.Sentence()
        sentences: list[list[Token]] = []
        while tokenizer.nextSentence(sentence, error):
            sentences.append(self._tokens(sentence))
            sentence = self._udpipe.Sentence()
        if error.occurred():
            msg = "UDPipe could not tokenize the text"
            raise ValueError(msg)
        return sentences

    def _tokens(self, sentence: Any) -> list[Token]:
        words, multiwords = sentence.words, sentence.multiwordTokens
        tokens: list[Token] = []
        # Word 0 is UDPipe's root node.
        word, multiword = 1, 0
        while word < len(words):
            if multiword < len(multiwords) and multiwords[multiword].idFirst == word:
                token = multiwords[multiword]
                word = token.idLast + 1
                multiword += 1
            else:
                token = words[word]
                word += 1
            tokens.append(Token(token.form, token.getTokenRangeStart(), token.getTokenRangeEnd()))
        return tokens


def model_directory(root: Path, model_id: str, catalog: Catalog) -> Path:
    """Return the directory of an unpacked NameTag 3 model: the one holding `options.json`.

    Raises:
        FileNotFoundError: If the archive holds no model, or more than one.
    """
    found = sorted(catalog[model_id].directory(root).rglob("options.json"))
    if len(found) != 1:
        msg = f"{model_id}: expected one unpacked model, found {len(found)}"
        raise FileNotFoundError(msg)
    return found[0].parent


def load_nametag_detector(
    root: Path, model_id: str, *, catalog: Catalog | None = None
) -> NametagDetector:
    """Build a NameTag 3 detector from a catalog model stored under a storage root.

    Args:
        root: Storage root holding `models/` (see `scripts/download.py`).
        model_id: Catalog id of a NameTag 3 model.
        catalog: The resource catalog; the one shipped with the core when omitted.

    Returns:
        A ready detector, named after the model.

    Raises:
        FileNotFoundError: If the model or its encoder files are not stored.
        ImportError: If the optional `ner` dependencies are not installed.
    """
    catalog = catalog or load_catalog()
    missing = missing_resources(catalog, model_id, root)
    if missing:
        msg = (
            f"model files missing under {root}: {', '.join(missing)}; "
            f"fetch them with: uv run python scripts/download.py fetch {model_id}"
        )
        raise FileNotFoundError(msg)
    directory = model_directory(root, model_id, catalog)
    with step(log, "load name model", done_level=logging.INFO, model=model_id):
        tagger = load_nametag_tagger(
            directory, catalog[encoder_resource(catalog, model_id)].directory(root)
        )
        splitter = UDPipeSplitter(directory / "udpipe.tokenizer")
    return NametagDetector(tagger, splitter, name=model_id)


def load_nametag_tagger(model_dir: Path, encoder_dir: Path) -> Tagger:
    """Load a NameTag 3 model's network from local files only.

    Args:
        model_dir: The unpacked model (`options.json`, `mappings.pickle`,
            `checkpoint.weights.h5`).
        encoder_dir: The encoder's config and tokenizer.

    Returns:
        The tagger.

    Raises:
        ImportError: If the optional `ner` dependencies are not installed.
    """
    from anonymizer.core.detect.nametag_model import Nametag3Tagger

    try:
        return Nametag3Tagger.load(model_dir, encoder_dir)
    except ImportError as error:
        msg = "NameTag 3 needs the optional 'ner' dependencies: uv sync --group ner"
        raise ImportError(msg) from error
