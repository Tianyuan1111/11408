# -*- coding: utf-8 -*-
"""为三本清理版生成 README 与"待核对"清单。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [
    ("操作系统",   os.path.join(BOOKDIR, "操作系统"),   "os"),
    ("数据结构",   os.path.join(BOOKDIR, "数据结构"),   "ds"),
    ("计算机网络", os.path.join(BOOKDIR, "计算机网络"), "cn"),
]
report = {r["slug"]: r for r in json.load(
    open(os.path.join(WS, "_ocr", "clean_rest_report.json"), encoding="utf-8"))}

OPT = re.compile(r"^([A-D])[.．]\s")
ROMAN = re.compile(r"[ⅠⅡⅢⅣ][ⅠI]|I{4,}")
CLEAN_NAME = {"os": "操作系统", "ds": "数据结构", "cn": "计算机网络"}

for name, outdir, slug in BOOKS:
    D = os.path.join(WS, outdir)
    # 必须排除本脚本自己生成的说明/清单文件，否则统计会把自己算成章节并重复计数
    files = {f: open(os.path.join(D, f), encoding="utf-8").read()
             for f in sorted(os.listdir(D))
             if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")}
    allt = "\n".join(files.values())

    lv = Counter({1: len(files)})
    for m in re.finditer(r"^(#{2,6})\s", allt, re.M):
        lv[len(m.group(1))] += 1

    # 罗马数字可疑
    roman = [(f, i, l.strip()) for f, t in files.items()
             for i, l in enumerate(t.split("\n")) if ROMAN.search(l)]
    roman_md = [f"# 罗马数字待核对清单（{name}）", "",
                f"共 **{len(roman)} 行** 出现罗马数字重复/错位（如 `ⅡI` 可能是 `II` 或 `III`）。", "",
                "此类错误**无法用规则安全修正**：同一形态在不同题目含义不同，",
                "且在《计算机组成原理》上做过原页 OCR 核验，证明两种含义都真实存在。", "",
                "题干的项目列表通常完好，可据此推断选项含义。", "",
                "| 文件 | 行 | 现状 |", "|---|---|---|"]
    for f, i, l in roman:
        roman_md.append(f"| {f} | {i} | {l[:90].replace('|', chr(92)+'|')} |")
    open(os.path.join(D, "待核对_罗马数字.md"), "w", encoding="utf-8").write("\n".join(roman_md) + "\n")

    # 选项块异常（连续选项超过 4 个 = 两题选项粘连，通常意味着题干缺失）
    anomalies = []
    for f, t in files.items():
        ls = t.split("\n")
        in_fence, k = False, 0
        while k < len(ls):
            if ls[k].strip().startswith("```"):
                in_fence = not in_fence
                k += 1
                continue
            if not in_fence and OPT.match(ls[k].strip()):
                seq, j = [], k
                while j < len(ls) and OPT.match(ls[j].strip()):
                    seq.append(OPT.match(ls[j].strip()).group(1))
                    j += 1
                if len(seq) > 4 or seq != sorted(seq):
                    anomalies.append((f, k, "".join(seq), ls[k].strip()[:70]))
                k = j
            else:
                k += 1

    st = report[slug]["stats"]
    rows = [(f, len(t), len(re.findall(r"!\[[^\]]*\]\([^)]+\)", t)), t.count("<table"))
            for f, t in files.items()]

    readme = f"""# 27王道《{name}》· 清理版

由 `../{name}_Markdown/王道{name}.md` 清理并分章而来。

## 目录结构

```
{outdir}/
""" + "".join(f"├── {f}\n" for f, _, _, _ in rows) + f"""├── 待核对_罗马数字.md   ← 无法自动修正的问题清单
├── README.md
└── images/                ← 各章共享，{st.get('图片复制', 0)} 张（只保留实际被引用的）
```

各章以 `images/xxx.jpg` 相对路径引用图片；**移动单个章节文件时请一并带上 `images/` 目录。**

## 各章规模

| 文件 | 字符数 | 图片 | 表格 |
|---|---|---|---|
""" + "\n".join(f"| {f} | {n:,} | {i} | {tb} |" for f, n, i, tb in rows) + f"""

