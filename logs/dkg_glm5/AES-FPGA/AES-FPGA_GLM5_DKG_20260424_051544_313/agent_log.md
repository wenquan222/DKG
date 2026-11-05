# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_051544_313 |
| Duration | 171.6s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-FPGA_GLM5_DKG_20260424_051544_313` |
| Total LLM Calls | 13 |
| First Round | prompt: 16,098, completion: 829 |
| Last Round | prompt: 26,613, completion: 743 |
| Total Tokens | 272,763 (prompt: 265,101, completion: 7,662) |

## 3. User Query

```
帮我对一个FPGA硬件实现的AES密码算法波形进行CPA恢复密钥，这是硬件实现，可能不需要滤波，可能需要纵向对齐，泄漏模型可能需要用Hamming Distance。明文文件为'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy'，密文文件为'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy',原始波形文件为'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个FPGA硬件实现的AES密码算法波形进行CPA恢复密钥，这是硬件实现，可能不需要滤波，可能需要纵向对齐，泄漏模型可能需要用Hamming Distance。明文文件为'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy'，密文文件为'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy',原始波形文件为'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy'"

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
["AES", "FPGA", "CPA", "Hamming Distance", "Static Alignment"]

Parsed Keywords: `["AES", "FPGA", "CPA", "Hamming Distance", "Static Alignment"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 39531 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (41779 chars, click to expand)</summary>

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

**Search keywords** (5): AES, FPGA, CPA, Hamming Distance, Static Alignment

**Summary**: 27 upper entities, 25 relationships, 16 diagnostic chains, 14 strategies


## 1. Upper Layer Entities (27)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### DeviceClass (9)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **Artix-7 FPGA on CW305 board** — category=FPGA
- **FPGA (Xilinx Virtex/Spartan)** — category=FPGA
- **SASEBO GII FPGA** — category=FPGA
- **Sasebo-GII board** — category=FPGA
- **Spartan-6 XC6SLX75 FPGA** — category=FPGA
- **Xilinx Virtex-II Pro FPGA on SASEBO** — category=FPGA

### LeakageModel (3)

- **Hamming Distance** — requirements=hardware implementation with register storage
- **Hamming distance** — requirements=reference_state=0xB7
- **Hamming distance between x_i(r) and x_i(r+1)** — requirements=between x_i(r) and x_i(r+1)

### Pipeline (7)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **MathMagic CPA Analysis Program for AES** — source=manual, trigger_condition=performing CPA analysis on AES implemented on SAKURA-G FPGA board, applicable_scenarios=CPA on AES-128 implemented in FPGA, using power consumption traces
- **Theoretical prediction of the correlation power analysis** — source=paper, trigger_condition=when evaluating the security of an FPGA implementation against CPA, applicable_scenarios=evaluating the success rate of a CPA attack on an FPGA implementation of a block cipher
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

### Preprocessing (2)

- **Static Alignment** — category=alignment
- **Static alignment** — category=alignment

### StatMethod (5)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled

## 2. Relationships (25)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: XOR operation output, support_count=1, confidence=0.2, source_papers=["TOOL-01-18-2023-NewAE-CW-SCA201-Lab3_1B-AES256-RE"]]]→ `AttackPoint:XOR operation output`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[works_with [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `Algorithm:SM4`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[works_with [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `StatMethod:Welch's t-test`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[works_with [source_text=攻击结果表明使用主成分分析预处理对攻击效果的影响不大，所需要的轨迹条数也没有增加，只需要500条，但是能使需要分析的数据量减少了5倍, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `Preprocessing:Principal Component Analysis`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[works_with [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `TraceType:Power`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[acquires_via [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `TraceType:Power`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use non-encryption flat region as reference, condition=when baseline drift is visible (e.g., non-contact EM, FPGA/ASIC), source_text=Vertical alignment, support_count=1]]→ `Preprocessing:Vertical alignment`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Reference peak must be inside candidate interval, set max_shift based on actual peak position variation, condition=only if first CPA falls in gray/red band (high_confidence_count below threshold), source_text=Static alignment, support_count=1]]→ `Preprocessing:Static alignment`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=If verification fails, use key_search with merged CPA details, condition=requires plaintext and ciphertext, source_text=Key verification and recovery, support_count=1]]→ `ValidationMethod:Key verification and recovery`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use conservative candidates, consider merging multiple CPA results if needed, condition=after optional alignment steps, source_text=Full CPA, support_count=1]]→ `StatMethod:Full CPA`
- `Pipeline:Unified Analysis Process (8 Steps)` —[consists_of [parameters_note=Use conservative candidates (10-20), read gap_pct and high_confidence_count, condition=direct CPA probe to decide whether alignment is needed, source_text=First CPA probe (without alignment), support_count=1]]→ `StatMethod:First CPA probe (without alignment)`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:Use Hamming distance between the output and input of the last round as the leakage model.`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:Use Hamming distance model for byte update operations`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:try different power models (bit, Hamming weight, Hamming distance, zero-value) to see which yields the highest and most distinct peak for a single key hypothesis`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:try Hamming distance model (for register transitions) or zero-value model (for S-boxes with low power at zero) for hardware implementations`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:Use target S-box_in_xor_prev_ct (or other HD targets) with HW model, and enable dual mode for linear HD targets.`
- `Preprocessing:Static Alignment` —[strategy_applies_to [source=expert_experience, condition=Any static_aligner invocation returns acceptance_rate < 70% on the target ROI; OR agent is deciding whether to run CPA on already-aligned traces where acceptance_rate < 70%, applicability=specific]]→ `Strategy:Static aligner tuning loop: monotonic acceptance, priority-ordered parameter sweep, 70% gate before aligned CPA`
- `Preprocessing:Static Alignment` —[strategy_applies_to [source=expert_experience, condition=Software cryptographic implementation (any MCU: STM32F1/F4/Cortex/AVR/Arduino; or contact smartcard running software crypto) + non-profiled CPA + direct CPA returns unstable high_confidence_count below empirical_threshold, applicability=specific]]→ `Strategy:Software implementation: variance-first ROI exploration before alignment`
- `Preprocessing:Static Alignment` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Preprocessing:Static Alignment` —[strategy_applies_to [source=expert_experience, condition=Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap), applicability=specific]]→ `Strategy:Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)`
- `Preprocessing:Static Alignment` —[strategy_applies_to [source=expert_experience, condition=Picking alignment reference peak on any long (>2000 samples) waveform, applicability=specific]]→ `Strategy:Do NOT use np.argmax(wave) as alignment reference—select from non-encryption flat region`

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

