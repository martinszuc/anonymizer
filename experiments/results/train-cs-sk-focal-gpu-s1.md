# train-cs-sk-focal-gpu-s1-dev

rules+gliner-cs-sk-focal-gpu-s1 after training (train-cs-sk-focal-gpu-s1).

Stage: dev · commit 0211b3728e · 2026-10-14T20:28:00+00:00 · seed 1, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-gpu-s1 @ 6f0bfadb5c · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.780 [0.66, 0.90] | 0.955 [0.88, 1.00] | 0.859 [0.77, 0.94] | 0.914 [0.85, 0.98] | 21 / 22 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.865 [0.82, 0.90] | 0.945 [0.92, 0.96] | 0.903 [0.88, 0.93] | 0.928 [0.91, 0.95] | 495 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.869 [0.83, 0.90] | 0.936 [0.90, 0.96] | 0.901 [0.87, 0.93] | 0.921 [0.89, 0.95] | 567 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.098 [0.02, 0.21] | 0.182 [0.04, 0.42] | 0.127 [0.03, 0.27] | 0.155 [0.03, 0.34] | 4 / 22 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.825 [0.78, 0.86] | 0.899 [0.87, 0.92] | 0.860 [0.83, 0.89] | 0.883 [0.86, 0.91] | 471 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.622 [0.28, 0.89] | 0.767 [0.44, 0.94] | 0.672 [0.33, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.793 [0.75, 0.83] | 0.858 [0.82, 0.89] | 0.824 [0.79, 0.86] | 0.844 [0.81, 0.88] | 520 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.381 [0.25, 0.47] | 0.273 [0.10, 0.55] | 1.8 [0.7, 3.2] | 6 / 22 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.038 [0.02, 0.05] | 0.926 [0.90, 0.95] | 6.1 [4.5, 8.1] | 485 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 0.318 [0.08, 0.62] | 0.622 [0.28, 0.89] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.097 [0.07, 0.13] | 0.883 [0.84, 0.92] | 7.8 [5.6, 10.5] | 535 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.811 [0.72, 0.88] | 0.957 [0.92, 0.98] | 0.878 [0.82, 0.92] | 0.923 [0.89, 0.95] | 264 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.783 [0.70, 0.85] | 0.917 [0.88, 0.95] | 0.845 [0.79, 0.89] | 0.886 [0.84, 0.92] | 253 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.037 [0.02, 0.06] | 0.938 [0.90, 0.97] | 7.9 [4.5, 12.2] | 259 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.528 [0.38, 0.68] | 1.000 [1.00, 1.00] | 0.691 [0.55, 0.81] | 0.849 [0.76, 0.91] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.810 [0.64, 0.95] | 0.991 [0.97, 1.00] | 0.891 [0.78, 0.97] | 0.949 [0.89, 0.99] | 217 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.809 [0.70, 0.90] | 0.905 [0.86, 0.94] | 0.854 [0.78, 0.91] | 0.884 [0.83, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.434 [0.28, 0.61] | 0.852 [0.67, 1.00] | 0.575 [0.40, 0.74] | 0.714 [0.53, 0.86] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.43, 0.90] | 0.606 [0.32, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.953 [0.85, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.97, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.601 [0.45, 0.76] | 0.708 [0.59, 0.82] | 0.650 [0.52, 0.79] | 0.683 [0.57, 0.80] | 155 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 0.812 [0.67, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.77, 0.98] | 0.929 [0.85, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.670 [0.57, 0.77] | 0.732 [0.67, 0.80] | 0.700 [0.63, 0.77] | 0.719 [0.65, 0.78] | 284 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.8 [3.1, 11.4] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s1 | 0.572 [0.34, 0.80] | 0.450 [0.22, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-gpu-s1 | 0.462 [0.19, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.2] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.009 [0.00, 0.02] | 0.982 [0.95, 1.00] | 11.1 [5.8, 18.0] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.063 [0.03, 0.10] | 0.912 [0.86, 0.95] | 19.6 [12.9, 28.1] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.993 [0.99, 1.00] | 0.959 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2031 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4318 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.994 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8961 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.847 [0.83, 0.86] | 0.833 [0.82, 0.85] | 0.840 [0.82, 0.86] | 0.836 [0.82, 0.85] | 1765 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.95, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.980 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.980 [0.98, 0.98] | 0.980 [0.97, 0.98] | 4264 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.942 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.940 [0.93, 0.94] | 0.938 [0.93, 0.94] | 8525 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.083 [0.07, 0.10] | 0.937 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1986 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.1] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.006 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.4 [0.3, 0.5] | 4312 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.036 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8793 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.989 [0.98, 0.99] | 0.961 [0.95, 0.97] | 0.975 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2036 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.994 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4305 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.99, 0.99] | 8797 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.833 [0.82, 0.85] | 0.825 [0.81, 0.84] | 0.829 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1747 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.976 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.974 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4223 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.939 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8335 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.091 [0.07, 0.11] | 0.944 [0.93, 0.95] | 1.2 [1.0, 1.5] | 2000 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4293 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.7 [1.4, 2.0] | 8654 / 8927 |
