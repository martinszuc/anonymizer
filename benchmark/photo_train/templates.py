"""Templates of the photo training documents, written for this set alone.

Syntax (a slot is replaced by its value; a person slot is marked as gold):

    {A.full.gen}       first name and surname in a case (nom gen dat acc voc loc ins)
    {A.titled.dat}     "panu Tomanovi": the title before the gold surname
    {A.surname.ins}    the surname alone
    {A.first.voc}      the first name alone
    {A.initial.nom}    "V. Toman"
    {A.rev}            "Toman Vít", as forms list people
    {M.sposs.f}        possessive of a man's surname ("Tomanova"), by agreement
    {A.addr} {A.rc} {A.born} {A.phone} {A.email} {A.account} {A.iban}
    {s~A.full.ins}     a vocalised preposition before a slot ("se Šebestou")
    {A?text|text}      for a man | for a woman
    {doc.company} {doc.company2} {doc.ico} {doc.ref} {doc.issued} {doc.place}
    {doc.amount}       document values, not personal: companies, their IČO and
                       reference numbers are listed as decoys

Persons A to E are of either gender, alternating over the instances; M and N
are men, V and W women. Slovak has no vocative. Degrees ("MUDr.") and labels
stay outside the slot, so a gold span is the name alone.
"""

from __future__ import annotations

from dataclasses import dataclass

KINDS = ("contract", "cv", "invoice", "form", "letter", "medical", "school")


@dataclass(frozen=True, slots=True)
class Template:
    """One document template.

    Attributes:
        name: Unique id within its language; part of each document's name.
        kind: One of `KINDS`.
        lines: The document's paragraphs (syntax in the module docstring).
        decoys: Fixed strings of the lines that look personal but are not.
        families: Groups of person letters sharing a surname ("AC").
        children: Letters of people born 2010 to 2019.
        elders: Letters of people born 1954 to 1962.
    """

    name: str
    kind: str
    lines: tuple[str, ...]
    decoys: tuple[str, ...] = ()
    families: tuple[str, ...] = ()
    children: str = ""
    elders: str = ""


