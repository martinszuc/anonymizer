# train-cs-ce-dev

rules+gliner-cs-ce after training (train-cs-ce).

Stage: dev · commit 0211b3728e · 2026-10-14T20:28:00+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-ce @ bc8d080c9a · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.844 [0.74, 0.96] | 0.909 [0.78, 1.00] | 0.875 [0.78, 0.97] | 0.895 [0.78, 0.98] | 20 / 22 |
| email | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-ce | 0.921 [0.89, 0.95] | 0.931 [0.91, 0.95] | 0.926 [0.91, 0.95] | 0.929 [0.91, 0.95] | 488 / 524 |
| phone | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-ce | 0.923 [0.89, 0.95] | 0.919 [0.88, 0.95] | 0.921 [0.89, 0.94] | 0.920 [0.89, 0.94] | 557 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.094 [0.00, 0.22] | 0.136 [0.00, 0.32] | 0.111 [0.00, 0.26] | 0.125 [0.00, 0.28] | 3 / 22 |
| email | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-ce | 0.885 [0.85, 0.92] | 0.897 [0.87, 0.92] | 0.891 [0.87, 0.91] | 0.895 [0.87, 0.92] | 470 / 524 |
| phone | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-ce | 0.852 [0.82, 0.88] | 0.853 [0.81, 0.89] | 0.852 [0.82, 0.88] | 0.853 [0.81, 0.89] | 517 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.414 [0.29, 0.52] | 0.182 [0.04, 0.39] | 1.4 [0.3, 2.6] | 4 / 22 |
| email | rules+gliner-cs-ce | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-ce | 0.053 [0.04, 0.07] | 0.910 [0.89, 0.93] | 3.5 [2.2, 4.7] | 477 / 524 |
| phone | rules+gliner-cs-ce | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-ce | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-ce | 0.113 [0.08, 0.15] | 0.866 [0.83, 0.90] | 4.8 [3.0, 6.7] | 525 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-ce | 0.870 [0.79, 0.94] | 0.880 [0.83, 0.92] | 0.875 [0.83, 0.92] | 0.878 [0.83, 0.92] | 243 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-ce | 0.830 [0.75, 0.91] | 0.833 [0.78, 0.89] | 0.832 [0.78, 0.88] | 0.833 [0.79, 0.88] | 230 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-ce | 0.098 [0.06, 0.13] | 0.862 [0.80, 0.92] | 4.8 [2.0, 8.0] | 238 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.571 [0.40, 0.74] | 1.000 [1.00, 1.00] | 0.727 [0.57, 0.85] | 0.870 [0.77, 0.93] | 27 / 27 |
| birth_number | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-ce | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-ce | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-ce | 0.817 [0.65, 0.97] | 1.000 [1.00, 1.00] | 0.899 [0.79, 0.98] | 0.957 [0.90, 0.99] | 219 / 219 |
| phone | rules+gliner-cs-ce | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-ce | 0.821 [0.71, 0.91] | 0.907 [0.86, 0.95] | 0.862 [0.79, 0.92] | 0.889 [0.84, 0.93] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.490 [0.33, 0.67] | 0.889 [0.72, 1.00] | 0.632 [0.47, 0.79] | 0.764 [0.60, 0.89] | 24 / 27 |
| birth_number | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-ce | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-ce | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-ce | 0.603 [0.45, 0.77] | 0.708 [0.58, 0.83] | 0.651 [0.52, 0.79] | 0.684 [0.56, 0.81] | 155 / 219 |
| phone | rules+gliner-cs-ce | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-ce | 0.680 [0.58, 0.78] | 0.735 [0.67, 0.80] | 0.706 [0.63, 0.79] | 0.723 [0.66, 0.79] | 285 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.0 [2.8, 9.8] | 27 / 27 |
| birth_number | rules+gliner-cs-ce | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-ce | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-ce | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-ce | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-ce | 0.007 [0.00, 0.02] | 0.986 [0.97, 1.00] | 11.2 [5.9, 18.1] | 216 / 219 |
| phone | rules+gliner-cs-ce | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-ce | 0.062 [0.03, 0.10] | 0.915 [0.86, 0.95] | 18.9 [12.4, 26.8] | 355 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.995 [0.99, 1.00] | 0.956 [0.95, 0.96] | 0.975 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2026 / 2119 |
| email | rules+gliner-cs-ce | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-ce | 0.996 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.994 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4313 / 4353 |
| any | rules+gliner-cs-ce | 0.997 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8949 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.853 [0.84, 0.87] | 0.833 [0.82, 0.85] | 0.843 [0.83, 0.86] | 0.837 [0.82, 0.85] | 1766 / 2119 |
| email | rules+gliner-cs-ce | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-ce | 0.984 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.979 [0.97, 0.98] | 4258 / 4353 |
| any | rules+gliner-cs-ce | 0.946 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8520 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.084 [0.07, 0.10] | 0.938 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1988 / 2119 |
| email | rules+gliner-cs-ce | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-ce | 0.007 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4305 / 4353 |
| any | rules+gliner-cs-ce | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.2, 1.7] | 8788 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.992 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.973 [0.97, 0.98] | 0.962 [0.95, 0.97] | 2022 / 2118 |
| email | rules+gliner-cs-ce | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-ce | 0.993 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4304 / 4344 |
| any | rules+gliner-cs-ce | 0.995 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8780 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.834 [0.82, 0.85] | 0.817 [0.80, 0.83] | 0.826 [0.81, 0.84] | 0.821 [0.80, 0.84] | 1731 / 2118 |
| email | rules+gliner-cs-ce | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-ce | 0.965 [0.96, 0.97] | 0.962 [0.95, 0.97] | 0.963 [0.96, 0.97] | 0.963 [0.96, 0.97] | 4179 / 4344 |
| any | rules+gliner-cs-ce | 0.934 [0.93, 0.94] | 0.927 [0.92, 0.93] | 0.930 [0.92, 0.94] | 0.928 [0.92, 0.93] | 8274 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce | 0.094 [0.08, 0.11] | 0.937 [0.93, 0.95] | 1.3 [1.1, 1.5] | 1985 / 2118 |
| email | rules+gliner-cs-ce | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-ce | 0.006 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.5 [0.4, 0.6] | 4289 / 4344 |
| any | rules+gliner-cs-ce | 0.038 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.9 [1.6, 2.2] | 8635 / 8927 |
