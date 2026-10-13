"""Held-out synthetic test set: short Czech and Slovak documents for the final RQ6 test.

RQ6 asks whether a name model trained here beats an existing one on reserved
test data. Besides the public test sets, the evaluation contract names a
held-out synthetic set "generated from templates the training data never
used". This is that set. Its templates were written for it alone: none
shares a sentence with the benchmark, the name-forms set or any generator of
training data (`tests/experiments/test_heldout.py` checks word 5-grams), and
no generator of training data may reuse them. Its names are disjoint from
the name-forms set and the benchmark. It is still written by the author of
the training data, so it is reported apart from the public sets.

Each document is one template filled with invented people: very common first
names and surnames combined arbitrarily, relatives (`Template.families`)
sharing a surname, with invented addresses, phones, e-mail addresses at the
reserved example domains, dates of birth, and birth numbers, account numbers
and IBANs whose check digits are computed here, by this module's own
arithmetic, not by the validators the pipeline uses. Names are declined by
`declension.py`. Gold spans cover the value only: not "pan", not "MUDr.", not
"bytem", not a label.

Gold types: person, address, email, phone, birth_number, date (of birth only,
as everywhere in this repository), bank_account and iban. Person spans carry
tags (facet → value), like the name-forms set, for `experiments.phenomena`:

    form       full, title-surname (after pan/paní/pán/pani), later-surname
               (a surname alone, the surname written earlier in the
               document), lone-surname (a surname alone, not written
               earlier), first-name, nickname, surname-possessive,
               first-name-possessive, initial ("J. Nováková"),
               surname-first ("Nováková Jana")
    case       nom, gen, dat, acc, voc, loc, ins (none for possessives)
    form-case  the two together
    class      the declension pattern of the word that carries the name
    gender     m, f
    context    role-noun (a role or kinship noun of `ROLE_NOUNS` right
               before the name, or after it behind a comma or a bracket:
               "svědkyně Nováková", "Jan Novák, jednatel", "(dcera)"),
               degree ("MUDr. Jana Malá"), label ("Pacient: Jan Malý"),
               plain; a span can have several
    kind       letter, contract, form, email, minutes

Template syntax (as `name_forms`, with more slots and persons):

    {A.full.gen}       full name in the genitive (gold person)
    {A.titled.dat}     "panu Novákovi": the title, then the surname (gold)
    {A.surname.nom}    the surname alone (gold)
    {A.first.voc}      the first name alone (gold)
    {A.nick.acc}       the nickname of A's first name (gold)
    {M.sposs.f}        possessive of a man's surname (gold), by `Agreement`
    {A.fposs.n}        possessive of the first name (gold)
    {A.initial.nom}    "J. Novák" (gold person)
    {A.rev}            "Novák Jan", as forms list people (gold person)
    {A.addr}           "Lipová 377, 763 15 Slušovice" (gold address)
    {A.addrblock}      the same on two lines (one gold address)
    {A.rc} {A.born} {A.phone} {A.email} {A.account} {A.iban}   (gold)
    {s~A.full.ins}     a vocalised preposition before a slot
    {A?text|text}      for a man | for a woman

Persons A to E are of either gender, alternating over the instances in
different patterns; M and N are men, V and W women.

Size: `INSTANCES` documents per template, plus the documents naming nobody
(`CONTROLS`), which use capitalised role nouns ("Nájemce", "Žadatel"), so
false alarms show. `dev` has its own few templates and names, for looking at
what the generator writes; it is not for tuning. `test` is read only with
`stage = "final"`. Instances of one template share their wording, so the
bootstrap intervals, which resample documents, are narrower than a resample
of templates would give.
"""

from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass
from datetime import date

from anonymizer.core.types import EntityType

from experiments.declension import (
    Agreement,
    Case,
    Name,
    Paradigm,
    decline,
    feminine_surname,
    has_possessive,
    possessive,
    title,
)
from experiments.name_forms import NameLists, Tag, preposition

HELDOUT_VERSION = "1"
"""Bumped whenever the generated documents change; recorded in results as the dataset version."""

SPLITS = ("dev", "test")

INSTANCES = {"dev": 4, "test": 8}
"""Documents generated from each template, each with other people."""

KINDS = ("letter", "contract", "form", "email", "minutes")

FORMS = (
    "full",
    "title-surname",
    "later-surname",
    "lone-surname",
    "first-name",
    "nickname",
    "surname-possessive",
    "first-name-possessive",
    "initial",
    "surname-first",
)
"""Forms in table order."""

CONTEXTS = ("role-noun", "degree", "label", "plain")

TYPES = frozenset(
    {
        EntityType.PERSON,
        EntityType.ADDRESS,
        EntityType.EMAIL,
        EntityType.PHONE,
        EntityType.BIRTH_NUMBER,
        EntityType.DATE,
        EntityType.BANK_ACCOUNT,
        EntityType.IBAN,
    }
)
"""Every type the documents mark."""


@dataclass(frozen=True, slots=True)
class Template:
    """One document template.

    Attributes:
        name: Unique id; seeds the people of its documents.
        kind: One of `KINDS`.
        lines: The document's lines (syntax in the module docstring).
        families: Groups of person letters sharing a surname ("AB").
        children: Letters of people born 2010 to 2019 rather than 1963 to 2002.
        elders: Letters of people born 1954 to 1962, a parent of a grown-up.
    """

    name: str
    kind: str
    lines: tuple[str, ...]
    families: tuple[str, ...] = ()
    children: str = ""
    elders: str = ""


@dataclass(frozen=True, slots=True)
class GoldSpan:
    """A gold span in a generated document; only person spans carry tags."""

    type: EntityType
    start: int
    end: int
    tags: tuple[Tag, ...] = ()


@dataclass(frozen=True, slots=True)
class HeldoutDocument:
    """One generated document with its gold spans."""

    template: str
    text: str
    spans: tuple[GoldSpan, ...]


@dataclass(frozen=True, slots=True)
class Person:
    """A generated person with every value a template may ask for."""

    female: bool
    first: Name
    surname: Name
    family_surname: Name
    nickname: Name | None
    street: str
    town: str
    born: date
    birth_number: str
    phone: str
    email: str
    account: str
    iban: str


H, S, E = Paradigm.HARD, Paradigm.SOFT, Paradigm.MOBILE_E
AM, OM, ADJ = Paradigm.A_MASC, Paradigm.O_MASC, Paradigm.ADJ_MASC
AF, IE, IA = Paradigm.A_FEM, Paradigm.IE_FEM, Paradigm.IA_FEM


def _names(*entries: tuple[str, Paradigm]) -> tuple[Name, ...]:
    return tuple(Name(word, paradigm) for word, paradigm in entries)


NAMES: dict[str, dict[str, NameLists]] = {
    "cs": {
        "dev": NameLists(
            male_first=_names(("Robert", H), ("Igor", H), ("Patrik", H), ("Jindřich", H)),
            female_first=_names(("Iveta", AF), ("Dana", AF), ("Vlasta", AF), ("Helena", AF)),
            surnames=_names(
                ("Kubát", H),
                ("Vlach", H),
                ("Holý", ADJ),
                ("Pavlík", H),
                ("Hanák", H),
                ("Mareš", S),
            ),
            nicknames={
                "Jindřich": Name("Jindra", AM),
                "Dana": Name("Danka", AF),
                "Helena": Name("Helenka", AF),
            },
        ),
        "test": NameLists(
            male_first=_names(
                ("Vladimír", H),
                ("Radim", H),
                ("Václav", H),
                ("Dominik", H),
                ("Adam", H),
                ("Richard", H),
                ("Antonín", H),
                ("Oldřich", H),
                ("Kamil", H),
                ("Jaromír", H),
                ("Libor", H),
                ("Aleš", S),
                ("Matěj", S),
                ("Bohumil", H),
            ),
            female_first=_names(
                ("Simona", AF),
                ("Radka", AF),
                ("Michaela", AF),
                ("Šárka", AF),
                ("Romana", AF),
                ("Blanka", AF),
                ("Ludmila", AF),
                ("Renata", AF),
                ("Irena", AF),
                ("Kristýna", AF),
                ("Adéla", AF),
                ("Jarmila", AF),
                ("Natálie", IE),
                ("Silvie", IE),
            ),
            surnames=_names(
                ("Kratochvíl", H),
                ("Doležal", H),
                ("Urban", H),
                ("Polák", H),
                ("Charvát", H),
                ("Mach", H),
                ("Kadlec", S),
                ("Kříž", S),
                ("Bednář", S),
                ("Jelínek", E),
                ("Štěpánek", E),
                ("Sedláček", E),
                ("Matoušek", E),
                ("Fiala", AM),
                ("Říha", AM),
                ("Zelenka", AM),
                ("Kopecký", ADJ),
                ("Hrubý", ADJ),
                ("Konečný", ADJ),
            ),
            nicknames={
                "Václav": Name("Venca", AM),
                "Antonín": Name("Tonda", AM),
                "Oldřich": Name("Olda", AM),
                "Jaromír": Name("Míra", AM),
                "Adam": Name("Áda", AM),
                "Bohumil": Name("Bohouš", S),
                "Kristýna": Name("Týna", AF),
                "Ludmila": Name("Lída", AF),
                "Jarmila": Name("Jarka", AF),
                "Blanka": Name("Blanička", AF),
                "Irena": Name("Irenka", AF),
            },
        ),
    },
    "sk": {
        "dev": NameLists(
            male_first=_names(("Viliam", H), ("Adrián", H), ("Radoslav", H)),
            female_first=_names(
                ("Viera", AF), ("Tatiana", AF), ("Patrícia", IA), ("Erika", AF), ("Zora", AF)
            ),
            surnames=_names(("Hric", S), ("Jurčák", H), ("Bednárik", H), ("Ondrejka", AM)),
            nicknames={
                "Viliam": Name("Vilo", OM),
                "Radoslav": Name("Rado", OM),
                "Viera": Name("Vierka", AF),
            },
        ),
        "test": NameLists(
            male_first=_names(
                ("Milan", H),
                ("Marián", H),
                ("Rastislav", H),
                ("Branislav", H),
                ("Matej", S),
                ("Ľubomír", H),
                ("Miroslav", H),
                ("Dušan", H),
                ("Vladislav", H),
                ("Ernest", H),
            ),
            female_first=_names(
                ("Kristína", AF),
                ("Dominika", AF),
                ("Alžbeta", AF),
                ("Renáta", AF),
                ("Adriána", AF),
                ("Miroslava", AF),
                ("Silvia", IA),
                ("Natália", IA),
                ("Viktória", IA),
                ("Oľga", AF),
            ),
            surnames=_names(
                ("Polák", H),
                ("Kráľ", H),
                ("Kolesár", H),
                ("Rusnák", H),
                ("Michalík", H),
                ("Lipták", H),
                ("Pekár", H),
                ("Krištof", H),
                ("Gajdoš", S),
                ("Dudáš", S),
                ("Ďurica", AM),
                ("Zelený", ADJ),
                ("Hladký", ADJ),
            ),
            nicknames={
                "Milan": Name("Milanko", OM),
                "Rastislav": Name("Rasťo", OM),
                "Branislav": Name("Braňo", OM),
                "Ľubomír": Name("Ľubo", OM),
                "Miroslav": Name("Miro", OM),
                "Dominika": Name("Nika", AF),
                "Alžbeta": Name("Betka", AF),
                "Renáta": Name("Renátka", AF),
                "Miroslava": Name("Mirka", AF),
            },
        ),
    },
}
"""Names per language and split; no name appears in both splits of a language."""

