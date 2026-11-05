# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_040456_536 |
| Duration | 302.6s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_040456_536` |
| Total LLM Calls | 16 |
| First Round | prompt: 16,706, completion: 923 |
| Last Round | prompt: 28,743, completion: 489 |
| Total Tokens | 379,276 (prompt: 373,268, completion: 6,008) |

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

LLM Response: ["AES", "STM32F103", "MCU", "CPA", "Power", "S-box Output"]

Parsed Keywords: `["AES", "STM32F103", "MCU", "CPA", "Power", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 40833 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (43111 chars, click to expand)</summary>

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

**Search keywords** (6): AES, STM32F103, MCU, CPA, Power, S-box Output

**Summary**: 33 upper entities, 25 relationships, 17 diagnostic chains, 14 strategies


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

### DeviceClass (11)

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

### Pipeline (8)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values

### StatMethod (7)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Compare hypothetical power consumption with measured traces** — type=non_profiled
- **Generate Hamming weight models for S-box output** — type=non_profiled

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
- `AttackPoint:S-box Output` —[strategy_applies_to [source=expert_experience, condition=Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear, applicability=specific]]→ `Strategy:Do NOT switch leakage target family as first response to low correlation on software implementations`
- `StatMethod:Generate Hamming weight models for S-box output` —[consists_of [parameters_note=models are lookup tables for the leakage of each possible S-box output, source_text=Generate Hamming weight models for S-box output, support_count=1, is_optional=False]]→ `Pipeline:SCALib CPA Attack on AES`
- `AttackPoint:Inverse S-box Output` —[has_attack_point [source_text=attack_point: Inverse S-box Output, round: 14, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[has_attack_point [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[works_with [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`

## 3. Diagnostic Chains (17)


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

### Obs: `leakage_model_selection` — any
- **Cause** (high): Non-linear operations (e.g., S-box) have stronger power consumption leakage than linear transformations
- **Check**: Compare correlation strength between S-box output and linear operation points
- **Action**: Choose S-box output as intermediate value for CPA or machine learning attacks
  - operation: `switch_component`
  - target: `intermediate_value`
  - strategy: Choose the S-box output (the value after XOR with round key and before linear transformation) as the intermediate value for CPA or machine learning attacks.
- **Relates to**: AttackPoint:`S-box Output`

### Obs: `key_byte_distinguishability` — any
- **Cause** (high): Different key bytes (e.g., 0x55 and 0xAA) can have the same Hamming weight, making them indistinguishable if attacking the key directly. The S-box output provides a nonlinear transformation that spreads the Hamming weights, creating a unique signature for each key hypothesis.
- **Action**: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.
  - operation: `switch_component`
  - target: `attack point`
  - strategy: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.

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

## 4. Strategies (14)


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
All files for this session are stored in: ..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_040456_536
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_040456_536/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 16,706→923

**🤖 LLM:** 我来帮您对STM32F103 MCU软件实现的AES进行CPA密钥恢复。首先，让我检查一下数据的基本情况。

**🔧 → `python_jupyter`**

<details><summary>Code (2406 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
plaintext_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy'
ciphertext_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy'
wave_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy'

plaintext = np.load(plaintext_path)
ciphertext = np.load(ciphertext_path)
wave = np.load(wave_path)

print(f"Plaintext shape: {plaintext.shape}")
print(f"Ciphertext shape: {ciphertext.shape}")
print(f"Wave shape: {wave.shape}")
print(f"Number of traces: {wave.shape[0]}")
print(f"Samples per trace: {wave.shape[1]}")
print(f"Plaintext dtype: {plaintext.dtype}")
print(f"Ciphertext dtype: {ciphertext.dtype}")
print(f"Wave dtype: {wave.dtype}")

# 查看前几个明文和密文
print(f"\nFirst plaintext (hex): {plaintext[0].tobytes().hex()}")
print(f"First ciphertext (hex): {ciphertext[0].tobytes().hex()}")

# 查看波形统计信息
print(f"\nWave min: {wave.min():.2f}, max: {wave.max():.2f}, mean: {wave.mean():.2f}, std: {wave.std():.2f}")

# 绘制前几个波形
plt.figure(figsize=(12, 6))
for i in range(3):
    plt.plot(wave[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('First 3 Power Traces')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('first_traces.png')
plt.show()

# 计算所有波形的平均值
mean_trace = wave.mean(axis=0)
plt.figure(figsize=(12, 4))
plt.plot(mean_trace)
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Average Power Trace')
plt.grid(True, alpha=0.3)
plt.savefig('mean_trace.png')
plt.show()

# 计算方差来识别加密区域
variance = wave.var(axis=0)
plt.figure(figsize=(12, 4))
plt.plot(variance)
plt.xlabel('Sample Index')
plt.ylabel('Variance')
plt.title('Variance Across Traces')
plt.grid(True, alpha=0.3)
plt.savefig('variance.png')
plt.show()

# 找出方差最大的区域
max_var_idx = np.argmax(variance)
print(f"\nMaximum variance at sample index: {max_var_idx}")
print(f"Maximum variance value: {variance[max_var_idx]:.2f}")

# 查看方差最大的区域附近
window = 100
start = max(0, max_var_idx - window)
end = min(len(variance), max_var_idx + window)
print(f"Variance in region [{start}, {end}]:")
print(f"  Max: {variance[start:end].max():.2f}")
print(f"  Mean: {variance[start:end].mean():.2f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (970 chars)</summary>

```
Plaintext shape: (250, 16)
Ciphertext shape: (250, 16)
Wave shape: (250, 1500)
Number of traces: 250
Samples per trace: 1500
Plaintext dtype: uint8
Ciphertext dtype: uint8
Wave dtype: float32

First plaintext (hex): 33f25e5f412260df3ad3d47477f4ce89
First ciphertext (hex): 17eaf0dcb9e3bc6f7a83d9f769bfc973

Wave min: -342.52, max: 90.55, mean: -131.33, std: 61.50

Maximum variance at sample index: 1102
Maximum variance value: 3632.30
Variance in region [1002, 1202]:
  Max: 3632.30
  Mean: 1338.84
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1653778022.py:39: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1653778022.py:50: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1653778022.py:61: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 18,000→355

**🤖 LLM:** 很好！数据已加载成功。我们有250条轨迹，每条1500个采样点。从方差分析可以看出，在样本索引1102附近有显著的方差峰值，这很可能对应加密操作区域。

根据DKG知识图谱的建议，对于STM32F103这样的32位MCU软件实现，我应该：
1. 首先尝试直接CPA攻击，使用S-box输出和汉明重量模型
2. 根据"Software implementation: variance-first ROI exploration before alignment"原则，先进行方差分析定位加密区域

让我先进行明文相关性分析来确认泄漏区域：

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

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 602, "peak_region_end": 608, "peak_time_index": 606, "peak_correlation": 0.219, "suggested_cpa_range": [552, 658], "all_byte_peaks": [606, 267, 303, 355, 229, 259, 266, 363, 240, 270, 344, 362, 603, 282, 715, 368], "byte_peaks_std": 141.9, "plot_path": "correlation_20260424_040557_199522.png"}`


![correlation_20260424_040557_199522.png](./correlation_20260424_040557_199522.png)


---

### Round 3 | tokens: 18,510→352

**🤖 LLM:** 相关性分析显示峰值在606附近，但方差分析显示最大方差在1102附近。根据DKG的"Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI"原则，我应该优先考虑方差峰值区域。

让我先对波形进行平滑滤波（根据DKG建议，软件实现使用权重2-3）：

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

<details><summary><b>📋 ← `weighted_moving_average`</b> (1564 chars)</summary>

```
{"out_wave_npy": "smoothed_20260424_040613_583395.npy", "plot_path": "smooth_compare_20260424_040613_583395.png", "n_traces": 250, "n_points": 1500, "weight": 3, "plaintext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy", "ciphertext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"}
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\993782142.py:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy" is not None:
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\993782142.py:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103
...(truncated)
```
</details>


![smooth_compare_20260424_040613_583395.png](./smooth_compare_20260424_040613_583395.png)


---

### Round 4 | tokens: 19,587→234

**🤖 LLM:** 现在让我对平滑后的波形进行直接CPA攻击。根据DKG知识，对于STM32F103这样的32位MCU软件实现，我应该使用S-box输出和汉明重量模型：

**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "smoothed_20260424_040613_583395.npy",
  "candidates": 20,
  "leakage_model": "HW",
  "target": "S-box_out"
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2702 chars)</summary>

```
{"recovered_key": "11F5D6449766770D99AABBCC50EEFF00", "cpa_avg_correlation": 0.3199, "cpa_min_correlation": 0.2585, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_040625_857857.png", "detail_file": "cpa_detail_20260424_040625_857857.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.312, "time_index": 597, "gap_pct": 15.4}, {"byte": 1, "key": "0xF5", "correlation": 0.2585, "time_index": 893, "gap_pct": 1.7}, {"byte": 2, "key": "0xD6", "correlation": 0.3456, "time_index": 494, "gap_pct": 19.1}, {"byte": 3, "key": "0x44", "correlation": 0.3648, "time_index": 1039, "gap_pct": 22.8}, {"byte": 4, "key": "0x97", "correlation": 0.2958, "time_index": 31, "gap_pct": 7.4}, {"byte": 5, "key": "0x66", "correlation": 0.3592, "time_index": 825, "gap_pct": 21.5}, {"byte": 6, "key": "0x77", "correlation": 0.2895, "time_index": 942, "gap_pct": 0.1}, {"byte": 7, "key": "0x0D", "correlation": 0.274, "time_index": 447, "gap_pct": 3.3}, {"byte": 8, "key": "0x99", "correlation": 0.313, "time_index": 611, "gap_pct": 9.1}, {"byte": 9, "key": "0xAA", "correlation": 0.2928, "time_index": 668, "gap_pct": 9.7}, {"byte": 10, "key": "0xBB", "correlation": 0.3673, "time_index": 914, "gap_pct": 27.3}, {"byte": 11, "key": "0xCC", "correlation": 0.3546, "time_index": 1023, "gap_pct": 19.3}, {"byte": 12, "key": "0x50", "correlation": 0.28, "time_index": 36, "gap_pct": 11.0}, {"byte": 13, "key": "0xEE", "correlation": 0.3327, "time_index": 863, "gap_pct": 17.3}, {"byte": 
...(truncated)
```
</details>


![cpa_result_20260424_040625_857857.png](./cpa_result_20260424_040625_857857.png)


---

### Round 5 | tokens: 21,004→354

**🤖 LLM:** CPA攻击恢复了密钥`11F5D6449766770D99AABBCC50EEFF00`，但只有9/16字节是高置信度的（红色带）。平均相关性0.3199还可以，但gap_pct显示有些字节的区分度不够好。

让我验证一下这个密钥是否正确：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "11F5D6449766770D99AABBCC50EEFF00",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
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

### Round 6 | tokens: 21,742→434

**🤖 LLM:** 密钥验证失败。根据DKG的"key_search found=false is NOT CPA failure"原则，我应该先尝试key_search而不是立即切换攻击参数。让我先检查一下哪些字节是低置信度的：

**🔧 → `python_jupyter`**

<details><summary>Code (925 chars)</summary>

```python
import json

# 加载CPA详细结果
with open('cpa_detail_20260424_040625_857857.json', 'r') as f:
    detail = json.load(f)

print("低置信度字节分析:")
for byte_info in detail['per_byte']:
    byte = byte_info['byte']
    gap_pct = byte_info['gap_pct']
    key = byte_info['key']
    correlation = byte_info['correlation']
    
    if gap_pct < 15:  # gap小于15%被认为是低置信度
        print(f"字节 {byte:2d}: key=0x{key}, gap={gap_pct:.1f}%, correlation={correlation:.3f} (低置信度)")
    else:
        print(f"字节 {byte:2d}: key=0x{key}, gap={gap_pct:.1f}%, correlation={correlation:.3f}")

# 查看低置信度字节的候选密钥
print("\n低置信度字节的候选密钥:")
low_conf_bytes = [1, 4, 6, 7, 8, 9, 12]  # 从CPA结果中看到的低置信度字节索引
for byte_idx in low_conf_bytes:
    candidates = detail['candidates'][str(byte_idx)]
    print(f"\n字节 {byte_idx}:")
    for i, cand in enumerate(candidates[:5]):  # 显示前5个候选
        print(f"  候选{i+1}: key=0x{cand['key']:02X}, correlation={cand['correlation']:.4f}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
低置信度字节分析:

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[99][39m[32m, line 8[39m
[32m      5[39m     detail = json.load(f)
[32m      7[39m [38;5;28mprint[39m([33m"[39m[33m低置信度字节分析:[39m[33m"[39m)
[32m----> [39m[32m8[39m [38;5;28;01mfor[39;00m byte_info [38;5;129;01min[39;00m [43mdetail[49m[43m[[49m[33;43m'[39;49m[33;43mper_byte[39;49m[33;43m'[39;49m[43m][49m:
[32m      9[39m     byte = byte_info[[33m'[39m[33mbyte[39m[33m'[39m]
[32m     10[39m     gap_pct = byte_info[[33m'[39m[33mgap_pct[39m[33m'[39m]

[31mKeyError[39m: 'per_byte'
```


---

### Round 7 | tokens: 22,585→339

**🤖 LLM:** 让我检查一下CPA详细文件的结构：

**🔧 → `python_jupyter`**

<details><summary>Code (901 chars)</summary>

```python
import json

with open('cpa_detail_20260424_040625_857857.json', 'r') as f:
    detail = json.load(f)

print("CPA详细文件键:", list(detail.keys()))
print("\n前几个键的示例:")
for key in list(detail.keys())[:5]:
    if isinstance(detail[key], dict):
        print(f"{key}: dict with keys {list(detail[key].keys())[:5]}...")
    elif isinstance(detail[key], list):
        print(f"{key}: list with {len(detail[key])} elements")
    else:
        print(f"{key}: {type(detail[key])}")

# 查看候选密钥
if 'candidates' in detail:
    print(f"\n候选密钥结构: {len(detail['candidates'])}个字节")
    for byte_idx in range(3):  # 查看前3个字节
        if str(byte_idx) in detail['candidates']:
            cands = detail['candidates'][str(byte_idx)]
            print(f"字节{byte_idx}: {len(cands)}个候选")
            for i, cand in enumerate(cands[:3]):
                print(f"  候选{i+1}: key=0x{cand['key']:02X}, corr={cand['correlation']:.4f}")
```
</details>

**📋 ← `python_jupyter`:** `CPA详细文件键: ['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results']

前几个键的示例:
n_traces: <class 'int'>
n_points: <class 'int'>
leakage_model: <class 'str'>
target: <class 'str'>
corr_mode: <class 'str'>`


---

### Round 8 | tokens: 23,022→241

**🤖 LLM:** 让我查看results字段：

**🔧 → `python_jupyter`**

<details><summary>Code (587 chars)</summary>

```python
import json

with open('cpa_detail_20260424_040625_857857.json', 'r') as f:
    detail = json.load(f)

results = detail['results']
print(f"results字段类型: {type(results)}")
print(f"results长度: {len(results)}")

# 查看第一个字节的结果
if len(results) > 0:
    print("\n第一个字节的结果:")
    print(results[0])
    
# 查看所有字节的gap_pct
print("\n各字节的gap_pct:")
for i, result in enumerate(results):
    byte = result['byte']
    gap_pct = result['gap_pct']
    key = result['key']
    correlation = result['correlation']
    print(f"字节 {byte:2d}: key=0x{key:02X}, gap={gap_pct:.1f}%, correlation={correlation:.3f}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
results字段类型: <class 'list'>
results长度: 16

第一个字节的结果:
{'byte': 0, 'topK': [{'key': 17, 'score': 0.3120080968350811, 'time_index': 597}, {'key': 147, 'score': 0.2638528876465953, 'time_index': 1129}, {'key': 21, 'score': 0.26281961219737743, 'time_index': 592}, {'key': 198, 'score': 0.2553195579635308, 'time_index': 687}, {'key': 227, 'score': 0.25360056348769905, 'time_index': 659}, {'key': 109, 'score': 0.24542802275060238, 'time_index': 1312}, {'key': 12, 'score': 0.24447279180756643, 'time_index': 520}, {'key': 175, 'score': 0.24073344644068678, 'time_index': 1296}, {'key': 89, 'score': 0.2396456446042409, 'time_index': 175}, {'key': 182, 'score': 0.23962084499931302, 'time_index': 360}, {'key': 53, 'score': 0.2371675400195156, 'time_index': 709}, {'key': 229, 'score': 0.23543441928519693, 'time_index': 858}, {'key': 47, 'score': 0.23535222586749696, 'time_index': 519}, {'key': 174, 'score': 0.2341743427916559, 'time_index': 1054}, {'key': 247, 'score': 0.23343939553152385, 'time_index': 278}, {'key': 58, 'score': 0.23342535144168042, 'time_index': 689}, {'key': 248, 'score': 0.23287371292146333, 'time_index': 698}, {'key': 2, 'score': 0.23225330301696598, 'time_index': 818}, {'key': 169, 'score': 0.2288817338433335, 'time_index': 336}, {'key': 214, 'score': 0.22711263820632188, 'time_index': 201}], 'best_key': 17}

各字节的gap_pct:

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[101][39m[32m, line 19[39m
[32m     17[39m [38;5;28;01mfor[39;00m i, result [38;5;129;01min[39;00m [38;5;28menumerate[39m(results):
[32m     18[39m     byte = result[[33m'[39m[33mbyte[39m[33m'[39m]
[32m---> [39m[32m19[39m     gap_pct = [43mresult[49m[43m[[49m[33;43m'[39;49m[33;43mgap_pct[39;49m[33;43m'[39;49m[43m][49m
[32m     20[39m     key = result[[33m'[39m[33mkey[39m[33m'[39m]
[32m     21[39m     correlation = result[[33m'[39m[33mcorrelation[39m[33m'[39m]

[31mKeyError[39m: 'gap_pct'
```


---

### Round 9 | tokens: 24,230→304

**🤖 LLM:** 让我正确查看CPA结果：

**🔧 → `python_jupyter`**

<details><summary>Code (658 chars)</summary>

```python
import json

with open('cpa_detail_20260424_040625_857857.json', 'r') as f:
    detail = json.load(f)

# 从之前的CPA攻击结果中，我们知道低置信度字节是：[1, 4, 6, 7, 8, 9, 12]
low_conf_bytes = [1, 4, 6, 7, 8, 9, 12]

print("低置信度字节的候选密钥分析:")
for byte_idx in low_conf_bytes:
    if str(byte_idx) in detail['candidates']:
        cands = detail['candidates'][str(byte_idx)]
        print(f"\n字节 {byte_idx}: {len(cands)}个候选")
        for i, cand in enumerate(cands[:5]):  # 显示前5个候选
            print(f"  候选{i+1}: key=0x{cand['key']:02X}, correlation={cand['correlation']:.4f}")
    else:
        print(f"\n字节 {byte_idx}: 无候选数据")

# 现在使用key_search工具
print("\n现在使用key_search工具搜索正确密钥...")
```
</details>

**❌ ← `python_jupyter` Error:**

```
低置信度字节的候选密钥分析:

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[102][39m[32m, line 11[39m
[32m      9[39m [38;5;28mprint[39m([33m"[39m[33m低置信度字节的候选密钥分析:[39m[33m"[39m)
[32m     10[39m [38;5;28;01mfor[39;00m byte_idx [38;5;129;01min[39;00m low_conf_bytes:
[32m---> [39m[32m11[39m     [38;5;28;01mif[39;00m [38;5;28mstr[39m(byte_idx) [38;5;129;01min[39;00m [43mdetail[49m[43m[[49m[33;43m'[39;49m[33;43mcandidates[39;49m[33;43m'[39;49m[43m][49m:
[32m     12[39m         cands = detail[[33m'[39m[33mcandidates[39m[33m'[39m][[38;5;28mstr[39m(byte_idx)]
[32m     13[39m         [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;130;01m\n[39;00m[33m字节 [39m[38;5;132;01m{[39;00mbyte_idx[38;5;132;01m}[39;00m[33m: [39m[38;5;132;01m{[39;00m[38;5;28mlen[39m(cands)[38;5;132;01m}[39;00m[33m个候选[39m[33m"[39m)

[31mKeyError[39m: 'candidates'
```


---

### Round 10 | tokens: 25,152→342

**🤖 LLM:** 让我直接使用key_search工具，它会自动处理这些细节：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "recovered_key_hex": "11F5D6449766770D99AABBCC50EEFF00",
  "cpa_detail_file": "cpa_detail_20260424_040625_857857.json",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 20,
  "max_combinations": 50000
}
```
</details>

**📋 ← `key_search`:** `{"found": false, "correct_key": null, "search_rounds": 50000, "unreliable_bytes": [1, 4, 6, 7, 8, 9, 12], "recommended_next_step": "merge_more_cpa_runs_or_rerun_with_higher_candidates", "message": "Not found after 50000 searches."}`


---

### Round 11 | tokens: 25,596→372

**🤖 LLM:** key_search在50000次搜索后没有找到正确密钥。根据DKG的"key_search found=false is NOT CPA failure"原则，我应该先增加搜索预算。让我尝试增加max_combinations：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "recovered_key_hex": "11F5D6449766770D99AABBCC50EEFF00",
  "cpa_detail_file": "cpa_detail_20260424_040625_857857.json",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 30,
  "max_combinations": 200000
}
```
</details>

**📋 ← `key_search`:** `{"found": false, "correct_key": null, "search_rounds": 200000, "unreliable_bytes": [1, 4, 6, 7, 8, 9, 12], "recommended_next_step": "merge_more_cpa_runs_or_rerun_with_higher_candidates", "message": "Not found after 200000 searches."}`


---

### Round 12 | tokens: 26,070→505

**🤖 LLM:** 仍然没有找到。根据DKG的"Software implementation: variance-first ROI exploration before alignment"原则，我应该先重新定位泄漏区域。让我检查一下方差峰值区域：

**🔧 → `python_jupyter`**

<details><summary>Code (1255 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 重新加载平滑后的波形
smoothed_wave = np.load('smoothed_20260424_040613_583395.npy')

# 计算方差
variance = smoothed_wave.var(axis=0)

# 找出方差最大的区域
max_var_idx = np.argmax(variance)
print(f"最大方差位置: {max_var_idx}")
print(f"最大方差值: {variance[max_var_idx]:.2f}")

# 查看方差峰值区域
window = 200
start = max(0, max_var_idx - window)
end = min(len(variance), max_var_idx + window)

plt.figure(figsize=(12, 4))
plt.plot(range(start, end), variance[start:end])
plt.axvline(x=max_var_idx, color='r', linestyle='--', alpha=0.5, label=f'Max variance at {max_var_idx}')
plt.xlabel('Sample Index')
plt.ylabel('Variance')
plt.title(f'Variance in Region [{start}, {end}]')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('variance_peak_region.png')
plt.show()

# 查看该区域的波形
plt.figure(figsize=(12, 6))
for i in range(5):
    plt.plot(range(start, end), smoothed_wave[i, start:end], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title(f'Waveforms in Variance Peak Region [{start}, {end}]')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('waveforms_variance_region.png')
plt.show()

# 建议的CPA区间
cpa_start = max_var_idx - 50
cpa_end = max_var_idx + 50
print(f"\n建议的CPA区间: [{cpa_start}, {cpa_end}]")
```
</details>

**📋 ← `python_jupyter`:** `最大方差位置: 1105
最大方差值: 3352.34

建议的CPA区间: [1055, 1155]
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1354780626.py:29: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1354780626.py:41: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 13 | tokens: 26,723→331

**🤖 LLM:** 方差峰值在1105附近。根据DKG的"Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI"原则，我应该基于方差峰值区域进行对齐。让我在这个区域进行静态对齐：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "smoothed_20260424_040613_583395.npy",
  "start": 1100,
  "length": 100,
  "max_shift": 200,
  "threshold": 85,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_040909_777604.npy", "plot_path": "align_overlay_20260424_040909_778604.png", "ref_trace_used": 125, "accepted": 250, "discarded": 0, "total": 250, "out_plaintext_npy": "plaintext_aligned_20260424_040909_778604.npy", "plaintext_traces": 250, "out_ciphertext_npy": "ciphertext_aligned_20260424_040909_778604.npy", "ciphertext_traces": 250, "alignment_avg_correlation": 0.9945, "alignment_min_correlation": 0.8889, "acceptance_rate": 1.0}`


![align_overlay_20260424_040909_778604.png](./align_overlay_20260424_040909_778604.png)


---

### Round 14 | tokens: 27,252→179

**🤖 LLM:** 很好！对齐成功，接受了所有250条轨迹，平均相关性0.9945。现在让我在对齐后的波形上重新进行CPA攻击：

**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_040909_778604.npy",
  "wave_npy": "aligned_20260424_040909_777604.npy",
  "candidates": 30,
  "leakage_model": "HW",
  "target": "S-box_out"
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2141 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.4, "cpa_min_correlation": 0.2993, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_040922_373309.png", "detail_file": "cpa_detail_20260424_040922_373309.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3877, "time_index": 584, "gap_pct": 26.0}, {"byte": 1, "key": "0x22", "correlation": 0.3363, "time_index": 849, "gap_pct": 17.1}, {"byte": 2, "key": "0x33", "correlation": 0.2993, "time_index": 689, "gap_pct": 10.0}, {"byte": 3, "key": "0x44", "correlation": 0.4444, "time_index": 1043, "gap_pct": 44.9}, {"byte": 4, "key": "0x55", "correlation": 0.3796, "time_index": 595, "gap_pct": 19.0}, {"byte": 5, "key": "0x66", "correlation": 0.4091, "time_index": 822, "gap_pct": 33.4}, {"byte": 6, "key": "0x77", "correlation": 0.4257, "time_index": 930, "gap_pct": 33.9}, {"byte": 7, "key": "0x88", "correlation": 0.399, "time_index": 960, "gap_pct": 26.2}, {"byte": 8, "key": "0x99", "correlation": 0.3685, "time_index": 605, "gap_pct": 30.9}, {"byte": 9, "key": "0xAA", "correlation": 0.4113, "time_index": 831, "gap_pct": 33.7}, {"byte": 10, "key": "0xBB", "correlation": 0.4313, "time_index": 1113, "gap_pct": 33.3}, {"byte": 11, "key": "0xCC", "correlation": 0.4466, "time_index": 996, "gap_pct": 39.3}, {"byte": 12, "key": "0xDD", "correlation": 0.3392, "time_index": 616, "gap_pct": 19.1}, {"byte": 13, "key": "0xEE", "correlation": 0.4648, "time_index": 848, "gap_pct": 36.8}, 
...(truncated)
```
</details>


![cpa_result_20260424_040922_373309.png](./cpa_result_20260424_040922_373309.png)


---

### Round 15 | tokens: 28,346→254

**🤖 LLM:** 太好了！对齐后的CPA攻击结果显著改善：恢复了密钥`112233445566778899AABBCCDDEEFF00`，15/16字节是高置信度的，只有字节2是低置信度的。平均相关性提高到0.4。让我验证这个密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_040909_778604.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_040909_778604.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "17EAF0DCB9E3BC6F7A83D9F769BFC973", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 17EAF0DCB9E3BC6F7A83D9F769BFC973...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 16 | tokens: 28,743→489

<details><summary><b>🤖 LLM Reasoning</b> (967 chars)</summary>

完美！密钥验证成功！我们成功恢复了正确的AES-128密钥：`112233445566778899AABBCCDDEEFF00`。

让我总结一下攻击过程：

## 攻击总结

**目标**: STM32F103 MCU软件实现的AES-128

**数据**:
- 250条轨迹，每条1500个采样点
- 明文和密文文件

**攻击步骤**:

1. **数据探索**: 加载数据并分析波形特性，发现方差峰值在样本1102附近

2. **平滑滤波**: 使用加权移动平均（权重=3）对波形进行平滑，这是软件实现的推荐设置

3. **直接CPA攻击**: 使用S-box输出和汉明重量模型进行CPA，但只恢复了9/16高置信度字节，密钥验证失败

4. **key_search尝试**: 尝试key_search但未成功，因为太多字节（7个）是低置信度的

5. **基于方差的对齐**: 根据DKG的"variance-ROI precedence"原则，在方差峰值区域（1100附近）进行静态对齐
   - 使用参数: start=1100, length=100, max_shift=200, threshold=85
   - 成功对齐所有250条轨迹，平均相关性0.9945

6. **对齐后的CPA攻击**: 在对齐波形上重新进行CPA攻击
   - 结果显著改善：15/16字节高置信度，平均相关性0.4
   - 恢复密钥: `112233445566778899AABBCCDDEEFF00`

7. **密钥验证**: 成功验证密钥正确

**关键成功因素**:
- 遵循DKG的"variance-first ROI exploration"原则，优先使用方差峰值区域进行对齐
- 使用适当的对齐参数（max_shift=200足够大）
- 对于STM32F103软件实现，使用S-box输出和汉明重量模型是正确的选择
- 对齐显著提高了CPA效果，从9/16提高到15/16高置信度字节

**恢复的AES-128密钥**: `112233445566778899AABBCCDDEEFF00`

这个案例展示了DKG知识图谱在实际SCA攻击中的价值，特别是关于对齐锚点选择和软件实现最佳实践的原则。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 16,706 | 923 | 17,629 |
| 2 | 18,000 | 355 | 18,355 |
| 3 | 18,510 | 352 | 18,862 |
| 4 | 19,587 | 234 | 19,821 |
| 5 | 21,004 | 354 | 21,358 |
| 6 | 21,742 | 434 | 22,176 |
| 7 | 22,585 | 339 | 22,924 |
| 8 | 23,022 | 241 | 23,263 |
| 9 | 24,230 | 304 | 24,534 |
| 10 | 25,152 | 342 | 25,494 |
| 11 | 25,596 | 372 | 25,968 |
| 12 | 26,070 | 505 | 26,575 |
| 13 | 26,723 | 331 | 27,054 |
| 14 | 27,252 | 179 | 27,431 |
| 15 | 28,346 | 254 | 28,600 |
| 16 | 28,743 | 489 | 29,232 |
| **Total** | **373,268** | **6,008** | **379,276** |

## 8. Final Output

完美！密钥验证成功！我们成功恢复了正确的AES-128密钥：`112233445566778899AABBCCDDEEFF00`。

让我总结一下攻击过程：

## 攻击总结

**目标**: STM32F103 MCU软件实现的AES-128

**数据**:
- 250条轨迹，每条1500个采样点
- 明文和密文文件

**攻击步骤**:

1. **数据探索**: 加载数据并分析波形特性，发现方差峰值在样本1102附近

2. **平滑滤波**: 使用加权移动平均（权重=3）对波形进行平滑，这是软件实现的推荐设置

3. **直接CPA攻击**: 使用S-box输出和汉明重量模型进行CPA，但只恢复了9/16高置信度字节，密钥验证失败

4. **key_search尝试**: 尝试key_search但未成功，因为太多字节（7个）是低置信度的

5. **基于方差的对齐**: 根据DKG的"variance-ROI precedence"原则，在方差峰值区域（1100附近）进行静态对齐
   - 使用参数: start=1100, length=100, max_shift=200, threshold=85
   - 成功对齐所有250条轨迹，平均相关性0.9945

6. **对齐后的CPA攻击**: 在对齐波形上重新进行CPA攻击
   - 结果显著改善：15/16字节高置信度，平均相关性0.4
   - 恢复密钥: `112233445566778899AABBCCDDEEFF00`

7. **密钥验证**: 成功验证密钥正确

**关键成功因素**:
- 遵循DKG的"variance-first ROI exploration"原则，优先使用方差峰值区域进行对齐
- 使用适当的对齐参数（max_shift=200足够大）
- 对于STM32F103软件实现，使用S-box输出和汉明重量模型是正确的选择
- 对齐显著提高了CPA效果，从9/16提高到15/16高置信度字节

**恢复的AES-128密钥**: `112233445566778899AABBCCDDEEFF00`

这个案例展示了DKG知识图谱在实际SCA攻击中的价值，特别是关于对齐锚点选择和软件实现最佳实践的原则。
