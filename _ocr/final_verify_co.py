# -*- coding: utf-8 -*-
"""最终验收：选项块完整性、已知残留、结构守恒、内容抽样。"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机组成原理")
files = {f: open(os.path.join(D, f), encoding="utf-8").read()
         for f in sorted(os.listdir(D)) if f.endswith(".md")}
allt = "\n".join(files.values())
all_lines = [(fn, l) for fn, t in files.items() for l in t.split("\n")]

OPT = re.compile(r"^([A-D])[.．]\s")

print("=== 1. 选项块完整性 ===")
i, blocks, bad = 0, 0, []
while i < len(all_lines):
    if OPT.match(all_lines[i][1]):
        seq, j = [], i
        while j < len(all_lines) and OPT.match(all_lines[j][1]):
            seq.append(OPT.match(all_lines[j][1]).group(1))
            j += 1
        blocks += 1
        if seq != sorted(seq) or len(seq) < 2:
            bad.append((all_lines[i][0], seq, all_lines[i][1][:70]))
        i = j
    else:
        i += 1
print(f"  选项块 {blocks} 个，异常 {len(bad)} 个")
for fn, seq, t in bad[:12]:
    print(f"    {fn} {seq}: {t}")

print("\n=== 2. 原先被误伤的 USB 那一题 ===")
t6 = files["第6章 总线.md"]
k = t6.find("均为总线标准的是")
for l in t6[k:k + 320].split("\n")[:8]:
    print(f"    {l[:100]}")

print("\n=== 3. 罗马数字乱码残留（转义为 ASCII 便于看）===")
ROMAN = re.compile(r"[ⅠⅡⅢⅣⅤ]+")
hits = [(fn, l) for fn, l in all_lines if ROMAN.search(l)]
print(f"  含全角罗马数字的行: {len(hits)}")
for fn, l in hits[:10]:
    print(f"    {fn}: {l[:95]}")

print("\n=== 4. 结构守恒（应与全书书签统计一致）===")
tot = Counter()
for fn, t in files.items():
    lv = Counter(len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s", t, re.M))
    tot.update(lv)
    print(f"  {fn:<26} {dict(sorted(lv.items()))}")
print(f"  合计 H1={tot[1]} H2={tot[2]} H3={tot[3]}   "
      f"（书签基准 L1=8 L2=42 L3=154）")

print("\n=== 5. 质量指标 ===")
print(f"  字符总数        {len(allt)}")
print(f"  残余页标记      {len(re.findall(r'<!-- page', allt))}")
print(f"  残余水印词      {sum(allt.count(w) for w in ['官方开源','bilibili','考研小舟','包邮','taobao','视频讲解'])}")
print(f"  残余脚注HTML    {allt.count('docvortex-page-footnote')}")
print(f"  残余 $$ 失衡     {sum(1 for f,t in files.items() if t.count('$$')%2)}")
print(f"  图片引用/磁盘   {len(re.findall(r'!\[\]\(', allt))} / {len(os.listdir(os.path.join(D,'images')))}")
print(f"  表格 <table>    {allt.count('<table')}")

print("\n=== 6. 正文抽样（第4章开头 25 行）===")
t4 = files["第4章 指令系统.md"].split("\n")
for l in t4[:25]:
    print(f"    {l[:100]}")
