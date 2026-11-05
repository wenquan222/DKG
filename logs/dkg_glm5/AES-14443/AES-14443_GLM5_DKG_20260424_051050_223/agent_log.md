# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_051050_223 |
| Duration | 260.2s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-14443_GLM5_DKG_20260424_051050_223` |
| Total LLM Calls | 10 |
| First Round | prompt: 14,517, completion: 1,071 |
| Last Round | prompt: 20,763, completion: 680 |
| Total Tokens | 180,476 (prompt: 174,901, completion: 5,575) |

## 3. User Query

```
帮我对一个非接触式智能卡实现的AES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个非接触式智能卡实现的AES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy'"

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
["AES", "Contactless Smartcard", "EM", "CPA", "ISO 14443"]

Parsed Keywords: `["AES", "Contactless Smartcard", "EM", "CPA", "ISO 14443"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 33795 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (36045 chars, click to expand)</summary>

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

**Search keywords** (5): AES, Contactless Smartcard, EM, CPA, ISO 14443

**Summary**: 21 upper entities, 20 relationships, 15 diagnostic chains, 12 strategies


## 1. Upper Layer Entities (21)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### DeviceClass (6)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **Commercial Contactless Smartcard** — category=Smartcard
- **32-bit implementation** — bus_width=32
- **ASIC implementation of PicoRV32 on Saidoyoki board** — category=ASIC

### Pipeline (7)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

### StatMethod (7)

- **Algebraic System Construction** — type=non_profiled
- **CEMA** — type=non_profiled
- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled

## 2. Relationships (20)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: XOR operation output, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `AttackPoint:XOR operation output`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
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

## 3. Diagnostic Chains (15)


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

### Obs: `key_byte_distinguishability` — any
- **Cause** (high): Different key bytes (e.g., 0x55 and 0xAA) can have the same Hamming weight, making them indistinguishable if attacking the key directly. The S-box output provides a nonlinear transformation that spreads the Hamming weights, creating a unique signature for each key hypothesis.
- **Action**: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.
  - operation: `switch_component`
  - target: `attack point`
  - strategy: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.

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

## 4. Strategies (12)


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

### 📋 [troubleshooting_checklist] DEMA on RFID Smartcard - Core Steps
- **Trigger**: when performing a non-invasive EM side-channel attack (DEMA) on an unknown RFID/contactless smartcard
- **Rationale**: This ordered sequence ensures that the basic prerequisites (triggering, alignment, localization) are satisfied before attempting the statistical attack, which is critical for black-box analysis.
- **[rank 1]** if `Find a suitable trigger point` → Identify a stable reference point in the communication protocol to start trace acquisition
- **[rank 2]** if `Align the traces` → Use a short reference pattern and align only the region of interest, especially for asynchronous devices
- **[rank 3]** if `Locate the DES encryption` → Correlate with known plaintext/ciphertext bytes to identify the time interval of the encryption operation
- **[rank 4]** if `Perform the EM analysis` → Apply CPA (or binwise CPA) on the aligned encryption interval to recover the key
- **Applies to**: StatMethod:CPA, Algorithm:3DES, DeviceClass:Commercial Contactless Smartcard

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-14443_GLM5_DKG_20260424_051050_223
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-14443_GLM5_DKG_20260424_051050_223/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 14,517→1,071

**🤖 LLM:** 我来帮你对这个非接触式智能卡的AES-128 EM侧信道波形进行CPA攻击。让我按照标准的分析流程进行。

## 第一步：波形可视化与特征分析

首先加载并可视化波形，观察数据特征：

**🔧 → `python_jupyter`**

<details><summary>Code (1107 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy')
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy')

print(f"波形数据形状: {wave.shape}")
print(f"明文数据形状: {plain.shape}")
print(f"密文数据形状: {cipher.shape}")
print(f"波形数据类型: {wave.dtype}")
print(f"波形值范围: [{wave.min():.2f}, {wave.max():.2f}]")

# 可视化前10条波形
plt.figure(figsize=(14, 8))
for i in range(10):
    plt.plot(wave[i] + i * 0.1, alpha=0.7, linewidth=0.5)
plt.xlabel('Sample Point', fontsize=12)
plt.ylabel('Amplitude (offset for clarity)', fontsize=12)
plt.title('First 10 EM Traces - Contactless Smartcard AES-128', fontsize=14)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('waveform_overview.png', dpi=150)
plt.show()
print("\n波形概览已保存为 waveform_overview.png")
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (5000, 1900)
明文数据形状: (5000, 16)
密文数据形状: (5000, 16)
波形数据类型: float32
波形值范围: [-40.36, 44.90]

波形概览已保存为 waveform_overview.png
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\400792860.py:25: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 2 | tokens: 15,108→784

**🔧 → `python_jupyter`**

<details><summary>Code (1776 chars)</summary>

```python
# 计算方差和均值曲线，定位加密区域
mean_trace = np.mean(wave, axis=0)
var_trace = np.var(wave, axis=0)
std_trace = np.std(wave, axis=0)

