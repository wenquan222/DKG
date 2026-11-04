# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_053246_934 |
| Duration | 256.5s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_053246_934` |
| Total LLM Calls | 12 |
| First Round | prompt: 17,307, completion: 970 |
| Last Round | prompt: 28,272, completion: 371 |
| Total Tokens | 286,311 (prompt: 281,286, completion: 5,025) |

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

LLM Response: ["AES", "STM32F103", "CPA", "Power", "MCU", "Software Implementation"]

Parsed Keywords: `["AES", "STM32F103", "CPA", "Power", "MCU", "Software Implementation"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 44160 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (46438 chars, click to expand)</summary>

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

**Search keywords** (6): AES, STM32F103, CPA, Power, MCU, Software Implementation

**Summary**: 34 upper entities, 25 relationships, 18 diagnostic chains, 15 strategies


## 1. Upper Layer Entities (34)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### DeviceClass (12)

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
- **Software implementation (CHES Challenge 2020)** — category=MCU

### Pipeline (15)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, canonical_source=round1_patch_002, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Correlation-based pattern matching for RDI removal** — source=expert_experience, trigger_condition=random delays exhibit regular patterns (e.g., repetitive dummy loops), applicable_scenarios=software implementations where dummy operations or AES operation blocks have distinctive and consistent leakage patterns
- **HMM cryptanalysis of RDI-protected implementations** — source=expert_experience, trigger_condition=attacking a software implementation protected with random delay insertions, applicable_scenarios=microcontroller implementations of symmetric block ciphers (e.g., AES) with random delays inserted via dummy loops or interrupts
- **HMM-based Random Delay Removal and CPA** — source=PAP-33-2013-ePrint-HMM-Remove-Random-Delays, trigger_condition=when attacking a software implementation protected with random delay insertions (RDI) via power traces, applicable_scenarios=Embedded software implementations (e.g., on 8-bit microcontrollers) using random delays as a hiding countermeasure; requires ability to profile instruction cycles on a similar device.
- **Improved Collision DL-SCA with Shared Feature Extractor and Multiple Distinguishers** — source=This work, trigger_condition=non-profiled side-channel attack on AES software implementation, applicable_scenarios=masked AES software implementations with serial Sbox computations
- **Practical Second-Order DPA Attack Strategy** — source=research_paper, trigger_condition=when performing a second-order DPA attack on a masked implementation, applicable_scenarios=masked software implementations of block ciphers, especially on 8-bit smart cards

### StatMethod (6)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Compare hypothetical power consumption with measured traces** — type=non_profiled

## 2. Relationships (25)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: XOR operation output, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `AttackPoint:XOR operation output`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use non-encryption flat region as reference, condition=when baseline drift is visible (e.g., non-contact EM, FPGA/ASIC), source_text=Vertical alignment, support_count=1]]→ `Preprocessing:Vertical alignment`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Reference peak must be inside candidate interval, set max_shift based on actual peak position variation, condition=only if first CPA falls in gray/red band (high_confidence_count below threshold), source_text=Static alignment, support_count=1]]→ `Preprocessing:Static alignment`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=If verification fails, use key_search with merged CPA details, condition=requires plaintext and ciphertext, source_text=Key verification and recovery, support_count=1]]→ `ValidationMethod:Key verification and recovery`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use conservative candidates, consider merging multiple CPA results if needed, condition=after optional alignment steps, source_text=Full CPA, support_count=1]]→ `StatMethod:Full CPA`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use conservative candidates (10-20), read gap_pct and high_confidence_count, condition=direct CPA probe to decide whether alignment is needed, source_text=First CPA probe (without alignment), support_count=1]]→ `StatMethod:First CPA probe (without alignment)`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Callback function called at reporting interval (default 25), condition=to get feedback during attack, source_text=Monitor attack progress with callback, support_count=1]]→ `DiagnosticMethod:Monitor attack progress with callback`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use output_vs_time method to plot correlation of guesses over time, condition=to locate leakage in time, source_text=Plot Output Vs. Time, support_count=1]]→ `DiagnosticMethod:Plot Output Vs. Time`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use pge_vs_trace method to plot partial guessing entropy, condition=to see attack progression, source_text=Plot PGE vs. Traces, support_count=1]]→ `DiagnosticMethod:Plot PGE vs. Traces`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use corr_vs_trace method to plot correlation values, condition=to compare correct key guess with incorrect ones, source_text=Plot Correlation vs. Traces, support_count=1]]→ `DiagnosticMethod:Plot Correlation vs. Traces`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use cpa() function with project and leakage model, source_text=Run CPA attack, support_count=1, is_optional=False]]→ `StatMethod:CPA`
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

### Obs: `trace_snr` — any
- **Cause** (high): unstable power supply introduces noise into power traces
- **Action**: use a high-quality regulated power supply, battery, or laboratory power supply
  - operation: `switch_component`
  - target: `power supply`
  - strategy: avoid powering the device from PC USB or PS/2 ports

### Obs: `trace_snr` — any
- **Cause** (high): unstable clock frequency or amplitude couples noise into power traces
- **Action**: use a sine wave clock signal from a suitable crystal oscillator or waveform generator
  - operation: `switch_component`
  - target: `clock generator`
  - strategy: prefer sine wave over square wave to reduce noise coupling

### Obs: `trace_snr` — any
- **Cause** (high): noise from connected components on the same PCB couples into the power measurement
- **Action**: minimize components on the measurement board and use optocouplers or magnetic couplers to isolate it from the interface board
  - operation: `add_step`
  - target: `measurement setup`
  - strategy: separate the measurement board (with only the target device and measurement circuit) from the interface board (handling PC communication)

### Obs: `trace_snr` — any
- **Cause** (high): low bandwidth of the connection between the device and oscilloscope filters high-frequency components, causing energy from multiple switching activities to overlap in time
- **Action**: accept that only total power per clock cycle can be measured; focus on reducing other noise sources
  - operation: `verify`
  - target: `measurement bandwidth`
  - strategy: typical measurement setups have bandwidth too low to separate individual gate transitions; switching noise corresponds to all gates switching in the same clock cycle

### Obs: `power_supply_noise` — any
- **Cause** (high): Noise on the power supply rail can couple into the measurement and obscure the subtle current variations of the cryptographic operation.
- **Action**: Add capacitors and ferrite beads on the supply side of the shunt resistor to clean the power rail.
  - operation: `add_step`
  - target: `power supply filtering`
  - strategy: Add capacitors and ferrite beads on the supply side of the shunt resistor to clean the power rail.

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

## 4. Strategies (15)


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

### ⚠ [anti_pattern_set] Anti-patterns for AES masking countermeasures
- **Trigger**: When designing or implementing a masking countermeasure for AES against power analysis
- **Rationale**: These practices introduce specific weaknesses that can be exploited by first-order or higher-order DPA, undermining the security goal of the masking countermeasure.
- **Anti-pattern 1**: (unnamed)
  - Why: The multiplicative mask does not change the all-zero byte value, leaving a predictable intermediate variable that satisfies the DPA fundamental hypothesis.
- **Anti-pattern 2**: (unnamed)
  - Why: It creates a correlation between intermediate variables that can be exploited by second-order DPA.
- **Anti-pattern 3**: (unnamed)
  - Why: The first and last rounds are most critical for DPA as they involve known plaintext/ciphertext and the key.
- **Applies to**: Algorithm:AES

### 📋 [troubleshooting_checklist] EM trace filtering and alignment for DES
- **Trigger**: when EM traces are noisy and misaligned
- **Rationale**: Noisy EM traces can be aligned by extracting the envelope and then aligning the envelope signals.
- **[rank 1]** if `Isolate EM traces` → Use the Split module to separate EM traces from power traces.
- **[rank 2]** if `Analyze frequency spectrum` → Use the Spectrum module to identify dominant frequencies (e.g., 4 MHz external clock, 32.3 MHz internal clock).
- **[rank 3]** if `Remove external clock harmonics` → Use the Harmonics filter to block the external clock frequency and its harmonics.
- **[rank 4]** if `Extract envelope` → Take the absolute value and apply a low-pass filter (e.g., weight 100) to get the envelope.
- **[rank 5]** if `Align traces` → Use static alignment on the envelope traces with appropriate parameters (length, threshold).
- **Applies to**: Algorithm:DES, Preprocessing:Harmonics Filter, Preprocessing:Static Alignment

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
All files for this session are stored in: ..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_053246_934
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_053246_934/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 17,307→970

**🤖 LLM:** 我将帮您对STM32F103 MCU软件实现的AES进行CPA密钥恢复。首先，让我检查一下数据文件的基本情况。

**🔧 → `python_jupyter`**

<details><summary>Code (2383 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt
import os

# 检查文件是否存在
plaintext_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy'
ciphertext_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy'
wave_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy'

print("文件检查:")
print(f"明文文件存在: {os.path.exists(plaintext_path)}")
print(f"密文文件存在: {os.path.exists(ciphertext_path)}")
print(f"波形文件存在: {os.path.exists(wave_path)}")

# 加载数据查看基本信息
plaintext = np.load(plaintext_path)
ciphertext = np.load(ciphertext_path)
wave = np.load(wave_path)

print(f"\n数据形状:")
print(f"明文: {plaintext.shape} (数据类型: {plaintext.dtype})")
print(f"密文: {ciphertext.shape} (数据类型: {ciphertext.dtype})")
print(f"波形: {wave.shape} (数据类型: {wave.dtype})")

print(f"\n波形统计信息:")
print(f"波形范围: [{wave.min():.2f}, {wave.max():.2f}]")
print(f"波形均值: {wave.mean():.2f}")
print(f"波形标准差: {wave.std():.2f}")

# 查看前几个明文/密文
print(f"\n前3个明文 (十六进制):")
for i in range(min(3, len(plaintext))):
    print(f"  {i}: {plaintext[i].tobytes().hex()}")

print(f"\n前3个密文 (十六进制):")
for i in range(min(3, len(ciphertext))):
    print(f"  {i}: {ciphertext[i].tobytes().hex()}")

# 绘制几条波形看看
plt.figure(figsize=(12, 6))
for i in range(3):
    plt.plot(wave[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('First 3 Power Traces')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('first_3_traces.png')
plt.show()

# 计算波形方差，寻找加密区域
trace_variance = np.var(wave, axis=0)
plt.figure(figsize=(12, 4))
plt.plot(trace_variance)
plt.xlabel('Sample Index')
plt.ylabel('Variance')
plt.title('Trace Variance Across All Traces')
plt.grid(True, alpha=0.3)
plt.savefig('trace_variance.png')
plt.show()

# 找出方差最大的区域
max_var_idx = np.argmax(trace_variance)
print(f"\n最大方差位置: 样本 {max_var_idx}, 方差值: {trace_variance[max_var_idx]:.4f}")

# 查看方差最大的区域附近
window = 100
start = max(0, max_var_idx - window)
end = min(len(trace_variance), max_var_idx + window)
print(f"最大方差区域 [{start}:{end}] 的方差统计:")
print(f"  均值: {trace_variance[start:end].mean():.4f}")
print(f"  最大值: {trace_variance[start:end].max():.4f}")
print(f"  最小值: {trace_variance[start:end].min():.4f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (878 chars)</summary>

```
文件检查:
明文文件存在: True
密文文件存在: True
波形文件存在: True

数据形状:
明文: (250, 16) (数据类型: uint8)
密文: (250, 16) (数据类型: uint8)
波形: (250, 1500) (数据类型: float32)

波形统计信息:
波形范围: [-342.52, 90.55]
波形均值: -131.33
波形标准差: 61.50

前3个明文 (十六进制):
  0: 33f25e5f412260df3ad3d47477f4ce89
  1: 381e684af2267f5b549e6d7fb8bf9bc5
  2: 5a29fb3a6236665e5d1ac5c49f435faa

前3个密文 (十六进制):
  0: 17eaf0dcb9e3bc6f7a83d9f769bfc973
  1: 354b46dbc4f91aa4fb2eba84e101a252
  2: 11b42377f7520e3e18aa8368d6c85599

最大方差位置: 样本 1102, 方差值: 3632.2959
最大方差区域 [1002:1202] 的方差统计:
  均值: 1338.8448
  最大值: 3632.2959
  最小值: 272.3355
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1677745715.py:49: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1677745715.py:60: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 18,726→432

**🤖 LLM:** 很好！数据加载成功。我们有250条轨迹，每条1500个采样点。从方差分析可以看出，加密区域大约在样本1102附近（方差最大）。这是STM32F103的软件实现，根据DKG知识，我应该：

1. **软件实现不需要垂直对齐**（根据anti_pattern_set）
2. **使用S-box_out + HW模型**（软件实现的标准配置）
3. **先尝试直接CPA**，如果效果不好再考虑对齐

让我先对原始波形进行CPA攻击，使用软件实现的标准配置：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "leakage_model": "HW",
  "target": "S-box_out",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2994 chars)</summary>

```
{"recovered_key": "11ECD6443566920D5339BBCC4EEEFF00", "cpa_avg_correlation": 0.3177, "cpa_min_correlation": 0.2679, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_053353_881907.png", "detail_file": "cpa_detail_20260424_053353_882907.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3251, "time_index": 586, "gap_pct": 14.4}, {"byte": 1, "key": "0xEC", "correlation": 0.2679, "time_index": 823, "gap_pct": 1.3}, {"byte": 2, "key": "0xD6", "correlation": 0.3516, "time_index": 492, "gap_pct": 21.1}, {"byte": 3, "key": "0x44", "correlation": 0.3574, "time_index": 1038, "gap_pct": 19.1}, {"byte": 4, "key": "0x35", "correlation": 0.2881, "time_index": 168, "gap_pct": 4.2}, {"byte": 5, "key": "0x66", "correlation": 0.3694, "time_index": 823, "gap_pct": 23.8}, {"byte": 6, "key": "0x92", "correlation": 0.3066, "time_index": 91, "gap_pct": 3.9}, {"byte": 7, "key": "0x0D", "correlation": 0.2767, "time_index": 446, "gap_pct": 3.9}, {"byte": 8, "key": "0x53", "correlation": 0.2897, "time_index": 1012, "gap_pct": 0.7}, {"byte": 9, "key": "0x39", "correlation": 0.2711, "time_index": 240, "gap_pct": 2.2}, {"byte": 10, "key": "0xBB", "correlation": 0.3862, "time_index": 913, "gap_pct": 30.6}, {"byte": 11, "key": "0xCC", "correlation": 0.3413, "time_index": 1021, "gap_pct": 11.6}, {"byte": 12, "key": "0x4E", "correlation": 0.27, "time_index": 338, "gap_pct": 1.1}, {"byte": 13, "key": "0xEE", "correlation": 0.333, "time_index": 862, "gap_pct": 21.0}, {"byte
...(truncated)
```
</details>


![cpa_result_20260424_053353_881907.png](./cpa_result_20260424_053353_881907.png)


---

### Round 3 | tokens: 20,471→380

**🤖 LLM:** 第一次CPA的结果显示只有6/16字节是高置信度的（红色区域）。平均相关性0.3177还不错，但gap_pct显示很多字节的区分度不够。根据DKG知识，对于软件实现，我应该：

1. **先尝试平滑滤波**（软件实现通常需要轻微滤波）
2. **检查是否需要对齐**（时间索引分散在91-1038之间，说明可能有对齐问题）

让我先应用加权移动平均滤波，这是软件实现的常见预处理：

**🔧 → `weighted_moving_average`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "weight": 3,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `weighted_moving_average`</b> (1566 chars)</summary>

```
{"out_wave_npy": "smoothed_20260424_053420_187858.npy", "plot_path": "smooth_compare_20260424_053420_187858.png", "n_traces": 250, "n_points": 1500, "weight": 3, "plaintext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy", "ciphertext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"}
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2144662725.py:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy" is not None:
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2144662725.py:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F1
...(truncated)
```
</details>


![smooth_compare_20260424_053420_187858.png](./smooth_compare_20260424_053420_187858.png)


---

### Round 4 | tokens: 21,578→282

**🤖 LLM:** 现在对平滑后的波形进行CPA攻击：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "smoothed_20260424_053420_187858.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "leakage_model": "HW",
  "target": "S-box_out",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2702 chars)</summary>

```
{"recovered_key": "11F5D6449766770D99AABBCC50EEFF00", "cpa_avg_correlation": 0.3199, "cpa_min_correlation": 0.2585, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_053434_140907.png", "detail_file": "cpa_detail_20260424_053434_140907.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.312, "time_index": 597, "gap_pct": 15.4}, {"byte": 1, "key": "0xF5", "correlation": 0.2585, "time_index": 893, "gap_pct": 1.7}, {"byte": 2, "key": "0xD6", "correlation": 0.3456, "time_index": 494, "gap_pct": 19.1}, {"byte": 3, "key": "0x44", "correlation": 0.3648, "time_index": 1039, "gap_pct": 22.8}, {"byte": 4, "key": "0x97", "correlation": 0.2958, "time_index": 31, "gap_pct": 7.4}, {"byte": 5, "key": "0x66", "correlation": 0.3592, "time_index": 825, "gap_pct": 21.5}, {"byte": 6, "key": "0x77", "correlation": 0.2895, "time_index": 942, "gap_pct": 0.1}, {"byte": 7, "key": "0x0D", "correlation": 0.274, "time_index": 447, "gap_pct": 3.3}, {"byte": 8, "key": "0x99", "correlation": 0.313, "time_index": 611, "gap_pct": 9.1}, {"byte": 9, "key": "0xAA", "correlation": 0.2928, "time_index": 668, "gap_pct": 9.7}, {"byte": 10, "key": "0xBB", "correlation": 0.3673, "time_index": 914, "gap_pct": 27.3}, {"byte": 11, "key": "0xCC", "correlation": 0.3546, "time_index": 1023, "gap_pct": 19.3}, {"byte": 12, "key": "0x50", "correlation": 0.28, "time_index": 36, "gap_pct": 11.0}, {"byte": 13, "key": "0xEE", "correlation": 0.3327, "time_index": 863, "gap_pct": 17.3}, {"byte": 
...(truncated)
```
</details>


![cpa_result_20260424_053434_140907.png](./cpa_result_20260424_053434_140907.png)


---

### Round 5 | tokens: 23,043→265

**🤖 LLM:** 平滑后高置信度字节从6个提升到9个，但仍然在红色区域。时间索引仍然很分散（31-1039），说明可能存在对齐问题。让我检查一下波形，看看是否需要对齐。根据DKG知识，我应该先进行方差分析来定位加密区域，然后进行对齐。

让我先进行明文相关性分析来定位泄漏区域：

**🔧 → `plaintext_ciphertext_correlation`** `{
  "wave_npy": "smoothed_20260424_053420_187858.npy",
  "data_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "data_type": "plaintext",
  "byte_index": 0,
  "model": "HW"
}`

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 603, "peak_region_end": 626, "peak_time_index": 607, "peak_correlation": 0.2136, "suggested_cpa_range": [553, 676], "all_byte_peaks": [607, 270, 307, 357, 230, 262, 269, 373, 243, 273, 347, 364, 64, 285, 102, 369], "byte_peaks_std": 117.5, "plot_path": "correlation_20260424_053455_211926.png"}`


![correlation_20260424_053455_211926.png](./correlation_20260424_053455_211926.png)


---

### Round 6 | tokens: 23,464→356

**🤖 LLM:** 明文相关性分析显示峰值在607附近，但不同字节的峰值位置差异很大（标准差117.5），这进一步证实了需要对齐。让我使用方差最大的区域（1102附近）作为对齐参考点。根据DKG知识，对于STM32F103这样的MCU，max_shift应该设置得大一些（150-200）。

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "smoothed_20260424_053420_187858.npy",
  "start": 1100,
  "length": 100,
  "max_shift": 200,
  "threshold": 85,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_053512_012130.npy", "plot_path": "align_overlay_20260424_053512_012130.png", "ref_trace_used": 125, "accepted": 250, "discarded": 0, "total": 250, "out_plaintext_npy": "plaintext_aligned_20260424_053512_012130.npy", "plaintext_traces": 250, "out_ciphertext_npy": "ciphertext_aligned_20260424_053512_012130.npy", "ciphertext_traces": 250, "alignment_avg_correlation": 0.9945, "alignment_min_correlation": 0.8889, "acceptance_rate": 1.0}`


![align_overlay_20260424_053512_012130.png](./align_overlay_20260424_053512_012130.png)


---

### Round 7 | tokens: 24,018→212

**🤖 LLM:** 很好！对齐成功，接受了所有250条轨迹，平均相关性0.9945。现在对对齐后的波形进行CPA攻击：

**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_053512_012130.npy",
  "wave_npy": "aligned_20260424_053512_012130.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_053512_012130.npy",
  "leakage_model": "HW",
  "target": "S-box_out",
  "candidates": 20
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2141 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.4, "cpa_min_correlation": 0.2993, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_053525_776816.png", "detail_file": "cpa_detail_20260424_053525_776816.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3877, "time_index": 584, "gap_pct": 26.0}, {"byte": 1, "key": "0x22", "correlation": 0.3363, "time_index": 849, "gap_pct": 17.1}, {"byte": 2, "key": "0x33", "correlation": 0.2993, "time_index": 689, "gap_pct": 10.0}, {"byte": 3, "key": "0x44", "correlation": 0.4444, "time_index": 1043, "gap_pct": 44.9}, {"byte": 4, "key": "0x55", "correlation": 0.3796, "time_index": 595, "gap_pct": 19.0}, {"byte": 5, "key": "0x66", "correlation": 0.4091, "time_index": 822, "gap_pct": 33.4}, {"byte": 6, "key": "0x77", "correlation": 0.4257, "time_index": 930, "gap_pct": 33.9}, {"byte": 7, "key": "0x88", "correlation": 0.399, "time_index": 960, "gap_pct": 26.2}, {"byte": 8, "key": "0x99", "correlation": 0.3685, "time_index": 605, "gap_pct": 30.9}, {"byte": 9, "key": "0xAA", "correlation": 0.4113, "time_index": 831, "gap_pct": 33.7}, {"byte": 10, "key": "0xBB", "correlation": 0.4313, "time_index": 1113, "gap_pct": 33.3}, {"byte": 11, "key": "0xCC", "correlation": 0.4466, "time_index": 996, "gap_pct": 39.3}, {"byte": 12, "key": "0xDD", "correlation": 0.3392, "time_index": 616, "gap_pct": 19.1}, {"byte": 13, "key": "0xEE", "correlation": 0.4648, "time_index": 848, "gap_pct": 36.8}, 
...(truncated)
```
</details>


![cpa_result_20260424_053525_776816.png](./cpa_result_20260424_053525_776816.png)


---

### Round 8 | tokens: 25,145→260

**🤖 LLM:** 太好了！对齐后CPA结果显著改善：15/16字节是高置信度的，只有字节2不可靠。恢复的密钥是`112233445566778899AABBCCDDEEFF00`。平均相关性从0.32提升到0.40。现在让我验证这个密钥是否正确：

**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_053512_012130.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_053512_012130.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "17EAF0DCB9E3BC6F7A83D9F769BFC973", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 17EAF0DCB9E3BC6F7A83D9F769BFC973...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 9 | tokens: 25,548→496

**🤖 LLM:** 完美！密钥验证通过！恢复的密钥`112233445566778899AABBCCDDEEFF00`是正确的。让我再验证几个其他轨迹以确保一致性：

**🔧 → `python_jupyter`**

<details><summary>Code (1103 chars)</summary>

```python
import numpy as np
from Crypto.Cipher import AES

# 加载数据
plaintext = np.load('plaintext_aligned_20260424_053512_012130.npy')
ciphertext = np.load('ciphertext_aligned_20260424_053512_012130.npy')
key = bytes.fromhex('112233445566778899AABBCCDDEEFF00')

# 创建AES加密器
cipher = AES.new(key, AES.MODE_ECB)

# 验证多个轨迹
print("验证多个轨迹的密钥正确性:")
for i in range(5):
    pt = bytes(plaintext[i])
    ct_expected = bytes(ciphertext[i])
    ct_actual = cipher.encrypt(pt)
    
    if ct_actual == ct_expected:
        print(f"  轨迹 {i}: ✅ 匹配")
    else:
        print(f"  轨迹 {i}: ❌ 不匹配")
        print(f"    预期: {ct_expected.hex()}")
        print(f"    实际: {ct_actual.hex()}")

# 检查字节2的情况
print(f"\n字节2的详细信息:")
print(f"  恢复的密钥字节2: 0x33")
print(f"  相关性: 0.2993")
print(f"  gap_pct: 10.0% (低于15%阈值)")

# 查看CPA细节
import json
with open('cpa_detail_20260424_053525_776816.json', 'r') as f:
    cpa_detail = json.load(f)

byte2_candidates = cpa_detail['per_byte_candidates'][2]
print(f"\n字节2的前5个候选:")
for i, cand in enumerate(byte2_candidates[:5]):
    print(f"  {i+1}. 密钥: 0x{cand['key_hex']}, 相关性: {cand['correlation']:.4f}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
验证多个轨迹的密钥正确性:
  轨迹 0: ✅ 匹配
  轨迹 1: ✅ 匹配
  轨迹 2: ✅ 匹配
  轨迹 3: ✅ 匹配
  轨迹 4: ✅ 匹配

字节2的详细信息:
  恢复的密钥字节2: 0x33
  相关性: 0.2993
  gap_pct: 10.0% (低于15%阈值)

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[327][39m[32m, line 37[39m
[32m     34[39m [38;5;28;01mwith[39;00m [38;5;28mopen[39m([33m'[39m[33mcpa_detail_20260424_053525_776816.json[39m[33m'[39m, [33m'[39m[33mr[39m[33m'[39m) [38;5;28;01mas[39;00m f:
[32m     35[39m     cpa_detail = json.load(f)
[32m---> [39m[32m37[39m byte2_candidates = [43mcpa_detail[49m[43m[[49m[33;43m'[39;49m[33;43mper_byte_candidates[39;49m[33;43m'[39;49m[43m][49m[[32m2[39m]
[32m     38[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;130;01m\n[39;00m[33m字节2的前5个候选:[39m[33m"[39m)
[32m     39[39m [38;5;28;01mfor[39;00m i, cand [38;5;129;01min[39;00m [38;5;28menumerate[39m(byte2_candidates[:[32m5[39m]):

[31mKeyError[39m: 'per_byte_candidates'
```


---

### Round 10 | tokens: 26,670→303

**🤖 LLM:** 让我检查CPA细节文件的结构：

**🔧 → `python_jupyter`**

<details><summary>Code (688 chars)</summary>

```python
import json

# 检查CPA细节文件
with open('cpa_detail_20260424_053525_776816.json', 'r') as f:
    cpa_detail = json.load(f)

print("CPA细节文件键:", list(cpa_detail.keys()))
print("\n字节2的候选信息:")
if 'per_byte_candidates' in cpa_detail:
    byte2_candidates = cpa_detail['per_byte_candidates'][2]
    for i, cand in enumerate(byte2_candidates[:5]):
        print(f"  {i+1}. 密钥: 0x{cand['key_hex']}, 相关性: {cand['correlation']:.4f}")
else:
    print("  没有找到per_byte_candidates键")
    
# 查看低置信度子键信息
print("\n低置信度子键信息:")
low_conf = cpa_detail.get('low_confidence_subkeys', [])
for subkey in low_conf:
    print(f"  字节 {subkey['byte']}: 最佳密钥 0x{subkey['best_key_hex']}, gap: {subkey['top1_top2_gap']:.4f}")
```
</details>

**📋 ← `python_jupyter`:** `CPA细节文件键: ['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results']

字节2的候选信息:
  没有找到per_byte_candidates键

低置信度子键信息:`


---

### Round 11 | tokens: 27,044→698

**🤖 LLM:** 让我查看完整的攻击结果总结：

**🔧 → `python_jupyter`**

<details><summary>Code (1408 chars)</summary>

```python
# 总结攻击过程
print("="*60)
print("STM32F103 AES-128 CPA密钥恢复总结")
print("="*60)

print(f"\n1. 数据信息:")
print(f"   - 轨迹数量: 250")
print(f"   - 采样点数: 1500")
print(f"   - 算法: AES-128 ECB")

print(f"\n2. 攻击过程:")
print(f"   a) 初始CPA (原始波形):")
print(f"      - 恢复密钥: 11ECD6443566920D5339BBCC4EEEFF00")
print(f"      - 高置信度字节: 6/16 (红色区域)")
print(f"      - 平均相关性: 0.3177")

print(f"\n   b) 平滑滤波后CPA:")
print(f"      - 恢复密钥: 11F5D6449766770D99AABBCC50EEFF00")  
print(f"      - 高置信度字节: 9/16 (红色区域)")
print(f"      - 平均相关性: 0.3199")

print(f"\n   c) 对齐后CPA:")
print(f"      - 对齐参数: start=1100, length=100, max_shift=200, threshold=85")
print(f"      - 接受率: 250/250 (100%)")
print(f"      - 对齐平均相关性: 0.9945")
print(f"      - 恢复密钥: 112233445566778899AABBCCDDEEFF00")
print(f"      - 高置信度字节: 15/16 (绿色区域)")
print(f"      - 平均相关性: 0.4000")
print(f"      - 唯一低置信度字节: 字节2 (gap_pct=10.0%)")

print(f"\n3. 密钥验证:")
print(f"   - 恢复的密钥: 112233445566778899AABBCCDDEEFF00")
print(f"   - 验证结果: ✅ MATCH (所有5个测试轨迹都通过)")

print(f"\n4. 关键成功因素:")
print(f"   - 使用方差分析定位加密区域 (样本1102附近)")
print(f"   - 适当的对齐参数 (max_shift=200 覆盖MCU时钟抖动)")
print(f"   - 软件实现标准配置: S-box_out + HW模型")
print(f"   - 轻微平滑滤波 (weight=3)")

print(f"\n5. 从DKG知识应用:")
print(f"   - ✅ 软件实现不需要垂直对齐")
print(f"   - ✅ 使用S-box_out + HW模型作为默认")
print(f"   - ✅ 对齐max_shift设置较大值(200)而不是默认小值")
print(f"   - ✅ 方差优先的ROI探索原则")
print(f"   - ✅ 在绿色区域(15/16)不重新预处理，直接验证密钥")

print("\n" + "="*60)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1158 chars)</summary>

```
============================================================
STM32F103 AES-128 CPA密钥恢复总结
============================================================

1. 数据信息:
   - 轨迹数量: 250
   - 采样点数: 1500
   - 算法: AES-128 ECB

2. 攻击过程:
   a) 初始CPA (原始波形):
      - 恢复密钥: 11ECD6443566920D5339BBCC4EEEFF00
      - 高置信度字节: 6/16 (红色区域)
      - 平均相关性: 0.3177

   b) 平滑滤波后CPA:
      - 恢复密钥: 11F5D6449766770D99AABBCC50EEFF00
      - 高置信度字节: 9/16 (红色区域)
      - 平均相关性: 0.3199

   c) 对齐后CPA:
      - 对齐参数: start=1100, length=100, max_shift=200, threshold=85
      - 接受率: 250/250 (100%)
      - 对齐平均相关性: 0.9945
      - 恢复密钥: 112233445566778899AABBCCDDEEFF00
      - 高置信度字节: 15/16 (绿色区域)
      - 平均相关性: 0.4000
      - 唯一低置信度字节: 字节2 (gap_pct=10.0%)

3. 密钥验证:
   - 恢复的密钥: 112233445566778899AABBCCDDEEFF00
   - 验证结果: ✅ MATCH (所有5个测试轨迹都通过)

4. 关键成功因素:
   - 使用方差分析定位加密区域 (样本1102附近)
   - 适当的对齐参数 (max_shift=200 覆盖MCU时钟抖动)
   - 软件实现标准配置: S-box_out + HW模型
   - 轻微平滑滤波 (weight=3)

5. 从DKG知识应用:
   - ✅ 软件实现不需要垂直对齐
   - ✅ 使用S-box_out + HW模型作为默认
   - ✅ 对齐max_shift设置较大值(200)而不是默认小值
   - ✅ 方差优先的ROI探索原则
   - ✅ 在绿色区域(15/16)不重新预处理，直接验证密钥

============================================================
```
</details>


---

### Round 12 | tokens: 28,272→371

**🤖 LLM:** ## 总结

成功恢复了STM32F103 MCU软件实现的AES-128密钥：**`112233445566778899AABBCCDDEEFF00`**

### 攻击流程：
1. **初始分析**：检查数据，发现加密区域在样本1102附近（方差最大）
2. **直接CPA**：使用S-box_out + HW模型，只有6/16字节高置信度
3. **平滑滤波**：应用weight=3的加权移动平均，提升到9/16字节
4. **静态对齐**：以样本1100为中心，length=100，max_shift=200进行对齐
5. **对齐后CPA**：显著改善，15/16字节高置信度，平均相关性0.40
6. **密钥验证**：验证通过，密钥正确

### 关键成功因素：
- **正确的泄漏模型**：软件实现使用S-box_out + HW模型
- **适当的对齐**：使用方差最大的区域作为对齐参考，max_shift=200覆盖MCU时钟抖动
- **轻微滤波**：weight=3平滑滤波改善信噪比
- **遵循DKG最佳实践**：软件实现不需要垂直对齐，对齐参数设置合理

### 从DKG知识应用：
1. 遵循了"软件实现不需要垂直对齐"的anti-pattern
2. 应用了"对齐max_shift应该开始大(300+)，不是默认小"的原则
3. 使用了"方差优先的ROI探索原则"定位加密区域
4. 在绿色区域(15/16高置信度)直接验证密钥，不重新预处理

攻击成功证明了DKG知识在实战中的有效性，特别是对于STM32F103这类MCU软件实现的AES攻击。


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 17,307 | 970 | 18,277 |
| 2 | 18,726 | 432 | 19,158 |
| 3 | 20,471 | 380 | 20,851 |
| 4 | 21,578 | 282 | 21,860 |
| 5 | 23,043 | 265 | 23,308 |
| 6 | 23,464 | 356 | 23,820 |
| 7 | 24,018 | 212 | 24,230 |
| 8 | 25,145 | 260 | 25,405 |
| 9 | 25,548 | 496 | 26,044 |
| 10 | 26,670 | 303 | 26,973 |
| 11 | 27,044 | 698 | 27,742 |
| 12 | 28,272 | 371 | 28,643 |
| **Total** | **281,286** | **5,025** | **286,311** |

## 8. Final Output

## 总结

成功恢复了STM32F103 MCU软件实现的AES-128密钥：**`112233445566778899AABBCCDDEEFF00`**

### 攻击流程：
1. **初始分析**：检查数据，发现加密区域在样本1102附近（方差最大）
2. **直接CPA**：使用S-box_out + HW模型，只有6/16字节高置信度
3. **平滑滤波**：应用weight=3的加权移动平均，提升到9/16字节
4. **静态对齐**：以样本1100为中心，length=100，max_shift=200进行对齐
5. **对齐后CPA**：显著改善，15/16字节高置信度，平均相关性0.40
6. **密钥验证**：验证通过，密钥正确

### 关键成功因素：
- **正确的泄漏模型**：软件实现使用S-box_out + HW模型
- **适当的对齐**：使用方差最大的区域作为对齐参考，max_shift=200覆盖MCU时钟抖动
- **轻微滤波**：weight=3平滑滤波改善信噪比
- **遵循DKG最佳实践**：软件实现不需要垂直对齐，对齐参数设置合理

### 从DKG知识应用：
1. 遵循了"软件实现不需要垂直对齐"的anti-pattern
2. 应用了"对齐max_shift应该开始大(300+)，不是默认小"的原则
3. 使用了"方差优先的ROI探索原则"定位加密区域
4. 在绿色区域(15/16高置信度)直接验证密钥，不重新预处理

攻击成功证明了DKG知识在实战中的有效性，特别是对于STM32F103这类MCU软件实现的AES攻击。
