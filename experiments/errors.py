"""What kind of names a system misses and what it wrongly flags, in counts only.

`python -m experiments errors --config experiments/configs/rq6-dev.toml` runs
every system of a run config exactly as `experiments run` does (same loaders,
`core.pipeline` through `systems.detect`, the same name model cache, so a run
from a warm cache does not load a model) and sorts its errors into
structural categories computed from the page text, without keeping it. It
writes `<name>-errors.json` and `<name>-errors.md`.

Persons and addresses are analysed, on the corpora that score them.

**Misses.** A gold span's outcome is decided by the predictions of its type
on its page, as the match counts in `metrics.py` decide:

- **not found**: no prediction of its type overlaps it. These are exactly the
  gold spans partial-match recall misses.
- **found in part**: one overlaps it, but some character that is not
  whitespace is covered by no prediction of its type: the rest stays
  readable unless a prediction of another type covers it.
- found whole: every such character is covered (not an error).

Spans not found that a prediction of another type overlaps are counted on
their own (`other_type` in the counts): a name tagged as an address is
redacted all the same.

Categories of a gold span depend only on the span and its page text, never
on a system, so every system is measured on the same gold per category. A
span can fall into several; the three `words` categories partition them.

- `words=1`, `words=2`, `words=3+`: words in the span, split at whitespace
  ("Nováková-Svobodová" is one word, "J. Novák" two).
- `title`: an academic title (`detect.titles.TITLES_BEFORE`) or an
  honorific (`HONORIFICS`: pan, paní, pane, pán, slečna, Mr., ...; matched
  without case and without a final period) is the word directly before the
  span on its line, or the span's first word.
- `sentence_start`: the span starts its line, or follows sentence-final
  punctuation (`.`, `!`, `?`, `…`) whose word is not a title, an honorific
  or an initial ("Ing. Novák" is not a sentence start). Opening quotes,
  brackets and dashes in between are ignored. Sentence corpora put one
  sentence on each line, so the line start is the sentence start there.
- `after_label`: the line holds a colon before the span, and the line's
  text before its first colon is one to four words beginning with a
  letter: a form's "Label: value" ("Jméno: Ing. Jan Novák"). Prose with a
  colon early in the line ("Řekl mu: ...") counts too.
- `all_caps`: at least two letters, all upper case.
- `hyphen_apostrophe`: holds a hyphen (ASCII, Unicode or non-breaking), an
  en dash or an apostrophe (ASCII, typographic or modifier letter): double
  surnames, O'Brien.
- `diacritics`: holds a letter outside ASCII (á, č, ř, ľ, ...).
- `initial`: holds a word that is one upper-case letter, with or without a
  period ("J. Novák", "Jan N.").

Per category: gold spans, those not found and found in part, each as a
count, a share of the system's errors of that outcome, and a rate (errors
in the category / gold in the category) with its 95 % bootstrap interval
over documents, on the same draws as `experiments run`.

**False alarms.** A prediction of a person or an address that overlaps no
gold span of its type (what partial-match precision counts against). Its
categories depend on the prediction, so each system's predictions are
counted per category, and the rate is false alarms / predictions in the
category. Shared with the misses: `words=*`, `title`, `sentence_start`,
`after_label`, `all_caps`; of their own:

- `capitalised_word`: one word whose first letter is upper case and which
  is not all capitals ("Kupující", "Praha").
- `role_noun`: the first word is a role noun of the corpus's language
  (`detect.roles.role_words_for`: "Kupující Novák"). The name filter drops
  spans of nothing but role nouns, so these are the ones it let through.
- `organization`: overlaps a gold organisation (CNEC and UNER mark them;
  they are never scored).
- `other_type`: overlaps a gold span of another type, other than an
  organisation (a person predicted over an address).

Nothing read from a corpus is printed or written into the results: no text,
only counts, rates and the category names above. CNEC and UNER name real
people. `--examples DIR` writes a few example spans per category, with
some context, into a git-ignored folder outside `results/`, and only for
corpora the catalog does not mark as holding real personal data (REDACT,
OpenPII, the generated name-forms sets).
"""

