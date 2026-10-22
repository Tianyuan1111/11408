# -*- coding: utf-8 -*-
"""导出章首页(header 块)的全部内容，评估能救回多少。"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
d = json.load(open(os.path.join(WS, "_ocr", "os_full_x", "structured_content.json"), encoding="utf-8"))
pages = d["pages"]

# 统计每页 header 块占比，找出"整页被当页眉"的页
print("=== 各页 block 类型统计（header 占比 >=80% 且 blocks>3）===")
suspects = []
for p in pages:
    bl = p["blocks"]
    if not bl:
        continue
    nh = sum(1 for b in bl if b.get("type") == "header")
    if nh / len(bl) >= 0.8 and len(bl) > 3:
        suspects.append(p["page_idx"])
        print(f"  page_idx={p['page_idx']} (PDF {p['page_idx']+1})  blocks={len(bl)} header={nh}")
print("涉及页:", suspects)
print()

for idx in suspects:
    p = pages[idx]
    print(f"########## page_idx={idx} (PDF {idx+1}) ##########")
    for b in p["blocks"]:
        c = b.get("content")
        if isinstance(c, list):
            c = " ".join(str(x.get("content", x)) for x in c)
        print(f"  [{b.get('type')}] {str(c)[:200]}")
    print()
