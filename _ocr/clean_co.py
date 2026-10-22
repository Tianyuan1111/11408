# -*- coding: utf-8 -*-
"""
《计算机组成原理》Markdown 清理 + 按章拆分。（v3 · 最终）

处理顺序很关键，v1/v2 的教训：
  - 噪声原本夹在「题干」与「选项 A」之间（行中），选项拆分后才被推到行尾，
    所以必须 **先拆选项、再降噪**，否则漏掉 8 行。
  - 公式规范化必须在修复"考点追踪"之前，否则数字仍被空格拆散（"2 0 2 3"）匹配不到。
  - 行中噪声混杂正常术语（CPU/SUB/DMA），因此中段只删「紧接选项标记之前」的那类，
    有明确结构信号才动手。
"""
import os, re, sys, json, shutil
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SRC_DIR = os.path.join(WORKDIR, "计算机组成原理_Markdown")
SRC_MD = os.path.join(SRC_DIR, "王道计算机组成原理.md")
OUT_DIR = os.path.join(BOOKDIR, "计算机组成原理")

FIX_BLOCKS = [
    (re.compile(r"【基西面题】卜.*?2023\s*\)"),
     "考点追踪CPU执行时间的相关计算（2012、2013、2014、2017、2022、2023）"),
    (re.compile(r"通高面瓣卜.*?2025\s*\)"),
     "考点追踪数据的大小端存储（2016、2018、2019、2024、2025）"),
]
SENT_END = r"。！？；：\)）】"
NOISE_END = re.compile(rf"([{SENT_END}])\s+([A-Z]{{1,6}})\s*$")          # 行尾噪声
NOISE_MULTI = re.compile(rf"([{SENT_END}])(\s+[A-Z]{{1,6}}){{2,}}\s*$")   # 成串噪声在行尾
NOISE_MID = re.compile(rf"([{SENT_END}])\s+[A-Z]{{1,6}}\s+(?=[A-D][.、]\s)")  # 行中、紧接选项
BOX = re.compile(r"\\(mathrm|mathsf|mathtt|texttt|text|mathbf|mathit)\s*\{([^{}]*)\}")
OPT_MARK = re.compile(r"([A-D])[.．]\s*")   # 只用点号；顿号在本书 71 处全是行文（"选项A、B"），不是选项标记
WATERMARK = ("官方开源", "bilibili.com", "考研小舟", "包邮", "taobao.com",
             "扫码关注“王道在线”", "遇到问题请加微信", "开通题库小程序VIP权限",
             "盗版书无兑换码")
FOOTNOTE = re.compile(
    r"<small><span class=\"docvortex-page-footnote\"[^>]*>(.*?)</span></small>", re.S)
PAGE_MARK = re.compile(r"^<!-- page \d+ of \d+ -->$")
CHAP_H1 = re.compile(r"^# (第\d+章.*|参考文献.*)$")
ILLEGAL_FN = str.maketrans({"/": "／", "\\": "＼", ":": "：", "*": "＊",
                            "?": "？", '"': "＂", "<": "＜", ">": "＞", "|": "｜"})

stats = Counter()
noise_tokens = Counter()
samples_math, samples_letters, samples_split = [], [], []


def split_options(line: str):
    """按 A./B./C./D. 标记拆分（标记前不要求空格，OCR 常把空格吃掉）。

    选项可能从任意字母开始——例如 A 在上一行，本行只有 B/C/D。
    因此对每个起点求最长连续递增序列，取最长的一个。
    """
    raw = [(m.group(1), m.start()) for m in OPT_MARK.finditer(line)]
    if len(raw) < 2:
        return [line]
    best = []
    for s in range(len(raw)):
        seq, expect = [raw[s]], "ABCD".index(raw[s][0])
        for ch, pos in raw[s + 1:]:
            if "ABCD".index(ch) == expect + 1:
                seq.append((ch, pos))
                expect += 1
        if len(seq) > len(best):
            best = seq
    if len(best) < 2:
        return [line]
    # 题干极短又非行首时，可能是误判
    if 0 < best[0][1] < 8:
        return [line]
    parts, stem = [], line[: best[0][1]].rstrip()
    if stem:
        parts.append(stem)
    for k, (ch, pos) in enumerate(best):
        end = best[k + 1][1] if k + 1 < len(best) else len(line)
        parts.append(line[pos:end].strip())
    return [p for p in parts if p]


def tidy_option_marker(s: str) -> str:
    """选项行统一成 'X. 内容'（OCR 常写成 'B.64'）。"""
    m = re.match(r"^([A-D])[.．]\s*(.*)$", s)
    if m and m.group(2):
        fixed = f"{m.group(1)}. {m.group(2)}"
        if fixed != s:
            stats["选项标记规范化"] += 1
        return fixed
    return s