from __future__ import annotations

import datetime
import json
import re
import subprocess
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anonymizer.core
from anonymizer.core.detect.nametag import SentenceSplitter
from anonymizer.core.detect.roles import role_words_for
from anonymizer.core.detect.titles import TITLES_BEFORE
from anonymizer.core.resources import Catalog, load_catalog
from anonymizer.core.types import Entity, EntityType

from experiments.config import RunConfig
from experiments.datasets import DATASETS, Corpus, GoldDocument, dataset_version, load_corpus
from experiments.metrics import Resampler, Tally, interval, resamples, total
from experiments.report import UNDEFINED, format_interval
from experiments.run import corpus_models, git_state, machine, once, scored_types
from experiments.systems import (
    CACHE_FLOOR,
    NameModel,
    detect,
    model_loader,
    model_versions,
    splitter_loader,
    system_models,
)

ERRORS_SCHEMA = 1

ANALYSED_TYPES = (EntityType.PERSON, EntityType.ADDRESS)
"""Types whose errors are sorted; the others are the rules' job and have few."""

ALL = "all"
"""The category every span is in."""

MISS_CATEGORIES: dict[str, str] = {
    ALL: "every gold span of the type",
    "words=1": "one word (split at whitespace)",
    "words=2": "two words",
    "words=3+": "three or more words",
    "title": "a title or honorific directly before it or as its first word",
    "sentence_start": "starts its line or a sentence",
    "after_label": "the value of a 'Label: value' line",
    "all_caps": "all letters upper case",
    "hyphen_apostrophe": "holds a hyphen, dash or apostrophe",
    "diacritics": "holds a letter outside ASCII",
    "initial": "holds a one-letter initial",
}
"""Categories of a gold span, in table order (definitions: module docstring)."""

ALARM_CATEGORIES: dict[str, str] = {
    ALL: "every false alarm of the type",
    "words=1": "one word",
    "words=2": "two words",
    "words=3+": "three or more words",
    "capitalised_word": "one capitalised word, not all capitals",
    "all_caps": "all letters upper case",
    "title": "a title or honorific directly before it or as its first word",
    "sentence_start": "starts its line or a sentence",
    "after_label": "the value of a 'Label: value' line",
    "role_noun": "starts with a role noun",
    "organization": "overlaps a gold organisation",
    "other_type": "overlaps a gold span of another type",
}
"""Categories of a prediction, in table order (definitions: module docstring)."""

HONORIFICS = frozenset(
    {
        # Czech: pan, paní, slečna in their cases, and the abbreviations p., sl.
        *("pan", "pana", "panu", "pane", "panem", "panovi", "páni", "pánové", "pánům"),
        *("pány", "paní", "slečna", "slečny", "slečně", "slečnu", "slečno", "slečnou"),
        *("p", "sl"),
        # Slovak: pán, pani, slečna in their cases.
        *("pán", "pána", "pánovi", "pánom", "pánov", "pani", "panej", "paniu", "paňou"),
        *("panie", "slečne"),
        # English.
        *("mr", "mrs", "ms", "miss", "mx", "sir"),
    }
)
"""Honorifics before a name, lower case, without a final period."""

_TITLE_WORDS = frozenset(
    word.rstrip(".").lower() for title in TITLES_BEFORE for word in title.split()
)
_EDGE = ",;:!?()[]{}\"'„“”«»"
# Opening quotes, brackets and dashes (low-9 and left single quote, en and em dash).
_OPENERS = " \t\"'„“\u201a\u2018«»([{-\u2013\u2014"
_SENTENCE_ENDS = ".!?…"
# Hyphen-minus, hyphen, non-breaking hyphen, en dash; apostrophe, right single quote,
# modifier letter apostrophe.
_HYPHENS_APOSTROPHES = frozenset("-\u2010\u2011\u2013'\u2019\u02bc")
_INITIAL = re.compile(r"[^\W\d_]\.?")
_LETTERS = re.compile(r"[^\W\d_]+")
_LABEL_WORDS = 4
_CONTEXT = 40
EXAMPLES_PER_CATEGORY = 5

