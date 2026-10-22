# train-cs-sk-xlmr-ce-r3-dev

rules+xlmr-cs-sk-ce-r3 after training (train-cs-sk-xlmr-ce-r3).

Stage: dev · commit 0b2364ff37 · 2026-10-21T20:29:02+00:00 · seed 20261010, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce-r3 @ edde36175c · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.857 [0.76, 0.95] | 0.955 [0.86, 1.00] | 0.903 [0.85, 0.96] | 0.933 [0.86, 0.98] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.928 [0.90, 0.96] | 0.945 [0.92, 0.96] | 0.936 [0.92, 0.96] | 0.941 [0.92, 0.96] | 495 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.929 [0.90, 0.96] | 0.932 [0.90, 0.96] | 0.931 [0.91, 0.95] | 0.932 [0.91, 0.95] | 565 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.171 [0.06, 0.32] | 0.273 [0.11, 0.50] | 0.210 [0.08, 0.38] | 0.244 [0.09, 0.44] | 6 / 22 |
| email | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.887 [0.85, 0.92] | 0.899 [0.87, 0.92] | 0.893 [0.87, 0.92] | 0.896 [0.87, 0.92] | 471 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.854 [0.81, 0.89] | 0.860 [0.82, 0.90] | 0.857 [0.82, 0.89] | 0.859 [0.82, 0.89] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.310 [0.17, 0.43] | 0.364 [0.17, 0.62] | 0.9 [0.3, 1.6] | 8 / 22 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.036 [0.02, 0.05] | 0.927 [0.91, 0.95] | 3.1 [1.8, 4.5] | 486 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3 | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.086 [0.05, 0.12] | 0.888 [0.85, 0.92] | 4.0 [2.5, 5.6] | 538 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3 | 0.881 [0.80, 0.95] | 0.913 [0.86, 0.95] | 0.897 [0.85, 0.94] | 0.906 [0.87, 0.94] | 252 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3 | 0.853 [0.77, 0.93] | 0.880 [0.83, 0.92] | 0.866 [0.81, 0.92] | 0.875 [0.83, 0.92] | 243 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3 | 0.079 [0.04, 0.12] | 0.895 [0.84, 0.94] | 4.3 [1.6, 7.6] | 247 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.509 [0.33, 0.72] | 1.000 [1.00, 1.00] | 0.675 [0.49, 0.84] | 0.838 [0.71, 0.93] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.784 [0.62, 0.94] | 0.931 [0.81, 1.00] | 0.852 [0.74, 0.95] | 0.898 [0.80, 0.97] | 204 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.790 [0.68, 0.89] | 0.874 [0.81, 0.93] | 0.830 [0.76, 0.89] | 0.856 [0.80, 0.90] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.400 [0.24, 0.61] | 0.815 [0.64, 0.96] | 0.537 [0.36, 0.72] | 0.675 [0.50, 0.83] | 22 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.600 [0.45, 0.76] | 0.699 [0.59, 0.81] | 0.646 [0.53, 0.77] | 0.676 [0.58, 0.78] | 153 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.664 [0.56, 0.77] | 0.724 [0.67, 0.79] | 0.693 [0.62, 0.77] | 0.711 [0.65, 0.77] | 281 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 8.5 [2.9, 16.7] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce-r3 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.050 [0.00, 0.13] | 0.904 [0.79, 0.98] | 10.3 [5.3, 17.1] | 198 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.080 [0.04, 0.12] | 0.869 [0.80, 0.93] | 20.6 [12.2, 30.8] | 337 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.990 [0.99, 0.99] | 1.000 [1.00, 1.00] | 0.995 [0.99, 1.00] | 0.998 [1.00, 1.00] | 2119 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.998 [1.00, 1.00] | 0.997 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.997 [1.00, 1.00] | 4339 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.996 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.996 [1.00, 1.00] | 0.996 [1.00, 1.00] | 9064 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.868 [0.85, 0.88] | 0.894 [0.88, 0.91] | 0.881 [0.87, 0.89] | 0.889 [0.88, 0.90] | 1894 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.985 [0.98, 0.99] | 0.984 [0.98, 0.99] | 0.984 [0.98, 0.99] | 0.984 [0.98, 0.99] | 4283 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.949 [0.94, 0.95] | 0.953 [0.95, 0.96] | 0.951 [0.95, 0.96] | 0.952 [0.95, 0.96] | 8672 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.001 [0.00, 0.00] | 0.996 [0.99, 1.00] | 1.1 [0.9, 1.3] | 2111 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.003 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.2 [0.2, 0.3] | 4327 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.007 [0.01, 0.01] | 0.982 [0.98, 0.98] | 1.4 [1.2, 1.6] | 8933 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.985 [0.98, 0.99] | 0.996 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.994 [0.99, 1.00] | 2109 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.997 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 4323 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 8883 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.847 [0.83, 0.86] | 0.876 [0.86, 0.89] | 0.861 [0.85, 0.87] | 0.870 [0.86, 0.88] | 1855 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.979 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4246 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.943 [0.94, 0.95] | 0.948 [0.94, 0.95] | 0.945 [0.94, 0.95] | 0.947 [0.94, 0.95] | 8461 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3 | 0.003 [0.00, 0.00] | 0.992 [0.99, 1.00] | 1.3 [1.1, 1.5] | 2100 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3 | 0.003 [0.00, 0.00] | 0.992 [0.99, 1.00] | 0.3 [0.2, 0.4] | 4311 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3 | 0.007 [0.01, 0.01] | 0.983 [0.98, 0.99] | 1.7 [1.5, 1.9] | 8772 / 8927 |
