# train-cs-sk-weighted-s1-dev

rules+gliner-cs-sk-weighted-s1 after training (train-cs-sk-weighted-s1).

Stage: dev · commit e44e907302 · 2026-10-12T05:22:36+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-weighted-s1 @ 113de09f06 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.889 [0.78, 0.97] | 1.000 [1.00, 1.00] | 0.941 [0.88, 0.99] | 0.976 [0.95, 0.99] | 22 / 22 |
| email | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.887 [0.85, 0.92] | 0.941 [0.92, 0.96] | 0.913 [0.89, 0.93] | 0.929 [0.91, 0.95] | 493 / 524 |
| phone | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.895 [0.86, 0.92] | 0.934 [0.91, 0.96] | 0.914 [0.89, 0.93] | 0.926 [0.90, 0.95] | 566 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.111 [0.02, 0.25] | 0.182 [0.04, 0.42] | 0.138 [0.03, 0.31] | 0.161 [0.04, 0.36] | 4 / 22 |
| email | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.851 [0.82, 0.88] | 0.903 [0.88, 0.92] | 0.876 [0.85, 0.90] | 0.892 [0.87, 0.91] | 473 / 524 |
| phone | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.819 [0.78, 0.85] | 0.860 [0.82, 0.90] | 0.839 [0.80, 0.87] | 0.851 [0.81, 0.88] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.365 [0.25, 0.45] | 0.273 [0.10, 0.55] | 0.9 [0.3, 1.7] | 6 / 22 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.042 [0.03, 0.06] | 0.924 [0.90, 0.94] | 5.1 [3.7, 6.7] | 484 / 524 |
| phone | rules+gliner-cs-sk-weighted-s1 | 0.318 [0.08, 0.62] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.098 [0.07, 0.13] | 0.881 [0.84, 0.91] | 5.8 [4.2, 7.6] | 534 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-s1 | 0.825 [0.73, 0.90] | 0.931 [0.90, 0.96] | 0.875 [0.81, 0.92] | 0.908 [0.87, 0.94] | 257 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-s1 | 0.792 [0.70, 0.86] | 0.884 [0.84, 0.92] | 0.836 [0.78, 0.88] | 0.864 [0.82, 0.90] | 244 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-s1 | 0.056 [0.03, 0.09] | 0.913 [0.87, 0.95] | 6.6 [3.5, 10.6] | 252 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.540 [0.40, 0.69] | 1.000 [1.00, 1.00] | 0.701 [0.57, 0.82] | 0.854 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.810 [0.64, 0.95] | 0.995 [0.98, 1.00] | 0.893 [0.78, 0.98] | 0.952 [0.90, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-weighted-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.812 [0.70, 0.90] | 0.907 [0.86, 0.95] | 0.857 [0.79, 0.91] | 0.886 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.460 [0.30, 0.64] | 0.852 [0.67, 1.00] | 0.597 [0.42, 0.76] | 0.728 [0.54, 0.87] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.597 [0.45, 0.76] | 0.703 [0.58, 0.83] | 0.646 [0.52, 0.79] | 0.679 [0.56, 0.80] | 154 / 219 |
| phone | rules+gliner-cs-sk-weighted-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.672 [0.57, 0.77] | 0.729 [0.66, 0.80] | 0.700 [0.62, 0.78] | 0.717 [0.65, 0.78] | 283 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 5.9 [2.7, 9.7] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-weighted-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.007 [0.00, 0.02] | 0.986 [0.97, 1.00] | 11.2 [5.8, 18.2] | 216 / 219 |
| phone | rules+gliner-cs-sk-weighted-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.062 [0.03, 0.10] | 0.915 [0.86, 0.95] | 18.8 [12.2, 26.9] | 355 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.995 [0.99, 1.00] | 0.956 [0.95, 0.96] | 0.975 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2026 / 2119 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.995 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4316 / 4353 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.996 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8954 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.848 [0.83, 0.86] | 0.831 [0.81, 0.85] | 0.839 [0.82, 0.85] | 0.834 [0.82, 0.85] | 1760 / 2119 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.983 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.980 [0.98, 0.98] | 4262 / 4353 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.944 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.940 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8518 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.086 [0.07, 0.10] | 0.934 [0.92, 0.95] | 1.0 [0.9, 1.2] | 1980 / 2119 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4310 / 4353 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8785 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.994 [0.99, 1.00] | 0.960 [0.95, 0.97] | 0.977 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2034 / 2118 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.995 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4306 / 4344 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.996 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.99, 0.99] | 8794 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.837 [0.82, 0.85] | 0.824 [0.81, 0.84] | 0.831 [0.81, 0.85] | 0.827 [0.81, 0.84] | 1746 / 2118 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.977 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4225 / 4344 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.940 [0.94, 0.95] | 0.934 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8334 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-s1 | 0.092 [0.07, 0.11] | 0.940 [0.93, 0.95] | 1.1 [1.0, 1.3] | 1991 / 2118 |
| email | rules+gliner-cs-sk-weighted-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-weighted-s1 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4292 / 4344 |
| any | rules+gliner-cs-sk-weighted-s1 | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8644 / 8927 |
