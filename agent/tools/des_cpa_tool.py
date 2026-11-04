# des_cpa_tool.py
"""
DES CPA 攻击工具

攻击第一轮 S-box 输出，恢复 48-bit 子密钥，然后反推 64-bit 主密钥。
DES 有 8 个 S-box（各 6-bit→4-bit），所以恢复 8×6 = 48 bit 子密钥。

注意：DES 每字节最后一位是校验位，软件加密时被置零，
所以恢复的密钥每字节最后一位为 0 是正常现象。
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional

# ==================== DES 常量 ====================

# 初始置换 IP (1-indexed → 0-indexed in code)
IP = [
    58,50,42,34,26,18,10,2, 60,52,44,36,28,20,12,4,
    62,54,46,38,30,22,14,6, 64,56,48,40,32,24,16,8,
    57,49,41,33,25,17,9,1,  59,51,43,35,27,19,11,3,
    61,53,45,37,29,21,13,5, 63,55,47,39,31,23,15,7
]

# 扩展置换 E: 32-bit → 48-bit (1-indexed)
E_TABLE = [
    32, 1, 2, 3, 4, 5,   4, 5, 6, 7, 8, 9,
     8, 9,10,11,12,13,  12,13,14,15,16,17,
    16,17,18,19,20,21,  20,21,22,23,24,25,
    24,25,26,27,28,29,  28,29,30,31,32, 1
]

# 8 个 DES S-box (各 4 行 16 列)
DES_SBOXES = [
    # S1
    [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
     [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
     [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
     [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],
    # S2
    [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
     [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
     [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
     [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],
    # S3
    [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
     [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
     [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
     [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],
    # S4
    [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
     [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
     [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
     [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],
    # S5
    [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
     [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
     [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
     [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],
    # S6
    [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
     [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
     [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
     [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],
    # S7
    [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
     [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
     [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
     [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],
    # S8
    [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
     [1,15,13,8,10,3,7,4,12,5,6,2,0,14,9,11],
     [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
     [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]
]

# PC-1: 64-bit key → 56-bit (去校验位) (1-indexed)
PC1 = [
    57,49,41,33,25,17,9,  1,58,50,42,34,26,18,
    10, 2,59,51,43,35,27, 19,11, 3,60,52,44,36,
    63,55,47,39,31,23,15,  7,62,54,46,38,30,22,
    14, 6,61,53,45,37,29, 21,13, 5,28,20,12, 4
]

# PC-2: 56-bit → 48-bit (1-indexed)
PC2 = [
    14,17,11,24, 1, 5, 3,28,15, 6,21,10,
    23,19,12, 4,26, 8,16, 7,27,20,13, 2,
    41,52,31,37,47,55,30,40,51,45,33,48,
    44,49,39,56,34,53,46,42,50,36,29,32
]

# 左移位数 (16 轮)
LEFT_SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]

# P 置换 (1-indexed) —— F 函数输出的比特重排
# 输入: 32-bit (S-box 8 个 4-bit 输出拼接)
# 输出: 32-bit (用于和 L 异或)
P_TABLE = [
    16,7,20,21, 29,12,28,17, 1,15,23,26, 5,18,31,10,
    2,8,24,14, 32,27,3,9,    19,13,30,6,  22,11,4,25
]

# 每个 S-box 对 F 函数输出（32-bit）的哪 4 个 bit 位置贡献了
# 比如 S1 (sbox_idx=0) 输出 4 bits 占 32-bit 中的位置 [p0..p3]
# 通过 P_TABLE 反查：P[i]=v 表示 F[i] 来自 S 输出的第 v 位
# S_i (i=0..7) 贡献了 S 输出的 bit [4i..4i+3]，我们要知道它们在 F 中的位置
def _build_sbox_to_f_positions():
    """返回 sbox_to_fpos[sbox_idx] = [p0, p1, p2, p3]（F 输出中 4 个 0-indexed 位置）

    重要：顺序必须与 S-box 输出 bit 对齐，即：
      out[sbox][j] = S-box 输出的第 j 个 bit (j=0..3) 在 F 中的位置。
    这样在 _compute_des_target 里 `r0_4bits[j] ^ l0_4bits[j] ^ sbox_out_bit[j]`
    才是对同一个 F 位置做 XOR。

    之前 bug：直接按 fpos 数值顺序 append，导致非 sbox 0 的映射全部错位，
    只有 sbox 0 碰巧（因为 [8,16,22,30] 正好数值递增对应 SOut bit 0-3）
    能打出正确相关性。
    """
    out = [[None] * 4 for _ in range(8)]
    for fpos_0indexed in range(32):
        # F[fpos] = S output 的第 P[fpos]-1 位（1-indexed → 0-indexed）
        src_bit_0idx = P_TABLE[fpos_0indexed] - 1
        sbox_idx = src_bit_0idx // 4
        bit_in_sbox = src_bit_0idx % 4   # 0..3 —— 这是 S-box 输出的第几个 bit
        out[sbox_idx][bit_in_sbox] = fpos_0indexed
    return out

SBOX_TO_F_POSITIONS = _build_sbox_to_f_positions()  # 每个 sbox 有 4 个 F-bit 位置

# 预先计算 HW 表
HW_LUT = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
LOW_GAP_THRESHOLD = 0.15

# 预计算 S-box 查找表：sbox_lut[sbox_idx][6-bit input] → 4-bit output
SBOX_LUT = np.zeros((8, 64), dtype=np.uint8)
for si in range(8):
    for val6 in range(64):
        # 6-bit input: b5 b4 b3 b2 b1 b0
        # row = b5*2 + b0, col = b4*8 + b3*4 + b2*2 + b1
        row = ((val6 >> 5) & 1) * 2 + (val6 & 1)
        col = (val6 >> 1) & 0xF
        SBOX_LUT[si][val6] = DES_SBOXES[si][row][col]


# ==================== 辅助函数 ====================

def _bytes_to_bits(data: np.ndarray) -> np.ndarray:
    """(n_traces, 8) uint8 → (n_traces, 64) bit array"""
    n = data.shape[0]
    bits = np.zeros((n, 64), dtype=np.uint8)
    for i in range(8):
        for j in range(8):
            bits[:, i * 8 + j] = (data[:, i] >> (7 - j)) & 1
    return bits


def _apply_permutation(bits: np.ndarray, perm: list) -> np.ndarray:
    """应用置换表 (1-indexed)"""
    return bits[:, [p - 1 for p in perm]]


def _get_r0_expanded(plaintext: np.ndarray) -> np.ndarray:
    """
    明文 (n_traces, 8) → IP置换 → 取 R0 (右半32-bit) → E扩展 → (n_traces, 48) bit array
    """
    bits = _bytes_to_bits(plaintext)       # (n, 64)
    ip_bits = _apply_permutation(bits, IP) # (n, 64)
    r0 = ip_bits[:, 32:64]                 # (n, 32) 右半
    r0_exp = _apply_permutation(r0, E_TABLE)  # 这里 E_TABLE 是 1-indexed 到 32-bit
    # E_TABLE 引用的是 R0 的 bit 位置（1-indexed），需要特殊处理
    # 重新实现 E 扩展
    r0_exp = r0[:, [e - 1 for e in E_TABLE]]  # (n, 48)
    return r0_exp


def _get_l0_r0(plaintext: np.ndarray):
    """返回 IP 置换后的 L0 (n,32) 和 R0_expanded (n,48)"""
    bits = _bytes_to_bits(plaintext)
    ip_bits = _apply_permutation(bits, IP)
    l0 = ip_bits[:, 0:32]                        # (n, 32)
    r0 = ip_bits[:, 32:64]                       # (n, 32)
    r0_exp = r0[:, [e - 1 for e in E_TABLE]]     # (n, 48)
    return l0, r0, r0_exp


def _leak_transform(v: np.ndarray, model: str) -> np.ndarray:
    """泄露模型"""
    if model.upper() == "HW":
        return HW_LUT[v].astype(np.float64)
    elif model.upper() == "ID":
        return v.astype(np.float64)
    else:
        raise ValueError(f"Unsupported leakage model: {model}")


def _topk_gap(top_k: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """返回 top1_score, top2_score, 相对 gap（按绝对相关性）"""
    if not top_k:
        return None, None, None
    top1 = abs(float(top_k[0]["score"]))
    top2 = abs(float(top_k[1]["score"])) if len(top_k) >= 2 else None
    gap = None if top2 is None else (top1 - top2) / (top1 + 1e-12)
    return top1, top2, gap


def _build_subkey_analysis(result_item: Dict[str, Any]) -> Dict[str, Any]:
    """把原始 S-box 结果标准化成统一的 subkey 分析结构。"""
    top_k = result_item.get("topK", [])
    top1_score, top2_score, gap = _topk_gap(top_k)
    top1 = top_k[0] if top_k else {}
    best_key = int(result_item.get("best_key", top1.get("key", 0)))
    item = {
        "subkey_type": "sbox",
        "subkey_index": int(result_item["sbox"]),
        "sbox": int(result_item["sbox"]),
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
    """
    计算带符号的相关性：返回 (best_pos, best_neg, best_idx_abs)
    - best_pos: max(+corr)
    - best_neg: max(-corr) = -min(corr)
    - best_idx_abs: |corr| 最大的时间点

    和 aes_cpa_tool 的 _best_corr_signed 保持一致，供硬件 HD dual 模式用。
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


