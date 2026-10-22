# -*- coding: utf-8 -*-
"""确认《操作系统》中所有与习题/答案相关的标题，避免漏摘。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '操作系统')
files = [f for f in sorted(os.listdir(D))
         if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")]

CAND = re.compile(r"习题|答案|解析|综合应用|单项选择|多项选择|填空|判断")
EXTRACT = re.compile(r"^###\s+.*?(本节习题精选|习题精选|答案与解析|本章习题)\s*$")

print("=== 所有命中的标题，标注是否会被摘出 ===")
for f in files:
    lines = open(os.path.join(D, f), encoding="utf-8").read().split("\n")
    hits = [(i, l.strip()) for i, l in enumerate(lines) if CAND.search(l)]
    if not hits:
        continue
    print(f"\n--- {f} ---")
    for i, t in hits:
        lvl = len(t) - len(t.lstrip("#"))
        flag = "摘出" if EXTRACT.match(t) else ("层级内" if lvl >= 4 else "!! 保留（需人工判断）")
        print(f"  L{i:>5} {'#'*lvl} {t[:70]:<74} {flag}")