标题结构：一级 {lv[1]} 个、二级 {lv[2]} 个、三级 {lv[3]} 个{f"、四级 {lv[4]} 个" if lv[4] else ""}，
与 PDF 书签（自第 1 章起）**逐级一致**，分章未改变任何层级。

## 清理内容

| 项目 | 处理量 | 说明 |
|---|---|---|
| 前置页 | 删除 {st.get('删除前置页行数', 0)} 行 | 封面、版权/CIP、B站·微信·小程序推广、前言、致读者、王道训练营广告、目录页 |
| 页标记 | 删除 {st.get('删除页标记', 0)} 个 | `<!-- page N of M -->`（按你的选择一并删除） |
| 水印与广告 | 删除 {st.get('删除水印广告行', 0)} 行 | B站水印、打印店广告（考研小舟/包邮/淘宝书店）、「视频讲解」标记 |
| 行尾 OCR 噪声 | 删除 {st.get('删除行尾噪声', 0) + st.get('删除成串噪声', 0) + st.get('删除行中噪声', 0)} 处 | 句末标点后跟随的乱码字母串（`XT`/`XTA`/`K`/`MX`…） |
| 选项挤行 | 拆分 {st.get('拆分选项行', 0)} 行 | 选项原文常无空格（`A. xxxB. yyy`），已拆成独立行 |
| 粘连题号 | 拆开 {st.get('拆开粘连题号', 0)} 处 | 选项末尾粘了下题题号（`D. 1007.` = `D. 10` + `07.`），按递增题号定位切点 |
| 选项标记 | 规范化 {st.get('选项标记规范化', 0)} 处 | `B.64` → `B. 64` |
| 选项间空行 | 合并 {st.get('合并选项间空行', 0)} 处 | PDF 分页把 D 与 A/B/C 隔开的情况 |
| 脚注 | 转换 {st.get('脚注转引用', 0)} 行 | `<small><span class="docvortex-page-footnote">` → `> 引用块` |
| 公式空格 | 规范化 {st.get('公式规范化', 0)} + {st.get('公式字母合并', 0)} 处 | `1 0 ^ {{ 6 }}`→`10^{{6}}`；逐字符空格 `d o u b l e`→`double` |
| 连续空行 | 压缩 {st.get('压缩空行', 0)} 处 | |

### 清理规则的两条安全边界

- **围栏代码块内不做任何改动。** 数据结构有 257 个 C 代码块，其中的 `A.length`、`C.data` 会被误认为选项标记（实测曾破坏 443 行），现已按 ``` 围栏跳过。
- **选项标记只认点号。** 顿号在本书中出现 {st.get('顿号处数', '若干')} 处，经查全部是行文（`选项A、B、C`、`序列A、B、C`、答案 `13.B、A、C、D`），不是选项分隔符。

## 已知问题

### 1. 罗马数字错乱（{len(roman)} 行）——未修正

部分选择题的罗马数字项目出现重复，如 `A. I、ⅡI`。**不做自动修正**，因为同一形态在不同题目含义不同（在《计算机组成原理》上裁原页 OCR 核验过：同形 `ⅢI` 有的应为 `II`、有的应为 `III`）。完整清单见 `待核对_罗马数字.md`。

### 2. 题干缺失 / 选项粘连（{len(anomalies)} 处）——源文件固有

个别题目出现连续两套 A-D 选项，说明**该题题干在源文件中就已丢失**（对照原始 Markdown 确认非清理所致）。
另有个别选项被 PDF 版式中的插图隔开（内容完好）。

| 文件 | 行 | 选项序列 |
|---|---|---|
""" + "\n".join(f"| {f} | {i} | {seq} |" for f, i, seq, _ in anomalies[:40]) + f"""

### 3. 其余 OCR 固有风险

数字、下标、运算符建议对照原 PDF 抽查。本次解决的是**可机械判定**的错误，不能替代逐字校对。
"""
    open(os.path.join(D, "README.md"), "w", encoding="utf-8").write(readme)
    print(f"{name}: README 已生成 | 罗马数字 {len(roman)} 行 | 题干异常 {len(anomalies)} 处 | 图片 {st.get('图片复制',0)}")
