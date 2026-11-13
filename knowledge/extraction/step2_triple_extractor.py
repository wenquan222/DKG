"""
DKG Step 2: 三元组抽取 (Triple Extractor)

从Step 1的结构化描述中抽取知识图谱的实体和关系三元组。
上层：8种节点 + 7种关系
下层：3种节点 + 2种关系
"""

import json
import os
import sys
from pathlib import Path
from openai import OpenAI


import yaml

# Windows GBK 默认 stdout 碰到 emoji 会崩，强制 utf-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

def load_config():
    """从项目根目录读取config.yaml"""
    # 从extraction/目录往上找两层到DKG/
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))

# ==================== LLM 调用 ====================

from llm_utils import call_llm_with_retry, scope_filter_upper


def call_llm(content: str, prompt_template: str, client: OpenAI, model: str, max_tokens: int = 16000) -> str:
    """thinking on + retry/backoff + usage 日志"""
    prompt = prompt_template.replace("{content}", content)
    content_text, _meta = call_llm_with_retry(
        client=client, model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1, max_tokens=max_tokens,
        thinking_budget=16000, enable_thinking=True,
    )
    return content_text


def parse_json_response(response_text: str) -> dict | list:
    text = response_text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)


# ==================== 抽取逻辑 ====================

def run_extraction(
    step1_output: str,
    prompt_path: str,
    client: OpenAI,
    model: str,
    workspace_dir: str | None = None,
    layer: str | None = None,
) -> dict:
    """
    用指定的prompt对Step 1的输出进行三元组抽取。

    Args:
        step1_output: Step 1输出的JSON字符串
        prompt_path: prompt文件路径
        workspace_dir / layer: 若提供,会把LLM原始响应保存到
            {workspace_dir}/step2_{layer}_raw_response.txt,便于 JSON
            解析失败时事后定位问题。
    """
    prompt_template = Path(prompt_path).read_text(encoding="utf-8")

    print(f"  Prompt: {prompt_path}")
    print(f"  Input length: {len(step1_output)} chars")
    print(f"  Calling LLM...")

    response_text = call_llm(step1_output, prompt_template, client, model)

    print(f"  Response length: {len(response_text)} chars")

    # 无论成功还是失败,都先把 LLM 原始响应落盘,避免失败时一次昂贵调用白烧
    raw_path = None
    if workspace_dir and layer:
        raw_path = f"{workspace_dir}/step2_{layer}_raw_response.txt"
        Path(raw_path).parent.mkdir(parents=True, exist_ok=True)
        Path(raw_path).write_text(response_text, encoding="utf-8")
        print(f"  Raw response saved: {raw_path}")

    try:
        result = parse_json_response(response_text)
    except json.JSONDecodeError as e:
        # 打印失败位置的 ±200 字符上下文,方便定位
        pos = getattr(e, "pos", 0)
        start = max(0, pos - 200)
        end = min(len(response_text), pos + 200)
        context = response_text[start:end]
        print(f"  ❌ JSON parse error: {e.msg}")
        print(f"     position: char {pos} (line {e.lineno}, col {e.colno})")
        print(f"  ── Context (±200 chars around error) ──")
        for line in context.splitlines():
            print(f"     {line}")
        print(f"  ── end of context ──")
        print(f"  💡 Full raw response at: {raw_path or '(not saved)'}")
        raise

    # 统计输出规模(按层分类打印)
    if isinstance(result, dict):
        if "entities" in result:
            # Upper 层:细分 Pipeline / 其他 entities, consists_of / 其他 relationships
            entities = result.get("entities", [])
            relationships = result.get("relationships", [])
            n_pipeline = sum(1 for e in entities if e.get("type") == "Pipeline")
            n_consists_of = sum(1 for r in relationships if r.get("relation") == "consists_of")
            n_other_entities = len(entities) - n_pipeline
            n_other_rels = len(relationships) - n_consists_of
            print(f"  Extracted entities: {len(entities)} total "
                  f"({n_other_entities} standard + {n_pipeline} Pipeline)")
            print(f"  Extracted relationships: {len(relationships)} total "
                  f"({n_other_rels} standard + {n_consists_of} consists_of)")
        elif "observations" in result:
            # Lower 层:加 strategies 和 strategy_applies_to 的计数
            n_obs = len(result.get("observations", []))
            n_causes = len(result.get("causes", []))
            n_actions = len(result.get("actions", []))
            n_strategies = len(result.get("strategies", []))
            n_indicates = len(result.get("indicates", []))
            n_resolves = len(result.get("resolves", []))
            n_sat = len(result.get("strategy_applies_to", []))
            print(f"  Extracted nodes: {n_obs} obs, {n_causes} causes, "
                  f"{n_actions} actions, {n_strategies} strategies")
            print(f"  Extracted relations: {n_indicates} indicates, "
                  f"{n_resolves} resolves, {n_sat} strategy_applies_to")

    return result


