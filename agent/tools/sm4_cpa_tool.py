# sm4_cpa_tool.py
"""
SM4 CPA 攻击工具

SM4 的密钥恢复需要分 4 轮做 CPA：
- 第 1 轮：猜 rk0 的 4 字节，中间值 = S-box(X1 ⊕ X2 ⊕ X3 ⊕ rk0 的第 i 字节)
- 第 2 轮：用已恢复的 rk0 计算 X4，猜 rk1
- 第 3 轮：用 rk0, rk1 计算 X5，猜 rk2
- 第 4 轮：用 rk0, rk1, rk2 计算 X6，猜 rk3

每轮恢复 4 字节（32 bits）的轮密钥，共 4 轮 = 128 bits。
从 4 个轮密钥反推 128-bit 主密钥。

agent 在使用时需要指定每轮对应的波形区间（wave_start, wave_end），
通常从波形特征中目视或程序定位每轮的起止位置。
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional

# ==================== SM4 常量 ====================

# SM4 S-box (τ 变换 / 合字变换)
SM4_SBOX = np.array([
    0xD6,0x90,0xE9,0xFE,0xCC,0xE1,0x3D,0xB7,0x16,0xB6,0x14,0xC2,0x28,0xFB,0x2C,0x05,
    0x2B,0x67,0x9A,0x76,0x2A,0xBE,0x04,0xC3,0xAA,0x44,0x13,0x26,0x49,0x86,0x06,0x99,
    0x9C,0x42,0x50,0xF4,0x91,0xEF,0x98,0x7A,0x33,0x54,0x0B,0x43,0xED,0xCF,0xAC,0x62,
    0xE4,0xB3,0x1C,0xA9,0xC9,0x08,0xE8,0x95,0x80,0xDF,0x94,0xFA,0x75,0x8F,0x3F,0xA6,
    0x47,0x07,0xA7,0xFC,0xF3,0x73,0x17,0xBA,0x83,0x59,0x3C,0x19,0xE6,0x85,0x4F,0xA8,
    0x68,0x6B,0x81,0xB2,0x71,0x64,0xDA,0x8B,0xF8,0xEB,0x0F,0x4B,0x70,0x56,0x9D,0x35,
    0x1E,0x24,0x0E,0x5E,0x63,0x58,0xD1,0xA2,0x25,0x22,0x7C,0x3B,0x01,0x21,0x78,0x87,
    0xD4,0x00,0x46,0x57,0x9F,0xD3,0x27,0x52,0x4C,0x36,0x02,0xE7,0xA0,0xC4,0xC8,0x9E,
    0xEA,0xBF,0x8A,0xD2,0x40,0xC7,0x38,0xB5,0xA3,0xF7,0xF2,0xCE,0xF9,0x61,0x15,0xA1,
    0xE0,0xAE,0x5D,0xA4,0x9B,0x34,0x1A,0x55,0xAD,0x93,0x32,0x30,0xF5,0x8C,0xB1,0xE3,
    0x1D,0xF6,0xE2,0x2E,0x82,0x66,0xCA,0x60,0xC0,0x29,0x23,0xAB,0x0D,0x53,0x4E,0x6F,
    0xD5,0xDB,0x37,0x45,0xDE,0xFD,0x8E,0x2F,0x03,0xFF,0x6A,0x72,0x6D,0x6C,0x5B,0x51,
    0x8D,0x1B,0xAF,0x92,0xBB,0xDD,0xBC,0x7F,0x11,0xD9,0x5C,0x41,0x1F,0x10,0x5A,0xD8,
    0x0A,0xC1,0x31,0x88,0xA5,0xCD,0x7B,0xBD,0x2D,0x74,0xD0,0x12,0xB8,0xE5,0xB4,0xB0,
    0x89,0x69,0x97,0x4A,0x0C,0x96,0x77,0x7E,0x65,0xB9,0xF1,0x09,0xC5,0x6E,0xC6,0x84,
    0x18,0xF0,0x7D,0xEC,0x3A,0xDC,0x4D,0x20,0x79,0xEE,0x5F,0x3E,0xD7,0xCB,0x39,0x48,
], dtype=np.uint8)

# SM4 系统参数 FK
FK = [0xA3B1BAC6, 0x56AA3350, 0x677D9197, 0xB27022DC]

# SM4 常量 CK
CK = [
    0x00070E15, 0x1C232A31, 0x383F464D, 0x545B6269,
    0x70777E85, 0x8C939AA1, 0xA8AFB6BD, 0xC4CBD2D9,
    0xE0E7EEF5, 0xFC030A11, 0x181F262D, 0x343B4249,
    0x50575E65, 0x6C737A81, 0x888F969D, 0xA4ABB2B9,
    0xC0C7CED5, 0xDCE3EAF1, 0xF8FF060D, 0x141B2229,
    0x30373E45, 0x4C535A61, 0x686F767D, 0x848B9299,
    0xA0A7AEB5, 0xBCC3CAD1, 0xD8DFE6ED, 0xF4FB0209,
    0x10171E25, 0x2C333A41, 0x484F565D, 0x646B7279,
]

# HW 查找表
HW_LUT = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
LOW_GAP_THRESHOLD = 0.15


# ==================== SM4 辅助函数 ====================

def _sm4_sbox_byte(b: int) -> int:
    """单字节 S-box 查找"""
    return int(SM4_SBOX[b & 0xFF])


def _sm4_sbox_word(word: int) -> int:
    """4 字节并行 S-box 查找（τ 变换）"""
    b0 = _sm4_sbox_byte((word >> 24) & 0xFF)
    b1 = _sm4_sbox_byte((word >> 16) & 0xFF)
    b2 = _sm4_sbox_byte((word >> 8) & 0xFF)
    b3 = _sm4_sbox_byte(word & 0xFF)
    return (b0 << 24) | (b1 << 16) | (b2 << 8) | b3


def _sm4_L(word: int) -> int:
    """线性变换 L"""
    word &= 0xFFFFFFFF
    return word ^ _rotl32(word, 2) ^ _rotl32(word, 10) ^ _rotl32(word, 18) ^ _rotl32(word, 24)


def _sm4_L_prime(word: int) -> int:
    """密钥扩展用的线性变换 L'"""
    word &= 0xFFFFFFFF
    return word ^ _rotl32(word, 13) ^ _rotl32(word, 23)


