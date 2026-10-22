# -*- coding: utf-8 -*-
"""检查选项标记使用顿号(、)的情况，判断是否应把它从分隔符中移除。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SRC = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
lines = open(SRC, encoding="utf-8").read().split("\n")

dot = re.compile(r"(?<![A-Za-z0-9])([A-D])[.．]\s*")
dun = re.compile(r"(?<![A-Za-z0-9])([A-D])、\s*")

n_dot = sum(len(dot.findall(l)) for l in lines)
n_dun = sum(len(dun.findall(l)) for l in lines)
print(f"以「字母.」作标记: {n_dot} 处")
print(f"以「字母、」作标记: {n_dun} 处")

print("\n=== 顿号标记的全部出现位置 ===")
for i, l in enumerate(lines):
    for m in dun.finditer(l):
        if m.group(1) in "ABCD":
            print(f"  L{i} [{m.group(1)}、]: …{l[max(0,m.start()-40):m.start()+45]}…")

print("\n=== 顿号标记是否总是伴随点号标记出现（后者才是真正的选项）===")
both = sum(1 for l in lines if dun.search(l) and dot.search(l))
print(f"  同行同时含两种标记的行: {both}")
