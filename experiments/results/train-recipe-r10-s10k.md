# train-recipe-r10-s10k-dev

rules+gliner-recipe-r10-s10k after training (train-recipe-r10-s10k).

Stage: dev · commit 94ed4acc40 · 2026-10-15T22:40:56+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r10-s10k @ dbc1a7da2c · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.905 [0.77, 1.00] | 0.773 [0.60, 0.93] | 0.834 [0.70, 0.93] | 0.796 [0.64, 0.92] | 17 / 22 |
| email | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s10k | 0.930 [0.90, 0.96] | 0.947 [0.92, 0.97] | 0.938 [0.92, 0.96] | 0.943 [0.92, 0.96] | 496 / 524 |
| phone | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s10k | 0.936 [0.91, 0.96] | 0.924 [0.89, 0.95] | 0.930 [0.91, 0.95] | 0.926 [0.90, 0.95] | 560 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.191 [0.04, 0.37] | 0.182 [0.04, 0.39] | 0.186 [0.04, 0.37] | 0.183 [0.04, 0.38] | 4 / 22 |
| email | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s10k | 0.891 [0.85, 0.92] | 0.905 [0.88, 0.93] | 0.898 [0.87, 0.92] | 0.902 [0.87, 0.93] | 474 / 524 |
| phone | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s10k | 0.874 [0.84, 0.91] | 0.861 [0.82, 0.90] | 0.868 [0.83, 0.90] | 0.864 [0.82, 0.90] | 522 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.528 [0.39, 0.65] | 0.182 [0.04, 0.39] | 0.5 [0.1, 1.1] | 4 / 22 |
| email | rules+gliner-recipe-r10-s10k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r10-s10k | 0.044 [0.03, 0.06] | 0.916 [0.89, 0.94] | 2.9 [1.7, 4.2] | 480 / 524 |
| phone | rules+gliner-recipe-r10-s10k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r10-s10k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r10-s10k | 0.119 [0.08, 0.16] | 0.871 [0.83, 0.91] | 3.4 [2.1, 4.8] | 528 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s10k | 0.845 [0.77, 0.92] | 0.906 [0.86, 0.95] | 0.874 [0.82, 0.92] | 0.893 [0.85, 0.93] | 250 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s10k | 0.821 [0.74, 0.90] | 0.880 [0.83, 0.93] | 0.850 [0.79, 0.90] | 0.868 [0.82, 0.91] | 243 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s10k | 0.082 [0.05, 0.12] | 0.888 [0.83, 0.94] | 5.6 [2.6, 8.9] | 245 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.571 [0.40, 0.74] | 1.000 [1.00, 1.00] | 0.727 [0.57, 0.85] | 0.870 [0.77, 0.93] | 27 / 27 |
| birth_number | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s10k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s10k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s10k | 0.795 [0.62, 0.95] | 0.927 [0.81, 1.00] | 0.856 [0.73, 0.96] | 0.897 [0.80, 0.97] | 203 / 219 |
| phone | rules+gliner-recipe-r10-s10k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s10k | 0.808 [0.69, 0.90] | 0.866 [0.80, 0.92] | 0.836 [0.76, 0.89] | 0.854 [0.80, 0.90] | 336 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.469 [0.31, 0.63] | 0.852 [0.68, 1.00] | 0.605 [0.44, 0.75] | 0.733 [0.57, 0.87] | 23 / 27 |
| birth_number | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s10k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s10k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s10k | 0.631 [0.47, 0.79] | 0.703 [0.59, 0.82] | 0.665 [0.54, 0.79] | 0.688 [0.58, 0.80] | 154 / 219 |
| phone | rules+gliner-recipe-r10-s10k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s10k | 0.697 [0.59, 0.80] | 0.729 [0.67, 0.79] | 0.713 [0.64, 0.78] | 0.723 [0.66, 0.79] | 283 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.0 [2.8, 9.8] | 26 / 27 |
| birth_number | rules+gliner-recipe-r10-s10k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r10-s10k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r10-s10k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s10k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r10-s10k | 0.057 [0.01, 0.14] | 0.913 [0.80, 0.99] | 9.9 [4.9, 16.8] | 200 / 219 |
| phone | rules+gliner-recipe-r10-s10k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r10-s10k | 0.086 [0.05, 0.13] | 0.871 [0.80, 0.93] | 17.7 [11.4, 25.6] | 338 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.999 [1.00, 1.00] | 0.949 [0.94, 0.96] | 0.973 [0.97, 0.98] | 0.958 [0.95, 0.97] | 2010 / 2119 |
| email | rules+gliner-recipe-r10-s10k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r10-s10k | 0.997 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 4320 / 4353 |
| any | rules+gliner-recipe-r10-s10k | 0.998 [1.00, 1.00] | 0.983 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8938 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.863 [0.85, 0.88] | 0.833 [0.82, 0.85] | 0.848 [0.83, 0.86] | 0.839 [0.82, 0.85] | 1766 / 2119 |
| email | rules+gliner-recipe-r10-s10k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s10k | 0.986 [0.98, 0.99] | 0.981 [0.98, 0.99] | 0.983 [0.98, 0.99] | 0.982 [0.98, 0.99] | 4270 / 4353 |
| any | rules+gliner-recipe-r10-s10k | 0.949 [0.94, 0.95] | 0.938 [0.93, 0.94] | 0.943 [0.94, 0.95] | 0.940 [0.94, 0.95] | 8532 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.087 [0.07, 0.10] | 0.934 [0.92, 0.94] | 0.9 [0.8, 1.1] | 1980 / 2119 |
| email | rules+gliner-recipe-r10-s10k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s10k | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.2 [0.2, 0.3] | 4310 / 4353 |
| any | rules+gliner-recipe-r10-s10k | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.2 [1.0, 1.4] | 8785 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.999 [1.00, 1.00] | 0.952 [0.94, 0.96] | 0.975 [0.97, 0.98] | 0.961 [0.95, 0.97] | 2017 / 2118 |
| email | rules+gliner-recipe-r10-s10k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r10-s10k | 0.996 [0.99, 1.00] | 0.994 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 4317 / 4344 |
| any | rules+gliner-recipe-r10-s10k | 0.998 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8786 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.846 [0.83, 0.86] | 0.821 [0.80, 0.84] | 0.833 [0.82, 0.85] | 0.826 [0.81, 0.84] | 1738 / 2118 |
| email | rules+gliner-recipe-r10-s10k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r10-s10k | 0.978 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.976 [0.97, 0.98] | 4237 / 4344 |
| any | rules+gliner-recipe-r10-s10k | 0.943 [0.94, 0.95] | 0.934 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.936 [0.93, 0.94] | 8338 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s10k | 0.093 [0.08, 0.11] | 0.939 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1989 / 2118 |
| email | rules+gliner-recipe-r10-s10k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r10-s10k | 0.004 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4303 / 4344 |
| any | rules+gliner-recipe-r10-s10k | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.5 [1.3, 1.7] | 8653 / 8927 |
