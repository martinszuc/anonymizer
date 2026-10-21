# train-cs-sk-xlmr-ce-dev

rules+xlmr-cs-sk-ce after training (train-cs-sk-xlmr-ce).

Stage: dev · commit 156b8b704e · 2026-10-21T01:05:40+00:00 · seed 20261010, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce @ fafa48033a · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.938 [0.85, 1.00] | 0.955 [0.86, 1.00] | 0.946 [0.88, 1.00] | 0.951 [0.87, 1.00] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce | 0.925 [0.89, 0.96] | 0.945 [0.93, 0.96] | 0.935 [0.91, 0.95] | 0.941 [0.92, 0.96] | 495 / 524 |
| phone | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce | 0.931 [0.90, 0.96] | 0.936 [0.91, 0.96] | 0.933 [0.91, 0.95] | 0.935 [0.91, 0.95] | 567 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.156 [0.04, 0.33] | 0.227 [0.06, 0.47] | 0.185 [0.05, 0.38] | 0.208 [0.06, 0.44] | 5 / 22 |
| email | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce | 0.884 [0.85, 0.92] | 0.901 [0.87, 0.93] | 0.892 [0.86, 0.92] | 0.897 [0.87, 0.92] | 472 / 524 |
| phone | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce | 0.854 [0.81, 0.89] | 0.860 [0.81, 0.90] | 0.857 [0.82, 0.89] | 0.859 [0.81, 0.90] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.343 [0.20, 0.45] | 0.318 [0.12, 0.58] | 0.6 [0.1, 1.1] | 7 / 22 |
| email | rules+xlmr-cs-sk-ce | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce | 0.034 [0.02, 0.05] | 0.927 [0.90, 0.95] | 3.3 [1.9, 4.7] | 486 / 524 |
| phone | rules+xlmr-cs-sk-ce | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce | 0.090 [0.06, 0.13] | 0.886 [0.85, 0.92] | 3.8 [2.4, 5.3] | 537 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce | 0.888 [0.81, 0.96] | 0.924 [0.88, 0.96] | 0.906 [0.86, 0.95] | 0.916 [0.88, 0.95] | 255 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce | 0.860 [0.78, 0.94] | 0.891 [0.84, 0.94] | 0.875 [0.82, 0.93] | 0.885 [0.84, 0.93] | 246 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce | 0.059 [0.03, 0.09] | 0.906 [0.85, 0.95] | 4.4 [1.4, 7.6] | 250 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.500 [0.33, 0.70] | 1.000 [1.00, 1.00] | 0.667 [0.49, 0.82] | 0.833 [0.71, 0.92] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce | 0.801 [0.64, 0.96] | 0.931 [0.81, 1.00] | 0.861 [0.74, 0.96] | 0.902 [0.80, 0.98] | 204 / 219 |
| phone | rules+xlmr-cs-sk-ce | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce | 0.801 [0.69, 0.90] | 0.874 [0.81, 0.93] | 0.836 [0.77, 0.89] | 0.858 [0.80, 0.91] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.407 [0.25, 0.61] | 0.815 [0.64, 0.96] | 0.543 [0.37, 0.72] | 0.679 [0.50, 0.83] | 22 / 27 |
| birth_number | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce | 0.610 [0.46, 0.77] | 0.699 [0.59, 0.81] | 0.651 [0.53, 0.77] | 0.679 [0.58, 0.79] | 153 / 219 |
| phone | rules+xlmr-cs-sk-ce | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce | 0.675 [0.57, 0.78] | 0.727 [0.66, 0.79] | 0.700 [0.63, 0.77] | 0.716 [0.65, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 7.4 [2.5, 13.9] | 26 / 27 |
| birth_number | rules+xlmr-cs-sk-ce | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce | 0.051 [0.00, 0.13] | 0.899 [0.78, 0.98] | 9.4 [4.6, 15.9] | 197 / 219 |
| phone | rules+xlmr-cs-sk-ce | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce | 0.083 [0.05, 0.12] | 0.863 [0.80, 0.93] | 18.5 [10.7, 27.8] | 335 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.980 [0.97, 0.99] | 0.998 [1.00, 1.00] | 0.989 [0.99, 0.99] | 0.995 [0.99, 1.00] | 2115 / 2119 |
| email | rules+xlmr-cs-sk-ce | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce | 0.998 [1.00, 1.00] | 0.997 [0.99, 1.00] | 0.998 [1.00, 1.00] | 0.997 [1.00, 1.00] | 4339 / 4353 |
| any | rules+xlmr-cs-sk-ce | 0.994 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.996 [0.99, 1.00] | 9060 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.859 [0.85, 0.87] | 0.891 [0.88, 0.91] | 0.875 [0.86, 0.89] | 0.885 [0.87, 0.90] | 1889 / 2119 |
| email | rules+xlmr-cs-sk-ce | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce | 0.985 [0.98, 0.99] | 0.983 [0.98, 0.99] | 0.984 [0.98, 0.99] | 0.983 [0.98, 0.99] | 4279 / 4353 |
| any | rules+xlmr-cs-sk-ce | 0.946 [0.94, 0.95] | 0.952 [0.95, 0.96] | 0.949 [0.94, 0.95] | 0.951 [0.95, 0.96] | 8663 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.003 [0.00, 0.00] | 0.993 [0.99, 1.00] | 1.2 [1.0, 1.4] | 2105 / 2119 |
| email | rules+xlmr-cs-sk-ce | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce | 0.003 [0.00, 0.00] | 0.994 [0.99, 1.00] | 0.2 [0.1, 0.3] | 4326 / 4353 |
| any | rules+xlmr-cs-sk-ce | 0.008 [0.01, 0.01] | 0.981 [0.98, 0.98] | 1.5 [1.3, 1.7] | 8926 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.981 [0.98, 0.99] | 0.995 [0.99, 1.00] | 0.988 [0.98, 0.99] | 0.993 [0.99, 0.99] | 2108 / 2118 |
| email | rules+xlmr-cs-sk-ce | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce | 0.998 [1.00, 1.00] | 0.996 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.996 [0.99, 1.00] | 4325 / 4344 |
| any | rules+xlmr-cs-sk-ce | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 8886 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.844 [0.83, 0.86] | 0.875 [0.86, 0.89] | 0.859 [0.84, 0.87] | 0.869 [0.85, 0.88] | 1854 / 2118 |
| email | rules+xlmr-cs-sk-ce | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce | 0.980 [0.98, 0.98] | 0.977 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4245 / 4344 |
| any | rules+xlmr-cs-sk-ce | 0.942 [0.94, 0.95] | 0.948 [0.94, 0.95] | 0.945 [0.94, 0.95] | 0.947 [0.94, 0.95] | 8459 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce | 0.005 [0.00, 0.01] | 0.987 [0.98, 0.99] | 1.3 [1.1, 1.5] | 2091 / 2118 |
| email | rules+xlmr-cs-sk-ce | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce | 0.003 [0.00, 0.00] | 0.993 [0.99, 1.00] | 0.3 [0.2, 0.4] | 4314 / 4344 |
| any | rules+xlmr-cs-sk-ce | 0.008 [0.01, 0.01] | 0.982 [0.98, 0.98] | 1.7 [1.4, 1.9] | 8766 / 8927 |
