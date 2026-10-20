# train-recipe-r1-s5k-dev

rules+gliner-recipe-r1-s5k after training (train-recipe-r1-s5k).

Stage: dev · commit 94ed4acc40 · 2026-10-15T20:15:38+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r1-s5k @ 9935bc12b5 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.889 [0.75, 1.00] | 0.818 [0.65, 0.96] | 0.852 [0.73, 0.95] | 0.831 [0.69, 0.95] | 18 / 22 |
| email | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r1-s5k | 0.920 [0.89, 0.95] | 0.927 [0.90, 0.95] | 0.924 [0.90, 0.94] | 0.926 [0.90, 0.95] | 486 / 524 |
| phone | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r1-s5k | 0.925 [0.90, 0.95] | 0.911 [0.88, 0.94] | 0.918 [0.89, 0.94] | 0.914 [0.88, 0.94] | 552 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.111 [0.00, 0.26] | 0.136 [0.00, 0.32] | 0.122 [0.00, 0.28] | 0.130 [0.00, 0.30] | 3 / 22 |
| email | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r1-s5k | 0.882 [0.85, 0.91] | 0.887 [0.86, 0.91] | 0.885 [0.86, 0.91] | 0.886 [0.86, 0.91] | 465 / 524 |
| phone | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r1-s5k | 0.856 [0.82, 0.89] | 0.845 [0.80, 0.88] | 0.851 [0.82, 0.88] | 0.847 [0.81, 0.88] | 512 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.502 [0.36, 0.62] | 0.182 [0.04, 0.39] | 0.8 [0.2, 1.5] | 4 / 22 |
| email | rules+gliner-recipe-r1-s5k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r1-s5k | 0.057 [0.04, 0.07] | 0.905 [0.88, 0.93] | 3.3 [2.0, 4.7] | 474 / 524 |
| phone | rules+gliner-recipe-r1-s5k | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r1-s5k | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r1-s5k | 0.125 [0.08, 0.17] | 0.861 [0.82, 0.89] | 4.1 [2.5, 5.8] | 522 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r1-s5k | 0.867 [0.78, 0.94] | 0.880 [0.82, 0.94] | 0.874 [0.82, 0.92] | 0.878 [0.83, 0.92] | 243 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r1-s5k | 0.827 [0.75, 0.91] | 0.833 [0.77, 0.89] | 0.830 [0.78, 0.88] | 0.832 [0.79, 0.88] | 230 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r1-s5k | 0.103 [0.06, 0.15] | 0.862 [0.80, 0.92] | 5.0 [2.1, 8.2] | 238 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.562 [0.40, 0.73] | 1.000 [1.00, 1.00] | 0.720 [0.57, 0.84] | 0.865 [0.77, 0.93] | 27 / 27 |
| birth_number | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r1-s5k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r1-s5k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r1-s5k | 0.786 [0.62, 0.95] | 0.931 [0.82, 1.00] | 0.853 [0.74, 0.95] | 0.898 [0.80, 0.98] | 204 / 219 |
| phone | rules+gliner-recipe-r1-s5k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r1-s5k | 0.802 [0.69, 0.90] | 0.871 [0.81, 0.93] | 0.835 [0.77, 0.89] | 0.856 [0.80, 0.90] | 338 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.458 [0.30, 0.63] | 0.815 [0.64, 0.96] | 0.587 [0.41, 0.74] | 0.705 [0.53, 0.84] | 22 / 27 |
| birth_number | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r1-s5k | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r1-s5k | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r1-s5k | 0.617 [0.47, 0.78] | 0.699 [0.57, 0.82] | 0.655 [0.53, 0.78] | 0.681 [0.57, 0.80] | 153 / 219 |
| phone | rules+gliner-recipe-r1-s5k | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r1-s5k | 0.687 [0.58, 0.79] | 0.724 [0.66, 0.79] | 0.705 [0.63, 0.78] | 0.717 [0.65, 0.78] | 281 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 5.7 [2.5, 9.5] | 26 / 27 |
| birth_number | rules+gliner-recipe-r1-s5k | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r1-s5k | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r1-s5k | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r1-s5k | 0.052 [0.00, 0.13] | 0.918 [0.80, 0.99] | 10.5 [5.6, 17.3] | 201 / 219 |
| phone | rules+gliner-recipe-r1-s5k | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-recipe-r1-s5k | 0.084 [0.05, 0.12] | 0.874 [0.81, 0.93] | 18.0 [11.8, 25.7] | 339 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.999 [1.00, 1.00] | 0.940 [0.93, 0.95] | 0.968 [0.96, 0.97] | 0.951 [0.94, 0.96] | 1992 / 2119 |
| email | rules+gliner-recipe-r1-s5k | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r1-s5k | 0.997 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.994 [0.99, 1.00] | 0.993 [0.99, 0.99] | 4318 / 4353 |
| any | rules+gliner-recipe-r1-s5k | 0.998 [1.00, 1.00] | 0.980 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8918 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.858 [0.84, 0.87] | 0.822 [0.81, 0.84] | 0.840 [0.82, 0.85] | 0.829 [0.81, 0.85] | 1742 / 2119 |
| email | rules+gliner-recipe-r1-s5k | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r1-s5k | 0.986 [0.98, 0.99] | 0.981 [0.98, 0.99] | 0.983 [0.98, 0.99] | 0.982 [0.98, 0.99] | 4268 / 4353 |
| any | rules+gliner-recipe-r1-s5k | 0.948 [0.94, 0.95] | 0.935 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8505 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.093 [0.08, 0.11] | 0.924 [0.91, 0.94] | 1.0 [0.8, 1.1] | 1959 / 2119 |
| email | rules+gliner-recipe-r1-s5k | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-recipe-r1-s5k | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.2 [0.1, 0.3] | 4308 / 4353 |
| any | rules+gliner-recipe-r1-s5k | 0.040 [0.03, 0.05] | 0.963 [0.96, 0.97] | 1.3 [1.1, 1.5] | 8762 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 1.000 [1.00, 1.00] | 0.935 [0.92, 0.95] | 0.966 [0.96, 0.97] | 0.948 [0.94, 0.96] | 1981 / 2118 |
| email | rules+gliner-recipe-r1-s5k | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r1-s5k | 0.996 [0.99, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 4314 / 4344 |
| any | rules+gliner-recipe-r1-s5k | 0.998 [1.00, 1.00] | 0.980 [0.98, 0.98] | 0.989 [0.99, 0.99] | 0.983 [0.98, 0.99] | 8747 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.847 [0.83, 0.86] | 0.807 [0.79, 0.82] | 0.827 [0.81, 0.84] | 0.815 [0.80, 0.83] | 1710 / 2118 |
| email | rules+gliner-recipe-r1-s5k | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r1-s5k | 0.980 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4239 / 4344 |
| any | rules+gliner-recipe-r1-s5k | 0.945 [0.94, 0.95] | 0.931 [0.93, 0.94] | 0.938 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8312 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r1-s5k | 0.103 [0.09, 0.12] | 0.921 [0.91, 0.93] | 1.0 [0.8, 1.2] | 1950 / 2118 |
| email | rules+gliner-recipe-r1-s5k | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r1-s5k | 0.005 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4303 / 4344 |
| any | rules+gliner-recipe-r1-s5k | 0.041 [0.03, 0.05] | 0.965 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8614 / 8927 |
