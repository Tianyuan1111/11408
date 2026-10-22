# -*- coding: utf-8 -*-
"""探测三本书的基本信息并导出各自的书签 TOC。"""
import os, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import fitz

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("数据结构", os.path.join(BOOKDIR, "27王道《数据结构》高清带书签.pdf"), "ds"),
    ("计算机组成原理", os.path.join(BOOKDIR, "27王道《计算机组成原理》高清带书签.pdf"), "co"),
    ("计算机网络", os.path.join(BOOKDIR, "27王道《计算机网络》高清带书签.pdf"), "cn"),
]

for name, fn, slug in BOOKS:
    p = os.path.join(WS, fn)
    d = fitz.open(p)
    toc = d.get_toc(simple=True)
    lv = Counter(t[0] for t in toc)
    # 抽样确认文字层
    sample = [len(d[i].get_text().strip()) for i in range(0, min(40, d.page_count))]
    out = os.path.join(WS, "_ocr", f"toc_{slug}.json")
    json.dump([{"level": l, "title": t, "page": pg} for l, t, pg in toc],
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"=== {name} ===")
    print(f"  页数={d.page_count}  书签={len(toc)}  层级分布={dict(sorted(lv.items()))}")
    print(f"  前40页文字层字符数合计={sum(sample)} (0 表示纯扫描)")
    print(f"  前 8 条书签:")
    for l, t, pg in toc[:8]:
        print(f"    L{l} p{pg:>3}  {t}")
    print(f"  已导出: {out}")
    print()
    d.close()
