# -*- coding: utf-8 -*-
"""
通用清理 + 按章拆分（操作系统 / 数据结构 / 计算机网络）。

规则与《计算机组成原理》一致，但每本的关键参数均按本实测：
  - 选项标记：三本都只用半角点（全角点 0 处）；顿号 89/92/89 处经查全是行文
    （"选项A、B、C"、"序列A、B、C"、答案"13.B、A、C、D"），故只认点号。
  - 三本均无"标题被误判为公式块"的情况，不需要定点修复。
用法: python clean_book.py <os|ds|cn>
"""
import os, re, sys, json, shutil
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = {
    "os": {"name": "操作系统",   "src": os.path.join(WORKDIR, '操作系统_Markdown', '王道操作系统.md'),   "out": os.path.join(BOOKDIR, "操作系统")},
    "ds": {"name": "数据结构",   "src": os.path.join(WORKDIR, '数据结构_Markdown', '王道数据结构.md'),   "out": os.path.join(BOOKDIR, "数据结构")},
    "cn": {"name": "计算机网络", "src": os.path.join(WORKDIR, '计算机网络_Markdown', '王道计算机网络.md'), "out": os.path.join(BOOKDIR, "计算机网络")},
}

SENT_END = r"。！？；：\)）】"
NOISE_END = re.compile(rf"([{SENT_END}])\s+([A-Z]{{1,6}})\s*$")
NOISE_MULTI = re.compile(rf"([{SENT_END}])(\s+[A-Z]{{1,6}}){{2,}}\s*$")
NOISE_MID = re.compile(rf"([{SENT_END}])\s+[A-Z]{{1,6}}\s+(?=[A-D][.．]\s)")
BOX = re.compile(r"\\(mathrm|mathsf|mathtt|texttt|text|mathbf|mathit)\s*\{([^{}]*)\}")
OPT_MARK = re.compile(r"([A-D])[.．]\s*")
FOOTNOTE = re.compile(
    r"<small><span class=\"docvortex-page-footnote\"[^>]*>(.*?)</span></small>", re.S)
PAGE_MARK = re.compile(r"^<!-- page \d+ of \d+ -->$")
# 只保留正式章节；前言/致读者/王道训练营/目录 都在这之前，一并丢弃
CHAP_KEEP = re.compile(r"^# (第\d+章.*|参\s*考\s*文\s*献.*)$")
WATERMARK = ("官方开源", "bilibili.com", "考研小舟", "包邮", "taobao.com",
             "扫码关注", "遇到问题请加微信", "开通题库小程序VIP权限", "盗版书无兑换码")
ILLEGAL_FN = str.maketrans({"/": "／", "\\": "＼", ":": "：", "*": "＊",
                            "?": "？", '"': "＂", "<": "＜", ">": "＞", "|": "｜"})

stats = Counter()
noise_tokens = Counter()
samples = {"math": [], "letters": [], "split": []}


def normalize_math(s: str) -> str:
    s = re.sub(r"(?<=\d)\s+(?=\d)", "", s)
    s = re.sub(r"\s*\^\s*", "^", s)
    s = re.sub(r"\s*_\s*", "_", s)
    s = re.sub(r"\{\s+", "{", s)
    s = re.sub(r"\s+\}", "}", s)
    s = re.sub(r"\b([A-Za-z])(?: ([A-Za-z])){2,}\b", lambda m: m.group(0).replace(" ", ""), s)
    return s


def fix_letter_spacing(s: str) -> str:
    def rep(m):
        cmd, inner = m.group(1), m.group(2)
        toks = inner.split()
        alpha = [t for t in toks if re.fullmatch(r"[A-Za-z]+", t)]
        if len(alpha) >= 3 and all(len(t) == 1 for t in alpha):
            new = re.sub(r"(?<=[A-Za-z0-9])\s+(?=[A-Za-z0-9])", "", inner)
            if len(samples["letters"]) < 8:
                samples["letters"].append((f"\\{cmd}{{{inner}}}", f"\\{cmd}{{{new}}}"))
            stats["公式字母合并"] += 1
            return f"\\{cmd}{{{new}}}"
        return m.group(0)
    return BOX.sub(rep, s)