### Obs: `leakage_model_selection` — any
- **Cause** (high): CMOS FPGA power consumption is proportional to switching activity, making bit transition model effective
- **Check**: Experimental correlation between global prediction vector (bit transitions) and global consumption vector (measured power) was approximately 0.45
- **Action**: Use Hamming weight of register transitions as selection function for power prediction
  - operation: `switch_component`
  - target: `LeakageModel`
  - strategy: Model power consumption as the number of bit transitions in target registers at the targeted clock cycle.
- **Relates to**: LeakageModel:`Hamming Weight of transitions`

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

### Obs: `alignment_speed` — when using static alignment on large trace sets
- **Cause** (high): Calculating similarity at every sample point is computationally expensive
- **Check**: Measure alignment time for large trace sets
- **Action**: Use fast alignment with a step parameter to skip some sample points in similarity calculation
  - operation: `adjust_param`
  - target: `alignment.step`
  - strategy: Set the step to a value that balances speed and accuracy (e.g., 2, 3, etc.)
- **Relates to**: Preprocessing:`Static Alignment`

### Obs: `alignment_quality` — misaligned in S-box lookup area
- **Cause** (high): S-box lookup order is randomized, causing misalignment in the S-box lookup area
- **Check**: By visually inspecting the traces
- **Action**: Use static alignment with a high threshold (e.g., 0.90) on the S-box lookup area to select traces with the same S-box order
  - operation: `adjust_param`
  - target: `StaticAlign.threshold`
  - strategy: Use static alignment with a high threshold (e.g., 0.90) on the S-box lookup area to select traces with the same S-box order
- **Relates to**: Preprocessing:`Static Alignment`

### Obs: `alignment_method_applicability` — any
- **Cause** (high): Static alignment cannot handle non-linear misalignment from countermeasures like random delays or clock randomization
- **Action**: Switch to dynamic alignment technique
  - operation: `switch_component`
  - target: `alignment method`
  - strategy: Use dynamic alignment which matches different segments of the curve with different offsets and performs non-linear sampling to align different parts to the same position.

### Obs: `cpa_high_confidence_count` — any
- **Cause** (high): Static alignment is not always necessary and may worsen results if aligned to wrong peak.
- **Action**: Perform direct CPA first. If high_confidence_count is in green band (AES≥13, DES≥6, SM4 per round≥3), skip static alignment.
  - operation: `skip_step`
  - target: `static_alignment`
  - strategy: Always try direct CPA before deciding to align.
- **Relates to**: Preprocessing:`Static Alignment`

### Obs: `alignment_quality` — waveform segments after the aligned region remain misaligned
- **Cause** (high): Random process interrupts and random clock delays cause non-linear misalignment that static (shift-only) alignment cannot correct
- **Check**: Inspect waveform segments after the aligned region for remaining misalignment
- **Action**: Use elastic alignment (non-linear resampling) instead of static alignment
  - operation: `switch_component`
  - target: `alignment.method`
  - strategy: Switch from static alignment to elastic alignment when static alignment fails to align the entire waveform
- **Relates to**: Preprocessing:`Static Alignment`

### Obs: `alignment_max_shift_coverage` — any
- **Cause** (high): To ensure the alignment search range covers the actual maximum left/right shift observed in the traces
- **Check**: Visually inspect sample traces to measure maximum left and right shifts
- **Action**: Set the maximum shift to be not less than the larger of the observed left and right shifts
  - operation: `adjust_param`
  - target: `alignment.max_shift`
  - strategy: Visually estimate the maximum left and right shift from a few sample traces before setting the parameter
- **Relates to**: Preprocessing:`Static Alignment`

### Obs: `reference_trace_selection` — any
- **Cause** (high): The second trace is often of good quality and representative of the trace set
- **Check**: Check trace quality metrics for early traces in the acquisition
- **Action**: Use the second trace as the reference trace for alignment
  - operation: `adjust_param`
  - target: `alignment.ref_trace`
  - strategy: Set the reference trace index to 1 (0-based) or 2 (1-based) depending on software convention
- **Relates to**: Preprocessing:`Static Alignment`

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

### ⭐ ⚠ [anti_pattern_set] alignment max_shift should start large (300+), not default to small
- **Trigger**: Any static_aligner invocation on smartcard / MCU traces
- **Rationale**: max_shift is the search radius for the reference peak. On smartcards and MCUs the peak jitter is on the order of hundreds of samples; a small radius discards most traces and can leave the true signal outside the window. Starting large costs only computation.
- **Anti-pattern 1**: Set max_shift=80 or 100 on first alignment attempt; when acceptance_rate < 90%, switch alignment method instead of enlarging max_shift.
  - Why: Smartcard waveform offsets routinely reach 300-500 sample points due to I/O jitter and card clock drift. max_shift too small causes >50% of traces to be discarded, and the surviving subset may not capture the real peak offset.
  - Correct: Initial max_shift: at least 300 (smartcard), 150-200 (MCU with stable clock). If acceptance_rate < 90%, FIRST double max_shift (300→600→1000) before considering alternate alignment methods. max_shift too large only costs a bit of compute, max_shift too small costs valid traces permanently.
- **Applies to**: Preprocessing:Static Alignment

