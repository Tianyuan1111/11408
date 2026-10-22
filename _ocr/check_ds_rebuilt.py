# -*- coding: utf-8 -*-
"""确认重建后第1章正文与 H1 的先后关系。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")
SRC = os.path.join(WORKDIR, '数据结构_Markdown', '王道数据结构.md')
lines = open(SRC, encoding="utf-8").read().split("\n")
PAGE = re.compile(r"<!-- page (\d+) of (\d+) -->")

h1 = [(i, l.strip()[2:]) for i, l in enumerate(lines) if re.match(r"^# ", l)]
print("H1 位置:")
for i, t in h1:
    print(f"  L{i:>6}  {t}")

probe = "数据是信息的载体"
pi = [i for i, l in enumerate(lines) if probe in l]
print(f"\n第1章正文句「{probe}」位置: {pi}")
print(f"# 第1章 绪论 位置: {[i for i,t in h1 if t.startswith('第1章')]}")
print(f"  正文在 H1 之后? {pi and pi[0] > [i for i,t in h1 if t.startswith('第1章')][0]}")

print("\n=== 第1章 H1 前后 20 行 ===")
k = [i for i, t in h1 if t.startswith("第1章")][0]
for j in range(max(0, k - 6), min(k + 20, len(lines))):
    if lines[j].strip():
        print(f"L{j:>6}| {lines[j][:110]}")

print("\n=== 页标记连续性 ===")
marks = [(i, int(PAGE.match(l.strip()).group(1))) for i, l in enumerate(lines) if PAGE.match(l.strip())]
print(f"  共 {len(marks)}，范围 {marks[0][1]}-{marks[-1][1]}，严格递增={all(b[1]>a[1] for a,b in zip(marks,marks[1:]))}")
bad = [(a, b) for a, b in zip(marks, marks[1:]) if b[1] != a[1] + 1]
print(f"  页码不连续处: {len(bad)}")
