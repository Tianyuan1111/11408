# -*- coding: utf-8 -*-
"""清理后复核：残余噪声、字母被空格拆散、选项拆分质量、章节结构。"""
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

NOISE_TAIL = re.compile(r"([。！？；：\)）】])\s+([A-Z]{1,6})\s*$")
files = {f: open(os.path.join(D, f), encoding="utf-8").read()
         for f in sorted(os.listdir(D)) if f.endswith(".md")}

print("=== 1. 残余行尾噪声（8 行）===")
for fn, t in files.items():
    for i, l in enumerate(t.split("\n")):
        if NOISE_TAIL.search(l.rstrip()):
            print(f"  {fn} L{i}: ...{l.strip()[-70:]!r}")

print("\n=== 2. 公式里字母被空格拆散（3 个以上单字母）===")
SPACED = re.compile(r"(?:\b[A-Za-z]\s+){2,}[A-Za-z]\b")
cnt, samples = 0, []
for fn, t in files.items():
    for l in t.split("\n"):
        for m in re.finditer(r"\$[^$\n]+\$", l):
            if SPACED.search(m.group(0)):
                cnt += 1
                if len(samples) < 12:
                    samples.append((fn, m.group(0)[:110]))
print(f"  含此问题的行内公式: {cnt} 处")
for fn, s in samples:
    print(f"    [{fn[:6]}] {s}")

print("\n=== 3. 其中出现在 \\text{} / \\mathtt{} 里的（会真实显示为空格）===")
TEXTBOX = re.compile(r"\\(?:text|mathtt|texttt|mathrm)\s*\{[^{}]*\}")
shown = 0
for fn, t in files.items():
    for m in re.finditer(r"\$[^$\n]+\$", t):
        for tb in TEXTBOX.finditer(m.group(0)):
            inner = tb.group(0)
            letters = re.findall(r"[A-Za-z]", inner)
            spaces = len(re.findall(r"[A-Za-z]\s+[A-Za-z]", inner))
            if spaces >= 3 and len(set(letters)) >= 3:
                print(f"    {inner[:100]}")
                shown += 1
                if shown >= 15:
                    break
        if shown >= 15:
            break
    if shown >= 15:
        break

print("\n=== 4. 选项拆分结果抽查（取 3 处）===")
n = 0
for fn, t in files.items():
    lines = t.split("\n")
    for i, l in enumerate(lines):
        if re.match(r"^A[.、]\s", l) and i > 0:
            print(f"  --- {fn} L{i-1}.. ---")
            for j in range(max(0, i - 1), min(i + 4, len(lines))):
                print(f"    L{j}: {lines[j][:100]}")
            n += 1
            break
    if n >= 3:
        break

print("\n=== 5. 各章节文件结构 ===")
for fn, t in files.items():
    lv = Counter(len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s", t, re.M))
    imgs = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", t))
    print(f"  {fn:<26} 字符{len(t):>7}  标题{dict(sorted(lv.items()))} 图{imgs:>3} "
          f"表格{t.count('<table'):>2} 公式块{t.count('$$')//2:>3}")
