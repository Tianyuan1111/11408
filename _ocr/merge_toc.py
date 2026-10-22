# -*- coding: utf-8 -*-
"""
把 MinerU 的 markdown.md 与 PDF 书签合并，生成层级正确的最终 Markdown。（v2）

关键修正（相对 v1）：
  1. 章标题合并：MinerU 会把"第1章 / 计算机系统概述"拆成两个标题，
     而书签是"第1章 计算机系统概述"。现在允许前缀包含匹配，并直接用
     书签文本作为标题；紧随其后、内容被章标题包含的冗余标题行会被删除。
  2. 答案项识别：形如 "19. C" / "15. 【解答】" 的伪标题不再加粗，回落为正文。
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
SRC_IMAGES = os.path.join(SRC, "images")
TOC = os.path.join(WS, "_ocr", "toc.json")
OUT_DIR = os.path.join(WORKDIR, "操作系统_Markdown")
OUT_MD = os.path.join(OUT_DIR, "王道操作系统.md")

PAGE_RE = re.compile(r"<!--\s*page\s+(\d+)\s+of\s+(\d+)\s*-->")
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BARE_CHAP = re.compile(r"^第\d+章$")
CHAPTER = re.compile(r"^第\d+章")
# 答案项 / 解答项：不该当标题
ANSWER_LIKE = re.compile(r"^\d{1,2}\s*[.、]\s*(【解答】|[A-D])\s*$")

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
    s = "".join(out)
    return "".join(c for c in s if c not in _PUNCT).lower()


def load_bookmarks():
    with open(TOC, encoding="utf-8") as f:
        raw = json.load(f)
    bms = []
    for d in raw:
        title = " ".join(d["title"].split())
        if not title:
            continue
        bms.append({"level": d["level"], "title": title, "page": d["page"],
                    "n": norm(title), "bare_chap": bool(BARE_CHAP.match(title))})
    return bms


def main():
    lines = open(SRC_MD, encoding="utf-8").read().split("\n")

    cur = 0
    headings = []
    for i, ln in enumerate(lines):
        m = PAGE_RE.search(ln)
        if m:
            cur = int(m.group(1))
        h = HEAD_RE.match(ln)
        if h:
            headings.append({"i": i, "level": len(h.group(1)), "text": h.group(2).strip(),
                             "page": cur, "n": norm(h.group(2))})

    all_bms = load_bookmarks()
    # 裸"第N章"不单独出标题（与"第N章 章名"重复），但保留用于匹配
    bms = [b for b in all_bms if not b["bare_chap"]]
    print(f"行数={len(lines)}  MinerU 标题={len(headings)}  书签={len(all_bms)}(去裸章名后 {len(bms)})")

    def matches(hn, bn):
        if not hn or not bn:
            return False
        if hn == bn:
            return True
        if len(bn) >= 4 and len(hn) >= 4 and (hn.startswith(bn) or bn.startswith(hn)):
            return True
        # 章标题：MinerU 可能只识别出"第1章"，书签是"第1章 计算机系统概述"
        if len(hn) >= 3 and bn.startswith(hn) and len(bn) > len(hn):
            return True
        return False

    # 顺序匹配（可正确区分重名标题，如两处"单项选择题"）
    matched = {}     # headings 下标 -> bookmark
    used = set()
    cursor = 0
    for bi, bm in enumerate(bms):
        for hi in range(cursor, len(headings)):
            if hi in matched:
                continue
            if matches(headings[hi]["n"], bm["n"]):
                matched[hi] = bi
                used.add(bi)
                cursor = hi + 1
                break

    # 未匹配书签 -> 页边界补插
    insert_at_page = defaultdict(list)
    for bi, bm in enumerate(bms):
        if bi not in used:
            insert_at_page[bm["page"]].append(bm)

    # 章标题后的冗余标题：内容被该章标题包含，则删除
    drop_lines = set()
    chapter_bm_by_hi = {hi: bms[bi] for hi, bi in matched.items() if CHAPTER.match(bms[bi]["title"])}
    for hi, bm in chapter_bm_by_hi.items():
        for hj in range(hi + 1, min(hi + 4, len(headings))):
            if hj in matched:
                break
            hn = headings[hj]["n"]
            if len(hn) >= 3 and hn in bm["n"]:
                drop_lines.add(headings[hj]["i"])

    head_by_line = {h["i"]: hi for hi, h in enumerate(headings)}
    out, inserted, stats = [], set(), defaultdict(int)
    for i, ln in enumerate(lines):
        m = PAGE_RE.search(ln)
        if m:
            out.append(ln)
            for bm in insert_at_page.get(int(m.group(1)), []):
                key = (bm["page"], bm["n"])
                if key in inserted:
                    continue
                inserted.add(key)
                out += ["", "#" * bm["level"] + " " + bm["title"], ""]
                stats["inserted"] += 1
            continue

        if i in drop_lines:
            stats["dropped_redundant"] += 1
            continue

        if i in head_by_line:
            hi = head_by_line[i]
            if hi in matched:
                bm = bms[matched[hi]]
                # 用书签文本作为标题，保证与全书目录一致
                out.append("#" * bm["level"] + " " + bm["title"])
                stats["matched"] += 1
            elif ANSWER_LIKE.match(headings[hi]["text"]):
                out.append(headings[hi]["text"])       # 答案项回落为正文
                stats["answer_demoted"] += 1
            else:
                out.append(f"**{headings[hi]['text']}**")
                stats["bold"] += 1
            continue

        out.append(ln)

    text = re.sub(r"\n{4,}", "\n\n\n", "\n".join(out)).strip() + "\n"

    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.isdir(SRC_IMAGES):
        dst_img = os.path.join(OUT_DIR, "images")
        if os.path.isdir(dst_img):
            shutil.rmtree(dst_img)
        shutil.copytree(SRC_IMAGES, dst_img)
    open(OUT_MD, "w", encoding="utf-8").write(text)

    print("命中标题      :", stats["matched"])
    print("页边界补插    :", stats["inserted"])
    print("删除冗余标题  :", stats["dropped_redundant"])
    print("答案项回落正文:", stats["answer_demoted"])
    print("保留加粗小标题:", stats["bold"])
    print("输出          :", OUT_MD)


if __name__ == "__main__":
    main()
