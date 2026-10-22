# -*- coding: utf-8 -*-
"""
通用习题摘出（数据结构 / 计算机组成原理 / 计算机网络）。

各书的习题标题形式不同，规则取并集：
  数据结构      -> ### X.Y.Z 本节试题精选   + ### X.Y.Z 答案与解析
  计算机组成原理 -> ### X.Y.Z 本节习题精选   + ### X.Y.Z 答案与解析
  计算机网络    -> ### X.Y.Z 本节习题精选   + ### X.Y.Z 答案与解析
区块范围到下一个 H2/H3 为止；其下的 #### 单项选择题 等属于该区块。

安全性：
  - 先备份章节文件，摘出后按行多重集比对，证明无损（只多出习题文件的标题与来源说明）。
  - 围栏代码块不影响（习题区不会跨代码块）。
用法: python extract_ex.py <ds|co|cn>
"""
import os, re, sys, shutil
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = {
    "ds": ("数据结构", os.path.join(BOOKDIR, "数据结构")),
    "co": ("计算机组成原理", os.path.join(BOOKDIR, "计算机组成原理")),
    "cn": ("计算机网络", os.path.join(BOOKDIR, "计算机网络")),
}
EX_RE = re.compile(r"^###\s+.*?(本节习题精选|本节试题精选|习题精选|试题精选|"
                   r"答案与解析|本章习题|本章试题)\s*$")
HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
H23 = re.compile(r"^#{2,3}\s")


def run(slug):
    name, outdir = BOOKS[slug]
    D = os.path.join(WS, outdir)
    BK = os.path.join(WS, "_ocr", f"{slug}_pre_extract")

    # 0) 清理旧版命名（组成原理第1章曾手工拆成 _习题.md）
    stale = [f for f in os.listdir(D) if f.endswith("_习题.md")]
    files = [f for f in sorted(os.listdir(D)) if f.endswith(".md")
             and f != "README.md" and not f.startswith("待核对")
             and "习题与解析" not in f and f not in stale]

    # 1) 备份
    if os.path.isdir(BK):
        shutil.rmtree(BK)
    os.makedirs(BK)
    for f in files:
        shutil.copy2(os.path.join(D, f), os.path.join(BK, f))

    print("=" * 76)
    print(f"### {name}   （{len(files)} 个章节文件）")
    print("=" * 76)

    made = []
    for f in files:
        p = os.path.join(D, f)
        lines = open(p, encoding="utf-8").read().split("\n")
        if not any(EX_RE.match(l.strip()) for l in lines):
            print(f"  {f}: 无习题区块，跳过")
            continue

        ranges = []
        for i, l in enumerate(lines):
            if EX_RE.match(l.strip()):
                j = i + 1
                while j < len(lines) and not H23.match(lines[j]):
                    j += 1
                ranges.append((i, j))
        merged = []
        for a, b in ranges:
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else:
                merged.append((a, b))

        ex, main, k = [], [], 0
        for a, b in merged:
            main.extend(lines[k:a])
            ex.extend(lines[a:b])
            ex.append("")
            k = b
        main.extend(lines[k:])

        open(p, "w", encoding="utf-8").write(
            re.sub(r"\n{3,}", "\n\n", "\n".join(main)).rstrip() + "\n")

        m = HEAD.match(lines[0])
        title = m.group(2).strip() if m else f[:-3]
        ex_name = f"{f.split()[0]} 习题与解析.md"
        open(os.path.join(D, ex_name), "w", encoding="utf-8").write(
            f"# {title} · 习题与解析\n\n"
            f"> 由《{title}》正文摘出；区块标题保留了原书的小节编号。\n\n"
            + re.sub(r"\n{3,}", "\n\n", "\n".join(ex)).strip() + "\n")
        made.append(ex_name)
        print(f"  {f}: 摘出 {len(merged)} 个区块 -> {ex_name}")

    # 2) 无损校验：备份行多重集 vs (新正文 + 习题文件)
    def bag(paths):
        c = Counter()
        for p in paths:
            for l in open(p, encoding="utf-8").read().split("\n"):
                if l.strip():
                    c[l.rstrip()] += 1
        return c

    before = bag([os.path.join(BK, f) for f in files])
    now_files = [os.path.join(D, f) for f in sorted(os.listdir(D))
                 if f.endswith(".md") and f != "README.md" and not f.startswith("待核对")]
    after = bag(now_files)
    missing = before - after
    extra = after - before
    print(f"\n  无损校验: 备份 {sum(before.values())} 行 -> 现在 {sum(after.values())} 行")
    print(f"    缺失 {sum(missing.values())} 行；多出 {sum(extra.values())} 行")
    for l, n in list(missing.items())[:6]:
        print(f"      缺 {n}x {l[:88]}")
    for l, n in list(extra.items())[:6]:
        print(f"      多 {n}x {l[:88]}")

    # 3) 删除旧命名文件（内容已并入新的习题文件）
    for f in stale:
        p = os.path.join(D, f)
        old = bag([p])
        lost = old - after
        if lost:
            print(f"  !! 旧文件 {f} 有 {sum(lost.values())} 行未并入，保留不删")
        else:
            os.remove(p)
            print(f"  已删除旧命名文件 {f}（内容已并入）")
    return missing


if __name__ == "__main__":
    slugs = [sys.argv[1]] if len(sys.argv) > 1 else ["ds", "co", "cn"]
    bad = 0
    for s in slugs:
        if run(s):
            bad += 1
    print("\n结论:", "全部无损" if bad == 0 else f"{bad} 本存在缺失，需排查")
