# train-cs-sk-focal-gpu-s2-dev

rules+gliner-cs-sk-focal-gpu-s2 after training (train-cs-sk-focal-gpu-s2).

Stage: dev · commit 0211b3728e · 2026-10-14T20:28:05+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-gpu-s2 @ 969b50c212 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.789 [0.66, 0.91] | 0.909 [0.79, 1.00] | 0.845 [0.74, 0.93] | 0.882 [0.78, 0.96] | 20 / 22 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.885 [0.85, 0.92] | 0.950 [0.93, 0.97] | 0.916 [0.89, 0.94] | 0.936 [0.92, 0.95] | 498 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.887 [0.85, 0.92] | 0.937 [0.91, 0.96] | 0.911 [0.88, 0.93] | 0.927 [0.90, 0.95] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.079 [0.00, 0.19] | 0.136 [0.00, 0.33] | 0.100 [0.00, 0.24] | 0.119 [0.00, 0.29] | 3 / 22 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.849 [0.81, 0.88] | 0.914 [0.89, 0.94] | 0.880 [0.85, 0.90] | 0.900 [0.88, 0.92] | 479 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.814 [0.77, 0.85] | 0.868 [0.83, 0.90] | 0.840 [0.80, 0.87] | 0.857 [0.82, 0.89] | 526 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.420 [0.30, 0.52] | 0.227 [0.07, 0.44] | 1.5 [0.5, 2.7] | 5 / 22 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.036 [0.02, 0.05] | 0.927 [0.91, 0.95] | 5.2 [3.8, 6.8] | 486 / 524 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 0.318 [0.09, 0.61] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-gpu-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.101 [0.07, 0.14] | 0.883 [0.84, 0.92] | 6.6 [4.6, 8.8] | 535 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.832 [0.74, 0.90] | 0.938 [0.90, 0.97] | 0.882 [0.82, 0.93] | 0.915 [0.87, 0.95] | 259 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.796 [0.71, 0.87] | 0.891 [0.84, 0.94] | 0.841 [0.78, 0.89] | 0.871 [0.82, 0.91] | 246 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.052 [0.02, 0.08] | 0.920 [0.87, 0.96] | 6.5 [3.5, 10.4] | 254 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.509 [0.37, 0.66] | 1.000 [1.00, 1.00] | 0.675 [0.54, 0.79] | 0.838 [0.75, 0.91] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.764 [0.60, 0.93] | 0.995 [0.99, 1.00] | 0.864 [0.75, 0.96] | 0.939 [0.88, 0.98] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.783 [0.68, 0.88] | 0.907 [0.86, 0.94] | 0.841 [0.78, 0.90] | 0.879 [0.84, 0.91] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.418 [0.28, 0.58] | 0.852 [0.69, 1.00] | 0.561 [0.40, 0.73] | 0.706 [0.55, 0.85] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.556 [0.40, 0.74] | 0.699 [0.57, 0.82] | 0.619 [0.48, 0.77] | 0.665 [0.54, 0.79] | 153 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.637 [0.53, 0.76] | 0.727 [0.66, 0.80] | 0.679 [0.60, 0.77] | 0.707 [0.64, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 7.1 [3.3, 11.9] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-gpu-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 13.9 [6.5, 23.8] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 22.8 [14.6, 32.3] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.992 [0.99, 1.00] | 0.961 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2036 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4316 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8962 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.843 [0.83, 0.86] | 0.832 [0.81, 0.85] | 0.837 [0.82, 0.85] | 0.834 [0.82, 0.85] | 1762 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.982 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.981 [0.98, 0.98] | 0.980 [0.97, 0.98] | 4263 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.942 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.938 [0.93, 0.94] | 8520 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.080 [0.06, 0.10] | 0.938 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1988 / 2119 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.5] | 4310 / 4353 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.035 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.6 [1.3, 1.9] | 8793 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.985 [0.98, 0.99] | 0.963 [0.95, 0.97] | 0.974 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2040 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.994 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4307 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.994 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8802 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.830 [0.81, 0.85] | 0.827 [0.81, 0.84] | 0.829 [0.81, 0.84] | 0.828 [0.81, 0.84] | 1752 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.974 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4222 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.937 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8339 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.089 [0.07, 0.11] | 0.945 [0.93, 0.95] | 1.3 [1.1, 1.5] | 2002 / 2118 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4293 / 4344 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.037 [0.03, 0.04] | 0.970 [0.97, 0.97] | 1.7 [1.5, 2.0] | 8656 / 8927 |
