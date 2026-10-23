# train-cs-sk-focal-more-s1-dev

rules+gliner-cs-sk-focal-more-s1 after training (train-cs-sk-focal-more-s1).

Stage: dev · commit caf443dff4 · 2026-10-22T14:12:39+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-more-s1 @ d8427e8de8 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.805 [0.68, 0.92] | 1.000 [1.00, 1.00] | 0.892 [0.81, 0.96] | 0.954 [0.92, 0.98] | 22 / 22 |
| email | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.855 [0.81, 0.90] | 0.952 [0.93, 0.97] | 0.901 [0.87, 0.93] | 0.931 [0.91, 0.95] | 499 / 524 |
| phone | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.861 [0.82, 0.90] | 0.942 [0.92, 0.96] | 0.900 [0.87, 0.92] | 0.925 [0.90, 0.95] | 571 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.073 [0.00, 0.17] | 0.136 [0.00, 0.35] | 0.095 [0.00, 0.23] | 0.116 [0.00, 0.28] | 3 / 22 |
| email | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.815 [0.77, 0.86] | 0.910 [0.89, 0.93] | 0.860 [0.83, 0.89] | 0.890 [0.86, 0.91] | 477 / 524 |
| phone | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.784 [0.74, 0.83] | 0.866 [0.83, 0.90] | 0.823 [0.78, 0.86] | 0.848 [0.81, 0.88] | 525 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.385 [0.25, 0.50] | 0.227 [0.07, 0.47] | 1.6 [0.6, 2.8] | 5 / 22 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.035 [0.02, 0.05] | 0.929 [0.91, 0.95] | 6.9 [5.1, 9.0] | 487 / 524 |
| phone | rules+gliner-cs-sk-focal-more-s1 | 0.318 [0.08, 0.62] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.095 [0.06, 0.13] | 0.884 [0.85, 0.91] | 8.4 [6.2, 10.8] | 536 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.829 [0.74, 0.91] | 0.996 [0.99, 1.00] | 0.905 [0.85, 0.95] | 0.958 [0.93, 0.98] | 275 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.799 [0.71, 0.88] | 0.949 [0.91, 0.98] | 0.868 [0.81, 0.92] | 0.915 [0.87, 0.95] | 262 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.004 [0.00, 0.01] | 0.978 [0.94, 1.00] | 6.6 [3.3, 10.7] | 270 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.500 [0.37, 0.64] | 1.000 [1.00, 1.00] | 0.667 [0.54, 0.78] | 0.833 [0.74, 0.90] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.801 [0.63, 0.95] | 0.995 [0.98, 1.00] | 0.888 [0.77, 0.97] | 0.950 [0.89, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal-more-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.803 [0.69, 0.89] | 0.907 [0.86, 0.95] | 0.852 [0.78, 0.90] | 0.884 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.411 [0.27, 0.56] | 0.852 [0.67, 1.00] | 0.554 [0.38, 0.71] | 0.701 [0.52, 0.85] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.603 [0.46, 0.75] | 0.722 [0.61, 0.83] | 0.657 [0.54, 0.78] | 0.694 [0.58, 0.80] | 158 / 219 |
| phone | rules+gliner-cs-sk-focal-more-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.666 [0.56, 0.76] | 0.740 [0.68, 0.80] | 0.701 [0.63, 0.77] | 0.724 [0.66, 0.78] | 287 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 7.2 [3.5, 11.9] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-more-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 10.9 [6.0, 17.9] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-more-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 19.9 [13.4, 28.5] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.984 [0.98, 0.99] | 0.961 [0.95, 0.97] | 0.973 [0.97, 0.98] | 0.966 [0.96, 0.97] | 2037 / 2119 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.992 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.987 [0.98, 0.99] | 4290 / 4353 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.992 [0.99, 0.99] | 0.983 [0.98, 0.99] | 0.987 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8939 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.827 [0.81, 0.84] | 0.826 [0.81, 0.84] | 0.827 [0.81, 0.84] | 0.826 [0.81, 0.84] | 1750 / 2119 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.979 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4234 / 4353 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.937 [0.93, 0.94] | 0.932 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8481 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.080 [0.07, 0.09] | 0.932 [0.92, 0.94] | 1.3 [1.1, 1.5] | 1976 / 2119 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.011 [0.01, 0.01] | 0.983 [0.98, 0.99] | 0.4 [0.2, 0.5] | 4279 / 4353 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.037 [0.03, 0.04] | 0.962 [0.96, 0.97] | 1.7 [1.5, 2.0] | 8750 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.974 [0.97, 0.98] | 0.964 [0.96, 0.97] | 0.969 [0.96, 0.97] | 0.966 [0.96, 0.97] | 2042 / 2118 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.994 [0.99, 1.00] | 0.988 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.989 [0.99, 0.99] | 4292 / 4344 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.991 [0.99, 0.99] | 0.985 [0.98, 0.99] | 0.988 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8791 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.807 [0.79, 0.82] | 0.818 [0.80, 0.83] | 0.813 [0.80, 0.83] | 0.816 [0.80, 0.83] | 1733 / 2118 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.973 [0.97, 0.98] | 0.967 [0.96, 0.97] | 0.970 [0.96, 0.98] | 0.969 [0.96, 0.97] | 4202 / 4344 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.931 [0.93, 0.94] | 0.930 [0.92, 0.94] | 0.930 [0.93, 0.94] | 0.930 [0.92, 0.94] | 8301 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s1 | 0.088 [0.07, 0.11] | 0.939 [0.93, 0.95] | 1.6 [1.3, 1.8] | 1988 / 2118 |
| email | rules+gliner-cs-sk-focal-more-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-more-s1 | 0.008 [0.01, 0.01] | 0.985 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4278 / 4344 |
| any | rules+gliner-cs-sk-focal-more-s1 | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 2.1 [1.8, 2.4] | 8627 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.901 [0.84, 0.95] | 0.983 [0.96, 1.00] | 0.941 [0.90, 0.97] | 0.966 [0.94, 0.98] | 293 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.809 [0.75, 0.86] | 0.883 [0.83, 0.93] | 0.844 [0.79, 0.89] | 0.867 [0.82, 0.91] | 263 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.026 [0.01, 0.05] | 0.906 [0.86, 0.94] | 5.2 [3.1, 7.5] | 270 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.987 [0.97, 1.00] | 0.962 [0.93, 0.98] | 0.974 [0.96, 0.99] | 0.967 [0.94, 0.98] | 381 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.987 [0.97, 1.00] | 0.962 [0.93, 0.98] | 0.974 [0.96, 0.99] | 0.967 [0.94, 0.98] | 381 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s1 | 0.044 [0.02, 0.08] | 0.962 [0.93, 0.98] | 0.4 [0.1, 0.9] | 381 / 396 |
