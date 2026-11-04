# DKG Upper Layer Schema: Configuration Space Graph

> Design reference document for upper-layer node types and relationship types. Not loaded by code.

---

## Node Types

### 1. Algorithm

Target symmetric block cipher.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Algorithm name | AES, DES, 3DES, SM4, PRESENT, Camellia, SEED, ARIA, SIMON, SPECK, GIFT, SKINNY, ... |
| key_length | Key length (bit) | 64, 80, 96, 128, 192, 256, ... |
| num_rounds | Total number of rounds | AES-128→10, AES-192→12, AES-256→14, DES→16, 3DES→48, SM4→32, PRESENT→31, ... |
| encryption_mode | Block cipher mode of operation | ECB, CBC, CTR, CFB, OFB, GCM, CCM, ... |

---

### 2. DeviceClass

Target device under attack.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Specific device model | STM32F429, STM32F103, AT89S52, ATmega328P, Sakura-G, Sakura-X, SASEBO-GII, Contact Smartcard, Contactless Smartcard, ... |
| category | Device category | MCU, FPGA, ASIC, Smartcard, SoC |
| implementation_type | Crypto implementation type | software, hardware |
| bus_width | Data bus width (bit) | 8, 16, 32, 64, N/A |

---

### 3. TraceType

Type of side-channel trace.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Trace type | Power, EM, Optical, Acoustic |
| acquisition_method | Acquisition method | shunt resistor, current probe, EM near-field probe, EM far-field probe, camera (rolling shutter), photodetector, microphone, ... |

---

### 4. Countermeasure

Protection mechanism against SCA.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Specific countermeasure name | 1st-order Boolean Masking, 2nd-order Boolean Masking, 3rd-order Boolean Masking, Multiplicative Masking, Arithmetic Masking, Affine Masking, Rotating S-box Masking, Random Dummy Operations, Shuffle, Noise Injection, Power Balancing, Dual-Rail Logic (DRP), Masking + Shuffle, Masking + Noise Injection, ... |
| type | Countermeasure category | masking, hiding_temporal, hiding_amplitude, combined |

---

### 5. AttackPoint

Intermediate value position targeted in the attack.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Attack point name without round info; round is stored separately | S-box Output, S-box Input, AddRoundKey Output, MixColumns Output, SubBytes Output, Key Schedule Output, ... |
| round | Target round | first, last, 1, 2, 3, ..., or any specific round number |
| required_data | Required known data | plaintext, ciphertext, plaintext + previous ciphertext, plaintext + ciphertext, plaintext + IV, ... |

> Naming convention: `name` must NOT include round information. Use `S-box Output` with `round: "first"` rather than `S-box Output (first round)`.

---

### 6. LeakageModel

Power leakage model for statistical analysis.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Model name | Hamming Weight, Hamming Distance, Bit Model, Zero-value Model, Multivariate Gaussian, Linear Regression, ... |
| requirements | Prerequisites for using this model. May include implementation constraints, data requirements, or setup requirements. Stored as free text for now. | single intermediate value, two intermediate values, profiling traces from same device, targets individual bits, software implementation, hardware implementation, ... |

---

### 7. Preprocessing

Trace preprocessing method.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Method name | Static Alignment, Vertical Alignment, Elastic Alignment, Pattern Matching, Time-Frequency Alignment, Lowpass Filter, Bandpass Filter, Highpass Filter, Averaging, Trace Selection, Trace Compression, Downsampling, PCA, LDA, ICA, POI Selection (SOSD), POI Selection (SNR), POI Selection (CPA-based), ... |
| category | Preprocessing category | alignment, denoising, compression, dimensionality_reduction, poi_selection |

> Note: Specific parameters are not node properties. Parameter recommendations should be expressed in the lower-layer `Strategy` node as `parameter_preset_bundle`.

---

### 8. StatMethod

Statistical distinguisher for key recovery.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Method name | DPA, CPA, MIA, 2nd-order CPA, 2nd-order DPA, Collision Attack, Template Attack, Stochastic Attack, CNN Classifier, MLP Classifier, Transformer Classifier, ... |
| type | Method category | non_profiled, profiled, deep_learning |

> Note: This framework primarily supports non_profiled methods (CPA/DPA/MIA and higher-order variants). Profiled and deep_learning types are reserved for future extension.

---

### 9. Pipeline

A named end-to-end analysis flow composed of ordered step-methods.

Pipeline is a canonical methodology node. It describes HOW to conduct an analysis, not a specific measured experiment. A pipeline has a name, a trigger condition, and an ordered sequence of steps linked via the `consists_of` relationship.

Key distinction from specific experiments: Pipeline nodes describe reusable methodologies extracted from expert guides, manuals, and textbooks. They do NOT contribute to `works_with` confidence statistics; those come from specific_experiment records. They serve as reference flows that the agent can follow when starting a new attack.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Pipeline name | Unified Analysis Process (8 Steps), Masked AES Analysis Flow, FPGA HD Validation Flow, ... |
| trigger_condition | When to use this pipeline | free text |
| applicable_scenarios | Typical use cases | free text |
| source | Where this pipeline comes from | expert_experience, paper:XXX, manual:XXX |

