# rq6-gpu-dev

RQ6 on one GPU type, development data, three seeds each: the two final candidates,
cross-entropy and focal loss, retrained on MetaCentrum (fobos, NVIDIA L40S, --tag gpu),
against GLiNER zero-shot. Cross-entropy is also scored at 0.041, the threshold at which
a calibrated cross-entropy model reports what weight 10 reports at 0.3 and the control
focal loss was compared with on the Mac (rq6-threshold-dev). Every trained model here
comes from one kind of machine; none from the Mac is mixed in. Train the six models
first (docs/metacentrum.md).

Stage: dev · commit c2b5bb68d5 · 2026-10-15T03:09:34+00:00 · seed 20261010, 1000 resamples · models: mdeberta-v3-base-tokenizer @ a0484667b2, gliner-multi-v2.1 @ 443d26d654, gliner-cs-sk-ce-gpu @ d7ade2e1a6, gliner-cs-sk-ce-gpu-s1 @ 51e354cfff, gliner-cs-sk-ce-gpu-s2 @ 9f4ede6fbc, gliner-cs-sk-focal-gpu @ 24309ca531, gliner-cs-sk-focal-gpu-s1 @ 6f0bfadb5c, gliner-cs-sk-focal-gpu-s2 @ 969b50c212 · tool 0.6.0

## cnec-2.0/dtest · cs · dev

75 documents, 75 pages, 900 sentences or records. Gold spans: address 22, email 19, person 524, phone 37, url 4.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner | 0.651 [0.47, 0.79] | 1.000 [1.00, 1.00] | 0.788 [0.64, 0.88] | 0.903 [0.82, 0.95] | 22 / 22 |
| address | rules+gliner-cs-sk-ce-gpu | 0.829 [0.71, 0.94] | 0.909 [0.78, 1.00] | 0.867 [0.77, 0.95] | 0.892 [0.78, 0.98] | 20 / 22 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.838 [0.73, 0.94] | 0.955 [0.87, 1.00] | 0.892 [0.81, 0.97] | 0.929 [0.85, 0.99] | 21 / 22 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.818 [0.69, 0.94] | 0.864 [0.72, 1.00] | 0.840 [0.72, 0.95] | 0.854 [0.72, 0.97] | 19 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.846 [0.75, 0.94] | 1.000 [1.00, 1.00] | 0.917 [0.85, 0.97] | 0.965 [0.94, 0.99] | 22 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.805 [0.69, 0.91] | 1.000 [1.00, 1.00] | 0.892 [0.82, 0.95] | 0.954 [0.92, 0.98] | 22 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.769 [0.64, 0.91] | 0.909 [0.78, 1.00] | 0.833 [0.72, 0.94] | 0.877 [0.77, 0.97] | 20 / 22 |
| address | rules+gliner-cs-sk-focal-gpu | 0.821 [0.70, 0.94] | 1.000 [1.00, 1.00] | 0.901 [0.83, 0.97] | 0.958 [0.92, 0.99] | 22 / 22 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.780 [0.67, 0.90] | 0.955 [0.87, 1.00] | 0.859 [0.77, 0.94] | 0.914 [0.84, 0.97] | 21 / 22 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.789 [0.66, 0.91] | 0.909 [0.78, 1.00] | 0.845 [0.74, 0.93] | 0.882 [0.77, 0.97] | 20 / 22 |
| email | rules+gliner | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner | 0.911 [0.87, 0.95] | 0.815 [0.76, 0.86] | 0.860 [0.82, 0.89] | 0.833 [0.79, 0.87] | 427 / 524 |
| person | rules+gliner-cs-sk-ce-gpu | 0.912 [0.88, 0.94] | 0.943 [0.92, 0.96] | 0.927 [0.91, 0.95] | 0.936 [0.92, 0.95] | 494 / 524 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.911 [0.88, 0.94] | 0.937 [0.91, 0.96] | 0.924 [0.90, 0.94] | 0.932 [0.91, 0.95] | 491 / 524 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.918 [0.89, 0.95] | 0.939 [0.92, 0.96] | 0.928 [0.91, 0.95] | 0.935 [0.91, 0.95] | 492 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.881 [0.84, 0.92] | 0.949 [0.93, 0.97] | 0.914 [0.89, 0.94] | 0.934 [0.91, 0.95] | 497 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.862 [0.82, 0.90] | 0.945 [0.92, 0.96] | 0.901 [0.87, 0.93] | 0.927 [0.91, 0.95] | 495 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.883 [0.85, 0.92] | 0.949 [0.93, 0.97] | 0.915 [0.89, 0.94] | 0.935 [0.91, 0.95] | 497 / 524 |
| person | rules+gliner-cs-sk-focal-gpu | 0.859 [0.82, 0.90] | 0.945 [0.92, 0.96] | 0.900 [0.87, 0.92] | 0.926 [0.90, 0.94] | 495 / 524 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.865 [0.82, 0.90] | 0.945 [0.92, 0.96] | 0.903 [0.87, 0.93] | 0.928 [0.91, 0.95] | 495 / 524 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.885 [0.85, 0.92] | 0.950 [0.93, 0.97] | 0.916 [0.89, 0.94] | 0.936 [0.92, 0.95] | 498 / 524 |
| phone | rules+gliner | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner | 0.891 [0.85, 0.93] | 0.825 [0.78, 0.86] | 0.857 [0.82, 0.89] | 0.838 [0.80, 0.87] | 500 / 606 |
| any | rules+gliner-cs-sk-ce-gpu | 0.913 [0.88, 0.94] | 0.927 [0.89, 0.95] | 0.920 [0.89, 0.94] | 0.924 [0.90, 0.95] | 562 / 606 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.913 [0.88, 0.94] | 0.927 [0.89, 0.95] | 0.920 [0.89, 0.94] | 0.924 [0.89, 0.95] | 562 / 606 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.918 [0.89, 0.95] | 0.924 [0.89, 0.95] | 0.921 [0.89, 0.95] | 0.923 [0.89, 0.95] | 560 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.887 [0.85, 0.92] | 0.941 [0.91, 0.96] | 0.913 [0.89, 0.94] | 0.929 [0.90, 0.95] | 570 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.868 [0.83, 0.90] | 0.937 [0.91, 0.96] | 0.901 [0.87, 0.93] | 0.922 [0.90, 0.94] | 568 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.884 [0.85, 0.92] | 0.936 [0.90, 0.96] | 0.909 [0.88, 0.93] | 0.925 [0.89, 0.95] | 567 / 606 |
| any | rules+gliner-cs-sk-focal-gpu | 0.867 [0.83, 0.90] | 0.937 [0.91, 0.96] | 0.900 [0.87, 0.92] | 0.922 [0.90, 0.94] | 568 / 606 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.869 [0.83, 0.90] | 0.936 [0.90, 0.96] | 0.901 [0.87, 0.93] | 0.921 [0.89, 0.94] | 567 / 606 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.887 [0.85, 0.92] | 0.937 [0.90, 0.96] | 0.911 [0.89, 0.94] | 0.927 [0.90, 0.95] | 568 / 606 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner | 0.032 [0.00, 0.09] | 0.091 [0.00, 0.25] | 0.047 [0.00, 0.13] | 0.066 [0.00, 0.18] | 2 / 22 |
| address | rules+gliner-cs-sk-ce-gpu | 0.086 [0.00, 0.20] | 0.136 [0.00, 0.32] | 0.105 [0.00, 0.24] | 0.122 [0.00, 0.28] | 3 / 22 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.108 [0.02, 0.24] | 0.182 [0.04, 0.40] | 0.136 [0.03, 0.30] | 0.160 [0.03, 0.35] | 4 / 22 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.091 [0.00, 0.22] | 0.136 [0.00, 0.32] | 0.109 [0.00, 0.26] | 0.124 [0.00, 0.28] | 3 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.077 [0.00, 0.18] | 0.136 [0.00, 0.32] | 0.098 [0.00, 0.22] | 0.118 [0.00, 0.27] | 3 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.098 [0.02, 0.21] | 0.182 [0.04, 0.40] | 0.127 [0.03, 0.28] | 0.155 [0.03, 0.34] | 4 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.077 [0.00, 0.18] | 0.136 [0.00, 0.32] | 0.098 [0.00, 0.23] | 0.118 [0.00, 0.27] | 3 / 22 |
| address | rules+gliner-cs-sk-focal-gpu | 0.103 [0.02, 0.22] | 0.182 [0.04, 0.40] | 0.131 [0.03, 0.29] | 0.158 [0.03, 0.34] | 4 / 22 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.098 [0.02, 0.21] | 0.182 [0.04, 0.40] | 0.127 [0.03, 0.28] | 0.155 [0.03, 0.34] | 4 / 22 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.079 [0.00, 0.18] | 0.136 [0.00, 0.32] | 0.100 [0.00, 0.23] | 0.119 [0.00, 0.27] | 3 / 22 |
| email | rules+gliner | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19 / 19 |
| person | rules+gliner | 0.857 [0.81, 0.90] | 0.756 [0.71, 0.80] | 0.803 [0.76, 0.84] | 0.774 [0.73, 0.81] | 396 / 524 |
| person | rules+gliner-cs-sk-ce-gpu | 0.873 [0.84, 0.90] | 0.905 [0.88, 0.93] | 0.888 [0.86, 0.91] | 0.898 [0.87, 0.92] | 474 / 524 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.866 [0.83, 0.90] | 0.889 [0.86, 0.91] | 0.878 [0.85, 0.90] | 0.885 [0.86, 0.91] | 466 / 524 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.882 [0.85, 0.91] | 0.903 [0.88, 0.92] | 0.892 [0.87, 0.91] | 0.899 [0.88, 0.92] | 473 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.844 [0.81, 0.88] | 0.910 [0.89, 0.93] | 0.876 [0.85, 0.90] | 0.896 [0.87, 0.92] | 477 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.820 [0.78, 0.86] | 0.897 [0.87, 0.92] | 0.857 [0.83, 0.88] | 0.880 [0.86, 0.90] | 470 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.848 [0.81, 0.88] | 0.912 [0.89, 0.93] | 0.879 [0.85, 0.90] | 0.898 [0.88, 0.92] | 478 / 524 |
| person | rules+gliner-cs-sk-focal-gpu | 0.821 [0.78, 0.86] | 0.903 [0.88, 0.92] | 0.860 [0.83, 0.88] | 0.885 [0.86, 0.91] | 473 / 524 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.825 [0.78, 0.86] | 0.899 [0.87, 0.92] | 0.860 [0.83, 0.89] | 0.883 [0.86, 0.91] | 471 / 524 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.849 [0.81, 0.88] | 0.914 [0.89, 0.93] | 0.880 [0.85, 0.90] | 0.900 [0.88, 0.92] | 479 / 524 |
| phone | rules+gliner | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.622 [0.29, 0.90] | 0.767 [0.45, 0.95] | 0.672 [0.34, 0.91] | 23 / 37 |
| url | rules+gliner | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.667 [0.00, 1.00] | 0.556 [0.00, 1.00] | 2 / 4 |
| any | rules+gliner | 0.780 [0.72, 0.83] | 0.733 [0.68, 0.78] | 0.756 [0.70, 0.80] | 0.742 [0.69, 0.79] | 444 / 606 |
| any | rules+gliner-cs-sk-ce-gpu | 0.838 [0.80, 0.87] | 0.860 [0.82, 0.89] | 0.849 [0.81, 0.88] | 0.855 [0.82, 0.89] | 521 / 606 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.830 [0.79, 0.87] | 0.848 [0.81, 0.88] | 0.839 [0.80, 0.87] | 0.845 [0.81, 0.88] | 514 / 606 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.848 [0.81, 0.88] | 0.858 [0.82, 0.89] | 0.853 [0.82, 0.88] | 0.856 [0.82, 0.89] | 520 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.810 [0.77, 0.85] | 0.866 [0.82, 0.90] | 0.837 [0.80, 0.87] | 0.855 [0.81, 0.89] | 525 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.787 [0.74, 0.83] | 0.855 [0.81, 0.89] | 0.820 [0.78, 0.85] | 0.840 [0.80, 0.87] | 518 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.811 [0.77, 0.85] | 0.866 [0.83, 0.90] | 0.838 [0.80, 0.87] | 0.855 [0.82, 0.89] | 525 / 606 |
| any | rules+gliner-cs-sk-focal-gpu | 0.791 [0.75, 0.83] | 0.860 [0.82, 0.89] | 0.824 [0.79, 0.86] | 0.845 [0.80, 0.88] | 521 / 606 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.793 [0.75, 0.83] | 0.858 [0.81, 0.89] | 0.824 [0.79, 0.86] | 0.844 [0.80, 0.88] | 520 / 606 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.814 [0.77, 0.85] | 0.868 [0.83, 0.90] | 0.840 [0.81, 0.87] | 0.857 [0.82, 0.89] | 526 / 606 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner | 0.404 [0.29, 0.52] | 0.182 [0.04, 0.38] | 3.0 [1.7, 4.4] | 4 / 22 |
| address | rules+gliner-cs-sk-ce-gpu | 0.411 [0.26, 0.55] | 0.227 [0.06, 0.46] | 1.3 [0.4, 2.2] | 5 / 22 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.403 [0.27, 0.50] | 0.273 [0.09, 0.52] | 1.3 [0.4, 2.2] | 6 / 22 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.424 [0.29, 0.53] | 0.227 [0.06, 0.46] | 1.5 [0.4, 2.7] | 5 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.369 [0.25, 0.48] | 0.227 [0.06, 0.46] | 1.3 [0.4, 2.2] | 5 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.365 [0.26, 0.46] | 0.273 [0.09, 0.52] | 1.6 [0.6, 2.6] | 6 / 22 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.404 [0.27, 0.51] | 0.227 [0.06, 0.46] | 1.9 [0.7, 3.2] | 5 / 22 |
| address | rules+gliner-cs-sk-focal-gpu | 0.377 [0.27, 0.48] | 0.273 [0.09, 0.52] | 1.4 [0.4, 2.4] | 6 / 22 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.381 [0.26, 0.47] | 0.273 [0.09, 0.52] | 1.8 [0.7, 3.0] | 6 / 22 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.420 [0.29, 0.53] | 0.227 [0.06, 0.46] | 1.5 [0.5, 2.6] | 5 / 22 |
| email | rules+gliner | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 0.0 [0.0, 0.0] | 19 / 19 |
| person | rules+gliner | 0.152 [0.11, 0.20] | 0.800 [0.75, 0.84] | 3.8 [2.4, 5.4] | 419 / 524 |
| person | rules+gliner-cs-sk-ce-gpu | 0.043 [0.03, 0.06] | 0.918 [0.90, 0.94] | 3.7 [2.4, 5.1] | 481 / 524 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.047 [0.03, 0.06] | 0.916 [0.90, 0.94] | 4.0 [2.6, 5.3] | 480 / 524 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.047 [0.03, 0.06] | 0.914 [0.89, 0.93] | 3.4 [2.0, 4.7] | 479 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.036 [0.02, 0.05] | 0.927 [0.91, 0.95] | 5.3 [3.6, 6.9] | 486 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.038 [0.03, 0.05] | 0.926 [0.91, 0.95] | 6.4 [4.7, 8.2] | 485 / 524 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.038 [0.03, 0.05] | 0.926 [0.91, 0.94] | 5.3 [3.8, 6.7] | 485 / 524 |
| person | rules+gliner-cs-sk-focal-gpu | 0.038 [0.03, 0.05] | 0.924 [0.90, 0.94] | 6.5 [4.8, 8.2] | 484 / 524 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.038 [0.02, 0.05] | 0.926 [0.90, 0.95] | 6.1 [4.5, 7.7] | 485 / 524 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.036 [0.02, 0.05] | 0.927 [0.91, 0.95] | 5.2 [3.7, 6.7] | 486 / 524 |
| phone | rules+gliner | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu-s2 | 0.328 [0.08, 0.65] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 0.318 [0.08, 0.64] | 0.622 [0.29, 0.90] | 0.0 [0.0, 0.0] | 23 / 37 |
| url | rules+gliner | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu-s1 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| url | rules+gliner-cs-sk-focal-gpu-s2 | 0.384 [0.00, 1.00] | 0.500 [0.00, 1.00] | 0.0 [0.0, 0.0] | 2 / 4 |
| any | rules+gliner | 0.187 [0.15, 0.23] | 0.771 [0.72, 0.81] | 6.8 [4.7, 8.9] | 467 / 606 |
| any | rules+gliner-cs-sk-ce-gpu | 0.102 [0.07, 0.14] | 0.875 [0.84, 0.90] | 4.9 [3.2, 6.7] | 530 / 606 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.106 [0.07, 0.14] | 0.875 [0.84, 0.91] | 5.1 [3.3, 6.9] | 530 / 606 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.108 [0.07, 0.14] | 0.871 [0.83, 0.90] | 4.8 [2.8, 6.9] | 528 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.093 [0.06, 0.12] | 0.883 [0.85, 0.91] | 6.5 [4.4, 8.6] | 535 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.095 [0.07, 0.13] | 0.883 [0.85, 0.91] | 7.9 [5.6, 10.2] | 535 / 606 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.099 [0.07, 0.13] | 0.881 [0.84, 0.91] | 7.0 [4.6, 9.3] | 534 / 606 |
| any | rules+gliner-cs-sk-focal-gpu | 0.097 [0.07, 0.13] | 0.881 [0.84, 0.91] | 7.8 [5.7, 9.8] | 534 / 606 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.097 [0.06, 0.13] | 0.883 [0.84, 0.91] | 7.8 [5.5, 10.1] | 535 / 606 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.101 [0.07, 0.14] | 0.883 [0.84, 0.91] | 6.6 [4.6, 8.7] | 535 / 606 |

