# -*- coding: utf-8 -*-
"""定点修复：把计算机网络第1章末尾误挂的第2章考纲内容搬到第2章开头。"""
import os, re, sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

D = os.path.join(BOOKDIR, '计算机网络')
P1 = os.path.join(D, "第1章 计算机网络体系结构.md")
P2 = os.path.join(D, "第2章 物理层.md")

ls1 = open(P1, encoding="utf-8").read().split("\n")
# 定位末尾的 章标题残片
i = next((k for k, l in enumerate(ls1) if re.match(r"^\*\*\s*第\s*2\s*章", l.strip())), None)
assert i is not None, "未找到第2章残片"
print("第1章末尾待移除区域:")
for k in range(i, min(i + 8, len(ls1))):
    print(f"  L{k}: {ls1[k]!r}")

# 收集需要搬运的行：**第2章 第** / **物理层** 是章标题残片（丢弃），
# 【考纲内容】 与 （一）通信基础 需要搬到第2章
moved = [l for l in ls1[i:i + 8] if re.match(r"^#{0,4}\s*\*{0,2}【考纲内容】", l.strip())
         or l.strip().startswith("（一）")]
print("搬运行:", moved)

# 从第1章删除该区域（含随后的空行）
j = i
while j < len(ls1) and (not ls1[j].strip() or j < i + 8):
    if j >= i + 8:
        break
    j += 1
ls1_new = ls1[:i] + ls1[j:]
open(P1, "w", encoding="utf-8").write(re.sub(r"\n{3,}", "\n\n", "\n".join(ls1_new)).rstrip() + "\n")

# 插入第2章：来源说明之后
ls2 = open(P2, encoding="utf-8").read().split("\n")
note = next(k for k, l in enumerate(ls2) if l.strip().startswith(">"))
ins = note + 1
while ins < len(ls2) and not ls2[ins].strip():
    ins += 1
ls2[ins:ins] = ["## 【考纲内容】", ""] + [m for m in moved if not re.match(r"^#{0,4}\s*\*{0,2}【考纲内容】", m.strip())] + [""]
open(P2, "w", encoding="utf-8").write("\n".join(ls2))

print("\n=== 修复后 第2章 开头 ===")
for l in open(P2, encoding="utf-8").read().split("\n")[:12]:
    if l.strip():
        print(f"    {l[:96]}")
print("\n=== 修复后 第1章 末尾 ===")
for l in open(P1, encoding="utf-8").read().split("\n")[-10:]:
    if l.strip():
        print(f"    {l[:96]}")
