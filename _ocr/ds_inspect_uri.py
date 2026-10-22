# -*- coding: utf-8 -*-
"""检查 pickle 里所有内联 data URI，找出不合法的那些，并报告所在页/块/bbox。"""
import os, re, sys, pickle, json

sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("MINERU_HOME", r"E:\dsh_cache\mineru")

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
PKL = os.path.join(WS, "_ocr", "ds_result.pkl")

STRICT = re.compile(r"data:image/([^;]+);base64,([A-Za-z0-9+/]*={0,2})")
INLINE = re.compile(r"data:image/([^;\"']+);base64,([^\"']+)", re.DOTALL)

print("载入 pickle ...", flush=True)
with open(PKL, "rb") as f:
    result = pickle.load(f)
print("载入完成:", type(result).__name__, flush=True)

mj = result.middle_json
pages = getattr(mj, "pages", None)
print("页数:", len(pages) if pages else "n/a", flush=True)


def walk_strings(obj, path=()):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, path + (str(k),))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from walk_strings(v, path + (str(i),))


bad = []
for p in pages:
    pid = getattr(p, "page_idx", None)
    for bi, blk in enumerate(getattr(p, "blocks", []) or []):
        d = blk.model_dump() if hasattr(blk, "model_dump") else (
            blk.dict() if hasattr(blk, "dict") else blk)
        if not isinstance(d, dict):
            d = {"content": str(d)}
        for path, s in walk_strings(d):
            if "data:image/" not in s:
                continue
            for m in INLINE.finditer(s):
                uri = m.group(0)
                ok = STRICT.fullmatch(uri) is not None
                if not ok:
                    payload = uri.split(",", 1)[1] if "," in uri else ""
                    bad.append({
                        "page_idx": pid, "block_idx": bi,
                        "block_type": d.get("type"), "bbox": d.get("bbox"),
                        "json_path": ".".join(path),
                        "uri_len": len(uri), "payload_len": len(payload),
                        "payload_mod4": len(payload) % 4,
                        "has_ws": bool(re.search(r"\s", payload)),
                        "bad_chars": sorted({c for c in payload if not re.match(r"[A-Za-z0-9+/=]", c)})[:10],
                        "head": uri[:80], "tail": uri[-60:],
                        "host_str_len": len(s),
                    })

print(f"\n发现不合法 data URI: {len(bad)} 个\n")
for b in bad:
    print(f"--- page_idx={b['page_idx']} block={b['block_idx']} type={b['block_type']} bbox={b['bbox']}")
    print(f"    URI长度={b['uri_len']} 载荷长度={b['payload_len']} 载荷%4={b['payload_mod4']}")
    print(f"    含空白={b['has_ws']} 非法字符={b['bad_chars']}")
    print(f"    所在字符串长度={b['host_str_len']}  json路径={b['json_path']}")
    print(f"    头: {b['head']}")
    print(f"    尾: {b['tail']}")
    print()

json.dump(bad, open(os.path.join(WS, "_ocr", "ds_bad_uris.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("明细已写入 _ocr/ds_bad_uris.json")