### Across seeds

Mean ± sample standard deviation over n replicates, each scored on all documents.

| type | match | system | n | P | R | F1 | F2 |
|---|---|---|---|---|---|---|---|
| address | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.095 ± 0.012 | 0.152 ± 0.026 | 0.117 ± 0.017 | 0.135 ± 0.021 |
| email | strict | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| person | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.874 ± 0.008 | 0.899 ± 0.008 | 0.886 ± 0.008 | 0.894 ± 0.008 |
| phone | strict | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 0.622 ± 0.000 | 0.767 ± 0.000 | 0.672 ± 0.000 |
| url | strict | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 0.500 ± 0.000 | 0.667 ± 0.000 | 0.556 ± 0.000 |
| any | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.839 ± 0.009 | 0.855 ± 0.006 | 0.847 ± 0.007 | 0.852 ± 0.006 |
| address | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.828 ± 0.010 | 0.909 ± 0.045 | 0.867 ± 0.026 | 0.892 ± 0.037 |
| email | partial | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| person | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.913 ± 0.004 | 0.940 ± 0.003 | 0.926 ± 0.002 | 0.934 ± 0.002 |
| phone | partial | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 0.622 ± 0.000 | 0.767 ± 0.000 | 0.672 ± 0.000 |
| url | partial | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 0.500 ± 0.000 | 0.667 ± 0.000 | 0.556 ± 0.000 |
| any | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.915 ± 0.003 | 0.926 ± 0.002 | 0.920 ± 0.001 | 0.924 ± 0.001 |
| address | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.084 ± 0.012 | 0.152 ± 0.026 | 0.108 ± 0.017 | 0.130 ± 0.021 |
| email | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.837 ± 0.015 | 0.906 ± 0.008 | 0.871 ± 0.012 | 0.892 ± 0.010 |
| phone | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 0.622 ± 0.000 | 0.767 ± 0.000 | 0.672 ± 0.000 |
| url | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 0.500 ± 0.000 | 0.667 ± 0.000 | 0.556 ± 0.000 |
| any | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.803 ± 0.014 | 0.862 ± 0.007 | 0.832 ± 0.010 | 0.850 ± 0.008 |
| address | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.807 ± 0.039 | 0.970 ± 0.052 | 0.881 ± 0.043 | 0.932 ± 0.048 |
| email | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.876 ± 0.012 | 0.947 ± 0.002 | 0.910 ± 0.007 | 0.932 ± 0.004 |
| phone | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 0.622 ± 0.000 | 0.767 ± 0.000 | 0.672 ± 0.000 |
| url | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 0.500 ± 0.000 | 0.667 ± 0.000 | 0.556 ± 0.000 |
| any | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.880 ± 0.010 | 0.938 ± 0.003 | 0.908 ± 0.006 | 0.926 ± 0.004 |
| address | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.093 ± 0.012 | 0.167 ± 0.026 | 0.119 ± 0.017 | 0.144 ± 0.022 |
| email | strict | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| person | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.832 ± 0.015 | 0.905 ± 0.008 | 0.867 ± 0.012 | 0.889 ± 0.009 |
| phone | strict | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 0.622 ± 0.000 | 0.767 ± 0.000 | 0.672 ± 0.000 |
| url | strict | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 0.500 ± 0.000 | 0.667 ± 0.000 | 0.556 ± 0.000 |
| any | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.799 ± 0.013 | 0.862 ± 0.005 | 0.829 ± 0.009 | 0.849 ± 0.007 |
| address | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.797 ± 0.021 | 0.955 ± 0.045 | 0.868 ± 0.029 | 0.918 ± 0.038 |
| email | partial | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| person | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.870 ± 0.013 | 0.947 ± 0.003 | 0.907 ± 0.009 | 0.930 ± 0.006 |
| phone | partial | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 0.622 ± 0.000 | 0.767 ± 0.000 | 0.672 ± 0.000 |
| url | partial | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 0.500 ± 0.000 | 0.667 ± 0.000 | 0.556 ± 0.000 |
| any | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.874 ± 0.011 | 0.937 ± 0.001 | 0.904 ± 0.006 | 0.924 ± 0.003 |

### Seed by seed (paired)

Candidate minus baseline per seed: mean ± sd; on how many seeds F2 rose.

| type | match | baseline → candidate | n | ΔP | ΔR | ΔF1 | ΔF2 | F2 rose |
|---|---|---|---|---|---|---|---|---|
| address | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.063 ± 0.012 | +0.061 ± 0.026 | +0.070 ± 0.017 | +0.069 ± 0.021 | 3 / 3 |
| email | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.017 ± 0.008 | +0.143 ± 0.008 | +0.083 ± 0.008 | +0.120 ± 0.008 | 3 / 3 |
| phone | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| url | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.058 ± 0.009 | +0.123 ± 0.006 | +0.091 ± 0.007 | +0.110 ± 0.006 | 3 / 3 |
| address | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.177 ± 0.010 | -0.091 ± 0.045 | +0.078 ± 0.026 | -0.012 ± 0.037 | 1 / 3 |
| email | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.002 ± 0.004 | +0.125 ± 0.003 | +0.066 ± 0.002 | +0.102 ± 0.002 | 3 / 3 |
| phone | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| url | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.024 ± 0.003 | +0.101 ± 0.002 | +0.064 ± 0.001 | +0.086 ± 0.001 | 3 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.002 ± 0.016 | +0.015 ± 0.026 | +0.003 ± 0.020 | +0.008 ± 0.023 | 1 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.042 ± 0.009 | +0.006 ± 0.007 | -0.019 ± 0.008 | -0.004 ± 0.008 | 1 / 3 |
| phone | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| url | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.040 ± 0.007 | +0.007 ± 0.006 | -0.018 ± 0.006 | -0.003 ± 0.006 | 1 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.031 ± 0.025 | +0.045 ± 0.045 | +0.002 ± 0.034 | +0.027 ± 0.041 | 2 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.044 ± 0.010 | +0.007 ± 0.005 | -0.020 ± 0.008 | -0.004 ± 0.006 | 1 / 3 |
| phone | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| url | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.041 ± 0.008 | +0.010 ± 0.003 | -0.016 ± 0.006 | -0.000 ± 0.004 | 1 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.009 ± 0.014 | +0.015 ± 0.026 | +0.011 ± 0.018 | +0.013 ± 0.022 | 2 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.005 ± 0.015 | -0.001 ± 0.006 | -0.004 ± 0.011 | -0.002 ± 0.008 | 2 / 3 |
| phone | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| url | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.004 ± 0.014 | -0.001 ± 0.005 | -0.002 ± 0.010 | -0.001 ± 0.007 | 2 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.010 ± 0.026 | -0.015 ± 0.026 | -0.012 ± 0.023 | -0.014 ± 0.023 | 1 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.006 ± 0.014 | -0.001 ± 0.003 | -0.003 ± 0.009 | -0.002 ± 0.005 | 2 / 3 |
| phone | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| url | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.006 ± 0.013 | -0.001 ± 0.003 | -0.004 ± 0.008 | -0.002 ± 0.005 | 1 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.011 ± 0.003 | +0.000 ± 0.000 | -0.009 ± 0.002 | -0.005 ± 0.001 | 0 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.037 ± 0.009 | +0.008 ± 0.002 | -0.016 ± 0.004 | -0.002 ± 0.002 | 0 / 3 |
| phone | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| url | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.036 ± 0.008 | +0.007 ± 0.001 | -0.015 ± 0.004 | -0.002 ± 0.002 | 0 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.021 ± 0.035 | +0.061 ± 0.026 | +0.014 ± 0.031 | +0.040 ± 0.028 | 3 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.038 ± 0.010 | +0.008 ± 0.002 | -0.016 ± 0.005 | -0.002 ± 0.002 | 0 / 3 |
| phone | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| url | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.035 ± 0.010 | +0.012 ± 0.002 | -0.013 ± 0.006 | +0.002 ± 0.003 | 2 / 3 |

