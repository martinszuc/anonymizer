# train-cs-sk-ce-gpu-dev

rules+gliner-cs-sk-ce-gpu after training (train-cs-sk-ce-gpu).

Stage: dev · commit 0211b3728e · 2026-10-14T19:46:00+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-ce-gpu @ d7ade2e1a6 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.829 [0.71, 0.94] | 0.909 [0.78, 1.00] | 0.867 [0.77, 0.95] | 0.892 [0.78, 0.98] | 20 / 22 |
| email | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-gpu | 0.912 [0.88, 0.94] | 0.943 [0.92, 0.96] | 0.927 [0.91, 0.95] | 0.936 [0.92, 0.95] | 494 / 524 |
| phone | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-gpu | 0.913 [0.88, 0.94] | 0.927 [0.89, 0.95] | 0.920 [0.89, 0.94] | 0.924 [0.90, 0.95] | 562 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.086 [0.00, 0.20] | 0.136 [0.00, 0.32] | 0.105 [0.00, 0.24] | 0.122 [0.00, 0.28] | 3 / 22 |
| email | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-gpu | 0.873 [0.84, 0.90] | 0.905 [0.88, 0.93] | 0.888 [0.86, 0.91] | 0.898 [0.87, 0.92] | 474 / 524 |
| phone | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-gpu | 0.838 [0.80, 0.87] | 0.860 [0.82, 0.89] | 0.849 [0.81, 0.88] | 0.855 [0.82, 0.89] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.411 [0.26, 0.55] | 0.227 [0.06, 0.46] | 1.3 [0.4, 2.2] | 5 / 22 |
| email | rules+gliner-cs-sk-ce-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-gpu | 0.043 [0.03, 0.06] | 0.918 [0.90, 0.94] | 3.7 [2.4, 5.1] | 481 / 524 |
| phone | rules+gliner-cs-sk-ce-gpu | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-gpu | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-gpu | 0.102 [0.07, 0.14] | 0.875 [0.84, 0.90] | 4.9 [3.2, 6.7] | 530 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-gpu | 0.859 [0.77, 0.94] | 0.913 [0.87, 0.95] | 0.885 [0.83, 0.93] | 0.902 [0.86, 0.93] | 252 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-gpu | 0.828 [0.74, 0.91] | 0.873 [0.83, 0.91] | 0.850 [0.80, 0.90] | 0.864 [0.82, 0.90] | 241 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-gpu | 0.071 [0.04, 0.10] | 0.895 [0.85, 0.94] | 5.4 [2.2, 9.0] | 247 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-gpu | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-gpu | 0.790 [0.63, 0.95] | 0.931 [0.82, 1.00] | 0.855 [0.74, 0.96] | 0.899 [0.80, 0.98] | 204 / 219 |
| phone | rules+gliner-cs-sk-ce-gpu | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-gpu | 0.801 [0.69, 0.90] | 0.871 [0.81, 0.93] | 0.835 [0.76, 0.89] | 0.856 [0.80, 0.91] | 338 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.431 [0.29, 0.59] | 0.815 [0.64, 0.96] | 0.564 [0.41, 0.71] | 0.692 [0.52, 0.83] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-gpu | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-gpu | 0.637 [0.48, 0.80] | 0.722 [0.62, 0.83] | 0.677 [0.56, 0.79] | 0.703 [0.61, 0.81] | 158 / 219 |
| phone | rules+gliner-cs-sk-ce-gpu | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-gpu | 0.694 [0.59, 0.79] | 0.737 [0.68, 0.80] | 0.715 [0.64, 0.78] | 0.728 [0.68, 0.79] | 286 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.1 [3.0, 10.0] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-ce-gpu | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-ce-gpu | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-gpu | 0.051 [0.00, 0.13] | 0.918 [0.80, 0.99] | 10.1 [5.3, 16.8] | 201 / 219 |
| phone | rules+gliner-cs-sk-ce-gpu | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-gpu | 0.083 [0.05, 0.12] | 0.874 [0.81, 0.93] | 18.0 [11.9, 25.9] | 339 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.997 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.976 [0.97, 0.98] | 0.963 [0.96, 0.97] | 2024 / 2119 |
| email | rules+gliner-cs-sk-ce-gpu | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-ce-gpu | 0.995 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4305 / 4353 |
| any | rules+gliner-cs-sk-ce-gpu | 0.997 [1.00, 1.00] | 0.983 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8940 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.849 [0.83, 0.86] | 0.828 [0.81, 0.84] | 0.838 [0.82, 0.85] | 0.832 [0.82, 0.85] | 1755 / 2119 |
| email | rules+gliner-cs-sk-ce-gpu | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-gpu | 0.984 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.979 [0.97, 0.98] | 4256 / 4353 |
| any | rules+gliner-cs-sk-ce-gpu | 0.945 [0.94, 0.95] | 0.935 [0.93, 0.94] | 0.940 [0.94, 0.95] | 0.937 [0.93, 0.94] | 8508 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.085 [0.07, 0.10] | 0.933 [0.92, 0.94] | 1.0 [0.9, 1.2] | 1978 / 2119 |
| email | rules+gliner-cs-sk-ce-gpu | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-gpu | 0.008 [0.01, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4299 / 4353 |
| any | rules+gliner-cs-sk-ce-gpu | 0.038 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8772 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.996 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.977 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2029 / 2118 |
| email | rules+gliner-cs-sk-ce-gpu | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-ce-gpu | 0.996 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4304 / 4344 |
| any | rules+gliner-cs-sk-ce-gpu | 0.997 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8786 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.841 [0.82, 0.86] | 0.823 [0.81, 0.84] | 0.832 [0.82, 0.85] | 0.827 [0.81, 0.84] | 1744 / 2118 |
| email | rules+gliner-cs-sk-ce-gpu | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-ce-gpu | 0.977 [0.97, 0.98] | 0.972 [0.96, 0.98] | 0.974 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4220 / 4344 |
| any | rules+gliner-cs-sk-ce-gpu | 0.941 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8327 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu | 0.092 [0.07, 0.11] | 0.942 [0.93, 0.95] | 1.1 [1.0, 1.3] | 1994 / 2118 |
| email | rules+gliner-cs-sk-ce-gpu | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-ce-gpu | 0.006 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4287 / 4344 |
| any | rules+gliner-cs-sk-ce-gpu | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8642 / 8927 |
