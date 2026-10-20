# train-recipe-r5-s5k-dev

rules+gliner-recipe-r5-s5k after training (train-recipe-r5-s5k).

Stage: dev · commit 94ed4acc40 · 2026-10-16T00:09:37+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r5-s5k @ 99d407be2e · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.864 [0.71, 1.00] | 0.773 [0.60, 0.93] | 0.816 [0.68, 0.92] | 0.789 [0.63, 0.92] | 17 / 22 |
| email | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r5-s5k | 0.919 [0.89, 0.95] | 0.933 [0.91, 0.96] | 0.926 [0.90, 0.95] | 0.930 [0.91, 0.95] | 489 / 524 |
| phone | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r5-s5k | 0.923 [0.89, 0.95] | 0.911 [0.87, 0.94] | 0.917 [0.89, 0.94] | 0.913 [0.88, 0.94] | 552 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.227 [0.06, 0.43] | 0.227 [0.05, 0.48] | 0.227 [0.05, 0.44] | 0.227 [0.05, 0.46] | 5 / 22 |
| email | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r5-s5k | 0.883 [0.85, 0.91] | 0.895 [0.87, 0.92] | 0.889 [0.86, 0.91] | 0.893 [0.87, 0.92] | 469 / 524 |
| phone | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r5-s5k | 0.868 [0.83, 0.90] | 0.855 [0.81, 0.89] | 0.861 [0.83, 0.89] | 0.857 [0.82, 0.89] | 518 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.500 [0.33, 0.64] | 0.227 [0.05, 0.48] | 0.8 [0.2, 1.5] | 5 / 22 |
| email | rules+gliner-recipe-r5-s5k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r5-s5k | 0.054 [0.04, 0.07] | 0.906 [0.88, 0.93] | 3.3 [2.1, 4.7] | 475 / 524 |
| phone | rules+gliner-recipe-r5-s5k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r5-s5k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r5-s5k | 0.120 [0.08, 0.16] | 0.865 [0.82, 0.90] | 4.1 [2.6, 5.8] | 524 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s5k | 0.854 [0.78, 0.93] | 0.913 [0.86, 0.96] | 0.882 [0.83, 0.93] | 0.900 [0.86, 0.94] | 252 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s5k | 0.820 [0.75, 0.89] | 0.873 [0.82, 0.93] | 0.846 [0.80, 0.90] | 0.862 [0.82, 0.91] | 241 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s5k | 0.068 [0.04, 0.10] | 0.895 [0.84, 0.94] | 5.3 [2.5, 8.6] | 247 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.571 [0.40, 0.74] | 1.000 [1.00, 1.00] | 0.727 [0.57, 0.85] | 0.870 [0.77, 0.93] | 27 / 27 |
| birth_number | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r5-s5k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s5k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r5-s5k | 0.795 [0.63, 0.95] | 0.927 [0.81, 1.00] | 0.856 [0.74, 0.96] | 0.897 [0.80, 0.97] | 203 / 219 |
| phone | rules+gliner-recipe-r5-s5k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r5-s5k | 0.810 [0.70, 0.90] | 0.869 [0.81, 0.93] | 0.838 [0.77, 0.89] | 0.856 [0.80, 0.90] | 337 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.449 [0.29, 0.62] | 0.815 [0.64, 0.96] | 0.579 [0.41, 0.73] | 0.701 [0.53, 0.84] | 22 / 27 |
| birth_number | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r5-s5k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s5k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r5-s5k | 0.627 [0.47, 0.78] | 0.699 [0.58, 0.82] | 0.661 [0.54, 0.78] | 0.683 [0.57, 0.80] | 153 / 219 |
| phone | rules+gliner-recipe-r5-s5k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r5-s5k | 0.692 [0.59, 0.79] | 0.724 [0.66, 0.79] | 0.708 [0.64, 0.78] | 0.718 [0.66, 0.78] | 281 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.0 [2.8, 9.8] | 26 / 27 |
| birth_number | rules+gliner-recipe-r5-s5k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r5-s5k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r5-s5k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s5k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r5-s5k | 0.056 [0.01, 0.14] | 0.922 [0.80, 0.99] | 10.1 [5.2, 16.8] | 202 / 219 |
| phone | rules+gliner-recipe-r5-s5k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r5-s5k | 0.086 [0.05, 0.12] | 0.876 [0.81, 0.93] | 17.9 [11.6, 25.8] | 340 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.998 [1.00, 1.00] | 0.951 [0.94, 0.96] | 0.974 [0.97, 0.98] | 0.960 [0.95, 0.97] | 2015 / 2119 |
| email | rules+gliner-recipe-r5-s5k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r5-s5k | 0.996 [0.99, 1.00] | 0.989 [0.98, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4303 / 4353 |
| any | rules+gliner-recipe-r5-s5k | 0.997 [1.00, 1.00] | 0.981 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8927 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.857 [0.84, 0.87] | 0.831 [0.82, 0.85] | 0.844 [0.83, 0.86] | 0.836 [0.82, 0.85] | 1761 / 2119 |
| email | rules+gliner-recipe-r5-s5k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r5-s5k | 0.985 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.982 [0.98, 0.99] | 0.979 [0.97, 0.98] | 4256 / 4353 |
| any | rules+gliner-recipe-r5-s5k | 0.948 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.942 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8512 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.088 [0.07, 0.10] | 0.934 [0.92, 0.94] | 1.0 [0.8, 1.1] | 1979 / 2119 |
| email | rules+gliner-recipe-r5-s5k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r5-s5k | 0.009 [0.01, 0.01] | 0.986 [0.98, 0.99] | 0.2 [0.1, 0.3] | 4294 / 4353 |
| any | rules+gliner-recipe-r5-s5k | 0.039 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.3 [1.1, 1.5] | 8768 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.999 [1.00, 1.00] | 0.949 [0.94, 0.96] | 0.973 [0.97, 0.98] | 0.959 [0.95, 0.97] | 2010 / 2118 |
| email | rules+gliner-recipe-r5-s5k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r5-s5k | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 0.994 [0.99, 1.00] | 0.994 [0.99, 1.00] | 4314 / 4344 |
| any | rules+gliner-recipe-r5-s5k | 0.998 [1.00, 1.00] | 0.983 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8776 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.848 [0.83, 0.86] | 0.821 [0.80, 0.84] | 0.834 [0.82, 0.85] | 0.826 [0.81, 0.84] | 1739 / 2118 |
| email | rules+gliner-recipe-r5-s5k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r5-s5k | 0.977 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.975 [0.97, 0.98] | 4234 / 4344 |
| any | rules+gliner-recipe-r5-s5k | 0.943 [0.94, 0.95] | 0.934 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.936 [0.93, 0.94] | 8336 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s5k | 0.095 [0.08, 0.11] | 0.934 [0.92, 0.94] | 1.0 [0.9, 1.2] | 1979 / 2118 |
| email | rules+gliner-recipe-r5-s5k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r5-s5k | 0.005 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4300 / 4344 |
| any | rules+gliner-recipe-r5-s5k | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.4 [1.2, 1.7] | 8640 / 8927 |
