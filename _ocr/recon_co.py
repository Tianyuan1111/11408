# -*- coding: utf-8 -*-
"""侦察《计算机组成原理》Markdown 的内容形态：水印/广告/重复行/格式问题。"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
MD = os.path.join(WORKDIR, "计算机组成原理_Markdown", "王道计算机组成原理.md")
text = open(MD, encoding="utf-8").read()
lines = text.split("\n")
print(f"总行数={len(lines)}  字符数={len(text)}")

print("\n=== 1. 高频重复行（可能是水印/页脚，出现 >=5 次）===")
c = Counter(l.strip() for l in lines if l.strip() and not l.strip().startswith("<!--"))
for line, n in c.most_common(40):
    if n >= 5:
        print(f"  {n:>4} 次 | {line[:110]}")

print("\n=== 2. 广告/水印关键词命中 ===")
KW = ["淘宝", "微信", "扫码", "关注", "公众号", "包邮", "下单", "备注", "QQ", "群",
      "训练营", "视频讲解", "赠送", "优惠", "客服", "购买", "正版", "盗版", "印刷",
      "店铺", "小舟", "草稿纸", "5分/页", "分/页", "二维码", "知乎", "bilibili",
      "www.", "http", "版权所有", "侵权", "翻印", "举报", "咨询", "加群"]
hits = Counter()
examples = {}
for i, l in enumerate(lines):
    for k in KW:
        if k in l:
            hits[k] += 1
            examples.setdefault(k, (i, l.strip()[:120]))
for k, n in hits.most_common():
    i, ex = examples[k]
    print(f"  {k:<8} {n:>4} 次 | 例(L{i}): {ex}")

print("\n=== 3. 含图片但无图注的行（可能是水印图/二维码）===")
img_only = [i for i, l in enumerate(lines) if re.fullmatch(r"!\[[^\]]*\]\([^)]+\)", l.strip())]
print(f"  纯图片行总数: {len(img_only)}")
for i in img_only[:15]:
    nxt = lines[i + 1].strip()[:60] if i + 1 < len(lines) else ""
    prv = lines[i - 1].strip()[:60] if i > 0 else ""
    print(f"    L{i}: 前[{prv}] 后[{nxt}]")

print("\n=== 4. 格式异常统计 ===")
print(f"  空行: {sum(1 for l in lines if not l.strip())}")
print(f"  仅含标点/空格的行: {sum(1 for l in lines if l.strip() and not re.search(r'[\\w\\u4e00-\\u9fff]', l))}")
print(f"  加粗行(**...**): {sum(1 for l in lines if re.fullmatch(r'\\*\\*.+\\*\\*', l.strip()))}")
print(f"  以 - 或数字. 开头的疑似残留列表: {sum(1 for l in lines if re.match(r'^[-•]\\s|^\\d+[.、]\\s', l.strip()))}")
print(f"  表格块 <table>: {text.count('<table')}")
print(f"  含连续 >=3 空格的行: {sum(1 for l in lines if re.search(r'   +', l))}")

print("\n=== 5. 页标记与章节 ===")
marks = re.findall(r"<!-- page (\d+) of (\d+) -->", text)
print(f"  页标记 {len(marks)} 个")
h1 = [(i, l.strip("# ").strip()) for i, l in enumerate(lines) if re.match(r"^# ", l)]
print(f"  一级标题 {len(h1)} 个:")
for i, t in h1:
    print(f"    L{i:>6}  {t}")
