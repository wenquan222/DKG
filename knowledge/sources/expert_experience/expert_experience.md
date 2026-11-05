# 专家经验：侧信道攻击（SCA）分析指南

## 一、整体分析流程

对称加密算法（AES/DES/SM4）的CPA分析，遵循统一的分析流程。

### 统一分析流程

**流程不按波形长短分**：

波形是否已经截取到加密区间，决定第一次 CPA 的命中概率，但不决定用哪种流程。**所有案例都遵循同一个统一流程**：候选区间选择 → direct CPA 试探 → 根据 gap / 相关性决定是否静态对齐与纵向对齐 → 完整 CPA → verify / key_search。已经截好的波形可能在 direct CPA 这一步就命中，没截好的才需要进入对齐、扫描和候选合并。

**规则分层**：
- 本节只写**通用决策原则**，不把具体参数写成普适事实。
- 设备名、start 位置、threshold、max_shift、典型相关性范围这类数值，只能作为**当前数据集 / 当前实验平台的经验先验（lab priors）**。
- 遇到新设备、新采集方式、新实现原型时，优先复用这里的**诊断逻辑**，不要直接套用现成的数值配方。

### 标准步骤（8 步）

**Step 1 — 观察波形特征**
- 波形点数 / 幅值分布 / 是否有多个大尖峰
- 判断**实现原型**，不是只看设备外壳：
  - 软件型 round-state 泄漏：优先考虑 `S-box_out + HW`
  - 硬件型 register-transition 泄漏：优先考虑 HD / XOR 类 target
  - 如果无法确定实现原型，先保留多个候选 target family，在 Step 7 用诊断性试探区分
- **注意**：波形最大尖峰（np.argmax）通常是 IO/协议信号，**不是 S-box 泄漏位置**（详见问题 10）

**Step 2 — 预处理**
- 软件实现：加权滑动平均（权重 2-3），不确定就不滤波
- 硬件实现（FPGA/ASIC）：一般不需要滤波

**Step 3 — 选择候选加密区间**
- 先排除明显的协议通信 / IO / 响应反馈尖峰
- 优先选择**疑似加密区间**：有周期性、重复轮结构、或与明文相关性峰相对应的位置
- 如果当前只能看到多个可疑区间，不要提前裁死；保留 2-3 个候选区间给 Step 7
- **冷读时的 fallback 顺序**：
  1. 先看是否有明显的轮结构 / 周期性
  2. 再看明文相关性 / 统计相关性是否能给出候选区间
  3. 如果前两者都不明显，对 2-3 个候选区间分别做小范围 direct CPA probe
  4. 不要在整段长波形上盲目直接开打，也不要因为一眼看不出区间就默认最大峰是泄漏点

**Step 4 — 第一次 CPA 试探（不对齐，先看信号）**

这是判断”要不要做对齐”的诊断步骤，不是最终 CPA。

- 选合适的 target + leakage_model（见”六、各算法攻击要点”），用保守 `candidates`（如 10-20）
- **不做静态对齐**，直接对 **Step 3 选出的候选加密区间** 跑 CPA（必要时先做 lowpass）
- 读取 CPA 工具输出的 3 个信号：
  - `high_confidence_count`：gap_pct ≥ 15% 的字节数（AES 16 字节，DES 8 个 sbox）
  - 每字节的 `gap_pct = (top1 - top2) / top1 × 100%`
  - `cpa_avg_correlation`（参考，不作主要判据）

**Step 4 决策（决定后续走哪条路）**：

| 情况 | 判据 | 行动 |
|---|---|---|
| **🟢 直接成功** | `high_confidence_count ≥ 13/16`（AES）/ `≥ 6/8`（DES）/ `≥ 3/4`（SM4 单轮） | 跳过 Step 5-7 的对齐与诊断，直接到 Step 8 verify + key_search |
| **🟡 灰色带** | `high_confidence_count` 介于 10-12/16（AES） / 5/8（DES） | 进入 Step 5-7，尝试对齐改善；也可生成 detail JSON 备用于多策略合并 |
| **🔴 信号不足** | `high_confidence_count < 10/16` / `< 5/8` / 多数字节 gap_pct < 10% | 进入 Step 5-7，必须做对齐 / 换 target / 换区间 |

**为什么先不对齐**：
- 如果波形已经聚焦到加密区间（短波形、用户截取/重采过的波形），对齐没必要
- **选错对齐参考位置反而会降低 CPA 质量**：对齐到 IO 反馈 / 协议峰 → 把 S-box 泄漏打散到不同位置（详见问题 7、问题 13、问题 15）
- Step 4 的成本只是一次 CPA（几秒到几十秒），是最便宜的诊断方式

**Step 5 — 静态对齐（仅当 Step 4 灰色 / 红色时）**

- 只在**候选加密区间内**选择参考峰（不用全波形第一个峰或全局最大峰作默认规则）
- `length / max_shift / threshold` 的选择遵循”数据驱动”原则（详见”四、静态对齐”）
- 若一开始没把握，先用保守参数保证区间覆盖，再根据接受率和对齐质量迭代

**Step 6 — 纵向对齐（独立判断，与静态对齐并行）**

**⚠️ 纵向对齐的触发条件与 Step 4-5 无关**。即使 Step 4 直接 CPA 成功，也要判断是否需要纵向对齐。

- **何时做**：
  - 非接触式 EM（14443 / 类似场景，DC 偏移明显）
  - FPGA / ASIC 硬件实现（功耗基线不稳）
  - 任何观察到 trace 叠加图基线区域 std 明显（> 全局噪声 2×）的场景
- **方法**：用**非加密的平坦区域**（通常是加密尖峰之前）作为基线参考，每条 trace 减去自己的基线均值（详见”五、纵向对齐”）
- **注意**：纵向对齐不丢弃 trace，不受 `acceptance_rate` 影响

**Step 7 — 完整 CPA + 诊断分支**

做完 Step 5-6（若需要）后，用处理后的波形重跑 CPA（`candidates` 保守值起步，若 Step 4 就看到部分字节可信度偏低则起步用 20-30）。

读取 4 类信息后做决策：
- `cpa_avg_correlation`（整体参考，**不作主要判据**，会被低信号字节拉低）
- 每字节 / 每 S-box 的 **`gap_pct`**（字节级可信度的正向信号，详见问题 14）
- 恢复字节覆盖率（全部 / 部分 / 局部区段）
- 工具是否真正完成验证（不是 `NOT_VERIFIED`）

**关键判断原则**：
- **主要看 gap 分布，不只看 avg_corr**：`high_confidence_count ≥ 13/16`（AES） / `≥ 6/8`（DES）时，即使 `avg_corr` 很低（如 0.08），**CPA 本质已经成功** → 进入 Step 8
- **避免维度混淆**：
  - 想确认”字节是否对了” → 看 `gap_pct`
  - 想确认”对齐是否稳定” → 看 `alignment_avg_correlation`
  - 想确认”CPA 是否打到泄漏点” → 看 `cpa_avg_correlation` 和 gap 分布联合判断

**诊断分支**（适用于 Step 7 结果不理想的情况）：
- **分支 A：信号强，直接验证**
  - `high_confidence_count` 高且多数 gap_pct 健康 → 直接 verify
  - verify MISMATCH 但低置信字节不多 → 先调大 candidates，再 key_search
- **分支 B：有真实信号，但只恢复了部分字节 / gap 普遍偏小**
  - 不要立即宣告失败
  - 先做互补策略：不同 start、不同参考峰、不同区间、必要时不同 target family
  - 把多个 detail JSON 合并给 `key_search(extra_cpa_detail_files=[...])`
- **分支 C：对齐看起来很好，但 CPA 仍很弱**
  - 优先怀疑”对齐到了错误区间”或”实现原型判断错了”
  - 换 start / 换候选区间 / 换 target family / 换采集通道（功耗 ↔ EM），而不是只微调 threshold
- **分支 D：工具没有真正完成验证**
  - `NOT_VERIFIED`、路径错误、缺少 plaintext/ciphertext `.npy`、schema 读错，这些都属于**验证链路问题**
  - 这种情况不能当作攻击失败，必须先修复验证输入再重试
- **分支 E：做过多策略合并后仍搜不到**
  - `key_search` 搜不到，说明正确字节没有进入候选池
  - 此时再回看：实现原型判断、target family、对齐区间、trace 数量、工具实现本身是否有 bug

**Step 8 — 密钥验证与闭环**
- 用 `encrypt_decrypt_verify` 验证（**必须传 plaintext_npy + ciphertext_npy**，不要手写 hex）
- MISMATCH → 调 `key_search` 搜索近邻密钥；若已做过互补 detail 合并仍失败，再回 Step 7 的分支 E
- NOT_VERIFIED → 不记为攻击失败，先修正验证链路
- DES 密钥：CPA 恢复的 parity bit 全为 0，但加密结果和原始密钥完全一致，不需要还原 parity

**统一触发原则**：
- 是否进入多策略 / 多区间 / 多 start，**由观测结果决定**，不是由波形长短决定
- 不要把某一批案例的参数配方写成未来所有案例的硬规则

**指标语义约定（必须区分清楚）**：
- **对齐接受率 / acceptance_rate**：`static_aligner` 有多少条 trace 通过模板匹配，只反映对齐步骤保留了多少数据
- **对齐平均相关性 / alignment_avg_correlation**：`static_aligner` 输出的模板互相关均值，只反映**对齐步骤本身**是否稳定
- **CPA平均相关性 / cpa_avg_correlation**：CPA 输出的平均相关性，反映**是否真的打到了泄漏点**
- **攻击成败相关的决策一律看 CPA 指标**：优先看 `gap_pct` / `high_confidence_count`，其次看 `cpa_avg_correlation`；**不要**用 `alignment_avg_correlation` 代替
- **反模式**：对齐接受率 100% + 对齐相关性 0.99+ 就以为”攻击健康” —— 错！必须看 cpa_avg_correlation

---

## 二、滤波参数选择

加权滑动平均公式：s_i = (w * s_{i-1} + x_i) / (1 + w)，w为权重参数。

参数建议：
- 软件实现（智能卡、MCU）：权重设为2-3。软件实现的信号特征本身较清晰，过大的权重会导致有用信号被平滑掉，反而降低CPA的成功率。
- 硬件实现（FPGA、ASIC）：一般不需要滤波。
- 注意：权重过大是常见错误，会导致信号失真。如果不确定，宁可不滤波也不要用太大的权重，或者从较小的滤波权重开始尝试。

## 三、静态对齐参考区域的选择方法

对齐参考应该选择**候选加密区间内**稳定、可重复的特征峰，而不是把“全波形第一个突出峰”当成默认规则。

具体做法：
1. 先结合波形形态、明文相关性、历史已知区间或多 start 试探，圈定**候选加密区间**
2. 再在该候选区间内确定幅值门槛：取波形绝对值的均值+3倍标准差作为"突出"的标准
3. 在**候选区间内部**寻找第一个超过该门槛的位置，作为局部参考峰
   示例代码：
   ref_idx = len(wave) // 3  # 选数据集约1/3处的trace作为参考，避免首尾的极端情况
   trace = wave[ref_idx]
   trace_roi = trace[start:end]  # start/end 来自候选加密区间，不要直接对全波形做全局选峰
   abs_trace = np.abs(trace_roi)
   threshold = abs_trace.mean() + 3 * abs_trace.std()
   candidates = np.where(abs_trace > threshold)[0]
   first_peak_pos = start + candidates[0]  # 候选区间内第一个超过门槛的位置
4. 以该位置为中心，选取前后各50-60个采样点作为参考区间（总长度100-120，覆盖1个完整的特征峰周期即可）
5. 参考波形号选择数据集中间附近的trace（如总数的1/3处），避免第一条（可能有采集初始化噪声）和最后一条

为什么强调“候选区间内的第一个”，而不是“全波形第一个”或“全局最大”：
- 全波形里可能有多个幅值更大的协议 / IO 尖峰，它们对 CPA 没价值
- 如果不同 trace 的全局最大值落在不同尖峰上，用 argmax 会导致参考位置不一致
- 候选加密区间内的局部特征峰，才是静态对齐应跟踪的对象

**如何判断 max_shift（最大偏移量）—— 看的是同一个候选特征峰的局部偏移，不是全局最大峰的位置差**：