def fix_math_spans(text: str) -> str:
    def rep(m):
        fixed = normalize_math(m.group(2))
        if fixed != m.group(2):
            stats["公式规范化"] += 1
        return m.group(1) + fixed + m.group(3)
    text = re.sub(r"(\$\$)(.*?)(\$\$)", rep, text, flags=re.S)
    text = re.sub(r"(\$)([^$\n]+?)(\$)", rep, text)
    return fix_letter_spacing(text)


def split_options(line: str):
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
    if 0 < best[0][1] < 8:
        return [line]
    parts, stem = [], line[: best[0][1]].rstrip()
    if stem:
        parts.append(stem)
    for k, (ch, pos) in enumerate(best):
        end = best[k + 1][1] if k + 1 < len(best) else len(line)
        parts.append(line[pos:end].strip())
    return [p for p in parts if p]


def fix_math_spans_outside_fences(text: str) -> str:
    """只在围栏代码块之外做公式规范化——代码里的 $ 不该被动。"""
    out, buf, in_fence = [], [], False
    for ln in text.split("\n"):
        if ln.strip().startswith("```"):
            if buf:
                out.append(fix_math_spans("\n".join(buf)))
                buf = []
            out.append(ln)
            in_fence = not in_fence
            continue
        (out if in_fence else buf).append(ln)
    if buf:
        out.append(fix_math_spans("\n".join(buf)))
    return "\n".join(out)


def tidy_option_marker(s: str) -> str:
    m = re.match(r"^([A-D])[.．]\s*(.*)$", s)
    if m and m.group(2):
        fixed = f"{m.group(1)}. {m.group(2)}"
        if fixed != s:
            stats["选项标记规范化"] += 1
        return fixed
    return s


def strip_noise(s: str) -> str:
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


QNUM = re.compile(r"^(\d{1,2})[.、]\s")
OPT_HEAD = re.compile(r"^[A-D][.．]\s*")


def split_at_question(s: str, expected_q):
    """在"选项内容末尾粘连的下题题号"处切开；返回 [head, tail] 或 None。

    题号顺序递增，所以用预期题号（如 "06."）去定位切点，
    比猜数字边界（"45706." 到底是 457+06 还是 45+706）可靠。
    """
    key = f"{expected_q:02d}."
    for m in re.finditer(re.escape(key), s):
        if m.start() == 0:
            continue
        rest = s[m.end():]
        if rest[:1].isspace() or re.match(r"[\u4e00-\u9fff]", rest[:1] or " "):
            return [s[: m.start()].rstrip(), s[m.start():].strip()]
    return None


def emit(s: str):
    """对一行做选项拆分 / 降噪 / 标记规范化，返回若干行。"""
    parts = split_options(s.strip()) if re.search(r"[A-D][.．]\s*", s) else [s]
    if len(parts) > 1:
        stats["拆分选项行"] += 1
        if len(samples["split"]) < 2:
            samples["split"].append((s.strip()[:90], parts))
        return [tidy_option_marker(strip_noise(p)) for p in parts] + [""]
    return [tidy_option_marker(strip_noise(s))]


