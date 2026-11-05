# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_052239_103 |
| Duration | 202.2s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-STM32F429_GLM5_DKG_20260424_052239_103` |
| Total LLM Calls | 12 |
| First Round | prompt: 16,643, completion: 1,035 |
| Last Round | prompt: 36,427, completion: 587 |
| Total Tokens | 273,179 (prompt: 264,785, completion: 8,394) |

## 3. User Query

```
帮我对一个STM32F429 MCU软件实现的AES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个STM32F429 MCU软件实现的AES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy'"

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
["AES", "STM32F429", "MCU", "EM", "CPA", "Software"]

Parsed Keywords: `["AES", "STM32F429", "MCU", "EM", "CPA", "Software"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 42123 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (44381 chars, click to expand)</summary>

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

**Search keywords** (6): AES, STM32F429, MCU, EM, CPA, Software

**Summary**: 33 upper entities, 30 relationships, 21 diagnostic chains, 12 strategies


## 1. Upper Layer Entities (33)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### DeviceClass (15)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **STM32F429** — category=MCU, bus_width=32
- **32-bit STM Controller** — category=MCU, bus_width=32
- **32-bit STM microcontroller** — category=MCU, bus_width=32
- **8-bit AVR microcontroller** — category=MCU, bus_width=8
- **8-bit Atmel AVR microcontroller** — category=MCU, bus_width=8
- **8-bit Microcontroller** — category=MCU, bus_width=8
- **8-bit microcontroller** — category=MCU, bus_width=8
- **8-bit microcontroller (ASCAD dataset)** — category=MCU
- **8051 compatible microcontroller** — implementation_type=software, category=MCU
- **32-bit implementation** — bus_width=32
- **ASIC implementation of PicoRV32 on Saidoyoki board** — category=ASIC
- **ATSAMD21 microcontroller** — implementation_type=software, category=MCU

### Pipeline (10)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **Correlation-based pattern matching for RDI removal** — source=expert_experience, trigger_condition=random delays exhibit regular patterns (e.g., repetitive dummy loops), applicable_scenarios=software implementations where dummy operations or AES operation blocks have distinctive and consistent leakage patterns
- **HMM cryptanalysis of RDI-protected implementations** — source=expert_experience, trigger_condition=attacking a software implementation protected with random delay insertions, applicable_scenarios=microcontroller implementations of symmetric block ciphers (e.g., AES) with random delays inserted via dummy loops or interrupts
- **HMM-based Random Delay Removal and CPA** — source=PAP-33-2013-ePrint-HMM-Remove-Random-Delays, trigger_condition=when attacking a software implementation protected with random delay insertions (RDI) via power traces, applicable_scenarios=Embedded software implementations (e.g., on 8-bit microcontrollers) using random delays as a hiding countermeasure; requires ability to profile instruction cycles on a similar device.

### StatMethod (7)

- **Algebraic System Construction** — type=non_profiled
- **CEMA** — type=non_profiled
- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled

## 2. Relationships (30)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: XOR operation output, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `AttackPoint:XOR operation output`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
- `DeviceClass:STM32F429` —[works_with [source_text=一阶CPA分析...猜测出真实密钥0x00112233445566778899AABBCCDDEEFF。, support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `StatMethod:CPA`
- `DeviceClass:STM32F429` —[works_with [source_text=电磁分析...如图 778为对电磁波执行一阶CPA的结果, support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `TraceType:EM`
- `DeviceClass:STM32F429` —[works_with [source_text=能量信号采波 & 一阶CPA分析, support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `TraceType:Power`
- `DeviceClass:STM32F429` —[works_with [source_text=一阶CPA分析...猜测出真实密钥0x00112233445566778899AABBCCDDEEFF。, support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `Algorithm:AES`
- `DeviceClass:STM32F429` —[works_with [source_text=Static alignment discarded 0 traces., support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `Preprocessing:Static Alignment`
- `DeviceClass:32-bit STM Controller` —[works_with [source_text=CHES CTF ... AutoPOI ... 1830, support_count=1, confidence=0.2, source_papers=["PAP-74-2023-ePrint-AutoPOI"]]]→ `Algorithm:AES`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Preprocessing:Resampling`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Pipeline:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `StatMethod:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `LeakageModel:identity`
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
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=perform correlation power analysis on the processed traces, typically targeting first-round S-box output with Hamming weight model, source_text=perform correlation power analysis on the processed traces, typically targeting first-round S-box output with Hamming weight model, support_count=1, is_optional=False]]→ `StatMethod:CPA`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=find the most probable state sequence to identify and remove dummy cycles, outputting aligned traces, source_text=find the most probable state sequence to identify and remove dummy cycles, outputting aligned traces, support_count=1, is_optional=False]]→ `Preprocessing:Viterbi algorithm for delay removal`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=define states corresponding to instruction cycles and transition probabilities based on the code flow; compact representation for dummy loops, source_text=define states corresponding to instruction cycles and transition probabilities based on the code flow; compact representation for dummy loops, support_count=1, is_optional=False]]→ `DiagnosticMethod:HMM model construction`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=build Gaussian templates for each instruction cycle using PCA for dimensionality reduction (3 dimensions kept), condition=profiling phase requires a training device with known delay lengths, source_text=build Gaussian templates for each instruction cycle using PCA for dimensionality reduction (3 dimensions kept), support_count=1]]→ `DiagnosticMethod:Template building for instruction cycles`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[alternative_to [source_text=Heuristic and less generic than HMM; effective only when patterns are regular and distinguishable., support_count=1, confidence=0.2, source_papers=["PAP-27-2012-ePrint-Durvaux-Cryptanalysis-Random-Delay"]]]→ `Pipeline:Correlation-based pattern matching for RDI removal`

## 3. Diagnostic Chains (21)


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

### Obs: `reference_trace_selection` — any
- **Cause** (high): The second trace is often of good quality and representative of the trace set
- **Check**: Check trace quality metrics for early traces in the acquisition
- **Action**: Use the second trace as the reference trace for alignment
  - operation: `adjust_param`
  - target: `alignment.ref_trace`
  - strategy: Set the reference trace index to 1 (0-based) or 2 (1-based) depending on software convention
- **Relates to**: Preprocessing:`Static Alignment`

### Obs: `encryption_interval` — any
- **Cause** (high): Extending the time between two encryptions allows for better waveform separation and control over the acquisition rate.
- **Action**: Increase the encryption interval parameter in the acquisition software.
  - operation: `adjust_param`
  - target: `acquisition.encryption_interval`
  - strategy: Increase the encryption interval parameter in the acquisition software.

### Obs: `leakage_interval_selection` — any
- **Cause** (high): Automated leakage analysis can identify the time interval where the cryptographic operation leaks information, providing a good starting point for CPA.
- **Action**: Run the leakage analysis function in the software before CPA to automatically populate the leakage interval.
  - operation: `add_step`
  - target: `analysis.leakage_analysis`
  - strategy: Run the leakage analysis function in the software before CPA to automatically populate the leakage interval.
- **Relates to**: DiagnosticMethod:`Leakage Analysis`

### Obs: `waveform_jitter_vertical` — observed
- **Cause** (high): Electromagnetic interference from poorly arranged cables/probes and nearby high-radiation devices (e.g., mobile phones).
- **Check**: Observed as significant vertical抖动 on the energy waveform (channel 2).
- **Action**: Minimize environmental EMI by organizing cables and distancing the target from noise sources; use software-based vertical normalization as a countermeasure.
  - operation: `adjust_param`
  - target: `acquisition.environment`
  - strategy: 1. Rearrange all cables and probe wires on the board to minimize mutual interference. 2. Keep the development board away from high-radiation devices. 3. Use the vertical normalization function provided in the analysis software.

### Obs: `recovered_key_verification` — any
- **Cause** (high): DES key bytes include a parity bit (LSB) that is often ignored or set to zero by encryption software/hardware.
- **Action**: Ignore or zero the least significant bit (parity bit) of each byte when comparing recovered DES key
  - operation: `verify`
  - target: `recovered_key`
  - strategy: When comparing recovered DES key to expected key, ignore or zero the least significant bit (parity bit) of each byte.
- **Relates to**: ValidationMethod:`Key Verification`

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

### ⭐ • [canonical_pipeline_principle] Static aligner tuning loop: monotonic acceptance, priority-ordered parameter sweep, 70% gate before aligned CPA
- **Trigger**: Any static_aligner invocation returns acceptance_rate < 70% on the target ROI; OR agent is deciding whether to run CPA on already-aligned traces where acceptance_rate < 70%
- **Rationale**: Alignment parameters differ in leverage: max_shift determines whether the true peak is inside the search window, the reference point determines whether the window is on the right feature at all, and threshold only fine-tunes acceptance. Tuning in that order, and reverting any step that lowers acceptance, avoids wasting rounds on a monotonic search.
- **Content**: [{"principle": "When static_aligner acceptance_rate is below the aligned-CPA gate, the agent MUST enter a priority-ordered parameter tuning loop with monotonic acceptance constraint, BEFORE running aligned CPA. The acceptance_rate is the fraction of traces whose alignment template correlation exceeded threshold; low acceptance means a large subset of traces is missing — aligned CPA on that subset 
- **Applies to**: StatMethod:CPA, Preprocessing:Static Alignment

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-STM32F429_GLM5_DKG_20260424_052239_103
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-STM32F429_GLM5_DKG_20260424_052239_103/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 16,643→1,035

**🤖 LLM:** 我来帮你对STM32F429 MCU软件实现的AES电磁侧信道波形进行CPA攻击。让我按照标准的分析流程进行。

## 第一步：观察波形特征并初步分析

首先，让我加载并观察波形数据的特征：

**🔧 → `python_jupyter`**

<details><summary>Code (1798 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy')
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy')

print(f"波形数据形状: {wave.shape}")
print(f"明文数据形状: {plain.shape}")
print(f"密文数据形状: {cipher.shape}")
print(f"\n波形数据范围: [{wave.min():.4f}, {wave.max():.4f}]")
print(f"波形均值: {wave.mean():.4f}")
print(f"波形标准差: {wave.std():.4f}")

# 绘制几条波形观察特征
plt.figure(figsize=(14, 8))

# 绘制前10条波形
plt.subplot(2, 2, 1)
for i in range(10):
    plt.plot(wave[i], alpha=0.6, linewidth=0.8)
plt.title('前10条波形叠加')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 绘制单条波形
plt.subplot(2, 2, 2)
plt.plot(wave[0], linewidth=1)
plt.title('第1条波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 计算并绘制方差曲线（定位加密区域）
plt.subplot(2, 2, 3)
variance = np.var(wave, axis=0)
plt.plot(variance, linewidth=1, color='red')
plt.title('波形方差曲线（定位加密区域）')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.grid(True, alpha=0.3)

# 标记方差峰值区域
peak_idx = np.argmax(variance)
plt.axvline(x=peak_idx, color='green', linestyle='--', label=f'峰值位置: {peak_idx}')
plt.legend()

# 绘制均值波形
plt.subplot(2, 2, 4)
mean_wave = np.mean(wave, axis=0)
plt.plot(mean_wave, linewidth=1, color='blue')
plt.title('平均波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

print(f"\n方差峰值位置: {peak_idx}")
print(f"方差峰值值: {variance[peak_idx]:.4f}")
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (1000, 1000)
明文数据形状: (1000, 16)
密文数据形状: (1000, 16)

波形数据范围: [0.0000, 125000.0000]
波形均值: 25611.7031
波形标准差: 16987.9805

方差峰值位置: 9
方差峰值值: 1007727296.0000
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\507719236.py:61: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 2 | tokens: 17,572→781

**🔧 → `python_jupyter`**

<details><summary>Code (1872 chars)</summary>

```python
# 进一步分析方差曲线，寻找加密区域
plt.figure(figsize=(14, 6))

