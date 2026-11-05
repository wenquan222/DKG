# DKG Agent Execution Log

## 1. Configuration

| Parameter | Value |
|---|---|
| Model | `deepseek-ai/DeepSeek-V3.2` |
| API | https://api.siliconflow.cn/v1 |
| Temperature | 0.1 |
| Max Tokens | 163840 |
| Start Time | 20260508_173111_758 |
| Duration | 315.3s |
| Neo4j | bolt://localhost:7687 |
| Session Dir | `..\logs\exp_rag\SM4-7816_DeepSeek-V3.2_NoKG_20260508_173111_758` |
| Total LLM Calls | 15 |
| First Round | prompt: 8,869, completion: 624 |
| Last Round | prompt: 17,725, completion: 657 |
| Total Tokens | 209,190 (prompt: 203,506, completion: 5,684) |

## 3. User Query

```
帮我对一个接触式智能卡实现的SM4密码算法波形进行CPA恢复密钥，SM4需要分4轮分别做CPA恢复轮密钥，然后从4个轮密钥反推主密钥。明文文件为'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy'，密文文件为'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy',原始波形文件为'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy'
```

## 4. Initial Knowledge Retrieval

**Step A: Keyword Extraction**

<details><summary>Prompt sent to LLM (click to expand)</summary>

```
You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"帮我对一个接触式智能卡实现的SM4密码算法波形进行CPA恢复密钥，SM4需要分4轮分别做CPA恢复轮密钥，然后从4个轮密钥反推主密钥。明文文件为'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy'，密文文件为'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy',原始波形文件为'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy'"

## Output rules (strict)

Return ONLY a JSON array of keyword strings. **At most 10 keywords.** No commentary.

Extraction principle — pick keywords that **uniquely identify the concrete attack scenario**, not generic SCA vocabulary:
1. The specific algorithm mentioned (e.g., `AES` / `DES` / `SM4`)
2. The specific device / platform mentioned (e.g., `STM32F103` / `FPGA` / `Contact Smartcard`)
3. The specific trace type if stated (e.g., `Power` / `EM`)
4. At most 2-3 method keywords drawn from user's wording (e.g., if user explicitly says "correlation power analysis", add `CPA`; if user says "masked implementation", add `Masking`)
5. Only add 1-2 task-diagnostic keywords if the request describes a specific failure mode (e.g., "my alignment acceptance is low" → `alignment acceptance`)

## What NOT to include

- Do NOT repeat synonyms (pick one: "HW" OR "Hamming Weight", not both)
- Do NOT add generic catch-all keywords like "CPA failure", "troubleshooting checklist", "failure diagnosis", "parameter preset" unless the user explicitly asks for them — the KG retriever will pull relevant diagnostic/strategy nodes via cross-layer links from the concrete entities above
- Do NOT add pipeline-meta terms like "unified analysis", "8-step process", "methodology", "multi-strategy" — these match too many Pipeline nodes
- Do NOT list every entity type's example exhaustively

## Good examples

User: "CPA on STM32F103 software AES, power traces"
→ `["AES", "STM32F103", "MCU", "Power", "CPA", "Hamming Weight", "S-box Output"]`   (7 keywords)

User: "FPGA AES hardware attack, contactless EM"
→ `["AES", "FPGA", "EM", "Contactless", "CPA", "Hamming Distance"]`   (6 keywords)

User: "DES analysis on smartcard, my alignment keeps dropping traces"
→ `["DES", "Smartcard", "Static Alignment", "alignment acceptance"]`   (4 keywords)

```
</details>

LLM Response: ["SM4", "Contact Smartcard", "CPA", "Power", "Round Key Recovery", "Master Key Derivation"]

Parsed Keywords: `["SM4", "Contact Smartcard", "CPA", "Power", "Round Key Recovery", "Master Key Derivation"]`

**Step B: KG Search**

Config: `{"mode": "rag", "top_k": 5}`

KG returned 5079 chars of raw knowledge (embedded in System Prompt below)

## 5. System Prompt

<details><summary>Full System Prompt (7062 chars, click to expand)</summary>

