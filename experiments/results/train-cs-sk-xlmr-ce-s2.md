# train-cs-sk-xlmr-ce-s2-dev

rules+xlmr-cs-sk-ce-s2 after training (train-cs-sk-xlmr-ce-s2).

Stage: dev · commit 156b8b704e · 2026-10-21T01:13:53+00:00 · seed 2, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce-s2 @ a62555cb99 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.889 [0.78, 0.98] | 0.955 [0.86, 1.00] | 0.920 [0.85, 0.97] | 0.941 [0.87, 0.99] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.945 [0.92, 0.97] | 0.947 [0.92, 0.97] | 0.946 [0.92, 0.96] | 0.946 [0.92, 0.97] | 496 / 524 |
| phone | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.946 [0.92, 0.97] | 0.937 [0.91, 0.96] | 0.942 [0.92, 0.96] | 0.939 [0.91, 0.96] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.139 [0.03, 0.28] | 0.227 [0.06, 0.46] | 0.172 [0.04, 0.34] | 0.202 [0.05, 0.41] | 5 / 22 |
| email | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.900 [0.87, 0.93] | 0.908 [0.88, 0.93] | 0.904 [0.88, 0.93] | 0.907 [0.88, 0.93] | 476 / 524 |
| phone | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.864 [0.82, 0.90] | 0.868 [0.83, 0.90] | 0.866 [0.83, 0.89] | 0.867 [0.83, 0.90] | 526 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.318 [0.21, 0.42] | 0.273 [0.09, 0.50] | 0.9 [0.4, 1.6] | 6 / 22 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.029 [0.02, 0.04] | 0.931 [0.91, 0.95] | 2.2 [1.3, 3.3] | 488 / 524 |
| phone | rules+xlmr-cs-sk-ce-s2 | 0.328 [0.09, 0.64] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.083 [0.05, 0.11] | 0.888 [0.85, 0.92] | 3.1 [2.0, 4.3] | 538 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-s2 | 0.887 [0.80, 0.96] | 0.909 [0.86, 0.95] | 0.898 [0.85, 0.93] | 0.905 [0.86, 0.94] | 251 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-s2 | 0.855 [0.77, 0.93] | 0.877 [0.82, 0.93] | 0.866 [0.81, 0.91] | 0.872 [0.82, 0.92] | 242 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-s2 | 0.075 [0.04, 0.11] | 0.891 [0.84, 0.94] | 4.3 [1.5, 8.2] | 246 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.491 [0.31, 0.73] | 1.000 [1.00, 1.00] | 0.658 [0.48, 0.84] | 0.828 [0.69, 0.93] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.794 [0.64, 0.94] | 1.000 [1.00, 1.00] | 0.885 [0.78, 0.97] | 0.951 [0.90, 0.99] | 219 / 219 |
| phone | rules+xlmr-cs-sk-ce-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.793 [0.68, 0.89] | 0.907 [0.86, 0.94] | 0.846 [0.78, 0.90] | 0.882 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.364 [0.20, 0.60] | 0.741 [0.56, 0.91] | 0.488 [0.31, 0.70] | 0.614 [0.43, 0.80] | 20 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.577 [0.43, 0.74] | 0.703 [0.59, 0.82] | 0.634 [0.51, 0.76] | 0.674 [0.56, 0.79] | 154 / 219 |
| phone | rules+xlmr-cs-sk-ce-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.644 [0.55, 0.74] | 0.722 [0.66, 0.79] | 0.680 [0.61, 0.76] | 0.705 [0.64, 0.77] | 280 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.029 [0.00, 0.08] | 0.926 [0.81, 1.00] | 8.1 [2.5, 16.4] | 25 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.011 [0.00, 0.02] | 0.973 [0.94, 0.99] | 11.7 [6.5, 18.4] | 213 / 219 |
| phone | rules+xlmr-cs-sk-ce-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.067 [0.04, 0.10] | 0.902 [0.85, 0.94] | 21.5 [13.3, 31.3] | 350 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.976 [0.97, 0.98] | 0.999 [1.00, 1.00] | 0.987 [0.98, 0.99] | 0.994 [0.99, 1.00] | 2117 / 2119 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.998 [1.00, 1.00] | 0.998 [1.00, 1.00] | 0.998 [1.00, 1.00] | 0.998 [1.00, 1.00] | 4342 / 4353 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.993 [0.99, 0.99] | 0.997 [1.00, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 9066 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.845 [0.83, 0.86] | 0.886 [0.87, 0.90] | 0.865 [0.85, 0.88] | 0.878 [0.86, 0.89] | 1878 / 2119 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.985 [0.98, 0.99] | 0.984 [0.98, 0.99] | 0.985 [0.98, 0.99] | 0.985 [0.98, 0.99] | 4285 / 4353 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.943 [0.94, 0.95] | 0.952 [0.95, 0.96] | 0.947 [0.94, 0.95] | 0.950 [0.95, 0.95] | 8658 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.002 [0.00, 0.00] | 0.992 [0.99, 1.00] | 1.2 [1.0, 1.5] | 2103 / 2119 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.003 [0.00, 0.00] | 0.995 [0.99, 1.00] | 0.2 [0.2, 0.3] | 4330 / 4353 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.007 [0.01, 0.01] | 0.981 [0.98, 0.98] | 1.6 [1.3, 1.8] | 8928 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.974 [0.97, 0.98] | 0.997 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.992 [0.99, 0.99] | 2111 / 2118 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.997 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.997 [0.99, 1.00] | 0.996 [0.99, 1.00] | 4328 / 4344 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.992 [0.99, 0.99] | 0.996 [0.99, 1.00] | 0.994 [0.99, 0.99] | 0.995 [0.99, 1.00] | 8888 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.835 [0.82, 0.85] | 0.876 [0.86, 0.89] | 0.855 [0.84, 0.87] | 0.867 [0.85, 0.88] | 1855 / 2118 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.979 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.979 [0.97, 0.98] | 4251 / 4344 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.939 [0.93, 0.94] | 0.948 [0.94, 0.95] | 0.944 [0.94, 0.95] | 0.947 [0.94, 0.95] | 8466 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-s2 | 0.003 [0.00, 0.01] | 0.989 [0.98, 0.99] | 1.5 [1.2, 1.7] | 2095 / 2118 |
| email | rules+xlmr-cs-sk-ce-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce-s2 | 0.003 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.3 [0.2, 0.4] | 4316 / 4344 |
| any | rules+xlmr-cs-sk-ce-s2 | 0.007 [0.01, 0.01] | 0.983 [0.98, 0.99] | 1.9 [1.6, 2.1] | 8772 / 8927 |
