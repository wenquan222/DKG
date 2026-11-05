# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_041901_879 |
| Duration | 265.2s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_DSv3.2\AES-7816_DeepSeek-V3.2_DKG_20260424_041901_879` |
| Total LLM Calls | 11 |
| First Round | prompt: 16,112, completion: 923 |
| Last Round | prompt: 33,826, completion: 429 |
| Total Tokens | 281,048 (prompt: 276,209, completion: 4,839) |

## 3. User Query

```
帮我对一个接触式智能卡实现的AES密码算法波形进行CPA恢复密钥，明文文件为'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy'，密文文件为'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy',原始波形文件为'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个接触式智能卡实现的AES密码算法波形进行CPA恢复密钥，明文文件为'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy'，密文文件为'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy',原始波形文件为'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy'"

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

LLM Response: ["AES", "Contact Smartcard", "CPA", "Power", "S-box Output"]

Parsed Keywords: `["AES", "Contact Smartcard", "CPA", "Power", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 38692 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (40960 chars, click to expand)</summary>

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

**Search keywords** (5): AES, Contact Smartcard, CPA, Power, S-box Output

**Summary**: 26 upper entities, 24 relationships, 16 diagnostic chains, 13 strategies


## 1. Upper Layer Entities (26)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### AttackPoint (6)

- **Inverse S-box Output** — round=13
- **Masked S-box Output**
- **S-box Output** — required_data=ciphertext, round=last
- **S-box Output and Mask** — required_data=plaintext, round=first
- **S-box output** — round=1
- **S-box outputs** — round=first

### DeviceClass (4)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **Contact Smartcard with 16-bit RISC CPU** — category=Smartcard, bus_width=16

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

## 2. Relationships (24)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: XOR operation output, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `AttackPoint:XOR operation output`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
- `DeviceClass:Contact Smartcard with 16-bit RISC CPU` —[works_with [source_text=Attack on the Blinded Lookup Table Implementation, support_count=1, confidence=0.2, source_papers=["PAP-103-2011-CHES-Clavier-Improved-CollisionCorr-Masked-AES"]]]→ `StatMethod:Collision-Correlation Attack`
- `DeviceClass:Contact Smartcard with 16-bit RISC CPU` —[works_with [source_text=Attack on the Blinded Lookup Table Implementation, support_count=1, confidence=0.2, source_papers=["PAP-103-2011-CHES-Clavier-Improved-CollisionCorr-Masked-AES"]]]→ `Algorithm:AES`
- `DeviceClass:Contact Smartcard with 16-bit RISC CPU` —[acquires_via [source_text=proprietary simulation tool, support_count=1, confidence=0.2, source_papers=["PAP-103-2011-CHES-Clavier-Improved-CollisionCorr-Masked-AES"]]]→ `TraceType:Simulated Power`
- `DeviceClass:Contact Smartcard with 16-bit RISC CPU` —[acquires_via [source_text=MicroPross MP100 reader and Lecroy WavePro oscilloscope, support_count=1, confidence=0.2, source_papers=["PAP-103-2011-CHES-Clavier-Improved-CollisionCorr-Masked-AES"]]]→ `TraceType:Power`
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

## 3. Diagnostic Chains (16)


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
All files for this session are stored in: ..\logs\exp3_DSv3.2\AES-7816_DeepSeek-V3.2_DKG_20260424_041901_879
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_DSv3.2\AES-7816_DeepSeek-V3.2_DKG_20260424_041901_879/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 16,112→923

**🤖 LLM:** 我来帮您对接触式智能卡实现的AES密码算法波形进行CPA恢复密钥。首先，让我检查一下数据的基本情况。

**🔧 → `python_jupyter`**

<details><summary>Code (2418 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
plaintext_path = 'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy'
ciphertext_path = 'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy'
wave_path = 'data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy'

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
plt.title('First 3 traces')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('first_traces.png')
plt.show()

# 绘制平均波形
mean_wave = wave.mean(axis=0)
plt.figure(figsize=(12, 4))
plt.plot(mean_wave)
plt.xlabel('Sample index')
plt.ylabel('Amplitude')
plt.title('Average trace')
plt.grid(True, alpha=0.3)
plt.savefig('average_trace.png')
plt.show()

# 计算方差，寻找加密区域
variance = wave.var(axis=0)
plt.figure(figsize=(12, 4))
plt.plot(variance)
plt.xlabel('Sample index')
plt.ylabel('Variance')
plt.title('Variance across traces')
plt.grid(True, alpha=0.3)
plt.savefig('variance.png')
plt.show()

# 找出方差最大的区域
max_var_idx = np.argmax(variance)
print(f"\nMaximum variance at sample index: {max_var_idx}")
print(f"Maximum variance value: {variance[max_var_idx]:.2f}")

# 查看方差最大的区域附近
window = 200
start = max(0, max_var_idx - window)
end = min(len(variance), max_var_idx + window)
print(f"Variance in region [{start}, {end}]:")
print(f"  Max: {variance[start:end].max():.2f}")
print(f"  Mean: {variance[start:end].mean():.2f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (984 chars)</summary>

```
Plaintext shape: (100, 16)
Ciphertext shape: (100, 16)
Wave shape: (100, 7400)
Number of traces: 100
Samples per trace: 7400
Plaintext dtype: uint8
Ciphertext dtype: uint8
Wave dtype: float32

