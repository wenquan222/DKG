"""
DKG Step 3: 知识融合 (Knowledge Fusion)

跨文档处理：读取所有Step 2输出，执行标准化、去重、关系推断、冲突检测。
上层：代码标准化+去重+LLM推断新关系+代码算confidence
下层：合并+LLM过滤清洗+代码完整性检查
"""

import json
import os
import re
import glob
from pathlib import Path
from collections import defaultdict
from openai import OpenAI
import yaml


# ==================== 配置读取 ====================

def load_config():
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


# ==================== LLM 调用 ====================

from llm_utils import call_llm_with_retry, scope_filter_upper


def call_llm(content: str, prompt_path: str, client: OpenAI, model: str,
             enable_thinking: bool = False, stream: bool = False) -> dict:
    """retry/backoff + usage 日志。stream=True 时走流式接收，绕开大响应 SDK 600s timeout"""
    prompt_template = Path(prompt_path).read_text(encoding="utf-8")
    prompt = prompt_template.replace("{content}", content)

    print(f"  Calling LLM ({model}) thinking={'on' if enable_thinking else 'OFF'} stream={stream}...")
    text, _meta = call_llm_with_retry(
        client=client, model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1, max_tokens=16000,
        thinking_budget=16000 if enable_thinking else 0,
        enable_thinking=enable_thinking,
        stream=stream,
    )

    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    return json.loads(text)


# ==================== 上层：代码处理函数 ====================

# 实体名标准化映射表
ENTITY_NAME_MAPPING = {
    # AttackPoint 标准化：统一去掉轮次信息（round 存在单独属性里）
    # 2026-04 修订：name 不再嵌入 round，"S-box Output (first round)" → "S-box Output"
    "S-box Output (first round)": "S-box Output",
    "S-box Output (last round)": "S-box Output",
    "S-box Input (first round)": "S-box Input",
    "S-box Input (last round)": "S-box Input",
    "AddRoundKey Output (first round)": "AddRoundKey Output",
    "Flow A": "Unified Analysis Process (8 Steps)",
    "Flow B": "Unified Analysis Process (8 Steps)",
    "流程A": "Unified Analysis Process (8 Steps)",
    "流程B": "Unified Analysis Process (8 Steps)",
    "Unified Analysis Process": "Unified Analysis Process (8 Steps)",
    "统一分析流程": "Unified Analysis Process (8 Steps)",
    # TraceType 标准化
    "Electromagnetic": "EM",
    # DeviceClass category 标准化
    "Microcontroller": "MCU",
}

# 需要在properties里也标准化的字段
CATEGORY_MAPPING = {
    "Microcontroller": "MCU",
}


def standardize_entity_names(entities: list, relationships: list) -> tuple[list, list]:
    """标准化实体名称，同时更新关系中的引用"""

    # 构建重命名映射
    rename_map = {}
    for entity in entities:
        old_name = entity["name"]
        new_name = ENTITY_NAME_MAPPING.get(old_name, old_name)
        if old_name != new_name:
            rename_map[old_name] = new_name
            entity["name"] = new_name
            print(f"    Renamed: '{old_name}' → '{new_name}'")

        # 标准化category属性
        props = entity.get("properties", {})
        if "category" in props and props["category"] in CATEGORY_MAPPING:
            old_cat = props["category"]
            props["category"] = CATEGORY_MAPPING[old_cat]
            print(f"    Category: '{old_cat}' → '{props['category']}'")

    # 更新关系中的引用
    for rel in relationships:
        if rel["subject"] in rename_map:
            rel["subject"] = rename_map[rel["subject"]]
        if rel["object"] in rename_map:
            rel["object"] = rename_map[rel["object"]]

    return entities, relationships


def remove_invalid_relationships(entities: list, relationships: list) -> list:
    """
    删除语义错误的关系。与旧版相比，改用 entity type 做严格判断（而不是字符串匹配）。

    规则：
    1. 同类型单选节点之间不应该有 works_with：
       - AttackPoint ↔ AttackPoint（不同攻击点不是协作关系）
       - LeakageModel ↔ LeakageModel（HW 和 HD 是 alternative_to，不是 works_with）
       - TraceType ↔ TraceType（Power 和 EM 同理）
       - Algorithm ↔ Algorithm（不同算法之间不协作）
    2. Countermeasure 为 "none" 时不应该有 weakens 关系
    3. Pipeline 不应该参与 works_with（按 Step2 prompt 设计，canonical_pipeline 不贡献 confidence）
    4. consists_of 的 subject 必须是 Pipeline；object 应该是合法的上层 step-method 类型
       （Preprocessing / StatMethod / DiagnosticMethod / ValidationMethod / RecoveryMethod）
    """
    # 建 name → type 映射（name 可能重复但不同 type 很少见，取第一个）
    name_to_type: dict[str, str] = {}
    for e in entities:
        name = e.get("name", "")
        if name and name not in name_to_type:
            name_to_type[name] = e.get("type", "")

    # 同类型不应该有 works_with 的类型集合
    SINGLE_CHOICE_TYPES = {"AttackPoint", "LeakageModel", "TraceType", "Algorithm"}

    valid = []
    removed_count = 0
    warnings = []

    for rel in relationships:
        relation = rel.get("relation", "")
        subj = rel.get("subject", "")
        obj = rel.get("object", "")
        subj_type = name_to_type.get(subj, "")
        obj_type = name_to_type.get(obj, "")

        # 规则 1：同类型单选节点间的 works_with 不合法
        if relation == "works_with":
            if subj_type and subj_type == obj_type and subj_type in SINGLE_CHOICE_TYPES:
                removed_count += 1
                warnings.append(f"      dropped {subj_type} ↔ {subj_type}: {subj} works_with {obj}")
                continue
            # Pipeline 不应参与 works_with
            if subj_type == "Pipeline" or obj_type == "Pipeline":
                removed_count += 1
                warnings.append(f"      dropped Pipeline works_with: {subj} works_with {obj}")
                continue

        # 规则 2：Countermeasure 为 "none" 时不应该有 weakens 关系
        if relation == "weakens" and subj == "none":
            removed_count += 1
            warnings.append(f"      dropped weakens from 'none': {subj} weakens {obj}")
            continue

        # 规则 3：consists_of 的 subject 必须是 Pipeline
        if relation == "consists_of":
            if subj_type and subj_type != "Pipeline":
                removed_count += 1
                warnings.append(f"      dropped consists_of with non-Pipeline subject: {subj_type} {subj}")
                continue
            # object 不是合法 step-method 类型时保留但打 warning
            if obj_type and obj_type not in ("Preprocessing", "StatMethod", "DiagnosticMethod", "ValidationMethod", "RecoveryMethod"):
                warnings.append(f"      WARNING: consists_of target is {obj_type} (not a valid step-method type): {subj} → {obj}")

        valid.append(rel)

    if removed_count > 0:
        print(f"    Removed {removed_count} invalid relationships")
        for w in warnings[:20]:  # 最多打印 20 条
            print(w)
        if len(warnings) > 20:
            print(f"      ... and {len(warnings) - 20} more")
    elif warnings:
        # 没删任何关系，但有 warning
        for w in warnings[:10]:
            print(w)

    return valid


