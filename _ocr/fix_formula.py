# -*- coding: utf-8 -*-
"""
修复第 370 页那个 OCR 失败的公式：
  1. 按 structured_content 的 bbox 从 PDF 原页裁出该公式区域（高 DPI）；
  2. 用 easyocr 反查裁图内容，确认裁对了区域（防止裁错位置）；
  3. 把最终 Markdown 里那段乱码公式替换为图片引用——保持忠实，不臆造公式内容。
"""
import os, re, sys, json
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
PDF = os.path.join(BOOKDIR, "27王道《操作系统》高清带书签.pdf")
MD = os.path.join(WORKDIR, "操作系统_Markdown", "王道操作系统.md")
IMG_DIR = os.path.join(WORKDIR, "操作系统_Markdown", "images")
SC = os.path.join(WS, "_ocr", "os_full_x", "structured_content.json")

PAGE_IDX = 369                     # PDF 第 370 页
BLOCK = 11
DPI = 400
MARGIN_PT = 4

sc = json.load(open(SC, encoding="utf-8"))
blk = sc["pages"][PAGE_IDX]["blocks"][BLOCK]
x0, y0, x1, y1 = blk["bbox"]
doc = fitz.open(PDF)
page = doc[PAGE_IDX]
W, H = page.rect.width, page.rect.height

rect = fitz.Rect(
    max(0, x0 * W - MARGIN_PT),
    max(0, y0 * H - MARGIN_PT),
    min(W, x1 * W + MARGIN_PT),
    min(H, y1 * H + MARGIN_PT),
)
print("裁剪区域(pt):", rect)

pix = page.get_pixmap(dpi=DPI, clip=rect)
name = f"page_{PAGE_IDX}_equation_{BLOCK}_orig.png"
out = os.path.join(IMG_DIR, name)
pix.save(out)
print(f"已保存: {out}  {pix.width}x{pix.height}")

# --- 反查验证：裁图里应该出现"磁盘容量"等字样 ---
img = np.array(Image.open(out).convert("RGB"))
import easyocr
reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
res = reader.readtext(img, detail=0)
joined = " ".join(res)
print("裁图 OCR 结果:", joined[:200])
keys = ["磁盘容量", "柱面", "磁道", "扇区"]
hit = [k for k in keys if k in joined]
print("命中关键词:", hit)

if len(hit) >= 3:
    lines = open(MD, encoding="utf-8").read().split("\n")
    gi = [i for i, l in enumerate(lines) if l.count("区") > 20]
    if gi:
        i = gi[0]
        # 替换 $$ ... $$ 整块
        start = i
        while start > 0 and lines[start].strip() != "$$":
            start -= 1
        end = i
        while end < len(lines) and lines[end].strip() != "$$":
            end += 1
        print(f"替换 L{start}..L{end}（原为乱码公式块）")
        new = [f"![]({name})", "", "> 注：原 PDF 中该公式为公式化排版，OCR 多次识别失败（识别为重复乱码），此处直接嵌入原图。"]
        lines[start:end + 1] = new
        open(MD, "w", encoding="utf-8").write("\n".join(lines))
        print("已写回 Markdown")
    else:
        print("未在 Markdown 中找到乱码行")
else:
    print("裁图验证不通过，未修改 Markdown")
