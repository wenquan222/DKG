# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_044804_942 |
| Duration | 336.8s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_044804_942` |
| Total LLM Calls | 15 |
| First Round | prompt: 16,706, completion: 990 |
| Last Round | prompt: 29,722, completion: 592 |
| Total Tokens | 362,902 (prompt: 355,931, completion: 6,971) |

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
All files for this session are stored in: ..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_044804_942
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_DSv3.2\AES-STM32F103_DeepSeek-V3.2_DKG_20260424_044804_942/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 16,706→990

**🤖 LLM:** 我将帮您对STM32F103 MCU软件实现的AES进行CPA密钥恢复。首先，让我检查一下数据的基本情况。

**🔧 → `python_jupyter`**

<details><summary>Code (2606 chars)</summary>

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
print("\nFirst 3 plaintexts (hex):")
for i in range(3):
    print(f"Trace {i}: {plaintext[i].tobytes().hex()}")

print("\nFirst 3 ciphertexts (hex):")
for i in range(3):
    print(f"Trace {i}: {ciphertext[i].tobytes().hex()}")

# 查看波形统计信息
print(f"\nWave statistics:")
print(f"  Min: {wave.min():.2f}")
print(f"  Max: {wave.max():.2f}")
print(f"  Mean: {wave.mean():.2f}")
print(f"  Std: {wave.std():.2f}")

# 绘制前几个波形
plt.figure(figsize=(12, 6))
for i in range(3):
    plt.plot(wave[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample index')
plt.ylabel('Amplitude')
plt.title('First 3 power traces')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('first_traces.png')
plt.show()

# 计算所有波形的平均值
mean_trace = wave.mean(axis=0)
plt.figure(figsize=(12, 4))
plt.plot(mean_trace)
plt.xlabel('Sample index')
plt.ylabel('Amplitude')
plt.title('Average power trace')
plt.grid(True, alpha=0.3)
plt.savefig('mean_trace.png')
plt.show()

# 计算方差来识别加密区域
variance_trace = wave.var(axis=0)
plt.figure(figsize=(12, 4))
plt.plot(variance_trace)
plt.xlabel('Sample index')
plt.ylabel('Variance')
plt.title('Variance across traces')
plt.grid(True, alpha=0.3)
plt.savefig('variance_trace.png')
plt.show()

# 找到方差最大的区域
max_var_idx = np.argmax(variance_trace)
print(f"\nMaximum variance at sample index: {max_var_idx}")
print(f"Maximum variance value: {variance_trace[max_var_idx]:.2f}")

# 查看方差最大的区域附近
window = 100
start = max(0, max_var_idx - window)
end = min(len(variance_trace), max_var_idx + window)
print(f"Variance in region [{start}, {end}]:")
print(f"  Max: {variance_trace[start:end].max():.2f}")
print(f"  Mean: {variance_trace[start:end].mean():.2f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1180 chars)</summary>

```
Plaintext shape: (250, 16)
Ciphertext shape: (250, 16)
Wave shape: (250, 1500)
Number of traces: 250
Samples per trace: 1500
Plaintext dtype: uint8
Ciphertext dtype: uint8
Wave dtype: float32

First 3 plaintexts (hex):
Trace 0: 33f25e5f412260df3ad3d47477f4ce89
Trace 1: 381e684af2267f5b549e6d7fb8bf9bc5
Trace 2: 5a29fb3a6236665e5d1ac5c49f435faa

First 3 ciphertexts (hex):
Trace 0: 17eaf0dcb9e3bc6f7a83d9f769bfc973
Trace 1: 354b46dbc4f91aa4fb2eba84e101a252
Trace 2: 11b42377f7520e3e18aa8368d6c85599

Wave statistics:
  Min: -342.52
  Max: 90.55
  Mean: -131.33
  Std: 61.50

Maximum variance at sample index: 1102
Maximum variance value: 3632.30
Variance in region [1002, 1202]:
  Max: 3632.30
  Mean: 1338.84
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\3152236519.py:48: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\3152236519.py:59: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\3152236519.py:70: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 18,188→474

