# train-recipe-r5-s10k-dev

rules+gliner-recipe-r5-s10k after training (train-recipe-r5-s10k).

Stage: dev · commit 94ed4acc40 · 2026-10-16T00:22:32+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r5-s10k @ 36b234283e · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.889 [0.75, 1.00] | 0.636 [0.44, 0.87] | 0.742 [0.58, 0.88] | 0.675 [0.49, 0.87] | 14 / 22 |
| email | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r5-s10k | 0.922 [0.89, 0.95] | 0.945 [0.92, 0.96] | 0.933 [0.91, 0.95] | 0.940 [0.92, 0.96] | 495 / 524 |
| phone | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r5-s10k | 0.933 [0.91, 0.96] | 0.921 [0.89, 0.95] | 0.927 [0.90, 0.95] | 0.923 [0.90, 0.95] | 558 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.222 [0.06, 0.41] | 0.182 [0.04, 0.39] | 0.200 [0.05, 0.39] | 0.189 [0.04, 0.38] | 4 / 22 |
| email | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r5-s10k | 0.882 [0.85, 0.91] | 0.903 [0.88, 0.93] | 0.892 [0.87, 0.91] | 0.899 [0.87, 0.92] | 473 / 524 |
| phone | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r5-s10k | 0.871 [0.84, 0.90] | 0.860 [0.82, 0.89] | 0.865 [0.83, 0.89] | 0.862 [0.83, 0.89] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.604 [0.42, 0.73] | 0.182 [0.04, 0.39] | 0.5 [0.1, 1.1] | 4 / 22 |
| email | rules+gliner-recipe-r5-s10k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r5-s10k | 0.046 [0.03, 0.06] | 0.914 [0.89, 0.93] | 3.0 [1.8, 4.3] | 479 / 524 |
| phone | rules+gliner-recipe-r5-s10k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r5-s10k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r5-s10k | 0.131 [0.08, 0.18] | 0.870 [0.83, 0.90] | 3.6 [2.2, 4.9] | 527 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s10k | 0.866 [0.79, 0.93] | 0.913 [0.86, 0.96] | 0.889 [0.84, 0.93] | 0.903 [0.86, 0.94] | 252 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s10k | 0.835 [0.76, 0.91] | 0.877 [0.82, 0.93] | 0.855 [0.80, 0.91] | 0.868 [0.82, 0.91] | 242 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s10k | 0.078 [0.04, 0.12] | 0.895 [0.84, 0.94] | 5.1 [2.3, 8.3] | 247 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.562 [0.40, 0.73] | 1.000 [1.00, 1.00] | 0.720 [0.57, 0.84] | 0.865 [0.77, 0.93] | 27 / 27 |
| birth_number | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r5-s10k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s10k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r5-s10k | 0.787 [0.62, 0.94] | 0.936 [0.82, 1.00] | 0.855 [0.74, 0.95] | 0.902 [0.80, 0.98] | 205 / 219 |
| phone | rules+gliner-recipe-r5-s10k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r5-s10k | 0.802 [0.69, 0.90] | 0.874 [0.81, 0.93] | 0.837 [0.77, 0.89] | 0.859 [0.81, 0.91] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.458 [0.30, 0.63] | 0.815 [0.64, 0.96] | 0.587 [0.41, 0.74] | 0.705 [0.53, 0.84] | 22 / 27 |
| birth_number | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r5-s10k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s10k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r5-s10k | 0.630 [0.48, 0.79] | 0.717 [0.61, 0.83] | 0.671 [0.56, 0.79] | 0.698 [0.59, 0.81] | 157 / 219 |
| phone | rules+gliner-recipe-r5-s10k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r5-s10k | 0.695 [0.59, 0.79] | 0.735 [0.68, 0.80] | 0.714 [0.64, 0.78] | 0.726 [0.67, 0.79] | 285 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 5.7 [2.5, 9.5] | 26 / 27 |
| birth_number | rules+gliner-recipe-r5-s10k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r5-s10k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r5-s10k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r5-s10k | 0.048 [0.00, 0.13] | 0.927 [0.81, 1.00] | 10.3 [5.5, 17.1] | 203 / 219 |
| phone | rules+gliner-recipe-r5-s10k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r5-s10k | 0.082 [0.05, 0.12] | 0.879 [0.81, 0.94] | 17.8 [11.6, 25.6] | 341 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.999 [1.00, 1.00] | 0.946 [0.94, 0.96] | 0.972 [0.97, 0.98] | 0.956 [0.95, 0.96] | 2005 / 2119 |
| email | rules+gliner-recipe-r5-s10k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r5-s10k | 0.997 [0.99, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 4323 / 4353 |
| any | rules+gliner-recipe-r5-s10k | 0.998 [1.00, 1.00] | 0.982 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8937 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.862 [0.85, 0.88] | 0.831 [0.81, 0.85] | 0.846 [0.83, 0.86] | 0.837 [0.82, 0.85] | 1761 / 2119 |
| email | rules+gliner-recipe-r5-s10k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r5-s10k | 0.985 [0.98, 0.99] | 0.981 [0.98, 0.99] | 0.983 [0.98, 0.99] | 0.982 [0.98, 0.99] | 4270 / 4353 |
| any | rules+gliner-recipe-r5-s10k | 0.949 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.943 [0.94, 0.95] | 0.940 [0.93, 0.94] | 8526 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.089 [0.07, 0.11] | 0.931 [0.92, 0.94] | 0.9 [0.8, 1.1] | 1973 / 2119 |
| email | rules+gliner-recipe-r5-s10k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r5-s10k | 0.005 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.2 [0.2, 0.3] | 4311 / 4353 |
| any | rules+gliner-recipe-r5-s10k | 0.038 [0.03, 0.04] | 0.965 [0.96, 0.97] | 1.2 [1.0, 1.4] | 8779 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 1.000 [1.00, 1.00] | 0.943 [0.93, 0.95] | 0.970 [0.96, 0.98] | 0.954 [0.95, 0.96] | 1997 / 2118 |
| email | rules+gliner-recipe-r5-s10k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r5-s10k | 0.996 [0.99, 1.00] | 0.994 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 4317 / 4344 |
| any | rules+gliner-recipe-r5-s10k | 0.998 [1.00, 1.00] | 0.982 [0.98, 0.98] | 0.990 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8766 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.847 [0.83, 0.86] | 0.814 [0.80, 0.83] | 0.830 [0.81, 0.84] | 0.820 [0.80, 0.84] | 1724 / 2118 |
| email | rules+gliner-recipe-r5-s10k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r5-s10k | 0.980 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4242 / 4344 |
| any | rules+gliner-recipe-r5-s10k | 0.945 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8329 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s10k | 0.100 [0.08, 0.12] | 0.928 [0.92, 0.94] | 1.0 [0.8, 1.2] | 1966 / 2118 |
| email | rules+gliner-recipe-r5-s10k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r5-s10k | 0.004 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4306 / 4344 |
| any | rules+gliner-recipe-r5-s10k | 0.039 [0.03, 0.05] | 0.967 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8633 / 8927 |