Progress = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class MissCounts(Tally):
    """Gold spans of one category and those a system got wrong, additive over documents.

    Attributes:
        gold: Distinct gold spans.
        not_found: Of those, overlapped by no prediction of their type.
        partly: Overlapped, but not covered whole by predictions of their type.
        other_type: Not found, but overlapped by a prediction of another type.
    """

    gold: int = 0
    not_found: int = 0
    partly: int = 0
    other_type: int = 0

    def metric(self, name: str) -> float | None:
        """`not_found_rate` or `partly_rate`: the outcome's share of the gold spans."""
        if name == "not_found_rate":
            return self.not_found / self.gold if self.gold else None
        if name == "partly_rate":
            return self.partly / self.gold if self.gold else None
        msg = f"unknown metric {name!r}"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class AlarmCounts(Tally):
    """Predictions of one category and the false alarms among them, additive over documents."""

    predicted: int = 0
    alarms: int = 0

    def metric(self, name: str) -> float | None:
        """`alarm_rate`: false alarms / predictions."""
        if name == "alarm_rate":
            return self.alarms / self.predicted if self.predicted else None
        msg = f"unknown metric {name!r}"
        raise ValueError(msg)


MISS_RATES = ("not_found_rate", "partly_rate")


@dataclass(frozen=True, slots=True)
class Span:
    """A span of page text with its type."""

    type: EntityType
    page: int
    start: int
    end: int

    def overlaps(self, other: Span) -> bool:
        """Whether two spans on the same page share a character."""
        return self.page == other.page and self.start < other.end and other.start < self.end


def _spans(entities: Iterable[Entity]) -> list[Span]:
    """Distinct spans of the entities in page text, in order."""
    found: dict[Span, None] = {}
    for entity in entities:
        if not entity.in_page_text or entity.page_index is None:
            continue
        start, end = entity.span
        found[Span(entity.type, entity.page_index, start, end)] = None
    return list(found)


# --- Categories -----------------------------------------------------------------


def _words_category(value: str) -> str:
    count = len(value.split())
    return f"words={count}" if count < 3 else "words=3+"


def _key(word: str) -> str:
    return word.strip(_EDGE).rstrip(".").lower()


def _is_title(word: str) -> bool:
    key = _key(word)
    return key in _TITLE_WORDS or key in HONORIFICS


def _is_initial(word: str) -> bool:
    core = word.strip(_EDGE)
    return bool(_INITIAL.fullmatch(core)) and core[0].isupper()


def _line_before(text: str, start: int) -> str:
    return text[text.rfind("\n", 0, start) + 1 : start]


def _sentence_start(before: str) -> bool:
    trimmed = before.rstrip(_OPENERS)
    if not trimmed:
        return True
    if trimmed[-1] not in _SENTENCE_ENDS:
        return False
    last = trimmed.split()[-1]
    return not (_is_title(last) or _is_initial(last))


def _after_label(before: str) -> bool:
    head, colon, _ = before.partition(":")
    words = head.split()
    return bool(colon) and 1 <= len(words) <= _LABEL_WORDS and words[0][0].isalpha()


def _all_caps(value: str) -> bool:
    letters = [character for character in value if character.isalpha()]
    return len(letters) >= 2 and all(character.isupper() for character in letters)


def shape(text: str, start: int, end: int) -> set[str]:
    """Return the categories of a span that depend on its text alone.

    Args:
        text: The page text.
        start: First offset of the span.
        end: Offset one past the span.

    Returns:
        The `MISS_CATEGORIES` the span falls into, `all` apart.
    """
    value = text[start:end]
    words = value.split()
    before = _line_before(text, start)
    previous = before.split()[-1:]
    categories = {_words_category(value)}
    if (previous and _is_title(previous[0])) or (words and _is_title(words[0])):
        categories.add("title")
    if _sentence_start(before):
        categories.add("sentence_start")
    if _after_label(before):
        categories.add("after_label")
    if _all_caps(value):
        categories.add("all_caps")
    if any(character in _HYPHENS_APOSTROPHES for character in value):
        categories.add("hyphen_apostrophe")
    if any(character.isalpha() and not character.isascii() for character in value):
        categories.add("diacritics")
    if any(_is_initial(word) for word in words):
        categories.add("initial")
    return categories


