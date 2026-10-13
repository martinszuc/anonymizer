# train-cs-sk-focal-s2-dev

rules+gliner-cs-sk-focal-s2 after training (train-cs-sk-focal-s2).

Stage: dev · commit e44e907302 · 2026-10-12T07:51:00+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-s2 @ de9cfe79fc · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.829 [0.72, 0.92] | 1.000 [1.00, 1.00] | 0.907 [0.84, 0.96] | 0.961 [0.93, 0.98] | 22 / 22 |
| email | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-s2 | 0.870 [0.83, 0.91] | 0.943 [0.92, 0.96] | 0.905 [0.88, 0.93] | 0.927 [0.90, 0.95] | 494 / 524 |
| phone | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-s2 | 0.876 [0.84, 0.91] | 0.937 [0.91, 0.96] | 0.906 [0.88, 0.93] | 0.924 [0.90, 0.95] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.073 [0.00, 0.18] | 0.136 [0.00, 0.33] | 0.095 [0.00, 0.24] | 0.116 [0.00, 0.28] | 3 / 22 |
| email | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-s2 | 0.835 [0.79, 0.87] | 0.906 [0.88, 0.93] | 0.869 [0.84, 0.89] | 0.891 [0.87, 0.91] | 475 / 524 |
| phone | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-s2 | 0.798 [0.75, 0.84] | 0.861 [0.82, 0.90] | 0.829 [0.79, 0.86] | 0.848 [0.81, 0.88] | 522 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.353 [0.24, 0.44] | 0.227 [0.07, 0.44] | 1.8 [0.6, 3.2] | 5 / 22 |
| email | rules+gliner-cs-sk-focal-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-s2 | 0.038 [0.03, 0.05] | 0.926 [0.90, 0.95] | 5.8 [4.2, 7.5] | 485 / 524 |
| phone | rules+gliner-cs-sk-focal-s2 | 0.318 [0.09, 0.61] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-s2 | 0.095 [0.07, 0.12] | 0.881 [0.84, 0.91] | 7.4 [5.3, 10.0] | 534 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-s2 | 0.795 [0.71, 0.87] | 0.949 [0.91, 0.98] | 0.865 [0.81, 0.91] | 0.914 [0.88, 0.94] | 262 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-s2 | 0.761 [0.68, 0.83] | 0.902 [0.86, 0.94] | 0.826 [0.77, 0.87] | 0.870 [0.83, 0.91] | 249 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-s2 | 0.039 [0.02, 0.07] | 0.931 [0.89, 0.97] | 8.6 [5.0, 13.1] | 257 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.528 [0.38, 0.68] | 1.000 [1.00, 1.00] | 0.691 [0.56, 0.81] | 0.849 [0.76, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-s2 | 0.760 [0.61, 0.93] | 0.995 [0.99, 1.00] | 0.862 [0.76, 0.96] | 0.937 [0.88, 0.98] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-s2 | 0.782 [0.68, 0.88] | 0.907 [0.86, 0.94] | 0.840 [0.77, 0.90] | 0.879 [0.83, 0.91] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.434 [0.29, 0.61] | 0.852 [0.69, 1.00] | 0.575 [0.41, 0.74] | 0.714 [0.56, 0.86] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-s2 | 0.560 [0.41, 0.74] | 0.703 [0.58, 0.83] | 0.624 [0.49, 0.77] | 0.669 [0.54, 0.80] | 154 / 219 |
| phone | rules+gliner-cs-sk-focal-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-s2 | 0.642 [0.54, 0.76] | 0.729 [0.66, 0.80] | 0.683 [0.60, 0.77] | 0.710 [0.64, 0.78] | 283 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.8 [3.0, 11.4] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-s2 | 0.007 [0.00, 0.02] | 0.986 [0.97, 1.00] | 13.9 [6.5, 23.6] | 216 / 219 |
| phone | rules+gliner-cs-sk-focal-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-s2 | 0.062 [0.03, 0.10] | 0.915 [0.86, 0.95] | 22.4 [14.1, 31.8] | 355 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.992 [0.99, 1.00] | 0.959 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.966 [0.96, 0.97] | 2033 / 2119 |
| email | rules+gliner-cs-sk-focal-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-s2 | 0.993 [0.99, 1.00] | 0.993 [0.99, 1.00] | 0.993 [0.99, 0.99] | 0.993 [0.99, 0.99] | 4321 / 4353 |
| any | rules+gliner-cs-sk-focal-s2 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8963 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.846 [0.83, 0.86] | 0.833 [0.82, 0.85] | 0.839 [0.82, 0.85] | 0.835 [0.82, 0.85] | 1764 / 2119 |
| email | rules+gliner-cs-sk-focal-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-s2 | 0.981 [0.98, 0.99] | 0.980 [0.97, 0.98] | 0.981 [0.98, 0.98] | 0.980 [0.97, 0.98] | 4266 / 4353 |
| any | rules+gliner-cs-sk-focal-s2 | 0.942 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.940 [0.93, 0.94] | 0.938 [0.93, 0.94] | 8525 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.081 [0.07, 0.10] | 0.939 [0.93, 0.95] | 1.1 [0.9, 1.4] | 1989 / 2119 |
| email | rules+gliner-cs-sk-focal-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-s2 | 0.006 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.4 [0.3, 0.5] | 4313 / 4353 |
| any | rules+gliner-cs-sk-focal-s2 | 0.035 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8797 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.989 [0.98, 0.99] | 0.964 [0.96, 0.97] | 0.976 [0.97, 0.98] | 0.969 [0.96, 0.98] | 2041 / 2118 |
| email | rules+gliner-cs-sk-focal-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-s2 | 0.992 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4307 / 4344 |
| any | rules+gliner-cs-sk-focal-s2 | 0.994 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8802 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.831 [0.81, 0.85] | 0.825 [0.81, 0.84] | 0.828 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1748 / 2118 |
| email | rules+gliner-cs-sk-focal-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-s2 | 0.974 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4227 / 4344 |
| any | rules+gliner-cs-sk-focal-s2 | 0.937 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8338 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s2 | 0.090 [0.07, 0.11] | 0.946 [0.94, 0.96] | 1.3 [1.1, 1.5] | 2003 / 2118 |
| email | rules+gliner-cs-sk-focal-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-s2 | 0.006 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.4 [0.3, 0.5] | 4295 / 4344 |
| any | rules+gliner-cs-sk-focal-s2 | 0.037 [0.03, 0.04] | 0.970 [0.97, 0.97] | 1.8 [1.5, 2.0] | 8659 / 8927 |
