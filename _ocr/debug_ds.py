# -*- coding: utf-8 -*-
"""用 Python API 复现数据结构的导出失败，以拿到完整 traceback。"""
import os, sys, traceback, time

os.environ["MINERU_HOME"] = r"E:\dsh_cache\mineru"
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
PDF = os.path.join(BOOKDIR, "27王道《数据结构》高清带书签.pdf")
OUT = os.path.join(WS, "_ocr", "ds_full")

t0 = time.time()
print("阶段 1: parse() ...", flush=True)
try:
    from mineru.parser import parse
    result = parse(PDF, tier="basic")
    print(f"  parse 成功 ({time.time()-t0:.0f}s)", flush=True)
except Exception:
    print("  parse 抛异常:", flush=True)
    traceback.print_exc()
    raise SystemExit(1)

print("阶段 2: save() ...", flush=True)
try:
    from mineru.parser.writer import FileBasedDataWriter
    os.makedirs(OUT, exist_ok=True)
    result.save(FileBasedDataWriter(OUT))
    print(f"  save 成功 ({time.time()-t0:.0f}s)", flush=True)
except Exception:
    print("  save 抛异常:", flush=True)
    traceback.print_exc()
    raise SystemExit(1)

print("全部完成", flush=True)
