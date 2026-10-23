# train-cs-sk-focal-more-s2-dev

rules+gliner-cs-sk-focal-more-s2 after training (train-cs-sk-focal-more-s2).

Stage: dev · commit caf443dff4 · 2026-10-22T14:34:37+00:00 · seed 2, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal-more-s2 @ 20602b4e09 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.816 [0.70, 0.91] | 1.000 [1.00, 1.00] | 0.899 [0.82, 0.95] | 0.957 [0.92, 0.98] | 22 / 22 |
| email | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.854 [0.81, 0.89] | 0.949 [0.93, 0.97] | 0.899 [0.87, 0.92] | 0.928 [0.91, 0.95] | 497 / 524 |
| phone | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.862 [0.82, 0.90] | 0.937 [0.91, 0.96] | 0.898 [0.87, 0.92] | 0.921 [0.90, 0.94] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.105 [0.02, 0.23] | 0.182 [0.04, 0.40] | 0.133 [0.03, 0.29] | 0.159 [0.04, 0.36] | 4 / 22 |
| email | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.818 [0.78, 0.86] | 0.910 [0.89, 0.93] | 0.862 [0.83, 0.89] | 0.890 [0.86, 0.91] | 477 / 524 |
| phone | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.88] | 0.767 [0.45, 0.93] | 0.672 [0.34, 0.90] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.789 [0.74, 0.83] | 0.866 [0.83, 0.90] | 0.826 [0.79, 0.86] | 0.850 [0.81, 0.88] | 525 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.393 [0.27, 0.51] | 0.273 [0.10, 0.50] | 1.5 [0.6, 2.6] | 6 / 22 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.039 [0.03, 0.05] | 0.926 [0.90, 0.94] | 6.7 [5.0, 8.7] | 485 / 524 |
| phone | rules+gliner-cs-sk-focal-more-s2 | 0.318 [0.09, 0.61] | 0.622 [0.29, 0.88] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner-cs-sk-focal-more-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.098 [0.07, 0.13] | 0.883 [0.85, 0.91] | 8.1 [5.9, 10.6] | 535 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.829 [0.72, 0.91] | 0.993 [0.98, 1.00] | 0.903 [0.84, 0.95] | 0.955 [0.92, 0.98] | 274 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.792 [0.69, 0.87] | 0.938 [0.90, 0.97] | 0.859 [0.79, 0.91] | 0.905 [0.86, 0.94] | 259 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.005 [0.00, 0.01] | 0.975 [0.94, 1.00] | 6.6 [3.2, 11.5] | 269 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.509 [0.37, 0.67] | 1.000 [1.00, 1.00] | 0.675 [0.54, 0.80] | 0.838 [0.74, 0.91] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.769 [0.61, 0.93] | 0.995 [0.99, 1.00] | 0.868 [0.76, 0.96] | 0.940 [0.89, 0.98] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal-more-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.785 [0.68, 0.88] | 0.907 [0.86, 0.94] | 0.842 [0.78, 0.89] | 0.880 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.418 [0.27, 0.59] | 0.852 [0.69, 1.00] | 0.561 [0.40, 0.73] | 0.706 [0.55, 0.85] | 23 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.15] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.552 [0.29, 0.82] | 0.711 [0.45, 0.90] | 0.606 [0.34, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.92, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.579 [0.43, 0.76] | 0.722 [0.61, 0.83] | 0.642 [0.51, 0.78] | 0.688 [0.57, 0.80] | 158 / 219 |
| phone | rules+gliner-cs-sk-focal-more-s2 | 0.812 [0.65, 0.97] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.651 [0.55, 0.76] | 0.740 [0.68, 0.80] | 0.692 [0.62, 0.77] | 0.720 [0.66, 0.78] | 287 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 7.0 [3.3, 11.5] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal-more-s2 | 0.572 [0.36, 0.81] | 0.450 [0.21, 0.65] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner-cs-sk-focal-more-s2 | 0.462 [0.20, 0.71] | 0.552 [0.29, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.1] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal-more-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.008 [0.00, 0.02] | 0.982 [0.95, 1.00] | 13.3 [6.0, 22.9] | 215 / 219 |
| phone | rules+gliner-cs-sk-focal-more-s2 | 0.035 [0.00, 0.12] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.0] | 26 / 27 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 22.0 [13.7, 31.1] | 354 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.984 [0.98, 0.99] | 0.962 [0.95, 0.97] | 0.973 [0.97, 0.98] | 0.966 [0.96, 0.97] | 2038 / 2119 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.990 [0.99, 0.99] | 0.990 [0.99, 0.99] | 0.990 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4308 / 4353 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.992 [0.99, 0.99] | 0.985 [0.98, 0.99] | 0.988 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8957 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.829 [0.81, 0.85] | 0.827 [0.81, 0.84] | 0.828 [0.81, 0.84] | 0.828 [0.81, 0.84] | 1753 / 2119 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.978 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4255 / 4353 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8506 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.076 [0.06, 0.09] | 0.933 [0.92, 0.94] | 1.2 [1.0, 1.4] | 1978 / 2119 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.009 [0.01, 0.01] | 0.987 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4296 / 4353 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.035 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.7 [1.4, 1.9] | 8769 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.977 [0.97, 0.98] | 0.962 [0.95, 0.97] | 0.969 [0.96, 0.97] | 0.965 [0.96, 0.97] | 2037 / 2118 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.991 [0.99, 0.99] | 0.988 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.989 [0.99, 0.99] | 4292 / 4344 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.991 [0.99, 0.99] | 0.984 [0.98, 0.99] | 0.987 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8786 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.812 [0.79, 0.83] | 0.815 [0.80, 0.83] | 0.814 [0.80, 0.83] | 0.815 [0.80, 0.83] | 1727 / 2118 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.972 [0.97, 0.98] | 0.968 [0.96, 0.97] | 0.970 [0.96, 0.98] | 0.969 [0.96, 0.97] | 4206 / 4344 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.931 [0.93, 0.94] | 0.929 [0.92, 0.94] | 0.930 [0.92, 0.94] | 0.930 [0.92, 0.94] | 8297 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal-more-s2 | 0.088 [0.07, 0.11] | 0.939 [0.93, 0.95] | 1.5 [1.3, 1.8] | 1988 / 2118 |
| email | rules+gliner-cs-sk-focal-more-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner-cs-sk-focal-more-s2 | 0.009 [0.01, 0.01] | 0.985 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4280 / 4344 |
| any | rules+gliner-cs-sk-focal-more-s2 | 0.037 [0.03, 0.04] | 0.967 [0.96, 0.97] | 2.1 [1.8, 2.4] | 8629 / 8927 |

## wikigoldsk/dev · sk · dev

56 documents, 56 pages, 669 sentences or records. Gold spans: person 298.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.909 [0.86, 0.95] | 0.983 [0.96, 1.00] | 0.945 [0.92, 0.97] | 0.968 [0.95, 0.99] | 293 / 298 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.822 [0.76, 0.88] | 0.883 [0.83, 0.93] | 0.851 [0.79, 0.90] | 0.870 [0.81, 0.92] | 263 / 298 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.027 [0.01, 0.05] | 0.909 [0.86, 0.95] | 5.0 [2.8, 7.3] | 271 / 298 |

## slavicner-cs/dev · cs · dev

88 documents, 89 pages, 259 sentences or records. Gold spans: person 396.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.985 [0.97, 1.00] | 0.962 [0.93, 0.98] | 0.973 [0.96, 0.99] | 0.967 [0.94, 0.98] | 381 / 396 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.985 [0.97, 1.00] | 0.962 [0.93, 0.98] | 0.973 [0.96, 0.99] | 0.967 [0.94, 0.98] | 381 / 396 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal-more-s2 | 0.044 [0.02, 0.08] | 0.962 [0.93, 0.98] | 0.5 [0.1, 1.0] | 381 / 396 |
