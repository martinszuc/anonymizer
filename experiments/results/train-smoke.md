# train-smoke-dev

rules+gliner-cs-sk-smoke after training (train-smoke).

Stage: dev · commit aa9a994a05 · 2026-10-10T17:56:21+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-smoke @ b1be281da1 · tool 0.5.0

## cnec-2.0/dtest · cs · dev

25 documents, 25 pages, 300 sentences or records. Gold spans: address 9, email 9, person 218, phone 16.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke | 0.684 [0.29, 0.88] | 1.000 [1.00, 1.00] | 0.812 [0.46, 0.93] | 0.915 [0.68, 0.97] | 9 / 9 |
| email | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 9 / 9 |
| person | rules+gliner-cs-sk-smoke | 0.915 [0.86, 0.96] | 0.936 [0.90, 0.97] | 0.925 [0.89, 0.95] | 0.931 [0.90, 0.96] | 204 / 218 |
| phone | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.375 [0.00, 1.00] | 0.545 [0.00, 1.00] | 0.429 [0.00, 1.00] | 6 / 16 |
| url | rules+gliner-cs-sk-smoke | – | – | – | – | 0 / 0 |
| any | rules+gliner-cs-sk-smoke | 0.903 [0.86, 0.94] | 0.921 [0.87, 0.96] | 0.912 [0.87, 0.94] | 0.917 [0.87, 0.95] | 232 / 252 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke | 0.053 [0.00, 0.29] | 0.111 [0.00, 0.50] | 0.071 [0.00, 0.36] | 0.091 [0.00, 0.41] | 1 / 9 |
| email | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 9 / 9 |
| person | rules+gliner-cs-sk-smoke | 0.879 [0.83, 0.93] | 0.899 [0.86, 0.93] | 0.889 [0.85, 0.92] | 0.895 [0.86, 0.92] | 196 / 218 |
| phone | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.375 [0.00, 1.00] | 0.545 [0.00, 1.00] | 0.429 [0.00, 1.00] | 6 / 16 |
| url | rules+gliner-cs-sk-smoke | – | – | – | – | 0 / 0 |
| any | rules+gliner-cs-sk-smoke | 0.829 [0.74, 0.89] | 0.845 [0.77, 0.90] | 0.837 [0.76, 0.89] | 0.842 [0.76, 0.90] | 213 / 252 |

## uner-sk-snk/dev · sk · dev

25 documents, 75 pages, 750 sentences or records. Gold spans: person 167.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-smoke | 0.646 [0.47, 0.82] | 0.766 [0.67, 0.85] | 0.701 [0.57, 0.80] | 0.739 [0.65, 0.82] | 128 / 167 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-smoke | 0.631 [0.46, 0.80] | 0.737 [0.64, 0.82] | 0.680 [0.56, 0.77] | 0.713 [0.62, 0.79] | 123 / 167 |

## redact/sample · cs · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 13, birth_number 14, date 22, email 33, id_number 4, person 134, phone 17.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke | 0.245 [0.12, 0.43] | 1.000 [1.00, 1.00] | 0.394 [0.21, 0.61] | 0.619 [0.39, 0.79] | 13 / 13 |
| birth_number | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.071 [0.00, 0.21] | 0.133 [0.00, 0.35] | 0.088 [0.00, 0.25] | 1 / 14 |
| date | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.500 [0.16, 0.84] | 0.667 [0.27, 0.91] | 0.556 [0.19, 0.87] | 11 / 22 |
| email | rules+gliner-cs-sk-smoke | 0.917 [0.74, 1.00] | 1.000 [1.00, 1.00] | 0.957 [0.85, 1.00] | 0.982 [0.93, 1.00] | 33 / 33 |
| id_number | rules+gliner-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 4 |
| person | rules+gliner-cs-sk-smoke | 0.694 [0.52, 0.90] | 0.978 [0.95, 1.00] | 0.812 [0.67, 0.94] | 0.904 [0.83, 0.96] | 131 / 134 |
| phone | rules+gliner-cs-sk-smoke | 0.889 [0.73, 1.00] | 0.941 [0.81, 1.00] | 0.914 [0.78, 1.00] | 0.930 [0.80, 1.00] | 16 / 17 |
| any | rules+gliner-cs-sk-smoke | 0.689 [0.57, 0.81] | 0.869 [0.80, 0.92] | 0.769 [0.68, 0.84] | 0.826 [0.76, 0.88] | 206 / 237 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke | 0.170 [0.08, 0.32] | 0.692 [0.50, 0.90] | 0.273 [0.14, 0.45] | 0.429 [0.26, 0.60] | 9 / 13 |
| birth_number | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.071 [0.00, 0.21] | 0.133 [0.00, 0.35] | 0.088 [0.00, 0.25] | 1 / 14 |
| date | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 0.500 [0.16, 0.84] | 0.667 [0.27, 0.91] | 0.556 [0.19, 0.87] | 11 / 22 |
| email | rules+gliner-cs-sk-smoke | 0.917 [0.74, 1.00] | 1.000 [1.00, 1.00] | 0.957 [0.85, 1.00] | 0.982 [0.93, 1.00] | 33 / 33 |
| id_number | rules+gliner-cs-sk-smoke | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 4 |
| person | rules+gliner-cs-sk-smoke | 0.550 [0.38, 0.75] | 0.739 [0.59, 0.86] | 0.631 [0.48, 0.79] | 0.691 [0.55, 0.82] | 99 / 134 |
| phone | rules+gliner-cs-sk-smoke | 0.889 [0.73, 1.00] | 0.941 [0.81, 1.00] | 0.914 [0.78, 1.00] | 0.930 [0.80, 1.00] | 16 / 17 |
| any | rules+gliner-cs-sk-smoke | 0.569 [0.45, 0.68] | 0.717 [0.62, 0.80] | 0.634 [0.54, 0.72] | 0.682 [0.59, 0.76] | 170 / 237 |