TEMPLATES: dict[str, tuple[Template, ...]] = {
    "cs": (
        Template(
            "loan",
            "contract",
            (
                "Smlouva o zápůjčce peněz",
                "uzavřená mezi {A.full.ins} a {B.full.ins} podle § 2390 zákona č. 89/2012 Sb.,"
                " občanský zákoník",
                "{A?Zapůjčitel|Zapůjčitelka}: {A.full.nom}, datum narození {A.born},"
                " rodné číslo {A.rc}, adresa pobytu {A.addr}",
                "{B?Vydlužitel|Vydlužitelka}: {B.full.nom}, rodné číslo {B.rc},"
                " adresa pobytu {B.addr}, mobil {B.phone}",
                "1. {A.titled.nom} půjčuje {B.titled.dat} částku {doc.amount}. Peníze pošle"
                " bezhotovostně na účet {B.account} nejpozději pátý pracovní den po podpisu.",
                "2. {B.surname.nom} vrátí půjčené peníze v deseti měsíčních splátkách na účet"
                " {A.account}. Splátky začnou běžet od {doc.issued}.",
                "3. Bude-li {B.surname.nom} se splátkou v prodlení déle než třicet dní, smí"
                " {A.surname.nom} chtít zbytek dluhu zaplatit najednou.",
                "4. Podpisu byl přítomen {M.full.nom}, jenž stvrzuje, že obě strany jednaly"
                " svobodně a vážně.",
                "{doc.place}, {doc.issued}",
                "Za {A?zapůjčitele|zapůjčitelku}: {A.full.nom}",
                "Za {B?vydlužitele|vydlužitelku}: {B.full.nom}",
            ),
            decoys=("§ 2390 zákona č. 89/2012 Sb.",),
        ),
        Template(
            "garage",
            "contract",
            (
                "Smlouva o nájmu garáže",
                "{A?Pronajímatel|Pronajímatelka}: {A.full.nom}, {A.addr},"
                " bankovní spojení {A.iban}",
                "{B?Nájemce|Nájemkyně}: {B.full.nom}, {B?narozen|narozena} {B.born},"
                " {B.addr}, e-mail {B.email}",
                "Pronajímatel přenechává do užívání řadovou garáž číslo 14 v areálu firmy"
                " {doc.company}, IČO {doc.ico}, za měsíční nájemné 1 500 Kč.",
                "Garáž bude {B.full.dat} předána dne {doc.issued} se dvěma klíči od vrat."
                " Nájemné posílá {B.titled.nom} vždy do patnáctého dne v měsíci na účet"
                " {A.iban}.",
                "Druhý klíč smí se souhlasem pronajímatele používat {C?bratr|sestra}"
                " {B?nájemce|nájemkyně} {C.full.nom}.",
                "Smlouva platí bez časového omezení, vypovědět ji lze s tříměsíční lhůtou."
                " Pronajímatel smí garáž zkontrolovat po předchozí domluvě s {B.titled.ins}.",
                "Za pronajímatele dnes jedná na základě plné moci {D.full.nom}, tel. {D.phone}.",
                "{doc.place}, {doc.issued}",
                "Podpisy: {A.initial.nom}, {B.initial.nom}",
            ),
            families=("BC",),
        ),
        Template(
            "cv",
            "cv",
            (
                "Životopis",
                "{A.full.nom}",
                "Narození: {A.born}",
                "Bydliště: {A.addr}",
                "Kontakt: {A.phone}, {A.email}",
                "Praxe",
                "Nyní: vedoucí skladu ve firmě {doc.company}. Řídím tým osmi skladníků,"
                " plánuji směny a odpovídám za čtvrtletní inventury.",
                "Předtím sedm let: skladní{A?k|ce} ve firmě {doc.company2}, kde mě zaučoval"
                " {M.full.nom}; s {M.titled.ins} jsem zaváděl{A?|a} čtečky čárových kódů.",
                "Vzdělání",
                "Střední průmyslová škola strojní, obor logistika, ukončeno maturitou",
                "Dovednosti",
                "Angličtina na úrovni B2, řidičský průkaz skupin B a C, průkaz obsluhy"
                " vysokozdvižného vozíku, pokročilá práce s tabulkami.",
                "Reference",
                "Na požádání je ochotna sdělit vedoucí provozu {V.full.nom}, telefon {V.phone}.",
                "Uvedené údaje smí firma použít jen pro toto výběrové řízení.",
            ),
        ),
        Template(
            "invoice",
            "invoice",
            (
                "Faktura číslo {doc.ref}",
                "Dodavatel: {doc.company}, IČO: {doc.ico}",
                "Odběratel: {A.full.nom}, {A.addr}",
                "Vystaveno: {doc.issued}, splatnost čtrnáct dní",
                "Předmět plnění: oprava plynového kotle a výměna oběhového čerpadla v rodinném"
                " domě {A.titled.gen}",
                "Celkem k úhradě včetně DPH: {doc.amount}",
                "Práci provedl servisní technik {M.full.nom}, který zákazníkovi předal"
                " protokol o zkoušce těsnosti.",
                "Fakturu převzal{A?|a}: {A.initial.nom}, telefon {A.phone}",
                "Platit lze i převodem z účtu {A.account}; jako variabilní symbol uveďte"
                " číslo faktury.",
                "Na čerpadlo poskytujeme záruku 24 měsíců. Reklamace řeší {V.titled.nom},"
                " e-mail {V.email}.",
            ),
        ),
        Template(
            "parking",
            "form",
            (
                "Žádost o parkovací kartu pro rezidenty",
                "Odbor dopravy Městského úřadu {doc.place}, číslo jednací {doc.ref}",
                "Příjmení a jméno žadatele: {A.rev}",
                "Narozen{A?|a}: {A.born}; rodné číslo: {A.rc}",
                "Adresa trvalého pobytu: {A.addr}",
                "Kontaktní telefon: {A.phone}",
                "Provozovatel vozidla, pokud jím není žadatel: {B.full.nom}, {B.addr}",
                "Kartu za žadatele vyzvedne: {C.full.nom}",
                "Poplatek 600 Kč uhradím z účtu {A.account} do deseti dnů od vydání karty.",
                "Karta se vydává podle § 23 zákona č. 13/1997 Sb., o pozemních komunikacích.",
                "Vyřizuje: {V.full.nom}, referentka odboru dopravy",
            ),
            decoys=("§ 23 zákona č. 13/1997 Sb.",),
            families=("AB",),
        ),
        Template(
            "deposit",
            "letter",
            (
                "{A.full.nom}, {A.addr}",
                "{B.full.nom}, {B.addr}",
                "{doc.place}, {doc.issued}",
                "Věc: vrácení kauce za byt",
                "Vážen{B?ý|á} {B.titled.voc},",
                "obracím se na Vás kvůli kauci 24 000 Kč, kterou jsem Vám složil{A?|a} při"
                " podpisu nájemní smlouvy. Byt jsem Vám předal{A?|a} poslední den nájmu"
                " vymalovaný a uklizený.",
                "Při předání byl přítomen Váš syn {M.full.nom}. {M.sposs.f} poznámka v"
                " předávacím protokolu potvrzuje, že byt nemá žádné závady.",
                "Kauci mi prosím pošlete na účet {A.iban} do konce tohoto měsíce. Kopii"
                " protokolu podepsanou {M.surname.ins} přikládám.",
                "Pokud se nedomluvíme, předám věc své advokátce JUDr. {V.full.dat}.",
                "S pozdravem",
                "{A.full.nom}, tel. {A.phone}",
            ),
            families=("BM",),
        ),
        Template(
            "discharge",
            "medical",
            (
                "Nemocnice {doc.place}, interní oddělení",
                "Propouštěcí zpráva",
                "{A?Pacient|Pacientka}: {A.rev}, narozen{A?|a} {A.born}, RČ {A.rc}",
                "Bydliště: {A.addr}, telefon {A.phone}",
                "Hospitalizace ukončena: {doc.issued}",
                "Ošetřující lékař: MUDr. {M.full.nom}",
                "Anamnéza: {A.titled.nom} byl{A?|a} přijat{A?|a} pro tlak na hrudi a dušnost"
                " při chůzi do schodů. Otec {A?pacienta|pacientky} prodělal infarkt.",
                "Průběh: Během pobytu byl{A?|a} {A.surname.nom} oběhově stabilní, zátěžový test"
                " bez známek ischemie.",
                "Doporučení: kontrola u praktické lékařky MUDr. {V.full.gen} do sedmi dnů,"
                " dieta s omezením soli.",
                "Informace o zdravotním stavu lze podávat {B?manželovi|manželce} {B.full.dat},"
                " telefon {B.phone}.",
                "Zprávu převzal{A?|a}: {A.initial.nom}",
            ),
            families=("AB",),
        ),
        Template(
            "camp",
            "school",
            (
                "Přihláška na letní příměstský tábor",
                "Pořádá Dům dětí a mládeže {doc.place}, oddíl turistiky",
                "Dítě: {C.full.nom}, datum narození {C.born}, rodné číslo {C.rc}",
                "Zákonný zástupce: {A.full.nom}, {A.addr}",
                "Telefon a e-mail zástupce: {A.phone}, {A.email}",
                "Dítě bude z tábora vyzvedávat také {B?dědeček|babička} {B.full.nom}.",
                "Souhlasím, aby {C.first.nom} odcházel{C?|a} domů {C?sám|sama} po skončení"
                " programu v 16 hodin.",
                "Táborový poplatek 3 200 Kč pošlu z účtu {A.account}; potvrzení o přijetí"
                " prosím zašlete {A.titled.dat} e-mailem.",
                "Vedoucí oddílu: Bc. {V.full.nom}; zdravotník tábora: {N.full.nom}",
                "Podpis zákonného zástupce: {A.initial.nom}",
            ),
            families=("AC",),
            children="C",
            elders="B",
        ),
    ),
    "sk": (
        Template(
            "loan",
            "contract",
            (
                "Zmluva o pôžičke peňazí",
                "uzatvorená podľa § 657 Občianskeho zákonníka č. 40/1964 Zb. medzi"
                " {A.full.ins} a {B.full.ins}",
                "{A?Veriteľ|Veriteľka}: {A.full.nom}, dátum narodenia {A.born},"
                " rodné číslo {A.rc}, bydlisko {A.addr}",
                "{B?Dlžník|Dlžníčka}: {B.full.nom}, RČ {B.rc}, bydlisko"
                " {B.addr}, telefón {B.phone}",
                "Článok 1. {A.titled.nom} požičiava {B.titled.dat} sumu {doc.amount}, ktorú"
                " pošle prevodom na účet {B.iban} najneskôr tretí pracovný deň po podpise.",
                "Článok 2. {B.surname.nom} vráti požičanú sumu v dvanástich mesačných splátkach,"
                " vždy do desiateho dňa v mesiaci, na účet {A.iban}.",
                "Článok 3. Ak sa {B.surname.nom} dostane do omeškania s dvoma splátkami, môže"
                " {A.surname.nom} chcieť zvyšok dlhu splatiť jednorazovo.",
                "Článok 4. Pri podpise bol prítomný svedok {M.full.nom}, bytom {M.addr}.",
                "{doc.place}, {doc.issued}",
                "Podpis {A?veriteľa|veriteľky}: {A.full.nom}",
                "Podpis {B?dlžníka|dlžníčky}: {B.full.nom}",
            ),
            decoys=("§ 657 Občianskeho zákonníka č. 40/1964 Zb.",),
        ),
        Template(
            "garden",
            "contract",
            (
                "Zmluva o nájme záhradkárskej parcely",
                "Prenajímateľ: Záhradkárska osada Pod Hájom, v zastúpení {A.full.ins},"
                " {A?predsedom|predsedníčkou} výboru osady",
                "{B?Nájomca|Nájomkyňa}: {B.full.nom}, {B?narodený|narodená} {B.born}, bytom"
                " {B.addr}, e-mail {B.email}",
                "Prenajímateľ prenecháva {B.titled.dat} do užívania parcelu číslo 27 s rozlohou"
                " tristodvadsať štvorcových metrov.",
                "Ročné nájomné 180 EUR uhradí {B.surname.nom} do konca marca na účet osady."
                " Vodu z osadného rozvodu platí podľa vodomeru.",
                "Parcelu môže spolu s {B?nájomcom|nájomkyňou} obhospodarovať aj"
                " {B?jeho|jej} {C?brat|sestra} {C.full.nom}.",
                "O žiadosti {B.titled.gen} o postavenie skleníka rozhodne výbor na najbližšej"
                " schôdzi.",
                "Kontakt na správcu osady: {M.full.nom}, tel. {M.phone}",
                "{doc.place}, {doc.issued}",
                "Podpisy zmluvných strán: {A.initial.nom}, {B.initial.nom}",
            ),
            decoys=("Záhradkárska osada Pod Hájom",),
            families=("BC",),
        ),
        Template(
            "cv",
            "cv",
            (
                "Životopis",
                "Meno a priezvisko: {A.full.nom}",
                "Dátum narodenia: {A.born}",
                "Adresa: {A.addr}",
                "Kontakt: {A.phone}, {A.email}",
                "Pracovné skúsenosti",
                "Súčasné zamestnanie: účtovní{A?k|čka} v spoločnosti {doc.company}; vediem mzdovú"
                " agendu pre šesťdesiat zamestnancov.",
                "Predtým šesť rokov: asistent{A?|ka} hlavnej účtovníčky v spoločnosti"
                " {doc.company2}, kde ma zaúčala {V.full.nom}.",
                "Vzdelanie",
                "Obchodná akadémia, odbor ekonomika podniku, maturita",
                "Jazyky: nemčina B1, angličtina A2",
                "Odporúčanie poskytne Ing. {M.full.nom}, vedúci ekonomického oddelenia,"
                " tel. {M.phone}.",
                "Záujmy: turistika, šach, dobrovoľníctvo v miestnej knižnici",
            ),
        ),
        Template(
            "invoice",
            "invoice",
            (
                "Faktúra číslo {doc.ref}",
                "Dodávateľ: {doc.company}, IČO: {doc.ico}",
                "Odberateľ: {A.full.nom}, {A.addr}",
                "Dátum vyhotovenia: {doc.issued}",
                "Za výmenu troch okien v byte {A.titled.gen} fakturujeme sumu {doc.amount}.",
                "Montáž vykonal {M.full.nom} spolu {s~N.full.ins}.",
                "Faktúru prevzal{A?|a}: {A.initial.nom}, tel. {A.phone}",
                "Sumu uhraďte do štrnástich dní; pri platbe z účtu {A.iban} uveďte ako"
                " variabilný symbol číslo faktúry.",
                "Otázky k faktúre vybaví {V.titled.nom}, e-mail {V.email}.",
                "Dodávateľ nie je platiteľom dane podľa zákona č. 222/2004 Z. z.",
            ),
            decoys=("zákona č. 222/2004 Z. z.",),
        ),
        Template(
            "fishing",
            "form",
            (
                "Žiadosť o vydanie povolenia na rybolov",
                "Miestna organizácia Slovenského rybárskeho zväzu {doc.place}",
                "Priezvisko a meno žiadateľa: {A.rev}",
                "Dátum narodenia: {A.born}, rodné číslo: {A.rc}",
                "Trvalé bydlisko: {A.addr}",
                "Telefón: {A.phone}",
                "Členský príspevok som uhradil{A?|a} z účtu {A.iban} dňa {doc.issued}.",
                "Za žiadateľa sa zaručuje člen výboru {M.full.nom}.",
                "Povolenie prevezme namiesto žiadateľa {B.full.nom} na základe splnomocnenia.",
                "Údaje spracúvame podľa zákona č. 18/2018 Z. z.",
                "Prijala: {V.full.nom}, tajomníčka organizácie, číslo žiadosti {doc.ref}",
            ),
            decoys=("zákona č. 18/2018 Z. z.",),
        ),
        Template(
            "trees",
            "letter",
            (
                "{A.full.nom}, {A.addr}",
                "Mestský úrad {doc.place}, k rukám {B.titled.gen}",
                "{doc.place}, {doc.issued}",
                "Vec: orezanie stromov pri ceste",
                "Vážen{B?ý|á} {B.titled.nom},",
                "obraciam sa na Vás so žiadosťou o orezanie dvoch líp, ktoré rastú pred domom"
                " môjho suseda {M.full.gen}. Ich konáre už zasahujú do elektrického vedenia.",
                "{M.titled.nom} s orezaním súhlasí a je ochotný pomôcť. Fotografie stromov Vám"
                " pošlem z adresy {A.email}.",
                "Ak by bolo treba stromy obhliadnuť, zastihnete ma na čísle {A.phone}; keď"
                " nebudem doma, dvor Vám ukáže {C?môj syn|moja dcéra} {C.full.nom}.",
                "Za kladné vybavenie vopred ďakujem.",
                "S pozdravom",
                "{A.full.nom}",
            ),
            families=("AC",),
        ),
        Template(
            "knee",
            "medical",
            (
                "Ortopedická ambulancia, Poliklinika Sever, {doc.place}",
                "Lekárska správa",
                "{A?Pacient|Pacientka}: {A.full.nom}, rodné číslo {A.rc}, dátum narodenia {A.born}",
                "Adresa: {A.addr}, telefón {A.phone}",
                "Odoslala: MUDr. {V.full.nom}, všeobecná lekárka",
                "Anamnéza: {A.titled.nom} pred dvoma týždňami {A?spadol|spadla} na schodoch"
                " a odvtedy {A?ho|ju} bolí pravé koleno.",
                "Nález: koleno opuchnuté, pohyblivosť obmedzená, röntgen bez zlomeniny.",
                "Záver: pomliaždenie pravého kolena.",
                "Odporúčanie: pokojový režim desať dní a kontrola u nás;"
                " {A?pacientovi|pacientke} {A.full.dat} sme vystavili potvrdenie o pracovnej"
                " neschopnosti.",
                "Na kontrolu {A?ho|ju} privezie {B?manžel|manželka} {B.full.nom}.",
                "Vyšetril: MUDr. {M.full.nom}, ortopéd",
                "{doc.place}, {doc.issued}",
            ),
            decoys=("Poliklinika Sever",),
            families=("AB",),
        ),
        Template(
            "leave",
            "school",
            (
                "Žiadosť o uvoľnenie žiaka z vyučovania",
                "Základná škola s materskou školou {doc.place}",
                "Triedna učiteľka: Mgr. {V.full.nom}",
                "{C?Žiak|Žiačka}: {C.full.nom}, trieda 6.B, dátum narodenia {C.born}",
                "Žiadam o uvoľnenie {C?môjho syna|mojej dcéry} {C.full.gen} z vyučovania"
                " na päť dní z rodinných dôvodov.",
                "Učivo z vynechaných hodín {C.first.nom} dobehne podľa pokynov vyučujúcich.",
                "Zákonný zástupca: {A.full.nom}, {A.addr}, tel. {A.phone}",
                "O uvoľnení na viac ako tri dni rozhoduje riaditeľ školy PaedDr. {M.full.nom}.",
                "Vyjadrenie triednej učiteľky: súhlasím, {C.surname.nom} prospieva bez problémov.",
                "Podpis zákonného zástupcu: {A.initial.nom}",
                "Rodné číslo žiaka pre evidenciu: {C.rc}",
            ),
            families=("AC",),
            children="C",
        ),
    ),
}
"""Templates per language, in the order documents cycle through them."""
