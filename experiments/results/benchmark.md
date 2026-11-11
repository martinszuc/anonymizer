# Benchmark: anonymizer 0.7.0

Run 2026-11-11T11:29:51+00:00 on Linux x86_64, Python 3.12.14, commit `04a732d`.
Models: `mdeberta-v3-base-tokenizer@a0484667b223`, `gliner-multi-v2.1@443d26d654e0`, `xlm-roberta-large-tokenizer@c23d21b0620b`, `nametag3-multilingual-260521@hdl:11234/1-`, `robeczech-base-v1.1-tokenizer@a75ff238206b`, `nametag3-czech-cnec2.0-240830@hdl:11234/1-`, `xlmr-cs-sk-ce-more@79eb1ba17d02`, `gliner-cs-sk-focal-more@c65dbc7ab2fc`, `xlmr-focal-more@0b7f1749d8a2`.

## Summary

| system | found | partial | missed | false alarms | per 1,000 words | decoys removed | safe documents | leak check passed | seconds |
|---|---|---|---|---|---|---|---|---|---|
| rules | 86/224 | 1 | 137 | 14 | 3.0 | 14 | 8/26 | 26/26 | 1.9 |
| rules+gliner | 198/224 | 1 | 25 | 44 | 9.4 | 28 | 17/26 | 26/26 | 191.3 |
| rules+nametag3-multilingual-260521 | 208/224 | 3 | 13 | 17 | 3.6 | 15 | 22/26 | 26/26 | 219.8 |
| rules+nametag3-czech-cnec2.0-240830 | 209/224 | 1 | 14 | 22 | 4.7 | 20 | 22/26 | 26/26 | 96.9 |
| rules+xlmr-focal-more | 212/224 | 0 | 12 | 26 | 5.6 | 20 | 22/26 | 25/26 | 480.0 |

## Found per type

| type | rules | rules+gliner | rules+nametag3-multilingual-260521 | rules+nametag3-czech-cnec2.0-240830 | rules+xlmr-focal-more |
|---|---|---|---|---|---|
| address | 20/23 | 22/23 | 20/23 | 22/23 | 23/23 |
| bank_account | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| birth_number | 7/7 | 7/7 | 7/7 | 7/7 | 7/7 |
| company_id | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| credit_card | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| date | 8/11 | 8/11 | 8/11 | 8/11 | 8/11 |
| email | 18/18 | 18/18 | 18/18 | 18/18 | 18/18 |
| iban | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| id_number | 1/4 | 2/4 | 1/4 | 1/4 | 1/4 |
| person | 0/128 | 109/128 | 122/128 | 121/128 | 123/128 |
| phone | 19/20 | 19/20 | 19/20 | 19/20 | 19/20 |
| url | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |

## Per carrier

| carrier | rules: found / left there | rules+gliner: found / left there | rules+nametag3-multilingual-260521: found / left there | rules+nametag3-czech-cnec2.0-240830: found / left there | rules+xlmr-focal-more: found / left there |
|---|---|---|---|---|---|
| annotation | 0/5 / 0 | 5/5 / 0 | 5/5 / 0 | 5/5 / 0 | 5/5 / 0 |
| bookmark | 0/2 / 0 | 2/2 / 0 | 2/2 / 0 | 2/2 / 0 | 2/2 / 0 |
| embedded_file | 0/4 / 0 | 2/4 / 0 | 2/4 / 0 | 2/4 / 0 | 2/4 / 0 |
| form_field | 4/8 / 0 | 7/8 / 0 | 6/8 / 0 | 7/8 / 0 | 7/8 / 0 |
| link | 7/7 / 0 | 7/7 / 0 | 7/7 / 0 | 7/7 / 0 | 7/7 / 0 |
| metadata | 0/15 / 0 | 14/15 / 0 | 13/15 / 0 | 13/15 / 0 | 14/15 / 0 |
| page | 75/179 / 109 | 160/179 / 23 | 172/179 / 5 | 172/179 / 6 | 174/179 / 4 |
| xmp | 0/4 / 0 | 1/4 / 0 | 1/4 / 0 | 1/4 / 0 | 1/4 / 0 |

## Per document kind

