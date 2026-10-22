# -*- coding: utf-8 -*-
"""侦察三本书的习题/答案标题形式（不能照搬操作系统的规则）。"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [("数据结构", os.path.join(BOOKDIR, "数据结构")),
         ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理")),
         ("计算机网络", os.path.join(BOOKDIR, "计算机网络"))]

HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
# 所有可能相关的标题
CAND = re.compile(r"习题|试题|答案|解析|综合应用|单项选择|多项选择|填空|判断|练习")
# 操作系统用的规则（对照组）
OS_RULE = re.compile(r"^###\s+.*?(本节习题精选|习题精选|答案与解析|本章习题)\s*$")

for name, d in BOOKS:
    D = os.path.join(WS, d)
    files = [f for f in sorted(os.listdir(D))
             if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")]
    print("=" * 78)
    print(f"### {name}   （{len(files)} 个文件）")
    print("=" * 78)
    all_cand = Counter()
    osrule = Counter()
    for f in files:
        lines = open(os.path.join(D, f), encoding="utf-8").read().split("\n")
        hits = []
        for i, l in enumerate(lines):
            m = HEAD.match(l)
            if not m:
                continue
            lvl, t = len(m.group(1)), m.group(2).strip()
            if CAND.search(t):
                hits.append((i, lvl, t))
                all_cand[t] += 1
                if OS_RULE.match(l):
                    osrule[t] += 1
        if hits:
            print(f"\n--- {f} ---")
            for i, lvl, t in hits:
                mark = "OS规则命中" if OS_RULE.match(lines[i]) else ("  ·" if lvl >= 4 else "!! 需确认")
                print(f"  L{i:>5} {'#'*lvl:<6} {t[:66]:<68} {mark}")
    print(f"\n  >>> {name}: 候选标题 {sum(all_cand.values())} 个，其中 OS 规则可命中 {sum(osrule.values())} 个")
    print(f"  >>> 未被 OS 规则覆盖的标题种类:")
    for t, n in all_cand.most_common():
        if t not in osrule:
            print(f"        {n:>3}x {t[:70]}")
    print()
