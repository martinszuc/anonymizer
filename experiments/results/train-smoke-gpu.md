# train-smoke-gpu-dev

rules+gliner-cs-sk-smoke-gpu after training (train-smoke-gpu).

Stage: dev · commit 0211b3728e · 2026-10-14T16:57:11+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-cs-sk-smoke-gpu @ 71264fb5b5 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

25 documents, 25 pages, 300 sentences or records. Gold spans: address 9, email 9, person 218, phone 16.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.652 [0.29, 0.81] | 1.000 [1.00, 1.00] | 0.789 [0.44, 0.89] | 0.904 [0.67, 0.96] | 9 / 9 |
| email | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 9 / 9 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.915 [0.86, 0.96] | 0.936 [0.90, 0.96] | 0.925 [0.89, 0.95] | 0.932 [0.90, 0.96] | 204 / 218 |
| phone | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 0.375 [0.00, 1.00] | 0.545 [0.00, 1.00] | 0.429 [0.00, 1.00] | 6 / 16 |
| url | rules+gliner-cs-sk-smoke-gpu | – | – | – | – | 0 / 0 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.905 [0.86, 0.95] | 0.932 [0.89, 0.96] | 0.918 [0.88, 0.95] | 0.927 [0.89, 0.95] | 235 / 252 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.043 [0.00, 0.25] | 0.111 [0.00, 0.50] | 0.062 [0.00, 0.33] | 0.085 [0.00, 0.41] | 1 / 9 |
| email | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 9 / 9 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.884 [0.83, 0.93] | 0.908 [0.87, 0.93] | 0.896 [0.86, 0.92] | 0.903 [0.87, 0.93] | 198 / 218 |
| phone | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 0.375 [0.00, 1.00] | 0.545 [0.00, 1.00] | 0.429 [0.00, 1.00] | 6 / 16 |
| url | rules+gliner-cs-sk-smoke-gpu | – | – | – | – | 0 / 0 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.832 [0.75, 0.90] | 0.865 [0.80, 0.91] | 0.848 [0.77, 0.90] | 0.858 [0.79, 0.91] | 218 / 252 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.254 [0.13, 0.38] | 0.111 [0.00, 0.50] | 2.6 [0.6, 5.0] | 1 / 9 |
| email | rules+gliner-cs-sk-smoke-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 9 / 9 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.043 [0.02, 0.06] | 0.922 [0.89, 0.95] | 4.8 [1.8, 8.6] | 201 / 218 |
| phone | rules+gliner-cs-sk-smoke-gpu | 0.213 [0.00, 0.42] | 0.625 [0.00, 1.00] | 0.0 [0.0, 0.0] | 10 / 16 |
| url | rules+gliner-cs-sk-smoke-gpu | – | – | 0.0 [0.0, 0.0] | 0 / 0 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.079 [0.05, 0.11] | 0.877 [0.82, 0.92] | 7.4 [3.2, 12.3] | 221 / 252 |

## uner-sk-snk/dev · sk · dev

25 documents, 75 pages, 750 sentences or records. Gold spans: person 167.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-smoke-gpu | 0.649 [0.48, 0.82] | 0.760 [0.66, 0.85] | 0.701 [0.58, 0.80] | 0.735 [0.64, 0.82] | 127 / 167 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-smoke-gpu | 0.639 [0.47, 0.81] | 0.743 [0.63, 0.84] | 0.687 [0.57, 0.79] | 0.719 [0.61, 0.81] | 124 / 167 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner-cs-sk-smoke-gpu | 0.212 [0.13, 0.29] | 0.760 [0.66, 0.85] | 9.9 [4.4, 17.3] | 127 / 167 |