这是一个常见的知识误区。正确的做法：
1. 先在若干条 trace（如第 2 条、中间一条、最后一条）上，在**同一候选区间内**分别找到局部参考峰的位置
2. 记录这些位置值（比如 412, 424, 453, 489, 520...）
3. **max_shift = 这些位置的最大值 - 最小值**（比如 520-412 = 108，max_shift 设 150 左右）

**绝对不能**这样做：
- ❌ 用 `np.argmax(np.abs(wave[i]))` 找每条 trace 的**全局最大峰**，然后看这些位置的范围
- 因为一条波形可能在 ~500 处有一个大尖峰，在 ~7900 处也有一个大尖峰
- 不同 trace 的 argmax 可能落在不同的尖峰上（83 条在 500 附近，17 条在 7900 附近）
- 这样算出的"范围 7600"是假偏移——实际偏移只有 ~100

**诊断标志**：如果统计出来的"峰值位置标准差"大于波形长度的 30%，几乎可以确定是不同 trace 的 argmax 找到了不同的尖峰，而不是真实偏移。应该改用 mean+3σ 方法找第一个突出峰。

常见错误：
- 直接用np.argmax找全局最大值，当波形有多个大尖峰时不同trace可能匹配到不同峰
- 看到"峰值位置标准差 2800"就认为波形"严重错位"——实际可能只是全局 argmax 找到了不同的尖峰
- 用阈值很低去找峰值，结果找到的全是噪声小峰
- 在没有候选区间判断的情况下，直接把全波形第一个突出峰当成加密区间
- 刻意避开大尖峰，选择波形开头的平坦区域做对齐
- 使用第一条trace（index=0）做参考——第一条可能有采集初始化噪声，应选中间附近的trace


## 四、静态对齐（横向对齐）

目的：消除不同trace之间的水平时间偏移。软件实现通常需要静态对齐。

参考区间选择原则：
- 优先选择具有明显尖峰特征的区域（如sharp peak），这样互相关匹配更准确。
- 参考区间长度应覆盖1个完整的特征峰（100-120个采样点通常足够）。
- 避免选择平坦区域或噪声过大的区域。

参数设置：

- 参考波形号（ref_trace）：建议选择**数据集中间附近**的trace（如总数的1/3处）。避免第一条（可能有采集初始化噪声）和最后一条。
- 参考区间长度（length）：覆盖1个完整特征峰即可，通常100-120个采样点够用。不需要过大。
- 最大偏移量（max_shift）：**这是最关键的参数，必须根据数据确定，不能写死一个小值**。具体做法：
  1. 观察若干条trace（如第2条、中间一条、最后一条）的特征峰位置
  2. 记录峰值位置的最大值和最小值
  3. **max_shift = 峰值位置的波动范围**（即 max_pos - min_pos）
  4. 如果不确定，**宁可大一些也不要太小**——max_shift过大只是计算稍慢，max_shift过小会导致大量有效trace被丢弃
  5. 实际经验：智能卡波形的偏移可能在几百个采样点的量级（如500），不要假设偏移很小就设80-100

- 对齐阈值（threshold）：**当前 benchmark 的实用起点**可从 85 开始。若在这套数据上 threshold=85 仍丢弃超过10-20%，**首先检查max_shift是不是太小**，而不是先降低 threshold。对新设备/新采波链路，这个数值只当弱先验。

**关键原则 —— "好的对齐 = 高接受率 + 合适的 max_shift"**：

正确的对齐逻辑是：
1. max_shift 足够大，覆盖了特征峰在不同trace之间的实际位置偏移
2. length 适中，覆盖了完整的特征峰
3. threshold 从当前平台常用起点（如 85）开始，大多数 trace（95%+）都能通过
4. 只有极少数真正异常的trace被丢弃（<5%）

**反面警示 —— 两种错误模式**：

错误模式1（max_shift太小）：
- max_shift=80-100，实际偏移范围是500
- 大量偏移>100的trace被丢弃，只剩30-50%
- 前半段字节还能恢复（离参考峰近），后半段字节恢复不了（trace数不够）
- **修复**：把max_shift设为实际偏移范围

错误模式2（length太短+threshold太低）：
- length=50, threshold=60
- 接受率虽然高（95%+），但模板只覆盖参考峰极小的一段
- 大量没真正对齐的trace被当成"合格"保留
- CPA全部字节相关性低、gap小
- **修复**：length回到100-120，threshold回到85，max_shift设为实际偏移范围

## 五、纵向对齐（Vertical Alignment）

目的：消除不同trace之间的功耗/电磁基线偏移（DC offset）。不同trace的基线电平可能不同，导致CPA相关性被噪声淹没。

适用场景：
- **软件实现一般不需要纵向对齐**
- **硬件实现（FPGA、ASIC）通常需要纵向对齐**——硬件实现的功耗基线在不同trace之间可能存在较大的纵向偏移，这是FPGA CPA攻击失败的常见原因之一

**纵向对齐的具体方法**：
1. **选择参考区间**：必须是波形中**非加密操作的平坦区域**——通常是加密尖峰**之前**的噪声部分
   - 例如：波形有300个采样点，加密操作的尖峰从第50点开始，那么参考区间选 [0, 40)（前40个点的平坦噪声区域）
   - **绝对不要选加密区间内的尖峰部分作为参考**——那里的信号本身就有波动
2. **计算基线**：对每条trace，计算参考区间内所有采样点的均值
3. **校正**：每条trace减去各自的基线均值，使所有trace在参考区间的均值归零

**执行顺序**：滤波（如需要）→ 静态对齐 → **纵向对齐** → CPA

**不丢弃trace**：纵向对齐不会丢弃任何trace，输出和输入的trace数量完全相同。

**验证方法**：对齐后，画出多条trace的叠加图，基线区域应该基本重合（std 接近0）。如果加密区域的尖峰也对齐了，说明对齐效果好。

## 六、各算法CPA攻击要点

### AES-128
- 攻击位置：第一轮S-box输出（S-box out, round 1）
- 恢复结果：一次CPA恢复全部16个密钥字节
- 泄露模型**取决于实现类型**：

**软件实现（智能卡、MCU）**：
- 泄露模型：Hamming Weight (HW)
- 需要的数据：明文（plaintext）
- 中间值：HW(SBOX[plaintext[i] XOR key])
- 一般不需要滤波，可能不需要纵向对齐
- **典型 SNR 范围**（相关性量级参考，决定 candidates 选多少）：
  - 接触式智能卡（7816）、STM32F103 等：平均相关性 0.30-0.50，top 1 基本就对，candidates=10 够用
  - STM32F429（Cortex-M4，缓存/分支时序噪声大）：平均相关性 **0.15-0.25**，top 1 可能错 2-4 个字节，**建议 candidates ≥ 20**，部分字节可能排到 rank 10-20
  - 非接触式 EM：信号弱但噪声多，建议 candidates ≥ 30

**遇到低相关性（< 0.25）的决策规则**：

不要盲目重调对齐和 target，按以下判断：
1. **先判断是不是当前平台的低 SNR 常态**：STM32F429/Cortex-M4/非接触式 EM 的平均相关性本来就可能落在 0.15-0.25，这说明“不能只看 avg_corr 下结论”，不是自动宣告失败
2. **但也不要据此排除区间/对齐问题**：如果 `high_confidence_count` 低、只恢复局部字节，或不同 start 呈明显互补，仍要优先检查候选区间和对齐 start
3. **判断 target**：软件实现（MCU/智能卡）优先固定在 `S-box_out` + HW，除非有强证据说明实现原型判断错了；不要把低相关性直接解释成“该换 target”
4. **正确做法**：先看 gap 分布。如果已经有较多高 gap 字节，则把 `candidates` 调到 20-30 再 key_search；如果 gap 普遍很差，则回到区间 / 对齐 / 多策略合并
5. **只有在 3-5 组互补区间/对齐策略都落在同一低量级时**，才把它当作当前采集通道的 SNR 上限；这时再接受“需要更多 trace”或“只能 candidates+merge+key_search 补救”

**硬件实现（FPGA、ASIC）**：
- 泄露模型：**HD（Hamming Distance，汉明距离）**——通过 target 的 XOR 组合表达，leakage_model 仍选 HW
- 推荐尝试的 target（按优先级）：
  1. `S-box_in_xor_prev_ct`（即 HD 模型：寄存器翻转的汉明距离）：HW(pt[i] ^ key ^ ct[i-1])，需要密文文件
  2. `S-box_out`：HW(SBOX[pt ^ key])——有些硬件实现也能用标准 HW 模型
  3. `S-box_in_xor_out`（即 HD 模型：S-box I/O 间的汉明距离）：HW((pt ^ key) ^ SBOX[pt ^ key])
- 需要的数据：明文（plaintext）**和密文（ciphertext）**
- 原理：FPGA 的加密寄存器在两次加密之间**保留上一次的密文**。新一次加密开始时，寄存器从 `ciphertext[i-1]` 翻转到 `plaintext[i] XOR key`（S-box 输入），功耗与翻转比特数成正比
- 第一条 trace（i=0）没有"上一次密文"，退化为 HW(plaintext[0] XOR key)
- 一般不需要滤波，可能需要纵向对齐
- 波形通常很短（如 150 个采样点），max_shift 可能也很小
- **如果一种 target 的 gap 很小（< 10%），换另一种 target 重试**，不同硬件实现的泄漏位置不同

#### HD 模型的 k ↔ k^0xFF 对称性问题（重要！）

HD 线性模型（`S-box_in_xor_prev_ct`）存在一个**数学上固有**的二义性：对任意密钥猜测 k，k 和 k^0xFF 的相关性绝对值完全相等，方向相反。

**为什么**：
- 中间值 = pt ^ k ^ ct_prev（线性表达）
- 换 k' = k^0xFF → 中间值变 pt ^ k ^ 0xFF ^ ct_prev = 原中间值 ^ 0xFF
- HW(x ^ 0xFF) = 8 - HW(x)（汉明重量互补）
- 所以 corr(k^0xFF, trace) = -corr(k, trace)，|corr| 完全相等

**后果**：如果 CPA 只看 |corr|，它无法区分 k 和 k^0xFF —— 16 个字节各有 50% 概率选到正确值或互补值。典型症状是恢复出的密钥每字节要么正确、要么是正确值 XOR 0xFF，混杂出现。

**解决方法**：`aes_cpa_attack` 工具检测到 target=`S-box_in_xor_prev_ct` + HW 时会自动启用 **dual 模式**，返回两套密钥候选：
- `recovered_key_pos`：最正相关（+corr 最大）拼出的密钥
- `recovered_key_neg`：最负相关（-corr 最大）拼出的密钥

两套互为 bit-wise 互补（每字节差 0xFF），其中**有且仅有一套是正确密钥**。

**使用方法**：
1. 拿到 CPA 结果后，用 `encrypt_decrypt_verify` **先试 recovered_key_pos**
2. 如果 MISMATCH，**再试 recovered_key_neg**
3. 其中一套必然通过验证

**为什么不能硬编码选正或选负**：功耗/电磁采集的极性取决于物理探头连接方向、采集设备的放大器极性、被测芯片的电流方向等多种因素。同一个 FPGA 实现，换一个采集设置可能正/负相关的方向就反过来。所以不能先验假设"真实 k 对应最负相关"。dual 模式返回两套让 verifier 选，才是物理上严谨的做法。

**对其他 target 不适用**：只有 `S-box_in_xor_prev_ct`（及其他纯线性 HD target）有这个问题。`S-box_out` 经过了 S-box 的非线性，k 和 k^0xFF 给出的 S-box 输出完全不同，不存在互补对称性，直接用 |corr| 排序即可。

### DES-64
- 攻击位置：第一轮S-box输出
- 恢复结果：一次CPA恢复8个密钥字节（通过8个S-box各恢复6-bit子密钥，反推64-bit主密钥）
- 泄露模型**取决于实现类型**：

**软件实现（智能卡、MCU）**：
- 泄露模型：Hamming Weight (HW)
- target: `S-box_out`（默认）
- 需要的数据：明文（plaintext）

