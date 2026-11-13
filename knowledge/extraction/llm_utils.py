"""
共享 LLM 调用与 scope 过滤工具（供 step1/2/3 复用）

内容：
- call_llm_with_retry: 指数退避重试（429/503/timeout）+ usage/finish_reason 日志
- estimate_tokens: 粗估 token 数（中英混合）
- chunk_markdown_by_sections: 按 ## 标题层级切分 md，兜底 token 阈值
- SCOPE: 范围锚定清单 + scope_filter_upper / scope_filter_lower 后处理白名单过滤
"""

from __future__ import annotations

import re
import time
from typing import Any

from openai import (
    OpenAI,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)


# ============================================================================
# LLM 调用（含 retry/backoff + usage 日志）
# ============================================================================

RETRYABLE_EXCEPTIONS = (
    RateLimitError,           # 429
    InternalServerError,      # 500/503
    APITimeoutError,
)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _stream_collect(
    *,
    client: OpenAI,
    model: str,
    messages: list,
    temperature: float,
    max_tokens: int,
    extra_body: dict | None,
) -> tuple[str, str | None, Any, str]:
    """
    发起 stream=True 调用，逐 chunk 收集 content + reasoning_content + usage。
    返回 (content, finish_reason, usage_obj, reasoning_content)。

    关键点：流式下单次 chunk 间隔 < 60s，SDK 不会因"生成太慢"超时。
    要拿到 usage 需要 stream_options={"include_usage": True}（SiliconFlow / OpenAI 都支持）。
    """
    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    finish_reason: str | None = None
    usage_obj = None

    stream_iter = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=extra_body,
        stream=True,
        stream_options={"include_usage": True},
    )

    for chunk in stream_iter:
        # usage 通常在最后一个 chunk（choices 为空）里返回
        if getattr(chunk, "usage", None):
            usage_obj = chunk.usage
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        delta = choice.delta
        if getattr(delta, "content", None):
            content_parts.append(delta.content)
        # SiliconFlow / DeepSeek thinking 模式用 reasoning_content 字段承载推理过程
        rc = getattr(delta, "reasoning_content", None)
        if rc:
            reasoning_parts.append(rc)
        if choice.finish_reason:
            finish_reason = choice.finish_reason

    return (
        "".join(content_parts),
        finish_reason,
        usage_obj,
        "".join(reasoning_parts),
    )


def call_llm_with_retry(
    client: OpenAI,
    model: str,
    messages: list,
    *,
    temperature: float = 0.1,
    max_tokens: int = 16000,
    thinking_budget: int = 16000,
    enable_thinking: bool = True,
    max_retries: int = 5,
    log_usage: bool = True,
    stream: bool = False,
) -> tuple[str, dict]:
    """
    带重试的 LLM 调用。
    返回 (content: str, meta: dict)。meta 含 usage / finish_reason / reasoning_content(前 200 字)。

    stream=True：走流式接收。SDK 默认 600s timeout 是"首字节延迟"，流式接收时每收到一个
    chunk 就刷新一次 keep-alive，可以绕开大输出（20+ 分钟生成）导致的 timeout 问题。
    总耗时和费用跟 stream=False 一样，只是把"一次等完"改成"逐块收"，不超时。
    """
    extra_body: dict[str, Any] = {}
    if enable_thinking:
        extra_body["enable_thinking"] = True
        extra_body["thinking_budget"] = thinking_budget

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            t0 = time.time()
            if stream:
                content, finish, usage_obj, rc = _stream_collect(
                    client=client, model=model, messages=messages,
                    temperature=temperature, max_tokens=max_tokens,
                    extra_body=extra_body or None,
                )
            else:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_body=extra_body or None,
                )
                choice = resp.choices[0]
                content = choice.message.content or ""
                finish = choice.finish_reason
                usage_obj = resp.usage
                rc = getattr(choice.message, "reasoning_content", None) or ""
            elapsed = time.time() - t0

            meta = {
                "prompt_tokens": getattr(usage_obj, "prompt_tokens", None) if usage_obj else None,
                "completion_tokens": getattr(usage_obj, "completion_tokens", None) if usage_obj else None,
                "total_tokens": getattr(usage_obj, "total_tokens", None) if usage_obj else None,
                "finish_reason": finish,
                "elapsed_sec": round(elapsed, 1),
                "reasoning_len": len(rc),
                "attempt": attempt + 1,
                "stream": stream,
            }

            if log_usage:
                mode = "stream" if stream else "once"
                print(f"    [LLM/{mode}] {elapsed:.1f}s  "
                      f"prompt={meta['prompt_tokens']}  "
                      f"completion={meta['completion_tokens']}  "
                      f"finish={finish}  "
                      f"reasoning={meta['reasoning_len']}ch  "
                      f"attempt={meta['attempt']}")

            if finish == "length":
                print(f"    ⚠️  finish_reason=length → output may be truncated. "
                      f"Consider raising max_tokens or shortening input.")

            return content, meta

        except RETRYABLE_EXCEPTIONS as e:
            last_exc = e
            if attempt >= max_retries:
                break
            sleep_sec = min(60, 2 ** attempt + 1)
            print(f"    ⚠️  {type(e).__name__} on attempt {attempt + 1}/{max_retries + 1} — "
                  f"retry in {sleep_sec}s...")
            time.sleep(sleep_sec)

        except APIStatusError as e:
            last_exc = e
            status = getattr(e, "status_code", None)
            if status in RETRYABLE_STATUS_CODES and attempt < max_retries:
                sleep_sec = min(60, 2 ** attempt + 1)
                print(f"    ⚠️  APIStatusError {status} on attempt {attempt + 1}/{max_retries + 1} — "
                      f"retry in {sleep_sec}s...")
                time.sleep(sleep_sec)
                continue
            break

    raise RuntimeError(f"LLM call failed after {max_retries + 1} attempts: {last_exc}")