```
You are an expert in side-channel analysis (SCA), specialized in power analysis attacks such as CPA and DPA.

**[Retrieved Documents (RAG)]**
The following text chunks were retrieved from a 166-document SCA corpus by dense vector
similarity to your task description. They are unstructured excerpts and may be partially
off-topic. Use them as context, not as authoritative instructions:
- Verify each suggestion against your own SCA expertise.
- Adapt parameters based on actual waveform characteristics you observe.
- Make independent decisions when retrieved text conflicts with your analysis.

Top-5 retrieved chunks (cosine similarity over 166-doc SCA corpus):

--- Chunk 1 (doc='expert_experience', chunk=42, score=0.685) ---
**阶段 11 实测实例**：
- **AES-14443 第一次失败**：agent 选 start=1350（波形后段大尖峰）对齐 → CPA 14/16 降到 9/16，byte 0-5 全错。第二次直接 CPA 不对齐 → 14/16 对 → key_search 补 byte 1/4/11 → MATCH
- **AES-STM32F429 EM 波形**：波形 1000 点已经聚焦，直接 CPA 16/16 全对，无需 key_search
- **AES-7816 / AES-STM32F103 / AES-FPGA 等传统 case**：阶段 11 未系统验证"直接 CPA"是否同样更优；因此对这类案例只能说"若 Step 4 落入红色带，就按统一流程进入 Step 5 做对齐"，不能把它们写成 direct CPA 一定失败或一定成功的硬结论
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
## 九、Canonical 策略与反模式集合（KG canonical Strategy 节点的来源）

--- Chunk 2 (doc='MAN-06-2024-MathMagic-Detector-1.7.2-Manual', chunk=216, score=0.666) ---
<!-- image -->
图 729 选中纵向对齐模板
<!-- image -->
图 730 纵向对齐参数设置界面
- 1.1.1.1.1.1.1. **一阶CPA分析**
选择“密码”，继续选择“一阶CPA分析”，参数设置界面如图 731所示。一阶CPA分析，是在已知泄露位置的情况下猜测密钥，若对明文使用猜测的密钥进行加密的结果与真实密文相同，则猜测出真实密钥，否则继续进行密钥猜测，若猜测时间过长，则判断为猜测失败。使用该单片机使用USB通信，对AES算法进行一阶CPA分析结果如图 732所示，猜测出真实密钥0x112233445566778899AABBCCDDEEFF00。
<!-- image -->
图 731 一阶CPA参数设置界面
<!-- image -->
图 732 一阶CPA分析结果
#### 5.3.3 STM32 F103 I2C通信AES测评示例
该STM32F103单片机实现了对16字节明文进行AES加密，并返回16字节的密文结果。初始密钥为0x000102030405060708090A0B0C0D0E0F，用户可在I2C协议中对密钥进行修改。
- 1.1.1.1.1.1.1. **设备连接**
按照如图 733所示连接好USB2XXX、STM32F103和多功能侧信道分析仪，管脚连接可参考5.3.1节。
<!-- image -->
图 733 STM32 F103 I2C通信实物连接图
USB2XXX总线适配器连接多功能分析仪输入端：
3V连接第一个管脚；GND连接第二个管脚；SCL连接第三个管脚；SDA连接第四个管脚。（从上往下）USB2XXX总线适配器的引脚定义和实物图分别如图 734、图 735所示，注意缺口方向。
STM32F103连接多功能分析仪的输出端：
3V连接第一个管脚；GND连接第二个管脚；SCL连接第三个管脚；SDA连接第四个管脚。
<!-- image -->
图 734 USB2XXX总线适配器引脚定义示意图
<!-- image -->
图 735 USB2XXX总线适配器引脚实物图
- 1.1.1.1.1.1.1. **采波**

--- Chunk 3 (doc='MAN-06-2024-MathMagic-Detector-1.7.2-Manual', chunk=24, score=0.660) ---
- 支持Lecroy HDO6054A、PicoScope 3403D以及RIGOL DS7000示波器采波；
- 支持智能卡、串口、I2C 、SPI、Socket、FDTI和Daemon通信采波；
- 提供滤波、滑动窗口平均、波形对齐、重采样压缩、文件合并、波形格式转化等波形处理功能；
- 支持对AES、DES、RSA、ECC算法，以及国密SM2、SM3、SM4算法进行侧信道分析；
- 支持简单能量分析、已知密钥的中间值泄露分析、已知密钥的CPA排名分析、一阶CPA分析、模板分析等多种分析方法；
- 提供ISO/IEC 17825、GM/T 0083标准中规定的计时分析、TVLA等侧信道测试方法，并支持将测试结果导出，生成报告文档；
- 支持3G/4G/5G SIM卡MILENAGE算法分析；
- 多功能扩展，允许用户编写二次开发脚本，轻松实现非标准功能。
## 2 软件安装
1. 安装读卡器驱动
解压缩“[读卡器驱动]ACR1281U-C1 PCSC非安装驱动-4260.zip”压缩包，在安装前先将采波设备插入电脑，电脑会提示类似“发现的新硬件向导”的窗口，可根据窗口中的提示对驱动程序进行安装。
1. 示波器驱动安装
用户可根据所使用不同型号的示波器选择相应驱动进行安装。
1. Lecroy示波器
运行“[力科示波器驱动]activedso.exe”，执行安装。
1. Pico示波器
运行“[Pico示波器驱动]PicoScope6\_6.14.44.5870.exe”，执行安装。
1. RIGOL示波器
解压缩“[RIGOL]Ultra Sigma(PC)Installer\_00.01.06.01.zip”压缩包，运行文件夹下的“setup.exe”，执行安装。
1. 安装MathMagic Detector侧信道分析测评软件
双击运行MathMagic Detector Setup-1.7.2.exe程序，如图 1所示，点击“下一步”。
<!-- image -->
图 1 软件安装过程1
同意许可协议，点击“下一步”。输入用户信息，继续点击“下一步”。由于使用过程中可能产生大量波形数据，会占用较大硬盘空间，我们建议安装的默认路径为D:\MathMagic\Detector，用户可根据需要自行修改，如图 2所示。

--- Chunk 4 (doc='MAN-06-2024-MathMagic-Detector-1.7.2-Manual', chunk=179, score=0.659) ---
<!-- image -->
图 520 填充结果
#### 4.9.8 波形运算
- 0.1.1.0.1.1.1. **背景**
使用此功能可以对两个波形进行加减乘除等简单运算。
- 0.1.1.0.1.1.1. **目的**
对两组波形进行简单的加减乘除运算。
- 0.1.1.0.1.1.1. **输入**
在执行操作前，可以在软件主界面上选择参与运算的波形，波形运算的参数设置界面如图 521所示，波形一即为在主界面上选中的波形。
<!-- image -->
图 521 波形运算参数设置
- **选择波形：** 点击“预览”，可以选择另一条参与运算的波形。
- **运算方法：** 运算类型。支持加减乘除四种运算。
点击“确认”执行“波形一 加/减/乘/除 波形二”的波形运算后，生成处理后的波形，耗时会通过日志进行显示。
- 0.1.1.0.1.1.1. **示例**
以SM2加密算法波形为例，加密操作起始位置的大尖峰会影响波形特征的观察或后续操作，使用本功能可以将前端尖峰降低至与后面波形段相统一，以便后续波形处理。首先，对原始波形执行低通滤波，低通滤波详细步骤见本说明书4.6.1节。然后，使用原始波形减去滤波后的波形，得到最终处理好的波形。参与运算的波形如图 522所示，上方为原始波形，下方为滤波后波形。
<!-- image -->
图 522 运算波形
准备好参与运算的波形后，在原始波形界面上执行“波形运算”操作。“波形一”为当前选中波形，“运算方法”下拉菜单选择“减”，点击“预览”在安装路径下的“TempTraces”文件夹中选择滤波后的波形。参数设置如图 523所示。
<!-- image -->
图 523 波形运算参数设置
点击“确认”，执行减法，得到结果波形如图 524，可见波形中加密起始位置的高尖峰已消失。
<!-- image -->
图 524 波形运算结果
#### 4.9.9 时频转换
1. **背景**
某些情况下时间维度的波形信息泄露不太明显，转到频率维度可能有更明显特征。时频转换可以通过快速傅里叶变换的方式实现时间维度到频域维度的转换。
1. **目的**
通过快速傅里叶变换实现时域到频域的转换。
1. **输入**
时频转换的参数设置界面如图 525所示。

--- Chunk 5 (doc='MAN-06-2024-MathMagic-Detector-1.7.2-Manual', chunk=227, score=0.655) ---
<!-- image -->
图 789 选中触发拉低部分波形
<!-- image -->
图 790 计时分析参数配置界面
<!-- image -->
a. 密钥随机明文固定测试结果
<!-- image -->
b. 密钥固定明文随机测试结果
图 791 计时分析结果
- 0.1.1.0.1.1.1. **能量信号采波**
能量信号的采波步骤和触发通道采波的过程类似，其参数配置界面如图 792所示，此处可以选择软件中参数配置文件F429\_usb\_SM3\_Pico.ini。使用该设置设备采集到的2000条示例波如图 793所示。
<!-- image -->
a “采集设置”参数配置1
<!-- image -->
b “采集设置”参数配置2
<!-- image -->
c “目标设备”参数配置
图 792 采波参数配置界面
<!-- image -->
图 793 SM3示例波形（2000条）
- 0.1.1.0.1.1.1. **低通滤波**
低通滤波的目的是去除波形中高频率噪声的影响。选择“滤波”，继续选择“低通滤波”。参数设置如图 794所示，滤波得到的波形如图 795所示。
<!-- image -->
图 794 低通滤波参数设置
<!-- image -->
图 795 SM3示例波形低通滤波（2000条）
- 0.1.1.0.1.1.1. **纵向对齐**
纵向对齐的目的是让波形在纵向方向对齐。在原始波形中选中一部分作为模板（如图 796所示），然后选择“对齐”，继续选择“纵向对齐”，该功能的参数设置界面如图 797所示。其中，“参考波形”中的“起始点”、“点长度”、“参考波形号”对应波形中选择的模板。该功能用模板所在的波之外的每一条波与选中的模板在对应位置上求平均偏移量，随后将其所有采样点都减去偏移量，以达到纵向对齐的目的。
<!-- image -->
图 796 选中纵向对齐模板
<!-- image -->
图 797 纵向对齐参数设置界面
- 0.1.1.0.1.1.1. **TVLA分析**


**[Session Directory]**
All files for this session are stored in: ..\logs\exp_rag\SM4-7816_DeepSeek-V3.2_NoKG_20260508_173111_758
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'..\logs\exp_rag\SM4-7816_DeepSeek-V3.2_NoKG_20260508_173111_758/'` or `'../logs/...'` — just use the bare filename.
- When using file paths in Python code, always use forward slashes (/) or raw strings (r'...').
- Never invent, guess, or modify input file paths. If unsure, use python_jupyter with os.listdir() to check.