**硬件实现（FPGA、ASIC、非接触式智能卡）**：
- 泄露模型：**HD（Hamming Distance，汉明距离）**——通过 target 的 XOR 组合表达，leakage_model 仍选 HW
- 推荐尝试的 target（按优先级，对照 Detector DES 的 4 种 target）：
  1. **`R_xor_LOut`**（**强烈推荐，硬件 FPGA 标准**）：HW(R0 ^ L0 ^ F)——DES 寄存器在一轮内的翻转量。对应 Detector DES target 1（R XOR LOut）。物理含义：DES 每轮结束时 R 寄存器从 R(i-1) 翻转到 R(i) = L(i-1) ^ F(R(i-1), K)，翻转比特数就是攻击的能量泄漏。8 个 S-box 各贡献 4 个 F-bit 位置（经 P 置换），本地计算 HW 只需要各 S-box 的 4 个 F-bit + 对应 L0/R0 bit 位置
  2. `LOut`：HW(L1_4bits) = HW(L0 ^ F)——本轮左半输出的 HW
  3. `S-box_in_xor_out`（即 S-box 输入输出间的 HD）：HW((E(R0) ^ K) ^ SBOX[E(R0) ^ K])——6-bit 中高 2-bit 线性，低 4-bit 经 SBOX 非线性
  4. `S-box_out`：HW(SBOX[E(R0) ^ K])——有些硬件实现也能用标准 HW 模型
  5. `S-box_in`：HW(E(R0) ^ K)——线性，k/k^0x3F 对称，自动启用 dual 模式
- 需要的数据：明文（plaintext）——注意 DES 硬件 target（R_xor_LOut, LOut）**不需要**密文
- **实证结果（非接触式智能卡 DES-14443）**：`R_xor_LOut` 可以恢复部分字节（S0 相关性 ~0.08，其他 0.04），而 `S-box_out` / `S-box_in_xor_out` 均无法识别任何字节（全部 0.04 相关性）。硬件 DES 首选 `R_xor_LOut`。
- **如果相关性普遍低（< 0.05）且 gap 很小**：优先换 target 为 `R_xor_LOut`，再调整纵向对齐的参考区间
- 特殊说明：DES密钥每个字节的最后一位是奇偶校验位。**CPA恢复的密钥校验位全部为0，这是正确且预期的结果**。详细解释：
  - DES 内部通过 PC-1 置换选取密钥的 56 个有效位，**丢弃每字节第 8 位（校验位）**
  - 因此原始密钥 `1122334455667788`（校验位=1）和 CPA 恢复的 `1022324454667688`（校验位=0）的**有效 56-bit 密钥完全相同**
  - 用任何一个加密同一段明文，**得到的密文完全一样**——所以 CPA 恢复的"校验位为0的密钥"可以直接用于加密验证，不需要还原校验位
  - **验证时**：直接用 CPA 恢复的密钥（校验位为0）调用 `crypto_verify` 验证即可。如果验证通过（MATCH），说明密钥恢复正确
  - **如果验证不通过**：不要认为是校验位的问题——校验位不影响加密结果。应该检查 CPA 的 top1-top2 gap，gap 小的字节可能恢复错误


### SM4-128
- 攻击方式：4 轮依次 CPA，每轮恢复 4 字节 round key，第 N 轮需要前 N-1 轮的 round key 作为输入
- 完成 4 轮后自动反推 128-bit 主密钥
- target 选项（对照 Detector SM4FirstOrder）：
  1. `S-box_out`（默认，推荐）：HW(SBOX[xor_b ^ k])——软件标准，Detector target 2
  2. `S-box_in_xor_out`：HW((xor_b ^ k) ^ SBOX[...])——S-box I/O 间的 HD，Detector target 1
  3. `S-box_in`：HW(xor_b ^ k)——线性，k/k^0xFF 对称，自动启用 dual 模式
- SM4 没有对应 AES 的 HD(hardware) 跨加密 target（因为 SM4 4 轮攻击已经是跨轮状态，不需要跨加密寄存器翻转）
- 波形上 4 轮 S-box 区间**从前往后依次排列**，调 `wave_start` / `wave_end` 分别定位每轮区间


## 七、密钥恢复验证

CPA攻击恢复密钥后，必须验证密钥的正确性。

验证方法一：观察每字节的 `gap_pct` 分布（详见问题 14 的三段带定义）
- `gap_pct ≥ 15%` → 高可信，该字节已恢复正确
- `gap_pct` 在 10%-15% → 灰色带，放入 key_search 候选池
- `gap_pct < 10%` → 接近零信号，需改善 CPA 或大幅增大 `candidates`

注意：如果攻击位置选的是S-box输入（而非S-box输出），可能会出现排名第1和第2拉不开差距的情况。这是因为S-box输入端存在线性相关问题——猜测密钥之间只差1bit时，相关性依然很高。这也是为什么推荐使用S-box输出作为攻击位置，而不是S-box输入。

验证方法二：加密比对
使用恢复的密钥对已知明文进行加密，将加密结果与对应的密文逐字节比较。如果完全匹配，则密钥正确。
前提：需要用户提供密文文件。如果用户只提供了明文和波形而没有密文，应主动要求用户提供密文文件，因为没有密文就无法通过加密比对来验证密钥。

## 八、常见问题诊断

### 问题1：静态对齐后丢弃的trace过多（>5%）
好的对齐在threshold=85时应该保留95%以上的trace。如果丢弃率超过5-10%，**首先检查max_shift是不是太小**：
- **最可能的原因**：max_shift太小，没覆盖实际的位置偏移范围。**先观察几条trace的特征峰位置波动范围，把max_shift设为该范围**
- 参考区域选择不当（特征不明显）：重新选择有sharp peak的区域
- 阈值不是第一个该调的——在max_shift足够大的情况下，85的阈值通常不会导致大量丢弃

### 问题2：CPA分析无法恢复正确密钥
可能原因及解决方案：
- 滤波过度：检查滤波权重是否过大（从小的权重做起）
- 对齐效果不好：检查对齐后的波形叠加图，确保特征位置已对齐
- 攻击位置选错（如用了S-box输入而非输出）

### 问题3：CPA验证失败后的排查顺序

当CPA恢复的密钥验证失败时，**必须按以下优先级排查，不要乱序乱试**：

**排查优先级（从高到低）**：

**0. （最高优先级）先看 gap 分布判断 CPA 是否已经成功**
   - 读 CPA 结果的 `high_confidence_count` 和每字节 `gap_pct`
   - 如果 `high_confidence_count ≥ 13/16`（AES）或 `≥ 6/8`（DES）：**CPA 已经成功**——验证失败只是因为少数低 gap 字节错了
     - **不要换 target / 对齐 / 滤波 / leakage_model**——这些都是对的
     - **正确做法**：扩大 `candidates` 到 30-50，运行 `key_search` 在低 gap 字节的候选池中搜索
     - 详见问题 14（Gap 双向语义）
   - 如果 `high_confidence_count < 10/16`（AES）或 `< 5/8`（DES）：CPA 信号确实不够，才按下面步骤 1-5 排查

1. **对齐位置**（仅当 `high_confidence_count` 低时进入）
   - **先看 CPA 相关性量级，但不要套单一绝对阈值**：
     - 成功量级取决于实现原型、采集方式、trace 数量和 target family
     - 要同时看：`cpa_avg_correlation`、gap 分布、是否只恢复出部分字节 / 部分 S-box
     - 如果对齐接受率 > 95% **但 CPA 仍接近噪声地板，或只恢复局部字节**，优先怀疑对齐到了错误区间
   - 这种情况下换 `max_shift` / `length` / `threshold` / `target` 都没用——都会得到相似的低相关性
   - **正确做法**：试不同的 `start` 位置对齐（比如波形长度 8000，试 1000 / 3000 / 5000 / 7000），选 CPA 相关性最高的位置
   - 详见问题 7

2. **对齐参数**（max_shift / length / threshold）
   - **只有当 CPA 已经显示出真实信号，但 gap 小或局部字节仍不稳时，才调这些**
   - 首先检查 `max_shift`：丢弃率 > 5% 说明 max_shift 太小，不覆盖实际偏移范围
- `length` 以覆盖一个完整特征峰为准；当前 benchmark 常见起点是 100-120，但新设备不应机械照搬
   - 参考波形号选中间附近的 trace（不是第一条或最后一条）
   - 参考区按"mean + 3σ 找第一个超过门槛的峰"选择，不要 np.argmax 全局最大
- **丢弃率是关键指标**：在当前 benchmark 上，好的对齐常见表现是 threshold≈85 时保留 95%+ trace；对新平台仍应以实际丢弃率与 CPA 结果为准

3. **滤波参数**
   - 软件实现权重是否在 2-3 之间？
   - 尝试 `weight=2`、`weight=3`、以及**不滤波**三种设置对比
   - 不要用 `weight > 3`，会导致信号失真

4. **攻击 target**（不要盲目切换）
   - 先判断**实现原型**，再决定 target family：
     - 软件 round-state 泄漏优先 **S-box_out + HW**
     - 硬件 register-transition 泄漏优先 HD / XOR 类 target（AES: `S-box_in_xor_prev_ct`，DES: `R_xor_LOut`）
   - 如果实现原型已经很明确，就不要在同一 family 内盲目切换 target
   - 如果换 target 后相关性、gap、恢复字节分布都几乎不变，问题更可能在区间 / 对齐，而不是 target 本身

5. **波形数量**（最低优先级）
   - trace 是否足够必须放在实现原型、target family、对齐区间都合理之后判断
   - 实际中确实存在"100 条就够"和"需要数千条"两类情况，但这只是**当前 benchmark 的经验分布**
   - 对未知案例，不要先验假设"100 条一定够"或"只要再采一点就能成功"
   - 如果相关性始终贴近噪声地板，先排查 target / 区间；如果相关性稳定存在但候选池一直缺字节，再考虑 trace 不足

**验证失败后的正确决策流程**：

CPA 恢复密钥 → 加密验证 MISMATCH → 分析每字节的 top1-top2 gap → 调用 key_search 在候选中搜索
→ 如果 key_search **找到了**正确密钥 → 完成
→ 如果 key_search **没找到** → **这说明正确密钥字节不在 CPA 的 top K 候选里**

**key_search 搜不到时的正确判断**：
- key_search 搜不到 ≠ "需要扩大搜索范围"或"自己写穷搜代码"
- key_search 搜不到 = **CPA 的候选质量不够**——正确密钥字节没进入 top K
- 正确做法：**改善 CPA 质量，然后合并多次 CPA 的可靠字节**
  1. 先确认 verify 真的跑完了，不是 `NOT_VERIFIED`
  2. 加滤波（如果之前没加）：尝试 weight=2 的加权滑动平均
  3. 调整区间 / 对齐策略：换 start、换 ref_trace、调 max_shift、调 length
  4. 只有在实现原型不确定时，才尝试不同 target family
  5. 重新做 CPA → 拿到新的候选集 → 合并多次结果 → 再用 key_search 搜索

**多次 CPA 结果合并策略**：

单次 CPA 可能只恢复部分字节（比如 byte 0-10 可靠但 byte 11-15 不可靠）。改参数重跑后，不同字节的可靠性分布可能不同。正确做法是**合并每字节的候选池，然后 key_search**：

- 每次 CPA 产出的 detail JSON 里有每字节的 topK 候选及其相关性分数
- 对同一字节，**把所有 CPA 结果的 top-K 候选合并、去重**，形成一个更大的候选集
- 正确密钥只要在**任意一次** CPA 的 top-K 里出现过就能进入合并后的候选池
- 将合并后的候选池交给 key_search 搜索

典型场景：
- 第 1 次 CPA（weight=2 滤波）：byte 0-10 的 gap > 30%（正确密钥在 top1），byte 11-15 的 gap < 5%（正确密钥可能在 top3-5）
- 第 2 次 CPA（不滤波 + 不同对齐参数）：byte 11-15 的 gap > 25%（正确密钥在 top1），byte 0-4 的 gap 只有 15%（正确密钥在 top2）
- 合并后：每个字节的候选池里都包含了正确密钥 → key_search 能找到

**合并时的注意事项**：
- 只有对**同一组波形**的多次 CPA 才能合并（不同波形集不能混用）
- 合并的前提是每次 CPA 的 candidates 参数设得足够大（默认 10），保证候选池有足够覆盖
- 合并后每字节的候选数可能从 10 变成 15-20 个（去重后），组合空间增大但仍在 key_search 的搜索能力范围内
- 如果合并后 key_search 仍然搜不到，说明所有 CPA 里正确密钥都没进入 top-K，需要更根本的改善（更多 trace 或不同的 target/leakage_model）