# 绘制统计特征
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# 均值曲线
axes[0].plot(mean_trace, color='blue', linewidth=0.8)
axes[0].set_xlabel('Sample Point', fontsize=11)
axes[0].set_ylabel('Mean Amplitude', fontsize=11)
axes[0].set_title('Mean Trace', fontsize=12)
axes[0].grid(True, alpha=0.3)

# 方差曲线（关键：定位加密操作区域）
axes[1].plot(var_trace, color='red', linewidth=0.8)
axes[1].set_xlabel('Sample Point', fontsize=11)
axes[1].set_ylabel('Variance', fontsize=11)
axes[1].set_title('Variance Trace (Encryption Region Detection)', fontsize=12)
axes[1].grid(True, alpha=0.3)

# 标记方差峰值区域
var_peaks = np.where(var_trace > np.mean(var_trace) + 2*np.std(var_trace))[0]
if len(var_peaks) > 0:
    axes[1].axvspan(var_peaks[0], var_peaks[-1], alpha=0.2, color='green', label=f'High variance region: [{var_peaks[0]}, {var_peaks[-1]}]')
    axes[1].legend(fontsize=10)

# 标准差曲线
axes[2].plot(std_trace, color='green', linewidth=0.8)
axes[2].set_xlabel('Sample Point', fontsize=11)
axes[2].set_ylabel('Standard Deviation', fontsize=11)
axes[2].set_title('Standard Deviation Trace', fontsize=12)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('variance_analysis.png', dpi=150)
plt.show()

print(f"\n方差峰值区域: [{var_peaks[0]}, {var_peaks[-1]}]")
print(f"方差最大值位置: {np.argmax(var_trace)}")
print(f"方差最大值: {var_trace.max():.4f}")
print(f"方差均值: {var_trace.mean():.4f}")

# 检查基线漂移（非接触式EM常见问题）
baseline_region = wave[:, :100]  # 前100个点作为基线
baseline_means = np.mean(baseline_region, axis=1)
baseline_std = np.std(baseline_means)
print(f"\n基线区域均值标准差: {baseline_std:.4f}")
if baseline_std > 1.0:
    print("⚠️ 检测到明显的基线漂移，可能需要垂直对齐")
else:
    print("✓ 基线相对稳定，垂直对齐可能不是必需的")
```
</details>

**📋 ← `python_jupyter`:** `方差峰值区域: [0, 1899]
方差最大值位置: 6
方差最大值: 428.8090
方差均值: 22.2043

基线区域均值标准差: 0.5628
✓ 基线相对稳定，垂直对齐可能不是必需的
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3437784560.py:38: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 15,895→416

**🔧 → `python_jupyter`**

<details><summary>Code (1165 chars)</summary>

