"""
评估指标计算 + 日志解析

核心指标：
- Success Rate (SR): 完全恢复正确密钥的比例
- Byte Recovery Rate (BRR): 正确字节数 / 总字节数
- Rounds: LLM 对话轮数
- Tool Calls: 工具调用次数
- Tokens: prompt/completion token 累计
"""
import os
import re
import json
import glob
from typing import Dict, List, Optional


# ==================== 正确密钥 ground truth ====================

# 从 DKG_project_context.md 抽取的正确密钥（hex 格式，大写无空格）
GROUND_TRUTH_KEYS = {
    "AES-7816":      "112233445566778899AABBCCDDEEFF00",
    "AES-14443":     "112233445566778899AABBCCDDEEFF00",
    "AES-FPGA":      "0123456789ABCDEFFEDCBA9876543210",
    "AES-STM32F103": "112233445566778899AABBCCDDEEFF00",
    "AES-STM32F429": "00112233445566778899AABBCCDDEEFF",
    "DES-7816":      "1022324454667688",  # PC-1 丢弃校验位后的等价密钥
    "DES-14443":     "1122334455667788",
    "SM4-7816":      "0123456789ABCDEFFEDCBA9876543210",
}

# DES 的校验位校正：原始密钥 vs CPA 恢复密钥
# DES 每 byte 最低 bit 是 parity，不参与加密；去 parity 后的等价 key 加密结果完全一致
# 2026-04-23 补全 DES-14443 的 parity 等价（此前缺失导致 Patch 002 smoke 真 MATCH 被误判 FAIL）
DES_KEY_EQUIVALENTS = {
    "DES-7816":  ["1122334455667788", "1022324454667688"],
    "DES-14443": ["1122334455667788", "1022324454667688"],
}


# ==================== 密钥比对 ====================

def _normalize_hex(k: str) -> str:
    """规范化 hex 字符串：去空格、大写"""
    return re.sub(r"\s+", "", k or "").upper()


def count_correct_bytes(recovered_hex: str, truth_hex: str) -> int:
    """按字节比对正确数（hex 字符串，2 字符 = 1 字节）"""
    r = _normalize_hex(recovered_hex)
    t = _normalize_hex(truth_hex)
    if not r or not t or len(r) != len(t):
        return 0
    n_bytes = len(t) // 2
    count = 0
    for i in range(n_bytes):
        if r[i*2:i*2+2] == t[i*2:i*2+2]:
            count += 1
    return count


def total_key_bytes(case: str) -> int:
    """每个案例的总字节数（用来算 BRR）"""
    if case.startswith("AES"):
        return 16
    if case.startswith("DES"):
        return 8
    if case.startswith("SM4"):
        return 16
    return 16


def is_key_correct(recovered_hex: str, case: str) -> bool:
    """密钥是否完全正确（DES 处理校验位等价性）"""
    truth = GROUND_TRUTH_KEYS.get(case, "")
    if not truth:
        return False
    r = _normalize_hex(recovered_hex)
    if r == _normalize_hex(truth):
        return True
    for alt in DES_KEY_EQUIVALENTS.get(case, []):
        if r == _normalize_hex(alt):
            return True
    return False


# ==================== 日志解析 ====================

