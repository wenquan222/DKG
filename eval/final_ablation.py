"""Final ablation results for the TDSC paper (Base / Tools / Knowledge / DKG).

Inputs: a log root with one folder per configuration.
  - Full run set (80 runs per configuration, used for the paper):
      <root>/{6-Base,5-Tools,7-Knowledge,1-DKG-DeepSeek-V3.2}/<session>/
  - Public sample in this repository (3 runs per case, set DKG_LOG_LAYOUT=artifact):
      logs/{base,tools,knowledge,dkg_deepseek}/<case>/<session>/
    Totals computed on the sample will differ from the paper; the complete
    per-run verdicts are in results/final_ablation_per_run.csv.

Success rule
  - Tools, DKG: robust evaluator re_evaluate_qwen_sessions.evaluate_session,
    unchanged from the existing paper numbers.
  - Base, Knowledge: manual review on 2026-11-05. A run counts only if the full
    key was computed by CPA code on the traces and printed (per-byte table with
    correlations). Runs that filled bytes from a key pattern, took the key from
    the graph's vendor example, or printed the SM4 test vector do not count.
    MANUAL lists every run whose verdict differs from the robust evaluator.

Efficiency: metrics.parse_session (rounds, tokens_total, duration_sec), averaged
per case over all 10 runs, as in the existing paper table.

Outputs: results/final_ablation_{per_run,by_case,by_config}.csv
         (results/sample_final_ablation_*.csv when DKG_LOG_LAYOUT=artifact)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
from re_evaluate_qwen_sessions import evaluate_session  # noqa: E402
from metrics import parse_session  # noqa: E402

import os
ARTIFACT = os.environ.get("DKG_LOG_LAYOUT") == "artifact"
BASE = Path(os.environ.get("DKG_LOG_ROOT", ROOT / "logs"))
OUT = ROOT / "results"
TAG = "sample_" if ARTIFACT else ""
CONFIGS = [("Base", "base"), ("Tools", "tools"),
           ("Knowledge", "knowledge"), ("DKG", "dkg_deepseek")] if ARTIFACT else [("Base", "6-Base"), ("Tools", "5-Tools"),
           ("Knowledge", "7-Knowledge"), ("DKG", "1-DKG-DeepSeek-V3.2")]
MANUAL_CONFIGS = {"Base", "Knowledge"}
CASES = ["AES-7816", "AES-14443", "AES-FPGA", "AES-STM32F103",
         "AES-STM32F429", "DES-7816", "DES-14443", "SM4-7816"]

# (config, session timestamp suffix) -> (verdict, reason)
MANUAL = {
    # Base, counted: full per-byte CPA table computed from traces
    ("Base", "20260508_150013_408"): (1, "round 11 per-byte CPA table, 16/16 bytes correct"),
    ("Base", "20260509_053631_202"): (1, "round 15 per-byte CPA table, 16/16 bytes correct"),
    ("Base", "20260509_075135_391"): (1, "round 12 per-byte CPA table, 16/16 bytes correct"),
    ("Base", "20260508_211127_810"): (1, "round 7 per-byte CPA table, 16/16 bytes correct"),
    ("Base", "20260508_151502_783"): (1, "round 7 per-byte CPA table, 16/16 bytes correct"),
    ("Base", "20260508_212424_610"): (1, "round 6 per-byte CPA table, 16/16 bytes correct"),
    ("Base", "20261104_175915_061"): (1, "round 7 per-byte CPA table, 16/16 bytes correct"),
    ("Base", "20261104_205423_856"): (1, "round 7 per-byte CPA table, 16/16 bytes correct"),
    # Base, not counted
    ("Base", "20261104_201859_089"): (0, "byte 12 filled as 0xcc from the incrementing key pattern"),
    ("Base", "20261104_171821_426"): (0, "DES master key taken from a common-key pattern match"),
    ("Base", "20261104_205055_046"): (0, "only the SM4 test vector printed; master key not derived"),
    # Knowledge, not counted
    ("Knowledge", "20260515_164657_694"): (0, "key guessed from the STM32F429 vendor example"),
    ("Knowledge", "20261104_145658_104"): (0, "CPA 15/16; byte 5 set to 0x55 by hand"),
    ("Knowledge", "20261104_191818_615"): (0, "CPA 13/16; remaining bytes filled from the key pattern"),
    ("Knowledge", "20261104_202834_922"): (0, "key taken from the STM32F429 example in the graph"),
    ("Knowledge", "20260515_013523_205"): (0, "only the first SM4 round key recovered; master key is the test vector"),
}


def suffix(name: str) -> str:
    parts = name.split("_")
    return "_".join(parts[-3:])


def main() -> None:
    rows = []
    for label, folder in CONFIGS:
        cfg_dir = BASE / folder
        sessions = [x for c in sorted(cfg_dir.iterdir()) if c.is_dir() for x in sorted(c.iterdir())] if ARTIFACT else sorted(cfg_dir.iterdir())
        for s in sessions:
            if not s.is_dir():
                continue
            v = evaluate_session(s)
            ok = int(bool(v.get("success")))
            reason = v.get("reason", "")
            key = (label, suffix(s.name))
            if label in MANUAL_CONFIGS and key in MANUAL:
                ok, reason = MANUAL[key][0], "manual: " + MANUAL[key][1]
            m = parse_session(str(s)) or {}
            rows.append({
                "config": label, "case": s.name.split("_")[0], "session_dir": s.name,
                "success": ok, "reason": reason,
                "rounds": m.get("rounds", 0), "tokens_total": m.get("tokens_total", 0),
                "duration_sec": round(m.get("duration_sec", 0.0), 1),
            })
    missing = [k for k in MANUAL if not any(r["config"] == k[0] and suffix(r["session_dir"]) == k[1] for r in rows)]
    if missing and not ARTIFACT:
        sys.exit(f"MANUAL entries not found: {missing}")

    OUT.mkdir(exist_ok=True)
    fields = ["config", "case", "session_dir", "success", "reason", "rounds", "tokens_total", "duration_sec"]
    with open(OUT / f"{TAG}final_ablation_per_run.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

    def agg(sel):
        n = len(sel)
        return {"n": n, "ok": sum(r["success"] for r in sel),
                "SR": round(sum(r["success"] for r in sel) / n * 100, 1),
                "avg_rounds": round(sum(r["rounds"] for r in sel) / n, 1),
                "avg_tokens": round(sum(r["tokens_total"] for r in sel) / n),
                "avg_duration_sec": round(sum(r["duration_sec"] for r in sel) / n)}

    by_case, by_cfg = [], []
    for label, _ in CONFIGS:
        cr = [r for r in rows if r["config"] == label]
        for c in CASES:
            by_case.append({"config": label, "case": c, **agg([r for r in cr if r["case"] == c])})
        by_cfg.append({"config": label, **agg(cr)})
    for name, data in (("by_case", by_case), ("by_config", by_cfg)):
        with open(OUT / f"{TAG}final_ablation_{name}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)

    for r in by_cfg:
        print(f"{r['config']:<10} {r['ok']:>2}/{r['n']}  SR={r['SR']:5.1f}%  R={r['avg_rounds']:5.1f}  "
              f"Tok={r['avg_tokens']/1000:4.0f}K  T={r['avg_duration_sec']:5.0f}s")


if __name__ == "__main__":
    main()
