# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_040954_254 |
| Duration | 152.2s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\DES-7816_GLM5_DKG_20260424_040954_254` |
| Total LLM Calls | 15 |
| First Round | prompt: 17,064, completion: 776 |
| Last Round | prompt: 27,203, completion: 390 |
| Total Tokens | 342,051 (prompt: 335,891, completion: 6,160) |

## 3. User Query

```
帮我对一个接触式智能卡实现的DES密码算法波形进行CPA恢复密钥，明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个接触式智能卡实现的DES密码算法波形进行CPA恢复密钥，明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy'"

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
["DES", "Contact Smartcard", "CPA", "Power", "Hamming Weight", "S-box Output", "Key Recovery"]

Parsed Keywords: `["DES", "Contact Smartcard", "CPA", "Power", "Hamming Weight", "S-box Output", "Key Recovery"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 45808 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (48056 chars, click to expand)</summary>

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

**Search keywords** (7): DES, Contact Smartcard, CPA, Power, Hamming Weight, S-box Output, Key Recovery

**Summary**: 37 upper entities, 33 relationships, 21 diagnostic chains, 16 strategies


## 1. Upper Layer Entities (37)


### Algorithm (3)

- **3DES** — num_rounds=48, key_length=112
- **DES** — num_rounds=16, encryption_mode=ECB, key_length=56
- **SimonsVoss key derivation function (obscurity function O and modified DES)** — num_rounds=8, key_length=128

### AttackPoint (6)

- **Inverse S-box Output** — round=13
- **Masked S-box Output**
- **S-box Output** — required_data=ciphertext, round=last
- **S-box Output and Mask** — required_data=plaintext, round=first
- **S-box output** — round=1
- **S-box outputs** — round=first

### DeviceClass (2)

- **Contact DES Test Card** — category=Smartcard
- **Contact Smartcard with 16-bit RISC CPU** — category=Smartcard, bus_width=16

### LeakageModel (5)

- **Hamming Weight** — requirements=software implementation
- **Hamming Weight (bit-based)** — requirements=bit-based
- **Hamming Weight of transitions**
- **Hamming weight**
- **Hamming weight of fused features**

### Pipeline (10)

- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, canonical_source=round1_patch_002, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **Generic Side-Channel Attack Pipeline** — source=PAP-13-2009-EUROCRYPT-Standaert-Unified-Framework, trigger_condition=starting a side-channel key recovery attack, applicable_scenarios=general side-channel attacks on cryptographic implementations
- **Single-bit AES Key Recovery** — source=tutorial_lab, trigger_condition=when attacking an AES implementation with a single bit of leakage available, applicable_scenarios=AES implementations where a single bit of the S-box output is leaked (e.g., through power or EM side channels)

### RecoveryMethod (4)

- **Full Key Recovery** — input_type=correlation scores for all bytes
- **Full key recovery** — input_type=partial_subkey_candidates
- **Key Recovery** — input_type=SAT solution
- **Key recovery** — input_type=round keys

### StatMethod (7)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Compare hypothetical power consumption with measured traces** — type=non_profiled
- **Generate Hamming weight models for S-box output** — type=non_profiled

## 2. Relationships (33)

- `Algorithm:3DES` —[has_attack_point [source_text=first round S-box output, support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `AttackPoint:S-box output`
- `Algorithm:3DES` —[works_with [source_text=3DES was implemented on the smartcard., support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `DeviceClass:Commercial Contactless Smartcard`
- `Algorithm:3DES` —[strategy_applies_to [source_text=The process to perform a DEMA of the 3DES implementation can be split up into the following steps, applicability=general, source_papers=["PAP-86"]]]→ `Strategy:DEMA on RFID Smartcard - Core Steps`
- `DeviceClass:Contact DES Test Card` —[works_with [source_text=使用该DES卡一阶CPA分析, support_count=1, confidence=0.2, source_papers=["MAN-02-2024-MathMagic-DES-Contact-TestCard-Example"]]]→ `TraceType:Power`
- `DeviceClass:Contact DES Test Card` —[works_with [source_text=接触式DES测试卡测评示例, support_count=1, confidence=0.2, source_papers=["MAN-02-2024-MathMagic-DES-Contact-TestCard-Example"]]]→ `Preprocessing:Known-key Correlation Analysis`
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
- `StatMethod:Generate Hamming weight models for S-box output` —[consists_of [parameters_note=models are lookup tables for the leakage of each possible S-box output, source_text=Generate Hamming weight models for S-box output, support_count=1, is_optional=False]]→ `Pipeline:SCALib CPA Attack on AES`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Avoid using the identity model for bijective S-boxes in MIA; use a non-bijective model (e.g., Hamming weight) or target a non-bijective intermediate value (e.g., predict only a subset of bits).`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:try different power models (bit, Hamming weight, Hamming distance, zero-value) to see which yields the highest and most distinct peak for a single key hypothesis`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:use the Hamming weight model for microcontrollers with precharged buses`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Use a non-injective leakage function that incurs information loss (e.g., Hamming weight, LSB, MSB).`
- `AttackPoint:S-box Output` —[strategy_applies_to [source=round1_patch_001, condition=Software implementation (MCU/smartcard) + first-pass CPA returns low correlation (cpa_avg_correlation < 0.2) + gap distribution unclear, applicability=specific]]→ `Strategy:Do NOT switch leakage target family as first response to low correlation on software implementations`
- `AttackPoint:Inverse S-box Output` —[has_attack_point [source_text=attack_point: Inverse S-box Output, round: 14, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[has_attack_point [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`
- `AttackPoint:Masked S-box Output` —[works_with [source_text=攻击点：Two masked S-box outputs, support_count=1, confidence=0.2, source_papers=["MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated"]]]→ `Algorithm:AES`
- `RecoveryMethod:Full Key Recovery` —[consists_of [parameters_note=repeat for all 16 bytes of AES-128 key, source_text=Full Key Recovery, support_count=1, is_optional=False]]→ `Pipeline:CPA Attack on AES Firmware Implementation`
- `RecoveryMethod:Full key recovery` —[relates_to [role=add_step]]→ `Action:Apply key enumeration algorithms`
- `RecoveryMethod:Full key recovery` —[consists_of [parameters_note=repeat for all 8 S-boxes to recover 48-bit round subkey; remaining 8 bits via exhaustive search or analyzing another round, source_text=repeat for all 8 S-boxes to recover 48-bit round subkey, support_count=1, is_optional=False]]→ `Pipeline:Differential Power Analysis (DPA) on DES`
- `Pipeline:Generic Side-Channel Attack Pipeline` —[consists_of [parameters_note=apply statistical test T to compare model/partition with leakages, source_text=Statistical test: apply statistical test T to compare model/partition with leakages, support_count=1, is_optional=False]]→ `StatMethod:Statistical Test`
- `Pipeline:Generic Side-Channel Attack Pipeline` —[consists_of [parameters_note=mapping R transforms leakages, may include filtering, averaging, condition=if leakages and predictions have different number of samples or post-processing needed, source_text=Leakage reduction: mapping R transforms leakages, may include filtering, averaging, support_count=1]]→ `Preprocessing:Leakage Reduction`

