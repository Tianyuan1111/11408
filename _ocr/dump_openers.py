# -*- coding: utf-8 -*-
"""列出各受影响章节开头被丢弃的 header 块（含类型），用于设计精确修复。"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统", os.path.join(BOOKDIR, "操作系统"), "_ocr/os_full", "_ocr/toc.json"),
    ("数据结构", os.path.join(BOOKDIR, "数据结构"), "_ocr/ds_full", "_ocr/toc_ds.json"),
    ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理"), "_ocr/co_full", "_ocr/toc_co.json"),
    ("计算机网络", os.path.join(BOOKDIR, "计算机网络"), "_ocr/cn_full", "_ocr/toc_cn.json"),
]
SKIP = {"page_number", "page_footnote", "ref_text", "index"}


def btext(b):
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


def norm(s):
    return re.sub(r"[\s\u3000*]+", "", s)


for name, outdir, zipdir, toc in BOOKS:
    D = os.path.join(WS, outdir)
    zd = os.path.join(WS, zipdir)
    zf = [f for f in os.listdir(zd) if f.lower().endswith(".zip")][0]
    with zipfile.ZipFile(os.path.join(zd, zf)) as z:
        sc = json.loads(z.read("structured_content.json").decode("utf-8"))
    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))
    chaps, seen = [], set()
    for d in raw:
        t = " ".join(d["title"].split())
        if d["level"] != 1 or not re.match(r"^第\d+章", t):
            continue
        num = re.match(r"^(第\d+章)", t).group(1)
        if num in seen:
            continue
        seen.add(num)
        chaps.append((num, d["page"]))

    print("=" * 78)
    print(f"### {name}")
    print("=" * 78)
    for num, page in chaps:
        f = next((x for x in os.listdir(D) if x.startswith(num) and x.endswith(".md")
                  and "习题" not in x), None)
        if not f:
            continue
        ntext = norm(open(os.path.join(D, f), encoding="utf-8").read())
        for idx in (page - 1, page, page - 2):
            if not (0 <= idx < len(sc["pages"])):
                continue
            blocks = sc["pages"][idx]["blocks"]
            seq = []
            for b in blocks:
                tp = b.get("type")
                if tp in SKIP:
                    continue
                t = btext(b).strip()
                if tp == "header" and t:
                    seq.append(("H", t))
                    continue
                if tp in ("text", "paragraph_title") and t:
                    seq.append(("T", t))
                    break
                break
            if not any("考纲内容" in t for _, t in seq):
                continue
            print(f"\n  {num}  (PDF第{page}页)")
            for tp, t in seq:
                present = norm(t)[:14] in ntext
                mark = "已有" if present else "缺失"
                print(f"      [{tp}] {mark}  {t[:76]}")
            break