### ⭐ ⚠ [anti_pattern_set] Do NOT use np.argmax(wave) as alignment reference—select from non-encryption flat region
- **Trigger**: Picking alignment reference peak on any long (>2000 samples) waveform
- **Rationale**: The global maximum of a trace is usually a trigger, I/O, or acquisition transient rather than the S-box interval. Aligning on it produces a high acceptance rate while tracking the wrong part of the trace, so the reference must be chosen inside the encryption body.
- **Anti-pattern 1**: Use np.argmax(wave) globally to pick the alignment reference, OR pick a prominent peak inside the encryption region as reference.
  - Why: Global argmax typically returns an I/O acknowledge peak or a clock-glitch spike, NOT the S-box leakage region. Peaks inside the encryption region fluctuate with plaintext, so their timing is not a stable alignment reference.
  - Correct: Alignment reference should be chosen from a FLAT non-encryption region (typically the idle segment before the first encryption peak). Use 'mean + 3σ' to find the first peak that crosses the threshold, not np.argmax.
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

### ⭐ 📋 [troubleshooting_checklist] Decision to perform static alignment based on direct CPA result
- **Trigger**: after first CPA probe (without alignment)
- **Rationale**: Direct CPA can succeed without alignment if the waveform is already focused on the encryption interval. Alignment is only needed when signal is insufficient.
- **[rank 1]** if `high_confidence_count for AES` → if ≥13, skip alignment; if 10-12, enter alignment and multi-strategy; if <10, must align
- **[rank 2]** if `high_confidence_count for DES` → if ≥6, skip alignment; if 5, enter alignment and multi-strategy; if <5, must align
- **[rank 3]** if `high_confidence_count for SM4 per round` → if ≥3, skip alignment; if 2, enter alignment and multi-strategy; if <2, must align
- **Applies to**: Preprocessing:Static Alignment, StatMethod:CPA

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

### 📋 [troubleshooting_checklist] EM trace filtering and alignment for DES
- **Trigger**: when EM traces are noisy and misaligned
- **Rationale**: Noisy EM traces can be aligned by extracting the envelope and then aligning the envelope signals.
- **[rank 1]** if `Isolate EM traces` → Use the Split module to separate EM traces from power traces.
- **[rank 2]** if `Analyze frequency spectrum` → Use the Spectrum module to identify dominant frequencies (e.g., 4 MHz external clock, 32.3 MHz internal clock).
- **[rank 3]** if `Remove external clock harmonics` → Use the Harmonics filter to block the external clock frequency and its harmonics.
- **[rank 4]** if `Extract envelope` → Take the absolute value and apply a low-pass filter (e.g., weight 100) to get the envelope.
- **[rank 5]** if `Align traces` → Use static alignment on the envelope traces with appropriate parameters (length, threshold).
- **Applies to**: Algorithm:DES, Preprocessing:Harmonics Filter, Preprocessing:Static Alignment

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-FPGA_GLM5_DKG_20260424_051544_313
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-FPGA_GLM5_DKG_20260424_051544_313/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 16,098→829

**🤖 LLM:** 我来帮你对FPGA硬件实现的AES进行CPA攻击。根据你的提示和FPGA硬件实现的特点，我会按照以下步骤进行：

1. **先观察波形特征**，判断是否需要纵向对齐
2. **直接进行CPA攻击**（硬件实现通常不需要滤波）
3. **使用Hamming Distance模型**（FPGA寄存器转换特性）

让我先加载并分析波形数据：

**🔧 → `python_jupyter`**

<details><summary>Code (818 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave = np.load(r'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy')
plain = np.load(r'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy')
cipher = np.load(r'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy')

print(f"波形形状: {wave.shape}")
print(f"明文形状: {plain.shape}")
print(f"密文形状: {cipher.shape}")
print(f"\n波形统计:")
print(f"  均值范围: {wave.mean(axis=1).min():.2f} ~ {wave.mean(axis=1).max():.2f}")
print(f"  标准差范围: {wave.std(axis=1).min():.2f} ~ {wave.std(axis=1).max():.2f}")
print(f"  全局均值: {wave.mean():.2f}")
print(f"  全局标准差: {wave.std():.2f}")
```
</details>

**📋 ← `python_jupyter`:** `波形形状: (2000, 300)
明文形状: (2000, 16)
密文形状: (2000, 16)

波形统计:
  均值范围: -25.80 ~ 7.51
  标准差范围: 15.16 ~ 17.81
  全局均值: -4.26
  全局标准差: 17.62`


---

### Round 2 | tokens: 16,626→658

**🔧 → `python_jupyter`**

<details><summary>Code (1307 chars)</summary>

```python
# 绘制波形特征
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 绘制前10条波形
ax1 = axes[0, 0]
for i in range(10):
    ax1.plot(wave[i], alpha=0.6, linewidth=0.8)
ax1.set_title('前10条波形叠加', fontsize=12)
ax1.set_xlabel('采样点')
ax1.set_ylabel('功耗值')
ax1.grid(True, alpha=0.3)

# 2. 绘制平均波形
ax2 = axes[0, 1]
mean_wave = wave.mean(axis=0)
ax2.plot(mean_wave, color='red', linewidth=1.5)
ax2.set_title('平均波形', fontsize=12)
ax2.set_xlabel('采样点')
ax2.set_ylabel('功耗值')
ax2.grid(True, alpha=0.3)

# 3. 绘制每条轨迹的均值（检查基线漂移）
ax3 = axes[1, 0]
trace_means = wave.mean(axis=1)
ax3.plot(trace_means, alpha=0.7)
ax3.axhline(y=trace_means.mean(), color='red', linestyle='--', label=f'全局均值: {trace_means.mean():.2f}')
ax3.set_title('每条轨迹的均值（基线漂移检测）', fontsize=12)
ax3.set_xlabel('轨迹编号')
ax3.set_ylabel('均值')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. 绘制方差分布
ax4 = axes[1, 1]
variance = np.var(wave, axis=0)
ax4.plot(variance, color='green', linewidth=1.5)
ax4.set_title('各采样点的方差', fontsize=12)
ax4.set_xlabel('采样点')
ax4.set_ylabel('方差')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('waveform_analysis.png', dpi=150)
plt.show()

print("\n基线漂移分析:")
print(f"  均值标准差: {trace_means.std():.2f}")
print(f"  均值极差: {trace_means.max() - trace_means.min():.2f}")
print(f"\n判断: {'需要纵向对齐' if trace_means.std() > 5 else '可能不需要纵向对齐'}")
```
</details>

**📋 ← `python_jupyter`:** `基线漂移分析:
  均值标准差: 5.78
  均值极差: 33.31

判断: 需要纵向对齐
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1001252470.py:44: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 17,259→570

**🤖 LLM:** 波形分析显示存在明显的基线漂移（均值标准差5.78，极差33.31），**需要纵向对齐**。

现在让我先进行纵向对齐，然后尝试直接CPA攻击。对于FPGA硬件实现，我会使用Hamming Distance模型：

**🔧 → `python_jupyter`**

<details><summary>Code (632 chars)</summary>

```python
# 查看波形前段，选择平坦区域作为基线参考
fig, ax = plt.subplots(figsize=(12, 5))

# 绘制平均波形的前100个点
ax.plot(mean_wave[:100], color='blue', linewidth=1.5, label='平均波形')
ax.axhline(y=mean_wave[:100].mean(), color='red', linestyle='--', alpha=0.5, label='前100点均值')
ax.set_title('平均波形前100点（选择基线参考区域）', fontsize=12)
ax.set_xlabel('采样点')
ax.set_ylabel('功耗值')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('baseline_region.png', dpi=150)
plt.show()

# 查看前30点的平坦程度
print(f"\n前30点统计:")
print(f"  均值: {mean_wave[:30].mean():.2f}")
print(f"  标准差: {mean_wave[:30].std():.2f}")
print(f"  极差: {mean_wave[:30].max() - mean_wave[:30].min():.2f}")
```
</details>

**📋 ← `python_jupyter`:** `前30点统计:
  均值: 4.91
  标准差: 0.23
  极差: 0.77
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\3580717549.py:15: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 4 | tokens: 17,671→260

**🤖 LLM:** 前30点非常平坦（标准差0.23），适合作为基线参考区域。现在进行纵向对齐：

**🔧 → `vertical_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy",
  "ref_start": 0,
  "ref_end": 30,
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `vertical_aligner`</b> (654 chars)</summary>

```
{"out_wave_npy": "valigned_20260424_051701_546592.npy", "plot_path": "valign_compare_20260424_051701_546592.png", "n_traces": 2000, "n_points": 300, "ref_region": [0, 30], "baseline_std": 5.7737, "baseline_std_after": 1e-06, "out_plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy", "out_ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy"}
```
</details>


![valign_compare_20260424_051701_546592.png](./valign_compare_20260424_051701_546592.png)


---

### Round 5 | tokens: 18,211→376

**🤖 LLM:** 纵向对齐成功！基线标准差从5.77降至几乎为0。现在进行CPA攻击，使用FPGA硬件的Hamming Distance模型：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "valigned_20260424_051701_546592.npy",
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy",
  "target": "S-box_in_xor_prev_ct",
  "leakage_model": "HW",
  "candidates": 30
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2038 chars)</summary>