def _subkey48_to_key64(subkey_6bits: List[int]) -> str:
    """
    从 8 个 6-bit 子密钥 → 48-bit 第一轮子密钥 → 反推 64-bit 主密钥。

    PC-2 是 56→48 的选择置换。知道 48-bit 就知道 56-bit 中 48 个位。
    剩余 8 个位未知，暴力搜索 256 种可能（但这里简化：把未知位设为 0，
    校验位也设为 0，得到的密钥可能不完全精确但对 CPA 分析够用）。

    实际上对于 SCA 场景，恢复的 48-bit 子密钥包含了密钥的绝大部分信息，
    校验位本身就会被软件置零。
    """
    # 组装 48-bit 子密钥
    k48_bits = []
    for si in range(8):
        val = subkey_6bits[si]
        for j in range(6):
            k48_bits.append((val >> (5 - j)) & 1)

    # PC-2 是从 56-bit 中选 48-bit 的置换
    # 反转 PC-2：知道输出的 48 bits，推出输入（56-bit CD1）的对应位
    cd1 = [0] * 56
    for i, pos in enumerate(PC2):
        cd1[pos - 1] = k48_bits[i]

    # 反转 LS1（循环左移1位 → 循环右移1位）
    c1 = cd1[:28]
    d1 = cd1[28:]
    # 第一轮左移 1 位，反转 = 右移 1 位
    c0 = [c1[-1]] + c1[:-1]
    d0 = [d1[-1]] + d1[:-1]
    cd0 = c0 + d0

    # 反转 PC-1：从 56-bit CD0 → 64-bit key
    key64 = [0] * 64
    for i, pos in enumerate(PC1):
        key64[pos - 1] = cd0[i]

    # 设置校验位为 0（每字节第 8 位，index 7,15,23,...,63）
    for byte_idx in range(8):
        key64[byte_idx * 8 + 7] = 0

    # bits → bytes
    key_bytes = []
    for i in range(8):
        val = 0
        for j in range(8):
            val = (val << 1) | key64[i * 8 + j]
        key_bytes.append(val)

    return ''.join(f'{b:02X}' for b in key_bytes)


