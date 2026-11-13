"""
DKG Neo4j Import Script

将 final_upper.json 和 final_lower.json 导入 Neo4j 图数据库。
运行前确保 Neo4j 已启动。

依赖：pip install neo4j pyyaml
"""

import json
from pathlib import Path
from neo4j import GraphDatabase
import yaml


# ==================== 配置读取 ====================

def load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


# ==================== Neo4j 连接 ====================

class DKGGraphDB:
    def __init__(self, uri, username, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        print(f"Connected to Neo4j at {uri}")

    def close(self):
        self.driver.close()

    def run(self, query, **params):
        with self.driver.session(database=self.database) as session:
            result = session.run(query, **params)
            return result.data()

    def clear_all(self):
        """清空数据库（谨慎使用）"""
        self.run("MATCH (n) DETACH DELETE n")
        print("Database cleared.")

    # ==================== 上层导入 ====================

    def import_upper_entities(self, entities: list):
        """导入上层实体节点"""
        count = 0
        for entity in entities:
            name = entity["name"]
            entity_type = entity["type"]
            props = entity.get("properties", {})

            # 跳过 "none" Countermeasure
            if entity_type == "Countermeasure" and name == "none":
                continue

            # 构建属性字符串
            props_clean = {k: v for k, v in props.items() if v is not None and k != "name"}

            query = f"""
            MERGE (n:{entity_type} {{name: $name}})
            SET n += $props
            """
            self.run(query, name=name, props=props_clean)
            count += 1

        print(f"  Imported {count} upper layer entities")

    def import_upper_relationships(self, relationships: list, name_to_type: dict | None = None):
        """导入上层关系。

        ``name_to_type`` 是 ``{entity_name: entity_type}`` 映射（由 entities 列表
        预先构建）。MATCH 时用它把 label 也带上，避免同名节点跨 label 时
        ``MERGE`` 把一条 JSON 边复制成多条 Neo4j 边。
        """
        if name_to_type is None:
            name_to_type = {}
        count = 0
        skipped_missing = 0
        for rel in relationships:
            subject = rel["subject"]
            relation = rel["relation"]
            obj = rel["object"]
            props = rel.get("properties", {})

            # 跳过涉及 "none" Countermeasure 的关系
            if subject == "none" or obj == "none":
                continue

            # 清理属性：移除None值，列表转为JSON字符串
            props_clean = {}
            for k, v in props.items():
                if v is None:
                    continue
                if isinstance(v, list):
                    props_clean[k] = json.dumps(v, ensure_ascii=False)
                elif isinstance(v, (int, float, bool, str)):
                    props_clean[k] = v

            # 用 name_to_type 限定 label,避免跨 label 同名节点造成重复边
            s_label = name_to_type.get(subject)
            o_label = name_to_type.get(obj)
            if not s_label or not o_label:
                skipped_missing += 1
                continue
            query = f"""
            MATCH (a:{s_label} {{name: $subject}})
            MATCH (b:{o_label} {{name: $object}})
            MERGE (a)-[r:{relation}]->(b)
            SET r += $props
            """
            try:
                self.run(query, subject=subject, object=obj, props=props_clean)
                count += 1
            except Exception as e:
                print(f"    WARNING: Failed to create {subject} -[{relation}]-> {obj}: {e}")

        print(f"  Imported {count} upper layer relationships"
              + (f"  (skipped {skipped_missing} with missing entity)" if skipped_missing else ""))

    # ==================== 下层导入 ====================

    def import_lower_observations(self, observations: list):
        """导入下层 Observation 节点"""
        for obs in observations:
            query = """
            MERGE (n:Observation {id: $id})
            SET n.metric = $metric, n.condition = $condition
            """
            self.run(query, id=obs["id"], metric=obs["metric"], condition=obs["condition"])
        print(f"  Imported {len(observations)} Observation nodes")

    def import_lower_causes(self, causes: list):
        """导入下层 Cause 节点"""
        for cause in causes:
            query = """
            MERGE (n:Cause {name: $name})
            """
            self.run(query, name=cause["name"])
        print(f"  Imported {len(causes)} Cause nodes")

    def import_lower_actions(self, actions: list):
        """导入下层 Action 节点"""
        for action in actions:
            props = {
                "operation": action.get("operation", ""),
                "target": action.get("target", ""),
                "strategy": action.get("strategy", ""),
            }
            query = """
            MERGE (n:Action {name: $name})
            SET n += $props
            """
            self.run(query, name=action["name"], props=props)
        print(f"  Imported {len(actions)} Action nodes")

    def import_lower_indicates(self, indicates: list):
        """导入 indicates 关系：Observation → Cause"""
        count = 0
        for ind in indicates:
            props = {
                "likelihood": ind.get("likelihood", ""),
                "diagnostic_check": ind.get("diagnostic_check", ""),
                "source_text": ind.get("source_text", ""),
            }
            source_papers = ind.get("source_papers", [])
            if source_papers:
                props["source_papers"] = json.dumps(source_papers, ensure_ascii=False)

            query = """
            MATCH (o:Observation {id: $obs_id})
            MATCH (c:Cause {name: $cause_name})
            MERGE (o)-[r:indicates]->(c)
            SET r += $props
            """
            try:
                self.run(query, obs_id=ind["observation_id"], cause_name=ind["cause_name"], props=props)
                count += 1
            except Exception as e:
                print(f"    WARNING: indicates failed: {e}")
        print(f"  Imported {count} indicates relationships")

    def import_lower_resolves(self, resolves: list):
        """导入 resolves 关系：Action → Cause"""
        count = 0
        for res in resolves:
            props = {
                "source_text": res.get("source_text", ""),
            }
            source_papers = res.get("source_papers", [])
            if source_papers:
                props["source_papers"] = json.dumps(source_papers, ensure_ascii=False)

            query = """
            MATCH (a:Action {name: $action_name})
            MATCH (c:Cause {name: $cause_name})
            MERGE (a)-[r:resolves]->(c)
            SET r += $props
            """
            try:
                self.run(query, action_name=res["action_name"], cause_name=res["cause_name"], props=props)
                count += 1
            except Exception as e:
                print(f"    WARNING: resolves failed: {e}")
        print(f"  Imported {count} resolves relationships")

    def import_lower_strategies(self, strategies: list):
        """
        导入下层 Strategy 节点（2026-04 新加）。

        Strategy 有四种 type:
          - troubleshooting_checklist   (有序排查清单)
          - anti_pattern_set            (反面规则集)
          - parameter_preset_bundle     (参数预设组合)
          - canonical_pipeline_principle (规范主流程原则)

        除 content/rationale 外，``is_canonical`` (bool) 和 ``priority`` (int)
        被 agent 在 ``kg_search`` 检索时用来排序，必须如实写入 Neo4j。

        content 字段是 JSON 字符串（由 Step 2 保证扁平化），直接作为 Neo4j 的
        string property 存储。agent 查询时按需反序列化 JSON 即可恢复结构。
        """
        count = 0
        for strat in strategies:
            strat_id = strat.get("id", "")
            if not strat_id:
                print(f"    WARNING: strategy missing id, skipping: {strat.get('name', '?')}")
                continue

            # content 应该已经是 JSON string。保险起见：如果是 dict/list，转成 string
            content = strat.get("content", "")
            if isinstance(content, (dict, list)):
                content = json.dumps(content, ensure_ascii=False)

            query = """
            MERGE (n:Strategy {id: $id})
            SET n.name = $name,
                n.type = $type,
                n.trigger_condition = $trigger_condition,
                n.content = $content,
                n.rationale = $rationale,
                n.is_canonical = $is_canonical,
                n.priority = $priority
            """
            try:
                self.run(
                    query,
                    id=strat_id,
                    name=strat.get("name", ""),
                    type=strat.get("type", ""),
                    trigger_condition=strat.get("trigger_condition", ""),
                    content=content,
                    rationale=strat.get("rationale", ""),
                    is_canonical=bool(strat.get("is_canonical", False)),
                    priority=int(strat.get("priority", 50)),
                )
                count += 1
            except Exception as e:
                print(f"    WARNING: Strategy import failed for {strat_id}: {e}")
        print(f"  Imported {count} Strategy nodes")

    def import_cross_layer_links(self, relates_to: list, name_to_type: dict | None = None):
        """导入 relates_to 关系：Action → 上层实体（跨层连接）.

        ``name_to_type`` 是上层 ``{entity_name: entity_type}`` 映射，用来限定
        target 的 label，避免跨 label 同名节点造成边复制。
        """
        if name_to_type is None:
            name_to_type = {}
        count = 0
        skipped_missing = 0
        for link in relates_to:
            action_name = link.get("action_name", "")
            entity_name = link.get("entity_name", "")
            role = link.get("role", "")

            e_label = name_to_type.get(entity_name)
            if not e_label:
                skipped_missing += 1
                continue
            query = f"""
            MATCH (a:Action {{name: $action_name}})
            MATCH (e:{e_label} {{name: $entity_name}})
            MERGE (a)-[r:relates_to]->(e)
            SET r.role = $role
            """
            try:
                self.run(query, action_name=action_name, entity_name=entity_name, role=role)
                count += 1
            except Exception as e:
                print(f"    WARNING: relates_to failed: {action_name} → {entity_name}: {e}")
        print(f"  Imported {count} cross-layer relates_to links"
              + (f"  (skipped {skipped_missing} with missing upper entity)" if skipped_missing else ""))

    def import_strategy_applies_to(self, edges: list, name_to_type: dict | None = None):
        """
        导入 strategy_applies_to 跨层边：Strategy → 上层实体（2026-04 新加）。

        ``name_to_type`` 是上层 ``{entity_name: entity_type}`` 映射，用来限定
        target 的 label，避免跨 label 同名节点造成边复制。

        Strategy 侧按 name 匹配（因为 final_lower.json 里 strategy_applies_to 边只
        有 strategy_name 字段，没有 strategy_id）。Step 3 的 (name, type) 去重保证
        Strategy name 在同一 KG 里唯一。
        """
        if name_to_type is None:
            name_to_type = {}
        count = 0
        skipped_missing = 0
        for edge in edges:
            strategy_name = edge.get("strategy_name", "")
            target_entity = edge.get("target_entity", "")

            if not strategy_name or not target_entity:
                continue

            props = {
                "applicability": edge.get("applicability", "general"),
                "condition": edge.get("condition") or "",
                "source_text": edge.get("source_text", ""),
            }
            source_papers = edge.get("source_papers", [])
            if source_papers:
                props["source_papers"] = json.dumps(source_papers, ensure_ascii=False)

            e_label = name_to_type.get(target_entity)
            if not e_label:
                skipped_missing += 1
                continue
            query = f"""
            MATCH (s:Strategy {{name: $strategy_name}})
            MATCH (e:{e_label} {{name: $target_entity}})
            MERGE (s)-[r:strategy_applies_to]->(e)
            SET r += $props
            """
            try:
                self.run(query, strategy_name=strategy_name, target_entity=target_entity, props=props)
                count += 1
            except Exception as e:
                print(f"    WARNING: strategy_applies_to failed: {strategy_name} → {target_entity}: {e}")
        print(f"  Imported {count} strategy_applies_to cross-layer links"
              + (f"  (skipped {skipped_missing} with missing upper entity)" if skipped_missing else ""))

    # ==================== 创建索引 ====================

    def create_indexes(self):
        """创建索引加速查询"""
        indexes = [
            # 上层原有节点
            "CREATE INDEX IF NOT EXISTS FOR (n:Algorithm) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:DeviceClass) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:TraceType) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Countermeasure) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:AttackPoint) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:LeakageModel) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Preprocessing) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:StatMethod) ON (n.name)",
            # 上层控制流节点（2026-04-17 扩边）
            "CREATE INDEX IF NOT EXISTS FOR (n:Pipeline) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:DiagnosticMethod) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:ValidationMethod) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:RecoveryMethod) ON (n.name)",
            # 下层 3 个原有节点
            "CREATE INDEX IF NOT EXISTS FOR (n:Observation) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Cause) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Action) ON (n.name)",
            # 下层第 4 个节点（Strategy，2026-04 新加）
            # Strategy 同时按 id 和 name 查询，两个都建索引
            "CREATE INDEX IF NOT EXISTS FOR (n:Strategy) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Strategy) ON (n.name)",
        ]
        for idx in indexes:
            try:
                self.run(idx)
            except Exception:
                pass
        print("  Indexes created")


# ==================== 主函数 ====================

def main():
    # ========================================
    # ========== 在这里修改配置 ==========
    # ========================================

    # --- Neo4j 配置 ---
    neo4j_uri = "bolt://localhost:7687"
    neo4j_username = "neo4j"
    neo4j_password = "dkg123456"
    neo4j_database = "neo4j"

    # --- 输入文件 ---
    # 默认读 round1/ 子目录（阶段 12 Round 1 产出）。
    # 阶段 11 frozen 基线仍在 upper_layer/final_upper.json / lower_layer/final_lower.json（根路径）。
    # 想导入阶段 11 基线：改成 "upper_layer/final_upper.json" / "lower_layer/final_lower.json"。
    upper_path = "upper_layer/round1/final_upper.json"
    lower_path = "lower_layer/round1/final_lower.json"

    # --- 是否清空数据库（首次导入设为True）---
    clear_database = True

    # --- 是否导入上层/下层 ---
    import_upper = True
    import_lower = True

    # ========================================
    # ========== 以下不需要修改 ==========
    # ========================================

    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # 上一层是 knowledge/ 目录
    os.chdir("..")

    # 连接 Neo4j
    db = DKGGraphDB(neo4j_uri, neo4j_username, neo4j_password, neo4j_database)

    try:
        # 清空
        if clear_database:
            print("\nClearing database...")
            db.clear_all()

        # 创建索引
        print("\nCreating indexes...")
        db.create_indexes()

        # 导入上层
        if import_upper:
            print(f"\n{'='*60}")
            print("Importing Upper Layer")
            print(f"{'='*60}")

            upper_data = json.loads(Path(upper_path).read_text(encoding="utf-8"))
            db.import_upper_entities(upper_data.get("entities", []))
            # build name -> type map for label-aware MATCH in relationship imports
            upper_name_to_type = {e["name"]: e["type"] for e in upper_data.get("entities", [])
                                  if e.get("name") and e.get("type")
                                  and not (e["type"] == "Countermeasure" and e["name"] == "none")}
            db.import_upper_relationships(upper_data.get("relationships", []), upper_name_to_type)

        # 导入下层
        if import_lower:
            print(f"\n{'='*60}")
            print("Importing Lower Layer")
            print(f"{'='*60}")

            lower_data = json.loads(Path(lower_path).read_text(encoding="utf-8"))
            # 诊断三元组节点
            db.import_lower_observations(lower_data.get("observations", []))
            db.import_lower_causes(lower_data.get("causes", []))
            db.import_lower_actions(lower_data.get("actions", []))
            # Strategy 节点（2026-04 新加）
            db.import_lower_strategies(lower_data.get("strategies", []))
            # 下层内部关系
            db.import_lower_indicates(lower_data.get("indicates", []))
            db.import_lower_resolves(lower_data.get("resolves", []))
            # 跨层关系（用 upper_name_to_type 限定 label）
            db.import_cross_layer_links(lower_data.get("relates_to", []), upper_name_to_type)
            # Strategy 跨层关系（2026-04 新加）
            db.import_strategy_applies_to(lower_data.get("strategy_applies_to", []), upper_name_to_type)

        # 统计
        print(f"\n{'='*60}")
        print("Import Summary")
        print(f"{'='*60}")

        stats = db.run("""
        MATCH (n) 
        RETURN labels(n)[0] AS label, count(n) AS count 
        ORDER BY count DESC
        """)
        print("\nNode counts:")
        for s in stats:
            print(f"  {s['label']}: {s['count']}")

        rel_stats = db.run("""
        MATCH ()-[r]->() 
        RETURN type(r) AS type, count(r) AS count 
        ORDER BY count DESC
        """)
        print("\nRelationship counts:")
        for s in rel_stats:
            print(f"  {s['type']}: {s['count']}")

    finally:
        db.close()
        print("\nDone!")


if __name__ == "__main__":
    main()
