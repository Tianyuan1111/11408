# -*- coding: utf-8 -*-
"""对三本检查页码对齐质量：是否有"广告签名导致指针跳飞"。"""
import os, re, sys, json, zipfile
sys.stdout.reconfigure(encoding="utf-8")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
BOOKS = [("操作系统", "_ocr/os_full"), ("数据结构", "_ocr/ds_full"), ("计算机网络", "_ocr/cn_full")]
SKIP_TYPES = {"header", "page_number", "page_footnote", "ref_text", "index"}
_PUNCT = "　 \t\u00a0.,，。、;；:：!！?？\"'“”‘’()（）[]【】{}《》〈〉<>·-—_…~`*/\\|+="


def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if o == 0x3000:
            ch = " "
        elif 0xFF01 <= o <= 0xFF5E:
            ch = chr(o - 0xFEE0)
        out.append(ch)
    return "".join(c for c in "".join(out) if c not in _PUNCT).lower()


def block_text(b):
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("content", "")) for x in c if isinstance(x, dict))
    return c if isinstance(c, str) else ""


for name, zipdir in BOOKS:
    zd = os.path.join(WS, zipdir)
    zf = [f for f in os.listdir(zd) if f.lower().endswith(".zip")][0]
    with zipfile.ZipFile(os.path.join(zd, zf)) as z:
        lines = z.read("markdown.md").decode("utf-8").split("\n")
        sc = json.loads(z.read("structured_content.json").decode("utf-8"))
    ln_norm = [norm(l) for l in lines]

    pos, fails, jumps, ad_sigs = 0, 0, [], []
    for p in sc["pages"]:
        sig = ""
        for b in p["blocks"]:
            if b.get("type") in SKIP_TYPES:
                continue
            t = norm(block_text(b))
            if len(t) >= 6:
                sig = t[:30]
                break
        found = None
        if sig:
            if any(k in sig for k in ("taobao", "王道书店", "购买王道", "考研小舟", "包邮", "bilibili")):
                ad_sigs.append((p["page_idx"] + 1, sig[:40]))
            for i in range(pos, len(lines)):
                if not ln_norm[i]:
                    continue
                if sig in ln_norm[i] or (len(ln_norm[i]) >= 8 and ln_norm[i] in sig):
                    found = i
                    break
        if found is None:
            fails += 1
            found = pos
        else:
            if found - pos > 400:
                jumps.append((p["page_idx"] + 1, pos, found))
            pos = max(pos, found)

    print(f"### {name}: 总页 {len(sc['pages'])}  未匹配 {fails}  大跨度跳转 {len(jumps)}  广告签名 {len(ad_sigs)}")
    for pg, s in ad_sigs[:6]:
        print(f"    广告签名 PDF第{pg}页: {s}")
    for pg, a, b in jumps[:6]:
        print(f"    跳转 PDF第{pg}页: L{a} -> L{b}")
    print()
