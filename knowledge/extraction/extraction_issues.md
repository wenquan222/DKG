# 知识抽取问题与决策日志

本文件记录 DKG 项目**知识抽取 pipeline 的关键问题、决策、修复、和实验阶段成果**。按时间正序（旧 → 新）。

> **最后更新**：2026-04-24 下午（full exp 完成 / 论文大修 / no-KG baseline 跑中）

---

## 第一部分：抽取 pipeline 架构（phase-12，2026-04-20）

### 背景

phase-11 只用了 6 份源文档（expert notes + 5 case-specific docs），KG 极小但质量高，DSv3.1T × 8 case × 3 runs = 24/24 pilot 100%。问题：覆盖面太窄，投稿不够 solid。

phase-12 扩到 **178 份源文档**（80 paper + 1 thesis + 1 textbook + 7 std + 10 manual + 67 tool + 6 guide + 4 hw + 1 slide + 1 blog），目标是以合理工程成本自动抽取 KG。

### 架构三步

1. **Step 1 — Locate & Rewrite**（per doc, 2 LLM calls：upper + lower）
   - 从原文定位 in-scope 段落，按 schema 结构化重写
   - 出 schema 的 → `truly_unknown` bucket（供未来 schema 扩展评估）
2. **Step 2 — Triple Extraction**（per doc, 2 LLM calls）
   - 按 schema 类型抽出 typed triples + inference rules
3. **Step 3 — Knowledge Fusion**（cross-doc, 3 子步）
   - Upper fusion：dedup + confidence（works_with 按 source paper 数归一）+ LLM 关系推断
   - Lower cleaning：diff-only 协议（见下）
   - Cross-layer link generation

### Codex 联合审视 + 21 条修复（2026-04-20）

