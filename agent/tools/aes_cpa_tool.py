# aes_cpa_tool.py
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

# AES S-box
AES_SBOX = np.array([
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
], dtype=np.uint8)

# 预先计算HW表（0..255）
HW_LUT = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
LOW_GAP_THRESHOLD = 0.15

def _sbox_out(pt_byte_vec: np.ndarray, k: int) -> np.ndarray:
    """S-box_out: SBOX[pt ^ k]"""
    return AES_SBOX[np.bitwise_xor(pt_byte_vec, k)]

def _leak_transform(v: np.ndarray, model: str) -> np.ndarray:
    """泄露模型：'HW' = 汉明重量，'ID' = 字节值本身"""
    if model.upper() == "HW":
        return HW_LUT[v]
    elif model.upper() == "ID":
        return v.astype(np.float32)
    else:
        raise ValueError(f"Unsupported leakage model: {model}. Use 'HW' or 'ID'.")

def _merge_dedup_topK(top_pos, top_neg, candidates):
    """合并 pos/neg 两套 top，按 |score| 降序去重。用于 dual 模式下兼容下游的 topK 字段。"""
    merged = {}
    for s, t, k in list(top_pos) + list(top_neg):
        k = int(k)
        if k not in merged or abs(s) > abs(merged[k]["score"]):
            merged[k] = {"key": k, "score": float(s), "time_index": int(t)}
    items = sorted(merged.values(), key=lambda x: abs(x["score"]), reverse=True)
    return items[:max(1, int(candidates))]


