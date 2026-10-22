# -*- coding: utf-8 -*-
"""
修复《数据结构》唯一损坏的图片并导出 zip（复用已缓存的分析结果，不重跑 17 分钟）。

问题：第 195 页 block 16（表格图 5.30）的 HTML content 里内联的 data URI 被截断损坏
      （载荷 39453 字符，不是 4 的倍数，还混入了 < > 标记）。
      但同一块的 image_base64 字段是完好的（16075 字符，以 JPEG 结束符结尾）。
做法：把损坏的内联 URI 替换为完好的 image_base64，并补齐被截断处缺失的闭合标签。
      属无损修复——用的是原文自带的正确图片数据，没有任何推测。
"""
import os, re, sys, pickle, time, zipfile

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
os.environ.setdefault("MINERU_HOME", r"E:\dsh_cache\mineru")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
PKL = os.path.join(WS, "_ocr", "ds_result.pkl")
OUT = os.path.join(WS, "_ocr", "ds_full")
ZIP_NAME = "27王道《数据结构》高清带书签.zip"

PAGE_IDX, BLOCK_IDX = 194, 16
STRICT = re.compile(r"data:image/([^;]+);base64,([A-Za-z0-9+/]*={0,2})")


def close_tags(html: str) -> str:
    """按已开启但未闭合的数量，补齐 HTML 闭合标签。"""
    adds = []
    for tag in ("td", "th", "tr", "tbody", "thead", "table"):
        opens = len(re.findall(rf"<{tag}\b", html)) - len(re.findall(rf"</{tag}>", html))
        adds.extend([f"</{tag}>"] * max(0, opens))
    return "".join(adds)


def main():
    print("载入缓存的分析结果 ...", flush=True)
    with open(PKL, "rb") as f:
        result = pickle.load(f)

    page = result.middle_json.pages[PAGE_IDX]
    blk = page.blocks[BLOCK_IDX]
    d = blk.model_dump() if hasattr(blk, "model_dump") else blk.dict()
    c0 = d["content"][0]
    html = c0["content"]
    good = c0["image_base64"]

    print(f"页 {PAGE_IDX+1} block {BLOCK_IDX} type={d.get('type')} bbox={d.get('bbox')}")
    print(f"  损坏 HTML 长度={len(html)}   完好 image_base64 长度={len(good)}")
    assert STRICT.fullmatch(good), "image_base64 本身也不合法，无法用此方案"

    m = re.search(r'<img\s+src="?', html)
    assert m, "未找到 <img src="
    prefix = html[: m.start()]
    fixed = prefix + f'<img src="{good}">' + close_tags(prefix)
    print(f"  修复后 HTML 长度={len(fixed)}")

    # 写回（content 是 pydantic 模型，这里直接改底层对象）
    inner = blk.content[0]
    if hasattr(inner, "content"):
        inner.content = fixed
    else:
        inner["content"] = fixed
    print("  已写回修复后的 HTML", flush=True)

    # 安全网：万一还有别的非法 URI，不再让整个导出失败
    import docvortex.foundation._image_payload as _payload
    orig = _payload.parse_image_data_uri_strict
    hits = {"n": 0}

    def tolerant(uri):
        try:
            return orig(uri)
        except Exception as exc:
            hits["n"] += 1
            print(f"  !! 仍有非法 data URI: len={len(uri) if isinstance(uri,str) else '-'} {exc}", flush=True)
            raise

    for name in ("docvortex.foundation._image_payload", "docvortex.assets",
                 "docvortex.export._images", "docvortex.export.bundle"):
        try:
            mod = __import__(name, fromlist=["parse_image_data_uri_strict"])
            if hasattr(mod, "parse_image_data_uri_strict"):
                mod.parse_image_data_uri_strict = tolerant
        except Exception:
            pass

    from mineru.kit.common import save_parse_result
    from pathlib import Path
    dest = Path(OUT) / ZIP_NAME
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    print("导出 zip ...", flush=True)
    save_parse_result(result, dest, "zip")
    print(f"导出完成，用时 {time.time()-t0:.0f}s", flush=True)
    print(f"  {dest}  {dest.stat().st_size/1048576:.1f} MB", flush=True)
    print(f"  残余非法 URI 次数: {hits['n']}", flush=True)


if __name__ == "__main__":
    main()
