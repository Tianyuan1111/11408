# -*- coding: utf-8 -*-
"""系统排查：各章文件末尾是否残留下一章的内容（章标题被插到自己考纲内容之后）。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [("操作系统", os.path.join(BOOKDIR, "操作系统")), ("数据结构", os.path.join(BOOKDIR, "数据结构")),
         ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理")), ("计算机网络", os.path.join(BOOKDIR, "计算机网络"))]
# 章标题残片（被降级为粗体的章号/章名）
FRAG = re.compile(r"^\*\*\s*第\s*\d*\s*章")
KAO = re.compile(r"^#{0,4}\s*\*{0,2}【考纲内容】")

for name, outdir in BOOKS:
    D = os.path.join(WS, outdir)
    files = [f for f in sorted(os.listdir(D)) if f.endswith(".md")
             and f != "README.md" and not f.startswith("待核对") and "习题" not in f]
    print(f"\n### {name}")
    any_issue = False
    for f in files:
        ls = open(os.path.join(D, f), encoding="utf-8").read().split("\n")
        issues = []
        for i, l in enumerate(ls):
            s = l.strip()
            if FRAG.match(s):
                issues.append((i, "章标题残片", s[:60]))
            if KAO.match(s) and i > 12:
                issues.append((i, "考纲内容非首位", s[:60]))
        # 末尾 12 行里是否有下一章特征
        tail = [(len(ls) - 12 + k, ls[len(ls) - 12 + k].strip())
                for k in range(12) if len(ls) - 12 + k >= 0]
        for i, s in tail:
            if re.match(r"^\*\*\s*第\s*\d+\s*章", s) and "·" not in s:
                issues.append((i, "末尾章标题残片", s[:60]))
        if issues:
            any_issue = True
            print(f"  {f}:")
            for i, kind, s in issues[:6]:
                print(f"      L{i:>5} [{kind}] {s}")
    if not any_issue:
        print("  未发现错位")