STREETS = {
    "cs": (
        "Lipová",
        "Polní",
        "Školní",
        "Zahradní",
        "Javorová",
        "Na Výsluní",
        "Družstevní",
        "Sadová",
        "Krátká",
        "Pod Lesem",
        "Luční",
        "Jabloňová",
        "K Rybníku",
        "Nádražní",
        "Okružní",
        "Větrná",
        "Za Školou",
    ),
    "sk": (
        "Hlavná",
        "Lipová",
        "Záhradná",
        "Školská",
        "Poľná",
        "Družstevná",
        "Krátka",
        "Slnečná",
        "Jarná",
        "Mlynská",
        "Športová",
        "Agátová",
        "Topoľová",
        "Nová",
        "Lúčna",
    ),
}
"""Street names that name no person, so an address holds no name of its own."""

TOWNS = {
    "cs": (
        ("280 02", "Kolín"),
        ("390 01", "Tábor"),
        ("397 01", "Písek"),
        ("586 01", "Jihlava"),
        ("674 01", "Třebíč"),
        ("767 01", "Kroměříž"),
        ("750 02", "Přerov"),
        ("755 01", "Vsetín"),
        ("796 01", "Prostějov"),
        ("537 01", "Chrudim"),
        ("339 01", "Klatovy"),
        ("266 01", "Beroun"),
        ("276 01", "Mělník"),
        ("591 01", "Žďár nad Sázavou"),
        ("686 01", "Uherské Hradiště"),
        ("612 00", "Brno"),
        ("140 00", "Praha 4"),
        ("702 00", "Ostrava"),
    ),
    "sk": (
        ("010 01", "Žilina"),
        ("917 01", "Trnava"),
        ("949 01", "Nitra"),
        ("080 01", "Prešov"),
        ("058 01", "Poprad"),
        ("960 01", "Zvolen"),
        ("911 01", "Trenčín"),
        ("974 01", "Banská Bystrica"),
        ("071 01", "Michalovce"),
        ("934 01", "Levice"),
        ("040 01", "Košice"),
        ("831 04", "Bratislava"),
        ("034 01", "Ružomberok"),
        ("905 01", "Senica"),
    ),
}
"""Postcode and town; towns are not personal data, the address as a whole is."""

BANK_CODES = {
    "cs": ("0100", "0300", "0600", "0800", "2010", "3030", "5500", "6210"),
    "sk": ("0200", "0900", "1100", "5600", "7500", "8330"),
}
_COUNTRY = {"cs": "CZ", "sk": "SK"}
_DOMAINS = ("example.com", "example.org", "example.net")

DEGREES = frozenset({"Bc.", "Ing.", "JUDr.", "Mgr.", "MUDr.", "PhDr.", "RNDr."})
"""Academic degrees written before a name; the gold span starts after them."""

ROLE_NOUNS = {
    "cs": frozenset(
        {
            "bratr",
            "chovatele",
            "chovatelky",
            "dcera",
            "dárce",
            "kolega",
            "kolegyně",
            "kupující",
            "makléře",
            "makléřky",
            "nájemce",
            "nájemkyně",
            "objednatel",
            "objednatelka",
            "občan",
            "občanka",
            "pacient",
            "pacientka",
            "pracovnice",
            "pracovník",
            "prodávající",
            "pronajímatel",
            "pronajímatele",
            "pronajímatelka",
            "předseda",
            "předsedkyně",
            "předávající",
            "přebírající",
            "redaktor",
            "redaktorka",
            "sestra",
            "soused",
            "sousedka",
            "spolužačky",
            "spolužáka",
            "starosta",
            "starostka",
            "svědek",
            "svědkyně",
            "syn",
            "technik",
            "technička",
            "učitel",
            "učitelka",
            "zapisovatelem",
            "zapisovatelkou",
            "zaměstnanec",
            "zaměstnankyně",
            "zhotovitel",
            "zhotovitelka",
            "ředitel",
            "ředitele",
            "ředitelka",
            "žáka",
            "žákyně",
        }
    ),
    "sk": frozenset(
        {
            "brat",
            "dcéra",
            "dlžník",
            "dlžníčka",
            "dôverník",
            "dôverníčka",
            "hospodár",
            "hospodárka",
            "kolega",
            "kolegyňa",
            "mama",
            "nájomca",
            "nájomcu",
            "nájomkyňa",
            "otec",
            "poistník",
            "poistníčka",
            "poslanec",
            "poslankyňa",
            "predsedajúca",
            "predsedajúci",
            "prenajímateľ",
            "prenajímateľka",
            "riaditeľa",
            "riaditeľky",
            "ručiteľ",
            "ručiteľka",
            "suseda",
            "susedky",
            "svedok",
            "svedkyňa",
            "správca",
            "správkyňa",
            "sestra",
            "syn",
            "veriteľ",
            "veriteľka",
            "zamestnanec",
            "zamestnankyňa",
            "zapisovateľ",
            "zapisovateľka",
            "študenta",
            "študentku",
        }
    ),
}
"""Role and kinship nouns, in the forms the templates write next to a name (`context` tag)."""