def build(slug):
    cfg = BOOKS[slug]
    name = cfg["name"]
    src = os.path.join(WS, cfg["src"])
    out_dir = os.path.join(WS, cfg["out"])
    src_img = os.path.join(os.path.dirname(src), "images")

    # 全局计数器按本重置（否则三本的统计会互相累加）
    stats.clear()
    noise_tokens.clear()
    for v in samples.values():
        v.clear()

    lines = open(src, encoding="utf-8").read().split("\n")
    print("=" * 76)
    print(f"### {name}   ({len(lines)} 行)")
    print("=" * 76)

    start = next((i for i, l in enumerate(lines) if CHAP_KEEP.match(l.strip())), None)
    assert start is not None, "未找到章节起点"
    stats["删除前置页行数"] = start
    lines = lines[start:]

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

    text = fix_math_spans_outside_fences("\n".join(kept))
    kept = text.split("\n")

    out, in_fence, expected_q = [], False, None
    for ln in kept:
        # 围栏代码块内一律原样保留：C 代码里的 A.length / C.data 会被误当成选项标记
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            out.append(ln)
            continue
        if in_fence:
            out.append(ln)
            continue
        s = ln
        if NOISE_MID.search(s):
            s = NOISE_MID.sub(r"\1 ", s)
            stats["删除行中噪声"] += 1

        m = QNUM.match(s.strip())
        if m:
            expected_q = int(m.group(1)) + 1
        elif expected_q is not None and OPT_HEAD.search(s):
            # 选项内容末尾粘了下题题号（"D. 1007." = "D. 10" + "07."）。
            # 题号顺序递增，用"预期题号"定位切点，比猜数字边界可靠。
            cut = split_at_question(s, expected_q)
            if cut:
                head, tail = cut
                stats["拆开粘连题号"] += 1
                out.extend(emit(head))
                out.extend(emit(tail))
                tm = QNUM.match(tail.strip())
                if tm:
                    expected_q = int(tm.group(1)) + 1
                continue

        out.extend(emit(s))

    text = "\n".join(out)
    before = text.count("\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    stats["压缩空行"] = before - text.count("\n")

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
    os.makedirs(out_dir, exist_ok=True)
    chapters, cur_title, cur_body = [], None, []
    for ln in lines:
        if CHAP_KEEP.match(ln.strip()):
            if cur_title is not None:
                chapters.append((cur_title, cur_body))
            cur_title, cur_body = re.sub(r"\s+", " ", ln.strip()[2:].strip()), []
        elif cur_title is not None:
            cur_body.append(ln)
    if cur_title is not None:
        chapters.append((cur_title, cur_body))

    files = []
    for title, body in chapters:
        content = "\n".join(body).strip() + "\n"
        fn = title.translate(ILLEGAL_FN) + ".md"
        open(os.path.join(out_dir, fn), "w", encoding="utf-8").write(
            f"# {title}\n\n> 来源：27王道《{name}》高清带书签.pdf（已清理水印、广告与 OCR 噪声）\n\n{content}")
        files.append((fn, title, content))
    print(f"切分为 {len(files)} 章: " + ", ".join(f for f, _, _ in files))

    dst_img = os.path.join(out_dir, "images")
    if os.path.isdir(dst_img):
        shutil.rmtree(dst_img)
    os.makedirs(dst_img, exist_ok=True)
    all_text = "\n".join(c for _, _, c in files)
    refs = {os.path.basename(p) for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", all_text)}
    copied = missing = 0
    for n in sorted(refs):
        p = os.path.join(src_img, n)
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(dst_img, n))
            copied += 1
        else:
            missing += 1
    stats["图片复制"] = copied

    resid_noise = sum(1 for l in all_text.split("\n")
                      if NOISE_END.search(l.rstrip()) or NOISE_MULTI.search(l.rstrip()))
    # 统计层级时须含写入的标题行本身
    lv = Counter({1: len(files)})
    for m in re.finditer(r"^(#{2,6})\s", all_text, re.M):
        lv[len(m.group(1))] += 1
    print(f"  清理: 前置页{stats['删除前置页行数']} 页标记{stats['删除页标记']} "
          f"水印{stats['删除水印广告行']} 噪声{stats['删除行尾噪声'] + stats['删除成串噪声'] + stats['删除行中噪声']} "
          f"拆选项{stats['拆分选项行']} 脚注{stats['脚注转引用']} 公式{stats['公式规范化']}")
    print(f"  残余: 噪声{resid_noise} 水印{sum(all_text.count(w) for w in WATERMARK)} "
          f"页标记{len(re.findall(r'<!-- page', all_text))} 脚注{all_text.count('docvortex-page-footnote')}")
    print(f"  结构: H1={lv[1]} H2={lv[2]} H3={lv[3]} H4={lv[4]}")
    print(f"  图片: 引用{len(refs)} 复制{copied} 缺失{missing}")
    print(f"  输出: {out_dir}\n")

    return {"slug": slug, "name": name, "files": [f for f, _, _ in files],
            "stats": dict(stats), "levels": {str(k): v for k, v in sorted(lv.items())},
            "refs": len(refs), "copied": copied, "missing": missing,
            "resid_noise": resid_noise,
            "out_dir": out_dir, "chapters": [(t, len(c)) for _, t, c in files]}


if __name__ == "__main__":
    slugs = [sys.argv[1]] if len(sys.argv) > 1 else ["os", "ds", "cn"]
    reports = [build(s) for s in slugs]
    json.dump(reports, open(os.path.join(WS, "_ocr", "clean_rest_report.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    print("已写入 _ocr/clean_rest_report.json")