| kind | documents | rules: found / safe / false alarms | rules+gliner: found / safe / false alarms | rules+nametag3-multilingual-260521: found / safe / false alarms | rules+nametag3-czech-cnec2.0-240830: found / safe / false alarms | rules+xlmr-focal-more: found / safe / false alarms |
|---|---|---|---|---|---|---|
| authorization | 1 | 4/11 / 0/1 / 1 | 9/11 / 0/1 / 2 | 10/11 / 1/1 / 1 | 10/11 / 1/1 / 1 | 10/11 / 1/1 / 1 |
| contract | 3 | 20/50 / 0/3 / 3 | 47/50 / 2/3 / 3 | 48/50 / 3/3 / 4 | 48/50 / 3/3 / 3 | 49/50 / 3/3 / 3 |
| cv | 3 | 18/33 / 0/3 / 0 | 32/33 / 3/3 / 0 | 31/33 / 3/3 / 0 | 31/33 / 3/3 / 0 | 31/33 / 3/3 / 1 |
| decision | 1 | 4/13 / 0/1 / 0 | 12/13 / 0/1 / 0 | 12/13 / 0/1 / 0 | 12/13 / 0/1 / 0 | 12/13 / 0/1 / 0 |
| email | 3 | 11/33 / 0/3 / 3 | 25/33 / 1/3 / 3 | 31/33 / 2/3 / 3 | 30/33 / 2/3 / 3 | 31/33 / 2/3 / 3 |
| form | 1 | 8/18 / 1/1 / 0 | 16/18 / 1/1 / 0 | 14/18 / 1/1 / 0 | 16/18 / 1/1 / 0 | 16/18 / 1/1 / 0 |
| invoice | 2 | 9/15 / 0/2 / 3 | 14/15 / 1/2 / 3 | 14/15 / 1/2 / 3 | 14/15 / 1/2 / 3 | 14/15 / 1/2 / 3 |
| letter | 2 | 8/20 / 0/2 / 1 | 17/20 / 1/2 / 2 | 17/20 / 1/2 / 1 | 17/20 / 1/2 / 1 | 18/20 / 1/2 / 1 |
| minutes | 2 | 1/19 / 0/2 / 0 | 15/19 / 1/2 / 1 | 19/19 / 2/2 / 0 | 19/19 / 2/2 / 1 | 19/19 / 2/2 / 1 |
| notice | 2 | 0/0 / 2/2 / 0 | 0/0 / 2/2 / 11 | 0/0 / 2/2 / 0 | 0/0 / 2/2 / 4 | 0/0 / 2/2 / 6 |
| policy | 2 | 0/0 / 2/2 / 3 | 0/0 / 2/2 / 13 | 0/0 / 2/2 / 3 | 0/0 / 2/2 / 6 | 0/0 / 2/2 / 4 |
| report | 1 | 3/12 / 0/1 / 0 | 11/12 / 0/1 / 0 | 12/12 / 1/1 / 1 | 12/12 / 1/1 / 0 | 12/12 / 1/1 / 0 |
| rules | 1 | 0/0 / 1/1 / 0 | 0/0 / 1/1 / 6 | 0/0 / 1/1 / 1 | 0/0 / 1/1 / 0 | 0/0 / 1/1 / 3 |
| terms | 2 | 0/0 / 2/2 / 0 | 0/0 / 2/2 / 0 | 0/0 / 2/2 / 0 | 0/0 / 2/2 / 0 | 0/0 / 2/2 / 0 |

## Per document

