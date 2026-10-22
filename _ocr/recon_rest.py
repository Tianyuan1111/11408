# -*- coding: utf-8 -*-
"""对三本书各自实测问题分布（规则必须按本测量，不能照搬）。"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统",   os.path.join(WORKDIR, "操作系统_Markdown"),     "王道操作系统.md"),
    ("数据结构",   os.path.join(WORKDIR, "数据结构_Markdown"),     "王道数据结构.md"),
    ("计算机网络", os.path.join(WORKDIR, "计算机网络_Markdown"),   "王道计算机网络.md"),
]

CHAP = re.compile(r"^# (第\d+章.*|参考文献.*)$")
CJK_OR_ALNUM = re.compile(r"[\u4e00-\u9fff0-9A-Za-z]")
SENT = r"。！？；：\)）】"
NOISE_END = re.compile(rf"([{SENT}])\s+([A-Z]{{1,6}})\s*$")
NOISE_MID = re.compile(rf"([{SENT}])\s+([A-Z]{{1,6}})\s+(?=[A-D][.．]\s)")
FOOTNOTE = re.compile(r"docvortex-page-footnote")
PAGE = re.compile(r"^<!-- page \d+ of \d+ -->$")
OPT_ANY = re.compile(r"[A-D][.．]\s*")
OPT_SPACED = re.compile(r"[A-D][.．]\s+\S.*?\s+[A-D][.．]\s")
MATH_SPLIT = re.compile(r"\$[^$\n]*?(?:\d\s+){1,}\d\s*\^|\$[^$\n]*?\d\s+\d\s+\d")
LETTER_SPLIT = re.compile(r"\$[^$\n]*?(?:[A-Za-z] ){3,}[A-Za-z]")
ROMAN = re.compile(r"[ⅠⅡⅢⅣ][ⅠI]|I{4,}")

for name, outdir, mdfile in BOOKS:
    p = os.path.join(WS, outdir, mdfile)
    text = open(p, encoding="utf-8").read()
    lines = text.split("\n")
    print("=" * 78)
    print(f"### {name}  ({len(lines)} 行, {len(text)} 字符)")
    print("=" * 78)

    h1 = [(i, l.strip()[2:].strip()) for i, l in enumerate(lines) if re.match(r"^# ", l)]
    first = next((i for i, t in h1 if CHAP.match("# " + t)), None)
    print(f"一级标题 {len(h1)} 个：")
    for i, t in h1:
        mark = "  <- 正文起点" if i == first else ""
        print(f"    L{i:>6}  {t}{mark}")
    print(f"前置页需删除: L0-L{first-1}（{first} 行）")

    print(f"\n  页标记 {sum(1 for l in lines if PAGE.match(l.strip()))}")
    print(f"  脚注HTML {sum(1 for l in lines if FOOTNOTE.search(l))}")
    print(f"  行尾噪声 {sum(1 for l in lines if NOISE_END.search(l.rstrip()))}")
    print(f"  行中噪声 {sum(1 for l in lines if NOISE_MID.search(l))}")
    print(f"  含选项标记的行 {sum(1 for l in lines if OPT_ANY.search(l))}")
    print(f"  选项挤行(含2个以上) {sum(1 for l in lines if OPT_SPACED.search(l))}")
    print(f"  公式内拆散数字 {sum(1 for l in lines if MATH_SPLIT.search(l))}")
    print(f"  公式内逐字空格 {sum(1 for l in lines if LETTER_SPLIT.search(l))}")
    print(f"  罗马数字可疑 {sum(1 for l in lines if ROMAN.search(l))}")

    toks = Counter(m.group(2) for l in lines if (m := NOISE_END.search(l.rstrip())))
    print(f"  行尾噪声 token: " + ", ".join(f"{t}×{n}" for t, n in toks.most_common()))

    print(f"\n  水印/广告关键词命中：")
    for kw in ["官方开源", "bilibili", "王道在线", "考研小舟", "包邮", "taobao",
               "视频讲解", "扫码", "微信", "兑换码", "小程序", "盗版", "训练营",
               "公众号", "客服", "知乎", "版权所有", "侵权"]:
        n = sum(1 for l in lines if kw in l)
        if n:
            ex = next(l.strip()[:80] for l in lines if kw in l)
            print(f"    {kw:<8} {n:>3}  {ex}")
    print()