def _extract_final_key(log_text: str) -> Optional[str]:
    """从 agent_log.md 中提取最终恢复的密钥。

    优先级（从高到低）：
      1. `correct_key` (key_search 工具返回)
      2. encrypt_decrypt_verify 的 tool call 里 `key_hex`，且紧跟的 tool result `verification: MATCH`
      3. `recovered_key` (aes_cpa_attack / des_cpa_attack / sm4_cpa_attack 工具返回)

    2026-04-23 改进：原正则 `[^}]*` 不跨行，漏掉 encrypt_decrypt_verify 的 call → result 结构
    （agent 用 python_jupyter 手工构造 key 时，没有 recovered_key 字段，只能靠 verify MATCH 附近的 key_hex）
    """
    # (1) key_search 成功
    cks = re.findall(r'"correct_key":\s*"([0-9A-Fa-f]+)"', log_text)
    if cks:
        return cks[-1]

    # (2) encrypt_decrypt_verify MATCH 附近的 key_hex
    # 策略：找所有 `"verification": "MATCH"` 位置，往前 3000 chars 内找最近的 `"key_hex": "..."`
    # 2026-04-23 二次调整：lookback 500 对长 LLM reasoning 的 session 不够（AES-FPGA dual-mode
    # 实测 MATCH 往前 500 chars 未命中，2000 chars 才找到），扩到 3000 chars 兼容长 reasoning 块
    match_positions = [m.start() for m in re.finditer(r'"verification":\s*"MATCH"', log_text)]
    verify_match_keys = []
    for pos in match_positions:
        lookback = log_text[max(0, pos - 3000):pos]
        khs = re.findall(r'"key_hex":\s*"([0-9A-Fa-f]+)"', lookback)
        if khs:
            verify_match_keys.append(khs[-1])
    if verify_match_keys:
        return verify_match_keys[-1]

    # (3) CPA tool 返回 recovered_key
    rks = re.findall(r'"recovered_key":\s*"([0-9A-Fa-f]+)"', log_text)
    if rks:
        return rks[-1]

    return None


def _count_rounds(log_text: str) -> int:
    """统计 LLM 对话轮数（### Round N 的个数）"""
    return len(re.findall(r"^### Round \d+", log_text, flags=re.MULTILINE))


def _count_tool_calls(log_text: str) -> int:
    """统计工具调用次数"""
    return len(re.findall(r"🔧 → `|\\u{1f527}|\*\*.*→ `[a-z_]+`", log_text))


def _extract_tokens(log_text: str) -> Dict[str, int]:
    """从 Token Summary 表格提取总 prompt/completion tokens"""
    # 形如：| Total Tokens | 102,345 (prompt: 89,123, completion: 13,222) |
    m = re.search(
        r"Total Tokens\s*\|\s*([\d,]+)\s*\(prompt:\s*([\d,]+),\s*completion:\s*([\d,]+)\)",
        log_text
    )
    if not m:
        return {"total": 0, "prompt": 0, "completion": 0}
    return {
        "total":      int(m.group(1).replace(",", "")),
        "prompt":     int(m.group(2).replace(",", "")),
        "completion": int(m.group(3).replace(",", "")),
    }


def _extract_duration(log_text: str) -> float:
    """从 Configuration 表格提取 Duration（秒）"""
    m = re.search(r"\|\s*Duration\s*\|\s*([\d.]+)s", log_text)
    return float(m.group(1)) if m else 0.0


def _extract_model(log_text: str) -> str:
    """从 Configuration 提取 Model"""
    m = re.search(r"\|\s*Model\s*\|\s*`?([^`|]+)`?\s*\|", log_text)
    return m.group(1).strip() if m else ""


def _extract_use_kg(log_text: str) -> bool:
    """从 kg_config 或目录名推断是否使用了 KG"""
    # Config 里 "disabled": True 说明是 No-KG
    if '"disabled": true' in log_text or '"disabled": True' in log_text:
        return False
    # 默认有 KG
    return True


# ==================== 单个 session 的指标 ====================