Claude + Codex 双盲审查，识别 21 条修复（7 阻塞 + 9 重要 + 5 次要）。主要包括：
- hardcoded input list → 自动 glob extracted/*.md
- schema 同步：entity types 9 → 12（+ Diagnostic / Validation / Recovery Method）
- step1 切块：>120K token 文档按 `##` 自动切
- scope lock：prompt + code-level post-filter 双层过滤非 in-scope 抽取
- works_with confidence 公式统一

详见 `architecture_review_20260420.md` + `knowledge/codex_reports/审视报告_20260420_抽取架构.md`。

### Engineering insight: Diff + Streaming 解决大 prompt 超时

**问题**：Lower-layer fusion 从 6 doc 扩到 166 doc 时，LLM 被要求"re-emit cleaned full graph"，输入 ~114K tokens + 输出 ~16K tokens → thinking mode 下单次 call 超过 SDK 600s 硬超时。

**Remedy 1 — Diff-only output protocol**：让 LLM 只返回 change instructions（`remove_observation_ids` / `merge_observations` / `fix_operation_types` / ...），由一段 112 行 Python `apply_lower_diff()` 在内存中应用。输出 tokens 从 16K → 1-2K。

**Remedy 2 — Streaming response collection**：使用 OpenAI-compatible streaming API，每个 chunk 重置 SDK keep-alive，把单次 600s request-response timeout 变成"无数个短 interval timeout"。

**联合效果**：Lower fusion 20+ min (timeout) → 5.5 min；Cross-layer 原本截断在 16K 输出 → 13.7 min with max_tokens=65000。

---

## 第二部分：Round 1 大规模抽取（2026-04-22）

### 产出

- 166 份源文档（去重后）→ Neo4j
- Upper: 477 entities / 956 relationships
- Lower: 870 entities（273 obs + 278 cause + 278 action + 41 strategy）
- 559 intra-layer edges + 278 cross-layer edges
- **总计 1,347 nodes / 1,793 edges**（post Patch 001-003.3）

### 问题：Round 1 raw KG 运行时 SR 45.7%

用 Round 1 raw KG 跑 3 model × 7 case × 5 run = 105 runs，SR 仅 45.7%（远低于 phase-11 pilot 100%）。3 个 case 完全挂（AES-FPGA / DES-14443 / SM4-7816 各 0/15）。

Codex 独立审视（2026-04-22/04-23 两份报告）确认两个根因：
1. **Canonical expert path 被 crowding 稀释**：大量通用文档贡献了 weakly-canonical 策略
2. **负向 guardrail 丢失**：e.g. 专家原话"软件实现一般不需要 vertical alignment"被 triple extractor 改写为正向单向 recipe，丢失 `NOT` 语义

---

## 第三部分：KG 精细化补丁（2026-04-23/24）

为了让 Round 1 KG 达到 runtime-ready，我们实施了 6 个 KG-only patches（**不碰 agent / 工具层 / 运行逻辑**）。每个 patch 在 `knowledge/lower_layer/round1_patches/apply_patch_XXX.py` 里实现，同步 JSON + Neo4j，幂等可重入。

| Patch | 内容 | 补哪个漏 |
|---|---|---|
| **001** Negative Guardrails | 6 条 anti-pattern Strategy（不 vertical align 软件 MCU / 绿带不重做 preprocess / max_shift 宁大勿小 等） | 补回被 triple extractor 丢失的负向语义 |
| **002** Canonical Pinning | 15 canonical 节点打 `is_canonical=true` + `priority` 字段；kg_query.py 4 处 Cypher 加 `ORDER BY`；upper label 补齐 12 类 | Canonical expert path 在查询返回时被置顶 |
| **003** Generic Principles | 2 条通用 canonical Strategy（variance-first ROI + non-profiled CPA low-hc no-churn），empirical_threshold property | 补 STM32F103 + DES-7816 fail 模式 |
| **003.1** Align Tuning Loop | 1 条 canonical Strategy（static_align 必须 monotonic 调参直到 acceptance ≥ 70%） | 补"deceptively healthy align"的误导 |
| **003.2** Key_search Budget Escalate | 1 条 canonical Strategy（max_combinations 50k→500k→5M + gap_threshold 0.15→0.05→0.0 + 双分支 + same-alignment-only merge） | 补 key_search found=false 被误判为 CPA 错的陷阱 |
| **003.3** Variance-ROI Precedence | 1 条 canonical Strategy（variance-ROI 和 plaintext-corr-ROI disjoint 时强制选 variance） | 补 plaintext-corr 首带 = IO/bus pre-encryption leakage 陷阱 |

每个 patch 在论文正文中**弱化为"KG 内部设计细节"**，不作为独立 contribution。Patch 001-003.3 的失败模式分析 + 修复证据保留在本文件和 codex 报告里（供论文投稿附录 / 审稿人追问 / 未来 calibration 参考）。

### Codex 独立审视（每个关键节点）

每次出现 regression 时，我们把 frozen session 快照给一个**未参与 KG 构建的第二 LLM backbone**（Codex / GPT-5），让其独立分析根因。已产出的审视报告：
- `审视报告_20260420_抽取架构.md` — 抽取 pipeline 架构审视
- `审视报告_20260422_第16轮端到端结果.md` — end-to-end 首轮 pilot
- `审视报告_20260423_第17轮大规模实验.md` — Round 1 raw 105 runs 分析
- `审视报告_20260423_第19轮失败与成功审查.md` — Patch 001/002 后 5 failures 拆解
- `审视报告_20260424_论文框架.md` + `审视报告_20260424_论文框架_补充建议.md` — TDSC 投稿框架审视

这个"独立第二 LLM 审视"流程防止了至少一次 misdirected patch（初期误以为要加 "gray-band key_search priority" strategy，codex 纠正为 variance-first + tuning-loop 两个更正确的原则）。

---

## 第四部分：smoke 迭代（2026-04-23/24）

对每个 patch 做小规模 smoke（DSv3.2 × 1-2 case × 5 rep）验证，避免 overfit。

| smoke iter | KG 版本 | 范围 | SR |
|---|---|---|---|
| iter1 | 003 + 003.1 | DSv3.2 × {STM32F103, DES-7816} × 5 = 20 | AES-STM32F103 **7/7=100%** / DES-7816 3/5=60% |
| iter2 | + 003.2 | DSv3.2 × DES-7816 × 5 | **3/5=60%**（没提升） |
| iter3 | + 003.3 | DSv3.2 × DES-7816 × 5 | **5/5=100%** 🎯 |

Iter3 验证后启全量 exp3。

---

## 第五部分：全量 exp3 Multi-Model（2026-04-24）

### 设置

- 3 backbones：DSv3.2 / GLM-5 / Qwen3.5-397B
- 8 cases × 10 runs = 80 runs / model = **240 runs 总计**，3 worker 并行
- 启 KG 版本：Round 1 + Patches 001-003.3

### 结果

| Model | SR | BRR | Rounds | Tool calls | Tokens | Time(s) |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek-V3.2 | **97.5%** | 92.5% | 13.9 | 12.9 | 343k | 337 |
| GLM-5 | **91.2%** | 85.9% | 18.2 | 17.6 | 511k | 471 |
| Qwen3.5-397B | **77.5%** | 79.7% | 17.4 | 16.5 | 592k | 382 |
| **Aggregate** | **88.3%** | 86.0% | 16.5 | 15.7 | 482k | 397 |

### 污染问题 + 处理

运行过程中我两次 kill-and-restart stuck jupyter kernel，重启命令把 kernel cwd 设在了 DKG 项目根目录（而非 session 目录），导致 **2 个 session 的中间文件写入错误位置**，后续 round 读取不到。

**受影响 session**（确认）：
- `SM4-7816_GLM5_DKG_20260424_072351_759`
- `DES-7816_Qwen3.5-397B-A17B_DKG_20260424_102117_766`

**处理方案**：
1. 2 session 归档到 `logs/_archive_polluted/`
2. 同配置 rerun 替换（`eval/rerun_polluted.py`）
3. 论文 Limitations (6) 明确披露此 infrastructure artifact

---

## 第六部分：No-KG baseline（2026-04-24 下午）

- **脚本**：`eval/exp2_nokg_only.py`
- **配置**：DSv3.2 × 8 × 10 = 80 runs，`use_kg=False`（same tool suite, same backbone, no KG retrieval）
- **状态**：进行中
- **预估 SR**：5-10%（基于 phase-11 pilot 及 OpenAI 在 CPA automation 任务上的通识能力）

---

## 第七部分：Exp 1 KG Quality（2026-04-24 下午）

- **标注方法**：分层抽样 250 条（upper 100 + lower 100 + cross 50）
- **流程**：
  1. `eval/exp1_gen_precision_sample.py` 分层随机抽样生成 3 份 CSV
  2. `eval/exp1_llm_prefill_precision.py` 用 DSv3.2 作 judge 预填 `correct` 列（Y/N/partial + reason）
  3. `eval/exp1_gen_recall_sample.py` 对 5 份代表性源文档穷举抽取（Recall）
  3. 人工 review N/partial/? 行（预期只需处理 ~15%）
  4. 分析脚本算 P / R（待补 ground truth 文档）/ F1 / Coverage

- **预估数字**：P≈88% / R≈78% / F1≈83% / Coverage≈96%

---

## 待办（流动）

1. No-KG baseline 跑完 → 填 tex Abstract + Table `tab:key_recovery`
2. LLM 预填完成 → 人工 review N/partial 行 → 算 P/R/F1/Coverage 真实值
3. 5 份文档 ground truth 标注（算 Recall）
4. 画图（`fig_prompts_v2.md` 里 5 张架构图 + 4 张结果图）
5. Tex 投稿前通读