```python
# 更细致的方差分析 - 使用滑动窗口
window_size = 50
var_smoothed = np.convolve(var_trace, np.ones(window_size)/window_size, mode='same')

# 找到方差峰值
from scipy.signal import find_peaks
peaks, properties = find_peaks(var_smoothed, height=np.percentile(var_smoothed, 75), distance=50)

plt.figure(figsize=(14, 6))
plt.plot(var_trace, alpha=0.3, label='Raw variance', linewidth=0.5)
plt.plot(var_smoothed, color='red', linewidth=1.5, label='Smoothed variance')
plt.scatter(peaks, var_smoothed[peaks], color='green', s=100, zorder=5, label=f'Peaks ({len(peaks)})')

for i, peak in enumerate(peaks[:10]):  # 标注前10个峰值
    plt.annotate(f'{peak}', (peak, var_smoothed[peak]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)

plt.xlabel('Sample Point', fontsize=11)
plt.ylabel('Variance', fontsize=11)
plt.title('Variance Analysis with Peak Detection', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('variance_peaks.png', dpi=150)
plt.show()

print(f"检测到 {len(peaks)} 个方差峰值")
print(f"峰值位置: {peaks[:20]}")
print(f"\n前5个峰值详情:")
for i, peak in enumerate(peaks[:5]):
    print(f"  峰值{i+1}: 位置 {peak}, 方差值 {var_trace[peak]:.2f}")
```
</details>

**📋 ← `python_jupyter`:** `检测到 9 个方差峰值
峰值位置: [  25 1413 1495 1548 1649 1714 1765 1816 1875]

前5个峰值详情:
  峰值1: 位置 25, 方差值 19.33
  峰值2: 位置 1413, 方差值 21.98
  峰值3: 位置 1495, 方差值 22.23
  峰值4: 位置 1548, 方差值 47.00
  峰值5: 位置 1649, 方差值 108.17
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1099383440.py:24: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 4 | tokens: 16,488→430

**🔧 → `python_jupyter`**

<details><summary>Code (847 chars)</summary>

```python
# 查看后半段波形的详细特征（可能是加密区域）
plt.figure(figsize=(14, 6))

# 绘制单条波形的后半段
plt.subplot(1, 2, 1)
plt.plot(wave[0, 1300:], linewidth=0.8)
plt.xlabel('Sample Point (from 1300)', fontsize=11)
plt.ylabel('Amplitude', fontsize=11)
plt.title('Single Trace (1300-1900)', fontsize=12)
plt.grid(True, alpha=0.3)

# 绘制方差的后半段
plt.subplot(1, 2, 2)
plt.plot(var_trace[1300:], color='red', linewidth=1)
plt.xlabel('Sample Point (from 1300)', fontsize=11)
plt.ylabel('Variance', fontsize=11)
plt.title('Variance (1300-1900)', fontsize=12)
plt.grid(True, alpha=0.3)

# 标记峰值
for peak in peaks:
    if peak >= 1300:
        plt.axvline(peak-1300, color='green', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('encryption_region_detail.png', dpi=150)
plt.show()

print("后半段波形分析完成")
print(f"\n候选加密区域: 1300-1900 (共600个采样点)")
print(f"方差峰值集中在: {peaks[peaks >= 1300]}")
```
</details>

**📋 ← `python_jupyter`:** `后半段波形分析完成

候选加密区域: 1300-1900 (共600个采样点)
方差峰值集中在: [1413 1495 1548 1649 1714 1765 1816 1875]
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1485008958.py:27: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 5 | tokens: 16,916→342

**🤖 LLM:** ## 第二步：直接CPA攻击（探测）

根据方差分析，加密区域可能在后半段。让我先进行直接CPA攻击，评估是否需要预处理：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 30
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2338 chars)</summary>

```
{"recovered_key": "115033445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.144, "cpa_min_correlation": 0.0828, "n_traces": 5000, "target": "S-box_out", "plot_path": "cpa_result_20260424_051236_734176.png", "detail_file": "cpa_detail_20260424_051236_734176.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.115, "time_index": 204, "gap_pct": 41.7}, {"byte": 1, "key": "0x50", "correlation": 0.0852, "time_index": 315, "gap_pct": 9.7}, {"byte": 2, "key": "0x33", "correlation": 0.188, "time_index": 397, "gap_pct": 51.4}, {"byte": 3, "key": "0x44", "correlation": 0.2965, "time_index": 498, "gap_pct": 68.6}, {"byte": 4, "key": "0x55", "correlation": 0.0839, "time_index": 562, "gap_pct": 14.3}, {"byte": 5, "key": "0x66", "correlation": 0.1132, "time_index": 650, "gap_pct": 29.4}, {"byte": 6, "key": "0x77", "correlation": 0.1601, "time_index": 732, "gap_pct": 48.7}, {"byte": 7, "key": "0x88", "correlation": 0.1411, "time_index": 821, "gap_pct": 33.7}, {"byte": 8, "key": "0x99", "correlation": 0.1829, "time_index": 927, "gap_pct": 52.4}, {"byte": 9, "key": "0xAA", "correlation": 0.1604, "time_index": 997, "gap_pct": 49.4}, {"byte": 10, "key": "0xBB", "correlation": 0.1449, "time_index": 1109, "gap_pct": 46.5}, {"byte": 11, "key": "0xCC", "correlation": 0.0903, "time_index": 1204, "gap_pct": 10.2}, {"byte": 12, "key": "0xDD", "correlation": 0.0828, "time_index": 1286, "gap_pct": 15.6}, {"byte": 13, "key": "0xEE", "correlation": 0.1587, "time_index": 1380, "gap_pct": 48.6
...(truncated)
```
</details>


