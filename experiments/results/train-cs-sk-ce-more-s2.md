# train-cs-sk-ce-more-s2-dev

rules+gliner-cs-sk-ce-more-s2 after training (train-cs-sk-ce-more-s2).

Stage: dev · commit 0b2364ff37 · 2026-10-21T22:37:36+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-ce-more-s2 @ b88b5e5da6 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.929 [0.83, 1.00] | 0.864 [0.71, 1.00] | 0.895 [0.79, 0.96] | 0.876 [0.74, 0.98] | 19 / 22 |
| email | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.890 [0.85, 0.92] | 0.937 [0.91, 0.96] | 0.913 [0.89, 0.93] | 0.927 [0.90, 0.95] | 491 / 524 |
| phone | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.899 [0.87, 0.93] | 0.921 [0.89, 0.95] | 0.910 [0.88, 0.93] | 0.916 [0.89, 0.94] | 558 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.179 [0.05, 0.38] | 0.227 [0.07, 0.46] | 0.200 [0.06, 0.41] | 0.215 [0.07, 0.42] | 5 / 22 |
| email | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.848 [0.81, 0.88] | 0.895 [0.87, 0.92] | 0.871 [0.84, 0.90] | 0.885 [0.86, 0.91] | 469 / 524 |
| phone | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.829 [0.79, 0.86] | 0.855 [0.81, 0.89] | 0.842 [0.81, 0.87] | 0.850 [0.81, 0.88] | 518 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.428 [0.27, 0.57] | 0.318 [0.12, 0.56] | 0.5 [0.1, 1.1] | 7 / 22 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.049 [0.03, 0.07] | 0.910 [0.89, 0.93] | 4.8 [3.4, 6.4] | 477 / 524 |
| phone | rules+gliner-cs-sk-ce-more-s2 | 0.328 [0.09, 0.64] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.108 [0.07, 0.15] | 0.871 [0.83, 0.90] | 5.2 [3.7, 6.9] | 528 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.858 [0.77, 0.93] | 0.971 [0.95, 0.99] | 0.911 [0.86, 0.95] | 0.946 [0.92, 0.96] | 268 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.819 [0.74, 0.89] | 0.917 [0.87, 0.96] | 0.865 [0.81, 0.91] | 0.895 [0.85, 0.93] | 253 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.023 [0.01, 0.04] | 0.953 [0.91, 0.98] | 5.5 [2.6, 9.2] | 263 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.571 [0.41, 0.75] | 1.000 [1.00, 1.00] | 0.727 [0.58, 0.85] | 0.870 [0.78, 0.94] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.810 [0.65, 0.96] | 0.991 [0.98, 1.00] | 0.891 [0.78, 0.98] | 0.949 [0.89, 0.99] | 217 / 219 |
| phone | rules+gliner-cs-sk-ce-more-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.817 [0.70, 0.91] | 0.905 [0.86, 0.94] | 0.858 [0.79, 0.91] | 0.886 [0.84, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.449 [0.30, 0.63] | 0.815 [0.65, 0.97] | 0.579 [0.42, 0.75] | 0.701 [0.55, 0.85] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.612 [0.46, 0.77] | 0.722 [0.61, 0.83] | 0.662 [0.54, 0.78] | 0.697 [0.59, 0.80] | 158 / 219 |
| phone | rules+gliner-cs-sk-ce-more-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.681 [0.58, 0.78] | 0.737 [0.68, 0.80] | 0.708 [0.64, 0.77] | 0.725 [0.67, 0.79] | 286 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.0 [2.6, 9.9] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-ce-more-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.011 [0.00, 0.02] | 0.977 [0.95, 1.00] | 10.6 [5.5, 17.5] | 214 / 219 |
| phone | rules+gliner-cs-sk-ce-more-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.067 [0.04, 0.10] | 0.907 [0.85, 0.95] | 18.4 [12.2, 25.4] | 352 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.995 [0.99, 1.00] | 0.951 [0.94, 0.96] | 0.973 [0.97, 0.98] | 0.960 [0.95, 0.97] | 2016 / 2119 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.995 [0.99, 1.00] | 0.987 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.989 [0.99, 0.99] | 4298 / 4353 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.996 [0.99, 1.00] | 0.981 [0.98, 0.98] | 0.988 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8923 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.844 [0.83, 0.86] | 0.822 [0.80, 0.84] | 0.832 [0.82, 0.85] | 0.826 [0.81, 0.84] | 1741 / 2119 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.983 [0.98, 0.99] | 0.976 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4248 / 4353 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.943 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.938 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8485 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.086 [0.07, 0.10] | 0.928 [0.92, 0.94] | 1.1 [0.9, 1.4] | 1967 / 2119 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.010 [0.01, 0.01] | 0.985 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4288 / 4353 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.039 [0.03, 0.04] | 0.962 [0.96, 0.97] | 1.5 [1.2, 1.7] | 8750 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.990 [0.99, 0.99] | 0.952 [0.94, 0.96] | 0.971 [0.97, 0.98] | 0.960 [0.95, 0.97] | 2017 / 2118 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.995 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.98, 0.99] | 4285 / 4344 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.996 [0.99, 1.00] | 0.981 [0.98, 0.98] | 0.988 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8758 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.829 [0.81, 0.85] | 0.812 [0.79, 0.83] | 0.821 [0.80, 0.84] | 0.816 [0.80, 0.83] | 1720 / 2118 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.975 [0.97, 0.98] | 0.966 [0.96, 0.97] | 0.971 [0.97, 0.98] | 0.968 [0.96, 0.97] | 4198 / 4344 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.938 [0.93, 0.94] | 0.928 [0.92, 0.93] | 0.933 [0.93, 0.94] | 0.930 [0.92, 0.94] | 8281 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s2 | 0.095 [0.08, 0.11] | 0.933 [0.92, 0.94] | 1.3 [1.1, 1.6] | 1976 / 2118 |
| email | rules+gliner-cs-sk-ce-more-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-ce-more-s2 | 0.009 [0.01, 0.01] | 0.983 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4271 / 4344 |
| any | rules+gliner-cs-sk-ce-more-s2 | 0.040 [0.03, 0.05] | 0.964 [0.96, 0.97] | 1.7 [1.5, 2.0] | 8608 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.934 [0.89, 0.97] | 0.960 [0.93, 0.98] | 0.947 [0.92, 0.97] | 0.955 [0.93, 0.98] | 286 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.852 [0.79, 0.90] | 0.866 [0.81, 0.92] | 0.859 [0.80, 0.90] | 0.863 [0.80, 0.91] | 258 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.042 [0.02, 0.07] | 0.893 [0.84, 0.93] | 3.6 [1.9, 5.7] | 266 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.990 [0.98, 1.00] | 0.962 [0.93, 0.98] | 0.976 [0.96, 0.99] | 0.968 [0.94, 0.99] | 381 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.990 [0.98, 1.00] | 0.962 [0.93, 0.98] | 0.976 [0.96, 0.99] | 0.968 [0.94, 0.99] | 381 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s2 | 0.044 [0.02, 0.08] | 0.962 [0.93, 0.98] | 0.3 [0.0, 0.8] | 381 / 396 |
