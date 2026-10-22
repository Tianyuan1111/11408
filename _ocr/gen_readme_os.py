# -*- coding: utf-8 -*-
"""重新生成《操作系统》清理版 README（含习题摘出说明）。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "操作系统")
rep = {r["slug"]: r for r in json.load(
    open(os.path.join(WS, "_ocr", "clean_rest_report.json"), encoding="utf-8"))}["os"]
st = rep["stats"]

files = [f for f in sorted(os.listdir(D))
         if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")]
main_files = [f for f in files if "习题与解析" not in f]
ex_files = [f for f in files if "习题与解析" in f]

lv = Counter({1: len(files)})
allt = "\n".join(open(os.path.join(D, f), encoding="utf-8").read() for f in files)
for m in re.finditer(r"^(#{2,6})\s", allt, re.M):
    lv[len(m.group(1))] += 1

roman = sum(1 for f in main_files + ex_files
            for l in open(os.path.join(D, f), encoding="utf-8").read().split("\n")
            if re.search(r"[ⅠⅡⅢⅣ][ⅠI]|I{4,}", l))

def info(f):
    t = open(os.path.join(D, f), encoding="utf-8").read()
    return len(t), len(re.findall(r"!\[[^\]]*\]\([^)]+\)", t)), t.count("<table")

mrows = [(f, *info(f)) for f in main_files]
erows = [(f, *info(f)) for f in ex_files]
tot_main = sum(r[1] for r in mrows)
tot_ex = sum(r[1] for r in erows)

# 按章号配对，避免"参考文献"占位导致整列串位
pairs = []
for i in range(1, 6):
    mf = next((f for f in main_files if f.startswith(f"第{i}章")), None)
    ef = next((f for f in ex_files if f.startswith(f"第{i}章")), None)
    if mf and ef:
        pairs.append((i, mf, ef))

readme = f"""# 27王道《操作系统》· 清理版

由 `../操作系统_Markdown/王道操作系统.md` 清理、分章，并**把习题摘出**而成。

## 目录结构

```
操作系统_清理版/
""" + "".join(f"├── {f}\n" for f in main_files) + "".join(f"├── {f}   ← 习题与答案\n" for f in ex_files) + f"""├── 待核对_罗马数字.md   ← 无法自动修正的问题清单
├── README.md
└── images/                ← 全部文件共享，157 张
```

各文件以 `images/xxx.jpg` 相对路径引用图片；**移动单个文件时请一并带上 `images/` 目录。**
正文与习题文件共用同一份图片，习题里的配图不会缺失。

## 习题已摘出

原书把「本节习题精选」与「答案与解析」插在每个小节之后，占全文 **59%**。
现已按章摘到独立的 `第N章 习题与解析.md`，**正文中完全移除、不留痕迹**。

- 摘出依据：`### X.Y.Z 本节习题精选` 与 `### X.Y.Z 答案与解析` 两类 H3 标题（其下的 `#### 单项选择题`、`#### 二、综合应用题` 属该区块）。
- 区块标题**保留原小节编号**（如 `### 1.3.5 本节习题精选`），便于对照正文。
- 章节开头的"思考题参考答案"属于考点讲解的叙事部分，**未摘出**，仍在正文中。
- 无损性已验证：把正文与习题文件的行多重集合并，与重新生成的含习题版本逐行比对，**缺失 0 行**（多出的 10 行即两个文件的标题与来源说明）。

| 章节 | 摘出后正文 | 习题与解析 |
|---|---|---|
""" + "\n".join(
    f"| 第{i}章 | {dict((f, n) for f, n, _, _ in mrows).get(mf, 0):,} | "
    f"{dict((f, n) for f, n, _, _ in erows).get(ef, 0):,} |"
    for i, mf, ef in pairs
) + f"""

正文合计 **{tot_main:,}** 字符，习题与解析合计 **{tot_ex:,}** 字符。
摘出使正文减少 **59%**（288,111 字符的习题区块移出正文；上表为含换行的文件大小）。

## 各文件规模

| 文件 | 字符数 | 图片 | 表格 |
|---|---|---|---|
""" + "\n".join(f"| {f} | {n:,} | {i} | {tb} |" for f, n, i, tb in mrows + erows) + f"""

标题结构：一级 {lv[1]} 个、二级 {lv[2]} 个、三级 {lv[3]} 个、四级 {lv[4]} 个。
（其中三级/四级含习题文件的区块标题；正文单独统计与 PDF 书签一致。）

## 清理内容

| 项目 | 处理量 | 说明 |
|---|---|---|
| 前置页 | 删除 {st.get('删除前置页行数', 0)} 行 | 封面、版权/CIP、B站·微信·小程序推广、前言、致读者、王道训练营广告、目录页 |
| 页标记 | 删除 {st.get('删除页标记', 0)} 个 | `<!-- page N of M -->`（按你的选择一并删除） |
| 水印与广告 | 删除 {st.get('删除水印广告行', 0)} 行 | B站水印、打印店广告（考研小舟/包邮/淘宝书店）、「视频讲解」标记 |
| 行尾 OCR 噪声 | 删除 {st.get('删除行尾噪声', 0) + st.get('删除成串噪声', 0) + st.get('删除行中噪声', 0)} 处 | 句末标点后跟随的乱码字母串（`XT`/`XTA`/`K`/`MX`…） |
| 选项挤行 | 拆分 {st.get('拆分选项行', 0)} 行 | 选项原文常无空格（`A. xxxB. yyy`），已拆成独立行 |
| 选项标记 | 规范化 {st.get('选项标记规范化', 0)} 处 | `B.64` → `B. 64` |
| 选项间空行 | 合并 {st.get('合并选项间空行', 0)} 处 | PDF 分页把 D 与 A/B/C 隔开的情况 |
| 脚注 | 转换 {st.get('脚注转引用', 0)} 行 | `<small><span class="docvortex-page-footnote">` → `> 引用块` |
| 公式空格 | 规范化 {st.get('公式规范化', 0)} 处 | `1 0 ^ {{ 6 }}` → `10^{{6}}` |
| 连续空行 | 压缩 {st.get('压缩空行', 0)} 处 | |

### 清理规则的两条安全边界

- **围栏代码块内不做任何改动。** 代码里的 `A.length`、`C.data` 会被误认为选项标记，故按 ``` 围栏跳过。
- **选项标记只认点号。** 本书中顿号出现 89 处，经查全部是行文（`选项A、B、C`、答案 `13.B、A、C、D`），不是选项分隔符。

## 已知问题

### 1. 罗马数字错乱（{roman} 行）——未修正

部分选择题的罗马数字项目出现重复，如 `A. I、ⅡI`。**不做自动修正**，因为同一形态在不同题目含义不同
（在《计算机组成原理》上裁原页 OCR 核验过：同形 `ⅢI` 有的应为 `II`、有的应为 `III`）。
完整清单见 `待核对_罗马数字.md`。该清单同时覆盖正文与习题文件。

### 2. 其余 OCR 固有风险

数字、下标、运算符建议对照原 PDF 抽查。本次处理解决的是**可机械判定**的错误，不能替代逐字校对。
"""
open(os.path.join(D, "README.md"), "w", encoding="utf-8").write(readme)
print("README 已重新生成")
print(f"正文文件 {len(main_files)} 个 / 习题文件 {len(ex_files)} 个；正文 {tot_main:,} 字符，习题 {tot_ex:,} 字符")
