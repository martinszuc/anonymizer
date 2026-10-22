# train-cs-sk-focal-r3-dev

rules+gliner-cs-sk-focal-r3 after training (train-cs-sk-focal-r3).

Stage: dev · commit 0b2364ff37 · 2026-10-21T20:57:27+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-r3 @ b3e835729b · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.824 [0.71, 0.93] | 0.909 [0.78, 1.00] | 0.864 [0.77, 0.95] | 0.891 [0.78, 0.97] | 20 / 22 |
| email | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3 | 0.891 [0.86, 0.92] | 0.954 [0.94, 0.97] | 0.922 [0.90, 0.94] | 0.941 [0.92, 0.96] | 500 / 524 |
| phone | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3 | 0.895 [0.86, 0.93] | 0.941 [0.91, 0.96] | 0.917 [0.89, 0.94] | 0.931 [0.91, 0.95] | 570 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.118 [0.03, 0.25] | 0.182 [0.04, 0.39] | 0.143 [0.03, 0.30] | 0.164 [0.04, 0.35] | 4 / 22 |
| email | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3 | 0.856 [0.82, 0.89] | 0.918 [0.90, 0.94] | 0.886 [0.86, 0.91] | 0.905 [0.88, 0.92] | 481 / 524 |
| phone | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3 | 0.827 [0.79, 0.86] | 0.873 [0.84, 0.90] | 0.849 [0.82, 0.88] | 0.863 [0.83, 0.89] | 529 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.409 [0.28, 0.52] | 0.227 [0.06, 0.46] | 1.3 [0.5, 2.2] | 5 / 22 |
| email | rules+gliner-cs-sk-focal-r3 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-r3 | 0.036 [0.02, 0.05] | 0.929 [0.91, 0.95] | 4.7 [3.2, 6.2] | 487 / 524 |
| phone | rules+gliner-cs-sk-focal-r3 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-r3 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-r3 | 0.099 [0.07, 0.13] | 0.884 [0.85, 0.91] | 5.9 [4.0, 7.9] | 536 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3 | 0.806 [0.73, 0.88] | 0.938 [0.90, 0.97] | 0.867 [0.82, 0.91] | 0.909 [0.87, 0.94] | 259 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3 | 0.781 [0.70, 0.86] | 0.906 [0.86, 0.95] | 0.839 [0.78, 0.89] | 0.878 [0.83, 0.92] | 250 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-r3 | 0.049 [0.03, 0.07] | 0.920 [0.87, 0.96] | 7.8 [4.4, 11.5] | 254 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.509 [0.36, 0.67] | 1.000 [1.00, 1.00] | 0.675 [0.53, 0.80] | 0.839 [0.74, 0.91] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3 | 0.780 [0.62, 0.93] | 0.991 [0.98, 1.00] | 0.873 [0.76, 0.96] | 0.940 [0.88, 0.98] | 217 / 219 |
| phone | rules+gliner-cs-sk-focal-r3 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3 | 0.795 [0.69, 0.88] | 0.905 [0.86, 0.94] | 0.846 [0.78, 0.90] | 0.880 [0.84, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.434 [0.29, 0.60] | 0.852 [0.69, 0.97] | 0.575 [0.41, 0.73] | 0.714 [0.55, 0.85] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3 | 0.578 [0.44, 0.74] | 0.708 [0.60, 0.82] | 0.637 [0.51, 0.77] | 0.677 [0.57, 0.79] | 155 / 219 |
| phone | rules+gliner-cs-sk-focal-r3 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3 | 0.654 [0.56, 0.76] | 0.732 [0.67, 0.80] | 0.691 [0.62, 0.77] | 0.715 [0.65, 0.79] | 284 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.3 [3.1, 10.2] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-r3 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-r3 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-r3 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-r3 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-r3 | 0.009 [0.00, 0.02] | 0.982 [0.96, 1.00] | 12.0 [6.7, 18.6] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-r3 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-r3 | 0.063 [0.03, 0.10] | 0.912 [0.86, 0.95] | 20.0 [13.2, 27.8] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.987 [0.98, 0.99] | 0.959 [0.95, 0.97] | 0.973 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2032 / 2119 |
| email | rules+gliner-cs-sk-focal-r3 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-r3 | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4319 / 4353 |
| any | rules+gliner-cs-sk-focal-r3 | 0.993 [0.99, 0.99] | 0.985 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8960 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.842 [0.83, 0.86] | 0.833 [0.82, 0.85] | 0.837 [0.82, 0.85] | 0.835 [0.82, 0.85] | 1765 / 2119 |
| email | rules+gliner-cs-sk-focal-r3 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-r3 | 0.979 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.979 [0.97, 0.98] | 4264 / 4353 |
| any | rules+gliner-cs-sk-focal-r3 | 0.941 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.938 [0.93, 0.94] | 8526 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.082 [0.07, 0.10] | 0.937 [0.93, 0.95] | 1.2 [0.9, 1.4] | 1986 / 2119 |
| email | rules+gliner-cs-sk-focal-r3 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-r3 | 0.007 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.4 [0.3, 0.5] | 4307 / 4353 |
| any | rules+gliner-cs-sk-focal-r3 | 0.036 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.6 [1.4, 1.9] | 8788 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.982 [0.98, 0.99] | 0.962 [0.95, 0.97] | 0.972 [0.97, 0.98] | 0.966 [0.96, 0.97] | 2038 / 2118 |
| email | rules+gliner-cs-sk-focal-r3 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-r3 | 0.994 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4303 / 4344 |
| any | rules+gliner-cs-sk-focal-r3 | 0.993 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8797 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.823 [0.81, 0.84] | 0.823 [0.80, 0.84] | 0.823 [0.81, 0.84] | 0.823 [0.81, 0.84] | 1742 / 2118 |
| email | rules+gliner-cs-sk-focal-r3 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-r3 | 0.975 [0.97, 0.98] | 0.971 [0.96, 0.98] | 0.973 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4218 / 4344 |
| any | rules+gliner-cs-sk-focal-r3 | 0.936 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8325 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-r3 | 0.090 [0.07, 0.11] | 0.943 [0.93, 0.95] | 1.3 [1.1, 1.5] | 1997 / 2118 |
| email | rules+gliner-cs-sk-focal-r3 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-r3 | 0.007 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.3, 0.5] | 4290 / 4344 |
| any | rules+gliner-cs-sk-focal-r3 | 0.037 [0.03, 0.04] | 0.969 [0.96, 0.97] | 1.8 [1.5, 2.0] | 8648 / 8927 |