## redact/sample · cs · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 13, birth_number 14, date 22, email 33, id_number 4, person 134, phone 17.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.265 [0.12, 0.47] | 1.000 [1.00, 1.00] | 0.419 [0.22, 0.64] | 0.644 [0.42, 0.82] | 13 / 13 |
| birth_number | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 0.071 [0.00, 0.21] | 0.133 [0.00, 0.35] | 0.088 [0.00, 0.25] | 1 / 14 |
| date | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 0.500 [0.16, 0.84] | 0.667 [0.27, 0.91] | 0.556 [0.19, 0.87] | 11 / 22 |
| email | rules+gliner-cs-sk-smoke-gpu | 0.917 [0.74, 1.00] | 1.000 [1.00, 1.00] | 0.957 [0.85, 1.00] | 0.982 [0.93, 1.00] | 33 / 33 |
| id_number | rules+gliner-cs-sk-smoke-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 4 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.692 [0.51, 0.89] | 0.985 [0.96, 1.00] | 0.813 [0.67, 0.93] | 0.908 [0.83, 0.97] | 132 / 134 |
| phone | rules+gliner-cs-sk-smoke-gpu | 0.889 [0.73, 1.00] | 0.941 [0.81, 1.00] | 0.914 [0.78, 1.00] | 0.930 [0.80, 1.00] | 16 / 17 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.697 [0.58, 0.81] | 0.873 [0.80, 0.93] | 0.775 [0.69, 0.85] | 0.831 [0.77, 0.88] | 207 / 237 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.184 [0.08, 0.34] | 0.692 [0.50, 0.90] | 0.290 [0.15, 0.46] | 0.446 [0.27, 0.61] | 9 / 13 |
| birth_number | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 0.071 [0.00, 0.21] | 0.133 [0.00, 0.35] | 0.088 [0.00, 0.25] | 1 / 14 |
| date | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 0.500 [0.16, 0.84] | 0.667 [0.27, 0.91] | 0.556 [0.19, 0.87] | 11 / 22 |
| email | rules+gliner-cs-sk-smoke-gpu | 0.917 [0.74, 1.00] | 1.000 [1.00, 1.00] | 0.957 [0.85, 1.00] | 0.982 [0.93, 1.00] | 33 / 33 |
| id_number | rules+gliner-cs-sk-smoke-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 4 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.555 [0.39, 0.75] | 0.754 [0.61, 0.87] | 0.639 [0.49, 0.79] | 0.703 [0.58, 0.83] | 101 / 134 |
| phone | rules+gliner-cs-sk-smoke-gpu | 0.889 [0.73, 1.00] | 0.941 [0.81, 1.00] | 0.914 [0.78, 1.00] | 0.930 [0.80, 1.00] | 16 / 17 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.579 [0.46, 0.70] | 0.726 [0.64, 0.80] | 0.644 [0.55, 0.73] | 0.691 [0.61, 0.77] | 172 / 237 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.075 [0.00, 0.16] | 0.769 [0.55, 1.00] | 14.2 [5.9, 25.0] | 10 / 13 |
| birth_number | rules+gliner-cs-sk-smoke-gpu | 0.607 [0.36, 0.85] | 0.429 [0.17, 0.67] | 0.0 [0.0, 0.0] | 6 / 14 |
| date | rules+gliner-cs-sk-smoke-gpu | 0.508 [0.17, 0.84] | 0.500 [0.16, 0.84] | 0.0 [0.0, 0.0] | 11 / 22 |
| email | rules+gliner-cs-sk-smoke-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.6 [0.0, 5.1] | 33 / 33 |
| id_number | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 4 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.012 [0.00, 0.03] | 0.978 [0.95, 1.00] | 14.1 [6.1, 24.2] | 131 / 134 |
| phone | rules+gliner-cs-sk-smoke-gpu | 0.057 [0.00, 0.18] | 0.941 [0.81, 1.00] | 0.2 [0.0, 0.7] | 16 / 17 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.096 [0.05, 0.16] | 0.873 [0.79, 0.93] | 30.2 [19.4, 42.5] | 207 / 237 |

