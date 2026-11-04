# DKG 抽取架构审视（2026-04-20，全量启动前）

> 在 176 份新材料全量抽取前，对 step1-3 架构 + prompts + 流程的系统性诊断。
> 审视者：Claude（会请 Codex 独立做同样审视并合并意见）

---

## 0. 架构回顾

```
raw/*.{pdf,docx,...}
    ↓  extract.py / extract_chunked.py （文档文本化）
extracted/*.md   (178 份，其中 BOOK-01/MAN-07/MAN-08 过 LLM 窗口)
    ↓  step1_locator.py  + prompts/step1_{upper,lower}.txt
workspace/<stem>/step1_{upper,lower}.json   (结构化记录 + unclassified_knowledge)
    ↓  step2_triple_extractor.py + prompts/step2_{upper,lower}.txt
workspace/<stem>/step2_{upper,lower}.json   (entities + relationships)
    ↓  step3_knowledge_fusion.py + prompts/step3_*.txt
workspace/_merged/{upper,lower,cross}.json  (标准化 + 去重 + 融合 + 跨层)
    ↓  init_graph.py
Neo4j  (upper 12 节点 / 8 关系 + lower 4 节点 / 3 关系)
```

**2 层（upper config-space + lower diagnostic-chain）× 3 步（locate / triple / fuse）= 6 个 prompt 文件 + 3 个 Python 脚本。**

---

## 1. 每一步的问题清单

### Step 1 — Locator（从文档抽结构化记录）

**问题 1.1（★★★ 阻塞级）：输入硬编码且只含 6 个旧文件**

`step1_locator.py` 的 `input_files` 写死为：
- `expert_experience.md`
- 5 份 manuals&tutorials docx

