# train-recipe-r10-s2k-s1-dev

rules+gliner-recipe-r10-s2k-s1 after training (train-recipe-r10-s2k-s1).

Stage: dev · commit 156b8b704e · 2026-10-21T01:00:08+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r10-s2k-s1 @ 4e3db1ea66 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.815 [0.71, 0.94] | 0.818 [0.67, 0.95] | 0.817 [0.71, 0.92] | 0.818 [0.69, 0.93] | 18 / 22 |
| email | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.923 [0.89, 0.95] | 0.937 [0.92, 0.96] | 0.930 [0.91, 0.95] | 0.934 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.924 [0.89, 0.95] | 0.919 [0.89, 0.95] | 0.921 [0.90, 0.94] | 0.920 [0.89, 0.94] | 557 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.185 [0.06, 0.38] | 0.227 [0.07, 0.50] | 0.204 [0.06, 0.41] | 0.217 [0.07, 0.45] | 5 / 22 |
| email | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.887 [0.85, 0.92] | 0.901 [0.88, 0.92] | 0.894 [0.87, 0.92] | 0.898 [0.87, 0.92] | 472 / 524 |
| phone | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.864 [0.82, 0.90] | 0.860 [0.82, 0.89] | 0.862 [0.82, 0.89] | 0.861 [0.82, 0.89] | 521 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.488 [0.32, 0.63] | 0.273 [0.10, 0.55] | 1.1 [0.4, 2.1] | 6 / 22 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.047 [0.03, 0.06] | 0.914 [0.89, 0.94] | 3.3 [2.1, 4.8] | 479 / 524 |
| phone | rules+gliner-recipe-r10-s2k-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r10-s2k-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.116 [0.07, 0.15] | 0.873 [0.83, 0.91] | 4.4 [2.7, 6.6] | 529 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k-s1 | 0.841 [0.75, 0.92] | 0.920 [0.87, 0.96] | 0.879 [0.82, 0.92] | 0.903 [0.86, 0.94] | 254 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k-s1 | 0.811 [0.72, 0.89] | 0.884 [0.83, 0.93] | 0.846 [0.79, 0.90] | 0.868 [0.82, 0.91] | 244 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r10-s2k-s1 | 0.060 [0.03, 0.09] | 0.902 [0.85, 0.95] | 5.9 [2.8, 9.8] | 249 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.529 [0.39, 0.68] | 1.000 [1.00, 1.00] | 0.692 [0.56, 0.81] | 0.849 [0.76, 0.91] | 27 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.803 [0.63, 0.95] | 0.936 [0.82, 1.00] | 0.865 [0.74, 0.96] | 0.906 [0.80, 0.98] | 205 / 219 |
| phone | rules+gliner-recipe-r10-s2k-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.809 [0.70, 0.90] | 0.874 [0.81, 0.93] | 0.840 [0.77, 0.89] | 0.860 [0.80, 0.91] | 339 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.431 [0.29, 0.59] | 0.815 [0.62, 0.96] | 0.564 [0.40, 0.71] | 0.692 [0.51, 0.84] | 22 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.635 [0.47, 0.80] | 0.708 [0.59, 0.83] | 0.669 [0.55, 0.79] | 0.692 [0.58, 0.81] | 155 / 219 |
| phone | rules+gliner-recipe-r10-s2k-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.694 [0.59, 0.79] | 0.729 [0.66, 0.80] | 0.711 [0.64, 0.78] | 0.722 [0.66, 0.78] | 283 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.021 [0.00, 0.07] | 0.963 [0.87, 1.00] | 5.9 [2.8, 9.8] | 26 / 27 |
| birth_number | rules+gliner-recipe-r10-s2k-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r10-s2k-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-recipe-r10-s2k-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.048 [0.00, 0.13] | 0.927 [0.81, 1.00] | 9.9 [5.0, 17.1] | 203 / 219 |
| phone | rules+gliner-recipe-r10-s2k-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.082 [0.05, 0.12] | 0.879 [0.81, 0.94] | 17.6 [11.3, 25.7] | 341 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.995 [0.99, 1.00] | 0.948 [0.94, 0.96] | 0.971 [0.97, 0.98] | 0.957 [0.95, 0.96] | 2009 / 2119 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.995 [0.99, 1.00] | 0.982 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.985 [0.98, 0.99] | 4276 / 4353 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.996 [0.99, 1.00] | 0.978 [0.97, 0.98] | 0.987 [0.99, 0.99] | 0.982 [0.98, 0.98] | 8896 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.840 [0.82, 0.86] | 0.816 [0.80, 0.83] | 0.828 [0.81, 0.84] | 0.821 [0.80, 0.84] | 1730 / 2119 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.982 [0.98, 0.99] | 0.969 [0.96, 0.98] | 0.976 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4219 / 4353 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.942 [0.94, 0.95] | 0.928 [0.92, 0.93] | 0.935 [0.93, 0.94] | 0.931 [0.93, 0.94] | 8445 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.092 [0.08, 0.11] | 0.921 [0.91, 0.93] | 1.1 [0.9, 1.3] | 1952 / 2119 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.013 [0.01, 0.02] | 0.980 [0.97, 0.98] | 0.3 [0.2, 0.4] | 4265 / 4353 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.042 [0.04, 0.05] | 0.958 [0.95, 0.96] | 1.5 [1.2, 1.7] | 8712 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.985 [0.98, 0.99] | 0.949 [0.94, 0.96] | 0.967 [0.96, 0.97] | 0.956 [0.95, 0.96] | 2009 / 2118 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.994 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.986 [0.98, 0.99] | 4276 / 4344 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.995 [0.99, 1.00] | 0.979 [0.98, 0.98] | 0.987 [0.99, 0.99] | 0.982 [0.98, 0.98] | 8743 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.821 [0.80, 0.84] | 0.806 [0.79, 0.82] | 0.814 [0.80, 0.83] | 0.809 [0.79, 0.83] | 1708 / 2118 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.975 [0.97, 0.98] | 0.965 [0.96, 0.97] | 0.970 [0.96, 0.98] | 0.967 [0.96, 0.97] | 4192 / 4344 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.936 [0.93, 0.94] | 0.926 [0.92, 0.93] | 0.931 [0.93, 0.94] | 0.928 [0.92, 0.93] | 8265 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r10-s2k-s1 | 0.104 [0.08, 0.12] | 0.927 [0.91, 0.94] | 1.3 [1.1, 1.5] | 1963 / 2118 |
| email | rules+gliner-recipe-r10-s2k-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r10-s2k-s1 | 0.011 [0.01, 0.01] | 0.982 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4266 / 4344 |
| any | rules+gliner-recipe-r10-s2k-s1 | 0.043 [0.04, 0.05] | 0.962 [0.96, 0.97] | 1.7 [1.5, 2.0] | 8590 / 8927 |
