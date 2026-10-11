"""Hand-written Czech and Slovak declension of personal names, for the name-forms set.

Only the patterns the name lists of `name_forms.py` use are covered, and each
name carries its pattern (`Paradigm`) explicitly rather than having it guessed
from its ending: "Vaněk" ends like "Hájek" but softens its stem (Vaňka), and a
list entry that needs a pattern not written here is better refused than
declined wrongly. The tests check every pattern against forms written out by
hand.

Patterns (Czech example; Slovak where it differs):

    hard       Novák, Jan, Petr        (pán; Slovak chlap)
    soft       Beneš, Tomáš, Ondřej    (muž; in Slovak declined like hard)
    mobile-e   Hájek, Pavel, Peter     (pán with the last e dropped: Hájka)
    a-masc     Svoboda, Honza          (předseda; Slovak hrdina: gen. Vargu)
    o-masc     Slovak Janko, Miško     (gen. Janka)
    adj-masc   Novotný, Malý           (mladý)
    adj-soft   Jiří                    (jarní)
    ova        Nováková                (Slovak: gen. Novákovej)
    adj-fem    Novotná, Malá           (mladá)
    a-fem      Jana, Lenka             (žena; Czech dative softens: Lence)
    ie-fem     Marie, Lucie            (Czech: dat. Marii, ins. Marií)
    ia-fem     Slovak Mária, Lucia     (gen. Márie, acc. Máriu)
    indeclinable   Megan               (foreign women's names)

Masculine animate nouns take `-ovi` in the dative and locative; a first name
before a surname takes `-u` (hard) or `-i` (soft) instead in Czech ("Janu
Novákovi"). Modern Slovak has no vocative: addressing someone uses the
nominative, so `Case.VOC` is refused for Slovak.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Case(StrEnum):
    """The seven Czech cases, by their usual abbreviation."""

    NOM = "nom"
    GEN = "gen"
    DAT = "dat"
    ACC = "acc"
    VOC = "voc"
    LOC = "loc"
    INS = "ins"


class Paradigm(StrEnum):
    """A declension pattern (see the module docstring)."""

    HARD = "hard"
    SOFT = "soft"
    MOBILE_E = "mobile-e"
    A_MASC = "a-masc"
    O_MASC = "o-masc"
    ADJ_MASC = "adj-masc"
    ADJ_SOFT = "adj-soft"
    OVA = "ova"
    ADJ_FEM = "adj-fem"
    A_FEM = "a-fem"
    IE_FEM = "ie-fem"
    IA_FEM = "ia-fem"
    INDECLINABLE = "indeclinable"


class Agreement(StrEnum):
    """The form of a possessive adjective, by the noun it agrees with."""

    MASC = "m"  # Novákův dům
    FEM = "f"  # Novákova žena
    NEUT = "n"  # Novákovo auto
    FEM_ACC = "f_acc"  # Novákovu knihu
    FEM_INS = "f_ins"  # Novákovou pomocí
    MASC_LOC = "m_loc"  # o Novákově návrhu


@dataclass(frozen=True, slots=True)
class Name:
    """A name in the nominative with its declension pattern."""

    word: str
    paradigm: Paradigm


LANGUAGES = ("cs", "sk")

_MASCULINE_NOUNS = frozenset({Paradigm.HARD, Paradigm.SOFT, Paradigm.MOBILE_E})
_VOWELS = frozenset("aáeéěiíoóuúůyý")

# Endings for gen, dat, acc, voc, loc, ins after the stem; None where a rule decides
# (the vocative of hard nouns, the softened feminine dative and locative).
_CS_ENDINGS: dict[Paradigm, tuple[str | None, ...]] = {
    Paradigm.HARD: ("a", "ovi", "a", None, "ovi", "em"),
    Paradigm.MOBILE_E: ("a", "ovi", "a", None, "ovi", "em"),
    Paradigm.SOFT: ("e", "ovi", "e", "i", "ovi", "em"),
    Paradigm.A_MASC: ("y", "ovi", "u", "o", "ovi", "ou"),
    Paradigm.ADJ_MASC: ("ého", "ému", "ého", "ý", "ém", "ým"),
    Paradigm.ADJ_SOFT: ("ího", "ímu", "ího", "í", "ím", "ím"),
    Paradigm.OVA: ("é", "é", "ou", "á", "é", "ou"),
    Paradigm.ADJ_FEM: ("é", "é", "ou", "á", "é", "ou"),
    Paradigm.A_FEM: ("y", None, "u", "o", None, "ou"),
    Paradigm.IE_FEM: ("e", "i", "i", "e", "i", "í"),
}
_SK_ENDINGS: dict[Paradigm, tuple[str, str, str, str, str]] = {
    Paradigm.HARD: ("a", "ovi", "a", "ovi", "om"),
    Paradigm.MOBILE_E: ("a", "ovi", "a", "ovi", "om"),
    Paradigm.SOFT: ("a", "ovi", "a", "ovi", "om"),
    Paradigm.A_MASC: ("u", "ovi", "u", "ovi", "om"),
    Paradigm.O_MASC: ("a", "ovi", "a", "ovi", "om"),
    Paradigm.ADJ_MASC: ("ého", "ému", "ého", "om", "ým"),
    Paradigm.OVA: ("ej", "ej", "ú", "ej", "ou"),
    Paradigm.ADJ_FEM: ("ej", "ej", "ú", "ej", "ou"),
    Paradigm.A_FEM: ("y", "e", "u", "e", "ou"),
    Paradigm.IA_FEM: ("e", "i", "u", "i", "ou"),
}
_CASE_INDEX_CS = {Case.GEN: 0, Case.DAT: 1, Case.ACC: 2, Case.VOC: 3, Case.LOC: 4, Case.INS: 5}
_CASE_INDEX_SK = {Case.GEN: 0, Case.DAT: 1, Case.ACC: 2, Case.LOC: 3, Case.INS: 4}

# Czech feminine stems soften before -e in the dative and locative (Lenka → Lence).
_CS_FEM_DATIVE = (("ch", "še"), ("k", "ce"), ("h", "ze"), ("g", "ze"), ("r", "ře"))
_CS_FEM_DATIVE_E_CARON = frozenset("dtnbpvfm")  # Jana → Janě, Eva → Evě
# The same softening before the possessive -in (Petra → Petřin, Lenka → Lenčin).
_CS_FEM_POSSESSIVE = (("ch", "š"), ("k", "č"), ("h", "ž"), ("g", "ž"), ("r", "ř"))

_CS_MASC_POSSESSIVE = {
    Agreement.MASC: "ův",
    Agreement.FEM: "ova",
    Agreement.NEUT: "ovo",
    Agreement.FEM_ACC: "ovu",
    Agreement.FEM_INS: "ovou",
    Agreement.MASC_LOC: "ově",
}
_CS_FEM_POSSESSIVE_ENDINGS = {
    Agreement.MASC: "in",
    Agreement.FEM: "ina",
    Agreement.NEUT: "ino",
    Agreement.FEM_ACC: "inu",
    Agreement.FEM_INS: "inou",
    Agreement.MASC_LOC: "ině",
}
_SK_MASC_POSSESSIVE = {**_CS_MASC_POSSESSIVE, Agreement.MASC: "ov", Agreement.MASC_LOC: "ovom"}
_SK_FEM_POSSESSIVE_ENDINGS = {**_CS_FEM_POSSESSIVE_ENDINGS, Agreement.MASC_LOC: "inom"}

_TITLES = {
    "cs": {
        Case.NOM: "pan",
        Case.GEN: "pana",
        Case.DAT: "panu",
        Case.ACC: "pana",
        Case.VOC: "pane",
        Case.LOC: "panu",
        Case.INS: "panem",
    },
    "sk": {
        Case.NOM: "pán",
        Case.GEN: "pána",
        Case.DAT: "pánovi",
        Case.ACC: "pána",
        Case.LOC: "pánovi",
        Case.INS: "pánom",
    },
}
_FEMALE_TITLES = {"cs": "paní", "sk": "pani"}


def stem(name: Name) -> str:
    """Return the part the endings attach to (Hájek → Hájk, Svoboda → Svobod)."""
    word = name.word
    if name.paradigm is Paradigm.MOBILE_E:
        if len(word) < 3 or word[-2] != "e":
            msg = f"{name.paradigm} needs a word ending in e and a consonant"
            raise ValueError(msg)
        return word[:-2] + word[-1]
    if name.paradigm in {Paradigm.HARD, Paradigm.SOFT, Paradigm.INDECLINABLE}:
        return word
    return word[:-1]


def decline(name: Name, case: Case, language: str, *, before_surname: bool = False) -> str:
    """Return a name in a case.

    Args:
        name: The name in the nominative, with its pattern.
        case: The case wanted.
        language: `cs` or `sk`.
        before_surname: The name is a first name followed by a surname, which
            changes the Czech dative and locative of masculine nouns.

    Returns:
        The declined form.

    Raises:
        ValueError: For a pattern the language does not have here, or the
            Slovak vocative.
    """
    if case is Case.NOM or name.paradigm is Paradigm.INDECLINABLE:
        return name.word
    if language == "cs":
        return _decline_cs(name, case, before_surname=before_surname)
    if language == "sk":
        return _decline_sk(name, case)
    msg = f"no declension for language {language!r}"
    raise ValueError(msg)


def _decline_cs(name: Name, case: Case, *, before_surname: bool) -> str:
    endings = _CS_ENDINGS.get(name.paradigm)
    if endings is None:
        msg = f"no Czech pattern {name.paradigm}"
        raise ValueError(msg)
    base = stem(name)
    soft = name.paradigm is Paradigm.SOFT
    if before_surname and case in {Case.DAT, Case.LOC} and name.paradigm in _MASCULINE_NOUNS:
        return base + ("i" if soft else "u")
    if name.paradigm is Paradigm.A_FEM and case in {Case.DAT, Case.LOC}:
        return _cs_feminine_dative(base)
    ending = endings[_CASE_INDEX_CS[case]]
    if ending is None:  # left: the vocative of hard masculine nouns
        return _cs_hard_vocative(base)
    return base + ending


def _cs_hard_vocative(base: str) -> str:
    if base.endswith(("k", "h", "g")):  # also -ch
        return base + "u"
    if base.endswith("r") and base[-2] not in _VOWELS:  # Petr → Petře, but Taylor → Taylore
        return base[:-1] + "ře"
    return base + "e"


def _cs_feminine_dative(base: str) -> str:
    for consonant, ending in _CS_FEM_DATIVE:
        if base.endswith(consonant):
            return base[: -len(consonant)] + ending
    return base + ("ě" if base[-1] in _CS_FEM_DATIVE_E_CARON else "e")


def _decline_sk(name: Name, case: Case) -> str:
    if case is Case.VOC:
        msg = "Slovak addresses people in the nominative; there is no vocative here"
        raise ValueError(msg)
    endings = _SK_ENDINGS.get(name.paradigm)
    if endings is None:
        msg = f"no Slovak pattern {name.paradigm}"
        raise ValueError(msg)
    return stem(name) + endings[_CASE_INDEX_SK[case]]


def possessive(name: Name, agreement: Agreement, language: str) -> str:
    """Return the possessive adjective of a name (Novák → Novákova, Jana → Janina).

    Args:
        name: A masculine noun (hard, soft, mobile-e, a-masc, o-masc) or a
            feminine first name (a-fem, ie-fem, ia-fem).
        agreement: The form, by the noun it agrees with.
        language: `cs` or `sk`.

    Returns:
        The possessive adjective.

    Raises:
        ValueError: For adjectival and indeclinable names, which have none
            (the genitive is used: "Novotného dům"), and Slovak feminine stems
            in -k, whose possessive is not settled here.
    """
    base = stem(name)
    masculine = name.paradigm in {*_MASCULINE_NOUNS, Paradigm.A_MASC, Paradigm.O_MASC}
    feminine = name.paradigm in {Paradigm.A_FEM, Paradigm.IE_FEM, Paradigm.IA_FEM}
    if language == "cs" and name.paradigm is not Paradigm.O_MASC:
        if masculine:
            return base + _CS_MASC_POSSESSIVE[agreement]
        if feminine:
            for consonant, softened in _CS_FEM_POSSESSIVE:
                if base.endswith(consonant):
                    base = base[: -len(consonant)] + softened
                    break
            return base + _CS_FEM_POSSESSIVE_ENDINGS[agreement]
    if language == "sk":
        if masculine:
            return base + _SK_MASC_POSSESSIVE[agreement]
        if feminine and not base.endswith("k"):
            return base + _SK_FEM_POSSESSIVE_ENDINGS[agreement]
    msg = f"no {language} possessive for {name.paradigm}"
    raise ValueError(msg)


def has_possessive(name: Name, language: str) -> bool:
    """Whether `possessive` can form this name's possessive adjective."""
    try:
        possessive(name, Agreement.MASC, language)
    except ValueError:
        return False
    return True


def feminine_surname(surname: Name) -> Name:
    """Return the feminine form of a masculine surname (Novák → Nováková, Malý → Malá).

    Indeclinable foreign surnames stay as they are.
    """
    if surname.paradigm is Paradigm.INDECLINABLE:
        return surname
    if surname.paradigm is Paradigm.ADJ_MASC:
        return Name(surname.word[:-1] + "á", Paradigm.ADJ_FEM)
    if surname.paradigm in {*_MASCULINE_NOUNS, Paradigm.A_MASC}:
        return Name(stem(surname) + "ová", Paradigm.OVA)
    msg = f"no feminine surname for {surname.paradigm}"
    raise ValueError(msg)


def title(female: bool, case: Case, language: str) -> str:
    """Return "pan"/"paní" (Slovak "pán"/"pani") in a case; the feminine never changes."""
    if female:
        return _FEMALE_TITLES[language]
    forms = _TITLES[language]
    if case not in forms:
        msg = f"no {language} title in the {case}"
        raise ValueError(msg)
    return forms[case]
