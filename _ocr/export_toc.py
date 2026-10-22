# -*- coding: utf-8 -*-
"""导出书签结构为 UTF-8 JSON，供后续注入 Markdown 标题。"""
import os, json, sys
sys.stdout.reconfigure(encoding="utf-8")
import fitz

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
PDF = os.path.join(BOOKDIR, "27王道《操作系统》高清带书签.pdf")

doc = fitz.open(PDF)
toc = doc.get_toc(simple=True)
print("pages:", doc.page_count, "toc:", len(toc))

data = [{"level": lv, "title": ti, "page": pg} for lv, ti, pg in toc]
out = os.path.join(WS, "_ocr", "toc.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# 统计层级分布 + 打印前 40 条确认中文正常
from collections import Counter
print("level counts:", dict(sorted(Counter(d["level"] for d in data).items())))
print("page range:", min(d["page"] for d in data), "-", max(d["page"] for d in data))
print("---- first 40 ----")
for d in data[:40]:
    print("  " * d["level"], f'L{d["level"]} p{d["page"]:>3}  {d["title"]}')
print(f"\nwritten: {out}")
