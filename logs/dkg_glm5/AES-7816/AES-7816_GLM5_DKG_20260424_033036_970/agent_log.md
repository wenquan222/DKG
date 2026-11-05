# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `Pro/zai-org/GLM-5` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260424_033036_970 |
| Duration | 97.6s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp3_GLM-5\AES-7816_GLM5_DKG_20260424_033036_970` |
| Total LLM Calls | 7 |
| First Round | prompt: 12,679, completion: 739 |
| Last Round | prompt: 17,705, completion: 523 |
| Total Tokens | 113,648 (prompt: 109,810, completion: 3,838) |

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

LLM Response: json
["AES", "Contact Smartcard", "CPA", "ISO 7816"]

Parsed Keywords: `["AES", "Contact Smartcard", "CPA", "ISO 7816"]`

**Step B: KG Search**

Config: `{"max_results_per_keyword": 5, "max_diagnostic_chains": 5, "max_upper_components": 8}`

KG returned 25885 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (28133 chars, click to expand)</summary>

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

**Search keywords** (4): AES, Contact Smartcard, CPA, ISO 7816

**Summary**: 15 upper entities, 14 relationships, 10 diagnostic chains, 9 strategies


## 1. Upper Layer Entities (15)


### Algorithm (1)

- **AES** — num_rounds=14, encryption_mode=CBC, key_length=256

### DeviceClass (4)

- **AES ASIC** — category=ASIC
- **AES-128 core (TSMC 65nm)** — category=ASIC
- **BasicAesSimulationContainer** — category=Simulated
- **Contact Smartcard with 16-bit RISC CPU** — category=Smartcard, bus_width=16

### Pipeline (5)

- **Algebraic Side-Channel Attack** — source=paper, trigger_condition=starting an algebraic side-channel attack on a symmetric block cipher, applicable_scenarios=Symmetric block ciphers with simple algebraic structure (e.g., PRESENT, AES) implemented on devices with informative leakage models (e.g., Hamming weight). Can work with single trace, unknown plaintext/ciphertext, and masked implementations.
- **CPA Attack on AES Firmware Implementation** — source=tutorial, trigger_condition=when performing non-profiled CPA attack on AES firmware implementation, applicable_scenarios=CPA attack on AES using power traces, targeting first round S-box output with Hamming Weight leakage model
- **ChipWhisperer Analyzer CPA Attack** — source=tutorial, trigger_condition=when you have a ChipWhisperer project with power traces of an AES encryption, applicable_scenarios=CPA attack on AES using ChipWhisperer Analyzer tool
- **Combined Collision Attack Framework** — source=PAP-104-2012-IEEE-ToC-Beyond-Limits-DPA-Collision, trigger_condition=when attacking an AES-128 implementation with side-channel leakage to recover the key with limited traces, applicable_scenarios=AES-128 on 8-bit microcontrollers using power consumption traces
- **Unified Analysis Process (8 Steps)** — is_canonical=True, source=expert_experience, priority=100, trigger_condition=starting any CPA analysis task, applicable_scenarios=general CPA workflow across software, hardware, pre-cropped, and long-waveform scenarios

### StatMethod (5)

- **2nd-order CPA** — type=non_profiled
- **CPA** — type=non_profiled
- **CPA with conditional averaging** — type=non_profiled
- **Correlation Power Analysis (CPA)** — type=non_profiled
- **DPA (CPA) for Key-Byte Ranking** — type=non_profiled

## 2. Relationships (14)

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

## 3. Diagnostic Chains (10)


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

## 4. Strategies (9)


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

**[Session Directory]**
All files for this session are stored in: ..\logs\exp3_GLM-5\AES-7816_GLM5_DKG_20260424_033036_970
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp3_GLM-5\AES-7816_GLM5_DKG_20260424_033036_970/'` or `'../logs/...'` — just use the bare filename.
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

### Round 1 | tokens: 12,679→739

**🤖 LLM:** 我来帮你对接触式智能卡的AES波形进行CPA攻击。根据知识图谱，接触式智能卡AES的标准攻击配置是：
- **攻击点**：S-box Output（第一轮S-box输出）
- **泄漏模型**：Hamming Weight (HW)

让我先进行直接CPA探测，评估波形质量：

**🔧 → `aes_cpa_attack`**

<details><summary>Arguments</summary>

```json
{
  "plaintext_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "wave_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}
```
</details>

<details><summary><b>📋 ← `aes_cpa_attack`</b> (3567 chars)</summary>

