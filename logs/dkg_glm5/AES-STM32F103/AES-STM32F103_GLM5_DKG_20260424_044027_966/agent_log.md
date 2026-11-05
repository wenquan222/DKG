# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_044027_966 |
| Duration | 429.6s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-STM32F103_GLM5_DKG_20260424_044027_966` |
| Total LLM Calls | 24 |
| First Round | prompt: 17,280, completion: 1,131 |
| Last Round | prompt: 38,586, completion: 463 |
| Total Tokens | 703,424 (prompt: 691,946, completion: 11,478) |

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

LLM Response: json
["AES", "STM32F103", "MCU", "CPA", "Power", "Software"]

Parsed Keywords: `["AES", "STM32F103", "MCU", "CPA", "Power", "Software"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 46088 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (48346 chars, click to expand)</summary>

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

**Search keywords** (6): AES, STM32F103, MCU, CPA, Power, Software

**Summary**: 32 upper entities, 25 relationships, 21 diagnostic chains, 15 strategies


## 1. Upper Layer Entities (32)


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
- **ATSAMD21 microcontroller** — implementation_type=software, category=MCU

### Pipeline (13)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **Close to worst-case evaluation methodology for masked bitslice implementations** — source=thesis, trigger_condition=evaluating masked bitslice implementations, applicable_scenarios=masked bitslice software implementations on microcontrollers
- **Collision DL-SCA (Staib-Moradi)** — source=Staib and Moradi (2023), trigger_condition=non-profiled side-channel attack on a block cipher with serial Sbox computations, applicable_scenarios=software implementations where Sbox computations are serial and leakages are separable in time
- **Correlation-based pattern matching for RDI removal** — source=expert_experience, trigger_condition=random delays exhibit regular patterns (e.g., repetitive dummy loops), applicable_scenarios=software implementations where dummy operations or AES operation blocks have distinctive and consistent leakage patterns
- **HMM cryptanalysis of RDI-protected implementations** — source=expert_experience, trigger_condition=attacking a software implementation protected with random delay insertions, applicable_scenarios=microcontroller implementations of symmetric block ciphers (e.g., AES) with random delays inserted via dummy loops or interrupts
- **HMM-based Random Delay Removal and CPA** — source=PAP-33-2013-ePrint-HMM-Remove-Random-Delays, trigger_condition=when attacking a software implementation protected with random delay insertions (RDI) via power traces, applicable_scenarios=Embedded software implementations (e.g., on 8-bit microcontrollers) using random delays as a hiding countermeasure; requires ability to profile instruction cycles on a similar device.

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
- `DeviceClass:32-bit STM Controller` —[works_with [source_text=CHES CTF ... AutoPOI ... 1830, support_count=1, confidence=0.2, source_papers=["PAP-74-2023-ePrint-AutoPOI"]]]→ `Algorithm:AES`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Preprocessing:Resampling`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Pipeline:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `StatMethod:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `LeakageModel:identity`
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

## 4. Strategies (15)


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

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-STM32F103_GLM5_DKG_20260424_044027_966
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-STM32F103_GLM5_DKG_20260424_044027_966/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 17,280→1,131

**🤖 LLM:** 我来帮你对STM32F103 MCU软件实现的AES进行CPA攻击。根据知识图谱，这是一个软件实现，我将按照标准流程进行分析。

首先，让我检查波形数据的基本特征：

**🔧 → `python_jupyter`**

<details><summary>Code (1813 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy')

print(f"波形数据形状: {wave.shape}")
print(f"明文数据形状: {plain.shape}")
print(f"密文数据形状: {cipher.shape}")
print(f"\n波形数据范围: [{wave.min():.4f}, {wave.max():.4f}]")
print(f"波形数据均值: {wave.mean():.4f}")
print(f"波形数据标准差: {wave.std():.4f}")

# 绘制几条波形查看特征
plt.figure(figsize=(14, 8))

# 绘制前5条波形
plt.subplot(2, 2, 1)
for i in range(5):
    plt.plot(wave[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Point')
plt.ylabel('Power')
plt.title('First 5 Traces')
plt.legend()
plt.grid(True, alpha=0.3)

# 绘制平均波形
plt.subplot(2, 2, 2)
mean_wave = np.mean(wave, axis=0)
plt.plot(mean_wave)
plt.xlabel('Sample Point')
plt.ylabel('Power (Mean)')
plt.title('Average Trace')
plt.grid(True, alpha=0.3)

# 绘制方差（用于定位加密区域）
plt.subplot(2, 2, 3)
var_wave = np.var(wave, axis=0)
plt.plot(var_wave)
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.title('Variance Across Traces')
plt.grid(True, alpha=0.3)

# 绘制标准差
plt.subplot(2, 2, 4)
std_wave = np.std(wave, axis=0)
plt.plot(std_wave)
plt.xlabel('Sample Point')
plt.ylabel('Std Dev')
plt.title('Standard Deviation Across Traces')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

# 找到方差最大的区域（可能是加密区域）
var_peaks = np.argsort(var_wave)[-20:]
print(f"\n方差最大的20个采样点: {sorted(var_peaks)}")
print(f"方差峰值位置: {np.argmax(var_wave)}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (626 chars)</summary>

```
波形数据形状: (250, 1500)
明文数据形状: (250, 16)
密文数据形状: (250, 16)

波形数据范围: [-342.5197, 90.5512]
波形数据均值: -131.3288
波形数据标准差: 61.4955

方差最大的20个采样点: [np.int64(1063), np.int64(1064), np.int64(1065), np.int64(1094), np.int64(1095), np.int64(1096), np.int64(1097), np.int64(1098), np.int64(1099), np.int64(1100), np.int64(1101), np.int64(1102), np.int64(1103), np.int64(1104), np.int64(1105), np.int64(1106), np.int64(1107), np.int64(1108), np.int64(1109), np.int64(1110)]
方差峰值位置: 1102
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3694000068.py:58: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 18,289→365

**🤖 LLM:** 很好！波形数据显示：
- **250条trace，每条1500个采样点**
- **方差峰值区域在1098-1110附近**，这很可能是AES加密的关键区域

根据知识图谱的建议，对于STM32F103软件实现，我将：
1. 先进行**直接CPA探测**（不做对齐），评估是否需要预处理
2. 使用标准的 **S-box_out + HW** 模型

让我先进行直接CPA攻击：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2994 chars)</summary>

```
{"recovered_key": "11ECD6443566920D5339BBCC4EEEFF00", "cpa_avg_correlation": 0.3177, "cpa_min_correlation": 0.2679, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_044129_670947.png", "detail_file": "cpa_detail_20260424_044129_670947.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3251, "time_index": 586, "gap_pct": 14.4}, {"byte": 1, "key": "0xEC", "correlation": 0.2679, "time_index": 823, "gap_pct": 1.3}, {"byte": 2, "key": "0xD6", "correlation": 0.3516, "time_index": 492, "gap_pct": 21.1}, {"byte": 3, "key": "0x44", "correlation": 0.3574, "time_index": 1038, "gap_pct": 19.1}, {"byte": 4, "key": "0x35", "correlation": 0.2881, "time_index": 168, "gap_pct": 4.2}, {"byte": 5, "key": "0x66", "correlation": 0.3694, "time_index": 823, "gap_pct": 23.8}, {"byte": 6, "key": "0x92", "correlation": 0.3066, "time_index": 91, "gap_pct": 3.9}, {"byte": 7, "key": "0x0D", "correlation": 0.2767, "time_index": 446, "gap_pct": 3.9}, {"byte": 8, "key": "0x53", "correlation": 0.2897, "time_index": 1012, "gap_pct": 0.7}, {"byte": 9, "key": "0x39", "correlation": 0.2711, "time_index": 240, "gap_pct": 2.2}, {"byte": 10, "key": "0xBB", "correlation": 0.3862, "time_index": 913, "gap_pct": 30.6}, {"byte": 11, "key": "0xCC", "correlation": 0.3413, "time_index": 1021, "gap_pct": 11.6}, {"byte": 12, "key": "0x4E", "correlation": 0.27, "time_index": 338, "gap_pct": 1.1}, {"byte": 13, "key": "0xEE", "correlation": 0.333, "time_index": 862, "gap_pct": 21.0}, {"byte
...(truncated)
```
</details>


![cpa_result_20260424_044129_670947.png](./cpa_result_20260424_044129_670947.png)


---

### Round 3 | tokens: 19,871→540

**🤖 LLM:** 直接CPA结果显示：
- **恢复密钥**: `11ECD6443566920D5339BBCC4EEEFF00`
- **高置信度字节**: 6/16（红色区域）
- **平均相关性**: 0.3177

6/16的高置信度字节处于红色区域，让我先验证这个密钥是否正确：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "key_hex": "11ECD6443566920D5339BBCC4EEEFF00",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "8D71B849FC798D496E582EEA92E9E917", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 8D71B849FC798D496E582EEA92E9E917...\n❌ Key verification FAILED — 16/16 ciphertext bytes differ\n   Expected:  17EAF0DCB9E3BC6F7A83D9F769BFC973\n   Got:       8D71B849FC798D496E582EEA92E9E917\n\n   ⚠️ IMPORTANT: '16 ciphertext bytes differ' does NOT mean '16 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 4 | tokens: 20,488→1,141

**🤖 LLM:** 密钥验证失败。根据知识图谱策略，在红色区域（6/16高置信度）不应该直接使用key_search，而应该先重新定位泄漏区域。

让我进行更详细的方差分析来定位加密区间：

**🔧 → `python_jupyter`**

<details><summary>Code (2809 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载波形数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')

# 计算方差
var_wave = np.var(wave, axis=0)

# 使用滑动窗口计算方差，找到加密区域
window_size = 50
var_smooth = np.convolve(var_wave, np.ones(window_size)/window_size, mode='same')

# 找到方差突增的区域
threshold = np.mean(var_smooth) + np.std(var_smooth)
high_var_regions = var_smooth > threshold

# 找到连续的高方差区域
from scipy.ndimage import label
labeled, num_features = label(high_var_regions)
print(f"检测到 {num_features} 个高方差区域")

# 分析每个区域
regions = []
for i in range(1, num_features + 1):
    indices = np.where(labeled == i)[0]
    if len(indices) > 20:  # 只考虑足够大的区域
        start = indices[0]
        end = indices[-1]
        peak_idx = indices[np.argmax(var_smooth[indices])]
        regions.append({
            'start': start,
            'end': end,
            'length': end - start + 1,
            'peak': peak_idx,
            'peak_var': var_smooth[peak_idx]
        })

# 按峰值方差排序
regions.sort(key=lambda x: x['peak_var'], reverse=True)

print("\n高方差区域（按峰值排序）：")
for i, r in enumerate(regions[:5]):
    print(f"区域 {i+1}: [{r['start']}, {r['end']}] 长度={r['length']}, 峰值位置={r['peak']}, 峰值方差={r['peak_var']:.2f}")

# 绘制分析结果
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.plot(var_wave, alpha=0.5, label='Raw Variance')
plt.plot(var_smooth, linewidth=2, label='Smoothed Variance')
plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold={threshold:.2f}')
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.title('Variance Analysis for Encryption Region Detection')
plt.legend()
plt.grid(True, alpha=0.3)

# 标记主要区域
if regions:
    main_region = regions[0]
    plt.axvspan(main_region['start'], main_region['end'], alpha=0.3, color='green', label='Main Region')

# 绘制平均波形对比
plt.subplot(1, 2, 2)
mean_wave = np.mean(wave, axis=0)
plt.plot(mean_wave)
plt.xlabel('Sample Point')
plt.ylabel('Power (Mean)')
plt.title('Average Trace with Variance Peak')
if regions:
    main_region = regions[0]
    plt.axvline(x=main_region['peak'], color='r', linestyle='--', label=f'Variance Peak at {main_region["peak"]}')
    plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('variance_roi_analysis.png', dpi=150)
plt.show()

# 输出推荐的加密区域
if regions:
    main_region = regions[0]
    print(f"\n推荐的主要加密区域: [{main_region['start']}, {main_region['end']}]")
    print(f"方差峰值位置: {main_region['peak']}")
    
    # 检查CPA结果中的时间索引是否落在这个区域
    cpa_time_indices = [586, 823, 492, 1038, 168, 823, 91, 446, 1012, 240, 913, 1021, 338, 862, 895, 1015]
    in_region_count = sum(1 for t in cpa_time_indices if main_region['start'] <= t <= main_region['end'])
    print(f"\nCPA时间索引落在主区域内的比例: {in_region_count}/16")
```
</details>

**📋 ← `python_jupyter`:** `检测到 4 个高方差区域

高方差区域（按峰值排序）：
区域 1: [1044, 1160] 长度=117, 峰值位置=1087, 峰值方差=2491.63
区域 2: [90, 126] 长度=37, 峰值位置=109, 峰值方差=1323.16
区域 3: [403, 426] 长度=24, 峰值位置=417, 峰值方差=1244.62

推荐的主要加密区域: [1044, 1160]
方差峰值位置: 1087

CPA时间索引落在主区域内的比例: 0/16
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1490468521.py:79: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 5 | tokens: 21,707→396

**🤖 LLM:** **关键发现**：方差分析显示主要加密区域在 **[1044, 1160]**，但CPA的时间索引**没有一个**落在这个区域内！这说明CPA在错误的时间区域找到了相关性。

让我使用明文相关性分析来确认真正的泄漏区域：

**🔧 → `plaintext_ciphertext_correlation`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "data_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "data_type": "plaintext",
  "byte_index": 0,
  "model": "HW"
}
```
</details>

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 602, "peak_region_end": 608, "peak_time_index": 606, "peak_correlation": 0.219, "suggested_cpa_range": [552, 658], "all_byte_peaks": [606, 267, 303, 355, 229, 259, 266, 363, 240, 270, 344, 362, 603, 282, 715, 368], "byte_peaks_std": 141.9, "plot_path": "correlation_20260424_044222_097438.png"}`


![correlation_20260424_044222_097438.png](./correlation_20260424_044222_097438.png)


---

### Round 6 | tokens: 22,077→553

**🤖 LLM:** 明文相关性分析显示峰值在606附近，但相关性较低（0.219）。根据知识图谱策略，**方差ROI优先于明文相关性ROI**，因为方差峰值区域（1087）更可能是真正的加密区域。

让我在方差峰值区域进行CPA攻击：

**🔧 → `python_jupyter`**

<details><summary>Code (842 chars)</summary>

```python
import numpy as np
import json

# 加载数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy')

# 提取方差峰值区域 [1044, 1160]
roi_start = 1044
roi_end = 1160
wave_roi = wave[:, roi_start:roi_end]

print(f"提取的ROI区域: [{roi_start}, {roi_end}]")
print(f"ROI波形形状: {wave_roi.shape}")

# 保存ROI波形
np.save('wave_roi.npy', wave_roi)
np.save('plain_roi.npy', plain)
np.save('cipher_roi.npy', cipher)

print("\nROI数据已保存")
print(f"ROI区域长度: {roi_end - roi_start} 采样点")
```
</details>

**📋 ← `python_jupyter`:** `提取的ROI区域: [1044, 1160]
ROI波形形状: (250, 116)

ROI数据已保存
ROI区域长度: 116 采样点`


---

### Round 7 | tokens: 22,524→77

**🤖 LLM:** 现在在方差峰值区域进行CPA攻击：

**🔧 → `aes_cpa_attack`** `{
  "wave_npy": "wave_roi.npy",
  "plaintext_npy": "plain_roi.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (3448 chars)</summary>

```
{"recovered_key": "93D2D636B50F9202DF408D03A73B8D6C", "cpa_avg_correlation": 0.2436, "cpa_min_correlation": 0.225, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_044240_280002.png", "detail_file": "cpa_detail_20260424_044240_280002.json", "per_byte": [{"byte": 0, "key": "0x93", "correlation": 0.2683, "time_index": 82, "gap_pct": 14.3}, {"byte": 1, "key": "0xD2", "correlation": 0.2335, "time_index": 79, "gap_pct": 0.1}, {"byte": 2, "key": "0xD6", "correlation": 0.2311, "time_index": 28, "gap_pct": 2.5}, {"byte": 3, "key": "0x36", "correlation": 0.2336, "time_index": 31, "gap_pct": 2.8}, {"byte": 4, "key": "0xB5", "correlation": 0.225, "time_index": 111, "gap_pct": 2.7}, {"byte": 5, "key": "0x0F", "correlation": 0.2323, "time_index": 67, "gap_pct": 1.9}, {"byte": 6, "key": "0x92", "correlation": 0.2698, "time_index": 10, "gap_pct": 13.6}, {"byte": 7, "key": "0x02", "correlation": 0.2408, "time_index": 82, "gap_pct": 5.4}, {"byte": 8, "key": "0xDF", "correlation": 0.2393, "time_index": 17, "gap_pct": 0.9}, {"byte": 9, "key": "0x40", "correlation": 0.2542, "time_index": 11, "gap_pct": 7.1}, {"byte": 10, "key": "0x8D", "correlation": 0.2461, "time_index": 82, "gap_pct": 3.4}, {"byte": 11, "key": "0x03", "correlation": 0.2396, "time_index": 82, "gap_pct": 2.7}, {"byte": 12, "key": "0xA7", "correlation": 0.2461, "time_index": 38, "gap_pct": 13.6}, {"byte": 13, "key": "0x3B", "correlation": 0.2487, "time_index": 3, "gap_pct": 16.8}, {"byte": 14, "key": "0x8
...(truncated)
```
</details>


![cpa_result_20260424_044240_280002.png](./cpa_result_20260424_044240_280002.png)


---

### Round 8 | tokens: 24,140→987

**🤖 LLM:** ROI区域的CPA结果更差（1/16高置信度）。这说明可能存在波形对齐问题。让我检查波形的对齐情况：

**🔧 → `python_jupyter`**

<details><summary>Code (2129 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载波形
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')

# 检查前20条波形的对齐情况
plt.figure(figsize=(14, 10))

# 绘制前20条波形
plt.subplot(2, 2, 1)
for i in range(20):
    plt.plot(wave[i], alpha=0.5, linewidth=0.8)
plt.xlabel('Sample Point')
plt.ylabel('Power')
plt.title('First 20 Traces (Alignment Check)')
plt.grid(True, alpha=0.3)

# 绘制方差峰值区域 [1044, 1160]
plt.subplot(2, 2, 2)
for i in range(20):
    plt.plot(range(1044, 1160), wave[i, 1044:1160], alpha=0.7, linewidth=0.8)
plt.xlabel('Sample Point')
plt.ylabel('Power')
plt.title('Variance Peak Region [1044-1160] (20 traces)')
plt.grid(True, alpha=0.3)

# 绘制明文相关性峰值区域 [552, 658]
plt.subplot(2, 2, 3)
for i in range(20):
    plt.plot(range(552, 658), wave[i, 552:658], alpha=0.7, linewidth=0.8)
plt.xlabel('Sample Point')
plt.ylabel('Power')
plt.title('Plaintext Correlation Region [552-658] (20 traces)')
plt.grid(True, alpha=0.3)

# 计算并绘制相关系数矩阵（检查trace之间的相似性）
plt.subplot(2, 2, 4)
# 选择方差峰值区域计算相关性
roi = wave[:, 1044:1160]
corr_matrix = np.corrcoef(roi[:50])  # 前50条trace
plt.imshow(corr_matrix, cmap='hot', aspect='auto')
plt.colorbar(label='Correlation')
plt.xlabel('Trace Index')
plt.ylabel('Trace Index')
plt.title('Trace Correlation Matrix (ROI region)')

plt.tight_layout()
plt.savefig('alignment_check.png', dpi=150)
plt.show()

# 计算trace之间的平均相关性
avg_corr = np.mean(corr_matrix[np.triu_indices(50, k=1)])
print(f"前50条trace在ROI区域的平均相关性: {avg_corr:.4f}")

# 检查是否存在明显的峰值偏移
# 通过互相关找到峰值位置
from scipy.signal import find_peaks

peak_positions = []
for i in range(50):
    # 在方差峰值区域找最大值位置
    trace_roi = wave[i, 1044:1160]
    peaks, _ = find_peaks(trace_roi, height=np.max(trace_roi)*0.8)
    if len(peaks) > 0:
        peak_positions.append(1044 + peaks[0])

if peak_positions:
    peak_std = np.std(peak_positions)
    print(f"\n峰值位置标准差: {peak_std:.2f} 采样点")
    print(f"峰值位置范围: [{min(peak_positions)}, {max(peak_positions)}]")
    if peak_std > 10:
        print("⚠️ 峰值位置变化较大，可能需要对齐")
    else:
        print("✓ 峰值位置相对稳定，对齐问题不大")
```
</details>

**📋 ← `python_jupyter`:** `前50条trace在ROI区域的平均相关性: 0.6572

峰值位置标准差: 0.00 采样点
峰值位置范围: [1076, 1076]
✓ 峰值位置相对稳定，对齐问题不大
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3005508947.py:50: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 9 | tokens: 25,074→2,250

**🤖 LLM:** 波形对齐良好。让我尝试扩大搜索范围，看看是否有其他泄漏区域：

**🔧 → `python_jupyter`**

<details><summary>Code (4144 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy')

# AES S-box
sbox = np.array([
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
])

# Hamming weight lookup table
hw_table = np.array([bin(i).count('1') for i in range(256)])

# 对每个字节进行CPA，记录最大相关性位置
n_traces, n_points = wave.shape
correlation_maps = []

print("计算每个字节的CPA相关性图...")
for byte_idx in range(16):
    # 计算假设功耗（所有256个候选密钥）
    hypothetical_power = np.zeros((256, n_traces))
    for key_guess in range(256):
        sbox_out = sbox[plain[:, byte_idx] ^ key_guess]
        hypothetical_power[key_guess] = hw_table[sbox_out]
    
    # 计算相关性
    correlation = np.zeros((256, n_points))
    for key_guess in range(256):
        hp = hypothetical_power[key_guess]
        hp_mean = np.mean(hp)
        hp_std = np.std(hp)
        
        for t in range(n_points):
            trace_col = wave[:, t]
            trace_mean = np.mean(trace_col)
            trace_std = np.std(trace_col)
            
            if hp_std > 0 and trace_std > 0:
                correlation[key_guess, t] = np.abs(np.mean((hp - hp_mean) * (trace_col - trace_mean)) / (hp_std * trace_std))
    
    correlation_maps.append(correlation)
    
    # 找到最大相关性
    max_idx = np.unravel_index(np.argmax(correlation), correlation.shape)
    print(f"字节 {byte_idx}: 最大相关性={correlation[max_idx]:.4f}, 密钥候选={max_idx[0]:02X}, 时间点={max_idx[1]}")

# 绘制所有字节的相关性热图
plt.figure(figsize=(16, 10))
for byte_idx in range(16):
    plt.subplot(4, 4, byte_idx + 1)
    plt.imshow(correlation_maps[byte_idx], aspect='auto', cmap='hot', extent=[0, n_points, 255, 0])
    plt.xlabel('Sample Point')
    plt.ylabel('Key Guess')
    plt.title(f'Byte {byte_idx}')
    plt.colorbar(label='|Correlation|')

plt.tight_layout()
plt.savefig('correlation_heatmap_all_bytes.png', dpi=150)
plt.show()

# 绘制每个字节的最大相关性曲线
plt.figure(figsize=(14, 6))
for byte_idx in range(16):
    max_corr_per_time = np.max(correlation_maps[byte_idx], axis=0)
    plt.plot(max_corr_per_time, alpha=0.7, label=f'Byte {byte_idx}')

plt.xlabel('Sample Point')
plt.ylabel('Max Correlation')
plt.title('Maximum Correlation per Time Point (All Bytes)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('max_correlation_per_time.png', dpi=150)
plt.show()
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (934 chars)</summary>

```
计算每个字节的CPA相关性图...
字节 0: 最大相关性=0.3251, 密钥候选=11, 时间点=586
字节 1: 最大相关性=0.2679, 密钥候选=EC, 时间点=823
字节 2: 最大相关性=0.3516, 密钥候选=D6, 时间点=492
字节 3: 最大相关性=0.3574, 密钥候选=44, 时间点=1038
字节 4: 最大相关性=0.2881, 密钥候选=35, 时间点=168
字节 5: 最大相关性=0.3694, 密钥候选=66, 时间点=823
字节 6: 最大相关性=0.3066, 密钥候选=92, 时间点=91
字节 7: 最大相关性=0.2767, 密钥候选=0D, 时间点=446
字节 8: 最大相关性=0.2897, 密钥候选=53, 时间点=1012
字节 9: 最大相关性=0.2711, 密钥候选=39, 时间点=240
字节 10: 最大相关性=0.3862, 密钥候选=BB, 时间点=913
字节 11: 最大相关性=0.3413, 密钥候选=CC, 时间点=1021
字节 12: 最大相关性=0.2700, 密钥候选=4E, 时间点=338
字节 13: 最大相关性=0.3330, 密钥候选=EE, 时间点=862
字节 14: 最大相关性=0.3131, 密钥候选=FF, 时间点=895
字节 15: 最大相关性=0.3369, 密钥候选=00, 时间点=1015
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2019700562.py:76: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2019700562.py:91: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 10 | tokens: 27,733→443

**🤖 LLM:** 从相关性分析可以看到，每个字节的泄漏时间点确实分散在不同位置，这是AES软件实现的正常现象。直接CPA得到了6/16高置信度字节，虽然处于红色区域，但让我尝试使用key_search来搜索正确的密钥：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "recovered_key_hex": "11ECD6443566920D5339BBCC4EEEFF00",
  "cpa_detail_file": "cpa_detail_20260424_044129_670947.json",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 20,
  "max_combinations": 50000
}
```
</details>

**📋 ← `key_search`:** `{"found": false, "correct_key": null, "search_rounds": 50000, "unreliable_bytes": [0, 1, 4, 6, 7, 8, 9, 11, 12, 14], "recommended_next_step": "merge_more_cpa_runs_or_rerun_with_higher_candidates", "message": "Not found after 50000 searches."}`


---

### Round 11 | tokens: 28,099→320

**🤖 LLM:** key_search未找到正确密钥。根据知识图谱策略，在红色区域应该增加搜索预算而不是切换攻击维度。让我扩大搜索范围：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "cpa_detail_file": "cpa_detail_20260424_044129_670947.json",
  "gap_threshold": 0.2,
  "max_candidates_per_byte": 30,
  "max_combinations": 200000,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "recovered_key_hex": "11ECD6443566920D5339BBCC4EEEFF00",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

**📋 ← `key_search`:** `{"found": false, "correct_key": null, "search_rounds": 200000, "unreliable_bytes": [0, 1, 3, 4, 6, 7, 8, 9, 11, 12, 14, 15], "recommended_next_step": "merge_more_cpa_runs_or_rerun_with_higher_candidates", "message": "Not found after 200000 searches."}`


---

### Round 12 | tokens: 28,449→215

**🤖 LLM:** 让我尝试使用ID模型（Identity）进行CPA攻击：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "candidates": 20,
  "leakage_model": "ID",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "target": "S-box_out",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy"
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (3559 chars)</summary>

```
{"recovered_key": "5AB2CDD255674981DCD924CC9239687D", "cpa_avg_correlation": 0.2876, "cpa_min_correlation": 0.2627, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_044555_576589.png", "detail_file": "cpa_detail_20260424_044555_576589.json", "per_byte": [{"byte": 0, "key": "0x5A", "correlation": 0.2982, "time_index": 15, "gap_pct": 3.9}, {"byte": 1, "key": "0xB2", "correlation": 0.2732, "time_index": 160, "gap_pct": 1.1}, {"byte": 2, "key": "0xCD", "correlation": 0.2998, "time_index": 155, "gap_pct": 9.4}, {"byte": 3, "key": "0xD2", "correlation": 0.2745, "time_index": 144, "gap_pct": 2.6}, {"byte": 4, "key": "0x55", "correlation": 0.3042, "time_index": 55, "gap_pct": 8.0}, {"byte": 5, "key": "0x67", "correlation": 0.2988, "time_index": 780, "gap_pct": 5.2}, {"byte": 6, "key": "0x49", "correlation": 0.2796, "time_index": 1355, "gap_pct": 3.0}, {"byte": 7, "key": "0x81", "correlation": 0.2627, "time_index": 586, "gap_pct": 2.4}, {"byte": 8, "key": "0xDC", "correlation": 0.2981, "time_index": 1195, "gap_pct": 2.0}, {"byte": 9, "key": "0xD9", "correlation": 0.3194, "time_index": 823, "gap_pct": 9.6}, {"byte": 10, "key": "0x24", "correlation": 0.307, "time_index": 186, "gap_pct": 10.3}, {"byte": 11, "key": "0xCC", "correlation": 0.2821, "time_index": 1022, "gap_pct": 2.1}, {"byte": 12, "key": "0x92", "correlation": 0.2786, "time_index": 1377, "gap_pct": 1.3}, {"byte": 13, "key": "0x39", "correlation": 0.2768, "time_index": 1364, "gap_pct": 1.4}, {"byte": 
...(truncated)
```
</details>


![cpa_result_20260424_044555_576589.png](./cpa_result_20260424_044555_576589.png)


---

### Round 13 | tokens: 30,228→269

**🤖 LLM:** ID模型效果更差。让我尝试对波形进行滤波处理来提高信噪比：

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

<details><summary><b>📋 ← `weighted_moving_average`</b> (1568 chars)</summary>

```
{"out_wave_npy": "smoothed_20260424_044609_878540.npy", "plot_path": "smooth_compare_20260424_044609_878540.png", "n_traces": 250, "n_points": 1500, "weight": 3, "plaintext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy", "ciphertext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"}
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3086010298.py:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy" is not None:
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3086010298.py:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32
...(truncated)
```
</details>


![smooth_compare_20260424_044609_878540.png](./smooth_compare_20260424_044609_878540.png)


---

### Round 14 | tokens: 31,154→145

**🤖 LLM:** 现在在平滑后的波形上进行CPA攻击：

**🔧 → `aes_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "target": "S-box_out",
  "wave_npy": "smoothed_20260424_044609_878540.npy"
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2702 chars)</summary>

```
{"recovered_key": "11F5D6449766770D99AABBCC50EEFF00", "cpa_avg_correlation": 0.3199, "cpa_min_correlation": 0.2585, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_044616_903969.png", "detail_file": "cpa_detail_20260424_044616_903969.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.312, "time_index": 597, "gap_pct": 15.4}, {"byte": 1, "key": "0xF5", "correlation": 0.2585, "time_index": 893, "gap_pct": 1.7}, {"byte": 2, "key": "0xD6", "correlation": 0.3456, "time_index": 494, "gap_pct": 19.1}, {"byte": 3, "key": "0x44", "correlation": 0.3648, "time_index": 1039, "gap_pct": 22.8}, {"byte": 4, "key": "0x97", "correlation": 0.2958, "time_index": 31, "gap_pct": 7.4}, {"byte": 5, "key": "0x66", "correlation": 0.3592, "time_index": 825, "gap_pct": 21.5}, {"byte": 6, "key": "0x77", "correlation": 0.2895, "time_index": 942, "gap_pct": 0.1}, {"byte": 7, "key": "0x0D", "correlation": 0.274, "time_index": 447, "gap_pct": 3.3}, {"byte": 8, "key": "0x99", "correlation": 0.313, "time_index": 611, "gap_pct": 9.1}, {"byte": 9, "key": "0xAA", "correlation": 0.2928, "time_index": 668, "gap_pct": 9.7}, {"byte": 10, "key": "0xBB", "correlation": 0.3673, "time_index": 914, "gap_pct": 27.3}, {"byte": 11, "key": "0xCC", "correlation": 0.3546, "time_index": 1023, "gap_pct": 19.3}, {"byte": 12, "key": "0x50", "correlation": 0.28, "time_index": 36, "gap_pct": 11.0}, {"byte": 13, "key": "0xEE", "correlation": 0.3327, "time_index": 863, "gap_pct": 17.3}, {"byte": 
...(truncated)
```
</details>


![cpa_result_20260424_044616_903969.png](./cpa_result_20260424_044616_903969.png)


---

### Round 15 | tokens: 32,478→234

**🤖 LLM:** 滤波后CPA结果改善！**高置信度字节提升到9/16**（灰色区域）。让我验证这个密钥：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "key_hex": "11F5D6449766770D99AABBCC50EEFF00",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "0E0C9F19784F04E80114CBC4D14A2EF6", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 0E0C9F19784F04E80114CBC4D14A2EF6...\n❌ Key verification FAILED — 16/16 ciphertext bytes differ\n   Expected:  17EAF0DCB9E3BC6F7A83D9F769BFC973\n   Got:       0E0C9F19784F04E80114CBC4D14A2EF6\n\n   ⚠️ IMPORTANT: '16 ciphertext bytes differ' does NOT mean '16 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 16 | tokens: 33,043→289

**🤖 LLM:** 密钥仍不正确，但已进入灰色区域（9/16）。让我使用key_search进行密钥搜索：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "cpa_detail_file": "cpa_detail_20260424_044616_903969.json",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 20,
  "max_combinations": 100000,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "recovered_key_hex": "11F5D6449766770D99AABBCC50EEFF00",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

**📋 ← `key_search`:** `{"found": false, "correct_key": null, "search_rounds": 100000, "unreliable_bytes": [1, 4, 6, 7, 8, 9, 12], "recommended_next_step": "merge_more_cpa_runs_or_rerun_with_higher_candidates", "message": "Not found after 100000 searches."}`


---

### Round 17 | tokens: 33,374→285

**🤖 LLM:** 让我尝试合并两次CPA的结果：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "cpa_detail_file": "cpa_detail_20260424_044616_903969.json",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "extra_cpa_detail_files": [
    "cpa_detail_20260424_044129_670947.json"
  ],
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 30,
  "max_combinations": 200000,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "recovered_key_hex": "11F5D6449766770D99AABBCC50EEFF00"
}
```
</details>

<details><summary><b>📋 ← `key_search`</b> (923 chars)</summary>

```
{"found": false, "correct_key": null, "search_rounds": 200000, "unreliable_bytes": [0, 1, 4, 6, 7, 8, 9, 11, 12], "recommended_next_step": "merge_more_cpa_runs_or_rerun_with_higher_candidates", "message": "Not found after 200000 searches.", "merge_info": {"n_files": 2, "per_unit": [{"byte": 0, "merged_candidates": 25}, {"byte": 1, "merged_candidates": 27}, {"byte": 2, "merged_candidates": 26}, {"byte": 3, "merged_candidates": 24}, {"byte": 4, "merged_candidates": 24}, {"byte": 5, "merged_candidates": 25}, {"byte": 6, "merged_candidates": 24}, {"byte": 7, "merged_candidates": 27}, {"byte": 8, "merged_candidates": 23}, {"byte": 9, "merged_candidates": 25}, {"byte": 10, "merged_candidates": 25}, {"byte": 11, "merged_candidates": 24}, {"byte": 12, "merged_candidates": 29}, {"byte": 13, "merged_candidates": 27}, {"byte": 14, "merged_candidates": 25}, {"byte": 15, "merged_candidates": 22}], "metadata_warnings": []}}
```
</details>


---

### Round 18 | tokens: 33,951→237

**🤖 LLM:** 让我尝试使用更大的滤波权重：

**🔧 → `weighted_moving_average`**

<details><summary>Arguments</summary>

```json
{
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "weight": 2
}
```
</details>

<details><summary><b>📋 ← `weighted_moving_average`</b> (1568 chars)</summary>

```
{"out_wave_npy": "smoothed_20260424_044659_850163.npy", "plot_path": "smooth_compare_20260424_044659_850163.png", "n_traces": 250, "n_points": 1500, "weight": 2, "plaintext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy", "ciphertext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"}
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1079375834.py:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy" is not None:
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1079375834.py:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32
...(truncated)
```
</details>


![smooth_compare_20260424_044659_850163.png](./smooth_compare_20260424_044659_850163.png)


---

### Round 19 | tokens: 34,861→130

**🔧 → `aes_cpa_attack`** `{
  "candidates": 25,
  "leakage_model": "HW",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "target": "S-box_out",
  "wave_npy": "smoothed_20260424_044659_850163.npy"
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2704 chars)</summary>

```
{"recovered_key": "11F5D6449766920D99AABBCC50EEFF00", "cpa_avg_correlation": 0.3187, "cpa_min_correlation": 0.2597, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_044705_912224.png", "detail_file": "cpa_detail_20260424_044705_912224.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3158, "time_index": 597, "gap_pct": 15.1}, {"byte": 1, "key": "0xF5", "correlation": 0.2597, "time_index": 893, "gap_pct": 1.1}, {"byte": 2, "key": "0xD6", "correlation": 0.3465, "time_index": 493, "gap_pct": 19.5}, {"byte": 3, "key": "0x44", "correlation": 0.3609, "time_index": 1038, "gap_pct": 21.1}, {"byte": 4, "key": "0x97", "correlation": 0.2933, "time_index": 30, "gap_pct": 4.2}, {"byte": 5, "key": "0x66", "correlation": 0.3614, "time_index": 825, "gap_pct": 21.7}, {"byte": 6, "key": "0x92", "correlation": 0.2933, "time_index": 93, "gap_pct": 2.0}, {"byte": 7, "key": "0x0D", "correlation": 0.2747, "time_index": 446, "gap_pct": 2.4}, {"byte": 8, "key": "0x99", "correlation": 0.3095, "time_index": 610, "gap_pct": 7.1}, {"byte": 9, "key": "0xAA", "correlation": 0.2876, "time_index": 667, "gap_pct": 8.2}, {"byte": 10, "key": "0xBB", "correlation": 0.3722, "time_index": 914, "gap_pct": 28.8}, {"byte": 11, "key": "0xCC", "correlation": 0.3482, "time_index": 1023, "gap_pct": 15.4}, {"byte": 12, "key": "0x50", "correlation": 0.2737, "time_index": 35, "gap_pct": 6.4}, {"byte": 13, "key": "0xEE", "correlation": 0.3335, "time_index": 863, "gap_pct": 19.2}, {"byte
...(truncated)
```
</details>


![cpa_result_20260424_044705_912224.png](./cpa_result_20260424_044705_912224.png)


---

### Round 20 | tokens: 36,177→316

**🤖 LLM:** 让我合并三次CPA结果进行更全面的密钥搜索：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "cpa_detail_file": "cpa_detail_20260424_044705_912224.json",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "extra_cpa_detail_files": [
    "cpa_detail_20260424_044616_903969.json",
    "cpa_detail_20260424_044129_670947.json"
  ],
  "gap_threshold": 0.12,
  "max_candidates_per_byte": 30,
  "max_combinations": 500000,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "recovered_key_hex": "11F5D6449766920D99AABBCC50EEFF00"
}
```
</details>

<details><summary><b>📋 ← `key_search`</b> (916 chars)</summary>

```
{"found": false, "correct_key": null, "search_rounds": 500000, "unreliable_bytes": [1, 4, 6, 7, 8, 9, 12], "recommended_next_step": "merge_more_cpa_runs_or_rerun_with_higher_candidates", "message": "Not found after 500000 searches.", "merge_info": {"n_files": 3, "per_unit": [{"byte": 0, "merged_candidates": 28}, {"byte": 1, "merged_candidates": 29}, {"byte": 2, "merged_candidates": 31}, {"byte": 3, "merged_candidates": 27}, {"byte": 4, "merged_candidates": 29}, {"byte": 5, "merged_candidates": 28}, {"byte": 6, "merged_candidates": 26}, {"byte": 7, "merged_candidates": 29}, {"byte": 8, "merged_candidates": 26}, {"byte": 9, "merged_candidates": 26}, {"byte": 10, "merged_candidates": 26}, {"byte": 11, "merged_candidates": 28}, {"byte": 12, "merged_candidates": 30}, {"byte": 13, "merged_candidates": 30}, {"byte": 14, "merged_candidates": 26}, {"byte": 15, "merged_candidates": 26}], "metadata_warnings": []}}
```
</details>


---

### Round 21 | tokens: 36,774→291

**🤖 LLM:** 让我尝试使用静态对齐来改善波形质量：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "length": 100,
  "max_shift": 100,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ref_trace": 125,
  "start": 1050,
  "threshold": 85,
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `static_aligner`</b> (782 chars)</summary>

```
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3170713047.py:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
  ref_trace = len(waves) // 2 if 125 is None else int(125)
{"out_aligned_npy": "aligned_20260424_044734_438492.npy", "plot_path": "align_overlay_20260424_044734_438492.png", "ref_trace_used": 125, "accepted": 250, "discarded": 0, "total": 250, "out_plaintext_npy": "plaintext_aligned_20260424_044734_438492.npy", "plaintext_traces": 250, "out_ciphertext_npy": "ciphertext_aligned_20260424_044734_438492.npy", "ciphertext_traces": 250, "alignment_avg_correlation": 0.9893, "alignment_min_correlation": 0.9296, "acceptance_rate": 1.0}
```
</details>


![align_overlay_20260424_044734_438492.png](./align_overlay_20260424_044734_438492.png)


---

### Round 22 | tokens: 37,311→129

**🤖 LLM:** 静态对齐成功！接受率100%。现在在对齐后的波形上进行CPA：

**🔧 → `aes_cpa_attack`** `{
  "candidates": 25,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_044734_438492.npy",
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_044734_438492.npy"
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2052 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.4577, "cpa_min_correlation": 0.3605, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_044741_843583.png", "detail_file": "cpa_detail_20260424_044741_843583.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.5402, "time_index": 1097, "gap_pct": 43.6}, {"byte": 1, "key": "0x22", "correlation": 0.3807, "time_index": 633, "gap_pct": 24.9}, {"byte": 2, "key": "0x33", "correlation": 0.3605, "time_index": 923, "gap_pct": 20.0}, {"byte": 3, "key": "0x44", "correlation": 0.502, "time_index": 1041, "gap_pct": 47.2}, {"byte": 4, "key": "0x55", "correlation": 0.4082, "time_index": 592, "gap_pct": 24.9}, {"byte": 5, "key": "0x66", "correlation": 0.5254, "time_index": 1104, "gap_pct": 45.0}, {"byte": 6, "key": "0x77", "correlation": 0.4779, "time_index": 929, "gap_pct": 39.1}, {"byte": 7, "key": "0x88", "correlation": 0.432, "time_index": 957, "gap_pct": 31.9}, {"byte": 8, "key": "0x99", "correlation": 0.4094, "time_index": 604, "gap_pct": 28.4}, {"byte": 9, "key": "0xAA", "correlation": 0.4631, "time_index": 828, "gap_pct": 36.9}, {"byte": 10, "key": "0xBB", "correlation": 0.4981, "time_index": 1111, "gap_pct": 37.5}, {"byte": 11, "key": "0xCC", "correlation": 0.5029, "time_index": 995, "gap_pct": 41.7}, {"byte": 12, "key": "0xDD", "correlation": 0.3796, "time_index": 614, "gap_pct": 20.3}, {"byte": 13, "key": "0xEE", "correlation": 0.4483, "time_index": 846, "gap_pct": 36.
...(truncated)
```
</details>


![cpa_result_20260424_044741_843583.png](./cpa_result_20260424_044741_843583.png)


---

### Round 23 | tokens: 38,278→272

**🤖 LLM:** **太棒了！** 静态对齐后CPA结果显著改善：
- **恢复密钥**: `112233445566778899AABBCCDDEEFF00`
- **高置信度字节**: **16/16**（绿色区域！）
- **平均相关性**: 0.4577（显著提升）

让我验证这个密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "AES",
  "ciphertext_npy": "ciphertext_aligned_20260424_044734_438492.npy",
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "plaintext_npy": "plaintext_aligned_20260424_044734_438492.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "17EAF0DCB9E3BC6F7A83D9F769BFC973", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 17EAF0DCB9E3BC6F7A83D9F769BFC973...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 24 | tokens: 38,586→463

**🤖 LLM:** ## ✅ **密钥恢复成功！**

**恢复的AES-128密钥**: `112233445566778899AABBCCDDEEFF00`

---

### 📊 **攻击过程总结**

| 步骤 | 操作 | 结果 | 高置信度字节 |
|------|------|------|-------------|
| 1 | 直接CPA（原始波形） | 平均相关性 0.3177 | 6/16（红色区域） |
| 2 | 方差ROI区域CPA | 平均相关性 0.2436 | 1/16（红色区域） |
| 3 | 滤波后CPA（weight=3） | 平均相关性 0.3199 | 9/16（灰色区域） |
| 4 | **静态对齐后CPA** | **平均相关性 0.4577** | **16/16（绿色区域）** ✅ |

---

### 🔑 **关键成功因素**

1. **静态对齐是关键**：在方差峰值区域（1050附近）进行静态对齐后，相关性从0.32提升到0.46，高置信度字节从6/16提升到16/16

2. **方差分析定位加密区域**：通过方差分析准确定位了加密操作区域（1044-1160），为静态对齐提供了正确的参考区域

3. **标准攻击配置有效**：对于STM32F103软件实现，标准的 `S-box_out + HW` 模型完全适用

---

### 📈 **CPA结果详情**

- **所有16个字节的相关性gap都超过15%**，表明密钥恢复非常可靠
- **最高相关性**: 字节0 (0x11) - 0.5402
- **最低相关性**: 字节2 (0x33) - 0.3605
- **平均相关性**: 0.4577

攻击成功完成！🎉


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 17,280 | 1,131 | 18,411 |
| 2 | 18,289 | 365 | 18,654 |
| 3 | 19,871 | 540 | 20,411 |
| 4 | 20,488 | 1,141 | 21,629 |
| 5 | 21,707 | 396 | 22,103 |
| 6 | 22,077 | 553 | 22,630 |
| 7 | 22,524 | 77 | 22,601 |
| 8 | 24,140 | 987 | 25,127 |
| 9 | 25,074 | 2,250 | 27,324 |
| 10 | 27,733 | 443 | 28,176 |
| 11 | 28,099 | 320 | 28,419 |
| 12 | 28,449 | 215 | 28,664 |
| 13 | 30,228 | 269 | 30,497 |
| 14 | 31,154 | 145 | 31,299 |
| 15 | 32,478 | 234 | 32,712 |
| 16 | 33,043 | 289 | 33,332 |
| 17 | 33,374 | 285 | 33,659 |
| 18 | 33,951 | 237 | 34,188 |
| 19 | 34,861 | 130 | 34,991 |
| 20 | 36,177 | 316 | 36,493 |
| 21 | 36,774 | 291 | 37,065 |
| 22 | 37,311 | 129 | 37,440 |
| 23 | 38,278 | 272 | 38,550 |
| 24 | 38,586 | 463 | 39,049 |
| **Total** | **691,946** | **11,478** | **703,424** |

## 8. Final Output

## ✅ **密钥恢复成功！**

**恢复的AES-128密钥**: `112233445566778899AABBCCDDEEFF00`

---

### 📊 **攻击过程总结**

| 步骤 | 操作 | 结果 | 高置信度字节 |
|------|------|------|-------------|
| 1 | 直接CPA（原始波形） | 平均相关性 0.3177 | 6/16（红色区域） |
| 2 | 方差ROI区域CPA | 平均相关性 0.2436 | 1/16（红色区域） |
| 3 | 滤波后CPA（weight=3） | 平均相关性 0.3199 | 9/16（灰色区域） |
| 4 | **静态对齐后CPA** | **平均相关性 0.4577** | **16/16（绿色区域）** ✅ |

---

### 🔑 **关键成功因素**

1. **静态对齐是关键**：在方差峰值区域（1050附近）进行静态对齐后，相关性从0.32提升到0.46，高置信度字节从6/16提升到16/16

2. **方差分析定位加密区域**：通过方差分析准确定位了加密操作区域（1044-1160），为静态对齐提供了正确的参考区域

3. **标准攻击配置有效**：对于STM32F103软件实现，标准的 `S-box_out + HW` 模型完全适用

---

### 📈 **CPA结果详情**

- **所有16个字节的相关性gap都超过15%**，表明密钥恢复非常可靠
- **最高相关性**: 字节0 (0x11) - 0.5402
- **最低相关性**: 字节2 (0x33) - 0.3605
- **平均相关性**: 0.4577

攻击成功完成！🎉