def strip_noise(s: str) -> str:
    """行尾降噪：先处理成串，再处理单个。"""
    s2 = s.rstrip()
    m = NOISE_MULTI.search(s2)
    if m:
        stats["删除成串噪声"] += 1
        for t in re.findall(r"[A-Z]{1,6}", m.group(0)):
            noise_tokens[t] += 1
        return s2[: m.start(1) + 1]
    m = NOISE_END.search(s2)
    if m:
        noise_tokens[m.group(2)] += 1
        stats["删除行尾噪声"] += 1
        return s2[: m.start(2)].rstrip()
    return s2


def normalize_math(s: str) -> str:
    s = re.sub(r"(?<=\d)\s+(?=\d)", "", s)
    s = re.sub(r"\s*\^\s*", "^", s)
    s = re.sub(r"\s*_\s*", "_", s)
    s = re.sub(r"\{\s+", "{", s)
    s = re.sub(r"\s+\}", "}", s)
    # 逐字符空格：'S u b' -> 'Sub'（公式模型把每个字母都隔开了）。
    # 数学模式下空格本就被忽略，合并只影响源码可读性，不改变渲染结果。
    s = re.sub(r"\b([A-Za-z])(?: ([A-Za-z])){2,}\b",
               lambda m: m.group(0).replace(" ", ""), s)
    return s


def fix_letter_spacing(s: str) -> str:
    """\\mathrm { d o u b l e } -> \\mathrm{double}（逐字符空格是公式模型的识别毛病）"""
    def rep(m):
        cmd, inner = m.group(1), m.group(2)
        toks = inner.split()
        alpha = [t for t in toks if re.fullmatch(r"[A-Za-z]+", t)]
        if len(alpha) >= 3 and all(len(t) == 1 for t in alpha):
            new = re.sub(r"(?<=[A-Za-z0-9])\s+(?=[A-Za-z0-9])", "", inner)
            if len(samples_letters) < 12:
                samples_letters.append((f"\\{cmd}{{{inner}}}", f"\\{cmd}{{{new}}}"))
            stats["公式字母合并"] += 1
            return f"\\{cmd}{{{new}}}"
        return m.group(0)
    return BOX.sub(rep, s)


def fix_math_spans(text: str) -> str:
    def rep(m):
        body = m.group(2)
        fixed = normalize_math(body)
        if fixed != body:
            stats["公式空格规范化"] += 1
            if len(samples_math) < 8:
                samples_math.append((body[:70], fixed[:70]))
        return m.group(1) + fixed + m.group(3)
    text = re.sub(r"(\$\$)(.*?)(\$\$)", rep, text, flags=re.S)
    text = re.sub(r"(\$)([^$\n]+?)(\$)", rep, text)
    return fix_letter_spacing(text)


