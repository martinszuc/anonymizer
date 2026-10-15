# train-sk-ce-dev

rules+gliner-sk-ce after training (train-sk-ce).

Stage: dev · commit 0211b3728e · 2026-10-14T20:49:30+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-sk-ce @ 3c04733043 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.531 [0.39, 0.67] | 1.000 [1.00, 1.00] | 0.694 [0.56, 0.80] | 0.850 [0.76, 0.91] | 22 / 22 |
| email | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-sk-ce | 0.891 [0.85, 0.93] | 0.908 [0.87, 0.94] | 0.900 [0.87, 0.93] | 0.905 [0.88, 0.93] | 476 / 524 |
| phone | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-sk-ce | 0.871 [0.83, 0.91] | 0.917 [0.89, 0.95] | 0.893 [0.86, 0.92] | 0.908 [0.88, 0.93] | 556 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.047 [0.00, 0.10] | 0.136 [0.00, 0.32] | 0.070 [0.00, 0.15] | 0.099 [0.00, 0.21] | 3 / 22 |
| email | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-sk-ce | 0.831 [0.79, 0.87] | 0.832 [0.79, 0.87] | 0.831 [0.80, 0.86] | 0.832 [0.80, 0.86] | 436 / 524 |
| phone | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-sk-ce | 0.766 [0.72, 0.81] | 0.800 [0.76, 0.84] | 0.783 [0.74, 0.82] | 0.793 [0.75, 0.83] | 485 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.380 [0.28, 0.47] | 0.227 [0.06, 0.46] | 4.4 [2.6, 6.2] | 5 / 22 |
| email | rules+gliner-sk-ce | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-sk-ce | 0.061 [0.04, 0.08] | 0.903 [0.87, 0.93] | 4.9 [3.3, 6.4] | 473 / 524 |
| phone | rules+gliner-sk-ce | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-sk-ce | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-sk-ce | 0.115 [0.08, 0.15] | 0.861 [0.82, 0.90] | 9.3 [6.7, 11.7] | 522 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-sk-ce | 0.823 [0.73, 0.91] | 0.841 [0.77, 0.90] | 0.832 [0.77, 0.88] | 0.837 [0.78, 0.89] | 232 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-sk-ce | 0.798 [0.70, 0.89] | 0.815 [0.74, 0.88] | 0.806 [0.74, 0.86] | 0.812 [0.75, 0.87] | 225 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-sk-ce | 0.135 [0.08, 0.19] | 0.826 [0.76, 0.89] | 6.2 [2.8, 10.4] | 228 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.500 [0.35, 0.67] | 1.000 [1.00, 1.00] | 0.667 [0.52, 0.80] | 0.833 [0.73, 0.91] | 27 / 27 |
| birth_number | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-sk-ce | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-sk-ce | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-sk-ce | 0.785 [0.62, 0.95] | 0.922 [0.81, 0.99] | 0.848 [0.73, 0.95] | 0.891 [0.79, 0.97] | 202 / 219 |
| phone | rules+gliner-sk-ce | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-sk-ce | 0.790 [0.67, 0.89] | 0.866 [0.80, 0.92] | 0.826 [0.75, 0.89] | 0.850 [0.80, 0.90] | 336 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.389 [0.25, 0.55] | 0.778 [0.62, 0.93] | 0.518 [0.37, 0.67] | 0.648 [0.48, 0.79] | 21 / 27 |
| birth_number | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-sk-ce | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-sk-ce | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-sk-ce | 0.632 [0.48, 0.79] | 0.712 [0.61, 0.82] | 0.669 [0.56, 0.78] | 0.695 [0.59, 0.80] | 156 / 219 |
| phone | rules+gliner-sk-ce | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-sk-ce | 0.684 [0.58, 0.78] | 0.729 [0.67, 0.79] | 0.706 [0.63, 0.77] | 0.720 [0.66, 0.78] | 283 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 8.0 [3.5, 13.7] | 26 / 27 |
| birth_number | rules+gliner-sk-ce | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-sk-ce | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-sk-ce | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-sk-ce | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-sk-ce | 0.057 [0.01, 0.14] | 0.909 [0.79, 0.99] | 10.1 [5.2, 16.7] | 199 / 219 |
| phone | rules+gliner-sk-ce | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-sk-ce | 0.086 [0.05, 0.13] | 0.869 [0.80, 0.93] | 19.8 [12.2, 28.8] | 337 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.992 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.974 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2029 / 2119 |
| email | rules+gliner-sk-ce | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-sk-ce | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.995 [0.99, 1.00] | 4329 / 4353 |
| any | rules+gliner-sk-ce | 0.995 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8969 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.821 [0.80, 0.84] | 0.808 [0.79, 0.83] | 0.815 [0.80, 0.83] | 0.811 [0.80, 0.83] | 1713 / 2119 |
| email | rules+gliner-sk-ce | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-sk-ce | 0.976 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.976 [0.97, 0.98] | 4247 / 4353 |
| any | rules+gliner-sk-ce | 0.934 [0.93, 0.94] | 0.929 [0.92, 0.93] | 0.932 [0.93, 0.94] | 0.930 [0.93, 0.94] | 8456 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.091 [0.08, 0.11] | 0.913 [0.90, 0.92] | 1.1 [0.9, 1.2] | 1934 / 2119 |
| email | rules+gliner-sk-ce | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-sk-ce | 0.004 [0.00, 0.01] | 0.993 [0.99, 1.00] | 0.4 [0.3, 0.5] | 4324 / 4353 |
| any | rules+gliner-sk-ce | 0.038 [0.03, 0.04] | 0.962 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8753 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.992 [0.99, 1.00] | 0.968 [0.96, 0.98] | 0.980 [0.98, 0.98] | 0.973 [0.97, 0.98] | 2050 / 2118 |
| email | rules+gliner-sk-ce | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-sk-ce | 0.997 [0.99, 1.00] | 0.994 [0.99, 1.00] | 0.996 [0.99, 1.00] | 0.995 [0.99, 1.00] | 4319 / 4344 |
| any | rules+gliner-sk-ce | 0.996 [0.99, 1.00] | 0.988 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 8819 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.841 [0.82, 0.86] | 0.837 [0.82, 0.85] | 0.839 [0.82, 0.85] | 0.837 [0.82, 0.85] | 1772 / 2118 |
| email | rules+gliner-sk-ce | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-sk-ce | 0.979 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4240 / 4344 |
| any | rules+gliner-sk-ce | 0.942 [0.94, 0.95] | 0.938 [0.93, 0.94] | 0.940 [0.93, 0.94] | 0.939 [0.93, 0.94] | 8373 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-sk-ce | 0.088 [0.07, 0.11] | 0.949 [0.94, 0.96] | 1.1 [0.9, 1.3] | 2009 / 2118 |
| email | rules+gliner-sk-ce | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-sk-ce | 0.004 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4306 / 4344 |
| any | rules+gliner-sk-ce | 0.035 [0.03, 0.04] | 0.972 [0.97, 0.98] | 1.5 [1.3, 1.8] | 8676 / 8927 |
