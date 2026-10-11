"""Czech and Slovak name-forms challenge set: short texts naming people in controlled forms.

Czech inflects names in seven cases, so one person appears as "Jan Novák",
"pana Nováka", "Novákovi", "pane Nováku" or "Novákova žena". The benchmark
found names of two or more words 80 of 81 times but names written as one word
5 of 16 (`docs/findings.md`). This set measures, per kind of form, how often a
system misses a name: every gold span carries tags (`Tag`) saying what form
it is in, and `experiments.phenomena` reports recall per tag.

Each text is one template filled with invented people: very common first
names and surnames combined arbitrarily, as in the benchmark, never a real
person. Names are declined by the hand-written rules of `declension.py`; each
gold span covers the name only (not "pan", not a preposition), as CNEC and the
benchmark mark them. A handful of texts per split name nobody and use
capitalised role nouns ("Kupující", "Žadatel"), so false alarms show.

Tags of a gold span (facet → value):

    form       full, title-surname (after pan/paní/pane), later-surname (a
               surname alone after a full mention), first-name, nickname,
               surname-possessive (Novákův), first-name-possessive (Janin),
               foreign-full, foreign-first (English names in Czech text)
    case       nom, gen, dat, acc, voc, loc, ins (none for possessives)
    form-case  the two together, e.g. full/gen
    class      the declension pattern of the word that carries the name
               (`declension.Paradigm`): the surname for full names and
               surnames, else the first name or nickname
    gender     m, f

Splits: `dev` and `test` share no name and no template, so the test half
stays meaningful after tuning on dev. Slovak has no vocative (`declension`),
fewer templates, and no foreign names.

These templates are for evaluation only. A generator of training data must
not reuse them, or a model trained on its output would be scored on texts
it was trained on (CLAUDE.md: synthetic training data must not reuse the
templates of a held-out synthetic test set).

Size: every template is filled `INSTANCES` times. Czech dev holds 64
templates (two per form and case) and Slovak dev 24, so a form and case has
24 gold names in Czech and 12 in Slovak: enough to tell a form found almost
always from one found half the time or never, in a run of minutes on the CPU.
Instances of one template share their wording, so the bootstrap intervals,
which resample texts, are narrower than a resample of templates would give.
"""

from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass

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

NAME_FORMS_VERSION = "1"
"""Bumped whenever the generated texts change; recorded in results as the dataset version."""

INSTANCES = 12
"""Texts generated from each template, each with other people."""

SPLITS = ("dev", "test")

FORMS = (
    "full",
    "title-surname",
    "later-surname",
    "first-name",
    "nickname",
    "surname-possessive",
    "first-name-possessive",
    "foreign-full",
    "foreign-first",
)
"""Forms in table order."""

Tag = tuple[str, str]
"""A facet and its value, e.g. `("case", "gen")`."""


@dataclass(frozen=True, slots=True)
class GoldName:
    """A gold person span in a generated text."""

    start: int
    end: int
    tags: tuple[Tag, ...]


@dataclass(frozen=True, slots=True)
class FormText:
    """One generated text with its gold names."""

    text: str
    names: tuple[GoldName, ...]


@dataclass(frozen=True, slots=True)
class NameLists:
    """The names one split draws from.

    Attributes:
        male_first: Men's first names.
        female_first: Women's first names.
        surnames: Surnames in the masculine form; women get `feminine_surname`.
        nicknames: Formal first name → its nickname.
        foreign_male_first: English men's first names (declined as hard nouns).
        foreign_female_first: English women's first names (indeclinable).
        foreign_surnames: English surnames; women's stay indeclinable.
    """

    male_first: tuple[Name, ...]
    female_first: tuple[Name, ...]
    surnames: tuple[Name, ...]
    nicknames: dict[str, Name]
    foreign_male_first: tuple[Name, ...] = ()
    foreign_female_first: tuple[Name, ...] = ()
    foreign_surnames: tuple[Name, ...] = ()


H, S, E = Paradigm.HARD, Paradigm.SOFT, Paradigm.MOBILE_E
AM, OM, ADJ = Paradigm.A_MASC, Paradigm.O_MASC, Paradigm.ADJ_MASC
AF, IE, IA = Paradigm.A_FEM, Paradigm.IE_FEM, Paradigm.IA_FEM


def _names(*entries: tuple[str, Paradigm]) -> tuple[Name, ...]:
    return tuple(Name(word, paradigm) for word, paradigm in entries)


