# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_045432_709 |
| Duration | 152.4s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-7816_GLM5_DKG_20260424_045432_709` |
| Total LLM Calls | 10 |
| First Round | prompt: 16,658, completion: 1,139 |
| Last Round | prompt: 24,396, completion: 538 |
| Total Tokens | 213,581 (prompt: 208,073, completion: 5,508) |

## 3. User Query

```
帮我对一个接触式智能卡实现的AES密码算法波形进行CPA恢复密钥，明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个接触式智能卡实现的AES密码算法波形进行CPA恢复密钥，明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy'"

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
["AES", "Contact Smartcard", "CPA", "Power", "Key Recovery"]

Parsed Keywords: `["AES", "Contact Smartcard", "CPA", "Power", "Key Recovery"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 43185 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (45433 chars, click to expand)</summary>

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

**Search keywords** (5): AES, Contact Smartcard, CPA, Power, Key Recovery

**Summary**: 25 upper entities, 24 relationships, 20 diagnostic chains, 15 strategies


## 1. Upper Layer Entities (25)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### DeviceClass (4)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **Contact Smartcard with 16-bit RISC CPU** — category=Smartcard, bus_width=16

### Pipeline (10)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, canonical_source=round1_patch_002, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **Generic Side-Channel Attack Pipeline** — source=PAP-13-2009-EUROCRYPT-Standaert-Unified-Framework, trigger_condition=starting a side-channel key recovery attack, applicable_scenarios=general side-channel attacks on cryptographic implementations
- **Single-bit AES Key Recovery** — source=tutorial_lab, trigger_condition=when attacking an AES implementation with a single bit of leakage available, applicable_scenarios=AES implementations where a single bit of the S-box output is leaked (e.g., through power or EM side channels)

### RecoveryMethod (4)

- **Full Key Recovery** — input_type=correlation scores for all bytes
- **Full key recovery** — input_type=partial_subkey_candidates
- **Key Recovery** — input_type=SAT solution
- **Key recovery** — input_type=round keys

### StatMethod (6)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Compare hypothetical power consumption with measured traces** — type=non_profiled

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
- `RecoveryMethod:Full Key Recovery` —[consists_of [parameters_note=repeat for all 16 bytes of AES-128 key, source_text=Full Key Recovery, support_count=1, is_optional=False]]→ `Pipeline:CPA Attack on AES Firmware Implementation`
- `RecoveryMethod:Full key recovery` —[relates_to [role=add_step]]→ `Action:Apply key enumeration algorithms`
- `RecoveryMethod:Full key recovery` —[consists_of [parameters_note=repeat for all 8 S-boxes to recover 48-bit round subkey; remaining 8 bits via exhaustive search or analyzing another round, source_text=repeat for all 8 S-boxes to recover 48-bit round subkey, support_count=1, is_optional=False]]→ `Pipeline:Differential Power Analysis (DPA) on DES`
- `Pipeline:Generic Side-Channel Attack Pipeline` —[consists_of [parameters_note=apply statistical test T to compare model/partition with leakages, source_text=Statistical test: apply statistical test T to compare model/partition with leakages, support_count=1, is_optional=False]]→ `StatMethod:Statistical Test`
- `Pipeline:Generic Side-Channel Attack Pipeline` —[consists_of [parameters_note=mapping R transforms leakages, may include filtering, averaging, condition=if leakages and predictions have different number of samples or post-processing needed, source_text=Leakage reduction: mapping R transforms leakages, may include filtering, averaging, support_count=1]]→ `Preprocessing:Leakage Reduction`

## 3. Diagnostic Chains (20)


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

### Obs: `key_recovery_limit` — = 0
- **Cause** (high): key recovery algorithm is disabled
- **Action**: set W to a value greater than 0
  - operation: `adjust_param`
  - target: `key_recovery_limit`
  - strategy: set W (key recovery limit) to a positive integer

### Obs: `trace_count` — any
- **Cause** (high): The attack may succeed with fewer traces than the total captured. Using all traces for analysis is unnecessary if the key is recovered earlier.
- **Check**: Plotting Partial Guessing Entropy (PGE) vs. Traces shows the PGE dropping to zero before the maximum trace count.
- **Action**: Use the PGE vs. Traces plot to determine the minimum number of traces needed for successful key recovery and adjust future capture/analysis accordingly.
  - operation: `adjust_param`
  - target: `trace count for analysis`
  - strategy: Use the PGE vs. Traces plot to identify the point of key recovery and optimize the number of traces captured in subsequent attacks.
- **Relates to**: DiagnosticMethod:`Plot PGE vs. Traces`

### Obs: `cpa_avg_correlation` — no key recovery, low correlation after SAD resynchronization
- **Cause** (high): Jitter during the encryption operation (multiple delays) cannot be corrected by a single global shift (SAD).
- **Check**: CPA still fails after SAD; visual inspection shows residual jitter in the aligned traces.
- **Action**: Replace ResyncSAD with ResyncDTW (Dynamic Time Warp).
  - operation: `switch_component`
  - target: `preprocessing method`
  - strategy: Replace ResyncSAD with ResyncDTW (Dynamic Time Warp). When jitter occurs during the encryption operation (not just at trigger), use DTW instead of SAD for resynchronization.
- **Relates to**: Preprocessing:`ResyncSAD`

### Obs: `attack_execution_time` — any
- **Cause** (high): Conditional leakage averaging can speed up key recovery time but requires more traces
- **Check**: implied by parameter option description
- **Action**: Set condavg = true to use conditional leakage averaging for faster key recovery at the cost of requiring more traces
  - operation: `adjust_param`
  - target: `attack.condavg`
  - strategy: Set condavg = true to use conditional leakage averaging for faster key recovery at the cost of requiring more traces
- **Relates to**: StatMethod:`CPA with conditional averaging`

### Obs: `alignment_discard_rate` — 30-50%
- **Cause** (high): max_shift too small, so only traces with small offset are kept, which are not enough for the second half.
- **Check**: Check peak position variation.
- **Action**: Check peak position variation and set max_shift to the actual range.
  - operation: `adjust_param`
  - target: `alignment.max_shift`
  - strategy: When partial key recovery occurs, check max_shift first.
- **Relates to**: Preprocessing:`Static Alignment`

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

### ⚠ [anti_pattern_set] Non-sensitive leakage times to ignore
- **Trigger**: when evaluating side-channel leakage for block ciphers
- **Rationale**: These leakage points do not represent a vulnerability for key recovery because they depend on known data or are not directly exploitable. Failing a device based on them would be overly conservative.
- **Anti-pattern 1**: (unnamed)
  - Why: Leakage in outer rounds is less sensitive because it depends on known plaintext/ciphertext and is harder to exploit for key recovery.
- **Anti-pattern 2**: (unnamed)
  - Why: Key loading often involves known values or is not directly exploitable for key recovery in the same way as intermediate cryptographic operations.
- **Anti-pattern 3**: (unnamed)
  - Why: Plaintext and ciphertext are known, so their leakage does not directly reveal the secret key.
- **Applies to**: Algorithm:AES, StatMethod:DPA

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

### 📋 [troubleshooting_checklist] Adaptive Message Selection for Efficient Key Recovery
- **Trigger**: When using the basic collision-correlation method and wanting to reduce the number of messages (and thus total traces) required for key recovery.
- **Rationale**: This method exploits non-collision events (which are numerous) to build blacklists and uses graph connectivity to guide adaptive message selection, maximizing new information per message.
- **[rank 1]** if `Define penalty of candidate message` → For each pair (i1, i2), check if m_i1 ⊕ m_i2 is already blacklisted. If yes, penalty++. If no, penalty remains unchanged.
- **[rank 2]** if `Refine penalty calculation` → If (i1, i2) and (i1, i2') are in same connected component and m_i1 ⊕ m_i2 = m_i2 ⊕ m_i2' is known, then the two opportunities count as one. Increase penalty by 1.
- **[rank 3]** if `Select candidate message with minimal penalty` → Use a two-step heuristic: 1) Randomly pick a few hundred messages, select the one with lowest penalty. 2) Iteratively try small modifications to the best candidate until no improvement.
- **Applies to**: Algorithm:AES, StatMethod:Collision-Correlation Attack

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-7816_GLM5_DKG_20260424_045432_709
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-7816_GLM5_DKG_20260424_045432_709/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 16,658→1,139

**🤖 LLM:** 我来帮你对接触式智能卡的AES波形进行CPA攻击。让我先分析波形特征，然后按照标准流程进行攻击。

## 第一步：波形可视化与特征分析

**🔧 → `python_jupyter`**

<details><summary>Code (1860 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy')
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy')

print(f"波形形状: {wave.shape}")
print(f"明文形状: {plain.shape}")
print(f"密文形状: {cipher.shape}")
print(f"波形数据类型: {wave.dtype}")
print(f"波形范围: [{wave.min():.2f}, {wave.max():.2f}]")

# 绘制几条波形
plt.figure(figsize=(14, 8))

# 绘制前5条波形
plt.subplot(2, 2, 1)
for i in range(min(5, wave.shape[0])):
    plt.plot(wave[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Point')
plt.ylabel('Power')
plt.title('First 5 Traces (Full Waveform)')
plt.legend()
plt.grid(True, alpha=0.3)

# 绘制平均波形
plt.subplot(2, 2, 2)
avg_wave = np.mean(wave, axis=0)
plt.plot(avg_wave)
plt.xlabel('Sample Point')
plt.ylabel('Average Power')
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
plt.ylabel('Standard Deviation')
plt.title('Standard Deviation Across Traces')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

# 分析方差峰值区域（可能的加密区域）
var_peaks = np.where(var_wave > np.mean(var_wave) + 2*np.std(var_wave))[0]
if len(var_peaks) > 0:
    print(f"\n高方差区域（可能的加密区域）: 样本点 {var_peaks[0]} 到 {var_peaks[-1]}")
    print(f"方差峰值位置: {np.argmax(var_wave)}")
```
</details>

