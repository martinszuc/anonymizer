# train-cs-sk-ce-gpu-s1-dev

rules+gliner-cs-sk-ce-gpu-s1 after training (train-cs-sk-ce-gpu-s1).

Stage: dev · commit 0211b3728e · 2026-10-14T20:02:50+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-ce-gpu-s1 @ 51e354cfff · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.838 [0.73, 0.94] | 0.955 [0.88, 1.00] | 0.892 [0.82, 0.96] | 0.929 [0.86, 0.99] | 21 / 22 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.911 [0.88, 0.94] | 0.937 [0.91, 0.96] | 0.924 [0.90, 0.94] | 0.932 [0.91, 0.95] | 491 / 524 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.913 [0.88, 0.94] | 0.927 [0.90, 0.95] | 0.920 [0.89, 0.94] | 0.924 [0.90, 0.95] | 562 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.108 [0.02, 0.24] | 0.182 [0.04, 0.42] | 0.136 [0.03, 0.30] | 0.160 [0.04, 0.36] | 4 / 22 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.866 [0.83, 0.90] | 0.889 [0.86, 0.91] | 0.878 [0.85, 0.90] | 0.885 [0.86, 0.91] | 466 / 524 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.830 [0.79, 0.86] | 0.848 [0.81, 0.88] | 0.839 [0.80, 0.87] | 0.845 [0.81, 0.88] | 514 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.403 [0.26, 0.50] | 0.273 [0.10, 0.55] | 1.3 [0.5, 2.3] | 6 / 22 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.047 [0.03, 0.06] | 0.916 [0.89, 0.94] | 4.0 [2.7, 5.5] | 480 / 524 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 0.318 [0.08, 0.62] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-ce-gpu-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.106 [0.07, 0.14] | 0.875 [0.83, 0.91] | 5.1 [3.3, 7.2] | 530 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.841 [0.75, 0.92] | 0.927 [0.89, 0.96] | 0.882 [0.82, 0.93] | 0.909 [0.87, 0.94] | 256 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.811 [0.72, 0.89] | 0.888 [0.84, 0.93] | 0.848 [0.79, 0.90] | 0.871 [0.83, 0.91] | 245 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.062 [0.04, 0.09] | 0.909 [0.86, 0.95] | 5.8 [2.6, 9.8] | 251 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.549 [0.41, 0.70] | 1.000 [1.00, 1.00] | 0.709 [0.58, 0.82] | 0.859 [0.77, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-gpu-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.817 [0.64, 0.96] | 0.995 [0.98, 1.00] | 0.897 [0.78, 0.98] | 0.954 [0.90, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.817 [0.71, 0.91] | 0.907 [0.86, 0.95] | 0.860 [0.79, 0.91] | 0.888 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.431 [0.29, 0.59] | 0.815 [0.62, 0.96] | 0.564 [0.40, 0.71] | 0.692 [0.51, 0.84] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-gpu-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.595 [0.44, 0.76] | 0.699 [0.58, 0.82] | 0.643 [0.51, 0.78] | 0.675 [0.55, 0.80] | 153 / 219 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.667 [0.56, 0.77] | 0.724 [0.65, 0.79] | 0.695 [0.62, 0.77] | 0.712 [0.64, 0.78] | 281 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.021 [0.00, 0.07] | 0.963 [0.87, 1.00] | 6.1 [3.0, 10.0] | 26 / 27 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-ce-gpu-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 11.1 [5.8, 18.0] | 215 / 219 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.065 [0.03, 0.10] | 0.910 [0.86, 0.95] | 19.0 [12.6, 26.9] | 353 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.996 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.975 [0.97, 0.98] | 0.963 [0.96, 0.97] | 2023 / 2119 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.995 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.994 [0.99, 1.00] | 0.993 [0.99, 0.99] | 4318 / 4353 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.997 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8953 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.850 [0.83, 0.87] | 0.831 [0.81, 0.85] | 0.840 [0.82, 0.86] | 0.834 [0.82, 0.85] | 1760 / 2119 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.983 [0.98, 0.99] | 0.980 [0.97, 0.98] | 0.982 [0.98, 0.99] | 0.980 [0.98, 0.98] | 4264 / 4353 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.945 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8520 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.086 [0.07, 0.10] | 0.934 [0.92, 0.95] | 1.0 [0.9, 1.2] | 1980 / 2119 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4311 / 4353 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8786 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.995 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.975 [0.97, 0.98] | 0.963 [0.96, 0.97] | 2023 / 2118 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.995 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4306 / 4344 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.996 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8784 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.840 [0.82, 0.86] | 0.822 [0.80, 0.84] | 0.831 [0.81, 0.85] | 0.825 [0.81, 0.84] | 1740 / 2118 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.976 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4225 / 4344 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.941 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8329 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.094 [0.07, 0.11] | 0.938 [0.93, 0.95] | 1.1 [1.0, 1.4] | 1987 / 2118 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.5] | 4293 / 4344 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8641 / 8927 |
