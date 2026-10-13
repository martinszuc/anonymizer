# train-cs-sk-weighted-w10-s2-dev

rules+gliner-cs-sk-weighted-w10-s2 after training (train-cs-sk-weighted-w10-s2).

Stage: dev · commit e44e907302 · 2026-10-12T17:18:37+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-weighted-w10-s2 @ a40dfd19ff · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.786 [0.66, 0.89] | 1.000 [1.00, 1.00] | 0.880 [0.79, 0.94] | 0.948 [0.91, 0.98] | 22 / 22 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.870 [0.83, 0.91] | 0.945 [0.92, 0.96] | 0.906 [0.88, 0.93] | 0.929 [0.90, 0.95] | 495 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.874 [0.83, 0.91] | 0.939 [0.91, 0.96] | 0.905 [0.88, 0.93] | 0.925 [0.90, 0.95] | 569 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.071 [0.00, 0.17] | 0.136 [0.00, 0.33] | 0.094 [0.00, 0.23] | 0.115 [0.00, 0.28] | 3 / 22 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.835 [0.79, 0.87] | 0.908 [0.88, 0.93] | 0.870 [0.84, 0.90] | 0.893 [0.87, 0.92] | 476 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.797 [0.75, 0.84] | 0.863 [0.82, 0.90] | 0.829 [0.79, 0.86] | 0.849 [0.81, 0.88] | 523 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.353 [0.24, 0.44] | 0.227 [0.07, 0.44] | 2.2 [0.9, 3.7] | 5 / 22 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.038 [0.03, 0.05] | 0.927 [0.91, 0.95] | 5.9 [4.3, 7.6] | 486 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10-s2 | 0.318 [0.09, 0.61] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.095 [0.07, 0.12] | 0.883 [0.85, 0.91] | 7.9 [5.6, 10.6] | 535 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.807 [0.72, 0.88] | 0.960 [0.93, 0.99] | 0.877 [0.82, 0.92] | 0.925 [0.89, 0.95] | 265 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.773 [0.69, 0.84] | 0.913 [0.86, 0.96] | 0.837 [0.78, 0.88] | 0.881 [0.84, 0.92] | 252 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.035 [0.01, 0.06] | 0.942 [0.89, 0.98] | 8.1 [4.7, 12.5] | 260 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.528 [0.38, 0.68] | 1.000 [1.00, 1.00] | 0.691 [0.56, 0.81] | 0.849 [0.76, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.769 [0.61, 0.94] | 0.995 [0.99, 1.00] | 0.868 [0.76, 0.97] | 0.940 [0.88, 0.98] | 218 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.788 [0.68, 0.89] | 0.907 [0.86, 0.94] | 0.844 [0.78, 0.90] | 0.881 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.415 [0.28, 0.59] | 0.815 [0.65, 0.97] | 0.550 [0.40, 0.71] | 0.683 [0.53, 0.83] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.564 [0.41, 0.75] | 0.703 [0.58, 0.82] | 0.626 [0.49, 0.77] | 0.670 [0.55, 0.79] | 154 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.642 [0.54, 0.76] | 0.727 [0.66, 0.80] | 0.682 [0.60, 0.76] | 0.708 [0.64, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.8 [3.0, 11.4] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-weighted-w10-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 13.7 [6.3, 23.6] | 215 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.065 [0.03, 0.10] | 0.910 [0.85, 0.95] | 22.2 [14.0, 31.7] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.991 [0.99, 0.99] | 0.958 [0.95, 0.97] | 0.974 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2030 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.992 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4318 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.994 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8957 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.847 [0.83, 0.86] | 0.833 [0.82, 0.85] | 0.840 [0.83, 0.85] | 0.836 [0.82, 0.85] | 1766 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.980 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.980 [0.97, 0.98] | 4264 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.943 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.940 [0.93, 0.94] | 0.938 [0.93, 0.94] | 8525 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.082 [0.07, 0.10] | 0.941 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1993 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.006 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.4 [0.3, 0.5] | 4310 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.036 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.6 [1.4, 1.9] | 8798 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.989 [0.98, 0.99] | 0.964 [0.96, 0.97] | 0.976 [0.97, 0.98] | 0.969 [0.96, 0.98] | 2042 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.994 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4306 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.995 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8802 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.831 [0.82, 0.85] | 0.826 [0.81, 0.84] | 0.829 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1750 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.976 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4227 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.939 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8340 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s2 | 0.089 [0.07, 0.11] | 0.946 [0.94, 0.96] | 1.3 [1.1, 1.5] | 2004 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10-s2 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4293 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10-s2 | 0.037 [0.03, 0.04] | 0.970 [0.97, 0.97] | 1.8 [1.5, 2.0] | 8658 / 8927 |
