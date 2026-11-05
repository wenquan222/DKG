# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_045107_018 |
| Duration | 136.6s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\DES-14443_GLM5_DKG_20260424_045107_018` |
| Total LLM Calls | 10 |
| First Round | prompt: 15,155, completion: 1,094 |
| Last Round | prompt: 22,883, completion: 605 |
| Total Tokens | 195,377 (prompt: 190,211, completion: 5,166) |

## 3. User Query

```
帮我对一个非接触式智能卡实现的DES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个非接触式智能卡实现的DES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy'"

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
["DES", "Contactless Smartcard", "EM", "CPA", "Hamming Weight", "S-box Output"]

Parsed Keywords: `["DES", "Contactless Smartcard", "EM", "CPA", "Hamming Weight", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 37333 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (39583 chars, click to expand)</summary>

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

**Search keywords** (6): DES, Contactless Smartcard, EM, CPA, Hamming Weight, S-box Output

**Summary**: 34 upper entities, 29 relationships, 15 diagnostic chains, 13 strategies


## 1. Upper Layer Entities (34)


### Algorithm (3)

- **3DES** — num_rounds=48, key_length=112
- **DES** — num_rounds=16, encryption_mode=ECB, key_length=56
- **SimonsVoss key derivation function (obscurity function O and modified DES)** — num_rounds=8, key_length=128

### AttackPoint (6)

- **Inverse S-box Output** — round=13
- **Masked S-box Output**
- **S-box Output** — required_data=ciphertext, round=last
- **S-box Output and Mask** — required_data=plaintext, round=first
- **S-box output** — round=1
- **S-box outputs** — round=first

### DeviceClass (4)

- **Contact DES Test Card** — category=Smartcard
- **Commercial Contactless Smartcard** — category=Smartcard
- **32-bit implementation** — bus_width=32
- **ASIC implementation of PicoRV32 on Saidoyoki board** — category=ASIC

### LeakageModel (5)

- **Hamming Weight** — requirements=software implementation
- **Hamming Weight (bit-based)** — requirements=bit-based
- **Hamming Weight of transitions**
- **Hamming weight**
- **Hamming weight of fused features**

### Pipeline (8)

- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool

### StatMethod (8)

- **Algebraic System Construction** — type=non_profiled
- **CEMA** — type=non_profiled
- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Generate Hamming weight models for S-box output** — type=non_profiled

## 2. Relationships (29)

- `Algorithm:3DES` —[has_attack_point [source_text=first round S-box output, support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `AttackPoint:S-box output`
- `Algorithm:3DES` —[works_with [source_text=3DES was implemented on the smartcard., support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `DeviceClass:Commercial Contactless Smartcard`
- `Algorithm:3DES` —[strategy_applies_to [source_text=The process to perform a DEMA of the 3DES implementation can be split up into the following steps, applicability=general, source_papers=["PAP-86"]]]→ `Strategy:DEMA on RFID Smartcard - Core Steps`
- `DeviceClass:Contact DES Test Card` —[works_with [source_text=使用该DES卡一阶CPA分析, support_count=1, confidence=0.2, source_papers=["MAN-02-2024-MathMagic-DES-Contact-TestCard-Example"]]]→ `TraceType:Power`
- `DeviceClass:Contact DES Test Card` —[works_with [source_text=接触式DES测试卡测评示例, support_count=1, confidence=0.2, source_papers=["MAN-02-2024-MathMagic-DES-Contact-TestCard-Example"]]]→ `Preprocessing:Known-key Correlation Analysis`
- `DeviceClass:Commercial Contactless Smartcard` —[strategy_applies_to [source_text=filtered with f_lowpass = 8 MHz and f_highpass = 50 kHz, applicability=general, source_papers=["PAP-86"]]]→ `Strategy:Digital Demodulation Filter Preset for DES Interval`
- `DeviceClass:Commercial Contactless Smartcard` —[strategy_applies_to [source_text=The process to perform a DEMA of the 3DES implementation can be split up into the following steps, applicability=general, source_papers=["PAP-86"]]]→ `Strategy:DEMA on RFID Smartcard - Core Steps`
- `DeviceClass:Commercial Contactless Smartcard` —[works_with [source_text=CPA succeeded on the smartcard., support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `StatMethod:CPA`
- `DeviceClass:Commercial Contactless Smartcard` —[works_with [source_text=3DES was implemented on the smartcard., support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `Algorithm:3DES`
- `DeviceClass:Commercial Contactless Smartcard` —[acquires_via [source_text=near-field probe (RF-U 5-2) with amplification, support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `TraceType:EM`
- `DiagnosticMethod:Waveform characteristic observation and implementation prototype judgment` —[consists_of [parameters_note=Judge software round-state vs hardware register-transition leakage, source_text=Waveform characteristic observation and implementation prototype judgment, support_count=1, is_optional=False]]→ `Pipeline:Unified Analysis Process (8 Steps)`
- `DeviceClass:32-bit implementation` —[acquires_via [source_text=A similar attack has also been conducted on a 32-bit implementation, support_count=1, confidence=0.2, source_papers=["PAP-04-2004-CHES-Brier-CPA-Leakage-Model"]]]→ `TraceType:Power`
- `DeviceClass:32-bit implementation` —[works_with [source_text=A similar attack has also been conducted on a 32-bit implementation, support_count=1, confidence=0.2, source_papers=["PAP-04-2004-CHES-Brier-CPA-Leakage-Model"]]]→ `StatMethod:CPA`
- `DeviceClass:32-bit implementation` —[works_with [source_text=A similar attack has also been conducted on a 32-bit implementation, support_count=1, confidence=0.2, source_papers=["PAP-04-2004-CHES-Brier-CPA-Leakage-Model"]]]→ `Algorithm:DES`
- `DeviceClass:ASIC implementation of PicoRV32 on Saidoyoki board` —[works_with [source_text=experimental validation on ASIC implementation of PicoRV32 on Saidoyoki board, support_count=1, confidence=0.2, source_papers=["PAP-81-2024-ePrint-ARCHER-RISC-V"]]]→ `StatMethod:Correlation Attack`
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

## 3. Diagnostic Chains (15)


### Obs: `trace_count` — any
- **Cause** (high): statistical confidence requires a certain number of traces to distinguish the correct key hypothesis from zero correlation
- **Check**: statistical derivation using confidence intervals
- **Action**: use the rule of thumb n = (3.719 / p)^2 to estimate traces needed for confidence level 0.9999, where p is the expected correlation coefficient
  - operation: `adjust_param`
  - target: `trace count`
  - strategy: for |p| ≤ 0.2, this rule provides a good estimate; the constant 3.719 corresponds to z_(1-α/2) for α=0.0001
- **Relates to**: DiagnosticMethod:`Efficiency Analysis`

### Obs: `vulnerability_to_ema` — any
- **Cause** (high): Electromagnetic emanations can be measured and analyzed similarly to power consumption, providing a side channel that leaks information about computations.
- **Action**: Use signal strength reduction (e.g., shielding) and signal information reduction (e.g., randomization) to protect against EMA.
  - operation: `add_step`
  - target: `implementation`
  - strategy: Employ circuit redesign, shielding, physically secured zones, and randomization techniques to reduce compromising signals.

### Obs: `recovered_key_verification` — any
- **Cause** (high): DES key bytes include a parity bit (LSB) that is often ignored or set to zero by encryption software/hardware.
- **Action**: Ignore or zero the least significant bit (parity bit) of each byte when comparing recovered DES key
  - operation: `verify`
  - target: `recovered_key`
  - strategy: When comparing recovered DES key to expected key, ignore or zero the least significant bit (parity bit) of each byte.
- **Relates to**: ValidationMethod:`Key Verification`

### Obs: `attack_feasibility_assessment` — any
- **Cause** (high): Global prediction vector provides theoretical noise-free baseline for feasibility estimation
- **Check**: Simulated attacks showed successful key distinction after ~300-600 traces
- **Action**: Perform simulated attack using global prediction vector before collecting real measurements
  - operation: `add_step`
  - target: `ValidationMethod`
  - strategy: Compute correlation between selected prediction matrix and global prediction vector for increasing N to estimate minimum required traces.
- **Relates to**: DeviceClass:`Simulated Device`

### Obs: `key_byte_distinguishability` — any
- **Cause** (high): Different key bytes (e.g., 0x55 and 0xAA) can have the same Hamming weight, making them indistinguishable if attacking the key directly. The S-box output provides a nonlinear transformation that spreads the Hamming weights, creating a unique signature for each key hypothesis.
- **Action**: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.
  - operation: `switch_component`
  - target: `attack point`
  - strategy: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.

### Obs: `common_mode_noise_and_ground_loops` — any
- **Cause** (high): Differential probes reject common-mode noise and avoid ground loop issues, providing a cleaner measurement of the voltage drop across the shunt resistor.
- **Action**: Use a differential probe for the front end instead of a single-ended probe.
  - operation: `switch_component`
  - target: `probe type`
  - strategy: Use a differential probe for the front end instead of a single-ended probe.

### Obs: `power_supply_noise` — any
- **Cause** (high): Noise on the power supply rail can couple into the measurement and obscure the subtle current variations of the cryptographic operation.
- **Action**: Add capacitors and ferrite beads on the supply side of the shunt resistor to clean the power rail.
  - operation: `add_step`
  - target: `power supply filtering`
  - strategy: Add capacitors and ferrite beads on the supply side of the shunt resistor to clean the power rail.

### Obs: `trace_snr` — any
- **Cause** (high): noise from connected components on the same PCB couples into the power measurement
- **Action**: minimize components on the measurement board and use optocouplers or magnetic couplers to isolate it from the interface board
  - operation: `add_step`
  - target: `measurement setup`
  - strategy: separate the measurement board (with only the target device and measurement circuit) from the interface board (handling PC communication)

### Obs: `trace_noise_and_dc_offset` — any
- **Cause** (high): AC coupling removes DC offset, and a bandwidth limit filter reduces high-frequency noise, making it easier to see the signal of interest.
- **Action**: Set oscilloscope to AC coupling and enable bandwidth limit filter.
  - operation: `adjust_param`
  - target: `oscilloscope settings`
  - strategy: Set oscilloscope to AC coupling and enable bandwidth limit filter.

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

### Obs: `attack_position_selection` — any
- **Cause** (high): The S-box output is a non-linear operation that often exhibits strong leakage in HW model, and is a common target in first-round attacks
- **Check**: Check implementation details for known leakage points
- **Action**: Set the target to 'S-box out' and model to 'HW' for first-round CPA on AES
  - operation: `adjust_param`
  - target: `cpa.target, cpa.model`
  - strategy: Target: S-box out, Model: HW
- **Relates to**: AttackPoint:`S-box Output`

### Obs: `leakage_model_selection` — any
- **Cause** (high): Non-linear operations (e.g., S-box) have stronger power consumption leakage than linear transformations
- **Check**: Compare correlation strength between S-box output and linear operation points
- **Action**: Choose S-box output as intermediate value for CPA or machine learning attacks
  - operation: `switch_component`
  - target: `intermediate_value`
  - strategy: Choose the S-box output (the value after XOR with round key and before linear transformation) as the intermediate value for CPA or machine learning attacks.
- **Relates to**: AttackPoint:`S-box Output`

## 4. Strategies (13)


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

### ⭐ ⚠ [anti_pattern_set] Do NOT treat alignment_avg_correlation as a CPA success metric
- **Trigger**: Any time an alignment tool returns alignment_avg_correlation >= 0.9
- **Rationale**: alignment_avg_correlation measures how well each trace matches the reference template inside the search radius. A stable I/O or protocol peak can match almost perfectly while containing no S-box leakage, so alignment quality and CPA quality are independent signals.
- **Anti-pattern 1**: Report 'alignment_avg_correlation = 0.99, so CPA will succeed' or use alignment metric to decide whether to stop iterating.
  - Why: alignment_avg_correlation measures how stable template matching is across traces; it's a preprocessing quality metric, not a CPA success metric. A high alignment correlation just means traces are synchronized—it says nothing about whether the synchronization point is the leakage point.
  - Correct: CPA success/failure is judged ONLY by gap_pct and high_confidence_count in the CPA tool return value. alignment_avg_correlation is used solely to decide if alignment parameters themselves need tuning (low alignment_avg_correlation = tune max_shift/length/threshold).
- **Applies to**: Preprocessing:Static Alignment

### ⭐ ⚠ [anti_pattern_set] alignment max_shift should start large (300+), not default to small
- **Trigger**: Any static_aligner invocation on smartcard / MCU traces
- **Rationale**: max_shift is the search radius for the reference peak. On smartcards and MCUs the peak jitter is on the order of hundreds of samples; a small radius discards most traces and can leave the true signal outside the window. Starting large costs only computation.
- **Anti-pattern 1**: Set max_shift=80 or 100 on first alignment attempt; when acceptance_rate < 90%, switch alignment method instead of enlarging max_shift.
  - Why: Smartcard waveform offsets routinely reach 300-500 sample points due to I/O jitter and card clock drift. max_shift too small causes >50% of traces to be discarded, and the surviving subset may not capture the real peak offset.
  - Correct: Initial max_shift: at least 300 (smartcard), 150-200 (MCU with stable clock). If acceptance_rate < 90%, FIRST double max_shift (300→600→1000) before considering alternate alignment methods. max_shift too large only costs a bit of compute, max_shift too small costs valid traces permanently.
- **Applies to**: Preprocessing:Static Alignment

### ⭐ 📋 [troubleshooting_checklist] Criteria for selecting an alignment pattern
- **Trigger**: when attempting to align traces before DPA
- **Rationale**: A well-chosen pattern ensures accurate alignment, which is crucial for successful DPA. These criteria help avoid common pitfalls that lead to poor alignment.
- **[rank 1]** if `uniqueness` → Choose a pattern that is unique in the trace, such as a sharp peak or trough, to avoid multiple matches.
- **[rank 2]** if `data dependency` → Prefer patterns that do not depend on intermediate values of the cryptographic algorithm (e.g., key loading operations) to ensure consistent appearance across traces.
- **[rank 3]** if `length` → Avoid overly long patterns; shorter, distinctive patterns often yield better alignment.
- **[rank 4]** if `distance to attacked intermediate value` → If the device uses random dummy operations, select a pattern close to the processing location of the attacked intermediate value to minimize residual misalignment.
- **Applies to**: StatMethod:DPA, Preprocessing:Static Alignment

### ⭐ 📋 [troubleshooting_checklist] Two-stage SAD alignment and grouped attack for non-deterministic MixColumns
- **Trigger**: When traces are not synchronized with the target clock and the MixColumns step has non-deterministic timing, causing misalignment.
- **Rationale**: Non-deterministic timing in the MixColumns step causes misalignment across traces. A two-stage alignment (coarse then fine) corrects for global clock drift, while attacking in groups aligned to each MixColumns word handles the local timing variability within the round.
- **[rank 1]** if `Coarse alignment` → Apply a coarse Sum of Absolute Differences (SAD) filter to get traces roughly aligned.
- **[rank 2]** if `Fine alignment` → Apply a secondary, fine SAD filter aligned to an abrupt current swing (e.g., the start of the MixColumns operation).
- **[rank 3]** if `Attack first MixColumns word` → Perform CPA on the first group of bytes (0, 13, 10, 7) corresponding to the first MixColumns word.
- **[rank 4]** if `Realign for subsequent words` → Realign traces to the start of the next MixColumns word and attack the corresponding byte groups: (4, 1, 14, 11), then (8, 5, 2, 15), then (12, 9, 6, 3).
- **Applies to**: Algorithm:AES, StatMethod:CPA, Preprocessing:Static Alignment

### ⭐ • [canonical_pipeline_principle] key_search found=false is NOT CPA failure — escalate search budget + dual-mode both branches BEFORE pivoting any other dimension
- **Trigger**: Non-profiled CPA on any symmetric block cipher (AES / DES / SM4); at least one prior CPA run (aligned or direct) has yielded high_confidence_count in or above the gray band (AES >= 10/16, DES >= 3/8, SM4 per-round >= 2/4); key_search was invoked once with default or near-default parameters and returned found=false; OR a dual-mode (e.g., linear-HD / S-box_in on contactless AES / DES) attack returned two candidates with per-byte gap_pct == 0
- **Rationale**: key_search with the default budget only covers a few bytes of top-3 combinations. A found=false result therefore means the budget is too small, not that CPA failed; escalating the combination budget and enumerating both dual-mode branches is cheaper than re-running the attack.
- **Content**: [{"principle": "A single key_search returning found=false is NOT sufficient evidence that CPA / alignment / target / leakage model is wrong. Before pivoting ANY other dimension (leakage target, leakage model, preprocessing chain, alignment anchor, target family), the agent MUST escalate the key_search budget along a fixed four-step ladder (combinations, gap_threshold, candidates, dual-mode both-br
- **Applies to**: StatMethod:CPA

### ⭐ • [canonical_pipeline_principle] Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)
- **Trigger**: Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap)
- **Rationale**: The first plaintext/ciphertext correlation band is usually the I/O bus or register write before the round starts. It correlates strongly and aligns cleanly but contains no S-box leakage, so when variance and correlation ROIs are disjoint the variance peak is the encryption body and must be preferred.
- **Content**: [{"principle": "When variance-based ROI exploration and plaintext/ciphertext-correlation analysis disagree on the encryption-region location (disjoint candidate intervals), the agent MUST anchor static_aligner on the VARIANCE-peak region, NOT the first plaintext/ciphertext-correlation band. This is a device-agnostic rule that extends Strategy A's variance-first principle (originally software MCU o
- **Applies to**: StatMethod:CPA, Preprocessing:Static Alignment

### ⭐ • [canonical_pipeline_principle] Software implementation: variance-first ROI exploration before alignment
- **Trigger**: Software cryptographic implementation (any MCU: STM32F1/F4/Cortex/AVR/Arduino; or contact smartcard running software crypto) + non-profiled CPA + direct CPA returns unstable high_confidence_count below empirical_threshold
- **Rationale**: A software trace contains plaintext I/O, key-schedule computation, and the encryption rounds. Only the round body carries S-box leakage, and it shows a distinct per-sample variance increase, so variance-based ROI selection is more reliable than aligning the whole trace first.
- **Content**: [{"principle": "For software cryptographic implementations, when direct CPA does NOT yield stable high-confidence candidates, the agent MUST first perform variance-based / energy-signature ROI exploration (e.g., np.var / np.std over sliding windows) to locate the encryption region, BEFORE deciding alignment intervals or switching leakage targets.", "reason": "Software implementations on MCU/smartc
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

### ⭐ 📋 [troubleshooting_checklist] Decision to perform static alignment based on direct CPA result
- **Trigger**: after first CPA probe (without alignment)
- **Rationale**: Direct CPA can succeed without alignment if the waveform is already focused on the encryption interval. Alignment is only needed when signal is insufficient.
- **[rank 1]** if `high_confidence_count for AES` → if ≥13, skip alignment; if 10-12, enter alignment and multi-strategy; if <10, must align
- **[rank 2]** if `high_confidence_count for DES` → if ≥6, skip alignment; if 5, enter alignment and multi-strategy; if <5, must align
- **[rank 3]** if `high_confidence_count for SM4 per round` → if ≥3, skip alignment; if 2, enter alignment and multi-strategy; if <2, must align
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

### 📋 [troubleshooting_checklist] DEMA on RFID Smartcard - Core Steps
- **Trigger**: when performing a non-invasive EM side-channel attack (DEMA) on an unknown RFID/contactless smartcard
- **Rationale**: This ordered sequence ensures that the basic prerequisites (triggering, alignment, localization) are satisfied before attempting the statistical attack, which is critical for black-box analysis.
- **[rank 1]** if `Find a suitable trigger point` → Identify a stable reference point in the communication protocol to start trace acquisition
- **[rank 2]** if `Align the traces` → Use a short reference pattern and align only the region of interest, especially for asynchronous devices
- **[rank 3]** if `Locate the DES encryption` → Correlate with known plaintext/ciphertext bytes to identify the time interval of the encryption operation
- **[rank 4]** if `Perform the EM analysis` → Apply CPA (or binwise CPA) on the aligned encryption interval to recover the key
- **Applies to**: StatMethod:CPA, Algorithm:3DES, DeviceClass:Commercial Contactless Smartcard

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
All files for this session are stored in: ..\logs\exp3_GLM-5\DES-14443_GLM5_DKG_20260424_045107_018
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\DES-14443_GLM5_DKG_20260424_045107_018/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 15,155→1,094

**🤖 LLM:** 我来帮你对非接触式智能卡的DES电磁侧信道波形进行CPA攻击。让我先观察波形特征，然后按照标准流程进行分析。

## 第一步：波形特征观察

**🔧 → `python_jupyter`**

<details><summary>Code (2093 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy')
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy')

print(f"波形数据形状: {wave.shape}")
print(f"明文数据形状: {plain.shape}")
print(f"密文数据形状: {cipher.shape}")
print(f"波形数据类型: {wave.dtype}")
print(f"波形值范围: [{wave.min():.2f}, {wave.max():.2f}]")
print(f"波形均值: {wave.mean():.2f}, 标准差: {wave.std():.2f}")

# 绘制多条波形观察特征
plt.figure(figsize=(14, 10))

# 子图1：叠加显示多条波形
plt.subplot(2, 2, 1)
for i in range(min(50, wave.shape[0])):
    plt.plot(wave[i], alpha=0.3, linewidth=0.5)
plt.title('50 Traces Overlay')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)

# 子图2：单条波形
plt.subplot(2, 2, 2)
plt.plot(wave[0], linewidth=1)
plt.title('Single Trace (Trace 0)')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)

# 子图3：方差分析（定位加密区域）
plt.subplot(2, 2, 3)
variance = np.var(wave, axis=0)
plt.plot(variance, linewidth=1.5, color='red')
plt.title('Variance Across Traces')
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.grid(True, alpha=0.3)

# 标记方差峰值区域
peak_idx = np.argmax(variance)
plt.axvline(x=peak_idx, color='green', linestyle='--', label=f'Peak at {peak_idx}')
plt.legend()

# 子图4：均值和标准差
plt.subplot(2, 2, 4)
mean_trace = np.mean(wave, axis=0)
std_trace = np.std(wave, axis=0)
plt.plot(mean_trace, linewidth=1.5, label='Mean')
plt.fill_between(range(len(mean_trace)), mean_trace - std_trace, mean_trace + std_trace, alpha=0.3, label='±1 Std')
plt.title('Mean Trace with Std Band')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

print(f"\n方差峰值位置: {peak_idx}")
print(f"方差峰值值: {variance[peak_idx]:.2f}")
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (10000, 300)
明文数据形状: (10000, 8)
密文数据形状: (10000, 8)
波形数据类型: float32
波形值范围: [-141.73, 23.62]
波形均值: -43.27, 标准差: 45.97

方差峰值位置: 146
方差峰值值: 30.15
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1918297499.py:64: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 2 | tokens: 16,107→919

**🔧 → `python_jupyter`**

<details><summary>Code (2133 chars)</summary>

```python
# 检查基线漂移情况
plt.figure(figsize=(14, 8))