def get_dedup_key(entity: dict) -> tuple:
    """
    根据节点类型生成不同的去重key。
    不同属性组合代表不同的实体，不能合并。

    - Algorithm: name + key_length（AES-128 和 AES-256 是不同实体）
    - DeviceClass: name（每个设备型号是独立实体）
    - TraceType: name（Power 和 EM 是不同实体）
    - Countermeasure: name（每种防护是独立实体）
    - AttackPoint: name + round（S-box Output first round 和 last round 是不同实体）
    - LeakageModel: name（HW 和 HD 是不同实体）
    - Preprocessing: name（每种预处理方法是独立实体）
    - StatMethod: name（CPA 和 2nd-order CPA 是不同实体）
    - DiagnosticMethod: name（每种判断/定位方法是独立实体）
    - ValidationMethod: name（每种验证方法是独立实体）
    - RecoveryMethod: name（每种恢复/搜索方法是独立实体）
    - Pipeline: name（旧 Flow A/B 等历史标签先标准化到当前统一流程名，再按同名合并）
    """
    entity_type = entity.get("type", "")
    name = entity.get("name", "")
    props = entity.get("properties", {})

    if entity_type == "Algorithm":
        # AES-128 ≠ AES-256
        key_length = props.get("key_length", "")
        return (entity_type, name, key_length)

    elif entity_type == "AttackPoint":
        # S-box Output (first round) ≠ S-box Output (last round)
        round_val = props.get("round", "")
        return (entity_type, name, round_val)

    elif entity_type == "StatMethod":
        # CPA ≠ 2nd-order CPA (already different by name)
        # But also distinguish non_profiled CPA from profiled CPA if same name
        method_type = props.get("type", "")
        return (entity_type, name, method_type)

    elif entity_type == "Pipeline":
        # 同名 Pipeline 合并。旧 Flow A/B 等历史标签会先标准化到统一流程名。
        # trigger_condition 差异不足以划分不同实体：同一个方法论，更像是描述角度略有不同
        return (entity_type, name)

    else:
        # DeviceClass, TraceType, Countermeasure, LeakageModel, Preprocessing
        # name 足够区分
        return (entity_type, name)


def deduplicate_entities(entities: list) -> list:
    """实体去重：根据节点类型使用不同的去重key，属性取并集"""
    seen = {}
    for entity in entities:
        key = get_dedup_key(entity)
        if key in seen:
            # 合并属性：新值补充旧值中的null
            existing_props = seen[key].get("properties", {})
            new_props = entity.get("properties", {})
            for k, v in new_props.items():
                if v is not None and (k not in existing_props or existing_props[k] is None):
                    existing_props[k] = v
            seen[key]["properties"] = existing_props
        else:
            seen[key] = entity

    deduped = list(seen.values())
    print(f"    Entities: {len(entities)} → {len(deduped)} (deduped)")
    return deduped


# confidence 饱和点：达到多少独立文档来源算 100% confidence
# 5 的含义：5 个独立实验都观察到同一组件组合成功，几乎可以确信这是稳定可用的配置
CONFIDENCE_SATURATION = 5.0


def deduplicate_relationships(relationships: list) -> list:
    """
    关系去重 + 计算 confidence。

    Confidence 的计算基于**独立文档来源数量**（unique_papers），不是简单的重复计数。
    理由：
    - 同一个文档如果被 LLM 多次抽取到同一关系，只算 1 个独立来源
    - 5 个独立文档都观察到 → confidence = 1.0（饱和）
    - 1 个文档 → confidence = 0.2
    - 0 个（infer 出来的） → support_count 取 1（保底），confidence = 0.2

    inferred 关系：如果 relationship 已经有 "inferred": True 标记，confidence 降低到 max(0.5, 原值)
    """
    groups = defaultdict(list)

    for rel in relationships:
        props = rel.get("properties", {})
        if rel["relation"] == "consists_of":
            key = (rel["subject"], rel["relation"], rel["object"], props.get("step_order"))
        else:
            key = (rel["subject"], rel["relation"], rel["object"])
        groups[key].append(rel)

    merged = []
    for key, rels in groups.items():
        # consists_of 用 4-tuple (含 step_order)，其他用 3-tuple
        subj, relation, obj = key[0], key[1], key[2]
        # 收集所有来源
        all_papers = []
        all_texts = []
        has_inferred = False
        for r in rels:
            props = r.get("properties", {})
            papers = props.get("source_papers", [])
            if isinstance(papers, list):
                all_papers.extend(papers)
            text = props.get("source_text", "")
            if text and text not in all_texts:
                all_texts.append(text)
            if props.get("inferred"):
                has_inferred = True

        # 独立文档来源去重
        unique_papers = sorted(set(p for p in all_papers if p))
        # support_count 以独立文档数为准，保底 1
        support_count = max(len(unique_papers), 1)

        # 计算 confidence
        confidence = min(support_count / CONFIDENCE_SATURATION, 1.0)
        # inferred 关系 confidence 上限降到 0.5（即使独立来源再多也只算中等置信）
        if has_inferred and confidence > 0.5:
            confidence = 0.5

        # 取第一条关系的属性作为基础，更新 confidence 和来源
        merged_rel = rels[0].copy()
        merged_rel["properties"] = merged_rel.get("properties", {}).copy()
        merged_rel["properties"]["confidence"] = round(confidence, 2)
        merged_rel["properties"]["support_count"] = support_count
        merged_rel["properties"]["source_papers"] = unique_papers
        if has_inferred:
            merged_rel["properties"]["inferred"] = True
        if all_texts:
            merged_rel["properties"]["source_text"] = all_texts[0]  # 保留第一条

        merged.append(merged_rel)

    print(f"    Relationships: {len(relationships)} → {len(merged)} (deduped)")
    return merged


def detect_conflicts(relationships: list) -> list:
    """检测矛盾关系"""
    conflicts = []

    # 检查同一对实体是否同时有正面和负面关系
    positive = {}  # works_with
    negative = {}  # incompatible (如果有的话)

    for rel in relationships:
        key = (rel["subject"], rel["object"])
        key_reverse = (rel["object"], rel["subject"])

        if rel["relation"] == "works_with":
            positive[key] = rel
            positive[key_reverse] = rel

    # 目前没有显式的incompatible_with关系，暂时只检查works_with的confidence冲突
    # 未来可以扩展

    return conflicts


def remove_placeholder_entities(entities: list, relationships: list) -> tuple[list, list]:
    """
    删除占位符实体和相关的边。

    当前 schema 下唯一的占位符是 Countermeasure 为 "none" 的实体——它代表"没有防护措施"，
    是 Step1/Step2 为了填 schema 强制字段而产生的虚节点。Step3 的 remove_invalid_relationships
    已经删掉了从 "none" 出发的 weakens 边，这个节点就变成了孤立节点，不应该保留在最终 KG 里。

    未来如果有其他占位符（比如 Algorithm 为 "unknown"），可以在这里扩展。
    """
    PLACEHOLDERS = {
        ("Countermeasure", "none"),
    }

    placeholder_names = set()
    kept_entities = []
    for e in entities:
        key = (e.get("type", ""), e.get("name", ""))
        if key in PLACEHOLDERS:
            placeholder_names.add(e.get("name", ""))
            continue
        kept_entities.append(e)

    # 删除和占位符相关的所有边（subject 或 object 是占位符名字）
    kept_rels = [
        r for r in relationships
        if r.get("subject") not in placeholder_names
        and r.get("object") not in placeholder_names
    ]

    n_removed_entities = len(entities) - len(kept_entities)
    n_removed_rels = len(relationships) - len(kept_rels)
    if n_removed_entities > 0:
        print(f"    Removed {n_removed_entities} placeholder entities: {placeholder_names}")
    if n_removed_rels > 0:
        print(f"    Removed {n_removed_rels} relationships involving placeholders")

    return kept_entities, kept_rels


