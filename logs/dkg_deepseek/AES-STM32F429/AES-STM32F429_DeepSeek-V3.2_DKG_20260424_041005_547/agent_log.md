# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_041005_547 |
| Duration | 255.6s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_DSv3.2\AES-STM32F429_DeepSeek-V3.2_DKG_20260424_041005_547` |
| Total LLM Calls | 9 |
| First Round | prompt: 17,014, completion: 811 |
| Last Round | prompt: 24,699, completion: 574 |
| Total Tokens | 189,689 (prompt: 184,345, completion: 5,344) |

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

LLM Response: ["AES", "STM32F429", "EM", "CPA", "MCU", "Software Implementation"]

Parsed Keywords: `["AES", "STM32F429", "EM", "CPA", "MCU", "Software Implementation"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 42035 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (44313 chars, click to expand)</summary>

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

**Search keywords** (6): AES, STM32F429, EM, CPA, MCU, Software Implementation

**Summary**: 35 upper entities, 30 relationships, 18 diagnostic chains, 13 strategies


## 1. Upper Layer Entities (35)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### DeviceClass (15)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **STM32F429** — category=MCU, bus_width=32
- **32-bit implementation** — bus_width=32
- **ASIC implementation of PicoRV32 on Saidoyoki board** — category=ASIC
- **32-bit STM Controller** — category=MCU, bus_width=32
- **32-bit STM microcontroller** — category=MCU, bus_width=32
- **8-bit AVR microcontroller** — category=MCU, bus_width=8
- **8-bit Atmel AVR microcontroller** — category=MCU, bus_width=8
- **8-bit Microcontroller** — category=MCU, bus_width=8
- **8-bit microcontroller** — category=MCU, bus_width=8
- **8-bit microcontroller (ASCAD dataset)** — category=MCU
- **8051 compatible microcontroller** — implementation_type=software, category=MCU
- **Software implementation (CHES Challenge 2020)** — category=MCU

### Pipeline (12)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, canonical_source=round1_patch_002, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **Correlation-based pattern matching for RDI removal** — source=expert_experience, trigger_condition=random delays exhibit regular patterns (e.g., repetitive dummy loops), applicable_scenarios=software implementations where dummy operations or AES operation blocks have distinctive and consistent leakage patterns
- **HMM cryptanalysis of RDI-protected implementations** — source=expert_experience, trigger_condition=attacking a software implementation protected with random delay insertions, applicable_scenarios=microcontroller implementations of symmetric block ciphers (e.g., AES) with random delays inserted via dummy loops or interrupts
- **HMM-based Random Delay Removal and CPA** — source=PAP-33-2013-ePrint-HMM-Remove-Random-Delays, trigger_condition=when attacking a software implementation protected with random delay insertions (RDI) via power traces, applicable_scenarios=Embedded software implementations (e.g., on 8-bit microcontrollers) using random delays as a hiding countermeasure; requires ability to profile instruction cycles on a similar device.
- **Improved Collision DL-SCA with Shared Feature Extractor and Multiple Distinguishers** — source=This work, trigger_condition=non-profiled side-channel attack on AES software implementation, applicable_scenarios=masked AES software implementations with serial Sbox computations
- **Practical Second-Order DPA Attack Strategy** — source=research_paper, trigger_condition=when performing a second-order DPA attack on a masked implementation, applicable_scenarios=masked software implementations of block ciphers, especially on 8-bit smart cards

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
- `DeviceClass:32-bit STM Controller` —[works_with [source_text=CHES CTF ... AutoPOI ... 1830, support_count=1, confidence=0.2, source_papers=["PAP-74-2023-ePrint-AutoPOI"]]]→ `Algorithm:AES`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Preprocessing:Resampling`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Pipeline:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `StatMethod:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `LeakageModel:identity`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=perform correlation power analysis on the processed traces, typically targeting first-round S-box output with Hamming weight model, source_text=perform correlation power analysis on the processed traces, typically targeting first-round S-box output with Hamming weight model, support_count=1, is_optional=False]]→ `StatMethod:CPA`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=find the most probable state sequence to identify and remove dummy cycles, outputting aligned traces, source_text=find the most probable state sequence to identify and remove dummy cycles, outputting aligned traces, support_count=1, is_optional=False]]→ `Preprocessing:Viterbi algorithm for delay removal`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=define states corresponding to instruction cycles and transition probabilities based on the code flow; compact representation for dummy loops, source_text=define states corresponding to instruction cycles and transition probabilities based on the code flow; compact representation for dummy loops, support_count=1, is_optional=False]]→ `DiagnosticMethod:HMM model construction`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=build Gaussian templates for each instruction cycle using PCA for dimensionality reduction (3 dimensions kept), condition=profiling phase requires a training device with known delay lengths, source_text=build Gaussian templates for each instruction cycle using PCA for dimensionality reduction (3 dimensions kept), support_count=1]]→ `DiagnosticMethod:Template building for instruction cycles`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[alternative_to [source_text=Heuristic and less generic than HMM; effective only when patterns are regular and distinguishable., support_count=1, confidence=0.2, source_papers=["PAP-27-2012-ePrint-Durvaux-Cryptanalysis-Random-Delay"]]]→ `Pipeline:Correlation-based pattern matching for RDI removal`

