# -*- coding: utf-8 -*-
"""检查表格、公式、图片、乱码。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(WORKDIR, "操作系统_Markdown")
MD = os.path.join(D, "王道操作系统.md")
text = open(MD, encoding="utf-8").read()
lines = text.split("\n")

print("=== 结构元素 ===")
print("  HTML 表格 <table> :", text.count("<table"))
print("  行内公式 $...$    :", len(re.findall(r"\$[^$\n]{2,80}\$", text)))
print("  公式块 \\[ / $$   :", text.count("\\["), text.count("$$"))
print("  图片引用 ![]()    :", len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text)))
print("  代码块 ```        :", text.count("```") // 2)

print("\n=== 图片文件核对 ===")
imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
iname = [os.path.basename(p) for p in imgs]
disk = set(os.listdir(os.path.join(D, "images")))
print("  引用图片数:", len(imgs), " 磁盘图片数:", len(disk))
missing = [n for n in iname if n not in disk]
print("  引用但文件缺失:", missing[:10] if missing else "无")
unused = sorted(disk - set(iname))
print("  磁盘有但未引用:", len(unused), unused[:5] if unused else "")

print("\n=== 表格样本 ===")
ti = text.find("<table")
print(text[ti:ti + 400].replace("\n", " ")[:400])

print("\n=== 公式样本 ===")
eq = [l for l in lines if "$" in l or "\\[" in l][:4]
for e in eq:
    print("  " + e[:150])

print("\n=== 乱码/替换字符检查 ===")
bad = {c: text.count(c) for c in ["\ufffd", "锟", "�"] if text.count(c)}
print("  异常字符:", bad if bad else "无")

print("\n=== 输出目录 ===")
tot = 0
for root, _, files in os.walk(D):
    for f in files:
        tot += os.path.getsize(os.path.join(root, f))
print("  总大小: %.1f MB" % (tot / 1024 / 1024))
print("  md 大小: %.2f MB" % (os.path.getsize(MD) / 1024 / 1024))