TEMPLATES: dict[str, dict[str, tuple[Template, ...]]] = {
    "cs": {
        "dev": (
            Template(
                "cs-dev-penalty",
                "letter",
                (
                    "{A.full.nom}",
                    "{A.addr}",
                    "Věc: Žádost o prominutí penále",
                    "Vážen{B?ý|á} {B.titled.voc},",
                    "žádám o prominutí penále za opožděnou platbu pojistného za srpen. Platbu jsem"
                    " odeslal{A?|a} včas, banka ji však připsala až o týden později; potvrzení"
                    " přikládám.",
                    "V této věci mě může zastupovat {C?můj bratr|moje sestra} {C.full.nom}."
                    " {C.surname.nom} má ode mě plnou moc.",
                    "S pozdravem",
                    "{A.full.nom}",
                ),
                families=("AC",),
            ),
            Template(
                "cs-dev-bicycle",
                "contract",
                (
                    "Kupní smlouva – jízdní kolo",
                    "Prodávající: {A.full.nom}, RČ {A.rc}, {A.addr}",
                    "Kupující: {B.full.nom}, tel. {B.phone}",
                    "Prodávající prodává kupujícímu horské kolo za 9 500 Kč, které kupující"
                    " uhradil{B?|a} na účet {A.account}.",
                    "{A.surname.nom} prohlašuje, že kolo koupil{A?|a} v roce 2023 od {C?pana|paní}"
                    " {C.full.gen}. {B.surname.nom} kolo převzal{B?|a} bez výhrad.",
                    "V Brně dne 3. října 2026",
                ),
            ),
            Template(
                "cs-dev-shift",
                "email",
                (
                    "Od: {A.full.nom} <{A.email}>",
                    "Komu: {B.email}",
                    "Předmět: Zítřejší směna",
                    "Ahoj {B.nick.voc},",
                    "vzal{B?|a} bys za mě zítra ranní směnu? {C.surname.nom} mi výměnu už"
                    " schválil{C?|a}. {D.fposs.f} sestra mě odveze k lékaři.",
                    "Díky, {A.first.nom}",
                ),
            ),
            Template(
                "cs-dev-editors",
                "minutes",
                (
                    "Zápis z porady redakce",
                    "Přítomni: {A.full.nom}, {B.full.nom}, {C.full.nom}",
                    "1. {A.surname.nom} navrhl{A?|a} téma listopadového čísla."
                    " {B?Redaktor|Redaktorka} {B.surname.nom} připraví rozhovor {s~D.full.ins}.",
                    "2. Fotografie dodá {C.initial.nom}.",
                    "Zapsal{C?|a}: {C.full.nom}",
                ),
            ),
        ),
        "test": (
            # letters
            Template(
                "cs-letter-noise",
                "letter",
                (
                    "{A.full.nom}",
                    "{A.addr}",
                    "V Kolíně dne 4. listopadu 2026",
                    "Věc: Stížnost na rušení nočního klidu",
                    "Vážen{B?ý|á} {B.titled.voc},",
                    "obracím se na Vás jako na správce našeho domu. Už třetí týden se z bytu nade"
                    " mnou ozývá po desáté hodině večer hlasitá hudba. Byt podle mých informací"
                    " užívá {C.full.nom} s rodinou.",
                    "{C?Se sousedem|Se sousedkou} jsem se snažil{A?|a} situaci vyřešit osobně, ale"
                    " {C.surname.nom} odmítá cokoli změnit. Prosím proto o písemné upozornění.",
                    "Stejný problém mi potvrdil{D?|a} i {D?soused|sousedka} {D.full.nom} z bytu"
                    " č. 7, {D?který|která} bydlí hned vedle.",
                    "Děkuji za vyřízení.",
                    "S pozdravem",
                    "{A.full.nom}",
                    "tel. {A.phone}",
                ),
            ),
            Template(
                "cs-letter-absence",
                "letter",
                (
                    "Mgr. {C.full.nom}",
                    "třídní učitel{C?|ka} 4. B",
                    "Vážen{C?ý|á} {C.titled.voc},",
                    "omlouvám {B?svého syna|svou dceru} {B.full.acc} z vyučování ve dnech 9. až"
                    " 13. listopadu. {B.first.nom} {B?onemocněl|onemocněla} angínou a podle lékaře"
                    " musí zůstat doma ještě do pátku.",
                    "Zadané úkoly nám může předat {D.fposs.f} maminka, která bydlí ve vedlejším"
                    " vchodě. Pokud by bylo potřeba cokoli dalšího, zastihnete mě na čísle"
                    " {A.phone}.",
                    "Děkuji za pochopení.",
                    "{A.full.nom}",
                ),
                families=("AB",),
                children="BD",
            ),
            Template(
                "cs-letter-reference",
                "letter",
                (
                    "Pracovní posudek",
                    "{A?Zaměstnanec|Zaměstnankyně}: {A.rev}",
                    "Datum narození: {A.born}",
                    "Bydliště: {A.addr}",
                    "{A?Pan|Paní} {A.full.nom} pracoval{A?|a} v naší společnosti od března 2019 do"
                    " září 2026 jako {A?skladník|skladnice}. {A.surname.nom} odpovídal{A?|a} za"
                    " příjem zboží a vedení skladové evidence a své úkoly plnil{A?|a} spolehlivě.",
                    "Na {A.surname.loc} jsme oceňovali hlavně pečlivost a ochotu zaskočit za"
                    " kolegy. Vedoucí skladu {B.full.nom} navrhl{B?|a} {A.surname.acc} dvakrát na"
                    " mimořádnou odměnu.",
                    "Pracovní poměr skončil dohodou na žádost {A?zaměstnance|zaměstnankyně}.",
                    "V Jihlavě dne 30. září 2026",
                    "Ing. {C.full.nom}",
                    "personální ředitel{C?|ka}",
                ),
            ),
            Template(
                "cs-letter-vehicle",
                "letter",
                (
                    "Městský úřad Kroměříž, odbor dopravy",
                    "Č. j.: MUKM/41870/2026",
                    "Vyřizuje: {B.full.nom}",
                    "Telefon: {B.phone}",
                    "{A?Pan|Paní}",
                    "{A.full.nom}",
                    "{A.addrblock}",
                    "Výzva k odstranění vozidla z pozemní komunikace",
                    "Vážen{A?ý|á} {A.titled.voc},",
                    "v ulici U Cihelny stojí déle než šest měsíců osobní automobil bez platné"
                    " technické prohlídky. Podle registru silničních vozidel jste jeho"
                    " provozovatel{A?em|kou} Vy. Vyzýváme Vás, abyste vozidlo do dvou měsíců od"
                    " doručení této výzvy odstranil{A?|a}.",
                    "Na vozidlo upozornil{E?|a} úřad {E?místní občan|místní občanka} {E.full.nom};"
                    " {E.surname.nom} k oznámení přiložil{E?|a} i fotografie.",
                    "Po marném uplynutí lhůty bude vozidlo odstraněno na náklady provozovatele.",
                    "{C.full.nom}",
                    "vedoucí odboru dopravy",
                ),
            ),
            Template(
                "cs-letter-cottage",
                "letter",
                (
                    "{A.full.nom}",
                    "{A.addrblock}",
                    "Ahoj {A.nick.voc},",
                    "moc děkujeme za pozvání na chalupu. Přijedeme v pátek večer, protože"
                    " {B.first.nom} končí v práci až v pět. {C.nick.nom} s námi bohužel nepojede,"
                    " v sobotu dělá zkoušky na vysoké.",
                    "Vezu {W.fposs.f_acc} bábovku a pro {D.first.acc} knížky, které jsem"
                    " {D?mu|jí} minule slíbil{E?|a}. Pozdravuj od nás i {M.nick.acc}, ať nezapomene"
                    " na rybářské pruty.",
                    "Těšíme se!",
                    "{E.first.nom}",
                ),
            ),
            # contracts
            Template(
                "cs-contract-car",
                "contract",
                (
                    "Kupní smlouva na ojeté motorové vozidlo",
                    "Prodávající: {A.full.nom}, datum narození {A.born}, trvalý pobyt {A.addr}",
                    "Kupující: {B.full.nom}, rodné číslo {B.rc}, trvalý pobyt {B.addr}",
                    "I. Předmět smlouvy",
                    "Prodávající prodává kupujícímu osobní automobil Škoda Fabia, rok výroby 2012,"
                    " najeto 168 400 km. V letech 2012 až 2019 vůz vlastnil{C?|a} {C?pan|paní}"
                    " {C.full.nom}, od {C?kterého|které} jej prodávající koupil{A?|a}.",
                    "II. Kupní cena",
                    "Kupní cena činí 118 000 Kč a kupující ji uhradí převodem na účet prodávajícího"
                    " č. {A.account} do tří dnů od podpisu.",
                    "III. Prohlášení stran",
                    "{A.surname.nom} prohlašuje, že na vozidle nejsou skryté vady, o nichž by"
                    " věděl{A?|a}. {B.surname.nom} potvrzuje, že vozidlo před koupí prohlédl{B?|a}"
                    " a absolvoval{B?|a} zkušební jízdu.",
                    "V Přerově dne 2. října 2026",
                    "prodávající: {A.full.nom}",
                    "kupující: {B.full.nom}",
                ),
            ),
            Template(
                "cs-contract-flat",
                "contract",
                (
                    "Smlouva o nájmu bytu",
                    "{A?Pronajímatel|Pronajímatelka}: {A.full.nom}, r. č. {A.rc}",
                    "trvale bytem {A.addr}",
                    "{B?Nájemce|Nájemkyně}: {B.full.nom}, nar. {B.born}",
                    "trvale bytem {B.addr}",
                    "1. Pronajímatel dává nájemci do nájmu dvoupokojový byt č. 12 v posledním patře"
                    " svého domu na dobu dvou let.",
                    "2. Měsíční nájemné ve výši 13 800 Kč se platí vždy do 10. dne kalendářního"
                    " měsíce na účet pronajímatele č. {A.account}.",
                    "3. Pronajímatel souhlasí, aby v bytě bydlel{C?|a} také {C?syn|dcera} nájemce"
                    " {C.full.nom}.",
                    "4. {B.surname.nom} převzal{B?|a} při podpisu dva klíče od bytu a jeden klíč od"
                    " sklepa. Drobné opravy hradí nájemce.",
                    "5. Závady hlaste {D?bratrovi|sestře} pronajímatele {D.full.dat}, tel."
                    " {D.phone}.",
                    "V Táboře dne 15. září 2026",
                    "{A.full.nom}, pronajímatel{A?|ka}",
                    "{B.full.nom}, nájem{B?ce|kyně}",
                ),
                families=("BC", "AD"),
            ),
            Template(
                "cs-contract-bathroom",
                "contract",
                (
                    "Smlouva o dílo",
                    "{A?Objednatel|Objednatelka}: {A.full.nom}, {A.addr}, tel. {A.phone}",
                    "{B?Zhotovitel|Zhotovitelka}: {B.full.nom}, místo podnikání {B.addr}",
                    "1. Zhotovitel provede pro objednatele rekonstrukci koupelny v bytě na výše"
                    " uvedené adrese, a to nejpozději do 30. listopadu 2026.",
                    "2. Cena díla činí 86 400 Kč včetně materiálu. Zálohu 20 000 Kč uhradí"
                    " objednatel na účet zhotovitele č. {B.account} před zahájením prací.",
                    "3. Práce řídí zhotovitel osobně. V době {B?jeho|její} nepřítomnosti {B?ho|ji}"
                    " zastupuje {C?pracovník|pracovnice} {C.full.nom}.",
                    "4. {A.surname.nom} zpřístupní byt každý všední den mezi sedmou a čtvrtou."
                    " {B.surname.nom} odpovídá za úklid po skončení prací a za odvoz suti.",
                    "5. Na provedené práce poskytuje zhotovitel záruku 24 měsíců.",
                    "V Olomouci dne 1. října 2026",
                    "objednatel: {A.initial.nom}",
                    "zhotovitel: {B.initial.nom}",
                ),
            ),
            Template(
                "cs-contract-gift",
                "contract",
                (
                    "Darovací smlouva",
                    "Dárce: {M.full.nom}, RČ {M.rc}, s trvalým pobytem {M.addr}",
                    "{A?Obdarovaný|Obdarovaná}: {A.full.nom}, s trvalým pobytem {A.addr}",
                    "I. Dárce je vlastníkem pozemku parc. č. 1247/3 v katastrálním území Klatovy,"
                    " který zdědil po své matce {V.full.loc}.",
                    "II. Dárce daruje tento pozemek {A?svému synovi|své dceři} {A.full.dat}"
                    " a {A?obdarovaný|obdarovaná} dar s díky přijímá.",
                    "III. Sestra dárce {W.full.nom} prohlašuje, že s darováním souhlasí a nebude"
                    " vůči {A?obdarovanému|obdarované} uplatňovat žádné nároky.",
                    "IV. Návrh na vklad vlastnického práva do katastru nemovitostí podá"
                    " {A.surname.nom} do 30 dnů od podpisu této smlouvy.",
                    "V Klatovech dne 22. září 2026",
                    "{M.full.nom}",
                    "{A.full.nom}",
                    "{W.full.nom}",
                ),
                families=("MAV",),
                elders="M",
            ),
            Template(
                "cs-contract-dpp",
                "contract",
                (
                    "Dohoda o provedení práce",
                    "Zaměstnavatel: Základní škola Polná, příspěvková organizace, zastoupená"
                    " {A?ředitelem|ředitelkou} Mgr. {A.full.ins}",
                    "{B?Zaměstnanec|Zaměstnankyně}: {B?pan|paní} {B.full.nom}, narozen{B?|a}"
                    " {B.born}, bydliště {B.addr}",
                    "1. Zaměstnanec se zavazuje vést od 1. 11. 2026 do 31. 1. 2027 kroužek"
                    " robotiky pro žáky druhého stupně v rozsahu nejvýše 120 hodin.",
                    "2. Odměna činí 250 Kč za hodinu a bude vyplácena měsíčně na účet"
                    " č. {B.account}.",
                    "3. Práci organizuje {C?zástupce|zástupkyně} ředitele {C.full.nom}."
                    " {C.surname.nom} také potvrzuje výkaz odpracovaných hodin.",
                    "4. {B.surname.nom} bere na vědomí, že musí dodržovat školní řád a pokyny"
                    " k bezpečnosti práce.",
                    "V Polné dne 20. října 2026",
                    "{A.full.nom}, ředitel{A?|ka} školy",
                    "{B.full.nom}",
                ),
            ),
            # forms
            Template(
                "cs-form-library",
                "form",
                (
                    "Přihláška čtenáře – Městská knihovna Písek",
                    "Příjmení a jméno: {A.rev}",
                    "Datum narození: {A.born}",
                    "Adresa trvalého pobytu: {A.addr}",
                    "{B?Zákonný zástupce|Zákonná zástupkyně}: {B.full.nom}",
                    "Telefon zákonného zástupce: {B.phone}",
                    "E-mail: {B.email}",
                    "Souhlasím s tím, aby {A?můj syn|moje dcera} {A.first.nom} {A?mohl|mohla}"
                    " půjčovat i knihy z oddělení pro dospělé.",
                    "Přihlášku přijal{C?|a}: {C.initial.nom}",
                    "Poznámka knihovny: čtenářský průkaz vydán 7. 10. 2026, poplatek 100 Kč"
                    " zaplacen.",
                ),
                families=("AB",),
                children="A",
            ),
            Template(
                "cs-form-accident",
                "form",
                (
                    "Záznam o dopravní nehodě",
                    "Datum a místo: 11. 10. 2026, 16.40, parkoviště u obchodního centra v Chrudimi",
                    "Řidič vozidla A: {A.full.nom}, {A.addr}, tel. {A.phone}",
                    "Řidič vozidla B: {B.full.nom}, {B.addr}, tel. {B.phone}",
                    "{C?Svědek|Svědkyně}: {C.full.nom}, tel. {C.phone}",
                    "Popis: Vozidlo A couvalo z parkovacího místa a narazilo do boku projíždějícího"
                    " vozidla B. {A.surname.nom} uvádí, že {A?mu|jí} výhled zakrývala zaparkovaná"
                    " dodávka. {B.surname.nom} nehodu nezavinil{B?|a} a nebyl{B?|a}"
                    " zraněn{B?|a}.",
                    "{C?Svědek|Svědkyně} {C.surname.nom} průběh nehody potvrzuje.",
                    "Viditelná poškození: vozidlo A zadní nárazník, vozidlo B přední a zadní dveře"
                    " vpravo.",
                ),
            ),
            Template(
                "cs-form-leave",
                "form",
                (
                    "Žádost o uvolnění žáka z vyučování",
                    "Jméno a příjmení žáka: {A.full.nom}",
                    "Třída: 6. A",
                    "{B?Třídní učitel|Třídní učitelka}: Mgr. {B.full.nom}",
                    "Termín: 16. 11. – 20. 11. 2026",
                    "Důvod: rodinná dovolená",
                    "Žádám o uvolnění {A?svého syna|své dcery} {A.first.gen} z vyučování"
                    " v uvedeném termínu. Zameškané učivo si {A.first.nom} doplní podle sešitů"
                    " {D?spolužáka|spolužačky} {D.full.gen}.",
                    "{E?Zákonný zástupce|Zákonná zástupkyně}: {E.full.nom}, tel. {E.phone}",
                    "Vyjádření třídní{B?ho učitele|učitelky}: souhlasím, {B.initial.nom}",
                ),
                families=("AE",),
                children="AD",
            ),
            Template(
                "cs-form-dog",
                "form",
                (
                    "Ohlášení držení psa – místní poplatek ze psů",
                    "{A?Držitel|Držitelka} psa: {A.rev}",
                    "Rodné číslo: {A.rc}",
                    "Trvalý pobyt: {A.addr}",
                    "Kontakt: {A.phone}, {A.email}",
                    "Jméno psa: Bertík, kříženec, stáří 3 roky",
                    "Pes je držen od: 2. září 2026, převzat od {B?chovatele|chovatelky}"
                    " {B.full.gen}",
                    "Poplatek bude hrazen převodem z účtu č. {A.account}.",
                    "Prohlašuji, že uvedené údaje jsou pravdivé. Pokud budu dlouhodobě mimo domov,"
                    " bude psa držet {C?můj bratr|moje sestra} {C.full.nom}.",
                    "Datum a podpis: 4. 10. 2026, {A.initial.nom}",
                ),
                families=("AC",),
            ),
            Template(
                "cs-form-gp",
                "form",
                (
                    "Registrace k praktickému lékaři",
                    "Ordinace: MUDr. {A.full.nom}, {A?praktický lékař|praktická lékařka}",
                    "{B?Pacient|Pacientka}: {B.full.nom}",
                    "Rodné číslo: {B.rc}",
                    "Bydliště: {B.addr}",
                    "Telefon: {B.phone}",
                    "Osoba, které lze podávat informace o zdravotním stavu: {C.full.nom}"
                    " ({C?syn|dcera}), tel. {C.phone}",
                    "{D?Předchozí praktický lékař|Předchozí praktická lékařka}: MUDr. {D.full.nom},"
                    " ordinace ukončila činnost 30. 6. 2026.",
                    "{B?Pacient|Pacientka} souhlasí s vyžádáním zdravotní dokumentace od MUDr."
                    " {D.surname.gen}. {B.surname.nom} je alergick{B?ý|á} na penicilin.",
                ),
                families=("BC",),
            ),
            # e-mails
            Template(
                "cs-email-orders",
                "email",
                (
                    "Od: {A.full.nom} <{A.email}>",
                    "Komu: {B.full.nom} <{B.email}>",
                    "Předmět: Podklady na pondělní poradu",
                    "Ahoj {B.first.voc},",
                    "posílám tabulku s objednávkami za září. Čísla za Moravu mi ještě"
                    " nedodal{C?|a} {C.surname.nom}, ale slíbil{C?|a} je do zítřka.",
                    "Na poradu chce přijít i {D.nick.nom} z účtárny, tak {D?ho|ji} prosím přidej"
                    " do pozvánky. A {E.fposs.f} prezentace je na sdíleném disku ve složce Obchod.",
                    "Díky a měj se,",
                    "{A.first.nom}",
                ),
            ),
            Template(
                "cs-email-dishwasher",
                "email",
                (
                    "Od: Zákaznická podpora <podpora@example.net>",
                    "Komu: {A.email}",
                    "Předmět: Reklamace č. 2026/1184",
                    "Dobrý den, {A.titled.voc},",
                    "děkujeme za zaslání reklamace myčky nádobí. {B?Technik|Technička} {B.full.nom}"
                    " Vás bude kontaktovat na čísle {A.phone} a domluví s Vámi termín návštěvy."
                    " {B.surname.nom} bude mít s sebou platební terminál, případný doplatek tedy"
                    " můžete uhradit kartou.",
                    "Při návštěvě si prosím připravte doklad o koupi. Vaši reklamaci má na starosti"
                    " {C?kolega|kolegyně} {C.full.nom}, s dotazy se proto obracejte přímo"
                    " na {C?něj|ni}.",
                    "S pozdravem",
                    "{D.full.nom}",
                    "zákaznická podpora",
                ),
            ),
            Template(
                "cs-email-parking",
                "email",
                (
                    "Od: {A.full.nom} <{A.email}>",
                    "Komu: vybor@example.org",
                    "Předmět: Fwd: Parkování v průjezdu",
                    "Dobrý den,",
                    "přeposílám zprávu od {B?pana|paní} {B.full.gen} z prvního patra. Stížnost se"
                    " týká auta v průjezdu: {M.sposs.n} auto tam stojí už druhý týden"
                    " a {M.surname.nom} na upozornění zatím nereagoval. Navrhuji to probrat na"
                    " příští schůzi výboru.",
                    "{A.full.nom}",
                    "---------- Přeposlaná zpráva ----------",
                    "Od: {B.full.nom} <{B.email}>",
                    "Dobrý den, {A.titled.voc},",
                    "už podruhé tento týden jsem ráno nemohl{B?|a} vyjet z garáže, protože průjezd"
                    " blokuje auto pana {M.full.gen}. Prosím o nápravu, jinak budu nucen{B?|a}"
                    " volat městskou policii.",
                    "{B.first.nom}",
                ),
            ),
            Template(
                "cs-email-birthday",
                "email",
                (
                    "Od: {A.full.nom} <{A.email}>",
                    "Komu: {B.email}",
                    "Předmět: Sobota u babičky",
                    "Ahoj {B.nick.voc},",
                    "babička v sobotu slaví osmdesátiny, tak jsem na půl dvanáctou zamluvil{A?|a}"
                    " stůl v restauraci U Lípy. {C.nick.nom} přiveze dort a {D.fposs.m} bratr"
                    " zařídí květiny.",
                    "Mohl{B?|a} bys cestou vyzvednout na nádraží {E.first.acc}? Vlak {E?mu|jí}"
                    " přijíždí v 10.40. Kdyby něco, volej mi na {A.phone}.",
                    "Pa,",
                    "{A.nick.nom}",
                ),
            ),
            Template(
                "cs-email-application",
                "email",
                (
                    "Od: {A.email}",
                    "Komu: kariera@example.com",
                    "Předmět: Odpověď na inzerát – mzdová účetní",
                    "Dobrý den,",
                    "reaguji na Váš inzerát na pozici mzdové účetní a v příloze posílám životopis."
                    " Na volné místo mě upozornil{B?|a} {B?Váš zaměstnanec|Vaše zaměstnankyně}"
                    " {B.full.nom}, se {B?kterým|kterou} jsem tři roky pracoval{A?|a} v předchozí"
                    " firmě. {B.surname.nom} Vám může mé pracovní zkušenosti potvrdit.",
                    "Jako referenci uvádím také {C?svého bývalého nadřízeného|svou bývalou"
                    " nadřízenou} Ing. {C.full.acc}, tel. {C.phone}.",
                    "Nastoupit mohu od 1. prosince.",
                    "S pozdravem",
                    "{A.full.nom}",
                    "{A.addr}",
                    "tel. {A.phone}",
                ),
            ),
            # minutes
            Template(
                "cs-minutes-firefighters",
                "minutes",
                (
                    "Zápis z výborové schůze Sboru dobrovolných hasičů Lipnice",
                    "Datum: 8. října 2026, hasičská zbrojnice",
                    "Přítomni: {A.full.nom}, {B.full.nom}, {C.full.nom}, {D.full.nom}",
                    "{E?Omluven|Omluvena}: {E.full.nom}",
                    "1. Starost{A?a|ka} {A.surname.nom} zahájil{A?|a} schůzi a konstatoval{A?|a},"
                    " že výbor je usnášeníschopný.",
                    "2. {C.surname.nom} informoval{C?|a} o stavu cisterny. Oprava čerpadla bude"
                    " stát přibližně 42 000 Kč; výbor opravu schválil všemi hlasy.",
                    "3. Na návrh {D.titled.gen} se jarní soutěž mladých hasičů uskuteční 9. května."
                    " Přihlášky družstev bude přijímat {D.surname.nom}.",
                    "4. Vedení kroužku mladých hasičů převezme po {E.fposs.m_loc} odchodu"
                    " {B.surname.nom}.",
                    "Zapsal{B?|a}: {B.full.nom}",
                    "Ověřil{A?|a}: {A.full.nom}",
                ),
            ),
            Template(
                "cs-minutes-parents",
                "minutes",
                (
                    "Zápis z třídních schůzek – 3. A",
                    "Konáno: 5. 11. 2026 v 17.00, učebna 204",
                    "{A?Třídní učitel|Třídní učitelka}: Mgr. {A.full.nom}",
                    "Přítomno: 18 rodičů (prezenční listina je přílohou zápisu)",
                    "1. {A?Pan učitel|Paní učitelka} {A.surname.nom} seznámil{A?|a} rodiče"
                    " s prospěchem třídy a s plánem lyžařského kurzu v únoru.",
                    "2. Za rodiče vystoupil{B?|a} {B.full.nom}, {B?předseda|předsedkyně} spolku"
                    " rodičů, a poděkoval{B?|a} za uspořádání podzimního výletu.",
                    "3. Nákup vánočních dárků pro třídu zajistí {C?pan|paní} {C.full.nom}."
                    " Příspěvek 200 Kč na žáka se vybírá do konce listopadu u {C?něj|ní}.",
                    "4. {E?Otec|Matka} {D?žáka|žákyně} {D.full.gen} požádal{E?|a} o přesunutí"
                    " konzultačních hodin na pozdější odpoledne. {A.surname.nom} vyhoví od"
                    " prosince.",
                    "Zapsal{B?|a}: {B.initial.nom}",
                ),
                children="D",
            ),
            Template(
                "cs-minutes-council",
                "minutes",
                (
                    "Zápis z 12. zasedání zastupitelstva obce Hrušovany",
                    "Zasedání zahájil{A?|a} v 18.00 starost{A?a|ka} obce {A.full.nom}. Přítomno"
                    " bylo 7 z 9 členů zastupitelstva, zasedání bylo usnášeníschopné.",
                    "Ověřovateli zápisu byli určeni {B.full.nom} a {C.full.nom},"
                    " zapisovatel{D?em|kou} {D.full.ins}.",
                    "Bod 1 – Prodej části pozemku",
                    "{E?Pan|Paní} {E.full.nom}, bytem {E.addr}, požádal{E?|a} o koupi části"
                    " obecního pozemku parc. č. 512/4 o výměře 38 m². {E.surname.nom} pozemek"
                    " dlouhodobě užívá jako příjezd ke své garáži. Zastupitelstvo prodej schválilo"
                    " (7 pro, 0 proti, 0 se zdrželo).",
                    "Bod 2 – Oprava chodníku",
                    "{B.surname.nom} se zeptal{B?|a} na celkové náklady opravy chodníku v horní"
                    " části obce. Starost{A?a|ka} odpověděl{A?|a}, že podle rozpočtu projektanta"
                    " dosáhnou 640 000 Kč.",
                    "Zasedání bylo ukončeno ve 20.15.",
                    "Zapsal{D?|a}: {D.full.nom}",
                    "Starost{A?a|ka}: {A.full.nom}",
                ),
            ),
            Template(
                "cs-minutes-handover",
                "minutes",
                (
                    "Protokol o předání a převzetí bytu",
                    "Předávající: {A.full.nom}, tel. {A.phone}",
                    "Přebírající: {B.full.nom}, tel. {B.phone}",
                    "Adresa bytu: {B.addr}",
                    "Stav vodoměrů: studená voda 112,4 m³, teplá voda 61,8 m³",
                    "Předáno: tři klíče od bytu, jeden klíč od poštovní schránky, čip ke vchodovým"
                    " dveřím",
                    "Zjištěné závady: prasklá dlaždice v koupelně. {A.surname.nom} se zavazuje"
                    " zajistit její výměnu do konce měsíce.",
                    "Předání proběhlo za přítomnosti {C?makléře|makléřky} {C.full.gen} z realitní"
                    " kanceláře. {B.surname.nom} převzal{B?|a} byt bez dalších výhrad.",
                    "V Třebíči dne 30. září 2026",
                    "předávající: {A.initial.nom}",
                    "přebírající: {B.initial.nom}",
                ),
            ),
        ),
    },
    "sk": {
        "dev": (
            Template(
                "sk-dev-newspaper",
                "letter",
                (
                    "{A.full.nom}",
                    "{A.addr}",
                    "Vec: Odhlásenie z odberu novín",
                    "Dobrý deň,",
                    "od 1. novembra odhlasujem odber denníka. Predplatné doteraz platil{B?|a}"
                    " {B?môj otec|moja mama} {B.full.nom}, ktor{B?ý|á} sa odsťahoval{B?|a}."
                    " {B.surname.nom} so zrušením súhlasí. Preplatok mi prosím vráťte na účet"
                    " {A.iban}.",
                    "S pozdravom",
                    "{A.full.nom}",
                ),
                families=("AB",),
            ),
            Template(
                "sk-dev-parking",
                "form",
                (
                    "Žiadosť o parkovaciu kartu",
                    "Meno a priezvisko: {A.full.nom}",
                    "Dátum narodenia: {A.born}",
                    "Adresa: {A.addr}",
                    "Telefón: {A.phone}",
                    "Vozidlo používa aj {B?môj brat|moja sestra} {B.full.nom}.",
                    "Prevzal{C?|a}: {C.initial.nom}",
                ),
                families=("AB",),
            ),
            Template(
                "sk-dev-meeting",
                "email",
                (
                    "Od: {A.email}",
                    "Komu: {B.email}",
                    "Predmet: Stretnutie",
                    "Ahoj {B.nick.nom},",
                    "uvidíme sa zajtra o šiestej. {C.surname.nom} príde neskôr, lebo {D.fposs.n}"
                    " auto je v servise.",
                    "{A.first.nom}",
                ),
            ),
        ),
        "test": (
            # letters
            Template(
                "sk-letter-tree",
                "letter",
                (
                    "{A.full.nom}",
                    "{A.addr}",
                    "Obecný úrad Brezová",
                    "Vec: Žiadosť o povolenie výrubu stromu",
                    "Dobrý deň,",
                    "žiadam o povolenie výrubu suchého orecha, ktorý rastie na hranici môjho"
                    " pozemku a pozemku {B?suseda|susedky} {B.full.gen}. Strom ohrozuje strechu"
                    " {B?jeho|jej} garáže a {B.surname.nom} s výrubom súhlasí; {B?jeho|jej}"
                    " písomný súhlas prikladám.",
                    "Výrub vykoná na vlastné náklady {C?môj syn|moja dcéra} {C.full.nom},"
                    " ktor{C?ý|á} má osvedčenie na prácu s motorovou pílou.",
                    "S pozdravom",
                    "{A.full.nom}",
                    "tel. {A.phone}",
                ),
                families=("AC",),
            ),
            Template(
                "sk-letter-recommendation",
                "letter",
                (
                    "Odporúčanie",
                    "Týmto odporúčam {A?študenta|študentku} {A.full.acc}, ktor{A?ý|á} v rokoch 2023"
                    " až 2026 študoval{A?|a} na našej škole odbor informačné technológie.",
                    "{A.surname.nom} patril{A?|a} medzi najlepších v ročníku. Pod vedením Ing."
                    " {B.full.gen} vypracoval{A?|a} ročníkový projekt o meraní kvality ovzdušia,"
                    " ktorý ocenila aj krajská komisia.",
                    "Na {A.surname.loc} si cením najmä samostatnosť, spoľahlivosť a ochotu pomôcť"
                    " spolužiakom.",
                    "S otázkami sa na mňa môžete obrátiť telefonicky na {C.phone} alebo e-mailom"
                    " {C.email}.",
                    "V Trnave 12. októbra 2026",
                    "Mgr. {C.full.nom}",
                    "{C?triedny učiteľ|triedna učiteľka}",
                ),
            ),
            Template(
                "sk-letter-postcard",
                "letter",
                (
                    "{A.full.nom}",
                    "{A.addrblock}",
                    "Ahoj {A.nick.nom},",
                    "pozdravujeme z Tatier! Počasie nám zatiaľ praje, včera sme vyšli až na Rysy."
                    " {B.nick.nom} bol{B?|a} hore prv{B?ý|á}, ja som sa doplazil{C?|a}"
                    " posledn{C?ý|á}.",
                    "V sobotu sa k nám pridá aj {D.first.nom} s deťmi. {E.fposs.n} auto sme"
                    " nechali pred domom, tak ho prosím občas skontroluj. Kľúč od bytu je u pána"
                    " {M.full.gen} z prízemia.",
                    "Vrátime sa v nedeľu večer.",
                    "{C.first.nom}",
                ),
            ),
            # contracts
            Template(
                "sk-contract-loan",
                "contract",
                (
                    "Zmluva o pôžičke",
                    "{A?Veriteľ|Veriteľka}: {A.full.nom}, nar. {A.born}, bytom {A.addr}",
                    "{B?Dlžník|Dlžníčka}: {B.full.nom}, r. č. {B.rc}, bytom {B.addr}",
                    "1. Veriteľ požičiava dlžníkovi sumu 6 000 eur, ktorú mu poukáže na účet"
                    " {B.iban} do piatich dní od podpisu zmluvy.",
                    "2. {B.surname.nom} sa zaväzuje vrátiť pôžičku v dvanástich mesačných"
                    " splátkach po 500 eur na účet veriteľa {A.iban}.",
                    "3. Ak bude dlžník v omeškaní s viac ako dvoma splátkami, môže {A.surname.nom}"
                    " požadovať vrátenie celej zostávajúcej sumy naraz.",
                    "4. Za záväzky dlžníka ručí {C.full.nom}, bytom {C.addr}, čo potvrdzuje svojím"
                    " podpisom.",
                    "V Žiline 3. septembra 2026",
                    "{A?veriteľ|veriteľka}: {A.full.nom}",
                    "{B?dlžník|dlžníčka}: {B.full.nom}",
                    "{C?ručiteľ|ručiteľka}: {C.full.nom}",
                ),
            ),
            Template(
                "sk-contract-garage",
                "contract",
                (
                    "Zmluva o nájme garáže",
                    "{A?Prenajímateľ|Prenajímateľka}: {A.rev}, {A.addr}",
                    "{B?Nájomca|Nájomkyňa}: {B.rev}, {B.addr}, tel. {B.phone}",
                    "1. Predmetom nájmu je garáž č. 14 v garážovom dvore za bytovým domom, v ktorom"
                    " býva prenajímateľ.",
                    "2. Nájomné 45 eur mesačne sa platí do pätnásteho dňa každého mesiaca na účet"
                    " {A.iban}.",
                    "3. Garáž môže popri nájomcovi používať aj {C?syn|dcéra} nájomcu {C.full.nom}."
                    " Inej osobe ju {B.surname.nom} prenechať nesmie.",
                    "4. Opravu poškodenej brány zabezpečí {A.surname.nom} do konca októbra 2026.",
                    "V Trenčíne 28. septembra 2026",
                    "{A.full.nom}",
                    "{B.full.nom}",
                ),
                families=("BC",),
            ),
            Template(
                "sk-contract-painting",
                "contract",
                (
                    "Dohoda o vykonaní práce",
                    "Zamestnávateľ: Materská škola Slnečnica, v zastúpení"
                    " {A?riaditeľom|riaditeľkou} Mgr. {A.full.ins}",
                    "{B?Zamestnanec|Zamestnankyňa}: {B.full.nom}, nar. {B.born}, bytom {B.addr}",
                    "Pracovná úloha: vymaľovanie dvoch tried a chodby do 31. októbra 2026.",
                    "Odmena: 900 eur, splatná na účet {B.iban} po prevzatí práce.",
                    "Vykonanú prácu prevezme {C?zástupca|zástupkyňa} {A?riaditeľa|riaditeľky}"
                    " {C.full.nom}. {B.surname.nom} pracuje s vlastným náradím, farby dodá"
                    " zamestnávateľ.",
                    "V Nitre 5. októbra 2026",
                    "{A.full.nom}",
                    "{B.full.nom}",
                ),
            ),
            # forms
            Template(
                "sk-form-swimming",
                "form",
                (
                    "Prihláška na plavecký kurz",
                    "Meno a priezvisko dieťaťa: {A.full.nom}",
                    "Dátum narodenia: {A.born}",
                    "{B?Zákonný zástupca|Zákonná zástupkyňa}: {B.full.nom}",
                    "Adresa: {B.addr}",
                    "Telefón: {B.phone}",
                    "E-mail: {B.email}",
                    "Zdravotné obmedzenia: žiadne",
                    "Dieťa bude z kurzu vyzdvihovať aj {C?starý otec|stará mama} {C.full.nom}.",
                    "Prihlášku prevzal{D?|a}: {D.initial.nom}",
                ),
                families=("AB",),
                children="A",
            ),
            Template(
                "sk-form-insurance",
                "form",
                (
                    "Oznámenie poistnej udalosti – poistenie domácnosti",
                    "{A?Poistník|Poistníčka}: {A.rev}",
                    "Rodné číslo: {A.rc}",
                    "Adresa poisteného bytu: {A.addr}",
                    "Kontaktný telefón: {A.phone}",
                    "Popis udalosti: Dňa 14. septembra 2026 vytopil{B?|a} byt {B?sused|susedka}"
                    " z horného poschodia {B.full.nom}. {B.surname.nom} nechal{B?|a} počas"
                    " dovolenky zapnutú práčku s poškodenou hadicou.",
                    "Škodu zistil{C?|a} {C.full.nom}, ktor{C?ý|á} počas neprítomnosti poistníka"
                    " kontroluje byt.",
                    "{D?Svedok|Svedkyňa}: {D.full.nom}, tel. {D.phone}",
                    "Plnenie žiadam poukázať na účet {A.iban}.",
                ),
            ),
            Template(
                "sk-form-fishing",
                "form",
                (
                    "Žiadosť o vydanie rybárskeho lístka",
                    "Priezvisko: {A.surname.nom}",
                    "Meno: {A.first.nom}",
                    "Dátum narodenia: {A.born}",
                    "Trvalý pobyt: {A.addr}",
                    "Číslo členského preukazu: 4471/2019",
                    "{A?Žiadateľ|Žiadateľka} je {A?členom|členkou} miestnej organizácie rybárskeho"
                    " zväzu od roku 2019 a nemá žiadne disciplinárne opatrenie.",
                    "Vyjadrenie hospodára: odporúčam vydať, {B.initial.nom},"
                    " {B?hospodár|hospodárka} MO",
                    "Lístok prevzal{A?|a} osobne dňa 1. 10. 2026.",
                ),
            ),
            Template(
                "sk-form-authorization",
                "form",
                (
                    "Splnomocnenie",
                    "Ja, dolu podpísan{A?ý|á} {A.full.nom}, nar. {A.born}, bytom {A.addr},",
                    "splnomocňujem {B?pána|pani} {B.full.acc}, nar. {B.born}, bytom {B.addr},",
                    "aby v mojom mene prevzal{B?|a} na pošte doporučenú zásielku č. RR418725093SK.",
                    "{B.surname.nom} sa pri preberaní preukáže vlastným občianskym preukazom.",
                    "V Prešove 9. októbra 2026",
                    "podpis {A?splnomocniteľa|splnomocniteľky}: {A.full.nom}",
                ),
            ),
            # e-mails
            Template(
                "sk-email-inventory",
                "email",
                (
                    "Od: {A.full.nom} <{A.email}>",
                    "Komu: {B.email}; {C.email}",
                    "Predmet: Inventúra skladu",
                    "Ahoj {B.first.nom} a {C.first.nom},",
                    "inventúra bude v piatok od siedmej. {D.surname.nom} z účtovného oddelenia"
                    " príde okolo desiatej skontrolovať zoznamy, tak ich prosím majte pripravené.",
                    "{E.nick.nom} je na dovolenke, takže {E?jeho|jej} regály spočíta"
                    " {B.first.nom}.",
                    "Ďakujem,",
                    "{A.first.nom}",
                ),
            ),
            Template(
                "sk-email-lift",
                "email",
                (
                    "Od: {A.email}",
                    "Komu: spravca@example.org",
                    "Predmet: Porucha výťahu",
                    "Dobrý deň, {B.titled.nom},",
                    "výťah v našom vchode opäť nefunguje už od pondelka. Pre {C?pána|pani}"
                    " {C.full.acc} z ôsmeho poschodia, ktor{C?ý|á} chodí o barlách, je to veľký"
                    " problém. {C.surname.nom} ma poprosil{C?|a}, aby som Vám napísal{A?|a} aj"
                    " v {C?jeho|jej} mene.",
                    "Opravára môžete poslať kedykoľvek, kľúč od strojovne má {D?domový"
                    " dôverník|domová dôverníčka} {D.full.nom}.",
                    "S pozdravom",
                    "{A.full.nom}, byt č. 23",
                ),
            ),
            Template(
                "sk-email-moving",
                "email",
                (
                    "Od: {A.full.nom} <{A.email}>",
                    "Komu: {B.email}",
                    "Predmet: Sťahovanie v sobotu",
                    "Ahoj {B.nick.nom},",
                    "v sobotu sa konečne sťahujeme do nového bytu. {C.nick.nom} požičia dodávku"
                    " a {D.fposs.m} brat pomôže so skriňou.",
                    "{B?Mohol|Mohla} by si ráno vyzdvihnúť {E.first.acc} na stanici?"
                    " Vlak {E?mu|jej} príde o 8.15.",
                    "Nová adresa: {A.addr}",
                    "Volaj, keby niečo: {A.phone}",
                    "{A.nick.nom}",
                ),
            ),
            # minutes
            Template(
                "sk-minutes-council",
                "minutes",
                (
                    "Zápisnica zo zasadnutia obecného zastupiteľstva v Brezovej",
                    "Zasadnutie otvoril{A?|a} starost{A?a|ka} obce {A.full.nom}. Za overovateľov"
                    " zápisnice boli určení {B.full.nom} a {C.full.nom}.",
                    "K bodu 2: {D?Pán|Pani} {D.full.nom}, bytom {D.addr}, požiadal{D?|a}"
                    " o odkúpenie obecného pozemku pod svojou garážou. {D.surname.nom} ponúka"
                    " 15 eur za meter štvorcový. Zastupiteľstvo predaj schválilo.",
                    "K bodu 3: {B?Poslanec|Poslankyňa} {B.surname.nom} upozornil{B?|a} na rozbitú"
                    " lavičku pri detskom ihrisku. Starost{A?a|ka} sľúbil{A?|a} opravu do konca"
                    " mesiaca.",
                    "Zapísal{E?|a}: {E.full.nom}",
                ),
            ),
            Template(
                "sk-minutes-owners",
                "minutes",
                (
                    "Zápisnica zo schôdze vlastníkov bytov a nebytových priestorov",
                    "Dátum: 2. októbra 2026, spoločenská miestnosť",
                    "{A?Predsedajúci|Predsedajúca}: {A.full.nom}",
                    "{B?Zapisovateľ|Zapisovateľka}: {B.full.nom}",
                    "1. {C?Správca|Správkyňa} {C.full.nom} {C?predniesol|predniesla} správu"
                    " o hospodárení za rok 2025. Na otázky vlastníkov odpovedal{C?|a}"
                    " {C.surname.nom} podrobne.",
                    "2. {D?Vlastník|Vlastníčka} bytu č. 9 {D.full.nom} {D?navrhol|navrhla} výmenu"
                    " zvončekového tabla a {D.surname.nom} predložil{D?|a} dve cenové ponuky."
                    " Návrh bol schválený.",
                    "3. {M.sposs.f} pripomienka k vyúčtovaniu tepla bude zapracovaná do budúceho"
                    " vyúčtovania.",
                    "Zapísal{B?|a}: {B.initial.nom}",
                ),
            ),
            Template(
                "sk-minutes-sales",
                "minutes",
                (
                    "Zápisnica z porady oddelenia predaja",
                    "Prítomní: {A.full.nom}, {B.full.nom}, {C.full.nom}, {D.full.nom}",
                    "Ospravedlnen{E?ý|á}: {E.full.nom}",
                    "1. {A.surname.nom} zhrnul{A?|a} výsledky za tretí štvrťrok: tržby vzrástli"
                    " o 6 %.",
                    "2. Počas dovolenky {E.surname.gen} prevezme {E?jeho|jej} klientov"
                    " {B?kolega|kolegyňa} {B.surname.nom}.",
                    "3. {D.initial.nom} pripraví nový cenník do 20. októbra.",
                    "Zapísal{C?|a}: {C.full.nom}",
                ),
            ),
        ),
    },
}
"""Templates per language and split; evaluation only (see the module docstring)."""