**[How to Work]**
- Use your own SCA expertise to plan and execute.
- Execute step by step based on YOUR judgment of the waveform characteristics.
- Use rag_search ONLY when:
  (1) You encounter an unexpected result and need additional context
  (2) You are unsure about a specific parameter and want to look up references
- Do NOT search before every step — trust your own analysis first.
- After each tool call, evaluate the result yourself before deciding next action.

```
</details>

## 6. Execution


---

### Round 1 | tokens: 8,869→624

**🤖 LLM:** 我来帮您对接触式智能卡实现的SM4算法波形进行CPA恢复密钥。首先，我需要加载数据并观察波形特征，然后按照SM4的4轮CPA攻击流程进行密钥恢复。

让我先查看一下数据的基本情况：

**🔧 → `python_jupyter`**

<details><summary>Code (1325 chars)</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
wave_path = 'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy'
plaintext_path = 'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy'
ciphertext_path = 'data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy'

# 加载数据
waves = np.load(wave_path)
plaintexts = np.load(plaintext_path)
ciphertexts = np.load(ciphertext_path)

print(f"波形数据形状: {waves.shape}")
print(f"明文数据形状: {plaintexts.shape}")
print(f"密文数据形状: {ciphertexts.shape}")
print(f"数据类型: waves={waves.dtype}, plaintexts={plaintexts.dtype}, ciphertexts={ciphertexts.dtype}")

# 查看前几条波形
plt.figure(figsize=(15, 8))
for i in range(5):
    plt.plot(waves[i], alpha=0.7, label=f'Trace {i}')
plt.title('前5条波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('raw_waves.png')
plt.show()

# 查看波形统计信息
print(f"\n波形统计信息:")
print(f"最小值: {waves.min():.4f}")
print(f"最大值: {waves.max():.4f}")
print(f"均值: {waves.mean():.4f}")
print(f"标准差: {waves.std():.4f}")

# 查看明文和密文示例
print(f"\n第一条明文 (hex): {plaintexts[0].tobytes().hex()}")
print(f"第一条密文 (hex): {ciphertexts[0].tobytes().hex()}")
```
</details>

**📋 ← `python_jupyter`:** `波形数据形状: (100, 6500)
明文数据形状: (100, 16)
密文数据形状: (100, 16)
数据类型: waves=float32, plaintexts=uint8, ciphertexts=uint8

波形统计信息:
最小值: -200.7874
最大值: 275.5905
均值: -1.7929
标准差: 64.6314

第一条明文 (hex): 15f172190435a0103048f7161a5f01fd
第一条密文 (hex): 169b73531b72211de486ef3fc2830686
C:\Users\Andersen\AppData\Local\Temp\ipykernel_14288\3343314533.py:29: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 2 | tokens: 9,696→458

**🤖 LLM:** 现在让我查看波形的整体特征，特别是寻找SM4算法的加密区间：

**🔧 → `python_jupyter`**

<details><summary>Code (1025 chars)</summary>

```python
# 计算平均波形
mean_wave = waves.mean(axis=0)
std_wave = waves.std(axis=0)