def parse_session(session_dir: str) -> Optional[Dict]:
    """
    解析一个 session 目录的 agent_log.md，返回指标字典。
    目录名格式: {case}_{model_short}_{kg_tag}_{timestamp}
    """
    log_path = os.path.join(session_dir, "agent_log.md")
    if not os.path.exists(log_path):
        return None

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        log_text = f.read()

    # 从目录名解析 case / model / kg_tag
    dir_name = os.path.basename(session_dir.rstrip(os.sep).rstrip("/"))
    parts = dir_name.split("_")
    case = parts[0] if parts else ""
    kg_tag = "DKG"
    for p in parts[1:]:
        if p in ("DKG", "NoKG"):
            kg_tag = p
            break

    recovered = _extract_final_key(log_text) or ""
    truth = GROUND_TRUTH_KEYS.get(case, "")
    total = total_key_bytes(case)
    correct = count_correct_bytes(recovered, truth) if truth else 0
    success = is_key_correct(recovered, case)

    tokens = _extract_tokens(log_text)

    return {
        "session_dir":    session_dir,
        "session_name":   dir_name,
        "case":           case,
        "model":          _extract_model(log_text),
        "kg_tag":         kg_tag,
        "use_kg":         _extract_use_kg(log_text),
        "recovered_key":  recovered,
        "truth_key":      truth,
        "success":        success,
        "correct_bytes":  correct,
        "total_bytes":    total,
        "byte_recovery":  correct / total if total > 0 else 0.0,
        "rounds":         _count_rounds(log_text),
        "tool_calls":     _count_tool_calls(log_text),
        "duration_sec":   _extract_duration(log_text),
        "tokens_total":   tokens["total"],
        "tokens_prompt":  tokens["prompt"],
        "tokens_compl":   tokens["completion"],
    }


def parse_log_dir(log_dir: str) -> List[Dict]:
    """解析一个 logs/{子目录} 下所有 session，返回指标列表"""
    results = []
    for session_dir in sorted(glob.glob(os.path.join(log_dir, "*"))):
        if os.path.isdir(session_dir):
            r = parse_session(session_dir)
            if r:
                results.append(r)
    return results


# ==================== 聚合统计 ====================

def aggregate_by(results: List[Dict], group_keys: List[str]) -> List[Dict]:
    """
    按 group_keys（如 ["case", "model", "kg_tag"]）聚合：
    - 平均 SR / BRR / rounds / tool_calls / tokens / duration
    - 输出每组的 runs 数量
    """
    groups: Dict[tuple, List[Dict]] = {}
    for r in results:
        key = tuple(r.get(k, "") for k in group_keys)
        groups.setdefault(key, []).append(r)

    agg = []
    for key, runs in groups.items():
        n = len(runs)
        row = {k: v for k, v in zip(group_keys, key)}
        row["n_runs"]         = n
        row["successes"]      = sum(1 for r in runs if r["success"])
        row["success_rate"]   = row["successes"] / n if n else 0.0
        row["avg_byte_recovery"] = sum(r["byte_recovery"] for r in runs) / n if n else 0.0
        row["avg_rounds"]     = sum(r["rounds"]     for r in runs) / n if n else 0.0
        row["avg_tool_calls"] = sum(r["tool_calls"] for r in runs) / n if n else 0.0
        row["avg_tokens"]     = sum(r["tokens_total"] for r in runs) / n if n else 0.0
        row["avg_duration"]   = sum(r["duration_sec"] for r in runs) / n if n else 0.0
        agg.append(row)
    return agg


def print_summary_table(agg_rows: List[Dict], group_keys: List[str]):
    """控制台打印聚合表格"""
    if not agg_rows:
        print("  (no results)")
        return
    # 标题
    cols = group_keys + ["n_runs", "success_rate", "avg_byte_recovery",
                         "avg_rounds", "avg_tool_calls", "avg_tokens", "avg_duration"]
    widths = {c: max(len(c), max(len(str(r.get(c, ""))) for r in agg_rows)) for c in cols}
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for r in agg_rows:
        cells = []
        for c in cols:
            v = r.get(c, "")
            if isinstance(v, float):
                if c in ("success_rate", "avg_byte_recovery"):
                    v = f"{v*100:.1f}%"
                else:
                    v = f"{v:.1f}"
            cells.append(str(v).ljust(widths[c]))
        print(" | ".join(cells))


def save_results_json(results: List[Dict], out_path: str):
    """把详细 results 列表存成 JSON"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def save_agg_csv(agg_rows: List[Dict], out_path: str, group_keys: List[str]):
    """把聚合结果存成 CSV（便于导入论文）"""
    import csv
    if not agg_rows:
        return
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cols = group_keys + ["n_runs", "successes", "success_rate", "avg_byte_recovery",
                         "avg_rounds", "avg_tool_calls", "avg_tokens", "avg_duration"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in agg_rows:
            w.writerow([r.get(c, "") for c in cols])
