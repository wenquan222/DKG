"""
Preprocessing Tools for Side-Channel Analysis

三个核心函数：
1. lowpass_iir_weighted — 加权滑动平均滤波
2. static_align — 静态对齐（互相关 + 阈值过滤）
3. vertical_align — 纵向对齐（基线校正）

形状约定：waves.shape == (n_traces, n_points)
"""

import numpy as np
from typing import Dict


# =========================
# 1) 加权滑动平均滤波
#    s_i = (w * s_{i-1} + x_i) / (1 + w)
# =========================
def lowpass_iir_weighted(waves: np.ndarray, w: int = 10) -> np.ndarray:
    """
    参数:
        waves: (n_traces, n_points) 波形矩阵
        w: 权重 (>0)，越大滤波越强。软件实现通常从2-3试起；
           硬件/EM 场景默认应先尝试“不滤波”，只有有明确证据时再把更强滤波当实验选项
    返回:
        同形矩阵
    """
    if waves.ndim != 2:
        raise ValueError(f"waves must be 2D (n_traces, n_points), got {waves.shape}")
    if w <= 0:
        raise ValueError("weight w must be > 0")

    n_traces, n_points = waves.shape
    out = np.empty_like(waves, dtype=np.float64)
    alpha = 1.0 / (1.0 + float(w))
    beta = 1.0 - alpha

    for t in range(n_traces):
        s = float(waves[t, 0])
        out[t, 0] = s
        for i in range(1, n_points):
            s = beta * s + alpha * float(waves[t, i])
            out[t, i] = s
    return out.astype(waves.dtype, copy=False)


# =========================
# 2) 静态对齐
# =========================
def _pearson_corr(a: np.ndarray, b: np.ndarray) -> float:
    """计算两个一维数组的Pearson相关系数"""
    am, bm = a.mean(), b.mean()
    asd = a.std(ddof=1) + 1e-12
    bsd = b.std(ddof=1) + 1e-12
    return float(np.dot(a - am, b - bm) / ((len(a) - 1) * asd * bsd))


def static_align(
    waves: np.ndarray,
    params: Dict[str, int]
) -> Dict[str, np.ndarray]:
    """
    静态对齐：用参考波形的指定区间作为模板，通过互相关找到每条trace的最佳偏移量。

    参数:
        waves: (n_traces, n_points)
        params: {
            "ref_trace": int,    # 参考波形索引
            "start": int,        # 模板起始采样点
            "length": int,       # 模板长度（采样点数）
            "max_shift": int,    # 最大偏移搜索范围
            "threshold": int     # 相关性阈值 (1-100)，低于此值的trace被丢弃
        }

    返回:
        {
            "aligned": (n_accepted, n_points) — 只包含通过阈值的trace
            "shifts": (n_traces,) — 每条trace的偏移量
            "accepted": (n_traces,) — bool，是否通过阈值
            "correlations": (n_traces,) — 每条trace与模板的最佳相关性
        }
    """
    if waves.ndim != 2:
        raise ValueError("waves must be (n_traces, n_points)")
    n_traces, n_points = waves.shape

    ref = int(params["ref_trace"])
    s = int(params["start"])
    L = int(params["length"])
    K = int(params["max_shift"])
    thr = float(params["threshold"]) / 100.0

    if not (0 <= ref < n_traces):
        raise ValueError(f"ref_trace {ref} out of range [0, {n_traces})")
    if not (0 <= s and s + L <= n_points):
        raise ValueError(f"start={s}, length={L} out of range for {n_points} points")
    if K < 0:
        raise ValueError("max_shift must be >= 0")

    template = waves[ref, s:s + L].astype(np.float64)

    # 搜索范围
    left = max(0, s - K)
    right = min(n_points - L, s + K)
    if right < left:
        left, right = s, s

    shifts = np.zeros(n_traces, dtype=int)
    accepted = np.zeros(n_traces, dtype=bool)
    correlations = np.zeros(n_traces, dtype=np.float64)

    # 参考波形直接通过
    accepted[ref] = True
    correlations[ref] = 1.0

    for t in range(n_traces):
        if t == ref:
            continue
        best_r = -2.0
        best_pos = s
        for pos in range(left, right + 1):
            seg = waves[t, pos:pos + L]
            r = _pearson_corr(seg, template)
            if r > best_r:
                best_r = r
                best_pos = pos

        shift = best_pos - s
        shifts[t] = shift
        correlations[t] = best_r
        accepted[t] = (best_r >= thr)

    # 对通过阈值的trace执行偏移
    aligned_list = []
    for t in range(n_traces):
        if accepted[t]:
            shifted = np.roll(waves[t], -shifts[t])
            aligned_list.append(shifted)

    aligned = np.array(aligned_list) if aligned_list else np.empty((0, n_points))

    return {
        "aligned": aligned,
        "shifts": shifts,
        "accepted": accepted,
        "correlations": correlations,
    }


# =========================
# 3) 纵向对齐（Vertical Alignment / 基线校正）
# =========================
def vertical_align(
    waves: np.ndarray,
    ref_start: int,
    ref_end: int,
) -> np.ndarray:
    """
    纵向对齐：用指定区间的均值做基线校正，消除 trace 间的 DC 偏移差异。

    原理：每条 trace 在 [ref_start, ref_end) 区间内计算均值，然后整条 trace
    减去该均值，使得所有 trace 在基线区间的均值都归零。

    参数:
        waves: (n_traces, n_points) 波形矩阵
        ref_start: 基线参考区间起始点（含）
        ref_end: 基线参考区间结束点（不含）

    使用要点:
        - 参考区间应选在**非加密操作的噪声部分**（如尖峰之前的平坦区域）
        - FPGA/ASIC 硬件实现特别需要纵向对齐（不同 trace 间 DC 偏移可能很大）
        - 纵向对齐**不丢弃 trace**，输出和输入 trace 数量相同
        - 通常在静态对齐之后、CPA 之前执行

    返回:
        (n_traces, n_points) 校正后的波形矩阵
    """
    if waves.ndim != 2:
        raise ValueError(f"waves must be 2D (n_traces, n_points), got {waves.shape}")
    n_traces, n_points = waves.shape

    if not (0 <= ref_start < ref_end <= n_points):
        raise ValueError(
            f"Invalid ref range [{ref_start}, {ref_end}) for {n_points} points"
        )

    # 计算每条 trace 在参考区间的均值
    baseline = waves[:, ref_start:ref_end].mean(axis=1, keepdims=True)

    # 每条 trace 减去各自的基线均值
    return (waves - baseline).astype(waves.dtype, copy=False)