### rules+gliner → rules+gliner-cs-sk-ce-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.054 [+0.00, +0.13] | +0.045 [+0.00, +0.15] | +0.058 [+0.00, +0.15] | +0.056 [+0.00, +0.15] | 0.082 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | +0.016 [-0.02, +0.05] | +0.149 [+0.11, +0.19] | +0.085 [+0.05, +0.12] | +0.124 [+0.09, +0.16] | 0.000 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | +0.057 [+0.02, +0.10] | +0.127 [+0.09, +0.17] | +0.093 [+0.06, +0.13] | +0.114 [+0.08, +0.15] | 0.000 |
| address | partial | +0.178 [+0.04, +0.36] | -0.091 [-0.22, +0.00] | +0.079 [-0.04, +0.24] | -0.011 [-0.12, +0.11] | 0.840 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | +0.000 [-0.02, +0.03] | +0.128 [+0.09, +0.17] | +0.067 [+0.04, +0.10] | +0.104 [+0.07, +0.14] | 0.000 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | +0.022 [+0.00, +0.05] | +0.102 [+0.07, +0.14] | +0.063 [+0.04, +0.09] | +0.087 [+0.06, +0.12] | 0.000 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | +0.008 [-0.07, +0.07] | +0.045 [+0.00, +0.15] | -1.7 [-3.0, -0.6] | 0.832 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.110 [-0.15, -0.08] | +0.118 [+0.08, +0.16] | -0.1 [-1.2, +1.0] | 0.000 |
| phone | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| url | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | -0.085 [-0.12, -0.06] | +0.104 [+0.07, +0.15] | -1.9 [-3.6, -0.3] | 0.000 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.017 [-0.03, +0.09] | +0.045 [+0.00, +0.17] | +0.026 [-0.02, +0.11] | +0.035 [-0.01, +0.14] | 0.756 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.052 [-0.07, -0.03] | -0.002 [-0.01, +0.01] | -0.029 [-0.04, -0.02] | -0.013 [-0.02, -0.00] | 0.018 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | -0.047 [-0.06, -0.03] | +0.000 [-0.01, +0.01] | -0.025 [-0.04, -0.01] | -0.010 [-0.02, -0.00] | 0.018 |
| address | partial | -0.008 [-0.05, +0.03] | +0.091 [+0.00, +0.22] | +0.034 [-0.02, +0.11] | +0.066 [-0.01, +0.17] | 0.202 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.052 [-0.07, -0.03] | +0.002 [-0.01, +0.01] | -0.027 [-0.04, -0.01] | -0.010 [-0.02, -0.00] | 0.024 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | -0.047 [-0.06, -0.03] | +0.010 [+0.00, +0.02] | -0.020 [-0.03, -0.01] | -0.002 [-0.01, +0.01] | 0.680 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.034 [-0.10, +0.04] | +0.045 [+0.00, +0.17] | +0.1 [+0.0, +0.3] | 0.328 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.005 [-0.01, +0.00] | +0.006 [-0.00, +0.01] | +2.8 [+1.8, +3.9] | 0.232 |
| phone | -0.010 [-0.04, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 0.704 |
| url | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | -0.005 [-0.02, +0.01] | +0.007 [-0.00, +0.01] | +2.8 [+1.8, +3.9] | 0.340 |

### rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.026 [-0.01, +0.10] | +0.045 [+0.00, +0.17] | +0.033 [-0.01, +0.12] | +0.039 [-0.00, +0.14] | 0.504 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.023 [-0.04, -0.01] | -0.008 [-0.02, +0.00] | -0.016 [-0.03, -0.01] | -0.011 [-0.02, -0.00] | 0.018 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | -0.020 [-0.03, -0.01] | -0.007 [-0.02, +0.00] | -0.014 [-0.02, -0.01] | -0.009 [-0.02, -0.00] | 0.000 |
| address | partial | -0.026 [-0.07, +0.00] | +0.000 [+0.00, +0.00] | -0.015 [-0.04, +0.00] | -0.007 [-0.02, +0.00] | 0.256 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.022 [-0.04, -0.01] | -0.004 [-0.01, +0.00] | -0.014 [-0.02, -0.00] | -0.008 [-0.02, -0.00] | 0.024 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | -0.021 [-0.04, -0.01] | -0.003 [-0.01, +0.00] | -0.013 [-0.02, -0.00] | -0.007 [-0.01, -0.00] | 0.000 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | +0.009 [-0.02, +0.05] | +0.045 [+0.00, +0.17] | +0.1 [+0.0, +0.3] | 0.746 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | +0.002 [-0.00, +0.01] | -0.004 [-0.01, +0.00] | +1.3 [+0.5, +2.2] | 0.594 |
| phone | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| url | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | +0.004 [-0.00, +0.01] | -0.002 [-0.01, +0.00] | +1.3 [+0.5, +2.1] | 0.216 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | -0.009 [-0.04, +0.00] | +0.000 [+0.00, +0.00] | -0.007 [-0.03, +0.00] | -0.004 [-0.01, +0.00] | 0.156 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.029 [-0.04, -0.01] | +0.006 [+0.00, +0.01] | -0.012 [-0.02, -0.00] | -0.002 [-0.01, +0.01] | 0.574 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | -0.027 [-0.04, -0.02] | +0.007 [+0.00, +0.01] | -0.011 [-0.02, -0.00] | -0.001 [-0.01, +0.01] | 0.758 |
| address | partial | +0.018 [+0.00, +0.05] | +0.091 [+0.00, +0.22] | +0.050 [+0.00, +0.13] | +0.073 [+0.00, +0.18] | 0.080 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.030 [-0.04, -0.02] | +0.006 [+0.00, +0.01] | -0.013 [-0.02, -0.00] | -0.002 [-0.01, +0.00] | 0.526 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| url | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | -0.026 [-0.04, -0.01] | +0.013 [+0.00, +0.02] | -0.007 [-0.02, +0.00] | +0.005 [-0.00, +0.01] | 0.246 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.043 [-0.09, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.2] | 0.078 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.007 [-0.01, -0.00] | +0.009 [+0.00, +0.02] | +1.5 [+0.8, +2.3] | 0.016 |
| phone | -0.010 [-0.04, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 0.704 |
| url | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | -0.009 [-0.02, -0.00] | +0.008 [+0.00, +0.02] | +1.6 [+0.8, +2.3] | 0.004 |

## uner-sk-snk/dev · sk · dev

36 documents, 106 pages, 1060 sentences or records. Gold spans: person 276.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner | 0.829 [0.73, 0.91] | 0.674 [0.60, 0.75] | 0.743 [0.67, 0.81] | 0.700 [0.63, 0.77] | 186 / 276 |
| person | rules+gliner-cs-sk-ce-gpu | 0.859 [0.77, 0.94] | 0.913 [0.87, 0.95] | 0.885 [0.83, 0.93] | 0.902 [0.86, 0.93] | 252 / 276 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.841 [0.75, 0.92] | 0.927 [0.89, 0.96] | 0.882 [0.83, 0.93] | 0.909 [0.87, 0.94] | 256 / 276 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.845 [0.76, 0.92] | 0.909 [0.86, 0.95] | 0.876 [0.82, 0.92] | 0.896 [0.85, 0.93] | 251 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.826 [0.74, 0.90] | 0.935 [0.90, 0.97] | 0.877 [0.83, 0.92] | 0.911 [0.87, 0.94] | 258 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.823 [0.74, 0.90] | 0.949 [0.92, 0.98] | 0.881 [0.83, 0.93] | 0.921 [0.89, 0.95] | 262 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.819 [0.73, 0.90] | 0.938 [0.90, 0.97] | 0.875 [0.82, 0.92] | 0.912 [0.87, 0.95] | 259 / 276 |
| person | rules+gliner-cs-sk-focal-gpu | 0.821 [0.74, 0.89] | 0.953 [0.92, 0.98] | 0.882 [0.83, 0.92] | 0.923 [0.89, 0.95] | 263 / 276 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.811 [0.73, 0.89] | 0.957 [0.92, 0.98] | 0.878 [0.82, 0.92] | 0.923 [0.89, 0.95] | 264 / 276 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.832 [0.75, 0.90] | 0.938 [0.90, 0.97] | 0.882 [0.83, 0.93] | 0.915 [0.88, 0.95] | 259 / 276 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| person | rules+gliner | 0.770 [0.68, 0.86] | 0.620 [0.54, 0.70] | 0.687 [0.62, 0.75] | 0.645 [0.57, 0.72] | 171 / 276 |
| person | rules+gliner-cs-sk-ce-gpu | 0.828 [0.74, 0.91] | 0.873 [0.83, 0.91] | 0.850 [0.80, 0.90] | 0.864 [0.82, 0.90] | 241 / 276 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.811 [0.73, 0.89] | 0.888 [0.85, 0.93] | 0.848 [0.79, 0.90] | 0.871 [0.83, 0.91] | 245 / 276 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.811 [0.73, 0.89] | 0.870 [0.81, 0.92] | 0.839 [0.78, 0.89] | 0.857 [0.81, 0.91] | 240 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.797 [0.72, 0.87] | 0.895 [0.85, 0.94] | 0.843 [0.79, 0.89] | 0.873 [0.83, 0.91] | 247 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.794 [0.71, 0.87] | 0.909 [0.86, 0.95] | 0.848 [0.79, 0.90] | 0.884 [0.84, 0.92] | 251 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.787 [0.71, 0.86] | 0.899 [0.84, 0.95] | 0.839 [0.78, 0.89] | 0.874 [0.82, 0.92] | 248 / 276 |
| person | rules+gliner-cs-sk-focal-gpu | 0.792 [0.71, 0.87] | 0.913 [0.87, 0.95] | 0.849 [0.80, 0.89] | 0.886 [0.85, 0.92] | 252 / 276 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.783 [0.70, 0.86] | 0.917 [0.88, 0.95] | 0.845 [0.79, 0.89] | 0.886 [0.85, 0.92] | 253 / 276 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.796 [0.72, 0.87] | 0.891 [0.84, 0.94] | 0.841 [0.79, 0.89] | 0.871 [0.82, 0.92] | 246 / 276 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| person | rules+gliner | 0.278 [0.20, 0.35] | 0.656 [0.57, 0.74] | 5.3 [2.6, 8.3] | 181 / 276 |
| person | rules+gliner-cs-sk-ce-gpu | 0.071 [0.04, 0.10] | 0.895 [0.85, 0.94] | 5.4 [2.2, 9.0] | 247 / 276 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.062 [0.03, 0.09] | 0.909 [0.86, 0.95] | 5.8 [2.7, 9.5] | 251 / 276 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.077 [0.04, 0.11] | 0.891 [0.84, 0.94] | 5.7 [2.6, 9.3] | 246 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.051 [0.03, 0.08] | 0.917 [0.87, 0.96] | 6.8 [3.6, 10.5] | 253 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.042 [0.02, 0.07] | 0.931 [0.89, 0.97] | 6.9 [3.5, 10.8] | 257 / 276 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.052 [0.02, 0.08] | 0.920 [0.87, 0.97] | 7.4 [4.0, 11.3] | 254 / 276 |
| person | rules+gliner-cs-sk-focal-gpu | 0.036 [0.02, 0.05] | 0.935 [0.89, 0.97] | 7.3 [3.9, 11.1] | 258 / 276 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.037 [0.02, 0.06] | 0.938 [0.90, 0.97] | 7.9 [4.5, 11.7] | 259 / 276 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.052 [0.02, 0.08] | 0.920 [0.87, 0.97] | 6.5 [3.4, 10.1] | 254 / 276 |

### Across seeds

Mean ± sample standard deviation over n replicates, each scored on all documents.

| type | match | system | n | P | R | F1 | F2 |
|---|---|---|---|---|---|---|---|
| person | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.817 ± 0.010 | 0.877 ± 0.010 | 0.846 ± 0.006 | 0.864 ± 0.007 |
| person | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.848 ± 0.010 | 0.917 ± 0.010 | 0.881 ± 0.005 | 0.902 ± 0.007 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.793 ± 0.005 | 0.901 ± 0.008 | 0.843 ± 0.004 | 0.877 ± 0.006 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.823 ± 0.003 | 0.941 ± 0.008 | 0.878 ± 0.003 | 0.914 ± 0.006 |
| person | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.791 ± 0.007 | 0.907 ± 0.014 | 0.845 ± 0.004 | 0.881 ± 0.009 |
| person | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.821 ± 0.010 | 0.949 ± 0.010 | 0.881 ± 0.002 | 0.920 ± 0.005 |

### Seed by seed (paired)

Candidate minus baseline per seed: mean ± sd; on how many seeds F2 rose.

| type | match | baseline → candidate | n | ΔP | ΔR | ΔF1 | ΔF2 | F2 rose |
|---|---|---|---|---|---|---|---|---|
| person | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.046 ± 0.010 | +0.257 ± 0.010 | +0.159 ± 0.006 | +0.219 ± 0.007 | 3 / 3 |
| person | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.019 ± 0.010 | +0.243 ± 0.010 | +0.138 ± 0.005 | +0.202 ± 0.007 | 3 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.026 ± 0.011 | +0.030 ± 0.009 | -0.001 ± 0.003 | +0.017 ± 0.005 | 3 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.027 ± 0.013 | +0.033 ± 0.006 | -0.001 ± 0.006 | +0.018 ± 0.004 | 3 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.002 ± 0.010 | +0.006 ± 0.013 | +0.001 ± 0.004 | +0.004 ± 0.008 | 2 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.001 ± 0.013 | +0.008 ± 0.009 | +0.003 ± 0.006 | +0.006 ± 0.006 | 3 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.024 ± 0.007 | +0.024 ± 0.004 | -0.002 ± 0.004 | +0.013 ± 0.004 | 3 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.026 ± 0.008 | +0.024 ± 0.004 | -0.003 ± 0.004 | +0.012 ± 0.004 | 3 / 3 |

### rules+gliner → rules+gliner-cs-sk-ce-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | +0.058 [+0.01, +0.10] | +0.254 [+0.18, +0.32] | +0.163 [+0.11, +0.22] | +0.219 [+0.15, +0.28] | 0.000 |
| person | partial | +0.030 [-0.01, +0.07] | +0.239 [+0.15, +0.31] | +0.142 [+0.09, +0.20] | +0.202 [+0.13, +0.27] | 0.000 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| person | -0.207 [-0.28, -0.13] | +0.239 [+0.15, +0.31] | +0.1 [-1.4, +1.4] | 0.000 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | -0.036 [-0.07, -0.01] | +0.040 [+0.02, +0.06] | -0.002 [-0.02, +0.02] | +0.022 [+0.00, +0.04] | 0.018 |
| person | partial | -0.038 [-0.07, -0.01] | +0.040 [+0.02, +0.06] | -0.003 [-0.03, +0.02] | +0.021 [+0.00, +0.04] | 0.026 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| person | -0.035 [-0.06, -0.02] | +0.040 [+0.02, +0.06] | +1.9 [+0.7, +3.8] | 0.000 |

### rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | -0.004 [-0.02, +0.01] | +0.018 [+0.00, +0.04] | +0.005 [-0.01, +0.02] | +0.013 [-0.00, +0.03] | 0.052 |
| person | partial | -0.005 [-0.02, +0.01] | +0.018 [+0.00, +0.04] | +0.005 [-0.01, +0.02] | +0.012 [-0.00, +0.03] | 0.056 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| person | -0.015 [-0.03, -0.00] | +0.018 [+0.00, +0.04] | +0.5 [-0.2, +1.3] | 0.020 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| person | strict | -0.031 [-0.07, -0.01] | +0.022 [+0.01, +0.04] | -0.007 [-0.03, +0.01] | +0.010 [-0.00, +0.02] | 0.168 |
| person | partial | -0.033 [-0.07, -0.01] | +0.022 [+0.01, +0.04] | -0.008 [-0.03, +0.01] | +0.009 [-0.01, +0.02] | 0.212 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| person | -0.021 [-0.04, -0.01] | +0.022 [+0.01, +0.04] | +1.4 [+0.4, +2.9] | 0.002 |

## redact/sample · cs · dev

40 documents, 40 pages, 40 sentences or records. Gold spans: address 27, birth_number 20, date 29, email 61, id_number 5, person 219, phone 27.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner | 0.495 [0.31, 0.68] | 1.000 [1.00, 1.00] | 0.662 [0.48, 0.81] | 0.830 [0.70, 0.91] | 27 / 27 |
| address | rules+gliner-cs-sk-ce-gpu | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.538 [0.38, 0.70] | 1.000 [1.00, 1.00] | 0.700 [0.55, 0.82] | 0.854 [0.76, 0.92] | 27 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.538 [0.38, 0.70] | 1.000 [1.00, 1.00] | 0.700 [0.55, 0.82] | 0.854 [0.76, 0.92] | 27 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.518 [0.37, 0.67] | 1.000 [1.00, 1.00] | 0.683 [0.54, 0.80] | 0.843 [0.75, 0.91] | 27 / 27 |
| address | rules+gliner-cs-sk-focal-gpu | 0.549 [0.40, 0.71] | 1.000 [1.00, 1.00] | 0.709 [0.57, 0.83] | 0.859 [0.77, 0.92] | 27 / 27 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.528 [0.38, 0.68] | 1.000 [1.00, 1.00] | 0.691 [0.55, 0.81] | 0.849 [0.75, 0.92] | 27 / 27 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.509 [0.37, 0.66] | 1.000 [1.00, 1.00] | 0.675 [0.54, 0.79] | 0.838 [0.75, 0.91] | 27 / 27 |
| birth_number | rules+gliner | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner | 0.649 [0.50, 0.82] | 0.918 [0.87, 0.95] | 0.760 [0.64, 0.88] | 0.848 [0.77, 0.91] | 201 / 219 |
| person | rules+gliner-cs-sk-ce-gpu | 0.790 [0.63, 0.95] | 0.931 [0.82, 1.00] | 0.855 [0.74, 0.96] | 0.899 [0.80, 0.98] | 204 / 219 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.817 [0.65, 0.97] | 0.995 [0.99, 1.00] | 0.897 [0.78, 0.98] | 0.954 [0.90, 0.99] | 218 / 219 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.814 [0.65, 0.96] | 0.995 [0.98, 1.00] | 0.896 [0.79, 0.98] | 0.953 [0.90, 0.99] | 218 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.798 [0.64, 0.95] | 0.995 [0.99, 1.00] | 0.886 [0.78, 0.97] | 0.949 [0.89, 0.99] | 218 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.801 [0.64, 0.95] | 0.995 [0.99, 1.00] | 0.888 [0.78, 0.97] | 0.950 [0.89, 0.99] | 218 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.811 [0.65, 0.96] | 0.995 [0.98, 1.00] | 0.894 [0.78, 0.98] | 0.952 [0.90, 0.99] | 218 / 219 |
| person | rules+gliner-cs-sk-focal-gpu | 0.776 [0.63, 0.92] | 0.995 [0.99, 1.00] | 0.872 [0.77, 0.96] | 0.942 [0.89, 0.98] | 218 / 219 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.810 [0.65, 0.96] | 0.991 [0.98, 1.00] | 0.891 [0.78, 0.98] | 0.949 [0.89, 0.99] | 217 / 219 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.764 [0.61, 0.93] | 0.995 [0.99, 1.00] | 0.864 [0.75, 0.97] | 0.939 [0.88, 0.98] | 218 / 219 |
| phone | rules+gliner | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu-s2 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner | 0.702 [0.61, 0.81] | 0.861 [0.81, 0.90] | 0.774 [0.71, 0.83] | 0.824 [0.78, 0.87] | 334 / 388 |
| any | rules+gliner-cs-sk-ce-gpu | 0.801 [0.69, 0.90] | 0.871 [0.81, 0.93] | 0.835 [0.76, 0.89] | 0.856 [0.80, 0.91] | 338 / 388 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.817 [0.71, 0.91] | 0.907 [0.86, 0.95] | 0.860 [0.79, 0.91] | 0.888 [0.84, 0.93] | 352 / 388 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.815 [0.71, 0.91] | 0.905 [0.86, 0.94] | 0.858 [0.79, 0.91] | 0.885 [0.84, 0.92] | 351 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.804 [0.70, 0.89] | 0.907 [0.86, 0.95] | 0.852 [0.78, 0.91] | 0.884 [0.84, 0.92] | 352 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.808 [0.70, 0.90] | 0.907 [0.86, 0.95] | 0.855 [0.79, 0.91] | 0.885 [0.84, 0.92] | 352 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.807 [0.70, 0.90] | 0.905 [0.86, 0.94] | 0.853 [0.78, 0.91] | 0.883 [0.84, 0.92] | 351 / 388 |
| any | rules+gliner-cs-sk-focal-gpu | 0.796 [0.69, 0.89] | 0.907 [0.86, 0.95] | 0.848 [0.78, 0.90] | 0.882 [0.84, 0.92] | 352 / 388 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.809 [0.70, 0.90] | 0.905 [0.86, 0.94] | 0.854 [0.79, 0.91] | 0.884 [0.84, 0.92] | 351 / 388 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.783 [0.68, 0.88] | 0.907 [0.86, 0.95] | 0.841 [0.77, 0.90] | 0.879 [0.84, 0.91] | 352 / 388 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner | 0.084 [0.04, 0.17] | 0.296 [0.14, 0.50] | 0.131 [0.06, 0.24] | 0.197 [0.09, 0.35] | 8 / 27 |
| address | rules+gliner-cs-sk-ce-gpu | 0.431 [0.29, 0.59] | 0.815 [0.64, 0.96] | 0.564 [0.41, 0.71] | 0.692 [0.52, 0.83] | 22 / 27 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.431 [0.29, 0.59] | 0.815 [0.64, 0.96] | 0.564 [0.41, 0.71] | 0.692 [0.52, 0.83] | 22 / 27 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.471 [0.32, 0.63] | 0.889 [0.72, 1.00] | 0.615 [0.46, 0.76] | 0.755 [0.59, 0.88] | 24 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.423 [0.28, 0.59] | 0.815 [0.64, 0.96] | 0.557 [0.39, 0.71] | 0.688 [0.52, 0.82] | 22 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.442 [0.29, 0.62] | 0.852 [0.69, 0.97] | 0.582 [0.42, 0.74] | 0.719 [0.56, 0.85] | 23 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.444 [0.30, 0.60] | 0.889 [0.72, 1.00] | 0.593 [0.44, 0.74] | 0.741 [0.58, 0.87] | 24 / 27 |
| address | rules+gliner-cs-sk-focal-gpu | 0.451 [0.30, 0.62] | 0.852 [0.69, 0.97] | 0.590 [0.43, 0.75] | 0.723 [0.56, 0.85] | 23 / 27 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.434 [0.29, 0.60] | 0.852 [0.69, 0.97] | 0.575 [0.41, 0.74] | 0.714 [0.55, 0.85] | 23 / 27 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.418 [0.28, 0.58] | 0.852 [0.69, 0.97] | 0.561 [0.40, 0.72] | 0.706 [0.55, 0.84] | 23 / 27 |
| birth_number | rules+gliner | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.050 [0.00, 0.16] | 0.095 [0.00, 0.27] | 0.062 [0.00, 0.19] | 1 / 20 |
| date | rules+gliner | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.552 [0.28, 0.82] | 0.711 [0.44, 0.90] | 0.606 [0.33, 0.85] | 16 / 29 |
| email | rules+gliner | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.953 [0.84, 1.00] | 1.000 [1.00, 1.00] | 0.976 [0.91, 1.00] | 0.990 [0.96, 1.00] | 61 / 61 |
| id_number | rules+gliner | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu-s1 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu-s2 | – | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0 / 5 |
| person | rules+gliner | 0.449 [0.32, 0.62] | 0.607 [0.48, 0.73] | 0.516 [0.39, 0.67] | 0.567 [0.45, 0.70] | 133 / 219 |
| person | rules+gliner-cs-sk-ce-gpu | 0.637 [0.48, 0.80] | 0.722 [0.62, 0.83] | 0.677 [0.56, 0.79] | 0.703 [0.61, 0.81] | 158 / 219 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.595 [0.45, 0.77] | 0.699 [0.57, 0.82] | 0.643 [0.51, 0.78] | 0.675 [0.56, 0.80] | 153 / 219 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.597 [0.45, 0.77] | 0.703 [0.58, 0.83] | 0.646 [0.51, 0.79] | 0.679 [0.56, 0.80] | 154 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.601 [0.46, 0.75] | 0.722 [0.62, 0.83] | 0.656 [0.54, 0.78] | 0.694 [0.59, 0.81] | 158 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.584 [0.44, 0.75] | 0.699 [0.57, 0.82] | 0.636 [0.50, 0.78] | 0.672 [0.55, 0.80] | 153 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.595 [0.45, 0.77] | 0.703 [0.58, 0.83] | 0.644 [0.51, 0.79] | 0.678 [0.56, 0.80] | 154 / 219 |
| person | rules+gliner-cs-sk-focal-gpu | 0.581 [0.44, 0.74] | 0.722 [0.61, 0.84] | 0.644 [0.52, 0.78] | 0.688 [0.57, 0.80] | 158 / 219 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.601 [0.45, 0.77] | 0.708 [0.60, 0.82] | 0.650 [0.53, 0.79] | 0.683 [0.57, 0.80] | 155 / 219 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.556 [0.40, 0.75] | 0.699 [0.57, 0.82] | 0.619 [0.49, 0.78] | 0.665 [0.54, 0.79] | 153 / 219 |
| phone | rules+gliner | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu-s2 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 0.812 [0.65, 0.96] | 0.963 [0.88, 1.00] | 0.881 [0.76, 0.98] | 0.929 [0.84, 0.99] | 26 / 27 |
| any | rules+gliner | 0.490 [0.40, 0.60] | 0.637 [0.56, 0.72] | 0.554 [0.48, 0.64] | 0.601 [0.53, 0.68] | 247 / 388 |
| any | rules+gliner-cs-sk-ce-gpu | 0.694 [0.59, 0.79] | 0.737 [0.68, 0.80] | 0.715 [0.64, 0.78] | 0.728 [0.68, 0.79] | 286 / 388 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.667 [0.57, 0.78] | 0.724 [0.66, 0.79] | 0.695 [0.62, 0.77] | 0.712 [0.65, 0.78] | 281 / 388 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.673 [0.57, 0.78] | 0.732 [0.66, 0.80] | 0.701 [0.62, 0.78] | 0.719 [0.65, 0.79] | 284 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.668 [0.57, 0.77] | 0.737 [0.68, 0.80] | 0.701 [0.63, 0.77] | 0.722 [0.67, 0.78] | 286 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.660 [0.56, 0.77] | 0.727 [0.66, 0.80] | 0.692 [0.61, 0.78] | 0.713 [0.64, 0.79] | 282 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.667 [0.57, 0.78] | 0.732 [0.66, 0.80] | 0.698 [0.62, 0.78] | 0.718 [0.65, 0.79] | 284 / 388 |
| any | rules+gliner-cs-sk-focal-gpu | 0.658 [0.56, 0.76] | 0.740 [0.68, 0.80] | 0.697 [0.62, 0.77] | 0.722 [0.66, 0.79] | 287 / 388 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.670 [0.57, 0.78] | 0.732 [0.67, 0.80] | 0.700 [0.63, 0.78] | 0.719 [0.66, 0.79] | 284 / 388 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.637 [0.53, 0.77] | 0.727 [0.66, 0.80] | 0.679 [0.59, 0.77] | 0.707 [0.64, 0.78] | 282 / 388 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner | 0.117 [0.04, 0.19] | 0.444 [0.25, 0.68] | 8.4 [4.1, 13.7] | 12 / 27 |
| address | rules+gliner-cs-sk-ce-gpu | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.1 [3.0, 10.0] | 26 / 27 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.1 [3.0, 10.0] | 26 / 27 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.1 [3.0, 9.9] | 27 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.021 [0.00, 0.07] | 0.963 [0.88, 1.00] | 6.7 [3.0, 11.4] | 26 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.7 [3.0, 11.4] | 27 / 27 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.8 [3.1, 11.6] | 27 / 27 |
| address | rules+gliner-cs-sk-focal-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.1 [3.0, 10.0] | 27 / 27 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 6.8 [3.1, 11.5] | 27 / 27 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 7.1 [3.4, 11.8] | 27 / 27 |
| birth_number | rules+gliner | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s1 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu-s2 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s1 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| birth_number | rules+gliner-cs-sk-focal-gpu-s2 | 0.572 [0.34, 0.83] | 0.450 [0.19, 0.67] | 0.0 [0.0, 0.0] | 9 / 20 |
| date | rules+gliner | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu-s1 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu-s2 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu-s1 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| date | rules+gliner-cs-sk-focal-gpu-s2 | 0.462 [0.20, 0.72] | 0.552 [0.28, 0.82] | 0.0 [0.0, 0.0] | 16 / 29 |
| email | rules+gliner | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.000 [0.00, 0.00] | 1.000 [1.00, 1.00] | 1.0 [0.0, 3.3] | 61 / 61 |
| id_number | rules+gliner | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu-s1 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| id_number | rules+gliner-cs-sk-focal-gpu-s2 | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0 / 5 |
| person | rules+gliner | 0.052 [0.03, 0.08] | 0.904 [0.86, 0.94] | 19.5 [10.2, 29.3] | 198 / 219 |
| person | rules+gliner-cs-sk-ce-gpu | 0.051 [0.00, 0.13] | 0.918 [0.80, 0.99] | 10.1 [5.3, 16.8] | 201 / 219 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.008 [0.00, 0.02] | 0.982 [0.96, 1.00] | 11.1 [5.8, 18.0] | 215 / 219 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.009 [0.00, 0.02] | 0.982 [0.96, 1.00] | 11.0 [5.8, 17.8] | 215 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.008 [0.00, 0.02] | 0.982 [0.96, 1.00] | 11.4 [6.1, 18.3] | 215 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.008 [0.00, 0.02] | 0.982 [0.96, 1.00] | 11.5 [6.1, 18.5] | 215 / 219 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.009 [0.00, 0.02] | 0.982 [0.96, 1.00] | 11.2 [5.8, 18.1] | 215 / 219 |
| person | rules+gliner-cs-sk-focal-gpu | 0.008 [0.00, 0.02] | 0.977 [0.95, 1.00] | 11.9 [6.4, 18.6] | 214 / 219 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.009 [0.00, 0.02] | 0.982 [0.96, 1.00] | 11.1 [5.7, 18.0] | 215 / 219 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.008 [0.00, 0.02] | 0.982 [0.96, 1.00] | 13.9 [6.3, 22.8] | 215 / 219 |
| phone | rules+gliner | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu-s2 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu-s1 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| phone | rules+gliner-cs-sk-focal-gpu-s2 | 0.035 [0.00, 0.11] | 0.963 [0.88, 1.00] | 0.7 [0.0, 2.1] | 26 / 27 |
| any | rules+gliner | 0.097 [0.06, 0.14] | 0.830 [0.76, 0.88] | 29.6 [19.9, 39.2] | 322 / 388 |
| any | rules+gliner-cs-sk-ce-gpu | 0.083 [0.05, 0.12] | 0.874 [0.81, 0.93] | 18.0 [11.9, 25.9] | 339 / 388 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.065 [0.04, 0.10] | 0.910 [0.86, 0.95] | 19.0 [12.3, 26.8] | 353 / 388 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.063 [0.03, 0.10] | 0.912 [0.86, 0.95] | 18.9 [12.2, 26.6] | 354 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.065 [0.04, 0.10] | 0.910 [0.86, 0.95] | 19.9 [12.9, 28.0] | 353 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 20.0 [12.7, 28.1] | 354 / 388 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.063 [0.03, 0.10] | 0.912 [0.86, 0.95] | 19.8 [12.6, 28.0] | 354 / 388 |
| any | rules+gliner-cs-sk-focal-gpu | 0.062 [0.03, 0.10] | 0.910 [0.86, 0.95] | 19.7 [13.0, 27.3] | 353 / 388 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.063 [0.03, 0.10] | 0.912 [0.86, 0.95] | 19.6 [12.5, 27.5] | 354 / 388 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.062 [0.03, 0.10] | 0.912 [0.86, 0.95] | 22.8 [13.5, 32.4] | 354 / 388 |

### Across seeds

Mean ± sample standard deviation over n replicates, each scored on all documents.

| type | match | system | n | P | R | F1 | F2 |
|---|---|---|---|---|---|---|---|
| address | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.444 ± 0.023 | 0.840 ± 0.043 | 0.581 ± 0.030 | 0.713 ± 0.036 |
| birth_number | strict | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 0.050 ± 0.000 | 0.095 ± 0.000 | 0.062 ± 0.000 |
| date | strict | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 0.552 ± 0.000 | 0.711 ± 0.000 | 0.606 ± 0.000 |
| email | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.953 ± 0.000 | 1.000 ± 0.000 | 0.976 ± 0.000 | 0.990 ± 0.000 |
| id_number | strict | rules+gliner-cs-sk-ce-gpu | 3 | – | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| person | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.610 ± 0.024 | 0.708 ± 0.012 | 0.655 ± 0.019 | 0.686 ± 0.015 |
| phone | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.812 ± 0.000 | 0.963 ± 0.000 | 0.881 ± 0.000 | 0.929 ± 0.000 |
| any | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.678 ± 0.014 | 0.731 ± 0.006 | 0.704 ± 0.010 | 0.720 ± 0.008 |
| address | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.549 ± 0.000 | 1.000 ± 0.000 | 0.709 ± 0.000 | 0.859 ± 0.000 |
| birth_number | partial | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 0.050 ± 0.000 | 0.095 ± 0.000 | 0.062 ± 0.000 |
| date | partial | rules+gliner-cs-sk-ce-gpu | 3 | 1.000 ± 0.000 | 0.552 ± 0.000 | 0.711 ± 0.000 | 0.606 ± 0.000 |
| email | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.953 ± 0.000 | 1.000 ± 0.000 | 0.976 ± 0.000 | 0.990 ± 0.000 |
| id_number | partial | rules+gliner-cs-sk-ce-gpu | 3 | – | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| person | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.807 ± 0.015 | 0.974 ± 0.037 | 0.883 ± 0.024 | 0.935 ± 0.031 |
| phone | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.812 ± 0.000 | 0.963 ± 0.000 | 0.881 ± 0.000 | 0.929 ± 0.000 |
| any | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.811 ± 0.009 | 0.894 ± 0.020 | 0.851 ± 0.014 | 0.876 ± 0.018 |
| address | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.437 ± 0.012 | 0.852 ± 0.037 | 0.577 ± 0.018 | 0.716 ± 0.027 |
| birth_number | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 0.050 ± 0.000 | 0.095 ± 0.000 | 0.062 ± 0.000 |
| date | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 0.552 ± 0.000 | 0.711 ± 0.000 | 0.606 ± 0.000 |
| email | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.953 ± 0.000 | 1.000 ± 0.000 | 0.976 ± 0.000 | 0.990 ± 0.000 |
| id_number | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | – | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.593 ± 0.008 | 0.708 ± 0.012 | 0.645 ± 0.010 | 0.681 ± 0.011 |
| phone | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.812 ± 0.000 | 0.963 ± 0.000 | 0.881 ± 0.000 | 0.929 ± 0.000 |
| any | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.665 ± 0.004 | 0.732 ± 0.005 | 0.697 ± 0.005 | 0.718 ± 0.005 |
| address | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.532 ± 0.012 | 1.000 ± 0.000 | 0.694 ± 0.010 | 0.850 ± 0.006 |
| birth_number | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 0.050 ± 0.000 | 0.095 ± 0.000 | 0.062 ± 0.000 |
| date | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 1.000 ± 0.000 | 0.552 ± 0.000 | 0.711 ± 0.000 | 0.606 ± 0.000 |
| email | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.953 ± 0.000 | 1.000 ± 0.000 | 0.976 ± 0.000 | 0.990 ± 0.000 |
| id_number | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | – | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.804 ± 0.006 | 0.995 ± 0.000 | 0.889 ± 0.004 | 0.950 ± 0.002 |
| phone | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.812 ± 0.000 | 0.963 ± 0.000 | 0.881 ± 0.000 | 0.929 ± 0.000 |
| any | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.806 ± 0.002 | 0.906 ± 0.002 | 0.853 ± 0.001 | 0.884 ± 0.001 |
| address | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.434 ± 0.016 | 0.852 ± 0.000 | 0.575 ± 0.014 | 0.714 ± 0.009 |
| birth_number | strict | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 0.050 ± 0.000 | 0.095 ± 0.000 | 0.062 ± 0.000 |
| date | strict | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 0.552 ± 0.000 | 0.711 ± 0.000 | 0.606 ± 0.000 |
| email | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.953 ± 0.000 | 1.000 ± 0.000 | 0.976 ± 0.000 | 0.990 ± 0.000 |
| id_number | strict | rules+gliner-cs-sk-focal-gpu | 3 | – | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| person | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.579 ± 0.022 | 0.709 ± 0.012 | 0.638 ± 0.016 | 0.679 ± 0.012 |
| phone | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.812 ± 0.000 | 0.963 ± 0.000 | 0.881 ± 0.000 | 0.929 ± 0.000 |
| any | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.655 ± 0.017 | 0.733 ± 0.006 | 0.692 ± 0.011 | 0.716 ± 0.008 |
| address | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.529 ± 0.020 | 1.000 ± 0.000 | 0.692 ± 0.017 | 0.849 ± 0.010 |
| birth_number | partial | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 0.050 ± 0.000 | 0.095 ± 0.000 | 0.062 ± 0.000 |
| date | partial | rules+gliner-cs-sk-focal-gpu | 3 | 1.000 ± 0.000 | 0.552 ± 0.000 | 0.711 ± 0.000 | 0.606 ± 0.000 |
| email | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.953 ± 0.000 | 1.000 ± 0.000 | 0.976 ± 0.000 | 0.990 ± 0.000 |
| id_number | partial | rules+gliner-cs-sk-focal-gpu | 3 | – | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| person | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.783 ± 0.024 | 0.994 ± 0.003 | 0.876 ± 0.014 | 0.943 ± 0.005 |
| phone | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.812 ± 0.000 | 0.963 ± 0.000 | 0.881 ± 0.000 | 0.929 ± 0.000 |
| any | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.796 ± 0.013 | 0.906 ± 0.002 | 0.848 ± 0.007 | 0.882 ± 0.002 |

### Seed by seed (paired)

Candidate minus baseline per seed: mean ± sd; on how many seeds F2 rose.

| type | match | baseline → candidate | n | ΔP | ΔR | ΔF1 | ΔF2 | F2 rose |
|---|---|---|---|---|---|---|---|---|
| address | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.360 ± 0.023 | +0.543 ± 0.043 | +0.450 ± 0.030 | +0.516 ± 0.036 | 3 / 3 |
| birth_number | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| date | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| email | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| id_number | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | – | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.160 ± 0.024 | +0.100 ± 0.012 | +0.139 ± 0.019 | +0.118 ± 0.015 | 3 / 3 |
| phone | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.188 ± 0.014 | +0.094 ± 0.006 | +0.150 ± 0.010 | +0.119 ± 0.008 | 3 / 3 |
| address | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.054 ± 0.000 | +0.000 ± 0.000 | +0.047 ± 0.000 | +0.028 ± 0.000 | 3 / 3 |
| birth_number | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| date | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| email | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| id_number | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | – | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.159 ± 0.015 | +0.056 ± 0.037 | +0.123 ± 0.024 | +0.088 ± 0.031 | 3 / 3 |
| phone | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.109 ± 0.009 | +0.033 ± 0.020 | +0.077 ± 0.014 | +0.053 ± 0.018 | 3 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.010 ± 0.038 | +0.012 ± 0.043 | -0.006 ± 0.043 | +0.002 ± 0.044 | 2 / 3 |
| birth_number | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| date | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| id_number | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | – | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.030 ± 0.032 | +0.002 ± 0.007 | -0.017 ± 0.021 | -0.007 ± 0.013 | 1 / 3 |
| phone | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.023 ± 0.022 | +0.002 ± 0.007 | -0.012 ± 0.015 | -0.004 ± 0.010 | 1 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.020 ± 0.020 | +0.000 ± 0.000 | -0.017 ± 0.017 | -0.010 ± 0.010 | 0 / 3 |
| birth_number | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| date | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| id_number | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | – | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.024 ± 0.023 | +0.020 ± 0.038 | -0.007 ± 0.024 | +0.008 ± 0.031 | 1 / 3 |
| phone | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.015 ± 0.015 | +0.012 ± 0.021 | -0.003 ± 0.015 | +0.006 ± 0.018 | 1 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.002 ± 0.028 | +0.000 ± 0.037 | -0.002 ± 0.032 | -0.001 ± 0.036 | 1 / 3 |
| birth_number | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| date | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| id_number | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | – | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.014 ± 0.028 | +0.002 ± 0.007 | -0.008 ± 0.020 | -0.003 ± 0.013 | 1 / 3 |
| phone | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.010 ± 0.020 | +0.001 ± 0.005 | -0.005 ± 0.013 | -0.002 ± 0.009 | 1 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.003 ± 0.012 | +0.000 ± 0.000 | -0.003 ± 0.010 | -0.002 ± 0.006 | 1 / 3 |
| birth_number | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| date | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| id_number | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | – | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.020 ± 0.028 | -0.001 ± 0.003 | -0.013 ± 0.016 | -0.007 ± 0.006 | 0 / 3 |
| phone | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.010 ± 0.013 | +0.000 ± 0.003 | -0.006 ± 0.006 | -0.003 ± 0.001 | 0 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.008 ± 0.019 | +0.012 ± 0.021 | -0.004 ± 0.021 | +0.003 ± 0.021 | 1 / 3 |
| birth_number | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| date | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| id_number | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | – | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.017 ± 0.018 | +0.000 ± 0.000 | -0.010 ± 0.010 | -0.004 ± 0.004 | 0 / 3 |
| phone | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.013 ± 0.011 | +0.001 ± 0.002 | -0.007 ± 0.006 | -0.002 ± 0.003 | 1 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.017 ± 0.012 | +0.000 ± 0.000 | -0.015 ± 0.010 | -0.009 ± 0.006 | 0 / 3 |
| birth_number | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| date | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| id_number | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | – | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.004 ± 0.012 | +0.021 ± 0.037 | +0.007 ± 0.022 | +0.015 ± 0.030 | 1 / 3 |
| phone | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.005 ± 0.006 | +0.012 ± 0.021 | +0.003 ± 0.013 | +0.008 ± 0.017 | 1 / 3 |

### rules+gliner → rules+gliner-cs-sk-ce-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.347 [+0.21, +0.49] | +0.518 [+0.28, +0.72] | +0.433 [+0.27, +0.58] | +0.495 [+0.30, +0.66] | 0.000 |
| birth_number | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | strict | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | +0.188 [+0.07, +0.32] | +0.114 [+0.04, +0.21] | +0.160 [+0.07, +0.25] | +0.135 [+0.06, +0.23] | 0.000 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | +0.204 [+0.12, +0.28] | +0.101 [+0.05, +0.16] | +0.161 [+0.10, +0.23] | +0.127 [+0.07, +0.19] | 0.000 |
| address | partial | +0.054 [-0.07, +0.17] | +0.000 [+0.00, +0.00] | +0.047 [-0.05, +0.17] | +0.029 [-0.03, +0.11] | 0.396 |
| birth_number | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | partial | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | +0.142 [+0.05, +0.24] | +0.014 [-0.11, +0.11] | +0.095 [+0.02, +0.17] | +0.052 [-0.04, +0.14] | 0.230 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | +0.099 [+0.04, +0.16] | +0.010 [-0.06, +0.06] | +0.061 [+0.02, +0.11] | +0.033 [-0.02, +0.08] | 0.206 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.096 [-0.17, -0.03] | +0.518 [+0.29, +0.71] | -2.2 [-4.8, -0.1] | 0.000 |
| birth_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| date | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| id_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.002 [-0.07, +0.08] | +0.014 [-0.11, +0.11] | -9.4 [-18.0, -1.8] | 0.858 |
| phone | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | -0.013 [-0.05, +0.02] | +0.044 [-0.02, +0.11] | -11.7 [-19.5, -4.1] | 0.414 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.020 [+0.00, +0.07] | +0.037 [+0.00, +0.12] | +0.026 [+0.00, +0.08] | +0.031 [+0.00, +0.10] | 0.712 |
| birth_number | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | strict | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.056 [-0.15, +0.00] | +0.000 [-0.04, +0.04] | -0.033 [-0.08, +0.01] | -0.015 [-0.06, +0.03] | 0.520 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | -0.036 [-0.09, +0.00] | +0.003 [-0.02, +0.03] | -0.018 [-0.05, +0.01] | -0.006 [-0.03, +0.02] | 0.652 |
| address | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| birth_number | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | partial | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.015 [-0.05, +0.01] | +0.064 [+0.00, +0.18] | +0.017 [-0.02, +0.08] | +0.043 [-0.01, +0.14] | 0.512 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | -0.005 [-0.02, +0.01] | +0.036 [+0.00, +0.10] | +0.013 [-0.01, +0.05] | +0.026 [-0.00, +0.08] | 0.368 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.021 [-0.07, +0.00] | +0.037 [+0.00, +0.12] | +0.0 [+0.0, +0.0] | 0.712 |
| birth_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| date | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| id_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.043 [-0.13, +0.00] | +0.059 [-0.01, +0.18] | +1.8 [+0.0, +4.5] | 0.260 |
| phone | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | -0.021 [-0.05, +0.00] | +0.036 [-0.00, +0.10] | +1.8 [+0.0, +4.5] | 0.078 |

### rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.028 [+0.00, +0.07] | +0.037 [+0.00, +0.12] | +0.033 [+0.00, +0.09] | +0.036 [+0.00, +0.11] | 0.256 |
| birth_number | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | strict | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.020 [-0.05, +0.01] | +0.000 [-0.04, +0.04] | -0.012 [-0.05, +0.02] | -0.005 [-0.04, +0.03] | 0.798 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | -0.010 [-0.03, +0.01] | +0.003 [-0.02, +0.03] | -0.004 [-0.03, +0.02] | -0.000 [-0.02, +0.02] | 0.992 |
| address | partial | +0.011 [+0.00, +0.03] | +0.000 [+0.00, +0.00] | +0.009 [+0.00, +0.03] | +0.005 [+0.00, +0.02] | 0.780 |
| birth_number | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | partial | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.023 [-0.05, -0.00] | +0.000 [+0.00, +0.00] | -0.014 [-0.03, -0.00] | -0.007 [-0.01, -0.00] | 0.026 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | -0.008 [-0.02, +0.00] | +0.000 [+0.00, +0.00] | -0.004 [-0.01, +0.00] | -0.002 [-0.01, +0.00] | 0.260 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.021 [-0.07, +0.00] | +0.037 [+0.00, +0.12] | -0.6 [-1.8, +0.0] | 0.712 |
| birth_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| date | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| id_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | +0.000 [+0.00, +0.00] | -0.005 [-0.01, +0.00] | +0.4 [-0.1, +1.1] | 0.722 |
| phone | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | -0.003 [-0.01, +0.00] | +0.000 [-0.01, +0.01] | -0.1 [-1.6, +0.9] | 0.712 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | -0.008 [-0.02, +0.00] | +0.000 [+0.00, +0.00] | -0.007 [-0.02, +0.00] | -0.004 [-0.01, +0.00] | 0.780 |
| birth_number | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | strict | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.036 [-0.11, +0.00] | +0.000 [+0.00, +0.00] | -0.021 [-0.06, +0.00] | -0.009 [-0.02, +0.00] | 0.090 |
| phone | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | strict | -0.026 [-0.07, -0.00] | +0.000 [+0.00, +0.00] | -0.014 [-0.04, -0.00] | -0.006 [-0.01, -0.00] | 0.034 |
| address | partial | -0.011 [-0.03, +0.00] | +0.000 [+0.00, +0.00] | -0.009 [-0.03, +0.00] | -0.005 [-0.02, +0.00] | 0.780 |
| birth_number | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| date | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| id_number | partial | – | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | +0.008 [-0.01, +0.03] | +0.064 [+0.00, +0.18] | +0.031 [-0.00, +0.10] | +0.049 [-0.00, +0.15] | 0.260 |
| phone | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| any | partial | +0.003 [-0.01, +0.02] | +0.036 [+0.00, +0.10] | +0.018 [-0.00, +0.06] | +0.028 [-0.00, +0.08] | 0.266 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.6 [+0.0, +1.8] | 1.000 |
| birth_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| date | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| id_number | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.043 [-0.13, +0.00] | +0.064 [+0.00, +0.18] | +1.3 [+0.0, +3.9] | 0.260 |
| phone | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| any | -0.018 [-0.05, +0.00] | +0.036 [+0.00, +0.10] | +1.9 [+0.1, +4.5] | 0.260 |

## openpii-1m-cs/dev · cs · dev

4672 documents, 4672 pages, 4672 sentences or records. Gold spans: address 2119, email 2625, person 4353.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner | 0.779 [0.76, 0.80] | 0.913 [0.90, 0.92] | 0.841 [0.83, 0.85] | 0.882 [0.87, 0.89] | 1934 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu | 0.997 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.976 [0.97, 0.98] | 0.963 [0.96, 0.97] | 2024 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.996 [0.99, 1.00] | 0.955 [0.94, 0.96] | 0.975 [0.97, 0.98] | 0.963 [0.95, 0.97] | 2023 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.995 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2029 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.993 [0.99, 1.00] | 0.959 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2031 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.993 [0.99, 1.00] | 0.957 [0.95, 0.97] | 0.975 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2028 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.991 [0.99, 1.00] | 0.961 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2036 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu | 0.994 [0.99, 1.00] | 0.957 [0.95, 0.97] | 0.975 [0.97, 0.98] | 0.964 [0.96, 0.97] | 2028 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.993 [0.99, 1.00] | 0.959 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2031 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.992 [0.99, 1.00] | 0.961 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2036 / 2119 |
| email | rules+gliner | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.998 [1.00, 1.00] | 0.993 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.994 [0.99, 1.00] | 2606 / 2625 |
| person | rules+gliner | 0.881 [0.87, 0.89] | 0.944 [0.94, 0.95] | 0.912 [0.90, 0.92] | 0.931 [0.92, 0.94] | 4110 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu | 0.995 [0.99, 1.00] | 0.989 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.990 [0.99, 0.99] | 4305 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.995 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.994 [0.99, 1.00] | 0.993 [0.99, 0.99] | 4318 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.997 [0.99, 1.00] | 0.990 [0.99, 0.99] | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4311 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.993 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4313 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.993 [0.99, 1.00] | 0.993 [0.99, 1.00] | 0.993 [0.99, 0.99] | 0.993 [0.99, 0.99] | 4321 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.994 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4314 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu | 0.993 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4313 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.992 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4318 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4316 / 4353 |
| any | rules+gliner | 0.884 [0.88, 0.89] | 0.952 [0.95, 0.96] | 0.917 [0.91, 0.92] | 0.937 [0.93, 0.94] | 8658 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu | 0.997 [1.00, 1.00] | 0.983 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8940 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.997 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8953 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.997 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8950 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.995 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8955 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8961 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8960 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu | 0.995 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8954 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.994 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8961 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8962 / 9097 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner | 0.236 [0.22, 0.25] | 0.361 [0.34, 0.38] | 0.285 [0.27, 0.30] | 0.327 [0.31, 0.35] | 765 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu | 0.849 [0.83, 0.86] | 0.828 [0.81, 0.84] | 0.838 [0.82, 0.85] | 0.832 [0.82, 0.85] | 1755 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.850 [0.84, 0.86] | 0.831 [0.81, 0.85] | 0.840 [0.82, 0.86] | 0.834 [0.82, 0.85] | 1760 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.848 [0.83, 0.86] | 0.832 [0.82, 0.85] | 0.840 [0.82, 0.85] | 0.835 [0.82, 0.85] | 1763 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.844 [0.83, 0.86] | 0.830 [0.81, 0.85] | 0.837 [0.82, 0.85] | 0.832 [0.82, 0.85] | 1758 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.847 [0.83, 0.86] | 0.832 [0.82, 0.85] | 0.839 [0.82, 0.85] | 0.835 [0.82, 0.85] | 1763 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.844 [0.83, 0.86] | 0.833 [0.82, 0.85] | 0.839 [0.82, 0.85] | 0.836 [0.82, 0.85] | 1766 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu | 0.845 [0.83, 0.86] | 0.830 [0.81, 0.85] | 0.837 [0.82, 0.85] | 0.833 [0.82, 0.85] | 1758 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.847 [0.83, 0.86] | 0.833 [0.82, 0.85] | 0.840 [0.82, 0.85] | 0.836 [0.82, 0.85] | 1765 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.843 [0.83, 0.86] | 0.832 [0.82, 0.85] | 0.837 [0.82, 0.85] | 0.834 [0.82, 0.85] | 1762 / 2119 |
| email | rules+gliner | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.956 [0.95, 0.96] | 0.951 [0.94, 0.96] | 0.953 [0.94, 0.96] | 0.952 [0.94, 0.96] | 2495 / 2625 |
| person | rules+gliner | 0.519 [0.50, 0.54] | 0.564 [0.55, 0.58] | 0.541 [0.53, 0.56] | 0.554 [0.54, 0.57] | 2455 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu | 0.984 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.979 [0.97, 0.98] | 4256 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.983 [0.98, 0.99] | 0.980 [0.97, 0.98] | 0.982 [0.98, 0.99] | 0.980 [0.98, 0.98] | 4264 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.985 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.982 [0.98, 0.99] | 0.980 [0.97, 0.98] | 4259 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.981 [0.98, 0.99] | 0.978 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.979 [0.97, 0.98] | 4259 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.981 [0.97, 0.99] | 0.980 [0.97, 0.98] | 0.980 [0.98, 0.99] | 0.980 [0.98, 0.98] | 4266 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.983 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.981 [0.98, 0.99] | 0.980 [0.97, 0.98] | 4262 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu | 0.980 [0.97, 0.98] | 0.978 [0.97, 0.98] | 0.979 [0.97, 0.98] | 0.978 [0.97, 0.98] | 4256 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.980 [0.97, 0.99] | 0.980 [0.97, 0.98] | 0.980 [0.97, 0.98] | 0.980 [0.97, 0.98] | 4264 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.982 [0.98, 0.99] | 0.979 [0.97, 0.98] | 0.981 [0.98, 0.98] | 0.980 [0.97, 0.98] | 4263 / 4353 |
| any | rules+gliner | 0.541 [0.53, 0.55] | 0.629 [0.62, 0.64] | 0.581 [0.57, 0.59] | 0.609 [0.60, 0.62] | 5719 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu | 0.945 [0.94, 0.95] | 0.935 [0.93, 0.94] | 0.940 [0.94, 0.95] | 0.937 [0.93, 0.94] | 8508 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.945 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8520 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.945 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.941 [0.94, 0.95] | 0.938 [0.93, 0.94] | 8519 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.942 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.937 [0.93, 0.94] | 8514 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.943 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.940 [0.94, 0.94] | 0.938 [0.93, 0.94] | 8525 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.943 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.940 [0.94, 0.94] | 0.938 [0.93, 0.94] | 8525 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu | 0.942 [0.94, 0.95] | 0.936 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.937 [0.93, 0.94] | 8512 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.942 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.940 [0.94, 0.94] | 0.938 [0.93, 0.94] | 8525 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.942 [0.94, 0.95] | 0.937 [0.93, 0.94] | 0.939 [0.93, 0.94] | 0.938 [0.93, 0.94] | 8520 / 9097 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner | 0.266 [0.25, 0.28] | 0.487 [0.47, 0.51] | 7.4 [6.8, 8.0] | 1031 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu | 0.085 [0.07, 0.10] | 0.933 [0.92, 0.94] | 1.0 [0.9, 1.2] | 1978 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.086 [0.07, 0.10] | 0.934 [0.92, 0.94] | 1.0 [0.9, 1.2] | 1980 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.082 [0.07, 0.10] | 0.936 [0.92, 0.95] | 1.1 [0.9, 1.3] | 1983 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.083 [0.07, 0.10] | 0.936 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1983 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.084 [0.07, 0.10] | 0.936 [0.92, 0.95] | 1.0 [0.9, 1.2] | 1983 / 2119 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.080 [0.07, 0.10] | 0.937 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1986 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu | 0.084 [0.07, 0.10] | 0.935 [0.92, 0.95] | 1.1 [0.9, 1.3] | 1982 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.083 [0.07, 0.10] | 0.937 [0.93, 0.95] | 1.1 [0.9, 1.3] | 1986 / 2119 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.080 [0.07, 0.10] | 0.938 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1988 / 2119 |
| email | rules+gliner | 0.021 [0.02, 0.03] | 0.952 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2499 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.022 [0.02, 0.03] | 0.951 [0.94, 0.96] | 0.1 [0.0, 0.2] | 2495 / 2625 |
| person | rules+gliner | 0.049 [0.04, 0.06] | 0.929 [0.92, 0.94] | 8.1 [7.7, 8.5] | 4045 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu | 0.008 [0.01, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4299 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4311 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.008 [0.01, 0.01] | 0.989 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4303 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.007 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4304 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.006 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.4 [0.2, 0.5] | 4315 / 4353 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.007 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.3 [0.2, 0.4] | 4306 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu | 0.007 [0.00, 0.01] | 0.989 [0.99, 0.99] | 0.4 [0.2, 0.5] | 4306 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.006 [0.00, 0.01] | 0.991 [0.99, 0.99] | 0.4 [0.3, 0.5] | 4312 / 4353 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.007 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.3 [0.2, 0.5] | 4310 / 4353 |
| any | rules+gliner | 0.115 [0.11, 0.12] | 0.833 [0.83, 0.84] | 15.6 [14.8, 16.3] | 7575 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu | 0.038 [0.03, 0.04] | 0.964 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8772 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8786 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.036 [0.03, 0.04] | 0.965 [0.96, 0.97] | 1.4 [1.2, 1.6] | 8781 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.036 [0.03, 0.04] | 0.965 [0.96, 0.97] | 1.5 [1.3, 1.7] | 8782 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.036 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.5 [1.3, 1.7] | 8793 / 9097 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.036 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.2, 1.7] | 8787 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu | 0.037 [0.03, 0.04] | 0.966 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8783 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.036 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8793 / 9097 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.035 [0.03, 0.04] | 0.967 [0.96, 0.97] | 1.6 [1.3, 1.9] | 8793 / 9097 |

### Across seeds

Mean ± sample standard deviation over n replicates, each scored on all documents.

| type | match | system | n | P | R | F1 | F2 |
|---|---|---|---|---|---|---|---|
| address | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.849 ± 0.001 | 0.830 ± 0.002 | 0.840 ± 0.001 | 0.834 ± 0.002 |
| email | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.956 ± 0.000 | 0.951 ± 0.000 | 0.953 ± 0.000 | 0.951 ± 0.000 |
| person | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.984 ± 0.001 | 0.979 ± 0.001 | 0.981 ± 0.000 | 0.980 ± 0.001 |
| any | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.945 ± 0.000 | 0.936 ± 0.001 | 0.941 ± 0.000 | 0.938 ± 0.001 |
| address | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.996 ± 0.001 | 0.956 ± 0.001 | 0.975 ± 0.000 | 0.964 ± 0.001 |
| email | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.998 ± 0.000 | 0.993 ± 0.000 | 0.995 ± 0.000 | 0.994 ± 0.000 |
| person | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.996 ± 0.001 | 0.990 ± 0.002 | 0.993 ± 0.001 | 0.991 ± 0.001 |
| any | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.997 ± 0.000 | 0.984 ± 0.001 | 0.990 ± 0.000 | 0.986 ± 0.001 |
| address | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.845 ± 0.002 | 0.832 ± 0.002 | 0.838 ± 0.001 | 0.834 ± 0.002 |
| email | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.956 ± 0.000 | 0.951 ± 0.000 | 0.953 ± 0.000 | 0.951 ± 0.000 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.981 ± 0.001 | 0.979 ± 0.001 | 0.980 ± 0.001 | 0.980 ± 0.001 |
| any | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.943 ± 0.000 | 0.937 ± 0.001 | 0.940 ± 0.001 | 0.938 ± 0.001 |
| address | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.993 ± 0.001 | 0.959 ± 0.002 | 0.975 ± 0.001 | 0.965 ± 0.001 |
| email | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.998 ± 0.000 | 0.993 ± 0.000 | 0.995 ± 0.000 | 0.994 ± 0.000 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.993 ± 0.001 | 0.991 ± 0.001 | 0.992 ± 0.001 | 0.992 ± 0.001 |
| any | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.995 ± 0.000 | 0.985 ± 0.000 | 0.990 ± 0.000 | 0.987 ± 0.000 |
| address | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.845 ± 0.002 | 0.831 ± 0.002 | 0.838 ± 0.002 | 0.834 ± 0.002 |
| email | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.956 ± 0.000 | 0.951 ± 0.000 | 0.953 ± 0.000 | 0.951 ± 0.000 |
| person | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.980 ± 0.001 | 0.979 ± 0.001 | 0.980 ± 0.001 | 0.979 ± 0.001 |
| any | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.942 ± 0.000 | 0.936 ± 0.001 | 0.939 ± 0.000 | 0.938 ± 0.001 |
| address | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.993 ± 0.001 | 0.959 ± 0.002 | 0.976 ± 0.001 | 0.965 ± 0.001 |
| email | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.998 ± 0.000 | 0.993 ± 0.000 | 0.995 ± 0.000 | 0.994 ± 0.000 |
| person | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.993 ± 0.001 | 0.991 ± 0.001 | 0.992 ± 0.000 | 0.992 ± 0.000 |
| any | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.995 ± 0.000 | 0.985 ± 0.000 | 0.990 ± 0.000 | 0.987 ± 0.000 |

### Seed by seed (paired)

Candidate minus baseline per seed: mean ± sd; on how many seeds F2 rose.

| type | match | baseline → candidate | n | ΔP | ΔR | ΔF1 | ΔF2 | F2 rose |
|---|---|---|---|---|---|---|---|---|
| address | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.613 ± 0.001 | +0.469 ± 0.002 | +0.554 ± 0.001 | +0.507 ± 0.002 | 3 / 3 |
| email | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.465 ± 0.001 | +0.415 ± 0.001 | +0.441 ± 0.000 | +0.425 ± 0.001 | 3 / 3 |
| any | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.404 ± 0.000 | +0.307 ± 0.001 | +0.359 ± 0.000 | +0.329 ± 0.001 | 3 / 3 |
| address | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.217 ± 0.001 | +0.043 ± 0.001 | +0.135 ± 0.000 | +0.081 ± 0.001 | 3 / 3 |
| email | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.115 ± 0.001 | +0.046 ± 0.002 | +0.081 ± 0.001 | +0.061 ± 0.001 | 3 / 3 |
| any | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.113 ± 0.000 | +0.032 ± 0.001 | +0.073 ± 0.000 | +0.049 ± 0.001 | 3 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.004 ± 0.001 | +0.001 ± 0.001 | -0.001 ± 0.001 | +0.000 ± 0.001 | 2 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.004 ± 0.001 | +0.000 ± 0.001 | -0.002 ± 0.001 | -0.000 ± 0.001 | 1 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.003 ± 0.000 | +0.000 ± 0.000 | -0.001 ± 0.000 | -0.000 ± 0.000 | 0 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.003 ± 0.000 | +0.003 ± 0.001 | +0.000 ± 0.001 | +0.002 ± 0.001 | 3 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.003 ± 0.001 | +0.001 ± 0.001 | -0.001 ± 0.001 | +0.000 ± 0.001 | 2 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.002 ± 0.000 | +0.001 ± 0.000 | -0.000 ± 0.000 | +0.001 ± 0.000 | 3 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.001 | -0.000 ± 0.001 | -0.000 ± 0.001 | -0.000 ± 0.001 | 2 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.001 ± 0.000 | -0.000 ± 0.000 | -0.001 ± 0.000 | -0.000 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.000 ± 0.000 | -0.000 ± 0.000 | -0.000 ± 0.000 | -0.000 ± 0.000 | 0 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.001 | +0.000 ± 0.001 | +0.000 ± 0.001 | 2 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.001 ± 0.000 | -0.000 ± 0.001 | -0.000 ± 0.000 | -0.000 ± 0.001 | 1 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.000 ± 0.000 | +0.000 ± 0.000 | -0.000 ± 0.000 | -0.000 ± 0.000 | 1 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.004 ± 0.001 | +0.001 ± 0.000 | -0.001 ± 0.000 | +0.000 ± 0.000 | 3 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.003 ± 0.000 | +0.001 ± 0.000 | -0.001 ± 0.000 | -0.000 ± 0.000 | 1 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.002 ± 0.000 | +0.001 ± 0.000 | -0.001 ± 0.000 | +0.000 ± 0.000 | 1 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.003 ± 0.001 | +0.003 ± 0.001 | -0.000 ± 0.000 | +0.002 ± 0.000 | 3 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.002 ± 0.000 | +0.001 ± 0.001 | -0.001 ± 0.000 | +0.000 ± 0.001 | 3 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.002 ± 0.000 | +0.001 ± 0.000 | -0.000 ± 0.000 | +0.001 ± 0.000 | 3 / 3 |

### rules+gliner → rules+gliner-cs-sk-ce-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.613 [+0.59, +0.63] | +0.467 [+0.45, +0.49] | +0.553 [+0.53, +0.57] | +0.506 [+0.49, +0.53] | 0.000 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | +0.465 [+0.45, +0.48] | +0.414 [+0.40, +0.43] | +0.440 [+0.42, +0.46] | +0.424 [+0.41, +0.44] | 0.000 |
| any | strict | +0.404 [+0.39, +0.41] | +0.307 [+0.30, +0.32] | +0.359 [+0.35, +0.37] | +0.328 [+0.32, +0.34] | 0.000 |
| address | partial | +0.218 [+0.20, +0.23] | +0.043 [+0.03, +0.06] | +0.135 [+0.12, +0.15] | +0.081 [+0.07, +0.09] | 0.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | +0.114 [+0.10, +0.13] | +0.045 [+0.04, +0.05] | +0.081 [+0.07, +0.09] | +0.059 [+0.05, +0.07] | 0.000 |
| any | partial | +0.113 [+0.11, +0.12] | +0.031 [+0.03, +0.04] | +0.073 [+0.07, +0.08] | +0.048 [+0.04, +0.05] | 0.000 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.181 [-0.20, -0.16] | +0.447 [+0.42, +0.47] | -6.4 [-6.9, -5.8] | 0.000 |
| email | +0.001 [+0.00, +0.00] | -0.002 [-0.00, -0.00] | +0.0 [+0.0, +0.0] | 0.024 |
| person | -0.041 [-0.05, -0.04] | +0.058 [+0.05, +0.07] | -7.8 [-8.2, -7.4] | 0.000 |
| any | -0.077 [-0.08, -0.07] | +0.132 [+0.12, +0.14] | -14.2 [-14.9, -13.5] | 0.000 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | -0.004 [-0.01, +0.00] | +0.001 [-0.00, +0.01] | -0.001 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | 0.874 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.004 [-0.01, -0.00] | +0.000 [-0.00, +0.00] | -0.002 [-0.00, -0.00] | -0.001 [-0.00, +0.00] | 0.288 |
| any | strict | -0.003 [-0.00, -0.00] | +0.000 [-0.00, +0.00] | -0.001 [-0.00, -0.00] | -0.000 [-0.00, +0.00] | 0.672 |
| address | partial | -0.003 [-0.01, -0.00] | +0.002 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | +0.001 [-0.00, +0.00] | 0.468 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.003 [-0.00, -0.00] | +0.002 [+0.00, +0.00] | -0.000 [-0.00, +0.00] | +0.001 [-0.00, +0.00] | 0.258 |
| any | partial | -0.002 [-0.00, -0.00] | +0.002 [+0.00, +0.00] | -0.000 [-0.00, +0.00] | +0.001 [-0.00, +0.00] | 0.054 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.001 [-0.00, +0.00] | +0.002 [-0.00, +0.01] | +0.1 [-0.0, +0.2] | 0.362 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.001 [-0.00, +0.00] | +0.002 [-0.00, +0.00] | +0.1 [+0.0, +0.1] | 0.344 |
| any | -0.001 [-0.00, +0.00] | +0.001 [+0.00, +0.00] | +0.2 [+0.1, +0.3] | 0.210 |

### rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.001 [-0.00, +0.01] | +0.000 [-0.00, +0.00] | +0.001 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | 0.984 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.001 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | 0.260 |
| any | strict | -0.000 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | 0.638 |
| address | partial | +0.001 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | 0.310 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.000 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | 0.930 |
| any | partial | -0.000 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | 0.848 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | +0.001 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | +0.0 [-0.1, +0.1] | 0.664 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | +0.000 [-0.00, +0.00] | +0.001 [-0.00, +0.00] | +0.0 [-0.0, +0.1] | 0.700 |
| any | +0.000 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | +0.0 [-0.1, +0.2] | 0.534 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | -0.005 [-0.01, -0.00] | +0.001 [-0.00, +0.00] | -0.002 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | 0.816 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.003 [-0.01, -0.00] | +0.001 [+0.00, +0.00] | -0.001 [-0.00, -0.00] | -0.000 [-0.00, +0.00] | 0.782 |
| any | strict | -0.003 [-0.00, -0.00] | +0.001 [+0.00, +0.00] | -0.001 [-0.00, -0.00] | -0.000 [-0.00, +0.00] | 0.942 |
| address | partial | -0.004 [-0.01, -0.00] | +0.003 [+0.00, +0.01] | -0.000 [-0.00, +0.00] | +0.002 [+0.00, +0.00] | 0.044 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.002 [-0.00, -0.00] | +0.002 [+0.00, +0.00] | -0.000 [-0.00, +0.00] | +0.001 [+0.00, +0.00] | 0.036 |
| any | partial | -0.002 [-0.00, -0.00] | +0.002 [+0.00, +0.00] | -0.000 [-0.00, +0.00] | +0.001 [+0.00, +0.00] | 0.002 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.002 [-0.00, -0.00] | +0.002 [+0.00, +0.00] | +0.1 [+0.0, +0.1] | 0.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.001 [-0.00, -0.00] | +0.001 [+0.00, +0.00] | +0.1 [+0.0, +0.1] | 0.000 |
| any | -0.001 [-0.00, -0.00] | +0.001 [+0.00, +0.00] | +0.1 [+0.1, +0.2] | 0.000 |

## openpii-1m-sk/dev · sk · dev

4451 documents, 4451 pages, 4451 sentences or records. Gold spans: address 2118, email 2465, person 4344.

### Partial match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner | 0.757 [0.74, 0.77] | 0.931 [0.92, 0.94] | 0.835 [0.82, 0.85] | 0.890 [0.88, 0.90] | 1972 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu | 0.996 [0.99, 1.00] | 0.958 [0.95, 0.97] | 0.977 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2029 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.995 [0.99, 1.00] | 0.955 [0.95, 0.96] | 0.975 [0.97, 0.98] | 0.963 [0.96, 0.97] | 2023 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.993 [0.99, 1.00] | 0.959 [0.95, 0.97] | 0.976 [0.97, 0.98] | 0.966 [0.96, 0.97] | 2032 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.992 [0.99, 1.00] | 0.963 [0.96, 0.97] | 0.977 [0.97, 0.98] | 0.969 [0.96, 0.98] | 2040 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.990 [0.99, 0.99] | 0.959 [0.95, 0.97] | 0.974 [0.97, 0.98] | 0.965 [0.96, 0.97] | 2030 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.987 [0.98, 0.99] | 0.962 [0.95, 0.97] | 0.974 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2038 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu | 0.992 [0.99, 1.00] | 0.967 [0.96, 0.97] | 0.979 [0.97, 0.98] | 0.972 [0.97, 0.98] | 2047 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.989 [0.98, 0.99] | 0.961 [0.95, 0.97] | 0.975 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2036 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.985 [0.98, 0.99] | 0.963 [0.96, 0.97] | 0.974 [0.97, 0.98] | 0.967 [0.96, 0.97] | 2040 / 2118 |
| email | rules+gliner | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.998 [1.00, 1.00] | 0.992 [0.99, 1.00] | 0.995 [0.99, 1.00] | 0.993 [0.99, 1.00] | 2446 / 2465 |
| person | rules+gliner | 0.889 [0.88, 0.90] | 0.945 [0.94, 0.95] | 0.916 [0.91, 0.92] | 0.933 [0.93, 0.94] | 4103 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu | 0.996 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4304 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.995 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4306 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.995 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4306 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.996 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 4305 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.993 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.993 [0.99, 0.99] | 4311 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.995 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4307 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu | 0.993 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.992 [0.99, 0.99] | 0.991 [0.99, 0.99] | 4305 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.994 [0.99, 1.00] | 0.991 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4305 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.994 [0.99, 1.00] | 0.992 [0.99, 0.99] | 0.993 [0.99, 0.99] | 0.992 [0.99, 0.99] | 4307 / 4344 |
| any | rules+gliner | 0.878 [0.87, 0.88] | 0.956 [0.95, 0.96] | 0.915 [0.91, 0.92] | 0.940 [0.94, 0.94] | 8536 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu | 0.997 [1.00, 1.00] | 0.984 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8786 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.996 [0.99, 1.00] | 0.984 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.986 [0.98, 0.99] | 8784 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.997 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.987 [0.99, 0.99] | 8794 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.996 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8798 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.98, 0.99] | 8796 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.995 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8801 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu | 0.995 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.991 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8806 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.995 [0.99, 1.00] | 0.985 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.987 [0.99, 0.99] | 8797 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.994 [0.99, 1.00] | 0.986 [0.98, 0.99] | 0.990 [0.99, 0.99] | 0.988 [0.99, 0.99] | 8802 / 8927 |

### Strict match

| type | system | P | R | F1 | F2 | found / gold |
|---|---|---|---|---|---|---|
| address | rules+gliner | 0.236 [0.22, 0.25] | 0.385 [0.36, 0.41] | 0.293 [0.28, 0.31] | 0.342 [0.32, 0.36] | 815 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu | 0.841 [0.82, 0.86] | 0.823 [0.81, 0.84] | 0.832 [0.82, 0.85] | 0.827 [0.81, 0.84] | 1744 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.840 [0.82, 0.85] | 0.822 [0.80, 0.84] | 0.831 [0.81, 0.85] | 0.825 [0.81, 0.84] | 1740 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.834 [0.82, 0.85] | 0.823 [0.80, 0.84] | 0.828 [0.81, 0.84] | 0.825 [0.81, 0.84] | 1742 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.835 [0.82, 0.85] | 0.827 [0.81, 0.84] | 0.831 [0.81, 0.85] | 0.828 [0.81, 0.84] | 1751 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.836 [0.82, 0.85] | 0.824 [0.81, 0.84] | 0.830 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1746 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.829 [0.81, 0.84] | 0.826 [0.81, 0.84] | 0.828 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1749 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu | 0.832 [0.82, 0.85] | 0.825 [0.81, 0.84] | 0.828 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1748 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.833 [0.82, 0.85] | 0.825 [0.81, 0.84] | 0.829 [0.81, 0.84] | 0.827 [0.81, 0.84] | 1747 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.830 [0.81, 0.85] | 0.827 [0.81, 0.84] | 0.829 [0.81, 0.84] | 0.828 [0.81, 0.84] | 1752 / 2118 |
| email | rules+gliner | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.962 [0.95, 0.97] | 0.957 [0.95, 0.96] | 0.960 [0.95, 0.97] | 0.958 [0.95, 0.97] | 2359 / 2465 |
| person | rules+gliner | 0.510 [0.49, 0.53] | 0.554 [0.54, 0.57] | 0.531 [0.52, 0.55] | 0.545 [0.53, 0.56] | 2406 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu | 0.977 [0.97, 0.98] | 0.972 [0.96, 0.98] | 0.974 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4220 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.976 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4225 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.977 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.975 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4224 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.976 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.974 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4221 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.975 [0.97, 0.98] | 0.974 [0.97, 0.98] | 0.974 [0.97, 0.98] | 0.974 [0.97, 0.98] | 4230 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.975 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.974 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4225 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu | 0.973 [0.97, 0.98] | 0.972 [0.96, 0.98] | 0.972 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4220 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.976 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.974 [0.97, 0.98] | 0.973 [0.97, 0.98] | 4223 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.974 [0.97, 0.98] | 0.972 [0.97, 0.98] | 0.973 [0.97, 0.98] | 0.972 [0.97, 0.98] | 4222 / 4344 |
| any | rules+gliner | 0.527 [0.52, 0.54] | 0.626 [0.62, 0.64] | 0.572 [0.56, 0.58] | 0.603 [0.59, 0.61] | 5588 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu | 0.941 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8327 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.941 [0.94, 0.95] | 0.933 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8329 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.940 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8331 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.940 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8335 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.939 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.937 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8340 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.938 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8339 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu | 0.937 [0.93, 0.94] | 0.933 [0.93, 0.94] | 0.935 [0.93, 0.94] | 0.934 [0.93, 0.94] | 8332 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.939 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8335 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.937 [0.93, 0.94] | 0.934 [0.93, 0.94] | 0.936 [0.93, 0.94] | 0.935 [0.93, 0.94] | 8339 / 8927 |

### Leak coverage

Characters other than whitespace. Residual: share of gold characters no prediction covers, whatever its type (lower is better). Hidden whole: gold spans with every character covered. Over: characters predicted outside every gold span, per 1,000 characters of text.

| type | system | residual | hidden whole | over / 1k | hidden / gold |
|---|---|---|---|---|---|
| address | rules+gliner | 0.250 [0.23, 0.27] | 0.505 [0.48, 0.53] | 8.9 [8.3, 9.6] | 1069 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu | 0.092 [0.07, 0.11] | 0.942 [0.93, 0.95] | 1.1 [1.0, 1.3] | 1994 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu-s1 | 0.094 [0.08, 0.11] | 0.938 [0.93, 0.95] | 1.1 [1.0, 1.3] | 1987 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu-s2 | 0.091 [0.07, 0.11] | 0.939 [0.93, 0.95] | 1.1 [1.0, 1.3] | 1989 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041 | 0.089 [0.07, 0.11] | 0.945 [0.94, 0.95] | 1.2 [1.0, 1.5] | 2002 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.092 [0.07, 0.11] | 0.942 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1994 / 2118 |
| address | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.090 [0.07, 0.11] | 0.943 [0.93, 0.95] | 1.2 [1.0, 1.4] | 1997 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu | 0.089 [0.07, 0.11] | 0.947 [0.94, 0.96] | 1.3 [1.1, 1.5] | 2006 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu-s1 | 0.091 [0.07, 0.11] | 0.944 [0.93, 0.95] | 1.2 [1.1, 1.5] | 2000 / 2118 |
| address | rules+gliner-cs-sk-focal-gpu-s2 | 0.089 [0.07, 0.11] | 0.945 [0.94, 0.95] | 1.3 [1.1, 1.5] | 2002 / 2118 |
| email | rules+gliner | 0.019 [0.01, 0.02] | 0.960 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2367 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| email | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu-s1 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| email | rules+gliner-cs-sk-focal-gpu-s2 | 0.020 [0.02, 0.03] | 0.958 [0.95, 0.97] | 0.1 [0.0, 0.2] | 2361 / 2465 |
| person | rules+gliner | 0.049 [0.04, 0.06] | 0.927 [0.92, 0.93] | 7.7 [7.3, 8.0] | 4026 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu | 0.006 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4287 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu-s1 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.3, 0.5] | 4293 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu-s2 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4290 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041 | 0.006 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4289 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.005 [0.00, 0.01] | 0.990 [0.99, 0.99] | 0.4 [0.3, 0.5] | 4299 / 4344 |
| person | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.3 [0.2, 0.4] | 4293 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu | 0.006 [0.00, 0.01] | 0.987 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4289 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu-s1 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4293 / 4344 |
| person | rules+gliner-cs-sk-focal-gpu-s2 | 0.006 [0.00, 0.01] | 0.988 [0.98, 0.99] | 0.4 [0.3, 0.5] | 4293 / 4344 |
| any | rules+gliner | 0.107 [0.10, 0.11] | 0.836 [0.83, 0.84] | 16.7 [16.0, 17.5] | 7462 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8642 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu-s1 | 0.038 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.6 [1.3, 1.8] | 8641 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu-s2 | 0.037 [0.03, 0.04] | 0.968 [0.96, 0.97] | 1.5 [1.3, 1.8] | 8640 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041 | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.7 [1.4, 1.9] | 8652 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s1 | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.7 [1.5, 1.9] | 8654 / 8927 |
| any | rules+gliner-cs-sk-ce-gpu@0.041-s2 | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.6 [1.4, 1.9] | 8651 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu | 0.036 [0.03, 0.04] | 0.970 [0.97, 0.97] | 1.8 [1.5, 2.1] | 8656 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu-s1 | 0.037 [0.03, 0.04] | 0.969 [0.97, 0.97] | 1.7 [1.5, 2.0] | 8654 / 8927 |
| any | rules+gliner-cs-sk-focal-gpu-s2 | 0.037 [0.03, 0.04] | 0.970 [0.97, 0.97] | 1.7 [1.5, 2.0] | 8656 / 8927 |