# 检查前100个采样点的基线（假设是加密前的静默区）
baseline_region = wave[:, :50]

# 子图1：前50个采样点的多条波形
plt.subplot(2, 2, 1)
for i in range(min(30, wave.shape[0])):
    plt.plot(wave[i, :50], alpha=0.5, linewidth=0.8)
plt.title('First 50 Samples (Baseline Region)')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)

# 子图2：基线区域的均值分布
plt.subplot(2, 2, 2)
baseline_means = np.mean(baseline_region, axis=1)
plt.hist(baseline_means, bins=50, edgecolor='black', alpha=0.7)
plt.title('Distribution of Baseline Means (per trace)')
plt.xlabel('Mean Amplitude')
plt.ylabel('Count')
plt.axvline(x=baseline_means.mean(), color='red', linestyle='--', label=f'Global Mean: {baseline_means.mean():.2f}')
plt.axvline(x=baseline_means.mean() + baseline_means.std(), color='orange', linestyle='--', label=f'±1 Std: {baseline_means.std():.2f}')
plt.axvline(x=baseline_means.mean() - baseline_means.std(), color='orange', linestyle='--')
plt.legend()
plt.grid(True, alpha=0.3)

# 子图3：基线标准差
baseline_stds = np.std(baseline_region, axis=1)
plt.subplot(2, 2, 3)
plt.hist(baseline_stds, bins=50, edgecolor='black', alpha=0.7, color='green')
plt.title('Distribution of Baseline Std (per trace)')
plt.xlabel('Std Amplitude')
plt.ylabel('Count')
plt.axvline(x=baseline_stds.mean(), color='red', linestyle='--', label=f'Mean Std: {baseline_stds.mean():.2f}')
plt.legend()
plt.grid(True, alpha=0.3)