# ==================== 主函数 ====================

def _compute_des_target(r0_val: np.ndarray, k: int, sbox_idx: int, target: str,
                         l0_4bits: Optional[np.ndarray] = None,
                         r0_4bits: Optional[np.ndarray] = None) -> np.ndarray:
    """
    根据 target 参数计算 DES 在第 1 轮某个 S-box 位置的中间值。

    target 选项（基于 Detector DES 的 4 种 target 设计）：
    - 'S-box_out':       SBOX(E(R0) ^ K) (4-bit)
                         软件实现默认。SBOX 非线性，无 k/k^0x3F 对称问题。
    - 'S-box_in':        E(R0) ^ K (6-bit，线性)
                         有 k/k^0x3F 互补对称性，建议配合 dual corr_mode。
    - 'S-box_in_xor_out':(E(R0) ^ K) XOR SBOX[...] (6-bit)
                         SBOX 打破 4-bit 的对称，但剩 2-bit（b5,b0）是线性。
    - 'R_xor_LOut':      HD(R1, L1) = F(R0,K) 对应 4 个 bit 的 HW
                         硬件 FPGA/智能卡常用。对应 Detector target 1。
                         每个 S-box 贡献 P 置换中指定的 4 个 F-bit，
                         与 L0 对应位置异或即 F_bit ^ L0_bit = Li 对应 bit。
                         需要传入 l0_4bits 和 r0_4bits（对应 4 个 F 输出位置）。
    - 'LOut':            L1_4bits 的 HW = (F(R0,K) ^ L0) 的 4 个 bit
                         等同于 R_xor_LOut（DES 的 L1 = R0，所以 HD(R0, L1) = ...）
                         实际 Detector target 2，仍通过 S-box 非线性。
    """
    t = target.lower().replace("-", "_")
    sbox_in = np.bitwise_xor(r0_val, k)            # 6-bit (0-63)
    sbox_out = SBOX_LUT[sbox_idx][sbox_in]          # 4-bit (0-15)

    if t == "s_box_out":
        return sbox_out
    elif t == "s_box_in":
        return sbox_in
    elif t == "s_box_in_xor_out":
        return np.bitwise_xor(sbox_in, sbox_out.astype(np.uint8))
    elif t in ("r_xor_lout", "lout"):
        # 需要 l0 对应 4 个 F-bit 位置的值
        if l0_4bits is None:
            raise ValueError(
                f"target '{target}' requires L0 bits. Internal helper should pass l0_4bits.")
        # F 输出 = P(SOut) 的对应 4 bit
        # sbox_out 的 4 个 bit 分别对应 F 输出的 4 个位置（SBOX_TO_F_POSITIONS[sbox_idx]）
        # 但我们只关心 HW，不需要真正做 P 置换——HW 对 bit 顺序不敏感
        # 所以只用 sbox_out 的 4 bit 和 l0 对应 4 bit 异或（XOR）
        f_bits = sbox_out.astype(np.uint8)          # (n,) 4-bit
        if t == "r_xor_lout":
            # R1 = L0 ^ F, L1 = R0. HD(L1, R1) = HW(R0 ^ L0 ^ F)
            # 4-bit 对应位: r0_4bits ^ l0_4bits ^ f_bits
            if r0_4bits is None:
                raise ValueError("target 'R_xor_LOut' requires r0_4bits")
            return np.bitwise_xor(np.bitwise_xor(r0_4bits, l0_4bits), f_bits)
        else:  # lout
            # L1 = R0 （DES Feistel）
            # R1 = L0 ^ F
            # 但 Detector 的 LOut = 本轮左侧输出 = R1? 看 Des.cs line 94: SOut^invPermute(L,P)
            # 实际含义：L1_bit = L0_bit ^ F_bit = L0_bit ^ SBOX_bit (这 4 个 bit 位置)
            return np.bitwise_xor(l0_4bits, f_bits)
    else:
        raise ValueError(
            f"Unsupported DES target: {target}. Use: "
            "S-box_out, S-box_in, S-box_in_xor_out, R_xor_LOut, LOut"
        )


