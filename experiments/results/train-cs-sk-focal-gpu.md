# train-cs-sk-focal-gpu-dev

rules+gliner-cs-sk-focal-gpu after training (train-cs-sk-focal-gpu).

Stage: dev · commit 0211b3728e · 2026-10-14T20:20:10+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-gpu @ 24309ca531 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.821 [0.70, 0.94] | 1.000 [1.00, 1.00] | 0.901 [0.83, 0.97] | 0.958 [0.92, 0.99] | 22 / 22 |
| email | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu | 0.859 [0.82, 0.90] | 0.945 [0.92, 0.96] | 0.900 [0.87, 0.92] | 0.926 [0.90, 0.94] | 495 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu | 0.867 [0.83, 0.90] | 0.937 [0.91, 0.96] | 0.900 [0.87, 0.92] | 0.922 [0.90, 0.94] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.103 [0.02, 0.22] | 0.182 [0.04, 0.40] | 0.131 [0.03, 0.29] | 0.158 [0.03, 0.34] | 4 / 22 |
| email | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu | 0.821 [0.78, 0.86] | 0.903 [0.88, 0.92] | 0.860 [0.83, 0.88] | 0.885 [0.86, 0.91] | 473 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu | 0.791 [0.75, 0.83] | 0.860 [0.82, 0.89] | 0.824 [0.79, 0.86] | 0.845 [0.80, 0.88] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.377 [0.27, 0.48] | 0.273 [0.09, 0.52] | 1.4 [0.4, 2.4] | 6 / 22 |
| email | rules+gliner-cs-sk-focal-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu | 0.038 [0.03, 0.05] | 0.924 [0.90, 0.94] | 6.5 [4.8, 8.2] | 484 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu | 0.097 [0.07, 0.13] | 0.881 [0.84, 0.91] | 7.8 [5.7, 9.8] | 534 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu | 0.821 [0.74, 0.89] | 0.953 [0.92, 0.98] | 0.882 [0.83, 0.92] | 0.923 [0.89, 0.95] | 263 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu | 0.792 [0.71, 0.87] | 0.913 [0.87, 0.95] | 0.849 [0.80, 0.89] | 0.886 [0.85, 0.92] | 252 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu | 0.036 [0.02, 0.05] | 0.935 [0.89, 0.97] | 7.3 [3.9, 11.1] | 258 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu | 0.776 [0.63, 0.92] | 0.995 [0.99, 1.00] | 0.872 [0.77, 0.96] | 0.942 [0.89, 0.98] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu | 0.796 [0.69, 0.89] | 0.907 [0.86, 0.95] | 0.848 [0.78, 0.90] | 0.882 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.451 [0.30, 0.62] | 0.852 [0.69, 0.97] | 0.590 [0.43, 0.75] | 0.723 [0.56, 0.85] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu | 0.581 [0.44, 0.74] | 0.722 [0.61, 0.84] | 0.644 [0.52, 0.78] | 0.688 [0.57, 0.80] | 158 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu | 0.658 [0.56, 0.76] | 0.740 [0.68, 0.80] | 0.697 [0.62, 0.77] | 0.722 [0.66, 0.79] | 287 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.1 [3.0, 10.0] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-gpu | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu | 0.008 [0.00, 0.02] | 0.977 [0.95, 1.00] | 11.9 [6.4, 18.6] | 214 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu | 0.062 [0.03, 0.10] | 0.910 [0.86, 0.95] | 19.7 [13.0, 27.3] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.994 [0.99, 1.00] | 0.957 [0.95, 0.97] | 0.975 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2028 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu | 0.993 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4313 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu | 0.995 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8954 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.845 [0.83, 0.86] | 0.830 [0.81, 0.85] | 0.837 [0.82, 0.85] | 0.833 [0.82, 0.85] | 1758 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu | 0.980 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4256 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu | 0.942 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.937 [0.93, 0.94] | 8512 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.084 [0.07, 0.10] | 0.935 [0.92, 0.95] | 1.1 [0.9, 1.3] | 1982 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu | 0.007 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.4 [0.2, 0.5] | 4306 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8783 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.992 [0.99, 1.00] | 0.967 [0.96, 0.97] | 0.979 [0.97, 0.98] | 0.972 [0.97, 0.98] | 2047 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu | 0.993 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4305 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu | 0.995 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8806 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.832 [0.82, 0.85] | 0.825 [0.81, 0.84] | 0.828 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1748 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu | 0.973 [0.97, 0.98] | 0.972 [0.96, 0.98] | 0.972 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4220 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu | 0.937 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.935 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8332 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu | 0.089 [0.07, 0.11] | 0.947 [0.94, 0.96] | 1.3 [1.1, 1.5] | 2006 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu | 0.006 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4289 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu | 0.036 [0.03, 0.04] | 0.970 [0.97, 0.97] | 1.8 [1.5, 2.1] | 8656 / 8927 |