### Across seeds

Mean ± sample standard deviation over n replicates, each scored on all documents.

| type | match | system | n | P | R | F1 | F2 |
|---|---|---|---|---|---|---|---|
| address | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.838 ± 0.003 | 0.822 ± 0.001 | 0.830 ± 0.002 | 0.826 ± 0.001 |
| email | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.962 ± 0.000 | 0.957 ± 0.000 | 0.959 ± 0.000 | 0.958 ± 0.000 |
| person | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.977 ± 0.000 | 0.972 ± 0.001 | 0.974 ± 0.000 | 0.973 ± 0.000 |
| any | strict | rules+gliner-cs-sk-ce-gpu | 3 | 0.941 ± 0.001 | 0.933 ± 0.000 | 0.937 ± 0.000 | 0.935 ± 0.000 |
| address | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.995 ± 0.002 | 0.958 ± 0.002 | 0.976 ± 0.001 | 0.965 ± 0.002 |
| email | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.998 ± 0.000 | 0.992 ± 0.000 | 0.995 ± 0.000 | 0.993 ± 0.000 |
| person | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.995 ± 0.001 | 0.991 ± 0.000 | 0.993 ± 0.000 | 0.992 ± 0.000 |
| any | partial | rules+gliner-cs-sk-ce-gpu | 3 | 0.997 ± 0.000 | 0.984 ± 0.001 | 0.990 ± 0.000 | 0.987 ± 0.001 |
| address | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.834 ± 0.004 | 0.826 ± 0.001 | 0.830 ± 0.002 | 0.827 ± 0.001 |
| email | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.962 ± 0.000 | 0.957 ± 0.000 | 0.959 ± 0.000 | 0.958 ± 0.000 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.976 ± 0.001 | 0.973 ± 0.001 | 0.974 ± 0.000 | 0.973 ± 0.001 |
| any | strict | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.939 ± 0.001 | 0.934 ± 0.000 | 0.936 ± 0.000 | 0.935 ± 0.000 |
| address | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.990 ± 0.003 | 0.961 ± 0.002 | 0.975 ± 0.002 | 0.967 ± 0.002 |
| email | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.998 ± 0.000 | 0.992 ± 0.000 | 0.995 ± 0.000 | 0.993 ± 0.000 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.994 ± 0.001 | 0.992 ± 0.001 | 0.993 ± 0.000 | 0.992 ± 0.000 |
| any | partial | rules+gliner-cs-sk-ce-gpu@0.041 | 3 | 0.995 ± 0.001 | 0.986 ± 0.000 | 0.990 ± 0.000 | 0.987 ± 0.000 |
| address | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.832 ± 0.002 | 0.826 ± 0.001 | 0.829 ± 0.000 | 0.827 ± 0.001 |
| email | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.962 ± 0.000 | 0.957 ± 0.000 | 0.959 ± 0.000 | 0.958 ± 0.000 |
| person | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.974 ± 0.001 | 0.972 ± 0.000 | 0.973 ± 0.001 | 0.972 ± 0.001 |
| any | strict | rules+gliner-cs-sk-focal-gpu | 3 | 0.938 ± 0.001 | 0.934 ± 0.000 | 0.936 ± 0.001 | 0.935 ± 0.000 |
| address | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.989 ± 0.004 | 0.964 ± 0.003 | 0.976 ± 0.003 | 0.969 ± 0.003 |
| email | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.998 ± 0.000 | 0.992 ± 0.000 | 0.995 ± 0.000 | 0.993 ± 0.000 |
| person | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.994 ± 0.001 | 0.991 ± 0.000 | 0.992 ± 0.000 | 0.992 ± 0.000 |
| any | partial | rules+gliner-cs-sk-focal-gpu | 3 | 0.994 ± 0.001 | 0.986 ± 0.001 | 0.990 ± 0.000 | 0.988 ± 0.000 |