## 3. Diagnostic Chains (18)


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

### Obs: `filter_weight_selection` — any
- **Cause** (high): Software implementations have clear signal; too high weight distorts signal and reduces CPA success. Hardware implementations generally do not require filtering.
- **Action**: Use weight 2-3 for software implementations (smartcard, MCU). Use no filter for hardware implementations (FPGA, ASIC).
  - operation: `adjust_param`
  - target: `filter.weight`
  - strategy: Start with small filter weights (2-3) for software; if uncertain, try no filter.
- **Relates to**: Preprocessing:`Low-pass Filter`
- **Alternatives**: Bandpass filtering

### Obs: `leakage_model_selection` — any
- **Cause** (high): Software implementations leak the Hamming weight of the S-box output.
- **Action**: Use target S-box_out with HW model.
  - operation: `switch_component`
  - target: `leakage_model`
  - strategy: For software AES, default to S-box_out + HW.
- **Relates to**: LeakageModel:`Hamming Weight`
- **Alternatives**: Identity

### Obs: `cpa_verification_status` — any
- **Cause** (medium): Wrong attack point (e.g., using S-box input instead of output).
- **Check**: Review target selection.
- **Action**: Use S-box output as attack point.
  - operation: `switch_component`
  - target: `leakage_model`
  - strategy: Default to S-box output for software implementations.
- **Relates to**: AttackPoint:`S-box Output`

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

### 📋 [troubleshooting_checklist] Code-assisted leakage region identification for software implementations
- **Trigger**: when you have power traces from a known software implementation and need to locate leakage regions for attack without knowing plaintexts/keys
- **Rationale**: Code analysis combined with averaged traces allows identification of algorithm steps and selection of relevant time windows without requiring secret data, enabling attacks in black-box or limited-knowledge scenarios.
- **[rank 1]** if `Average a large number of traces (e.g., 1000) to suppress noise and reveal repetitive patterns` → acquire more traces to improve signal-to-noise ratio
- **[rank 2]** if `Identify main algorithm phases (pre-processing, rounds, post-processing) by looking for characteristic repetitive patterns (e.g., 10 round patterns for AES)` → verify algorithm execution flow against known code structure
- **[rank 3]** if `Within pre-processing, locate table pre-computation loops (e.g., GTab, masked Sbox) by identifying long, regular patterns` → examine assembly code to understand table generation steps
- **[rank 4]** if `For specific shares (e.g., multiplicative mask r_m), zoom into the start of table pre-computation to find loading operations and loop entries` → refine window by correlating with assembly instructions for share manipulation
- **[rank 5]** if `For round operations (e.g., SubBytes), isolate the first round and count inner loop patterns to match expected operation counts (e.g., 16 patterns for SubBytes)` → verify loop counts against algorithm description
- **[rank 6]** if `Select contiguous time windows that encompass the identified leakage regions, balancing coverage and trace length` → adjust window boundaries based on SNR verification if secret data is later available
- **Applies to**: Algorithm:AES

