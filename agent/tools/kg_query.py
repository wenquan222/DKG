"""
DKG Knowledge Graph Search Module

纯搜索，不调LLM。输入关键词，输出原始知识条目JSON。
所有LLM相关逻辑（关键词提取、结果理解）都在agent主程序里。

搜索策略（2026-04 更新，支持 Pipeline 和 Strategy 新节点）：
1. 关键词匹配上层节点（Algorithm, DeviceClass, ..., **Pipeline**）
2. 从上层节点出发搜索相关关系（works_with, precedes, consists_of, ...）
3. 关键词匹配下层诊断链（Observation→Cause→Action），同时搜索Cause和Action的文本
4. 关键词匹配 **Strategy 节点**（按 name/type/trigger_condition/content/rationale），同时拉取 strategy_applies_to 的目标
5. 从已匹配的上层实体出发：
   5a. 通过 relates_to 反向拉取关联的 Action → 诊断链（跨层连接，Action 侧）
   5b. 通过 strategy_applies_to 反向拉取关联的 Strategy（跨层连接，Strategy 侧）
"""

import json
import warnings
import logging
from neo4j import GraphDatabase

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("neo4j").setLevel(logging.ERROR)


# ==================== 搜索配置 ====================
DEFAULT_CONFIG = {
    # 2026-04-23 二次调参（Round 1 KG 166 doc 规模下防信息过载）:
    # 配合 keyword prompt 限 ≤10 个，KG 返回 markdown 目标 ≤35K chars。
    # max_diagnostic_chains 再从 10→5：多关键词下同一 Obs-Cause-Action 链会被反复拉，
    # 降到 5 后单关键词最多 5 条，依靠关键词间 union 保证覆盖。
    "max_results_per_keyword": 5,
    "max_diagnostic_chains": 5,
    "max_upper_components": 8,
}


