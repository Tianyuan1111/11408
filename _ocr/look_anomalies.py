# -*- coding: utf-8 -*-
"""查看单-A 异常选项块的上下文，并回溯原始行。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机组成原理")
SRC = open(os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md"),
           encoding="utf-8").read().split("\n")

TARGETS = [
    ("第2章 数据的表示和运算.md", "A. 16"),
    ("第3章 存储系统.md", "A. ⅢI"),
    ("第3章 存储系统.md", "A. 97.9%"),
    ("第6章 总线.md", "A. PCI、CRT、US"),
    ("第6章 总线.md", "A. 可实现外设的即插即用和热拔插"),
]
for fn, key in TARGETS:
    t = open(os.path.join(D, fn), encoding="utf-8").read()
    ls = t.split("\n")
    hit = [i for i, l in enumerate(ls) if l.strip() == key]
    print(f"===== {fn} :: {key!r} =====")
    for i in hit[:1]:
        for j in range(max(0, i - 4), min(i + 8, len(ls))):
            print(f"  L{j}: {ls[j][:110]}")
    print()

print("=== 回溯：原始文件里这些题目的行 ===")
for kw in ["A. 97.9%", "A. ⅢI", "PCI、CRT、US", "A. 16 B."]:
    for i, l in enumerate(SRC):
        if kw in l:
            print(f"  L{i}: {l[:200]!r}")
            break
