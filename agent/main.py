"""
DKG Agent - 侧信道分析智能体

架构原则：
- 所有LLM逻辑在main函数里，工具只做纯数据检索
- KG工具：输入关键词 → 搜索Neo4j → 返回原始知识条目JSON
- 初始规划：main函数里调LLM提取关键词 → 搜KG → 注入system prompt
- HTTP拦截器记录框架发给LLM的每一次完整原始请求
"""

import sys
import os
import json
import re
import time
import socket
import subprocess
import atexit
import textwrap
from datetime import datetime
from typing import List, Optional, Type
import requests

from pydantic import BaseModel, Field, PrivateAttr
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from langchain_core.callbacks import BaseCallbackHandler
from openai import APIStatusError, APITimeoutError, InternalServerError, RateLimitError
import yaml
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.kg_query import DKGSearcher


def load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def start_kernel_if_needed(script_path=None, port=5055):
    if script_path is None:
        script_path = os.path.join(os.path.dirname(__file__), "tools", "python_jupyter_kernel_tool.py")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:
            print(f"  Jupyter Kernel already running on port {port}")
            return None
    print(f"  Starting Jupyter Kernel on port {port}...")
    proc = subprocess.Popen(
        [sys.executable, script_path, "--port", str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    atexit.register(proc.terminate)
    time.sleep(4)
    print(f"  Jupyter Kernel started (PID: {proc.pid}, Port: {port})")
    return proc


def ensure_kernel_alive(port=5055):
    """检测 Jupyter kernel 是否存活，死了就重启。在每个案例开始前调用。"""
    try:
        resp = requests.post(f"http://localhost:{port}/execute",
                             json={"code": "1+1"}, timeout=10)
        if resp.status_code == 200:
            return  # 存活
    except:
        pass
    # kernel 挂了，重启
    print(f"  WARNING: Jupyter Kernel on port {port} not responding, restarting...")
    # 只杀对应端口的进程（避免误杀并行的其他 kernel）
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'cmdline']):
            cmdline = proc.info.get('cmdline') or []
            cmdline_str = ' '.join(str(c) for c in cmdline)
            if 'python_jupyter_kernel_tool.py' in cmdline_str and f'--port {port}' in cmdline_str:
                proc.kill()
                print(f"  Killed old kernel PID: {proc.pid}")
    except ImportError:
        pass
    time.sleep(1)
    start_kernel_if_needed(port=port)
    time.sleep(2)


def configure_kernel_context(port: int, tools_dir: str, run_dir: Optional[str] = None):
    """为持久化 Jupyter kernel 注入 tools path，并在需要时切换 cwd。"""
    snippets = [
        (
            "import sys\n"
            f"_DKG_TOOLS_DIR = {json.dumps(tools_dir)}\n"
            "if _DKG_TOOLS_DIR not in sys.path:\n"
            "    sys.path.insert(0, _DKG_TOOLS_DIR)\n"
        )
    ]
    if run_dir is not None:
        snippets.append(
            "import os\n"
            f"os.chdir({json.dumps(run_dir)})\n"
        )
    try:
        requests.post(
            f"http://localhost:{port}/execute",
            json={"code": "\n".join(snippets)},
            timeout=10,
        )
    except Exception:
        pass


LLM_RETRY_MAX_RETRIES = 5
LLM_RETRY_INITIAL_DELAY = 2.0
LLM_RETRY_MAX_DELAY = 30.0
LLM_RETRY_BACKOFF_FACTOR = 2.0


def should_retry_llm_exception(exc: Exception) -> bool:
    """Retry transient provider overload / timeout errors, but not arbitrary logic failures."""
    if isinstance(exc, (InternalServerError, RateLimitError, APITimeoutError)):
        return True
    if isinstance(exc, APIStatusError):
        status_code = getattr(exc, "status_code", None)
        return status_code == 429 or (status_code is not None and status_code >= 500)
    if isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
        return True

    msg = str(exc).lower()
    transient_markers = [
        "system is too busy",
        "try again later",
        "rate limit",
        "timed out",
        "timeout",
        "temporarily unavailable",
        "connection reset",
    ]
    return any(marker in msg for marker in transient_markers)


# ==================== FullContextLogger ====================

class FullContextLogger(BaseCallbackHandler):
    """token捕获 + 日志输出"""

    def __init__(self, run_dir):
        self.run_dir = run_dir
        self.token_usage_list = []   # 每轮token数据
        self._call_counter = 0

    def on_chat_model_start(self, serialized, messages, **kwargs):
        self._call_counter += 1

    def on_chat_model_end(self, response, **kwargs):
        tu = None
        if hasattr(response, 'llm_output') and response.llm_output:
            tu = response.llm_output.get("token_usage")
        self.token_usage_list.append({
            "call": self._call_counter,
            "token_usage": tu
        })

    def write_log(self, log_path, meta, init_log, system_prompt, tools, messages, token_records=None):
        """
        从stream收集的messages列表 + token_records构建完整日志。
        token_records: List[dict] — 从AIMessage.response_metadata提取的每轮token数据
        """
        tr = token_records or []

        with open(log_path, "w", encoding="utf-8") as f:
            # ====== 1. Configuration ======
            f.write("# DKG Agent Execution Log\n\n")
            f.write("## 1. Configuration\n\n")
            f.write("| Parameter | Value |\n|---|---|\n")
            f.write(f"| Model | `{meta.get('Model','')}` |\n")
            f.write(f"| API | {meta.get('API','')} |\n")
            f.write(f"| Temperature | 0.1 |\n")
            f.write(f"| Max Tokens | 163840 |\n")
            f.write(f"| Start Time | {meta.get('Start Time','')} |\n")
            f.write(f"| Duration | {meta.get('Duration','')} |\n")
            f.write(f"| Neo4j | {meta.get('Neo4j','')} |\n")
            f.write(f"| Session Dir | `{meta.get('Directory','')}` |\n")

            # token统计
            if tr:
                first = tr[0]
                last = tr[-1]
                tp = sum(t["prompt_tokens"] for t in tr)
                tc = sum(t["completion_tokens"] for t in tr)
                f.write(f"| Total LLM Calls | {len(tr)} |\n")
                f.write(f"| First Round | prompt: {first['prompt_tokens']:,}, completion: {first['completion_tokens']:,} |\n")
                f.write(f"| Last Round | prompt: {last['prompt_tokens']:,}, completion: {last['completion_tokens']:,} |\n")
                f.write(f"| Total Tokens | {tp + tc:,} (prompt: {tp:,}, completion: {tc:,}) |\n")
            f.write("\n")

            # ====== 3. User Query ======
            f.write(f"## 3. User Query\n\n```\n{meta.get('Query','')}\n```\n\n")

            # ====== 4. Knowledge Retrieval ======
            f.write("## 4. Initial Knowledge Retrieval\n\n")
            if init_log:
                f.write("**Step A: Keyword Extraction**\n\n")
                f.write(f"<details><summary>Prompt sent to LLM (click to expand)</summary>\n\n```\n{init_log.get('keyword_prompt','')}\n```\n</details>\n\n")
                raw_resp = init_log.get('llm_raw_response', '').replace('`', '').strip()
                f.write(f"LLM Response: {raw_resp}\n\n")
                f.write(f"Parsed Keywords: `{json.dumps(init_log.get('parsed_keywords',[]), ensure_ascii=False)}`\n\n")

                f.write("**Step B: KG Search**\n\n")
                f.write(f"Config: `{json.dumps(init_log.get('kg_config', {}))}`\n\n")
                kg_result = init_log.get('kg_raw_result', '')
                f.write(f"KG returned {len(kg_result)} chars of raw knowledge (embedded in System Prompt below)\n\n")

            # ====== 5. System Prompt ======
            f.write("## 5. System Prompt\n\n")
            f.write(f"<details><summary>Full System Prompt ({len(system_prompt)} chars, click to expand)</summary>\n\n```\n{system_prompt}\n```\n</details>\n\n")

            # ====== 6. Execution ======
            f.write("## 6. Execution\n\n")

            round_counter = 0
            token_idx = 0  # token_records里的索引

            for msg in messages:
                msg_type = type(msg).__name__
                content = str(msg.content) if hasattr(msg, 'content') else ""

                if msg_type == "HumanMessage":
                    pass

                elif msg_type == "AIMessage":
                    round_counter += 1

                    # Token信息
                    token_str = ""
                    if token_idx < len(tr):
                        t = tr[token_idx]
                        token_str = f" | tokens: {t['prompt_tokens']:,}→{t['completion_tokens']:,}"
                        token_idx += 1

                    f.write(f"\n---\n\n### Round {round_counter}{token_str}\n\n")

                    # LLM推理
                    if content:
                        if len(content) > 800:
                            f.write(f"<details><summary><b>🤖 LLM Reasoning</b> ({len(content)} chars)</summary>\n\n{content}\n\n</details>\n\n")
                        else:
                            f.write(f"**🤖 LLM:** {content}\n\n")

                    # 工具调用
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_name = tc.get('name', '?')
                            args = tc.get('args', {})
                            args_str = json.dumps(args, ensure_ascii=False, indent=2)

                            if 'code' in args and len(args.get('code', '')) > 200:
                                code = args['code']
                                other_args = {k: v for k, v in args.items() if k != 'code'}
                                f.write(f"**🔧 → `{tool_name}`**\n\n")
                                if other_args:
                                    f.write(f"```json\n{json.dumps(other_args, ensure_ascii=False, indent=2)}\n```\n\n")
                                f.write(f"<details><summary>Code ({len(code)} chars)</summary>\n\n```python\n{code}\n```\n</details>\n\n")
                            elif len(args_str) > 300:
                                f.write(f"**🔧 → `{tool_name}`**\n\n<details><summary>Arguments</summary>\n\n```json\n{args_str}\n```\n</details>\n\n")
                            else:
                                f.write(f"**🔧 → `{tool_name}`** `{args_str}`\n\n")

                elif msg_type == "ToolMessage":
                    tool_name = msg.name if hasattr(msg, 'name') else "?"
                    tool_content = content
                    is_error = "ERROR" in tool_content or "Error" in tool_content

                    if is_error:
                        lim = 5000
                        d = tool_content if len(tool_content) <= lim else tool_content[:lim] + "\n...(truncated)"
                        f.write(f"**❌ ← `{tool_name}` Error:**\n\n```\n{d}\n```\n\n")
                    else:
                        lim = 1500
                        d = tool_content if len(tool_content) <= lim else tool_content[:lim] + "\n...(truncated)"
                        if len(d) > 500:
                            f.write(f"<details><summary><b>📋 ← `{tool_name}`</b> ({len(tool_content)} chars)</summary>\n\n```\n{d}\n```\n</details>\n\n")
                        else:
                            f.write(f"**📋 ← `{tool_name}`:** `{d}`\n\n")

                    # 嵌入图片：工具输出中提到的 .png 文件都在 session 目录下
                    img_paths = re.findall(r'["\']([^"\']+\.(?:png|jpg|jpeg))["\']', tool_content)
                    seen_imgs = set()
                    for ip in img_paths:
                        bn = os.path.basename(ip)
                        if bn not in seen_imgs:
                            seen_imgs.add(bn)
                            f.write(f'\n![{bn}](./{bn})\n\n')

            # ====== 7. Token Summary ======
            if tr:
                f.write("\n---\n\n## 7. Token Summary\n\n")
                f.write("| Round | Prompt | Completion | Total |\n")
                f.write("|---:|---:|---:|---:|\n")
                for i, t in enumerate(tr):
                    f.write(f"| {i+1} | {t['prompt_tokens']:,} | {t['completion_tokens']:,} | {t['total_tokens']:,} |\n")
                tp = sum(t["prompt_tokens"] for t in tr)
                tc = sum(t["completion_tokens"] for t in tr)
                f.write(f"| **Total** | **{tp:,}** | **{tc:,}** | **{tp+tc:,}** |\n\n")

            # ====== 8. Final Output ======
            # 优先反查 LLM 自己写的纯文本结论（成功 case 通常有）
            final = ""
            for msg in reversed(messages):
                if type(msg).__name__ == "AIMessage" and hasattr(msg, 'content') and msg.content:
                    if not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                        final = str(msg.content)
                        break

            # 如果 LLM 没写结论（失败 case 常见），自动生成机器化 summary
            if not final.strip():
                tool_call_count = {}
                last_recovered_key = None
                last_cpa_corr = None
                last_verification = None
                last_correct_key = None
                last_off_track = None
                for msg in messages:
                    mt = type(msg).__name__
                    if mt == "AIMessage" and hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            n = tc.get('name', '?')
                            tool_call_count[n] = tool_call_count.get(n, 0) + 1
                    if mt == "ToolMessage":
                        c = str(getattr(msg, 'content', ''))
                        # 提取关键字段（最近一次出现的）
                        m = re.search(r'"recovered_key[a-z_]*":\s*"([0-9A-Fa-f]+)"', c)
                        if m: last_recovered_key = m.group(1)
                        m = re.search(r'"correct_key":\s*"([0-9A-Fa-f]+)"', c)
                        if m: last_correct_key = m.group(1)
                        m = re.search(r'"cpa_avg_correlation":\s*([0-9.]+)', c)
                        if m: last_cpa_corr = m.group(1)
                        m = re.search(r'"verification":\s*"(MATCH|MISMATCH|PARTIAL_MISMATCH|NOT_VERIFIED|N/A)"', c)
                        if m: last_verification = m.group(1)

                lines = ["_(LLM did not produce a textual conclusion. Auto-generated summary from tool history:)_", ""]
                lines.append(f"- Total rounds: {len([m for m in messages if type(m).__name__ == 'AIMessage'])}")
                lines.append(f"- Tool call counts: " + ", ".join(f"`{k}`={v}" for k, v in sorted(tool_call_count.items(), key=lambda x: -x[1])))
                if last_cpa_corr:    lines.append(f"- Last CPA avg correlation: **{last_cpa_corr}**")
                if last_recovered_key: lines.append(f"- Last recovered_key: `{last_recovered_key}`")
                if last_correct_key: lines.append(f"- key_search correct_key: `{last_correct_key}`")
                if last_verification: lines.append(f"- Last verification status: **{last_verification}**")
                # off-track 标记（D 护栏注入到 meta）
                if isinstance(meta, dict) and meta.get("guard_warnings"):
                    lines.append(f"- ⚠️  Guard warnings ({len(meta['guard_warnings'])}):")
                    for w in meta['guard_warnings']:
                        lines.append(f"    - {w}")
                final = "\n".join(lines)

            f.write(f"## 8. Final Output\n\n{final}\n")