### ⚙ [parameter_preset_bundle] Gaussian Template Profiling Parameters for Masked Software
- **Trigger**: when building Gaussian templates for profiling shares in masked software implementations (especially bitslice) on 32‑bit microcontrollers
- **Rationale**: These values provide a good trade‑off between estimation accuracy and computational complexity for profiling shares in masked software, as empirically validated on ARM Cortex‑M0/M3 devices.
- `subspace dimension for 8‑bit variables` = 10 dimensions
- `subspace dimension for 2‑bit variables` = 3 dimensions
- `POI selection method` = None SNR
- `dimensionality reduction method` = None PCA or LDA
- **Applies to**: Preprocessing:SNR, Preprocessing:PCA

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_DSv3.2\AES-STM32F429_DeepSeek-V3.2_DKG_20260424_041005_547
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_DSv3.2\AES-STM32F429_DeepSeek-V3.2_DKG_20260424_041005_547/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 17,014→811

**🤖 LLM:** 我将帮您对STM32F429 MCU软件实现的AES进行CPA密钥恢复。首先，让我检查一下数据的基本情况。

**🔧 → `python_jupyter`**

<details><summary>Code (1850 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy'
plain_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy'
cipher_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy'

# 加载数据
waves = np.load(wave_path)
plaintexts = np.load(plain_path)
ciphertexts = np.load(cipher_path)

print(f"波形数据形状: {waves.shape}")
print(f"明文数据形状: {plaintexts.shape}")
print(f"密文数据形状: {ciphertexts.shape}")
print(f"数据类型 - 波形: {waves.dtype}, 明文: {plaintexts.dtype}, 密文: {ciphertexts.dtype}")

# 检查前几个明文和密文
print(f"\n前3个明文 (十六进制):")
for i in range(3):
    print(f"Trace {i}: {plaintexts[i].tobytes().hex()}")

print(f"\n前3个密文 (十六进制):")
for i in range(3):
    print(f"Trace {i}: {ciphertexts[i].tobytes().hex()}")

# 查看波形统计信息
print(f"\n波形统计:")
print(f"  最小值: {waves.min():.4f}")
print(f"  最大值: {waves.max():.4f}")
print(f"  平均值: {waves.mean():.4f}")
print(f"  标准差: {waves.std():.4f}")

# 绘制前几个波形
plt.figure(figsize=(12, 8))
for i in range(5):
    plt.plot(waves[i], alpha=0.7, label=f'Trace {i}')
plt.title('前5个波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('raw_waveforms.png')
plt.show()

# 计算平均波形
mean_wave = waves.mean(axis=0)
std_wave = waves.std(axis=0)

plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(mean_wave)
plt.title('平均波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

plt.subplot(2, 1, 2)
plt.plot(std_wave)
plt.title('波形标准差')
plt.xlabel('采样点')
plt.ylabel('标准差')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('mean_std_waveforms.png')
plt.show()
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (771 chars)</summary>

```
波形数据形状: (1000, 1000)
明文数据形状: (1000, 16)
密文数据形状: (1000, 16)
数据类型 - 波形: float32, 明文: uint8, 密文: uint8

前3个明文 (十六进制):
Trace 0: 958d9d0f39f42c8a4e6f6ac1cbf56434
Trace 1: 8f16fae6dd3bfc79509589f10eda44c5
Trace 2: 0c8fce0749fdc1dc1cd1b5976e2c734a

前3个密文 (十六进制):
Trace 0: fc1b4003e543afa97e5f7c4f94d63cb3
Trace 1: 36c771022430a0e5c9861fed41942e85
Trace 2: ec6cf1a8c0ded26d9214e28fcd6d44a8

波形统计:
  最小值: 0.0000
  最大值: 125000.0000
  平均值: 25611.7031
  标准差: 16987.9805
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2761512638.py:45: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2761512638.py:68: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 18,215→525

**🤖 LLM:** 数据已加载：1000条轨迹，每条1000个采样点。从波形统计看，幅值范围较大（0-125000），这是典型的EM信号特征。现在让我进行方差分析来定位加密区域：

**🔧 → `python_jupyter`**

<details><summary>Code (1178 chars)</summary>

```python
# 计算方差来定位加密区域
variance = np.var(waves, axis=0)

plt.figure(figsize=(12, 6))
plt.plot(variance)
plt.title('波形方差 (用于定位加密区域)')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.grid(True, alpha=0.3)

# 找到方差最大的区域
window_size = 50
smoothed_variance = np.convolve(variance, np.ones(window_size)/window_size, mode='valid')
peak_idx = np.argmax(smoothed_variance) + window_size//2

# 标记峰值区域
plt.axvline(x=peak_idx, color='red', linestyle='--', alpha=0.7, label=f'峰值点: {peak_idx}')
plt.legend()
plt.savefig('variance_analysis.png')
plt.show()

print(f"方差峰值位置: {peak_idx}")
print(f"峰值方差值: {variance[peak_idx]:.2f}")

# 查看峰值附近的区域
search_range = 100
start = max(0, peak_idx - search_range)
end = min(len(variance), peak_idx + search_range)

print(f"\n峰值附近区域 [{start}:{end}] 的方差统计:")
print(f"  平均方差: {variance[start:end].mean():.2f}")
print(f"  最大方差: {variance[start:end].max():.2f}")
print(f"  最小方差: {variance[start:end].min():.2f}")

# 绘制峰值附近的平均波形
plt.figure(figsize=(12, 6))
mean_wave = waves.mean(axis=0)
plt.plot(mean_wave[start:end])
plt.title(f'峰值附近平均波形 (采样点 {start}-{end})')
plt.xlabel('采样点 (相对位置)')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)
plt.savefig('peak_region_mean_wave.png')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `方差峰值位置: 779
峰值方差值: 256512064.00

峰值附近区域 [679:879] 的方差统计:
  平均方差: 230742832.00
  最大方差: 491030080.00
  最小方差: 26253336.00
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2134715480.py:20: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2134715480.py:44: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 18,921→263

**🤖 LLM:** 方差分析显示加密区域在采样点779附近。现在让我进行明文相关性分析来进一步确认：

**🔧 → `plaintext_ciphertext_correlation`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy",
  "data_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy",
  "data_type": "plaintext",
  "byte_index": 0,
  "model": "HW"
}
```
</details>

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 273, "peak_region_end": 273, "peak_time_index": 273, "peak_correlation": 0.5353, "suggested_cpa_range": [223, 323], "all_byte_peaks": [273, 282, 290, 298, 275, 284, 292, 300, 276, 285, 293, 302, 278, 287, 296, 304], "byte_peaks_std": 9.7, "plot_path": "correlation_20260424_041125_713004.png"}`


![correlation_20260424_041125_713004.png](./correlation_20260424_041125_713004.png)


---

### Round 4 | tokens: 19,340→554

**🤖 LLM:** 明文相关性分析显示峰值在采样点273附近，这与方差分析的结果（779）不一致。让我检查一下波形，看看是否有多个加密区域或基线漂移：

**🔧 → `python_jupyter`**

<details><summary>Code (1178 chars)</summary>

```python
# 检查整个波形的特征
mean_wave = waves.mean(axis=0)

plt.figure(figsize=(15, 10))

# 完整波形
plt.subplot(3, 1, 1)
plt.plot(mean_wave)
plt.title('完整平均波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 区域1: 200-400 (明文相关性峰值区域)
plt.subplot(3, 1, 2)
plt.plot(range(200, 400), mean_wave[200:400])
plt.title('区域1: 采样点 200-400 (明文相关性峰值区域)')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 区域2: 700-900 (方差峰值区域)
plt.subplot(3, 1, 3)
plt.plot(range(700, 900), mean_wave[700:900])
plt.title('区域2: 采样点 700-900 (方差峰值区域)')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_regions_comparison.png')
plt.show()

# 检查基线漂移
print("检查基线漂移:")
baseline_start = 0
baseline_end = 100
baseline_means = waves[:, baseline_start:baseline_end].mean(axis=1)
print(f"基线区域 [{baseline_start}:{baseline_end}] 的均值统计:")
print(f"  最小值: {baseline_means.min():.2f}")
print(f"  最大值: {baseline_means.max():.2f}")
print(f"  平均值: {baseline_means.mean():.2f}")
print(f"  标准差: {baseline_means.std():.2f}")

# 检查是否有明显的DC偏移
if baseline_means.std() > 1000:  # 如果基线标准差较大，可能有DC漂移
    print("警告: 检测到明显的基线漂移，可能需要垂直对齐")
else:
    print("基线相对稳定，可能不需要垂直对齐")
```
</details>

**📋 ← `python_jupyter`:** `检查基线漂移:
基线区域 [0:100] 的均值统计:
  最小值: 24100.00
  最大值: 29195.00
  平均值: 26735.62
  标准差: 924.09
基线相对稳定，可能不需要垂直对齐
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1730921167.py:32: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 5 | tokens: 20,022→380

**🤖 LLM:** 根据知识图谱中的策略，对于软件实现（STM32F429 MCU），默认不需要垂直对齐。基线标准差为924.09，相对稳定。现在让我先尝试直接CPA攻击，使用软件实现的默认设置：S-box_out + HW模型。

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy",
  "leakage_model": "HW",
  "target": "S-box_out",
  "candidates": 30
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2048 chars)</summary>

```
{"recovered_key": "00112233445566778899AABBCCDDEEFF", "cpa_avg_correlation": 0.5644, "cpa_min_correlation": 0.4463, "n_traces": 1000, "target": "S-box_out", "plot_path": "cpa_result_20260424_041209_987830.png", "detail_file": "cpa_detail_20260424_041209_987830.json", "per_byte": [{"byte": 0, "key": "0x00", "correlation": 0.4463, "time_index": 353, "gap_pct": 65.4}, {"byte": 1, "key": "0x11", "correlation": 0.5536, "time_index": 364, "gap_pct": 65.4}, {"byte": 2, "key": "0x22", "correlation": 0.5321, "time_index": 418, "gap_pct": 69.9}, {"byte": 3, "key": "0x33", "correlation": 0.5563, "time_index": 385, "gap_pct": 66.8}, {"byte": 4, "key": "0x44", "correlation": 0.5662, "time_index": 356, "gap_pct": 67.7}, {"byte": 5, "key": "0x55", "correlation": 0.5341, "time_index": 366, "gap_pct": 69.6}, {"byte": 6, "key": "0x66", "correlation": 0.5802, "time_index": 377, "gap_pct": 69.5}, {"byte": 7, "key": "0x77", "correlation": 0.5952, "time_index": 387, "gap_pct": 68.4}, {"byte": 8, "key": "0x88", "correlation": 0.6141, "time_index": 358, "gap_pct": 66.5}, {"byte": 9, "key": "0x99", "correlation": 0.4875, "time_index": 368, "gap_pct": 71.4}, {"byte": 10, "key": "0xAA", "correlation": 0.6308, "time_index": 379, "gap_pct": 73.6}, {"byte": 11, "key": "0xBB", "correlation": 0.5474, "time_index": 390, "gap_pct": 68.3}, {"byte": 12, "key": "0xCC", "correlation": 0.6539, "time_index": 360, "gap_pct": 72.5}, {"byte": 13, "key": "0xDD", "correlation": 0.618, "time_index": 371, "gap_pct": 70.4}
...(truncated)
```
</details>


![cpa_result_20260424_041209_987830.png](./cpa_result_20260424_041209_987830.png)


---

### Round 6 | tokens: 21,269→340

**🤖 LLM:** 太好了！直接CPA攻击成功恢复了密钥：`00112233445566778899AABBCCDDEEFF`。所有16个字节都是高置信度的（gap_pct ≥ 15%）。现在让我验证这个密钥是否正确：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "00112233445566778899AABBCCDDEEFF",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy",
  "trace_index": 0
}
```
</details>

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "FC1B4003E543AFA97E5F7C4F94D63CB3", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 958d9d0f39f42c8a4e6f6ac1cbf56434... → FC1B4003E543AFA97E5F7C4F94D63CB3...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 7 | tokens: 21,755→666

**🤖 LLM:** 完美！密钥验证通过。CPA攻击成功恢复了正确的AES-128密钥。让我分析一下攻击结果：

**🔧 → `python_jupyter`**

<details><summary>Code (1587 chars)</summary>

```python
# 分析CPA结果
import json

