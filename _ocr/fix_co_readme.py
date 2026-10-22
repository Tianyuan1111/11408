# -*- coding: utf-8 -*-
"""修正组成原理 README 里的图片占位符示例（原写法会被检查脚本当成真实引用）。"""
import os
import sys

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

sys.stdout.reconfigure(encoding="utf-8")

p = os.path.join(BOOKDIR, '计算机组成原理', 'README.md')
t = open(p, encoding="utf-8").read()
old = "各章文件均以 `![](images/xxx.jpg)` 相对路径引用图片。"
new = "各章文件均以 `images/xxx.jpg` 这样的相对路径引用图片。"
if old in t:
    open(p, "w", encoding="utf-8").write(t.replace(old, new))
    print("已替换")
else:
    print("未找到目标文本")
    import re
    m = re.search(r".{0,50}xxx\.jpg.{0,50}", t)
    print("实际:", m.group(0) if m else "无")