# ==================== Schemas ====================
class JupyterInput(BaseModel):
    code: str = Field(..., description="Python code to execute in Jupyter kernel.")

# ==================== Schemas ====================

class WeightedMAInput(BaseModel):
    wave_npy: str = Field(..., description="Path to wave file (.npy).")
    weight: int = Field(default=3, description="Smoothing weight. Software usually starts at 2-3. Hardware/EM should first try NO filtering; stronger filtering is an experiment option, not a default. Formula: s_i=(w*s_{i-1}+x_i)/(1+w).")
    plaintext_npy: Optional[str] = Field(default=None, description="Path to plaintext file. Will be passed through unchanged (filtering does not discard traces).")
    ciphertext_npy: Optional[str] = Field(default=None, description="Path to ciphertext file. Will be passed through unchanged.")

class StaticAlignInput(BaseModel):
    wave_npy: str = Field(..., description="Path to wave file (.npy).")
    ref_trace: Optional[int] = Field(default=None, description="Reference trace index. Recommended: choose a trace near the middle of the dataset. null=auto-pick the middle trace. Avoid always using trace 0/1 as a hard rule.")
    start: int = Field(..., description="Start point of alignment reference region (sample index). MUST lie inside a candidate ENCRYPTION interval and be centered on a feature peak believed to belong to crypto leakage. Do NOT default to the global maximum peak or the first prominent IO spike.")
    length: int = Field(default=120, description="Length of alignment reference region. Current benchmark often starts with 100-120 samples to cover one complete feature peak, but this is a lab prior rather than a universal constant.")
    max_shift: int = Field(default=50, description="Maximum shift range for correlation matching. Must be data-driven: cover the actual peak jitter range, not an arbitrary small constant.")
    threshold: int = Field(default=85, description="Correlation threshold (1-100). Current benchmark often starts near 85, but this is only a lab prior; judge by discard rate and resulting CPA quality.")
    plaintext_npy: Optional[str] = Field(default=None, description="Path to plaintext file. Will be filtered to keep only accepted traces (same indices as aligned waves).")
    ciphertext_npy: Optional[str] = Field(default=None, description="Path to ciphertext file. Will be filtered to keep only accepted traces.")


class VerticalAlignInput(BaseModel):
    wave_npy: str = Field(..., description="Path to wave file (.npy).")
    ref_start: int = Field(..., description="Start point of baseline reference region (sample index). Should be in a FLAT, NON-ENCRYPTION area (e.g., before the first spike).")
    ref_end: int = Field(..., description="End point of baseline reference region (not included). The region [ref_start, ref_end) should cover a quiet/flat segment.")
    plaintext_npy: Optional[str] = Field(default=None, description="Path to plaintext file. Passed through unchanged (vertical alignment does not discard traces).")
    ciphertext_npy: Optional[str] = Field(default=None, description="Path to ciphertext file. Passed through unchanged.")


class CPAInput(BaseModel):
    plaintext_npy: str = Field(..., description="Path to plaintext file (.npy). Must come from user input or previous tool output.")
    wave_npy: str = Field(..., description="Path to wave file (.npy). Must come from user input or previous tool output.")
    candidates: int = Field(default=20, description="Number of top key candidates per byte (saved to detail JSON for key_search). Default 20. For low-SNR devices (STM32F429, contactless smartcards), increase to 30-50 so the correct byte enters the pool.")
    leakage_model: str = Field(default="HW", description="Leakage model: 'HW' (Hamming Weight) or 'ID' (byte identity value).")
    target: str = Field(default="S-box_out", description="Leakage position / intermediate value target. Options: 'S-box_out' (SBOX[pt^key], most common for software), 'S-box_in' (pt^key, linear), 'S-box_in_xor_out' (HD between S-box input and output), 'S-box_in_xor_prev_ct' (FPGA register transition: S-box_in XOR ciphertext[i-1], requires ciphertext_npy), 'S-box_out_xor_prev_ct' (S-box_out XOR ciphertext[i-1], requires ciphertext_npy).")
    bytes_to_test: Optional[List[int]] = Field(default=None, description="Key bytes to test (0-15). null=all 16.")
    ciphertext_npy: Optional[str] = Field(default=None, description="Path to ciphertext file (.npy). Required when target contains 'prev_ct' (FPGA HD model). The tool uses ciphertext[i-1] as the previous register state.")
    corr_mode: Optional[str] = Field(default=None, description="Correlation mode. None=auto (dual for target='S-box_in_xor_prev_ct'+HW, abs otherwise). 'abs' = |corr| ranking (software). 'dual' = returns TWO candidate sets (positive-correlation topK and negative-correlation topK) because hardware HD linear models have k<->k^0xFF symmetry; downstream verifier picks the correct polarity.")

class DESCPAInput(BaseModel):
    plaintext_npy: str = Field(..., description="Path to DES plaintext file (.npy), shape (n_traces, 8) uint8.")
    wave_npy: str = Field(..., description="Path to wave file (.npy).")
    candidates: int = Field(default=20, description="Number of top key candidates per S-box (saved to detail JSON for key_search). Default 20. For low-SNR devices increase to 30-50.")
    leakage_model: str = Field(default="HW", description="Leakage model: 'HW' or 'ID'.")
    target: str = Field(default="S-box_out", description="Leakage position target. Options: 'S-box_out' (S-box output 4-bit, software standard), 'S-box_in' (E(R0)^K 6-bit, linear with k/k^0x3F symmetry - auto enables dual), 'S-box_in_xor_out' (HD between S-box I/O, 6-bit with high 2 bits linear), 'R_xor_LOut' (HW of register transition = HW(R0^L0^F), hardware FPGA standard - corresponds to Detector DES target 1), 'LOut' (HW of round output L1_4bits = L0^F, hardware).")
    sboxes_to_test: Optional[List[int]] = Field(default=None, description="S-box indices to test (0-7). null=all 8.")
    corr_mode: Optional[str] = Field(default=None, description="Correlation mode. None=auto (dual for 'S-box_in'+HW). 'abs' | 'dual' (dual returns pos/neg top candidates for linear HD models; downstream verifier picks correct polarity).")

class SM4CPAInput(BaseModel):
    plaintext_npy: str = Field(..., description="Path to SM4 plaintext file (.npy), shape (n_traces, 16) uint8.")
    wave_npy: str = Field(..., description="Path to wave file (.npy).")
    round_index: int = Field(default=0, description="Which round to attack (0-3). SM4 requires 4 rounds to recover full 128-bit key.")
    candidates: int = Field(default=20, description="Number of top key candidates per byte (saved to detail JSON for key_search). Default 20.")
    leakage_model: str = Field(default="HW", description="Leakage model: 'HW' or 'ID'.")
    target: str = Field(default="S-box_out", description="Leakage position target. Options: 'S-box_out' (SBOX output, software standard), 'S-box_in' (xor_b ^ k, linear with k/k^0xFF symmetry - auto enables dual), 'S-box_in_xor_out' (HD between S-box I/O).")
    bytes_to_test: Optional[List[int]] = Field(default=None, description="Round key bytes to test (0-3). null=all 4.")
    prev_round_keys: Optional[List[str]] = Field(default=None, description="Previously recovered round keys (hex strings). round_index=1 needs [rk0], round_index=2 needs [rk0,rk1], etc.")
    wave_start: Optional[int] = Field(default=None, description="Start sample point for this round's waveform region. null=beginning. RECOMMENDED: leave null for the first attempt — the tool will scan the FULL waveform and automatically find the correct leakage time point via argmax. Only specify wave_start/wave_end if you have strong evidence of the exact round interval.")
    wave_end: Optional[int] = Field(default=None, description="End sample point for this round's waveform region. null=end. Same recommendation as wave_start: leave null unless you are certain of the interval.")
    corr_mode: Optional[str] = Field(default=None, description="Correlation mode. None=auto (dual for 'S-box_in'+HW). 'abs' | 'dual'.")

