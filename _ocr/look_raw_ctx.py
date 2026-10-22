# -*- coding: utf-8 -*-
"""看清原始 markdown 中重复标题的上下文，判断文档真实顺序。"""
import os, re, sys, zipfile
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
ZIP = os.path.join(WS, "_ocr", "ds_full", "27王道《数据结构》高清带书签.zip")
with zipfile.ZipFile(ZIP) as z:
    lines = z.read("markdown.md").decode("utf-8").split("\n")

print("=== 原始 markdown L250-L275 ===")
for i in range(250, 276):
    print(f"{i:>6}| {lines[i][:118]}")

print("\n=== 原始 markdown L470-L500 ===")
for i in range(470, 501):
    print(f"{i:>6}| {lines[i][:118]}")

print("\n=== 原始 markdown 中所有以 # 开头且含『第』的行 ===")
for i, l in enumerate(lines):
    if l.startswith("#") and "第" in l:
        print(f"  L{i:>6}  {l[:80]}")

print("\n=== 原始 markdown 中所有以 # 开头且含『1.1』或『绪论』的行 ===")
for i, l in enumerate(lines):
    if l.startswith("#") and ("1.1" in l or "绪论" in l):
        print(f"  L{i:>6}  {l[:80]}")
