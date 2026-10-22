# -*- coding: utf-8 -*-
"""依次解析三本书（用 Python 编排，避免 PowerShell 5.1 的脚本编码坑）。"""
import os, sys, time, subprocess

sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
MINERU_KIT = r"E:\Python313\Scripts\mineru-kit.exe"

ENV = dict(os.environ)
ENV["MINERU_HOME"] = r"E:\dsh_cache\mineru"
ENV["PYTHONIOENCODING"] = "utf-8"
ENV["PYTHONUTF8"] = "1"

BOOKS = [
    ("数据结构",     os.path.join(BOOKDIR, "27王道《数据结构》高清带书签.pdf"),     "_ocr/ds_full"),
    ("计算机组成原理", os.path.join(BOOKDIR, "27王道《计算机组成原理》高清带书签.pdf"), "_ocr/co_full"),
    ("计算机网络",   os.path.join(BOOKDIR, "27王道《计算机网络》高清带书签.pdf"),   "_ocr/cn_full"),
]

KEEP = ("INFO", "ERROR", "已解析", "page/s", "Traceback", "错误")

for name, fn, out in BOOKS:
    t0 = time.time()
    print(f"================ START {name} ================", flush=True)
    cmd = [MINERU_KIT, "parse", os.path.join(WS, fn), "-o", os.path.join(WS, out),
           "--pages", "all", "--tier", "basic", "-f", "zip"]
    r = subprocess.run(cmd, env=ENV, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    dt = time.time() - t0
    print(f"exit={r.returncode}  elapsed={dt:.0f}s ({dt/60:.1f} min)", flush=True)
    for line in (r.stderr or "").splitlines():
        if any(k in line for k in KEEP):
            print("   " + line[-160:], flush=True)
    for line in (r.stdout or "").splitlines()[-5:]:
        print("   " + line[-160:], flush=True)
    print(f"================ DONE {name} ================\n", flush=True)

print("ALL BOOKS PARSED", flush=True)
