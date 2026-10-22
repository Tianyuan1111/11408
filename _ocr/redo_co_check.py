# -*- coding: utf-8 -*-
"""备份组成原理当前状态 -> 重新生成含习题的版本 -> 逐文件比对差异。"""
import os, sys, shutil, subprocess, difflib
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "计算机组成原理")
BK = os.path.join(WS, "_ocr", "co_before_redo")

# 1) 备份（不含 images）
if os.path.isdir(BK):
    shutil.rmtree(BK)
os.makedirs(BK)
for f in os.listdir(D):
    src = os.path.join(D, f)
    if os.path.isfile(src):
        shutil.copy2(src, os.path.join(BK, f))
print(f"已备份 {len(os.listdir(BK))} 个文件 -> {BK}")

# 2) 重新生成（clean_co.py 会把习题写回各章）
r = subprocess.run([sys.executable, os.path.join(WS, "_ocr", "clean_co.py")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print("重新生成:", "成功" if r.returncode == 0 else f"失败 rc={r.returncode}")
if r.returncode != 0:
    print(r.stdout[-1500:]); print(r.stderr[-1500:]); raise SystemExit(1)
print("   ", [l for l in r.stdout.split("\n") if "输出目录" in l])

# 3) 逐文件比对
print("\n=== 与备份的差异（重新生成 vs 你手上的版本）===")
old = set(os.listdir(BK))
new = {f for f in os.listdir(D) if os.path.isfile(os.path.join(D, f))}
print(f"仅备份有（重新生成会删除？不会自动删）: {sorted(old - new)}")
print(f"仅新版本有: {sorted(new - old)}")
for f in sorted(old & new):
    a = open(os.path.join(BK, f), encoding="utf-8").read().split("\n")
    b = open(os.path.join(D, f), encoding="utf-8").read().split("\n")
    if a == b:
        print(f"  {f:<34} 完全相同")
    else:
        d = [l for l in difflib.unified_diff(a, b, lineterm="", n=0)][:8]
        adds = sum(1 for l in d if l.startswith("+") and not l.startswith("+++"))
        dels = sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
        print(f"  {f:<34} 有差异（+{adds}/-{dels} 行，仅显示前几条）")
        for l in d[2:8]:
            print(f"        {l[:100]}")
