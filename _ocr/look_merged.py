# -*- coding: utf-8 -*-
"""列出「选项行粘连下题题号」的全部样例。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '数据结构')
OPT = re.compile(r"^[A-D][.．]\s")
n = 0
for f in sorted(os.listdir(D)):
    if not f.endswith(".md"):
        continue
    ls = open(os.path.join(D, f), encoding="utf-8").read().split("\n")
    in_fence = False
    for i, l in enumerate(ls):
        if l.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if OPT.match(l.strip()) and re.search(r"\d{2}[.、]\s*[\u4e00-\u9fff]", l):
            n += 1
            if n <= 25:
                print(f"[{f[:6]}] L{i}: {l.strip()[:150]}")
print(f"\n合计 {n} 行")