CONTROLS: dict[str, dict[str, tuple[Template, ...]]] = {
    "cs": {
        "dev": (
            Template(
                "cs-dev-control-site",
                "contract",
                (
                    "Zhotovitel nese odpovědnost za škody vzniklé při stavbě. Objednatel zajistí"
                    " Zhotoviteli přívod elektřiny a vody na staveniště.",
                ),
            ),
        ),
        "test": (
            Template(
                "cs-control-tools",
                "contract",
                (
                    "Obchodní podmínky půjčovny nářadí",
                    "1. Nájemce přebírá nářadí ve stavu způsobilém k užívání a vrací je očištěné.",
                    "2. Půjčovné se platí předem; při prodlení s vrácením účtuje Pronajímatel"
                    " dvojnásobnou sazbu za každý započatý den.",
                    "3. Ztrátu nebo poškození nářadí hlásí Nájemce bez zbytečného odkladu. Kauci"
                    " vrátí Pronajímatel po kontrole vráceného nářadí.",
                    "4. Spotřebitel může od smlouvy odstoupit, pokud nářadí dosud nepoužil.",
                ),
            ),
            Template(
                "cs-control-parking",
                "form",
                (
                    "Pokyny k vyplnění žádosti o parkovací kartu",
                    "Žadatel vyplní všechny kolonky hůlkovým písmem. Za nezletilého žadatele"
                    " podepisuje žádost Zákonný zástupce.",
                    "Přílohou je kopie velkého technického průkazu. Je-li Provozovatel vozidla"
                    " odlišný od žadatele, doloží Žadatel jeho písemný souhlas.",
                    "Kartu vydá Správce parkoviště do pěti pracovních dnů.",
                ),
            ),
            Template(
                "cs-control-school",
                "letter",
                (
                    "Výňatek ze školního řádu",
                    "Žák přichází do školy nejpozději deset minut před začátkem vyučování."
                    " Nepřítomnost omlouvá Zákonný zástupce do tří dnů.",
                    "Třídní učitel eviduje zameškané hodiny a při podezření na záškoláctví"
                    " informuje Ředitele školy.",
                    "Za ztrátu učebnice odpovídá Žák a škodu uhradí podle ceníku v příloze.",
                ),
            ),
            Template(
                "cs-control-committee",
                "minutes",
                (
                    "Zápis z jednání komise pro životní prostředí",
                    "Předsedající zahájil jednání v 16.00 a přivítal přítomné členy. Zapisovatel"
                    " konstatoval, že komise je usnášeníschopná.",
                    "Komise doporučuje Radě města schválit výsadbu dvaceti lip v parku"
                    " u nádraží. Stromy vysadí Zhotovitel vybraný v soutěži.",
                    "Ověřovatel zápisu neměl připomínky. Příští jednání svolá Předsedající"
                    " na leden.",
                ),
            ),
        ),
    },
    "sk": {
        "dev": (
            Template(
                "sk-dev-control-delivery",
                "contract",
                (
                    "Dodávateľ doručí tovar do piatich pracovných dní. Zásielku pri prevzatí"
                    " skontroluje Odberateľ.",
                ),
            ),
        ),
        "test": (
            Template(
                "sk-control-bicycles",
                "contract",
                (
                    "Všeobecné podmienky požičovne bicyklov",
                    "Nájomca preberá bicykel v technicky spôsobilom stave a vráti ho čistý.",
                    "Prenajímateľ môže požadovať zálohu 100 eur. Pri strate bicykla uhradí Nájomca"
                    " jeho zostatkovú cenu.",
                    "Spotrebiteľ má právo podať reklamáciu do 30 dní.",
                ),
            ),
            Template(
                "sk-control-application",
                "form",
                (
                    "Pokyny na vyplnenie prihlášky",
                    "Žiadateľ vyplní všetky údaje paličkovým písmom. Za maloletého žiadateľa"
                    " podpisuje prihlášku Zákonný zástupca.",
                    "Ak je Platiteľ poplatku iná osoba ako Žiadateľ, uvedie sa aj jeho kontaktný"
                    " údaj.",
                ),
            ),
            Template(
                "sk-control-sport",
                "minutes",
                (
                    "Zápisnica zo zasadnutia komisie pre šport",
                    "Predsedajúci otvoril zasadnutie a privítal prítomných členov. Zapisovateľ"
                    " skonštatoval, že komisia je uznášaniaschopná.",
                    "Komisia odporúča Mestskej rade schváliť príspevok na opravu tenisových"
                    " kurtov. Vyúčtovanie predloží Žiadateľ do konca roka.",
                ),
            ),
        ),
    },
}
"""Documents naming nobody, with capitalised role nouns; each is used once."""

