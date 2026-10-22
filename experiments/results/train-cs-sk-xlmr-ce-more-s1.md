# train-cs-sk-xlmr-ce-more-s1-dev

rules+xlmr-cs-sk-ce-more-s1 after training (train-cs-sk-xlmr-ce-more-s1).

Stage: dev · commit 0b2364ff37 · 2026-10-21T21:51:38+00:00 · seed 1, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce-more-s1 @ 2ca9ea1df1 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.935 [0.83, 1.00] | 0.955 [0.83, 1.00] | 0.945 [0.87, 1.00] | 0.951 [0.86, 1.00] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.916 [0.88, 0.94] | 0.943 [0.92, 0.96] | 0.929 [0.91, 0.95] | 0.937 [0.92, 0.95] | 494 / 524 |
| phone | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.923 [0.90, 0.95] | 0.934 [0.91, 0.96] | 0.929 [0.91, 0.95] | 0.932 [0.91, 0.95] | 566 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.226 [0.09, 0.43] | 0.318 [0.12, 0.60] | 0.264 [0.11, 0.49] | 0.294 [0.12, 0.55] | 7 / 22 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.872 [0.84, 0.91] | 0.895 [0.87, 0.92] | 0.883 [0.85, 0.91] | 0.890 [0.86, 0.92] | 469 / 524 |
| phone | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.848 [0.81, 0.88] | 0.858 [0.81, 0.90] | 0.853 [0.81, 0.89] | 0.856 [0.81, 0.89] | 520 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.348 [0.20, 0.47] | 0.409 [0.20, 0.69] | 0.6 [0.1, 1.2] | 9 / 22 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.035 [0.02, 0.05] | 0.927 [0.90, 0.95] | 3.9 [2.6, 5.3] | 486 / 524 |
| phone | rules+xlmr-cs-sk-ce-more-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.092 [0.06, 0.13] | 0.889 [0.85, 0.92] | 4.4 [2.9, 6.0] | 539 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.886 [0.80, 0.96] | 0.986 [0.97, 1.00] | 0.933 [0.88, 0.97] | 0.964 [0.94, 0.98] | 272 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.856 [0.76, 0.93] | 0.949 [0.90, 0.99] | 0.900 [0.84, 0.95] | 0.929 [0.88, 0.97] | 262 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.016 [0.00, 0.04] | 0.967 [0.92, 1.00] | 4.6 [1.7, 8.4] | 267 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.528 [0.37, 0.70] | 1.000 [1.00, 1.00] | 0.691 [0.54, 0.83] | 0.849 [0.75, 0.92] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.793 [0.62, 0.94] | 0.931 [0.82, 1.00] | 0.857 [0.74, 0.95] | 0.900 [0.80, 0.97] | 204 / 219 |
| phone | rules+xlmr-cs-sk-ce-more-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.799 [0.69, 0.89] | 0.874 [0.81, 0.93] | 0.834 [0.76, 0.88] | 0.858 [0.80, 0.90] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.415 [0.26, 0.60] | 0.815 [0.62, 0.96] | 0.550 [0.38, 0.72] | 0.683 [0.50, 0.84] | 22 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.614 [0.46, 0.77] | 0.703 [0.59, 0.81] | 0.655 [0.54, 0.77] | 0.683 [0.58, 0.79] | 154 / 219 |
| phone | rules+xlmr-cs-sk-ce-more-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.676 [0.57, 0.77] | 0.727 [0.67, 0.79] | 0.701 [0.63, 0.77] | 0.716 [0.66, 0.77] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.014 [0.00, 0.05] | 0.963 [0.87, 1.00] | 7.0 [2.6, 12.6] | 26 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce-more-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.050 [0.00, 0.13] | 0.909 [0.78, 0.99] | 9.8 [5.0, 16.7] | 199 / 219 |
| phone | rules+xlmr-cs-sk-ce-more-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.082 [0.05, 0.12] | 0.869 [0.80, 0.93] | 18.5 [11.8, 27.2] | 337 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.995 [0.99, 1.00] | 0.999 [1.00, 1.00] | 0.997 [0.99, 1.00] | 0.998 [1.00, 1.00] | 2116 / 2119 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.999 [1.00, 1.00] | 0.997 [1.00, 1.00] | 0.998 [1.00, 1.00] | 0.998 [1.00, 1.00] | 4341 / 4353 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.998 [1.00, 1.00] | 0.996 [1.00, 1.00] | 0.997 [1.00, 1.00] | 0.997 [1.00, 1.00] | 9064 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.873 [0.86, 0.89] | 0.891 [0.88, 0.90] | 0.882 [0.87, 0.89] | 0.887 [0.87, 0.90] | 1888 / 2119 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.986 [0.98, 0.99] | 0.984 [0.98, 0.99] | 0.985 [0.98, 0.99] | 0.985 [0.98, 0.99] | 4284 / 4353 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.950 [0.95, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.95, 0.96] | 0.952 [0.95, 0.96] | 8667 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.001 [0.00, 0.00] | 0.994 [0.99, 1.00] | 1.1 [0.9, 1.3] | 2107 / 2119 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.003 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.2 [0.1, 0.3] | 4328 / 4353 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.007 [0.01, 0.01] | 0.982 [0.98, 0.98] | 1.4 [1.1, 1.6] | 8930 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.997 [0.99, 1.00] | 0.997 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.997 [0.99, 1.00] | 2111 / 2118 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.999 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.998 [1.00, 1.00] | 0.997 [1.00, 1.00] | 4328 / 4344 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.998 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.996 [1.00, 1.00] | 8888 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.859 [0.84, 0.87] | 0.877 [0.86, 0.89] | 0.868 [0.85, 0.88] | 0.874 [0.86, 0.89] | 1858 / 2118 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.982 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.980 [0.97, 0.98] | 4254 / 4344 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.947 [0.94, 0.95] | 0.949 [0.94, 0.95] | 0.948 [0.94, 0.95] | 0.949 [0.94, 0.95] | 8472 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s1 | 0.004 [0.00, 0.01] | 0.992 [0.99, 1.00] | 1.1 [0.9, 1.3] | 2100 / 2118 |
| email | rules+xlmr-cs-sk-ce-more-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.002 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.2 [0.2, 0.3] | 4318 / 4344 |
| any | rules+xlmr-cs-sk-ce-more-s1 | 0.007 [0.01, 0.01] | 0.983 [0.98, 0.99] | 1.4 [1.2, 1.7] | 8779 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.954 [0.92, 0.98] | 0.983 [0.97, 1.00] | 0.968 [0.95, 0.98] | 0.977 [0.96, 0.99] | 293 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.862 [0.81, 0.91] | 0.879 [0.83, 0.92] | 0.870 [0.82, 0.91] | 0.876 [0.82, 0.92] | 262 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.026 [0.01, 0.04] | 0.913 [0.87, 0.95] | 2.7 [1.4, 4.1] | 272 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.990 [0.98, 1.00] | 0.960 [0.93, 0.98] | 0.974 [0.96, 0.99] | 0.965 [0.94, 0.98] | 380 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.990 [0.98, 1.00] | 0.960 [0.93, 0.98] | 0.974 [0.96, 0.99] | 0.965 [0.94, 0.98] | 380 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s1 | 0.048 [0.02, 0.08] | 0.960 [0.93, 0.98] | 0.3 [0.0, 0.8] | 380 / 396 |
