# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_052839_425 |
| Duration | 241.1s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_DSv3.2\AES-FPGA_DeepSeek-V3.2_DKG_20260424_052839_425` |
| Total LLM Calls | 11 |
| First Round | prompt: 15,324, completion: 791 |
| Last Round | prompt: 23,895, completion: 430 |
| Total Tokens | 221,468 (prompt: 216,682, completion: 4,786) |

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

LLM Response: ["AES", "FPGA", "Hardware Implementation", "CPA", "Hamming Distance", "Vertical Alignment"]

Parsed Keywords: `["AES", "FPGA", "Hardware Implementation", "CPA", "Hamming Distance", "Vertical Alignment"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 34489 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (36757 chars, click to expand)</summary>

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

**Search keywords** (6): AES, FPGA, Hardware Implementation, CPA, Hamming Distance, Vertical Alignment

**Summary**: 30 upper entities, 27 relationships, 12 diagnostic chains, 10 strategies


## 1. Upper Layer Entities (30)


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

### Pipeline (9)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **MathMagic CPA Analysis Program for AES** — source=manual, trigger_condition=performing CPA analysis on AES implemented on SAKURA-G FPGA board, applicable_scenarios=CPA on AES-128 implemented in FPGA, using power consumption traces
- **Theoretical prediction of the correlation power analysis** — source=paper, trigger_condition=when evaluating the security of an FPGA implementation against CPA, applicable_scenarios=evaluating the success rate of a CPA attack on an FPGA implementation of a block cipher
- **Correlation-Enhanced Collision Attack** — source=PAP-17-2010-CHES-Moradi-Collision-Correlation, trigger_condition=when attacking a masked or unprotected implementation of AES (or similar SPN cipher) with first-order leakage, applicable_scenarios=masked hardware implementations with remaining first-order leakage, unprotected implementations, known-plaintext or known-ciphertext scenarios
- **Welch's t-test and PCA based chosen-plaintext power analysis** — source=paper, trigger_condition=when attacking hardware implementations of SM4 with power traces, applicable_scenarios=hardware implementations of block ciphers where traditional byte-wise attacks are difficult due to parallel operations
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

### Preprocessing (3)

- **Vertical Alignment** — category=alignment
- **Vertical Alignment (baseline correction)** — category=alignment
- **Vertical alignment** — category=alignment

### StatMethod (5)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled

## 2. Relationships (27)

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
- `Pipeline:Welch's t-test and PCA based chosen-plaintext power analysis` —[consists_of [parameters_note=use incremental update for mean, variance, and t-value; choose selection function based on leakage model (e.g., function2 for two LSBs clustering), source_text=本文提出了一种基于Welch's t检验和主成分分析的选择明文功耗分析方法, support_count=1, is_optional=False]]→ `StatMethod:Welch's t-test`
- `Pipeline:Welch's t-test and PCA based chosen-plaintext power analysis` —[consists_of [parameters_note=select number of components such that cumulative contribution rate is sufficient, condition=when data dimensionality reduction is desired to improve analysis efficiency, source_text=本文提出了一种基于Welch's t检验和主成分分析的选择明文功耗分析方法, support_count=1]]→ `Preprocessing:Principal Component Analysis`
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
- `Preprocessing:Vertical Alignment` —[strategy_applies_to [source=expert_experience, condition=Software implementation (contact/contactless smartcard, MCU like STM32F1/F4/ARM Cortex) with baseline_std > 0 but no visible per-trace DC drift in the non-encryption region, applicability=specific]]→ `Strategy:Software implementations do NOT need vertical alignment by default`
- `Preprocessing:Vertical alignment` —[consists_of [parameters_note=Use non-encryption flat region as reference, condition=when baseline drift is visible (e.g., non-contact EM, FPGA/ASIC), source_text=Vertical alignment, support_count=1]]→ `Pipeline:Unified Analysis Process (8 Steps)`
- `Preprocessing:Vertical Alignment` —[works_with [source_text=非接触式AES测试卡测评示例, support_count=1, confidence=0.2, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Preprocessing:Static Alignment`
- `Preprocessing:Vertical Alignment` —[relates_to [role=add_step]]→ `Action:Perform vertical alignment using a flat non-encryption region (before encryption peaks) as reference. Subtract each trace's baseline mean.`
- `Preprocessing:Vertical Alignment` —[relates_to [role=add_step]]→ `Action:Normalize both leakages to have identical offsets`

## 3. Diagnostic Chains (12)


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

### Obs: `cpa_avg_correlation` — attacking last-round S-box input on an ASIC
- **Cause** (high): hardware implementations often have registers where power depends on the Hamming distance between successive values, or S-boxes consume less power for zero inputs
- **Check**: comparison of DPA results using different power models on an AES ASIC
- **Action**: try Hamming distance model (for register transitions) or zero-value model (for S-boxes with low power at zero) for hardware implementations
  - operation: `switch_component`
  - target: `power model`
  - strategy: Hamming distance model: power ∝ HD(previous value, current value); zero-value model: power is low only when data is zero
- **Relates to**: LeakageModel:`Hamming Distance`

### Obs: `leakage_model_selection` — any
- **Cause** (high): Hardware implementations combine operations and may process the last round in a single clock cycle, storing input and output in the same memory block. The last round is close to ciphertext, has AddRoundKey and SubBytes (nonlinear key addition), and no MixColumns, making it a suitable target. The reset assumption for Hamming weight may not hold, so Hamming distance is more appropriate.
- **Action**: Use Hamming distance between the output and input of the last round as the leakage model.
  - operation: `switch_component`
  - target: `leakage_model`
  - strategy: Switch from Hamming weight of S-box output (used for software) to Hamming distance of last round state for hardware AES.
- **Relates to**: LeakageModel:`Hamming Distance`

### Obs: `baseline_drift` — any
- **Cause** (high): Different traces have different baseline levels, which can drown CPA correlation.
- **Action**: Perform vertical alignment using a flat non-encryption region (before encryption peaks) as reference. Subtract each trace's baseline mean.
  - operation: `add_step`
  - target: `vertical_alignment`
  - strategy: Apply vertical alignment when DC offset is suspected, especially for hardware implementations and non-contact EM.
- **Relates to**: Preprocessing:`Vertical Alignment`

### Obs: `cpa_avg_correlation` — attacking S-box output on a microcontroller
- **Cause** (high): microcontroller uses a precharged bus, making power consumption inversely proportional to the Hamming weight of the data being processed
- **Check**: comparison of DPA results using different power models
- **Action**: use the Hamming weight model for microcontrollers with precharged buses
  - operation: `switch_component`
  - target: `power model`
  - strategy: instead of bit model, model power as HW(value) for such devices
- **Relates to**: LeakageModel:`Hamming Weight`
- **Alternatives**: Identity

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

### Obs: `attack_method_selection` — any
- **Cause** (high): Different methods offer trade-offs in resource usage, noise sensitivity, and result quality
- **Action**: Select method based on priorities: Correlation for best trade-off, Linear Regression for best results (requires ID leakage model), Differential for lower resource usage
  - operation: `adjust_param`
  - target: `attack_method`
  - strategy: Correlation is recommended for general use; Linear Regression yields best results but is resource-intensive; Differential is more noise-sensitive but uses fewer resources.
- **Relates to**: StatMethod:`CPA`

## 4. Strategies (10)


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

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_DSv3.2\AES-FPGA_DeepSeek-V3.2_DKG_20260424_052839_425
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_DSv3.2\AES-FPGA_DeepSeek-V3.2_DKG_20260424_052839_425/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 15,324→791

**🤖 LLM:** 我来帮您对FPGA硬件实现的AES进行CPA密钥恢复。根据您的描述，这是硬件实现，我需要特别注意：

1. **硬件特性**：FPGA实现通常需要Hamming Distance泄漏模型（寄存器切换）
2. **预处理**：可能需要纵向对齐（基线校正），但不需要滤波
3. **攻击点**：可能需要使用S-box_in_xor_prev_ct等硬件相关目标

让我先探索一下数据，了解波形特征。

**🔧 → `python_jupyter`**

<details><summary>Code (1602 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave_path = 'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy'
plaintext_path = 'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy'
ciphertext_path = 'data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy'

# 加载数据
waves = np.load(wave_path)
plaintexts = np.load(plaintext_path)
ciphertexts = np.load(ciphertext_path)

print(f"波形数据形状: {waves.shape}")
print(f"明文数据形状: {plaintexts.shape}")
print(f"密文数据形状: {ciphertexts.shape}")
print(f"数据类型: waves={waves.dtype}, plaintexts={plaintexts.dtype}, ciphertexts={ciphertexts.dtype}")

# 查看前几条波形
plt.figure(figsize=(15, 8))
for i in range(5):
    plt.plot(waves[i], alpha=0.7, label=f'Trace {i}')
plt.title('前5条波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('raw_waveforms.png')
plt.show()

# 查看波形统计信息
print(f"\n波形统计信息:")
print(f"  均值: {np.mean(waves):.4f}")
print(f"  标准差: {np.std(waves):.4f}")
print(f"  最小值: {np.min(waves):.4f}")
print(f"  最大值: {np.max(waves):.4f}")

# 查看基线漂移情况（前50个采样点）
baseline_region = waves[:, :50]
baseline_means = np.mean(baseline_region, axis=1)
print(f"\n基线区域（前50点）统计:")
print(f"  基线均值范围: {np.min(baseline_means):.4f} 到 {np.max(baseline_means):.4f}")
print(f"  基线标准差: {np.std(baseline_means):.4f}")

# 查看明文和密文示例
print(f"\n第一条明文（十六进制）: {plaintexts[0].tobytes().hex()}")
print(f"第一条密文（十六进制）: {ciphertexts[0].tobytes().hex()}")
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (2000, 300)
明文数据形状: (2000, 16)
密文数据形状: (2000, 16)
数据类型: waves=float32, plaintexts=uint8, ciphertexts=uint8

波形统计信息:
  均值: -4.2649
  标准差: 17.6175
  最小值: -91.4186
  最大值: 19.8727

基线区域（前50点）统计:
  基线均值范围: -16.3428 到 16.8513
  基线标准差: 5.7740

第一条明文（十六进制）: b9d1c48e348fe771fa464a77a178fb07
第一条密文（十六进制）: 51cd9cb46db542eec5843f16fc07cad9
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\647228204.py:29: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 2 | tokens: 16,366→746

**🤖 LLM:** 数据已加载。我有2000条轨迹，每条300个采样点。从基线统计看，基线均值范围从-16.34到16.85，标准差5.77，这表明存在明显的基线漂移，需要进行纵向对齐。

让我进一步分析波形特征：

**🔧 → `python_jupyter`**

<details><summary>Code (1700 chars)</summary>

```python
# 分析波形特征
plt.figure(figsize=(15, 10))

# 1. 平均波形
mean_wave = np.mean(waves, axis=0)
plt.subplot(2, 2, 1)
plt.plot(mean_wave)
plt.title('平均波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 2. 方差波形（识别高能量区域）
var_wave = np.var(waves, axis=0)
plt.subplot(2, 2, 2)
plt.plot(var_wave)
plt.title('方差波形（识别高能量区域）')
plt.xlabel('采样点')
plt.ylabel('方差')
plt.grid(True, alpha=0.3)

# 3. 前几条波形的基线区域
plt.subplot(2, 2, 3)
for i in range(10):
    plt.plot(waves[i, :50], alpha=0.5)
plt.title('前10条波形的基线区域（前50点）')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

# 4. 基线均值分布
plt.subplot(2, 2, 4)
plt.hist(baseline_means, bins=30, edgecolor='black', alpha=0.7)
plt.title('基线均值分布')
plt.xlabel('基线均值')
plt.ylabel('频数')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('wave_analysis.png')
plt.show()

# 识别高方差区域（可能的加密操作区域）
print("高方差区域分析:")
threshold = np.max(var_wave) * 0.3  # 30%最大方差作为阈值
high_var_indices = np.where(var_wave > threshold)[0]
print(f"  方差阈值: {threshold:.4f}")
print(f"  高方差区域: {high_var_indices[:20]}...")  # 显示前20个点
print(f"  高方差区域长度: {len(high_var_indices)}")

# 检查是否有明显的峰值
if len(high_var_indices) > 0:
    # 找到连续的高方差区域
    clusters = []
    current_cluster = [high_var_indices[0]]
    for i in range(1, len(high_var_indices)):
        if high_var_indices[i] - high_var_indices[i-1] == 1:
            current_cluster.append(high_var_indices[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [high_var_indices[i]]
    clusters.append(current_cluster)
    
    print(f"\n高方差聚类:")
    for i, cluster in enumerate(clusters[:5]):  # 显示前5个聚类
        print(f"  聚类{i+1}: 起始点={cluster[0]}, 结束点={cluster[-1]}, 长度={len(cluster)}")
```
</details>

**📋 ← `python_jupyter`:** `高方差区域分析:
  方差阈值: 43.9816
  高方差区域: [229 230 231]...
  高方差区域长度: 3

高方差聚类:
  聚类1: 起始点=229, 结束点=231, 长度=3
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\1629089677.py:41: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 17,241→429

**🤖 LLM:** 从分析结果看，波形有几个重要特征：
1. **基线漂移明显**：基线均值分布范围广（-16到16），标准差5.77，需要纵向对齐
2. **高方差区域有限**：只在229-231点有较高方差，这可能是加密操作区域
3. **波形相对简单**：每条轨迹只有300个点，可能已经截取到关键区域

根据DKG知识，对于FPGA硬件实现：
1. 需要纵向对齐处理基线漂移
2. 可能需要使用Hamming Distance泄漏模型
3. 攻击点可能需要选择硬件相关的目标（如S-box_in_xor_prev_ct）

让我先进行纵向对齐：

**🔧 → `vertical_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy",
  "ref_start": 0,
  "ref_end": 50,
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `vertical_aligner`</b> (653 chars)</summary>

```
{"out_wave_npy": "valigned_20260424_053009_596116.npy", "plot_path": "valign_compare_20260424_053009_596116.png", "n_traces": 2000, "n_points": 300, "ref_region": [0, 50], "baseline_std": 5.774, "baseline_std_after": 1e-06, "out_plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy", "out_ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy"}
```
</details>


![valign_compare_20260424_053009_596116.png](./valign_compare_20260424_053009_596116.png)


---

### Round 4 | tokens: 18,010→735

**🤖 LLM:** 纵向对齐已完成，基线标准差从5.77降低到接近0。现在让我检查对齐后的波形：

**🔧 → `python_jupyter`**

<details><summary>Code (1764 chars)</summary>

```python
# 检查纵向对齐后的波形
import numpy as np
import matplotlib.pyplot as plt

# 加载对齐后的波形
aligned_waves = np.load('valigned_20260424_053009_596116.npy')
print(f"对齐后波形形状: {aligned_waves.shape}")

# 比较对齐前后的基线
plt.figure(figsize=(15, 6))

# 对齐前的基线
original_waves = np.load('data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy')
original_baseline = np.mean(original_waves[:, :50], axis=1)

# 对齐后的基线
aligned_baseline = np.mean(aligned_waves[:, :50], axis=1)

plt.subplot(1, 2, 1)
plt.hist(original_baseline, bins=30, alpha=0.7, label='对齐前', edgecolor='black')
plt.hist(aligned_baseline, bins=30, alpha=0.7, label='对齐后', edgecolor='black')
plt.title('基线均值分布对比')
plt.xlabel('基线均值')
plt.ylabel('频数')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(original_baseline[:100], 'o-', alpha=0.7, label='对齐前')
plt.plot(aligned_baseline[:100], 'o-', alpha=0.7, label='对齐后')
plt.title('前100条轨迹的基线值')
plt.xlabel('轨迹索引')
plt.ylabel('基线均值')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('baseline_comparison.png')
plt.show()

# 查看对齐后的平均波形
mean_aligned = np.mean(aligned_waves, axis=0)
std_aligned = np.std(aligned_waves, axis=0)

plt.figure(figsize=(15, 5))
plt.subplot(1, 2, 1)
plt.plot(mean_aligned)
plt.title('对齐后平均波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(std_aligned)
plt.title('对齐后方差波形')
plt.xlabel('采样点')
plt.ylabel('标准差')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('aligned_wave_analysis.png')
plt.show()

print(f"\n对齐后波形统计:")
print(f"  均值: {np.mean(aligned_waves):.4f}")
print(f"  标准差: {np.std(aligned_waves):.4f}")
print(f"  最小值: {np.min(aligned_waves):.4f}")
print(f"  最大值: {np.max(aligned_waves):.4f}")
```
</details>

**📋 ← `python_jupyter`:** `对齐后波形形状: (2000, 300)

对齐后波形统计:
  均值: -9.3663
  标准差: 16.6446
  最小值: -79.2050
  最大值: 5.5183
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\23790392.py:39: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
C:\Users\Andersen\AppData\Local\Temp\ipykernel_1860\23790392.py:62: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 5 | tokens: 18,913→213

**🤖 LLM:** 纵向对齐效果很好，基线漂移已被消除。现在让我进行明文/密文相关性分析，以确定加密操作区域：

**🔧 → `plaintext_ciphertext_correlation`** `{
  "wave_npy": "valigned_20260424_053009_596116.npy",
  "data_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "data_type": "plaintext",
  "byte_index": 0,
  "model": "HW"
}`

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 122, "peak_region_end": 123, "peak_time_index": 123, "peak_correlation": 0.071, "suggested_cpa_range": [72, 173], "all_byte_peaks": [123, 108, 178, 288, 56, 294, 9, 284, 199, 220, 140, 274, 230, 11, 17, 252], "byte_peaks_std": 100.4, "plot_path": "correlation_20260424_053054_015422.png"}`


![correlation_20260424_053054_015422.png](./correlation_20260424_053054_015422.png)


---

### Round 6 | tokens: 19,281→228

**🤖 LLM:** 相关性分析显示峰值相关性较低（0.071），且不同字节的峰值位置分散（标准差100.4）。这表明可能需要尝试不同的泄漏模型或攻击点。让我也分析密文相关性：

**🔧 → `plaintext_ciphertext_correlation`** `{
  "wave_npy": "valigned_20260424_053009_596116.npy",
  "data_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy",
  "data_type": "ciphertext",
  "byte_index": 0,
  "model": "HW"
}`

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 267, "peak_region_end": 268, "peak_time_index": 268, "peak_correlation": 0.0794, "suggested_cpa_range": [217, 300], "all_byte_peaks": [268, 89, 277, 161, 201, 203, 105, 7, 75, 103, 184, 256, 123, 104, 280, 22], "byte_peaks_std": 85.9, "plot_path": "correlation_20260424_053108_769141.png"}`


![correlation_20260424_053108_769141.png](./correlation_20260424_053108_769141.png)


---

### Round 7 | tokens: 19,665→314

**🤖 LLM:** 密文相关性也较低。根据DKG知识，对于FPGA硬件实现，我应该尝试Hamming Distance泄漏模型。让我先尝试标准的S-box_out攻击（作为基准），然后尝试硬件相关的目标。

首先尝试标准的S-box_out攻击：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "wave_npy": "valigned_20260424_053009_596116.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 30
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (3548 chars)</summary>

```
{"recovered_key": "D6B7210FBF4C0F724D9D9DD5EFEE5111", "cpa_avg_correlation": 0.0987, "cpa_min_correlation": 0.0896, "n_traces": 2000, "target": "S-box_out", "plot_path": "cpa_result_20260424_053123_774583.png", "detail_file": "cpa_detail_20260424_053123_774583.json", "per_byte": [{"byte": 0, "key": "0xD6", "correlation": 0.101, "time_index": 81, "gap_pct": 5.0}, {"byte": 1, "key": "0xB7", "correlation": 0.0982, "time_index": 132, "gap_pct": 2.8}, {"byte": 2, "key": "0x21", "correlation": 0.1075, "time_index": 251, "gap_pct": 1.0}, {"byte": 3, "key": "0x0F", "correlation": 0.1076, "time_index": 69, "gap_pct": 9.8}, {"byte": 4, "key": "0xBF", "correlation": 0.0938, "time_index": 292, "gap_pct": 1.2}, {"byte": 5, "key": "0x4C", "correlation": 0.099, "time_index": 102, "gap_pct": 7.8}, {"byte": 6, "key": "0x0F", "correlation": 0.098, "time_index": 128, "gap_pct": 1.5}, {"byte": 7, "key": "0x72", "correlation": 0.0957, "time_index": 200, "gap_pct": 2.0}, {"byte": 8, "key": "0x4D", "correlation": 0.0942, "time_index": 124, "gap_pct": 7.8}, {"byte": 9, "key": "0x9D", "correlation": 0.1023, "time_index": 186, "gap_pct": 9.6}, {"byte": 10, "key": "0x9D", "correlation": 0.0896, "time_index": 116, "gap_pct": 1.8}, {"byte": 11, "key": "0xD5", "correlation": 0.1018, "time_index": 200, "gap_pct": 7.6}, {"byte": 12, "key": "0xEF", "correlation": 0.0974, "time_index": 135, "gap_pct": 3.4}, {"byte": 13, "key": "0xEE", "correlation": 0.1028, "time_index": 92, "gap_pct": 3.0}, {"byte": 14, "key
...(truncated)
```
</details>


![cpa_result_20260424_053123_774583.png](./cpa_result_20260424_053123_774583.png)


---

### Round 8 | tokens: 21,563→379

**🤖 LLM:** 标准S-box_out攻击效果不佳，没有高置信度的字节（0/16）。根据DKG知识，对于FPGA硬件实现，我应该尝试Hamming Distance模型。让我尝试硬件相关的目标：

1. **S-box_in_xor_prev_ct**：这是FPGA寄存器切换的典型目标
2. **S-box_in_xor_out**：S-box输入输出的Hamming Distance

首先尝试S-box_in_xor_prev_ct：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "wave_npy": "valigned_20260424_053009_596116.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy",
  "target": "S-box_in_xor_prev_ct",
  "leakage_model": "HW",
  "candidates": 30,
  "corr_mode": "dual"
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2036 chars)</summary>

```
[CPA] target=S-box_in_xor_prev_ct + HW: 硬件 HD 线性模型，启用 dual 模式返回正负两套候选（由下游验证器选出正确的那一套）
{"corr_mode": "dual", "note": "Hardware HD model produces TWO candidate keys due to k<->k^0xFF symmetry. Verify BOTH with encrypt_decrypt_verify to find the correct one.", "recovered_key_pos": "FEDCBA98765432100123456789ABCDEF", "recovered_key_neg": "0123456789ABCDEFFEDCBA9876543210", "n_traces": 2000, "target": "S-box_in_xor_prev_ct", "plot_path": "cpa_result_20260424_053150_343156.png", "detail_file": "cpa_detail_20260424_053150_343156.json", "per_byte": [{"byte": 0, "key_pos": "0xFE", "key_neg": "0x01", "score_pos": 0.196, "score_neg": 0.196}, {"byte": 1, "key_pos": "0xDC", "key_neg": "0x23", "score_pos": 0.192, "score_neg": 0.192}, {"byte": 2, "key_pos": "0xBA", "key_neg": "0x45", "score_pos": 0.1673, "score_neg": 0.1673}, {"byte": 3, "key_pos": "0x98", "key_neg": "0x67", "score_pos": 0.1757, "score_neg": 0.1757}, {"byte": 4, "key_pos": "0x76", "key_neg": "0x89", "score_pos": 0.1847, "score_neg": 0.1847}, {"byte": 5, "key_pos": "0x54", "key_neg": "0xAB", "score_pos": 0.1825, "score_neg": 0.1825}, {"byte": 6, "key_pos": "0x32", "key_neg": "0xCD", "score_pos": 0.1796, "score_neg": 0.1796}, {"byte": 7, "key_pos": "0x10", "key_neg": "0xEF", "score_pos": 0.1688, "score_neg": 0.1688}, {"byte": 8, "key_pos": "0x01", "key_neg": "0xFE", "score_pos": 0.1431, "score_neg": 0.1431}, {"byte": 9, "key_pos": "0x23", "key_neg": "0xDC", "score_pos": 0.1628, "score_neg": 0.1628}, {"byte": 10, "key_pos": "0
...(truncated)
```
</details>


![cpa_result_20260424_053150_343156.png](./cpa_result_20260424_053150_343156.png)


---

### Round 9 | tokens: 22,887→294

**🤖 LLM:** 很好！使用S-box_in_xor_prev_ct目标（硬件Hamming Distance模型）得到了显著更好的结果。相关性得分从之前的0.09-0.10提高到了0.14-0.19。由于这是硬件HD线性模型，它返回了两套候选密钥（正负对称）。

现在让我验证这两套密钥：

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "FEDCBA98765432100123456789ABCDEF",
  "algorithm": "AES",
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `encrypt_decrypt_verify`</b> (1081 chars)</summary>

```
{"result_hex": "8870EB9379649515EAF155084DDDF90A", "verification": "MISMATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: b9d1c48e348fe771fa464a77a178fb07... → 8870EB9379649515EAF155084DDDF90A...\n❌ Key verification FAILED — 16/16 ciphertext bytes differ\n   Expected:  51CD9CB46DB542EEC5843F16FC07CAD9\n   Got:       8870EB9379649515EAF155084DDDF90A\n\n   ⚠️ IMPORTANT: '16 ciphertext bytes differ' does NOT mean '16 key bytes are wrong'!\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes ALL ciphertext bytes to differ (diffusion property).\n   The CPA-recovered key may only have 1-3 wrong bytes.\n\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key.\n     It will automatically try alternative candidates for low-confidence bytes.\n   → If key_search is not available, check each byte's CPA correlation gap:\n     - gap > 15%: likely CORRECT (keep this byte)\n     - gap < 15%: likely WRONG (this byte needs correction)\n   → Do NOT discard the entire key or restart CPA from scratch."}
```
</details>


---

### Round 10 | tokens: 23,537→227

**🔧 → `encrypt_decrypt_verify`**

<details><summary>Arguments</summary>

```json
{
  "key_hex": "0123456789ABCDEFFEDCBA9876543210",
  "algorithm": "AES",
  "plaintext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy",
  "ciphertext_npy": "data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy"
}
```
</details>

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "51CD9CB46DB542EEC5843F16FC07CAD9", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: b9d1c48e348fe771fa464a77a178fb07... → 51CD9CB46DB542EEC5843F16FC07CAD9...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 11 | tokens: 23,895→430

<details><summary><b>🤖 LLM Reasoning</b> (870 chars)</summary>

太好了！第二套密钥 `0123456789ABCDEFFEDCBA9876543210` 验证成功！这意味着我们成功恢复了FPGA硬件实现的AES密钥。

让我总结一下攻击过程：

## 攻击总结

### 1. **数据特征分析**
- 2000条轨迹，每条300个采样点
- 明显的基线漂移（基线标准差5.77）
- 波形相对简单，可能已经截取到关键加密区域

### 2. **预处理步骤**
- **纵向对齐**：使用前50个采样点作为参考区域，成功消除基线漂移
- **无滤波**：根据DKG知识，硬件实现通常不需要滤波

### 3. **攻击策略**
1. **首次尝试**：标准S-box_out + HW模型 → 失败（0/16高置信度字节）
2. **硬件优化**：根据DKG知识，FPGA硬件实现需要使用Hamming Distance模型
3. **成功攻击**：使用S-box_in_xor_prev_ct目标 + HW模型 + dual模式

### 4. **成功关键**
- **正确的泄漏模型**：Hamming Distance模型适合FPGA硬件（寄存器切换）
- **正确的攻击点**：S-box_in_xor_prev_ct目标捕获了寄存器状态切换
- **dual模式**：正确处理了k<->k^0xFF对称性

### 5. **恢复的密钥**
```
成功密钥: 0123456789ABCDEFFEDCBA9876543210
验证: ✅ 完全匹配
```

### 6. **DKG知识应用验证**
从DKG检索的知识中，以下建议被证明是正确的：
- FPGA硬件实现需要纵向对齐（基线校正）
- 硬件实现应使用Hamming Distance泄漏模型
- 对于硬件HD线性模型，需要使用dual模式处理对称性
- 攻击点应选择硬件相关的目标（如S-box_in_xor_prev_ct）

这个案例展示了如何根据设备类型（FPGA硬件）选择合适的预处理和攻击策略，成功恢复了AES密钥。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 15,324 | 791 | 16,115 |
| 2 | 16,366 | 746 | 17,112 |
| 3 | 17,241 | 429 | 17,670 |
| 4 | 18,010 | 735 | 18,745 |
| 5 | 18,913 | 213 | 19,126 |
| 6 | 19,281 | 228 | 19,509 |
| 7 | 19,665 | 314 | 19,979 |
| 8 | 21,563 | 379 | 21,942 |
| 9 | 22,887 | 294 | 23,181 |
| 10 | 23,537 | 227 | 23,764 |
| 11 | 23,895 | 430 | 24,325 |
| **Total** | **216,682** | **4,786** | **221,468** |

## 8. Final Output

太好了！第二套密钥 `0123456789ABCDEFFEDCBA9876543210` 验证成功！这意味着我们成功恢复了FPGA硬件实现的AES密钥。

让我总结一下攻击过程：

## 攻击总结

### 1. **数据特征分析**
- 2000条轨迹，每条300个采样点
- 明显的基线漂移（基线标准差5.77）
- 波形相对简单，可能已经截取到关键加密区域

### 2. **预处理步骤**
- **纵向对齐**：使用前50个采样点作为参考区域，成功消除基线漂移
- **无滤波**：根据DKG知识，硬件实现通常不需要滤波

### 3. **攻击策略**
1. **首次尝试**：标准S-box_out + HW模型 → 失败（0/16高置信度字节）
2. **硬件优化**：根据DKG知识，FPGA硬件实现需要使用Hamming Distance模型
3. **成功攻击**：使用S-box_in_xor_prev_ct目标 + HW模型 + dual模式

### 4. **成功关键**
- **正确的泄漏模型**：Hamming Distance模型适合FPGA硬件（寄存器切换）
- **正确的攻击点**：S-box_in_xor_prev_ct目标捕获了寄存器状态切换
- **dual模式**：正确处理了k<->k^0xFF对称性

### 5. **恢复的密钥**
```
成功密钥: 0123456789ABCDEFFEDCBA9876543210
验证: ✅ 完全匹配
```

### 6. **DKG知识应用验证**
从DKG检索的知识中，以下建议被证明是正确的：
- FPGA硬件实现需要纵向对齐（基线校正）
- 硬件实现应使用Hamming Distance泄漏模型
- 对于硬件HD线性模型，需要使用dual模式处理对称性
- 攻击点应选择硬件相关的目标（如S-box_in_xor_prev_ct）

这个案例展示了如何根据设备类型（FPGA硬件）选择合适的预处理和攻击策略，成功恢复了AES密钥。