**📋 ← `python_jupyter`:** `波形形状: (100, 7400)
明文形状: (100, 16)
密文形状: (100, 16)
波形数据类型: float32
波形范围: [-86.61, 251.97]

高方差区域（可能的加密区域）: 样本点 1100 到 6687
方差峰值位置: 1376
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\786842865.py:57: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 2 | tokens: 17,533→739

**🔧 → `python_jupyter`**

<details><summary>Code (1823 chars)</summary>

```python
# 更详细地分析波形特征
import numpy as np
import matplotlib.pyplot as plt

wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy')

# 计算滑动窗口方差，更精确地定位加密区域
window_size = 100
var_smooth = np.convolve(np.var(wave, axis=0), np.ones(window_size)/window_size, mode='valid')

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.plot(var_smooth)
plt.xlabel('Sample Point')
plt.ylabel('Smoothed Variance')
plt.title('Smoothed Variance (window=100)')
plt.grid(True, alpha=0.3)

# 找到方差突增的位置
var_threshold = np.mean(var_smooth) + np.std(var_smooth)
high_var_regions = np.where(var_smooth > var_threshold)[0]
if len(high_var_regions) > 0:
    print(f"平滑后方差突增区域: {high_var_regions[0]} 到 {high_var_regions[-1]}")
    
    # 标记可能的加密起始和结束位置
    enc_start = high_var_regions[0]
    enc_end = high_var_regions[-1]
    print(f"可能的加密区域: {enc_start} - {enc_end}")
    
    plt.axvline(x=enc_start, color='r', linestyle='--', label=f'Enc Start: {enc_start}')
    plt.axvline(x=enc_end, color='r', linestyle='--', label=f'Enc End: {enc_end}')
    plt.legend()

