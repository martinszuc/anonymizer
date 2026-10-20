# train-recipe-r10-s5k-dev

rules+gliner-recipe-r10-s5k after training (train-recipe-r10-s5k).

Stage: dev · commit 94ed4acc40 · 2026-10-15T22:18:16+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r10-s5k @ b6df8dd5fe · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.850 [0.69, 1.00] | 0.682 [0.52, 0.87] | 0.757 [0.61, 0.88] | 0.710 [0.56, 0.87] | 15 / 22 |
| email | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s5k | 0.914 [0.88, 0.94] | 0.937 [0.91, 0.96] | 0.925 [0.90, 0.95] | 0.932 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s5k | 0.923 [0.90, 0.95] | 0.917 [0.89, 0.95] | 0.920 [0.90, 0.94] | 0.919 [0.89, 0.94] | 556 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.300 [0.11, 0.53] | 0.273 [0.09, 0.53] | 0.286 [0.10, 0.50] | 0.278 [0.09, 0.51] | 6 / 22 |
| email | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s5k | 0.877 [0.84, 0.91] | 0.897 [0.87, 0.92] | 0.887 [0.86, 0.91] | 0.893 [0.87, 0.91] | 470 / 524 |
| phone | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s5k | 0.867 [0.83, 0.90] | 0.858 [0.82, 0.89] | 0.862 [0.83, 0.89] | 0.860 [0.82, 0.89] | 520 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.536 [0.36, 0.67] | 0.318 [0.12, 0.58] | 0.8 [0.2, 1.5] | 7 / 22 |
| email | rules+gliner-recipe-r10-s5k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r10-s5k | 0.050 [0.03, 0.07] | 0.910 [0.89, 0.93] | 3.4 [2.2, 4.7] | 477 / 524 |
| phone | rules+gliner-recipe-r10-s5k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r10-s5k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r10-s5k | 0.125 [0.08, 0.17] | 0.871 [0.83, 0.91] | 4.2 [2.7, 5.8] | 528 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s5k | 0.841 [0.76, 0.91] | 0.920 [0.87, 0.96] | 0.879 [0.83, 0.92] | 0.903 [0.86, 0.94] | 254 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s5k | 0.811 [0.73, 0.88] | 0.884 [0.83, 0.94] | 0.846 [0.79, 0.90] | 0.868 [0.82, 0.91] | 244 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s5k | 0.063 [0.03, 0.10] | 0.902 [0.85, 0.95] | 5.8 [2.9, 9.1] | 249 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.571 [0.40, 0.74] | 1.000 [1.00, 1.00] | 0.727 [0.57, 0.85] | 0.870 [0.77, 0.93] | 27 / 27 |
| birth_number | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s5k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s5k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s5k | 0.782 [0.62, 0.94] | 0.927 [0.81, 1.00] | 0.849 [0.73, 0.95] | 0.894 [0.80, 0.97] | 203 / 219 |
| phone | rules+gliner-recipe-r10-s5k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s5k | 0.800 [0.69, 0.89] | 0.869 [0.81, 0.92] | 0.833 [0.76, 0.89] | 0.854 [0.80, 0.90] | 337 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.449 [0.29, 0.62] | 0.815 [0.64, 0.96] | 0.579 [0.41, 0.73] | 0.701 [0.53, 0.84] | 22 / 27 |
| birth_number | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s5k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s5k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s5k | 0.617 [0.47, 0.78] | 0.699 [0.58, 0.82] | 0.655 [0.53, 0.78] | 0.681 [0.57, 0.80] | 153 / 219 |
| phone | rules+gliner-recipe-r10-s5k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s5k | 0.685 [0.58, 0.79] | 0.724 [0.66, 0.79] | 0.704 [0.63, 0.78] | 0.716 [0.65, 0.78] | 281 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.0 [2.8, 9.8] | 26 / 27 |
| birth_number | rules+gliner-recipe-r10-s5k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r10-s5k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r10-s5k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s5k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r10-s5k | 0.054 [0.00, 0.14] | 0.918 [0.80, 0.99] | 10.6 [5.7, 17.2] | 201 / 219 |
| phone | rules+gliner-recipe-r10-s5k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r10-s5k | 0.085 [0.05, 0.13] | 0.874 [0.81, 0.93] | 18.3 [12.3, 25.9] | 339 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.997 [0.99, 1.00] | 0.947 [0.94, 0.96] | 0.971 [0.97, 0.98] | 0.956 [0.95, 0.96] | 2006 / 2119 |
| email | rules+gliner-recipe-r10-s5k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r10-s5k | 0.996 [0.99, 1.00] | 0.987 [0.98, 0.99] | 0.992 [0.99, 0.99] | 0.989 [0.99, 0.99] | 4298 / 4353 |
| any | rules+gliner-recipe-r10-s5k | 0.997 [1.00, 1.00] | 0.980 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.983 [0.98, 0.99] | 8914 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.852 [0.84, 0.87] | 0.823 [0.81, 0.84] | 0.837 [0.82, 0.85] | 0.829 [0.81, 0.84] | 1744 / 2119 |
| email | rules+gliner-recipe-r10-s5k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s5k | 0.985 [0.98, 0.99] | 0.976 [0.97, 0.98] | 0.980 [0.98, 0.98] | 0.978 [0.97, 0.98] | 4249 / 4353 |
| any | rules+gliner-recipe-r10-s5k | 0.946 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.940 [0.93, 0.94] | 0.936 [0.93, 0.94] | 8489 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.091 [0.07, 0.11] | 0.927 [0.92, 0.94] | 1.0 [0.8, 1.1] | 1965 / 2119 |
| email | rules+gliner-recipe-r10-s5k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s5k | 0.009 [0.01, 0.01] | 0.986 [0.98, 0.99] | 0.2 [0.2, 0.3] | 4290 / 4353 |
| any | rules+gliner-recipe-r10-s5k | 0.040 [0.03, 0.05] | 0.962 [0.96, 0.97] | 1.3 [1.1, 1.5] | 8750 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.998 [1.00, 1.00] | 0.945 [0.93, 0.95] | 0.971 [0.97, 0.98] | 0.955 [0.95, 0.96] | 2002 / 2118 |
| email | rules+gliner-recipe-r10-s5k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r10-s5k | 0.995 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4296 / 4344 |
| any | rules+gliner-recipe-r10-s5k | 0.997 [1.00, 1.00] | 0.980 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8751 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.841 [0.82, 0.86] | 0.811 [0.79, 0.83] | 0.826 [0.81, 0.84] | 0.817 [0.80, 0.83] | 1718 / 2118 |
| email | rules+gliner-recipe-r10-s5k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r10-s5k | 0.977 [0.97, 0.98] | 0.970 [0.96, 0.98] | 0.973 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4215 / 4344 |
| any | rules+gliner-recipe-r10-s5k | 0.942 [0.94, 0.95] | 0.929 [0.92, 0.93] | 0.935 [0.93, 0.94] | 0.932 [0.93, 0.94] | 8297 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s5k | 0.099 [0.08, 0.12] | 0.930 [0.92, 0.94] | 1.1 [0.9, 1.3] | 1969 / 2118 |
| email | rules+gliner-recipe-r10-s5k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r10-s5k | 0.008 [0.01, 0.01] | 0.985 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4280 / 4344 |
| any | rules+gliner-recipe-r10-s5k | 0.041 [0.03, 0.05] | 0.965 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8610 / 8927 |