NAMES: dict[str, dict[str, NameLists]] = {
    "cs": {
        "dev": NameLists(
            male_first=_names(
                ("Jan", H),
                ("Petr", H),
                ("Tomáš", S),
                ("Pavel", E),
                ("Jakub", H),
                ("Josef", H),
                ("Lukáš", S),
                ("Jiří", Paradigm.ADJ_SOFT),
            ),
            female_first=_names(
                ("Jana", AF),
                ("Petra", AF),
                ("Lenka", AF),
                ("Kamila", AF),
                ("Marie", IE),
                ("Eva", AF),
                ("Barbora", AF),
                ("Tereza", AF),
            ),
            surnames=_names(
                ("Novák", H),
                ("Dvořák", H),
                ("Navrátil", H),
                ("Zeman", H),
                ("Beneš", S),
                ("Kovář", S),
                ("Hájek", E),
                ("Bílek", E),
                ("Svoboda", AM),
                ("Hruška", AM),
                ("Novotný", ADJ),
                ("Černý", ADJ),
            ),
            nicknames={
                "Jan": Name("Honza", AM),
                "Josef": Name("Pepa", AM),
                "Jakub": Name("Kuba", AM),
                "Jiří": Name("Jirka", AM),
                "Jana": Name("Janička", AF),
                "Barbora": Name("Bára", AF),
                "Tereza": Name("Terka", AF),
                "Eva": Name("Evička", AF),
            },
            foreign_male_first=_names(("Sam", H), ("Jack", H)),
            foreign_female_first=_names(
                ("Megan", Paradigm.INDECLINABLE), ("Emily", Paradigm.INDECLINABLE)
            ),
            foreign_surnames=_names(("Taylor", H), ("Walker", H)),
        ),
        "test": NameLists(
            male_first=_names(
                ("Martin", H),
                ("Ondřej", S),
                ("Karel", E),
                ("David", H),
                ("Michal", H),
                ("Stanislav", H),
                ("Marek", E),
                ("Filip", H),
            ),
            female_first=_names(
                ("Hana", AF),
                ("Klára", AF),
                ("Monika", AF),
                ("Alena", AF),
                ("Lucie", IE),
                ("Ema", AF),
                ("Veronika", AF),
                ("Martina", AF),
            ),
            surnames=_names(
                ("Horák", H),
                ("Pospíšil", H),
                ("Musil", H),
                ("Kolář", S),
                ("Bartoš", S),
                ("Šimek", E),
                ("Kubíček", E),
                ("Procházka", AM),
                ("Vrána", AM),
                ("Sýkora", AM),
                ("Veselý", ADJ),
                ("Dvorský", ADJ),
            ),
            nicknames={
                "Stanislav": Name("Standa", AM),
                "Marek": Name("Mára", AM),
                "Ondřej": Name("Ondra", AM),
                "Klára": Name("Klárka", AF),
                "Veronika": Name("Verunka", AF),
                "Hana": Name("Hanka", AF),
                "Lucie": Name("Lucka", AF),
            },
            foreign_male_first=_names(("Ryan", H), ("Brian", H)),
            foreign_female_first=_names(
                ("Jennifer", Paradigm.INDECLINABLE), ("Ashley", Paradigm.INDECLINABLE)
            ),
            foreign_surnames=_names(("Turner", H), ("Cooper", H)),
        ),
    },
    "sk": {
        "dev": NameLists(
            male_first=_names(("Ján", H), ("Peter", E), ("Tomáš", S), ("Michal", H)),
            female_first=_names(("Jana", AF), ("Zuzana", AF), ("Mária", IA), ("Katarína", AF)),
            surnames=_names(
                ("Kováč", S),
                ("Horváth", H),
                ("Varga", AM),
                ("Malý", ADJ),
                ("Baláž", S),
                ("Hudák", H),
            ),
            nicknames={
                "Ján": Name("Janko", OM),
                "Michal": Name("Miško", OM),
                "Zuzana": Name("Zuzka", AF),
                "Katarína": Name("Katka", AF),
            },
        ),
        "test": NameLists(
            male_first=_names(("Martin", H), ("Juraj", S), ("Lukáš", S), ("Andrej", S)),
            female_first=_names(("Monika", AF), ("Lucia", IA), ("Petra", AF), ("Eva", AF)),
            surnames=_names(
                ("Tóth", H),
                ("Kollár", H),
                ("Mráz", H),
                ("Hruška", AM),
                ("Tichý", ADJ),
                ("Lukáč", S),
            ),
            nicknames={
                "Martin": Name("Maťko", OM),
                "Juraj": Name("Ďurko", OM),
                "Eva": Name("Evka", AF),
                "Lucia": Name("Lucka", AF),
            },
        ),
    },
}
"""Names per language and split; no name appears in both splits of a language."""

