# -*- coding: utf-8 -*-
"""从 zip 取 structured_content，扫描"含中文的公式块"以找出误分类。"""
import os, re, sys, json, zipfile

sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
ZIP = os.path.join(WS, "_ocr", "co_full", "27王道《计算机组成原理》高清带书签.zip")

with zipfile.ZipFile(ZIP) as z:
    names = z.namelist()
    sc = json.loads(z.read("structured_content.json").decode("utf-8"))
    md = z.read("markdown.md").decode("utf-8")
print("zip 内文件:", names)
print("页数:", len(sc["pages"]))

CJK = re.compile(r"[\u4e00-\u9fff]")
MARKER = re.compile(r"考点追踪|本章小结|常见问题|复习提示|考纲|例题|注意")

suspects = []
for p in sc["pages"]:
    for j, b in enumerate(p["blocks"]):
        if b.get("type") != "equation":
            continue
        c = b.get("content")
        if isinstance(c, list):
            c = " ".join(str(x.get("content", "")) for x in c)
        if not isinstance(c, str):
            continue
        cjk = len(CJK.findall(c))
        if cjk >= 4:                      # 公式里出现较多中文 → 可疑
            suspects.append({
                "page": p["page_idx"] + 1, "block": j,
                "type": b.get("type"), "bbox": b.get("bbox"),
                "cjk": cjk, "len": len(c),
                "has_marker": bool(MARKER.search(c)),
                "text": c[:160],
            })

print(f"\n=== 疑似误分类的公式块（含中文 >=4 字）: {len(suspects)} 个 ===")
for s in suspects:
    tag = "★含标记词" if s["has_marker"] else ""
    print(f"  PDF第{s['page']:>3}页 block{s['block']:>3} 中文{s['cjk']:>3}字 长{s['len']:>4} {tag}")
    print(f"      {s['text']}")

json.dump(suspects, open(os.path.join(WS, "_ocr", "co_suspect_eq.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n已写入 _ocr/co_suspect_eq.json")
