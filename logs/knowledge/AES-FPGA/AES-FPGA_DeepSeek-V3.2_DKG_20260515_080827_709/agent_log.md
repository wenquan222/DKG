# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260515_080827_709 |
| Duration | 1055.7s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp_knowledge_only\AES-FPGA_DeepSeek-V3.2_DKG_20260515_080827_709` |
| Total LLM Calls | 20 |
| First Round | prompt: 13,962, completion: 617 |
| Last Round | prompt: 69,190, completion: 683 |
| Total Tokens | 768,268 (prompt: 748,117, completion: 20,151) |

## 3. User Query

```
帮我对一个FPGA硬件实现的AES密码算法波形进行CPA恢复密钥，这是硬件实现，可能不需要滤波，可能需要纵向对齐，泄漏模型可能需要用Hamming Distance。明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个FPGA硬件实现的AES密码算法波形进行CPA恢复密钥，这是硬件实现，可能不需要滤波，可能需要纵向对齐，泄漏模型可能需要用Hamming Distance。明文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy'，密文文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy',原始波形文件为'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy'"

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

LLM Response: ["AES", "FPGA", "Hardware Implementation", "CPA", "Hamming Distance", "Vertical Alignment", "Power"]

Parsed Keywords: `["AES", "FPGA", "Hardware Implementation", "CPA", "Hamming Distance", "Vertical Alignment", "Power"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 48650 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (51437 chars, click to expand)</summary>

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

**Search keywords** (7): AES, FPGA, Hardware Implementation, CPA, Hamming Distance, Vertical Alignment, Power

**Summary**: 34 upper entities, 32 relationships, 19 diagnostic chains, 14 strategies


## 1. Upper Layer Entities (34)


### Algorithm (1)

- **AES** — num_rounds=['10', '14'], encryption_mode=['CBC', 'ECB'], key_length=['128', '256']

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

### Pipeline (11)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **MathMagic CPA Analysis Program for AES** — source=manual, trigger_condition=performing CPA analysis on AES implemented on SAKURA-G FPGA board, applicable_scenarios=CPA on AES-128 implemented in FPGA, using power consumption traces
- **Theoretical prediction of the correlation power analysis** — source=paper, trigger_condition=when evaluating the security of an FPGA implementation against CPA, applicable_scenarios=evaluating the success rate of a CPA attack on an FPGA implementation of a block cipher
- **Correlation-Enhanced Collision Attack** — source=PAP-17-2010-CHES-Moradi-Collision-Correlation, trigger_condition=when attacking a masked or unprotected implementation of AES (or similar SPN cipher) with first-order leakage, applicable_scenarios=masked hardware implementations with remaining first-order leakage, unprotected implementations, known-plaintext or known-ciphertext scenarios
- **Welch's t-test and PCA based chosen-plaintext power analysis** — source=paper, trigger_condition=when attacking hardware implementations of SM4 with power traces, applicable_scenarios=hardware implementations of block ciphers where traditional byte-wise attacks are difficult due to parallel operations
- **DPA Attack** — source=book, trigger_condition=when an attacker has access to a cryptographic device and can measure power consumption during multiple encryptions/decryptions, applicable_scenarios=attacking symmetric block cipher implementations using power side channel
- **DPA/DEMA Leakage Analysis for Symmetric-Key Cryptosystems** — source=ISO/IEC 17825:2024, trigger_condition=Testing symmetric-key cryptosystems for side-channel resistance at security levels 3 or 4, applicable_scenarios=Differential power or electromagnetic analysis on symmetric block ciphers (e.g., AES, DES) to detect sensitive information leakage
- **Differential Power Analysis (DPA) on DES** — source=PAP-01-1999-CRYPTO-Kocher-DPA, trigger_condition=when an attacker can observe power consumption during cryptographic operations and record corresponding ciphertexts (or plaintexts), applicable_scenarios=DES implementations on smart cards or other devices where power consumption leaks information about intermediate values

### Preprocessing (3)

- **Vertical Alignment** — category=alignment
- **Vertical Alignment (baseline correction)** — category=alignment
- **Vertical alignment** — category=alignment

### StatMethod (7)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled
- **First CPA probe (without alignment)** — type=non_profiled
- **Compare hypothetical power consumption with measured traces** — type=non_profiled

## 2. Relationships (32)

- `Algorithm:AES` —[strategy_applies_to [source_text=参考波形号：1，最大偏移量：400，阈值：85，点长度：100, applicability=specific, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Strategy:Static alignment default parameter bundle for contact smartcard AES`
- `Algorithm:AES` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: first add round key, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:first add round key`
- `Algorithm:AES` —[has_attack_point [source_text=attack_point: offset, support_count=1, confidence=0.2, source_papers=["TOOL-10-01-2014-DPAContest-v4-README"]]]→ `AttackPoint:offset`
- `Algorithm:AES` —[has_attack_point [source_text=Attack targeted the first decryption round (using round 10 key schedule), support_count=32, confidence=1.0, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack", "BOOK-01-2010-THU-Mangard-PowerAnalysisAttacks-Chinese", "MAN-01-2024-MathMagic-AES-Contact-TestCard-Example", "MAN-04-2024-MathMagic-AES-Contactless-TestCard-Example", "MAN-05-2024-MathMagic-STM32F429-UART-AES-Example", "MAN-06-2024-MathMagic-Detector-1.7.2-Manual", "MAN-08-2024-Riscure-Inspector-Tutorials", "MAN-09-2024-Lab-SCA-Experiment-Guide-Integrated", "PAP-11-2008-CHES-Gierlichs-MIA", "PAP-29-2013-ASIACRYPT-Standaert-Behind-Scene", "PAP-32-2013-ePrint-Compare-Distinguishers", "PAP-52-2018-ePrint-EM-Protection-Ground-Bridge", "PAP-53-2018-ePrint-GPU-Bitsliced-AES", "PAP-59-2019-ePrint-SNR-Trace-Extractors", "PAP-74-2023-ePrint-AutoPOI", "PAP-77-2023-ePrint-Plaintext-Collision", "PAP-81-2024-ePrint-ARCHER-RISC-V", "PAP-93-2014-ePrint-OFlynn-AES256-Bootloader-CPA", "STD-02-2019-ePrint-Whitnall-ISO-17825-Critical", "TOOL-01-12-2023-NewAE-CW-SCA201-Lab1_1A-Resync-SAD", "TOOL-01-16-2023-NewAE-CW-SCA201-Lab2_3-MixColumns", "TOOL-01-17-2023-NewAE-CW-SCA201-Lab3_1A-AES256-Bootloader", "TOOL-03-05-2021-Ledger-Lascar-Tutorial07-DPA-Example", "TOOL-03-09-2021-Ledger-Lascar-Example-CPA-SecondOrder", "TOOL-03-11-2021-Ledger-Lascar-Example-CPA-FullRanks", "TOOL-07-03-2018-Riscure-Jlsca-RHme2-eSCAlate-AES", "TOOL-07-04-2018-Riscure-Jlsca-RHme2-StillNotScary-AES", "TOOL-07-05-2018-Riscure-Jlsca-RHme2017-WhiteBox-AES", "TOOL-07-06-2018-Riscure-Jlsca-SecondOrder-CPA-ASCAD", "TOOL-08-06-2019-ANSSI-SecAES-STM32-FirstOrder", "TOOL-08-07-2019-ANSSI-SecAES-STM32-SecondOrder", "TOOL-08-08-2019-ANSSI-SecAES-STM32-ThirdOrder"]]]→ `AttackPoint:S-box Output`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[works_with [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `Algorithm:SM4`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[works_with [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `StatMethod:Welch's t-test`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[works_with [source_text=攻击结果表明使用主成分分析预处理对攻击效果的影响不大，所需要的轨迹条数也没有增加，只需要500条，但是能使需要分析的数据量减少了5倍, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `Preprocessing:Principal Component Analysis`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[works_with [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `TraceType:Power`
- `DeviceClass:Artix-7 FPGA on CW305 board` —[acquires_via [source_text=从图5b)可以看出使用500条曲线就可以攻击成功，这种选择函数的攻击效果优于前两种的原因，在于它更加细化了对轨迹的分类，更好地利用了泄露的功耗信息。, support_count=1, confidence=0.2, source_papers=["PAP-97-2018-NetInfoSec-SM4-Hardware-PowerAnalysis"]]]→ `TraceType:Power`
- `Pipeline:Welch's t-test and PCA based chosen-plaintext power analysis` —[consists_of [parameters_note=use incremental update for mean, variance, and t-value; choose selection function based on leakage model (e.g., function2 for two LSBs clustering), source_text=本文提出了一种基于Welch's t检验和主成分分析的选择明文功耗分析方法, support_count=1, is_optional=False]]→ `StatMethod:Welch's t-test`
- `Pipeline:Welch's t-test and PCA based chosen-plaintext power analysis` —[consists_of [parameters_note=select number of components such that cumulative contribution rate is sufficient, condition=when data dimensionality reduction is desired to improve analysis efficiency, source_text=本文提出了一种基于Welch's t检验和主成分分析的选择明文功耗分析方法, support_count=1]]→ `Preprocessing:Principal Component Analysis`
- `StatMethod:CPA` —[strategy_applies_to [condition=Non-profiled CPA on DES (any device class: contact smartcard, contactless smartcard, FPGA, MCU). The DES CPA tool has returned a high-confidence round-1 48-bit subkey K1 (high_confidence_count >= 6/8 S-boxes, gap_pct >= 20%, avg_correlation reasonable for the device class), BUT encrypt_decrypt_verify against the DES master key has returned MISMATCH. The DES CPA tool may have populated a 'master_key' field with a placeholder (K1 zero-padded, K1 duplicated, or an arbitrary parity assignment) that is not the actual master key., applicability=specific, source_papers=["expert_experience.md-patch-004"]]]→ `Strategy:DES master key recovery from 48-bit round-1 subkey via PC-2 inverse + parity enumeration`
- `StatMethod:CPA` —[strategy_applies_to [condition=Any non-profiled CPA on AES / DES / SM4 across any device class (contact smartcard, contactless smartcard, MCU, FPGA) where a candidate ROI is to be chosen for static_aligner; in particular, whenever python_jupyter variance / energy-signature analysis and plaintext/ciphertext correlation analysis are both available and their top-scoring regions are DISJOINT (do not overlap), applicability=specific, source_papers=["expert_experience.md-patch-003.3"]]]→ `Strategy:Alignment anchor: variance-ROI precedence over plaintext/ciphertext-correlation ROI (smartcard + MCU)`
- `StatMethod:CPA` —[strategy_applies_to [source_text=I used a coarse SAD filter first... Then I used a secondary extremely fine SAD... I first attacked key bytes 0, 13, 10, 7 then realigned to the next mix word..., applicability=general, source_papers=["BLG-01-2023-Hypoxic-Practical-AES128-Firmware-Crack"]]]→ `Strategy:Two-stage SAD alignment and grouped attack for non-deterministic MixColumns`
- `StatMethod:CPA` —[strategy_applies_to [condition=Any non-profiled CPA workflow on AES / DES / SM4 across any device class. Triggered whenever the agent has obtained a CPA output (typically high_confidence_count, gap_pct, avg_correlation looking favourable for the device class) and is about to write a final natural-language success message to the user, OR is considering terminating the session., applicability=general, source_papers=["expert_experience.md-patch-005"]]]→ `Strategy:Do NOT declare key-recovery success based on CPA-internal metrics; encrypt_decrypt_verify MATCH is mandatory`
- `StatMethod:CPA` —[strategy_applies_to [condition=Non-profiled CPA on any symmetric block cipher (AES / DES / SM4); at least one prior CPA run (aligned or direct) has yielded high_confidence_count in or above the gray band (AES >= 10/16, DES >= 3/8, SM4 per-round >= 2/4); key_search was invoked once with default or near-default parameters and returned found=false; OR a dual-mode (e.g., linear-HD / S-box_in on contactless AES / DES) attack returned two candidates with per-byte gap_pct == 0, applicability=specific, source_papers=["expert_experience.md-patch-003.2"]]]→ `Strategy:key_search found=false is NOT CPA failure — escalate search budget + dual-mode both branches BEFORE pivoting any other dimension`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:Use Hamming distance model for byte update operations`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:try different power models (bit, Hamming weight, Hamming distance, zero-value) to see which yields the highest and most distinct peak for a single key hypothesis`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:Use Hamming distance between the output and input of the last round as the leakage model.`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:Use target S-box_in_xor_prev_ct (or other HD targets) with HW model, and enable dual mode for linear HD targets.`
- `LeakageModel:Hamming Distance` —[relates_to [role=switch_component]]→ `Action:try Hamming distance model (for register transitions) or zero-value model (for S-boxes with low power at zero) for hardware implementations`
- `Preprocessing:Vertical Alignment` —[strategy_applies_to [condition=Software implementation (contact/contactless smartcard, MCU like STM32F1/F4/ARM Cortex) with baseline_std > 0 but no visible per-trace DC drift in the non-encryption region, applicability=specific, source_papers=["expert_experience.md-patch-001"]]]→ `Strategy:Software implementations do NOT need vertical alignment by default`
- `Preprocessing:Vertical Alignment` —[works_with [source_text=非接触式AES测试卡测评示例, support_count=1, confidence=0.2, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `DeviceClass:Non-contact AES Test Card`
- `Preprocessing:Vertical Alignment` —[works_with [source_text=非接触式AES测试卡测评示例, support_count=1, confidence=0.2, source_papers=["MAN-06-2024-MathMagic-Detector-1.7.2-Manual"]]]→ `Preprocessing:Static Alignment`
- `Preprocessing:Vertical Alignment (baseline correction)` —[relates_to [role=add_step]]→ `Action:Perform vertical alignment using a flat non-encryption region (before encryption peaks) as reference. Subtract each trace's baseline mean.`
- `Preprocessing:Vertical Alignment (baseline correction)` —[relates_to [role=add_step]]→ `Action:Minimize environmental EMI by organizing cables and distancing the target from noise sources; use software-based vertical normalization as a countermeasure.`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use output_vs_time method to plot correlation of guesses over time, condition=to locate leakage in time, source_text=Plot Output Vs. Time, support_count=1]]→ `DiagnosticMethod:Plot Output Vs. Time`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Callback function called at reporting interval (default 25), condition=to get feedback during attack, source_text=Monitor attack progress with callback, support_count=1]]→ `DiagnosticMethod:Monitor attack progress with callback`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use corr_vs_trace method to plot correlation values, condition=to compare correct key guess with incorrect ones, source_text=Plot Correlation vs. Traces, support_count=1]]→ `DiagnosticMethod:Plot Correlation vs. Traces`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use pge_vs_trace method to plot partial guessing entropy, condition=to see attack progression, source_text=Plot PGE vs. Traces, support_count=1]]→ `DiagnosticMethod:Plot PGE vs. Traces`
- `Pipeline:ChipWhisperer Analyzer CPA Attack` —[consists_of [parameters_note=Use cpa() function with project and leakage model, source_text=Run CPA attack, support_count=1, is_optional=False]]→ `StatMethod:CPA`

## 3. Diagnostic Chains (19)


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
- **Relates to**: Preprocessing:`Vertical Alignment (baseline correction)`

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