# 绘制完整方差曲线
plt.subplot(1, 2, 1)
plt.plot(variance, linewidth=1, color='red')
plt.title('完整方差曲线')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.grid(True, alpha=0.3)

# 找出方差较高的区域（可能是加密区域）
threshold = np.mean(variance) + np.std(variance)
high_var_regions = np.where(variance > threshold)[0]
if len(high_var_regions) > 0:
    print(f"高方差区域（方差 > {threshold:.2e}）:")
    print(f"  起始点: {high_var_regions[0]}")
    print(f"  结束点: {high_var_regions[-1]}")
    print(f"  覆盖范围: {high_var_regions[-1] - high_var_regions[0] + 1} 个采样点")
    
    # 标记高方差区域
    plt.axhline(y=threshold, color='orange', linestyle='--', label=f'阈值: {threshold:.2e}')
    plt.axvspan(high_var_regions[0], high_var_regions[-1], alpha=0.3, color='yellow', label='高方差区域')
    plt.legend()

# 绘制局部波形（高方差区域）
plt.subplot(1, 2, 2)
if len(high_var_regions) > 0:
    start = max(0, high_var_regions[0] - 50)
    end = min(wave.shape[1], high_var_regions[-1] + 50)
    for i in range(5):
        plt.plot(range(start, end), wave[i, start:end], alpha=0.7, linewidth=0.8, label=f'Trace {i}')
    plt.title(f'高方差区域波形（采样点 {start}-{end}）')
    plt.xlabel('采样点')
    plt.ylabel('幅值')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)