# 加载CPA详细结果
with open('cpa_detail_20260424_041209_987830.json', 'r') as f:
    cpa_detail = json.load(f)

print("CPA攻击结果分析:")
print(f"恢复的密钥: {cpa_detail['recovered_key']}")
print(f"平均相关性: {cpa_detail['cpa_avg_correlation']:.4f}")
print(f"最小相关性: {cpa_detail['cpa_min_correlation']:.4f}")
print(f"高置信度字节数: {cpa_detail['high_confidence_count']}/16")

# 分析每个字节的相关性
print("\n各字节相关性分析:")
bytes_data = cpa_detail['per_byte']
correlations = [b['correlation'] for b in bytes_data]
gap_pcts = [b['gap_pct'] for b in bytes_data]
time_indices = [b['time_index'] for b in bytes_data]

print(f"相关性范围: {min(correlations):.4f} - {max(correlations):.4f}")
print(f"平均相关性: {np.mean(correlations):.4f}")
print(f"平均gap百分比: {np.mean(gap_pcts):.1f}%")
print(f"时间索引范围: {min(time_indices)} - {max(time_indices)}")

# 绘制相关性分布
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.bar(range(16), correlations)
plt.title('各字节CPA相关性')
plt.xlabel('字节索引')
plt.ylabel('相关性')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.bar(range(16), gap_pcts)
plt.title('各字节gap百分比')
plt.xlabel('字节索引')
plt.ylabel('gap百分比 (%)')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('cpa_analysis_details.png')
plt.show()

