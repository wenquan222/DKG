# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_050136_994 |
| Duration | 503.7s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\SM4-7816_GLM5_DKG_20260424_050136_994` |
| Total LLM Calls | 39 |
| First Round | prompt: 15,512, completion: 720 |
| Last Round | prompt: 44,918, completion: 462 |
| Total Tokens | 1,285,977 (prompt: 1,268,377, completion: 17,600) |

## 3. User Query

```
帮我对一个接触式智能卡实现的SM4密码算法波形进行CPA恢复密钥，SM4需要分4轮分别做CPA恢复轮密钥，然后从4个轮密钥反推主密钥。明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个接触式智能卡实现的SM4密码算法波形进行CPA恢复密钥，SM4需要分4轮分别做CPA恢复轮密钥，然后从4个轮密钥反推主密钥。明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy'"

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
["SM4", "Contact Smartcard", "CPA", "Power", "Round Key", "Master Key", "Hamming Weight"]

Parsed Keywords: `["SM4", "Contact Smartcard", "CPA", "Power", "Round Key", "Master Key", "Hamming Weight"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 38756 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (41004 chars, click to expand)</summary>

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

**Search keywords** (7): SM4, Contact Smartcard, CPA, Power, Round Key, Master Key, Hamming Weight

**Summary**: 25 upper entities, 26 relationships, 17 diagnostic chains, 14 strategies


## 1. Upper Layer Entities (25)


### Algorithm (1)

- **SM4** — num_rounds=32, encryption_mode=ECB, key_length=128

### AttackPoint (1)

- **first add round key** — round=first

### DeviceClass (2)

- **Contact SM4 Test Card** — category=Smartcard
- **Contact Smartcard with 16-bit RISC CPU** — category=Smartcard, bus_width=16

### LeakageModel (5)

- **Hamming Weight** — requirements=software implementation
- **Hamming Weight (bit-based)** — requirements=bit-based
- **Hamming Weight of transitions**
- **Hamming weight**
- **Hamming weight of fused features**

### Pipeline (9)

- **Welch's t-test and PCA based chosen-plaintext power analysis** — source=paper, trigger_condition=when attacking hardware implementations of SM4 with power traces, applicable_scenarios=hardware implementations of block ciphers where traditional byte-wise attacks are difficult due to parallel operations
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, canonical_source=round1_patch_002, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values
- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.

### StatMethod (7)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **Compare hypothetical power consumption with measured traces** — type=non_profiled
- **Generate Hamming weight models for S-box output** — type=non_profiled

## 2. Relationships (26)

- `DeviceClass:Contact SM4 Test Card` —[works_with [source_text=对静态对齐后的波形进行已知密钥相关性分析, support_count=1, confidence=0.2, source_papers=["MAN-03-2024-MathMagic-SM4-Contact-TestCard-Example"]]]→ `Preprocessing:Static Alignment`
- `DeviceClass:Contact SM4 Test Card` —[acquires_via [source_text=接触式SM4测试卡测评示例, support_count=2, confidence=0.4, source_papers=["MAN-03-2024-MathMagic-SM4-Contact-TestCard-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `TraceType:Power`
- `DeviceClass:Contact SM4 Test Card` —[works_with [source_text=对泄露位置进行一阶CPA分析, support_count=2, confidence=0.4, source_papers=["MAN-03-2024-MathMagic-SM4-Contact-TestCard-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `StatMethod:CPA`
- `DeviceClass:Contact SM4 Test Card` —[works_with [source_text=对静态对齐后的波形进行已知密钥相关性分析, support_count=1, confidence=0.2, source_papers=["MAN-03-2024-MathMagic-SM4-Contact-TestCard-Example"]]]→ `Preprocessing:Known-key Correlation Analysis`
- `Algorithm:SM4` —[works_with [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `DeviceClass:Artix-7 FPGA on CW305 board`
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
- `AttackPoint:first add round key` —[works_with [source_text=then uses CPA on the unmasked first round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `StatMethod:CPA`
- `AttackPoint:first add round key` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `Algorithm:AES`
- `StatMethod:Generate Hamming weight models for S-box output` —[consists_of [parameters_note=models are lookup tables for the leakage of each possible S-box output, source_text=Generate Hamming weight models for S-box output, support_count=1, is_optional=False]]→ `Pipeline:SCALib CPA Attack on AES`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Avoid using the identity model for bijective S-boxes in MIA; use a non-bijective model (e.g., Hamming weight) or target a non-bijective intermediate value (e.g., predict only a subset of bits).`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:try different power models (bit, Hamming weight, Hamming distance, zero-value) to see which yields the highest and most distinct peak for a single key hypothesis`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:use the Hamming weight model for microcontrollers with precharged buses`
- `LeakageModel:Hamming Weight` —[relates_to [role=switch_component]]→ `Action:Use a non-injective leakage function that incurs information loss (e.g., Hamming weight, LSB, MSB).`

## 3. Diagnostic Chains (17)


### Obs: `leakage_model_selection` — any
- **Cause** (high): Selection function 2 (based on the two least significant bits of the intermediate value C0) provides a finer classification of traces, better utilizing the leakage information.
- **Check**: Experimental comparison: Function 2 succeeded with 500 traces, while Functions 1 and 3 required ~800 traces.
- **Action**: For attacking the first byte of the round key in SM4 hardware, use a selection function that classifies traces based on the two least significant bits of C0.
  - operation: `switch_component`
  - target: `leakage_model/selection_function`
  - strategy: Implement selection function: D = (C0 & 0x03), partitioning traces into 4 clusters based on the value of the two LSBs.

### Obs: `cpa_rounds` — any
- **Cause** (high): SM4 requires 4 rounds of CPA, each recovering 4 bytes of round key, then deriving the master key.
- **Action**: Perform 4-round CPA, using target S-box_out (or other) and adjusting wave_start/wave_end for each round.
  - operation: `adjust_param`
  - target: `cpa.rounds`
  - strategy: For SM4, plan for 4-round CPA with appropriate interval selection for each round.
- **Relates to**: StatMethod:`CPA`
- **Alternatives**: DPA, Difference of Means

### Obs: `cpa_high_confidence_count` — any
- **Cause** (high): Static alignment is not always necessary and may worsen results if aligned to wrong peak.
- **Action**: Perform direct CPA first. If high_confidence_count is in green band (AES≥13, DES≥6, SM4 per round≥3), skip static alignment.
  - operation: `skip_step`
  - target: `static_alignment`
  - strategy: Always try direct CPA before deciding to align.
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

### Obs: `cpa_avg_correlation` — any
- **Cause** (high): Hardware HD target naturally has low correlation, but the correct subkey may still be top-1.
- **Action**: Even with low correlation, if high_confidence_count is ≥6/8, CPA is successful and key_search can recover master key.
  - operation: `verify`
  - target: `cpa.high_confidence_count`
  - strategy: For hardware DES with HD target, focus on high_confidence_count rather than absolute correlation.
- **Relates to**: StatMethod:`CPA`
- **Alternatives**: DPA, Difference of Means

### Obs: `key_byte_distinguishability` — any
- **Cause** (high): Different key bytes (e.g., 0x55 and 0xAA) can have the same Hamming weight, making them indistinguishable if attacking the key directly. The S-box output provides a nonlinear transformation that spreads the Hamming weights, creating a unique signature for each key hypothesis.
- **Action**: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.
  - operation: `switch_component`
  - target: `attack point`
  - strategy: Target the output of the Inverse S-Box (or the combined InvSubBytesAndXOR operation) instead of the raw key byte.

### Obs: `attack_position_selection` — any
- **Cause** (high): The S-box output is a non-linear operation that often exhibits strong leakage in HW model, and is a common target in first-round attacks
- **Check**: Check implementation details for known leakage points
- **Action**: Set the target to 'S-box out' and model to 'HW' for first-round CPA on AES
  - operation: `adjust_param`
  - target: `cpa.target, cpa.model`
  - strategy: Target: S-box out, Model: HW
- **Relates to**: StatMethod:`CPA`

### Obs: `attack_method_selection` — any
- **Cause** (high): Different methods offer trade-offs in resource usage, noise sensitivity, and result quality
- **Action**: Select method based on priorities: Correlation for best trade-off, Linear Regression for best results (requires ID leakage model), Differential for lower resource usage
  - operation: `adjust_param`
  - target: `attack_method`
  - strategy: Correlation is recommended for general use; Linear Regression yields best results but is resource-intensive; Differential is more noise-sensitive but uses fewer resources.
- **Relates to**: StatMethod:`CPA`

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
All files for this session are stored in: ..\logs\exp3_GLM-5\SM4-7816_GLM5_DKG_20260424_050136_994
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\SM4-7816_GLM5_DKG_20260424_050136_994/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 15,512→720

**🤖 LLM:** 我来帮你对接触式智能卡的SM4实现进行CPA攻击。SM4确实需要分4轮分别攻击，每轮恢复4字节轮密钥，最后反推主密钥。

让我先检查数据的基本情况：

**🔧 → `python_jupyter`**

<details><summary>Code (672 chars)</summary>

```python
import numpy as np

# 加载数据
wave = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy')
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy')

print(f"波形数据形状: {wave.shape}")
print(f"明文数据形状: {plain.shape}")
print(f"密文数据形状: {cipher.shape}")
print(f"\n波形数据范围: [{wave.min():.4f}, {wave.max():.4f}]")
print(f"波形数据均值: {wave.mean():.4f}")
print(f"波形数据标准差: {wave.std():.4f}")
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (100, 6500)
明文数据形状: (100, 16)
密文数据形状: (100, 16)

波形数据范围: [-200.7874, 275.5905]
波形数据均值: -1.7929
波形数据标准差: 64.6314`


---

### Round 2 | tokens: 15,943→340

**🔧 → `python_jupyter`**

<details><summary>Code (900 chars)</summary>

```python
import matplotlib.pyplot as plt

# 可视化前几条波形
plt.figure(figsize=(14, 8))

# 绘制前5条波形
for i in range(5):
    plt.plot(wave[i] + i * 150, alpha=0.7, label=f'Trace {i}')

plt.xlabel('Sample Point', fontsize=12)
plt.ylabel('Power (offset for clarity)', fontsize=12)
plt.title('SM4 Power Traces (First 5 traces)', fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('waveform_overview.png', dpi=150)
plt.show()

# 计算方差来定位加密区域
variance = np.var(wave, axis=0)
plt.figure(figsize=(14, 4))
plt.plot(variance)
plt.xlabel('Sample Point', fontsize=12)
plt.ylabel('Variance', fontsize=12)
plt.title('Variance Across Traces', fontsize=14)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('variance_plot.png', dpi=150)
plt.show()

# 找到方差最大的区域
top_var_indices = np.argsort(variance)[-20:]
print(f"\n方差最大的20个采样点: {sorted(top_var_indices)}")
print(f"方差峰值位置: {np.argmax(variance)}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (659 chars)</summary>

```
方差最大的20个采样点: [np.int64(838), np.int64(839), np.int64(840), np.int64(1726), np.int64(1727), np.int64(1728), np.int64(2327), np.int64(3214), np.int64(3215), np.int64(3216), np.int64(4701), np.int64(4702), np.int64(4703), np.int64(4704), np.int64(5302), np.int64(5303), np.int64(6189), np.int64(6190), np.int64(6191), np.int64(6192)]
方差峰值位置: 6190
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2326044463.py:17: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2326044463.py:29: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 3 | tokens: 16,516→355

**🤖 LLM:** 现在让我开始SM4的CPA攻击。SM4需要分4轮进行，我先从第0轮开始：

