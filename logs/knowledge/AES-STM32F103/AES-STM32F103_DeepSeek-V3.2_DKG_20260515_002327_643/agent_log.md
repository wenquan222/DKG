# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260515_002327_643 |
| Duration | 2068.6s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp_knowledge_only\AES-STM32F103_DeepSeek-V3.2_DKG_20260515_002327_643` |
| Total LLM Calls | 14 |
| First Round | prompt: 13,192, completion: 575 |
| Last Round | prompt: 57,191, completion: 929 |
| Total Tokens | 455,762 (prompt: 439,840, completion: 15,922) |

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

LLM Response: ["AES", "STM32F103", "MCU", "CPA", "Power", "S-box Output", "Hamming Weight"]

Parsed Keywords: `["AES", "STM32F103", "MCU", "CPA", "Power", "S-box Output", "Hamming Weight"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 45355 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (48152 chars, click to expand)</summary>

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

**Search keywords** (7): AES, STM32F103, MCU, CPA, Power, S-box Output, Hamming Weight

**Summary**: 38 upper entities, 29 relationships, 16 diagnostic chains, 15 strategies


## 1. Upper Layer Entities (38)


### Algorithm (1)

- **AES** — num_rounds=['10', '14'], encryption_mode=['CBC', 'ECB'], key_length=['128', '256']

### AttackPoint (6)

- **Inverse S-box Output** — round=['13', '14']
- **Masked S-box Output**
- **S-box Output** — required_data=['ciphertext', 'plaintext'], round=['1', '13', '14', 'first', 'first (round 10 key schedule)', 'first four rounds', 'last']
- **S-box Output and Mask** — required_data=plaintext, round=first
- **S-box output** — round=['1', 'first']
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

### Pipeline (7)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values

### StatMethod (8)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **First CPA probe (without alignment)** — type=non_profiled
- **Compare hypothetical power consumption with measured traces** — type=non_profiled
- **Generate Hamming weight models for S-box output** — type=non_profiled

## 2. Relationships (29)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: offset, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:offset`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
- `DeviceClass:32-bit STM Controller` —[works_with [source_text=CHES CTF ... AutoPOI ... 1830, support_count=1, confidence=0.2, source_papers=["PAP-74-2023-ePrint-AutoPOI"]]]→ `Algorithm:AES`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `LeakageModel:identity`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=For the CHES_CTF dataset, 13 of the 16 tested ∆ values are successfully recovered, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Pipeline:Plaintext-based Side-channel Collision Attack (PSCCA)`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `Preprocessing:Resampling`
- `DeviceClass:32-bit STM microcontroller` —[works_with [source_text=exp_003__PAP-77, support_count=1, confidence=0.2, source_papers=["PAP-77-2023-ePrint-Plaintext-Collision"]]]→ `AttackPoint:S-box Output`
- `StatMethod:CPA` —[strategy_applies_to [condition=Non-profiled CPA on DES (any device class: contact smartcard, contactless smartcard, FPGA, MCU). The DES CPA tool has returned a high-confidence round-1 48-bit subkey K1 (high_confidence_count >= 6/8 S-boxes, gap_pct >= 20%, avg_correlation reasonable for the device class), BUT encrypt_decrypt_verify against the DES master key has returned MISMATCH. The DES CPA tool may have populated a 'master_key' field with a placeholder (K1 zero-padded, K1 duplicated, or an arbitrary parity assignment) that is not the actual master key., applicability=specific, source_papers=["expert_experience"]]]→ `Strategy:DES master key recovery from 48-bit round-1 subkey via PC-2 inverse + parity enumeration`
- `StatMethod:CPA` —[strategy_applies_to [condition=Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap), applicability=specific, source_papers=["expert_experience"]]]→ `Strategy:Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)`
- `StatMethod:CPA` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `StatMethod:CPA` —[strategy_applies_to [condition=Any non-profiled CPA workflow on AES / DES / SM4 across any device class. Triggered whenever the agent has obtained a CPA output (typically high_confidence_count, gap_pct, avg_correlation looking favourable for the device class) and is about to write a final natural-language success message to the user, OR is considering terminating the session., applicability=general, source_papers=["expert_experience"]]]→ `Strategy:Do NOT declare key-recovery success based on CPA-internal metrics; encrypt_decrypt_verify MATCH is mandatory`
- `StatMethod:CPA` —[strategy_applies_to [condition=Non-profiled CPA on any symmetric block cipher (AES / DES / SM4); at least one prior CPA run (aligned or direct) has yielded high_confidence_count in or above the gray band (AES >= 10/16, DES >= 3/8, SM4 per-round >= 2/4); key_search was invoked once with default or near-default parameters and returned found=false; OR a dual-mode (e.g., linear-HD / S-box_in on contactless AES / DES) attack returned two candidates with per-byte gap_pct == 0, applicability=specific, source_papers=["expert_experience"]]]→ `Strategy:key_search found=false is NOT CPA failure — escalate search budget + dual-mode both branches BEFORE pivoting any other dimension`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use output_vs_time method to plot correlation of guesses over time, condition=to locate leakage in time, source_text=Plot Output Vs. Time, support_count=1]]→ `DiagnosticMethod:Plot Output Vs. Time`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Callback function called at reporting interval (default 25), condition=to get feedback during attack, source_text=Monitor attack progress with callback, support_count=1]]→ `DiagnosticMethod:Monitor attack progress with callback`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use corr_vs_trace method to plot correlation values, condition=to compare correct key guess with incorrect ones, source_text=Plot Correlation vs. Traces, support_count=1]]→ `DiagnosticMethod:Plot Correlation vs. Traces`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use pge_vs_trace method to plot partial guessing entropy, condition=to see attack progression, source_text=Plot PGE vs. Traces, support_count=1]]→ `DiagnosticMethod:Plot PGE vs. Traces`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use cpa() function with project and leakage model, source_text=Run CPA attack, support_count=1, is_optional=False]]→ `StatMethod:CPA`
- `AttackPoint:S-box Output` —[strategy_applies_to [condition=Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear, applicability=specific, source_papers=["expert_experience"]]]→ `Strategy:Do NOT switch leakage target family as first response to low correlation on software implementations`
- `StatMethod:Generate Hamming weight models for S-box output` —[consists_of [parameters_note=models are lookup tables for the leakage of each possible S-box output, source_text=Generate Hamming weight models for S-box output, support_count=1, is_optional=False]]→ `Pipeline:SCALib CPA Attack on AES`
- `AttackPoint:Inverse S-box Output` —[has_attack_point [source_text=attack_point: Inverse S-box Output, round: 14, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `Algorithm:AES`
- `AttackPoint:Inverse S-box Output` —[relates_to [role=switch_component]]→ `Action:Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.`
- `AttackPoint:Masked S-box Output` —[works_with [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Avoid using the identity model for bijective S-boxes in MIA; use a non-bijective model (e.g., Hamming weight) or target a non-bijective intermediate value (e.g., predict only a subset of bits).`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Use a non-injective leakage function that incurs information loss (e.g., Hamming weight, LSB, MSB).`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Use target S-box_out with HW model.`
- `LeakageModel:Hamming Weight` —[relates_to [role=adjust_param]]→ `Action:Set the target to 'S-box out' and model to 'HW' for first-round CPA on AES`

## 3. Diagnostic Chains (16)


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
- **Relates to**: AttackPoint:`Inverse S-box Output`

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