# ============================================================================
# Token 估算与分块
# ============================================================================

# DeepSeek-V3.2 on SiliconFlow: input hard limit 163840 (160K).
# 预留: prompt 模板 ~4K + thinking 16K + output 16K + safety 4K = 40K reserved.
SAFE_INPUT_TOKENS = 120_000   # 单次调用输入安全上限（留给 prompt 和推理）
CHUNK_TARGET_TOKENS = 80_000  # 切块目标大小（每块 ~80K，给 prompt 和推理留充足空间）


def estimate_tokens(text: str) -> int:
    """
    粗估 token 数：
    - 中文字符 ≈ 1.5 char/token
    - 其他 ASCII/常见拉丁字符 ≈ 4 char/token
    - **其他 Unicode（CID 乱码、BMP 外符号、拉丁扩展、emoji 等）≈ 1 char/token**
      理由：PAP-02 Goubin CID 乱码 236K chars 按 4 估出 59K token 但实际 334K token，
      BPE tokenizer 对非 ASCII/常见字符每 char 切 1-3 个 token，必须保守估。
    """
    if not text:
        return 0
    cn = len(re.findall(r"[\u4e00-\u9fff]", text))
    # 常见 ASCII + 拉丁基础（\u0000-\u024f 覆盖 ASCII / Latin-1 / Latin Extended-A/B）
    ascii_like = len(re.findall(r"[\u0000-\u024f]", text))
    # 其他都按 1 char/token（CID 编码失败 / BMP 特殊符号 / emoji）
    weird = len(text) - cn - ascii_like
    return int(cn / 1.5 + ascii_like / 4 + weird * 1.0)


def chunk_markdown_by_sections(
    text: str,
    target_tokens: int = CHUNK_TARGET_TOKENS,
) -> list[str]:
    """
    把 md 按 ## 标题切成多个 chunk，每个 chunk 尽量 ≤ target_tokens。

    策略：
    1. 先按 '^## ' 切，把文件头（第一个 ## 之前）单独作为 chunk 0
    2. 每个 ## 章节估 token
    3. 贪心合并相邻小章节直到超 target
    4. 单章节 > target_tokens，按段落 re.split 再切二级
    """
    if estimate_tokens(text) <= target_tokens:
        return [text]

    # 按 '\n## ' 切分（保留标题行）
    # 注意：'# ' 的一级标题通常只在开头，不切
    parts = re.split(r"(?=\n##\s)", text)
    if len(parts) == 1:
        # 没有 ## 标题，按段落切
        return _chunk_by_paragraphs(text, target_tokens)

    # 贪心合并
    chunks: list[str] = []
    current = ""
    current_tokens = 0
    for p in parts:
        p_tokens = estimate_tokens(p)
        # 单个章节就超 target，先把当前累积冲掉，然后把这个大章节单独二次切
        if p_tokens > target_tokens:
            if current:
                chunks.append(current)
                current = ""
                current_tokens = 0
            sub_chunks = _chunk_by_paragraphs(p, target_tokens)
            chunks.extend(sub_chunks)
            continue
        # 累加不会超 target，继续合并
        if current_tokens + p_tokens <= target_tokens:
            current += p
            current_tokens += p_tokens
        else:
            chunks.append(current)
            current = p
            current_tokens = p_tokens
    if current:
        chunks.append(current)

    return chunks


def _chunk_by_paragraphs(text: str, target_tokens: int) -> list[str]:
    """段落级二次切分（用于单章节超 target_tokens 的情况）"""
    paragraphs = re.split(r"\n\n+", text)
    chunks: list[str] = []
    current = ""
    current_tokens = 0
    for p in paragraphs:
        p_tokens = estimate_tokens(p)
        if p_tokens > target_tokens:
            # 单段落就超 target（罕见），硬切字符
            if current:
                chunks.append(current)
                current = ""
                current_tokens = 0
            char_limit = target_tokens * 2  # 保守估
            for i in range(0, len(p), char_limit):
                chunks.append(p[i : i + char_limit])
            continue
        if current_tokens + p_tokens <= target_tokens:
            current += ("\n\n" if current else "") + p
            current_tokens += p_tokens
        else:
            chunks.append(current)
            current = p
            current_tokens = p_tokens
    if current:
        chunks.append(current)
    return chunks