# Template syntax:
#   {P.full.gen}      person P's full name in the genitive (gold)
#   {P.titled.dat}    "panu Novákovi": the title, then the surname (gold)
#   {P.surname.acc}   the surname alone (gold)
#   {P.first.voc}     the first name alone (gold)
#   {P.nick.nom}      the nickname of P's first name (gold)
#   {P.sposs.f}       the possessive of the surname (gold), by `Agreement`
#   {P.fposs.n}       the possessive of the first name (gold)
#   {s~P.full.ins}    a preposition before a slot, vocalised as the next word
#                     needs ("se Svobodou"); s, k and v, capitalised as written
#   {P?přišel|přišla} text for a man | for a woman
# Persons: P and Q of either gender (alternating over the instances), M a man,
# W a woman, F a person with an English name.

TEMPLATES: dict[str, dict[str, tuple[str, ...]]] = {
    "cs": {
        "dev": (
            # full name
            "Kupní smlouvu za prodávajícího podepsal{P?|a} {P.full.nom} dne 3. května.",
            "Na schůzi byl{P?|a} za předsed{P?u|kyni} zvolen{P?|a} {P.full.nom}.",
            "Předání vozidla proběhne za přítomnosti {P?svědka pana|svědkyně paní} {P.full.gen}.",
            "Na žádost {P.full.gen} vydává úřad toto potvrzení.",
            "Kupní cena bude vyplacena {P.full.dat} do 14 dnů od podpisu.",
            "Děkujeme {P.full.dat} za dlouholetou spolupráci.",
            "Valná hromada jmenovala {P.full.acc} do funkce jednatel{P?e|ky}.",
            "Pro tuto věc zmocňuji {P.full.acc}, aby mě zastupoval{P?|a} při jednání s úřady.",
            "Gratulujeme, {P.full.voc}! Vaše přihláška byla přijata.",
            "Dobrý den, {P.full.voc},\nzasíláme Vám fakturu za měsíc říjen.",
            "Zpráva o {P.full.loc} byla předána vedení školy.",
            "Na poradě se jednalo o {P.full.loc} a {P?jeho|jejím} povýšení.",
            "Nájemní smlouva se uzavírá {s~P.full.ins} na dobu neurčitou.",
            "Jednání {s~P.full.ins} proběhne ve čtvrtek v 10 hodin.",
            # pan/paní and the surname
            "Vozidlo podle svědků řídil{P?|a} {P.titled.nom}.",
            "Na jednání se omluvil{P?|a} {P.titled.nom} z důvodu nemoci.",
            "Podle vyjádření {P.titled.gen} byla škoda nahlášena včas.",
            "Bez souhlasu {P.titled.gen} nelze smlouvu měnit.",
            "Klíče od bytu byly předány {P.titled.dat}.",
            "Za pomoc při stěhování patří dík {P.titled.dat}.",
            "Pověřujeme {P.titled.acc} vedením projektu.",
            "S dotazy se obraťte na {P.titled.acc} z účetního oddělení.",
            "Dobrý den, {P.titled.voc},\nposíláme opravenou smlouvu.",
            "Vážen{P?ý|á} {P.titled.voc},\nVaše žádost byla vyřízena.",
            "Ve zprávě o {P.titled.loc} chybí datum nástupu.",
            "Hovořili jsme o {P.titled.loc} a {P?jeho|jejím} návrhu.",
            "Schůzku {s~P.titled.ins} jsme přesunuli na pondělí.",
            "Smlouvu jsme {s~P.titled.ins} projednali telefonicky.",
            # the surname alone after a full mention
            "Žádost podal{P?|a} {P.full.nom}. {P.surname.nom} uvádí, že byt užívá od roku 2015.",
            "Do kanceláře nastoupil{P?|a} {P.full.nom}. Od září {P.surname.nom} vede účetní"
            " oddělení.",
            "Obviněn{P?ý|á} {P.full.nom} se k věci vyjádřil{P?|a} ústně. Námitky {P.surname.gen}"
            " správní orgán neshledal důvodnými.",
            "{P?Svědkem byl|Svědkyní byla} {P.full.nom}. Výpověď {P.surname.gen} potvrdila průběh"
            " nehody.",
            "Smlouvu podepsal{P?|a} {P.full.nom}. {P.surname.dat} byla zaslána kopie smlouvy.",
            "Byt užívá {P.full.nom}. Nájemné {P.surname.dat} zvýšíme od ledna.",
            "Hlídka zastavila {P.full.acc}. Policisté {P.surname.acc} poučili o právech.",
            "V soutěži zvítězil{P?|a} {P.full.nom}. Porota {P.surname.acc} ocenila za originalitu.",
            "Do týmu {P?přišel|přišla} {P.full.nom}. O {P.surname.loc} se kolegové vyjadřují"
            " pozitivně.",
            "Komise hodnotila {P.full.acc}. Na {P.surname.loc} oceňuje především spolehlivost.",
            "Pozvánku obdržel{P?|a} {P.full.nom}. {S~P.surname.ins} počítáme jako"
            " s {P?řečníkem|řečnicí}.",
            "Výběrové řízení vyhrál{P?|a} {P.full.nom}. Smlouvu {s~P.surname.ins} podepíšeme"
            " příští týden.",
            # the first name alone
            "Od: {P.full.nom}\nAhoj, posílám podklady na zítřek. Díky, {P.first.nom}",
            "Zprávu za tým poslal{P?|a} {P.full.nom}. Zítra {P.first.nom} dorazí až v deset.",
            "Ahoj {P.first.voc}, potřeboval{Q?|a} bych domluvit schůzku. {Q.first.nom}",
            "{P?Milý|Milá} {P.first.voc}, děkujeme za krásné přání.",
            "Dárek předáme {P.first.dat} na oslavě.",
            "Zavolej prosím {P.first.dat}, že porada začne později.",
            # nicknames
            "Na chatu přijede i {P.nick.nom} s rodinou.",
            "{P.nick.nom} slíbil{P?|a}, že přiveze stan.",
            "Ahoj {P.nick.voc}, v sobotu jedeme na výlet.",
            "{P.nick.voc}, nezapomeň vrátit klíče od chaty!",
            "Včera jsem potkal {P.nick.acc} v obchodě.",
            "Pozdravuj ode mě {P.nick.acc}.",
            # possessive adjectives
            "V bytě žije {M.full.nom} s rodinou. {M.sposs.f} manželka pracuje jako učitelka.",
            "Soud rozhodl o {M.sposs.m_loc} návrhu na obnovu řízení.",
            "Pes utekl ze zahrady. {M.sposs.m} soused tvrdí, že branka byla otevřená.",
            "{P.fposs.n} auto stálo celou noc před domem.",
            "Půjčil jsem si {P.fposs.f_acc} knihu a zapomněl ji vrátit.",
            "{S~P.fposs.f_ins} pomocí jsme projekt stihli včas.",
            # English names
            "Na konferenci vystoupil{F?|a} {F.full.nom} z Londýna.",
            "Školení povede {F?lektor|lektorka} {F.full.nom}.",
            "Děkujeme {F.full.dat} za přednášku.",
            "Na recepci čeká {F.first.nom}, {F?nový kolega|nová kolegyně} z Dublinu.",
            "Pošli prosím {F.first.dat} odkaz na prezentaci.",
            "Zítra mám schůzku {s~F.first.ins}.",
        ),
        "test": (
            # full name
            "Za pronajímatele jedná {P.full.nom}.",
            "Zápis z jednání vyhotovil{P?|a} {P.full.nom}.",
            "Plná moc se vydává na základě žádosti {P.full.gen}.",
            "Do kanceláře {P.full.gen} se dostavte v úterý.",
            "Úřad zašle rozhodnutí {P.full.dat} doporučeně.",
            "Ředitelka udělila pochvalu {P.full.dat} za vzornou práci.",
            "Komise doporučila přijmout {P.full.acc} do pracovního poměru.",
            "Na fotografii vidíte {P.full.acc} při předávání ceny.",
            "{P?Milý|Milá} {P.full.voc}, zveme Vás na slavnostní večer.",
            "Děkujeme, {P.full.voc}, za Váš nákup.",
            "V posudku o {P.full.loc} chybí hodnocení praxe.",
            "Psali jsme o {P.full.loc} už v minulém čísle zpravodaje.",
            "Rozhovor {s~P.full.ins} vyjde v příštím čísle.",
            "Soud jednal {s~P.full.ins} jako se {P?svědkem|svědkyní}.",
            # pan/paní and the surname
            "Tento týden vedoucí zastupuje {P.titled.nom}.",
            "Telefon zvedl{P?|a} {P.titled.nom} a slíbil{P?|a} zpětné volání.",
            "Kancelář {P.titled.gen} najdete ve druhém patře.",
            "Podpis {P.titled.gen} na smlouvě chybí.",
            "Fakturu jsme poslali {P.titled.dat} e-mailem.",
            "Zásilka byla doručena {P.titled.dat} do vlastních rukou.",
            "Ke schůzce jsme přizvali i {P.titled.acc}.",
            "Prosíme o zastoupení za {P.titled.acc} během dovolené.",
            "Dobrý den, {P.titled.voc}, potvrzuji přijetí Vaší zprávy.",
            "{P?Milý|Milá} {P.titled.voc},\nděkujeme za trpělivost.",
            "V dopise o {P.titled.loc} se uvádí chybná adresa.",
            "Kolegové mluví o {P.titled.loc} s velkým respektem.",
            "Včera jsme telefonovali {s~P.titled.ins} ohledně opravy.",
            "Pracovní smlouva {s~P.titled.ins} končí v prosinci.",
            # the surname alone after a full mention
            "Byt koupil{P?|a} {P.full.nom}. Podle notáře {P.surname.nom} zaplatil{P?|a} celou cenu"
            " najednou.",
            "Stížnost podal{P?|a} {P.full.nom}. Ve stížnosti {P.surname.nom} popisuje hluk ze"
            " sousedství.",
            "Na kurz se přihlásil{P?|a} {P.full.nom}. Přihlášku {P.surname.gen} jsme přijali.",
            "Úraz utrpěl{P?|a} {P.full.nom}. Zdravotní stav {P.surname.gen} je stabilizovaný.",
            "Odvolání podal{P?|a} {P.full.nom}. Soud {P.surname.dat} vyhověl jen zčásti.",
            "Kurz dokončil{P?|a} {P.full.nom}. Certifikát {P.surname.dat} pošleme poštou.",
            "Ve volbách kandidoval{P?|a} {P.full.nom}. Voliči {P.surname.acc} zvolili do"
            " zastupitelstva.",
            "Na pohovor {P?přišel|přišla} {P.full.nom}. Personalistka {P.surname.acc} doporučila na"
            " místo asistent{P?a|ky}.",
            "Ocenění převzal{P?|a} {P.full.nom}. V článku o {P.surname.loc} chybí fotografie.",
            "Školení vedl{P?|a} {P.full.nom}. Účastníci na {P.surname.loc} oceňovali srozumitelný"
            " výklad.",
            "Nabídku zaslal{P?|a} {P.full.nom}. {S~P.surname.ins} jsme se dohodli na slevě.",
            "Do projektu se zapojil{P?|a} {P.full.nom}. Spolupráci {s~P.surname.ins} hodnotíme"
            " kladně.",
            # the first name alone
            "Zprávu napsal{P?|a} {P.full.nom}.\nPS: {P.first.nom} se omlouvá, že nepřijde.",
            "Na fotce vpravo stojí {P.first.nom} s kolegy z oddělení.",
            "Čau {P.first.voc}, máš chvilku na kafe? {Q.first.nom}",
            "Ahoj {P.first.voc}, díky za fotky z výletu!",
            "Napiš prosím {P.first.dat}, kdy přijedeme.",
            "Půjčil jsem {P.first.dat} kolo na víkend.",
            # nicknames
            "Na oslavu dorazil{P?|a} i {P.nick.nom}.",
            "Včera mi volal{P?|a} {P.nick.nom}, že se stěhuje.",
            "Díky, {P.nick.voc}, za pomoc se stěhováním!",
            "{P.nick.voc}, zavolej mi, až budeš doma.",
            "Vezmeme s sebou i {P.nick.acc}.",
            "Na nádraží jsme čekali na {P.nick.acc} skoro hodinu.",
            # possessive adjectives
            "Firmu založil {M.full.nom}. {M.sposs.n} jméno dnes nese celá ulice.",
            "Policie prověřuje {M.sposs.f_acc} výpověď.",
            "{V~M.sposs.m_loc} domě se ještě svítí.",
            "{P.fposs.m} pes štěká celou noc.",
            "Celá rodina obdivuje {P.fposs.f_acc} zahradu.",
            "Před {P.fposs.f_ins} chalupou roste starý dub.",
            # English names
            "Přednášku přednesl{F?|a} {F.full.nom} z Manchesteru.",
            "Projekt vede {F?konzultant|konzultantka} {F.full.nom}.",
            "Poděkování patří {F.full.dat}.",
            "Zítra přiletí {F.first.nom} z Bostonu.",
            "Předej prosím {F.first.dat} tuto obálku.",
            "Byl jsem na obědě {s~F.first.ins}.",
        ),
    },
    "sk": {
        "dev": (
            "Zmluvu za predávajúceho podpísal{P?|a} {P.full.nom} 3. mája.",
            "Na žiadosť {P.full.gen} vydáva úrad toto potvrdenie.",
            "Kúpna cena bude vyplatená {P.full.dat} do 14 dní od podpisu.",
            "Valné zhromaždenie vymenovalo {P.full.acc} za konateľ{P?a|ku}.",
            "Na porade sa hovorilo o {P.full.loc} a {P?jeho|jej} povýšení.",
            "Nájomná zmluva sa uzatvára {s~P.full.ins} na dobu neurčitú.",
            "Vozidlo podľa svedkov {P?viedol|viedla} {P.titled.nom}.",
            "Vážen{P?ý|á} {P.titled.nom},\nVaša žiadosť bola vybavená.",
            "Podľa vyjadrenia {P.titled.gen} bola škoda nahlásená včas.",
            "Kľúče od bytu boli odovzdané {P.titled.dat}.",
            "Poverujeme {P.titled.acc} vedením projektu.",
            "V správe o {P.titled.loc} chýba dátum nástupu.",
            "Stretnutie {s~P.titled.ins} sme presunuli na pondelok.",
            "Žiadosť podal{P?|a} {P.full.nom}. {P.surname.nom} uvádza, že byt užíva od roku 2015.",
            "{P?Svedkom bol|Svedkyňou bola} {P.full.nom}. Výpoveď {P.surname.gen} potvrdila"
            " priebeh nehody.",
            "Zmluvu podpísal{P?|a} {P.full.nom}. {P.surname.dat} bola zaslaná kópia zmluvy.",
            "Hliadka zastavila {P.full.acc}. Policajti {P.surname.acc} poučili o právach.",
            "Výberové konanie vyhral{P?|a} {P.full.nom}. Zmluvu {s~P.surname.ins} podpíšeme"
            " budúci týždeň.",
            "Od: {P.full.nom}\nAhoj, posielam podklady na zajtra. Vďaka, {P.first.nom}",
            "Darček odovzdáme {P.first.dat} na oslave.",
            "Na chatu príde aj {P.nick.nom} s rodinou.",
            "Pozdravuj odo mňa {P.nick.acc}.",
            "Súd rozhodol o {M.sposs.m_loc} návrhu na obnovu konania.",
            "{P.fposs.n} auto stálo celú noc pred domom.",
        ),
        "test": (
            "Za prenajímateľa koná {P.full.nom}.",
            "Do kancelárie {P.full.gen} sa dostavte v utorok.",
            "Úrad zašle rozhodnutie {P.full.dat} doporučene.",
            "Komisia odporučila prijať {P.full.acc} do pracovného pomeru.",
            "V posudku o {P.full.loc} chýba hodnotenie praxe.",
            "Rozhovor {s~P.full.ins} vyjde v budúcom čísle.",
            "Telefón {P?zdvihol|zdvihla} {P.titled.nom} a sľúbil{P?|a}, že zavolá späť.",
            "Dobrý deň, {P.titled.nom},\npotvrdzujem prijatie Vašej správy.",
            "Kancelária {P.titled.gen} je na druhom poschodí.",
            "Faktúru sme poslali {P.titled.dat} e-mailom.",
            "Na stretnutie sme prizvali aj {P.titled.acc}.",
            "Kolegovia hovoria o {P.titled.loc} s veľkým rešpektom.",
            "Pracovná zmluva {s~P.titled.ins} končí v decembri.",
            "Byt kúpil{P?|a} {P.full.nom}. Podľa notára {P.surname.nom} zaplatil{P?|a} celú cenu"
            " naraz.",
            "Na kurz sa prihlásil{P?|a} {P.full.nom}. Prihlášku {P.surname.gen} sme prijali.",
            "Kurz dokončil{P?|a} {P.full.nom}. Certifikát {P.surname.dat} pošleme poštou.",
            "Vo voľbách kandidoval{P?|a} {P.full.nom}. Voliči {P.surname.acc} zvolili do"
            " zastupiteľstva.",
            "Do projektu sa zapojil{P?|a} {P.full.nom}. Spoluprácu {s~P.surname.ins} hodnotíme"
            " kladne.",
            "Na fotke vpravo stojí {P.first.nom} s kolegami z oddelenia.",
            "Napíš prosím {P.first.dat}, kedy prídeme.",
            "Na oslavu dorazil{P?|a} aj {P.nick.nom}.",
            "Zoberieme so sebou aj {P.nick.acc}.",
            "Polícia preveruje {M.sposs.f_acc} výpoveď.",
            "Celá rodina obdivuje {P.fposs.f_acc} záhradu.",
        ),
    },
}
"""Templates per language and split; evaluation only (see the module docstring)."""

