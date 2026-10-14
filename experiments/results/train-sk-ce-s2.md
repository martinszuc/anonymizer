# train-sk-ce-s2-dev

rules+gliner-sk-ce-s2 after training (train-sk-ce-s2).

Stage: dev · commit 0211b3728e · 2026-10-14T20:50:42+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-sk-ce-s2 @ 42c32fbd58 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.559 [0.39, 0.70] | 1.000 [1.00, 1.00] | 0.717 [0.56, 0.83] | 0.864 [0.76, 0.92] | 22 / 22 |
| email | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-sk-ce-s2 | 0.847 [0.80, 0.88] | 0.927 [0.90, 0.95] | 0.885 [0.86, 0.91] | 0.910 [0.88, 0.93] | 486 / 524 |
| phone | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-sk-ce-s2 | 0.839 [0.80, 0.88] | 0.936 [0.91, 0.96] | 0.885 [0.86, 0.91] | 0.914 [0.89, 0.94] | 567 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.068 [0.02, 0.14] | 0.182 [0.04, 0.40] | 0.099 [0.02, 0.20] | 0.136 [0.03, 0.28] | 4 / 22 |
| email | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-sk-ce-s2 | 0.790 [0.75, 0.83] | 0.855 [0.82, 0.89] | 0.821 [0.79, 0.85] | 0.841 [0.81, 0.87] | 448 / 524 |
| phone | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-sk-ce-s2 | 0.743 [0.70, 0.78] | 0.822 [0.77, 0.86] | 0.781 [0.74, 0.82] | 0.805 [0.76, 0.84] | 498 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.359 [0.26, 0.45] | 0.273 [0.10, 0.50] | 4.0 [2.2, 5.8] | 6 / 22 |
| email | rules+gliner-sk-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-sk-ce-s2 | 0.045 [0.03, 0.06] | 0.926 [0.90, 0.95] | 7.4 [5.6, 9.4] | 485 / 524 |
| phone | rules+gliner-sk-ce-s2 | 0.318 [0.09, 0.61] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-sk-ce-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-sk-ce-s2 | 0.101 [0.07, 0.14] | 0.883 [0.84, 0.92] | 11.3 [8.6, 14.1] | 535 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-sk-ce-s2 | 0.822 [0.72, 0.90] | 0.870 [0.80, 0.92] | 0.845 [0.78, 0.90] | 0.860 [0.80, 0.90] | 240 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-sk-ce-s2 | 0.801 [0.70, 0.89] | 0.848 [0.78, 0.90] | 0.824 [0.76, 0.88] | 0.838 [0.78, 0.89] | 234 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-sk-ce-s2 | 0.119 [0.07, 0.18] | 0.851 [0.78, 0.91] | 6.3 [2.8, 10.9] | 235 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.450 [0.33, 0.59] | 1.000 [1.00, 1.00] | 0.621 [0.50, 0.74] | 0.804 [0.71, 0.88] | 27 / 27 |
| birth_number | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-sk-ce-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-sk-ce-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-sk-ce-s2 | 0.783 [0.62, 0.95] | 0.931 [0.80, 1.00] | 0.851 [0.73, 0.95] | 0.897 [0.80, 0.97] | 204 / 219 |
| phone | rules+gliner-sk-ce-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-sk-ce-s2 | 0.777 [0.67, 0.88] | 0.871 [0.80, 0.92] | 0.822 [0.75, 0.88] | 0.851 [0.80, 0.90] | 338 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.367 [0.24, 0.53] | 0.815 [0.64, 0.96] | 0.506 [0.35, 0.67] | 0.655 [0.49, 0.80] | 22 / 27 |
| birth_number | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-sk-ce-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-sk-ce-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-sk-ce-s2 | 0.634 [0.49, 0.79] | 0.722 [0.61, 0.83] | 0.675 [0.57, 0.78] | 0.702 [0.60, 0.80] | 158 / 219 |
| phone | rules+gliner-sk-ce-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-sk-ce-s2 | 0.678 [0.58, 0.78] | 0.737 [0.68, 0.80] | 0.706 [0.64, 0.78] | 0.724 [0.67, 0.78] | 286 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.9 [3.6, 10.7] | 27 / 27 |
| birth_number | rules+gliner-sk-ce-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-sk-ce-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-sk-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-sk-ce-s2 | 0.052 [0.00, 0.14] | 0.922 [0.80, 1.00] | 10.9 [5.6, 17.8] | 202 / 219 |
| phone | rules+gliner-sk-ce-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-sk-ce-s2 | 0.081 [0.05, 0.12] | 0.879 [0.81, 0.93] | 19.5 [12.2, 27.8] | 341 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.988 [0.98, 0.99] | 0.954 [0.95, 0.96] | 0.971 [0.97, 0.98] | 0.961 [0.95, 0.97] | 2022 / 2119 |
| email | rules+gliner-sk-ce-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-sk-ce-s2 | 0.994 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 4336 / 4353 |
| any | rules+gliner-sk-ce-s2 | 0.994 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8968 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.830 [0.81, 0.85] | 0.816 [0.80, 0.83] | 0.823 [0.81, 0.84] | 0.818 [0.80, 0.83] | 1728 / 2119 |
| email | rules+gliner-sk-ce-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-sk-ce-s2 | 0.974 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.975 [0.97, 0.98] | 4245 / 4353 |
| any | rules+gliner-sk-ce-s2 | 0.936 [0.93, 0.94] | 0.931 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.932 [0.93, 0.94] | 8471 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.087 [0.07, 0.10] | 0.918 [0.91, 0.93] | 1.1 [0.9, 1.3] | 1946 / 2119 |
| email | rules+gliner-sk-ce-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-sk-ce-s2 | 0.003 [0.00, 0.00] | 0.995 [0.99, 1.00] | 0.4 [0.3, 0.6] | 4330 / 4353 |
| any | rules+gliner-sk-ce-s2 | 0.036 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.6 [1.4, 1.9] | 8771 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.987 [0.98, 0.99] | 0.969 [0.96, 0.98] | 0.978 [0.97, 0.98] | 0.973 [0.97, 0.98] | 2052 / 2118 |
| email | rules+gliner-sk-ce-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-sk-ce-s2 | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 4324 / 4344 |
| any | rules+gliner-sk-ce-s2 | 0.994 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 8825 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.837 [0.82, 0.85] | 0.838 [0.82, 0.85] | 0.837 [0.82, 0.85] | 0.837 [0.82, 0.85] | 1774 / 2118 |
| email | rules+gliner-sk-ce-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-sk-ce-s2 | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4243 / 4344 |
| any | rules+gliner-sk-ce-s2 | 0.940 [0.93, 0.95] | 0.938 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.939 [0.93, 0.94] | 8377 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s2 | 0.087 [0.07, 0.11] | 0.951 [0.94, 0.96] | 1.2 [1.0, 1.4] | 2015 / 2118 |
| email | rules+gliner-sk-ce-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-sk-ce-s2 | 0.003 [0.00, 0.00] | 0.992 [0.99, 0.99] | 0.3 [0.2, 0.5] | 4311 / 4344 |
| any | rules+gliner-sk-ce-s2 | 0.035 [0.03, 0.04] | 0.973 [0.97, 0.98] | 1.6 [1.4, 1.9] | 8687 / 8927 |