| document | language | kind | rules: found / safe / false alarms | rules+gliner: found / safe / false alarms | rules+nametag3-multilingual-260521: found / safe / false alarms | rules+nametag3-czech-cnec2.0-240830: found / safe / false alarms | rules+xlmr-focal-more: found / safe / false alarms |
|---|---|---|---|---|---|---|---|
| cs-contract | cs | contract | 5/12 / **no** / 0 | 11/12 / **no** / 0 | 12/12 / yes / 0 | 12/12 / yes / 0 | 12/12 / yes / 0 |
| cs-cv | cs | cv | 8/14 / **no** / 0 | 14/14 / yes / 0 | 13/14 / yes / 0 | 13/14 / yes / 0 | 13/14 / yes / 0 |
| cs-decision | cs | decision | 4/13 / **no** / 0 | 12/13 / **no** / 0 | 12/13 / **no** / 0 | 12/13 / **no** / 0 | 12/13 / **no** / 0 |
| cs-email | cs | email | 5/15 / **no** / 1 | 11/15 / **no** / 1 | 15/15 / yes / 1 | 15/15 / yes / 1 | 15/15 / yes / 1 |
| cs-employment-contract | cs | contract | 6/18 / **no** / 3 | 16/18 / yes / 3 | 16/18 / yes / 4 | 16/18 / yes / 3 | 17/18 / yes / 3 |
| cs-gym-rules | cs | rules | 0/0 / yes / 0 | 0/0 / yes / 6 | 0/0 / yes / 1 | 0/0 / yes / 0 | 0/0 / yes / 3 |
| cs-invoice | cs | invoice | 4/6 / **no** / 1 | 6/6 / yes / 1 | 6/6 / yes / 1 | 6/6 / yes / 1 | 6/6 / yes / 1 |
| cs-long-report | cs | minutes | 1/3 / **no** / 0 | 3/3 / yes / 0 | 3/3 / yes / 0 | 3/3 / yes / 0 | 3/3 / yes / 0 |
| cs-notice | cs | notice | 0/0 / yes / 0 | 0/0 / yes / 3 | 0/0 / yes / 0 | 0/0 / yes / 2 | 0/0 / yes / 1 |
| cs-owners-minutes | cs | minutes | 0/16 / **no** / 0 | 12/16 / **no** / 1 | 16/16 / yes / 0 | 16/16 / yes / 1 | 16/16 / yes / 1 |
| cs-power-of-attorney | cs | authorization | 4/11 / **no** / 1 | 9/11 / **no** / 2 | 10/11 / yes / 1 | 10/11 / yes / 1 | 10/11 / yes / 1 |
| cs-privacy-notice | cs | policy | 0/0 / yes / 2 | 0/0 / yes / 9 | 0/0 / yes / 2 | 0/0 / yes / 3 | 0/0 / yes / 3 |
| cs-rental-contract | cs | contract | 9/20 / **no** / 0 | 20/20 / yes / 0 | 20/20 / yes / 0 | 20/20 / yes / 0 | 20/20 / yes / 0 |
| cs-school-form | cs | form | 8/18 / yes / 0 | 16/18 / yes / 0 | 14/18 / yes / 0 | 16/18 / yes / 0 | 16/18 / yes / 0 |
| cs-terms | cs | terms | 0/0 / yes / 0 | 0/0 / yes / 0 | 0/0 / yes / 0 | 0/0 / yes / 0 | 0/0 / yes / 0 |
| en-cv | en | cv | 4/7 / **no** / 0 | 7/7 / yes / 0 | 7/7 / yes / 0 | 7/7 / yes / 0 | 7/7 / yes / 0 |
| en-email | en | email | 2/9 / **no** / 1 | 5/9 / **no** / 1 | 7/9 / **no** / 1 | 6/9 / **no** / 1 | 7/9 / **no** / 1 |
| en-handbook | en | policy | 0/0 / yes / 1 | 0/0 / yes / 4 | 0/0 / yes / 1 | 0/0 / yes / 3 | 0/0 / yes / 1 |
| en-letter | en | letter | 3/11 / **no** / 1 | 8/11 / **no** / 2 | 8/11 / **no** / 1 | 8/11 / **no** / 1 | 9/11 / **no** / 1 |
| sk-cv | sk | cv | 6/12 / **no** / 0 | 11/12 / yes / 0 | 11/12 / yes / 0 | 11/12 / yes / 0 | 11/12 / yes / 1 |
| sk-email | sk | email | 4/9 / **no** / 1 | 9/9 / yes / 1 | 9/9 / yes / 1 | 9/9 / yes / 1 | 9/9 / yes / 1 |
| sk-invoice | sk | invoice | 5/9 / **no** / 2 | 8/9 / **no** / 2 | 8/9 / **no** / 2 | 8/9 / **no** / 2 | 8/9 / **no** / 2 |
| sk-letter | sk | letter | 5/9 / **no** / 0 | 9/9 / yes / 0 | 9/9 / yes / 0 | 9/9 / yes / 0 | 9/9 / yes / 0 |
| sk-medical-report | sk | report | 3/12 / **no** / 0 | 11/12 / **no** / 0 | 12/12 / yes / 1 | 12/12 / yes / 0 | 12/12 / yes / 0 |
| sk-terms | sk | terms | 0/0 / yes / 0 | 0/0 / yes / 0 | 0/0 / yes / 0 | 0/0 / yes / 0 | 0/0 / yes / 0 |
| sk-waste-notice | sk | notice | 0/0 / yes / 0 | 0/0 / yes / 8 | 0/0 / yes / 0 | 0/0 / yes / 2 | 0/0 / yes / 5 |

## Not found