### Seed by seed (paired)

Candidate minus baseline per seed: mean ± sd; on how many seeds F2 rose.

| type | match | baseline → candidate | n | ΔP | ΔR | ΔF1 | ΔF2 | F2 rose |
|---|---|---|---|---|---|---|---|---|
| address | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.602 ± 0.003 | +0.438 ± 0.001 | +0.537 ± 0.002 | +0.484 ± 0.001 | 3 / 3 |
| email | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.466 ± 0.000 | +0.418 ± 0.001 | +0.443 ± 0.000 | +0.428 ± 0.000 | 3 / 3 |
| any | strict | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.414 ± 0.001 | +0.307 ± 0.000 | +0.365 ± 0.000 | +0.331 ± 0.000 | 3 / 3 |
| address | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.237 ± 0.002 | +0.026 ± 0.002 | +0.140 ± 0.001 | +0.075 ± 0.002 | 3 / 3 |
| email | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.106 ± 0.001 | +0.047 ± 0.000 | +0.077 ± 0.000 | +0.059 ± 0.000 | 3 / 3 |
| any | partial | rules+gliner → rules+gliner-cs-sk-ce-gpu | 3 | +0.119 ± 0.000 | +0.028 ± 0.001 | +0.075 ± 0.000 | +0.047 ± 0.001 | 3 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.007 ± 0.002 | +0.003 ± 0.001 | -0.002 ± 0.002 | +0.001 ± 0.002 | 2 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.002 ± 0.002 | -0.000 ± 0.000 | -0.001 ± 0.001 | -0.001 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.003 ± 0.001 | +0.001 ± 0.000 | -0.001 ± 0.001 | +0.000 ± 0.000 | 2 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.006 ± 0.002 | +0.006 ± 0.002 | +0.000 ± 0.002 | +0.004 ± 0.002 | 3 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.002 ± 0.001 | +0.000 ± 0.000 | -0.001 ± 0.001 | -0.000 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu | 3 | -0.002 ± 0.001 | +0.002 ± 0.001 | -0.000 ± 0.001 | +0.001 ± 0.001 | 3 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.002 ± 0.002 | +0.000 ± 0.001 | -0.001 ± 0.002 | -0.000 ± 0.002 | 1 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.001 ± 0.002 | -0.001 ± 0.001 | -0.001 ± 0.001 | -0.001 ± 0.000 | 0 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.001 ± 0.001 | -0.000 ± 0.000 | -0.001 ± 0.001 | -0.000 ± 0.000 | 0 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.001 ± 0.001 | +0.002 ± 0.001 | +0.001 ± 0.001 | +0.002 ± 0.001 | 3 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.001 ± 0.002 | -0.000 ± 0.001 | -0.001 ± 0.001 | -0.001 ± 0.000 | 0 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu | 3 | -0.001 ± 0.001 | +0.000 ± 0.000 | -0.000 ± 0.000 | +0.000 ± 0.000 | 2 / 3 |
| address | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.005 ± 0.001 | +0.003 ± 0.000 | -0.001 ± 0.000 | +0.002 ± 0.000 | 3 / 3 |
| email | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.001 ± 0.000 | +0.001 ± 0.001 | -0.000 ± 0.000 | +0.000 ± 0.000 | 2 / 3 |
| any | strict | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.002 ± 0.000 | +0.001 ± 0.000 | -0.000 ± 0.000 | +0.000 ± 0.000 | 3 / 3 |
| address | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.005 ± 0.001 | +0.004 ± 0.001 | -0.000 ± 0.001 | +0.002 ± 0.001 | 3 / 3 |
| email | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | +0.000 ± 0.000 | 0 / 3 |
| person | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.001 ± 0.001 | +0.001 ± 0.001 | -0.000 ± 0.000 | +0.000 ± 0.000 | 2 / 3 |
| any | partial | rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 | 3 | -0.002 ± 0.000 | +0.001 ± 0.000 | -0.000 ± 0.000 | +0.001 ± 0.000 | 3 / 3 |

