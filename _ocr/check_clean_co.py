# -*- coding: utf-8 -*-
"""排查清理后残留问题。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机组成原理")

NOISE_TAIL = re.compile(
    r"([。！？；：\)）】])\s+"
    r"(X|K|XTA|XT|KK|KX|XTIT|VI|XK|YTA|XTT|KKK|YT|YAN|FA|LK|L|XV|XTOT|XTO|XI|KN|"
    r"XTON|KIK|KKIN|T|NIT|LIK|XIOT|KKNN|XN|I|KO|XTD|ULK)\s*$")

print("=== 1. 残余行尾噪声 ===")
for fn in sorted(os.listdir(D)):
    if not fn.endswith(".md"):
        continue
    for i, l in enumerate(open(os.path.join(D, fn), encoding="utf-8").read().split("\n")):
        if NOISE_TAIL.search(l.rstrip()):
            print(f"  {fn} L{i}: {l.strip()[-90:]!r}")

print("\n=== 2. 更宽的行尾大写字母残留（任意 1-6 个大写字母结尾）===")
LOOSE = re.compile(r"[。！？；：\)）】]\s+([A-Z]{1,6})\s*$")
for fn in sorted(os.listdir(D)):
    if not fn.endswith(".md"):
        continue
    for i, l in enumerate(open(os.path.join(D, fn), encoding="utf-8").read().split("\n")):
        m = LOOSE.search(l.rstrip())
        if m:
            print(f"  [{m.group(1)}] {fn} L{i}: {l.strip()[-80:]!r}")

print("\n=== 3. 考点追踪 修复情况 ===")
for fn in ("第1章 计算机系统概述.md", "第2章 数据的表示和运算.md"):
    t = open(os.path.join(D, fn), encoding="utf-8").read()
    for m in re.finditer(r".{0,40}(基西面题|通高面瓣|考点追踪CPU执行时间|考点追踪数据的大小端).{0,40}", t):
        print(f"  {fn}: {m.group(0)!r}")
    print(f"  {fn}: 考点追踪 共 {t.count('考点追踪')} 处")

print("\n=== 4. 公式规范化抽查（对比原始）===")
orig = open(os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md"),
            encoding="utf-8").read()
cur = open(os.path.join(D, "第2章 数据的表示和运算.md"), encoding="utf-8").read()
import itertools
for o, c in itertools.islice(
        ((o, c) for o, c in zip(
            re.findall(r"\$[^$\n]{5,80}\$", orig),
            re.findall(r"\$[^$\n]{5,80}\$", cur))), 12):
    flag = "  同" if o == c else "改→"
    print(f"  {flag} {o[:70]}")
    if o != c:
        print(f"       {c[:70]}")