class CryptoInput(BaseModel):
    key_hex: str = Field(..., description="Key hex string (e.g. '2b7e151628aed2a6abf7158809cf4f3c')")
    algorithm: str = Field(default="AES", description="Algorithm: 'AES', 'DES', or 'SM4'")
    mode: str = Field(default="ECB", description="Mode: 'ECB' or 'CBC'")
    operation: str = Field(default="encrypt", description="'encrypt' or 'decrypt'")
    plaintext_hex: Optional[str] = Field(default=None, description="Plaintext hex (e.g. '00112233...'). EITHER provide this OR plaintext_npy. NEVER use NIST/RFC test vectors — they are NOT your dataset.")
    ciphertext_hex: Optional[str] = Field(default=None, description="Expected ciphertext hex for verification. EITHER provide this OR ciphertext_npy. Without ANY ciphertext source, tool returns NOT_VERIFIED.")
    plaintext_npy: Optional[str] = Field(default=None, description="Path to plaintext .npy file. Tool reads plaintext[trace_index] and converts to hex. STRONGLY RECOMMENDED for CPA verification — guarantees the value matches your actual dataset.")
    ciphertext_npy: Optional[str] = Field(default=None, description="Path to ciphertext .npy file. Tool reads ciphertext[trace_index] and converts to hex. STRONGLY RECOMMENDED for CPA verification.")
    trace_index: int = Field(default=0, description="Which trace to use when reading plaintext_npy/ciphertext_npy (default 0 = first trace).")

class KeySearchInput(BaseModel):
    algorithm: str = Field(..., description="Algorithm: 'AES', 'DES', or 'SM4'")
    recovered_key_hex: str = Field(..., description="CPA recovered key hex (search starting point)")
    cpa_detail_file: str = Field(..., description="Path to primary CPA detail JSON (contains topK candidates per byte/sbox)")
    plaintext_npy: str = Field(..., description="Path to plaintext .npy file")
    ciphertext_npy: str = Field(..., description="Path to ciphertext .npy file")
    gap_threshold: float = Field(default=0.15, description="Bytes with correlation gap below this are considered unreliable (default 0.15 = 15%)")
    max_candidates_per_byte: int = Field(default=20, description="Max candidates to try per unreliable byte (default 20, matches CPA candidates)")
    max_combinations: int = Field(default=50000, description="Max total search combinations (default 50000)")
    extra_cpa_detail_files: Optional[List[str]] = Field(default=None, description="Additional CPA detail JSON files to merge with the primary one. Candidates from ALL files are pooled per byte/sbox (union + dedup). Use this when multiple CPA runs with different parameters each recovered different bytes reliably.")

class CorrelationInput(BaseModel):
    wave_npy: str = Field(..., description="Path to wave traces file (.npy). Must come from user input or previous tool output.")
    data_npy: str = Field(..., description="Path to plaintext or ciphertext file (.npy). Must come from user input or previous tool output.")
    data_type: str = Field(default="plaintext", description="'plaintext' or 'ciphertext'")
    byte_index: int = Field(default=0, description="Which byte to analyze (0-15)")
    model: str = Field(default="HW", description="'HW' (Hamming Weight of raw byte) or 'SBOX_HW' (HW of S-box output, slower but more accurate)")

class KGSearchInput(BaseModel):
    keywords: List[str] = Field(..., description=(
        "List of SCA-related keywords to search in the knowledge graph. "
        "Examples: ['CPA', 'correlation', 'low'], ['alignment', 'threshold', 'discard'], "
        "['S-box', 'attack_point'], ['Hamming Weight', 'leakage model']. "
        "The tool does pure keyword matching — provide specific, relevant terms."))


# ==================== Mixin ====================
class _RunDirMixin:
    _run_dir: str = "."
    def set_run_dir(self, d): self._run_dir = d
    def _auto_path(self, stem, ext):
        # Jupyter cwd 已经设为 session directory，所以只返回文件名即可
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{stem}_{ts}.{ext.lstrip('.')}"
    def _tool_import_prelude(self):
        tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools").replace(os.sep, '/')
        return textwrap.dedent(f"""
import sys
_DKG_TOOLS_DIR = {json.dumps(tools_dir)}
if _DKG_TOOLS_DIR not in sys.path:
    sys.path.insert(0, _DKG_TOOLS_DIR)
""").strip()


# ==================== Tools ====================
class JupyterAPITool(_RunDirMixin, BaseTool):
    name: str = "python_jupyter"
    description: str = (
        "Execute arbitrary Python code in a persistent Jupyter kernel. "
        "Use for data exploration, visualization, custom analysis. "
        "Kernel maintains state across calls. Save plots with plt.savefig().")
    args_schema: Type[BaseModel] = JupyterInput
    image_save_path: str = "."

    @staticmethod
    def _preprocess_code(raw):
        s = raw.strip()
        s = re.sub(r"^\s*```(?:python|py)?\s*\n?","",s,flags=re.IGNORECASE)
        s = re.sub(r"\n?\s*```\s*$","",s,flags=re.IGNORECASE)
        return textwrap.dedent(s.replace("\r\n","\n").replace("\r","\n")).strip()

    def _run(self, code):
        code = self._preprocess_code(code)
        port = int(os.environ.get("JUPYTER_PORT", "5055"))
        try:
            resp = requests.post(f"http://localhost:{port}/execute", json={"code":code}, timeout=900)
            if resp.status_code!=200: return f"Jupyter API Error: {resp.status_code}"
            result = ""
            for item in resp.json().get("outputs",[]):
                t = item.get("type")
                if t in ("text","stream"): result += item.get("content","")
                elif t == "error": result += "\n---ERROR---\n" + item.get("content","")
            return result.strip() or "(executed, no output)"
        except Exception as e: return f"Jupyter Error: {e}"


class WeightedMovingAverageTool(_RunDirMixin, BaseTool):
    name: str = "weighted_moving_average"
    description: str = (
        "Apply weighted moving average smoothing to power traces. "
        "Formula: s_i = (weight * s_{i-1} + x_i) / (1 + weight). "
        "Software implementation: usually start with weight 2-3. "
        "Hardware/EM: first try no filtering; only use stronger filtering as an explicit experiment. "
        "Filtering does NOT discard traces, so plaintext/ciphertext indices remain matched. "
        "If plaintext_npy/ciphertext_npy are provided, their paths are passed through in the output for convenience.")
    args_schema: Type[BaseModel] = WeightedMAInput

    def _run(self, wave_npy, weight=3, plaintext_npy=None, ciphertext_npy=None):
        out_npy = self._auto_path("smoothed", "npy")
        plot_path = self._auto_path("smooth_compare", "png")
        code = f"""
{self._tool_import_prelude()}
import numpy as np, json as _json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from preprocessing_tool import lowpass_iir_weighted
waves = np.load({json.dumps(wave_npy)})
filt = lowpass_iir_weighted(waves, w={weight})
np.save({json.dumps(out_npy)}, filt.astype(waves.dtype, copy=False))
plt.figure(figsize=(10,3))
plt.plot(waves[0], lw=0.9, label="Original[0]")
plt.plot(filt[0], lw=1.2, label="Smoothed[0] (w={weight})")
plt.title("Weighted Moving Average (weight={weight})")
plt.xlabel("Sample"); plt.ylabel("Amplitude"); plt.legend(); plt.tight_layout()
plt.savefig({json.dumps(plot_path)}, dpi=160); plt.close()
result = {{
    "out_wave_npy": {json.dumps(out_npy)},
    "plot_path": {json.dumps(plot_path)},
    "n_traces": int(waves.shape[0]),
    "n_points": int(waves.shape[1]),
    "weight": {weight},
}}
if {json.dumps(plaintext_npy)} is not None:
    result["plaintext_npy"] = {json.dumps(plaintext_npy)}
if {json.dumps(ciphertext_npy)} is not None:
    result["ciphertext_npy"] = {json.dumps(ciphertext_npy)}
print(_json.dumps(result))
"""
        return JupyterAPITool().run(code)


class StaticAlignTool(_RunDirMixin, BaseTool):
    name: str = "static_aligner"
    description: str = (
        "Static alignment via cross-correlation. "
        "Use this only AFTER direct CPA shows alignment is needed, or when candidate encryption intervals remain ambiguous. "
        "Choose start INSIDE a candidate ENCRYPTION interval, not from the global maximum peak or protocol/IO spikes. "
        "If ref_trace is omitted, the tool auto-selects a middle trace. "
        "Set length to cover one complete crypto feature peak; current benchmark often starts with 100-120 samples. "
        "Returns ONLY accepted traces. "
        "If plaintext_npy/ciphertext_npy are provided, they are automatically filtered "
        "to match the accepted traces (same indices). Use the output paths for subsequent CPA.")
    args_schema: Type[BaseModel] = StaticAlignInput

    def _run(self, wave_npy, ref_trace=None, start=0, length=120, max_shift=50, threshold=85,
             plaintext_npy=None, ciphertext_npy=None):
        out_npy = self._auto_path("aligned", "npy")
        out_pt = self._auto_path("plaintext_aligned", "npy") if plaintext_npy else "None"
        out_ct = self._auto_path("ciphertext_aligned", "npy") if ciphertext_npy else "None"
        plot_path = self._auto_path("align_overlay", "png")
        jref = "None" if ref_trace is None else str(int(ref_trace))
        code = f"""
{self._tool_import_prelude()}
import numpy as np, json as _json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from preprocessing_tool import static_align

waves = np.load({json.dumps(wave_npy)})
ref_trace = len(waves) // 2 if {jref} is None else int({jref})
params = {{"ref_trace":ref_trace,"start":{start},"length":{length},"max_shift":{max_shift},"threshold":{threshold}}}
ret = static_align(waves, params)
aligned = ret['aligned']
accepted = ret['accepted']

# 保存对齐后的波形（只有通过的trace）
np.save({json.dumps(out_npy)}, aligned)

# 自动过滤明文和密文（保持索引匹配）
result = {{
    "out_aligned_npy": {json.dumps(out_npy)},
    "plot_path": {json.dumps(plot_path)},
    "ref_trace_used": int(ref_trace),
    "accepted": int(accepted.sum()),
    "discarded": int((~accepted).sum()),
    "total": int(len(waves)),
}}

pt_path = {json.dumps(plaintext_npy)}
if pt_path is not None:
    pt = np.load(pt_path)
    pt_filtered = pt[accepted]
    np.save({json.dumps(out_pt)}, pt_filtered)
    result["out_plaintext_npy"] = {json.dumps(out_pt)}
    result["plaintext_traces"] = int(pt_filtered.shape[0])

ct_path = {json.dumps(ciphertext_npy)}
if ct_path is not None:
    ct = np.load(ct_path)
    ct_filtered = ct[accepted]
    np.save({json.dumps(out_ct)}, ct_filtered)
    result["out_ciphertext_npy"] = {json.dumps(out_ct)}
    result["ciphertext_traces"] = int(ct_filtered.shape[0])

# 相关性统计
corr_accepted = ret['correlations'][accepted]
if len(corr_accepted) > 0:
    result["alignment_avg_correlation"] = round(float(corr_accepted.mean()), 4)
    result["alignment_min_correlation"] = round(float(corr_accepted.min()), 4)
result["acceptance_rate"] = round(float(accepted.sum()) / float(len(waves)), 4) if len(waves) > 0 else 0.0

# 画对齐后的前5条
plt.figure(figsize=(10,3))
for idx in range(min(5, len(aligned))):
    plt.plot(aligned[idx], lw=0.8, label=f"Trace {{idx}}")
plt.title(f"Aligned (accepted: {{len(aligned)}}/{{len(waves)}})")
plt.xlabel("Sample"); plt.ylabel("Amplitude"); plt.legend(); plt.tight_layout()
plt.savefig({json.dumps(plot_path)}, dpi=160); plt.close()

print(_json.dumps(result))
"""
        return JupyterAPITool().run(code)


