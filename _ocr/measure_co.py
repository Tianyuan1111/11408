# -*- coding: utf-8 -*-
"""精确测量各类问题，为清理规则提供依据。"""
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

print("=== 1. 反复出现的水印行 ===")
c = Counter(l.strip() for l in lines if l.strip())
for pat in ["官方开源", "bilibili", "王道在线", "考研小舟", "扫码", "微信", "兑换码",
            "免费发布在B站", "小程序", "盗版", "淘宝", "taobao"]:
    tot = sum(1 for l in lines if pat in l)
    if tot:
        print(f"  「{pat}」 出现 {tot} 次")
        for l in lines:
            if pat in l:
                print(f"       {l.strip()[:120]}")
                break

print("\n=== 2. 正文噪点标记 ===")
for pat in ["视频讲解", "官方开源"]:
    idx = [i for i, l in enumerate(lines) if l.strip() == pat or (pat in l and len(l.strip()) < 90)]
    print(f"  「{pat}」 独立成行的次数: {len(idx)}  行号示例: {idx[:10]}")

print("\n=== 3. 选择题选项挤在一行（A. … B. … C. … D. …）===")
merged = []
for i, l in enumerate(lines):
    s = l.strip()
    if re.search(r"(^|\s)A[.、]", s) and re.search(r"\sB[.、]", s) and re.search(r"\sC[.、]", s):
        merged.append(i)
print(f"  共 {len(merged)} 行")
for i in merged[:6]:
    print(f"    L{i}: {lines[i].strip()[:150]}")

print("\n=== 4. 公式内被空格拆散的数字（如 1 0 ^ { 6 }）===")
bad_math = []
MATHSPLIT = re.compile(r"(?:\d\s+){1,}\d\s*\^|\d\s+\d\s+\d")
for i, l in enumerate(lines):
    if "$" in l and MATHSPLIT.search(l):
        bad_math.append(i)
print(f"  含疑似拆散数字的行: {len(bad_math)}")
for i in bad_math[:6]:
    print(f"    L{i}: {lines[i].strip()[:150]}")

print("\n=== 5. 脚注 HTML ===")
fn = [i for i, l in enumerate(lines) if "docvortex-page-footnote" in l]
print(f"  共 {len(fn)} 行；示例:")
for i in fn[:3]:
    print(f"    L{i}: {lines[i].strip()[:170]}")

print("\n=== 6. 章节边界（H1）与页范围 ===")
PAGE = re.compile(r"<!-- page (\d+) of (\d+) -->")
cur = 0
page_at = {}
for i, l in enumerate(lines):
    m = PAGE.match(l.strip())
    if m:
        cur = int(m.group(1))
    page_at[i] = cur
for i, l in enumerate(lines):
    if re.match(r"^# ", l):
        print(f"  L{i:>6}  PDF第{page_at[i]:>3}页  {l.strip('# ').strip()}")

print("\n=== 7. 其它可疑残留 ===")
for pat, label in [(r"XT\b|XTA|XT$", "行尾 XT 噪声"), (r"[KKS]T$", "行尾字母噪声"),
                   (r"\bMFL|FLOPS", "正常术语(对照)")]:
    hits = [i for i, l in enumerate(lines) if re.search(pat, l.strip())]
    print(f"  {label}: {len(hits)} 行  例: {[lines[i].strip()[-40:] for i in hits[:3]]}")