# 子图4：检查是否有明显的trace间DC漂移
plt.subplot(2, 2, 4)
trace_means = np.mean(wave, axis=1)
plt.plot(trace_means[:200], linewidth=1)
plt.title('Per-Trace Mean (First 200 traces)')
plt.xlabel('Trace Index')
plt.ylabel('Mean Amplitude')
plt.grid(True, alpha=0.3)

# 计算基线漂移指标
baseline_drift = baseline_stds.mean()
print(f"\n基线区域统计:")
print(f"基线均值范围: [{baseline_means.min():.2f}, {baseline_means.max():.2f}]")
print(f"基线均值标准差: {baseline_means.std():.2f}")
print(f"基线标准差的均值: {baseline_stds.mean():.2f}")
print(f"\n判断: 基线标准差均值 = {baseline_stds.mean():.2f}")
if baseline_stds.mean() > 5:
    print("→ 存在明显的基线漂移，建议进行垂直对齐")
else:
    print("→ 基线相对稳定，可能不需要垂直对齐")

plt.tight_layout()
plt.savefig('baseline_analysis.png', dpi=150)
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `基线区域统计:
基线均值范围: [-14.83, -2.77]
基线均值标准差: 0.86
基线标准差的均值: 2.06

判断: 基线标准差均值 = 2.06
→ 基线相对稳定，可能不需要垂直对齐
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\370566429.py:63: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 16,970→300

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

**❌ ← `aes_cpa_attack` Error:**

```
CPA Error: plaintext shape expect (n_traces,16), got (10000, 8)
Traceback (most recent call last):
  File "C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1939770603.py", line 10, in <module>
    result = run_aes_cpa(plaintext_npy="F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",wave_npy="F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy",candidates=20,leakage_model="HW",target="S-box_out",bytes_to_test=None,ciphertext_npy=None,corr_mode=None)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "F:\侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/agent/tools\aes_cpa_tool.py", line 236, in run_aes_cpa
    raise ValueError(f"plaintext shape expect (n_traces,16), got {P.shape}")