**🤖 LLM:** 很好！数据已加载成功。我们有250条轨迹，每条1500个采样点。从方差分析可以看出，在样本索引1102附近有明显的加密区域（方差最大值为3632.30）。这是STM32F103 MCU软件实现的典型特征。

根据DKG知识图谱的建议，对于软件实现（MCU），我应该：
1. 首先尝试直接CPA，不进行对齐（根据"Software implementation: variance-first ROI exploration before alignment"原则）
2. 使用S-box输出作为攻击点，HW作为泄漏模型（根据"attack_position_selection"诊断链）
3. 对于软件实现，通常不需要垂直对齐（根据"Software implementations do NOT need vertical alignment by default"反模式）

让我先尝试直接CPA攻击：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2994 chars)</summary>

```
{"recovered_key": "11ECD6443566920D5339BBCC4EEEFF00", "cpa_avg_correlation": 0.3177, "cpa_min_correlation": 0.2679, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_044915_700428.png", "detail_file": "cpa_detail_20260424_044915_700428.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3251, "time_index": 586, "gap_pct": 14.4}, {"byte": 1, "key": "0xEC", "correlation": 0.2679, "time_index": 823, "gap_pct": 1.3}, {"byte": 2, "key": "0xD6", "correlation": 0.3516, "time_index": 492, "gap_pct": 21.1}, {"byte": 3, "key": "0x44", "correlation": 0.3574, "time_index": 1038, "gap_pct": 19.1}, {"byte": 4, "key": "0x35", "correlation": 0.2881, "time_index": 168, "gap_pct": 4.2}, {"byte": 5, "key": "0x66", "correlation": 0.3694, "time_index": 823, "gap_pct": 23.8}, {"byte": 6, "key": "0x92", "correlation": 0.3066, "time_index": 91, "gap_pct": 3.9}, {"byte": 7, "key": "0x0D", "correlation": 0.2767, "time_index": 446, "gap_pct": 3.9}, {"byte": 8, "key": "0x53", "correlation": 0.2897, "time_index": 1012, "gap_pct": 0.7}, {"byte": 9, "key": "0x39", "correlation": 0.2711, "time_index": 240, "gap_pct": 2.2}, {"byte": 10, "key": "0xBB", "correlation": 0.3862, "time_index": 913, "gap_pct": 30.6}, {"byte": 11, "key": "0xCC", "correlation": 0.3413, "time_index": 1021, "gap_pct": 11.6}, {"byte": 12, "key": "0x4E", "correlation": 0.27, "time_index": 338, "gap_pct": 1.1}, {"byte": 13, "key": "0xEE", "correlation": 0.333, "time_index": 862, "gap_pct": 21.0}, {"byte
...(truncated)
```
</details>


![cpa_result_20260424_044915_700428.png](./cpa_result_20260424_044915_700428.png)


---

### Round 3 | tokens: 19,975→304

**🤖 LLM:** 第一次CPA结果：恢复了6/16个高置信度字节，平均相关性为0.3177。根据评估，这属于红色带（red band），需要重新定位泄漏区域或切换目标。让我先验证一下恢复的密钥是否正确：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "11ECD6443566920D5339BBCC4EEEFF00",
  "algorithm": "AES",
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

### Round 4 | tokens: 20,651→299