- **绝对不要做的事**：
  - ❌ 自己写 Python 穷搜代码在候选之外暴力搜索——如果正确值不在候选里，搜多少轮都没用
  - ❌ 根据密钥的数值模式猜测正确密钥——这不是方法论，只对测试密钥碰巧有效
  - ❌ 反复扩大搜索范围（从 top-4 扩到 top-10 到 top-20）——与其搜更多低质量候选，不如改善 CPA 让正确值进入 top-4

**CPA 失败时绝对不要做的事**：

- ❌ **在已经有足够 direct CPA 证据的场景里，仍盲目做明文相关性分析** —— 这会增加复杂度，但不会改进真正的决策链
- ❌ **为了提高接受率盲目降 threshold 和缩短 length** —— 这是牺牲对齐质量换表面数字，必然失败
- ❌ **盲目切换 leakage model（HW ↔ ID）** —— 这几乎从不是真正的故障点，浪费 token
- ❌ **一看到相关性低就下结论"trace 不足"** —— 先回到第 1 步检查对齐参数
- ❌ **在同一组参数的小范围内反复试**（比如 threshold 从 85 试到 84 到 83） —— 期望靠微调出奇迹是徒劳，要从更大的维度（length、max_shift）改
- ❌ **key_search 搜不到就自己写穷搜或猜密钥模式** —— 搜不到说明 CPA 候选质量差，应该回头改善 CPA

### 问题4：DES恢复的密钥每个字节最后一位都是0
原因：这是正常且预期的现象。DES密钥每字节第8位是奇偶校验位，DES内部通过PC-1置换丢弃这些位，只使用56个有效位。
解决方案：
- **不需要还原校验位**——CPA恢复的"校验位为0的密钥"和原始密钥加密结果完全相同
- 直接用恢复的密钥做 crypto_verify 验证即可
- 例如：原始密钥 `1122334455667788` 和 CPA 恢复的 `1022324454667688` 加密同一明文得到**相同密文**
- 如果 crypto_verify 返回 MISMATCH，**不是校验位的问题**——说明某些字节的6-bit子密钥恢复错了，检查对应S-box的top1-top2 gap

### 问题5：对齐后接受率 95%+ 但 CPA 全部字节失败（gap < 10%）

这是最容易误判的场景。典型症状：
- `accepted ≥ 95%`, `alignment_avg_correlation ≥ 0.9`
- CPA 每个字节的 top1 相关性都在 0.4 左右
- top1 和 top2 的差距都小于 10%
- 多次重新运行 CPA 得到不同的密钥

**根本原因**：对齐 `length` 太短 + `max_shift` 太大 + `threshold` 太低的组合。模板只覆盖参考峰极小的一段，大的max_shift让任何位置的波形片段都能和模板"凑合匹配"，低threshold让低质量的匹配也被接受。大量trace表面通过了对齐但实际没有真正对齐到位。

**解决方案**：
1. length 设为 100-120（覆盖一个完整特征峰）
2. max_shift 设为**实际偏移范围**（先观察几条trace的峰值位置波动）
3. threshold 保持 85
4. 重新跑 CPA 验证

**区分"正确的高接受率"和"虚假的高接受率"**：
- ✅ **正确的高接受率**：length=100-120, max_shift=实际偏移范围, threshold=85 → 95%+ 保留 → CPA 恢复密钥
- ❌ **虚假的高接受率**：length=50, max_shift=200, threshold=60 → 95%+ 保留 → CPA 全部字节失败
- 两者的区别在于前者是**max_shift精确匹配了实际偏移**，后者是**length太短+threshold太低"骗"来的接受率**

### 问题6：对齐后只保留了30-50%的trace，前半段密钥恢复正确但后半段错误

典型症状：
- threshold=85，但accepted只有30-50%
- CPA 前半段字节（如byte 0-10）恢复正确，后半段字节（如byte 11-15）错误
- 后半段字节的 top1-top2 gap 极小（<0.05）

**根本原因**：**max_shift 太小**。特征峰在不同trace之间的实际位置偏移超过了 max_shift 的范围，导致超过一半的trace被丢弃。剩余的trace数量不够支撑后半段字节的恢复（前半段因为离参考峰近，对齐效果好，所以少量trace也够用）。

**解决方案**：
1. 观察几条trace的特征峰位置，计算最大偏移范围
2. 把 max_shift 设为该偏移范围
3. 保持 threshold=85，length=100-120
4. 预期：95%+ trace 保留，后半段字节也能恢复


### 问题7：对齐接受率 100% + 对齐相关性 0.99+，但 CPA 相关性低（多 start 扫描诊断）

**典型症状**：
- `accepted = 100/100`（100% 接受率，完美！）
- 对齐 `alignment_avg_correlation = 0.98+`（对齐本身质量极高）
- CPA `cpa_avg_correlation` 仅 **0.15-0.5**（说明有对齐质量，但攻击信号并未同步变强）
- 所有字节 top1-top2 gap 都极小
- **换 target 也没用**（S-box_out / S-box_in / S-box_in_xor_out 都给出相近的低相关性）

**这个症状可能对应两种完全不同的根因，不能用单一阈值判断**：

- **根因 A：对齐到了错误的特征峰位置**（非 S-box 区间）
  - 波形包含非加密操作（命令处理、参数装载、IO 等待），它们也产生大尖峰
  - agent 用 mean+3σ 找"第一个突出峰"时抓到了非 S-box 的峰
  - 波形会对齐得很好（接受率 100%），但那个位置不含 S-box 泄漏
  - **解法**：换 start 位置到真正的 S-box 区间

- **根因 B：当前采集通道 SNR 低**（器件物理特性 + 采集条件）
  - STM32F429 功耗通道（Cortex-M4 缓存/分支时序噪声大）、非接触式 EM 等：**相关性 0.15-0.25 是当前采集通道的 SNR 上限**
  - 不是对齐问题，也不是 target 问题
  - **解法优先级**：
    1. **先确认采集通道**：同一设备的 EM 探头采集和功耗通道采集 SNR 可能差 2-3 倍（功耗通道通常 0.15-0.25，EM 探头 0.4-0.6）。如有条件换通道，优先换
    2. 通道无法换时：接受该相关性，用 gap 分布判断可信字节（详见问题 14）
    3. 提高 `candidates` 到 30+，走 key_search 补救少数低 gap 字节

**区分 A 和 B 的唯一方法：多 start 位置 CPA 扫描**（通用诊断工具）

**扫描步骤**：
1. 先根据**观测现象**决定是否要扫，而不是看波形长短：
   - 单次 CPA 只恢复了部分字节 / 部分 S-box
   - alignment 很好，但 CPA 仍接近噪声地板
   - 不同 target family 的结果都不稳定，怀疑对齐区间选错
2. 列若干候选 start 位置（按可疑区间均匀覆盖，而不是机械按总长度平均切）
   - 短波形也可能要扫
   - 长波形也可能只需要扫 2-3 个关键区间
   - 起点数量取决于“候选区间数”和“单次 CPA 是否只命中局部字节”，不是固定由点数决定
2. 对每个 start 做静态对齐（length=100-150, threshold=85）+ CPA，记录平均相关性
3. **根据扫描结果分支决策**：

| 扫描结果 | 根因 | 行动 |
|---------|------|------|
| **某个 start 相关性显著高于其他（如 1.5× 或更多）** | 根因 A，对齐错位 | 用该 start 完整跑 CPA + key_search |
| **所有 start 相关性都差不多低，但都明显高于噪声地板** | 根因 B，低 SNR / 物理极限 | 任选其一，扩大 candidates，合并多次 detail 后 key_search（参考问题 9 的 lab prior） |
| **所有 start 相关性都极低，且 gap 普遍很小** | 根因 C，target family 选错 / 区间不含泄漏 / trace 不足 | 回看实现原型、改 target family、检查区间选择；最后才考虑加 trace |

**关键原则**：
- ✅ 多 start 扫描是**通用诊断**，无论最终是 A/B/C 哪种根因都靠它分辨
- ❌ **不要把是否扫描写成波形长度规则**
- ❌ **不要反复换 target**：同一实现原型下如果换 target 换来换去相关性都差不多，说明根本不是 target 问题
- ❌ **不要反复调对齐参数**（length/threshold/max_shift 微调）：一旦对齐到了错误位置，调这些参数永远救不回来
- ❌ **不要把对齐平均相关性当成 CPA 平均相关性**：`alignment_avg_correlation = 0.99` 只能说明模板匹配稳定，不能推出 `cpa_avg_correlation` 也高

**案例参考**：
- **DES-7816 根因 A**：波形 8000 点，对齐开头大峰 CPA 仅 0.40；对齐到 start=4557 CPA 直接 0.80。多 start 扫描会看到"4557 附近相关性显著高"，一眼识别是对齐错位
- **STM32F429 根因 B**：所有 start 位置 CPA 都在 0.15-0.25，扫描不到"突出位置"，这就是硬件低 SNR。正确做法是 candidates=20 直接 key_search
- **AES-FPGA 根因 C**：硬件 HD 场景，软件 target 下相关性都极低；必须切 `S-box_in_xor_prev_ct` + dual 模式


### 问题8：agent 陷入参数微调循环（自动化运行策略，非 SCA 普适物理定律）

**当前困境典型场景**：
- agent 连续调用 `static_aligner` 5+ 次，每次只改微调 `threshold` / `max_shift`
- 连续调用 `aes_cpa_attack` 并换 target（S-box_out → S-box_in → S-box_in_xor_out）5+ 次
- 总轮数超过 30 但仍未恢复密钥

这些行为是 agent 的"**局部徘徊**"——在同一个维度上反复试，但问题根源不在那个维度。

**元规则**（主要针对当前 benchmark 的自动化 agent 运行策略，不应直接当作未知世界新案例的硬物理规则）：

1. **"5 次规则"——同一维度 5 次无改善即换维度**
   - 调对齐参数 5 次（`max_shift` / `length` / `threshold` 任意组合）仍未让 CPA 相关性提升 > 20% → 换对齐 `start` 位置（不是调参数）
   - 调对齐 `start` 位置 5 次都没出现明显高于噪声地板的稳定信号 → 不是单纯对齐问题，是实现原型 / target family / trace 数问题
   - 换 target 5 次（所有可用选项都试过了）都没改善 → **停止换 target**，重审 trace 质量或 SNR

2. **"相关性条件化判断"——区分低 SNR、区间错位和根本失败**
   - 不要使用单一绝对阈值跨案例判定成败
   - 要联合看：`cpa_avg_correlation`、gap 分布、恢复字节覆盖率、同类策略之间是否互补
   - 如果 CPA 明显高于噪声地板且只是 gap 小 / 个别字节错 → 优先扩大 candidates + key_search
   - 如果 alignment 很好但 CPA 仍接近噪声地板 → 优先怀疑区间错位或 target family 错
   - 如果多种互补策略都只能恢复固定局部字节 → 优先走候选池合并，而不是无限调单次参数

3. **"轮数上界"——简单案例 25 轮退出机制**
   - 软件 MCU / 智能卡的 AES/DES/SM4 在正常情况下应该 **15-20 轮**完成
   - 如果到 25 轮还没恢复密钥 → **不是简单案例，先诊断不是"继续调"**：
     - 多 start 扫描一次看是不是对齐错位
     - 或判断是不是需要硬件 target
   - 如果到 40 轮还没结果 → 强制结束，标记为失败等人工分析

4. **"反早放弃保护"——证据不足时不要结案 FAIL**
   - 典型反模式：连续几次 verify FAIL + 一次 key_search 找不到就放弃，但同类案例往往需要十几轮到几十轮的反复调参才能恢复
   - **规则**：
     - 在尝试完"对齐参数 / start 位置 / target family / candidates"这几条主线之前，不接受失败结论
     - `key_search` 第一次返回 MISMATCH → **必须** retry：调大 `candidates` 到 30+ 再跑一次 cpa，把新 detail 加到 `extra_cpa_detail_files` 让 key_search 合并候选池再搜
     - `key_search` 连续 3 次 MISMATCH 才能判定"候选池不够"，此时换对齐 start 或 target 重启 cpa
   - **早放弃的征兆**（self-check）：
     - 总 cpa 调用次数 ≤ 2 但 verify 已经 FAIL
     - 总 key_search 调用次数 ≤ 1 但已经判定整 case 失败
     - 没有试过换 start / 换 target 就写"无法恢复"
   - **与"5 次规则"的关系**：
     - "5 次规则"是反 over-iteration（在错误维度上反复试 5+ 次徒劳）
     - "反早放弃保护"是反 under-iteration（在正确维度上没试够就放弃）
     - 两者不冲突：在**正确维度**上至少试到 5 次；如果 5 次仍无改善，**换维度**继续