def main():
    raw = open(SRC_MD, encoding="utf-8").read()
    lines = raw.split("\n")
    print(f"原始: {len(lines)} 行, {len(raw)} 字符")

    start = next(i for i, l in enumerate(lines) if CHAP_H1.match(l))
    stats["删除前置页行数"] = start
    lines = lines[start:]

    # ---- 第一遍：结构性删除 ----
    kept = []
    for ln in lines:
        s = ln.strip()
        if PAGE_MARK.match(s):
            stats["删除页标记"] += 1
            continue
        if any(w in ln for w in WATERMARK) or s == "视频讲解":
            stats["删除水印广告行"] += 1
            continue
        if "docvortex-page-footnote" in ln:
            m = FOOTNOTE.search(ln)
            if m:
                kept.append("> " + m.group(1).strip())
                stats["脚注转引用"] += 1
                continue
        kept.append(ln)

    # ---- 第二遍：公式规范化 + 字母合并 ----
    text = fix_math_spans("\n".join(kept))
    kept = text.split("\n")

    # ---- 第三遍：修复误分类标记（去掉 $$ 包裹）----
    out, i = [], 0
    while i < len(kept):
        hit = next((good for pat, good in FIX_BLOCKS if pat.search(kept[i])), None)
        if hit is not None:
            if out and out[-1].strip() == "$$":
                out.pop()
            if i + 1 < len(kept) and kept[i + 1].strip() == "$$":
                i += 1
            out += [hit, ""]
            stats["修复误分类标记"] += 1
            i += 1
            continue
        out.append(kept[i])
        i += 1
    kept = out

    # ---- 第四遍：先删"行中·紧接选项"的噪声，再拆选项，最后逐段降噪 ----
    out = []
    for ln in kept:
        s = ln
        if NOISE_MID.search(s):
            s = NOISE_MID.sub(r"\1 ", s)
            stats["删除行中噪声"] += 1
        if re.search(r"[A-D][.．]\s*", s):
            parts = split_options(s.strip())
            if len(parts) > 1:
                if len(samples_split) < 3:
                    samples_split.append((s.strip()[:100], parts))
                stats["拆分选项行"] += 1
                out.extend(tidy_option_marker(strip_noise(p)) for p in parts)
                out.append("")
                continue
        out.append(tidy_option_marker(strip_noise(s)))

    text = "\n".join(out)
    before = text.count("\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    stats["压缩空行"] = before - text.count("\n")

    # 选项块内部的空行（PDF 分页造成 D 与 A/B/C 被隔开）-> 去掉，让选项连续
    ls = text.split("\n")
    merged, k = [], 0
    while k < len(ls):
        if (k > 0 and k + 1 < len(ls) and not ls[k].strip()
                and re.match(r"^[A-D][.．]\s", ls[k - 1].strip())
                and re.match(r"^[A-D][.．]\s", ls[k + 1].strip())):
            stats["合并选项间空行"] += 1
            k += 1
            continue
        merged.append(ls[k])
        k += 1
    text = "\n".join(merged)
    lines = text.split("\n")

    # ---- 按章拆分 ----
    os.makedirs(OUT_DIR, exist_ok=True)
    chapters, cur_title, cur_body = [], None, []
    for ln in lines:
        if CHAP_H1.match(ln.strip()):
            if cur_title is not None:
                chapters.append((cur_title, cur_body))
            cur_title, cur_body = ln.strip()[2:].strip(), []
        elif cur_title is not None:
            cur_body.append(ln)
    if cur_title is not None:
        chapters.append((cur_title, cur_body))

    print(f"\n切分得到 {len(chapters)} 个章节:")
    files = []
    for title, body in chapters:
        content = "\n".join(body).strip() + "\n"
        fn = title.translate(ILLEGAL_FN) + ".md"
        open(os.path.join(OUT_DIR, fn), "w", encoding="utf-8").write(
            f"# {title}\n\n> 来源：27王道《计算机组成原理》高清带书签.pdf（已清理水印、广告与 OCR 噪声）\n\n{content}")
        files.append((fn, title, content))
        print(f"  {fn:<26} {len(content):>7} 字符")

    # ---- 图片 ----
    src_img = os.path.join(SRC_DIR, "images")
    dst_img = os.path.join(OUT_DIR, "images")
    if os.path.isdir(dst_img):
        shutil.rmtree(dst_img)
    os.makedirs(dst_img, exist_ok=True)
    all_text = "\n".join(c for _, _, c in files)
    refs = {os.path.basename(p) for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", all_text)}
    copied = missing = 0
    for name in sorted(refs):
        src = os.path.join(src_img, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dst_img, name))
            copied += 1
        else:
            missing += 1
    stats["图片复制"] = copied

    # ---- 报告 ----
    print("\n=== 清理统计 ===")
    for k, v in stats.items():
        print(f"  {k:<16} {v}")

    resid = []
    for fn, _, c in files:
        for j, l in enumerate(c.split("\n")):
            if NOISE_END.search(l.rstrip()) or NOISE_MULTI.search(l.rstrip()):
                resid.append((fn, j, l.strip()[-60:]))
    print(f"\n  残余行尾噪声    {len(resid)}")
    for fn, j, t in resid:
        print(f"      {fn} L{j}: …{t}")
    print(f"  残余水印        {sum(all_text.count(w) for w in WATERMARK)}")
    print(f"  残余页标记      {len(re.findall(r'<!-- page', all_text))}")
    print(f"  残余脚注HTML    {all_text.count('docvortex-page-footnote')}")
    print(f"  残余乱码标记    {all_text.count('基西面题') + all_text.count('通高面瓣')}")
    print(f"  残余逐字空格    {len(re.findall(r'(?:[A-Za-z] ){3,}', all_text))}")
    print(f"  图片: 引用 {len(refs)}，复制 {copied}，缺失 {missing}")

    print(f"\n=== 公式字母合并样例 ===")
    for a, b in samples_letters:
        print(f"  {a}\n      -> {b}")
    print(f"\n=== 选项拆分样例 ===")
    for a, b in samples_split:
        print(f"  原: {a}")
        for p in b:
            print(f"      {p[:80]}")

    json.dump({"stats": dict(stats), "files": [f for f, _, _ in files],
               "noise_tokens": dict(noise_tokens),
               "residual_noise": [{"file": f, "line": j, "text": t} for f, j, t in resid]},
              open(os.path.join(WS, "_ocr", "co_clean_report.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n输出目录: {OUT_DIR}")


if __name__ == "__main__":
    main()