_PLACEHOLDER = re.compile(
    r"\{(?:(?P<preposition>[sSkKvV])~)?(?P<person>[A-EMNVW])"
    r"(?:\.(?P<slot>[a-z]+)(?:\.(?P<form>[a-z_]+))?"
    r"|\?(?P<male>[^|}]*)\|(?P<female>[^}]*))\}"
)

_NAME_SLOTS = frozenset(
    {"full", "titled", "surname", "first", "nick", "sposs", "fposs", "initial", "rev"}
)
# Slots that write the surname, so a surname alone after them is a later mention.
_SURNAME_SLOTS = frozenset({"full", "titled", "surname", "sposs", "initial", "rev"})
_VALUE_SLOTS = {
    "addr": EntityType.ADDRESS,
    "addrblock": EntityType.ADDRESS,
    "rc": EntityType.BIRTH_NUMBER,
    "born": EntityType.DATE,
    "phone": EntityType.PHONE,
    "email": EntityType.EMAIL,
    "account": EntityType.BANK_ACCOUNT,
    "iban": EntityType.IBAN,
}

# Birth numbers before 1954 have nine digits and no check digit; none is generated.
_BIRTH_YEARS = {"child": (2010, 2019), "adult": (1963, 2002), "elder": (1954, 1962)}

