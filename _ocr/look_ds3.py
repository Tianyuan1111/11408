# -*- coding: utf-8 -*-
"""细看三处问题的上下文与原文件对照。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "数据结构")
SRC = os.path.join(WORKDIR, "数据结构_Markdown", "王道数据结构.md")
src = open(SRC, encoding="utf-8").read().split("\n")

def show(path, lo, hi, tag):
    ls = open(path, encoding="utf-8").read().split("\n")
    print(f"--- {tag} L{lo}-L{hi} ---")
    for i in range(lo, min(hi, len(ls))):
        if ls[i].strip():
            print(f"  L{i:>5}| {ls[i][:112]}")
    print()

show(os.path.join(D, "第2章 线性表.md"), 658, 680, "清理版 第2章(A.data 区)")
show(os.path.join(D, "第5章 树与二叉树.md"), 130, 150, "清理版 第5章(重复选项)")
show(os.path.join(D, "第7章 查找.md"), 1163, 1180, "清理版 第7章(题干并入选项)")

print("=== 原文件中「至少有 h + 3 个结点」在哪 ===")
for i, l in enumerate(src):
    if "至少有 h + 3 个结点" in l or "至少有h+3个结点" in l:
        for j in range(max(0, i - 6), min(i + 4, len(src))):
            if src[j].strip():
                print(f"  L{j:>5}| {src[j][:112]}")
        break

print("\n=== 原文件中「数据[k++]」区 ===")
for i, l in enumerate(src):
    if "data[k++]=A.data" in l or "data[k++] = A.data" in l:
        for j in range(max(0, i - 8), min(i + 6, len(src))):
            if src[j].strip():
                print(f"  L{j:>5}| {src[j][:112]}")
        break

print("\n=== 统计：选项行末尾粘了下题题号（形如 \\d{2}\\. 紧跟内容）===")
allt = "\n".join(open(os.path.join(D, f), encoding="utf-8").read()
                 for f in os.listdir(D) if f.endswith(".md"))
n = 0
for m in re.finditer(r"^[A-D][.．]\s.*?\d{1,2}[.、]\s*\S", allt, re.M):
    n += 1
print(f"  疑似 {n} 处")
for m in list(re.finditer(r"^[A-D][.．]\s.{0,90}", allt, re.M))[:0]:
    pass
