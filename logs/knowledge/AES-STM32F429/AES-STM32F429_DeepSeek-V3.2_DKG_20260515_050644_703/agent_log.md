# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260515_050644_703 |
| Duration | 566.0s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp_knowledge_only\AES-STM32F429_DeepSeek-V3.2_DKG_20260515_050644_703` |
| Total LLM Calls | 10 |
| First Round | prompt: 13,359, completion: 658 |
| Last Round | prompt: 42,860, completion: 525 |
| Total Tokens | 271,080 (prompt: 262,430, completion: 8,650) |

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
All files for this session are stored in: ..\logs\exp_knowledge_only\AES-STM32F429_DeepSeek-V3.2_DKG_20260515_050644_703
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp_knowledge_only\AES-STM32F429_DeepSeek-V3.2_DKG_20260515_050644_703/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 13,359→658

**🤖 LLM:** 我来帮您对STM32F429 MCU软件实现的AES算法进行CPA密钥恢复。首先，我将加载数据并分析波形特征。

**🔧 → `python_jupyter`**

<details><summary>Code (1438 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
plain_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy'
cipher_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy'
wave_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy'

print("正在加载数据...")
plaintexts = np.load(plain_path)
ciphertexts = np.load(cipher_path)
traces = np.load(wave_path)

print(f"明文数据形状: {plaintexts.shape}")
print(f"密文数据形状: {ciphertexts.shape}")
print(f"波形数据形状: {traces.shape}")

# 检查数据基本信息
print(f"\n明文数据类型: {plaintexts.dtype}")
print(f"密文数据类型: {ciphertexts.dtype}")
print(f"波形数据类型: {traces.dtype}")

# 查看前几个明文和密文
print(f"\n前3个明文 (十六进制):")
for i in range(min(3, len(plaintexts))):
    print(f"  {i}: {plaintexts[i].tobytes().hex()}")
    
print(f"\n前3个密文 (十六进制):")
for i in range(min(3, len(ciphertexts))):
    print(f"  {i}: {ciphertexts[i].tobytes().hex()}")

# 查看波形统计信息
print(f"\n波形统计信息:")
print(f"  最小值: {traces.min():.4f}")
print(f"  最大值: {traces.max():.4f}")
print(f"  平均值: {traces.mean():.4f}")
print(f"  标准差: {traces.std():.4f}")
```
</details>

**📋 ← `python_jupyter`:** `正在加载数据...
明文数据形状: (1000, 16)
密文数据形状: (1000, 16)
波形数据形状: (1000, 1000)

明文数据类型: uint8
密文数据类型: uint8
波形数据类型: float32

前3个明文 (十六进制):
  0: 958d9d0f39f42c8a4e6f6ac1cbf56434
  1: 8f16fae6dd3bfc79509589f10eda44c5
  2: 0c8fce0749fdc1dc1cd1b5976e2c734a

前3个密文 (十六进制):
  0: fc1b4003e543afa97e5f7c4f94d63cb3
  1: 36c771022430a0e5c9861fed41942e85
  2: ec6cf1a8c0ded26d9214e28fcd6d44a8

波形统计信息:
  最小值: 0.0000
  最大值: 125000.0000
  平均值: 25611.7031
  标准差: 16987.9805`


---

### Round 2 | tokens: 14,303→833

**🤖 LLM:** 数据已成功加载。我们有1000条轨迹，每条1000个采样点，明文和密文都是16字节（128位）。现在让我可视化一些波形，了解其特性。

**🔧 → `python_jupyter`**

<details><summary>Code (2108 chars)</summary>

```python
# 可视化前几条波形
fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

for i in range(3):
    axes[i].plot(traces[i], linewidth=0.8)
    axes[i].set_ylabel(f'轨迹 {i}')
    axes[i].grid(True, alpha=0.3)
    
axes[2].set_xlabel('采样点')
axes[0].set_title('前3条EM波形轨迹')
plt.tight_layout()
plt.savefig('raw_traces.png', dpi=150, bbox_inches='tight')
plt.show()

# 查看所有轨迹的平均波形
mean_trace = traces.mean(axis=0)
std_trace = traces.std(axis=0)

fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
axes[0].plot(mean_trace, linewidth=1.2, color='blue', label='平均波形')
axes[0].fill_between(range(len(mean_trace)), 
                     mean_trace - std_trace, 
                     mean_trace + std_trace, 
                     alpha=0.3, color='blue', label='±1标准差')
axes[0].set_ylabel('幅值')
axes[0].set_title('平均波形和标准差')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 计算方差
variance_trace = np.var(traces, axis=0)
axes[1].plot(variance_trace, linewidth=1.2, color='red')
axes[1].set_xlabel('采样点')
axes[1].set_ylabel('方差')
axes[1].set_title('波形方差')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('mean_variance_traces.png', dpi=150, bbox_inches='tight')
plt.show()

# 找出方差最大的区域（可能的加密操作区域）
variance_threshold = variance_trace.max() * 0.1  # 最大方差的10%作为阈值
high_variance_indices = np.where(variance_trace > variance_threshold)[0]

if len(high_variance_indices) > 0:
    print(f"高方差区域（阈值={variance_threshold:.2f}）：")
    print(f"  起始点: {high_variance_indices[0]}")
    print(f"  结束点: {high_variance_indices[-1]}")
    print(f"  长度: {len(high_variance_indices)} 个采样点")
    
    # 找出连续的高方差区域
    diff = np.diff(high_variance_indices)
    breaks = np.where(diff > 1)[0]
    
    regions = []
    start = high_variance_indices[0]
    for break_idx in breaks:
        end = high_variance_indices[break_idx]
        regions.append((start, end))
        start = high_variance_indices[break_idx + 1]
    regions.append((start, high_variance_indices[-1]))
    
    print(f"\n连续高方差区域:")
    for i, (s, e) in enumerate(regions):
        print(f"  区域{i+1}: [{s}, {e}], 长度={e-s+1}")
else:
    print("未找到明显的高方差区域")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (2147 chars)</summary>

```
高方差区域（阈值=100772728.00）：
  起始点: 0
  结束点: 999
  长度: 799 个采样点

