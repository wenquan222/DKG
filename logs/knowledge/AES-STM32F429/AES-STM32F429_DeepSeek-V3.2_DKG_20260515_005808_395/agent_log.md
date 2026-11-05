# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260515_005808_395 |
| Duration | 424.4s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp_knowledge_only\AES-STM32F429_DeepSeek-V3.2_DKG_20260515_005808_395` |
| Total LLM Calls | 9 |
| First Round | prompt: 13,359, completion: 642 |
| Last Round | prompt: 32,705, completion: 440 |
| Total Tokens | 192,909 (prompt: 184,823, completion: 8,086) |

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

KG returned 46001 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (48798 chars, click to expand)</summary>

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

**Summary**: 35 upper entities, 30 relationships, 20 diagnostic chains, 13 strategies


## 1. Upper Layer Entities (35)


### Algorithm (1)

- **AES** — num_rounds=['10', '14'], encryption_mode=['CBC', 'ECB'], key_length=['128', '256']

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

### Pipeline (11)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Correlation-based pattern matching for RDI removal** — source=expert_experience, trigger_condition=random delays exhibit regular patterns (e.g., repetitive dummy loops), applicable_scenarios=software implementations where dummy operations or AES operation blocks have distinctive and consistent leakage patterns
- **HMM cryptanalysis of RDI-protected implementations** — source=expert_experience, trigger_condition=attacking a software implementation protected with random delay insertions, applicable_scenarios=microcontroller implementations of symmetric block ciphers (e.g., AES) with random delays inserted via dummy loops or interrupts
- **HMM-based Random Delay Removal and CPA** — source=PAP-33-2013-ePrint-HMM-Remove-Random-Delays, trigger_condition=when attacking a software implementation protected with random delay insertions (RDI) via power traces, applicable_scenarios=Embedded software implementations (e.g., on 8-bit microcontrollers) using random delays as a hiding countermeasure; requires ability to profile instruction cycles on a similar device.
- **Improved Collision DL-SCA with Shared Feature Extractor and Multiple Distinguishers** — source=This work, trigger_condition=non-profiled side-channel attack on AES software implementation, applicable_scenarios=masked AES software implementations with serial Sbox computations
- **Practical Second-Order DPA Attack Strategy** — source=research_paper, trigger_condition=when performing a second-order DPA attack on a masked implementation, applicable_scenarios=masked software implementations of block ciphers, especially on 8-bit smart cards

### StatMethod (8)

- **Algebraic System Construction** — type=non_profiled
- **CEMA** — type=non_profiled
- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **First CPA probe (without alignment)** — type=non_profiled

## 2. Relationships (30)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: offset, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:offset`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
- `DeviceClass:STM32F429` —[works_with [source_text=一阶CPA分析...猜测出真实密钥0x00112233445566778899AABBCCDDEEFF。, support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `StatMethod:CPA`
- `DeviceClass:STM32F429` —[works_with [source_text=电磁分析...如图 778为对电磁波执行一阶CPA的结果, support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `TraceType:EM`
- `DeviceClass:STM32F429` —[works_with [source_text=能量信号采波 & 一阶CPA分析, support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `TraceType:Power`
- `DeviceClass:STM32F429` —[works_with [source_text=一阶CPA分析...猜测出真实密钥0x00112233445566778899AABBCCDDEEFF。, support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `Algorithm:AES`
- `DeviceClass:STM32F429` —[works_with [source_text=Static alignment discarded 0 traces., support_count=1, confidence=0.2, source_papers=["MAN-05-2024-MathMagic-STM32F429-UART-AES-Example"]]]→ `Preprocessing:Static Alignment`
- `DeviceClass:32-bit implementation` —[acquires_via [source_text=A similar attack has also been conducted on a 32-bit implementation, support_count=1, confidence=0.2, source_papers=["PAP-04-2004-CHES-Brier-CPA-Leakage-Model"]]]→ `TraceType:Power`
- `DeviceClass:32-bit implementation` —[works_with [source_text=A similar attack has also been conducted on a 32-bit implementation, support_count=1, confidence=0.2, source_papers=["PAP-04-2004-CHES-Brier-CPA-Leakage-Model"]]]→ `Algorithm:DES`
- `DeviceClass:32-bit implementation` —[works_with [source_text=A similar attack has also been conducted on a 32-bit implementation, support_count=1, confidence=0.2, source_papers=["PAP-04-2004-CHES-Brier-CPA-Leakage-Model"]]]→ `StatMethod:CPA`
- `DeviceClass:ASIC implementation of PicoRV32 on Saidoyoki board` —[works_with [source_text=experimental validation on ASIC implementation of PicoRV32 on Saidoyoki board, support_count=1, confidence=0.2, source_papers=["PAP-81-2024-ePrint-ARCHER-RISC-V"]]]→ `StatMethod:Correlation Attack`
- `DeviceClass:ASIC implementation of PicoRV32 on Saidoyoki board` —[acquires_via [source_text=Figure 9 depicts the correlation plot where we observe two clear peaks with a correlation coefficient around 0.45., support_count=1, confidence=0.2, source_papers=["PAP-81-2024-ePrint-ARCHER-RISC-V"]]]→ `TraceType:Power`
- `StatMethod:CPA` —[strategy_applies_to [condition=Non-profiled CPA on DES (any device class: contact smartcard, contactless smartcard, FPGA, MCU). The DES CPA tool has returned a high-confidence round-1 48-bit subkey K1 (high_confidence_count >= 6/8 S-boxes, gap_pct >= 20%, avg_correlation reasonable for the device class), BUT encrypt_decrypt_verify against the DES master key has returned MISMATCH. The DES CPA tool may have populated a 'master_key' field with a placeholder (K1 zero-padded, K1 duplicated, or an arbitrary parity assignment) that is not the actual master key., applicability=specific, source_papers=["expert_experience"]]]→ `Strategy:DES master key recovery from 48-bit round-1 subkey via PC-2 inverse + parity enumeration`
- `StatMethod:CPA` —[strategy_applies_to [condition=Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap), applicability=specific, source_papers=["expert_experience"]]]→ `Strategy:Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)`
- `StatMethod:CPA` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `StatMethod:CPA` —[strategy_applies_to [condition=Any non-profiled CPA workflow on AES / DES / SM4 across any device class. Triggered whenever the agent has obtained a CPA output (typically high_confidence_count, gap_pct, avg_correlation looking favourable for the device class) and is about to write a final natural-language success message to the user, OR is considering terminating the session., applicability=general, source_papers=["expert_experience"]]]→ `Strategy:Do NOT declare key-recovery success based on CPA-internal metrics; encrypt_decrypt_verify MATCH is mandatory`
- `StatMethod:CPA` —[strategy_applies_to [condition=Non-profiled CPA on any symmetric block cipher (AES / DES / SM4); at least one prior CPA run (aligned or direct) has yielded high_confidence_count in or above the gray band (AES >= 10/16, DES >= 3/8, SM4 per-round >= 2/4); key_search was invoked once with default or near-default parameters and returned found=false; OR a dual-mode (e.g., linear-HD / S-box_in on contactless AES / DES) attack returned two candidates with per-byte gap_pct == 0, applicability=specific, source_papers=["expert_experience"]]]→ `Strategy:key_search found=false is NOT CPA failure — escalate search budget + dual-mode both branches BEFORE pivoting any other dimension`
- `DeviceClass:32-bit STM Controller` —[works_with [source_text=CHES CTF ... AutoPOI ... 1830, support_count=1, confidence=0.2, source_papers=["PAP-74-2023-ePrint-AutoPOI"]]]→ `Algorithm:AES`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `LeakageModel:identity`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Pipeline:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Preprocessing:Resampling`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `AttackPoint:S-box Output`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=perform correlation power analysis on the processed traces, typically targeting first-round S-box output with Hamming weight model, source_text=perform correlation power analysis on the processed traces, typically targeting first-round S-box output with Hamming weight model, support_count=1, is_optional=False]]→ `StatMethod:CPA`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=find the most probable state sequence to identify and remove dummy cycles, outputting aligned traces, source_text=find the most probable state sequence to identify and remove dummy cycles, outputting aligned traces, support_count=1, is_optional=False]]→ `Preprocessing:Viterbi algorithm for delay removal`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=define states corresponding to instruction cycles and transition probabilities based on the code flow; compact representation for dummy loops, source_text=define states corresponding to instruction cycles and transition probabilities based on the code flow; compact representation for dummy loops, support_count=1, is_optional=False]]→ `DiagnosticMethod:HMM model construction`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[consists_of [parameters_note=build Gaussian templates for each instruction cycle using PCA for dimensionality reduction (3 dimensions kept), condition=profiling phase requires a training device with known delay lengths, source_text=build Gaussian templates for each instruction cycle using PCA for dimensionality reduction (3 dimensions kept), support_count=1]]→ `DiagnosticMethod:Template building for instruction cycles`
- `Pipeline:HMM cryptanalysis of RDI-protected implementations` —[alternative_to [source_text=Heuristic and less generic than HMM; effective only when patterns are regular and distinguishable., support_count=1, confidence=0.2, source_papers=["PAP-27-2012-ePrint-Durvaux-Cryptanalysis-Random-Delay"]]]→ `Pipeline:Correlation-based pattern matching for RDI removal`

## 3. Diagnostic Chains (20)


### Obs: `attack_position_selection` — any
- **Cause** (high): The S-box output is a non-linear operation that often exhibits strong leakage in HW model, and is a common target in first-round attacks
- **Check**: Check implementation details for known leakage points
- **Action**: Set the target to 'S-box out' and model to 'HW' for first-round CPA on AES
  - operation: `adjust_param`
  - target: `cpa.target, cpa.model`
  - strategy: Target: S-box out, Model: HW
- **Relates to**: AttackPoint:`S-box Output`

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

### Obs: `resistance_to_higher_order_dpa` — any
- **Cause** (high): Using the same random mask for multiple S-box transformations within a single AES execution creates a correlation between intermediate variables. An attacker can perform a second-order DPA by analyzing power consumption at two points in time where the same mask is used.
- **Action**: Use mutually independent random masks for different S-boxes, especially in the first and last rounds. Randomize the order of S-box computations within a round if possible.
  - operation: `adjust_param`
  - target: `mask_independence`
  - strategy: Use mutually independent random masks for different S-boxes, especially in the first and last rounds. Randomize the order of S-box computations within a round if possible.
- **Relates to**: Countermeasure:`Shuffling of S-box operations`

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
- **Relates to**: AttackPoint:`Inverse S-box Output`

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

### Obs: `key_recovery_success_rate` — any
- **Cause** (high): using standalone collision attack or standalone DPA attack, which do not exploit all available key information
- **Check**: experimental comparison of success rates
- **Action**: combine collision attack with DPA
  - operation: `add_step`
  - target: `attack method`
  - strategy: use DPA ranking to filter chain guesses in collision attack
- **Relates to**: Pipeline:`Combined Collision Attack Framework`

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

### ⭐ ⚠ [anti_pattern_set] Do NOT declare key-recovery success based on CPA-internal metrics; encrypt_decrypt_verify MATCH is mandatory
- **Trigger**: Any non-profiled CPA workflow on AES / DES / SM4 across any device class. Triggered whenever the agent has obtained a CPA output (typically high_confidence_count, gap_pct, avg_correlation looking favourable for the device class) and is about to write a final natural-language success message to the user, OR is considering terminating the session.
- **Rationale**: CPA-internal metrics are necessary but not sufficient: a candidate can be off by one S-box subkey or by the master-key reconstruction step while still showing a high hc. encrypt_decrypt_verify is the only ground-truth signal, so success is declared only after it returns MATCH.
- **Anti-pattern 1**: (unnamed)
  - Correct: ['Step 1: After ANY CPA invocation that returns a candidate key, the IMMEDIATE next tool call MUST be encrypt_decrypt_verify on that candidate. Do not write any natural-language conclusion in between.', 'Step 2: encrypt_decrypt_verify result must be the basis of the success/failure decision. verification=PASSED (MATCH) → success can be declared. verification=FAILED (MISMATCH) → continue diagnostic loop; do NOT terminate session.', 'Step 3: On verify MISMATCH, the diagnostic ladder is: (a) for DES: invoke key_search per Strategy strat_des_master_key_recovery_protocol; (b) for AES with HD targets: try k XOR 0xFF dual-mode candidate; (c) for SM4: confirm all 4 round keys recovered, then verify each round-key independently before claiming master-key success; (d) for any cipher: invoke key_search with default 50000 budget if not yet tried; (e) only after these canonical recovery paths fail should the agent pivot leakage target / preprocessing / re-collect traces.', "Step 4: A natural-language success message must contain explicit reference to the verify result, e.g. 'encrypt_decrypt_verify PASSED with MATCH on all 16 ciphertext bytes; recovered master key = ...', NOT just 'I recovered the master key = ...'", "Step 5: If the round budget is nearly exhausted and no MATCH has been obtained, the correct termination output is 'CPA produced candidate K = ... with hc = .../... and gap_pct = ...%, but encrypt_decrypt_verify returned MISMATCH after attempting key_search and canonical recovery paths', NOT 'recovered master key = ...'."]
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

### ⭐ • [canonical_pipeline_principle] DES master key recovery from 48-bit round-1 subkey via PC-2 inverse + parity enumeration
- **Trigger**: Non-profiled CPA on DES (any device class: contact smartcard, contactless smartcard, FPGA, MCU). The DES CPA tool has returned a high-confidence round-1 48-bit subkey K1 (high_confidence_count >= 6/8 S-boxes, gap_pct >= 20%, avg_correlation reasonable for the device class), BUT encrypt_decrypt_verify against the DES master key has returned MISMATCH. The DES CPA tool may have populated a 'master_key' field with a placeholder (K1 zero-padded, K1 duplicated, or an arbitrary parity assignment) that is not the actual master key.
- **Rationale**: CPA on round 1 recovers only the 48-bit subkey K1. PC-2 omits eight bits of the 56-bit state and the parity bits are fixed by the byte parity rule, so the master key is one of at most 256 candidates; enumerating them is bounded and far cheaper than re-running the attack.
- **Content**: [{"principle": "DES has a 64-bit master key (with 8 parity bits) and CPA on round 1 only directly recovers the 48-bit round-1 subkey K1. Recovering the master key from K1 requires (a) inverting PC-2 to recover C1||D1 (56 bits with 8 missing positions), (b) right-shifting by 1 to recover C0||D0, (c) inverting PC-1 to recover the 64-bit master key with 8 unknown parity bits. The total brute-force sp
- **Applies to**: StatMethod:CPA, Algorithm:DES

### ⭐ • [canonical_pipeline_principle] Software implementation: variance-first ROI exploration before alignment
- **Trigger**: Software cryptographic implementation (any MCU: STM32F1/F4/Cortex/AVR/Arduino; or contact smartcard running software crypto) + non-profiled CPA + direct CPA returns unstable high_confidence_count below empirical_threshold
- **Rationale**: A software trace contains plaintext I/O, key-schedule computation, and the encryption rounds. Only the round body carries S-box leakage, and it shows a distinct per-sample variance increase, so variance-based ROI selection is more reliable than aligning the whole trace first.
- **Content**: [{"principle": "For software cryptographic implementations, when direct CPA does NOT yield stable high-confidence candidates, the agent MUST first perform variance-based / energy-signature ROI exploration (e.g., np.var / np.std over sliding windows) to locate the encryption region, BEFORE deciding alignment intervals or switching leakage targets.", "reason": "Software implementations on MCU/smartc
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

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

**[No SCA-Specific Tools — Implementation Required]**
You have access to a Python (Jupyter) kernel and the kg_search tool, but NO
specialized SCA tools. You must implement the entire attack pipeline yourself
(waveform inspection, alignment, CPA, key search, encrypt/decrypt verification)
in Python with numpy/scipy/sklearn/pycryptodome etc.

**[Session Directory]**
All files for this session are stored in: ..\logs\exp_knowledge_only\AES-STM32F429_DeepSeek-V3.2_DKG_20260515_005808_395
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp_knowledge_only\AES-STM32F429_DeepSeek-V3.2_DKG_20260515_005808_395/'` or `'../logs/...'` — just use the bare filename.
- When using file paths in Python code, always use forward slashes (/) or raw strings (r'...').
- Never invent, guess, or modify input file paths. If unsure, use python_jupyter with os.listdir() to check.

**[How to Work]**
- Use your own SCA expertise to plan and execute.
- Execute step by step based on YOUR judgment of the waveform characteristics.
- The KG provides configuration guidance and diagnostic strategies; use it to
  decide WHAT to do (attack point, leakage model, preprocessing chain, etc.).
- Write all SCA logic in Python yourself: there are NO specialized tools for CPA,
  alignment, key search, or crypto verification. Use jupyter + numpy/scipy.
- Use kg_search ONLY when:
  (1) You encounter an unexpected result (e.g., low correlation, verification failed)
  (2) You are unsure about a specific parameter and want to check best practices
- Do NOT search before every step — trust your own analysis first.
- After each tool call, evaluate the result yourself before deciding next action.

```
</details>

## 6. Execution


---

### Round 1 | tokens: 13,359→642

**🤖 LLM:** 我来帮您对STM32F429 MCU软件实现的AES算法进行CPA密钥恢复。首先，让我加载数据并检查波形特征。

**🔧 → `python_jupyter`**

<details><summary>Code (1411 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os

# 加载数据
plain_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy'
cipher_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy'
wave_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy'

# 检查文件是否存在
print("文件存在性检查:")
print(f"明文文件: {os.path.exists(plain_path)}")
print(f"密文文件: {os.path.exists(cipher_path)}")
print(f"波形文件: {os.path.exists(wave_path)}")

# 加载数据
plaintexts = np.load(plain_path)
ciphertexts = np.load(cipher_path)
traces = np.load(wave_path)

print(f"\n数据形状:")
print(f"明文: {plaintexts.shape}")
print(f"密文: {ciphertexts.shape}")
print(f"波形: {traces.shape}")

# 检查数据类型和范围
print(f"\n数据类型:")
print(f"明文: {plaintexts.dtype}, 范围: [{plaintexts.min()}, {plaintexts.max()}]")
print(f"密文: {ciphertexts.dtype}, 范围: [{ciphertexts.min()}, {ciphertexts.max()}]")
print(f"波形: {traces.dtype}, 范围: [{traces.min():.2f}, {traces.max():.2f}]")

# 查看前几个明文和密文
print(f"\n前3个明文 (十六进制):")
for i in range(3):
    print(f"Trace {i}: {plaintexts[i].tobytes().hex()}")

print(f"\n前3个密文 (十六进制):")
for i in range(3):
    print(f"Trace {i}: {ciphertexts[i].tobytes().hex()}")
```
</details>

**📋 ← `python_jupyter`:** `文件存在性检查:
明文文件: True
密文文件: True
波形文件: True

数据形状:
明文: (1000, 16)
密文: (1000, 16)
波形: (1000, 1000)

数据类型:
明文: uint8, 范围: [0, 255]
密文: uint8, 范围: [0, 255]
波形: float32, 范围: [0.00, 125000.00]

前3个明文 (十六进制):
Trace 0: 958d9d0f39f42c8a4e6f6ac1cbf56434
Trace 1: 8f16fae6dd3bfc79509589f10eda44c5
Trace 2: 0c8fce0749fdc1dc1cd1b5976e2c734a

前3个密文 (十六进制):
Trace 0: fc1b4003e543afa97e5f7c4f94d63cb3
Trace 1: 36c771022430a0e5c9861fed41942e85
Trace 2: ec6cf1a8c0ded26d9214e28fcd6d44a8`


---

### Round 2 | tokens: 14,295→723

**🤖 LLM:** 很好！数据加载成功。我们有1000条轨迹，每条1000个采样点。现在让我检查波形特征，看看是否需要预处理。

**🔧 → `python_jupyter`**

<details><summary>Code (1593 chars)</summary>

```python
# 可视化一些轨迹
plt.figure(figsize=(15, 10))

# 绘制前10条轨迹
plt.subplot(2, 2, 1)
for i in range(10):
    plt.plot(traces[i], alpha=0.5, linewidth=0.5)
plt.title('前10条原始轨迹')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 绘制平均轨迹
plt.subplot(2, 2, 2)
mean_trace = np.mean(traces, axis=0)
plt.plot(mean_trace, 'b-', linewidth=1)
plt.title('平均轨迹')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 绘制方差轨迹
plt.subplot(2, 2, 3)
var_trace = np.var(traces, axis=0)
plt.plot(var_trace, 'r-', linewidth=1)
plt.title('方差轨迹')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.grid(True, alpha=0.3)

# 绘制SNR（信噪比）轨迹
plt.subplot(2, 2, 4)
signal_power = np.var(mean_trace)
noise_power = np.mean(np.var(traces - mean_trace, axis=0))
snr_trace = var_trace / np.mean(np.var(traces - mean_trace, axis=0))
plt.plot(snr_trace, 'g-', linewidth=1)
plt.title('SNR轨迹')
plt.xlabel('采样点')
plt.ylabel('SNR')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# 检查是否需要对齐 - 查看轨迹间的相关性
print("轨迹对齐分析:")
print(f"平均轨迹最大值位置: {np.argmax(mean_trace)}")
print(f"方差轨迹最大值位置: {np.argmax(var_trace)}")
print(f"SNR轨迹最大值位置: {np.argmax(snr_trace)}")

# 检查轨迹间的偏移
# 计算每条轨迹与平均轨迹的互相关
max_shifts = []
for i in range(min(20, len(traces))):  # 只检查前20条以节省时间
    corr = signal.correlate(traces[i], mean_trace, mode='same')
    max_shift = np.argmax(corr) - len(mean_trace)//2
    max_shifts.append(max_shift)
    
print(f"\n前20条轨迹的偏移量范围: [{min(max_shifts)}, {max(max_shifts)}]")
print(f"平均偏移量: {np.mean(max_shifts):.2f}")
print(f"偏移量标准差: {np.std(max_shifts):.2f}")
```
</details>

**📋 ← `python_jupyter`:** `轨迹对齐分析:
平均轨迹最大值位置: 999
方差轨迹最大值位置: 9
SNR轨迹最大值位置: 9

前20条轨迹的偏移量范围: [0, 0]
平均偏移量: 0.00
偏移量标准差: 0.00`


---

### Round 3 | tokens: 15,096→830

**🤖 LLM:** 很好！轨迹看起来已经对齐了（偏移量为0）。现在让我检查是否需要滤波。根据KG知识，对于软件实现，通常需要低通滤波。让我先检查一下频率特性。

**🔧 → `python_jupyter`**

<details><summary>Code (1970 chars)</summary>

```python
# 检查频率特性
from scipy.fft import fft, fftfreq

# 计算平均轨迹的FFT
mean_trace = np.mean(traces, axis=0)
N = len(mean_trace)
yf = fft(mean_trace)
xf = fftfreq(N, 1)  # 假设采样率为1

# 只取正频率
positive_freq = xf[:N//2]
positive_magnitude = 2.0/N * np.abs(yf[:N//2])

plt.figure(figsize=(12, 6))
plt.plot(positive_freq, positive_magnitude)
plt.title('平均轨迹的频率谱')
plt.xlabel('频率')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)
plt.xlim([0, 0.5])  # 查看低频部分
plt.savefig('frequency_spectrum.png', dpi=150, bbox_inches='tight')
plt.show()

# 检查高频噪声
print("频率分析:")
print(f"最大频率分量位置: {positive_freq[np.argmax(positive_magnitude)]:.4f}")
print(f"前10个主要频率分量:")
top10_idx = np.argsort(positive_magnitude)[-10:][::-1]
for idx in top10_idx:
    print(f"  频率: {positive_freq[idx]:.4f}, 幅值: {positive_magnitude[idx]:.2f}")

# 应用低通滤波（根据KG建议，软件实现使用权重2-3的移动平均）
def moving_average(data, window_size):
    """简单的移动平均滤波器"""
    window = np.ones(window_size) / window_size
    return np.convolve(data, window, mode='same')

# 测试不同窗口大小的滤波效果
window_sizes = [3, 5, 7]
filtered_traces = {}

for ws in window_sizes:
    filtered = np.zeros_like(traces)
    for i in range(len(traces)):
        filtered[i] = moving_average(traces[i], ws)
    filtered_traces[ws] = filtered
    
# 可视化滤波效果
plt.figure(figsize=(15, 10))
for idx, ws in enumerate(window_sizes, 1):
    plt.subplot(2, 2, idx)
    plt.plot(traces[0], 'b-', alpha=0.5, label='原始', linewidth=0.5)
    plt.plot(filtered_traces[ws][0], 'r-', label=f'滤波(窗口={ws})', linewidth=1)
    plt.title(f'窗口大小={ws}的滤波效果')
    plt.xlabel('采样点')
    plt.ylabel('幅值')
    plt.legend()
    plt.grid(True, alpha=0.3)

# 绘制滤波后的方差
plt.subplot(2, 2, 4)
for ws in window_sizes:
    var_filtered = np.var(filtered_traces[ws], axis=0)
    plt.plot(var_filtered, label=f'窗口={ws}', linewidth=1)
plt.title('滤波后的方差轨迹')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('filtering_effects.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `频率分析:
最大频率分量位置: 0.0000
前10个主要频率分量:
  频率: 0.0000, 幅值: 51223.41
  频率: 0.0010, 幅值: 4087.73
  频率: 0.0500, 幅值: 3999.93
  频率: 0.0510, 幅值: 3024.59
  频率: 0.0020, 幅值: 2440.15
  频率: 0.1020, 幅值: 2147.49
  频率: 0.0050, 幅值: 2029.53
  频率: 0.0520, 幅值: 1628.45
  频率: 0.0040, 幅值: 1559.97
  频率: 0.0060, 幅值: 1388.15`


---

### Round 4 | tokens: 16,153→2,389

**🤖 LLM:** 现在让我根据KG知识进行CPA攻击。根据KG，对于STM32F429软件实现的AES，我应该：
1. 使用S-box输出作为攻击点
2. 使用汉明重量(HW)模型
3. 首先尝试直接CPA，如果需要再考虑对齐

让我实现CPA攻击：

**🔧 → `python_jupyter`**

<details><summary>Code (4321 chars)</summary>

```python
# 实现CPA攻击
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import itertools

# AES S-box
sbox = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

# 汉明重量计算
def hamming_weight(x):
    """计算字节的汉明重量"""
    return bin(x).count('1')

# 生成假设矩阵
def generate_hypothesis_matrix(plaintexts, key_byte_guess, byte_index):
    """
    为特定字节位置生成假设矩阵
    plaintexts: 明文数组 (n_traces, 16)
    key_byte_guess: 密钥字节猜测值 (0-255)
    byte_index: 字节位置 (0-15)
    """
    n_traces = len(plaintexts)
    hypotheses = np.zeros(n_traces)
    
    for i in range(n_traces):
        # 第一轮AddRoundKey + SubBytes的输出
        state_byte = plaintexts[i, byte_index] ^ key_byte_guess
        sbox_out = sbox[state_byte]
        # 使用汉明重量模型
        hypotheses[i] = hamming_weight(sbox_out)
    
    return hypotheses

# CPA计算
def cpa_attack(traces, plaintexts, target_byte):
    """
    对特定字节位置执行CPA攻击
    traces: 轨迹数据 (n_traces, n_samples)
    plaintexts: 明文数据 (n_traces, 16)
    target_byte: 目标字节位置 (0-15)
    """
    n_traces, n_samples = traces.shape
    correlations = np.zeros((256, n_samples))
    
    # 对每个密钥猜测计算相关性
    for kg in range(256):
        # 生成假设
        H = generate_hypothesis_matrix(plaintexts, kg, target_byte)
        
        # 标准化假设
        H_mean = np.mean(H)
        H_std = np.std(H)
        if H_std == 0:
            H_std = 1e-10
        H_norm = (H - H_mean) / H_std
        
        # 对每个采样点计算相关性
        for s in range(n_samples):
            T = traces[:, s]
            T_mean = np.mean(T)
            T_std = np.std(T)
            if T_std == 0:
                T_std = 1e-10
            T_norm = (T - T_mean) / T_std
            
            # Pearson相关系数
            corr = np.sum(H_norm * T_norm) / n_traces
            correlations[kg, s] = corr
    
    return correlations

# 执行CPA攻击
print("开始CPA攻击...")
print("目标: AES第一轮S-box输出，使用汉明重量模型")

# 使用滤波后的轨迹（窗口大小3，根据KG建议）
filtered_traces_ws3 = filtered_traces[3]

# 对每个字节位置执行CPA
all_correlations = []
best_keys = []
best_correlations = []

for byte_idx in range(16):
    print(f"\n攻击字节 {byte_idx}...")
    correlations = cpa_attack(filtered_traces_ws3, plaintexts, byte_idx)
    all_correlations.append(correlations)
    
    # 找到最佳密钥猜测
    max_corr = np.max(np.abs(correlations))
    best_key = np.argmax(np.max(np.abs(correlations), axis=1))
    
    best_keys.append(best_key)
    best_correlations.append(max_corr)
    
    print(f"  最佳密钥猜测: 0x{best_key:02x}, 最大相关系数: {max_corr:.4f}")

# 显示结果
print("\n" + "="*60)
print("CPA攻击结果:")
print("="*60)
for i in range(16):
    print(f"字节 {i:2d}: 密钥猜测 = 0x{best_keys[i]:02x}, 最大相关系数 = {best_correlations[i]:.4f}")

# 组合密钥
recovered_key = bytes(best_keys)
print(f"\n恢复的密钥: {recovered_key.hex()}")
print(f"密钥字符串: {recovered_key}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1521 chars)</summary>

```
开始CPA攻击...
目标: AES第一轮S-box输出，使用汉明重量模型

攻击字节 0...
  最佳密钥猜测: 0x00, 最大相关系数: 0.5860

攻击字节 1...
  最佳密钥猜测: 0x11, 最大相关系数: 0.4461

攻击字节 2...
  最佳密钥猜测: 0x22, 最大相关系数: 0.4446

攻击字节 3...
  最佳密钥猜测: 0x33, 最大相关系数: 0.4771

攻击字节 4...
  最佳密钥猜测: 0x44, 最大相关系数: 0.4802

攻击字节 5...
  最佳密钥猜测: 0x55, 最大相关系数: 0.4650

攻击字节 6...
  最佳密钥猜测: 0x66, 最大相关系数: 0.5083

攻击字节 7...
  最佳密钥猜测: 0x77, 最大相关系数: 0.5111

攻击字节 8...
  最佳密钥猜测: 0x88, 最大相关系数: 0.5063

攻击字节 9...
  最佳密钥猜测: 0x99, 最大相关系数: 0.4845

攻击字节 10...
  最佳密钥猜测: 0xaa, 最大相关系数: 0.4483

攻击字节 11...
  最佳密钥猜测: 0xbb, 最大相关系数: 0.5096

攻击字节 12...
  最佳密钥猜测: 0xcc, 最大相关系数: 0.5398

攻击字节 13...
  最佳密钥猜测: 0xdd, 最大相关系数: 0.5285

攻击字节 14...
  最佳密钥猜测: 0xee, 最大相关系数: 0.4757

攻击字节 15...
  最佳密钥猜测: 0xff, 最大相关系数: 0.6291

============================================================
CPA攻击结果:
============================================================
字节  0: 密钥猜测 = 0x00, 最大相关系数 = 0.5860
字节  1: 密钥猜测 = 0x11, 最大相关系数 = 0.4461
字节  2: 密钥猜测 = 0x22, 最大相关系数 = 0.4446
字节  3: 密钥猜测 = 0x33, 最大相关系数 = 0.4771
字节  4: 密钥猜测 = 0x44, 最大相关系数 = 0.4802
字节  5: 密钥猜测 = 0x55, 最大相关系数 = 0.4650
字节  6: 密钥猜测 = 0x66, 最大相关系数 = 0.5083
字节  7: 密钥猜测 = 0x77, 最大相关系数 = 0.5111
字节  8: 密钥猜测 = 0x88, 最大相关系数 = 0.5063
字节  9: 密钥猜测 = 0x99, 最大相关系数 = 0.4845
字节 10: 密钥猜测 = 0xaa, 最大相关系数 = 0.4483
字节 11: 密钥猜测 = 0xbb, 最大相关系数 = 0.5096
字节 12: 密钥猜测 = 0xcc, 最大相关系数 = 0.5398
字节 13: 密钥猜测 = 0xdd, 最大相关系数 = 0.5285
字节 14: 密钥猜测 = 0xee, 最大相关系数 = 0.4757
字节 15: 密钥猜测 = 0xff, 最大相关系数 = 0.6291

恢复的密钥: 00112233445566778899aabbccddeeff
密钥字符串: b'\x00\x11"3DUfw\x88\x99\xaa
...(truncated)
```
</details>


---

### Round 5 | tokens: 19,437→610

**🤖 LLM:** 太好了！CPA攻击成功恢复了密钥：`00112233445566778899aabbccddeeff`。这是一个典型的测试密钥（从00到FF的递增序列）。让我验证这个密钥是否正确：

**🔧 → `python_jupyter`**

<details><summary>Code (1400 chars)</summary>

```python
# 验证恢复的密钥
from Crypto.Cipher import AES

# 恢复的密钥
recovered_key = bytes([0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 
                       0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff])

print("验证恢复的密钥...")
print(f"恢复的密钥: {recovered_key.hex()}")

# 使用恢复的密钥加密第一个明文，验证是否匹配对应的密文
cipher = AES.new(recovered_key, AES.MODE_ECB)

# 测试前3个明文/密文对
success_count = 0
for i in range(3):
    plain = bytes(plaintexts[i])
    expected_cipher = bytes(ciphertexts[i])
    
    # 使用恢复的密钥加密
    computed_cipher = cipher.encrypt(plain)
    
    match = computed_cipher == expected_cipher
    success_count += 1 if match else 0
    
    print(f"\n测试 {i+1}:")
    print(f"  明文: {plain.hex()}")
    print(f"  期望密文: {expected_cipher.hex()}")
    print(f"  计算密文: {computed_cipher.hex()}")
    print(f"  匹配: {'是' if match else '否'}")

print(f"\n验证结果: {success_count}/3 匹配")

# 验证所有1000条轨迹
print("\n验证所有1000条轨迹...")
all_match = True
for i in range(len(plaintexts)):
    plain = bytes(plaintexts[i])
    expected_cipher = bytes(ciphertexts[i])
    computed_cipher = cipher.encrypt(plain)
    
    if computed_cipher != expected_cipher:
        print(f"轨迹 {i} 不匹配!")
        print(f"  明文: {plain.hex()}")
        print(f"  期望密文: {expected_cipher.hex()}")
        print(f"  计算密文: {computed_cipher.hex()}")
        all_match = False
        break

if all_match:
    print("所有1000条轨迹验证成功! 密钥完全正确!")
else:
    print("密钥验证失败!")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (511 chars)</summary>

```
验证恢复的密钥...
恢复的密钥: 00112233445566778899aabbccddeeff

测试 1:
  明文: 958d9d0f39f42c8a4e6f6ac1cbf56434
  期望密文: fc1b4003e543afa97e5f7c4f94d63cb3
  计算密文: fc1b4003e543afa97e5f7c4f94d63cb3
  匹配: 是

测试 2:
  明文: 8f16fae6dd3bfc79509589f10eda44c5
  期望密文: 36c771022430a0e5c9861fed41942e85
  计算密文: 36c771022430a0e5c9861fed41942e85
  匹配: 是

测试 3:
  明文: 0c8fce0749fdc1dc1cd1b5976e2c734a
  期望密文: ec6cf1a8c0ded26d9214e28fcd6d44a8
  计算密文: ec6cf1a8c0ded26d9214e28fcd6d44a8
  匹配: 是

验证结果: 3/3 匹配

验证所有1000条轨迹...
所有1000条轨迹验证成功! 密钥完全正确!
```
</details>


---

### Round 6 | tokens: 20,384→1,217

**🤖 LLM:** 完美！密钥验证成功。现在让我可视化CPA结果，看看相关系数的分布：

**🔧 → `python_jupyter`**

<details><summary>Code (3184 chars)</summary>

```python
# 可视化CPA结果
import matplotlib.pyplot as plt

# 创建子图
fig, axes = plt.subplots(4, 4, figsize=(20, 16))
axes = axes.flatten()

for byte_idx in range(16):
    ax = axes[byte_idx]
    correlations = all_correlations[byte_idx]
    
    # 找到最佳密钥猜测的相关系数轨迹
    best_key = best_keys[byte_idx]
    best_corr_trace = correlations[best_key, :]
    
    # 找到第二佳密钥猜测
    all_max_corrs = np.max(np.abs(correlations), axis=1)
    sorted_keys = np.argsort(all_max_corrs)[::-1]
    second_best_key = sorted_keys[1] if len(sorted_keys) > 1 else 0
    second_best_corr_trace = correlations[second_best_key, :]
    
    # 绘制
    ax.plot(best_corr_trace, 'b-', linewidth=1, label=f'最佳密钥 0x{best_key:02x}')
    ax.plot(second_best_corr_trace, 'r--', linewidth=0.5, alpha=0.7, label=f'第二佳 0x{second_best_key:02x}')
    
    # 标记最大相关系数点
    max_corr_idx = np.argmax(np.abs(best_corr_trace))
    max_corr_val = best_corr_trace[max_corr_idx]
    ax.plot(max_corr_idx, max_corr_val, 'go', markersize=8, markeredgecolor='k')
    
    ax.set_title(f'字节 {byte_idx}: 密钥=0x{best_key:02x}, 最大相关系数={best_correlations[byte_idx]:.4f}')
    ax.set_xlabel('采样点')
    ax.set_ylabel('相关系数')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=8)
    
    # 设置y轴范围
    ax.set_ylim([-0.7, 0.7])

plt.tight_layout()
plt.savefig('cpa_results_all_bytes.png', dpi=150, bbox_inches='tight')
plt.show()

# 绘制密钥字节的相关系数热图
plt.figure(figsize=(15, 8))

# 对于每个字节，显示所有密钥猜测的相关系数
for byte_idx in range(4):  # 只显示前4个字节以节省空间
    plt.subplot(2, 2, byte_idx + 1)
    
    correlations = all_correlations[byte_idx]
    # 找到每个采样点的最大相关系数
    max_corrs_per_sample = np.max(np.abs(correlations), axis=0)
    
    plt.plot(max_corrs_per_sample, 'b-', linewidth=1)
    plt.title(f'字节 {byte_idx}: 所有密钥猜测的最大相关系数')
    plt.xlabel('采样点')
    plt.ylabel('最大相关系数')
    plt.grid(True, alpha=0.3)
    
    # 标记最大值
    max_idx = np.argmax(max_corrs_per_sample)
    max_val = max_corrs_per_sample[max_idx]
    plt.plot(max_idx, max_val, 'ro', markersize=8)
    plt.annotate(f'{max_val:.3f}', xy=(max_idx, max_val), xytext=(max_idx+50, max_val),
                 arrowprops=dict(arrowstyle='->', color='red'))

plt.tight_layout()
plt.savefig('cpa_max_correlations.png', dpi=150, bbox_inches='tight')
plt.show()

# 分析相关系数差距
print("相关系数差距分析:")
print("="*60)
for byte_idx in range(16):
    correlations = all_correlations[byte_idx]
    
    # 计算每个密钥猜测的最大相关系数
    max_corrs = np.max(np.abs(correlations), axis=1)
    
    # 排序
    sorted_indices = np.argsort(max_corrs)[::-1]
    sorted_corrs = max_corrs[sorted_indices]
    
    best_corr = sorted_corrs[0]
    second_best_corr = sorted_corrs[1] if len(sorted_corrs) > 1 else 0
    
    gap = best_corr - second_best_corr
    gap_percent = (gap / best_corr * 100) if best_corr != 0 else 0
    
    print(f"字节 {byte_idx:2d}: 最佳={best_corr:.4f}, 第二佳={second_best_corr:.4f}, "
          f"差距={gap:.4f} ({gap_percent:.1f}%)")

# 计算整体统计
print("\n整体统计:")
avg_correlation = np.mean(best_correlations)
print(f"平均相关系数: {avg_correlation:.4f}")
print(f"最小相关系数: {min(best_correlations):.4f} (字节 {np.argmin(best_correlations)})")
print(f"最大相关系数: {max(best_correlations):.4f} (字节 {np.argmax(best_correlations)})")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (905 chars)</summary>

```
相关系数差距分析:
============================================================
字节  0: 最佳=0.5860, 第二佳=0.1806, 差距=0.4054 (69.2%)
字节  1: 最佳=0.4461, 第二佳=0.1509, 差距=0.2952 (66.2%)
字节  2: 最佳=0.4446, 第二佳=0.1607, 差距=0.2840 (63.9%)
字节  3: 最佳=0.4771, 第二佳=0.1712, 差距=0.3059 (64.1%)
字节  4: 最佳=0.4802, 第二佳=0.1778, 差距=0.3024 (63.0%)
字节  5: 最佳=0.4650, 第二佳=0.1611, 差距=0.3040 (65.4%)
字节  6: 最佳=0.5083, 第二佳=0.1693, 差距=0.3390 (66.7%)
字节  7: 最佳=0.5111, 第二佳=0.1878, 差距=0.3233 (63.3%)
字节  8: 最佳=0.5063, 第二佳=0.1512, 差距=0.3551 (70.1%)
字节  9: 最佳=0.4845, 第二佳=0.1536, 差距=0.3309 (68.3%)
字节 10: 最佳=0.4483, 第二佳=0.1580, 差距=0.2903 (64.8%)
字节 11: 最佳=0.5096, 第二佳=0.1707, 差距=0.3389 (66.5%)
字节 12: 最佳=0.5398, 第二佳=0.1819, 差距=0.3578 (66.3%)
字节 13: 最佳=0.5285, 第二佳=0.1632, 差距=0.3654 (69.1%)
字节 14: 最佳=0.4757, 第二佳=0.1584, 差距=0.3173 (66.7%)
字节 15: 最佳=0.6291, 第二佳=0.1580, 差距=0.4711 (74.9%)

整体统计:
平均相关系数: 0.5025
最小相关系数: 0.4446 (字节 2)
最大相关系数: 0.6291 (字节 15)
```
</details>


---

### Round 7 | tokens: 22,195→78

**🤖 LLM:** 现在让我检查一下KG中关于STM32F429和CPA的相关知识，看看是否有其他建议：

**🔧 → `kg_search`** `{
  "keywords": [
    "STM32F429",
    "CPA",
    "EM",
    "software implementation"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (36154 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (4): STM32F429, CPA, EM, software implementation

**Summary**: 22 upper entities, 20 relationships, 16 diagnostic chains, 11 strategies


## 1. Upper Layer Entities (22)


### DeviceClass (4)

- **STM32F429** — category=MCU, bus_width=32
- **32-bit implementation** — bus_width=32
- **ASIC implementation of PicoRV32 on Saidoyoki board** — category=ASIC
- **Software implementation (CHES Challenge 2020)** — category=MCU

### Pipeline (10)

- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=the
...(truncated)
```
</details>


---

### Round 8 | tokens: 31,199→1,157

**🤖 LLM:** 根据KG知识，我的攻击策略是正确的。现在让我创建一个总结报告，并保存所有重要结果：

**🔧 → `python_jupyter`**

<details><summary>Code (3667 chars)</summary>

```python
# 创建总结报告
import json
from datetime import datetime

# 收集攻击结果
attack_results = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "target_device": "STM32F429 MCU",
    "algorithm": "AES-128",
    "side_channel": "EM (Electromagnetic)",
    "trace_count": len(traces),
    "samples_per_trace": traces.shape[1],
    "preprocessing": {
        "filtering": "Moving average (window=3)",
        "alignment": "Not needed (traces already aligned)",
        "vertical_alignment": "Not applied (software implementation)"
    },
    "attack_parameters": {
        "attack_point": "First round S-box output",
        "leakage_model": "Hamming Weight (HW)",
        "method": "CPA (Correlation Power Analysis)"
    },
    "recovered_key": recovered_key.hex(),
    "verification": {
        "all_traces_match": True,
        "matched_count": len(plaintexts),
        "total_count": len(plaintexts)
    },
    "correlation_statistics": {
        "average_correlation": float(np.mean(best_correlations)),
        "min_correlation": float(min(best_correlations)),
        "max_correlation": float(max(best_correlations)),
        "byte_correlations": [float(corr) for corr in best_correlations]
    },
    "gap_analysis": {
        "average_gap_percent": float(np.mean([(best_correlations[i] - np.sort(np.max(np.abs(all_correlations[i]), axis=1))[-2]) / best_correlations[i] * 100 
                                             for i in range(16) if len(np.max(np.abs(all_correlations[i]), axis=1)) > 1]))
    }
}

# 保存结果到JSON文件
with open('cpa_attack_results.json', 'w', encoding='utf-8') as f:
    json.dump(attack_results, f, indent=2, ensure_ascii=False)

print("="*80)
print("CPA攻击总结报告")
print("="*80)
print(f"目标设备: {attack_results['target_device']}")
print(f"算法: {attack_results['algorithm']}")
print(f"侧信道类型: {attack_results['side_channel']}")
print(f"轨迹数量: {attack_results['trace_count']}")
print(f"每轨迹采样点数: {attack_results['samples_per_trace']}")
print()
print("预处理:")
print(f"  滤波: {attack_results['preprocessing']['filtering']}")
print(f"  对齐: {attack_results['preprocessing']['alignment']}")
print(f"  垂直对齐: {attack_results['preprocessing']['vertical_alignment']}")
print()
print("攻击参数:")
print(f"  攻击点: {attack_results['attack_parameters']['attack_point']}")
print(f"  泄漏模型: {attack_results['attack_parameters']['leakage_model']}")
print(f"  方法: {attack_results['attack_parameters']['method']}")
print()
print(f"恢复的密钥: {attack_results['recovered_key']}")
print()
print("验证结果:")
print(f"  所有轨迹匹配: {attack_results['verification']['all_traces_match']}")
print(f"  匹配数量: {attack_results['verification']['matched_count']}/{attack_results['verification']['total_count']}")
print()
print("相关系数统计:")
print(f"  平均相关系数: {attack_results['correlation_statistics']['average_correlation']:.4f}")
print(f"  最小相关系数: {attack_results['correlation_statistics']['min_correlation']:.4f}")
print(f"  最大相关系数: {attack_results['correlation_statistics']['max_correlation']:.4f}")
print()
print("根据KG知识应用的最佳实践:")
print("1. 软件实现使用S-box输出 + 汉明重量模型 ✓")
print("2. 软件实现不需要垂直对齐 ✓")
print("3. 使用轻量滤波(窗口大小3) ✓")
print("4. 轨迹已对齐，无需额外对齐 ✓")
print("5. 验证所有轨迹确保密钥正确 ✓")
print()
print("攻击成功! 密钥已完全恢复。")
print("="*80)

# 保存密钥到文件
with open('recovered_key.txt', 'w') as f:
    f.write(f"Recovered AES-128 Key: {recovered_key.hex()}\n")
    f.write(f"Key bytes: {list(recovered_key)}\n")
    f.write(f"Verification: All {len(plaintexts)} traces matched\n")

print(f"结果已保存到文件:")
print(f"  - cpa_attack_results.json")
print(f"  - recovered_key.txt")
print(f"  - waveform_analysis.png")
print(f"  - filtering_effects.png")
print(f"  - cpa_results_all_bytes.png")
print(f"  - cpa_max_correlations.png")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1013 chars)</summary>

```
================================================================================
CPA攻击总结报告
================================================================================
目标设备: STM32F429 MCU
算法: AES-128
侧信道类型: EM (Electromagnetic)
轨迹数量: 1000
每轨迹采样点数: 1000

预处理:
  滤波: Moving average (window=3)
  对齐: Not needed (traces already aligned)
  垂直对齐: Not applied (software implementation)

攻击参数:
  攻击点: First round S-box output
  泄漏模型: Hamming Weight (HW)
  方法: CPA (Correlation Power Analysis)

恢复的密钥: 00112233445566778899aabbccddeeff

验证结果:
  所有轨迹匹配: True
  匹配数量: 1000/1000

相关系数统计:
  平均相关系数: 0.5025
  最小相关系数: 0.4446
  最大相关系数: 0.6291

根据KG知识应用的最佳实践:
1. 软件实现使用S-box输出 + 汉明重量模型 ✓
2. 软件实现不需要垂直对齐 ✓
3. 使用轻量滤波(窗口大小3) ✓
4. 轨迹已对齐，无需额外对齐 ✓
5. 验证所有轨迹确保密钥正确 ✓

攻击成功! 密钥已完全恢复。
================================================================================
结果已保存到文件:
  - cpa_attack_results.json
  - recovered_key.txt
  - waveform_analysis.png
  - filtering_effects.png
  - cpa_results_all_bytes.png
  - cpa_max_correlations.png
```
</details>


---

### Round 9 | tokens: 32,705→440

<details><summary><b>🤖 LLM Reasoning</b> (824 chars)</summary>

## 总结

我已经成功对STM32F429 MCU软件实现的AES算法进行了CPA密钥恢复攻击。以下是关键结果：

### 攻击结果
- **恢复的AES-128密钥**: `00112233445566778899aabbccddeeff`
- **验证结果**: 所有1000条轨迹验证成功，密钥完全正确
- **攻击成功率**: 100%

### 技术细节
1. **目标设备**: STM32F429 MCU (32位微控制器)
2. **侧信道类型**: 电磁侧信道(EM)
3. **数据规模**: 1000条轨迹，每条1000个采样点
4. **攻击点**: AES第一轮S-box输出
5. **泄漏模型**: 汉明重量(Hamming Weight)模型
6. **预处理**: 移动平均滤波(窗口大小3)，无需对齐

### 相关系数分析
- 平均相关系数: 0.5025
- 最小相关系数: 0.4446 (字节2)
- 最大相关系数: 0.6291 (字节15)
- 相关系数差距: 63-75%，表明攻击非常可靠

### 根据KG知识应用的最佳实践
1. ✅ 软件实现使用S-box输出 + 汉明重量模型
2. ✅ 软件实现不需要垂直对齐
3. ✅ 使用轻量滤波(窗口大小2-3)
4. ✅ 轨迹已对齐，无需额外对齐
5. ✅ 验证所有轨迹确保密钥正确

### 文件输出
所有结果已保存到当前目录，包括：
- `cpa_attack_results.json` - 详细的攻击结果
- `recovered_key.txt` - 恢复的密钥
- 多个PNG图像文件 - 波形分析和CPA结果可视化

这次攻击展示了CPA在电磁侧信道分析中的有效性，特别是针对STM32F429这类32位MCU的软件AES实现。攻击成功的关键是正确选择了攻击点(S-box输出)和泄漏模型(汉明重量)，这与KG知识中的建议完全一致。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 13,359 | 642 | 14,001 |
| 2 | 14,295 | 723 | 15,018 |
| 3 | 15,096 | 830 | 15,926 |
| 4 | 16,153 | 2,389 | 18,542 |
| 5 | 19,437 | 610 | 20,047 |
| 6 | 20,384 | 1,217 | 21,601 |
| 7 | 22,195 | 78 | 22,273 |
| 8 | 31,199 | 1,157 | 32,356 |
| 9 | 32,705 | 440 | 33,145 |
| **Total** | **184,823** | **8,086** | **192,909** |

## 8. Final Output

## 总结

我已经成功对STM32F429 MCU软件实现的AES算法进行了CPA密钥恢复攻击。以下是关键结果：

### 攻击结果
- **恢复的AES-128密钥**: `00112233445566778899aabbccddeeff`
- **验证结果**: 所有1000条轨迹验证成功，密钥完全正确
- **攻击成功率**: 100%

### 技术细节
1. **目标设备**: STM32F429 MCU (32位微控制器)
2. **侧信道类型**: 电磁侧信道(EM)
3. **数据规模**: 1000条轨迹，每条1000个采样点
4. **攻击点**: AES第一轮S-box输出
5. **泄漏模型**: 汉明重量(Hamming Weight)模型
6. **预处理**: 移动平均滤波(窗口大小3)，无需对齐

### 相关系数分析
- 平均相关系数: 0.5025
- 最小相关系数: 0.4446 (字节2)
- 最大相关系数: 0.6291 (字节15)
- 相关系数差距: 63-75%，表明攻击非常可靠

### 根据KG知识应用的最佳实践
1. ✅ 软件实现使用S-box输出 + 汉明重量模型
2. ✅ 软件实现不需要垂直对齐
3. ✅ 使用轻量滤波(窗口大小2-3)
4. ✅ 轨迹已对齐，无需额外对齐
5. ✅ 验证所有轨迹确保密钥正确

### 文件输出
所有结果已保存到当前目录，包括：
- `cpa_attack_results.json` - 详细的攻击结果
- `recovered_key.txt` - 恢复的密钥
- 多个PNG图像文件 - 波形分析和CPA结果可视化

这次攻击展示了CPA在电磁侧信道分析中的有效性，特别是针对STM32F429这类32位MCU的软件AES实现。攻击成功的关键是正确选择了攻击点(S-box输出)和泄漏模型(汉明重量)，这与KG知识中的建议完全一致。
