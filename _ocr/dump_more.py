# -*- coding: utf-8 -*-
"""补看：数据结构第4章整页块；计算机网络各受影响章。"""
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


print("=== 数据结构 第4章 起始页(101-1=120? 书签p121) 全部块 ===")
with zipfile.ZipFile(os.path.join(WS, "_ocr", "ds_full",
                                  "27王道《数据结构》高清带书签.zip")) as z:
    sc = json.loads(z.read("structured_content.json").decode("utf-8"))
for idx in (119, 120, 121):
    p = sc["pages"][idx]
    print(f"\n  --- page_idx={idx} (PDF {idx+1}), {len(p['blocks'])} 块 ---")
    for b in p["blocks"]:
        t = btext(b).strip()
        if t:
            print(f"      [{b.get('type'):<16}] {t[:78]}")

print("\n\n=== 计算机网络：受影响章的 opener 序列 ===")
with zipfile.ZipFile(os.path.join(WS, "_ocr", "cn_full",
                                  "27王道《计算机网络》高清带书签.zip")) as z:
    sc2 = json.loads(z.read("structured_content.json").decode("utf-8"))
SKIP = {"page_number", "page_footnote", "ref_text", "index"}
for num, page in [(3, 62), (4, 139), (5, 236), (6, 279)]:
    for idx in (page - 1, page, page - 2):
        if not (0 <= idx < len(sc2["pages"])):
            continue
        seq = []
        for b in sc2["pages"][idx]["blocks"]:
            tp = b.get("type")
            if tp in SKIP:
                continue
            t = btext(b).strip()
            if tp == "header" and t:
                seq.append(("H", t))
                continue
            if tp in ("text", "paragraph_title") and t:
                seq.append(("T", t))
                break
            break
        if any("考纲内容" in t for _, t in seq):
            print(f"\n  {num}  (PDF第{page}页, page_idx={idx})")
            for tp, t in seq:
                print(f"      [{tp}] {t[:78]}")
            break