# 检查时间索引的模式
print(f"\n时间索引分析:")
print(f"时间索引平均值: {np.mean(time_indices):.1f}")
print(f"时间索引标准差: {np.std(time_indices):.1f}")

# 检查是否有明显的时间偏移模式
time_diffs = np.diff(time_indices)
print(f"相邻字节时间索引差异: {time_diffs}")
print(f"差异平均值: {np.mean(time_diffs):.1f}")

# 根据知识图谱，软件实现通常有连续的时间索引
if np.std(time_diffs) < 5:
    print("时间索引模式: 连续，符合软件实现特征")
else:
    print("时间索引模式: 分散，可能需要进一步分析")
```
</details>

**❌ ← `python_jupyter` Error:**

```
CPA攻击结果分析:

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[117][39m[32m, line 9[39m
[32m      6[39m     cpa_detail = json.load(f)
[32m      8[39m [38;5;28mprint[39m([33m"[39m[33mCPA攻击结果分析:[39m[33m"[39m)
[32m----> [39m[32m9[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m恢复的密钥: [39m[38;5;132;01m{[39;00m[43mcpa_detail[49m[43m[[49m[33;43m'[39;49m[33;43mrecovered_key[39;49m[33;43m'[39;49m[43m][49m[38;5;132;01m}[39;00m[33m"[39m)
[32m     10[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m平均相关性: [39m[38;5;132;01m{[39;00mcpa_detail[[33m'[39m[33mcpa_avg_correlation[39m[33m'[39m][38;5;132;01m:[39;00m[33m.4f[39m[38;5;132;01m}[39;00m[33m"[39m)
[32m     11[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33m最小相关性: [39m[38;5;132;01m{[39;00mcpa_detail[[33m'[39m[33mcpa_min_correlation[39m[33m'[39m][38;5;132;01m:[39;00m[33m.4f[39m[38;5;132;01m}[39;00m[33m"[39m)

[31mKeyError[39m: 'recovered_key'
```


---

### Round 8 | tokens: 23,110→1,231

**🤖 LLM:** 让我重新加载正确的CPA结果：

**🔧 → `python_jupyter`**

<details><summary>Code (2596 chars)</summary>

```python
# 直接从之前的CPA结果分析
print("CPA攻击成功总结:")
print("=" * 50)
print(f"恢复的密钥: 00112233445566778899AABBCCDDEEFF")
print(f"平均相关性: 0.5644")
print(f"最小相关性: 0.4463")
print(f"高置信度字节数: 16/16")

# 分析各字节结果
bytes_info = [
    {"byte": 0, "key": "0x00", "correlation": 0.4463, "gap_pct": 65.4},
    {"byte": 1, "key": "0x11", "correlation": 0.5536, "gap_pct": 65.4},
    {"byte": 2, "key": "0x22", "correlation": 0.5321, "gap_pct": 69.9},
    {"byte": 3, "key": "0x33", "correlation": 0.5563, "gap_pct": 66.8},
    {"byte": 4, "key": "0x44", "correlation": 0.5662, "gap_pct": 67.7},
    {"byte": 5, "key": "0x55", "correlation": 0.5341, "gap_pct": 69.6},
    {"byte": 6, "key": "0x66", "correlation": 0.5802, "gap_pct": 69.5},
    {"byte": 7, "key": "0x77", "correlation": 0.5952, "gap_pct": 68.4},
    {"byte": 8, "key": "0x88", "correlation": 0.6141, "gap_pct": 66.5},
    {"byte": 9, "key": "0x99", "correlation": 0.4875, "gap_pct": 71.4},
    {"byte": 10, "key": "0xAA", "correlation": 0.6308, "gap_pct": 73.6},
    {"byte": 11, "key": "0xBB", "correlation": 0.5474, "gap_pct": 68.3},
    {"byte": 12, "key": "0xCC", "correlation": 0.6539, "gap_pct": 72.5},
    {"byte": 13, "key": "0xDD", "correlation": 0.618, "gap_pct": 70.4},
    {"byte": 14, "key": "0xEE", "correlation": 0.5513, "gap_pct": 67.3},
    {"byte": 15, "key": "0xFF", "correlation": 0.564, "gap_pct": 71.3}
]

correlations = [b['correlation'] for b in bytes_info]
gap_pcts = [b['gap_pct'] for b in bytes_info]

print(f"\n相关性统计:")
print(f"  范围: {min(correlations):.4f} - {max(correlations):.4f}")
print(f"  平均值: {np.mean(correlations):.4f}")
print(f"  标准差: {np.std(correlations):.4f}")

print(f"\nGap百分比统计:")
print(f"  范围: {min(gap_pcts):.1f}% - {max(gap_pcts):.1f}%")
print(f"  平均值: {np.mean(gap_pcts):.1f}%")
print(f"  所有字节gap_pct > 15%: {all(gap > 15 for gap in gap_pcts)}")

print(f"\n攻击配置:")
print(f"  目标: S-box_out (S-box输出)")
print(f"  泄漏模型: HW (汉明重量)")
print(f"  轨迹数: 1000")
print(f"  采样点: 1000")

print(f"\n验证结果: ✅ 密钥验证通过")
print(f"  明文[0]: 958d9d0f39f42c8a4e6f6ac1cbf56434")
print(f"  计算密文: FC1B4003E543AFA97E5F7C4F94D63CB3")
print(f"  实际密文: FC1B4003E543AFA97E5F7C4F94D63CB3")

# 绘制结果
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.bar(range(16), correlations)
plt.title('各字节CPA相关性')
plt.xlabel('字节索引')
plt.ylabel('相关性')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.bar(range(16), gap_pcts)
plt.title('各字节gap百分比')
plt.xlabel('字节索引')
plt.ylabel('gap百分比 (%)')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('cpa_final_analysis.png')
plt.show()

print("\n" + "=" * 50)
print("攻击成功！STM32F429 MCU软件实现的AES-128密钥已被成功恢复。")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (735 chars)</summary>

```
CPA攻击成功总结:
==================================================
恢复的密钥: 00112233445566778899AABBCCDDEEFF
平均相关性: 0.5644
最小相关性: 0.4463
高置信度字节数: 16/16

相关性统计:
  范围: 0.4463 - 0.6539
  平均值: 0.5644
  标准差: 0.0509

Gap百分比统计:
  范围: 65.4% - 73.6%
  平均值: 69.0%
  所有字节gap_pct > 15%: True

攻击配置:
  目标: S-box_out (S-box输出)
  泄漏模型: HW (汉明重量)
  轨迹数: 1000
  采样点: 1000

验证结果: ✅ 密钥验证通过
  明文[0]: 958d9d0f39f42c8a4e6f6ac1cbf56434
  计算密文: FC1B4003E543AFA97E5F7C4F94D63CB3
  实际密文: FC1B4003E543AFA97E5F7C4F94D63CB3

==================================================
攻击成功！STM32F429 MCU软件实现的AES-128密钥已被成功恢复。
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\764079765.py:71: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 9 | tokens: 24,699→574

<details><summary><b>🤖 LLM Reasoning</b> (1151 chars)</summary>

## 总结

我已经成功对STM32F429 MCU软件实现的AES-128进行了CPA密钥恢复攻击。以下是关键结果：

### 攻击结果
- **恢复的密钥**: `00112233445566778899AABBCCDDEEFF`
- **验证状态**: ✅ 完全匹配（使用第一条轨迹的明文/密文验证）
- **攻击成功率**: 16/16字节高置信度恢复

### 技术细节
1. **数据特征**:
   - 1000条电磁侧信道轨迹
   - 每条轨迹1000个采样点
   - 幅值范围: 0-125,000（典型EM信号）

2. **攻击配置**:
   - **目标**: S-box输出（`S-box_out`）
   - **泄漏模型**: 汉明重量（`HW`）
   - **候选密钥数**: 30个/字节
   - **无需预处理**: 直接CPA攻击成功

3. **性能指标**:
   - 平均相关性: 0.5644
   - 最小相关性: 0.4463（字节0）
   - 最大相关性: 0.6539（字节12）
   - 平均gap百分比: 69.0%（所有字节>15%）

### 知识图谱应用验证
根据DKG知识图谱的指导：
1. **软件实现策略**: 使用`S-box_out` + `HW`模型，符合软件实现的默认配置
2. **无需垂直对齐**: 基线标准差924.09，相对稳定，符合软件实现不需要垂直对齐的原则
3. **直接CPA成功**: 验证了"软件实现：方差优先ROI探索"原则，但在此案例中直接CPA已足够

### 生成的输出文件
1. `raw_waveforms.png` - 原始波形图
2. `mean_std_waveforms.png` - 平均和标准差波形
3. `variance_analysis.png` - 方差分析图
4. `peak_region_mean_wave.png` - 峰值区域平均波形
5. `waveform_regions_comparison.png` - 波形区域对比
6. `correlation_20260424_041125_713004.png` - 明文相关性分析
7. `cpa_result_20260424_041209_987830.png` - CPA结果图
8. `cpa_detail_20260424_041209_987830.json` - CPA详细结果
9. `cpa_final_analysis.png` - CPA最终分析图

攻击完全成功，无需任何预处理或参数调整，验证了针对STM32F429 MCU软件实现AES的标准CPA攻击方法的有效性。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 17,014 | 811 | 17,825 |
| 2 | 18,215 | 525 | 18,740 |
| 3 | 18,921 | 263 | 19,184 |
| 4 | 19,340 | 554 | 19,894 |
| 5 | 20,022 | 380 | 20,402 |
| 6 | 21,269 | 340 | 21,609 |
| 7 | 21,755 | 666 | 22,421 |
| 8 | 23,110 | 1,231 | 24,341 |
| 9 | 24,699 | 574 | 25,273 |
| **Total** | **184,345** | **5,344** | **189,689** |

## 8. Final Output

## 总结

我已经成功对STM32F429 MCU软件实现的AES-128进行了CPA密钥恢复攻击。以下是关键结果：

### 攻击结果
- **恢复的密钥**: `00112233445566778899AABBCCDDEEFF`
- **验证状态**: ✅ 完全匹配（使用第一条轨迹的明文/密文验证）
- **攻击成功率**: 16/16字节高置信度恢复

### 技术细节
1. **数据特征**:
   - 1000条电磁侧信道轨迹
   - 每条轨迹1000个采样点
   - 幅值范围: 0-125,000（典型EM信号）

2. **攻击配置**:
   - **目标**: S-box输出（`S-box_out`）
   - **泄漏模型**: 汉明重量（`HW`）
   - **候选密钥数**: 30个/字节
   - **无需预处理**: 直接CPA攻击成功

3. **性能指标**:
   - 平均相关性: 0.5644
   - 最小相关性: 0.4463（字节0）
   - 最大相关性: 0.6539（字节12）
   - 平均gap百分比: 69.0%（所有字节>15%）

### 知识图谱应用验证
根据DKG知识图谱的指导：
1. **软件实现策略**: 使用`S-box_out` + `HW`模型，符合软件实现的默认配置
2. **无需垂直对齐**: 基线标准差924.09，相对稳定，符合软件实现不需要垂直对齐的原则
3. **直接CPA成功**: 验证了"软件实现：方差优先ROI探索"原则，但在此案例中直接CPA已足够

### 生成的输出文件
1. `raw_waveforms.png` - 原始波形图
2. `mean_std_waveforms.png` - 平均和标准差波形
3. `variance_analysis.png` - 方差分析图
4. `peak_region_mean_wave.png` - 峰值区域平均波形
5. `waveform_regions_comparison.png` - 波形区域对比
6. `correlation_20260424_041125_713004.png` - 明文相关性分析
7. `cpa_result_20260424_041209_987830.png` - CPA结果图
8. `cpa_detail_20260424_041209_987830.json` - CPA详细结果
9. `cpa_final_analysis.png` - CPA最终分析图

攻击完全成功，无需任何预处理或参数调整，验证了针对STM32F429 MCU软件实现AES的标准CPA攻击方法的有效性。
