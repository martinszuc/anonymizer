# train-cs-sk-focal-more-dev

rules+gliner-cs-sk-focal-more after training (train-cs-sk-focal-more).

Stage: dev · commit 2c6672c62a · 2026-10-22T12:29:32+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-more @ c65dbc7ab2 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.844 [0.73, 0.95] | 0.955 [0.82, 1.00] | 0.896 [0.80, 0.96] | 0.930 [0.82, 0.98] | 21 / 22 |
| email | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more | 0.852 [0.81, 0.89] | 0.952 [0.93, 0.97] | 0.899 [0.87, 0.93] | 0.930 [0.91, 0.95] | 499 / 524 |
| phone | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more | 0.863 [0.82, 0.90] | 0.937 [0.91, 0.96] | 0.898 [0.87, 0.92] | 0.921 [0.90, 0.94] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.125 [0.03, 0.26] | 0.182 [0.04, 0.39] | 0.148 [0.03, 0.30] | 0.167 [0.04, 0.35] | 4 / 22 |
| email | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more | 0.816 [0.78, 0.85] | 0.914 [0.89, 0.93] | 0.862 [0.83, 0.89] | 0.893 [0.87, 0.91] | 479 / 524 |
| phone | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more | 0.795 [0.75, 0.83] | 0.870 [0.83, 0.90] | 0.831 [0.79, 0.86] | 0.854 [0.82, 0.88] | 527 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.394 [0.27, 0.52] | 0.227 [0.06, 0.46] | 1.0 [0.3, 1.9] | 5 / 22 |
| email | rules+gliner-cs-sk-focal-more | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more | 0.037 [0.02, 0.05] | 0.929 [0.91, 0.95] | 6.9 [5.0, 8.8] | 487 / 524 |
| phone | rules+gliner-cs-sk-focal-more | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more | 0.098 [0.06, 0.13] | 0.884 [0.85, 0.92] | 7.8 [5.7, 10.0] | 536 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.824 [0.74, 0.90] | 0.993 [0.98, 1.00] | 0.901 [0.85, 0.95] | 0.954 [0.93, 0.98] | 274 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.788 [0.71, 0.86] | 0.942 [0.91, 0.98] | 0.858 [0.80, 0.91] | 0.907 [0.87, 0.94] | 260 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.009 [0.00, 0.02] | 0.975 [0.94, 1.00] | 7.0 [3.7, 10.8] | 269 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.509 [0.37, 0.66] | 1.000 [1.00, 1.00] | 0.675 [0.54, 0.79] | 0.838 [0.75, 0.91] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more | 0.755 [0.60, 0.91] | 0.995 [0.99, 1.00] | 0.859 [0.75, 0.95] | 0.936 [0.88, 0.98] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal-more | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more | 0.780 [0.68, 0.87] | 0.907 [0.86, 0.95] | 0.839 [0.77, 0.89] | 0.879 [0.84, 0.91] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.400 [0.26, 0.55] | 0.815 [0.64, 0.96] | 0.537 [0.38, 0.68] | 0.675 [0.51, 0.81] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more | 0.565 [0.42, 0.74] | 0.717 [0.61, 0.83] | 0.632 [0.51, 0.77] | 0.680 [0.57, 0.80] | 157 / 219 |
| phone | rules+gliner-cs-sk-focal-more | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more | 0.639 [0.54, 0.76] | 0.735 [0.68, 0.80] | 0.683 [0.61, 0.77] | 0.713 [0.65, 0.78] | 285 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 7.1 [3.4, 11.8] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-more | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more | 0.008 [0.00, 0.02] | 0.982 [0.96, 1.00] | 13.6 [6.4, 22.4] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-more | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more | 0.065 [0.04, 0.10] | 0.910 [0.86, 0.95] | 22.5 [13.5, 32.1] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.985 [0.98, 0.99] | 0.961 [0.95, 0.97] | 0.973 [0.97, 0.98] | 0.966 [0.96, 0.97] | 2036 / 2119 |
| email | rules+gliner-cs-sk-focal-more | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-more | 0.990 [0.99, 0.99] | 0.989 [0.99, 0.99] | 0.989 [0.99, 0.99] | 0.989 [0.99, 0.99] | 4303 / 4353 |
| any | rules+gliner-cs-sk-focal-more | 0.992 [0.99, 0.99] | 0.984 [0.98, 0.99] | 0.988 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8949 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.834 [0.82, 0.85] | 0.830 [0.81, 0.85] | 0.832 [0.82, 0.85] | 0.831 [0.81, 0.85] | 1758 / 2119 |
| email | rules+gliner-cs-sk-focal-more | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-more | 0.977 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.975 [0.97, 0.98] | 4244 / 4353 |
| any | rules+gliner-cs-sk-focal-more | 0.938 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8498 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.081 [0.06, 0.10] | 0.936 [0.93, 0.95] | 1.3 [1.0, 1.5] | 1984 / 2119 |
| email | rules+gliner-cs-sk-focal-more | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-more | 0.010 [0.01, 0.01] | 0.986 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4290 / 4353 |
| any | rules+gliner-cs-sk-focal-more | 0.037 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.8 [1.5, 2.0] | 8769 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 0.970 [0.96, 0.98] | 0.967 [0.96, 0.97] | 2043 / 2118 |
| email | rules+gliner-cs-sk-focal-more | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-more | 0.991 [0.99, 0.99] | 0.988 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.989 [0.99, 0.99] | 4292 / 4344 |
| any | rules+gliner-cs-sk-focal-more | 0.991 [0.99, 0.99] | 0.985 [0.98, 0.99] | 0.988 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8793 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.810 [0.79, 0.83] | 0.818 [0.80, 0.83] | 0.814 [0.80, 0.83] | 0.816 [0.80, 0.83] | 1732 / 2118 |
| email | rules+gliner-cs-sk-focal-more | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-more | 0.971 [0.96, 0.98] | 0.968 [0.96, 0.97] | 0.969 [0.96, 0.97] | 0.968 [0.96, 0.97] | 4204 / 4344 |
| any | rules+gliner-cs-sk-focal-more | 0.930 [0.92, 0.94] | 0.930 [0.92, 0.94] | 0.930 [0.92, 0.94] | 0.930 [0.92, 0.94] | 8301 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more | 0.089 [0.07, 0.11] | 0.944 [0.93, 0.95] | 1.6 [1.4, 1.9] | 1999 / 2118 |
| email | rules+gliner-cs-sk-focal-more | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-more | 0.009 [0.01, 0.01] | 0.985 [0.98, 0.99] | 0.4 [0.3, 0.6] | 4277 / 4344 |
| any | rules+gliner-cs-sk-focal-more | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 2.2 [1.9, 2.5] | 8637 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.910 [0.86, 0.95] | 0.987 [0.97, 1.00] | 0.947 [0.91, 0.97] | 0.970 [0.95, 0.98] | 294 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.817 [0.76, 0.87] | 0.886 [0.84, 0.93] | 0.850 [0.80, 0.89] | 0.871 [0.82, 0.91] | 264 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.025 [0.01, 0.04] | 0.909 [0.87, 0.94] | 4.8 [2.9, 7.0] | 271 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.990 [0.98, 1.00] | 0.962 [0.93, 0.99] | 0.976 [0.96, 0.99] | 0.968 [0.94, 0.99] | 381 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.990 [0.98, 1.00] | 0.962 [0.93, 0.99] | 0.976 [0.96, 0.99] | 0.968 [0.94, 0.99] | 381 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more | 0.044 [0.02, 0.08] | 0.962 [0.93, 0.99] | 0.3 [0.0, 0.7] | 381 / 396 |