CONTROLS: dict[str, dict[str, tuple[str, ...]]] = {
    "cs": {
        "dev": (
            "Kupující se zavazuje uhradit kupní cenu do 14 dnů. Prodávající prohlašuje, že na"
            " předmětu koupě neváznou dluhy.",
            "Žadatel doloží potvrzení o bezdlužnosti. Úřad rozhodne do 30 dnů od podání žádosti.",
            "Nájemce je povinen hradit nájemné vždy do 15. dne měsíce. Pronajímatel zajistí"
            " opravy společných prostor.",
            "Zhotovitel předá dílo Objednateli nejpozději do konce června.",
            "Zaměstnanec má nárok na dovolenou v délce pěti týdnů. Zaměstnavatel určí čerpání"
            " dovolené.",
            "Poplatník uhradí poplatek za komunální odpad do konce března. Správce poplatku vydá"
            " potvrzení.",
            "Svědek byl poučen o svých právech. Obviněný se k věci nevyjádřil.",
            "Krajský úřad Jihomoravského kraje v Brně vyzývá Uchazeče, aby doložili výpis z"
            " rejstříku trestů.",
        ),
        "test": (
            "Objednatel uhradí cenu díla na základě faktury. Zhotovitel odpovídá za vady díla po"
            " dobu dvou let.",
            "Pojištěný je povinen škodu bez odkladu oznámit. Pojistitel posoudí nárok do 30 dnů.",
            "Vlastník pozemku umožní přístup k vedení. Oprávněný uhradí jednorázovou náhradu.",
            "Dlužník splatí jistinu ve dvanácti splátkách. Věřitel může smlouvu vypovědět při"
            " prodlení.",
            "Student předloží potvrzení o studiu. Vedoucí katedry rozhodne o uznání předmětů.",
            "Pacient byl poučen o rizicích zákroku. Ošetřující lékař doporučil kontrolu za měsíc.",
            "Městský úřad Polička oznamuje, že Stavebník podal žádost o stavební povolení.",
            "Účastník řízení může podat odvolání do 15 dnů. Odvolací orgán rozhodne bez"
            " zbytečného odkladu.",
        ),
    },
    "sk": {
        "dev": (
            "Kupujúci sa zaväzuje uhradiť kúpnu cenu do 14 dní. Predávajúci vyhlasuje, že na veci"
            " neviaznu dlhy.",
            "Žiadateľ doloží potvrdenie o bezdlžnosti. Úrad rozhodne do 30 dní od podania"
            " žiadosti.",
            "Nájomca je povinný platiť nájomné vždy do 15. dňa v mesiaci. Prenajímateľ zabezpečí"
            " opravy spoločných priestorov.",
            "Zamestnanec má nárok na dovolenku v rozsahu piatich týždňov. Zamestnávateľ určí"
            " čerpanie dovolenky.",
        ),
        "test": (
            "Objednávateľ uhradí cenu diela na základe faktúry. Zhotoviteľ zodpovedá za vady"
            " diela dva roky.",
            "Poistený je povinný škodu bezodkladne oznámiť. Poisťovateľ posúdi nárok do 30 dní.",
            "Dlžník splatí istinu v dvanástich splátkach. Veriteľ môže zmluvu vypovedať pri"
            " omeškaní.",
            "Pacient bol poučený o rizikách zákroku. Ošetrujúci lekár odporučil kontrolu o mesiac.",
        ),
    },
}
"""Texts naming nobody, with capitalised role nouns; each is used once."""