### 问题9：[弱先验 / lab prior] 设备 SNR 基线参考表（具体数值，仅供参考）

本表总结当前实验平台上的**实测数据**，供判断相关性量级是否正常。注意：
- **这些是当前 benchmark / 当前采波设置下的实测参考，不是通用物理常数**
- 新设备、新探头、新放大链路、新归一化方法下，绝对值都可能变化
- 因此本表只能作为 **lab prior**，不能直接写成“未知案例的硬阈值”

| 设备类型 | 典型相关性范围 | 推荐 candidates | 备注 |
|---------|--------------|----------------|------|
| 接触式智能卡（7816）+ 软件 AES/DES/SM4 | **0.30-0.80** | 10-20 | 信号清晰，top 1 基本就对 |
| STM32F103 等低性能 MCU（功耗） | 0.30-0.50 | 10-20 | 和智能卡接近 |
| **STM32F429（Cortex-M4，功耗）** | **0.15-0.25** | 20-30 | Cortex-M4 缓存/分支时序，硬件 SNR 低 |
| **STM32F429（Cortex-M4，EM 探头采集）** | **0.4-0.6** ⚠️ | 10-20 | 单次采集参考（1000 trace × 1000 点，直接 CPA 16/16 全对）。**需要更多独立采集验证**才能作为稳定先验；换探头位置 / 近场屏蔽条件 / 放大链路可能给出不同结果 |
| 非接触式智能卡 AES（14443）EM | **0.10-0.22** | 30-50 | 信号中等，直接 CPA 可恢复大部分字节，少数字节需 key_search |
| **非接触式智能卡 DES（14443）硬件 HD（R_xor_LOut）** | **0.05-0.08** | 20-30 | 硬件 HD 天然低，但 8 sbox top-1 基本就对，key_search 即可恢复 master key |
| FPGA 硬件 + 正确 target + 纵向对齐 | 0.15-0.30 | 20-30 | HD 模型天然比 HW 低 |
| FPGA 硬件 + 错误 target | < 0.10 | N/A | 需要换 target 不是换 candidates |

**重要差异提示**：

- 同一设备（STM32F429）**采集方式不同**，信号量级差异显著：
  - 功耗通道（电流探头/分压电阻）：avg_corr 0.15-0.25（低 SNR）
  - EM 探头（Langer 近场探头）：avg_corr 0.4-0.6（高 SNR，因为 EM 探头能靠近泄漏源）
- **推论**：不能只按"设备型号"查表，还要看"采集通道"和"波形点数 / 采集带宽"

**使用 gap% 而不是 avg_corr 来判断**：

此表给出"典型相关性量级"，但**决策不应只看 avg_corr**。真正可靠的判断是 `high_confidence_count`（高 gap 字节数）：

- 即使 avg_corr 落在低区间（如 DES 14443 R_xor_LOut 的 0.065），只要 `high_confidence_count ≥ 6/8` → CPA 已经成功
- 即使 avg_corr 看起来"不错"（如 0.3），但 `high_confidence_count` 只有 5/16 → CPA 其实不可靠，需要改对齐或换 start
- 详见问题 14（Gap 双向语义）

**使用方法**：
- 看到新设备/新波形时，先查表找"典型范围"
- **如果实测相关性落在典型范围内**：这只能说明“信号量级不离谱”，**不能**直接推出“当前区间/对齐已经最优”或“现在就该直接 key_search”
- **如果实测相关性远低于典型范围**：不是硬件问题，是对齐/target/trace 问题
- **如果实测相关性远高于典型范围**：信号异常好（比如泄漏模板匹配度特别高），直接 CPA top 1 就能恢复

**本表会随着新案例加入持续扩展**。对于未在表中的设备，不要直接套某一行的绝对值；应先按实现原型判断它更像“软件 round-state”还是“硬件 register-transition”，再把这里的数值当作弱先验。

**⚠️ 重要副作用警示**：

此表是**起点参考**，不是**终止条件**。常见反模式：
- 看到 STM32F103 的 cpa 0.31 → "落在 0.30-0.50 baseline 内 → OK 不需要再调" → 很快放弃 → 失败
- 同类设备上恢复出 0.91+ 相关性的案例，往往经过多轮对齐参数调整

**关键差异**：基线只回答"是否接近当前平台的已知量级"，**不回答**"是否当前区间/对齐/参数最优"。因此：
- 如果 direct CPA 已经落在绿色带（高 gap 字节足够多）→ 直接 verify + key_search，不要因为 baseline 表再回去强制对齐
- 如果仍在灰色带或红色带 → 才继续做 3-5 组互补区间 / 对齐策略，看能否明显提升
- 只有当这些互补策略都落在同一量级时，baseline 才能被当作“当前采集通道的真实 SNR 上限”

**正确决策流程**：
1. 第一次 cpa 落在 baseline 内 → **先看 gap 分布和 high_confidence_count**
2. 如果已经在绿色带 → 直接 verify + key_search，不再为了“基线内”强制走对齐
3. 如果在灰色带 / 红色带 → 再尝试 3-5 次不同区间 / 对齐配置（多 start 扫描 / 不同 ref_trace / 不同 max_shift）
4. 如果所有尝试都落在 baseline 内且 gap 结构相似（说明真的是该通道的 SNR 上限）→ 才用 candidates=30+ + 多次 cpa 合并 + key_search


### 问题10：波形最大尖峰 ≠ S-box 泄漏位置（CPA 区间选择）

**常见错误**：

用 `np.argmax(np.abs(wave))` 找到全局最大尖峰位置做对齐参考。AES-STM32F429 的全局最大尖峰在 sample 1434 附近（波形末尾的 IO 反馈信号），真正的 S-box 泄漏区间在 sample 150-700。对齐到 1434 后 CPA 只有 2/16 字节对；改到 start=150 后 → 14/16 + merge → 16/16 恢复。

**波形中各类尖峰的物理含义**：
- **协议通信/IO 尖峰**：通常幅值最大、位置在波形开头（命令发送）或末尾（响应发送）。对 CPA **没有价值**
- **加密操作尖峰**：幅值中等，位置在波形中段，有规律的周期性（每轮操作一个周期）。这才是 CPA 要瞄准的

**定位 S-box 泄漏区间的方法**（按可靠性排序）：
1. **明文相关性分析**：HW(plaintext_byte) 与波形各时间点 Pearson，峰值 = 加密区间
2. **多 start CPA 扫描**（统一流程 Step 7）：不同 start 位置跑 CPA 比较 cpa_avg_correlation
3. **目视判断**：加密区间有规律的周期性特征（周期数 ≈ 算法轮数），协议通信是孤立大尖峰

**反模式**：`np.argmax(np.abs(wave))` → 对齐到全局最大 → CPA 打偏。永远不要以为"最大尖峰就是加密操作"。


### 问题11：泄漏分布型案例需要多对齐策略 + CPA 候选池合并

**典型现象**：

AES-14443 的 1900 点波形，byte 0-7 的 S-box 泄漏在 150-770，byte 8-15 在 800-1600。用前半段尖峰（start=164）对齐 → 前 8 字节对但后 8 不对。用后半段尖峰（start=1400）对齐 → 14/16 对。合并 3 种对齐的 CPA detail → key_search → 16/16 完整恢复。

**规则**：
- 某些案例的有效泄漏会**分布在不同时间位置**，单一对齐策略只能命中一部分字节 / 一部分 S-box
- 是否启用多策略，不由“波形长度 > 1000 点”单独决定，而由以下现象触发：
  - 单次 CPA 只能稳定恢复部分字节
  - 换 start 后，不同字节的可靠性分布明显互补
  - `key_search` 搜不到，但不同 detail 文件各自都包含一部分正确候选
- 每个策略生成一个 CPA detail JSON
- 通过 `key_search(extra_cpa_detail_files=[...])` 合并候选池 → 每字节只要在任一策略的 top-K 里出现过就能被 key_search 搜到

**代表样本**：AES-14443（prefix+suffix+wide）、AES-STM32F429（multi-start POI）


### 问题12：DES 硬件 HD target 的信号量级和 master key 恢复

**典型现象**：

DES 硬件（非接触式 / FPGA）使用 `R_xor_LOut` target（轮输入 XOR 轮输出），CPA 相关性在当前 benchmark 上**显著低于软件 HW target**：
DES 硬件（非接触式 / FPGA）使用 `R_xor_LOut` target（轮输入 XOR 轮输出），CPA 相关性在当前 benchmark 上**显著低于软件 HW target**：

| target 类型 | 典型 CPA 相关性 | traces 量级 |
|---|---|---|
| 软件 S-box_out + HW | 0.30-0.80 | 100 |
| **硬件 R_xor_LOut + HW（当前 benchmark）** | **0.05-0.08** | 10000 |

虽然 corr 只有 0.05-0.08，但**真子密钥在每个 S-box 的 top-1**（与 Detector MathMagic 完全一致）。这说明该量级在当前 benchmark 中仍可能是**有效信号**，不能机械地按“< 0.1 = 失败”处理。

**注意**：即使 CPA 所有 S-box rank=1，recovered_key **不是最终密钥**。原因：CPA 恢复 K1（48 bit）→ 反推 64-bit master key 时有 **16 bit 不确定**（8 parity + 8 PC-2 不选的 bit）。其中 8 个 PC-2 不选的 bit **影响加密结果**。
- 直接用 recovered_key 加密 → 大概率 MISMATCH（因为这 8 bit 填了 0）
- **必须调 key_search**（枚举 256 次以内）→ 得到真正的 master key

**反模式**：看到 DES recovered_key 加密 MISMATCH 就以为"CPA 恢复失败"→ 错！subkey 可能完全正确，只是 master key 反推有多解。


### 问题13：对齐质量好 ≠ 攻击会成功（指标分离原则）

**这是最容易误判的问题之一**：

- DES-14443：alignment_avg_correlation=0.997, acceptance_rate=100% → CPA 只有 0.04（对齐到错误区间不影响对齐指标，但 CPA 打在非加密段所以信号为 0）
- AES-STM32F429：alignment_avg_correlation=0.976 → CPA 只有 2/16（对齐到末尾 IO 峰）
- 改到正确区间后，对齐指标可能反而稍差（0.94），但 CPA 14/16 → 16/16

**判断标准**：

| 对齐质量 | CPA 信号 | 诊断 |
|---|---|---|
| 好 | 明显高于噪声地板 | ✅ 一切正常 |
| **好** | **接近噪声地板 / 只恢复局部字节** | **⚠️ 优先怀疑区间错位或 target family 错** |
| 差 | 差 | 对齐参数不对 → 调 max_shift / length / threshold |
| 差 | 好 | 罕见，可能对齐区间刚好覆盖了 S-box，但仍建议复核区间选择 |


### 问题14：Gap 的双向语义（正向可信度 + 负向不可靠）

**核心认知**：

top1-top2 gap（百分比）不是单向的"诊断失败"指标，而是**双向的字节级可信度信号**。

**gap_pct 三段带定义**（百分比 = `(top1 - top2) / top1 × 100%`）：

| gap_pct | 语义 | 处理 |
|---|---|---|
| **≥ 15%** | **高可信**：该字节几乎确定已恢复正确 | 锁定此字节，不动 |
| 10% - 15% | 低可信（灰色带）：该字节可能对也可能错 | 放入 key_search 候选池，增大 `candidates` |
| **< 10%** | **接近零信号**：该字节几乎等于随机猜测 | 必须改善 CPA 质量（对齐 / 滤波 / 换 start）或增大 `candidates` 到 50+ |

（问题 5 里提到的"gap < 10% = 全部字节失败"，指的是**所有字节**都落在这一段；如果只是个别字节 < 10%，可能仍可通过 key_search 补救）

**为什么这个双向性很重要**：