# 绘制前1000个点的细节（通常包含IO和预处理）
plt.subplot(1, 2, 2)
plt.plot(wave[0, :1500])
plt.xlabel('Sample Point')
plt.ylabel('Power')
plt.title('First 1500 Points of Trace 0')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_detail.png', dpi=150)
plt.show()

# 检查是否有明显的峰值模式（可能对应AES轮次）
avg_wave = np.mean(wave, axis=0)
# 在加密区域内寻找峰值
if len(high_var_regions) > 0:
    enc_region = avg_wave[enc_start:enc_end]
    from scipy.signal import find_peaks
    peaks, properties = find_peaks(enc_region, height=np.mean(enc_region), distance=50)
    print(f"\n在加密区域内检测到 {len(peaks)} 个峰值")
    if len(peaks) > 0:
        print(f"前10个峰值位置（相对于加密起始）: {peaks[:10]}")
        print(f"前10个峰值位置（绝对位置）: {peaks[:10] + enc_start}")
```
</details>

**📋 ← `python_jupyter`:** `平滑后方差突增区域: 1034 到 6681
可能的加密区域: 1034 - 6681

在加密区域内检测到 63 个峰值
前10个峰值位置（相对于加密起始）: [  7  93 190 245 343 457 527 595 692 775]
前10个峰值位置（绝对位置）: [1041 1127 1224 1279 1377 1491 1561 1629 1726 1809]
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1431018320.py:45: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 18,348→381

