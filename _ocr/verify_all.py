# -*- coding: utf-8 -*-
"""四本书统一验收。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统",     os.path.join(WORKDIR, "操作系统_Markdown"),     "王道操作系统.md",     "_ocr/toc.json"),
    ("数据结构",     os.path.join(WORKDIR, "数据结构_Markdown"),     "王道数据结构.md",     "_ocr/toc_ds.json"),
    ("计算机组成原理", os.path.join(WORKDIR, "计算机组成原理_Markdown"), "王道计算机组成原理.md", "_ocr/toc_co.json"),
    ("计算机网络",   os.path.join(WORKDIR, "计算机网络_Markdown"),   "王道计算机网络.md",   "_ocr/toc_cn.json"),
]
RUNAWAY = re.compile(r"(.)\1{11,}")
BARE = re.compile(r"^第\d+章$")

print(f"{'书名':<10} {'章节层级(输出/书签)':<28} {'页标记':<14} {'图(引用/缺失)':<14} {'表格':<6} {'公式块':<7} {'代码':<6} {'退化'}")
print("-" * 118)

summary = []
for name, outdir, mdfile, toc in BOOKS:
    md = os.path.join(WS, outdir, mdfile)
    if not os.path.exists(md):
        print(f"{name:<10} 缺失")
        continue
    text = open(md, encoding="utf-8").read()
    lines = text.split("\n")
    lv_out = Counter(len(m.group(1)) for l in lines if (m := re.match(r"^(#{1,6})\s", l)))

    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))
    bms = [d for d in raw if " ".join(d["title"].split()) and not BARE.match(" ".join(d["title"].split()))]
    lv_bm = Counter(d["level"] for d in bms)

    lv_str = " ".join(f"H{k}={lv_out.get(k,0)}/{lv_bm.get(k,0)}" for k in sorted(set(lv_out) | set(lv_bm)))
    ok = all(lv_out.get(k, 0) == lv_bm.get(k, 0) for k in set(lv_out) | set(lv_bm))

    marks = re.findall(r"<!-- page (\d+) of (\d+) -->", text)
    pages_ok = len(marks) == int(marks[0][1]) if marks else False
    strict_inc = all(int(b) > int(a) for (a, _), (b, _) in zip(marks, marks[1:]))

    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    idir = os.path.join(WS, outdir, "images")
    disk = set(os.listdir(idir)) if os.path.isdir(idir) else set()
    miss = [os.path.basename(p) for p in imgs if os.path.basename(p) not in disk]

    resid, in_eq = 0, False
    for l in lines:
        if l.strip() == "$$":
            in_eq = not in_eq
            continue
        if in_eq and RUNAWAY.search(l):
            resid += 1

    print(f"{name:<10} {lv_str:<28} {len(marks)}/{marks[0][1] if marks else '?'} {'递增' if strict_inc else '乱序':<6} "
          f"{len(imgs)}/{len(miss):<10} {text.count('<table'):<6} {text.count('$$')//2:<7} "
          f"{text.count('```')//2:<6} {resid}")
    summary.append((name, ok and pages_ok and strict_inc and not miss and resid == 0))

print("-" * 118)
print("总体:", "全部通过" if all(s for _, s in summary) else "有问题")

print("\n=== 各书 H1 标题 ===")
for name, outdir, mdfile, toc in BOOKS:
    md = os.path.join(WS, outdir, mdfile)
    if not os.path.exists(md):
        continue
    h1 = [l for l in open(md, encoding="utf-8").read().split("\n") if re.match(r"^# ", l)]
    print(f"  {name}: {len(h1)} 个 -> {', '.join(h.strip('# ') for h in h1)}")

print("\n=== 数据结构 第 195 页（修复过的那张图）上下文 ===")
md = os.path.join(WORKDIR, "数据结构_Markdown", "王道数据结构.md")
lines = open(md, encoding="utf-8").read().split("\n")
i = next((k for k, l in enumerate(lines) if "page 195 of" in l), None)
if i is not None:
    for j in range(i, min(i + 12, len(lines))):
        print(f"L{j:>6}: {lines[j][:150]}")