之前工具和知识库里只写了负向语义（把低 gap 字节标记为 `low_confidence_subkeys`），漏掉了正向语义（把高 gap 字节标记为"已恢复"）。agent 在"大多数字节已经对了"的场景下：
- 看到 `avg_corr` 低（比如 0.065）→ 以为 CPA 整体失败
- 没有注意到 14/16 字节 gap_pct 都 > 30%（实际上大多数字节已经对）
- 走到"换 target / 换对齐 / 加 trace"的错误分支，浪费几十轮

**`high_confidence_count` 阈值（按算法）**：

| 算法 | 总字节数 | 成功阈值（≥）| 灰色带 | 红色带（需大改） |
|---|---|---|---|---|
| AES-128 | 16 | **13** | 10 - 12 | < 10 |
| DES-64 | 8（S-box） | **6** | 5 | < 5 |
| SM4-128 单轮 | 4 | **3** | 2 | < 2 |
| SM4-128 四轮总计 | 16 | **13** | 10 - 12 | < 10 |

**关键推论（用于决策）**：

如果 `high_confidence_count ≥ 阈值`：
- **CPA 整体已经成功**
- **不要换 target / 换对齐方法 / 换 leakage_model**——这些维度都是对的
- **只针对少数低 gap 字节走 key_search**：增大 `candidates` 到 30-50，运行 `key_search` 在候选池中搜索
- 若 key_search 失败：对低 gap 字节单独做滤波/调对齐（只针对那几个字节），合并新旧 detail JSON 重新 key_search

**gap 阈值原则 —— 用百分比，不用具体数值**：

- ❌ 不能说"gap > 0.03 算高可信"——因为 avg_corr 本身量级不同（软件 0.3-0.7，硬件 0.05-0.08），绝对数值没可比性
- ✅ 应该说"gap_pct ≥ 15% 算高可信"——百分比是相对量，跨设备、跨算法、跨实现都可比

**典型实例**：

- **AES-14443**：直接 CPA 后 14/16 字节 gap_pct > 15%（达到成功阈值 13），byte 1 gap_pct=1.7%（接近零信号）。正确做法是 key_search byte 1 → 2801 轮找到正确密钥
- **DES-14443（R_xor_LOut）**：avg_corr=0.065（看似很低），但 7/8 sbox gap_pct > 25%（达到阈值 6）。这是硬件 HD 的正常基线，CPA 其实已经成功；key_search 245 轮即恢复 master key
- **AES-STM32F429（EM 波形）**：直接 CPA 后 16/16 字节 gap_pct 65-73%，整体 avg_corr=0.56。**全部高可信**，无需 key_search，直接 verify 成功


### 问题15：[通用原则] Direct CPA Before Alignment（静态对齐不是必须步骤）

**典型现象**：
重采后的 1900pt AES-14443 波形，**直接 CPA**（不做静态对齐）就能恢复 14/16 字节；但按传统"先对齐再 CPA"流程做时，选错了对齐参考位置（start=1350，波形后段的大尖峰），结果 CPA 从 14/16 降到 9/16，key_search 无法恢复。

**原则**：

**静态对齐**是**可选步骤**，不是必须步骤。判断要不要做静态对齐的流程就是 Step 4 的第一次 CPA 试探：

1. **先试直接 CPA**（或 lowpass filter weight=2 + 直接 CPA），不做静态对齐
2. **按 `high_confidence_count` 三段带决策**（见问题 14 的阈值表）：
   - **绿色带**（AES ≥ 13/16 / DES ≥ 6/8 / SM4 单轮 ≥ 3/4）→ **跳过静态对齐**，直接 verify + key_search
   - **红色带**（AES < 10/16 / DES < 5/8 / SM4 单轮 < 2/4）→ 必须做静态对齐
   - **灰色带** → 尝试对齐 + CPA 合并多策略

⚠️ **纵向对齐是独立判断，不在"跳过对齐"的范围内**：
- 即使 Step 4 直接 CPA 成功，若观察到 trace 基线有明显漂移（非接触 EM / FPGA / 硬件）仍应做纵向对齐
- 纵向对齐不丢弃 trace，成本低，疑似有 DC 偏移就做

**什么时候"直接 CPA"大概率能过**（经验判据，不是严格规则）：

- **波形已明确聚焦到加密区间**：用户截取/重采过，trace 叠加图大部分重合，肉眼看不到协议段
- **波形短 + 轮结构清楚**：例如某些按轮分段很明显、或当前工具已能稳定内部定位轮窗口的场景，静态对齐的收益往往很小

**什么时候"直接 CPA"大概率不够**（经验判据）：

- **长波形且包含明显非加密段**：长波形中协议 / IO 段占比大
- **trace 之间目视可见的时间抖动**：叠加图在特征峰位置发散（jitter 超过一个特征峰宽度）
- **Step 4 试探结果落在红色带**：大部分字节 gap_pct < 10%，明确信号不足

**判据优先级**：**不依赖"波形点数"这个单一数值**（2000 点既可能是纯加密段也可能是长波形截出的"还有协议段的中等波形"）。应看**波形结构**和**Step 4 实际 CPA 结果**。

**为什么选错对齐反而更差**：

对齐的本质是"把所有 trace 的特征峰对到同一个时间位置"。如果参考峰**不是**真实的 S-box 泄漏峰（比如选到了 IO 反馈尖峰、协议结束尖峰），所有 trace 被拉到"错误的同步位置"，S-box 泄漏反而被打散到不同位置。原来不对齐时 S-box 泄漏还有部分相干性，对齐后彻底破坏。

**实测实例**：

- **AES-14443**：先选 start=1350（波形后段大尖峰）对齐 → CPA 14/16 降到 9/16，byte 0-5 全错。改为直接 CPA 不对齐 → 14/16 对 → key_search 补 byte 1/4/11 → MATCH
- **AES-STM32F429 EM 波形**：波形 1000 点已经聚焦，直接 CPA 16/16 全对，无需 key_search
- **AES-7816 / AES-STM32F103 / AES-FPGA 等案例**：尚未系统验证"直接 CPA"是否同样更优；因此对这类案例只能说"若 Step 4 落入红色带，就按统一流程进入 Step 5 做对齐"，不能写成 direct CPA 一定失败或一定成功的硬结论

**决策摘要**（与 Step 4-8 流程一致）：

```
Step 1-3: 观察 + 预处理 + 选候选加密区间
  ↓
Step 4: 不对齐，直接 CPA（试探）
  ↓
read high_confidence_count
  ├─ 绿色 (AES≥13, DES≥6, SM4单轮≥3) → 跳到 Step 8（verify + key_search）
  ├─ 灰色                           → Step 5 (静态对齐) + Step 6 (纵向对齐独立) + Step 7 (重做 CPA，考虑合并多策略)
  └─ 红色                           → Step 5 + Step 6 + Step 7（必须调对齐/target）

※ Step 6 (纵向对齐) 不受绿色带影响——观察到 DC 偏移就做
```


## 九、常见反模式与决策原则

本章汇总 non-profiled CPA 中最容易走错的判断，以及对应的正确做法。每条按统一格式展开：

- **触发条件**（Trigger）：什么场景下这条策略应被应用
- **核心原则**（Principle）：策略要表达的因果或决策
- **为什么这样做**（Rationale）：物理/统计/工程根因
- **正确做法**（Correct behavior）：可执行的操作步骤
- **反模式**（Anti-pattern）：必须避免的具体错误
- **经验阈值/参数**（Empirical thresholds）：如果有具体数字
- **适用场景**（Applicability）：这条经验主要覆盖哪些设备 / 算法 / 失败模式

### 9.1 软件实现默认不做纵向对齐（anti-pattern）

**触发条件**：软件实现（接触式/非接触式智能卡，STM32F1/F4/Cortex-M MCU），波形 baseline_std > 0 但**没有可见的 per-trace DC drift**。

**核心原则**：软件实现的供电网络稳定，CPU 时钟带来的循环噪声体现为整段 trace 的恒定 DC 偏置，不需要 vertical alignment（基线校正）。盲目跑 vertical alignment 不会带来 CPA 增益，反而消耗 round 预算。

**为什么这样做**：vertical alignment 是为硬件 FPGA 实现设计的——FPGA 时钟切换会产生 per-trace 不一样的 DC 漂移。软件 MCU 不存在这种 per-trace 漂移；其 trace baseline 在所有 traces 上一致，对齐前后没有差别。

**正确做法**：
1. 软件实现（contact/contactless smartcard、MCU），跳过 vertical_aligner，直接进入 static_aligner（横向对齐）。
2. 仅当观察到 per-trace 显著 baseline 偏移（np.std(baselines) > 0.5 × np.mean(|trace|)）时，才考虑 vertical alignment。
3. FPGA / 硬件实现是 vertical alignment 的合理使用场景。

**反模式**：
- 拿到任何 case 都先跑 vertical_aligner 当作"标准预处理"，浪费 1 个 round。
- 看到 baseline_std > 0 就认为需要 vertical alignment——baseline_std 本来就不可能为 0。

**适用场景**：软件实现（智能卡、MCU，如 AES-7816、STM32F103、STM32F429）默认跳过纵向对齐；硬件实现（FPGA/ASIC）仍然需要，AES-FPGA 是反例。

### 9.2 软件实现的 CPA 低相关性首先不应换 leakage target 族（anti-pattern）

**触发条件**：软件实现（MCU、smartcard）首轮 CPA 返回 cpa_avg_correlation < 0.2、gap 分布不明显。

**核心原则**：软件实现的标准 leakage 模型是 `(S-box_out, HW)`。这是 95% 软件 case 的正确组合。当首轮 CPA 相关性低时，**第一反应不应是换 leakage target 族**（如换成 S-box_in、S-box_in_xor_out 等），而应先排查预处理（对齐区间、滤波带宽）和 trace 质量（信噪比、ROI 选择）。

**为什么这样做**：换 leakage target 是个高维参数，每次切换浪费 1-2 round；如果根因是对齐错或 ROI 错，换 target 不会改善任何东西。先固定 target，调通预处理，再考虑切 target 是更高效的搜索路径。

**正确做法**：
1. 软件 case 默认 `(S-box_out, HW)`。
2. 首轮 CPA 低相关时，依次检查：(a) ROI 是否在加密执行段（variance-peak 区域）；(b) 静态对齐是否做了 + acceptance ≥ 70%；(c) 是否需要简单滤波（low-pass / WMA）。
3. 上述三步走完仍低相关，再考虑切 target 到 S-box_in 或 S-box_in_xor_prev_ct。

**反模式**：
- 看到 first-pass CPA correlation 低，立即把 leakage target 列表轮一遍（5 个 target × 2 个模型 = 10 round 烧光）。
- 在没确认对齐质量前就切 target——切完仍低相关并迷茫。

**适用场景**：软件实现（MCU、智能卡）首轮 CPA 低相关时，先查 ROI 与对齐；典型失败是在 STM32F103 上连续换 4 次 target 仍低相关，根因是 ROI 取到了 plaintext I/O 段。

### 9.3 绿带 (high-confidence count) 区间下不应再做预处理，应直接 key_search（anti-pattern）

**触发条件**：CPA 输出的 high_confidence_count 落在绿带（AES ≥ 13/16, DES ≥ 6/8, SM4 单轮 ≥ 3/4），但 encrypt_decrypt_verify 返回 MISMATCH。

**核心原则**：绿带 hc 表明大部分 S-box 子密钥已被 CPA 正确恢复，剩余少数字节通常是 top-2/3 候选误判。这种局面下**正确响应是调用 key_search**（候选合并 + 暴力枚举近邻），而不是重做对齐或换 leakage 模型。

**为什么这样做**：重做预处理消耗大量 round 预算，而且对已经恢复的字节没有增益；key_search 默认 50000 候选预算可以覆盖 4 个字节范围内的近邻枚举（top-3 per byte ≈ 81 ~ 256 combinations），代价低而且很可能直接命中。

**正确做法**：
1. 看到 hc 在绿带，第一反应：调 key_search 默认参数（50000 候选）。
2. 如果绿带且首次 key_search 未中：升级到 500000。
3. 仍未中：考虑合并多次 CPA 的 candidate（不同 ROI 起点 / 滤波参数下的 cpa_detail）作为输入再 key_search。
4. 仅当 key_search 升级到 5M 仍未中，才考虑回到对齐/target 调整。

**反模式**：
- 看到 verify MISMATCH 立即回到 alignment 或 leakage target 调整，不知道 key_search 是绿带的标准下一步。
- key_search 用 default 失败就放弃 key_search，直接 pivot——应该先升级预算。