def check_completeness(entities: list, relationships: list) -> list:
    """检查孤立实体（没有任何关系的实体）"""
    entity_names = {e["name"] for e in entities}
    connected = set()

    for rel in relationships:
        connected.add(rel["subject"])
        connected.add(rel["object"])

    orphans = entity_names - connected
    if orphans:
        print(f"    Orphan entities (no relationships): {orphans}")

    return list(orphans)


def apply_lower_diff(merged: dict, diff: dict) -> dict:
    """
    把 LLM 返回的 diff（见 prompt_lower.txt Output Format）应用到 merged lower 数据。
    支持 4 种变更：
      1) remove_observation_ids / remove_cause_names / remove_action_names: 删节点 + 级联删相关关系
      2) fix_operation_types: 修正 action.operation 字段
      3) merge_observations: 把 duplicate_observation 删掉，它们的 indicates/resolves 边重定向到 keep_observation
      4) completeness_warnings: 仅 print，不自动改

    返回 patch 后的 merged（原地修改 + return 方便链式）。
    """
    # ---- 1) 合并 observations：先做 merge（会生成 ID 重定向映射，供后续 remove 使用）----
    obs_id_remap: dict[str, str] = {}
    merges = diff.get("merge_observations") or []
    for m in merges:
        keep_id = m.get("keep_observation_id")
        dup_ids = m.get("duplicate_observation_ids") or []
        if not keep_id or not dup_ids:
            continue
        for dup_id in dup_ids:
            obs_id_remap[dup_id] = keep_id
    if obs_id_remap:
        print(f"    merge_observations: 合并 {len(obs_id_remap)} 条重复 obs 到 {len(merges)} 条保留 obs")

    # ---- 2) 收集要删除的集合 ----
    remove_obs_ids = set(diff.get("remove_observation_ids") or []) | set(obs_id_remap.keys())
    remove_cause_names = set(diff.get("remove_cause_names") or [])
    remove_action_names = set(diff.get("remove_action_names") or [])

    # ---- 3) 过滤 observations / causes / actions ----
    before_o = len(merged.get("observations", []))
    merged["observations"] = [o for o in merged.get("observations", []) if o.get("id") not in remove_obs_ids]
    after_o = len(merged["observations"])
    if before_o != after_o:
        print(f"    remove_observations: {before_o} → {after_o} (删 {before_o - after_o})")

    before_c = len(merged.get("causes", []))
    merged["causes"] = [c for c in merged.get("causes", []) if c.get("name") not in remove_cause_names]
    after_c = len(merged["causes"])
    if before_c != after_c:
        print(f"    remove_causes: {before_c} → {after_c} (删 {before_c - after_c})")

    before_a = len(merged.get("actions", []))
    merged["actions"] = [a for a in merged.get("actions", []) if a.get("name") not in remove_action_names]
    after_a = len(merged["actions"])
    if before_a != after_a:
        print(f"    remove_actions: {before_a} → {after_a} (删 {before_a - after_a})")

    # ---- 4) 修正 action.operation ----
    fixes = diff.get("fix_operation_types") or []
    fix_map = {f.get("action_name"): f.get("new_operation") for f in fixes if f.get("action_name") and f.get("new_operation")}
    if fix_map:
        fixed_count = 0
        for a in merged.get("actions", []):
            if a.get("name") in fix_map:
                old_op = a.get("operation")
                new_op = fix_map[a["name"]]
                if old_op != new_op:
                    a["operation"] = new_op
                    fixed_count += 1
        print(f"    fix_operation_types: 修正 {fixed_count} 条 action.operation")

    # ---- 5) 重定向 indicates/resolves 关系（merge 引起） + 级联删除引用已删节点的关系 ----
    existing_obs_ids = {o.get("id") for o in merged.get("observations", [])}
    existing_cause_names = {c.get("name") for c in merged.get("causes", [])}
    existing_action_names = {a.get("name") for a in merged.get("actions", [])}

    # indicates: observation → cause
    new_indicates = []
    for ind in merged.get("indicates", []):
        oid = ind.get("observation_id", "")
        # merge 重定向
        if oid in obs_id_remap:
            ind["observation_id"] = obs_id_remap[oid]
            oid = ind["observation_id"]
        if oid not in existing_obs_ids:
            continue
        if ind.get("cause_name") not in existing_cause_names:
            continue
        new_indicates.append(ind)
    before_i = len(merged.get("indicates", []))
    merged["indicates"] = new_indicates
    if before_i != len(new_indicates):
        print(f"    indicates: {before_i} → {len(new_indicates)}")

    # resolves: action → cause
    new_resolves = []
    for res in merged.get("resolves", []):
        if res.get("action_name") not in existing_action_names:
            continue
        if res.get("cause_name") not in existing_cause_names:
            continue
        new_resolves.append(res)
    before_r = len(merged.get("resolves", []))
    merged["resolves"] = new_resolves
    if before_r != len(new_resolves):
        print(f"    resolves: {before_r} → {len(new_resolves)}")

    # indicates 去重（merge 后可能出现同 observation+cause 的重复）
    seen = set()
    uniq_ind = []
    for ind in merged["indicates"]:
        key = (ind.get("observation_id"), ind.get("cause_name"))
        if key not in seen:
            seen.add(key)
            uniq_ind.append(ind)
    if len(uniq_ind) < len(merged["indicates"]):
        print(f"    indicates dedup after merge: {len(merged['indicates'])} → {len(uniq_ind)}")
        merged["indicates"] = uniq_ind

    # ---- 6) 完整性警告 ----
    warns = diff.get("completeness_warnings") or []
    if warns:
        print(f"    completeness_warnings: {len(warns)} 条（仅记录，不自动修）")
        for w in warns[:5]:
            print(f"      - {w.get('observation_id', '?')}: {w.get('issue', '?')}")
        if len(warns) > 5:
            print(f"      ... and {len(warns) - 5} more")

    return merged


def deduplicate_lower_nodes(merged: dict) -> dict:
    """
    下层节点代码层去重（在 LLM 清洗之前跑一轮，避免 LLM 在完全重复的项上浪费 token）。
    - Cause: 按 name 精确去重（保留首次出现的）
    - Action: 按 (name, operation, target) 三元组精确去重
    - Strategy: 按 (name, type) 精确去重

    注意：这里是精确字符串匹配，不做大小写/空格归一化。
    模糊合并交给 LLM 清洗（step3_lower.txt prompt）去做，避免误合并破坏 indicates/resolves 引用。
    """
    # Cause 按 name 精确去重
    seen_causes = set()
    unique_causes = []
    for cause in merged.get("causes", []):
        key = cause.get("name", "")
        if key and key not in seen_causes:
            seen_causes.add(key)
            unique_causes.append(cause)
    n_cause_before = len(merged.get("causes", []))
    merged["causes"] = unique_causes

    # Action 按 (name, operation, target) 三元组去重
    seen_action_keys = set()
    unique_actions = []
    for action in merged.get("actions", []):
        key = (
            action.get("name", ""),
            action.get("operation", ""),
            action.get("target", ""),
        )
        if key not in seen_action_keys:
            seen_action_keys.add(key)
            unique_actions.append(action)
    n_action_before = len(merged.get("actions", []))
    merged["actions"] = unique_actions

    # Strategy 按 (name, type) 去重
    seen_strategy_keys = set()
    unique_strategies = []
    for strat in merged.get("strategies", []):
        key = (strat.get("name", ""), strat.get("type", ""))
        if key not in seen_strategy_keys:
            seen_strategy_keys.add(key)
            unique_strategies.append(strat)
    n_strat_before = len(merged.get("strategies", []))
    merged["strategies"] = unique_strategies

    print(f"    Causes: {n_cause_before} → {len(unique_causes)} (deduped)")
    print(f"    Actions: {n_action_before} → {len(unique_actions)} (deduped)")
    print(f"    Strategies: {n_strat_before} → {len(unique_strategies)} (deduped)")

    return merged


