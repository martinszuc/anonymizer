# train-cs-sk-weighted-s2-dev

rules+gliner-cs-sk-weighted-s2 after training (train-cs-sk-weighted-s2).

Stage: dev · commit e44e907302 · 2026-10-12T09:19:49+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-weighted-s2 @ c0ac251b10 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.842 [0.74, 0.94] | 1.000 [1.00, 1.00] | 0.914 [0.85, 0.97] | 0.964 [0.93, 0.99] | 22 / 22 |
| email | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.901 [0.87, 0.93] | 0.943 [0.92, 0.96] | 0.922 [0.90, 0.94] | 0.934 [0.91, 0.95] | 494 / 524 |
| phone | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.905 [0.87, 0.93] | 0.937 [0.91, 0.96] | 0.921 [0.90, 0.94] | 0.931 [0.90, 0.95] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.079 [0.00, 0.19] | 0.136 [0.00, 0.33] | 0.100 [0.00, 0.24] | 0.119 [0.00, 0.29] | 3 / 22 |
| email | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.863 [0.83, 0.89] | 0.903 [0.88, 0.93] | 0.882 [0.86, 0.90] | 0.894 [0.87, 0.92] | 473 / 524 |
| phone | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.825 [0.78, 0.86] | 0.858 [0.81, 0.89] | 0.841 [0.80, 0.87] | 0.851 [0.81, 0.88] | 520 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.365 [0.26, 0.45] | 0.227 [0.07, 0.44] | 1.3 [0.4, 2.3] | 5 / 22 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.038 [0.03, 0.05] | 0.926 [0.90, 0.95] | 4.4 [3.0, 5.9] | 485 / 524 |
| phone | rules+gliner-cs-sk-weighted-s2 | 0.318 [0.09, 0.61] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.097 [0.07, 0.13] | 0.881 [0.84, 0.91] | 5.6 [3.9, 7.7] | 534 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-s2 | 0.842 [0.76, 0.91] | 0.931 [0.90, 0.96] | 0.884 [0.83, 0.92] | 0.912 [0.88, 0.94] | 257 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-s2 | 0.805 [0.72, 0.87] | 0.884 [0.84, 0.93] | 0.843 [0.79, 0.89] | 0.867 [0.82, 0.91] | 244 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-s2 | 0.055 [0.03, 0.08] | 0.913 [0.87, 0.95] | 6.0 [3.2, 9.7] | 252 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.528 [0.38, 0.68] | 1.000 [1.00, 1.00] | 0.691 [0.56, 0.81] | 0.849 [0.76, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.775 [0.62, 0.95] | 0.995 [0.99, 1.00] | 0.871 [0.76, 0.97] | 0.942 [0.89, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-weighted-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.787 [0.68, 0.89] | 0.907 [0.86, 0.94] | 0.843 [0.78, 0.90] | 0.880 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.434 [0.29, 0.61] | 0.852 [0.69, 1.00] | 0.575 [0.41, 0.74] | 0.714 [0.56, 0.86] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.565 [0.41, 0.76] | 0.699 [0.57, 0.82] | 0.625 [0.49, 0.77] | 0.667 [0.54, 0.80] | 153 / 219 |
| phone | rules+gliner-cs-sk-weighted-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.645 [0.54, 0.76] | 0.727 [0.66, 0.80] | 0.684 [0.60, 0.77] | 0.709 [0.64, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.8 [3.0, 11.4] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-weighted-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 13.7 [6.2, 23.5] | 215 / 219 |
| phone | rules+gliner-cs-sk-weighted-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 22.2 [14.0, 31.5] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.994 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2030 / 2119 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.994 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.993 [0.99, 0.99] | 4320 / 4353 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.996 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8959 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.847 [0.83, 0.86] | 0.832 [0.81, 0.85] | 0.839 [0.82, 0.85] | 0.835 [0.82, 0.85] | 1762 / 2119 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.983 [0.98, 0.99] | 0.981 [0.97, 0.99] | 0.982 [0.98, 0.99] | 0.981 [0.98, 0.99] | 4268 / 4353 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.944 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.940 [0.94, 0.95] | 0.939 [0.93, 0.94] | 8526 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.082 [0.07, 0.10] | 0.937 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1986 / 2119 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.006 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4312 / 4353 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.036 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8793 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.992 [0.99, 1.00] | 0.962 [0.95, 0.97] | 0.977 [0.97, 0.98] | 0.968 [0.96, 0.97] | 2037 / 2118 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.995 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.994 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4308 / 4344 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.996 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8799 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.836 [0.82, 0.85] | 0.826 [0.81, 0.84] | 0.831 [0.81, 0.85] | 0.828 [0.81, 0.84] | 1750 / 2118 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.977 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4228 / 4344 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.940 [0.93, 0.95] | 0.934 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8341 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s2 | 0.090 [0.07, 0.11] | 0.944 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1999 / 2118 |
| email | rules+gliner-cs-sk-weighted-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-weighted-s2 | 0.006 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4295 / 4344 |
| any | rules+gliner-cs-sk-weighted-s2 | 0.037 [0.03, 0.04] | 0.970 [0.97, 0.97] | 1.6 [1.3, 1.8] | 8655 / 8927 |
