# -*- coding: utf-8 -*-
"""核对：代码块恢复情况 + xxx.jpg 来源。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "数据结构")
SRC = os.path.join(WORKDIR, "数据结构_Markdown", "王道数据结构.md")

print("=== 清理后：Merge 函数代码块 ===")
t = open(os.path.join(D, "第2章 线性表.md"), encoding="utf-8").read()
ls = t.split("\n")
i = next(k for k, l in enumerate(ls) if "bool Merge(SeqList" in l)
for j in range(max(0, i - 3), min(i + 22, len(ls))):
    print(f"  L{j:>5}| {ls[j]}")

print("\n=== 原文件同一段（对照）===")
t2 = open(SRC, encoding="utf-8").read()
ls2 = t2.split("\n")
i2 = next(k for k, l in enumerate(ls2) if "bool Merge(SeqList" in l)
for j in range(max(0, i2 - 2), min(i2 + 20, len(ls2))):
    print(f"  L{j:>5}| {ls2[j]}")

print("\n=== 清理后仍以选项标记开头、但在代码块内的行（应为 0）===")
n = 0
for f in sorted(os.listdir(D)):
    if not f.endswith(".md"):
        continue
    inf = False
    for l in open(os.path.join(D, f), encoding="utf-8").read().split("\n"):
        if l.strip().startswith("```"):
            inf = not inf
            continue
        if inf and re.match(r"^[A-D][.．]\s", l.strip()):
            n += 1
print(f"  {n} 行")

print("\n=== xxx.jpg 在组成原理原文中的位置 ===")
CO = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
co = open(CO, encoding="utf-8").read().split("\n")
for i, l in enumerate(co):
    if "xxx.jpg" in l:
        for j in range(max(0, i - 4), min(i + 3, len(co))):
            print(f"  L{j:>5}| {co[j][:110]}")
        break
