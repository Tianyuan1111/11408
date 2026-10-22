# -*- coding: utf-8 -*-
"""严谨侦察：正确统计格式问题，并输出前置页原文以便判断广告范围。"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
MD = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
lines = open(MD, encoding="utf-8").read().split("\n")

BOLD = re.compile(r"^\*\*.+\*\*$")
PAGE = re.compile(r"^<!-- page \d+ of \d+ -->$")
IMG = re.compile(r"^!\[[^\]]*\]\([^)]+\)$")
HAN = re.compile(r"[\u4e00-\u9fff]")
ALNUM = re.compile(r"[0-9A-Za-z]")
CJK_OR_ALNUM = re.compile(r"[\u4e00-\u9fff0-9A-Za-z]")
SPACES3 = re.compile(r"\S {3,}\S")
HTMLTAG = re.compile(r"</?[a-zA-Z][^>]*>")

stats = Counter()
for l in lines:
    s = l.strip()
    if not s:
        stats["空行"] += 1
        continue
    if PAGE.match(s):
        stats["页标记"] += 1
    elif IMG.match(s):
        stats["纯图片行"] += 1
    elif BOLD.match(s):
        stats["加粗行"] += 1
    elif s.startswith("#"):
        stats["标题"] += 1
    elif s in ("$$", "```"):
        stats["围栏"] += 1
    elif s.startswith("|"):
        stats["表格行"] += 1
    elif not CJK_OR_ALNUM.search(s):
        stats["疑似纯符号行"] += 1
    else:
        stats["正文行"] += 1

print("=== 行类型统计（共 %d 行）===" % len(lines))
for k, v in stats.most_common():
    print(f"  {k:<12} {v}")

print("\n=== 疑似纯符号行 示例（最多 25）===")
n = 0
for i, l in enumerate(lines):
    s = l.strip()
    if s and not CJK_OR_ALNUM.search(s) and not PAGE.match(s) and not IMG.match(s):
        print(f"  L{i:>6}: {s[:90]!r}")
        n += 1
        if n >= 25:
            break

print("\n=== 连续 3 空格以上的行 示例（最多 15）===")
n = 0
for i, l in enumerate(lines):
    if SPACES3.search(l):
        print(f"  L{i:>6}: {l.strip()[:110]!r}")
        n += 1
        if n >= 15:
            break

print("\n=== 内嵌 HTML 标签的行（非 table）===")
n = 0
for i, l in enumerate(lines):
    if HTMLTAG.search(l) and "<table" not in l:
        print(f"  L{i:>6}: {l.strip()[:130]}")
        n += 1
        if n >= 12:
            break

print("\n=== 前置页（L0-L280）原文 ===")
for i in range(0, 281):
    s = lines[i]
    print(f"{i:>4}| {s[:150]}")
