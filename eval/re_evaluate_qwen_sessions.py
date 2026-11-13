"""
Robust re-evaluator for Qwen Round 1 + Round 2 sessions.

The original metrics.py used 3-fallback hex extraction (correct_key /
verify-MATCH-near-key_hex / recovered_key) — but Qwen often does its
own DES master-key derivation in python_jupyter, declaring success in
the final narrative WITHOUT triggering any of those structural patterns.

This re-evaluator scans the LAST 8000 chars of agent_log.md (the final
summary section), finds every plausible master-key hex string (16 chars
for DES, 32 chars for AES/SM4), and checks whether any of them matches
the case's ground truth (or DES parity-equivalent variant) AND has a
success-indicating context (verified / matched / 验证 / 通过 / ✓ / 成功 / PASSED).
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics import GROUND_TRUTH_KEYS, DES_KEY_EQUIVALENTS, _normalize_hex

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


SUCCESS_KEYWORDS = [
    "verified", "validated", "matched", "match", "MATCH", "PASSED",
    "100/100", "100%", "✓", "成功", "通过", "验证", "正确", "恢复",
    "successfully", "success", "Success", "SUCCESS",
]


def all_acceptable_keys(case: str) -> set[str]:
    """ground-truth + DES parity-equivalent variants, all normalized."""
    acceptable = set()
    gt = GROUND_TRUTH_KEYS.get(case)
    if gt:
        acceptable.add(_normalize_hex(gt))
    for v in DES_KEY_EQUIVALENTS.get(case, []):
        acceptable.add(_normalize_hex(v))
    return acceptable


def _des_parity_signature(hex_str: str) -> str:
    """For DES, return the upper-7-bit signature of each byte (LSB masked).
    Two DES keys are parity-equivalent iff their signatures match."""
    h = _normalize_hex(hex_str)
    if len(h) != 16:
        return ""
    sig = []
    for i in range(8):
        byte = int(h[i*2:i*2+2], 16)
        sig.append(f"{byte & 0xFE:02X}")  # mask LSB
    return "".join(sig)


def is_match_with_des_parity(candidate: str, case: str) -> bool:
    """For DES: match by parity signature; for AES/SM4: match exact normalized."""
    cand_n = _normalize_hex(candidate)
    if not case.startswith("DES"):
        # exact match (AES / SM4)
        return cand_n in all_acceptable_keys(case)
    # DES: try parity signature
    cand_sig = _des_parity_signature(cand_n)
    if not cand_sig:
        return False
    for ok in all_acceptable_keys(case):
        if _des_parity_signature(ok) == cand_sig:
            return True
    return False


def evaluate_session(session_dir: Path) -> dict:
    """Return dict with { case, success, recovered_keys, verdict_reason }."""
    case = session_dir.name.split("_")[0]
    al = session_dir / "agent_log.md"
    if not al.exists():
        return {"case": case, "success": False, "reason": "no agent_log.md"}

    txt = al.read_text(encoding="utf-8", errors="ignore")

    acceptable = all_acceptable_keys(case)
    if not acceptable:
        return {"case": case, "success": False, "reason": f"no GT for case {case}"}

    # Required key length per case
    if case.startswith("DES"):
        key_len = 16  # 8 bytes = 16 hex chars
    elif case.startswith("AES") or case.startswith("SM4"):
        key_len = 32  # 16 bytes = 32 hex chars
    else:
        return {"case": case, "success": False, "reason": f"unknown algorithm for case {case}"}

    # Look in the LAST 8000 chars (final summary section, agent's own conclusion)
    tail = txt[-8000:] if len(txt) > 8000 else txt

    # Also look at any "verification": "MATCH" tool result occurrences
    # (regardless of position) — these are unambiguous tool-level success
    structured_matches = list(re.finditer(r'"verification":\s*"MATCH"', txt))
    for m in structured_matches:
        # find the key_hex back-tracking up to 3000 chars
        lookback = txt[max(0, m.start() - 3000):m.start()]
        for kh in re.finditer(r'"key_hex":\s*"([0-9A-Fa-f]+)"', lookback):
            if is_match_with_des_parity(kh.group(1), case):
                return {
                    "case": case,
                    "success": True,
                    "reason": f"tool verification:MATCH on key={kh.group(1)}",
                    "matched_key": kh.group(1),
                }

    # Also check key_search "found": true with master_key
    for m in re.finditer(r'"found":\s*true.*?"(?:master_key|recovered_key|correct_key)":\s*"([0-9A-Fa-f]+)"', txt, re.DOTALL):
        if is_match_with_des_parity(m.group(1), case):
            return {
                "case": case,
                "success": True,
                "reason": f"key_search found=true with key={m.group(1)}",
                "matched_key": m.group(1),
            }

    # Now scan the final tail for hex strings of correct length
    hex_pattern = re.compile(r'\b([0-9A-Fa-f]{' + str(key_len) + r'})\b')
    candidates = []
    for m in hex_pattern.finditer(tail):
        candidate = m.group(1)
        if not is_match_with_des_parity(candidate, case):
            continue
        # check if there's a success keyword within 400 chars before/after
        ctx_start = max(0, m.start() - 400)
        ctx_end = min(len(tail), m.end() + 400)
        context = tail[ctx_start:ctx_end]
        for kw in SUCCESS_KEYWORDS:
            if kw in context:
                candidates.append((candidate, kw))
                break

    if candidates:
        return {
            "case": case,
            "success": True,
            "reason": f"narrative hex match: {candidates[0][0]} near keyword '{candidates[0][1]}'",
            "matched_key": candidates[0][0],
        }

    return {"case": case, "success": False, "reason": "no recovered key matches GT in narrative"}


def evaluate_dir(log_dir: Path, label: str) -> None:
    print(f"\n{'='*70}")
    print(f"{label}: {log_dir}")
    print(f"{'='*70}")

    results = {}
    for d in sorted(log_dir.iterdir()):
        if not d.is_dir():
            continue
        if "DKG_" not in d.name and "NoKG_" not in d.name:
            continue
        r = evaluate_session(d)
        r["session_dir"] = d.name
        case = r["case"]
        results.setdefault(case, []).append(r)

    print(f"{'Case':<14} {'n':>3} {'OK':>3} {'SR':>7}")
    print("-" * 32)
    total_ok = total_n = 0
    for case in sorted(results):
        lst = results[case]
        ok = sum(1 for r in lst if r["success"])
        n = len(lst)
        total_ok += ok
        total_n += n
        sr = ok / n * 100 if n else 0
        print(f"{case:<14} {n:>3} {ok:>3} {sr:>6.1f}%")
    print("-" * 32)
    sr = total_ok / total_n * 100 if total_n else 0
    print(f"{'TOTAL':<14} {total_n:>3} {total_ok:>3} {sr:>6.1f}%")

    return results


def write_csvs(out_dir: Path, datasets: list[tuple[str, dict]]) -> None:
    """Persist per-run + by-case + by-model summaries as CSV/JSON.

    datasets: list of (label, results_dict) where results_dict[case] = list of session verdicts.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) per-run: every session row with verdict
    per_run_path = out_dir / "exp3_robust_per_run.csv"
    with per_run_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model_label", "case", "session_dir", "success", "reason", "matched_key"])
        for label, results in datasets:
            for case in sorted(results):
                for r in results[case]:
                    w.writerow([
                        label, case, r.get("session_dir", ""),
                        int(bool(r.get("success", False))),
                        r.get("reason", ""), r.get("matched_key", ""),
                    ])

    # 2) by-case: model × case × n × ok × SR
    by_case_path = out_dir / "exp3_robust_by_model_case.csv"
    with by_case_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model_label", "case", "n", "ok", "SR"])
        for label, results in datasets:
            for case in sorted(results):
                lst = results[case]
                ok = sum(1 for r in lst if r["success"])
                n = len(lst)
                sr = round(ok / n * 100, 1) if n else 0.0
                w.writerow([label, case, n, ok, sr])

    # 3) by-model: aggregate per model
    by_model_path = out_dir / "exp3_robust_by_model.csv"
    with by_model_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model_label", "n", "ok", "SR"])
        for label, results in datasets:
            total_ok = sum(1 for case in results for r in results[case] if r["success"])
            total_n = sum(len(results[case]) for case in results)
            sr = round(total_ok / total_n * 100, 1) if total_n else 0.0
            w.writerow([label, total_n, total_ok, sr])

    # 4) JSON dump (preserves structure for downstream analysis)
    json_path = out_dir / "exp3_robust_per_run.json"
    json_dump = {
        label: {case: results[case] for case in sorted(results)}
        for label, results in datasets
    }
    json_path.write_text(json.dumps(json_dump, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nWrote:")
    print(f"  {per_run_path}")
    print(f"  {by_case_path}")
    print(f"  {by_model_path}")
    print(f"  {json_path}")


def main():
    root = Path(__file__).resolve().parents[1]

    # === Round 1 multi-model (3 backbones × 80 = 240 runs) ===
    r1_root = root / "logs" / "论文最终结果-TDSC"

    print("\n" + "#"*70)
    print("# ROUND 1 — re-evaluating all 3 backbones with robust evaluator")
    print("#"*70)

    ds_results = evaluate_dir(r1_root / "1-DKG-DeepSeek-V3.2", "DSv3.2 (R1)")
    glm_results = evaluate_dir(r1_root / "2-DKG-GLM-5", "GLM-5 (R1)")
    qwen_results = evaluate_dir(r1_root / "3-DKG-Qwen3.5", "Qwen3.5-397B (R1)")

    # Round 2: Qwen rerun (3-case). After the user merged the R2 weak-case
    # sessions into the R1 main dir, this dir is removed. Skip gracefully.
    r2_dir = root / "logs" / "exp3_qwen_round2_rerun"
    qwen_r2_results = {}
    if r2_dir.exists():
        qwen_r2_results = evaluate_dir(r2_dir, "Qwen3.5-397B (R2 after patches+fusion)")
    else:
        print(f"\n[SKIP] R2 standalone dir removed (sessions merged into R1 main dir): {r2_dir}")

    # No-KG baseline (DSv3.2 × 80 runs)
    nokg_dir = root / "logs" / "论文最终结果-TDSC" / "5-Tools"
    nokg_results = {}
    if nokg_dir.exists():
        nokg_results = evaluate_dir(nokg_dir, "No-KG baseline (DSv3.2 × 80)")

    if qwen_r2_results:
        r1_results = qwen_results  # for downstream summary
        r2_results = qwen_r2_results
        print("\n" + "="*70)
        print("SUMMARY: Round 1 vs Round 2 (Qwen, 3 cases of interest)")
        print("="*70)
        for case in ["DES-14443", "DES-7816", "SM4-7816"]:
            r1 = r1_results.get(case, [])
            r2 = r2_results.get(case, [])
            r1_ok = sum(1 for r in r1 if r["success"])
            r2_ok = sum(1 for r in r2 if r["success"])
            r1_n = len(r1)
            r2_n = len(r2)
            r1_sr = r1_ok / r1_n * 100 if r1_n else 0
            r2_sr = r2_ok / r2_n * 100 if r2_n else 0
            delta = r2_sr - r1_sr
            sign = "+" if delta >= 0 else ""
            print(f"  {case:<12}  R1: {r1_ok}/{r1_n} = {r1_sr:.1f}%   R2: {r2_ok}/{r2_n} = {r2_sr:.1f}%   Δ {sign}{delta:.1f}pp")

    out_dir = root / "eval" / "results"
    datasets = [
        ("DSv3.2_R1", ds_results),
        ("GLM-5_R1", glm_results),
        ("Qwen3.5-397B_R1", qwen_results),
    ]
    if qwen_r2_results:
        datasets.append(("Qwen3.5-397B_R2", qwen_r2_results))
    datasets.append(("NoKG_DSv3.2", nokg_results))
    write_csvs(out_dir, datasets)


if __name__ == "__main__":
    main()
