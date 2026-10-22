# train-cs-sk-focal-r3-s1-dev

rules+gliner-cs-sk-focal-r3-s1 after training (train-cs-sk-focal-r3-s1).

Stage: dev · commit 0b2364ff37 · 2026-10-21T21:27:41+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-r3-s1 @ 7321fd6a63 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.811 [0.71, 0.91] | 1.000 [1.00, 1.00] | 0.895 [0.83, 0.95] | 0.955 [0.92, 0.98] | 22 / 22 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.884 [0.84, 0.92] | 0.956 [0.94, 0.97] | 0.918 [0.89, 0.94] | 0.941 [0.92, 0.96] | 501 / 524 |
| phone | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.887 [0.85, 0.92] | 0.944 [0.92, 0.97] | 0.915 [0.89, 0.94] | 0.932 [0.91, 0.95] | 572 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.108 [0.02, 0.24] | 0.182 [0.04, 0.44] | 0.136 [0.03, 0.31] | 0.160 [0.03, 0.37] | 4 / 22 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.849 [0.81, 0.89] | 0.920 [0.90, 0.94] | 0.883 [0.85, 0.91] | 0.905 [0.88, 0.93] | 482 / 524 |
| phone | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.817 [0.77, 0.85] | 0.875 [0.84, 0.91] | 0.845 [0.81, 0.88] | 0.862 [0.83, 0.89] | 530 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.357 [0.24, 0.44] | 0.227 [0.07, 0.47] | 1.6 [0.7, 2.8] | 5 / 22 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.031 [0.02, 0.04] | 0.935 [0.92, 0.95] | 5.2 [3.7, 7.0] | 490 / 524 |
| phone | rules+gliner-cs-sk-focal-r3-s1 | 0.318 [0.08, 0.62] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.090 [0.06, 0.12] | 0.889 [0.85, 0.92] | 6.7 [4.6, 9.2] | 539 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.819 [0.73, 0.90] | 0.957 [0.92, 0.98] | 0.882 [0.82, 0.93] | 0.925 [0.89, 0.95] | 264 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.787 [0.70, 0.86] | 0.913 [0.87, 0.95] | 0.846 [0.78, 0.90] | 0.885 [0.84, 0.92] | 252 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.035 [0.02, 0.06] | 0.938 [0.90, 0.97] | 7.5 [4.2, 11.8] | 259 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.518 [0.38, 0.67] | 1.000 [1.00, 1.00] | 0.683 [0.55, 0.80] | 0.843 [0.75, 0.91] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.789 [0.63, 0.93] | 0.995 [0.98, 1.00] | 0.881 [0.77, 0.96] | 0.946 [0.89, 0.98] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal-r3-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.799 [0.69, 0.89] | 0.907 [0.86, 0.95] | 0.850 [0.78, 0.90] | 0.883 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.426 [0.27, 0.60] | 0.852 [0.67, 1.00] | 0.568 [0.39, 0.73] | 0.710 [0.53, 0.86] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.575 [0.43, 0.73] | 0.699 [0.58, 0.82] | 0.631 [0.50, 0.77] | 0.670 [0.55, 0.79] | 153 / 219 |
| phone | rules+gliner-cs-sk-focal-r3-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.651 [0.55, 0.75] | 0.727 [0.65, 0.80] | 0.687 [0.61, 0.76] | 0.710 [0.64, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 7.0 [3.3, 12.1] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-r3-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 11.5 [6.2, 18.4] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-r3-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 20.3 [13.4, 28.4] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.991 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.974 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2030 / 2119 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.991 [0.99, 0.99] | 0.991 [0.99, 0.99] | 0.991 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4312 / 4353 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.993 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8954 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.840 [0.82, 0.86] | 0.828 [0.81, 0.85] | 0.834 [0.82, 0.85] | 0.831 [0.81, 0.85] | 1755 / 2119 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.977 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.977 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4253 / 4353 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.940 [0.93, 0.94] | 0.935 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.936 [0.93, 0.94] | 8504 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.083 [0.07, 0.10] | 0.933 [0.92, 0.94] | 1.1 [0.9, 1.3] | 1978 / 2119 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.008 [0.01, 0.01] | 0.988 [0.98, 0.99] | 0.4 [0.3, 0.6] | 4302 / 4353 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.037 [0.03, 0.04] | 0.965 [0.96, 0.97] | 1.6 [1.4, 1.8] | 8775 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.987 [0.98, 0.99] | 0.964 [0.96, 0.97] | 0.975 [0.97, 0.98] | 0.968 [0.96, 0.97] | 2041 / 2118 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.993 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4303 / 4344 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.994 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.99, 0.99] | 8800 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.825 [0.81, 0.84] | 0.822 [0.80, 0.84] | 0.823 [0.81, 0.84] | 0.822 [0.81, 0.84] | 1740 / 2118 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.974 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4221 / 4344 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.936 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8326 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3-s1 | 0.091 [0.07, 0.11] | 0.941 [0.93, 0.95] | 1.3 [1.1, 1.5] | 1993 / 2118 |
| email | rules+gliner-cs-sk-focal-r3-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-r3-s1 | 0.007 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4292 / 4344 |
| any | rules+gliner-cs-sk-focal-r3-s1 | 0.038 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.7 [1.5, 2.0] | 8646 / 8927 |
