# -*- coding: utf-8 -*-
"""验证摘出无损：重新生成含习题的章节，比对行多重集。"""
import os, re, subprocess, sys, shutil
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
D = os.path.join(BOOKDIR, "操作系统")
BACKUP = os.path.join(WS, "_ocr", "os_after_extract")

FENCE = "`" * 3


def linebag(pattern_filter):
    """返回目录下匹配文件的非空行多重集（跳过脚本自己生成的说明文件）。"""
    bag = Counter()
    for f in sorted(os.listdir(D)):
        if not f.endswith(".md") or f == "README.md" or f.startswith("待核对"):
            continue
        if not pattern_filter(f):
            continue
        for l in open(os.path.join(D, f), encoding="utf-8").read().split("\n"):
            if l.strip():
                bag[l.rstrip()] += 1
    return bag


# 1) 当前的「正文 + 习题」多重集
before = linebag(lambda f: True)
print(f"当前（正文+习题）非空行多重集: {sum(before.values())} 行")

# 2) 备份当前结果
if os.path.isdir(BACKUP):
    shutil.rmtree(BACKUP)
shutil.copytree(D, BACKUP, ignore=shutil.ignore_patterns("images"))

# 3) 重新生成含习题的章节文件
r = subprocess.run([sys.executable, os.path.join(WS, "_ocr", "clean_book.py"), "os"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print("重新生成:", "成功" if r.returncode == 0 else f"失败 rc={r.returncode}")
if r.returncode != 0:
    print(r.stdout[-2000:]); print(r.stderr[-2000:]); raise SystemExit(1)

# 4) 重新生成后的多重集（只取章节文件，不含习题文件——此时尚未摘出）
after = Counter()
for f in sorted(os.listdir(D)):
    if not f.endswith(".md") or "习题与解析" in f or f == "README.md" or f.startswith("待核对"):
        continue
    for l in open(os.path.join(D, f), encoding="utf-8").read().split("\n"):
        if l.strip():
            after[l.rstrip()] += 1
print(f"重新生成（仅章节）非空行多重集: {sum(after.values())} 行")

# 5) 比对：after 应等于 before 中"章节相关"的部分。
#    由于 before 含习题文件、after 不含，直接比 before(仅章节路径) vs after。
missing = after - before      # 重新生成里有、当前没有 -> 内容丢失
extra = before - after        # 当前有、重新生成里没有 -> 内容凭空多出
print(f"\n重新生成有而当前缺: {sum(missing.values())} 行")
for l, n in list(missing.items())[:10]:
    print(f"   缺 {n}x {l[:90]}")
print(f"当前有而重新生成无: {sum(extra.values())} 行")
for l, n in list(extra.items())[:10]:
    print(f"   多 {n}x {l[:90]}")

print("\n结论:", "一致（摘出无损）" if not missing else "存在缺失，需排查")
print(f"备份在: {BACKUP}")
