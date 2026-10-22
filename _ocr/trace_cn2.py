# -*- coding: utf-8 -*-
"""追查计算机网络第2章【考纲内容】在源 markdown 中的形态。"""
import os, re, sys, zipfile
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

SRC = os.path.join(WORKDIR, "计算机网络_Markdown", "王道计算机网络.md")
src = open(SRC, encoding="utf-8").read().split("\n")
i = next(k for k, l in enumerate(src) if l.strip().startswith("# 第2章"))
print("=== 源 markdown 第2章 H1 附近 ===")
for j in range(i, min(i + 16, len(src))):
    if src[j].strip():
        print(f"  {j:>5}| {src[j][:100]}")

print("\n=== 源 markdown 中所有『考纲内容』 ===")
for k, l in enumerate(src):
    if "考纲内容" in l:
        print(f"  {k:>5}| {l[:90]!r}")

print("\n=== MinerU 原始 markdown.md 中第2章附近 ===")
with zipfile.ZipFile(os.path.join(WS, "_ocr", "cn_full",
                                  "27王道《计算机网络》高清带书签.zip")) as z:
    raw = z.read("markdown.md").decode("utf-8").split("\n")
for k, l in enumerate(raw):
    if "考纲内容" in l:
        print(f"  {k:>5}| {l[:90]!r}")