**🤖 LLM:** 好的，波形分析显示：
- **100条波形**，每条7400个采样点
- **加密区域**大约在样本点1034-6681
- **方差峰值**在1376附近，这可能是第一轮S-box操作的位置

## 第二步：直接CPA探测（无预处理）

根据知识图谱建议，接触式智能卡AES应使用**S-box_out + HW模型**。我先进行直接CPA探测：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (3567 chars)</summary>

```
{"recovered_key": "146F98806836F55937FBCD36B5CF7096", "cpa_avg_correlation": 0.4648, "cpa_min_correlation": 0.4358, "n_traces": 100, "target": "S-box_out", "plot_path": "cpa_result_20260424_045601_406957.png", "detail_file": "cpa_detail_20260424_045601_406957.json", "per_byte": [{"byte": 0, "key": "0x14", "correlation": 0.4497, "time_index": 4625, "gap_pct": 0.5}, {"byte": 1, "key": "0x6F", "correlation": 0.4383, "time_index": 408, "gap_pct": 2.2}, {"byte": 2, "key": "0x98", "correlation": 0.4483, "time_index": 3443, "gap_pct": 2.8}, {"byte": 3, "key": "0x80", "correlation": 0.5045, "time_index": 1938, "gap_pct": 14.4}, {"byte": 4, "key": "0x68", "correlation": 0.4358, "time_index": 714, "gap_pct": 4.5}, {"byte": 5, "key": "0x36", "correlation": 0.4763, "time_index": 6619, "gap_pct": 1.0}, {"byte": 6, "key": "0xF5", "correlation": 0.4802, "time_index": 586, "gap_pct": 5.5}, {"byte": 7, "key": "0x59", "correlation": 0.4638, "time_index": 2732, "gap_pct": 8.4}, {"byte": 8, "key": "0x37", "correlation": 0.4605, "time_index": 4182, "gap_pct": 4.5}, {"byte": 9, "key": "0xFB", "correlation": 0.4505, "time_index": 5658, "gap_pct": 3.1}, {"byte": 10, "key": "0xCD", "correlation": 0.4594, "time_index": 6070, "gap_pct": 8.2}, {"byte": 11, "key": "0x36", "correlation": 0.4719, "time_index": 1381, "gap_pct": 3.6}, {"byte": 12, "key": "0xB5", "correlation": 0.4855, "time_index": 6826, "gap_pct": 3.4}, {"byte": 13, "key": "0xCF", "correlation": 0.4655, "time_index": 1142, "gap_pct": 3.0}, 
...(truncated)
```
</details>


![cpa_result_20260424_045601_406957.png](./cpa_result_20260424_045601_406957.png)


---

### Round 4 | tokens: 20,225→313

**🤖 LLM:** 直接CPA结果显示：
- **high_confidence_count = 0/16**（红带）
- 平均相关系数0.4648（不错）
- 但所有字节的gap都低于15%阈值

让我先验证这个密钥：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "key_hex": "146F98806836F55937FBCD36B5CF7096",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "CCBC091FEBB0601B0FA3261BBF523C5D", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 3871ca2c3c022647f326197e85d4aa71... → CCBC091FEBB0601B0FA3261BBF523C5D...\n❌ Key verification FAILED — 16/16 ciphertext bytes differ\n   Expected:  290AD4A41F352B837787D9581DFC4C43\n   Got:       CCBC091FEBB0601B0FA3261BBF523C5D\n\n   ⚠️ IMPORTANT: '16 ciphertext bytes differ' does NOT mean '16 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 5 | tokens: 20,811→708

**🤖 LLM:** 密钥验证失败。让我检查波形是否需要静态对齐：

**🔧 → `python_jupyter`**