def _rotl32(val: int, n: int) -> int:
    """32-bit 循环左移"""
    val &= 0xFFFFFFFF
    return ((val << n) | (val >> (32 - n))) & 0xFFFFFFFF


def _sm4_T(word: int) -> int:
    """合成变换 T = L ∘ τ"""
    return _sm4_L(_sm4_sbox_word(word))


def _sm4_T_prime(word: int) -> int:
    """密钥扩展用的 T' = L' ∘ τ"""
    return _sm4_L_prime(_sm4_sbox_word(word))


def _sm4_round_function(x0: int, x1: int, x2: int, x3: int, rk: int) -> int:
    """SM4 轮函数：X4 = X0 ⊕ T(X1 ⊕ X2 ⊕ X3 ⊕ rk)"""
    return (x0 ^ _sm4_T(x1 ^ x2 ^ x3 ^ rk)) & 0xFFFFFFFF


def _sm4_key_expand(mk_bytes: bytes) -> List[int]:
    """从 16 字节主密钥生成 32 个轮密钥"""
    mk = [
        int.from_bytes(mk_bytes[i:i+4], 'big') for i in range(0, 16, 4)
    ]
    k = [mk[i] ^ FK[i] for i in range(4)]

    rk = []
    for i in range(32):
        rk_i = k[i] ^ _sm4_T_prime(k[i+1] ^ k[i+2] ^ k[i+3] ^ CK[i])
        rk_i &= 0xFFFFFFFF
        rk.append(rk_i)
        k.append(rk_i)

    return rk