### ⭐ • [canonical_pipeline_principle] DES master key recovery from 48-bit round-1 subkey via PC-2 inverse + parity enumeration
- **Trigger**: Non-profiled CPA on DES (any device class: contact smartcard, contactless smartcard, FPGA, MCU). The DES CPA tool has returned a high-confidence round-1 48-bit subkey K1 (high_confidence_count >= 6/8 S-boxes, gap_pct >= 20%, avg_correlation reasonable for the device class), BUT encrypt_decrypt_verify against the DES master key has returned MISMATCH. The DES CPA tool may have populated a 'master_key' field with a placeholder (K1 zero-padded, K1 duplicated, or an arbitrary parity assignment) that is not the actual master key.
- **Rationale**: CPA on round 1 recovers only the 48-bit subkey K1. PC-2 omits eight bits of the 56-bit state and the parity bits are fixed by the byte parity rule, so the master key is one of at most 256 candidates; enumerating them is bounded and far cheaper than re-running the attack.
- **Content**: [{"principle": "DES has a 64-bit master key (with 8 parity bits) and CPA on round 1 only directly recovers the 48-bit round-1 subkey K1. Recovering the master key from K1 requires (a) inverting PC-2 to recover C1||D1 (56 bits with 8 missing positions), (b) right-shifting by 1 to recover C0||D0, (c) inverting PC-1 to recover the 64-bit master key with 8 unknown parity bits. The total brute-force sp
- **Applies to**: StatMethod:CPA, Algorithm:DES

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

**[No SCA-Specific Tools — Implementation Required]**
You have access to a Python (Jupyter) kernel and the kg_search tool, but NO
specialized SCA tools. You must implement the entire attack pipeline yourself
(waveform inspection, alignment, CPA, key search, encrypt/decrypt verification)
in Python with numpy/scipy/sklearn/pycryptodome etc.

**[Session Directory]**
All files for this session are stored in: ..\logs\exp_knowledge_only\AES-STM32F103_DeepSeek-V3.2_DKG_20260515_002327_643
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp_knowledge_only\AES-STM32F103_DeepSeek-V3.2_DKG_20260515_002327_643/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 13,192→575

**🤖 LLM:** 我来帮您对STM32F103 MCU软件实现的AES进行CPA密钥恢复。首先，让我加载数据并检查波形特征。

**🔧 → `python_jupyter`**

<details><summary>Code (1270 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt
import os

# 加载数据
plain_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy'
cipher_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy'
wave_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy'

print("检查文件是否存在:")
print(f"明文文件: {os.path.exists(plain_path)}")
print(f"密文文件: {os.path.exists(cipher_path)}")
print(f"波形文件: {os.path.exists(wave_path)}")

# 加载数据
plaintexts = np.load(plain_path)
ciphertexts = np.load(cipher_path)
traces = np.load(wave_path)

print(f"\n数据形状:")
print(f"明文: {plaintexts.shape}")
print(f"密文: {ciphertexts.shape}")
print(f"波形: {traces.shape}")

# 检查数据类型
print(f"\n数据类型:")
print(f"明文: {plaintexts.dtype}")
print(f"密文: {ciphertexts.dtype}")
print(f"波形: {traces.dtype}")

# 查看前几个明文和密文
print(f"\n前3个明文 (十六进制):")
for i in range(min(3, len(plaintexts))):
    print(f"Trace {i}: {plaintexts[i].tobytes().hex()}")
    
print(f"\n前3个密文 (十六进制):")
for i in range(min(3, len(ciphertexts))):
    print(f"Trace {i}: {ciphertexts[i].tobytes().hex()}")
```
</details>

**📋 ← `python_jupyter`:** `检查文件是否存在:
明文文件: True
密文文件: True
波形文件: True

数据形状:
明文: (250, 16)
密文: (250, 16)
波形: (250, 1500)

数据类型:
明文: uint8
密文: uint8
波形: float32

前3个明文 (十六进制):
Trace 0: 33f25e5f412260df3ad3d47477f4ce89
Trace 1: 381e684af2267f5b549e6d7fb8bf9bc5
Trace 2: 5a29fb3a6236665e5d1ac5c49f435faa

前3个密文 (十六进制):
Trace 0: 17eaf0dcb9e3bc6f7a83d9f769bfc973
Trace 1: 354b46dbc4f91aa4fb2eba84e101a252
Trace 2: 11b42377f7520e3e18aa8368d6c85599`


---

### Round 2 | tokens: 14,021→846

**🤖 LLM:** 很好！我们有250条轨迹，每条1500个采样点，明文和密文都是16字节（128位）。现在让我检查波形的基本特征：

**🔧 → `python_jupyter`**

<details><summary>Code (2051 chars)</summary>

```python
# 检查波形特征
print("波形统计信息:")
print(f"最小值: {traces.min():.4f}")
print(f"最大值: {traces.max():.4f}")
print(f"平均值: {traces.mean():.4f}")
print(f"标准差: {traces.std():.4f}")

# 查看几条波形
plt.figure(figsize=(15, 10))

# 前5条波形
plt.subplot(3, 1, 1)
for i in range(min(5, len(traces))):
    plt.plot(traces[i], alpha=0.7, label=f'Trace {i}')
plt.title('前5条原始波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)

# 平均波形
plt.subplot(3, 1, 2)
mean_trace = traces.mean(axis=0)
std_trace = traces.std(axis=0)
plt.plot(mean_trace, label='平均波形')
plt.fill_between(range(len(mean_trace)), mean_trace - std_trace, mean_trace + std_trace, alpha=0.3, label='±1标准差')
plt.title('平均波形 ± 标准差')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)

# 方差分析 - 寻找加密区域
plt.subplot(3, 1, 3)
variance = traces.var(axis=0)
plt.plot(variance, label='方差')
plt.title('波形方差 (用于定位加密区域)')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# 找出方差最大的区域
print(f"\n方差分析:")
print(f"最大方差: {variance.max():.6f} 在采样点 {variance.argmax()}")
print(f"平均方差: {variance.mean():.6f}")

# 找出方差超过平均方差2倍的区域
high_var_indices = np.where(variance > 2 * variance.mean())[0]
if len(high_var_indices) > 0:
    print(f"高方差区域 (方差 > 2倍平均值): {len(high_var_indices)} 个采样点")
    print(f"高方差区域范围: {high_var_indices[0]} - {high_var_indices[-1]}")
    
    # 检查是否有明显的加密模式
    if len(high_var_indices) > 100:  # 如果有足够长的高方差区域
        # 寻找可能的重复模式（AES轮操作）
        high_var_region = variance[high_var_indices[0]:high_var_indices[-1]+1]
        # 使用自相关检测重复模式
        autocorr = np.correlate(high_var_region, high_var_region, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        plt.figure(figsize=(12, 4))
        plt.plot(autocorr[:200])
        plt.title('高方差区域自相关 (检测重复模式)')
        plt.xlabel('滞后')
        plt.ylabel('自相关')
        plt.grid(True, alpha=0.3)
        plt.savefig('autocorrelation.png', dpi=150, bbox_inches='tight')
        plt.show()
```
</details>

**📋 ← `python_jupyter`:** `波形统计信息:
最小值: -342.5197
最大值: 90.5512
平均值: -131.3288
标准差: 61.4955

方差分析:
最大方差: 3632.295898 在采样点 1102
平均方差: 712.317810
高方差区域 (方差 > 2倍平均值): 133 个采样点
高方差区域范围: 105 - 1226`


---

### Round 3 | tokens: 14,978→2,834

**🤖 LLM:** 从波形分析可以看出：
1. 波形有明显的负偏置（平均值-131.33）
2. 方差分析显示高方差区域从采样点105到1226，这可能是加密操作区域
3. 最大方差在采样点1102

根据KG知识，对于STM32F103这样的32位MCU软件实现，我应该：
1. 使用S-box输出作为攻击点
2. 使用汉明重量(Hamming Weight)泄漏模型
3. 首先尝试直接CPA，如果不行再考虑对齐

让我先实现CPA攻击。根据KG中的诊断链，对于软件实现，我应该优先固定S-box_out + HW模型，除非有强证据表明需要切换目标。

**🔧 → `python_jupyter`**

<details><summary>Code (5214 chars)</summary>

```python
# 实现CPA攻击
from Crypto.Cipher import AES
import scipy.stats as stats

def hamming_weight(x):
    """计算字节的汉明重量"""
    return bin(x).count('1')

def sbox_output(plaintext_byte, key_byte):
    """计算AES S-box输出"""
    # AES S-box
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
    return sbox[plaintext_byte ^ key_byte]

def cpa_attack(traces, plaintexts, target_byte, time_window=None):
    """对指定字节进行CPA攻击"""
    n_traces = traces.shape[0]
    n_samples = traces.shape[1]
    
    if time_window is None:
        time_window = (0, n_samples)
    
    # 提取时间窗口内的轨迹
    start, end = time_window
    traces_window = traces[:, start:end]
    n_window_samples = traces_window.shape[1]
    
    # 为所有可能的密钥字节生成假设功耗
    hypothetical_power = np.zeros((256, n_traces), dtype=np.float32)
    
    for key_guess in range(256):
        for i in range(n_traces):
            # 计算S-box输出并转换为汉明重量
            sbox_out = sbox_output(plaintexts[i, target_byte], key_guess)
            hypothetical_power[key_guess, i] = hamming_weight(sbox_out)
    
    # 计算相关性
    correlations = np.zeros((256, n_window_samples), dtype=np.float32)
    
    for key_guess in range(256):
        for sample in range(n_window_samples):
            corr, _ = stats.pearsonr(hypothetical_power[key_guess], traces_window[:, sample])
            correlations[key_guess, sample] = corr
    
    return correlations

# 首先在高方差区域进行CPA攻击
high_var_start = 105
high_var_end = 1226
print(f"在高方差区域进行CPA攻击: {high_var_start} - {high_var_end}")

# 测试第一个字节
print("\n对字节0进行CPA攻击...")
corr_byte0 = cpa_attack(traces, plaintexts, 0, (high_var_start, high_var_end))

# 找出每个密钥猜测的最大相关性
max_corrs = np.max(np.abs(corr_byte0), axis=1)
best_guess = np.argmax(max_corrs)
best_corr = max_corrs[best_guess]

print(f"字节0 - 最佳猜测: {best_guess:02x} (十进制: {best_guess})")
print(f"字节0 - 最大相关性: {best_corr:.4f}")

# 可视化相关性
plt.figure(figsize=(15, 8))

# 所有猜测的相关性热图
plt.subplot(2, 2, 1)
plt.imshow(np.abs(corr_byte0), aspect='auto', cmap='hot', 
           extent=[high_var_start, high_var_end, 0, 256])
plt.colorbar(label='|相关性|')
plt.title('字节0 - 所有密钥猜测的相关性热图')
plt.xlabel('采样点')
plt.ylabel('密钥猜测 (0-255)')

# 最佳猜测的相关性随时间变化
plt.subplot(2, 2, 2)
sample_indices = range(high_var_start, high_var_end)
plt.plot(sample_indices, corr_byte0[best_guess], 'b-', label=f'最佳猜测 {best_guess:02x}')
plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
plt.title(f'字节0 - 最佳猜测 {best_guess:02x} 的相关性')
plt.xlabel('采样点')
plt.ylabel('相关性')
plt.legend()
plt.grid(True, alpha=0.3)

# 所有猜测的最大相关性
plt.subplot(2, 2, 3)
plt.bar(range(256), max_corrs, alpha=0.7)
plt.bar(best_guess, max_corrs[best_guess], color='red', alpha=0.8, label=f'最佳: {best_guess:02x}')
plt.title('字节0 - 所有密钥猜测的最大相关性')
plt.xlabel('密钥猜测')
plt.ylabel('最大|相关性|')
plt.legend()
plt.grid(True, alpha=0.3)

# 相关性分布
plt.subplot(2, 2, 4)
plt.hist(max_corrs, bins=30, alpha=0.7, edgecolor='black')
plt.axvline(x=best_corr, color='red', linestyle='--', label=f'最佳: {best_corr:.4f}')
plt.title('字节0 - 最大相关性分布')
plt.xlabel('最大|相关性|')
plt.ylabel('频数')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('cpa_byte0_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# 检查最佳猜测是否明显优于其他猜测
sorted_corrs = np.sort(max_corrs)[::-1]
gap = sorted_corrs[0] - sorted_corrs[1]
gap_pct = (gap / sorted_corrs[0]) * 100 if sorted_corrs[0] != 0 else 0

print(f"\n字节0分析:")
print(f"最佳相关性: {sorted_corrs[0]:.4f}")
print(f"次佳相关性: {sorted_corrs[1]:.4f}")
print(f"差距: {gap:.4f}")
print(f"差距百分比: {gap_pct:.1f}%")

if gap_pct > 20:  # 根据KG经验，差距大于20%通常表示高置信度
    print("✓ 高置信度猜测")
else:
    print("⚠ 置信度较低，可能需要进一步分析")
```
</details>

**📋 ← `python_jupyter`:** `在高方差区域进行CPA攻击: 105 - 1226

对字节0进行CPA攻击...
字节0 - 最佳猜测: 11 (十进制: 17)
字节0 - 最大相关性: 0.3251

字节0分析:
最佳相关性: 0.3251
次佳相关性: 0.2782
差距: 0.0469
差距百分比: 14.4%
⚠ 置信度较低，可能需要进一步分析`


---

### Round 4 | tokens: 17,926→1,462

**🤖 LLM:** 第一个字节的CPA结果显示相关性较低（0.325），差距百分比只有14.4%。根据KG知识，对于软件实现，我应该首先尝试优化对齐和选择更好的时间窗口，而不是立即切换攻击目标。

让我先检查是否需要对齐。根据KG中的"Software implementation: variance-first ROI exploration before alignment"策略，我应该先进行方差分析来定位加密区域。

**🔧 → `python_jupyter`**

<details><summary>Code (3865 chars)</summary>

```python
# 更精细的方差分析来定位加密区域
# 使用滑动窗口计算方差
window_size = 20
variance_sliding = np.zeros(traces.shape[1] - window_size + 1)

for i in range(len(variance_sliding)):
    variance_sliding[i] = traces[:, i:i+window_size].var()

# 找出方差峰值
peak_indices = []
for i in range(1, len(variance_sliding)-1):
    if variance_sliding[i] > variance_sliding[i-1] and variance_sliding[i] > variance_sliding[i+1]:
        if variance_sliding[i] > 2 * variance_sliding.mean():
            peak_indices.append(i)

print(f"找到 {len(peak_indices)} 个显著方差峰值")
if peak_indices:
    print(f"峰值位置: {peak_indices[:10]}...")  # 只显示前10个

# 可视化
plt.figure(figsize=(15, 10))

# 原始方差
plt.subplot(3, 1, 1)
plt.plot(variance, 'b-', alpha=0.7, label='原始方差')
plt.axhline(y=2*variance.mean(), color='r', linestyle='--', alpha=0.5, label='2倍平均方差')
plt.fill_between(range(len(variance)), 0, variance, where=(variance > 2*variance.mean()), 
                 color='red', alpha=0.3, label='高方差区域')
plt.title('原始方差分析')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.legend()
plt.grid(True, alpha=0.3)

# 滑动窗口方差
plt.subplot(3, 1, 2)
plt.plot(range(window_size//2, len(variance_sliding) + window_size//2), variance_sliding, 'g-', alpha=0.7, label='滑动窗口方差')
plt.axhline(y=2*variance_sliding.mean(), color='r', linestyle='--', alpha=0.5, label='2倍平均方差')
if peak_indices:
    plt.scatter([idx + window_size//2 for idx in peak_indices], 
                variance_sliding[peak_indices], color='red', s=20, label='峰值')
plt.title(f'滑动窗口方差 (窗口大小={window_size})')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.legend()
plt.grid(True, alpha=0.3)

# 平均波形与方差叠加
plt.subplot(3, 1, 3)
ax1 = plt.gca()
ax1.plot(mean_trace, 'b-', alpha=0.7, label='平均波形')
ax1.set_xlabel('采样点')
ax1.set_ylabel('波形幅值', color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.plot(variance, 'r-', alpha=0.5, label='方差')
ax2.set_ylabel('方差', color='r')
ax2.tick_params(axis='y', labelcolor='r')
ax2.axhline(y=2*variance.mean(), color='r', linestyle='--', alpha=0.3)

plt.title('平均波形与方差叠加')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('variance_detailed.png', dpi=150, bbox_inches='tight')
plt.show()

# 基于方差峰值选择更精确的时间窗口
if peak_indices:
    # 选择最显著的几个峰值
    peak_values = variance_sliding[peak_indices]
    significant_peaks = [peak_indices[i] for i in np.argsort(peak_values)[-5:]]  # 取最大的5个峰值
    significant_peaks.sort()
    
    print(f"\n最显著的5个方差峰值位置: {significant_peaks}")
    
    # 在这些峰值附近选择时间窗口
    attack_windows = []
    for peak in significant_peaks:
        start = max(0, peak - 10)
        end = min(len(variance_sliding), peak + 10)
        attack_windows.append((start, end))
    
    print(f"建议的攻击时间窗口: {attack_windows}")
    
    # 在这些窗口中进行CPA测试
    test_results = []
    for window_idx, (start, end) in enumerate(attack_windows[:3]):  # 只测试前3个窗口
        print(f"\n测试窗口 {window_idx+1}: {start}-{end}")
        corr_test = cpa_attack(traces, plaintexts, 0, (start, end))
        max_corrs_test = np.max(np.abs(corr_test), axis=1)
        best_guess_test = np.argmax(max_corrs_test)
        best_corr_test = max_corrs_test[best_guess_test]
        
        sorted_corrs_test = np.sort(max_corrs_test)[::-1]
        gap_test = sorted_corrs_test[0] - sorted_corrs_test[1]
        gap_pct_test = (gap_test / sorted_corrs_test[0]) * 100 if sorted_corrs_test[0] != 0 else 0
        
        test_results.append({
            'window': (start, end),
            'best_guess': best_guess_test,
            'best_corr': best_corr_test,
            'gap_pct': gap_pct_test
        })
        
        print(f"  最佳猜测: {best_guess_test:02x}, 相关性: {best_corr_test:.4f}, 差距百分比: {gap_pct_test:.1f}%")
    
    # 选择最佳窗口
    best_window_idx = np.argmax([r['gap_pct'] for r in test_results])
    best_window = test_results[best_window_idx]['window']
    print(f"\n最佳攻击窗口: {best_window} (差距百分比: {test_results[best_window_idx]['gap_pct']:.1f}%)")
```
</details>

**📋 ← `python_jupyter`:** `找到 6 个显著方差峰值
峰值位置: [113, 396, 543, 1054, 1092, 1142]...

最显著的5个方差峰值位置: [396, 543, 1054, 1092, 1142]
建议的攻击时间窗口: [(386, 406), (533, 553), (1044, 1064), (1082, 1102), (1132, 1152)]

测试窗口 1: 386-406
  最佳猜测: 74, 相关性: 0.2357, 差距百分比: 7.0%

测试窗口 2: 533-553
  最佳猜测: 49, 相关性: 0.1933, 差距百分比: 5.4%

测试窗口 3: 1044-1064
  最佳猜测: ae, 相关性: 0.2288, 差距百分比: 1.9%

最佳攻击窗口: (386, 406) (差距百分比: 7.0%)`


---

### Round 5 | tokens: 19,631→106

**🤖 LLM:** 方差分析显示有几个明显的峰值，但测试窗口的相关性仍然较低。根据KG知识，对于STM32F103这样的32位MCU，可能需要考虑预充电总线的影响。让我搜索一下相关的知识：

**🔧 → `kg_search`** `{
  "keywords": [
    "STM32F103",
    "precharged bus",
    "Hamming Weight",
    "microcontroller",
    "CPA"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (25476 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (5): STM32F103, precharged bus, Hamming Weight, microcontroller, CPA

**Summary**: 23 upper entities, 15 relationships, 8 diagnostic chains, 9 strategies


## 1. Upper Layer Entities (23)


### DeviceClass (8)

- **32-bit STM microcontroller** — category=MCU, bus_width=32
- **8-bit AVR microcontroller** — category=MCU, bus_width=8
- **8-bit Atmel AVR microcontroller** — category=MCU, bus_width=8
- **8-bit Microcontroller** — category=MCU, bus_width=8
- **8-bit microcontroller** — category=MCU, bus_width=8
- **8-bit microcontroller (ASCAD dataset)** — category=MCU
- **8051 compatible microcontroller** — implementation_type=software, category=MCU
- **8051 microcontroller** — category=MCU

### LeakageModel (5)

- **Hamming Weight** — requirements=software implementation
- **Hamming Weight (bit-based)** — requirements=bit-based
- **Hamming Weight of transitions**
- **Hamming weight**
- **Hamming weight of fused features**

### Pipeline (3)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing
...(truncated)
```
</details>


---

### Round 6 | tokens: 26,243→1,276

**🤖 LLM:** 根据KG搜索结果，我看到了几个关键点：
1. 对于微控制器，特别是使用预充电总线的，功耗可能与汉明重量成反比
2. 诊断链指出：对于攻击微控制器上的S-box输出，如果使用预充电总线，功耗可能与汉明重量成反比
3. 策略强调：对于软件实现，不要轻易切换泄漏目标，优先固定S-box_out + HW模型

让我尝试调整泄漏模型，考虑预充电总线的影响：

**🔧 → `python_jupyter`**

<details><summary>Code (3598 chars)</summary>

```python
# 尝试不同的泄漏模型
def cpa_attack_with_model(traces, plaintexts, target_byte, time_window=None, model='hw', inverse=False):
    """使用不同泄漏模型的CPA攻击"""
    n_traces = traces.shape[0]
    
    if time_window is None:
        time_window = (0, traces.shape[1])
    
    start, end = time_window
    traces_window = traces[:, start:end]
    n_window_samples = traces_window.shape[1]
    
    # 为所有可能的密钥字节生成假设功耗
    hypothetical_power = np.zeros((256, n_traces), dtype=np.float32)
    
    for key_guess in range(256):
        for i in range(n_traces):
            sbox_out = sbox_output(plaintexts[i, target_byte], key_guess)
            
            if model == 'hw':
                # 汉明重量模型
                power = hamming_weight(sbox_out)
            elif model == 'bit':
                # 比特模型（特定比特）
                power = (sbox_out >> 0) & 1  # LSB
            elif model == 'identity':
                # 恒等模型
                power = sbox_out
            elif model == 'hw_inverse':
                # 考虑预充电总线的反相关模型
                power = 8 - hamming_weight(sbox_out)  # 预充电总线：汉明重量越低，功耗越高
            else:
                power = hamming_weight(sbox_out)
            
            hypothetical_power[key_guess, i] = power
    
    # 计算相关性
    correlations = np.zeros((256, n_window_samples), dtype=np.float32)
    
    for key_guess in range(256):
        for sample in range(n_window_samples):
            corr, _ = stats.pearsonr(hypothetical_power[key_guess], traces_window[:, sample])
            correlations[key_guess, sample] = corr
    
    return correlations

# 测试不同的泄漏模型
test_models = ['hw', 'hw_inverse', 'bit', 'identity']
test_window = (105, 1226)  # 使用整个高方差区域

model_results = []

for model in test_models:
    print(f"\n测试泄漏模型: {model}")
    corr_model = cpa_attack_with_model(traces, plaintexts, 0, test_window, model=model)
    max_corrs_model = np.max(np.abs(corr_model), axis=1)
    best_guess_model = np.argmax(max_corrs_model)
    best_corr_model = max_corrs_model[best_guess_model]
    
    sorted_corrs_model = np.sort(max_corrs_model)[::-1]
    gap_model = sorted_corrs_model[0] - sorted_corrs_model[1]
    gap_pct_model = (gap_model / sorted_corrs_model[0]) * 100 if sorted_corrs_model[0] != 0 else 0
    
    model_results.append({
        'model': model,
        'best_guess': best_guess_model,
        'best_corr': best_corr_model,
        'gap_pct': gap_pct_model
    })
    
    print(f"  最佳猜测: {best_guess_model:02x}, 相关性: {best_corr_model:.4f}, 差距百分比: {gap_pct_model:.1f}%")

# 可视化比较
plt.figure(figsize=(15, 10))

for idx, result in enumerate(model_results):
    plt.subplot(2, 2, idx+1)
    
    # 重新计算该模型的相关性用于可视化
    corr_viz = cpa_attack_with_model(traces, plaintexts, 0, test_window, model=result['model'])
    max_corrs_viz = np.max(np.abs(corr_viz), axis=1)
    
    plt.bar(range(256), max_corrs_viz, alpha=0.7)
    plt.bar(result['best_guess'], max_corrs_viz[result['best_guess']], 
            color='red', alpha=0.8, label=f'最佳: {result["best_guess"]:02x}')
    
    plt.title(f'模型: {result["model"]}\n最佳: {result["best_guess"]:02x}, 相关性: {result["best_corr"]:.4f}')
    plt.xlabel('密钥猜测')
    plt.ylabel('最大|相关性|')
    plt.legend()
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('model_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

# 选择最佳模型
best_model_idx = np.argmax([r['gap_pct'] for r in model_results])
best_model = model_results[best_model_idx]
print(f"\n最佳泄漏模型: {best_model['model']}")
print(f"最佳猜测: {best_model['best_guess']:02x}")
print(f"最大相关性: {best_model['best_corr']:.4f}")
print(f"差距百分比: {best_model['gap_pct']:.1f}%")
```
</details>

**📋 ← `python_jupyter`:** `测试泄漏模型: hw
  最佳猜测: 11, 相关性: 0.3251, 差距百分比: 14.4%

测试泄漏模型: hw_inverse
  最佳猜测: 11, 相关性: 0.3251, 差距百分比: 14.4%

测试泄漏模型: bit
  最佳猜测: 76, 相关性: 0.2847, 差距百分比: 3.1%

测试泄漏模型: identity
  最佳猜测: 8e, 相关性: 0.2866, 差距百分比: 3.1%

最佳泄漏模型: hw
最佳猜测: 11
最大相关性: 0.3251
差距百分比: 14.4%`


---

### Round 7 | tokens: 27,695→805

**🤖 LLM:** 有趣的是，`hw`和`hw_inverse`模型给出了相同的结果（因为相关性是绝对值）。这表明相关性可能是负的。让我检查实际的相关性符号：

**🔧 → `python_jupyter`**

<details><summary>Code (1804 chars)</summary>

```python
# 检查相关性的符号
corr_hw = cpa_attack_with_model(traces, plaintexts, 0, test_window, model='hw')
corr_hw_inverse = cpa_attack_with_model(traces, plaintexts, 0, test_window, model='hw_inverse')

# 找出最佳猜测的实际相关性（不是绝对值）
best_guess = 0x11  # 从之前的结果
best_corr_hw = corr_hw[best_guess, :]
best_corr_hw_inverse = corr_hw_inverse[best_guess, :]

# 找出最大相关性的位置
max_idx_hw = np.argmax(np.abs(best_corr_hw))
max_idx_hw_inverse = np.argmax(np.abs(best_corr_hw_inverse))

print(f"HW模型 - 最佳猜测 {best_guess:02x}:")
print(f"  最大相关性位置: {max_idx_hw}")
print(f"  相关性值: {best_corr_hw[max_idx_hw]:.4f}")
print(f"  绝对值: {np.abs(best_corr_hw[max_idx_hw]):.4f}")

print(f"\nHW_INVERSE模型 - 最佳猜测 {best_guess:02x}:")
print(f"  最大相关性位置: {max_idx_hw_inverse}")
print(f"  相关性值: {best_corr_hw_inverse[max_idx_hw_inverse]:.4f}")
print(f"  绝对值: {np.abs(best_corr_hw_inverse[max_idx_hw_inverse]):.4f}")

# 检查相关性的符号
if best_corr_hw[max_idx_hw] < 0:
    print(f"\n⚠ HW模型显示负相关性 ({best_corr_hw[max_idx_hw]:.4f})")
    print("这可能表明预充电总线效应：汉明重量越高，功耗越低")
else:
    print(f"\n✓ HW模型显示正相关性 ({best_corr_hw[max_idx_hw]:.4f})")

# 可视化实际相关性（不是绝对值）
plt.figure(figsize=(15, 6))

plt.subplot(1, 2, 1)
plt.plot(range(test_window[0], test_window[1]), best_corr_hw, 'b-', label='HW模型')
plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
plt.title(f'HW模型 - 猜测 {best_guess:02x} 的实际相关性')
plt.xlabel('采样点')
plt.ylabel('相关性')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(range(test_window[0], test_window[1]), best_corr_hw_inverse, 'r-', label='HW_INVERSE模型')
plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
plt.title(f'HW_INVERSE模型 - 猜测 {best_guess:02x} 的实际相关性')
plt.xlabel('采样点')
plt.ylabel('相关性')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('correlation_sign.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `HW模型 - 最佳猜测 11:
  最大相关性位置: 481
  相关性值: -0.3251
  绝对值: 0.3251

HW_INVERSE模型 - 最佳猜测 11:
  最大相关性位置: 481
  相关性值: 0.3251
  绝对值: 0.3251

⚠ HW模型显示负相关性 (-0.3251)
这可能表明预充电总线效应：汉明重量越高，功耗越低`


---

### Round 8 | tokens: 28,618→1,411

**🤖 LLM:** 很好！这证实了我的怀疑：HW模型显示负相关性，这意味着功耗与汉明重量成反比。这是预充电总线的典型特征。现在我应该使用`hw_inverse`模型（或者在使用HW模型时考虑负相关性）。

根据KG策略，我应该继续使用S-box输出作为攻击点，但考虑预充电总线效应。让我对所有16个字节进行完整的CPA攻击：

**🔧 → `python_jupyter`**

<details><summary>Code (3747 chars)</summary>

```python
# 对所有16个字节进行完整的CPA攻击
def full_cpa_attack(traces, plaintexts, time_window=None, model='hw_inverse'):
    """对所有16个字节进行CPA攻击"""
    n_bytes = 16
    key_candidates = np.zeros(n_bytes, dtype=np.uint8)
    correlations = np.zeros(n_bytes, dtype=np.float32)
    gap_percentages = np.zeros(n_bytes, dtype=np.float32)
    
    if time_window is None:
        time_window = (0, traces.shape[1])
    
    for byte_idx in range(n_bytes):
        print(f"攻击字节 {byte_idx}...", end=' ')
        
        corr_byte = cpa_attack_with_model(traces, plaintexts, byte_idx, time_window, model=model)
        max_corrs = np.max(np.abs(corr_byte), axis=1)
        
        # 找出最佳猜测
        best_guess = np.argmax(max_corrs)
        best_corr = max_corrs[best_guess]
        
        # 计算差距百分比
        sorted_corrs = np.sort(max_corrs)[::-1]
        if len(sorted_corrs) > 1 and sorted_corrs[0] != 0:
            gap = sorted_corrs[0] - sorted_corrs[1]
            gap_pct = (gap / sorted_corrs[0]) * 100
        else:
            gap_pct = 0
        
        key_candidates[byte_idx] = best_guess
        correlations[byte_idx] = best_corr
        gap_percentages[byte_idx] = gap_pct
        
        print(f"猜测: {best_guess:02x}, 相关性: {best_corr:.4f}, 差距: {gap_pct:.1f}%")
    
    return key_candidates, correlations, gap_percentages

# 使用最佳时间窗口进行攻击
# 基于之前的分析，使用整个高方差区域
print("对所有16个字节进行CPA攻击 (使用hw_inverse模型):")
key_candidates, correlations, gap_percentages = full_cpa_attack(traces, plaintexts, test_window, model='hw_inverse')

print(f"\n恢复的密钥候选 (十六进制): {key_candidates.tobytes().hex()}")
print(f"平均相关性: {correlations.mean():.4f}")
print(f"平均差距百分比: {gap_percentages.mean():.1f}%")

# 统计高置信度字节数
high_confidence_threshold = 20  # 差距百分比大于20%视为高置信度
high_confidence_count = np.sum(gap_percentages > high_confidence_threshold)
print(f"\n高置信度字节数 (差距 > {high_confidence_threshold}%): {high_confidence_count}/16")

# 可视化结果
plt.figure(figsize=(15, 10))

# 字节相关性
plt.subplot(2, 2, 1)
bars = plt.bar(range(16), correlations, alpha=0.7)
# 根据置信度着色
for i, (corr, gap) in enumerate(zip(correlations, gap_percentages)):
    if gap > high_confidence_threshold:
        bars[i].set_color('green')
    elif gap > 10:
        bars[i].set_color('orange')
    else:
        bars[i].set_color('red')
plt.axhline(y=correlations.mean(), color='k', linestyle='--', alpha=0.5, label=f'平均: {correlations.mean():.3f}')
plt.title('各字节最大相关性')
plt.xlabel('字节索引')
plt.ylabel('最大|相关性|')
plt.legend()
plt.grid(True, alpha=0.3)

# 字节差距百分比
plt.subplot(2, 2, 2)
bars = plt.bar(range(16), gap_percentages, alpha=0.7)
plt.axhline(y=high_confidence_threshold, color='r', linestyle='--', alpha=0.5, label=f'高置信度阈值: {high_confidence_threshold}%')
plt.axhline(y=gap_percentages.mean(), color='k', linestyle='--', alpha=0.5, label=f'平均: {gap_percentages.mean():.1f}%')
plt.title('各字节差距百分比')
plt.xlabel('字节索引')
plt.ylabel('差距百分比 (%)')
plt.legend()
plt.grid(True, alpha=0.3)

# 密钥字节值
plt.subplot(2, 2, 3)
plt.bar(range(16), key_candidates, alpha=0.7)
plt.title('恢复的密钥字节值')
plt.xlabel('字节索引')
plt.ylabel('密钥字节值')
plt.grid(True, alpha=0.3)

# 相关性分布
plt.subplot(2, 2, 4)
plt.hist(correlations, bins=20, alpha=0.7, edgecolor='black')
plt.axvline(x=correlations.mean(), color='r', linestyle='--', label=f'平均: {correlations.mean():.3f}')
plt.title('相关性分布')
plt.xlabel('最大|相关性|')
plt.ylabel('频数')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('full_cpa_results.png', dpi=150, bbox_inches='tight')
plt.show()

# 保存结果
np.save('key_candidates.npy', key_candidates)
np.save('correlations.npy', correlations)
np.save('gap_percentages.npy', gap_percentages)

print(f"\n结果已保存到文件:")
print(f"  key_candidates.npy - 密钥候选")
print(f"  correlations.npy - 各字节相关性")
print(f"  gap_percentages.npy - 各字节差距百分比")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (893 chars)</summary>

```
对所有16个字节进行CPA攻击 (使用hw_inverse模型):
攻击字节 0... 猜测: 11, 相关性: 0.3251, 差距: 14.4%
攻击字节 1... 猜测: ec, 相关性: 0.2679, 差距: 1.3%
攻击字节 2... 猜测: d6, 相关性: 0.3516, 差距: 21.1%
攻击字节 3... 猜测: 44, 相关性: 0.3574, 差距: 19.3%
攻击字节 4... 猜测: 35, 相关性: 0.2881, 差距: 8.9%
攻击字节 5... 猜测: 66, 相关性: 0.3694, 差距: 23.8%
攻击字节 6... 猜测: 60, 相关性: 0.2823, 差距: 0.3%
攻击字节 7... 猜测: 0d, 相关性: 0.2767, 差距: 6.9%
攻击字节 8... 猜测: 53, 相关性: 0.2897, 差距: 0.7%
攻击字节 9... 猜测: 39, 相关性: 0.2711, 差距: 2.2%
攻击字节 10... 猜测: bb, 相关性: 0.3862, 差距: 34.3%
攻击字节 11... 猜测: cc, 相关性: 0.3413, 差距: 11.6%
攻击字节 12... 猜测: 4e, 相关性: 0.2700, 差距: 1.1%
攻击字节 13... 猜测: ee, 相关性: 0.3330, 差距: 21.0%
攻击字节 14... 猜测: ff, 相关性: 0.3131, 差距: 17.8%
攻击字节 15... 猜测: 00, 相关性: 0.3369, 差距: 17.4%

恢复的密钥候选 (十六进制): 11ecd6443566600d5339bbcc4eeeff00
平均相关性: 0.3162
平均差距百分比: 12.6%

高置信度字节数 (差距 > 20%): 4/16

结果已保存到文件:
  key_candidates.npy - 密钥候选
  correlations.npy - 各字节相关性
  gap_percentages.npy - 各字节差距百分比
```
</details>


---

### Round 9 | tokens: 30,605→142

**🤖 LLM:** CPA攻击完成了，但只有4/16个字节有高置信度（差距>20%）。根据KG策略，当高置信度字节数较低时，我应该首先尝试优化对齐和选择更好的时间窗口，而不是切换攻击目标。

让我尝试使用静态对齐来改善结果。根据KG中的"Static alignment default parameter bundle for contact smartcard AES"策略，我应该使用适当的参数：

**🔧 → `kg_search`** `{
  "keywords": [
    "static alignment",
    "STM32",
    "AES",
    "parameters",
    "max_shift"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (39689 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (5): static alignment, STM32, AES, parameters, max_shift

**Summary**: 15 upper entities, 15 relationships, 22 diagnostic chains, 15 strategies


## 1. Upper Layer Entities (15)


### Algorithm (1)

- **AES** — num_rounds=['10', '14'], encryption_mode=['CBC', 'ECB'], key_length=['128', '256']

### DeviceClass (8)

- **STM32** — category=MCU, bus_width=32
- **STM32F0** — category=MCU, bus_width=32
- **STM32F0DISCOVERY (Cortex-M0)** — category=MCU, bus_width=32
- **STM32F415** — implementation_type=hardware, category=MCU, bus_width=32
- **STM32F429** — category=MCU, bus_width=32
- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated

### Pipeline (4)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA
...(truncated)
```
</details>


---

### Round 10 | tokens: 41,197→1,812

**🤖 LLM:** 根据KG搜索结果，我看到了几个关键策略：
1. "Static alignment default parameter bundle for contact smartcard AES"：length=100, max_shift=400, threshold=85, ref_trace=1
2. "alignment max_shift should start large (300+), not default to small"：对于MCU，初始max_shift至少150-200
3. "Software implementation: variance-first ROI exploration before alignment"：对于软件实现，先进行方差分析定位加密区域

让我实现静态对齐：

**🔧 → `python_jupyter`**

<details><summary>Code (5136 chars)</summary>

```python
# 实现静态对齐
def static_align(traces, ref_idx=1, length=100, max_shift=200, threshold=0.85):
    """静态对齐实现"""
    n_traces, n_samples = traces.shape
    
    # 选择参考轨迹
    ref_trace = traces[ref_idx]
    
    # 选择参考窗口 - 基于方差分析选择高方差区域
    # 使用滑动窗口方差找到最佳对齐区域
    window_size = length
    variance_sliding = np.zeros(n_samples - window_size + 1)
    
    for i in range(len(variance_sliding)):
        variance_sliding[i] = traces[:, i:i+window_size].var()
    
    # 选择方差最大的区域作为参考窗口
    ref_start = np.argmax(variance_sliding)
    ref_end = ref_start + window_size
    ref_window = ref_trace[ref_start:ref_end]
    
    print(f"参考窗口: {ref_start}-{ref_end} (长度: {window_size})")
    print(f"参考窗口方差: {variance_sliding[ref_start]:.2f}")
    
    # 对齐所有轨迹
    aligned_traces = np.zeros_like(traces)
    shifts = np.zeros(n_traces, dtype=int)
    correlations = np.zeros(n_traces)
    accepted = np.zeros(n_traces, dtype=bool)
    
    for i in range(n_traces):
        if i == ref_idx:
            # 参考轨迹不需要对齐
            aligned_traces[i] = traces[i]
            shifts[i] = 0
            correlations[i] = 1.0
            accepted[i] = True
            continue
        
        trace = traces[i]
        best_corr = -1
        best_shift = 0
        
        # 在最大偏移范围内搜索最佳对齐
        for shift in range(-max_shift, max_shift + 1):
            start = ref_start + shift
            end = ref_end + shift
            
            if start < 0 or end > n_samples:
                continue
            
            window = trace[start:end]
            
            # 计算相关性
            corr = np.corrcoef(ref_window, window)[0, 1]
            if np.isnan(corr):
                corr = 0
            
            if corr > best_corr:
                best_corr = corr
                best_shift = shift
        
        # 检查是否接受该对齐
        if best_corr >= threshold:
            # 应用偏移
            if best_shift >= 0:
                aligned_traces[i, :n_samples-best_shift] = traces[i, best_shift:]
                aligned_traces[i, n_samples-best_shift:] = traces[i, -1]  # 填充边界
            else:
                aligned_traces[i, -best_shift:] = traces[i, :n_samples+best_shift]
                aligned_traces[i, :-best_shift] = traces[i, 0]  # 填充边界
            
            shifts[i] = best_shift
            correlations[i] = best_corr
            accepted[i] = True
        else:
            # 对齐失败，使用原始轨迹
            aligned_traces[i] = traces[i]
            shifts[i] = 0
            correlations[i] = best_corr
            accepted[i] = False
    
    acceptance_rate = np.mean(accepted) * 100
    avg_correlation = np.mean(correlations[accepted]) if np.any(accepted) else 0
    
    print(f"\n对齐统计:")
    print(f"接受率: {acceptance_rate:.1f}% ({np.sum(accepted)}/{n_traces})")
    print(f"平均相关性: {avg_correlation:.3f}")
    print(f"偏移范围: {shifts.min()} 到 {shifts.max()}")
    
    return aligned_traces, shifts, correlations, accepted, ref_start, ref_end

# 使用KG推荐的参数进行对齐
print("进行静态对齐...")
aligned_traces, shifts, correlations, accepted, ref_start, ref_end = static_align(
    traces, ref_idx=1, length=100, max_shift=200, threshold=0.85
)

# 保存对齐后的轨迹
np.save('aligned_traces.npy', aligned_traces)
np.save('shifts.npy', shifts)
np.save('alignment_correlations.npy', correlations)
np.save('accepted_traces.npy', accepted)

print(f"\n对齐结果已保存到文件")

# 可视化对齐结果
plt.figure(figsize=(15, 10))

# 偏移分布
plt.subplot(2, 2, 1)
plt.hist(shifts[accepted], bins=30, alpha=0.7, edgecolor='black')
plt.title('接受轨迹的偏移分布')
plt.xlabel('偏移量')
plt.ylabel('频数')
plt.grid(True, alpha=0.3)

# 相关性分布
plt.subplot(2, 2, 2)
plt.hist(correlations[accepted], bins=30, alpha=0.7, edgecolor='black', label='接受')
if np.any(~accepted):
    plt.hist(correlations[~accepted], bins=30, alpha=0.7, edgecolor='black', label='拒绝')
plt.axvline(x=0.85, color='r', linestyle='--', label='阈值 (0.85)')
plt.title('对齐相关性分布')
plt.xlabel('相关性')
plt.ylabel('频数')
plt.legend()
plt.grid(True, alpha=0.3)

# 对齐前后的平均波形对比
plt.subplot(2, 2, 3)
plt.plot(traces.mean(axis=0), 'b-', alpha=0.7, label='原始平均')
plt.plot(aligned_traces.mean(axis=0), 'r-', alpha=0.7, label='对齐后平均')
plt.axvline(x=ref_start, color='g', linestyle='--', alpha=0.5, label='参考窗口开始')
plt.axvline(x=ref_end, color='g', linestyle='--', alpha=0.5, label='参考窗口结束')
plt.title('对齐前后平均波形对比')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)

# 参考窗口附近的轨迹
plt.subplot(2, 2, 4)
window_start = max(0, ref_start - 50)
window_end = min(traces.shape[1], ref_end + 50)

# 显示前10条接受轨迹
for i in range(min(10, len(traces))):
    if accepted[i]:
        plt.plot(range(window_start, window_end), 
                aligned_traces[i, window_start:window_end], 
                alpha=0.3, linewidth=0.5)
plt.plot(range(window_start, window_end), 
         aligned_traces.mean(axis=0)[window_start:window_end], 
         'k-', linewidth=2, label='平均')
plt.axvspan(ref_start, ref_end, alpha=0.2, color='green', label='参考窗口')
plt.title('参考窗口附近的轨迹 (前10条接受轨迹)')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('alignment_results.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `进行静态对齐...
参考窗口: 1053-1153 (长度: 100)
参考窗口方差: 4866.67

对齐统计:
接受率: 100.0% (250/250)
平均相关性: 0.984
偏移范围: -16 到 45

对齐结果已保存到文件`


---

### Round 11 | tokens: 43,095→1,344

**🤖 LLM:** 很好！对齐非常成功，接受率100%，平均相关性0.984。现在让我在对齐后的轨迹上进行CPA攻击：

**🔧 → `python_jupyter`**

<details><summary>Code (3461 chars)</summary>

```python
# 在对齐后的轨迹上进行CPA攻击
print("在对齐后的轨迹上进行CPA攻击...")

# 使用对齐后的轨迹
aligned_key_candidates, aligned_correlations, aligned_gap_percentages = full_cpa_attack(
    aligned_traces, plaintexts, test_window, model='hw_inverse'
)

print(f"\n对齐后恢复的密钥候选 (十六进制): {aligned_key_candidates.tobytes().hex()}")
print(f"对齐后平均相关性: {aligned_correlations.mean():.4f}")
print(f"对齐后平均差距百分比: {aligned_gap_percentages.mean():.1f}%")

# 统计高置信度字节数
high_confidence_threshold = 20
aligned_high_confidence_count = np.sum(aligned_gap_percentages > high_confidence_threshold)
print(f"\n对齐后高置信度字节数 (差距 > {high_confidence_threshold}%): {aligned_high_confidence_count}/16")

# 与对齐前的结果比较
print("\n=== 对齐前后对比 ===")
print(f"高置信度字节数: {high_confidence_count}/16 → {aligned_high_confidence_count}/16")
print(f"平均相关性: {correlations.mean():.4f} → {aligned_correlations.mean():.4f}")
print(f"平均差距百分比: {gap_percentages.mean():.1f}% → {aligned_gap_percentages.mean():.1f}%")

# 可视化对比
plt.figure(figsize=(15, 10))

# 相关性对比
plt.subplot(2, 2, 1)
x = np.arange(16)
width = 0.35
plt.bar(x - width/2, correlations, width, alpha=0.7, label='对齐前')
plt.bar(x + width/2, aligned_correlations, width, alpha=0.7, label='对齐后')
plt.axhline(y=correlations.mean(), color='b', linestyle='--', alpha=0.5, label=f'对齐前平均: {correlations.mean():.3f}')
plt.axhline(y=aligned_correlations.mean(), color='r', linestyle='--', alpha=0.5, label=f'对齐后平均: {aligned_correlations.mean():.3f}')
plt.title('对齐前后相关性对比')
plt.xlabel('字节索引')
plt.ylabel('最大|相关性|')
plt.legend()
plt.grid(True, alpha=0.3)

# 差距百分比对比
plt.subplot(2, 2, 2)
plt.bar(x - width/2, gap_percentages, width, alpha=0.7, label='对齐前')
plt.bar(x + width/2, aligned_gap_percentages, width, alpha=0.7, label='对齐后')
plt.axhline(y=high_confidence_threshold, color='k', linestyle='--', alpha=0.5, label=f'高置信度阈值: {high_confidence_threshold}%')
plt.axhline(y=gap_percentages.mean(), color='b', linestyle='--', alpha=0.5, label=f'对齐前平均: {gap_percentages.mean():.1f}%')
plt.axhline(y=aligned_gap_percentages.mean(), color='r', linestyle='--', alpha=0.5, label=f'对齐后平均: {aligned_gap_percentages.mean():.1f}%')
plt.title('对齐前后差距百分比对比')
plt.xlabel('字节索引')
plt.ylabel('差距百分比 (%)')
plt.legend()
plt.grid(True, alpha=0.3)

# 密钥字节值对比
plt.subplot(2, 2, 3)
plt.bar(x - width/2, key_candidates, width, alpha=0.7, label='对齐前')
plt.bar(x + width/2, aligned_key_candidates, width, alpha=0.7, label='对齐后')
plt.title('对齐前后密钥字节值对比')
plt.xlabel('字节索引')
plt.ylabel('密钥字节值')
plt.legend()
plt.grid(True, alpha=0.3)

# 高置信度字节数对比
plt.subplot(2, 2, 4)
categories = ['对齐前', '对齐后']
values = [high_confidence_count, aligned_high_confidence_count]
colors = ['red' if v < 8 else 'orange' if v < 13 else 'green' for v in values]
bars = plt.bar(categories, values, alpha=0.7, color=colors)
plt.axhline(y=8, color='r', linestyle='--', alpha=0.5, label='低置信度 (<8)')
plt.axhline(y=13, color='g', linestyle='--', alpha=0.5, label='高置信度 (≥13)')
plt.title('高置信度字节数对比')
plt.ylabel('高置信度字节数')
plt.ylim(0, 16)
for bar, value in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
             f'{value}/16', ha='center', va='bottom')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('alignment_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

# 保存对齐后的结果
np.save('aligned_key_candidates.npy', aligned_key_candidates)
np.save('aligned_correlations.npy', aligned_correlations)
np.save('aligned_gap_percentages.npy', aligned_gap_percentages)

print(f"\n对齐后结果已保存到文件")
```
</details>

**❌ ← `python_jupyter` Error:**

```
在对齐后的轨迹上进行CPA攻击...
攻击字节 0... 猜测: 11, 相关性: 0.4908, 差距: 44.3%
攻击字节 1... 猜测: 22, 相关性: 0.3759, 差距: 31.5%
攻击字节 2... 猜测: 33, 相关性: 0.3652, 差距: 23.5%
攻击字节 3... 猜测: 44, 相关性: 0.5018, 差距: 49.6%
攻击字节 4... 猜测: 55, 相关性: 0.3908, 差距: 21.8%
攻击字节 5... 猜测: 66, 相关性: 0.4973, 差距: 45.1%
攻击字节 6... 猜测: 77, 相关性: 0.4839, 差距: 44.3%
攻击字节 7... 猜测: 88, 相关性: 0.4265, 差距: 30.9%
攻击字节 8... 猜测: 99, 相关性: 0.3880, 差距: 26.4%
攻击字节 9... 猜测: aa, 相关性: 0.4608, 差距: 38.7%
攻击字节 10... 猜测: bb, 相关性: 0.4929, 差距: 41.8%
攻击字节 11... 猜测: cc, 相关性: 0.5043, 差距: 38.7%
攻击字节 12... 猜测: dd, 相关性: 0.3834, 差距: 24.8%
攻击字节 13... 猜测: ee, 相关性: 0.4572, 差距: 42.8%
攻击字节 14... 猜测: ff, 相关性: 0.4779, 差距: 40.0%
攻击字节 15... 猜测: 00, 相关性: 0.5093, 差距: 45.7%

对齐后恢复的密钥候选 (十六进制): 112233445566778899aabbccddeeff00
对齐后平均相关性: 0.4504
对齐后平均差距百分比: 36.9%

对齐后高置信度字节数 (差距 > 20%): 16/16

=== 对齐前后对比 ===
高置信度字节数: 4/16 → 16/16
平均相关性: 0.9837 → 0.4504
平均差距百分比: 12.6% → 36.9%

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mValueError[39m                                Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[70][39m[32m, line 31[39m
[32m     29[39m x = np.arange([32m16[39m)
[32m     30[39m width = [32m0.35[39m
[32m---> [39m[32m31[39m [43mplt[49m[43m.[49m[43mbar[49m[43m([49m[43mx[49m[43m [49m[43m-[49m[43m [49m[43mwidth[49m[43m/[49m[32;43m2[39;49m[43m,[49m[43m [49m[43mcorrelations[49m[43m,[49m[43m [49m[43mwidth[49m[43m,[49m[43m [49m[43malpha[49m[43m=[49m[32;43m0.7[39;49m[43m,[49m[43m [49m[43mlabel[49m[43m=[49m[33;43m'[39;49m[33;43m对齐前[39;49m[33;43m'[39;49m[43m)[49m
[32m     32[39m plt.bar(x + width/[32m2[39m, aligned_correlations, width, alpha=[32m0.7[39m, label=[33m'[39m[33m对齐后[39m[33m'[39m)
[32m     33[39m plt.axhline(y=correlations.mean(), color=[33m'[39m[33mb[39m[33m'[39m, linestyle=[33m'[39m[33m--[39m[33m'[39m, alpha=[32m0.5[39m, label=[33mf[39m[33m'[39m[33m对齐前平均: [39m[38;5;132;01m{[39;00mcorrelations.mean()[38;5;132;01m:[39;00m[33m.3f[39m[38;5;132;01m}[39;00m[33m'[39m)

[36mFile [39m[32mF:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\matplotlib\pyplot.py:2989[39m, in [36mbar[39m[34m(x, height, width, bottom, align, data, **kwargs)[39m
[32m   2978[39m [38;5;129m@_copy_docstring_and_deprecators[39m(Axes.bar)
[32m   2979[39m [38;5;28;01mdef[39;00m[38;5;250m [39m[34mbar[39m(
[32m   2980[39m     x: [38;5;28mfloat[39m | ArrayLike,
[32m   (...)[39m[32m   2987[39m     **kwargs,
[32m   2988[39m ) -> BarContainer:
[32m-> [39m[32m2989[39m     [38;5;28;01mreturn[39;00m [43mgca[49m[43m([49m[43m)[49m[43m.[49m[43mbar[49m[43m([49m
[32m   2990[39m [43m        [49m[43mx[49m[43m,[49m
[32m   2991[39m [43m        [49m[43mheight[49m[43m,[49m
[32m   2992[39m [43m        [49m[43mwidth[49m[43m=[49m[43mwidth[49m[43m,[49m
[32m   2993[39m [43m        [49m[43mbottom[49m[43m=[49m[43mbottom[49m[43m,[49m
[32m   2994[39m [43m        [49m[43malign[49m[43m=[49m[43malign[49m[43m,[49m
[32m   2995[39m [43m        [49m[43m*[49m[43m*[49m[43m([49m[43m{[49m[33;43m"[39;49m[33;43mdata[39;49m[33;43m"[39;49m[43m:[49m[43m [49m[43mdata[49m[43m}[49m[43m [49m[38;5;28;43;01mif[39;49;00m[43m [49m[43mdata[49m[43m [49m[38;5;129;43;01mis[39;49;00m[43m [49m[38;5;129;43;01mnot[39;49;00m[43m [49m[38;5;28;43;01mNone[39;49;00m[43m [49m[38;5;28;43;01melse[39;49;00m[43m [49m[43m{[49m[43m}[49m[43m)[49m[43m,[49m
[32m   2996[39m [43m        [49m[43m*[49m[43m*[49m[43mkwargs[49m[43m,[49m
[32m   2997[39m [43m    [49m[43m)[49m

[36mFile [39m[32mF:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\matplotlib\__init__.py:1524[39m, in [36m_preprocess_data.<locals>.inner[39m[34m(ax, data, *args, **kwargs)[39m
[32m   1521[39m [38;5;129m@functools[39m.wraps(func)
[32m   1522[39m [38;5;28;01mdef[39;00m[38;5;250m [39m[34minner[39m(ax, *args, data=[38;5;28;01mNone[39;00m, **kwargs):
[32m   1523[39m     [38;5;28;01mif[39;00m data [38;5;129;01mis[39;00m [38;5;28;01mNone[39;00m:
[32m-> [39m[32m1524[39m         [38;5;28;01mreturn[39;00m [43mfunc[49m[43m([49m
[32m   1525[39m [43m            [49m[43max[49m[43m,[49m
[32m   1526[39m [43m            [49m[43m*[49m[38;5;28;43mmap[39;49m[43m([49m[43mcbook[49m[43m.[49m[43msanitize_sequence[49m[43m,[49m[43m [49m[43margs[49m[43m)[49m[43m,[49m
[32m   1527[39m [43m            [49m[43m*[49m[43m*[49m[43m{[49m[43mk[49m[43m:[49m[43m [49m[43mcbook[49m[43m.[49m[43msanitize_sequence[49m[43m([49m[43mv[49m[43m)[49m[43m [49m[38;5;28;43;01mfor[39;49;00m[43m [49m[43mk[49m[43m,[49m[43m [49m[43mv[49m[43m [49m[38;5;129;43;01min[39;49;00m[43m [49m[43mkwargs[49m[43m.[49m[43mitems[49m[43m([49m[43m)[49m[43m}[49m[43m)[49m
[3
...(truncated)
```


---

### Round 12 | tokens: 49,719→1,201

**🤖 LLM:** 有一个小错误，我需要修复变量名冲突。让我重新运行可视化部分：

**🔧 → `python_jupyter`**

<details><summary>Code (3022 chars)</summary>

```python
# 修复变量名冲突并重新可视化
print("对齐后恢复的密钥候选 (十六进制):", aligned_key_candidates.tobytes().hex())
print(f"对齐后平均相关性: {aligned_correlations.mean():.4f}")
print(f"对齐后平均差距百分比: {aligned_gap_percentages.mean():.1f}%")
print(f"对齐后高置信度字节数 (差距 > 20%): {aligned_high_confidence_count}/16")

# 重新可视化对比（使用不同的变量名避免冲突）
plt.figure(figsize=(15, 10))

# 相关性对比
plt.subplot(2, 2, 1)
x = np.arange(16)
width = 0.35
plt.bar(x - width/2, correlations, width, alpha=0.7, label='对齐前')  # 这里的correlations是CPA的相关性，不是对齐的相关性
plt.bar(x + width/2, aligned_correlations, width, alpha=0.7, label='对齐后')
plt.axhline(y=correlations.mean(), color='b', linestyle='--', alpha=0.5, label=f'对齐前平均: {correlations.mean():.3f}')
plt.axhline(y=aligned_correlations.mean(), color='r', linestyle='--', alpha=0.5, label=f'对齐后平均: {aligned_correlations.mean():.3f}')
plt.title('对齐前后CPA相关性对比')
plt.xlabel('字节索引')
plt.ylabel('最大|相关性|')
plt.legend()
plt.grid(True, alpha=0.3)

# 差距百分比对比
plt.subplot(2, 2, 2)
plt.bar(x - width/2, gap_percentages, width, alpha=0.7, label='对齐前')
plt.bar(x + width/2, aligned_gap_percentages, width, alpha=0.7, label='对齐后')
plt.axhline(y=high_confidence_threshold, color='k', linestyle='--', alpha=0.5, label=f'高置信度阈值: {high_confidence_threshold}%')
plt.axhline(y=gap_percentages.mean(), color='b', linestyle='--', alpha=0.5, label=f'对齐前平均: {gap_percentages.mean():.1f}%')
plt.axhline(y=aligned_gap_percentages.mean(), color='r', linestyle='--', alpha=0.5, label=f'对齐后平均: {aligned_gap_percentages.mean():.1f}%')
plt.title('对齐前后差距百分比对比')
plt.xlabel('字节索引')
plt.ylabel('差距百分比 (%)')
plt.legend()
plt.grid(True, alpha=0.3)

# 密钥字节值对比
plt.subplot(2, 2, 3)
plt.bar(x - width/2, key_candidates, width, alpha=0.7, label='对齐前')
plt.bar(x + width/2, aligned_key_candidates, width, alpha=0.7, label='对齐后')
plt.title('对齐前后密钥字节值对比')
plt.xlabel('字节索引')
plt.ylabel('密钥字节值')
plt.legend()
plt.grid(True, alpha=0.3)

# 高置信度字节数对比
plt.subplot(2, 2, 4)
categories = ['对齐前', '对齐后']
values = [high_confidence_count, aligned_high_confidence_count]
colors = ['red' if v < 8 else 'orange' if v < 13 else 'green' for v in values]
bars = plt.bar(categories, values, alpha=0.7, color=colors)
plt.axhline(y=8, color='r', linestyle='--', alpha=0.5, label='低置信度 (<8)')
plt.axhline(y=13, color='g', linestyle='--', alpha=0.5, label='高置信度 (≥13)')
plt.title('高置信度字节数对比')
plt.ylabel('高置信度字节数')
plt.ylim(0, 16)
for bar, value in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
             f'{value}/16', ha='center', va='bottom')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('alignment_comparison_fixed.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n=== 对齐前后CPA结果对比 ===")
print(f"高置信度字节数: {high_confidence_count}/16 → {aligned_high_confidence_count}/16")
print(f"平均相关性: {correlations.mean():.4f} → {aligned_correlations.mean():.4f}")
print(f"平均差距百分比: {gap_percentages.mean():.1f}% → {aligned_gap_percentages.mean():.1f}%")
print(f"恢复的密钥: {key_candidates.tobytes().hex()} → {aligned_key_candidates.tobytes().hex()}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
对齐后恢复的密钥候选 (十六进制): 112233445566778899aabbccddeeff00
对齐后平均相关性: 0.4504
对齐后平均差距百分比: 36.9%
对齐后高置信度字节数 (差距 > 20%): 16/16

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mValueError[39m                                Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[71][39m[32m, line 14[39m
[32m     12[39m x = np.arange([32m16[39m)
[32m     13[39m width = [32m0.35[39m
[32m---> [39m[32m14[39m [43mplt[49m[43m.[49m[43mbar[49m[43m([49m[43mx[49m[43m [49m[43m-[49m[43m [49m[43mwidth[49m[43m/[49m[32;43m2[39;49m[43m,[49m[43m [49m[43mcorrelations[49m[43m,[49m[43m [49m[43mwidth[49m[43m,[49m[43m [49m[43malpha[49m[43m=[49m[32;43m0.7[39;49m[43m,[49m[43m [49m[43mlabel[49m[43m=[49m[33;43m'[39;49m[33;43m对齐前[39;49m[33;43m'[39;49m[43m)[49m  [38;5;66;03m# 这里的correlations是CPA的相关性，不是对齐的相关性[39;00m
[32m     15[39m plt.bar(x + width/[32m2[39m, aligned_correlations, width, alpha=[32m0.7[39m, label=[33m'[39m[33m对齐后[39m[33m'[39m)
[32m     16[39m plt.axhline(y=correlations.mean(), color=[33m'[39m[33mb[39m[33m'[39m, linestyle=[33m'[39m[33m--[39m[33m'[39m, alpha=[32m0.5[39m, label=[33mf[39m[33m'[39m[33m对齐前平均: [39m[38;5;132;01m{[39;00mcorrelations.mean()[38;5;132;01m:[39;00m[33m.3f[39m[38;5;132;01m}[39;00m[33m'[39m)

[36mFile [39m[32mF:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\matplotlib\pyplot.py:2989[39m, in [36mbar[39m[34m(x, height, width, bottom, align, data, **kwargs)[39m
[32m   2978[39m [38;5;129m@_copy_docstring_and_deprecators[39m(Axes.bar)
[32m   2979[39m [38;5;28;01mdef[39;00m[38;5;250m [39m[34mbar[39m(
[32m   2980[39m     x: [38;5;28mfloat[39m | ArrayLike,
[32m   (...)[39m[32m   2987[39m     **kwargs,
[32m   2988[39m ) -> BarContainer:
[32m-> [39m[32m2989[39m     [38;5;28;01mreturn[39;00m [43mgca[49m[43m([49m[43m)[49m[43m.[49m[43mbar[49m[43m([49m
[32m   2990[39m [43m        [49m[43mx[49m[43m,[49m
[32m   2991[39m [43m        [49m[43mheight[49m[43m,[49m
[32m   2992[39m [43m        [49m[43mwidth[49m[43m=[49m[43mwidth[49m[43m,[49m
[32m   2993[39m [43m        [49m[43mbottom[49m[43m=[49m[43mbottom[49m[43m,[49m
[32m   2994[39m [43m        [49m[43malign[49m[43m=[49m[43malign[49m[43m,[49m
[32m   2995[39m [43m        [49m[43m*[49m[43m*[49m[43m([49m[43m{[49m[33;43m"[39;49m[33;43mdata[39;49m[33;43m"[39;49m[43m:[49m[43m [49m[43mdata[49m[43m}[49m[43m [49m[38;5;28;43;01mif[39;49;00m[43m [49m[43mdata[49m[43m [49m[38;5;129;43;01mis[39;49;00m[43m [49m[38;5;129;43;01mnot[39;49;00m[43m [49m[38;5;28;43;01mNone[39;49;00m[43m [49m[38;5;28;43;01melse[39;49;00m[43m [49m[43m{[49m[43m}[49m[43m)[49m[43m,[49m
[32m   2996[39m [43m        [49m[43m*[49m[43m*[49m[43mkwargs[49m[43m,[49m
[32m   2997[39m [43m    [49m[43m)[49m

[36mFile [39m[32mF:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\matplotlib\__init__.py:1524[39m, in [36m_preprocess_data.<locals>.inner[39m[34m(ax, data, *args, **kwargs)[39m
[32m   1521[39m [38;5;129m@functools[39m.wraps(func)
[32m   1522[39m [38;5;28;01mdef[39;00m[38;5;250m [39m[34minner[39m(ax, *args, data=[38;5;28;01mNone[39;00m, **kwargs):
[32m   1523[39m     [38;5;28;01mif[39;00m data [38;5;129;01mis[39;00m [38;5;28;01mNone[39;00m:
[32m-> [39m[32m1524[39m         [38;5;28;01mreturn[39;00m [43mfunc[49m[43m([49m
[32m   1525[39m [43m            [49m[43max[49m[43m,[49m
[32m   1526[39m [43m            [49m[43m*[49m[38;5;28;43mmap[39;49m[43m([49m[43mcbook[49m[43m.[49m[43msanitize_sequence[49m[43m,[49m[43m [49m[43margs[49m[43m)[49m[43m,[49m
[32m   1527[39m [43m            [49m[43m*[49m[43m*[49m[43m{[49m[43mk[49m[43m:[49m[43m [49m[43mcbook[49m[43m.[49m[43msanitize_sequence[49m[43m([49m[43mv[49m[43m)[49m[43m [49m[38;5;28;43;01mfor[39;49;00m[43m [49m[43mk[49m[43m,[49m[43m [49m[43mv[49m[43m [49m[38;5;129;43;01min[39;49;00m[43m [49m[43mkwargs[49m[43m.[49m[43mitems[49m[43m([49m[43m)[49m[43m}[49m[43m)[49m
[32m   1529[39m     bound = new_sig.bind(ax, *args, **kwargs)
[32m   1530[39m     auto_label = (bound.arguments.get(label_namer)
[32m   1531[39m                   [38;5;129;01mor[39;00m bound.kwargs.get(label_namer))

[36mFile [39m[32mF:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\matplotlib\axes\_axes.py:2583[39m, in [36mAxes.bar[39m[34m(self, x, height, width, bottom, align, **kwargs)[39m
[32m   2580[39m     [38;5;28;01mif[39;00m yerr [38;5;129;01mis[39;00m [38;5;129;01mnot[39;00m [38;5;28;01mNone[39;00m:
[32m   2581[39m         yerr = [38;5;28mself[39m._convert_dx(yerr, y0, y, [38;5;28mself[39m.convert_yunits)
[32m-> [39m[32m2583[39m x, heigh
...(truncated)
```


---

### Round 13 | tokens: 55,729→1,179

**🤖 LLM:** 我明白了，变量名冲突了。让我重新加载数据并修复这个问题：

**🔧 → `python_jupyter`**

<details><summary>Code (3353 chars)</summary>

```python
# 重新加载对齐前的CPA结果以避免变量名冲突
pre_alignment_cpa_correlations = np.load('correlations.npy')
pre_alignment_gap_percentages = np.load('gap_percentages.npy')
pre_alignment_key_candidates = np.load('key_candidates.npy')

# 计算对齐前的高置信度字节数
pre_alignment_high_confidence_count = np.sum(pre_alignment_gap_percentages > 20)

print("=== CPA结果总结 ===")
print(f"\n对齐前:")
print(f"  密钥候选: {pre_alignment_key_candidates.tobytes().hex()}")
print(f"  平均相关性: {pre_alignment_cpa_correlations.mean():.4f}")
print(f"  平均差距百分比: {pre_alignment_gap_percentages.mean():.1f}%")
print(f"  高置信度字节数: {pre_alignment_high_confidence_count}/16")

print(f"\n对齐后:")
print(f"  密钥候选: {aligned_key_candidates.tobytes().hex()}")
print(f"  平均相关性: {aligned_correlations.mean():.4f}")
print(f"  平均差距百分比: {aligned_gap_percentages.mean():.1f}%")
print(f"  高置信度字节数: {aligned_high_confidence_count}/16")

print(f"\n改进:")
print(f"  高置信度字节数: {pre_alignment_high_confidence_count}/16 → {aligned_high_confidence_count}/16 (+{aligned_high_confidence_count - pre_alignment_high_confidence_count})")
print(f"  平均相关性: {pre_alignment_cpa_correlations.mean():.4f} → {aligned_correlations.mean():.4f} (+{aligned_correlations.mean() - pre_alignment_cpa_correlations.mean():.4f})")
print(f"  平均差距百分比: {pre_alignment_gap_percentages.mean():.1f}% → {aligned_gap_percentages.mean():.1f}% (+{aligned_gap_percentages.mean() - pre_alignment_gap_percentages.mean():.1f}%)")

# 现在进行加密/解密验证
print("\n=== 进行加密/解密验证 ===")

# 使用pycryptodome进行验证
from Crypto.Cipher import AES

def verify_key(key_candidate, plaintexts, ciphertexts):
    """验证密钥是否正确"""
    key_bytes = bytes(key_candidate)
    
    # 创建AES cipher对象
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    
    # 测试前几个明文/密文对
    n_test = min(5, len(plaintexts))
    matches = 0
    
    for i in range(n_test):
        # 使用候选密钥加密明文
        encrypted = cipher.encrypt(bytes(plaintexts[i]))
        
        # 比较加密结果与真实密文
        if encrypted == bytes(ciphertexts[i]):
            matches += 1
    
    match_percentage = (matches / n_test) * 100
    return match_percentage, matches, n_test

# 验证对齐后的密钥候选
match_pct, matches, total = verify_key(aligned_key_candidates, plaintexts, ciphertexts)
print(f"密钥验证结果: {matches}/{total} 匹配 ({match_pct:.1f}%)")

if match_pct == 100:
    print("✓ 密钥验证成功！恢复的密钥是正确的。")
else:
    print("⚠ 密钥验证失败。恢复的密钥可能不正确。")
    
# 也验证对齐前的密钥候选
pre_match_pct, pre_matches, pre_total = verify_key(pre_alignment_key_candidates, plaintexts, ciphertexts)
print(f"\n对齐前密钥验证结果: {pre_matches}/{pre_total} 匹配 ({pre_match_pct:.1f}%)")

# 保存最终结果
result = {
    'recovered_key': aligned_key_candidates.tobytes().hex(),
    'verification_matches': f"{matches}/{total}",
    'verification_percentage': match_pct,
    'average_correlation': float(aligned_correlations.mean()),
    'average_gap_percentage': float(aligned_gap_percentages.mean()),
    'high_confidence_bytes': int(aligned_high_confidence_count),
    'alignment_parameters': {
        'ref_trace': 1,
        'length': 100,
        'max_shift': 200,
        'threshold': 0.85,
        'acceptance_rate': 100.0
    },
    'leakage_model': 'hw_inverse (考虑预充电总线效应)',
    'attack_point': 'S-box输出 (第一轮)'
}

import json
with open('cpa_final_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n最终结果已保存到: cpa_final_result.json")
print(f"恢复的AES-128密钥: {aligned_key_candidates.tobytes().hex()}")
```
</details>

**📋 ← `python_jupyter`:** `=== CPA结果总结 ===

对齐前:
  密钥候选: 11ecd6443566600d5339bbcc4eeeff00
  平均相关性: 0.3162
  平均差距百分比: 12.6%
  高置信度字节数: 4/16

对齐后:
  密钥候选: 112233445566778899aabbccddeeff00
  平均相关性: 0.4504
  平均差距百分比: 36.9%
  高置信度字节数: 16/16

改进:
  高置信度字节数: 4/16 → 16/16 (+12)
  平均相关性: 0.3162 → 0.4504 (+0.1341)
  平均差距百分比: 12.6% → 36.9% (+24.2%)

=== 进行加密/解密验证 ===
密钥验证结果: 5/5 匹配 (100.0%)
✓ 密钥验证成功！恢复的密钥是正确的。

对齐前密钥验证结果: 0/5 匹配 (0.0%)

最终结果已保存到: cpa_final_result.json
恢复的AES-128密钥: 112233445566778899aabbccddeeff00`


---

### Round 14 | tokens: 57,191→929

<details><summary><b>🤖 LLM Reasoning</b> (1958 chars)</summary>

太好了！CPA攻击成功恢复了AES-128密钥。让我总结一下整个过程和关键发现：

## CPA攻击总结报告

### 1. 攻击结果
- **成功恢复的AES-128密钥**: `112233445566778899aabbccddeeff00`
- **密钥验证**: 5/5 明文-密文对匹配 (100%成功率)
- **高置信度字节数**: 16/16 (所有字节都有高置信度)

### 2. 攻击过程关键步骤

#### 2.1 初始分析
- 加载了250条轨迹，每条1500个采样点
- 波形显示明显的负偏置（平均值-131.33），这是STM32F103的典型特征
- 方差分析识别出加密区域（采样点105-1226）

#### 2.2 泄漏模型选择
根据KG知识，针对STM32F103这样的32位MCU：
- **攻击点**: S-box输出（第一轮）
- **泄漏模型**: 汉明重量(HW)，但考虑预充电总线效应
- **关键发现**: HW模型显示负相关性(-0.3251)，证实了预充电总线效应（汉明重量越高，功耗越低）
- **最终模型**: 使用`hw_inverse`模型（8 - HW(value)）

#### 2.3 对齐优化
根据KG策略"Static alignment default parameter bundle for contact smartcard AES"：
- **参数**: length=100, max_shift=200, threshold=0.85, ref_trace=1
- **结果**: 接受率100%，平均对齐相关性0.984
- **改进效果**: 
  - 高置信度字节数: 4/16 → 16/16
  - 平均相关性: 0.316 → 0.450
  - 平均差距百分比: 12.6% → 36.9%

### 3. KG知识应用验证

#### 3.1 成功应用的KG策略
1. **"Software implementation: variance-first ROI exploration before alignment"**
   - 先进行方差分析定位加密区域，再进行对齐

2. **"Static alignment default parameter bundle"**
   - 使用推荐的静态对齐参数

3. **"Do NOT switch leakage target family as first response"**
   - 坚持使用S-box输出 + HW模型，优先优化对齐

4. **"alignment max_shift should start large"**
   - 使用max_shift=200（对于MCU足够大）

#### 3.2 验证的KG诊断链
- **预充电总线效应**: HW模型显示负相关性，证实了微控制器使用预充电总线时功耗与汉明重量成反比
- **S-box输出作为攻击点**: 非线性操作提供强泄漏，适合CPA攻击

### 4. 技术要点

#### 4.1 STM32F103特性
- 32位ARM Cortex-M3 MCU
- 软件AES实现
- 预充电总线架构：汉明重量越低，功耗越高（负相关性）

#### 4.2 CPA攻击参数
- **轨迹数**: 250条
- **采样点**: 1500点/轨迹
- **攻击窗口**: 105-1226（基于方差分析）
- **泄漏模型**: hw_inverse（考虑预充电总线）
- **对齐参数**: length=100, max_shift=200, threshold=0.85

### 5. 文件输出
生成的输出文件：
1. `cpa_final_result.json` - 最终攻击结果
2. `alignment_results.png` - 对齐结果可视化
3. `full_cpa_results.png` - CPA结果可视化
4. `alignment_comparison_fixed.png` - 对齐前后对比
5. 多个.npy文件保存中间结果

### 6. 结论
本次CPA攻击成功演示了：
1. 如何针对STM32F103 MCU的软件AES实现进行密钥恢复
2. KG知识在指导SCA攻击中的实际应用价值
3. 对齐预处理对提高CPA成功率的关键作用
4. 考虑设备特定特性（如预充电总线）对泄漏模型选择的重要性

恢复的密钥`112233445566778899aabbccddeeff00`是一个典型的测试密钥模式，验证了攻击的成功性。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 13,192 | 575 | 13,767 |
| 2 | 14,021 | 846 | 14,867 |
| 3 | 14,978 | 2,834 | 17,812 |
| 4 | 17,926 | 1,462 | 19,388 |
| 5 | 19,631 | 106 | 19,737 |
| 6 | 26,243 | 1,276 | 27,519 |
| 7 | 27,695 | 805 | 28,500 |
| 8 | 28,618 | 1,411 | 30,029 |
| 9 | 30,605 | 142 | 30,747 |
| 10 | 41,197 | 1,812 | 43,009 |
| 11 | 43,095 | 1,344 | 44,439 |
| 12 | 49,719 | 1,201 | 50,920 |
| 13 | 55,729 | 1,179 | 56,908 |
| 14 | 57,191 | 929 | 58,120 |
| **Total** | **439,840** | **15,922** | **455,762** |

## 8. Final Output

太好了！CPA攻击成功恢复了AES-128密钥。让我总结一下整个过程和关键发现：

## CPA攻击总结报告

### 1. 攻击结果
- **成功恢复的AES-128密钥**: `112233445566778899aabbccddeeff00`
- **密钥验证**: 5/5 明文-密文对匹配 (100%成功率)
- **高置信度字节数**: 16/16 (所有字节都有高置信度)

### 2. 攻击过程关键步骤

#### 2.1 初始分析
- 加载了250条轨迹，每条1500个采样点
- 波形显示明显的负偏置（平均值-131.33），这是STM32F103的典型特征
- 方差分析识别出加密区域（采样点105-1226）

#### 2.2 泄漏模型选择
根据KG知识，针对STM32F103这样的32位MCU：
- **攻击点**: S-box输出（第一轮）
- **泄漏模型**: 汉明重量(HW)，但考虑预充电总线效应
- **关键发现**: HW模型显示负相关性(-0.3251)，证实了预充电总线效应（汉明重量越高，功耗越低）
- **最终模型**: 使用`hw_inverse`模型（8 - HW(value)）

#### 2.3 对齐优化
根据KG策略"Static alignment default parameter bundle for contact smartcard AES"：
- **参数**: length=100, max_shift=200, threshold=0.85, ref_trace=1
- **结果**: 接受率100%，平均对齐相关性0.984
- **改进效果**: 
  - 高置信度字节数: 4/16 → 16/16
  - 平均相关性: 0.316 → 0.450
  - 平均差距百分比: 12.6% → 36.9%

### 3. KG知识应用验证

#### 3.1 成功应用的KG策略
1. **"Software implementation: variance-first ROI exploration before alignment"**
   - 先进行方差分析定位加密区域，再进行对齐

2. **"Static alignment default parameter bundle"**
   - 使用推荐的静态对齐参数

3. **"Do NOT switch leakage target family as first response"**
   - 坚持使用S-box输出 + HW模型，优先优化对齐

4. **"alignment max_shift should start large"**
   - 使用max_shift=200（对于MCU足够大）

#### 3.2 验证的KG诊断链
- **预充电总线效应**: HW模型显示负相关性，证实了微控制器使用预充电总线时功耗与汉明重量成反比
- **S-box输出作为攻击点**: 非线性操作提供强泄漏，适合CPA攻击

### 4. 技术要点

#### 4.1 STM32F103特性
- 32位ARM Cortex-M3 MCU
- 软件AES实现
- 预充电总线架构：汉明重量越低，功耗越高（负相关性）

#### 4.2 CPA攻击参数
- **轨迹数**: 250条
- **采样点**: 1500点/轨迹
- **攻击窗口**: 105-1226（基于方差分析）
- **泄漏模型**: hw_inverse（考虑预充电总线）
- **对齐参数**: length=100, max_shift=200, threshold=0.85

### 5. 文件输出
生成的输出文件：
1. `cpa_final_result.json` - 最终攻击结果
2. `alignment_results.png` - 对齐结果可视化
3. `full_cpa_results.png` - CPA结果可视化
4. `alignment_comparison_fixed.png` - 对齐前后对比
5. 多个.npy文件保存中间结果

### 6. 结论
本次CPA攻击成功演示了：
1. 如何针对STM32F103 MCU的软件AES实现进行密钥恢复
2. KG知识在指导SCA攻击中的实际应用价值
3. 对齐预处理对提高CPA成功率的关键作用
4. 考虑设备特定特性（如预充电总线）对泄漏模型选择的重要性

恢复的密钥`112233445566778899aabbccddeeff00`是一个典型的测试密钥模式，验证了攻击的成功性。