## openpii-1m-cs/dev · cs · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 13, email 18, person 26.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke | 0.722 [0.50, 0.90] | 0.923 [0.75, 1.00] | 0.810 [0.64, 0.93] | 0.874 [0.73, 0.97] | 12 / 13 |
| email | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 18 / 18 |
| person | rules+gliner-cs-sk-smoke | 0.743 [0.56, 0.95] | 1.000 [1.00, 1.00] | 0.853 [0.71, 0.98] | 0.935 [0.86, 0.99] | 26 / 26 |
| any | rules+gliner-cs-sk-smoke | 0.817 [0.67, 0.92] | 0.983 [0.94, 1.00] | 0.892 [0.80, 0.95] | 0.944 [0.89, 0.98] | 56 / 57 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke | 0.500 [0.28, 0.73] | 0.692 [0.43, 0.92] | 0.581 [0.33, 0.80] | 0.643 [0.39, 0.87] | 9 / 13 |
| email | rules+gliner-cs-sk-smoke | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 17 / 18 |
| person | rules+gliner-cs-sk-smoke | 0.714 [0.52, 0.92] | 0.962 [0.86, 1.00] | 0.820 [0.66, 0.95] | 0.899 [0.77, 0.98] | 25 / 26 |
| any | rules+gliner-cs-sk-smoke | 0.718 [0.56, 0.84] | 0.895 [0.79, 0.98] | 0.797 [0.67, 0.90] | 0.853 [0.75, 0.94] | 51 / 57 |

## openpii-1m-sk/dev · sk · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 9, email 15, person 36.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke | 0.600 [0.36, 0.84] | 1.000 [1.00, 1.00] | 0.750 [0.53, 0.91] | 0.882 [0.74, 0.96] | 9 / 9 |
| email | rules+gliner-cs-sk-smoke | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 15 / 15 |
| person | rules+gliner-cs-sk-smoke | 0.875 [0.75, 0.97] | 0.972 [0.91, 1.00] | 0.921 [0.85, 0.99] | 0.951 [0.89, 0.99] | 35 / 36 |
| any | rules+gliner-cs-sk-smoke | 0.843 [0.77, 0.92] | 0.983 [0.94, 1.00] | 0.908 [0.85, 0.96] | 0.952 [0.91, 0.98] | 59 / 60 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke | 0.267 [0.06, 0.50] | 0.444 [0.10, 0.83] | 0.333 [0.08, 0.60] | 0.392 [0.09, 0.70] | 4 / 9 |
| email | rules+gliner-cs-sk-smoke | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 14 / 15 |
| person | rules+gliner-cs-sk-smoke | 0.825 [0.69, 0.94] | 0.917 [0.79, 1.00] | 0.868 [0.75, 0.96] | 0.897 [0.78, 0.98] | 33 / 36 |
| any | rules+gliner-cs-sk-smoke | 0.729 [0.62, 0.83] | 0.850 [0.73, 0.95] | 0.785 [0.67, 0.88] | 0.823 [0.71, 0.92] | 51 / 60 |
