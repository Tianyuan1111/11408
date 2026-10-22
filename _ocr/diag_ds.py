# -*- coding: utf-8 -*-
"""正确诊断：数据结构哪些书签标题在输出中缺失（含原文件对照）。"""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "数据结构")
SRC = os.path.join(WORKDIR, "数据结构_Markdown", "王道数据结构.md")
BARE = re.compile(r"^第\d+章$")


def norm(s):
    s = re.sub(r"[\s\u3000]+", "", s)
    for a, b in [("．", "."), ("（", "("), ("）", ")"), ("，", ","), ("：", ":"),
                 ("；", ";"), ("·", ""), ("…", ""), ("\u3000", "")]:
        s = s.replace(a, b)
    return s.lower()


raw = json.load(open(os.path.join(WS, "_ocr", "toc_ds.json"), encoding="utf-8"))
bms = [d for d in raw if " ".join(d["title"].split()) and not BARE.match(" ".join(d["title"].split()))]
bms = [{"level": d["level"], "title": " ".join(d["title"].split()), "page": d["page"]} for d in bms]
idx = next(i for i, b in enumerate(bms) if b["title"].startswith("第1章"))
base = bms[idx:]
print(f"书签(第1章起)={len(base)} 条，层级分布={ {k: sum(1 for b in base if b['level']==k) for k in (1,2,3,4)} }")

files = {f: open(os.path.join(D, f), encoding="utf-8").read()
         for f in sorted(os.listdir(D)) if f.endswith(".md")}
allt = "\n".join(files.values())
heads = [norm(m.group(2)) for m in re.finditer(r"^(#{1,6})\s+(.*)$", allt, re.M)]
print(f"输出标题 {len(heads)} 个，层级分布=",
      {k: sum(1 for l in allt.split(chr(10)) if re.match(r"^" + "#" * k + r" ", l)) for k in (1, 2, 3, 4)})

print("\n=== 书签有、输出无的标题 ===")
srclines = open(SRC, encoding="utf-8").read().split("\n")
missing = []
for b in base:
    t = norm(b["title"])
    if any(t == h or (len(t) >= 4 and len(h) >= 4 and (h.startswith(t) or t.startswith(h)))
           for h in heads):
        continue
    missing.append(b)

print(f"共 {len(missing)} 条")
for b in missing:
    t = norm(b["title"])
    src_hit = [i for i, l in enumerate(srclines)
               if l.startswith("#") and t and t in norm(l.lstrip("# "))]
    print(f"  L{b['level']} p{b['page']:>3}  {b['title'][:44]:<46} 原文件行={src_hit[:2] if src_hit else '无'}")
