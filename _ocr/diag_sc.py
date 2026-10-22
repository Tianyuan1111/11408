# -*- coding: utf-8 -*-
"""检查 structured_content.json 的结构，为页标记对齐做准备。"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SC = os.path.join(WS, "_ocr", "os_full_x", "structured_content.json")
d = json.load(open(SC, encoding="utf-8"))
print("顶层键:", list(d.keys()))
pages = d["pages"]
print("页数:", len(pages))
print("第0页键:", list(pages[0].keys()))
print()

for idx in (12, 48, 49):
    p = pages[idx]
    print(f"===== page_idx={idx} (PDF 第 {idx+1} 页) blocks={len(p['blocks'])} =====")
    for b in p["blocks"][:6]:
        keys = list(b.keys())
        t = b.get("type")
        c = b.get("content")
        if isinstance(c, list):
            c = " | ".join(str(x.get("content", x))[:60] for x in c[:3])
        elif isinstance(c, str):
            c = c[:140]
        print(f"  type={t} keys={keys}")
        print(f"     content={str(c)[:160]}")
    print()