```
[CPA] target=S-box_in_xor_prev_ct + HW: 硬件 HD 线性模型，启用 dual 模式返回正负两套候选（由下游验证器选出正确的那一套）
{"corr_mode": "dual", "note": "Hardware HD model produces TWO candidate keys due to k<->k^0xFF symmetry. Verify BOTH with encrypt_decrypt_verify to find the correct one.", "recovered_key_pos": "FEDCBA98765432100123456789ABCDEF", "recovered_key_neg": "0123456789ABCDEFFEDCBA9876543210", "n_traces": 2000, "target": "S-box_in_xor_prev_ct", "plot_path": "cpa_result_20260424_051711_567777.png", "detail_file": "cpa_detail_20260424_051711_567777.json", "per_byte": [{"byte": 0, "key_pos": "0xFE", "key_neg": "0x01", "score_pos": 0.196, "score_neg": 0.196}, {"byte": 1, "key_pos": "0xDC", "key_neg": "0x23", "score_pos": 0.1914, "score_neg": 0.1914}, {"byte": 2, "key_pos": "0xBA", "key_neg": "0x45", "score_pos": 0.1677, "score_neg": 0.1677}, {"byte": 3, "key_pos": "0x98", "key_neg": "0x67", "score_pos": 0.1764, "score_neg": 0.1764}, {"byte": 4, "key_pos": "0x76", "key_neg": "0x89", "score_pos": 0.1837, "score_neg": 0.1837}, {"byte": 5, "key_pos": "0x54", "key_neg": "0xAB", "score_pos": 0.1826, "score_neg": 0.1826}, {"byte": 6, "key_pos": "0x32", "key_neg": "0xCD", "score_pos": 0.1801, "score_neg": 0.1801}, {"byte": 7, "key_pos": "0x10", "key_neg": "0xEF", "score_pos": 0.1672, "score_neg": 0.1672}, {"byte": 8, "key_pos": "0x01", "key_neg": "0xFE", "score_pos": 0.1438, "score_neg": 0.1438}, {"byte": 9, "key_pos": "0x23", "key_neg": "0xDC", "score_pos": 0.1616, "score_neg": 0.1616}, {"byte": 10, "key_pos": 
...(truncated)
```
</details>


![cpa_result_20260424_051711_567777.png](./cpa_result_20260424_051711_567777.png)


---

### Round 6 | tokens: 19,329→307

**🤖 LLM:** CPA攻击成功！由于Hamming Distance模型的对称性，返回了两套候选密钥。现在验证哪一套是正确的：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "key_hex": "FEDCBA98765432100123456789ABCDEF",
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy",
  "trace_index": 0
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "8870EB9379649515EAF155084DDDF90A", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: b9d1c48e348fe771fa464a77a178fb07... → 8870EB9379649515EAF155084DDDF90A...\n❌ Key verification FAILED — 16/16 ciphertext bytes differ\n   Expected:  51CD9CB46DB542EEC5843F16FC07CAD9\n   Got:       8870EB9379649515EAF155084DDDF90A\n\n   ⚠️ IMPORTANT: '16 ciphertext bytes differ' does NOT mean '16 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 7 | tokens: 19,863→185