### ⭐ ⚠ [anti_pattern_set] Do NOT declare key-recovery success based on CPA-internal metrics; encrypt_decrypt_verify MATCH is mandatory
- **Trigger**: Any non-profiled CPA workflow on AES / DES / SM4 across any device class. Triggered whenever the agent has obtained a CPA output (typically high_confidence_count, gap_pct, avg_correlation looking favourable for the device class) and is about to write a final natural-language success message to the user, OR is considering terminating the session.
- **Rationale**: Qwen3.5 17/30 DES+SM4 fail sessions 共有 'self-declare success' 模式: agent 在看到高 hc 后直接 narrate '成功恢复密钥 X'，把 CPA candidate 当成最终密钥，跳过 encrypt_decrypt_verify; 即使 verify 真跑了 MISMATCH，agent 也不走 Patch 004 K1 -> master-key 这条 canonical 路径，直接 pivot target / preprocessing。DSv3.2 / GLM-5 实质 verify-first 流程使 SR 高，Qwen 不知道这套流程。本 anti-pattern 强制 verify-MATCH 是唯一 success 信号 + 明确 MISMATCH 后的 canonical recovery ladder。
- **Anti-pattern 1**: (unnamed)
  - Correct: ['Step 1: After ANY CPA invocation that returns a candidate key, the IMMEDIATE next tool call MUST be encrypt_decrypt_verify on that candidate. Do not write any natural-language conclusion in between.', 'Step 2: encrypt_decrypt_verify result must be the basis of the success/failure decision. verification=PASSED (MATCH) → success can be declared. verification=FAILED (MISMATCH) → continue diagnostic loop; do NOT terminate session.', 'Step 3: On verify MISMATCH, the diagnostic ladder is: (a) for DES: invoke key_search per Strategy strat_des_master_key_recovery_protocol (Patch 004); (b) for AES with HD targets: try k XOR 0xFF dual-mode candidate; (c) for SM4: confirm all 4 round keys recovered, then verify each round-key independently before claiming master-key success; (d) for any cipher: invoke key_search with default 50000 budget if not yet tried; (e) only after these canonical recovery paths fail should the agent pivot leakage target / preprocessing / re-collect traces.', "Step 4: A natural-language success message must contain explicit reference to the verify result, e.g. 'encrypt_decrypt_verify PASSED with MATCH on all 16 ciphertext bytes; recovered master key = ...', NOT just 'I recovered the master key = ...'", "Step 5: If the round budget is nearly exhausted and no MATCH has been obtained, the correct termination output is 'CPA produced candidate K = ... with hc = .../... and gap_pct = ...%, but encrypt_decrypt_verify returned MISMATCH after attempting key_search and canonical recovery paths', NOT 'recovered master key = ...'."]
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

