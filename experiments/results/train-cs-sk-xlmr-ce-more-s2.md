# train-cs-sk-xlmr-ce-more-s2-dev

rules+xlmr-cs-sk-ce-more-s2 after training (train-cs-sk-xlmr-ce-more-s2).

Stage: dev · commit 0b2364ff37 · 2026-10-21T22:19:03+00:00 · seed 2, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-ce-more-s2 @ 85d0153bd3 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.865 [0.76, 0.96] | 0.955 [0.86, 1.00] | 0.907 [0.85, 0.96] | 0.935 [0.86, 0.98] | 21 / 22 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.912 [0.88, 0.94] | 0.945 [0.92, 0.96] | 0.928 [0.90, 0.95] | 0.938 [0.92, 0.96] | 495 / 524 |
| phone | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.918 [0.89, 0.94] | 0.932 [0.90, 0.96] | 0.925 [0.90, 0.94] | 0.929 [0.91, 0.95] | 565 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.162 [0.06, 0.29] | 0.273 [0.11, 0.48] | 0.203 [0.08, 0.36] | 0.240 [0.09, 0.43] | 6 / 22 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.868 [0.83, 0.90] | 0.901 [0.87, 0.93] | 0.884 [0.85, 0.91] | 0.894 [0.87, 0.92] | 472 / 524 |
| phone | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.835 [0.79, 0.87] | 0.861 [0.82, 0.89] | 0.848 [0.81, 0.88] | 0.856 [0.82, 0.89] | 522 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.262 [0.15, 0.38] | 0.409 [0.23, 0.62] | 1.2 [0.4, 2.1] | 9 / 22 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.039 [0.03, 0.05] | 0.924 [0.90, 0.94] | 4.0 [2.7, 5.4] | 484 / 524 |
| phone | rules+xlmr-cs-sk-ce-more-s2 | 0.328 [0.09, 0.64] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+xlmr-cs-sk-ce-more-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.081 [0.05, 0.11] | 0.886 [0.85, 0.92] | 5.1 [3.6, 6.7] | 537 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.887 [0.80, 0.96] | 0.978 [0.96, 1.00] | 0.931 [0.88, 0.97] | 0.959 [0.94, 0.98] | 270 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.858 [0.76, 0.93] | 0.938 [0.89, 0.98] | 0.896 [0.83, 0.95] | 0.921 [0.87, 0.97] | 259 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.022 [0.00, 0.04] | 0.960 [0.91, 0.99] | 4.5 [1.5, 8.4] | 265 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.491 [0.32, 0.71] | 1.000 [1.00, 1.00] | 0.658 [0.48, 0.83] | 0.828 [0.70, 0.93] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.764 [0.61, 0.90] | 0.931 [0.81, 1.00] | 0.840 [0.73, 0.93] | 0.892 [0.79, 0.97] | 204 / 219 |
| phone | rules+xlmr-cs-sk-ce-more-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.775 [0.67, 0.87] | 0.874 [0.81, 0.92] | 0.821 [0.76, 0.87] | 0.852 [0.80, 0.90] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.382 [0.23, 0.60] | 0.778 [0.61, 0.94] | 0.512 [0.34, 0.71] | 0.644 [0.47, 0.81] | 21 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.569 [0.44, 0.72] | 0.694 [0.58, 0.81] | 0.625 [0.51, 0.75] | 0.665 [0.56, 0.77] | 152 / 219 |
| phone | rules+xlmr-cs-sk-ce-more-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.641 [0.54, 0.75] | 0.719 [0.66, 0.79] | 0.678 [0.60, 0.75] | 0.702 [0.64, 0.77] | 279 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 7.6 [2.6, 14.5] | 27 / 27 |
| birth_number | rules+xlmr-cs-sk-ce-more-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+xlmr-cs-sk-ce-more-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+xlmr-cs-sk-ce-more-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.052 [0.01, 0.14] | 0.886 [0.77, 0.97] | 10.3 [5.5, 16.9] | 194 / 219 |
| phone | rules+xlmr-cs-sk-ce-more-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.081 [0.05, 0.12] | 0.858 [0.79, 0.92] | 19.7 [12.0, 28.7] | 333 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.977 [0.97, 0.98] | 0.996 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.992 [0.99, 0.99] | 2110 / 2119 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.998 [1.00, 1.00] | 0.997 [1.00, 1.00] | 0.998 [1.00, 1.00] | 0.997 [1.00, 1.00] | 4341 / 4353 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.993 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 9058 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.853 [0.84, 0.87] | 0.887 [0.87, 0.90] | 0.870 [0.86, 0.88] | 0.880 [0.87, 0.89] | 1880 / 2119 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.985 [0.98, 0.99] | 0.984 [0.98, 0.99] | 0.985 [0.98, 0.99] | 0.985 [0.98, 0.99] | 4285 / 4353 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.945 [0.94, 0.95] | 0.952 [0.95, 0.96] | 0.949 [0.94, 0.95] | 0.951 [0.95, 0.96] | 8660 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.003 [0.00, 0.00] | 0.990 [0.99, 0.99] | 1.4 [1.1, 1.6] | 2097 / 2119 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.003 [0.00, 0.00] | 0.995 [0.99, 1.00] | 0.2 [0.1, 0.3] | 4330 / 4353 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.008 [0.01, 0.01] | 0.981 [0.98, 0.98] | 1.7 [1.4, 2.0] | 8922 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.968 [0.96, 0.97] | 0.996 [0.99, 1.00] | 0.982 [0.98, 0.99] | 0.990 [0.99, 0.99] | 2109 / 2118 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.998 [1.00, 1.00] | 0.997 [0.99, 1.00] | 0.997 [1.00, 1.00] | 0.997 [1.00, 1.00] | 4330 / 4344 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.991 [0.99, 0.99] | 0.996 [0.99, 1.00] | 0.993 [0.99, 0.99] | 0.995 [0.99, 1.00] | 8888 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.830 [0.81, 0.85] | 0.874 [0.86, 0.89] | 0.852 [0.84, 0.87] | 0.865 [0.85, 0.88] | 1851 / 2118 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.981 [0.98, 0.99] | 0.980 [0.97, 0.98] | 0.981 [0.98, 0.98] | 0.980 [0.97, 0.98] | 4256 / 4344 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.939 [0.93, 0.94] | 0.949 [0.94, 0.95] | 0.944 [0.94, 0.95] | 0.947 [0.94, 0.95] | 8467 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-ce-more-s2 | 0.004 [0.00, 0.01] | 0.990 [0.98, 0.99] | 1.6 [1.4, 1.9] | 2096 / 2118 |
| email | rules+xlmr-cs-sk-ce-more-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.002 [0.00, 0.00] | 0.995 [0.99, 1.00] | 0.3 [0.2, 0.4] | 4322 / 4344 |
| any | rules+xlmr-cs-sk-ce-more-s2 | 0.007 [0.01, 0.01] | 0.983 [0.98, 0.99] | 2.0 [1.7, 2.3] | 8779 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.944 [0.89, 0.98] | 0.980 [0.96, 0.99] | 0.962 [0.93, 0.99] | 0.973 [0.95, 0.99] | 292 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.863 [0.80, 0.92] | 0.886 [0.83, 0.93] | 0.874 [0.82, 0.92] | 0.881 [0.83, 0.92] | 264 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.032 [0.02, 0.05] | 0.913 [0.87, 0.95] | 3.0 [1.3, 4.9] | 272 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.992 [0.98, 1.00] | 0.960 [0.93, 0.98] | 0.976 [0.96, 0.99] | 0.966 [0.94, 0.98] | 380 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.992 [0.98, 1.00] | 0.960 [0.93, 0.98] | 0.976 [0.96, 0.99] | 0.966 [0.94, 0.98] | 380 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-ce-more-s2 | 0.046 [0.02, 0.08] | 0.960 [0.93, 0.98] | 0.2 [0.0, 0.4] | 380 / 396 |
