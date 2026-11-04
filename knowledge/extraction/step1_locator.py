"""
DKG Step 1: 定位与重写 (Section Locator + Rewriter)

从原始文档中定位实验/经验描述，按统一模板重写为结构化JSON。
分别使用上层prompt和下层prompt，输出两份JSON文件。
"""

import json
import os
import sys
from pathlib import Path
from openai import OpenAI


import yaml

# Windows 默认 stdout 是 GBK，打印 emoji (⚠️ ✓) 会 UnicodeEncodeError 然后把整个处理流程打断
# 这里强制 utf-8，让 emoji 打印不崩。
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

# ==================== 文件读取 ====================

def read_docx(file_path: str) -> str:
    """从Word文档提取纯文本"""
    from docx import Document
    doc = Document(file_path)
    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def read_pdf(file_path: str) -> str:
    """从PDF提取纯文本"""
    import fitz
    doc = fitz.open(file_path)
    pages = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages.append(text.strip())
    doc.close()
    return "\n".join(pages)


def read_file(file_path: str) -> str:
    """根据扩展名自动选择读取方式"""
    ext = Path(file_path).suffix.lower()
    if ext == ".docx":
        return read_docx(file_path)
    elif ext == ".pdf":
        return read_pdf(file_path)
    elif ext in (".txt", ".md"):
        return Path(file_path).read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ==================== LLM 调用 ====================

from llm_utils import (
    call_llm_with_retry,
    estimate_tokens,
    chunk_markdown_by_sections,
    SAFE_INPUT_TOKENS,
)


def call_llm(content: str, prompt_template: str, client: OpenAI, model: str, max_tokens: int = 16000) -> str:
    """
    调用 LLM，返回原始文本响应。
    已启用 thinking 模式 + retry/backoff + usage 日志。
    """
    prompt = prompt_template.replace("{content}", content)
    content_text, _meta = call_llm_with_retry(
        client=client,
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=max_tokens,
        thinking_budget=16000,
        enable_thinking=True,
    )
    return content_text


def parse_json_response(response_text: str) -> list | dict:
    """从LLM响应中解析JSON，处理可能的markdown包裹 + 常见非严格 JSON 修复"""
    import re as _re
    text = response_text.strip()

    # 去掉markdown代码块
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # 简单修复：去掉尾逗号
        fixed = _re.sub(r",\s*([\]}])", r"\1", text)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        # 打印失败位置上下文帮助调试
        pos = getattr(e, "pos", 0)
        start = max(0, pos - 250)
        end = min(len(text), pos + 250)
        print(f"  ❌ JSON parse failed at char {pos} (line {e.lineno}, col {e.colno})")
        print(f"  ── Context (±250 chars) ──")
        for line in text[start:end].splitlines():
            print(f"     {line}")
        print(f"  ── end of context ──")
        raise


# ==================== 单层抽取 ====================

