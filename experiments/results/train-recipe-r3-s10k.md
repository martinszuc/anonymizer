# train-recipe-r3-s10k-dev

rules+gliner-recipe-r3-s10k after training (train-recipe-r3-s10k).

Stage: dev · commit 94ed4acc40 · 2026-10-15T22:38:57+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r3-s10k @ 78cce29c75 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.864 [0.71, 1.00] | 0.773 [0.60, 0.93] | 0.816 [0.68, 0.92] | 0.789 [0.63, 0.92] | 17 / 22 |
| email | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r3-s10k | 0.920 [0.89, 0.95] | 0.949 [0.93, 0.97] | 0.934 [0.91, 0.95] | 0.943 [0.92, 0.96] | 497 / 524 |
| phone | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r3-s10k | 0.929 [0.90, 0.96] | 0.927 [0.90, 0.95] | 0.928 [0.91, 0.95] | 0.928 [0.90, 0.95] | 562 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.227 [0.06, 0.43] | 0.227 [0.05, 0.48] | 0.227 [0.05, 0.44] | 0.227 [0.05, 0.46] | 5 / 22 |
| email | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r3-s10k | 0.885 [0.85, 0.92] | 0.910 [0.88, 0.93] | 0.897 [0.87, 0.92] | 0.905 [0.88, 0.93] | 477 / 524 |
| phone | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r3-s10k | 0.869 [0.83, 0.90] | 0.868 [0.83, 0.90] | 0.869 [0.83, 0.90] | 0.868 [0.83, 0.90] | 526 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.491 [0.33, 0.62] | 0.227 [0.05, 0.48] | 0.8 [0.2, 1.5] | 5 / 22 |
| email | rules+gliner-recipe-r3-s10k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r3-s10k | 0.043 [0.03, 0.06] | 0.920 [0.90, 0.94] | 3.1 [1.8, 4.5] | 482 / 524 |
| phone | rules+gliner-recipe-r3-s10k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r3-s10k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r3-s10k | 0.114 [0.07, 0.15] | 0.876 [0.84, 0.91] | 3.9 [2.4, 5.5] | 531 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s10k | 0.855 [0.78, 0.93] | 0.902 [0.85, 0.95] | 0.878 [0.83, 0.93] | 0.892 [0.85, 0.93] | 249 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s10k | 0.824 [0.75, 0.90] | 0.866 [0.81, 0.92] | 0.845 [0.79, 0.90] | 0.857 [0.81, 0.91] | 239 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s10k | 0.085 [0.05, 0.12] | 0.884 [0.83, 0.94] | 5.1 [2.3, 8.3] | 244 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.551 [0.38, 0.72] | 1.000 [1.00, 1.00] | 0.711 [0.55, 0.84] | 0.860 [0.76, 0.93] | 27 / 27 |
| birth_number | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r3-s10k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s10k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r3-s10k | 0.803 [0.63, 0.96] | 0.918 [0.81, 0.99] | 0.857 [0.73, 0.96] | 0.892 [0.80, 0.97] | 201 / 219 |
| phone | rules+gliner-recipe-r3-s10k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r3-s10k | 0.810 [0.70, 0.91] | 0.863 [0.80, 0.92] | 0.836 [0.77, 0.89] | 0.852 [0.80, 0.90] | 335 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.449 [0.29, 0.62] | 0.815 [0.64, 0.96] | 0.579 [0.40, 0.74] | 0.701 [0.53, 0.84] | 22 / 27 |
| birth_number | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r3-s10k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s10k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r3-s10k | 0.636 [0.48, 0.80] | 0.694 [0.58, 0.82] | 0.664 [0.54, 0.78] | 0.682 [0.57, 0.80] | 152 / 219 |
| phone | rules+gliner-recipe-r3-s10k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r3-s10k | 0.698 [0.59, 0.80] | 0.722 [0.66, 0.79] | 0.710 [0.64, 0.78] | 0.717 [0.65, 0.78] | 280 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.0 [2.5, 10.0] | 26 / 27 |
| birth_number | rules+gliner-recipe-r3-s10k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r3-s10k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r3-s10k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r3-s10k | 0.059 [0.01, 0.14] | 0.909 [0.80, 0.98] | 9.5 [4.7, 16.1] | 199 / 219 |
| phone | rules+gliner-recipe-r3-s10k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r3-s10k | 0.087 [0.05, 0.13] | 0.869 [0.80, 0.93] | 17.2 [10.9, 25.0] | 337 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.999 [1.00, 1.00] | 0.942 [0.93, 0.95] | 0.970 [0.96, 0.97] | 0.953 [0.94, 0.96] | 1997 / 2119 |
| email | rules+gliner-recipe-r3-s10k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r3-s10k | 0.997 [1.00, 1.00] | 0.993 [0.99, 0.99] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 4321 / 4353 |
| any | rules+gliner-recipe-r3-s10k | 0.998 [1.00, 1.00] | 0.981 [0.98, 0.98] | 0.990 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8925 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.862 [0.85, 0.88] | 0.827 [0.81, 0.84] | 0.844 [0.83, 0.86] | 0.834 [0.82, 0.85] | 1752 / 2119 |
| email | rules+gliner-recipe-r3-s10k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r3-s10k | 0.986 [0.98, 0.99] | 0.981 [0.98, 0.99] | 0.983 [0.98, 0.99] | 0.982 [0.98, 0.99] | 4270 / 4353 |
| any | rules+gliner-recipe-r3-s10k | 0.949 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.943 [0.94, 0.95] | 0.939 [0.93, 0.94] | 8517 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.089 [0.07, 0.10] | 0.928 [0.92, 0.94] | 0.9 [0.8, 1.1] | 1966 / 2119 |
| email | rules+gliner-recipe-r3-s10k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r3-s10k | 0.006 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.2 [0.1, 0.3] | 4309 / 4353 |
| any | rules+gliner-recipe-r3-s10k | 0.038 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.2 [1.0, 1.4] | 8770 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 1.000 [1.00, 1.00] | 0.936 [0.93, 0.95] | 0.967 [0.96, 0.97] | 0.948 [0.94, 0.96] | 1983 / 2118 |
| email | rules+gliner-recipe-r3-s10k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r3-s10k | 0.997 [0.99, 1.00] | 0.994 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 4316 / 4344 |
| any | rules+gliner-recipe-r3-s10k | 0.998 [1.00, 1.00] | 0.980 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8751 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.849 [0.83, 0.86] | 0.812 [0.79, 0.83] | 0.830 [0.81, 0.84] | 0.819 [0.80, 0.83] | 1719 / 2118 |
| email | rules+gliner-recipe-r3-s10k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r3-s10k | 0.980 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4240 / 4344 |
| any | rules+gliner-recipe-r3-s10k | 0.946 [0.94, 0.95] | 0.932 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8322 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s10k | 0.099 [0.08, 0.12] | 0.925 [0.91, 0.94] | 1.0 [0.8, 1.2] | 1959 / 2118 |
| email | rules+gliner-recipe-r3-s10k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r3-s10k | 0.004 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4305 / 4344 |
| any | rules+gliner-recipe-r3-s10k | 0.039 [0.03, 0.05] | 0.966 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8625 / 8927 |
