# -*- coding: utf-8 -*-
"""四本清理版：代码块误拆 + 图片完整性。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
DIRS = [("操作系统", os.path.join(BOOKDIR, "操作系统")),
        ("数据结构", os.path.join(BOOKDIR, "数据结构")),
        ("计算机组成原理", "计算机组成原理"),
        ("计算机网络", os.path.join(BOOKDIR, "计算机网络"))]
OPT = re.compile(r"^[A-D][.．]\s")
FENCE = "`" * 3

for name, d in DIRS:
    D = os.path.join(WS, d)
    if not os.path.isdir(D):
        print(f"### {name}: 目录不存在 {d}")
        continue
    broken, refs = 0, set()
    for f in sorted(os.listdir(D)):
        if not f.endswith(".md"):
            continue
        t = open(os.path.join(D, f), encoding="utf-8").read()
        refs |= {os.path.basename(p) for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", t)}
        inf = False
        for l in t.split("\n"):
            if l.strip().startswith(FENCE):
                inf = not inf
                continue
            if inf and OPT.match(l.strip()):
                broken += 1
    disk = set(os.listdir(os.path.join(D, "images")))
    print(f"### {name}")
    print(f"    代码块被误拆: {broken}")
    print(f"    图片: 引用 {len(refs)}  磁盘 {len(disk)}  缺失 {len(refs - disk)}  多余 {len(disk - refs)}")
    if refs - disk:
        print(f"      缺失清单: {sorted(refs - disk)[:6]}")