def _rk_to_mk(rk0: int, rk1: int, rk2: int, rk3: int) -> str:
    """
    从前 4 个轮密钥反推 128-bit 主密钥。

    密钥扩展公式：rk_i = K_i ⊕ T'(K_{i+1} ⊕ K_{i+2} ⊕ K_{i+3} ⊕ CK_i)
    其中 K_i = MK_i ⊕ FK_i

    已知 rk0..rk3，反推 K0..K3，再反推 MK0..MK3。
    但这需要解一个非线性方程组（T' 包含 S-box），直接暴力搜索不现实。

    简化做法：使用迭代反推。
    K4 = rk0, K5 = rk1, K6 = rk2, K7 = rk3
    反推 K3 = rk0 ⊕ T'(K4+1 ⊕ K4+2 ⊕ K4+3 ⊕ CK0) ... 不行，这是正向的。

    正确关系：rk_i = K_{i+4}（这是 SM4 密钥扩展的定义！）
    所以 rk0 = K4, rk1 = K5, rk2 = K6, rk3 = K7

    而 K4 = K0 ⊕ T'(K1 ⊕ K2 ⊕ K3 ⊕ CK0)
    知道 K4=rk0，要求 K0..K3。

    这仍然是非线性方程组。但我们可以用另一种方式：
    从 rk0..rk3 和 CK0..CK3 反推 K0..K3。

    K4 = K0 ⊕ T'(K1 ⊕ K2 ⊕ K3 ⊕ CK0)  → K0 = K4 ⊕ T'(K1 ⊕ K2 ⊕ K3 ⊕ CK0)
    K5 = K1 ⊕ T'(K2 ⊕ K3 ⊕ K4 ⊕ CK1)  → K1 = K5 ⊕ T'(K2 ⊕ K3 ⊕ K4 ⊕ CK1)
    K6 = K2 ⊕ T'(K3 ⊕ K4 ⊕ K5 ⊕ CK2)  → K2 = K6 ⊕ T'(K3 ⊕ K4 ⊕ K5 ⊕ CK2)
    K7 = K3 ⊕ T'(K4 ⊕ K5 ⊕ K6 ⊕ CK3)  → K3 = K7 ⊕ T'(K4 ⊕ K5 ⊕ K6 ⊕ CK3)

    反推顺序：先算 K3（已知 K4=rk0, K5=rk1, K6=rk2, K7=rk3），
    然后 K2，然后 K1，然后 K0。
    """
    k4, k5, k6, k7 = rk0, rk1, rk2, rk3

    k3 = (k7 ^ _sm4_T_prime(k4 ^ k5 ^ k6 ^ CK[3])) & 0xFFFFFFFF
    k2 = (k6 ^ _sm4_T_prime(k3 ^ k4 ^ k5 ^ CK[2])) & 0xFFFFFFFF
    k1 = (k5 ^ _sm4_T_prime(k2 ^ k3 ^ k4 ^ CK[1])) & 0xFFFFFFFF
    k0 = (k4 ^ _sm4_T_prime(k1 ^ k2 ^ k3 ^ CK[0])) & 0xFFFFFFFF

    # K_i = MK_i ⊕ FK_i → MK_i = K_i ⊕ FK_i
    mk0 = (k0 ^ FK[0]) & 0xFFFFFFFF
    mk1 = (k1 ^ FK[1]) & 0xFFFFFFFF
    mk2 = (k2 ^ FK[2]) & 0xFFFFFFFF
    mk3 = (k3 ^ FK[3]) & 0xFFFFFFFF

    return f"{mk0:08X}{mk1:08X}{mk2:08X}{mk3:08X}"


def _leak_transform(v: np.ndarray, model: str) -> np.ndarray:
    """泄露模型"""
    if model.upper() == "HW":
        return HW_LUT[v].astype(np.float64)
    elif model.upper() == "ID":
        return v.astype(np.float64)
    else:
        raise ValueError(f"Unsupported leakage model: {model}")