> Note: The steps of a pipeline are NOT stored as Pipeline properties. They are linked via the `consists_of` relationship to individual step-method nodes, with `step_order` indicating their sequence.

---

### 10. DiagnosticMethod

Analytical judgment or localization step used to decide the next branch in the attack workflow.

This node type exists to represent control-flow methods that are not naturally modeled as preprocessing or statistical attack methods. Typical examples include implementation prototype judgment, candidate interval selection, plaintext-correlation localization, periodicity inspection, and gap-based CPA quality assessment.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Method name | Implementation Prototype Judgment, Candidate Interval Selection, Plaintext Correlation Localization, Direct CPA Probe Assessment, Gap-Based Quality Assessment, ... |
| purpose | What this diagnostic method decides | implementation_judgment, region_localization, branch_decision, quality_assessment, target_family_check, ... |

---

### 11. ValidationMethod

Method used to validate whether a recovered key candidate is actually correct.

This node type exists because verification is a runtime step in the analysis path, but it is neither a preprocessing transform nor a statistical distinguisher. It covers explicit key checking operations such as encrypt/decrypt verification and related validation protocols.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Validation method name | Encrypt/Decrypt Verify, Dual-Mode Verification, Timing Validation, ... |
| evidence_required | What must be provided to run this validation | plaintext + ciphertext, plaintext only, ciphertext only, timing measurements, ... |

---

### 12. RecoveryMethod

Method used to recover a full usable key from CPA candidates or partially recovered subkeys.

This node type exists because key recovery/search is a post-CPA recovery step, not the distinguisher itself. It covers candidate enumeration, multi-run candidate merging, and algorithm-specific recovery procedures from partial or ambiguous subkeys.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Recovery method name | key_search, Candidate Merge, DES Master-Key Reconstruction, SM4 Round-Key Recovery, ... |
| input_type | What this recovery method consumes conceptually | candidate_pool, cpa_detail_json, partial_subkey, merged_candidates, ... |

---

## Relationship Types

### 1. has_attack_point (Structural)

Algorithm has this attackable intermediate value position.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| is_common | Whether this is the most commonly used attack point for this algorithm | true, false |
| source_papers | List of supporting papers | [Brier2004, Mangard2007, ...] |
| source_text | Original text excerpt from source | free text |

**Direction:** Algorithm → AttackPoint

---

### 2. acquires_via (Structural)

Device is commonly measured via this trace type.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| is_primary | Whether this is the primary acquisition method for this device | true, false |
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** DeviceClass → TraceType

---

### 3. weakens (Causal)

Countermeasure reduces the effectiveness of this attack method.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| severity | How severely the countermeasure affects the attack | high, medium, low |
| bypass_method | Known method to overcome this countermeasure | use 2nd-order CPA, increase trace count, apply elastic alignment, ... |
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** Countermeasure → StatMethod

---

### 4. works_with (Constraint)

Two components can be effectively used together in an attack pipeline.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| confidence | Reliability of this combination | 0.0 - 1.0 |
| condition | Under what condition this combination holds | free text, optional |
| note | Additional performance data, tips, or caveats | free text, optional |
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** Between any two node types

---

### 5. alternative_to (Constraint)

Component A and component B can replace each other within the same dimension.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| condition | Under what condition this substitution is relevant | free text, optional |
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** Bidirectional between nodes of the same type

> Note: Priority or ordering is NOT stored on this relationship. The agent determines which alternative to try first by checking `works_with` confidence for the current scenario at query time.

---

### 6. precedes (Sequential)

Step A should generally be performed before step B in the attack workflow.

Scope clarification: `precedes` expresses cross-pipeline general ordering constraints, for example filtering before alignment, diagnostic judgment before target selection, or verification before recovery escalation. These are universal rules that may hold across many pipelines.

For within-pipeline step ordering, use `consists_of` with `step_order` on a specific Pipeline node instead. `precedes` and `consists_of` are complementary, not redundant.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| is_mandatory | Whether this ordering is mandatory or recommended | true, false |
| condition | Under what condition this ordering applies | free text, optional |
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** Between any upper-layer step-method node types when the ordering is a general rule. Common cases include `Preprocessing → Preprocessing`, `Preprocessing → StatMethod`, `DiagnosticMethod → Preprocessing`, `DiagnosticMethod → StatMethod`, `StatMethod → ValidationMethod`, and `ValidationMethod → RecoveryMethod`.

---

### 7. consists_of (Structural)

Links a Pipeline to each of its constituent steps.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| step_order | Position of this step in the pipeline | 1, 2, 3, ... |
| is_optional | Whether this step can be skipped under certain conditions | true, false |
| condition | Under what condition this step applies or is skipped | free text, optional |
| parameters_note | Short note on parameter guidance specific to this step in this pipeline | free text, optional |
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** Pipeline → Preprocessing, StatMethod, DiagnosticMethod, ValidationMethod, or RecoveryMethod

> Note: The ordering of steps in a Pipeline is captured by the `step_order` property on this relationship, NOT by `precedes`. `precedes` describes a general `A before B` ordering rule across pipelines; `consists_of` describes membership in one specific named pipeline.