ValueError: plaintext shape expect (n_traces,16), got (10000, 8)
```


---

### Round 4 | tokens: 17,669→235

**🔧 → `des_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `des_cpa_attack`</b> (2115 chars)</summary>

```
{"recovered_key": "A8C628B4EADAA2E6", "cpa_avg_correlation": 0.0408, "cpa_min_correlation": 0.0373, "n_traces": 10000, "target": "S-box_out", "plot_path": "des_cpa_result_20260424_045314_944862.png", "detail_file": "des_cpa_detail_20260424_045314_944862.json", "per_sbox": [{"sbox": 0, "key": "0x3A", "correlation": 0.03757716827551415, "time_index": 72, "gap_pct": 0.5}, {"sbox": 1, "key": "0x37", "correlation": 0.04408537728676676, "time_index": 229, "gap_pct": 12.5}, {"sbox": 2, "key": "0x37", "correlation": 0.04820766829566469, "time_index": 51, "gap_pct": 16.7}, {"sbox": 3, "key": "0x35", "correlation": 0.037335031910917145, "time_index": 139, "gap_pct": 4.4}, {"sbox": 4, "key": "0x1A", "correlation": 0.041315795611214436, "time_index": 5, "gap_pct": 4.1}, {"sbox": 5, "key": "0x38", "correlation": 0.0380185254128461, "time_index": 117, "gap_pct": 7.4}, {"sbox": 6, "key": "0x16", "correlation": 0.04136191046108054, "time_index": 270, "gap_pct": 9.3}, {"sbox": 7, "key": "0x36", "correlation": 0.03836126236685273, "time_index": 8, "gap_pct": 0.5}], "high_confidence_count": 1, "recovery_assessment": "Only 1/8 sboxes are high-confidence. Treat this as a red band case: revisit interval selection, start position, or target choice. For DES hardware HD (R_xor_LOut), avg_corr 0.05-0.08 can still be normal, so check gap distribution first.", "low_confidence_subkeys": [{"subkey_index": 0, "sbox": 0, "best_key_hex": "0x3A", "top1_top2_gap": 0.004596665604475974}, {"subkey_index": 1, "sb
...(truncated)
```
</details>


