# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Qwen/Qwen3.5-397B-A17B` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_044902_597 |
| Duration | 188.9s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_Qwen3.5-397B\AES-STM32F103_Qwen3.5-397B-A17B_DKG_20260424_044902_597` |
| Total LLM Calls | 12 |
| First Round | prompt: 17,086, completion: 1,052 |
| Last Round | prompt: 29,648, completion: 418 |
| Total Tokens | 291,817 (prompt: 285,704, completion: 6,113) |

## 3. User Query

```
帮我对一个STM32F103 MCU软件实现的AES密码算法波形进行CPA恢复密钥，明文文件为'data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy'，密文文件为'data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy',原始波形文件为'data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个STM32F103 MCU软件实现的AES密码算法波形进行CPA恢复密钥，明文文件为'data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy'，密文文件为'data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy',原始波形文件为'data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy'"

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
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

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
- `AttackPoint:S-box Output` —[strategy_applies_to [source=expert_experience, condition=Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear, applicability=specific]]→ `Strategy:Do NOT switch leakage target family as first response to low correlation on software implementations`
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
All files for this session are stored in: ..\logs\exp3_Qwen3.5-397B\AES-STM32F103_Qwen3.5-397B-A17B_DKG_20260424_044902_597
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_Qwen3.5-397B\AES-STM32F103_Qwen3.5-397B-A17B_DKG_20260424_044902_597/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 17,086→1,052

**🤖 LLM:** 

我将对STM32F103 MCU软件实现的AES进行CPA攻击。根据专家经验，对于软件MCU实现，我应该：
1. 首先进行直接CPA探测（不带对齐）
2. 使用S-box_out + HW模型（软件实现的标准配置）
3. 根据结果判断是否需要静态对齐

让我先检查波形特征，然后进行第一次CPA探测。



**🔧 → `python_jupyter`**