## 3. Diagnostic Chains (21)


### Obs: `trace_count` — any
- **Cause** (high): statistical confidence requires a certain number of traces to distinguish the correct key hypothesis from zero correlation
- **Check**: statistical derivation using confidence intervals
- **Action**: use the rule of thumb n = (3.719 / p)^2 to estimate traces needed for confidence level 0.9999, where p is the expected correlation coefficient
  - operation: `adjust_param`
  - target: `trace count`
  - strategy: for |p| ≤ 0.2, this rule provides a good estimate; the constant 3.719 corresponds to z_(1-α/2) for α=0.0001
- **Relates to**: DiagnosticMethod:`Efficiency Analysis`

### Obs: `vulnerability_to_ema` — any
- **Cause** (high): Electromagnetic emanations can be measured and analyzed similarly to power consumption, providing a side channel that leaks information about computations.
- **Action**: Use signal strength reduction (e.g., shielding) and signal information reduction (e.g., randomization) to protect against EMA.
  - operation: `add_step`
  - target: `implementation`
  - strategy: Employ circuit redesign, shielding, physically secured zones, and randomization techniques to reduce compromising signals.

### Obs: `recovered_key_verification` — any
- **Cause** (high): DES key bytes include a parity bit (LSB) that is often ignored or set to zero by encryption software/hardware.
- **Action**: Ignore or zero the least significant bit (parity bit) of each byte when comparing recovered DES key
  - operation: `verify`
  - target: `recovered_key`
  - strategy: When comparing recovered DES key to expected key, ignore or zero the least significant bit (parity bit) of each byte.
- **Relates to**: ValidationMethod:`Key Verification`

### Obs: `attack_feasibility_assessment` — any
- **Cause** (high): Global prediction vector provides theoretical noise-free baseline for feasibility estimation
- **Check**: Simulated attacks showed successful key distinction after ~300-600 traces
- **Action**: Perform simulated attack using global prediction vector before collecting real measurements
  - operation: `add_step`
  - target: `ValidationMethod`
  - strategy: Compute correlation between selected prediction matrix and global prediction vector for increasing N to estimate minimum required traces.
- **Relates to**: DeviceClass:`Simulated Device`

### Obs: `key_byte_distinguishability` — any
- **Cause** (high): Different key bytes (e.g., 0x55 and 0xAA) can have the same Hamming weight, making them indistinguishable if attacking the key directly. The S-box output provides a nonlinear transformation that spreads the Hamming weights, creating a unique signature for each key hypothesis.
- **Action**: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.
  - operation: `switch_component`
  - target: `attack point`
  - strategy: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.

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

### Obs: `attack_position_selection` — any
- **Cause** (high): The S-box output is a non-linear operation that often exhibits strong leakage in HW model, and is a common target in first-round attacks
- **Check**: Check implementation details for known leakage points
- **Action**: Set the target to 'S-box out' and model to 'HW' for first-round CPA on AES
  - operation: `adjust_param`
  - target: `cpa.target, cpa.model`
  - strategy: Target: S-box out, Model: HW
- **Relates to**: AttackPoint:`S-box Output`

### Obs: `leakage_model_selection` — any
- **Cause** (high): Non-linear operations (e.g., S-box) have stronger power consumption leakage than linear transformations
- **Check**: Compare correlation strength between S-box output and linear operation points
- **Action**: Choose S-box output as intermediate value for CPA or machine learning attacks
  - operation: `switch_component`
  - target: `intermediate_value`
  - strategy: Choose the S-box output (the value after XOR with round key and before linear transformation) as the intermediate value for CPA or machine learning attacks.
- **Relates to**: AttackPoint:`S-box Output`

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

## 4. Strategies (16)


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