class DKGSearcher:
    """DKG知识图谱搜索器 — 纯关键词搜索，不调LLM"""

    def __init__(self, uri: str, username: str, password: str,
                 database: str = "neo4j", config: dict = None):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        self.config = {**DEFAULT_CONFIG, **(config or {})}

    def close(self):
        self.driver.close()

    def _run(self, query: str, **params):
        with self.driver.session(database=self.database) as session:
            return session.run(query, **params).data()

    # ================================================================
    # 辅助方法：构建诊断链条目（避免重复代码）
    # ================================================================

    def _add_diagnostic_chain(self, results, row, source="keyword"):
        """将一行诊断链查询结果加入results，自动去重"""
        chain_key = (row["obs_id"], row["cause"], row["action"])
        existing_keys = [(c["observation"]["id"], c["cause"], c["action"]["name"])
                         for c in results["diagnostic_chains"]]
        if chain_key not in existing_keys:
            alts = [a for a in (row.get("alternatives") or []) if a]
            entry = {
                "observation": {
                    "id": row["obs_id"],
                    "metric": row["metric"],
                    "condition": row["condition"]
                },
                "cause": row["cause"],
                "likelihood": row.get("likelihood"),
                "diagnostic_check": row.get("diagnostic_check"),
                "action": {
                    "name": row["action"],
                    "operation": row.get("operation"),
                    "target": row.get("target"),
                    "strategy": row.get("strategy"),
                },
                "related_component": {
                    "name": row["component_name"],
                    "type": row["component_type"],
                } if row.get("component_name") else None,
                "alternatives": alts if alts else None,
                "source": source,
            }
            results["diagnostic_chains"].append(entry)

    def _add_strategy(self, results, row, source="keyword"):
        """
        将一行 Strategy 查询结果加入 results["strategies"]，按 id 去重。

        Strategy 有三种 type（troubleshooting_checklist / anti_pattern_set / parameter_preset_bundle），
        content 字段保留原始 JSON 字符串，由 agent 在使用时按需反序列化。
        """
        strat_id = row.get("id", "")
        if not strat_id:
            return
        existing_ids = [s.get("id") for s in results["strategies"]]
        if strat_id in existing_ids:
            return

        # 清理 applies_to 列表（OPTIONAL MATCH 可能会产生 {name: None, ...} 的空项）
        applies_to_raw = row.get("applies_to") or []
        applies_to = [
            {
                "name": a.get("name"),
                "label": a.get("label"),
                "applicability": a.get("applicability"),
            }
            for a in applies_to_raw
            if a and a.get("name")
        ]

        entry = {
            "id": strat_id,
            "name": row.get("name"),
            "type": row.get("type"),
            "trigger_condition": row.get("trigger_condition"),
            "content": row.get("content"),  # JSON 字符串，保持原样
            "rationale": row.get("rationale"),
            "applies_to": applies_to,
            "source": source,
            # 2026-04-23 Patch 002：canonical 字段透传给 markdown render
            "is_canonical": bool(row.get("is_canonical", False)),
            "priority": int(row.get("priority") or 0),
        }
        results["strategies"].append(entry)

    # ================================================================
    # 核心搜索：输入关键词列表，输出原始JSON
    # ================================================================

    def search(self, keywords: list, as_markdown: bool = True) -> str:
        """
        用关键词列表在整个知识图谱中搜索。

        as_markdown=True (默认): 返回结构化 Markdown 文本（更易被 LLM 消费）
        as_markdown=False: 返回原始 JSON 字符串（旧代码兼容）

        返回结果包含：
        - upper_matches: 上层图谱匹配（含 Pipeline 节点）
        - diagnostic_chains: 下层诊断链（关键词匹配 + 跨层反向拉取）
        - strategies: Strategy 节点（关键词匹配 + 跨层反向拉取）
        - relationships: 相关关系（含 consists_of）
        """
        results = {
            "search_keywords": keywords,
            "upper_matches": [],
            "diagnostic_chains": [],
            "strategies": [],         # 2026-04 新增：Strategy 节点
            "relationships": [],
        }

        for kw in keywords:
            if not kw or not kw.strip():
                continue

            # ========== 1. 搜索上层节点 ==========
            # 2026-04-23 Patch 002：补齐 12 类 label（+DiagnosticMethod/ValidationMethod/RecoveryMethod）
            #                      + ORDER BY is_canonical/priority，保障 canonical expert path 优先
            upper = self._run("""
                MATCH (n)
                WHERE (n:Algorithm OR n:DeviceClass OR n:TraceType OR
                       n:AttackPoint OR n:LeakageModel OR n:Preprocessing OR
                       n:StatMethod OR n:Countermeasure OR n:Pipeline OR
                       n:DiagnosticMethod OR n:ValidationMethod OR n:RecoveryMethod)
                  AND (toLower(n.name) CONTAINS toLower($kw)
                       OR toLower(coalesce(n.category,'')) CONTAINS toLower($kw)
                       OR toLower(coalesce(n.type,'')) CONTAINS toLower($kw)
                       OR toLower(coalesce(n.implementation_type,'')) CONTAINS toLower($kw)
                       OR toLower(coalesce(n.trigger_condition,'')) CONTAINS toLower($kw)
                       OR toLower(coalesce(n.applicable_scenarios,'')) CONTAINS toLower($kw))
                RETURN DISTINCT n.name AS name, labels(n)[0] AS label, properties(n) AS props,
                       coalesce(n.is_canonical, false) AS is_canonical,
                       coalesce(n.priority, 0) AS priority
                ORDER BY is_canonical DESC, priority DESC, n.name
                LIMIT $limit
            """, kw=kw, limit=self.config["max_upper_components"])

            for row in upper:
                entry = {"name": row["name"], "label": row["label"], "properties": row["props"]}
                if entry not in results["upper_matches"]:
                    results["upper_matches"].append(entry)

            # ========== 2. 从上层节点出发搜索关系 ==========
            # 2026-04-23 Patch 002：补齐 12 类 label + ORDER BY canonical 优先
            rels = self._run("""
                MATCH (n)-[r]-(m)
                WHERE (n:Algorithm OR n:DeviceClass OR n:TraceType OR
                       n:AttackPoint OR n:LeakageModel OR n:Preprocessing OR
                       n:StatMethod OR n:Countermeasure OR n:Pipeline OR
                       n:DiagnosticMethod OR n:ValidationMethod OR n:RecoveryMethod)
                  AND (toLower(n.name) CONTAINS toLower($kw)
                       OR toLower(coalesce(n.category,'')) CONTAINS toLower($kw)
                       OR toLower(coalesce(n.trigger_condition,'')) CONTAINS toLower($kw))
                RETURN DISTINCT
                    n.name AS from_name, labels(n)[0] AS from_label,
                    type(r) AS relation, properties(r) AS rel_props,
                    m.name AS to_name, labels(m)[0] AS to_label,
                    properties(m) AS to_props,
                    coalesce(n.is_canonical, false) AS from_canonical,
                    coalesce(m.is_canonical, false) AS to_canonical,
                    coalesce(n.priority, 0) AS from_priority
                ORDER BY (from_canonical OR to_canonical) DESC, from_priority DESC, n.name
                LIMIT $limit
            """, kw=kw, limit=self.config["max_results_per_keyword"])

            for row in rels:
                entry = {
                    "from": {"name": row["from_name"], "label": row["from_label"]},
                    "relation": row["relation"],
                    "relation_properties": row["rel_props"],
                    "to": {"name": row["to_name"], "label": row["to_label"], "properties": row["to_props"]},
                }
                if entry not in results["relationships"]:
                    results["relationships"].append(entry)

            # ========== 3. 关键词匹配下层诊断链 ==========
            diag = self._run("""
                MATCH (o:Observation)-[i:indicates]->(c:Cause)
                MATCH (a:Action)-[r:resolves]->(c)
                WHERE toLower(o.metric) CONTAINS toLower($kw)
                   OR toLower(o.condition) CONTAINS toLower($kw)
                   OR toLower(c.name) CONTAINS toLower($kw)
                   OR toLower(a.name) CONTAINS toLower($kw)
                   OR toLower(coalesce(a.strategy,'')) CONTAINS toLower($kw)
                OPTIONAL MATCH (a)-[rt:relates_to]->(component)
                OPTIONAL MATCH (component)-[alt:alternative_to]-(alternative)
                RETURN 
                    o.id AS obs_id, o.metric AS metric, o.condition AS condition,
                    c.name AS cause, i.likelihood AS likelihood,
                    i.diagnostic_check AS diagnostic_check,
                    a.name AS action, a.operation AS operation,
                    a.target AS target, a.strategy AS strategy,
                    component.name AS component_name,
                    labels(component)[0] AS component_type,
                    collect(DISTINCT alternative.name) AS alternatives
                ORDER BY 
                    CASE i.likelihood 
                        WHEN 'high' THEN 1 WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 ELSE 4 
                    END
                LIMIT $limit
            """, kw=kw, limit=self.config["max_diagnostic_chains"])

            for row in diag:
                self._add_diagnostic_chain(results, row, source="keyword")

            # ========== 3b. 关键词匹配 Strategy 节点 (2026-04 新加) ==========
            # Strategy 有 5 个文本字段：name / type / trigger_condition / content / rationale
            # 其中 content 是 JSON 字符串（troubleshooting_checklist / anti_pattern_set / parameter_preset_bundle 的结构化内容）
            # 关键词匹配后，通过 OPTIONAL MATCH 拉出这个 Strategy 关联的 upper 实体（strategy_applies_to 的目标）
            # 2026-04-23 Patch 002：canonical Strategy 优先
            strat_rows = self._run("""
                MATCH (s:Strategy)
                WHERE toLower(s.name) CONTAINS toLower($kw)
                   OR toLower(coalesce(s.type,'')) CONTAINS toLower($kw)
                   OR toLower(coalesce(s.trigger_condition,'')) CONTAINS toLower($kw)
                   OR toLower(coalesce(s.content,'')) CONTAINS toLower($kw)
                   OR toLower(coalesce(s.rationale,'')) CONTAINS toLower($kw)
                OPTIONAL MATCH (s)-[sat:strategy_applies_to]->(component)
                WITH s, collect(DISTINCT {
                        name: component.name,
                        label: labels(component)[0],
                        applicability: sat.applicability
                     }) AS applies_to,
                     coalesce(s.is_canonical, false) AS is_canonical,
                     coalesce(s.priority, 0) AS priority
                RETURN DISTINCT
                    s.id AS id, s.name AS name, s.type AS type,
                    s.trigger_condition AS trigger_condition,
                    s.content AS content, s.rationale AS rationale,
                    applies_to, is_canonical, priority
                ORDER BY is_canonical DESC, priority DESC, s.id
                LIMIT $limit
            """, kw=kw, limit=self.config["max_results_per_keyword"])

            for row in strat_rows:
                self._add_strategy(results, row, source="keyword")

        # ========== 4. 跨层反向拉取 ==========
        # 从已匹配的上层实体出发，通过 relates_to 和 strategy_applies_to 反向找关联的下层知识
        # 这样即使关键词没直接匹配到下层节点，只要上层匹配了，相关的诊断知识和 Strategy 也能被拉出来
        upper_names = [m["name"] for m in results["upper_matches"]]
        if upper_names:
            # 4a. Action → upper entity 的 relates_to 反向拉取诊断链
            cross_layer = self._run("""
                MATCH (a:Action)-[rt:relates_to]->(component)
                WHERE component.name IN $names
                MATCH (a)-[r:resolves]->(c:Cause)
                MATCH (o:Observation)-[i:indicates]->(c)
                RETURN
                    o.id AS obs_id, o.metric AS metric, o.condition AS condition,
                    c.name AS cause, i.likelihood AS likelihood,
                    i.diagnostic_check AS diagnostic_check,
                    a.name AS action, a.operation AS operation,
                    a.target AS target, a.strategy AS strategy,
                    component.name AS component_name,
                    labels(component)[0] AS component_type
                ORDER BY
                    CASE i.likelihood
                        WHEN 'high' THEN 1 WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3 ELSE 4
                    END
                LIMIT $limit
            """, names=upper_names, limit=self.config["max_diagnostic_chains"])

            for row in cross_layer:
                row.setdefault("alternatives", [])
                self._add_diagnostic_chain(results, row, source="cross-layer")

            # 4b. Strategy → upper entity 的 strategy_applies_to 反向拉取 Strategy (2026-04 新加)
            # 比如 agent 查询里匹配到了 "Static Alignment" 这个 upper 节点，
            # 即使关键词没直接命中 Strategy，也应该把连到 Static Alignment 的 Strategy 全部拉出来
            # （比如 CPA Failure Troubleshooting Priority Checklist、Static Alignment Parameter Preset Bundle 等）
            # 2026-04-23 Patch 002：跨层反拉 Strategy 也按 canonical 优先
            strat_cross = self._run("""
                MATCH (s:Strategy)-[sat:strategy_applies_to]->(component)
                WHERE component.name IN $names
                WITH s
                OPTIONAL MATCH (s)-[sat2:strategy_applies_to]->(c2)
                WITH s, collect(DISTINCT {
                        name: c2.name,
                        label: labels(c2)[0],
                        applicability: sat2.applicability
                     }) AS applies_to,
                     coalesce(s.is_canonical, false) AS is_canonical,
                     coalesce(s.priority, 0) AS priority
                RETURN DISTINCT
                    s.id AS id, s.name AS name, s.type AS type,
                    s.trigger_condition AS trigger_condition,
                    s.content AS content, s.rationale AS rationale,
                    applies_to, is_canonical, priority
                ORDER BY is_canonical DESC, priority DESC, s.id
                LIMIT $limit
            """, names=upper_names, limit=self.config["max_results_per_keyword"])

            for row in strat_cross:
                self._add_strategy(results, row, source="cross-layer")

        if as_markdown:
            return self._to_markdown(results)
        return json.dumps(results, ensure_ascii=False, indent=2)

    # ================================================================
    # Markdown 格式化（保留所有字段，但对 LLM 更可读）
    # ================================================================

    def _to_markdown(self, results: dict) -> str:
        """把 search 结果格式化成结构化 Markdown，不损失字段信息。

        优势 vs JSON：
        - 分节清晰（Upper / Relationships / Diagnostic Chains / Strategies）
        - Strategy 的 content 字段（JSON string）反序列化后渲染成 Markdown 列表
        - anti-pattern 加 ⚠ 符号强化负向信号
        - 上层实体按 label 分组，不重复打印 label 字段
        - 同等信息量下比 JSON 约省 30% tokens（去掉引号/括号/缩进）
        """
        kw = results.get("search_keywords", []) or []
        upper = results.get("upper_matches", []) or []
        rels = results.get("relationships", []) or []
        diag = results.get("diagnostic_chains", []) or []
        strats = results.get("strategies", []) or []

        out: list[str] = []
        out.append("# DKG Retrieval Results\n")
        out.append(f"**Search keywords** ({len(kw)}): {', '.join(kw) if kw else '(none)'}\n")
        out.append(f"**Summary**: {len(upper)} upper entities, {len(rels)} relationships, "
                   f"{len(diag)} diagnostic chains, {len(strats)} strategies\n")

        # ---------- 1. Upper entities ----------
        if upper:
            out.append(f"\n## 1. Upper Layer Entities ({len(upper)})\n")
            # 按 label 分组
            by_label: dict[str, list] = {}
            for e in upper:
                by_label.setdefault(e.get("label", "?"), []).append(e)
            for label in sorted(by_label.keys()):
                items = by_label[label]
                out.append(f"\n### {label} ({len(items)})\n")
                for it in items:
                    props = it.get("properties", {}) or {}
                    # 只展示有值的属性，省略 source_text（太长）
                    key_props = [(k, v) for k, v in props.items()
                                 if v is not None and v != "" and k not in ("source_text", "name")]
                    prop_str = ", ".join(f"{k}={v}" for k, v in key_props[:8])
                    out.append(f"- **{it.get('name', '(unnamed)')}**"
                               + (f" — {prop_str}" if prop_str else ""))

        # ---------- 2. Relationships ----------
        if rels:
            out.append(f"\n## 2. Relationships ({len(rels)})\n")
            for r in rels:
                fr = r.get("from", {}) or {}
                to = r.get("to", {}) or {}
                rel = r.get("relation", "?")
                rp = r.get("relation_properties", {}) or {}
                rp_compact = [f"{k}={v}" for k, v in rp.items()
                              if v is not None and v != ""][:4]
                rp_str = f" [{', '.join(rp_compact)}]" if rp_compact else ""
                out.append(f"- `{fr.get('label', '?')}:{fr.get('name', '?')}` "
                           f"—[{rel}{rp_str}]→ "
                           f"`{to.get('label', '?')}:{to.get('name', '?')}`")

        # ---------- 3. Diagnostic chains (Obs → Cause → Action) ----------
        if diag:
            out.append(f"\n## 3. Diagnostic Chains ({len(diag)})\n")
            for c in diag:
                obs = c.get("observation", {}) or {}
                action = c.get("action", {}) or {}
                comp = c.get("related_component") or {}
                alts = c.get("alternatives") or []
                likelihood = c.get("likelihood") or "?"
                metric = obs.get("metric", "?")
                cond = obs.get("condition", "?")
                out.append(f"\n### Obs: `{metric}` — {cond}")
                out.append(f"- **Cause** ({likelihood}): {c.get('cause', '?')}")
                if c.get("diagnostic_check"):
                    out.append(f"- **Check**: {c['diagnostic_check']}")
                out.append(f"- **Action**: {action.get('name', '?')}")
                op = action.get("operation")
                tgt = action.get("target")
                strat = action.get("strategy")
                if op:
                    out.append(f"  - operation: `{op}`")
                if tgt:
                    out.append(f"  - target: `{tgt}`")
                if strat:
                    out.append(f"  - strategy: {strat}")
                if comp and comp.get("name"):
                    out.append(f"- **Relates to**: {comp.get('type', '?')}:`{comp['name']}`")
                if alts:
                    out.append(f"- **Alternatives**: {', '.join(alts)}")

        # ---------- 4. Strategy nodes ----------
        if strats:
            out.append(f"\n## 4. Strategies ({len(strats)})\n")
            # 排序优先级：(1) canonical 先 (2) priority 大的先 (3) type 分组
            #   type order: anti_pattern_set 最前（负向 guardrail） → troubleshooting_checklist → preset_bundle → other
            type_order = ["anti_pattern_set", "troubleshooting_checklist",
                          "parameter_preset_bundle", None, "other"]

            def _sort_key(s):
                t = s.get("type") or "other"
                type_rank = type_order.index(t) if t in type_order else len(type_order)
                # canonical 永远排前（不管 type）；同 canonical 内按 priority DESC；再按 type 分组
                canonical_rank = 0 if s.get("is_canonical") else 1
                priority_rank = -(s.get("priority") or 0)
                return (canonical_rank, priority_rank, type_rank)

            for s in sorted(strats, key=_sort_key):
                stype = s.get("type") or "other"
                icon = {
                    "anti_pattern_set": "⚠",
                    "troubleshooting_checklist": "📋",
                    "parameter_preset_bundle": "⚙",
                }.get(stype, "•")
                # canonical 加 ⭐ 让 LLM 一眼识别"主干专家策略"
                canonical_mark = "⭐ " if s.get("is_canonical") else ""
                out.append(f"\n### {canonical_mark}{icon} [{stype}] {s.get('name', '(unnamed)')}")
                if s.get("trigger_condition"):
                    out.append(f"- **Trigger**: {s['trigger_condition']}")
                if s.get("rationale"):
                    out.append(f"- **Rationale**: {s['rationale']}")

                # content 是 JSON 字符串，按 type 渲染成 Markdown
                content_raw = s.get("content")
                if content_raw:
                    rendered = self._render_strategy_content(stype, content_raw)
                    if rendered:
                        out.append(rendered)

                applies = s.get("applies_to") or []
                if applies:
                    apply_names = [f"{a.get('label', '?')}:{a.get('name', '?')}"
                                   for a in applies if a.get("name")]
                    if apply_names:
                        out.append(f"- **Applies to**: {', '.join(apply_names)}")

        return "\n".join(out)

    def _render_strategy_content(self, stype: str, content_raw: str) -> str:
        """把 Strategy.content (JSON 字符串) 渲染成 Markdown 列表，按 type 分格式。"""
        try:
            content = json.loads(content_raw)
        except (json.JSONDecodeError, TypeError):
            # JSON 解析失败，直接当文本截断后展示
            snippet = str(content_raw)[:400]
            return f"- **Content**: {snippet}"

        if not isinstance(content, list):
            return f"- **Content**: {json.dumps(content, ensure_ascii=False)[:400]}"

        lines = []
        if stype == "anti_pattern_set":
            for i, item in enumerate(content, 1):
                if not isinstance(item, dict):
                    continue
                ap = item.get("anti_pattern") or item.get("pattern") or "(unnamed)"
                lines.append(f"- **Anti-pattern {i}**: {ap}")
                if item.get("why"):
                    lines.append(f"  - Why: {item['why']}")
                if item.get("correct_behavior"):
                    lines.append(f"  - Correct: {item['correct_behavior']}")

        elif stype == "troubleshooting_checklist":
            for item in content:
                if not isinstance(item, dict):
                    continue
                rank = item.get("rank", "?")
                check = item.get("check", "?")
                act = item.get("action_if_bad", "?")
                prop = item.get("proportion_of_failures")
                prop_str = f" (~{prop})" if prop else ""
                lines.append(f"- **[rank {rank}]**{prop_str} if `{check}` → {act}")

        elif stype == "parameter_preset_bundle":
            for item in content:
                if not isinstance(item, dict):
                    continue
                p = item.get("param", "?")
                v = item.get("value", "?")
                unit = item.get("unit") or ""
                mn = item.get("min")
                mx = item.get("max")
                range_str = ""
                if mn is not None or mx is not None:
                    range_str = f" [range {mn}–{mx}]"
                lines.append(f"- `{p}` = {v}{' ' + unit if unit else ''}{range_str}")

        else:
            # fallback
            snippet = json.dumps(content, ensure_ascii=False)[:400]
            lines.append(f"- **Content**: {snippet}")

        return "\n".join(lines)

    # ================================================================
    # 便捷方法
    # ================================================================

    def search_preprocessing_pipeline(self) -> str:
        """返回完整的预处理流程链（precedes关系）"""
        results = self._run("""
            MATCH (p:Preprocessing)-[r:precedes]->(next)
            RETURN p.name AS from_name, properties(p) AS from_props,
                   next.name AS to_name, labels(next)[0] AS to_type,
                   r.is_mandatory AS is_mandatory
        """)
        return json.dumps(results, ensure_ascii=False, indent=2)

    def search_all_upper(self) -> str:
        """返回所有上层节点和它们的关系"""
        nodes = self._run("""
            MATCH (n)
            WHERE n:Algorithm OR n:DeviceClass OR n:TraceType OR 
                  n:AttackPoint OR n:LeakageModel OR n:Preprocessing OR 
                  n:StatMethod
            RETURN n.name AS name, labels(n)[0] AS label, properties(n) AS props
        """)
        rels = self._run("""
            MATCH (n)-[r]-(m)
            WHERE (n:Algorithm OR n:DeviceClass OR n:TraceType OR 
                   n:AttackPoint OR n:LeakageModel OR n:Preprocessing OR 
                   n:StatMethod)
              AND (m:Algorithm OR m:DeviceClass OR m:TraceType OR 
                   m:AttackPoint OR m:LeakageModel OR m:Preprocessing OR 
                   m:StatMethod)
            RETURN DISTINCT
                n.name AS from_name, labels(n)[0] AS from_label,
                type(r) AS relation, properties(r) AS rel_props,
                m.name AS to_name, labels(m)[0] AS to_label
        """)
        return json.dumps({"nodes": nodes, "relationships": rels}, ensure_ascii=False, indent=2)


