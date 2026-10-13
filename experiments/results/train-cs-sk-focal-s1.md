# train-cs-sk-focal-s1-dev

rules+gliner-cs-sk-focal-s1 after training (train-cs-sk-focal-s1).

Stage: dev · commit e44e907302 · 2026-10-12T04:05:07+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-s1 @ f734df43e9 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.821 [0.70, 0.93] | 1.000 [1.00, 1.00] | 0.901 [0.82, 0.96] | 0.958 [0.92, 0.99] | 22 / 22 |
| email | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-s1 | 0.860 [0.82, 0.90] | 0.950 [0.93, 0.97] | 0.903 [0.88, 0.93] | 0.931 [0.91, 0.95] | 498 / 524 |
| phone | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-s1 | 0.867 [0.83, 0.90] | 0.942 [0.92, 0.96] | 0.903 [0.88, 0.93] | 0.926 [0.90, 0.95] | 571 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.103 [0.02, 0.22] | 0.182 [0.04, 0.42] | 0.131 [0.03, 0.29] | 0.158 [0.04, 0.35] | 4 / 22 |
| email | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-s1 | 0.820 [0.78, 0.86] | 0.905 [0.88, 0.93] | 0.860 [0.83, 0.89] | 0.886 [0.86, 0.91] | 474 / 524 |
| phone | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-s1 | 0.790 [0.74, 0.83] | 0.861 [0.82, 0.90] | 0.824 [0.79, 0.86] | 0.846 [0.81, 0.88] | 522 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.365 [0.25, 0.45] | 0.273 [0.10, 0.55] | 1.4 [0.5, 2.5] | 6 / 22 |
| email | rules+gliner-cs-sk-focal-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-s1 | 0.034 [0.02, 0.05] | 0.929 [0.91, 0.95] | 6.5 [4.8, 8.4] | 487 / 524 |
| phone | rules+gliner-cs-sk-focal-s1 | 0.318 [0.08, 0.62] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-s1 | 0.092 [0.06, 0.12] | 0.886 [0.85, 0.92] | 7.8 [5.8, 9.9] | 537 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-s1 | 0.791 [0.71, 0.86] | 0.957 [0.92, 0.98] | 0.866 [0.81, 0.91] | 0.918 [0.88, 0.94] | 264 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-s1 | 0.764 [0.69, 0.83] | 0.917 [0.87, 0.95] | 0.834 [0.78, 0.88] | 0.881 [0.84, 0.92] | 253 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-s1 | 0.036 [0.02, 0.06] | 0.938 [0.89, 0.97] | 8.8 [5.5, 12.8] | 259 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.518 [0.38, 0.67] | 1.000 [1.00, 1.00] | 0.683 [0.55, 0.80] | 0.843 [0.75, 0.91] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-s1 | 0.808 [0.64, 0.95] | 0.995 [0.98, 1.00] | 0.892 [0.78, 0.97] | 0.951 [0.90, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-s1 | 0.808 [0.70, 0.89] | 0.910 [0.86, 0.95] | 0.856 [0.78, 0.91] | 0.887 [0.84, 0.92] | 353 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.426 [0.27, 0.60] | 0.852 [0.67, 1.00] | 0.568 [0.39, 0.73] | 0.710 [0.52, 0.86] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-s1 | 0.589 [0.44, 0.75] | 0.699 [0.58, 0.82] | 0.639 [0.51, 0.78] | 0.673 [0.55, 0.80] | 153 / 219 |
| phone | rules+gliner-cs-sk-focal-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-s1 | 0.660 [0.56, 0.76] | 0.727 [0.65, 0.80] | 0.692 [0.61, 0.77] | 0.713 [0.64, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.8 [3.1, 11.4] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-s1 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 11.3 [5.9, 18.2] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-s1 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 19.8 [13.1, 28.1] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.993 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.975 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2030 / 2119 |
| email | rules+gliner-cs-sk-focal-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-s1 | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4318 / 4353 |
| any | rules+gliner-cs-sk-focal-s1 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8958 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.850 [0.83, 0.86] | 0.835 [0.82, 0.85] | 0.843 [0.83, 0.86] | 0.838 [0.82, 0.85] | 1770 / 2119 |
| email | rules+gliner-cs-sk-focal-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-s1 | 0.981 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.980 [0.98, 0.98] | 0.980 [0.97, 0.98] | 4263 / 4353 |
| any | rules+gliner-cs-sk-focal-s1 | 0.943 [0.94, 0.95] | 0.938 [0.93, 0.94] | 0.940 [0.94, 0.95] | 0.939 [0.93, 0.94] | 8528 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.083 [0.07, 0.10] | 0.939 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1989 / 2119 |
| email | rules+gliner-cs-sk-focal-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-s1 | 0.006 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.4 [0.3, 0.5] | 4311 / 4353 |
| any | rules+gliner-cs-sk-focal-s1 | 0.036 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8795 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.992 [0.99, 1.00] | 0.964 [0.96, 0.97] | 0.978 [0.97, 0.98] | 0.970 [0.96, 0.98] | 2042 / 2118 |
| email | rules+gliner-cs-sk-focal-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-s1 | 0.995 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4305 / 4344 |
| any | rules+gliner-cs-sk-focal-s1 | 0.996 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8802 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.835 [0.82, 0.85] | 0.827 [0.81, 0.84] | 0.831 [0.81, 0.85] | 0.828 [0.81, 0.84] | 1751 / 2118 |
| email | rules+gliner-cs-sk-focal-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-s1 | 0.977 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4228 / 4344 |
| any | rules+gliner-cs-sk-focal-s1 | 0.940 [0.93, 0.95] | 0.935 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.936 [0.93, 0.94] | 8343 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-s1 | 0.090 [0.07, 0.11] | 0.944 [0.93, 0.95] | 1.2 [1.0, 1.4] | 2000 / 2118 |
| email | rules+gliner-cs-sk-focal-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-s1 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4293 / 4344 |
| any | rules+gliner-cs-sk-focal-s1 | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.6 [1.4, 1.9] | 8654 / 8927 |