First plaintext (hex): 3871ca2c3c022647f326197e85d4aa71
First ciphertext (hex): 290ad4a41f352b837787d9581dfc4c43

Wave statistics:
  Min: -86.61
  Max: 251.97
  Mean: 8.81
  Std: 36.56

Maximum variance at sample index: 1376
Maximum variance value: 5680.23
Variance in region [1176, 1576]:
  Max: 5680.23
  Mean: 2274.73
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2288249241.py:43: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2288249241.py:54: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\2288249241.py:65: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 17,407→349

**🤖 LLM:** 数据加载成功！我们有100条轨迹，每条7400个采样点。从方差图可以看出，在样本索引1376附近有一个明显的峰值，这很可能是加密操作发生的区域。让我进一步分析这个区域。

根据DKG知识图谱的建议，对于接触式智能卡实现的AES，我应该：
1. 首先尝试直接CPA攻击（不进行对齐）
2. 使用S-box输出作为攻击点，HW作为泄漏模型（这是软件实现的默认配置）
3. 如果直接CPA效果不好，再进行对齐处理

让我先进行直接CPA攻击：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "wave_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy",
  "candidates": 20,
  "leakage_model": "HW",
  "target": "S-box_out"
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (3567 chars)</summary>

```
{"recovered_key": "146F98806836F55937FBCD36B5CF7096", "cpa_avg_correlation": 0.4648, "cpa_min_correlation": 0.4358, "n_traces": 100, "target": "S-box_out", "plot_path": "cpa_result_20260424_042004_515298.png", "detail_file": "cpa_detail_20260424_042004_515298.json", "per_byte": [{"byte": 0, "key": "0x14", "correlation": 0.4497, "time_index": 4625, "gap_pct": 0.5}, {"byte": 1, "key": "0x6F", "correlation": 0.4383, "time_index": 408, "gap_pct": 2.2}, {"byte": 2, "key": "0x98", "correlation": 0.4483, "time_index": 3443, "gap_pct": 2.8}, {"byte": 3, "key": "0x80", "correlation": 0.5045, "time_index": 1938, "gap_pct": 14.4}, {"byte": 4, "key": "0x68", "correlation": 0.4358, "time_index": 714, "gap_pct": 4.5}, {"byte": 5, "key": "0x36", "correlation": 0.4763, "time_index": 6619, "gap_pct": 1.0}, {"byte": 6, "key": "0xF5", "correlation": 0.4802, "time_index": 586, "gap_pct": 5.5}, {"byte": 7, "key": "0x59", "correlation": 0.4638, "time_index": 2732, "gap_pct": 8.4}, {"byte": 8, "key": "0x37", "correlation": 0.4605, "time_index": 4182, "gap_pct": 4.5}, {"byte": 9, "key": "0xFB", "correlation": 0.4505, "time_index": 5658, "gap_pct": 3.1}, {"byte": 10, "key": "0xCD", "correlation": 0.4594, "time_index": 6070, "gap_pct": 8.2}, {"byte": 11, "key": "0x36", "correlation": 0.4719, "time_index": 1381, "gap_pct": 3.6}, {"byte": 12, "key": "0xB5", "correlation": 0.4855, "time_index": 6826, "gap_pct": 3.4}, {"byte": 13, "key": "0xCF", "correlation": 0.4655, "time_index": 1142, "gap_pct": 3.0}, 
...(truncated)
```
</details>


![cpa_result_20260424_042004_515298.png](./cpa_result_20260424_042004_515298.png)


---

### Round 3 | tokens: 19,339→333

