# train-cs-sk-weighted-w5-dev

rules+gliner-cs-sk-weighted-w5 after training (train-cs-sk-weighted-w5).

Stage: dev · commit 922797a75c · 2026-10-12T07:05:46+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-weighted-w5 @ 5bf8155a39 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.811 [0.70, 0.92] | 0.955 [0.82, 1.00] | 0.877 [0.77, 0.95] | 0.922 [0.81, 0.98] | 21 / 22 |
| email | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.886 [0.85, 0.92] | 0.945 [0.92, 0.96] | 0.914 [0.89, 0.94] | 0.932 [0.91, 0.95] | 495 / 524 |
| phone | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.889 [0.85, 0.92] | 0.937 [0.91, 0.96] | 0.913 [0.88, 0.94] | 0.927 [0.90, 0.95] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.108 [0.02, 0.24] | 0.182 [0.04, 0.40] | 0.136 [0.03, 0.30] | 0.160 [0.03, 0.35] | 4 / 22 |
| email | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.850 [0.81, 0.88] | 0.908 [0.88, 0.93] | 0.878 [0.85, 0.90] | 0.896 [0.87, 0.92] | 476 / 524 |
| phone | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.818 [0.78, 0.85] | 0.865 [0.82, 0.90] | 0.840 [0.80, 0.87] | 0.855 [0.82, 0.89] | 524 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.394 [0.27, 0.51] | 0.273 [0.09, 0.52] | 1.6 [0.6, 2.6] | 6 / 22 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.038 [0.03, 0.05] | 0.926 [0.91, 0.95] | 5.1 [3.6, 6.8] | 485 / 524 |
| phone | rules+gliner-cs-sk-weighted-w5 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w5 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.099 [0.07, 0.13] | 0.883 [0.84, 0.91] | 6.5 [4.5, 8.7] | 535 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w5 | 0.830 [0.75, 0.91] | 0.927 [0.89, 0.96] | 0.876 [0.82, 0.92] | 0.906 [0.87, 0.94] | 256 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w5 | 0.801 [0.72, 0.88] | 0.888 [0.84, 0.93] | 0.842 [0.79, 0.89] | 0.869 [0.83, 0.91] | 245 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w5 | 0.059 [0.03, 0.09] | 0.909 [0.86, 0.95] | 6.5 [3.1, 10.2] | 251 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w5 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.811 [0.65, 0.96] | 0.995 [0.99, 1.00] | 0.894 [0.78, 0.98] | 0.952 [0.90, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-weighted-w5 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.813 [0.70, 0.90] | 0.907 [0.86, 0.95] | 0.858 [0.79, 0.91] | 0.887 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.451 [0.30, 0.62] | 0.852 [0.69, 0.97] | 0.590 [0.43, 0.75] | 0.723 [0.56, 0.85] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w5 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.610 [0.46, 0.78] | 0.722 [0.62, 0.83] | 0.661 [0.54, 0.79] | 0.696 [0.59, 0.81] | 158 / 219 |
| phone | rules+gliner-cs-sk-weighted-w5 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.678 [0.58, 0.78] | 0.740 [0.68, 0.80] | 0.708 [0.64, 0.78] | 0.727 [0.67, 0.79] | 287 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.1 [3.0, 10.0] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w5 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-weighted-w5 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w5 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.008 [0.00, 0.02] | 0.982 [0.96, 1.00] | 10.8 [5.7, 17.4] | 215 / 219 |
| phone | rules+gliner-cs-sk-weighted-w5 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 18.7 [12.1, 26.5] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.994 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2030 / 2119 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.993 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4312 / 4353 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.995 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8955 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.846 [0.83, 0.86] | 0.831 [0.81, 0.85] | 0.838 [0.82, 0.85] | 0.834 [0.82, 0.85] | 1760 / 2119 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.980 [0.97, 0.99] | 0.978 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4257 / 4353 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.942 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.937 [0.93, 0.94] | 8514 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.083 [0.07, 0.10] | 0.936 [0.92, 0.95] | 1.1 [0.9, 1.2] | 1983 / 2119 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.007 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.4 [0.2, 0.5] | 4305 / 4353 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.2, 1.7] | 8783 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.993 [0.99, 1.00] | 0.963 [0.95, 0.97] | 0.978 [0.97, 0.98] | 0.969 [0.96, 0.98] | 2040 / 2118 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.995 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4304 / 4344 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.996 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8798 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.836 [0.82, 0.85] | 0.825 [0.81, 0.84] | 0.830 [0.81, 0.85] | 0.827 [0.81, 0.84] | 1747 / 2118 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.977 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4224 / 4344 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.940 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8335 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w5 | 0.090 [0.07, 0.11] | 0.945 [0.94, 0.95] | 1.2 [1.0, 1.5] | 2002 / 2118 |
| email | rules+gliner-cs-sk-weighted-w5 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-weighted-w5 | 0.007 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4288 / 4344 |
| any | rules+gliner-cs-sk-weighted-w5 | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.6 [1.4, 1.9] | 8651 / 8927 |
