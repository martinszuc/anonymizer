# train-cs-sk-ce-more-dev

rules+gliner-cs-sk-ce-more after training (train-cs-sk-ce-more).

Stage: dev · commit 0b2364ff37 · 2026-10-21T22:16:04+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-ce-more @ 80091cb60a · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.862 [0.75, 0.96] | 0.864 [0.72, 1.00] | 0.863 [0.74, 0.97] | 0.863 [0.73, 0.99] | 19 / 22 |
| email | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more | 0.889 [0.85, 0.92] | 0.943 [0.92, 0.96] | 0.915 [0.89, 0.94] | 0.931 [0.91, 0.95] | 494 / 524 |
| phone | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more | 0.895 [0.86, 0.93] | 0.924 [0.89, 0.95] | 0.909 [0.88, 0.93] | 0.918 [0.89, 0.94] | 560 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.138 [0.03, 0.29] | 0.182 [0.04, 0.39] | 0.157 [0.03, 0.33] | 0.171 [0.04, 0.36] | 4 / 22 |
| email | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more | 0.851 [0.81, 0.89] | 0.905 [0.88, 0.93] | 0.877 [0.85, 0.90] | 0.893 [0.87, 0.91] | 474 / 524 |
| phone | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more | 0.829 [0.79, 0.86] | 0.861 [0.82, 0.90] | 0.845 [0.81, 0.87] | 0.855 [0.82, 0.89] | 522 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.484 [0.34, 0.62] | 0.227 [0.06, 0.46] | 1.0 [0.3, 1.7] | 5 / 22 |
| email | rules+gliner-cs-sk-ce-more | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-more | 0.046 [0.03, 0.06] | 0.918 [0.90, 0.94] | 4.9 [3.3, 6.3] | 481 / 524 |
| phone | rules+gliner-cs-sk-ce-more | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-more | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-more | 0.112 [0.07, 0.15] | 0.875 [0.83, 0.91] | 5.7 [3.9, 7.4] | 530 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.848 [0.76, 0.93] | 0.960 [0.93, 0.99] | 0.900 [0.85, 0.95] | 0.935 [0.90, 0.96] | 265 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.806 [0.72, 0.88] | 0.902 [0.86, 0.94] | 0.851 [0.80, 0.90] | 0.881 [0.85, 0.91] | 249 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.033 [0.01, 0.06] | 0.942 [0.90, 0.98] | 5.8 [2.6, 9.5] | 260 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more | 0.800 [0.63, 0.96] | 0.936 [0.82, 1.00] | 0.863 [0.74, 0.97] | 0.905 [0.81, 0.98] | 205 / 219 |
| phone | rules+gliner-cs-sk-ce-more | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more | 0.807 [0.70, 0.90] | 0.874 [0.81, 0.93] | 0.839 [0.77, 0.90] | 0.860 [0.81, 0.91] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.431 [0.29, 0.59] | 0.815 [0.64, 0.96] | 0.564 [0.41, 0.71] | 0.692 [0.52, 0.83] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more | 0.645 [0.49, 0.80] | 0.722 [0.62, 0.83] | 0.681 [0.57, 0.79] | 0.705 [0.61, 0.81] | 158 / 219 |
| phone | rules+gliner-cs-sk-ce-more | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more | 0.699 [0.60, 0.80] | 0.737 [0.68, 0.80] | 0.718 [0.65, 0.78] | 0.729 [0.68, 0.79] | 286 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.1 [3.0, 10.0] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-ce-more | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-ce-more | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-more | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-more | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-more | 0.050 [0.00, 0.13] | 0.922 [0.80, 1.00] | 9.6 [4.8, 16.1] | 202 / 219 |
| phone | rules+gliner-cs-sk-ce-more | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-more | 0.083 [0.05, 0.12] | 0.876 [0.81, 0.94] | 17.4 [11.3, 25.0] | 340 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.996 [0.99, 1.00] | 0.952 [0.94, 0.96] | 0.974 [0.97, 0.98] | 0.960 [0.95, 0.97] | 2017 / 2119 |
| email | rules+gliner-cs-sk-ce-more | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-ce-more | 0.994 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 4288 / 4353 |
| any | rules+gliner-cs-sk-ce-more | 0.996 [0.99, 1.00] | 0.980 [0.98, 0.98] | 0.988 [0.99, 0.99] | 0.983 [0.98, 0.99] | 8916 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.846 [0.83, 0.86] | 0.824 [0.81, 0.84] | 0.835 [0.82, 0.85] | 0.828 [0.81, 0.84] | 1745 / 2119 |
| email | rules+gliner-cs-sk-ce-more | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-more | 0.982 [0.98, 0.99] | 0.973 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.975 [0.97, 0.98] | 4236 / 4353 |
| any | rules+gliner-cs-sk-ce-more | 0.943 [0.94, 0.95] | 0.932 [0.93, 0.94] | 0.938 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8478 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.087 [0.07, 0.10] | 0.929 [0.92, 0.94] | 1.0 [0.8, 1.2] | 1969 / 2119 |
| email | rules+gliner-cs-sk-ce-more | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-more | 0.011 [0.01, 0.01] | 0.983 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4279 / 4353 |
| any | rules+gliner-cs-sk-ce-more | 0.039 [0.03, 0.05] | 0.961 [0.96, 0.97] | 1.4 [1.1, 1.6] | 8743 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.991 [0.99, 0.99] | 0.950 [0.94, 0.96] | 0.970 [0.96, 0.98] | 0.958 [0.95, 0.97] | 2012 / 2118 |
| email | rules+gliner-cs-sk-ce-more | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-ce-more | 0.994 [0.99, 1.00] | 0.987 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.98, 0.99] | 4286 / 4344 |
| any | rules+gliner-cs-sk-ce-more | 0.996 [0.99, 1.00] | 0.981 [0.98, 0.98] | 0.988 [0.99, 0.99] | 0.984 [0.98, 0.99] | 8754 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.830 [0.81, 0.84] | 0.811 [0.79, 0.83] | 0.820 [0.80, 0.83] | 0.814 [0.80, 0.83] | 1717 / 2118 |
| email | rules+gliner-cs-sk-ce-more | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-ce-more | 0.976 [0.97, 0.98] | 0.968 [0.96, 0.97] | 0.972 [0.97, 0.98] | 0.970 [0.96, 0.97] | 4206 / 4344 |
| any | rules+gliner-cs-sk-ce-more | 0.939 [0.93, 0.94] | 0.928 [0.92, 0.93] | 0.933 [0.93, 0.94] | 0.930 [0.92, 0.94] | 8288 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-more | 0.097 [0.08, 0.12] | 0.931 [0.92, 0.94] | 1.4 [1.2, 1.6] | 1972 / 2118 |
| email | rules+gliner-cs-sk-ce-more | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-ce-more | 0.009 [0.01, 0.01] | 0.983 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4272 / 4344 |
| any | rules+gliner-cs-sk-ce-more | 0.041 [0.03, 0.05] | 0.964 [0.96, 0.97] | 1.8 [1.5, 2.1] | 8605 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.937 [0.90, 0.97] | 0.953 [0.93, 0.98] | 0.945 [0.92, 0.97] | 0.950 [0.92, 0.97] | 284 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.848 [0.79, 0.90] | 0.859 [0.81, 0.91] | 0.853 [0.80, 0.90] | 0.857 [0.81, 0.90] | 256 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.046 [0.03, 0.07] | 0.883 [0.83, 0.93] | 3.5 [2.0, 5.5] | 263 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.990 [0.98, 1.00] | 0.952 [0.92, 0.98] | 0.970 [0.95, 0.98] | 0.959 [0.93, 0.98] | 377 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.990 [0.98, 1.00] | 0.952 [0.92, 0.98] | 0.970 [0.95, 0.98] | 0.959 [0.93, 0.98] | 377 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-more | 0.052 [0.02, 0.09] | 0.952 [0.92, 0.98] | 0.3 [0.0, 0.7] | 377 / 396 |