def deduplicate_strategy_applies_to(edges: list) -> list:
    """
    strategy_applies_to 边按 (strategy_name, target_entity) 去重。

    跨文档合并时，同一个 strategy 可能在多个 workspace 里都链到同一个 upper entity
    （比如 "Timing Analysis Validation Protocol → AES" 出现 2 次）。这里做代码层去重，
    合并 source_papers。
    """
    groups: dict[tuple, list] = {}
    for edge in edges:
        key = (edge.get("strategy_name", ""), edge.get("target_entity", ""))
        groups.setdefault(key, []).append(edge)

    merged = []
    for (sname, tname), edge_list in groups.items():
        if len(edge_list) == 1:
            merged.append(edge_list[0])
            continue
        # 合并多条边：取第一条为基础，union source_papers
        base = edge_list[0].copy()
        all_papers = []
        for e in edge_list:
            papers = e.get("source_papers", [])
            if isinstance(papers, list):
                all_papers.extend(papers)
        base["source_papers"] = sorted(set(p for p in all_papers if p))
        # applicability 如果有 "specific"，优先保留 specific（更具体的范围声明）
        apps = {e.get("applicability", "general") for e in edge_list}
        if "specific" in apps:
            base["applicability"] = "specific"
        merged.append(base)

    dedup_count = len(edges) - len(merged)
    if dedup_count > 0:
        print(f"    strategy_applies_to dedup: {len(edges)} → {len(merged)}")

    return merged


def validate_strategy_applies_to(strategy_applies_to: list, upper_entities: list) -> list:
    """
    验证每条 strategy_applies_to 边的 target_entity 是否在合并后的 upper entities 里。

    Step2 生成 strategy_applies_to 时 upper 还没合并，实体名可能有变体（比如 Step2
    里是 "AES"，上层合并后变成了 "AES-128"）。这里做一次验证 + 模糊匹配。

    - 精确匹配：直接保留
    - 大小写不敏感匹配：保留并改写 target 到规范名
    - 前缀/包含匹配（比如 "AES" → "AES-128"）：保留并改写
    - 找不到匹配：丢弃，打 warning
    """
    upper_names = [e.get("name", "") for e in upper_entities if e.get("name")]
    upper_name_set = set(upper_names)
    upper_name_lower = {n.lower(): n for n in upper_names}

    validated = []
    dropped = 0

    for sat in strategy_applies_to:
        target = sat.get("target_entity", "")
        if not target:
            dropped += 1
            continue

        # 精确匹配
        if target in upper_name_set:
            validated.append(sat)
            continue

        # 大小写不敏感匹配
        if target.lower() in upper_name_lower:
            canonical = upper_name_lower[target.lower()]
            if canonical != target:
                print(f"    strategy_applies_to target '{target}' → '{canonical}' (case normalized)")
            sat["target_entity"] = canonical
            validated.append(sat)
            continue

        # 前缀 / 包含匹配：只在 target 和 upper name 之间有明显关联时接受
        # 比如 Step2 里的 "AES" 对应 upper 里的 "AES-128" 或 "AES" 本身
        candidates = [n for n in upper_names if target.lower() in n.lower() or n.lower() in target.lower()]
        if len(candidates) == 1:
            canonical = candidates[0]
            print(f"    strategy_applies_to target '{target}' → '{canonical}' (fuzzy match)")
            sat["target_entity"] = canonical
            validated.append(sat)
            continue
        elif len(candidates) > 1:
            print(f"    WARNING: strategy_applies_to target '{target}' has {len(candidates)} candidates {candidates}, keeping as-is")
            validated.append(sat)
            continue

        # 找不到匹配，丢弃
        strat_name = sat.get("strategy_name", "?")
        print(f"    WARNING: strategy_applies_to dropped: strategy '{strat_name}' → unknown target '{target}'")
        dropped += 1

    if dropped > 0:
        print(f"    Dropped {dropped} strategy_applies_to edges (no matching upper entity)")

    return validated


# ==================== 上层：合并所有文档 ====================

def merge_all_upper(workspace_dirs: list) -> dict:
    """读取并合并所有workspace的step2_upper.json"""
    all_entities = []
    all_relationships = []

    for ws in workspace_dirs:
        path = f"{ws}/step2_upper.json"
        if not Path(path).exists():
            continue

        data = json.loads(Path(path).read_text(encoding="utf-8"))
        ws_name = Path(ws).name

        # 给每条关系标记来源workspace
        for rel in data.get("relationships", []):
            props = rel.get("properties", {})
            papers = props.get("source_papers", [])
            if not papers or papers == ["doc_name"]:
                props["source_papers"] = [ws_name]

        all_entities.extend(data.get("entities", []))
        all_relationships.extend(data.get("relationships", []))

    print(f"  Collected from {len(workspace_dirs)} workspaces: {len(all_entities)} entities, {len(all_relationships)} relationships")
    return {"entities": all_entities, "relationships": all_relationships}


# ==================== 下层：合并所有文档 ====================

def merge_all_lower(workspace_dirs: list) -> dict:
    """读取并合并所有workspace的step2_lower.json，包括 diagnostic triples 和 strategies"""
    all_obs = []
    all_causes = []
    all_actions = []
    all_strategies = []               # 新增：保留 Strategy 节点
    all_indicates = []
    all_resolves = []
    all_strategy_applies_to = []      # 新增：保留 Strategy → upper 跨层边

    obs_counter = 1
    strat_counter = 1

    for ws in workspace_dirs:
        path = f"{ws}/step2_lower.json"
        if not Path(path).exists():
            continue

        data = json.loads(Path(path).read_text(encoding="utf-8"))
        ws_name = Path(ws).name

        # 重新编号 observation IDs 避免跨文档冲突
        obs_id_mapping = {}
        for obs in data.get("observations", []):
            old_id = obs["id"]
            new_id = f"diag_{obs_counter:03d}"
            obs_id_mapping[old_id] = new_id
            obs["id"] = new_id
            obs_counter += 1

        # 更新 indicates 中的 observation_id 引用
        for ind in data.get("indicates", []):
            old_id = ind.get("observation_id", "")
            if old_id in obs_id_mapping:
                ind["observation_id"] = obs_id_mapping[old_id]

        # 重新编号 Strategy IDs 避免跨文档冲突
        # strategy_applies_to 按 strategy_name 引用而不是 ID，所以重编号不影响引用
        for strat in data.get("strategies", []):
            old_id = strat.get("id", "")
            new_id = f"strat_{strat_counter:03d}"
            strat["id"] = new_id
            strat_counter += 1

        # 给 strategy_applies_to 边标记来源 workspace
        for sat in data.get("strategy_applies_to", []):
            papers = sat.get("source_papers", [])
            if not papers:
                sat["source_papers"] = [ws_name]

        all_obs.extend(data.get("observations", []))
        all_causes.extend(data.get("causes", []))
        all_actions.extend(data.get("actions", []))
        all_strategies.extend(data.get("strategies", []))
        all_indicates.extend(data.get("indicates", []))
        all_resolves.extend(data.get("resolves", []))
        all_strategy_applies_to.extend(data.get("strategy_applies_to", []))

    print(f"  Collected lower layer: {len(all_obs)} observations, {len(all_causes)} causes, "
          f"{len(all_actions)} actions, {len(all_strategies)} strategies")
    print(f"  Collected lower relations: {len(all_indicates)} indicates, {len(all_resolves)} resolves, "
          f"{len(all_strategy_applies_to)} strategy_applies_to")

    return {
        "observations": all_obs,
        "causes": all_causes,
        "actions": all_actions,
        "strategies": all_strategies,
        "indicates": all_indicates,
        "resolves": all_resolves,
        "strategy_applies_to": all_strategy_applies_to,
    }


