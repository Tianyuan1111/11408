# -*- coding: utf-8 -*-
"""侦察《操作系统》清理版的标题结构，定位习题与答案解析。"""
import os, re, sys
from collections import Counter

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '操作系统')
files = [f for f in sorted(os.listdir(D))
         if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")]

print("=== 文件清单 ===")
for f in files:
    t = open(os.path.join(D, f), encoding="utf-8").read()
    print(f"  {f:<28} {len(t):>7} 字符")

print("\n=== 各章标题结构（H2/H3，重点看习题相关）===")
KEY = re.compile(r"习题|答案|解析|综合应用|单项选择|小结|疑难|易混淆|思维拓展|归纳")
for f in files:
    print(f"\n--- {f} ---")
    for i, l in enumerate(open(os.path.join(D, f), encoding="utf-8").read().split("\n")):
        m = re.match(r"^(#{2,4})\s+(.*)$", l)
        if m:
            lvl, t = len(m.group(1)), m.group(2).strip()
            tag = "  <<< 习题相关" if KEY.search(t) else ""
            print(f"  L{i:>5} {'  '*(lvl-2)}{'#'*lvl} {t[:60]}{tag}")
