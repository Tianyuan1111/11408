# -*- coding: utf-8 -*-
"""四本最终验收：结构守恒、习题已摘净、图片完整。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统", os.path.join(BOOKDIR, "操作系统"), "_ocr/toc.json"),
    ("数据结构", os.path.join(BOOKDIR, "数据结构"), "_ocr/toc_ds.json"),
    ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理"), "_ocr/toc_co.json"),
    ("计算机网络", os.path.join(BOOKDIR, "计算机网络"), "_ocr/toc_cn.json"),
]
BARE = re.compile(r"^第\d+章$")
EX = re.compile(r"^#{1,4}\s+.*?(本节习题精选|本节试题精选|习题精选|试题精选|答案与解析|本章习题)\s*$")
FENCE = "`" * 3
NOISE = re.compile(r"([。！？；：\)）】])\s+[A-Z]{1,6}\s*$")
KAO = re.compile(r"^#{0,4}\s*\*{0,2}【考纲内容】")

ok_all = True
for name, outdir, toc in BOOKS:
    D = os.path.join(WS, outdir)
    md = [f for f in sorted(os.listdir(D)) if f.endswith(".md")
          and f != "README.md" and not f.startswith("待核对")]
    main = [f for f in md if "习题与解析" not in f]
    exf = [f for f in md if "习题与解析" in f]
    mtext = "\n".join(open(os.path.join(D, f), encoding="utf-8").read() for f in main)
    etext = "\n".join(open(os.path.join(D, f), encoding="utf-8").read() for f in exf)

    lv = Counter({1: len(main)})
    for m in re.finditer(r"^(#{2,6})\s", mtext + "\n" + etext, re.M):
        lv[len(m.group(1))] += 1

    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))
    bms = [{"level": d["level"], "title": " ".join(d["title"].split())} for d in raw]
    bms = [b for b in bms if b["title"] and not BARE.match(b["title"])]
    idx = next(i for i, b in enumerate(bms) if b["title"].startswith("第1章"))
    base = Counter(b["level"] for b in bms[idx:])
    lv_str = " ".join(f"H{k}={lv.get(k,0)}/{base.get(k,0)}" for k in sorted(set(lv) | set(base)))
    ok_lv = all(lv.get(k, 0) == base.get(k, 0) for k in set(lv) | set(base))

    resid_ex = sum(1 for l in mtext.split("\n") if EX.match(l.strip()))
    # 考纲内容：除参考文献外每章都应具备
    chaps = [f for f in main if f.startswith("第")]
    kao_missing = [f for f in chaps
                   if not any(KAO.match(l.strip())
                              for l in open(os.path.join(D, f), encoding="utf-8").read().split("\n"))]

    refs = {os.path.basename(p) for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", mtext + etext)}
    disk = set(os.listdir(os.path.join(D, "images")))
    miss_img = len(refs - disk)

    broken = 0
    for t in [open(os.path.join(D, f), encoding="utf-8").read() for f in md]:
        inf = False
        for l in t.split("\n"):
            if l.strip().startswith(FENCE):
                inf = not inf
                continue
            if inf and re.match(r"^[A-D][.．]\s", l.strip()):
                broken += 1

    resid = (sum(1 for l in (mtext + etext).split("\n") if NOISE.search(l.rstrip()))
             + len(re.findall(r"<!-- page", mtext + etext))
             + (mtext + etext).count("docvortex-page-footnote"))

    ok = ok_lv and resid_ex == 0 and not kao_missing and miss_img == 0 and broken == 0 and resid == 0
    ok_all &= ok
    print(f"### {name}   ({len(main)} 正文 + {len(exf)} 习题)")
    print(f"    层级 {lv_str}   {'OK' if ok_lv else '不一致'}")
    print(f"    正文残留习题标题 {resid_ex} | 缺【考纲内容】的章 {len(kao_missing)} {kao_missing}")
    print(f"    代码块误拆 {broken} | 图片缺失 {miss_img} | 残余噪声 {resid}")
    print(f"    {'✓ 通过' if ok else '✗ 有问题'}")
    print()

print("总体:", "四本全部通过" if ok_all else "存在问题")