class VerticalAlignTool(_RunDirMixin, BaseTool):
    name: str = "vertical_aligner"
    description: str = (
        "Vertical alignment (baseline correction) for hardware / EM traces with baseline drift. "
        "Removes DC offset differences between traces by subtracting each trace's mean "
        "in a specified reference region. The reference region MUST be a flat, "
        "non-encryption area (e.g., BEFORE the first spike, not in the encryption region). "
        "Does NOT discard any traces — output has the same number of traces as input. "
        "This decision is INDEPENDENT of static alignment: use it whenever baseline drift is visible, whether or not static alignment is needed.")
    args_schema: Type[BaseModel] = VerticalAlignInput

    def _run(self, wave_npy, ref_start, ref_end, plaintext_npy=None, ciphertext_npy=None):
        out_npy = self._auto_path("valigned", "npy")
        plot_path = self._auto_path("valign_compare", "png")
        code = f"""
{self._tool_import_prelude()}
import numpy as np, json as _json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from preprocessing_tool import vertical_align

waves = np.load({json.dumps(wave_npy)})
aligned = vertical_align(waves, ref_start={ref_start}, ref_end={ref_end})
np.save({json.dumps(out_npy)}, aligned)

# 对比图：对齐前后各5条
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
for i in range(min(5, len(waves))):
    ax1.plot(waves[i], lw=0.5)
    ax2.plot(aligned[i], lw=0.5)
ax1.axvspan({ref_start}, {ref_end}, alpha=0.2, color='green', label='ref region')
ax2.axvspan({ref_start}, {ref_end}, alpha=0.2, color='green', label='ref region')
ax1.set_title("Before vertical alignment"); ax1.legend()
ax2.set_title("After vertical alignment"); ax2.legend()
plt.xlabel("Sample"); plt.tight_layout()
plt.savefig({json.dumps(plot_path)}, dpi=160); plt.close()

result = {{
    "out_wave_npy": {json.dumps(out_npy)},
    "plot_path": {json.dumps(plot_path)},
    "n_traces": int(aligned.shape[0]),
    "n_points": int(aligned.shape[1]),
    "ref_region": [{ref_start}, {ref_end}],
    "baseline_std": round(float(waves[:, {ref_start}:{ref_end}].mean(axis=1).std()), 4),
    "baseline_std_after": round(float(aligned[:, {ref_start}:{ref_end}].mean(axis=1).std()), 6),
}}

pt_path = {json.dumps(plaintext_npy)}
if pt_path is not None:
    result["out_plaintext_npy"] = pt_path

ct_path = {json.dumps(ciphertext_npy)}
if ct_path is not None:
    result["out_ciphertext_npy"] = ct_path

print(_json.dumps(result))
"""
        return JupyterAPITool().run(code)


class CPATool(_RunDirMixin, BaseTool):
    name: str = "aes_cpa_attack"
    description: str = (
        "AES-128 CPA (Correlation Power Analysis) attack. "
        "Computes Pearson correlation between hypothetical power and actual traces for all 256 key candidates per byte. "
        "Returns best key, correlation, and time index for each byte. "
        "For hardware HD linear models (target='S-box_in_xor_prev_ct' + HW), the tool automatically returns "
        "TWO candidate keys per byte ('recovered_key_pos' and 'recovered_key_neg') due to k<->k^0xFF symmetry. "
        "Use encrypt_decrypt_verify on BOTH candidate keys to determine the correct polarity. "
        "Note: file paths must come from user input or previous tool output.")
    args_schema: Type[BaseModel] = CPAInput

    def _run(self, plaintext_npy, wave_npy, candidates=20, leakage_model="HW", target="S-box_out",
             bytes_to_test=None, ciphertext_npy=None, corr_mode=None):
        plot_path = self._auto_path("cpa_result","png")
        json_path = self._auto_path("cpa_detail","json")
        jb = json.dumps(bytes_to_test) if bytes_to_test else "None"
        jct = json.dumps(ciphertext_npy) if ciphertext_npy else "None"
        jcm = json.dumps(corr_mode) if corr_mode else "None"
        code = f"""
{self._tool_import_prelude()}
import json as _json, traceback, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from aes_cpa_tool import run_aes_cpa
try:
    result = run_aes_cpa(plaintext_npy={json.dumps(plaintext_npy)},wave_npy={json.dumps(wave_npy)},candidates={candidates},leakage_model={json.dumps(leakage_model)},target={json.dumps(target)},bytes_to_test={jb},ciphertext_npy={jct},corr_mode={jcm})
    is_dual = result.get("corr_mode") == "dual"
    fig,axes = plt.subplots(4,4,figsize=(16,12))
    for i,r in enumerate(result["results"]):
        ax = axes[i//4][i%4]
        ax.plot(r["best_curve"], lw=0.5, color='red')
        title = f"Byte {{r['byte']}}: "
        if is_dual:
            title += f"k+=0x{{r['best_key_pos']:02X}} k-=0x{{r['best_key_neg']:02X}}"
        else:
            title += f"key=0x{{r['best_key']:02X}} corr={{r['topK'][0]['score']:.3f}}"
        ax.set_title(title, fontsize=8)
    plt.suptitle("CPA Attack Results"); plt.tight_layout()
    plt.savefig({json.dumps(plot_path)}, dpi=160); plt.close()

    # 保存 detail JSON（key_search 要用）
    def _trim(r):
        out = {{"byte": r["byte"], "topK": r["topK"], "best_key": r["best_key"]}}
        if is_dual:
            out["corr_mode"] = "dual"
            out["topK_pos"] = r["topK_pos"]; out["topK_neg"] = r["topK_neg"]
            out["best_key_pos"] = r["best_key_pos"]; out["best_key_neg"] = r["best_key_neg"]
        return out
    with open({json.dumps(json_path)}, 'w') as f:
        _json.dump({{"n_traces":result["n_traces"],"n_points":result["n_points"],"leakage_model":result["leakage_model"],"target":result["target"],"corr_mode":result.get("corr_mode","abs"),"results":[_trim(r) for r in result["results"]]}}, f, indent=2)

    # 控制台返回：软件 CPA 一套密钥；硬件 HD 两套（pos 和 neg）
    if is_dual:
        key_pos_hex = "".join(f"{{r['best_key_pos']:02X}}" for r in result["results"])
        key_neg_hex = "".join(f"{{r['best_key_neg']:02X}}" for r in result["results"])
        summary = {{
            "corr_mode": "dual",
            "note": "Hardware HD model produces TWO candidate keys due to k<->k^0xFF symmetry. Verify BOTH with encrypt_decrypt_verify to find the correct one.",
            "recovered_key_pos": key_pos_hex,
            "recovered_key_neg": key_neg_hex,
            "n_traces": result["n_traces"], "target": result["target"],
            "plot_path": {json.dumps(plot_path)}, "detail_file": {json.dumps(json_path)},
            "per_byte": [{{"byte": r["byte"], "key_pos": f"0x{{r['best_key_pos']:02X}}", "key_neg": f"0x{{r['best_key_neg']:02X}}", "score_pos": round(r['topK_pos'][0]['score'], 4), "score_neg": round(r['topK_neg'][0]['score'], 4)}} for r in result["results"]],
        }}
    else:
        recovered_key = [r["best_key"] for r in result["results"]]
        key_hex = "".join(f"{{b:02X}}" for b in recovered_key)
        correlations = [r["topK"][0]["score"] for r in result["results"]]
        # build gap_pct map from subkey_analysis
        _sa_map = {{item["byte"]: item for item in result.get("subkey_analysis", [])}}
        def _gap_pct(b):
            g = _sa_map.get(b, {{}}).get("top1_top2_gap")
            return round(g * 100, 1) if g is not None else None
        summary = {{
            "recovered_key": key_hex,
            "cpa_avg_correlation": round(float(result.get("cpa_avg_correlation", sum(correlations)/len(correlations))), 4),
            "cpa_min_correlation": round(float(result.get("cpa_min_correlation", min(correlations))), 4),
            "n_traces": result["n_traces"], "target": result["target"],
            "plot_path": {json.dumps(plot_path)}, "detail_file": {json.dumps(json_path)},
            "per_byte": [{{"byte": r["byte"], "key": f"0x{{r['best_key']:02X}}", "correlation": round(r["topK"][0]["score"], 4), "time_index": r["topK"][0]["time_index"], "gap_pct": _gap_pct(r["byte"])}} for r in result["results"]],
            "high_confidence_count": result.get("high_confidence_count"),
            "recovery_assessment": result.get("recovery_assessment"),
            "low_confidence_subkeys": result.get("low_confidence_subkeys", []),
            "recommended_next_step": result.get("recommended_next_step"),
        }}
    import sys
    sys.stdout.flush()
    print(_json.dumps(summary, ensure_ascii=False), flush=True)
    sys.stdout.flush()
except Exception as e:
    import sys
    print(f"CPA Error: {{e}}", flush=True)
    print(traceback.format_exc(), flush=True)
    sys.stdout.flush()
"""
        return JupyterAPITool().run(code)

