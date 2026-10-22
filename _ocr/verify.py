# -*- coding: utf-8 -*-
"""验收最终 Markdown。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
MD = os.path.join(WORKDIR, "操作系统_Markdown", "王道操作系统.md")
lines = open(MD, encoding="utf-8").read().split("\n")
print("总行数:", len(lines), " 字符数:", sum(len(l) for l in lines))

print("\n=== 层级分布 ===")
for n in range(1, 7):
    c = sum(1 for l in lines if re.match(r"^" + "#" * n + r" ", l))
    if c:
        print(f"  H{n}: {c}")

print("\n=== 所有 H1 ===")
for l in lines:
    if re.match(r"^# ", l):
        print("  " + l)

print("\n=== 页标记检查 ===")
marks = [(i, int(m.group(1))) for i, l in enumerate(lines) if (m := re.search(r"<!-- page (\d+) of (\d+) -->", l))]
nums = [p for _, p in marks]
print(f"  数量={len(marks)}  范围={min(nums)}-{max(nums)}  严格递增={all(b > a for a, b in zip(nums, nums[1:]))}")
missing = sorted(set(range(1, 373)) - set(nums))
print(f"  缺失页: {missing if missing else '无'}")
# 页码与行号单调性
bad = [(marks[k][0], marks[k + 1][0]) for k in range(len(marks) - 1) if marks[k + 1][0] < marks[k][0]]
print(f"  行号回退的点: {len(bad)}")

print("\n=== 关键标题定位 ===")
for key in ["第2章 进程与线程", "第3章 内存管理", "第4章 文件管理", "第5章 输入/输出管理",
            "5.1.1 I/O设备", "5.1.3 I/O软件层次结构", "第1章 计算机系统概述"]:
    hit = [i for i, l in enumerate(lines) if l.strip().lstrip("#").strip() == key]
    print(f"  {'OK ' if hit else 'MISS'} {key}  -> 行 {hit[:3]}")

print("\n=== 第2章开头上下文 ===")
hit = [i for i, l in enumerate(lines) if l.strip() == "# 第2章 进程与线程"]
if hit:
    i = hit[0]
    for j in range(max(0, i - 6), min(i + 14, len(lines))):
        print(f"L{j:>6}: {lines[j][:120]}")
