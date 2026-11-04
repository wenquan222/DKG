# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Qwen/Qwen3.5-397B-A17B` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_055715_844 |
| Duration | 200.1s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_Qwen3.5-397B\AES-STM32F103_Qwen3.5-397B-A17B_DKG_20260424_055715_844` |
| Total LLM Calls | 12 |
| First Round | prompt: 17,086, completion: 1,101 |
| Last Round | prompt: 29,479, completion: 866 |
| Total Tokens | 292,848 (prompt: 285,521, completion: 7,327) |

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

LLM Response: ["AES", "STM32F103", "MCU", "Power", "CPA", "Hamming Weight", "S-box Output"]

Parsed Keywords: `["AES", "STM32F103", "MCU", "Power", "CPA", "Hamming Weight", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 40740 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (43038 chars, click to expand)</summary>

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

**Search keywords** (7): AES, STM32F103, MCU, Power, CPA, Hamming Weight, S-box Output

**Summary**: 38 upper entities, 29 relationships, 15 diagnostic chains, 14 strategies


## 1. Upper Layer Entities (38)


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

### LeakageModel (5)

- **Hamming Weight** — requirements=software implementation
- **Hamming Weight (bit-based)** — requirements=bit-based
- **Hamming Weight of transitions**
- **Hamming weight**
- **Hamming weight of fused features**

### Pipeline (8)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, canonical_source=round1_patch_002, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

### StatMethod (7)

- **Compare hypothetical power consumption with measured traces** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Generate Hamming weight models for S-box output** — type=non_profiled

## 2. Relationships (29)

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
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Callback function called at reporting interval (default 25), condition=to get feedback during attack, source_text=Monitor attack progress with callback, support_count=1]]→ `DiagnosticMethod:Monitor attack progress with callback`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use output_vs_time method to plot correlation of guesses over time, condition=to locate leakage in time, source_text=Plot Output Vs. Time, support_count=1]]→ `DiagnosticMethod:Plot Output Vs. Time`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use pge_vs_trace method to plot partial guessing entropy, condition=to see attack progression, source_text=Plot PGE vs. Traces, support_count=1]]→ `DiagnosticMethod:Plot PGE vs. Traces`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use corr_vs_trace method to plot correlation values, condition=to compare correct key guess with incorrect ones, source_text=Plot Correlation vs. Traces, support_count=1]]→ `DiagnosticMethod:Plot Correlation vs. Traces`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use cpa() function with project and leakage model, source_text=Run CPA attack, support_count=1, is_optional=False]]→ `StatMethod:CPA`
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

## 3. Diagnostic Chains (15)


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

### Obs: `key_byte_distinguishability` — any
- **Cause** (high): Different key bytes (e.g., 0x55 and 0xAA) can have the same Hamming weight, making them indistinguishable if attacking the key directly. The S-box output provides a nonlinear transformation that spreads the Hamming weights, creating a unique signature for each key hypothesis.
- **Action**: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.
  - operation: `switch_component`
  - target: `attack point`
  - strategy: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.

### Obs: `leakage_model_selection` — any
- **Cause** (high): Non-linear operations (e.g., S-box) have stronger power consumption leakage than linear transformations
- **Check**: Compare correlation strength between S-box output and linear operation points
- **Action**: Choose S-box output as intermediate value for CPA or machine learning attacks
  - operation: `switch_component`
  - target: `intermediate_value`
  - strategy: Choose the S-box output (the value after XOR with round key and before linear transformation) as the intermediate value for CPA or machine learning attacks.
- **Relates to**: AttackPoint:`S-box Output`

## 4. Strategies (14)


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

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_Qwen3.5-397B\AES-STM32F103_Qwen3.5-397B-A17B_DKG_20260424_055715_844
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_Qwen3.5-397B\AES-STM32F103_Qwen3.5-397B-A17B_DKG_20260424_055715_844/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 17,086→1,101

**🤖 LLM:** 

我将对STM32F103 MCU软件实现的AES进行CPA攻击。根据知识图谱和SCA最佳实践，我会采用标准流程：先探索波形特征，然后直接CPA探测，根据结果决定是否需要预处理。

让我先检查文件并分析波形特征：



**🔧 → `python_jupyter`**

