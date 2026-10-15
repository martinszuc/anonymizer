# train-cs-ce-s2-dev

rules+gliner-cs-ce-s2 after training (train-cs-ce-s2).

Stage: dev · commit 0211b3728e · 2026-10-14T20:37:26+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-ce-s2 @ f555ca4bf9 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.882 [0.79, 0.97] | 0.955 [0.88, 1.00] | 0.917 [0.84, 0.99] | 0.939 [0.87, 0.99] | 21 / 22 |
| email | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-ce-s2 | 0.928 [0.90, 0.95] | 0.937 [0.91, 0.96] | 0.932 [0.91, 0.95] | 0.935 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-ce-s2 | 0.931 [0.90, 0.95] | 0.931 [0.90, 0.96] | 0.931 [0.91, 0.95] | 0.931 [0.90, 0.95] | 564 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.118 [0.03, 0.27] | 0.182 [0.04, 0.40] | 0.143 [0.03, 0.32] | 0.164 [0.04, 0.36] | 4 / 22 |
| email | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-ce-s2 | 0.884 [0.85, 0.91] | 0.891 [0.86, 0.92] | 0.888 [0.86, 0.91] | 0.890 [0.86, 0.91] | 467 / 524 |
| phone | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-ce-s2 | 0.850 [0.81, 0.88] | 0.850 [0.81, 0.89] | 0.850 [0.81, 0.88] | 0.850 [0.81, 0.88] | 515 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.410 [0.29, 0.50] | 0.273 [0.10, 0.50] | 0.8 [0.2, 1.6] | 6 / 22 |
| email | rules+gliner-cs-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-ce-s2 | 0.042 [0.03, 0.06] | 0.920 [0.90, 0.94] | 3.2 [2.2, 4.4] | 482 / 524 |
| phone | rules+gliner-cs-ce-s2 | 0.318 [0.09, 0.61] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-ce-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-ce-s2 | 0.105 [0.07, 0.14] | 0.878 [0.84, 0.91] | 4.1 [2.8, 5.5] | 532 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-ce-s2 | 0.860 [0.77, 0.93] | 0.877 [0.82, 0.93] | 0.868 [0.81, 0.91] | 0.873 [0.82, 0.92] | 242 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-ce-s2 | 0.824 [0.73, 0.90] | 0.833 [0.77, 0.89] | 0.829 [0.77, 0.88] | 0.832 [0.78, 0.88] | 230 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-ce-s2 | 0.103 [0.06, 0.15] | 0.859 [0.80, 0.92] | 5.1 [2.2, 9.1] | 237 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.549 [0.40, 0.70] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-ce-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-ce-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-ce-s2 | 0.807 [0.64, 0.97] | 0.936 [0.81, 1.00] | 0.867 [0.75, 0.97] | 0.907 [0.80, 0.99] | 205 / 219 |
| phone | rules+gliner-cs-ce-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-ce-s2 | 0.811 [0.70, 0.90] | 0.874 [0.81, 0.92] | 0.841 [0.77, 0.90] | 0.861 [0.80, 0.91] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.451 [0.30, 0.62] | 0.852 [0.69, 1.00] | 0.590 [0.43, 0.75] | 0.723 [0.56, 0.87] | 23 / 27 |
| birth_number | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-ce-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-ce-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-ce-s2 | 0.639 [0.49, 0.80] | 0.712 [0.60, 0.82] | 0.674 [0.56, 0.79] | 0.696 [0.59, 0.80] | 156 / 219 |
| phone | rules+gliner-cs-ce-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-ce-s2 | 0.699 [0.60, 0.80] | 0.735 [0.67, 0.80] | 0.716 [0.65, 0.78] | 0.727 [0.67, 0.79] | 285 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.1 [2.9, 10.0] | 27 / 27 |
| birth_number | rules+gliner-cs-ce-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-ce-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-ce-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-ce-s2 | 0.048 [0.00, 0.14] | 0.922 [0.80, 1.00] | 9.6 [5.0, 16.1] | 202 / 219 |
| phone | rules+gliner-cs-ce-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-ce-s2 | 0.079 [0.05, 0.12] | 0.879 [0.81, 0.93] | 17.5 [11.2, 24.8] | 341 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.997 [0.99, 1.00] | 0.953 [0.94, 0.96] | 0.974 [0.97, 0.98] | 0.961 [0.95, 0.97] | 2019 / 2119 |
| email | rules+gliner-cs-ce-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-ce-s2 | 0.996 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4305 / 4353 |
| any | rules+gliner-cs-ce-s2 | 0.997 [1.00, 1.00] | 0.982 [0.98, 0.98] | 0.990 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8935 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.854 [0.84, 0.87] | 0.831 [0.81, 0.85] | 0.842 [0.83, 0.86] | 0.836 [0.82, 0.85] | 1761 / 2119 |
| email | rules+gliner-cs-ce-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-ce-s2 | 0.984 [0.98, 0.99] | 0.977 [0.97, 0.98] | 0.981 [0.98, 0.98] | 0.979 [0.97, 0.98] | 4254 / 4353 |
| any | rules+gliner-cs-ce-s2 | 0.946 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8511 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.086 [0.07, 0.10] | 0.936 [0.92, 0.95] | 1.0 [0.8, 1.2] | 1983 / 2119 |
| email | rules+gliner-cs-ce-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-ce-s2 | 0.008 [0.01, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4298 / 4353 |
| any | rules+gliner-cs-ce-s2 | 0.038 [0.03, 0.04] | 0.965 [0.96, 0.97] | 1.3 [1.1, 1.6] | 8776 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.994 [0.99, 1.00] | 0.954 [0.94, 0.96] | 0.974 [0.97, 0.98] | 0.962 [0.95, 0.97] | 2021 / 2118 |
| email | rules+gliner-cs-ce-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-ce-s2 | 0.994 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4301 / 4344 |
| any | rules+gliner-cs-ce-s2 | 0.996 [0.99, 1.00] | 0.983 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8777 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.836 [0.82, 0.85] | 0.817 [0.80, 0.83] | 0.826 [0.81, 0.84] | 0.821 [0.80, 0.84] | 1730 / 2118 |
| email | rules+gliner-cs-ce-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-ce-s2 | 0.964 [0.96, 0.97] | 0.959 [0.95, 0.97] | 0.961 [0.95, 0.97] | 0.960 [0.95, 0.97] | 4166 / 4344 |
| any | rules+gliner-cs-ce-s2 | 0.934 [0.93, 0.94] | 0.925 [0.92, 0.93] | 0.930 [0.92, 0.94] | 0.927 [0.92, 0.93] | 8260 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-ce-s2 | 0.094 [0.08, 0.11] | 0.936 [0.92, 0.95] | 1.2 [1.0, 1.5] | 1982 / 2118 |
| email | rules+gliner-cs-ce-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-ce-s2 | 0.007 [0.00, 0.01] | 0.986 [0.98, 0.99] | 0.5 [0.4, 0.6] | 4285 / 4344 |
| any | rules+gliner-cs-ce-s2 | 0.038 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.9 [1.6, 2.1] | 8628 / 8927 |