**🤖 LLM:** 第一套密钥验证失败，验证第二套：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "algorithm": "AES",
  "key_hex": "0123456789ABCDEFFEDCBA9876543210",
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy",
  "trace_index": 0
}
```
</details>

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "51CD9CB46DB542EEC5843F16FC07CAD9", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: b9d1c48e348fe771fa464a77a178fb07... → 51CD9CB46DB542EEC5843F16FC07CAD9...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 8 | tokens: 20,153→1,531

<details><summary><b>🤖 LLM Reasoning</b> (832 chars)</summary>

🎉 **CPA攻击成功！**

## 攻击结果

**恢复的密钥**: `0123456789ABCDEFFEDCBA9876543210`

✅ 密钥验证通过！

## 攻击过程总结

### 1. 波形分析
- 波形形状: 2000条轨迹 × 300采样点
- **基线漂移检测**: 均值标准差 = 5.78，极差 = 33.31
- **结论**: 存在明显的基线漂移，需要纵向对齐

### 2. 纵向对齐
- 参考区域: 前30个采样点（平坦区域）
- 对齐效果: 基线标准差从 5.77 降至 ≈0

### 3. CPA攻击配置
- **目标**: `S-box_in_xor_prev_ct`（FPGA寄存器转换）
- **泄漏模型**: Hamming Weight (HW)
- **相关系数模式**: dual（Hamming Distance模型的对称性）
- **轨迹数量**: 2000条

### 4. 密钥验证
由于Hamming Distance模型的k↔k^0xFF对称性，CPA返回了两套候选密钥：
- 候选1: `FEDCBA98765432100123456789ABCDEF` ❌ 验证失败
- 候选2: `0123456789ABCDEFFEDCBA9876543210` ✅ **验证成功**

### 5. 各字节相关性
所有16字节的相关系数在 0.14-0.20 范围内，信号质量良好：
- 最高: Byte 0 (0.196), Byte 13 (0.194), Byte 15 (0.192)
- 最低: Byte 8 (0.144)

## 关键经验

1. **FPGA硬件实现确实需要纵向对齐**（基线漂移明显）
2. **不需要滤波**（硬件实现信号较清晰）
3. **Hamming Distance模型**对FPGA寄存器转换非常有效
4. **dual模式**自动处理了HD模型的对称性问题

</details>

**🔧 → `python_jupyter`**

<details><summary>Code (2357 chars)</summary>

```python
# 生成最终报告图表
import matplotlib.pyplot as plt
import json

# 读取CPA详细结果
with open('cpa_detail_20260424_051711_567777.json', 'r') as f:
    cpa_detail = json.load(f)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 纵向对齐前后对比
ax1 = axes[0, 0]
wave_raw = np.load(r'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy')
wave_aligned = np.load('valigned_20260424_051701_546592.npy')
for i in range(5):
    ax1.plot(wave_raw[i] + i*20, alpha=0.5, linewidth=0.8, label=f'Raw {i}' if i == 0 else '')
    ax1.plot(wave_aligned[i] + i*20, alpha=0.8, linewidth=1.2, label=f'Aligned {i}' if i == 0 else '')
ax1.set_title('纵向对齐前后对比（前5条轨迹）', fontsize=12)
ax1.set_xlabel('采样点')
ax1.set_ylabel('功耗值（偏移显示）')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. 各字节相关性
ax2 = axes[0, 1]
correlations = [byte_info['score_pos'] for byte_info in cpa_detail['per_byte']]
bytes_idx = list(range(16))
bars = ax2.bar(bytes_idx, correlations, color='steelblue', alpha=0.7)
ax2.axhline(y=np.mean(correlations), color='red', linestyle='--', label=f'平均: {np.mean(correlations):.3f}')
ax2.set_title('各字节CPA相关性', fontsize=12)
ax2.set_xlabel('字节索引')
ax2.set_ylabel('相关系数')
ax2.set_xticks(bytes_idx)
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# 3. 恢复的密钥可视化
ax3 = axes[1, 0]
key_hex = '0123456789ABCDEFFEDCBA9876543210'
key_bytes = [int(key_hex[i*2:i*2+2], 16) for i in range(16)]
ax3.bar(bytes_idx, key_bytes, color='green', alpha=0.7)
ax3.set_title(f'恢复的密钥: {key_hex}', fontsize=12)
ax3.set_xlabel('字节索引')
ax3.set_ylabel('字节值')
ax3.set_xticks(bytes_idx)
ax3.grid(True, alpha=0.3, axis='y')

# 4. 攻击成功标志
ax4 = axes[1, 1]
ax4.text(0.5, 0.6, '✅ CPA攻击成功！', fontsize=24, ha='center', va='center', 
         fontweight='bold', color='green', transform=ax4.transAxes)
ax4.text(0.5, 0.4, f'密钥: {key_hex}', fontsize=14, ha='center', va='center',
         fontfamily='monospace', transform=ax4.transAxes)
ax4.text(0.5, 0.25, f'轨迹数: 2000 | 模型: HD (S-box_in_xor_prev_ct)', fontsize=11, 
         ha='center', va='center', transform=ax4.transAxes)
ax4.axis('off')

