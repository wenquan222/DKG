# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_041706_520 |
| Duration | 324.3s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-14443_GLM5_DKG_20260424_041706_520` |
| Total LLM Calls | 14 |
| First Round | prompt: 15,525, completion: 1,347 |
| Last Round | prompt: 36,299, completion: 503 |
| Total Tokens | 316,257 (prompt: 306,524, completion: 9,733) |

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
["AES", "Contactless Smartcard", "EM", "CPA", "Hamming Weight", "S-box Output"]

Parsed Keywords: `["AES", "Contactless Smartcard", "EM", "CPA", "Hamming Weight", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 37457 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (39707 chars, click to expand)</summary>

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

**Search keywords** (6): AES, Contactless Smartcard, EM, CPA, Hamming Weight, S-box Output

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
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

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
- `AttackPoint:S-box Output` —[strategy_applies_to [source=expert_experience, condition=Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear, applicability=specific]]→ `Strategy:Do NOT switch leakage target family as first response to low correlation on software implementations`
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
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-14443_GLM5_DKG_20260424_041706_520
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-14443_GLM5_DKG_20260424_041706_520/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 15,525→1,347

**🤖 LLM:** 我来帮你对这个非接触式智能卡的AES-128 EM侧信道波形进行CPA攻击。让我按照标准的分析流程逐步进行。

## 第一步：波形可视化与特征分析

首先，让我查看波形的基本特征，判断是否需要预处理。

**🔧 → `python_jupyter`**

<details><summary>Code (1723 chars)</summary>

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
print(f"\n波形统计信息:")
print(f"  最小值: {wave.min():.4f}")
print(f"  最大值: {wave.max():.4f}")
print(f"  均值: {wave.mean():.4f}")
print(f"  标准差: {wave.std():.4f}")

# 绘制多条波形查看特征
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# 绘制前10条波形
for i in range(10):
    axes[0].plot(wave[i], alpha=0.5, linewidth=0.8)
axes[0].set_title('前10条波形叠加', fontsize=12)
axes[0].set_xlabel('采样点')
axes[0].set_ylabel('幅值')
axes[0].grid(True, alpha=0.3)

# 绘制单条波形
axes[1].plot(wave[0], linewidth=0.8)
axes[1].set_title('第1条波形', fontsize=12)
axes[1].set_xlabel('采样点')
axes[1].set_ylabel('幅值')
axes[1].grid(True, alpha=0.3)

# 计算并绘制方差曲线（定位加密区域）
variance = np.var(wave, axis=0)
axes[2].plot(variance, linewidth=1.2, color='red')
axes[2].set_title('方差曲线（定位加密区域）', fontsize=12)
axes[2].set_xlabel('采样点')
axes[2].set_ylabel('方差')
axes[2].grid(True, alpha=0.3)

# 标记方差峰值区域
top_var_idx = np.argsort(variance)[-20:]
axes[2].scatter(top_var_idx, variance[top_var_idx], c='blue', s=30, zorder=5, label='Top 20 variance peaks')
axes[2].legend()

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

print(f"\n方差峰值位置（Top 10）: {sorted(top_var_idx[:10])}")
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (5000, 1900)
明文数据形状: (5000, 16)
密文数据形状: (5000, 16)

波形统计信息:
  最小值: -40.3571
  最大值: 44.8985
  均值: 2.4710
  标准差: 15.6936

方差峰值位置（Top 10）: [np.int64(12), np.int64(13), np.int64(14), np.int64(1856), np.int64(1857), np.int64(1864), np.int64(1868), np.int64(1891), np.int64(1892), np.int64(1896)]
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3528691544.py:51: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 2 | tokens: 16,499→935

**🔧 → `python_jupyter`**

<details><summary>Code (1900 chars)</summary>

```python
# 检查基线漂移和对齐情况
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# 1. 检查前100个采样点的基线（假设为非加密区域）
baseline_region = wave[:, :100]
baseline_means = np.mean(baseline_region, axis=1)
axes[0, 0].plot(baseline_means, linewidth=0.8)
axes[0, 0].set_title('前100采样点的基线均值（per trace）', fontsize=11)
axes[0, 0].set_xlabel('Trace编号')
axes[0, 0].set_ylabel('基线均值')
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].axhline(y=np.mean(baseline_means), color='r', linestyle='--', label=f'平均: {np.mean(baseline_means):.2f}')
axes[0, 0].legend()

print(f"基线均值统计:")
print(f"  均值: {baseline_means.mean():.4f}")
print(f"  标准差: {baseline_means.std():.4f}")
print(f"  范围: [{baseline_means.min():.4f}, {baseline_means.max():.4f}]")

# 2. 检查波形对齐情况 - 叠加显示前50条波形
for i in range(50):
    axes[0, 1].plot(wave[i], alpha=0.3, linewidth=0.5)
axes[0, 1].set_title('前50条波形叠加（检查对齐）', fontsize=11)
axes[0, 1].set_xlabel('采样点')
axes[0, 1].set_ylabel('幅值')
axes[0, 1].grid(True, alpha=0.3)

# 3. 查看中间区域（假设加密区域）
mid_start, mid_end = 200, 1700
mid_wave = wave[:, mid_start:mid_end]
for i in range(20):
    axes[1, 0].plot(range(mid_start, mid_end), mid_wave[i], alpha=0.5, linewidth=0.8)
axes[1, 0].set_title(f'中间区域 ({mid_start}-{mid_end}) 波形', fontsize=11)
axes[1, 0].set_xlabel('采样点')
axes[1, 0].set_ylabel('幅值')
axes[1, 0].grid(True, alpha=0.3)

# 4. 方差曲线 - 更详细的视图
variance = np.var(wave, axis=0)
axes[1, 1].plot(variance, linewidth=1, color='red')
axes[1, 1].set_title('方差曲线（全波形）', fontsize=11)
axes[1, 1].set_xlabel('采样点')
axes[1, 1].set_ylabel('方差')
axes[1, 1].grid(True, alpha=0.3)

# 标记可能的加密区域
# 找到方差最大的连续区域（排除开头和结尾的IO区域）
var_smoothed = np.convolve(variance, np.ones(50)/50, mode='same')
peak_region = np.argsort(var_smoothed)[-100:]
peak_region_sorted = sorted(peak_region)
print(f"\n平滑后方差峰值区域（排除首尾）: {[x for x in peak_region_sorted if 100 < x < 1800][:20]}")

plt.tight_layout()
plt.savefig('baseline_alignment_check.png', dpi=150)
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `基线均值统计:
  均值: 1.2507
  标准差: 0.5628
  范围: [-1.0592, 3.0647]

平滑后方差峰值区域（排除首尾）: []
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1956072309.py:55: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 17,402→793

**🔧 → `python_jupyter`**

<details><summary>Code (1941 chars)</summary>

```python
# 更详细地分析方差曲线，寻找加密区域
variance = np.var(wave, axis=0)

# 平滑方差曲线
from scipy.ndimage import uniform_filter1d
var_smoothed = uniform_filter1d(variance, size=50)

# 找到方差峰值
peak_indices = np.argsort(var_smoothed)[::-1][:50]
peak_indices_sorted = sorted(peak_indices)

print("方差峰值位置（Top 50，按位置排序）:")
print(peak_indices_sorted)

# 绘制方差曲线并标记峰值
fig, axes = plt.subplots(2, 1, figsize=(14, 8))

axes[0].plot(variance, linewidth=0.8, alpha=0.7, label='原始方差')
axes[0].plot(var_smoothed, linewidth=1.5, color='red', label='平滑方差')
axes[0].scatter(peak_indices_sorted[:20], var_smoothed[peak_indices_sorted[:20]], 
                c='green', s=50, zorder=5, label='Top 20 peaks')
axes[0].set_title('方差曲线分析', fontsize=12)
axes[0].set_xlabel('采样点')
axes[0].set_ylabel('方差')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 查看不同区域的波形特征
# 分段查看
regions = [(0, 200), (200, 600), (600, 1000), (1000, 1400), (1400, 1700), (1700, 1900)]
for i, (start, end) in enumerate(regions):
    region_var = np.mean(variance[start:end])
    print(f"区域 {start}-{end}: 平均方差 = {region_var:.4f}")

# 绘制分段方差
segment_vars = [np.mean(variance[s:e]) for s, e in regions]
axes[1].bar(range(len(regions)), segment_vars, color='steelblue', alpha=0.7)
axes[1].set_xticks(range(len(regions)))
axes[1].set_xticklabels([f'{s}-{e}' for s, e in regions], rotation=45)
axes[1].set_title('分段平均方差', fontsize=12)
axes[1].set_xlabel('采样区间')
axes[1].set_ylabel('平均方差')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('variance_detailed_analysis.png', dpi=150)
plt.show()

# 找到方差最大的连续区域（排除首尾IO区域）
# 使用滑动窗口找到方差最大的区域
window_size = 200
max_var = 0
best_start = 0
for start in range(100, 1700, 50):
    end = start + window_size
    if end <= 1900:
        region_var = np.mean(variance[start:end])
        if region_var > max_var:
            max_var = region_var
            best_start = start

print(f"\n方差最大的200点窗口: {best_start}-{best_start+window_size}, 平均方差 = {max_var:.4f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1133 chars)</summary>

```
方差峰值位置（Top 50，按位置排序）:
[np.int64(0), np.int64(1), np.int64(2), np.int64(3), np.int64(4), np.int64(5), np.int64(6), np.int64(7), np.int64(8), np.int64(9), np.int64(10), np.int64(11), np.int64(12), np.int64(13), np.int64(14), np.int64(15), np.int64(16), np.int64(17), np.int64(18), np.int64(19), np.int64(20), np.int64(1849), np.int64(1872), np.int64(1873), np.int64(1874), np.int64(1875), np.int64(1876), np.int64(1877), np.int64(1878), np.int64(1879), np.int64(1880), np.int64(1881), np.int64(1882), np.int64(1883), np.int64(1884), np.int64(1885), np.int64(1886), np.int64(1887), np.int64(1888), np.int64(1889), np.int64(1890), np.int64(1891), np.int64(1892), np.int64(1893), np.int64(1894), np.int64(1895), np.int64(1896), np.int64(1897), np.int64(1898), np.int64(1899)]
区域 0-200: 平均方差 = 32.2516
区域 200-600: 平均方差 = 7.8672
区域 600-1000: 平均方差 = 12.1875
区域 1000-1400: 平均方差 = 18.2044
区域 1400-1700: 平均方差 = 27.1704
区域 1700-1900: 平均方差 = 61.4159

方差最大的200点窗口: 1650-1850, 平均方差 = 36.9233
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\738291130.py:47: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 4 | tokens: 18,609→736

**🔧 → `python_jupyter`**

<details><summary>Code (1495 chars)</summary>

```python
# 查看中间区域的详细波形特征
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 中间区域（200-1700）的波形
mid_wave = wave[0, 200:1700]
axes[0, 0].plot(range(200, 1700), mid_wave, linewidth=0.8)
axes[0, 0].set_title('中间区域波形 (200-1700)', fontsize=11)
axes[0, 0].set_xlabel('采样点')
axes[0, 0].set_ylabel('幅值')
axes[0, 0].grid(True, alpha=0.3)

# 2. 叠加多条波形查看对齐情况
for i in range(30):
    axes[0, 1].plot(range(200, 1700), wave[i, 200:1700], alpha=0.4, linewidth=0.6)
axes[0, 1].set_title('中间区域30条波形叠加', fontsize=11)
axes[0, 1].set_xlabel('采样点')
axes[0, 1].set_ylabel('幅值')
axes[0, 1].grid(True, alpha=0.3)

# 3. 中间区域的方差曲线
mid_variance = np.var(wave[:, 200:1700], axis=0)
axes[1, 0].plot(range(200, 1700), mid_variance, linewidth=1, color='red')
axes[1, 0].set_title('中间区域方差曲线', fontsize=11)
axes[1, 0].set_xlabel('采样点')
axes[1, 0].set_ylabel('方差')
axes[1, 0].grid(True, alpha=0.3)

# 标记方差峰值
mid_peaks = np.argsort(mid_variance)[-10:] + 200
axes[1, 0].scatter(mid_peaks, mid_variance[mid_peaks - 200], c='blue', s=40, zorder=5)

# 4. 查看特定区域的波形细节
# 选择方差相对较高的区域
detail_start, detail_end = 600, 1200
for i in range(20):
    axes[1, 1].plot(range(detail_start, detail_end), wave[i, detail_start:detail_end], alpha=0.5, linewidth=0.7)
axes[1, 1].set_title(f'细节区域波形 ({detail_start}-{detail_end})', fontsize=11)
axes[1, 1].set_xlabel('采样点')
axes[1, 1].set_ylabel('幅值')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('middle_region_analysis.png', dpi=150)
plt.show()

print(f"中间区域方差峰值位置: {sorted(mid_peaks)}")
```
</details>

**📋 ← `python_jupyter`:** `中间区域方差峰值位置: [np.int64(1422), np.int64(1510), np.int64(1511), np.int64(1641), np.int64(1642), np.int64(1643), np.int64(1648), np.int64(1649), np.int64(1650), np.int64(1655)]
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\479814603.py:44: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 5 | tokens: 19,371→292

**🤖 LLM:** 现在让我进行直接CPA攻击，看看是否需要预处理：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 30
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2338 chars)</summary>

```
{"recovered_key": "115033445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.144, "cpa_min_correlation": 0.0828, "n_traces": 5000, "target": "S-box_out", "plot_path": "cpa_result_20260424_041907_917090.png", "detail_file": "cpa_detail_20260424_041907_917090.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.115, "time_index": 204, "gap_pct": 41.7}, {"byte": 1, "key": "0x50", "correlation": 0.0852, "time_index": 315, "gap_pct": 9.7}, {"byte": 2, "key": "0x33", "correlation": 0.188, "time_index": 397, "gap_pct": 51.4}, {"byte": 3, "key": "0x44", "correlation": 0.2965, "time_index": 498, "gap_pct": 68.6}, {"byte": 4, "key": "0x55", "correlation": 0.0839, "time_index": 562, "gap_pct": 14.3}, {"byte": 5, "key": "0x66", "correlation": 0.1132, "time_index": 650, "gap_pct": 29.4}, {"byte": 6, "key": "0x77", "correlation": 0.1601, "time_index": 732, "gap_pct": 48.7}, {"byte": 7, "key": "0x88", "correlation": 0.1411, "time_index": 821, "gap_pct": 33.7}, {"byte": 8, "key": "0x99", "correlation": 0.1829, "time_index": 927, "gap_pct": 52.4}, {"byte": 9, "key": "0xAA", "correlation": 0.1604, "time_index": 997, "gap_pct": 49.4}, {"byte": 10, "key": "0xBB", "correlation": 0.1449, "time_index": 1109, "gap_pct": 46.5}, {"byte": 11, "key": "0xCC", "correlation": 0.0903, "time_index": 1204, "gap_pct": 10.2}, {"byte": 12, "key": "0xDD", "correlation": 0.0828, "time_index": 1286, "gap_pct": 15.6}, {"byte": 13, "key": "0xEE", "correlation": 0.1587, "time_index": 1380, "gap_pct": 48.6
...(truncated)
```
</details>


![cpa_result_20260424_041907_917090.png](./cpa_result_20260424_041907_917090.png)


---

### Round 6 | tokens: 20,532→291

**🤖 LLM:** 很好！直接CPA攻击得到了**13/16高置信度字节**，这是一个非常好的结果。让我先验证密钥：

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

### Round 7 | tokens: 21,086→435

**🤖 LLM:** 验证失败，但这是正常的。根据知识图谱策略，在green-band regime（13/16高置信度）下，应该使用key_search来修正低置信度字节。让我执行key_search：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "recovered_key_hex": "115033445566778899AABBCCDDEEFF00",
  "cpa_detail_file": "cpa_detail_20260424_041907_917090.json",
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

### Round 8 | tokens: 21,433→220

**🤖 LLM:** 太好了！key_search成功找到了正确的密钥！让我验证一下：

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

### Round 9 | tokens: 21,739→489

**🤖 LLM:** 让我再验证几个其他trace以确保密钥完全正确：

**🔧 → `python_jupyter`**

<details><summary>Code (1200 chars)</summary>

```python
from Crypto.Cipher import AES
import numpy as np

# 加载数据
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy')

# 恢复的密钥
key_hex = "112233445566778899AABBCCDDEEFF00"
key_bytes = bytes.fromhex(key_hex)

# 创建AES cipher
cipher_obj = AES.new(key_bytes, AES.MODE_ECB)

# 验证多个trace
print("验证多个trace的加密结果:")
print("=" * 80)
success_count = 0
for i in [0, 100, 500, 1000, 2000, 3000, 4000, 4999]:
    pt = plain[i].tobytes()
    expected_ct = cipher[i].tobytes()
    computed_ct = cipher_obj.encrypt(pt)
    
    match = computed_ct == expected_ct
    success_count += match
    
    print(f"Trace {i:4d}: {'✓ MATCH' if match else '✗ MISMATCH'}")
    if not match:
        print(f"  Expected:  {expected_ct.hex().upper()}")
        print(f"  Computed:  {computed_ct.hex().upper()}")

print("=" * 80)
print(f"验证结果: {success_count}/8 traces匹配")

if success_count == 8:
    print("\n🎉 密钥恢复成功！")
    print(f"恢复的AES-128密钥: {key_hex}")
else:
    print("\n⚠️ 部分trace验证失败，可能需要进一步检查")
```
</details>

**📋 ← `python_jupyter`:** `验证多个trace的加密结果:
================================================================================
Trace    0: ✓ MATCH
Trace  100: ✓ MATCH
Trace  500: ✓ MATCH
Trace 1000: ✓ MATCH
Trace 2000: ✓ MATCH
Trace 3000: ✓ MATCH
Trace 4000: ✓ MATCH
Trace 4999: ✓ MATCH
================================================================================
验证结果: 8/8 traces匹配

🎉 密钥恢复成功！
恢复的AES-128密钥: 112233445566778899AABBCCDDEEFF00`


---

### Round 10 | tokens: 22,333→1,647

**🤖 LLM:** 完美！让我生成最终的分析报告：

**🔧 → `python_jupyter`**

<details><summary>Code (3767 chars)</summary>

```python
import json
import matplotlib.pyplot as plt
import numpy as np

# 读取CPA详细结果
with open('cpa_detail_20260424_041907_917090.json', 'r') as f:
    cpa_detail = json.load(f)

# 创建综合报告
print("=" * 80)
print("AES-128 非接触式智能卡 EM侧信道 CPA攻击报告")
print("=" * 80)

print("\n【数据集信息】")
print(f"  波形文件: AES-128-14443-5000traces-1900points_wave.npy")
print(f"  明文文件: AES-128-14443-5000traces-1900points_plain.npy")
print(f"  密文文件: AES-128-14443-5000traces-1900points_cipher.npy")
print(f"  Trace数量: 5000")
print(f"  采样点数: 1900")
print(f"  侧信道类型: EM (电磁)")

print("\n【攻击配置】")
print(f"  攻击算法: AES-128 CPA")
print(f"  攻击目标: S-box output (第一轮)")
print(f"  泄漏模型: Hamming Weight (HW)")
print(f"  候选数量: 30 per byte")

print("\n【直接CPA结果】")
print(f"  恢复密钥: 115033445566778899AABBCCDDEEFF00")
print(f"  平均相关系数: 0.144")
print(f"  最小相关系数: 0.0828")
print(f"  高置信度字节: 13/16 (81.25%)")

print("\n【低置信度字节分析】")
low_conf = cpa_detail['low_confidence_subkeys']
for item in low_conf:
    byte_idx = item['subkey_index']
    gap = item['top1_top2_gap'] * 100
    print(f"  Byte {byte_idx:2d}: gap = {gap:5.1f}% (需要修正)")

print("\n【Key Search结果】")
print(f"  搜索策略: 针对低置信度字节 [1, 4, 11]")
print(f"  搜索轮次: 6301")
print(f"  最终密钥: 112233445566778899AABBCCDDEEFF00")

print("\n【密钥验证】")
print(f"  验证状态: ✓ 全部通过 (8/8 traces)")
print(f"  最终结果: 🎉 密钥恢复成功！")

print("\n【密钥对比】")
print(f"  CPA初始密钥: 11 50 33 44 55 66 77 88 99 AA BB CC DD EE FF 00")
print(f"  正确密钥:     11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00")
print(f"  错误字节:     Byte 1 (0x50→0x22), Byte 4 (0x55→0x55), Byte 11 (0xCC→0xCC)")
print(f"  实际修正:     Byte 1: 0x50 → 0x22")

# 绘制CPA结果可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 每个字节的相关系数
correlations = [item['correlation'] for item in cpa_detail['per_byte']]
axes[0, 0].bar(range(16), correlations, color='steelblue', alpha=0.7)
axes[0, 0].axhline(y=np.mean(correlations), color='red', linestyle='--', 
                   label=f'平均: {np.mean(correlations):.3f}')
axes[0, 0].set_title('各字节相关系数', fontsize=12)
axes[0, 0].set_xlabel('字节索引')
axes[0, 0].set_ylabel('相关系数')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3, axis='y')

# 2. Gap百分比
gaps = [item['gap_pct'] for item in cpa_detail['per_byte']]
colors = ['green' if g >= 15 else 'red' for g in gaps]
axes[0, 1].bar(range(16), gaps, color=colors, alpha=0.7)
axes[0, 1].axhline(y=15, color='orange', linestyle='--', linewidth=2, label='阈值 15%')
axes[0, 1].set_title('各字节Gap百分比 (绿色=高置信度, 红色=低置信度)', fontsize=12)
axes[0, 1].set_xlabel('字节索引')
axes[0, 1].set_ylabel('Gap (%)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 3. 泄漏时间点分布
time_indices = [item['time_index'] for item in cpa_detail['per_byte']]
axes[1, 0].scatter(time_indices, correlations, s=100, c='steelblue', alpha=0.7, edgecolors='black')
for i, (t, c) in enumerate(zip(time_indices, correlations)):
    axes[1, 0].annotate(f'B{i}', (t, c), fontsize=8, ha='center', va='bottom')
axes[1, 0].set_title('泄漏时间点分布', fontsize=12)
axes[1, 0].set_xlabel('采样点索引')
axes[1, 0].set_ylabel('相关系数')
axes[1, 0].grid(True, alpha=0.3)

# 4. 密钥恢复过程总结
summary_text = f"""
CPA攻击成功总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
数据集: 5000 traces × 1900 points
设备类型: 非接触式智能卡
侧信道: EM (电磁)

攻击配置:
  • 目标: S-box output
  • 模型: Hamming Weight
  • 候选数: 30 per byte

直接CPA结果:
  • 高置信度: 13/16 (81.25%)
  • 平均相关系数: 0.144

Key Search:
  • 目标字节: [1, 4, 11]
  • 搜索轮次: 6301
  • 结果: 成功

最终密钥:
  112233445566778899AABBCCDDEEFF00

验证: ✓ 全部通过
"""
axes[1, 1].text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
                verticalalignment='center', transform=axes[1, 1].transAxes)
axes[1, 1].axis('off')

plt.tight_layout()
plt.savefig('final_attack_report.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "=" * 80)
print("分析报告已保存至: final_attack_report.png")
print("=" * 80)
```
</details>

**❌ ← `python_jupyter` Error:**

```
================================================================================
AES-128 非接触式智能卡 EM侧信道 CPA攻击报告
================================================================================

【数据集信息】
  波形文件: AES-128-14443-5000traces-1900points_wave.npy
  明文文件: AES-128-14443-5000traces-1900points_plain.npy
  密文文件: AES-128-14443-5000traces-1900points_cipher.npy
  Trace数量: 5000
  采样点数: 1900
  侧信道类型: EM (电磁)

【攻击配置】
  攻击算法: AES-128 CPA
  攻击目标: S-box output (第一轮)
  泄漏模型: Hamming Weight (HW)
  候选数量: 30 per byte

【直接CPA结果】
  恢复密钥: 115033445566778899AABBCCDDEEFF00
  平均相关系数: 0.144
  最小相关系数: 0.0828
  高置信度字节: 13/16 (81.25%)

【低置信度字节分析】

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[215][39m[32m, line 35[39m
[32m     32[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m  高置信度字节: 13/16 (81.25%)[39m[33m"[39m)
[32m     34[39m [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33m【低置信度字节分析】[39m[33m"[39m)
[32m---> [39m[32m35[39m low_conf = [43mcpa_detail[49m[43m[[49m[33;43m'[39;49m[33;43mlow_confidence_subkeys[39;49m[33;43m'[39;49m[43m][49m
[32m     36[39m [38;5;28;01mfor[39;00m item [38;5;129;01min[39;00m low_conf:
[32m     37[39m     byte_idx = item[[33m'[39m[33msubkey_index[39m[33m'[39m]

[31mKeyError[39m: 'low_confidence_subkeys'
```


---

### Round 11 | tokens: 24,596→146

**🔧 → `python_jupyter`**

<details><summary>Code (293 chars)</summary>

```python
import json

# 读取CPA详细结果
with open('cpa_detail_20260424_041907_917090.json', 'r') as f:
    cpa_detail = json.load(f)

print("CPA detail JSON keys:")
print(cpa_detail.keys())

# 检查per_byte的内容
print("\nper_byte示例 (前3个字节):")
for i in range(3):
    print(f"Byte {i}: {cpa_detail['per_byte'][i]}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
CPA detail JSON keys:
dict_keys(['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results'])

per_byte示例 (前3个字节):

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[216][39m[32m, line 13[39m
[32m     11[39m [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33mper_byte示例 (前3个字节):[39m[33m"[39m)
[32m     12[39m [38;5;28;01mfor[39;00m i [38;5;129;01min[39;00m [38;5;28mrange[39m([32m3[39m):
[32m---> [39m[32m13[39m     [38;5;28mprint[39m([33mf[39m[33m"[39m[33mByte [39m[38;5;132;01m{[39;00mi[38;5;132;01m}[39;00m[33m: [39m[38;5;132;01m{[39;00m[43mcpa_detail[49m[43m[[49m[33;43m'[39;49m[33;43mper_byte[39;49m[33;43m'[39;49m[43m][49m[i][38;5;132;01m}[39;00m[33m"[39m)

[31mKeyError[39m: 'per_byte'
```


---

### Round 12 | tokens: 25,156→96

**🔧 → `python_jupyter`** `{
  "code": "import json\n\n# 读取CPA详细结果\nwith open('cpa_detail_20260424_041907_917090.json', 'r') as f:\n    cpa_detail = json.load(f)\n\nprint(\"CPA detail完整结构:\")\nprint(json.dumps(cpa_detail, indent=2)[:2000])"
}`

<details><summary><b>📋 ← `python_jupyter`</b> (2016 chars)</summary>

```
CPA detail完整结构:
{
  "n_traces": 5000,
  "n_points": 1900,
  "leakage_model": "HW",
  "target": "S-box_out",
  "corr_mode": "abs",
  "results": [
    {
      "byte": 0,
      "topK": [
        {
          "key": 17,
          "score": 0.11500355776367749,
          "time_index": 204
        },
        {
          "key": 31,
          "score": 0.06707882325371158,
          "time_index": 210
        },
        {
          "key": 45,
          "score": 0.06496216755967821,
          "time_index": 203
        },
        {
          "key": 197,
          "score": 0.06037228521338876,
          "time_index": 204
        },
        {
          "key": 50,
          "score": 0.05911140464164049,
          "time_index": 1299
        },
        {
          "key": 120,
          "score": 0.05857376934842497,
          "time_index": 199
        },
        {
          "key": 212,
          "score": 0.057399196559422806,
          "time_index": 833
        },
        {
          "key": 10,
          "score": 0.057330033530380756,
          "time_index": 204
        },
        {
          "key": 143,
          "score": 0.056373932508510555,
          "time_index": 373
        },
        {
          "key": 172,
          "score": 0.05626282996788417,
          "time_index": 204
        },
        {
          "key": 106,
          "score": 0.055869870532786664,
          "time_index": 83
        },
        {
          "key": 173,
          "score": 0.05509270592592687,
          "time_index": 
...(truncated)
```
</details>


---

### Round 13 | tokens: 25,944→1,803

**🔧 → `python_jupyter`**

<details><summary>Code (4361 chars)</summary>

```python
import json
import matplotlib.pyplot as plt
import numpy as np

# 读取CPA详细结果
with open('cpa_detail_20260424_041907_917090.json', 'r') as f:
    cpa_detail = json.load(f)

# 提取每个字节的最佳候选
per_byte_stats = []
for result in cpa_detail['results']:
    byte_idx = result['byte']
    top1 = result['topK'][0]
    top2 = result['topK'][1]
    
    gap = (top1['score'] - top2['score']) / top1['score'] * 100 if top1['score'] > 0 else 0
    
    per_byte_stats.append({
        'byte': byte_idx,
        'key': top1['key'],
        'correlation': top1['score'],
        'time_index': top1['time_index'],
        'gap_pct': gap
    })

# 创建综合报告
print("=" * 80)
print("AES-128 非接触式智能卡 EM侧信道 CPA攻击报告")
print("=" * 80)

print("\n【数据集信息】")
print(f"  波形文件: AES-128-14443-5000traces-1900points_wave.npy")
print(f"  明文文件: AES-128-14443-5000traces-1900points_plain.npy")
print(f"  密文文件: AES-128-14443-5000traces-1900points_cipher.npy")
print(f"  Trace数量: 5000")
print(f"  采样点数: 1900")
print(f"  侧信道类型: EM (电磁)")

print("\n【攻击配置】")
print(f"  攻击算法: AES-128 CPA")
print(f"  攻击目标: S-box output (第一轮)")
print(f"  泄漏模型: Hamming Weight (HW)")
print(f"  候选数量: 30 per byte")

print("\n【直接CPA结果】")
print(f"  恢复密钥: 115033445566778899AABBCCDDEEFF00")
avg_corr = np.mean([s['correlation'] for s in per_byte_stats])
min_corr = np.min([s['correlation'] for s in per_byte_stats])
print(f"  平均相关系数: {avg_corr:.4f}")
print(f"  最小相关系数: {min_corr:.4f}")

high_conf_count = sum(1 for s in per_byte_stats if s['gap_pct'] >= 15)
print(f"  高置信度字节: {high_conf_count}/16 ({high_conf_count/16*100:.1f}%)")

print("\n【低置信度字节分析】")
low_conf_bytes = [s for s in per_byte_stats if s['gap_pct'] < 15]
for item in low_conf_bytes:
    print(f"  Byte {item['byte']:2d}: gap = {item['gap_pct']:5.1f}% (需要修正)")

print("\n【Key Search结果】")
print(f"  搜索策略: 针对低置信度字节 [1, 4, 11]")
print(f"  搜索轮次: 6301")
print(f"  最终密钥: 112233445566778899AABBCCDDEEFF00")

print("\n【密钥验证】")
print(f"  验证状态: ✓ 全部通过 (8/8 traces)")
print(f"  最终结果: 🎉 密钥恢复成功！")

print("\n【密钥对比】")
print(f"  CPA初始密钥: 11 50 33 44 55 66 77 88 99 AA BB CC DD EE FF 00")
print(f"  正确密钥:     11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00")
print(f"  错误字节:     Byte 1 (0x50→0x22)")

# 绘制CPA结果可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 每个字节的相关系数
correlations = [s['correlation'] for s in per_byte_stats]
axes[0, 0].bar(range(16), correlations, color='steelblue', alpha=0.7)
axes[0, 0].axhline(y=np.mean(correlations), color='red', linestyle='--', 
                   label=f'平均: {np.mean(correlations):.3f}')
axes[0, 0].set_title('各字节相关系数', fontsize=12)
axes[0, 0].set_xlabel('字节索引')
axes[0, 0].set_ylabel('相关系数')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3, axis='y')

# 2. Gap百分比
gaps = [s['gap_pct'] for s in per_byte_stats]
colors = ['green' if g >= 15 else 'red' for g in gaps]
axes[0, 1].bar(range(16), gaps, color=colors, alpha=0.7)
axes[0, 1].axhline(y=15, color='orange', linestyle='--', linewidth=2, label='阈值 15%')
axes[0, 1].set_title('各字节Gap百分比 (绿色=高置信度, 红色=低置信度)', fontsize=12)
axes[0, 1].set_xlabel('字节索引')
axes[0, 1].set_ylabel('Gap (%)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 3. 泄漏时间点分布
time_indices = [s['time_index'] for s in per_byte_stats]
axes[1, 0].scatter(time_indices, correlations, s=100, c='steelblue', alpha=0.7, edgecolors='black')
for i, (t, c) in enumerate(zip(time_indices, correlations)):
    axes[1, 0].annotate(f'B{i}', (t, c), fontsize=8, ha='center', va='bottom')
axes[1, 0].set_title('泄漏时间点分布', fontsize=12)
axes[1, 0].set_xlabel('采样点索引')
axes[1, 0].set_ylabel('相关系数')
axes[1, 0].grid(True, alpha=0.3)

# 4. 密钥恢复过程总结
summary_text = f"""
CPA攻击成功总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
数据集: 5000 traces × 1900 points
设备类型: 非接触式智能卡
侧信道: EM (电磁)

攻击配置:
  • 目标: S-box output
  • 模型: Hamming Weight
  • 候选数: 30 per byte

直接CPA结果:
  • 高置信度: {high_conf_count}/16 ({high_conf_count/16*100:.1f}%)
  • 平均相关系数: {avg_corr:.3f}

Key Search:
  • 目标字节: [1, 4, 11]
  • 搜索轮次: 6301
  • 结果: 成功

最终密钥:
  112233445566778899AABBCCDDEEFF00

验证: ✓ 全部通过
"""
axes[1, 1].text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
                verticalalignment='center', transform=axes[1, 1].transAxes)
axes[1, 1].axis('off')

plt.tight_layout()
plt.savefig('final_attack_report.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "=" * 80)
print("分析报告已保存至: final_attack_report.png")
print("=" * 80)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (25902 chars)</summary>

```
================================================================================
AES-128 非接触式智能卡 EM侧信道 CPA攻击报告
================================================================================

【数据集信息】
  波形文件: AES-128-14443-5000traces-1900points_wave.npy
  明文文件: AES-128-14443-5000traces-1900points_plain.npy
  密文文件: AES-128-14443-5000traces-1900points_cipher.npy
  Trace数量: 5000
  采样点数: 1900
  侧信道类型: EM (电磁)

【攻击配置】
  攻击算法: AES-128 CPA
  攻击目标: S-box output (第一轮)
  泄漏模型: Hamming Weight (HW)
  候选数量: 30 per byte

【直接CPA结果】
  恢复密钥: 115033445566778899AABBCCDDEEFF00
  平均相关系数: 0.1440
  最小相关系数: 0.0828
  高置信度字节: 13/16 (81.2%)

【低置信度字节分析】
  Byte  1: gap =   9.7% (需要修正)
  Byte  4: gap =  14.3% (需要修正)
  Byte 11: gap =  10.2% (需要修正)

【Key Search结果】
  搜索策略: 针对低置信度字节 [1, 4, 11]
  搜索轮次: 6301
  最终密钥: 112233445566778899AABBCCDDEEFF00

【密钥验证】
  验证状态: ✓ 全部通过 (8/8 traces)
  最终结果: 🎉 密钥恢复成功！

【密钥对比】
  CPA初始密钥: 11 50 33 44 55 66 77 88 99 AA BB CC DD EE FF 00
  正确密钥:     11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00
  错误字节:     Byte 1 (0x50→0x22)
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2980074824.py:140: UserWarning: Glyph 25915 (\N{CJK UNIFIED IDEOGRAPH-653B}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2980074824.py:140: UserWarning: Glyph 20987 (\N{CJK UNIFIED IDEOGRAPH-51FB}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2980074824.py:140: UserWarning
...(truncated)
```
</details>


![final_attack_report.png](./final_attack_report.png)


---

### Round 14 | tokens: 36,299→503

<details><summary><b>🤖 LLM Reasoning</b> (923 chars)</summary>

## 🎉 攻击成功完成！

我已经成功对非接触式智能卡的AES-128 EM侧信道波形进行了CPA攻击，完整流程如下：

### 📊 攻击总结

**数据集信息：**
- 波形：5000 traces × 1900 points
- 设备：非接触式智能卡（ISO 14443）
- 侧信道：电磁（EM）

**攻击配置：**
- 目标：S-box output（第一轮）
- 泄漏模型：Hamming Weight (HW)
- 候选数：30 per byte

**攻击结果：**

| 阶段 | 结果 |
|------|------|
| 直接CPA | 13/16 高置信度字节 (81.2%) |
| 平均相关系数 | 0.144 |
| 低置信度字节 | Byte 1, 4, 11 (gap < 15%) |
| Key Search | 6301轮搜索后成功 |
| **最终密钥** | **112233445566778899AABBCCDDEEFF00** |
| 验证状态 | ✅ 全部通过 (8/8 traces) |

### 🔍 关键发现

1. **波形质量良好**：直接CPA就获得了13/16的高置信度字节，说明波形对齐良好，信噪比较高

2. **泄漏特征明显**：16个字节的泄漏时间点分布在95-1444采样点范围内，呈现明显的时序特征

3. **Key Search高效**：仅6301次搜索就找到了正确密钥，修正了Byte 1的错误（0x50→0x22）

4. **符合预期**：非接触式智能卡的EM侧信道泄漏符合软件实现的Hamming Weight模型

### 📁 生成的文件

- `cpa_result_20260424_041907_917090.png` - CPA结果可视化
- `cpa_detail_20260424_041907_917090.json` - CPA详细结果（包含topK候选）
- `final_attack_report.png` - 综合分析报告

**恢复的AES-128密钥：`112233445566778899AABBCCDDEEFF00`**

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 15,525 | 1,347 | 16,872 |
| 2 | 16,499 | 935 | 17,434 |
| 3 | 17,402 | 793 | 18,195 |
| 4 | 18,609 | 736 | 19,345 |
| 5 | 19,371 | 292 | 19,663 |
| 6 | 20,532 | 291 | 20,823 |
| 7 | 21,086 | 435 | 21,521 |
| 8 | 21,433 | 220 | 21,653 |
| 9 | 21,739 | 489 | 22,228 |
| 10 | 22,333 | 1,647 | 23,980 |
| 11 | 24,596 | 146 | 24,742 |
| 12 | 25,156 | 96 | 25,252 |
| 13 | 25,944 | 1,803 | 27,747 |
| 14 | 36,299 | 503 | 36,802 |
| **Total** | **306,524** | **9,733** | **316,257** |

## 8. Final Output

## 🎉 攻击成功完成！

我已经成功对非接触式智能卡的AES-128 EM侧信道波形进行了CPA攻击，完整流程如下：

### 📊 攻击总结

**数据集信息：**
- 波形：5000 traces × 1900 points
- 设备：非接触式智能卡（ISO 14443）
- 侧信道：电磁（EM）

**攻击配置：**
- 目标：S-box output（第一轮）
- 泄漏模型：Hamming Weight (HW)
- 候选数：30 per byte

**攻击结果：**

| 阶段 | 结果 |
|------|------|
| 直接CPA | 13/16 高置信度字节 (81.2%) |
| 平均相关系数 | 0.144 |
| 低置信度字节 | Byte 1, 4, 11 (gap < 15%) |
| Key Search | 6301轮搜索后成功 |
| **最终密钥** | **112233445566778899AABBCCDDEEFF00** |
| 验证状态 | ✅ 全部通过 (8/8 traces) |

### 🔍 关键发现

1. **波形质量良好**：直接CPA就获得了13/16的高置信度字节，说明波形对齐良好，信噪比较高

2. **泄漏特征明显**：16个字节的泄漏时间点分布在95-1444采样点范围内，呈现明显的时序特征

3. **Key Search高效**：仅6301次搜索就找到了正确密钥，修正了Byte 1的错误（0x50→0x22）

4. **符合预期**：非接触式智能卡的EM侧信道泄漏符合软件实现的Hamming Weight模型

### 📁 生成的文件

- `cpa_result_20260424_041907_917090.png` - CPA结果可视化
- `cpa_detail_20260424_041907_917090.json` - CPA详细结果（包含topK候选）
- `final_attack_report.png` - 综合分析报告

**恢复的AES-128密钥：`112233445566778899AABBCCDDEEFF00`**
