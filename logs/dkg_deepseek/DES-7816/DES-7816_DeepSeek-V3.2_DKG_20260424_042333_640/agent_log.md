# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_042333_640 |
| Duration | 221.8s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_DSv3.2\DES-7816_DeepSeek-V3.2_DKG_20260424_042333_640` |
| Total LLM Calls | 12 |
| First Round | prompt: 15,831, completion: 713 |
| Last Round | prompt: 24,416, completion: 412 |
| Total Tokens | 249,996 (prompt: 245,386, completion: 4,610) |

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

LLM Response: ["DES", "Contact Smartcard", "Power", "CPA", "Hamming Weight", "S-box Output"]

Parsed Keywords: `["DES", "Contact Smartcard", "Power", "CPA", "Hamming Weight", "S-box Output"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 38763 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (41031 chars, click to expand)</summary>

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

**Search keywords** (6): DES, Contact Smartcard, Power, CPA, Hamming Weight, S-box Output

**Summary**: 31 upper entities, 28 relationships, 16 diagnostic chains, 14 strategies


## 1. Upper Layer Entities (31)


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

### Pipeline (8)

- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.

### StatMethod (7)

- **Compare hypothetical power consumption with measured traces** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Generate Hamming weight models for S-box output** — type=non_profiled

## 2. Relationships (28)

- `Algorithm:3DES` —[has_attack_point [source_text=first round S-box output, support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `AttackPoint:S-box output`
- `Algorithm:3DES` —[works_with [source_text=3DES was implemented on the smartcard., support_count=1, confidence=0.2, source_papers=["PAP-86-2009-ePrint-Kasper-EM-Attack-Contactless"]]]→ `DeviceClass:Commercial Contactless Smartcard`
- `Algorithm:3DES` —[strategy_applies_to [source_text=The process to perform a DEMA of the 3DES implementation can be split up into the following steps, applicability=general, source_papers=["PAP-86"]]]→ `Strategy:DEMA on RFID Smartcard - Core Steps`
- `DeviceClass:Contact DES Test Card` —[works_with [source_text=使用该DES卡一阶CPA分析, support_count=1, confidence=0.2, source_papers=["MAN-02-2024-MathMagic-DES-Contact-TestCard-Example"]]]→ `TraceType:Power`
- `DeviceClass:Contact DES Test Card` —[works_with [source_text=接触式DES测试卡测评示例, support_count=1, confidence=0.2, source_papers=["MAN-02-2024-MathMagic-DES-Contact-TestCard-Example"]]]→ `Preprocessing:Known-key Correlation Analysis`
- `DeviceClass:Contact Smartcard with 16-bit RISC CPU` —[works_with [source_text=Attack on the Blinded Lookup Table Implementation, support_count=1, confidence=0.2, source_papers=["PAP-103-2011-CHES-Clavier-Improved-CollisionCorr-Masked-AES"]]]→ `StatMethod:Collision-Correlation Attack`
- `DeviceClass:Contact Smartcard with 16-bit RISC CPU` —[works_with [source_text=Attack on the Blinded Lookup Table Implementation, support_count=1, confidence=0.2, source_papers=["PAP-103-2011-CHES-Clavier-Improved-CollisionCorr-Masked-AES"]]]→ `Algorithm:AES`
- `DeviceClass:Contact Smartcard with 16-bit RISC CPU` —[acquires_via [source_text=proprietary simulation tool, support_count=1, confidence=0.2, source_papers=["PAP-103-2011-CHES-Clavier-Improved-CollisionCorr-Masked-AES"]]]→ `TraceType:Simulated Power`
- `DeviceClass:Contact Smartcard with 16-bit RISC CPU` —[acquires_via [source_text=MicroPross MP100 reader and Lecroy WavePro oscilloscope, support_count=1, confidence=0.2, source_papers=["PAP-103-2011-CHES-Clavier-Improved-CollisionCorr-Masked-AES"]]]→ `TraceType:Power`
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

## 3. Diagnostic Chains (16)


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

### ⭐ • [canonical_pipeline_principle] Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)
- **Trigger**: Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap)
- **Rationale**: The first plaintext/ciphertext correlation band is usually the I/O bus or register write before the round starts. It correlates strongly and aligns cleanly but contains no S-box leakage, so when variance and correlation ROIs are disjoint the variance peak is the encryption body and must be preferred.
- **Content**: [{"principle": "When variance-based ROI exploration and plaintext/ciphertext-correlation analysis disagree on the encryption-region location (disjoint candidate intervals), the agent MUST anchor static_aligner on the VARIANCE-peak region, NOT the first plaintext/ciphertext-correlation band. This is a device-agnostic rule that extends Strategy A's variance-first principle (originally software MCU o
- **Applies to**: StatMethod:CPA, Preprocessing:Static Alignment

### ⭐ • [canonical_pipeline_principle] Software implementation: variance-first ROI exploration before alignment
- **Trigger**: Software cryptographic implementation (any MCU: STM32F1/F4/Cortex/AVR/Arduino; or contact smartcard running software crypto) + non-profiled CPA + direct CPA returns unstable high_confidence_count below empirical_threshold
- **Rationale**: A software trace contains plaintext I/O, key-schedule computation, and the encryption rounds. Only the round body carries S-box leakage, and it shows a distinct per-sample variance increase, so variance-based ROI selection is more reliable than aligning the whole trace first.
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
All files for this session are stored in: ..\logs\exp3_DSv3.2\DES-7816_DeepSeek-V3.2_DKG_20260424_042333_640
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_DSv3.2\DES-7816_DeepSeek-V3.2_DKG_20260424_042333_640/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 15,831→713

**🤖 LLM:** 我将帮您对接触式智能卡实现的DES算法进行CPA密钥恢复。首先，让我检查数据的基本情况。

**🔧 → `python_jupyter`**

<details><summary>Code (1696 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
plaintext_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy'
ciphertext_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy'
wave_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy'

plaintext = np.load(plaintext_path)
ciphertext = np.load(ciphertext_path)
wave = np.load(wave_path)

print(f"Plaintext shape: {plaintext.shape}, dtype: {plaintext.dtype}")
print(f"Ciphertext shape: {ciphertext.shape}, dtype: {ciphertext.dtype}")
print(f"Wave shape: {wave.shape}, dtype: {wave.dtype}")

# 检查前几个明文和密文
print(f"\nFirst 3 plaintexts (hex):")
for i in range(3):
    print(f"  Trace {i}: {plaintext[i].tobytes().hex()}")

print(f"\nFirst 3 ciphertexts (hex):")
for i in range(3):
    print(f"  Trace {i}: {ciphertext[i].tobytes().hex()}")

# 绘制前几条波形
plt.figure(figsize=(12, 6))
for i in range(5):
    plt.plot(wave[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('First 5 Power Traces')
plt.legend()
plt.grid(True)
plt.savefig('first_5_traces.png')
plt.show()

# 计算波形统计信息
print(f"\nWave statistics:")
print(f"  Mean: {np.mean(wave):.2f}")
print(f"  Std: {np.std(wave):.2f}")
print(f"  Min: {np.min(wave):.2f}")
print(f"  Max: {np.max(wave):.2f}")

# 检查波形是否有明显的基线漂移
baseline_region = wave[:, :100]  # 前100个样本作为基线区域
baseline_std = np.std(baseline_region, axis=1)
print(f"\nBaseline std (first 100 samples): mean={np.mean(baseline_std):.4f}, max={np.max(baseline_std):.4f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (633 chars)</summary>

```
Plaintext shape: (100, 8), dtype: uint8
Ciphertext shape: (100, 8), dtype: uint8
Wave shape: (100, 2000), dtype: float32

First 3 plaintexts (hex):
  Trace 0: 0061025bbac9c589
  Trace 1: 53a4ddf212b24305
  Trace 2: 1fcd889399dcf666

First 3 ciphertexts (hex):
  Trace 0: 52fb7a16e8dedeb1
  Trace 1: 11b89e09d008f102
  Trace 2: b84d6f9fc5e4fff5

Wave statistics:
  Mean: -5.94
  Std: 31.10
  Min: -98.43
  Max: 90.55

Baseline std (first 100 samples): mean=25.0917, max=32.1423
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\4231001202.py:36: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 2 | tokens: 16,830→323

**🤖 LLM:** 数据已加载：100条DES加密轨迹，每条2000个采样点。明文和密文都是8字节（64位）。从波形图看，有明显的加密活动区域。基线标准差较大（平均25.09），但这是接触式智能卡，根据知识图谱中的策略"Software implementations do NOT need vertical alignment by default"，我应该先不进行垂直对齐。

现在按照统一分析流程，首先进行第一次CPA探测（不进行对齐）：

**🔧 → `des_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy",
  "candidates": 20,
  "leakage_model": "HW",
  "target": "S-box_out"
}
```
</details>

<details><summary><b>📋 ← `des_cpa_attack`</b> (2024 chars)</summary>

```
{"recovered_key": "C044F6082640244E", "cpa_avg_correlation": 0.423, "cpa_min_correlation": 0.3904, "n_traces": 100, "target": "S-box_out", "plot_path": "des_cpa_result_20260424_042424_828246.png", "detail_file": "des_cpa_detail_20260424_042424_828246.json", "per_sbox": [{"sbox": 0, "key": "0x31", "correlation": 0.39037268317088836, "time_index": 1322, "gap_pct": 0.1}, {"sbox": 1, "key": "0x0B", "correlation": 0.4060454194444173, "time_index": 1681, "gap_pct": 4.8}, {"sbox": 2, "key": "0x11", "correlation": 0.4525161327273126, "time_index": 968, "gap_pct": 17.3}, {"sbox": 3, "key": "0x12", "correlation": 0.4719257426834791, "time_index": 165, "gap_pct": 20.0}, {"sbox": 4, "key": "0x2C", "correlation": 0.395343631928101, "time_index": 423, "gap_pct": 5.1}, {"sbox": 5, "key": "0x03", "correlation": 0.41651745844251536, "time_index": 1324, "gap_pct": 1.3}, {"sbox": 6, "key": "0x2D", "correlation": 0.44027035877131243, "time_index": 131, "gap_pct": 5.5}, {"sbox": 7, "key": "0x14", "correlation": 0.41088700159899666, "time_index": 1135, "gap_pct": 7.6}], "high_confidence_count": 2, "recovery_assessment": "Only 2/8 sboxes are high-confidence. Treat this as a red band case: revisit interval selection, start position, or target choice. For DES hardware HD (R_xor_LOut), avg_corr 0.05-0.08 can still be normal, so check gap distribution first.", "low_confidence_subkeys": [{"subkey_index": 0, "sbox": 0, "best_key_hex": "0x31", "top1_top2_gap": 0.0013423937504577297}, {"subkey_index": 1, "
...(truncated)
```
</details>


![des_cpa_result_20260424_042424_828246.png](./des_cpa_result_20260424_042424_828246.png)


---

### Round 3 | tokens: 18,025→378

**🤖 LLM:** 第一次CPA探测结果：恢复的密钥为`C044F6082640244E`，但只有2/8个S-box是高置信度的（红色带）。平均相关性0.423不错，但gap分布显示很多S-box的gap_pct很低（0.1%, 1.3%等）。根据知识图谱中的策略"Decision to perform static alignment based on direct CPA result"，对于DES，如果high_confidence_count < 5，需要进行对齐。

让我先验证这个恢复的密钥是否正确：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "C044F6082640244E",
  "algorithm": "DES",
  "mode": "ECB",
  "operation": "encrypt",
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

### Round 4 | tokens: 18,716→718

**🤖 LLM:** 密钥验证失败。根据知识图谱策略"Software implementation: variance-first ROI exploration before alignment"，我应该先进行方差分析来定位加密区域，然后再进行对齐。让我分析波形方差：

**🔧 → `python_jupyter`**

<details><summary>Code (1801 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载波形
wave = np.load('F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy')

# 计算方差和标准差
variance = np.var(wave, axis=0)
std_dev = np.std(wave, axis=0)

# 找到方差最大的区域
window_size = 50
variance_smoothed = np.convolve(variance, np.ones(window_size)/window_size, mode='same')

# 找到前几个峰值
from scipy.signal import find_peaks
peaks, properties = find_peaks(variance_smoothed, height=np.max(variance_smoothed)*0.3, distance=100)

print(f"Found {len(peaks)} peaks in variance:")
for i, peak in enumerate(peaks[:10]):
    print(f"  Peak {i}: sample {peak}, variance={variance_smoothed[peak]:.2f}")

# 绘制方差和标准差
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# 原始波形（平均）
axes[0].plot(np.mean(wave, axis=0))
axes[0].set_title('Average Power Trace')
axes[0].set_xlabel('Sample Index')
axes[0].set_ylabel('Amplitude')
axes[0].grid(True)

# 方差
axes[1].plot(variance, alpha=0.7, label='Variance')
axes[1].plot(variance_smoothed, 'r-', alpha=0.8, label=f'Smoothed (window={window_size})')
axes[1].plot(peaks, variance_smoothed[peaks], 'go', label='Peaks')
axes[1].set_title('Variance of Power Traces')
axes[1].set_xlabel('Sample Index')
axes[1].set_ylabel('Variance')
axes[1].legend()
axes[1].grid(True)

# 标准差
axes[2].plot(std_dev)
axes[2].set_title('Standard Deviation of Power Traces')
axes[2].set_xlabel('Sample Index')
axes[2].set_ylabel('Standard Deviation')
axes[2].grid(True)

plt.tight_layout()
plt.savefig('variance_analysis.png')
plt.show()

# 检查明文/密文相关性区域
print("\nVariance peaks (potential encryption regions):")
for i, peak in enumerate(peaks[:5]):
    start = max(0, peak - 50)
    end = min(len(variance), peak + 50)
    print(f"  Region {i}: samples {start}-{end} (center at {peak})")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (831 chars)</summary>

```
Found 16 peaks in variance:
  Peak 0: sample 25, variance=725.88
  Peak 1: sample 180, variance=727.86
  Peak 2: sample 304, variance=869.30
  Peak 3: sample 413, variance=949.10
  Peak 4: sample 537, variance=959.89
  Peak 5: sample 646, variance=976.66
  Peak 6: sample 762, variance=978.54
  Peak 7: sample 879, variance=995.01
  Peak 8: sample 1020, variance=1093.50
  Peak 9: sample 1120, variance=1351.15

Variance peaks (potential encryption regions):
  Region 0: samples 0-75 (center at 25)
  Region 1: samples 130-230 (center at 180)
  Region 2: samples 254-354 (center at 304)
  Region 3: samples 363-463 (center at 413)
  Region 4: samples 487-587 (center at 537)
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1408411174.py:52: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 5 | tokens: 19,750→275

**🤖 LLM:** 方差分析显示多个峰值区域。根据知识图谱策略"Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI"，我应该优先选择方差峰值区域作为对齐锚点。让我检查明文相关性分析：

**🔧 → `plaintext_ciphertext_correlation`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy",
  "data_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy",
  "data_type": "plaintext",
  "byte_index": 0,
  "model": "HW"
}
```
</details>

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 531, "peak_region_end": 535, "peak_time_index": 533, "peak_correlation": 0.3068, "suggested_cpa_range": [481, 585], "all_byte_peaks": [533, 1496, 1951, 1606, 1707, 1970, 1657, 1067], "byte_peaks_std": 450.8, "plot_path": "correlation_20260424_042528_766362.png"}`


![correlation_20260424_042528_766362.png](./correlation_20260424_042528_766362.png)


---

### Round 6 | tokens: 20,164→364

**🤖 LLM:** 明文相关性分析显示峰值在533附近，这与方差峰值537接近。根据知识图谱策略，我应该选择方差峰值区域作为对齐锚点。让我选择方差最大的区域（样本1020-1120附近）进行对齐：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy",
  "start": 1020,
  "length": 100,
  "max_shift": 200,
  "threshold": 85,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_042545_630556.npy", "plot_path": "align_overlay_20260424_042545_630556.png", "ref_trace_used": 50, "accepted": 91, "discarded": 9, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260424_042545_630556.npy", "plaintext_traces": 91, "out_ciphertext_npy": "ciphertext_aligned_20260424_042545_630556.npy", "ciphertext_traces": 91, "alignment_avg_correlation": 0.9804, "alignment_min_correlation": 0.9637, "acceptance_rate": 0.91}`


![align_overlay_20260424_042545_630556.png](./align_overlay_20260424_042545_630556.png)


---

### Round 7 | tokens: 20,726→178

**🤖 LLM:** 对齐成功！接受了91条轨迹（丢弃9条）。对齐平均相关性0.9804很高。现在对对齐后的轨迹进行CPA攻击：

**🔧 → `des_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_042545_630556.npy",
  "wave_npy": "aligned_20260424_042545_630556.npy",
  "candidates": 30,
  "leakage_model": "HW",
  "target": "S-box_out"
}`

<details><summary><b>📋 ← `des_cpa_attack`</b> (1551 chars)</summary>

```
{"recovered_key": "1002324454422688", "cpa_avg_correlation": 0.7676, "cpa_min_correlation": 0.6668, "n_traces": 91, "target": "S-box_out", "plot_path": "des_cpa_result_20260424_042557_933887.png", "detail_file": "des_cpa_detail_20260424_042557_933887.json", "per_sbox": [{"sbox": 0, "key": "0x18", "correlation": 0.8617003451471748, "time_index": 1801, "gap_pct": 44.9}, {"sbox": 1, "key": "0x13", "correlation": 0.6667593130323852, "time_index": 1178, "gap_pct": 32.1}, {"sbox": 2, "key": "0x08", "correlation": 0.7593009537557672, "time_index": 1279, "gap_pct": 38.1}, {"sbox": 3, "key": "0x08", "correlation": 0.77222562113302, "time_index": 1370, "gap_pct": 33.0}, {"sbox": 4, "key": "0x05", "correlation": 0.8532047955117916, "time_index": 1476, "gap_pct": 24.7}, {"sbox": 5, "key": "0x32", "correlation": 0.7274666415001141, "time_index": 1568, "gap_pct": 31.4}, {"sbox": 6, "key": "0x2B", "correlation": 0.7393060029109857, "time_index": 1675, "gap_pct": 40.7}, {"sbox": 7, "key": "0x02", "correlation": 0.7606609777239195, "time_index": 1774, "gap_pct": 32.2}], "high_confidence_count": 8, "recovery_assessment": "8/8 sboxes high-confidence (gap >= 15%). Only sboxes [] are unreliable. Run key_search to recover the master key (DES has 16-bit ambiguity from parity + PC-2 unselected bits). Do NOT switch target/method/alignment yet — for DES hardware HD (R_xor_LOut), avg_corr 0.05-0.08 is NORMAL baseline, not a failure signal.", "low_confidence_subkeys": [], "recommended_next_step": "most_
...(truncated)
```
</details>


![des_cpa_result_20260424_042557_933887.png](./des_cpa_result_20260424_042557_933887.png)


---

### Round 8 | tokens: 21,535→253

**🤖 LLM:** 太好了！对齐后的CPA结果显著改善：所有8个S-box都是高置信度的（gap_pct从24.7%到44.9%），平均相关性从0.423提高到0.7676。恢复的密钥是`1002324454422688`。现在验证这个密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "1002324454422688",
  "algorithm": "DES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_042545_630556.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_042545_630556.npy",
  "trace_index": 0
}`

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (996 chars)</summary>

```
{"result_hex": "748A23EF3BD3BE26", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 0061025bbac9c589... → 748A23EF3BD3BE26...\n❌ Key verification FAILED — 8/8 ciphertext bytes differ\n   Expected:  52FB7A16E8DEDEB1\n   Got:       748A23EF3BD3BE26\n\n   ⚠️ IMPORTANT: '8 ciphertext bytes differ' does NOT mean '8 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 9 | tokens: 22,110→302

**🤖 LLM:** 验证仍然失败，但根据知识图谱策略"key_search found=false is NOT CPA failure — escalate search budget + dual-mode both branches BEFORE pivoting any other dimension"，我应该先使用key_search工具。所有S-box都是高置信度的，但DES有奇偶校验位和PC-2未选择位的歧义。让我使用key_search：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "DES",
  "recovered_key_hex": "1002324454422688",
  "cpa_detail_file": "des_cpa_detail_20260424_042557_933887.json",
  "plaintext_npy": "plaintext_aligned_20260424_042545_630556.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_042545_630556.npy",
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 30,
  "max_combinations": 50000
}
```
</details>

<details><summary><b>📋 ← `key_search`</b> (1684 chars)</summary>

```
{"found": true, "correct_key": "1022324454667688", "search_rounds": 245, "total_search_space": 256, "sbox_analysis": [{"sbox": 0, "gap": 0.4493, "reliable": true, "top1": 24, "candidates": [24, 19, 26, 58, 17, 56, 15, 39, 7, 43, 16, 4, 34, 23, 13, 52, 55, 6, 14, 28, 36, 40, 53, 41, 46, 29, 33, 49, 57, 5]}, {"sbox": 1, "gap": 0.3212, "reliable": true, "top1": 19, "candidates": [19, 1, 4, 17, 14, 46, 18, 47, 31, 59, 36, 7, 39, 62, 6, 22, 58, 26, 13, 5, 49, 16, 35, 44, 21, 30, 57, 24, 11, 45]}, {"sbox": 2, "gap": 0.3811, "reliable": true, "top1": 8, "candidates": [8, 7, 4, 43, 42, 15, 9, 32, 33, 55, 0, 22, 39, 41, 5, 13, 63, 12, 11, 1, 6, 35, 59, 2, 56, 17, 37, 28, 16, 50]}, {"sbox": 3, "gap": 0.3304, "reliable": true, "top1": 8, "candidates": [8, 32, 48, 24, 17, 9, 23, 2, 37, 19, 4, 7, 28, 11, 33, 50, 1, 27, 13, 35, 20, 29, 42, 22, 12, 38, 21, 47, 25, 41]}, {"sbox": 4, "gap": 0.2469, "reliable": true, "top1": 5, "candidates": [5, 35, 0, 38, 51, 22, 21, 14, 54, 63, 16, 40, 50, 61, 1, 17, 45, 20, 60, 48, 11, 33, 34, 26, 18, 6, 57, 43, 46, 44]}, {"sbox": 5, "gap": 0.3142, "reliable": true, "top1": 50, "candidates": [50, 15, 34, 44, 4, 9, 58, 17, 45, 36, 43, 8, 61, 25, 7, 6, 16, 22, 24, 59, 0, 18, 10, 39, 27, 19, 1, 35, 12, 5]}, {"sbox": 6, "gap": 0.4075, "reliable": true, "top1": 43, "candidates": [43, 41, 61, 22, 21, 38, 56, 20, 53, 42, 44, 18, 24, 52, 39, 48, 15, 13, 27, 8, 2, 34, 6, 0, 50, 60, 31, 49, 55, 45]}, {"sbox": 7, "gap": 0.322, "reliable": true, "top1": 2, "candidates"
...(truncated)
```
</details>


---

### Round 10 | tokens: 23,481→212

**🤖 LLM:** 太好了！key_search找到了正确的密钥：`1022324454667688`。现在验证这个密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "1022324454667688",
  "algorithm": "DES",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_042545_630556.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_042545_630556.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "52FB7A16E8DEDEB1", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "DES-64-ECB encrypt: 0061025bbac9c589... → 52FB7A16E8DEDEB1...\n✅ Key verification PASSED — all 8 bytes match."}`


---

### Round 11 | tokens: 23,802→482

**🤖 LLM:** 完美！密钥验证成功。让我也检查其他几条轨迹以确保一致性：

**🔧 → `python_jupyter`**

<details><summary>Code (1382 chars)</summary>

```python
import numpy as np
from Crypto.Cipher import DES

# 加载对齐后的数据
plaintext = np.load('plaintext_aligned_20260424_042545_630556.npy')
ciphertext = np.load('ciphertext_aligned_20260424_042545_630556.npy')

# 正确的密钥
correct_key_hex = '1022324454667688'
correct_key_bytes = bytes.fromhex(correct_key_hex)

# 创建DES加密器
cipher = DES.new(correct_key_bytes, DES.MODE_ECB)

# 测试前5条轨迹
print("Testing first 5 traces with recovered key:")
for i in range(5):
    plain_bytes = bytes(plaintext[i])
    cipher_bytes = bytes(ciphertext[i])
    
    # 使用恢复的密钥加密
    encrypted = cipher.encrypt(plain_bytes)
    
    if encrypted == cipher_bytes:
        print(f"  Trace {i}: ✓ MATCH")
    else:
        print(f"  Trace {i}: ✗ MISMATCH")
        print(f"    Plaintext: {plain_bytes.hex()}")
        print(f"    Expected:  {cipher_bytes.hex()}")
        print(f"    Got:       {encrypted.hex()}")

print(f"\nSuccessfully recovered DES key: {correct_key_hex}")

# 分析密钥差异
original_recovered = bytes.fromhex('1002324454422688')
correct_key = bytes.fromhex('1022324454667688')

print("\nKey comparison:")
print(f"Original CPA recovered: {original_recovered.hex()}")
print(f"Correct key (after search): {correct_key.hex()}")

# 计算汉明距离
diff = bytes(a ^ b for a, b in zip(original_recovered, correct_key))
print(f"Bytes different: {diff.hex()}")
print(f"Number of different bytes: {sum(1 for b in diff if b != 0)}")
```
</details>

**📋 ← `python_jupyter`:** `Testing first 5 traces with recovered key:
  Trace 0: ✓ MATCH
  Trace 1: ✓ MATCH
  Trace 2: ✓ MATCH
  Trace 3: ✓ MATCH
  Trace 4: ✓ MATCH

Successfully recovered DES key: 1022324454667688

Key comparison:
Original CPA recovered: 1002324454422688
Correct key (after search): 1022324454667688
Bytes different: 0020000000245000
Number of different bytes: 3`


---

### Round 12 | tokens: 24,416→412

<details><summary><b>🤖 LLM Reasoning</b> (822 chars)</summary>

## 总结

成功恢复了接触式智能卡DES实现的密钥：`1022324454667688`

### 攻击过程分析：

1. **初始状态**：100条DES加密轨迹，每条2000个采样点
2. **第一次CPA探测**：使用S-box_out + HW模型，恢复密钥`C044F6082640244E`，但只有2/8个S-box是高置信度的（红色带）
3. **方差分析**：根据知识图谱策略"Software implementation: variance-first ROI exploration before alignment"，进行方差分析定位加密区域
4. **静态对齐**：选择方差峰值区域（样本1020）作为对齐锚点，接受91条轨迹，丢弃9条
5. **对齐后CPA**：结果显著改善，所有8个S-box都是高置信度，恢复密钥`1002324454422688`
6. **密钥搜索**：使用key_search工具，在245次搜索后找到正确密钥`1022324454667688`

### 关键成功因素：

1. **遵循知识图谱策略**：
   - 软件实现不默认进行垂直对齐
   - 方差优先的ROI探索
   - 对齐锚点选择方差峰值区域而非明文相关性区域
   - 在绿色带情况下使用key_search而非重新预处理

2. **技术细节**：
   - 初始CPA平均相关性：0.423 → 对齐后：0.7676
   - 高置信度S-box数量：2/8 → 8/8
   - 密钥差异：原始恢复密钥有3个字节错误，key_search成功纠正

3. **DES特性**：
   - DES密钥包含奇偶校验位（通常置0）
   - PC-2置换有未选择位，导致密钥恢复存在歧义
   - 需要key_search处理这些歧义

攻击成功验证了知识图谱中关于接触式智能卡DES CPA攻击的最佳实践策略。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 15,831 | 713 | 16,544 |
| 2 | 16,830 | 323 | 17,153 |
| 3 | 18,025 | 378 | 18,403 |
| 4 | 18,716 | 718 | 19,434 |
| 5 | 19,750 | 275 | 20,025 |
| 6 | 20,164 | 364 | 20,528 |
| 7 | 20,726 | 178 | 20,904 |
| 8 | 21,535 | 253 | 21,788 |
| 9 | 22,110 | 302 | 22,412 |
| 10 | 23,481 | 212 | 23,693 |
| 11 | 23,802 | 482 | 24,284 |
| 12 | 24,416 | 412 | 24,828 |
| **Total** | **245,386** | **4,610** | **249,996** |

## 8. Final Output

## 总结

成功恢复了接触式智能卡DES实现的密钥：`1022324454667688`

### 攻击过程分析：

1. **初始状态**：100条DES加密轨迹，每条2000个采样点
2. **第一次CPA探测**：使用S-box_out + HW模型，恢复密钥`C044F6082640244E`，但只有2/8个S-box是高置信度的（红色带）
3. **方差分析**：根据知识图谱策略"Software implementation: variance-first ROI exploration before alignment"，进行方差分析定位加密区域
4. **静态对齐**：选择方差峰值区域（样本1020）作为对齐锚点，接受91条轨迹，丢弃9条
5. **对齐后CPA**：结果显著改善，所有8个S-box都是高置信度，恢复密钥`1002324454422688`
6. **密钥搜索**：使用key_search工具，在245次搜索后找到正确密钥`1022324454667688`

### 关键成功因素：

1. **遵循知识图谱策略**：
   - 软件实现不默认进行垂直对齐
   - 方差优先的ROI探索
   - 对齐锚点选择方差峰值区域而非明文相关性区域
   - 在绿色带情况下使用key_search而非重新预处理

2. **技术细节**：
   - 初始CPA平均相关性：0.423 → 对齐后：0.7676
   - 高置信度S-box数量：2/8 → 8/8
   - 密钥差异：原始恢复密钥有3个字节错误，key_search成功纠正

3. **DES特性**：
   - DES密钥包含奇偶校验位（通常置0）
   - PC-2置换有未选择位，导致密钥恢复存在歧义
   - 需要key_search处理这些歧义

攻击成功验证了知识图谱中关于接触式智能卡DES CPA攻击的最佳实践策略。
