# train-cs-sk-xlmr-ce-s1-dev

rules+xlmr-cs-sk-ce-s1 after training (train-cs-sk-xlmr-ce-s1).

Stage: dev · commit 156b8b704e · 2026-10-21T01:05:03+00:00 · seed 1, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce-s1 @ 61a0cb303e · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.903 [0.80, 1.00] | 0.955 [0.83, 1.00] | 0.928 [0.85, 0.98] | 0.944 [0.85, 0.99] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.938 [0.90, 0.96] | 0.941 [0.92, 0.96] | 0.939 [0.92, 0.96] | 0.940 [0.92, 0.96] | 493 / 524 |
| phone | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.940 [0.91, 0.96] | 0.932 [0.91, 0.96] | 0.936 [0.91, 0.95] | 0.934 [0.91, 0.95] | 565 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.194 [0.07, 0.36] | 0.273 [0.10, 0.53] | 0.226 [0.08, 0.43] | 0.252 [0.09, 0.48] | 6 / 22 |
| email | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.892 [0.86, 0.92] | 0.899 [0.88, 0.92] | 0.895 [0.87, 0.92] | 0.897 [0.87, 0.92] | 471 / 524 |
| phone | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.864 [0.82, 0.90] | 0.860 [0.82, 0.90] | 0.862 [0.82, 0.89] | 0.861 [0.82, 0.89] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.334 [0.21, 0.43] | 0.364 [0.17, 0.64] | 0.7 [0.2, 1.3] | 8 / 22 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.037 [0.02, 0.05] | 0.922 [0.90, 0.94] | 2.5 [1.5, 3.8] | 483 / 524 |
| phone | rules+xlmr-cs-sk-ce-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.091 [0.06, 0.12] | 0.883 [0.84, 0.91] | 3.2 [1.9, 4.8] | 535 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-s1 | 0.888 [0.80, 0.96] | 0.891 [0.84, 0.94] | 0.890 [0.84, 0.93] | 0.891 [0.85, 0.93] | 246 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-s1 | 0.863 [0.77, 0.94] | 0.866 [0.81, 0.91] | 0.864 [0.81, 0.91] | 0.865 [0.81, 0.91] | 239 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-s1 | 0.096 [0.06, 0.14] | 0.873 [0.81, 0.92] | 4.1 [1.3, 8.2] | 241 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.509 [0.34, 0.71] | 1.000 [1.00, 1.00] | 0.675 [0.50, 0.83] | 0.839 [0.72, 0.93] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.770 [0.61, 0.91] | 0.931 [0.82, 1.00] | 0.843 [0.73, 0.93] | 0.894 [0.79, 0.96] | 204 / 219 |
| phone | rules+xlmr-cs-sk-ce-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.784 [0.68, 0.88] | 0.874 [0.81, 0.93] | 0.827 [0.76, 0.88] | 0.854 [0.80, 0.90] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.415 [0.25, 0.62] | 0.815 [0.62, 0.96] | 0.550 [0.37, 0.74] | 0.683 [0.50, 0.84] | 22 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.548 [0.40, 0.70] | 0.676 [0.55, 0.79] | 0.605 [0.47, 0.72] | 0.646 [0.52, 0.76] | 148 / 219 |
| phone | rules+xlmr-cs-sk-ce-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.633 [0.52, 0.74] | 0.711 [0.64, 0.78] | 0.670 [0.59, 0.75] | 0.694 [0.63, 0.76] | 276 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.013 [0.00, 0.04] | 0.963 [0.87, 1.00] | 7.6 [2.5, 14.5] | 26 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.058 [0.01, 0.15] | 0.863 [0.73, 0.97] | 10.7 [5.8, 18.0] | 189 / 219 |
| phone | rules+xlmr-cs-sk-ce-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.085 [0.05, 0.13] | 0.843 [0.77, 0.90] | 20.1 [12.2, 30.4] | 327 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.971 [0.96, 0.98] | 0.997 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.991 [0.99, 0.99] | 2112 / 2119 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.998 [1.00, 1.00] | 0.997 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.997 [1.00, 1.00] | 4339 / 4353 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.992 [0.99, 0.99] | 0.996 [0.99, 1.00] | 0.994 [0.99, 0.99] | 0.995 [0.99, 1.00] | 9059 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.851 [0.83, 0.87] | 0.890 [0.88, 0.90] | 0.870 [0.86, 0.88] | 0.882 [0.87, 0.90] | 1886 / 2119 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.986 [0.98, 0.99] | 0.984 [0.98, 0.99] | 0.985 [0.98, 0.99] | 0.984 [0.98, 0.99] | 4284 / 4353 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.945 [0.94, 0.95] | 0.953 [0.95, 0.96] | 0.949 [0.94, 0.95] | 0.951 [0.95, 0.96] | 8665 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.004 [0.00, 0.01] | 0.993 [0.99, 1.00] | 1.4 [1.2, 1.6] | 2104 / 2119 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.003 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.2 [0.1, 0.3] | 4327 / 4353 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.008 [0.01, 0.01] | 0.981 [0.98, 0.98] | 1.7 [1.5, 2.0] | 8926 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.969 [0.96, 0.98] | 0.998 [1.00, 1.00] | 0.983 [0.98, 0.99] | 0.992 [0.99, 0.99] | 2113 / 2118 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.998 [1.00, 1.00] | 0.997 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.997 [0.99, 1.00] | 4329 / 4344 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.991 [0.99, 0.99] | 0.996 [0.99, 1.00] | 0.994 [0.99, 0.99] | 0.995 [0.99, 1.00] | 8892 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.833 [0.82, 0.85] | 0.878 [0.86, 0.89] | 0.855 [0.84, 0.87] | 0.868 [0.85, 0.88] | 1859 / 2118 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.980 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.979 [0.97, 0.98] | 4250 / 4344 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.939 [0.93, 0.94] | 0.949 [0.94, 0.95] | 0.944 [0.94, 0.95] | 0.947 [0.94, 0.95] | 8469 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s1 | 0.003 [0.00, 0.00] | 0.992 [0.99, 1.00] | 1.5 [1.3, 1.7] | 2102 / 2118 |
| email | rules+xlmr-cs-sk-ce-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce-s1 | 0.003 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.3 [0.2, 0.4] | 4317 / 4344 |
| any | rules+xlmr-cs-sk-ce-s1 | 0.007 [0.01, 0.01] | 0.984 [0.98, 0.99] | 1.9 [1.6, 2.1] | 8780 / 8927 |