# ==================== 保存结果 ====================

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

    import argparse
    import hashlib

    # CLI（和 step1 一致）
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", default="0/1",
                        help="I/N 分片（按 workspace stem hash 分派），默认 0/1 单进程全跑")
    parser.add_argument("--api-key-index", type=int, default=0,
                        help="siliconflow key 编号：0=api_key, 1=api_key_2, 2=api_key_3, 3=api_key_4")
    args = parser.parse_args()
    try:
        shard_i, shard_n = (int(x) for x in args.shard.split("/"))
        assert 0 <= shard_i < shard_n
    except Exception:
        print(f"ERROR: --shard 格式应为 I/N，实际 {args.shard}")
        return

    # --- 自动扫描 workspace/* 里含有 step1_*.json 的目录 ---
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ws_root = Path("workspace")
    if not ws_root.exists():
        print(f"  ERROR: workspace directory not found: {ws_root}")
        return
    workspaces = sorted(
        str(p) for p in ws_root.iterdir()
        if p.is_dir() and (
            (p / "step1_upper.json").exists() or (p / "step1_lower.json").exists()
        )
    )
    # 分片
    if shard_n > 1:
        before = len(workspaces)
        workspaces = [
            w for w in workspaces
            if (int(hashlib.md5(Path(w).name.encode()).hexdigest(), 16) % shard_n) == shard_i
        ]
        print(f"[shard] {shard_i}/{shard_n}: {len(workspaces)}/{before} workspaces assigned")

    print(f"Found {len(workspaces)} workspaces with step1 output:")
    for w in workspaces[:10]:
        print(f"  - {w}")
    if len(workspaces) > 10:
        print(f"  ... and {len(workspaces) - 10} more")

    # --- LLM 配置 ---
    config = load_config()

    # ---- 配置 A: SiliconFlow + Pro/DeepSeek-V3.2 ----
    base_url = config["api"]["siliconflow"]["base_url"]
    key_field = "api_key" if args.api_key_index == 0 else f"api_key_{args.api_key_index + 1}"
    if key_field not in config["api"]["siliconflow"]:
        print(f"ERROR: config.api.siliconflow 里没有 {key_field}")
        return
    api_key = config["api"]["siliconflow"][key_field]
    print(f"[config] using siliconflow.{key_field}")
    model = "deepseek-ai/DeepSeek-V3.2"

    # ---- 配置 B: OpenRouter + Claude Opus 4.6 (贵，最终版抽取用) ----
    # api_key = config["api"]["openrouter"]["api_key"]
    # base_url = config["api"]["openrouter"]["base_url"]
    # model = "anthropic/claude-opus-4.6"

    # --- Prompt 文件路径 ---
    prompt_upper = "prompts/step2_upper.txt"
    prompt_lower = "prompts/step2_lower.txt"

    # --- 是否跑上层/下层 ---
    run_upper = True
    run_lower = True

    # ========================================
    # ========== 以下不需要修改 ==========
    # ========================================

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    for workspace_dir in workspaces:
        workspace_name = Path(workspace_dir).name

        # 按层独立增量 skip：某层 step2 json 已存在则跳过（删对应文件可重跑）
        upper_done = Path(f"{workspace_dir}/step2_upper.json").exists()
        lower_done = Path(f"{workspace_dir}/step2_lower.json").exists()
        if (not run_upper or upper_done) and (not run_lower or lower_done):
            print(f"  [skip-existing] {workspace_name}: both step2 layers done")
            continue

        print(f"\n{'='*60}")
        print(f"Step 2: Triple Extraction")
        print(f"Workspace: {workspace_dir}")
        print(f"{'='*60}")

        # 检查workspace是否存在
        if not Path(workspace_dir).exists():
            print(f"  WARNING: Workspace not found, skipping")
            continue

        # 上层抽取
        if run_upper and not upper_done:
            step1_upper_path = f"{workspace_dir}/step1_upper.json"
            if Path(step1_upper_path).exists():
                print(f"\n--- Upper Layer ---")
                step1_data = Path(step1_upper_path).read_text(encoding="utf-8")
                parsed = json.loads(step1_data)

                # 新格式: {"specific_experiments": [...], "canonical_pipelines": [...]}
                # 旧格式兼容: 裸 list
                if isinstance(parsed, dict):
                    n_exp = len(parsed.get("specific_experiments", []))
                    n_pipe = len(parsed.get("canonical_pipelines", []))
                    is_empty = (n_exp == 0 and n_pipe == 0)
                    print(f"  Input: {n_exp} specific_experiments, {n_pipe} canonical_pipelines")
                else:
                    # 旧格式：裸 list
                    is_empty = (parsed == [] or parsed is None)
                    if not is_empty:
                        print(f"  ⚠️ Legacy list format detected (expected dict). Input: {len(parsed)} records")

                if is_empty:
                    print(f"  Step 1 upper output is empty, saving empty result")
                    save_json({"entities": [], "relationships": []},
                             f"{workspace_dir}/step2_upper.json")
                else:
                    try:
                        upper_result = run_extraction(
                            step1_data, prompt_upper, client, model,
                            workspace_dir=workspace_dir, layer="upper"
                        )
                        # Scope post-filter: 白名单兜底过滤越界 Algorithm / StatMethod
                        if isinstance(upper_result, dict) and "entities" in upper_result:
                            before_e = len(upper_result.get("entities", []))
                            before_r = len(upper_result.get("relationships", []))
                            kept_e, kept_r, warns = scope_filter_upper(
                                upper_result["entities"],
                                upper_result.get("relationships", []),
                            )
                            if warns:
                                print(f"  ⚠️  Scope filter dropped "
                                      f"{before_e - len(kept_e)} entities, "
                                      f"{before_r - len(kept_r)} relationships:")
                                for w in warns[:10]:
                                    print(f"      {w}")
                                if len(warns) > 10:
                                    print(f"      ... and {len(warns) - 10} more")
                            upper_result["entities"] = kept_e
                            upper_result["relationships"] = kept_r
                            upper_result["scope_filter_warnings"] = warns
                        save_json(upper_result, f"{workspace_dir}/step2_upper.json")
                    except Exception as e:
                        print(f"  ERROR: {e}")
            else:
                print(f"  step1_upper.json not found, skipping upper layer")

        # 下层抽取
        if run_lower and not lower_done:
            step1_lower_path = f"{workspace_dir}/step1_lower.json"
            if Path(step1_lower_path).exists():
                print(f"\n--- Lower Layer ---")
                step1_data = Path(step1_lower_path).read_text(encoding="utf-8")
                parsed = json.loads(step1_data)

                # 新格式: {"diagnostic_triples": [...], "strategies": [...]}
                # 旧格式兼容: 裸 list
                if isinstance(parsed, dict):
                    n_tri = len(parsed.get("diagnostic_triples", []))
                    n_strat = len(parsed.get("strategies", []))
                    is_empty = (n_tri == 0 and n_strat == 0)
                    print(f"  Input: {n_tri} diagnostic_triples, {n_strat} strategies")
                else:
                    # 旧格式：裸 list
                    is_empty = (parsed == [] or parsed is None)
                    if not is_empty:
                        print(f"  ⚠️ Legacy list format detected (expected dict). Input: {len(parsed)} records")

                if is_empty:
                    print(f"  Step 1 lower output is empty, saving empty result")
                    save_json({
                        "observations": [], "causes": [], "actions": [], "strategies": [],
                        "indicates": [], "resolves": [], "strategy_applies_to": []
                    }, f"{workspace_dir}/step2_lower.json")
                else:
                    try:
                        lower_result = run_extraction(
                            step1_data, prompt_lower, client, model,
                            workspace_dir=workspace_dir, layer="lower"
                        )
                        save_json(lower_result, f"{workspace_dir}/step2_lower.json")
                    except Exception as e:
                        print(f"  ERROR: {e}")
            else:
                print(f"  step1_lower.json not found, skipping lower layer")

        print(f"\n{'='*60}")
        print(f"Done: {workspace_name}")
        print(f"{'='*60}")

    print(f"\n\nAll workspaces processed!")


if __name__ == "__main__":
    main()