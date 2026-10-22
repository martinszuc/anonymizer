# train-cs-sk-focal-r3-s2-dev

rules+gliner-cs-sk-focal-r3-s2 after training (train-cs-sk-focal-r3-s2).

Stage: dev · commit 0b2364ff37 · 2026-10-21T21:27:29+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-r3-s2 @ 899e2dcb88 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.861 [0.75, 0.95] | 0.955 [0.82, 1.00] | 0.905 [0.82, 0.96] | 0.934 [0.83, 0.98] | 21 / 22 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.872 [0.83, 0.91] | 0.949 [0.93, 0.97] | 0.909 [0.88, 0.93] | 0.932 [0.91, 0.95] | 497 / 524 |
| phone | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.880 [0.85, 0.91] | 0.937 [0.91, 0.96] | 0.908 [0.88, 0.93] | 0.925 [0.90, 0.95] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.111 [0.03, 0.24] | 0.182 [0.04, 0.40] | 0.138 [0.03, 0.30] | 0.161 [0.04, 0.36] | 4 / 22 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.839 [0.80, 0.88] | 0.914 [0.89, 0.93] | 0.875 [0.85, 0.90] | 0.898 [0.87, 0.92] | 479 / 524 |
| phone | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.809 [0.77, 0.85] | 0.870 [0.83, 0.90] | 0.839 [0.80, 0.87] | 0.857 [0.82, 0.89] | 527 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.382 [0.27, 0.48] | 0.273 [0.10, 0.50] | 1.0 [0.3, 1.9] | 6 / 22 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.036 [0.02, 0.05] | 0.927 [0.91, 0.95] | 5.7 [4.2, 7.3] | 486 / 524 |
| phone | rules+gliner-cs-sk-focal-r3-s2 | 0.318 [0.09, 0.61] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.096 [0.07, 0.13] | 0.884 [0.85, 0.92] | 6.6 [4.8, 8.5] | 536 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.829 [0.74, 0.90] | 0.957 [0.92, 0.98] | 0.888 [0.83, 0.93] | 0.928 [0.89, 0.95] | 264 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.797 [0.71, 0.87] | 0.913 [0.87, 0.95] | 0.851 [0.79, 0.90] | 0.887 [0.84, 0.92] | 252 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.035 [0.02, 0.06] | 0.938 [0.90, 0.97] | 6.7 [3.7, 10.8] | 259 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.518 [0.38, 0.67] | 1.000 [1.00, 1.00] | 0.683 [0.55, 0.81] | 0.843 [0.75, 0.91] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.754 [0.60, 0.92] | 0.991 [0.98, 1.00] | 0.857 [0.75, 0.95] | 0.932 [0.88, 0.98] | 217 / 219 |
| phone | rules+gliner-cs-sk-focal-r3-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.781 [0.68, 0.87] | 0.905 [0.86, 0.94] | 0.839 [0.77, 0.89] | 0.877 [0.83, 0.91] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.407 [0.27, 0.58] | 0.815 [0.65, 0.97] | 0.543 [0.39, 0.71] | 0.679 [0.52, 0.82] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.560 [0.41, 0.74] | 0.708 [0.59, 0.82] | 0.625 [0.49, 0.76] | 0.672 [0.55, 0.79] | 155 / 219 |
| phone | rules+gliner-cs-sk-focal-r3-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.637 [0.54, 0.75] | 0.729 [0.67, 0.80] | 0.680 [0.60, 0.76] | 0.709 [0.64, 0.78] | 283 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.8 [3.0, 11.5] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-r3-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.009 [0.00, 0.02] | 0.982 [0.95, 1.00] | 13.8 [6.6, 23.5] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-r3-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.066 [0.04, 0.10] | 0.910 [0.85, 0.95] | 22.4 [14.2, 31.6] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.990 [0.99, 0.99] | 0.959 [0.95, 0.97] | 0.974 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2032 / 2119 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.993 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4310 / 4353 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.994 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8953 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.842 [0.83, 0.86] | 0.832 [0.81, 0.85] | 0.837 [0.82, 0.85] | 0.834 [0.82, 0.85] | 1762 / 2119 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.980 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4252 / 4353 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.941 [0.94, 0.95] | 0.935 [0.93, 0.94] | 0.938 [0.93, 0.94] | 0.937 [0.93, 0.94] | 8510 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.084 [0.07, 0.10] | 0.938 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1987 / 2119 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.008 [0.01, 0.01] | 0.988 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4300 / 4353 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.037 [0.03, 0.04] | 0.965 [0.96, 0.97] | 1.6 [1.4, 1.9] | 8782 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.981 [0.98, 0.99] | 0.964 [0.96, 0.97] | 0.973 [0.97, 0.98] | 0.968 [0.96, 0.97] | 2042 / 2118 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.994 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4300 / 4344 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.993 [0.99, 0.99] | 0.985 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8797 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.825 [0.81, 0.84] | 0.828 [0.81, 0.84] | 0.827 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1753 / 2118 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.974 [0.97, 0.98] | 0.970 [0.96, 0.98] | 0.972 [0.97, 0.98] | 0.971 [0.97, 0.98] | 4214 / 4344 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.936 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8330 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s2 | 0.088 [0.07, 0.11] | 0.945 [0.93, 0.95] | 1.3 [1.1, 1.5] | 2001 / 2118 |
| email | rules+gliner-cs-sk-focal-r3-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-r3-s2 | 0.007 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4287 / 4344 |
| any | rules+gliner-cs-sk-focal-r3-s2 | 0.037 [0.03, 0.04] | 0.969 [0.96, 0.97] | 1.7 [1.5, 2.0] | 8649 / 8927 |
