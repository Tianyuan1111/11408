# -*- coding: utf-8 -*-
"""撤销 fix_kaogang.py 的插入（重算被插入的行，从其出现位置精确移除）。"""
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


def inserted_lines(sc, page, text):
    """重算 fix_kaogang 当时插入的行。"""
    opener = None
    for idx in (page - 1, page, page - 2):
        if idx < 0 or idx >= len(sc["pages"]):
            continue
        seq = []
        for b in sc["pages"][idx]["blocks"]:
            tp = b.get("type")
            if tp in SKIP:
                continue
            if tp == "header":
                t = btext(b).strip()
                if t:
                    seq.append(t)
                continue
            break
        if any("考纲内容" in t for t in seq):
            opener = seq
            break
    if not opener:
        return []
    k = next(i for i, t in enumerate(opener) if "考纲内容" in t)
    ntext = norm(text)
    miss = [t for t in opener[k:] if norm(t)[:14] and norm(t)[:14] not in ntext]
    # 注意：这里要用"插入前"的文本判断，故调用方传原始文本
    return [f"**{t}**" if "考纲内容" in t else t for t in miss]


total = 0
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

    print(f"\n### {name}")
    for num, page in chaps:
        f = next((x for x in os.listdir(D) if x.startswith(num) and x.endswith(".md")
                  and "习题" not in x), None)
        if not f:
            continue
        p = os.path.join(D, f)
        ls = open(p, encoding="utf-8").read().split("\n")

        # 重算：把"插入后"的文本去掉插入行后再判断，做法是逐条在文件头部查找
        # 直接扫描前 12 行，找出与 structured_content 某条 opener 文本完全相同的行
        idxs = (page - 1, page, page - 2)
        seqs = []
        for idx in idxs:
            if 0 <= idx < len(sc["pages"]):
                s2 = []
                for b in sc["pages"][idx]["blocks"]:
                    tp = b.get("type")
                    if tp in SKIP:
                        continue
                    if tp == "header":
                        t = btext(b).strip()
                        if t:
                            s2.append(t)
                        continue
                    break
                if any("考纲内容" in t for t in s2):
                    seqs.append(s2)
        if not seqs:
            continue
        seq = seqs[0]
        k = next(i for i, t in enumerate(seq) if "考纲内容" in t)
        cand = {f"**{t}**" if "考纲内容" in t else t for t in seq[k:]}

        # 在前 12 行内移除属于 cand 的行（含其后紧跟的一个空行）
        removed = []
        out, i = [], 0
        while i < len(ls):
            if i < 12 and ls[i] in cand:
                removed.append(ls[i])
                i += 1
                if i < len(ls) and not ls[i].strip():
                    i += 1
                continue
            out.append(ls[i])
            i += 1
        if removed:
            open(p, "w", encoding="utf-8").write("\n".join(out))
            total += 1
            print(f"  {num:<6} 已撤销 {len(removed)} 行: " + " | ".join(x[:24] for x in removed))

print(f"\n共撤销 {total} 章")