_PLACEHOLDER = re.compile(
    r"\{(?:(?P<preposition>[sSkKvV])~)?(?P<person>[PQMWF])"
    r"(?:\.(?P<slot>full|titled|surname|first|nick|sposs|fposs)\.(?P<form>[a-z_]+)"
    r"|\?(?P<male>[^|}]*)\|(?P<female>[^}]*))\}"
)

# A preposition takes a vowel before a word starting with these letters.
_VOCALISED = {
    "cs": {"s": ("se", "szšž"), "k": ("ke", "kg"), "v": ("ve", "vf")},
    "sk": {"s": ("so", "szšž"), "k": ("ku", "kg"), "v": ("vo", "vf")},
}


@dataclass(frozen=True, slots=True)
class Person:
    """A generated person: gender and names, the surname already in its gendered form."""

    female: bool
    first: Name
    surname: Name
    nickname: Name | None
    foreign: bool


def generate(language: str, split: str) -> list[FormText]:
    """Return every text of one language and split, the same on every call.

    Args:
        language: `cs` or `sk`.
        split: `dev` or `test`.

    Returns:
        `INSTANCES` texts per template, in template order, then the texts
        naming nobody.

    Raises:
        ValueError: For an unknown language or split.
    """
    if language not in TEMPLATES or split not in SPLITS:
        msg = f"no name-forms texts for {language}/{split}"
        raise ValueError(msg)
    lists = NAMES[language][split]
    texts: list[FormText] = []
    for template in TEMPLATES[language][split]:
        # Seeded by the template itself, so editing one template leaves the
        # people of every other one unchanged.
        draw = random.Random(f"name-forms/{language}/{split}/{template}")
        for instance in range(INSTANCES):
            people = _cast(template, lists, draw, instance, language)
            texts.append(render(template, people, language))
    texts += [FormText(control, ()) for control in CONTROLS[language][split]]
    return texts