**现状**：这 6 份都在 **raw/** 老路径下（实际已删了，现在应该走 `extracted/` 的 MAN-01..06）。
**影响**：全量 178 份无法批量处理。
**修复**：改成自动扫描 `knowledge/sources/extracted/*.md`，并按类别（PAP/STD/MAN/TOOL/BOOK/THE/GUI/HWM/SLD/BLG）选择性 `skip_layers`。

**问题 1.2（★★★ 阻塞级）：MAN-07 单文件 28.5 万 token，超 160K 窗口**

实测 token（用字符估算）：
- MAN-07 ~ 284K tokens（超 160K 窗口 1.8×）
- BOOK-01 ~ 140K tokens（接近极限）
- MAN-08 ~ 106K tokens（接近极限）

**影响**：这三份会报 `BadRequest 20015 max_prompt_tokens 163840`。
**修复**：step1 需加"输入切块"逻辑。分块策略：
- 按 `## ` 章节切
- 每块最大 100K token（预留 60K 给 prompt + 推理 + 输出）
- 每块独立抽取 → 合并 records（去 id 冲突）

**问题 1.3（★★ 重要）：Scope filter 未真正实现**

`step1_upper.txt` Rule 8 只说"ignore timing analysis, TVLA, known-key evaluation, UI operations, file format details, wiring instructions, plotting steps"。

**缺漏**：
- 没明确排除 PQC / RSA / ECC / 流密码（Ascon/ChaCha）/ 认证加密
- 没明确排除 template / DL-SCA / profiled 类建模攻击
- 实际即使 raw/ 层面已清理，**单份文档内部仍混越界内容**（Mangard 中文书含 RSA 章节、SoK 综述覆盖 PQC、Riscure Inspector 含 template 教程等）

**修复**：在 step1_{upper,lower}.txt 加显式"白/黑名单"段落：
```
### Scope Lock

ONLY extract knowledge within this scope:
  - algorithms: AES / DES / 3DES / SM4 / PRESENT / ARIA / Camellia / SEED /
    SIMON / SPECK / GIFT / SKINNY (symmetric block ciphers)
  - attack types: non-profiled only — CPA / DPA / MIA / Collision /
    2nd-order / Linear Regression (non-stochastic) / Algebraic SCA

SKIP entirely (do NOT create records):
  - RSA / ECC / ECDSA / Ed25519 / Diffie-Hellman
  - PQC: Dilithium / Kyber / Falcon / SPHINCS / McEliece / BIKE
  - stream ciphers: ChaCha20 / Salsa20 / Ascon / Xoodyak
  - AEAD / MAC / hash-specific attacks
  - template attacks / profiled attacks / stochastic attacks
  - DL-SCA / CNN / MLP / Transformer-based SCA
  - fault injection / glitching / DFA
  - timing attacks / cache attacks / rowhammer

If a paragraph mixes in-scope and out-of-scope content:
  - extract only the in-scope part
  - list the out-of-scope content briefly in unclassified_knowledge
    with route_to="out_of_scope"
```

**问题 1.4（★ 次要）：`unclassified_knowledge` 的 `truly_unknown` 机制已有但没强化**

Prompt 已有 `route_to: "truly_unknown"` 的桶，给 **schema 表达不了** 的知识留路径。好。
**建议加强**：要求 LLM 给 truly_unknown 条目附 `proposed_node_type` 字段，比如：
```json
{
  "content": "trace 中的时钟漂移频谱特性（f=2.3MHz ± 0.2MHz 随温度变化）",
  "route_to": "truly_unknown",
  "proposed_node_type": "SignalProperty / HardwareCharacteristic",
  "proposed_schema_extension": "add new node type 'SignalProperty' with [name, freq_range, variability]"
}
```
后面迭代 schema 时这些建议就是直接输入。

**问题 1.5（★ 次要）：ID 冲突**

Step1 每份文档单独跑，生成 `experiment_id: exp_001`、`strategy_id: strat_001` 都从 001 起。跨文档有重复。
**影响**：step3 融合时可能被当重复剔除。
**修复**：step1 输出前加文档前缀，如 `exp_PAP-01_001`。

---

### Step 2 — Triple Extractor（结构化记录 → 图三元组）

**问题 2.1（★★ 重要）：输入用 Step 1 的 JSON，但依赖 Step 1 质量**

Step2 的输入是 Step1 的结构化 JSON（通常 < 50K token），输入侧 OK。
**但**：如果 Step1 漏抽或错抽（受 1.3 scope 问题影响），Step2 传错误的下去。

**修复**：不改 step2，但 step1 的 scope filter 必须先修。

**问题 2.2（★★ 重要）：step2_upper 没提 4 个新 upper 节点的语义边界**

Codex 加的 `DiagnosticMethod / ValidationMethod / RecoveryMethod` 在 step2_upper.txt 第 30-32 行列出了，但**没有明确边界规则**（什么算 Diagnostic vs Preprocessing？）。

**风险**：LLM 把传统 Preprocessing（如 POI Selection via SNR）误判为 DiagnosticMethod（"quality_assessment"）。

**修复**：step2_upper.txt 加辨析表：
```
Node Type Disambiguation:
- Preprocessing = applies a transformation to traces (filter, align, compress, project)
- DiagnosticMethod = makes a BRANCHING decision without transforming traces
  (e.g., judge implementation prototype, select candidate interval by plaintext correlation)
- ValidationMethod = verifies a key candidate using plaintext+ciphertext
- RecoveryMethod = constructs full key from partial/ambiguous subkeys (search, merge)
```

**问题 2.3（★ 次要）：Inference Rules 过于激进**

step2_upper.txt 的 inference rules：
- `If device name contains STM32 and bus_width is null -> set bus_width=32, category=MCU`
- `If CPA succeeded on software -> infer Hamming Weight`
- `If CPA succeeded on hardware -> infer Hamming Distance`

这些是有道理的，但**源文档没说 implementation_type 时依然可能推错**（比如 STM32 跑了硬件 AES 协处理器，该用 HD，但规则只看 name=STM32 就推 HW）。

**修复**：推理规则前加 guard："仅当 explicit source text 明示 implementation type 才推"。

---

### Step 3 — Knowledge Fusion（跨文档融合）

**问题 3.1（★★ 重要）：融合时可能错把不同 schema 的相似实体合并**

step3 有 ENTITY_NAME_MAPPING 静态表 + LLM 推断冲突裁决。静态表能处理显性别名（Flow A = Unified Process）。

**风险**：LLM 融合时可能把"Static Alignment"和"Vertical Alignment"当同一个实体合并（都是 alignment 类）。

**修复**：step3 prompt 加"合并禁止清单"（显式列出不应合并的近义节点对）。

**问题 3.2（★★ 重要）：`works_with` confidence 计算公式不透明**

step3 代码里有 confidence 计算，但 prompt 没写规则。
**建议**：step3_upper.txt 加明确公式（例如 `confidence = log(1 + support_count) / log(1 + 10)`, clamp to [0,1]），让 LLM 理解。

**问题 3.3（★ 次要）：跨层 strategy_applies_to 的质量依赖 lower 侧的 `related_upper_entities` 字段**

step1_lower 让 LLM 自己写 `related_upper_entities`，step3 再匹配上层实体名。
**风险**：LLM 写的名称可能和上层实际抽到的不完全一致（"Static Alignment" vs "static alignment" vs "Alignment"）。

**修复**：step3 匹配时加大小写无关 + 子串包含的宽松匹配。代码里已有部分处理，需加单元测试覆盖。

---

## 2. 无关知识会不会抽出来？

### 当前情况

- Step 1 prompt Rule 8 只排除"UI/wiring/timing analysis/TVLA"，**不排除 PQC/RSA/ECC/建模**
- Step 1 `unclassified_knowledge.route_to` 有 4 个桶：`lower` / `lower_strategy` / `upper` / `upper_pipeline` / `truly_unknown`，**但没有 `out_of_scope` 桶**
- 结果：跨算法/跨威胁模型的越界知识**会被 LLM 尝试塞进 specific_experiment 或 diagnostic_triple**

### 风险实例

- **Mangard 中文书** 含 RSA 模乘攻击章节 → LLM 可能抽出 "Algorithm: RSA"、"AttackPoint: Modular Multiplication" 三元组
- **PAP-69 Picek SoK-DLSCA** 综述对比 DL vs non-profiled → LLM 可能把 DL 实验当 specific_experiment 抽
- **PAP-97 SM4 论文** 摘要提到对比 template 方法 → LLM 可能创建 "template attack" 节点

### 修复方案（要在 prompt 里强制）

**方案 D（我在 extraction_issues.md 已记录）：Prompt 规则打底 + 白名单兜底**

1. Prompt 层：step1_{upper,lower}.txt 加明确 Scope Lock 段（见 1.3 修复示例）
2. 代码层：step2/step3 过滤器（白名单）
   ```python
   ALLOWED_ALGORITHMS = {"AES", "DES", "3DES", "SM4", "PRESENT", "ARIA", "Camellia", "SEED", "SIMON", "SPECK", "GIFT", "SKINNY"}
   ALLOWED_STATMETHOD_TYPES = {"non_profiled"}
   # 上层实体 Algorithm / StatMethod 不在白名单 → 丢弃 + 记 warning
   ```

---

## 3. 超出 schema 表达边界的知识怎么记？

### 当前机制（已存在，较弱）

Step 1 prompt 的 `unclassified_knowledge.route_to: "truly_unknown"` 会把 "schema 装不下的知识" 存到 JSON 里：
```json
{
  "content": "...",
  "why_valuable": "...",
  "route_to": "truly_unknown",
  "routing_reason": "..."
}
```

Step 1 代码 `_check_unclassified` 会按 route_to 分桶，存到 `workspace/<stem>/unclassified_knowledge_{upper,lower}.json`。

### 增强建议

**步骤 A：让 LLM 主动给 schema extension proposal**

改 step1 prompt 的 truly_unknown 段落：
```
For "truly_unknown" items, additionally provide:
  "proposed_node_type": "suggest a new node type name in PascalCase"
  "proposed_properties": ["list", "of", "attribute_names"]
  "proposed_relations": "describe how this node should connect to existing 12 upper nodes"
```

**步骤 B：跨文档聚合 truly_unknown 后人工 review**

加一个 step3.5（或 step3 内部）：把所有文档的 truly_unknown 项目聚合 → LLM 做主题聚类 → 输出 "schema extension suggestions" 文档：
```markdown
# Schema Extension Candidates (auto-generated)

## Candidate 1: SignalProperty (suggested 15 times across 8 documents)
- Typical content: clock drift, frequency variability, sampling artifacts
- Suggested properties: [name, freq_range, variability_source]
- Example records: ...

## Candidate 2: HardwareNoise (suggested 7 times)
...
```

**步骤 C：每大版本（阶段）手工 review 这份提案文档，决定是否加节点**

和我们之前讨论的 CodeReference/Dataset 一样 — **不主动加，等数据告诉我们需要**。

---

## 4. 其他系统性问题

### 4.1 Token 预算可观测性缺失

**问题**：每次 LLM 调用的 input/output tokens 没统计到文件。如果某个文档被"静默截断"或 finish_reason=length，现在代码不报警。

**修复**：`call_llm` 返回 response 对象前记录 `response.usage` 到 log：
```python
print(f"  usage: prompt={u.prompt_tokens}, completion={u.completion_tokens}, "
      f"finish={resp.choices[0].finish_reason}")
```

### 4.2 缺单元测试

**问题**：176 份文档全量跑前，没 smoke test（比如针对 expert_experience.md 的已知 golden output 做对比）。
**建议**：保留 phase 11 的 `final_upper.json` / `final_lower.json` 作 ground truth，每次改 prompt 后回归测试一次。

### 4.3 抽取耗时估算

- Thinking 模式 + 中等文档（30K token）每个文档 ~3-5 分钟
- 178 份 × 4 分钟 × 2 层（step1 upper+lower）= **~24 小时**
- Step2 在 step1 output 上再跑一次 ~5 分钟/份 = **~30 小时**
- Step3 全量融合 ~1-2 小时
- **全流程估计 50-60 小时**

**建议**：分批跑（先跑专家经验 + MAN 6 份做 smoke test → 对结果满意再上 PAP 80+ 份）。

---

## 5. 全量启动前必做清单

### 阻塞级（不做不能跑）
- [ ] 修 step1_locator.py 的 `input_files` 硬编码 → 改为扫描 `extracted/*.md`
- [ ] 加 step1 输入切块逻辑（MAN-07/BOOK-01 会报错）
- [ ] 加 step1_{upper,lower}.txt 的 Scope Lock 段

### 重要（做了质量显著提升）
- [ ] 加 step2_upper.txt 的 4 个新节点类型辨析
- [ ] 加 step3 合并禁止清单
- [ ] 加白名单 post-filter（Algorithm / StatMethod.type）
- [ ] 加 `response.usage` 日志

### 可选（lower priority）
- [ ] truly_unknown 增加 proposed_node_type 字段
- [ ] 跨层匹配宽松化（大小写无关）
- [ ] step1 ID 加文档前缀避免冲突

### 跑前验证
- [ ] 在 expert_experience.md 上 smoke test（对比 phase 11 的 final_*.json）
- [ ] 在 1 份英文 paper + 1 份中文 paper + 1 份 TOOL.md 各跑一遍看输出质量

---

## 6. 决策点（需要你定）

1. **切块策略**：按章节（`##`）切还是按字符数固定切？
   - 按章节切更语义化但实现复杂
   - 按字符切简单但可能切到句中间
   - **我建议**：按 `##`/`#` 切，若单章节 > 80K token 再切二级
   
2. **白名单过滤放哪一层**：step1 prompt 里让 LLM 过滤？还是 step2 代码里过滤？
   - Prompt 层：LLM 可能偶尔漏网
   - 代码层：确定性强，但需维护列表
   - **我建议**：都做（双保险），先 prompt 靠 LLM 智能判断边界，后代码兜底

3. **smoke test 用什么作为 ground truth**？
   - phase 11 的 final_upper.json / final_lower.json 是基于旧的 9 节点 schema，现在是 12 节点
   - 可以拿来对比但不 100% 对等
   - **我建议**：手工 review expert_experience.md 的 step1 输出，做一份 "2026 baseline"

---

## 附：Codex 独立审视 prompt

把下面整段发给 Codex（或另一个 Claude 实例），让它独立给一份审视报告：

```
任务：独立审视 DKG 知识图谱抽取架构

背景：
- 项目位于 F:\侧信道\SCA-GPT\实验五：基于知识图谱的Agent\GraphRAG_Agent\DKG
- 176 份源材料已抽取为 extracted/*.md
- 抽取 pipeline 3 步：step1 Locate → step2 Triple → step3 Fuse
- 每步分 upper（12 节点配置空间）+ lower（4 节点诊断链）两层
- 范围：Non-profiled SCA on 分组密码（AES/DES/SM4 等），排除 PQC/RSA/ECC/流密码/建模
- 模型：SiliconFlow DeepSeek-V3.2 + thinking 模式，上下文 160K token 硬限
- 使用中文 SCA 领域术语，保持简体中文回答

需审视文件：
- knowledge/extraction/step1_locator.py
- knowledge/extraction/step2_triple_extractor.py
- knowledge/extraction/step3_knowledge_fusion.py
- knowledge/extraction/prompts/step1_{upper,lower}.txt
- knowledge/extraction/prompts/step2_{upper,lower}.txt
- knowledge/extraction/prompts/step3_{upper,lower,cross_layer}.txt
- knowledge/ontology/upper_schema.md（12 节点 / 8 关系）
- knowledge/ontology/lower_schema.md（4 节点 / 3 关系）
- knowledge/sources/knowledge_source_plan.md（源清单）
- knowledge/extraction/extraction_issues.md（已知问题与讨论）

请输出一份 markdown 审视报告，涵盖：

1. 每一步（step1/step2/step3）的架构评估，逐个列出潜在问题，标记严重度（★★★ 阻塞级 / ★★ 重要 / ★ 次要）
2. 三个专项检查：
   (a) 无关知识（out-of-scope）会不会被误抽？当前防护是否足够？如果不够，具体怎么改？
   (b) 超出当前 schema 表达能力的知识如何被记录下来以便迭代 schema？现有机制是否够用？
   (c) 单文档超 160K token 时会怎样？现在有无应对？
3. 全量启动前的必改清单（按阻塞级别排序）
4. 与你预期有差距的地方（如果有）

避免的陷阱：
- 不要提议加过多 schema 扩展节点（此前已决定不加 CodeReference、Dataset 两个节点，只保留 Codex 之前加的 DiagnosticMethod/ValidationMethod/RecoveryMethod）
- 不要提议重写整个架构（手术式改动，只点出问题）
- 如果你发现 Claude 的审视报告（architecture_review_20260420.md）遗漏的问题，显式指出
- 如果你发现 Claude 报告里有错误/过度担忧，显式指出

输出长度：控制在 800-1500 行内，不用太长。
```

---

## 7. 本审视的置信度声明

- 已读：step1/2/3 Python、step1_{upper,lower}、step2_{upper,lower}、step3_{upper,lower,cross_layer}、upper_schema.md、lower_schema.md
- 未验证：phase 11 实际输出 json 是否符合当前 schema 预期
- 审视可能遗漏：代码里某些 edge case / prompt 里某些细节规则

请配合 Codex 的独立审视交叉验证。

---

## 8. 补充审视（读完全部 prompt + schema 之后发现）

### 8.1 Schema vs Prompt 严重不同步 ★★★

**step3_upper.txt 第 6-8 行** 写："The graph contains **9 entity types**: Algorithm, DeviceClass, TraceType, Countermeasure, AttackPoint, LeakageModel, Preprocessing, StatMethod, and **Pipeline**."

**但 schema 实际有 12 个节点**（Codex 2026-04-17 加了 DiagnosticMethod / ValidationMethod / RecoveryMethod）。

**影响**：
- step3 推断新关系时，LLM 被告知只有 9 种节点，不会正确处理新的 3 种节点之间的关系推断
- 可能错把 DiagnosticMethod 当 Preprocessing 混用

**修复（必做）**：step3_upper.txt 开头的 entity types 列表要更新为 12 个节点。这是迫切修复项。

### 8.2 Schema 实际有 4 个 lower 关系，不是 3 个

我之前说 lower 有 3 关系（indicates/resolves/strategy_applies_to）。读完 `lower_schema.md` 发现实际 **4 个关系**：
1. indicates
2. resolves
3. **relates_to**（Action → upper entity）← 我之前漏掉
4. strategy_applies_to

`relates_to` 由 step3_cross_layer.txt 负责生成。这就是 Action 和上层实体的跨层链接。

**连锁影响**：
- `step2_lower.txt` 第 59-60 行只列 **3 个** relationship types（indicates / resolves / strategy_applies_to），**缺 relates_to**
- 但 relates_to 是 step3 阶段由 LLM 根据 cross_layer prompt 生成的，step2 不负责
- 所以 step2 prompt 里不列 relates_to 是合理的设计

**实际 bug 是哪里？** 上层 schema 节点总数和 step3 prompt 的节点数不一致（8.1）。lower 关系分布正常。

### 8.3 truly_unknown 有出口但没有聚合器 ★★

step1 有 `_check_unclassified` 把 truly_unknown 存到 `workspace/<stem>/unclassified_knowledge_{upper,lower}.json`，但：

- **step2 不读它**：step2 只读 step1_upper.json 和 step1_lower.json
- **step3 不读它**：step3 只读所有 step2 输出，做融合
- **结果**：**176 份文档的 truly_unknown 全分散在各自 workspace 下，没有跨文档聚合**

**影响**：超 schema 的知识"记录了但没人看"。每次要改 schema 时，你得手动去每个 workspace 翻 unclassified_knowledge_*.json。

**修复方案**：新增 `step3.5_unclassified_aggregator.py`：
```python
# 扫所有 workspace/*/unclassified_knowledge_{upper,lower}.json
# LLM 做主题聚类
# 输出 workspace/_merged/schema_extension_candidates.md
#   (按主题分组 + 频率统计 + proposed_node_type)
```

### 8.4 `relates_to` 1-to-1 约束太严 ★

step3_cross_layer.txt 第 33 行：`"One Action can relate to at most one entity"`

但实际：
- "use middle trace as reference" 应同时 relates_to `Static Alignment`（参数设置）+ `Smartcard`（设备相关）
- "Apply 2nd-order CPA on masked AES" 应同时 relates_to `CPA`（操作）+ `Masked AES`（对应 Countermeasure）

**修复**：改成 "at most 3 entities"，或干脆去掉上限。

### 8.5 `precedes` 关系被谁生成？★

schema 列了 7 个关系，其中 **precedes** 是跨 pipeline 的通用规则（如"filtering 一般在 alignment 之前"）。

但：
- step2_upper.txt 的关系列表列出 precedes（第 49 行：`precedes: step-method -> step-method`）
- step3_upper.txt 也有 precedes 的推断示例

**问题**：precedes 的抽取来源不清。从单份文档里抽？还是 step3 跨文档推断？

**风险**：两边都可能抽到冲突的 precedes（比如一篇文章说"先 alignment 再 filter"，另一篇说反了），step3 去重时没有冲突裁决策略。

**建议**：
- precedes 主要在 step3 推断（标记 `is_mandatory: false`）
- step2 只在文档明确写"先 X 再 Y"时才生成 precedes
- step3 合并时，同对节点的冲突 precedes 用 **多数投票 + is_mandatory 降级** 裁决

### 8.6 `consists_of` 的 category 字典必须与 schema 对齐 ★

step2_upper.txt 第 54-59 行的 category → 节点类型映射：
```
{denoising, alignment, compression, dimensionality_reduction, poi_selection} → Preprocessing
{attack} → StatMethod
{quality_assessment, implementation_judgment, region_localization, branch_decision} → DiagnosticMethod
{verification} → ValidationMethod
{recovery} → RecoveryMethod
```

这个映射是**硬编码在 prompt 里**的。如果 schema 加新 Preprocessing category（比如 `signal_enhancement`），prompt 也要改。

**建议**：在 step2 代码里把这个映射做成配置文件（YAML），prompt 用 `{category_map}` 占位，代码动态填充。这样 schema 改一次，prompt 自动更新。当前不紧迫，但迭代时要注意。

### 8.7 step3_lower 故意不处理 Strategy — 代码必须先 split 再 merge ★

step3_lower.txt 第 7 行：`"Strategy nodes are handled OUTSIDE this prompt"`。

意味着 step3 的代码必须：
1. 从合并后的 lower JSON **剥离** strategies 和 strategy_applies_to
2. 把只剩 triples 的 JSON 送 LLM 清洗
3. LLM 返回 triples 后，代码**把 strategies 塞回去**

**需要验证**：`step3_knowledge_fusion.py` 是否真的这么做了？如果没做，会把 Strategy 喂给一个不处理它的 prompt，行为未定义。

**建议**：读 `step3_knowledge_fusion.py` 的 lower 处理函数确认。（我上面没完整读这部分代码）

### 8.8 Pipeline 节点里 "8 Steps" 固定名 ★★

step1_upper.txt 的 canonical_pipeline 例子（第 158 行）写死 `"Unified Analysis Process (8 Steps)"`。ENTITY_NAME_MAPPING 也把 Flow A/B 都映射到它。

**但**：如果未来你加新 canonical pipeline（如 "Masked AES Analysis Flow"），prompt 例子还是用 "8 Steps" 这个特例，**LLM 可能把所有 pipeline 都叫这个名字**。

**建议**：
- step1 prompt 的例子换成更中性的 placeholder（`"<Pipeline Name from Source>"`）
- 保留 "Unified Analysis Process (8 Steps)" 作为默认 fallback

---

## 9. 清单补丁（补充 5-8 节发现后）

### 阻塞级加 1 条
- [ ] **修 step3_upper.txt 的 entity types 从 9 更新到 12**（加 DiagnosticMethod/ValidationMethod/RecoveryMethod 到关系推断规则里）

### 重要加 2 条
- [ ] 新增 step3.5 聚合 truly_unknown 到 schema extension 候选文档
- [ ] 验证 step3 代码是否真的把 Strategy/strategy_applies_to 剥离再喂 LLM

### 次要加 2 条
- [ ] relates_to 改为 at most 3 entities
- [ ] step1 canonical_pipeline 例子换中性 placeholder
- [ ] precedes 冲突裁决策略（多数投票 + is_mandatory 降级）

---

## 10. 严重度重排（读完全部后）

| 严重度 | 问题 | 位置 |
|-------|------|------|
| ★★★ | step1 硬编码文件列表 | step1_locator.py |
| ★★★ | MAN-07/BOOK-01/MAN-08 超窗口无切块 | step1_locator.py |
| ★★★ | Scope Filter 缺失 | step1_{upper,lower}.txt |
| ★★★ | **step3_upper entity types 9 vs schema 12** | step3_upper.txt |
| ★★ | truly_unknown 没聚合 | 缺 step3.5 |
| ★★ | Strategy 剥离/回填待验证 | step3_knowledge_fusion.py |
| ★★ | 4 新 upper 节点边界辨析 | step2_upper.txt |
| ★★ | Step3 合并禁止清单 | step3_upper.txt |
| ★★ | Inference Rules 激进 | step2_upper.txt |
| ★★ | works_with confidence 公式不透明 | step3 代码 |
| ★ | relates_to 1-to-1 约束 | step3_cross_layer.txt |
| ★ | precedes 冲突裁决 | step3_upper.txt |
| ★ | ID 冲突 | step1 |
| ★ | token usage 日志缺 | 3 个 step |
| ★ | canonical_pipeline 例子固定名 | step1_upper.txt |

---

## 11. 合并 Codex 独立审视（2026-04-20 01:27）

Codex 的审视报告见 `knowledge/codex_reports/审视报告_20260420_抽取架构.md`。两份报告**主矛盾判断一致**（架构对，工程缺口多），但 Codex 有 4 处 Claude 遗漏、2 处纠正 Claude 的误判。

### 11.1 Codex 补充的 Claude 遗漏

**补充 A：Step 2 / Step 3 入口也是硬编码 ★★★**

Claude 只指出 step1_locator.py 的 input_files 硬编码，**漏了 step2_triple_extractor.py 和 step3_knowledge_fusion.py 的 main() 同样硬编码旧 6 workspace**。

→ 全量启动前三个 main() 都要改成动态扫描。

**补充 B：不止 step3_upper，step1_lower 也残留旧 9 类 upper entity ★★**

Claude 只指出 step3_upper.txt "9 entity types" 过时。**实际上 step1_lower.txt 的 Two-Layer Pipeline Context 段也只列 9 类**，没有 DiagnosticMethod / ValidationMethod / RecoveryMethod。

→ step1_lower.txt 也要同步更新。

**补充 C：step2_lower.txt 的 strategy_applies_to 目标类型未补齐 ★★**

Claude 没检查 step2_lower 关系类型列表。**step2_lower.txt 的 strategy_applies_to 允许目标只列了 7 类上层节点**（Algorithm / DeviceClass / AttackPoint / LeakageModel / Preprocessing / StatMethod / Pipeline），**缺 DiagnosticMethod / ValidationMethod / RecoveryMethod**。

→ step2_lower.txt 和 lower_schema.md 的 strategy_applies_to 方向说明都要补齐。

**补充 D：缺 retry/backoff + usage 日志在三个 step 都存在 ★★**

Claude 只提了 token usage 日志，Codex 指出**三个 step 都没有 retry/backoff** —— 176 份跑几十小时，中途遇 429/503/timeout 会直接中断不续跑。

→ 所有 call_llm 统一加：
```python
# 指数退避重试（复用 agent/main.py 已有策略）
# + 记录 response.usage.prompt_tokens / completion_tokens / finish_reason
```

### 11.2 Codex 纠正 Claude 误判

**纠正 A：step3 代码已正确 split/restore Strategy**

Claude 在 8.7 节担心"step3_lower.txt 声称 Strategy outside this prompt，但代码是否真剥离？"。

Codex 确认：**step3_knowledge_fusion.py 已经显式做了 split → LLM 清洗 triples → 把 strategies/strategy_applies_to 恢复回去**。

→ 不是 bug，删除这条"待验证"项。

**纠正 B：lower schema 关系数无 bug**

Claude 先前一度说"lower 只 3 关系（漏 relates_to）"，后来自己订正为 4 关系。Codex 直接确认：**lower_schema.md 实际 4 关系** (indicates/resolves/relates_to/strategy_applies_to)，**step2_lower.txt 只列 3 关系是合理设计**（relates_to 由 step3_cross_layer 生成，不归 step2 管）。

→ 这不是 bug，是职责分工。

### 11.3 整合后的最终必改清单

**★★★ 阻塞级（合并后 7 条）**

1. step1_locator.py 扫 extracted/*.md，去掉硬编码 6 文档
2. step2_triple_extractor.py 扫 workspace/*/step1_*.json，去掉硬编码 6 workspace
3. step3_knowledge_fusion.py 扫 workspace/*/step2_*.json，去掉硬编码 6 workspace
4. Step1 加入 section-aware chunking（`##` 切分 + token 兜底）→ 解决 MAN-07 28.5 万 token 问题
5. step1_upper.txt + step1_lower.txt 加硬 Scope Lock 段（显式排除 RSA/ECC/PQC/stream/AEAD/profiled/DL/fault）
6. step2 或 step3 代码层加 scope post-filter 白名单（双保险）
7. step3_upper.txt entity types 9→12 同步；consists_of 目标类型补齐 4 种新节点

