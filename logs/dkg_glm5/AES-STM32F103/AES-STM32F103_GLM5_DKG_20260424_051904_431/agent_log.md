# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_051904_431 |
| Duration | 143.3s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-STM32F103_GLM5_DKG_20260424_051904_431` |
| Total LLM Calls | 11 |
| First Round | prompt: 14,413, completion: 594 |
| Last Round | prompt: 23,600, completion: 699 |
| Total Tokens | 214,992 (prompt: 209,209, completion: 5,783) |

## 3. User Query

```
帮我对一个STM32F103 MCU软件实现的AES密码算法波形进行CPA恢复密钥，明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个STM32F103 MCU软件实现的AES密码算法波形进行CPA恢复密钥，明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy'"

## Output rules (strict)

Return ONLY a JSON array of keyword strings. **At most 10 keywords.** No commentary.

Extraction principle — pick keywords that **uniquely identify the concrete attack scenario**, not generic SCA vocabulary:
1. The specific algorithm mentioned (e.g., `AES` / `DES` / `SM4`)
2. The specific device / platform mentioned (e.g., `STM32F103` / `FPGA` / `Contact Smartcard`)
3. The specific trace type if stated (e.g., `Power` / `EM`)
4. At most 2-3 method keywords drawn from user's wording (e.g., if user explicitly says "correlation power analysis", add `CPA`; if user says "masked implementation", add `Masking`)
5. Only add 1-2 task-diagnostic keywords if the request describes a specific failure mode (e.g., "my alignment acceptance is low" → `alignment acceptance`)

## What NOT to include

- Do NOT repeat synonyms (pick one: "HW" OR "Hamming Weight", not both)
- Do NOT add generic catch-all keywords like "CPA failure", "troubleshooting checklist", "failure diagnosis", "parameter preset" unless the user explicitly asks for them — the KG retriever will pull relevant diagnostic/strategy nodes via cross-layer links from the concrete entities above
- Do NOT add pipeline-meta terms like "unified analysis", "8-step process", "methodology", "multi-strategy" — these match too many Pipeline nodes
- Do NOT list every entity type's example exhaustively

## Good examples

User: "CPA on STM32F103 software AES, power traces"
→ `["AES", "STM32F103", "MCU", "Power", "CPA", "Hamming Weight", "S-box Output"]`   (7 keywords)

User: "FPGA AES hardware attack, contactless EM"
→ `["AES", "FPGA", "EM", "Contactless", "CPA", "Hamming Distance"]`   (6 keywords)

User: "DES analysis on smartcard, my alignment keeps dropping traces"
→ `["DES", "Smartcard", "Static Alignment", "alignment acceptance"]`   (4 keywords)