def _cast(
    template: str, lists: NameLists, draw: random.Random, instance: int, language: str
) -> dict[str, Person]:
    """Choose the people of one instance, all with different first names and surnames."""
    needs: dict[str, set[str]] = {}
    for found in _PLACEHOLDER.finditer(template):
        needs.setdefault(found["person"], set()).add(found["slot"] or "")
    people: dict[str, Person] = {}
    for letter in sorted(needs):
        female = _female(letter, instance)
        taken = {name for person in people.values() for name in (person.first, person.surname)}
        people[letter] = _person(letter, female, needs[letter], lists, draw, taken, language)
    return people


def _female(letter: str, instance: int) -> bool:
    if letter == "M":
        return False
    if letter == "W":
        return True
    if letter == "Q":  # pairs with P in all four ways over four instances
        return (instance // 2) % 2 == 1
    return instance % 2 == 1


def _person(
    letter: str,
    female: bool,
    slots: set[str],
    lists: NameLists,
    draw: random.Random,
    taken: set[Name],
    language: str,
) -> Person:
    if letter == "F":
        first_names = lists.foreign_female_first if female else lists.foreign_male_first
        surname = draw.choice(lists.foreign_surnames)
        if female:
            surname = Name(surname.word, Paradigm.INDECLINABLE)
        return Person(female, draw.choice(first_names), surname, None, foreign=True)
    first_names = [
        name
        for name in (lists.female_first if female else lists.male_first)
        if name not in taken
        and ("nick" not in slots or name.word in lists.nicknames)
        and ("fposs" not in slots or has_possessive(name, language))
    ]
    surnames = [
        name
        for name in lists.surnames
        if name not in taken and ("sposs" not in slots or has_possessive(name, language))
    ]
    first = draw.choice(first_names)
    surname = draw.choice(surnames)
    return Person(
        female,
        first,
        feminine_surname(surname) if female else surname,
        lists.nicknames.get(first.word),
        foreign=False,
    )


def render(template: str, people: dict[str, Person], language: str) -> FormText:
    """Fill a template with people; return the text and its gold names.

    Args:
        template: A template (syntax above `TEMPLATES`).
        people: The person of each letter the template uses.
        language: `cs` or `sk`.

    Returns:
        The NFC text with one gold span per name slot.
    """
    parts: list[str] = []
    names: list[GoldName] = []
    position = 0
    length = 0
    for found in _PLACEHOLDER.finditer(template):
        literal = template[position : found.start()]
        parts.append(literal)
        length += len(literal)
        position = found.end()
        person = people[found["person"]]
        if found["slot"] is None:
            chosen = found["female"] if person.female else found["male"]
            parts.append(chosen)
            length += len(chosen)
            continue
        lead, name, tags = _slot(person, found["slot"], found["form"], language)
        if found["preposition"]:
            lead = _preposition(found["preposition"], lead + name, language) + " " + lead
        names.append(GoldName(length + len(lead), length + len(lead) + len(name), tags))
        parts += [lead, name]
        length += len(lead) + len(name)
    parts.append(template[position:])
    text = "".join(parts)
    if unicodedata.normalize("NFC", text) != text:
        msg = "a template or name is not in NFC"
        raise ValueError(msg)
    return FormText(text, tuple(names))


def _preposition(written: str, following: str, language: str) -> str:
    vocalised, before = _VOCALISED[language][written.lower()]
    word = vocalised if following[:1].lower() in before else written.lower()
    return word.capitalize() if written.isupper() else word


def _slot(person: Person, slot: str, form: str, language: str) -> tuple[str, str, tuple[Tag, ...]]:
    """Return the text before the name, the name, and its tags."""
    gender = "f" if person.female else "m"
    if slot in {"sposs", "fposs"}:
        source = person.surname if slot == "sposs" else person.first
        kind = "surname-possessive" if slot == "sposs" else "first-name-possessive"
        name = possessive(source, Agreement(form), language)
        return "", name, _tags(kind, None, source, gender)
    case = Case(form)
    if slot == "full":
        first = decline(person.first, case, language, before_surname=True)
        kind = "foreign-full" if person.foreign else "full"
        name = f"{first} {decline(person.surname, case, language)}"
        return "", name, _tags(kind, case, person.surname, gender)
    if slot == "titled":
        lead = title(person.female, case, language) + " "
        name = decline(person.surname, case, language)
        return lead, name, _tags("title-surname", case, person.surname, gender)
    if slot == "surname":
        name = decline(person.surname, case, language)
        return "", name, _tags("later-surname", case, person.surname, gender)
    if slot == "nick":
        if person.nickname is None:
            msg = f"{person.first.word} has no nickname"
            raise ValueError(msg)
        name = decline(person.nickname, case, language)
        return "", name, _tags("nickname", case, person.nickname, gender)
    kind = "foreign-first" if person.foreign else "first-name"
    return "", decline(person.first, case, language), _tags(kind, case, person.first, gender)


def _tags(form: str, case: Case | None, carrier: Name, gender: str) -> tuple[Tag, ...]:
    tags: list[Tag] = [("form", form)]
    if case is not None:
        tags += [("case", str(case)), ("form-case", f"{form}/{case}")]
    else:
        tags.append(("form-case", form))
    tags += [("class", str(carrier.paradigm)), ("gender", gender)]
    return tuple(tags)
