# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Qwen/Qwen3.5-397B-A17B` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_043950_701 |
| Duration | 242.5s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_Qwen3.5-397B\AES-14443_Qwen3.5-397B-A17B_DKG_20260424_043950_701` |
| Total LLM Calls | 8 |
| First Round | prompt: 16,322, completion: 1,115 |
| Last Round | prompt: 21,879, completion: 382 |
| Total Tokens | 159,175 (prompt: 155,083, completion: 4,092) |

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

LLM Response: ["AES", "Contactless Smartcard", "ISO14443", "EM", "CPA", "Hamming Weight", "S-box Output"]

Parsed Keywords: `["AES", "Contactless Smartcard", "ISO14443", "EM", "CPA", "Hamming Weight", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 37467 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (39757 chars, click to expand)</summary>

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

**Search keywords** (7): AES, Contactless Smartcard, ISO14443, EM, CPA, Hamming Weight, S-box Output

**Summary**: 33 upper entities, 29 relationships, 13 diagnostic chains, 13 strategies


## 1. Upper Layer Entities (33)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### AttackPoint (6)

- **Inverse S-box Output** — round=13
- **Masked S-box Output**
- **S-box Output** — required_data=ciphertext, round=last
- **S-box Output and Mask** — required_data=plaintext, round=first
- **S-box output** — round=1
- **S-box outputs** — round=first

### DeviceClass (6)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **Commercial Contactless Smartcard** — category=Smartcard
- **32-bit implementation** — bus_width=32
- **ASIC implementation of PicoRV32 on Saidoyoki board** — category=ASIC

### LeakageModel (5)

- **Hamming Weight** — requirements=software implementation
- **Hamming Weight (bit-based)** — requirements=bit-based
- **Hamming Weight of transitions**
- **Hamming weight**
- **Hamming weight of fused features**

### Pipeline (7)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, canonical_source=round1_patch_002, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

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
- `StatMethod:Generate Hamming weight models for S-box output` —[consists_of [parameters_note=models are lookup tables for the leakage of each possible S-box output, source_text=Generate Hamming weight models for S-box output, support_count=1, is_optional=False]]→ `Pipeline:SCALib CPA Attack on AES`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Avoid using the identity model for bijective S-boxes in MIA; use a non-bijective model (e.g., Hamming weight) or target a non-bijective intermediate value (e.g., predict only a subset of bits).`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:try different power models (bit, Hamming weight, Hamming distance, zero-value) to see which yields the highest and most distinct peak for a single key hypothesis`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:use the Hamming weight model for microcontrollers with precharged buses`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Use a non-injective leakage function that incurs information loss (e.g., Hamming weight, LSB, MSB).`
- `AttackPoint:S-box Output` —[strategy_applies_to [source=round1_patch_001, condition=Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear, applicability=specific]]→ `Strategy:Do NOT switch leakage target family as first response to low correlation on software implementations`
- `AttackPoint:Inverse S-box Output` —[has_attack_point [source_text=attack_point: Inverse S-box Output, round: 14, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[has_attack_point [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[works_with [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`

## 3. Diagnostic Chains (13)


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
- **Rationale**: smoke Patch 003+003.1 DSv3.2 DES-7816 5-run eval 3/5=60% 中 2 次 fail 共享此根因：Run 3 Round 17 aligned CPA S-box_in dual-mode 给出 '1002B0465C422698'（HD-3 from truth）但默认 gap_threshold=0.15 过滤 掉全部 byte（dual-mode gap_pct=0 by design）→ 没 key_search 就走 target churn。Run 4 Round 12 hc=4/8 recovered='10002A445442268A'（HD-6 from truth，4 字节精确匹配）→ Round 14 key_search default budget → not found → Round 15 起切 target 模型放弃了 near-miss key。Phase-14 成功 路径 Round 12 key_search（gap_thr=0.15, 30 cand, 50k combos）一击即中 因为 aligned hc=8/8 (HD-2)，本 smoke 两次只做到 HD-5/HD-6，所以需要更大 预算。本 strategy 固化max_combinations/gap_threshold/max_candidates 三阶梯 + dual-mode 双分支 + same-alignment-only merging 5 条规则，通用不限算法/设备。
- **Content**: [{"principle": "A single key_search returning found=false is NOT sufficient evidence that CPA / alignment / target / leakage model is wrong. Before pivoting ANY other dimension (leakage target, leakage model, preprocessing chain, alignment anchor, target family), the agent MUST escalate the key_search budget along a fixed four-step ladder (combinations, gap_threshold, candidates, dual-mode both-br
- **Applies to**: StatMethod:CPA

### ⭐ • [canonical_pipeline_principle] Software implementation: variance-first ROI exploration before alignment
- **Trigger**: Software cryptographic implementation (any MCU: STM32F1/F4/Cortex/AVR/Arduino; or contact smartcard running software crypto) + non-profiled CPA + direct CPA returns unstable high_confidence_count below empirical_threshold
- **Rationale**: phase-11 DSv3.1T AES-STM32F103 成功样本 Round 2 即 np.var 定位方差突增区 (samples 1098-1107) → Round 3 direct CPA 成功；round19 DSv3.2 三条 STM32F103 fail 全缺 variance-first 步骤，直接把 plaintext/ciphertext correlation 首个相关带 当 ROI 做 static alignment，acceptance rate 持续 4/250-5/250 仍继续在同区间 重复对齐。此处 codify 为通用软件实现原则，阈值标 empirical。
- **Content**: [{"principle": "For software cryptographic implementations, when direct CPA does NOT yield stable high-confidence candidates, the agent MUST first perform variance-based / energy-signature ROI exploration (e.g., np.var / np.std over sliding windows) to locate the encryption region, BEFORE deciding alignment intervals or switching leakage targets.", "reason": "Software implementations on MCU/smartc
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

### ⭐ • [canonical_pipeline_principle] Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)
- **Trigger**: Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap)
- **Rationale**: smoke iter2 Patch 003+003.1+003.2 DSv3.2 DES-7816 仍 3/5=60%，2 fail 最佳 aligned recovered key HD=6（远超 phase-14 成功 HD=3），key_search 500k-5M budget 覆盖 64^6 空间 < 0.01%。根因：agent 在 plaintext/ciphertext correlation 首带（~500-600 samples，IO/bus pre-encryption 区）对齐而非 variance peak 区（~1000-1300 samples，真 S-box 加密体）。Patch 003 Strategy A 有 variance-first 原则但 scope 限制 software MCU，DES 接触式智能卡被排除。本 strategy 将 variance-first 扩展为 device-agnostic，并明确 disjoint ROI 决策规则 + 欺骗性 alignment 指标诊断（high align_corr + low aligned CPA hc = anchor 错）。
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
All files for this session are stored in: ..\logs\exp3_Qwen3.5-397B\AES-14443_Qwen3.5-397B-A17B_DKG_20260424_043950_701
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_Qwen3.5-397B\AES-14443_Qwen3.5-397B-A17B_DKG_20260424_043950_701/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 16,322→1,115

**🤖 LLM:** 

我将对这个非接触式智能卡的AES-128 EM波形进行CPA攻击。首先让我检查波形特征，确定预处理策略。



**🔧 → `python_jupyter`**

<details><summary>Code (1723 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy')
plain = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy')
cipher = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy')

print(f"波形形状: {wave.shape}")
print(f"明文形状: {plain.shape}")
print(f"密文形状: {cipher.shape}")
print(f"波形数据类型: {wave.dtype}")
print(f"波形范围: [{wave.min():.2f}, {wave.max():.2f}]")

# 检查基线漂移 - 看前100个点的标准差
baseline_region = wave[:, :100]
baseline_std_per_trace = np.std(baseline_region, axis=1)
baseline_mean_per_trace = np.mean(baseline_region, axis=1)

print(f"\n基线区域(0-100)统计:")
print(f"  各迹线基线均值的标准差: {np.std(baseline_mean_per_trace):.4f}")
print(f"  各迹线基线均值范围: [{baseline_mean_per_trace.min():.4f}, {baseline_mean_per_trace.max():.4f}]")

# 绘制几条迹线观察特征
plt.figure(figsize=(15, 8))
for i in range(5):
    plt.plot(wave[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('First 5 Traces - Raw Waveform')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('raw_waveform.png', dpi=150)
plt.show()

# 计算整体方差，找加密区域
variance = np.var(wave, axis=0)
plt.figure(figsize=(15, 4))
plt.plot(variance)
plt.xlabel('Sample Index')
plt.ylabel('Variance')
plt.title('Variance Across All Traces - Look for Encryption Regions')
plt.grid(True, alpha=0.3)
plt.savefig('variance_plot.png', dpi=150)
plt.show()

# 找方差峰值区域
peak_indices = np.argsort(variance)[-20:]  # 最高方差的20个点
print(f"\n最高方差点索引: {sorted(peak_indices)}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (788 chars)</summary>

```
波形形状: (5000, 1900)
明文形状: (5000, 16)
密文形状: (5000, 16)
波形数据类型: float32
波形范围: [-40.36, 44.90]

基线区域(0-100)统计:
  各迹线基线均值的标准差: 0.5628
  各迹线基线均值范围: [-1.0592, 3.0647]

最高方差点索引: [np.int64(4), np.int64(5), np.int64(6), np.int64(7), np.int64(12), np.int64(13), np.int64(14), np.int64(1856), np.int64(1857), np.int64(1862), np.int64(1863), np.int64(1864), np.int64(1868), np.int64(1869), np.int64(1891), np.int64(1892), np.int64(1896), np.int64(1897), np.int64(1898), np.int64(1899)]
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\1165817104.py:34: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\1165817104.py:45: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 17,539→603

**🤖 LLM:** 



**🔧 → `python_jupyter`**

<details><summary>Code (1095 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy')

# 绘制中间区域的波形，找加密特征
plt.figure(figsize=(15, 6))

# 绘制平均波形
mean_wave = np.mean(wave, axis=0)
plt.plot(mean_wave, 'k-', linewidth=1.5, label='Mean Waveform', alpha=0.8)

# 绘制标准差
std_wave = np.std(wave, axis=0)
plt.fill_between(range(1900), mean_wave - std_wave, mean_wave + std_wave, alpha=0.3, label='±1 Std Dev')

plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Average Waveform with Standard Deviation Band')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(0, 1900)
plt.savefig('mean_std_waveform.png', dpi=150)

# 放大观察中间区域（可能包含加密操作）
plt.figure(figsize=(15, 6))
plt.plot(mean_wave, 'k-', linewidth=1.5)
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Full Mean Waveform - Look for AES Round Patterns')
plt.grid(True, alpha=0.3)
plt.xlim(100, 1800)  # 排除开头和结尾的IO区域
plt.savefig('mean_waveform_zoom.png', dpi=150)

# 检查是否有明显的周期性特征（AES 10轮）
# 计算自相关或找重复模式
print("波形统计完成，请查看保存的图片")
```
</details>

**📋 ← `python_jupyter`:** `波形统计完成，请查看保存的图片`


---

### Round 3 | tokens: 18,025→635

**🤖 LLM:** 

让我查看波形特征并决定预处理策略。根据KG知识，非接触式智能卡EM迹线通常需要：
1. 垂直对齐（基线校正）- 因为EM迹线常有基线漂移
2. 可能需要静态对齐

首先检查基线漂移情况，然后进行直接CPA探针测试。



**🔧 → `python_jupyter`**

<details><summary>Code (1386 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy')

# 检查基线漂移 - 看前200个点（应该是非加密区域）
baseline_region = wave[:, :200]
baseline_means = np.mean(baseline_region, axis=1)

print(f"基线均值统计 (0-200 samples):")
print(f"  均值: {np.mean(baseline_means):.4f}")
print(f"  标准差: {np.std(baseline_means):.4f}")
print(f"  最小值: {baseline_means.min():.4f}")
print(f"  最大值: {baseline_means.max():.4f}")
print(f"  范围: {baseline_means.max() - baseline_means.min():.4f}")

# 绘制基线均值分布
plt.figure(figsize=(10, 4))
plt.hist(baseline_means, bins=50, edgecolor='black', alpha=0.7)
plt.xlabel('Baseline Mean (samples 0-200)')
plt.ylabel('Count')
plt.title(f'Distribution of Baseline Means\nStd={np.std(baseline_means):.4f}, Range={baseline_means.max()-baseline_means.min():.4f}')
plt.grid(True, alpha=0.3)
plt.savefig('baseline_distribution.png', dpi=150)

# 绘制前10条迹线的前500个点，观察基线是否对齐
plt.figure(figsize=(15, 6))
for i in range(10):
    plt.plot(wave[i, :500], label=f'Trace {i}', alpha=0.7)
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('First 10 Traces (samples 0-500) - Check Baseline Alignment')
plt.legend(loc='upper right', fontsize=8)
plt.grid(True, alpha=0.3)
plt.savefig('baseline_alignment_check.png', dpi=150)

print("\n如果基线均值范围较大(>2-3)，说明存在DC漂移，需要垂直对齐")
```
</details>

**📋 ← `python_jupyter`:** `基线均值统计 (0-200 samples):
  均值: 1.9197
  标准差: 0.3213
  最小值: 0.5877
  最大值: 3.0686
  范围: 2.4809

如果基线均值范围较大(>2-3)，说明存在DC漂移，需要垂直对齐`


---

### Round 4 | tokens: 18,771→364

**🤖 LLM:** 

基线有一定漂移（范围约2.48）。根据KG知识，非接触式EM迹线通常需要垂直对齐。但让我先进行直接CPA探针测试，评估原始波形的攻击效果。



**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2338 chars)</summary>

```
{"recovered_key": "115033445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.144, "cpa_min_correlation": 0.0828, "n_traces": 5000, "target": "S-box_out", "plot_path": "cpa_result_20260424_044230_977983.png", "detail_file": "cpa_detail_20260424_044230_977983.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.115, "time_index": 204, "gap_pct": 41.7}, {"byte": 1, "key": "0x50", "correlation": 0.0852, "time_index": 315, "gap_pct": 9.7}, {"byte": 2, "key": "0x33", "correlation": 0.188, "time_index": 397, "gap_pct": 51.4}, {"byte": 3, "key": "0x44", "correlation": 0.2965, "time_index": 498, "gap_pct": 68.6}, {"byte": 4, "key": "0x55", "correlation": 0.0839, "time_index": 562, "gap_pct": 14.3}, {"byte": 5, "key": "0x66", "correlation": 0.1132, "time_index": 650, "gap_pct": 29.4}, {"byte": 6, "key": "0x77", "correlation": 0.1601, "time_index": 732, "gap_pct": 48.7}, {"byte": 7, "key": "0x88", "correlation": 0.1411, "time_index": 821, "gap_pct": 33.7}, {"byte": 8, "key": "0x99", "correlation": 0.1829, "time_index": 927, "gap_pct": 52.4}, {"byte": 9, "key": "0xAA", "correlation": 0.1604, "time_index": 997, "gap_pct": 49.4}, {"byte": 10, "key": "0xBB", "correlation": 0.1449, "time_index": 1109, "gap_pct": 46.5}, {"byte": 11, "key": "0xCC", "correlation": 0.0903, "time_index": 1204, "gap_pct": 10.2}, {"byte": 12, "key": "0xDD", "correlation": 0.0828, "time_index": 1286, "gap_pct": 15.6}, {"byte": 13, "key": "0xEE", "correlation": 0.1587, "time_index": 1380, "gap_pct": 48.6
...(truncated)
```
</details>


![cpa_result_20260424_044230_977983.png](./cpa_result_20260424_044230_977983.png)


---

### Round 5 | tokens: 20,185→331

**🤖 LLM:** 

非常好的结果！直接CPA就获得了13/16字节的高置信度结果。根据KG的anti-pattern规则，在green-band regime（AES >= 13/16）下，如果验证失败，应该使用key_search而不是重新做预处理。

让我先验证恢复的密钥是否正确：



**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "115033445566778899AABBCCDDEEFF00",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
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

### Round 6 | tokens: 20,929→382

**🤖 LLM:** 

正如预期，验证失败但CPA结果显示13/16字节是高置信度的。根据KG的canonical pipeline principle，在green-band + MISMATCH情况下，应该使用key_search而不是重新做预处理。

让我使用key_search来修复低置信度的字节（字节1、4、11）：



**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "recovered_key_hex": "115033445566778899AABBCCDDEEFF00",
  "cpa_detail_file": "cpa_detail_20260424_044230_977983.json",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 20,
  "max_combinations": 50000
}
```
</details>

**📋 ← `key_search`:** `{"found": true, "correct_key": "112233445566778899AABBCCDDEEFF00", "search_rounds": 2801, "unreliable_bytes": [1, 4, 11], "message": "Key found after 2801 searches: 112233445566778899AABBCCDDEEFF00"}`


---

### Round 7 | tokens: 21,433→280

**🤖 LLM:** 

太好了！key_search成功找到了正确的密钥！让我验证一下：



**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy",
  "trace_index": 0
}
```
</details>

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "36F8A59DA55B127E03833A46548601D1", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 6f97fbb2277c573866e603dfc2d185ee... → 36F8A59DA55B127E03833A46548601D1...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 8 | tokens: 21,879→382

**🤖 LLM:** 

## 攻击成功！

### 攻击总结

**目标**: 非接触式智能卡 AES-128 EM侧信道攻击

**攻击流程**:
1. **直接CPA攻击**（无预处理）:
   - 使用 S-box_out + HW 模型
   - 恢复密钥: `115033445566778899AABBCCDDEEFF00`
   - 高置信度字节: 13/16 (字节1、4、11置信度较低)
   - 平均相关系数: 0.144

2. **密钥验证**: 初始密钥验证失败（MISMATCH）

3. **key_search修复**:
   - 针对低置信度字节（1、4、11）搜索候选密钥
   - 搜索2801次后找到正确密钥
   - 正确密钥: `112233445566778899AABBCCDDEEFF00`

4. **最终验证**: ✅ 密钥验证通过

### 关键发现

- **无需预处理**: 该数据集质量较好，直接CPA即可获得13/16高置信度字节
- **KG规则应用成功**: 遵循了"green-band + MISMATCH → 使用key_search而非重新预处理"的anti-pattern规则
- **密钥差异**: CPA恢复的密钥与真实密钥仅在字节1有差异（0x50 → 0x22），这导致了整个密文不匹配（AES扩散特性）

### 恢复的密钥
```
112233445566778899AABBCCDDEEFF00
```


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 16,322 | 1,115 | 17,437 |
| 2 | 17,539 | 603 | 18,142 |
| 3 | 18,025 | 635 | 18,660 |
| 4 | 18,771 | 364 | 19,135 |
| 5 | 20,185 | 331 | 20,516 |
| 6 | 20,929 | 382 | 21,311 |
| 7 | 21,433 | 280 | 21,713 |
| 8 | 21,879 | 382 | 22,261 |
| **Total** | **155,083** | **4,092** | **159,175** |

## 8. Final Output



## 攻击成功！

### 攻击总结

**目标**: 非接触式智能卡 AES-128 EM侧信道攻击

**攻击流程**:
1. **直接CPA攻击**（无预处理）:
   - 使用 S-box_out + HW 模型
   - 恢复密钥: `115033445566778899AABBCCDDEEFF00`
   - 高置信度字节: 13/16 (字节1、4、11置信度较低)
   - 平均相关系数: 0.144

2. **密钥验证**: 初始密钥验证失败（MISMATCH）

3. **key_search修复**:
   - 针对低置信度字节（1、4、11）搜索候选密钥
   - 搜索2801次后找到正确密钥
   - 正确密钥: `112233445566778899AABBCCDDEEFF00`

4. **最终验证**: ✅ 密钥验证通过

### 关键发现

- **无需预处理**: 该数据集质量较好，直接CPA即可获得13/16高置信度字节
- **KG规则应用成功**: 遵循了"green-band + MISMATCH → 使用key_search而非重新预处理"的anti-pattern规则
- **密钥差异**: CPA恢复的密钥与真实密钥仅在字节1有差异（0x50 → 0x22），这导致了整个密文不匹配（AES扩散特性）

### 恢复的密钥
```
112233445566778899AABBCCDDEEFF00
```