```
</details>

LLM Response: json
["AES", "STM32F103", "MCU", "CPA", "Hamming Weight", "S-box Output"]

Parsed Keywords: `["AES", "STM32F103", "MCU", "CPA", "Hamming Weight", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 32351 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (34609 chars, click to expand)</summary>

```
You are an expert in side-channel analysis (SCA), specialized in power analysis attacks such as CPA and DPA.

**[Knowledge from Graph]**
The following is raw knowledge from the DKG knowledge graph. 
IMPORTANT: This knowledge is for REFERENCE ONLY — it may be incomplete, inaccurate for your specific scenario, or based on different devices/datasets. 
You MUST apply your own SCA expertise to:
- Evaluate whether each suggestion is appropriate for this specific case
- Adapt parameters based on actual waveform characteristics you observe
- Make independent decisions when KG knowledge conflicts with your analysis
Do not blindly follow KG recommendations without verifying they apply to the current data.

# DKG Retrieval Results

**Search keywords** (6): AES, STM32F103, MCU, CPA, Hamming Weight, S-box Output

**Summary**: 34 upper entities, 24 relationships, 10 diagnostic chains, 11 strategies


## 1. Upper Layer Entities (34)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### AttackPoint (6)

- **Inverse S-box Output** — round=13
- **Masked S-box Output**
- **S-box Output** — required_data=ciphertext, round=last
- **S-box Output and Mask** — required_data=plaintext, round=first
- **S-box output** — round=1
- **S-box outputs** — round=first

### DeviceClass (11)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **32-bit STM Controller** — category=MCU, bus_width=32
- **32-bit STM microcontroller** — category=MCU, bus_width=32
- **8-bit AVR microcontroller** — category=MCU, bus_width=8
- **8-bit Atmel AVR microcontroller** — category=MCU, bus_width=8
- **8-bit Microcontroller** — category=MCU, bus_width=8
- **8-bit microcontroller** — category=MCU, bus_width=8
- **8-bit microcontroller (ASCAD dataset)** — category=MCU
- **8051 compatible microcontroller** — implementation_type=software, category=MCU

### LeakageModel (5)

- **Hamming Weight** — requirements=software implementation
- **Hamming Weight (bit-based)** — requirements=bit-based
- **Hamming Weight of transitions**
- **Hamming weight**
- **Hamming weight of fused features**

### Pipeline (5)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

### StatMethod (6)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Generate Hamming weight models for S-box output** — type=non_profiled

## 2. Relationships (24)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: XOR operation output, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `AttackPoint:XOR operation output`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
- `DeviceClass:32-bit STM Controller` —[works_with [source_text=CHES CTF ... AutoPOI ... 1830, support_count=1, confidence=0.2, source_papers=["PAP-74-2023-ePrint-AutoPOI"]]]→ `Algorithm:AES`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Preprocessing:Resampling`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Pipeline:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `StatMethod:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `LeakageModel:identity`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use non-encryption flat region as reference, condition=when baseline drift is visible (e.g., non-contact EM, FPGA/ASIC), source_text=Vertical alignment, support_count=1]]→ `Preprocessing:Vertical alignment`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Reference peak must be inside candidate interval, set max_shift based on actual peak position variation, condition=only if first CPA falls in gray/red band (high_confidence_count below threshold), source_text=Static alignment, support_count=1]]→ `Preprocessing:Static alignment`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=If verification fails, use key_search with merged CPA details, condition=requires plaintext and ciphertext, source_text=Key verification and recovery, support_count=1]]→ `ValidationMethod:Key verification and recovery`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use conservative candidates, consider merging multiple CPA results if needed, condition=after optional alignment steps, source_text=Full CPA, support_count=1]]→ `StatMethod:Full CPA`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use conservative candidates (10-20), read gap_pct and high_confidence_count, condition=direct CPA probe to decide whether alignment is needed, source_text=First CPA probe (without alignment), support_count=1]]→ `StatMethod:First CPA probe (without alignment)`
- `StatMethod:Generate Hamming weight models for S-box output` —[consists_of [parameters_note=models are lookup tables for the leakage of each possible S-box output, source_text=Generate Hamming weight models for S-box output, support_count=1, is_optional=False]]→ `Pipeline:SCALib CPA Attack on AES`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Avoid using the identity model for bijective S-boxes in MIA; use a non-bijective model (e.g., Hamming weight) or target a non-bijective intermediate value (e.g., predict only a subset of bits).`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:try different power models (bit, Hamming weight, Hamming distance, zero-value) to see which yields the highest and most distinct peak for a single key hypothesis`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:use the Hamming weight model for microcontrollers with precharged buses`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Use a non-injective leakage function that incurs information loss (e.g., Hamming weight, LSB, MSB).`
- `AttackPoint:S-box Output` —[strategy_applies_to [source=expert_experience, condition=Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear, applicability=specific]]→ `Strategy:Do NOT switch leakage target family as first response to low correlation on software implementations`
- `AttackPoint:Inverse S-box Output` —[has_attack_point [source_text=attack_point: Inverse S-box Output, round: 14, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[has_attack_point [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[works_with [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`

## 3. Diagnostic Chains (10)


### Obs: `attack_position_selection` — any
- **Cause** (high): The S-box output is a non-linear operation that often exhibits strong leakage in HW model, and is a common target in first-round attacks
- **Check**: Check implementation details for known leakage points
- **Action**: Set the target to 'S-box out' and model to 'HW' for first-round CPA on AES
  - operation: `adjust_param`
  - target: `cpa.target, cpa.model`
  - strategy: Target: S-box out, Model: HW
- **Relates to**: StatMethod:`CPA`
- **Alternatives**: DPA, Difference of Means

### Obs: `encryption_interval_visibility` — any
- **Cause** (high): Without a dedicated trigger, the encryption operation is buried in a long trace. Low-frequency noise and irrelevant operations obscure the pattern.
- **Action**: Capture long low-rate trace, filter, look for repeating patterns
  - operation: `add_step`
  - target: `preprocessing`
  - strategy: First capture a long trace at a lower sampling rate (e.g., 12.5 MSa/s). Apply a low-pass filter (e.g., moving average) to smooth the trace. Look for repeating patterns (e.g., 9 similar rounds for AES).
- **Relates to**: Preprocessing:`Low-pass Filter`
- **Alternatives**: Bandpass filtering

### Obs: `trace_alignment_reference` — any
- **Cause** (high): Random delays inserted between operations cause the same operation to appear at different sample indices in different traces, making direct averaging impossible.
- **Action**: Filter traces and use repeating pattern as alignment reference
  - operation: `add_step`
  - target: `preprocessing`
  - strategy: Apply a low-pass filter to the traces. The filtered traces will show 16 similar intervals (for AES S-boxes). Use the first such interval as a reference pattern for alignment.
- **Relates to**: Preprocessing:`Static Alignment`

### Obs: `filter_weight_selection` — any
- **Cause** (high): Software implementations have clear signal; too high weight distorts signal and reduces CPA success. Hardware implementations generally do not require filtering.
- **Action**: Use weight 2-3 for software implementations (smartcard, MCU). Use no filter for hardware implementations (FPGA, ASIC).
  - operation: `adjust_param`
  - target: `filter.weight`
  - strategy: Start with small filter weights (2-3) for software; if uncertain, try no filter.
- **Relates to**: Preprocessing:`Low-pass Filter`
- **Alternatives**: Bandpass filtering

### Obs: `cpa_avg_correlation` — attacking S-box output on a microcontroller
- **Cause** (high): microcontroller uses a precharged bus, making power consumption inversely proportional to the Hamming weight of the data being processed
- **Check**: comparison of DPA results using different power models
- **Action**: use the Hamming weight model for microcontrollers with precharged buses
  - operation: `switch_component`
  - target: `power model`
  - strategy: instead of bit model, model power as HW(value) for such devices
- **Relates to**: LeakageModel:`Hamming Weight`
- **Alternatives**: Identity

### Obs: `cpa_avg_correlation` — attacking last-round S-box input on an ASIC
- **Cause** (high): hardware implementations often have registers where power depends on the Hamming distance between successive values, or S-boxes consume less power for zero inputs
- **Check**: comparison of DPA results using different power models on an AES ASIC
- **Action**: try Hamming distance model (for register transitions) or zero-value model (for S-boxes with low power at zero) for hardware implementations
  - operation: `switch_component`
  - target: `power model`
  - strategy: Hamming distance model: power ∝ HD(previous value, current value); zero-value model: power is low only when data is zero
- **Relates to**: LeakageModel:`zero value`

### Obs: `cpa_high_confidence_count` — when the power model does not match the device's actual power consumption
- **Cause** (high): the chosen power model (e.g., bit or Hamming weight) does not accurately capture the data-dependent power consumption of the target circuit
- **Check**: simulation of power consumption using annotated netlist shows similar correlations for many key hypotheses
- **Action**: try different power models (bit, Hamming weight, Hamming distance, zero-value) to see which yields the highest and most distinct peak for a single key hypothesis
  - operation: `switch_component`
  - target: `power model`
  - strategy: iteratively test models and select the one that maximizes the difference between the correct key correlation and others
- **Relates to**: LeakageModel:`zero value`

### Obs: `partial_guessing_entropy` — any
- **Cause** (high): PGE indicates the rank of the correct key guess. A low PGE (approaching 1) for a key byte indicates high confidence, while a high PGE indicates low confidence or a wrong attack configuration.
- **Action**: Monitor the PGE for each key byte during CPA. A clear winner (significantly lower PGE than others) indicates a successful attack for that byte.
  - operation: `verify`
  - target: `attack progress`
  - strategy: Monitor the PGE for each key byte during CPA. A clear winner (significantly lower PGE than others) indicates a successful attack for that byte.
- **Relates to**: StatMethod:`CPA`
- **Alternatives**: DPA, Difference of Means

### Obs: `key_byte_distinguishability` — any
- **Cause** (high): Different key bytes (e.g., 0x55 and 0xAA) can have the same Hamming weight, making them indistinguishable if attacking the key directly. The S-box output provides a nonlinear transformation that spreads the Hamming weights, creating a unique signature for each key hypothesis.
- **Action**: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.
  - operation: `switch_component`
  - target: `attack point`
  - strategy: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.

### Obs: `leakage_model_selection` — any
- **Cause** (high): Non-linear operations (e.g., S-box) have stronger power consumption leakage than linear transformations
- **Check**: Compare correlation strength between S-box output and linear operation points
- **Action**: Choose S-box output as intermediate value for CPA or machine learning attacks
  - operation: `switch_component`
  - target: `intermediate_value`
  - strategy: Choose the S-box output (the value after XOR with round key and before linear transformation) as the intermediate value for CPA or machine learning attacks.
- **Relates to**: AttackPoint:`S-box Output`

## 4. Strategies (11)


### ⭐ ⚠ [anti_pattern_set] Software implementations do NOT need vertical alignment by default
- **Trigger**: Software implementation (contact/contactless smartcard, MCU like STM32F1/F4/ARM Cortex) with baseline_std > 0 but no visible per-trace DC drift in the non-encryption region
- **Rationale**: Software implementations draw current through a stable supply network; cyclic noise from the CPU clock appears as a constant DC offset across the whole trace, so subtracting a per-trace baseline removes signal rather than drift. Vertical alignment is needed for hardware implementations, where clock switching produces a per-trace DC shift.
- **Anti-pattern 1**: Apply vertical alignment on software MCU/smartcard solely because baseline_std > 5 or > 10
  - Why: Software implementations naturally have small baseline fluctuations from ADC noise and power-rail coupling; this is NOT DC drift. Vertical alignment subtracts per-trace baseline mean, which can remove genuine low-frequency leakage signal embedded in the baseline and degrade CPA correlation.
  - Correct: Apply vertical alignment ONLY when: (a) the trace is captured from FPGA / ASIC hardware, OR (b) the trace is non-contact EM with visually confirmed per-trace DC shift in the non-encryption region. For a pure software MCU / contact smartcard, skip vertical alignment by default; the baseline noise is not DC drift.
- **Anti-pattern 2**: After vertical alignment, if CPA returns only 2-3/16 high-confidence bytes, continue switching leakage target instead of reverting vertical alignment
  - Why: If vertical alignment is the cause of leakage destruction, switching target/model never recovers; the correct path is to re-run direct CPA on the un-aligned (raw or only-filtered) trace and compare.
  - Correct: When high_confidence_count drops to red band (AES < 10/16 / DES < 5/8 / SM4 per-round < 2/4) AFTER a preprocessing step, try running CPA on the pre-preprocessing trace as a sanity check before switching any attack dimension.
- **Applies to**: Preprocessing:Vertical Alignment

### ⭐ ⚠ [anti_pattern_set] In green-band regime, do NOT re-run preprocessing—use key_search instead
- **Trigger**: high_confidence_count in green band (AES >= 13/16, DES >= 6/8, SM4 per-round >= 3/4) AND encrypt_decrypt_verify returns MISMATCH
- **Rationale**: When high_confidence_count is in the green band, most S-box subkeys are already correct and the remaining errors are top-2/3 confusions. Re-running preprocessing cannot fix those bytes and may damage the ones already recovered; key_search enumerates the small neighbourhood directly.
- **Anti-pattern 1**: After CPA reaches green-band high_confidence_count but verify MISMATCH, re-run static alignment / re-apply filter / switch leakage model to 'fix' it.
  - Why: Green band means 80%+ of bytes are already correct; MISMATCH just means 1-3 bytes need key_search correction. Redoing preprocessing may destroy the already-correct bytes and force restart.
  - Correct: In green band + MISMATCH: ONLY invoke key_search (increase candidates or expand search space over the low-confidence bytes). Do NOT touch alignment/filter/target/model.
- **Applies to**: StatMethod:CPA

### ⭐ ⚠ [anti_pattern_set] Do NOT switch leakage target family as first response to low correlation on software implementations
- **Trigger**: Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear
- **Rationale**: For software implementations the standard leakage model is (S-box_out, HW). A low first-pass correlation is more often caused by a wrong ROI or poor alignment than by a wrong target family, and each target switch costs a full CPA round without improving a misaligned window.
- **Anti-pattern 1**: On a software implementation, switch leakage target from S-box_out to S-box_in / S-box_in_xor_prev_ct / etc. as the first repair after seeing low correlation.
  - Why: Under a fixed implementation prototype, the correlation magnitude is determined primarily by SNR, alignment, and interval selection—switching target within the same family yields nearly identical correlations. Repeatedly switching wastes rounds and can misdirect the agent away from the real root cause.
  - Correct: For software MCU/smartcard, default to S-box_out + HW model and ONLY switch target when there is explicit evidence of implementation-prototype mismatch (e.g., dual-mode k/k^0xFF pattern visible in CPA detail, suggests linear-HD target). First fix alignment and interval; switch target last.
- **Applies to**: AttackPoint:S-box Output, StatMethod:CPA

### ⭐ ⚠ [anti_pattern_set] alignment max_shift should start large (300+), not default to small
- **Trigger**: Any static_aligner invocation on smartcard / MCU traces
- **Rationale**: max_shift is the search radius for the reference peak. On smartcards and MCUs the peak jitter is on the order of hundreds of samples; a small radius discards most traces and can leave the true signal outside the window. Starting large costs only computation.
- **Anti-pattern 1**: Set max_shift=80 or 100 on first alignment attempt; when acceptance_rate < 90%, switch alignment method instead of enlarging max_shift.
  - Why: Smartcard waveform offsets routinely reach 300-500 sample points due to I/O jitter and card clock drift. max_shift too small causes >50% of traces to be discarded, and the surviving subset may not capture the real peak offset.
  - Correct: Initial max_shift: at least 300 (smartcard), 150-200 (MCU with stable clock). If acceptance_rate < 90%, FIRST double max_shift (300→600→1000) before considering alternate alignment methods. max_shift too large only costs a bit of compute, max_shift too small costs valid traces permanently.
- **Applies to**: Preprocessing:Static Alignment

### ⭐ ⚠ [anti_pattern_set] Do NOT treat alignment_avg_correlation as a CPA success metric
- **Trigger**: Any time an alignment tool returns alignment_avg_correlation >= 0.9
- **Rationale**: alignment_avg_correlation measures how well each trace matches the reference template inside the search radius. A stable I/O or protocol peak can match almost perfectly while containing no S-box leakage, so alignment quality and CPA quality are independent signals.
- **Anti-pattern 1**: Report 'alignment_avg_correlation = 0.99, so CPA will succeed' or use alignment metric to decide whether to stop iterating.
  - Why: alignment_avg_correlation measures how stable template matching is across traces; it's a preprocessing quality metric, not a CPA success metric. A high alignment correlation just means traces are synchronized—it says nothing about whether the synchronization point is the leakage point.
  - Correct: CPA success/failure is judged ONLY by gap_pct and high_confidence_count in the CPA tool return value. alignment_avg_correlation is used solely to decide if alignment parameters themselves need tuning (low alignment_avg_correlation = tune max_shift/length/threshold).
- **Applies to**: Preprocessing:Static Alignment

### ⭐ 📋 [troubleshooting_checklist] Two-stage SAD alignment and grouped attack for non-deterministic MixColumns
- **Trigger**: When traces are not synchronized with the target clock and the MixColumns step has non-deterministic timing, causing misalignment.
- **Rationale**: Non-deterministic timing in the MixColumns step causes misalignment across traces. A two-stage alignment (coarse then fine) corrects for global clock drift, while attacking in groups aligned to each MixColumns word handles the local timing variability within the round.
- **[rank 1]** if `Coarse alignment` → Apply a coarse Sum of Absolute Differences (SAD) filter to get traces roughly aligned.
- **[rank 2]** if `Fine alignment` → Apply a secondary, fine SAD filter aligned to an abrupt current swing (e.g., the start of the MixColumns operation).
- **[rank 3]** if `Attack first MixColumns word` → Perform CPA on the first group of bytes (0, 13, 10, 7) corresponding to the first MixColumns word.
- **[rank 4]** if `Realign for subsequent words` → Realign traces to the start of the next MixColumns word and attack the corresponding byte groups: (4, 1, 14, 11), then (8, 5, 2, 15), then (12, 9, 6, 3).
- **Applies to**: Algorithm:AES, StatMethod:CPA, Preprocessing:Static Alignment

### ⭐ ⚙ [parameter_preset_bundle] Static alignment default parameter bundle for contact smartcard AES
- **Trigger**: when performing static alignment on contact smartcard AES traces after candidate interval selection
- **Rationale**: These parameters are used in the example for aligning AES traces from a contact smartcard. The threshold of 85% is a common starting point for accepting aligned traces, and the maximum shift is set to cover the observed shifts. The reference trace is typically the second trace.
- `length` = 100 samples [range 100–120]
- `max_shift` = 400 samples
- `threshold` = 85 percent
- `ref_trace` = 1 index (0-based)
- **Applies to**: Algorithm:AES, Preprocessing:Static Alignment

### ⭐ • [canonical_pipeline_principle] key_search found=false is NOT CPA failure — escalate search budget + dual-mode both branches BEFORE pivoting any other dimension
- **Trigger**: Non-profiled CPA on any symmetric block cipher (AES / DES / SM4); at least one prior CPA run (aligned or direct) has yielded high_confidence_count in or above the gray band (AES >= 10/16, DES >= 3/8, SM4 per-round >= 2/4); key_search was invoked once with default or near-default parameters and returned found=false; OR a dual-mode (e.g., linear-HD / S-box_in on contactless AES / DES) attack returned two candidates with per-byte gap_pct == 0
- **Rationale**: key_search with the default budget only covers a few bytes of top-3 combinations. A found=false result therefore means the budget is too small, not that CPA failed; escalating the combination budget and enumerating both dual-mode branches is cheaper than re-running the attack.
- **Content**: [{"principle": "A single key_search returning found=false is NOT sufficient evidence that CPA / alignment / target / leakage model is wrong. Before pivoting ANY other dimension (leakage target, leakage model, preprocessing chain, alignment anchor, target family), the agent MUST escalate the key_search budget along a fixed four-step ladder (combinations, gap_threshold, candidates, dual-mode both-br
- **Applies to**: StatMethod:CPA

### ⭐ • [canonical_pipeline_principle] Software implementation: variance-first ROI exploration before alignment
- **Trigger**: Software cryptographic implementation (any MCU: STM32F1/F4/Cortex/AVR/Arduino; or contact smartcard running software crypto) + non-profiled CPA + direct CPA returns unstable high_confidence_count below empirical_threshold
- **Rationale**: A software trace contains plaintext I/O, key-schedule computation, and the encryption rounds. Only the round body carries S-box leakage, and it shows a distinct per-sample variance increase, so variance-based ROI selection is more reliable than aligning the whole trace first.
- **Content**: [{"principle": "For software cryptographic implementations, when direct CPA does NOT yield stable high-confidence candidates, the agent MUST first perform variance-based / energy-signature ROI exploration (e.g., np.var / np.std over sliding windows) to locate the encryption region, BEFORE deciding alignment intervals or switching leakage targets.", "reason": "Software implementations on MCU/smartc
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

### ⭐ • [canonical_pipeline_principle] Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)
- **Trigger**: Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap)
- **Rationale**: The first plaintext/ciphertext correlation band is usually the I/O bus or register write before the round starts. It correlates strongly and aligns cleanly but contains no S-box leakage, so when variance and correlation ROIs are disjoint the variance peak is the encryption body and must be preferred.
- **Content**: [{"principle": "When variance-based ROI exploration and plaintext/ciphertext-correlation analysis disagree on the encryption-region location (disjoint candidate intervals), the agent MUST anchor static_aligner on the VARIANCE-peak region, NOT the first plaintext/ciphertext-correlation band. This is a device-agnostic rule that extends Strategy A's variance-first principle (originally software MCU o
- **Applies to**: StatMethod:CPA, Preprocessing:Static Alignment

### 📋 [troubleshooting_checklist] Theoretical prediction of correlation power analysis success rate
- **Trigger**: When planning or evaluating a CPA attack against an FPGA implementation
- **Rationale**: This algorithm provides a statistical prediction of CPA success based on design parameters (number of registers, predictable registers), measurement quality, and trace count. It helps attackers estimate feasibility and defenders evaluate vulnerability.
- **[rank 1]** if `Determine the total number of 1-bit registers in the FPGA design, n.` → Review design specifications or netlist to count registers.
- **[rank 2]** if `Determine the number of predictable and full such registers, m.` → Identify registers after the first non-linear layer (S-boxes) and before diffusion layers. Ensure they are 'full' (leak secret information).
- **[rank 3]** if `Determine the correlation coefficient value, r_{P,G} ≈ √(m/n).` → Recalculate m and n if the approximation seems off (e.g., if diffusion is incomplete).
- **[rank 4]** if `Estimate the measurement quality r_{G,M}. A typical value is 0.5. Use r_{G,M}=1 for simulated data.` → Perform preliminary experiment to measure r_{G,M} by correlating global prediction vector with actual power traces.
- **[rank 5]** if `Determine r_{P,M} = r_{P,G} × r_{G,M}.` → Recalculate previous steps.
- **[rank 6]** if `Determine the number of key guesses g.` → Based on target register size (e.g., 8-bit S-box output gives g=256).
- **[rank 7]** if `Determine the number of measurements (plaintexts) available, N.` → Collect more traces if N is too low for desired success rate.
- **[rank 8]** if `Compute success rate using formula: SR = Φ( (atanh(r_{P,M}) * √(N-3)) / √2 )^g.` → If SR is too low, increase N or improve r_{P,M} (e.g., by targeting more registers or improving measurements).
- **Applies to**: TraceType:EM, StatMethod:CPA

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-STM32F103_GLM5_DKG_20260424_051904_431
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-STM32F103_GLM5_DKG_20260424_051904_431/'` or `'../logs/...'` — just use the bare filename.
- When using file paths in Python code, always use forward slashes (/) or raw strings (r'...').
- Never invent, guess, or modify input file paths. If unsure, use python_jupyter with os.listdir() to check.

**[How to Work]**
- Use your own SCA expertise to plan and execute. The initial knowledge above 
  gives you the attack configuration — algorithm, device type, preprocessing chain.
- Execute step by step based on YOUR judgment of the waveform characteristics.
- Use kg_search ONLY when:
  (1) You encounter an unexpected result (e.g., too many traces discarded, 
      verification failed, correlation too low)
  (2) You are unsure about a specific parameter and want to check best practices
- Do NOT search before every step — trust your own analysis first.
- After each tool call, evaluate the result yourself before deciding next action.

```
</details>

## 6. Execution


---

### Round 1 | tokens: 14,413→594

**🤖 LLM:** 我来帮你对STM32F103 MCU软件实现的AES进行CPA攻击。根据知识图谱，这是软件实现，应该使用S-box Output + Hamming Weight模型。

让我先进行直接CPA探测，评估波形质量：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2994 chars)</summary>

```
{"recovered_key": "11ECD6443566920D5339BBCC4EEEFF00", "cpa_avg_correlation": 0.3177, "cpa_min_correlation": 0.2679, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_052027_738710.png", "detail_file": "cpa_detail_20260424_052027_738710.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3251, "time_index": 586, "gap_pct": 14.4}, {"byte": 1, "key": "0xEC", "correlation": 0.2679, "time_index": 823, "gap_pct": 1.3}, {"byte": 2, "key": "0xD6", "correlation": 0.3516, "time_index": 492, "gap_pct": 21.1}, {"byte": 3, "key": "0x44", "correlation": 0.3574, "time_index": 1038, "gap_pct": 19.1}, {"byte": 4, "key": "0x35", "correlation": 0.2881, "time_index": 168, "gap_pct": 4.2}, {"byte": 5, "key": "0x66", "correlation": 0.3694, "time_index": 823, "gap_pct": 23.8}, {"byte": 6, "key": "0x92", "correlation": 0.3066, "time_index": 91, "gap_pct": 3.9}, {"byte": 7, "key": "0x0D", "correlation": 0.2767, "time_index": 446, "gap_pct": 3.9}, {"byte": 8, "key": "0x53", "correlation": 0.2897, "time_index": 1012, "gap_pct": 0.7}, {"byte": 9, "key": "0x39", "correlation": 0.2711, "time_index": 240, "gap_pct": 2.2}, {"byte": 10, "key": "0xBB", "correlation": 0.3862, "time_index": 913, "gap_pct": 30.6}, {"byte": 11, "key": "0xCC", "correlation": 0.3413, "time_index": 1021, "gap_pct": 11.6}, {"byte": 12, "key": "0x4E", "correlation": 0.27, "time_index": 338, "gap_pct": 1.1}, {"byte": 13, "key": "0xEE", "correlation": 0.333, "time_index": 862, "gap_pct": 21.0}, {"byte
...(truncated)
```
</details>


![cpa_result_20260424_052027_738710.png](./cpa_result_20260424_052027_738710.png)


---

### Round 2 | tokens: 15,945→720

**🤖 LLM:** 直接CPA结果显示只有6/16字节高置信度（红色区域），平均相关系数0.32。根据知识图谱策略，对于软件MCU实现，当直接CPA不稳定时，应该**先进行方差分析定位加密区域**，而不是切换target。

让我进行方差分析找到真正的加密区间：

**🔧 → `python_jupyter`**

<details><summary>Code (1351 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载波形数据
wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')
print(f"波形形状: {wave.shape}")

# 计算每个采样点的方差
variance = np.var(wave, axis=0)

# 绘制方差图
plt.figure(figsize=(14, 5))
plt.plot(variance)
plt.xlabel('Sample Index')
plt.ylabel('Variance')
plt.title('Variance Analysis - AES STM32F103')
plt.grid(True, alpha=0.3)

# 标记方差峰值区域
threshold = np.mean(variance) + 2 * np.std(variance)
peaks = np.where(variance > threshold)[0]
if len(peaks) > 0:
    plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold={threshold:.2f}')
    plt.axvspan(peaks[0], peaks[-1], alpha=0.2, color='red', label=f'High variance region: [{peaks[0]}, {peaks[-1]}]')
    print(f"\n高方差区域: [{peaks[0]}, {peaks[-1]}]")
    print(f"方差峰值位置: {np.argmax(variance)}, 峰值: {np.max(variance):.2f}")

plt.legend()
plt.tight_layout()
plt.savefig('variance_analysis.png', dpi=150)
plt.show()

# 找到方差突增的区域
print("\n方差统计:")
print(f"均值: {np.mean(variance):.4f}")
print(f"标准差: {np.std(variance):.4f}")
print(f"最大值: {np.max(variance):.4f} (位置: {np.argmax(variance)})")

# 滑动窗口分析，找到方差变化最剧烈的区域
window_size = 50
var_diff = np.convolve(variance, np.ones(window_size)/window_size, mode='same')
print(f"\n滑动窗口平均后的方差峰值位置: {np.argmax(var_diff)}")
```
</details>

**📋 ← `python_jupyter`:** `波形形状: (250, 1500)

高方差区域: [401, 1117]
方差峰值位置: 1102, 峰值: 3632.30

方差统计:
均值: 712.3178
标准差: 530.7588
最大值: 3632.2959 (位置: 1102)

滑动窗口平均后的方差峰值位置: 1087
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\807590833.py:31: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 16,661→853

**🤖 LLM:** 方差分析显示高方差区域在**[401, 1117]**，峰值在1102附近。这表明加密操作主要在这个区间。让我查看这个区域的波形特征，选择合适的对齐参考点：

**🔧 → `python_jupyter`**

<details><summary>Code (1641 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载波形
wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')

# 查看方差峰值区域附近的波形（选择中间的trace作为参考）
ref_trace_idx = 125
ref_trace = wave[ref_trace_idx]

# 绘制完整波形和方差峰值区域
fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# 完整波形
axes[0].plot(ref_trace)
axes[0].axvspan(401, 1117, alpha=0.2, color='red', label='High variance region [401-1117]')
axes[0].set_xlabel('Sample Index')
axes[0].set_ylabel('Amplitude')
axes[0].set_title(f'Full Waveform - Trace {ref_trace_idx}')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 方差峰值区域放大（1000-1200，覆盖峰值1102）
zoom_start, zoom_end = 1000, 1200
axes[1].plot(range(zoom_start, zoom_end), ref_trace[zoom_start:zoom_end])
axes[1].set_xlabel('Sample Index')
axes[1].set_ylabel('Amplitude')
axes[1].set_title(f'Zoomed Region [{zoom_start}-{zoom_end}] around variance peak (1102)')
axes[1].grid(True, alpha=0.3)

# 标记一些特征点
peak_in_zoom = 1102 - zoom_start
axes[1].axvline(x=1102, color='r', linestyle='--', alpha=0.5, label='Variance peak at 1102')

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

# 计算该区域的一些统计特征
print(f"方差峰值区域 [1000-1200] 的统计:")
print(f"均值: {np.mean(ref_trace[1000:1200]):.2f}")
print(f"标准差: {np.std(ref_trace[1000:1200]):.2f}")
print(f"最大值: {np.max(ref_trace[1000:1200]):.2f}")
print(f"最小值: {np.min(ref_trace[1000:1200]):.2f}")

# 查看多条trace在该区域的差异
print(f"\n多条trace在峰值区域的差异:")
for i in [0, 50, 100, 125, 150, 200, 249]:
    trace_max_pos = np.argmax(wave[i, 1000:1200]) + 1000
    print(f"Trace {i}: 峰值位置 = {trace_max_pos}")
```
</details>

**📋 ← `python_jupyter`:** `方差峰值区域 [1000-1200] 的统计:
均值: -125.18
标准差: 57.54
最大值: -27.56
最小值: -255.91

多条trace在峰值区域的差异:
Trace 0: 峰值位置 = 1078
Trace 50: 峰值位置 = 1088
Trace 100: 峰值位置 = 1083
Trace 125: 峰值位置 = 1075
Trace 150: 峰值位置 = 1072
Trace 200: 峰值位置 = 1090
Trace 249: 峰值位置 = 1088
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\104069811.py:37: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 4 | tokens: 17,557→454

**🤖 LLM:** 波形分析显示峰值位置偏移范围约18个采样点（1072-1090），相对较小。现在我在方差峰值区域进行静态对齐：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "start": 1080,
  "length": 100,
  "max_shift": 200,
  "threshold": 85,
  "ref_trace": 125,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `static_aligner`</b> (782 chars)</summary>

```
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3046665200.py:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
  ref_trace = len(waves) // 2 if 125 is None else int(125)
{"out_aligned_npy": "aligned_20260424_052117_978456.npy", "plot_path": "align_overlay_20260424_052117_978456.png", "ref_trace_used": 125, "accepted": 250, "discarded": 0, "total": 250, "out_plaintext_npy": "plaintext_aligned_20260424_052117_978456.npy", "plaintext_traces": 250, "out_ciphertext_npy": "ciphertext_aligned_20260424_052117_978456.npy", "ciphertext_traces": 250, "alignment_avg_correlation": 0.9917, "alignment_min_correlation": 0.9491, "acceptance_rate": 1.0}
```
</details>


![align_overlay_20260424_052117_978456.png](./align_overlay_20260424_052117_978456.png)


---

### Round 5 | tokens: 18,107→164

**🤖 LLM:** 对齐非常成功！接受率100%，平均相关系数0.99。现在用对齐后的波形进行CPA：

**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_052117_978456.npy",
  "wave_npy": "aligned_20260424_052117_978456.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2052 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.441, "cpa_min_correlation": 0.3616, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_052126_515414.png", "detail_file": "cpa_detail_20260424_052126_515414.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.4568, "time_index": 582, "gap_pct": 34.4}, {"byte": 1, "key": "0x22", "correlation": 0.3732, "time_index": 633, "gap_pct": 29.4}, {"byte": 2, "key": "0x33", "correlation": 0.3669, "time_index": 923, "gap_pct": 18.2}, {"byte": 3, "key": "0x44", "correlation": 0.4915, "time_index": 1040, "gap_pct": 45.2}, {"byte": 4, "key": "0x55", "correlation": 0.4045, "time_index": 593, "gap_pct": 33.2}, {"byte": 5, "key": "0x66", "correlation": 0.4863, "time_index": 1104, "gap_pct": 40.2}, {"byte": 6, "key": "0x77", "correlation": 0.4919, "time_index": 929, "gap_pct": 42.8}, {"byte": 7, "key": "0x88", "correlation": 0.4071, "time_index": 958, "gap_pct": 19.9}, {"byte": 8, "key": "0x99", "correlation": 0.3979, "time_index": 604, "gap_pct": 33.4}, {"byte": 9, "key": "0xAA", "correlation": 0.4674, "time_index": 830, "gap_pct": 41.6}, {"byte": 10, "key": "0xBB", "correlation": 0.4581, "time_index": 1111, "gap_pct": 29.6}, {"byte": 11, "key": "0xCC", "correlation": 0.4874, "time_index": 995, "gap_pct": 41.5}, {"byte": 12, "key": "0xDD", "correlation": 0.3616, "time_index": 612, "gap_pct": 16.0}, {"byte": 13, "key": "0xEE", "correlation": 0.4692, "time_index": 846, "gap_pct": 39.
...(truncated)
```
</details>


![cpa_result_20260424_052126_515414.png](./cpa_result_20260424_052126_515414.png)


---

### Round 6 | tokens: 19,080→281

**🤖 LLM:** 太棒了！对齐后CPA结果显著改善：
- **高置信度字节：16/16**（绿色区域）
- 平均相关系数：0.441（从0.32提升）
- 恢复密钥：`112233445566778899AABBCCDDEEFF00`

现在验证密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "AES",
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "plaintext_npy": "plaintext_aligned_20260424_052117_978456.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_052117_978456.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "17EAF0DCB9E3BC6F7A83D9F769BFC973", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 17EAF0DCB9E3BC6F7A83D9F769BFC973...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 7 | tokens: 19,378→853

**🤖 LLM:** 🎉 **CPA攻击成功！密钥已恢复并验证通过！**

## 攻击结果总结

### 恢复的密钥
```
112233445566778899AABBCCDDEEFF00
```

### 攻击过程

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | 直接CPA探测 | 6/16字节高置信度，相关系数0.32（红色区域） |
| 2 | 方差分析 | 定位加密区域[401, 1117]，峰值在1102 |
| 3 | 静态对齐 | 接受率100%，平均相关系数0.99 |
| 4 | 对齐后CPA | **16/16字节高置信度**，相关系数0.44（绿色区域） |
| 5 | 密钥验证 | ✅ **MATCH - 验证通过** |

### 关键发现

1. **方差分析至关重要**：直接CPA在完整波形上效果不佳，通过方差分析准确定位了加密操作区域

2. **对齐显著提升效果**：
   - 高置信度字节：6/16 → 16/16
   - 平均相关系数：0.32 → 0.44
   - 所有字节的gap_pct都超过15%

3. **软件实现策略验证**：对于STM32F103 MCU软件实现，S-box Output + Hamming Weight模型是正确的选择，无需切换target

### 各字节恢复详情

所有16个字节都表现出强相关性（0.36-0.49）和显著的gap（16%-45%），表明密钥恢复非常可靠。

**🔧 → `python_jupyter`**

<details><summary>Code (799 chars)</summary>

```python
import json

# 读取CPA详情
with open('cpa_detail_20260424_052126_515414.json', 'r') as f:
    detail = json.load(f)

print("=" * 60)
print("AES-128 密钥恢复结果")
print("=" * 60)
print(f"\n恢复密钥: {detail['recovered_key']}")
print(f"验证状态: ✅ 通过")
print(f"\n各字节详情:")
print("-" * 60)
print(f"{'字节':<6} {'密钥':<6} {'相关系数':<12} {'Gap%':<10} {'时间点':<8}")
print("-" * 60)

for byte_info in detail['per_byte']:
    print(f"{byte_info['byte']:<6} {byte_info['key']:<6} {byte_info['correlation']:<12.4f} {byte_info['gap_pct']:<10.1f} {byte_info['time_index']:<8}")

print("-" * 60)
print(f"\n统计:")
print(f"  平均相关系数: {detail['cpa_avg_correlation']:.4f}")
print(f"  最小相关系数: {detail['cpa_min_correlation']:.4f}")
print(f"  高置信度字节: {detail['high_confidence_count']}/16")
print(f"  使用轨迹数: {detail['n_traces']}")
print("=" * 60)
```
</details>

**❌ ← `python_jupyter` Error:**

```
============================================================
AES-128 密钥恢复结果
============================================================

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[372][39m[32m, line 10[39m
[32m      8[39m [38;5;28mprint[39m([33m"[39m[33mAES-128 密钥恢复结果[39m[33m"[39m)
[32m      9[39m [38;5;28mprint[39m([33m"[39m[33m=[39m[33m"[39m * [32m60[39m)
[32m---> [39m[32m10[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;130;01m\n[39;00m[33m恢复密钥: [39m[38;5;132;01m{[39;00m[43mdetail[49m[43m[[49m[33;43m'[39;49m[33;43mrecovered_key[39;49m[33;43m'[39;49m[43m][49m[38;5;132;01m}[39;00m[33m"[39m)
[32m     11[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m验证状态: ✅ 通过[39m[33m"[39m)
[32m     12[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;130;01m\n[39;00m[33m各字节详情:[39m[33m"[39m)

[31mKeyError[39m: 'recovered_key'
```


---

### Round 8 | tokens: 20,555→401

**🔧 → `python_jupyter`**

<details><summary>Code (998 chars)</summary>

```python
import json

# 读取CPA详情
with open('cpa_detail_20260424_052126_515414.json', 'r') as f:
    detail = json.load(f)

# 查看结构
print("JSON keys:", list(detail.keys())[:10])

# 从per_byte中提取密钥
per_byte = detail['per_byte']
recovered_key = ''.join([byte_info['best_key_hex'].replace('0x', '').upper().zfill(2) for byte_info in per_byte])

print("\n" + "=" * 60)
print("AES-128 密钥恢复结果")
print("=" * 60)
print(f"\n恢复密钥: {recovered_key}")
print(f"验证状态: ✅ 通过")
print(f"\n各字节详情:")
print("-" * 60)
print(f"{'字节':<6} {'密钥':<6} {'相关系数':<12} {'Gap%':<10} {'时间点':<8}")
print("-" * 60)

for byte_info in per_byte:
    print(f"{byte_info['byte_index']:<6} {byte_info['best_key_hex']:<6} {byte_info['best_corr']:<12.4f} {byte_info['gap_pct']:<10.1f} {byte_info['best_time_index']:<8}")

print("-" * 60)
print(f"\n统计:")
print(f"  平均相关系数: {detail['avg_corr']:.4f}")
print(f"  最小相关系数: {detail['min_corr']:.4f}")
print(f"  高置信度字节: {detail['high_confidence_count']}/16")
print(f"  使用轨迹数: {detail['n_traces']}")
print("=" * 60)
```
</details>

**❌ ← `python_jupyter` Error:**

```
JSON keys: ['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results']

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[373][39m[32m, line 11[39m
[32m      8[39m [38;5;28mprint[39m([33m"[39m[33mJSON keys:[39m[33m"[39m, [38;5;28mlist[39m(detail.keys())[:[32m10[39m])
[32m     10[39m [38;5;66;03m# 从per_byte中提取密钥[39;00m
[32m---> [39m[32m11[39m per_byte = [43mdetail[49m[43m[[49m[33;43m'[39;49m[33;43mper_byte[39;49m[33;43m'[39;49m[43m][49m
[32m     12[39m recovered_key = [33m'[39m[33m'[39m.join([byte_info[[33m'[39m[33mbest_key_hex[39m[33m'[39m].replace([33m'[39m[33m0x[39m[33m'[39m, [33m'[39m[33m'[39m).upper().zfill([32m2[39m) [38;5;28;01mfor[39;00m byte_info [38;5;129;01min[39;00m per_byte])
[32m     14[39m [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33m"[39m + [33m"[39m[33m=[39m[33m"[39m * [32m60[39m)

[31mKeyError[39m: 'per_byte'
```


---

### Round 9 | tokens: 21,468→134

**🔧 → `python_jupyter`**

<details><summary>Code (331 chars)</summary>

```python
import json

# 读取CPA详情
with open('cpa_detail_20260424_052126_515414.json', 'r') as f:
    detail = json.load(f)

# 查看完整结构
print("JSON结构:")
for key in detail.keys():
    print(f"  {key}: {type(detail[key])}")

# 查看results的结构
if 'results' in detail:
    print("\nresults[0] 示例:")
    print(json.dumps(detail['results'][0], indent=2))
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (2040 chars)</summary>

```
JSON结构:
  n_traces: <class 'int'>
  n_points: <class 'int'>
  leakage_model: <class 'str'>
  target: <class 'str'>
  corr_mode: <class 'str'>
  results: <class 'list'>

results[0] 示例:
{
  "byte": 0,
  "topK": [
    {
      "key": 17,
      "score": 0.4568002517105698,
      "time_index": 582
    },
    {
      "key": 14,
      "score": 0.2994344748818417,
      "time_index": 1143
    },
    {
      "key": 158,
      "score": 0.2875218433292253,
      "time_index": 1391
    },
    {
      "key": 172,
      "score": 0.2820999589265752,
      "time_index": 1153
    },
    {
      "key": 144,
      "score": 0.28128509173914934,
      "time_index": 1147
    },
    {
      "key": 123,
      "score": 0.27750651154223843,
      "time_index": 1174
    },
    {
      "key": 75,
      "score": 0.2731790227319457,
      "time_index": 885
    },
    {
      "key": 130,
      "score": 0.2684090558485067,
      "time_index": 585
    },
    {
      "key": 113,
      "score": 0.26526300655588575,
      "time_index": 1236
    },
    {
      "key": 210,
      "score": 0.26423513456527825,
      "time_index": 42
    },
    {
      "key": 89,
      "score": 0.2594804090012124,
      "time_index": 172
    },
    {
      "key": 200,
      "score": 0.255651187463612,
      "time_index": 1356
    },
    {
      "key": 53,
      "score": 0.2549330720906369,
      "time_index": 513
    },
    {
      "key": 56,
      "score": 0.2531469569443148,
      "time_index": 1124
    },
    {
      "key": 81,
  
...(truncated)
```
</details>


---

### Round 10 | tokens: 22,445→630

**🔧 → `python_jupyter`**

<details><summary>Code (1517 chars)</summary>

```python
import json

# 读取CPA详情
with open('cpa_detail_20260424_052126_515414.json', 'r') as f:
    detail = json.load(f)

# 从results中提取密钥和统计信息
results = detail['results']
recovered_key = ''.join([f"{r['topK'][0]['key']:02X}" for r in results])

# 计算统计信息
correlations = [r['topK'][0]['score'] for r in results]
time_indices = [r['topK'][0]['time_index'] for r in results]

# 计算gap
gaps = []
for r in results:
    if len(r['topK']) >= 2:
        gap = (r['topK'][0]['score'] - r['topK'][1]['score']) / r['topK'][0]['score'] * 100
        gaps.append(gap)
    else:
        gaps.append(0)

print("=" * 70)
print("AES-128 密钥恢复结果 - STM32F103 MCU软件实现")
print("=" * 70)
print(f"\n恢复密钥: {recovered_key}")
print(f"验证状态: ✅ MATCH - 验证通过")
print(f"\n各字节详情:")
print("-" * 70)
print(f"{'字节':<6} {'密钥':<8} {'相关系数':<12} {'Gap%':<10} {'时间点':<8}")
print("-" * 70)

for i, r in enumerate(results):
    key_hex = f"{r['topK'][0]['key']:02X}"
    corr = r['topK'][0]['score']
    time_idx = r['topK'][0]['time_index']
    gap = gaps[i]
    print(f"{i:<6} 0x{key_hex:<6} {corr:<12.4f} {gap:<10.1f} {time_idx:<8}")

print("-" * 70)
print(f"\n统计信息:")
print(f"  平均相关系数: {sum(correlations)/len(correlations):.4f}")
print(f"  最小相关系数: {min(correlations):.4f}")
print(f"  最大相关系数: {max(correlations):.4f}")
print(f"  平均Gap: {sum(gaps)/len(gaps):.1f}%")
print(f"  高置信度字节 (Gap≥15%): {sum(1 for g in gaps if g >= 15)}/16")
print(f"  使用轨迹数: {detail['n_traces']}")
print(f"  泄漏模型: {detail['leakage_model']}")
print(f"  攻击目标: {detail['target']}")
print("=" * 70)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1503 chars)</summary>

```
======================================================================
AES-128 密钥恢复结果 - STM32F103 MCU软件实现
======================================================================

恢复密钥: 112233445566778899AABBCCDDEEFF00
验证状态: ✅ MATCH - 验证通过

各字节详情:
----------------------------------------------------------------------
字节     密钥       相关系数         Gap%       时间点     
----------------------------------------------------------------------
0      0x11     0.4568       34.4       582     
1      0x22     0.3732       29.4       633     
2      0x33     0.3669       18.2       923     
3      0x44     0.4915       45.2       1040    
4      0x55     0.4045       33.2       593     
5      0x66     0.4863       40.2       1104    
6      0x77     0.4919       42.8       929     
7      0x88     0.4071       19.9       958     
8      0x99     0.3979       33.4       604     
9      0xAA     0.4674       41.6       830     
10     0xBB     0.4581       29.6       1111    
11     0xCC     0.4874       41.5       995     
12     0xDD     0.3616       16.0       612     
13     0xEE     0.4692       39.5       846     
14     0xFF     0.4524       37.6       885     
15     0x00     0.4841       40.6       1002    
----------------------------------------------------------------------

统计信息:
  平均相关系数: 0.4410
  最小相关系数: 0.3616
  最大相关系数: 0.4919
  平均Gap: 33.9%
  高置信度字节 (Gap≥15%): 16/16
  使用轨迹数: 250
  泄漏模型: HW
  攻击目标: S-box_out
===================================================================
...(truncated)
```
</details>


---

### Round 11 | tokens: 23,600→699

<details><summary><b>🤖 LLM Reasoning</b> (1245 chars)</summary>

## 🎉 CPA攻击成功完成！

### 最终结果

**恢复密钥**: `112233445566778899AABBCCDDEEFF00`  
**验证状态**: ✅ **MATCH - 验证通过**

---

### 攻击流程总结

| 阶段 | 操作 | 关键指标 | 改善 |
|------|------|----------|------|
| **初始探测** | 直接CPA（全波形） | 6/16高置信度，ρ=0.32 | - |
| **方差分析** | 定位加密区域 | 发现[401-1117]区间 | 关键步骤 |
| **静态对齐** | 峰值区域对齐 | 接受率100%，ρ=0.99 | ✅ |
| **最终CPA** | 对齐后攻击 | **16/16高置信度，ρ=0.44** | ✅✅ |
| **密钥验证** | 加密验证 | **MATCH** | ✅✅✅ |

---

### 关键技术发现

#### 1. **方差分析的重要性**
- 直接CPA在完整波形上效果不佳（6/16字节）
- 方差分析准确定位了加密操作区域[401-1117]
- 峰值在1102附近，这是真正的S-box泄漏区域

#### 2. **对齐的显著效果**
```
高置信度字节:  6/16 → 16/16  (+167%)
平均相关系数:  0.32 → 0.44  (+38%)
平均Gap:       ~10% → 33.9% (+239%)
```

#### 3. **正确的攻击配置**
- **设备**: STM32F103 MCU（软件实现）
- **泄漏模型**: Hamming Weight (HW)
- **攻击目标**: S-box Output
- **轨迹数量**: 250条

---

### 各字节恢复质量

所有16个字节都表现出**强相关性**和**显著区分度**：

| 指标 | 范围 | 说明 |
|------|------|------|
| 相关系数 | 0.36 - 0.49 | 全部 > 0.35，信号强 |
| Gap百分比 | 16% - 45% | 全部 ≥ 15%，区分度高 |
| 时间分布 | 582 - 1111 | 覆盖整个加密区间 |

**最佳字节**: Byte 3 (0x44) - 相关系数0.49，Gap 45.2%  
**最弱字节**: Byte 12 (0xDD) - 相关系数0.36，Gap 16.0%（仍为高置信度）

---

### 知识图谱策略验证

✅ **软件实现不需要垂直对齐** - 未使用，正确  
✅ **方差优先于明文相关定位** - 成功应用  
✅ **S-box_out + HW模型** - 效果最佳  
✅ **对齐参数选择** - max_shift=200足够覆盖MCU抖动  

本次攻击完美验证了知识图谱中的最佳实践！

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 14,413 | 594 | 15,007 |
| 2 | 15,945 | 720 | 16,665 |
| 3 | 16,661 | 853 | 17,514 |
| 4 | 17,557 | 454 | 18,011 |
| 5 | 18,107 | 164 | 18,271 |
| 6 | 19,080 | 281 | 19,361 |
| 7 | 19,378 | 853 | 20,231 |
| 8 | 20,555 | 401 | 20,956 |
| 9 | 21,468 | 134 | 21,602 |
| 10 | 22,445 | 630 | 23,075 |
| 11 | 23,600 | 699 | 24,299 |
| **Total** | **209,209** | **5,783** | **214,992** |

## 8. Final Output

## 🎉 CPA攻击成功完成！

### 最终结果

**恢复密钥**: `112233445566778899AABBCCDDEEFF00`  
**验证状态**: ✅ **MATCH - 验证通过**

---

### 攻击流程总结

| 阶段 | 操作 | 关键指标 | 改善 |
|------|------|----------|------|
| **初始探测** | 直接CPA（全波形） | 6/16高置信度，ρ=0.32 | - |
| **方差分析** | 定位加密区域 | 发现[401-1117]区间 | 关键步骤 |
| **静态对齐** | 峰值区域对齐 | 接受率100%，ρ=0.99 | ✅ |
| **最终CPA** | 对齐后攻击 | **16/16高置信度，ρ=0.44** | ✅✅ |
| **密钥验证** | 加密验证 | **MATCH** | ✅✅✅ |

---

### 关键技术发现

#### 1. **方差分析的重要性**
- 直接CPA在完整波形上效果不佳（6/16字节）
- 方差分析准确定位了加密操作区域[401-1117]
- 峰值在1102附近，这是真正的S-box泄漏区域

#### 2. **对齐的显著效果**
```
高置信度字节:  6/16 → 16/16  (+167%)
平均相关系数:  0.32 → 0.44  (+38%)
平均Gap:       ~10% → 33.9% (+239%)
```

#### 3. **正确的攻击配置**
- **设备**: STM32F103 MCU（软件实现）
- **泄漏模型**: Hamming Weight (HW)
- **攻击目标**: S-box Output
- **轨迹数量**: 250条

---

### 各字节恢复质量

所有16个字节都表现出**强相关性**和**显著区分度**：

| 指标 | 范围 | 说明 |
|------|------|------|
| 相关系数 | 0.36 - 0.49 | 全部 > 0.35，信号强 |
| Gap百分比 | 16% - 45% | 全部 ≥ 15%，区分度高 |
| 时间分布 | 582 - 1111 | 覆盖整个加密区间 |

**最佳字节**: Byte 3 (0x44) - 相关系数0.49，Gap 45.2%  
**最弱字节**: Byte 12 (0xDD) - 相关系数0.36，Gap 16.0%（仍为高置信度）

---

### 知识图谱策略验证

✅ **软件实现不需要垂直对齐** - 未使用，正确  
✅ **方差优先于明文相关定位** - 成功应用  
✅ **S-box_out + HW模型** - 效果最佳  
✅ **对齐参数选择** - max_shift=200足够覆盖MCU抖动  

本次攻击完美验证了知识图谱中的最佳实践！