plt.tight_layout()
plt.savefig('variance_analysis.png', dpi=150)
plt.show()

# 计算基线噪声（非加密区域）
if len(high_var_regions) > 0:
    # 假设波形开始部分是基线
    baseline_region = wave[:, :min(50, high_var_regions[0])]
    baseline_std = np.std(baseline_region)
    baseline_mean = np.mean(baseline_region)
    print(f"\n基线区域统计:")
    print(f"  均值: {baseline_mean:.4f}")
    print(f"  标准差: {baseline_std:.4f}")
    
    # 计算SNR估计
    signal_region = wave[:, high_var_regions[0]:high_var_regions[-1]+1]
    signal_std = np.std(signal_region)
    print(f"\n信号区域统计:")
    print(f"  标准差: {signal_std:.4f}")
    print(f"  SNR估计: {signal_std/baseline_std:.2f}")
```
</details>

**📋 ← `python_jupyter`:** `高方差区域（方差 > 3.27e+08）:
  起始点: 3
  结束点: 999
  覆盖范围: 997 个采样点

基线区域统计:
  均值: 16585.5000
  标准差: 11109.7002

信号区域统计:
  标准差: 16995.3672
  SNR估计: 1.53
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3165047707.py:41: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 18,414→570

**🔧 → `python_jupyter`**

<details><summary>Code (1074 chars)</summary>

```python
# 检查波形对齐情况 - 观察多条波形的叠加情况
plt.figure(figsize=(14, 6))

# 叠加显示前50条波形
plt.subplot(1, 2, 1)
for i in range(50):
    plt.plot(wave[i], alpha=0.3, linewidth=0.5)
plt.title('前50条波形叠加（检查对齐）')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 计算并显示相关系数矩阵（检查波形间相似度）
plt.subplot(1, 2, 2)
# 随机选择100条波形计算相关系数
sample_indices = np.random.choice(wave.shape[0], 100, replace=False)
sample_waves = wave[sample_indices]
corr_matrix = np.corrcoef(sample_waves)

# 显示相关系数分布
corr_values = corr_matrix[np.triu_indices(100, k=1)]
plt.hist(corr_values, bins=50, edgecolor='black', alpha=0.7)
plt.title('波形间相关系数分布')
plt.xlabel('相关系数')
plt.ylabel('频数')
plt.grid(True, alpha=0.3)

mean_corr = np.mean(corr_values)
std_corr = np.std(corr_values)
plt.axvline(x=mean_corr, color='red', linestyle='--', label=f'均值: {mean_corr:.4f}')
plt.legend()

print(f"波形间相关系数统计:")
print(f"  均值: {mean_corr:.4f}")
print(f"  标准差: {std_corr:.4f}")
print(f"  最小值: {np.min(corr_values):.4f}")
print(f"  最大值: {np.max(corr_values):.4f}")

plt.tight_layout()
plt.savefig('alignment_check.png', dpi=150)
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `波形间相关系数统计:
  均值: 0.2697
  标准差: 0.3623
  最小值: -0.2805
  最大值: 0.9491
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1539259265.py:41: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 4 | tokens: 18,942→307

**🔧 → `python_jupyter`**

<details><summary>Code (464 chars)</summary>

```python
# 检查明文和密文数据
print("明文示例（前5条）:")
for i in range(5):
    print(f"  Trace {i}: {plain[i].hex()}")
    
print("\n密文示例（前5条）:")
for i in range(5):
    print(f"  Trace {i}: {cipher[i].hex()}")

# 检查明文/密文的字节分布
print("\n明文字节统计:")
print(f"  形状: {plain.shape}")
print(f"  数据类型: {plain.dtype}")
print(f"  值范围: [{plain.min()}, {plain.max()}]")

print("\n密文字节统计:")
print(f"  形状: {cipher.shape}")
print(f"  数据类型: {cipher.dtype}")
print(f"  值范围: [{cipher.min()}, {cipher.max()}]")
```
</details>

**❌ ← `python_jupyter` Error:**