![des_cpa_result_20260424_045314_944862.png](./des_cpa_result_20260424_045314_944862.png)


---

### Round 5 | tokens: 18,768→398

**🤖 LLM:** 直接CPA结果很差（high_confidence_count=1/8，avg_corr=0.04），这是典型的非接触式智能卡硬件实现特征。根据知识图谱，对于硬件DES，应该尝试**R_xor_LOut**目标（硬件寄存器转换模型）。

**🔧 → `des_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "target": "R_xor_LOut",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy"
}
```
</details>

<details><summary><b>📋 ← `des_cpa_attack`</b> (1640 chars)</summary>

```
{"recovered_key": "1002324454422688", "cpa_avg_correlation": 0.0647, "cpa_min_correlation": 0.0552, "n_traces": 10000, "target": "R_xor_LOut", "plot_path": "des_cpa_result_20260424_045328_680043.png", "detail_file": "des_cpa_detail_20260424_045328_680043.json", "per_sbox": [{"sbox": 0, "key": "0x18", "correlation": 0.06532909050168481, "time_index": 71, "gap_pct": 37.3}, {"sbox": 1, "key": "0x13", "correlation": 0.0670683319225106, "time_index": 80, "gap_pct": 34.4}, {"sbox": 2, "key": "0x08", "correlation": 0.05685691480249112, "time_index": 81, "gap_pct": 27.3}, {"sbox": 3, "key": "0x08", "correlation": 0.06660892409404137, "time_index": 79, "gap_pct": 28.4}, {"sbox": 4, "key": "0x05", "correlation": 0.06105223181775767, "time_index": 78, "gap_pct": 33.0}, {"sbox": 5, "key": "0x32", "correlation": 0.08301818706588436, "time_index": 81, "gap_pct": 43.6}, {"sbox": 6, "key": "0x2B", "correlation": 0.06231637119273267, "time_index": 82, "gap_pct": 13.8}, {"sbox": 7, "key": "0x02", "correlation": 0.05516262101644671, "time_index": 83, "gap_pct": 25.6}], "high_confidence_count": 7, "recovery_assessment": "7/8 sboxes high-confidence (gap >= 15%). Only sboxes [6] are unreliable. Run key_search to recover the master key (DES has 16-bit ambiguity from parity + PC-2 unselected bits). Do NOT switch target/method/alignment yet — for DES hardware HD (R_xor_LOut), avg_corr 0.05-0.08 is NORMAL baseline, not a failure signal.", "low_confidence_subkeys": [{"subkey_index": 6, "sbox": 6, "best
...(truncated)
```
</details>