**🤖 LLM:** 直接CPA攻击的结果显示：平均相关性为0.4648，但没有一个字节是高置信度的（high_confidence_count=0）。从结果看，每个字节的gap_pct都相对较低（大部分在2-8%之间），这表明攻击点可能没有对齐到正确的泄漏区域。

让我先验证一下恢复的密钥是否正确：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "146F98806836F55937FBCD36B5CF7096",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "ciphertext_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "CCBC091FEBB0601B0FA3261BBF523C5D", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 3871ca2c3c022647f326197e85d4aa71... → CCBC091FEBB0601B0FA3261BBF523C5D...\n❌ Key verification FAILED — 16/16 ciphertext bytes differ\n   Expected:  290AD4A41F352B837787D9581DFC4C43\n   Got:       CCBC091FEBB0601B0FA3261BBF523C5D\n\n   ⚠️ IMPORTANT: '16 ciphertext bytes differ' does NOT mean '16 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 4 | tokens: 20,038→270

**🤖 LLM:** 密钥验证失败，这与CPA结果一致。根据DKG知识图谱的建议，对于软件实现（接触式智能卡），我应该首先尝试对齐处理。让我先进行明文相关性分析，找到泄漏区域：

**🔧 → `plaintext_ciphertext_correlation`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy",
  "data_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "data_type": "plaintext",
  "byte_index": 0,
  "model": "HW"
}
```
</details>

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 1160, "peak_region_end": 1171, "peak_time_index": 1165, "peak_correlation": 0.3503, "suggested_cpa_range": [1110, 1221], "all_byte_peaks": [1165, 952, 1130, 862, 4886, 5424, 125, 6555, 6955, 6467, 2298, 6610, 168, 600, 58, 6330], "byte_peaks_std": 2741.6, "plot_path": "correlation_20260424_042051_754967.png"}`


![correlation_20260424_042051_754967.png](./correlation_20260424_042051_754967.png)


---

### Round 5 | tokens: 20,480→603

**🤖 LLM:** 明文相关性分析显示，字节0的峰值在样本1165附近，相关性为0.3503。建议的CPA范围是[1110, 1221]。让我查看一下这个区域：

**🔧 → `python_jupyter`**

<details><summary>Code (1389 chars)</summary>

```python
# 查看建议的CPA区域
import numpy as np
import matplotlib.pyplot as plt

wave = np.load('data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy')
mean_wave = wave.mean(axis=0)

# 绘制建议区域
start, end = 1110, 1221
plt.figure(figsize=(12, 4))
plt.plot(range(start, end), mean_wave[start:end])
plt.axvline(1165, color='red', linestyle='--', alpha=0.7, label='Peak at 1165')
plt.xlabel('Sample index')
plt.ylabel('Amplitude')
plt.title(f'Mean trace in suggested CPA region [{start}, {end}]')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('suggested_region.png')
plt.show()

# 计算这个区域的方差
variance = wave.var(axis=0)
print(f"Variance in region [{start}, {end}]:")
print(f"  Max: {variance[start:end].max():.2f}")
print(f"  Mean: {variance[start:end].mean():.2f}")
print(f"  At peak (1165): {variance[1165]:.2f}")

# 查看所有字节的峰值位置
all_peaks = [1165, 952, 1130, 862, 4886, 5424, 125, 6555, 6955, 6467, 2298, 6610, 168, 600, 58, 6330]
print(f"\nAll byte peaks: {all_peaks}")
print(f"Peaks std: {np.std(all_peaks):.2f}")

# 检查是否有明显的对齐问题
print(f"\nChecking alignment by looking at first few traces in peak region:")
for i in range(3):
    trace_segment = wave[i, start:end]
    peak_idx_in_segment = np.argmax(np.abs(trace_segment))
    print(f"Trace {i}: peak at sample {start + peak_idx_in_segment} (relative to start: {peak_idx_in_segment})")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (597 chars)</summary>

```
Variance in region [1110, 1221]:
  Max: 3431.86
  Mean: 2019.83
  At peak (1165): 723.51

All byte peaks: [1165, 952, 1130, 862, 4886, 5424, 125, 6555, 6955, 6467, 2298, 6610, 168, 600, 58, 6330]
Peaks std: 2741.58

Checking alignment by looking at first few traces in peak region:
Trace 0: peak at sample 1208 (relative to start: 98)
Trace 1: peak at sample 1218 (relative to start: 108)
Trace 2: peak at sample 1110 (relative to start: 0)
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\3702028983.py:19: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 6 | tokens: 21,330→117

