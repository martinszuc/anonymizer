# train-cs-sk-ce-more-s1-dev

rules+gliner-cs-sk-ce-more-s1 after training (train-cs-sk-ce-more-s1).

Stage: dev · commit 0b2364ff37 · 2026-10-21T22:39:18+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-ce-more-s1 @ 7779c13a74 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.880 [0.77, 1.00] | 0.818 [0.64, 0.95] | 0.848 [0.73, 0.94] | 0.830 [0.68, 0.95] | 18 / 22 |
| email | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.892 [0.85, 0.92] | 0.943 [0.92, 0.96] | 0.917 [0.89, 0.94] | 0.932 [0.91, 0.95] | 494 / 524 |
| phone | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.899 [0.86, 0.93] | 0.921 [0.89, 0.95] | 0.910 [0.88, 0.93] | 0.916 [0.89, 0.94] | 558 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.120 [0.00, 0.29] | 0.136 [0.00, 0.35] | 0.128 [0.00, 0.31] | 0.133 [0.00, 0.33] | 3 / 22 |
| email | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.854 [0.82, 0.89] | 0.905 [0.88, 0.93] | 0.879 [0.85, 0.90] | 0.894 [0.87, 0.92] | 474 / 524 |
| phone | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.835 [0.79, 0.87] | 0.860 [0.82, 0.89] | 0.847 [0.81, 0.88] | 0.855 [0.82, 0.89] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.494 [0.34, 0.62] | 0.182 [0.04, 0.44] | 0.7 [0.2, 1.4] | 4 / 22 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.049 [0.03, 0.07] | 0.914 [0.89, 0.93] | 4.7 [3.3, 6.2] | 479 / 524 |
| phone | rules+gliner-cs-sk-ce-more-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.114 [0.07, 0.15] | 0.870 [0.83, 0.90] | 5.2 [3.7, 7.0] | 527 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.850 [0.76, 0.93] | 0.949 [0.91, 0.98] | 0.897 [0.84, 0.94] | 0.927 [0.89, 0.96] | 262 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.817 [0.73, 0.89] | 0.906 [0.85, 0.95] | 0.859 [0.80, 0.91] | 0.886 [0.84, 0.93] | 250 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.045 [0.01, 0.09] | 0.931 [0.88, 0.97] | 5.6 [2.4, 9.5] | 257 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.549 [0.41, 0.70] | 1.000 [1.00, 1.00] | 0.709 [0.58, 0.82] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.814 [0.64, 0.96] | 0.995 [0.98, 1.00] | 0.896 [0.78, 0.98] | 0.953 [0.90, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-ce-more-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.815 [0.70, 0.90] | 0.907 [0.86, 0.95] | 0.859 [0.79, 0.91] | 0.887 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.431 [0.29, 0.59] | 0.815 [0.62, 0.96] | 0.564 [0.40, 0.71] | 0.692 [0.51, 0.84] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.612 [0.47, 0.77] | 0.722 [0.61, 0.83] | 0.662 [0.54, 0.79] | 0.697 [0.58, 0.81] | 158 / 219 |
| phone | rules+gliner-cs-sk-ce-more-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.678 [0.58, 0.77] | 0.737 [0.67, 0.80] | 0.706 [0.64, 0.77] | 0.724 [0.66, 0.78] | 286 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.021 [0.00, 0.07] | 0.963 [0.87, 1.00] | 6.1 [3.0, 10.0] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-ce-more-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 10.6 [5.7, 17.5] | 215 / 219 |
| phone | rules+gliner-cs-sk-ce-more-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.065 [0.03, 0.10] | 0.910 [0.86, 0.95] | 18.5 [12.3, 26.5] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.995 [0.99, 1.00] | 0.950 [0.94, 0.96] | 0.972 [0.97, 0.98] | 0.959 [0.95, 0.97] | 2014 / 2119 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.996 [0.99, 1.00] | 0.983 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.986 [0.98, 0.99] | 4279 / 4353 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.997 [1.00, 1.00] | 0.979 [0.98, 0.98] | 0.988 [0.99, 0.99] | 0.982 [0.98, 0.98] | 8904 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.842 [0.82, 0.86] | 0.820 [0.80, 0.84] | 0.831 [0.81, 0.85] | 0.824 [0.81, 0.84] | 1737 / 2119 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.984 [0.98, 0.99] | 0.972 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4229 / 4353 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.943 [0.94, 0.95] | 0.930 [0.92, 0.94] | 0.937 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8463 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.088 [0.07, 0.10] | 0.926 [0.91, 0.94] | 1.1 [0.9, 1.3] | 1962 / 2119 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.013 [0.01, 0.02] | 0.981 [0.98, 0.99] | 0.2 [0.2, 0.3] | 4269 / 4353 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.040 [0.03, 0.05] | 0.959 [0.95, 0.96] | 1.5 [1.2, 1.7] | 8726 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.992 [0.99, 1.00] | 0.948 [0.94, 0.96] | 0.969 [0.96, 0.97] | 0.956 [0.95, 0.96] | 2007 / 2118 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 4279 / 4344 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.996 [0.99, 1.00] | 0.979 [0.98, 0.98] | 0.988 [0.99, 0.99] | 0.983 [0.98, 0.98] | 8741 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.834 [0.82, 0.85] | 0.813 [0.79, 0.83] | 0.823 [0.81, 0.84] | 0.817 [0.80, 0.83] | 1721 / 2118 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 0.971 [0.96, 0.98] | 0.967 [0.96, 0.97] | 4193 / 4344 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.940 [0.93, 0.94] | 0.927 [0.92, 0.93] | 0.933 [0.93, 0.94] | 0.930 [0.92, 0.94] | 8279 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more-s1 | 0.098 [0.08, 0.12] | 0.929 [0.92, 0.94] | 1.2 [1.0, 1.4] | 1968 / 2118 |
| email | rules+gliner-cs-sk-ce-more-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-ce-more-s1 | 0.011 [0.01, 0.01] | 0.981 [0.98, 0.99] | 0.3 [0.2, 0.5] | 4262 / 4344 |
| any | rules+gliner-cs-sk-ce-more-s1 | 0.042 [0.04, 0.05] | 0.962 [0.96, 0.97] | 1.6 [1.4, 1.9] | 8591 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.931 [0.88, 0.97] | 0.960 [0.93, 0.98] | 0.945 [0.91, 0.97] | 0.954 [0.93, 0.97] | 286 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.843 [0.78, 0.90] | 0.866 [0.81, 0.91] | 0.854 [0.80, 0.90] | 0.861 [0.81, 0.91] | 258 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.041 [0.02, 0.06] | 0.889 [0.84, 0.93] | 3.8 [1.9, 5.8] | 265 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.990 [0.98, 1.00] | 0.960 [0.93, 0.98] | 0.974 [0.96, 0.99] | 0.965 [0.94, 0.98] | 380 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.990 [0.98, 1.00] | 0.960 [0.93, 0.98] | 0.974 [0.96, 0.99] | 0.965 [0.94, 0.98] | 380 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more-s1 | 0.046 [0.02, 0.08] | 0.960 [0.93, 0.98] | 0.3 [0.0, 0.8] | 380 / 396 |
