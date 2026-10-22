# -*- coding: utf-8 -*-
"""查计算机网络第2章为何没有【考纲内容】。"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）


def btext(b):
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


print("=== 清理版 计算机网络 第2章 前 16 行 ===")
p = os.path.join(BOOKDIR, "计算机网络", "第2章 物理层.md")
for l in open(p, encoding="utf-8").read().split("\n")[:24]:
    if l.strip():
        print(f"    {l[:96]}")

print("\n=== 其它章【考纲内容】的写法（对照）===")
for f in ["第1章 计算机网络体系结构.md", "第3章 数据链路层.md"]:
    for l in open(os.path.join(BOOKDIR, "计算机网络", f), encoding="utf-8").read().split("\n")[:12]:
        if "考纲" in l:
            print(f"    {f}: {l.strip()[:80]!r}")

print("\n=== PDF 解析：第2章起始页(PDF 42, idx=41) 及前后 ===")
with zipfile.ZipFile(os.path.join(WS, "_ocr", "cn_full",
                                  "27王道《计算机网络》高清带书签.zip")) as z:
    sc = json.loads(z.read("structured_content.json").decode("utf-8"))
SKIP = {"page_number", "page_footnote", "ref_text", "index"}
for idx in (40, 41, 42):
    pg = sc["pages"][idx]
    print(f"\n  --- page_idx={idx} (PDF {idx+1}) {len(pg['blocks'])} 块 ---")
    n = 0
    for b in pg["blocks"]:
        t = btext(b).strip()
        if t:
            print(f"      [{b.get('type'):<16}] {t[:76]}")
            n += 1
        if n >= 12:
            break