**🤖 LLM:** 从结果可以看出，不同轨迹在建议区域内的峰值位置有显著差异（相对位置从0到108），这表明存在对齐问题。根据DKG知识图谱的建议，对于接触式智能卡AES，我应该使用静态对齐。让我使用从知识图谱中检索到的参数进行对齐：

**🔧 → `kg_search`** `{
  "keywords": [
    "contact smartcard",
    "AES",
    "static alignment",
    "parameters"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (34209 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (4): contact smartcard, AES, static alignment, parameters

**Summary**: 11 upper entities, 14 relationships, 16 diagnostic chains, 15 strategies


## 1. Upper Layer Entities (11)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### DeviceClass (4)

- **Contact Smartcard with 16-bit RISC CPU** — category=Smartcard, bus_width=16
- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated

### Pipeline (4)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collisio
...(truncated)
```
</details>


---

### Round 7 | tokens: 30,406→971

**🤖 LLM:** 从知识图谱中，我找到了针对接触式智能卡AES的静态对齐默认参数包：
- `length` = 100 samples
- `max_shift` = 400 samples  
- `threshold` = 85 percent
- `ref_trace` = 1 index (0-based)

根据策略"Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI"，我应该使用方差峰值区域作为对齐锚点，而不是明文相关性区域。让我先找到方差峰值区域：

**🔧 → `python_jupyter`**

<details><summary>Code (2385 chars)</summary>

```python
# 找到方差峰值区域作为对齐锚点
import numpy as np
import matplotlib.pyplot as plt

wave = np.load('data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy')
variance = wave.var(axis=0)

# 找到方差最大的区域
max_var_idx = np.argmax(variance)
print(f"Maximum variance at sample index: {max_var_idx}")
print(f"Maximum variance value: {variance[max_var_idx]:.2f}")

# 查看峰值附近的区域
window = 200
start_region = max(0, max_var_idx - window)
end_region = min(len(variance), max_var_idx + window)

# 绘制方差和平均波形
mean_wave = wave.mean(axis=0)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# 方差图
ax1.plot(variance)
ax1.axvline(max_var_idx, color='red', linestyle='--', alpha=0.7, label=f'Max variance at {max_var_idx}')
ax1.axvspan(start_region, end_region, alpha=0.2, color='green', label='Variance peak region')
ax1.set_xlabel('Sample index')
ax1.set_ylabel('Variance')
ax1.set_title('Variance across traces')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 平均波形图
ax2.plot(mean_wave)
ax2.axvline(max_var_idx, color='red', linestyle='--', alpha=0.7, label=f'Max variance at {max_var_idx}')
ax2.axvspan(start_region, end_region, alpha=0.2, color='green', label='Variance peak region')
ax2.set_xlabel('Sample index')
ax2.set_ylabel('Amplitude')
ax2.set_title('Mean trace')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('variance_peak_region.png')
plt.show()

# 在方差峰值区域找到合适的对齐起点
# 我们需要找到一个稳定的特征点，而不是随机选择
peak_region_wave = mean_wave[start_region:end_region]
# 找到区域内的局部最大值
from scipy.signal import find_peaks
peaks, properties = find_peaks(peak_region_wave, height=np.mean(peak_region_wave) + np.std(peak_region_wave))
if len(peaks) > 0:
    # 选择第一个显著的峰值
    alignment_start = start_region + peaks[0]
    print(f"\nFound peak in variance region at sample {alignment_start}")
    print(f"Peak height: {peak_region_wave[peaks[0]]:.2f}")
else:
    # 如果没有找到明显的峰值，使用方差最大值点
    alignment_start = max_var_idx
    print(f"\nUsing variance maximum point at sample {alignment_start}")

# 检查这个点是否适合作为对齐参考
print(f"\nChecking alignment candidate at sample {alignment_start}:")
print(f"  Mean value: {mean_wave[alignment_start]:.2f}")
print(f"  Variance: {variance[alignment_start]:.2f}")

# 查看附近几个轨迹在这个点的值
print(f"\nValues at sample {alignment_start} for first 5 traces:")
for i in range(5):
    print(f"  Trace {i}: {wave[i, alignment_start]:.2f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (508 chars)</summary>

```
Maximum variance at sample index: 1376
Maximum variance value: 5680.23

Found peak in variance region at sample 1222
Peak height: 20.47

Checking alignment candidate at sample 1222:
  Mean value: 20.47
  Variance: 2667.56