连续高方差区域:
  区域1: [0, 12], 长度=13
  区域2: [14, 15], 长度=2
  区域3: [17, 18], 长度=2
  区域4: [21, 21], 长度=1
  区域5: [23, 23], 长度=1
  区域6: [25, 25], 长度=1
  区域7: [27, 27], 长度=1
  区域8: [31, 46], 长度=16
  区域9: [48, 48], 长度=1
  区域10: [50, 68], 长度=19
  区域11: [71, 87], 长度=17
  区域12: [89, 89], 长度=1
  区域13: [91, 107], 长度=17
  区域14: [109, 109], 长度=1
  区域15: [111, 127], 长度=17
  区域16: [129, 129], 长度=1
  区域17: [131, 149], 长度=19
  区域18: [152, 170], 长度=19
  区域19: [172, 189], 长度=18
  区域20: [191, 193], 长度=3
  区域21: [195, 197], 长度=3
  区域22: [207, 207], 长度=1
  区域23: [210, 210], 长度=1
  区域24: [220, 220], 长度=1
  区域25: [222, 223], 长度=2
  区域26: [232, 234], 长度=3
  区域27: [246, 252], 长度=7
  区域28: [254, 255], 长度=2
  区域29: [259, 259], 长度=1
  区域30: [261, 262], 长度=2
  区域31: [264, 264], 长度=1
  区域32: [272, 279], 长度=8
  区域33: [281, 287], 长度=7
  区域34: [289, 295], 长度=7
  区域35: [297, 303], 长度=7
  区域36: [305, 305], 长度=1
  区域37: [307, 308], 长度=2
  区域38: [312, 331], 长度=20
  区域39: [333, 339], 长度=7
  区域40: [341, 342], 长度=2
  区域41: [346, 347], 长度=2
  区域42: [349, 356], 长度=8
  区域43: [358, 361], 长度=4
  区域44: [364, 371], 长度=8
  区域45: [374, 375], 长度=2
  区域46: [377, 377], 长度=1
  区域47: [379, 382], 长度=4
  区域48: [385, 390], 长度=6
  区域49: [396, 407], 长度=12
  区域50: [412, 416], 长度=5
  区域51: [418, 424], 长度=7
  区域52: [428, 433], 长度=6
  区域53: [436, 448], 长度=13
  区域54: [455, 455], 长度=1
  区域55: [457, 465], 长度=9
  区域56: [472, 488], 长度=17
  区域57: [493, 509], 长度=17
  区域58: [512, 529], 长度=18
 
...(truncated)
```
</details>


---

### Round 3 | tokens: 16,439→664

**🤖 LLM:** 从方差分析来看，波形中有很多高方差区域。让我检查一下是否需要对齐。首先，根据KG知识，对于STM32F429这样的软件实现，通常不需要垂直对齐，但可能需要静态对齐。让我先检查波形是否已经对齐。

**🔧 → `python_jupyter`**

<details><summary>Code (1487 chars)</summary>

```python
# 检查波形是否需要对齐 - 查看前几条轨迹的起始部分
fig, axes = plt.subplots(5, 1, figsize=(12, 10), sharex=True)

# 查看前50个采样点
for i in range(5):
    axes[i].plot(traces[i, :100], linewidth=1.2)
    axes[i].set_ylabel(f'轨迹 {i}')
    axes[i].grid(True, alpha=0.3)
    
axes[4].set_xlabel('采样点 (0-99)')
axes[0].set_title('前5条轨迹的前100个采样点（检查对齐情况）')
plt.tight_layout()
plt.savefig('alignment_check.png', dpi=150, bbox_inches='tight')
plt.show()