```
明文示例（前5条）:

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mAttributeError[39m                            Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[381][39m[32m, line 4[39m
[32m      2[39m [38;5;28mprint[39m([33m"[39m[33m明文示例（前5条）:[39m[33m"[39m)
[32m      3[39m [38;5;28;01mfor[39;00m i [38;5;129;01min[39;00m [38;5;28mrange[39m([32m5[39m):
[32m----> [39m[32m4[39m     [38;5;28mprint[39m([33mf[39m[33m"[39m[33m  Trace [39m[38;5;132;01m{[39;00mi[38;5;132;01m}[39;00m[33m: [39m[38;5;132;01m{[39;00m[43mplain[49m[43m[[49m[43mi[49m[43m][49m[43m.[49m[43mhex[49m()[38;5;132;01m}[39;00m[33m"[39m)
[32m      6[39m [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33m密文示例（前5条）:[39m[33m"[39m)
[32m      7[39m [38;5;28;01mfor[39;00m i [38;5;129;01min[39;00m [38;5;28mrange[39m([32m5[39m):

[31mAttributeError[39m: 'numpy.ndarray' object has no attribute 'hex'
```


---

### Round 5 | tokens: 19,656→254

**🔧 → `python_jupyter`**

<details><summary>Code (558 chars)</summary>

```python
# 检查明文和密文数据
print("明文示例（前5条）:")
for i in range(5):
    hex_str = ''.join([f'{b:02x}' for b in plain[i]])
    print(f"  Trace {i}: {hex_str}")
    
print("\n密文示例（前5条）:")
for i in range(5):
    hex_str = ''.join([f'{b:02x}' for b in cipher[i]])
    print(f"  Trace {i}: {hex_str}")

# 检查明文/密文的字节分布
print("\n明文字节统计:")
print(f"  形状: {plain.shape}")
print(f"  数据类型: {plain.dtype}")
print(f"  值范围: [{plain.min()}, {plain.max()}]")

print("\n密文字节统计:")
print(f"  形状: {cipher.shape}")
print(f"  数据类型: {cipher.dtype}")
print(f"  值范围: [{cipher.min()}, {cipher.max()}]")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (574 chars)</summary>

```
明文示例（前5条）:
  Trace 0: 958d9d0f39f42c8a4e6f6ac1cbf56434
  Trace 1: 8f16fae6dd3bfc79509589f10eda44c5
  Trace 2: 0c8fce0749fdc1dc1cd1b5976e2c734a
  Trace 3: b1b1de68824aee599124bfa36b3a7c74
  Trace 4: 2ba4b43c275cea92541dca0c85640b23

密文示例（前5条）:
  Trace 0: fc1b4003e543afa97e5f7c4f94d63cb3
  Trace 1: 36c771022430a0e5c9861fed41942e85
  Trace 2: ec6cf1a8c0ded26d9214e28fcd6d44a8
  Trace 3: 5bd7b87097a6d0051af6213182c36b17
  Trace 4: be1186c1e5e92693585053be8b6803f0

明文字节统计:
  形状: (1000, 16)
  数据类型: uint8
  值范围: [0, 255]

密文字节统计:
  形状: (1000, 16)
  数据类型: uint8
  值范围: [0, 255]
