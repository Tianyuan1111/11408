# -*- coding: utf-8 -*-
"""核实：计算机网络各章文件末尾是否残留下一章的考纲内容。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机网络")

print("=== 第1章文件末尾 30 行（看是否有第2章的内容）===")
p = os.path.join(D, "第1章 计算机网络体系结构.md")
ls = open(p, encoding="utf-8").read().split("\n")
for l in ls[-32:]:
    if l.strip():
        print(f"    {l[:100]}")

print("\n=== 各正文文件里【考纲内容】出现位置（行号 / 总行数）===")
for f in sorted(os.listdir(D)):
    if not f.endswith(".md") or "习题" in f or f in ("README.md",) or f.startswith("待核对"):
        continue
    t = open(os.path.join(D, f), encoding="utf-8").read().split("\n")
    hits = [i for i, l in enumerate(t) if "考纲内容" in l]
    print(f"    {f:<32} 共 {len(t):>5} 行，考纲内容在第 {hits} 行")

print("\n=== 源 markdown 中第2章 H1 前后的页标记 ===")
SRC = os.path.join(WORKDIR, "计算机网络_Markdown", "王道计算机网络.md")
src = open(SRC, encoding="utf-8").read().split("\n")
for j in range(1680, 1706):
    print(f"    {j:>5}| {src[j][:96]}")
