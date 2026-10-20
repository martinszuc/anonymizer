# train-recipe-r3-s2k-dev

rules+gliner-recipe-r3-s2k after training (train-recipe-r3-s2k).

Stage: dev · commit 94ed4acc40 · 2026-10-15T22:53:12+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r3-s2k @ 265b48952f · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.862 [0.76, 0.97] | 0.864 [0.72, 1.00] | 0.863 [0.76, 0.96] | 0.863 [0.74, 0.98] | 19 / 22 |
| email | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k | 0.909 [0.88, 0.94] | 0.947 [0.93, 0.97] | 0.927 [0.90, 0.95] | 0.939 [0.92, 0.96] | 496 / 524 |
| phone | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k | 0.913 [0.88, 0.94] | 0.927 [0.89, 0.96] | 0.920 [0.89, 0.94] | 0.924 [0.89, 0.95] | 562 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.103 [0.00, 0.25] | 0.136 [0.00, 0.32] | 0.118 [0.00, 0.27] | 0.128 [0.00, 0.29] | 3 / 22 |
| email | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k | 0.872 [0.84, 0.90] | 0.910 [0.89, 0.93] | 0.891 [0.86, 0.91] | 0.902 [0.88, 0.92] | 477 / 524 |
| phone | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k | 0.845 [0.81, 0.88] | 0.865 [0.82, 0.90] | 0.855 [0.82, 0.88] | 0.861 [0.82, 0.89] | 524 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.458 [0.32, 0.59] | 0.227 [0.06, 0.46] | 0.8 [0.2, 1.5] | 5 / 22 |
| email | rules+gliner-recipe-r3-s2k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k | 0.043 [0.03, 0.06] | 0.920 [0.90, 0.94] | 3.8 [2.5, 5.2] | 482 / 524 |
| phone | rules+gliner-recipe-r3-s2k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k | 0.108 [0.07, 0.14] | 0.876 [0.83, 0.91] | 4.6 [3.1, 6.1] | 531 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k | 0.838 [0.76, 0.92] | 0.920 [0.87, 0.96] | 0.877 [0.82, 0.92] | 0.902 [0.86, 0.94] | 254 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k | 0.811 [0.73, 0.89] | 0.888 [0.84, 0.93] | 0.848 [0.79, 0.90] | 0.871 [0.82, 0.91] | 245 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k | 0.062 [0.03, 0.09] | 0.902 [0.85, 0.95] | 5.9 [2.9, 9.4] | 249 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.540 [0.39, 0.70] | 1.000 [1.00, 1.00] | 0.701 [0.56, 0.82] | 0.854 [0.76, 0.92] | 27 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k | 0.800 [0.63, 0.95] | 0.986 [0.97, 1.00] | 0.883 [0.77, 0.97] | 0.942 [0.89, 0.98] | 216 / 219 |
| phone | rules+gliner-recipe-r3-s2k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k | 0.806 [0.70, 0.90] | 0.902 [0.85, 0.94] | 0.851 [0.78, 0.91] | 0.881 [0.84, 0.92] | 350 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.440 [0.29, 0.60] | 0.815 [0.64, 0.96] | 0.571 [0.41, 0.72] | 0.696 [0.53, 0.83] | 22 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k | 0.592 [0.45, 0.75] | 0.703 [0.58, 0.82] | 0.643 [0.52, 0.78] | 0.678 [0.56, 0.80] | 154 / 219 |
| phone | rules+gliner-recipe-r3-s2k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k | 0.667 [0.57, 0.77] | 0.727 [0.66, 0.80] | 0.695 [0.62, 0.77] | 0.714 [0.65, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 5.9 [2.7, 9.7] | 26 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r3-s2k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k | 0.012 [0.00, 0.03] | 0.977 [0.95, 1.00] | 11.6 [6.2, 18.2] | 214 / 219 |
| phone | rules+gliner-recipe-r3-s2k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k | 0.067 [0.04, 0.11] | 0.907 [0.85, 0.95] | 19.2 [12.5, 26.8] | 352 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.995 [0.99, 1.00] | 0.953 [0.94, 0.96] | 0.974 [0.97, 0.98] | 0.961 [0.95, 0.97] | 2020 / 2119 |
| email | rules+gliner-recipe-r3-s2k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r3-s2k | 0.995 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4308 / 4353 |
| any | rules+gliner-recipe-r3-s2k | 0.996 [0.99, 1.00] | 0.983 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8938 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.848 [0.83, 0.86] | 0.828 [0.81, 0.84] | 0.838 [0.82, 0.85] | 0.832 [0.82, 0.85] | 1754 / 2119 |
| email | rules+gliner-recipe-r3-s2k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r3-s2k | 0.984 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.979 [0.97, 0.98] | 4256 / 4353 |
| any | rules+gliner-recipe-r3-s2k | 0.945 [0.94, 0.95] | 0.935 [0.93, 0.94] | 0.940 [0.94, 0.94] | 0.937 [0.93, 0.94] | 8507 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.085 [0.07, 0.10] | 0.932 [0.92, 0.94] | 1.1 [0.9, 1.2] | 1976 / 2119 |
| email | rules+gliner-recipe-r3-s2k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r3-s2k | 0.009 [0.01, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4298 / 4353 |
| any | rules+gliner-recipe-r3-s2k | 0.038 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8769 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.995 [0.99, 1.00] | 0.952 [0.94, 0.96] | 0.973 [0.97, 0.98] | 0.961 [0.95, 0.97] | 2017 / 2118 |
| email | rules+gliner-recipe-r3-s2k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r3-s2k | 0.995 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4302 / 4344 |
| any | rules+gliner-recipe-r3-s2k | 0.997 [1.00, 1.00] | 0.983 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8776 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.837 [0.82, 0.85] | 0.816 [0.80, 0.83] | 0.826 [0.81, 0.84] | 0.820 [0.80, 0.84] | 1728 / 2118 |
| email | rules+gliner-recipe-r3-s2k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r3-s2k | 0.976 [0.97, 0.98] | 0.971 [0.96, 0.98] | 0.973 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4218 / 4344 |
| any | rules+gliner-recipe-r3-s2k | 0.940 [0.93, 0.95] | 0.931 [0.92, 0.94] | 0.936 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8312 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k | 0.095 [0.08, 0.11] | 0.933 [0.92, 0.94] | 1.1 [0.9, 1.3] | 1977 / 2118 |
| email | rules+gliner-recipe-r3-s2k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r3-s2k | 0.007 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4287 / 4344 |
| any | rules+gliner-recipe-r3-s2k | 0.039 [0.03, 0.05] | 0.966 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8625 / 8927 |
