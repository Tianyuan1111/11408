# -*- coding: utf-8 -*-
"""核实组成原理各章【考纲内容】是否真的从源 markdown 中丢失。"""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS_MD = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
import zipfile
ZIP = os.path.join(WS, "_ocr", "co_full", "27王道《计算机组成原理》高清带书签.zip")

# 各章起始 PDF 页（来自书签）
CHAP = [(1, "计算机系统概述", 13), (2, "数据的表示和运算", 31), (3, "存储系统", 88),
        (4, "指令系统", 159), (5, "中央处理器", 207), (6, "总线", 286), (7, "输入/输出系统", 303)]

print("=== 源 markdown 中各章是否有『考纲内容』 ===")
src = open(BOOKS_MD, encoding="utf-8").read().split("\n")
h1 = [(i, l.strip()[2:]) for i, l in enumerate(src) if re.match(r"^# 第\d+章", l)]
for k, (i, t) in enumerate(h1):
    end = h1[k + 1][0] if k + 1 < len(h1) else len(src)
    seg = "\n".join(src[i:end])
    print(f"  {t:<24} 有『考纲内容』: {'考纲内容' in seg}")

print("\n=== PDF 解析数据（structured_content）中对应页的块 ===")
with zipfile.ZipFile(ZIP) as z:
    sc = json.loads(z.read("structured_content.json").decode("utf-8"))

for num, name, page in CHAP:
    idx = page - 1
    p = sc["pages"][idx]
    texts = []
    for b in p["blocks"]:
        c = b.get("content")
        if isinstance(c, list):
            c = " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
        if isinstance(c, str) and c.strip():
            texts.append((b.get("type"), c.strip()[:60]))
    has = any("考纲" in t for _, t in texts)
    print(f"\n  第{num}章 {name}  (PDF 第{page} 页, 共 {len(texts)} 块)  含『考纲内容』: {has}")
    for tp, t in texts[:7]:
        print(f"      [{tp:<15}] {t}")
