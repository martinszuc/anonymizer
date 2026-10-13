# train-cs-sk-weighted-w10-dev

rules+gliner-cs-sk-weighted-w10 after training (train-cs-sk-weighted-w10).

Stage: dev · commit e44e907302 · 2026-10-12T13:29:08+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-weighted-w10 @ 8f0541dcc8 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.786 [0.66, 0.92] | 1.000 [1.00, 1.00] | 0.880 [0.79, 0.96] | 0.948 [0.91, 0.98] | 22 / 22 |
| email | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.885 [0.85, 0.92] | 0.937 [0.91, 0.96] | 0.910 [0.88, 0.93] | 0.926 [0.90, 0.95] | 491 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.886 [0.85, 0.92] | 0.934 [0.91, 0.96] | 0.909 [0.88, 0.93] | 0.924 [0.90, 0.95] | 566 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.095 [0.02, 0.21] | 0.182 [0.04, 0.40] | 0.125 [0.03, 0.28] | 0.154 [0.03, 0.34] | 4 / 22 |
| email | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.851 [0.81, 0.88] | 0.903 [0.88, 0.92] | 0.876 [0.85, 0.90] | 0.892 [0.87, 0.91] | 473 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.811 [0.77, 0.85] | 0.860 [0.82, 0.89] | 0.835 [0.80, 0.87] | 0.850 [0.81, 0.88] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.352 [0.24, 0.45] | 0.273 [0.09, 0.52] | 2.0 [0.7, 3.3] | 6 / 22 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.041 [0.03, 0.06] | 0.924 [0.90, 0.94] | 5.0 [3.5, 6.6] | 484 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.097 [0.07, 0.13] | 0.881 [0.84, 0.91] | 6.8 [4.4, 9.2] | 534 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10 | 0.821 [0.74, 0.90] | 0.935 [0.90, 0.97] | 0.874 [0.82, 0.92] | 0.909 [0.87, 0.94] | 258 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10 | 0.792 [0.71, 0.87] | 0.895 [0.84, 0.94] | 0.840 [0.79, 0.89] | 0.872 [0.83, 0.91] | 247 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10 | 0.054 [0.03, 0.08] | 0.917 [0.86, 0.96] | 7.2 [3.8, 11.1] | 253 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.538 [0.39, 0.69] | 1.000 [1.00, 1.00] | 0.700 [0.56, 0.82] | 0.854 [0.76, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.803 [0.63, 0.96] | 0.931 [0.81, 1.00] | 0.863 [0.74, 0.97] | 0.903 [0.80, 0.98] | 204 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.807 [0.70, 0.90] | 0.871 [0.81, 0.93] | 0.838 [0.77, 0.90] | 0.858 [0.80, 0.91] | 338 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.423 [0.28, 0.58] | 0.815 [0.64, 0.96] | 0.557 [0.40, 0.71] | 0.688 [0.52, 0.82] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.647 [0.49, 0.80] | 0.722 [0.62, 0.83] | 0.682 [0.57, 0.80] | 0.705 [0.61, 0.81] | 158 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.699 [0.60, 0.79] | 0.737 [0.68, 0.80] | 0.718 [0.65, 0.78] | 0.729 [0.68, 0.79] | 286 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.2 [3.0, 10.0] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-weighted-w10 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.050 [0.00, 0.13] | 0.922 [0.80, 1.00] | 9.6 [4.8, 16.2] | 202 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.083 [0.05, 0.12] | 0.876 [0.81, 0.94] | 17.6 [11.4, 25.3] | 340 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.994 [0.99, 1.00] | 0.959 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2031 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.992 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4314 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.995 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8955 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.847 [0.83, 0.86] | 0.832 [0.82, 0.85] | 0.839 [0.82, 0.85] | 0.835 [0.82, 0.85] | 1762 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.980 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.979 [0.97, 0.98] | 4261 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.943 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.940 [0.93, 0.94] | 0.938 [0.93, 0.94] | 8519 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.084 [0.07, 0.10] | 0.937 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1985 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.008 [0.01, 0.01] | 0.989 [0.99, 0.99] | 0.3 [0.2, 0.5] | 4306 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.3, 1.7] | 8786 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.992 [0.99, 1.00] | 0.963 [0.95, 0.97] | 0.977 [0.97, 0.98] | 0.968 [0.96, 0.97] | 2039 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.995 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4299 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.996 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8791 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.832 [0.82, 0.85] | 0.823 [0.81, 0.84] | 0.827 [0.81, 0.84] | 0.825 [0.81, 0.84] | 1743 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.975 [0.97, 0.98] | 0.969 [0.96, 0.97] | 0.972 [0.97, 0.98] | 0.970 [0.96, 0.98] | 4210 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.938 [0.93, 0.94] | 0.932 [0.93, 0.94] | 0.935 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8316 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10 | 0.091 [0.07, 0.11] | 0.942 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1996 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10 | 0.007 [0.00, 0.01] | 0.986 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4282 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10 | 0.037 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.6 [1.4, 1.9] | 8639 / 8927 |