### rules+gliner → rules+gliner-cs-sk-ce-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | +0.604 [+0.59, +0.62] | +0.439 [+0.42, +0.46] | +0.539 [+0.52, +0.56] | +0.485 [+0.47, +0.50] | 0.000 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | +0.466 [+0.45, +0.48] | +0.418 [+0.40, +0.43] | +0.443 [+0.43, +0.46] | +0.428 [+0.41, +0.44] | 0.000 |
| any | strict | +0.415 [+0.40, +0.42] | +0.307 [+0.30, +0.32] | +0.365 [+0.35, +0.37] | +0.331 [+0.32, +0.34] | 0.000 |
| address | partial | +0.239 [+0.22, +0.26] | +0.027 [+0.01, +0.04] | +0.141 [+0.13, +0.15] | +0.075 [+0.06, +0.09] | 0.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | +0.107 [+0.10, +0.12] | +0.046 [+0.04, +0.05] | +0.077 [+0.07, +0.08] | +0.059 [+0.05, +0.06] | 0.000 |
| any | partial | +0.119 [+0.11, +0.13] | +0.028 [+0.02, +0.03] | +0.075 [+0.07, +0.08] | +0.047 [+0.04, +0.05] | 0.000 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.158 [-0.18, -0.14] | +0.437 [+0.42, +0.46] | -7.8 [-8.4, -7.2] | 0.000 |
| email | +0.002 [+0.00, +0.00] | -0.002 [-0.00, -0.00] | +0.0 [+0.0, +0.0] | 0.006 |
| person | -0.043 [-0.05, -0.04] | +0.060 [+0.05, +0.07] | -7.4 [-7.7, -6.9] | 0.000 |
| any | -0.069 [-0.08, -0.06] | +0.132 [+0.13, +0.14] | -15.2 [-15.9, -14.4] | 0.000 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | -0.009 [-0.01, -0.00] | +0.002 [-0.00, +0.01] | -0.003 [-0.01, +0.00] | -0.000 [-0.00, +0.00] | 0.908 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.004 [-0.01, -0.00] | +0.000 [-0.00, +0.00] | -0.002 [-0.00, -0.00] | -0.001 [-0.00, +0.00] | 0.266 |
| any | strict | -0.004 [-0.01, -0.00] | +0.001 [-0.00, +0.00] | -0.002 [-0.00, -0.00] | -0.000 [-0.00, +0.00] | 0.558 |
| address | partial | -0.004 [-0.01, -0.00] | +0.009 [+0.00, +0.01] | +0.002 [-0.00, +0.01] | +0.006 [+0.00, +0.01] | 0.000 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.003 [-0.01, -0.00] | +0.000 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | -0.000 [-0.00, +0.00] | 0.540 |
| any | partial | -0.002 [-0.00, -0.00] | +0.002 [+0.00, +0.00] | -0.000 [-0.00, +0.00] | +0.001 [+0.00, +0.00] | 0.004 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.003 [-0.01, -0.00] | +0.006 [+0.00, +0.01] | +0.2 [+0.0, +0.3] | 0.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.000 [-0.00, +0.00] | +0.001 [-0.00, +0.00] | +0.0 [-0.0, +0.1] | 0.642 |
| any | -0.001 [-0.00, -0.00] | +0.002 [+0.00, +0.00] | +0.2 [+0.1, +0.3] | 0.000 |

