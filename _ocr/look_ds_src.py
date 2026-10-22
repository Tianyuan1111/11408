# -*- coding: utf-8 -*-
import os
import sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")
SRC = os.path.join(WORKDIR, '数据结构_Markdown', '王道数据结构.md')
lines = open(SRC, encoding="utf-8").read().split("\n")

for lo, hi, tag in [(250, 300, "目录起始附近"), (480, 530, "缺失标题 502 附近"),
                    (1330, 1370, "第1章 H1 附近")]:
    print(f"===== {tag}  (L{lo}-L{hi}) =====")
    for i in range(lo, min(hi, len(lines))):
        s = lines[i]
        if s.strip():
            print(f"{i:>5}| {s[:120]}")
    print()