**★★ 重要级（合并后 9 条）**

8. step1_lower.txt upper entity 列表 9→12
9. step2_lower.txt strategy_applies_to 目标类型补齐 3 种新节点
10. lower_schema.md 跨层目标示例文本同步到 12 节点边界
11. 三个 step 的 call_llm 统一补 **retry/backoff + usage/finish_reason 日志**
12. step2_upper.txt 加 4 种新节点（Pipeline/Diag/Val/Recovery）边界辨析规则
13. step3_upper.txt 加合并禁止清单（防 Static vs Vertical Alignment 误合并）
14. step3_cross_layer.txt 放宽 relates_to 1-to-1 为最多 3 个
15. works_with confidence 公式显式写进 step3 prompt
16. 新增 step3.5_unclassified_aggregator.py 做 truly_unknown 跨文档聚合

**★ 次要级（可全量后优化）**

17. step2_upper.txt 推理规则加 guard（仅显式支持才推断）
18. step1 ID 加文档前缀避免冲突
19. step1 canonical_pipeline 例子换中性 placeholder
20. precedes 冲突裁决策略
21. `_check_unclassified` 已有的 `truly_unknown` 条目加 `proposed_node_type` 结构化字段

### 11.4 删除项（Codex 纠正后不再是问题）

- ~~step3 代码是否真 split Strategy 需要验证~~ → 确认已正确实现
- ~~lower schema 关系数不同步~~ → 没这回事

---

## 12. 下一步

**推荐执行顺序：**

1. **先修阻塞级 7 条**（1-2 天工作量）
2. **smoke test**：在 expert_experience.md + MAN-01 + 1 份 PAP 各跑一遍，对比 phase 11 baseline
3. **重要级 8-16 起步 → 按优先级批量补**（3-5 天）
4. **全量启动** 176 份（预估 50-60 小时 thinking 模式）
5. 跑完后做 step3.5 truly_unknown 聚合，看 schema 是否需要迭代

**要我现在就开始做阻塞级修复吗？** 改动清单我心里有谱，可以直接动手。

或者你想先 commit + push 两份审视报告给版本记录留痕，再开始改？
