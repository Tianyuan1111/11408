# -*- coding: utf-8 -*-
"""核对：组成原理各章是否仍含习题区；以及用户手工拆出的第1章习题文件结构。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '计算机组成原理')
EX = re.compile(r"^###\s+.*?(本节习题精选|习题精选|答案与解析|本章习题|一、习题精选|二、答案与解析)\s*$")
ANY = re.compile(r"习题|答案与解析")

print("=== 各章正文中的习题标题 ===")
for f in sorted(os.listdir(D)):
    if not f.endswith(".md") or f in ("README.md",) or f.startswith("待核对"):
        continue
    t = open(os.path.join(D, f), encoding="utf-8").read()
    hits = [l.strip() for l in t.split("\n") if re.match(r"^#{1,6}\s", l) and ANY.search(l)]
    print(f"  {f:<34} 标题命中 {len(hits):>2}  {hits[:1]}")

print("\n=== 用户手工拆出的第1章习题文件（前 40 行）===")
p = os.path.join(D, "第1章 计算机系统概述_习题.md")
ls = open(p, encoding="utf-8").read().split("\n")
for i, l in enumerate(ls[:40]):
    if l.strip():
        print(f"  {i:>4}| {l[:104]}")

print("\n=== 该文件全部标题 ===")
for l in ls:
    if re.match(r"^#{1,6}\s", l):
        print(f"    {l.strip()[:90]}")

print("\n=== 第1章正文当前标题 ===")
for l in open(os.path.join(D, "第1章 计算机系统概述.md"), encoding="utf-8").read().split("\n"):
    if re.match(r"^#{1,3}\s", l):
        print(f"    {l.strip()[:90]}")