![cpa_result_20260424_051236_734176.png](./cpa_result_20260424_051236_734176.png)


---

### Round 6 | tokens: 18,096→415

**🤖 LLM:** **优秀！直接CPA攻击效果很好：**
- ✅ **高置信度字节：13/16**（绿色区域）
- 平均相关系数：0.144
- 只有3个字节置信度较低：byte 1 (9.7%), byte 4 (14.3%), byte 11 (10.2%)

这说明波形对齐良好，S-box_out + HW模型适合此设备。现在验证密钥：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "key_hex": "115033445566778899AABBCCDDEEFF00",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "2E3B64F5F71BD8F3985CF33F4EEAB65D", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 6f97fbb2277c573866e603dfc2d185ee... → 2E3B64F5F71BD8F3985CF33F4EEAB65D...\n❌ Key verification FAILED — 16/16 ciphertext bytes differ\n   Expected:  36F8A59DA55B127E03833A46548601D1\n   Got:       2E3B64F5F71BD8F3985CF33F4EEAB65D\n\n   ⚠️ IMPORTANT: '16 ciphertext bytes differ' does NOT mean '16 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 7 | tokens: 18,714→349

**🤖 LLM:** 验证失败，但这是正常的——13/16字节高置信度意味着只有少数字节需要修正。现在使用key_search搜索正确密钥：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "recovered_key_hex": "115033445566778899AABBCCDDEEFF00",
  "cpa_detail_file": "cpa_detail_20260424_051236_734176.json",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 30,
  "max_combinations": 50000
}
```
</details>

**📋 ← `key_search`:** `{"found": true, "correct_key": "112233445566778899AABBCCDDEEFF00", "search_rounds": 6301, "unreliable_bytes": [1, 4, 11], "message": "Key found after 6301 searches: 112233445566778899AABBCCDDEEFF00"}`


---

### Round 8 | tokens: 19,049→220

**🤖 LLM:** 🎉 **成功！密钥已恢复！**

让我验证最终结果：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy",
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy",
  "trace_index": 0
}
```
</details>

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "36F8A59DA55B127E03833A46548601D1", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 6f97fbb2277c573866e603dfc2d185ee... → 36F8A59DA55B127E03833A46548601D1...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 9 | tokens: 19,355→868

**🔧 → `python_jupyter`**

<details><summary>Code (1922 chars)</summary>

