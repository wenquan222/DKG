# Exp 1 — Recall results (5-document ground truth)

Fuzzy-match threshold: 0.7 (SequenceMatcher ratio)
Ground-truth Y set: 113 items (from 5 source documents)

## Per-document Recall
| Document | GT total | TP | FN | Recall |
|---|---:|---:|---:|---:|
| MAN-01 | 28 | 28 | 0 | 100.0% |
| PAP-04 | 27 | 20 | 7 | 74.1% |
| PAP-93 | 18 | 16 | 2 | 88.9% |
| TOOL-01 | 24 | 22 | 2 | 91.7% |
| TOOL-01 | 16 | 14 | 2 | 87.5% |
| **OVERALL** | **113** | **100** | **13** | **88.5%** |

## Per-kind Recall
| Kind | GT total | TP | FN | Recall |
|---|---:|---:|---:|---:|
| upper | 60 | 55 | 5 | 91.7% |
| lower | 39 | 32 | 7 | 82.0% |
| cross | 14 | 13 | 1 | 92.9% |

## Missed items (FN)
13 ground-truth items not found in KG:

| Doc | Kind | Triple / Item |
|---|---|---|
| PAP | upper | (Hamming Distance, alternative_to, Hamming Weight) |
| PAP | upper | (Electromagnetic Radiation, alternative_to, Power) |
| PAP | lower | [lower] exhaustively search for reference state R |
| PAP | lower | [lower] use partial correlation for wider architectures |
| PAP | cross | (use partial correlation for wider archit, strategy_applies_to, 32-bit architecture) |
| PAP | upper | (CPA, alternative_to, DPA) |
| PAP | upper | (Unstable Clocking, weakens, CPA) |
| PAP | lower | [lower] use absolute correlation value for S-box attack |
| PAP | lower | [lower] cannot use absolute correlation for XOR attack |
| TOOL | upper | (Hamming Distance, alternative_to, Hamming Weight) |
| TOOL | lower | [lower] use absolute correlation for key ranking |
| TOOL | lower | [lower] select unique reference segment |
| TOOL | lower | [lower] discard traces with excessive shift |