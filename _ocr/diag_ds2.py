# -*- coding: utf-8 -*-
"""查数据的 structures：选项异常上下文 + $$ 失衡位置。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '数据结构')
files = {f: open(os.path.join(D, f), encoding="utf-8").read()
         for f in sorted(os.listdir(D)) if f.endswith(".md")}

print("=== 1. $$ 失衡文件与定位 ===")
for f, t in files.items():
    if t.count("$$") % 2:
        print(f"  {f}: $$ 共 {t.count('$$')} 次（奇数）")
        pos = [m.start() for m in re.finditer(r"\$\$", t)]
        # 按行看每个 $$ 是否独占一行；找出不成对的那个
        lines = t.split("\n")
        blocks, open_i = [], None
        for i, l in enumerate(lines):
            if l.strip() == "$$":
                if open_i is None:
                    open_i = i
                else:
                    blocks.append((open_i, i))
                    open_i = None
        print(f"  独占一行的 $$ 配成 {len(blocks)} 块，未闭合行={open_i}")
        if open_i is not None:
            for j in range(max(0, open_i - 4), min(open_i + 12, len(lines))):
                print(f"    L{j}: {lines[j][:110]}")
        # 也检查行内出现的 $$
        inline = [i for i, l in enumerate(lines)
                  if "$$" in l and l.strip() != "$$"]
        print(f"  行内出现 $$ 的行: {len(inline)}")
        for i in inline[:6]:
            print(f"    L{i}: {lines[i][:120]}")

print("\n=== 2. A.data 类误判上下文 ===")
for f, t in files.items():
    for i, l in enumerate(t.split("\n")):
        if re.match(r"^[A-D][.．]\s*", l) and re.search(r"[A-D]\.[a-z]", l):
            print(f"  {f} L{i}: {l[:100]}")

print("\n=== 3. 连排两个 ABCD 的上下文 ===")
for f, t in files.items():
    ls = t.split("\n")
    for i in range(len(ls) - 7):
        if all(re.match(r"^[A-D][.．]\s", ls[i + k].strip()) for k in range(8)):
            print(f"  --- {f} L{i} ---")
            for k in range(max(0, i - 3), min(i + 9, len(ls))):
                print(f"    L{k}: {ls[k][:100]}")
            break
