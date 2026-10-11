"""Declension rules against forms written out by hand, never produced by the rules themselves."""

import pytest

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

CASES = (Case.NOM, Case.GEN, Case.DAT, Case.ACC, Case.VOC, Case.LOC, Case.INS)
SLOVAK_CASES = (Case.NOM, Case.GEN, Case.DAT, Case.ACC, Case.LOC, Case.INS)

# nom, gen, dat, acc, voc, loc, ins
CZECH = [
    ("Novák", Paradigm.HARD, "Novák Nováka Novákovi Nováka Nováku Novákovi Novákem"),
    (
        "Navrátil",
        Paradigm.HARD,
        "Navrátil Navrátila Navrátilovi Navrátila Navrátile Navrátilovi Navrátilem",
    ),
    ("Petr", Paradigm.HARD, "Petr Petra Petrovi Petra Petře Petrovi Petrem"),
    ("Taylor", Paradigm.HARD, "Taylor Taylora Taylorovi Taylora Taylore Taylorovi Taylorem"),
    ("Jack", Paradigm.HARD, "Jack Jacka Jackovi Jacka Jacku Jackovi Jackem"),
    ("Beneš", Paradigm.SOFT, "Beneš Beneše Benešovi Beneše Beneši Benešovi Benešem"),
    ("Ondřej", Paradigm.SOFT, "Ondřej Ondřeje Ondřejovi Ondřeje Ondřeji Ondřejovi Ondřejem"),
    ("Hájek", Paradigm.MOBILE_E, "Hájek Hájka Hájkovi Hájka Hájku Hájkovi Hájkem"),
    ("Kubíček", Paradigm.MOBILE_E, "Kubíček Kubíčka Kubíčkovi Kubíčka Kubíčku Kubíčkovi Kubíčkem"),
    ("Pavel", Paradigm.MOBILE_E, "Pavel Pavla Pavlovi Pavla Pavle Pavlovi Pavlem"),
    ("Svoboda", Paradigm.A_MASC, "Svoboda Svobody Svobodovi Svobodu Svobodo Svobodovi Svobodou"),
    ("Hruška", Paradigm.A_MASC, "Hruška Hrušky Hruškovi Hrušku Hruško Hruškovi Hruškou"),
    ("Honza", Paradigm.A_MASC, "Honza Honzy Honzovi Honzu Honzo Honzovi Honzou"),
    (
        "Novotný",
        Paradigm.ADJ_MASC,
        "Novotný Novotného Novotnému Novotného Novotný Novotném Novotným",
    ),
    ("Jiří", Paradigm.ADJ_SOFT, "Jiří Jiřího Jiřímu Jiřího Jiří Jiřím Jiřím"),
    ("Nováková", Paradigm.OVA, "Nováková Novákové Novákové Novákovou Nováková Novákové Novákovou"),
    ("Novotná", Paradigm.ADJ_FEM, "Novotná Novotné Novotné Novotnou Novotná Novotné Novotnou"),
    ("Jana", Paradigm.A_FEM, "Jana Jany Janě Janu Jano Janě Janou"),
    ("Eva", Paradigm.A_FEM, "Eva Evy Evě Evu Evo Evě Evou"),
    ("Petra", Paradigm.A_FEM, "Petra Petry Petře Petru Petro Petře Petrou"),
    ("Lenka", Paradigm.A_FEM, "Lenka Lenky Lence Lenku Lenko Lence Lenkou"),
    ("Janička", Paradigm.A_FEM, "Janička Janičky Janičce Janičku Janičko Janičce Janičkou"),
    ("Kamila", Paradigm.A_FEM, "Kamila Kamily Kamile Kamilu Kamilo Kamile Kamilou"),
    ("Tereza", Paradigm.A_FEM, "Tereza Terezy Tereze Terezu Terezo Tereze Terezou"),
    ("Bára", Paradigm.A_FEM, "Bára Báry Báře Báru Báro Báře Bárou"),
    ("Marie", Paradigm.IE_FEM, "Marie Marie Marii Marii Marie Marii Marií"),
    ("Megan", Paradigm.INDECLINABLE, "Megan Megan Megan Megan Megan Megan Megan"),
]

