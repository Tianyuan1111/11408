# -*- coding: utf-8 -*-
import os
import re, sys, os

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

NOISE = re.compile(r"([。！？；：\)）】])\s+([A-Z]{1,6})\s*$")
D = os.path.join(BOOKDIR, '计算机组成原理')

# 直接从文件里取出那 8 行
targets = []
for fn in sorted(os.listdir(D)):
    if not fn.endswith(".md"):
        continue
    for l in open(os.path.join(D, fn), encoding="utf-8").read().split("\n"):
        if NOISE.search(l.rstrip()):
            targets.append((fn, l.rstrip()))

for fn, t in targets:
    m = NOISE.search(t)
    print(f"{fn}")
    print(f"  匹配={bool(m)}  行尾码点={[(c, hex(ord(c))) for c in t[-8:]]}")
    print(f"  文本尾部={t[-40:]!r}")
