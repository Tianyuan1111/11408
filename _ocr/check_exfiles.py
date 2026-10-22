# -*- coding: utf-8 -*-
"""核对习题文件的内容与结构。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '操作系统')
EX = re.compile(r"^###\s+.*?(本节习题精选|答案与解析)\s*$")

for f in sorted(os.listdir(D)):
    if not f.endswith(".md") or "习题与解析" not in f:
        continue
    t = open(os.path.join(D, f), encoding="utf-8").read()
    ls = t.split("\n")
    heads = [l for l in ls if re.match(r"^#{1,6}\s", l)]
    blocks = [l for l in ls if EX.match(l.strip())]
    print(f"=== {f} ===")
    print(f"  {len(t)} 字符，{len(ls)} 行；标题 {len(heads)} 个，其中习题/答案区块标题 {len(blocks)} 个")
    print("  前 12 行:")
    for l in ls[:12]:
        if l.strip():
            print(f"    {l[:100]}")
    print("  区块标题一览:")
    for b in blocks:
        print(f"    {b.strip()[:80]}")
    print()

print("=== 正文文件开头（确认没有习题痕迹、内容衔接正常）===")
for f in ["第1章 计算机系统概述.md"]:
    ls = open(os.path.join(D, f), encoding="utf-8").read().split("\n")
    print(f"--- {f} 前 10 行 ---")
    for l in ls[:10]:
        if l.strip():
            print(f"    {l[:100]}")
    # 找 1.1.4 前后
    i = next((k for k, l in enumerate(ls) if "1.1.3" in l), None)
    if i:
        print(f"--- 原 1.1.4 习题位置附近（现应直接接 1.2）---")
        for j in range(i, min(i + 14, len(ls))):
            if ls[j].strip():
                print(f"    {ls[j][:100]}")