plt.figure(figsize=(15, 10))

# 平均波形
plt.subplot(2, 1, 1)
plt.plot(mean_wave, 'b-', linewidth=1.5, label='平均波形')
plt.fill_between(range(len(mean_wave)), mean_wave - std_wave, mean_wave + std_wave, alpha=0.3, label='±标准差')
plt.title('平均波形 (±标准差)')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)

# 寻找明显的峰值区域
plt.subplot(2, 1, 2)
abs_mean = np.abs(mean_wave)
plt.plot(abs_mean, 'r-', linewidth=1, label='平均波形绝对值')
plt.title('平均波形绝对值 (用于识别峰值区域)')
plt.xlabel('采样点')
plt.ylabel('绝对值')
plt.grid(True, alpha=0.3)

# 标记前几个峰值
peaks = []
for i in range(1, len(abs_mean)-1):
    if abs_mean[i] > abs_mean[i-1] and abs_mean[i] > abs_mean[i+1] and abs_mean[i] > 50:  # 阈值设为50
        peaks.append(i)
        
# 显示前20个峰值
print(f"找到 {len(peaks)} 个峰值 (阈值>50)")
print("前20个峰值位置:")
for i, peak in enumerate(peaks[:20]):
    print(f"  峰值 {i}: 位置={peak}, 值={abs_mean[peak]:.2f}")

plt.tight_layout()
plt.savefig('mean_wave_analysis.png')
plt.show()
```
</details>

<details><summary><b>📋 ← `python_jupyter`</b> (682 chars)</summary>

```
找到 137 个峰值 (阈值>50)
前20个峰值位置:
  峰值 0: 位置=624, 值=52.01
  峰值 1: 位置=650, 值=51.73
  峰值 2: 位置=680, 值=51.34
  峰值 3: 位置=712, 值=53.23
  峰值 4: 位置=721, 值=57.40
  峰值 5: 位置=731, 值=57.80
  峰值 6: 位置=739, 值=57.13
  峰值 7: 位置=750, 值=56.34
  峰值 8: 位置=767, 值=64.49
  峰值 9: 位置=779, 值=67.36
  峰值 10: 位置=792, 值=61.73
  峰值 11: 位置=808, 值=55.04
  峰值 12: 位置=821, 值=55.35
  峰值 13: 位置=983, 值=54.33
  峰值 14: 位置=1359, 值=56.50
  峰值 15: 位置=1404, 值=50.35
  峰值 16: 位置=1417, 值=57.13
  峰值 17: 位置=1423, 值=56.30
  峰值 18: 位置=1478, 值=55.39
  峰值 19: 位置=1496, 值=58.43
C:\Users\Andersen\AppData\Local\Temp\ipykernel_14288\1188182078.py:40: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
```
</details>


---

### Round 3 | tokens: 10,584→375

**🤖 LLM:** 现在让我查看波形中是否存在明显的基线漂移（纵向对齐问题）：

**🔧 → `python_jupyter`**

<details><summary>Code (866 chars)</summary>

```python
# 检查基线漂移
plt.figure(figsize=(15, 8))

# 查看前20条波形的基线
baseline_region_start = 0
baseline_region_end = 100  # 前100个采样点作为基线区域
baseline_values = waves[:, baseline_region_start:baseline_region_end].mean(axis=1)

plt.subplot(2, 1, 1)
plt.plot(baseline_values, 'bo-', markersize=4)
plt.title('各条波形的基线平均值 (前100个采样点)')
plt.xlabel('波形索引')
plt.ylabel('基线平均值')
plt.grid(True, alpha=0.3)

plt.subplot(2, 1, 2)
plt.hist(baseline_values, bins=20, edgecolor='black')
plt.title('基线平均值分布')
plt.xlabel('基线平均值')
plt.ylabel('频数')
plt.grid(True, alpha=0.3)

print(f"基线平均值统计:")
print(f"  最小值: {baseline_values.min():.4f}")
print(f"  最大值: {baseline_values.max():.4f}")
print(f"  均值: {baseline_values.mean():.4f}")
print(f"  标准差: {baseline_values.std():.4f}")
print(f"  范围: {baseline_values.max() - baseline_values.min():.4f}")

plt.tight_layout()
plt.savefig('baseline_drift.png')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `基线平均值统计:
  最小值: -8.7008
  最大值: 19.2126
  均值: 4.6232
  标准差: 5.7649
  范围: 27.9134
C:\Users\Andersen\AppData\Local\Temp\ipykernel_14288\3634897075.py:32: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 4 | tokens: 11,075→324

**🤖 LLM:** 我看到存在明显的基线漂移（范围约28个单位）。对于接触式智能卡，通常需要先进行纵向对齐（基线校正）。让我先进行纵向对齐：

**🔧 → `vertical_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy",
  "ref_start": 0,
  "ref_end": 100,
  "plaintext_npy": "data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "ciphertext_npy": "data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy"
}
```
</details>

<details><summary><b>📋 ← `vertical_aligner`</b> (655 chars)</summary>

```
{"out_wave_npy": "valigned_20260508_173243_884300.npy", "plot_path": "valign_compare_20260508_173243_884300.png", "n_traces": 100, "n_points": 6500, "ref_region": [0, 100], "baseline_std": 5.7649, "baseline_std_after": 2e-06, "out_plaintext_npy": "data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy", "out_ciphertext_npy": "data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy"}
```
</details>


![valign_compare_20260508_173243_884300.png](./valign_compare_20260508_173243_884300.png)


---

### Round 5 | tokens: 11,744→447

**🤖 LLM:** 纵向对齐完成，基线标准差从5.76降到了接近0。现在让我查看对齐后的波形：

**🔧 → `python_jupyter`**

<details><summary>Code (981 chars)</summary>

```python
# 加载纵向对齐后的波形
valigned_waves = np.load('valigned_20260508_173243_884300.npy')

