# -*- coding: utf-8 -*-
"""零安装基线验证：用已装好的 easyocr 试 OCR 一页，评估质量与速度。"""
import os, sys, time, io

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
# 把所有缓存目录都引到工作区内，避免沙箱拒写
os.environ.setdefault("EASYOCR_MODULE_PATH", os.path.join(WS, "_ocr", "models"))
os.environ.setdefault("MODULE_PATH", os.path.join(WS, "_ocr", "models"))

sys.stdout.reconfigure(encoding="utf-8")

import fitz
import numpy as np

PDF = os.path.join(BOOKDIR, "27王道《操作系统》高清带书签.pdf")
PAGE = int(sys.argv[1]) if len(sys.argv) > 1 else 100

doc = fitz.open(PDF)
page = doc[PAGE]
pix = page.get_pixmap(dpi=200)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
if pix.n == 4:
    img = img[:, :, :3]
print(f"[page {PAGE}] raster {pix.width}x{pix.height}", flush=True)

# 书签里这一页的标题，用来对照
toc_titles = [t[1] for t in doc.get_toc() if t[2] == PAGE + 1]
print("[bookmark titles on this page]", toc_titles, flush=True)

t0 = time.time()
import easyocr
print(f"[load] easyocr import+init start", flush=True)
reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
print(f"[load] ready in {time.time()-t0:.1f}s", flush=True)

t1 = time.time()
res = reader.readtext(img, detail=1, paragraph=False)
dt = time.time() - t1
print(f"[ocr] {len(res)} boxes in {dt:.1f}s ({dt/max(1,len(res)):.2f}s/box)", flush=True)

lines = []
for box, txt, conf in res:
    ys = [p[1] for p in box]
    xs = [p[0] for p in box]
    lines.append((min(ys), min(xs), txt, conf))
lines.sort()
out = os.path.join(WS, "_ocr", f"probe_p{PAGE}.txt")
with open(out, "w", encoding="utf-8") as f:
    for y, x, txt, conf in lines:
        f.write(f"{txt}\t{conf:.2f}\n")
print(f"[out] {out}", flush=True)
print("---- first 25 lines ----", flush=True)
for y, x, txt, conf in lines[:25]:
    print(f"{conf:.2f}  {txt}", flush=True)