def _topk_gap(top_k: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """返回 top1_score, top2_score, 相对 gap（按绝对相关性）"""
    if not top_k:
        return None, None, None
    top1 = abs(float(top_k[0]["score"]))
    top2 = abs(float(top_k[1]["score"])) if len(top_k) >= 2 else None
    gap = None if top2 is None else (top1 - top2) / (top1 + 1e-12)
    return top1, top2, gap


def _build_subkey_analysis(result_item: Dict[str, Any]) -> Dict[str, Any]:
    """把原始 byte 结果标准化成统一的 subkey 分析结构。"""
    top_k = result_item.get("topK", [])
    top1_score, top2_score, gap = _topk_gap(top_k)
    top1 = top_k[0] if top_k else {}
    best_key = int(result_item.get("best_key", top1.get("key", 0)))
    return {
        "subkey_type": "byte",
        "subkey_index": int(result_item["byte"]),
        "byte": int(result_item["byte"]),
        "best_key": best_key,
        "best_key_hex": f"0x{best_key:02X}",
        "top1_key": int(top1.get("key", 0)) if top_k else None,
        "top1_score": top1_score,
        "top2_score": top2_score,
        "top1_top2_gap": gap,
        "time_index": int(top1["time_index"]) if top_k else None,
        "candidate_count": len(top_k),
        "low_confidence": bool(gap is not None and gap < LOW_GAP_THRESHOLD),
    }


def _best_corr_signed(
    X: np.ndarray,          # (n_traces, n_points)
    L: np.ndarray,          # (n_traces,)
    std_X: np.ndarray,      # (n_points,)
    points_block: int = 2000,
) -> Tuple[float, float, int]:
    """
    计算相关性在时间维的【带符号】最大值 + 最小值 + 最佳时间索引。

    返回 (best_pos, best_neg, best_idx_abs):
      - best_pos:  max(+corr)  —— 最正的相关性
      - best_neg:  max(-corr) = -min(corr) —— 最负的相关性（反号）
      - best_idx_abs: |corr| 最大的时间点索引

    这样调用方可以自己决定用哪个：
      - 软件 CPA：用 |corr| = max(best_pos, best_neg)
      - 硬件 HD："dual" 模式两个都返回，让 agent 试两套
    """
    n, p = X.shape
    L = L.astype(np.float64)
    Lz = (L - L.mean()) / (L.std(ddof=1) + 1e-12)
    inv = 1.0 / ((n - 1.0) * (std_X + 1e-12))

    best_pos = -np.inf
    best_neg = -np.inf
    best_abs = -np.inf
    best_idx = -1
    for start in range(0, p, points_block):
        end = min(p, start + points_block)
        dot = X[:, start:end].T @ Lz
        raw = dot * inv[start:end]           # signed correlation (w,)
        neg = -raw

        j_pos = int(np.argmax(raw))
        if raw[j_pos] > best_pos:
            best_pos = float(raw[j_pos])

        j_neg = int(np.argmax(neg))
        if neg[j_neg] > best_neg:
            best_neg = float(neg[j_neg])

        absv = np.abs(raw)
        j_abs = int(np.argmax(absv))
        if absv[j_abs] > best_abs:
            best_abs = float(absv[j_abs])
            best_idx = start + j_abs

    return best_pos, best_neg, best_idx


def _corr_curve_signed(
    X: np.ndarray, L: np.ndarray, std_X: np.ndarray,
    points_block: int = 2000,
) -> np.ndarray:
    """返回全时域的【带符号】相关性曲线（不取绝对值）"""
    n, p = X.shape
    if L.shape[0] != n:
        raise ValueError(f"L length mismatch: L={L.shape}, n_traces={n}")
    if std_X.shape[0] != p:
        raise ValueError(f"std_X length mismatch: std_X={std_X.shape}, n_points={p}")

    L = L.astype(np.float64)
    Lz = (L - L.mean()) / (L.std(ddof=1) + 1e-12)
    inv = 1.0 / ((n - 1.0) * (std_X + 1e-12))
    out = np.empty(p, dtype=np.float64)
    for start in range(0, p, points_block):
        end = min(p, start + points_block)
        dot = X[:, start:end].T @ Lz
        out[start:end] = dot * inv[start:end]
    return out


def _compute_target(pt_b: np.ndarray, k: int, target: str,
                     ct_b: np.ndarray = None) -> np.ndarray:
    """
    根据 target 参数计算中间值（泄漏位置）。

    target 选项（正向加密，第 1 轮）：
    - 'S-box_out':             SBOX[pt ^ key]                    （最常见，软件实现）
    - 'S-box_in':              pt ^ key                          （线性，gap 可能小）
    - 'S-box_in_xor_out':      (pt ^ key) XOR SBOX[pt ^ key]    （S-box 输入输出之间的 HD）
    - 'S-box_in_xor_prev_ct':  (pt ^ key) XOR ct[i-1]           （FPGA 寄存器翻转，需要密文）
    - 'S-box_out_xor_prev_ct': SBOX[pt ^ key] XOR ct[i-1]       （S-box 输出和上一轮密文的 HD）

    HD 不是独立的泄漏模型——通过 target 的 XOR 组合自然实现。
    比如 HD(S-box_in, prev_ct) = HW(S-box_in XOR prev_ct)，
    用 target='S-box_in_xor_prev_ct' + leakage_model='HW' 即可。
    """
    t = target.lower().replace("-", "_")
    sbox_in = np.bitwise_xor(pt_b, k)
    sbox_out = AES_SBOX[sbox_in]

    if t == "s_box_out":
        return sbox_out
    elif t == "s_box_in":
        return sbox_in
    elif t == "s_box_in_xor_out":
        return np.bitwise_xor(sbox_in, sbox_out)
    elif t == "s_box_in_xor_prev_ct":
        if ct_b is None:
            raise ValueError("target 'S-box_in_xor_prev_ct' requires ciphertext_npy")
        inter = sbox_in.copy()
        inter[1:] = np.bitwise_xor(sbox_in[1:], ct_b[:-1])
        return inter
    elif t == "s_box_out_xor_prev_ct":
        if ct_b is None:
            raise ValueError("target 'S-box_out_xor_prev_ct' requires ciphertext_npy")
        inter = sbox_out.copy()
        inter[1:] = np.bitwise_xor(sbox_out[1:], ct_b[:-1])
        return inter
    else:
        raise ValueError(
            f"Unsupported target: {target}. Use: "
            "S-box_out, S-box_in, S-box_in_xor_out, S-box_in_xor_prev_ct, S-box_out_xor_prev_ct"
        )


def run_aes_cpa(
    plaintext_npy: str,
    wave_npy: str,
    candidates: int = 10,
    leakage_model: str = "HW",
    target: str = "S-box_out",
    bytes_to_test: Optional[List[int]] = None,
    ciphertext_npy: Optional[str] = None,
    points_block: int = 2000,
    corr_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    AES CPA 攻击。

    参数：
        leakage_model: 'HW'（汉明重量）或 'ID'（字节值）
        target: 泄漏位置（见 _compute_target 的 docstring）
        ciphertext_npy: 密文文件（target 含 prev_ct 时必须提供）
        corr_mode:
            - None (default): 自动根据 target 判断
                - 硬件 HD 线性模型（target='S-box_in_xor_prev_ct' + HW）自动 'dual'
                - 其他自动 'abs'
            - 'abs': 按 |corr| 排序（软件 CPA 传统做法）
            - 'dual': 返回两套 topK：topK_pos (按 +corr 降序), topK_neg (按 -corr 降序)
                用于硬件 HD 线性模型。由于 HW(x) + HW(x^0xFF) = 8，k 和 k^0xFF 的相关性
                互为相反数，|corr| 相等无法区分。因此返回正负两套候选，由下游的
                encrypt_decrypt_verify 用真实密文选出正确的那一套
                （采集极性不确定，不能硬编码选正或选负）。
    """
    P = np.load(plaintext_npy)
    X = np.load(wave_npy)
    CT = np.load(ciphertext_npy) if ciphertext_npy else None

    if P.ndim != 2 or P.shape[1] != 16:
        raise ValueError(f"plaintext shape expect (n_traces,16), got {P.shape}")
    if X.shape[0] != P.shape[0]:
        raise ValueError(f"trace count mismatch: plaintext {P.shape[0]} vs wave {X.shape[0]}")

    n_traces, n_points = X.shape
    std_X = X.std(axis=0, ddof=1).astype(np.float64) + 1e-12

    if bytes_to_test is None:
        bytes_to_test = list(range(16))

    # 根据 target 自动选 corr_mode（用户可显式覆盖）
    t_normalized = target.lower().replace("-", "_")
    if corr_mode is None:
        if t_normalized == "s_box_in_xor_prev_ct" and leakage_model.upper() == "HW":
            corr_mode = "dual"
        else:
            corr_mode = "abs"
    if corr_mode not in ("abs", "dual"):
        raise ValueError(f"corr_mode must be 'abs' or 'dual', got {corr_mode!r}")

    if corr_mode == "dual":
        print(f"[CPA] target={target} + HW: 硬件 HD 线性模型，启用 dual 模式返回正负两套候选"
              f"（由下游验证器选出正确的那一套）")

    results = []

    for b in bytes_to_test:
        pt_b = P[:, b]
        ct_b = CT[:, b] if CT is not None else None

        # 对每个 k，计算 (best_pos, best_neg, best_idx_abs) 的带符号相关性
        scores_pos: List[Tuple[float, int, int]] = []  # (pos_score, t_idx, k)
        scores_neg: List[Tuple[float, int, int]] = []  # (neg_score, t_idx, k)
        scores_abs: List[Tuple[float, int, int]] = []  # (abs_score, t_idx, k)
        all_curves = []

        for k in range(256):
            inter = _compute_target(pt_b, k, target, ct_b)
            L = _leak_transform(inter, leakage_model)
            bp, bn, tidx = _best_corr_signed(X, L, std_X, points_block=points_block)
            scores_pos.append((bp, tidx, k))
            scores_neg.append((bn, tidx, k))
            scores_abs.append((max(bp, bn), tidx, k))

            # 绘图曲线：abs 模式存 |corr|，dual 模式存带符号
            curve = _corr_curve_signed(X, L, std_X, points_block=points_block)
            if corr_mode == "abs":
                curve = np.abs(curve)
            all_curves.append(curve.tolist())

        if corr_mode == "abs":
            scores_abs.sort(key=lambda x: x[0], reverse=True)
            top = scores_abs[:max(1, int(candidates))]
            best_score, best_t, best_k = scores_abs[0]
            results.append({
                "byte": b,
                "topK": [{"key": int(k), "score": float(s), "time_index": int(t)} for (s, t, k) in top],
                "best_key": int(best_k),
                "best_curve": all_curves[best_k],
                "all_curves": all_curves,
            })
        else:  # dual
            scores_pos.sort(key=lambda x: x[0], reverse=True)
            scores_neg.sort(key=lambda x: x[0], reverse=True)
            top_pos = scores_pos[:max(1, int(candidates))]
            top_neg = scores_neg[:max(1, int(candidates))]
            bk_pos = scores_pos[0][2]
            bk_neg = scores_neg[0][2]
            results.append({
                "byte": b,
                "corr_mode": "dual",
                "topK_pos": [{"key": int(k), "score": float(s), "time_index": int(t)} for (s, t, k) in top_pos],
                "topK_neg": [{"key": int(k), "score": float(s), "time_index": int(t)} for (s, t, k) in top_neg],
                "best_key_pos": int(bk_pos),
                "best_key_neg": int(bk_neg),
                # 为兼容下游（encrypt_decrypt_verify / key_search）保留 topK：先放 pos 再放 neg 的去重合并
                "topK": _merge_dedup_topK(top_pos, top_neg, candidates),
                "best_key": int(bk_pos),  # 默认先试 pos；agent 不对再试 neg
                "best_curve": all_curves[bk_pos],
                "all_curves": all_curves,
            })

    subkey_analysis = [_build_subkey_analysis(r) for r in results]
    low_confidence_subkeys = [
        {
            "subkey_index": item["subkey_index"],
            "byte": item["byte"],
            "best_key_hex": item["best_key_hex"],
            "top1_top2_gap": item["top1_top2_gap"],
        }
        for item in subkey_analysis if item["low_confidence"]
    ]
    best_scores = [item["top1_score"] for item in subkey_analysis if item["top1_score"] is not None]
    cpa_avg_correlation = float(np.mean(best_scores)) if best_scores else 0.0
    cpa_min_correlation = float(np.min(best_scores)) if best_scores else 0.0

    # --- gap-based recovery assessment (gap is already relative: (top1-top2)/top1) ---
    n_subkeys = len(subkey_analysis)
    high_confidence_count = sum(1 for item in subkey_analysis if not item["low_confidence"])
    low_gap_bytes = [item["byte"] for item in subkey_analysis if item["low_confidence"]]

    if high_confidence_count >= 13:
        recommended_next_step = "most_bytes_correct_run_key_search_for_unreliable_only"
        recovery_assessment = (
            f"{high_confidence_count}/{n_subkeys} bytes high-confidence "
            f"(gap >= {int(LOW_GAP_THRESHOLD * 100)}%). "
            f"Only bytes {low_gap_bytes} are unreliable. "
            f"Run key_search targeting those bytes. "
            f"Do NOT switch target/method/alignment before exhausting verification and targeted key_search."
        )
    elif high_confidence_count >= 10:
        recommended_next_step = "alignment_or_multi_strategy_merge_then_key_search"
        recovery_assessment = (
            f"{high_confidence_count}/{n_subkeys} bytes high-confidence. "
            f"Bytes {low_gap_bytes} are unreliable. "
            f"This is the gray band: keep the same candidate interval / target family in scope, "
            f"then try complementary alignment or interval strategies and merge detail JSON files before key_search."
        )
    else:
        recommended_next_step = "relocalize_leakage_or_switch_target_before_key_search"
        recovery_assessment = (
            f"Only {high_confidence_count}/{n_subkeys} bytes are high-confidence. "
            f"This is the red band: first revisit candidate interval, start position, or target family. "
            f"Average correlation ({cpa_avg_correlation:.4f}) is secondary context, not the main decision signal."
        )

    return {
        "schema_version": "cpa_detail_v2",
        "n_traces": int(n_traces),
        "n_points": int(n_points),
        "leakage_model": leakage_model,
        "target": target,
        "corr_mode": corr_mode,
        "results": results,
        "subkey_results": results,
        "subkey_analysis": subkey_analysis,
        "cpa_avg_correlation": cpa_avg_correlation,
        "cpa_min_correlation": cpa_min_correlation,
        "high_confidence_count": high_confidence_count,
        "recovery_assessment": recovery_assessment,
        # 保留旧字段兼容已有脚本
        "avg_correlation": cpa_avg_correlation,
        "min_correlation": cpa_min_correlation,
        "low_confidence_subkeys": low_confidence_subkeys,
        "recommended_candidates": max(int(candidates), 30 if low_confidence_subkeys else int(candidates)),
        "recommended_next_step": recommended_next_step,
    }
