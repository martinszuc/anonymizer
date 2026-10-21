# train-xlmr-smoke-dev

rules+xlmr-cs-sk-smoke after training (train-xlmr-smoke).

Stage: dev · commit 156b8b704e · 2026-10-20T23:09:19+00:00 · seed 20261010, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, xlmr-cs-sk-smoke @ 3019da3d09 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

25 documents, 25 pages, 300 sentences or records. Gold spans: address 9, email 9, person 218, phone 16.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.556 [0.27, 1.00] | 0.714 [0.43, 1.00] | 0.610 [0.32, 1.00] | 5 / 9 |
| email | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 9 / 9 |
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 218 |
| phone | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.375 [0.00, 1.00] | 0.545 [0.00, 1.00] | 0.429 [0.00, 1.00] | 6 / 16 |
| url | rules+xlmr-cs-sk-smoke | – | – | – | – | 0 / 0 |
| any | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.079 [0.02, 0.17] | 0.147 [0.03, 0.29] | 0.097 [0.02, 0.20] | 20 / 252 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.200 [0.00, 0.67] | 0.111 [0.00, 0.50] | 0.143 [0.00, 0.50] | 0.122 [0.00, 0.50] | 1 / 9 |
| email | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 9 / 9 |
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 218 |
| phone | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.375 [0.00, 1.00] | 0.545 [0.00, 1.00] | 0.429 [0.00, 1.00] | 6 / 16 |
| url | rules+xlmr-cs-sk-smoke | – | – | – | – | 0 / 0 |
| any | rules+xlmr-cs-sk-smoke | 0.800 [0.17, 0.96] | 0.064 [0.00, 0.15] | 0.118 [0.01, 0.26] | 0.078 [0.01, 0.18] | 16 / 252 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.798 [0.41, 0.94] | 0.111 [0.00, 0.50] | 0.0 [0.0, 0.0] | 1 / 9 |
| email | rules+xlmr-cs-sk-smoke | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 9 / 9 |
| person | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 218 |
| phone | rules+xlmr-cs-sk-smoke | 0.460 [0.00, 1.00] | 0.375 [0.00, 1.00] | 0.0 [0.0, 0.0] | 6 / 16 |
| url | rules+xlmr-cs-sk-smoke | – | – | 0.0 [0.0, 0.0] | 0 / 0 |
| any | rules+xlmr-cs-sk-smoke | 0.884 [0.78, 0.97] | 0.064 [0.00, 0.15] | 0.0 [0.0, 0.0] | 16 / 252 |

## uner-sk-snk/dev · sk · dev

25 documents, 75 pages, 750 sentences or records. Gold spans: person 167.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 167 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 167 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 167 |

## redact/sample · cs · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 13, birth_number 14, date 22, email 33, id_number 4, person 134, phone 17.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.429 [0.17, 0.74] | 0.692 [0.40, 0.92] | 0.529 [0.25, 0.78] | 0.616 [0.33, 0.83] | 9 / 13 |
| birth_number | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.071 [0.00, 0.21] | 0.133 [0.00, 0.35] | 0.088 [0.00, 0.25] | 1 / 14 |
| date | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.500 [0.16, 0.84] | 0.667 [0.27, 0.91] | 0.556 [0.19, 0.87] | 11 / 22 |
| email | rules+xlmr-cs-sk-smoke | 0.917 [0.74, 1.00] | 1.000 [1.00, 1.00] | 0.957 [0.85, 1.00] | 0.982 [0.93, 1.00] | 33 / 33 |
| id_number | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 4 |
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 134 |
| phone | rules+xlmr-cs-sk-smoke | 0.889 [0.73, 1.00] | 0.941 [0.81, 1.00] | 0.914 [0.78, 1.00] | 0.930 [0.80, 1.00] | 16 / 17 |
| any | rules+xlmr-cs-sk-smoke | 0.816 [0.70, 0.92] | 0.300 [0.24, 0.36] | 0.438 [0.37, 0.50] | 0.343 [0.28, 0.40] | 71 / 237 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.191 [0.04, 0.43] | 0.308 [0.08, 0.62] | 0.235 [0.05, 0.46] | 0.274 [0.06, 0.53] | 4 / 13 |
| birth_number | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.071 [0.00, 0.21] | 0.133 [0.00, 0.35] | 0.088 [0.00, 0.25] | 1 / 14 |
| date | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.500 [0.16, 0.84] | 0.667 [0.27, 0.91] | 0.556 [0.19, 0.87] | 11 / 22 |
| email | rules+xlmr-cs-sk-smoke | 0.917 [0.74, 1.00] | 1.000 [1.00, 1.00] | 0.957 [0.85, 1.00] | 0.982 [0.93, 1.00] | 33 / 33 |
| id_number | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 4 |
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 134 |
| phone | rules+xlmr-cs-sk-smoke | 0.889 [0.73, 1.00] | 0.941 [0.81, 1.00] | 0.914 [0.78, 1.00] | 0.930 [0.80, 1.00] | 16 / 17 |
| any | rules+xlmr-cs-sk-smoke | 0.759 [0.64, 0.87] | 0.279 [0.22, 0.33] | 0.407 [0.34, 0.47] | 0.319 [0.26, 0.38] | 66 / 237 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.500 [0.21, 0.80] | 0.385 [0.08, 0.75] | 3.4 [1.0, 6.3] | 5 / 13 |
| birth_number | rules+xlmr-cs-sk-smoke | 0.607 [0.36, 0.85] | 0.429 [0.17, 0.67] | 0.0 [0.0, 0.0] | 6 / 14 |
| date | rules+xlmr-cs-sk-smoke | 0.508 [0.17, 0.84] | 0.500 [0.16, 0.84] | 0.0 [0.0, 0.0] | 11 / 22 |
| email | rules+xlmr-cs-sk-smoke | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.6 [0.0, 5.1] | 33 / 33 |
| id_number | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 4 |
| person | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 134 |
| phone | rules+xlmr-cs-sk-smoke | 0.057 [0.00, 0.18] | 0.941 [0.81, 1.00] | 0.2 [0.0, 0.7] | 16 / 17 |
| any | rules+xlmr-cs-sk-smoke | 0.569 [0.49, 0.65] | 0.300 [0.23, 0.37] | 5.2 [2.0, 9.2] | 71 / 237 |

