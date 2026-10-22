# -*- coding: utf-8 -*-
"""
罗马数字错乱核验：把每条可疑行定位回 PDF 原块，裁图 OCR，输出"现状 vs 原页"对照。

思路：structured_content.json 记录了每个文本块的 page_idx + bbox。
      按文本内容把可疑行匹配回原块，再按 bbox 裁图 OCR，拿到原页真实文字。
"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("EASYOCR_MODULE_PATH", os.path.join(OCR, 'models'))

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机组成原理")
ZIP = os.path.join(WS, "_ocr", "co_full", "27王道《计算机组成原理》高清带书签.zip")
PDF = os.path.join(BOOKDIR, "27王道《计算机组成原理》高清带书签.pdf")
OUTDIR = os.path.join(WS, "_ocr", "roman_verify")
os.makedirs(OUTDIR, exist_ok=True)

SUSPECT = re.compile(r"[ⅠⅡⅢⅣ][ⅠI]|I{4,}")
CJK_OR_ALNUM = re.compile(r"[\u4e00-\u9fff0-9A-Za-z]")


def norm(s):
    return re.sub(r"[\s\u3000]+", "", s)


with zipfile.ZipFile(ZIP) as z:
    sc = json.loads(z.read("structured_content.json").decode("utf-8"))

blocks = []
for p in sc["pages"]:
    for b in p["blocks"]:
        c = b.get("content")
        if isinstance(c, list):
            c = " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
        if isinstance(c, str) and c.strip():
            blocks.append({"page": p["page_idx"], "bbox": b.get("bbox"),
                           "type": b.get("type"), "text": c, "n": norm(c)})
print(f"结构化文本块: {len(blocks)}")

files = {f: open(os.path.join(D, f), encoding="utf-8").read()
         for f in sorted(os.listdir(D)) if f.endswith(".md")}
susp = [(fn, l.strip()) for fn, t in files.items() for l in t.split("\n") if SUSPECT.search(l)]
print(f"可疑行: {len(susp)}")

# 把可疑行匹配回原块
jobs = {}
unmatched = []
for fn, l in susp:
    key = norm(re.sub(r"[ⅠⅡⅢⅣ]", "I", l))
    hit = None
    for b in blocks:
        bn = re.sub(r"[ⅠⅡⅢⅣ]", "I", b["n"])
        if key and (key in bn or (len(key) > 12 and bn in key)):
            hit = b
            break
    if hit:
        jobs.setdefault((hit["page"], tuple(hit["bbox"]), hit["text"][:40]), []).append((fn, l))
    else:
        unmatched.append((fn, l))
print(f"定位到原块: {len(jobs)} 个块，覆盖 {sum(len(v) for v in jobs.values())} 行")
print(f"未能定位: {len(unmatched)} 行")

if unmatched[:5]:
    print("  未定位示例:")
    for fn, l in unmatched[:5]:
        print(f"    [{fn[:5]}] {l[:80]}")

import fitz
import numpy as np
from PIL import Image
import easyocr

doc = fitz.open(PDF)
reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)

results = []
for idx, ((page, bbox, head), items) in enumerate(sorted(jobs.items())):
    x0, y0, x1, y1 = bbox
    pg = doc[page]
    W, H = pg.rect.width, pg.rect.height
    rect = fitz.Rect(max(0, x0 * W - 5), max(0, y0 * H - 8),
                     min(W, x1 * W + 5), min(H, y1 * H + 8))
    p = os.path.join(OUTDIR, f"p{page+1}_{idx}.png")
    pg.get_pixmap(dpi=400, clip=rect).save(p)
    img = np.array(Image.open(p).convert("RGB"))
    ocr = " ".join(reader.readtext(img, detail=0))
    results.append({"page": page + 1, "bbox": bbox, "now": [l for _, l in items],
                    "ocr": ocr, "png": p})
    if (idx + 1) % 8 == 0:
        print(f"  ...已核验 {idx+1}/{len(jobs)}", flush=True)

json.dump(results, open(os.path.join(WS, "_ocr", "roman_verify.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"\n=== 核验结果（前 25 组）===")
for r in results[:25]:
    print(f"\nPDF第{r['page']}页  现识别:")
    for l in r["now"]:
        print(f"    {l[:100]}")
    print(f"  原页OCR: {r['ocr'][:180]}")
print(f"\n完整结果: _ocr/roman_verify.json （共 {len(results)} 组）")
