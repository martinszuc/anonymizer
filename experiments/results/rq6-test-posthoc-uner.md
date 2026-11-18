# rq6-test-posthoc-uner

POST HOC addendum to rq6-test, run after the final test (29 Oct) and reported apart from it;
the final table and its verdict stay as they are. On development data NameTag 3 multilingual
scored better on UNER-SK in its uner tagset than in conll, the tagset of every earlier run
(nametag-tagset-dev, repo PR #149). This run re-scores the opponent in uner on the same main
test sets, beside conll as a control (at this commit; it differs from the rq6-test row where
rules changed after 29 Oct: propagation 046a10a, birth-number labels 74af0fd, c25b6c0). The final model is not re-run: its test scores are those of rq6-test, so
the two are compared by point estimate, not paired. Run on the M4 Pro CPU. No choice depends
on it: the final model was fixed on 22 Oct.

Stage: final · commit 2fc56b1758 · 2026-11-16T09:56:46+00:00 · seed 20261010, 1000 resamples · models: xlm-roberta-large-tokenizer @ c23d21b062, nametag3-multilingual-260521 @ hdl:11234/ · tool 0.7.0

## redact/test · cs · test

456 documents, 456 pages, 456 sentences or records. Gold spans: address 359, birth_number 283, date 304, email 718, id_number 46, person 2477, phone 422.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+nametag-multi | 0.563 [0.50, 0.62] | 0.599 [0.52, 0.67] | 0.580 [0.52, 0.64] | 0.591 [0.52, 0.66] | 215 / 359 |
| address | rules+nametag-multi-uner | 0.563 [0.50, 0.62] | 0.599 [0.52, 0.67] | 0.580 [0.52, 0.64] | 0.591 [0.52, 0.66] | 215 / 359 |
| birth_number | rules+nametag-multi | 0.962 [0.93, 0.99] | 0.541 [0.47, 0.61] | 0.692 [0.63, 0.75] | 0.593 [0.52, 0.66] | 153 / 283 |
| birth_number | rules+nametag-multi-uner | 0.962 [0.93, 0.99] | 0.541 [0.47, 0.61] | 0.692 [0.63, 0.75] | 0.593 [0.52, 0.66] | 153 / 283 |
| date | rules+nametag-multi | 0.990 [0.97, 1.00] | 0.625 [0.56, 0.68] | 0.766 [0.72, 0.81] | 0.675 [0.61, 0.73] | 190 / 304 |
| date | rules+nametag-multi-uner | 0.990 [0.97, 1.00] | 0.625 [0.56, 0.68] | 0.766 [0.72, 0.81] | 0.675 [0.61, 0.73] | 190 / 304 |
| email | rules+nametag-multi | 0.948 [0.92, 0.97] | 0.985 [0.97, 0.99] | 0.966 [0.95, 0.98] | 0.977 [0.97, 0.99] | 707 / 718 |
| email | rules+nametag-multi-uner | 0.948 [0.92, 0.97] | 0.985 [0.97, 0.99] | 0.966 [0.95, 0.98] | 0.977 [0.97, 0.99] | 707 / 718 |
| id_number | rules+nametag-multi | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 46 |
| id_number | rules+nametag-multi-uner | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 46 |
| person | rules+nametag-multi | 0.847 [0.81, 0.88] | 0.920 [0.89, 0.95] | 0.882 [0.85, 0.91] | 0.904 [0.88, 0.93] | 2278 / 2477 |
| person | rules+nametag-multi-uner | 0.853 [0.82, 0.89] | 0.913 [0.88, 0.94] | 0.882 [0.85, 0.91] | 0.900 [0.87, 0.92] | 2261 / 2477 |
| phone | rules+nametag-multi | 0.890 [0.85, 0.93] | 0.962 [0.94, 0.98] | 0.925 [0.90, 0.95] | 0.947 [0.93, 0.96] | 406 / 422 |
| phone | rules+nametag-multi-uner | 0.890 [0.85, 0.93] | 0.962 [0.94, 0.98] | 0.925 [0.90, 0.95] | 0.947 [0.93, 0.96] | 406 / 422 |
| any | rules+nametag-multi | 0.861 [0.84, 0.88] | 0.871 [0.85, 0.89] | 0.866 [0.85, 0.88] | 0.869 [0.85, 0.88] | 4012 / 4609 |
| any | rules+nametag-multi-uner | 0.864 [0.84, 0.89] | 0.867 [0.85, 0.89] | 0.866 [0.85, 0.88] | 0.866 [0.85, 0.88] | 3995 / 4609 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+nametag-multi | 0.361 [0.31, 0.42] | 0.384 [0.32, 0.45] | 0.372 [0.32, 0.43] | 0.380 [0.32, 0.44] | 138 / 359 |
| address | rules+nametag-multi-uner | 0.361 [0.31, 0.42] | 0.384 [0.32, 0.45] | 0.372 [0.32, 0.43] | 0.380 [0.32, 0.44] | 138 / 359 |
| birth_number | rules+nametag-multi | 0.962 [0.93, 0.99] | 0.541 [0.47, 0.61] | 0.692 [0.63, 0.75] | 0.593 [0.52, 0.66] | 153 / 283 |
| birth_number | rules+nametag-multi-uner | 0.962 [0.93, 0.99] | 0.541 [0.47, 0.61] | 0.692 [0.63, 0.75] | 0.593 [0.52, 0.66] | 153 / 283 |
| date | rules+nametag-multi | 0.990 [0.97, 1.00] | 0.625 [0.56, 0.68] | 0.766 [0.72, 0.81] | 0.675 [0.61, 0.73] | 190 / 304 |
| date | rules+nametag-multi-uner | 0.990 [0.97, 1.00] | 0.625 [0.56, 0.68] | 0.766 [0.72, 0.81] | 0.675 [0.61, 0.73] | 190 / 304 |
| email | rules+nametag-multi | 0.948 [0.92, 0.97] | 0.985 [0.97, 0.99] | 0.966 [0.95, 0.98] | 0.977 [0.97, 0.99] | 707 / 718 |
| email | rules+nametag-multi-uner | 0.948 [0.92, 0.97] | 0.985 [0.97, 0.99] | 0.966 [0.95, 0.98] | 0.977 [0.97, 0.99] | 707 / 718 |
| id_number | rules+nametag-multi | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 46 |
| id_number | rules+nametag-multi-uner | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 46 |
| person | rules+nametag-multi | 0.655 [0.61, 0.69] | 0.730 [0.69, 0.77] | 0.691 [0.65, 0.73] | 0.714 [0.67, 0.75] | 1809 / 2477 |
| person | rules+nametag-multi-uner | 0.668 [0.63, 0.71] | 0.732 [0.69, 0.77] | 0.699 [0.66, 0.73] | 0.718 [0.68, 0.75] | 1812 / 2477 |
| phone | rules+nametag-multi | 0.888 [0.85, 0.92] | 0.960 [0.94, 0.98] | 0.923 [0.90, 0.94] | 0.945 [0.93, 0.96] | 405 / 422 |
| phone | rules+nametag-multi-uner | 0.888 [0.85, 0.92] | 0.960 [0.94, 0.98] | 0.923 [0.90, 0.94] | 0.945 [0.93, 0.96] | 405 / 422 |
| any | rules+nametag-multi | 0.731 [0.70, 0.76] | 0.745 [0.72, 0.77] | 0.738 [0.71, 0.76] | 0.742 [0.72, 0.76] | 3433 / 4609 |
| any | rules+nametag-multi-uner | 0.740 [0.71, 0.76] | 0.746 [0.72, 0.77] | 0.743 [0.72, 0.76] | 0.744 [0.72, 0.77] | 3436 / 4609 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+nametag-multi | 0.463 [0.39, 0.54] | 0.426 [0.35, 0.49] | 3.5 [3.0, 4.1] | 153 / 359 |
| address | rules+nametag-multi-uner | 0.463 [0.39, 0.54] | 0.426 [0.35, 0.49] | 3.5 [3.0, 4.1] | 153 / 359 |
| birth_number | rules+nametag-multi | 0.287 [0.23, 0.35] | 0.707 [0.64, 0.77] | 0.1 [0.0, 0.2] | 200 / 283 |
| birth_number | rules+nametag-multi-uner | 0.287 [0.23, 0.35] | 0.707 [0.64, 0.77] | 0.1 [0.0, 0.2] | 200 / 283 |
| date | rules+nametag-multi | 0.328 [0.27, 0.39] | 0.674 [0.61, 0.73] | 0.0 [0.0, 0.1] | 205 / 304 |
| date | rules+nametag-multi-uner | 0.328 [0.27, 0.39] | 0.674 [0.61, 0.73] | 0.0 [0.0, 0.1] | 205 / 304 |
| email | rules+nametag-multi | 0.014 [0.01, 0.02] | 0.985 [0.97, 0.99] | 1.4 [0.8, 2.0] | 707 / 718 |
| email | rules+nametag-multi-uner | 0.014 [0.01, 0.02] | 0.985 [0.97, 0.99] | 1.4 [0.8, 2.0] | 707 / 718 |
| id_number | rules+nametag-multi | 0.959 [0.89, 1.00] | 0.043 [0.00, 0.11] | 0.0 [0.0, 0.0] | 2 / 46 |
| id_number | rules+nametag-multi-uner | 0.959 [0.89, 1.00] | 0.043 [0.00, 0.11] | 0.0 [0.0, 0.0] | 2 / 46 |
| person | rules+nametag-multi | 0.052 [0.04, 0.07] | 0.892 [0.86, 0.92] | 10.7 [8.3, 13.1] | 2209 / 2477 |
| person | rules+nametag-multi-uner | 0.055 [0.04, 0.07] | 0.885 [0.85, 0.92] | 9.5 [7.5, 11.6] | 2192 / 2477 |
| phone | rules+nametag-multi | 0.041 [0.02, 0.06] | 0.960 [0.94, 0.98] | 0.3 [0.1, 0.4] | 405 / 422 |
| phone | rules+nametag-multi-uner | 0.041 [0.02, 0.06] | 0.960 [0.94, 0.98] | 0.3 [0.1, 0.4] | 405 / 422 |
| any | rules+nametag-multi | 0.133 [0.12, 0.15] | 0.842 [0.82, 0.86] | 15.9 [13.4, 18.4] | 3881 / 4609 |
| any | rules+nametag-multi-uner | 0.134 [0.12, 0.15] | 0.838 [0.82, 0.86] | 14.8 [12.6, 17.0] | 3864 / 4609 |

### rules+nametag-multi → rules+nametag-multi-uner (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| birth_number | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | strict | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | +0.013 [+0.00, +0.02] | +0.001 [-0.00, +0.01] | +0.008 [+0.00, +0.02] | +0.004 [-0.00, +0.01] | 0.138 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | +0.009 [+0.00, +0.02] | +0.001 [-0.00, +0.00] | +0.005 [+0.00, +0.01] | +0.002 [-0.00, +0.01] | 0.132 |
| address | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| birth_number | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | partial | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | +0.006 [-0.00, +0.01] | -0.007 [-0.02, -0.00] | +0.000 [-0.01, +0.01] | -0.004 [-0.01, +0.00] | 0.322 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | +0.004 [-0.00, +0.01] | -0.004 [-0.01, -0.00] | +0.000 [-0.00, +0.00] | -0.002 [-0.01, +0.00] | 0.314 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| birth_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| date | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| id_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | +0.003 [+0.00, +0.01] | -0.007 [-0.02, +0.00] | -1.1 [-2.0, -0.5] | 0.016 |
| phone | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | +0.001 [+0.00, +0.00] | -0.004 [-0.01, +0.00] | -1.1 [-1.9, -0.5] | 0.016 |

## cnec-2.0/etest · cs · test

75 documents, 75 pages, 899 sentences or records. Gold spans: address 11, email 16, person 534, phone 25, url 1.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+nametag-multi | 0.900 [0.64, 1.00] | 0.818 [0.50, 1.00] | 0.857 [0.57, 1.00] | 0.833 [0.50, 1.00] | 9 / 11 |
| address | rules+nametag-multi-uner | 0.900 [0.64, 1.00] | 0.818 [0.50, 1.00] | 0.857 [0.57, 1.00] | 0.833 [0.50, 1.00] | 9 / 11 |
| email | rules+nametag-multi | 1.000 [1.00, 1.00] | 0.875 [0.54, 1.00] | 0.933 [0.70, 1.00] | 0.897 [0.59, 1.00] | 14 / 16 |
| email | rules+nametag-multi-uner | 1.000 [1.00, 1.00] | 0.875 [0.54, 1.00] | 0.933 [0.70, 1.00] | 0.897 [0.59, 1.00] | 14 / 16 |
| person | rules+nametag-multi | 0.964 [0.94, 0.98] | 0.867 [0.82, 0.91] | 0.913 [0.88, 0.94] | 0.885 [0.85, 0.92] | 463 / 534 |
| person | rules+nametag-multi-uner | 0.934 [0.90, 0.96] | 0.875 [0.83, 0.92] | 0.903 [0.88, 0.93] | 0.886 [0.85, 0.92] | 467 / 534 |
| phone | rules+nametag-multi | 0.957 [0.76, 1.00] | 0.880 [0.57, 1.00] | 0.917 [0.67, 1.00] | 0.894 [0.61, 1.00] | 22 / 25 |
| phone | rules+nametag-multi-uner | 0.957 [0.76, 1.00] | 0.880 [0.57, 1.00] | 0.917 [0.67, 1.00] | 0.894 [0.61, 1.00] | 22 / 25 |
| url | rules+nametag-multi | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1 / 1 |
| url | rules+nametag-multi-uner | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1 / 1 |
| any | rules+nametag-multi | 0.963 [0.94, 0.98] | 0.871 [0.82, 0.91] | 0.914 [0.88, 0.94] | 0.888 [0.85, 0.92] | 511 / 587 |
| any | rules+nametag-multi-uner | 0.936 [0.91, 0.96] | 0.877 [0.83, 0.92] | 0.906 [0.88, 0.93] | 0.888 [0.85, 0.92] | 515 / 587 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+nametag-multi | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 11 |
| address | rules+nametag-multi-uner | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 11 |
| email | rules+nametag-multi | 1.000 [1.00, 1.00] | 0.875 [0.54, 1.00] | 0.933 [0.70, 1.00] | 0.897 [0.59, 1.00] | 14 / 16 |
| email | rules+nametag-multi-uner | 1.000 [1.00, 1.00] | 0.875 [0.54, 1.00] | 0.933 [0.70, 1.00] | 0.897 [0.59, 1.00] | 14 / 16 |
| person | rules+nametag-multi | 0.870 [0.83, 0.91] | 0.803 [0.75, 0.85] | 0.835 [0.79, 0.87] | 0.816 [0.77, 0.86] | 429 / 534 |
| person | rules+nametag-multi-uner | 0.844 [0.80, 0.89] | 0.813 [0.76, 0.86] | 0.828 [0.79, 0.87] | 0.819 [0.77, 0.86] | 434 / 534 |
| phone | rules+nametag-multi | 0.913 [0.67, 1.00] | 0.840 [0.52, 1.00] | 0.875 [0.59, 0.98] | 0.854 [0.56, 0.99] | 21 / 25 |
| phone | rules+nametag-multi-uner | 0.913 [0.67, 1.00] | 0.840 [0.52, 1.00] | 0.875 [0.59, 0.98] | 0.854 [0.56, 0.99] | 21 / 25 |
| url | rules+nametag-multi | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1 / 1 |
| url | rules+nametag-multi-uner | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1 / 1 |
| any | rules+nametag-multi | 0.860 [0.82, 0.90] | 0.792 [0.74, 0.84] | 0.825 [0.79, 0.86] | 0.805 [0.76, 0.85] | 465 / 587 |
| any | rules+nametag-multi-uner | 0.836 [0.80, 0.88] | 0.801 [0.75, 0.85] | 0.818 [0.78, 0.85] | 0.808 [0.77, 0.85] | 470 / 587 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+nametag-multi | 0.647 [0.55, 0.77] | 0.000 [0.00, 0.00] | 0.3 [0.0, 0.7] | 0 / 11 |
| address | rules+nametag-multi-uner | 0.647 [0.55, 0.77] | 0.000 [0.00, 0.00] | 0.3 [0.0, 0.7] | 0 / 11 |
| email | rules+nametag-multi | 0.139 [0.00, 0.48] | 0.875 [0.54, 1.00] | 0.0 [0.0, 0.0] | 14 / 16 |
| email | rules+nametag-multi-uner | 0.139 [0.00, 0.48] | 0.875 [0.54, 1.00] | 0.0 [0.0, 0.0] | 14 / 16 |
| person | rules+nametag-multi | 0.110 [0.07, 0.15] | 0.824 [0.77, 0.87] | 1.3 [0.7, 2.2] | 440 / 534 |
| person | rules+nametag-multi-uner | 0.101 [0.07, 0.14] | 0.835 [0.78, 0.88] | 2.9 [1.7, 4.4] | 446 / 534 |
| phone | rules+nametag-multi | 0.131 [0.00, 0.40] | 0.840 [0.52, 1.00] | 0.1 [0.0, 0.3] | 21 / 25 |
| phone | rules+nametag-multi-uner | 0.131 [0.00, 0.40] | 0.840 [0.52, 1.00] | 0.1 [0.0, 0.3] | 21 / 25 |
| url | rules+nametag-multi | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 1 / 1 |
| url | rules+nametag-multi-uner | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 1 / 1 |
| any | rules+nametag-multi | 0.148 [0.11, 0.19] | 0.811 [0.76, 0.86] | 1.8 [0.9, 2.7] | 476 / 587 |
| any | rules+nametag-multi-uner | 0.141 [0.10, 0.19] | 0.821 [0.77, 0.87] | 3.4 [2.0, 5.0] | 482 / 587 |

### rules+nametag-multi → rules+nametag-multi-uner (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.026 [-0.05, -0.00] | +0.009 [-0.00, +0.03] | -0.007 [-0.02, +0.01] | +0.003 [-0.01, +0.02] | 0.766 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | -0.023 [-0.05, -0.00] | +0.009 [-0.00, +0.03] | -0.006 [-0.02, +0.01] | +0.003 [-0.01, +0.02] | 0.756 |
| address | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.030 [-0.06, -0.01] | +0.007 [-0.00, +0.02] | -0.009 [-0.02, +0.00] | +0.001 [-0.01, +0.01] | 0.922 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | -0.027 [-0.05, -0.01] | +0.007 [-0.00, +0.02] | -0.009 [-0.02, +0.00] | +0.001 [-0.01, +0.01] | 0.926 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.009 [-0.03, +0.00] | +0.011 [-0.00, +0.03] | +1.6 [+0.6, +2.9] | 0.278 |
| phone | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| url | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | -0.008 [-0.03, +0.00] | +0.010 [-0.00, +0.03] | +1.6 [+0.6, +2.9] | 0.278 |

## uner-sk-snk/test · sk · test

36 documents, 106 pages, 1061 sentences or records. Gold spans: person 539.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+nametag-multi | 0.925 [0.87, 0.96] | 0.896 [0.86, 0.93] | 0.910 [0.88, 0.94] | 0.902 [0.86, 0.93] | 483 / 539 |
| person | rules+nametag-multi-uner | 0.929 [0.88, 0.96] | 0.926 [0.89, 0.95] | 0.927 [0.89, 0.95] | 0.926 [0.89, 0.95] | 499 / 539 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+nametag-multi | 0.797 [0.74, 0.85] | 0.787 [0.73, 0.85] | 0.792 [0.74, 0.84] | 0.789 [0.74, 0.84] | 424 / 539 |
| person | rules+nametag-multi-uner | 0.803 [0.75, 0.85] | 0.816 [0.76, 0.87] | 0.810 [0.76, 0.86] | 0.814 [0.76, 0.86] | 440 / 539 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+nametag-multi | 0.093 [0.06, 0.13] | 0.803 [0.75, 0.86] | 4.8 [2.3, 8.1] | 433 / 539 |
| person | rules+nametag-multi-uner | 0.071 [0.05, 0.11] | 0.835 [0.78, 0.88] | 4.8 [2.5, 8.1] | 450 / 539 |

### rules+nametag-multi → rules+nametag-multi-uner (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | +0.006 [-0.00, +0.02] | +0.030 [+0.00, +0.06] | +0.018 [+0.00, +0.04] | +0.025 [+0.00, +0.05] | 0.042 |
| person | partial | +0.004 [-0.01, +0.01] | +0.030 [+0.00, +0.06] | +0.017 [+0.00, +0.03] | +0.025 [+0.00, +0.05] | 0.036 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| person | -0.021 [-0.04, +0.00] | +0.032 [+0.00, +0.06] | +0.0 [-0.5, +0.5] | 0.066 |