# nom, gen, dat, acc, loc, ins
SLOVAK = [
    ("Kováč", Paradigm.SOFT, "Kováč Kováča Kováčovi Kováča Kováčovi Kováčom"),
    ("Horváth", Paradigm.HARD, "Horváth Horvátha Horváthovi Horvátha Horváthovi Horváthom"),
    ("Peter", Paradigm.MOBILE_E, "Peter Petra Petrovi Petra Petrovi Petrom"),
    ("Varga", Paradigm.A_MASC, "Varga Vargu Vargovi Vargu Vargovi Vargom"),
    ("Janko", Paradigm.O_MASC, "Janko Janka Jankovi Janka Jankovi Jankom"),
    ("Malý", Paradigm.ADJ_MASC, "Malý Malého Malému Malého Malom Malým"),
    ("Kováčová", Paradigm.OVA, "Kováčová Kováčovej Kováčovej Kováčovú Kováčovej Kováčovou"),
    ("Malá", Paradigm.ADJ_FEM, "Malá Malej Malej Malú Malej Malou"),
    ("Zuzana", Paradigm.A_FEM, "Zuzana Zuzany Zuzane Zuzanu Zuzane Zuzanou"),
    ("Monika", Paradigm.A_FEM, "Monika Moniky Monike Moniku Monike Monikou"),
    ("Mária", Paradigm.IA_FEM, "Mária Márie Márii Máriu Márii Máriou"),
]


@pytest.mark.parametrize(("word", "paradigm", "forms"), CZECH)
def test_czech_cases(word: str, paradigm: Paradigm, forms: str):
    name = Name(word, paradigm)
    assert [decline(name, case, "cs") for case in CASES] == forms.split()


@pytest.mark.parametrize(("word", "paradigm", "forms"), SLOVAK)
def test_slovak_cases(word: str, paradigm: Paradigm, forms: str):
    name = Name(word, paradigm)
    assert [decline(name, case, "sk") for case in SLOVAK_CASES] == forms.split()


def test_slovak_has_no_vocative():
    with pytest.raises(ValueError, match="nominative"):
        decline(Name("Kováč", Paradigm.SOFT), Case.VOC, "sk")


@pytest.mark.parametrize(
    ("word", "paradigm", "dative"),
    [
        ("Jan", Paradigm.HARD, "Janu"),
        ("Pavel", Paradigm.MOBILE_E, "Pavlu"),
        ("Tomáš", Paradigm.SOFT, "Tomáši"),
        ("Jiří", Paradigm.ADJ_SOFT, "Jiřímu"),
        ("Jana", Paradigm.A_FEM, "Janě"),
    ],
)
def test_a_czech_first_name_before_a_surname(word: str, paradigm: Paradigm, dative: str):
    # "Janu Novákovi", not "Janovi Novákovi": the -ovi goes on the surname only.
    assert decline(Name(word, paradigm), Case.DAT, "cs", before_surname=True) == dative


def test_a_slovak_first_name_keeps_ovi_before_a_surname():
    assert decline(Name("Ján", Paradigm.HARD), Case.DAT, "sk", before_surname=True) == "Jánovi"


