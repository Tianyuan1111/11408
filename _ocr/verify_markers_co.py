# -*- coding: utf-8 -*-
"""裁出两处疑似乱码标记的原图并 OCR，用于确认正确文字。"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("EASYOCR_MODULE_PATH", os.path.join(OCR, 'models'))

import fitz
import numpy as np
from PIL import Image

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
PDF = os.path.join(BOOKDIR, "27王道《计算机组成原理》高清带书签.pdf")
ZIP = os.path.join(WS, "_ocr", "co_full", "27王道《计算机组成原理》高清带书签.zip")
OUTDIR = os.path.join(WS, "_ocr", "co_verify")
os.makedirs(OUTDIR, exist_ok=True)

with zipfile.ZipFile(ZIP) as z:
    sc = json.loads(z.read("structured_content.json").decode("utf-8"))

# 先统计"考点追踪"在正文中正常出现的次数
md = open(os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md"), encoding="utf-8").read()
print("正文中「考点追踪」出现次数:", md.count("考点追踪"))
for m in re.finditer(r"考点追踪[^\n]{0,60}", md):
    print("   ", m.group(0)[:70])

TARGETS = [(23, 4, "基西面题"), (70, 14, "通高面瓣卜")]   # (page_idx, block_idx, 现有乱码)
doc = fitz.open(PDF)
crops = []
for pidx, bidx, label in TARGETS:
    blk = sc["pages"][pidx]["blocks"][bidx]
    x0, y0, x1, y1 = blk["bbox"]
    pg = doc[pidx]
    W, H = pg.rect.width, pg.rect.height
    # 上下各留一点余量，确保涵盖整行
    rect = fitz.Rect(max(0, x0 * W - 6), max(0, y0 * H - 10),
                     min(W, x1 * W + 6), min(H, y1 * H + 10))
    pix = pg.get_pixmap(dpi=400, clip=rect)
    p = os.path.join(OUTDIR, f"p{pidx+1}_b{bidx}.png")
    pix.save(p)
    crops.append((p, pidx + 1, label, blk.get("content")))
    print(f"\nPDF第{pidx+1}页 block{bidx} 裁剪 {pix.width}x{pix.height} -> {p}")

print("\n=== 对裁图做 OCR ===")
import easyocr
reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
for p, page, label, content in crops:
    img = np.array(Image.open(p).convert("RGB"))
    res = reader.readtext(img, detail=0)
    print(f"\n--- PDF第{page}页（原识别: {str(content)[:60]}...）")
    print("    OCR 结果:", " ".join(res))