| system | document | type | carrier | item | outcome | left readable |
|---|---|---|---|---|---|---|
| rules | cs-contract | person | page | Ondřej Dvořák | missed | yes |
| rules | cs-contract | person | page | Kateřina Veselá | missed | yes |
| rules | cs-contract | person | page | Kateřina Veselá | missed | yes |
| rules | cs-contract | person | page | Petra Svobody | missed | yes |
| rules | cs-contract | person | page | Ondřeji Dvořákovi | missed | yes |
| rules | cs-contract | person | page | Ondřej Dvořák | missed | yes |
| rules | cs-contract | person | page | Kateřina Veselá | missed | yes |
| rules | cs-cv | person | page | Tereza Procházková | missed | yes |
| rules | cs-cv | person | page | Ondřejem Dvořákem | missed | yes |
| rules | cs-cv | person | page | Kateřina Veselá | missed | yes |
| rules | cs-cv | person | metadata | Tereza Procházková | missed | yes |
| rules | cs-cv | id_number | metadata | TP-448812 | missed | no |
| rules | cs-cv | person | metadata | Tereza Procházková | missed | yes |
| rules | cs-decision | person | page | Alena Doubravová | missed | yes |
| rules | cs-decision | person | page | Vojtěch Sýkora | missed | yes |
| rules | cs-decision | id_number | page | 4H2 7781 | missed | yes |
| rules | cs-decision | person | page | Hana Malinová | missed | yes |
| rules | cs-decision | person | page | Sýkora | missed | yes |
| rules | cs-decision | person | page | Vojtěcha Sýkory | missed | yes |
| rules | cs-decision | person | page | Alena Doubravová | missed | yes |
| rules | cs-decision | person | page | Vojtěch Sýkora | missed | yes |
| rules | cs-decision | person | bookmark | Vojtěch Sýkora | missed | yes |
| rules | cs-email | person | page | Barbora Čermáková | missed | yes |
| rules | cs-email | person | page | Filip Navrátil | missed | yes |
| rules | cs-email | person | page | Navrátile | missed | yes |
| rules | cs-email | person | page | Roman Bartoš | missed | yes |
| rules | cs-email | person | page | Barbora Čermáková | missed | yes |
| rules | cs-email | person | page | Filip Navrátil | missed | yes |
| rules | cs-email | person | page | Báro | missed | yes |
| rules | cs-email | person | page | Bartoš | missed | yes |
| rules | cs-email | person | page | Filip | missed | yes |
| rules | cs-email | person | metadata | Barbora Čermáková | missed | yes |
| rules | cs-employment-contract | person | page | Radkem Hájkem | missed | yes |
| rules | cs-employment-contract | person | page | Petr Kalous | missed | yes |
| rules | cs-employment-contract | person | page | Petra Kalouse | missed | yes |
| rules | cs-employment-contract | person | page | Petru Kalousovi | missed | yes |
| rules | cs-employment-contract | person | page | Zdeňka Marková | missed | yes |
| rules | cs-employment-contract | person | page | Jitku Brabcovou | missed | yes |
| rules | cs-employment-contract | person | page | Radek Hájek | missed | yes |
| rules | cs-employment-contract | person | page | Petr Kalous | missed | yes |
| rules | cs-employment-contract | person | metadata | Kalous | missed | yes |
| rules | cs-employment-contract | person | metadata | Jitka Brabcová | missed | no |
| rules | cs-employment-contract | person | xmp | Jitka Brabcová | missed | no |
| rules | cs-employment-contract | person | xmp | Petr Kalous | missed | yes |
| rules | cs-invoice | person | page | Jan Novák | missed | yes |
| rules | cs-invoice | person | page | Jan Novák | missed | yes |
| rules | cs-long-report | person | page | Jana Malá | missed | yes |
| rules | cs-long-report | person | page | Lukáš Černý | missed | yes |
| rules | cs-owners-minutes | person | page | Zdeněk Vrána | missed | yes |
| rules | cs-owners-minutes | person | page | Olga Benešová | missed | yes |
| rules | cs-owners-minutes | person | page | Miloš Musil | missed | yes |
| rules | cs-owners-minutes | person | page | Daniela Krejčí | missed | yes |
| rules | cs-owners-minutes | person | page | Pavel Zeman | missed | yes |
| rules | cs-owners-minutes | person | page | Dvořákovi | missed | yes |
| rules | cs-owners-minutes | person | page | Zdeněk Vrána | missed | yes |
| rules | cs-owners-minutes | person | page | Olga Benešová | missed | yes |
| rules | cs-owners-minutes | person | page | Musil | missed | yes |
| rules | cs-owners-minutes | person | page | Krejčí | missed | yes |
| rules | cs-owners-minutes | person | page | Pavel Zeman | missed | yes |
| rules | cs-owners-minutes | person | page | Vránu | missed | yes |
| rules | cs-owners-minutes | person | page | Zemanem | missed | yes |
| rules | cs-owners-minutes | person | page | Olze Benešové | missed | yes |
| rules | cs-owners-minutes | person | page | Olga Benešová | missed | yes |
| rules | cs-owners-minutes | person | page | Zdeněk Vrána | missed | yes |
| rules | cs-power-of-attorney | person | page | Jaroslava Hrušková | missed | yes |
| rules | cs-power-of-attorney | person | page | Tomáše Vlčka | missed | yes |
| rules | cs-power-of-attorney | person | page | Hruškové | missed | yes |
| rules | cs-power-of-attorney | person | page | Jaroslava Hrušková | missed | yes |
| rules | cs-power-of-attorney | person | page | Tomáš Vlček | missed | yes |
| rules | cs-power-of-attorney | person | embedded_file | hruskova | missed | no |
| rules | cs-power-of-attorney | person | embedded_file | Jaroslava Hrušková | missed | yes |
| rules | cs-rental-contract | person | page | Jiří Holub | missed | yes |
| rules | cs-rental-contract | person | page | Lenka Šimková | missed | yes |
| rules | cs-rental-contract | person | page | Lence Šimkové | missed | yes |
| rules | cs-rental-contract | person | page | Jiřího Holuba | missed | yes |
| rules | cs-rental-contract | person | page | Martin Holub | missed | yes |
| rules | cs-rental-contract | person | page | Martina Holuba | missed | yes |
| rules | cs-rental-contract | person | page | Jiří Holub | missed | yes |
| rules | cs-rental-contract | person | page | Lenka Šimková | missed | yes |
| rules | cs-rental-contract | person | metadata | Lenka Šimková | missed | yes |
| rules | cs-rental-contract | person | annotation | Martin Holub | missed | yes |
| rules | cs-rental-contract | person | annotation | Šimkové | missed | yes |
| rules | cs-school-form | person | metadata | Tobiáš Kučera | missed | no |
| rules | cs-school-form | person | page | Tobiáš Kučera | missed | no |
| rules | cs-school-form | person | form_field | Tobiáš Kučera | missed | no |
| rules | cs-school-form | date | page | 15. 7. 2017 | missed | no |
| rules | cs-school-form | date | form_field | 15. 7. 2017 | missed | no |
| rules | cs-school-form | address | page | Bezručova 1680 | missed | no |
| rules | cs-school-form | address | form_field | Bezručova 1680 | missed | no |
| rules | cs-school-form | person | page | Markéta Kučerová | missed | no |
| rules | cs-school-form | person | form_field | Markéta Kučerová | missed | no |
| rules | cs-school-form | person | annotation | Ivana Pospíšilová | missed | no |
| rules | en-cv | person | page | Jordan Ellis | missed | yes |
| rules | en-cv | person | page | Priya Raman | missed | yes |
| rules | en-cv | person | metadata | Jordan Ellis | missed | yes |
| rules | en-email | person | page | Samuel Okafor | missed | yes |
| rules | en-email | person | page | Rachel | missed | yes |
| rules | en-email | person | page | Alan Whitfield | missed | yes |
| rules | en-email | person | page | Megan | missed | yes |
| rules | en-email | phone | page | +44 7700 900461 | missed | yes |
| rules | en-email | person | page | Sam | missed | yes |
| rules | en-email | person | embedded_file | okafor | missed | yes |
| rules | en-letter | person | page | Olivia Carter | missed | yes |
| rules | en-letter | address | page | 58 Maple Avenue, Apt 4B, Madison, WI 53703 | partial | yes |
| rules | en-letter | date | page | March 12, 1990 | missed | yes |
| rules | en-letter | person | page | Daniel Carter | missed | yes |
| rules | en-letter | person | page | Kevin Doyle | missed | yes |
| rules | en-letter | person | page | Olivia Carter | missed | yes |
| rules | en-letter | person | metadata | Olivia Carter | missed | yes |
| rules | en-letter | person | xmp | Olivia Carter | missed | yes |
| rules | sk-cv | person | page | Zuzana Kováčová | missed | yes |
| rules | sk-cv | person | page | Gabriele Šoltésovej | missed | yes |
| rules | sk-cv | person | page | Gabriela Šoltésová | missed | yes |
| rules | sk-cv | person | metadata | Zuzana Kováčová | missed | yes |
| rules | sk-cv | person | metadata | Zuzana Kováčová | missed | yes |
| rules | sk-cv | person | xmp | Zuzana Kováčová | missed | yes |
| rules | sk-email | person | page | Michal Gregor | missed | yes |
| rules | sk-email | person | page | Šimon Varga | missed | yes |
| rules | sk-email | person | page | Lukáčová | missed | yes |
| rules | sk-email | person | page | Michal Gregor | missed | yes |
| rules | sk-email | person | metadata | Michal Gregor | missed | yes |
| rules | sk-invoice | person | page | Marek Baláž | missed | yes |
| rules | sk-invoice | id_number | page | 1084572913 | missed | yes |
| rules | sk-invoice | person | page | Marek Baláž | missed | yes |
| rules | sk-invoice | person | embedded_file | Marek Baláž | missed | yes |
| rules | sk-letter | person | page | Mária Horváthová | missed | yes |
| rules | sk-letter | person | page | Mária Horváthová | missed | yes |
| rules | sk-letter | person | metadata | Mária Horváthová | missed | yes |
| rules | sk-letter | person | bookmark | Mária Horváthová | missed | yes |
| rules | sk-medical-report | person | page | Ladislav Hudák | missed | yes |
| rules | sk-medical-report | person | page | Hudák | missed | yes |
| rules | sk-medical-report | person | page | Anna Hudáková | missed | yes |
| rules | sk-medical-report | person | page | Petra Lacka | missed | yes |
| rules | sk-medical-report | person | page | Katarína Bieliková | missed | yes |
| rules | sk-medical-report | person | page | Juraj Fekete | missed | yes |
| rules | sk-medical-report | person | metadata | Katarína Bieliková | missed | yes |
| rules | sk-medical-report | person | annotation | Katarína Bieliková | missed | yes |
| rules | sk-medical-report | person | annotation | Hudákom | missed | no |
| rules+gliner | cs-contract | person | page | Petra Svobody | missed | yes |
| rules+gliner | cs-decision | id_number | page | 4H2 7781 | missed | yes |
| rules+gliner | cs-email | person | page | Navrátile | missed | yes |
| rules+gliner | cs-email | person | page | Báro | missed | yes |
| rules+gliner | cs-email | person | page | Bartoš | missed | yes |
| rules+gliner | cs-email | person | page | Filip | missed | yes |
| rules+gliner | cs-employment-contract | person | metadata | Kalous | missed | no |
| rules+gliner | cs-employment-contract | person | xmp | Jitka Brabcová | missed | no |
| rules+gliner | cs-owners-minutes | person | page | Musil | missed | yes |
| rules+gliner | cs-owners-minutes | person | page | Krejčí | missed | yes |
| rules+gliner | cs-owners-minutes | person | page | Vránu | missed | yes |
| rules+gliner | cs-owners-minutes | person | page | Zemanem | missed | yes |
| rules+gliner | cs-power-of-attorney | person | page | Hruškové | missed | yes |
| rules+gliner | cs-power-of-attorney | person | embedded_file | hruskova | missed | no |
| rules+gliner | cs-school-form | date | page | 15. 7. 2017 | missed | no |
| rules+gliner | cs-school-form | date | form_field | 15. 7. 2017 | missed | no |
| rules+gliner | en-email | person | page | Megan | missed | yes |
| rules+gliner | en-email | phone | page | +44 7700 900461 | missed | yes |
| rules+gliner | en-email | person | page | Sam | missed | yes |
| rules+gliner | en-email | person | embedded_file | okafor | missed | no |
| rules+gliner | en-letter | address | page | 58 Maple Avenue, Apt 4B, Madison, WI 53703 | partial | no |
| rules+gliner | en-letter | date | page | March 12, 1990 | missed | yes |
| rules+gliner | en-letter | person | xmp | Olivia Carter | missed | no |
| rules+gliner | sk-cv | person | xmp | Zuzana Kováčová | missed | no |
| rules+gliner | sk-invoice | id_number | page | 1084572913 | missed | yes |
| rules+gliner | sk-medical-report | person | page | Hudák | missed | yes |
| rules+nametag3-multilingual-260521 | cs-cv | id_number | metadata | TP-448812 | missed | no |
| rules+nametag3-multilingual-260521 | cs-decision | id_number | page | 4H2 7781 | missed | yes |
| rules+nametag3-multilingual-260521 | cs-employment-contract | person | metadata | Kalous | missed | no |
| rules+nametag3-multilingual-260521 | cs-employment-contract | person | xmp | Jitka Brabcová | missed | no |
| rules+nametag3-multilingual-260521 | cs-power-of-attorney | person | embedded_file | hruskova | missed | no |
| rules+nametag3-multilingual-260521 | cs-school-form | date | page | 15. 7. 2017 | missed | no |
| rules+nametag3-multilingual-260521 | cs-school-form | date | form_field | 15. 7. 2017 | missed | no |
| rules+nametag3-multilingual-260521 | cs-school-form | address | page | Bezručova 1680 | partial | no |
| rules+nametag3-multilingual-260521 | cs-school-form | address | form_field | Bezručova 1680 | partial | no |
| rules+nametag3-multilingual-260521 | en-email | phone | page | +44 7700 900461 | missed | yes |
| rules+nametag3-multilingual-260521 | en-email | person | embedded_file | okafor | missed | no |
| rules+nametag3-multilingual-260521 | en-letter | address | page | 58 Maple Avenue, Apt 4B, Madison, WI 53703 | partial | yes |
| rules+nametag3-multilingual-260521 | en-letter | date | page | March 12, 1990 | missed | yes |
| rules+nametag3-multilingual-260521 | en-letter | person | xmp | Olivia Carter | missed | no |
| rules+nametag3-multilingual-260521 | sk-cv | person | xmp | Zuzana Kováčová | missed | no |
| rules+nametag3-multilingual-260521 | sk-invoice | id_number | page | 1084572913 | missed | yes |
| rules+nametag3-czech-cnec2.0-240830 | cs-cv | id_number | metadata | TP-448812 | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | cs-decision | id_number | page | 4H2 7781 | missed | yes |
| rules+nametag3-czech-cnec2.0-240830 | cs-employment-contract | person | metadata | Kalous | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | cs-employment-contract | person | xmp | Jitka Brabcová | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | cs-power-of-attorney | person | embedded_file | hruskova | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | cs-school-form | date | page | 15. 7. 2017 | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | cs-school-form | date | form_field | 15. 7. 2017 | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | en-email | person | page | Megan | missed | yes |
| rules+nametag3-czech-cnec2.0-240830 | en-email | phone | page | +44 7700 900461 | missed | yes |
| rules+nametag3-czech-cnec2.0-240830 | en-email | person | embedded_file | okafor | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | en-letter | address | page | 58 Maple Avenue, Apt 4B, Madison, WI 53703 | partial | yes |
| rules+nametag3-czech-cnec2.0-240830 | en-letter | date | page | March 12, 1990 | missed | yes |
| rules+nametag3-czech-cnec2.0-240830 | en-letter | person | xmp | Olivia Carter | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | sk-cv | person | xmp | Zuzana Kováčová | missed | no |
| rules+nametag3-czech-cnec2.0-240830 | sk-invoice | id_number | page | 1084572913 | missed | yes |
| rules+xlmr-focal-more | cs-cv | id_number | metadata | TP-448812 | missed | no |
| rules+xlmr-focal-more | cs-decision | id_number | page | 4H2 7781 | missed | yes |
| rules+xlmr-focal-more | cs-employment-contract | person | xmp | Jitka Brabcová | missed | no |
| rules+xlmr-focal-more | cs-power-of-attorney | person | embedded_file | hruskova | missed | no |
| rules+xlmr-focal-more | cs-school-form | date | page | 15. 7. 2017 | missed | no |
| rules+xlmr-focal-more | cs-school-form | date | form_field | 15. 7. 2017 | missed | no |
| rules+xlmr-focal-more | en-email | phone | page | +44 7700 900461 | missed | yes |
| rules+xlmr-focal-more | en-email | person | embedded_file | okafor | missed | no |
| rules+xlmr-focal-more | en-letter | date | page | March 12, 1990 | missed | yes |
| rules+xlmr-focal-more | en-letter | person | xmp | Olivia Carter | missed | no |
| rules+xlmr-focal-more | sk-cv | person | xmp | Zuzana Kováčová | missed | no |
| rules+xlmr-focal-more | sk-invoice | id_number | page | 1084572913 | missed | yes |

