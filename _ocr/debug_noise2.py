# -*- coding: utf-8 -*-
"""追溯：这些行在原始文件中长什么样，为何 pass3 没处理掉。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SRC = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
lines = open(SRC, encoding="utf-8").read().split("\n")

NOISE = re.compile(r"([。！？；：\)）】])\s+([A-Z]{1,6})\s*$")
KEYS = ["是易失性存储器", "能表示的最小整数是", "最先完成的步骤是", "区分它们的依据是"]

for k in KEYS:
    for i, l in enumerate(lines):
        if k in l:
            print(f"--- 原文 L{i} (键={k}) ---")
            print(f"  {l[:220]!r}")
            print(f"  噪声规则匹配={bool(NOISE.search(l.rstrip()))}")
            print(f"  下一行 L{i+1}: {lines[i+1][:80]!r}")
            print()
            break

print("=== 模拟 pass3 对上述行的处理 ===")
for k in KEYS:
    for i, l in enumerate(lines):
        if k in l:
            s = l.rstrip()
            m = NOISE.search(s)
            print(f"  键={k}")
            print(f"    匹配={bool(m)}")
            if m:
                print(f"    group2={m.group(2)!r}  start2={m.start(2)}")
                print(f"    截断后={s[:m.start(2)].rstrip()[-50:]!r}")
            break