plt.tight_layout()
plt.savefig('final_attack_report.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "="*60)
print("FPGA AES-128 CPA攻击完成")
print("="*60)
print(f"恢复密钥: {key_hex}")
print(f"验证状态: ✅ 成功")
print(f"平均相关性: {np.mean(correlations):.4f}")
print("="*60)
```
</details>

**❌ ← `python_jupyter` Error:**

```
---ERROR---
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
Cell In[359], line 26
     24 # 2. 各字节相关性
     25 ax2 = axes[0, 1]
---> 26 correlations = [byte_info['score_pos'] for byte_info in cpa_detail['per_byte']]
     27 bytes_idx = list(range(16))
     28 bars = ax2.bar(bytes_idx, correlations, color='steelblue', alpha=0.7)

KeyError: 'per_byte'
```


---

### Round 9 | tokens: 21,935→137

**🔧 → `python_jupyter`**

<details><summary>Code (352 chars)</summary>

```python
# 检查JSON结构
import json
with open('cpa_detail_20260424_051711_567777.json', 'r') as f:
    cpa_detail = json.load(f)
print("JSON keys:", cpa_detail.keys() if isinstance(cpa_detail, dict) else type(cpa_detail))
print("\nFirst few entries:")
if isinstance(cpa_detail, dict):
    for k, v in list(cpa_detail.items())[:3]:
        print(f"  {k}: {type(v)}")
```
</details>

**📋 ← `python_jupyter`:** `JSON keys: dict_keys(['n_traces', 'n_points', 'leakage_model', 'target', 'corr_mode', 'results'])

First few entries:
  n_traces: <class 'int'>
  n_points: <class 'int'>
  leakage_model: <class 'str'>`


---

### Round 10 | tokens: 22,128→963

**🔧 → `python_jupyter`**

<details><summary>Code (2433 chars)</summary>

```python
# 生成最终报告图表
import matplotlib.pyplot as plt
import json
import numpy as np

# 读取CPA详细结果
with open('cpa_detail_20260424_051711_567777.json', 'r') as f:
    cpa_detail = json.load(f)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 纵向对齐前后对比
ax1 = axes[0, 0]
wave_raw = np.load(r'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy')
wave_aligned = np.load('valigned_20260424_051701_546592.npy')
for i in range(5):
    ax1.plot(wave_raw[i] + i*20, alpha=0.5, linewidth=0.8, label=f'Raw {i}' if i == 0 else '')
    ax1.plot(wave_aligned[i] + i*20, alpha=0.8, linewidth=1.2, label=f'Aligned {i}' if i == 0 else '')
ax1.set_title('纵向对齐前后对比（前5条轨迹）', fontsize=12)
ax1.set_xlabel('采样点')
ax1.set_ylabel('功耗值（偏移显示）')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. 各字节相关性
ax2 = axes[0, 1]
# 从results中提取相关性
results = cpa_detail['results']
correlations = [results[str(i)]['top_candidates'][0]['correlation'] for i in range(16)]
bytes_idx = list(range(16))
bars = ax2.bar(bytes_idx, correlations, color='steelblue', alpha=0.7)
ax2.axhline(y=np.mean(correlations), color='red', linestyle='--', label=f'平均: {np.mean(correlations):.3f}')
ax2.set_title('各字节CPA相关性', fontsize=12)
ax2.set_xlabel('字节索引')
ax2.set_ylabel('相关系数')
ax2.set_xticks(bytes_idx)
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# 3. 恢复的密钥可视化
ax3 = axes[1, 0]
key_hex = '0123456789ABCDEFFEDCBA9876543210'
key_bytes = [int(key_hex[i*2:i*2+2], 16) for i in range(16)]
ax3.bar(bytes_idx, key_bytes, color='green', alpha=0.7)
ax3.set_title(f'恢复的密钥: {key_hex}', fontsize=12)
ax3.set_xlabel('字节索引')
ax3.set_ylabel('字节值')
ax3.set_xticks(bytes_idx)
ax3.grid(True, alpha=0.3, axis='y')

# 4. 攻击成功标志
ax4 = axes[1, 1]
ax4.text(0.5, 0.6, '✅ CPA攻击成功！', fontsize=24, ha='center', va='center', 
         fontweight='bold', color='green', transform=ax4.transAxes)
ax4.text(0.5, 0.4, f'密钥: {key_hex}', fontsize=14, ha='center', va='center',
         fontfamily='monospace', transform=ax4.transAxes)
ax4.text(0.5, 0.25, f'轨迹数: 2000 | 模型: HD (S-box_in_xor_prev_ct)', fontsize=11, 
         ha='center', va='center', transform=ax4.transAxes)
ax4.axis('off')

plt.tight_layout()
plt.savefig('final_attack_report.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "="*60)
print("FPGA AES-128 CPA攻击完成")
print("="*60)
print(f"恢复密钥: {key_hex}")
print(f"验证状态: ✅ 成功")
print(f"平均相关性: {np.mean(correlations):.4f}")
print("="*60)
```
</details>

**❌ ← `python_jupyter` Error:**

```
---ERROR---
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[361], line 29
     27 # 从results中提取相关性
     28 results = cpa_detail['results']
---> 29 correlations = [results[str(i)]['top_candidates'][0]['correlation'] for i in range(16)]
     30 bytes_idx = list(range(16))
     31 bars = ax2.bar(bytes_idx, correlations, color='steelblue', alpha=0.7)

Cell In[361], line 29, in <listcomp>(.0)
     27 # 从results中提取相关性
     28 results = cpa_detail['results']
---> 29 correlations = [results[str(i)]['top_candidates'][0]['correlation'] for i in range(16)]
     30 bytes_idx = list(range(16))
     31 bars = ax2.bar(bytes_idx, correlations, color='steelblue', alpha=0.7)

TypeError: list indices must be integers or slices, not str
```


---

### Round 11 | tokens: 24,060→127

**🔧 → `python_jupyter`**

<details><summary>Code (374 chars)</summary>

```python
# 检查results结构
results = cpa_detail['results']
print(f"Results type: {type(results)}")
if isinstance(results, list):
    print(f"Results length: {len(results)}")
    print(f"First result keys: {results[0].keys() if isinstance(results[0], dict) else type(results[0])}")
    if isinstance(results[0], dict):
        print(f"First result sample: {list(results[0].items())[:3]}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (2108 chars)</summary>

```
Results type: <class 'list'>
Results length: 16
First result keys: dict_keys(['byte', 'topK', 'best_key', 'corr_mode', 'topK_pos', 'topK_neg', 'best_key_pos', 'best_key_neg'])
First result sample: [('byte', 0), ('topK', [{'key': 254, 'score': 0.19598972048084176, 'time_index': 234}, {'key': 1, 'score': 0.1959897204808316, 'time_index': 234}, {'key': 190, 'score': 0.17912998514672218, 'time_index': 234}, {'key': 65, 'score': 0.17912998514672218, 'time_index': 234}, {'key': 238, 'score': 0.17014723811699345, 'time_index': 234}, {'key': 17, 'score': 0.17014723811699345, 'time_index': 234}, {'key': 222, 'score': 0.16733815853429526, 'time_index': 234}, {'key': 33, 'score': 0.16733815853428502, 'time_index': 234}, {'key': 174, 'score': 0.1549974509305724, 'time_index': 234}, {'key': 81, 'score': 0.15499745093056214, 'time_index': 234}, {'key': 126, 'score': 0.15257887342918713, 'time_index': 232}, {'key': 129, 'score': 0.15257887342918713, 'time_index': 232}, {'key': 255, 'score': 0.1483635418765729, 'time_index': 242}, {'key': 0, 'score': 0.1483635418765729, 'time_index': 242}, {'key': 158, 'score': 0.14815742440760368, 'time_index': 234}, {'key': 97, 'score': 0.14815742440760368, 'time_index': 234}, {'key': 49, 'score': 0.14099756376910094, 'time_index': 234}, {'key': 206, 'score': 0.14099756376909192, 'time_index': 234}, {'key': 250, 'score': 0.13956936609125545, 'time_index': 234}, {'key': 5, 'score': 0.13956936609125545, 'time_index': 234}, {'key': 62, 'score': 0.135664105073
...(truncated)
```
</details>


---

### Round 12 | tokens: 25,155→976

**🔧 → `python_jupyter`**

<details><summary>Code (2395 chars)</summary>

```python
# 生成最终报告图表
import matplotlib.pyplot as plt
import json
import numpy as np

# 读取CPA详细结果
with open('cpa_detail_20260424_051711_567777.json', 'r') as f:
    cpa_detail = json.load(f)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 纵向对齐前后对比
ax1 = axes[0, 0]
wave_raw = np.load(r'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy')
wave_aligned = np.load('valigned_20260424_051701_546592.npy')
for i in range(5):
    ax1.plot(wave_raw[i] + i*20, alpha=0.5, linewidth=0.8, label=f'Raw {i}' if i == 0 else '')
    ax1.plot(wave_aligned[i] + i*20, alpha=0.8, linewidth=1.2, label=f'Aligned {i}' if i == 0 else '')
ax1.set_title('纵向对齐前后对比（前5条轨迹）', fontsize=12)
ax1.set_xlabel('采样点')
ax1.set_ylabel('功耗值（偏移显示）')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. 各字节相关性
ax2 = axes[0, 1]
results = cpa_detail['results']
correlations = [results[i]['topK'][0]['score'] for i in range(16)]
bytes_idx = list(range(16))
bars = ax2.bar(bytes_idx, correlations, color='steelblue', alpha=0.7)
ax2.axhline(y=np.mean(correlations), color='red', linestyle='--', label=f'平均: {np.mean(correlations):.3f}')
ax2.set_title('各字节CPA相关性', fontsize=12)
ax2.set_xlabel('字节索引')
ax2.set_ylabel('相关系数')
ax2.set_xticks(bytes_idx)
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# 3. 恢复的密钥可视化
ax3 = axes[1, 0]
key_hex = '0123456789ABCDEFFEDCBA9876543210'
key_bytes = [int(key_hex[i*2:i*2+2], 16) for i in range(16)]
ax3.bar(bytes_idx, key_bytes, color='green', alpha=0.7)
ax3.set_title(f'恢复的密钥: {key_hex}', fontsize=12)
ax3.set_xlabel('字节索引')
ax3.set_ylabel('字节值')
ax3.set_xticks(bytes_idx)
ax3.grid(True, alpha=0.3, axis='y')

# 4. 攻击成功标志
ax4 = axes[1, 1]
ax4.text(0.5, 0.6, '✅ CPA攻击成功！', fontsize=24, ha='center', va='center', 
         fontweight='bold', color='green', transform=ax4.transAxes)
ax4.text(0.5, 0.4, f'密钥: {key_hex}', fontsize=14, ha='center', va='center',
         fontfamily='monospace', transform=ax4.transAxes)
ax4.text(0.5, 0.25, f'轨迹数: 2000 | 模型: HD (S-box_in_xor_prev_ct)', fontsize=11, 
         ha='center', va='center', transform=ax4.transAxes)
ax4.axis('off')

plt.tight_layout()
plt.savefig('final_attack_report.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "="*60)
print("FPGA AES-128 CPA攻击完成")
print("="*60)
print(f"恢复密钥: {key_hex}")
print(f"验证状态: ✅ 成功")
print(f"平均相关性: {np.mean(correlations):.4f}")
print("="*60)
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1673 chars)</summary>

```
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\542084638.py:60: UserWarning: Glyph 9989 (\N{WHITE HEAVY CHECK MARK}) missing from font(s) SimHei.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\542084638.py:60: UserWarning: Glyph 23494 (\N{CJK UNIFIED IDEOGRAPH-5BC6}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\542084638.py:60: UserWarning: Glyph 38053 (\N{CJK UNIFIED IDEOGRAPH-94A5}) missing from font(s) DejaVu Sans Mono.
  plt.tight_layout()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\542084638.py:61: UserWarning: Glyph 9989 (\N{WHITE HEAVY CHECK MARK}) missing from font(s) SimHei.
  plt.savefig('final_attack_report.png', dpi=150, bbox_inches='tight')
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\542084638.py:61: UserWarning: Glyph 23494 (\N{CJK UNIFIED IDEOGRAPH-5BC6}) missing from font(s) DejaVu Sans Mono.
  plt.savefig('final_attack_report.png', dpi=150, bbox_inches='tight')
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\542084638.py:61: UserWarning: Glyph 38053 (\N{CJK UNIFIED IDEOGRAPH-94A5}) missing from font(s) DejaVu Sans Mono.
  plt.savefig('final_attack_report.png', dpi=150, bbox_inches='tight')

============================================================
FPGA AES-128 CPA攻击完成
============================================================
恢复密钥: 0123456789ABCDEFFEDCBA9876543210
验证状态: ✅ 成功
平均相关性: 0.1755
============================================
...(truncated)
```
</details>


![final_attack_report.png](./final_attack_report.png)


---

### Round 13 | tokens: 26,613→743

<details><summary><b>🤖 LLM Reasoning</b> (1342 chars)</summary>

## 🎉 FPGA AES-128 CPA攻击成功完成！

### 最终结果

**恢复的密钥**: `0123456789ABCDEFFEDCBA9876543210`

✅ **密钥验证通过** - 所有16字节匹配正确！

---

### 攻击过程总结

#### 1️⃣ 波形分析
- **数据规模**: 2000条轨迹 × 300采样点
- **基线漂移检测**: 
  - 均值标准差: 5.78
  - 均值极差: 33.31
- **结论**: 存在明显基线漂移，需要纵向对齐

#### 2️⃣ 纵向对齐
- **参考区域**: 前30个采样点（平坦区域，标准差仅0.23）
- **对齐效果**: 基线标准差从 5.77 降至 ≈0
- **保留轨迹**: 2000条（无丢弃）

#### 3️⃣ CPA攻击配置
| 参数 | 值 |
|------|-----|
| 目标 | `S-box_in_xor_prev_ct` |
| 泄漏模型 | Hamming Weight (HW) |
| 相关系数模式 | dual（处理HD对称性） |
| 轨迹数量 | 2000 |
| 候选数量 | 30 |

#### 4️⃣ 密钥验证
由于Hamming Distance模型的 **k ↔ k^0xFF 对称性**，CPA返回了两套候选密钥：

| 候选 | 密钥 | 验证结果 |
|------|------|----------|
| 正极性 | `FEDCBA98765432100123456789ABCDEF` | ❌ 失败 |
| **负极性** | **`0123456789ABCDEFFEDCBA9876543210`** | **✅ 成功** |

#### 5️⃣ 各字节相关性
- **平均相关性**: 0.1755
- **最高**: Byte 0 (0.196), Byte 13 (0.194), Byte 15 (0.192)
- **最低**: Byte 8 (0.144)
- **所有字节相关性均良好**，信号质量稳定

---

### 关键经验总结

| 经验点 | 结论 |
|--------|------|
| **纵向对齐** | ✅ FPGA硬件实现需要（基线漂移明显） |
| **滤波** | ❌ 不需要（硬件信号清晰） |
| **泄漏模型** | ✅ Hamming Distance有效（FPGA寄存器转换） |
| **dual模式** | ✅ 自动处理HD对称性问题 |
| **轨迹数量** | 2000条足够（相关性0.14-0.20） |

---

### 生成的文件

1. `valigned_20260424_051701_546592.npy` - 纵向对齐后的波形
2. `cpa_detail_20260424_051711_567777.json` - CPA详细结果
3. `cpa_result_20260424_051711_567777.png` - CPA相关性图
4. `final_attack_report.png` - 最终攻击报告图

攻击成功！🎯

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 16,098 | 829 | 16,927 |
| 2 | 16,626 | 658 | 17,284 |
| 3 | 17,259 | 570 | 17,829 |
| 4 | 17,671 | 260 | 17,931 |
| 5 | 18,211 | 376 | 18,587 |
| 6 | 19,329 | 307 | 19,636 |
| 7 | 19,863 | 185 | 20,048 |
| 8 | 20,153 | 1,531 | 21,684 |
| 9 | 21,935 | 137 | 22,072 |
| 10 | 22,128 | 963 | 23,091 |
| 11 | 24,060 | 127 | 24,187 |
| 12 | 25,155 | 976 | 26,131 |
| 13 | 26,613 | 743 | 27,356 |
| **Total** | **265,101** | **7,662** | **272,763** |

## 8. Final Output

## 🎉 FPGA AES-128 CPA攻击成功完成！

### 最终结果

**恢复的密钥**: `0123456789ABCDEFFEDCBA9876543210`

✅ **密钥验证通过** - 所有16字节匹配正确！

---

### 攻击过程总结

#### 1️⃣ 波形分析
- **数据规模**: 2000条轨迹 × 300采样点
- **基线漂移检测**: 
  - 均值标准差: 5.78
  - 均值极差: 33.31
- **结论**: 存在明显基线漂移，需要纵向对齐

#### 2️⃣ 纵向对齐
- **参考区域**: 前30个采样点（平坦区域，标准差仅0.23）
- **对齐效果**: 基线标准差从 5.77 降至 ≈0
- **保留轨迹**: 2000条（无丢弃）

#### 3️⃣ CPA攻击配置
| 参数 | 值 |
|------|-----|
| 目标 | `S-box_in_xor_prev_ct` |
| 泄漏模型 | Hamming Weight (HW) |
| 相关系数模式 | dual（处理HD对称性） |
| 轨迹数量 | 2000 |
| 候选数量 | 30 |

#### 4️⃣ 密钥验证
由于Hamming Distance模型的 **k ↔ k^0xFF 对称性**，CPA返回了两套候选密钥：

| 候选 | 密钥 | 验证结果 |
|------|------|----------|
| 正极性 | `FEDCBA98765432100123456789ABCDEF` | ❌ 失败 |
| **负极性** | **`0123456789ABCDEFFEDCBA9876543210`** | **✅ 成功** |

#### 5️⃣ 各字节相关性
- **平均相关性**: 0.1755
- **最高**: Byte 0 (0.196), Byte 13 (0.194), Byte 15 (0.192)
- **最低**: Byte 8 (0.144)
- **所有字节相关性均良好**，信号质量稳定

---

### 关键经验总结

| 经验点 | 结论 |
|--------|------|
| **纵向对齐** | ✅ FPGA硬件实现需要（基线漂移明显） |
| **滤波** | ❌ 不需要（硬件信号清晰） |
| **泄漏模型** | ✅ Hamming Distance有效（FPGA寄存器转换） |
| **dual模式** | ✅ 自动处理HD对称性问题 |
| **轨迹数量** | 2000条足够（相关性0.14-0.20） |

---

### 生成的文件

1. `valigned_20260424_051701_546592.npy` - 纵向对齐后的波形
2. `cpa_detail_20260424_051711_567777.json` - CPA详细结果
3. `cpa_result_20260424_051711_567777.png` - CPA相关性图
4. `final_attack_report.png` - 最终攻击报告图

攻击成功！🎯