## False alarms

| system | document | detected text |
|---|---|---|
| rules | cs-email | recepce@example.org |
| rules | cs-employment-contract | 262/2006 |
| rules | cs-employment-contract | 69281432 |
| rules | cs-employment-contract | Družstevní 1120, 572 01 Polička |
| rules | cs-invoice | 45862176 |
| rules | cs-power-of-attorney | Českobratrská 2227/7, 702 00 Ostrava |
| rules | cs-privacy-notice | Sochora 27, 170 00 Praha 7 |
| rules | cs-privacy-notice | gdpr@example.com |
| rules | en-email | hr@example.net |
| rules | en-handbook | people@example.org |
| rules | en-letter | Chicago, IL 60680 |
| rules | sk-email | zakaznicka.podpora@example.com |
| rules | sk-invoice | 36512281 |
| rules | sk-invoice | Poľná 4, 951 36 Lehota |
| rules+gliner | cs-email | recepce@example.org |
| rules+gliner | cs-employment-contract | 262/2006 |
| rules+gliner | cs-employment-contract | 69281432 |
| rules+gliner | cs-employment-contract | Družstevní 1120, 572 01 Polička |
| rules+gliner | cs-gym-rules | Trenér |
| rules+gliner | cs-gym-rules | Trenéra |
| rules+gliner | cs-gym-rules | Zdravotník |
| rules+gliner | cs-gym-rules | Údržbář |
| rules+gliner | cs-gym-rules | čísle 150 |
| rules+gliner | cs-gym-rules | čísle 155 |
| rules+gliner | cs-invoice | 45862176 |
| rules+gliner | cs-notice | Masarykově náměstí |
| rules+gliner | cs-notice | Nádražní ulice |
| rules+gliner | cs-notice | Starosta |
| rules+gliner | cs-owners-minutes | jednotky č. 7 |
| rules+gliner | cs-power-of-attorney | jejího |
| rules+gliner | cs-power-of-attorney | Českobratrská 2227/7, 702 00 Ostrava |
| rules+gliner | cs-privacy-notice | Pověřence |
| rules+gliner | cs-privacy-notice | Pověřenec |
| rules+gliner | cs-privacy-notice | Pplk. Sochora 27 |
| rules+gliner | cs-privacy-notice | Sochora 27, 170 00 Praha 7 |
| rules+gliner | cs-privacy-notice | Subjekt |
| rules+gliner | cs-privacy-notice | Uchazeče |
| rules+gliner | cs-privacy-notice | Zákazníka |
| rules+gliner | cs-privacy-notice | Zákazníků |
| rules+gliner | cs-privacy-notice | gdpr@example.com |
| rules+gliner | en-email | hr@example.net |
| rules+gliner | en-handbook | Data Protection Officer |
| rules+gliner | en-handbook | Head of People |
| rules+gliner | en-handbook | Line Manager |
| rules+gliner | en-handbook | people@example.org |
| rules+gliner | en-letter | Chicago, IL 60680 |
| rules+gliner | en-letter | PO Box 7720 |
| rules+gliner | sk-email | zakaznicka.podpora@example.com |
| rules+gliner | sk-invoice | 36512281 |
| rules+gliner | sk-invoice | Poľná 4, 951 36 Lehota |
| rules+gliner | sk-waste-notice | Hlavný |
| rules+gliner | sk-waste-notice | Poplatník |
| rules+gliner | sk-waste-notice | Poplatníka |
| rules+gliner | sk-waste-notice | Poplatníkom |
| rules+gliner | sk-waste-notice | Poplatníkovi |
| rules+gliner | sk-waste-notice | Prednosta |
| rules+gliner | sk-waste-notice | Priemyselnej ulici |
| rules+gliner | sk-waste-notice | Vlastník |
| rules+nametag3-multilingual-260521 | cs-email | recepce@example.org |
| rules+nametag3-multilingual-260521 | cs-employment-contract | 262/2006 |
| rules+nametag3-multilingual-260521 | cs-employment-contract | 69281432 |
| rules+nametag3-multilingual-260521 | cs-employment-contract | Družstevní 1120, 572 01 Polička |
| rules+nametag3-multilingual-260521 | cs-employment-contract | Ing |
| rules+nametag3-multilingual-260521 | cs-gym-rules | Údržbář |
| rules+nametag3-multilingual-260521 | cs-invoice | 45862176 |
| rules+nametag3-multilingual-260521 | cs-power-of-attorney | Českobratrská 2227/7, 702 00 Ostrava |
| rules+nametag3-multilingual-260521 | cs-privacy-notice | Sochora 27, 170 00 Praha 7 |
| rules+nametag3-multilingual-260521 | cs-privacy-notice | gdpr@example.com |
| rules+nametag3-multilingual-260521 | en-email | hr@example.net |
| rules+nametag3-multilingual-260521 | en-handbook | people@example.org |
| rules+nametag3-multilingual-260521 | en-letter | Chicago, IL 60680 |
| rules+nametag3-multilingual-260521 | sk-email | zakaznicka.podpora@example.com |
| rules+nametag3-multilingual-260521 | sk-invoice | 36512281 |
| rules+nametag3-multilingual-260521 | sk-invoice | Poľná 4, 951 36 Lehota |
| rules+nametag3-multilingual-260521 | sk-medical-report | MUDr |
| rules+nametag3-czech-cnec2.0-240830 | cs-email | recepce@example.org |
| rules+nametag3-czech-cnec2.0-240830 | cs-employment-contract | 262/2006 |
| rules+nametag3-czech-cnec2.0-240830 | cs-employment-contract | 69281432 |
| rules+nametag3-czech-cnec2.0-240830 | cs-employment-contract | Družstevní 1120, 572 01 Polička |
| rules+nametag3-czech-cnec2.0-240830 | cs-invoice | 45862176 |
| rules+nametag3-czech-cnec2.0-240830 | cs-notice | Masarykově náměstí |
| rules+nametag3-czech-cnec2.0-240830 | cs-notice | Nádražní ulice |
| rules+nametag3-czech-cnec2.0-240830 | cs-owners-minutes | Na Vyhlídce, Kolín |
| rules+nametag3-czech-cnec2.0-240830 | cs-power-of-attorney | Českobratrská 2227/7, 702 00 Ostrava |
| rules+nametag3-czech-cnec2.0-240830 | cs-privacy-notice | Sochora |
| rules+nametag3-czech-cnec2.0-240830 | cs-privacy-notice | Sochora 27, 170 00 Praha 7 |
| rules+nametag3-czech-cnec2.0-240830 | cs-privacy-notice | gdpr@example.com |
| rules+nametag3-czech-cnec2.0-240830 | en-email | hr@example.net |
| rules+nametag3-czech-cnec2.0-240830 | en-handbook | Finch |
| rules+nametag3-czech-cnec2.0-240830 | en-handbook | Harrow |
| rules+nametag3-czech-cnec2.0-240830 | en-handbook | people@example.org |
| rules+nametag3-czech-cnec2.0-240830 | en-letter | Lakeshore Federal Bank, PO Box 7720, Chicago, IL 60680 |
| rules+nametag3-czech-cnec2.0-240830 | sk-email | zakaznicka.podpora@example.com |
| rules+nametag3-czech-cnec2.0-240830 | sk-invoice | 36512281 |
| rules+nametag3-czech-cnec2.0-240830 | sk-invoice | Agro Dvor Lehota, s. r. o., Poľná 4, 951 36 Lehota |
| rules+nametag3-czech-cnec2.0-240830 | sk-waste-notice | Hron |
| rules+nametag3-czech-cnec2.0-240830 | sk-waste-notice | Priemyselnej ulici |
| rules+xlmr-focal-more | cs-email | recepce@example.org |
| rules+xlmr-focal-more | cs-employment-contract | 262/2006 |
| rules+xlmr-focal-more | cs-employment-contract | 69281432 |
| rules+xlmr-focal-more | cs-employment-contract | Družstevní 1120, 572 01 Polička |
| rules+xlmr-focal-more | cs-gym-rules | Lukách |
| rules+xlmr-focal-more | cs-gym-rules | Trenéra |
| rules+xlmr-focal-more | cs-gym-rules | Údržbář |
| rules+xlmr-focal-more | cs-invoice | 45862176 |
| rules+xlmr-focal-more | cs-notice | Masarykově náměstí |
| rules+xlmr-focal-more | cs-owners-minutes | Na Vyhlídce, Kolín |
| rules+xlmr-focal-more | cs-power-of-attorney | Českobratrská 2227/7, 702 00 Ostrava |
| rules+xlmr-focal-more | cs-privacy-notice | Pplk. Sochora 27, 170 00 Praha 7 |
| rules+xlmr-focal-more | cs-privacy-notice | Uchazeče |
| rules+xlmr-focal-more | cs-privacy-notice | gdpr@example.com |
| rules+xlmr-focal-more | en-email | hr@example.net |
| rules+xlmr-focal-more | en-handbook | people@example.org |
| rules+xlmr-focal-more | en-letter | Chicago, IL 60680 |
| rules+xlmr-focal-more | sk-cv | Ing |
| rules+xlmr-focal-more | sk-email | zakaznicka.podpora@example.com |
| rules+xlmr-focal-more | sk-invoice | 36512281 |
| rules+xlmr-focal-more | sk-invoice | Poľná 4, 951 36 Lehota |
| rules+xlmr-focal-more | sk-waste-notice | Hlavný |
| rules+xlmr-focal-more | sk-waste-notice | Poplatník |
| rules+xlmr-focal-more | sk-waste-notice | Poplatníka |
| rules+xlmr-focal-more | sk-waste-notice | Poplatníkovi |
| rules+xlmr-focal-more | sk-waste-notice | Priemyselnej ulici |
