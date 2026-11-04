"""
Crypto Verification Tool

支持 AES / DES / SM4 的加解密，用于验证CPA恢复的密钥是否正确。

依赖：pip install pycryptodome

用法（agent调用）：
  输入：明文(hex) + 密钥(hex) + 算法 + 模式
  输出：加密结果(hex)，以及与期望密文的比对结果
"""

from Crypto.Cipher import AES, DES
from typing import Optional

# SM4需要单独的库，先尝试导入
try:
    from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
    HAS_SM4 = True
except ImportError:
    try:
        from pysmx.SM4 import Sm4, ENCRYPT, DECRYPT
        HAS_SM4 = True
    except ImportError:
        HAS_SM4 = False


def crypto_operate(
    plaintext_hex: str,
    key_hex: str,
    algorithm: str = "AES",
    mode: str = "ECB",
    operation: str = "encrypt",
    ciphertext_hex: Optional[str] = None,
    iv_hex: Optional[str] = None,
) -> dict:
    """
    执行加解密操作。

    参数：
        plaintext_hex: 明文的十六进制字符串（如 "00112233..."）
        key_hex: 密钥的十六进制字符串
        algorithm: "AES", "DES", "SM4"
        mode: "ECB" 或 "CBC"
        operation: "encrypt" 或 "decrypt"
        ciphertext_hex: 期望的密文（可选，用于验证）
        iv_hex: CBC模式的IV（可选，ECB不需要）

    返回：
        {
            "result_hex": "加密/解密结果的hex",
            "verification": "MATCH" / "MISMATCH" / "NOT_VERIFIED",
            "details": "详细说明"
        }
    """
    try:
        plaintext = bytes.fromhex(plaintext_hex.replace(" ", ""))
        key = bytes.fromhex(key_hex.replace(" ", ""))
        iv = bytes.fromhex(iv_hex.replace(" ", "")) if iv_hex else None

        algorithm = algorithm.upper()
        mode = mode.upper()
        operation = operation.lower()

        # 验证密钥长度
        if algorithm == "AES":
            if len(key) not in (16, 24, 32):
                return {"result_hex": "", "verification": "ERROR",
                        "details": f"AES key must be 16/24/32 bytes, got {len(key)} bytes"}
        elif algorithm == "DES":
            if len(key) != 8:
                return {"result_hex": "", "verification": "ERROR",
                        "details": f"DES key must be 8 bytes, got {len(key)} bytes"}
        elif algorithm == "SM4":
            if len(key) != 16:
                return {"result_hex": "", "verification": "ERROR",
                        "details": f"SM4 key must be 16 bytes, got {len(key)} bytes"}
            if not HAS_SM4:
                return {"result_hex": "", "verification": "ERROR",
                        "details": "SM4 not available. Install gmssl: pip install gmssl"}
        else:
            return {"result_hex": "", "verification": "ERROR",
                    "details": f"Unsupported algorithm: {algorithm}. Use AES, DES, or SM4."}

        # 执行加解密
        if algorithm == "AES":
            if mode == "ECB":
                cipher = AES.new(key, AES.MODE_ECB)
            elif mode == "CBC":
                if iv is None:
                    iv = b'\x00' * 16
                cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            else:
                return {"result_hex": "", "verification": "ERROR",
                        "details": f"Unsupported mode: {mode}. Use ECB or CBC."}

            if operation == "encrypt":
                result = cipher.encrypt(plaintext)
            else:
                result = cipher.decrypt(plaintext)

        elif algorithm == "DES":
            if mode == "ECB":
                cipher = DES.new(key, DES.MODE_ECB)
            elif mode == "CBC":
                if iv is None:
                    iv = b'\x00' * 8
                cipher = DES.new(key, DES.MODE_CBC, iv=iv)
            else:
                return {"result_hex": "", "verification": "ERROR",
                        "details": f"Unsupported mode: {mode}"}

            if operation == "encrypt":
                result = cipher.encrypt(plaintext)
            else:
                result = cipher.decrypt(plaintext)

        elif algorithm == "SM4":
            sm4 = CryptSM4()
            if operation == "encrypt":
                sm4.set_key(key, SM4_ENCRYPT)
                raw = sm4.crypt_ecb(plaintext) if mode == "ECB" else sm4.crypt_cbc(iv or b'\x00'*16, plaintext)
                # gmssl 的 crypt_ecb 会自动做 PKCS7 padding（16B→32B），只取前 block_size 字节
                result = raw[:len(plaintext)]
            else:
                sm4.set_key(key, SM4_DECRYPT)
                raw = sm4.crypt_ecb(plaintext) if mode == "ECB" else sm4.crypt_cbc(iv or b'\x00'*16, plaintext)
                result = raw[:len(plaintext)]

        result_hex = result.hex().upper()

        # 验证
        verification_requested = ciphertext_hex is not None
        verification = "NOT_VERIFIED"
        verification_performed = False
        details = f"{algorithm}-{len(key)*8}-{mode} {operation}: {plaintext_hex[:32]}... → {result_hex[:32]}..."

        if ciphertext_hex:
            verification_performed = True
            expected = ciphertext_hex.replace(" ", "").upper()
            total_bytes = min(len(expected), len(result_hex)) // 2

            if result_hex == expected:
                verification = "MATCH"
                details += f"\n✅ Key verification PASSED — all {total_bytes} bytes match."
            else:
                # 逐字节比对
                matched = []
                mismatched = []
                for i in range(0, total_bytes * 2, 2):
                    byte_idx = i // 2
                    if expected[i:i+2] == result_hex[i:i+2]:
                        matched.append(byte_idx)
                    else:
                        mismatched.append(byte_idx)

                n_matched = len(matched)
                n_mismatched = len(mismatched)

                verification = "MISMATCH"
                details += f"\n❌ Key verification FAILED — {n_mismatched}/{total_bytes} ciphertext bytes differ"

                details += f"\n   Expected:  {expected[:64]}{'...' if len(expected)>64 else ''}"
                details += f"\n   Got:       {result_hex[:64]}{'...' if len(result_hex)>64 else ''}"

                # 关键提示：始终显示，因为密码学扩散效应导致即使密钥只差1字节，密文也会全部不同
                details += f"\n"
                details += f"\n   ⚠️ IMPORTANT: '{n_mismatched} ciphertext bytes differ' does NOT mean "
                details += f"'{n_mismatched} key bytes are wrong'!"
                details += f"\n   In block ciphers (AES/DES/SM4), even 1 wrong KEY byte causes "
                details += f"ALL ciphertext bytes to differ (diffusion property)."
                details += f"\n   The CPA-recovered key may only have 1-3 wrong bytes."
                details += f"\n"
                details += f"\n   → NEXT STEP: Use the 'key_search' tool to search for the correct key."
                details += f"\n     It will automatically try alternative candidates for low-confidence bytes."
                details += f"\n   → If key_search is not available, check each byte's CPA correlation gap:"
                details += f"\n     - gap > 15%: likely CORRECT (keep this byte)"
                details += f"\n     - gap < 15%: likely WRONG (this byte needs correction)"
                details += f"\n   → Do NOT discard the entire key or restart CPA from scratch."
        else:
            details += (
                "\n⚠️ Verification not performed: ciphertext_hex was not provided. "
                "This result only shows raw crypto output, not whether the recovered key is correct."
                "\n→ For CPA key verification, call this tool again with ciphertext_hex so it can return MATCH or MISMATCH."
            )

        return {
            "result_hex": result_hex,
            "verification": verification,
            "verification_requested": verification_requested,
            "verification_performed": verification_performed,
            "details": details
        }

    except Exception as e:
        return {"result_hex": "", "verification": "ERROR", "details": f"Crypto error: {str(e)}"}


# ==================== 测试 ====================

if __name__ == "__main__":
    # AES-128-ECB 测试
    # 已知正确的AES-128测试向量 (FIPS 197 Appendix B)
    print("=== AES-128-ECB Test ===")
    result = crypto_operate(
        plaintext_hex="3243f6a8885a308d313198a2e0370734",
        key_hex="2b7e151628aed2a6abf7158809cf4f3c",
        algorithm="AES",
        mode="ECB",
        operation="encrypt",
        ciphertext_hex="3925841d02dc09fbdc118597196a0b32"  # 期望的密文
    )
    print(f"Result: {result['result_hex']}")
    print(f"Verification: {result['verification']}")
    print(f"Details: {result['details']}")

    # 故意用错密钥测试
    print("\n=== AES-128-ECB Wrong Key Test ===")
    result2 = crypto_operate(
        plaintext_hex="3243f6a8885a308d313198a2e0370734",
        key_hex="0000000000000000000000000000000000",  # 错误密钥
        algorithm="AES",
        mode="ECB",
        operation="encrypt",
        ciphertext_hex="3925841d02dc09fbdc118597196a0b32"
    )
    print(f"Verification: {result2['verification']}")
    print(f"Details: {result2['details']}")
