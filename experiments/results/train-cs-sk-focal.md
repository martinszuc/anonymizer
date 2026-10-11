# train-cs-sk-focal-dev

rules+gliner-cs-sk-focal after training (train-cs-sk-focal).

Stage: dev · commit fd77019ce6 · 2026-10-11T04:16:08+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-focal @ a9c8ebc1ab · tool 0.5.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal | 0.780 [0.66, 0.90] | 1.000 [1.00, 1.00] | 0.877 [0.79, 0.95] | 0.947 [0.91, 0.98] | 22 / 22 |
| email | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal | 0.867 [0.83, 0.90] | 0.945 [0.92, 0.96] | 0.904 [0.88, 0.93] | 0.928 [0.91, 0.95] | 495 / 524 |
| phone | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal | 0.871 [0.83, 0.91] | 0.936 [0.91, 0.96] | 0.902 [0.87, 0.93] | 0.922 [0.90, 0.94] | 567 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal | 0.098 [0.02, 0.22] | 0.182 [0.04, 0.40] | 0.127 [0.03, 0.28] | 0.155 [0.03, 0.34] | 4 / 22 |
| email | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner-cs-sk-focal | 0.832 [0.79, 0.87] | 0.908 [0.89, 0.93] | 0.869 [0.84, 0.89] | 0.892 [0.87, 0.91] | 476 / 524 |
| phone | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner-cs-sk-focal | 0.798 [0.75, 0.84] | 0.865 [0.83, 0.90] | 0.830 [0.79, 0.86] | 0.850 [0.81, 0.88] | 524 / 606 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal | 0.810 [0.73, 0.89] | 0.949 [0.91, 0.98] | 0.874 [0.82, 0.92] | 0.918 [0.88, 0.95] | 262 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-focal | 0.782 [0.70, 0.85] | 0.909 [0.87, 0.95] | 0.841 [0.79, 0.89] | 0.881 [0.84, 0.92] | 251 / 276 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal | 0.528 [0.38, 0.68] | 1.000 [1.00, 1.00] | 0.691 [0.55, 0.81] | 0.849 [0.75, 0.92] | 27 / 27 |
| birth_number | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal | 0.801 [0.64, 0.95] | 0.995 [0.99, 1.00] | 0.888 [0.78, 0.97] | 0.950 [0.89, 0.99] | 218 / 219 |
| phone | rules+gliner-cs-sk-focal | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal | 0.808 [0.70, 0.90] | 0.907 [0.86, 0.95] | 0.855 [0.79, 0.91] | 0.886 [0.84, 0.92] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal | 0.415 [0.27, 0.58] | 0.815 [0.64, 0.96] | 0.550 [0.39, 0.70] | 0.683 [0.52, 0.82] | 22 / 27 |
| birth_number | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner-cs-sk-focal | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner-cs-sk-focal | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner-cs-sk-focal | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner-cs-sk-focal | 0.592 [0.45, 0.76] | 0.708 [0.60, 0.82] | 0.644 [0.52, 0.78] | 0.681 [0.57, 0.80] | 155 / 219 |
| phone | rules+gliner-cs-sk-focal | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner-cs-sk-focal | 0.661 [0.56, 0.77] | 0.729 [0.67, 0.80] | 0.694 [0.62, 0.77] | 0.715 [0.65, 0.78] | 283 / 388 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal | 0.994 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2030 / 2119 |
| email | rules+gliner-cs-sk-focal | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner-cs-sk-focal | 0.991 [0.99, 0.99] | 0.989 [0.99, 0.99] | 0.990 [0.99, 0.99] | 0.989 [0.99, 0.99] | 4304 / 4353 |
| any | rules+gliner-cs-sk-focal | 0.994 [0.99, 1.00] | 0.983 [0.98, 0.99] | 0.989 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8946 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal | 0.846 [0.83, 0.86] | 0.832 [0.81, 0.85] | 0.839 [0.82, 0.85] | 0.834 [0.82, 0.85] | 1762 / 2119 |
| email | rules+gliner-cs-sk-focal | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner-cs-sk-focal | 0.979 [0.97, 0.98] | 0.976 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.977 [0.97, 0.98] | 4249 / 4353 |
| any | rules+gliner-cs-sk-focal | 0.942 [0.94, 0.95] | 0.935 [0.93, 0.94] | 0.938 [0.93, 0.94] | 0.936 [0.93, 0.94] | 8507 / 9097 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal | 0.991 [0.99, 0.99] | 0.964 [0.96, 0.97] | 0.977 [0.97, 0.98] | 0.969 [0.96, 0.98] | 2041 / 2118 |
| email | rules+gliner-cs-sk-focal | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner-cs-sk-focal | 0.995 [0.99, 1.00] | 0.988 [0.98, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4293 / 4344 |
| any | rules+gliner-cs-sk-focal | 0.996 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8788 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-focal | 0.832 [0.82, 0.85] | 0.824 [0.81, 0.84] | 0.828 [0.81, 0.84] | 0.825 [0.81, 0.84] | 1745 / 2118 |
| email | rules+gliner-cs-sk-focal | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner-cs-sk-focal | 0.976 [0.97, 0.98] | 0.969 [0.96, 0.97] | 0.972 [0.97, 0.98] | 0.970 [0.96, 0.98] | 4207 / 4344 |
| any | rules+gliner-cs-sk-focal | 0.939 [0.93, 0.94] | 0.932 [0.93, 0.94] | 0.935 [0.93, 0.94] | 0.933 [0.93, 0.94] | 8316 / 8927 |