<details><summary>Code (1460 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy')

# 检查波形对齐情况
# 绘制多条波形在加密区域的叠加
enc_start = 1034
enc_end = 2500  # 只看前半部分，包含第一轮

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
for i in range(min(20, wave.shape[0])):
    plt.plot(wave[i, enc_start:enc_end], alpha=0.5)
plt.xlabel('Sample Point (relative to enc_start)')
plt.ylabel('Power')
plt.title(f'20 Traces Overlay (samples {enc_start}-{enc_end})')
plt.grid(True, alpha=0.3)

# 计算波形间的相关性，检查对齐质量
plt.subplot(1, 2, 2)
# 使用第一条波形作为参考
ref = wave[0, enc_start:enc_end]
correlations = []
for i in range(wave.shape[0]):
    corr = np.corrcoef(ref, wave[i, enc_start:enc_end])[0, 1]
    correlations.append(corr)

plt.hist(correlations, bins=20, edgecolor='black')
plt.xlabel('Correlation with Trace 0')
plt.ylabel('Count')
plt.title('Trace Alignment Quality')
plt.axvline(x=np.mean(correlations), color='r', linestyle='--', label=f'Mean: {np.mean(correlations):.3f}')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('alignment_check.png', dpi=150)
plt.show()

print(f"波形间平均相关性: {np.mean(correlations):.4f}")
print(f"波形间相关性范围: [{np.min(correlations):.4f}, {np.max(correlations):.4f}]")
print(f"相关性标准差: {np.std(correlations):.4f}")

# 如果相关性低于0.9，说明需要对齐
if np.mean(correlations) < 0.9:
    print("\n⚠️ 波形相关性较低，可能需要静态对齐")
else:
    print("\n✓ 波形对齐质量良好")
```
</details>

**📋 ← `python_jupyter`:** `波形间平均相关性: 0.0141
波形间相关性范围: [-0.2550, 1.0000]
相关性标准差: 0.1762

⚠️ 波形相关性较低，可能需要静态对齐
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1160749262.py:40: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 6 | tokens: 21,464→439

**🤖 LLM:** 波形相关性极低（0.0141），说明存在严重错位，必须进行静态对齐。

## 第三步：静态对齐

根据知识图谱建议，使用接触式智能卡AES的标准参数：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy",
  "start": 1377,
  "length": 100,
  "max_shift": 400,
  "threshold": 85,
  "ref_trace": 1,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `static_aligner`</b> (775 chars)</summary>

```
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2053680648.py:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
  ref_trace = len(waves) // 2 if 1 is None else int(1)
{"out_aligned_npy": "aligned_20260424_045648_970100.npy", "plot_path": "align_overlay_20260424_045648_970100.png", "ref_trace_used": 1, "accepted": 100, "discarded": 0, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260424_045648_970100.npy", "plaintext_traces": 100, "out_ciphertext_npy": "ciphertext_aligned_20260424_045648_970100.npy", "ciphertext_traces": 100, "alignment_avg_correlation": 0.9712, "alignment_min_correlation": 0.881, "acceptance_rate": 1.0}
```
</details>


![align_overlay_20260424_045648_970100.png](./align_overlay_20260424_045648_970100.png)


---

### Round 7 | tokens: 22,027→164

**🤖 LLM:** 对齐成功！接受率100%，平均相关性0.9712。现在用对齐后的波形重新CPA：

**🔧 → `aes_cpa_attack`** `{
  "wave_npy": "aligned_20260424_045648_970100.npy",
  "plaintext_npy": "plaintext_aligned_20260424_045648_970100.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2358 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.715, "cpa_min_correlation": 0.4793, "n_traces": 100, "target": "S-box_out", "plot_path": "cpa_result_20260424_045657_699546.png", "detail_file": "cpa_detail_20260424_045657_699546.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.8706, "time_index": 1570, "gap_pct": 44.2}, {"byte": 1, "key": "0x22", "correlation": 0.8674, "time_index": 1877, "gap_pct": 43.9}, {"byte": 2, "key": "0x33", "correlation": 0.8387, "time_index": 2210, "gap_pct": 43.5}, {"byte": 3, "key": "0x44", "correlation": 0.8485, "time_index": 2516, "gap_pct": 43.4}, {"byte": 4, "key": "0x55", "correlation": 0.8562, "time_index": 2850, "gap_pct": 43.3}, {"byte": 5, "key": "0x66", "correlation": 0.8097, "time_index": 3171, "gap_pct": 42.1}, {"byte": 6, "key": "0x77", "correlation": 0.7326, "time_index": 3490, "gap_pct": 37.9}, {"byte": 7, "key": "0x88", "correlation": 0.7712, "time_index": 3811, "gap_pct": 39.6}, {"byte": 8, "key": "0x99", "correlation": 0.6957, "time_index": 4130, "gap_pct": 29.1}, {"byte": 9, "key": "0xAA", "correlation": 0.6913, "time_index": 4450, "gap_pct": 23.1}, {"byte": 10, "key": "0xBB", "correlation": 0.6264, "time_index": 4755, "gap_pct": 24.3}, {"byte": 11, "key": "0xCC", "correlation": 0.6879, "time_index": 5091, "gap_pct": 33.9}, {"byte": 12, "key": "0xDD", "correlation": 0.6177, "time_index": 5410, "gap_pct": 23.3}, {"byte": 13, "key": "0xEE", "correlation": 0.4793, "time_index": 5765, "ga
...(truncated)
```
</details>


![cpa_result_20260424_045657_699546.png](./cpa_result_20260424_045657_699546.png)


---

### Round 8 | tokens: 23,156→283

**🤖 LLM:** 太好了！对齐后CPA效果显著提升：
- **high_confidence_count = 13/16**（绿带！）
- 平均相关系数从0.46提升到0.715
- 恢复密钥：`112233445566778899AABBCCDDEEFF00`

让我验证这个密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "AES",
  "ciphertext_npy": "ciphertext_aligned_20260424_045648_970100.npy",
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "plaintext_npy": "plaintext_aligned_20260424_045648_970100.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "290AD4A41F352B837787D9581DFC4C43", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 3871ca2c3c022647f326197e85d4aa71... → 290AD4A41F352B837787D9581DFC4C43...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 9 | tokens: 23,455→804

**🤖 LLM:** ## ✅ 攻击成功！

**恢复的密钥**：`112233445566778899AABBCCDDEEFF00`

密钥验证通过！让我总结一下攻击过程：

**🔧 → `python_jupyter`**

<details><summary>Code (1479 chars)</summary>

```python
import json

# 生成攻击报告
report = {
    "攻击算法": "AES-128",
    "设备类型": "接触式智能卡",
    "波形数量": 100,
    "采样点数": 7400,
    "攻击方法": "CPA (Correlation Power Analysis)",
    "攻击目标": "S-box output",
    "泄漏模型": "Hamming Weight (HW)",
    "预处理": {
        "静态对齐": {
            "起始点": 1377,
            "长度": 100,
            "最大偏移": 400,
            "阈值": 85,
            "参考轨迹": 1,
            "接受率": "100%",
            "平均相关性": 0.9712
        }
    },
    "CPA结果": {
        "恢复密钥": "112233445566778899AABBCCDDEEFF00",
        "高置信度字节": "13/16",
        "平均相关系数": 0.715,
        "最小相关系数": 0.4793
    },
    "验证结果": "✅ 通过 - 所有16字节匹配"
}

print("=" * 60)
print("AES-128 接触式智能卡 CPA攻击报告")
print("=" * 60)
for key, value in report.items():
    if isinstance(value, dict):
        print(f"\n{key}:")
        for k, v in value.items():
            if isinstance(v, dict):
                print(f"  {k}:")
                for kk, vv in v.items():
                    print(f"    - {kk}: {vv}")
            else:
                print(f"  - {k}: {v}")
    else:
        print(f"{key}: {value}")

print("\n" + "=" * 60)
print("关键成功因素:")
print("=" * 60)
print("1. ✓ 正确识别波形错位问题（相关性0.0141）")
print("2. ✓ 使用方差分析定位加密区域（样本1034-6681）")
print("3. ✓ 应用标准静态对齐参数（接触式智能卡AES）")
print("4. ✓ 选择正确的攻击目标（S-box_out + HW模型）")
print("5. ✓ 100条轨迹足够恢复完整密钥")

# 保存报告
with open('attack_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("\n报告已保存至: attack_report.json")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (824 chars)</summary>

```
============================================================
AES-128 接触式智能卡 CPA攻击报告
============================================================
攻击算法: AES-128
设备类型: 接触式智能卡
波形数量: 100
采样点数: 7400
攻击方法: CPA (Correlation Power Analysis)
攻击目标: S-box output
泄漏模型: Hamming Weight (HW)

预处理:
  静态对齐:
    - 起始点: 1377
    - 长度: 100
    - 最大偏移: 400
    - 阈值: 85
    - 参考轨迹: 1
    - 接受率: 100%
    - 平均相关性: 0.9712

CPA结果:
  - 恢复密钥: 112233445566778899AABBCCDDEEFF00
  - 高置信度字节: 13/16
  - 平均相关系数: 0.715
  - 最小相关系数: 0.4793
验证结果: ✅ 通过 - 所有16字节匹配

============================================================
关键成功因素:
============================================================
1. ✓ 正确识别波形错位问题（相关性0.0141）
2. ✓ 使用方差分析定位加密区域（样本1034-6681）
3. ✓ 应用标准静态对齐参数（接触式智能卡AES）
4. ✓ 选择正确的攻击目标（S-box_out + HW模型）
5. ✓ 100条轨迹足够恢复完整密钥

报告已保存至: attack_report.json
```
</details>


---

### Round 10 | tokens: 24,396→538

**🤖 LLM:** ## 🎉 攻击成功总结

我已经成功对接触式智能卡的AES-128波形进行了CPA攻击，完整流程如下：

### 📊 攻击流程

1. **波形分析**
   - 100条波形，每条7400个采样点
   - 通过方差分析定位加密区域：样本1034-6681
   - 发现波形严重错位（相关性仅0.0141）

2. **直接CPA探测**
   - 未对齐波形CPA失败（high_confidence_count = 0/16）
   - 确认必须进行静态对齐

3. **静态对齐**
   - 参数：start=1377, length=100, max_shift=400, threshold=85
   - 结果：接受率100%，平均相关性0.9712

4. **对齐后CPA**
   - **恢复密钥**：`112233445566778899AABBCCDDEEFF00`
   - 高置信度字节：13/16（绿带）
   - 平均相关系数：0.715

5. **密钥验证**
   - ✅ **验证通过** - 所有16字节匹配

### 🔑 关键成功因素

1. ✓ 正确识别波形错位问题
2. ✓ 使用方差分析定位加密区域
3. ✓ 应用知识图谱标准对齐参数
4. ✓ 选择正确攻击目标（S-box_out + HW模型）
5. ✓ 100条轨迹足够恢复完整密钥

所有结果文件已保存在当前会话目录中。


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 16,658 | 1,139 | 17,797 |
| 2 | 17,533 | 739 | 18,272 |
| 3 | 18,348 | 381 | 18,729 |
| 4 | 20,225 | 313 | 20,538 |
| 5 | 20,811 | 708 | 21,519 |
| 6 | 21,464 | 439 | 21,903 |
| 7 | 22,027 | 164 | 22,191 |
| 8 | 23,156 | 283 | 23,439 |
| 9 | 23,455 | 804 | 24,259 |
| 10 | 24,396 | 538 | 24,934 |
| **Total** | **208,073** | **5,508** | **213,581** |

## 8. Final Output

## 🎉 攻击成功总结

我已经成功对接触式智能卡的AES-128波形进行了CPA攻击，完整流程如下：

### 📊 攻击流程

1. **波形分析**
   - 100条波形，每条7400个采样点
   - 通过方差分析定位加密区域：样本1034-6681
   - 发现波形严重错位（相关性仅0.0141）

2. **直接CPA探测**
   - 未对齐波形CPA失败（high_confidence_count = 0/16）
   - 确认必须进行静态对齐

3. **静态对齐**
   - 参数：start=1377, length=100, max_shift=400, threshold=85
   - 结果：接受率100%，平均相关性0.9712

4. **对齐后CPA**
   - **恢复密钥**：`112233445566778899AABBCCDDEEFF00`
   - 高置信度字节：13/16（绿带）
   - 平均相关系数：0.715

5. **密钥验证**
   - ✅ **验证通过** - 所有16字节匹配

### 🔑 关键成功因素

1. ✓ 正确识别波形错位问题
2. ✓ 使用方差分析定位加密区域
3. ✓ 应用知识图谱标准对齐参数
4. ✓ 选择正确攻击目标（S-box_out + HW模型）
5. ✓ 100条轨迹足够恢复完整密钥

所有结果文件已保存在当前会话目录中。