# ==================== 测试 ====================

if __name__ == "__main__":
    searcher = DKGSearcher(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="dkg123456"
    )
    try:
        # 用LLM实际会提取的关键词
        keywords = ["AES", "smartcard", "CPA", "power", "S-box Output first round",
                    "Hamming Weight", "Static Alignment", "Vertical Alignment",
                    "Moving Average", "Plaintext Correlation Analysis"]

        print(f"=== Test: search({keywords}) ===")
        result = searcher.search(keywords)
        data = json.loads(result)

        print(f"\nUpper matches: {len(data['upper_matches'])}")
        for m in data["upper_matches"]:
            print(f"  [{m['label']}] {m['name']}")

        print(f"\nDiagnostic chains: {len(data['diagnostic_chains'])}")
        print(f"  - from keyword: {sum(1 for c in data['diagnostic_chains'] if c.get('source') == 'keyword')}")
        print(f"  - from cross-layer: {sum(1 for c in data['diagnostic_chains'] if c.get('source') == 'cross-layer')}")

        print("\n=== Diagnostic chains detail ===")
        for c in data["diagnostic_chains"]:
            comp = c.get("related_component")
            comp_str = f" → {comp['name']}" if comp else ""
            print(f"  [{c.get('source', '?'):11s}] {c['observation']['id']}: {c['action']['name'][:70]}{comp_str}")

        # 检查关键条目是否搜到
        # 用内容匹配而不是ID匹配
        print("\n=== 内容检查 ===")
        all_actions = [c["action"]["name"].lower() for c in data["diagnostic_chains"]]
        content_checks = {
            "候选加密区间": any("candidate encryption interval" in a or "candidate interval" in a for a in all_actions),
            "不要最大峰做对齐": any("global maximum" in a or "io spike" in a or "prominent peak" in a for a in all_actions),
            "参考trace取中间": any("middle trace" in a or "middle of the dataset" in a for a in all_actions),
            "gap/high_confidence_count 优先": any("high_confidence_count" in a or "gap_pct" in a for a in all_actions),
            "滤波权重2-3": any("2-3" in a for a in all_actions),
            "S-box输出": any("s-box output" in a for a in all_actions),
            "滤波权重过大": any("smaller filter" in a or "skip filtering" in a for a in all_actions),
        }
        for desc, found in content_checks.items():
            print(f"  {'✅' if found else '❌'} {desc}")

        print(f"\nRelationships: {len(data['relationships'])}")
        print(f"Total JSON size: {len(result)} chars")
    finally:
        searcher.close()