```python
# 生成完整的分析报告
import json

print("=" * 80)
print("AES-128 非接触式智能卡 EM侧信道 CPA攻击报告")
print("=" * 80)

print("\n【数据集信息】")
print(f"  波形文件: AES-128-14443-5000traces-1900points_wave.npy")
print(f"  明文文件: AES-128-14443-5000traces-1900points_plain.npy")
print(f"  密文文件: AES-128-14443-5000traces-1900points_cipher.npy")
print(f"  采集方式: 电磁侧信道 (EM)")
print(f"  设备类型: 非接触式智能卡 (Contactless Smartcard)")
print(f"  波形数量: 5000 条")
print(f"  采样点数: 1900 点")

print("\n【攻击配置】")
print(f"  攻击算法: AES-128")
print(f"  攻击方法: CPA (Correlation Power Analysis)")
print(f"  泄漏目标: S-box output (第一轮S盒输出)")
print(f"  泄漏模型: Hamming Weight (HW)")
print(f"  候选数量: 30 个/字节")

print("\n【攻击结果】")
print(f"  ✅ 恢复密钥: 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00")
print(f"  ✅ 验证状态: MATCH (密钥正确)")
print(f"  平均相关系数: 0.144")
print(f"  高置信度字节: 13/16 (81.25%)")

print("\n【低置信度字节修正】")
print(f"  Byte 1: 0x50 → 0x22 (gap: 9.7%)")
print(f"  Byte 4: 0x55 → 0x55 (gap: 14.3%, 实际正确)")
print(f"  Byte 11: 0xCC → 0xCC (gap: 10.2%, 实际正确)")
print(f"  Key Search 搜索轮次: 6301")

print("\n【分析过程】")
print("  1. 波形可视化 → 识别方差峰值区域")
print("  2. 直接CPA攻击 → 13/16字节高置信度")
print("  3. 密钥验证 → MISMATCH (3字节需修正)")
print("  4. Key Search → 成功找到正确密钥")
print("  5. 最终验证 → MATCH ✓")

print("\n【关键发现】")
print("  • 非接触式智能卡EM波形质量良好，无需静态对齐")
print("  • S-box_out + HW模型非常适合此设备")
print("  • 基线稳定，无需垂直对齐")
print("  • 5000条波形足够恢复完整密钥")

print("\n" + "=" * 80)
print("攻击成功完成！")
print("=" * 80)

# 保存报告
report = {
    "algorithm": "AES-128",
    "device": "Contactless Smartcard",
    "method": "CPA",
    "recovered_key": "112233445566778899AABBCCDDEEFF00",
    "verification": "MATCH",
    "high_confidence_count": 13,
    "avg_correlation": 0.144,
    "traces_used": 5000,
    "preprocessing": "None (direct CPA)",
    "leakage_target": "S-box_out",
    "leakage_model": "HW"
}

with open('attack_report.json', 'w') as f:
    json.dump(report, f, indent=2)
    
print("\n报告已保存至 attack_report.json")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1305 chars)</summary>

```
================================================================================
AES-128 非接触式智能卡 EM侧信道 CPA攻击报告
================================================================================

【数据集信息】
  波形文件: AES-128-14443-5000traces-1900points_wave.npy
  明文文件: AES-128-14443-5000traces-1900points_plain.npy
  密文文件: AES-128-14443-5000traces-1900points_cipher.npy
  采集方式: 电磁侧信道 (EM)
  设备类型: 非接触式智能卡 (Contactless Smartcard)
  波形数量: 5000 条
  采样点数: 1900 点

【攻击配置】
  攻击算法: AES-128
  攻击方法: CPA (Correlation Power Analysis)
  泄漏目标: S-box output (第一轮S盒输出)
  泄漏模型: Hamming Weight (HW)
  候选数量: 30 个/字节

【攻击结果】
  ✅ 恢复密钥: 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00
  ✅ 验证状态: MATCH (密钥正确)
  平均相关系数: 0.144
  高置信度字节: 13/16 (81.25%)

【低置信度字节修正】
  Byte 1: 0x50 → 0x22 (gap: 9.7%)
  Byte 4: 0x55 → 0x55 (gap: 14.3%, 实际正确)
  Byte 11: 0xCC → 0xCC (gap: 10.2%, 实际正确)
  Key Search 搜索轮次: 6301

【分析过程】
  1. 波形可视化 → 识别方差峰值区域
  2. 直接CPA攻击 → 13/16字节高置信度
  3. 密钥验证 → MISMATCH (3字节需修正)
  4. Key Search → 成功找到正确密钥
  5. 最终验证 → MATCH ✓

【关键发现】
  • 非接触式智能卡EM波形质量良好，无需静态对齐
  • S-box_out + HW模型非常适合此设备
  • 基线稳定，无需垂直对齐
  • 5000条波形足够恢复完整密钥

================================================================================
攻击成功完成！
================================================================================

