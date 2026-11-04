"""
Step 3.5: Unclassified Knowledge Aggregator

扫描所有 workspace/*/unclassified_knowledge_{upper,lower}.json，
按 route_to 分桶聚合，再用 LLM 做主题聚类，产出 schema 候选文档。

输出：
  workspace/_merged/schema_extension_candidates.md
  workspace/_merged/out_of_scope_summary.md

用法：
  python step3_5_unclassified_aggregator.py
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from openai import OpenAI

import yaml

from llm_utils import call_llm_with_retry


def load_config():
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def collect_unclassified(workspace_root: Path) -> dict:
    """
    扫描所有 workspace/*/unclassified_knowledge_{upper,lower}.json，
    按 route_to 分桶。
    """
    buckets: dict[str, list] = defaultdict(list)
    per_file_counts: dict[str, dict] = {}

    for ws_dir in workspace_root.iterdir():
        if not ws_dir.is_dir():
            continue
        for layer in ["upper", "lower"]:
            f = ws_dir / f"unclassified_knowledge_{layer}.json"
            if not f.exists():
                continue
            try:
                items = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"  WARN: parse failed {f}: {e}")
                continue
            if not isinstance(items, list):
                continue
            counts = defaultdict(int)
            for item in items:
                route = item.get("route_to", "unspecified")
                item["_source_workspace"] = ws_dir.name
                item["_source_layer"] = layer
                buckets[route].append(item)
                counts[route] += 1
            per_file_counts[f"{ws_dir.name}/{layer}"] = dict(counts)

    return {"buckets": dict(buckets), "per_file_counts": per_file_counts}


def summarize_out_of_scope(out_of_scope_items: list, output_path: Path):
    """out_of_scope 桶：仅统计 + 列出原文片段，不做 LLM 聚类（这些已经确认不抽）"""
    if not out_of_scope_items:
        output_path.write_text("# Out-of-scope records\n\n(none)\n", encoding="utf-8")
        return

    by_source = defaultdict(list)
    for item in out_of_scope_items:
        by_source[item.get("_source_workspace", "unknown")].append(item)

    lines = [
        "# Out-of-scope Knowledge Summary",
        "",
        f"> Total: {len(out_of_scope_items)} items from {len(by_source)} documents",
        "",
        "These are paragraphs mentioning algorithms/methods outside our current scope "
        "(RSA / ECC / PQC / stream ciphers / AEAD / template / DL / fault injection). "
        "They were intentionally NOT extracted into the KG. This file is for audit only.",
        "",
    ]
    for src, items in sorted(by_source.items()):
        lines.append(f"## {src} ({len(items)} items)")
        lines.append("")
        for item in items[:5]:
            content = (item.get("content") or "")[:150]
            reason = item.get("routing_reason", "")
            lines.append(f"- **{content}...** _{reason}_")
        if len(items) > 5:
            lines.append(f"- _... {len(items) - 5} more omitted_")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Saved: {output_path} ({len(out_of_scope_items)} items)")


def cluster_truly_unknown(truly_unknown_items: list, client: OpenAI, model: str) -> list[dict]:
    """
    用 LLM 对 truly_unknown 做主题聚类：
    返回 [{"theme": str, "proposed_node_type": str, "example_items": [...], "frequency": int}, ...]
    """
    if not truly_unknown_items:
        return []

    # 如果条目太多（>100），先按 proposed_node_type（若已有）聚，再 LLM 细化
    # 否则直接 LLM 一次性聚类
    prompt_items = []
    for i, item in enumerate(truly_unknown_items[:200]):  # 最多 200 条，避免 token 超限
        content = (item.get("content") or "")[:200]
        node_suggestion = item.get("proposed_node_type", "")
        src = item.get("_source_workspace", "")
        prompt_items.append(f"[{i}] ({src}) {content}"
                            + (f" | proposed: {node_suggestion}" if node_suggestion else ""))

    prompt = """你是侧信道分析知识图谱 schema 设计专家。下面是 {n} 条"超出当前 schema 表达能力"的知识条目，
每条被抽取时 LLM 判断无法放进现有 12 上层节点 + 4 下层节点。

请对它们做主题聚类，输出 JSON 数组。每个聚类包含：
- theme: 简洁的主题名（中文）
- proposed_node_type: 建议的新节点类型名（PascalCase 英文）
- proposed_properties: 建议的属性（字符串数组）
- example_indices: 示例条目的编号数组（最多 5 个）
- frequency: 该主题出现次数
- rationale: 为什么现有 schema 不能表达（一句话）

如果某主题条目 < 3 次，合并进更通用的类别。

约束：
- 只输出 JSON 数组，不要有 markdown 包装
- 不要提议已存在的 16 类节点
- 主题数控制在 5-15 个

条目：
{items}
""".format(n=len(prompt_items), items="\n".join(prompt_items))

    print(f"  Clustering {len(truly_unknown_items)} truly_unknown items via LLM...")
    text, _meta = call_llm_with_retry(
        client=client, model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1, max_tokens=8000,
        thinking_budget=16000, enable_thinking=True,
    )
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        clusters = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  ⚠️  LLM output JSON parse failed: {e}")
        print(f"     first 300 chars: {text[:300]}")
        return []

    return clusters if isinstance(clusters, list) else []


def write_schema_extension_candidates(
    clusters: list[dict],
    truly_unknown_items: list,
    output_path: Path,
):
    """把聚类结果写成 schema 候选 md"""
    lines = [
        "# Schema Extension Candidates (auto-generated)",
        "",
        f"> Aggregated from {len(truly_unknown_items)} `truly_unknown` items "
        f"across all workspaces.",
        "",
        "Review this file after each large batch. Each cluster is a candidate for adding "
        "a new node type (or property on existing node). Decisions tracked in "
        "`extraction/extraction_issues.md`.",
        "",
    ]
    if not clusters:
        lines.append("(no clusters found)\n")
    else:
        for i, c in enumerate(clusters, 1):
            lines.append(f"## {i}. {c.get('theme', '(unnamed)')} — "
                         f"proposed: `{c.get('proposed_node_type', '(?)')}`")
            lines.append("")
            lines.append(f"- **Frequency**: {c.get('frequency', '?')} items")
            lines.append(f"- **Why existing schema insufficient**: {c.get('rationale', '-')}")
            props = c.get("proposed_properties") or []
            lines.append(f"- **Suggested properties**: {', '.join(props) if props else '-'}")
            examples = c.get("example_indices") or []
            if examples:
                lines.append(f"- **Example items**:")
                for idx in examples[:5]:
                    if isinstance(idx, int) and 0 <= idx < len(truly_unknown_items):
                        content = (truly_unknown_items[idx].get("content") or "")[:120]
                        lines.append(f"  - `[{idx}]` {content}...")
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Saved: {output_path} ({len(clusters)} clusters)")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    config = load_config()
    base_url = config["api"]["siliconflow"]["base_url"]
    api_key = config["api"]["siliconflow"]["api_key"]
    model = "deepseek-ai/DeepSeek-V3.2"
    client = OpenAI(api_key=api_key, base_url=base_url)

    ws_root = Path("workspace")
    if not ws_root.exists():
        print(f"  ERROR: workspace not found: {ws_root}")
        return

    out_dir = ws_root / "_merged"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Step 3.5: Unclassified Knowledge Aggregator")
    print(f"{'='*60}\n")

    data = collect_unclassified(ws_root)
    buckets = data["buckets"]

    print(f"Collected items per route_to bucket:")
    for route, items in sorted(buckets.items()):
        print(f"  {route}: {len(items)} items")

    # Out-of-scope 汇总（仅统计，不做聚类）
    oos_items = buckets.get("out_of_scope", [])
    summarize_out_of_scope(oos_items, out_dir / "out_of_scope_summary.md")

    # truly_unknown 聚类（schema 候选）
    tu_items = buckets.get("truly_unknown", [])
    clusters = cluster_truly_unknown(tu_items, client, model)
    write_schema_extension_candidates(
        clusters, tu_items, out_dir / "schema_extension_candidates.md"
    )

    # 保存原始聚合快照
    snapshot = {
        "per_file_counts": data["per_file_counts"],
        "bucket_sizes": {k: len(v) for k, v in buckets.items()},
        "clusters": clusters,
    }
    (out_dir / "unclassified_snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n{'='*60}")
    print(f"Aggregation complete. See:")
    print(f"  - {out_dir / 'schema_extension_candidates.md'}")
    print(f"  - {out_dir / 'out_of_scope_summary.md'}")
    print(f"  - {out_dir / 'unclassified_snapshot.json'}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
