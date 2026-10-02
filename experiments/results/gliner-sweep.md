# gliner-sweep

Reproduces the 2026-10-02 measurement behind PR #55 (docs/findings.md, *False alarms
from the name model*): GLiNER person spans before and after the "organization"
distractor and the name filter, and the threshold raised to 0.5. Development data only.

Stage: dev · commit a753245423 · 2026-10-02T18:27:47+00:00 · seed 20261002, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-multi-v2.1 @ 443d26d654 · tool 0.3.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: person 524.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | before | 0.843 [0.78, 0.89] | 0.794 [0.74, 0.84] | 0.818 [0.77, 0.85] | 0.803 [0.75, 0.84] | 416 / 524 |
| person | before, threshold 0.5 | 0.881 [0.82, 0.93] | 0.672 [0.61, 0.73] | 0.762 [0.71, 0.81] | 0.705 [0.65, 0.76] | 352 / 524 |
| person | + organization | 0.858 [0.80, 0.90] | 0.821 [0.77, 0.87] | 0.839 [0.80, 0.87] | 0.828 [0.78, 0.87] | 430 / 524 |
| person | + name filter | 0.909 [0.86, 0.94] | 0.821 [0.77, 0.87] | 0.863 [0.82, 0.90] | 0.837 [0.79, 0.88] | 430 / 524 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | before | 0.791 [0.73, 0.84] | 0.731 [0.67, 0.78] | 0.760 [0.71, 0.80] | 0.742 [0.69, 0.79] | 383 / 524 |
| person | before, threshold 0.5 | 0.843 [0.77, 0.89] | 0.635 [0.57, 0.70] | 0.725 [0.66, 0.77] | 0.668 [0.61, 0.73] | 333 / 524 |
| person | + organization | 0.803 [0.74, 0.85] | 0.754 [0.70, 0.80] | 0.778 [0.73, 0.82] | 0.763 [0.71, 0.81] | 395 / 524 |
| person | + name filter | 0.849 [0.80, 0.89] | 0.752 [0.70, 0.80] | 0.798 [0.75, 0.83] | 0.769 [0.72, 0.81] | 394 / 524 |

### before → + organization (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | +0.011 [-0.00, +0.03] | +0.023 [+0.01, +0.04] | +0.018 [+0.01, +0.03] | +0.021 [+0.01, +0.03] | 0.002 |
| person | partial | +0.015 [+0.00, +0.03] | +0.027 [+0.01, +0.04] | +0.021 [+0.01, +0.04] | +0.025 [+0.01, +0.04] | 0.000 |

### + organization → + name filter (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | +0.046 [+0.02, +0.08] | -0.002 [-0.02, +0.01] | +0.020 [+0.00, +0.04] | +0.006 [-0.01, +0.02] | 0.414 |
| person | partial | +0.052 [+0.03, +0.08] | +0.000 [+0.00, +0.00] | +0.024 [+0.01, +0.04] | +0.009 [+0.00, +0.02] | 0.000 |

## uner-sk-snk/dev+tokens · sk · dev

89 documents, 89 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | before | 0.724 [0.63, 0.81] | 0.634 [0.56, 0.70] | 0.676 [0.61, 0.73] | 0.650 [0.59, 0.71] | 175 / 276 |
| person | before, threshold 0.5 | 0.786 [0.68, 0.88] | 0.565 [0.49, 0.63] | 0.657 [0.59, 0.71] | 0.599 [0.53, 0.66] | 156 / 276 |
| person | + organization | 0.740 [0.65, 0.83] | 0.667 [0.60, 0.73] | 0.701 [0.64, 0.75] | 0.680 [0.62, 0.73] | 184 / 276 |
| person | + name filter | 0.788 [0.69, 0.87] | 0.667 [0.60, 0.73] | 0.722 [0.66, 0.77] | 0.688 [0.62, 0.74] | 184 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | before | 0.636 [0.55, 0.72] | 0.551 [0.49, 0.61] | 0.590 [0.53, 0.64] | 0.566 [0.51, 0.62] | 152 / 276 |
| person | before, threshold 0.5 | 0.709 [0.61, 0.81] | 0.504 [0.44, 0.57] | 0.589 [0.53, 0.65] | 0.535 [0.48, 0.60] | 139 / 276 |
| person | + organization | 0.642 [0.55, 0.73] | 0.573 [0.52, 0.63] | 0.605 [0.55, 0.66] | 0.585 [0.53, 0.64] | 158 / 276 |
| person | + name filter | 0.736 [0.64, 0.83] | 0.616 [0.55, 0.69] | 0.671 [0.60, 0.72] | 0.637 [0.57, 0.69] | 170 / 276 |

### before → + organization (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | +0.006 [-0.01, +0.03] | +0.022 [+0.01, +0.04] | +0.015 [-0.00, +0.04] | +0.019 [+0.00, +0.04] | 0.006 |
| person | partial | +0.016 [-0.00, +0.04] | +0.033 [+0.01, +0.06] | +0.025 [+0.01, +0.05] | +0.030 [+0.01, +0.05] | 0.004 |

### + organization → + name filter (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | +0.094 [+0.05, +0.14] | +0.043 [+0.01, +0.07] | +0.065 [+0.03, +0.10] | +0.051 [+0.02, +0.08] | 0.002 |
| person | partial | +0.048 [+0.02, +0.08] | +0.000 [+0.00, +0.00] | +0.021 [+0.01, +0.04] | +0.008 [+0.00, +0.01] | 0.000 |
