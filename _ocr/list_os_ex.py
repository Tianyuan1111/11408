# -*- coding: utf-8 -*-
"""列出《操作系统》全部习题/答案解析区块及其体积，评估摘出影响。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '操作系统')
files = [f for f in sorted(os.listdir(D))
         if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")]

# 习题/答案区块：H3 标题以 "本节习题精选"/"答案与解析" 结尾，或含"习题""答案与解析"
EX_HEAD = re.compile(r"^###\s+.*?(本节习题精选|答案与解析|习题精选|本章习题)\s*$")

total_main = total_ex = 0
for f in files:
    lines = open(os.path.join(D, f), encoding="utf-8").read().split("\n")
    heads = [(i, l.strip()) for i, l in enumerate(lines) if EX_HEAD.match(l)]
    if not heads:
        print(f"--- {f}: 无习题区块 ---")
        continue
    # 区块结束 = 下一个同/更高级标题（## 或 ###）
    bounds = []
    for k, (i, t) in enumerate(heads):
        j = i + 1
        while j < len(lines):
            if re.match(r"^#{2,3}\s", lines[j]):
                break
            j += 1
        bounds.append((i, j, t))
    ex_chars = sum(sum(len(x) for x in lines[a:b]) for a, b, _ in bounds)
    print(f"--- {f} ---  全章 {sum(len(l) for l in lines)} 字符，其中习题区块 {ex_chars} 字符 "
          f"（{ex_chars*100//max(1,sum(len(l) for l in lines))}%）")
    for a, b, t in bounds:
        print(f"    L{a:>5}-{b:<5} {sum(len(x) for x in lines[a:b]):>6} 字符  {t}")
    total_main += sum(len(l) for l in lines) - ex_chars
    total_ex += ex_chars

print(f"\n合计：正文 {total_main} 字符，习题区块 {total_ex} 字符 "
      f"（占 {total_ex*100//(total_main+total_ex)}%）")