```
</details>


---

### Round 6 | tokens: 20,276→559

**🤖 LLM:** 好的，我已经完成了初步的波形分析。让我总结一下观察到的特征：

**波形特征分析：**
1. **数据规模**: 1000条波形，每条1000个采样点
2. **波形对齐**: 波形间相关系数均值仅0.27，标准差0.36，说明**存在明显的时序抖动，对齐较差**
3. **SNR估计**: 约1.53，信噪比较低
4. **方差分布**: 整个波形区域方差都较高，没有明显的加密区域边界

根据KG知识和经验，STM32F429是32位MCU软件实现，EM侧信道通常需要考虑对齐问题。让我先进行**直接CPA探测**，看看是否需要静态对齐：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2048 chars)</summary>

```
{"recovered_key": "00112233445566778899AABBCCDDEEFF", "cpa_avg_correlation": 0.5644, "cpa_min_correlation": 0.4463, "n_traces": 1000, "target": "S-box_out", "plot_path": "cpa_result_20260424_052445_838178.png", "detail_file": "cpa_detail_20260424_052445_838178.json", "per_byte": [{"byte": 0, "key": "0x00", "correlation": 0.4463, "time_index": 353, "gap_pct": 65.4}, {"byte": 1, "key": "0x11", "correlation": 0.5536, "time_index": 364, "gap_pct": 65.4}, {"byte": 2, "key": "0x22", "correlation": 0.5321, "time_index": 418, "gap_pct": 69.9}, {"byte": 3, "key": "0x33", "correlation": 0.5563, "time_index": 385, "gap_pct": 66.8}, {"byte": 4, "key": "0x44", "correlation": 0.5662, "time_index": 356, "gap_pct": 67.7}, {"byte": 5, "key": "0x55", "correlation": 0.5341, "time_index": 366, "gap_pct": 69.6}, {"byte": 6, "key": "0x66", "correlation": 0.5802, "time_index": 377, "gap_pct": 69.5}, {"byte": 7, "key": "0x77", "correlation": 0.5952, "time_index": 387, "gap_pct": 68.4}, {"byte": 8, "key": "0x88", "correlation": 0.6141, "time_index": 358, "gap_pct": 66.5}, {"byte": 9, "key": "0x99", "correlation": 0.4875, "time_index": 368, "gap_pct": 71.4}, {"byte": 10, "key": "0xAA", "correlation": 0.6308, "time_index": 379, "gap_pct": 73.6}, {"byte": 11, "key": "0xBB", "correlation": 0.5474, "time_index": 390, "gap_pct": 68.3}, {"byte": 12, "key": "0xCC", "correlation": 0.6539, "time_index": 360, "gap_pct": 72.5}, {"byte": 13, "key": "0xDD", "correlation": 0.618, "time_index": 371, "gap_pct": 70.4}
...(truncated)
```
</details>


![cpa_result_20260424_052445_838178.png](./cpa_result_20260424_052445_838178.png)


---

### Round 7 | tokens: 21,475→473

**🤖 LLM:** 太好了！直接CPA攻击就取得了**非常优秀的结果**：

**CPA攻击结果：**
- ✅ **恢复密钥**: `00112233445566778899AABBCCDDEEFF`
- ✅ **高置信度字节数**: **16/16**（全部字节）
- ✅ **平均相关系数**: 0.5644（非常高）
- ✅ **Gap百分比**: 所有字节都在65%-74%之间（远超15%阈值）

这是一个**教科书级别的成功案例**！让我验证这个密钥是否正确：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "key_hex": "00112233445566778899AABBCCDDEEFF",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy",
  "trace_index": 0
}
```
</details>

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "FC1B4003E543AFA97E5F7C4F94D63CB3", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 958d9d0f39f42c8a4e6f6ac1cbf56434... → FC1B4003E543AFA97E5F7C4F94D63CB3...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 8 | tokens: 21,911→985

**🤖 LLM:** 🎉 **密钥验证成功！**

让我生成详细的分析报告：

**🔧 → `python_jupyter`**

<details><summary>Code (2107 chars)</summary>

```python
import json

# 加载CPA详细结果
with open('cpa_detail_20260424_052445_838178.json', 'r') as f:
    cpa_detail = json.load(f)

# 生成分析报告
print("=" * 80)
print("AES-128 STM32F429 EM侧信道CPA攻击报告")
print("=" * 80)

print("\n【数据集信息】")
print(f"  设备类型: STM32F429 MCU (32位)")
print(f"  实现类型: 软件实现")
print(f"  侧信道类型: 电磁 (EM)")
print(f"  波形数量: 1000 条")
print(f"  采样点数: 1000 点/波形")

print("\n【攻击配置】")
print(f"  攻击方法: CPA (Correlation Power Analysis)")
print(f"  攻击目标: S-box output (第一轮S盒输出)")
print(f"  泄漏模型: Hamming Weight (HW)")
print(f"  预处理: 无需对齐/滤波（直接攻击成功）")

print("\n【攻击结果】")
print(f"  ✅ 恢复密钥: {cpa_detail['recovered_key']}")
print(f"  ✅ 验证状态: MATCH (密钥正确)")
print(f"  ✅ 高置信度字节: {cpa_detail['high_confidence_count']}/16")
print(f"  ✅ 平均相关系数: {cpa_detail['cpa_avg_correlation']:.4f}")
print(f"  ✅ 最小相关系数: {cpa_detail['cpa_min_correlation']:.4f}")

print("\n【各字节详细结果】")
print("-" * 80)
print(f"{'字节':<6} {'密钥':<8} {'相关系数':<12} {'时间点':<10} {'Gap%':<10} {'置信度'}")
print("-" * 80)

for byte_info in cpa_detail['per_byte']:
    confidence = "高" if byte_info['gap_pct'] >= 15 else "低"
    print(f"{byte_info['byte']:<6} {byte_info['key']:<8} {byte_info['correlation']:<12.4f} "
          f"{byte_info['time_index']:<10} {byte_info['gap_pct']:<10.1f} {confidence}")

print("-" * 80)

print("\n【关键发现】")
print("  1. 直接CPA攻击即成功，无需静态对齐或滤波")
print("  2. 所有16个字节均为高置信度（Gap% > 65%）")
print("  3. 相关系数范围: 0.4463 - 0.6539，信号强度优秀")
print("  4. 泄漏时间点集中在 353-418 采样点区间")
print("  5. STM32F429软件AES实现的EM泄漏特征明显")

print("\n【成功因素分析】")
print("  ✓ 足够的波形数量 (1000条)")
print("  ✓ 软件实现的HW泄漏模型匹配良好")
print("  ✓ EM探头位置准确捕获了加密操作泄漏")
print("  ✓ 波形质量高，尽管有抖动但CPA仍能提取密钥")

print("\n【结论】")
print("  攻击完全成功！恢复的密钥 00112233445566778899AABBCCDDEEFF 已通过验证。")
print("  这表明STM32F429 MCU上的软件AES实现存在严重的EM侧信道泄漏风险。")
print("=" * 80)

# 绘制CPA结果图
from PIL import Image
import matplotlib.pyplot as plt

img = Image.open('cpa_result_20260424_052445_838178.png')
plt.figure(figsize=(12, 8))
plt.imshow(img)
plt.axis('off')
plt.title('CPA攻击结果可视化', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('final_cpa_result.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

**❌ ← `python_jupyter` Error:**

```
================================================================================
AES-128 STM32F429 EM侧信道CPA攻击报告
================================================================================

【数据集信息】
  设备类型: STM32F429 MCU (32位)
  实现类型: 软件实现
  侧信道类型: 电磁 (EM)
  波形数量: 1000 条
  采样点数: 1000 点/波形

【攻击配置】
  攻击方法: CPA (Correlation Power Analysis)
  攻击目标: S-box output (第一轮S盒输出)
  泄漏模型: Hamming Weight (HW)
  预处理: 无需对齐/滤波（直接攻击成功）

【攻击结果】

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[385][39m[32m, line 26[39m
[32m     23[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m  预处理: 无需对齐/滤波（直接攻击成功）[39m[33m"[39m)
[32m     25[39m [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33m【攻击结果】[39m[33m"[39m)
[32m---> [39m[32m26[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m  ✅ 恢复密钥: [39m[38;5;132;01m{[39;00m[43mcpa_detail[49m[43m[[49m[33;43m'[39;49m[33;43mrecovered_key[39;49m[33;43m'[39;49m[43m][49m[38;5;132;01m}[39;00m[33m"[39m)
[32m     27[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m  ✅ 验证状态: MATCH (密钥正确)[39m[33m"[39m)
[32m     28[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m  ✅ 高置信度字节: [39m[38;5;132;01m{[39;00mcpa_detail[[33m'[39m[33mhigh_confidence_count[39m[33m'[39m][38;5;132;01m}[39;00m[33m/16[39m[33m"[39m)

[31mKeyError[39m: 'recovered_key'
```


---

### Round 9 | tokens: 23,557→101

**🔧 → `python_jupyter`**

<details><summary>Code (236 chars)</summary>

```python
# 检查JSON文件结构
import json

with open('cpa_detail_20260424_052445_838178.json', 'r') as f:
    cpa_detail = json.load(f)

print("JSON文件的键:")
print(list(cpa_detail.keys()))
print("\nJSON内容预览:")
print(json.dumps(cpa_detail, indent=2)[:500])
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (593 chars)</summary>

```
JSON文件的键:
['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results']

JSON内容预览:
{
  "n_traces": 1000,
  "n_points": 1000,
  "leakage_model": "HW",
  "target": "S-box_out",
  "corr_mode": "abs",
  "results": [
    {
      "byte": 0,
      "topK": [
        {
          "key": 0,
          "score": 0.44629811883424253,
          "time_index": 353
        },
        {
          "key": 242,
          "score": 0.1546028704302906,
          "time_index": 273
        },
        {
          "key": 208,
          "score": 0.1545939431494346,
          "time_index": 273
        },
```
</details>


---

### Round 10 | tokens: 23,868→1,292

**🔧 → `python_jupyter`**

<details><summary>Code (2513 chars)</summary>

```python
import json

# 加载CPA详细结果
with open('cpa_detail_20260424_052445_838178.json', 'r') as f:
    cpa_detail = json.load(f)

# 提取每个字节的最佳密钥
recovered_key_bytes = []
for result in cpa_detail['results']:
    best_candidate = result['topK'][0]  # 第一个就是最佳候选
    recovered_key_bytes.append(best_candidate['key'])

recovered_key = ''.join([f'{b:02X}' for b in recovered_key_bytes])

# 生成分析报告
print("=" * 80)
print("AES-128 STM32F429 EM侧信道CPA攻击报告")
print("=" * 80)

print("\n【数据集信息】")
print(f"  设备类型: STM32F429 MCU (32位)")
print(f"  实现类型: 软件实现")
print(f"  侧信道类型: 电磁 (EM)")
print(f"  波形数量: {cpa_detail['n_traces']} 条")
print(f"  采样点数: {cpa_detail['n_points']} 点/波形")

print("\n【攻击配置】")
print(f"  攻击方法: CPA (Correlation Power Analysis)")
print(f"  攻击目标: {cpa_detail['target']} (第一轮S盒输出)")
print(f"  泄漏模型: {cpa_detail['leakage_model']} (Hamming Weight)")
print(f"  预处理: 无需对齐/滤波（直接攻击成功）")

print("\n【攻击结果】")
print(f"  ✅ 恢复密钥: {recovered_key}")
print(f"  ✅ 验证状态: MATCH (密钥正确)")
print(f"  ✅ 高置信度字节: 16/16")
print(f"  ✅ 平均相关系数: 0.5644")
print(f"  ✅ 最小相关系数: 0.4463")

print("\n【各字节详细结果】")
print("-" * 80)
print(f"{'字节':<6} {'密钥':<8} {'相关系数':<12} {'时间点':<10} {'Gap%':<10} {'置信度'}")
print("-" * 80)

# 从之前的CPA结果中获取gap信息
gap_data = [
    (0, "0x00", 0.4463, 353, 65.4),
    (1, "0x11", 0.5536, 364, 65.4),
    (2, "0x22", 0.5321, 418, 69.9),
    (3, "0x33", 0.5563, 385, 66.8),
    (4, "0x44", 0.5662, 356, 67.7),
    (5, "0x55", 0.5341, 366, 69.6),
    (6, "0x66", 0.5802, 377, 69.5),
    (7, "0x77", 0.5952, 387, 68.4),
    (8, "0x88", 0.6141, 358, 66.5),
    (9, "0x99", 0.4875, 368, 71.4),
    (10, "0xAA", 0.6308, 379, 73.6),
    (11, "0xBB", 0.5474, 390, 68.3),
    (12, "0xCC", 0.6539, 360, 72.5),
    (13, "0xDD", 0.618, 371, 70.4),
    (14, "0xEE", 0.5513, 381, 67.3),
    (15, "0xFF", 0.564, 392, 71.3),
]

for byte_idx, key_hex, corr, time_idx, gap in gap_data:
    confidence = "高" if gap >= 15 else "低"
    print(f"{byte_idx:<6} {key_hex:<8} {corr:<12.4f} {time_idx:<10} {gap:<10.1f} {confidence}")

print("-" * 80)

print("\n【关键发现】")
print("  1. 直接CPA攻击即成功，无需静态对齐或滤波")
print("  2. 所有16个字节均为高置信度（Gap% > 65%）")
print("  3. 相关系数范围: 0.4463 - 0.6539，信号强度优秀")
print("  4. 泄漏时间点集中在 353-418 采样点区间")
print("  5. STM32F429软件AES实现的EM泄漏特征明显")

print("\n【成功因素分析】")
print("  ✓ 足够的波形数量 (1000条)")
print("  ✓ 软件实现的HW泄漏模型匹配良好")
print("  ✓ EM探头位置准确捕获了加密操作泄漏")
print("  ✓ 波形质量高，尽管有抖动但CPA仍能提取密钥")

print("\n【结论】")
print("  攻击完全成功！恢复的密钥 00112233445566778899AABBCCDDEEFF 已通过验证。")
print("  这表明STM32F429 MCU上的软件AES实现存在严重的EM侧信道泄漏风险。")
print("=" * 80)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (2150 chars)</summary>

```
================================================================================
AES-128 STM32F429 EM侧信道CPA攻击报告
================================================================================

【数据集信息】
  设备类型: STM32F429 MCU (32位)
  实现类型: 软件实现
  侧信道类型: 电磁 (EM)
  波形数量: 1000 条
  采样点数: 1000 点/波形

【攻击配置】
  攻击方法: CPA (Correlation Power Analysis)
  攻击目标: S-box_out (第一轮S盒输出)
  泄漏模型: HW (Hamming Weight)
  预处理: 无需对齐/滤波（直接攻击成功）

【攻击结果】
  ✅ 恢复密钥: 00112233445566778899AABBCCDDEEFF
  ✅ 验证状态: MATCH (密钥正确)
  ✅ 高置信度字节: 16/16
  ✅ 平均相关系数: 0.5644
  ✅ 最小相关系数: 0.4463

【各字节详细结果】
--------------------------------------------------------------------------------
字节     密钥       相关系数         时间点        Gap%       置信度
--------------------------------------------------------------------------------
0      0x00     0.4463       353        65.4       高
1      0x11     0.5536       364        65.4       高
2      0x22     0.5321       418        69.9       高
3      0x33     0.5563       385        66.8       高
4      0x44     0.5662       356        67.7       高
5      0x55     0.5341       366        69.6       高
6      0x66     0.5802       377        69.5       高
7      0x77     0.5952       387        68.4       高
8      0x88     0.6141       358        66.5       高
9      0x99     0.4875       368        71.4       高
10     0xAA     0.6308       379        73.6       高
11     0xBB     0.5474       390        68.3       高
12     0xCC     0.6539       360        72.5       高
13     0xDD     0.6180       371
...(truncated)
```
</details>


---

### Round 11 | tokens: 26,044→1,450

**🔧 → `python_jupyter`**

<details><summary>Code (3253 chars)</summary>

```python
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# 创建综合报告图
fig = plt.figure(figsize=(16, 10))

# 1. 波形示例
ax1 = plt.subplot(2, 3, 1)
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy')
for i in range(5):
    ax1.plot(wave[i], alpha=0.7, linewidth=0.8)
ax1.set_title('波形示例（前5条）', fontsize=12, fontweight='bold')
ax1.set_xlabel('采样点')
ax1.set_ylabel('幅值')
ax1.grid(True, alpha=0.3)

# 2. 方差曲线
ax2 = plt.subplot(2, 3, 2)
variance = np.var(wave, axis=0)
ax2.plot(variance, color='red', linewidth=1)
ax2.set_title('方差曲线', fontsize=12, fontweight='bold')
ax2.set_xlabel('采样点')
ax2.set_ylabel('方差')
ax2.grid(True, alpha=0.3)
# 标记泄漏区域
ax2.axvspan(353, 418, alpha=0.3, color='green', label='泄漏区域')
ax2.legend()

# 3. 相关系数分布
ax3 = plt.subplot(2, 3, 3)
correlations = [0.4463, 0.5536, 0.5321, 0.5563, 0.5662, 0.5341, 0.5802, 0.5952,
                0.6141, 0.4875, 0.6308, 0.5474, 0.6539, 0.618, 0.5513, 0.564]
bytes_idx = list(range(16))
colors = ['green' if c > 0.5 else 'orange' for c in correlations]
bars = ax3.bar(bytes_idx, correlations, color=colors, alpha=0.7, edgecolor='black')
ax3.set_title('各字节相关系数', fontsize=12, fontweight='bold')
ax3.set_xlabel('字节索引')
ax3.set_ylabel('相关系数')
ax3.set_ylim(0, 0.7)
ax3.axhline(y=0.5, color='red', linestyle='--', label='阈值 0.5')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# 4. Gap百分比分布
ax4 = plt.subplot(2, 3, 4)
gaps = [65.4, 65.4, 69.9, 66.8, 67.7, 69.6, 69.5, 68.4,
        66.5, 71.4, 73.6, 68.3, 72.5, 70.4, 67.3, 71.3]
ax4.bar(bytes_idx, gaps, color='steelblue', alpha=0.7, edgecolor='black')
ax4.set_title('各字节Gap百分比', fontsize=12, fontweight='bold')
ax4.set_xlabel('字节索引')
ax4.set_ylabel('Gap %')
ax4.set_ylim(0, 80)
ax4.axhline(y=15, color='red', linestyle='--', label='置信度阈值 15%')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

# 5. 泄漏时间点分布
ax5 = plt.subplot(2, 3, 5)
time_points = [353, 364, 418, 385, 356, 366, 377, 387,
               358, 368, 379, 390, 360, 371, 381, 392]
ax5.scatter(time_points, correlations, s=100, c='purple', alpha=0.6, edgecolors='black')
ax5.set_title('泄漏时间点 vs 相关系数', fontsize=12, fontweight='bold')
ax5.set_xlabel('时间点（采样点）')
ax5.set_ylabel('相关系数')
ax5.grid(True, alpha=0.3)

# 6. 成功指标总结
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')
summary_text = """
攻击成功总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 恢复密钥: 00112233445566778899AABBCCDDEEFF
✅ 验证状态: MATCH (密钥正确)
✅ 高置信度字节: 16/16 (100%)

关键指标:
• 平均相关系数: 0.5644
• 最小相关系数: 0.4463
• 平均Gap百分比: 68.9%
• 泄漏时间范围: 353-418 采样点

攻击配置:
• 目标: S-box output
• 模型: Hamming Weight
• 预处理: 无需对齐/滤波

结论: 攻击完全成功！
"""
ax6.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
         verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

plt.tight_layout()
plt.savefig('attack_summary.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n✅ 分析完成！所有结果已保存到当前会话目录。")
print(f"\n生成的文件:")
print(f"  - waveform_analysis.png: 波形特征分析")
print(f"  - variance_analysis.png: 方差分析")
print(f"  - alignment_check.png: 对齐检查")
print(f"  - cpa_result_20260424_052445_838178.png: CPA结果图")
print(f"  - attack_summary.png: 攻击总结图")
print(f"  - cpa_detail_20260424_052445_838178.json: CPA详细数据")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (27056 chars)</summary>

```
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1089383382.py:95: UserWarning: Glyph 25915 (\N{CJK UNIFIED IDEOGRAPH-653B}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1089383382.py:95: UserWarning: Glyph 20987 (\N{CJK UNIFIED IDEOGRAPH-51FB}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1089383382.py:95: UserWarning: Glyph 25104 (\N{CJK UNIFIED IDEOGRAPH-6210}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1089383382.py:95: UserWarning: Glyph 21151 (\N{CJK UNIFIED IDEOGRAPH-529F}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1089383382.py:95: UserWarning: Glyph 24635 (\N{CJK UNIFIED IDEOGRAPH-603B}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1089383382.py:95: UserWarning: Glyph 32467 (\N{CJK UNIFIED IDEOGRAPH-7ED3}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1089383382.py:95: UserWarning: Glyph 9989 (\N{WHITE HEAVY CHECK MARK}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1089383382.py:95: UserWarning: Glyph 24674 (\N{CJK UNIFIED IDEOGRAPH-6062}) missing from font(s) DejaVu Sans Mono.
  plt.tight_la
...(truncated)
```
</details>


![attack_summary.png](./attack_summary.png)


---

### Round 12 | tokens: 36,427→587

<details><summary><b>🤖 LLM Reasoning</b> (1096 chars)</summary>

## 🎉 攻击成功总结

我已经成功完成了对STM32F429 MCU软件AES实现的电磁侧信道CPA攻击！

### 📊 攻击结果

**✅ 恢复密钥**: `00112233445566778899AABBCCDDEEFF`  
**✅ 验证状态**: **MATCH** (密钥正确)  
**✅ 高置信度字节**: **16/16** (100%)

### 🔍 关键发现

1. **直接CPA攻击成功** - 无需静态对齐或滤波预处理
2. **所有16个字节均为高置信度** - Gap百分比在65%-74%之间（远超15%阈值）
3. **相关系数优秀** - 范围0.4463-0.6539，平均0.5644
4. **泄漏时间集中** - 在353-418采样点区间
5. **软件实现特征明显** - HW泄漏模型匹配良好

### 📈 攻击配置

| 参数 | 值 |
|------|-----|
| 攻击方法 | CPA (Correlation Power Analysis) |
| 攻击目标 | S-box output (第一轮S盒输出) |
| 泄漏模型 | Hamming Weight (HW) |
| 波形数量 | 1000条 |
| 预处理 | 无需对齐/滤波 |

### 💡 成功因素

- ✓ **足够的波形数量** (1000条提供了良好的统计基础)
- ✓ **正确的泄漏模型** (软件实现使用HW模型)
- ✓ **高质量的EM采集** (探头位置准确捕获加密操作)
- ✓ **明显的泄漏特征** (STM32F429软件AES的EM泄漏强)

### 📁 生成的文件

所有分析结果已保存到会话目录：
- `waveform_analysis.png` - 波形特征分析
- `variance_analysis.png` - 方差分析  
- `alignment_check.png` - 对齐检查
- `cpa_result_20260424_052445_838178.png` - CPA结果可视化
- `attack_summary.png` - 攻击总结图
- `cpa_detail_20260424_052445_838178.json` - CPA详细数据

### ⚠️ 安全启示

这次攻击表明STM32F429 MCU上的软件AES实现存在**严重的EM侧信道泄漏风险**。在实际应用中，应考虑：
- 使用硬件加密模块
- 实现侧信道防护（如掩码、隐藏）
- 增加随机延迟等反制措施

攻击完全成功！🎯

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 16,643 | 1,035 | 17,678 |
| 2 | 17,572 | 781 | 18,353 |
| 3 | 18,414 | 570 | 18,984 |
| 4 | 18,942 | 307 | 19,249 |
| 5 | 19,656 | 254 | 19,910 |
| 6 | 20,276 | 559 | 20,835 |
| 7 | 21,475 | 473 | 21,948 |
| 8 | 21,911 | 985 | 22,896 |
| 9 | 23,557 | 101 | 23,658 |
| 10 | 23,868 | 1,292 | 25,160 |
| 11 | 26,044 | 1,450 | 27,494 |
| 12 | 36,427 | 587 | 37,014 |
| **Total** | **264,785** | **8,394** | **273,179** |

## 8. Final Output

## 🎉 攻击成功总结

我已经成功完成了对STM32F429 MCU软件AES实现的电磁侧信道CPA攻击！

### 📊 攻击结果

**✅ 恢复密钥**: `00112233445566778899AABBCCDDEEFF`  
**✅ 验证状态**: **MATCH** (密钥正确)  
**✅ 高置信度字节**: **16/16** (100%)

### 🔍 关键发现

1. **直接CPA攻击成功** - 无需静态对齐或滤波预处理
2. **所有16个字节均为高置信度** - Gap百分比在65%-74%之间（远超15%阈值）
3. **相关系数优秀** - 范围0.4463-0.6539，平均0.5644
4. **泄漏时间集中** - 在353-418采样点区间
5. **软件实现特征明显** - HW泄漏模型匹配良好

### 📈 攻击配置

| 参数 | 值 |
|------|-----|
| 攻击方法 | CPA (Correlation Power Analysis) |
| 攻击目标 | S-box output (第一轮S盒输出) |
| 泄漏模型 | Hamming Weight (HW) |
| 波形数量 | 1000条 |
| 预处理 | 无需对齐/滤波 |

### 💡 成功因素

- ✓ **足够的波形数量** (1000条提供了良好的统计基础)
- ✓ **正确的泄漏模型** (软件实现使用HW模型)
- ✓ **高质量的EM采集** (探头位置准确捕获加密操作)
- ✓ **明显的泄漏特征** (STM32F429软件AES的EM泄漏强)

### 📁 生成的文件

所有分析结果已保存到会话目录：
- `waveform_analysis.png` - 波形特征分析
- `variance_analysis.png` - 方差分析  
- `alignment_check.png` - 对齐检查
- `cpa_result_20260424_052445_838178.png` - CPA结果可视化
- `attack_summary.png` - 攻击总结图
- `cpa_detail_20260424_052445_838178.json` - CPA详细数据

### ⚠️ 安全启示

这次攻击表明STM32F429 MCU上的软件AES实现存在**严重的EM侧信道泄漏风险**。在实际应用中，应考虑：
- 使用硬件加密模块
- 实现侧信道防护（如掩码、隐藏）
- 增加随机延迟等反制措施

攻击完全成功！🎯
