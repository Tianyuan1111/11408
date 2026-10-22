# -*- coding: utf-8 -*-
"""诊断：找出未能匹配 MinerU 标题的书签。"""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SRC_MD = os.path.join(WS, "_ocr", "os_full_x", "markdown.md")
TOC = os.path.join(WS, "_ocr", "toc.json")

PAGE_RE = re.compile(r"<!--\s*page\s+(\d+)\s+of\s+(\d+)\s*-->")
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BARE_CHAP = re.compile(r"^第\d+章$")

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


lines = open(SRC_MD, encoding="utf-8").read().split("\n")
pages_seen, cur = set(), 0
headings = []
for i, ln in enumerate(lines):
    m = PAGE_RE.search(ln)
    if m:
        cur = int(m.group(1))
        pages_seen.add(cur)
    h = HEAD_RE.match(ln)
    if h:
        headings.append({"text": h.group(2).strip(), "page": cur, "n": norm(h.group(2))})

raw = json.load(open(TOC, encoding="utf-8"))
bms = [{"level": d["level"], "title": " ".join(d["title"].split()), "page": d["page"]}
       for d in raw if " ".join(d["title"].split())]
bms = [b for b in bms if not BARE_CHAP.match(b["title"])]
for b in bms:
    b["n"] = norm(b["title"])

print("markdown 中出现的页码数:", len(pages_seen), "范围", min(pages_seen), "-", max(pages_seen))

def matches(hn, bn):
    if not hn or not bn:
        return False
    if hn == bn:
        return True
    if len(bn) >= 4 and len(hn) >= 4 and (hn.startswith(bn) or bn.startswith(hn)):
        return True
    if len(hn) >= 3 and bn.startswith(hn) and len(bn) > len(hn):
        return True
    return False

matched, used, cursor = {}, set(), 0
for bi, bm in enumerate(bms):
    for hi in range(cursor, len(headings)):
        if hi in matched:
            continue
        if matches(headings[hi]["n"], bm["n"]):
            matched[hi] = bi
            used.add(bi)
            cursor = hi + 1
            break

print("\n未匹配的书签:")
for bi, bm in enumerate(bms):
    if bi not in used:
        print(f'  L{bm["level"]} p{bm["page"]:>3} 页标记存在={bm["page"] in pages_seen}  {bm["title"]}')