## openpii-1m-cs/dev · cs · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 13, email 18, person 26.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.462 [0.20, 0.73] | 0.632 [0.33, 0.84] | 0.517 [0.24, 0.77] | 6 / 13 |
| email | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 18 / 18 |
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 26 |
| any | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.421 [0.31, 0.52] | 0.593 [0.47, 0.69] | 0.476 [0.36, 0.58] | 24 / 57 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.429 [0.00, 1.00] | 0.231 [0.00, 0.47] | 0.300 [0.00, 0.58] | 0.254 [0.00, 0.51] | 3 / 13 |
| email | rules+xlmr-cs-sk-smoke | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 17 / 18 |
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 26 |
| any | rules+xlmr-cs-sk-smoke | 0.800 [0.64, 0.95] | 0.351 [0.24, 0.44] | 0.488 [0.36, 0.59] | 0.395 [0.28, 0.49] | 20 / 57 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.598 [0.35, 0.85] | 0.231 [0.00, 0.47] | 0.0 [0.0, 0.0] | 3 / 13 |
| email | rules+xlmr-cs-sk-smoke | 0.016 [0.00, 0.06] | 0.944 [0.79, 1.00] | 0.0 [0.0, 0.0] | 17 / 18 |
| person | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 26 |
| any | rules+xlmr-cs-sk-smoke | 0.571 [0.47, 0.69] | 0.351 [0.24, 0.44] | 0.0 [0.0, 0.0] | 20 / 57 |

## openpii-1m-sk/dev · sk · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 9, email 15, person 36.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.444 [0.14, 0.75] | 0.615 [0.25, 0.86] | 0.500 [0.17, 0.79] | 4 / 9 |
| email | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 15 / 15 |
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 36 |
| any | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.317 [0.24, 0.38] | 0.481 [0.39, 0.55] | 0.367 [0.28, 0.43] | 19 / 60 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 9 |
| email | rules+xlmr-cs-sk-smoke | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 14 / 15 |
| person | rules+xlmr-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 36 |
| any | rules+xlmr-cs-sk-smoke | 0.700 [0.53, 0.92] | 0.233 [0.17, 0.30] | 0.350 [0.26, 0.44] | 0.269 [0.20, 0.34] | 14 / 60 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+xlmr-cs-sk-smoke | 0.655 [0.35, 0.95] | 0.111 [0.00, 0.38] | 0.1 [0.0, 0.4] | 1 / 9 |
| email | rules+xlmr-cs-sk-smoke | 0.011 [0.00, 0.04] | 0.933 [0.77, 1.00] | 0.0 [0.0, 0.0] | 14 / 15 |
| person | rules+xlmr-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 36 |
| any | rules+xlmr-cs-sk-smoke | 0.659 [0.57, 0.76] | 0.250 [0.18, 0.32] | 0.1 [0.0, 0.4] | 15 / 60 |
