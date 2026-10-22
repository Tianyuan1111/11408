# -*- coding: utf-8 -*-
"""
把《操作系统》清理版里的习题摘成独立文件。

习题在书中以 H3 标题成对出现：`### X.Y.Z 本节习题精选` 与 `### X.Y.Z 答案与解析`，
区块范围到下一个 H2/H3 标题为止（其下的 `#### 单项选择题` 等属于该区块）。

产物：同目录下 `第N章 习题与解析.md`；正文文件里这些区块完全移除。
幂等：若某章已无习题区块，则跳过、不覆盖既有文件。
"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '操作系统')
EX_RE = re.compile(r"^###\s+.*?(本节习题精选|习题精选|答案与解析|本章习题)\s*$")
HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
H23 = re.compile(r"^#{2,3}\s")

files = [f for f in sorted(os.listdir(D))
         if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")]
src_files = [f for f in files if f.startswith("第") and "习题与解析" not in f]

report = []
for f in src_files:
    p = os.path.join(D, f)
    lines = open(p, encoding="utf-8").read().split("\n")
    orig_chars = sum(len(l) for l in lines)

    # 区块范围
    ranges = []
    for i, l in enumerate(lines):
        if EX_RE.match(l.strip()):
            j = i + 1
            while j < len(lines) and not H23.match(lines[j]):
                j += 1
            ranges.append((i, j))

    if not ranges:
        print(f"  {f}: 无习题区块，跳过")
        continue

    # 合并相邻/重叠区间
    merged = []
    for a, b in ranges:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))

    ex_lines, main_lines = [], []
    k = 0
    for a, b in merged:
        main_lines.extend(lines[k:a])
        ex_lines.extend(lines[a:b])
        ex_lines.append("")
        k = b
    main_lines.extend(lines[k:])

    ex_chars = sum(len(l) for l in ex_lines)
    main_chars = sum(len(l) for l in main_lines)

    # 正文：压缩因移除产生的多余空行
    main_text = re.sub(r"\n{3,}", "\n\n", "\n".join(main_lines)).rstrip() + "\n"
    open(p, "w", encoding="utf-8").write(main_text)

    # 习题文件
    m = HEAD.match(lines[0])
    chap_title = m.group(2).strip() if m else f[:-3]
    ex_title = f"{chap_title} · 习题与解析"
    ex_text = (f"# {ex_title}\n\n"
               f"> 由《{chap_title}》正文摘出；区块标题保留了原书的小节编号。\n\n"
               + re.sub(r"\n{3,}", "\n\n", "\n".join(ex_lines)).strip() + "\n")
    ex_name = f"{f.split()[0]} 习题与解析.md"
    open(os.path.join(D, ex_name), "w", encoding="utf-8").write(ex_text)

    report.append((f, ex_name, orig_chars, main_chars, len(ex_text), len(merged)))
    print(f"  {f}: {orig_chars} -> 正文 {main_chars} 字符（-{(orig_chars-main_chars)*100//orig_chars}%）"
          f"，{ex_name} {len(ex_text)} 字符，摘出 {len(merged)} 个区块")

# 复核：正文里不应再有习题标题
print("\n=== 复核 ===")
left = 0
for f in src_files:
    t = open(os.path.join(D, f), encoding="utf-8").read()
    for l in t.split("\n"):
        if EX_RE.match(l.strip()):
            left += 1
            print(f"  !! 残留: {f}: {l[:70]}")
print(f"  正文残留习题标题: {left}")
tot_orig = sum(r[2] for r in report)
tot_main = sum(r[3] for r in report)
tot_ex = sum(r[4] for r in report)
print(f"  合计原文 {tot_orig} 字符 -> 正文 {tot_main} + 习题文件 {tot_ex} = {tot_main+tot_ex}")
print(f"  正文减少 {tot_orig-tot_main} 字符（{(tot_orig-tot_main)*100//tot_orig}%）")
