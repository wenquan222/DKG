"""
DKG Sources Extractor — raw/ → extracted/*.md

双模运行：
  主模式（主 venv 调用）：orchestrator，派发每份文件到对应转换函数
  worker 模式（ASCII venv 调用）：仅跑 docling 转换一份文件，subprocess 用
    → python extract.py --worker <input> <output>

Pipeline：
  .pdf / .docx / .pptx / .html / .xlsx
        → docling (ASCII venv @ E:/Program Files/dkg_docling_env)
        → PDF 失败 fallback: pdftotext
  .rst / .tex   → pandoc -f {rst|latex} -t gfm
  .py / .m      → 包成 ```language ... ``` 代码块
  .md           → 直接 cp

设计原则：
- 一份源文件产出一份 extracted/<stem>.md（不切分，切分留给 step1）
- 已存在的输出跳过（可中断续跑），加 --force 覆盖
- 失败记到 extract_logs/failures.log，不中断整体

用法：
  python knowledge/sources/extract.py --limit 5              # 试水
  python knowledge/sources/extract.py --only PAP-04 MAN-01   # 指定
  python knowledge/sources/extract.py                        # 全量
  python knowledge/sources/extract.py --force                # 覆盖已有
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Tuple


# ============================================================================
# Paths
# ============================================================================

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
OUT = ROOT / "extracted"
# 失败日志统一走项目顶层 logs/，不再污染 knowledge/sources/
LOG_DIR = ROOT.parent.parent / "logs" / "extract_failures"
FAILURE_LOG = LOG_DIR / "failures.log"

# docling 专用 ASCII venv（避免 docling_parse C++ 读中文路径 venv 的 bug）
DOCLING_PYTHON = Path(os.environ.get("DOCLING_PYTHON", "python"))

# pandoc 用于 .rst / .tex（docling 不支持这两种）
# 先查 PATH，再试已知安装位置
_PANDOC_ABS_CANDIDATES = [
    r"C:/Program Files/Pandoc/pandoc.exe",
]
PANDOC_EXE = (
    shutil.which("pandoc")
    or next((p for p in _PANDOC_ABS_CANDIDATES if Path(p).exists()), "pandoc")
)


# ============================================================================
# Worker mode: 被 subprocess 调用，跑 docling 单份文件转换
# ============================================================================

def worker_main(input_path: str, output_md: str, force_ocr: bool = False):
    """
    运行在 DOCLING_PYTHON 指向的 ASCII venv 里（由主模式 subprocess 调起）。
    只在此函数里 import docling。
    force_ocr: 对扫描版或文本层损坏的 PDF（常见于中文 PDF），强制全页 OCR。
    """
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions

    src = Path(input_path)
    dst = Path(output_md)

    pdf_opts = PdfPipelineOptions()
    pdf_opts.do_table_structure = True
    pdf_opts.do_picture_description = False
    pdf_opts.generate_picture_images = False
    pdf_opts.enable_remote_services = False

    # 启用 OCR，支持中英文；force_ocr=True 时强制全页 OCR（用于扫描版/字体损坏 PDF）
    pdf_opts.do_ocr = True
    pdf_opts.ocr_options = RapidOcrOptions(
        lang=["chinese", "english"],
        force_full_page_ocr=force_ocr,
    )

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_opts)}
    )

    try:
        result = converter.convert(str(src))
        md_text = result.document.export_to_markdown()
    except Exception as e:
        print(f"docling convert failed: {type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)

    header = (
        f"# {src.stem}\n\n"
        f"> Source: `raw/{src.name}`  (engine: docling)\n\n"
    )
    dst.write_text(header + md_text, encoding="utf-8")
    print(f"OK: {len(md_text)} chars -> {dst}", file=sys.stderr)


# ============================================================================
# Main-mode converters
# ============================================================================

def convert_via_docling(src: Path, dst: Path, force_ocr: bool = False) -> Tuple[bool, str]:
    """Dispatch 到 ASCII venv 的 docling。PDF 失败 fallback pdftotext；其他格式失败直接 FAIL。
    force_ocr: 强制全页 OCR（用于中文扫描版/字体损坏 PDF）。"""
    if not DOCLING_PYTHON.exists():
        err = f"docling python missing at {DOCLING_PYTHON}"
        if src.suffix.lower() == ".pdf":
            return _fallback_pdftotext(src, dst, err)
        return False, err

    cmd = [str(DOCLING_PYTHON), str(Path(__file__).resolve()),
           "--worker", str(src), str(dst)]
    if force_ocr:
        cmd.append("--force-ocr")

    try:
        # force_ocr 模式下单份文件可能几小时（大扫描 PDF），超时放到 6h
        timeout_sec = 21600 if force_ocr else 3600
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout_sec)
        if proc.returncode == 0 and dst.exists():
            return True, "docling" + ("+ocr" if force_ocr else "")
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace")[-400:]
        err = f"docling rc={proc.returncode}: ...{stderr}"
    except subprocess.TimeoutExpired:
        err = f"docling timeout (>{timeout_sec//3600}h)"
    except Exception as e:
        err = f"docling subprocess: {type(e).__name__}: {str(e)[:200]}"

    if src.suffix.lower() == ".pdf":
        return _fallback_pdftotext(src, dst, err)
    return False, err


def _fallback_pdftotext(src: Path, dst: Path, prev_err: str) -> Tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(src), "-"],
            capture_output=True, timeout=180,
        )
        if proc.returncode != 0:
            stderr_snippet = (proc.stderr or b"").decode("utf-8", errors="replace")[:200]
            return False, f"{prev_err} || pdftotext rc={proc.returncode}: {stderr_snippet}"
        text = (proc.stdout or b"").decode("utf-8", errors="replace")
        header = f"# {src.stem}\n\n> Note: fallback pdftotext (no images/tables)\n\n"
        dst.write_text(header + text, encoding="utf-8")
        return True, "pdftotext (fallback)"
    except FileNotFoundError:
        return False, f"{prev_err} || pdftotext not installed"
    except Exception as e:
        return False, f"{prev_err} || pdftotext: {type(e).__name__}: {str(e)[:150]}"


def convert_rst_or_tex(src: Path, dst: Path) -> Tuple[bool, str]:
    fmt = "rst" if src.suffix.lower() == ".rst" else "latex"
    try:
        proc = subprocess.run(
            [PANDOC_EXE, "-f", fmt, "-t", "gfm", str(src)],
            capture_output=True, timeout=120,
        )
        if proc.returncode != 0:
            stderr_snippet = (proc.stderr or b"").decode("utf-8", errors="replace")[:200]
            return False, f"pandoc rc={proc.returncode}: {stderr_snippet}"
        text = (proc.stdout or b"").decode("utf-8", errors="replace")
        header = f"# {src.stem}\n\n> Source: `raw/{src.name}`\n\n"
        dst.write_text(header + text, encoding="utf-8")
        return True, f"pandoc-{fmt}"
    except FileNotFoundError:
        return False, "pandoc not installed (run: winget install JohnMacFarlane.Pandoc)"
    except Exception as e:
        return False, f"pandoc: {type(e).__name__}: {str(e)[:150]}"


def convert_code(src: Path, dst: Path) -> Tuple[bool, str]:
    lang_map = {".py": "python", ".m": "matlab"}
    lang = lang_map.get(src.suffix.lower(), "")
    try:
        content = src.read_text(encoding="utf-8", errors="replace")
        wrapped = f"# {src.stem}\n\n> Source: `raw/{src.name}`\n\n```{lang}\n{content}\n```\n"
        dst.write_text(wrapped, encoding="utf-8")
        return True, "code-fence"
    except Exception as e:
        return False, f"code-fence: {type(e).__name__}: {str(e)[:150]}"


def convert_md(src: Path, dst: Path) -> Tuple[bool, str]:
    try:
        shutil.copy2(src, dst)
        return True, "cp"
    except Exception as e:
        return False, f"cp: {type(e).__name__}: {str(e)[:150]}"


def dispatch(src: Path, dst: Path, force_ocr: bool = False) -> Tuple[bool, str]:
    ext = src.suffix.lower()
    if ext == ".md":
        return convert_md(src, dst)
    if ext in {".py", ".m"}:
        return convert_code(src, dst)
    if ext in {".rst", ".tex"}:
        return convert_rst_or_tex(src, dst)
    if ext in {".pdf", ".docx", ".pptx", ".html", ".xlsx"}:
        return convert_via_docling(src, dst, force_ocr=force_ocr)
    return False, f"unsupported extension: {ext}"


# ============================================================================
# Main mode
# ============================================================================

def main_mode(args):
    force_ocr = getattr(args, "force_ocr", False)
    OUT.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    files = sorted(f for f in RAW.iterdir() if f.is_file())
    if args.only:
        filter_set = set(args.only)
        files = [f for f in files if f.stem in filter_set or f.name in filter_set]
    if args.limit:
        files = files[: args.limit]

    n = len(files)
    print("=== DKG Extract ===")
    print(f"Input:   {RAW}  ({n} files)")
    print(f"Output:  {OUT}")
    print(f"Engine:  docling ({DOCLING_PYTHON})")
    print()

    success = skipped = failed = 0
    failures = []

    for i, f in enumerate(files, 1):
        dst_name = f.name if f.suffix.lower() == ".md" else (f.stem + ".md")
        dst = OUT / dst_name

        if dst.exists() and not args.force:
            skipped += 1
            print(f"[{i:3d}/{n}] SKIP  {f.name}  (exists)")
            continue

        t0 = time.time()
        try:
            ok, detail = dispatch(f, dst, force_ocr=force_ocr)
        except Exception as e:
            ok, detail = False, f"unexpected: {type(e).__name__}: {str(e)[:200]}"
        elapsed = time.time() - t0

        if ok:
            success += 1
            print(f"[{i:3d}/{n}] OK    {f.name}  ({detail}, {elapsed:.1f}s)")
        else:
            failed += 1
            failures.append((f.name, detail))
            print(f"[{i:3d}/{n}] FAIL  {f.name}  ({detail})")
            try:
                dst.unlink(missing_ok=True)
            except Exception:
                pass

    if failures:
        with FAILURE_LOG.open("a", encoding="utf-8") as fp:
            fp.write(f"\n=== run at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            for name, detail in failures:
                fp.write(f"{name}\t{detail}\n")

    print()
    print("=== Summary ===")
    print(f"Total:    {n}")
    print(f"Success:  {success}")
    print(f"Skipped:  {skipped}")
    print(f"Failed:   {failed}")
    if failures:
        print(f"Failure details: {FAILURE_LOG}")


# ============================================================================
# Entry
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="DKG raw/ → extracted/*.md")
    parser.add_argument("--worker", nargs=2, metavar=("IN", "OUT"),
                        help="内部使用：worker 模式跑 docling 单份文件")
    parser.add_argument("--force", action="store_true", help="覆盖已有输出")
    parser.add_argument("--only", nargs="+", help="只处理指定文件（stem 或全名）")
    parser.add_argument("--limit", type=int, help="只处理前 N 个")
    parser.add_argument("--force-ocr", action="store_true",
                        help="docling 强制全页 OCR（中文扫描版/字体损坏 PDF 需要，慢）")
    args = parser.parse_args()

    if args.worker:
        worker_main(args.worker[0], args.worker[1], force_ocr=args.force_ocr)
    else:
        main_mode(args)


if __name__ == "__main__":
    main()
