# -*- coding: utf-8 -*-
"""v3 复核：选项拆分是否过度、残余逐字空格、整体结构。"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机组成原理")
SRC = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
files = {f: open(os.path.join(D, f), encoding="utf-8").read()
         for f in sorted(os.listdir(D)) if f.endswith(".md")}
allt = "\n".join(files.values())

print("=== 1. 选项块完整性：A→B→C(→D) 是否齐全 ===")
lines_all = [(fn, l) for fn, t in files.items() for l in t.split("\n")]
i, blocks, bad = 0, 0, []
while i < len(lines_all):
    if re.match(r"^A[.、]\s", lines_all[i][1]):
        seq = []
        j = i
        while j < len(lines_all) and re.match(r"^[A-D][.、]\s", lines_all[j][1]):
            seq.append(lines_all[j][1][0])
            j += 1
        blocks += 1
        if seq != sorted(seq) or len(seq) < 2 or seq[0] != "A":
            bad.append((lines_all[i][0], i, seq, lines_all[i][1][:60]))
        i = j
    else:
        i += 1
print(f"  识别到选项块 {blocks} 个；异常 {len(bad)} 个")
for fn, idx, seq, t in bad[:10]:
    print(f"    {fn} {seq}: {t}")

print("\n=== 2. 拆出的选项内容异常短的（<3 字符，可能误拆）===")
short = [(fn, l) for fn, l in lines_all
         if re.match(r"^[A-D][.、]\s", l) and len(l.strip()) < 5]
print(f"  共 {len(short)} 个")
for fn, l in short[:12]:
    print(f"    {fn}: {l!r}")

print("\n=== 3. 被拆行的题干过短（<12 字符，疑似误拆）===")
for fn, t in files.items():
    ls = t.split("\n")
    for k, l in enumerate(ls):
        if re.match(r"^A[.、]\s", l) and k > 0:
            stem = ls[k - 1].strip()
            if stem and not re.match(r"^[A-D][.、]", stem) and 0 < len(stem) < 12:
                print(f"    {fn} L{k-1}: {stem!r}")

print("\n=== 4. 残余逐字空格 ===")
for m in re.finditer(r".{0,50}(?:[A-Za-z] ){3,}.{0,30}", allt):
    print(f"    {m.group(0)!r}")

print("\n=== 5. 结构总览 ===")
tot_img = 0
for fn, t in files.items():
    lv = Counter(len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s", t, re.M))
    imgs = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", t))
    tot_img += imgs
    dollar = t.count("$$")
    print(f"  {fn:<26} 字符{len(t):>7} 标题{dict(sorted(lv.items()))} 图{imgs:>3} "
          f"$${dollar:>3}{'(不平衡!)' if dollar % 2 else ''} 表格{t.count('<table'):>2}")

print(f"\n  图片引用合计 {tot_img}")
disk = os.listdir(os.path.join(D, "images"))
print(f"  磁盘图片 {len(disk)}")
refs = {os.path.basename(p) for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", allt)}
print(f"  引用集合 {len(refs)}  缺失 {len(refs - set(disk))}  多余 {len(set(disk) - refs)}")

print("\n=== 6. 关键修复点确认 ===")
print(f"  考点追踪 总出现: {allt.count('考点追踪')}")
print(f"  乱码残留(基西面题/通高面瓣): {allt.count('基西面题') + allt.count('通高面瓣')}")
print(f"  含『考点追踪CPU执行时间』: {'考点追踪CPU执行时间的相关计算' in allt}")
print(f"  含『考点追踪数据的大小端存储』: {'考点追踪数据的大小端存储' in allt}")

print("\n=== 7. 抽查一个完整的习题+答案片段（第1章）===")
t = files["第1章 计算机系统概述.md"]
ls = t.split("\n")
k = next(i for i, l in enumerate(ls) if re.match(r"^A[.、]\s", l))
for j in range(max(0, k - 3), min(k + 12, len(ls))):
    print(f"  L{j}: {ls[j][:96]}")