class DESCPATool(_RunDirMixin, BaseTool):
    name: str = "des_cpa_attack"
    description: str = (
        "DES CPA attack. Attacks first-round intermediate value (8 S-boxes, 6-bit key each). "
        "Recovers 48-bit subkey then derives 64-bit master key (parity bits zeroed). "
        "Targets: 'S-box_out' (software), 'R_xor_LOut' (hardware FPGA register transition - recommended for contactless smartcard DES), 'LOut', 'S-box_in_xor_out', 'S-box_in'. "
        "For 'S-box_in' + HW, auto enables dual mode (returns recovered_key_pos and recovered_key_neg). "
        "DES key parity bits = 0 is normal. "
        "Input: plaintext (n_traces, 8) uint8 + wave traces.")
    args_schema: Type[BaseModel] = DESCPAInput

    def _run(self, plaintext_npy, wave_npy, candidates=20, leakage_model="HW", target="S-box_out",
             sboxes_to_test=None, corr_mode=None):
        plot_path = self._auto_path("des_cpa_result", "png")
        json_path = self._auto_path("des_cpa_detail", "json")
        js = json.dumps(sboxes_to_test) if sboxes_to_test else "None"
        jcm = json.dumps(corr_mode) if corr_mode else "None"
        code = f"""
{self._tool_import_prelude()}
import json as _json, traceback, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from des_cpa_tool import run_des_cpa
try:
    result = run_des_cpa(plaintext_npy={json.dumps(plaintext_npy)},wave_npy={json.dumps(wave_npy)},candidates={candidates},leakage_model={json.dumps(leakage_model)},target={json.dumps(target)},sboxes_to_test={js},corr_mode={jcm})
    is_dual = result.get("corr_mode") == "dual"
    fig,axes = plt.subplots(2,4,figsize=(16,6))
    for i,r in enumerate(result["results"]):
        ax = axes[i//4][i%4]
        scores = r.get("all_scores", [])
        if scores:
            xs = list(range(len(scores)))
            ax.bar(xs, scores, color='steelblue', width=0.85)
            if r.get("topK"):
                top_key = int(r["topK"][0]["key"])
                if 0 <= top_key < len(scores):
                    ax.bar([top_key], [scores[top_key]], color='crimson', width=0.85)
            ax.set_xlim(-0.5, max(len(scores) - 0.5, 0.5))
            ax.set_xlabel("Key candidate", fontsize=7)
            ax.set_ylabel("|corr|", fontsize=7)
            ax.grid(alpha=0.25, axis='y')
        if is_dual:
            ax.set_title(f"S{{r['sbox']}}: k+=0x{{r['best_key_pos']:02X}} k-=0x{{r['best_key_neg']:02X}}", fontsize=8)
        else:
            ax.set_title(f"S-box {{r['sbox']}}: key=0x{{r['best_key']:02X}} corr={{r['topK'][0]['score']:.3f}}", fontsize=8)
    plt.suptitle(f"DES CPA - Key: {{result['recovered_key']}}"); plt.tight_layout()
    plt.savefig({json.dumps(plot_path)}, dpi=160); plt.close()
    with open({json.dumps(json_path)}, 'w') as f:
        _json.dump(result, f, indent=2, default=str)

    if is_dual:
        summary = {{
            "corr_mode": "dual",
            "note": "Linear HD model: TWO candidate keys. Verify BOTH with encrypt_decrypt_verify.",
            "recovered_key_pos": result["recovered_key_pos"],
            "recovered_key_neg": result["recovered_key_neg"],
            "cpa_avg_correlation": round(float(result.get("cpa_avg_correlation", result["avg_correlation"])), 4),
            "target": result["target"],
            "n_traces": result["n_traces"],
            "plot_path": {json.dumps(plot_path)}, "detail_file": {json.dumps(json_path)},
            "per_sbox": result["per_sbox"],
            "high_confidence_count": result.get("high_confidence_count"),
            "recovery_assessment": result.get("recovery_assessment"),
            "low_confidence_subkeys": result.get("low_confidence_subkeys", []),
            "recommended_next_step": result.get("recommended_next_step"),
        }}
    else:
        summary = {{
            "recovered_key": result["recovered_key"],
            "cpa_avg_correlation": round(float(result.get("cpa_avg_correlation", result["avg_correlation"])), 4),
            "cpa_min_correlation": round(float(result.get("cpa_min_correlation", result["min_correlation"])), 4),
            "n_traces": result["n_traces"], "target": result["target"],
            "plot_path": {json.dumps(plot_path)}, "detail_file": {json.dumps(json_path)},
            "per_sbox": result["per_sbox"],
            "high_confidence_count": result.get("high_confidence_count"),
            "recovery_assessment": result.get("recovery_assessment"),
            "low_confidence_subkeys": result.get("low_confidence_subkeys", []),
            "recommended_next_step": result.get("recommended_next_step"),
        }}
    import sys
    sys.stdout.flush()
    print(_json.dumps(summary, ensure_ascii=False), flush=True)
    sys.stdout.flush()
except Exception as e:
    import sys
    print(f"DES CPA Error: {{e}}", flush=True)
    print(traceback.format_exc(), flush=True)
    sys.stdout.flush()
"""
        return JupyterAPITool().run(code)


class SM4CPATool(_RunDirMixin, BaseTool):
    name: str = "sm4_cpa_attack"
    description: str = (
        "SM4 CPA attack (single round). SM4 requires 4 separate CPA attacks (round 0-3), "
        "each recovering 4 bytes (32 bits) of the round key. "
        "Call this tool 4 times with round_index=0,1,2,3. "
        "For round_index > 0, pass previously recovered round keys via prev_round_keys. "
        "Use wave_start/wave_end to specify each round's waveform region. "
        "After all 4 rounds, the tool automatically derives the 128-bit master key. "
        "Input: plaintext (n_traces, 16) uint8 + wave traces.")
    args_schema: Type[BaseModel] = SM4CPAInput

    def _run(self, plaintext_npy, wave_npy, round_index=0, candidates=20, leakage_model="HW",
             target="S-box_out", bytes_to_test=None, prev_round_keys=None,
             wave_start=None, wave_end=None, corr_mode=None):
        json_path = self._auto_path(f"sm4_cpa_round{round_index}_detail", "json")
        jb = json.dumps(bytes_to_test) if bytes_to_test else "None"
        jprk = json.dumps(prev_round_keys) if prev_round_keys else "None"
        jws = json.dumps(wave_start) if wave_start is not None else "None"
        jwe = json.dumps(wave_end) if wave_end is not None else "None"
        jcm = json.dumps(corr_mode) if corr_mode else "None"
        code = f"""
{self._tool_import_prelude()}
import json as _json, traceback
from sm4_cpa_tool import run_sm4_cpa
try:
    result = run_sm4_cpa(plaintext_npy={json.dumps(plaintext_npy)},wave_npy={json.dumps(wave_npy)},round_index={round_index},candidates={candidates},leakage_model={json.dumps(leakage_model)},target={json.dumps(target)},bytes_to_test={jb},prev_round_keys={jprk},wave_start={jws},wave_end={jwe},corr_mode={jcm})
    is_dual = result.get("corr_mode") == "dual"
    with open({json.dumps(json_path)}, 'w') as f:
        _json.dump(result, f, indent=2, default=str)

    if is_dual:
        out = {{
            "round_index": result["round_index"],
            "corr_mode": "dual",
            "note": "Linear HD model: TWO round key candidates. Try both for verification.",
            "recovered_round_key_pos": result["recovered_round_key_pos"],
            "recovered_round_key_neg": result["recovered_round_key_neg"],
            "cpa_avg_correlation": round(float(result.get("cpa_avg_correlation", result["avg_correlation"])), 4),
            "target": result["target"],
            "n_traces": result["n_traces"],
            "detail_file": {json.dumps(json_path)},
            "per_byte": result["per_byte"],
            "high_confidence_count": result.get("high_confidence_count"),
            "recovery_assessment": result.get("recovery_assessment"),
            "low_confidence_subkeys": result.get("low_confidence_subkeys", []),
            "recommended_next_step": result.get("recommended_next_step"),
        }}
    else:
        out = {{
            "round_index": result["round_index"],
            "recovered_round_key": result["recovered_round_key"],
            "cpa_avg_correlation": round(float(result.get("cpa_avg_correlation", result["avg_correlation"])), 4),
            "cpa_min_correlation": round(float(result.get("cpa_min_correlation", result["min_correlation"])), 4),
            "target": result["target"],
            "n_traces": result["n_traces"],
            "detail_file": {json.dumps(json_path)},
            "per_byte": result["per_byte"],
            "high_confidence_count": result.get("high_confidence_count"),
            "recovery_assessment": result.get("recovery_assessment"),
            "low_confidence_subkeys": result.get("low_confidence_subkeys", []),
            "recommended_next_step": result.get("recommended_next_step"),
        }}
    if "recovered_master_key" in result:
        out["recovered_master_key"] = result["recovered_master_key"]
        out["master_key_math_consistent"] = result.get("master_key_math_consistent", False)
        if "master_key_verification_note" in result:
            out["master_key_verification_note"] = result["master_key_verification_note"]
    print(_json.dumps(out, ensure_ascii=False))
except Exception as e:
    print(f"SM4 CPA Error: {{e}}")
    import traceback; print(traceback.format_exc())
"""
        return JupyterAPITool().run(code)


class KeySearchTool(_RunDirMixin, BaseTool):
    name: str = "key_search"
    description: str = (
        "Search for the correct key near a CPA-recovered key. "
        "Use this AFTER CPA attack when encrypt_decrypt_verify returns MISMATCH. "
        "Reads CPA detail JSON, identifies low-confidence subkeys from topK candidates, "
        "and searches combinations near the recovered key. Supports AES/DES/SM4 and merging "
        "candidates from multiple CPA runs via extra_cpa_detail_files. "
        "Merge only runs from the SAME underlying waveform dataset / same case; do not mix unrelated datasets.")
    args_schema: Type[BaseModel] = KeySearchInput

    def _run(self, algorithm, recovered_key_hex, cpa_detail_file, plaintext_npy, ciphertext_npy,
             gap_threshold=0.15, max_candidates_per_byte=4, max_combinations=50000,
             extra_cpa_detail_files=None):
        jextra = json.dumps(extra_cpa_detail_files) if extra_cpa_detail_files else "None"
        code = f"""
{self._tool_import_prelude()}
import json as _json
from key_search_tool import run_key_search
result = run_key_search(
    algorithm={json.dumps(algorithm)},
    recovered_key_hex={json.dumps(recovered_key_hex)},
    cpa_detail_file={json.dumps(cpa_detail_file)},
    plaintext_npy={json.dumps(plaintext_npy)},
    ciphertext_npy={json.dumps(ciphertext_npy)},
    gap_threshold={gap_threshold},
    max_candidates_per_byte={max_candidates_per_byte},
    max_combinations={max_combinations},
    extra_cpa_detail_files={jextra}
)
print(_json.dumps(result, ensure_ascii=False))
"""
        return JupyterAPITool().run(code)


class CryptoTool(_RunDirMixin, BaseTool):
    name: str = "encrypt_decrypt_verify"
    description: str = (
        "Encrypt or decrypt data using AES/DES/SM4 to verify recovered keys. "
        "Two verification directions: (1) encrypt plaintext with recovered key, compare with ciphertext; "
        "(2) decrypt ciphertext with recovered key, compare with plaintext. "
        "Supports AES-128/192/256, DES-64, SM4-128 in ECB or CBC mode. "
        "IMPORTANT: If verification shows PARTIAL_MISMATCH, check each byte's CPA correlation gap — "
        "bytes with gap > 20% are likely correct, only retry for low-gap bytes.")
    description: str = (
        "Encrypt or decrypt data using AES/DES/SM4. "
        "For CPA key verification: provide BOTH plaintext_npy AND ciphertext_npy (preferred — guarantees dataset-correct values). "
        "Or provide plaintext_hex AND ciphertext_hex (BUT NEVER use NIST/RFC test vectors like '00112233...EEFF' — they are not your dataset). "
        "Without ciphertext (hex or npy), tool returns NOT_VERIFIED and only shows raw crypto output. "
        "Preferred CPA workflow: provide recovered_key + plaintext_npy + ciphertext_npy, "
        "then only call key_search if verification=MISMATCH. "
        "Supports AES-128/192/256, DES-64, SM4-128 in ECB or CBC mode.")
    args_schema: Type[BaseModel] = CryptoInput

    def _run(self, key_hex, algorithm="AES", mode="ECB", operation="encrypt",
             plaintext_hex=None, ciphertext_hex=None,
             plaintext_npy=None, ciphertext_npy=None, trace_index=0):
        # 自动读 npy → hex（避免 agent 编 NIST 测试向量这种 false negative）
        # 注意：npy 路径可能是相对 session directory 的，主进程 cwd 不同
        # 所以先尝试原路径，找不到就在 AGENT_RUN_DIR 下找
        import os as _os
        def _resolve_npy(path):
            if path and not _os.path.isabs(path) and not _os.path.exists(path):
                run_dir = _os.environ.get("AGENT_RUN_DIR", "")
                candidate = _os.path.join(run_dir, path)
                if _os.path.exists(candidate):
                    return candidate
            return path

        warnings = []
        if plaintext_npy and not plaintext_hex:
            try:
                import numpy as _np
                pt = _np.load(_resolve_npy(plaintext_npy))
                plaintext_hex = pt[trace_index].tobytes().hex()
            except Exception as e:
                warnings.append(f"Failed to load plaintext_npy: {e}")
        if ciphertext_npy and not ciphertext_hex:
            try:
                import numpy as _np
                ct = _np.load(_resolve_npy(ciphertext_npy))
                ciphertext_hex = ct[trace_index].tobytes().hex()
            except Exception as e:
                warnings.append(f"Failed to load ciphertext_npy: {e}")
        if not plaintext_hex:
            return json.dumps({
                "verification": "NOT_VERIFIED",
                "details": "ERROR: must provide plaintext_hex or plaintext_npy. " + " | ".join(warnings),
            }, ensure_ascii=False)

        # json.dumps(None) → "null"，但 Python 里应该是 None
        ct_arg = json.dumps(ciphertext_hex) if ciphertext_hex else "None"
        code = f"""
{self._tool_import_prelude()}
import json as _json
from encrypt_decrypt_verify_tool import crypto_operate
result = crypto_operate(
    plaintext_hex={json.dumps(plaintext_hex)},
    key_hex={json.dumps(key_hex)},
    algorithm={json.dumps(algorithm)},
    mode={json.dumps(mode)},
    operation={json.dumps(operation)},
    ciphertext_hex={ct_arg}
)
print(_json.dumps(result, ensure_ascii=False))
"""
        return JupyterAPITool().run(code)

