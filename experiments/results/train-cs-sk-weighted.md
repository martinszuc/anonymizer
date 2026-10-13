# train-cs-sk-weighted-dev

rules+gliner-cs-sk-weighted after training (train-cs-sk-weighted).

Stage: dev · commit e44e907302 · 2026-10-12T01:31:22+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-weighted @ 8a9742a93d · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.865 [0.76, 0.96] | 1.000 [1.00, 1.00] | 0.927 [0.87, 0.98] | 0.970 [0.94, 0.99] | 22 / 22 |
| email | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted | 0.898 [0.86, 0.93] | 0.937 [0.91, 0.96] | 0.917 [0.89, 0.94] | 0.929 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted | 0.903 [0.87, 0.94] | 0.931 [0.90, 0.95] | 0.917 [0.89, 0.94] | 0.925 [0.90, 0.95] | 564 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.108 [0.02, 0.24] | 0.182 [0.04, 0.40] | 0.136 [0.03, 0.30] | 0.160 [0.03, 0.35] | 4 / 22 |
| email | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted | 0.863 [0.83, 0.90] | 0.903 [0.88, 0.92] | 0.882 [0.86, 0.90] | 0.894 [0.87, 0.91] | 473 / 524 |
| phone | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted | 0.828 [0.79, 0.86] | 0.860 [0.82, 0.89] | 0.844 [0.81, 0.87] | 0.853 [0.81, 0.88] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.361 [0.24, 0.46] | 0.273 [0.09, 0.52] | 1.0 [0.3, 1.9] | 6 / 22 |
| email | rules+gliner-cs-sk-weighted | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-weighted | 0.044 [0.03, 0.06] | 0.920 [0.90, 0.94] | 4.4 [2.9, 5.8] | 482 / 524 |
| phone | rules+gliner-cs-sk-weighted | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-weighted | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-weighted | 0.100 [0.07, 0.13] | 0.878 [0.84, 0.91] | 5.3 [3.6, 7.1] | 532 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted | 0.843 [0.76, 0.92] | 0.924 [0.89, 0.96] | 0.882 [0.83, 0.93] | 0.907 [0.87, 0.94] | 255 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted | 0.813 [0.73, 0.89] | 0.884 [0.84, 0.93] | 0.847 [0.79, 0.90] | 0.869 [0.82, 0.91] | 244 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-weighted | 0.065 [0.04, 0.09] | 0.906 [0.86, 0.95] | 5.8 [2.7, 9.4] | 250 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.540 [0.39, 0.70] | 1.000 [1.00, 1.00] | 0.701 [0.56, 0.82] | 0.854 [0.76, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted | 0.797 [0.62, 0.96] | 0.931 [0.81, 1.00] | 0.859 [0.73, 0.97] | 0.901 [0.80, 0.98] | 204 / 219 |
| phone | rules+gliner-cs-sk-weighted | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted | 0.807 [0.70, 0.90] | 0.871 [0.81, 0.93] | 0.838 [0.77, 0.90] | 0.858 [0.80, 0.91] | 338 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.440 [0.29, 0.60] | 0.815 [0.64, 0.96] | 0.571 [0.41, 0.72] | 0.696 [0.53, 0.83] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted | 0.630 [0.48, 0.79] | 0.708 [0.60, 0.82] | 0.667 [0.55, 0.79] | 0.691 [0.58, 0.80] | 155 / 219 |
| phone | rules+gliner-cs-sk-weighted | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted | 0.692 [0.59, 0.79] | 0.729 [0.67, 0.80] | 0.710 [0.64, 0.78] | 0.722 [0.66, 0.79] | 283 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 5.9 [2.7, 9.7] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-weighted | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-weighted | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-weighted | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-sk-weighted | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-weighted | 0.050 [0.00, 0.13] | 0.922 [0.80, 1.00] | 9.8 [4.8, 16.7] | 202 / 219 |
| phone | rules+gliner-cs-sk-weighted | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-sk-weighted | 0.083 [0.05, 0.12] | 0.876 [0.81, 0.94] | 17.4 [11.2, 25.2] | 340 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.994 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.974 [0.97, 0.98] | 0.963 [0.95, 0.97] | 2024 / 2119 |
| email | rules+gliner-cs-sk-weighted | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-weighted | 0.995 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4314 / 4353 |
| any | rules+gliner-cs-sk-weighted | 0.996 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8950 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.846 [0.83, 0.86] | 0.829 [0.81, 0.84] | 0.837 [0.82, 0.85] | 0.832 [0.82, 0.85] | 1756 / 2119 |
| email | rules+gliner-cs-sk-weighted | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted | 0.983 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.980 [0.97, 0.98] | 4261 / 4353 |
| any | rules+gliner-cs-sk-weighted | 0.944 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.940 [0.93, 0.94] | 0.937 [0.93, 0.94] | 8513 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.085 [0.07, 0.10] | 0.934 [0.92, 0.94] | 1.1 [0.9, 1.3] | 1980 / 2119 |
| email | rules+gliner-cs-sk-weighted | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-weighted | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4308 / 4353 |
| any | rules+gliner-cs-sk-weighted | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.2, 1.7] | 8783 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.995 [0.99, 1.00] | 0.961 [0.95, 0.97] | 0.978 [0.97, 0.98] | 0.968 [0.96, 0.97] | 2036 / 2118 |
| email | rules+gliner-cs-sk-weighted | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-weighted | 0.996 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4301 / 4344 |
| any | rules+gliner-cs-sk-weighted | 0.997 [1.00, 1.00] | 0.985 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8790 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.835 [0.82, 0.85] | 0.822 [0.80, 0.84] | 0.828 [0.81, 0.84] | 0.824 [0.81, 0.84] | 1740 / 2118 |
| email | rules+gliner-cs-sk-weighted | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-weighted | 0.976 [0.97, 0.98] | 0.970 [0.96, 0.98] | 0.973 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4215 / 4344 |
| any | rules+gliner-cs-sk-weighted | 0.940 [0.93, 0.94] | 0.932 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8318 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-weighted | 0.091 [0.07, 0.11] | 0.942 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1995 / 2118 |
| email | rules+gliner-cs-sk-weighted | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-weighted | 0.007 [0.00, 0.01] | 0.986 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4283 / 4344 |
| any | rules+gliner-cs-sk-weighted | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.6 [1.4, 1.8] | 8639 / 8927 |
