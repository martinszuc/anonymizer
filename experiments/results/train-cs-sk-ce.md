# train-cs-sk-ce-dev

rules+gliner-cs-sk-ce after training (train-cs-sk-ce).

Stage: dev · commit fd77019ce6 · 2026-10-11T02:16:55+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-ce @ ee7c5fb9d2 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce | 0.857 [0.75, 0.95] | 0.955 [0.82, 1.00] | 0.903 [0.81, 0.97] | 0.933 [0.82, 0.99] | 21 / 22 |
| email | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce | 0.918 [0.89, 0.95] | 0.933 [0.91, 0.95] | 0.925 [0.90, 0.94] | 0.930 [0.91, 0.95] | 489 / 524 |
| phone | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce | 0.920 [0.89, 0.95] | 0.926 [0.90, 0.95] | 0.923 [0.90, 0.94] | 0.925 [0.90, 0.95] | 561 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce | 0.114 [0.03, 0.26] | 0.182 [0.04, 0.40] | 0.140 [0.03, 0.31] | 0.163 [0.03, 0.36] | 4 / 22 |
| email | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-ce | 0.882 [0.85, 0.91] | 0.899 [0.87, 0.92] | 0.890 [0.87, 0.91] | 0.895 [0.87, 0.92] | 471 / 524 |
| phone | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-ce | 0.847 [0.81, 0.88] | 0.856 [0.82, 0.89] | 0.852 [0.81, 0.88] | 0.855 [0.82, 0.89] | 519 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce | 0.848 [0.76, 0.93] | 0.902 [0.85, 0.94] | 0.874 [0.82, 0.92] | 0.891 [0.85, 0.93] | 249 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-ce | 0.814 [0.73, 0.90] | 0.855 [0.80, 0.90] | 0.834 [0.78, 0.89] | 0.847 [0.80, 0.89] | 236 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce | 0.540 [0.39, 0.70] | 1.000 [1.00, 1.00] | 0.701 [0.56, 0.82] | 0.854 [0.76, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce | 0.801 [0.63, 0.95] | 0.991 [0.98, 1.00] | 0.886 [0.77, 0.97] | 0.946 [0.89, 0.98] | 217 / 219 |
| phone | rules+gliner-cs-sk-ce | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce | 0.807 [0.70, 0.90] | 0.905 [0.86, 0.94] | 0.853 [0.78, 0.91] | 0.883 [0.84, 0.92] | 351 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce | 0.440 [0.29, 0.60] | 0.815 [0.64, 0.96] | 0.571 [0.41, 0.72] | 0.696 [0.53, 0.83] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-ce | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-ce | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-ce | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-ce | 0.605 [0.46, 0.76] | 0.722 [0.62, 0.83] | 0.658 [0.54, 0.79] | 0.695 [0.59, 0.81] | 158 / 219 |
| phone | rules+gliner-cs-sk-ce | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-ce | 0.674 [0.57, 0.78] | 0.737 [0.68, 0.80] | 0.704 [0.63, 0.78] | 0.724 [0.67, 0.79] | 286 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce | 0.997 [0.99, 1.00] | 0.953 [0.94, 0.96] | 0.975 [0.97, 0.98] | 0.962 [0.95, 0.97] | 2020 / 2119 |
| email | rules+gliner-cs-sk-ce | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-ce | 0.995 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4307 / 4353 |
| any | rules+gliner-cs-sk-ce | 0.997 [1.00, 1.00] | 0.982 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.985 [0.98, 0.99] | 8937 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce | 0.850 [0.83, 0.87] | 0.828 [0.81, 0.84] | 0.839 [0.82, 0.85] | 0.833 [0.82, 0.85] | 1755 / 2119 |
| email | rules+gliner-cs-sk-ce | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-ce | 0.984 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.979 [0.97, 0.98] | 4257 / 4353 |
| any | rules+gliner-cs-sk-ce | 0.945 [0.94, 0.95] | 0.935 [0.93, 0.94] | 0.940 [0.94, 0.94] | 0.937 [0.93, 0.94] | 8508 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce | 0.995 [0.99, 1.00] | 0.960 [0.95, 0.97] | 0.978 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2034 / 2118 |
| email | rules+gliner-cs-sk-ce | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-ce | 0.996 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4301 / 4344 |
| any | rules+gliner-cs-sk-ce | 0.997 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8788 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-ce | 0.835 [0.82, 0.85] | 0.821 [0.80, 0.84] | 0.828 [0.81, 0.84] | 0.824 [0.81, 0.84] | 1739 / 2118 |
| email | rules+gliner-cs-sk-ce | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-ce | 0.978 [0.97, 0.98] | 0.972 [0.96, 0.98] | 0.975 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4220 / 4344 |
| any | rules+gliner-cs-sk-ce | 0.940 [0.93, 0.95] | 0.932 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8322 / 8927 |
