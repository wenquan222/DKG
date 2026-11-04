# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_040139_954 |
| Duration | 164.3s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-STM32F429_GLM5_DKG_20260424_040139_954` |
| Total LLM Calls | 12 |
| First Round | prompt: 16,060, completion: 742 |
| Last Round | prompt: 28,010, completion: 1,077 |
| Total Tokens | 262,965 (prompt: 254,415, completion: 8,550) |

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
["AES", "STM32F429", "MCU", "EM", "CPA", "Hamming Weight", "S-box Output"]

Parsed Keywords: `["AES", "STM32F429", "MCU", "EM", "CPA", "Hamming Weight", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 38523 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (40781 chars, click to expand)</summary>

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

**Search keywords** (7): AES, STM32F429, MCU, EM, CPA, Hamming Weight, S-box Output

**Summary**: 41 upper entities, 34 relationships, 14 diagnostic chains, 12 strategies


## 1. Upper Layer Entities (41)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### AttackPoint (6)

- **Inverse S-box Output** — round=13
- **Masked S-box Output**
- **S-box Output** — required_data=ciphertext, round=last
- **S-box Output and Mask** — required_data=plaintext, round=first
- **S-box output** — round=1
- **S-box outputs** — round=first

### DeviceClass (14)

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

## 2. Relationships (34)

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
- `StatMethod:Generate Hamming weight models for S-box output` —[consists_of [parameters_note=models are lookup tables for the leakage of each possible S-box output, source_text=Generate Hamming weight models for S-box output, support_count=1, is_optional=False]]→ `Pipeline:SCALib CPA Attack on AES`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Avoid using the identity model for bijective S-boxes in MIA; use a non-bijective model (e.g., Hamming weight) or target a non-bijective intermediate value (e.g., predict only a subset of bits).`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:try different power models (bit, Hamming weight, Hamming distance, zero-value) to see which yields the highest and most distinct peak for a single key hypothesis`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:use the Hamming weight model for microcontrollers with precharged buses`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Use a non-injective leakage function that incurs information loss (e.g., Hamming weight, LSB, MSB).`
- `AttackPoint:S-box Output` —[strategy_applies_to [source=round1_patch_001, condition=Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear, applicability=specific]]→ `Strategy:Do NOT switch leakage target family as first response to low correlation on software implementations`
- `AttackPoint:Inverse S-box Output` —[has_attack_point [source_text=attack_point: Inverse S-box Output, round: 14, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[has_attack_point [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[works_with [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`

## 3. Diagnostic Chains (14)


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

### Obs: `leakage_model_selection` — any
- **Cause** (high): Non-linear operations (e.g., S-box) have stronger power consumption leakage than linear transformations
- **Check**: Compare correlation strength between S-box output and linear operation points
- **Action**: Choose S-box output as intermediate value for CPA or machine learning attacks
  - operation: `switch_component`
  - target: `intermediate_value`
  - strategy: Choose the S-box output (the value after XOR with round key and before linear transformation) as the intermediate value for CPA or machine learning attacks.
- **Relates to**: AttackPoint:`S-box Output`

## 4. Strategies (12)


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

### ⭐ ⚠ [anti_pattern_set] alignment max_shift should start large (300+), not default to small
- **Trigger**: Any static_aligner invocation on smartcard / MCU traces
- **Rationale**: From expert_experience.md L223-224: 宁可大一些也不要太小
- **Anti-pattern 1**: Set max_shift=80 or 100 on first alignment attempt; when acceptance_rate < 90%, switch alignment method instead of enlarging max_shift.
  - Why: Smartcard waveform offsets routinely reach 300-500 sample points due to I/O jitter and card clock drift. max_shift too small causes >50% of traces to be discarded, and the surviving subset may not capture the real peak offset.
  - Correct: Initial max_shift: at least 300 (smartcard), 150-200 (MCU with stable clock). If acceptance_rate < 90%, FIRST double max_shift (300→600→1000) before considering alternate alignment methods. max_shift too large only costs a bit of compute, max_shift too small costs valid traces permanently.
- **Applies to**: Preprocessing:Static Alignment

### ⭐ ⚠ [anti_pattern_set] Do NOT treat alignment_avg_correlation as a CPA success metric
- **Trigger**: Any time an alignment tool returns alignment_avg_correlation >= 0.9
- **Rationale**: From expert_experience.md L144/L601: 攻击成败看 gap_pct/high_confidence_count，不要用 alignment_avg_correlation 代替
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
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-STM32F429_GLM5_DKG_20260424_040139_954
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-STM32F429_GLM5_DKG_20260424_040139_954/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 16,060→742

**🤖 LLM:** 我来帮你对STM32F429 MCU的AES电磁侧信道波形进行CPA攻击。让我按照标准的SCA分析流程进行。

## 第一步：加载并可视化波形数据

首先，让我加载波形数据并观察其特征，判断实现原型和是否需要预处理。

**🔧 → `python_jupyter`**

<details><summary>Code (1110 chars)</summary>

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

# 可视化前5条trace
plt.figure(figsize=(14, 8))
for i in range(5):
    plt.plot(wave[i] + i*0.1, alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude (offset for clarity)')
plt.title('STM32F429 AES-128 EM Traces (First 5 traces)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('waveform_overview.png', dpi=150)
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (1000, 1000)
明文数据形状: (1000, 16)
密文数据形状: (1000, 16)

波形数据范围: [0.0000, 125000.0000]
波形均值: 25611.7031
波形标准差: 16987.9805
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3666611910.py:27: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 2 | tokens: 16,694→640

**🔧 → `python_jupyter`**

<details><summary>Code (1501 chars)</summary>

```python
# 分析波形特征
# 1. 计算每个采样点的方差（找加密区域）
variance = np.var(wave, axis=0)

# 2. 计算基线漂移（检查是否需要垂直对齐）
baseline_means = np.mean(wave[:, :50], axis=1)  # 前50个点的均值作为基线
baseline_std = np.std(baseline_means)
print(f"基线均值范围: [{baseline_means.min():.2f}, {baseline_means.max():.2f}]")
print(f"基线均值标准差: {baseline_std:.2f}")

# 3. 检查trace之间的对齐情况
plt.figure(figsize=(15, 10))

# 子图1：方差分析
plt.subplot(2, 2, 1)
plt.plot(variance)
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.title('Variance Across All Traces')
plt.grid(True, alpha=0.3)

# 子图2：基线分布
plt.subplot(2, 2, 2)
plt.hist(baseline_means, bins=30, edgecolor='black', alpha=0.7)
plt.xlabel('Baseline Mean (first 50 samples)')
plt.ylabel('Count')
plt.title(f'Baseline Distribution (std={baseline_std:.2f})')
plt.grid(True, alpha=0.3)

# 子图3：叠加显示多条trace（检查对齐）
plt.subplot(2, 2, 3)
for i in range(20):
    plt.plot(wave[i], alpha=0.3, linewidth=0.5)
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.title('20 Traces Overlay (Check Alignment)')
plt.grid(True, alpha=0.3)

# 子图4：平均trace
plt.subplot(2, 2, 4)
mean_trace = np.mean(wave, axis=0)
plt.plot(mean_trace)
plt.xlabel('Sample Point')
plt.ylabel('Mean Amplitude')
plt.title('Average Trace')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

# 找方差最大的区域（可能的加密区域）
top_variance_idx = np.argsort(variance)[-20:][::-1]
print(f"\n方差最大的20个采样点: {sorted(top_variance_idx)}")
print(f"方差峰值区域: {np.argmax(variance)} (variance={variance[np.argmax(variance)]:.2f})")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (547 chars)</summary>

```
基线均值范围: [19370.00, 28660.00]
基线均值标准差: 2457.50

方差最大的20个采样点: [np.int64(7), np.int64(8), np.int64(9), np.int64(274), np.int64(277), np.int64(404), np.int64(413), np.int64(432), np.int64(445), np.int64(460), np.int64(462), np.int64(488), np.int64(586), np.int64(745), np.int64(785), np.int64(787), np.int64(793), np.int64(795), np.int64(922), np.int64(999)]
方差峰值区域: 9 (variance=1007727296.00)
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1966990294.py:50: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 3 | tokens: 17,487→731

**🔧 → `python_jupyter`**

<details><summary>Code (1361 chars)</summary>

```python
# 更详细地分析波形结构
# 查看平均trace的特征
mean_trace = np.mean(wave, axis=0)

# 寻找可能的加密区域（通过方差和能量特征）
# 使用滑动窗口计算局部方差
window_size = 50
local_var = []
for i in range(0, len(variance) - window_size, 10):
    local_var.append((i, np.mean(variance[i:i+window_size])))

local_var = np.array(local_var)

# 找到方差较高的区域
high_var_regions = local_var[local_var[:, 1] > np.percentile(local_var[:, 1], 75)]
print("高方差区域（可能为加密区域）:")
for start, var_val in high_var_regions[:10]:
    print(f"  起始点 {int(start)}, 平均方差 {var_val:.2f}")

# 绘制更详细的分析图
plt.figure(figsize=(15, 8))

plt.subplot(2, 1, 1)
plt.plot(mean_trace, label='Mean Trace', linewidth=1.5)
plt.xlabel('Sample Point')
plt.ylabel('Mean Amplitude')
plt.title('Mean Trace with High-Variance Regions Highlighted')
plt.grid(True, alpha=0.3)

# 标记高方差区域
for start, var_val in high_var_regions[:5]:
    plt.axvspan(start, start + window_size, alpha=0.2, color='red')

plt.subplot(2, 1, 2)
plt.plot(variance, label='Variance', linewidth=1.5)
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.title('Variance Distribution')
plt.grid(True, alpha=0.3)

# 标记高方差区域
for start, var_val in high_var_regions[:5]:
    plt.axvspan(start, start + window_size, alpha=0.2, color='red')

plt.tight_layout()
plt.savefig('variance_analysis.png', dpi=150)
plt.show()

print(f"\n建议：波形长度1000点，可能已经预裁剪到加密区域附近")
print(f"基线漂移标准差 {baseline_std:.2f} 较大，可能需要垂直对齐")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (516 chars)</summary>

```
高方差区域（可能为加密区域）:
  起始点 40, 平均方差 236978480.00
  起始点 50, 平均方差 242571104.00
  起始点 70, 平均方差 239189264.00
  起始点 110, 平均方差 237126096.00
  起始点 120, 平均方差 244524928.00
  起始点 130, 平均方差 243285584.00
  起始点 140, 平均方差 247944608.00
  起始点 750, 平均方差 252827872.00
  起始点 760, 平均方差 247394432.00
  起始点 770, 平均方差 253987616.00

建议：波形长度1000点，可能已经预裁剪到加密区域附近
基线漂移标准差 2457.50 较大，可能需要垂直对齐
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\171611279.py:47: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 4 | tokens: 18,279→423

**🤖 LLM:** ## 第二步：直接CPA攻击（无预处理）

根据KG知识，STM32F429是MCU软件实现，应该使用**S-box_out + HW模型**。让我先进行直接CPA攻击，评估是否需要预处理。

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
{"recovered_key": "00112233445566778899AABBCCDDEEFF", "cpa_avg_correlation": 0.5644, "cpa_min_correlation": 0.4463, "n_traces": 1000, "target": "S-box_out", "plot_path": "cpa_result_20260424_040258_296856.png", "detail_file": "cpa_detail_20260424_040258_296856.json", "per_byte": [{"byte": 0, "key": "0x00", "correlation": 0.4463, "time_index": 353, "gap_pct": 65.4}, {"byte": 1, "key": "0x11", "correlation": 0.5536, "time_index": 364, "gap_pct": 65.4}, {"byte": 2, "key": "0x22", "correlation": 0.5321, "time_index": 418, "gap_pct": 69.9}, {"byte": 3, "key": "0x33", "correlation": 0.5563, "time_index": 385, "gap_pct": 66.8}, {"byte": 4, "key": "0x44", "correlation": 0.5662, "time_index": 356, "gap_pct": 67.7}, {"byte": 5, "key": "0x55", "correlation": 0.5341, "time_index": 366, "gap_pct": 69.6}, {"byte": 6, "key": "0x66", "correlation": 0.5802, "time_index": 377, "gap_pct": 69.5}, {"byte": 7, "key": "0x77", "correlation": 0.5952, "time_index": 387, "gap_pct": 68.4}, {"byte": 8, "key": "0x88", "correlation": 0.6141, "time_index": 358, "gap_pct": 66.5}, {"byte": 9, "key": "0x99", "correlation": 0.4875, "time_index": 368, "gap_pct": 71.4}, {"byte": 10, "key": "0xAA", "correlation": 0.6308, "time_index": 379, "gap_pct": 73.6}, {"byte": 11, "key": "0xBB", "correlation": 0.5474, "time_index": 390, "gap_pct": 68.3}, {"byte": 12, "key": "0xCC", "correlation": 0.6539, "time_index": 360, "gap_pct": 72.5}, {"byte": 13, "key": "0xDD", "correlation": 0.618, "time_index": 371, "gap_pct": 70.4}
...(truncated)
```
</details>


![cpa_result_20260424_040258_296856.png](./cpa_result_20260424_040258_296856.png)


---

### Round 5 | tokens: 19,369→359

**🤖 LLM:** ## 第三步：验证恢复的密钥

CPA攻击非常成功！让我验证恢复的密钥是否正确。

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

### Round 6 | tokens: 19,706→1,010

**🤖 LLM:** ## ✅ 攻击成功！

让我生成最终的分析报告：

**🔧 → `python_jupyter`**

<details><summary>Code (1524 chars)</summary>

```python
import json

# 读取CPA详细结果
with open('cpa_detail_20260424_040258_296856.json', 'r') as f:
    cpa_detail = json.load(f)

# 生成最终报告
print("=" * 80)
print("STM32F429 AES-128 电磁侧信道CPA攻击报告")
print("=" * 80)

print("\n【攻击配置】")
print(f"  算法: AES-128")
print(f"  设备: STM32F429 MCU (32-bit ARM Cortex-M4)")
print(f"  侧信道类型: 电磁 (EM)")
print(f"  实现类型: 软件")
print(f"  攻击目标: S-box Output (第一轮)")
print(f"  泄漏模型: Hamming Weight (HW)")
print(f"  迹数: 1000 traces")
print(f"  采样点: 1000 points")

print("\n【攻击结果】")
print(f"  ✅ 恢复密钥: 00112233445566778899AABBCCDDEEFF")
print(f"  ✅ 验证状态: MATCH (密钥正确)")
print(f"  平均相关系数: 0.5644")
print(f"  最小相关系数: 0.4463")
print(f"  高置信度字节: 16/16 (100%)")

print("\n【各字节详情】")
print(f"{'字节':<6} {'密钥':<6} {'相关系数':<12} {'时间点':<10} {'Gap%':<10}")
print("-" * 50)
for byte_info in cpa_detail['per_byte']:
    print(f"{byte_info['byte']:<6} {byte_info['key']:<6} {byte_info['correlation']:<12.4f} {byte_info['time_index']:<10} {byte_info['gap_pct']:<10.1f}")

print("\n【分析总结】")
print("  1. 攻击非常成功，无需任何预处理（无对齐、无滤波）")
print("  2. STM32F429软件实现的S-box输出在HW模型下泄漏强烈")
print("  3. 电磁侧信道测量质量高，信噪比优秀")
print("  4. 1000条迹数完全足够恢复全部16字节密钥")
print("  5. 所有字节的相关系数均 > 0.44，gap > 65%，置信度极高")

print("\n【泄漏时间点分析】")
time_indices = [byte_info['time_index'] for byte_info in cpa_detail['per_byte']]
print(f"  泄漏时间范围: {min(time_indices)} - {max(time_indices)}")
print(f"  平均泄漏时间: {np.mean(time_indices):.1f}")
print(f"  时间跨度: {max(time_indices) - min(time_indices)} 采样点")
print(f"  这表明S-box操作在约350-420采样点范围内顺序执行")

print("\n" + "=" * 80)
```
</details>

**❌ ← `python_jupyter` Error:**

```
================================================================================
STM32F429 AES-128 电磁侧信道CPA攻击报告
================================================================================

【攻击配置】
  算法: AES-128
  设备: STM32F429 MCU (32-bit ARM Cortex-M4)
  侧信道类型: 电磁 (EM)
  实现类型: 软件
  攻击目标: S-box Output (第一轮)
  泄漏模型: Hamming Weight (HW)
  迹数: 1000 traces
  采样点: 1000 points

【攻击结果】
  ✅ 恢复密钥: 00112233445566778899AABBCCDDEEFF
  ✅ 验证状态: MATCH (密钥正确)
  平均相关系数: 0.5644
  最小相关系数: 0.4463
  高置信度字节: 16/16 (100%)

【各字节详情】
字节     密钥     相关系数         时间点        Gap%      
--------------------------------------------------

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[138][39m[32m, line 32[39m
[32m     30[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;132;01m{[39;00m[33m'[39m[33m字节[39m[33m'[39m[38;5;132;01m:[39;00m[33m<6[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00m[33m'[39m[33m密钥[39m[33m'[39m[38;5;132;01m:[39;00m[33m<6[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00m[33m'[39m[33m相关系数[39m[33m'[39m[38;5;132;01m:[39;00m[33m<12[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00m[33m'[39m[33m时间点[39m[33m'[39m[38;5;132;01m:[39;00m[33m<10[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00m[33m'[39m[33mGap[39m[33m%[39m[33m'[39m[38;5;132;01m:[39;00m[33m<10[39m[38;5;132;01m}[39;00m[33m"[39m)
[32m     31[39m [38;5;28mprint[39m([33m"[39m[33m-[39m[33m"[39m * [32m50[39m)
[32m---> [39m[32m32[39m [38;5;28;01mfor[39;00m byte_info [38;5;129;01min[39;00m [43mcpa_detail[49m[43m[[49m[33;43m'[39;49m[33;43mper_byte[39;49m[33;43m'[39;49m[43m][49m:
[32m     33[39m     [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;132;01m{[39;00mbyte_info[[33m'[39m[33mbyte[39m[33m'[39m][38;5;132;01m:[39;00m[33m<6[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00mbyte_info[[33m'[39m[33mkey[39m[33m'[39m][38;5;132;01m:[39;00m[33m<6[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00mbyte_info[[33m'[39m[33mcorrelation[39m[33m'[39m][38;5;132;01m:[39;00m[33m<12.4f[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00mbyte_info[[33m'[39m[33mtime_index[39m[33m'[39m][38;5;132;01m:[39;00m[33m<10[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00mbyte_info[[33m'[39m[33mgap_pct[39m[33m'[39m][38;5;132;01m:[39;00m[33m<10.1f[39m[38;5;132;01m}[39;00m[33m"[39m)
[32m     35[39m [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33m【分析总结】[39m[33m"[39m)

[31mKeyError[39m: 'per_byte'
```


---

### Round 7 | tokens: 21,863→125

**🔧 → `python_jupyter`**

<details><summary>Code (277 chars)</summary>

```python
import json

# 读取CPA详细结果
with open('cpa_detail_20260424_040258_296856.json', 'r') as f:
    cpa_detail = json.load(f)

# 检查JSON结构
print("JSON keys:", cpa_detail.keys())
print("\nFirst few entries:")
for key in list(cpa_detail.keys())[:3]:
    print(f"{key}: {cpa_detail[key]}")
```
</details>

**📋 ← `python_jupyter`:** `JSON keys: dict_keys(['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results'])

First few entries:
n_traces: 1000
n_points: 1000
leakage_model: HW`


---

### Round 8 | tokens: 22,032→706

**🔧 → `python_jupyter`**

<details><summary>Code (1533 chars)</summary>

```python
import json
import numpy as np

# 读取CPA详细结果
with open('cpa_detail_20260424_040258_296856.json', 'r') as f:
    cpa_detail = json.load(f)

# 生成最终报告
print("=" * 80)
print("STM32F429 AES-128 电磁侧信道CPA攻击报告")
print("=" * 80)

print("\n【攻击配置】")
print(f"  算法: AES-128")
print(f"  设备: STM32F429 MCU (32-bit ARM Cortex-M4)")
print(f"  侧信道类型: 电磁 (EM)")
print(f"  实现类型: 软件")
print(f"  攻击目标: S-box Output (第一轮)")
print(f"  泄漏模型: Hamming Weight (HW)")
print(f"  迹数: 1000 traces")
print(f"  采样点: 1000 points")

print("\n【攻击结果】")
print(f"  ✅ 恢复密钥: 00112233445566778899AABBCCDDEEFF")
print(f"  ✅ 验证状态: MATCH (密钥正确)")
print(f"  平均相关系数: 0.5644")
print(f"  最小相关系数: 0.4463")
print(f"  高置信度字节: 16/16 (100%)")

print("\n【各字节详情】")
print(f"{'字节':<6} {'密钥':<6} {'相关系数':<12} {'时间点':<10} {'Gap%':<10}")
print("-" * 50)
for byte_idx, result in enumerate(cpa_detail['results']):
    print(f"{byte_idx:<6} {result['best_key']:<6} {result['best_corr']:<12.4f} {result['best_time']:<10} {result['gap_pct']:<10.1f}")

print("\n【分析总结】")
print("  1. 攻击非常成功，无需任何预处理（无对齐、无滤波）")
print("  2. STM32F429软件实现的S-box输出在HW模型下泄漏强烈")
print("  3. 电磁侧信道测量质量高，信噪比优秀")
print("  4. 1000条迹数完全足够恢复全部16字节密钥")
print("  5. 所有字节的相关系数均 > 0.44，gap > 65%，置信度极高")

print("\n【泄漏时间点分析】")
time_indices = [result['best_time'] for result in cpa_detail['results']]
print(f"  泄漏时间范围: {min(time_indices)} - {max(time_indices)}")
print(f"  平均泄漏时间: {np.mean(time_indices):.1f}")
print(f"  时间跨度: {max(time_indices) - min(time_indices)} 采样点")
print(f"  这表明S-box操作在约350-420采样点范围内顺序执行")

print("\n" + "=" * 80)
```
</details>

**❌ ← `python_jupyter` Error:**

```
================================================================================
STM32F429 AES-128 电磁侧信道CPA攻击报告
================================================================================

【攻击配置】
  算法: AES-128
  设备: STM32F429 MCU (32-bit ARM Cortex-M4)
  侧信道类型: 电磁 (EM)
  实现类型: 软件
  攻击目标: S-box Output (第一轮)
  泄漏模型: Hamming Weight (HW)
  迹数: 1000 traces
  采样点: 1000 points

【攻击结果】
  ✅ 恢复密钥: 00112233445566778899AABBCCDDEEFF
  ✅ 验证状态: MATCH (密钥正确)
  平均相关系数: 0.5644
  最小相关系数: 0.4463
  高置信度字节: 16/16 (100%)

【各字节详情】
字节     密钥     相关系数         时间点        Gap%      
--------------------------------------------------

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[140][39m[32m, line 34[39m
[32m     32[39m [38;5;28mprint[39m([33m"[39m[33m-[39m[33m"[39m * [32m50[39m)
[32m     33[39m [38;5;28;01mfor[39;00m byte_idx, result [38;5;129;01min[39;00m [38;5;28menumerate[39m(cpa_detail[[33m'[39m[33mresults[39m[33m'[39m]):
[32m---> [39m[32m34[39m     [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;132;01m{[39;00mbyte_idx[38;5;132;01m:[39;00m[33m<6[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00mresult[[33m'[39m[33mbest_key[39m[33m'[39m][38;5;132;01m:[39;00m[33m<6[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00m[43mresult[49m[43m[[49m[33;43m'[39;49m[33;43mbest_corr[39;49m[33;43m'[39;49m[43m][49m[38;5;132;01m:[39;00m[33m<12.4f[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00mresult[[33m'[39m[33mbest_time[39m[33m'[39m][38;5;132;01m:[39;00m[33m<10[39m[38;5;132;01m}[39;00m[33m [39m[38;5;132;01m{[39;00mresult[[33m'[39m[33mgap_pct[39m[33m'[39m][38;5;132;01m:[39;00m[33m<10.1f[39m[38;5;132;01m}[39;00m[33m"[39m)
[32m     36[39m [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33m【分析总结】[39m[33m"[39m)
[32m     37[39m [38;5;28mprint[39m([33m"[39m[33m  1. 攻击非常成功，无需任何预处理（无对齐、无滤波）[39m[33m"[39m)

[31mKeyError[39m: 'best_corr'
```


---

### Round 9 | tokens: 23,773→132

**🔧 → `python_jupyter`**

<details><summary>Code (336 chars)</summary>

```python
import json

# 读取CPA详细结果
with open('cpa_detail_20260424_040258_296856.json', 'r') as f:
    cpa_detail = json.load(f)

# 检查results结构
print("Results structure:")
print(f"Number of results: {len(cpa_detail['results'])}")
print(f"\nFirst result keys: {cpa_detail['results'][0].keys()}")
print(f"\nFirst result: {cpa_detail['results'][0]}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1395 chars)</summary>

```
Results structure:
Number of results: 16

First result keys: dict_keys(['byte', 'topK', 'best_key'])

First result: {'byte': 0, 'topK': [{'key': 0, 'score': 0.44629811883424253, 'time_index': 353}, {'key': 242, 'score': 0.1546028704302906, 'time_index': 273}, {'key': 208, 'score': 0.1545939431494346, 'time_index': 273}, {'key': 43, 'score': 0.1486571681475202, 'time_index': 273}, {'key': 73, 'score': 0.14552869749166195, 'time_index': 273}, {'key': 79, 'score': 0.142323953265494, 'time_index': 273}, {'key': 63, 'score': 0.13970734467914486, 'time_index': 353}, {'key': 180, 'score': 0.1379288170805279, 'time_index': 274}, {'key': 228, 'score': 0.13666103297834875, 'time_index': 312}, {'key': 25, 'score': 0.13613444714692044, 'time_index': 47}, {'key': 45, 'score': 0.13520316251505998, 'time_index': 273}, {'key': 184, 'score': 0.13242372994030321, 'time_index': 353}, {'key': 127, 'score': 0.12816513863090245, 'time_index': 668}, {'key': 18, 'score': 0.12796388511100779, 'time_index': 354}, {'key': 178, 'score': 0.12633462779687324, 'time_index': 273}, {'key': 150, 'score': 0.12503543988584156, 'time_index': 273}, {'key': 216, 'score': 0.12481893560839008, 'time_index': 444}, {'key': 235, 'score': 0.12465302343762746, 'time_index': 199}, {'key': 105, 'score': 0.1243338567906056, 'time_index': 459}, {'key': 117, 'score': 0.12424679799542979, 'time_index': 353}], 'best_key': 0}
```
</details>


---

### Round 10 | tokens: 24,550→1,237

**🔧 → `python_jupyter`**

<details><summary>Code (2270 chars)</summary>

```python
import json
import numpy as np

# 读取CPA详细结果
with open('cpa_detail_20260424_040258_296856.json', 'r') as f:
    cpa_detail = json.load(f)

# 生成最终报告
print("=" * 80)
print("STM32F429 AES-128 电磁侧信道CPA攻击报告")
print("=" * 80)

print("\n【攻击配置】")
print(f"  算法: AES-128")
print(f"  设备: STM32F429 MCU (32-bit ARM Cortex-M4)")
print(f"  侧信道类型: 电磁 (EM)")
print(f"  实现类型: 软件")
print(f"  攻击目标: S-box Output (第一轮)")
print(f"  泄漏模型: Hamming Weight (HW)")
print(f"  迹数: 1000 traces")
print(f"  采样点: 1000 points")

print("\n【攻击结果】")
print(f"  ✅ 恢复密钥: 00112233445566778899AABBCCDDEEFF")
print(f"  ✅ 验证状态: MATCH (密钥正确)")
print(f"  平均相关系数: 0.5644")
print(f"  最小相关系数: 0.4463")
print(f"  高置信度字节: 16/16 (100%)")

print("\n【各字节详情】")
print(f"{'字节':<6} {'密钥':<8} {'相关系数':<12} {'时间点':<10} {'Gap%':<10}")
print("-" * 50)

# 从CPA工具返回的结果中提取信息
per_byte_data = [
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

for byte_idx, key, corr, time_idx, gap in per_byte_data:
    print(f"{byte_idx:<6} {key:<8} {corr:<12.4f} {time_idx:<10} {gap:<10.1f}")

print("\n【分析总结】")
print("  1. 攻击非常成功，无需任何预处理（无对齐、无滤波）")
print("  2. STM32F429软件实现的S-box输出在HW模型下泄漏强烈")
print("  3. 电磁侧信道测量质量高，信噪比优秀")
print("  4. 1000条迹数完全足够恢复全部16字节密钥")
print("  5. 所有字节的相关系数均 > 0.44，gap > 65%，置信度极高")

print("\n【泄漏时间点分析】")
time_indices = [data[3] for data in per_byte_data]
print(f"  泄漏时间范围: {min(time_indices)} - {max(time_indices)}")
print(f"  平均泄漏时间: {np.mean(time_indices):.1f}")
print(f"  时间跨度: {max(time_indices) - min(time_indices)} 采样点")
print(f"  这表明S-box操作在约350-420采样点范围内顺序执行")

print("\n【关键发现】")
print("  • 字节12 (0xCC) 相关系数最高 (0.6539)，泄漏最强")
print("  • 字节0 (0x00) 相关系数最低 (0.4463)，但仍远超阈值")
print("  • 所有字节的gap > 65%，说明正确密钥与次优候选区分明显")
print("  • 无需静态对齐、垂直对齐或滤波，直接CPA即可成功")

print("\n" + "=" * 80)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1920 chars)</summary>

```
================================================================================
STM32F429 AES-128 电磁侧信道CPA攻击报告
================================================================================

【攻击配置】
  算法: AES-128
  设备: STM32F429 MCU (32-bit ARM Cortex-M4)
  侧信道类型: 电磁 (EM)
  实现类型: 软件
  攻击目标: S-box Output (第一轮)
  泄漏模型: Hamming Weight (HW)
  迹数: 1000 traces
  采样点: 1000 points

【攻击结果】
  ✅ 恢复密钥: 00112233445566778899AABBCCDDEEFF
  ✅ 验证状态: MATCH (密钥正确)
  平均相关系数: 0.5644
  最小相关系数: 0.4463
  高置信度字节: 16/16 (100%)

【各字节详情】
字节     密钥       相关系数         时间点        Gap%      
--------------------------------------------------
0      0x00     0.4463       353        65.4      
1      0x11     0.5536       364        65.4      
2      0x22     0.5321       418        69.9      
3      0x33     0.5563       385        66.8      
4      0x44     0.5662       356        67.7      
5      0x55     0.5341       366        69.6      
6      0x66     0.5802       377        69.5      
7      0x77     0.5952       387        68.4      
8      0x88     0.6141       358        66.5      
9      0x99     0.4875       368        71.4      
10     0xAA     0.6308       379        73.6      
11     0xBB     0.5474       390        68.3      
12     0xCC     0.6539       360        72.5      
13     0xDD     0.6180       371        70.4      
14     0xEE     0.5513       381        67.3      
15     0xFF     0.5640       392        71.3      

【分析总结】
  1. 攻击非常成功，无需任何预处理（无对齐、无滤波）
  2. STM32F429软件实现的S-box输出在
...(truncated)
```
</details>


---

### Round 11 | tokens: 26,592→1,368

**🔧 → `python_jupyter`**

<details><summary>Code (3389 chars)</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

# 创建综合可视化
fig = plt.figure(figsize=(16, 12))

# 子图1：相关系数分布
ax1 = plt.subplot(2, 3, 1)
correlations = [0.4463, 0.5536, 0.5321, 0.5563, 0.5662, 0.5341, 0.5802, 0.5952, 
                0.6141, 0.4875, 0.6308, 0.5474, 0.6539, 0.618, 0.5513, 0.564]
byte_indices = list(range(16))
colors = ['green' if c > 0.5 else 'orange' for c in correlations]
bars = ax1.bar(byte_indices, correlations, color=colors, edgecolor='black', alpha=0.7)
ax1.axhline(y=0.5, color='red', linestyle='--', label='Threshold (0.5)')
ax1.set_xlabel('Byte Index')
ax1.set_ylabel('Correlation Coefficient')
ax1.set_title('CPA Correlation per Byte')
ax1.set_ylim([0, 0.7])
ax1.legend()
ax1.grid(True, alpha=0.3)

# 子图2：Gap百分比分布
ax2 = plt.subplot(2, 3, 2)
gaps = [65.4, 65.4, 69.9, 66.8, 67.7, 69.6, 69.5, 68.4, 66.5, 71.4, 73.6, 68.3, 72.5, 70.4, 67.3, 71.3]
ax2.bar(byte_indices, gaps, color='steelblue', edgecolor='black', alpha=0.7)
ax2.axhline(y=15, color='red', linestyle='--', label='Threshold (15%)')
ax2.set_xlabel('Byte Index')
ax2.set_ylabel('Gap Percentage (%)')
ax2.set_title('Gap Between Best and Second Best Key')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 子图3：泄漏时间点分布
ax3 = plt.subplot(2, 3, 3)
time_points = [353, 364, 418, 385, 356, 366, 377, 387, 358, 368, 379, 390, 360, 371, 381, 392]
ax3.scatter(time_points, correlations, s=100, c=correlations, cmap='RdYlGn', edgecolors='black', alpha=0.7)
ax3.set_xlabel('Time Index (Sample Point)')
ax3.set_ylabel('Correlation Coefficient')
ax3.set_title('Leakage Time vs Correlation')
ax3.grid(True, alpha=0.3)
cbar = plt.colorbar(ax3.collections[0], ax=ax3)
cbar.set_label('Correlation')

# 子图4：恢复的密钥可视化
ax4 = plt.subplot(2, 3, 4)
key_bytes = [0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
ax4.bar(byte_indices, key_bytes, color='purple', edgecolor='black', alpha=0.7)
ax4.set_xlabel('Byte Index')
ax4.set_ylabel('Key Value (Hex)')
ax4.set_title('Recovered Key Bytes')
ax4.set_ylim([0, 256])
ax4.grid(True, alpha=0.3)

# 子图5：平均波形与泄漏区域
ax5 = plt.subplot(2, 3, 5)
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy')
mean_trace = np.mean(wave, axis=0)
ax5.plot(mean_trace, linewidth=1, color='blue', alpha=0.7, label='Mean Trace')
ax5.axvspan(350, 420, alpha=0.3, color='red', label='S-box Leakage Region')
ax5.set_xlabel('Sample Point')
ax5.set_ylabel('Mean Amplitude')
ax5.set_title('Mean Trace with Leakage Region')
ax5.legend()
ax5.grid(True, alpha=0.3)

# 子图6：攻击成功率统计
ax6 = plt.subplot(2, 3, 6)
success_metrics = ['High-Confidence\nBytes', 'Avg Correlation', 'Min Correlation', 'Avg Gap%']
values = [16/16*100, 0.5644*100, 0.4463*100, np.mean(gaps)]
colors = ['green', 'blue', 'orange', 'purple']
bars = ax6.bar(success_metrics, values, color=colors, edgecolor='black', alpha=0.7)
ax6.set_ylabel('Value (%)')
ax6.set_title('Attack Success Metrics')
ax6.set_ylim([0, 100])
ax6.grid(True, alpha=0.3, axis='y')

# 在柱状图上添加数值标签
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('cpa_attack_summary.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n可视化图表已保存为 'cpa_attack_summary.png'")
```
</details>

**📋 ← `python_jupyter`:** `可视化图表已保存为 'cpa_attack_summary.png'
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\231339127.py:85: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


![cpa_attack_summary.png](./cpa_attack_summary.png)


---

### Round 12 | tokens: 28,010→1,077

<details><summary><b>🤖 LLM Reasoning</b> (1868 chars)</summary>

## 🎉 攻击完成总结

我已成功对STM32F429 MCU软件实现的AES-128算法进行了电磁侧信道CPA攻击，完整分析报告如下：

---

### 📊 **攻击结果**

| 项目 | 结果 |
|------|------|
| **恢复密钥** | `00112233445566778899AABBCCDDEEFF` |
| **验证状态** | ✅ **MATCH** (密钥完全正确) |
| **高置信度字节** | **16/16 (100%)** |
| **平均相关系数** | **0.5644** |
| **最小相关系数** | **0.4463** |

---

### 🔧 **攻击配置**

- **算法**: AES-128
- **设备**: STM32F429 MCU (32-bit ARM Cortex-M4)
- **侧信道类型**: 电磁 (EM)
- **实现类型**: 软件
- **攻击目标**: S-box Output (第一轮)
- **泄漏模型**: Hamming Weight (HW)
- **迹数**: 1000 traces
- **采样点**: 1000 points

---

### 📈 **关键发现**

1. **攻击非常成功** - 无需任何预处理（无静态对齐、无垂直对齐、无滤波）
2. **泄漏强烈** - 所有字节相关系数 > 0.44，远超阈值
3. **区分度高** - 所有字节gap > 65%，正确密钥与次优候选区分明显
4. **测量质量优秀** - 电磁侧信道信噪比高
5. **泄漏时间集中** - S-box操作在350-420采样点范围内顺序执行

---

### 🎯 **各字节攻击详情**

| 字节 | 密钥 | 相关系数 | 时间点 | Gap% |
|------|------|----------|--------|------|
| 0 | 0x00 | 0.4463 | 353 | 65.4% |
| 1 | 0x11 | 0.5536 | 364 | 65.4% |
| 2 | 0x22 | 0.5321 | 418 | 69.9% |
| 3 | 0x33 | 0.5563 | 385 | 66.8% |
| 4 | 0x44 | 0.5662 | 356 | 67.7% |
| 5 | 0x55 | 0.5341 | 366 | 69.6% |
| 6 | 0x66 | 0.5802 | 377 | 69.5% |
| 7 | 0x77 | 0.5952 | 387 | 68.4% |
| 8 | 0x88 | 0.6141 | 358 | 66.5% |
| 9 | 0x99 | 0.4875 | 368 | 71.4% |
| 10 | 0xAA | 0.6308 | 379 | 73.6% |
| 11 | 0xBB | 0.5474 | 390 | 68.3% |
| 12 | 0xCC | **0.6539** | 360 | 72.5% |
| 13 | 0xDD | 0.6180 | 371 | 70.4% |
| 14 | 0xEE | 0.5513 | 381 | 67.3% |
| 15 | 0xFF | 0.5640 | 392 | 71.3% |

---

### 💡 **技术要点**

根据DKG知识图谱的指导：
- ✅ STM32F429是MCU软件实现，使用**S-box_out + HW模型**是正确选择
- ✅ 软件实现通常不需要垂直对齐（除非有明显的DC漂移）
- ✅ 波形已预裁剪到加密区域，无需额外的ROI定位
- ✅ 1000条迹数对于高质量EM测量完全足够

---

### 📁 **生成的文件**

1. `waveform_overview.png` - 波形概览
2. `waveform_analysis.png` - 波形特征分析
3. `variance_analysis.png` - 方差分析
4. `cpa_result_20260424_040258_296856.png` - CPA结果图
5. `cpa_detail_20260424_040258_296856.json` - CPA详细数据
6. `cpa_attack_summary.png` - 攻击总结可视化

攻击圆满成功！🎉

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 16,060 | 742 | 16,802 |
| 2 | 16,694 | 640 | 17,334 |
| 3 | 17,487 | 731 | 18,218 |
| 4 | 18,279 | 423 | 18,702 |
| 5 | 19,369 | 359 | 19,728 |
| 6 | 19,706 | 1,010 | 20,716 |
| 7 | 21,863 | 125 | 21,988 |
| 8 | 22,032 | 706 | 22,738 |
| 9 | 23,773 | 132 | 23,905 |
| 10 | 24,550 | 1,237 | 25,787 |
| 11 | 26,592 | 1,368 | 27,960 |
| 12 | 28,010 | 1,077 | 29,087 |
| **Total** | **254,415** | **8,550** | **262,965** |

## 8. Final Output

## 🎉 攻击完成总结

我已成功对STM32F429 MCU软件实现的AES-128算法进行了电磁侧信道CPA攻击，完整分析报告如下：

---

### 📊 **攻击结果**

| 项目 | 结果 |
|------|------|
| **恢复密钥** | `00112233445566778899AABBCCDDEEFF` |
| **验证状态** | ✅ **MATCH** (密钥完全正确) |
| **高置信度字节** | **16/16 (100%)** |
| **平均相关系数** | **0.5644** |
| **最小相关系数** | **0.4463** |

---

### 🔧 **攻击配置**

- **算法**: AES-128
- **设备**: STM32F429 MCU (32-bit ARM Cortex-M4)
- **侧信道类型**: 电磁 (EM)
- **实现类型**: 软件
- **攻击目标**: S-box Output (第一轮)
- **泄漏模型**: Hamming Weight (HW)
- **迹数**: 1000 traces
- **采样点**: 1000 points

---

### 📈 **关键发现**

1. **攻击非常成功** - 无需任何预处理（无静态对齐、无垂直对齐、无滤波）
2. **泄漏强烈** - 所有字节相关系数 > 0.44，远超阈值
3. **区分度高** - 所有字节gap > 65%，正确密钥与次优候选区分明显
4. **测量质量优秀** - 电磁侧信道信噪比高
5. **泄漏时间集中** - S-box操作在350-420采样点范围内顺序执行

---

### 🎯 **各字节攻击详情**

| 字节 | 密钥 | 相关系数 | 时间点 | Gap% |
|------|------|----------|--------|------|
| 0 | 0x00 | 0.4463 | 353 | 65.4% |
| 1 | 0x11 | 0.5536 | 364 | 65.4% |
| 2 | 0x22 | 0.5321 | 418 | 69.9% |
| 3 | 0x33 | 0.5563 | 385 | 66.8% |
| 4 | 0x44 | 0.5662 | 356 | 67.7% |
| 5 | 0x55 | 0.5341 | 366 | 69.6% |
| 6 | 0x66 | 0.5802 | 377 | 69.5% |
| 7 | 0x77 | 0.5952 | 387 | 68.4% |
| 8 | 0x88 | 0.6141 | 358 | 66.5% |
| 9 | 0x99 | 0.4875 | 368 | 71.4% |
| 10 | 0xAA | 0.6308 | 379 | 73.6% |
| 11 | 0xBB | 0.5474 | 390 | 68.3% |
| 12 | 0xCC | **0.6539** | 360 | 72.5% |
| 13 | 0xDD | 0.6180 | 371 | 70.4% |
| 14 | 0xEE | 0.5513 | 381 | 67.3% |
| 15 | 0xFF | 0.5640 | 392 | 71.3% |

---

### 💡 **技术要点**

根据DKG知识图谱的指导：
- ✅ STM32F429是MCU软件实现，使用**S-box_out + HW模型**是正确选择
- ✅ 软件实现通常不需要垂直对齐（除非有明显的DC漂移）
- ✅ 波形已预裁剪到加密区域，无需额外的ROI定位
- ✅ 1000条迹数对于高质量EM测量完全足够

---

### 📁 **生成的文件**

1. `waveform_overview.png` - 波形概览
2. `waveform_analysis.png` - 波形特征分析
3. `variance_analysis.png` - 方差分析
4. `cpa_result_20260424_040258_296856.png` - CPA结果图
5. `cpa_detail_20260424_040258_296856.json` - CPA详细数据
6. `cpa_attack_summary.png` - 攻击总结可视化

攻击圆满成功！🎉
