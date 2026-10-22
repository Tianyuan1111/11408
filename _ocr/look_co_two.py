# -*- coding: utf-8 -*-
"""对照：备份(你的版本) 与 重新生成版本 的第1、2章实际内容。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '计算机组成原理')
BK = os.path.join(OCR, 'co_before_redo')
EX = re.compile(r"^#{1,4}\s+.*(习题精选|答案与解析|试题精选).*$")

for f in ["第1章 计算机系统概述.md", "第2章 数据的表示和运算.md"]:
    for tag, root in [("你的版本", BK), ("重新生成", D)]:
        p = os.path.join(root, f)
        t = open(p, encoding="utf-8").read()
        ls = t.split("\n")
        exs = [l.strip() for l in ls if EX.match(l)]
        print(f"===== {f} / {tag}: {len(t)} 字符, {len(ls)} 行, 习题标题 {len(exs)} =====")
        for l in ls[:14]:
            if l.strip():
                print(f"    {l[:96]}")
        if exs:
            print("    习题标题:", exs[:6])
        print()

print("=== 源 markdown 里第1章有没有考纲内容 / 习题 ===")
src = open(os.path.join(WORKDIR, '计算机组成原理_Markdown', '王道计算机组成原理.md'),
           encoding="utf-8").read().split("\n")
for i, l in enumerate(src[:60]):
    if l.strip():
        print(f"  {i:>4}| {l[:96]}")