Values at sample 1222 for first 5 traces:
  Trace 0: 0.00
  Trace 1: 216.54
  Trace 2: 19.68
  Trace 3: -31.50
  Trace 4: -55.12
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1854766049.py:44: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 8 | tokens: 31,573→392

**🤖 LLM:** 我发现方差峰值在样本1376，但在该区域找到一个峰值在样本1222。然而，从不同轨迹在这个点的值来看，差异很大（从-55.12到216.54），这表明可能存在对齐问题。让我使用从知识图谱获取的参数进行静态对齐：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy",
  "start": 1222,
  "length": 100,
  "max_shift": 400,
  "threshold": 85,
  "ref_trace": 1,
  "plaintext_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "ciphertext_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `static_aligner`</b> (775 chars)</summary>

```
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\4195736077.py:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
  ref_trace = len(waves) // 2 if 1 is None else int(1)
{"out_aligned_npy": "aligned_20260424_042225_958753.npy", "plot_path": "align_overlay_20260424_042225_958753.png", "ref_trace_used": 1, "accepted": 100, "discarded": 0, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260424_042225_958753.npy", "plaintext_traces": 100, "out_ciphertext_npy": "ciphertext_aligned_20260424_042225_958753.npy", "ciphertext_traces": 100, "alignment_avg_correlation": 0.9981, "alignment_min_correlation": 0.9969, "acceptance_rate": 1.0}
```
</details>


![align_overlay_20260424_042225_958753.png](./align_overlay_20260424_042225_958753.png)


---

### Round 9 | tokens: 32,269→189

**🤖 LLM:** 很好！对齐成功，接受率为100%（所有100条轨迹都被接受），平均对齐相关性为0.9981，这表明对齐效果很好。现在让我对对齐后的轨迹进行CPA攻击：