def _get_l0_r0_sbox_bits(l0_32: np.ndarray, r0_32: np.ndarray, sbox_idx: int):
    """
    对于 S-box sbox_idx，返回该 S-box 贡献的 4 个 F-bit 对应的 L0 比特和 R0 比特。

    F-bit 位置 = SBOX_TO_F_POSITIONS[sbox_idx]（长度 4）
    L0 / R0 都是 32-bit，按这 4 个位置取。

    返回的 4-bit 值打包成 uint8，每个 trace 一个值（0..15）。
    """
    fpos = SBOX_TO_F_POSITIONS[sbox_idx]            # len=4, 每个是 F[0..31] 的 0-indexed 位置
    # l0_32 shape: (n, 32)，bit 0 是 MSB（DES 左侧高位）
    l0_bits = l0_32[:, fpos]                         # (n, 4)
    r0_bits = r0_32[:, fpos]                         # (n, 4)
    # 打包成 4-bit 整数
    l0_val = np.zeros(l0_32.shape[0], dtype=np.uint8)
    r0_val = np.zeros(r0_32.shape[0], dtype=np.uint8)
    for j in range(4):
        l0_val |= (l0_bits[:, j].astype(np.uint8) << (3 - j))
        r0_val |= (r0_bits[:, j].astype(np.uint8) << (3 - j))
    return l0_val, r0_val