def run_extraction(content: str, prompt_path: str, client: OpenAI, model: str) -> list | dict:
    """
    用指定的prompt对文本进行抽取。
    若文档 token 数超 SAFE_INPUT_TOKENS，自动按 ## 切块后逐块抽取，最后合并。

    content: 文档文本
    prompt_path: prompt文件路径
    """
    prompt_template = Path(prompt_path).read_text(encoding="utf-8")

    print(f"  Prompt: {prompt_path}")
    content_tokens = estimate_tokens(content)
    print(f"  Content: {len(content)} chars (~{content_tokens} tokens)")

    # 超大文档：切块 + 合并
    if content_tokens > SAFE_INPUT_TOKENS:
        print(f"  ⚠️  Document exceeds safe input budget ({SAFE_INPUT_TOKENS} tokens). "
              f"Chunking by sections...")
        chunks = chunk_markdown_by_sections(content)
        print(f"  → Split into {len(chunks)} chunks: "
              f"{[estimate_tokens(c) for c in chunks]}")
        chunk_results: list[dict] = []
        for idx, chunk_text in enumerate(chunks, 1):
            print(f"  [chunk {idx}/{len(chunks)}] {estimate_tokens(chunk_text)} tokens, "
                  f"calling {model}...")
            response_text = call_llm(chunk_text, prompt_template, client, model)
            try:
                chunk_result = parse_json_response(response_text)
            except (json.JSONDecodeError, Exception) as e:
                print(f"  [chunk {idx}] parse failed: {e}")
                print(f"    Raw tail: ...{response_text[-200:]}")
                continue
            chunk_results.append(chunk_result if isinstance(chunk_result, dict) else {"records": chunk_result})

        return _merge_chunk_results(chunk_results)

    # 正常：单次调用
    print(f"  Calling {model}...")
    response_text = call_llm(content, prompt_template, client, model)
    print(f"  Response length: {len(response_text)} chars")

    try:
        result = parse_json_response(response_text)
    except (json.JSONDecodeError, Exception) as e:
        print(f"  ERROR: {e}")
        print(f"  Raw response tail: ...{response_text[-200:]}")
        # 失败时把 raw response 存盘供事后分析
        debug_path = Path(prompt_path).parent.parent / f"_last_parse_fail_{Path(prompt_path).stem}.txt"
        try:
            debug_path.write_text(response_text, encoding="utf-8")
            print(f"  Raw response saved for debug: {debug_path}")
        except Exception:
            pass
        raise

    # 统计
    if isinstance(result, list):
        print(f"  Extracted: {len(result)} records")
    elif isinstance(result, dict):
        print(f"  Extracted: {len(result.keys())} top-level keys")

    return result


def _merge_chunk_results(chunk_results: list[dict]) -> dict:
    """合并多个 chunk 的抽取结果（按 list 字段拼接）"""
    if not chunk_results:
        return {}
    merged: dict = {}
    for cr in chunk_results:
        for key, val in cr.items():
            if isinstance(val, list):
                merged.setdefault(key, []).extend(val)
            else:
                merged.setdefault(key, val)
    # 为 list 字段去重 id 冲突（在同一 key 下，自动加 chunk 前缀）
    for key in ["specific_experiments", "canonical_pipelines", "diagnostic_triples", "strategies"]:
        if key in merged and isinstance(merged[key], list):
            seen_ids: dict[str, int] = {}
            for item in merged[key]:
                for id_field in ["experiment_id", "pipeline_id", "experience_id", "strategy_id"]:
                    if id_field in item and item[id_field]:
                        old = item[id_field]
                        cnt = seen_ids.get(old, 0)
                        if cnt > 0:
                            item[id_field] = f"{old}_c{cnt}"
                        seen_ids[old] = cnt + 1
    return merged


# ==================== 保存结果 ====================

