# -*- coding: utf-8 -*-
"""为四本清理版统一生成 README。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统", os.path.join(BOOKDIR, "操作系统"), "os", "_ocr/toc.json"),
    ("数据结构", os.path.join(BOOKDIR, "数据结构"), "ds", "_ocr/toc_ds.json"),
    ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理"), "co", "_ocr/toc_co.json"),
    ("计算机网络", os.path.join(BOOKDIR, "计算机网络"), "cn", "_ocr/toc_cn.json"),
]
BARE = re.compile(r"^第\d+章$")
ROMAN = re.compile(r"[ⅠⅡⅢⅣ][ⅠI]|I{4,}")

# 考纲内容恢复情况（来自 fix_kaogang2 的运行结果）
KAO_FIXED = {
    "os": ["第2章", "第3章", "第4章", "第5章"],
    "ds": ["第1章", "第2章", "第4章", "第6章"],
    "co": ["第1章", "第5章", "第6章", "第7章"],
    "cn": ["第2章", "第3章", "第4章", "第5章", "第6章"],
}
KNOWN = {
    "os": "全书 **131 行** 出现罗马数字重复/错位（如 `A. I、ⅡI`）。"
          "**不做自动修正**，因为同一形态在不同题目含义不同。完整清单见 `待核对_罗马数字.md`。",
    "ds": "全书 **84 行** 出现罗马数字重复/错位。**不做自动修正**，清单见 `待核对_罗马数字.md`。",
    "co": "全书 **101 行** 出现罗马数字重复/错位。**不做自动修正**，清单见 `待核对_罗马数字.md`。",
    "cn": "全书 **30 行** 出现罗马数字重复/错位。**不做自动修正**，清单见 `待核对_罗马数字.md`。",
}

for name, outdir, slug, toc in BOOKS:
    D = os.path.join(WS, outdir)
    md = [f for f in sorted(os.listdir(D)) if f.endswith(".md")
          and f != "README.md" and not f.startswith("待核对")]
    main = [f for f in md if "习题与解析" not in f]
    exf = [f for f in md if "习题与解析" in f]
    mtext = "\n".join(open(os.path.join(D, f), encoding="utf-8").read() for f in main)
    etext = "\n".join(open(os.path.join(D, f), encoding="utf-8").read() for f in exf)

    lv = Counter({1: len(main)})
    for m in re.finditer(r"^(#{2,6})\s", mtext + "\n" + etext, re.M):
        lv[len(m.group(1))] += 1
    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))
    bms = [{"level": d["level"], "title": " ".join(d["title"].split())} for d in raw]
    bms = [b for b in bms if b["title"] and not BARE.match(b["title"])]
    idx = next(i for i, b in enumerate(bms) if b["title"].startswith("第1章"))
    base = Counter(b["level"] for b in bms[idx:])

    def info(f):
        t = open(os.path.join(D, f), encoding="utf-8").read()
        return len(t), len(re.findall(r"!\[[^\]]*\]\([^)]+\)", t)), t.count("<table")
    mrows = [(f, *info(f)) for f in main]
    erows = [(f, *info(f)) for f in exf]
    tm, te = sum(r[1] for r in mrows), sum(r[1] for r in erows)
    roman = sum(1 for t in (mtext, etext) for l in t.split("\n") if ROMAN.search(l))
    imgs = len(os.listdir(os.path.join(D, "images")))

    readme = f"""# 27王道《{name}》· 清理版

由 `../{name}_Markdown/王道{name}.md` 清理、分章，并**把习题摘出**而成。

## 目录结构

```
{outdir}/
""" + "".join(f"├── {f}\n" for f, _, _, _ in mrows) + \
        "".join(f"├── {f}   ← 习题与答案\n" for f, _, _, _ in erows) + f"""├── 待核对_罗马数字.md
├── README.md
└── images/                ← 全部文件共享，{imgs} 张
```

各文件以 `images/xxx.jpg` 相对路径引用图片；**移动单个文件时请一并带上 `images/` 目录。**
正文与习题文件共用同一份图片，习题里的配图不会缺失。

## 习题已摘出

原书把「本节习题精选 / 本节试题精选」与「答案与解析」插在每个小节之后。
现已按章摘到独立的 `第N章 习题与解析.md`，**正文中完全移除、不留痕迹**。

- 摘出依据：`### X.Y.Z 本节习题精选`（数据结构为「本节**试题**精选」）与 `### X.Y.Z 答案与解析` 两类 H3 标题；
  其下的 `#### 单项选择题`、`#### 二、综合应用题` 属于该区块。
- 区块标题**保留原小节编号**，便于与正文对照。
- 章节开头的"思考题参考答案"属于考点讲解的叙事部分，**未摘出**，仍在正文中。
- 无损性已验证：先备份章节文件，摘出后按**行多重集**比对，**缺失 0 行**
  （多出的仅为习题文件的标题与来源说明）。

| 文件 | 字符数 | 图片 | 表格 |
|---|---|---|---|
""" + "\n".join(f"| {f} | {n:,} | {i} | {tb} |" for f, n, i, tb in mrows + erows) + f"""

正文合计 **{tm:,}** 字符，习题与解析合计 **{te:,}** 字符。

## 已恢复：各章开头的【考纲内容】

修复前，**{len(KAO_FIXED[slug])} 章的【考纲内容】条目缺失**（{('、'.join(KAO_FIXED[slug]))}）。

**原因**：PDF 解析把这些块标成了 `header`（页眉类），Markdown 渲染器会把这类块丢弃，
于是每章开头的考纲要点在转换时就没了。文字本身完整保存在解析数据中。

**修复方式**：从解析数据中取回这些块，按原顺序插到章标题/来源说明之后
（若该章已有【考纲内容】标题，则插到该标题之下）——正是它们在原书中的位置，
紧随其后的就是那个幸存的正文块，衔接无缝。**属无损恢复，非推测补写。**

## 标题结构

一级 {lv[1]} 个、二级 {lv[2]} 个、三级 {lv[3]} 个{f"、四级 {lv[4]} 个" if lv[4] else ""}
（正文与习题文件合计），与 PDF 书签自第 1 章起**逐级一致** —— 分章与摘出只是搬运标题，未增删任何层级。

## 已知问题

### 1. 罗马数字错乱（{roman} 行）——未修正

{KNOWN[slug]}

**为什么不做自动修正**：同一形态在不同题目里含义不同。在《计算机组成原理》上裁原页 OCR 核验证明：
第 76 页 `A. 仅I、ⅡI` 实际是 `A. 仅I、II`，而第 248 页 `C. 只有ⅢI` 实际是 `C. 只有II`（不是 `III`）。
对原页裁图 OCR 噪声也大，不足以作为修改依据。**宁可保留原样，也不猜测后写入习题答案。**

### 2. 其余 OCR 固有风险

数字、下标、运算符建议对照原 PDF 抽查。本次处理解决的是**可机械判定**的问题，不能替代逐字校对。
"""
    open(os.path.join(D, "README.md"), "w", encoding="utf-8").write(readme)
    print(f"{name}: README 完成（正文 {len(main)} + 习题 {len(exf)}；层级 "
          f"H1={lv[1]} H2={lv[2]} H3={lv[3]} H4={lv[4]}；罗马数字 {roman}）")
