# -*- coding: utf-8 -*-
"""三本书：选项标记风格 + 疑被误分类为公式块的中文标题。"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统",   os.path.join(WORKDIR, "操作系统_Markdown"),     "王道操作系统.md",     "_ocr/os_full"),
    ("数据结构",   os.path.join(WORKDIR, "数据结构_Markdown"),     "王道数据结构.md",     "_ocr/ds_full"),
    ("计算机网络", os.path.join(WORKDIR, "计算机网络_Markdown"),   "王道计算机网络.md",   "_ocr/cn_full"),
]
CJK = re.compile(r"[\u4e00-\u9fff]")
MARKER_WORD = re.compile(r"考点追踪|本章小结|常见问题|复习提示|考纲|例题|注意|疑难")

for name, outdir, mdfile, zipdir in BOOKS:
    print("=" * 76)
    print(f"### {name}")
    print("=" * 76)
    text = open(os.path.join(WS, outdir, mdfile), encoding="utf-8").read()
    lines = text.split("\n")

    dot = sum(len(re.findall(r"(?<![A-Za-z0-9])[A-D][.](?:\s|(?=[\u4e00-\u9fff\w]))", l)) for l in lines)
    fw = sum(len(re.findall(r"(?<![A-Za-z0-9])[A-D]．", l)) for l in lines)
    dun = sum(len(re.findall(r"(?<![A-Za-z0-9])[A-D]、", l)) for l in lines)
    print(f"选项标记样式： 半角点 {dot} 处 | 全角点 {fw} 处 | 顿号 {dun} 处")
    if dun:
        print("  顿号样例（判断是否为行文而非选项）:")
        n = 0
        for i, l in enumerate(lines):
            for m in re.finditer(r"(?<![A-Za-z0-9])[A-D]、", l):
                print(f"    L{i}: …{l[max(0,m.start()-35):m.start()+40]}…")
                n += 1
                break
            if n >= 5:
                break

    zd = os.path.join(WS, zipdir)
    zips = [f for f in os.listdir(zd) if f.lower().endswith(".zip")] if os.path.isdir(zd) else []
    if not zips:
        print("  !! 未找到 zip，跳过误分类扫描\n")
        continue
    with zipfile.ZipFile(os.path.join(zd, zips[0])) as z:
        sc = json.loads(z.read("structured_content.json").decode("utf-8"))

    susp = []
    for p in sc["pages"]:
        for j, b in enumerate(p["blocks"]):
            if b.get("type") != "equation":
                continue
            c = b.get("content")
            if isinstance(c, list):
                c = " ".join(str(x.get("content", "")) for x in c)
            if not isinstance(c, str):
                continue
            if len(CJK.findall(c)) >= 4:
                susp.append({"page": p["page_idx"] + 1, "block": j, "cjk": len(CJK.findall(c)),
                             "marker": bool(MARKER_WORD.search(c)), "text": c[:130]})
    strong = [s for s in susp if s["marker"]]
    print(f"  含中文的公式块 {len(susp)} 个；其中含标记词的 {len(strong)} 个（疑似误分类标题）")
    for s in strong:
        print(f"    PDF第{s['page']}页 block{s['block']}: {s['text']}")
    print()