```
{"recovered_key": "146F98806836F55937FBCD36B5CF7096", "cpa_avg_correlation": 0.4648, "cpa_min_correlation": 0.4358, "n_traces": 100, "target": "S-box_out", "plot_path": "cpa_result_20260424_033115_200573.png", "detail_file": "cpa_detail_20260424_033115_200573.json", "per_byte": [{"byte": 0, "key": "0x14", "correlation": 0.4497, "time_index": 4625, "gap_pct": 0.5}, {"byte": 1, "key": "0x6F", "correlation": 0.4383, "time_index": 408, "gap_pct": 2.2}, {"byte": 2, "key": "0x98", "correlation": 0.4483, "time_index": 3443, "gap_pct": 2.8}, {"byte": 3, "key": "0x80", "correlation": 0.5045, "time_index": 1938, "gap_pct": 14.4}, {"byte": 4, "key": "0x68", "correlation": 0.4358, "time_index": 714, "gap_pct": 4.5}, {"byte": 5, "key": "0x36", "correlation": 0.4763, "time_index": 6619, "gap_pct": 1.0}, {"byte": 6, "key": "0xF5", "correlation": 0.4802, "time_index": 586, "gap_pct": 5.5}, {"byte": 7, "key": "0x59", "correlation": 0.4638, "time_index": 2732, "gap_pct": 8.4}, {"byte": 8, "key": "0x37", "correlation": 0.4605, "time_index": 4182, "gap_pct": 4.5}, {"byte": 9, "key": "0xFB", "correlation": 0.4505, "time_index": 5658, "gap_pct": 3.1}, {"byte": 10, "key": "0xCD", "correlation": 0.4594, "time_index": 6070, "gap_pct": 8.2}, {"byte": 11, "key": "0x36", "correlation": 0.4719, "time_index": 1381, "gap_pct": 3.6}, {"byte": 12, "key": "0xB5", "correlation": 0.4855, "time_index": 6826, "gap_pct": 3.4}, {"byte": 13, "key": "0xCF", "correlation": 0.4655, "time_index": 1142, "gap_pct": 3.0}, 
...(truncated)
```
</details>


![cpa_result_20260424_033115_200573.png](./cpa_result_20260424_033115_200573.png)


---

### Round 2 | tokens: 14,523→968

**🤖 LLM:** 直接CPA结果显示：
- **平均相关系数**：0.4648（较高，信号质量不错）
- **高置信度字节数**：0/16（红带）
- **问题**：所有字节的gap_pct都低于15%阈值

这是典型的红带情况。根据知识图谱策略，我需要先定位加密区间。让我进行方差分析来找到真正的加密区域：

**🔧 → `python_jupyter`**

