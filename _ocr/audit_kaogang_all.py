# -*- coding: utf-8 -*-
"""审计四本书：各章【考纲内容】开头的 header 块是否在成品里丢失。"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统", os.path.join(BOOKDIR, "操作系统"), os.path.join(WORKDIR, '操作系统_Markdown', '王道操作系统.md'), "_ocr/os_full", "_ocr/toc.json"),
    ("数据结构", os.path.join(BOOKDIR, "数据结构"), os.path.join(WORKDIR, '数据结构_Markdown', '王道数据结构.md'), "_ocr/ds_full", "_ocr/toc_ds.json"),
    ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理"), os.path.join(WORKDIR, '计算机组成原理_Markdown', '王道计算机组成原理.md'), "_ocr/co_full", "_ocr/toc_co.json"),
    ("计算机网络", os.path.join(BOOKDIR, "计算机网络"), os.path.join(WORKDIR, '计算机网络_Markdown', '王道计算机网络.md'), "_ocr/cn_full", "_ocr/toc_cn.json"),
]
SKIP = {"page_number", "page_footnote", "ref_text", "index"}


def btext(b):
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


for name, outdir, srcmd, zipdir, toc in BOOKS:
    D = os.path.join(WS, outdir)
    zd = os.path.join(WS, zipdir)
    zf = [f for f in os.listdir(zd) if f.lower().endswith(".zip")][0]
    with zipfile.ZipFile(os.path.join(zd, zf)) as z:
        sc = json.loads(z.read("structured_content.json").decode("utf-8"))
    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))
    chaps = [(d["title"].split()[0], d["page"]) for d in raw
             if d["level"] == 1 and d["title"].strip().startswith("第") and "章" in d["title"][:4]]
    # 去重（有的书章标题分两条）
    seen, cl = set(), []
    for t, p in chaps:
        if t not in seen:
            seen.add(t)
            cl.append((t, p))

    files = {f: open(os.path.join(D, f), encoding="utf-8").read()
             for f in os.listdir(D) if f.endswith(".md")
             and f != "README.md" and not f.startswith("待核对")}
    allt = "\n".join(files.values())
    norm = lambda s: re.sub(r"[\s\u3000]+", "", s)

    print(f"\n### {name}")
    for title, page in cl:
        idx = page - 1
        if idx >= len(sc["pages"]):
            continue
        blocks = sc["pages"][idx]["blocks"]
        # 取该页开头连续的 header 块（到第一个 text/paragraph_title 为止）
        opener = []
        for b in blocks:
            tp = b.get("type")
            if tp in SKIP:
                continue
            if tp == "header":
                t = btext(b).strip()
                if t:
                    opener.append(t)
                continue
            break
        if not opener:
            continue
        # 检查这些文本是否存在于成品中
        missing = [t for t in opener if norm(t)[:20] and norm(t)[:20] not in norm(allt)]
        # 只看【考纲内容】及其后的条目（章号/章名本来就用 H1 表达）
        k = next((i for i, t in enumerate(opener) if "考纲内容" in t), None)
        if k is None:
            continue
        miss_k = [t for t in opener[k:] if norm(t)[:20] not in norm(allt)]
        flag = "丢失" if miss_k else "完整"
        print(f"  {title:<10} PDF第{page:>3}页  开头 header {len(opener)} 块 -> 考纲部分 {flag}")
        for t in miss_k:
            print(f"       缺: {t[:70]}")
