# train-cs-sk-xlmr-ce-r3-s1-dev

rules+xlmr-cs-sk-ce-r3-s1 after training (train-cs-sk-xlmr-ce-r3-s1).

Stage: dev · commit 0b2364ff37 · 2026-10-21T20:34:09+00:00 · seed 1, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce-r3-s1 @ 919e0a49a9 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.919 [0.83, 1.00] | 0.955 [0.83, 1.00] | 0.936 [0.87, 0.99] | 0.947 [0.86, 1.00] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.939 [0.91, 0.96] | 0.945 [0.92, 0.96] | 0.942 [0.92, 0.96] | 0.944 [0.92, 0.96] | 495 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.944 [0.92, 0.97] | 0.936 [0.91, 0.96] | 0.940 [0.92, 0.96] | 0.937 [0.91, 0.96] | 567 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.162 [0.05, 0.32] | 0.273 [0.10, 0.50] | 0.203 [0.07, 0.38] | 0.240 [0.09, 0.45] | 6 / 22 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.905 [0.87, 0.94] | 0.908 [0.88, 0.93] | 0.907 [0.88, 0.93] | 0.908 [0.88, 0.93] | 476 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.868 [0.83, 0.90] | 0.870 [0.83, 0.90] | 0.869 [0.83, 0.90] | 0.869 [0.83, 0.90] | 527 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.343 [0.19, 0.46] | 0.364 [0.19, 0.62] | 0.8 [0.3, 1.5] | 8 / 22 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.032 [0.02, 0.05] | 0.929 [0.91, 0.95] | 2.4 [1.4, 3.6] | 487 / 524 |
| phone | rules+xlmr-cs-sk-ce-r3-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-r3-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.089 [0.06, 0.12] | 0.889 [0.85, 0.92] | 3.2 [2.1, 4.5] | 539 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.883 [0.80, 0.96] | 0.902 [0.86, 0.94] | 0.892 [0.84, 0.93] | 0.898 [0.86, 0.93] | 249 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.858 [0.77, 0.94] | 0.877 [0.83, 0.92] | 0.867 [0.81, 0.91] | 0.873 [0.83, 0.91] | 242 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.084 [0.05, 0.12] | 0.884 [0.83, 0.93] | 4.3 [1.5, 8.4] | 244 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.491 [0.32, 0.70] | 1.000 [1.00, 1.00] | 0.658 [0.48, 0.82] | 0.828 [0.70, 0.92] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.759 [0.61, 0.90] | 0.922 [0.80, 0.99] | 0.833 [0.72, 0.92] | 0.884 [0.78, 0.95] | 202 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.772 [0.67, 0.87] | 0.869 [0.81, 0.92] | 0.817 [0.75, 0.87] | 0.847 [0.79, 0.89] | 337 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.400 [0.24, 0.61] | 0.815 [0.62, 0.96] | 0.537 [0.36, 0.73] | 0.675 [0.49, 0.84] | 22 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.571 [0.44, 0.71] | 0.694 [0.58, 0.80] | 0.627 [0.52, 0.73] | 0.665 [0.56, 0.77] | 152 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.645 [0.54, 0.74] | 0.722 [0.66, 0.78] | 0.681 [0.61, 0.75] | 0.705 [0.65, 0.76] | 280 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 8.3 [2.6, 16.1] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-r3-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce-r3-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-r3-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.056 [0.01, 0.14] | 0.881 [0.75, 0.97] | 9.7 [4.9, 16.8] | 193 / 219 |
| phone | rules+xlmr-cs-sk-ce-r3-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.083 [0.05, 0.12] | 0.856 [0.78, 0.91] | 19.8 [12.3, 29.9] | 332 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.994 [0.99, 1.00] | 0.999 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.998 [1.00, 1.00] | 2116 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.999 [1.00, 1.00] | 0.995 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.996 [0.99, 1.00] | 4333 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.998 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.996 [0.99, 1.00] | 9056 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.875 [0.86, 0.89] | 0.895 [0.88, 0.91] | 0.884 [0.87, 0.90] | 0.891 [0.88, 0.90] | 1896 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.986 [0.98, 0.99] | 0.983 [0.98, 0.99] | 0.985 [0.98, 0.99] | 0.984 [0.98, 0.99] | 4278 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.951 [0.95, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.95, 0.96] | 0.953 [0.95, 0.96] | 8670 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.001 [0.00, 0.00] | 0.996 [0.99, 1.00] | 1.0 [0.9, 1.2] | 2111 / 2119 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.003 [0.00, 0.00] | 0.993 [0.99, 1.00] | 0.2 [0.1, 0.3] | 4321 / 4353 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.007 [0.01, 0.01] | 0.981 [0.98, 0.98] | 1.3 [1.1, 1.6] | 8927 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.995 [0.99, 1.00] | 0.997 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.997 [0.99, 1.00] | 2112 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.998 [1.00, 1.00] | 0.995 [0.99, 1.00] | 0.997 [0.99, 1.00] | 0.996 [0.99, 1.00] | 4323 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.997 [1.00, 1.00] | 0.995 [0.99, 1.00] | 0.996 [1.00, 1.00] | 0.996 [0.99, 1.00] | 8884 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.856 [0.84, 0.87] | 0.878 [0.86, 0.89] | 0.867 [0.85, 0.88] | 0.874 [0.86, 0.89] | 1860 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.980 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4244 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.945 [0.94, 0.95] | 0.948 [0.94, 0.95] | 0.947 [0.94, 0.95] | 0.948 [0.94, 0.95] | 8464 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-r3-s1 | 0.002 [0.00, 0.00] | 0.994 [0.99, 1.00] | 1.1 [0.9, 1.3] | 2105 / 2118 |
| email | rules+xlmr-cs-sk-ce-r3-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce-r3-s1 | 0.003 [0.00, 0.00] | 0.992 [0.99, 1.00] | 0.3 [0.2, 0.4] | 4310 / 4344 |
| any | rules+xlmr-cs-sk-ce-r3-s1 | 0.007 [0.01, 0.01] | 0.983 [0.98, 0.99] | 1.5 [1.2, 1.7] | 8776 / 8927 |