# ==================== 跨层连接：Action → 上层实体 ====================

def build_cross_layer_links(upper_entities: list, lower_actions: list, client, model: str, prompt_path: str = "prompts/step3_cross_layer.txt") -> list:
    """用LLM自动匹配下层Action和上层实体，生成relates_to关系"""

    # 格式化上层实体列表
    entity_list = []
    for e in upper_entities:
        if e.get("name") == "none":
            continue
        entity_list.append(f"- {e['name']} ({e.get('type', '')})")
    upper_str = "\n".join(entity_list)

    # 格式化下层Action列表
    action_list = []
    for a in lower_actions:
        action_list.append(f"- {a['name']} (operation: {a.get('operation', '')}, target: {a.get('target', '')})")
    lower_str = "\n".join(action_list)

    # 读取prompt模板并填充
    prompt_template = Path(prompt_path).read_text(encoding="utf-8")
    prompt = prompt_template.replace("{upper_entities}", upper_str).replace("{lower_actions}", lower_str)

    print(f"  Calling LLM for cross-layer linking (thinking=OFF, stream=on, max_tokens=65000)...")
    from types import SimpleNamespace
    # max_tokens=65000: 前轮 16000 不够装 278 actions × N entities 的 relates_to JSON（撞上限被截断）。
    # thinking=False: cross_layer 是"action name 匹配 entity name"的机械检索，不需深推理；
    #                  前轮 reasoning 69K chars 花了 23 分钟却没帮 JSON 完整输出。
    # stream=True: 绕开 SDK 600s timeout。
    cross_text, _cross_meta = call_llm_with_retry(
        client=client, model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1, max_tokens=65000,
        thinking_budget=0, enable_thinking=False,
        stream=True,
    )
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=cross_text))])

    text = response.choices[0].message.content.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        links = json.loads(text)
    except json.JSONDecodeError as e:
        # LLM 偶尔返回带尾逗号 / 单引号等非严格 JSON。先尝试简单修复，再退一次 retry。
        print(f"    WARN: cross-layer JSON parse failed: {e}")
        print(f"    Raw text (first 400 chars): {text[:400]}")
        try:
            # 简单修复：去掉尾逗号
            import re as _re
            fixed = _re.sub(r",\s*([\]}])", r"\1", text)
            links = json.loads(fixed)
            print(f"    Recovered by trailing-comma fix")
        except Exception:
            print(f"    WARN: falling back to empty relates_to (step3 will save lower without cross-layer Action→upper edges)")
            return []

    # 验证：确保action_name和entity_name都存在于输入中
    valid_actions = {a["name"] for a in lower_actions}
    valid_entities = {e["name"] for e in upper_entities}

    def _clean_action_name(s: str) -> str:
        """兜底：LLM 有时把 '(operation: ..., target: ...)' 后缀也复制进来，剥掉它"""
        idx = s.find(" (operation:")
        if idx > 0:
            return s[:idx].rstrip()
        return s.rstrip()

    def _clean_entity_name(s: str) -> str:
        """兜底：LLM 有时把 '(EntityType)' 后缀也复制进来，剥掉它"""
        # 匹配末尾的 '(Type)' 后缀（Type 里不含括号）
        m = re.search(r"\s*\([A-Za-z][A-Za-z_0-9 ]*\)\s*$", s)
        if m:
            return s[:m.start()].rstrip()
        return s.rstrip()

    validated = []
    for link in links:
        raw_a = link.get("action_name", "")
        raw_e = link.get("entity_name", "")
        role = link.get("role", "")

        action_name = _clean_action_name(raw_a)
        entity_name = _clean_entity_name(raw_e)
        if action_name not in valid_actions:
            print(f"    WARNING: Action not found: '{raw_a}' -> '{action_name}', skipping")
            continue
        if entity_name not in valid_entities:
            print(f"    WARNING: Entity not found: '{raw_e}' -> '{entity_name}', skipping")
            continue

        link["action_name"] = action_name
        link["entity_name"] = entity_name
        validated.append(link)
        print(f"    {action_name} --[relates_to ({role})]--> {entity_name}")

    return validated


# ==================== 保存 ====================

def save_json(data, output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"  Saved: {output_path}")


# ==================== 主函数 ====================

