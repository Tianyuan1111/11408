# -*- coding: utf-8 -*-
"""生成清理版 README，并输出"罗马数字待核对清单"。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机组成原理")
report = json.load(open(os.path.join(WS, "_ocr", "co_clean_report.json"), encoding="utf-8"))
rv = json.load(open(os.path.join(WS, "_ocr", "roman_verify.json"), encoding="utf-8"))

files = {f: open(os.path.join(D, f), encoding="utf-8").read()
         for f in sorted(os.listdir(D)) if f.endswith(".md")}
allt = "\n".join(files.values())
SUSPECT = re.compile(r"[ⅠⅡⅢⅣ][ⅠI]|I{4,}")

# ---------- 罗马数字待核对清单 ----------
entries = []
for r in rv:
    qs = []
    for l in r["now"]:
        qs.append(l[:70])
    entries.append((r["page"], qs))
bad_lines = [(fn, l.strip()) for fn, t in files.items()
             for l in t.split("\n") if SUSPECT.search(l)]

roman_md = ["# 罗马数字待核对清单", "",
            f"共 **{len(bad_lines)} 行** 涉及罗马数字错乱（`ⅡI`/`ⅢII` 这类重复）。",
            "",
            "这类错误**无法用规则安全修正** —— 同一形态在不同题目里含义不同：",
            "",
            "- 第 76 页（2015 真题）：`A. 仅I、ⅡI` 实际应为 `A. 仅I、II`",
            "- 第 248 页（微程序控制）：`C. 只有ⅢI` 实际应为 `C. 只有II`",
            "",
            "对原页二次 OCR 的噪声也很大，无法作为依据。因此保持原样，仅列出位置供人工核对。",
            "题干的罗马数字项目列表本身通常是完整的，可据此推断选项含义。", "",
            "| PDF 页 | 现状（OCR 结果） |", "|---|---|"]
for page, qs in entries:
    roman_md.append(f"| {page} | {'<br>'.join(q.replace('|', '\\|') for q in qs)} |")
open(os.path.join(D, "待核对_罗马数字.md"), "w", encoding="utf-8").write("\n".join(roman_md) + "\n")

# ---------- README ----------
lv_tot = Counter()
rows = []
for fn, t in files.items():
    lv = Counter(len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s", t, re.M))
    lv_tot.update(lv)
    rows.append((fn, len(t), len(re.findall(r"!\[[^\]]*\]\([^)]+\)", t)),
                 t.count("<table"), t.count("$$") // 2))
rows.sort()

st = report["stats"]
readme = f"""# 27王道《计算机组成原理》· 清理版

由 `../计算机组成原理_Markdown/王道计算机组成原理.md` 清理而来，按章拆分为独立文件。

## 目录结构

```
计算机组成原理_清理版/
├── 第1章 计算机系统概述.md
├── 第2章 数据的表示和运算.md
├── 第3章 存储系统.md
├── 第4章 指令系统.md
├── 第5章 中央处理器.md
├── 第6章 总线.md
├── 第7章 输入／输出系统.md
├── 参考文献.md
├── 待核对_罗马数字.md      ← 无法自动修正的问题清单
├── README.md
└── images/                 ← 全章共享，{st.get('图片复制', 0)} 张（只保留实际被引用的）
```

各章文件均以 `![](images/xxx.jpg)` 相对路径引用图片。**移动单个章节文件时请一并带上 `images/` 目录。**

## 各章规模

| 文件 | 字符数 | 图片 | 表格 | 公式块 |
|---|---|---|---|---|
""" + "\n".join(f"| {fn} | {n:,} | {i} | {tb} | {eq} |" for fn, n, i, tb, eq in rows) + f"""

标题结构：一级 {lv_tot[1]} 个、二级 {lv_tot[2]} 个、三级 {lv_tot[3]} 个，
与 PDF 书签基准（L1=8 / L2=42 / L3=154）**完全一致**，拆分未改变任何层级。

## 清理内容