# 计算轨迹间的互相关，检查偏移
def cross_correlation(trace1, trace2, max_lag=100):
    """计算两条轨迹的互相关"""
    corr = signal.correlate(trace1, trace2, mode='full')
    lags = signal.correlation_lags(len(trace1), len(trace2), mode='full')
    
    # 只保留中心附近的lags
    center_idx = len(lags) // 2
    start_idx = center_idx - max_lag
    end_idx = center_idx + max_lag + 1
    
    return corr[start_idx:end_idx], lags[start_idx:end_idx]

# 计算第一条轨迹与其他轨迹的互相关
print("计算轨迹间的互相关偏移...")
ref_trace = traces[0]
max_lag = 50

offsets = []
for i in range(1, min(10, len(traces))):  # 检查前10条轨迹
    corr, lags = cross_correlation(ref_trace, traces[i], max_lag)
    max_corr_idx = np.argmax(np.abs(corr))
    offset = lags[max_corr_idx]
    offsets.append(offset)
    print(f"  轨迹{i}相对于轨迹0的偏移: {offset}")

if len(offsets) > 0:
    print(f"\n偏移统计:")
    print(f"  平均偏移: {np.mean(offsets):.2f}")
    print(f"  标准差: {np.std(offsets):.2f}")
    print(f"  最大偏移: {np.max(np.abs(offsets))}")
    
    if np.max(np.abs(offsets)) > 5:
        print("⚠️ 检测到显著偏移，可能需要对齐")
    else:
        print("✓ 偏移较小，可能不需要对齐")
```
</details>

**📋 ← `python_jupyter`:** `计算轨迹间的互相关偏移...
  轨迹1相对于轨迹0的偏移: 0
  轨迹2相对于轨迹0的偏移: -3
  轨迹3相对于轨迹0的偏移: -40
  轨迹4相对于轨迹0的偏移: -40
  轨迹5相对于轨迹0的偏移: -4
  轨迹6相对于轨迹0的偏移: -40
  轨迹7相对于轨迹0的偏移: -9
  轨迹8相对于轨迹0的偏移: 0
  轨迹9相对于轨迹0的偏移: -9

偏移统计:
  平均偏移: -16.11
  标准差: 17.16
  最大偏移: 40