class CorrelationTool(_RunDirMixin, BaseTool):
    name: str = "plaintext_ciphertext_correlation"
    description: str = (
        "Plaintext/ciphertext correlation analysis: compute Pearson correlation between "
        "plaintext (or ciphertext) byte Hamming Weight and power trace at each time point. "
        "Use this to locate the leakage region when CPA on the full waveform gives weak signal. "
        "Returns peak correlation region and suggested CPA range. "
        "NOTE: If CPA already gives strong signal on the full waveform, this tool is NOT needed.")
    args_schema: Type[BaseModel] = CorrelationInput

    def _run(self, wave_npy, data_npy, data_type="plaintext", byte_index=0, model="HW"):
        plot_path = self._auto_path("correlation", "png")
        code = f"""
{self._tool_import_prelude()}
import json as _json
from plaintext_ciphertext_correlation_tool import correlation_analysis
result = correlation_analysis(
    wave_npy={json.dumps(wave_npy)},
    data_npy={json.dumps(data_npy)},
    data_type={json.dumps(data_type)},
    byte_index={byte_index},
    model={json.dumps(model)},
    save_plot={json.dumps(plot_path)}
)
print(_json.dumps(result, ensure_ascii=False))
"""
        return JupyterAPITool().run(code)

class KGSearchTool(BaseTool):
    """纯关键词搜索——不调LLM，直接查Neo4j返回原始JSON"""
    name: str = "kg_search"
    description: str = (
        "Search the DKG knowledge graph using keywords. Returns raw knowledge entries matching the keywords. "
        "You must provide specific SCA-related keywords. The tool does pure keyword matching, no interpretation. "
        "Use when you need: attack parameters, preprocessing methods, diagnostic causes, "
        "alternative components, or recommended actions from the knowledge base.")
    args_schema: Type[BaseModel] = KGSearchInput
    _searcher: Optional[DKGSearcher] = PrivateAttr(default=None)

    def set_searcher(self, s): self._searcher = s

    def _run(self, keywords):
        if not self._searcher: return "Error: KG searcher not initialized"
        try: return self._searcher.search(keywords)
        except Exception as e: return f"KG Error: {e}"


# ==================== System Prompt ====================
def build_system_prompt(kg_knowledge, run_dir, mode="dkg"):
    """Build system prompt for the agent.

    ``mode`` selects how external knowledge is presented:
      - "dkg"            : injected DKG knowledge + on-demand kg_search tool (default)
      - "rag"            : injected RAG-retrieved chunks + on-demand rag_search tool
      - "no_kg"          : tool-only baseline (no external knowledge, full 11 tools)
      - "python_only"    : Python-kernel-only baseline (only python_jupyter, no SCA tools, no knowledge)
      - "knowledge_only" : Knowledge baseline (python_jupyter + KG, no SCA tools); agent
                           must implement attacks in Python while using KG for guidance
    """
    if mode == "dkg":
        knowledge_section = (
            "**[Knowledge from Graph]**\n"
            "The following is raw knowledge from the DKG knowledge graph. \n"
            "IMPORTANT: This knowledge is for REFERENCE ONLY — it may be incomplete, "
            "inaccurate for your specific scenario, or based on different devices/datasets. \n"
            "You MUST apply your own SCA expertise to:\n"
            "- Evaluate whether each suggestion is appropriate for this specific case\n"
            "- Adapt parameters based on actual waveform characteristics you observe\n"
            "- Make independent decisions when KG knowledge conflicts with your analysis\n"
            "Do not blindly follow KG recommendations without verifying they apply to the current data.\n\n"
            f"{kg_knowledge}\n"
        )
        how_to_work_extra = (
            "- Use kg_search ONLY when:\n"
            "  (1) You encounter an unexpected result (e.g., too many traces discarded, \n"
            "      verification failed, correlation too low)\n"
            "  (2) You are unsure about a specific parameter and want to check best practices\n"
            "- Do NOT search before every step — trust your own analysis first.\n"
        )
    elif mode == "rag":
        knowledge_section = (
            "**[Retrieved Documents (RAG)]**\n"
            "The following text chunks were retrieved from a 166-document SCA corpus by dense vector\n"
            "similarity to your task description. They are unstructured excerpts and may be partially\n"
            "off-topic. Use them as context, not as authoritative instructions:\n"
            "- Verify each suggestion against your own SCA expertise.\n"
            "- Adapt parameters based on actual waveform characteristics you observe.\n"
            "- Make independent decisions when retrieved text conflicts with your analysis.\n\n"
            f"{kg_knowledge}\n"
        )
        how_to_work_extra = (
            "- Use rag_search ONLY when:\n"
            "  (1) You encounter an unexpected result and need additional context\n"
            "  (2) You are unsure about a specific parameter and want to look up references\n"
            "- Do NOT search before every step — trust your own analysis first.\n"
        )
    elif mode == "python_only":
        knowledge_section = (
            "**[No External Knowledge / No Specialized Tools]**\n"
            "You only have access to a Python (Jupyter) kernel. No SCA-specific tools, no knowledge\n"
            "graph, no retrieved documents. Implement everything (waveform inspection, alignment,\n"
            "CPA, key search, encrypt/decrypt verification) yourself with numpy/scipy/sklearn etc.\n"
        )
        how_to_work_extra = (
            "- Plan the full attack pipeline yourself: load traces, inspect, preprocess, attack, recover, verify.\n"
            "- Write all SCA logic in Python directly (e.g., compute Pearson correlation between hypothesized\n"
            "  intermediate values and trace samples; implement DES/AES/SM4 key schedule reverse if needed).\n"
            "- You may install or import any pure-Python or numpy/scipy library available in the kernel.\n"
        )
    elif mode == "knowledge_only":
        knowledge_section = (
            "**[Knowledge from Graph]**\n"
            "The following is raw knowledge from the DKG knowledge graph. \n"
            "IMPORTANT: This knowledge is for REFERENCE ONLY — it may be incomplete, "
            "inaccurate for your specific scenario, or based on different devices/datasets. \n"
            "You MUST apply your own SCA expertise to:\n"
            "- Evaluate whether each suggestion is appropriate for this specific case\n"
            "- Adapt parameters based on actual waveform characteristics you observe\n"
            "- Make independent decisions when KG knowledge conflicts with your analysis\n"
            "Do not blindly follow KG recommendations without verifying they apply to the current data.\n\n"
            f"{kg_knowledge}\n"
            "\n"
            "**[No SCA-Specific Tools — Implementation Required]**\n"
            "You have access to a Python (Jupyter) kernel and the kg_search tool, but NO\n"
            "specialized SCA tools. You must implement the entire attack pipeline yourself\n"
            "(waveform inspection, alignment, CPA, key search, encrypt/decrypt verification)\n"
            "in Python with numpy/scipy/sklearn/pycryptodome etc.\n"
        )
        how_to_work_extra = (
            "- The KG provides configuration guidance and diagnostic strategies; use it to\n"
            "  decide WHAT to do (attack point, leakage model, preprocessing chain, etc.).\n"
            "- Write all SCA logic in Python yourself: there are NO specialized tools for CPA,\n"
            "  alignment, key search, or crypto verification. Use jupyter + numpy/scipy.\n"
            "- Use kg_search ONLY when:\n"
            "  (1) You encounter an unexpected result (e.g., low correlation, verification failed)\n"
            "  (2) You are unsure about a specific parameter and want to check best practices\n"
            "- Do NOT search before every step — trust your own analysis first.\n"
        )
    else:  # "no_kg"
        knowledge_section = (
            "**[No External Knowledge]**\n"
            "You have access to the SCA tool suite but no knowledge graph or retrieved documents.\n"
            "Rely on your own SCA expertise to choose tool parameters.\n"
        )
        how_to_work_extra = ""

    return f"""You are an expert in side-channel analysis (SCA), specialized in power analysis attacks such as CPA and DPA.

{knowledge_section}
**[Session Directory]**
All files for this session are stored in: {run_dir}
The Python (Jupyter) working directory is already set to this session directory.

**[File Path Rules]**
- Input files: use the EXACT paths from the user's query or from previous tool outputs. Do not modify them.
- Output files (np.save, plt.savefig, json.dump, etc.): **use just the filename** (e.g., `'smoothed.npy'`, `'cpa_result.png'`).
  The working directory is already the session directory, so files will be saved there automatically.
  Do NOT prepend `'{run_dir}/'` or `'../logs/...'` — just use the bare filename.
- When using file paths in Python code, always use forward slashes (/) or raw strings (r'...').
- Never invent, guess, or modify input file paths. If unsure, use python_jupyter with os.listdir() to check.

**[How to Work]**
- Use your own SCA expertise to plan and execute.
- Execute step by step based on YOUR judgment of the waveform characteristics.
{how_to_work_extra}- After each tool call, evaluate the result yourself before deciding next action.
"""


# ==================== 关键词提取Prompt ====================
KEYWORD_EXTRACTION_PROMPT = """You are a side-channel analysis expert. Extract a FEW, HIGH-QUALITY search keywords from the user's request to query a DUAL-LAYER knowledge graph (upper = configuration space with 12 entity types: Algorithm / DeviceClass / TraceType / AttackPoint / LeakageModel / Preprocessing / StatMethod / Countermeasure / Pipeline / DiagnosticMethod / ValidationMethod / RecoveryMethod; lower = diagnostic space: Observation / Cause / Action / Strategy).

User request:
"{query}"

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
"""


# ==================== Query 定义 ====================

_TRACES_BASE = "./data/traces"