@pytest.mark.parametrize(
    ("word", "paradigm", "language", "forms"),
    [
        ("Novák", Paradigm.HARD, "cs", "Novákův Novákova Novákovo Novákovu Novákovou Novákově"),
        ("Hájek", Paradigm.MOBILE_E, "cs", "Hájkův Hájkova Hájkovo Hájkovu Hájkovou Hájkově"),
        (
            "Svoboda",
            Paradigm.A_MASC,
            "cs",
            "Svobodův Svobodova Svobodovo Svobodovu Svobodovou Svobodově",
        ),
        ("Jana", Paradigm.A_FEM, "cs", "Janin Janina Janino Janinu Janinou Janině"),
        ("Petra", Paradigm.A_FEM, "cs", "Petřin Petřina Petřino Petřinu Petřinou Petřině"),
        ("Lenka", Paradigm.A_FEM, "cs", "Lenčin Lenčina Lenčino Lenčinu Lenčinou Lenčině"),
        ("Marie", Paradigm.IE_FEM, "cs", "Mariin Mariina Mariino Mariinu Mariinou Mariině"),
        ("Kováč", Paradigm.SOFT, "sk", "Kováčov Kováčova Kováčovo Kováčovu Kováčovou Kováčovom"),
        ("Zuzana", Paradigm.A_FEM, "sk", "Zuzanin Zuzanina Zuzanino Zuzaninu Zuzaninou Zuzaninom"),
        ("Mária", Paradigm.IA_FEM, "sk", "Máriin Máriina Máriino Máriinu Máriinou Máriinom"),
    ],
)
def test_possessives(word: str, paradigm: Paradigm, language: str, forms: str):
    name = Name(word, paradigm)
    assert [possessive(name, agreement, language) for agreement in Agreement] == forms.split()


@pytest.mark.parametrize(
    ("name", "language"),
    [
        (Name("Novotný", Paradigm.ADJ_MASC), "cs"),
        (Name("Nováková", Paradigm.OVA), "cs"),
        (Name("Megan", Paradigm.INDECLINABLE), "cs"),
        (Name("Jiří", Paradigm.ADJ_SOFT), "cs"),
        (Name("Monika", Paradigm.A_FEM), "sk"),
    ],
)
def test_names_without_a_possessive(name: Name, language: str):
    assert not has_possessive(name, language)
    with pytest.raises(ValueError, match="possessive"):
        possessive(name, Agreement.FEM, language)


@pytest.mark.parametrize(
    ("word", "paradigm", "feminine"),
    [
        ("Novák", Paradigm.HARD, "Nováková"),
        ("Beneš", Paradigm.SOFT, "Benešová"),
        ("Hájek", Paradigm.MOBILE_E, "Hájková"),
        ("Svoboda", Paradigm.A_MASC, "Svobodová"),
        ("Novotný", Paradigm.ADJ_MASC, "Novotná"),
        ("Kováč", Paradigm.SOFT, "Kováčová"),
        ("Taylor", Paradigm.INDECLINABLE, "Taylor"),
    ],
)
def test_feminine_surnames(word: str, paradigm: Paradigm, feminine: str):
    assert feminine_surname(Name(word, paradigm)).word == feminine


def test_titles():
    assert [title(False, case, "cs") for case in CASES] == [
        "pan",
        "pana",
        "panu",
        "pana",
        "pane",
        "panu",
        "panem",
    ]
    assert [title(True, case, "cs") for case in CASES] == ["paní"] * 7
    assert [title(False, case, "sk") for case in SLOVAK_CASES] == (
        ["pán", "pána", "pánovi", "pána", "pánovi", "pánom"]
    )
    assert title(True, Case.INS, "sk") == "pani"
    with pytest.raises(ValueError, match="title"):
        title(False, Case.VOC, "sk")


def test_patterns_refuse_what_they_do_not_cover():
    with pytest.raises(ValueError, match="mobile-e"):
        decline(Name("Novák", Paradigm.MOBILE_E), Case.GEN, "cs")
    with pytest.raises(ValueError, match="Slovak pattern"):
        decline(Name("Jiří", Paradigm.ADJ_SOFT), Case.GEN, "sk")
    with pytest.raises(ValueError, match="Czech pattern"):
        decline(Name("Janko", Paradigm.O_MASC), Case.GEN, "cs")
    with pytest.raises(ValueError, match="language"):
        decline(Name("Novák", Paradigm.HARD), Case.GEN, "pl")
    with pytest.raises(ValueError, match="feminine"):
        feminine_surname(Name("Jiří", Paradigm.ADJ_SOFT))
