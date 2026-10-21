# train-recipe-r5-s2k-s1-dev

rules+gliner-recipe-r5-s2k-s1 after training (train-recipe-r5-s2k-s1).

Stage: dev · commit 156b8b704e · 2026-10-21T00:44:50+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r5-s2k-s1 @ 88c3519066 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.917 [0.80, 1.00] | 0.818 [0.67, 0.95] | 0.865 [0.76, 0.96] | 0.836 [0.70, 0.96] | 18 / 22 |
| email | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.906 [0.87, 0.93] | 0.941 [0.92, 0.96] | 0.923 [0.90, 0.94] | 0.934 [0.91, 0.95] | 493 / 524 |
| phone | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.913 [0.88, 0.94] | 0.924 [0.90, 0.95] | 0.919 [0.90, 0.94] | 0.922 [0.90, 0.94] | 560 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.167 [0.04, 0.35] | 0.182 [0.04, 0.44] | 0.174 [0.04, 0.39] | 0.179 [0.04, 0.42] | 4 / 22 |
| email | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.871 [0.84, 0.90] | 0.903 [0.88, 0.93] | 0.887 [0.86, 0.91] | 0.896 [0.87, 0.92] | 473 / 524 |
| phone | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.853 [0.81, 0.89] | 0.860 [0.82, 0.89] | 0.856 [0.82, 0.88] | 0.858 [0.82, 0.89] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.494 [0.32, 0.63] | 0.182 [0.04, 0.44] | 0.5 [0.1, 1.2] | 4 / 22 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.045 [0.03, 0.06] | 0.918 [0.90, 0.94] | 4.1 [2.9, 5.6] | 481 / 524 |
| phone | rules+gliner-recipe-r5-s2k-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r5-s2k-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.116 [0.07, 0.15] | 0.873 [0.83, 0.90] | 4.6 [3.3, 6.1] | 529 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s2k-s1 | 0.835 [0.75, 0.92] | 0.924 [0.88, 0.96] | 0.877 [0.82, 0.92] | 0.905 [0.86, 0.94] | 255 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s2k-s1 | 0.799 [0.72, 0.88] | 0.877 [0.82, 0.92] | 0.836 [0.78, 0.88] | 0.860 [0.81, 0.90] | 242 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r5-s2k-s1 | 0.058 [0.03, 0.09] | 0.906 [0.85, 0.95] | 6.1 [3.0, 9.6] | 250 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.549 [0.41, 0.70] | 1.000 [1.00, 1.00] | 0.709 [0.58, 0.82] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s2k-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.807 [0.63, 0.96] | 0.995 [0.98, 1.00] | 0.891 [0.77, 0.98] | 0.951 [0.89, 0.99] | 218 / 219 |
| phone | rules+gliner-recipe-r5-s2k-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.818 [0.71, 0.91] | 0.905 [0.86, 0.94] | 0.859 [0.79, 0.91] | 0.886 [0.84, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.451 [0.30, 0.60] | 0.852 [0.67, 1.00] | 0.590 [0.43, 0.73] | 0.723 [0.55, 0.86] | 23 / 27 |
| birth_number | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s2k-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.602 [0.46, 0.76] | 0.712 [0.60, 0.83] | 0.653 [0.53, 0.78] | 0.687 [0.57, 0.81] | 156 / 219 |
| phone | rules+gliner-recipe-r5-s2k-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.674 [0.57, 0.77] | 0.735 [0.67, 0.80] | 0.703 [0.63, 0.77] | 0.722 [0.65, 0.78] | 285 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.021 [0.00, 0.07] | 0.963 [0.87, 1.00] | 6.1 [3.0, 10.0] | 26 / 27 |
| birth_number | rules+gliner-recipe-r5-s2k-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r5-s2k-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-recipe-r5-s2k-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.011 [0.00, 0.03] | 0.982 [0.95, 1.00] | 11.2 [5.9, 18.1] | 215 / 219 |
| phone | rules+gliner-recipe-r5-s2k-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.067 [0.04, 0.10] | 0.910 [0.86, 0.95] | 19.0 [12.6, 26.9] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.996 [0.99, 1.00] | 0.949 [0.94, 0.96] | 0.972 [0.97, 0.98] | 0.958 [0.95, 0.97] | 2011 / 2119 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.995 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.98, 0.99] | 4291 / 4353 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.996 [0.99, 1.00] | 0.980 [0.98, 0.98] | 0.988 [0.99, 0.99] | 0.983 [0.98, 0.99] | 8911 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.846 [0.83, 0.86] | 0.821 [0.80, 0.84] | 0.833 [0.82, 0.85] | 0.826 [0.81, 0.84] | 1740 / 2119 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.982 [0.98, 0.99] | 0.972 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4232 / 4353 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.943 [0.94, 0.95] | 0.931 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8468 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.089 [0.07, 0.10] | 0.926 [0.92, 0.94] | 1.1 [0.9, 1.3] | 1963 / 2119 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.012 [0.01, 0.02] | 0.982 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4274 / 4353 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.040 [0.03, 0.05] | 0.960 [0.96, 0.96] | 1.4 [1.2, 1.6] | 8732 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.990 [0.99, 0.99] | 0.952 [0.94, 0.96] | 0.971 [0.97, 0.98] | 0.959 [0.95, 0.97] | 2016 / 2118 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.995 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 4281 / 4344 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.996 [0.99, 1.00] | 0.981 [0.98, 0.98] | 0.988 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8753 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.831 [0.81, 0.85] | 0.814 [0.80, 0.83] | 0.823 [0.81, 0.84] | 0.817 [0.80, 0.83] | 1724 / 2118 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.975 [0.97, 0.98] | 0.966 [0.96, 0.97] | 0.971 [0.97, 0.98] | 0.968 [0.96, 0.97] | 4196 / 4344 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.938 [0.93, 0.94] | 0.928 [0.92, 0.93] | 0.933 [0.93, 0.94] | 0.930 [0.92, 0.94] | 8284 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r5-s2k-s1 | 0.098 [0.08, 0.12] | 0.932 [0.92, 0.94] | 1.2 [1.0, 1.5] | 1974 / 2118 |
| email | rules+gliner-recipe-r5-s2k-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r5-s2k-s1 | 0.011 [0.01, 0.01] | 0.983 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4268 / 4344 |
| any | rules+gliner-recipe-r5-s2k-s1 | 0.042 [0.04, 0.05] | 0.964 [0.96, 0.97] | 1.7 [1.4, 1.9] | 8603 / 8927 |