### rules+gliner-cs-sk-ce-gpu@0.041 → rules+gliner-cs-sk-focal-gpu (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | -0.004 [-0.01, +0.00] | -0.001 [-0.01, +0.00] | -0.003 [-0.01, +0.00] | -0.002 [-0.01, +0.00] | 0.342 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.003 [-0.01, -0.00] | -0.000 [-0.00, +0.00] | -0.002 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | 0.164 |
| any | strict | -0.002 [-0.00, -0.00] | -0.000 [-0.00, +0.00] | -0.001 [-0.00, -0.00] | -0.001 [-0.00, +0.00] | 0.198 |
| address | partial | +0.000 [-0.00, +0.00] | +0.003 [+0.00, +0.01] | +0.002 [+0.00, +0.00] | +0.003 [+0.00, +0.01] | 0.008 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.003 [-0.01, +0.00] | +0.000 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | -0.001 [-0.00, +0.00] | 0.346 |
| any | partial | -0.001 [-0.00, +0.00] | +0.001 [+0.00, +0.00] | -0.000 [-0.00, +0.00] | +0.001 [-0.00, +0.00] | 0.190 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.001 [-0.00, +0.00] | +0.002 [-0.00, +0.00] | +0.0 [-0.0, +0.2] | 0.244 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | +0.000 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | +0.0 [-0.0, +0.1] | 0.994 |
| any | -0.000 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | +0.1 [-0.0, +0.2] | 0.280 |