# 计算对齐后的平均波形
mean_valigned = valigned_waves.mean(axis=0)

plt.figure(figsize=(15, 10))

# 对比对齐前后的平均波形
plt.subplot(2, 1, 1)
plt.plot(mean_wave, 'b-', alpha=0.7, label='原始平均波形')
plt.plot(mean_valigned, 'r-', alpha=0.7, label='纵向对齐后平均波形')
plt.title('纵向对齐前后平均波形对比')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)

# 查看对齐后的前几条波形
plt.subplot(2, 1, 2)
for i in range(5):
    plt.plot(valigned_waves[i], alpha=0.7, label=f'Trace {i}')
plt.title('纵向对齐后的前5条波形')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('valigned_comparison.png')
plt.show()

# 检查对齐后的基线
baseline_valigned = valigned_waves[:, 0:100].mean(axis=1)
print(f"\n纵向对齐后基线统计:")
print(f"  最小值: {baseline_valigned.min():.4f}")
print(f"  最大值: {baseline_valigned.max():.4f}")
print(f"  均值: {baseline_valigned.mean():.4f}")
print(f"  标准差: {baseline_valigned.std():.4f}")
```
</details>

**📋 ← `python_jupyter`:** `纵向对齐后基线统计:
  最小值: -0.0000
  最大值: 0.0000
  均值: -0.0000
  标准差: 0.0000
C:\Users\Andersen\AppData\Local\Temp\ipykernel_14288\2690586023.py:31: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 6 | tokens: 12,300→256

**🤖 LLM:** 纵向对齐效果很好。现在我需要观察波形特征，确定SM4算法的加密区间。SM4算法有32轮，但CPA攻击通常针对前几轮。让我先尝试直接对第一轮进行CPA攻击，看看效果：

**🔧 → `sm4_cpa_attack`** `{
  "plaintext_npy": "data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "wave_npy": "valigned_20260508_173243_884300.npy",
  "round_index": 0,
  "candidates": 30,
  "leakage_model": "HW",
  "target": "S-box_out"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (1255 chars)</summary>

```
{"round_index": 0, "recovered_round_key": "57DE7733", "cpa_avg_correlation": 0.4597, "cpa_min_correlation": 0.4347, "target": "S-box_out", "n_traces": 100, "detail_file": "sm4_cpa_round0_detail_20260508_173341_954231.json", "per_byte": [{"byte": 0, "key": "0x57", "correlation": 0.45919646282979204, "time_index": 481}, {"byte": 1, "key": "0xDE", "correlation": 0.4346554218980436, "time_index": 3570}, {"byte": 2, "key": "0x77", "correlation": 0.47438389433377304, "time_index": 6084}, {"byte": 3, "key": "0x33", "correlation": 0.4704069190391532, "time_index": 1016}], "high_confidence_count": 0, "recovery_assessment": "Only 0/4 bytes are high-confidence in this round. Treat this as a red band case: relocalize the round window, revisit alignment, or switch target family.", "low_confidence_subkeys": [{"subkey_index": 0, "byte": 0, "best_key_hex": "0x57", "top1_top2_gap": 0.005961397750718433}, {"subkey_index": 1, "byte": 1, "best_key_hex": "0xDE", "top1_top2_gap": 0.0020038695311090484}, {"subkey_index": 2, "byte": 2, "best_key_hex": "0x77", "top1_top2_gap": 0.06670903075150578}, {"subkey_index": 3, "byte": 3, "best_key_hex": "0x33", "top1_top2_gap": 0.037772501796737315}], "recommended_next_step": "relocalize_round_window_or_switch_target"}
```
</details>


---

### Round 7 | tokens: 13,064→486

**🤖 LLM:** 第一轮CPA的结果显示没有高置信度的字节（0/4），这属于红色带情况。根据我的经验，对于接触式智能卡，可能需要考虑静态对齐。让我先检查波形是否存在时间抖动：

**🔧 → `python_jupyter`**

<details><summary>Code (1071 chars)</summary>

```python
# 检查波形的时间对齐情况
# 通过查看特定特征点的位置变化来判断时间抖动

# 选择一个明显的峰值作为参考点
ref_peak = 750  # 从之前的分析中看到的明显峰值位置
search_window = 50  # 搜索窗口

# 计算每条波形在参考点附近的峰值位置
peak_positions = []
for i in range(min(20, len(valigned_waves))):  # 只检查前20条
    trace = valigned_waves[i]
    # 在参考点附近搜索局部最大值
    start = max(0, ref_peak - search_window)
    end = min(len(trace), ref_peak + search_window)
    local_region = trace[start:end]
    local_peak = np.argmax(np.abs(local_region)) + start
    peak_positions.append(local_peak)

plt.figure(figsize=(12, 6))
plt.plot(peak_positions, 'bo-', markersize=6)
plt.axhline(y=ref_peak, color='r', linestyle='--', alpha=0.7, label=f'参考位置 {ref_peak}')
plt.title('前20条波形中特征峰值位置变化')
plt.xlabel('波形索引')
plt.ylabel('峰值位置（采样点）')
plt.legend()
plt.grid(True, alpha=0.3)

print(f"峰值位置统计:")
print(f"  最小值: {min(peak_positions)}")
print(f"  最大值: {max(peak_positions)}")
print(f"  均值: {np.mean(peak_positions):.1f}")
print(f"  标准差: {np.std(peak_positions):.1f}")
print(f"  范围: {max(peak_positions) - min(peak_positions)}")

plt.savefig('peak_position_variation.png')
plt.show()
```
</details>

**📋 ← `python_jupyter`:** `峰值位置统计:
  最小值: 700
  最大值: 794
  均值: 763.5
  标准差: 28.5
  范围: 94
C:\Users\Andersen\AppData\Local\Temp\ipykernel_14288\4191035385.py:36: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 8 | tokens: 13,655→597

**🤖 LLM:** 确实存在明显的时间抖动（范围94个采样点）。我需要进行静态对齐。首先，我需要选择一个合适的对齐参考区域。让我查看波形中SM4算法的加密区间：