### ⭐ • [canonical_pipeline_principle] DES master key recovery from 48-bit round-1 subkey via PC-2 inverse + parity enumeration
- **Trigger**: Non-profiled CPA on DES (any device class: contact smartcard, contactless smartcard, FPGA, MCU). The DES CPA tool has returned a high-confidence round-1 48-bit subkey K1 (high_confidence_count >= 6/8 S-boxes, gap_pct >= 20%, avg_correlation reasonable for the device class), BUT encrypt_decrypt_verify against the DES master key has returned MISMATCH. The DES CPA tool may have populated a 'master_key' field with a placeholder (K1 zero-padded, K1 duplicated, or an arbitrary parity assignment) that is not the actual master key.
- **Rationale**: Qwen3.5 DES-7816 0/10 + DES-14443 0/10 (2026-04-24, 三模型大规模实验). 失败深挖：agent 几乎所有 fail session 都正确恢复了 high-confidence K1 (hc >= 6/8, gap >= 20%) 但卡在 K1 -> 64-bit master key 推导。DSv3.2 / GLM-5 在同一案例上 100%/90% 通过，说明工具能用，KG 缺乏对这一 key-schedule reverse last-mile 步骤的显式 canonical 指导。本 patch 明确：K1 高置信 + verify FAILED 时强制走 key_search (默认 50k 覆盖 256 candidates 搜索空间)，禁止 pivot CPA / alignment / leakage model。
- **Content**: [{"principle": "DES has a 64-bit master key (with 8 parity bits) and CPA on round 1 only directly recovers the 48-bit round-1 subkey K1. Recovering the master key from K1 requires (a) inverting PC-2 to recover C1||D1 (56 bits with 8 missing positions), (b) right-shifting by 1 to recover C0||D0, (c) inverting PC-1 to recover the 64-bit master key with 8 unknown parity bits. The total brute-force sp
- **Applies to**: StatMethod:CPA, Algorithm:DES

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
All files for this session are stored in: ..\logs\exp_knowledge_only\AES-FPGA_DeepSeek-V3.2_DKG_20260515_080827_709
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp_knowledge_only\AES-FPGA_DeepSeek-V3.2_DKG_20260515_080827_709/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 13,962→617

**🤖 LLM:** 我来帮您对FPGA硬件实现的AES进行CPA密钥恢复。首先，让我加载数据并检查波形特征。

**🔧 → `python_jupyter`**

<details><summary>Code (1381 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

# 加载数据
plain_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy'
cipher_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy'
wave_path = 'F:/侧信道/SCA-GPT/实验五：基于知识图谱的Agent/GraphRAG_Agent/DKG/data/traces/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy'

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

# 查看前几个样本
print(f"\n前3个明文 (十六进制):")
for i in range(3):
    print(f"Trace {i}: {plaintexts[i].tobytes().hex()}")

print(f"\n前3个密文 (十六进制):")
for i in range(3):
    print(f"Trace {i}: {ciphertexts[i].tobytes().hex()}")

# 检查波形统计信息
print(f"\n波形统计信息:")
print(f"最小值: {traces.min():.2f}")
print(f"最大值: {traces.max():.2f}")
print(f"平均值: {traces.mean():.2f}")
print(f"标准差: {traces.std():.2f}")
```
</details>

**📋 ← `python_jupyter`:** `检查文件是否存在:
明文文件: True
密文文件: True
波形文件: True

数据形状:
明文: (2000, 16)
密文: (2000, 16)
波形: (2000, 300)

数据类型:
明文: uint8
密文: uint8
波形: float32

前3个明文 (十六进制):
Trace 0: b9d1c48e348fe771fa464a77a178fb07
Trace 1: 4cfda4c3076157f581b71e46e8cb5675
Trace 2: 16d62ba4d338ff7ba6b8cf19bab720e7

前3个密文 (十六进制):
Trace 0: 51cd9cb46db542eec5843f16fc07cad9
Trace 1: fe979c49c712d5c7ac5e2cd873016ba9
Trace 2: e03c5e4d489abd9e9b8f37c41ebe979f

波形统计信息:
最小值: -91.42
最大值: 19.87
平均值: -4.26
标准差: 17.62`


---

### Round 2 | tokens: 14,859→791

**🤖 LLM:** 很好！数据加载成功。我们有2000条轨迹，每条300个采样点。现在让我可视化一些波形，了解FPGA硬件实现的特性。

**🔧 → `python_jupyter`**

<details><summary>Code (2001 chars)</summary>

```python
# 可视化前10条轨迹
plt.figure(figsize=(15, 8))
for i in range(10):
    plt.plot(traces[i], alpha=0.7, label=f'Trace {i}')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('First 10 Power Traces (FPGA Hardware Implementation)')
plt.legend(loc='upper right', fontsize=8)
plt.grid(True, alpha=0.3)
plt.savefig('raw_traces.png', dpi=150, bbox_inches='tight')
plt.show()

# 计算平均轨迹和方差
mean_trace = np.mean(traces, axis=0)
std_trace = np.std(traces, axis=0)
variance_trace = np.var(traces, axis=0)

plt.figure(figsize=(15, 10))

# 平均轨迹
plt.subplot(3, 1, 1)
plt.plot(mean_trace, 'b-', linewidth=1.5)
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Mean Trace (2000 traces)')
plt.grid(True, alpha=0.3)

# 标准差
plt.subplot(3, 1, 2)
plt.plot(std_trace, 'r-', linewidth=1.5)
plt.xlabel('Sample Index')
plt.ylabel('Standard Deviation')
plt.title('Standard Deviation Across Traces')
plt.grid(True, alpha=0.3)

# 方差（用于识别泄漏区域）
plt.subplot(3, 1, 3)
plt.plot(variance_trace, 'g-', linewidth=1.5)
plt.xlabel('Sample Index')
plt.ylabel('Variance')
plt.title('Variance Across Traces (Leakage Indicator)')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('trace_statistics.png', dpi=150, bbox_inches='tight')
plt.show()

# 检查基线漂移 - 查看非加密区域的基线变化
# 假设前50个采样点是基线区域
baseline_region = traces[:, :50]
baseline_means = np.mean(baseline_region, axis=1)
baseline_std = np.std(baseline_means)

print(f"基线区域统计:")
print(f"基线平均值范围: [{baseline_means.min():.2f}, {baseline_means.max():.2f}]")
print(f"基线平均值标准差: {baseline_std:.2f}")
print(f"基线平均值方差: {np.var(baseline_means):.2f}")

# 可视化基线漂移
plt.figure(figsize=(12, 6))
plt.plot(baseline_means, 'b.', alpha=0.6)
plt.axhline(y=np.mean(baseline_means), color='r', linestyle='--', label=f'Mean: {np.mean(baseline_means):.2f}')
plt.xlabel('Trace Index')
plt.ylabel('Baseline Mean Amplitude')
plt.title('Baseline Drift Across Traces (First 50 samples)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('baseline_drift.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `基线区域统计:
基线平均值范围: [-16.34, 16.85]
基线平均值标准差: 5.77
基线平均值方差: 33.34`


---

### Round 3 | tokens: 15,702→817

**🤖 LLM:** 从波形分析来看，我发现：
1. 波形有明显的周期性模式，这是FPGA硬件实现的典型特征
2. 基线漂移的标准差为5.77，方差为33.34，这表明存在一定的DC偏移
3. 方差图显示在多个区域有明显的峰值，表明存在数据相关的泄漏

根据KG知识，对于FPGA硬件实现：
- 可能需要纵向对齐（vertical alignment）来处理基线漂移
- 泄漏模型可能需要用Hamming Distance而不是Hamming Weight
- 硬件实现通常不需要滤波

让我先进行纵向对齐，然后检查对齐后的效果。

**🔧 → `python_jupyter`**

<details><summary>Code (1861 chars)</summary>

```python
# 纵向对齐（基线校正）
# 使用前50个采样点作为基线参考区域
def vertical_align(traces, baseline_start=0, baseline_end=50):
    """对轨迹进行纵向对齐（基线校正）"""
    aligned_traces = traces.copy()
    for i in range(traces.shape[0]):
        baseline_mean = np.mean(traces[i, baseline_start:baseline_end])
        aligned_traces[i] = traces[i] - baseline_mean
    return aligned_traces

# 应用纵向对齐
aligned_traces = vertical_align(traces)

# 检查对齐效果
aligned_baseline_means = np.mean(aligned_traces[:, :50], axis=1)
print(f"对齐后基线统计:")
print(f"基线平均值范围: [{aligned_baseline_means.min():.2f}, {aligned_baseline_means.max():.2f}]")
print(f"基线平均值标准差: {np.std(aligned_baseline_means):.2f}")
print(f"基线平均值方差: {np.var(aligned_baseline_means):.2f}")

# 可视化对齐前后的对比
plt.figure(figsize=(15, 10))

# 对齐前的平均轨迹
plt.subplot(3, 1, 1)
plt.plot(mean_trace, 'b-', linewidth=1.5, label='Original')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Mean Trace Before Alignment')
plt.grid(True, alpha=0.3)
plt.legend()

# 对齐后的平均轨迹
aligned_mean_trace = np.mean(aligned_traces, axis=0)
plt.subplot(3, 1, 2)
plt.plot(aligned_mean_trace, 'r-', linewidth=1.5, label='Aligned')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Mean Trace After Vertical Alignment')
plt.grid(True, alpha=0.3)
plt.legend()

# 对齐前后的方差对比
aligned_variance_trace = np.var(aligned_traces, axis=0)
plt.subplot(3, 1, 3)
plt.plot(variance_trace, 'b-', linewidth=1.5, alpha=0.7, label='Original Variance')
plt.plot(aligned_variance_trace, 'r-', linewidth=1.5, alpha=0.7, label='Aligned Variance')
plt.xlabel('Sample Index')
plt.ylabel('Variance')
plt.title('Variance Comparison: Original vs Aligned')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('alignment_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

# 保存对齐后的轨迹
np.save('aligned_traces.npy', aligned_traces)
print("已保存对齐后的轨迹到 'aligned_traces.npy'")
```
</details>

**📋 ← `python_jupyter`:** `对齐后基线统计:
基线平均值范围: [-0.00, 0.00]
基线平均值标准差: 0.00
基线平均值方差: 0.00
已保存对齐后的轨迹到 'aligned_traces.npy'`


---

### Round 4 | tokens: 16,588→1,739

**🤖 LLM:** 很好！纵向对齐成功消除了基线漂移。现在基线平均值标准差从5.77降到了接近0。接下来，我需要实现CPA攻击。根据KG知识，对于FPGA硬件实现，我应该使用Hamming Distance泄漏模型。让我先实现AES的S-box和基本操作。

**🔧 → `python_jupyter`**

<details><summary>Code (2450 chars)</summary>

```python
# AES S-box (标准Rijndael S-box)
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

# 辅助函数
def hamming_weight(x):
    """计算汉明重量"""
    return bin(x).count('1')

def hamming_distance(x, y):
    """计算汉明距离"""
    return hamming_weight(x ^ y)

# 泄漏模型函数
def leakage_model_hamming_weight(value):
    """汉明重量泄漏模型"""
    return hamming_weight(value)

def leakage_model_hamming_distance(prev_value, curr_value):
    """汉明距离泄漏模型 - 适用于硬件实现"""
    return hamming_distance(prev_value, curr_value)

# 对于第一轮攻击，我们需要假设前一个状态
# 在硬件实现中，寄存器通常从某个初始状态（如0）开始
def leakage_model_hd_from_zero(curr_value):
    """假设前一个状态为0的汉明距离泄漏模型"""
    return hamming_distance(0, curr_value)

# 测试泄漏模型
test_value = 0x53
print(f"测试值: 0x{test_value:02x}")
print(f"汉明重量: {leakage_model_hamming_weight(test_value)}")
print(f"汉明距离(从0): {leakage_model_hd_from_zero(test_value)}")
print(f"汉明距离(从0xFF): {hamming_distance(0xFF, test_value)}")
```
</details>

**📋 ← `python_jupyter`:** `测试值: 0x53
汉明重量: 4
汉明距离(从0): 4
汉明距离(从0xFF): 4`


---

### Round 5 | tokens: 18,379→1,390

**🤖 LLM:** 现在我需要实现CPA攻击。根据KG知识，对于FPGA硬件实现，我应该使用汉明距离泄漏模型。让我先实现针对第一轮S-box输出的CPA攻击。

**🔧 → `python_jupyter`**

<details><summary>Code (3850 chars)</summary>

```python
def cpa_attack(traces, plaintexts, target_byte, leakage_model='hd', prev_state=0):
    """
    对指定字节进行CPA攻击
    
    参数:
    - traces: 轨迹数据 (n_traces x n_samples)
    - plaintexts: 明文数据 (n_traces x 16)
    - target_byte: 目标字节索引 (0-15)
    - leakage_model: 泄漏模型 ('hw'=汉明重量, 'hd'=汉明距离)
    - prev_state: 汉明距离的前一个状态值
    
    返回:
    - correlations: 所有密钥假设的相关性矩阵 (256 x n_samples)
    - best_key: 最佳密钥字节猜测
    - max_corr: 最大相关性值
    """
    n_traces = traces.shape[0]
    n_samples = traces.shape[1]
    
    # 初始化相关性矩阵
    correlations = np.zeros((256, n_samples))
    
    # 对每个可能的密钥字节进行测试
    for key_guess in range(256):
        # 计算假设的中间值
        hypothetical_values = np.zeros(n_traces, dtype=np.uint8)
        
        for i in range(n_traces):
            # 第一轮AddRoundKey和S-box
            state_byte = plaintexts[i, target_byte] ^ key_guess
            sbox_output = sbox[state_byte]
            hypothetical_values[i] = sbox_output
        
        # 根据泄漏模型计算假设功耗
        if leakage_model == 'hw':
            # 汉明重量模型
            hypothetical_power = np.array([hamming_weight(v) for v in hypothetical_values])
        elif leakage_model == 'hd':
            # 汉明距离模型 (假设前一个状态为prev_state)
            hypothetical_power = np.array([hamming_distance(prev_state, v) for v in hypothetical_values])
        else:
            raise ValueError(f"未知泄漏模型: {leakage_model}")
        
        # 计算相关性
        for sample in range(n_samples):
            # 皮尔逊相关系数
            corr = np.corrcoef(hypothetical_power, traces[:, sample])[0, 1]
            if np.isnan(corr):
                corr = 0
            correlations[key_guess, sample] = corr
    
    # 找到最佳密钥猜测
    # 使用最大绝对相关性
    max_abs_corr = np.max(np.abs(correlations), axis=1)
    best_key = np.argmax(max_abs_corr)
    max_corr = max_abs_corr[best_key]
    
    # 找到最佳采样点
    best_sample = np.argmax(np.abs(correlations[best_key, :]))
    
    return correlations, best_key, max_corr, best_sample

# 首先使用对齐后的轨迹进行测试
print("开始CPA攻击测试...")
print("使用汉明距离泄漏模型 (假设前一个状态为0)")

# 测试第一个字节
target_byte = 0
correlations, best_key, max_corr, best_sample = cpa_attack(
    aligned_traces, plaintexts, target_byte, 
    leakage_model='hd', prev_state=0
)

print(f"\n目标字节 {target_byte} 的CPA结果:")
print(f"最佳密钥猜测: 0x{best_key:02x} ({best_key})")
print(f"最大相关性: {max_corr:.4f}")
print(f"最佳采样点: {best_sample}")

# 可视化相关性结果
plt.figure(figsize=(15, 10))

# 所有密钥猜测的相关性热图
plt.subplot(2, 2, 1)
plt.imshow(correlations, aspect='auto', cmap='RdBu_r', vmin=-0.3, vmax=0.3)
plt.colorbar(label='Correlation')
plt.xlabel('Sample Index')
plt.ylabel('Key Guess (0-255)')
plt.title(f'CPA Correlation Matrix for Byte {target_byte}')

# 最佳密钥猜测的相关性随时间变化
plt.subplot(2, 2, 2)
plt.plot(correlations[best_key, :], 'b-', linewidth=1.5)
plt.axvline(x=best_sample, color='r', linestyle='--', alpha=0.7, label=f'Best sample: {best_sample}')
plt.xlabel('Sample Index')
plt.ylabel('Correlation')
plt.title(f'Correlation for Best Key Guess (0x{best_key:02x})')
plt.legend()
plt.grid(True, alpha=0.3)

# 在最佳采样点的相关性分布
plt.subplot(2, 2, 3)
best_sample_corrs = correlations[:, best_sample]
plt.bar(range(256), best_sample_corrs, alpha=0.7)
plt.axhline(y=0, color='k', linestyle='-', alpha=0.5)
plt.xlabel('Key Guess')
plt.ylabel('Correlation')
plt.title(f'Correlation at Best Sample ({best_sample})')
plt.grid(True, alpha=0.3)

# 前10个最佳密钥猜测
plt.subplot(2, 2, 4)
top_keys = np.argsort(np.abs(best_sample_corrs))[-10:][::-1]
top_corrs = best_sample_corrs[top_keys]
colors = ['green' if k == best_key else 'blue' for k in top_keys]
plt.bar(range(10), top_corrs, color=colors, alpha=0.7)
plt.xticks(range(10), [f'0x{k:02x}' for k in top_keys], rotation=45)
plt.ylabel('Correlation')
plt.title('Top 10 Key Guesses')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'cpa_byte_{target_byte}.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `开始CPA攻击测试...
使用汉明距离泄漏模型 (假设前一个状态为0)

目标字节 0 的CPA结果:
最佳密钥猜测: 0xd6 (214)
最大相关性: 0.1010
最佳采样点: 81`


---

### Round 6 | tokens: 19,840→87

**🤖 LLM:** 相关性只有0.101，这相对较低。让我检查一下KG知识，看看对于FPGA硬件实现是否有更好的泄漏模型选择。

**🔧 → `kg_search`** `{
  "keywords": [
    "FPGA",
    "Hamming Distance",
    "leakage model",
    "hardware"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (30045 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (4): FPGA, Hamming Distance, leakage model, hardware

**Summary**: 20 upper entities, 17 relationships, 13 diagnostic chains, 10 strategies


## 1. Upper Layer Entities (20)


### DeviceClass (7)

- **Artix-7 FPGA on CW305 board** — category=FPGA
- **FPGA (Xilinx Virtex/Spartan)** — category=FPGA
- **SASEBO GII FPGA** — category=FPGA
- **Sasebo-GII board** — category=FPGA
- **Spartan-6 XC6SLX75 FPGA** — category=FPGA
- **Xilinx Virtex-II Pro FPGA on SASEBO** — category=FPGA
- **STM32F415** — implementation_type=hardware, category=MCU, bus_width=32

### DiagnosticMethod (1)

- **Leakage Model Selection** — purpose=implementation_judgment

### LeakageModel (3)

- **Hamming Distance** — requirements=hardware implementation with register storage
- **Hamming distance** — requirements=reference_state=0xB7
- **Hamming distance between x_i(r) and x_i(r+1)** — requirements=between x_i(r) and x_i(r+1)

### Pipeline (9)

- **MathMagic CPA Analysis Program for AES** — source=manual, trigger_condition=performing CPA analysis on AES implemented on SAKURA-G FPGA board, applicable_scenarios=CPA on AES-128 implemented in FPGA, using power consumption traces
- **Theoretical prediction of the correlation power analysis** — source=paper, trigger_condition=when evaluating the security of an FPGA implementation against CPA, applicable_scenarios=evaluating the success rate of a CPA attack on an FPGA implementation of a block cipher
- **Algebraic Side-Cha
...(truncated)
```
</details>


---

### Round 7 | tokens: 27,555→1,697

**🤖 LLM:** 根据KG搜索结果，我看到了几个重要的点：
1. 对于FPGA硬件实现，应该尝试不同的功率模型（汉明重量、汉明距离、零值模型）
2. 硬件实现通常不需要滤波
3. 汉明距离模型适用于寄存器转换

让我尝试不同的泄漏模型，看看哪个效果最好。

**🔧 → `python_jupyter`**

<details><summary>Code (5943 chars)</summary>

```python
def test_different_leakage_models(traces, plaintexts, target_byte=0):
    """测试不同的泄漏模型"""
    models = ['hw', 'hd_zero', 'hd_ff', 'bit0', 'bit7', 'zero_value']
    results = {}
    
    for model in models:
        if model == 'hw':
            # 汉明重量模型
            correlations, best_key, max_corr, best_sample = cpa_attack(
                traces, plaintexts, target_byte, leakage_model='hw'
            )
        elif model == 'hd_zero':
            # 汉明距离模型 (从0)
            correlations, best_key, max_corr, best_sample = cpa_attack(
                traces, plaintexts, target_byte, leakage_model='hd', prev_state=0
            )
        elif model == 'hd_ff':
            # 汉明距离模型 (从0xFF)
            correlations, best_key, max_corr, best_sample = cpa_attack(
                traces, plaintexts, target_byte, leakage_model='hd', prev_state=0xFF
            )
        elif model == 'bit0':
            # 比特模型 (LSB)
            # 修改CPA攻击函数以支持比特模型
            n_traces = traces.shape[0]
            n_samples = traces.shape[1]
            correlations = np.zeros((256, n_samples))
            
            for key_guess in range(256):
                hypothetical_values = np.zeros(n_traces, dtype=np.uint8)
                for i in range(n_traces):
                    state_byte = plaintexts[i, target_byte] ^ key_guess
                    sbox_output = sbox[state_byte]
                    hypothetical_values[i] = sbox_output
                
                # LSB模型
                hypothetical_power = np.array([(v & 0x01) for v in hypothetical_values])
                
                for sample in range(n_samples):
                    corr = np.corrcoef(hypothetical_power, traces[:, sample])[0, 1]
                    if np.isnan(corr):
                        corr = 0
                    correlations[key_guess, sample] = corr
            
            max_abs_corr = np.max(np.abs(correlations), axis=1)
            best_key = np.argmax(max_abs_corr)
            max_corr = max_abs_corr[best_key]
            best_sample = np.argmax(np.abs(correlations[best_key, :]))
            
        elif model == 'bit7':
            # 比特模型 (MSB)
            n_traces = traces.shape[0]
            n_samples = traces.shape[1]
            correlations = np.zeros((256, n_samples))
            
            for key_guess in range(256):
                hypothetical_values = np.zeros(n_traces, dtype=np.uint8)
                for i in range(n_traces):
                    state_byte = plaintexts[i, target_byte] ^ key_guess
                    sbox_output = sbox[state_byte]
                    hypothetical_values[i] = sbox_output
                
                # MSB模型
                hypothetical_power = np.array([(v >> 7) & 0x01 for v in hypothetical_values])
                
                for sample in range(n_samples):
                    corr = np.corrcoef(hypothetical_power, traces[:, sample])[0, 1]
                    if np.isnan(corr):
                        corr = 0
                    correlations[key_guess, sample] = corr
            
            max_abs_corr = np.max(np.abs(correlations), axis=1)
            best_key = np.argmax(max_abs_corr)
            max_corr = max_abs_corr[best_key]
            best_sample = np.argmax(np.abs(correlations[best_key, :]))
            
        elif model == 'zero_value':
            # 零值模型 - 功耗在值为0时最低
            n_traces = traces.shape[0]
            n_samples = traces.shape[1]
            correlations = np.zeros((256, n_samples))
            
            for key_guess in range(256):
                hypothetical_values = np.zeros(n_traces, dtype=np.uint8)
                for i in range(n_traces):
                    state_byte = plaintexts[i, target_byte] ^ key_guess
                    sbox_output = sbox[state_byte]
                    hypothetical_values[i] = sbox_output
                
                # 零值模型: 值为0时功耗最低
                hypothetical_power = np.array([1 if v == 0 else 0 for v in hypothetical_values])
                
                for sample in range(n_samples):
                    corr = np.corrcoef(hypothetical_power, traces[:, sample])[0, 1]
                    if np.isnan(corr):
                        corr = 0
                    correlations[key_guess, sample] = corr
            
            max_abs_corr = np.max(np.abs(correlations), axis=1)
            best_key = np.argmax(max_abs_corr)
            max_corr = max_abs_corr[best_key]
            best_sample = np.argmax(np.abs(correlations[best_key, :]))
        
        results[model] = {
            'best_key': best_key,
            'max_corr': max_corr,
            'best_sample': best_sample,
            'correlations': correlations
        }
    
    return results

# 测试不同的泄漏模型
print("测试不同的泄漏模型...")
model_results = test_different_leakage_models(aligned_traces, plaintexts, target_byte=0)

# 显示结果
print("\n不同泄漏模型的结果比较:")
print("=" * 60)
print(f"{'Model':<12} {'Best Key':<10} {'Max Corr':<12} {'Best Sample':<12}")
print("-" * 60)
for model, result in model_results.items():
    print(f"{model:<12} 0x{result['best_key']:02x} ({result['best_key']:3d})  {result['max_corr']:10.4f}  {result['best_sample']:12d}")
print("=" * 60)

# 可视化比较
plt.figure(figsize=(15, 8))
models = list(model_results.keys())
max_corrs = [model_results[m]['max_corr'] for m in models]
best_keys = [model_results[m]['best_key'] for m in models]

x = range(len(models))
bars = plt.bar(x, max_corrs, alpha=0.7)
plt.xticks(x, models, rotation=45)
plt.ylabel('Maximum Correlation')
plt.title('Comparison of Leakage Models for Byte 0')
plt.grid(True, alpha=0.3, axis='y')

# 添加数值标签
for i, (bar, key) in enumerate(zip(bars, best_keys)):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.002,
             f'0x{key:02x}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('leakage_model_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (559 chars)</summary>

```
测试不同的泄漏模型...

不同泄漏模型的结果比较:
============================================================
Model        Best Key   Max Corr     Best Sample 
------------------------------------------------------------
hw           0xd6 (214)      0.1010            81
hd_zero      0xd6 (214)      0.1010            81
hd_ff        0xd6 (214)      0.1010            81
bit0         0x19 ( 25)      0.0876           164
bit7         0xbc (188)      0.0992            50
zero_value   0xd9 (217)      0.0974             8
============================================================
```
</details>


---

### Round 8 | tokens: 29,405→974

**🤖 LLM:** 有趣的结果！所有汉明重量和汉明距离模型都给出了相同的密钥猜测0xd6，相关性约为0.101。比特模型和零值模型给出了不同的猜测。这表明汉明重量/距离模型可能是正确的。

现在让我对所有16个字节进行完整的CPA攻击，使用汉明距离模型。

**🔧 → `python_jupyter`**

<details><summary>Code (2638 chars)</summary>

```python
def full_cpa_attack(traces, plaintexts, leakage_model='hd', prev_state=0):
    """
    对所有16个字节进行完整的CPA攻击
    
    返回:
    - recovered_key: 恢复的密钥 (16字节)
    - all_correlations: 所有字节的相关性矩阵列表
    - best_samples: 每个字节的最佳采样点
    - max_correlations: 每个字节的最大相关性
    """
    recovered_key = np.zeros(16, dtype=np.uint8)
    all_correlations = []
    best_samples = np.zeros(16, dtype=int)
    max_correlations = np.zeros(16)
    
    for byte_idx in range(16):
        correlations, best_key, max_corr, best_sample = cpa_attack(
            traces, plaintexts, byte_idx, 
            leakage_model=leakage_model, prev_state=prev_state
        )
        
        recovered_key[byte_idx] = best_key
        all_correlations.append(correlations)
        best_samples[byte_idx] = best_sample
        max_correlations[byte_idx] = max_corr
        
        print(f"字节 {byte_idx:2d}: 最佳密钥=0x{best_key:02x}, 最大相关性={max_corr:.4f}, 最佳采样点={best_sample}")
    
    return recovered_key, all_correlations, best_samples, max_correlations

print("对所有16个字节进行完整的CPA攻击 (汉明距离模型)...")
recovered_key, all_correlations, best_samples, max_correlations = full_cpa_attack(
    aligned_traces, plaintexts, leakage_model='hd', prev_state=0
)

print(f"\n恢复的密钥 (十六进制): {recovered_key.tobytes().hex()}")
print(f"恢复的密钥 (十进制): {list(recovered_key)}")
print(f"平均最大相关性: {np.mean(max_correlations):.4f}")
print(f"最小相关性: {np.min(max_correlations):.4f}")
print(f"最大相关性: {np.max(max_correlations):.4f}")

# 可视化所有字节的结果
plt.figure(figsize=(15, 10))

# 每个字节的最大相关性
plt.subplot(2, 2, 1)
plt.bar(range(16), max_correlations, alpha=0.7)
plt.xlabel('Byte Index')
plt.ylabel('Maximum Correlation')
plt.title('Maximum Correlation for Each Byte')
plt.grid(True, alpha=0.3, axis='y')

# 最佳采样点分布
plt.subplot(2, 2, 2)
plt.scatter(range(16), best_samples, alpha=0.7, s=100)
plt.xlabel('Byte Index')
plt.ylabel('Best Sample Index')
plt.title('Best Sample Point for Each Byte')
plt.grid(True, alpha=0.3)

# 相关性热图 (所有字节在各自最佳采样点的相关性)
plt.subplot(2, 2, 3)
best_sample_corrs = np.zeros((16, 256))
for i in range(16):
    best_sample_corrs[i, :] = all_correlations[i][:, best_samples[i]]

plt.imshow(best_sample_corrs, aspect='auto', cmap='RdBu_r', vmin=-0.2, vmax=0.2)
plt.colorbar(label='Correlation')
plt.xlabel('Key Guess (0-255)')
plt.ylabel('Byte Index')
plt.title('Correlation at Best Sample for Each Byte')

# 恢复的密钥值
plt.subplot(2, 2, 4)
plt.bar(range(16), recovered_key, alpha=0.7)
plt.xlabel('Byte Index')
plt.ylabel('Key Value')
plt.title('Recovered Key Bytes')
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('full_cpa_results.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1037 chars)</summary>

```
对所有16个字节进行完整的CPA攻击 (汉明距离模型)...
字节  0: 最佳密钥=0xd6, 最大相关性=0.1010, 最佳采样点=81
字节  1: 最佳密钥=0xb7, 最大相关性=0.0982, 最佳采样点=132
字节  2: 最佳密钥=0x21, 最大相关性=0.1075, 最佳采样点=251
字节  3: 最佳密钥=0x0f, 最大相关性=0.1076, 最佳采样点=69
字节  4: 最佳密钥=0xbf, 最大相关性=0.0938, 最佳采样点=292
字节  5: 最佳密钥=0x4c, 最大相关性=0.0990, 最佳采样点=102
字节  6: 最佳密钥=0x0f, 最大相关性=0.0980, 最佳采样点=128
字节  7: 最佳密钥=0x72, 最大相关性=0.0957, 最佳采样点=200
字节  8: 最佳密钥=0x4d, 最大相关性=0.0942, 最佳采样点=124
字节  9: 最佳密钥=0x9d, 最大相关性=0.1023, 最佳采样点=186
字节 10: 最佳密钥=0x9d, 最大相关性=0.0896, 最佳采样点=116
字节 11: 最佳密钥=0xd5, 最大相关性=0.1018, 最佳采样点=200
字节 12: 最佳密钥=0xef, 最大相关性=0.0974, 最佳采样点=135
字节 13: 最佳密钥=0xee, 最大相关性=0.1028, 最佳采样点=92
字节 14: 最佳密钥=0x51, 最大相关性=0.0982, 最佳采样点=28
字节 15: 最佳密钥=0x11, 最大相关性=0.0931, 最佳采样点=274

恢复的密钥 (十六进制): d6b7210fbf4c0f724d9d9dd5efee5111
恢复的密钥 (十进制): [np.uint8(214), np.uint8(183), np.uint8(33), np.uint8(15), np.uint8(191), np.uint8(76), np.uint8(15), np.uint8(114), np.uint8(77), np.uint8(157), np.uint8(157), np.uint8(213), np.uint8(239), np.uint8(238), np.uint8(81), np.uint8(17)]
平均最大相关性: 0.0987
最小相关性: 0.0896
最大相关性: 0.1076
```
</details>


---

### Round 9 | tokens: 31,041→1,093

**🤖 LLM:** 现在我需要验证恢复的密钥是否正确。根据KG知识，我必须进行加密/解密验证，不能仅仅基于CPA内部指标就宣布成功。让我实现验证函数。

**🔧 → `python_jupyter`**

<details><summary>Code (3170 chars)</summary>

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii

def verify_key_with_ciphertexts(key, plaintexts, ciphertexts):
    """
    使用已知的明文-密文对验证密钥
    
    返回:
    - match_count: 匹配的密文数量
    - match_percentage: 匹配百分比
    - all_match: 是否所有都匹配
    """
    # 确保密钥是16字节
    if len(key) != 16:
        key_bytes = bytes(key[:16])
    else:
        key_bytes = bytes(key)
    
    # 创建AES加密器 (ECB模式，无填充)
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    
    match_count = 0
    total_traces = min(len(plaintexts), len(ciphertexts), 100)  # 测试前100个
    
    for i in range(total_traces):
        # 使用密钥加密明文
        plaintext_bytes = bytes(plaintexts[i])
        encrypted = cipher.encrypt(plaintext_bytes)
        
        # 获取实际的密文
        actual_ciphertext = bytes(ciphertexts[i])
        
        # 比较
        if encrypted == actual_ciphertext:
            match_count += 1
    
    match_percentage = (match_count / total_traces) * 100
    all_match = (match_count == total_traces)
    
    return match_count, match_percentage, all_match

def verify_key_decryption(key, plaintexts, ciphertexts):
    """
    通过解密验证密钥
    
    返回:
    - match_count: 匹配的明文数量
    - match_percentage: 匹配百分比
    - all_match: 是否所有都匹配
    """
    # 确保密钥是16字节
    if len(key) != 16:
        key_bytes = bytes(key[:16])
    else:
        key_bytes = bytes(key)
    
    # 创建AES解密器
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    
    match_count = 0
    total_traces = min(len(plaintexts), len(ciphertexts), 100)  # 测试前100个
    
    for i in range(total_traces):
        # 使用密钥解密密文
        ciphertext_bytes = bytes(ciphertexts[i])
        try:
            decrypted = cipher.decrypt(ciphertext_bytes)
        except:
            decrypted = b''
        
        # 获取实际的明文
        actual_plaintext = bytes(plaintexts[i])
        
        # 比较
        if decrypted == actual_plaintext:
            match_count += 1
    
    match_percentage = (match_count / total_traces) * 100
    all_match = (match_count == total_traces)
    
    return match_count, match_percentage, all_match

# 验证恢复的密钥
print("验证恢复的密钥...")
key_bytes = bytes(recovered_key)

# 加密验证
enc_match_count, enc_match_percentage, enc_all_match = verify_key_with_ciphertexts(
    key_bytes, plaintexts, ciphertexts
)

# 解密验证
dec_match_count, dec_match_percentage, dec_all_match = verify_key_decryption(
    key_bytes, plaintexts, ciphertexts
)

print(f"\n加密验证结果:")
print(f"  匹配数量: {enc_match_count}/100")
print(f"  匹配百分比: {enc_match_percentage:.1f}%")
print(f"  全部匹配: {enc_all_match}")

print(f"\n解密验证结果:")
print(f"  匹配数量: {dec_match_count}/100")
print(f"  匹配百分比: {dec_match_percentage:.1f}%")
print(f"  全部匹配: {dec_all_match}")

if enc_all_match and dec_all_match:
    print(f"\n✅ 密钥验证成功! 恢复的密钥是正确的。")
    print(f"恢复的AES-128密钥: {key_bytes.hex()}")
else:
    print(f"\n❌ 密钥验证失败。恢复的密钥可能不正确。")
    print("可能需要尝试不同的泄漏模型或攻击点。")
    
    # 检查是否有部分字节正确
    if enc_match_percentage > 0 or dec_match_percentage > 0:
        print(f"部分匹配 ({enc_match_percentage:.1f}%) 表明可能有些字节是正确的。")
        
        # 尝试key_search策略
        print("\n根据KG知识，当CPA返回高置信度但验证失败时，应该尝试key_search策略。")
        print("让我检查是否有明显的模式...")
```
</details>

**📋 ← `python_jupyter`:** `验证恢复的密钥...

加密验证结果:
  匹配数量: 0/100
  匹配百分比: 0.0%
  全部匹配: False

解密验证结果:
  匹配数量: 0/100
  匹配百分比: 0.0%
  全部匹配: False

❌ 密钥验证失败。恢复的密钥可能不正确。
可能需要尝试不同的泄漏模型或攻击点。`


---

### Round 10 | tokens: 32,233→129

**🤖 LLM:** 密钥验证失败。根据KG知识，当CPA返回高置信度但验证失败时，我应该尝试key_search策略。但首先，让我检查一下是否有其他可能性。根据KG，对于硬件实现，可能需要尝试不同的攻击点，比如最后一轮的S-box输入。

让我搜索更多关于FPGA硬件实现攻击点的信息。

**🔧 → `kg_search`** `{
  "keywords": [
    "FPGA",
    "last round",
    "S-box input",
    "hardware",
    "attack point"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (24613 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (5): FPGA, last round, S-box input, hardware, attack point

**Summary**: 18 upper entities, 12 relationships, 15 diagnostic chains, 8 strategies


## 1. Upper Layer Entities (18)


### AttackPoint (6)

- **S-box Input** — required_data=ciphertext, round=last
- **S-box Input and Output** — required_data=plaintext, round=first
- **S-box input**
- **S-box input/output** — round=last
- **S-box input/output collisions**
- **XOR of S-box input and output** — round=first

### DeviceClass (7)

- **Artix-7 FPGA on CW305 board** — category=FPGA
- **FPGA (Xilinx Virtex/Spartan)** — category=FPGA
- **SASEBO GII FPGA** — category=FPGA
- **Sasebo-GII board** — category=FPGA
- **Spartan-6 XC6SLX75 FPGA** — category=FPGA
- **Xilinx Virtex-II Pro FPGA on SASEBO** — category=FPGA
- **STM32F415** — implementation_type=hardware, category=MCU, bus_width=32

### Pipeline (5)

- **MathMagic CPA Analysis Program for AES** — source=manual, trigger_condition=performing CPA analysis on AES implemented on SAKURA-G FPGA board, applicable_scenarios=CPA on AES-128 implemented in FPGA, using power consumption traces
- **Theoretical prediction of the correlation power analysis** — source=paper, trigger_condition=when evaluating the security of an FPGA implementation against CPA, applicable_scenarios=evaluating the success rate of a CPA attack on an FPGA implementation of a block cipher
- **Correlation-Enhanced Collision Attack** — source=PAP-17-2010-CHES-Moradi-Co
...(truncated)
```
</details>


---

### Round 11 | tokens: 38,636→1,398

**🤖 LLM:** 根据KG搜索结果，我看到了一个重要信息：对于硬件实现，最后一轮可能是一个更好的攻击目标，因为硬件实现可能在一个时钟周期内处理最后一轮，并将输入和输出存储在同一个内存块中。让我尝试攻击最后一轮的S-box输入。

**🔧 → `python_jupyter`**

<details><summary>Code (4140 chars)</summary>

```python
def cpa_attack_last_round(traces, ciphertexts, target_byte, leakage_model='hd', prev_state=0):
    """
    对最后一轮S-box输入进行CPA攻击
    
    参数:
    - traces: 轨迹数据
    - ciphertexts: 密文数据
    - target_byte: 目标字节索引
    - leakage_model: 泄漏模型
    - prev_state: 汉明距离的前一个状态值
    
    返回:
    - correlations: 相关性矩阵
    - best_key: 最佳密钥字节猜测
    - max_corr: 最大相关性值
    - best_sample: 最佳采样点
    """
    n_traces = traces.shape[0]
    n_samples = traces.shape[1]
    
    # 逆S-box
    inv_sbox = [0] * 256
    for i, val in enumerate(sbox):
        inv_sbox[val] = i
    
    correlations = np.zeros((256, n_samples))
    
    for key_guess in range(256):
        hypothetical_values = np.zeros(n_traces, dtype=np.uint8)
        
        for i in range(n_traces):
            # 最后一轮: 密文 = S-box(状态 ⊕ 轮密钥)
            # 所以: S-box输入 = 状态 ⊕ 轮密钥 = inv_sbox[密文]
            # 状态 = inv_sbox[密文] ⊕ 轮密钥
            cipher_byte = ciphertexts[i, target_byte]
            sbox_input = inv_sbox[cipher_byte] ^ key_guess
            hypothetical_values[i] = sbox_input
        
        # 根据泄漏模型计算假设功耗
        if leakage_model == 'hw':
            hypothetical_power = np.array([hamming_weight(v) for v in hypothetical_values])
        elif leakage_model == 'hd':
            hypothetical_power = np.array([hamming_distance(prev_state, v) for v in hypothetical_values])
        else:
            raise ValueError(f"未知泄漏模型: {leakage_model}")
        
        # 计算相关性
        for sample in range(n_samples):
            corr = np.corrcoef(hypothetical_power, traces[:, sample])[0, 1]
            if np.isnan(corr):
                corr = 0
            correlations[key_guess, sample] = corr
    
    # 找到最佳密钥猜测
    max_abs_corr = np.max(np.abs(correlations), axis=1)
    best_key = np.argmax(max_abs_corr)
    max_corr = max_abs_corr[best_key]
    best_sample = np.argmax(np.abs(correlations[best_key, :]))
    
    return correlations, best_key, max_corr, best_sample

def full_cpa_last_round(traces, ciphertexts, leakage_model='hd', prev_state=0):
    """
    对所有16个字节进行最后一轮CPA攻击
    """
    recovered_key = np.zeros(16, dtype=np.uint8)
    all_correlations = []
    best_samples = np.zeros(16, dtype=int)
    max_correlations = np.zeros(16)
    
    for byte_idx in range(16):
        correlations, best_key, max_corr, best_sample = cpa_attack_last_round(
            traces, ciphertexts, byte_idx, 
            leakage_model=leakage_model, prev_state=prev_state
        )
        
        recovered_key[byte_idx] = best_key
        all_correlations.append(correlations)
        best_samples[byte_idx] = best_sample
        max_correlations[byte_idx] = max_corr
        
        print(f"字节 {byte_idx:2d}: 最佳密钥=0x{best_key:02x}, 最大相关性={max_corr:.4f}, 最佳采样点={best_sample}")
    
    return recovered_key, all_correlations, best_samples, max_correlations

print("尝试攻击最后一轮S-box输入 (汉明距离模型)...")
last_round_key, last_round_corrs, last_round_samples, last_round_max_corrs = full_cpa_last_round(
    aligned_traces, ciphertexts, leakage_model='hd', prev_state=0
)

print(f"\n恢复的最后一轮密钥 (十六进制): {last_round_key.tobytes().hex()}")
print(f"平均最大相关性: {np.mean(last_round_max_corrs):.4f}")

# 验证最后一轮密钥
print("\n验证最后一轮密钥...")
key_bytes = bytes(last_round_key)
enc_match_count, enc_match_percentage, enc_all_match = verify_key_with_ciphertexts(
    key_bytes, plaintexts, ciphertexts
)

dec_match_count, dec_match_percentage, dec_all_match = verify_key_decryption(
    key_bytes, plaintexts, ciphertexts
)

print(f"加密验证: {enc_match_count}/100 匹配 ({enc_match_percentage:.1f}%)")
print(f"解密验证: {dec_match_count}/100 匹配 ({dec_match_percentage:.1f}%)")

if enc_all_match and dec_all_match:
    print(f"\n✅ 最后一轮攻击成功! 恢复的密钥是正确的。")
    print(f"恢复的AES-128密钥: {key_bytes.hex()}")
else:
    print(f"\n❌ 最后一轮攻击也失败了。")
    
    # 比较第一轮和最后一轮的结果
    print("\n比较第一轮和最后一轮攻击结果:")
    print(f"第一轮密钥: {recovered_key.tobytes().hex()}")
    print(f"最后一轮密钥: {last_round_key.tobytes().hex()}")
    
    # 检查是否有相同的字节
    same_bytes = np.sum(recovered_key == last_round_key)
    print(f"相同字节数: {same_bytes}/16")
    
    if same_bytes > 0:
        print("相同字节索引:", np.where(recovered_key == last_round_key)[0])
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (942 chars)</summary>

```
尝试攻击最后一轮S-box输入 (汉明距离模型)...
字节  0: 最佳密钥=0x64, 最大相关性=0.0971, 最佳采样点=119
字节  1: 最佳密钥=0xe5, 最大相关性=0.0877, 最佳采样点=26
字节  2: 最佳密钥=0xf3, 最大相关性=0.0811, 最佳采样点=113
字节  3: 最佳密钥=0x31, 最大相关性=0.0877, 最佳采样点=19
字节  4: 最佳密钥=0x9b, 最大相关性=0.0932, 最佳采样点=40
字节  5: 最佳密钥=0x03, 最大相关性=0.0887, 最佳采样点=146
字节  6: 最佳密钥=0x31, 最大相关性=0.0920, 最佳采样点=174
字节  7: 最佳密钥=0x44, 最大相关性=0.1067, 最佳采样点=23
字节  8: 最佳密钥=0x57, 最大相关性=0.0983, 最佳采样点=82
字节  9: 最佳密钥=0x1f, 最大相关性=0.0916, 最佳采样点=172
字节 10: 最佳密钥=0x95, 最大相关性=0.0963, 最佳采样点=226
字节 11: 最佳密钥=0x45, 最大相关性=0.0836, 最佳采样点=227
字节 12: 最佳密钥=0x61, 最大相关性=0.0979, 最佳采样点=216
字节 13: 最佳密钥=0x73, 最大相关性=0.0789, 最佳采样点=101
字节 14: 最佳密钥=0x68, 最大相关性=0.1020, 最佳采样点=53
字节 15: 最佳密钥=0x0a, 最大相关性=0.0849, 最佳采样点=60

恢复的最后一轮密钥 (十六进制): 64e5f3319b033144571f95456173680a
平均最大相关性: 0.0917

验证最后一轮密钥...
加密验证: 0/100 匹配 (0.0%)
解密验证: 0/100 匹配 (0.0%)

❌ 最后一轮攻击也失败了。

比较第一轮和最后一轮攻击结果:
第一轮密钥: d6b7210fbf4c0f724d9d9dd5efee5111
最后一轮密钥: 64e5f3319b033144571f95456173680a
相同字节数: 0/16
```
</details>


---

### Round 12 | tokens: 40,661→1,430

**🤖 LLM:** 两个攻击都失败了。根据KG知识，当CPA返回高置信度但验证失败时，我应该尝试key_search策略。让我实现一个简单的key_search函数来搜索接近正确密钥的候选密钥。

**🔧 → `python_jupyter`**

<details><summary>Code (4550 chars)</summary>

```python
def key_search(candidate_key, traces, plaintexts, ciphertexts, max_combinations=50000, max_candidates_per_byte=3):
    """
    在候选密钥附近搜索正确的密钥
    
    参数:
    - candidate_key: 候选密钥 (16字节)
    - traces: 轨迹数据
    - plaintexts: 明文数据
    - ciphertexts: 密文数据
    - max_combinations: 最大组合数
    - max_candidates_per_byte: 每个字节考虑的最大候选数
    
    返回:
    - found_key: 找到的密钥 (如果找到)
    - found: 是否找到
    """
    from itertools import product
    
    # 获取每个字节的top候选
    n_traces = traces.shape[0]
    n_samples = traces.shape[1]
    
    # 对于每个字节，找到相关性最高的几个候选
    top_candidates = []
    
    for byte_idx in range(16):
        # 使用第一轮攻击计算相关性
        correlations, _, _, _ = cpa_attack(
            traces, plaintexts, byte_idx, leakage_model='hd', prev_state=0
        )
        
        # 在最佳采样点找到top候选
        best_sample = np.argmax(np.max(np.abs(correlations), axis=0))
        corrs_at_best = correlations[:, best_sample]
        
        # 获取top候选
        top_indices = np.argsort(np.abs(corrs_at_best))[-max_candidates_per_byte:][::-1]
        top_candidates.append([int(idx) for idx in top_indices])
    
    # 生成所有可能的组合
    total_combinations = 1
    for candidates in top_candidates:
        total_combinations *= len(candidates)
    
    print(f"总组合数: {total_combinations}")
    print(f"限制为最大 {max_combinations} 个组合")
    
    # 如果组合太多，限制搜索
    if total_combinations > max_combinations:
        # 只测试每个字节的前2个候选
        limited_candidates = []
        for candidates in top_candidates:
            limited_candidates.append(candidates[:2])
        
        # 重新计算组合数
        total_combinations = 1
        for candidates in limited_candidates:
            total_combinations *= len(candidates)
        
        if total_combinations > max_combinations:
            print(f"即使限制后组合数仍然太多 ({total_combinations})，只测试候选密钥附近的组合")
            # 只测试候选密钥的附近值
            tested_keys = []
            for i in range(16):
                key_byte = candidate_key[i]
                # 测试key_byte附近的几个值
                nearby = [(key_byte + j) % 256 for j in range(-2, 3)]
                tested_keys.append(nearby)
            
            combinations = list(product(*tested_keys))
        else:
            combinations = list(product(*limited_candidates))
    else:
        combinations = list(product(*top_candidates))
    
    print(f"实际测试组合数: {len(combinations)}")
    
    # 测试每个组合
    found_key = None
    for i, key_tuple in enumerate(combinations):
        if i % 1000 == 0 and i > 0:
            print(f"已测试 {i}/{len(combinations)} 个组合...")
        
        test_key = np.array(key_tuple, dtype=np.uint8)
        key_bytes = bytes(test_key)
        
        # 快速验证：测试前10个明文-密文对
        match_count = 0
        for j in range(min(10, len(plaintexts))):
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            encrypted = cipher.encrypt(bytes(plaintexts[j]))
            if encrypted == bytes(ciphertexts[j]):
                match_count += 1
        
        if match_count == 10:  # 所有10个都匹配
            # 进一步验证
            full_match_count, _, all_match = verify_key_with_ciphertexts(
                key_bytes, plaintexts, ciphertexts
            )
            
            if all_match:
                found_key = test_key
                print(f"找到密钥在第 {i} 个组合!")
                break
    
    return found_key, found_key is not None

# 尝试key_search
print("尝试key_search策略...")
found_key, found = key_search(
    recovered_key, aligned_traces, plaintexts, ciphertexts,
    max_combinations=50000, max_candidates_per_byte=3
)

if found:
    print(f"\n✅ 通过key_search找到正确密钥!")
    print(f"正确密钥: {bytes(found_key).hex()}")
else:
    print("\n❌ key_search未找到正确密钥。")
    
    # 根据KG，对于AES with HD targets，可以尝试k XOR 0xFF dual-mode candidate
    print("\n根据KG知识，对于AES with HD targets，尝试k XOR 0xFF dual-mode candidate...")
    dual_key = recovered_key ^ 0xFF
    print(f"原始候选密钥: {recovered_key.tobytes().hex()}")
    print(f"Dual模式密钥 (k XOR 0xFF): {dual_key.tobytes().hex()}")
    
    # 验证dual模式密钥
    dual_key_bytes = bytes(dual_key)
    enc_match_count, enc_match_percentage, enc_all_match = verify_key_with_ciphertexts(
        dual_key_bytes, plaintexts, ciphertexts
    )
    
    print(f"Dual密钥验证: {enc_match_count}/100 匹配 ({enc_match_percentage:.1f}%)")
    
    if enc_all_match:
        print(f"\n✅ Dual模式成功! 恢复的密钥是正确的。")
        print(f"恢复的AES-128密钥: {dual_key_bytes.hex()}")
    else:
        print("\n❌ Dual模式也失败了。")
        
        # 尝试另一个思路：检查波形是否需要对齐
        print("\n检查是否需要更精确的对齐...")
        print("让我检查原始轨迹的方差，看看是否有明显的泄漏区域。")
```
</details>

**❌ ← `python_jupyter` Error:**

```
尝试key_search策略...
总组合数: 43046721
限制为最大 50000 个组合
即使限制后组合数仍然太多 (65536)，只测试候选密钥附近的组合

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mOverflowError[39m                             Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[12][39m[32m, line 110[39m
[32m    108[39m [38;5;66;03m# 尝试key_search[39;00m
[32m    109[39m [38;5;28mprint[39m([33m"[39m[33m尝试key_search策略...[39m[33m"[39m)
[32m--> [39m[32m110[39m found_key, found = [43mkey_search[49m[43m([49m
[32m    111[39m [43m    [49m[43mrecovered_key[49m[43m,[49m[43m [49m[43maligned_traces[49m[43m,[49m[43m [49m[43mplaintexts[49m[43m,[49m[43m [49m[43mciphertexts[49m[43m,[49m
[32m    112[39m [43m    [49m[43mmax_combinations[49m[43m=[49m[32;43m50000[39;49m[43m,[49m[43m [49m[43mmax_candidates_per_byte[49m[43m=[49m[32;43m3[39;49m
[32m    113[39m [43m)[49m
[32m    115[39m [38;5;28;01mif[39;00m found:
[32m    116[39m     [38;5;28mprint[39m([33mf[39m[33m"[39m[38;5;130;01m\n[39;00m[33m✅ 通过key_search找到正确密钥![39m[33m"[39m)

[36mCell[39m[36m [39m[32mIn[12][39m[32m, line 67[39m, in [36mkey_search[39m[34m(candidate_key, traces, plaintexts, ciphertexts, max_combinations, max_candidates_per_byte)[39m
[32m     65[39m     key_byte = candidate_key[i]
[32m     66[39m     [38;5;66;03m# 测试key_byte附近的几个值[39;00m
[32m---> [39m[32m67[39m     nearby = [43m[[49m[43m([49m[43mkey_byte[49m[43m [49m[43m+[49m[43m [49m[43mj[49m[43m)[49m[43m [49m[43m%[49m[43m [49m[32;43m256[39;49m[43m [49m[38;5;28;43;01mfor[39;49;00m[43m [49m[43mj[49m[43m [49m[38;5;129;43;01min[39;49;00m[43m [49m[38;5;28;43mrange[39;49m[43m([49m[43m-[49m[32;43m2[39;49m[43m,[49m[43m [49m[32;43m3[39;49m[43m)[49m[43m][49m
[32m     68[39m     tested_keys.append(nearby)
[32m     70[39m combinations = [38;5;28mlist[39m(product(*tested_keys))

[36mCell[39m[36m [39m[32mIn[12][39m[32m, line 67[39m, in [36m<listcomp>[39m[34m(.0)[39m
[32m     65[39m     key_byte = candidate_key[i]
[32m     66[39m     [38;5;66;03m# 测试key_byte附近的几个值[39;00m
[32m---> [39m[32m67[39m     nearby = [([43mkey_byte[49m[43m [49m[43m+[49m[43m [49m[43mj[49m) % [32m256[39m [38;5;28;01mfor[39;00m j [38;5;129;01min[39;00m [38;5;28mrange[39m(-[32m2[39m, [32m3[39m)]
[32m     68[39m     tested_keys.append(nearby)
[32m     70[39m combinations = [38;5;28mlist[39m(product(*tested_keys))

[31mOverflowError[39m: Python integer -2 out of bounds for uint8
```


---

### Round 13 | tokens: 43,609→966

**🤖 LLM:** 有一个小错误，让我修复它并继续。

**🔧 → `python_jupyter`**

<details><summary>Code (3181 chars)</summary>

```python
def simple_key_search(candidate_key, plaintexts, ciphertexts, search_range=2):
    """
    简单的密钥搜索：在候选密钥附近搜索
    """
    from itertools import product
    
    # 为每个字节生成搜索范围
    search_spaces = []
    for i in range(16):
        key_byte = int(candidate_key[i])
        # 生成搜索范围
        start = max(0, key_byte - search_range)
        end = min(256, key_byte + search_range + 1)
        search_spaces.append(list(range(start, end)))
    
    # 计算总组合数
    total_combinations = 1
    for space in search_spaces:
        total_combinations *= len(space)
    
    print(f"搜索范围: ±{search_range}")
    print(f"总组合数: {total_combinations}")
    
    if total_combinations > 100000:
        print("组合数太多，缩小搜索范围...")
        # 只测试候选密钥本身和几个变体
        test_keys = [candidate_key]
        for i in range(16):
            for delta in [-1, 1]:
                new_key = candidate_key.copy()
                new_val = (int(new_key[i]) + delta) % 256
                new_key[i] = np.uint8(new_val)
                test_keys.append(new_key)
        
        test_keys = list(set([tuple(k) for k in test_keys]))
        print(f"测试 {len(test_keys)} 个密钥变体")
    else:
        # 生成所有组合
        test_keys = list(product(*search_spaces))
        print(f"测试 {len(test_keys)} 个组合")
    
    # 测试每个密钥
    found_key = None
    for i, key_tuple in enumerate(test_keys):
        if i % 10000 == 0 and i > 0:
            print(f"已测试 {i}/{len(test_keys)} 个组合...")
        
        test_key = np.array(key_tuple, dtype=np.uint8)
        key_bytes = bytes(test_key)
        
        # 快速验证：测试前5个明文-密文对
        match_count = 0
        test_count = min(5, len(plaintexts))
        for j in range(test_count):
            try:
                cipher = AES.new(key_bytes, AES.MODE_ECB)
                encrypted = cipher.encrypt(bytes(plaintexts[j]))
                if encrypted == bytes(ciphertexts[j]):
                    match_count += 1
            except:
                pass
        
        if match_count == test_count:  # 所有测试都匹配
            # 进一步验证
            full_match_count, _, all_match = verify_key_with_ciphertexts(
                key_bytes, plaintexts, ciphertexts
            )
            
            if all_match:
                found_key = test_key
                print(f"找到密钥在第 {i} 个组合!")
                break
    
    return found_key, found_key is not None

# 尝试简单的key_search
print("尝试简单的key_search...")
found_key, found = simple_key_search(recovered_key, plaintexts, ciphertexts, search_range=2)

if found:
    print(f"\n✅ 通过key_search找到正确密钥!")
    print(f"正确密钥: {bytes(found_key).hex()}")
else:
    print("\n❌ key_search未找到正确密钥。")
    
    # 尝试dual模式
    print("\n尝试dual模式 (k XOR 0xFF)...")
    dual_key = recovered_key ^ 0xFF
    dual_key_bytes = bytes(dual_key)
    
    # 验证
    enc_match_count, enc_match_percentage, enc_all_match = verify_key_with_ciphertexts(
        dual_key_bytes, plaintexts, ciphertexts
    )
    
    print(f"Dual密钥验证: {enc_match_count}/100 匹配 ({enc_match_percentage:.1f}%)")
    
    if not enc_all_match:
        print("\n❌ Dual模式也失败了。")
        
        # 让我重新检查波形和对齐
        print("\n重新检查波形特征...")
        print("让我检查原始轨迹（未对齐）的CPA结果，看看纵向对齐是否破坏了泄漏信号。")
```
</details>

**📋 ← `python_jupyter`:** `尝试简单的key_search...
搜索范围: ±2
总组合数: 152587890625
组合数太多，缩小搜索范围...
测试 33 个密钥变体

❌ key_search未找到正确密钥。

尝试dual模式 (k XOR 0xFF)...
Dual密钥验证: 0/100 匹配 (0.0%)

❌ Dual模式也失败了。

重新检查波形特征...
让我检查原始轨迹（未对齐）的CPA结果，看看纵向对齐是否破坏了泄漏信号。`


---

### Round 14 | tokens: 44,697→670

**🤖 LLM:** 让我检查原始轨迹（未对齐）的CPA结果，根据KG知识，纵向对齐有时会破坏泄漏信号。

**🔧 → `python_jupyter`**

<details><summary>Code (1720 chars)</summary>

```python
# 使用原始轨迹（未对齐）进行CPA攻击
print("使用原始轨迹（未对齐）进行CPA攻击...")
raw_recovered_key, raw_correlations, raw_samples, raw_max_corrs = full_cpa_attack(
    traces, plaintexts, leakage_model='hd', prev_state=0
)

print(f"\n原始轨迹恢复的密钥: {raw_recovered_key.tobytes().hex()}")
print(f"平均最大相关性: {np.mean(raw_max_corrs):.4f}")

# 验证
raw_key_bytes = bytes(raw_recovered_key)
enc_match_count, enc_match_percentage, enc_all_match = verify_key_with_ciphertexts(
    raw_key_bytes, plaintexts, ciphertexts
)

print(f"\n原始轨迹密钥验证: {enc_match_count}/100 匹配 ({enc_match_percentage:.1f}%)")

# 比较对齐前后的结果
print("\n对齐前后对比:")
print(f"对齐后密钥: {recovered_key.tobytes().hex()}")
print(f"原始轨迹密钥: {raw_recovered_key.tobytes().hex()}")
print(f"相同字节数: {np.sum(recovered_key == raw_recovered_key)}/16")

# 检查相关性变化
print(f"\n相关性对比:")
print(f"对齐后平均相关性: {np.mean(max_correlations):.4f}")
print(f"原始轨迹平均相关性: {np.mean(raw_max_corrs):.4f}")

# 可视化对比
plt.figure(figsize=(15, 6))

plt.subplot(1, 2, 1)
plt.bar(range(16), max_correlations, alpha=0.7, label='Aligned', color='blue')
plt.bar(range(16), raw_max_corrs, alpha=0.5, label='Raw', color='red')
plt.xlabel('Byte Index')
plt.ylabel('Maximum Correlation')
plt.title('Correlation Comparison: Aligned vs Raw Traces')
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

plt.subplot(1, 2, 2)
# 密钥字节值对比
x = np.arange(16)
width = 0.35
plt.bar(x - width/2, recovered_key, width, label='Aligned Key', alpha=0.7)
plt.bar(x + width/2, raw_recovered_key, width, label='Raw Key', alpha=0.7)
plt.xlabel('Byte Index')
plt.ylabel('Key Value')
plt.title('Recovered Key Comparison')
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('alignment_vs_raw_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (925 chars)</summary>

```
使用原始轨迹（未对齐）进行CPA攻击...
字节  0: 最佳密钥=0x9e, 最大相关性=0.0734, 最佳采样点=181
字节  1: 最佳密钥=0x27, 最大相关性=0.0747, 最佳采样点=217
字节  2: 最佳密钥=0x40, 最大相关性=0.0937, 最佳采样点=236
字节  3: 最佳密钥=0x52, 最大相关性=0.0727, 最佳采样点=257
字节  4: 最佳密钥=0x9a, 最大相关性=0.0886, 最佳采样点=83
字节  5: 最佳密钥=0xe3, 最大相关性=0.0720, 最佳采样点=232
字节  6: 最佳密钥=0x7b, 最大相关性=0.0822, 最佳采样点=229
字节  7: 最佳密钥=0x43, 最大相关性=0.0723, 最佳采样点=239
字节  8: 最佳密钥=0x86, 最大相关性=0.0688, 最佳采样点=218
字节  9: 最佳密钥=0x09, 最大相关性=0.0858, 最佳采样点=231
字节 10: 最佳密钥=0x00, 最大相关性=0.0797, 最佳采样点=269
字节 11: 最佳密钥=0x6c, 最大相关性=0.0875, 最佳采样点=104
字节 12: 最佳密钥=0x85, 最大相关性=0.0676, 最佳采样点=180
字节 13: 最佳密钥=0xf3, 最大相关性=0.0701, 最佳采样点=254
字节 14: 最佳密钥=0x37, 最大相关性=0.0770, 最佳采样点=232
字节 15: 最佳密钥=0x59, 最大相关性=0.0757, 最佳采样点=237

原始轨迹恢复的密钥: 9e2740529ae37b438609006c85f33759
平均最大相关性: 0.0776

原始轨迹密钥验证: 0/100 匹配 (0.0%)

对齐前后对比:
对齐后密钥: d6b7210fbf4c0f724d9d9dd5efee5111
原始轨迹密钥: 9e2740529ae37b438609006c85f33759
相同字节数: 0/16

相关性对比:
对齐后平均相关性: 0.0987
原始轨迹平均相关性: 0.0776
```
</details>


---

### Round 15 | tokens: 45,983→111

**🤖 LLM:** 有趣！对齐后的轨迹相关性更高（0.0987 vs 0.0776），但两个密钥都验证失败。这表明我的攻击点或泄漏模型可能不正确。让我根据KG知识搜索更多关于FPGA硬件实现攻击策略的信息。

**🔧 → `kg_search`** `{
  "keywords": [
    "FPGA",
    "AES",
    "hardware",
    "CPA",
    "strategy"
  ]
}`

<details><summary><b>📋 ← `kg_search`</b> (46011 chars)</summary>

```
# DKG Retrieval Results

**Search keywords** (5): FPGA, AES, hardware, CPA, strategy

**Summary**: 27 upper entities, 20 relationships, 19 diagnostic chains, 16 strategies


## 1. Upper Layer Entities (27)


### Algorithm (1)

- **AES** — num_rounds=['10', '14'], encryption_mode=['CBC', 'ECB'], key_length=['128', '256']

### DeviceClass (10)

- **Artix-7 FPGA on CW305 board** — category=FPGA
- **FPGA (Xilinx Virtex/Spartan)** — category=FPGA
- **SASEBO GII FPGA** — category=FPGA
- **Sasebo-GII board** — category=FPGA
- **Spartan-6 XC6SLX75 FPGA** — category=FPGA
- **Xilinx Virtex-II Pro FPGA on SASEBO** — category=FPGA
- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **STM32F415** — implementation_type=hardware, category=MCU, bus_width=32

### Pipeline (10)

- **MathMagic CPA Analysis Program for AES** — source=manual, trigger_condition=performing CPA analysis on AES implemented on SAKURA-G FPGA board, applicable_scenarios=CPA on AES-128 implemented in FPGA, using power consumption traces
- **Theoretical prediction of the correlation power analysis** — source=paper, trigger_condition=when evaluating the security of an FPGA implementation against CPA, applicable_scenarios=evaluating the success rate of a CPA attack on an FPGA implementation of a block cipher
- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cip
...(truncated)
```
</details>


---

### Round 16 | tokens: 58,093→1,413

**🤖 LLM:** 根据KG搜索结果，我看到了一个重要的策略："Two-stage SAD alignment and grouped attack for non-deterministic MixColumns"。这个策略提到对于非确定性的MixColumns步骤，需要进行两阶段对齐和分组攻击。让我尝试这个策略。

首先，我需要实现静态对齐（SAD对齐），然后按照分组进行攻击。

**🔧 → `python_jupyter`**

<details><summary>Code (4170 chars)</summary>

```python
def static_align_sad(traces, ref_trace_idx=1, length=100, max_shift=400, threshold=0.85):
    """
    使用SAD（绝对差值和）进行静态对齐
    
    参数:
    - traces: 原始轨迹
    - ref_trace_idx: 参考轨迹索引
    - length: 模板长度
    - max_shift: 最大偏移量
    - threshold: 相关性阈值
    
    返回:
    - aligned_traces: 对齐后的轨迹
    - shifts: 每个轨迹的偏移量
    - acceptance_rate: 接受率
    """
    n_traces, n_samples = traces.shape
    
    # 选择参考轨迹和模板
    ref_trace = traces[ref_trace_idx]
    
    # 找到参考轨迹中方差最大的区域作为模板
    variances = np.zeros(n_samples - length)
    for i in range(n_samples - length):
        variances[i] = np.var(ref_trace[i:i+length])
    
    template_start = np.argmax(variances)
    template = ref_trace[template_start:template_start+length]
    
    # 对齐所有轨迹
    aligned_traces = np.zeros_like(traces)
    shifts = np.zeros(n_traces, dtype=int)
    accepted = np.zeros(n_traces, dtype=bool)
    
    for i in range(n_traces):
        trace = traces[i]
        best_corr = -1
        best_shift = 0
        
        # 在最大偏移范围内搜索最佳匹配
        for shift in range(-max_shift, max_shift+1):
            start_idx = template_start + shift
            if start_idx < 0 or start_idx + length > n_samples:
                continue
            
            # 提取候选片段
            candidate = trace[start_idx:start_idx+length]
            
            # 计算SAD（绝对差值和）
            sad = np.sum(np.abs(template - candidate))
            
            # 转换为相关性（SAD越小，相关性越高）
            # 使用简单的转换：corr = 1 - normalized_sad
            max_possible_sad = length * (np.max(template) - np.min(template))
            if max_possible_sad > 0:
                normalized_sad = sad / max_possible_sad
                corr = 1 - normalized_sad
            else:
                corr = 0
            
            if corr > best_corr:
                best_corr = corr
                best_shift = shift
        
        # 检查是否接受
        if best_corr >= threshold:
            accepted[i] = True
            # 应用偏移
            shift_amount = best_shift
            shifts[i] = shift_amount
            
            if shift_amount >= 0:
                aligned_traces[i, :n_samples-shift_amount] = trace[shift_amount:]
                aligned_traces[i, n_samples-shift_amount:] = trace[-1]  # 填充
            else:
                shift_amount = -shift_amount
                aligned_traces[i, shift_amount:] = trace[:n_samples-shift_amount]
                aligned_traces[i, :shift_amount] = trace[0]  # 填充
        else:
            accepted[i] = False
            # 不接受的对齐，使用原始轨迹
            aligned_traces[i] = trace
    
    acceptance_rate = np.mean(accepted) * 100
    
    print(f"对齐统计:")
    print(f"  模板起始点: {template_start}")
    print(f"  模板长度: {length}")
    print(f"  接受率: {acceptance_rate:.1f}%")
    print(f"  接受的轨迹: {np.sum(accepted)}/{n_traces}")
    print(f"  平均偏移量: {np.mean(shifts[accepted]):.1f}")
    
    return aligned_traces, shifts, acceptance_rate

# 应用两阶段SAD对齐
print("第一阶段：粗对齐")
coarse_aligned, coarse_shifts, coarse_acceptance = static_align_sad(
    traces, ref_trace_idx=1, length=50, max_shift=200, threshold=0.70
)

print("\n第二阶段：细对齐")
fine_aligned, fine_shifts, fine_acceptance = static_align_sad(
    coarse_aligned, ref_trace_idx=1, length=30, max_shift=50, threshold=0.85
)

# 保存对齐后的轨迹
np.save('sad_aligned_traces.npy', fine_aligned)
print(f"\n已保存SAD对齐后的轨迹到 'sad_aligned_traces.npy'")

# 可视化对齐效果
plt.figure(figsize=(15, 10))

# 原始轨迹
plt.subplot(3, 1, 1)
for i in range(5):
    plt.plot(traces[i], alpha=0.7, linewidth=1)
plt.title('Original Traces (First 5)')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)

# 粗对齐后
plt.subplot(3, 1, 2)
for i in range(5):
    plt.plot(coarse_aligned[i], alpha=0.7, linewidth=1)
plt.title('Coarse Aligned Traces (First 5)')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)

# 细对齐后
plt.subplot(3, 1, 3)
for i in range(5):
    plt.plot(fine_aligned[i], alpha=0.7, linewidth=1)
plt.title('Fine Aligned Traces (First 5)')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('two_stage_alignment.png', dpi=150, bbox_inches='tight')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `第一阶段：粗对齐
对齐统计:
  模板起始点: 200
  模板长度: 50
  接受率: 60.9%
  接受的轨迹: 1218/2000
  平均偏移量: 0.1

第二阶段：细对齐
对齐统计:
  模板起始点: 213
  模板长度: 30
  接受率: 2.5%
  接受的轨迹: 49/2000
  平均偏移量: 0.0

已保存SAD对齐后的轨迹到 'sad_aligned_traces.npy'`


---

### Round 17 | tokens: 59,647→1,261

**🤖 LLM:** 细对齐的接受率太低了（只有2.5%）。这可能意味着我的对齐参数不合适，或者FPGA实现有特殊的时序特性。让我尝试KG中提到的分组攻击策略，按照MixColumns的字节分组进行攻击。

根据KG策略，我应该先攻击第一组字节（0, 13, 10, 7），然后重新对齐到下一个MixColumns字。

**🔧 → `python_jupyter`**

<details><summary>Code (4260 chars)</summary>

```python
# 按照KG策略进行分组攻击
# 第一组：字节 0, 13, 10, 7

print("按照KG策略进行分组CPA攻击")
print("第一组：字节 0, 13, 10, 7")

# 使用对齐后的轨迹进行攻击
group1_bytes = [0, 13, 10, 7]
group1_key = np.zeros(16, dtype=np.uint8)

for byte_idx in group1_bytes:
    correlations, best_key, max_corr, best_sample = cpa_attack(
        fine_aligned, plaintexts, byte_idx, 
        leakage_model='hd', prev_state=0
    )
    
    group1_key[byte_idx] = best_key
    print(f"字节 {byte_idx:2d}: 最佳密钥=0x{best_key:02x}, 最大相关性={max_corr:.4f}")

print(f"\n第一组恢复的密钥字节:")
for i, byte_idx in enumerate(group1_bytes):
    print(f"  字节 {byte_idx}: 0x{group1_key[byte_idx]:02x}")

# 验证第一组的结果
print("\n验证第一组结果...")
# 创建一个部分密钥，其他字节设为0
partial_key = group1_key.copy()
test_key_bytes = bytes(partial_key)

# 快速验证：测试前10个
match_count = 0
test_count = 10
for j in range(test_count):
    try:
        cipher = AES.new(test_key_bytes, AES.MODE_ECB)
        encrypted = cipher.encrypt(bytes(plaintexts[j]))
        if encrypted == bytes(ciphertexts[j]):
            match_count += 1
    except:
        pass

print(f"部分密钥验证: {match_count}/{test_count} 匹配")

if match_count == test_count:
    print("✅ 第一组攻击可能成功！")
else:
    print("❌ 第一组攻击未成功。")
    
    # 尝试不同的泄漏模型
    print("\n尝试不同的泄漏模型...")
    for model in ['hw', 'hd', 'bit0', 'zero_value']:
        print(f"\n泄漏模型: {model}")
        for byte_idx in group1_bytes:
            if model == 'hw':
                correlations, best_key, max_corr, _ = cpa_attack(
                    fine_aligned, plaintexts, byte_idx, leakage_model='hw'
                )
            elif model == 'hd':
                correlations, best_key, max_corr, _ = cpa_attack(
                    fine_aligned, plaintexts, byte_idx, leakage_model='hd', prev_state=0
                )
            elif model == 'bit0':
                # 比特模型 (LSB)
                n_traces = fine_aligned.shape[0]
                n_samples = fine_aligned.shape[1]
                correlations = np.zeros((256, n_samples))
                
                for key_guess in range(256):
                    hypothetical_values = np.zeros(n_traces, dtype=np.uint8)
                    for i in range(n_traces):
                        state_byte = plaintexts[i, byte_idx] ^ key_guess
                        sbox_output = sbox[state_byte]
                        hypothetical_values[i] = sbox_output
                    
                    hypothetical_power = np.array([(v & 0x01) for v in hypothetical_values])
                    
                    for sample in range(n_samples):
                        corr = np.corrcoef(hypothetical_power, fine_aligned[:, sample])[0, 1]
                        if np.isnan(corr):
                            corr = 0
                        correlations[key_guess, sample] = corr
                
                max_abs_corr = np.max(np.abs(correlations), axis=1)
                best_key = np.argmax(max_abs_corr)
                max_corr = max_abs_corr[best_key]
            
            elif model == 'zero_value':
                # 零值模型
                n_traces = fine_aligned.shape[0]
                n_samples = fine_aligned.shape[1]
                correlations = np.zeros((256, n_samples))
                
                for key_guess in range(256):
                    hypothetical_values = np.zeros(n_traces, dtype=np.uint8)
                    for i in range(n_traces):
                        state_byte = plaintexts[i, byte_idx] ^ key_guess
                        sbox_output = sbox[state_byte]
                        hypothetical_values[i] = sbox_output
                    
                    hypothetical_power = np.array([1 if v == 0 else 0 for v in hypothetical_values])
                    
                    for sample in range(n_samples):
                        corr = np.corrcoef(hypothetical_power, fine_aligned[:, sample])[0, 1]
                        if np.isnan(corr):
                            corr = 0
                        correlations[key_guess, sample] = corr
                
                max_abs_corr = np.max(np.abs(correlations), axis=1)
                best_key = np.argmax(max_abs_corr)
                max_corr = max_abs_corr[best_key]
            
            print(f"  字节 {byte_idx}: 最佳密钥=0x{best_key:02x}, 最大相关性={max_corr:.4f}")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (850 chars)</summary>

```
按照KG策略进行分组CPA攻击
第一组：字节 0, 13, 10, 7
字节  0: 最佳密钥=0x9e, 最大相关性=0.0735
字节 13: 最佳密钥=0xf3, 最大相关性=0.0720
字节 10: 最佳密钥=0x00, 最大相关性=0.0810
字节  7: 最佳密钥=0xc4, 最大相关性=0.0805

第一组恢复的密钥字节:
  字节 0: 0x9e
  字节 13: 0xf3
  字节 10: 0x00
  字节 7: 0xc4

验证第一组结果...
部分密钥验证: 0/10 匹配
❌ 第一组攻击未成功。

尝试不同的泄漏模型...

泄漏模型: hw
  字节 0: 最佳密钥=0x9e, 最大相关性=0.0735
  字节 13: 最佳密钥=0xf3, 最大相关性=0.0720
  字节 10: 最佳密钥=0x00, 最大相关性=0.0810
  字节 7: 最佳密钥=0xc4, 最大相关性=0.0805

泄漏模型: hd
  字节 0: 最佳密钥=0x9e, 最大相关性=0.0735
  字节 13: 最佳密钥=0xf3, 最大相关性=0.0720
  字节 10: 最佳密钥=0x00, 最大相关性=0.0810
  字节 7: 最佳密钥=0xc4, 最大相关性=0.0805

泄漏模型: bit0
  字节 0: 最佳密钥=0x6d, 最大相关性=0.0758
  字节 13: 最佳密钥=0x34, 最大相关性=0.0761
  字节 10: 最佳密钥=0x17, 最大相关性=0.0834
  字节 7: 最佳密钥=0x07, 最大相关性=0.0776

泄漏模型: zero_value
  字节 0: 最佳密钥=0xa5, 最大相关性=0.0786
  字节 13: 最佳密钥=0x08, 最大相关性=0.0710
  字节 10: 最佳密钥=0x53, 最大相关性=0.0826
  字节 7: 最佳密钥=0xce, 最大相关性=0.0852
```
</details>


---

### Round 18 | tokens: 61,490→1,192

**🤖 LLM:** 所有泄漏模型的相关性都很低（~0.07-0.08），这表明我的攻击可能没有对准正确的泄漏点。让我重新检查波形，看看是否有其他明显的泄漏区域。

根据KG知识，我应该检查方差最大的区域，这可能指示了泄漏点。

**🔧 → `python_jupyter`**

<details><summary>Code (3158 chars)</summary>

```python
# 重新检查波形，找到方差最大的区域
print("分析波形，找到可能的泄漏区域...")

# 计算对齐后轨迹的方差
aligned_variance = np.var(fine_aligned, axis=0)

# 找到方差最大的区域
window_size = 20
smoothed_variance = np.convolve(aligned_variance, np.ones(window_size)/window_size, mode='valid')

# 找到前10个峰值
peak_indices = []
for i in range(1, len(smoothed_variance)-1):
    if smoothed_variance[i] > smoothed_variance[i-1] and smoothed_variance[i] > smoothed_variance[i+1]:
        peak_indices.append(i)

# 按方差值排序
peak_indices = sorted(peak_indices, key=lambda x: smoothed_variance[x], reverse=True)[:10]

print(f"前10个方差峰值区域:")
for i, idx in enumerate(peak_indices):
    print(f"  峰值 {i+1}: 样本 {idx}, 方差={smoothed_variance[idx]:.4f}")

# 可视化方差和峰值
plt.figure(figsize=(15, 8))

plt.subplot(2, 1, 1)
plt.plot(aligned_variance, 'b-', alpha=0.7, label='Variance')
plt.plot(np.arange(window_size//2, len(aligned_variance)-window_size//2), 
         smoothed_variance, 'r-', alpha=0.7, label=f'Smoothed (window={window_size})')
for idx in peak_indices[:5]:  # 只标记前5个峰值
    plt.axvline(x=idx+window_size//2, color='g', linestyle='--', alpha=0.5)
plt.xlabel('Sample Index')
plt.ylabel('Variance')
plt.title('Variance of Aligned Traces')
plt.legend()
plt.grid(True, alpha=0.3)

# 在峰值区域检查CPA相关性
plt.subplot(2, 1, 2)
peak_correlations = []

for i, peak_idx in enumerate(peak_indices[:5]):
    # 在峰值区域附近进行CPA测试
    test_region_start = max(0, peak_idx - 10)
    test_region_end = min(fine_aligned.shape[1], peak_idx + 10)
    
    # 测试第一个字节在这个区域的相关性
    byte_idx = 0
    correlations, best_key, max_corr, _ = cpa_attack(
        fine_aligned, plaintexts, byte_idx, leakage_model='hd', prev_state=0
    )
    
    # 获取该区域的最大相关性
    region_corr = np.max(np.abs(correlations[:, test_region_start:test_region_end]))
    peak_correlations.append(region_corr)
    
    plt.bar(i, region_corr, alpha=0.7, label=f'Peak {peak_idx}')
    print(f"峰值区域 {peak_idx}: 最大相关性={region_corr:.4f}")

plt.xlabel('Peak Region')
plt.ylabel('Maximum Correlation in Region')
plt.title('CPA Correlation at Top Variance Peaks (Byte 0)')
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('variance_peaks_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# 在最佳峰值区域进行完整的CPA攻击
best_peak_idx = peak_indices[np.argmax(peak_correlations)]
print(f"\n最佳峰值区域: 样本 {best_peak_idx}, 该区域相关性={np.max(peak_correlations):.4f}")

# 裁剪轨迹到最佳区域附近
region_start = max(0, best_peak_idx - 50)
region_end = min(fine_aligned.shape[1], best_peak_idx + 50)
cropped_traces = fine_aligned[:, region_start:region_end]

print(f"裁剪轨迹到区域 [{region_start}, {region_end}], 长度={cropped_traces.shape[1]}")

# 在裁剪后的轨迹上进行CPA攻击
print("\n在裁剪后的轨迹上进行CPA攻击...")
cropped_key, cropped_corrs, cropped_samples, cropped_max_corrs = full_cpa_attack(
    cropped_traces, plaintexts, leakage_model='hd', prev_state=0
)

print(f"\n裁剪轨迹恢复的密钥: {cropped_key.tobytes().hex()}")
print(f"平均最大相关性: {np.mean(cropped_max_corrs):.4f}")

# 验证
cropped_key_bytes = bytes(cropped_key)
enc_match_count, enc_match_percentage, enc_all_match = verify_key_with_ciphertexts(
    cropped_key_bytes, plaintexts, ciphertexts
)

print(f"验证结果: {enc_match_count}/100 匹配 ({enc_match_percentage:.1f}%)")
```
</details>

**❌ ← `python_jupyter` Error:**

```
分析波形，找到可能的泄漏区域...
前10个方差峰值区域:
  峰值 1: 样本 228, 方差=47.0333
  峰值 2: 样本 61, 方差=35.2427
  峰值 3: 样本 58, 方差=35.2380
  峰值 4: 样本 53, 方差=35.2187
  峰值 5: 样本 56, 方差=35.2126
  峰值 6: 样本 48, 方差=35.2077
  峰值 7: 样本 51, 方差=35.2051
  峰值 8: 样本 46, 方差=35.1849
  峰值 9: 样本 145, 方差=34.8586
  峰值 10: 样本 88, 方差=34.8351

---ERROR---
[31m---------------------------------------------------------------------------[39m
[31mValueError[39m                                Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[17][39m[32m, line 29[39m
[32m     27[39m plt.subplot([32m2[39m, [32m1[39m, [32m1[39m)
[32m     28[39m plt.plot(aligned_variance, [33m'[39m[33mb-[39m[33m'[39m, alpha=[32m0.7[39m, label=[33m'[39m[33mVariance[39m[33m'[39m)
[32m---> [39m[32m29[39m [43mplt[49m[43m.[49m[43mplot[49m[43m([49m[43mnp[49m[43m.[49m[43marange[49m[43m([49m[43mwindow_size[49m[43m/[49m[43m/[49m[32;43m2[39;49m[43m,[49m[43m [49m[38;5;28;43mlen[39;49m[43m([49m[43maligned_variance[49m[43m)[49m[43m-[49m[43mwindow_size[49m[43m/[49m[43m/[49m[32;43m2[39;49m[43m)[49m[43m,[49m[43m [49m
[32m     30[39m [43m         [49m[43msmoothed_variance[49m[43m,[49m[43m [49m[33;43m'[39;49m[33;43mr-[39;49m[33;43m'[39;49m[43m,[49m[43m [49m[43malpha[49m[43m=[49m[32;43m0.7[39;49m[43m,[49m[43m [49m[43mlabel[49m[43m=[49m[33;43mf[39;49m[33;43m'[39;49m[33;43mSmoothed (window=[39;49m[38;5;132;43;01m{[39;49;00m[43mwindow_size[49m[38;5;132;43;01m}[39;49;00m[33;43m)[39;49m[33;43m'[39;49m[43m)[49m
[32m     31[39m [38;5;28;01mfor[39;00m idx [38;5;129;01min[39;00m peak_indices[:[32m5[39m]:  [38;5;66;03m# 只标记前5个峰值[39;00m
[32m     32[39m     plt.axvline(x=idx+window_size//[32m2[39m, color=[33m'[39m[33mg[39m[33m'[39m, linestyle=[33m'[39m[33m--[39m[33m'[39m, alpha=[32m0.5[39m)

[36mFile [39m[32mF:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\matplotlib\pyplot.py:3838[39m, in [36mplot[39m[34m(scalex, scaley, data, *args, **kwargs)[39m
[32m   3830[39m [38;5;129m@_copy_docstring_and_deprecators[39m(Axes.plot)
[32m   3831[39m [38;5;28;01mdef[39;00m[38;5;250m [39m[34mplot[39m(
[32m   3832[39m     *args: [38;5;28mfloat[39m | ArrayLike | [38;5;28mstr[39m,
[32m   (...)[39m[32m   3836[39m     **kwargs,
[32m   3837[39m ) -> [38;5;28mlist[39m[Line2D]:
[32m-> [39m[32m3838[39m     [38;5;28;01mreturn[39;00m [43mgca[49m[43m([49m[43m)[49m[43m.[49m[43mplot[49m[43m([49m
[32m   3839[39m [43m        [49m[43m*[49m[43margs[49m[43m,[49m
[32m   3840[39m [43m        [49m[43mscalex[49m[43m=[49m[43mscalex[49m[43m,[49m
[32m   3841[39m [43m        [49m[43mscaley[49m[43m=[49m[43mscaley[49m[43m,[49m
[32m   3842[39m [43m        [49m[43m*[49m[43m*[49m[43m([49m[43m{[49m[33;43m"[39;49m[33;43mdata[39;49m[33;43m"[39;49m[43m:[49m[43m [49m[43mdata[49m[43m}[49m[43m [49m[38;5;28;43;01mif[39;49;00m[43m [49m[43mdata[49m[43m [49m[38;5;129;43;01mis[39;49;00m[43m [49m[38;5;129;43;01mnot[39;49;00m[43m [49m[38;5;28;43;01mNone[39;49;00m[43m [49m[38;5;28;43;01melse[39;49;00m[43m [49m[43m{[49m[43m}[49m[43m)[49m[43m,[49m
[32m   3843[39m [43m        [49m[43m*[49m[43m*[49m[43mkwargs[49m[43m,[49m
[32m   3844[39m [43m    [49m[43m)[49m

[36mFile [39m[32mF:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\matplotlib\axes\_axes.py:1777[39m, in [36mAxes.plot[39m[34m(self, scalex, scaley, data, *args, **kwargs)[39m
[32m   1534[39m [38;5;250m[39m[33;03m"""[39;00m
[32m   1535[39m [33;03mPlot y versus x as lines and/or markers.[39;00m
[32m   1536[39m 
[32m   (...)[39m[32m   1774[39m [33;03m(``'green'``) or hex strings (``'#008000'``).[39;00m
[32m   1775[39m [33;03m"""[39;00m
[32m   1776[39m kwargs = cbook.normalize_kwargs(kwargs, mlines.Line2D)
[32m-> [39m[32m1777[39m lines = [*[38;5;28mself[39m._get_lines([38;5;28mself[39m, *args, data=data, **kwargs)]
[32m   1778[39m [38;5;28;01mfor[39;00m line [38;5;129;01min[39;00m lines:
[32m   1779[39m     [38;5;28mself[39m.add_line(line)

[36mFile [39m[32mF:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\.venv\Lib\site-packages\matplotlib\axes\_base.py:297[39m, in [36m_process_plot_var_args.__call__[39m[34m(self, axes, data, return_kwargs, *args, **kwargs)[39m
[32m    295[39m     this += args[[32m0[39m],
[32m    296[39m     args = args[[32m1[39m:]
[32m--> [39m[32m297[39m [38;5;28;01myield from[39;00m [38;5;28;43mself[39;49m[43m.[49m[43m_plot_args[49m[43m([49m
[32m    298[39m [43m    [49m[43maxes[49m[43m,[49m[43m [49m[43mthis[49m[43m,[49m[43m [49m[43mkwargs[49m[43m,[49m[43m [49m[43mambiguous_fmt_datakey[49m[43m=[49m[43mambiguous_fmt_datakey[49m[43m,[49m
[32m    299[39m [43m    [49m[43mreturn_kwargs[49m[43m=[49m[43mreturn_kwargs
...(truncated)
```


---

### Round 19 | tokens: 66,547→1,693

**🤖 LLM:** 有一个小错误，让我修复它并继续分析。

**🔧 → `python_jupyter`**

<details><summary>Code (5369 chars)</summary>

```python
# 修复可视化错误并继续分析
print("继续分析波形特征...")

# 计算对齐后轨迹的方差
aligned_variance = np.var(fine_aligned, axis=0)

# 找到方差最大的区域
window_size = 20
smoothed_variance = np.convolve(aligned_variance, np.ones(window_size)/window_size, mode='valid')

# 找到前10个峰值
peak_indices = []
for i in range(1, len(smoothed_variance)-1):
    if smoothed_variance[i] > smoothed_variance[i-1] and smoothed_variance[i] > smoothed_variance[i+1]:
        peak_indices.append(i)

# 按方差值排序
peak_indices = sorted(peak_indices, key=lambda x: smoothed_variance[x], reverse=True)[:10]

print(f"前10个方差峰值区域:")
for i, idx in enumerate(peak_indices):
    print(f"  峰值 {i+1}: 样本 {idx}, 方差={smoothed_variance[idx]:.4f}")

# 在峰值区域检查CPA相关性
print("\n在峰值区域检查CPA相关性 (字节0):")
peak_correlations = []

for i, peak_idx in enumerate(peak_indices[:5]):
    # 在峰值区域附近进行CPA测试
    test_region_start = max(0, peak_idx - 10)
    test_region_end = min(fine_aligned.shape[1], peak_idx + 10)
    
    # 测试第一个字节在这个区域的相关性
    byte_idx = 0
    correlations, best_key, max_corr, _ = cpa_attack(
        fine_aligned, plaintexts, byte_idx, leakage_model='hd', prev_state=0
    )
    
    # 获取该区域的最大相关性
    region_corr = np.max(np.abs(correlations[:, test_region_start:test_region_end]))
    peak_correlations.append(region_corr)
    
    print(f"峰值区域 {peak_idx}: 最大相关性={region_corr:.4f}")

# 在最佳峰值区域进行完整的CPA攻击
if len(peak_correlations) > 0:
    best_peak_idx = peak_indices[np.argmax(peak_correlations)]
    print(f"\n最佳峰值区域: 样本 {best_peak_idx}, 该区域相关性={np.max(peak_correlations):.4f}")
    
    # 裁剪轨迹到最佳区域附近
    region_start = max(0, best_peak_idx - 50)
    region_end = min(fine_aligned.shape[1], best_peak_idx + 50)
    cropped_traces = fine_aligned[:, region_start:region_end]
    
    print(f"裁剪轨迹到区域 [{region_start}, {region_end}], 长度={cropped_traces.shape[1]}")
    
    # 在裁剪后的轨迹上进行CPA攻击
    print("\n在裁剪后的轨迹上进行CPA攻击...")
    cropped_key, cropped_corrs, cropped_samples, cropped_max_corrs = full_cpa_attack(
        cropped_traces, plaintexts, leakage_model='hd', prev_state=0
    )
    
    print(f"\n裁剪轨迹恢复的密钥: {cropped_key.tobytes().hex()}")
    print(f"平均最大相关性: {np.mean(cropped_max_corrs):.4f}")
    
    # 验证
    cropped_key_bytes = bytes(cropped_key)
    enc_match_count, enc_match_percentage, enc_all_match = verify_key_with_ciphertexts(
        cropped_key_bytes, plaintexts, ciphertexts
    )
    
    print(f"验证结果: {enc_match_count}/100 匹配 ({enc_match_percentage:.1f}%)")
    
    if not enc_all_match:
        print("\n❌ 裁剪区域攻击也失败了。")
        
        # 让我尝试一个不同的方法：使用原始轨迹，但尝试不同的攻击点
        print("\n尝试不同的攻击点...")
        print("根据KG知识，对于硬件实现，可能需要攻击S-box输入而不是输出。")
        
        # 尝试攻击第一轮S-box输入（AddRoundKey的输出）
        print("\n尝试攻击第一轮AddRoundKey输出 (S-box输入)...")
        
        def cpa_attack_sbox_input(traces, plaintexts, target_byte, leakage_model='hd', prev_state=0):
            """攻击S-box输入（AddRoundKey输出）"""
            n_traces = traces.shape[0]
            n_samples = traces.shape[1]
            
            correlations = np.zeros((256, n_samples))
            
            for key_guess in range(256):
                hypothetical_values = np.zeros(n_traces, dtype=np.uint8)
                
                for i in range(n_traces):
                    # AddRoundKey: 明文 ⊕ 密钥
                    sbox_input = plaintexts[i, target_byte] ^ key_guess
                    hypothetical_values[i] = sbox_input
                
                # 根据泄漏模型计算假设功耗
                if leakage_model == 'hw':
                    hypothetical_power = np.array([hamming_weight(v) for v in hypothetical_values])
                elif leakage_model == 'hd':
                    hypothetical_power = np.array([hamming_distance(prev_state, v) for v in hypothetical_values])
                else:
                    raise ValueError(f"未知泄漏模型: {leakage_model}")
                
                # 计算相关性
                for sample in range(n_samples):
                    corr = np.corrcoef(hypothetical_power, traces[:, sample])[0, 1]
                    if np.isnan(corr):
                        corr = 0
                    correlations[key_guess, sample] = corr
            
            # 找到最佳密钥猜测
            max_abs_corr = np.max(np.abs(correlations), axis=1)
            best_key = np.argmax(max_abs_corr)
            max_corr = max_abs_corr[best_key]
            best_sample = np.argmax(np.abs(correlations[best_key, :]))
            
            return correlations, best_key, max_corr, best_sample
        
        # 对第一个字节测试S-box输入攻击
        print("测试字节0的S-box输入攻击...")
        sbox_input_corrs, sbox_input_key, sbox_input_max_corr, sbox_input_sample = cpa_attack_sbox_input(
            fine_aligned, plaintexts, 0, leakage_model='hd', prev_state=0
        )
        
        print(f"S-box输入攻击结果: 最佳密钥=0x{sbox_input_key:02x}, 最大相关性={sbox_input_max_corr:.4f}")
        
        # 比较S-box输出和输入攻击的结果
        sbox_output_corrs, sbox_output_key, sbox_output_max_corr, sbox_output_sample = cpa_attack(
            fine_aligned, plaintexts, 0, leakage_model='hd', prev_state=0
        )
        
        print(f"S-box输出攻击结果: 最佳密钥=0x{sbox_output_key:02x}, 最大相关性={sbox_output_max_corr:.4f}")
        
        if sbox_input_max_corr > sbox_output_max_corr:
            print("S-box输入攻击的相关性更高，这可能表明硬件实现泄漏的是AddRoundKey操作。")
        else:
            print("S-box输出攻击的相关性更高，这可能表明硬件实现泄漏的是S-box操作。")
else:
    print("没有找到有效的峰值区域。")
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (1463 chars)</summary>

```
继续分析波形特征...
前10个方差峰值区域:
  峰值 1: 样本 228, 方差=47.0333
  峰值 2: 样本 61, 方差=35.2427
  峰值 3: 样本 58, 方差=35.2380
  峰值 4: 样本 53, 方差=35.2187
  峰值 5: 样本 56, 方差=35.2126
  峰值 6: 样本 48, 方差=35.2077
  峰值 7: 样本 51, 方差=35.2051
  峰值 8: 样本 46, 方差=35.1849
  峰值 9: 样本 145, 方差=34.8586
  峰值 10: 样本 88, 方差=34.8351

在峰值区域检查CPA相关性 (字节0):
峰值区域 228: 最大相关性=0.0671
峰值区域 61: 最大相关性=0.0657
峰值区域 58: 最大相关性=0.0657
峰值区域 53: 最大相关性=0.0651
峰值区域 56: 最大相关性=0.0651

最佳峰值区域: 样本 228, 该区域相关性=0.0671
裁剪轨迹到区域 [178, 278], 长度=100

在裁剪后的轨迹上进行CPA攻击...
字节  0: 最佳密钥=0x9e, 最大相关性=0.0735, 最佳采样点=3
字节  1: 最佳密钥=0xf4, 最大相关性=0.0741, 最佳采样点=55
字节  2: 最佳密钥=0x40, 最大相关性=0.0916, 最佳采样点=61
字节  3: 最佳密钥=0x2f, 最大相关性=0.0702, 最佳采样点=70
字节  4: 最佳密钥=0x9a, 最大相关性=0.0830, 最佳采样点=35
字节  5: 最佳密钥=0xe3, 最大相关性=0.0803, 最佳采样点=53
字节  6: 最佳密钥=0x55, 最大相关性=0.0736, 最佳采样点=58
字节  7: 最佳密钥=0xc4, 最大相关性=0.0805, 最佳采样点=51
字节  8: 最佳密钥=0x86, 最大相关性=0.0677, 最佳采样点=40
字节  9: 最佳密钥=0x09, 最大相关性=0.0772, 最佳采样点=23
字节 10: 最佳密钥=0x00, 最大相关性=0.0801, 最佳采样点=91
字节 11: 最佳密钥=0x6c, 最大相关性=0.0874, 最佳采样点=31
字节 12: 最佳密钥=0x78, 最大相关性=0.0777, 最佳采样点=52
字节 13: 最佳密钥=0xf3, 最大相关性=0.0720, 最佳采样点=53
字节 14: 最佳密钥=0x37, 最大相关性=0.0788, 最佳采样点=54
字节 15: 最佳密钥=0x59, 最大相关性=0.0753, 最佳采样点=59

裁剪轨迹恢复的密钥: 9ef4402f9ae355c48609006c78f33759
平均最大相关性: 0.0777
验证结果: 0/100 匹配 (0.0%)

❌ 裁剪区域攻击也失败了。

尝试不同的攻击点...
根据KG知识，对于硬件实现，可能需要攻击S-box输入而不是输出。

尝试攻击第一轮AddRoundKey输出 (S-box输入)...
测试字节0的S-box输入攻击...
S-box输入攻击结果: 最佳密钥=0x2b, 最大相关性=0.0529
S-box输出攻击结果: 最佳密钥=0x9e, 最大相关性=0.0735
S-box输出攻击的相关性更高，这可能表明硬件实现泄漏的是S-box操作。
```
</details>


---

### Round 20 | tokens: 69,190→683

<details><summary><b>🤖 LLM Reasoning</b> (1278 chars)</summary>

基于我的分析，我尝试了多种方法但都未能成功恢复密钥。让我总结一下我的发现和建议：

## 总结分析

我对FPGA硬件实现的AES进行了全面的CPA攻击分析，包括：

### 1. **预处理步骤**
- 应用了纵向对齐（vertical alignment）来处理基线漂移
- 尝试了两阶段SAD对齐策略
- 检查了波形方差以识别泄漏区域

### 2. **泄漏模型测试**
- 测试了多种泄漏模型：汉明重量（HW）、汉明距离（HD）、比特模型、零值模型
- 汉明距离模型（假设前一个状态为0）给出了最高的相关性（~0.10）

### 3. **攻击点尝试**
- 第一轮S-box输出攻击
- 最后一轮S-box输入攻击  
- 第一轮AddRoundKey输出（S-box输入）攻击
- S-box输出攻击的相关性最高

### 4. **策略应用**
- 应用了KG中的两阶段对齐和分组攻击策略
- 尝试了key_search和dual模式（k XOR 0xFF）
- 检查了方差峰值区域

## 关键发现

1. **相关性较低**：所有攻击的最大相关性都在0.07-0.10范围内，这相对较低，表明信号噪声比较大或泄漏模型不匹配。

2. **对齐困难**：细对齐的接受率很低（2.5%），表明FPGA实现可能有特殊的时序特性或非确定性延迟。

3. **验证失败**：所有恢复的密钥都未能通过加密/解密验证。

## 建议的下一步

根据KG知识和我的分析，我建议：

### 1. **重新检查波形采集**
- 检查是否有触发信号可用
- 确认采样率是否足够高
- 检查是否有环境噪声干扰

### 2. **尝试不同的预处理**
- 对于FPGA硬件，可能需要尝试带通滤波而不是低通滤波
- 考虑使用PCA降维来提取主要泄漏成分
- 尝试不同的对齐方法，如基于相关性的对齐

### 3. **探索其他攻击方法**
- 尝试二阶CPA攻击，如果实现有掩码保护
- 考虑使用碰撞攻击（collision attack）
- 尝试模板攻击（如果可以获得已知密钥的轨迹）

### 4. **硬件特定考虑**
- FPGA实现可能有流水线或并行处理，导致多个操作同时发生
- 可能需要攻击不同的中间值，如MixColumns输出
- 考虑寄存器传输的精确时序

### 5. **收集更多数据**
- 增加轨迹数量（当前2000条可能不足）
- 尝试不同的明文集合
- 确保采集设置优化（探头位置、采样率等）

## 保存的文件

我已经保存了以下文件供进一步分析：
- `aligned_traces.npy` - 纵向对齐后的轨迹
- `sad_aligned_traces.npy` - SAD对齐后的轨迹
- 多个可视化图表显示了波形特征和分析结果

虽然本次CPA攻击未能成功恢复密钥，但分析过程提供了有价值的信息，可以指导后续的攻击策略调整。FPGA硬件实现的侧信道分析通常比软件实现更具挑战性，需要更精细的预处理和攻击点选择。

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 13,962 | 617 | 14,579 |
| 2 | 14,859 | 791 | 15,650 |
| 3 | 15,702 | 817 | 16,519 |
| 4 | 16,588 | 1,739 | 18,327 |
| 5 | 18,379 | 1,390 | 19,769 |
| 6 | 19,840 | 87 | 19,927 |
| 7 | 27,555 | 1,697 | 29,252 |
| 8 | 29,405 | 974 | 30,379 |
| 9 | 31,041 | 1,093 | 32,134 |
| 10 | 32,233 | 129 | 32,362 |
| 11 | 38,636 | 1,398 | 40,034 |
| 12 | 40,661 | 1,430 | 42,091 |
| 13 | 43,609 | 966 | 44,575 |
| 14 | 44,697 | 670 | 45,367 |
| 15 | 45,983 | 111 | 46,094 |
| 16 | 58,093 | 1,413 | 59,506 |
| 17 | 59,647 | 1,261 | 60,908 |
| 18 | 61,490 | 1,192 | 62,682 |
| 19 | 66,547 | 1,693 | 68,240 |
| 20 | 69,190 | 683 | 69,873 |
| **Total** | **748,117** | **20,151** | **768,268** |

## 8. Final Output

基于我的分析，我尝试了多种方法但都未能成功恢复密钥。让我总结一下我的发现和建议：

## 总结分析

我对FPGA硬件实现的AES进行了全面的CPA攻击分析，包括：

### 1. **预处理步骤**
- 应用了纵向对齐（vertical alignment）来处理基线漂移
- 尝试了两阶段SAD对齐策略
- 检查了波形方差以识别泄漏区域

### 2. **泄漏模型测试**
- 测试了多种泄漏模型：汉明重量（HW）、汉明距离（HD）、比特模型、零值模型
- 汉明距离模型（假设前一个状态为0）给出了最高的相关性（~0.10）

### 3. **攻击点尝试**
- 第一轮S-box输出攻击
- 最后一轮S-box输入攻击  
- 第一轮AddRoundKey输出（S-box输入）攻击
- S-box输出攻击的相关性最高

### 4. **策略应用**
- 应用了KG中的两阶段对齐和分组攻击策略
- 尝试了key_search和dual模式（k XOR 0xFF）
- 检查了方差峰值区域

## 关键发现

1. **相关性较低**：所有攻击的最大相关性都在0.07-0.10范围内，这相对较低，表明信号噪声比较大或泄漏模型不匹配。

2. **对齐困难**：细对齐的接受率很低（2.5%），表明FPGA实现可能有特殊的时序特性或非确定性延迟。

3. **验证失败**：所有恢复的密钥都未能通过加密/解密验证。

## 建议的下一步

根据KG知识和我的分析，我建议：

### 1. **重新检查波形采集**
- 检查是否有触发信号可用
- 确认采样率是否足够高
- 检查是否有环境噪声干扰

### 2. **尝试不同的预处理**
- 对于FPGA硬件，可能需要尝试带通滤波而不是低通滤波
- 考虑使用PCA降维来提取主要泄漏成分
- 尝试不同的对齐方法，如基于相关性的对齐

### 3. **探索其他攻击方法**
- 尝试二阶CPA攻击，如果实现有掩码保护
- 考虑使用碰撞攻击（collision attack）
- 尝试模板攻击（如果可以获得已知密钥的轨迹）

### 4. **硬件特定考虑**
- FPGA实现可能有流水线或并行处理，导致多个操作同时发生
- 可能需要攻击不同的中间值，如MixColumns输出
- 考虑寄存器传输的精确时序

### 5. **收集更多数据**
- 增加轨迹数量（当前2000条可能不足）
- 尝试不同的明文集合
- 确保采集设置优化（探头位置、采样率等）

## 保存的文件

我已经保存了以下文件供进一步分析：
- `aligned_traces.npy` - 纵向对齐后的轨迹
- `sad_aligned_traces.npy` - SAD对齐后的轨迹
- 多个可视化图表显示了波形特征和分析结果

虽然本次CPA攻击未能成功恢复密钥，但分析过程提供了有价值的信息，可以指导后续的攻击策略调整。FPGA硬件实现的侧信道分析通常比软件实现更具挑战性，需要更精细的预处理和攻击点选择。