**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_042225_958753.npy",
  "wave_npy": "aligned_20260424_042225_958753.npy",
  "candidates": 20,
  "leakage_model": "HW",
  "target": "S-box_out"
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2253 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.7252, "cpa_min_correlation": 0.507, "n_traces": 100, "target": "S-box_out", "plot_path": "cpa_result_20260424_042238_801463.png", "detail_file": "cpa_detail_20260424_042238_801463.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.891, "time_index": 1570, "gap_pct": 46.0}, {"byte": 1, "key": "0x22", "correlation": 0.8717, "time_index": 1876, "gap_pct": 42.1}, {"byte": 2, "key": "0x33", "correlation": 0.8346, "time_index": 2210, "gap_pct": 40.0}, {"byte": 3, "key": "0x44", "correlation": 0.863, "time_index": 2531, "gap_pct": 44.6}, {"byte": 4, "key": "0x55", "correlation": 0.8605, "time_index": 2850, "gap_pct": 43.8}, {"byte": 5, "key": "0x66", "correlation": 0.8319, "time_index": 3171, "gap_pct": 44.5}, {"byte": 6, "key": "0x77", "correlation": 0.7467, "time_index": 3490, "gap_pct": 37.7}, {"byte": 7, "key": "0x88", "correlation": 0.7703, "time_index": 3811, "gap_pct": 39.5}, {"byte": 8, "key": "0x99", "correlation": 0.7138, "time_index": 4130, "gap_pct": 28.5}, {"byte": 9, "key": "0xAA", "correlation": 0.7047, "time_index": 4450, "gap_pct": 32.6}, {"byte": 10, "key": "0xBB", "correlation": 0.633, "time_index": 4755, "gap_pct": 26.0}, {"byte": 11, "key": "0xCC", "correlation": 0.6898, "time_index": 5091, "gap_pct": 34.6}, {"byte": 12, "key": "0xDD", "correlation": 0.6007, "time_index": 5410, "gap_pct": 19.5}, {"byte": 13, "key": "0xEE", "correlation": 0.507, "time_index": 5765, "gap_pc
...(truncated)
```
</details>


![cpa_result_20260424_042238_801463.png](./cpa_result_20260424_042238_801463.png)


---

### Round 10 | tokens: 33,429→263

**🤖 LLM:** 太好了！对齐后的CPA攻击结果显著改善：
- 平均相关性从0.4648提高到0.7252
- 高置信度字节数：14/16（gap_pct ≥ 15%）
- 只有字节13和15是低置信度的

恢复的密钥是`112233445566778899AABBCCDDEEFF00`。让我验证这个密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "algorithm": "AES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_042225_958753.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_042225_958753.npy"
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "290AD4A41F352B837787D9581DFC4C43", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 3871ca2c3c022647f326197e85d4aa71... → 290AD4A41F352B837787D9581DFC4C43...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 11 | tokens: 33,826→429

**🤖 LLM:** 完美！密钥验证成功！我们成功恢复了AES-128密钥：`112233445566778899AABBCCDDEEFF00`。

让我总结一下攻击过程：

## 攻击总结

### 1. 初始状态
- **设备**: 接触式智能卡实现的AES-128
- **数据**: 100条轨迹，每条7400个采样点
- **直接CPA结果**: 平均相关性0.4648，高置信度字节数0/16，密钥验证失败

### 2. 关键步骤
1. **方差分析**: 发现方差峰值在样本1376附近
2. **静态对齐**: 使用DKG知识图谱推荐的接触式智能卡AES参数
   - 对齐起点: 1222（方差峰值区域）
   - 长度: 100 samples
   - 最大偏移: 400 samples  
   - 阈值: 85%
   - 参考轨迹: 1 (0-based)
3. **对齐结果**: 接受率100%，平均对齐相关性0.9981
4. **对齐后CPA**: 平均相关性提高到0.7252，高置信度字节数14/16

### 3. 恢复的密钥
**AES-128密钥**: `112233445566778899AABBCCDDEEFF00`

### 4. 验证结果
✅ 密钥验证通过 - 所有16个字节匹配

### 5. 关键成功因素
1. **遵循DKG策略**: 使用方差峰值区域作为对齐锚点，而不是明文相关性区域
2. **合适的参数**: 使用接触式智能卡特定的对齐参数（max_shift=400等）
3. **正确的攻击点**: 坚持使用S-box输出和HW泄漏模型（软件实现的默认配置）
4. **无需垂直对齐**: 根据DKG建议，软件实现通常不需要垂直对齐

这个案例展示了知识图谱在指导侧信道攻击中的价值，特别是针对特定设备类型（接触式智能卡）的参数选择和策略决策。


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 16,112 | 923 | 17,035 |
| 2 | 17,407 | 349 | 17,756 |
| 3 | 19,339 | 333 | 19,672 |
| 4 | 20,038 | 270 | 20,308 |
| 5 | 20,480 | 603 | 21,083 |
| 6 | 21,330 | 117 | 21,447 |
| 7 | 30,406 | 971 | 31,377 |
| 8 | 31,573 | 392 | 31,965 |
| 9 | 32,269 | 189 | 32,458 |
| 10 | 33,429 | 263 | 33,692 |
| 11 | 33,826 | 429 | 34,255 |
| **Total** | **276,209** | **4,839** | **281,048** |

## 8. Final Output

完美！密钥验证成功！我们成功恢复了AES-128密钥：`112233445566778899AABBCCDDEEFF00`。

让我总结一下攻击过程：

## 攻击总结

### 1. 初始状态
- **设备**: 接触式智能卡实现的AES-128
- **数据**: 100条轨迹，每条7400个采样点
- **直接CPA结果**: 平均相关性0.4648，高置信度字节数0/16，密钥验证失败

### 2. 关键步骤
1. **方差分析**: 发现方差峰值在样本1376附近
2. **静态对齐**: 使用DKG知识图谱推荐的接触式智能卡AES参数
   - 对齐起点: 1222（方差峰值区域）
   - 长度: 100 samples
   - 最大偏移: 400 samples  
   - 阈值: 85%
   - 参考轨迹: 1 (0-based)
3. **对齐结果**: 接受率100%，平均对齐相关性0.9981
4. **对齐后CPA**: 平均相关性提高到0.7252，高置信度字节数14/16

### 3. 恢复的密钥
**AES-128密钥**: `112233445566778899AABBCCDDEEFF00`

### 4. 验证结果
✅ 密钥验证通过 - 所有16个字节匹配

### 5. 关键成功因素
1. **遵循DKG策略**: 使用方差峰值区域作为对齐锚点，而不是明文相关性区域
2. **合适的参数**: 使用接触式智能卡特定的对齐参数（max_shift=400等）
3. **正确的攻击点**: 坚持使用S-box输出和HW泄漏模型（软件实现的默认配置）
4. **无需垂直对齐**: 根据DKG建议，软件实现通常不需要垂直对齐

这个案例展示了知识图谱在指导侧信道攻击中的价值，特别是针对特定设备类型（接触式智能卡）的参数选择和策略决策。