# 所有案例的 query 模板（取消注释要跑的，或用 BATCH_QUERIES 批量跑）
ALL_QUERIES = {
    # --- 已跑完的 3 个 ---
    "AES-7816": f"帮我对一个接触式智能卡实现的AES密码算法波形进行CPA恢复密钥，明文文件为'{_TRACES_BASE}/AES_128_7816/AES-128-7816-100traces-7400points_plain.npy'，密文文件为'{_TRACES_BASE}/AES_128_7816/AES-128-7816-100traces-7400points_cipher.npy',原始波形文件为'{_TRACES_BASE}/AES_128_7816/AES-128-7816-100traces-7400points_wave.npy'",

    "DES-7816": f"帮我对一个接触式智能卡实现的DES密码算法波形进行CPA恢复密钥，明文文件为'{_TRACES_BASE}/DES-64-7816/DES-64-7816-100traces-2000points_plain.npy'，密文文件为'{_TRACES_BASE}/DES-64-7816/DES-64-7816-100traces-2000points_cipher.npy',原始波形文件为'{_TRACES_BASE}/DES-64-7816/DES-64-7816-100traces-2000points_wave.npy'",

    "SM4-7816": f"帮我对一个接触式智能卡实现的SM4密码算法波形进行CPA恢复密钥，SM4需要分4轮分别做CPA恢复轮密钥，然后从4个轮密钥反推主密钥。明文文件为'{_TRACES_BASE}/SM4-128-7816/SM4-128-7816-100traces-6500points_plain.npy'，密文文件为'{_TRACES_BASE}/SM4-128-7816/SM4-128-7816-100traces-6500points_cipher.npy',原始波形文件为'{_TRACES_BASE}/SM4-128-7816/SM4-128-7816-100traces-6500points_wave.npy'",

    # --- 待跑的 5 个 ---
    "AES-14443": f"帮我对一个非接触式智能卡实现的AES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'{_TRACES_BASE}/AES-128-14443/AES-128-14443-5000traces-1900points_plain.npy'，密文文件为'{_TRACES_BASE}/AES-128-14443/AES-128-14443-5000traces-1900points_cipher.npy',原始波形文件为'{_TRACES_BASE}/AES-128-14443/AES-128-14443-5000traces-1900points_wave.npy'",

    "AES-FPGA": f"帮我对一个FPGA硬件实现的AES密码算法波形进行CPA恢复密钥，这是硬件实现，可能不需要滤波，可能需要纵向对齐，泄漏模型可能需要用Hamming Distance。明文文件为'{_TRACES_BASE}/AES-128-FPGA/AES-128-FPGA-2000traces-300points_plain.npy'，密文文件为'{_TRACES_BASE}/AES-128-FPGA/AES-128-FPGA-2000traces-300points_cipher.npy',原始波形文件为'{_TRACES_BASE}/AES-128-FPGA/AES-128-FPGA-2000traces-300points_wave.npy'",

    "AES-STM32F103": f"帮我对一个STM32F103 MCU软件实现的AES密码算法波形进行CPA恢复密钥，明文文件为'{_TRACES_BASE}/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_plain.npy'，密文文件为'{_TRACES_BASE}/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_cipher.npy',原始波形文件为'{_TRACES_BASE}/AES-128-STM32F103/AES-128-STM32F103-250traces-1500points_wave.npy'",

    "AES-STM32F429": f"帮我对一个STM32F429 MCU软件实现的AES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'{_TRACES_BASE}/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_plain.npy'，密文文件为'{_TRACES_BASE}/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_cipher.npy',原始波形文件为'{_TRACES_BASE}/AES-128-STM32F429/AES-128-STM32F429-EM-1000traces-1000points_wave.npy'",

    "DES-14443": f"帮我对一个非接触式智能卡实现的DES密码算法波形进行CPA恢复密钥，这是电磁侧信道（EM），明文文件为'{_TRACES_BASE}/DES-64-14443/DES-64-14443-10000traces-300points_plain.npy'，密文文件为'{_TRACES_BASE}/DES-64-14443/DES-64-14443-10000traces-300points_cipher.npy',原始波形文件为'{_TRACES_BASE}/DES-64-14443/DES-64-14443-10000traces-300points_wave.npy'",
}


