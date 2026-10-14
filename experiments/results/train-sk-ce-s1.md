# train-sk-ce-s1-dev

rules+gliner-sk-ce-s1 after training (train-sk-ce-s1).

Stage: dev · commit 0211b3728e · 2026-10-14T20:49:03+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-sk-ce-s1 @ d40cda495b · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.530 [0.38, 0.67] | 1.000 [1.00, 1.00] | 0.693 [0.55, 0.80] | 0.850 [0.75, 0.91] | 22 / 22 |
| email | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-sk-ce-s1 | 0.895 [0.86, 0.93] | 0.906 [0.87, 0.93] | 0.901 [0.87, 0.92] | 0.904 [0.88, 0.93] | 475 / 524 |
| phone | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-sk-ce-s1 | 0.871 [0.83, 0.91] | 0.914 [0.88, 0.94] | 0.892 [0.86, 0.92] | 0.905 [0.88, 0.93] | 554 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.045 [0.00, 0.10] | 0.136 [0.00, 0.35] | 0.068 [0.00, 0.15] | 0.097 [0.00, 0.23] | 3 / 22 |
| email | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-sk-ce-s1 | 0.842 [0.80, 0.88] | 0.844 [0.81, 0.87] | 0.843 [0.81, 0.87] | 0.843 [0.81, 0.87] | 442 / 524 |
| phone | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-sk-ce-s1 | 0.773 [0.73, 0.82] | 0.810 [0.76, 0.85] | 0.791 [0.75, 0.83] | 0.802 [0.76, 0.84] | 491 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.363 [0.26, 0.44] | 0.227 [0.07, 0.47] | 4.0 [2.3, 5.8] | 5 / 22 |
| email | rules+gliner-sk-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-sk-ce-s1 | 0.068 [0.04, 0.10] | 0.901 [0.87, 0.93] | 4.7 [3.2, 6.3] | 472 / 524 |
| phone | rules+gliner-sk-ce-s1 | 0.318 [0.08, 0.62] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-sk-ce-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-sk-ce-s1 | 0.118 [0.09, 0.15] | 0.860 [0.82, 0.89] | 8.6 [6.2, 11.3] | 521 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-sk-ce-s1 | 0.839 [0.74, 0.92] | 0.859 [0.79, 0.92] | 0.849 [0.78, 0.90] | 0.855 [0.80, 0.90] | 237 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-sk-ce-s1 | 0.811 [0.71, 0.89] | 0.823 [0.76, 0.88] | 0.817 [0.75, 0.87] | 0.820 [0.76, 0.87] | 227 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-sk-ce-s1 | 0.129 [0.08, 0.19] | 0.841 [0.78, 0.90] | 5.9 [2.5, 10.4] | 232 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.452 [0.33, 0.59] | 1.000 [1.00, 1.00] | 0.622 [0.49, 0.74] | 0.805 [0.71, 0.88] | 27 / 27 |
| birth_number | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-sk-ce-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-sk-ce-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-sk-ce-s1 | 0.787 [0.63, 0.94] | 0.931 [0.82, 1.00] | 0.853 [0.73, 0.94] | 0.898 [0.79, 0.97] | 204 / 219 |
| phone | rules+gliner-sk-ce-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-sk-ce-s1 | 0.778 [0.67, 0.87] | 0.869 [0.80, 0.92] | 0.821 [0.75, 0.87] | 0.849 [0.79, 0.89] | 337 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.355 [0.24, 0.48] | 0.815 [0.64, 0.96] | 0.494 [0.36, 0.62] | 0.647 [0.50, 0.77] | 22 / 27 |
| birth_number | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-sk-ce-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-sk-ce-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-sk-ce-s1 | 0.630 [0.48, 0.78] | 0.717 [0.60, 0.83] | 0.671 [0.56, 0.78] | 0.698 [0.59, 0.80] | 157 / 219 |
| phone | rules+gliner-sk-ce-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-sk-ce-s1 | 0.672 [0.57, 0.77] | 0.735 [0.67, 0.79] | 0.702 [0.63, 0.76] | 0.721 [0.66, 0.78] | 285 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.021 [0.00, 0.07] | 0.963 [0.87, 1.00] | 9.6 [5.0, 16.0] | 26 / 27 |
| birth_number | rules+gliner-sk-ce-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-sk-ce-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-sk-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-sk-ce-s1 | 0.055 [0.01, 0.14] | 0.913 [0.79, 0.99] | 10.1 [5.2, 17.2] | 200 / 219 |
| phone | rules+gliner-sk-ce-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-sk-ce-s1 | 0.085 [0.05, 0.13] | 0.871 [0.80, 0.93] | 21.5 [14.1, 30.2] | 338 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.988 [0.98, 0.99] | 0.959 [0.95, 0.97] | 0.973 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2032 / 2119 |
| email | rules+gliner-sk-ce-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-sk-ce-s1 | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 4334 / 4353 |
| any | rules+gliner-sk-ce-s1 | 0.994 [0.99, 1.00] | 0.987 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8975 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.826 [0.81, 0.84] | 0.816 [0.80, 0.83] | 0.821 [0.81, 0.84] | 0.818 [0.80, 0.83] | 1730 / 2119 |
| email | rules+gliner-sk-ce-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-sk-ce-s1 | 0.975 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.975 [0.97, 0.98] | 4246 / 4353 |
| any | rules+gliner-sk-ce-s1 | 0.935 [0.93, 0.94] | 0.931 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.932 [0.93, 0.94] | 8472 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.088 [0.07, 0.10] | 0.919 [0.91, 0.93] | 1.1 [0.9, 1.3] | 1947 / 2119 |
| email | rules+gliner-sk-ce-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-sk-ce-s1 | 0.003 [0.00, 0.00] | 0.993 [0.99, 1.00] | 0.4 [0.3, 0.5] | 4324 / 4353 |
| any | rules+gliner-sk-ce-s1 | 0.036 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.6 [1.4, 1.8] | 8766 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.989 [0.98, 0.99] | 0.966 [0.96, 0.97] | 0.977 [0.97, 0.98] | 0.971 [0.96, 0.98] | 2046 / 2118 |
| email | rules+gliner-sk-ce-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-sk-ce-s1 | 0.997 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 4321 / 4344 |
| any | rules+gliner-sk-ce-s1 | 0.996 [0.99, 1.00] | 0.988 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 8819 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.838 [0.82, 0.85] | 0.835 [0.82, 0.85] | 0.837 [0.82, 0.85] | 0.836 [0.82, 0.85] | 1768 / 2118 |
| email | rules+gliner-sk-ce-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-sk-ce-s1 | 0.979 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4241 / 4344 |
| any | rules+gliner-sk-ce-s1 | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 0.940 [0.93, 0.94] | 0.939 [0.93, 0.94] | 8372 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce-s1 | 0.089 [0.07, 0.11] | 0.948 [0.94, 0.96] | 1.1 [1.0, 1.4] | 2008 / 2118 |
| email | rules+gliner-sk-ce-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-sk-ce-s1 | 0.004 [0.00, 0.01] | 0.992 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4307 / 4344 |
| any | rules+gliner-sk-ce-s1 | 0.036 [0.03, 0.04] | 0.972 [0.97, 0.98] | 1.5 [1.3, 1.8] | 8676 / 8927 |
