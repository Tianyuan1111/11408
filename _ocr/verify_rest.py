# -*- coding: utf-8 -*-
"""三本清理版验收：与书签逐级比对（从第1章起）+ 选项块完整性 + 抽样。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统",   os.path.join(BOOKDIR, "操作系统"),   "_ocr/toc.json"),
    ("数据结构",   os.path.join(BOOKDIR, "数据结构"),   "_ocr/toc_ds.json"),
    ("计算机网络", os.path.join(BOOKDIR, "计算机网络"), "_ocr/toc_cn.json"),
]
BARE = re.compile(r"^第\d+章$")
OPT = re.compile(r"^([A-D])[.．]\s")
SENT = r"。！？；：\)）】"
NOISE_END = re.compile(rf"([{SENT}])\s+[A-Z]{{1,6}}\s*$")

ok_all = True
for name, outdir, toc in BOOKS:
    D = os.path.join(WS, outdir)
    files = {f: open(os.path.join(D, f), encoding="utf-8").read()
             for f in sorted(os.listdir(D)) if f.endswith(".md")}
    allt = "\n".join(files.values())
    print("=" * 76)
    print(f"### {name}   ({len(files)} 个文件)")
    print("=" * 76)

    lv = Counter({1: len(files)})
    for m in re.finditer(r"^(#{2,6})\s", allt, re.M):
        lv[len(m.group(1))] += 1

    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))
    bms = [d for d in raw if " ".join(d["title"].split()) and not BARE.match(" ".join(d["title"].split()))]
    idx = next(i for i, b in enumerate(bms) if " ".join(b["title"].split()).startswith("第1章"))
    base = Counter(b["level"] for b in bms[idx:])

    print("  标题层级  输出 vs 书签(第1章起):")
    for k in sorted(set(lv) | set(base)):
        got, exp = lv.get(k, 0), base.get(k, 0)
        flag = "OK" if got == exp else f"差异 {got-exp:+d}"
        if got != exp:
            ok_all = False
        print(f"    H{k}: 输出={got:<5} 书签={exp:<5} {flag}")

    # 选项块完整性
    lines = [(f, l) for f, t in files.items() for l in t.split("\n")]
    i, blocks, bad = 0, 0, []
    while i < len(lines):
        if OPT.match(lines[i][1]):
            seq, j = [], i
            while j < len(lines) and OPT.match(lines[j][1]):
                seq.append(OPT.match(lines[j][1]).group(1)); j += 1
            blocks += 1
            if seq != sorted(seq) or len(seq) < 2:
                bad.append((lines[i][0], seq, lines[i][1][:70]))
            i = j
        else:
            i += 1
    print(f"  选项块 {blocks} 个，异常 {len(bad)} 个")
    for f, seq, t in bad[:5]:
        print(f"      {f} {seq}: {t}")

    print(f"  残余: 噪声{sum(1 for l in allt.split(chr(10)) if NOISE_END.search(l.rstrip()))} "
          f"页标记{len(re.findall(r'<!-- page', allt))} "
          f"水印{sum(allt.count(w) for w in ['官方开源','bilibili','考研小舟','包邮','taobao','视频讲解'])} "
          f"脚注HTML{allt.count('docvortex-page-footnote')} "
          f"$$失衡{sum(1 for t in files.values() if t.count('$$') % 2)}")
    imgs = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", allt))
    disk = len(os.listdir(os.path.join(D, "images")))
    refs = {os.path.basename(p) for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", allt)}
    print(f"  图片: 引用{imgs} 磁盘{disk} 缺失{len(refs - set(os.listdir(os.path.join(D,'images'))))} "
          f"表格{allt.count('<table')} 字符{len(allt)}")
    print(f"  文件: " + ", ".join(f"{f}({len(t)//1000}k)" for f, t in files.items()))
    print()

print("总体:", "全部通过" if ok_all else "存在差异")