def main():
    # ========================================
    # ========== 在这里修改配置 ==========
    # ========================================

    # --- 自动扫描 workspace/* 里含有 step2_*.json 的目录 ---
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ws_root = Path("workspace")
    if not ws_root.exists():
        print(f"  ERROR: workspace directory not found: {ws_root}")
        return
    workspaces = sorted(
        str(p) for p in ws_root.iterdir()
        if p.is_dir() and (
            (p / "step2_upper.json").exists() or (p / "step2_lower.json").exists()
        )
    )
    print(f"Found {len(workspaces)} workspaces with step2 output:")
    for w in workspaces[:10]:
        print(f"  - {w}")
    if len(workspaces) > 10:
        print(f"  ... and {len(workspaces) - 10} more")

    # --- LLM 配置 ---
    config = load_config()

    # ---- 配置 C（2026-04-20 晚切换）: SiliconFlow Pro + Kimi-K2.5 (256K context, thinking) ----
    # step3 Lower 114K 输入 + thinking 用 DSv3.2 频繁 timeout，换 Kimi-K2.5 256K 更稳
    base_url = config["api"]["siliconflow"]["base_url"]
    api_key = config["api"]["siliconflow"]["api_key_pro"]
    model = "Pro/moonshotai/Kimi-K2.5"

    # ---- 配置 A: SiliconFlow + DeepSeek-V3.2（step1/step2 用，step3 Lower timeout 频繁） ----
    # api_key = config["api"]["siliconflow"]["api_key"]
    # model = "deepseek-ai/DeepSeek-V3.2"

    # ---- 配置 B: OpenRouter + Claude Opus 4.6 (贵，最终版抽取用) ----
    # api_key = config["api"]["openrouter"]["api_key"]
    # base_url = config["api"]["openrouter"]["base_url"]
    # model = "anthropic/claude-opus-4.6"

    # --- Prompt 文件路径 ---
    prompt_upper = "prompts/step3_upper.txt"
    prompt_lower = "prompts/step3_lower.txt"
    prompt_cross_layer = "prompts/step3_cross_layer.txt"

    # --- 输出路径 ---
    # 改到 round1/ 子目录防止覆盖阶段 11 frozen 基线（knowledge/{upper,lower}_layer/final_*.json）
    # round1 跑稳了再手动 promote 到根路径。
    output_upper = "../upper_layer/round1/final_upper.json"
    output_lower = "../lower_layer/round1/final_lower.json"
    output_conflicts = "workspace/conflict_report.json"

    # --- 是否跑上层/下层 ---
    # Upper 已在 2026-04-20 17:00 用 DSv3.2 完成（final_upper.json 已就位），跳过不重跑。
    # Lower 也已于 2026-04-20 22:20 用 diff+stream 完成（final_lower.json 已就位），本次跳过。
    # 只补跑 cross_layer（上轮被 max_tokens=16000 截断，现改 max_tokens=65000 + thinking off 重跑）。
    run_upper = False
    run_lower = False
    # Lower LLM clean 走 diff + stream 模式（2026-04-20 晚重构）：LLM 只输出变更指令，输出
    # 从 16K tokens 降到 1-2K tokens，避开原先 114K 输入下单次生成 20+ 分钟超 SDK timeout 问题。
    # 如要跳过：改成 False，只做代码层 dedup。
    run_lower_llm_clean = True

    # ========================================
    # ========== 以下不需要修改 ==========
    # ========================================

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    client = OpenAI(api_key=api_key, base_url=base_url)

    # ==================== 上层处理 ====================
    if run_upper:
        print(f"\n{'='*60}")
        print(f"Step 3: Knowledge Fusion — Upper Layer")
        print(f"{'='*60}")

        # 3a. 合并所有文档
        print(f"\n[3a] Merging all documents...")
        merged = merge_all_upper(workspaces)

        # 3b. 实体名标准化
        print(f"\n[3b] Standardizing entity names...")
        merged["entities"], merged["relationships"] = standardize_entity_names(
            merged["entities"], merged["relationships"]
        )

        # 3c. 删除无效关系（先做一次，清理 Step2 阶段可能出现的明显错误）
        print(f"\n[3c] Removing invalid relationships (pre-dedup)...")
        merged["relationships"] = remove_invalid_relationships(
            merged["entities"], merged["relationships"]
        )

        # 3d. 实体去重
        print(f"\n[3d] Deduplicating entities...")
        merged["entities"] = deduplicate_entities(merged["entities"])

        # 3e. 关系去重 + 算confidence
        print(f"\n[3e] Deduplicating relationships + calculating confidence...")
        merged["relationships"] = deduplicate_relationships(merged["relationships"])

        # 3f. LLM推断跨文档关系
        print(f"\n[3f] Inferring cross-document relationships (LLM)...")
        try:
            merged_json = json.dumps(merged, ensure_ascii=False, indent=2)
            inferred = call_llm(merged_json, prompt_upper, client, model)
            new_rels = inferred.get("inferred_relationships", [])
            print(f"  Inferred {len(new_rels)} new relationships")

            # 给推断出来的关系打 inferred 标记 + 兜底 source_papers
            for r in new_rels:
                props = r.setdefault("properties", {})
                props["inferred"] = True
                if not props.get("source_papers"):
                    props["source_papers"] = []
                if not props.get("source_text"):
                    props["source_text"] = "inferred from cross-document analysis"

            merged["relationships"].extend(new_rels)

            # 推断关系后再跑一次清洗：删无效 + 去重（避免 LLM 推出已存在或非法的关系）
            if new_rels:
                print(f"  Re-running invalid-relationship filter after inference...")
                merged["relationships"] = remove_invalid_relationships(
                    merged["entities"], merged["relationships"]
                )
                print(f"  Re-running relationship dedup after inference...")
                merged["relationships"] = deduplicate_relationships(merged["relationships"])
        except Exception as e:
            print(f"  ERROR in LLM inference: {e}")

        # 3g. 删除占位符实体（Countermeasure="none" 等虚节点）
        print(f"\n[3g] Removing placeholder entities...")
        merged["entities"], merged["relationships"] = remove_placeholder_entities(
            merged["entities"], merged["relationships"]
        )

        # 3h. 冲突检测
        print(f"\n[3h] Detecting conflicts...")
        conflicts = detect_conflicts(merged["relationships"])
        if conflicts:
            print(f"  Found {len(conflicts)} conflicts")
        else:
            print(f"  No conflicts found")

        # 3i. 完整性检查
        print(f"\n[3i] Checking completeness...")
        orphans = check_completeness(merged["entities"], merged["relationships"])

        # 保存
        print(f"\n--- Saving upper layer results ---")
        save_json(merged, output_upper)
        save_json({"conflicts": conflicts, "orphan_entities": orphans}, output_conflicts)

        # 统计
        print(f"\n--- Upper Layer Summary ---")
        print(f"  Final entities: {len(merged['entities'])}")
        print(f"  Final relationships: {len(merged['relationships'])}")
        rel_types = defaultdict(int)
        for r in merged["relationships"]:
            rel_types[r["relation"]] += 1
        for rt, count in sorted(rel_types.items()):
            print(f"    {rt}: {count}")

    # ==================== 下层处理 ====================
    if run_lower:
        print(f"\n{'='*60}")
        print(f"Step 3: Knowledge Fusion — Lower Layer")
        print(f"{'='*60}")

        # 合并所有文档
        print(f"\n[Merge] Merging all documents...")
        merged_lower = merge_all_lower(workspaces)

        # 代码层去重（在 LLM 清洗之前，避免 LLM 在完全重复的项上浪费 token）
        print(f"\n[Dedup] Deduplicating lower nodes (code level)...")
        merged_lower = deduplicate_lower_nodes(merged_lower)

        # 跳过空的下层
        total_items = (len(merged_lower["observations"]) +
                      len(merged_lower["causes"]) +
                      len(merged_lower["actions"]) +
                      len(merged_lower.get("strategies", [])))
        if total_items == 0:
            print(f"  No lower layer data to process")
            save_json(merged_lower, output_lower)
        else:
            # LLM 清洗只处理 diagnostic triples（observations/causes/actions/indicates/resolves）
            # strategies 和 strategy_applies_to 不进 LLM，保持结构化原样
            strategies_backup = merged_lower.get("strategies", [])
            strategy_applies_to_backup = merged_lower.get("strategy_applies_to", [])

            # 构造只含 diagnostic triples 的输入供 LLM 清洗
            llm_input = {
                "observations": merged_lower.get("observations", []),
                "causes": merged_lower.get("causes", []),
                "actions": merged_lower.get("actions", []),
                "indicates": merged_lower.get("indicates", []),
                "resolves": merged_lower.get("resolves", []),
            }

            if not run_lower_llm_clean:
                print(f"\n[Clean] SKIPPED (run_lower_llm_clean=False) — 保留代码层 dedup 结果")

            print(f"\n[Clean] Filtering and cleaning diagnostic triples (LLM, diff+stream)...")
            try:
                if not run_lower_llm_clean:
                    raise RuntimeError("__SKIP_LLM_CLEAN__")
                # DIFF 模式：LLM 只返回变更指令（remove/fix/merge），代码层 apply_lower_diff 把指令应用到
                # merged_lower。输出 tokens 从 ~16K → ~1-2K，生成时间从 20+ 分钟 → <1 分钟。
                # stream=True 额外保险，避免大响应时 SDK 600s timeout（虽然 diff 输出本来就小）。
                lower_json = json.dumps(llm_input, ensure_ascii=False, indent=2)
                diff_result = call_llm(lower_json, prompt_lower, client, model,
                                       enable_thinking=True, stream=True)

                # 打印 diff 摘要
                print(f"  LLM diff summary:")
                for key in ["remove_observation_ids", "remove_cause_names", "remove_action_names",
                            "fix_operation_types", "merge_observations", "completeness_warnings"]:
                    n = len(diff_result.get(key) or [])
                    if n > 0:
                        print(f"    {key}: {n}")

                # 应用 diff 到 merged_lower（原地修改）
                # diff 模式下 LLM 只返回变更指令，apply_lower_diff 已做完所有修改 + 级联删除 +
                # indicates dedup，不再需要旧的"覆盖字段 + 再去重"逻辑。
                merged_lower = apply_lower_diff(merged_lower, diff_result)
            except Exception as e:
                if str(e) == "__SKIP_LLM_CLEAN__":
                    print(f"  [LLM clean bypass] 代码层 dedup 结果直接保留")
                else:
                    print(f"  ERROR in LLM cleaning: {e}")

            # 恢复 strategies 和 strategy_applies_to（LLM 不动）
            merged_lower["strategies"] = strategies_backup
            merged_lower["strategy_applies_to"] = strategy_applies_to_backup

            # 保存
            print(f"\n--- Saving lower layer results ---")
            save_json(merged_lower, output_lower)

            # 统计
            print(f"\n--- Lower Layer Summary ---")
            print(f"  Final observations: {len(merged_lower.get('observations', []))}")
            print(f"  Final causes: {len(merged_lower.get('causes', []))}")
            print(f"  Final actions: {len(merged_lower.get('actions', []))}")
            print(f"  Final strategies: {len(merged_lower.get('strategies', []))}")
            print(f"  Final indicates: {len(merged_lower.get('indicates', []))}")
            print(f"  Final resolves: {len(merged_lower.get('resolves', []))}")
            print(f"  Final strategy_applies_to: {len(merged_lower.get('strategy_applies_to', []))}")

    # ==================== 跨层连接 ====================
    # 只要两份 final 都存在就跑 cross_layer，不依赖 run_upper / run_lower（支持补跑场景）
    if Path(output_upper).exists() and Path(output_lower).exists():
        print(f"\n{'='*60}")
        print(f"Step 3: Cross-Layer Linking")
        print(f"{'='*60}")

        # 读取已保存的上下层数据
        upper_data = json.loads(Path(output_upper).read_text(encoding="utf-8"))
        lower_data = json.loads(Path(output_lower).read_text(encoding="utf-8"))

        # 建立 Action → upper entity 的 relates_to 关系（LLM 生成）
        print(f"\n[Action → upper] Building relates_to links via LLM...")
        relates_to = build_cross_layer_links(
            upper_entities=upper_data.get("entities", []),
            lower_actions=lower_data.get("actions", []),
            client=client,
            model=model,
            prompt_path=prompt_cross_layer
        )

        # 验证 Strategy → upper entity 的 strategy_applies_to 边
        # 这些边在 Step2 已经生成（从 strategy.related_upper_entities），现在做：
        # 1. 代码层去重（同一个 (strategy, target) 来自多个 workspace 的情况合并）
        # 2. target_entity 必须存在于合并后的 upper entities 里（否则是死链）
        print(f"\n[Strategy → upper] Deduplicating and validating strategy_applies_to edges...")
        raw_sat = lower_data.get("strategy_applies_to", [])
        deduped_sat = deduplicate_strategy_applies_to(raw_sat)
        validated_sat = validate_strategy_applies_to(deduped_sat, upper_data.get("entities", []))
        print(f"  strategy_applies_to: {len(raw_sat)} → {len(deduped_sat)} (deduped) → {len(validated_sat)} (validated)")

        # 写入下层数据
        lower_data["relates_to"] = relates_to
        lower_data["strategy_applies_to"] = validated_sat
        save_json(lower_data, output_lower)

        print(f"\n  Generated {len(relates_to)} cross-layer relates_to links")
        print(f"  Validated {len(validated_sat)} cross-layer strategy_applies_to edges")

    print(f"\n{'='*60}")
    print(f"Step 3 fusion complete!")
    print(f"{'='*60}")

    # Step 3.6 — post-fusion dedupe + dangling cleanup (pure Python, no LLM)
    if Path(output_upper).exists() and Path(output_lower).exists():
        run_postfusion_dedupe(output_upper, output_lower)

    print(f"\n{'='*60}")
    print(f"Step 3 complete (fusion + post-fusion dedupe)!")
    print(f"{'='*60}")