# Weights of the Czech and Slovak account number check (ČNB decree 169/2011),
# right-aligned: the last digit always has weight 1.
_ACCOUNT_WEIGHTS = (6, 3, 7, 9, 10, 5, 8, 4, 2, 1)


def generate(language: str, split: str) -> list[HeldoutDocument]:
    """Return every document of one language and split, the same on every call.

    Args:
        language: `cs` or `sk`.
        split: `dev` or `test`.

    Returns:
        `INSTANCES[split]` documents per template, in template order, then the
        documents naming nobody.

    Raises:
        ValueError: For an unknown language or split.
    """
    if language not in TEMPLATES or split not in SPLITS:
        msg = f"no held-out documents for {language}/{split}"
        raise ValueError(msg)
    lists = NAMES[language][split]
    documents: list[HeldoutDocument] = []
    for template in TEMPLATES[language][split]:
        # Seeded by the template's name, so editing one template leaves the
        # people of every other one unchanged.
        draw = random.Random(f"heldout/{language}/{split}/{template.name}")
        for instance in range(INSTANCES[split]):
            people = _cast(template, lists, draw, instance, language)
            documents.append(render(template, people, language))
    documents += [render(control, {}, language) for control in CONTROLS[language][split]]
    return documents


def _cast(
    template: Template, lists: NameLists, draw: random.Random, instance: int, language: str
) -> dict[str, Person]:
    """Choose the people of one document: different first names, surnames shared by families."""
    needs: dict[str, set[str]] = {}
    for found in _PLACEHOLDER.finditer("\n".join(template.lines)):
        needs.setdefault(found["person"], set()).add(found["slot"] or "")
    family_of = {letter: group for group in template.families for letter in group}
    family_surnames: dict[str, Name] = {}
    people: dict[str, Person] = {}
    # People needing a nickname or a possessive choose first: fewer first names qualify.
    for letter in sorted(needs, key=lambda letter: (not needs[letter] & {"nick", "fposs"}, letter)):
        female = _female(letter, instance)
        if female and "sposs" in needs[letter]:
            msg = f"{template.name}: a woman's surname has no possessive ({letter})"
            raise ValueError(msg)
        group = family_of.get(letter, letter)
        if group not in family_surnames:
            wants_possessive = any("sposs" in needs.get(member, ()) for member in group)
            family_surnames[group] = draw.choice(
                [
                    name
                    for name in lists.surnames
                    if name not in family_surnames.values()
                    and (not wants_possessive or has_possessive(name, language))
                ]
            )
        taken = {person.first for person in people.values()}
        first = draw.choice(
            [
                name
                for name in (lists.female_first if female else lists.male_first)
                if name not in taken
                and ("nick" not in needs[letter] or name.word in lists.nicknames)
                and ("fposs" not in needs[letter] or has_possessive(name, language))
            ]
        )
        people[letter] = _person(
            female,
            first,
            family_surnames[group],
            lists.nicknames.get(first.word),
            years=_birth_years(template, letter),
            draw=draw,
            language=language,
        )
    return people