**🤖 LLM:** 密钥验证失败，但这是预期的，因为我们只有6/16个高置信度字节。根据DKG知识图谱的"Software implementation: variance-first ROI exploration before alignment"原则，我应该先进行方差分析来定位加密区域。让我先进行明文/密文相关性分析来更好地定位泄漏区域：

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

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 602, "peak_region_end": 608, "peak_time_index": 606, "peak_correlation": 0.219, "suggested_cpa_range": [552, 658], "all_byte_peaks": [606, 267, 303, 355, 229, 259, 266, 363, 240, 270, 344, 362, 603, 282, 715, 368], "byte_peaks_std": 141.9, "plot_path": "correlation_20260424_044952_132473.png"}`


![correlation_20260424_044952_132473.png](./correlation_20260424_044952_132473.png)


---

### Round 5 | tokens: 21,105→276

**🤖 LLM:** 明文相关性分析显示峰值在样本606附近，建议的CPA范围为[552, 658]。但之前方差分析显示最大方差在1102附近。让我也看看密文相关性：

**🔧 → `plaintext_ciphertext_correlation`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "data_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "data_type": "ciphertext",
  "byte_index": 0,
  "model": "HW"
}
```
</details>

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 657, "peak_region_end": 661, "peak_time_index": 659, "peak_correlation": 0.1644, "suggested_cpa_range": [607, 711], "all_byte_peaks": [659, 936, 488, 658, 848, 852, 117, 1205, 905, 1052, 443, 1, 457, 328, 580, 998], "byte_peaks_std": 329.5, "plot_path": "correlation_20260424_045006_350482.png"}`


![correlation_20260424_045006_350482.png](./correlation_20260424_045006_350482.png)


---

### Round 6 | tokens: 21,539→988

**🤖 LLM:** 密文相关性峰值在659附近。现在让我可视化这些区域，看看哪个区域更可能是真正的加密区域：

**🔧 → `python_jupyter`**

<details><summary>Code (2638 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 重新加载数据
wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')
mean_trace = wave.mean(axis=0)
variance_trace = wave.var(axis=0)

# 标记关键区域
plaintext_peak = 606
ciphertext_peak = 659
variance_peak = 1102

# 绘制平均波形和方差
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

# 平均波形
ax1.plot(mean_trace, 'b-', alpha=0.7, label='Mean trace')
ax1.axvline(plaintext_peak, color='g', linestyle='--', alpha=0.7, label=f'Plaintext peak ({plaintext_peak})')
ax1.axvline(ciphertext_peak, color='orange', linestyle='--', alpha=0.7, label=f'Ciphertext peak ({ciphertext_peak})')
ax1.axvline(variance_peak, color='r', linestyle='--', alpha=0.7, label=f'Variance peak ({variance_peak})')
ax1.set_xlabel('Sample index')
ax1.set_ylabel('Amplitude')
ax1.set_title('Average power trace with key points')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 方差
ax2.plot(variance_trace, 'r-', alpha=0.7, label='Variance')
ax2.axvline(plaintext_peak, color='g', linestyle='--', alpha=0.7, label=f'Plaintext peak ({plaintext_peak})')
ax2.axvline(ciphertext_peak, color='orange', linestyle='--', alpha=0.7, label=f'Ciphertext peak ({ciphertext_peak})')
ax2.axvline(variance_peak, color='r', linestyle='--', alpha=0.7, label=f'Variance peak ({variance_peak})')
ax2.set_xlabel('Sample index')
ax2.set_ylabel('Variance')
ax2.set_title('Variance across traces with key points')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('key_regions.png')
plt.show()

# 查看方差峰值区域的特征
print("Variance peak region analysis:")
window = 50
start = max(0, variance_peak - window)
end = min(len(variance_trace), variance_peak + window)
print(f"Region [{start}, {end}]:")
print(f"  Variance max: {variance_trace[start:end].max():.2f}")
print(f"  Variance mean: {variance_trace[start:end].mean():.2f}")
print(f"  Variance std: {variance_trace[start:end].std():.2f}")

# 查看明文相关性峰值区域
print(f"\nPlaintext correlation peak region analysis:")
start = max(0, plaintext_peak - window)
end = min(len(variance_trace), plaintext_peak + window)
print(f"Region [{start}, {end}]:")
print(f"  Variance max: {variance_trace[start:end].max():.2f}")
print(f"  Variance mean: {variance_trace[start:end].mean():.2f}")

# 查看密文相关性峰值区域
print(f"\nCiphertext correlation peak region analysis:")
start = max(0, ciphertext_peak - window)
end = min(len(variance_trace), ciphertext_peak + window)
print(f"Region [{start}, {end}]:")
print(f"  Variance max: {variance_trace[start:end].max():.2f}")
print(f"  Variance mean: {variance_trace[start:end].mean():.2f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (504 chars)</summary>

```
Variance peak region analysis:
Region [1052, 1152]:
  Variance max: 3632.30
  Variance mean: 2027.68
  Variance std: 794.32