<details><summary>Code (1856 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# Load the data
wave = np.load('data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')
plain = np.load('data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy')
cipher = np.load('data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy')

print(f"Wave shape: {wave.shape}")
print(f"Plaintext shape: {plain.shape}")
print(f"Ciphertext shape: {cipher.shape}")
print(f"Wave dtype: {wave.dtype}")
print(f"Wave min: {wave.min()}, max: {wave.max()}, mean: {wave.mean()}")

# Plot average trace to see encryption region
avg_trace = np.mean(wave, axis=0)
std_trace = np.std(wave, axis=0)

plt.figure(figsize=(15, 5))
plt.subplot(2, 1, 1)
plt.plot(avg_trace)
plt.title('Average Trace (250 traces)')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(std_trace)
plt.title('Standard Deviation Trace')
plt.xlabel('Sample Point')
plt.ylabel('Std Dev')
plt.grid(True)

plt.tight_layout()
plt.savefig('wave_overview.png')
plt.show()

# Check variance to locate encryption region
variance = np.var(wave, axis=0)
plt.figure(figsize=(12, 4))
plt.plot(variance)
plt.title('Variance Across Traces - Look for High Variance Regions (Encryption)')
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.grid(True)
plt.savefig('variance_trace.png')
plt.show()

# Find high variance regions
high_var_indices = np.where(variance > np.percentile(variance, 90))[0]
print(f"High variance regions (90th percentile): {high_var_indices[:50]}...")
if len(high_var_indices) > 0:
    print(f"First high variance region: {high_var_indices[0]} to {high_var_indices[-1]}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (782 chars)</summary>

```
Wave shape: (250, 1500)
Plaintext shape: (250, 16)
Ciphertext shape: (250, 16)
Wave dtype: float32
Wave min: -342.51971435546875, max: 90.55120086669922, mean: -131.32882690429688
High variance regions (90th percentile): [ 95  96 104 105 106 109 110 111 112 113 114 115 116 117 118 119 120 121
 122 123 124 125 397 398 399 400 401 402 403 404 405 406 407 408 409 410
 411 412 413 414 544 545 546 547 548 549 550 551 552 553]...
First high variance region: 95 to 1228
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\2934981454.py:36: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\2934981454.py:47: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 18,336→391

**🤖 LLM:** 

波形分析显示有250条迹线，1500个采样点。方差分析显示多个高方差区域，表明加密操作分布在不同时间段。

现在进行第一次直接CPA探测（不带对齐），使用软件MCU的标准配置：S-box_out + HW模型。



**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "wave_npy": "data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "leakage_model": "HW",
  "target": "S-box_out",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2994 chars)</summary>

```
{"recovered_key": "11ECD6443566920D5339BBCC4EEEFF00", "cpa_avg_correlation": 0.3177, "cpa_min_correlation": 0.2679, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_045112_527525.png", "detail_file": "cpa_detail_20260424_045112_527525.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.3251, "time_index": 586, "gap_pct": 14.4}, {"byte": 1, "key": "0xEC", "correlation": 0.2679, "time_index": 823, "gap_pct": 1.3}, {"byte": 2, "key": "0xD6", "correlation": 0.3516, "time_index": 492, "gap_pct": 21.1}, {"byte": 3, "key": "0x44", "correlation": 0.3574, "time_index": 1038, "gap_pct": 19.1}, {"byte": 4, "key": "0x35", "correlation": 0.2881, "time_index": 168, "gap_pct": 4.2}, {"byte": 5, "key": "0x66", "correlation": 0.3694, "time_index": 823, "gap_pct": 23.8}, {"byte": 6, "key": "0x92", "correlation": 0.3066, "time_index": 91, "gap_pct": 3.9}, {"byte": 7, "key": "0x0D", "correlation": 0.2767, "time_index": 446, "gap_pct": 3.9}, {"byte": 8, "key": "0x53", "correlation": 0.2897, "time_index": 1012, "gap_pct": 0.7}, {"byte": 9, "key": "0x39", "correlation": 0.2711, "time_index": 240, "gap_pct": 2.2}, {"byte": 10, "key": "0xBB", "correlation": 0.3862, "time_index": 913, "gap_pct": 30.6}, {"byte": 11, "key": "0xCC", "correlation": 0.3413, "time_index": 1021, "gap_pct": 11.6}, {"byte": 12, "key": "0x4E", "correlation": 0.27, "time_index": 338, "gap_pct": 1.1}, {"byte": 13, "key": "0xEE", "correlation": 0.333, "time_index": 862, "gap_pct": 21.0}, {"byte
...(truncated)
```
</details>


![cpa_result_20260424_045112_527525.png](./cpa_result_20260424_045112_527525.png)


---

### Round 3 | tokens: 20,140→634

**🤖 LLM:** 

第一次CPA结果显示：
- 恢复密钥：`11ECD6443566920D5339BBCC4EEEFF00`
- 高置信度字节数：6/16（红色区域，<10/16）
- 平均相关系数：0.3177

根据专家经验，6/16的高置信度字节数处于红色区域，需要重新定位泄漏区域或进行静态对齐。让我先查看CPA详情文件，了解哪些字节置信度低，然后进行静态对齐。

首先，让我检查CPA结果中各个字节的时间索引分布，看看是否需要对齐：



**🔧 → `python_jupyter`**

<details><summary>Code (1307 chars)</summary>

```python
import json
import numpy as np

# Load CPA detail
with open('cpa_detail_20260424_045112_527525.json', 'r') as f:
    cpa_detail = json.load(f)

# Extract time indices and correlations
time_indices = [b['time_index'] for b in cpa_detail['per_byte']]
correlations = [b['correlation'] for b in cpa_detail['per_byte']]
gap_pcts = [b['gap_pct'] for b in cpa_detail['per_byte']]
keys = [b['key'] for b in cpa_detail['per_byte']]

print("Byte analysis:")
print(f"{'Byte':<5} {'Key':<6} {'Corr':<8} {'Gap%':<8} {'TimeIdx':<10} {'Confidence'}")
print("-" * 60)
for i in range(16):
    conf = "HIGH" if gap_pcts[i] > 0.15 else "LOW"
    print(f"{i:<5} {keys[i]:<6} {correlations[i]:<8.4f} {gap_pcts[i]:<8.4f} {time_indices[i]:<10} {conf}")

print(f"\nTime index range: {min(time_indices)} to {max(time_indices)}")
print(f"Time index spread: {max(time_indices) - min(time_indices)}")

# Check if time indices are clustered
time_indices_arr = np.array(time_indices)
print(f"\nTime indices sorted: {np.sort(time_indices_arr)}")

# Identify high confidence bytes
high_conf_bytes = [i for i, g in enumerate(gap_pcts) if g > 0.15]
low_conf_bytes = [i for i, g in enumerate(gap_pcts) if g <= 0.15]
print(f"\nHigh confidence bytes (gap > 15%): {high_conf_bytes}")
print(f"Low confidence bytes (gap <= 15%): {low_conf_bytes}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
---ERROR---
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
Cell In[179], line 9
      6     cpa_detail = json.load(f)
      8 # Extract time indices and correlations
----> 9 time_indices = [b['time_index'] for b in cpa_detail['per_byte']]
     10 correlations = [b['correlation'] for b in cpa_detail['per_byte']]
     11 gap_pcts = [b['gap_pct'] for b in cpa_detail['per_byte']]

KeyError: 'per_byte'
```


---

### Round 4 | tokens: 21,368→136

**🤖 LLM:** 

让我检查CPA详情文件的结构：



**🔧 → `python_jupyter`**

<details><summary>Code (278 chars)</summary>

```python
import json

# Load CPA detail
with open('cpa_detail_20260424_045112_527525.json', 'r') as f:
    cpa_detail = json.load(f)

# Print keys to understand structure
print("CPA detail keys:", cpa_detail.keys())
print("\nFull content:")
print(json.dumps(cpa_detail, indent=2)[:2000])
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (2119 chars)</summary>

```
CPA detail keys: dict_keys(['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results'])

Full content:
{
  "n_traces": 250,
  "n_points": 1500,
  "leakage_model": "HW",
  "target": "S-box_out",
  "corr_mode": "abs",
  "results": [
    {
      "byte": 0,
      "topK": [
        {
          "key": 17,
          "score": 0.3250724366280273,
          "time_index": 586
        },
        {
          "key": 198,
          "score": 0.27818509875717523,
          "time_index": 686
        },
        {
          "key": 58,
          "score": 0.26933490809232236,
          "time_index": 70
        },
        {
          "key": 147,
          "score": 0.2683197316967659,
          "time_index": 1126
        },
        {
          "key": 21,
          "score": 0.26772015112301584,
          "time_index": 473
        },
        {
          "key": 232,
          "score": 0.2633013693864752,
          "time_index": 709
        },
        {
          "key": 109,
          "score": 0.25262450607327475,
          "time_index": 1311
        },
        {
          "key": 175,
          "score": 0.2510898053513292,
          "time_index": 1294
        },
        {
          "key": 229,
          "score": 0.24836878174680724,
          "time_index": 856
        },
        {
          "key": 47,
          "score": 0.24413088316825435,
          "time_index": 516
        },
        {
          "key": 219,
          "score": 0.24410301905807874,
          "time_index": 609
        },
...(truncated)
```
</details>


---

### Round 5 | tokens: 22,493→635

**🤖 LLM:** 

现在我了解了结构。让我分析时间索引分布：



**🔧 → `python_jupyter`**

<details><summary>Code (1703 chars)</summary>

```python
import json
import numpy as np

# Load CPA detail
with open('cpa_detail_20260424_045112_527525.json', 'r') as f:
    cpa_detail = json.load(f)

results = cpa_detail['results']

# Extract best key info for each byte
time_indices = []
correlations = []
gap_pcts = []
keys = []

for r in results:
    byte_idx = r['byte']
    top1 = r['topK'][0]
    top2 = r['topK'][1]
    
    time_indices.append(top1['time_index'])
    correlations.append(top1['score'])
    keys.append(top1['key'])
    
    # Calculate gap
    gap = top1['score'] - top2['score']
    gap_pct = gap / top1['score'] if top1['score'] > 0 else 0
    gap_pcts.append(gap_pct)

print("Byte analysis:")
print(f"{'Byte':<5} {'Key':<6} {'Corr':<8} {'Gap%':<8} {'TimeIdx':<10} {'Confidence'}")
print("-" * 60)
for i in range(16):
    conf = "HIGH" if gap_pcts[i] > 0.15 else "LOW"
    print(f"{i:<5} 0x{keys[i]:02X}   {correlations[i]:<8.4f} {gap_pcts[i]*100:<8.2f} {time_indices[i]:<10} {conf}")

print(f"\nTime index range: {min(time_indices)} to {max(time_indices)}")
print(f"Time index spread: {max(time_indices) - min(time_indices)}")

# Identify high confidence bytes
high_conf_bytes = [i for i, g in enumerate(gap_pcts) if g > 0.15]
low_conf_bytes = [i for i, g in enumerate(gap_pcts) if g <= 0.15]
print(f"\nHigh confidence bytes (gap > 15%): {high_conf_bytes} (count: {len(high_conf_bytes)})")
print(f"Low confidence bytes (gap <= 15%): {low_conf_bytes} (count: {len(low_conf_bytes)})")

# Check time indices of high confidence bytes
high_conf_times = [time_indices[i] for i in high_conf_bytes]
print(f"\nHigh confidence time indices: {high_conf_times}")
print(f"High conf time range: {min(high_conf_times)} to {max(high_conf_times)}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1171 chars)</summary>

```
Byte analysis:
Byte  Key    Corr     Gap%     TimeIdx    Confidence
------------------------------------------------------------
0     0x11   0.3251   14.42    586        LOW
1     0xEC   0.2679   1.32     823        LOW
2     0xD6   0.3516   21.06    492        HIGH
3     0x44   0.3574   19.06    1038       HIGH
4     0x35   0.2881   4.24     168        LOW
5     0x66   0.3694   23.82    823        HIGH
6     0x92   0.3066   3.94     91         LOW
7     0x0D   0.2767   3.93     446        LOW
8     0x53   0.2897   0.65     1012       LOW
9     0x39   0.2711   2.19     240        LOW
10    0xBB   0.3862   30.59    913        HIGH
11    0xCC   0.3413   11.59    1021       LOW
12    0x4E   0.2700   1.12     338        LOW
13    0xEE   0.3330   20.97    862        HIGH
14    0xFF   0.3131   13.20    895        LOW
15    0x00   0.3369   17.41    1015       HIGH

Time index range: 91 to 1038
Time index spread: 947

High confidence bytes (gap > 15%): [2, 3, 5, 10, 13, 15] (count: 6)
Low confidence bytes (gap <= 15%): [0, 1, 4, 6, 7, 8, 9, 11, 12, 14] (count: 10)

High confidence time indices: [492, 1038, 823, 913, 862, 1015]
High conf time range: 492 to 1038
```
</details>


---

### Round 6 | tokens: 23,803→530

**🤖 LLM:** 

分析显示时间索引分散在91到1038之间，跨度947个采样点。高置信度字节的时间索引集中在492-1038范围内。这表明迹线可能存在对齐问题。

根据专家经验，对于软件MCU实现，我应该：
1. 首先使用方差分析定位加密区域
2. 然后进行静态对齐

让我先查看波形的方差分布，找到合适的对齐参考点：



**🔧 → `python_jupyter`**

<details><summary>Code (1209 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# Load wave
wave = np.load('data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')

# Calculate variance
variance = np.var(wave, axis=0)

# Find peaks in variance
from scipy.signal import find_peaks

# Find peaks
peaks, properties = find_peaks(variance, height=np.percentile(variance, 75), distance=50)

plt.figure(figsize=(15, 6))
plt.plot(variance, label='Variance')
plt.plot(peaks, variance[peaks], 'rx', label='Peaks', markersize=10)
plt.title('Variance Analysis - Looking for Encryption Regions')
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.legend()
plt.grid(True)
plt.savefig('variance_peaks.png')

# Print top peaks
top_peak_indices = np.argsort(variance)[-20:][::-1]
print("Top 20 variance peaks:")
for idx in top_peak_indices:
    print(f"  Sample {idx}: variance = {variance[idx]:.4f}")

# Check the region around high-confidence time indices
high_conf_times = [492, 1038, 823, 913, 862, 1015]
print(f"\nVariance at high-confidence time indices:")
for t in high_conf_times:
    print(f"  Sample {t}: variance = {variance[t]:.4f}")

plt.tight_layout()
plt.show()
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1149 chars)</summary>

```
Top 20 variance peaks:
  Sample 1102: variance = 3632.2959
  Sample 1104: variance = 3597.3411
  Sample 1103: variance = 3597.3022
  Sample 1101: variance = 3565.4551
  Sample 1100: variance = 3526.7256
  Sample 1105: variance = 3517.9214
  Sample 1099: variance = 3429.9905
  Sample 1106: variance = 3427.4363
  Sample 1107: variance = 3325.5828
  Sample 1098: variance = 3319.7595
  Sample 1097: variance = 3223.6514
  Sample 1108: variance = 3213.0256
  Sample 1096: variance = 3114.9207
  Sample 1109: variance = 3075.2351
  Sample 1095: variance = 3027.7334
  Sample 1110: variance = 2948.0176
  Sample 1094: variance = 2873.9551
  Sample 1064: variance = 2857.4351
  Sample 1065: variance = 2841.3477
  Sample 1063: variance = 2840.4050

Variance at high-confidence time indices:
  Sample 492: variance = 597.4330
  Sample 1038: variance = 434.4194
  Sample 823: variance = 307.3928
  Sample 913: variance = 358.2586
  Sample 862: variance = 242.5185
  Sample 1015: variance = 527.3967
C:\Users\Andersen\AppData\Local\Temp\ipykernel_24372\2873556145.py:39: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 7 | tokens: 24,960→624

**🤖 LLM:** 

方差分析显示最高方差区域在1095-1110附近，这应该是主要的加密泄漏区域。高置信度字节的时间索引（492-1038）并不在最高方差区域，说明可能需要重新定位对齐参考点。

根据专家经验，我应该：
1. 选择方差峰值区域作为对齐参考
2. 使用较大的max_shift（300+）进行静态对齐

让我选择一个合适的参考点进行静态对齐。最高方差在1102附近，我可以选择这个区域作为对齐参考。首先，让我查看这个区域的波形特征：



**🔧 → `python_jupyter`**

<details><summary>Code (1287 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# Load wave
wave = np.load('data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy')

# Plot a few traces around the high variance region (1090-1120)
plt.figure(figsize=(15, 6))
for i in range(5):  # Plot first 5 traces
    plt.plot(wave[i, 1050:1150], label=f'Trace {i}', alpha=0.7)

plt.title('Traces around high variance region (1050-1150)')
plt.xlabel('Sample Point')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.savefig('traces_1050_1150.png')

# Also check the region around sample 1100 for alignment reference
# Let's see the average trace to identify a good reference point
avg_trace = np.mean(wave, axis=0)
plt.figure(figsize=(15, 4))
plt.plot(avg_trace[1050:1150])
plt.title('Average Trace (1050-1150) - Look for a clear peak for alignment reference')
plt.xlabel('Sample Point (relative to 1050)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.savefig('avg_1050_1150.png')

# Check trace alignment by looking at a few traces
print("Checking trace alignment around sample 1100:")
for i in range(5):
    peak_idx = 1050 + np.argmax(np.abs(wave[i, 1050:1150]))
    print(f"  Trace {i}: peak at sample {peak_idx}, value = {wave[i, peak_idx]:.2f}")
```
</details>

**📋 ← `python_jupyter`:** `Checking trace alignment around sample 1100:
  Trace 0: peak at sample 1121, value = -248.03
  Trace 1: peak at sample 1113, value = -267.72
  Trace 2: peak at sample 1111, value = -255.91
  Trace 3: peak at sample 1116, value = -251.97
  Trace 4: peak at sample 1098, value = -212.60`


---

### Round 8 | tokens: 25,731→460

**🤖 LLM:** 

迹线在1100附近确实存在对齐问题，峰值位置从1098到1121不等，跨度约23个采样点。这表明需要静态对齐。

根据专家经验，对于接触式智能卡/MCU，我应该：
- 选择方差峰值区域内的一个清晰特征点作为对齐参考
- 使用较大的max_shift（至少300）
- 参考点应该在加密区间内

最高方差在1102，我选择1100作为对齐参考起点，长度120覆盖一个完整的S-box操作峰值。



**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy",
  "plaintext_npy": "data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy",
  "ciphertext_npy": "data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy",
  "start": 1100,
  "length": 120,
  "max_shift": 400,
  "threshold": 85,
  "ref_trace": null
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_045245_289798.npy", "plot_path": "align_overlay_20260424_045245_289798.png", "ref_trace_used": 125, "accepted": 250, "discarded": 0, "total": 250, "out_plaintext_npy": "plaintext_aligned_20260424_045245_289798.npy", "plaintext_traces": 250, "out_ciphertext_npy": "ciphertext_aligned_20260424_045245_289798.npy", "ciphertext_traces": 250, "alignment_avg_correlation": 0.9904, "alignment_min_correlation": 0.8908, "acceptance_rate": 1.0}`


![align_overlay_20260424_045245_289798.png](./align_overlay_20260424_045245_289798.png)


---

### Round 9 | tokens: 26,436→204

**🤖 LLM:** 

静态对齐成功：
- 接受率：100%（250/250条迹线）
- 平均对齐相关系数：0.9904
- 参考迹线：125（中间迹线）

现在使用对齐后的迹线进行CPA攻击：



**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_045245_289798.npy",
  "wave_npy": "aligned_20260424_045245_289798.npy",
  "leakage_model": "HW",
  "target": "S-box_out",
  "candidates": 20
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2048 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.4425, "cpa_min_correlation": 0.3591, "n_traces": 250, "target": "S-box_out", "plot_path": "cpa_result_20260424_045257_925840.png", "detail_file": "cpa_detail_20260424_045257_925840.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.4635, "time_index": 582, "gap_pct": 36.5}, {"byte": 1, "key": "0x22", "correlation": 0.3858, "time_index": 633, "gap_pct": 26.6}, {"byte": 2, "key": "0x33", "correlation": 0.3591, "time_index": 924, "gap_pct": 17.9}, {"byte": 3, "key": "0x44", "correlation": 0.4889, "time_index": 1041, "gap_pct": 46.4}, {"byte": 4, "key": "0x55", "correlation": 0.4226, "time_index": 592, "gap_pct": 24.7}, {"byte": 5, "key": "0x66", "correlation": 0.4307, "time_index": 820, "gap_pct": 35.8}, {"byte": 6, "key": "0x77", "correlation": 0.4723, "time_index": 929, "gap_pct": 41.5}, {"byte": 7, "key": "0x88", "correlation": 0.4278, "time_index": 958, "gap_pct": 26.4}, {"byte": 8, "key": "0x99", "correlation": 0.398, "time_index": 602, "gap_pct": 32.0}, {"byte": 9, "key": "0xAA", "correlation": 0.463, "time_index": 828, "gap_pct": 37.4}, {"byte": 10, "key": "0xBB", "correlation": 0.434, "time_index": 1111, "gap_pct": 25.7}, {"byte": 11, "key": "0xCC", "correlation": 0.5011, "time_index": 995, "gap_pct": 39.8}, {"byte": 12, "key": "0xDD", "correlation": 0.3967, "time_index": 613, "gap_pct": 29.7}, {"byte": 13, "key": "0xEE", "correlation": 0.4561, "time_index": 848, "gap_pct": 36.4},
...(truncated)
```
</details>


![cpa_result_20260424_045257_925840.png](./cpa_result_20260424_045257_925840.png)


---

### Round 10 | tokens: 27,622→299

**🤖 LLM:** 

优秀的结果！对齐后的CPA攻击成功恢复了所有16个字节：

- 恢复密钥：`112233445566778899AABBCCDDEEFF00`
- 高置信度字节数：16/16（全部高置信度）
- 平均相关系数：0.4425（显著提升）
- 所有字节的gap_pct都大于15%

现在需要验证这个密钥是否正确。让我使用encrypt_decrypt_verify进行验证：



**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_045245_289798.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_045245_289798.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "17EAF0DCB9E3BC6F7A83D9F769BFC973", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 33f25e5f412260df3ad3d47477f4ce89... → 17EAF0DCB9E3BC6F7A83D9F769BFC973...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 11 | tokens: 28,081→730

**🤖 LLM:** 

密钥验证成功！CPA攻击完全成功。

让我总结一下整个攻击过程：



**🔧 → `python_jupyter`**

<details><summary>Code (1729 chars)</summary>

```python
import json

# Load the final CPA detail for summary
with open('cpa_detail_20260424_045257_925840.json', 'r') as f:
    cpa_detail = json.load(f)

print("=" * 70)
print("CPA Attack Summary - AES-128 on STM32F103 MCU")
print("=" * 70)

print("\n📊 Attack Configuration:")
print(f"  - Algorithm: AES-128")
print(f"  - Device: STM32F103 MCU (Software Implementation)")
print(f"  - Leakage Model: Hamming Weight (HW)")
print(f"  - Target: S-box_out")
print(f"  - Number of traces: {cpa_detail['n_traces']}")
print(f"  - Number of points: {cpa_detail['n_points']}")

print("\n🔑 Recovered Key: 112233445566778899AABBCCDDEEFF00")

print("\n✅ Verification: MATCH - All 16 bytes correct!")

print("\n📈 Per-byte Results:")
print(f"{'Byte':<6} {'Key':<8} {'Correlation':<12} {'Gap%':<10} {'TimeIdx':<10} {'Status'}")
print("-" * 70)

results = cpa_detail['results']
for r in results:
    byte_idx = r['byte']
    top1 = r['topK'][0]
    top2 = r['topK'][1]
    gap_pct = (top1['score'] - top2['score']) / top1['score'] * 100 if top1['score'] > 0 else 0
    status = "✓ HIGH" if gap_pct > 15 else "✗ LOW"
    print(f"{byte_idx:<6} 0x{top1['key']:02X}    {top1['score']:<12.4f} {gap_pct:<10.2f} {top1['time_index']:<10} {status}")

print("\n" + "=" * 70)
print("Attack Pipeline:")
print("  1. Direct CPA (no alignment) → 6/16 high-confidence bytes (RED band)")
print("  2. Variance analysis → Found high variance region at samples 1095-1110")
print("  3. Static alignment @ sample 1100, max_shift=400, length=120")
print("     - Acceptance rate: 100% (250/250)")
print("     - Alignment correlation: 0.9904")
print("  4. CPA on aligned traces → 16/16 high-confidence bytes (GREEN band)")
print("  5. Key verification: MATCH ✓")
print("=" * 70)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (2105 chars)</summary>

```
======================================================================
CPA Attack Summary - AES-128 on STM32F103 MCU
======================================================================

📊 Attack Configuration:
  - Algorithm: AES-128
  - Device: STM32F103 MCU (Software Implementation)
  - Leakage Model: Hamming Weight (HW)
  - Target: S-box_out
  - Number of traces: 250
  - Number of points: 1500

🔑 Recovered Key: 112233445566778899AABBCCDDEEFF00

✅ Verification: MATCH - All 16 bytes correct!

📈 Per-byte Results:
Byte   Key      Correlation  Gap%       TimeIdx    Status
----------------------------------------------------------------------
0      0x11    0.4635       36.47      582        ✓ HIGH
1      0x22    0.3858       26.64      633        ✓ HIGH
2      0x33    0.3591       17.90      924        ✓ HIGH
3      0x44    0.4889       46.39      1041       ✓ HIGH
4      0x55    0.4226       24.72      592        ✓ HIGH
5      0x66    0.4307       35.83      820        ✓ HIGH
6      0x77    0.4723       41.46      929        ✓ HIGH
7      0x88    0.4278       26.38      958        ✓ HIGH
8      0x99    0.3980       32.00      602        ✓ HIGH
9      0xAA    0.4630       37.43      828        ✓ HIGH
10     0xBB    0.4340       25.71      1111       ✓ HIGH
11     0xCC    0.5011       39.84      995        ✓ HIGH
12     0xDD    0.3967       29.74      613        ✓ HIGH
13     0xEE    0.4561       36.37      848        ✓ HIGH
14     0xFF    0.4886       43.12      885        ✓ 
...(truncated)
```
</details>


---

### Round 12 | tokens: 29,648→418

**🤖 LLM:** 

## CPA攻击成功完成！

### 攻击结果总结

**恢复的AES-128密钥**: `112233445566778899AABBCCDDEEFF00`

**验证结果**: ✅ **MATCH** - 所有16字节完全正确

### 攻击流程

1. **第一次CPA探测（无对齐）**
   - 配置：S-box_out + HW模型（软件MCU标准配置）
   - 结果：6/16高置信度字节（红色区域）
   - 平均相关系数：0.3177

2. **方差分析定位加密区域**
   - 发现最高方差区域在样本1095-1110
   - 确定对齐参考点：样本1100

3. **静态对齐**
   - 参考点：1100，长度：120，最大偏移：400
   - 接受率：100%（250/250条迹线）
   - 对齐相关系数：0.9904

4. **第二次CPA（对齐后）**
   - 结果：16/16高置信度字节（绿色区域）
   - 平均相关系数：0.4425（提升39%）
   - 所有字节gap_pct > 15%

5. **密钥验证**
   - 使用encrypt_decrypt_verify验证
   - 结果：MATCH ✓

### 关键经验

- 对于软件MCU实现，直接CPA可能因迹线未对齐而效果不佳
- 方差分析是定位加密区域的有效方法
- 静态对齐显著提升了CPA效果（从6/16到16/16高置信度字节）
- 使用较大的max_shift（400）确保捕获所有迹线的偏移


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 17,086 | 1,052 | 18,138 |
| 2 | 18,336 | 391 | 18,727 |
| 3 | 20,140 | 634 | 20,774 |
| 4 | 21,368 | 136 | 21,504 |
| 5 | 22,493 | 635 | 23,128 |
| 6 | 23,803 | 530 | 24,333 |
| 7 | 24,960 | 624 | 25,584 |
| 8 | 25,731 | 460 | 26,191 |
| 9 | 26,436 | 204 | 26,640 |
| 10 | 27,622 | 299 | 27,921 |
| 11 | 28,081 | 730 | 28,811 |
| 12 | 29,648 | 418 | 30,066 |
| **Total** | **285,704** | **6,113** | **291,817** |

## 8. Final Output



## CPA攻击成功完成！

### 攻击结果总结

**恢复的AES-128密钥**: `112233445566778899AABBCCDDEEFF00`

**验证结果**: ✅ **MATCH** - 所有16字节完全正确

### 攻击流程

1. **第一次CPA探测（无对齐）**
   - 配置：S-box_out + HW模型（软件MCU标准配置）
   - 结果：6/16高置信度字节（红色区域）
   - 平均相关系数：0.3177

2. **方差分析定位加密区域**
   - 发现最高方差区域在样本1095-1110
   - 确定对齐参考点：样本1100

3. **静态对齐**
   - 参考点：1100，长度：120，最大偏移：400
   - 接受率：100%（250/250条迹线）
   - 对齐相关系数：0.9904

4. **第二次CPA（对齐后）**
   - 结果：16/16高置信度字节（绿色区域）
   - 平均相关系数：0.4425（提升39%）
   - 所有字节gap_pct > 15%

5. **密钥验证**
   - 使用encrypt_decrypt_verify验证
   - 结果：MATCH ✓

### 关键经验

- 对于软件MCU实现，直接CPA可能因迹线未对齐而效果不佳
- 方差分析是定位加密区域的有效方法
- 静态对齐显著提升了CPA效果（从6/16到16/16高置信度字节）
- 使用较大的max_shift（400）确保捕获所有迹线的偏移
