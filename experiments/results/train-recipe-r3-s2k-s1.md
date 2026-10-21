# train-recipe-r3-s2k-s1-dev

rules+gliner-recipe-r3-s2k-s1 after training (train-recipe-r3-s2k-s1).

Stage: dev · commit 156b8b704e · 2026-10-21T00:36:16+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-recipe-r3-s2k-s1 @ 8d0f1d4022 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.889 [0.78, 1.00] | 0.818 [0.64, 1.00] | 0.852 [0.73, 0.97] | 0.831 [0.68, 0.98] | 18 / 22 |
| email | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.918 [0.88, 0.95] | 0.937 [0.92, 0.96] | 0.927 [0.90, 0.95] | 0.933 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.923 [0.89, 0.95] | 0.921 [0.89, 0.95] | 0.922 [0.89, 0.95] | 0.921 [0.89, 0.95] | 558 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.148 [0.03, 0.32] | 0.182 [0.04, 0.44] | 0.163 [0.04, 0.37] | 0.174 [0.04, 0.41] | 4 / 22 |
| email | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.881 [0.85, 0.91] | 0.901 [0.88, 0.92] | 0.891 [0.86, 0.91] | 0.897 [0.87, 0.92] | 472 / 524 |
| phone | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.857 [0.82, 0.89] | 0.858 [0.82, 0.89] | 0.857 [0.82, 0.89] | 0.858 [0.82, 0.89] | 520 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.469 [0.30, 0.58] | 0.227 [0.07, 0.47] | 0.7 [0.2, 1.4] | 5 / 22 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.046 [0.03, 0.06] | 0.914 [0.89, 0.93] | 3.4 [2.1, 4.9] | 479 / 524 |
| phone | rules+gliner-recipe-r3-s2k-s1 | 0.328 [0.09, 0.63] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-recipe-r3-s2k-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.114 [0.07, 0.16] | 0.871 [0.83, 0.90] | 4.1 [2.6, 5.7] | 528 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k-s1 | 0.845 [0.75, 0.93] | 0.913 [0.87, 0.95] | 0.878 [0.82, 0.93] | 0.899 [0.86, 0.94] | 252 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k-s1 | 0.815 [0.72, 0.90] | 0.877 [0.83, 0.92] | 0.845 [0.79, 0.90] | 0.864 [0.82, 0.91] | 242 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-recipe-r3-s2k-s1 | 0.070 [0.04, 0.10] | 0.895 [0.84, 0.94] | 5.7 [2.6, 9.6] | 247 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.549 [0.41, 0.70] | 1.000 [1.00, 1.00] | 0.709 [0.58, 0.82] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.816 [0.64, 0.96] | 0.991 [0.98, 1.00] | 0.895 [0.78, 0.98] | 0.950 [0.89, 0.99] | 217 / 219 |
| phone | rules+gliner-recipe-r3-s2k-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.817 [0.70, 0.91] | 0.905 [0.86, 0.94] | 0.858 [0.78, 0.91] | 0.886 [0.84, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.451 [0.29, 0.62] | 0.852 [0.67, 1.00] | 0.590 [0.41, 0.75] | 0.723 [0.54, 0.87] | 23 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.598 [0.45, 0.76] | 0.699 [0.58, 0.82] | 0.644 [0.52, 0.78] | 0.676 [0.55, 0.80] | 153 / 219 |
| phone | rules+gliner-recipe-r3-s2k-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.671 [0.57, 0.77] | 0.727 [0.65, 0.80] | 0.698 [0.62, 0.77] | 0.715 [0.64, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.1 [3.0, 10.0] | 27 / 27 |
| birth_number | rules+gliner-recipe-r3-s2k-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-recipe-r3-s2k-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-recipe-r3-s2k-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.010 [0.00, 0.02] | 0.977 [0.95, 1.00] | 11.1 [5.8, 18.0] | 214 / 219 |
| phone | rules+gliner-recipe-r3-s2k-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.063 [0.03, 0.10] | 0.910 [0.86, 0.95] | 18.9 [12.6, 26.7] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.996 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.975 [0.97, 0.98] | 0.963 [0.96, 0.97] | 2023 / 2119 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.996 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4303 / 4353 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.997 [1.00, 1.00] | 0.982 [0.98, 0.98] | 0.990 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8936 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.846 [0.83, 0.86] | 0.827 [0.81, 0.84] | 0.836 [0.82, 0.85] | 0.831 [0.81, 0.85] | 1752 / 2119 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.984 [0.98, 0.99] | 0.976 [0.97, 0.98] | 0.980 [0.98, 0.98] | 0.978 [0.97, 0.98] | 4250 / 4353 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.944 [0.94, 0.95] | 0.934 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.936 [0.93, 0.94] | 8498 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.085 [0.07, 0.10] | 0.932 [0.92, 0.94] | 1.0 [0.8, 1.2] | 1974 / 2119 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.009 [0.01, 0.01] | 0.986 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4294 / 4353 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.038 [0.03, 0.04] | 0.963 [0.96, 0.97] | 1.3 [1.1, 1.5] | 8763 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.993 [0.99, 1.00] | 0.957 [0.95, 0.97] | 0.975 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2027 / 2118 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.996 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4299 / 4344 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.996 [0.99, 1.00] | 0.983 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8779 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.833 [0.82, 0.85] | 0.820 [0.80, 0.84] | 0.827 [0.81, 0.84] | 0.822 [0.81, 0.84] | 1736 / 2118 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.978 [0.97, 0.98] | 0.971 [0.97, 0.98] | 0.974 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4217 / 4344 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.940 [0.93, 0.95] | 0.932 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8316 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-recipe-r3-s2k-s1 | 0.093 [0.08, 0.11] | 0.936 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1983 / 2118 |
| email | rules+gliner-recipe-r3-s2k-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-recipe-r3-s2k-s1 | 0.008 [0.01, 0.01] | 0.986 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4282 / 4344 |
| any | rules+gliner-recipe-r3-s2k-s1 | 0.039 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8626 / 8927 |
