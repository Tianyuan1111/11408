# -*- coding: utf-8 -*-
"""查清第1章考纲内容为何在重新生成后缺失。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SRC = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
D = os.path.join(BOOKDIR, "计算机组成原理")
BK = os.path.join(WS, "_ocr", "co_before_redo")

import datetime
for p in [SRC, os.path.join(D, "第1章 计算机系统概述.md"),
          os.path.join(BK, "第1章 计算机系统概述.md")]:
    print(f"  {datetime.datetime.fromtimestamp(os.path.getmtime(p))}  {p}")

print("\n=== 源 markdown 中第1章 H1 附近 ===")
src = open(SRC, encoding="utf-8").read().split("\n")
i = next(k for k, l in enumerate(src) if l.strip().startswith("# 第1章"))
for j in range(i, min(i + 30, len(src))):
    if src[j].strip():
        print(f"  {j:>5}| {src[j][:100]}")

print("\n=== 源 markdown 中『考纲内容』出现位置 ===")
for k, l in enumerate(src):
    if "考纲内容" in l:
        print(f"  {k:>5}| {l[:100]}")

print("\n=== 重新生成的第1章里是否含『考纲内容』 ===")
t = open(os.path.join(D, "第1章 计算机系统概述.md"), encoding="utf-8").read()
print("  含『考纲内容』:", "考纲内容" in t)
print("  含『（一）计算机系统层次结构』:", "（一）计算机系统层次结构" in t)
print("  含『计算机系统的基本组成』:", "计算机系统的基本组成" in t)
print("  含『计算机硬件的基本组成』:", "计算机硬件的基本组成" in t)