Plaintext correlation peak region analysis:
Region [556, 656]:
  Variance max: 1794.28
  Variance mean: 528.98

Ciphertext correlation peak region analysis:
Region [609, 709]:
  Variance max: 540.55
  Variance mean: 408.34
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\3039636060.py:41: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 7 | tokens: 22,704→372

**🤖 LLM:** 根据DKG知识图谱的"Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI"原则，当方差ROI和明文/密文相关性ROI不一致时，我应该优先选择方差峰值区域作为对齐锚点。方差峰值区域（1102附近）的方差值（3632.30）远高于其他区域。

让我先对波形进行平滑滤波，然后尝试在方差峰值区域进行CPA：

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
{"out_wave_npy": "smoothed_20260424_045104_928599.npy", "plot_path": "smooth_compare_20260424_045104_928599.png", "n_traces": 250, "n_points": 1500, "weight": 3, "plaintext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy", "ciphertext_npy": "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"}
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
<>:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1902683768.py:25: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy" is not None:
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1902683768.py:27: SyntaxWarning: "is not" with a literal. Did you mean "!="?
  if "F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F1
...(truncated)
```
</details>


![smooth_compare_20260424_045104_928599.png](./smooth_compare_20260424_045104_928599.png)


---

### Round 8 | tokens: 23,803→542

**🤖 LLM:** 现在让我在平滑后的波形上，针对方差峰值区域进行CPA。首先，我需要确定一个合适的区间。根据之前的分析，方差峰值在1102附近，让我在这个区域尝试CPA：

**🔧 → `python_jupyter`**

<details><summary>Code (1404 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载平滑后的波形
smoothed_wave = np.load('smoothed_20260424_045104_928599.npy')
mean_smoothed = smoothed_wave.mean(axis=0)
variance_smoothed = smoothed_wave.var(axis=0)

# 找到方差峰值
max_var_idx = np.argmax(variance_smoothed)
print(f"Smoothed variance peak at sample index: {max_var_idx}")
print(f"Smoothed variance peak value: {variance_smoothed[max_var_idx]:.2f}")

# 查看峰值附近的区域
window = 100
start = max(0, max_var_idx - window)
end = min(len(variance_smoothed), max_var_idx + window)

plt.figure(figsize=(12, 6))
plt.plot(variance_smoothed, 'r-', alpha=0.7, label='Variance (smoothed)')
plt.axvline(max_var_idx, color='r', linestyle='--', alpha=0.7, label=f'Variance peak ({max_var_idx})')
plt.axvspan(start, end, alpha=0.2, color='orange', label='Candidate region')
plt.xlabel('Sample index')
plt.ylabel('Variance')
plt.title('Variance of smoothed traces')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('smoothed_variance_region.png')
plt.show()

print(f"\nCandidate region for CPA: [{start}, {end}]")
print(f"Region length: {end - start} samples")

# 查看这个区域的平均波形特征
plt.figure(figsize=(12, 4))
plt.plot(mean_smoothed[start:end], 'b-')
plt.xlabel(f'Sample index (relative to {start})')
plt.ylabel('Amplitude')
plt.title(f'Average smoothed trace in region [{start}, {end}]')
plt.grid(True, alpha=0.3)
plt.savefig('candidate_region_waveform.png')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `Smoothed variance peak at sample index: 1105
Smoothed variance peak value: 3352.34

Candidate region for CPA: [1005, 1205]
Region length: 200 samples
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1439557766.py:29: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1439557766.py:42: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 9 | tokens: 24,509→423

**🤖 LLM:** 平滑后的方差峰值在1105附近，与原始波形的1102基本一致。现在让我在这个区域[1005, 1205]进行CPA。但首先，我需要提取这个区域的波形：

**🔧 → `python_jupyter`**

<details><summary>Code (919 chars)</summary>