![des_cpa_result_20260424_045328_680043.png](./des_cpa_result_20260424_045328_680043.png)


---

### Round 6 | tokens: 19,671→311

**🤖 LLM:** 太好了！使用硬件寄存器转换模型（R_xor_LOut）后，结果显著改善：
- **high_confidence_count = 7/8**（绿色区域）
- avg_corr = 0.0647（硬件DES的正常范围）
- 只有S-box 6的gap较低（13.8%）

现在验证恢复的密钥：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "key_hex": "1002324454422688",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (996 chars)</summary>

```
{"result_hex": "9F98C98B89389CD2", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 19a4073f51fdaea7... → 9F98C98B89389CD2...\n❌ Key verification FAILED — 8/8 ciphertext bytes differ\n   Expected:  F434B0F486FC4A4B\n   Got:       9F98C98B89389CD2\n\n   ⚠️ IMPORTANT: '8 ciphertext bytes differ' does NOT mean '8 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 7 | tokens: 20,207→370

**🤖 LLM:** 验证失败，但这是正常的。根据策略，在绿色区域（7/8高置信度）+ MISMATCH的情况下，应该使用key_search搜索正确的密钥：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "recovered_key_hex": "1002324454422688",
  "cpa_detail_file": "des_cpa_detail_20260424_045328_680043.json",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 30,
  "max_combinations": 100000
}
```
</details>

