# train-recipe-r5-s2k-s2-dev

rules+gliner-recipe-r5-s2k-s2 after training (train-recipe-r5-s2k-s2).

Stage: dev · commit 156b8b704e · 2026-10-21T00:52:23+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r5-s2k-s2 @ 2418d395bf · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.833 [0.69, 0.96] | 0.773 [0.60, 0.92] | 0.802 [0.67, 0.92] | 0.784 [0.63, 0.92] | 17 / 22 |
| email | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.919 [0.89, 0.95] | 0.939 [0.92, 0.96] | 0.929 [0.91, 0.95] | 0.935 [0.91, 0.95] | 492 / 524 |
| phone | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.922 [0.89, 0.95] | 0.919 [0.88, 0.95] | 0.920 [0.89, 0.94] | 0.920 [0.89, 0.94] | 557 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.208 [0.06, 0.42] | 0.227 [0.07, 0.46] | 0.217 [0.07, 0.43] | 0.223 [0.07, 0.44] | 5 / 22 |
| email | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.884 [0.85, 0.92] | 0.901 [0.87, 0.93] | 0.892 [0.87, 0.92] | 0.897 [0.87, 0.92] | 472 / 524 |
| phone | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.865 [0.83, 0.90] | 0.860 [0.82, 0.90] | 0.863 [0.83, 0.89] | 0.861 [0.82, 0.89] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.516 [0.37, 0.65] | 0.227 [0.07, 0.46] | 1.0 [0.3, 1.8] | 5 / 22 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.048 [0.03, 0.06] | 0.916 [0.89, 0.94] | 3.4 [2.2, 4.8] | 480 / 524 |
| phone | rules+gliner-recipe-r5-s2k-s2 | 0.328 [0.09, 0.64] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r5-s2k-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.119 [0.08, 0.16] | 0.873 [0.83, 0.91] | 4.3 [2.9, 6.2] | 529 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s2k-s2 | 0.826 [0.74, 0.90] | 0.920 [0.88, 0.96] | 0.871 [0.81, 0.91] | 0.900 [0.86, 0.93] | 254 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s2k-s2 | 0.790 [0.71, 0.86] | 0.873 [0.82, 0.92] | 0.830 [0.77, 0.88] | 0.855 [0.81, 0.90] | 241 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s2k-s2 | 0.063 [0.04, 0.09] | 0.902 [0.85, 0.94] | 6.4 [3.3, 10.2] | 249 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.549 [0.40, 0.70] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s2k-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.807 [0.64, 0.95] | 0.991 [0.98, 1.00] | 0.889 [0.78, 0.97] | 0.948 [0.89, 0.99] | 217 / 219 |
| phone | rules+gliner-recipe-r5-s2k-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.813 [0.70, 0.91] | 0.905 [0.86, 0.94] | 0.857 [0.79, 0.91] | 0.885 [0.84, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.431 [0.29, 0.60] | 0.815 [0.65, 0.97] | 0.564 [0.41, 0.72] | 0.692 [0.54, 0.83] | 22 / 27 |
| birth_number | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s2k-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.591 [0.44, 0.75] | 0.699 [0.57, 0.82] | 0.640 [0.51, 0.77] | 0.674 [0.56, 0.79] | 153 / 219 |
| phone | rules+gliner-recipe-r5-s2k-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.664 [0.57, 0.76] | 0.724 [0.66, 0.79] | 0.693 [0.62, 0.76] | 0.711 [0.65, 0.78] | 281 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.1 [2.9, 10.0] | 26 / 27 |
| birth_number | rules+gliner-recipe-r5-s2k-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r5-s2k-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s2k-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.010 [0.00, 0.02] | 0.977 [0.95, 1.00] | 11.3 [6.1, 18.0] | 214 / 219 |
| phone | rules+gliner-recipe-r5-s2k-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.066 [0.04, 0.10] | 0.907 [0.85, 0.95] | 19.2 [12.8, 26.3] | 352 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.994 [0.99, 1.00] | 0.950 [0.94, 0.96] | 0.972 [0.97, 0.98] | 0.959 [0.95, 0.97] | 2013 / 2119 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.996 [0.99, 1.00] | 0.988 [0.98, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4302 / 4353 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.997 [1.00, 1.00] | 0.981 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8925 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.846 [0.83, 0.86] | 0.821 [0.80, 0.84] | 0.833 [0.82, 0.85] | 0.826 [0.81, 0.84] | 1740 / 2119 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.985 [0.98, 0.99] | 0.977 [0.97, 0.98] | 0.981 [0.98, 0.98] | 0.978 [0.97, 0.98] | 4251 / 4353 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.945 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8486 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.089 [0.07, 0.11] | 0.929 [0.92, 0.94] | 1.1 [0.9, 1.3] | 1968 / 2119 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.009 [0.01, 0.01] | 0.986 [0.98, 0.99] | 0.2 [0.2, 0.3] | 4293 / 4353 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.039 [0.03, 0.05] | 0.963 [0.96, 0.97] | 1.4 [1.2, 1.7] | 8756 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.992 [0.99, 1.00] | 0.952 [0.94, 0.96] | 0.972 [0.97, 0.98] | 0.960 [0.95, 0.97] | 2017 / 2118 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.995 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4297 / 4344 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.996 [0.99, 1.00] | 0.982 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8768 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.834 [0.82, 0.85] | 0.815 [0.80, 0.83] | 0.825 [0.81, 0.84] | 0.819 [0.80, 0.84] | 1726 / 2118 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.975 [0.97, 0.98] | 0.969 [0.96, 0.97] | 0.972 [0.97, 0.98] | 0.970 [0.96, 0.98] | 4210 / 4344 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.939 [0.93, 0.94] | 0.930 [0.92, 0.94] | 0.934 [0.93, 0.94] | 0.932 [0.93, 0.94] | 8300 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s2 | 0.097 [0.08, 0.12] | 0.935 [0.92, 0.94] | 1.2 [1.0, 1.5] | 1980 / 2118 |
| email | rules+gliner-recipe-r5-s2k-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r5-s2k-s2 | 0.008 [0.01, 0.01] | 0.986 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4283 / 4344 |
| any | rules+gliner-recipe-r5-s2k-s2 | 0.040 [0.03, 0.05] | 0.966 [0.96, 0.97] | 1.7 [1.4, 2.0] | 8624 / 8927 |