```python
import numpy as np

# 加载平滑后的波形
smoothed_wave = np.load('smoothed_20260424_045104_928599.npy')

# 提取候选区域 [1005, 1205]
start_idx = 1005
end_idx = 1205
region_wave = smoothed_wave[:, start_idx:end_idx]

print(f"Original smoothed wave shape: {smoothed_wave.shape}")
print(f"Region wave shape: {region_wave.shape}")
print(f"Region length: {region_wave.shape[1]} samples")

# 保存区域波形
region_wave_path = 'region_wave.npy'
np.save(region_wave_path, region_wave)
print(f"Region wave saved to: {region_wave_path}")

# 也保存对应的明文和密文
plaintext = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy')
ciphertext = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy')

print(f"Plaintext shape: {plaintext.shape}")
print(f"Ciphertext shape: {ciphertext.shape}")
```
</details>

**📋 ← `python_jupyter`:** `Original smoothed wave shape: (250, 1500)
Region wave shape: (250, 200)
Region length: 200 samples
Region wave saved to: region_wave.npy
Plaintext shape: (250, 16)
Ciphertext shape: (250, 16)`


---

### Round 10 | tokens: 25,009→271

**🤖 LLM:** 现在我在方差峰值区域进行CPA：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "region_wave.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (3166 chars)</summary>

```
{"recovered_key": "931F6C447D9C920253401BCCA73B8D00", "cpa_avg_correlation": 0.2699, "cpa_min_correlation": 0.2158, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_045203_637755.png", "detail_file": "cpa_detail_20260424_045203_637755.json", "per_byte": [{"byte": 0, "key": "0x93", "correlation": 0.2639, "time_index": 124, "gap_pct": 11.2}, {"byte": 1, "key": "0x1F", "correlation": 0.2308, "time_index": 57, "gap_pct": 1.1}, {"byte": 2, "key": "0x6C", "correlation": 0.2299, "time_index": 21, "gap_pct": 0.1}, {"byte": 3, "key": "0x44", "correlation": 0.3648, "time_index": 34, "gap_pct": 36.1}, {"byte": 4, "key": "0x7D", "correlation": 0.2158, "time_index": 62, "gap_pct": 0.8}, {"byte": 5, "key": "0x9C", "correlation": 0.2693, "time_index": 23, "gap_pct": 15.3}, {"byte": 6, "key": "0x92", "correlation": 0.2571, "time_index": 52, "gap_pct": 3.4}, {"byte": 7, "key": "0x02", "correlation": 0.2362, "time_index": 124, "gap_pct": 3.7}, {"byte": 8, "key": "0x53", "correlation": 0.2846, "time_index": 10, "gap_pct": 12.9}, {"byte": 9, "key": "0x40", "correlation": 0.2644, "time_index": 51, "gap_pct": 9.5}, {"byte": 10, "key": "0x1B", "correlation": 0.2329, "time_index": 185, "gap_pct": 0.1}, {"byte": 11, "key": "0xCC", "correlation": 0.3546, "time_index": 18, "gap_pct": 31.9}, {"byte": 12, "key": "0xA7", "correlation": 0.249, "time_index": 79, "gap_pct": 7.7}, {"byte": 13, "key": "0x3B", "correlation": 0.2568, "time_index": 43, "gap_pct": 3.7}, {"byte": 14, "key":
...(truncated)
```
</details>


![cpa_result_20260424_045203_637755.png](./cpa_result_20260424_045203_637755.png)


---

### Round 11 | tokens: 26,690→614

**🤖 LLM:** 结果更差了，只有4/16个高置信度字节。让我检查一下是否需要对齐。根据DKG知识图谱，对于软件实现，我应该先尝试静态对齐。让我检查一下波形是否需要对齐：

**🔧 → `python_jupyter`**