def _birth_years(template: Template, letter: str) -> tuple[int, int]:
    if letter in template.children:
        return _BIRTH_YEARS["child"]
    if letter in template.elders:
        return _BIRTH_YEARS["elder"]
    return _BIRTH_YEARS["adult"]


def _female(letter: str, instance: int) -> bool:
    """Gender by letter: M, N men; V, W women; A to E alternate in different patterns."""
    if letter in "MN":
        return False
    if letter in "VW":
        return True
    first, second, third = instance % 2, (instance // 2) % 2, (instance // 4) % 2
    pattern = {
        "A": first,
        "B": second,
        "C": first ^ second ^ 1,
        "D": second ^ third,
        "E": first ^ third,
    }
    return pattern[letter] == 1


def _person(
    female: bool,
    first: Name,
    family_surname: Name,
    nickname: Name | None,
    *,
    years: tuple[int, int],
    draw: random.Random,
    language: str,
) -> Person:
    """Draw every value of a person, always in the same order."""
    surname = feminine_surname(family_surname) if female else family_surname
    number = str(draw.randint(1, 2400))
    if draw.random() < 0.35:
        number += f"/{draw.randint(1, 60)}"
    postcode, town = draw.choice(TOWNS[language])
    born = date(draw.randint(*years), draw.randint(1, 12), draw.randint(1, 28))
    prefix = _account_part(draw, draw.choice((2, 6))) if draw.random() < 0.3 else ""
    base = _account_part(draw, draw.choice((8, 10)))
    return Person(
        female=female,
        first=first,
        surname=surname,
        family_surname=family_surname,
        nickname=nickname,
        street=f"{draw.choice(STREETS[language])} {number}",
        town=f"{postcode} {town}",
        born=born,
        birth_number=birth_number(born, female=female, draw=draw),
        phone=_phone(draw, language),
        email=_email(first, surname, draw),
        account=f"{prefix + '-' if prefix else ''}{base}/{draw.choice(BANK_CODES['cs'])}",
        iban=iban(_COUNTRY[language], draw.choice(BANK_CODES[language]), prefix, base),
    )


def birth_number(born: date, *, female: bool, draw: random.Random) -> str:
    """Return a birth number (rodné číslo) for a date of birth, with its check digit.

    The ten digits YYMMDDSSSC, month plus 50 for a woman, are divisible by 11:
    the check digit C is the first nine digits modulo 11. A serial whose
    remainder is 10 is drawn again rather than written with a 0.
    """
    month = born.month + (50 if female else 0)
    while True:
        first_nine = f"{born.year % 100:02d}{month:02d}{born.day:02d}{draw.randrange(1000):03d}"
        check = int(first_nine) % 11
        if check < 10:
            return f"{first_nine[:6]}/{first_nine[6:]}{check}"


def _account_part(draw: random.Random, length: int) -> str:
    """Return a prefix or base of an account number whose weighted sum is divisible by 11."""
    weights = _ACCOUNT_WEIGHTS[-length:]
    while True:
        digits = [draw.randint(1, 9), *(draw.randrange(10) for _ in range(length - 2))]
        last = -sum(digit * weight for digit, weight in zip(digits, weights, strict=False)) % 11
        if last < 10:
            return "".join(map(str, digits)) + str(last)


def iban(country: str, bank_code: str, prefix: str, base: str) -> str:
    """Return the IBAN of a Czech or Slovak account, in groups of four.

    The check digits make the number, with the country and check moved to the
    end and letters read as 10 to 35, leave 1 modulo 97 (ISO 13616).
    """
    bban = bank_code + prefix.zfill(6) + base.zfill(10)
    letters = "".join(str(ord(letter) - ord("A") + 10) for letter in country)
    check = 98 - int(bban + letters + "00") % 97
    compact = f"{country}{check:02d}{bban}"
    return " ".join(compact[start : start + 4] for start in range(0, len(compact), 4))


def _phone(draw: random.Random, language: str) -> str:
    """Return a mobile number: Czech 6xx/7xx, Slovak 9xx, with or without the country code."""
    lead = draw.choice("67") if language == "cs" else "9"
    digits = lead + "".join(str(draw.randrange(10)) for _ in range(8))
    groups = f"{digits[:3]} {digits[3:6]} {digits[6:]}"
    if draw.random() < 0.5:
        return f"+{420 if language == 'cs' else 421} {groups}"
    return groups if language == "cs" else f"0{groups}"


def _email(first: Name, surname: Name, draw: random.Random) -> str:
    """Return an e-mail address made of the name, at one of the reserved example domains."""
    given, family = _ascii(first.word), _ascii(surname.word)
    local = draw.choice(
        (f"{given}.{family}", f"{given[0]}.{family}", f"{family}.{given}", f"{given}{family}")
    )
    return f"{local}@{draw.choice(_DOMAINS)}"


def _ascii(word: str) -> str:
    decomposed = unicodedata.normalize("NFKD", word)
    return "".join(char for char in decomposed if char.isascii()).lower()


def render(template: Template, people: dict[str, Person], language: str) -> HeldoutDocument:
    """Fill a template with people; return the text and its gold spans.

    Args:
        template: A template (syntax in the module docstring).
        people: The person of each letter the template uses.
        language: `cs` or `sk`.

    Returns:
        The NFC text with one gold span per value slot.

    Raises:
        ValueError: For an unknown slot, a form the slot does not take, or
            text not in NFC.
    """
    source = "\n".join(template.lines)
    parts: list[str] = []
    spans: list[GoldSpan] = []
    surname_written: set[str] = set()
    position = 0
    length = 0
    for found in _PLACEHOLDER.finditer(source):
        literal = source[position : found.start()]
        parts.append(literal)
        length += len(literal)
        position = found.end()
        letter = found["person"]
        person = people[letter]
        if found["slot"] is None:
            chosen = found["female"] if person.female else found["male"]
            parts.append(chosen)
            length += len(chosen)
            continue
        slot = found["slot"]
        later = letter in surname_written
        lead, value, kind, tags = _slot(person, slot, found["form"], language, later=later)
        if slot in _SURNAME_SLOTS:
            surname_written.add(letter)
        if found["preposition"]:
            lead = preposition(found["preposition"], lead + value, language) + " " + lead
        start = length + len(lead)
        spans.append(GoldSpan(kind, start, start + len(value), tags))
        parts += [lead, value]
        length += len(lead) + len(value)
    parts.append(source[position:])
    text = "".join(parts)
    if unicodedata.normalize("NFC", text) != text:
        msg = f"{template.name}: a template, name or value is not in NFC"
        raise ValueError(msg)
    spans = [
        GoldSpan(
            span.type,
            span.start,
            span.end,
            (
                *span.tags,
                *(("context", context) for context in contexts(text, span, language)),
                ("kind", template.kind),
            ),
        )
        if span.type is EntityType.PERSON
        else span
        for span in spans
    ]
    return HeldoutDocument(template.name, text, tuple(spans))


def _slot(
    person: Person, slot: str, form: str | None, language: str, *, later: bool
) -> tuple[str, str, EntityType, tuple[Tag, ...]]:
    """Return the text before the value, the value, its type and its tags."""
    if slot in _VALUE_SLOTS:
        if form is not None:
            msg = f"{slot} takes no form"
            raise ValueError(msg)
        return "", _value(person, slot), _VALUE_SLOTS[slot], ()
    if slot not in _NAME_SLOTS:
        msg = f"unknown slot {slot!r}"
        raise ValueError(msg)
    gender = "f" if person.female else "m"
    if slot == "rev":
        if form is not None:
            msg = "rev takes no form"
            raise ValueError(msg)
        value = f"{person.surname.word} {person.first.word}"
        return (
            "",
            value,
            EntityType.PERSON,
            _tags("surname-first", Case.NOM, person.surname, gender),
        )
    if form is None:
        msg = f"{slot} needs a form"
        raise ValueError(msg)
    if slot in {"sposs", "fposs"}:
        source = person.family_surname if slot == "sposs" else person.first
        kind = "surname-possessive" if slot == "sposs" else "first-name-possessive"
        value = possessive(source, Agreement(form), language)
        return "", value, EntityType.PERSON, _tags(kind, None, source, gender)
    case = Case(form)
    surname = decline(person.surname, case, language)
    if slot == "full":
        first = decline(person.first, case, language, before_surname=True)
        return (
            "",
            f"{first} {surname}",
            EntityType.PERSON,
            _tags("full", case, person.surname, gender),
        )
    if slot == "titled":
        lead = title(person.female, case, language) + " "
        return (
            lead,
            surname,
            EntityType.PERSON,
            _tags("title-surname", case, person.surname, gender),
        )
    if slot == "surname":
        kind = "later-surname" if later else "lone-surname"
        return "", surname, EntityType.PERSON, _tags(kind, case, person.surname, gender)
    if slot == "initial":
        value = f"{person.first.word[0]}. {surname}"
        return "", value, EntityType.PERSON, _tags("initial", case, person.surname, gender)
    if slot == "nick":
        if person.nickname is None:
            msg = f"{person.first.word} has no nickname"
            raise ValueError(msg)
        value = decline(person.nickname, case, language)
        return "", value, EntityType.PERSON, _tags("nickname", case, person.nickname, gender)
    value = decline(person.first, case, language)
    return "", value, EntityType.PERSON, _tags("first-name", case, person.first, gender)


def _value(person: Person, slot: str) -> str:
    born = person.born
    values = {
        "addr": f"{person.street}, {person.town}",
        "addrblock": f"{person.street}\n{person.town}",
        "rc": person.birth_number,
        "born": f"{born.day}. {born.month}. {born.year}",
        "phone": person.phone,
        "email": person.email,
        "account": person.account,
        "iban": person.iban,
    }
    return values[slot]


def _tags(form: str, case: Case | None, carrier: Name, gender: str) -> tuple[Tag, ...]:
    tags: list[Tag] = [("form", form)]
    if case is not None:
        tags += [("case", str(case)), ("form-case", f"{form}/{case}")]
    else:
        tags.append(("form-case", form))
    tags += [("class", str(carrier.paradigm)), ("gender", gender)]
    return tuple(tags)


_FOLLOWING_WORD = re.compile(r"(?:,| \()\s*([^\W\d_]+)")


def contexts(text: str, span: GoldSpan, language: str) -> tuple[str, ...]:
    """Return what stands next to a person span (`CONTEXTS`; see the module docstring).

    Args:
        text: The document text.
        span: A person span in it.
        language: `cs` or `sk`, choosing `ROLE_NOUNS`.

    Returns:
        role-noun, degree and label as they apply, or plain.
    """
    line_start = text.rfind("\n", 0, span.start) + 1
    prefix = text[line_start : span.start]
    words = prefix.split()
    previous = words[-1] if words else ""
    following = _FOLLOWING_WORD.match(text, span.end)
    roles = ROLE_NOUNS[language]
    found: list[str] = []
    if previous.strip(":,(").lower() in roles or (following and following[1].lower() in roles):
        found.append("role-noun")
    if previous in DEGREES:
        found.append("degree")
    if prefix.endswith(": ") and ":" not in prefix[:-2]:
        found.append("label")
    return tuple(found) or ("plain",)
