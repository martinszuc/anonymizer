# train-recipe-r3-s2k-s2-dev

rules+gliner-recipe-r3-s2k-s2 after training (train-recipe-r3-s2k-s2).

Stage: dev · commit 156b8b704e · 2026-10-21T00:44:01+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r3-s2k-s2 @ e97d625660 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.893 [0.79, 1.00] | 0.864 [0.71, 1.00] | 0.878 [0.78, 0.96] | 0.869 [0.74, 0.98] | 19 / 22 |
| email | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.901 [0.87, 0.93] | 0.941 [0.92, 0.96] | 0.921 [0.90, 0.94] | 0.933 [0.91, 0.95] | 493 / 524 |
| phone | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.908 [0.88, 0.94] | 0.926 [0.89, 0.95] | 0.917 [0.89, 0.94] | 0.922 [0.89, 0.95] | 561 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.179 [0.05, 0.37] | 0.227 [0.07, 0.46] | 0.200 [0.06, 0.40] | 0.215 [0.07, 0.43] | 5 / 22 |
| email | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.867 [0.83, 0.90] | 0.906 [0.88, 0.93] | 0.886 [0.86, 0.91] | 0.898 [0.88, 0.92] | 475 / 524 |
| phone | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.845 [0.81, 0.88] | 0.865 [0.82, 0.90] | 0.855 [0.82, 0.88] | 0.861 [0.82, 0.89] | 524 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.458 [0.32, 0.57] | 0.227 [0.07, 0.46] | 0.7 [0.2, 1.4] | 5 / 22 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.042 [0.03, 0.06] | 0.920 [0.90, 0.94] | 4.2 [2.9, 5.5] | 482 / 524 |
| phone | rules+gliner-recipe-r3-s2k-s2 | 0.328 [0.09, 0.64] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.110 [0.07, 0.15] | 0.876 [0.83, 0.91] | 4.8 [3.5, 6.4] | 531 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k-s2 | 0.845 [0.75, 0.92] | 0.913 [0.87, 0.95] | 0.877 [0.82, 0.92] | 0.898 [0.86, 0.93] | 252 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k-s2 | 0.807 [0.72, 0.88] | 0.866 [0.82, 0.91] | 0.836 [0.78, 0.88] | 0.854 [0.81, 0.89] | 239 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k-s2 | 0.070 [0.04, 0.10] | 0.895 [0.84, 0.94] | 5.7 [2.6, 9.7] | 247 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.538 [0.40, 0.69] | 1.000 [1.00, 1.00] | 0.700 [0.57, 0.81] | 0.854 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.813 [0.65, 0.96] | 0.991 [0.98, 1.00] | 0.893 [0.78, 0.98] | 0.949 [0.89, 0.99] | 217 / 219 |
| phone | rules+gliner-recipe-r3-s2k-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.815 [0.70, 0.91] | 0.905 [0.86, 0.94] | 0.858 [0.79, 0.91] | 0.885 [0.84, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.423 [0.29, 0.59] | 0.815 [0.65, 0.97] | 0.557 [0.41, 0.72] | 0.688 [0.54, 0.83] | 22 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.607 [0.45, 0.77] | 0.712 [0.60, 0.82] | 0.655 [0.53, 0.78] | 0.688 [0.58, 0.80] | 156 / 219 |
| phone | rules+gliner-recipe-r3-s2k-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.673 [0.58, 0.77] | 0.732 [0.67, 0.80] | 0.701 [0.63, 0.77] | 0.719 [0.66, 0.78] | 284 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.2 [2.9, 10.0] | 26 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r3-s2k-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.010 [0.00, 0.02] | 0.977 [0.95, 1.00] | 10.9 [5.7, 17.6] | 214 / 219 |
| phone | rules+gliner-recipe-r3-s2k-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.066 [0.04, 0.10] | 0.907 [0.85, 0.95] | 18.8 [12.6, 25.9] | 352 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.996 [0.99, 1.00] | 0.953 [0.94, 0.96] | 0.974 [0.97, 0.98] | 0.962 [0.95, 0.97] | 2020 / 2119 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.995 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4307 / 4353 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.996 [1.00, 1.00] | 0.983 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8938 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.849 [0.83, 0.86] | 0.828 [0.81, 0.84] | 0.838 [0.82, 0.85] | 0.832 [0.82, 0.85] | 1754 / 2119 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.983 [0.98, 0.99] | 0.977 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4252 / 4353 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.944 [0.94, 0.95] | 0.935 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.936 [0.93, 0.94] | 8502 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.086 [0.07, 0.10] | 0.933 [0.92, 0.94] | 1.0 [0.9, 1.2] | 1978 / 2119 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.008 [0.01, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4298 / 4353 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.038 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8771 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.993 [0.99, 1.00] | 0.953 [0.94, 0.96] | 0.973 [0.97, 0.98] | 0.961 [0.95, 0.97] | 2019 / 2118 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.995 [0.99, 1.00] | 0.989 [0.98, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4294 / 4344 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.996 [0.99, 1.00] | 0.982 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8766 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.837 [0.82, 0.85] | 0.819 [0.80, 0.84] | 0.828 [0.81, 0.84] | 0.822 [0.80, 0.84] | 1734 / 2118 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.977 [0.97, 0.98] | 0.969 [0.96, 0.97] | 0.973 [0.97, 0.98] | 0.971 [0.97, 0.98] | 4211 / 4344 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.940 [0.93, 0.95] | 0.931 [0.92, 0.94] | 0.935 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8308 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s2 | 0.096 [0.08, 0.11] | 0.936 [0.92, 0.95] | 1.2 [1.0, 1.4] | 1982 / 2118 |
| email | rules+gliner-recipe-r3-s2k-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r3-s2k-s2 | 0.009 [0.01, 0.01] | 0.985 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4279 / 4344 |
| any | rules+gliner-recipe-r3-s2k-s2 | 0.040 [0.03, 0.05] | 0.966 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8622 / 8927 |