### rules+gliner-cs-sk-ce-gpu → rules+gliner-cs-sk-ce-gpu@0.041 (paired)

Candidate minus baseline; p is two-sided, from the same resamples.

| type | match | ΔP | ΔR | ΔF1 | ΔF2 | p (F2) |
|---|---|---|---|---|---|---|
| address | strict | -0.005 [-0.01, -0.00] | +0.003 [+0.00, +0.01] | -0.001 [-0.00, +0.00] | +0.002 [-0.00, +0.00] | 0.104 |
| email | strict | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | strict | -0.000 [-0.00, +0.00] | +0.000 [+0.00, +0.00] | -0.000 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | 0.842 |
| any | strict | -0.002 [-0.00, -0.00] | +0.001 [+0.00, +0.00] | -0.000 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | 0.136 |
| address | partial | -0.004 [-0.01, -0.00] | +0.005 [+0.00, +0.01] | +0.001 [-0.00, +0.00] | +0.003 [+0.00, +0.01] | 0.002 |
| email | partial | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | 1.000 |
| person | partial | -0.000 [-0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.000 [-0.00, +0.00] | +0.000 [-0.00, +0.00] | 0.590 |
| any | partial | -0.001 [-0.00, -0.00] | +0.001 [+0.00, +0.00] | +0.000 [-0.00, +0.00] | +0.001 [+0.00, +0.00] | 0.004 |

Leak coverage, candidate minus baseline:

| type | Δresidual | Δhidden whole | Δover / 1k | p (residual) |
|---|---|---|---|---|
| address | -0.002 [-0.00, -0.00] | +0.004 [+0.00, +0.01] | +0.1 [+0.0, +0.2] | 0.000 |
| email | +0.000 [+0.00, +0.00] | +0.000 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 1.000 |
| person | -0.000 [-0.00, +0.00] | +0.001 [+0.00, +0.00] | +0.0 [+0.0, +0.0] | 0.282 |
| any | -0.001 [-0.00, -0.00] | +0.001 [+0.00, +0.00] | +0.1 [+0.0, +0.2] | 0.000 |
