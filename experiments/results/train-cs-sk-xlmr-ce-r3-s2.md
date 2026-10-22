# train-cs-sk-xlmr-ce-r3-s2-dev

rules+xlmr-cs-sk-ce-r3-s2 after training (train-cs-sk-xlmr-ce-r3-s2).

Stage: dev · commit 0b2364ff37 · 2026-10-21T20:49:23+00:00 · seed 2, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce-r3-s2 @ f46f8ad478 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.938 [0.83, 1.00] | 0.955 [0.86, 1.00] | 0.946 [0.88, 1.00] | 0.951 [0.88, 1.00] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.931 [0.90, 0.96] | 0.952 [0.93, 0.97] | 0.941 [0.92, 0.96] | 0.948 [0.93, 0.97] | 499 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.936 [0.91, 0.96] | 0.942 [0.92, 0.97] | 0.939 [0.92, 0.96] | 0.941 [0.92, 0.96] | 571 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.156 [0.04, 0.31] | 0.227 [0.06, 0.46] | 0.185 [0.04, 0.37] | 0.208 [0.05, 0.42] | 5 / 22 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.895 [0.86, 0.93] | 0.914 [0.89, 0.94] | 0.905 [0.88, 0.93] | 0.910 [0.88, 0.93] | 479 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.864 [0.82, 0.90] | 0.871 [0.83, 0.91] | 0.868 [0.83, 0.90] | 0.870 [0.83, 0.91] | 528 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.293 [0.16, 0.41] | 0.364 [0.16, 0.61] | 0.7 [0.2, 1.2] | 8 / 22 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.025 [0.02, 0.04] | 0.941 [0.92, 0.96] | 3.0 [1.8, 4.5] | 493 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3-s2 | 0.328 [0.09, 0.64] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.076 [0.05, 0.11] | 0.899 [0.86, 0.93] | 3.7 [2.3, 5.3] | 545 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.874 [0.79, 0.94] | 0.909 [0.86, 0.95] | 0.891 [0.84, 0.93] | 0.902 [0.86, 0.94] | 251 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.846 [0.75, 0.92] | 0.877 [0.82, 0.92] | 0.861 [0.80, 0.91] | 0.871 [0.82, 0.92] | 242 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.080 [0.04, 0.12] | 0.891 [0.84, 0.94] | 4.7 [1.9, 8.4] | 246 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.466 [0.32, 0.67] | 1.000 [1.00, 1.00] | 0.635 [0.48, 0.80] | 0.813 [0.70, 0.91] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.807 [0.64, 0.96] | 0.922 [0.80, 1.00] | 0.861 [0.74, 0.96] | 0.897 [0.79, 0.97] | 202 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.795 [0.67, 0.90] | 0.869 [0.80, 0.92] | 0.830 [0.75, 0.89] | 0.853 [0.80, 0.90] | 337 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.362 [0.22, 0.57] | 0.778 [0.61, 0.94] | 0.494 [0.33, 0.69] | 0.632 [0.45, 0.80] | 21 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.606 [0.46, 0.77] | 0.690 [0.58, 0.80] | 0.645 [0.54, 0.76] | 0.671 [0.57, 0.77] | 151 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.662 [0.55, 0.78] | 0.717 [0.65, 0.78] | 0.688 [0.61, 0.76] | 0.705 [0.64, 0.77] | 278 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.016 [0.00, 0.06] | 0.963 [0.88, 1.00] | 7.2 [2.7, 13.3] | 26 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce-r3-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.055 [0.01, 0.15] | 0.890 [0.77, 0.98] | 8.9 [4.2, 15.4] | 195 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.084 [0.05, 0.12] | 0.858 [0.79, 0.91] | 17.8 [10.5, 26.2] | 333 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.996 [0.99, 1.00] | 0.998 [1.00, 1.00] | 0.997 [1.00, 1.00] | 0.997 [1.00, 1.00] | 2114 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.998 [1.00, 1.00] | 0.998 [1.00, 1.00] | 0.998 [1.00, 1.00] | 0.998 [1.00, 1.00] | 4342 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.998 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.997 [1.00, 1.00] | 9062 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.876 [0.86, 0.89] | 0.893 [0.88, 0.91] | 0.884 [0.87, 0.90] | 0.890 [0.88, 0.90] | 1893 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.986 [0.98, 0.99] | 0.985 [0.98, 0.99] | 0.985 [0.98, 0.99] | 0.985 [0.98, 0.99] | 4287 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.951 [0.95, 0.96] | 0.954 [0.95, 0.96] | 0.952 [0.95, 0.96] | 0.953 [0.95, 0.96] | 8675 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.003 [0.00, 0.00] | 0.995 [0.99, 1.00] | 1.0 [0.8, 1.3] | 2108 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.003 [0.00, 0.00] | 0.995 [0.99, 1.00] | 0.2 [0.1, 0.3] | 4329 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.008 [0.01, 0.01] | 0.982 [0.98, 0.98] | 1.4 [1.1, 1.6] | 8932 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.994 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 2108 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.998 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.996 [0.99, 1.00] | 4326 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.997 [1.00, 1.00] | 0.995 [0.99, 1.00] | 0.996 [1.00, 1.00] | 0.996 [0.99, 1.00] | 8883 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.855 [0.84, 0.87] | 0.877 [0.86, 0.89] | 0.866 [0.85, 0.88] | 0.873 [0.86, 0.89] | 1858 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.981 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.979 [0.97, 0.98] | 4249 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.945 [0.94, 0.95] | 0.949 [0.94, 0.95] | 0.947 [0.94, 0.95] | 0.948 [0.94, 0.95] | 8467 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s2 | 0.004 [0.00, 0.01] | 0.990 [0.99, 0.99] | 1.1 [0.9, 1.3] | 2097 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3-s2 | 0.003 [0.00, 0.00] | 0.993 [0.99, 1.00] | 0.3 [0.2, 0.4] | 4314 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3-s2 | 0.008 [0.01, 0.01] | 0.983 [0.98, 0.99] | 1.5 [1.2, 1.7] | 8772 / 8927 |