def save_json(data, output_path: str):
    """保存JSON到文件"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"  Saved: {output_path}")


# ==================== 辅助函数 ====================

def _check_unclassified(result, workspace_dir, layer):
    """检查并保存Step 1中schema外的知识，按route_to分桶"""
    if isinstance(result, list):
        print(f"  ⚠️ WARNING: LLM returned list instead of dict for {layer}. "
              f"unclassified_knowledge is unreachable — check prompt format.")
        return

    if not isinstance(result, dict):
        print(f"  ⚠️ WARNING: unexpected result type ({type(result).__name__}) for {layer}")
        return

    unclassified = result.get("unclassified_knowledge", [])

    if not unclassified:
        print(f"  ✓ All knowledge fits schema ({layer})")
        return

    # 按 route_to 分桶统计
    buckets: dict[str, list] = {}
    for item in unclassified:
        route = item.get("route_to", "unspecified")
        buckets.setdefault(route, []).append(item)

    # 先落盘，再打印（防止 print 在某些 locale 下抛 UnicodeEncodeError 导致未保存）
    unc_path = f"{workspace_dir}/unclassified_knowledge_{layer}.json"
    with open(unc_path, "w", encoding="utf-8") as f:
        json.dump(unclassified, f, ensure_ascii=False, indent=2)

    print(f"  [!] Found {len(unclassified)} unclassified knowledge items ({layer}):")
    for route, items in buckets.items():
        print(f"    [{route}] {len(items)} items:")
        for item in items[:3]:  # 每类最多打印 3 条摘要
            content_preview = (item.get("content") or "")[:80]
            reason = item.get("routing_reason", item.get("why_excluded", ""))
            try:
                print(f"      - {content_preview}...")
                print(f"        reason: {reason}")
            except UnicodeEncodeError:
                print(f"      - (unicode-encode-error preview suppressed)")
        if len(items) > 3:
            print(f"      ... and {len(items) - 3} more")
    print(f"  Saved to {unc_path}")


def _prefix_record_ids(result: dict, doc_stem: str, layer: str):
    """给每条 record 的 id 加文档前缀，避免跨文档 id 冲突（exp_001 → exp_PAP-04_001）"""
    if not isinstance(result, dict):
        return
    id_fields = {
        "specific_experiments": "experiment_id",
        "canonical_pipelines": "pipeline_id",
        "diagnostic_triples": "experience_id",
        "strategies": "strategy_id",
    }
    short_stem = doc_stem
    # 把太长的 stem 截断成 "CAT-NN" 前 6 字符作为前缀
    if "-" in doc_stem:
        parts = doc_stem.split("-")
        if len(parts) >= 2:
            short_stem = f"{parts[0]}-{parts[1]}"
    for key, id_field in id_fields.items():
        items = result.get(key, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and id_field in item and item[id_field]:
                old = item[id_field]
                if not old.startswith(short_stem):
                    item[id_field] = f"{old}__{short_stem}"


def _save_layer_result(result, workspace_dir: str, layer: str):
    """
    保存单层抽取结果。
    - upper 层：存 specific_experiments 和 canonical_pipelines 两个桶
    - lower 层：存 diagnostic_triples 和 strategies 两个桶
    - 向后兼容旧的 records 字段（LLM 偶尔会返回旧格式）
    """
    doc_stem = Path(workspace_dir).name
    _prefix_record_ids(result, doc_stem, layer)
    out_path = f"{workspace_dir}/step1_{layer}.json"

    if not isinstance(result, dict):
        # LLM 返回了裸数组，按旧格式兜底存
        print(f"  ⚠️ Legacy format detected for {layer}, saving as flat list")
        save_json(result, out_path)
        return

    if layer == "upper":
        payload = {
            "specific_experiments": result.get("specific_experiments", []),
            "canonical_pipelines": result.get("canonical_pipelines", []),
        }
        # 兼容：如果 LLM 返回了旧的 "records" 字段，归入 specific_experiments
        if not payload["specific_experiments"] and not payload["canonical_pipelines"] \
                and "records" in result:
            print(f"  ⚠️ Legacy 'records' field found, routing to specific_experiments")
            payload["specific_experiments"] = result["records"]

        n_exp = len(payload["specific_experiments"])
        n_pipe = len(payload["canonical_pipelines"])
        print(f"  Upper: {n_exp} specific_experiments, {n_pipe} canonical_pipelines")

    elif layer == "lower":
        payload = {
            "diagnostic_triples": result.get("diagnostic_triples", []),
            "strategies": result.get("strategies", []),
        }
        # 兼容旧的 "records" 字段
        if not payload["diagnostic_triples"] and not payload["strategies"] \
                and "records" in result:
            print(f"  ⚠️ Legacy 'records' field found, routing to diagnostic_triples")
            payload["diagnostic_triples"] = result["records"]

        n_tri = len(payload["diagnostic_triples"])
        n_strat = len(payload["strategies"])
        print(f"  Lower: {n_tri} diagnostic_triples, {n_strat} strategies")

    else:
        # 未知层，直接存整个 dict
        payload = result

    save_json(payload, out_path)


# ==================== 主函数 ====================

def _normalize_input(entry) -> dict:
    """
    把 input_files 里的每一项统一成 dict 格式:
      {"path": ..., "skip_layers": [...]}

    兼容三种输入写法：
      "path/to/file.md"                              -> 两层都跑
      {"path": "..."}                                 -> 两层都跑
      {"path": "...", "skip_layers": ["upper"]}       -> 只跑下层
    """
    if isinstance(entry, str):
        return {"path": entry, "skip_layers": []}
    if isinstance(entry, dict):
        return {
            "path": entry["path"],
            "skip_layers": entry.get("skip_layers", []),
        }
    raise ValueError(f"Unsupported input_files entry type: {type(entry).__name__}")


def _build_input_files_from_extracted() -> list[dict]:
    """
    自动扫描 knowledge/sources/extracted/*.md，按前缀分配 skip_layers。

    skip_layers 策略（基于材料类型的先验）：
    - expert_experience, MAN (实验测评案例): 两层都跑（有 specific_experiment + diagnostic）
    - PAP (学术论文): 两层都跑
    - STD, GUI, BOOK (标准/指南/教材): 仅 upper（教材重在方法流程，极少故障诊断经验；下层会空或编造）
    - THE (学位论文): 两层都跑（论文通常含大量实验细节）
    - TOOL, HWM, SLD, BLG: 仅 upper（工具文档、硬件手册、课件、博客主要是配置知识）
    """
    extracted_dir = Path(__file__).parent.parent / "sources" / "extracted"
    expert_exp = Path(__file__).parent.parent / "sources" / "expert_experience" / "expert_experience.md"

    files: list[dict] = []

    # 专家经验优先（用户专家经验是 frozen 参考基线）
    if expert_exp.exists():
        files.append({"path": str(expert_exp), "skip_layers": []})

    # Skip 上层的类别
    skip_upper_prefixes = set()  # 默认都跑 upper
    # Skip 下层的类别（不适合产 diagnostic_triple）
    skip_lower_prefixes = {"STD", "GUI", "BOOK", "TOOL", "HWM", "SLD", "BLG"}

    for md_path in sorted(extracted_dir.glob("*.md")):
        stem = md_path.stem
        prefix = stem.split("-", 1)[0] if "-" in stem else ""
        entry = {"path": str(md_path), "skip_layers": []}
        if prefix in skip_upper_prefixes:
            entry["skip_layers"].append("upper")
        if prefix in skip_lower_prefixes:
            entry["skip_layers"].append("lower")
        files.append(entry)

    return files


def main():
    # ========================================
    # ========== 在这里修改配置 ==========
    # ========================================

    import os
    import argparse
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # --- CLI 参数（支持 4 路并行） ---
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", default="0/1",
                        help="I/N 分片（按 stem hash 分派），默认 0/1 = 单进程全跑")
    parser.add_argument("--api-key-index", type=int, default=0,
                        help="用 config.api.siliconflow 里第几把 key (0=api_key, 1=api_key_2 ...)")
    parser.add_argument("--run-lower-all", action="store_true",
                        help="强制所有类别都跑下层 lower（默认 STD/GUI/BOOK/TOOL/HWM/SLD/BLG 跳 lower）")
    args = parser.parse_args()

    try:
        shard_i, shard_n = (int(x) for x in args.shard.split("/"))
        assert 0 <= shard_i < shard_n
    except Exception:
        print(f"ERROR: --shard 格式应为 I/N，实际 {args.shard}")
        return

    # --- 批量输入文件列表 ---
    # 默认：自动扫描 knowledge/sources/extracted/*.md
    # 按类别前缀决定 skip_layers（例如 BLG/TOOL 仅跑 upper；THE/BOOK 教材类跳过 upper 仅跑 lower）
    input_files = _build_input_files_from_extracted()

    # --run-lower-all 时，清空 skip_layers 里的 "lower"，让所有材料都跑下层
    if args.run_lower_all:
        for e in input_files:
            if isinstance(e, dict) and "skip_layers" in e:
                e["skip_layers"] = [x for x in e["skip_layers"] if x != "lower"]
        print(f"[config] --run-lower-all 启用：所有材料都跑 lower")

    # 按 stem hash 分片
    import hashlib
    if shard_n > 1:
        before = len(input_files)
        def _in_shard(entry):
            stem = Path(_normalize_input(entry)["path"]).stem
            h = int(hashlib.md5(stem.encode()).hexdigest(), 16)
            return (h % shard_n) == shard_i
        input_files = [e for e in input_files if _in_shard(e)]
        print(f"[shard] {shard_i}/{shard_n}: {len(input_files)}/{before} files assigned to this shard")

    # --- LLM 配置 ---
    # 要切换 provider 时，注释掉当前激活的配置块，取消注释另一个。
    # 两种 provider 都是 OpenAI 兼容 API，client 初始化代码不用改。
    config = load_config()

    # ---- 配置 A: SiliconFlow + Pro/DeepSeek-V3.2 (日常抽取用，Pro 版 TPM 高不 503) ----
    base_url = config["api"]["siliconflow"]["base_url"]
    # 按 --api-key-index 选 key：0=api_key, 1=api_key_2, 2=api_key_3, 3=api_key_4
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
    prompt_upper = "prompts/step1_upper.txt"
    prompt_lower = "prompts/step1_lower.txt"

    # 初始化LLM客户端
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    for raw_entry in input_files:
        entry = _normalize_input(raw_entry)
        input_file = entry["path"]
        skip_layers = set(entry["skip_layers"])

        workspace_name = Path(input_file).stem
        workspace_dir = f"workspace/{workspace_name}"
        os.makedirs(workspace_dir, exist_ok=True)

        # 增量跳过：按层独立判断。某层的 json 已存在 → 把该层加进 skip_layers
        # （比如之前只跑了 upper，这次开 --run-lower-all 时只补跑 lower，不重跑 upper）
        # 要重跑某层，删掉对应 step1_<layer>.json 即可；要整份重跑，删 workspace/<stem>/ 目录。
        for layer in ("upper", "lower"):
            if layer in skip_layers:
                continue
            if Path(f"{workspace_dir}/step1_{layer}.json").exists():
                skip_layers.add(layer)
                print(f"  [skip-existing] {workspace_name}: {layer} already done")
        if skip_layers.issuperset({"upper", "lower"}):
            continue

        print(f"\n{'=' * 60}")
        print(f"Step 1: Locate & Rewrite")
        print(f"Input: {input_file}")
        print(f"Workspace: {workspace_dir}")
        if skip_layers:
            print(f"Skip layers: {sorted(skip_layers)}")
        print(f"{'=' * 60}")

        # 1. 读取文件
        try:
            full_text = read_file(input_file)
        except Exception as e:
            print(f"  ERROR reading file: {e}")
            continue
        print(f"Full text length: {len(full_text)} chars")

        # 2. 保存原文
        raw_text_path = f"{workspace_dir}/raw_text.txt"
        Path(raw_text_path).write_text(full_text, encoding="utf-8")
        print(f"Raw text saved: {raw_text_path}")

        # 3. 上层抽取
        if "upper" in skip_layers:
            print(f"\n--- Upper Layer [SKIPPED per config] ---")
        else:
            print(f"\n--- Upper Layer ---")
            try:
                upper_result = run_extraction(full_text, prompt_upper, client, model)
                _save_layer_result(upper_result, workspace_dir, "upper")
                _check_unclassified(upper_result, workspace_dir, "upper")
            except Exception as e:
                print(f"  ERROR: {e}")

        # 4. 下层抽取
        if "lower" in skip_layers:
            print(f"\n--- Lower Layer [SKIPPED per config] ---")
        else:
            print(f"\n--- Lower Layer ---")
            try:
                lower_result = run_extraction(full_text, prompt_lower, client, model)
                _save_layer_result(lower_result, workspace_dir, "lower")
                _check_unclassified(lower_result, workspace_dir, "lower")
            except Exception as e:
                print(f"  ERROR: {e}")

        print(f"\n{'=' * 60}")
        print(f"Done: {workspace_name}")
        print(f"{'=' * 60}")

    print(f"\n\nAll files processed!")


if __name__ == "__main__":
    main()