**适用场景**：绿带 hc + verify MISMATCH 的非建模 CPA（AES / DES / SM4）；典型是 DES-7816 在 hc=8/8 后由 key_search 直接补出主密钥。

### 9.4 不应把 alignment_avg_correlation 当作 CPA 成功指标（anti-pattern）

**触发条件**：static_aligner 任意一次输出 alignment_avg_correlation ≥ 0.9。

**核心原则**：alignment_avg_correlation（对齐平均相关性）只衡量对齐效果——所有 trace 与参考波形的相似度。它**不衡量 CPA 是否能成功**。两个独立指标必须分开看。

**为什么这样做**：对齐相关性高的物理意义是"参考波形周围 max_shift 半径内能找到匹配段"。如果参考点选错（如选在 plaintext I/O 段而不是 S-box 加密段），对齐结果可以非常好（相关 0.97+, acceptance 100%），但对齐窗口内根本没有 leakage 信号，CPA 必然全军覆没。

**正确做法**：
1. alignment_avg_correlation ≥ 0.9 + acceptance ≥ 70% **只能确认对齐成功**，不代表 CPA 会成功。
2. 必须独立 run aligned CPA 看 hc 才能判断对齐参考点是否选对。
3. 如果 alignment 指标好但 aligned CPA 全字节低 hc，**优先怀疑 ROI 选错**（不在加密段），而不是 CPA 算法/leakage 模型。

**反模式**：
- 把 alignment 100% acceptance 当作"OK，预处理 done"，直接基于此 declare success。
- 见到 alignment 高+aligned CPA 低就推测 CPA 算法有问题——根因往往是参考点选错。

**适用场景**：任何用到 static_aligner 的场景；典型是 DES-14443 对齐相关 0.997、接受率 100%，但 aligned CPA hc=0/8，根因是参考点落在加密前的 I/O bus 区。

### 9.5 静态对齐 max_shift 起始值应大（300+），不能 default 到小（anti-pattern）

**触发条件**：smartcard 或 MCU trace 上首次调 static_aligner。

**核心原则**：smartcard / MCU 的 jitter 范围在 100-500 samples 量级。如果 max_shift 设得太小（如 default 50），实际 jitter 超出此范围会导致大量 trace 被 discard（acceptance < 50%），且对齐窗口内可能不包含真正的目标信号。

**为什么这样做**：max_shift 是搜索半径——大就慢但保险，小就快但容易漏。在 smartcard / MCU 上，先大后小是稳妥策略。如果 acceptance 在 max_shift=300 下 ≥ 80%，可以再缩小观察 acceptance 是否保持。

**正确做法**：
1. 首次 static_aligner：max_shift=300 起步。
2. 观察 acceptance：≥ 70% 通过，否则增大到 500 再试一次。
3. 若 acceptance 仍 < 70%，问题不在 max_shift，而在参考点选择（见 9.6 / 9.4）。
4. 仅当 acceptance ≥ 90% 持续稳定，才考虑缩小 max_shift 提升速度。

**反模式**：
- 用 max_shift=50 或 100 起步，期望快速收敛；结果 acceptance 30%。
- 看到 acceptance 低首先调 threshold 而不是 max_shift。

**适用场景**：smartcard / MCU 上首次配置 static_aligner；典型是 7816 卡 max_shift=50 时接受率只有 30%，调到 300 后升到 75%+。

### 9.6 不应用 np.argmax(wave) 作为 alignment 参考点（anti-pattern）

**触发条件**：长波形（>2000 samples）上选 alignment reference peak。

**核心原则**：np.argmax(wave) 选出来的是整段波形中**最大尖峰**，这往往是触发信号、I/O bus leakage 或采样硬件的开关瞬态——**不是 S-box 加密段**。alignment reference 应从加密执行的"非平坦区间"（variance-peak 区）选取。

**为什么这样做**：触发尖峰在所有 trace 上都很相似，所以以它为 reference 的对齐看起来效果很好（acceptance 100%），但对齐窗口跟着触发段走，加密段的 jitter 没被消除。

**正确做法**：
1. 对齐参考点选择：先看 trace 的 variance / np.std 分布，找加密执行体（variance 高的区间）。
2. 在加密体内挑一个有清晰局部 max 的样本点作为 ref（不是全局 argmax）。
3. 优先使用 plaintext_ciphertext_correlation 工具的输出区间作为参考——但**不是首带**（首带常是 I/O bus，见 9.11）。
4. 接触式 DES smartcard（2000-pt trace）典型加密体在 1000-1300 samples 区间。

**反模式**：
- ref_index = np.argmax(wave)。
- ref_point 选择不看 variance 分布。

**适用场景**：长波形上选 alignment reference peak；典型失败是 DES-7816 用 argmax 选到 1850 处的 trigger 信号，对齐 100% 通过但 aligned CPA 全字节失败。

### 9.7 软件实现：变量方差先于对齐的 ROI 探索（通用原则）

**触发条件**：软件加密实现（MCU: STM32F1/F4/Cortex/AVR/Arduino，或运行软件 crypto 的接触式智能卡）+ 非建模 CPA + 首轮 CPA 不直接成功。

**核心原则**：在做 alignment 之前，先用 variance / energy-signature 分析定位加密执行体在 trace 上的位置。直接对齐 + 直接 CPA 在软件 case 上往往因为 ROI 选错而失败。

**为什么这样做**：软件 case 的整段 trace 包含三个 phase：(a) plaintext I/O bus（前段）、(b) AddRoundKey + key schedule 计算（中前段）、(c) S-box / 加密轮迭代（中段，方差最高）。CPA 的 leakage 信号只存在于 (c)。np.var 在滑动窗口（50-200 samples）下能稳定识别 (c)。

**正确做法**：
1. 调用 python_jupyter 计算 sliding-window variance（窗口 50-200 samples，stride 25-50）。
2. 找 variance 比基线高 2-5 倍的窗口——加密体候选 ROI。
3. 对该 ROI 做 alignment（max_shift 300 起步）+ CPA。
4. 比较 variance-ROI 与 plaintext_ciphertext_correlation 工具的首带结果——若 disjoint，必须选 variance-ROI（见 9.11）。

**经验阈值**：
- variance 滑窗大小：50-200 samples
- ROI 阈值：variance 比基线 ≥ 2.0×（首选 ≥ 3.0×）
- 软件 contact smartcard 2000-pt trace：典型加密体 in samples 1000-1300

**反模式**：
- 拿到软件 trace 直接 static_aligner + aes_cpa_attack（不做 ROI 探索）。
- ROI 选 plaintext-corr 首带（往往是 I/O bus pre-encryption 区）。

**适用场景**：软件实现（MCU、接触式智能卡）+ 非建模 CPA + 首轮 CPA 不直接成功；典型是 STM32F103 先用 variance 定位加密体，再对齐 + CPA 命中。

### 9.8 非建模 CPA 持续低 hc 时应诊断 peak 可靠性而非 target 切换（通用原则）

**触发条件**：非建模 CPA on AES / DES / SM4 + 连续 ≥ 3 轮 CPA 输出 hc 都低（AES < 8/16, DES < 4/8）。

**核心原则**：连续 3 轮 hc 低 ≠ leakage target 选错。先诊断 peak 信号本身的可靠性（trace 数量是否充足、滤波是否过激、对齐是否引入伪影），而不是直接 churn 不同 leakage target。

**为什么这样做**：每轮 leakage target 切换都浪费 1-2 round 预算。连续低 hc 的根因通常在 trace 质量（阶段噪声 / 实测 SNR）而不是 target；如果是 target 错（如 S-box_in vs S-box_out），通常第一次 CPA 就显示出某些字节高 hc。

**正确做法**：
1. 连续低 hc → 先看 cpa_avg_correlation 趋势：是否随 round 单调下降？若下降，说明预处理破坏了信号。
2. 检查滤波 weight：weighted_moving_average 的 weight ≥ 5 在低 SNR case 上会平滑掉 leakage。
3. 检查 alignment：max_shift 是否过大（造成对齐窗口内信号被混合）。
4. 仅当 (1)(2)(3) 都排除，才考虑切 target。

**反模式**：
- 一看到第一次 CPA 低 hc 就遍历 5 个 target——这是高维 churning。
- 不区分"信号质量差"和"target 错"两个独立失败模式。

**适用场景**：软件 case 连续多轮 hc 都低；典型是 STM32F103 上连续 5+ 轮换 target 仍失败，最后发现是 trace 数量不足（约 100 条，需要 250+）。

### 9.9 静态对齐参数调优循环：单调 acceptance + 优先级排序参数扫描 + 70% 门槛（通用原则）

**触发条件**：static_aligner 任意一次 acceptance < 70%，或 agent 准备在已对齐 traces 上跑 CPA 之前。

**核心原则**：静态对齐参数调优有清晰的优先级序：max_shift（最大）> reference_point（次大）> threshold（最小）。每次调参 acceptance 必须**单调上升**——若调整后 acceptance 反而下降，回滚到上一组参数。70% acceptance 是 aligned CPA 的最低门槛；< 70% 不应进入 CPA。

**为什么这样做**：对齐参数空间高维，盲目网格搜索浪费 round。优先级序按"对 acceptance 影响大小"排序——max_shift 调大几乎总是提升 acceptance（除非 ref 错）；reference 调对是 binary（要么对要么错）；threshold 是细调。

**正确做法**：
1. 第一次 static_aligner 失败（acceptance < 70%）：检查 max_shift 是否 ≥ 300。若 < 300，扩大到 500 重试。
2. max_shift 已大但 acceptance 仍低：换 reference point（按 9.6 选 variance-peak 区）。
3. reference 也试过：调 threshold（50 → 70 → 85，往低走）。
4. 上述三步走完 acceptance 仍 < 70%：说明 trace 本身 jitter 严重或不一致，跳过 alignment 直接 CPA 或 vertical_aligner 先做基线校正。

**经验阈值**：
- aligned CPA 进入门槛：acceptance ≥ 70%（绝对硬阈值）
- 单调性：每次调参后 acceptance 必须 ≥ 上一次

**反模式**：
- 调 threshold 而不调 max_shift（次序错）。
- 看到 acceptance 下降不回滚，继续调下去。
- acceptance 50% 就跑 aligned CPA（违反 70% 门槛）。

**适用场景**：static_aligner 接受率低于 70% 时；典型是 STM32F103 上 65% → 调 threshold 反而降到 60% → 回滚 → 改 max_shift 到 500 → 75% 通过 → aligned CPA hc=16/16。

### 9.10 key_search found=false 不是 CPA 失败信号：优先升级预算 + 双模式枚举，再考虑 pivot（通用原则）

**触发条件**：non-profiled CPA on AES / DES / SM4 任意一次 key_search 返回 found=false。

**核心原则**：key_search default 预算（50000 候选）只覆盖前几个 byte 的 top-3 候选合并空间。found=false 不代表 CPA 错，而代表搜索预算不够。**先升级 key_search 预算**（50k → 500k → 5M），同时枚举双模式（k vs k⊕0xFF for AES HD），再考虑 pivot CPA / alignment / leakage。

**为什么这样做**：CPA 在 hc=绿带的情况下，正确密钥几乎肯定在 top-3 候选内。50k 预算等价于 4 字节范围的 top-3（3^4=81）；500k 是 6 字节范围；5M 是 8 字节范围。对 AES (16字节) 完全覆盖需要 3^16 ~ 43M——5M 是合理上限。

**正确做法**：
1. key_search default → found=false：升级到 max_combinations=500000 + gap_threshold=0.05。
2. 仍 found=false：升级到 5,000,000 + gap_threshold=0.0 + max_candidates=64 per byte。
3. AES HD 模式额外：跑 dual mode（同时搜 k 和 k⊕0xFF）。
4. 多次 CPA 候选合并：把不同 alignment / 滤波下的 cpa_detail 文件合并输入 key_search（候选 union 而非交集）。
5. 5M 仍未中：才考虑 pivot CPA target / leakage model / 再做对齐。

**重要：tool 参数类型规范**：调用 key_search / encrypt_decrypt_verify 时，所有 hex 字符串参数（recovered_key_hex、key_hex 等）**必须传 string 类型**（如 "1002324454422688"），不能传 int 类型（如 1002324454422688）。整数会触发 ValueError 或 AttributeError。