# ============================================================================
# Scope Post-Filter 白名单
# ============================================================================

IN_SCOPE_ALGORITHMS = {
    # 主流分组密码（别名归一化后的标准名）
    "AES", "AES-128", "AES-192", "AES-256",
    "DES", "3DES", "TDES", "Triple-DES",
    "SM4", "SMS4",
    "PRESENT", "ARIA", "Camellia", "SEED",
    "SIMON", "SPECK", "GIFT", "SKINNY", "KATAN", "LED",
    "MISTY1", "KASUMI", "CLEFIA",
}

# normalize 函数：不同来源可能写 "AES-128" / "AES128" / "aes 128"
def _normalize_algo_name(name: str) -> str:
    if not name:
        return ""
    return re.sub(r"[\s\-_]+", "", name).upper().replace("TRIPLEDES", "3DES")


OUT_OF_SCOPE_ALGO_KEYWORDS = {
    # 公钥 / PQC / 流 / AEAD
    "RSA", "ECC", "ECDSA", "EDDSA", "ED25519", "X25519",
    "DIFFIEHELLMAN", "DH", "ECDH",
    "DILITHIUM", "KYBER", "FALCON", "SPHINCS", "MCELIECE", "BIKE", "NTRU", "SABER",
    "CHACHA20", "CHACHA", "SALSA20", "ZUC",
    "ASCON", "XOODYAK", "GIMLI", "KETJE", "ISAP",
    "HMAC", "SHA1", "SHA256", "SHA3", "BLAKE",
}

OUT_OF_SCOPE_STATMETHOD_TYPES = {
    "profiled", "deep_learning",
}

OUT_OF_SCOPE_STATMETHOD_NAME_KEYWORDS = {
    "Template Attack", "Template", "Stochastic Attack", "Stochastic",
    "CNN", "MLP", "Transformer", "ResNet",
    "Deep Learning", "DL-SCA", "DL SCA", "Profiled Attack",
    # 故障注入
    "DFA", "Differential Fault", "Fault Injection", "Laser Fault", "Glitch",
}


def is_in_scope_algorithm(name: str | None) -> bool:
    """算法名是否在允许清单"""
    if not name:
        return True  # 未指定不判定为越界（让其他字段兜底）
    norm = _normalize_algo_name(name)
    for allowed in IN_SCOPE_ALGORITHMS:
        if _normalize_algo_name(allowed) == norm:
            return True
    # 检查是否命中越界关键词
    for oos in OUT_OF_SCOPE_ALGO_KEYWORDS:
        if oos in norm:
            return False
    return True  # 未知但不命中越界关键词：保留


def is_in_scope_statmethod(name: str | None, method_type: str | None) -> bool:
    """StatMethod 是否在允许清单"""
    if method_type and method_type.lower() in OUT_OF_SCOPE_STATMETHOD_TYPES:
        return False
    if name:
        for oos in OUT_OF_SCOPE_STATMETHOD_NAME_KEYWORDS:
            if oos.lower() in name.lower():
                return False
    return True


def scope_filter_upper(entities: list[dict], relationships: list[dict]) -> tuple[list[dict], list[dict], list[str]]:
    """
    step2/step3 后处理：对 upper 抽取结果做白名单过滤。
    返回 (保留的 entities, 保留的 relationships, warnings)。
    """
    warnings: list[str] = []
    dropped_names: set[str] = set()

    kept_entities: list[dict] = []
    for e in entities:
        name = e.get("name", "")
        etype = e.get("type", "")
        props = e.get("properties", {}) or {}

        if etype == "Algorithm":
            if not is_in_scope_algorithm(name):
                warnings.append(f"[scope] drop out-of-scope Algorithm: {name}")
                dropped_names.add(name)
                continue
        elif etype == "StatMethod":
            if not is_in_scope_statmethod(name, props.get("type")):
                warnings.append(f"[scope] drop out-of-scope StatMethod: {name} "
                                f"(type={props.get('type')})")
                dropped_names.add(name)
                continue

        kept_entities.append(e)

    # 关系中引用了被丢弃实体的，也丢弃
    kept_rels: list[dict] = []
    for r in relationships:
        subj = r.get("subject", "")
        obj = r.get("object", "")
        if subj in dropped_names or obj in dropped_names:
            warnings.append(f"[scope] drop relationship referencing dropped entity: "
                            f"{subj} -{r.get('relation')}-> {obj}")
            continue
        kept_rels.append(r)

    return kept_entities, kept_rels, warnings
