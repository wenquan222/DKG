"""
Plaintext/Ciphertext Correlation Analysis Tool

对波形的每个采样点，计算其与明文（或密文）字节的Hamming Weight的相关性。
相关性高的区域就是加密运算的泄露区间。

用途：在CPA之前定位目标区间，避免在整段波形上盲目攻击。
"""

import numpy as np


# AES S-box
SBOX = [
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
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16,
]

def hw(x):
    """Hamming Weight"""
    return bin(x).count('1')

HW_TABLE = np.array([hw(i) for i in range(256)])


def correlation_analysis(
    wave_npy: str,
    data_npy: str,
    data_type: str = "plaintext",
    byte_index: int = 0,
    model: str = "HW",
    save_plot: str = None,
) -> dict:
    """
    对波形每个采样点，计算与明文/密文字节的相关性。

    参数：
        wave_npy: 波形文件路径
        data_npy: 明文或密文文件路径
        data_type: "plaintext" 或 "ciphertext"
        byte_index: 分析第几个字节 (0-15)
        model: "HW" (Hamming Weight of raw byte) 或 "SBOX_HW" (HW of S-box output, 需要遍历256个key猜测)
        save_plot: 保存图片的路径（可选）

    返回：
        {
            "peak_region_start": int,    # 相关性最高区域的起始点
            "peak_region_end": int,      # 相关性最高区域的结束点
            "peak_time_index": int,      # 最高相关性的采样点
            "peak_correlation": float,   # 最高相关性值
            "suggested_cpa_range": [start, end],  # 建议的CPA分析区间
            "plot_path": str,            # 图片路径
        }
    """
    waves = np.load(wave_npy)
    data = np.load(data_npy)

    n_traces, n_points = waves.shape

    # 计算每条trace对应的中间值
    byte_vals = data[:, byte_index].astype(np.int32)

    if model == "HW":
        # 直接算明文字节的Hamming Weight
        intermediate = HW_TABLE[byte_vals].astype(np.float64)
    elif model == "SBOX_HW":
        # 对256个key猜测，取相关性最大的（类似mini-CPA）
        best_corr_per_point = np.zeros(n_points)
        for key_guess in range(256):
            sbox_out = np.array([SBOX[b ^ key_guess] for b in byte_vals])
            hw_vals = HW_TABLE[sbox_out].astype(np.float64)
            # 计算与每个采样点的相关性
            hw_mean = hw_vals.mean()
            hw_std = hw_vals.std() + 1e-12
            hw_norm = (hw_vals - hw_mean) / hw_std

            wave_mean = waves.mean(axis=0)
            wave_std = waves.std(axis=0) + 1e-12
            corr = np.abs(np.dot(hw_norm, (waves - wave_mean) / wave_std) / n_traces)
            best_corr_per_point = np.maximum(best_corr_per_point, corr)

        correlation_curve = best_corr_per_point
    else:
        intermediate = byte_vals.astype(np.float64)

    if model != "SBOX_HW":
        # 计算Pearson相关性
        inter_mean = intermediate.mean()
        inter_std = intermediate.std() + 1e-12
        inter_norm = (intermediate - inter_mean) / inter_std

        wave_mean = waves.mean(axis=0)
        wave_std = waves.std(axis=0) + 1e-12

        correlation_curve = np.abs(np.dot(inter_norm, (waves - wave_mean) / wave_std) / n_traces)

    # 找峰值区域
    peak_idx = int(np.argmax(correlation_curve))
    peak_val = float(correlation_curve[peak_idx])

    # 用峰值 50% 作为可视化启发式来圈定峰附近区域。
    # 这是便于后续人工/agent 缩小候选区间的经验规则，不应被当成通用物理阈值。
    threshold = peak_val * 0.5
    above = correlation_curve > threshold
    # 找包含peak_idx的连续区域
    region_start = peak_idx
    region_end = peak_idx
    while region_start > 0 and above[region_start - 1]:
        region_start -= 1
    while region_end < n_points - 1 and above[region_end + 1]:
        region_end += 1

    # 建议的CPA范围：在峰值区域基础上前后扩展20%
    margin = max(50, int((region_end - region_start) * 0.2))
    cpa_start = max(0, region_start - margin)
    cpa_end = min(n_points, region_end + margin)

    # 多字节分析：对字节0-15都做一次，看整体分布
    all_peaks = []
    for bi in range(min(16, data.shape[1])):
        bv = data[:, bi].astype(np.int32)
        hw_v = HW_TABLE[bv].astype(np.float64)
        hm = hw_v.mean()
        hs = hw_v.std() + 1e-12
        hn = (hw_v - hm) / hs
        c = np.abs(np.dot(hn, (waves - wave_mean) / wave_std) / n_traces)
        all_peaks.append(int(np.argmax(c)))

    # 画图
    plot_path = save_plot
    if save_plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 1, figsize=(14, 8))

        # 上图：相关性曲线
        ax1 = axes[0]
        ax1.plot(correlation_curve, linewidth=0.8, color='blue')
        ax1.axvline(peak_idx, color='red', linestyle='--', linewidth=1, label=f'Peak: {peak_idx}')
        ax1.axvspan(cpa_start, cpa_end, alpha=0.15, color='green', label=f'Suggested CPA range: [{cpa_start}, {cpa_end}]')
        ax1.set_title(f'{data_type.capitalize()} Correlation Analysis (byte {byte_index}, model={model})')
        ax1.set_xlabel('Sample Point')
        ax1.set_ylabel('|Correlation|')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 下图：所有16字节的峰值分布
        ax2 = axes[1]
        ax2.bar(range(len(all_peaks)), all_peaks, color='steelblue', alpha=0.7)
        ax2.set_title('Peak Time Index per Byte (all 16 bytes)')
        ax2.set_xlabel('Byte Index')
        ax2.set_ylabel('Peak Sample Point')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_plot, dpi=160)
        plt.close()

    return {
        "peak_region_start": int(region_start),
        "peak_region_end": int(region_end),
        "peak_time_index": peak_idx,
        "peak_correlation": round(peak_val, 4),
        "suggested_cpa_range": [cpa_start, cpa_end],
        "all_byte_peaks": all_peaks,
        "byte_peaks_std": round(float(np.std(all_peaks)), 1),
        "plot_path": plot_path,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        result = correlation_analysis(
            wave_npy=sys.argv[1],
            data_npy=sys.argv[2],
            byte_index=0,
            model="HW",
            save_plot="correlation_test.png"
        )
        import json
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python plaintext_ciphertext_correlation_tool.py <wave.npy> <plaintext.npy>")
