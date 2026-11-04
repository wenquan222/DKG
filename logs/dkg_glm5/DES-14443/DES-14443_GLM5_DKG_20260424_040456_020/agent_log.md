# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_040456_020 |
| Duration | 97.0s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\DES-14443_GLM5_DKG_20260424_040456_020` |
| Total LLM Calls | 9 |
| First Round | prompt: 15,789, completion: 785 |
| Last Round | prompt: 21,872, completion: 470 |
| Total Tokens | 173,440 (prompt: 169,700, completion: 3,740) |

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
["DES", "Contactless Smartcard", "EM", "CPA", "Key Recovery"]

Parsed Keywords: `["DES", "Contactless Smartcard", "EM", "CPA", "Key Recovery"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 40695 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (42945 chars, click to expand)</summary>

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

**Search keywords** (5): DES, Contactless Smartcard, EM, CPA, Key Recovery

**Summary**: 28 upper entities, 25 relationships, 22 diagnostic chains, 14 strategies


## 1. Upper Layer Entities (28)


### Algorithm (3)

- **3DES** — num_rounds=48, key_length=112
- **DES** — num_rounds=16, encryption_mode=ECB, key_length=56
- **SimonsVoss key derivation function (obscurity function O and modified DES)** — num_rounds=8, key_length=128

### DeviceClass (4)

- **Contact DES Test Card** — category=Smartcard
- **Commercial Contactless Smartcard** — category=Smartcard
- **32-bit implementation** — bus_width=32
- **ASIC implementation of PicoRV32 on Saidoyoki board** — category=ASIC

### Pipeline (10)

- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, canonical_source=round1_patch_002, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Generic Side-Channel Attack Pipeline** — source=PAP-13-2009-EUROCRYPT-Standaert-Unified-Framework, trigger_condition=starting a side-channel key recovery attack, applicable_scenarios=general side-channel attacks on cryptographic implementations
- **Single-bit AES Key Recovery** — source=tutorial_lab, trigger_condition=when attacking an AES implementation with a single bit of leakage available, applicable_scenarios=AES implementations where a single bit of the S-box output is leaked (e.g., through power or EM side channels)

### RecoveryMethod (4)

- **Full Key Recovery** — input_type=correlation scores for all bytes
- **Full key recovery** — input_type=partial_subkey_candidates
- **Key Recovery** — input_type=SAT solution
- **Key recovery** — input_type=round keys

### StatMethod (7)

- **Algebraic System Construction** — type=non_profiled
- **CEMA** — type=non_profiled
- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled

## 2. Relationships (25)

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
- `RecoveryMethod:Full Key Recovery` —[consists_of [parameters_note=repeat for all 16 bytes of AES-128 key, source_text=Full Key Recovery, support_count=1, is_optional=False]]→ `Pipeline:CPA Attack on AES Firmware Implementation`
- `RecoveryMethod:Full key recovery` —[relates_to [role=add_step]]→ `Action:Apply key enumeration algorithms`
- `RecoveryMethod:Full key recovery` —[consists_of [parameters_note=repeat for all 8 S-boxes to recover 48-bit round subkey; remaining 8 bits via exhaustive search or analyzing another round, source_text=repeat for all 8 S-boxes to recover 48-bit round subkey, support_count=1, is_optional=False]]→ `Pipeline:Differential Power Analysis (DPA) on DES`
- `Pipeline:Generic Side-Channel Attack Pipeline` —[consists_of [parameters_note=apply statistical test T to compare model/partition with leakages, source_text=Statistical test: apply statistical test T to compare model/partition with leakages, support_count=1, is_optional=False]]→ `StatMethod:Statistical Test`
- `Pipeline:Generic Side-Channel Attack Pipeline` —[consists_of [parameters_note=mapping R transforms leakages, may include filtering, averaging, condition=if leakages and predictions have different number of samples or post-processing needed, source_text=Leakage reduction: mapping R transforms leakages, may include filtering, averaging, support_count=1]]→ `Preprocessing:Leakage Reduction`

## 3. Diagnostic Chains (22)


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

### Obs: `key_recovery_limit` — = 0
- **Cause** (high): key recovery algorithm is disabled
- **Action**: set W to a value greater than 0
  - operation: `adjust_param`
  - target: `key_recovery_limit`
  - strategy: set W (key recovery limit) to a positive integer

### Obs: `trace_count` — any
- **Cause** (high): The attack may succeed with fewer traces than the total captured. Using all traces for analysis is unnecessary if the key is recovered earlier.
- **Check**: Plotting Partial Guessing Entropy (PGE) vs. Traces shows the PGE dropping to zero before the maximum trace count.
- **Action**: Use the PGE vs. Traces plot to determine the minimum number of traces needed for successful key recovery and adjust future capture/analysis accordingly.
  - operation: `adjust_param`
  - target: `trace count for analysis`
  - strategy: Use the PGE vs. Traces plot to identify the point of key recovery and optimize the number of traces captured in subsequent attacks.
- **Relates to**: DiagnosticMethod:`Plot PGE vs. Traces`

### Obs: `cpa_avg_correlation` — no key recovery, low correlation after SAD resynchronization
- **Cause** (high): Jitter during the encryption operation (multiple delays) cannot be corrected by a single global shift (SAD).
- **Check**: CPA still fails after SAD; visual inspection shows residual jitter in the aligned traces.
- **Action**: Replace ResyncSAD with ResyncDTW (Dynamic Time Warp).
  - operation: `switch_component`
  - target: `preprocessing method`
  - strategy: Replace ResyncSAD with ResyncDTW (Dynamic Time Warp). When jitter occurs during the encryption operation (not just at trigger), use DTW instead of SAD for resynchronization.
- **Relates to**: Preprocessing:`ResyncSAD`

### Obs: `attack_execution_time` — any
- **Cause** (high): Conditional leakage averaging can speed up key recovery time but requires more traces
- **Check**: implied by parameter option description
- **Action**: Set condavg = true to use conditional leakage averaging for faster key recovery at the cost of requiring more traces
  - operation: `adjust_param`
  - target: `attack.condavg`
  - strategy: Set condavg = true to use conditional leakage averaging for faster key recovery at the cost of requiring more traces
- **Relates to**: StatMethod:`CPA with conditional averaging`

### Obs: `alignment_discard_rate` — 30-50%
- **Cause** (high): max_shift too small, so only traces with small offset are kept, which are not enough for the second half.
- **Check**: Check peak position variation.
- **Action**: Check peak position variation and set max_shift to the actual range.
  - operation: `adjust_param`
  - target: `alignment.max_shift`
  - strategy: When partial key recovery occurs, check max_shift first.
- **Relates to**: Preprocessing:`Static Alignment`

### Obs: `attack_position_selection` — any
- **Cause** (high): The S-box output is a non-linear operation that often exhibits strong leakage in HW model, and is a common target in first-round attacks
- **Check**: Check implementation details for known leakage points
- **Action**: Set the target to 'S-box out' and model to 'HW' for first-round CPA on AES
  - operation: `adjust_param`
  - target: `cpa.target, cpa.model`
  - strategy: Target: S-box out, Model: HW
- **Relates to**: StatMethod:`CPA`

### Obs: `attack_method_selection` — any
- **Cause** (high): Different methods offer trade-offs in resource usage, noise sensitivity, and result quality
- **Action**: Select method based on priorities: Correlation for best trade-off, Linear Regression for best results (requires ID leakage model), Differential for lower resource usage
  - operation: `adjust_param`
  - target: `attack_method`
  - strategy: Correlation is recommended for general use; Linear Regression yields best results but is resource-intensive; Differential is more noise-sensitive but uses fewer resources.
- **Relates to**: StatMethod:`CPA`

### Obs: `cpa_computation_speed` — any
- **Cause** (high): Direct CPA computes correlation for every sample point across all key guesses, which is computationally heavy when traces have many points (e.g., 8000).
- **Action**: Perform mean CPA over identified leakage interval
  - operation: `adjust_param`
  - target: `analysis_interval`
  - strategy: First perform leakage analysis with known key to identify a small high-leakage interval (e.g., sample index 415). Then compute mean correlation only within that interval for each key guess.
- **Relates to**: StatMethod:`CPA`

### Obs: `stat_method_selection` — any
- **Cause** (high): Pearson correlation is simple, well-understood, and effective without noise estimation
- **Action**: Compute Pearson correlation coefficient between global consumption vector and prediction matrix columns
  - operation: `switch_component`
  - target: `StatMethod`
  - strategy: Use formula r = (E[(P - µ_P)(M - µ_M)]) / (σ_P * σ_M)
- **Relates to**: StatMethod:`CPA`

## 4. Strategies (14)


### ⭐ ⚠ [anti_pattern_set] Software implementations do NOT need vertical alignment by default
- **Trigger**: Software implementation (contact/contactless smartcard, MCU like STM32F1/F4/ARM Cortex) with baseline_std > 0 but no visible per-trace DC drift in the non-encryption region
- **Rationale**: From expert_experience.md L256/L283/L307: software generally does not need vertical alignment; hardware (FPGA/ASIC) usually does. Round 1 KG extraction lost the negative constraint ('software doesn't need') and only kept the positive 'especially for hardware'. This patch restores the negative boundary.
- **Anti-pattern 1**: Apply vertical alignment on software MCU/smartcard solely because baseline_std > 5 or > 10
  - Why: Software implementations naturally have small baseline fluctuations from ADC noise and power-rail coupling; this is NOT DC drift. Vertical alignment subtracts per-trace baseline mean, which can remove genuine low-frequency leakage signal embedded in the baseline and degrade CPA correlation.
  - Correct: Apply vertical alignment ONLY when: (a) the trace is captured from FPGA / ASIC hardware, OR (b) the trace is non-contact EM with visually confirmed per-trace DC shift in the non-encryption region. For a pure software MCU / contact smartcard, skip vertical alignment by default; the baseline noise is not DC drift.
- **Anti-pattern 2**: After vertical alignment, if CPA returns only 2-3/16 high-confidence bytes, continue switching leakage target instead of reverting vertical alignment
  - Why: If vertical alignment is the cause of leakage destruction, switching target/model never recovers; the correct path is to re-run direct CPA on the un-aligned (raw or only-filtered) trace and compare.
  - Correct: When high_confidence_count drops to red band (AES < 10/16 / DES < 5/8 / SM4 per-round < 2/4) AFTER a preprocessing step, try running CPA on the pre-preprocessing trace as a sanity check before switching any attack dimension.
- **Applies to**: Preprocessing:Vertical Alignment

### ⭐ ⚠ [anti_pattern_set] In green-band regime, do NOT re-run preprocessing—use key_search instead
- **Trigger**: high_confidence_count in green band (AES >= 13/16, DES >= 6/8, SM4 per-round >= 3/4) AND encrypt_decrypt_verify returns MISMATCH
- **Rationale**: From expert_experience.md L416/L831: gap 高时不要换 target / 对齐 / 滤波 / leakage_model
- **Anti-pattern 1**: After CPA reaches green-band high_confidence_count but verify MISMATCH, re-run static alignment / re-apply filter / switch leakage model to 'fix' it.
  - Why: Green band means 80%+ of bytes are already correct; MISMATCH just means 1-3 bytes need key_search correction. Redoing preprocessing may destroy the already-correct bytes and force restart.
  - Correct: In green band + MISMATCH: ONLY invoke key_search (increase candidates or expand search space over the low-confidence bytes). Do NOT touch alignment/filter/target/model.
- **Applies to**: StatMethod:CPA

### ⭐ ⚠ [anti_pattern_set] Do NOT switch leakage target family as first response to low correlation on software implementations
- **Trigger**: Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear
- **Rationale**: From expert_experience.md L294/L443/L599: 软件优先固定 S-box_out + HW，除非强证据；不要反复换 target
- **Anti-pattern 1**: On a software implementation, switch leakage target from S-box_out to S-box_in / S-box_in_xor_prev_ct / etc. as the first repair after seeing low correlation.
  - Why: Under a fixed implementation prototype, the correlation magnitude is determined primarily by SNR, alignment, and interval selection—switching target within the same family yields nearly identical correlations. Repeatedly switching wastes rounds and can misdirect the agent away from the real root cause.
  - Correct: For software MCU/smartcard, default to S-box_out + HW model and ONLY switch target when there is explicit evidence of implementation-prototype mismatch (e.g., dual-mode k/k^0xFF pattern visible in CPA detail, suggests linear-HD target). First fix alignment and interval; switch target last.
- **Applies to**: AttackPoint:S-box Output, StatMethod:CPA

### ⭐ ⚠ [anti_pattern_set] Do NOT treat alignment_avg_correlation as a CPA success metric
- **Trigger**: Any time an alignment tool returns alignment_avg_correlation >= 0.9
- **Rationale**: From expert_experience.md L144/L601: 攻击成败看 gap_pct/high_confidence_count，不要用 alignment_avg_correlation 代替
- **Anti-pattern 1**: Report 'alignment_avg_correlation = 0.99, so CPA will succeed' or use alignment metric to decide whether to stop iterating.
  - Why: alignment_avg_correlation measures how stable template matching is across traces; it's a preprocessing quality metric, not a CPA success metric. A high alignment correlation just means traces are synchronized—it says nothing about whether the synchronization point is the leakage point.
  - Correct: CPA success/failure is judged ONLY by gap_pct and high_confidence_count in the CPA tool return value. alignment_avg_correlation is used solely to decide if alignment parameters themselves need tuning (low alignment_avg_correlation = tune max_shift/length/threshold).
- **Applies to**: Preprocessing:Static Alignment

### ⭐ ⚠ [anti_pattern_set] alignment max_shift should start large (300+), not default to small
- **Trigger**: Any static_aligner invocation on smartcard / MCU traces
- **Rationale**: From expert_experience.md L223-224: 宁可大一些也不要太小
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
- **Rationale**: smoke Patch 003+003.1 DSv3.2 DES-7816 5-run eval 3/5=60% 中 2 次 fail 共享此根因：Run 3 Round 17 aligned CPA S-box_in dual-mode 给出 '1002B0465C422698'（HD-3 from truth）但默认 gap_threshold=0.15 过滤 掉全部 byte（dual-mode gap_pct=0 by design）→ 没 key_search 就走 target churn。Run 4 Round 12 hc=4/8 recovered='10002A445442268A'（HD-6 from truth，4 字节精确匹配）→ Round 14 key_search default budget → not found → Round 15 起切 target 模型放弃了 near-miss key。Phase-14 成功 路径 Round 12 key_search（gap_thr=0.15, 30 cand, 50k combos）一击即中 因为 aligned hc=8/8 (HD-2)，本 smoke 两次只做到 HD-5/HD-6，所以需要更大 预算。本 strategy 固化max_combinations/gap_threshold/max_candidates 三阶梯 + dual-mode 双分支 + same-alignment-only merging 5 条规则，通用不限算法/设备。
- **Content**: [{"principle": "A single key_search returning found=false is NOT sufficient evidence that CPA / alignment / target / leakage model is wrong. Before pivoting ANY other dimension (leakage target, leakage model, preprocessing chain, alignment anchor, target family), the agent MUST escalate the key_search budget along a fixed four-step ladder (combinations, gap_threshold, candidates, dual-mode both-br
- **Applies to**: StatMethod:CPA

### ⭐ • [canonical_pipeline_principle] Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)
- **Trigger**: Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap)
- **Rationale**: smoke iter2 Patch 003+003.1+003.2 DSv3.2 DES-7816 仍 3/5=60%，2 fail 最佳 aligned recovered key HD=6（远超 phase-14 成功 HD=3），key_search 500k-5M budget 覆盖 64^6 空间 < 0.01%。根因：agent 在 plaintext/ciphertext correlation 首带（~500-600 samples，IO/bus pre-encryption 区）对齐而非 variance peak 区（~1000-1300 samples，真 S-box 加密体）。Patch 003 Strategy A 有 variance-first 原则但 scope 限制 software MCU，DES 接触式智能卡被排除。本 strategy 将 variance-first 扩展为 device-agnostic，并明确 disjoint ROI 决策规则 + 欺骗性 alignment 指标诊断（high align_corr + low aligned CPA hc = anchor 错）。
- **Content**: [{"principle": "When variance-based ROI exploration and plaintext/ciphertext-correlation analysis disagree on the encryption-region location (disjoint candidate intervals), the agent MUST anchor static_aligner on the VARIANCE-peak region, NOT the first plaintext/ciphertext-correlation band. This is a device-agnostic rule that extends Strategy A's variance-first principle (originally software MCU o
- **Applies to**: StatMethod:CPA, Preprocessing:Static Alignment

### ⭐ • [canonical_pipeline_principle] Software implementation: variance-first ROI exploration before alignment
- **Trigger**: Software cryptographic implementation (any MCU: STM32F1/F4/Cortex/AVR/Arduino; or contact smartcard running software crypto) + non-profiled CPA + direct CPA returns unstable high_confidence_count below empirical_threshold
- **Rationale**: phase-11 DSv3.1T AES-STM32F103 成功样本 Round 2 即 np.var 定位方差突增区 (samples 1098-1107) → Round 3 direct CPA 成功；round19 DSv3.2 三条 STM32F103 fail 全缺 variance-first 步骤，直接把 plaintext/ciphertext correlation 首个相关带 当 ROI 做 static alignment，acceptance rate 持续 4/250-5/250 仍继续在同区间 重复对齐。此处 codify 为通用软件实现原则，阈值标 empirical。
- **Content**: [{"principle": "For software cryptographic implementations, when direct CPA does NOT yield stable high-confidence candidates, the agent MUST first perform variance-based / energy-signature ROI exploration (e.g., np.var / np.std over sliding windows) to locate the encryption region, BEFORE deciding alignment intervals or switching leakage targets.", "reason": "Software implementations on MCU/smartc
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

### ⭐ 📋 [troubleshooting_checklist] Decision to perform static alignment based on direct CPA result
- **Trigger**: after first CPA probe (without alignment)
- **Rationale**: Direct CPA can succeed without alignment if the waveform is already focused on the encryption interval. Alignment is only needed when signal is insufficient.
- **[rank 1]** if `high_confidence_count for AES` → if ≥13, skip alignment; if 10-12, enter alignment and multi-strategy; if <10, must align
- **[rank 2]** if `high_confidence_count for DES` → if ≥6, skip alignment; if 5, enter alignment and multi-strategy; if <5, must align
- **[rank 3]** if `high_confidence_count for SM4 per round` → if ≥3, skip alignment; if 2, enter alignment and multi-strategy; if <2, must align
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

### ⚠ [anti_pattern_set] Non-sensitive leakage times to ignore
- **Trigger**: when evaluating side-channel leakage for block ciphers
- **Rationale**: These leakage points do not represent a vulnerability for key recovery because they depend on known data or are not directly exploitable. Failing a device based on them would be overly conservative.
- **Anti-pattern 1**: (unnamed)
  - Why: Leakage in outer rounds is less sensitive because it depends on known plaintext/ciphertext and is harder to exploit for key recovery.
- **Anti-pattern 2**: (unnamed)
  - Why: Key loading often involves known values or is not directly exploitable for key recovery in the same way as intermediate cryptographic operations.
- **Anti-pattern 3**: (unnamed)
  - Why: Plaintext and ciphertext are known, so their leakage does not directly reveal the secret key.
- **Applies to**: Algorithm:AES, StatMethod:DPA

### 📋 [troubleshooting_checklist] DEMA on RFID Smartcard - Core Steps
- **Trigger**: when performing a non-invasive EM side-channel attack (DEMA) on an unknown RFID/contactless smartcard
- **Rationale**: This ordered sequence ensures that the basic prerequisites (triggering, alignment, localization) are satisfied before attempting the statistical attack, which is critical for black-box analysis.
- **[rank 1]** if `Find a suitable trigger point` → Identify a stable reference point in the communication protocol to start trace acquisition
- **[rank 2]** if `Align the traces` → Use a short reference pattern and align only the region of interest, especially for asynchronous devices
- **[rank 3]** if `Locate the DES encryption` → Correlate with known plaintext/ciphertext bytes to identify the time interval of the encryption operation
- **[rank 4]** if `Perform the EM analysis` → Apply CPA (or binwise CPA) on the aligned encryption interval to recover the key
- **Applies to**: StatMethod:CPA, Algorithm:3DES, DeviceClass:Commercial Contactless Smartcard

### 📋 [troubleshooting_checklist] Adaptive Message Selection for Efficient Key Recovery
- **Trigger**: When using the basic collision-correlation method and wanting to reduce the number of messages (and thus total traces) required for key recovery.
- **Rationale**: This method exploits non-collision events (which are numerous) to build blacklists and uses graph connectivity to guide adaptive message selection, maximizing new information per message.
- **[rank 1]** if `Define penalty of candidate message` → For each pair (i1, i2), check if m_i1 ⊕ m_i2 is already blacklisted. If yes, penalty++. If no, penalty remains unchanged.
- **[rank 2]** if `Refine penalty calculation` → If (i1, i2) and (i1, i2') are in same connected component and m_i1 ⊕ m_i2 = m_i2 ⊕ m_i2' is known, then the two opportunities count as one. Increase penalty by 1.
- **[rank 3]** if `Select candidate message with minimal penalty` → Use a two-step heuristic: 1) Randomly pick a few hundred messages, select the one with lowest penalty. 2) Iteratively try small modifications to the best candidate until no improvement.
- **Applies to**: Algorithm:AES, StatMethod:Collision-Correlation Attack

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_GLM-5\DES-14443_GLM5_DKG_20260424_040456_020
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\DES-14443_GLM5_DKG_20260424_040456_020/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 15,789→785

**🤖 LLM:** 我来帮你对非接触式智能卡的DES电磁侧信道波形进行CPA攻击。让我按照标准流程进行分析。

首先，让我加载数据并查看波形特征：

**🔧 → `python_jupyter`**

<details><summary>Code (842 chars)</summary>

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
print(f"\n波形数据类型: {wave.dtype}")
print(f"明文数据类型: {plain.dtype}")
print(f"密文数据类型: {cipher.dtype}")

# 查看波形统计信息
print(f"\n波形统计:")
print(f"  最小值: {wave.min():.4f}")
print(f"  最大值: {wave.max():.4f}")
print(f"  均值: {wave.mean():.4f}")
print(f"  标准差: {wave.std():.4f}")
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (10000, 300)
明文数据形状: (10000, 8)
密文数据形状: (10000, 8)

波形数据类型: float32
明文数据类型: uint8
密文数据类型: uint8

波形统计:
  最小值: -141.7323
  最大值: 23.6221
  均值: -43.2685
  标准差: 45.9733`


---

### Round 2 | tokens: 16,297→704

**🔧 → `python_jupyter`**

<details><summary>Code (1497 chars)</summary>

```python
# 可视化波形特征
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 叠加显示前100条波形
ax1 = axes[0, 0]
for i in range(min(100, wave.shape[0])):
    ax1.plot(wave[i], alpha=0.1, color='blue')
ax1.set_title('前100条波形叠加（检查时间偏移）')
ax1.set_xlabel('采样点')
ax1.set_ylabel('幅度')
ax1.grid(True, alpha=0.3)

# 2. 方差分布（找加密区域）
ax2 = axes[0, 1]
variance = np.var(wave, axis=0)
ax2.plot(variance, color='red', linewidth=1.5)
ax2.set_title('方差分布（定位加密区域）')
ax2.set_xlabel('采样点')
ax2.set_ylabel('方差')
ax2.grid(True, alpha=0.3)
# 标记方差峰值
peak_idx = np.argmax(variance)
ax2.axvline(peak_idx, color='green', linestyle='--', label=f'峰值位置: {peak_idx}')
ax2.legend()

# 3. 均值波形
ax3 = axes[1, 0]
mean_wave = np.mean(wave, axis=0)
ax3.plot(mean_wave, color='purple', linewidth=1.5)
ax3.set_title('均值波形')
ax3.set_xlabel('采样点')
ax3.set_ylabel('幅度')
ax3.grid(True, alpha=0.3)

# 4. 检查基线漂移（非加密区域的均值变化）
ax4 = axes[1, 1]
baseline_means = np.mean(wave[:, :50], axis=1)  # 前50个采样点的均值
ax4.hist(baseline_means, bins=50, color='orange', alpha=0.7, edgecolor='black')
ax4.set_title('基线均值分布（前50采样点）')
ax4.set_xlabel('均值幅度')
ax4.set_ylabel('频数')
ax4.axvline(baseline_means.mean(), color='red', linestyle='--', 
            label=f'总体均值: {baseline_means.mean():.2f}\n标准差: {baseline_means.std():.2f}')
ax4.legend()

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

print(f"\n关键观察:")
print(f"1. 方差峰值位置: 采样点 {peak_idx}")
print(f"2. 基线均值标准差: {baseline_means.std():.4f} ({'需要垂直对齐' if baseline_means.std() > 5 else '无需垂直对齐'})")
```
</details>

**📋 ← `python_jupyter`:** `关键观察:
1. 方差峰值位置: 采样点 146
2. 基线均值标准差: 0.8624 (无需垂直对齐)
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2204248238.py:48: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 16,991→378

**🤖 LLM:** 好的，波形分析显示：
- **波形长度**：300个采样点（较短，可能已裁剪到加密区域）
- **方差峰值**：采样点146
- **基线漂移**：标准差0.86，无需垂直对齐

现在让我先进行**直接CPA攻击**（不做对齐），使用标准S-box_out + HW模型：

**🔧 → `des_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 30
}
```
</details>

<details><summary><b>📋 ← `des_cpa_attack`</b> (2545 chars)</summary>

```
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3030422331.py:12: RuntimeWarning: More than 20 figures have been opened. Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory. (To control this warning, see the rcParam `figure.max_open_warning`). Consider using `matplotlib.pyplot.close()`.
  fig,axes = plt.subplots(2,4,figsize=(16,6))
{"recovered_key": "A8C628B4EADAA2E6", "cpa_avg_correlation": 0.0408, "cpa_min_correlation": 0.0373, "n_traces": 10000, "target": "S-box_out", "plot_path": "des_cpa_result_20260424_040608_196787.png", "detail_file": "des_cpa_detail_20260424_040608_196787.json", "per_sbox": [{"sbox": 0, "key": "0x3A", "correlation": 0.03757716827551415, "time_index": 72, "gap_pct": 0.5}, {"sbox": 1, "key": "0x37", "correlation": 0.04408537728676676, "time_index": 229, "gap_pct": 12.5}, {"sbox": 2, "key": "0x37", "correlation": 0.04820766829566469, "time_index": 51, "gap_pct": 16.7}, {"sbox": 3, "key": "0x35", "correlation": 0.037335031910917145, "time_index": 139, "gap_pct": 4.4}, {"sbox": 4, "key": "0x1A", "correlation": 0.041315795611214436, "time_index": 5, "gap_pct": 4.1}, {"sbox": 5, "key": "0x38", "correlation": 0.0380185254128461, "time_index": 117, "gap_pct": 7.4}, {"sbox": 6, "key": "0x16", "correlation": 0.04136191046108054, "time_index": 270, "gap_pct": 9.3}, {"sbox": 7, "key": "0x36", "correlation": 0.03836126236685273, "time_index": 8, "gap_pct": 0.5}], "high_
...(truncated)
```
</details>


![des_cpa_result_20260424_040608_196787.png](./des_cpa_result_20260424_040608_196787.png)


---

### Round 4 | tokens: 18,274→358

**🤖 LLM:** 直接CPA结果显示：
- **高置信度S-box**：仅1/8（红色区域）
- **平均相关系数**：0.0408（较低）
- **大部分gap_pct很低**：说明信号不明显

让我先验证这个密钥，然后尝试硬件HD模型（非接触式智能卡常用）：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "key_hex": "A8C628B4EADAA2E6",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (996 chars)</summary>

```
{"result_hex": "0096B5CE43822553", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 19a4073f51fdaea7... → 0096B5CE43822553...\n❌ Key verification FAILED — 8/8 ciphertext bytes differ\n   Expected:  F434B0F486FC4A4B\n   Got:       0096B5CE43822553\n\n   ⚠️ IMPORTANT: '8 ciphertext bytes differ' does NOT mean '8 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 5 | tokens: 18,804→216

**🤖 LLM:** 密钥验证失败。让我尝试**硬件HD模型**（非接触式智能卡常用）：

**🔧 → `des_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy",
  "target": "R_xor_LOut",
  "leakage_model": "HW",
  "candidates": 30
}
```
</details>

<details><summary><b>📋 ← `des_cpa_attack`</b> (2069 chars)</summary>

```
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\838488770.py:12: RuntimeWarning: More than 20 figures have been opened. Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory. (To control this warning, see the rcParam `figure.max_open_warning`). Consider using `matplotlib.pyplot.close()`.
  fig,axes = plt.subplots(2,4,figsize=(16,6))
{"recovered_key": "1002324454422688", "cpa_avg_correlation": 0.0647, "cpa_min_correlation": 0.0552, "n_traces": 10000, "target": "R_xor_LOut", "plot_path": "des_cpa_result_20260424_040628_081741.png", "detail_file": "des_cpa_detail_20260424_040628_081741.json", "per_sbox": [{"sbox": 0, "key": "0x18", "correlation": 0.06532909050168481, "time_index": 71, "gap_pct": 37.3}, {"sbox": 1, "key": "0x13", "correlation": 0.0670683319225106, "time_index": 80, "gap_pct": 34.4}, {"sbox": 2, "key": "0x08", "correlation": 0.05685691480249112, "time_index": 81, "gap_pct": 27.3}, {"sbox": 3, "key": "0x08", "correlation": 0.06660892409404137, "time_index": 79, "gap_pct": 28.4}, {"sbox": 4, "key": "0x05", "correlation": 0.06105223181775767, "time_index": 78, "gap_pct": 33.0}, {"sbox": 5, "key": "0x32", "correlation": 0.08301818706588436, "time_index": 81, "gap_pct": 43.6}, {"sbox": 6, "key": "0x2B", "correlation": 0.06231637119273267, "time_index": 82, "gap_pct": 13.8}, {"sbox": 7, "key": "0x02", "correlation": 0.05516262101644671, "time_index": 83, "gap_pct": 25.6}], "hig
...(truncated)
```
</details>


![des_cpa_result_20260424_040628_081741.png](./des_cpa_result_20260424_040628_081741.png)


---

### Round 6 | tokens: 19,775→318

**🤖 LLM:** 太好了！**R_xor_LOut硬件HD模型**效果显著：
- **高置信度S-box**：7/8（绿色区域）
- **平均相关系数**：0.0647（符合硬件HD预期）
- **仅S-box 6不可靠**（gap=13.8%）

让我验证这个密钥：

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

### Round 7 | tokens: 20,308→297

**🤖 LLM:** 验证失败，但7/8高置信度说明大部分字节正确。让我使用**key_search**搜索正确密钥：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "recovered_key_hex": "1002324454422688",
  "cpa_detail_file": "des_cpa_detail_20260424_040628_081741.json",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 30,
  "max_combinations": 50000
}
```
</details>

<details><summary><b>📋 ← `key_search`</b> (1691 chars)</summary>

```
{"found": true, "correct_key": "1022324454667688", "search_rounds": 245, "total_search_space": 7680, "sbox_analysis": [{"sbox": 0, "gap": 0.3731, "reliable": true, "top1": 24, "candidates": [24, 55, 34, 23, 37, 8, 46, 32, 14, 38, 58, 7, 28, 26, 20, 13, 57, 62, 0, 27, 48, 4, 59, 49, 61, 30, 43, 60, 42, 15]}, {"sbox": 1, "gap": 0.3439, "reliable": true, "top1": 19, "candidates": [19, 32, 51, 3, 7, 58, 60, 17, 27, 44, 23, 50, 47, 53, 42, 54, 13, 29, 30, 8, 40, 45, 49, 16, 41, 6, 10, 12, 34, 14]}, {"sbox": 2, "gap": 0.2734, "reliable": true, "top1": 8, "candidates": [8, 60, 26, 52, 63, 10, 38, 44, 22, 31, 43, 35, 49, 13, 62, 59, 37, 9, 56, 34, 33, 29, 21, 36, 18, 45, 51, 32, 0, 19]}, {"sbox": 3, "gap": 0.2842, "reliable": true, "top1": 8, "candidates": [8, 26, 19, 45, 58, 32, 2, 31, 5, 34, 55, 11, 37, 18, 28, 53, 0, 20, 4, 47, 27, 6, 40, 36, 15, 50, 24, 23, 22, 44]}, {"sbox": 4, "gap": 0.3303, "reliable": true, "top1": 5, "candidates": [5, 42, 32, 7, 1, 36, 62, 26, 30, 10, 18, 22, 6, 60, 54, 41, 8, 44, 46, 33, 63, 21, 24, 51, 39, 23, 25, 59, 34, 49]}, {"sbox": 5, "gap": 0.4355, "reliable": true, "top1": 50, "candidates": [50, 48, 12, 26, 18, 46, 7, 54, 58, 24, 40, 5, 36, 23, 51, 62, 43, 37, 53, 4, 0, 3, 33, 47, 9, 61, 13, 32, 52, 16]}, {"sbox": 6, "gap": 0.1384, "reliable": false, "top1": 43, "candidates": [43, 31, 41, 39, 52, 58, 28, 0, 3, 32, 14, 53, 19, 13, 35, 44, 16, 2, 46, 15, 4, 54, 36, 62, 33, 61, 22, 7, 29, 34]}, {"sbox": 7, "gap": 0.2559, "reliable": true, "top1": 2, "c
...(truncated)
```
</details>


---

### Round 8 | tokens: 21,590→214

**🤖 LLM:** 太好了！**key_search成功找到正确密钥**：`1022324454667688`

让我验证这个密钥：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "key_hex": "1022324454667688",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy",
  "trace_index": 0
}
```
</details>

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "F434B0F486FC4A4B", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 19a4073f51fdaea7... → F434B0F486FC4A4B...\n✅ Key verification PASSED — all 8 bytes match."}`


---

### Round 9 | tokens: 21,872→470

<details><summary><b>🤖 LLM Reasoning</b> (855 chars)</summary>

## ✅ 攻击成功！

### 📊 攻击总结

**目标设备**：非接触式智能卡（EM侧信道）  
**算法**：DES-64  
**波形数量**：10,000条  
**波形长度**：300采样点  

---

### 🔑 恢复的密钥

```
1022324454667688
```

**验证结果**：✅ MATCH（密文完全匹配）

---

### 📈 攻击过程

| 步骤 | 方法 | 结果 | 说明 |
|------|------|------|------|
| 1 | 波形分析 | 方差峰值@146 | 无明显基线漂移 |
| 2 | 直接CPA (S-box_out + HW) | 1/8高置信度 | ❌ 软件模型不适用 |
| 3 | **硬件HD模型** (R_xor_LOut + HW) | **7/8高置信度** | ✅ 正确的泄漏模型 |
| 4 | key_search | 245次搜索找到 | 修正S-box 6错误 |

---

### 💡 关键发现

1. **泄漏模型选择**：非接触式智能卡使用**硬件HD模型**（R_xor_LOut），而非软件S-box输出模型
   - S-box_out平均相关系数：0.0408
   - R_xor_LOut平均相关系数：0.0647（提升58%）

2. **高置信度字节**：7/8 S-box的gap > 15%，说明CPA攻击有效

3. **低置信度字节**：S-box 6（gap=13.8%）需要key_search修正

---

### 📁 生成的文件

- `des_cpa_result_20260424_040628_081741.png` - CPA相关系数图
- `des_cpa_detail_20260424_040628_081741.json` - CPA详细结果（含候选密钥）
- `waveform_analysis.png` - 波形分析图

攻击成功完成！🎉

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 15,789 | 785 | 16,574 |
| 2 | 16,297 | 704 | 17,001 |
| 3 | 16,991 | 378 | 17,369 |
| 4 | 18,274 | 358 | 18,632 |
| 5 | 18,804 | 216 | 19,020 |
| 6 | 19,775 | 318 | 20,093 |
| 7 | 20,308 | 297 | 20,605 |
| 8 | 21,590 | 214 | 21,804 |
| 9 | 21,872 | 470 | 22,342 |
| **Total** | **169,700** | **3,740** | **173,440** |

## 8. Final Output

## ✅ 攻击成功！

### 📊 攻击总结

**目标设备**：非接触式智能卡（EM侧信道）  
**算法**：DES-64  
**波形数量**：10,000条  
**波形长度**：300采样点  

---

### 🔑 恢复的密钥

```
1022324454667688
```

**验证结果**：✅ MATCH（密文完全匹配）

---

### 📈 攻击过程

| 步骤 | 方法 | 结果 | 说明 |
|------|------|------|------|
| 1 | 波形分析 | 方差峰值@146 | 无明显基线漂移 |
| 2 | 直接CPA (S-box_out + HW) | 1/8高置信度 | ❌ 软件模型不适用 |
| 3 | **硬件HD模型** (R_xor_LOut + HW) | **7/8高置信度** | ✅ 正确的泄漏模型 |
| 4 | key_search | 245次搜索找到 | 修正S-box 6错误 |

---

### 💡 关键发现

1. **泄漏模型选择**：非接触式智能卡使用**硬件HD模型**（R_xor_LOut），而非软件S-box输出模型
   - S-box_out平均相关系数：0.0408
   - R_xor_LOut平均相关系数：0.0647（提升58%）

2. **高置信度字节**：7/8 S-box的gap > 15%，说明CPA攻击有效

3. **低置信度字节**：S-box 6（gap=13.8%）需要key_search修正

---

### 📁 生成的文件

- `des_cpa_result_20260424_040628_081741.png` - CPA相关系数图
- `des_cpa_detail_20260424_040628_081741.json` - CPA详细结果（含候选密钥）
- `waveform_analysis.png` - 波形分析图

攻击成功完成！🎉