**经验阈值**：
- max_combinations 阶梯：50k → 500k → 5M
- gap_threshold 阶梯：0.15 → 0.05 → 0.0
- max_candidates per byte：20 → 40 → 64
- 多次 CPA 合并：仅合并 same-alignment-window 的 cpa_detail（不混合不同对齐窗口的候选）

**反模式**：
- key_search 50k 一次失败就 pivot。
- 多次 CPA 合并跨 alignment（不同对齐下的候选合并意义不明确）。
- AES HD 模式只搜 k 不搜 k⊕0xFF。
- key_hex 参数传整数（1002324454422688）而不是 hex 字符串（"1002324454422688"）—— 工具会报 type 错。

**适用场景**：key_search 返回 found=false 或 verify 因参数类型报错时；典型是 DES-7816 默认 50k 未中、升级到 500k + dual mode 后命中。

### 9.11 对齐锚点：variance-ROI 优先于 plaintext-correlation-ROI（通用原则）

**触发条件**：任何 non-profiled CPA on AES/DES/SM4 在任何设备类（接触式 / 非接触式智能卡 / MCU / FPGA）上选 alignment ROI 时，**variance 分析和 plaintext_ciphertext_correlation 分析给出 disjoint（不重叠）区间**。

**核心原则**：smartcard 或 MCU trace 上**第一个** plaintext/ciphertext-correlation 高带，几乎总是加密前的 I/O bus 或 register leakage 区域（明文字节进入 ALU / DES key 寄存器 / AES AddRoundKey 寄存器时直接出现在 bus 上）。这个区段的相关性可以非常高（|ρ| > 0.3），但**不是 S-box leakage**。对齐锚点必须选 variance-peak 区（加密体），不是 plaintext-corr 首带。

**为什么这样做**：I/O bus 信号非常稳定（0.97 align_corr, 100% acceptance），导致 alignment 指标看起来很完美，但对齐窗口跟着 I/O bus 走，CPA 在该窗口内 hc=0-3 必然失败。这种"deceptively healthy alignment + low aligned CPA hc"是 9.4 现象的子情形。variance-ROI 找的是加密执行体——register switching / ALU activity 提升 per-sample variance——这才是 S-box leakage 所在。

**正确做法**：
1. 先做 variance / energy-signature ROI 分析（按 9.7 标准做法）。
2. 同时做 plaintext_ciphertext_correlation 分析。
3. 比较两个 ROI：若 IoU ≥ 0.3（重叠），任意可用，优先精细化的；若 disjoint，**强制选 variance-ROI**。
4. 若 alignment 指标好但 aligned CPA hc 低（AES ≤ 8/16, DES ≤ 4/8, SM4 ≤ 2/4 per round），**首要怀疑锚点选在 I/O bus**，再次 anchor 到 variance-peak 重做。

**经验阈值/参数**：
- IoU 阈值：< 0.3 → 视为 disjoint
- deceptive alignment 签名：align_corr ≥ 0.95 + acceptance ≥ 90% + aligned CPA hc ≤ block_byte/2 → 锚点错
- 接触式 DES smartcard 2000-pt：plaintext-corr 首带通常在 samples 400-700（I/O bus），加密体在 samples 1000-1300（variance peak）

**反模式**：
- 拿到 plaintext-corr 工具输出，选第一个高带作为对齐锚点。
- 看到 alignment 指标 0.97 + acceptance 100% 就认为对齐 OK，不验证 aligned CPA。
- 在 disjoint ROI 情境下选 plaintext-corr ROI 而非 variance-ROI。

**适用场景**：variance 与 plaintext/ciphertext 相关性给出不重叠区间时；典型是 DES-7816 的 plaintext-corr 首带在 533 附近（I/O bus），variance 峰在 1123 附近（加密体）。

### 9.12 DES K1 → master key 反推协议（通用原则）

**触发条件**：DES non-profiled CPA on round 1 已恢复高置信 K1（hc ≥ 6/8, gap_pct ≥ 20%），但 encrypt_decrypt_verify 返回 MISMATCH。DES CPA 工具可能在 master_key 字段填了占位值（K1 + zero padding 或 arbitrary parity 猜测），不是真实主密钥。

**核心原则**：DES master key 是 64-bit（含 8 parity bits），CPA on round 1 仅恢复 48-bit subkey K1。从 K1 反推 master key 需要：(a) PC-2 反置换恢复 56-bit C1‖D1（缺 8 bit, PC-2 没选的位置）；(b) 反向左移 1 步恢复 C0‖D0；(c) PC-1 反置换得 64-bit master key（含 8 个未知 parity bit）。总搜索空间 = 2^8 (PC-2 缺) × 1 (parity 由字节奇偶规则锁定) = 256 candidates，**完全在 key_search default 50000 预算内**。

**为什么这样做**：DES 的 8 个 PC-2 不选位置（标准 FIPS 46-3）固定为：{9,18,22,25,35,38,43,54}（1-indexed），这 8 个 bit 不影响 K1 但影响 master key 加密结果，必须枚举。8 个 parity bit 由"每字节奇偶"规则确定（已知非校验 7 bit → parity 1 bit），不需要独立枚举。所以理论搜索空间 256 candidates。

**正确做法**：
1. DES CPA 高置信 K1 + verify FAILED → **不要 pivot CPA target / leakage model / preprocessing**。K1 本身大概率是对的，问题在 K1 → master key 反推。
2. 调 key_search --algo des on cpa_detail file. Default 50000 预算覆盖 256 candidates。**注意 recovered_key_hex 参数必须传 string（"1002324454422688"），不能传 int**。
3. 若 key_search 返回 found=true 但 master_key 与 CPA 工具的 master_key 字段不同——以 key_search 结果为准（CPA 工具的 master_key 字段是占位值）。
4. 若 default 预算下 found=false，升级到 500000（按 9.10 的升级阶梯）。500k 后仍未中，说明 K1 本身有 ≥ 1 个 S-box 子密钥错（HD ≥ 1 from true K1）——此时才考虑 pivot 到 round 2 CPA（contactless / FPGA 场景用 R_xor_LOut）或重收 traces。
5. （fallback）如果 key_search 不支持 DES PC-2 反置换：在 python_jupyter 中手实现：256 个 missing-bit 赋值 → 用 PC-2 反置换 + 反向左移 + PC-1 反置换 + 字节奇偶规则得 64-bit candidate → 用 encrypt_decrypt_verify 验证（key_hex 传 string）。最多 256 次验证。
6. DES-14443 硬件 HD case：用 R_xor_LOut target 恢复的 K1 走完全相同的 master-key 反推协议，不需要特殊处理。

**经验阈值**：
- K1 高置信：hc ≥ 6/8 + gap_pct ≥ 20% + avg_correlation 适合设备类
- 预期 master-key search space：256 candidates（worst case 65536 if parity 也独立枚举）
- key_search 默认预算（50000）已远超需要

**反模式**：
- 把 DES CPA 工具的 master_key 字段当成最终密钥（它常是 K1 + 0 padding 或 arbitrary parity 猜测）。
- K1 高置信 + verify FAILED → 立即 pivot CPA 参数 / preprocessing。
- 手工伪造 master key（K1 重复、K1 + 0 padding、随机 parity 猜测）。
- verify FAILED 后跳过 key_search 直接换 leakage target。
- key_search 调用时把 recovered_key_hex 写成整数（如 1002324454422688）—— 工具因 type 错失败。

**适用场景**：DES non-profiled CPA 已恢复高置信 K1、但 master key verify 返回 MISMATCH 时；典型是 DES-7816 由 key_search 补出主密钥。

### 9.13 没有 encrypt_decrypt_verify MATCH 之前不应宣告成功（anti-pattern）

**触发条件**：任何 non-profiled CPA workflow on AES / DES / SM4，agent 看到 CPA 输出（hc 高、gap_pct 高、avg_correlation 看起来不错）后，准备给 user 写最终成功消息，或考虑 terminate session。

**核心原则**：CPA 内部置信度高（hc ≥ block-byte threshold, gap_pct ≥ 20%, avg_correlation 适合）是**必要但不充分**条件。唯一的 ground-truth 成功信号是 encrypt_decrypt_verify 返回 verification=PASSED + MATCH 在 details。在该 tool call 完成且返回 MATCH 之前，candidate key 只是假设——可能正确、可能差 1 个 S-box subkey、可能差 master-key 反推。把 CPA 工具的 candidate 当成最终密钥跳过 verification 阶段，正是 verification 设计的目的（catch 这种情形）。

**为什么这样做**：DES、SM4、AES 在 CPA 输出与 master-key 验证之间有不同的反推路径——DES 需要 PC-2 反置换 + parity（见 9.12）；SM4 需要 4 轮 round-key 恢复 + key schedule 反推；AES 一般直接验证但 HD 模式可能有 dual-mode 歧义（k vs k⊕0xFF）。每种情况下 CPA 工具的**第一个** candidate 即使内部指标完美也常是错的，只有 encrypt_decrypt_verify 能 disambiguate。在 trace-budget-limited case（100 traces, 接触式智能卡）某 1-2 个 S-box subkey 的 hc 看起来高但实际偏 1——这种情况只有 verify MISMATCH 后才能触发 key_search 近邻枚举。

**正确做法**：
1. 任何 CPA invocation 返回 candidate key 后，**下一个 tool call 必须是 encrypt_decrypt_verify**。两者之间**不写**任何"成功恢复"自然语言结论。**注意 key_hex 参数必须传 hex string（"1002324454422688"），不能传 int 类型——传 int 会让 verify 工具报 ValueError**。
2. encrypt_decrypt_verify 结果是成功/失败决策的依据：verification=PASSED + MATCH → 才能宣告成功；verification=FAILED + MISMATCH → 继续诊断循环，**不 terminate session**。
3. verify MISMATCH 时，诊断 ladder：(a) DES → 走 9.12 的 master-key 反推；(b) AES HD target → 试 k⊕0xFF dual mode；(c) SM4 → 确认 4 轮 round-key 都恢复，再每轮独立 verify；(d) 任何 cipher → 调 key_search default 50000 预算（如未试过）；(e) 上述标准路径都 fail 才 pivot leakage / preprocessing / 重收 traces。
4. 自然语言成功消息**必须显式引用 verify 结果**：例如 "encrypt_decrypt_verify PASSED with MATCH on all 16 ciphertext bytes; recovered master key = ..."，而不是"我成功恢复了主密钥 = ..."。
5. round 预算快用完且仍无 MATCH，正确 termination 输出："CPA 产出 candidate K = ... 含 hc = .../... 和 gap_pct = ...%，但 encrypt_decrypt_verify 返回 MISMATCH，已尝试 key_search 和标准反推路径仍未中"，**不是**"已恢复主密钥 = ..."。

**经验阈值**：
- ground-truth 成功信号：verify return field verification == 'PASSED' AND 'MATCH' substring in details
- 单独不充分的内部置信度信号：AES hc=16/16 不充分（HD dual-mode 歧义）；DES hc=8/8 不充分（K1 仅 48-bit 需反推）；SM4 hc per round 高不充分（需 4 轮 + key-schedule 反推）；gap_pct ≥ 20% 必要不充分
- 每 session 强制 verify call 数：至少 1（不调 verify 不能宣告 session success）

**反模式**：
- 写 final summary 如"成功恢复主密钥 0x..."、"密钥 X 已成功恢复"或"Key recovered: ..."在 encrypt_decrypt_verify 返回 MATCH 之前。
- 把 CPA 工具的 master_key 字段当 final answer，未调 encrypt_decrypt_verify。
- 基于 hc=full 或 gap_pct ≥ 阈值就宣告成功，无显式 verification 调用。
- 把 candidate key 用粗体 / 高亮在 final output——可能是 K1 padded、arbitrary parity 猜测或近邻。
- 跳过 encrypt_decrypt_verify 因为"CPA 看起来对"——verify call 成本低、强制、唯一 ground-truth。
- encrypt_decrypt_verify 返回 MISMATCH 后立即 pivot 到不同 leakage target / leakage model / 重收 traces，不试标准 recovery 路径（DES master-key 反推、AES HD dual mode、multi-CPA candidate 合并）。
- key_hex 参数传 int（1002324454422688）而非 hex string ("1002324454422688")。

**适用场景**：任何 CPA 返回 candidate key、准备写成功结论之前；典型失败是 DES-14443 把 K1 padding 当主密钥写进最终输出。

