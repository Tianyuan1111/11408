# -*- coding: utf-8 -*-
import os
import json, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(os.path.join(OCR, 'toc_ds.json'), encoding="utf-8"))
print("总条数", len(d))
print("前 6 条:", [(x["level"], x["page"], x["title"]) for x in d[:6]])
print()
print("所有 L1 条目:")
for x in d:
    if x["level"] == 1:
        print(f"   p{x['page']:>3}  {x['title']!r}")
print()
print("含『第』且以章结尾附近的条目:")
for x in d[:40]:
    print(f"   L{x['level']} p{x['page']:>3}  {x['title']!r}")
