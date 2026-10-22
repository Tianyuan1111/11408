# -*- coding: utf-8 -*-
"""复现 build_book.py 的页码对齐，看每一页匹配到了哪一行。"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
ZIP = os.path.join(WS, "_ocr", "ds_full", "27王道《数据结构》高清带书签.zip")
SKIP_TYPES = {"header", "page_number", "page_footnote", "ref_text", "index"}
_PUNCT = "　 \t\u00a0.,，。、;；:：!！?？\"'“”‘’()（）[]【】{}《》〈〉<>·-—_…~`*/\\|+="


def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if o == 0x3000:
            ch = " "
        elif 0xFF01 <= o <= 0xFF5E:
            ch = chr(o - 0xFEE0)
        out.append(ch)
    return "".join(c for c in "".join(out) if c not in _PUNCT).lower()


def block_text(b):
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


with zipfile.ZipFile(ZIP) as z:
    lines = z.read("markdown.md").decode("utf-8").split("\n")
    sc = json.loads(z.read("structured_content.json").decode("utf-8"))

line_norms = [norm(l) for l in lines]
pos = 0
print("page_idx  PDF页  签名(前24)                        匹配行  该行内容")
for p in sc["pages"][:34]:
    idx = p["page_idx"]
    sig = ""
    for b in p["blocks"]:
        if b.get("type") in SKIP_TYPES:
            continue
        t = norm(block_text(b))
        if len(t) >= 6:
            sig = t[:30]
            break
    found = None
    if sig:
        for i in range(pos, len(lines)):
            ln = line_norms[i]
            if not ln:
                continue
            if sig in ln or (len(ln) >= 8 and ln in sig):
                found = i
                break
    mark = ""
    if found is None:
        found = pos
        mark = "  <== 无签名/未匹配，落在当前位置"
    else:
        pos = max(pos, found)
    print(f"{idx:>8}  {idx+1:>4}  {sig[:24]:<32} L{found:<6} {lines[found][:60]!r}{mark}")
