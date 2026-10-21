# train-recipe-r10-s2k-s2-dev

rules+gliner-recipe-r10-s2k-s2 after training (train-recipe-r10-s2k-s2).

Stage: dev · commit 156b8b704e · 2026-10-21T01:06:37+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r10-s2k-s2 @ 525d842635 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.875 [0.76, 1.00] | 0.818 [0.65, 0.95] | 0.846 [0.73, 0.94] | 0.829 [0.68, 0.94] | 18 / 22 |
| email | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.903 [0.87, 0.93] | 0.949 [0.93, 0.97] | 0.925 [0.90, 0.94] | 0.939 [0.92, 0.95] | 497 / 524 |
| phone | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.911 [0.88, 0.94] | 0.929 [0.90, 0.96] | 0.920 [0.90, 0.94] | 0.925 [0.90, 0.95] | 563 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.208 [0.06, 0.41] | 0.227 [0.07, 0.46] | 0.217 [0.07, 0.43] | 0.223 [0.07, 0.44] | 5 / 22 |
| email | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.869 [0.83, 0.90] | 0.910 [0.89, 0.93] | 0.889 [0.86, 0.91] | 0.902 [0.88, 0.92] | 477 / 524 |
| phone | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.853 [0.81, 0.89] | 0.868 [0.83, 0.90] | 0.860 [0.83, 0.89] | 0.865 [0.83, 0.90] | 526 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.471 [0.35, 0.58] | 0.273 [0.10, 0.50] | 0.7 [0.2, 1.4] | 6 / 22 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.041 [0.03, 0.05] | 0.924 [0.90, 0.94] | 4.2 [2.9, 5.7] | 484 / 524 |
| phone | rules+gliner-recipe-r10-s2k-s2 | 0.328 [0.09, 0.64] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.110 [0.07, 0.15] | 0.881 [0.84, 0.91] | 4.8 [3.4, 6.6] | 534 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k-s2 | 0.838 [0.75, 0.91] | 0.920 [0.88, 0.96] | 0.877 [0.82, 0.92] | 0.902 [0.86, 0.94] | 254 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k-s2 | 0.805 [0.71, 0.88] | 0.880 [0.83, 0.93] | 0.841 [0.78, 0.89] | 0.864 [0.82, 0.91] | 243 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k-s2 | 0.061 [0.03, 0.09] | 0.902 [0.85, 0.95] | 6.0 [3.0, 9.8] | 249 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.538 [0.40, 0.69] | 1.000 [1.00, 1.00] | 0.700 [0.57, 0.82] | 0.854 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.792 [0.62, 0.95] | 0.927 [0.80, 1.00] | 0.854 [0.73, 0.96] | 0.896 [0.79, 0.98] | 203 / 219 |
| phone | rules+gliner-recipe-r10-s2k-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.805 [0.70, 0.90] | 0.869 [0.80, 0.92] | 0.836 [0.77, 0.89] | 0.855 [0.80, 0.90] | 337 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.423 [0.29, 0.59] | 0.815 [0.65, 0.97] | 0.557 [0.40, 0.72] | 0.688 [0.54, 0.83] | 22 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.629 [0.48, 0.78] | 0.703 [0.59, 0.82] | 0.664 [0.55, 0.77] | 0.687 [0.59, 0.79] | 154 / 219 |
| phone | rules+gliner-recipe-r10-s2k-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.688 [0.59, 0.78] | 0.727 [0.67, 0.79] | 0.707 [0.64, 0.77] | 0.719 [0.66, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.4 [3.2, 10.3] | 26 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r10-s2k-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.057 [0.00, 0.15] | 0.913 [0.79, 0.99] | 10.0 [5.3, 16.5] | 200 / 219 |
| phone | rules+gliner-recipe-r10-s2k-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.086 [0.05, 0.13] | 0.871 [0.80, 0.93] | 18.2 [11.7, 25.7] | 338 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.991 [0.99, 1.00] | 0.950 [0.94, 0.96] | 0.970 [0.96, 0.98] | 0.958 [0.95, 0.97] | 2013 / 2119 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.994 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.987 [0.98, 0.99] | 4286 / 4353 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.995 [0.99, 1.00] | 0.980 [0.98, 0.98] | 0.987 [0.99, 0.99] | 0.983 [0.98, 0.99] | 8911 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.839 [0.82, 0.85] | 0.818 [0.80, 0.83] | 0.829 [0.81, 0.84] | 0.822 [0.81, 0.84] | 1734 / 2119 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.981 [0.98, 0.99] | 0.972 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4231 / 4353 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.941 [0.94, 0.95] | 0.930 [0.92, 0.94] | 0.936 [0.93, 0.94] | 0.932 [0.93, 0.94] | 8461 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.090 [0.08, 0.11] | 0.926 [0.91, 0.94] | 1.2 [1.0, 1.4] | 1962 / 2119 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.012 [0.01, 0.02] | 0.982 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4274 / 4353 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.041 [0.04, 0.05] | 0.960 [0.96, 0.96] | 1.5 [1.3, 1.8] | 8731 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.983 [0.98, 0.99] | 0.947 [0.94, 0.96] | 0.965 [0.96, 0.97] | 0.954 [0.95, 0.96] | 2006 / 2118 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.994 [0.99, 1.00] | 0.987 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 4286 / 4344 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.994 [0.99, 1.00] | 0.980 [0.98, 0.98] | 0.987 [0.99, 0.99] | 0.983 [0.98, 0.99] | 8750 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.819 [0.80, 0.84] | 0.803 [0.78, 0.82] | 0.811 [0.79, 0.83] | 0.806 [0.79, 0.82] | 1701 / 2118 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.973 [0.97, 0.98] | 0.966 [0.96, 0.97] | 0.970 [0.96, 0.97] | 0.967 [0.96, 0.97] | 4195 / 4344 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.935 [0.93, 0.94] | 0.925 [0.92, 0.93] | 0.930 [0.92, 0.94] | 0.927 [0.92, 0.93] | 8261 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s2 | 0.102 [0.08, 0.12] | 0.926 [0.91, 0.94] | 1.4 [1.2, 1.6] | 1961 / 2118 |
| email | rules+gliner-recipe-r10-s2k-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r10-s2k-s2 | 0.010 [0.01, 0.01] | 0.983 [0.98, 0.99] | 0.3 [0.2, 0.5] | 4268 / 4344 |
| any | rules+gliner-recipe-r10-s2k-s2 | 0.043 [0.04, 0.05] | 0.962 [0.96, 0.97] | 1.8 [1.5, 2.1] | 8590 / 8927 |
