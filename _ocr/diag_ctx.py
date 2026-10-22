# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
lines = open(os.path.join(WS, "_ocr", "os_full_x", "markdown.md"), encoding="utf-8").read().split("\n")

for key in ["2.1 进程与线程简介", "3.1 ", "4.1 ", "5.1 "]:
    hits = [i for i, ln in enumerate(lines) if key in ln and ln.strip().startswith("#")]
    print(f"===== 「{key}」 标题行: {hits[:5]} =====")
    if hits:
        s = max(0, hits[0] - 22)
        for i in range(s, min(hits[0] + 3, len(lines))):
            print(f"L{i:>6}: {lines[i][:130]}")
    print()
