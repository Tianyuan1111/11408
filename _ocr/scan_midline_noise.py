# -*- coding: utf-8 -*-
"""扫描行中噪声（句末标点 + 大写字母串 + 后续内容）。"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SRC = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
lines = open(SRC, encoding="utf-8").read().split("\n")

# 行中：句末标点 + 空格 + 1-6 大写字母 + 空格 + 后面还有内容
MID = re.compile(r"([。！？；：\)）】])\s+([A-Z]{1,6})\s+(?=\S)")
END = re.compile(r"([。！？；：\)）】])\s+([A-Z]{1,6})\s*$")

mid_hits, end_hits = [], []
for i, l in enumerate(lines):
    s = l.rstrip()
    for m in MID.finditer(s):
        # 排除本身就是行尾的那次匹配
        if END.search(s) and END.search(s).start(2) == m.start(2):
            continue
        mid_hits.append((i, m.group(2), s))
    if END.search(s):
        end_hits.append((i, END.search(s).group(2)))

print(f"行尾噪声: {len(end_hits)} 行")
print(f"行中噪声候选: {len(mid_hits)} 处")
print("\n=== 行中噪声明细（token 分布）===")
print("  " + ", ".join(f"{t}×{n}" for t, n in Counter(t for _, t, _ in mid_hits).most_common()))

print("\n=== 行中噪声样例（前 20）===")
for i, t, s in mid_hits[:20]:
    # 显示 token 前后
    pos = s.find(t)
    print(f"  L{i:>6} [{t}] …{s[max(0,pos-45):pos+55]}…")

print("\n=== 行中噪声的 token 是否都在选项标记之前？===")
before_opt = sum(1 for i, t, s in mid_hits
                 if re.search(rf"\)\s+{re.escape(t)}\s+A[.、]\s", s))
print(f"  {before_opt} / {len(mid_hits)} 处紧跟 A. 选项标记")

print("\n=== 行中噪声 token 是否也出现在行尾集合里（佐证同为噪声）===")
end_tokens = {t for _, t in end_hits}
for t in sorted({t for _, t, _ in mid_hits}):
    print(f"  {t:<8} 行尾集合内={t in end_tokens}")