def alarm_categories(
    text: str, span: Span, gold: Sequence[Span], role_words: frozenset[str]
) -> set[str]:
    """Return the `ALARM_CATEGORIES` of a false alarm, `all` apart.

    Args:
        text: The page text.
        span: The prediction.
        gold: Every gold span of the document, of any type, scored or not.
        role_words: Role nouns of the corpus's language.
    """
    value = text[span.start : span.end]
    categories = shape(text, span.start, span.end) & set(ALARM_CATEGORIES)
    words = value.split()
    if len(words) == 1 and value[:1].isupper() and not _all_caps(value):
        categories.add("capitalised_word")
    first = _LETTERS.search(words[0]) if words else None
    if first and first.group().lower() in role_words:
        categories.add("role_noun")
    for other in gold:
        if other.type is span.type or not other.overlaps(span):
            continue
        categories.add("organization" if other.type is EntityType.ORGANIZATION else "other_type")
    return categories


def _uncovered(text: str, span: Span, covering: Iterable[Span]) -> bool:
    """Whether a character of the span that is not whitespace lies outside every covering span."""
    covered = [False] * (span.end - span.start)
    for other in covering:
        for offset in range(max(other.start, span.start), min(other.end, span.end)):
            covered[offset - span.start] = True
    return any(
        not covered[offset - span.start] and not text[offset].isspace()
        for offset in range(span.start, min(span.end, len(text)))
    )


# --- Counting -------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GoldSpan:
    """An analysed gold span and its categories, `all` included."""

    span: Span
    categories: frozenset[str]


def gold_spans(gold: GoldDocument, types: Iterable[EntityType]) -> list[GoldSpan]:
    """Return a document's distinct gold spans of the given types with their categories."""
    wanted = set(types)
    pages = [page.text for page in gold.document.pages]
    return [
        GoldSpan(span, frozenset({ALL, *shape(pages[span.page], span.start, span.end)}))
        for span in _spans(entity for entity in gold.gold if entity.type in wanted)
    ]