<details><summary><b>📋 ← `key_search`</b> (1381 chars)</summary>

```
{"found": true, "correct_key": "1022324454667688", "search_rounds": 245, "total_search_space": 5120, "sbox_analysis": [{"sbox": 0, "gap": 0.3731, "reliable": true, "top1": 24, "candidates": [24, 55, 34, 23, 37, 8, 46, 32, 14, 38, 58, 7, 28, 26, 20, 13, 57, 62, 0, 27]}, {"sbox": 1, "gap": 0.3439, "reliable": true, "top1": 19, "candidates": [19, 32, 51, 3, 7, 58, 60, 17, 27, 44, 23, 50, 47, 53, 42, 54, 13, 29, 30, 8]}, {"sbox": 2, "gap": 0.2734, "reliable": true, "top1": 8, "candidates": [8, 60, 26, 52, 63, 10, 38, 44, 22, 31, 43, 35, 49, 13, 62, 59, 37, 9, 56, 34]}, {"sbox": 3, "gap": 0.2842, "reliable": true, "top1": 8, "candidates": [8, 26, 19, 45, 58, 32, 2, 31, 5, 34, 55, 11, 37, 18, 28, 53, 0, 20, 4, 47]}, {"sbox": 4, "gap": 0.3303, "reliable": true, "top1": 5, "candidates": [5, 42, 32, 7, 1, 36, 62, 26, 30, 10, 18, 22, 6, 60, 54, 41, 8, 44, 46, 33]}, {"sbox": 5, "gap": 0.4355, "reliable": true, "top1": 50, "candidates": [50, 48, 12, 26, 18, 46, 7, 54, 58, 24, 40, 5, 36, 23, 51, 62, 43, 37, 53, 4]}, {"sbox": 6, "gap": 0.1384, "reliable": false, "top1": 43, "candidates": [43, 31, 41, 39, 52, 58, 28, 0, 3, 32, 14, 53, 19, 13, 35, 44, 16, 2, 46, 15]}, {"sbox": 7, "gap": 0.2559, "reliable": true, "top1": 2, "candidates": [2, 13, 28, 29, 6, 60, 7, 34, 15, 17, 3, 27, 54, 0, 24, 4, 8, 56, 10, 9]}], "message": "DES key found after 245 searches: 1022324454667688"}
```
</details>


---

### Round 8 | tokens: 21,257→200

**🤖 LLM:** 太好了！key_search成功找到了正确的密钥！让我验证一下：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy",
  "key_hex": "1022324454667688",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "trace_index": 0
}
```
</details>

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "F434B0F486FC4A4B", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 19a4073f51fdaea7... → F434B0F486FC4A4B...\n✅ Key verification PASSED — all 8 bytes match."}`


---

### Round 9 | tokens: 21,524→734

**🤖 LLM:** ## ✅ 攻击成功！

成功恢复了非接触式智能卡DES算法的密钥。让我总结整个攻击过程：

**🔧 → `python_jupyter`**

<details><summary>Code (1528 chars)</summary>

```python
import json

# 读取CPA详细结果
with open('des_cpa_detail_20260424_045328_680043.json', 'r') as f:
    cpa_detail = json.load(f)

print("=" * 70)
print("DES-64 非接触式智能卡 EM侧信道 CPA攻击结果总结")
print("=" * 70)

print("\n【数据集信息】")
print(f"  波形数量: 10,000 traces")
print(f"  采样点数: 300 points")
print(f"  设备类型: 非接触式智能卡 (Contactless Smartcard)")
print(f"  采集方式: 电磁侧信道 (EM)")

print("\n【攻击策略】")
print(f"  ✓ 第一步: 直接CPA (S-box_out + HW) → 失败 (high_confidence=1/8)")
print(f"  ✓ 第二步: 切换硬件模型 (R_xor_LOut + HW) → 成功 (high_confidence=7/8)")
print(f"  ✓ 第三步: key_search搜索 → 找到正确密钥")

print("\n【恢复的密钥】")
print(f"  最终密钥: 1022324454667688")
print(f"  验证状态: ✅ MATCH (密钥正确)")

print("\n【CPA性能指标】")
print(f"  平均相关系数: 0.0647")
print(f"  最小相关系数: 0.0552")
print(f"  高置信度S-box数: 7/8")
print(f"  低置信度S-box: S-box 6 (gap=13.8%)")

print("\n【各S-box详情】")
print(f"  S-box | Key  | Corr   | Gap%  | Status")
print(f"  ------|------|--------|-------|--------")
for sbox_info in cpa_detail['per_sbox']:
    status = "✓ High" if sbox_info['gap_pct'] >= 15 else "⚠ Low"
    print(f"    {sbox_info['sbox']}   | 0x{sbox_info['key'][2:]:>2s} | {sbox_info['correlation']:.4f} | {sbox_info['gap_pct']:5.1f} | {status}")

print("\n【关键发现】")
print(f"  1. 非接触式智能卡DES实现属于硬件寄存器转换模型")
print(f"  2. R_xor_LOut目标比S-box_out更适合硬件实现")
print(f"  3. 相关系数0.06-0.08是硬件DES的正常范围")
print(f"  4. key_search成功修正了S-box 6的错误候选")

print("\n【攻击成功要素】")
print(f"  ✓ 正确识别硬件实现类型")
print(f"  ✓ 选择合适的泄漏模型 (R_xor_LOut)")
print(f"  ✓ 使用key_search修正低置信度字节")
print(f"  ✓ 充足的trace数量 (10,000 traces)")

print("=" * 70)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1329 chars)</summary>

```
======================================================================
DES-64 非接触式智能卡 EM侧信道 CPA攻击结果总结
======================================================================

