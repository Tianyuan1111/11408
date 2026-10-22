# -*- coding: utf-8 -*-
"""确认剩余选项异常的来源：清理引入 vs 原文固有。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

CASES = [
    ("数据结构", os.path.join(BOOKDIR, "数据结构"), "第5章 树与二叉树.md",
     os.path.join(WORKDIR, '数据结构_Markdown', '王道数据结构.md'), "A. 树的高度至多是n-3"),
    ("数据结构", os.path.join(BOOKDIR, "数据结构"), "第6章 图.md",
     os.path.join(WORKDIR, '数据结构_Markdown', '王道数据结构.md'), "D. $( a , e ) , ( c , e )"),
    ("计算机网络", os.path.join(BOOKDIR, "计算机网络"), "第4章 网络层.md",
     os.path.join(WORKDIR, '计算机网络_Markdown', '王道计算机网络.md'), "A. 有效分配IP地址空间"),
]

for name, outdir, fn, src, key in CASES:
    print("=" * 76)
    print(f"### {name} / {fn}")
    print("=" * 76)
    t = open(os.path.join(WS, outdir, fn), encoding="utf-8").read().split("\n")
    i = next((k for k, l in enumerate(t) if l.strip().startswith(key)), None)
    print("--- 清理版 ---")
    if i is not None:
        for j in range(max(0, i - 8), min(i + 8, len(t))):
            if t[j].strip():
                print(f"  L{j:>5}| {t[j][:105]}")
    s = open(os.path.join(WS, src), encoding="utf-8").read().split("\n")
    j = next((k for k, l in enumerate(s) if key.replace(" ", "") in l.replace(" ", "")), None)
    print("--- 原文 ---")
    if j is not None:
        for k in range(max(0, j - 6), min(j + 6, len(s))):
            if s[k].strip():
                print(f"  L{k:>5}| {s[k][:105]}")
    print()
