# -*- coding: utf-8 -*-
"""
通用转换流水线：MinerU 产物(zip) + PDF 书签 + 原始 PDF  ->  层级正确的 Markdown。

用法:  python build_book.py <slug>      # slug 见 BOOKS: os / ds / co / cn

流程：
  1. 解压 MinerU 的 zip 产物（markdown.md / structured_content.json / images/）；
  2. 用 structured_content 中"每页第一个正文块"的文字，在 markdown 中顺序对齐出每页起始行 -> 插入页标记；
  3. 用书签文本按文档顺序匹配 MinerU 识别出的标题 -> 位置取 MinerU、层级取书签；
  4. 书签有而 MinerU 漏识别的（多为章首页被误判为页眉）-> 按页码在页边界补插；
  5. 答案项回落为正文；识别出但书签没有的标题降级为加粗；
  6. 公式识别退化的块（重复乱码）-> 从原 PDF 裁出原图嵌入，不臆造内容；
  7. 输出自检报告。
"""
import os, re, sys, json, shutil, zipfile
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）

BOOKS = {
    "os": {"name": "操作系统",     "pdf": os.path.join(BOOKDIR, "27王道《操作系统》高清带书签.pdf"),
           "toc": "_ocr/toc.json",    "zip_dir": "_ocr/os_full", "out": os.path.join(WORKDIR, "操作系统_Markdown")},
    "ds": {"name": "数据结构",     "pdf": os.path.join(BOOKDIR, "27王道《数据结构》高清带书签.pdf"),
           "toc": "_ocr/toc_ds.json", "zip_dir": "_ocr/ds_full", "out": os.path.join(WORKDIR, "数据结构_Markdown")},
    "co": {"name": "计算机组成原理", "pdf": os.path.join(BOOKDIR, "27王道《计算机组成原理》高清带书签.pdf"),
           "toc": "_ocr/toc_co.json", "zip_dir": "_ocr/co_full", "out": os.path.join(WORKDIR, "计算机组成原理_Markdown")},
    "cn": {"name": "计算机网络",   "pdf": os.path.join(BOOKDIR, "27王道《计算机网络》高清带书签.pdf"),
           "toc": "_ocr/toc_cn.json", "zip_dir": "_ocr/cn_full", "out": os.path.join(WORKDIR, "计算机网络_Markdown")},
}

HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BARE_CHAP = re.compile(r"^第\d+章$")
CHAPTER = re.compile(r"^第\d+章")
ANSWER_LIKE = re.compile(r"^\d{1,2}\s*[.、)]\s*(【解答】|【答案】|[A-D])\s*$")
SKIP_TYPES = {"header", "page_number", "page_footnote", "ref_text", "index"}
# 广告浮层文字不能用作对齐签名：它同时出现在多页，会把指针一把甩到正文中段。
AD_LIKE = re.compile(r"taobao|王道书店|购买王道|考研小舟|包邮|官方开源|bilibili|"
                     r"扫码|微信|兑换码|小程序|公众号")
RUNAWAY = re.compile(r"(.)\1{11,}")          # 报告用：同一字符重复 12 次以上
# 修复用阈值更严：合法内容里不可能出现 24 个连续相同字符（二进制位串通常带空格分隔），
# 而公式模型退化时会成百上千次重复同一字符并延续到块尾。
RUNAWAY_HARD = re.compile(r"(.)\1{23,}")
DPI = 400
MARGIN_PT = 4

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


def extract_zip(slug, cfg) -> str:
    """找到并解压 MinerU 的 zip 产物，返回解压目录。"""
    zd = os.path.join(WS, cfg["zip_dir"])
    zips = [f for f in os.listdir(zd) if f.lower().endswith(".zip")]
    if not zips:
        raise SystemExit(f"[{slug}] 未找到 zip 产物：{zd}")
    src = os.path.join(WS, "_ocr", f"{slug}_full_x")
    if os.path.isdir(src):
        shutil.rmtree(src)
    os.makedirs(src, exist_ok=True)
    with zipfile.ZipFile(os.path.join(zd, zips[0])) as z:
        z.extractall(src)
    print(f"[{slug}] 解压 {zips[0]} -> {src}")
    return src


