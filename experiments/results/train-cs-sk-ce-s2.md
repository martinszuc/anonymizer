# train-cs-sk-ce-s2-dev

rules+gliner-cs-sk-ce-s2 after training (train-cs-sk-ce-s2).

Stage: dev · commit e44e907302 · 2026-10-12T06:36:43+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-ce-s2 @ 90e2adaf08 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.871 [0.76, 0.97] | 0.864 [0.71, 1.00] | 0.867 [0.75, 0.97] | 0.865 [0.73, 0.98] | 19 / 22 |
| email | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-s2 | 0.911 [0.88, 0.94] | 0.937 [0.92, 0.96] | 0.924 [0.90, 0.94] | 0.932 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-s2 | 0.915 [0.88, 0.95] | 0.922 [0.89, 0.95] | 0.919 [0.89, 0.94] | 0.921 [0.89, 0.95] | 559 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.097 [0.00, 0.25] | 0.136 [0.00, 0.33] | 0.113 [0.00, 0.28] | 0.126 [0.00, 0.31] | 3 / 22 |
| email | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-s2 | 0.874 [0.84, 0.91] | 0.899 [0.87, 0.92] | 0.886 [0.86, 0.91] | 0.894 [0.87, 0.92] | 471 / 524 |
| phone | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-s2 | 0.844 [0.80, 0.88] | 0.855 [0.81, 0.89] | 0.849 [0.81, 0.88] | 0.853 [0.81, 0.89] | 518 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.440 [0.31, 0.54] | 0.227 [0.07, 0.44] | 1.0 [0.3, 1.8] | 5 / 22 |
| email | rules+gliner-cs-sk-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-s2 | 0.048 [0.03, 0.06] | 0.914 [0.89, 0.94] | 3.7 [2.4, 5.2] | 479 / 524 |
| phone | rules+gliner-cs-sk-ce-s2 | 0.328 [0.09, 0.64] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-s2 | 0.111 [0.08, 0.15] | 0.871 [0.83, 0.90] | 4.6 [3.1, 6.7] | 528 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-s2 | 0.851 [0.76, 0.92] | 0.917 [0.87, 0.95] | 0.883 [0.83, 0.92] | 0.903 [0.86, 0.93] | 253 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-s2 | 0.814 [0.73, 0.89] | 0.873 [0.83, 0.92] | 0.843 [0.79, 0.89] | 0.861 [0.81, 0.90] | 241 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-s2 | 0.070 [0.04, 0.10] | 0.895 [0.84, 0.94] | 5.5 [2.6, 9.2] | 247 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.549 [0.40, 0.70] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-s2 | 0.773 [0.62, 0.95] | 0.991 [0.98, 1.00] | 0.869 [0.76, 0.97] | 0.938 [0.89, 0.98] | 217 / 219 |
| phone | rules+gliner-cs-sk-ce-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-s2 | 0.790 [0.68, 0.89] | 0.905 [0.86, 0.94] | 0.843 [0.78, 0.90] | 0.879 [0.84, 0.91] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.451 [0.30, 0.62] | 0.852 [0.69, 1.00] | 0.590 [0.43, 0.75] | 0.723 [0.56, 0.87] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-s2 | 0.573 [0.41, 0.76] | 0.703 [0.58, 0.83] | 0.631 [0.49, 0.78] | 0.672 [0.55, 0.80] | 154 / 219 |
| phone | rules+gliner-cs-sk-ce-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-s2 | 0.654 [0.55, 0.77] | 0.729 [0.66, 0.80] | 0.689 [0.61, 0.78] | 0.713 [0.64, 0.79] | 283 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.1 [2.9, 10.0] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-ce-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-s2 | 0.009 [0.00, 0.02] | 0.982 [0.96, 1.00] | 13.6 [6.2, 23.4] | 215 / 219 |
| phone | rules+gliner-cs-sk-ce-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-s2 | 0.063 [0.03, 0.10] | 0.912 [0.86, 0.95] | 21.4 [13.5, 30.5] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.997 [0.99, 1.00] | 0.957 [0.95, 0.96] | 0.976 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2027 / 2119 |
| email | rules+gliner-cs-sk-ce-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-ce-s2 | 0.995 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.994 [0.99, 1.00] | 0.993 [0.99, 0.99] | 4317 / 4353 |
| any | rules+gliner-cs-sk-ce-s2 | 0.997 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8952 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.850 [0.83, 0.87] | 0.831 [0.81, 0.85] | 0.841 [0.83, 0.85] | 0.835 [0.82, 0.85] | 1761 / 2119 |
| email | rules+gliner-cs-sk-ce-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-s2 | 0.984 [0.98, 0.99] | 0.980 [0.97, 0.98] | 0.982 [0.98, 0.99] | 0.980 [0.98, 0.98] | 4264 / 4353 |
| any | rules+gliner-cs-sk-ce-s2 | 0.945 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8520 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.084 [0.07, 0.10] | 0.936 [0.92, 0.95] | 1.1 [0.9, 1.3] | 1983 / 2119 |
| email | rules+gliner-cs-sk-ce-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-s2 | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4308 / 4353 |
| any | rules+gliner-cs-sk-ce-s2 | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.4 [1.2, 1.7] | 8786 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.994 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2029 / 2118 |
| email | rules+gliner-cs-sk-ce-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-ce-s2 | 0.997 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.994 [0.99, 1.00] | 0.993 [0.99, 0.99] | 4307 / 4344 |
| any | rules+gliner-cs-sk-ce-s2 | 0.997 [1.00, 1.00] | 0.985 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8790 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.838 [0.82, 0.85] | 0.823 [0.81, 0.84] | 0.831 [0.81, 0.85] | 0.826 [0.81, 0.84] | 1744 / 2118 |
| email | rules+gliner-cs-sk-ce-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-ce-s2 | 0.978 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4225 / 4344 |
| any | rules+gliner-cs-sk-ce-s2 | 0.941 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8332 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s2 | 0.092 [0.07, 0.11] | 0.940 [0.93, 0.95] | 1.1 [1.0, 1.4] | 1991 / 2118 |
| email | rules+gliner-cs-sk-ce-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-ce-s2 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4292 / 4344 |
| any | rules+gliner-cs-sk-ce-s2 | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8644 / 8927 |