**🔧 → `sm4_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy",
  "round_index": 0,
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (1254 chars)</summary>

```
{"round_index": 0, "recovered_round_key": "F1DE7733", "cpa_avg_correlation": 0.4676, "cpa_min_correlation": 0.4459, "target": "S-box_out", "n_traces": 100, "detail_file": "sm4_cpa_round0_detail_20260424_050301_884462.json", "per_byte": [{"byte": 0, "key": "0xF1", "correlation": 0.46296397927202204, "time_index": 6281}, {"byte": 1, "key": "0xDE", "correlation": 0.4458865551908085, "time_index": 3570}, {"byte": 2, "key": "0x77", "correlation": 0.4818867469130951, "time_index": 4596}, {"byte": 3, "key": "0x33", "correlation": 0.47957734129236296, "time_index": 1016}], "high_confidence_count": 0, "recovery_assessment": "Only 0/4 bytes are high-confidence in this round. Treat this as a red band case: relocalize the round window, revisit alignment, or switch target family.", "low_confidence_subkeys": [{"subkey_index": 0, "byte": 0, "best_key_hex": "0xF1", "top1_top2_gap": 0.015265620122222375}, {"subkey_index": 1, "byte": 1, "best_key_hex": "0xDE", "top1_top2_gap": 0.007089534995135141}, {"subkey_index": 2, "byte": 2, "best_key_hex": "0x77", "top1_top2_gap": 0.06683339575404913}, {"subkey_index": 3, "byte": 3, "best_key_hex": "0x33", "top1_top2_gap": 0.05163456712097791}], "recommended_next_step": "relocalize_round_window_or_switch_target"}
```
</details>


---

### Round 4 | tokens: 17,226→340

**🤖 LLM:** 第0轮CPA完成，相关性不错（0.4676），但高置信度字节数为0。让我继续第1轮：

**🔧 → `sm4_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy",
  "round_index": 1,
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20,
  "prev_round_keys": [
    "F1DE7733"
  ]
}
```
</details>

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (1252 chars)</summary>

```
{"round_index": 1, "recovered_round_key": "586CE653", "cpa_avg_correlation": 0.4565, "cpa_min_correlation": 0.4405, "target": "S-box_out", "n_traces": 100, "detail_file": "sm4_cpa_round1_detail_20260424_050314_026417.json", "per_byte": [{"byte": 0, "key": "0x58", "correlation": 0.4792521449973949, "time_index": 1121}, {"byte": 1, "key": "0x6C", "correlation": 0.4405010736801864, "time_index": 3352}, {"byte": 2, "key": "0xE6", "correlation": 0.45232132464957503, "time_index": 187}, {"byte": 3, "key": "0x53", "correlation": 0.45391280374562387, "time_index": 5025}], "high_confidence_count": 0, "recovery_assessment": "Only 0/4 bytes are high-confidence in this round. Treat this as a red band case: relocalize the round window, revisit alignment, or switch target family.", "low_confidence_subkeys": [{"subkey_index": 0, "byte": 0, "best_key_hex": "0x58", "top1_top2_gap": 0.07610838114487058}, {"subkey_index": 1, "byte": 1, "best_key_hex": "0x6C", "top1_top2_gap": 0.005885594639337034}, {"subkey_index": 2, "byte": 2, "best_key_hex": "0xE6", "top1_top2_gap": 0.0294430754829072}, {"subkey_index": 3, "byte": 3, "best_key_hex": "0x53", "top1_top2_gap": 0.021630762974847912}], "recommended_next_step": "relocalize_round_window_or_switch_target"}
```
</details>


---

### Round 5 | tokens: 17,963→216

**🤖 LLM:** 第1轮完成，继续第2轮：

**🔧 → `sm4_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "prev_round_keys": [
    "F1DE7733",
    "586CE653"
  ],
  "round_index": 2,
  "target": "S-box_out",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy"
}
```
</details>

**❌ ← `sm4_cpa_attack` Error:**

```
SM4 CPA Error: [Errno 2] No such file or directory: 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-7816/SM4-128-7816-100traces-6500points_plain.npy'
Traceback (most recent call last):
  File "C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3381600069.py", line 8, in <module>
    result = run_sm4_cpa(plaintext_npy="F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/SM4-7816/SM4-128-7816-100traces-6500points_plain.npy",wave_npy="F:/\u4fa7\u4fe1\u9053/SCA-GPT/\u5b9e\u9a8c\u4e94\uff1a\u57fa\u4e8e\u77e5\u8bc6\u56fe\u8c31\u7684Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy",round_index=2,candidates=20,leakage_model="HW",target="S-box_out",bytes_to_test=None,prev_round_keys=["F1DE7733", "586CE653"],wave_start=None,wave_end=None,corr_mode=None)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "F:\侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/agent/tools\sm4_cpa_tool.py", line 336, in run_sm4_cpa
    P = np.load(plaintext_npy)  # (n_traces, 16)
        ^^^^^^^^^^^^^^^^^^^^^^
  File "F:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\numpy\lib\_npyio_impl.py", line 454, in load
    fid = stack.enter_context(open(os.fspath(file), "rb"))
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-7816/SM4-128-7816-100traces-6500points_plain.npy'
```


---

### Round 6 | tokens: 18,946→208

**🤖 LLM:** 路径错误，让我修正：

**🔧 → `sm4_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "prev_round_keys": [
    "F1DE7733",
    "586CE653"
  ],
  "round_index": 2,
  "target": "S-box_out",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy"
}
```
</details>

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (1154 chars)</summary>

```
{"round_index": 2, "recovered_round_key": "D6AD46FA", "cpa_avg_correlation": 0.4785, "cpa_min_correlation": 0.4403, "target": "S-box_out", "n_traces": 100, "detail_file": "sm4_cpa_round2_detail_20260424_050330_842741.json", "per_byte": [{"byte": 0, "key": "0xD6", "correlation": 0.46086332431541005, "time_index": 71}, {"byte": 1, "key": "0xAD", "correlation": 0.4403076257054242, "time_index": 3546}, {"byte": 2, "key": "0x46", "correlation": 0.4850788423121152, "time_index": 5830}, {"byte": 3, "key": "0xFA", "correlation": 0.527642652157666, "time_index": 6479}], "high_confidence_count": 1, "recovery_assessment": "Only 1/4 bytes are high-confidence in this round. Treat this as a red band case: relocalize the round window, revisit alignment, or switch target family.", "low_confidence_subkeys": [{"subkey_index": 0, "byte": 0, "best_key_hex": "0xD6", "top1_top2_gap": 0.01721556325170591}, {"subkey_index": 1, "byte": 1, "best_key_hex": "0xAD", "top1_top2_gap": 0.02409889137886387}, {"subkey_index": 2, "byte": 2, "best_key_hex": "0x46", "top1_top2_gap": 0.08796535013442948}], "recommended_next_step": "relocalize_round_window_or_switch_target"}
```
</details>


---

### Round 7 | tokens: 19,608→223

**🤖 LLM:** 第2轮完成，继续第3轮：

**🔧 → `sm4_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "prev_round_keys": [
    "F1DE7733",
    "586CE653",
    "D6AD46FA"
  ],
  "round_index": 3,
  "target": "S-box_out",
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy"
}
```
</details>

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (1570 chars)</summary>

```
{"round_index": 3, "recovered_round_key": "14A67022", "cpa_avg_correlation": 0.4667, "cpa_min_correlation": 0.4516, "target": "S-box_out", "n_traces": 100, "detail_file": "sm4_cpa_round3_detail_20260424_050339_399560.json", "per_byte": [{"byte": 0, "key": "0x14", "correlation": 0.4604609334152263, "time_index": 1362}, {"byte": 1, "key": "0xA6", "correlation": 0.4515829107737944, "time_index": 3446}, {"byte": 2, "key": "0x70", "correlation": 0.4818003554654557, "time_index": 1264}, {"byte": 3, "key": "0x22", "correlation": 0.47307184764387056, "time_index": 3588}], "high_confidence_count": 0, "recovery_assessment": "Only 0/4 bytes are high-confidence in this round. Treat this as a red band case: relocalize the round window, revisit alignment, or switch target family.", "low_confidence_subkeys": [{"subkey_index": 0, "byte": 0, "best_key_hex": "0x14", "top1_top2_gap": 0.007383562853687652}, {"subkey_index": 1, "byte": 1, "best_key_hex": "0xA6", "top1_top2_gap": 0.030080138049498335}, {"subkey_index": 2, "byte": 2, "best_key_hex": "0x70", "top1_top2_gap": 0.06401698492033739}, {"subkey_index": 3, "byte": 3, "best_key_hex": "0x22", "top1_top2_gap": 0.012590744154372616}], "recommended_next_step": "relocalize_round_window_or_switch_target", "recovered_master_key": "3112E16E3B8A8FCFDE1C388C6CB9DE92", "master_key_math_consistent": true, "master_key_verification_note": "IMPORTANT: math_consistent=true only means rk0-rk3 are internally consistent with this master_key. It does NOT mean 
...(truncated)
```
</details>


---

### Round 8 | tokens: 20,425→341

**🤖 LLM:** 太好了！4轮CPA全部完成，工具自动反推出了主密钥。现在让我验证这个密钥是否正确：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "SM4",
  "key_hex": "3112E16E3B8A8FCFDE1C388C6CB9DE92",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "4A407F47BFF6212618863509F74AFC46", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "SM4-128-ECB encrypt: 15f172190435a0103048f7161a5f01fd... → 4A407F47BFF6212618863509F74AFC46...\n❌ Key verification FAILED — 14/16 ciphertext bytes differ\n   Expected:  169B73531B72211DE486EF3FC2830686\n   Got:       4A407F47BFF6212618863509F74AFC46\n\n   ⚠️ IMPORTANT: '14 ciphertext bytes differ' does NOT mean '14 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 9 | tokens: 20,996→429

**🤖 LLM:** 密钥验证失败，但这是正常的。SM4的扩散特性意味着即使只有1个字节错误，所有密文字节都会不同。让我使用key_search工具来搜索正确的密钥：

**🔧 → `key_search`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "SM4",
  "cpa_detail_file": "sm4_cpa_round0_detail_20260424_050301_884462.json",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy",
  "extra_cpa_detail_files": [
    "sm4_cpa_round1_detail_20260424_050314_026417.json",
    "sm4_cpa_round2_detail_20260424_050330_842741.json",
    "sm4_cpa_round3_detail_20260424_050339_399560.json"
  ],
  "gap_threshold": 0.15,
  "max_candidates_per_byte": 20,
  "max_combinations": 50000,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "recovered_key_hex": "3112E16E3B8A8FCFDE1C388C6CB9DE92"
}
```
</details>

**❌ ← `key_search` Error:**

```
---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mValueError[39m                                Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[309][39m[32m, line 7[39m
[32m      5[39m [38;5;28;01mimport[39;00m[38;5;250m [39m[34;01mjson[39;00m[38;5;250m [39m[38;5;28;01mas[39;00m[38;5;250m [39m[34;01m_json[39;00m
[32m      6[39m [38;5;28;01mfrom[39;00m[38;5;250m [39m[34;01mkey_search_tool[39;00m[38;5;250m [39m[38;5;28;01mimport[39;00m run_key_search
[32m----> [39m[32m7[39m result = [43mrun_key_search[49m[43m([49m
[32m      8[39m [43m    [49m[43malgorithm[49m[43m=[49m[33;43m"[39;49m[33;43mSM4[39;49m[33;43m"[39;49m[43m,[49m
[32m      9[39m [43m    [49m[43mrecovered_key_hex[49m[43m=[49m[33;43m"[39;49m[33;43m3112E16E3B8A8FCFDE1C388C6CB9DE92[39;49m[33;43m"[39;49m[43m,[49m
[32m     10[39m [43m    [49m[43mcpa_detail_file[49m[43m=[49m[33;43m"[39;49m[33;43msm4_cpa_round0_detail_20260424_050301_884462.json[39;49m[33;43m"[39;49m[43m,[49m
[32m     11[39m [43m    [49m[43mplaintext_npy[49m[43m=[49m[33;43m"[39;49m[33;43mF:/[39;49m[38;5;130;43;01m\u4fa7[39;49;00m[38;5;130;43;01m\u4fe1[39;49;00m[38;5;130;43;01m\u9053[39;49;00m[33;43m/SCA-GPT/[39;49m[38;5;130;43;01m\u5b9e[39;49;00m[38;5;130;43;01m\u9a8c[39;49;00m[38;5;130;43;01m\u4e94[39;49;00m[38;5;130;43;01m\uff1a[39;49;00m[38;5;130;43;01m\u57fa[39;49;00m[38;5;130;43;01m\u4e8e[39;49;00m[38;5;130;43;01m\u77e5[39;49;00m[38;5;130;43;01m\u8bc6[39;49;00m[38;5;130;43;01m\u56fe[39;49;00m[38;5;130;43;01m\u8c31[39;49;00m[38;5;130;43;01m\u7684[39;49;00m[33;43mAgent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy[39;49m[33;43m"[39;49m[43m,[49m
[32m     12[39m [43m    [49m[43mciphertext_npy[49m[43m=[49m[33;43m"[39;49m[33;43mF:/[39;49m[38;5;130;43;01m\u4fa7[39;49;00m[38;5;130;43;01m\u4fe1[39;49;00m[38;5;130;43;01m\u9053[39;49;00m[33;43m/SCA-GPT/[39;49m[38;5;130;43;01m\u5b9e[39;49;00m[38;5;130;43;01m\u9a8c[39;49;00m[38;5;130;43;01m\u4e94[39;49;00m[38;5;130;43;01m\uff1a[39;49;00m[38;5;130;43;01m\u57fa[39;49;00m[38;5;130;43;01m\u4e8e[39;49;00m[38;5;130;43;01m\u77e5[39;49;00m[38;5;130;43;01m\u8bc6[39;49;00m[38;5;130;43;01m\u56fe[39;49;00m[38;5;130;43;01m\u8c31[39;49;00m[38;5;130;43;01m\u7684[39;49;00m[33;43mAgent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy[39;49m[33;43m"[39;49m[43m,[49m
[32m     13[39m [43m    [49m[43mgap_threshold[49m[43m=[49m[32;43m0.15[39;49m[43m,[49m
[32m     14[39m [43m    [49m[43mmax_candidates_per_byte[49m[43m=[49m[32;43m20[39;49m[43m,[49m
[32m     15[39m [43m    [49m[43mmax_combinations[49m[43m=[49m[32;43m50000[39;49m[43m,[49m
[32m     16[39m [43m    [49m[43mextra_cpa_detail_files[49m[43m=[49m[43m[[49m[33;43m"[39;49m[33;43msm4_cpa_round1_detail_20260424_050314_026417.json[39;49m[33;43m"[39;49m[43m,[49m[43m [49m[33;43m"[39;49m[33;43msm4_cpa_round2_detail_20260424_050330_842741.json[39;49m[33;43m"[39;49m[43m,[49m[43m [49m[33;43m"[39;49m[33;43msm4_cpa_round3_detail_20260424_050339_399560.json[39;49m[33;43m"[39;49m[43m][49m
[32m     17[39m [43m)[49m
[32m     18[39m [38;5;28mprint[39m(_json.dumps(result, ensure_ascii=[38;5;28;01mFalse[39;00m))

[36mFile [39m[32mF:\侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/agent/tools\key_search_tool.py:284[39m, in [36mrun_key_search[39m[34m(algorithm, recovered_key_hex, cpa_detail_file, plaintext_npy, ciphertext_npy, gap_threshold, max_candidates_per_byte, max_combinations, extra_cpa_detail_files)[39m
[32m    281[39m [38;5;28;01mif[39;00m extra_cpa_detail_files:
[32m    282[39m     file_list.extend(extra_cpa_detail_files)
[32m--> [39m[32m284[39m results, merge_info = [43m_load_and_merge_cpa_details[49m[43m([49m[43mfile_list[49m[43m)[49m
[32m    286[39m [38;5;28;01mif[39;00m algo == [33m"[39m[33mDES[39m[33m"[39m:
[32m    287[39m     out = _des_search(results, pt, ct, gap_threshold, max_candidates_per_byte, max_combinations)

[36mFile [39m[32mF:\侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/agent/tools\key_search_tool.py:176[39m, in [36m_load_and_merge_cpa_details[39m[34m(file_list)[39m
[32m    174[39m     cur_val = meta.get(field)
[32m    175[39m     [38;5;28;01mif[39;00m ref_val [38;5;129;01mis[39;00m [38;5;129;01mnot[39;00m [38;5;28;01mNone[39;00m [38;5;129;01mand[39;00m cur_val [38;5;129;01mis[39;00m [38;5;129;01mnot[39;00m [38;5;28;01mNone[39;00m [38;5;129;01mand[39;00m ref_val != cur_val:
[32m--> [39m[32m176[39m         [38;5;28;01mraise[39;00m [38;5;167;01mValueError[39;00m(
[32m    177[39m             [33mf[39m[33m"[39m[33mIncompatible CPA detail files: [39m[38;5;132;01m{[39;00mfield[38;5;132;01m}[39;00m[33m mismatch be
...(truncated)
```


---

### Round 10 | tokens: 24,484→4,060

**🤖 LLM:** key_search工具不支持合并不同轮次的SM4 CPA结果。让我手动实现SM4的密钥搜索：

**🔧 → `python_jupyter`**

<details><summary>Code (7221 chars)</summary>

```python
import json
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# SM4 implementation (Python)
def sm4_sbox(b):
    """SM4 S-box"""
    SBOX = [
        0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
        0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99,
        0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed, 0xcf, 0xac, 0x62,
        0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa, 0x75, 0x8f, 0x3f, 0xa6,
        0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c, 0x19, 0xe6, 0x85, 0x4f, 0xa8,
        0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb, 0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35,
        0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25, 0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87,
        0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52, 0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e,
        0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38, 0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1,
        0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34, 0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3,
        0x1d, 0xf6, 0xe3, 0x92, 0xab, 0x79, 0x6c, 0x2e, 0x9c, 0x74, 0x28, 0x51, 0x85, 0x3c, 0x81, 0x6f,
        0x1b, 0x47, 0x62, 0x0a, 0x19, 0x89, 0xaf, 0x13, 0x81, 0x7d, 0x59, 0xd7, 0x86, 0x3e, 0x62, 0xd9,
        0x30, 0x89, 0x49, 0x67, 0x76, 0xb5, 0x98, 0x05, 0x6a, 0x78, 0xf7, 0x84, 0x67, 0x72, 0x36, 0x5f,
        0x38, 0x09, 0x54, 0xab, 0x8d, 0x2c, 0x4e, 0x40, 0xa3, 0x0e, 0x19, 0xae, 0x5b, 0x5a, 0x76, 0x49,
        0x8c, 0x0d, 0xb5, 0xf0, 0x7c, 0x9b, 0x25, 0x8d, 0x35, 0x7e, 0xc8, 0x05, 0x45, 0x49, 0x2b, 0x1d,
        0x0a, 0xbe, 0x0e, 0x24, 0x38, 0x2e, 0x1b, 0xa5, 0x4c, 0x93, 0x5a, 0x35, 0xcc, 0x4d, 0x01, 0x91
    ]
    return SBOX[b]

def sm4_l(b):
    """SM4 L linear transformation"""
    return b ^ ((b << 2) | (b >> 30)) & 0xFFFFFFFF ^ \
           ((b << 10) | (b >> 22)) & 0xFFFFFFFF ^ \
           ((b << 18) | (b >> 14)) & 0xFFFFFFFF ^ \
           ((b << 24) | (b >> 8)) & 0xFFFFFFFF

def sm4_l_prime(b):
    """SM4 L' linear transformation for key expansion"""
    return b ^ ((b << 13) | (b >> 19)) & 0xFFFFFFFF ^ \
           ((b << 23) | (b >> 9)) & 0xFFFFFFFF

def sm4_tau(a):
    """SM4 τ transformation (4 S-boxes)"""
    b0 = sm4_sbox((a >> 24) & 0xFF)
    b1 = sm4_sbox((a >> 16) & 0xFF)
    b2 = sm4_sbox((a >> 8) & 0xFF)
    b3 = sm4_sbox(a & 0xFF)
    return (b0 << 24) | (b1 << 16) | (b2 << 8) | b3

def sm4_t(a):
    """SM4 T transformation"""
    return sm4_l(sm4_tau(a))

def sm4_t_prime(a):
    """SM4 T' transformation for key expansion"""
    return sm4_l_prime(sm4_tau(a))

# SM4 key expansion
def sm4_key_expansion(key_bytes):
    """Expand 128-bit key to 32 round keys"""
    FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]
    CK = [
        0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
        0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
        0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
        0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
        0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
        0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
        0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
        0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
    ]
    
    # Initialize with FK
    K = [0] * 36
    for i in range(4):
        K[i] = int.from_bytes(key_bytes[i*4:(i+1)*4], 'big') ^ FK[i]
    
    # Generate round keys
    rk = []
    for i in range(32):
        K[i+4] = K[i] ^ sm4_t_prime(K[i+1] ^ K[i+2] ^ K[i+3] ^ CK[i])
        rk.append(K[i+4])
    
    return rk

# SM4 encryption
def sm4_encrypt_block(plaintext, rk):
    """Encrypt one 128-bit block"""
    # Split into 4 32-bit words
    X = [0] * 36
    for i in range(4):
        X[i] = int.from_bytes(plaintext[i*4:(i+1)*4], 'big')
    
    # 32 rounds
    for i in range(32):
        X[i+4] = X[i] ^ sm4_t(X[i+1] ^ X[i+2] ^ X[i+3] ^ rk[i])
    
    # Reverse order for output
    Y = X[35:31:-1]
    
    # Convert back to bytes
    ciphertext = b''
    for word in Y:
        ciphertext += word.to_bytes(4, 'big')
    
    return ciphertext

# Reverse key expansion: from rk0-rk3 to master key
def sm4_reverse_key_expansion(rk0, rk1, rk2, rk3):
    """Recover master key from first 4 round keys"""
    FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]
    CK = [0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269]
    
    # From rk[i] = K[i+4] = K[i] ^ T'(K[i+1] ^ K[i+2] ^ K[i+3] ^ CK[i])
    # We need to find K[0], K[1], K[2], K[3]
    # 
    # rk[0] = K[4] = K[0] ^ T'(K[1] ^ K[2] ^ K[3] ^ CK[0])
    # rk[1] = K[5] = K[1] ^ T'(K[2] ^ K[3] ^ K[4] ^ CK[1])
    # rk[2] = K[6] = K[2] ^ T'(K[3] ^ K[4] ^ K[5] ^ CK[2])
    # rk[3] = K[7] = K[3] ^ T'(K[4] ^ K[5] ^ K[6] ^ CK[3])
    #
    # This is a system of equations. We can solve it iteratively.
    
    # Actually, we can use the inverse relationship:
    # K[i] = rk[i] ^ T'(K[i+1] ^ K[i+2] ^ K[i+3] ^ CK[i])
    # But we don't know K[4], K[5], K[6], K[7] initially
    
    # Better approach: use the fact that K[4] = rk[0], K[5] = rk[1], etc.
    # Then work backwards:
    # K[3] = rk[3] ^ T'(K[4] ^ K[5] ^ K[6] ^ CK[3])
    # But we need K[6] which we don't have yet...
    
    # Actually, let's use a different approach:
    # We know K[4..7] = rk[0..3]
    # We can compute K[0..3] by reversing the key expansion
    
    K = [0] * 8
    K[4] = rk0
    K[5] = rk1
    K[6] = rk2
    K[7] = rk3
    
    # Reverse the key expansion
    # K[i] = K[i+4] ^ T'(K[i+1] ^ K[i+2] ^ K[i+3] ^ CK[i])
    # We need to solve this backwards
    
    # From K[7] = K[3] ^ T'(K[4] ^ K[5] ^ K[6] ^ CK[3])
    # => K[3] = K[7] ^ T'(K[4] ^ K[5] ^ K[6] ^ CK[3])
    K[3] = K[7] ^ sm4_t_prime(K[4] ^ K[5] ^ K[6] ^ CK[3])
    
    # From K[6] = K[2] ^ T'(K[3] ^ K[4] ^ K[5] ^ CK[2])
    # => K[2] = K[6] ^ T'(K[3] ^ K[4] ^ K[5] ^ CK[2])
    K[2] = K[6] ^ sm4_t_prime(K[3] ^ K[4] ^ K[5] ^ CK[2])
    
    # From K[5] = K[1] ^ T'(K[2] ^ K[3] ^ K[4] ^ CK[1])
    # => K[1] = K[5] ^ T'(K[2] ^ K[3] ^ K[4] ^ CK[1])
    K[1] = K[5] ^ sm4_t_prime(K[2] ^ K[3] ^ K[4] ^ CK[1])
    
    # From K[4] = K[0] ^ T'(K[1] ^ K[2] ^ K[3] ^ CK[0])
    # => K[0] = K[4] ^ T'(K[1] ^ K[2] ^ K[3] ^ CK[0])
    K[0] = K[4] ^ sm4_t_prime(K[1] ^ K[2] ^ K[3] ^ CK[0])
    
    # Now recover master key from K[0..3]
    # K[i] = MK[i] ^ FK[i]
    # => MK[i] = K[i] ^ FK[i]
    master_key = b''
    for i in range(4):
        mk_word = K[i] ^ FK[i]
        master_key += mk_word.to_bytes(4, 'big')
    
    return master_key

# Test the reverse key expansion
rk0 = 0xF1DE7733
rk1 = 0x586CE653
rk2 = 0xD6AD46FA
rk3 = 0x14A67022

master_key = sm4_reverse_key_expansion(rk0, rk1, rk2, rk3)
print(f"Recovered master key: {master_key.hex().upper()}")

# Verify by expanding the key
rk_test = sm4_key_expansion(master_key)
print(f"\nFirst 4 round keys from recovered master key:")
print(f"  rk[0] = 0x{rk_test[0]:08X} (expected: 0x{rk0:08X})")
print(f"  rk[1] = 0x{rk_test[1]:08X} (expected: 0x{rk1:08X})")
print(f"  rk[2] = 0x{rk_test[2]:08X} (expected: 0x{rk2:08X})")
print(f"  rk[3] = 0x{rk_test[3]:08X} (expected: 0x{rk3:08X})")
```
</details>

**📋 ← `python_jupyter`:** `Recovered master key: E474C0850AF01A57CF4892320620AA60

First 4 round keys from recovered master key:
  rk[0] = 0xF1DE7733 (expected: 0xF1DE7733)
  rk[1] = 0x586CE653 (expected: 0x586CE653)
  rk[2] = 0xD6AD46FA (expected: 0xD6AD46FA)
  rk[3] = 0x14A67022 (expected: 0x14A67022)`


---

### Round 11 | tokens: 28,473→482

**🔧 → `python_jupyter`**

<details><summary>Code (955 chars)</summary>

```python
# Load plaintext and ciphertext
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy')

# Test both keys
key1 = bytes.fromhex('3112E16E3B8A8FCFDE1C388C6CB9DE92')
key2 = bytes.fromhex('E474C0850AF01A57CF4892320620AA60')

# Expand keys
rk1 = sm4_key_expansion(key1)
rk2 = sm4_key_expansion(key2)

# Test with first plaintext
pt0 = plain[0].tobytes()
ct0_expected = cipher[0].tobytes()

ct1 = sm4_encrypt_block(pt0, rk1)
ct2 = sm4_encrypt_block(pt0, rk2)

print(f"Plaintext:  {pt0.hex().upper()}")
print(f"Expected:   {ct0_expected.hex().upper()}")
print(f"\nKey 1 result: {ct1.hex().upper()}")
print(f"Key 2 result: {ct2.hex().upper()}")

print(f"\nKey 1 match: {ct1 == ct0_expected}")
print(f"Key 2 match: {ct2 == ct0_expected}")
```
</details>

**📋 ← `python_jupyter`:** `Plaintext:  15F172190435A0103048F7161A5F01FD
Expected:   169B73531B72211DE486EF3FC2830686

Key 1 result: 2046817119E4585DC6B6E86FFF091377
Key 2 result: 051F9BF493CC88F20F213D041B386126

Key 1 match: False
Key 2 match: False`


---

### Round 12 | tokens: 28,984→378

**🤖 LLM:** 两个密钥都不匹配。让我分析CPA的详细结果，看看哪些字节需要搜索：

**🔧 → `python_jupyter`**

<details><summary>Code (844 chars)</summary>

```python
import json

# Load all 4 rounds' CPA details
rounds = []
for i in range(4):
    with open(f'sm4_cpa_round{i}_detail_*.json'.replace('*', '20260424_050301_884462' if i==0 else '20260424_050314_026417' if i==1 else '20260424_050330_842741' if i==2 else '20260424_050339_399560'), 'r') as f:
        rounds.append(json.load(f))

# Print summary
for i, r in enumerate(rounds):
    print(f"\n=== Round {i} ===")
    print(f"Recovered round key: {r['recovered_round_key']}")
    print(f"Average correlation: {r['cpa_avg_correlation']:.4f}")
    print(f"High confidence count: {r['high_confidence_count']}/4")
    print("\nPer-byte details:")
    for byte_info in r['per_byte']:
        gap = byte_info.get('top1_top2_gap', 0)
        print(f"  Byte {byte_info['byte']}: 0x{byte_info['key'][2:]} (corr={byte_info['correlation']:.4f}, gap={gap:.4f})")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1138 chars)</summary>

```
=== Round 0 ===
Recovered round key: F1DE7733
Average correlation: 0.4676
High confidence count: 0/4

Per-byte details:
  Byte 0: 0xF1 (corr=0.4630, gap=0.0000)
  Byte 1: 0xDE (corr=0.4459, gap=0.0000)
  Byte 2: 0x77 (corr=0.4819, gap=0.0000)
  Byte 3: 0x33 (corr=0.4796, gap=0.0000)

=== Round 1 ===
Recovered round key: 586CE653
Average correlation: 0.4565
High confidence count: 0/4

Per-byte details:
  Byte 0: 0x58 (corr=0.4793, gap=0.0000)
  Byte 1: 0x6C (corr=0.4405, gap=0.0000)
  Byte 2: 0xE6 (corr=0.4523, gap=0.0000)
  Byte 3: 0x53 (corr=0.4539, gap=0.0000)

=== Round 2 ===
Recovered round key: D6AD46FA
Average correlation: 0.4785
High confidence count: 1/4

Per-byte details:
  Byte 0: 0xD6 (corr=0.4609, gap=0.0000)
  Byte 1: 0xAD (corr=0.4403, gap=0.0000)
  Byte 2: 0x46 (corr=0.4851, gap=0.0000)
  Byte 3: 0xFA (corr=0.5276, gap=0.0000)

=== Round 3 ===
Recovered round key: 14A67022
Average correlation: 0.4667
High confidence count: 0/4

Per-byte details:
  Byte 0: 0x14 (corr=0.4605, gap=0.0000)
  Byte 1: 0xA6 (corr=0.4516, gap=0.0000)
  Byte 2: 0x70 (corr=0.4818, gap=0.0000)
  Byte 3: 0x22 (corr=0.4731, gap=0.0000)
```
</details>


---

### Round 13 | tokens: 29,870→209

**🔧 → `python_jupyter`**

<details><summary>Code (720 chars)</summary>

```python
# Check the actual detail file structure
import glob

# Find the actual detail files
detail_files = glob.glob('sm4_cpa_round*_detail_*.json')
print(f"Found detail files: {detail_files}")

# Load and inspect one
with open(detail_files[0], 'r') as f:
    data = json.load(f)
    print(f"\nKeys in detail file: {data.keys()}")
    if 'top_candidates' in data:
        print(f"\nTop candidates structure: {type(data['top_candidates'])}")
        if isinstance(data['top_candidates'], dict):
            print(f"Keys: {data['top_candidates'].keys()}")
            # Show first byte's candidates
            if '0' in data['top_candidates']:
                print(f"\nByte 0 top candidates: {data['top_candidates']['0'][:5]}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (655 chars)</summary>

```
Found detail files: ['sm4_cpa_round0_detail_20260424_050301_884462.json', 'sm4_cpa_round1_detail_20260424_050314_026417.json', 'sm4_cpa_round2_detail_20260424_050330_842741.json', 'sm4_cpa_round3_detail_20260424_050339_399560.json']

Keys in detail file: dict_keys(['schema_version', 'round_index', 'n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results', 'subkey_results', 'subkey_analysis', 'recovered_round_key', 'cpa_avg_correlation', 'cpa_min_correlation', 'avg_correlation', 'min_correlation', 'per_byte', 'high_confidence_count', 'recovery_assessment', 'low_confidence_subkeys', 'recommended_candidates', 'recommended_next_step'])
```
</details>


---

### Round 14 | tokens: 30,279→135

**🔧 → `python_jupyter`**

<details><summary>Code (416 chars)</summary>

```python
# Check subkey_results structure
with open(detail_files[0], 'r') as f:
    data = json.load(f)
    
print("Subkey results keys:", data['subkey_results'].keys())
print("\nByte 0 subkey results:")
print(json.dumps(data['subkey_results']['0'][:3], indent=2))

print("\n\nSubkey analysis keys:", data['subkey_analysis'].keys())
print("\nByte 0 subkey analysis:")
print(json.dumps(data['subkey_analysis']['0'], indent=2))
```
</details>

**❌ ← `python_jupyter` Error:**

```
---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mAttributeError[39m                            Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[314][39m[32m, line 5[39m
[32m      2[39m [38;5;28;01mwith[39;00m [38;5;28mopen[39m(detail_files[[32m0[39m], [33m'[39m[33mr[39m[33m'[39m) [38;5;28;01mas[39;00m f:
[32m      3[39m     data = json.load(f)
[32m----> [39m[32m5[39m [38;5;28mprint[39m([33m"[39m[33mSubkey results keys:[39m[33m"[39m, [43mdata[49m[43m[[49m[33;43m'[39;49m[33;43msubkey_results[39;49m[33;43m'[39;49m[43m][49m[43m.[49m[43mkeys[49m())
[32m      6[39m [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33mByte 0 subkey results:[39m[33m"[39m)
[32m      7[39m [38;5;28mprint[39m(json.dumps(data[[33m'[39m[33msubkey_results[39m[33m'[39m][[33m'[39m[33m0[39m[33m'[39m][:[32m3[39m], indent=[32m2[39m))

[31mAttributeError[39m: 'list' object has no attribute 'keys'
```


---

### Round 15 | tokens: 30,875→140

**🔧 → `python_jupyter`**

<details><summary>Code (441 chars)</summary>

```python
# Check subkey_results structure
with open(detail_files[0], 'r') as f:
    data = json.load(f)
    
print("Subkey results type:", type(data['subkey_results']))
print("Subkey results length:", len(data['subkey_results']))

if isinstance(data['subkey_results'], list):
    print("\nFirst element (byte 0):")
    print(json.dumps(data['subkey_results'][0][:3], indent=2))
else:
    print("\nSubkey results keys:", data['subkey_results'].keys())
```
</details>

**❌ ← `python_jupyter` Error:**

```
Subkey results type: <class 'list'>
Subkey results length: 4

First element (byte 0):

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mTypeError[39m                                 Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[315][39m[32m, line 10[39m
[32m      8[39m [38;5;28;01mif[39;00m [38;5;28misinstance[39m(data[[33m'[39m[33msubkey_results[39m[33m'[39m], [38;5;28mlist[39m):
[32m      9[39m     [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33mFirst element (byte 0):[39m[33m"[39m)
[32m---> [39m[32m10[39m     [38;5;28mprint[39m(json.dumps([43mdata[49m[43m[[49m[33;43m'[39;49m[33;43msubkey_results[39;49m[33;43m'[39;49m[43m][49m[43m[[49m[32;43m0[39;49m[43m][49m[43m[[49m[43m:[49m[32;43m3[39;49m[43m][49m, indent=[32m2[39m))
[32m     11[39m [38;5;28;01melse[39;00m:
[32m     12[39m     [38;5;28mprint[39m([33m"[39m[38;5;130;01m\n[39;00m[33mSubkey results keys:[39m[33m"[39m, data[[33m'[39m[33msubkey_results[39m[33m'[39m].keys())

[31mTypeError[39m: unhashable type: 'slice'
```


---

### Round 16 | tokens: 31,525→171

**🔧 → `python_jupyter`**

<details><summary>Code (634 chars)</summary>

```python
# Check subkey_results structure more carefully
with open(detail_files[0], 'r') as f:
    data = json.load(f)
    
print("Subkey results type:", type(data['subkey_results']))
print("Subkey results length:", len(data['subkey_results']))

# Check first element
first_elem = data['subkey_results'][0]
print("\nFirst element type:", type(first_elem))
print("First element:", first_elem)

# Check subkey_analysis
print("\n\nSubkey analysis type:", type(data['subkey_analysis']))
print("Subkey analysis length:", len(data['subkey_analysis']))
print("\nFirst subkey_analysis element:")
print(json.dumps(data['subkey_analysis'][0], indent=2))
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1814 chars)</summary>

```
Subkey results type: <class 'list'>
Subkey results length: 4

First element type: <class 'dict'>
First element: {'byte': 0, 'topK': [{'key': 241, 'score': 0.46296397927202204, 'time_index': 6281}, {'key': 126, 'score': 0.45589654703416765, 'time_index': 760}, {'key': 87, 'score': 0.4526713194992899, 'time_index': 3456}, {'key': 173, 'score': 0.44776561546367066, 'time_index': 5140}, {'key': 17, 'score': 0.4424987853583267, 'time_index': 2492}, {'key': 38, 'score': 0.4403179376794627, 'time_index': 596}, {'key': 207, 'score': 0.4308499800684925, 'time_index': 2706}, {'key': 169, 'score': 0.4260935517436079, 'time_index': 5089}, {'key': 15, 'score': 0.42368933456646485, 'time_index': 651}, {'key': 81, 'score': 0.42196962620221784, 'time_index': 5219}, {'key': 182, 'score': 0.4178665173344064, 'time_index': 2525}, {'key': 74, 'score': 0.41623395787308587, 'time_index': 44}, {'key': 179, 'score': 0.4155409212594863, 'time_index': 2471}, {'key': 26, 'score': 0.4076811371184029, 'time_index': 3784}, {'key': 56, 'score': 0.40360921378640724, 'time_index': 320}, {'key': 189, 'score': 0.4032025010221103, 'time_index': 533}, {'key': 77, 'score': 0.40242208651036493, 'time_index': 2915}, {'key': 130, 'score': 0.40235470289698827, 'time_index': 2209}, {'key': 224, 'score': 0.40039081019361916, 'time_index': 424}, {'key': 180, 'score': 0.3993430818700858, 'time_index': 2183}], 'best_key': 241}


Subkey analysis type: <class 'list'>
Subkey analysis length: 4

First subkey_analysis element:
...(truncated)
```
</details>


---

### Round 17 | tokens: 32,551→1,103

**🤖 LLM:** 现在我看到了详细结构。让我实现一个搜索策略，尝试每轮每个字节的top候选：

**🔧 → `python_jupyter`**

<details><summary>Code (2396 chars)</summary>

```python
import json
import itertools
import numpy as np

# Load all CPA details
round_details = []
for i in range(4):
    with open(f'sm4_cpa_round{i}_detail_*.json'.replace('*', 
        '20260424_050301_884462' if i==0 else 
        '20260424_050314_026417' if i==1 else 
        '20260424_050330_842741' if i==2 else 
        '20260424_050339_399560'), 'r') as f:
        round_details.append(json.load(f))

# Load plaintext and ciphertext
plain = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy')
cipher = np.load(r'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy')

pt0 = plain[0].tobytes()
ct0_expected = cipher[0].tobytes()

print(f"Testing with plaintext: {pt0.hex().upper()}")
print(f"Expected ciphertext: {ct0_expected.hex().upper()}")

# Get top candidates for each byte in each round
# We'll try top 3 candidates for each byte
top_n = 3

round_candidates = []
for r_idx, r_data in enumerate(round_details):
    byte_candidates = []
    for byte_idx in range(4):
        topK = r_data['subkey_results'][byte_idx]['topK'][:top_n]
        candidates = [c['key'] for c in topK]
        byte_candidates.append(candidates)
    round_candidates.append(byte_candidates)
    print(f"\nRound {r_idx} candidates:")
    for byte_idx, cands in enumerate(byte_candidates):
        print(f"  Byte {byte_idx}: {[hex(c) for c in cands]}")

# Now we need to search through combinations
# But this is 3^16 = 43 million combinations, too many
# Let's try a smarter approach: fix high-confidence bytes, search low-confidence ones

# For now, let's try the top-1 candidates first
print("\n\n=== Testing top-1 candidates ===")
rk = []
for r_idx in range(4):
    rk_bytes = []
    for byte_idx in range(4):
        rk_bytes.append(round_candidates[r_idx][byte_idx][0])
    rk_word = (rk_bytes[0] << 24) | (rk_bytes[1] << 16) | (rk_bytes[2] << 8) | rk_bytes[3]
    rk.append(rk_word)
    print(f"Round {r_idx} key: 0x{rk_word:08X}")

# Recover master key
master_key = sm4_reverse_key_expansion(rk[0], rk[1], rk[2], rk[3])
print(f"\nRecovered master key: {master_key.hex().upper()}")

# Verify
rk_test = sm4_key_expansion(master_key)
ct_test = sm4_encrypt_block(pt0, rk_test)
print(f"Encrypted: {ct_test.hex().upper()}")
print(f"Match: {ct_test == ct0_expected}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (993 chars)</summary>

```
Testing with plaintext: 15F172190435A0103048F7161A5F01FD
Expected ciphertext: 169B73531B72211DE486EF3FC2830686

Round 0 candidates:
  Byte 0: ['0xf1', '0x7e', '0x57']
  Byte 1: ['0xde', '0x50', '0x62']
  Byte 2: ['0x77', '0x8', '0xe']
  Byte 3: ['0x33', '0x59', '0xc6']

Round 1 candidates:
  Byte 0: ['0x58', '0x96', '0xa3']
  Byte 1: ['0x6c', '0xd8', '0x9c']
  Byte 2: ['0xe6', '0x6', '0xd']
  Byte 3: ['0x53', '0x8d', '0x42']

Round 2 candidates:
  Byte 0: ['0xd6', '0x53', '0x42']
  Byte 1: ['0xad', '0x8f', '0x48']
  Byte 2: ['0x46', '0x9a', '0x29']
  Byte 3: ['0xfa', '0xe2', '0x87']

Round 3 candidates:
  Byte 0: ['0x14', '0x69', '0x74']
  Byte 1: ['0xa6', '0x3c', '0x93']
  Byte 2: ['0x70', '0x80', '0xd']
  Byte 3: ['0x22', '0x89', '0xd4']


=== Testing top-1 candidates ===
Round 0 key: 0xF1DE7733
Round 1 key: 0x586CE653
Round 2 key: 0xD6AD46FA
Round 3 key: 0x14A67022

Recovered master key: E474C0850AF01A57CF4892320620AA60
Encrypted: 051F9BF493CC88F20F213D041B386126
Match: False
```
</details>


---

### Round 18 | tokens: 33,858→933

**🤖 LLM:** 让我尝试一个更智能的搜索策略，逐字节搜索：

**🔧 → `python_jupyter`**

<details><summary>Code (2849 chars)</summary>

```python
# More efficient search: try changing one byte at a time
# Start with top-1 candidates, then try replacing each byte with top-2, top-3

def test_key_combination(rk_bytes):
    """Test a combination of round keys"""
    rk = []
    for r_idx in range(4):
        rk_word = (rk_bytes[r_idx*4] << 24) | (rk_bytes[r_idx*4+1] << 16) | \
                  (rk_bytes[r_idx*4+2] << 8) | rk_bytes[r_idx*4+3]
        rk.append(rk_word)
    
    master_key = sm4_reverse_key_expansion(rk[0], rk[1], rk[2], rk[3])
    rk_test = sm4_key_expansion(master_key)
    ct_test = sm4_encrypt_block(pt0, rk_test)
    
    return ct_test == ct0_expected, master_key

# Start with top-1 candidates
base_rk_bytes = []
for r_idx in range(4):
    for byte_idx in range(4):
        base_rk_bytes.append(round_candidates[r_idx][byte_idx][0])

print("Testing base combination (all top-1)...")
found, mk = test_key_combination(base_rk_bytes)
print(f"Result: {'FOUND!' if found else 'Not found'}")

if not found:
    print("\n=== Trying single-byte variations ===")
    found_key = None
    
    # Try changing one byte at a time
    for r_idx in range(4):
        for byte_idx in range(4):
            for cand_idx in [1, 2]:  # Try top-2 and top-3
                test_bytes = base_rk_bytes.copy()
                test_bytes[r_idx*4 + byte_idx] = round_candidates[r_idx][byte_idx][cand_idx]
                
                found, mk = test_key_combination(test_bytes)
                if found:
                    print(f"FOUND! Changed Round {r_idx} Byte {byte_idx} to candidate {cand_idx+1}")
                    print(f"Master key: {mk.hex().upper()}")
                    found_key = mk
                    break
            if found_key:
                break
        if found_key:
            break
    
    if not found_key:
        print("\n=== Trying two-byte variations ===")
        # Try changing two bytes at a time
        for i in range(16):
            for j in range(i+1, 16):
                r_i, b_i = i // 4, i % 4
                r_j, b_j = j // 4, j % 4
                
                for ci in [1, 2]:
                    for cj in [1, 2]:
                        test_bytes = base_rk_bytes.copy()
                        test_bytes[i] = round_candidates[r_i][b_i][ci]
                        test_bytes[j] = round_candidates[r_j][b_j][cj]
                        
                        found, mk = test_key_combination(test_bytes)
                        if found:
                            print(f"FOUND! Changed bytes {i} and {j}")
                            print(f"Master key: {mk.hex().upper()}")
                            found_key = mk
                            break
                    if found_key:
                        break
                if found_key:
                    break
            if found_key:
                break
```
</details>

**📋 ← `python_jupyter`:** `Testing base combination (all top-1)...
Result: Not found

=== Trying single-byte variations ===

=== Trying two-byte variations ===`


---

### Round 19 | tokens: 34,608→447

**🤖 LLM:** 让我尝试三字节变化搜索：

**🔧 → `python_jupyter`**

<details><summary>Code (1502 chars)</summary>

```python
# Try three-byte variations
print("=== Trying three-byte variations ===")
found_key = None
count = 0

for i in range(16):
    for j in range(i+1, 16):
        for k in range(j+1, 16):
            r_i, b_i = i // 4, i % 4
            r_j, b_j = j // 4, j % 4
            r_k, b_k = k // 4, k % 4
            
            for ci in [1, 2]:
                for cj in [1, 2]:
                    for ck in [1, 2]:
                        count += 1
                        test_bytes = base_rk_bytes.copy()
                        test_bytes[i] = round_candidates[r_i][b_i][ci]
                        test_bytes[j] = round_candidates[r_j][b_j][cj]
                        test_bytes[k] = round_candidates[r_k][b_k][ck]
                        
                        found, mk = test_key_combination(test_bytes)
                        if found:
                            print(f"FOUND after {count} attempts!")
                            print(f"Changed bytes {i}, {j}, {k}")
                            print(f"Master key: {mk.hex().upper()}")
                            found_key = mk
                            break
                    if found_key:
                        break
                if found_key:
                    break
            if found_key:
                break
        if found_key:
            break
    if found_key:
        break

if not found_key:
    print(f"Tested {count} combinations, not found")
    print("\nNeed to expand search space or check CPA quality...")
```
</details>

**📋 ← `python_jupyter`:** `=== Trying three-byte variations ===
Tested 4480 combinations, not found

Need to expand search space or check CPA quality...`


---

### Round 20 | tokens: 34,999→485

**🤖 LLM:** 让我扩大搜索空间，尝试更多候选：

**🔧 → `python_jupyter`**

<details><summary>Code (1631 chars)</summary>

```python
# Expand to top 5 candidates and try more combinations
top_n = 5

round_candidates_5 = []
for r_idx, r_data in enumerate(round_details):
    byte_candidates = []
    for byte_idx in range(4):
        topK = r_data['subkey_results'][byte_idx]['topK'][:top_n]
        candidates = [c['key'] for c in topK]
        byte_candidates.append(candidates)
    round_candidates_5.append(byte_candidates)

print("Expanded to top 5 candidates per byte")

# Try four-byte variations with top 5 candidates
print("\n=== Trying four-byte variations (top 5 candidates) ===")
found_key = None
count = 0
max_attempts = 100000

import random

# Random sampling approach for efficiency
test_bytes = base_rk_bytes.copy()

for attempt in range(max_attempts):
    # Randomly select 4 bytes to change
    bytes_to_change = random.sample(range(16), 4)
    
    for idx in bytes_to_change:
        r_idx, b_idx = idx // 4, idx % 4
        # Randomly select a candidate (not the top-1)
        cand_idx = random.randint(1, top_n-1)
        test_bytes[idx] = round_candidates_5[r_idx][b_idx][cand_idx]
    
    found, mk = test_key_combination(test_bytes)
    count += 1
    
    if found:
        print(f"FOUND after {count} attempts!")
        print(f"Master key: {mk.hex().upper()}")
        found_key = mk
        break
    
    # Reset for next iteration
    for idx in bytes_to_change:
        r_idx, b_idx = idx // 4, idx % 4
        test_bytes[idx] = round_candidates_5[r_idx][b_idx][0]

if not found_key:
    print(f"Tested {count} random combinations, not found")
    print("\nLet me try a systematic approach with top 3 candidates for all bytes...")
```
</details>

**📋 ← `python_jupyter`:** `Expanded to top 5 candidates per byte

=== Trying four-byte variations (top 5 candidates) ===
Tested 100000 random combinations, not found

Let me try a systematic approach with top 3 candidates for all bytes...`


---

### Round 21 | tokens: 35,498→467

**🤖 LLM:** 让我重新分析波形，可能需要更好的预处理或对齐：

**🔧 → `python_jupyter`**

<details><summary>Code (1346 chars)</summary>

```python
# Let's analyze the waveform more carefully
# Check if there are alignment issues

import matplotlib.pyplot as plt

# Plot average trace
avg_trace = np.mean(wave, axis=0)
std_trace = np.std(wave, axis=0)

fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# Average trace
axes[0].plot(avg_trace)
axes[0].set_title('Average Power Trace', fontsize=14)
axes[0].set_xlabel('Sample Point')
axes[0].set_ylabel('Power')
axes[0].grid(True, alpha=0.3)

# Standard deviation
axes[1].plot(std_trace)
axes[1].set_title('Standard Deviation Across Traces', fontsize=14)
axes[1].set_xlabel('Sample Point')
axes[1].set_ylabel('Std Dev')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('trace_analysis.png', dpi=150)
plt.show()

# Find regions with high variance
high_std_regions = np.where(std_trace > np.percentile(std_trace, 90))[0]
print(f"\nHigh variance regions (top 10%):")
print(f"  Sample ranges: {high_std_regions[:20]}... (showing first 20)")

# Check if traces are aligned
# Compare first 10 traces in a small region
plt.figure(figsize=(14, 4))
for i in range(10):
    plt.plot(wave[i, 1000:1200] + i*50, alpha=0.5)
plt.title('Trace Alignment Check (samples 1000-1200)', fontsize=14)
plt.xlabel('Sample Point')
plt.ylabel('Power (offset)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('alignment_check.png', dpi=150)
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `High variance regions (top 10%):
  Sample ranges: [820 821 822 823 824 825 826 827 828 833 834 835 836 837 838 839 840 841
 842 843]... (showing first 20)
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1054614471.py:28: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1054614471.py:46: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 22 | tokens: 36,102→327

**🤖 LLM:** 让我尝试静态对齐来改善CPA质量：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy",
  "start": 1000,
  "length": 120,
  "max_shift": 100,
  "threshold": 80,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_050754_538906.npy", "plot_path": "align_overlay_20260424_050754_538906.png", "ref_trace_used": 50, "accepted": 82, "discarded": 18, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260424_050754_538906.npy", "plaintext_traces": 82, "out_ciphertext_npy": "ciphertext_aligned_20260424_050754_538906.npy", "ciphertext_traces": 82, "alignment_avg_correlation": 0.9869, "alignment_min_correlation": 0.8901, "acceptance_rate": 0.82}`


![align_overlay_20260424_050754_538906.png](./align_overlay_20260424_050754_538906.png)


---

### Round 23 | tokens: 36,527→146

**🤖 LLM:** 对齐完成，接受了82条曲线。现在用对齐后的波形重新做CPA：

**🔧 → `sm4_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_050754_538906.npy",
  "round_index": 0,
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_050754_538906.npy"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (841 chars)</summary>

```
{"round_index": 0, "recovered_round_key": "F12186F9", "cpa_avg_correlation": 0.8451, "cpa_min_correlation": 0.7819, "target": "S-box_out", "n_traces": 82, "detail_file": "sm4_cpa_round0_detail_20260424_050802_680209.json", "per_byte": [{"byte": 0, "key": "0xF1", "correlation": 0.9022575879303489, "time_index": 1243}, {"byte": 1, "key": "0x21", "correlation": 0.8299363939223987, "time_index": 1390}, {"byte": 2, "key": "0x86", "correlation": 0.8661576695240195, "time_index": 1152}, {"byte": 3, "key": "0xF9", "correlation": 0.7819320167584513, "time_index": 1105}], "high_confidence_count": 4, "recovery_assessment": "4/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 24 | tokens: 36,962→172

**🤖 LLM:** 太好了！对齐后相关性大幅提升（0.8451），4个字节都是高置信度！继续第1轮：

**🔧 → `sm4_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_050754_538906.npy",
  "prev_round_keys": [
    "F12186F9"
  ],
  "round_index": 1,
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_050754_538906.npy"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (841 chars)</summary>

```
{"round_index": 1, "recovered_round_key": "41662B61", "cpa_avg_correlation": 0.7978, "cpa_min_correlation": 0.7278, "target": "S-box_out", "n_traces": 82, "detail_file": "sm4_cpa_round1_detail_20260424_050811_238270.json", "per_byte": [{"byte": 0, "key": "0x41", "correlation": 0.8534660188290318, "time_index": 2730}, {"byte": 1, "key": "0x66", "correlation": 0.7277649021029112, "time_index": 2877}, {"byte": 2, "key": "0x2B", "correlation": 0.8330817985798019, "time_index": 2640}, {"byte": 3, "key": "0x61", "correlation": 0.7769320609640221, "time_index": 3136}], "high_confidence_count": 4, "recovery_assessment": "4/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 25 | tokens: 37,424→136

**🤖 LLM:** 第1轮完成，继续第2轮：

**🔧 → `sm4_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_050754_538906.npy",
  "prev_round_keys": [
    "F12186F9",
    "41662B61"
  ],
  "round_index": 2,
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_050754_538906.npy"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (839 chars)</summary>

```
{"round_index": 2, "recovered_round_key": "5A6AB19A", "cpa_avg_correlation": 0.736, "cpa_min_correlation": 0.6812, "target": "S-box_out", "n_traces": 82, "detail_file": "sm4_cpa_round2_detail_20260424_050818_390328.json", "per_byte": [{"byte": 0, "key": "0x5A", "correlation": 0.7571951011418895, "time_index": 4218}, {"byte": 1, "key": "0x6A", "correlation": 0.6870359275167307, "time_index": 4169}, {"byte": 2, "key": "0xB1", "correlation": 0.8184454823168883, "time_index": 4126}, {"byte": 3, "key": "0x9A", "correlation": 0.681150065956565, "time_index": 4535}], "high_confidence_count": 4, "recovery_assessment": "4/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 26 | tokens: 37,873→137

**🤖 LLM:** 第2轮完成，继续第3轮：

**🔧 → `sm4_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_050754_538906.npy",
  "prev_round_keys": [
    "F12186F9",
    "41662B61",
    "5A6AB19A"
  ],
  "round_index": 3,
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_050754_538906.npy"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (1380 chars)</summary>

```
{"round_index": 3, "recovered_round_key": "7B672077", "cpa_avg_correlation": 0.6811, "cpa_min_correlation": 0.5346, "target": "S-box_out", "n_traces": 82, "detail_file": "sm4_cpa_round3_detail_20260424_050826_762682.json", "per_byte": [{"byte": 0, "key": "0x7B", "correlation": 0.7894677099063886, "time_index": 5707}, {"byte": 1, "key": "0x67", "correlation": 0.5345549110653708, "time_index": 5649}, {"byte": 2, "key": "0x20", "correlation": 0.8083006568486152, "time_index": 5616}, {"byte": 3, "key": "0x77", "correlation": 0.5918783608695267, "time_index": 5764}], "high_confidence_count": 2, "recovery_assessment": "2/4 bytes high-confidence in this round. This is the SM4 gray band: refine the round window or merge complementary CPA attempts before moving on.", "low_confidence_subkeys": [{"subkey_index": 1, "byte": 1, "best_key_hex": "0x67", "top1_top2_gap": 0.04673426343021426}, {"subkey_index": 3, "byte": 3, "best_key_hex": "0x77", "top1_top2_gap": 0.10558119419417493}], "recommended_next_step": "alignment_or_multi_strategy_merge_before_next_round", "recovered_master_key": "A68B463DC1D8B3975EF1AC1D769A3210", "master_key_math_consistent": true, "master_key_verification_note": "IMPORTANT: math_consistent=true only means rk0-rk3 are internally consistent with this master_key. It does NOT mean the key is correct. You MUST call encrypt_decrypt_verify to confirm."}
```
</details>


---

### Round 27 | tokens: 38,512→157

**🤖 LLM:** 4轮CPA全部完成！现在验证恢复的主密钥：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "SM4",
  "ciphertext_npy": "ciphertext_aligned_20260424_050754_538906.npy",
  "key_hex": "A68B463DC1D8B3975EF1AC1D769A3210",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_050754_538906.npy",
  "trace_index": 0
}`

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "1ECAD7FC168351E41F1A3F785AA679F9", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "SM4-128-ECB encrypt: 15f172190435a0103048f7161a5f01fd... → 1ECAD7FC168351E41F1A3F785AA679F9...\n❌ Key verification FAILED — 16/16 ciphertext bytes differ\n   Expected:  169B73531B72211DE486EF3FC2830686\n   Got:       1ECAD7FC168351E41F1A3F785AA679F9\n\n   ⚠️ IMPORTANT: '16 ciphertext bytes differ' does NOT mean '16 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 28 | tokens: 38,996→529

**🤖 LLM:** 密钥验证失败，第3轮有2个低置信度字节。让我手动搜索正确的密钥：

**🔧 → `python_jupyter`**

<details><summary>Code (1423 chars)</summary>

```python
# Load aligned plaintext and ciphertext
plain_aligned = np.load('plaintext_aligned_20260424_050754_538906.npy')
cipher_aligned = np.load('ciphertext_aligned_20260424_050754_538906.npy')

pt0 = plain_aligned[0].tobytes()
ct0_expected = cipher_aligned[0].tobytes()

print(f"Testing with aligned data:")
print(f"Plaintext:  {pt0.hex().upper()}")
print(f"Ciphertext: {ct0_expected.hex().upper()}")

# Load all 4 rounds' CPA details from aligned traces
round_details_aligned = []
for i in range(4):
    with open(f'sm4_cpa_round{i}_detail_*.json'.replace('*', 
        '20260424_050802_680209' if i==0 else 
        '20260424_050811_238270' if i==1 else 
        '20260424_050818_390328' if i==2 else 
        '20260424_050826_762682'), 'r') as f:
        round_details_aligned.append(json.load(f))

# Get top candidates for each byte
top_n = 5
round_candidates_aligned = []
for r_idx, r_data in enumerate(round_details_aligned):
    byte_candidates = []
    for byte_idx in range(4):
        topK = r_data['subkey_results'][byte_idx]['topK'][:top_n]
        candidates = [c['key'] for c in topK]
        byte_candidates.append(candidates)
    round_candidates_aligned.append(byte_candidates)

# Print candidates
for r_idx in range(4):
    print(f"\nRound {r_idx} candidates:")
    for byte_idx in range(4):
        cands = round_candidates_aligned[r_idx][byte_idx]
        print(f"  Byte {byte_idx}: {[hex(c) for c in cands]}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1014 chars)</summary>

```
Testing with aligned data:
Plaintext:  15F172190435A0103048F7161A5F01FD
Ciphertext: 169B73531B72211DE486EF3FC2830686

Round 0 candidates:
  Byte 0: ['0xf1', '0x54', '0x1d', '0x82', '0xa6']
  Byte 1: ['0x21', '0xf1', '0x53', '0x25', '0x5a']
  Byte 2: ['0x86', '0x57', '0xd1', '0x2c', '0x4f']
  Byte 3: ['0xf9', '0xd1', '0x40', '0xed', '0xc2']

Round 1 candidates:
  Byte 0: ['0x41', '0x87', '0x7c', '0x12', '0x71']
  Byte 1: ['0x66', '0x8f', '0x1d', '0x65', '0x98']
  Byte 2: ['0x2b', '0x6e', '0x36', '0xbf', '0x0']
  Byte 3: ['0x61', '0xfd', '0xf2', '0x35', '0x5e']

Round 2 candidates:
  Byte 0: ['0x5a', '0xe0', '0x43', '0x9d', '0xcd']
  Byte 1: ['0x6a', '0xd8', '0x94', '0x1d', '0xe3']
  Byte 2: ['0xb1', '0x5d', '0xae', '0xf0', '0xf6']
  Byte 3: ['0x9a', '0x0', '0x12', '0x3d', '0xf0']

Round 3 candidates:
  Byte 0: ['0x7b', '0x2f', '0xa7', '0x42', '0x98']
  Byte 1: ['0x67', '0xa9', '0x41', '0x5e', '0xf5']
  Byte 2: ['0x20', '0x66', '0x87', '0xdd', '0x6d']
  Byte 3: ['0x77', '0x67', '0x28', '0x5a', '0x91']
```
</details>


---

### Round 29 | tokens: 40,033→723

**🔧 → `python_jupyter`**

<details><summary>Code (2509 chars)</summary>

```python
# Search for the correct key
# Focus on Round 3 which has low confidence bytes

def test_key_combination_aligned(rk_bytes):
    """Test a combination of round keys"""
    rk = []
    for r_idx in range(4):
        rk_word = (rk_bytes[r_idx*4] << 24) | (rk_bytes[r_idx*4+1] << 16) | \
                  (rk_bytes[r_idx*4+2] << 8) | rk_bytes[r_idx*4+3]
        rk.append(rk_word)
    
    master_key = sm4_reverse_key_expansion(rk[0], rk[1], rk[2], rk[3])
    rk_test = sm4_key_expansion(master_key)
    ct_test = sm4_encrypt_block(pt0, rk_test)
    
    return ct_test == ct0_expected, master_key

# Start with top-1 candidates
base_rk_bytes = []
for r_idx in range(4):
    for byte_idx in range(4):
        base_rk_bytes.append(round_candidates_aligned[r_idx][byte_idx][0])

print("Testing base combination (all top-1)...")
found, mk = test_key_combination_aligned(base_rk_bytes)
print(f"Result: {'FOUND!' if found else 'Not found'}")

if not found:
    # Focus on Round 3 bytes 1 and 3 (low confidence)
    print("\n=== Focusing on Round 3 low-confidence bytes ===")
    found_key = None
    
    # Try all combinations for Round 3 bytes 1 and 3
    for b1_cand in round_candidates_aligned[3][1]:
        for b3_cand in round_candidates_aligned[3][3]:
            test_bytes = base_rk_bytes.copy()
            test_bytes[13] = b1_cand  # Round 3, byte 1
            test_bytes[15] = b3_cand  # Round 3, byte 3
            
            found, mk = test_key_combination_aligned(test_bytes)
            if found:
                print(f"FOUND! Round 3 byte 1 = 0x{b1_cand:02X}, byte 3 = 0x{b3_cand:02X}")
                print(f"Master key: {mk.hex().upper()}")
                found_key = mk
                break
        if found_key:
            break
    
    if not found_key:
        print("Not found in Round 3 variations")
        print("\n=== Trying single-byte variations across all rounds ===")
        
        for i in range(16):
            r_idx, b_idx = i // 4, i % 4
            for cand in round_candidates_aligned[r_idx][b_idx][1:]:
                test_bytes = base_rk_bytes.copy()
                test_bytes[i] = cand
                
                found, mk = test_key_combination_aligned(test_bytes)
                if found:
                    print(f"FOUND! Byte {i} (Round {r_idx}, byte {b_idx}) = 0x{cand:02X}")
                    print(f"Master key: {mk.hex().upper()}")
                    found_key = mk
                    break
            if found_key:
                break
```
</details>

**📋 ← `python_jupyter`:** `Testing base combination (all top-1)...
Result: Not found

=== Focusing on Round 3 low-confidence bytes ===
Not found in Round 3 variations

=== Trying single-byte variations across all rounds ===`


---

### Round 30 | tokens: 40,764→378

**🤖 LLM:** 让我尝试两字节变化搜索：

**🔧 → `python_jupyter`**

<details><summary>Code (1307 chars)</summary>

```python
# Try two-byte variations
print("=== Trying two-byte variations ===")
found_key = None
count = 0

for i in range(16):
    r_i, b_i = i // 4, i % 4
    for j in range(i+1, 16):
        r_j, b_j = j // 4, j % 4
        
        for ci in range(1, 5):  # Try candidates 2-5
            for cj in range(1, 5):
                count += 1
                test_bytes = base_rk_bytes.copy()
                test_bytes[i] = round_candidates_aligned[r_i][b_i][ci]
                test_bytes[j] = round_candidates_aligned[r_j][b_j][cj]
                
                found, mk = test_key_combination_aligned(test_bytes)
                if found:
                    print(f"FOUND after {count} attempts!")
                    print(f"Changed bytes {i} and {j}")
                    print(f"  Byte {i} (Round {r_i}, byte {b_i}) = 0x{round_candidates_aligned[r_i][b_i][ci]:02X}")
                    print(f"  Byte {j} (Round {r_j}, byte {b_j}) = 0x{round_candidates_aligned[r_j][b_j][cj]:02X}")
                    print(f"Master key: {mk.hex().upper()}")
                    found_key = mk
                    break
            if found_key:
                break
        if found_key:
            break
    if found_key:
        break

if not found_key:
    print(f"Tested {count} two-byte combinations, not found")
```
</details>

**📋 ← `python_jupyter`:** `=== Trying two-byte variations ===
Tested 1920 two-byte combinations, not found`


---

### Round 31 | tokens: 41,151→391

**🤖 LLM:** 让我尝试三字节变化搜索：

**🔧 → `python_jupyter`**

<details><summary>Code (1473 chars)</summary>

```python
# Try three-byte variations
print("=== Trying three-byte variations ===")
found_key = None
count = 0
max_attempts = 50000

import itertools

for i, j, k in itertools.combinations(range(16), 3):
    r_i, b_i = i // 4, i % 4
    r_j, b_j = j // 4, j % 4
    r_k, b_k = k // 4, k % 4
    
    for ci in range(1, 4):  # Try candidates 2-4
        for cj in range(1, 4):
            for ck in range(1, 4):
                count += 1
                if count > max_attempts:
                    print(f"Reached max attempts ({max_attempts})")
                    break
                    
                test_bytes = base_rk_bytes.copy()
                test_bytes[i] = round_candidates_aligned[r_i][b_i][ci]
                test_bytes[j] = round_candidates_aligned[r_j][b_j][cj]
                test_bytes[k] = round_candidates_aligned[r_k][b_k][ck]
                
                found, mk = test_key_combination_aligned(test_bytes)
                if found:
                    print(f"FOUND after {count} attempts!")
                    print(f"Changed bytes {i}, {j}, {k}")
                    print(f"Master key: {mk.hex().upper()}")
                    found_key = mk
                    break
            if found_key or count > max_attempts:
                break
        if found_key or count > max_attempts:
            break
    if found_key or count > max_attempts:
        break

if not found_key:
    print(f"Tested {count} three-byte combinations, not found")
```
</details>

**📋 ← `python_jupyter`:** `=== Trying three-byte variations ===
Tested 15120 three-byte combinations, not found`


---

### Round 32 | tokens: 41,552→350

**🤖 LLM:** 让我尝试不同的对齐参数：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "ciphertext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy",
  "length": 150,
  "max_shift": 150,
  "plaintext_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "start": 1100,
  "threshold": 75,
  "wave_npy": "F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260424_050937_849908.npy", "plot_path": "align_overlay_20260424_050937_849908.png", "ref_trace_used": 50, "accepted": 96, "discarded": 4, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260424_050937_849908.npy", "plaintext_traces": 96, "out_ciphertext_npy": "ciphertext_aligned_20260424_050937_849908.npy", "ciphertext_traces": 96, "alignment_avg_correlation": 0.9424, "alignment_min_correlation": 0.8537, "acceptance_rate": 0.96}`


![align_overlay_20260424_050937_849908.png](./align_overlay_20260424_050937_849908.png)


---

### Round 33 | tokens: 41,973→126

**🤖 LLM:** 接受率更高了（96条）。让我用新的对齐结果重新做CPA：

**🔧 → `sm4_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_050937_849908.npy",
  "round_index": 0,
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_050937_849908.npy"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (840 chars)</summary>

```
{"round_index": 0, "recovered_round_key": "F12186F9", "cpa_avg_correlation": 0.8472, "cpa_min_correlation": 0.7831, "target": "S-box_out", "n_traces": 96, "detail_file": "sm4_cpa_round0_detail_20260424_050946_927593.json", "per_byte": [{"byte": 0, "key": "0xF1", "correlation": 0.8891277368533945, "time_index": 1243}, {"byte": 1, "key": "0x21", "correlation": 0.8607239914578386, "time_index": 1390}, {"byte": 2, "key": "0x86", "correlation": 0.855766054886591, "time_index": 1152}, {"byte": 3, "key": "0xF9", "correlation": 0.7831246538689989, "time_index": 1106}], "high_confidence_count": 4, "recovery_assessment": "4/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 34 | tokens: 42,406→112

**🔧 → `sm4_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_050937_849908.npy",
  "prev_round_keys": [
    "F12186F9"
  ],
  "round_index": 1,
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_050937_849908.npy"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (841 chars)</summary>

```
{"round_index": 1, "recovered_round_key": "41662B61", "cpa_avg_correlation": 0.7937, "cpa_min_correlation": 0.7371, "target": "S-box_out", "n_traces": 96, "detail_file": "sm4_cpa_round1_detail_20260424_050953_950129.json", "per_byte": [{"byte": 0, "key": "0x41", "correlation": 0.8547413201215522, "time_index": 2730}, {"byte": 1, "key": "0x66", "correlation": 0.7371119423771196, "time_index": 2682}, {"byte": 2, "key": "0x2B", "correlation": 0.8005060860376254, "time_index": 2640}, {"byte": 3, "key": "0x61", "correlation": 0.7823816924524921, "time_index": 3136}], "high_confidence_count": 4, "recovery_assessment": "4/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 35 | tokens: 42,835→117

**🔧 → `sm4_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_050937_849908.npy",
  "prev_round_keys": [
    "F12186F9",
    "41662B61"
  ],
  "round_index": 2,
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_050937_849908.npy"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (841 chars)</summary>

```
{"round_index": 2, "recovered_round_key": "5A6AB19A", "cpa_avg_correlation": 0.7329, "cpa_min_correlation": 0.6628, "target": "S-box_out", "n_traces": 96, "detail_file": "sm4_cpa_round2_detail_20260424_051001_270098.json", "per_byte": [{"byte": 0, "key": "0x5A", "correlation": 0.7632761210656022, "time_index": 4218}, {"byte": 1, "key": "0x6A", "correlation": 0.6899195002599596, "time_index": 4169}, {"byte": 2, "key": "0xB1", "correlation": 0.8157566972948889, "time_index": 4127}, {"byte": 3, "key": "0x9A", "correlation": 0.6627895823034206, "time_index": 4535}], "high_confidence_count": 4, "recovery_assessment": "4/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 36 | tokens: 43,274→131

**🔧 → `sm4_cpa_attack`** `{
  "candidates": 20,
  "leakage_model": "HW",
  "plaintext_npy": "plaintext_aligned_20260424_050937_849908.npy",
  "prev_round_keys": [
    "F12186F9",
    "41662B61",
    "5A6AB19A"
  ],
  "round_index": 3,
  "target": "S-box_out",
  "wave_npy": "aligned_20260424_050937_849908.npy"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (1249 chars)</summary>

```
{"round_index": 3, "recovered_round_key": "7BA92077", "cpa_avg_correlation": 0.6825, "cpa_min_correlation": 0.5491, "target": "S-box_out", "n_traces": 96, "detail_file": "sm4_cpa_round3_detail_20260424_051009_533297.json", "per_byte": [{"byte": 0, "key": "0x7B", "correlation": 0.8170813051201113, "time_index": 5707}, {"byte": 1, "key": "0xA9", "correlation": 0.5490550944961381, "time_index": 5657}, {"byte": 2, "key": "0x20", "correlation": 0.7842343661132083, "time_index": 5616}, {"byte": 3, "key": "0x77", "correlation": 0.5794512329834193, "time_index": 5802}], "high_confidence_count": 3, "recovery_assessment": "3/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [{"subkey_index": 1, "byte": 1, "best_key_hex": "0xA9", "top1_top2_gap": 0.11955637664173493}], "recommended_next_step": "continue_round_recovery_or_verify_master_key", "recovered_master_key": "0123456789ABCDEFFEDCBA9876543210", "master_key_math_consistent": true, "master_key_verification_note": "IMPORTANT: math_consistent=true only means rk0-rk3 are internally consistent with this master_key. It does NOT mean the key is correct. You MUST call encrypt_decrypt_verify to confirm."}
```
</details>


---

### Round 37 | tokens: 43,844→168

**🤖 LLM:** 太好了！恢复的主密钥看起来像是一个标准测试密钥！让我验证：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "SM4",
  "ciphertext_npy": "ciphertext_aligned_20260424_050937_849908.npy",
  "key_hex": "0123456789ABCDEFFEDCBA9876543210",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_050937_849908.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "169B73531B72211DE486EF3FC2830686", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "SM4-128-ECB encrypt: 15f172190435a0103048f7161a5f01fd... → 169B73531B72211DE486EF3FC2830686...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 38 | tokens: 44,092→856

**🤖 LLM:** 🎉 **成功！密钥验证通过！**

## 攻击总结

### 恢复的密钥
**主密钥**: `0123456789ABCDEFFEDCBA9876543210`

这是一个标准的SM4测试密钥。

### 攻击过程

1. **数据概况**
   - 波形：100条曲线，6500个采样点
   - 设备：接触式智能卡SM4实现

2. **预处理**
   - 原始波形存在对齐问题
   - 使用静态对齐（start=1100, length=150, max_shift=150, threshold=75）
   - 对齐后接受率：96/100条曲线

3. **CPA攻击结果**

| 轮次 | 轮密钥 | 平均相关性 | 高置信度字节 |
|------|--------|-----------|-------------|
| 0 | F12186F9 | 0.8472 | 4/4 |
| 1 | 41662B61 | 0.7937 | 4/4 |
| 2 | 5A6AB19A | 0.7329 | 4/4 |
| 3 | 7BA92077 | 0.6825 | 3/4 |

4. **关键发现**
   - 静态对齐对SM4攻击至关重要，相关性从~0.46提升到~0.85
   - 对齐参数需要根据实际波形调整
   - SM4的4轮CPA需要依次进行，每轮依赖前一轮的结果

### 验证结果
```
明文:  15F172190435A0103048F7161A5F01FD
密文:  169B73531B72211DE486EF3FC2830686
✅ 密钥验证通过 — 所有16字节匹配
```

**🔧 → `python_jupyter`**

<details><summary>Code (460 chars)</summary>

```python
# 生成最终报告
print("=" * 60)
print("SM4 CPA攻击成功报告")
print("=" * 60)
print(f"\n恢复的主密钥: 0123456789ABCDEFFEDCBA9876543210")
print(f"\n轮密钥:")
print(f"  rk[0] = 0xF12186F9")
print(f"  rk[1] = 0x41662B61")
print(f"  rk[2] = 0x5A6AB19A")
print(f"  rk[3] = 0x7BA92077")
print(f"\n攻击参数:")
print(f"  - 泄露模型: Hamming Weight (HW)")
print(f"  - 攻击目标: S-box output")
print(f"  - 对齐方式: 静态对齐 (correlation-based)")
print(f"  - 有效曲线数: 96/100")
print(f"\n验证状态: ✅ 成功")
print("=" * 60)
```
</details>

**📋 ← `python_jupyter`:** `============================================================
SM4 CPA攻击成功报告
============================================================

恢复的主密钥: 0123456789ABCDEFFEDCBA9876543210

轮密钥:
  rk[0] = 0xF12186F9
  rk[1] = 0x41662B61
  rk[2] = 0x5A6AB19A
  rk[3] = 0x7BA92077

攻击参数:
  - 泄露模型: Hamming Weight (HW)
  - 攻击目标: S-box output
  - 对齐方式: 静态对齐 (correlation-based)
  - 有效曲线数: 96/100

验证状态: ✅ 成功
============================================================`


---

### Round 39 | tokens: 44,918→462

**🤖 LLM:** ## 攻击成功！

我已经成功对接触式智能卡的SM4实现进行了CPA攻击，完整流程如下：

### 📊 攻击流程

1. **数据加载与分析**
   - 100条功率曲线，6500个采样点
   - 发现波形存在对齐问题

2. **静态对齐预处理**
   - 参数：start=1100, length=150, max_shift=150, threshold=75
   - 接受率：96/100条曲线
   - 对齐后相关性从~0.46提升到~0.85

3. **4轮CPA攻击**
   - 每轮恢复4字节轮密钥
   - 使用Hamming Weight模型，攻击S-box输出
   - 相关性：0.68-0.85，高置信度字节：15/16

4. **主密钥反推**
   - 从4个轮密钥(rk0-rk3)反推128位主密钥
   - SM4密钥扩展算法的逆过程

### 🔑 恢复结果

| 项目 | 值 |
|------|-----|
| **主密钥** | `0123456789ABCDEFFEDCBA9876543210` |
| **rk[0]** | `F12186F9` |
| **rk[1]** | `41662B61` |
| **rk[2]** | `5A6AB19A` |
| **rk[3]** | `7BA92077` |

### ✅ 验证结果
- 明文加密后与实际密文完全匹配
- 密钥验证通过！

### 💡 关键经验
1. **对齐是关键**：SM4软件实现对齐后相关性显著提升
2. **参数调优**：对齐参数需要根据实际波形调整
3. **轮次依赖**：SM4的4轮CPA需要依次进行，每轮依赖前一轮结果
4. **候选搜索**：低置信度字节需要尝试多个候选值


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 15,512 | 720 | 16,232 |
| 2 | 15,943 | 340 | 16,283 |
| 3 | 16,516 | 355 | 16,871 |
| 4 | 17,226 | 340 | 17,566 |
| 5 | 17,963 | 216 | 18,179 |
| 6 | 18,946 | 208 | 19,154 |
| 7 | 19,608 | 223 | 19,831 |
| 8 | 20,425 | 341 | 20,766 |
| 9 | 20,996 | 429 | 21,425 |
| 10 | 24,484 | 4,060 | 28,544 |
| 11 | 28,473 | 482 | 28,955 |
| 12 | 28,984 | 378 | 29,362 |
| 13 | 29,870 | 209 | 30,079 |
| 14 | 30,279 | 135 | 30,414 |
| 15 | 30,875 | 140 | 31,015 |
| 16 | 31,525 | 171 | 31,696 |
| 17 | 32,551 | 1,103 | 33,654 |
| 18 | 33,858 | 933 | 34,791 |
| 19 | 34,608 | 447 | 35,055 |
| 20 | 34,999 | 485 | 35,484 |
| 21 | 35,498 | 467 | 35,965 |
| 22 | 36,102 | 327 | 36,429 |
| 23 | 36,527 | 146 | 36,673 |
| 24 | 36,962 | 172 | 37,134 |
| 25 | 37,424 | 136 | 37,560 |
| 26 | 37,873 | 137 | 38,010 |
| 27 | 38,512 | 157 | 38,669 |
| 28 | 38,996 | 529 | 39,525 |
| 29 | 40,033 | 723 | 40,756 |
| 30 | 40,764 | 378 | 41,142 |
| 31 | 41,151 | 391 | 41,542 |
| 32 | 41,552 | 350 | 41,902 |
| 33 | 41,973 | 126 | 42,099 |
| 34 | 42,406 | 112 | 42,518 |
| 35 | 42,835 | 117 | 42,952 |
| 36 | 43,274 | 131 | 43,405 |
| 37 | 43,844 | 168 | 44,012 |
| 38 | 44,092 | 856 | 44,948 |
| 39 | 44,918 | 462 | 45,380 |
| **Total** | **1,268,377** | **17,600** | **1,285,977** |

## 8. Final Output

## 攻击成功！

我已经成功对接触式智能卡的SM4实现进行了CPA攻击，完整流程如下：

### 📊 攻击流程

1. **数据加载与分析**
   - 100条功率曲线，6500个采样点
   - 发现波形存在对齐问题

2. **静态对齐预处理**
   - 参数：start=1100, length=150, max_shift=150, threshold=75
   - 接受率：96/100条曲线
   - 对齐后相关性从~0.46提升到~0.85

3. **4轮CPA攻击**
   - 每轮恢复4字节轮密钥
   - 使用Hamming Weight模型，攻击S-box输出
   - 相关性：0.68-0.85，高置信度字节：15/16

4. **主密钥反推**
   - 从4个轮密钥(rk0-rk3)反推128位主密钥
   - SM4密钥扩展算法的逆过程

### 🔑 恢复结果

| 项目 | 值 |
|------|-----|
| **主密钥** | `0123456789ABCDEFFEDCBA9876543210` |
| **rk[0]** | `F12186F9` |
| **rk[1]** | `41662B61` |
| **rk[2]** | `5A6AB19A` |
| **rk[3]** | `7BA92077` |

### ✅ 验证结果
- 明文加密后与实际密文完全匹配
- 密钥验证通过！

### 💡 关键经验
1. **对齐是关键**：SM4软件实现对齐后相关性显著提升
2. **参数调优**：对齐参数需要根据实际波形调整
3. **轮次依赖**：SM4的4轮CPA需要依次进行，每轮依赖前一轮结果
4. **候选搜索**：低置信度字节需要尝试多个候选值
