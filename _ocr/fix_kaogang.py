# -*- coding: utf-8 -*-
"""
恢复各章开头丢失的【考纲内容】条目。

原因：这些块在 PDF 解析结果里被标成 header（页眉类），Markdown 渲染器会丢弃它们，
于是每章开头的考纲要点缺失。文字本身完整保存在 structured_content.json 中，可无损恢复。

做法：从章节起始页（±1 页窗口）取开头连续的 header 块，自【考纲内容】起，
      把「该章文件里尚不存在」的条目按原顺序插到章标题/来源说明之后。
"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统", os.path.join(BOOKDIR, "操作系统"), "_ocr/os_full", "_ocr/toc.json"),
    ("数据结构", os.path.join(BOOKDIR, "数据结构"), "_ocr/ds_full", "_ocr/toc_ds.json"),
    ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理"), "_ocr/co_full", "_ocr/toc_co.json"),
    ("计算机网络", os.path.join(BOOKDIR, "计算机网络"), "_ocr/cn_full", "_ocr/toc_cn.json"),
]
SKIP = {"page_number", "page_footnote", "ref_text", "index"}


def btext(b):
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


def norm(s):
    return re.sub(r"[\s\u3000*]+", "", s)


total_fixed = 0
for name, outdir, zipdir, toc in BOOKS:
    D = os.path.join(WS, outdir)
    zd = os.path.join(WS, zipdir)
    zf = [f for f in os.listdir(zd) if f.lower().endswith(".zip")][0]
    with zipfile.ZipFile(os.path.join(zd, zf)) as z:
        sc = json.loads(z.read("structured_content.json").decode("utf-8"))
    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))

    chaps, seen = [], set()
    for d in raw:
        t = " ".join(d["title"].split())
        if d["level"] != 1 or not re.match(r"^第\d+章", t):
            continue
        num = re.match(r"^(第\d+章)", t).group(1)
        if num in seen:
            continue
        seen.add(num)
        chaps.append((num, d["page"]))

    print(f"\n### {name}")
    for num, page in chaps:
        f = next((x for x in os.listdir(D) if x.startswith(num) and x.endswith(".md")
                  and "习题" not in x), None)
        if not f:
            print(f"  {num}: 未找到章节文件，跳过")
            continue
        p = os.path.join(D, f)
        text = open(p, encoding="utf-8").read()
        ntext = norm(text)

        # 在章节起始页 ±1 内找含【考纲内容】的开头 header 序列
        opener = None
        for idx in (page - 1, page, page - 2):
            if idx < 0 or idx >= len(sc["pages"]):
                continue
            seq = []
            for b in sc["pages"][idx]["blocks"]:
                tp = b.get("type")
                if tp in SKIP:
                    continue
                if tp == "header":
                    t = btext(b).strip()
                    if t:
                        seq.append(t)
                    continue
                break
            if any("考纲内容" in t for t in seq):
                opener = seq
                break
        if not opener:
            continue
        k = next(i for i, t in enumerate(opener) if "考纲内容" in t)
        items = opener[k:]

        missing = [t for t in items if norm(t)[:14] and norm(t)[:14] not in ntext]
        if not missing:
            print(f"  {num:<6} 考纲内容完整，无需处理")
            continue

        # 组装待插入文本：考纲内容标题用粗体，与其它章保持一致
        lines = []
        for t in missing:
            lines.append(f"**{t}**" if "考纲内容" in t else t)
        block = "\n".join(lines) + "\n\n"

        # 插到 H1 与来源说明之后
        ls = text.split("\n")
        ins = 1
        if len(ls) > 1 and ls[1].startswith(">"):
            ins = 2
            while ins < len(ls) and not ls[ins].strip():
                ins += 1
        ls[ins:ins] = block.split("\n")[:-1]
        open(p, "w", encoding="utf-8").write("\n".join(ls))
        total_fixed += 1
        print(f"  {num:<6} 已补入 {len(missing)} 行: " + " | ".join(x[:26] for x in missing))

print(f"\n共修复 {total_fixed} 章")