def repair_equations(lines, pages, pdf_path, images_dir):
    """把公式模型退化的块替换为原图裁切。返回替换处数。"""
    import fitz
    suspects = []
    for p in pages:
        for j, b in enumerate(p["blocks"]):
            if b.get("type") != "equation":
                continue
            txt = block_text(b)
            if RUNAWAY_HARD.search(txt):
                suspects.append((p["page_idx"], j, txt))
    if not suspects:
        return 0, []

    doc = fitz.open(pdf_path)
    line_norms = [norm(l) for l in lines]
    fixed, report = 0, []
    for page_idx, bj, txt in suspects:
        sig = norm(txt)[:24]
        # 定位 markdown 中对应的公式行
        li = None
        for i, ln in enumerate(line_norms):
            if sig and sig in ln:
                li = i
                break
        if li is None:
            report.append(f"page {page_idx+1} block {bj}: 未在 markdown 中定位到，跳过")
            continue
        start = li
        while start > 0 and lines[start].strip() != "$$":
            start -= 1
        end = li
        while end < len(lines) and lines[end].strip() != "$$":
            end += 1
        if lines[start].strip() != "$$" or end >= len(lines):
            report.append(f"page {page_idx+1} block {bj}: 公式块边界异常，跳过")
            continue

        # 裁原图
        blk = pages[page_idx]["blocks"][bj]
        x0, y0, x1, y1 = blk["bbox"]
        pg = doc[page_idx]
        W, H = pg.rect.width, pg.rect.height
        rect = fitz.Rect(max(0, x0 * W - MARGIN_PT), max(0, y0 * H - MARGIN_PT),
                         min(W, x1 * W + MARGIN_PT), min(H, y1 * H + MARGIN_PT))
        name = f"page_{page_idx}_equation_{bj}_orig.png"
        pg.get_pixmap(dpi=DPI, clip=rect).save(os.path.join(images_dir, name))
        lines[start:end + 1] = [
            f"![](images/{name})",
            "",
            f"> 说明：原 PDF 第 {page_idx+1} 页该公式为公式排版，OCR 公式模型识别失败"
            f"（输出重复乱码），此处直接嵌入原图，未作内容推断。",
        ]
        fixed += 1
        report.append(f"page {page_idx+1} block {bj}: 已替换为原图 {name} ({rect.width:.0f}x{rect.height:.0f}pt)")
    doc.close()
    return fixed, report


