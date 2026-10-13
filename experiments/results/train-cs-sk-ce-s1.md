# train-cs-sk-ce-s1-dev

rules+gliner-cs-sk-ce-s1 after training (train-cs-sk-ce-s1).

Stage: dev · commit e44e907302 · 2026-10-12T02:48:13+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-ce-s1 @ 41418e7b74 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.938 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.968 [0.92, 1.00] | 0.987 [0.96, 1.00] | 22 / 22 |
| email | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-s1 | 0.913 [0.88, 0.94] | 0.937 [0.91, 0.96] | 0.925 [0.90, 0.94] | 0.932 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-s1 | 0.920 [0.89, 0.95] | 0.929 [0.90, 0.95] | 0.925 [0.90, 0.94] | 0.927 [0.90, 0.95] | 563 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.125 [0.03, 0.29] | 0.182 [0.04, 0.42] | 0.148 [0.03, 0.33] | 0.167 [0.04, 0.37] | 4 / 22 |
| email | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-s1 | 0.874 [0.84, 0.90] | 0.897 [0.87, 0.92] | 0.885 [0.86, 0.91] | 0.892 [0.87, 0.91] | 470 / 524 |
| phone | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-s1 | 0.844 [0.80, 0.88] | 0.855 [0.82, 0.89] | 0.849 [0.81, 0.88] | 0.853 [0.81, 0.88] | 518 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.380 [0.26, 0.48] | 0.273 [0.10, 0.55] | 0.6 [0.1, 1.2] | 6 / 22 |
| email | rules+gliner-cs-sk-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-s1 | 0.045 [0.03, 0.06] | 0.918 [0.90, 0.94] | 3.7 [2.5, 5.2] | 481 / 524 |
| phone | rules+gliner-cs-sk-ce-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-s1 | 0.103 [0.07, 0.13] | 0.876 [0.84, 0.91] | 4.2 [3.0, 5.8] | 531 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-s1 | 0.843 [0.75, 0.92] | 0.920 [0.88, 0.95] | 0.880 [0.82, 0.93] | 0.904 [0.86, 0.94] | 254 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-s1 | 0.813 [0.72, 0.90] | 0.880 [0.83, 0.92] | 0.845 [0.79, 0.90] | 0.866 [0.82, 0.90] | 243 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-s1 | 0.063 [0.04, 0.09] | 0.902 [0.85, 0.94] | 5.8 [2.7, 9.8] | 249 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.540 [0.40, 0.69] | 1.000 [1.00, 1.00] | 0.701 [0.57, 0.82] | 0.854 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-s1 | 0.816 [0.64, 0.96] | 0.995 [0.98, 1.00] | 0.897 [0.78, 0.98] | 0.954 [0.90, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-ce-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-s1 | 0.816 [0.70, 0.91] | 0.907 [0.86, 0.95] | 0.859 [0.79, 0.91] | 0.887 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.440 [0.29, 0.60] | 0.815 [0.62, 0.96] | 0.571 [0.40, 0.72] | 0.696 [0.52, 0.84] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-s1 | 0.602 [0.45, 0.76] | 0.703 [0.58, 0.83] | 0.648 [0.52, 0.79] | 0.680 [0.56, 0.80] | 154 / 219 |
| phone | rules+gliner-cs-sk-ce-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-s1 | 0.673 [0.57, 0.77] | 0.727 [0.66, 0.80] | 0.699 [0.62, 0.78] | 0.715 [0.65, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.021 [0.00, 0.07] | 0.963 [0.87, 1.00] | 5.9 [2.7, 9.7] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-ce-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-ce-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-s1 | 0.007 [0.00, 0.02] | 0.986 [0.97, 1.00] | 11.1 [5.8, 18.0] | 216 / 219 |
| phone | rules+gliner-cs-sk-ce-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-s1 | 0.065 [0.03, 0.10] | 0.912 [0.86, 0.95] | 18.7 [12.1, 26.6] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.995 [0.99, 1.00] | 0.954 [0.94, 0.96] | 0.974 [0.97, 0.98] | 0.962 [0.95, 0.97] | 2022 / 2119 |
| email | rules+gliner-cs-sk-ce-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-ce-s1 | 0.995 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4312 / 4353 |
| any | rules+gliner-cs-sk-ce-s1 | 0.996 [0.99, 1.00] | 0.983 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8945 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.850 [0.83, 0.87] | 0.831 [0.81, 0.85] | 0.840 [0.82, 0.86] | 0.834 [0.82, 0.85] | 1760 / 2119 |
| email | rules+gliner-cs-sk-ce-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-s1 | 0.984 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.982 [0.98, 0.99] | 0.980 [0.98, 0.98] | 4261 / 4353 |
| any | rules+gliner-cs-sk-ce-s1 | 0.945 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8517 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.086 [0.07, 0.10] | 0.933 [0.92, 0.94] | 1.1 [0.9, 1.2] | 1978 / 2119 |
| email | rules+gliner-cs-sk-ce-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-s1 | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4309 / 4353 |
| any | rules+gliner-cs-sk-ce-s1 | 0.038 [0.03, 0.04] | 0.965 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8782 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.994 [0.99, 1.00] | 0.959 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.966 [0.96, 0.97] | 2031 / 2118 |
| email | rules+gliner-cs-sk-ce-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-ce-s1 | 0.996 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4304 / 4344 |
| any | rules+gliner-cs-sk-ce-s1 | 0.997 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8789 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.839 [0.82, 0.85] | 0.825 [0.81, 0.84] | 0.832 [0.82, 0.85] | 0.828 [0.81, 0.84] | 1747 / 2118 |
| email | rules+gliner-cs-sk-ce-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-ce-s1 | 0.978 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4226 / 4344 |
| any | rules+gliner-cs-sk-ce-s1 | 0.941 [0.94, 0.95] | 0.934 [0.93, 0.94] | 0.938 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8336 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-s1 | 0.092 [0.07, 0.11] | 0.940 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1990 / 2118 |
| email | rules+gliner-cs-sk-ce-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-ce-s1 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4291 / 4344 |
| any | rules+gliner-cs-sk-ce-s1 | 0.037 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8642 / 8927 |