报告已保存至 attack_report.json
```
</details>


---

### Round 10 | tokens: 20,763→680

<details><summary><b>🤖 LLM Reasoning</b> (941 chars)</summary>

## 🎉 攻击成功完成！

### 📊 攻击总结

**恢复的AES-128密钥：**
```
11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00
```

### 🔍 分析流程

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1️⃣ | 波形可视化与方差分析 | 识别加密区域，波形质量良好 |
| 2️⃣ | 直接CPA攻击 | 13/16字节高置信度 (81.25%) |
| 3️⃣ | 密钥验证 | MISMATCH (3字节需修正) |
| 4️⃣ | Key Search搜索 | 6301轮搜索找到正确密钥 |
| 5️⃣ | 最终验证 | ✅ **MATCH** |

### 📈 关键指标

- **平均相关系数**：0.144
- **高置信度字节**：13/16 (gap ≥ 15%)
- **低置信度字节**：Byte 1 (9.7%), Byte 4 (14.3%), Byte 11 (10.2%)
- **使用波形数**：5000条
- **预处理**：无需（直接CPA成功）

### 💡 关键发现

1. **波形质量优秀**：非接触式智能卡EM波形对齐良好，无需静态对齐
2. **模型匹配**：S-box_out + HW模型非常适合此设备的软件AES实现
3. **基线稳定**：无明显的DC漂移，无需垂直对齐
4. **数据充足**：5000条波形足以高质量恢复完整密钥

### 📁 生成的文件

- `waveform_overview.png` - 波形概览
- `variance_analysis.png` - 方差分析图
- `variance_peaks.png` - 方差峰值检测
- `encryption_region_detail.png` - 加密区域细节
- `cpa_result_*.png` - CPA相关系数图
- `cpa_detail_*.json` - CPA详细结果
- `attack_report.json` - 完整攻击报告

这是一个非常成功的CPA攻击案例，展示了非接触式智能卡EM侧信道分析的有效性！

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 14,517 | 1,071 | 15,588 |
| 2 | 15,108 | 784 | 15,892 |
| 3 | 15,895 | 416 | 16,311 |
| 4 | 16,488 | 430 | 16,918 |
| 5 | 16,916 | 342 | 17,258 |
| 6 | 18,096 | 415 | 18,511 |
| 7 | 18,714 | 349 | 19,063 |
| 8 | 19,049 | 220 | 19,269 |
| 9 | 19,355 | 868 | 20,223 |
| 10 | 20,763 | 680 | 21,443 |
| **Total** | **174,901** | **5,575** | **180,476** |

## 8. Final Output

## 🎉 攻击成功完成！

### 📊 攻击总结

**恢复的AES-128密钥：**
```
11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00
```

### 🔍 分析流程

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1️⃣ | 波形可视化与方差分析 | 识别加密区域，波形质量良好 |
| 2️⃣ | 直接CPA攻击 | 13/16字节高置信度 (81.25%) |
| 3️⃣ | 密钥验证 | MISMATCH (3字节需修正) |
| 4️⃣ | Key Search搜索 | 6301轮搜索找到正确密钥 |
| 5️⃣ | 最终验证 | ✅ **MATCH** |

### 📈 关键指标

- **平均相关系数**：0.144
- **高置信度字节**：13/16 (gap ≥ 15%)
- **低置信度字节**：Byte 1 (9.7%), Byte 4 (14.3%), Byte 11 (10.2%)
- **使用波形数**：5000条
- **预处理**：无需（直接CPA成功）

### 💡 关键发现

1. **波形质量优秀**：非接触式智能卡EM波形对齐良好，无需静态对齐
2. **模型匹配**：S-box_out + HW模型非常适合此设备的软件AES实现
3. **基线稳定**：无明显的DC漂移，无需垂直对齐
4. **数据充足**：5000条波形足以高质量恢复完整密钥

### 📁 生成的文件

- `waveform_overview.png` - 波形概览
- `variance_analysis.png` - 方差分析图
- `variance_peaks.png` - 方差峰值检测
- `encryption_region_detail.png` - 加密区域细节
- `cpa_result_*.png` - CPA相关系数图
- `cpa_detail_*.json` - CPA详细结果
- `attack_report.json` - 完整攻击报告

这是一个非常成功的CPA攻击案例，展示了非接触式智能卡EM侧信道分析的有效性！
