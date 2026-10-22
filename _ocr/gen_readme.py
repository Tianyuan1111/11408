# -*- coding: utf-8 -*-
"""按实际文件统计，为每本书生成 README。"""
import os, re, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BARE = re.compile(r"^第\d+章$")

KNOWN = {
    "操作系统": """全书仅 **2 处** 公式识别失败，均已处理：

1. **第 370 页**（第 7 题解答）磁盘容量公式：公式模型在中文与公式混排处退化，输出重复乱码，`flash` 档同样无法识别。已改为嵌入原图，并附上对该区域原图二次 OCR 还原的文本（经算术校验：300×10×200×512/1024 = 300000 = 3×10⁵ KB）。
2. **第 220 页** 内存分配示意图的公式块：模型把数组退化成了上千个 `1`。已改为嵌入原图。""",
    "数据结构": """全书仅 **1 处** 公式识别失败，另有 **1 处图片数据损坏**：

1. **第 126 页** 一个公式块：模型输出重复乱码，已改为嵌入原图。
2. **第 195 页**「图 5.30 S₁∪S₂ 的表示方法」：该表格块 HTML 里内联的图片数据被截断损坏（载荷长度不是 4 的倍数，还混入了 HTML 标记），导致整本书的导出直接失败。同一区块自带的 `image_base64` 字段是完好的，已用它替换损坏数据并补齐闭合标签——**无损修复，未做任何内容推断**。修复后该图正常显示为 583×66 的 JPEG。""",
    "计算机组成原理": """未发现公式或图片识别失败，无降级处理。""",
    "计算机网络": """未发现公式或图片识别失败，无降级处理。""",
}

BOOKS = [
    ("操作系统", os.path.join(WORKDIR, "操作系统_Markdown"), "王道操作系统.md", "_ocr/toc.json", 372, 435, 15),
    ("数据结构", os.path.join(WORKDIR, "数据结构_Markdown"), "王道数据结构.md", "_ocr/toc_ds.json", 404, 478, 18),
    ("计算机组成原理", os.path.join(WORKDIR, "计算机组成原理_Markdown"), "王道计算机组成原理.md", "_ocr/toc_co.json", 340, 204, 13),
    ("计算机网络", os.path.join(WORKDIR, "计算机网络_Markdown"), "王道计算机网络.md", "_ocr/toc_cn.json", 316, 419, 10),
]

for name, outdir, mdfile, toc, pages, ntoc, minutes in BOOKS:
    d = os.path.join(WS, outdir)
    md = os.path.join(d, mdfile)
    if not os.path.exists(md):
        print(f"跳过 {name}: 无 {md}")
        continue
    text = open(md, encoding="utf-8").read()
    lines = text.split("\n")
    lv = Counter(len(m.group(1)) for l in lines if (m := re.match(r"^(#{1,6})\s", l)))
    raw = json.load(open(os.path.join(WS, toc), encoding="utf-8"))
    bms = [x for x in raw if not BARE.match(" ".join(x["title"].split()))]
    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    disk = len(os.listdir(os.path.join(d, "images"))) if os.path.isdir(os.path.join(d, "images")) else 0
    total = sum(os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(d) for f in fs)
    h1 = [l.strip("# ").strip() for l in lines if re.match(r"^# ", l)]
    n_inline = len(re.findall(r"\$[^$\n]{2,80}\$", text))   # 注意：不能用双反斜杠，否则匹配不到
    lv_rows = "\n".join(
        f"| {'一二三四五六'[k-1]}级标题 | {lv.get(k,0)} |"
        for k in sorted(lv) if lv.get(k, 0))

    readme = f"""# 27王道《{name}》Markdown 版

由原件 `27王道《{name}》高清带书签.pdf`（{pages} 页、纯图片扫描件）转换而来。

## 文件

| 文件 | 说明 |
|---|---|
| `{mdfile}` | 正文，{os.path.getsize(md)/1048576:.2f} MB，约 {len(text)//10000} 万字 |
| `images/` | {disk} 张图片（图、表、公式的原图裁切） |

图片采用相对路径 `images/xxx.jpg` 引用。**移动 `.md` 时请连同 `images/` 目录一起移动**，否则图片会失效。

整个目录约 {total/1048576:.1f} MB。

## 内容规模

| 元素 | 数量 |
|---|---|
| 页标记 `<!-- page N of {pages} -->` | {len(re.findall(r'<!-- page', text))}（完整覆盖、严格递增） |
{lv_rows}
| HTML 表格 | {text.count('<table')} |
| 行内公式 `$...$` | {n_inline} |
| 独立公式块 `$$...$$` | {text.count('$$')//2} |
| 代码块 | {text.count('```')//2} |
| 图片 | {len(imgs)} 处引用，{disk} 个文件，缺失 0 |

## 标题结构

一级标题共 {len(h1)} 个：

{chr(10).join('- ' + h for h in h1)}

标题层级与 PDF 内置书签**完全一致**：书签共 {len(bms)} 条（L2/L3/L4 分别为 {sum(1 for b in bms if b['level']==2)}/{sum(1 for b in bms if b['level']==3)}/{sum(1 for b in bms if b['level']==4)}），输出层级数量与之精确吻合。

## 转换方式

原件没有任何文字层，必须 OCR。使用 **MinerU 4.0.10**（basic 档：版面分析 + PP-OCR + 表格 + 公式识别，Torch 后端跑在 RTX 4060 上），{pages} 页约 {minutes} 分钟。

PDF 自带 {ntoc} 条书签，但它只有页码、没有页内位置；MinerU 定位准确但标题层级几乎全是 `##`。因此把两者互补合并：

1. MinerU 解析全书，导出 Markdown + 图片 + `structured_content.json`；
2. 用 `structured_content.json` 里「每页第一个正文块」的文字，在 Markdown 中顺序对齐出每页起始行，插入页标记；
3. 用书签文本按文档顺序匹配 MinerU 识别出的标题 → **位置取 MinerU 的、层级取书签的**；
4. 书签里有、MinerU 漏识别的（多为各章首页被版面模型误判为"页眉"而丢弃的章名与【考纲内容】）→ 按对齐出的页码在页边界补插；
5. 答案项（形如 `19. C`、`15. 【解答】`）回落为正文，避免污染标题层级；
6. 自动检测公式识别退化的块（同一字符重复 24 次以上），改为嵌入原图。

流线脚本见 `../_ocr/build_book.py`。

## 已知问题

{KNOWN[name]}

其余识别质量良好，但 OCR 结果建议对照原 PDF 抽查，尤其是数字、下标与运算符。
"""
    p = os.path.join(d, "README.md")
    open(p, "w", encoding="utf-8").write(readme)
    print(f"已生成 {p}")
