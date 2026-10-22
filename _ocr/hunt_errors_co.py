# -*- coding: utf-8 -*-
"""系统排查识别错误：方括号标记、行尾噪声、可疑乱码。"""
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

print("=== 1. 所有 【…】 标记及其出现次数 ===")
marks = Counter()
for l in lines:
    for m in re.finditer(r"【([^】]{0,25})】", l):
        marks[m.group(1)] += 1
for k, v in marks.most_common(40):
    print(f"  {v:>4}  {k}")

print("\n=== 2. 【…】 中可疑（含非常用字/长度异常）===")
COMMON = set("考点追踪注意例解答案本节小结真题统考补充知识常见问题易混淆知识点复习提示"
             "考纲内容单项选择题综合应用题解析总结误区提示例题")
for k, v in marks.items():
    if not any(c in k for c in "考点追踪注意例解答案节结真题补充常见问题复习提示纲单选综合应用误区"):
        idx = [i for i, l in enumerate(lines) if f"【{k}】" in l][:2]
        print(f"  可疑: 【{k}】 {v} 次  行: {idx}")
        for i in idx:
            print(f"      L{i}: {lines[i].strip()[:150]}")

print("\n=== 3. 行尾 ASCII 噪声（正文行末尾 1-6 个大写字母）===")
TAIL = re.compile(r"([\u4e00-\u9fff。，、；：）】])\s+([A-Z]{1,6})$")
hits = []
for i, l in enumerate(lines):
    s = l.strip()
    if "$" in s or s.startswith("<") or "http" in s:
        continue
    m = TAIL.search(s)
    if m:
        hits.append((i, m.group(1), m.group(2)))
print(f"  共 {len(hits)} 行")
for i, ch, tail in hits[:40]:
    print(f"    L{i:>6}: …{ch!r} + [{tail}]   | {lines[i].strip()[-70:]}")

print("\n=== 4. 出现频率极低的汉字（可能是误识别）===")
CJK = re.compile(r"[\u4e00-\u9fff]")
cnt = Counter(c for l in lines for c in l if CJK.match(c))
rare = [(c, n) for c, n in cnt.items() if n <= 2]
print(f"  只出现 1-2 次的汉字: {len(rare)} 个")
print("   " + " ".join(f"{c}({n})" for c, n in sorted(rare, key=lambda x: x[1])[:80]))

print("\n=== 5. 可疑连接/重复（同一字连续重复、异常搭配）===")
for pat, label in [(r"([\u4e00-\u9fff])\1{2,}", "同字连续>=3"),
                   (r"[a-zA-Z]{6,}", "长英文串")]:
    h = [(i, re.search(pat, l).group(0)) for i, l in enumerate(lines) if re.search(pat, l)]
    print(f"  {label}: {len(h)} 处  例: {[(i, s[:20]) for i, s in h[:8]]}")
