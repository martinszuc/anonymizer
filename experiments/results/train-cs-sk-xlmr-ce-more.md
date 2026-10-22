# train-cs-sk-xlmr-ce-more-dev

rules+xlmr-cs-sk-ce-more after training (train-cs-sk-xlmr-ce-more).

Stage: dev · commit 0b2364ff37 · 2026-10-21T21:52:02+00:00 · seed 20261010, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce-more @ 79eb1ba17d · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.882 [0.79, 0.97] | 0.955 [0.86, 1.00] | 0.917 [0.85, 0.97] | 0.939 [0.86, 0.99] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more | 0.915 [0.88, 0.94] | 0.945 [0.92, 0.96] | 0.929 [0.91, 0.95] | 0.939 [0.92, 0.96] | 495 / 524 |
| phone | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more | 0.919 [0.89, 0.95] | 0.932 [0.91, 0.96] | 0.926 [0.90, 0.94] | 0.930 [0.91, 0.95] | 565 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.176 [0.06, 0.33] | 0.273 [0.10, 0.50] | 0.214 [0.07, 0.40] | 0.246 [0.09, 0.45] | 6 / 22 |
| email | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more | 0.866 [0.83, 0.90] | 0.891 [0.86, 0.92] | 0.879 [0.85, 0.91] | 0.886 [0.86, 0.91] | 467 / 524 |
| phone | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more | 0.838 [0.80, 0.88] | 0.853 [0.81, 0.89] | 0.846 [0.81, 0.88] | 0.850 [0.81, 0.88] | 517 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.276 [0.15, 0.39] | 0.409 [0.19, 0.67] | 0.9 [0.3, 1.8] | 9 / 22 |
| email | rules+xlmr-cs-sk-ce-more | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more | 0.037 [0.03, 0.05] | 0.926 [0.90, 0.95] | 4.1 [2.5, 5.7] | 485 / 524 |
| phone | rules+xlmr-cs-sk-ce-more | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more | 0.083 [0.06, 0.11] | 0.888 [0.85, 0.92] | 5.0 [3.2, 6.8] | 538 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.882 [0.80, 0.95] | 0.982 [0.97, 0.99] | 0.929 [0.88, 0.97] | 0.960 [0.94, 0.98] | 271 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.853 [0.77, 0.93] | 0.942 [0.90, 0.98] | 0.895 [0.84, 0.95] | 0.923 [0.88, 0.96] | 260 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.023 [0.01, 0.04] | 0.964 [0.93, 0.99] | 4.7 [1.8, 8.2] | 266 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.500 [0.33, 0.69] | 1.000 [1.00, 1.00] | 0.667 [0.50, 0.82] | 0.833 [0.71, 0.92] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more | 0.778 [0.62, 0.93] | 0.922 [0.80, 1.00] | 0.844 [0.73, 0.94] | 0.889 [0.79, 0.97] | 202 / 219 |
| phone | rules+xlmr-cs-sk-ce-more | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more | 0.785 [0.68, 0.88] | 0.869 [0.81, 0.92] | 0.825 [0.76, 0.88] | 0.851 [0.80, 0.90] | 337 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.407 [0.25, 0.60] | 0.815 [0.64, 0.96] | 0.543 [0.37, 0.72] | 0.679 [0.50, 0.83] | 22 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more | 0.579 [0.43, 0.74] | 0.690 [0.57, 0.81] | 0.629 [0.51, 0.75] | 0.664 [0.55, 0.78] | 151 / 219 |
| phone | rules+xlmr-cs-sk-ce-more | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more | 0.652 [0.54, 0.76] | 0.719 [0.65, 0.79] | 0.684 [0.60, 0.76] | 0.705 [0.63, 0.77] | 279 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 7.6 [2.8, 14.2] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce-more | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more | 0.056 [0.01, 0.14] | 0.877 [0.75, 0.98] | 9.7 [4.6, 16.5] | 192 / 219 |
| phone | rules+xlmr-cs-sk-ce-more | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more | 0.083 [0.05, 0.12] | 0.853 [0.78, 0.92] | 19.0 [11.7, 28.2] | 331 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.992 [0.99, 1.00] | 0.999 [1.00, 1.00] | 0.995 [0.99, 1.00] | 0.997 [1.00, 1.00] | 2116 / 2119 |
| email | rules+xlmr-cs-sk-ce-more | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce-more | 0.999 [1.00, 1.00] | 0.997 [1.00, 1.00] | 0.998 [1.00, 1.00] | 0.998 [1.00, 1.00] | 4341 / 4353 |
| any | rules+xlmr-cs-sk-ce-more | 0.997 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.996 [1.00, 1.00] | 9063 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.872 [0.86, 0.88] | 0.893 [0.88, 0.91] | 0.882 [0.87, 0.90] | 0.889 [0.88, 0.90] | 1893 / 2119 |
| email | rules+xlmr-cs-sk-ce-more | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-more | 0.986 [0.98, 0.99] | 0.985 [0.98, 0.99] | 0.986 [0.98, 0.99] | 0.985 [0.98, 0.99] | 4286 / 4353 |
| any | rules+xlmr-cs-sk-ce-more | 0.950 [0.95, 0.95] | 0.954 [0.95, 0.96] | 0.952 [0.95, 0.96] | 0.953 [0.95, 0.96] | 8674 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.002 [0.00, 0.00] | 0.996 [0.99, 1.00] | 1.1 [0.9, 1.3] | 2110 / 2119 |
| email | rules+xlmr-cs-sk-ce-more | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-more | 0.003 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.2 [0.1, 0.3] | 4327 / 4353 |
| any | rules+xlmr-cs-sk-ce-more | 0.007 [0.01, 0.01] | 0.982 [0.98, 0.98] | 1.4 [1.1, 1.6] | 8932 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.991 [0.99, 0.99] | 0.996 [0.99, 1.00] | 0.994 [0.99, 1.00] | 0.995 [0.99, 1.00] | 2109 / 2118 |
| email | rules+xlmr-cs-sk-ce-more | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce-more | 0.998 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.997 [0.99, 1.00] | 4327 / 4344 |
| any | rules+xlmr-cs-sk-ce-more | 0.997 [1.00, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.996 [0.99, 1.00] | 8886 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.854 [0.84, 0.87] | 0.877 [0.86, 0.89] | 0.865 [0.85, 0.88] | 0.872 [0.86, 0.89] | 1857 / 2118 |
| email | rules+xlmr-cs-sk-ce-more | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce-more | 0.980 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4248 / 4344 |
| any | rules+xlmr-cs-sk-ce-more | 0.945 [0.94, 0.95] | 0.948 [0.94, 0.95] | 0.947 [0.94, 0.95] | 0.948 [0.94, 0.95] | 8466 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more | 0.004 [0.00, 0.01] | 0.990 [0.98, 0.99] | 1.1 [0.9, 1.3] | 2096 / 2118 |
| email | rules+xlmr-cs-sk-ce-more | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce-more | 0.003 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.3 [0.2, 0.3] | 4317 / 4344 |
| any | rules+xlmr-cs-sk-ce-more | 0.007 [0.01, 0.01] | 0.983 [0.98, 0.99] | 1.5 [1.3, 1.7] | 8774 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.948 [0.90, 0.98] | 0.980 [0.96, 0.99] | 0.963 [0.93, 0.98] | 0.973 [0.96, 0.99] | 292 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.869 [0.81, 0.92] | 0.889 [0.84, 0.93] | 0.879 [0.83, 0.92] | 0.885 [0.84, 0.93] | 265 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.029 [0.01, 0.05] | 0.916 [0.88, 0.95] | 2.6 [1.3, 4.2] | 273 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.997 [0.99, 1.00] | 0.962 [0.93, 0.99] | 0.979 [0.96, 0.99] | 0.969 [0.95, 0.99] | 381 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.997 [0.99, 1.00] | 0.962 [0.93, 0.99] | 0.979 [0.96, 0.99] | 0.969 [0.95, 0.99] | 381 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more | 0.044 [0.02, 0.08] | 0.962 [0.93, 0.99] | 0.1 [0.0, 0.2] | 381 / 396 |
