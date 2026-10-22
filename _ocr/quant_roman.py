# -*- coding: utf-8 -*-
"""量化罗马数字错乱：区分"正常使用"与"重复/错位"。"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机组成原理")
files = {f: open(os.path.join(D, f), encoding="utf-8").read()
         for f in sorted(os.listdir(D)) if f.endswith(".md")}

ROMAN_ANY = re.compile(r"[ⅠⅡⅢⅣⅤ]")
# 可疑：全角数字后面紧跟 I（重复），或 4 个以上连续 I
SUSPECT = re.compile(r"[ⅠⅡⅢⅣ][ⅠI]|I{4,}")

all_lines = [(fn, l) for fn, t in files.items() for l in t.split("\n")]
any_hits = [(fn, l) for fn, l in all_lines if ROMAN_ANY.search(l)]
susp = [(fn, l) for fn, l in all_lines if SUSPECT.search(l)]

print(f"含全角罗马数字的行: {len(any_hits)}")
print(f"其中疑似错乱（重复/错位）: {len(susp)}")
print(f"推测正常使用: {len(any_hits) - len(susp)}")

print("\n=== 所有疑似错乱行 ===")
for fn, l in susp:
    print(f"  [{fn[:5]}] {l[:120]}")

print("\n=== 正常使用的样子（对照）===")
normal = [(fn, l) for fn, l in any_hits if not SUSPECT.search(l)][:6]
for fn, l in normal:
    print(f"  [{fn[:5]}] {l[:120]}")
