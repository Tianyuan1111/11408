# -*- coding: utf-8 -*-
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.join(BOOKDIR, '计算机组成原理')
CASES = [("第1章 计算机系统概述.md", "D. 高级语言中的每条语句与ISA"),
         ("第2章 数据的表示和运算.md", "D. 一般用移码表示浮点数的阶码"),
         ("第5章 中央处理器.md", "D. 取指令阶段和指令译码阶段"),
         ("第6章 总线.md", "D. 提供数据信息")]
for fn, key in CASES:
    ls = open(os.path.join(D, fn), encoding="utf-8").read().split("\n")
    i = next((k for k, l in enumerate(ls) if l.strip().startswith(key)), None)
    print(f"===== {fn} =====")
    if i is not None:
        for j in range(max(0, i - 8), min(i + 3, len(ls))):
            print(f"  L{j}: {ls[j][:100]}")
    print()
