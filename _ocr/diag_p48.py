# -*- coding: utf-8 -*-
import os, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
d = json.load(open(os.path.join(WS, "_ocr", "os_full_x", "structured_content.json"), encoding="utf-8"))
pages = d["pages"]

p = pages[48]
print("=== page_idx=48 类型分布 ===", Counter(b.get("type") for b in p["blocks"]))
for i, b in enumerate(p["blocks"]):
    c = b.get("content")
    if isinstance(c, list):
        c = " ".join(str(x.get("content", x)) for x in c)
    print(f"{i:>3} [{b.get('type'):<16}] {str(c)[:150]}")

print()
print("=== 全文档类型分布 ===")
allc = Counter()
for pg in pages:
    for b in pg["blocks"]:
        allc[b.get("type")] += 1
for k, v in allc.most_common():
    print(f"  {k:<18} {v}")