**🔧 → `python_jupyter`**

<details><summary>Code (1317 chars)</summary>

```python
# 更仔细地查看波形，寻找SM4算法的特征模式
# SM4算法通常会有明显的周期性特征

plt.figure(figsize=(15, 8))

# 查看平均波形的绝对值，寻找周期性
abs_mean_valigned = np.abs(mean_valigned)

# 使用滑动窗口计算能量
window_size = 50
energy = np.convolve(abs_mean_valigned**2, np.ones(window_size)/window_size, mode='same')

plt.subplot(2, 1, 1)
plt.plot(abs_mean_valigned, 'b-', alpha=0.7, label='平均波形绝对值')
plt.plot(energy/np.max(energy)*np.max(abs_mean_valigned), 'r-', alpha=0.7, label='能量（归一化）')
plt.title('平均波形绝对值与能量分布')
plt.xlabel('采样点')
plt.ylabel('幅值')
plt.legend()
plt.grid(True, alpha=0.3)

# 标记可能的加密区间
# 从之前的峰值分析看，600-900点区域有明显活动
plt.axvspan(600, 900, alpha=0.2, color='green', label='候选加密区间1')
plt.axvspan(1300, 1600, alpha=0.2, color='orange', label='候选加密区间2')

# 查看相关性最高的时间点（从第一轮CPA结果）
cpa_time_points = [481, 3570, 6084, 1016]
plt.subplot(2, 1, 2)
plt.plot(abs_mean_valigned, 'b-', alpha=0.7)
for i, tp in enumerate(cpa_time_points):
    plt.axvline(x=tp, color='r', alpha=0.5, linestyle='--')
    plt.text(tp, abs_mean_valigned[tp]*1.1, f'Byte{i}', fontsize=8, ha='center')
plt.title('CPA相关性最高时间点分布')
plt.xlabel('采样点')
plt.ylabel('绝对值')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('sm4_encryption_intervals.png')
plt.show()

print("CPA相关性最高时间点:")
for i, tp in enumerate(cpa_time_points):
    print(f"  Byte {i}: 时间点={tp}, 绝对值={abs_mean_valigned[tp]:.2f}")
```
</details>

**📋 ← `python_jupyter`:** `CPA相关性最高时间点:
  Byte 0: 时间点=481, 绝对值=9.27
  Byte 1: 时间点=3570, 绝对值=32.70
  Byte 2: 时间点=6084, 绝对值=39.15
  Byte 3: 时间点=1016, 绝对值=38.88
C:\Users\Andersen\AppData\Local\Temp\ipykernel_14288\897228729.py:41: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()`


---

### Round 9 | tokens: 14,399→347

**🤖 LLM:** 从CPA结果看，相关性最高的时间点分布很分散（481, 1016, 3570, 6084），这可能是由于时间抖动导致的。我需要选择一个在加密区间内的特征点进行静态对齐。从波形看，600-900点区域有明显活动，我选择这个区域中的一个明显峰值作为对齐参考：

**🔧 → `static_aligner`**

<details><summary>Arguments</summary>

```json
{
  "wave_npy": "valigned_20260508_173243_884300.npy",
  "start": 750,
  "length": 120,
  "max_shift": 100,
  "threshold": 85,
  "plaintext_npy": "data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy",
  "ciphertext_npy": "data/traces/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy"
}
```
</details>

**📋 ← `static_aligner`:** `{"out_aligned_npy": "aligned_20260508_173454_210120.npy", "plot_path": "align_overlay_20260508_173454_210120.png", "ref_trace_used": 50, "accepted": 82, "discarded": 18, "total": 100, "out_plaintext_npy": "plaintext_aligned_20260508_173454_210120.npy", "plaintext_traces": 82, "out_ciphertext_npy": "ciphertext_aligned_20260508_173454_210120.npy", "ciphertext_traces": 82, "alignment_avg_correlation": 0.9861, "alignment_min_correlation": 0.8556, "acceptance_rate": 0.82}`


![align_overlay_20260508_173454_210120.png](./align_overlay_20260508_173454_210120.png)


---

### Round 10 | tokens: 14,944→193

**🤖 LLM:** 静态对齐完成了，接受了82条波形（丢弃18条）。现在让我对对齐后的波形进行第一轮SM4 CPA攻击：

