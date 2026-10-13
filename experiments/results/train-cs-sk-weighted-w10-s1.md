# train-cs-sk-weighted-w10-s1-dev

rules+gliner-cs-sk-weighted-w10-s1 after training (train-cs-sk-weighted-w10-s1).

Stage: dev · commit e44e907302 · 2026-10-12T14:47:01+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-weighted-w10-s1 @ b7fb37b541 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.762 [0.63, 0.89] | 1.000 [1.00, 1.00] | 0.865 [0.77, 0.94] | 0.941 [0.89, 0.97] | 22 / 22 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.878 [0.84, 0.91] | 0.947 [0.92, 0.97] | 0.911 [0.88, 0.93] | 0.932 [0.91, 0.95] | 496 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.879 [0.84, 0.91] | 0.939 [0.91, 0.96] | 0.908 [0.88, 0.93] | 0.926 [0.90, 0.95] | 569 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.095 [0.02, 0.21] | 0.182 [0.04, 0.42] | 0.125 [0.03, 0.27] | 0.154 [0.03, 0.34] | 4 / 22 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.841 [0.80, 0.88] | 0.906 [0.88, 0.93] | 0.872 [0.84, 0.90] | 0.892 [0.87, 0.91] | 475 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.803 [0.76, 0.84] | 0.863 [0.82, 0.90] | 0.832 [0.79, 0.87] | 0.850 [0.81, 0.88] | 523 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.365 [0.25, 0.45] | 0.273 [0.10, 0.55] | 1.9 [0.8, 3.3] | 6 / 22 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.036 [0.02, 0.05] | 0.927 [0.91, 0.95] | 5.5 [4.0, 7.2] | 486 / 524 |
| phone | rules+gliner-cs-sk-weighted-w10-s1 | 0.318 [0.08, 0.62] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted-w10-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.094 [0.06, 0.12] | 0.884 [0.85, 0.92] | 7.2 [5.0, 9.8] | 536 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.827 [0.74, 0.90] | 0.946 [0.91, 0.97] | 0.882 [0.83, 0.93] | 0.919 [0.88, 0.95] | 261 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.795 [0.71, 0.87] | 0.899 [0.85, 0.93] | 0.844 [0.79, 0.89] | 0.876 [0.83, 0.91] | 248 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.045 [0.02, 0.07] | 0.927 [0.88, 0.96] | 6.7 [3.5, 10.6] | 256 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.538 [0.39, 0.70] | 1.000 [1.00, 1.00] | 0.700 [0.56, 0.82] | 0.854 [0.76, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.804 [0.64, 0.95] | 0.991 [0.97, 1.00] | 0.888 [0.78, 0.97] | 0.947 [0.89, 0.99] | 217 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.807 [0.70, 0.89] | 0.905 [0.86, 0.94] | 0.853 [0.78, 0.91] | 0.883 [0.83, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.423 [0.28, 0.59] | 0.815 [0.62, 0.96] | 0.557 [0.39, 0.71] | 0.688 [0.51, 0.83] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.589 [0.44, 0.75] | 0.699 [0.58, 0.82] | 0.639 [0.51, 0.78] | 0.673 [0.55, 0.80] | 153 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.661 [0.56, 0.76] | 0.724 [0.65, 0.79] | 0.691 [0.61, 0.77] | 0.711 [0.64, 0.78] | 281 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.021 [0.00, 0.07] | 0.963 [0.87, 1.00] | 6.7 [3.0, 11.3] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-weighted-w10-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-weighted-w10-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted-w10-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.009 [0.00, 0.02] | 0.982 [0.95, 1.00] | 11.4 [6.0, 18.3] | 215 / 219 |
| phone | rules+gliner-cs-sk-weighted-w10-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.066 [0.04, 0.10] | 0.910 [0.86, 0.95] | 19.8 [13.0, 28.2] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.995 [0.99, 1.00] | 0.957 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2028 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.992 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4317 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8957 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.849 [0.83, 0.86] | 0.833 [0.82, 0.85] | 0.841 [0.83, 0.86] | 0.836 [0.82, 0.85] | 1765 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.980 [0.97, 0.99] | 0.979 [0.97, 0.98] | 0.980 [0.98, 0.98] | 0.980 [0.97, 0.98] | 4263 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.943 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.940 [0.93, 0.95] | 0.938 [0.93, 0.94] | 8524 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.084 [0.07, 0.10] | 0.937 [0.93, 0.95] | 1.1 [0.9, 1.2] | 1986 / 2119 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.4 [0.2, 0.5] | 4310 / 4353 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.036 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.3, 1.7] | 8791 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.992 [0.99, 1.00] | 0.962 [0.95, 0.97] | 0.977 [0.97, 0.98] | 0.968 [0.96, 0.97] | 2038 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.994 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4303 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.996 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.99, 0.99] | 8796 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.833 [0.82, 0.85] | 0.824 [0.81, 0.84] | 0.829 [0.81, 0.84] | 0.826 [0.81, 0.84] | 1746 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.976 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.974 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4223 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.939 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8333 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted-w10-s1 | 0.090 [0.07, 0.11] | 0.943 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1997 / 2118 |
| email | rules+gliner-cs-sk-weighted-w10-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-weighted-w10-s1 | 0.006 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.5] | 4289 / 4344 |
| any | rules+gliner-cs-sk-weighted-w10-s1 | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.6 [1.4, 1.9] | 8647 / 8927 |