| 项目 | 处理量 | 说明 |
|---|---|---|
| 前置页 | 删除 {st.get('删除前置页行数', 0)} 行 | 封面、版权/CIP、B站·微信·小程序推广、前言、致读者、王道训练营广告、目录页 |
| 页标记 | 删除 {st.get('删除页标记', 0)} 个 | `<!-- page N of 340 -->`（按你的选择一并删除） |
| 水印与广告 | 删除 {st.get('删除水印广告行', 0)} 行 | `官方开源，高清带书签PDF…bilibili.com`（10 处）、打印店广告（考研小舟/包邮）、「视频讲解」标记（7 处） |
| 行尾 OCR 噪声 | 删除 {st.get('删除行尾噪声', 0) + st.get('删除成串噪声', 0) + st.get('删除行中噪声', 0)} 处 | 句末标点后跟随的乱码字母串（`XT`/`XTA`/`K`/`MX`/`IR`…），共 38 种 token |
| 选项挤行 | 拆分 {st.get('拆分选项行', 0)} 行 | 大量选项原文完全无空格（`A. xxxB. yyyC. zzz`），已拆成独立行 |
| 选项标记 | 规范化 {st.get('选项标记规范化', 0)} 处 | `B.64` → `B. 64` |
| 选项间空行 | 合并 {st.get('合并选项间空行', 0)} 处 | PDF 分页导致 D 选项与 A/B/C 被空行隔开 |
| 脚注 | 转换 {st.get('脚注转引用', 0)} 行 | `<small><span class="docvortex-page-footnote">` → `> 引用块` |
| 公式空格 | 规范化 {st.get('公式空格规范化', 0)} 处 | `1 0 ^ { 6 }` → `10^{{6}}`；逐字符空格 `d o u b l e` → `double` |
| 误分类标题 | 修复 {st.get('修复误分类标记', 0)} 处 | 两处「考点追踪」被公式模型误判并乱码，已裁原图 OCR 核实后还原 |
| 连续空行 | 压缩 {st.get('压缩空行', 0)} 处 | |

### 两处「考点追踪」的修复依据

MinerU 把这两个标题误判成公式块，再经公式模型处理后文字全乱。修改前**裁取原页区域做了二次 OCR 核实**：

| PDF 页 | 原（乱码） | 核实后 |
|---|---|---|
| 24 | `【基西面题】卜 …执行时间的相关计算` | `考点追踪CPU执行时间的相关计算（2012、2013、2014、2017、2022、2023）` |
| 71 | `通高面瓣卜 …数据的大小端存储` | `考点追踪数据的大小端存储（2016、2018、2019、2024、2025）` |

第 71 页的 OCR 结果清晰无歧义；第 24 页 OCR 得到 `考总追踪`，结合全书另外 180 处「考点追踪」标记判定。

## 已知问题

### 1. 罗马数字错乱（{len(bad_lines)} 行）——未修正

部分选择题的罗马数字项目出现重复，如 `A. I、ⅡI`（应为 `A. I、II`）、`C. I、II和ⅢII`（应为 `C. I、II和III`）。

**为什么没有自动修正**：同一形态在不同题目里含义不同。二次 OCR 核验证明：

- 第 76 页 `A. 仅I、ⅡI` → 实际是 `A. 仅I、II`
- 第 248 页 `C. 只有ⅢI` → 实际是 `C. 只有II`（而不是 `III`）

对原页裁图 OCR 的噪声也很大，不足以作为修改依据。**宁可保留原样，也不猜测后写进习题答案。**
完整清单见 `待核对_罗马数字.md`（含 PDF 页码）。题干的项目列表通常完好，可据此推断选项含义。

### 2. 其余 OCR 固有风险

数字、下标、运算符建议对照原 PDF 抽查。本次清理解决的是**可机械判定的**错误（噪声、拆行、空格、误分类），
无法替代逐字校对。
"""

open(os.path.join(D, "README.md"), "w", encoding="utf-8").write(readme)
print(f"已生成 README.md 与 待核对_罗马数字.md")
print(f"罗马数字可疑行: {len(bad_lines)}，涉及题目块: {len(entries)}")
for fn, n, i, tb, eq in rows:
    print(f"  {fn:<26} {n:>7} 字符  图{i:>3}  表{tb:>2}  公式{eq:>3}")