def _compute_sm4_target(xor_b: np.ndarray, k: int, target: str) -> np.ndarray:
    """
    计算 SM4 S-box 级别的中间值。xor_b 已经是前 3 个状态字的 XOR（8-bit）。

    target 选项（对照 Detector SM4FirstOrder）：
    - 'S-box_out':       SBOX[xor_b ^ k]                 (软件标准，Detector target 2)
    - 'S-box_in':        xor_b ^ k                       (线性，Detector target 3；k/k^0xFF 对称)
    - 'S-box_in_xor_out':(xor_b ^ k) XOR SBOX[...]       (HD，Detector target 1)
    """
    t = target.lower().replace("-", "_")
    sbox_in = np.bitwise_xor(xor_b, k)
    sbox_out = SM4_SBOX[sbox_in]
    if t == "s_box_out":
        return sbox_out
    elif t == "s_box_in":
        return sbox_in
    elif t == "s_box_in_xor_out":
        return np.bitwise_xor(sbox_in, sbox_out)
    else:
        raise ValueError(
            f"Unsupported SM4 target: {target}. Use: "
            "S-box_out, S-box_in, S-box_in_xor_out"
        )


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
    item = {
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
    if result_item.get("corr_mode") == "dual":
        item["best_key_pos_hex"] = f"0x{int(result_item['best_key_pos']):02X}"
        item["best_key_neg_hex"] = f"0x{int(result_item['best_key_neg']):02X}"
    return item


def _best_corr_signed(X: np.ndarray, L: np.ndarray, std_X: np.ndarray,
                      points_block: int = 2000) -> Tuple[float, float, int]:
    """带符号相关性：返回 (best_pos, best_neg, best_idx_abs)，同 AES/DES 实现。"""
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
        raw = dot * inv[start:end]
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


# ==================== 主函数 ====================

def run_sm4_cpa(
    plaintext_npy: str,
    wave_npy: str,
    round_index: int = 0,
    candidates: int = 4,
    leakage_model: str = "HW",
    target: str = "S-box_out",
    bytes_to_test: Optional[List[int]] = None,
    prev_round_keys: Optional[List[str]] = None,
    wave_start: Optional[int] = None,
    wave_end: Optional[int] = None,
    points_block: int = 2000,
    corr_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    SM4 CPA 攻击（单轮）。

    SM4 密钥恢复需要分 4 轮做 CPA，每轮恢复 4 字节（32 bits）的轮密钥。
    agent 需要依次调用此函数 4 次（round_index=0,1,2,3），
    每次把前面轮次的结果通过 prev_round_keys 传入。

    参数：
        plaintext_npy: 明文 (n_traces, 16) uint8
        wave_npy: 波形 (n_traces, n_points)
        round_index: 攻击第几轮 (0-3)
        candidates: 每个字节报告的 top K 候选数
        leakage_model: "HW" / "ID"
        bytes_to_test: 测试轮密钥的哪些字节 (0-3)，None = 全部 4 字节
        prev_round_keys: 前面轮次已恢复的轮密钥列表（hex 字符串，每个 8 hex = 4 字节 = 32 bits）。
            round_index=0 时不需要；round_index=1 时需要 [rk0]；round_index=2 时需要 [rk0, rk1]；等等
        wave_start: 截取波形的起始采样点（用于定位每轮区间），None = 从头开始
        wave_end: 截取波形的结束采样点，None = 到末尾

    返回：
        {
            "round_index": int,
            "n_traces": int,
            "n_points": int,
            "leakage_model": str,
            "results": [
                {
                    "byte": int (0-3),
                    "topK": [{"key": int, "score": float, "time_index": int}, ...],
                    "best_key": int,
                },
                ...
            ],
            "recovered_round_key": "AABBCCDD",  # 32-bit 轮密钥 (hex)
            "avg_correlation": float,
            "min_correlation": float,
            "per_byte": [
                {"byte": 0, "key": "0xAA", "correlation": 0.85, "time_index": 1234},
                ...
            ]
        }
    """
    P = np.load(plaintext_npy)  # (n_traces, 16)
    X = np.load(wave_npy)       # (n_traces, n_points)

    if P.ndim != 2 or P.shape[1] != 16:
        raise ValueError(f"SM4 plaintext shape expect (n_traces, 16), got {P.shape}")
    if X.shape[0] != P.shape[0]:
        raise ValueError(f"trace count mismatch: plaintext {P.shape[0]} vs wave {X.shape[0]}")

    # 截取波形区间
    if wave_start is not None or wave_end is not None:
        ws = wave_start or 0
        we = wave_end or X.shape[1]
        X = X[:, ws:we]

    n_traces, n_points = X.shape
    std_X = X.std(axis=0, ddof=1).astype(np.float64) + 1e-12

    # 解析前面轮次的轮密钥
    prev_rks = []
    if prev_round_keys:
        for rk_hex in prev_round_keys:
            rk_hex = rk_hex.replace(" ", "")
            prev_rks.append(int(rk_hex, 16))

    if round_index > 0 and len(prev_rks) < round_index:
        raise ValueError(f"round_index={round_index} requires {round_index} previous round keys, "
                         f"got {len(prev_rks)}")

    # 计算 SM4 轮函数的输入（需要前面轮次的中间值）
    # 明文分成 4 个 32-bit word: X0, X1, X2, X3
    X_words = np.zeros((n_traces, 4), dtype=np.uint32)
    for i in range(4):
        for j in range(4):
            X_words[:, i] = (X_words[:, i] << 8) | P[:, i * 4 + j].astype(np.uint32)

    # 逐轮计算中间值
    # 初始：state = [X0, X1, X2, X3]
    # 每轮后：state.append(X_new)，然后 state 滑窗
    state = [X_words[:, i] for i in range(4)]  # [X0, X1, X2, X3]

    for r in range(round_index):
        # 用已知的 rk_r 计算第 r 轮的输出
        rk = prev_rks[r]
        # X_{r+4} = X_r ⊕ T(X_{r+1} ⊕ X_{r+2} ⊕ X_{r+3} ⊕ rk_r)
        # 这里需要对每条 trace 分别计算（因为明文不同）
        x_new = np.zeros(n_traces, dtype=np.uint32)
        for t in range(n_traces):
            x_new[t] = _sm4_round_function(
                int(state[0][t]), int(state[1][t]),
                int(state[2][t]), int(state[3][t]),
                rk
            )
        state.append(x_new)
        state = state[1:]  # 滑窗：[X1, X2, X3, X4] → 为下一轮准备

    # 现在 state = [X_{r}, X_{r+1}, X_{r+2}, X_{r+3}]
    # 当前轮的 S-box 输入 = X_{r+1} ⊕ X_{r+2} ⊕ X_{r+3} ⊕ rk_{round_index}
    # 对每个字节：sbox_input_byte[i] = (X_{r+1} ⊕ X_{r+2} ⊕ X_{r+3})[byte i] ⊕ rk_byte[i]

    # 计算 X_{r+1} ⊕ X_{r+2} ⊕ X_{r+3} 的每个字节
    xor_123 = state[1].astype(np.uint32) ^ state[2].astype(np.uint32) ^ state[3].astype(np.uint32)
    # 拆分成 4 个字节
    xor_bytes = np.zeros((n_traces, 4), dtype=np.uint8)
    for i in range(4):
        xor_bytes[:, i] = ((xor_123 >> (24 - 8 * i)) & 0xFF).astype(np.uint8)

    if bytes_to_test is None:
        bytes_to_test = list(range(4))

    # 自动选 corr_mode：S-box_in 是线性，和 AES 一样有 k/k^0xFF 对称
    t_normalized = target.lower().replace("-", "_")
    if corr_mode is None:
        if t_normalized == "s_box_in" and leakage_model.upper() == "HW":
            corr_mode = "dual"
        else:
            corr_mode = "abs"
    if corr_mode not in ("abs", "dual"):
        raise ValueError(f"corr_mode must be 'abs' or 'dual', got {corr_mode!r}")

    if corr_mode == "dual":
        print(f"[SM4-CPA] target={target} + HW -> dual mode")

    results = []
    best_keys_pos = [0] * 4
    best_keys_neg = [0] * 4

    for b in bytes_to_test:
        xor_b = xor_bytes[:, b]

        scores_pos = []
        scores_neg = []
        scores_abs = []
        for k in range(256):
            inter = _compute_sm4_target(xor_b, k, target)
            L = _leak_transform(inter, leakage_model)
            bp, bn, tidx = _best_corr_signed(X, L, std_X, points_block=points_block)
            scores_pos.append((bp, tidx, k))
            scores_neg.append((bn, tidx, k))
            scores_abs.append((max(bp, bn), tidx, k))

        if corr_mode == "abs":
            scores_abs.sort(key=lambda x: x[0], reverse=True)
            top = scores_abs[:max(1, int(candidates))]
            bk = scores_abs[0][2]
            best_keys_pos[b] = bk
            best_keys_neg[b] = bk
            results.append({
                "byte": b,
                "topK": [{"key": int(k), "score": float(s), "time_index": int(t)}
                         for (s, t, k) in top],
                "best_key": int(bk),
            })
        else:  # dual
            scores_pos.sort(key=lambda x: x[0], reverse=True)
            scores_neg.sort(key=lambda x: x[0], reverse=True)
            top_pos = scores_pos[:max(1, int(candidates))]
            top_neg = scores_neg[:max(1, int(candidates))]
            bk_pos = scores_pos[0][2]
            bk_neg = scores_neg[0][2]
            best_keys_pos[b] = bk_pos
            best_keys_neg[b] = bk_neg
            merged = {}
            for s, t, k in list(top_pos) + list(top_neg):
                k = int(k)
                if k not in merged or abs(s) > abs(merged[k]["score"]):
                    merged[k] = {"key": k, "score": float(s), "time_index": int(t)}
            topK = sorted(merged.values(), key=lambda x: abs(x["score"]), reverse=True)[:max(1, int(candidates))]
            results.append({
                "byte": b,
                "corr_mode": "dual",
                "topK_pos": [{"key": int(k), "score": float(s), "time_index": int(t)} for (s, t, k) in top_pos],
                "topK_neg": [{"key": int(k), "score": float(s), "time_index": int(t)} for (s, t, k) in top_neg],
                "best_key_pos": int(bk_pos),
                "best_key_neg": int(bk_neg),
                "topK": topK,
                "best_key": int(bk_pos),
            })

    # 组装 32-bit 轮密钥（默认 pos）
    rk_val_pos = (best_keys_pos[0] << 24) | (best_keys_pos[1] << 16) | (best_keys_pos[2] << 8) | best_keys_pos[3]
    rk_hex_pos = f"{rk_val_pos:08X}"
    rk_val_neg = (best_keys_neg[0] << 24) | (best_keys_neg[1] << 16) | (best_keys_neg[2] << 8) | best_keys_neg[3]
    rk_hex_neg = f"{rk_val_neg:08X}"

    all_corrs = [abs(r["topK"][0]["score"]) for r in results]
    per_byte = []
    for r in results:
        top1 = r["topK"][0]
        entry = {
            "byte": r["byte"],
            "key": f"0x{top1['key']:02X}",
            "correlation": top1["score"],
            "time_index": top1["time_index"],
        }
        if r.get("corr_mode") == "dual":
            entry["key_pos"] = f"0x{r['best_key_pos']:02X}"
            entry["key_neg"] = f"0x{r['best_key_neg']:02X}"
        per_byte.append(entry)

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
    cpa_avg_correlation = float(np.mean(all_corrs)) if all_corrs else 0.0
    cpa_min_correlation = float(np.min(all_corrs)) if all_corrs else 0.0
    high_confidence_count = sum(1 for item in subkey_analysis if not item["low_confidence"])
    if high_confidence_count >= 3:
        recommended_next_step = "continue_round_recovery_or_verify_master_key"
        recovery_assessment = (
            f"{high_confidence_count}/4 bytes high-confidence in this round. "
            f"Proceed to the next round or verify the master key if round 3 is finished."
        )
    elif high_confidence_count >= 2:
        recommended_next_step = "alignment_or_multi_strategy_merge_before_next_round"
        recovery_assessment = (
            f"{high_confidence_count}/4 bytes high-confidence in this round. "
            f"This is the SM4 gray band: refine the round window or merge complementary CPA attempts before moving on."
        )
    else:
        recommended_next_step = "relocalize_round_window_or_switch_target"
        recovery_assessment = (
            f"Only {high_confidence_count}/4 bytes are high-confidence in this round. "
            f"Treat this as a red band case: relocalize the round window, revisit alignment, or switch target family."
        )

    output = {
        "schema_version": "cpa_detail_v2",
        "round_index": round_index,
        "n_traces": int(n_traces),
        "n_points": int(n_points),
        "leakage_model": leakage_model,
        "target": target,
        "corr_mode": corr_mode,
        "results": results,
        "subkey_results": results,
        "subkey_analysis": subkey_analysis,
        "recovered_round_key": rk_hex_pos,
        "cpa_avg_correlation": cpa_avg_correlation,
        "cpa_min_correlation": cpa_min_correlation,
        # 保留旧字段兼容已有脚本
        "avg_correlation": cpa_avg_correlation,
        "min_correlation": cpa_min_correlation,
        "per_byte": per_byte,
        "high_confidence_count": high_confidence_count,
        "recovery_assessment": recovery_assessment,
        "low_confidence_subkeys": low_confidence_subkeys,
        "recommended_candidates": max(int(candidates), 30 if low_confidence_subkeys else int(candidates)),
        "recommended_next_step": recommended_next_step,
    }

    # dual 模式时返回两套 round key
    if corr_mode == "dual":
        output["recovered_round_key_pos"] = rk_hex_pos
        output["recovered_round_key_neg"] = rk_hex_neg

    # 如果已经做完 4 轮（round_index=3 且有前 3 轮的密钥），反推主密钥
    if round_index == 3 and len(prev_rks) == 3:
        try:
            mk_hex = _rk_to_mk(prev_rks[0], prev_rks[1], prev_rks[2], rk_val_pos)
            output["recovered_master_key"] = mk_hex

            # 数学一致性检查：用主密钥做密钥扩展，看前 4 轮密钥是否自洽
            # ⚠️ 这只验证 rk0-rk3 和 master_key 之间的数学关系
            # 如果 rk0 本身就错了，rk1-rk3 会跟着错但互相一致 → 这里仍然 True
            # 因此这个标志 **不等于**"密钥恢复正确" —— 必须用 encrypt_decrypt_verify 做外部验证
            mk_bytes = bytes.fromhex(mk_hex)
            expected_rks = _sm4_key_expand(mk_bytes)
            rks_match = (
                expected_rks[0] == prev_rks[0] and
                expected_rks[1] == prev_rks[1] and
                expected_rks[2] == prev_rks[2] and
                expected_rks[3] == rk_val_pos
            )
            output["master_key_math_consistent"] = rks_match
            output["master_key_verification_note"] = (
                "IMPORTANT: math_consistent=true only means rk0-rk3 are internally consistent with this master_key. "
                "It does NOT mean the key is correct. You MUST call encrypt_decrypt_verify to confirm."
            )
        except Exception as e:
            output["recovered_master_key"] = f"ERROR: {e}"
            output["master_key_math_consistent"] = False

    return output