【数据集信息】
  波形数量: 10,000 traces
  采样点数: 300 points
  设备类型: 非接触式智能卡 (Contactless Smartcard)
  采集方式: 电磁侧信道 (EM)

【攻击策略】
  ✓ 第一步: 直接CPA (S-box_out + HW) → 失败 (high_confidence=1/8)
  ✓ 第二步: 切换硬件模型 (R_xor_LOut + HW) → 成功 (high_confidence=7/8)
  ✓ 第三步: key_search搜索 → 找到正确密钥

【恢复的密钥】
  最终密钥: 1022324454667688
  验证状态: ✅ MATCH (密钥正确)

【CPA性能指标】
  平均相关系数: 0.0647
  最小相关系数: 0.0552
  高置信度S-box数: 7/8
  低置信度S-box: S-box 6 (gap=13.8%)

【各S-box详情】
  S-box | Key  | Corr   | Gap%  | Status
  ------|------|--------|-------|--------
    0   | 0x18 | 0.0653 |  37.3 | ✓ High
    1   | 0x13 | 0.0671 |  34.4 | ✓ High
    2   | 0x08 | 0.0569 |  27.3 | ✓ High
    3   | 0x08 | 0.0666 |  28.4 | ✓ High
    4   | 0x05 | 0.0611 |  33.0 | ✓ High
    5   | 0x32 | 0.0830 |  43.6 | ✓ High
    6   | 0x2B | 0.0623 |  13.8 | ⚠ Low
    7   | 0x02 | 0.0552 |  25.6 | ✓ High

【关键发现】
  1. 非接触式智能卡DES实现属于硬件寄存器转换模型
  2. R_xor_LOut目标比S-box_out更适合硬件实现
  3. 相关系数0.06-0.08是硬件DES的正常范围
  4. key_search成功修正了S-box 6的错误候选

【攻击成功要素】
  ✓ 正确识别硬件实现类型
  ✓ 选择合适的泄漏模型 (R_xor_LOut)
  ✓ 使用key_search修正低置信度字节
  ✓ 充足的trace数量 (10,000 traces)
======================================================================
```
</details>


---

### Round 10 | tokens: 22,883→605

**🤖 LLM:** ## 🎯 攻击总结

成功对非接触式智能卡DES算法进行了CPA攻击，完整流程如下：

### 攻击过程

1. **波形特征分析**
   - 10,000条EM波形，300个采样点
   - 方差峰值在sample 146（加密区域）
   - 基线稳定，无需垂直对齐

2. **第一次CPA（软件模型）**
   - 目标：S-box_out + HW
   - 结果：❌ 失败（high_confidence=1/8，avg_corr=0.04）

3. **第二次CPA（硬件模型）**
   - 目标：**R_xor_LOut + HW**（硬件寄存器转换）
   - 结果：✅ 成功（high_confidence=7/8，avg_corr=0.0647）

4. **密钥搜索与验证**
   - key_search搜索245次组合
   - 最终密钥：**1022324454667688**
   - 验证：✅ **MATCH**

### 关键经验

1. **硬件实现识别**：非接触式智能卡DES通常使用硬件寄存器转换模型，R_xor_LOut比S-box_out更有效

2. **相关系数范围**：硬件DES的avg_corr在0.05-0.08是正常范围，不代表失败

3. **key_search策略**：在绿色区域（≥6/8高置信度）+ MISMATCH时，应使用key_search而非重新对齐或切换模型

4. **知识图谱指导**：KG提供的硬件模型建议（R_xor_LOut）是攻击成功的关键

攻击成功！🎉


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 15,155 | 1,094 | 16,249 |
| 2 | 16,107 | 919 | 17,026 |
| 3 | 16,970 | 300 | 17,270 |
| 4 | 17,669 | 235 | 17,904 |
| 5 | 18,768 | 398 | 19,166 |
| 6 | 19,671 | 311 | 19,982 |
| 7 | 20,207 | 370 | 20,577 |
| 8 | 21,257 | 200 | 21,457 |
| 9 | 21,524 | 734 | 22,258 |
| 10 | 22,883 | 605 | 23,488 |
| **Total** | **190,211** | **5,166** | **195,377** |

## 8. Final Output

## 🎯 攻击总结

成功对非接触式智能卡DES算法进行了CPA攻击，完整流程如下：

### 攻击过程

1. **波形特征分析**
   - 10,000条EM波形，300个采样点
   - 方差峰值在sample 146（加密区域）
   - 基线稳定，无需垂直对齐

2. **第一次CPA（软件模型）**
   - 目标：S-box_out + HW
   - 结果：❌ 失败（high_confidence=1/8，avg_corr=0.04）

3. **第二次CPA（硬件模型）**
   - 目标：**R_xor_LOut + HW**（硬件寄存器转换）
   - 结果：✅ 成功（high_confidence=7/8，avg_corr=0.0647）

4. **密钥搜索与验证**
   - key_search搜索245次组合
   - 最终密钥：**1022324454667688**
   - 验证：✅ **MATCH**

### 关键经验

1. **硬件实现识别**：非接触式智能卡DES通常使用硬件寄存器转换模型，R_xor_LOut比S-box_out更有效

2. **相关系数范围**：硬件DES的avg_corr在0.05-0.08是正常范围，不代表失败

3. **key_search策略**：在绿色区域（≥6/8高置信度）+ MISMATCH时，应使用key_search而非重新对齐或切换模型

4. **知识图谱指导**：KG提供的硬件模型建议（R_xor_LOut）是攻击成功的关键

攻击成功！🎉