def run_des_cpa(
    plaintext_npy: str,
    wave_npy: str,
    candidates: int = 4,
    leakage_model: str = "HW",
    target: str = "S-box_out",
    sboxes_to_test: Optional[List[int]] = None,
    points_block: int = 2000,
    corr_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    DES CPA 攻击。

    参数：
        leakage_model: 'HW' / 'ID'
        target: 'S-box_out' / 'S-box_in' / 'S-box_in_xor_out'
                'R_xor_LOut' (硬件 FPGA 推荐，寄存器翻转)
                'LOut' (左半输出的 HD)
        corr_mode: None=auto（'S-box_in' + HW 自动 dual）; 'abs' | 'dual'
    """
    P = np.load(plaintext_npy)
    X = np.load(wave_npy)

    if P.ndim != 2 or P.shape[1] != 8:
        raise ValueError(f"DES plaintext shape expect (n_traces, 8), got {P.shape}")
    if X.shape[0] != P.shape[0]:
        raise ValueError(f"trace count mismatch: plaintext {P.shape[0]} vs wave {X.shape[0]}")

    n_traces, n_points = X.shape
    std_X = X.std(axis=0, ddof=1).astype(np.float64) + 1e-12

    l0_32, r0_32, r0_exp = _get_l0_r0(P)

    if sboxes_to_test is None:
        sboxes_to_test = list(range(8))

    # 自动选 corr_mode
    t_normalized = target.lower().replace("-", "_")
    if corr_mode is None:
        # S-box_in 是纯线性（没过 SBOX 非线性），k/k^0x3F 对称 → 需要 dual
        if t_normalized == "s_box_in" and leakage_model.upper() == "HW":
            corr_mode = "dual"
        else:
            corr_mode = "abs"
    if corr_mode not in ("abs", "dual"):
        raise ValueError(f"corr_mode must be 'abs' or 'dual', got {corr_mode!r}")

    if corr_mode == "dual":
        print(f"[DES-CPA] target={target} + HW -> dual mode (pos/neg candidates)")

    results = []
    best_keys_6bit_pos = [0] * 8
    best_keys_6bit_neg = [0] * 8

    for si in sboxes_to_test:
        r0_6bits = r0_exp[:, si * 6:(si + 1) * 6]
        r0_val = np.zeros(n_traces, dtype=np.uint8)
        for j in range(6):
            r0_val |= (r0_6bits[:, j].astype(np.uint8) << (5 - j))

        # 如果 target 需要 L0/R0 的 4-bit（R_xor_LOut / LOut），预先算好
        l0_4bits = r0_4bits = None
        if t_normalized in ("r_xor_lout", "lout"):
            l0_4bits, r0_4bits = _get_l0_r0_sbox_bits(l0_32, r0_32, si)

        scores_pos = []
        scores_neg = []
        scores_abs = []
        all_scores_by_key = []

        for k in range(64):
            inter = _compute_des_target(r0_val, k, si, target,
                                         l0_4bits=l0_4bits, r0_4bits=r0_4bits)
            L = _leak_transform(inter, leakage_model)
            bp, bn, tidx = _best_corr_signed(X, L, std_X, points_block=points_block)
            scores_pos.append((bp, tidx, k))
            scores_neg.append((bn, tidx, k))
            abs_score = max(bp, bn)
            scores_abs.append((abs_score, tidx, k))
            all_scores_by_key.append(float(abs_score))

        if corr_mode == "abs":
            scores_abs.sort(key=lambda x: x[0], reverse=True)
            top = scores_abs[:max(1, int(candidates))]
            bk = scores_abs[0][2]
            best_keys_6bit_pos[si] = bk
            best_keys_6bit_neg[si] = bk
            results.append({
                "sbox": si,
                "topK": [{"key": int(k), "score": float(s), "time_index": int(t)}
                         for (s, t, k) in top],
                "best_key": int(bk),
                "all_scores": all_scores_by_key,
            })
        else:  # dual
            scores_pos.sort(key=lambda x: x[0], reverse=True)
            scores_neg.sort(key=lambda x: x[0], reverse=True)
            top_pos = scores_pos[:max(1, int(candidates))]
            top_neg = scores_neg[:max(1, int(candidates))]
            bk_pos = scores_pos[0][2]
            bk_neg = scores_neg[0][2]
            best_keys_6bit_pos[si] = bk_pos
            best_keys_6bit_neg[si] = bk_neg
            merged = {}
            for s, t, k in list(top_pos) + list(top_neg):
                k = int(k)
                if k not in merged or abs(s) > abs(merged[k]["score"]):
                    merged[k] = {"key": k, "score": float(s), "time_index": int(t)}
            topK = sorted(merged.values(), key=lambda x: abs(x["score"]), reverse=True)[:max(1, int(candidates))]
            results.append({
                "sbox": si,
                "corr_mode": "dual",
                "topK_pos": [{"key": int(k), "score": float(s), "time_index": int(t)} for (s, t, k) in top_pos],
                "topK_neg": [{"key": int(k), "score": float(s), "time_index": int(t)} for (s, t, k) in top_neg],
                "best_key_pos": int(bk_pos),
                "best_key_neg": int(bk_neg),
                "topK": topK,
                "best_key": int(bk_pos),
                "all_scores": all_scores_by_key,
            })

    recovered_key_pos = _subkey48_to_key64(best_keys_6bit_pos)
    recovered_key_neg = _subkey48_to_key64(best_keys_6bit_neg)

    all_scores = [abs(r["topK"][0]["score"]) for r in results]
    subkey_analysis = [_build_subkey_analysis(r) for r in results]
    _sa_map = {item["sbox"]: item for item in subkey_analysis}
    per_sbox = []
    for r in results:
        top1 = r["topK"][0]
        sbox_idx = r["sbox"]
        sa = _sa_map.get(sbox_idx, {})
        gap = sa.get("top1_top2_gap")
        entry = {
            "sbox": sbox_idx,
            "key": f"0x{top1['key']:02X}",
            "correlation": top1["score"],
            "time_index": top1["time_index"],
            "gap_pct": round(gap * 100, 1) if gap is not None else None,
        }
        if r.get("corr_mode") == "dual":
            entry["key_pos"] = f"0x{r['best_key_pos']:02X}"
            entry["key_neg"] = f"0x{r['best_key_neg']:02X}"
        per_sbox.append(entry)

    low_confidence_subkeys = [
        {
            "subkey_index": item["subkey_index"],
            "sbox": item["sbox"],
            "best_key_hex": item["best_key_hex"],
            "top1_top2_gap": item["top1_top2_gap"],
        }
        for item in subkey_analysis if item["low_confidence"]
    ]
    cpa_avg_correlation = float(np.mean(all_scores)) if all_scores else 0.0
    cpa_min_correlation = float(np.min(all_scores)) if all_scores else 0.0

    # --- gap-based recovery assessment (same logic as AES CPA) ---
    n_subkeys = len(subkey_analysis)
    high_confidence_count = sum(1 for item in subkey_analysis if not item["low_confidence"])
    low_gap_sboxes = [item["sbox"] for item in subkey_analysis if item["low_confidence"]]

    if high_confidence_count >= 6:
        recommended_next_step = "most_sboxes_correct_run_key_search_for_unreliable_only"
        recovery_assessment = (
            f"{high_confidence_count}/{n_subkeys} sboxes high-confidence "
            f"(gap >= {int(LOW_GAP_THRESHOLD * 100)}%). "
            f"Only sboxes {low_gap_sboxes} are unreliable. "
            f"Run key_search to recover the master key (DES has 16-bit ambiguity from parity + PC-2 unselected bits). "
            f"Do NOT switch target/method/alignment yet — for DES hardware HD (R_xor_LOut), avg_corr 0.05-0.08 is NORMAL baseline, "
            f"not a failure signal."
        )
    elif high_confidence_count >= 5:
        recommended_next_step = "alignment_or_multi_strategy_merge_then_key_search"
        recovery_assessment = (
            f"{high_confidence_count}/{n_subkeys} sboxes high-confidence. "
            f"Sboxes {low_gap_sboxes} are unreliable. "
            f"This is the DES gray band: keep the same leakage family in scope, try complementary interval/alignment strategies, "
            f"and merge detail files before key_search."
        )
    else:
        recommended_next_step = "relocalize_or_change_target_before_key_search"
        recovery_assessment = (
            f"Only {high_confidence_count}/{n_subkeys} sboxes are high-confidence. "
            f"Treat this as a red band case: revisit interval selection, start position, or target choice. "
            f"For DES hardware HD (R_xor_LOut), avg_corr 0.05-0.08 can still be normal, so check gap distribution first."
        )

    out = {
        "schema_version": "cpa_detail_v2",
        "n_traces": int(n_traces),
        "n_points": int(n_points),
        "leakage_model": leakage_model,
        "target": target,
        "corr_mode": corr_mode,
        "results": results,
        "subkey_results": results,
        "subkey_analysis": subkey_analysis,
        "recovered_key": recovered_key_pos,
        "cpa_avg_correlation": cpa_avg_correlation,
        "cpa_min_correlation": cpa_min_correlation,
        "high_confidence_count": high_confidence_count,
        "recovery_assessment": recovery_assessment,
        # 保留旧字段兼容已有脚本
        "avg_correlation": cpa_avg_correlation,
        "min_correlation": cpa_min_correlation,
        "per_sbox": per_sbox,
        "low_confidence_subkeys": low_confidence_subkeys,
        "recommended_candidates": max(int(candidates), 30 if low_confidence_subkeys else int(candidates)),
        "recommended_next_step": recommended_next_step,
    }
    if corr_mode == "dual":
        out["recovered_key_pos"] = recovered_key_pos
        out["recovered_key_neg"] = recovered_key_neg
    return out