**🔧 → `sm4_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260508_173454_210120.npy",
  "wave_npy": "aligned_20260508_173454_210120.npy",
  "round_index": 0,
  "candidates": 30,
  "leakage_model": "HW",
  "target": "S-box_out"
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (841 chars)</summary>

```
{"round_index": 0, "recovered_round_key": "F12186F9", "cpa_avg_correlation": 0.7202, "cpa_min_correlation": 0.6866, "target": "S-box_out", "n_traces": 82, "detail_file": "sm4_cpa_round0_detail_20260508_173507_876682.json", "per_byte": [{"byte": 0, "key": "0xF1", "correlation": 0.6907690738200358, "time_index": 1243}, {"byte": 1, "key": "0x21", "correlation": 0.7562083135392708, "time_index": 1389}, {"byte": 2, "key": "0x86", "correlation": 0.7470595865649612, "time_index": 1333}, {"byte": 3, "key": "0xF9", "correlation": 0.6866335611296923, "time_index": 1105}], "high_confidence_count": 4, "recovery_assessment": "4/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 11 | tokens: 15,466→222

**🤖 LLM:** 很好！第一轮CPA现在有4/4高置信度字节，平均相关性0.72，这是一个很好的结果。现在让我继续攻击第二轮：

**🔧 → `sm4_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260508_173454_210120.npy",
  "wave_npy": "aligned_20260508_173454_210120.npy",
  "round_index": 1,
  "candidates": 30,
  "leakage_model": "HW",
  "target": "S-box_out",
  "prev_round_keys": [
    "F12186F9"
  ]
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (841 chars)</summary>

```
{"round_index": 1, "recovered_round_key": "41662B61", "cpa_avg_correlation": 0.7254, "cpa_min_correlation": 0.6957, "target": "S-box_out", "n_traces": 82, "detail_file": "sm4_cpa_round1_detail_20260508_173521_652128.json", "per_byte": [{"byte": 0, "key": "0x41", "correlation": 0.7663533962959393, "time_index": 2731}, {"byte": 1, "key": "0x66", "correlation": 0.6966250911167906, "time_index": 2877}, {"byte": 2, "key": "0x2B", "correlation": 0.7429052229528758, "time_index": 2821}, {"byte": 3, "key": "0x61", "correlation": 0.6956615964550055, "time_index": 3136}], "high_confidence_count": 4, "recovery_assessment": "4/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 12 | tokens: 16,017→219

**🤖 LLM:** 第二轮也很好，4/4高置信度字节，平均相关性0.725。现在继续第三轮：

**🔧 → `sm4_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260508_173454_210120.npy",
  "wave_npy": "aligned_20260508_173454_210120.npy",
  "round_index": 2,
  "candidates": 30,
  "leakage_model": "HW",
  "target": "S-box_out",
  "prev_round_keys": [
    "F12186F9",
    "41662B61"
  ]
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (932 chars)</summary>

```
{"round_index": 2, "recovered_round_key": "5A6AB19A", "cpa_avg_correlation": 0.6563, "cpa_min_correlation": 0.6028, "target": "S-box_out", "n_traces": 82, "detail_file": "sm4_cpa_round2_detail_20260508_173534_766466.json", "per_byte": [{"byte": 0, "key": "0x5A", "correlation": 0.690056784942478, "time_index": 4217}, {"byte": 1, "key": "0x6A", "correlation": 0.6163828715961225, "time_index": 4169}, {"byte": 2, "key": "0xB1", "correlation": 0.7160448149868963, "time_index": 4126}, {"byte": 3, "key": "0x9A", "correlation": 0.6028390632922057, "time_index": 4535}], "high_confidence_count": 3, "recovery_assessment": "3/4 bytes high-confidence in this round. Proceed to the next round or verify the master key if round 3 is finished.", "low_confidence_subkeys": [{"subkey_index": 3, "byte": 3, "best_key_hex": "0x9A", "top1_top2_gap": 0.05483350587117631}], "recommended_next_step": "continue_round_recovery_or_verify_master_key"}
```
</details>


---

### Round 13 | tokens: 16,613→236

**🤖 LLM:** 第三轮有3/4高置信度字节，byte 3的置信度稍低（gap=0.055）。现在继续第四轮：

**🔧 → `sm4_cpa_attack`** `{
  "plaintext_npy": "plaintext_aligned_20260508_173454_210120.npy",
  "wave_npy": "aligned_20260508_173454_210120.npy",
  "round_index": 3,
  "candidates": 30,
  "leakage_model": "HW",
  "target": "S-box_out",
  "prev_round_keys": [
    "F12186F9",
    "41662B61",
    "5A6AB19A"
  ]
}`

<details><summary><b>📋 ← `sm4_cpa_attack`</b> (1379 chars)</summary>

```
{"round_index": 3, "recovered_round_key": "7BA92077", "cpa_avg_correlation": 0.6039, "cpa_min_correlation": 0.5311, "target": "S-box_out", "n_traces": 82, "detail_file": "sm4_cpa_round3_detail_20260508_173549_052443.json", "per_byte": [{"byte": 0, "key": "0x7B", "correlation": 0.640579062427588, "time_index": 5706}, {"byte": 1, "key": "0xA9", "correlation": 0.5365656396880306, "time_index": 5670}, {"byte": 2, "key": "0x20", "correlation": 0.7074964099078697, "time_index": 5615}, {"byte": 3, "key": "0x77", "correlation": 0.5310983735080952, "time_index": 5764}], "high_confidence_count": 2, "recovery_assessment": "2/4 bytes high-confidence in this round. This is the SM4 gray band: refine the round window or merge complementary CPA attempts before moving on.", "low_confidence_subkeys": [{"subkey_index": 1, "byte": 1, "best_key_hex": "0xA9", "top1_top2_gap": 0.11777334026095176}, {"subkey_index": 3, "byte": 3, "best_key_hex": "0x77", "top1_top2_gap": 0.05400312045954031}], "recommended_next_step": "alignment_or_multi_strategy_merge_before_next_round", "recovered_master_key": "0123456789ABCDEFFEDCBA9876543210", "master_key_math_consistent": true, "master_key_verification_note": "IMPORTANT: math_consistent=true only means rk0-rk3 are internally consistent with this master_key. It does NOT mean the key is correct. You MUST call encrypt_decrypt_verify to confirm."}
```
</details>


---

### Round 14 | tokens: 17,355→243

**🤖 LLM:** 第四轮有2/4高置信度字节，属于灰色带。工具已经计算出了主密钥：`0123456789ABCDEFFEDCBA9876543210`。现在我需要验证这个密钥是否正确：

**🔧 → `encrypt_decrypt_verify`** `{
  "key_hex": "0123456789ABCDEFFEDCBA9876543210",
  "algorithm": "SM4",
  "mode": "ECB",
  "operation": "encrypt",
  "plaintext_npy": "plaintext_aligned_20260508_173454_210120.npy",
  "ciphertext_npy": "ciphertext_aligned_20260508_173454_210120.npy",
  "trace_index": 0
}`

**📋 ← `encrypt_decrypt_verify`:** `{"result_hex": "169B73531B72211DE486EF3FC2830686", "verification": "MATCH", "verification_requested": true, "verification_performed": true, "details": "SM4-128-ECB encrypt: 15f172190435a0103048f7161a5f01fd... → 169B73531B72211DE486EF3FC2830686...\n✅ Key verification PASSED — all 16 bytes match."}`


---

### Round 15 | tokens: 17,725→657

<details><summary><b>🤖 LLM Reasoning</b> (1161 chars)</summary>

太好了！密钥验证通过！这意味着我们成功恢复了SM4的主密钥。让我总结一下整个恢复过程：

## SM4密钥恢复总结

### 1. 数据基本情况
- 波形数据：100条轨迹，每条6500个采样点
- 明文/密文：16字节SM4加密数据
- 设备：接触式智能卡（7816接口）

### 2. 预处理步骤
1. **纵向对齐（基线校正）**：使用前100个采样点作为基线参考区域，消除了约28个单位的基线漂移
2. **静态对齐（时间对齐）**：使用750-870采样点区域作为参考，对齐后保留82条轨迹（丢弃18条），平均相关性0.986

### 3. SM4四轮CPA攻击结果

#### 第0轮（RK₀）
- 恢复的轮密钥：`F12186F9`
- 平均相关性：0.720
- 高置信度字节：4/4

#### 第1轮（RK₁）
- 恢复的轮密钥：`41662B61`
- 平均相关性：0.725
- 高置信度字节：4/4

#### 第2轮（RK₂）
- 恢复的轮密钥：`5A6AB19A`
- 平均相关性：0.656
- 高置信度字节：3/4（byte 3置信度稍低）

#### 第3轮（RK₃）
- 恢复的轮密钥：`7BA92077`
- 平均相关性：0.604
- 高置信度字节：2/4（bytes 1和3置信度较低）

### 4. 主密钥恢复
从四个轮密钥推导出的主密钥：`0123456789ABCDEFFEDCBA9876543210`

### 5. 密钥验证
使用恢复的主密钥对第一条明文进行加密，得到的密文与数据集中的密文完全匹配，验证通过！

### 6. 关键成功因素
1. **适当的预处理**：纵向对齐消除了基线漂移，静态对齐解决了时间抖动问题
2. **合适的泄漏模型**：使用Hamming Weight模型和S-box输出作为目标
3. **足够的轨迹数量**：82条对齐后的轨迹提供了足够的统计信息
4. **接触式智能卡特性**：相对稳定的功耗特征使得CPA攻击有效

### 7. 保存的文件
- 纵向对齐后的波形：`valigned_20260508_173243_884300.npy`
- 静态对齐后的波形：`aligned_20260508_173454_210120.npy`
- 对齐后的明文：`plaintext_aligned_20260508_173454_210120.npy`
- 对齐后的密文：`ciphertext_aligned_20260508_173454_210120.npy`
- 四轮CPA的详细结果文件
- 各种分析图表

**成功恢复的SM4-128主密钥：`0123456789ABCDEFFEDCBA9876543210`**

</details>


---

## 7. Token Summary

| Round | Prompt | Completion | Total |
|---:|---:|---:|---:|
| 1 | 8,869 | 624 | 9,493 |
| 2 | 9,696 | 458 | 10,154 |
| 3 | 10,584 | 375 | 10,959 |
| 4 | 11,075 | 324 | 11,399 |
| 5 | 11,744 | 447 | 12,191 |
| 6 | 12,300 | 256 | 12,556 |
| 7 | 13,064 | 486 | 13,550 |
| 8 | 13,655 | 597 | 14,252 |
| 9 | 14,399 | 347 | 14,746 |
| 10 | 14,944 | 193 | 15,137 |
| 11 | 15,466 | 222 | 15,688 |
| 12 | 16,017 | 219 | 16,236 |
| 13 | 16,613 | 236 | 16,849 |
| 14 | 17,355 | 243 | 17,598 |
| 15 | 17,725 | 657 | 18,382 |
| **Total** | **203,506** | **5,684** | **209,190** |

## 8. Final Output

太好了！密钥验证通过！这意味着我们成功恢复了SM4的主密钥。让我总结一下整个恢复过程：

## SM4密钥恢复总结

### 1. 数据基本情况
- 波形数据：100条轨迹，每条6500个采样点
- 明文/密文：16字节SM4加密数据
- 设备：接触式智能卡（7816接口）

### 2. 预处理步骤
1. **纵向对齐（基线校正）**：使用前100个采样点作为基线参考区域，消除了约28个单位的基线漂移
2. **静态对齐（时间对齐）**：使用750-870采样点区域作为参考，对齐后保留82条轨迹（丢弃18条），平均相关性0.986

### 3. SM4四轮CPA攻击结果

#### 第0轮（RK₀）
- 恢复的轮密钥：`F12186F9`
- 平均相关性：0.720
- 高置信度字节：4/4

#### 第1轮（RK₁）
- 恢复的轮密钥：`41662B61`
- 平均相关性：0.725
- 高置信度字节：4/4

#### 第2轮（RK₂）
- 恢复的轮密钥：`5A6AB19A`
- 平均相关性：0.656
- 高置信度字节：3/4（byte 3置信度稍低）

#### 第3轮（RK₃）
- 恢复的轮密钥：`7BA92077`
- 平均相关性：0.604
- 高置信度字节：2/4（bytes 1和3置信度较低）

### 4. 主密钥恢复
从四个轮密钥推导出的主密钥：`0123456789ABCDEFFEDCBA9876543210`

### 5. 密钥验证
使用恢复的主密钥对第一条明文进行加密，得到的密文与数据集中的密文完全匹配，验证通过！

### 6. 关键成功因素
1. **适当的预处理**：纵向对齐消除了基线漂移，静态对齐解决了时间抖动问题
2. **合适的泄漏模型**：使用Hamming Weight模型和S-box输出作为目标
3. **足够的轨迹数量**：82条对齐后的轨迹提供了足够的统计信息
4. **接触式智能卡特性**：相对稳定的功耗特征使得CPA攻击有效

### 7. 保存的文件
- 纵向对齐后的波形：`valigned_20260508_173243_884300.npy`
- 静态对齐后的波形：`aligned_20260508_173454_210120.npy`
- 对齐后的明文：`plaintext_aligned_20260508_173454_210120.npy`
- 对齐后的密文：`ciphertext_aligned_20260508_173454_210120.npy`
- 四轮CPA的详细结果文件
- 各种分析图表

**成功恢复的SM4-128主密钥：`0123456789ABCDEFFEDCBA9876543210`**
