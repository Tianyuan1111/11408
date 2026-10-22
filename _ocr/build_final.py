# -*- coding: utf-8 -*-
"""
最终合并：MinerU markdown + PDF 书签 + structured_content 页码对齐  ->  层级正确的 Markdown。

解决的三件事：
  1. 页标记缺失：mineru-kit 的 markdown 没有 `<!-- page N -->`。
     用 structured_content.json 里"每页第一个正文块"的文字，在 markdown 中顺序对齐出每页起始行，
     从而插入页标记。
  2. 章标题丢失：章首页的「第N章 / 章名 / 【考纲内容】」被版面模型判为页眉而被渲染器丢弃。
     这些书签匹配不到任何标题，改为按对齐出的页码在页边界补插（层级用书签的，是准的）。
  3. 标题层级：MinerU 几乎全输出 ##，用书签层级校正；答案项（19. C）回落为正文。
"""
import os, re, sys, json, shutil
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
SRC = os.path.join(WS, "_ocr", "os_full_x")
SRC_MD = os.path.join(SRC, "markdown.md")
SRC_SC = os.path.join(SRC, "structured_content.json")
SRC_IMAGES = os.path.join(SRC, "images")
TOC = os.path.join(WS, "_ocr", "toc.json")
OUT_DIR = os.path.join(WORKDIR, "操作系统_Markdown")
OUT_MD = os.path.join(OUT_DIR, "王道操作系统.md")

HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BARE_CHAP = re.compile(r"^第\d+章$")
CHAPTER = re.compile(r"^第\d+章")
ANSWER_LIKE = re.compile(r"^\d{1,2}\s*[.、]\s*(【解答】|[A-D])\s*$")
SKIP_TYPES = {"header", "page_number", "page_footnote", "ref_text", "index"}

_PUNCT = "　 \t\u00a0.,，。、;；:：!！?？\"'“”‘’()（）[]【】{}《》〈〉<>·-—_…~`*/\\|+="


def norm(s: str) -> str:
    out = []
    for ch in s:
        o = ord(ch)
        if o == 0x3000:
            ch = " "
        elif 0xFF01 <= o <= 0xFF5E:
            ch = chr(o - 0xFEE0)
        out.append(ch)
    return "".join(c for c in "".join(out) if c not in _PUNCT).lower()


def block_text(b) -> str:
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


def matches(hn: str, bn: str) -> bool:
    if not hn or not bn:
        return False
    if hn == bn:
        return True
    if len(bn) >= 4 and len(hn) >= 4 and (hn.startswith(bn) or bn.startswith(hn)):
        return True
    if len(hn) >= 3 and bn.startswith(hn) and len(bn) > len(hn):
        return True
    return False


def main():
    lines = open(SRC_MD, encoding="utf-8").read().split("\n")
    sc = json.load(open(SRC_SC, encoding="utf-8"))
    pages = sc["pages"]

    # ---------- 1. 页码对齐 ----------
    # 每页取第一个"正文类"块作为定位签名
    sigs = {}
    for p in pages:
        idx = p["page_idx"]
        s = ""
        for b in p["blocks"]:
            if b.get("type") in SKIP_TYPES:
                continue
            t = norm(block_text(b))
            if len(t) >= 6:
                s = t[:30]
                break
        sigs[idx] = s

    line_norms = [norm(ln) for ln in lines]
    page_start = {}          # page_idx -> line index
    marker_line = {}         # line index -> [page_idx,...]
    pos = 0
    aligned = 0
    for p in pages:
        idx = p["page_idx"]
        sig = sigs[idx]
        found = None
        if sig:
            for i in range(pos, len(lines)):
                ln = line_norms[i]
                if not ln:
                    continue
                if sig in ln or (len(ln) >= 8 and ln in sig):
                    found = i
                    break
        if found is None:
            found = pos if idx > 0 else 0        # 无正文页（纯装饰页）：落在当前位置
        else:
            aligned += 1
        page_start[idx] = found
        marker_line.setdefault(found, []).append(idx)
        pos = max(pos, found)

    print(f"页对齐成功: {aligned}/{len(pages)}  页标记插入点: {len(marker_line)}")

    # ---------- 2. 书签匹配 ----------
    headings = []
    for i, ln in enumerate(lines):
        h = HEAD_RE.match(ln)
        if h:
            headings.append({"i": i, "text": h.group(2).strip(), "n": norm(h.group(2))})

    raw = json.load(open(TOC, encoding="utf-8"))
    all_bms = [{"level": d["level"], "title": " ".join(d["title"].split()), "page": d["page"]}
               for d in raw if " ".join(d["title"].split())]
    bms = [b for b in all_bms if not BARE_CHAP.match(b["title"])]
    for b in bms:
        b["n"] = norm(b["title"])

    matched, used, cursor = {}, set(), 0
    for bi, bm in enumerate(bms):
        for hi in range(cursor, len(headings)):
            if hi in matched:
                continue
            if matches(headings[hi]["n"], bm["n"]):
                matched[hi] = bi
                used.add(bi)
                cursor = hi + 1
                break

    # 未匹配书签 -> 落到其所在页(page 是 1-based)的起始行
    insert_at_line = defaultdict(list)
    for bi, bm in enumerate(bms):
        if bi in used:
            continue
        li = page_start.get(bm["page"] - 1, 0)
        insert_at_line[li].append(bm)

    # 章标题后的冗余标题（如 MinerU 单独识别的"计算机系统概述"）
    drop_lines = set()
    for hi, bi in matched.items():
        bm = bms[bi]
        if not CHAPTER.match(bm["title"]):
            continue
        for hj in range(hi + 1, min(hi + 4, len(headings))):
            if hj in matched:
                break
            if len(headings[hj]["n"]) >= 3 and headings[hj]["n"] in bm["n"]:
                drop_lines.add(headings[hj]["i"])

    head_by_line = {h["i"]: hi for hi, h in enumerate(headings)}

    # ---------- 3. 生成 ----------
    out, stats = [], defaultdict(int)
    emitted_pages = set()
    for i, ln in enumerate(lines):
        # 该行之前插入：页标记 + 未匹配书签
        for idx in sorted(marker_line.get(i, [])):
            if idx in emitted_pages:
                continue
            emitted_pages.add(idx)
            out.append(f"<!-- page {idx + 1} of {len(pages)} -->")
            out.append("")
            stats["markers"] += 1
        for bm in insert_at_line.get(i, []):
            out += ["#" * bm["level"] + " " + bm["title"], ""]
            stats["inserted"] += 1

        if i in drop_lines:
            stats["dropped"] += 1
            continue

        if i in head_by_line:
            hi = head_by_line[i]
            if hi in matched:
                bm = bms[matched[hi]]
                out.append("#" * bm["level"] + " " + bm["title"])
                stats["matched"] += 1
            elif ANSWER_LIKE.match(headings[hi]["text"]):
                out.append(headings[hi]["text"])
                stats["answer"] += 1
            else:
                out.append(f"**{headings[hi]['text']}**")
                stats["bold"] += 1
            continue

        out.append(ln)

    text = re.sub(r"\n{4,}", "\n\n\n", "\n".join(out)).strip() + "\n"

    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.isdir(SRC_IMAGES):
        dst = os.path.join(OUT_DIR, "images")
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(SRC_IMAGES, dst)
    open(OUT_MD, "w", encoding="utf-8").write(text)

    for k in ("markers", "matched", "inserted", "dropped", "answer", "bold"):
        print(f"{k:<10}: {stats[k]}")
    print("输出      :", OUT_MD)


if __name__ == "__main__":
    main()
