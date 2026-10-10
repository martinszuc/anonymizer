# FUNSD scans: anonymizer 0.4.0

Run 2026-10-10T17:25:05+00:00 on Darwin arm64, Python 3.12.14, commit `6d9072f`. Detection: `rules+gliner`.

## onnxtr

| level | CER | diacritics | boxed | ink under boxes | partly outside | found | false alarms | readable after | partly after | safe | leak check passed | s/page |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test | 23.8% | n/a | 81.5% | 96.8% | 425/8707 | 119/182 | 179 | 51 | 5 | 23/50 | 48/50 | 1.92 |

## kraken

| level | CER | diacritics | boxed | ink under boxes | partly outside | found | false alarms | readable after | partly after | safe | leak check passed | s/page |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test | 24.5% | n/a | 53.8% | 93.9% | 602/8707 | 120/182 | 166 | 48 | 3 | 23/50 | 47/50 | 11.56 |

50 forms; derived items: address 10, person 103, phone 69.
