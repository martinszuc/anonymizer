# train-recipe-r1-s10k-dev

rules+gliner-recipe-r1-s10k after training (train-recipe-r1-s10k).

Stage: dev · commit 94ed4acc40 · 2026-10-15T20:35:57+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r1-s10k @ 4cee988812 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.870 [0.72, 1.00] | 0.773 [0.60, 0.93] | 0.818 [0.68, 0.92] | 0.790 [0.63, 0.92] | 17 / 22 |
| email | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r1-s10k | 0.916 [0.88, 0.95] | 0.935 [0.91, 0.96] | 0.925 [0.90, 0.95] | 0.931 [0.91, 0.95] | 490 / 524 |
| phone | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r1-s10k | 0.923 [0.89, 0.95] | 0.916 [0.89, 0.94] | 0.920 [0.90, 0.94] | 0.917 [0.89, 0.94] | 555 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.130 [0.00, 0.30] | 0.136 [0.00, 0.32] | 0.133 [0.00, 0.30] | 0.135 [0.00, 0.31] | 3 / 22 |
| email | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r1-s10k | 0.880 [0.84, 0.91] | 0.897 [0.87, 0.92] | 0.888 [0.86, 0.91] | 0.893 [0.87, 0.92] | 470 / 524 |
| phone | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r1-s10k | 0.860 [0.82, 0.90] | 0.853 [0.81, 0.89] | 0.857 [0.82, 0.89] | 0.855 [0.82, 0.89] | 517 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.527 [0.37, 0.66] | 0.182 [0.04, 0.39] | 0.8 [0.2, 1.6] | 4 / 22 |
| email | rules+gliner-recipe-r1-s10k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r1-s10k | 0.052 [0.04, 0.07] | 0.912 [0.89, 0.93] | 3.4 [2.0, 4.8] | 478 / 524 |
| phone | rules+gliner-recipe-r1-s10k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r1-s10k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r1-s10k | 0.125 [0.09, 0.16] | 0.868 [0.83, 0.90] | 4.3 [2.6, 5.9] | 526 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r1-s10k | 0.869 [0.79, 0.94] | 0.891 [0.83, 0.95] | 0.880 [0.83, 0.93] | 0.887 [0.84, 0.93] | 246 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r1-s10k | 0.841 [0.76, 0.92] | 0.862 [0.80, 0.92] | 0.852 [0.80, 0.91] | 0.858 [0.80, 0.91] | 238 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r1-s10k | 0.096 [0.05, 0.14] | 0.873 [0.81, 0.93] | 4.8 [2.0, 8.0] | 241 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.562 [0.40, 0.73] | 0.963 [0.88, 1.00] | 0.710 [0.57, 0.83] | 0.843 [0.74, 0.92] | 26 / 27 |
| birth_number | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r1-s10k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r1-s10k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r1-s10k | 0.807 [0.64, 0.97] | 0.936 [0.82, 1.00] | 0.867 [0.75, 0.97] | 0.907 [0.81, 0.99] | 205 / 219 |
| phone | rules+gliner-recipe-r1-s10k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r1-s10k | 0.815 [0.70, 0.91] | 0.869 [0.81, 0.93] | 0.841 [0.77, 0.90] | 0.857 [0.80, 0.91] | 337 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.458 [0.30, 0.62] | 0.815 [0.65, 0.96] | 0.587 [0.42, 0.73] | 0.705 [0.54, 0.84] | 22 / 27 |
| birth_number | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r1-s10k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r1-s10k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r1-s10k | 0.643 [0.49, 0.80] | 0.717 [0.61, 0.83] | 0.678 [0.56, 0.80] | 0.701 [0.60, 0.81] | 157 / 219 |
| phone | rules+gliner-recipe-r1-s10k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r1-s10k | 0.704 [0.60, 0.80] | 0.735 [0.68, 0.80] | 0.719 [0.64, 0.79] | 0.728 [0.67, 0.79] | 285 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.040 [0.00, 0.10] | 0.926 [0.82, 1.00] | 6.0 [2.8, 9.8] | 25 / 27 |
| birth_number | rules+gliner-recipe-r1-s10k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r1-s10k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r1-s10k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r1-s10k | 0.050 [0.00, 0.13] | 0.922 [0.80, 1.00] | 9.6 [4.7, 16.4] | 202 / 219 |
| phone | rules+gliner-recipe-r1-s10k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r1-s10k | 0.086 [0.05, 0.13] | 0.874 [0.81, 0.93] | 17.3 [11.1, 25.1] | 339 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.902 [0.89, 0.91] | 0.948 [0.94, 0.95] | 0.920 [0.91, 0.93] | 1912 / 2119 |
| email | rules+gliner-recipe-r1-s10k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r1-s10k | 0.997 [1.00, 1.00] | 0.992 [0.99, 0.99] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 4318 / 4353 |
| any | rules+gliner-recipe-r1-s10k | 0.998 [1.00, 1.00] | 0.972 [0.97, 0.97] | 0.985 [0.98, 0.99] | 0.977 [0.97, 0.98] | 8839 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.857 [0.84, 0.87] | 0.788 [0.77, 0.81] | 0.821 [0.81, 0.84] | 0.801 [0.78, 0.82] | 1670 / 2119 |
| email | rules+gliner-recipe-r1-s10k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r1-s10k | 0.985 [0.98, 0.99] | 0.980 [0.97, 0.98] | 0.982 [0.98, 0.99] | 0.981 [0.98, 0.99] | 4264 / 4353 |
| any | rules+gliner-recipe-r1-s10k | 0.949 [0.94, 0.95] | 0.927 [0.92, 0.93] | 0.938 [0.93, 0.94] | 0.931 [0.93, 0.94] | 8430 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.108 [0.09, 0.13] | 0.889 [0.87, 0.90] | 0.9 [0.8, 1.1] | 1884 / 2119 |
| email | rules+gliner-recipe-r1-s10k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r1-s10k | 0.007 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.2 [0.1, 0.3] | 4306 / 4353 |
| any | rules+gliner-recipe-r1-s10k | 0.045 [0.04, 0.05] | 0.955 [0.95, 0.96] | 1.2 [1.0, 1.4] | 8685 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 1.000 [1.00, 1.00] | 0.895 [0.88, 0.91] | 0.944 [0.94, 0.95] | 0.914 [0.90, 0.93] | 1895 / 2118 |
| email | rules+gliner-recipe-r1-s10k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r1-s10k | 0.997 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 4320 / 4344 |
| any | rules+gliner-recipe-r1-s10k | 0.999 [1.00, 1.00] | 0.971 [0.97, 0.97] | 0.985 [0.98, 0.99] | 0.976 [0.97, 0.98] | 8668 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.842 [0.83, 0.86] | 0.769 [0.75, 0.79] | 0.804 [0.79, 0.82] | 0.782 [0.76, 0.80] | 1628 / 2118 |
| email | rules+gliner-recipe-r1-s10k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r1-s10k | 0.980 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4243 / 4344 |
| any | rules+gliner-recipe-r1-s10k | 0.945 [0.94, 0.95] | 0.922 [0.92, 0.93] | 0.934 [0.93, 0.94] | 0.927 [0.92, 0.93] | 8235 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s10k | 0.115 [0.10, 0.13] | 0.882 [0.87, 0.90] | 1.0 [0.8, 1.1] | 1868 / 2118 |
| email | rules+gliner-recipe-r1-s10k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r1-s10k | 0.004 [0.00, 0.01] | 0.992 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4309 / 4344 |
| any | rules+gliner-recipe-r1-s10k | 0.044 [0.04, 0.05] | 0.956 [0.95, 0.96] | 1.3 [1.2, 1.6] | 8538 / 8927 |
