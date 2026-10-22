# -*- coding: utf-8 -*-
"""全量检测 OCR 退化（连续重复字符 / 异常长行），并溯源到 structured_content。"""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
MD = os.path.join(WORKDIR, "操作系统_Markdown", "王道操作系统.md")
lines = open(MD, encoding="utf-8").read().split("\n")

print("=== 连续重复字符 >=8 次的行 ===")
pat = re.compile(r"(.)\1{7,}")
found = []
for i, l in enumerate(lines):
    m = pat.search(l)
    if m:
        found.append((i, m.group(0)[:20], l[:90]))
for i, rep, prev in found:
    print(f"  L{i}: 重复[{rep[:12]}]  {prev}")
print(f"  合计: {len(found)} 行")

print("\n=== 极长行（>1500 字符）===")
for i, l in enumerate(lines):
    if len(l) > 1500:
        print(f"  L{i}: 长度 {len(l)}  {l[:70]}")

print("\n=== 溯源：structured_content 第 370 页(idx 369) ===")
sc = json.load(open(os.path.join(WS, "_ocr", "os_full_x", "structured_content.json"), encoding="utf-8"))
p = sc["pages"][369]
for j, b in enumerate(p["blocks"]):
    c = b.get("content")
    if isinstance(c, list):
        c = " ".join(str(x.get("content", "")) for x in c)
    c = str(c)
    if "区" in c and c.count("区") > 10:
        print(f"  block {j} type={b.get('type')}")
        print("   前150:", c[:150])
        print("   后150:", c[-150:])