class ErrorTally:
    """Collects one system's per-document counts per type and category over a corpus."""

    def __init__(
        self,
        types: Sequence[EntityType],
        role_words: frozenset[str],
        examples: dict[str, Any] | None = None,
    ) -> None:
        """Prepare empty counts.

        Args:
            types: The analysed types scored on the corpus.
            role_words: Role nouns of the corpus's language.
            examples: Where to keep example spans, for a synthetic corpus;
                `None` keeps none.
        """
        self.types = tuple(types)
        self.role_words = role_words
        self.examples = examples
        self.misses: dict[tuple[str, str], list[MissCounts]] = {
            (str(kind), category): [] for kind in self.types for category in MISS_CATEGORIES
        }
        self.alarms: dict[tuple[str, str], list[AlarmCounts]] = {
            (str(kind), category): [] for kind in self.types for category in ALARM_CATEGORIES
        }

    def add(
        self, found: Sequence[Entity], gold: GoldDocument, expected: Sequence[GoldSpan]
    ) -> None:
        """Count one document; every key gets an entry, so resample indices stay aligned.

        Args:
            found: What the system found in the document.
            gold: The document with its gold spans.
            expected: Its analysed gold spans (`gold_spans`).
        """
        pages = [page.text for page in gold.document.pages]
        predicted = _spans(found)
        misses: dict[tuple[str, str], MissCounts] = {}
        for item in expected:
            span = item.span
            same = [
                other for other in predicted if other.type is span.type and other.overlaps(span)
            ]
            not_found = not same
            partly = bool(same) and _uncovered(pages[span.page], span, same)
            other_type = not_found and any(
                other.type is not span.type and other.overlaps(span) for other in predicted
            )
            counts = MissCounts(1, int(not_found), int(partly), int(other_type))
            for category in item.categories:
                key = (str(span.type), category)
                misses[key] = misses.get(key, MissCounts()) + counts
            if not_found or partly:
                outcome = "not_found" if not_found else "partly"
                self._example("misses", span, item.categories, pages, outcome)
        everything = _spans(gold.gold)
        alarms: dict[tuple[str, str], AlarmCounts] = {}
        for span in predicted:
            if span.type not in self.types:
                continue
            false = not any(
                other.type is span.type and other.overlaps(span) for other in everything
            )
            categories = {ALL} | alarm_categories(
                pages[span.page], span, everything, self.role_words
            )
            if false:
                self._example("false_alarms", span, categories, pages, None)
            counts = AlarmCounts(1, int(false))
            for category in categories:
                key = (str(span.type), category)
                alarms[key] = alarms.get(key, AlarmCounts()) + counts
        for key, per_document in self.misses.items():
            per_document.append(misses.get(key, MissCounts()))
        for key, per_document in self.alarms.items():
            per_document.append(alarms.get(key, AlarmCounts()))

    def _example(
        self,
        side: str,
        span: Span,
        categories: Iterable[str],
        pages: Sequence[str],
        outcome: str | None,
    ) -> None:
        if self.examples is None:
            return
        text = pages[span.page]
        example = {
            "text": text[span.start : span.end],
            "context": text[max(0, span.start - _CONTEXT) : span.end + _CONTEXT],
            **({"outcome": outcome} if outcome else {}),
        }
        by_category = self.examples.setdefault(side, {}).setdefault(str(span.type), {})
        for category in categories:
            kept = by_category.setdefault(category, [])
            if len(kept) < EXAMPLES_PER_CATEGORY:
                kept.append(example)

    def results(self, resampler: Resampler) -> dict[str, Any]:
        """Return counts, shares and rates with intervals, per type and category."""
        misses: dict[str, dict[str, Any]] = {}
        for (kind, category), per_document in self.misses.items():
            summed = total(per_document)
            overall = total(self.misses[kind, ALL])
            resampled = resampler.totals(per_document)
            misses.setdefault(kind, {})[category] = {
                "counts": summed.to_dict(),
                "share_not_found": _share(summed.not_found, overall.not_found),
                "share_partly": _share(summed.partly, overall.partly),
                **{rate: interval(per_document, resampled, rate).to_dict() for rate in MISS_RATES},
            }
        alarms: dict[str, dict[str, Any]] = {}
        for (kind, category), per_document in self.alarms.items():
            summed = total(per_document)
            overall = total(self.alarms[kind, ALL])
            alarms.setdefault(kind, {})[category] = {
                "counts": summed.to_dict(),
                "share": _share(summed.alarms, overall.alarms),
                "alarm_rate": interval(
                    per_document, resampler.totals(per_document), "alarm_rate"
                ).to_dict(),
            }
        return {"misses": misses, "false_alarms": alarms}


def _share(part: int, whole: int) -> float | None:
    return round(part / whole, 4) if whole else None


# --- Running --------------------------------------------------------------------


def is_synthetic(dataset: str, catalog: Catalog | None = None) -> bool:
    """Whether a dataset is generated, or catalogued as naming no real person."""
    spec = DATASETS[dataset]
    if spec.generated is not None:
        return True
    return not (catalog or load_catalog())[spec.catalog_id].real_personal_data


