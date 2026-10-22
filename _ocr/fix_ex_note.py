# -*- coding: utf-8 -*-
"""修正习题文件的来源说明措辞；确认正文衔接。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '操作系统')
OLD = "；区块编号（如 1.1.4）与原书小节对应。"
NEW = "；区块标题保留了原书的小节编号。"

for f in sorted(os.listdir(D)):
    if not f.endswith(".md") or "习题与解析" not in f:
        continue
    p = os.path.join(D, f)
    t = open(p, encoding="utf-8").read()
    if OLD in t:
        open(p, "w", encoding="utf-8").write(t.replace(OLD, NEW))
        print(f"  已修正 {f}")

print("\n=== 正文衔接检查（第1章：1.1.3 之后应直接进入 1.2）===")
ls = open(os.path.join(D, "第1章 计算机系统概述.md"), encoding="utf-8").read().split("\n")
i = next(k for k, l in enumerate(ls) if "1.1.3" in l)
for j in range(i, min(i + 22, len(ls))):
    if ls[j].strip():
        print(f"  {ls[j][:104]}")

print("\n=== 正文衔接检查（第2章：2.1.5 之后）===")
ls2 = open(os.path.join(D, "第2章 进程与线程.md"), encoding="utf-8").read().split("\n")
k = next((k for k, l in enumerate(ls2) if "2.1.5" in l and l.startswith("###")), i)
for j in range(k, min(k + 18, len(ls2))):
    if ls2[j].strip():
        print(f"  {ls2[j][:104]}")