# ==================== Step 3.6: Post-Fusion Dedupe ====================
# Pure-Python pass that runs automatically at the end of Step 3 main().
# Closes the JSON-vs-Neo4j count divergence by collapsing same-(type,name)
# entity records, same-(subject,relation,object) relationship records,
# duplicate lower-layer edges, and dangling cross-layer references.
#
# Can also be invoked directly via:
#   python -c "from step3_knowledge_fusion import run_postfusion_dedupe; \
#              run_postfusion_dedupe('../upper_layer/round1/final_upper.json', \
#                                    '../lower_layer/round1/final_lower.json')"

def _stringify(v):
    """Coerce a scalar into a string for set-based union."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    return str(v)


def _merge_props(records, special_text_keys=("source_text",)):
    """Merge ``properties`` dicts from a list of records.

    For each property key:
      * ``None`` / empty values dropped
      * Lists flattened, scalars stringified, both union-deduped (preserving order)
      * Keys in ``special_text_keys`` joined with ' || ' instead of listed
      * Single-value -> scalar; multi-value -> sorted list of strings
    """
    text_buckets = defaultdict(list)
    text_seen = defaultdict(set)
    other_buckets = defaultdict(list)
    other_seen = defaultdict(set)
    list_origin = {}

    for rec in records:
        props = rec.get("properties") or {}
        for k, v in props.items():
            if v is None:
                continue
            if isinstance(v, list):
                list_origin[k] = True
                for item in v:
                    if item is None:
                        continue
                    s = _stringify(item).strip()
                    if not s:
                        continue
                    if k in special_text_keys:
                        if s not in text_seen[k]:
                            text_seen[k].add(s)
                            text_buckets[k].append(s)
                    else:
                        if s not in other_seen[k]:
                            other_seen[k].add(s)
                            other_buckets[k].append(s)
                continue
            s = _stringify(v).strip()
            if not s:
                continue
            if k in special_text_keys:
                if s not in text_seen[k]:
                    text_seen[k].add(s)
                    text_buckets[k].append(s)
            else:
                if s not in other_seen[k]:
                    other_seen[k].add(s)
                    other_buckets[k].append(s)

    out = {}
    for k, items in text_buckets.items():
        out[k] = " || ".join(items) if items else ""
    for k, items in other_buckets.items():
        if not items:
            continue
        if list_origin.get(k):
            out[k] = items
        elif len(items) == 1:
            out[k] = items[0]
        else:
            out[k] = sorted(items)
    return out


def _dedupe_entities(entities):
    by_key = defaultdict(list)
    order = []
    for e in entities:
        key = (e.get("type", ""), e.get("name", ""))
        if key not in by_key:
            order.append(key)
        by_key[key].append(e)

    deduped = []
    for key in order:
        recs = by_key[key]
        if len(recs) == 1:
            deduped.append(recs[0])
            continue
        merged_props = _merge_props(recs, special_text_keys=("source_text",))
        deduped.append({
            "name": key[1],
            "type": key[0],
            "properties": merged_props,
        })
    return deduped


def _dedupe_relationships(rels):
    by_key = defaultdict(list)
    order = []
    for r in rels:
        key = (r.get("subject", ""), r.get("relation", ""), r.get("object", ""))
        if key not in by_key:
            order.append(key)
        by_key[key].append(r)

    deduped = []
    for key in order:
        recs = by_key[key]
        if len(recs) == 1:
            deduped.append(recs[0])
            continue
        merged_props = _merge_props(recs, special_text_keys=("source_text",))
        deduped.append({
            "subject": key[0],
            "relation": key[1],
            "object": key[2],
            "properties": merged_props,
        })
    return deduped


def _dedupe_lower_edges(items, key_fields):
    """Dedupe a list of lower-layer edge dicts by ``key_fields`` tuple.
    Returns ``(deduped_list, n_dropped)``."""
    by_key = defaultdict(list)
    order = []
    for it in items:
        key = tuple(it.get(f, "") for f in key_fields)
        if key not in by_key:
            order.append(key)
        by_key[key].append(it)
    deduped = []
    for key in order:
        recs = by_key[key]
        if len(recs) == 1:
            deduped.append(recs[0])
            continue
        merged = {f: v for f, v in zip(key_fields, key)}
        wrapped = [{"properties": {k: v for k, v in r.items() if k not in key_fields}} for r in recs]
        merged_props = _merge_props(wrapped, special_text_keys=("source_text",))
        merged.update(merged_props)
        deduped.append(merged)
    return deduped, len(items) - len(deduped)


def _drop_dangling(items, ref_field, valid_set, label):
    """Drop items whose ``ref_field`` value is not in ``valid_set``."""
    kept = []
    dropped = []
    for it in items:
        if it.get(ref_field) in valid_set:
            kept.append(it)
        else:
            dropped.append((label, it.get(ref_field), it))
    return kept, dropped


def run_postfusion_dedupe(upper_path: str, lower_path: str) -> None:
    """Apply post-fusion dedupe + dangling cleanup; rewrite both files in
    place, with .pre_dedupe.bak backups.

    Performs:
      1. Upper entities  : group by (type, name); merge properties.
      2. Upper rels      : group by (subject, relation, object); merge.
      3. Lower edges     : drop dangling (target not in declared entities)
                           + dedupe by edge endpoints. Touches indicates,
                           resolves, relates_to, strategy_applies_to.

    Idempotent: re-running on already-deduped JSON makes no change.
    """
    import shutil  # local import: keep module top tidy

    print(f"\n{'='*60}")
    print("Step 3.6 — Post-Fusion Dedupe Pass")
    print(f"{'='*60}")

    upper_path_p = Path(upper_path)
    lower_path_p = Path(lower_path)
    upper = json.loads(upper_path_p.read_text(encoding="utf-8"))
    lower = json.loads(lower_path_p.read_text(encoding="utf-8"))

    # --- Upper-layer dedupe ---
    ents = upper.get("entities", [])
    deduped_ents = _dedupe_entities(ents)
    rels = upper.get("relationships", [])
    deduped_rels = _dedupe_relationships(rels)

    print(f"  Upper entities      : {len(ents)} -> {len(deduped_ents)}")
    print(f"  Upper relationships : {len(rels)} -> {len(deduped_rels)}")

    # --- Lower-layer edge dedupe + dangling cleanup ---
    upper_name_set = {e["name"] for e in deduped_ents
                      if not (e.get("type") == "Countermeasure" and e.get("name") == "none")}
    cause_set = {c.get("name", "") for c in lower.get("causes", [])}
    action_set = {a.get("name", "") for a in lower.get("actions", [])}
    obs_set = {o.get("id", "") for o in lower.get("observations", [])}
    strat_name_set = {s.get("name", "") for s in lower.get("strategies", [])}

    # Drop dangling FIRST (otherwise dedupe key collapses bad refs)
    indicates = lower.get("indicates", [])
    indicates, ind_drop1 = _drop_dangling(indicates, "observation_id", obs_set, "indicates.observation_id")
    indicates, ind_drop2 = _drop_dangling(indicates, "cause_name", cause_set, "indicates.cause_name")
    indicates, _ = _dedupe_lower_edges(indicates, ("observation_id", "cause_name"))

    resolves = lower.get("resolves", [])
    resolves, res_drop1 = _drop_dangling(resolves, "action_name", action_set, "resolves.action_name")
    resolves, res_drop2 = _drop_dangling(resolves, "cause_name", cause_set, "resolves.cause_name")
    resolves, _ = _dedupe_lower_edges(resolves, ("action_name", "cause_name"))

    relates_to = lower.get("relates_to", [])
    relates_to, rt_drop1 = _drop_dangling(relates_to, "action_name", action_set, "relates_to.action_name")
    relates_to, rt_drop2 = _drop_dangling(relates_to, "entity_name", upper_name_set, "relates_to.entity_name")
    relates_to, _ = _dedupe_lower_edges(relates_to, ("action_name", "entity_name"))

    s_applies = lower.get("strategy_applies_to", [])
    s_applies, sa_drop1 = _drop_dangling(s_applies, "strategy_name", strat_name_set, "strategy_applies_to.strategy_name")
    s_applies, sa_drop2 = _drop_dangling(s_applies, "target_entity", upper_name_set, "strategy_applies_to.target_entity")
    s_applies, _ = _dedupe_lower_edges(s_applies, ("strategy_name", "target_entity"))

    all_dropped = (ind_drop1 + ind_drop2 + res_drop1 + res_drop2 +
                   rt_drop1 + rt_drop2 + sa_drop1 + sa_drop2)

    print(f"  indicates           : {len(lower.get('indicates', []))} -> {len(indicates)}")
    print(f"  resolves            : {len(lower.get('resolves', []))} -> {len(resolves)}")
    print(f"  relates_to          : {len(lower.get('relates_to', []))} -> {len(relates_to)}")
    print(f"  strategy_applies_to : {len(lower.get('strategy_applies_to', []))} -> {len(s_applies)}")
    if all_dropped:
        print(f"  Dangling references dropped: {len(all_dropped)}")
        for label, val, _it in all_dropped[:8]:
            print(f"    [{label}] -> {val!r}")
        if len(all_dropped) > 8:
            print(f"    ... and {len(all_dropped) - 8} more")

    # Skip rewrite if nothing changed (idempotent re-run)
    if (len(deduped_ents) == len(ents)
            and len(deduped_rels) == len(rels)
            and not all_dropped
            and len(indicates) == len(lower.get("indicates", []))
            and len(resolves) == len(lower.get("resolves", []))
            and len(relates_to) == len(lower.get("relates_to", []))
            and len(s_applies) == len(lower.get("strategy_applies_to", []))):
        print("  No changes; skipping rewrite.")
        return

    # Backup + rewrite upper
    ubak = upper_path_p.with_suffix(upper_path_p.suffix + ".pre_dedupe.bak")
    if not ubak.exists():
        shutil.copy2(upper_path_p, ubak)
        print(f"  Backup written (upper): {ubak.name}")
    new_upper = dict(upper)
    new_upper["entities"] = deduped_ents
    new_upper["relationships"] = deduped_rels
    upper_path_p.write_text(json.dumps(new_upper, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Rewrote (upper): {upper_path_p.name}")

    # Backup + rewrite lower
    lbak = lower_path_p.with_suffix(lower_path_p.suffix + ".pre_dedupe.bak")
    if not lbak.exists():
        shutil.copy2(lower_path_p, lbak)
        print(f"  Backup written (lower): {lbak.name}")
    new_lower = dict(lower)
    new_lower["indicates"] = indicates
    new_lower["resolves"] = resolves
    new_lower["relates_to"] = relates_to
    new_lower["strategy_applies_to"] = s_applies
    lower_path_p.write_text(json.dumps(new_lower, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Rewrote (lower): {lower_path_p.name}")


if __name__ == "__main__":
    main()
