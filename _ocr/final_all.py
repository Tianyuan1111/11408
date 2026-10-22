# -*- coding: utf-8 -*-
"""四本清理版最终统一验收。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统",     os.path.join(BOOKDIR, "操作系统"),     "_ocr/toc.json"),
    ("数据结构",     os.path.join(BOOKDIR, "数据结构"),     "_ocr/toc_ds.json"),
    ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理"), "_ocr/toc_co.json"),
    ("计算机网络",   os.path.join(BOOKDIR, "计算机网络"),   "_ocr/toc_cn.json"),
]
BARE = re.compile(r"^第\d+章$")
OPT = re.compile(r"^([A-D])[.．]\s")
NOISE = re.compile(r"([。！？；：\)）】])\s+[A-Z]{1,6}\s*$")
FENCE = "`" * 3

all_ok = True
print(f"{'书名':<10} {'层级(输出/书签)':<40} {'选项块':<8} {'代码误拆':<8} {'图':<8} {'残余'}")
print("-" * 108)
for name, outdir, toc in BOOKS:
    D = os.path.join(WS, outdir)
    files = {f: open(os.path.join(D, f), encoding="utf-8").read()
             for f in sorted(os.listdir(D))
             if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")}
    allt = "\n".join(files.values())

    lv = Counter({1: len(files)})
    for m in re.finditer(r"^(#{2,6})\s", allt, re.M):
        lv[len(m.group(1))] += 1

    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))
    bms = [{"level": d["level"], "title": " ".join(d["title"].split())} for d in raw]
    bms = [b for b in bms if b["title"] and not BARE.match(b["title"])]
    idx = next(i for i, b in enumerate(bms) if b["title"].startswith("第1章"))
    base = Counter(b["level"] for b in bms[idx:])

    lv_str = " ".join(f"H{k}={lv.get(k,0)}/{base.get(k,0)}" for k in sorted(set(lv) | set(base)))
    ok_lv = all(lv.get(k, 0) == base.get(k, 0) for k in set(lv) | set(base))

    # 选项块
    lines = [(f, l) for f, t in files.items() for l in t.split("\n")]
    i, blocks, bad = 0, 0, 0
    while i < len(lines):
        if OPT.match(lines[i][1]):
            seq, j = [], i
            while j < len(lines) and OPT.match(lines[j][1]):
                seq.append(OPT.match(lines[j][1]).group(1)); j += 1
            blocks += 1
            if seq != sorted(seq) or len(seq) < 2:
                bad += 1
            i = j
        else:
            i += 1

    # 代码块内误拆
    broken = 0
    for t in files.values():
        inf = False
        for l in t.split("\n"):
            if l.strip().startswith(FENCE):
                inf = not inf
                continue
            if inf and OPT.match(l.strip()):
                broken += 1

    imgs = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", allt))
    refs = {os.path.basename(p) for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", allt)}
    disk = set(os.listdir(os.path.join(D, "images")))
    miss = len(refs - disk)
    resid = (sum(1 for l in allt.split("\n") if NOISE.search(l.rstrip()))
             + len(re.findall(r"<!-- page", allt))
             + allt.count("docvortex-page-footnote")
             + sum(allt.count(w) for w in ["官方开源", "bilibili", "考研小舟", "包邮", "taobao", "视频讲解"]))

    ok = ok_lv and broken == 0 and miss == 0 and resid == 0
    all_ok &= ok
    print(f"{name:<10} {lv_str:<40} {blocks}(异常{bad})".ljust(20)
          + f"{broken:<8} {imgs}/{miss:<6} {resid}")

print("-" * 108)
print("总体:", "四本全部通过" if all_ok else "存在问题")
