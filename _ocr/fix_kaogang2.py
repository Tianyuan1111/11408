# -*- coding: utf-8 -*-
"""
恢复各章开头丢失的【考纲内容】等块（v2，修正位置与停止条件）。

背景：这些块在 PDF 解析结果里被标成 header（页眉类），Markdown 渲染器会丢弃。
文字完整保存在 structured_content.json 中，属无损恢复。

v2 修正：
  - 插入位置：若该章已有【考纲内容】标题，则插到该标题之后；否则插到「来源说明」之后
    （正是原书里这些行的位置——紧接其后的就是那个幸存的正文块，如【复习提示】）。
  - 停止条件：从【考纲内容】起、到第一个非 header 块为止；不越界把后续正文拉进来。
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
KAO = re.compile(r"^#{0,4}\s*\*{0,2}【考纲内容】")


def btext(b):
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


def norm(s):
    return re.sub(r"[\s\u3000*#]+", "", s)


def opener_run(sc, page):
    """取章节起始页(±1)开头连续的 header 块，自【考纲内容】起、到第一个非 header 块止。"""
    for idx in (page - 1, page, page - 2):
        if not (0 <= idx < len(sc["pages"])):
            continue
        heads = []
        for b in sc["pages"][idx]["blocks"]:
            tp = b.get("type")
            if tp in SKIP:
                continue
            t = btext(b).strip()
            if tp == "header":
                if t:
                    heads.append(t)
                continue
            break
        k = next((i for i, t in enumerate(heads) if "考纲内容" in t), None)
        if k is not None:
            return heads[k:]
    return []


total = 0
for name, outdir, zipdir, toc in BOOKS:
    D = os.path.join(WS, outdir)
    zd = os.path.join(WS, zipdir)
    zf = [f for f in os.listdir(zd) if f.lower().endswith(".zip")][0]
    with zipfile.ZipFile(os.path.join(zd, zf)) as z:
        sc = json.loads(z.read("structured_content.json").decode("utf-8"))
    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))

    files = [f for f in sorted(os.listdir(D)) if f.endswith(".md")
             and f != "README.md" and not f.startswith("待核对") and "习题" not in f]
    # 该书的【考纲内容】标题书写惯例（多数派）
    styles = {"## 【考纲内容】": 0, "**【考纲内容】**": 0, "【考纲内容】": 0}
    for f in files:
        for l in open(os.path.join(D, f), encoding="utf-8").read().split("\n"):
            s = l.strip()
            if KAO.match(s) and s in styles:
                styles[s] += 1
    style = max(styles, key=styles.get) if any(styles.values()) else "**【考纲内容】**"

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

    print(f"\n### {name}  （【考纲内容】惯例: {style}）")
    for num, page in chaps:
        f = next((x for x in files if x.startswith(num)), None)
        if not f:
            continue
        p = os.path.join(D, f)
        ls = open(p, encoding="utf-8").read().split("\n")
        ntext = norm("\n".join(ls))

        run = opener_run(sc, page)
        if not run:
            continue
        missing = [t for t in run if norm(t)[:14] and norm(t)[:14] not in ntext]
        if not missing:
            print(f"  {num:<6} 完整，无需处理")
            continue

        lines = []
        for t in missing:
            if "考纲内容" in t:
                lines.append(style)
            elif "知识框架" in t:
                lines.append(f"**【{t.strip('【】')}】**" if t.startswith("【") else t)
            else:
                lines.append(t)
        block = lines + [""]

        # 定位插入点
        kao_i = next((i for i, l in enumerate(ls) if KAO.match(l.strip())), None)
        if kao_i is not None:
            ins = kao_i + 1
            while ins < len(ls) and not ls[ins].strip():
                ins += 1
        else:
            note_i = next((i for i, l in enumerate(ls) if l.strip().startswith(">")), None)
            ins = (note_i + 1) if note_i is not None else 1
            while ins < len(ls) and not ls[ins].strip():
                ins += 1
        ls[ins:ins] = block
        open(p, "w", encoding="utf-8").write("\n".join(ls))
        total += 1
        print(f"  {num:<6} 补入 {len(lines)} 行 @L{ins}: " + " | ".join(x[:24] for x in lines))

print(f"\n共修复 {total} 章")