<details><summary>Code (1987 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载波形数据
wave = np.load('data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy')
print(f"波形形状: {wave.shape}")

# 计算方差分布（滑动窗口）
window_size = 50
variances = []
for i in range(0, wave.shape[1] - window_size, window_size // 2):
    window = wave[:, i:i+window_size]
    variances.append(np.var(window, axis=0).mean())

variances = np.array(variances)
var_peak_idx = np.argmax(variances)
var_peak_sample = var_peak_idx * (window_size // 2)

print(f"\n方差分析:")
print(f"方差峰值位置: sample {var_peak_sample}")
print(f"方差峰值值: {variances[var_peak_idx]:.4f}")

# 找到方差突增区域（加密区间）
threshold = variances.mean() + variances.std()
high_var_regions = np.where(variances > threshold)[0]
if len(high_var_regions) > 0:
    roi_start = high_var_regions[0] * (window_size // 2)
    roi_end = (high_var_regions[-1] + 1) * (window_size // 2) + window_size
    print(f"高方差区域: samples {roi_start} - {roi_end}")
    print(f"区域长度: {roi_end - roi_start} samples")

# 绘制方差分布
plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
plt.plot(variances)
plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
plt.axvline(x=var_peak_idx, color='g', linestyle='--', label=f'Peak at {var_peak_sample}')
plt.xlabel('Window Index')
plt.ylabel('Variance')
plt.title('Variance Distribution Across Waveform')
plt.legend()
plt.grid(True, alpha=0.3)

# 绘制一条示例波形
plt.subplot(1, 2, 2)
plt.plot(wave[0])
plt.axvline(x=var_peak_sample, color='g', linestyle='--', label=f'Variance Peak {var_peak_sample}')
if len(high_var_regions) > 0:
    plt.axvspan(roi_start, roi_end, alpha=0.2, color='red', label='High Variance ROI')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Sample Trace (Trace 0)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('variance_analysis.png', dpi=150)
plt.show()

print(f"\n建议的加密区间: samples {max(0, roi_start-200)} - {min(wave.shape[1], roi_end+200)}")
```
</details>

**📋 ← `python_jupyter`:** `波形形状: (100, 7400)

方差分析:
方差峰值位置: sample 1350
方差峰值值: 4016.5791
高方差区域: samples 1075 - 6775
区域长度: 5700 samples

建议的加密区间: samples 875 - 6975
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\2631138256.py:58: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 3 | tokens: 15,396→483

**🤖 LLM:** 方差分析显示高方差区域很宽（1075-6775），但CPA结果显示各字节泄漏时间分散在408-6826范围内。这表明可能存在对齐问题。让我进行明文相关性分析来精确定位泄漏区域：

**🔧 → `plaintext_ciphertext_correlation`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy",
  "data_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "data_type": "plaintext",
  "byte_index": 0,
  "model": "SBOX_HW"
}
```
</details>

**📋 ← `plaintext_ciphertext_correlation`:** `{"peak_region_start": 4476, "peak_region_end": 5435, "peak_time_index": 4625, "peak_correlation": 0.4497, "suggested_cpa_range": [4285, 5626], "all_byte_peaks": [1165, 952, 1130, 862, 4886, 5424, 125, 6555, 6955, 6467, 2298, 6610, 168, 600, 58, 6330], "byte_peaks_std": 2741.6, "plot_path": "correlation_20260424_033150_853213.png"}`


![correlation_20260424_033150_853213.png](./correlation_20260424_033150_853213.png)


---

### Round 4 | tokens: 15,779→525

**🤖 LLM:** 明文相关性分析揭示了关键问题：
- **字节泄漏时间标准差**：2741.6（极高！）
- **字节泄漏分散范围**：58 到 6955

这证实了存在严重的对齐问题。根据知识图谱策略，我需要进行静态对齐。使用接触式智能卡AES的推荐参数：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy",
  "start": 4500,
  "length": 100,
  "max_shift": 400,
  "threshold": 85,
  "ref_trace": 1,
  "plaintext_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy",
  "ciphertext_npy": "data/traces/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `static_aligner`</b> (774 chars)</summary>

```
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
<>:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
C:\Users\Andersen\AppData\Local\Temp\ipykernel_15860\1218181736.py:11: SyntaxWarning: "is" with a literal. Did you mean "=="?
  ref_trace = len(waves) // 2 if 1 is None else int(1)
{"out_aligned_npy": "aligned_20260424_033202_247228.npy", "plot_path": "align_overlay_20260424_033202_247228.png", "ref_trace_used": 1, "accepted": 100, "discarded": 0, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260424_033202_247228.npy", "plaintext_traces": 100, "out_ciphertext_npy": "ciphertext_aligned_20260424_033202_247228.npy", "ciphertext_traces": 100, "alignment_avg_correlation": 0.992, "alignment_min_correlation": 0.985, "acceptance_rate": 1.0}
```
</details>


![align_overlay_20260424_033202_247228.png](./align_overlay_20260424_033202_247228.png)


---

### Round 5 | tokens: 16,361→202

**🤖 LLM:** 对齐非常成功！
- **接受率**：100%（100/100条轨迹全部接受）
- **对齐平均相关系数**：0.992（极高）

现在用对齐后的波形重新进行CPA攻击：

**🔧 → `aes_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260424_033202_247228.npy",
  "wave_npy": "aligned_20260424_033202_247228.npy",
  "target": "S-box_out",
  "leakage_model": "HW",
  "candidates": 20
}`

<details><summary><b>📋 ← `aes_cpa_attack`</b> (2061 chars)</summary>

```
{"recovered_key": "112233445566778899AABBCCDDEEFF00", "cpa_avg_correlation": 0.7966, "cpa_min_correlation": 0.7408, "n_traces": 100, "target": "S-box_out", "plot_path": "cpa_result_20260424_033210_665415.png", "detail_file": "cpa_detail_20260424_033210_665415.json", "per_byte": [{"byte": 0, "key": "0x11", "correlation": 0.7568, "time_index": 1567, "gap_pct": 38.7}, {"byte": 1, "key": "0x22", "correlation": 0.7945, "time_index": 1888, "gap_pct": 40.1}, {"byte": 2, "key": "0x33", "correlation": 0.7555, "time_index": 2207, "gap_pct": 33.1}, {"byte": 3, "key": "0x44", "correlation": 0.8269, "time_index": 2528, "gap_pct": 39.9}, {"byte": 4, "key": "0x55", "correlation": 0.85, "time_index": 2847, "gap_pct": 43.0}, {"byte": 5, "key": "0x66", "correlation": 0.831, "time_index": 3167, "gap_pct": 46.6}, {"byte": 6, "key": "0x77", "correlation": 0.8166, "time_index": 3487, "gap_pct": 44.0}, {"byte": 7, "key": "0x88", "correlation": 0.8352, "time_index": 3807, "gap_pct": 43.0}, {"byte": 8, "key": "0x99", "correlation": 0.8119, "time_index": 4111, "gap_pct": 41.8}, {"byte": 9, "key": "0xAA", "correlation": 0.794, "time_index": 4432, "gap_pct": 36.1}, {"byte": 10, "key": "0xBB", "correlation": 0.7446, "time_index": 4749, "gap_pct": 36.7}, {"byte": 11, "key": "0xCC", "correlation": 0.7573, "time_index": 5087, "gap_pct": 31.0}, {"byte": 12, "key": "0xDD", "correlation": 0.8373, "time_index": 5392, "gap_pct": 46.6}, {"byte": 13, "key": "0xEE", "correlation": 0.7408, "time_index": 5712, "gap_p
...(truncated)
```
</details>


![cpa_result_20260424_033210_665415.png](./cpa_result_20260424_033210_665415.png)


---

### Round 6 | tokens: 17,367→398

**🤖 LLM:** 太棒了！对齐后的CPA结果非常优秀：
- **恢复密钥**：`112233445566778899AABBCCDDEEFF00`
- **平均相关系数**：0.7966（极高！）
- **高置信度字节数**：16/16（绿带！）
- **所有字节gap_pct**：31.0% - 47.2%（全部远超15%阈值）

现在验证密钥是否正确：

**🔧 → `encrypt_decrypt_verify`** `{
  "algorithm": "AES",
  "key_hex": "112233445566778899AABBCCDDEEFF00",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260424_033202_247228.npy",
  "ciphertext_npy": "ciphertext_aligned_20260424_033202_247228.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "290AD4A41F352B837787D9581DFC4C43", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "AES-128-ECB encrypt: 3871ca2c3c022647f326197e85d4aa71... → 290AD4A41F352B837787D9581DFC4C43...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 7 | tokens: 17,705→523

**🤖 LLM:** 🎉 **密钥恢复成功！**

## 攻击结果总结

### 恢复的密钥
```
112233445566778899AABBCCDDEEFF00
```

### 攻击过程

**1. 直接CPA探测（未对齐）**
- 平均相关系数：0.4648
- 高置信度字节数：0/16（红带）
- 问题：字节泄漏时间分散（标准差2741.6），存在严重对齐问题

**2. 静态对齐**
- 对齐参数：start=4500, length=100, max_shift=400, threshold=85
- 接受率：100%（100/100条轨迹）
- 对齐相关系数：0.992

**3. 对齐后CPA攻击**
- 平均相关系数：**0.7966**（提升71%）
- 高置信度字节数：**16/16**（绿带）
- 所有字节gap_pct：31.0% - 47.2%

**4. 密钥验证**
- ✅ 验证通过：密钥正确

### 关键发现

接触式智能卡AES实现存在明显的时序抖动，导致不同轨迹中相同操作出现在不同时间点。通过静态对齐（基于S-box输出区域的特征峰）成功解决了这个问题，使CPA攻击的相关系数从0.46提升到0.80，所有16个密钥字节均以高置信度恢复。


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 12,679 | 739 | 13,418 |
| 2 | 14,523 | 968 | 15,491 |
| 3 | 15,396 | 483 | 15,879 |
| 4 | 15,779 | 525 | 16,304 |
| 5 | 16,361 | 202 | 16,563 |
| 6 | 17,367 | 398 | 17,765 |
| 7 | 17,705 | 523 | 18,228 |
| **Total** | **109,810** | **3,838** | **113,648** |

## 8. Final Output

🎉 **密钥恢复成功！**

## 攻击结果总结

### 恢复的密钥
```
112233445566778899AABBCCDDEEFF00
```

### 攻击过程

**1. 直接CPA探测（未对齐）**
- 平均相关系数：0.4648
- 高置信度字节数：0/16（红带）
- 问题：字节泄漏时间分散（标准差2741.6），存在严重对齐问题

**2. 静态对齐**
- 对齐参数：start=4500, length=100, max_shift=400, threshold=85
- 接受率：100%（100/100条轨迹）
- 对齐相关系数：0.992

**3. 对齐后CPA攻击**
- 平均相关系数：**0.7966**（提升71%）
- 高置信度字节数：**16/16**（绿带）
- 所有字节gap_pct：31.0% - 47.2%

**4. 密钥验证**
- ✅ 验证通过：密钥正确

### 关键发现

接触式智能卡AES实现存在明显的时序抖动，导致不同轨迹中相同操作出现在不同时间点。通过静态对齐（基于S-box输出区域的特征峰）成功解决了这个问题，使CPA攻击的相关系数从0.46提升到0.80，所有16个密钥字节均以高置信度恢复。