<details><summary>Code (1540 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载原始波形
wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')

# 查看前10条波形在方差峰值区域附近
variance_peak = 1102
window = 50
start = max(0, variance_peak - window)
end = min(wave.shape[1], variance_peak + window)

plt.figure(figsize=(14, 8))
for i in range(10):
    plt.plot(wave[i, start:end], alpha=0.7, label=f'Trace {i}')
plt.xlabel(f'Sample index (relative to {start})')
plt.ylabel('Amplitude')
plt.title(f'First 10 traces in variance peak region [{start}, {end}]')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('trace_alignment_check.png')
plt.show()

# 计算这个区域内波形的互相关性
from scipy import signal

# 使用第一条轨迹作为参考
ref_trace = wave[0, start:end]
correlations = []

for i in range(1, 10):
    corr = signal.correlate(ref_trace, wave[i, start:end], mode='same')
    max_corr = np.max(corr)
    correlations.append(max_corr)
    print(f"Trace {i} max correlation with trace 0: {max_corr:.4f}")

print(f"\nAverage correlation: {np.mean(correlations):.4f}")
print(f"Std of correlations: {np.std(correlations):.4f}")

# 检查是否需要对齐 - 查看峰值位置是否一致
peak_positions = []
for i in range(10):
    region = wave[i, start:end]
    peak_pos = np.argmax(np.abs(region))  # 使用绝对值找到最大峰值
    peak_positions.append(peak_pos)
    print(f"Trace {i} peak position in region: {peak_pos}")

print(f"\nPeak position range: {min(peak_positions)} to {max(peak_positions)}")
print(f"Peak position std: {np.std(peak_positions):.2f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1098 chars)</summary>

```
Trace 1 max correlation with trace 0: 2430482.5000
Trace 2 max correlation with trace 0: 2263996.5000
Trace 3 max correlation with trace 0: 2468225.0000
Trace 4 max correlation with trace 0: 1882819.8750
Trace 5 max correlation with trace 0: 2225727.2500
Trace 6 max correlation with trace 0: 2158921.7500
Trace 7 max correlation with trace 0: 2500527.2500
Trace 8 max correlation with trace 0: 2121768.5000
Trace 9 max correlation with trace 0: 2127038.2500

Average correlation: 2242167.2500
Std of correlations: 187933.8906
Trace 0 peak position in region: 69
Trace 1 peak position in region: 61
Trace 2 peak position in region: 59
Trace 3 peak position in region: 64
Trace 4 peak position in region: 46
Trace 5 peak position in region: 66
Trace 6 peak position in region: 62
Trace 7 peak position in region: 66
Trace 8 peak position in region: 54
Trace 9 peak position in region: 52

Peak position range: 46 to 69
Peak position std: 6.86
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1818022706.py:22: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 12 | tokens: 27,685→398

**🤖 LLM:** 峰值位置在46到69之间变化，标准差为6.86个样本点，这表明存在一定的对齐需求。根据DKG知识图谱的"alignment max_shift should start large (300+), not default to small"原则，对于MCU，我应该使用较大的max_shift（150-200）。让我尝试静态对齐：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "start": 1102,
  "length": 100,
  "max_shift": 200,
  "threshold": 85,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_045250_973767.npy", "plot_path": "align_overlay_20260424_045250_973767.png", "ref_trace_used": 125, "accepted": 250, "discarded": 0, "total": 250, "out_plaintext_npy": "plaintext_aligned_20260424_045250_973767.npy", "plaintext_traces": 250, "out_ciphertext_npy": "ciphertext_aligned_20260424_045250_973767.npy", "ciphertext_traces": 250, "alignment_avg_correlation": 0.9921, "alignment_min_correlation": 0.8883, "acceptance_rate": 1.0}`


![align_overlay_20260424_045250_973767.png](./align_overlay_20260424_045250_973767.png)


---

### Round 13 | tokens: 28,281→213

**🤖 LLM:** 很好！对齐成功，接受了所有250条轨迹，平均相关性为0.9921。现在让我在对齐后的波形上进行CPA：

**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_045250_973767.npy",
  "wave_npy": "aligned_20260424_045250_973767.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_045250_973767.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2050 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.4366, "cpa_min_correlation": 0.3515, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_045305_006977.png", "detail_file": "cpa_detail_20260424_045305_006977.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.4243, "time_index": 582, "gap_pct": 34.1}, {"byte": 1, "key": "0x22", "correlation": 0.3877, "time_index": 633, "gap_pct": 30.0}, {"byte": 2, "key": "0x33", "correlation": 0.3515, "time_index": 924, "gap_pct": 26.2}, {"byte": 3, "key": "0x44", "correlation": 0.4731, "time_index": 1040, "gap_pct": 44.7}, {"byte": 4, "key": "0x55", "correlation": 0.4226, "time_index": 592, "gap_pct": 33.2}, {"byte": 5, "key": "0x66", "correlation": 0.4109, "time_index": 821, "gap_pct": 32.1}, {"byte": 6, "key": "0x77", "correlation": 0.4536, "time_index": 929, "gap_pct": 37.9}, {"byte": 7, "key": "0x88", "correlation": 0.4322, "time_index": 958, "gap_pct": 29.7}, {"byte": 8, "key": "0x99", "correlation": 0.4214, "time_index": 604, "gap_pct": 34.4}, {"byte": 9, "key": "0xAA", "correlation": 0.4648, "time_index": 829, "gap_pct": 40.0}, {"byte": 10, "key": "0xBB", "correlation": 0.4495, "time_index": 1111, "gap_pct": 36.3}, {"byte": 11, "key": "0xCC", "correlation": 0.4951, "time_index": 995, "gap_pct": 36.4}, {"byte": 12, "key": "0xDD", "correlation": 0.3781, "time_index": 613, "gap_pct": 21.7}, {"byte": 13, "key": "0xEE", "correlation": 0.4515, "time_index": 836, "gap_pct": 33.
...(truncated)
```
</details>


![cpa_result_20260424_045305_006977.png](./cpa_result_20260424_045305_006977.png)


---

### Round 14 | tokens: 29,364→215

**🤖 LLM:** 太好了！对齐后的CPA结果非常好：16/16个字节都是高置信度的，平均相关性提高到0.4366。恢复的密钥是`112233445566778899AABBCCDDEEFF00`。让我验证这个密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "algorithm": "AES",
  "plaintext_npy": "plaintext_aligned_20260424_045250_973767.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_045250_973767.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "17EAF0DCB9E3BC6F7A83D9F769BFC973", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 17EAF0DCB9E3BC6F7A83D9F769BFC973...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 15 | tokens: 29,722→592

<details><summary><b>🤖 LLM Reasoning</b> (1188 chars)</summary>

完美！密钥验证成功！我们成功恢复了STM32F103 MCU软件实现的AES-128密钥：`112233445566778899AABBCCDDEEFF00`。

让我总结一下攻击过程：

## 攻击总结

**目标**: STM32F103 MCU软件实现的AES-128
**数据**: 250条轨迹，每条1500个采样点
**恢复的密钥**: `112233445566778899AABBCCDDEEFF00`

### 攻击步骤：

1. **初始分析**: 加载数据并检查波形特征，发现方差峰值在样本1102附近。

2. **第一次CPA尝试**: 在全波形上直接进行CPA，只恢复了6/16个高置信度字节，平均相关性0.3177。

3. **区域定位**: 
   - 明文相关性分析显示峰值在606附近
   - 密文相关性分析显示峰值在659附近  
   - 方差分析显示峰值在1102附近
   - 根据DKG知识图谱的"Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI"原则，选择方差峰值区域作为攻击目标

4. **波形平滑**: 使用权重为3的加权移动平均进行平滑滤波。

5. **区域CPA尝试**: 在方差峰值区域[1005, 1205]进行CPA，结果更差（4/16高置信度字节）。

6. **对齐检查**: 检查波形发现峰值位置有偏移（标准差6.86个样本），需要对齐。

7. **静态对齐**: 在方差峰值1102处进行静态对齐，使用参数：length=100, max_shift=200, threshold=85。成功对齐所有250条轨迹，平均相关性0.9921。

8. **最终CPA**: 在对齐后的波形上进行CPA，成功恢复所有16个字节，平均相关性0.4366，所有字节的gap_pct都超过15%。

9. **密钥验证**: 验证成功，恢复的密钥完全正确。

### 关键成功因素：

1. **遵循DKG知识图谱原则**:
   - 对于软件实现，优先使用方差ROI而不是明文/密文相关性ROI
   - 使用较大的max_shift（200）进行对齐
   - 对于MCU软件实现，使用S-box_out + HW模型

2. **正确的预处理顺序**:
   - 先进行方差分析定位加密区域
   - 然后进行静态对齐
   - 最后进行CPA攻击

3. **参数选择合理**:
   - 对齐参考点选择在方差峰值处（1102）
   - 使用适当的对齐长度（100）和阈值（85）

这个案例展示了DKG知识图谱在实际SCA攻击中的价值，特别是关于区域选择和预处理顺序的指导原则。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 16,706 | 990 | 17,696 |
| 2 | 18,188 | 474 | 18,662 |
| 3 | 19,975 | 304 | 20,279 |
| 4 | 20,651 | 299 | 20,950 |
| 5 | 21,105 | 276 | 21,381 |
| 6 | 21,539 | 988 | 22,527 |
| 7 | 22,704 | 372 | 23,076 |
| 8 | 23,803 | 542 | 24,345 |
| 9 | 24,509 | 423 | 24,932 |
| 10 | 25,009 | 271 | 25,280 |
| 11 | 26,690 | 614 | 27,304 |
| 12 | 27,685 | 398 | 28,083 |
| 13 | 28,281 | 213 | 28,494 |
| 14 | 29,364 | 215 | 29,579 |
| 15 | 29,722 | 592 | 30,314 |
| **Total** | **355,931** | **6,971** | **362,902** |

## 8. Final Output

完美！密钥验证成功！我们成功恢复了STM32F103 MCU软件实现的AES-128密钥：`112233445566778899AABBCCDDEEFF00`。

让我总结一下攻击过程：

## 攻击总结

**目标**: STM32F103 MCU软件实现的AES-128
**数据**: 250条轨迹，每条1500个采样点
**恢复的密钥**: `112233445566778899AABBCCDDEEFF00`

### 攻击步骤：

1. **初始分析**: 加载数据并检查波形特征，发现方差峰值在样本1102附近。

2. **第一次CPA尝试**: 在全波形上直接进行CPA，只恢复了6/16个高置信度字节，平均相关性0.3177。

3. **区域定位**: 
   - 明文相关性分析显示峰值在606附近
   - 密文相关性分析显示峰值在659附近  
   - 方差分析显示峰值在1102附近
   - 根据DKG知识图谱的"Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI"原则，选择方差峰值区域作为攻击目标

4. **波形平滑**: 使用权重为3的加权移动平均进行平滑滤波。

5. **区域CPA尝试**: 在方差峰值区域[1005, 1205]进行CPA，结果更差（4/16高置信度字节）。

6. **对齐检查**: 检查波形发现峰值位置有偏移（标准差6.86个样本），需要对齐。

7. **静态对齐**: 在方差峰值1102处进行静态对齐，使用参数：length=100, max_shift=200, threshold=85。成功对齐所有250条轨迹，平均相关性0.9921。

8. **最终CPA**: 在对齐后的波形上进行CPA，成功恢复所有16个字节，平均相关性0.4366，所有字节的gap_pct都超过15%。

9. **密钥验证**: 验证成功，恢复的密钥完全正确。

### 关键成功因素：

1. **遵循DKG知识图谱原则**:
   - 对于软件实现，优先使用方差ROI而不是明文/密文相关性ROI
   - 使用较大的max_shift（200）进行对齐
   - 对于MCU软件实现，使用S-box_out + HW模型

2. **正确的预处理顺序**:
   - 先进行方差分析定位加密区域
   - 然后进行静态对齐
   - 最后进行CPA攻击

3. **参数选择合理**:
   - 对齐参考点选择在方差峰值处（1102）
   - 使用适当的对齐长度（100）和阈值（85）

这个案例展示了DKG知识图谱在实际SCA攻击中的价值，特别是关于区域选择和预处理顺序的指导原则。
