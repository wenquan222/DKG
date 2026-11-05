# DKG Knowledge Graph Statistics

> Generated: 2026-11-05  
> KG version: Round 2 fusion (166 source documents)

## Summary

- **Total nodes**: 1334
- **Total edges**: 1813
  - Intra-upper: 953
  - Intra-lower (indicates + resolves): 558
  - Cross-layer (strategy_applies_to + relates_to): 302
- **Average node degree**: 2.718

## Upper Layer (Configuration Space Graph)

- Entities: **462**
- Relationships: **953**

### Entity count by type (12 types)

| Type | Count |
|---|---:|
| Preprocessing | 90 |
| DeviceClass | 83 |
| StatMethod | 75 |
| Countermeasure | 46 |
| AttackPoint | 36 |
| DiagnosticMethod | 36 |
| Pipeline | 34 |
| LeakageModel | 26 |
| RecoveryMethod | 12 |
| Algorithm | 10 |
| ValidationMethod | 8 |
| TraceType | 6 |

### Relationship count by type

| Relation | Count |
|---|---:|
| works_with | 603 |
| consists_of | 137 |
| acquires_via | 86 |
| has_attack_point | 39 |
| precedes | 34 |
| weakens | 30 |
| alternative_to | 24 |

### `works_with` confidence stats

- With numeric confidence: 603
- Avg confidence: 0.228
- Range: [0.2, 1.0]

## Lower Layer (Diagnostic Strategy Graph)

- Observations: **273**
- Causes: **278**
- Actions: **278**
- Strategies: **43** (canonical: **21**)

- `indicates` edges: 278
- `resolves` edges: 280
- `strategy_applies_to` cross-layer edges: 80
- `relates_to` cross-layer edges: 222

### Strategy type breakdown

| Type | Count |
|---|---:|
| troubleshooting_checklist | 23 |
| parameter_preset_bundle | 10 |
| anti_pattern_set | 10 |

### Canonical Strategy priority distribution

| Priority | Count |
|---:|---:|
| 100 | 14 |
| 95 | 6 |
| 90 | 1 |

### Canonical Strategy IDs

- `strat_001`
- `strat_002`
- `strat_003`
- `strat_023`
- `strat_024`
- `strat_027`
- `strat_029`
- `strat_030`
- `strat_alignment_metric_separation`
- `strat_argmax_not_reference`
- `strat_des_master_key_recovery_protocol`
- `strat_green_band_key_search`
- `strat_key_search_escalate_before_pivot`
- `strat_max_shift_large_start`
- `strat_no_target_churn_software`
- `strat_no_vertical_align_software`
- `strat_nonprofiled_cpa_low_hc_no_churn`
- `strat_software_impl_roi_variance_first`
- `strat_static_align_tuning_loop`
- `strat_variance_roi_precedence_over_plaintext_corr`
- `strat_verify_before_declare`

### Action operation-type distribution

| Operation | Count |
|---|---:|
| adjust_param | 109 |
| switch_component | 85 |
| add_step | 60 |
| verify | 19 |
| acquire_more_data | 3 |
| skip_step | 2 |

## Top source papers (upper layer)

| Paper | # relationships sourced |
|---|---:|
| `PAP-17-2010-CHES-Moradi-Collision-Correlation` | 86 |
| `BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese` | 44 |
| `PAP-27-2012-ePrint-Durvaux-Cryptanalysis-Random-Delay` | 40 |
| `PAP-101-2006-CTRSA-Oswald-2ndOrder-DPA-Masked-BlockCipher` | 39 |
| `PAP-77-2023-ePrint-Plaintext-Collision` | 38 |
| `MAN-08-2024-Riscure-Inspector-Tutorials` | 37 |
| `MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated` | 34 |
| `PAP-18-2010-CHES-Moradi-Correlation-Enhanced-Collision` | 28 |
| `BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack` | 26 |
| `MAN-06-2024-MathMagic-Detector-1.7.2-Manual` | 24 |
| `PAP-53-2018-ePrint-GPU-Bitsliced-AES` | 23 |
| `PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene` | 22 |
| `PAP-59-2019-ePrint-SNR-Trace-Extractors` | 22 |
| `THE-01-2022-UCLouvain-Bronchain-Thesis-WorstCase-SCA` | 21 |
| `TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES` | 20 |

## Top source papers (lower layer)

| Paper | # items sourced |
|---|---:|
| `expert_experience` | 47 |
| `PAP-86` | 13 |
| `PAP-21` | 12 |
| `PAP-26` | 12 |
| `PAP-101` | 10 |
| `PAP-15` | 10 |
| `PAP-18` | 10 |
| `STD-06-2024-ISO-IEC-17825-Updated` | 9 |
| `PAP-29` | 8 |
| `PAP-97` | 8 |
| `PAP-16` | 6 |
| `PAP-81` | 6 |
| `MAN-08-2024-Riscure-Inspector-Tutorials` | 6 |

## Neo4j live sanity check

- Total nodes: 1334
- Total edges: 1813
- Canonical Strategies (Neo4j): 21

### Node labels (Neo4j)

| Label | Count |
|---|---:|
| Cause | 278 |
| Action | 278 |
| Observation | 273 |
| Preprocessing | 90 |
| DeviceClass | 83 |
| StatMethod | 75 |
| Countermeasure | 46 |
| Strategy | 43 |
| AttackPoint | 36 |
| DiagnosticMethod | 36 |
| Pipeline | 34 |
| LeakageModel | 26 |
| RecoveryMethod | 12 |
| Algorithm | 10 |
| ValidationMethod | 8 |
| TraceType | 6 |

### Edge types (Neo4j)

| Type | Count |
|---|---:|
| works_with | 603 |
| resolves | 280 |
| indicates | 278 |
| relates_to | 222 |
| consists_of | 137 |
| acquires_via | 86 |
| strategy_applies_to | 80 |
| has_attack_point | 39 |
| precedes | 34 |
| weakens | 30 |
| alternative_to | 24 |

