"""Person and address spans from a name model, cut back to the value.

The name model tags capitalised role nouns as persons: "Kupující" (buyer),
"Žadatel" (applicant), "Vedoucí odboru" (head of department), "Adult",
"Student". Contracts, terms, official letters and forms repeat them on every
page, so they made up most of the false alarms in review. A name, by
contrast, is capitalised word by word. So every person span a model reports
passes two steps:

1. Lowercase words at its edges are trimmed: "pan Novák" becomes "Novák",
   "Starosta města" becomes "Starosta". Abbreviations (`doc.`, `prof.`) and
   name particles (`z`, `von`, `de`) are not trimmed. A span with no
   capitalised word left is dropped: "žák", "zletilý student".
2. A span whose every capitalised word is a role noun of the document's
   language is dropped: "Kupujícímu", "Zákonný zástupce".

Role nouns that are also common surnames (Starosta, Žák, Kupec, Svědek,
Soudce; Child, Nurse, Judge, Clerk) are left off the lists: dropping a real
name leaks it, while a role left in costs one click in review.

The same model tags the labels of a form's address fields as addresses: "Post
Code", "Contact Address", "Telephone Number", the column and row headers next
to the handwritten values. Field-label words at the edges of an address span
are trimmed ("Post Code AB1 2CD" becomes "AB1 2CD"), and a span of nothing
else is dropped. The words name a field, never a place, so one list serves
every language: forms are often bilingual.

Rules are not filtered; their evidence is a pattern or a checksum, not
capitalisation.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable

from anonymizer.core.detect.base import Detector, describe
from anonymizer.core.types import Entity, EntityType, Page

log = logging.getLogger(__name__)

NAME_PARTICLES = frozenset(
    {"z", "ze", "von", "van", "de", "da", "di", "du", "der", "den", "la", "le"}
)
"""Lowercase words that belong to a name ("Jan z Lobkovic", "Ludwig van Beethoven")."""


def _inflect(bases: Iterable[str], cut: int, endings: Iterable[str]) -> set[str]:
    """Return every base form with its last `cut` letters replaced by each ending."""
    endings = tuple(endings)
    return {base[: len(base) - cut] + ending for base in bases for ending in endings}


# Czech paradigms, written as the endings that replace the base form's ending.
_CS_SOFT_ADJECTIVE = ("í", "ího", "ímu", "ím", "ími")  # kupující
_CS_HARD_ADJECTIVE = ("ý", "ého", "ému", "ém", "ým", "ých", "ými", "á", "é", "ou", "í")  # zákonný
_CS_AGENT = ("", "e", "i", "em", "é", "ů", "ům", "ích", "ka", "ky", "ce", "ku", "kou")  # žadatel
_CS_CE = ("ce", "ci", "cem", "ců", "cům", "cích")  # zástupce
_CS_HARD_NOUN = ("", "a", "ovi", "em", "e", "u", "i", "y", "ů", "ům", "ech")  # referent
_CS_SOFT_NOUN = ("", "e", "i", "em", "ovi", "ové", "ů", "ům", "ích")  # notář
_CS_A_NOUN = ("a", "y", "ovi", "ou", "o", "ové", "ů", "ům")  # předseda
_CS_STRANA = ("a", "y", "ě", "u", "ou", "", "ám", "ách", "ami")  # strana

# Slovak paradigms.
_SK_SOFT_ADJECTIVE = ("i", "eho", "emu", "om", "im", "ich", "imi")  # kupujúci
_SK_HARD_ADJECTIVE = ("ý", "ého", "ému", "om", "ým", "ých", "ými", "á", "ej", "ú", "ou", "é", "í")
_SK_AGENT = (
    "",
    "a",
    "ovi",
    "om",
    "ia",
    "ov",
    "och",
    "mi",
    "ka",
    "ky",
    "ke",
    "ku",
    "kou",
)  # žiadateľ
_SK_CA = ("ca", "cu", "covi", "com", "covia", "cov", "coch", "cami")  # zástupca
_SK_HARD_NOUN = ("", "a", "ovi", "om", "i", "ov", "och", "mi", "ka", "ky", "ke", "ku", "kou")
_SK_STRANA = ("a", "y", "e", "u", "ou", "", "ám", "ách", "ami")

CZECH_ROLE_WORDS = frozenset(
    _inflect(
        (
            "kupující",
            "prodávající",
            "vedoucí",
            "pronajímající",
            "objednávající",
            "převádějící",
            "nabývající",
            "smluvní",
            "pověřující",
        ),
        1,
        _CS_SOFT_ADJECTIVE,
    )
    | _inflect(
        ("zákonný", "oprávněný", "povinný", "nezletilý", "zletilý", "pověřený", "odpovědný"),
        1,
        _CS_HARD_ADJECTIVE,
    )
    | _inflect(
        (
            "žadatel",
            "spotřebitel",
            "zhotovitel",
            "objednatel",
            "pronajímatel",
            "zaměstnavatel",
            "dodavatel",
            "odběratel",
            "poskytovatel",
            "provozovatel",
            "uživatel",
            "zpracovatel",
            "věřitel",
            "ručitel",
            "jednatel",
            "nabyvatel",
            "zřizovatel",
            "pojistitel",
            "vydavatel",
            "navrhovatel",
            "zadavatel",
            "pořadatel",
            "ředitel",
            "učitel",
            "zmocnitel",
        ),
        0,
        _CS_AGENT,
    )
    | _inflect(
        (
            "zástupce",
            "plátce",
            "příjemce",
            "dopravce",
            "správce",
            "nájemce",
            "prodejce",
            "převodce",
        ),
        2,
        _CS_CE,
    )
    | _inflect(
        (
            "referent",
            "účastník",
            "dlužník",
            "nájemník",
            "pacient",
            "klient",
            "student",
            "občan",
            "poplatník",
            "primátor",
            "hejtman",
            "advokát",
            "exekutor",
        ),
        0,
        _CS_HARD_NOUN,
    )
    | _inflect(("matrikář", "notář", "lékař"), 0, _CS_SOFT_NOUN)
    | _inflect(("místostarosta", "předseda", "místopředseda"), 1, _CS_A_NOUN)
    | _inflect(("strana",), 1, _CS_STRANA)
    | {"zaměstnanec", "zaměstnance", "zaměstnanci", "zaměstnancem", "zaměstnanců"}
    | {"matrikářka", "matrikářky", "matrikářce", "matrikářku", "matrikářkou"}
)
"""Czech role nouns and the adjectives used with them, in every case."""

SLOVAK_ROLE_WORDS = frozenset(
    _inflect(
        ("kupujúci", "predávajúci", "vedúci", "prenajímajúci", "objednávajúci", "nadobúdajúci"),
        1,
        _SK_SOFT_ADJECTIVE,
    )
    | _inflect(
        ("zákonný", "oprávnený", "povinný", "maloletý", "plnoletý", "zmluvný", "poverený"),
        1,
        _SK_HARD_ADJECTIVE,
    )
    | _inflect(
        (
            "žiadateľ",
            "spotrebiteľ",
            "zhotoviteľ",
            "objednávateľ",
            "prenajímateľ",
            "zamestnávateľ",
            "dodávateľ",
            "odberateľ",
            "poskytovateľ",
            "prevádzkovateľ",
            "užívateľ",
            "spracovateľ",
            "veriteľ",
            "ručiteľ",
            "konateľ",
            "nadobúdateľ",
            "zriaďovateľ",
            "poisťovateľ",
            "riaditeľ",
            "učiteľ",
        ),
        0,
        _SK_AGENT,
    )
    | _inflect(
        ("zástupca", "platca", "príjemca", "dopravca", "správca", "nájomca", "predajca"),
        2,
        _SK_CA,
    )
    | _inflect(
        (
            "referent",
            "účastník",
            "dlžník",
            "pacient",
            "klient",
            "študent",
            "občan",
            "notár",
            "advokát",
        ),
        0,
        _SK_HARD_NOUN,
    )
    | _inflect(("strana",), 1, _SK_STRANA)
    | {"zamestnanec", "zamestnanca", "zamestnancovi", "zamestnancom", "zamestnanci", "zamestnancov"}
)
"""Slovak role nouns and the adjectives used with them, in every case."""

ENGLISH_ROLE_WORDS = frozenset(
    {
        *("adult", "adults", "minor", "minors", "children", "student", "students"),
        *("pupil", "pupils", "applicant", "applicants", "claimant", "respondent"),
        *("defendant", "plaintiff", "tenant", "tenants", "landlord", "employee"),
        *("employees", "employer", "client", "clients", "patient", "patients"),
        *("customer", "customers", "buyer", "seller", "vendor", "purchaser"),
        *("guardian", "carer", "carers", "parent", "parents", "mother", "father"),
        *("spouse", "partner", "member", "members", "resident", "residents"),
        *("occupant", "beneficiary", "signatory", "recipient", "teacher", "doctor"),
        *("worker", "practitioner", "officer", "manager", "staff", "representative"),
        *("referrer", "person", "persons", "people", "individual", "name", "surname"),
        *("forename", "signature", "gender", "sex", "next", "kin", "emergency"),
        *("contact", "social", "care", "risk"),
    }
)
"""English role nouns, and the words of a form's fields about a person
("Gender", "Next of Kin", "Adult at Risk")."""

_ROLE_WORDS_BY_LANGUAGE = {
    "cs": CZECH_ROLE_WORDS,
    "sk": SLOVAK_ROLE_WORDS,
    "en": ENGLISH_ROLE_WORDS,
}

ADDRESS_LABEL_HEADS = frozenset(
    {
        *("address", "addresses", "code", "postcode", "zip", "zipcode", "number", "no"),
        *("telephone", "phone", "mobile", "tel", "email", "e-mail", "fax"),
        *("adresa", "adresy", "adrese", "adresu", "adresou", "bydliště", "bydlisko"),
        *("bydliska", "psč", "telefon", "telefonu", "telefón", "telefónu", "číslo"),
        *("čísla", "mobil", "sídlo", "sídla", "pobyt", "pobytu"),
    }
)
"""Words that end the label of an address field: "Post Code", "Adresa", "PSČ"."""

ADDRESS_LABEL_WORDS = ADDRESS_LABEL_HEADS | frozenset(
    {
        *("home", "contact", "postal", "post", "permanent", "current", "previous"),
        *("residential", "correspondence", "registered", "mailing", "work"),
        *("trvalé", "trvalý", "trvalého", "trvalém", "kontaktní", "kontaktná"),
        *("korespondenční", "korešpondenčná", "doručovací", "doručovacia"),
        *("poštovní", "poštová", "poštové", "telefonní", "telefónne", "mobilní"),
        *("mobilné", "místo", "miesto", "směrovací", "smerovacie"),
    }
)
"""Every word of an address field's label. A word that only qualifies the
field ("Home", "Post") is trimmed only together with the word it qualifies:
"Home Farm" may be a place, "Home Address" is a label."""

_WORD = re.compile(r"\S+")
_LETTERS = re.compile(r"[^\W\d_]+")
_EDGE = ",;:!?()[]{}\"'„“”«»"


def role_words_for(language: str | None) -> frozenset[str]:
    """Return the role words of a language; every list for `None` or an unknown language.

    Args:
        language: BCP 47 tag, or `None` when the language is not known.

    Returns:
        Lowercase word forms.
    """
    primary = language.strip().lower().split("-")[0] if language else None
    if primary in _ROLE_WORDS_BY_LANGUAGE:
        return _ROLE_WORDS_BY_LANGUAGE[primary]
    return frozenset().union(*_ROLE_WORDS_BY_LANGUAGE.values())


def cut_to_name(
    text: str, start: int, end: int, role_words: frozenset[str]
) -> tuple[int, int] | None:
    """Trim a person span to its capitalised words; `None` if no name is left.

    Args:
        text: The text the span refers to.
        start: First offset of the span.
        end: Offset one past the span.
        role_words: Lowercase role words of the document's language.

    Returns:
        The trimmed span, or `None` when the span holds no capitalised word or
        only role words.
    """
    words = [(match.start(), match.end()) for match in _WORD.finditer(text, start, end)]
    while words and _is_trimmable(text[slice(*words[0])]):
        words.pop(0)
    while words and _is_trimmable(text[slice(*words[-1])]):
        words.pop()
    if not words:
        return None
    capitalised = [text[slice(*word)] for word in words if not _is_trimmable(text[slice(*word)])]
    if all(_letters(word).lower() in role_words for word in capitalised):
        return None
    # Both edge words hold letters, so the stripping stops inside them.
    return _strip_edges(text, words[0][0], words[-1][1])


def cut_to_address(text: str, start: int, end: int) -> tuple[int, int] | None:
    """Trim the labels of address fields off an address span; `None` if nothing else is left.

    A label is a run of `ADDRESS_LABEL_WORDS` ending in one of
    `ADDRESS_LABEL_HEADS` ("Post Code", "Telephone Number"), at either edge of
    the span. Words with no letter or digit at the edges go with it.

    Args:
        text: The text the span refers to.
        start: First offset of the span.
        end: Offset one past the span.

    Returns:
        The trimmed span, or `None` when the span holds only labels.
    """
    words = [
        (match.start(), match.end())
        for match in _WORD.finditer(text, start, end)
        if any(character.isalnum() for character in match.group())
    ]
    keys = [_label_key(text[slice(*word)]) for word in words]
    first = _label_length(keys)
    last = len(words) - _label_length(keys[first:][::-1], head_first=True)
    if first >= last:
        return None
    return _strip_edges(text, words[first][0], words[last - 1][1])


def _strip_edges(text: str, start: int, end: int) -> tuple[int, int]:
    while start < end and text[start] in _EDGE:
        start += 1
    while end > start and text[end - 1] in _EDGE:
        end -= 1
    return start, end


def _label_key(word: str) -> str:
    return word.strip(_EDGE).rstrip(".").lower()


def _label_length(keys: list[str], *, head_first: bool = False) -> int:
    """Number of leading keys that form an address label.

    Read forwards, a label ends at its last head word; read backwards
    (`head_first`), it must start with one.
    """
    length = 0
    for index, key in enumerate(keys):
        if key not in ADDRESS_LABEL_WORDS:
            break
        if head_first and index == 0 and key not in ADDRESS_LABEL_HEADS:
            break
        if head_first or key in ADDRESS_LABEL_HEADS:
            length = index + 1
    return length


def _letters(word: str) -> str:
    match = _LETTERS.search(word)
    return match.group(0) if match else ""


def _is_trimmable(word: str) -> bool:
    """Whether a word cannot be part of a name: no letters, or an ordinary lowercase word."""
    core = word.strip(_EDGE)
    letters = _letters(core)
    if not letters:
        return True
    return letters[0].islower() and not core.endswith(".") and core.lower() not in NAME_PARTICLES


class NamesOnly:
    """Wraps a model detector and cuts its spans back to the value.

    Person spans are cut to the name (`cut_to_name`), address spans lose the
    labels of address fields (`cut_to_address`). Other entity types pass
    unchanged.

    Attributes:
        detector: The wrapped model detector.
        role_words: Role words of the document's language.
    """

    def __init__(self, detector: Detector, language: str | None) -> None:
        """Initialize the filter.

        Args:
            detector: The model detector to wrap.
            language: BCP 47 tag selecting the role words; every list for `None`.
        """
        self.detector = detector
        self.role_words = role_words_for(language)

    @property
    def name(self) -> str:
        """Identifier used in logs and evaluation reports: the wrapped detector's."""
        return self.detector.name

    def detect(self, page: Page) -> list[Entity]:
        """Return the wrapped detector's entities, person and address spans cut to the value.

        Args:
            page: Page to scan; offsets refer to `page.text`.

        Returns:
            Entities in reading order.
        """
        kept: list[Entity] = []
        for entity in self.detector.detect(page):
            if entity.type is EntityType.PERSON:
                cut = cut_to_name(page.text, *entity.span, self.role_words)
            elif entity.type is EntityType.ADDRESS:
                cut = cut_to_address(page.text, *entity.span)
            else:
                kept.append(entity)
                continue
            if cut is None:
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("dropped, no value in the span: %s", describe(entity))
                continue
            if cut != entity.span:
                entity.start, entity.end = cut
                entity.text = page.text[cut[0] : cut[1]]
                entity.bboxes = page.bboxes_for_span(*cut)
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("trimmed to the value: %s", describe(entity))
            kept.append(entity)
        return kept