def analyse(
    config: RunConfig,
    *,
    resource_root: Path,
    cache_dir: Path,
    load_model: Callable[[str], Any] | None = None,
    load_splitter: Callable[[str], SentenceSplitter] | None = None,
    progress: Progress = lambda _: None,
    limit: int | None = None,
    keep_examples: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the configured systems on the configured splits and sort their errors.

    Args:
        config: The run configuration, as `experiments run` reads it.
        resource_root: Storage root holding `data/` and `models/`.
        cache_dir: The name models' output cache, shared with `experiments run`.
        load_model: Returns a name model by catalog id (default: from the root).
        load_splitter: Returns a NameTag model's sentence splitter by catalog id.
        progress: Told what is running (no corpus text).
        limit: Analyse only the first documents of each split.
        keep_examples: Also collect example spans of the synthetic corpora.

    Returns:
        The results, as stored in `<name>-errors.json`, and the examples by
        corpus and system (empty unless asked for; never part of the results).
    """
    catalog = load_catalog(root=resource_root)
    load_model = once(load_model or model_loader(resource_root, catalog))
    load_splitter = once(load_splitter or splitter_loader(resource_root, catalog))
    corpora: dict[str, Any] = {}
    examples: dict[str, Any] = {}
    for reference in config.datasets:
        corpus = load_corpus(reference.id, reference.split, resource_root, reference.text, limit)
        progress(f"{corpus.key}: {len(corpus.documents)} documents")
        models = corpus_models(config, corpus, cache_dir, load_model, load_splitter, catalog)
        kept: dict[str, Any] | None = (
            {} if keep_examples and is_synthetic(corpus.dataset, catalog) else None
        )
        corpora[corpus.key] = _analyse_corpus(config, corpus, models, progress, kept)
        if kept:
            examples[corpus.key] = kept
    return {
        "schema": ERRORS_SCHEMA,
        "name": f"{config.name}-errors",
        "config_name": config.name,
        "description": config.description,
        "stage": config.stage,
        "created": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "tool_version": anonymizer.core.__version__,
        "git": git_state(),
        "machine": machine(),
        "seed": config.seed,
        "resamples": config.resamples,
        "cache_floor": CACHE_FLOOR,
        "models": model_versions(config.systems, catalog),
        "datasets": {reference.id: dataset_version(reference.id) for reference in config.datasets},
        "systems": {system.name: system.describe() for system in config.systems},
        "categories": {"misses": MISS_CATEGORIES, "false_alarms": ALARM_CATEGORIES},
        "config": config.raw,
        **({"limit": limit} if limit is not None else {}),
        "corpora": corpora,
    }, examples


def _analyse_corpus(
    config: RunConfig,
    corpus: Corpus,
    models: dict[tuple[str, float], NameModel],
    progress: Progress,
    examples: dict[str, Any] | None,
) -> dict[str, Any]:
    types = scored_types(config, corpus)
    analysed = [kind for kind in ANALYSED_TYPES if kind in types]
    documents = len(corpus.documents)
    resampler = Resampler(documents, resamples(documents, config.resamples, config.seed))
    expected = [gold_spans(gold, analysed) for gold in corpus.documents]
    gold_counts = {
        str(kind): {
            category: sum(
                1
                for spans in expected
                for item in spans
                if item.span.type is kind and category in item.categories
            )
            for category in MISS_CATEGORIES
        }
        for kind in analysed
    }
    role_words = role_words_for(corpus.language)
    systems: dict[str, Any] = {}
    for system in config.systems:
        used = system_models(system, models)
        before = {model_id: (model.hits, model.misses) for model_id, model in used.items()}
        system_examples = None if examples is None else examples.setdefault(system.name, {})
        tally = ErrorTally(analysed, role_words, system_examples)
        for gold, spans in zip(corpus.documents, expected, strict=True):
            detect(system, gold.document, corpus.language, used)
            tally.add(gold.document.entities, gold, spans)
            gold.document.entities = []
        details: dict[str, Any] = {}
        for model in used.values():
            model.cache.save()
        if used:
            details["cache"] = {
                "hits": sum(model.hits - before[model_id][0] for model_id, model in used.items()),
                "misses": sum(
                    model.misses - before[model_id][1] for model_id, model in used.items()
                ),
            }
        systems[system.name] = details | (tally.results(resampler) if analysed else {})
        progress(f"{corpus.key}: {system.name} done")
    return {
        "dataset": corpus.dataset,
        "version": corpus.version,
        "split": corpus.split,
        "role": str(corpus.role),
        "language": corpus.language,
        "text": str(corpus.text_form),
        "documents": documents,
        "analysed_types": [str(kind) for kind in analysed],
        "gold": gold_counts,
        "systems": systems,
    }


def check_examples_folder(folder: Path, results: Path) -> None:
    """Refuse a folder for examples that lies in the results or that git would track.

    Args:
        folder: Where the examples would go.
        results: The results directory, which is committed.

    Raises:
        ValueError: If the folder is inside `results`, or inside a git
            repository and not ignored by it.
    """
    resolved = folder.resolve()
    if resolved.is_relative_to(results.resolve()):
        msg = "examples hold corpus text and never go into the results directory"
        raise ValueError(msg)
    existing = next(parent for parent in (resolved, *resolved.parents) if parent.exists())
    try:
        answer = subprocess.run(
            ["git", "check-ignore", "-q", str(resolved)],
            cwd=existing,
            capture_output=True,
            check=False,
        )
    except OSError:
        return
    # 0: ignored; 1: inside a repository and not ignored; 128: no repository.
    if answer.returncode == 1:
        msg = "the examples folder must be ignored by git (e.g. under outputs/)"
        raise ValueError(msg)


# --- Tables ---------------------------------------------------------------------


def markdown(results: dict[str, Any]) -> str:
    """Render the error analysis as Markdown tables, from the results alone."""
    git = results["git"]
    lines = [
        f"# {results['name']}",
        "",
        f"Error analysis of `{results['config_name']}`: commit "
        f"`{(git.get('commit') or 'unknown')[:7]}`{' (dirty tree)' if git.get('dirty') else ''}, "
        f"seed {results['seed']}, {results['resamples']} resamples, 95 % bootstrap intervals "
        "over documents. Definitions: `experiments/errors.py`.",
        "",
        "Cells: errors in the category · their share of the system's errors of that kind · "
        "rate (errors / spans in the category) [interval].",
        "",
    ]
    for key, corpus in results["corpora"].items():
        systems = [name for name, system in corpus["systems"].items() if "misses" in system]
        if not systems:
            continue
        lines += [f"## {key} · {corpus['language']} · {corpus['role']}", ""]
        lines += [f"{corpus['documents']} documents.", ""]
        for kind in corpus["analysed_types"]:
            gold = corpus["gold"][kind]
            for outcome, title, share in (
                ("not_found", "not found", "share_not_found"),
                ("partly", "found only in part", "share_partly"),
            ):
                lines += [f"### {kind} · {title}", ""]
                rows = [
                    [
                        category,
                        str(gold[category]),
                        *(
                            _cell(
                                corpus["systems"][name]["misses"][kind][category],
                                outcome,
                                share,
                                f"{outcome}_rate",
                            )
                            for name in systems
                        ),
                    ]
                    for category in MISS_CATEGORIES
                    if gold[category]
                ]
                lines += _table(["category", "gold", *systems], rows)
                lines.append("")
            other = ", ".join(
                f"{name} {corpus['systems'][name]['misses'][kind][ALL]['counts']['other_type']}"
                for name in systems
            )
            lines += [
                f"Not found as {kind}, but overlapped by a prediction of another type "
                f"(redacted all the same): {other}.",
                "",
                f"### {kind} · false alarms",
                "",
            ]
            rows = []
            for category in ALARM_CATEGORIES:
                cells = [
                    corpus["systems"][name]["false_alarms"][kind][category] for name in systems
                ]
                if not any(cell["counts"]["alarms"] for cell in cells):
                    continue
                rows.append(
                    [category, *(_cell(cell, "alarms", "share", "alarm_rate") for cell in cells)]
                )
            lines += _table(["category", *systems], rows) if rows else ["No false alarms."]
            lines.append("")
    return "\n".join(lines)


def _cell(entry: dict[str, Any], count: str, share: str, rate: str) -> str:
    value = entry[share]
    shown = UNDEFINED if value is None else f"{100 * value:.0f} %"
    return f"{entry['counts'][count]} · {shown} · {format_interval(entry[rate])}"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    return [
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
        *("| " + " | ".join(row) + " |" for row in rows),
    ]


def write_errors(results: dict[str, Any], folder: Path) -> Path:
    """Write `<name>.json` and `<name>.md` into a folder; return the JSON path."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{results['name']}.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    path.with_suffix(".md").write_text(markdown(results), encoding="utf-8")
    return path