## openpii-1m-cs/dev · cs · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 13, email 18, person 26.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.650 [0.47, 0.82] | 0.923 [0.75, 1.00] | 0.763 [0.60, 0.88] | 0.852 [0.70, 0.94] | 12 / 13 |
| email | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 18 / 18 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.743 [0.56, 0.94] | 1.000 [1.00, 1.00] | 0.853 [0.71, 0.97] | 0.935 [0.86, 0.99] | 26 / 26 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.808 [0.67, 0.91] | 0.983 [0.94, 1.00] | 0.887 [0.80, 0.94] | 0.942 [0.89, 0.97] | 56 / 57 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.500 [0.32, 0.68] | 0.769 [0.55, 1.00] | 0.606 [0.41, 0.77] | 0.694 [0.48, 0.87] | 10 / 13 |
| email | rules+gliner-cs-sk-smoke-gpu | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 0.944 [0.79, 1.00] | 17 / 18 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.714 [0.52, 0.91] | 0.962 [0.86, 1.00] | 0.820 [0.67, 0.95] | 0.899 [0.79, 0.98] | 25 / 26 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.712 [0.59, 0.82] | 0.912 [0.81, 0.98] | 0.800 [0.69, 0.89] | 0.864 [0.76, 0.94] | 52 / 57 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.122 [0.00, 0.29] | 0.769 [0.55, 1.00] | 8.2 [3.0, 14.3] | 10 / 13 |
| email | rules+gliner-cs-sk-smoke-gpu | 0.016 [0.00, 0.06] | 0.944 [0.79, 1.00] | 0.0 [0.0, 0.0] | 17 / 18 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.9 [0.6, 15.4] | 26 / 26 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.049 [0.00, 0.11] | 0.930 [0.86, 0.98] | 15.0 [7.6, 23.9] | 53 / 57 |

## openpii-1m-sk/dev · sk · dev

25 documents, 25 pages, 25 sentences or records. Gold spans: address 9, email 15, person 36.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.556 [0.26, 0.88] | 0.889 [0.60, 1.00] | 0.684 [0.38, 0.91] | 0.794 [0.51, 0.95] | 8 / 9 |
| email | rules+gliner-cs-sk-smoke-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 15 / 15 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.921 [0.82, 1.00] | 0.972 [0.91, 1.00] | 0.946 [0.88, 0.99] | 0.962 [0.91, 1.00] | 35 / 36 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.845 [0.75, 0.94] | 0.967 [0.91, 1.00] | 0.902 [0.84, 0.96] | 0.940 [0.89, 0.98] | 58 / 60 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.278 [0.06, 0.58] | 0.556 [0.14, 0.89] | 0.370 [0.08, 0.67] | 0.463 [0.11, 0.77] | 5 / 9 |
| email | rules+gliner-cs-sk-smoke-gpu | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 0.933 [0.77, 1.00] | 14 / 15 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.868 [0.76, 0.97] | 0.917 [0.79, 1.00] | 0.892 [0.78, 0.97] | 0.907 [0.79, 0.99] | 33 / 36 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.732 [0.62, 0.85] | 0.867 [0.77, 0.95] | 0.794 [0.70, 0.89] | 0.836 [0.75, 0.91] | 52 / 60 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner-cs-sk-smoke-gpu | 0.117 [0.00, 0.39] | 0.667 [0.29, 1.00] | 10.2 [2.4, 20.7] | 6 / 9 |
| email | rules+gliner-cs-sk-smoke-gpu | 0.011 [0.00, 0.04] | 0.933 [0.77, 1.00] | 0.0 [0.0, 0.0] | 14 / 15 |
| person | rules+gliner-cs-sk-smoke-gpu | 0.018 [0.00, 0.06] | 0.972 [0.91, 1.00] | 3.3 [0.5, 7.1] | 35 / 36 |
| any | rules+gliner-cs-sk-smoke-gpu | 0.038 [0.00, 0.09] | 0.917 [0.85, 0.98] | 13.5 [4.4, 24.6] | 55 / 60 |
