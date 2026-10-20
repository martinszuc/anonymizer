# train-recipe-r10-s2k-dev

rules+gliner-recipe-r10-s2k after training (train-recipe-r10-s2k).

Stage: dev · commit 94ed4acc40 · 2026-10-15T22:04:55+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r10-s2k @ 9724a7e1e7 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.846 [0.72, 0.96] | 0.818 [0.65, 0.95] | 0.832 [0.70, 0.94] | 0.824 [0.67, 0.94] | 18 / 22 |
| email | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k | 0.910 [0.88, 0.94] | 0.947 [0.92, 0.97] | 0.928 [0.91, 0.95] | 0.939 [0.92, 0.96] | 496 / 524 |
| phone | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k | 0.914 [0.88, 0.94] | 0.926 [0.89, 0.96] | 0.920 [0.89, 0.94] | 0.923 [0.89, 0.95] | 561 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.192 [0.06, 0.40] | 0.227 [0.06, 0.45] | 0.208 [0.06, 0.42] | 0.219 [0.06, 0.44] | 5 / 22 |
| email | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k | 0.872 [0.84, 0.90] | 0.906 [0.88, 0.93] | 0.889 [0.86, 0.91] | 0.899 [0.87, 0.92] | 475 / 524 |
| phone | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k | 0.852 [0.81, 0.89] | 0.865 [0.82, 0.90] | 0.858 [0.82, 0.89] | 0.862 [0.82, 0.89] | 524 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.480 [0.34, 0.63] | 0.273 [0.09, 0.52] | 1.0 [0.3, 1.7] | 6 / 22 |
| email | rules+gliner-recipe-r10-s2k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k | 0.042 [0.03, 0.06] | 0.920 [0.90, 0.94] | 3.7 [2.4, 5.1] | 482 / 524 |
| phone | rules+gliner-recipe-r10-s2k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k | 0.109 [0.07, 0.15] | 0.878 [0.84, 0.91] | 4.6 [3.1, 6.3] | 532 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k | 0.838 [0.76, 0.91] | 0.927 [0.88, 0.96] | 0.881 [0.83, 0.93] | 0.908 [0.87, 0.94] | 256 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k | 0.809 [0.72, 0.89] | 0.888 [0.84, 0.93] | 0.846 [0.79, 0.89] | 0.871 [0.83, 0.91] | 245 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k | 0.055 [0.03, 0.08] | 0.909 [0.86, 0.95] | 6.0 [2.9, 9.7] | 251 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k | 0.800 [0.63, 0.95] | 0.986 [0.97, 1.00] | 0.883 [0.77, 0.97] | 0.942 [0.89, 0.98] | 216 / 219 |
| phone | rules+gliner-recipe-r10-s2k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k | 0.814 [0.71, 0.91] | 0.902 [0.85, 0.94] | 0.856 [0.79, 0.91] | 0.883 [0.84, 0.92] | 350 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.431 [0.29, 0.59] | 0.815 [0.64, 0.96] | 0.564 [0.41, 0.71] | 0.692 [0.52, 0.83] | 22 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k | 0.589 [0.44, 0.76] | 0.699 [0.57, 0.82] | 0.639 [0.51, 0.78] | 0.673 [0.55, 0.80] | 153 / 219 |
| phone | rules+gliner-recipe-r10-s2k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k | 0.663 [0.56, 0.77] | 0.724 [0.66, 0.79] | 0.692 [0.61, 0.77] | 0.711 [0.65, 0.78] | 281 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.1 [3.0, 10.0] | 26 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r10-s2k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k | 0.012 [0.00, 0.03] | 0.977 [0.95, 1.00] | 11.2 [5.9, 18.1] | 214 / 219 |
| phone | rules+gliner-recipe-r10-s2k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k | 0.067 [0.04, 0.11] | 0.907 [0.85, 0.95] | 19.1 [12.6, 26.8] | 352 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.991 [0.99, 1.00] | 0.948 [0.94, 0.96] | 0.969 [0.96, 0.97] | 0.956 [0.95, 0.96] | 2008 / 2119 |
| email | rules+gliner-recipe-r10-s2k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r10-s2k | 0.994 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.986 [0.98, 0.99] | 4281 / 4353 |
| any | rules+gliner-recipe-r10-s2k | 0.995 [0.99, 1.00] | 0.979 [0.98, 0.98] | 0.987 [0.98, 0.99] | 0.982 [0.98, 0.98] | 8901 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.840 [0.82, 0.86] | 0.817 [0.80, 0.83] | 0.828 [0.81, 0.84] | 0.822 [0.80, 0.84] | 1731 / 2119 |
| email | rules+gliner-recipe-r10-s2k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s2k | 0.981 [0.98, 0.99] | 0.971 [0.96, 0.98] | 0.976 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4226 / 4353 |
| any | rules+gliner-recipe-r10-s2k | 0.942 [0.94, 0.95] | 0.929 [0.92, 0.93] | 0.935 [0.93, 0.94] | 0.932 [0.93, 0.94] | 8454 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.090 [0.07, 0.11] | 0.925 [0.91, 0.94] | 1.1 [0.9, 1.3] | 1960 / 2119 |
| email | rules+gliner-recipe-r10-s2k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s2k | 0.014 [0.01, 0.02] | 0.981 [0.98, 0.98] | 0.3 [0.2, 0.4] | 4270 / 4353 |
| any | rules+gliner-recipe-r10-s2k | 0.042 [0.04, 0.05] | 0.959 [0.95, 0.96] | 1.5 [1.3, 1.8] | 8725 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.983 [0.98, 0.99] | 0.950 [0.94, 0.96] | 0.966 [0.96, 0.97] | 0.957 [0.95, 0.96] | 2013 / 2118 |
| email | rules+gliner-recipe-r10-s2k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r10-s2k | 0.993 [0.99, 1.00] | 0.987 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 4288 / 4344 |
| any | rules+gliner-recipe-r10-s2k | 0.993 [0.99, 1.00] | 0.981 [0.98, 0.98] | 0.987 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8759 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.821 [0.80, 0.84] | 0.808 [0.79, 0.82] | 0.814 [0.80, 0.83] | 0.810 [0.79, 0.83] | 1711 / 2118 |
| email | rules+gliner-recipe-r10-s2k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r10-s2k | 0.973 [0.97, 0.98] | 0.967 [0.96, 0.97] | 0.970 [0.96, 0.97] | 0.968 [0.96, 0.97] | 4199 / 4344 |
| any | rules+gliner-recipe-r10-s2k | 0.935 [0.93, 0.94] | 0.927 [0.92, 0.93] | 0.931 [0.93, 0.94] | 0.928 [0.92, 0.93] | 8275 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k | 0.097 [0.08, 0.12] | 0.931 [0.92, 0.94] | 1.4 [1.2, 1.6] | 1971 / 2118 |
| email | rules+gliner-recipe-r10-s2k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r10-s2k | 0.010 [0.01, 0.01] | 0.983 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4272 / 4344 |
| any | rules+gliner-recipe-r10-s2k | 0.041 [0.03, 0.05] | 0.964 [0.96, 0.97] | 1.8 [1.6, 2.1] | 8604 / 8927 |
