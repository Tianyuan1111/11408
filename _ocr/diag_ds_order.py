# -*- coding: utf-8 -*-
"""理清数据结构 markdown 的真实文档顺序：H1 与页标记的先后关系；是否重复。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SRC = os.path.join(WORKDIR, "数据结构_Markdown", "王道数据结构.md")
lines = open(SRC, encoding="utf-8").read().split("\n")
PAGE = re.compile(r"<!-- page (\d+) of (\d+) -->")

print("=== 全部页标记的头尾（顺序）===")
marks = [(i, int(PAGE.match(l.strip()).group(1))) for i, l in enumerate(lines) if PAGE.match(l.strip())]
print(f"共 {len(marks)} 个；前 20 个:")
for i, p in marks[:20]:
    print(f"  L{i:>6} page {p}")
print("  ...")
# 找出页码不递增的位置
bad = [(marks[k], marks[k + 1]) for k in range(len(marks) - 1) if marks[k + 1][1] != marks[k][1] + 1]
print(f"\n页码不连续处: {len(bad)}")
for a, b in bad[:20]:
    print(f"  L{a[0]} page{a[1]}  ->  L{b[0]} page{b[1]}")

print("\n=== 全部 H1 及其之前最近的页标记 ===")
cur = None
for i, l in enumerate(lines):
    m = PAGE.match(l.strip())
    if m:
        cur = int(m.group(1))
    if re.match(r"^# ", l):
        print(f"  L{i:>6}  (前页标记 page {cur})  {l.strip()[2:]}")

print("\n=== 是否重复：第1章独有句子的出现次数 ===")
for probe in ["数据是信息的载体，是描述客观事物属性的数",
              "算法的时间复杂度和空间复杂度",
              "抽象数据类型（ADT)",
              "线性表的定义和基本操作"]:
    idxs = [i for i, l in enumerate(lines) if probe in l]
    print(f"  {probe[:24]!r}: {len(idxs)} 次 -> {idxs[:6]}")
