# -*- coding: utf-8 -*-
"""
解析《数据结构》并在导出阶段绕过 "Invalid image data URI"。

背景：materials 外置图片时用 re.fullmatch(r"data:image/([^;]+);base64,([A-Za-z0-9+/]*={0,2})")
      严格校验 data URI。只要 base64 载荷里带了换行/空白，或使用了 URL-safe 字母表，
      或 MIME 段多了参数，就会判定非法并让整个导出失败。

做法：monkeypatch 该校验函数为"先规范化、再交给原实现"，并记录每一次实际修复的值。
      分析过程在本进程内执行，所以补丁对本流程完全生效。
      另外在分析结束后尽力把结果 pickle 到磁盘，万一导出仍失败可免于重跑 17 分钟。
"""
import os, re, sys, time, pickle, ctypes, traceback, subprocess

# ---- 环境必须在导入重型库之前设好 ----
os.environ.setdefault("MINERU_HOME", r"E:\dsh_cache\mineru")
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
os.environ["DOCVORTEX_PDF_RENDER_THREADS"] = "1"
os.environ["MINERU_PROCESSING_WINDOW_SIZE"] = "32"
os.environ["DOCVORTEX_PDF_RENDER_TIMEOUT"] = "1800"

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

# ── 路径根：随 _ocr 目录位置自动推导（不再写死 Desktop 路径）──────────────
OCR     = os.path.dirname(os.path.abspath(__file__))   # 本目录 = <工作区>/_ocr
WS      = os.path.dirname(OCR)                         # 工作区根
BOOKDIR = os.path.join(WS, "408")                      # 教材 PDF + 成品章节
WORKDIR = os.path.join(OCR, "work")                    # 中间产物（*_Markdown 等）
PDF = os.path.join(BOOKDIR, "27王道《数据结构》高清带书签.pdf")
OUT = os.path.join(WS, "_ocr", "ds_full")
PKL = os.path.join(WS, "_ocr", "ds_result.pkl")
FIXLOG = os.path.join(WS, "_ocr", "ds_uri_fix.log")

fixlog = open(FIXLOG, "w", encoding="utf-8", buffering=1)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)
    fixlog.write(msg + "\n")


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def free_mb():
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(m)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 1048576


# ---------------- monkeypatch ----------------
import docvortex.foundation._image_payload as _payload

_ORIG = _payload.parse_image_data_uri_strict
_fixes = {"n": 0}


def _normalize(uri: str):
    """把常见但不合规的 data URI 规范化；返回规范化后的字符串。"""
    s = uri
    # 1) 去掉所有空白（base64 常被换行折断）
    s = re.sub(r"\s+", "", s)
    # 2) MIME 段多余参数：data:image/png;charset=utf-8;base64,xxx
    m = re.match(r"^data:image/([^;,]+)(?:;[^,;]*)*;base64,(.*)$", s, re.S)
    if m:
        subtype, payload = m.group(1), m.group(2)
        # 3) URL-safe base64 转标准 base64
        payload = payload.replace("-", "+").replace("_", "/")
        # 4) 补齐 padding
        payload = payload.rstrip("=")
        pad = (-len(payload)) % 4
        payload += "=" * pad
        s = f"data:image/{subtype};base64,{payload}"
    return s


def tolerant(uri):
    try:
        return _ORIG(uri)
    except Exception as exc:
        _fixes["n"] += 1
        head = repr(uri)[:160] if isinstance(uri, str) else repr(uri)[:160]
        log(f"!! data URI 校验失败 #{_fixes['n']}: {type(exc).__name__}: {exc}")
        log(f"   长度={len(uri) if isinstance(uri, str) else 'n/a'}  预览={head}")
        if not isinstance(uri, str):
            raise
        cand = _normalize(uri)
        if cand != uri:
            try:
                payload, ext = _ORIG(cand)
                log(f"   规范化成功 -> {ext}, {len(payload)} 字节")
                return payload, ext
            except Exception as exc2:
                log(f"   规范化后仍失败: {exc2}")
        else:
            log("   规范化未改变内容（说明不是空白/字母表/参数问题）")
        raise


# 所有按引用持有该函数的模块都要一起替换
_patched = []
for modname in ("docvortex.foundation._image_payload",
                "docvortex.assets",
                "docvortex.export._images",
                "docvortex.export.bundle",
                "docvortex.render._internal.html.sanitizer",
                "mineru.kit.gradio.artifacts",
                "mineru.doclib.server"):
    try:
        mod = __import__(modname, fromlist=["parse_image_data_uri_strict"])
        if hasattr(mod, "parse_image_data_uri_strict"):
            mod.parse_image_data_uri_strict = tolerant
            _patched.append(modname)
    except Exception as e:
        log(f"跳过 {modname}: {type(e).__name__}")
log("已打补丁的模块: " + ", ".join(_patched))


def main():
    from mineru.parser import parse
    from mineru.kit.common import save_parse_result

    log(f"起始空闲内存 {free_mb():.0f} MB；低内存配置 RENDER_THREADS=1 / WINDOW_SIZE=32")
    t0 = time.time()
    log("开始解析 数据结构 (404 页) ...")
    result = parse(PDF, tier="basic")
    log(f"分析完成，用时 {(time.time()-t0)/60:.1f} 分钟，空闲内存 {free_mb():.0f} MB")

    # 尽力缓存结果，便于导出失败时免于重跑
    try:
        with open(PKL, "wb") as f:
            pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
        log(f"结果已缓存: {PKL} ({os.path.getsize(PKL)/1048576:.1f} MB)")
    except Exception as e:
        log(f"结果缓存失败（不影响导出）: {type(e).__name__}: {e}")

    log("开始导出 zip ...")
    try:
        save_parse_result(result, __import__("pathlib").Path(OUT) /
                          "27王道《数据结构》高清带书签.zip", "zip")
        log("导出成功")
    except Exception:
        log("导出失败:")
        fixlog.write(traceback.format_exc())
        print(traceback.format_exc())
    log(f"URI 修复次数: {_fixes['n']}")
    fixlog.close()


if __name__ == "__main__":
    main()