⚠️ 检测到显著偏移，可能需要对齐`


---

### Round 4 | tokens: 17,271→96

**🤖 LLM:** 检测到显著的偏移（最大40个采样点），需要进行对齐。根据KG知识，对于软件实现，我应该使用静态对齐。让我先搜索一下关于对齐的最佳实践。

**🔧 → `kg_search`** `{
  "keywords": [
    "static alignment",
    "STM32F429",
    "AES",
    "max_shift"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (33030 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (4): static alignment, STM32F429, AES, max_shift

**Summary**: 11 upper entities, 15 relationships, 15 diagnostic chains, 13 strategies


## 1. Upper Layer Entities (11)


### Algorithm (1)

- **AES** — num_rounds=['10', '14'], encryption_mode=['CBC', 'ECB'], key_length=['128', '256']

### DeviceClass (4)

- **STM32F429** — category=MCU, bus_width=32
- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated

### Pipeline (4)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Fra
...(truncated)
```
</details>


---

### Round 5 | tokens: 26,058→3,031

**🤖 LLM:** 根据KG知识，我需要先进行方差分析来定位加密区域，然后进行静态对齐。让我先实现一个静态对齐函数，然后进行CPA攻击。

**🔧 → `python_jupyter`**

<details><summary>Code (7289 chars)</summary>

```python
# 实现静态对齐函数
def static_align(traces, ref_idx=1, length=100, max_shift=200, threshold=0.85):
    """
    静态对齐函数
    traces: 原始轨迹 (n_traces, n_samples)
    ref_idx: 参考轨迹索引
    length: 对齐窗口长度
    max_shift: 最大偏移量
    threshold: 相似度阈值
    """
    n_traces, n_samples = traces.shape
    
    # 选择参考轨迹和参考窗口
    ref_trace = traces[ref_idx]
    
    # 找到参考轨迹中方差最大的区域作为对齐窗口
    # 使用滑动窗口计算方差
    window_variances = []
    for i in range(n_samples - length):
        window = ref_trace[i:i+length]
        window_variances.append(np.var(window))
    
    # 找到方差最大的窗口起始位置
    ref_start = np.argmax(window_variances)
    ref_window = ref_trace[ref_start:ref_start+length]
    
    print(f"参考窗口: 起始点={ref_start}, 长度={length}, 方差={np.max(window_variances):.2f}")
    
    # 对齐所有轨迹
    aligned_traces = np.zeros_like(traces)
    accepted_count = 0
    
    for i in range(n_traces):
        if i == ref_idx:
            # 参考轨迹直接复制
            aligned_traces[i] = traces[i]
            accepted_count += 1
            continue
            
        trace = traces[i]
        best_corr = -1
        best_shift = 0
        
        # 在[-max_shift, max_shift]范围内搜索最佳匹配
        for shift in range(-max_shift, max_shift+1):
            start = ref_start + shift
            if start < 0 or start + length > n_samples:
                continue
                
            window = trace[start:start+length]
            
            # 计算相关系数
            corr = np.corrcoef(ref_window, window)[0, 1]
            if corr > best_corr:
                best_corr = corr
                best_shift = shift
        
        # 检查是否达到阈值
        if best_corr >= threshold:
            # 应用偏移
            if best_shift >= 0:
                aligned_traces[i, best_shift:] = traces[i, :-best_shift] if best_shift > 0 else traces[i]
            else:
                aligned_traces[i, :best_shift] = traces[i, -best_shift:]
            accepted_count += 1
        else:
            # 未达到阈值，使用原始轨迹
            aligned_traces[i] = traces[i]
    
    acceptance_rate = accepted_count / n_traces * 100
    print(f"对齐结果: 接受率={acceptance_rate:.1f}% ({accepted_count}/{n_traces})")
    
    return aligned_traces, acceptance_rate

# 首先尝试直接CPA（不对齐）来评估是否需要对齐
print("首先尝试直接CPA（不对齐）...")

# 实现CPA函数
def cpa_attack(traces, plaintexts, target_byte=0, model='HW', leakage_point='sbox_out'):
    """
    对单个字节进行CPA攻击
    """
    n_traces, n_samples = traces.shape
    n_plaintexts = len(plaintexts)
    
    # 确保轨迹和明文数量匹配
    assert n_traces == n_plaintexts, f"轨迹数量({n_traces})和明文数量({n_plaintexts})不匹配"
    
    # 生成假设值矩阵 (256个密钥假设 × n_traces)
    hypotheses = np.zeros((256, n_traces), dtype=np.uint8)
    
    for k in range(256):
        for i in range(n_traces):
            if target_byte < len(plaintexts[i]):
                pt_byte = plaintexts[i][target_byte]
                
                if leakage_point == 'sbox_out':
                    # S-box输出: Sbox[pt_byte ^ k]
                    from Crypto.Cipher import AES
                    # 使用标准AES S-box
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
                    hypotheses[k, i] = sbox[pt_byte ^ k]
                elif leakage_point == 'sbox_in':
                    # S-box输入: pt_byte ^ k
                    hypotheses[k, i] = pt_byte ^ k
                else:
                    raise ValueError(f"未知泄漏点: {leakage_point}")
    
    # 根据模型计算预测值
    if model == 'HW':
        # 汉明重量模型
        predictions = np.zeros((256, n_traces))
        for k in range(256):
            predictions[k] = np.array([bin(h).count('1') for h in hypotheses[k]])
    elif model == 'identity':
        # 恒等模型
        predictions = hypotheses.astype(float)
    else:
        raise ValueError(f"未知模型: {model}")
    
    # 计算相关系数矩阵 (256个假设 × n_samples)
    correlations = np.zeros((256, n_samples))
    
    for k in range(256):
        pred = predictions[k]
        pred_mean = np.mean(pred)
        pred_std = np.std(pred)
        
        if pred_std == 0:
            continue
            
        for s in range(n_samples):
            trace_slice = traces[:, s]
            trace_mean = np.mean(trace_slice)
            trace_std = np.std(trace_slice)
            
            if trace_std == 0:
                continue
                
            # 计算Pearson相关系数
            cov = np.mean((pred - pred_mean) * (trace_slice - trace_mean))
            correlations[k, s] = cov / (pred_std * trace_std)
    
    # 找到最佳密钥假设
    max_corr_per_key = np.max(np.abs(correlations), axis=1)
    best_key = np.argmax(max_corr_per_key)
    best_correlation = max_corr_per_key[best_key]
    
    # 计算gap（最佳与次佳的相关性差异）
    sorted_indices = np.argsort(max_corr_per_key)[::-1]
    if len(sorted_indices) > 1:
        gap = max_corr_per_key[sorted_indices[0]] - max_corr_per_key[sorted_indices[1]]
    else:
        gap = 0
    
    return {
        'best_key': best_key,
        'best_correlation': best_correlation,
        'gap': gap,
        'correlations': correlations,
        'max_corr_per_key': max_corr_per_key
    }

# 对第一个字节进行直接CPA测试
print("对第一个字节进行直接CPA测试...")
result = cpa_attack(traces, plaintexts, target_byte=0, model='HW', leakage_point='sbox_out')
print(f"字节0的最佳密钥: 0x{result['best_key']:02x}")
print(f"最大相关系数: {result['best_correlation']:.4f}")
print(f"Gap: {result['gap']:.4f}")

# 检查是否需要对齐（根据KG策略）
# AES的高置信度阈值：≥13/16跳过对齐，10-12进入对齐，<10必须对齐
# 我们先测试几个字节看看
```
</details>

**📋 ← `python_jupyter`:** `首先尝试直接CPA（不对齐）...
对第一个字节进行直接CPA测试...
字节0的最佳密钥: 0x00
最大相关系数: 0.4463
Gap: 0.2917`


---

### Round 6 | tokens: 29,151→750

**🤖 LLM:** 第一个字节的CPA结果显示相关系数为0.4463，gap为0.2917，看起来不错。但根据KG策略，我需要测试更多字节来确定是否需要对齐。让我测试所有16个字节。

**🔧 → `python_jupyter`**

<details><summary>Code (1700 chars)</summary>

```python
# 测试所有16个字节的直接CPA结果
print("测试所有16个字节的直接CPA结果...")
direct_results = []
high_confidence_count = 0
threshold_gap = 0.05  # gap阈值

for byte_idx in range(16):
    result = cpa_attack(traces, plaintexts, target_byte=byte_idx, model='HW', leakage_point='sbox_out')
    direct_results.append(result)
    
    # 检查是否为高置信度（gap > 阈值）
    if result['gap'] > threshold_gap:
        high_confidence_count += 1
    
    print(f"字节{byte_idx:2d}: 最佳密钥=0x{result['best_key']:02x}, 相关系数={result['best_correlation']:.4f}, gap={result['gap']:.4f}")

print(f"\n高置信度字节数: {high_confidence_count}/16")
print(f"高置信度比例: {high_confidence_count/16*100:.1f}%")

# 根据KG策略决定是否需要对齐
# AES: ≥13/16跳过对齐，10-12进入对齐，<10必须对齐
if high_confidence_count >= 13:
    print("✓ 高置信度字节数≥13，可以跳过对齐")
elif high_confidence_count >= 10:
    print("⚠ 高置信度字节数10-12，建议进行对齐")
else:
    print("✗ 高置信度字节数<10，必须进行对齐")

# 可视化第一个字节的CPA结果
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# 显示所有密钥假设的相关性
axes[0].plot(direct_results[0]['max_corr_per_key'], 'o-', markersize=3, linewidth=0.8)
axes[0].axvline(x=direct_results[0]['best_key'], color='red', linestyle='--', alpha=0.7, label=f'最佳密钥: 0x{direct_results[0]["best_key"]:02x}')
axes[0].set_xlabel('密钥假设 (0-255)')
axes[0].set_ylabel('最大相关系数')
axes[0].set_title(f'字节0的CPA结果 - 所有密钥假设的相关性')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 显示最佳密钥假设的相关系数随时间变化
best_key = direct_results[0]['best_key']
axes[1].plot(direct_results[0]['correlations'][best_key], linewidth=0.8)
axes[1].set_xlabel('采样点')
axes[1].set_ylabel('相关系数')
axes[1].set_title(f'字节0 - 最佳密钥0x{best_key:02x}的相关系数随时间变化')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('direct_cpa_byte0.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (727 chars)</summary>

```
测试所有16个字节的直接CPA结果...
字节 0: 最佳密钥=0x00, 相关系数=0.4463, gap=0.2917
字节 1: 最佳密钥=0x11, 相关系数=0.5536, gap=0.3620
字节 2: 最佳密钥=0x22, 相关系数=0.5321, gap=0.3721
字节 3: 最佳密钥=0x33, 相关系数=0.5563, gap=0.3717
字节 4: 最佳密钥=0x44, 相关系数=0.5662, gap=0.3832
字节 5: 最佳密钥=0x55, 相关系数=0.5341, gap=0.3716
字节 6: 最佳密钥=0x66, 相关系数=0.5802, gap=0.4034
字节 7: 最佳密钥=0x77, 相关系数=0.5952, gap=0.4074
字节 8: 最佳密钥=0x88, 相关系数=0.6141, gap=0.4085
字节 9: 最佳密钥=0x99, 相关系数=0.4875, gap=0.3481
字节10: 最佳密钥=0xaa, 相关系数=0.6308, gap=0.4640
字节11: 最佳密钥=0xbb, 相关系数=0.5474, gap=0.3739
字节12: 最佳密钥=0xcc, 相关系数=0.6539, gap=0.4740
字节13: 最佳密钥=0xdd, 相关系数=0.6180, gap=0.4349
字节14: 最佳密钥=0xee, 相关系数=0.5513, gap=0.3712
字节15: 最佳密钥=0xff, 相关系数=0.5640, gap=0.4023

高置信度字节数: 16/16
高置信度比例: 100.0%
✓ 高置信度字节数≥13，可以跳过对齐
```
</details>


---

### Round 7 | tokens: 30,402→855

**🤖 LLM:** 太好了！直接CPA已经恢复了所有16个字节的密钥，看起来密钥是`0x00112233445566778899AABBCCDDEEFF`。所有字节的gap都很大（>0.05），表明高置信度。根据KG策略，高置信度字节数≥13可以跳过对齐。

现在让我验证这个密钥是否正确。根据KG的反模式策略，**绝对不能仅凭CPA内部指标就宣布成功，必须进行加密/解密验证**。

**🔧 → `python_jupyter`**

<details><summary>Code (2240 chars)</summary>

```python
# 根据KG策略：必须进行加密/解密验证
print("进行加密/解密验证...")

# 从CPA结果构建密钥
recovered_key = bytes([direct_results[i]['best_key'] for i in range(16)])
print(f"恢复的密钥: {recovered_key.hex()}")

# 使用pycryptodome进行验证
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# 测试加密验证
try:
    # 使用恢复的密钥加密第一个明文
    cipher = AES.new(recovered_key, AES.MODE_ECB)
    
    # 验证所有轨迹
    match_count = 0
    mismatch_indices = []
    
    for i in range(min(100, len(plaintexts))):  # 测试前100个
        plaintext = bytes(plaintexts[i])
        expected_ciphertext = bytes(ciphertexts[i])
        
        # 加密
        actual_ciphertext = cipher.encrypt(plaintext)
        
        if actual_ciphertext == expected_ciphertext:
            match_count += 1
        else:
            mismatch_indices.append(i)
    
    print(f"验证结果: {match_count}/{min(100, len(plaintexts))} 匹配")
    
    if match_count == min(100, len(plaintexts)):
        print("✓ 加密验证成功！恢复的密钥是正确的。")
    else:
        print(f"✗ 加密验证失败。不匹配的索引: {mismatch_indices[:10]}")  # 只显示前10个
        
        # 尝试解密验证
        print("\n尝试解密验证...")
        decrypt_match_count = 0
        for i in range(min(100, len(ciphertexts))):
            ciphertext = bytes(ciphertexts[i])
            expected_plaintext = bytes(plaintexts[i])
            
            try:
                actual_plaintext = cipher.decrypt(ciphertext)
                if actual_plaintext == expected_plaintext:
                    decrypt_match_count += 1
            except:
                pass
        
        print(f"解密验证: {decrypt_match_count}/{min(100, len(ciphertexts))} 匹配")
        
except Exception as e:
    print(f"验证过程中出现错误: {e}")

# 可视化恢复的密钥
fig, ax = plt.subplots(figsize=(12, 4))
key_bytes = list(recovered_key)
x_pos = np.arange(16)
ax.bar(x_pos, key_bytes, color='skyblue', edgecolor='black')
ax.set_xlabel('字节位置')
ax.set_ylabel('密钥值')
ax.set_title(f'恢复的AES-128密钥: {recovered_key.hex()}')
ax.set_xticks(x_pos)
ax.set_xticklabels([f'{i}' for i in range(16)])
ax.grid(True, alpha=0.3, axis='y')

# 在柱子上添加十六进制值
for i, v in enumerate(key_bytes):
    ax.text(i, v + 2, f'0x{v:02x}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('recovered_key.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `进行加密/解密验证...
恢复的密钥: 00112233445566778899aabbccddeeff
验证结果: 100/100 匹配
✓ 加密验证成功！恢复的密钥是正确的。`


---

### Round 8 | tokens: 31,319→126

**🤖 LLM:** 完美！加密验证成功，所有100个测试样本都匹配。这意味着我们成功恢复了正确的AES-128密钥：`0x00112233445566778899AABBCCDDEEFF`。

让我再搜索一下关于STM32F429 AES CPA的最佳实践，确保我们的方法符合KG建议。

**🔧 → `kg_search`** `{
  "keywords": [
    "STM32F429",
    "CPA",
    "AES",
    "software implementation",
    "Hamming Weight"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (38312 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (5): STM32F429, CPA, AES, software implementation, Hamming Weight

**Summary**: 29 upper entities, 25 relationships, 13 diagnostic chains, 11 strategies


## 1. Upper Layer Entities (29)


### Algorithm (1)

- **AES** — num_rounds=['10', '14'], encryption_mode=['CBC', 'ECB'], key_length=['128', '256']

### DeviceClass (5)

- **STM32F429** — category=MCU, bus_width=32
- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **Software implementation (CHES Challenge 2020)** — category=MCU

### LeakageModel (5)

- **Hamming Weight** — requirements=software implementation
- **Hamming Weight (bit-based)** — requirements=bit-based
- **Hamming Weight of transitions**
- **Hamming weight**
- **Hamming weight of fused features**

### Pipeline (11)

- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on 
...(truncated)
```
</details>


---

### Round 9 | tokens: 41,268→1,112

**🤖 LLM:** 很好！KG确认了我们的方法符合最佳实践。根据KG，对于STM32F429这样的软件实现：
1. 使用S-box输出作为攻击点
2. 使用汉明重量(HW)模型
3. 软件实现通常不需要垂直对齐
4. 必须进行加密/解密验证

我们的攻击完全符合这些指导原则。现在让我生成最终的报告。

**🔧 → `python_jupyter`**

<details><summary>Code (2587 chars)</summary>

```python
# 生成最终报告
print("=" * 70)
print("STM32F429 MCU AES-128 CPA攻击结果报告")
print("=" * 70)

print(f"\n📊 数据概况:")
print(f"  轨迹数量: {len(traces)}")
print(f"  采样点数/轨迹: {traces.shape[1]}")
print(f"  明文/密文数量: {len(plaintexts)}")
print(f"  侧信道类型: 电磁(EM)")

print(f"\n🎯 攻击配置 (根据KG最佳实践):")
print(f"  攻击点: S-box输出 (第一轮)")
print(f"  泄漏模型: 汉明重量(HW)")
print(f"  攻击方法: 相关性功率分析(CPA)")
print(f"  预处理: 无垂直对齐 (软件实现不需要)")

print(f"\n🔑 CPA恢复结果:")
recovered_key = bytes([direct_results[i]['best_key'] for i in range(16)])
print(f"  恢复的密钥: {recovered_key.hex()}")
print(f"  密钥格式: 0x{recovered_key.hex().upper()}")

print(f"\n📈 CPA统计指标:")
print(f"  高置信度字节数: 16/16 (100%)")
print(f"  平均相关系数: {np.mean([r['best_correlation'] for r in direct_results]):.4f}")
print(f"  平均gap值: {np.mean([r['gap'] for r in direct_results]):.4f}")
print(f"  最小gap值: {np.min([r['gap'] for r in direct_results]):.4f} (字节{np.argmin([r['gap'] for r in direct_results])})")
print(f"  最大gap值: {np.max([r['gap'] for r in direct_results]):.4f} (字节{np.argmax([r['gap'] for r in direct_results])})")

print(f"\n✅ 验证结果 (根据KG反模式策略):")
print(f"  加密验证: 100/100 匹配")
print(f"  验证状态: PASSED (MATCH)")
print(f"  结论: 密钥恢复成功！")

print(f"\n💡 关键发现:")
print(f"  1. 直接CPA成功恢复所有16个字节，无需对齐")
print(f"  2. 所有字节的gap值均大于0.05，表明高置信度")
print(f"  3. 相关系数范围: 0.4463 - 0.6539，信号质量良好")
print(f"  4. 验证通过，确认密钥正确性")

print(f"\n📁 生成的文件:")
print(f"  1. raw_traces.png - 原始波形图")
print(f"  2. mean_variance_traces.png - 平均波形和方差图")
print(f"  3. alignment_check.png - 对齐检查图")
print(f"  4. direct_cpa_byte0.png - 字节0的CPA结果图")
print(f"  5. recovered_key.png - 恢复的密钥可视化")

print(f"\n" + "=" * 70)
print("攻击完成！成功恢复AES-128密钥。")
print("=" * 70)

# 保存详细结果
import json

results = {
    "device": "STM32F429 MCU",
    "algorithm": "AES-128",
    "side_channel": "EM",
    "recovered_key": recovered_key.hex(),
    "verification": "PASSED",
    "cpa_results": {
        f"byte_{i}": {
            "best_key": int(direct_results[i]['best_key']),
            "best_correlation": float(direct_results[i]['best_correlation']),
            "gap": float(direct_results[i]['gap'])
        } for i in range(16)
    },
    "statistics": {
        "high_confidence_bytes": 16,
        "avg_correlation": float(np.mean([r['best_correlation'] for r in direct_results])),
        "avg_gap": float(np.mean([r['gap'] for r in direct_results])),
        "min_gap": float(np.min([r['gap'] for r in direct_results])),
        "max_gap": float(np.max([r['gap'] for r in direct_results]))
    }
}

with open('cpa_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n详细结果已保存到: cpa_results.json")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1131 chars)</summary>

```
======================================================================
STM32F429 MCU AES-128 CPA攻击结果报告
======================================================================

📊 数据概况:
  轨迹数量: 1000
  采样点数/轨迹: 1000
  明文/密文数量: 1000
  侧信道类型: 电磁(EM)

🎯 攻击配置 (根据KG最佳实践):
  攻击点: S-box输出 (第一轮)
  泄漏模型: 汉明重量(HW)
  攻击方法: 相关性功率分析(CPA)
  预处理: 无垂直对齐 (软件实现不需要)

🔑 CPA恢复结果:
  恢复的密钥: 00112233445566778899aabbccddeeff
  密钥格式: 0x00112233445566778899AABBCCDDEEFF

📈 CPA统计指标:
  高置信度字节数: 16/16 (100%)
  平均相关系数: 0.5644
  平均gap值: 0.3900
  最小gap值: 0.2917 (字节0)
  最大gap值: 0.4740 (字节12)

✅ 验证结果 (根据KG反模式策略):
  加密验证: 100/100 匹配
  验证状态: PASSED (MATCH)
  结论: 密钥恢复成功！

💡 关键发现:
  1. 直接CPA成功恢复所有16个字节，无需对齐
  2. 所有字节的gap值均大于0.05，表明高置信度
  3. 相关系数范围: 0.4463 - 0.6539，信号质量良好
  4. 验证通过，确认密钥正确性

📁 生成的文件:
  1. raw_traces.png - 原始波形图
  2. mean_variance_traces.png - 平均波形和方差图
  3. alignment_check.png - 对齐检查图
  4. direct_cpa_byte0.png - 字节0的CPA结果图
  5. recovered_key.png - 恢复的密钥可视化

======================================================================
攻击完成！成功恢复AES-128密钥。
======================================================================

详细结果已保存到: cpa_results.json
```
</details>


---

### Round 10 | tokens: 42,860→525

<details><summary><b>🤖 LLM Reasoning</b> (1024 chars)</summary>

## 总结

我已经成功对STM32F429 MCU软件实现的AES-128算法进行了CPA密钥恢复攻击。以下是关键成果：

### 🎯 **成功恢复的AES-128密钥**
**`0x00112233445566778899AABBCCDDEEFF`**

### 📊 **攻击详情**

1. **数据特征**：
   - 1000条电磁(EM)侧信道轨迹
   - 每条轨迹1000个采样点
   - 对应的明文和密文数据

2. **攻击配置**（遵循KG最佳实践）：
   - **攻击点**：第一轮S-box输出（最有效的泄漏点）
   - **泄漏模型**：汉明重量(HW)模型（适合软件实现）
   - **预处理**：无垂直对齐（软件实现通常不需要）

3. **CPA结果**：
   - **高置信度字节数**：16/16 (100%)
   - **平均相关系数**：0.5644
   - **平均gap值**：0.3900（所有字节gap > 0.05，表明高置信度）
   - **最佳相关系数**：0.6539（字节12）

4. **验证结果**：
   - **加密验证**：100/100匹配 ✓
   - **验证状态**：PASSED (MATCH)

### 🔍 **技术要点**

根据DKG知识图谱的指导：
1. **遵循反模式策略**：没有仅凭CPA内部指标宣布成功，而是进行了强制性的加密/解密验证
2. **软件实现最佳实践**：使用S-box输出+HW模型，避免不必要的垂直对齐
3. **高置信度处理**：所有16个字节均为高置信度，符合跳过对齐的条件（≥13/16）

### 📁 **生成的文件**
- `raw_traces.png` - 原始波形可视化
- `mean_variance_traces.png` - 平均波形和方差分析
- `alignment_check.png` - 对齐检查
- `direct_cpa_byte0.png` - 字节0的CPA详细结果
- `recovered_key.png` - 恢复的密钥可视化
- `cpa_results.json` - 详细的JSON格式结果

**结论**：CPA攻击成功恢复了STM32F429 MCU上软件实现的AES-128密钥，验证了电磁侧信道分析的有效性，并严格遵循了知识图谱中的最佳实践和反模式策略。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 13,359 | 658 | 14,017 |
| 2 | 14,303 | 833 | 15,136 |
| 3 | 16,439 | 664 | 17,103 |
| 4 | 17,271 | 96 | 17,367 |
| 5 | 26,058 | 3,031 | 29,089 |
| 6 | 29,151 | 750 | 29,901 |
| 7 | 30,402 | 855 | 31,257 |
| 8 | 31,319 | 126 | 31,445 |
| 9 | 41,268 | 1,112 | 42,380 |
| 10 | 42,860 | 525 | 43,385 |
| **Total** | **262,430** | **8,650** | **271,080** |

## 8. Final Output

## 总结

我已经成功对STM32F429 MCU软件实现的AES-128算法进行了CPA密钥恢复攻击。以下是关键成果：

### 🎯 **成功恢复的AES-128密钥**
**`0x00112233445566778899AABBCCDDEEFF`**

### 📊 **攻击详情**

1. **数据特征**：
   - 1000条电磁(EM)侧信道轨迹
   - 每条轨迹1000个采样点
   - 对应的明文和密文数据

2. **攻击配置**（遵循KG最佳实践）：
   - **攻击点**：第一轮S-box输出（最有效的泄漏点）
   - **泄漏模型**：汉明重量(HW)模型（适合软件实现）
   - **预处理**：无垂直对齐（软件实现通常不需要）

3. **CPA结果**：
   - **高置信度字节数**：16/16 (100%)
   - **平均相关系数**：0.5644
   - **平均gap值**：0.3900（所有字节gap > 0.05，表明高置信度）
   - **最佳相关系数**：0.6539（字节12）

4. **验证结果**：
   - **加密验证**：100/100匹配 ✓
   - **验证状态**：PASSED (MATCH)

### 🔍 **技术要点**

根据DKG知识图谱的指导：
1. **遵循反模式策略**：没有仅凭CPA内部指标宣布成功，而是进行了强制性的加密/解密验证
2. **软件实现最佳实践**：使用S-box输出+HW模型，避免不必要的垂直对齐
3. **高置信度处理**：所有16个字节均为高置信度，符合跳过对齐的条件（≥13/16）

### 📁 **生成的文件**
- `raw_traces.png` - 原始波形可视化
- `mean_variance_traces.png` - 平均波形和方差分析
- `alignment_check.png` - 对齐检查
- `direct_cpa_byte0.png` - 字节0的CPA详细结果
- `recovered_key.png` - 恢复的密钥可视化
- `cpa_results.json` - 详细的JSON格式结果

**结论**：CPA攻击成功恢复了STM32F429 MCU上软件实现的AES-128密钥，验证了电磁侧信道分析的有效性，并严格遵循了知识图谱中的最佳实践和反模式策略。
