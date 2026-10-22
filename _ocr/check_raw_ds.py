# -*- coding: utf-8 -*-
"""检查 MinerU 原始 markdown.md 的顺序（排除是我后处理造成的）。"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
ZIP = os.path.join(WS, "_ocr", "ds_full", "27王道《数据结构》高清带书签.zip")
with zipfile.ZipFile(ZIP) as z:
    md = z.read("markdown.md").decode("utf-8")
    sc = json.loads(z.read("structured_content.json").decode("utf-8"))

lines = md.split("\n")
print(f"原始 markdown.md: {len(lines)} 行, {len(md)} 字符")
print("含页标记:", len(re.findall(r"<!-- page", md)))

print("\n=== 原始 markdown 中 H1 的位置 ===")
for i, l in enumerate(lines):
    if re.match(r"^# ", l):
        print(f"  L{i:>6}  {l.strip()[2:]}")

print("\n=== 第1章内容与目录的先后 ===")
for probe in ["目   录", "# 目 录", "数据是信息的载体", "1.1 数据结构的基本概念", "第1章 绪论"]:
    idxs = [i for i, l in enumerate(lines) if probe in l]
    print(f"  {probe!r}: {len(idxs)} 次  {idxs[:5]}")

print("\n=== structured_content 的页序（前 30 页的首块文字）===")
for p in sc["pages"][:30]:
    first = ""
    for b in p["blocks"]:
        c = b.get("content")
        if isinstance(c, list):
            c = " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
        if isinstance(c, str) and c.strip():
            first = c.strip()[:58]
            break
    print(f"  page_idx={p['page_idx']:>3} (PDF {p['page_idx']+1:>3})  {first}")
