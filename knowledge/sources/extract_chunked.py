"""
分块 OCR 超大 PDF（解决 docling OCR 内存累积 OOM 问题）

用 pymupdf 把一份大 PDF 按页数切分，对每块单独送 docling OCR（独立 subprocess），
每块完成后合并输出 md，块间模型完全释放，避免内存泄漏累积。

用法：
  python extract_chunked.py <INPUT_PDF> <OUTPUT_MD> [--chunk-pages 200]

在主 venv 里跑（需要 pymupdf + subprocess 调 docling worker）。
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCLING_PYTHON = Path(os.environ.get("DOCLING_PYTHON", "python"))
EXTRACT_PY = ROOT / "extract.py"


def split_pdf(src_pdf: Path, out_dir: Path, chunk_pages: int) -> list[Path]:
    """用 pymupdf 按 chunk_pages 切分 PDF，返回分块 PDF 路径列表。"""
    import pymupdf
    doc = pymupdf.open(str(src_pdf))
    total = len(doc)
    chunks = []
    for i in range(0, total, chunk_pages):
        start = i
        end = min(i + chunk_pages, total)
        out_path = out_dir / f"chunk_{start:04d}-{end-1:04d}.pdf"
        new_doc = pymupdf.open()
        new_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
        new_doc.save(str(out_path))
        new_doc.close()
        chunks.append(out_path)
        print(f"  chunk {len(chunks)}: pages {start+1}..{end} -> {out_path.name}", flush=True)
    doc.close()
    return chunks


def run_docling_on_chunk(chunk_pdf: Path, out_md: Path, force_ocr: bool = True) -> bool:
    """调 extract.py --worker 跑一块。"""
    cmd = [str(DOCLING_PYTHON), str(EXTRACT_PY),
           "--worker", str(chunk_pdf), str(out_md)]
    if force_ocr:
        cmd.append("--force-ocr")
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=7200)
        if proc.returncode == 0 and out_md.exists():
            return True
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace")[-500:]
        print(f"  docling rc={proc.returncode}: ...{stderr}", flush=True)
        return False
    except subprocess.TimeoutExpired:
        print(f"  chunk timeout (>2h)", flush=True)
        return False
    except Exception as e:
        print(f"  chunk error: {type(e).__name__}: {e}", flush=True)
        return False


def merge_markdown(chunk_mds: list[Path], final_md: Path, src_name: str):
    """合并各块 md：保留原 header，拼接内容。"""
    header = (
        f"# {Path(src_name).stem}\n\n"
        f"> Source: `raw/{src_name}`  (engine: docling chunked OCR)\n\n"
    )
    parts = [header]
    for i, md_path in enumerate(chunk_mds, 1):
        content = md_path.read_text(encoding="utf-8")
        # 去掉每块自己的 header（第一个 "# " 标题 + 下一行 Source 行 + 空行）
        lines = content.splitlines()
        # header 通常占 3-4 行；找第一个非 header 的段落起点
        skip = 0
        for j, L in enumerate(lines):
            if j == 0 and L.startswith("# "):
                skip = j + 1
                continue
            if L.startswith("> Source:"):
                skip = j + 1
                continue
            if L.strip() == "" and skip == j:
                skip = j + 1
                continue
            break
        body = "\n".join(lines[skip:])
        parts.append(f"<!-- chunk {i}: {md_path.name} -->\n\n{body}\n")
    final_md.write_text("\n".join(parts), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="分块 OCR 大 PDF")
    parser.add_argument("input_pdf")
    parser.add_argument("output_md")
    parser.add_argument("--chunk-pages", type=int, default=200,
                        help="每块页数（默认 200）")
    args = parser.parse_args()

    src = Path(args.input_pdf)
    dst = Path(args.output_md)

    # 用户 temp 路径（ASCII，避免中文）
    work_dir = Path(tempfile.mkdtemp(prefix="dkg_chunk_"))
    print(f"work_dir: {work_dir}", flush=True)

    try:
        # Step 1: split
        print(f"splitting {src.name} ({Path(src).stat().st_size/1024/1024:.1f}MB)...", flush=True)
        chunk_pdfs = split_pdf(src, work_dir, args.chunk_pages)
        print(f"split into {len(chunk_pdfs)} chunks", flush=True)

        # Step 2: OCR each chunk, 允许部分失败（记 log 继续）
        chunk_mds = []
        failed_chunks = []
        for i, c in enumerate(chunk_pdfs, 1):
            t0 = time.time()
            md_path = work_dir / f"{c.stem}.md"
            print(f"[{i}/{len(chunk_pdfs)}] OCR chunk {c.name}...", flush=True)
            ok = run_docling_on_chunk(c, md_path, force_ocr=True)
            elapsed = time.time() - t0
            if ok:
                size = md_path.stat().st_size
                print(f"  OK ({elapsed:.0f}s, {size} bytes)", flush=True)
                chunk_mds.append(md_path)
            else:
                print(f"  FAIL ({elapsed:.0f}s) — 跳过，继续下一块", flush=True)
                failed_chunks.append(c.name)

        # Step 3: merge whatever succeeded
        if not chunk_mds:
            print("所有块都失败，放弃", flush=True)
            return 1
        print(f"merging {len(chunk_mds)} mds into {dst.name}  (failed: {len(failed_chunks)})...", flush=True)
        merge_markdown(chunk_mds, dst, src.name)
        if failed_chunks:
            # 在 md 末尾追加失败记录
            with dst.open("a", encoding="utf-8") as f:
                f.write(f"\n\n<!-- FAILED CHUNKS: {', '.join(failed_chunks)} -->\n")
        print(f"done: {dst}  ({dst.stat().st_size} bytes, {len(failed_chunks)} chunks failed)", flush=True)
        # 不 cleanup work_dir 若有失败（方便调试）
        if failed_chunks:
            print(f"work_dir kept for debugging: {work_dir}", flush=True)
            return 0
    finally:
        if not (locals().get('failed_chunks') or []):
            shutil.rmtree(work_dir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
