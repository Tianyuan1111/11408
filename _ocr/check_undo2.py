# -*- coding: utf-8 -*-
"""核对带 `## 【考纲内容】` 的书（操作系统 / 计算机网络）插入位置。"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
for d, f in [(os.path.join(BOOKDIR, "操作系统"), "第2章 进程与线程.md"),
             (os.path.join(BOOKDIR, "操作系统"), "第4章 文件管理.md"),
             (os.path.join(BOOKDIR, "计算机网络"), "第4章 网络层.md"),
             (os.path.join(BOOKDIR, "计算机网络"), "第6章 应用层.md")]:
    ls = open(os.path.join(WS, d, f), encoding="utf-8").read().split("\n")
    print(f"===== {d} / {f} =====")
    n = 0
    for l in ls:
        if not l.strip():
            continue
        print(f"    {l[:96]}")
        n += 1
        if n >= 11:
            break
    print()
