# -*- coding: utf-8 -*-
"""查看损坏块的 HTML 上下文（把超长 data URI 折叠掉）。"""
import os, re, sys, pickle

sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("MINERU_HOME", r"E:\dsh_cache\mineru")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

with open(os.path.join(WS, "_ocr", "ds_result.pkl"), "rb") as f:
    result = pickle.load(f)

page = result.middle_json.pages[194]
blk = page.blocks[16]
d = blk.model_dump() if hasattr(blk, "model_dump") else blk.dict()
print("block 键:", list(d.keys()))
print("type:", d.get("type"), " bbox:", d.get("bbox"))
print("index:", d.get("index"))
print()
c = d.get("content")
print("content 类型:", type(c).__name__, " 长度:", len(c) if hasattr(c, "__len__") else "-")
if isinstance(c, list):
    for i, item in enumerate(c):
        s = item.get("content") if isinstance(item, dict) else str(item)
        print(f"--- content[{i}] keys={list(item.keys()) if isinstance(item, dict) else '-'} len={len(s)}")
        # 折叠 data URI
        folded = re.sub(r"(data:image/[^;]+;base64,)[A-Za-z0-9+/=<>\s]{60,}",
                        r"\1 <<<共 \g<0> 略>>> ", str(s))
        folded = re.sub(r"<<<共 data:image/[^;]+;base64,", "<<<", folded)
        print(folded[:2000])
        print()