### ⭐ • [canonical_pipeline_principle] Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)
- **Trigger**: Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap)
- **Rationale**: smoke iter2 Patch 003+003.1+003.2 DSv3.2 DES-7816 仍 3/5=60%，2 fail 最佳 aligned recovered key HD=6（远超 phase-14 成功 HD=3），key_search 500k-5M budget 覆盖 64^6 空间 < 0.01%。根因：agent 在 plaintext/ciphertext correlation 首带（~500-600 samples，IO/bus pre-encryption 区）对齐而非 variance peak 区（~1000-1300 samples，真 S-box 加密体）。Patch 003 Strategy A 有 variance-first 原则但 scope 限制 software MCU，DES 接触式智能卡被排除。本 strategy 将 variance-first 扩展为 device-agnostic，并明确 disjoint ROI 决策规则 + 欺骗性 alignment 指标诊断（high align_corr + low aligned CPA hc = anchor 错）。
- **Content**: [{"principle": "When variance-based ROI exploration and plaintext/ciphertext-correlation analysis disagree on the encryption-region location (disjoint candidate intervals), the agent MUST anchor static_aligner on the VARIANCE-peak region, NOT the first plaintext/ciphertext-correlation band. This is a device-agnostic rule that extends Strategy A's variance-first principle (originally software MCU o
- **Applies to**: StatMethod:CPA, Preprocessing:Static Alignment

### ⭐ • [canonical_pipeline_principle] Software implementation: variance-first ROI exploration before alignment
- **Trigger**: Software cryptographic implementation (any MCU: STM32F1/F4/Cortex/AVR/Arduino; or contact smartcard running software crypto) + non-profiled CPA + direct CPA returns unstable high_confidence_count below empirical_threshold
- **Rationale**: phase-11 DSv3.1T AES-STM32F103 成功样本 Round 2 即 np.var 定位方差突增区 (samples 1098-1107) → Round 3 direct CPA 成功；round19 DSv3.2 三条 STM32F103 fail 全缺 variance-first 步骤，直接把 plaintext/ciphertext correlation 首个相关带 当 ROI 做 static alignment，acceptance rate 持续 4/250-5/250 仍继续在同区间 重复对齐。此处 codify 为通用软件实现原则，阈值标 empirical。
- **Content**: [{"principle": "For software cryptographic implementations, when direct CPA does NOT yield stable high-confidence candidates, the agent MUST first perform variance-based / energy-signature ROI exploration (e.g., np.var / np.std over sliding windows) to locate the encryption region, BEFORE deciding alignment intervals or switching leakage targets.", "reason": "Software implementations on MCU/smartc
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

### ⭐ 📋 [troubleshooting_checklist] Decision to perform static alignment based on direct CPA result
- **Trigger**: after first CPA probe (without alignment)
- **Rationale**: Direct CPA can succeed without alignment if the waveform is already focused on the encryption interval. Alignment is only needed when signal is insufficient.
- **[rank 1]** if `high_confidence_count for AES` → if ≥13, skip alignment; if 10-12, enter alignment and multi-strategy; if <10, must align
- **[rank 2]** if `high_confidence_count for DES` → if ≥6, skip alignment; if 5, enter alignment and multi-strategy; if <5, must align
- **[rank 3]** if `high_confidence_count for SM4 per round` → if ≥3, skip alignment; if 2, enter alignment and multi-strategy; if <2, must align
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

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
All files for this session are stored in: ..\logs\exp3_GLM-5\DES-7816_GLM5_DKG_20260424_040954_254
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\DES-7816_GLM5_DKG_20260424_040954_254/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 17,064→776

**🤖 LLM:** 我来帮您对接触式智能卡DES实现进行CPA攻击。让我按照标准的SCA分析流程进行。

首先，让我检查数据并分析波形特征：

**🔧 → `python_jupyter`**

<details><summary>Code (1000 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
plain_path = r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy'
cipher_path = r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy'
wave_path = r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy'

plaintext = np.load(plain_path)
ciphertext = np.load(cipher_path)
wave = np.load(wave_path)

print(f"Plaintext shape: {plaintext.shape}, dtype: {plaintext.dtype}")
print(f"Ciphertext shape: {ciphertext.shape}, dtype: {ciphertext.dtype}")
print(f"Wave shape: {wave.shape}, dtype: {wave.dtype}")
print(f"\nFirst plaintext: {plaintext[0].hex()}")
print(f"First ciphertext: {ciphertext[0].hex()}")
print(f"\nWave statistics:")
print(f"  Min: {wave.min():.4f}, Max: {wave.max():.4f}")
print(f"  Mean: {wave.mean():.4f}, Std: {wave.std():.4f}")
```
</details>

**❌ ← `python_jupyter` Error:**

```
Plaintext shape: (100, 8), dtype: uint8
Ciphertext shape: (100, 8), dtype: uint8
Wave shape: (100, 2000), dtype: float32

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mAttributeError[39m                            Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[167][39m[32m, line 16[39m
[32m     14[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33mCiphertext shape: [39m[38;5;132;01m{[39;00mciphertext.shape[38;5;132;01m}[39;00m[33m, dtype: [39m[38;5;132;01m{[39;00mciphertext.dtype[38;5;132;01m}[39;00m[33m"[39m)
[32m     15[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33mWave shape: [39m[38;5;132;01m{[39;00mwave.shape[38;5;132;01m}[39;00m[33m, dtype: [39m[38;5;132;01m{[39;00mwave.dtype[38;5;132;01m}[39;00m[33m"[39m)
[32m---> [39m[32m16[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;130;01m\n[39;00m[33mFirst plaintext: [39m[38;5;132;01m{[39;00m[43mplaintext[49m[43m[[49m[32;43m0[39;49m[43m][49m[43m.[49m[43mhex[49m()[38;5;132;01m}[39;00m[33m"[39m)
[32m     17[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[33mFirst ciphertext: [39m[38;5;132;01m{[39;00mciphertext[[32m0[39m].hex()[38;5;132;01m}[39;00m[33m"[39m)
[32m     18[39m [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;130;01m\n[39;00m[33mWave statistics:[39m[33m"[39m)

[31mAttributeError[39m: 'numpy.ndarray' object has no attribute 'hex'
```


---

### Round 2 | tokens: 18,174→847

**🔧 → `python_jupyter`**

<details><summary>Code (2355 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
plain_path = r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy'
cipher_path = r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy'
wave_path = r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy'

plaintext = np.load(plain_path)
ciphertext = np.load(cipher_path)
wave = np.load(wave_path)

print(f"Plaintext shape: {plaintext.shape}, dtype: {plaintext.dtype}")
print(f"Ciphertext shape: {ciphertext.shape}, dtype: {ciphertext.dtype}")
print(f"Wave shape: {wave.shape}, dtype: {wave.dtype}")
print(f"\nFirst plaintext: {plaintext[0].tobytes().hex()}")
print(f"First ciphertext: {ciphertext[0].tobytes().hex()}")
print(f"\nWave statistics:")
print(f"  Min: {wave.min():.4f}, Max: {wave.max():.4f}")
print(f"  Mean: {wave.mean():.4f}, Std: {wave.std():.4f}")

# 绘制波形图
plt.figure(figsize=(14, 8))

# 绘制多条波形
plt.subplot(2, 2, 1)
for i in range(min(10, wave.shape[0])):
    plt.plot(wave[i], alpha=0.5, linewidth=0.5)
plt.title('First 10 Traces Overlay')
plt.xlabel('Sample Point')
plt.ylabel('Power')
plt.grid(True, alpha=0.3)

# 绘制平均波形
plt.subplot(2, 2, 2)
mean_wave = np.mean(wave, axis=0)
plt.plot(mean_wave)
plt.title('Average Trace')
plt.xlabel('Sample Point')
plt.ylabel('Power')
plt.grid(True, alpha=0.3)

# 绘制方差
plt.subplot(2, 2, 3)
var_wave = np.var(wave, axis=0)
plt.plot(var_wave)
plt.title('Variance Across Traces')
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.grid(True, alpha=0.3)

# 绘制方差（找加密区域）
plt.subplot(2, 2, 4)
plt.plot(var_wave)
plt.title('Variance (Zoomed)')
plt.xlabel('Sample Point')
plt.ylabel('Variance')
plt.grid(True, alpha=0.3)

# 标记方差峰值区域
var_peaks = np.where(var_wave > np.max(var_wave) * 0.3)[0]
if len(var_peaks) > 0:
    plt.axvspan(var_peaks[0], var_peaks[-1], alpha=0.3, color='red', label='High variance region')
    print(f"\nHigh variance region: samples {var_peaks[0]} - {var_peaks[-1]}")

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

print(f"\nVariance peak locations (top 10):")
peak_indices = np.argsort(var_wave)[-10:][::-1]
for idx in peak_indices:
    print(f"  Sample {idx}: variance = {var_wave[idx]:.6f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (881 chars)</summary>

```
Plaintext shape: (100, 8), dtype: uint8
Ciphertext shape: (100, 8), dtype: uint8
Wave shape: (100, 2000), dtype: float32

First plaintext: 0061025bbac9c589
First ciphertext: 52fb7a16e8dedeb1

Wave statistics:
  Min: -98.4252, Max: 90.5512
  Mean: -5.9419, Std: 31.1046

High variance region: samples 0 - 1999

Variance peak locations (top 10):
  Sample 1105: variance = 1595.474243
  Sample 1104: variance = 1573.464478
  Sample 1106: variance = 1541.100830
  Sample 1103: variance = 1523.647217
  Sample 1142: variance = 1523.459473
  Sample 1143: variance = 1506.620483
  Sample 1132: variance = 1503.621582
  Sample 1131: variance = 1500.556763
  Sample 1054: variance = 1472.062866
  Sample 1141: variance = 1469.117798
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2776163588.py:68: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 3 | tokens: 19,367→362

**🤖 LLM:** 好的，数据已加载成功：
- **100条波形**，每条2000个采样点
- **DES明文/密文**：8字节格式
- **方差峰值区域**：约1100-1150采样点，这可能是加密操作区域

现在让我按照**统一分析流程**进行CPA攻击。首先进行**第一次CPA探测**（不做对齐）：

**🔧 → `des_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `des_cpa_attack`</b> (2024 chars)</summary>

```
{"recovered_key": "C044F6082640244E", "cpa_avg_correlation": 0.423, "cpa_min_correlation": 0.3904, "n_traces": 100, "target": "S-box_out", "plot_path": "des_cpa_result_20260424_041109_955659.png", "detail_file": "des_cpa_detail_20260424_041109_955659.json", "per_sbox": [{"sbox": 0, "key": "0x31", "correlation": 0.39037268317088836, "time_index": 1322, "gap_pct": 0.1}, {"sbox": 1, "key": "0x0B", "correlation": 0.4060454194444173, "time_index": 1681, "gap_pct": 4.8}, {"sbox": 2, "key": "0x11", "correlation": 0.4525161327273126, "time_index": 968, "gap_pct": 17.3}, {"sbox": 3, "key": "0x12", "correlation": 0.4719257426834791, "time_index": 165, "gap_pct": 20.0}, {"sbox": 4, "key": "0x2C", "correlation": 0.395343631928101, "time_index": 423, "gap_pct": 5.1}, {"sbox": 5, "key": "0x03", "correlation": 0.41651745844251536, "time_index": 1324, "gap_pct": 1.3}, {"sbox": 6, "key": "0x2D", "correlation": 0.44027035877131243, "time_index": 131, "gap_pct": 5.5}, {"sbox": 7, "key": "0x14", "correlation": 0.41088700159899666, "time_index": 1135, "gap_pct": 7.6}], "high_confidence_count": 2, "recovery_assessment": "Only 2/8 sboxes are high-confidence. Treat this as a red band case: revisit interval selection, start position, or target choice. For DES hardware HD (R_xor_LOut), avg_corr 0.05-0.08 can still be normal, so check gap distribution first.", "low_confidence_subkeys": [{"subkey_index": 0, "sbox": 0, "best_key_hex": "0x31", "top1_top2_gap": 0.0013423937504577297}, {"subkey_index": 1, "
...(truncated)
```
</details>


![des_cpa_result_20260424_041109_955659.png](./des_cpa_result_20260424_041109_955659.png)


---

### Round 4 | tokens: 20,512→508

**🤖 LLM:** 第一次CPA探测结果分析：
- **高置信度S-box数量：2/8**（红色区域）
- **平均相关性：0.423**（不错）
- **问题**：各S-box时间索引差异很大（165-1681），说明存在对齐问题

根据决策规则，high_confidence_count < 5，**必须进行对齐**。但先让我验证一下当前恢复的密钥：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "key_hex": "C044F6082640244E",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (996 chars)</summary>

```
{"result_hex": "1284FD705ABCD783", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 0061025bbac9c589... → 1284FD705ABCD783...\n❌ Key verification FAILED — 8/8 ciphertext bytes differ\n   Expected:  52FB7A16E8DEDEB1\n   Got:       1284FD705ABCD783\n\n   ⚠️ IMPORTANT: '8 ciphertext bytes differ' does NOT mean '8 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 5 | tokens: 21,061→407

**🤖 LLM:** 验证失败（预期中，因为只有2/8高置信度）。现在进行**静态对齐**以改善结果。根据方差分析，加密区域在1100-1150附近：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy",
  "start": 1100,
  "length": 120,
  "max_shift": 50,
  "threshold": 85,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_041133_168522.npy", "plot_path": "align_overlay_20260424_041133_168522.png", "ref_trace_used": 50, "accepted": 16, "discarded": 84, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260424_041133_168522.npy", "plaintext_traces": 16, "out_ciphertext_npy": "ciphertext_aligned_20260424_041133_168522.npy", "ciphertext_traces": 16, "alignment_avg_correlation": 0.9719, "alignment_min_correlation": 0.954, "acceptance_rate": 0.16}`


![align_overlay_20260424_041133_168522.png](./align_overlay_20260424_041133_168522.png)


---

### Round 6 | tokens: 21,500→538

**🤖 LLM:** 对齐接受率太低（16%），需要调整参数。让我检查峰值位置变化范围：

**🔧 → `python_jupyter`**

<details><summary>Code (1296 chars)</summary>

```python
import numpy as np

# 加载原始波形
wave_path = r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy'
wave = np.load(wave_path)

# 在1100-1200范围内找每条波形的峰值位置
peak_positions = []
for i in range(wave.shape[0]):
    segment = wave[i, 1050:1200]
    peak_pos = np.argmax(np.abs(segment)) + 1050
    peak_positions.append(peak_pos)

peak_positions = np.array(peak_positions)
print(f"Peak positions in region 1050-1200:")
print(f"  Min: {peak_positions.min()}, Max: {peak_positions.max()}")
print(f"  Mean: {peak_positions.mean():.1f}, Std: {peak_positions.std():.1f}")
print(f"  Range: {peak_positions.max() - peak_positions.min()}")

# 绘制峰值位置分布
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 4))
plt.hist(peak_positions, bins=20, edgecolor='black')
plt.xlabel('Peak Position')
plt.ylabel('Count')
plt.title('Distribution of Peak Positions (1050-1200)')
plt.axvline(peak_positions.mean(), color='red', linestyle='--', label=f'Mean: {peak_positions.mean():.1f}')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('peak_position_distribution.png', dpi=150)
plt.show()

# 计算需要的max_shift
shift_range = peak_positions.max() - peak_positions.min()
print(f"\nRecommended max_shift: at least {shift_range} (current was 50)")
```
</details>

**📋 ← `python_jupyter`:** `Peak positions in region 1050-1200:
  Min: 1051, Max: 1196
  Mean: 1132.2, Std: 38.8
  Range: 145

Recommended max_shift: at least 145 (current was 50)
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1944440677.py:32: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 7 | tokens: 22,044→277

**🤖 LLM:** 峰值位置变化范围是145，需要增大max_shift。重新对齐：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy",
  "length": 120,
  "max_shift": 200,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy",
  "start": 1100,
  "threshold": 85,
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_041152_708983.npy", "plot_path": "align_overlay_20260424_041152_708983.png", "ref_trace_used": 50, "accepted": 91, "discarded": 9, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260424_041152_708983.npy", "plaintext_traces": 91, "out_ciphertext_npy": "ciphertext_aligned_20260424_041152_708983.npy", "ciphertext_traces": 91, "alignment_avg_correlation": 0.9729, "alignment_min_correlation": 0.9318, "acceptance_rate": 0.91}`


![align_overlay_20260424_041152_708983.png](./align_overlay_20260424_041152_708983.png)


---

### Round 8 | tokens: 22,464→134

**🤖 LLM:** 很好！接受率提升到91%（91/100条）。现在用对齐后的波形进行CPA：

**🔧 → `des_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_041152_708983.npy",
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_041152_708983.npy"
}`

<details><summary><b>📋 ← `des_cpa_attack`</b> (1552 chars)</summary>

```
{"recovered_key": "1002324454422688", "cpa_avg_correlation": 0.7413, "cpa_min_correlation": 0.652, "n_traces": 91, "target": "S-box_out", "plot_path": "des_cpa_result_20260424_041159_438015.png", "detail_file": "des_cpa_detail_20260424_041159_438015.json", "per_sbox": [{"sbox": 0, "key": "0x18", "correlation": 0.7861219521302546, "time_index": 1078, "gap_pct": 41.2}, {"sbox": 1, "key": "0x13", "correlation": 0.6520094660283255, "time_index": 1171, "gap_pct": 31.8}, {"sbox": 2, "key": "0x08", "correlation": 0.7474148478543082, "time_index": 1279, "gap_pct": 39.4}, {"sbox": 3, "key": "0x08", "correlation": 0.7813641064897408, "time_index": 1370, "gap_pct": 31.1}, {"sbox": 4, "key": "0x05", "correlation": 0.8241589391087105, "time_index": 1476, "gap_pct": 26.3}, {"sbox": 5, "key": "0x32", "correlation": 0.7124848855542844, "time_index": 1568, "gap_pct": 35.5}, {"sbox": 6, "key": "0x2B", "correlation": 0.7582891822678975, "time_index": 1675, "gap_pct": 42.7}, {"sbox": 7, "key": "0x02", "correlation": 0.6683774600351582, "time_index": 1767, "gap_pct": 22.4}], "high_confidence_count": 8, "recovery_assessment": "8/8 sboxes high-confidence (gap >= 15%). Only sboxes [] are unreliable. Run key_search to recover the master key (DES has 16-bit ambiguity from parity + PC-2 unselected bits). Do NOT switch target/method/alignment yet — for DES hardware HD (R_xor_LOut), avg_corr 0.05-0.08 is NORMAL baseline, not a failure signal.", "low_confidence_subkeys": [], "recommended_next_step": "most
...(truncated)
```
</details>


![des_cpa_result_20260424_041159_438015.png](./des_cpa_result_20260424_041159_438015.png)


---

### Round 9 | tokens: 23,209→216

**🤖 LLM:** 太好了！对齐后CPA结果显著改善：
- **高置信度S-box：8/8**（绿色区域！）
- **平均相关性：0.7413**（非常高）
- **所有gap > 15%**

现在验证密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "DES",
  "ciphertext_npy": "ciphertext_aligned_20260424_041152_708983.npy",
  "key_hex": "1002324454422688",
  "plaintext_npy": "plaintext_aligned_20260424_041152_708983.npy",
  "trace_index": 0
}`

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (996 chars)</summary>

```
{"result_hex": "748A23EF3BD3BE26", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 0061025bbac9c589... → 748A23EF3BD3BE26...\n❌ Key verification FAILED — 8/8 ciphertext bytes differ\n   Expected:  52FB7A16E8DEDEB1\n   Got:       748A23EF3BD3BE26\n\n   ⚠️ IMPORTANT: '8 ciphertext bytes differ' does NOT mean '8 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 10 | tokens: 23,650→315

**🤖 LLM:** 验证失败，但所有S-box都是高置信度。这可能是因为DES密钥的奇偶校验位问题。让我使用key_search搜索正确密钥：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "cpa_detail_file": "des_cpa_detail_20260424_041159_438015.json",
  "ciphertext_npy": "ciphertext_aligned_20260424_041152_708983.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 20,
  "max_combinations": 50000,
  "plaintext_npy": "plaintext_aligned_20260424_041152_708983.npy",
  "recovered_key_hex": "1002324454422688"
}
```
</details>

<details><summary><b>📋 ← `key_search`</b> (1378 chars)</summary>

```
{"found": true, "correct_key": "1022324454667688", "search_rounds": 245, "total_search_space": 256, "sbox_analysis": [{"sbox": 0, "gap": 0.4115, "reliable": true, "top1": 24, "candidates": [24, 19, 4, 17, 13, 26, 15, 58, 6, 56, 36, 23, 53, 51, 38, 57, 55, 39, 44, 7]}, {"sbox": 1, "gap": 0.3185, "reliable": true, "top1": 19, "candidates": [19, 18, 59, 48, 62, 4, 17, 58, 12, 13, 3, 32, 16, 31, 57, 26, 41, 23, 2, 33]}, {"sbox": 2, "gap": 0.3938, "reliable": true, "top1": 8, "candidates": [8, 2, 7, 43, 13, 1, 41, 56, 17, 15, 33, 9, 12, 63, 24, 0, 32, 4, 25, 42]}, {"sbox": 3, "gap": 0.3108, "reliable": true, "top1": 8, "candidates": [8, 32, 17, 48, 24, 20, 7, 23, 37, 2, 16, 11, 47, 28, 33, 1, 4, 41, 13, 27]}, {"sbox": 4, "gap": 0.2634, "reliable": true, "top1": 5, "candidates": [5, 35, 0, 51, 22, 48, 54, 38, 16, 21, 14, 44, 34, 53, 33, 6, 60, 52, 20, 26]}, {"sbox": 5, "gap": 0.3554, "reliable": true, "top1": 50, "candidates": [50, 15, 6, 36, 44, 17, 34, 45, 9, 25, 10, 4, 58, 19, 33, 1, 63, 56, 18, 2]}, {"sbox": 6, "gap": 0.4269, "reliable": true, "top1": 43, "candidates": [43, 22, 53, 44, 41, 48, 54, 27, 18, 0, 38, 61, 56, 21, 20, 51, 15, 35, 13, 26]}, {"sbox": 7, "gap": 0.2239, "reliable": true, "top1": 2, "candidates": [2, 3, 5, 59, 6, 28, 26, 54, 60, 53, 4, 17, 30, 15, 45, 13, 52, 41, 1, 55]}], "message": "DES key found after 245 searches: 1022324454667688"}
```
</details>


---

### Round 11 | tokens: 24,628→126

**🤖 LLM:** 太好了！key_search找到了正确密钥！让我验证：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "DES",
  "ciphertext_npy": "ciphertext_aligned_20260424_041152_708983.npy",
  "key_hex": "1022324454667688",
  "plaintext_npy": "plaintext_aligned_20260424_041152_708983.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "52FB7A16E8DEDEB1", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 0061025bbac9c589... → 52FB7A16E8DEDEB1...\n✅ Key verification PASSED — all 8 bytes match."}`


---

### Round 12 | tokens: 24,818→118

**🤖 LLM:** 完美！密钥验证成功！让我再验证几条其他trace确保正确：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "DES",
  "ciphertext_npy": "ciphertext_aligned_20260424_041152_708983.npy",
  "key_hex": "1022324454667688",
  "plaintext_npy": "plaintext_aligned_20260424_041152_708983.npy",
  "trace_index": 1
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "11B89E09D008F102", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 53a4ddf212b24305... → 11B89E09D008F102...\n✅ Key verification PASSED — all 8 bytes match."}`


---

### Round 13 | tokens: 25,009→90

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "DES",
  "ciphertext_npy": "ciphertext_aligned_20260424_041152_708983.npy",
  "key_hex": "1022324454667688",
  "plaintext_npy": "plaintext_aligned_20260424_041152_708983.npy",
  "trace_index": 2
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "B84D6F9FC5E4FFF5", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 1fcd889399dcf666... → B84D6F9FC5E4FFF5...\n✅ Key verification PASSED — all 8 bytes match."}`


---

### Round 14 | tokens: 25,188→1,056

**🤖 LLM:** 完美！所有验证都通过了。让我生成最终的分析报告：

**🔧 → `python_jupyter`**

<details><summary>Code (2334 chars)</summary>

```python
import json

# 生成最终报告
report = """
================================================================================
                    DES-7816 接触式智能卡 CPA攻击报告
================================================================================

【攻击配置】
• 算法: DES-64 (ECB模式)
• 设备: 接触式智能卡 (ISO 7816)
• 波形数量: 100条 (2000采样点/条)
• 攻击方法: CPA (Correlation Power Analysis)
• 泄漏模型: Hamming Weight (HW)
• 攻击目标: S-box Output (第一轮)

【分析流程】
1. 第一次CPA探测 (无对齐)
   - 高置信度S-box: 2/8 (红色区域)
   - 平均相关性: 0.423
   - 问题: 各S-box时间索引差异大 (165-1681)，存在对齐问题

2. 静态对齐
   - 对齐区域: 1100-1220 (方差峰值区域)
   - max_shift: 200 (根据峰值位置变化范围调整)
   - 接受率: 91% (91/100条波形)
   - 对齐相关性: 0.9729

3. 对齐后CPA攻击
   - 高置信度S-box: 8/8 (绿色区域) ✓
   - 平均相关性: 0.7413 (显著提升)
   - 所有S-box gap > 15%

4. 密钥搜索与验证
   - 搜索轮次: 245
   - 搜索空间: 256
   - 验证结果: ✓ MATCH (多条trace验证通过)

【恢复密钥】
• 十六进制: 1022324454667688
• 二进制: 00010000 00100010 00110010 01000100 01010100 01100110 01110110 10001000

【各S-box攻击详情】
S-box | Key  | Correlation | Gap (%) | Time Index | Status
------|------|-------------|---------|------------|--------
  0   | 0x18 |   0.7861    |  41.2   |   1078     | ✓ High
  1   | 0x13 |   0.6520    |  31.8   |   1171     | ✓ High
  2   | 0x08 |   0.7474    |  39.4   |   1279     | ✓ High
  3   | 0x08 |   0.7814    |  31.1   |   1370     | ✓ High
  4   | 0x05 |   0.8242    |  26.3   |   1476     | ✓ High
  5   | 0x32 |   0.7125    |  35.5   |   1568     | ✓ High
  6   | 0x2B |   0.7583    |  42.7   |   1675     | ✓ High
  7   | 0x02 |   0.6684    |  22.4   |   1767     | ✓ High

【关键成功因素】
1. ✓ 正确识别加密区域 (方差峰值分析)
2. ✓ 根据实际峰值变化范围调整max_shift (50→200)
3. ✓ 使用静态对齐消除时间偏移
4. ✓ 高接受率对齐 (91%) 保证足够trace数量
5. ✓ 使用key_search处理DES奇偶校验位问题

【文件输出】
• 对齐后波形: aligned_20260424_041152_708983.npy
• 对齐后明文: plaintext_aligned_20260424_041152_708983.npy
• 对齐后密文: ciphertext_aligned_20260424_041152_708983.npy
• CPA结果图: des_cpa_result_20260424_041159_438015.png
• CPA详情: des_cpa_detail_20260424_041159_438015.json
• 对齐叠加图: align_overlay_20260424_041152_708983.png

================================================================================
                              攻击成功！
================================================================================
"""

print(report)

# 保存报告
with open('attack_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print("\n报告已保存至: attack_report.txt")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (2182 chars)</summary>

```
================================================================================
                    DES-7816 接触式智能卡 CPA攻击报告
================================================================================

【攻击配置】
• 算法: DES-64 (ECB模式)
• 设备: 接触式智能卡 (ISO 7816)
• 波形数量: 100条 (2000采样点/条)
• 攻击方法: CPA (Correlation Power Analysis)
• 泄漏模型: Hamming Weight (HW)
• 攻击目标: S-box Output (第一轮)

【分析流程】
1. 第一次CPA探测 (无对齐)
   - 高置信度S-box: 2/8 (红色区域)
   - 平均相关性: 0.423
   - 问题: 各S-box时间索引差异大 (165-1681)，存在对齐问题

2. 静态对齐
   - 对齐区域: 1100-1220 (方差峰值区域)
   - max_shift: 200 (根据峰值位置变化范围调整)
   - 接受率: 91% (91/100条波形)
   - 对齐相关性: 0.9729

3. 对齐后CPA攻击
   - 高置信度S-box: 8/8 (绿色区域) ✓
   - 平均相关性: 0.7413 (显著提升)
   - 所有S-box gap > 15%

4. 密钥搜索与验证
   - 搜索轮次: 245
   - 搜索空间: 256
   - 验证结果: ✓ MATCH (多条trace验证通过)

【恢复密钥】
• 十六进制: 1022324454667688
• 二进制: 00010000 00100010 00110010 01000100 01010100 01100110 01110110 10001000

【各S-box攻击详情】
S-box | Key  | Correlation | Gap (%) | Time Index | Status
------|------|-------------|---------|------------|--------
  0   | 0x18 |   0.7861    |  41.2   |   1078     | ✓ High
  1   | 0x13 |   0.6520    |  31.8   |   1171     | ✓ High
  2   | 0x08 |   0.7474    |  39.4   |   1279     | ✓ High
  3   | 0x08 |   0.7814    |  31.1   |   1370     | ✓ High
  4   | 0x05 |   0.8242    |  26.3   |   1476     | ✓ High
  5   | 0x32 |   0.7125    |  35.5   |   1568     | ✓ High
  6   | 0x2B |   0.7583    |  42.7   |   1675     | ✓ High
  7   | 0x02 |   0.6684    |  22.4   |   1767     | ✓ High

【关键成功
...(truncated)
```
</details>


---

### Round 15 | tokens: 27,203→390

**🤖 LLM:** ## 🎉 攻击成功完成！

### 📊 攻击总结

**恢复的DES密钥：`1022324454667688`**

### 🔍 关键分析步骤

1. **第一次CPA探测**（无对齐）
   - 结果：2/8 高置信度S-box（红色区域）
   - 问题：时间索引差异大（165-1681），存在严重对齐问题

2. **静态对齐优化**
   - 通过方差分析定位加密区域（1100-1220）
   - 根据实际峰值变化范围调整max_shift（50→200）
   - 达到91%接受率（91/100条波形）

3. **对齐后CPA攻击**
   - 结果：**8/8 高置信度S-box**（绿色区域）✓
   - 平均相关性从0.423提升到**0.7413**
   - 所有S-box gap > 15%

4. **密钥搜索与验证**
   - 使用key_search处理DES奇偶校验位问题
   - 245轮搜索找到正确密钥
   - 多条trace验证全部通过 ✓

### 💡 成功关键因素

- ✅ 正确识别加密区域（方差峰值分析）
- ✅ 数据驱动的参数调整（max_shift根据实际变化范围）
- ✅ 高质量对齐（91%接受率 + 0.97对齐相关性）
- ✅ 使用key_search处理DES密钥特殊性

### 📁 输出文件

所有分析结果已保存在会话目录中，包括：
- 对齐后的波形/明文/密文文件
- CPA攻击结果图和详情JSON
- 完整分析报告（attack_report.txt）


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 17,064 | 776 | 17,840 |
| 2 | 18,174 | 847 | 19,021 |
| 3 | 19,367 | 362 | 19,729 |
| 4 | 20,512 | 508 | 21,020 |
| 5 | 21,061 | 407 | 21,468 |
| 6 | 21,500 | 538 | 22,038 |
| 7 | 22,044 | 277 | 22,321 |
| 8 | 22,464 | 134 | 22,598 |
| 9 | 23,209 | 216 | 23,425 |
| 10 | 23,650 | 315 | 23,965 |
| 11 | 24,628 | 126 | 24,754 |
| 12 | 24,818 | 118 | 24,936 |
| 13 | 25,009 | 90 | 25,099 |
| 14 | 25,188 | 1,056 | 26,244 |
| 15 | 27,203 | 390 | 27,593 |
| **Total** | **335,891** | **6,160** | **342,051** |

## 8. Final Output

## 🎉 攻击成功完成！

### 📊 攻击总结

**恢复的DES密钥：`1022324454667688`**

### 🔍 关键分析步骤

1. **第一次CPA探测**（无对齐）
   - 结果：2/8 高置信度S-box（红色区域）
   - 问题：时间索引差异大（165-1681），存在严重对齐问题

2. **静态对齐优化**
   - 通过方差分析定位加密区域（1100-1220）
   - 根据实际峰值变化范围调整max_shift（50→200）
   - 达到91%接受率（91/100条波形）

3. **对齐后CPA攻击**
   - 结果：**8/8 高置信度S-box**（绿色区域）✓
   - 平均相关性从0.423提升到**0.7413**
   - 所有S-box gap > 15%

4. **密钥搜索与验证**
   - 使用key_search处理DES奇偶校验位问题
   - 245轮搜索找到正确密钥
   - 多条trace验证全部通过 ✓

### 💡 成功关键因素

- ✅ 正确识别加密区域（方差峰值分析）
- ✅ 数据驱动的参数调整（max_shift根据实际变化范围）
- ✅ 高质量对齐（91%接受率 + 0.97对齐相关性）
- ✅ 使用key_search处理DES密钥特殊性

### 📁 输出文件

所有分析结果已保存在会话目录中，包括：
- 对齐后的波形/明文/密文文件
- CPA攻击结果图和详情JSON
- 完整分析报告（attack_report.txt）