def build(slug, out_override=None):
    cfg = BOOKS[slug]
    name = cfg["name"]
    src = extract_zip(slug, cfg)
    md_path = os.path.join(src, "markdown.md")
    sc_path = os.path.join(src, "structured_content.json")
    src_images = os.path.join(src, "images")
    pdf_path = os.path.join(WS, cfg["pdf"])
    out_dir = out_override or os.path.join(WS, cfg["out"])
    out_md = os.path.join(out_dir, f"王道{name}.md")

    lines = open(md_path, encoding="utf-8").read().split("\n")
    sc = json.load(open(sc_path, encoding="utf-8"))
    pages = sc["pages"]

    # ---------- 1. 页码对齐 ----------
    # 逐块尝试：用该页第一个"能在当前位置之后找到"的正文块定位。
    # 不能只挑第一个够长的块——TOC 页上的淘宝书店广告浮层文字同时出现在多页，
    # 会让指针一把甩到正文中段（数据结构就因此错位，第1章正文被当成前置页）。
    line_norms = [norm(l) for l in lines]

    def locate(p, start):
        for b in p["blocks"]:
            if b.get("type") in SKIP_TYPES:
                continue
            t = norm(block_text(b))
            if len(t) < 6 or AD_LIKE.search(t):
                continue
            sig = t[:30]
            for i in range(start, len(lines)):
                ln = line_norms[i]
                if not ln:
                    continue
                if sig in ln or (len(ln) >= 8 and ln in sig):
                    return i
        return None

    page_start, marker_line = {}, defaultdict(list)
    pos, aligned = 0, 0
    for p in pages:
        idx = p["page_idx"]
        found = locate(p, pos)
        if found is None:
            found = pos
        else:
            aligned += 1
        page_start[idx] = found
        marker_line[found].append(idx)
        pos = max(pos, found)

    # ---------- 2. 书签匹配 ----------
    headings = []
    for i, ln in enumerate(lines):
        h = HEAD_RE.match(ln)
        if h:
            headings.append({"i": i, "text": h.group(2).strip(), "n": norm(h.group(2))})

    raw = json.load(open(os.path.join(WS, cfg["toc"]), encoding="utf-8"))
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

    insert_at_line = defaultdict(list)
    for bi, bm in enumerate(bms):
        if bi not in used:
            insert_at_line[page_start.get(bm["page"] - 1, 0)].append(bm)

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
    emitted = set()
    for i, ln in enumerate(lines):
        for idx in sorted(marker_line.get(i, [])):
            if idx in emitted:
                continue
            emitted.add(idx)
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

    # ---------- 4. 写文件 ----------
    os.makedirs(out_dir, exist_ok=True)
    dst_images = os.path.join(out_dir, "images")
    if os.path.isdir(dst_images):
        shutil.rmtree(dst_images)
    shutil.copytree(src_images, dst_images)
    open(out_md, "w", encoding="utf-8").write(text)

    # ---------- 5. 修复退化公式 ----------
    final = open(out_md, encoding="utf-8").read().split("\n")
    fixed, fix_report = repair_equations(final, pages, pdf_path, dst_images)
    if fixed:
        open(out_md, "w", encoding="utf-8").write("\n".join(final))

    # ---------- 6. 自检 ----------
    text = open(out_md, encoding="utf-8").read()
    flines = text.split("\n")
    print(f"\n########## {name} 自检报告 ##########")
    print(f"页数={len(pages)}  对齐成功={aligned}/{len(pages)}  页标记={stats['markers']}")
    lv_out = Counter(len(m.group(1)) for l in flines if (m := HEAD_RE.match(l)))
    lv_bm = Counter(b["level"] for b in bms)
    print("标题层级  输出 vs 书签:")
    for k in sorted(set(lv_out) | set(lv_bm)):
        flag = "OK " if lv_out.get(k, 0) == lv_bm.get(k, 0) else "差异"
        print(f"   H{k}: 输出={lv_out.get(k,0):<5} 书签={lv_bm.get(k,0):<5} {flag}")
    print(f"命中={stats['matched']} 页边界补插={stats['inserted']} 冗余删除={stats['dropped']} "
          f"答案回落={stats['answer']} 保留加粗={stats['bold']}")
    unm = [(b['level'], b['page'], b['title']) for i, b in enumerate(bms) if i not in used]
    print(f"未匹配书签: {len(unm)}")
    for l, pg, t in unm[:20]:
        print(f"   L{l} p{pg}  {t}")

    imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    disk = set(os.listdir(dst_images))
    miss = [os.path.basename(p) for p in imgs if os.path.basename(p) not in disk]
    print(f"图片: 引用={len(imgs)} 磁盘={len(disk)} 缺失={len(miss)} {miss[:5]}")
    n_inline = len(re.findall(r"\$[^$\n]{2,80}\$", text))
    print(f"表格={text.count('<table')} 行内公式={n_inline} "
          f"公式块={text.count('$$')//2} 代码块={text.count('```')//2}")

    # 残余退化：只看 $$ 块内部（正文里的省略号点线、二进制串属正常）
    resid, in_eq = [], False
    for l in flines:
        if l.strip() == "$$":
            in_eq = not in_eq
            continue
        if in_eq and RUNAWAY.search(l):
            resid.append(l[:60])
    print(f"$$ 块内残余退化: {len(resid)}")
    for r in resid[:5]:
        print("   " + r)
    if fix_report:
        print(f"公式修复 {fixed} 处:")
        for r in fix_report:
            print("   " + r)
    print(f"输出: {out_md}")
    return out_md


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in BOOKS:
        print("用法: python build_book.py <os|ds|co|cn> [输出目录]")
        raise SystemExit(1)
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
