# -*- coding: utf-8 -*-
"""确认行尾噪声 token 分布，并统计各清理规则的影响面。"""
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

TAIL = re.compile(r"([。！？；：\)）】])\s+([A-Z]{1,6})$")
tokens = Counter()
occ = []
for i, l in enumerate(lines):
    s = l.strip()
    if "$" in s or s.startswith("<") or "http" in s or s.startswith("!"):
        continue
    m = TAIL.search(s)
    if m:
        tokens[m.group(2)] += 1
        occ.append((i, m.group(2)))

print("=== 行尾噪声 token 分布 ===")
for t, n in tokens.most_common():
    print(f"  {t:<8} {n} 次")

print(f"\n总计 {len(occ)} 行命中")
print("\n=== 这些 token 在句中（非行尾）是否也出现？用于判断是否为正常词 ===")
for t in list(tokens)[:12]:
    mid = sum(1 for l in lines if re.search(rf"\b{t}\b", l) and not re.search(rf"\b{t}\s*$", l.strip()))
    print(f"  {t:<8} 句中/非行尾出现 {mid} 次")

print("\n=== 各清理规则影响面 ===")
RULES = {
    "水印行(官方开源/bilibili)": lambda l: "官方开源" in l or "bilibili.com" in l,
    "视频讲解标记": lambda l: l.strip() == "视频讲解",
    "打印店广告": lambda l: "考研小舟" in l or "包邮" in l,
    "脚注HTML": lambda l: "docvortex-page-footnote" in l,
    "行尾ASCII噪声": lambda l: bool(TAIL.search(l.strip())) and "$" not in l and not l.strip().startswith("<"),
    "选项挤行": lambda l: bool(re.search(r"(^|\s)A[.、]", l)) and bool(re.search(r"\sB[.、]", l)) and bool(re.search(r"\sC[.、]", l)),
    "公式内拆散数字": lambda l: "$" in l and bool(re.search(r"(?:\d\s+){1,}\d\s*\^|\d\s+\d\s+\d", l)),
    "空行": lambda l: not l.strip(),
}
for name, fn in RULES.items():
    print(f"  {name:<24} {sum(1 for l in lines if fn(l))} 行")

print("\n=== 噪声 token 出现在哪些页（确认是否集中在页边界）===")
PAGE = re.compile(r"<!-- page (\d+) of (\d+) -->")
cur, pages_of = 0, Counter()
for i, l in enumerate(lines):
    m = PAGE.match(l.strip())
    if m:
        cur = int(m.group(1))
    if TAIL.search(l.strip()) and "$" not in l:
        pages_of[cur] += 1
print(f"  涉及 {len(pages_of)} 个页面；页面分布前 15: {pages_of.most_common(15)}")
