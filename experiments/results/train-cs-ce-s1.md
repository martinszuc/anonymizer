# train-cs-ce-s1-dev

rules+gliner-cs-ce-s1 after training (train-cs-ce-s1).

Stage: dev · commit 0211b3728e · 2026-10-14T20:31:12+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-ce-s1 @ d644a320ab · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.867 [0.75, 0.97] | 0.864 [0.71, 1.00] | 0.865 [0.77, 0.94] | 0.864 [0.74, 0.96] | 19 / 22 |
| email | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-ce-s1 | 0.923 [0.89, 0.95] | 0.937 [0.91, 0.96] | 0.930 [0.91, 0.95] | 0.934 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-ce-s1 | 0.926 [0.89, 0.95] | 0.917 [0.89, 0.95] | 0.922 [0.90, 0.94] | 0.919 [0.89, 0.94] | 556 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.100 [0.00, 0.24] | 0.136 [0.00, 0.35] | 0.115 [0.00, 0.27] | 0.127 [0.00, 0.31] | 3 / 22 |
| email | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-ce-s1 | 0.882 [0.85, 0.91] | 0.895 [0.87, 0.92] | 0.888 [0.86, 0.91] | 0.892 [0.87, 0.91] | 469 / 524 |
| phone | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-ce-s1 | 0.852 [0.81, 0.89] | 0.852 [0.81, 0.89] | 0.852 [0.82, 0.88] | 0.852 [0.81, 0.88] | 516 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.471 [0.30, 0.61] | 0.227 [0.07, 0.47] | 0.9 [0.3, 1.8] | 5 / 22 |
| email | rules+gliner-cs-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-ce-s1 | 0.055 [0.04, 0.07] | 0.908 [0.89, 0.93] | 3.4 [2.1, 4.7] | 476 / 524 |
| phone | rules+gliner-cs-ce-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-ce-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-ce-s1 | 0.117 [0.08, 0.15] | 0.866 [0.83, 0.90] | 4.2 [2.7, 6.1] | 525 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-ce-s1 | 0.840 [0.74, 0.92] | 0.880 [0.83, 0.93] | 0.860 [0.80, 0.91] | 0.872 [0.83, 0.91] | 243 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-ce-s1 | 0.808 [0.72, 0.89] | 0.841 [0.78, 0.89] | 0.824 [0.77, 0.87] | 0.834 [0.78, 0.88] | 232 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-ce-s1 | 0.097 [0.06, 0.14] | 0.862 [0.80, 0.92] | 6.0 [2.8, 10.0] | 238 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.549 [0.41, 0.70] | 1.000 [1.00, 1.00] | 0.709 [0.58, 0.82] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-ce-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-ce-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-ce-s1 | 0.816 [0.64, 0.96] | 0.991 [0.98, 1.00] | 0.895 [0.78, 0.98] | 0.950 [0.89, 0.99] | 217 / 219 |
| phone | rules+gliner-cs-ce-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-ce-s1 | 0.816 [0.70, 0.91] | 0.902 [0.85, 0.94] | 0.857 [0.78, 0.91] | 0.883 [0.83, 0.92] | 350 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.471 [0.32, 0.64] | 0.889 [0.71, 1.00] | 0.615 [0.45, 0.76] | 0.755 [0.59, 0.88] | 24 / 27 |
| birth_number | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-ce-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-ce-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-ce-s1 | 0.604 [0.45, 0.76] | 0.703 [0.58, 0.82] | 0.650 [0.52, 0.79] | 0.681 [0.56, 0.81] | 154 / 219 |
| phone | rules+gliner-cs-ce-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-ce-s1 | 0.678 [0.57, 0.78] | 0.732 [0.66, 0.80] | 0.704 [0.63, 0.78] | 0.720 [0.65, 0.79] | 284 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.1 [3.0, 10.0] | 27 / 27 |
| birth_number | rules+gliner-cs-ce-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-ce-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-ce-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-ce-s1 | 0.013 [0.00, 0.03] | 0.977 [0.95, 1.00] | 11.1 [5.8, 18.0] | 214 / 219 |
| phone | rules+gliner-cs-ce-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-ce-s1 | 0.065 [0.03, 0.10] | 0.910 [0.86, 0.95] | 19.0 [12.6, 26.8] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.996 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.975 [0.97, 0.98] | 0.963 [0.96, 0.97] | 2023 / 2119 |
| email | rules+gliner-cs-ce-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-ce-s1 | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 4325 / 4353 |
| any | rules+gliner-cs-ce-s1 | 0.997 [1.00, 1.00] | 0.985 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8957 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.850 [0.83, 0.86] | 0.829 [0.81, 0.85] | 0.839 [0.82, 0.85] | 0.833 [0.82, 0.85] | 1757 / 2119 |
| email | rules+gliner-cs-ce-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-ce-s1 | 0.984 [0.98, 0.99] | 0.981 [0.98, 0.99] | 0.983 [0.98, 0.99] | 0.982 [0.98, 0.99] | 4272 / 4353 |
| any | rules+gliner-cs-ce-s1 | 0.945 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.939 [0.93, 0.94] | 8525 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.086 [0.07, 0.10] | 0.933 [0.92, 0.94] | 1.1 [0.9, 1.3] | 1978 / 2119 |
| email | rules+gliner-cs-ce-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-ce-s1 | 0.006 [0.00, 0.01] | 0.992 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4316 / 4353 |
| any | rules+gliner-cs-ce-s1 | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.2, 1.7] | 8789 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.995 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.974 [0.97, 0.98] | 0.962 [0.95, 0.97] | 2022 / 2118 |
| email | rules+gliner-cs-ce-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-ce-s1 | 0.993 [0.99, 1.00] | 0.993 [0.99, 1.00] | 0.993 [0.99, 0.99] | 0.993 [0.99, 0.99] | 4312 / 4344 |
| any | rules+gliner-cs-ce-s1 | 0.996 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8790 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.835 [0.82, 0.85] | 0.816 [0.80, 0.83] | 0.825 [0.81, 0.84] | 0.820 [0.80, 0.84] | 1728 / 2118 |
| email | rules+gliner-cs-ce-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-ce-s1 | 0.966 [0.96, 0.97] | 0.966 [0.96, 0.97] | 0.966 [0.96, 0.97] | 0.966 [0.96, 0.97] | 4194 / 4344 |
| any | rules+gliner-cs-ce-s1 | 0.935 [0.93, 0.94] | 0.928 [0.92, 0.93] | 0.932 [0.93, 0.94] | 0.930 [0.92, 0.94] | 8286 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s1 | 0.095 [0.08, 0.11] | 0.933 [0.92, 0.94] | 1.2 [1.0, 1.4] | 1976 / 2118 |
| email | rules+gliner-cs-ce-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-ce-s1 | 0.005 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.5 [0.4, 0.6] | 4298 / 4344 |
| any | rules+gliner-cs-ce-s1 | 0.038 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.8 [1.5, 2.1] | 8635 / 8927 |