<details><summary>Code (1947 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载文件
wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')
plain = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy')
cipher = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy')

print(f"波形形状: {wave.shape}")
print(f"明文形状: {plain.shape}")
print(f"密文形状: {cipher.shape}")
print(f"波形数据类型: {wave.dtype}")
print(f"明文数据类型: {plain.dtype}")
print(f"密文数据类型: {cipher.dtype}")

# 查看前几条波形的统计特征
print(f"\n波形统计 (所有traces):")
print(f"  均值: {wave.mean():.4f}")
print(f"  标准差: {wave.std():.4f}")
print(f"  最小值: {wave.min():.4f}")
print(f"  最大值: {wave.max():.4f}")

# 计算每条trace的基线标准差（前100点作为非加密区参考）
baseline_std = wave[:, :100].std(axis=1).mean()
print(f"\n基线区域(0-100)平均标准差: {baseline_std:.4f}")

# 绘制前5条波形查看特征
plt.figure(figsize=(15, 5))
for i in range(5):
    plt.plot(wave[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.title('First 5 Power Traces - AES-128 STM32F103')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('waveform_overview.png', dpi=150)
plt.show()

# 计算方差图定位加密区域（滑动窗口）
window_size = 50
variance_profile = np.zeros(wave.shape[1] - window_size)
for i in range(wave.shape[1] - window_size):
    variance_profile[i] = wave[:, i:i+window_size].var()

plt.figure(figsize=(15, 4))
plt.plot(variance_profile)
plt.xlabel('Sample Point (sliding window)')
plt.ylabel('Variance')
plt.title(f'Variance Profile (window={window_size}) - Look for peaks indicating encryption')
plt.grid(True, alpha=0.3)
plt.savefig('variance_profile.png', dpi=150)
plt.show()

# 找到方差最大的区域
peak_idx = np.argmax(variance_profile)
print(f"\n方差峰值位置: {peak_idx}")
print(f"峰值方差: {variance_profile[peak_idx]:.4f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (547 chars)</summary>

```
波形形状: (250, 1500)
明文形状: (250, 16)
密文形状: (250, 16)
波形数据类型: float32
明文数据类型: uint8
密文数据类型: uint8

波形统计 (所有traces):
  均值: -131.3288
  标准差: 61.4955
  最小值: -342.5197
  最大值: 90.5512

基线区域(0-100)平均标准差: 36.5667

方差峰值位置: 1075
峰值方差: 5847.7388
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\3184606405.py:37: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\3184606405.py:52: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 18,282→476

**🤖 LLM:** 

波形分析完成：
- 250条trace，1500点/条
- 方差峰值在sample 1075附近，这是加密操作的核心区域
- 基线标准差约36.6，属于正常软件MCU噪声水平

根据知识图谱建议，软件MCU实现应先进行直接CPA探测，使用S-box_out + HW模型。让我先执行直接CPA：



**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "leakage_model": "HW",
  "target": "S-box_out",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2994 chars)</summary>

```
{"recovered_key": "11ECD6443566920D5339BBCC4EEEFF00", "cpa_avg_correlation": 0.3177, "cpa_min_correlation": 0.2679, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_055905_155866.png", "detail_file": "cpa_detail_20260424_055905_155866.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3251, "time_index": 586, "gap_pct": 14.4}, {"byte": 1, "key": "0xEC", "correlation": 0.2679, "time_index": 823, "gap_pct": 1.3}, {"byte": 2, "key": "0xD6", "correlation": 0.3516, "time_index": 492, "gap_pct": 21.1}, {"byte": 3, "key": "0x44", "correlation": 0.3574, "time_index": 1038, "gap_pct": 19.1}, {"byte": 4, "key": "0x35", "correlation": 0.2881, "time_index": 168, "gap_pct": 4.2}, {"byte": 5, "key": "0x66", "correlation": 0.3694, "time_index": 823, "gap_pct": 23.8}, {"byte": 6, "key": "0x92", "correlation": 0.3066, "time_index": 91, "gap_pct": 3.9}, {"byte": 7, "key": "0x0D", "correlation": 0.2767, "time_index": 446, "gap_pct": 3.9}, {"byte": 8, "key": "0x53", "correlation": 0.2897, "time_index": 1012, "gap_pct": 0.7}, {"byte": 9, "key": "0x39", "correlation": 0.2711, "time_index": 240, "gap_pct": 2.2}, {"byte": 10, "key": "0xBB", "correlation": 0.3862, "time_index": 913, "gap_pct": 30.6}, {"byte": 11, "key": "0xCC", "correlation": 0.3413, "time_index": 1021, "gap_pct": 11.6}, {"byte": 12, "key": "0x4E", "correlation": 0.27, "time_index": 338, "gap_pct": 1.1}, {"byte": 13, "key": "0xEE", "correlation": 0.333, "time_index": 862, "gap_pct": 21.0}, {"byte
...(truncated)
```
</details>


![cpa_result_20260424_055905_155866.png](./cpa_result_20260424_055905_155866.png)


---

### Round 3 | tokens: 20,117→881

**🤖 LLM:** 

直接CPA结果显示：
- 恢复密钥：`11ECD6443566920D5339BBCC4EEEFF00`
- 高置信度字节：6/16（红色区域，<10/16）
- 平均相关系数：0.3177（尚可）
- 多个字节gap_pct很低（如byte 8只有0.7%，byte 1只有1.3%）

根据知识图谱的"variance-first ROI exploration"原则，我应该先定位方差峰值区域（1075附近），然后检查CPA结果中各字节的时间分布，看是否集中在正确区域。让我先分析CPA detail文件，看看时间索引分布：



**🔧 → `python_jupyter`**

<details><summary>Code (1757 chars)</summary>

```python
import json
import numpy as np
import matplotlib.pyplot as plt

# 加载CPA detail
with open('cpa_detail_20260424_055905_155866.json', 'r') as f:
    cpa_detail = json.load(f)

# 提取每个字节的最佳key、correlation、time_index、gap_pct
bytes_info = cpa_detail['per_byte']
time_indices = [b['time_index'] for b in bytes_info]
correlations = [b['correlation'] for b in bytes_info]
gaps = [b['gap_pct'] for b in bytes_info]
keys = [b['key'] for b in bytes_info]

print("各字节CPA结果:")
print(f"{'Byte':<5} {'Key':<6} {'Corr':<8} {'Time':<8} {'Gap%':<8} {'Confidence'}")
print("-" * 50)
for i, b in enumerate(bytes_info):
    conf = "HIGH" if b['gap_pct'] > 0.15 else ("MED" if b['gap_pct'] > 0.05 else "LOW")
    print(f"{i:<5} {b['key']:<6} {b['correlation']:.4f}   {b['time_index']:<8} {b['gap_pct']*100:<8.2f} {conf}")

# 绘制时间索引分布
plt.figure(figsize=(15, 4))
plt.scatter(range(16), time_indices, c=correlations, cmap='viridis', s=100)
for i, (t, c, g) in enumerate(zip(time_indices, correlations, gaps)):
    conf_color = 'green' if g > 0.15 else ('orange' if g > 0.05 else 'red')
    plt.annotate(f'{i}:{t}', (i, t), fontsize=8, color=conf_color)
plt.xlabel('Key Byte Index')
plt.ylabel('Time Index (sample point)')
plt.title('CPA Time Index Distribution per Byte')
plt.grid(True, alpha=0.3)
plt.savefig('cpa_time_distribution.png', dpi=150)
plt.show()

# 检查时间索引是否集中在方差峰值区域(1075附近)
print(f"\n方差峰值区域: ~1075")
print(f"CPA时间索引范围: {min(time_indices)} - {max(time_indices)}")
print(f"时间索引在1000-1200范围内的字节: {[i for i, t in enumerate(time_indices) if 1000 <= t <= 1200]}")

# 查看高置信度字节的时间分布
high_conf_bytes = [i for i, b in enumerate(bytes_info) if b['gap_pct'] > 0.15]
print(f"\n高置信度字节(>15% gap): {high_conf_bytes}")
print(f"高置信度字节的时间索引: {[time_indices[i] for i in high_conf_bytes]}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[300][39m[32m, line 10[39m
[32m      7[39m     cpa_detail = json.load(f)
[32m      9[39m [38;5;66;03m# 提取每个字节的最佳key、correlation、time_index、gap_pct[39;00m
[32m---> [39m[32m10[39m bytes_info = [43mcpa_detail[49m[43m[[49m[33;43m'[39;49m[33;43mper_byte[39;49m[33;43m'[39;49m[43m][49m
[32m     11[39m time_indices = [b[[33m'[39m[33mtime_index[39m[33m'[39m] [38;5;28;01mfor[39;00m b [38;5;129;01min[39;00m bytes_info]
[32m     12[39m correlations = [b[[33m'[39m[33mcorrelation[39m[33m'[39m] [38;5;28;01mfor[39;00m b [38;5;129;01min[39;00m bytes_info]

[31mKeyError[39m: 'per_byte'
```


---

### Round 4 | tokens: 21,467→137

**🤖 LLM:** 

让我检查CPA detail文件的实际结构：



**🔧 → `python_jupyter`**

<details><summary>Code (243 chars)</summary>

```python
import json

with open('cpa_detail_20260424_055905_155866.json', 'r') as f:
    cpa_detail = json.load(f)

print("CPA detail文件顶层键:")
print(list(cpa_detail.keys()))

# 查看文件内容结构
import pprint
print("\n文件内容预览:")
pprint.pprint(cpa_detail, depth=2)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (528 chars)</summary>

```
CPA detail文件顶层键:
['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results']

文件内容预览:
{'corr_mode': 'abs',
 'leakage_model': 'HW',
 'n_points': 1500,
 'n_traces': 250,
 'results': [{...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...},
             {...}],
 'target': 'S-box_out'}
```
</details>


---

### Round 5 | tokens: 21,774→933

**🤖 LLM:** 



**🔧 → `python_jupyter`**

<details><summary>Code (2405 chars)</summary>

```python
import json
import numpy as np
import matplotlib.pyplot as plt

# 加载CPA detail
with open('cpa_detail_20260424_055905_155866.json', 'r') as f:
    cpa_detail = json.load(f)

# results是列表，每个元素对应一个字节
results = cpa_detail['results']
print(f"results长度: {len(results)}")
print(f"第一个字节结果键: {list(results[0].keys())}")

# 提取每个字节的信息
time_indices = []
correlations = []
gaps = []
keys = []

for i, r in enumerate(results):
    byte_idx = r['byte']
    best_candidate = r['candidates'][0]  # 最佳候选
    key = best_candidate['key']
    corr = best_candidate['correlation']
    time_idx = best_candidate['time_index']
    
    # 计算gap (top1 - top2)
    if len(r['candidates']) >= 2:
        top1_corr = r['candidates'][0]['correlation']
        top2_corr = r['candidates'][1]['correlation']
        gap = top1_corr - top2_corr
    else:
        gap = 0
    
    time_indices.append(time_idx)
    correlations.append(corr)
    gaps.append(gap)
    keys.append(key)

print("\n各字节CPA结果:")
print(f"{'Byte':<5} {'Key':<6} {'Corr':<8} {'Time':<8} {'Gap':<8} {'Gap%':<8} {'Confidence'}")
print("-" * 65)
for i in range(16):
    gap_pct = gaps[i] / correlations[i] if correlations[i] > 0 else 0
    conf = "HIGH" if gap_pct > 0.15 else ("MED" if gap_pct > 0.05 else "LOW")
    print(f"{i:<5} 0x{keys[i]:02X}   {correlations[i]:.4f}   {time_indices[i]:<8} {gaps[i]:.4f}   {gap_pct*100:<8.2f} {conf}")

# 绘制时间索引分布
plt.figure(figsize=(15, 4))
plt.scatter(range(16), time_indices, c=correlations, cmap='viridis', s=100)
for i, (t, c, g) in enumerate(zip(time_indices, correlations, gaps)):
    gap_pct = g / c if c > 0 else 0
    conf_color = 'green' if gap_pct > 0.15 else ('orange' if gap_pct > 0.05 else 'red')
    plt.annotate(f'{i}:{t}', (i, t), fontsize=8, color=conf_color)
plt.xlabel('Key Byte Index')
plt.ylabel('Time Index (sample point)')
plt.title('CPA Time Index Distribution per Byte')
plt.grid(True, alpha=0.3)
plt.savefig('cpa_time_distribution.png', dpi=150)
plt.show()

# 检查时间索引是否集中在方差峰值区域(1075附近)
print(f"\n方差峰值区域: ~1075")
print(f"CPA时间索引范围: {min(time_indices)} - {max(time_indices)}")
print(f"时间索引在1000-1200范围内的字节: {[i for i, t in enumerate(time_indices) if 1000 <= t <= 1200]}")

# 查看高置信度字节
high_conf_bytes = [i for i in range(16) if (gaps[i]/correlations[i] if correlations[i]>0 else 0) > 0.15]
print(f"\n高置信度字节(>15% gap): {high_conf_bytes}")
print(f"高置信度字节的时间索引: {[time_indices[i] for i in high_conf_bytes]}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
results长度: 16
第一个字节结果键: ['byte', 'topK', 'best_key']

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mKeyError[39m                                  Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[302][39m[32m, line 22[39m
[32m     20[39m [38;5;28;01mfor[39;00m i, r [38;5;129;01min[39;00m [38;5;28menumerate[39m(results):
[32m     21[39m     byte_idx = r[[33m'[39m[33mbyte[39m[33m'[39m]
[32m---> [39m[32m22[39m     best_candidate = [43mr[49m[43m[[49m[33;43m'[39;49m[33;43mcandidates[39;49m[33;43m'[39;49m[43m][49m[[32m0[39m]  [38;5;66;03m# 最佳候选[39;00m
[32m     23[39m     key = best_candidate[[33m'[39m[33mkey[39m[33m'[39m]
[32m     24[39m     corr = best_candidate[[33m'[39m[33mcorrelation[39m[33m'[39m]

[31mKeyError[39m: 'candidates'
```


---

### Round 6 | tokens: 23,194→116

**🤖 LLM:** 



**🔧 → `python_jupyter`**

<details><summary>Code (208 chars)</summary>

```python
import json

with open('cpa_detail_20260424_055905_155866.json', 'r') as f:
    cpa_detail = json.load(f)

# 查看第一个字节结果的完整结构
print("第一个字节结果完整内容:")
import pprint
pprint.pprint(cpa_detail['results'][0], depth=4)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1487 chars)</summary>

```
第一个字节结果完整内容:
{'best_key': 17,
 'byte': 0,
 'topK': [{'key': 17, 'score': 0.3250724366280273, 'time_index': 586},
          {'key': 198, 'score': 0.27818509875717523, 'time_index': 686},
          {'key': 58, 'score': 0.26933490809232236, 'time_index': 70},
          {'key': 147, 'score': 0.2683197316967659, 'time_index': 1126},
          {'key': 21, 'score': 0.26772015112301584, 'time_index': 473},
          {'key': 232, 'score': 0.2633013693864752, 'time_index': 709},
          {'key': 109, 'score': 0.25262450607327475, 'time_index': 1311},
          {'key': 175, 'score': 0.2510898053513292, 'time_index': 1294},
          {'key': 229, 'score': 0.24836878174680724, 'time_index': 856},
          {'key': 47, 'score': 0.24413088316825435, 'time_index': 516},
          {'key': 219, 'score': 0.24410301905807874, 'time_index': 609},
          {'key': 182, 'score': 0.24372717478215877, 'time_index': 355},
          {'key': 93, 'score': 0.24102453923431377, 'time_index': 608},
          {'key': 53, 'score': 0.23968284060151285, 'time_index': 1214},
          {'key': 116, 'score': 0.23571139856458417, 'time_index': 388},
          {'key': 12, 'score': 0.235336743592682, 'time_index': 518},
          {'key': 247, 'score': 0.23310098937769885, 'time_index': 274},
          {'key': 2, 'score': 0.23074203119635264, 'time_index': 814},
          {'key': 227, 'score': 0.22971521325743305, 'time_index': 658},
          {'key': 8, 'score': 0.2290662770864723, 'time_index': 677}]}
```
</details>


---

### Round 7 | tokens: 24,197→946

**🤖 LLM:** 

现在我了解了结构。让我重新分析：



**🔧 → `python_jupyter`**

<details><summary>Code (2328 chars)</summary>

```python
import json
import numpy as np
import matplotlib.pyplot as plt

# 加载CPA detail
with open('cpa_detail_20260424_055905_155866.json', 'r') as f:
    cpa_detail = json.load(f)

results = cpa_detail['results']

# 提取每个字节的信息
time_indices = []
correlations = []
gaps = []
keys = []

for i, r in enumerate(results):
    byte_idx = r['byte']
    best_key = r['best_key']
    topK = r['topK']
    
    key = topK[0]['key']
    corr = topK[0]['score']
    time_idx = topK[0]['time_index']
    
    # 计算gap (top1 - top2)
    if len(topK) >= 2:
        top1_corr = topK[0]['score']
        top2_corr = topK[1]['score']
        gap = top1_corr - top2_corr
    else:
        gap = 0
    
    time_indices.append(time_idx)
    correlations.append(corr)
    gaps.append(gap)
    keys.append(key)

print("各字节CPA结果:")
print(f"{'Byte':<5} {'Key':<6} {'Corr':<8} {'Time':<8} {'Gap':<8} {'Gap%':<8} {'Confidence'}")
print("-" * 65)
for i in range(16):
    gap_pct = gaps[i] / correlations[i] if correlations[i] > 0 else 0
    conf = "HIGH" if gap_pct > 0.15 else ("MED" if gap_pct > 0.05 else "LOW")
    print(f"{i:<5} 0x{keys[i]:02X}   {correlations[i]:.4f}   {time_indices[i]:<8} {gaps[i]:.4f}   {gap_pct*100:<8.2f} {conf}")

# 绘制时间索引分布
plt.figure(figsize=(15, 4))
plt.scatter(range(16), time_indices, c=correlations, cmap='viridis', s=100)
for i, (t, c, g) in enumerate(zip(time_indices, correlations, gaps)):
    gap_pct = g / c if c > 0 else 0
    conf_color = 'green' if gap_pct > 0.15 else ('orange' if gap_pct > 0.05 else 'red')
    plt.annotate(f'{i}:{t}', (i, t), fontsize=8, color=conf_color)
plt.xlabel('Key Byte Index')
plt.ylabel('Time Index (sample point)')
plt.title('CPA Time Index Distribution per Byte')
plt.grid(True, alpha=0.3)
plt.savefig('cpa_time_distribution.png', dpi=150)
plt.show()

# 检查时间索引是否集中在方差峰值区域(1075附近)
print(f"\n方差峰值区域: ~1075")
print(f"CPA时间索引范围: {min(time_indices)} - {max(time_indices)}")
print(f"时间索引在1000-1200范围内的字节: {[i for i, t in enumerate(time_indices) if 1000 <= t <= 1200]}")

# 查看高置信度字节
high_conf_bytes = [i for i in range(16) if (gaps[i]/correlations[i] if correlations[i]>0 else 0) > 0.15]
print(f"\n高置信度字节(>15% gap): {high_conf_bytes}")
print(f"高置信度字节的时间索引: {[time_indices[i] for i in high_conf_bytes]}")

# 恢复的密钥
recovered_key = ''.join([f'{k:02X}' for k in keys])
print(f"\n恢复的密钥: {recovered_key}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1348 chars)</summary>

```
各字节CPA结果:
Byte  Key    Corr     Time     Gap      Gap%     Confidence
-----------------------------------------------------------------
0     0x11   0.3251   586      0.0469   14.42    MED
1     0xEC   0.2679   823      0.0035   1.32     LOW
2     0xD6   0.3516   492      0.0740   21.06    HIGH
3     0x44   0.3574   1038     0.0681   19.06    HIGH
4     0x35   0.2881   168      0.0122   4.24     LOW
5     0x66   0.3694   823      0.0880   23.82    HIGH
6     0x92   0.3066   91       0.0121   3.94     LOW
7     0x0D   0.2767   446      0.0109   3.93     LOW
8     0x53   0.2897   1012     0.0019   0.65     LOW
9     0x39   0.2711   240      0.0059   2.19     LOW
10    0xBB   0.3862   913      0.1182   30.59    HIGH
11    0xCC   0.3413   1021     0.0396   11.59    MED
12    0x4E   0.2700   338      0.0030   1.12     LOW
13    0xEE   0.3330   862      0.0698   20.97    HIGH
14    0xFF   0.3131   895      0.0413   13.20    MED
15    0x00   0.3369   1015     0.0587   17.41    HIGH

方差峰值区域: ~1075
CPA时间索引范围: 91 - 1038
时间索引在1000-1200范围内的字节: [3, 8, 11, 15]

高置信度字节(>15% gap): [2, 3, 5, 10, 13, 15]
高置信度字节的时间索引: [492, 1038, 823, 913, 862, 1015]

恢复的密钥: 11ECD6443566920D5339BBCC4EEEFF00
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\2161672857.py:59: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 8 | tokens: 26,001→839

**🤖 LLM:** 

分析结果显示：
- 时间索引分散在91-1038之间，没有集中在方差峰值1075附近
- 高置信度字节只有6个（2,3,5,10,13,15），处于红色区域
- 时间索引分布很散，说明可能存在对齐问题

根据知识图谱的"variance-first ROI"原则，我应该：
1. 先使用方差峰值区域（1075附近）作为参考点进行静态对齐
2. 然后重新进行CPA

让我先查看波形在1075附近的特征，确定合适的对齐参数：



**🔧 → `python_jupyter`**

<details><summary>Code (1696 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')

# 查看方差峰值附近的波形特征
# 方差峰值在1075，查看1000-1200区域
plt.figure(figsize=(15, 6))

# 绘制前10条波形在900-1200区域的叠加
for i in range(10):
    plt.plot(range(900, 1200), wave[i, 900:1200], alpha=0.5, label=f'Trace {i}' if i<5 else '')

plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.title('Waveform Overlay in Region 900-1200 (Variance Peak ~1075)')
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)
plt.savefig('waveform_900_1200.png', dpi=150)
plt.show()

# 计算平均波形查看特征
avg_wave = wave.mean(axis=0)
std_wave = wave.std(axis=0)

plt.figure(figsize=(15, 4))
plt.plot(avg_wave, label='Mean')
plt.plot(avg_wave + std_wave, 'r--', alpha=0.5, label='Mean + Std')
plt.plot(avg_wave - std_wave, 'r--', alpha=0.5, label='Mean - Std')
plt.axvline(x=1075, color='green', linestyle=':', label='Variance Peak')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.title('Average Waveform with Std Deviation')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('avg_waveform.png', dpi=150)
plt.show()

# 查看前200点的基线区域
plt.figure(figsize=(15, 4))
for i in range(5):
    plt.plot(wave[i, :200], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.title('Baseline Region (0-200) - Check for DC drift')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('baseline_region.png', dpi=150)
plt.show()

# 检查基线是否有明显的DC漂移（软件MCU通常不需要垂直对齐）
baseline_means = wave[:, :100].mean(axis=1)
print(f"基线均值分布: min={baseline_means.min():.2f}, max={baseline_means.max():.2f}, std={baseline_means.std():.2f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (511 chars)</summary>

```
基线均值分布: min=-90.04, max=15.87, std=11.14
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\412562053.py:20: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\412562053.py:37: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\412562053.py:49: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 9 | tokens: 27,058→546

**🤖 LLM:** 

基线均值标准差约11.14，对于软件MCU实现来说属于正常噪声范围，不需要垂直对齐（知识图谱明确指出软件实现默认不需要垂直对齐）。

现在我需要进行静态对齐。根据知识图谱：
- 对齐参考点应该在加密区间内，选择方差峰值附近的一个特征峰
- 对于接触式智能卡/AES，推荐参数：length=100-120, max_shift=300-400, threshold=85
- 参考点应该选在加密区域内，而不是全局最大值

从CPA结果看，高置信度字节的时间索引在492, 823, 862, 913, 1015, 1038，说明加密操作可能分布在较宽的区域。让我选择1038（byte 3，高置信度）作为对齐参考点，因为：
1. 它在方差峰值区域附近
2. 它是高置信度字节
3. gap_pct=19%较高



**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "start": 1038,
  "length": 120,
  "max_shift": 400,
  "threshold": 85,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_060103_340817.npy", "plot_path": "align_overlay_20260424_060103_340817.png", "ref_trace_used": 125, "accepted": 250, "discarded": 0, "total": 250, "out_plaintext_npy": "plaintext_aligned_20260424_060103_340817.npy", "plaintext_traces": 250, "out_ciphertext_npy": "ciphertext_aligned_20260424_060103_340817.npy", "ciphertext_traces": 250, "alignment_avg_correlation": 0.9822, "alignment_min_correlation": 0.8776, "acceptance_rate": 1.0}`


![align_overlay_20260424_060103_340817.png](./align_overlay_20260424_060103_340817.png)


---

### Round 10 | tokens: 27,849→184

**🤖 LLM:** 

对齐效果很好：
- 接受率100%（250/250）
- 平均对齐相关系数0.9822

现在使用对齐后的波形重新进行CPA攻击：



**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_060103_340817.npy",
  "wave_npy": "aligned_20260424_060103_340817.npy",
  "leakage_model": "HW",
  "target": "S-box_out",
  "candidates": 20
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2050 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.4383, "cpa_min_correlation": 0.3613, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_060115_213102.png", "detail_file": "cpa_detail_20260424_060115_213102.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.5281, "time_index": 1094, "gap_pct": 46.4}, {"byte": 1, "key": "0x22", "correlation": 0.38, "time_index": 632, "gap_pct": 25.0}, {"byte": 2, "key": "0x33", "correlation": 0.3661, "time_index": 924, "gap_pct": 25.4}, {"byte": 3, "key": "0x44", "correlation": 0.429, "time_index": 1041, "gap_pct": 37.7}, {"byte": 4, "key": "0x55", "correlation": 0.3914, "time_index": 592, "gap_pct": 23.4}, {"byte": 5, "key": "0x66", "correlation": 0.4373, "time_index": 1103, "gap_pct": 36.9}, {"byte": 6, "key": "0x77", "correlation": 0.5083, "time_index": 929, "gap_pct": 44.4}, {"byte": 7, "key": "0x88", "correlation": 0.3963, "time_index": 958, "gap_pct": 24.6}, {"byte": 8, "key": "0x99", "correlation": 0.4295, "time_index": 604, "gap_pct": 39.1}, {"byte": 9, "key": "0xAA", "correlation": 0.4202, "time_index": 828, "gap_pct": 29.7}, {"byte": 10, "key": "0xBB", "correlation": 0.4357, "time_index": 906, "gap_pct": 27.5}, {"byte": 11, "key": "0xCC", "correlation": 0.4762, "time_index": 994, "gap_pct": 36.1}, {"byte": 12, "key": "0xDD", "correlation": 0.3613, "time_index": 614, "gap_pct": 25.3}, {"byte": 13, "key": "0xEE", "correlation": 0.4451, "time_index": 668, "gap_pct": 36.0}
...(truncated)
```
</details>


![cpa_result_20260424_060115_213102.png](./cpa_result_20260424_060115_213102.png)


---

### Round 11 | tokens: 29,017→302

**🤖 LLM:** 

Excellent! 对齐后的CPA结果非常完美：
- 恢复密钥：`112233445566778899AABBCCDDEEFF00`
- 高置信度字节：16/16（全部高置信度！）
- 平均相关系数：0.4383（显著提升）
- 所有字节的gap_pct都在23%-47%之间，远高于15%阈值

现在需要验证这个密钥是否正确。使用encrypt_decrypt_verify进行验证：



**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_060103_340817.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_060103_340817.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "17EAF0DCB9E3BC6F7A83D9F769BFC973", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 17EAF0DCB9E3BC6F7A83D9F769BFC973...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 12 | tokens: 29,479→866

<details><summary><b>🤖 LLM Reasoning</b> (1243 chars)</summary>



🎉 **CPA攻击成功！**

## 实验结果总结

### 攻击流程
1. **直接CPA探测**：初始CPA获得6/16高置信度字节，时间索引分散（91-1038），表明存在对齐问题
2. **静态对齐**：以sample 1038（高置信度字节3的时间点）为参考点进行静态对齐
   - 对齐参数：start=1038, length=120, max_shift=400, threshold=85
   - 对齐效果：100%接受率，平均对齐相关系数0.9822
3. **对齐后CPA**：获得16/16高置信度字节，平均相关系数从0.3177提升至0.4383
4. **密钥验证**：✅ MATCH - 密钥验证通过

### 恢复的密钥
```
112233445566778899AABBCCDDEEFF00
```

### 关键发现
- **对齐是关键**：初始CPA时间索引分散表明波形存在偏移，静态对齐后所有字节都达到高置信度
- **方差峰值定位**：方差分析显示峰值在sample 1075附近，选择1038作为对齐参考点是成功的
- **软件MCU不需要垂直对齐**：基线标准差约11属于正常噪声，符合知识图谱建议

### 各字节详细结果
| Byte | Key | Correlation | Time Index | Gap% |
|------|-----|-------------|------------|------|
| 0 | 0x11 | 0.5281 | 1094 | 46.4% |
| 1 | 0x22 | 0.3800 | 632 | 25.0% |
| 2 | 0x33 | 0.3661 | 924 | 25.4% |
| 3 | 0x44 | 0.4290 | 1041 | 37.7% |
| 4 | 0x55 | 0.3914 | 592 | 23.4% |
| 5 | 0x66 | 0.4373 | 1103 | 36.9% |
| 6 | 0x77 | 0.5083 | 929 | 44.4% |
| 7 | 0x88 | 0.3963 | 958 | 24.6% |
| 8 | 0x99 | 0.4295 | 604 | 39.1% |
| 9 | 0xAA | 0.4202 | 828 | 29.7% |
| 10 | 0xBB | 0.4357 | 906 | 27.5% |
| 11 | 0xCC | 0.4762 | 994 | 36.1% |
| 12 | 0xDD | 0.3613 | 614 | 25.3% |
| 13 | 0xEE | 0.4451 | 668 | 36.0% |
| 14 | 0xFF | 0.4985 | 884 | 43.5% |
| 15 | 0x00 | 0.5103 | 1002 | 46.6% |

所有16个字节均成功恢复并验证通过！

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 17,086 | 1,101 | 18,187 |
| 2 | 18,282 | 476 | 18,758 |
| 3 | 20,117 | 881 | 20,998 |
| 4 | 21,467 | 137 | 21,604 |
| 5 | 21,774 | 933 | 22,707 |
| 6 | 23,194 | 116 | 23,310 |
| 7 | 24,197 | 946 | 25,143 |
| 8 | 26,001 | 839 | 26,840 |
| 9 | 27,058 | 546 | 27,604 |
| 10 | 27,849 | 184 | 28,033 |
| 11 | 29,017 | 302 | 29,319 |
| 12 | 29,479 | 866 | 30,345 |
| **Total** | **285,521** | **7,327** | **292,848** |

## 8. Final Output



🎉 **CPA攻击成功！**

## 实验结果总结

### 攻击流程
1. **直接CPA探测**：初始CPA获得6/16高置信度字节，时间索引分散（91-1038），表明存在对齐问题
2. **静态对齐**：以sample 1038（高置信度字节3的时间点）为参考点进行静态对齐
   - 对齐参数：start=1038, length=120, max_shift=400, threshold=85
   - 对齐效果：100%接受率，平均对齐相关系数0.9822
3. **对齐后CPA**：获得16/16高置信度字节，平均相关系数从0.3177提升至0.4383
4. **密钥验证**：✅ MATCH - 密钥验证通过

### 恢复的密钥
```
112233445566778899AABBCCDDEEFF00
```

### 关键发现
- **对齐是关键**：初始CPA时间索引分散表明波形存在偏移，静态对齐后所有字节都达到高置信度
- **方差峰值定位**：方差分析显示峰值在sample 1075附近，选择1038作为对齐参考点是成功的
- **软件MCU不需要垂直对齐**：基线标准差约11属于正常噪声，符合知识图谱建议

### 各字节详细结果
| Byte | Key | Correlation | Time Index | Gap% |
|------|-----|-------------|------------|------|
| 0 | 0x11 | 0.5281 | 1094 | 46.4% |
| 1 | 0x22 | 0.3800 | 632 | 25.0% |
| 2 | 0x33 | 0.3661 | 924 | 25.4% |
| 3 | 0x44 | 0.4290 | 1041 | 37.7% |
| 4 | 0x55 | 0.3914 | 592 | 23.4% |
| 5 | 0x66 | 0.4373 | 1103 | 36.9% |
| 6 | 0x77 | 0.5083 | 929 | 44.4% |
| 7 | 0x88 | 0.3963 | 958 | 24.6% |
| 8 | 0x99 | 0.4295 | 604 | 39.1% |
| 9 | 0xAA | 0.4202 | 828 | 29.7% |
| 10 | 0xBB | 0.4357 | 906 | 27.5% |
| 11 | 0xCC | 0.4762 | 994 | 36.1% |
| 12 | 0xDD | 0.3613 | 614 | 25.3% |
| 13 | 0xEE | 0.4451 | 668 | 36.0% |
| 14 | 0xFF | 0.4985 | 884 | 43.5% |
| 15 | 0x00 | 0.5103 | 1002 | 46.6% |

所有16个字节均成功恢复并验证通过！