# ==================== Main ====================
def main():
    # ========== 要跑的案例 ==========
    # 通过环境变量 EVAL_CASES 可以覆盖（eval 脚本用）
    _cases_env = os.environ.get("EVAL_CASES")
    if _cases_env:
        query_keys = _cases_env.split(",")
    else:
        query_keys = ["AES-7816", "DES-7816", "SM4-7816", "AES-14443", "AES-FPGA", "AES-STM32F103", "AES-STM32F429", "DES-14443"]

    # ========== 模型配置 ==========
    config = load_config()

    base_url = config["api"]["siliconflow"]["base_url"]
    # api_key 路由：每个模型独占一个 key，避免 TPM (tokens per minute) 撞车
    # 4 个模型并行时各走各的 key，互不限速
    # 大规模 exp3 启用 DSv3.2 + Qwen3.5 + GLM-5 + M2.5 四路并行，
    # 各占一个 key（api_key / api_key_2 / api_key_pro / api_key_pro_2）。
    MODEL_TO_KEY_FIELD = {
        # Pro 系列（走 api_key_pro / api_key_pro_2）
        "Pro/MiniMaxAI/MiniMax-M2.5":       "api_key_pro",
        "Pro/zai-org/GLM-5":                "api_key_pro_2",
        # 普通系列（走 api_key / api_key_2）
        "deepseek-ai/DeepSeek-V3.2":        "api_key",
        "Qwen/Qwen3.5-397B-A17B":           "api_key_2",
        # 其他（保留作单独测试用，不进 4 路并行默认组）
        "moonshotai/Kimi-K2-Instruct-0905": "api_key_2",
        "deepseek-ai/DeepSeek-V3.1-Terminus": "api_key",
    }
    def _get_api_key(model_name):
        """根据模型名路由到对应的 api_key 字段；未知模型走 fallback。

        环境变量 EVAL_API_KEY_FIELD 可以强制覆盖路由（用于并行 baseline
        实验时手动错峰 — 例如 RAG 走 api_key_2 让 Python-only 独占 api_key）。
        """
        sf = config["api"]["siliconflow"]
        forced = os.environ.get("EVAL_API_KEY_FIELD")
        if forced and sf.get(forced):
            return sf[forced]
        key_field = MODEL_TO_KEY_FIELD.get(model_name)
        if key_field and sf.get(key_field):
            return sf[key_field]
        # fallback: Pro/ 开头用 pro key，否则用普通 key
        if model_name.startswith("Pro/"):
            return sf["api_key_pro"]
        return sf["api_key"]
    def _get_key_field(model_name):
        """返回当前模型用的 key 字段名（用于打印）"""
        forced = os.environ.get("EVAL_API_KEY_FIELD")
        if forced:
            return forced
        return MODEL_TO_KEY_FIELD.get(
            model_name,
            "api_key_pro" if model_name.startswith("Pro/") else "api_key"
        )

    # 初始占位（循环里按 model 重新取）
    api_key = config["api"]["siliconflow"]["api_key_pro"]

    # 通过环境变量 EVAL_MODELS 可以覆盖（eval 脚本用）
    _models_env = os.environ.get("EVAL_MODELS")
    if _models_env:
        models_to_test = _models_env.split(",")
    else:
        models_to_test = [
            "Pro/MiniMaxAI/MiniMax-M2.5",
            "Pro/zai-org/GLM-5",
            "Qwen/Qwen3.5-397B-A17B",
            "moonshotai/Kimi-K2-Instruct-0905",
        ]

    model = models_to_test[0]

    # KG 开关（eval 脚本用于跑 baseline: USE_KG=0 表示不注入 KG 知识）
    use_kg = os.environ.get("USE_KG", "1") != "0"

    # 第二档 baseline 开关：RAG（dense vector retrieval over the same 166-doc corpus）
    # USE_RAG=1 + USE_KG=0 = RAG agent variant: 用 RAG 检索取代 KG 注入 + 加 rag_search 工具
    use_rag = os.environ.get("USE_RAG", "0") == "1"

    # 第三档 baseline 开关：tools_mode
    #   "full"        : 全 11 工具（10 SCA 工具 + 可选 kg_search/rag_search）—— DKG / No-KG / RAG 都用
    #   "python_only" : 仅 python_jupyter 一个工具，其它工具全部移除（Python-only baseline）
    tools_mode = os.environ.get("TOOLS_MODE", "full")
    if tools_mode not in ("full", "python_only"):
        print(f"  [WARN] Unknown TOOLS_MODE='{tools_mode}', falling back to 'full'")
        tools_mode = "full"

    # 日志目录前缀（eval 脚本分组用）
    log_subdir = os.environ.get("LOG_SUBDIR", "")

    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "dkg123456"

    # ========== 公共初始化（只做一次）==========
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools").replace(os.sep, '/')

    # 通过环境变量支持自定义端口（用于并行跑）
    jupyter_port = int(os.environ.get("JUPYTER_PORT", "5055"))

    print(f"\n[Init] Jupyter Kernel (port {jupyter_port})...")
    start_kernel_if_needed(port=jupyter_port)
    configure_kernel_context(port=jupyter_port, tools_dir=tools_dir)
    print(f"  Jupyter path: {tools_dir}")

    print("[Init] Neo4j...")
    kg_searcher = DKGSearcher(uri=neo4j_uri, username=neo4j_user, password=neo4j_password)

    # 模型名简称映射
    _MODEL_SHORT = {
        "DeepSeek-V3.1-Terminus": "DSv3.1T",
        "claude-opus-4.6": "Opus4.6",
        "MiniMax-M2.5": "MiniMaxM2.5",
        "Kimi-K2.5": "KimiK2.5",
        "GLM-5": "GLM5",
        "Qwen3-235B-A22B": "Qwen3-235B",
    }
    # ========== 循环跑每个案例 ==========
    n_rounds = int(os.environ.get("EVAL_ROUNDS", "1"))  # 每个模型×每个案例跑几轮
    n_total = n_rounds * len(models_to_test) * len(query_keys)
    run_count = 0

    for round_i in range(n_rounds):
      for model in models_to_test:
        _raw_model = model.split("/")[-1]
        _model_short = _MODEL_SHORT.get(_raw_model, _raw_model)

        for qi, qkey in enumerate(query_keys):
          query = ALL_QUERIES[qkey]
          run_count += 1
          timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
          kg_tag = "DKG" if use_kg else "NoKG"
          dir_name = f"{qkey}_{_model_short}_{kg_tag}_{timestamp}"
          base_log_dir = os.path.join("..", "logs", log_subdir) if log_subdir else os.path.join("..", "logs")
          run_dir = os.path.join(base_log_dir, dir_name)
          os.makedirs(run_dir, exist_ok=True)
          os.environ["AGENT_RUN_DIR"] = run_dir

          print(f"\n{'='*60}")
          print(f"[{run_count}/{n_total}] Round {round_i+1}/{n_rounds} | Model: {_model_short} | Case: {qkey}")
          print(f"Session: {run_dir}")
          print(f"{'='*60}")

          # 检测 kernel 是否存活，死了就重启
          ensure_kernel_alive(port=jupyter_port)

          # 切换 Jupyter cwd 到新的 session directory
          abs_run_dir = os.path.abspath(run_dir).replace(os.sep, '/')
          configure_kernel_context(port=jupyter_port, tools_dir=tools_dir, run_dir=abs_run_dir)
          print(f"  Jupyter cwd: {abs_run_dir}")

          # 根据当前模型名动态选 api_key（4 模型分别独占 4 个 key）
          current_api_key = _get_api_key(model)
          key_type = _get_key_field(model)
          print(f"[Init] LLM ({model}, using {key_type})...")
          llm = ChatOpenAI(
            model=model,
            temperature=0.1,
            max_tokens=163840,
            base_url=base_url,
            api_key=current_api_key
          )
          llm_with_retry = llm.with_retry(
            retry_if_exception_type=(InternalServerError, RateLimitError, APIStatusError, APITimeoutError),
            wait_exponential_jitter=True,
            stop_after_attempt=LLM_RETRY_MAX_RETRIES + 1,
            exponential_jitter_params={
              "initial": LLM_RETRY_INITIAL_DELAY,
              "max": LLM_RETRY_MAX_DELAY,
              "exp_base": LLM_RETRY_BACKOFF_FACTOR,
              "jitter": 1.0,
            },
          )
          model_retry = ModelRetryMiddleware(
            max_retries=LLM_RETRY_MAX_RETRIES,
            retry_on=should_retry_llm_exception,
            on_failure="error",
            initial_delay=LLM_RETRY_INITIAL_DELAY,
            max_delay=LLM_RETRY_MAX_DELAY,
            backoff_factor=LLM_RETRY_BACKOFF_FACTOR,
            jitter=True,
          )
          print(
            f"  LLM retry: max_retries={LLM_RETRY_MAX_RETRIES}, "
            f"initial_delay={LLM_RETRY_INITIAL_DELAY}s, max_delay={LLM_RETRY_MAX_DELAY}s"
          )

          # ======================================================
          # 阶段1：从用户query提取关键词（LLM调用，在main里做）
          # ======================================================
          print("\n[Phase 1] Extracting keywords from user query...")
          init_log = {}

          keyword_prompt = KEYWORD_EXTRACTION_PROMPT.format(query=query)
          init_log["keyword_prompt"] = keyword_prompt

          keyword_response = llm_with_retry.invoke(keyword_prompt)
          llm_raw_response = str(keyword_response.content)
          init_log["llm_raw_response"] = llm_raw_response
          print(f"  LLM response: {llm_raw_response}")

          try:
            text = llm_raw_response.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            keywords = json.loads(text)
            if not isinstance(keywords, list):
                keywords = [str(keywords)]
          except:
            keywords = re.findall(r'"([^"]+)"', llm_raw_response)
            if not keywords:
                keywords = ["AES", "CPA", "smartcard", "power"]

          init_log["parsed_keywords"] = keywords
          print(f"  Parsed keywords: {keywords}")

          # ======================================================
          # 阶段2：用关键词搜索知识图谱（纯代码，不调LLM）
          # ======================================================
          if use_kg:
            print("\n[Phase 2] Searching knowledge graph...")
            init_log["kg_config"] = dict(kg_searcher.config)
            kg_raw_result = kg_searcher.search(keywords)
          elif use_rag:
            print("\n[Phase 2] Retrieving RAG context (dense vector search over 166-doc corpus)...")
            # Lazy import: only loaded when RAG mode is enabled
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eval", "exp_rag"))
            from rag_search_tool import build_rag_initial_context
            kg_raw_result = build_rag_initial_context(query, top_k=5)
            init_log["kg_config"] = {"mode": "rag", "top_k": 5}
          else:
            mode_label = "Python-only" if tools_mode == "python_only" else "tool-only No-KG"
            print(f"\n[Phase 2] No external knowledge ({mode_label} baseline)")
            init_log["kg_config"] = {"disabled": True, "mode": tools_mode}
            kg_raw_result = ""
          init_log["kg_raw_result"] = kg_raw_result
          print(f"  Initial knowledge: {len(kg_raw_result)} chars")

          # ======================================================
          # 阶段3：构建System Prompt + 创建Agent
          # ======================================================
          print("\n[Phase 3] Building agent...")

          # Determine prompt + tools mode
          if tools_mode == "python_only":
              if use_kg:
                  prompt_mode = "knowledge_only"
              else:
                  prompt_mode = "python_only"
          elif use_kg:
              prompt_mode = "dkg"
          elif use_rag:
              prompt_mode = "rag"
          else:
              prompt_mode = "no_kg"

          system_prompt = build_system_prompt(kg_raw_result, run_dir, mode=prompt_mode)

          jupyter_tool = JupyterAPITool(image_save_path=run_dir)
          jupyter_tool.set_run_dir(run_dir)

          if tools_mode == "python_only":
              # Python-kernel baseline: jupyter only, no SCA tools.
              # If USE_KG=1, additionally provide kg_search → Knowledge-Only baseline.
              tools = [jupyter_tool]
              if use_kg:
                  kg_tool = KGSearchTool()
                  kg_tool.set_searcher(kg_searcher)
                  tools.append(kg_tool)
          else:
              # Full SCA tool suite (10 tools) + optional kg_search / rag_search
              kg_tool = KGSearchTool()
              kg_tool.set_searcher(kg_searcher)
              smooth_tool = WeightedMovingAverageTool()
              align_tool = StaticAlignTool()
              cpa_tool = CPATool()
              des_cpa_tool = DESCPATool()
              sm4_cpa_tool = SM4CPATool()
              verify_tool = CryptoTool()
              search_tool = KeySearchTool()
              valign_tool = VerticalAlignTool()
              corr_tool = CorrelationTool()
              for t in [smooth_tool, align_tool, cpa_tool, valign_tool,
                        verify_tool, search_tool, des_cpa_tool, sm4_cpa_tool, corr_tool]:
                  if hasattr(t, 'set_run_dir'): t.set_run_dir(run_dir)
              tools = [smooth_tool, align_tool, valign_tool, corr_tool, cpa_tool,
                       des_cpa_tool, sm4_cpa_tool, verify_tool, search_tool, jupyter_tool]
              if use_kg:
                  tools.append(kg_tool)
              elif use_rag:
                  sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eval", "exp_rag"))
                  from rag_search_tool import RAGSearchTool
                  rag_tool = RAGSearchTool()
                  rag_tool.set_run_dir(run_dir)
                  tools.append(rag_tool)

          logger = FullContextLogger(run_dir=run_dir)
          agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
            middleware=[model_retry],
          )

          # ======================================================
          # 阶段4：运行Agent
          # ======================================================
          print(f"\n{'=' * 60}\nRunning agent...\nQuery: {query[:100]}...\n{'=' * 60}\n")
          start_time = time.time()

          messages_collected = []
          token_records = []

          # ====== D 护栏：运行时检测域外跑偏 + 卡 jupyter ======
          # 域外关键词：第 9 轮观察到 GLM-5 串到了别的项目代码（broker / cash / pos_checker）
          OFF_TRACK_KEYWORDS = [
              "calculate_cash", "broker", "pos_checker",
              "stock_price", "trading_strategy", "portfolio",
              "todo_list", "calendar.ics",
          ]
          STUCK_JUPYTER_THRESHOLD = 4   # 连续 4 轮只用 python_jupyter 不调正式工具 → warn
          guard_warnings = []
          jupyter_streak = 0

          try:
            for step in agent.stream(
                    {"messages": [{"role": "user", "content": query}]},
                    stream_mode="updates",
                    config={"callbacks": [logger]}
            ):
                for _, node_output in step.items():
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            messages_collected.append(msg)
                            mt = type(msg).__name__
                            c = str(msg.content) if hasattr(msg, 'content') else ""

                            if mt == "AIMessage":
                                if hasattr(msg, 'response_metadata') and msg.response_metadata:
                                    rm = msg.response_metadata
                                    usage = rm.get("token_usage") or rm.get("usage") or {}
                                    if usage:
                                        token_records.append({
                                            "prompt_tokens": usage.get("prompt_tokens", 0),
                                            "completion_tokens": usage.get("completion_tokens", 0),
                                            "total_tokens": usage.get("total_tokens", 0),
                                        })

                                if c: print(f"\n🤖 [LLM]: {c[:500]}")

                                # D 护栏 1: 域外关键词检测
                                c_lower = c.lower()
                                hit = [kw for kw in OFF_TRACK_KEYWORDS if kw.lower() in c_lower]
                                if hit:
                                    warn = f"off-track keywords at round {len(token_records)}: {hit}"
                                    if warn not in guard_warnings:
                                        guard_warnings.append(warn)
                                        print(f"\n⚠️  [GUARD] LLM output contains off-task keywords: {hit}")
                                        print(f"        Likely model context contamination. Will not auto-interrupt; flagged for review.")

                                # D 护栏 2: 连续 jupyter 轮数
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    names = [tc.get('name', '?') for tc in msg.tool_calls]
                                    if all(n == 'python_jupyter' for n in names):
                                        jupyter_streak += 1
                                    else:
                                        jupyter_streak = 0
                                    for tc in msg.tool_calls:
                                        print(f"\n🔧 [Tool Call]: {tc['name']}({json.dumps(tc['args'], ensure_ascii=False)[:200]})")
                                if jupyter_streak == STUCK_JUPYTER_THRESHOLD:
                                    warn = f"stuck in python_jupyter for {STUCK_JUPYTER_THRESHOLD} consecutive rounds (round {len(token_records)})"
                                    guard_warnings.append(warn)
                                    print(f"\n⚠️  [GUARD] {warn}; consider calling cpa/key_search/verify wrapper instead.")

                            elif mt == "ToolMessage":
                                lim = 1500 if ("ERROR" in c or "Error" in c) else 500
                                print(f"\n📋 [Tool Result]: {c[:lim]}{'...' if len(c) > lim else ''}")

                # 每轮实时保存日志
                duration = time.time() - start_time
                log_path = os.path.join(run_dir, "agent_log.md")
                logger.write_log(log_path, meta={
                    "Model": model, "API": base_url, "Start Time": timestamp,
                    "Duration": f"{duration:.1f}s (running...)", "Directory": run_dir,
                    "Neo4j": neo4j_uri, "Tools": ", ".join(t.name for t in tools), "Query": query,
                    "guard_warnings": guard_warnings,
                }, init_log=init_log, system_prompt=system_prompt, tools=tools,
                                 messages=messages_collected, token_records=token_records)

          except KeyboardInterrupt:
            print(f"\n⚠️ Agent interrupted by user on case {qkey}")
          except Exception as e:
            print(f"\nError on case {qkey}: {e}")
            import traceback; traceback.print_exc()
          finally:
            duration = time.time() - start_time
            log_path = os.path.join(run_dir, "agent_log.md")
            logger.write_log(log_path, meta={
                "Model": model, "API": base_url, "Start Time": timestamp,
                "Duration": f"{duration:.1f}s", "Directory": run_dir,
                "Neo4j": neo4j_uri, "Tools": ", ".join(t.name for t in tools), "Query": query,
                "guard_warnings": guard_warnings,
            }, init_log=init_log, system_prompt=system_prompt, tools=tools,
                             messages=messages_collected, token_records=token_records)
            if guard_warnings:
                print(f"\n⚠️  [GUARD SUMMARY] {len(guard_warnings)} warning(s) raised in this case:")
                for w in guard_warnings:
                    print(f"      - {w}")
            print(f"\n[DONE] [{qi+1}/{len(query_keys)}] {qkey} done. Log: {log_path}")

    # 循环结束，关闭资源
    kg_searcher.close()
    print(f"\n{'='*60}\nAll {n_rounds} rounds x {len(models_to_test)} models x {len(query_keys)} cases = {n_total} runs completed!\n{'='*60}")

if __name__ == "__main__":
    main()


